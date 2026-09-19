from __future__ import annotations

import base64
import io
import json
import os
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

from eink_books.cli import main
from eink_books.puter_cover import (
    DEFAULT_MODEL,
    PUTER_MODELS,
    decode_image_payload,
    generate_puter_cover_bytes,
    list_puter_models,
    resolve_puter_token,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (40, 60), (80, 80, 80)).save(buf, "PNG")
    return buf.getvalue()


class TokenTests(unittest.TestCase):
    def test_requires_token(self) -> None:
        with mock.patch("eink_books.puter_cover.load_project_env"):
            with mock.patch.dict(os.environ, {}, clear=True):
                os.environ.pop("PUTER_AUTH_TOKEN", None)
                with self.assertRaises(ValueError):
                    resolve_puter_token(None)

    def test_reads_env(self) -> None:
        with mock.patch("eink_books.puter_cover.load_project_env"):
            with mock.patch.dict(os.environ, {"PUTER_AUTH_TOKEN": " tok "}):
                self.assertEqual(resolve_puter_token(None), "tok")

    def test_reads_dotenv_file(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            env_file = Path(tmp) / ".env"
            env_file.write_text("PUTER_AUTH_TOKEN=from-file\n", encoding="utf-8")
            with mock.patch("eink_books.env._env_paths", return_value=(env_file,)):
                with mock.patch.dict(os.environ, {}, clear=True):
                    os.environ.pop("PUTER_AUTH_TOKEN", None)
                    self.assertEqual(resolve_puter_token(None), "from-file")


class DecodeTests(unittest.TestCase):
    def test_raw_png(self) -> None:
        raw = _png_bytes()
        got, media = decode_image_payload(raw, "image/png")
        self.assertEqual(got, raw)
        self.assertEqual(media, "image/png")

    def test_data_uri(self) -> None:
        raw = _png_bytes()
        uri = "data:image/png;base64," + base64.b64encode(raw).decode("ascii")
        got, media = decode_image_payload(uri.encode("utf-8"))
        self.assertEqual(got, raw)
        self.assertEqual(media, "image/png")

    def test_json_url(self) -> None:
        raw = _png_bytes()

        def fetch(url, headers, body):
            self.assertEqual(url, "https://example.test/cover.png")
            self.assertIsNone(body)
            return raw, "image/png"

        envelope = json.dumps({"success": True, "result": "https://example.test/cover.png"})
        got, media = decode_image_payload(envelope.encode("utf-8"), fetch=fetch)
        self.assertEqual(got, raw)
        self.assertEqual(media, "image/png")

    def test_driver_error(self) -> None:
        payload = json.dumps(
            {"success": False, "error": {"code": "insufficient_funds", "message": "upgrade"}}
        )
        with self.assertRaises(RuntimeError) as ctx:
            decode_image_payload(payload.encode("utf-8"))
        self.assertIn("upgrade", str(ctx.exception))


class GenerateTests(unittest.TestCase):
    def test_posts_driver_call(self) -> None:
        raw = _png_bytes()

        def fetch(url, headers, body):
            self.assertIn("/drivers/call", url)
            self.assertEqual(body["interface"], "puter-image-generation")
            self.assertEqual(body["driver"], "ai-image")
            self.assertEqual(body["method"], "generate")
            self.assertEqual(body["args"]["prompt"], "a cover")
            self.assertEqual(body["args"]["model"], DEFAULT_MODEL)
            self.assertEqual(body["args"]["aspect_ratio"], "3:4")
            self.assertEqual(body["args"]["quality"], "low")
            self.assertTrue(body["args"]["test_mode"])
            self.assertEqual(headers["Authorization"], "Bearer tok")
            return raw, "image/png"

        got, media = generate_puter_cover_bytes(
            prompt="a cover",
            token="tok",
            quality="low",
            test_mode=True,
            fetch=fetch,
        )
        self.assertEqual(got, raw)
        self.assertEqual(media, "image/png")


class ListTests(unittest.TestCase):
    def test_catalog_without_token(self) -> None:
        models = list_puter_models()
        ids = [m.id for m in models]
        self.assertIn(DEFAULT_MODEL, ids)
        self.assertIn("black-forest-labs/flux-schnell", ids)
        self.assertEqual(len(models), len(PUTER_MODELS))

    def test_live_list(self) -> None:
        def fetch(url, headers, body):
            self.assertEqual(body["method"], "list")
            return json.dumps(
                {"success": True, "result": ["openai/gpt-image-2", {"id": "x-ai/grok-imagine-image"}]}
            ).encode("utf-8"), "application/json"

        models = list_puter_models("tok", fetch=fetch)
        self.assertEqual([m.id for m in models], ["openai/gpt-image-2", "x-ai/grok-imagine-image"])


class CliTests(unittest.TestCase):
    def test_dry_run_needs_no_token(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            os.environ.pop("PUTER_AUTH_TOKEN", None)
            code = main(
                [
                    "cover-puter",
                    str(FIXTURES / "simple.md"),
                    "--dry-run",
                ]
            )
        self.assertEqual(code, 0)

    def test_list_models_without_token(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            os.environ.pop("PUTER_AUTH_TOKEN", None)
            code = main(["cover-puter", "--list-models"])
        self.assertEqual(code, 0)
