"""Expand <eink-image> tags into generated (or cached) on-disk images."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from eink_books.puter_cover import generate_puter_cover_bytes, resolve_puter_token

IMAGE_TAG = re.compile(
    r"<eink-image(?P<attrs>[^>]*)>(?P<body>.*?)</eink-image>",
    re.IGNORECASE | re.DOTALL,
)
IMAGE_SELF = re.compile(
    r"<eink-image(?P<attrs>[^>]*)/>",
    re.IGNORECASE,
)
ATTR = re.compile(r'([A-Za-z_:][\w:.-]*)\s*=\s*"([^"]*)"')

_PAGE_HINT = (
    "Full-page illustration for an e-ink Kindle book. High contrast, limited "
    "muted palette that still reads in grayscale, no lettering, no captions, "
    "no UI chrome, no watermark."
)


def parse_attrs(raw: str) -> dict[str, str]:
    return {key: value for key, value in ATTR.findall(raw or "")}


def prompt_slug(prompt: str, explicit_id: str = "") -> str:
    if explicit_id:
        safe = re.sub(r"[^a-z0-9-]+", "-", explicit_id.lower()).strip("-")
        if safe:
            return safe[:40]
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
    return digest


def illustration_prompt(prompt: str) -> str:
    body = prompt.strip()
    if _PAGE_HINT.lower() in body.lower():
        return body
    return f"{_PAGE_HINT} {body}"


def _replacement(attrs: dict[str, str], body: str, dest_dir: Path, generate: bool) -> str:
    prompt = (body or attrs.get("prompt") or "").strip()
    if not prompt:
        return ""
    alt = (attrs.get("alt") or prompt.split(".")[0][:80]).strip()
    slug = prompt_slug(prompt, attrs.get("id", ""))
    dest = dest_dir / f"eink-{slug}.jpg"
    if not dest.is_file():
        if not generate:
            return f"\n\n[{alt}]\n\n"
        from eink_books.cover import save_cover

        token = resolve_puter_token()
        raw, _media = generate_puter_cover_bytes(
            prompt=illustration_prompt(prompt),
            token=token,
            aspect_ratio=attrs.get("ratio") or "3:4",
            quality=attrs.get("quality") or None,
        )
        save_cover(raw, dest, overlay=False)
    rel = dest.name
    return f"\n\n![{alt}](images/{rel})\n\n"


def expand_image_tags(markdown: str, source_dir: Path, *, generate: bool = True) -> str:
    """Replace <eink-image> tags with Markdown image references.

    Generated files land in ``<source_dir>/images/eink-<id>.jpg`` and are
    reused on the next build when the prompt (or id) is unchanged.
    """
    dest_dir = source_dir / "images"
    dest_dir.mkdir(parents=True, exist_ok=True)

    def block(match: re.Match[str]) -> str:
        return _replacement(parse_attrs(match.group("attrs")), match.group("body"), dest_dir, generate)

    def self_closing(match: re.Match[str]) -> str:
        return _replacement(parse_attrs(match.group("attrs")), "", dest_dir, generate)

    text = IMAGE_TAG.sub(block, markdown)
    return IMAGE_SELF.sub(self_closing, text)


def find_image_tags(markdown: str) -> list[str]:
    prompts: list[str] = []
    for match in IMAGE_TAG.finditer(markdown):
        prompt = (match.group("body") or parse_attrs(match.group("attrs")).get("prompt") or "").strip()
        if prompt:
            prompts.append(prompt)
    for match in IMAGE_SELF.finditer(markdown):
        prompt = parse_attrs(match.group("attrs")).get("prompt", "").strip()
        if prompt:
            prompts.append(prompt)
    return prompts
