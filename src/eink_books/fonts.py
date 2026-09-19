from __future__ import annotations

from importlib.resources import files
from pathlib import Path

_SYSTEM_FONTS = (
    Path("/usr/share/fonts/liberation/LiberationSerif-Regular.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    Path("/usr/share/fonts/TTF/DejaVuSerif.ttf"),
    Path("/usr/share/fonts/noto/NotoSerif-Regular.ttf"),
)


def bundled_font() -> Path:
    return Path(str(files("eink_books").joinpath("data/LiberationSerif-Regular.ttf")))


def find_font(explicit: str | Path | None = None) -> Path:
    """Return a serif TTF for desk pagination and for shipping to the Kindle."""
    if explicit is not None:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"font not found: {path}")
        return path

    bundled = bundled_font()
    if bundled.is_file():
        return bundled

    for candidate in _SYSTEM_FONTS:
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        "no serif TTF found; pass --font PATH "
        "(needed so Portuguese accents survive on the Kindle)"
    )
