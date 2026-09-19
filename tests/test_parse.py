from __future__ import annotations

import unittest
from pathlib import Path

from eink_books.parse import load_book, slugify
from eink_books.render import markdown_to_html, split_h1_chapters, tokens_to_fbink_paragraphs
from eink_books.render import parse_tokens

FIXTURES = Path(__file__).parent / "fixtures"


class SlugifyTests(unittest.TestCase):
    def test_ascii_and_accents(self) -> None:
        self.assertEqual(slugify("O Relogio de Areia"), "o-relogio-de-areia")
        self.assertEqual(slugify("O Relógio de Areia"), "o-relogio-de-areia")
        self.assertEqual(slugify("!!!"), "book")


class SplitTests(unittest.TestCase):
    def test_splits_on_h1_not_h2(self) -> None:
        chapters = split_h1_chapters("# One\n\nHi\n\n## Sub\n\n# Two\n\nBye\n")
        self.assertEqual([title for title, _body in chapters], ["One", "Two"])
        self.assertIn("## Sub", chapters[0][1])

    def test_no_heading_is_one_chapter(self) -> None:
        chapters = split_h1_chapters("just text\n")
        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0][0], "Chapter")

    def test_ignores_hash_inside_fence(self) -> None:
        md = "# Real\n\n```\n# Not a heading\n```\n\nbody\n"
        chapters = split_h1_chapters(md)
        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0][0], "Real")
        self.assertIn("# Not a heading", chapters[0][1])


class RenderTests(unittest.TestCase):
    def test_html_and_fbink(self) -> None:
        md = "Hello **world** and *friends*.\n\n![x](pic.png)\n"
        html = markdown_to_html(md)
        self.assertIn("<strong>world</strong>", html)
        self.assertIn("<em>friends</em>", html)
        paras = tokens_to_fbink_paragraphs(parse_tokens(md))
        self.assertTrue(any("**world**" in p and "*friends*" in p for p in paras))
        self.assertTrue(any("[[eink-image:pic.png]]" in p for p in paras))


class LoadBookTests(unittest.TestCase):
    def test_single_file(self) -> None:
        book = load_book(FIXTURES / "simple.md")
        self.assertEqual(book.title, "Simple Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.language, "en")
        self.assertEqual(book.slug, "simple-book")
        self.assertEqual([c.title for c in book.chapters], ["First", "Second"])
        self.assertIn("<strong>world</strong>", book.chapters[0].html)
        self.assertTrue(any("**world**" in p for p in book.chapters[0].fbink_paragraphs))

    def test_folder(self) -> None:
        book = load_book(FIXTURES / "chapters")
        self.assertEqual(book.title, "Folder Book")
        self.assertEqual([c.title for c in book.chapters], ["Folder Book", "Night"])


if __name__ == "__main__":
    unittest.main()
