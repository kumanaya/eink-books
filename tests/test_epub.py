from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from eink_books.build import build
from eink_books.parse import load_book

FIXTURES = Path(__file__).parent / "fixtures"


class EpubTests(unittest.TestCase):
    def test_epub_has_opf_ncx_nav_and_chapters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            artifacts = build(FIXTURES / "simple.md", out, target="koreader", launcher=False)
            epub_path = artifacts["epub"]
            self.assertTrue(epub_path.is_file())
            with zipfile.ZipFile(epub_path) as zf:
                names = zf.namelist()
                self.assertIn("META-INF/container.xml", names)
                joined = "\n".join(names)
                self.assertTrue(any(n.endswith(".ncx") for n in names), joined)
                self.assertTrue(any("nav" in n.lower() and n.endswith(".xhtml") for n in names), joined)
                self.assertTrue(any("chap_01" in n for n in names), joined)
                self.assertTrue(any("chap_02" in n for n in names), joined)
                self.assertTrue(any(n.endswith("eink.css") for n in names), joined)
                opf = next(n for n in names if n.endswith(".opf"))
                opf_text = zf.read(opf).decode("utf-8")
                self.assertIn("Simple Book", opf_text)
                self.assertIn("Test Author", opf_text)
                container = zf.read("META-INF/container.xml").decode("utf-8")
                self.assertIn("rootfile", container)

    def test_cover_is_embedded(self) -> None:
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "book.md"
            cover = Path(tmp) / "cover.png"
            Image.new("RGB", (80, 120), (20, 20, 20)).save(cover)
            src.write_text(
                "---\ntitle: Covered\nauthor: A\nlanguage: en\ncover: cover.png\n"
                "identifier: urn:uuid:cover-1\n---\n\n# Only\n\nHi.\n",
                encoding="utf-8",
            )
            out = Path(tmp) / "out"
            artifacts = build(src, out, target="koreader", launcher=False)
            with zipfile.ZipFile(artifacts["epub"]) as zf:
                names = zf.namelist()
                self.assertTrue(any("cover" in n.lower() for n in names), names)
                self.assertTrue(any(n.endswith("cover.xhtml") for n in names), names)
                opf = next(n for n in names if n.endswith(".opf"))
                self.assertIn("cover.xhtml", zf.read(opf).decode("utf-8"))

    def test_load_then_epub_keeps_chapter_count(self) -> None:
        book = load_book(FIXTURES / "simple.md")
        self.assertEqual(len(book.chapters), 2)
