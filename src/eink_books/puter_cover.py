"""Generate book covers via Puter's image-generation driver.

Puter.js (`puter.ai.txt2img`) is the documented frontend. From a desktop CLI
the same call is `POST https://api.puter.com/drivers/call` with
`interface=puter-image-generation`. Auth is a free Puter account token
(User-Pays): the developer does not need OpenRouter or an image-model key.

See: https://developer.puter.com/tutorials/free-unlimited-image-generation-api/
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

from eink_books.env import load_project_env

DRIVERS_URL = "https://api.puter.com/drivers/call"
DEFAULT_MODEL = "openai/gpt-image-1-mini"
DEFAULT_DRIVER = "ai-image"
INTERFACE = "puter-image-generation"
_HTTP_TIMEOUT = 180

# Catalog from the Puter.js tutorial (used when the live `list` call is skipped
# or unavailable). Order matches the published page.
PUTER_MODELS: tuple[str, ...] = (
    "x-ai/grok-imagine-image-quality",
    "x-ai/grok-imagine-image",
    "openai/gpt-image-2",
    "qwen/qwen-image-2.0-pro",
    "qwen/qwen-image-2.0",
    "google/gemini-3.1-flash-image-preview",
    "black-forest-labs/flux-2-klein-9b-base",
    "black-forest-labs/flux-2-klein-4b",
    "wan-ai/wan2.6-image",
    "google/gemini-3-pro-image-preview",
    "openai/gpt-image-1.5",
    "openai/gpt-image-1-mini",
    "bytedance-seed/seedream-4.0",
    "google/imagen-4.0-ultra",
    "google/imagen-4.0-fast",
    "google/imagen-4.0",
    "leonardoai/lucid-origin",
    "qwen/qwen-image",
    "black-forest-labs/flux.1-kontext-pro",
    "black-forest-labs/flux.1-kontext-max",
    "black-forest-labs/flux.2-max",
    "black-forest-labs/flux.2-flex",
    "black-forest-labs/flux-2-pro",
    "black-forest-labs/flux-2-dev",
    "google/imagen-4.0-preview",
    "bytedance-seed/seedream-3.0",
    "openai/gpt-image-1",
    "google/gemini-2.5-flash-image",
    "hidream-ai/hidream-i1-full",
    "hidream-ai/hidream-i1-fast",
    "hidream-ai/hidream-i1-dev",
    "ideogram/ideogram-3.0",
    "leonardoai/phoenix-1.0",
    "rundiffusion/juggernaut-pro-flux",
    "rundiffusion/juggernaut-lightning-flux",
    "black-forest-labs/flux-1.1-pro",
    "black-forest-labs/flux.1-krea-dev",
    "black-forest-labs/flux-schnell",
    "stabilityai/stable-diffusion-3-medium",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "lykon/dreamshaper",
)

Fetcher = Callable[[str, dict[str, str] | None, dict[str, Any] | None], tuple[bytes, str]]


@dataclass(frozen=True)
class PuterModel:
    id: str
    name: str
    provider: str = ""


def resolve_puter_token(explicit: str | None = None) -> str:
    load_project_env()
    token = (explicit or os.environ.get("PUTER_AUTH_TOKEN") or "").strip()
    if not token:
        raise ValueError(
            "set PUTER_AUTH_TOKEN, put it in .env, or pass --token "
            "(create one at https://puter.com/dashboard — Puter is User-Pays, no image-API key)"
        )
    return token


def puter_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://puter.com",
        "Referer": "https://puter.com/",
        "User-Agent": "eink-books/0.1 (Puter image generation)",
    }


def _http(
    url: str,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
) -> tuple[bytes, str]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="GET" if body is None else "POST")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
            media = resp.headers.get_content_type() or ""
            return resp.read(), media
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Puter HTTP {exc.code}: {detail}") from exc


def driver_body(
    *,
    method: str,
    args: dict[str, Any] | None = None,
    driver: str = DEFAULT_DRIVER,
    token: str | None = None,
    test_mode: bool = False,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "interface": INTERFACE,
        "driver": driver,
        "method": method,
        "args": args or {},
        "test_mode": test_mode,
    }
    if token:
        body["auth_token"] = token
    return body


def _decode_data_uri(uri: str) -> tuple[bytes, str]:
    header, _, payload = uri.partition(",")
    if not payload:
        raise RuntimeError(f"Puter returned an empty data URI: {uri[:80]}")
    media = "image/png"
    if header.startswith("data:") and ";" in header:
        media = header[5:].split(";", 1)[0] or media
    if ";base64" in header:
        return base64.b64decode(payload), media
    return payload.encode("utf-8"), media


def _looks_like_image(raw: bytes) -> bool:
    return raw.startswith((b"\x89PNG", b"\xff\xd8\xff", b"RIFF", b"GIF8"))


def _error_from_payload(payload: dict[str, Any]) -> str:
    error = payload.get("error")
    if isinstance(error, dict):
        message = error.get("message") or error.get("code") or error
        return str(message)
    if error:
        return str(error)
    return json.dumps(payload, ensure_ascii=False)[:400]


def decode_image_payload(
    raw: bytes,
    media: str = "",
    *,
    fetch: Fetcher = _http,
) -> tuple[bytes, str]:
    """Turn a Puter driver response (blob, JSON envelope, URL, data URI) into bytes."""
    stripped = raw.lstrip()
    if media.startswith("image/") or _looks_like_image(raw):
        return raw, media or "image/png"
    text = raw.decode("utf-8", errors="replace").strip()
    if text.startswith("data:image"):
        return _decode_data_uri(text)
    if text.startswith(("http://", "https://")):
        fetched, fetched_media = fetch(text, None, None)
        return fetched, fetched_media or "image/png"
    if not text.startswith("{") and not text.startswith("["):
        raise RuntimeError(f"Puter returned no image: {text[:200]}")
    payload = json.loads(text)
    if isinstance(payload, dict) and payload.get("success") is False:
        raise RuntimeError(f"Puter driver error: {_error_from_payload(payload)}")
    result = payload.get("result") if isinstance(payload, dict) else payload
    if isinstance(result, dict):
        result = (
            result.get("url")
            or result.get("image")
            or result.get("src")
            or result.get("b64_json")
            or result.get("data")
        )
    if isinstance(result, str) and result.startswith("data:"):
        return _decode_data_uri(result)
    if isinstance(result, str) and result.startswith(("http://", "https://")):
        fetched, fetched_media = fetch(result, None, None)
        return fetched, fetched_media or "image/png"
    if isinstance(result, str):
        try:
            return base64.b64decode(result), "image/png"
        except Exception as exc:
            raise RuntimeError(f"Puter returned no image: {result[:200]}") from exc
    raise RuntimeError(f"Puter returned no image: {text[:200]}")


def generate_puter_cover_bytes(
    *,
    prompt: str,
    token: str,
    model: str = DEFAULT_MODEL,
    driver: str = DEFAULT_DRIVER,
    aspect_ratio: str | None = "3:4",
    quality: str | None = None,
    test_mode: bool = False,
    fetch: Fetcher = _http,
) -> tuple[bytes, str]:
    args: dict[str, Any] = {"prompt": prompt, "model": model, "test_mode": test_mode}
    if aspect_ratio:
        args["aspect_ratio"] = aspect_ratio
    if quality:
        args["quality"] = quality
    body = driver_body(method="generate", args=args, driver=driver, token=token, test_mode=test_mode)
    raw, media = fetch(DRIVERS_URL, puter_headers(token), body)
    return decode_image_payload(raw, media, fetch=fetch)


def _normalize_listed(item: Any) -> PuterModel | None:
    if isinstance(item, str) and item.strip():
        return PuterModel(id=item.strip(), name=item.strip())
    if not isinstance(item, dict):
        return None
    model_id = str(item.get("id") or item.get("puterId") or item.get("name") or "").strip()
    if not model_id:
        return None
    return PuterModel(
        id=model_id,
        name=str(item.get("name") or model_id),
        provider=str(item.get("provider") or ""),
    )


def catalog_models() -> list[PuterModel]:
    return [PuterModel(id=mid, name=mid) for mid in PUTER_MODELS]


def list_puter_models(
    token: str | None = None,
    *,
    fetch: Fetcher | None = None,
) -> list[PuterModel]:
    """Ask the live driver for models; fall back to the published tutorial list."""
    if not token:
        return catalog_models()
    do_fetch = fetch or _http
    for method in ("list", "models"):
        try:
            raw, _media = do_fetch(
                DRIVERS_URL,
                puter_headers(token),
                driver_body(method=method, args={}, token=token),
            )
        except RuntimeError:
            continue
        text = raw.decode("utf-8", errors="replace").strip()
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        result = payload.get("result") if isinstance(payload, dict) else payload
        if isinstance(result, dict):
            result = result.get("models") or result.get("data") or result.get("items")
        if not isinstance(result, list):
            continue
        models = [m for item in result if (m := _normalize_listed(item))]
        if models:
            return models
    return catalog_models()
