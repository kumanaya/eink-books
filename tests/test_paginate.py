from __future__ import annotations

import unittest

from eink_books.devices import resolve_device
from eink_books.fonts import find_font
from eink_books.paginate import paginate, wrap_line
from PIL import ImageFont


class DeviceTests(unittest.TestCase):
    def test_kt4_and_override(self) -> None:
        kt4 = resolve_device("kt4")
        self.assertEqual((kt4.width, kt4.height), (600, 800))
        wide = resolve_device("kt4", width=800)
        self.assertEqual(wide.width, 800)
        self.assertEqual(wide.height, 800)
        with self.assertRaises(ValueError):
            resolve_device("not-a-kindle")


class PaginateTests(unittest.TestCase):
    def test_long_text_is_more_than_one_page(self) -> None:
        font = find_font()
        profile = resolve_device("kt4")
        paragraphs = [f"Word number {i} repeats so the page fills up." for i in range(80)]
        pages = paginate(paragraphs, font, profile, font_size_pt=14)
        self.assertGreater(len(pages), 1)
        self.assertTrue(all(page.endswith("\n") for page in pages))

    def test_wrap_respects_width(self) -> None:
        font = ImageFont.truetype(str(find_font()), size=32)
        lines = wrap_line("alpha beta gamma delta epsilon zeta", font, max_width=80)
        self.assertGreater(len(lines), 1)
