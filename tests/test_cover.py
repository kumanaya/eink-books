from __future__ import annotations

import base64
import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from eink_books.cover import (
    choose_aspect_ratio,
    choose_quality,
    cover_prompt,
    estimate_usd,
    generate_cover_bytes,
    pick_cheapest_model,
    save_cover,
    write_frontmatter_cover,
)
from eink_books.cover import ImageModel
from eink_books.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (40, 60), (80, 80, 80)).save(buf, "PNG")
    return buf.getvalue()


class EstimateTests(unittest.TestCase):
    def test_prefers_per_image_over_higher_tier(self) -> None:
        pricing = [
            {"billable": "output_image", "unit": "image", "cost_usd": 0.019, "variant": "2k"},
            {"billable": "output_image", "unit": "image", "cost_usd": 0.01},
        ]
        self.assertAlmostEqual(estimate_usd(pricing), 0.01)

    def test_megapixel_and_token(self) -> None:
        self.assertAlmostEqual(
            estimate_usd([{"billable": "output_image", "unit": "megapixel", "cost_usd": 0.014}]),
            0.014,
        )
        self.assertAlmostEqual(
            estimate_usd([{"billable": "output_image", "unit": "token", "cost_usd": 0.000008}]),
            0.0064,
        )


class PromptTests(unittest.TestCase):
    def test_includes_title_and_eink_hint(self) -> None:
        prompt = cover_prompt("O Relogio de Areia", "Daniel Kumanaya", "hourglass", "pt")
        self.assertIn("O Relogio de Areia", prompt)
        self.assertIn("Daniel Kumanaya", prompt)
        self.assertIn("e-ink", prompt)
        self.assertIn("hourglass", prompt)
        self.assertIn("Portuguese", prompt)


class AspectTests(unittest.TestCase):
    def test_falls_back_to_portrait(self) -> None:
        model = ImageModel(
            id="x",
            name="x",
            estimate_usd=0.01,
            aspect_ratios=("1:1", "2:3", "auto"),
            qualities=("auto", "low"),
            pricing_note="",
        )
        self.assertEqual(choose_aspect_ratio(model, "3:4"), "2:3")
        self.assertEqual(choose_quality(model, None), "low")
        mute = ImageModel("muse", "muse", 0.01, (), (), "")
        self.assertIsNone(choose_aspect_ratio(mute, "3:4"))
        self.assertIsNone(choose_quality(mute, "low"))


class PickerTests(unittest.TestCase):
    def test_picks_cheapest_portrait(self) -> None:
        models = [
            ImageModel("dear", "dear", 0.05, ("3:4",), ("low",), ""),
            ImageModel("cheap", "cheap", 0.006, ("2:3",), ("low",), ""),
            ImageModel("square-only", "sq", 0.001, ("1:1",), (), ""),
        ]
        picked = pick_cheapest_model(models)
        self.assertEqual(picked.id, "cheap")


class SaveTests(unittest.TestCase):
    def test_resizes_and_writes_jpeg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "cover.jpg"
            save_cover(_png_bytes(), dest, title="Hello", author="A")
            with Image.open(dest) as image:
                self.assertEqual(image.size, (600, 800))
                self.assertEqual(image.format, "JPEG")


class GenerateTests(unittest.TestCase):
    def test_decodes_b64(self) -> None:
        raw = _png_bytes()

        def fetch(url, headers, body):
            self.assertIn("/images", url)
            self.assertEqual(body["model"], "openai/gpt-image-1-mini")
            return {
                "data": [{"b64_json": base64.b64encode(raw).decode("ascii"), "media_type": "image/png"}],
                "usage": {"cost": 0.006},
            }

        got, media, usage = generate_cover_bytes(
            model="openai/gpt-image-1-mini",
            prompt="a cover",
            api_key="sk-test",
            aspect_ratio="2:3",
            quality="low",
            fetch=fetch,
        )
        self.assertEqual(got, raw)
        self.assertEqual(media, "image/png")
        self.assertEqual(usage["cost"], 0.006)


class FrontmatterTests(unittest.TestCase):
    def test_writes_cover_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "book.md"
            src.write_text("---\ntitle: T\nauthor: A\n---\n\n# Hi\n\nText.\n", encoding="utf-8")
            cover = Path(tmp) / "cover.jpg"
            cover.write_bytes(b"x")
            write_frontmatter_cover(src, cover)
            self.assertIn("cover: cover.jpg", src.read_text(encoding="utf-8"))


class CliDryRunTests(unittest.TestCase):
    def test_dry_run_needs_no_key(self) -> None:
        code = main(
            [
                "cover",
                str(FIXTURES / "simple.md"),
                "--model",
                "openai/gpt-image-1-mini",
                "--dry-run",
            ]
        )
        self.assertEqual(code, 0)
