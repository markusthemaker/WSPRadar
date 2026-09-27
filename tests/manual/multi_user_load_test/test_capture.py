"""Captured-query integrity and failure handling; all provider calls are mocked."""

import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, Mock, patch

import pandas as pd

try:
    from . import capture
except ImportError:
    import capture


class CaptureTests(unittest.TestCase):
    def test_provider_selection_uses_explicit_enabled_key_and_preserves_default(self):
        primary = SimpleNamespace(key="wspr_live", enabled=True)
        secondary = SimpleNamespace(key="wd2", enabled=True)
        disabled = SimpleNamespace(key="wd1", enabled=False)
        providers = (primary, secondary, disabled)
        self.assertIs(capture.select_provider(providers), primary)
        self.assertIs(capture.select_provider(providers, "wd2"), secondary)
        for invalid_key in ("wd1", "unknown"):
            with self.subTest(provider=invalid_key), self.assertRaisesRegex(ValueError, "No enabled configured provider"):
                capture.select_provider(providers, invalid_key)

    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.directory = Path(temporary_directory.name)
        self.configuration = self.directory / "source.config"
        self.configuration.write_text('{"settings": {"purpose": "capture test"}}\n', encoding="utf-8")
        self.output = self.directory / "capture"
        self.query_plan = [{
            "analysis_id": "RX_PERFORMANCE", "variant": variant,
            "sql": f"SELECT '{variant}' FORMAT Parquet", "response_format": "parquet",
            "analysis_contract": {"analysis_kind": "opportunity", "is_sequential": False, "is_local_median": False},
        } for variant in ("strict", "legacy")]
        frame = pd.DataFrame({
            "time_slot": [100], "peer_sign": pd.Series(["K1ABC"], dtype="string"),
            "peer_grid": pd.Series(["FN31"], dtype="string"),
            "target_seen": [1], "external_seen": [1], "target_snr": [-10.0],
        })
        self.frames = {self.query_plan[0]["sql"]: frame.iloc[:0], self.query_plan[1]["sql"]: frame}
        self.raw_paths = {}
        for index, (sql_query, rows) in enumerate(self.frames.items()):
            raw_path = self.directory / f"raw-{index}.parquet"
            rows.to_parquet(raw_path, index=False)
            self.raw_paths[sql_query] = raw_path

    def capture_with_mock_provider(self, error=None):
        import config
        from config import app_config
        from core import data_engine, provider_dispatch
        from core.fetch_models import FetchResult

        provider = SimpleNamespace(key="wspr_live", url="https://example.invalid/", display_name="Test provider", enabled=True)
        lease = MagicMock()
        lease.__enter__.return_value = lease

        def fetch_query(sql_query, **_kwargs):
            return FetchResult(error=error) if error is not None else FetchResult(dataframe=self.frames[sql_query].copy())

        self.fetch_query = Mock(side_effect=fetch_query)
        with patch.object(capture, "_require_fresh_process"), \
                patch.object(capture, "build_query_plan", return_value=({}, {}, self.query_plan)), \
                patch.object(config, "CACHE_DIR", config.CACHE_DIR), \
                patch.object(app_config, "CACHE_DIR", app_config.CACHE_DIR), \
                patch.object(config, "WSPR_DATABASE_PROVIDERS", (provider,)), \
                patch.object(data_engine, "fetch_wspr_data", self.fetch_query), \
                patch.object(data_engine, "_query_cache_path", side_effect=lambda sql_query, *_args, **_kwargs: self.raw_paths[sql_query]), \
                patch.object(provider_dispatch.UPSTREAM_PROVIDER_DISPATCH, "acquire_run", return_value=lease):
            return capture.capture_queries(self.output, self.configuration)

    def write_manifest(self, manifest):
        (self.output / capture.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")

    def test_capture_copies_raw_bytes_and_loader_accepts_empty_strict_plus_populated_legacy(self):
        manifest = self.capture_with_mock_provider()
        query_paths, provenance = capture.load_query_capture(self.output, self.configuration, self.query_plan)
        self.assertEqual(provenance["query_result_rows"], 1)
        self.assertEqual([record["rows"] for record in manifest["queries"]], [0, 1])
        self.assertEqual(self.fetch_query.call_count, 2)
        for query in self.query_plan:
            sql_hash = capture._query_identity(query)[3]
            self.assertEqual(query_paths[sql_hash].read_bytes(), self.raw_paths[query["sql"]].read_bytes())
        self.assertFalse((self.output / f"{capture.MANIFEST_NAME}.pending").exists())
        with self.assertRaisesRegex(FileExistsError, "NEW"):
            capture.capture_queries(self.output, self.configuration)

    def test_provider_error_stops_without_publishing_a_completed_capture(self):
        from core.fetch_models import FetchError

        with self.assertRaisesRegex(RuntimeError, "result_row_limit_exceeded.*no retry"):
            self.capture_with_mock_provider(FetchError(code="result_row_limit_exceeded", message="Row limit exceeded"))
        self.assertEqual(self.fetch_query.call_count, 1)
        self.assertFalse((self.output / capture.MANIFEST_NAME).exists())
        diagnostic = json.loads((self.output / "capture_failure.json").read_text(encoding="utf-8"))
        self.assertEqual(diagnostic["code"], "result_row_limit_exceeded")
        self.assertEqual(diagnostic["provider"]["key"], "wspr_live")

    def test_provider_response_is_retained_with_a_bounded_size(self):
        from core.fetch_models import FetchError

        response_text = "ClickHouse exception: " + "x" * capture.MAX_ERROR_RESPONSE_CHARACTERS
        with self.assertRaisesRegex(RuntimeError, "http_error"):
            self.capture_with_mock_provider(FetchError(code="http_error", message="HTTP 500",
                                                      status_code=500, response_text=response_text))
        diagnostic = json.loads((self.output / "capture_failure.json").read_text(encoding="utf-8"))
        self.assertEqual(diagnostic["status_code"], 500)
        self.assertEqual(diagnostic["sql"], self.query_plan[0]["sql"])
        self.assertEqual(diagnostic["response_text"], response_text[:capture.MAX_ERROR_RESPONSE_CHARACTERS])

    def test_all_empty_variants_do_not_publish_a_completed_capture(self):
        self.frames = {sql_query: rows.iloc[:0] for sql_query, rows in self.frames.items()}
        for sql_query, rows in self.frames.items():
            rows.to_parquet(self.raw_paths[sql_query], index=False)
        with self.assertRaisesRegex(ValueError, "All strict/legacy query results were empty"):
            self.capture_with_mock_provider()
        self.assertFalse((self.output / capture.MANIFEST_NAME).exists())

    def test_missing_capture_has_an_actionable_preparation_error(self):
        with self.assertRaisesRegex(FileNotFoundError, "run capture.py once"):
            capture.load_query_capture(self.output, self.configuration, self.query_plan)

    def test_configuration_and_current_sql_must_match_exactly(self):
        self.capture_with_mock_provider()
        changed_configuration = self.directory / "changed.config"
        changed_configuration.write_bytes(self.configuration.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "configuration differs"):
            capture.load_query_capture(self.output, changed_configuration, self.query_plan)
        changed_plan = copy.deepcopy(self.query_plan)
        changed_plan[1]["sql"] += " "
        with self.assertRaisesRegex(ValueError, "query set differs"):
            capture.load_query_capture(self.output, self.configuration, changed_plan)

    def test_query_set_and_format_cannot_be_substituted(self):
        manifest = self.capture_with_mock_provider()
        for change in ("missing", "duplicate", "format"):
            with self.subTest(change=change):
                altered = copy.deepcopy(manifest)
                if change == "missing":
                    altered["queries"].pop()
                elif change == "duplicate":
                    altered["queries"].append(copy.deepcopy(altered["queries"][0]))
                else:
                    altered["queries"][0]["response_format"] = "csv"
                self.write_manifest(altered)
                with self.assertRaisesRegex(ValueError, "query set differs|missing required"):
                    capture.load_query_capture(self.output, self.configuration, self.query_plan)

    def test_modified_file_bytes_and_unsafe_paths_are_rejected(self):
        manifest = self.capture_with_mock_provider()
        result_record = manifest["queries"][1]["result_file"]
        result_path = self.output / result_record["path"]
        original = result_path.read_bytes()
        result_path.write_bytes(original + b"changed")
        with self.assertRaisesRegex(ValueError, "size/hash"):
            capture.load_query_capture(self.output, self.configuration, self.query_plan)
        result_path.write_bytes(original)
        for unsafe_name in ("../outside.parquet", "/outside.parquet", "C:/outside.parquet", "results\\outside.parquet"):
            with self.subTest(path=unsafe_name):
                altered = copy.deepcopy(manifest)
                altered["queries"][1]["result_file"]["path"] = unsafe_name
                self.write_manifest(altered)
                with self.assertRaisesRegex(ValueError, "Unsafe capture"):
                    capture.load_query_capture(self.output, self.configuration, self.query_plan)

    def test_manifest_rows_must_match_actual_footer_and_production_limit(self):
        from config import MAX_ANALYSIS_RESULT_ROWS

        manifest = self.capture_with_mock_provider()
        for wrong_rows in (2, MAX_ANALYSIS_RESULT_ROWS + 1, True):
            with self.subTest(rows=wrong_rows):
                altered = copy.deepcopy(manifest)
                altered["queries"][1]["rows"] = wrong_rows
                self.write_manifest(altered)
                with self.assertRaisesRegex(ValueError, "row count|row limit"):
                    capture.load_query_capture(self.output, self.configuration, self.query_plan)

    def test_missing_required_parquet_columns_are_rejected_even_with_new_hash(self):
        manifest = self.capture_with_mock_provider()
        record = manifest["queries"][1]
        result_path = self.output / record["result_file"]["path"]
        self.frames[self.query_plan[1]["sql"]].drop(columns=["target_seen"]).to_parquet(result_path, index=False)
        record["result_file"] = capture._file_record(result_path, self.output)
        self.write_manifest(manifest)
        with self.assertRaisesRegex(ValueError, "schema is invalid.*target_seen"):
            capture.load_query_capture(self.output, self.configuration, self.query_plan)


if __name__ == "__main__":
    unittest.main()
