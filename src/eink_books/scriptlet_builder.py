from __future__ import annotations

import re
import shutil
from importlib.resources import files
from pathlib import Path

from PIL import Image

from eink_books.devices import DeviceProfile
from eink_books.models import Book
from eink_books.paginate import paginate
from eink_books.render import parse_image_page_mark

_KINDLE_DOCS = "/mnt/us/documents"
_KINDLE_APP = "/mnt/us/extensions/eink-books"
_KOREADER = "/mnt/us/koreader/koreader.sh"


def _header_value(text: str) -> str:
    return " ".join(text.split()) or "Untitled"


def _load_template(name: str) -> str:
    return files("eink_books").joinpath(f"templates/{name}").read_text(encoding="utf-8")


def _apply(template: str, mapping: dict[str, str], icon: str) -> str:
    text = template
    for key, value in mapping.items():
        text = text.replace(f"__{key}__", value)
    if icon:
        text = text.replace("__ICON__", icon)
    else:
        text = re.sub(r"# Icon: __ICON__\n", "", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("#!/bin/sh\n"):
        raise ValueError("generated scriptlet lost its shebang")
    if "# Name:" not in "\n".join(text.splitlines()[:10]):
        raise ValueError("generated scriptlet is missing # Name: in the header")
    return text


def _write_sh(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    path.chmod(path.stat().st_mode | 0o111)
    return path


def _prepare_cover(book: Book, app_dir: Path) -> Path | None:
    if book.cover_path is None:
        return None
    dest = app_dir / "cover.jpg"
    image = Image.open(book.cover_path)
    if image.mode not in {"RGB", "L"}:
        image = image.convert("RGB")
    elif image.mode == "L":
        image = image.convert("RGB")
    image.thumbnail((600, 800))
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest, "JPEG", quality=85)
    return dest


def _icon_path(slug: str, has_cover: bool) -> str:
    if not has_cover:
        return ""
    return f"{_KINDLE_APP}/{slug}/cover.jpg"


def write_pages(
    book: Book,
    app_dir: Path,
    font_path: Path,
    profile: DeviceProfile,
    font_size_pt: float,
) -> list[Path]:
    paragraphs: list[str] = []
    for chapter in book.chapters:
        paragraphs.append(f"**{chapter.title}**")
        paragraphs.extend(chapter.fbink_paragraphs)

    pages = paginate(paragraphs, font_path, profile, font_size_pt)
    if book.cover_path is not None:
        pages = ["@image:cover.jpg\n", *pages]

    images_dir = app_dir / "images"
    if images_dir.exists():
        shutil.rmtree(images_dir)
    copied: set[str] = set()
    for chapter in book.chapters:
        for _src, path in chapter.images:
            if path.name in copied or not path.is_file():
                continue
            images_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, images_dir / path.name)
            copied.add(path.name)

    page_dir = app_dir / "pages"
    if page_dir.exists():
        shutil.rmtree(page_dir)
    page_dir.mkdir(parents=True)
    paths: list[Path] = []
    for index, text in enumerate(pages, start=1):
        src = parse_image_page_mark(text)
        if src:
            text = f"@image:{_scriptlet_image_ref(src)}\n"
        path = page_dir / f"{index:04d}.page"
        path.write_text(text, encoding="utf-8", newline="\n")
        paths.append(path)
    shutil.copy2(font_path, app_dir / "font.ttf")
    return paths


def _scriptlet_image_ref(src: str) -> str:
    name = Path(src).name
    if name.startswith("cover."):
        return name
    return f"images/{name}"


def build_reader(
    book: Book,
    out_dir: Path,
    font_path: Path,
    profile: DeviceProfile,
    font_size_pt: float,
) -> Path:
    app_dir = out_dir / book.slug
    app_dir.mkdir(parents=True, exist_ok=True)
    cover = _prepare_cover(book, app_dir)
    pages = write_pages(book, app_dir, font_path, profile, font_size_pt)
    mapping = {
        "NAME": _header_value(book.title),
        "AUTHOR": _header_value(book.author),
        "DESCRIPTION": "Scriptlet book",
        "APP_DIR": f"{_KINDLE_APP}/{book.slug}",
        "PAGE_COUNT": str(len(pages)),
        "FONT_SIZE": str(int(round(font_size_pt))),
        "SCREEN_W": str(profile.width),
        "SCREEN_H": str(profile.height),
    }
    text = _apply(_load_template("reader.sh.tmpl"), mapping, _icon_path(book.slug, cover is not None))
    return _write_sh(out_dir / f"{book.slug}.sh", text)


def build_launcher(book: Book, out_dir: Path) -> Path:
    app_dir = out_dir / book.slug
    app_dir.mkdir(parents=True, exist_ok=True)
    cover = _prepare_cover(book, app_dir)
    mapping = {
        "NAME": _header_value(book.title),
        "AUTHOR": _header_value(book.author),
        "DESCRIPTION": "Open in KOReader",
        "APP_DIR": f"{_KINDLE_APP}/{book.slug}",
        "EPUB_PATH": f"{_KINDLE_DOCS}/{book.slug}.epub",
        "KOREADER": _KOREADER,
    }
    text = _apply(
        _load_template("launcher.sh.tmpl"),
        mapping,
        _icon_path(book.slug, cover is not None),
    )
    return _write_sh(out_dir / f"{book.slug}-koreader.sh", text)
