"""Portable source identity and strict transfer-bundle file selection."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

HARNESS_DIRECTORY = Path(__file__).resolve().parent
if str(HARNESS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIRECTORY))

from make_bundle import build_bundle, collect_bundle_paths, source_digest, validated_source_path


class BundleTests(unittest.TestCase):
    def test_runner_verifies_extracted_snapshot_without_using_an_outer_checkout(self):
        import run
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            source = b"snapshot_source = True\n"
            (repository / "app.py").write_bytes(source)
            records = [{"path": "app.py", "sha256": hashlib.sha256(source).hexdigest()}]
            snapshot = {"files": records, "source_digest": source_digest(records),
                        "git_revision": "snapshot-revision", "dirty": True}
            (repository / "source_snapshot.json").write_text(json.dumps(snapshot), encoding="utf-8")
            with patch.object(run, "REPOSITORY", repository), patch(
                "make_bundle.inspect_checkout", side_effect=AssertionError("Must not inspect enclosing checkout"),
            ):
                versions = run.version_record()
            self.assertTrue(versions["snapshot_verified"])
            self.assertEqual(versions["source_digest"], snapshot["source_digest"])
            self.assertEqual(versions["git_revision"], "snapshot-revision")

    def test_runner_rejects_modified_extracted_source(self):
        import run
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            (repository / "app.py").write_bytes(b"changed\n")
            records = [{"path": "app.py", "sha256": hashlib.sha256(b"original\n").hexdigest()}]
            snapshot = {"files": records, "source_digest": source_digest(records),
                        "git_revision": "snapshot-revision", "dirty": True}
            (repository / "source_snapshot.json").write_text(json.dumps(snapshot), encoding="utf-8")
            with patch.object(run, "REPOSITORY", repository):
                with self.assertRaisesRegex(ValueError, "Extracted source differs"):
                    run.version_record()

    def test_bundle_snapshot_hashes_the_exact_current_file_contents(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            source_bytes = b"working_tree_change = True\n"
            (repository / "app.py").write_bytes(source_bytes)
            inventory = {"git_revision": "example-revision", "dirty": True,
                         "files": ["app.py"], "excluded_files": [],
                         "total_source_bytes": len(source_bytes)}
            with patch("make_bundle.inspect_checkout", return_value=inventory):
                bundle = build_bundle(repository, Path(".test/transfer.zip"))
            with zipfile.ZipFile(bundle["path"]) as archive:
                self.assertEqual(set(archive.namelist()), {"app.py", "source_snapshot.json"})
                self.assertEqual(archive.read("app.py"), source_bytes)
                snapshot = json.loads(archive.read("source_snapshot.json"))
            self.assertTrue(snapshot["dirty"])
            self.assertEqual(snapshot["files"], [{"path": "app.py", "sha256": hashlib.sha256(source_bytes).hexdigest()}])
            self.assertEqual(snapshot["source_digest"], source_digest(snapshot["files"]))

    def test_edit_during_packaging_prevents_partial_bundle_publication(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            source_path = repository / "app.py"
            source_path.write_bytes(b"before\n")
            inventory = {"git_revision": "example-revision", "dirty": True,
                         "files": ["app.py"], "excluded_files": [], "total_source_bytes": 7}

            def edit_before_final_validation(records):
                source_path.write_bytes(b"after\n")
                return source_digest(records)

            with patch("make_bundle.inspect_checkout", return_value=inventory), patch(
                "make_bundle.source_digest", side_effect=edit_before_final_validation,
            ):
                with self.assertRaisesRegex(RuntimeError, "Source changed"):
                    build_bundle(repository, Path(".test/transfer.zip"))
            self.assertFalse((repository / ".test/transfer.zip").exists())
            self.assertEqual(list((repository / ".test").iterdir()), [])

    def test_inventory_excludes_reports_secrets_and_deleted_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            for name in ("app.py", ".streamlit/secrets.toml", "output/plot.png", "config/example.config"):
                path = repository / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(name, encoding="utf-8")
            included, excluded = collect_bundle_paths(repository, [
                "app.py", ".streamlit/secrets.toml", "output/plot.png", "config/example.config", "deleted.py",
            ])
            self.assertEqual(included, ["app.py", "config/example.config"])
            self.assertEqual(set(excluded), {".streamlit/secrets.toml", "output/plot.png", "deleted.py"})

    def test_inventory_rejects_traversal_and_unapproved_harness_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            with self.assertRaises(ValueError):
                collect_bundle_paths(repository, ["../outside.py"])
            harness = repository / "tests/manual/multi_user_load_test"
            harness.mkdir(parents=True)
            (harness / "private-notes.txt").write_text("must not upload", encoding="utf-8")
            with self.assertRaises(ValueError):
                collect_bundle_paths(repository, [])

    def test_inventory_preserves_unstaged_script_moves_without_adding_neighbors(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            internal_directory = repository / "scripts/internal"
            internal_directory.mkdir(parents=True)
            moved_script = internal_directory / "build_example.py"
            moved_script.write_text("retained_builder = True\n", encoding="utf-8")
            (internal_directory / "private_helper.py").write_text("private = True\n", encoding="utf-8")
            included, excluded = collect_bundle_paths(repository, ["scripts/build_example.py"])
            self.assertEqual(included, ["scripts/internal/build_example.py"])
            self.assertEqual(excluded, ["scripts/build_example.py"])

    def test_inventory_does_not_treat_a_second_existing_script_as_a_move(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            internal_directory = repository / "scripts/internal"
            internal_directory.mkdir(parents=True)
            for script in (repository / "scripts/example.py", internal_directory / "example.py"):
                script.write_text("example = True\n", encoding="utf-8")
            included, excluded = collect_bundle_paths(repository, ["scripts/example.py"])
            self.assertEqual(included, ["scripts/example.py"])
            self.assertEqual(excluded, [])

    def test_inventory_includes_the_linked_load_test_history(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            history = repository / "tests/manual/multi_user_load_test/HISTORY.md"
            history.parent.mkdir(parents=True)
            history.write_text("# Historical diagnostics\n", encoding="utf-8")
            included, excluded = collect_bundle_paths(repository, [])
            self.assertEqual(included, ["tests/manual/multi_user_load_test/HISTORY.md"])
            self.assertEqual(excluded, [])

    def test_inventory_includes_approved_guides_without_private_notes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            approved_guides = [
                "scripts/README.md",
                "docs/verification-history.md",
                "docs/relocation-ledgers/engineering-verification-history.md",
                "config/demos_backlog/README.md",
            ]
            for name in [*approved_guides, "docs/private-notes.md"]:
                guide = repository / name
                guide.parent.mkdir(parents=True, exist_ok=True)
                guide.write_text("# Guide\n", encoding="utf-8")
            included, excluded = collect_bundle_paths(repository, [])
            self.assertEqual(included, sorted(approved_guides))
            self.assertEqual(excluded, [])

    def test_source_digest_is_ordered_portable_and_excludes_snapshot_and_images(self):
        records = [
            {"path": "ui\\panel.py", "sha256": "b"},
            {"path": "photo.png", "sha256": "excluded"},
            {"path": "source_snapshot.json", "sha256": "self-reference"},
            {"path": "app.py", "sha256": "a"},
        ]
        expected = hashlib.sha256(b"app.py:a\nui/panel.py:b\n").hexdigest()
        self.assertEqual(source_digest(records), expected)

    def test_symlink_is_rejected_even_when_it_targets_an_internal_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            (repository / "real.py").write_text("value = 1\n", encoding="utf-8")
            try:
                (repository / "link.py").symlink_to(repository / "real.py")
            except OSError as error:
                self.skipTest(f"Symlink creation is unavailable on this host: {error}")
            with self.assertRaises(ValueError):
                validated_source_path(repository, "link.py")


if __name__ == "__main__":
    unittest.main()
