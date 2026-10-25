"""Page-source contracts: exact text preservation and explicit bounded lookup."""

import json
from pathlib import Path
import tempfile
import unittest

from scripts.page_content import load_catalog, read_text_blocks


class PageContentTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.pages = self.root / "pages"
        self.pages.mkdir()
        self.page = self.pages / "home.en.md"
        self.catalog = self.root / "catalog.json"

    def write_catalog(self, value):
        self.catalog.write_text(json.dumps(value), encoding="utf-8")

    def test_exact_text_and_nested_catalog_structure_are_preserved(self):
        prose = "  **Signal quality**\n\nA <strong>native</strong> figure: 1\u202f234.  "
        self.page.write_text("<!-- text: intro -->\n" + prose + "\n<!-- /text -->\n", encoding="utf-8")
        self.write_catalog({"items": [{"$text": "home.en.md#intro"}, 3, True], "id": "stable"})
        self.assertEqual(load_catalog(self.catalog, self.pages), {"items": [prose, 3, True], "id": "stable"})

    def test_duplicate_and_unplaced_content_fail_instead_of_disappearing(self):
        block = "<!-- text: intro -->\nText\n<!-- /text -->\n"
        for source in (block + block, "Lost introduction\n" + block, block + "Lost conclusion"):
            with self.subTest(source=source):
                self.page.write_text(source, encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_text_blocks(self.page)

    def test_missing_and_unsafe_references_are_rejected(self):
        self.page.write_text("<!-- text: intro -->\nText\n<!-- /text -->\n", encoding="utf-8")
        for reference in ("../outside.md#intro", "/outside.md#intro", "C:/outside.md#intro", "home.en.md#missing", "home.en.md", "home.en.md#"):
            with self.subTest(reference=reference):
                self.write_catalog({"$text": reference})
                with self.assertRaises(ValueError):
                    load_catalog(self.catalog, self.pages)

    def test_text_references_reject_ambiguous_extra_fields(self):
        self.write_catalog({"$text": "home.en.md#intro", "fallback": "Hidden copy"})
        with self.assertRaises(ValueError):
            load_catalog(self.catalog, self.pages)


if __name__ == "__main__":
    unittest.main()
