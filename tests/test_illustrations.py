from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from PIL import Image

from eink_books.devices import resolve_device
from eink_books.fonts import find_font
from eink_books.illustrations import expand_image_tags, find_image_tags, prompt_slug
from eink_books.parse import load_book
from eink_books.paginate import paginate
from eink_books.render import image_page_mark


class TagTests(unittest.TestCase):
    def test_finds_block_and_self_closing(self) -> None:
        md = (
            '<eink-image id="a">a girl on a beach</eink-image>\n\n'
            '<eink-image prompt="hourglass in sand" />\n'
        )
        self.assertEqual(find_image_tags(md), ["a girl on a beach", "hourglass in sand"])

    def test_expands_to_cached_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            images.mkdir()
            dest = images / f"eink-{prompt_slug('hourglass')}.jpg"
            Image.new("RGB", (40, 60), (10, 10, 10)).save(dest)
            out = expand_image_tags(
                '<eink-image>hourglass</eink-image>\n\nText.\n',
                root,
                generate=False,
            )
            self.assertIn(f"](images/{dest.name})", out)
            self.assertNotIn("<eink-image>", out)

    def test_missing_without_generate_is_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = expand_image_tags("<eink-image>never-made</eink-image>", Path(tmp), generate=False)
            self.assertIn("[never-made]", out)


class LoadTests(unittest.TestCase):
    def test_book_metadata_and_figure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            images.mkdir()
            dest = images / "eink-scene.jpg"
            Image.new("RGB", (40, 60), (30, 30, 30)).save(dest)
            src = root / "book.md"
            src.write_text(
                "---\ntitle: T\nauthor: A\nlanguage: pt\n"
                "description: A blurb.\npublisher: House\n"
                "subjects:\n  - Fiction\n---\n\n"
                "# One\n\nHi.\n\n"
                '<eink-image id="scene" alt="A scene">ignored because cached</eink-image>\n',
                encoding="utf-8",
            )
            book = load_book(src, generate_images=False)
            self.assertEqual(book.description, "A blurb.")
            self.assertEqual(book.publisher, "House")
            self.assertEqual(book.subjects, ["Fiction"])
            self.assertIn('class="illustration"', book.chapters[0].html)
            self.assertTrue(any("[[eink-image:" in p for p in book.chapters[0].fbink_paragraphs))
            self.assertEqual(len(book.chapters[0].images), 1)


class PageMarkTests(unittest.TestCase):
    def test_image_is_its_own_page(self) -> None:
        paras = ["hello there " * 8, image_page_mark("images/x.jpg"), "after"]
        pages = paginate(paras, find_font(), resolve_device("kt4"), 14.0)
        self.assertTrue(any("[[eink-image:images/x.jpg]]" in p for p in pages))
        self.assertGreaterEqual(len(pages), 2)
