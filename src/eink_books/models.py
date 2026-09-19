from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Chapter:
    title: str
    markdown: str
    html: str
    fbink_paragraphs: list[str]
    images: list[tuple[str, Path]] = field(default_factory=list)


@dataclass
class Book:
    title: str
    author: str
    language: str
    identifier: str
    slug: str
    source_dir: Path
    chapters: list[Chapter]
    cover_path: Path | None = None
    description: str = ""
    publisher: str = ""
    date: str = ""
    rights: str = ""
    subjects: list[str] = field(default_factory=list)
    subtitle: str = ""
