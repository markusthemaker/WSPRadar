"""Ownership and compatibility contracts for immutable completed-run metadata."""

from dataclasses import FrozenInstanceError
import json

import pytest

from core.analysis_plan import DECODE_FILTER_LEGACY, DECODE_FILTER_STRICT
from core.completed_run import (
    COMPLETED_MAP_NO_DATA,
    COMPLETED_PREPARED_NO_DATA,
    COMPLETED_RENDERABLE,
    COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
    CompletedAnalysis,
    CompletedAnalysisIdentity,
    CompletedQueryFetch,
    CompletedRun,
)
from core.fetch_models import DatabaseSource, FetchSource
from core.result_diagnostics import NO_SOURCE_ROWS, ResultDiagnostic
from ui.result_state import (
    COMPLETED_RUN_SNAPSHOT_KEY,
    get_completed_run_snapshot,
    publish_completed_run_snapshot,
)


def _completed_snapshot():
    """Represent an empty, source-pinned Benchmark with historical fallback."""
    return {
        "schema_version": COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
        "map_data_schema_version": 1,
        "run_id": 42,
        "request_fingerprint": "request-fingerprint",
        "analysis_plan_fingerprint": "plan-fingerprint",
        "database_source": DatabaseSource.WD2.value,
        "analyses": ({
            "analysis": {
                "id": "RX_COMPARE",
                "analysis_kind": "comparison",
                "is_compare": True,
                "is_sequential": False,
                "absolute_method_version": None,
            },
            "outcome": COMPLETED_PREPARED_NO_DATA,
            "evidence_path": None,
            "station_rows_path": None,
            "segment_rows_path": None,
            "selected_decode_filter_mode": DECODE_FILTER_LEGACY,
            "query_fetches": (
                {
                    "decode_filter_mode": DECODE_FILTER_STRICT,
                    "elapsed_seconds": 0.12,
                    "delivery_source": FetchSource.WD2.value,
                },
                {
                    "decode_filter_mode": DECODE_FILTER_LEGACY,
                    "elapsed_seconds": 0.03,
                    "delivery_source": FetchSource.MEMORY_CACHE.value,
                },
            ),
            "diagnostic": ResultDiagnostic.create(
                NO_SOURCE_ROWS, measured_counts={"source_row_count": 0},
            ).to_dict(),
        },),
    }


@pytest.mark.parametrize("outcome", [
    COMPLETED_PREPARED_NO_DATA, COMPLETED_MAP_NO_DATA, COMPLETED_RENDERABLE,
])
def test_schema_two_codec_preserves_outcomes_paths_and_query_provenance(outcome):
    """Retain the published dictionary shape, including nullable diagnostics."""
    snapshot = _completed_snapshot()
    analysis_snapshot = snapshot["analyses"][0]
    analysis_snapshot["outcome"] = outcome
    if outcome != COMPLETED_PREPARED_NO_DATA:
        analysis_snapshot["evidence_path"] = "artifacts/spots_RX_COMPARE.parquet"
        analysis_snapshot["diagnostic"] = None
    if outcome == COMPLETED_RENDERABLE:
        analysis_snapshot["station_rows_path"] = "artifacts/map_stations_RX_COMPARE.parquet"
        analysis_snapshot["segment_rows_path"] = "artifacts/map_segments_RX_COMPARE.parquet"

    completed_run = CompletedRun.from_dict(snapshot)

    assert completed_run.to_dict() == snapshot
    assert CompletedRun.from_dict(completed_run.to_dict()) == completed_run
    assert CompletedRun.from_dict(json.loads(json.dumps(snapshot))) == completed_run
    assert completed_run.analyses[0].selected_decode_filter_mode == DECODE_FILTER_LEGACY
    assert tuple(fetch.delivery_source for fetch in completed_run.analyses[0].query_fetches) == (
        FetchSource.WD2.value, FetchSource.MEMORY_CACHE.value,
    )


def test_publication_isolates_dictionary_inputs_and_serialized_outputs():
    """Caller edits cannot rewrite completed provenance after publication."""
    session_state = {}
    snapshot = _completed_snapshot()
    publish_completed_run_snapshot(session_state, snapshot)
    completed_run = get_completed_run_snapshot(session_state)
    expected_snapshot = completed_run.to_dict()

    snapshot["analyses"][0]["query_fetches"][0]["delivery_source"] = "changed by caller"
    snapshot["analyses"][0]["diagnostic"]["measured_counts"]["source_row_count"] = 99
    serialized_snapshot = completed_run.to_dict()
    serialized_snapshot["analyses"][0]["analysis"]["id"] = "changed by reader"
    serialized_snapshot["analyses"][0]["diagnostic"]["measured_counts"]["source_row_count"] = 88

    assert get_completed_run_snapshot(session_state) is completed_run
    assert completed_run.to_dict() == expected_snapshot


def test_direct_records_own_mutable_collections_and_diagnostic_inputs():
    """Typed publication retains no mutable aliases from constructor inputs."""
    query_fetches = [CompletedQueryFetch(
        decode_filter_mode=DECODE_FILTER_STRICT,
        elapsed_seconds=0.2,
        delivery_source=FetchSource.DISK_CACHE.value,
    )]
    diagnostic_counts = [["source_row_count", 0]]
    diagnostic = ResultDiagnostic(
        reason=NO_SOURCE_ROWS,
        applied_thresholds=[],
        measured_counts=diagnostic_counts,
    )
    completed_analysis = CompletedAnalysis(
        analysis=CompletedAnalysisIdentity.from_dict(_completed_snapshot()["analyses"][0]["analysis"]),
        outcome=COMPLETED_PREPARED_NO_DATA,
        evidence_path=None,
        station_rows_path=None,
        segment_rows_path=None,
        selected_decode_filter_mode=DECODE_FILTER_STRICT,
        query_fetches=query_fetches,
        diagnostic=diagnostic,
    )
    completed_analyses = [completed_analysis]
    completed_run = CompletedRun(
        run_id=42,
        request_fingerprint="request-fingerprint",
        analysis_plan_fingerprint="plan-fingerprint",
        database_source=DatabaseSource.WD2.value,
        analyses=completed_analyses,
        map_data_schema_version=1,
    )
    query_fetches.clear()
    completed_analyses.clear()
    diagnostic_counts[0][1] = 99

    assert completed_run.analyses == (completed_analysis,)
    assert len(completed_analysis.query_fetches) == 1
    assert completed_analysis.diagnostic.measured_counts == (("source_row_count", 0),)
    for record, field_name, replacement in (
        (completed_run, "run_id", 99),
        (completed_analysis, "outcome", COMPLETED_RENDERABLE),
        (completed_analysis.analysis, "id", "other-analysis"),
        (completed_analysis.query_fetches[0], "elapsed_seconds", 99.0),
        (completed_analysis.diagnostic, "reason", "other-reason"),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(record, field_name, replacement)


def test_legacy_dictionary_is_restored_once_and_reused_without_copying(monkeypatch):
    """Warm result reads reuse the validated object without reparsing metadata."""
    snapshot = _completed_snapshot()
    session_state = {COMPLETED_RUN_SNAPSHOT_KEY: snapshot}
    completed_run = get_completed_run_snapshot(session_state)
    assert isinstance(completed_run, CompletedRun)
    assert session_state[COMPLETED_RUN_SNAPSHOT_KEY] is completed_run

    def reject_repeated_parsing(_cls, _snapshot):
        pytest.fail("An immutable completed run must not be parsed again")

    monkeypatch.setattr(CompletedRun, "from_dict", classmethod(reject_repeated_parsing))
    snapshot["database_source"] = "changed after restoration"
    assert get_completed_run_snapshot(session_state) is completed_run
    publish_completed_run_snapshot(session_state, completed_run)
    assert get_completed_run_snapshot(session_state) is completed_run


@pytest.mark.parametrize("field_path", [
    ("request_fingerprint",),
    ("analysis_plan_fingerprint",),
    ("database_source",),
    ("analyses", 0, "diagnostic"),
    ("analyses", 0, "selected_decode_filter_mode"),
    ("analyses", 0, "query_fetches", 0, "delivery_source"),
])
def test_missing_completion_provenance_cannot_replace_a_valid_run(field_path):
    """Reject incomplete publication before changing the completed marker."""
    snapshot = _completed_snapshot()
    previous_run = CompletedRun.from_dict(snapshot)
    session_state = {COMPLETED_RUN_SNAPSHOT_KEY: previous_run}
    parent_snapshot = snapshot
    for field_name in field_path[:-1]:
        parent_snapshot = parent_snapshot[field_name]
    del parent_snapshot[field_path[-1]]

    with pytest.raises((TypeError, ValueError)):
        publish_completed_run_snapshot(session_state, snapshot)

    assert session_state[COMPLETED_RUN_SNAPSHOT_KEY] is previous_run
    assert get_completed_run_snapshot({COMPLETED_RUN_SNAPSHOT_KEY: snapshot}) is None


@pytest.mark.parametrize(("field_path", "invalid_value"), [
    (("schema_version",), 999),
    (("map_data_schema_version",), 0),
    (("database_source",), "unknown-provider"),
    (("analyses", 0, "analysis", "is_compare"), False),
    (("analyses", 0, "analysis", "is_sequential"), "false"),
    (("analyses", 0, "outcome"), "unknown-outcome"),
    (("analyses", 0, "outcome"), COMPLETED_RENDERABLE),
    (("analyses", 0, "evidence_path"), "unexpected-evidence.parquet"),
    (("analyses", 0, "selected_decode_filter_mode"), DECODE_FILTER_STRICT),
    (("analyses", 0, "query_fetches"), ()),
    (("analyses", 0, "query_fetches", 0, "delivery_source"), "unknown-tier"),
    (("analyses", 0, "diagnostic", "measured_counts", "source_row_count"), 1),
])
def test_malformed_completion_is_unavailable(field_path, invalid_value):
    """Inconsistent metadata is never treated as a reusable completed result."""
    snapshot = _completed_snapshot()
    parent_snapshot = snapshot
    for field_name in field_path[:-1]:
        parent_snapshot = parent_snapshot[field_name]
    parent_snapshot[field_path[-1]] = invalid_value

    assert get_completed_run_snapshot({COMPLETED_RUN_SNAPSHOT_KEY: snapshot}) is None


def test_valid_diagnostic_cannot_explain_a_different_completion_outcome():
    """A no-source diagnostic cannot accompany an already prepared evidence map."""
    snapshot = _completed_snapshot()
    snapshot["analyses"][0]["outcome"] = COMPLETED_MAP_NO_DATA
    snapshot["analyses"][0]["evidence_path"] = "artifacts/spots_RX_COMPARE.parquet"

    with pytest.raises(ValueError, match="diagnostic does not match"):
        CompletedRun.from_dict(snapshot)
    assert get_completed_run_snapshot({COMPLETED_RUN_SNAPSHOT_KEY: snapshot}) is None


@pytest.mark.parametrize("elapsed_seconds", [
    pytest.param(float("nan"), id="nan"),
    pytest.param(float("inf"), id="infinity"),
    pytest.param(True, id="boolean"),
    pytest.param(-0.1, id="negative"),
    pytest.param(10 ** 1000, id="integer-overflow"),
])
def test_invalid_query_duration_is_rejected_without_breaking_result_restoration(elapsed_seconds):
    snapshot = _completed_snapshot()
    snapshot["analyses"][0]["query_fetches"][0]["elapsed_seconds"] = elapsed_seconds

    with pytest.raises(ValueError, match="duration"):
        CompletedRun.from_dict(snapshot)
    assert get_completed_run_snapshot({COMPLETED_RUN_SNAPSHOT_KEY: snapshot}) is None
