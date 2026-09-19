from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Callable

from PIL import Image, ImageDraw, ImageFont

from eink_books.env import load_project_env
from eink_books.fonts import find_font
from eink_books.parse import load_book

IMAGES_URL = "https://openrouter.ai/api/v1/images"
MODELS_URL = "https://openrouter.ai/api/v1/images/models"
DEFAULT_MODEL = "openai/gpt-image-1-mini"
FALLBACK_MODEL = DEFAULT_MODEL
PORTRAIT_RATIOS = ("3:4", "2:3", "4:5")
CHEAP_CANDIDATES = (
    "openai/gpt-image-1-mini",
    "openai/gpt-5-image-mini",
    "openai/gpt-image-2",
    "black-forest-labs/flux.2-klein-4b",
    "sourceful/riverflow-v2.5-fast",
    "microsoft/mai-image-2.6-flash",
    "google/gemini-3.1-flash-lite-image",
)
KNOWN_ESTIMATES: dict[str, float] = {}
_TOKEN_IMAGE_ESTIMATE = 800
_HTTP_TIMEOUT = 180

Fetcher = Callable[[str, dict[str, str] | None, dict[str, Any] | None], Any]


@dataclass(frozen=True)
class ImageModel:
    id: str
    name: str
    estimate_usd: float | None
    aspect_ratios: tuple[str, ...]
    qualities: tuple[str, ...]
    pricing_note: str
    has_endpoint: bool = True


def _http_json(
    url: str,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
) -> Any:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="GET" if body is None else "POST")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter HTTP {exc.code}: {detail}") from exc


def openrouter_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/kumanaya/e-ink-hack",
        "X-Title": "eink-books",
    }


def resolve_api_key(explicit: str | None = None) -> str:
    load_project_env()
    key = (explicit or os.environ.get("OPENROUTER_API_KEY") or "").strip()
    if not key:
        raise ValueError("set OPENROUTER_API_KEY, put it in .env, or pass --api-key")
    return key


def estimate_usd(pricing: list[dict[str, Any]], megapixels: float = 1.0) -> float | None:
    best: float | None = None
    for line in pricing:
        if line.get("billable") != "output_image":
            continue
        if str(line.get("variant", "")).lower() in {"2k", "4k"}:
            continue
        try:
            cost = float(line.get("cost_usd") or 0)
        except (TypeError, ValueError):
            continue
        unit = line.get("unit")
        if unit == "image":
            usd = cost
        elif unit == "megapixel":
            usd = cost * megapixels
        elif unit == "token":
            usd = cost * _TOKEN_IMAGE_ESTIMATE
        else:
            continue
        if best is None or usd < best:
            best = usd
    return best


def _enum_values(params: dict[str, Any], key: str) -> tuple[str, ...]:
    spec = params.get(key) or {}
    if spec.get("type") == "enum":
        return tuple(str(v) for v in spec.get("values") or [])
    return ()


def _endpoints_url(item: dict[str, Any], model_id: str) -> str:
    path = item.get("endpoints") or f"/api/v1/images/models/{model_id}/endpoints"
    if str(path).startswith("/"):
        return "https://openrouter.ai" + path
    return str(path)


def _from_listing_item(item: dict[str, Any], fetch: Fetcher) -> ImageModel:
    model_id = str(item.get("id"))
    params = item.get("supported_parameters") or {}
    estimates: list[float] = []
    notes: list[str] = []
    try:
        record = fetch(_endpoints_url(item, model_id), None, None)
    except RuntimeError:
        record = {"endpoints": []}
    endpoints = record.get("endpoints") or []
    for endpoint in endpoints:
        pricing = endpoint.get("pricing") or []
        usd = estimate_usd(pricing)
        if usd is not None:
            estimates.append(usd)
        billed = [
            f"{p.get('cost_usd')}/{p.get('unit')}"
            for p in pricing
            if p.get("billable") == "output_image"
        ]
        if billed:
            notes.append(", ".join(billed))
    known = KNOWN_ESTIMATES.get(model_id)
    if not estimates and known is not None:
        estimates.append(known)
        notes.append(f"{known}/image")
    return ImageModel(
        id=model_id,
        name=str(item.get("name") or model_id),
        estimate_usd=min(estimates) if estimates else None,
        aspect_ratios=_enum_values(params, "aspect_ratio"),
        qualities=_enum_values(params, "quality"),
        pricing_note="; ".join(notes) or "pricing unknown",
        has_endpoint=bool(endpoints),
    )


def list_image_models(
    fetch: Fetcher = _http_json,
    only_ids: tuple[str, ...] | None = None,
) -> list[ImageModel]:
    listing = fetch(MODELS_URL, None, None)
    models: list[ImageModel] = []
    wanted = set(only_ids) if only_ids is not None else None
    for item in listing.get("data") or []:
        model_id = item.get("id")
        if not model_id or str(model_id).startswith("openrouter/"):
            continue
        if wanted is not None and model_id not in wanted:
            continue
        model = _from_listing_item(item, fetch)
        if wanted is None and not model.has_endpoint:
            continue
        models.append(model)
    models.sort(key=lambda m: (m.estimate_usd is None, m.estimate_usd or 0, m.id))
    return models


def _fallback_model() -> ImageModel:
    return ImageModel(
        id=FALLBACK_MODEL,
        name=FALLBACK_MODEL,
        estimate_usd=0.0064,
        aspect_ratios=("1:1", "3:2", "2:3", "auto"),
        qualities=("auto", "low", "medium", "high"),
        pricing_note="fallback; openai/gpt-image-1-mini ~$0.006 at quality=low",
    )


def find_model(model_id: str, fetch: Fetcher = _http_json) -> ImageModel:
    try:
        found = list_image_models(fetch, only_ids=(model_id,))
        if found:
            return found[0]
    except RuntimeError:
        pass
    return ImageModel(
        id=model_id,
        name=model_id,
        estimate_usd=None,
        aspect_ratios=(),
        qualities=("auto", "low", "medium", "high"),
        pricing_note="user-selected",
        has_endpoint=True,
    )


def pick_cheapest_model(
    models: list[ImageModel] | None = None,
    fetch: Fetcher = _http_json,
) -> ImageModel:
    catalog = models if models is not None else list_image_models(fetch, only_ids=CHEAP_CANDIDATES)
    catalog = sorted(catalog, key=lambda m: (m.estimate_usd is None, m.estimate_usd or 0, m.id))
    portrait = [
        m
        for m in catalog
        if m.estimate_usd is not None and any(r in m.aspect_ratios for r in PORTRAIT_RATIOS)
    ]
    if portrait:
        return portrait[0]
    priced = [m for m in catalog if m.estimate_usd is not None]
    if priced:
        return priced[0]
    return _fallback_model()


def choose_aspect_ratio(model: ImageModel, requested: str) -> str | None:
    if not model.aspect_ratios:
        return None
    if requested in model.aspect_ratios:
        return requested
    for candidate in PORTRAIT_RATIOS:
        if candidate in model.aspect_ratios:
            return candidate
    if "auto" in model.aspect_ratios:
        return "auto"
    return model.aspect_ratios[0]


def choose_quality(model: ImageModel, requested: str | None) -> str | None:
    if not model.qualities:
        return None
    if requested and requested in model.qualities:
        return requested
    if "low" in model.qualities:
        return "low"
    return model.qualities[0]


def cover_prompt(title: str, author: str, extra: str = "", language: str = "en") -> str:
    extra = extra.strip()
    if language.lower().startswith("pt"):
        mood = "Mood should match a literary Portuguese short story."
    else:
        mood = "Mood should match a literary short story."
    parts = [
        "Print book cover illustration for an e-ink Kindle library icon.",
        f'Title: "{title}". Author: {author}.',
        "Portrait composition, high contrast, limited muted palette that still reads in grayscale,",
        "no tiny paragraphs, no UI chrome, no watermark, no extra captions besides the title if needed.",
        mood,
    ]
    if extra:
        parts.append(extra)
    return " ".join(parts)


def prompt_from_source(source: Path, extra: str = "") -> tuple[str, str, str, str]:
    book = load_book(source)
    return book.title, book.author, book.language, cover_prompt(book.title, book.author, extra, book.language)


def generate_cover_bytes(
    *,
    model: str,
    prompt: str,
    api_key: str,
    aspect_ratio: str | None = None,
    quality: str | None = None,
    fetch: Fetcher = _http_json,
) -> tuple[bytes, str, dict[str, Any]]:
    body: dict[str, Any] = {"model": model, "prompt": prompt, "n": 1}
    if aspect_ratio:
        body["aspect_ratio"] = aspect_ratio
    if quality:
        body["quality"] = quality
    payload = fetch(IMAGES_URL, openrouter_headers(api_key), body)
    images = payload.get("data") or []
    if not images or not images[0].get("b64_json"):
        raise RuntimeError(f"OpenRouter returned no image: {payload}")
    raw = base64.b64decode(images[0]["b64_json"])
    media = str(images[0].get("media_type") or "image/png")
    return raw, media, payload.get("usage") or {}


def _overlay_title(image: Image.Image, title: str, author: str) -> Image.Image:
    image = image.convert("RGB")
    image = image.copy()
    draw = ImageDraw.Draw(image)
    width, height = image.size
    font_path = find_font()
    title_size = max(22, height // 16)
    author_size = max(16, height // 24)
    title_font = ImageFont.truetype(str(font_path), title_size)
    author_font = ImageFont.truetype(str(font_path), author_size)
    band_h = int(height * 0.22)
    band = Image.new("RGB", (width, band_h), (18, 18, 18))
    image.paste(band, (0, height - band_h))
    margin = max(16, width // 24)
    draw = ImageDraw.Draw(image)
    draw.text((margin, height - band_h + margin // 2), title, font=title_font, fill=(245, 245, 245))
    draw.text(
        (margin, height - band_h + margin // 2 + title_size + 8),
        author,
        font=author_font,
        fill=(200, 200, 200),
    )
    return image


def save_cover(
    raw: bytes,
    dest: Path,
    *,
    title: str = "",
    author: str = "",
    overlay: bool = True,
    size: tuple[int, int] = (600, 800),
) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(BytesIO(raw)) as src:
        image = src.convert("RGB")
    image = image.resize(size, Image.Resampling.LANCZOS)
    if overlay and title:
        image = _overlay_title(image, title, author)
    suffix = dest.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        image.save(dest, "JPEG", quality=88)
    else:
        image.save(dest)
    return dest


def write_frontmatter_cover(source: Path, cover_path: Path) -> None:
    import frontmatter

    post = frontmatter.load(source)
    try:
        rel = cover_path.resolve().relative_to(source.resolve().parent)
    except ValueError:
        rel = cover_path
    post["cover"] = str(rel).replace("\\", "/")
    dumped = frontmatter.dumps(post)
    if not dumped.endswith("\n"):
        dumped += "\n"
    source.write_text(dumped, encoding="utf-8")
