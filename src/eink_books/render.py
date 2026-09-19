from __future__ import annotations

import re
from pathlib import Path

from markdown_it import MarkdownIt
from markdown_it.token import Token

_MD = MarkdownIt("commonmark", {"html": False}).enable("strikethrough")
IMAGE_PAGE_RE = re.compile(r"^\[\[eink-image:(.+?)\]\]$")


def image_page_mark(src: str) -> str:
    return f"[[eink-image:{src}]]"


def parse_image_page_mark(paragraph: str) -> str | None:
    match = IMAGE_PAGE_RE.match(paragraph.strip())
    return match.group(1) if match else None


def wrap_illustration_figures(html: str) -> str:
    return re.sub(
        r"<p>\s*(<img\b[^>]*>)\s*</p>",
        r'<figure class="illustration">\1</figure>',
        html,
    )


def parse_tokens(markdown: str) -> list[Token]:
    return _MD.parse(markdown)


def markdown_to_html(markdown: str) -> str:
    return wrap_illustration_figures(_MD.render(markdown))


def rewrite_html_images(html: str, mapping: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        src = match.group(1)
        return f'src="{mapping.get(src, src)}"'

    return re.sub(r'src="([^"]+)"', repl, html)


def collect_image_srcs(tokens: list[Token]) -> list[str]:
    found: list[str] = []
    for token in tokens:
        if token.type == "image":
            src = token.attrGet("src")
            if src:
                found.append(src)
        if token.children:
            found.extend(collect_image_srcs(token.children))
    return found


def resolve_images(srcs: list[str], source_dir: Path) -> list[tuple[str, Path]]:
    resolved: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for src in srcs:
        if src in seen or src.startswith(("http://", "https://", "data:")):
            continue
        seen.add(src)
        path = (source_dir / src).resolve()
        if path.is_file():
            resolved.append((src, path))
    return resolved


def _inline_fbink(tokens: list[Token] | None) -> str:
    if not tokens:
        return ""
    parts: list[str] = []
    for token in tokens:
        if token.type == "text":
            parts.append(token.content)
        elif token.type == "softbreak":
            parts.append(" ")
        elif token.type == "hardbreak":
            parts.append("\n")
        elif token.type == "code_inline":
            parts.append(token.content)
        elif token.type == "image":
            continue
        elif token.type == "strong_open":
            parts.append("**")
        elif token.type == "strong_close":
            parts.append("**")
        elif token.type == "em_open":
            parts.append("*")
        elif token.type == "em_close":
            parts.append("*")
        elif token.type in {"s_open", "s_close"}:
            continue
        elif token.type == "link_open":
            continue
        elif token.type == "link_close":
            continue
        elif token.children:
            parts.append(_inline_fbink(token.children))
    return "".join(parts)


def tokens_to_fbink_paragraphs(tokens: list[Token]) -> list[str]:
    paragraphs: list[str] = []
    i = 0
    list_index = 0
    in_ordered = False

    while i < len(tokens):
        token = tokens[i]
        t = token.type

        if t == "heading_open":
            inline = tokens[i + 1] if i + 1 < len(tokens) else None
            text = _inline_fbink(inline.children if inline else None).strip()
            if text:
                paragraphs.append(f"**{text}**")
            i += 3
            continue

        if t == "paragraph_open":
            inline = tokens[i + 1] if i + 1 < len(tokens) else None
            children = inline.children if inline else None
            text = _inline_fbink(children).strip()
            if text:
                paragraphs.append(text)
            for src in collect_image_srcs(children or []):
                paragraphs.append(image_page_mark(src))
            i += 3
            continue

        if t == "blockquote_open":
            inner: list[Token] = []
            depth = 1
            i += 1
            while i < len(tokens) and depth:
                if tokens[i].type == "blockquote_open":
                    depth += 1
                elif tokens[i].type == "blockquote_close":
                    depth -= 1
                    if depth == 0:
                        break
                inner.append(tokens[i])
                i += 1
            for para in tokens_to_fbink_paragraphs(inner):
                paragraphs.append(f"> {para}")
            i += 1
            continue

        if t == "bullet_list_open":
            in_ordered = False
            i += 1
            continue

        if t == "ordered_list_open":
            in_ordered = True
            list_index = 0
            i += 1
            continue

        if t in {"bullet_list_close", "ordered_list_close"}:
            in_ordered = False
            i += 1
            continue

        if t == "list_item_open":
            inner = []
            depth = 1
            i += 1
            while i < len(tokens) and depth:
                if tokens[i].type == "list_item_open":
                    depth += 1
                elif tokens[i].type == "list_item_close":
                    depth -= 1
                    if depth == 0:
                        break
                inner.append(tokens[i])
                i += 1
            body = " ".join(tokens_to_fbink_paragraphs(inner)).strip()
            if in_ordered:
                list_index += 1
                prefix = f"{list_index}. "
            else:
                prefix = "- "
            if body:
                paragraphs.append(prefix + body)
            i += 1
            continue

        if t in {"fence", "code_block"}:
            for line in token.content.rstrip("\n").split("\n"):
                paragraphs.append(line if line else " ")
            i += 1
            continue

        if t == "hr":
            paragraphs.append("--------")
            i += 1
            continue

        if t == "html_block":
            i += 1
            continue

        i += 1

    return [p for p in paragraphs if p.strip()]


def split_h1_chapters(markdown: str) -> list[tuple[str, str]]:
    """Split on ATX h1 headings, ignoring headings inside fences."""
    tokens = parse_tokens(markdown)
    lines = markdown.splitlines()
    starts: list[tuple[int, int, str]] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == "heading_open" and token.tag == "h1" and token.map:
            inline = tokens[i + 1] if i + 1 < len(tokens) else None
            title = _inline_fbink(inline.children if inline else None).strip() or "Chapter"
            start, end = token.map
            starts.append((start, end, title))
        i += 1

    if not starts:
        body = markdown.strip()
        return [("Chapter", body)] if body else []

    chapters: list[tuple[str, str]] = []
    preamble = "\n".join(lines[: starts[0][0]]).strip()
    if preamble:
        chapters.append(("Chapter", preamble))

    for idx, (_start, heading_end, title) in enumerate(starts):
        body_end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        body = "\n".join(lines[heading_end:body_end]).strip()
        chapters.append((title, body))
    return chapters
