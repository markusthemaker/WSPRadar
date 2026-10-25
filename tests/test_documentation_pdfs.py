"""Offline integrity and source-correspondence contracts for documentation PDFs."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import documentation_pdfs as downloads


class DocumentationPdfTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.manuals = {"en": "# English manual\r\nComplete content.\r\n", "de": "# Deutsche Anleitung\nVollständiger Inhalt.\n"}
        self.version = "0.99.9"
        self.manifest = {
            "schema_version": 1, "logo_sha256": "a" * 64,
            "renderer": {
                "source_sha256": {"docs/pdf_generator.py": "b" * 64, "i18n.py": "c" * 64},
                "dependencies": {"python": "3.12.10", "reportlab": "4.4.4"},
                "fonts_sha256": {"SourceSans3-Regular.ttf": "d" * 64},
            }, "files": {},
        }
        self.expected = {}
        for name, language in downloads.PDF_NAMES.items():
            payload = ("%PDF-1.4\nComplete " + language + " manual.\n%%EOF\n").encode()
            (self.root / name).write_bytes(payload)
            self.expected["assets/documentation/" + name] = payload
            record = {
                "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                "language": language,
                "manual_sha256": hashlib.sha256(self.manuals[language].encode()).hexdigest(),
                "app_version": self.version,
            }
            identity = {
                "language": language, "manual_sha256": record["manual_sha256"],
                "app_version": self.version, "logo_sha256": self.manifest["logo_sha256"],
                "renderer": self.manifest["renderer"],
            }
            record["render_key"] = hashlib.sha256((json.dumps(
                identity, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False,
            ) + "\n").encode()).hexdigest()
            self.manifest["files"][name] = record
        self.write_manifest()

    def write_manifest(self, manifest=None):
        (self.root / "manifest.json").write_text(
            json.dumps(self.manifest if manifest is None else manifest), encoding="utf-8",
        )

    def load(self, **kwargs):
        return downloads.documentation_pdf_files(
            self.root, kwargs.get("manuals", self.manuals), kwargs.get("app_version", self.version),
        )

    def test_publishes_exact_pdf_bytes_without_manifest_or_rendering_dependencies(self):
        self.assertEqual(self.load(), self.expected)

    def mixed_revision_manifest(self):
        """Refresh English while retaining the original German artifact and identity."""
        previous_identity = {key: deepcopy(self.manifest[key]) for key in ("logo_sha256", "renderer")}
        current_identity = deepcopy(previous_identity)
        current_identity["logo_sha256"] = "e" * 64
        current_identity["renderer"]["source_sha256"] = self.renderer_sources(full_catalog=True)
        current_identity["renderer"]["dependencies"]["reportlab"] = "5.0.0"
        current_identity["renderer"]["fonts_sha256"]["SourceSans3-Regular.ttf"] = "f" * 64
        manifest = {
            "schema_version": 2,
            "renderers": {"en": current_identity, "de": previous_identity},
            "files": deepcopy(self.manifest["files"]),
        }
        self.manuals["en"] = "# Reviewed English manual\nNew content.\n"
        payload = b"%PDF-1.4\nReviewed English manual with current renderer.\n%%EOF\n"
        name = "WSPRadar_Doc_EN.pdf"
        (self.root / name).write_bytes(payload)
        self.expected["assets/documentation/" + name] = payload
        record = manifest["files"][name]
        record.update(
            bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(),
            manual_sha256=hashlib.sha256(self.manuals["en"].encode("utf-8")).hexdigest(),
        )
        identity = {
            "language": "en", "manual_sha256": record["manual_sha256"],
            "app_version": self.version, **current_identity,
        }
        record["render_key"] = hashlib.sha256((json.dumps(
            identity, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False,
        ) + "\n").encode("utf-8")).hexdigest()
        return manifest

    def test_schema_two_publishes_new_english_and_byte_exact_legacy_german(self):
        original_german_record = deepcopy(self.manifest["files"]["WSPRadar_Doc_DE.pdf"])
        original_german_payload = (self.root / "WSPRadar_Doc_DE.pdf").read_bytes()
        original_english_payload = (self.root / "WSPRadar_Doc_EN.pdf").read_bytes()
        manifest = self.mixed_revision_manifest()
        self.write_manifest(manifest)

        output = self.load()
        self.assertEqual(output, self.expected)
        self.assertEqual(output["assets/documentation/WSPRadar_Doc_DE.pdf"], original_german_payload)
        self.assertEqual(manifest["files"]["WSPRadar_Doc_DE.pdf"], original_german_record)
        self.assertNotEqual(output["assets/documentation/WSPRadar_Doc_EN.pdf"], original_english_payload)
        self.assertIn("docs/pdf_generator.py", manifest["renderers"]["de"]["renderer"]["source_sha256"])
        self.assertIn("docs/manual/pdf_generator.py", manifest["renderers"]["en"]["renderer"]["source_sha256"])

    def test_schema_two_requires_exact_language_identity_inventory(self):
        baseline = self.mixed_revision_manifest()
        for kind in ("missing_en", "missing_de", "extra_language", "not_a_mapping", "extra_top_level", "missing_top_level", "boolean_schema", "unknown_schema"):
            with self.subTest(kind=kind):
                manifest = deepcopy(baseline)
                if kind.startswith("missing_") and kind != "missing_top_level":
                    del manifest["renderers"][kind.removeprefix("missing_")]
                elif kind == "extra_language":
                    manifest["renderers"]["fr"] = deepcopy(manifest["renderers"]["en"])
                elif kind == "not_a_mapping":
                    manifest["renderers"] = []
                elif kind == "extra_top_level":
                    manifest["renderer"] = deepcopy(manifest["renderers"]["en"]["renderer"])
                elif kind == "missing_top_level":
                    del manifest["renderers"]
                else:
                    manifest["schema_version"] = True if kind == "boolean_schema" else 3
                self.write_manifest(manifest)
                with self.assertRaisesRegex(ValueError, "Invalid documentation PDF manifest"):
                    self.load()

    def test_schema_two_validates_each_language_renderer_metadata(self):
        baseline = self.mixed_revision_manifest()
        for language in ("en", "de"):
            for kind in ("not_a_mapping", "missing_logo", "extra_identity_field", "logo_hash", "renderer_type", "source_inventory", "source_hash", "font_hash", "dependency_version"):
                with self.subTest(language=language, kind=kind):
                    manifest = deepcopy(baseline)
                    identity = manifest["renderers"][language]
                    if kind == "not_a_mapping":
                        manifest["renderers"][language] = None
                    elif kind == "missing_logo":
                        del identity["logo_sha256"]
                    elif kind == "extra_identity_field":
                        identity["unverified"] = True
                    elif kind == "logo_hash":
                        identity["logo_sha256"] = "invalid"
                    elif kind == "renderer_type":
                        identity["renderer"] = []
                    elif kind == "source_inventory":
                        identity["renderer"]["source_sha256"].pop("i18n.py")
                    elif kind == "source_hash":
                        identity["renderer"]["source_sha256"]["i18n.py"] = "invalid"
                    elif kind == "font_hash":
                        identity["renderer"]["fonts_sha256"]["SourceSans3-Regular.ttf"] = "invalid"
                    else:
                        identity["renderer"]["dependencies"]["python"] = None
                    self.write_manifest(manifest)
                    with self.assertRaisesRegex(ValueError, "Invalid documentation PDF renderer"):
                        self.load()

    def test_schema_two_render_keys_bind_each_pdf_to_its_own_identity(self):
        baseline = self.mixed_revision_manifest()
        for language in ("en", "de"):
            for kind in ("changed_logo", "changed_renderer", "other_language_identity", "changed_key"):
                with self.subTest(language=language, kind=kind):
                    manifest = deepcopy(baseline)
                    identity = manifest["renderers"][language]
                    if kind == "changed_logo":
                        identity["logo_sha256"] = "1" * 64
                    elif kind == "changed_renderer":
                        identity["renderer"]["dependencies"]["python"] = "3.13.0"
                    elif kind == "other_language_identity":
                        other = "de" if language == "en" else "en"
                        manifest["renderers"][language] = deepcopy(manifest["renderers"][other])
                    else:
                        manifest["files"][f"WSPRadar_Doc_{language.upper()}.pdf"]["render_key"] = "0" * 64
                    self.write_manifest(manifest)
                    with self.assertRaisesRegex(ValueError, "render identity mismatch"):
                        self.load()

    def test_schema_two_still_requires_exact_manuals_and_application_version(self):
        manifest = self.mixed_revision_manifest()
        self.write_manifest(manifest)
        for language in ("en", "de"):
            with self.subTest(language=language):
                with self.assertRaisesRegex(ValueError, "Stale documentation PDF"):
                    self.load(manuals={**self.manuals, language: self.manuals[language] + "Changed."})
        with self.assertRaisesRegex(ValueError, "Stale documentation PDF"):
            self.load(app_version="1.0.0")

    def test_schema_two_rejects_corruption_of_either_pdf(self):
        manifest = self.mixed_revision_manifest()
        self.write_manifest(manifest)
        for name in downloads.PDF_NAMES:
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b"corruption")
                    with self.assertRaisesRegex(ValueError, "hash mismatch"):
                        self.load()
                finally:
                    path.write_bytes(original)

    def renderer_sources(self, renderer_path="docs/manual/pdf_generator.py", *, full_catalog=False):
        names = {renderer_path, "i18n.py"}
        if full_catalog:
            names.update({
                "localization/__init__.py", "localization/sources.py",
                "localization/catalogs.py", "localization/key_order.py",
                "localization/common_en.py", "localization/common_de.py",
                "localization/inputs_en.py", "localization/inputs_de.py",
                "localization/results_en.py", "localization/results_de.py",
                "localization/figures_en.py", "localization/figures_de.py",
                "localization/inspector_en.py", "localization/inspector_de.py",
                "localization/exports_en.py", "localization/exports_de.py",
                "localization/guided_inputs_en.py", "localization/guided_inputs_de.py",
                "localization/result_guidance_en.py", "localization/result_guidance_de.py",
            })
        return {name: hashlib.sha256(name.encode()).hexdigest() for name in names}

    def write_renderer_sources(self, sources, *, refresh_render_keys=True):
        self.manifest["renderer"]["source_sha256"] = sources
        if refresh_render_keys:
            for record in self.manifest["files"].values():
                identity = {
                    "language": record["language"], "manual_sha256": record["manual_sha256"],
                    "app_version": self.version, "logo_sha256": self.manifest["logo_sha256"],
                    "renderer": self.manifest["renderer"],
                }
                record["render_key"] = hashlib.sha256((json.dumps(
                    identity, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False,
                ) + "\n").encode()).hexdigest()
        self.write_manifest()

    def test_legacy_and_relocated_renderer_inventories_preserve_pdf_payloads(self):
        for renderer_path, full_catalog in (
            ("docs/pdf_generator.py", False),
            ("docs/manual/pdf_generator.py", False),
            ("docs/manual/pdf_generator.py", True),
        ):
            with self.subTest(renderer_path=renderer_path, full_catalog=full_catalog):
                self.write_renderer_sources(self.renderer_sources(renderer_path, full_catalog=full_catalog))
                self.assertEqual(self.load(), self.expected)

    def test_current_renderer_inventory_rejects_each_missing_source(self):
        sources = self.renderer_sources(full_catalog=True)
        for missing in sources:
            with self.subTest(missing=missing):
                self.write_renderer_sources({name: digest for name, digest in sources.items() if name != missing})
                with self.assertRaisesRegex(ValueError, "Invalid documentation PDF renderer sources"):
                    self.load()

    def test_renderer_inventory_rejects_unknown_and_mixed_sources(self):
        sources = self.renderer_sources(full_catalog=True)
        invalid = {
            "arbitrary": {**sources, "unreviewed.py": "f" * 64},
            "unknown_catalog": {**sources, "localization/unknown_en.py": "f" * 64},
            "both_renderer_paths": {**sources, "docs/pdf_generator.py": "f" * 64},
            "partial_catalog": {**self.renderer_sources(), "localization/common_en.py": "f" * 64},
            "unsupported_combination": self.renderer_sources("docs/pdf_generator.py", full_catalog=True),
        }
        for label, inventory in invalid.items():
            with self.subTest(inventory=label):
                self.write_renderer_sources(inventory)
                with self.assertRaisesRegex(ValueError, "Invalid documentation PDF renderer sources"):
                    self.load()

    def test_relocated_renderer_identity_requires_recomputed_render_keys(self):
        self.write_renderer_sources(self.renderer_sources(full_catalog=True), refresh_render_keys=False)
        with self.assertRaisesRegex(ValueError, "render identity mismatch"):
            self.load()

    def test_manual_content_and_line_endings_are_exact_revision_inputs(self):
        for value in (self.manuals["en"] + "New content.", self.manuals["en"].replace("\r\n", "\n")):
            with self.subTest(manual=value):
                with self.assertRaisesRegex(ValueError, "Stale documentation PDF"):
                    self.load(manuals={**self.manuals, "en": value})

    def test_application_version_must_match_imported_version(self):
        with self.assertRaisesRegex(ValueError, "Stale documentation PDF"):
            self.load(app_version="1.0.0")

    def test_content_corruption_and_missing_pdf_signature_fail(self):
        name = "WSPRadar_Doc_EN.pdf"
        original = (self.root / name).read_bytes()
        (self.root / name).write_bytes(original + b"corruption")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.load()
        payload = b"Not a PDF"
        (self.root / name).write_bytes(payload)
        self.manifest["files"][name].update(bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "signature missing"):
            self.load()

    def test_expected_manifest_paths_cannot_be_replaced_or_extended(self):
        for path in ("../secret.pdf", "C:/absolute.pdf", "nested/file.pdf", "..\\secret.pdf"):
            with self.subTest(path=path):
                manifest = deepcopy(self.manifest)
                manifest["files"][path] = manifest["files"].pop("WSPRadar_Doc_EN.pdf")
                self.write_manifest(manifest)
                with self.assertRaisesRegex(ValueError, "Invalid documentation PDF manifest"):
                    self.load()

    def test_extra_or_missing_source_inventory_is_rejected(self):
        extra = self.root / "unreviewed.pdf"
        extra.write_bytes(b"%PDF-extra")
        with self.assertRaisesRegex(ValueError, "inventory"):
            self.load()
        extra.unlink()
        (self.root / "WSPRadar_Doc_EN.pdf").unlink()
        with self.assertRaisesRegex(ValueError, "inventory"):
            self.load()

    def test_schema_record_and_renderer_metadata_are_strict(self):
        for kind in ("schema", "byte_type", "language", "sha256", "renderer", "font", "version"):
            with self.subTest(kind=kind):
                manifest = deepcopy(self.manifest)
                record = manifest["files"]["WSPRadar_Doc_EN.pdf"]
                if kind == "schema":
                    manifest["schema_version"] = True
                elif kind == "byte_type":
                    record["bytes"] = True
                elif kind == "language":
                    record["language"] = "de"
                elif kind == "sha256":
                    record["sha256"] = "invalid"
                elif kind == "renderer":
                    manifest["renderer"]["source_sha256"].pop("i18n.py")
                elif kind == "font":
                    manifest["renderer"]["fonts_sha256"] = {}
                else:
                    manifest["renderer"]["dependencies"]["python"] = None
                self.write_manifest(manifest)
                with self.assertRaisesRegex(ValueError, "Invalid documentation PDF"):
                    self.load()

    def test_renderer_identity_change_requires_a_matching_render_key(self):
        self.manifest["renderer"]["dependencies"]["reportlab"] = "5.0.0"
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "render identity mismatch"):
            self.load()

    def test_directory_in_place_of_expected_pdf_is_rejected(self):
        pdf = self.root / "WSPRadar_Doc_EN.pdf"
        pdf.unlink()
        pdf.mkdir()
        with self.assertRaisesRegex(ValueError, "source type"):
            self.load()

    def test_reparse_points_and_symlinks_are_rejected_before_file_reads(self):
        original = Path.lstat
        for mode, attributes in ((stat.S_IFLNK, 0), (stat.S_IFREG, stat.FILE_ATTRIBUTE_REPARSE_POINT)):
            with self.subTest(mode=mode, attributes=attributes):
                def lstat(path):
                    if path == self.root / "WSPRadar_Doc_EN.pdf":
                        return SimpleNamespace(st_mode=mode, st_file_attributes=attributes)
                    return original(path)
                with patch.object(Path, "lstat", lstat):
                    with self.assertRaisesRegex(ValueError, "links and junctions"):
                        self.load()

    def test_linked_source_directory_or_parent_is_rejected(self):
        original = Path.lstat
        for linked in (self.root, self.root.parent):
            with self.subTest(path=linked):
                def lstat(path):
                    if path == linked:
                        return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
                    return original(path)
                with patch.object(Path, "lstat", lstat):
                    with self.assertRaisesRegex(ValueError, "links and junctions"):
                        self.load()


if __name__ == "__main__":
    unittest.main()
