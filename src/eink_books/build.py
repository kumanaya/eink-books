from __future__ import annotations

from pathlib import Path

from eink_books.devices import DeviceProfile, resolve_device
from eink_books.epub_builder import build_epub
from eink_books.fonts import find_font
from eink_books.parse import load_book
from eink_books.scriptlet_builder import build_launcher, build_reader


def build(
    source: Path,
    out_dir: Path,
    target: str = "both",
    device: str = "kt4",
    width: int | None = None,
    height: int | None = None,
    font_size: float = 14.0,
    font: str | Path | None = None,
    launcher: bool | None = None,
    generate_images: bool = True,
) -> dict[str, Path]:
    if target not in {"koreader", "scriptlet", "both"}:
        raise ValueError(f"unknown target: {target}")
    if launcher is None:
        # One library icon: the FBInk reader when both exist, the KOReader
        # launcher only when the EPUB is the sole target.
        launcher = target == "koreader"

    book = load_book(Path(source), generate_images=generate_images)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    profile: DeviceProfile = resolve_device(device, width, height)
    artifacts: dict[str, Path] = {}

    if target in {"koreader", "both"}:
        artifacts["epub"] = build_epub(book, out_dir / f"{book.slug}.epub")
        if launcher:
            artifacts["launcher"] = build_launcher(book, out_dir)

    if target in {"scriptlet", "both"}:
        font_path = find_font(font)
        artifacts["reader"] = build_reader(book, out_dir, font_path, profile, font_size)
        artifacts["pages"] = out_dir / book.slug / "pages"

    return artifacts
