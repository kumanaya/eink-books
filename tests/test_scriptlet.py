from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from eink_books.build import build

FIXTURES = Path(__file__).parent / "fixtures"
REPO = Path(__file__).resolve().parents[2]
CHECK = REPO / "dev-tools" / "check.sh"
EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "hello-book.md"


def _header(path: Path) -> str:
    return "\n".join(path.read_text(encoding="utf-8").splitlines()[:10])


class ScriptletTests(unittest.TestCase):
    def test_reader_header_pages_and_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            artifacts = build(FIXTURES / "simple.md", out, target="scriptlet")
            reader = artifacts["reader"]
            pages = artifacts["pages"]
            text = reader.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("#!/bin/sh\n"))
            self.assertNotIn("\r", text)
            header = _header(reader)
            self.assertIn("# Name: Simple Book", header)
            self.assertIn("# Author: Test Author", header)
            self.assertIn("# DontUseFBInk", header)
            self.assertGreaterEqual(len(list(pages.glob("*.page"))), 1)
            self.assertTrue((out / "simple-book" / "font.ttf").is_file())
            self._assert_check(reader)

    def test_launcher_and_both(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            artifacts = build(EXAMPLE, out, target="both", generate_images=False)
            self.assertIn("epub", artifacts)
            self.assertNotIn("launcher", artifacts)
            self.assertIn("reader", artifacts)
            artifacts = build(EXAMPLE, out, target="both", launcher=True, generate_images=False)
            self.assertIn("launcher", artifacts)
            launcher = artifacts["launcher"]
            header = _header(launcher)
            self.assertIn("# Name:", header)
            self.assertIn("# DontUseFBInk", header)
            body = launcher.read_text(encoding="utf-8")
            self.assertIn("koreader.sh", body)
            self.assertIn("--asap", body)
            self._assert_check(launcher)
            self._assert_check(artifacts["reader"])
            page_files = sorted((out / "o-relogio-de-areia" / "pages").glob("*.page"))
            self.assertGreater(len(page_files), 1)

    def test_no_launcher_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            artifacts = build(FIXTURES / "simple.md", out, target="koreader", launcher=False)
            self.assertIn("epub", artifacts)
            self.assertNotIn("launcher", artifacts)
            self.assertFalse(any(out.glob("*-koreader.sh")))

    def _assert_check(self, script: Path) -> None:
        if not CHECK.is_file():
            self.skipTest("dev-tools/check.sh is not next to this project")
        # check.sh only writes its file list when the target is a directory.
        with tempfile.TemporaryDirectory() as wrap:
            copied = Path(wrap) / script.name
            copied.write_bytes(script.read_bytes())
            result = subprocess.run(
                ["sh", str(CHECK), wrap],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT: passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
