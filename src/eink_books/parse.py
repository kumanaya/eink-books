from __future__ import annotations

import re
import unicodedata
import uuid
from pathlib import Path

import frontmatter

from eink_books.models import Book, Chapter
from eink_books.illustrations import expand_image_tags
from eink_books.render import (
    collect_image_srcs,
    markdown_to_html,
    parse_tokens,
    resolve_images,
    rewrite_html_images,
    split_h1_chapters,
    tokens_to_fbink_paragraphs,
)


def slugify(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug or "book"


def _as_str(value: object, default: str) -> str:
    if value is None:
        return default
    return str(value).strip() or default


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _load_markdown_file(path: Path) -> tuple[dict, str]:
    post = frontmatter.load(path)
    meta = dict(post.metadata)
    return meta, post.content


def _build_chapter(title: str, markdown: str, source_dir: Path) -> Chapter:
    tokens = parse_tokens(markdown)
    html = markdown_to_html(markdown)
    images = resolve_images(collect_image_srcs(tokens), source_dir)
    mapping = {src: f"images/{path.name}" for src, path in images}
    if mapping:
        html = rewrite_html_images(html, mapping)
    return Chapter(
        title=title,
        markdown=markdown,
        html=html,
        fbink_paragraphs=tokens_to_fbink_paragraphs(tokens),
        images=images,
    )


def load_book(source: Path, *, generate_images: bool = True) -> Book:
    source = source.resolve()
    if source.is_file():
        files = [source]
        source_dir = source.parent
    elif source.is_dir():
        files = sorted(p for p in source.iterdir() if p.suffix.lower() == ".md")
        source_dir = source
        if not files:
            raise FileNotFoundError(f"no .md files in {source}")
    else:
        raise FileNotFoundError(f"source not found: {source}")

    book_meta: dict = {}
    bodies: list[str] = []
    for index, path in enumerate(files):
        meta, content = _load_markdown_file(path)
        if index == 0:
            book_meta = meta
        content = content.strip()
        if not content:
            continue
        if source.is_dir() and not re.search(r"(?m)^# ", content):
            heading = _as_str(meta.get("title"), path.stem)
            content = f"# {heading}\n\n{content}"
        bodies.append(content)

    combined = expand_image_tags(
        "\n\n".join(bodies).strip(),
        source_dir,
        generate=generate_images,
    )
    if not combined:
        raise ValueError("markdown source is empty")

    title = _as_str(book_meta.get("title"), "")
    splits = split_h1_chapters(combined)
    if len(splits) == 1 and splits[0][0] == "Chapter" and title:
        splits = [(title, splits[0][1])]
    if not title:
        title = splits[0][0] if splits else source.stem

    author = _as_str(book_meta.get("author"), "Unknown")
    language = _as_str(book_meta.get("language"), "en")
    identifier = _as_str(book_meta.get("identifier"), f"urn:uuid:{uuid.uuid4()}")
    slug = slugify(_as_str(book_meta.get("slug"), title))

    cover = book_meta.get("cover")
    cover_path: Path | None = None
    if cover:
        cover_path = (source_dir / str(cover)).resolve()
        if not cover_path.is_file():
            raise FileNotFoundError(f"cover not found: {cover_path}")

    chapters = [_build_chapter(ch_title, ch_md, source_dir) for ch_title, ch_md in splits]
    if not chapters:
        raise ValueError("no chapters found")

    return Book(
        title=title,
        author=author,
        language=language,
        identifier=identifier,
        slug=slug,
        source_dir=source_dir,
        chapters=chapters,
        cover_path=cover_path,
        description=_as_str(book_meta.get("description"), ""),
        publisher=_as_str(book_meta.get("publisher"), ""),
        date=_as_str(book_meta.get("date"), ""),
        rights=_as_str(book_meta.get("rights"), ""),
        subjects=_as_list(book_meta.get("subjects") or book_meta.get("subject")),
        subtitle=_as_str(book_meta.get("subtitle"), ""),
    )
