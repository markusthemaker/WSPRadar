"""Keep the optional live SQL comparison bounded and outside routine networking."""

import json
from types import SimpleNamespace

import pandas as pd
import pytest

from scripts.internal import verify_milazzo_clickhouse as checker


def _query_rows():
    """Supply two distinct peer-cycle rows, including missing successful SNR."""
    return pd.DataFrame({
        "time_slot": [10773059, 10773060],
        "peer_sign": ["VE6PDQ", "N7NB"],
        "peer_grid": ["DO34ir", "CN87ur"],
        "peer_lat": [54.729000091552734, 47.729000091552734],
        "peer_lon": [-113.29199981689453, -122.29199981689453],
        "target_seen": [1, 0], "external_seen": [0, 1],
        "target_snr": [-23.0, float("nan")],
    })


def test_query_comparison_preserves_source_precision_and_ignores_row_order():
    """Float32 coordinate serialization must not invent a live mismatch."""
    expected = _query_rows()
    actual = expected.iloc[::-1].copy()
    actual["peer_lat"] = [47.729, 54.729]
    actual["peer_lon"] = [-122.292, -113.292]
    actual["target_seen"] = actual.target_seen.astype("uint8")
    checker.compare_query_rows(actual, expected)


@pytest.mark.parametrize("mutation", [
    "snr", "flag", "missing_row", "duplicate", "identity", "missing_column", "unknown_as_zero",
])
def test_query_comparison_rejects_scientific_or_population_drift(mutation):
    """Matching totals must not hide changed identities, nulls or scientific values."""
    expected = _query_rows()
    actual = expected.copy()
    if mutation == "snr":
        actual.loc[0, "target_snr"] += 1
    elif mutation == "flag":
        actual.loc[0, "target_seen"] = 0
    elif mutation == "missing_row":
        actual = actual.iloc[:1]
    elif mutation == "duplicate":
        actual = pd.concat([actual.iloc[:1], actual.iloc[:1]], ignore_index=True)
    elif mutation == "identity":
        actual.loc[0, "peer_grid"] = "DO34is"
    elif mutation == "missing_column":
        actual = actual.drop(columns="external_seen")
    else:
        actual.loc[1, "target_snr"] = 0
    with pytest.raises(AssertionError):
        checker.compare_query_rows(actual, expected)


def _install_offline_plan(monkeypatch, fixture_directory):
    """Replace scientific preflight only in command-orchestration unit tests."""
    fixture_directory.mkdir()
    for filename in (
        "manifest.json", "approval.json", "reviewed_expectations.json",
        "network_source.parquet", "performance.config", "benchmark_source.csv",
        "benchmark.config", "benchmark_expected_native_units.csv",
        "benchmark_native_sql_capture.csv", "benchmark_native_capture.sql",
    ):
        (fixture_directory / filename).write_text("unit-test provenance", encoding="utf-8")
    monkeypatch.setattr(checker, "FIXTURE_DIRECTORY", fixture_directory)
    plan = [
        (name, "SELECT '" + name + "' FORMAT CSVWithNames", _query_rows())
        for name in ("performance_strict", "performance_fallback", "benchmark_strict", "benchmark_fallback")
    ]
    monkeypatch.setattr(checker, "build_query_plan", lambda directory: plan)
    return plan


def test_dry_run_never_requests_network_or_reports_live_success(monkeypatch, tmp_path):
    """The explicit planning mode writes provenance without becoming a live pass."""
    _install_offline_plan(monkeypatch, tmp_path / "reference")

    def reject_live_request(*args):
        pytest.fail("A dry run attempted a live provider request")

    monkeypatch.setattr(checker, "fetch_live_query", reject_live_request)
    output_directory = tmp_path / "planned"
    assert checker.main(["--dry-run", "--output-directory", str(output_directory)]) == 0
    report = json.loads((output_directory / "report.json").read_text())
    assert report["status"] == "dry_run_complete_not_live_verified"
    assert len(report["queries"]) == 4
    assert all(query["status"] == "planned" for query in report["queries"])
    assert len(list(output_directory.glob("*.sql"))) == 4


@pytest.mark.parametrize("outcome", ["match", "mismatch", "unavailable"])
def test_explicit_provider_check_reports_failures_without_refreshing_evidence(
    monkeypatch, tmp_path, outcome,
):
    """Mock transport proves bounded one-provider calls and nonzero failed checks."""
    fixture_directory = tmp_path / "reference"
    _install_offline_plan(monkeypatch, fixture_directory)
    before = {path.name: path.read_bytes() for path in fixture_directory.iterdir()}
    requests = []

    def controlled_request(query, provider):
        requests.append((query, provider.key))
        if outcome == "unavailable":
            raise TimeoutError("bounded test timeout")
        actual = _query_rows()
        if outcome == "mismatch":
            actual.loc[0, "target_snr"] += 1
        return actual, {"http_status": 200, "response_bytes": 100}

    monkeypatch.setattr(checker, "fetch_live_query", controlled_request)
    output_directory = tmp_path / outcome
    exit_code = checker.main(["--provider", "wspr_live", "--output-directory", str(output_directory)])
    report = json.loads((output_directory / "report.json").read_text())
    assert exit_code == (0 if outcome == "match" else 1)
    assert report["status"] == {
        "match": "live_outputs_match_frozen_reference",
        "mismatch": "mismatch_requires_investigation",
        "unavailable": "failed",
    }[outcome]
    assert len(requests) == (1 if outcome == "unavailable" else 4)
    assert {provider for _, provider in requests} == {"wspr_live"}
    assert before == {path.name: path.read_bytes() for path in fixture_directory.iterdir()}


@pytest.mark.parametrize("analysis", ["performance", "benchmark"])
def test_selected_analysis_queries_only_requested_scope_and_reports_partial_coverage(
    monkeypatch, tmp_path, analysis,
):
    """A two-query provider success must not imply both analyses were checked."""
    _install_offline_plan(monkeypatch, tmp_path / "reference")
    requested_queries = []

    def matching_request(query, provider):
        requested_queries.append(query)
        return _query_rows(), {"http_status": 200, "response_bytes": 100}

    monkeypatch.setattr(checker, "fetch_live_query", matching_request)
    output_directory = tmp_path / analysis
    assert checker.main([
        "--analysis", analysis, "--output-directory", str(output_directory),
    ]) == 0
    report = json.loads((output_directory / "report.json").read_text())
    expected_names = [analysis + "_strict", analysis + "_fallback"]
    assert report["requested_analysis"] == analysis
    assert report["status"] == "live_requested_scope_matches_frozen_reference"
    assert report["matched_requested_scope"] == expected_names
    assert [query["name"] for query in report["queries"]] == expected_names
    assert report["request_policy"]["maximum_requests"] == 2
    assert len(requested_queries) == 2
    assert all(analysis + "_" in query for query in requested_queries)
    assert {path.stem for path in output_directory.glob("*.sql")} == set(expected_names)


def test_live_transport_rejects_non_read_only_query_before_opening_session(monkeypatch):
    """The occasional verifier cannot submit writes or multiple statements."""
    def reject_session():
        pytest.fail("Invalid SQL reached the network boundary")

    monkeypatch.setattr(checker.requests, "Session", reject_session)
    provider = SimpleNamespace(url="https://db1.wspr.live/")
    for query in ("DROP TABLE wspr.rx FORMAT CSVWithNames", "SELECT 1; SELECT 2 FORMAT CSVWithNames"):
        with pytest.raises(ValueError, match="read-only"):
            checker.fetch_live_query(query, provider)


@pytest.mark.parametrize("should_hit_limit", [False, True])
def test_http_failure_preserves_bounded_provider_diagnostics_without_retry(
    monkeypatch, tmp_path, should_hit_limit,
):
    """HTTP failures retain actionable text and stop reading at the byte cap."""
    _install_offline_plan(monkeypatch, tmp_path / "reference")
    response_body = b"Code: 241. MEMORY_LIMIT_EXCEEDED. Diagnostic from provider."
    if should_hit_limit:
        response_body += b"x" * checker.MAXIMUM_ERROR_BODY_BYTES
    request_calls = []
    consumed_chunks = []

    class ErrorResponse:
        status_code = 500
        encoding = "utf-8"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def iter_content(self, chunk_size):
            consumed_chunks.append(chunk_size)
            yield response_body
            if should_hit_limit:
                pytest.fail("HTTP error diagnostics read beyond their capture limit")

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url, **kwargs):
            request_calls.append((url, kwargs))
            return ErrorResponse()

    monkeypatch.setattr(checker.requests, "Session", FakeSession)
    output_directory = tmp_path / "http_failure"
    assert checker.main(["--output-directory", str(output_directory)]) == 1
    report = json.loads((output_directory / "report.json").read_text())
    failed_query = report["queries"][0]
    assert report["status"] == "failed"
    assert failed_query["status"] == "request_failed"
    assert failed_query["http_status"] == 500
    assert failed_query["error_type"] == "ProviderQueryError"
    assert "MEMORY_LIMIT_EXCEEDED" in failed_query["error_body"]
    assert failed_query["error_body_bytes"] == min(len(response_body), checker.MAXIMUM_ERROR_BODY_BYTES)
    assert failed_query["error_body_limit_reached"] is should_hit_limit
    assert len(failed_query["error_body"].encode("utf-8")) <= checker.MAXIMUM_ERROR_BODY_BYTES
    assert len(request_calls) == 1
    assert request_calls[0][1]["allow_redirects"] is False
    assert consumed_chunks == [1024]
    assert all(query["status"] == "planned" for query in report["queries"][1:])


def test_http_error_capture_respects_existing_request_deadline(monkeypatch):
    """An exhausted request budget cannot start another error-body read."""
    class ExpiredResponse:
        status_code = 500
        encoding = "utf-8"

        def iter_content(self, chunk_size):
            pytest.fail("HTTP error body was read after its request deadline")
            yield b"unreachable"

    monkeypatch.setattr(checker.time, "monotonic", lambda: 100.0)
    metadata = checker.capture_http_error(ExpiredResponse(), deadline=90.0, started_at=20.0)
    assert metadata["http_status"] == 500
    assert metadata["error_body"] == ""
    assert metadata["error_body_bytes"] == 0
    assert metadata["error_body_deadline_reached"] is True


@pytest.mark.parametrize("change_scientific_value", [False, True])
def test_native_distance_reference_cannot_replace_scientific_expectations(
    tmp_path, change_scientific_value,
):
    """Only the auxiliary native distance may differ from the verified adapter."""
    expected = _query_rows()
    expected["best_ref_dist"] = [21220.9, 0.0]
    captured = expected.copy()
    captured.loc[0, "best_ref_dist"] = 21187.357020515254
    if change_scientific_value:
        captured.loc[0, "target_snr"] += 1
    outside_window = captured.iloc[:1].copy()
    outside_window["time_slot"] = 0
    pd.concat([captured, outside_window]).to_csv(
        tmp_path / "benchmark_native_sql_capture.csv", index=False, na_rep="\\N",
    )
    replay = SimpleNamespace(sql_rows=expected, configuration={
        "start_utc": "2010-12-19T12:00:00Z", "end_utc": "2010-12-20T20:00:00Z",
    })
    if change_scientific_value:
        with pytest.raises(AssertionError):
            checker.benchmark_native_expected(replay, tmp_path)
    else:
        native_expected = checker.benchmark_native_expected(replay, tmp_path)
        assert len(native_expected) == len(expected)
        checker.compare_query_rows(native_expected, captured)
        changed_distance = native_expected.copy()
        changed_distance.loc[0, "best_ref_dist"] += 1
        with pytest.raises(AssertionError):
            checker.compare_query_rows(changed_distance, native_expected)
