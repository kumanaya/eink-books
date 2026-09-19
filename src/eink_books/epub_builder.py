from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ebooklib import epub

from eink_books.models import Book

_CSS_NAME = "eink.css"


def _package_css() -> bytes:
    from importlib.resources import files

    return files("eink_books").joinpath("css/eink.css").read_bytes()


def _chapter_body(title: str, html: str) -> str:
    return f"<h1>{_escape(title)}</h1>\n{html}"


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _cover_page(book: Book, cover_href: str) -> str:
    alt = _escape(f"Cover: {book.title}")
    return (
        f'<div class="cover-page"><img src="{cover_href}" alt="{alt}" /></div>'
    )


def _modified() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_epub(book: Book, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)

    epub_book = epub.EpubBook()
    epub_book.set_identifier(book.identifier)
    title = book.title if not book.subtitle else f"{book.title}: {book.subtitle}"
    epub_book.set_title(title)
    epub_book.set_language(book.language)
    epub_book.add_author(book.author)
    epub_book.add_metadata("DC", "title", book.title)
    if book.description:
        epub_book.add_metadata("DC", "description", book.description)
    if book.publisher:
        epub_book.add_metadata("DC", "publisher", book.publisher)
    if book.date:
        epub_book.add_metadata("DC", "date", book.date)
    if book.rights:
        epub_book.add_metadata("DC", "rights", book.rights)
    for subject in book.subjects:
        epub_book.add_metadata("DC", "subject", subject)
    epub_book.add_metadata("DC", "type", "Text")
    epub_book.add_metadata(None, "meta", "", {"property": "dcterms:modified", "content": _modified()})

    style = epub.EpubItem(
        uid="style_eink",
        file_name=_CSS_NAME,
        media_type="text/css",
        content=_package_css(),
    )
    epub_book.add_item(style)

    spine: list = []
    cover_page = None
    if book.cover_path is not None:
        cover_name = f"cover{book.cover_path.suffix.lower()}"
        epub_book.set_cover(cover_name, book.cover_path.read_bytes(), create_page=False)
        cover_page = epub.EpubHtml(
            title="Cover",
            file_name="cover.xhtml",
            lang=book.language,
        )
        cover_page.content = _cover_page(book, cover_name)
        cover_page.add_item(style)
        epub_book.add_item(cover_page)
        spine.append(cover_page)

    added_images: set[str] = set()
    chapters: list[epub.EpubHtml] = []
    for index, chapter in enumerate(book.chapters, start=1):
        item = epub.EpubHtml(
            title=chapter.title,
            file_name=f"chap_{index:02d}.xhtml",
            lang=book.language,
        )
        item.content = _chapter_body(chapter.title, chapter.html)
        item.add_item(style)
        epub_book.add_item(item)
        chapters.append(item)

        for _src, path in chapter.images:
            fname = path.name
            if fname in added_images:
                continue
            added_images.add(fname)
            epub_book.add_item(
                epub.EpubItem(
                    uid=f"img_{len(added_images)}",
                    file_name=f"images/{fname}",
                    media_type=_media_type(path),
                    content=path.read_bytes(),
                )
            )

    epub_book.toc = tuple(chapters)
    epub_book.add_item(epub.EpubNcx())
    nav = epub.EpubNav()
    epub_book.add_item(nav)
    epub_book.spine = [*spine, "nav", *chapters]

    epub.write_epub(str(dest), epub_book, {"epub2_guide": True})
    return dest


def _media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
    }.get(suffix, "application/octet-stream")
