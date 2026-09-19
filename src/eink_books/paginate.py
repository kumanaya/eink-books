from __future__ import annotations

import re
from pathlib import Path

from PIL import ImageFont

from eink_books.devices import DeviceProfile
from eink_books.render import parse_image_page_mark

_MARKERS = re.compile(r"\*+")


def visible_text(line: str) -> str:
    return _MARKERS.sub("", line)


def _measure(font: ImageFont.FreeTypeFont, text: str) -> float:
    sample = visible_text(text) or " "
    if hasattr(font, "getlength"):
        return float(font.getlength(sample))
    box = font.getbbox(sample)
    return float(box[2] - box[0])


def wrap_line(text: str, font: ImageFont.FreeTypeFont, max_width: float) -> list[str]:
    text = text.replace("\t", "    ")
    if not text:
        return [""]
    if "\n" in text:
        lines: list[str] = []
        for part in text.split("\n"):
            lines.extend(wrap_line(part, font, max_width))
        return lines

    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if _measure(font, candidate) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        if _measure(font, word) <= max_width:
            current = word
            continue
        # Hard-break a single overlong token.
        chunk = ""
        for char in word:
            trial = chunk + char
            if chunk and _measure(font, trial) > max_width:
                lines.append(chunk)
                chunk = char
            else:
                chunk = trial
        current = chunk
    if current:
        lines.append(current)
    return lines or [""]


def paginate(
    paragraphs: list[str],
    font_path: Path,
    profile: DeviceProfile,
    font_size_pt: float,
    margin: int = 28,
) -> list[str]:
    px = max(10, int(round(font_size_pt * profile.dpi / 72.0)))
    font = ImageFont.truetype(str(font_path), size=px)
    line_h = max(px + 2, int(round(px * 1.35)))
    slack = 8
    usable_w = max(40.0, float(profile.width - (2 * margin) - slack))
    footer = max(20, int(round(px * 1.2)))
    usable_h = max(line_h, profile.height - (2 * margin) - footer)

    pages: list[list[str]] = []
    current: list[str] = []
    y = 0

    def flush() -> None:
        nonlocal current, y
        while current and current[-1] == "":
            current.pop()
        if current:
            pages.append(current)
        current = []
        y = 0

    def add_line(line: str, height: int) -> None:
        nonlocal y
        if y + height > usable_h and current:
            flush()
        current.append(line)
        y += height

    for para in paragraphs:
        if parse_image_page_mark(para):
            flush()
            pages.append([para.strip()])
            continue
        wrapped = wrap_line(para, font, usable_w)
        for line in wrapped:
            add_line(line, line_h)
        if current:
            add_line("", line_h // 2)

    flush()
    if not pages:
        pages = [[""]]
    return ["\n".join(page).rstrip() + "\n" for page in pages]
