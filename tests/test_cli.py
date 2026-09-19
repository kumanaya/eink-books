from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from eink_books.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


class CliTests(unittest.TestCase):
    def test_build_both(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code = main(
                [
                    "build",
                    str(FIXTURES / "simple.md"),
                    "--target",
                    "both",
                    "--out",
                    tmp,
                ]
            )
            self.assertEqual(code, 0)
            out = Path(tmp)
            self.assertTrue((out / "simple-book.epub").is_file())
            self.assertTrue((out / "simple-book.sh").is_file())
            self.assertFalse((out / "simple-book-koreader.sh").is_file())

    def test_missing_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code = main(["build", str(Path(tmp) / "nope.md"), "--out", tmp])
            self.assertEqual(code, 1)
