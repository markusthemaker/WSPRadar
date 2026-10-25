"""Contracts for source-bounded, reproducible browser asset preparation."""

from copy import deepcopy
from io import BytesIO
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from scripts import browser_assets


class BrowserAssetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.assets = self.source / "assets"
        self.assets.mkdir(parents=True)
        self.cache = self.root / "cache"
        self.original = Image.new("RGB", (8, 4))
        self.original.putdata([(x * 20, y * 60, (x + y) * 15) for y in range(4) for x in range(8)])
        self.original.save(self.assets / "original.png")
        source_bytes = (self.assets / "original.png").read_bytes()
        preview = self.original.resize((4, 2), Image.Resampling.LANCZOS)
        encoded = BytesIO()
        preview.save(encoded, "WEBP", lossless=True, quality=100, method=4, exact=True)
        self.expected = encoded.getvalue()
        self.record = {
            "path": "preview.webp",
            **browser_assets.signature(self.expected),
            "recipe": {
                "kind": "image", "source_path": "assets/original.png",
                "source_bytes": len(source_bytes),
                "source_sha256": browser_assets.signature(source_bytes)["sha256"],
                "width": 4, "height": 2, "format": "WEBP",
                "lossless": True, "quality": 100, "method": 4, "exact": True,
            },
        }

    def materialize(self, record=None, **kwargs):
        return browser_assets.resource_payload(self.assets, {"files": [self.record if record is None else record]}, source_root=self.source, cache_root=self.cache, **kwargs)

    def test_lossless_derivative_and_verified_cache_are_equivalent(self):
        first = self.materialize()
        with Image.open(BytesIO(first["preview.webp"])) as preview:
            self.assertEqual(preview.convert("RGB").tobytes(), self.original.resize((4, 2), Image.Resampling.LANCZOS).tobytes())
        with patch.object(browser_assets, "encode_recipe", side_effect=AssertionError("cache was not reused")):
            self.assertEqual(self.materialize(), first)
        self.assertEqual(self.materialize(rebuild=True), first)

    def test_cached_output_does_not_bypass_source_fingerprint(self):
        self.materialize()
        (self.assets / "original.png").write_bytes(b"changed source")
        with patch.object(browser_assets, "encode_recipe", side_effect=AssertionError("invalid input reached encoder")):
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                self.materialize()

    def test_corrupt_cache_is_regenerated_and_reverified(self):
        expected = self.materialize()
        cache_file, = self.cache.iterdir()
        cache_file.write_bytes(b"incomplete cached output")
        self.assertEqual(self.materialize(), expected)
        self.assertEqual(cache_file.read_bytes(), self.expected)

    def test_recipe_cannot_upscale_or_change_aspect_ratio(self):
        for width, height in ((16, 8), (4, 3), (True, 2)):
            with self.subTest(width=width, height=height):
                record = deepcopy(self.record)
                record["recipe"].update(width=width, height=height)
                with self.assertRaisesRegex(ValueError, "dimensions|aspect ratio"):
                    self.materialize(record)

    def test_recipe_source_and_published_path_cannot_escape_their_roots(self):
        for path in ("../secret.png", "/absolute.png", "C:/absolute.png", "..\\secret.png"):
            for field in ("source", "output"):
                with self.subTest(path=path, field=field):
                    record = deepcopy(self.record)
                    if field == "source":
                        record["recipe"]["source_path"] = path
                    else:
                        record["path"] = path
                    with self.assertRaisesRegex(ValueError, "asset path"):
                        self.materialize(record)

    def test_archived_master_requires_bounded_source_and_matching_hash(self):
        master = self.source / "archive" / "approved.webp"
        master.parent.mkdir()
        master.write_bytes(self.expected)
        record = {"path": "preview.webp", "source_path": "archive/approved.webp", **browser_assets.signature(self.expected)}
        self.assertEqual(self.materialize(record)["preview.webp"], self.expected)
        master.write_bytes(b"unreviewed replacement")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.materialize(record)
        record["source_path"] = "../outside.webp"
        with self.assertRaisesRegex(ValueError, "asset path"):
            self.materialize(record)

    def test_encoding_mismatch_cannot_enter_cache(self):
        with patch.object(browser_assets, "encode_recipe", return_value=b"different encoding"):
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                self.materialize()
        self.assertFalse(self.cache.exists())

    def test_duplicate_public_paths_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            browser_assets.resource_payload(self.assets, {"files": [self.record, self.record]}, source_root=self.source, cache_root=self.cache)


class LandingPngMasterTests(unittest.TestCase):
    def test_png_fallbacks_keep_reviewed_bytes_without_an_encoder_or_cache(self):
        asset_root = browser_assets.SOURCE_ROOT / "assets" / "landing"
        manifest = json.loads((asset_root / "manifest.json").read_text(encoding="utf-8"))
        fallbacks = [manifest[name]["fallback"] for name in ("hero", "logo", "network")]
        records_by_path = {record["path"]: record for record in manifest["files"]}
        records = [records_by_path[fallback["path"]] for fallback in fallbacks]

        for record in records:
            self.assertNotIn("recipe", record)
            self.assertTrue(record["source_path"].startswith("assets/browser-assets/landing/"))
            retained = record["retained_recipe"]
            self.assertEqual(retained["format"], "PNG")
            original = browser_assets.bounded_path(browser_assets.SOURCE_ROOT, retained["source_path"])
            browser_assets.verify(original.read_bytes(), {
                "bytes": retained["source_bytes"], "sha256": retained["source_sha256"],
            }, retained["source_path"])

        with tempfile.TemporaryDirectory() as temporary:
            cache = Path(temporary) / "empty-cache"
            with patch.object(browser_assets, "encode_recipe", side_effect=AssertionError("PNG master was re-encoded")):
                payload = browser_assets.resource_payload(asset_root, {"files": records}, cache_root=cache, rebuild=True)
            self.assertFalse(cache.exists())
        self.assertEqual(set(payload), {fallback["path"] for fallback in fallbacks})
        for fallback in fallbacks:
            browser_assets.verify(payload[fallback["path"]], fallback, fallback["path"])


if __name__ == "__main__":
    unittest.main()
