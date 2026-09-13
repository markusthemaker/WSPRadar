from ui.inspector import selection_state as inspector_selection
import pytest

from ui import result_state


def test_reset_result_state_retires_artifacts_and_clears_all_run_caches(monkeypatch):
    """A lightweight reset must preserve the complete result lifecycle."""
    retired_states = []
    monkeypatch.setattr(
        result_state,
        "retire_registered_session_artifacts",
        lambda session_state: retired_states.append(session_state),
    )
    session_state = {
        "run_id": 42,
        result_state.EXPORT_STATE_KEY: {"old": "block"},
        result_state.EXPORT_RUN_ID_KEY: 11,
        result_state.EXPORT_ZIP_BYTES_KEY: b"zip",
        result_state.EXPORT_ZIP_FILENAME_KEY: "results.zip",
        result_state.EXPORT_ZIP_SIGNATURE_KEY: "signature",
        result_state.INSPECTOR_CACHE_STATE_KEY: object(),
        result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY: {
            "run_id": 42,
            "source_key": "wd2",
        },
        result_state.COMPLETED_RUN_SNAPSHOT_KEY: {
            "schema_version": result_state.COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
            "run_id": 42,
        },
        inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY: {
            "analysis_id": "RX_COMP",
            "run_id": 42,
            "scope_token": "rall_dall",
            "station_identities": [
                {"callsign": "A1AAA", "locator": "AA00"}
            ],
        },
        inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY: {
            "analysis_id": "RX_COMP",
            "run_id": 42,
        },
        "unrelated": "preserved",
    }

    result_state.reset_result_state(session_state)

    assert retired_states == [session_state]
    assert session_state[result_state.EXPORT_STATE_KEY] == {}
    assert session_state[result_state.EXPORT_RUN_ID_KEY] == 42
    assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert result_state.EXPORT_ZIP_FILENAME_KEY not in session_state
    assert result_state.EXPORT_ZIP_SIGNATURE_KEY not in session_state
    assert result_state.INSPECTOR_CACHE_STATE_KEY not in session_state
    assert result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY not in session_state
    assert result_state.COMPLETED_RUN_SNAPSHOT_KEY not in session_state
    assert (
        inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY
        not in session_state
    )
    assert inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY not in session_state
    assert session_state["unrelated"] == "preserved"


def test_clear_prepared_result_state_does_not_clear_registered_blocks():
    """Prepared downloads can be invalidated without dropping result recipes."""
    session_state = {
        result_state.EXPORT_STATE_KEY: {"RX": "recipe"},
        result_state.EXPORT_ZIP_BYTES_KEY: b"zip",
        result_state.EXPORT_ZIP_FILENAME_KEY: "results.zip",
        result_state.EXPORT_ZIP_SIGNATURE_KEY: "signature",
    }

    result_state.clear_prepared_result_state(session_state)

    assert session_state[result_state.EXPORT_STATE_KEY] == {"RX": "recipe"}
    assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert result_state.EXPORT_ZIP_FILENAME_KEY not in session_state
    assert result_state.EXPORT_ZIP_SIGNATURE_KEY not in session_state


def test_clear_rendered_result_state_preserves_database_source_binding():
    """A same-run refresh must drop stale recipes without changing provenance."""
    source_binding = {"run_id": 42, "source_key": "wd2"}
    completed_snapshot = {
        "schema_version": result_state.COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
        "run_id": 42,
    }
    session_state = {
        "run_id": 42,
        result_state.EXPORT_STATE_KEY: {"old": "recipe"},
        result_state.EXPORT_RUN_ID_KEY: 42,
        result_state.EXPORT_ZIP_BYTES_KEY: b"zip",
        result_state.INSPECTOR_CACHE_STATE_KEY: object(),
        result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY: source_binding,
        result_state.COMPLETED_RUN_SNAPSHOT_KEY: completed_snapshot,
        inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY: {
            "analysis_id": "RX_COMP",
            "run_id": 42,
            "scope_token": "rall_dall",
            "station_identities": [
                {"callsign": "A1AAA", "locator": "AA00"}
            ],
        },
        inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY: {
            "analysis_id": "RX_COMP",
            "run_id": 42,
        },
    }

    result_state.clear_rendered_result_state(session_state)

    assert session_state[result_state.EXPORT_STATE_KEY] == {}
    assert session_state[result_state.EXPORT_RUN_ID_KEY] == 42
    assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert result_state.INSPECTOR_CACHE_STATE_KEY not in session_state
    assert session_state[result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY] is source_binding
    assert (
        session_state[result_state.COMPLETED_RUN_SNAPSHOT_KEY]
        is completed_snapshot
    )
    assert (
        inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY
        not in session_state
    )
    assert inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY not in session_state


def test_completed_rerender_preserves_inspector_cache_and_station_focus():
    """Keep same-result cache and focus through a navigation rerender."""
    inspector_cache = object()
    session_state = {
        "run_id": 42,
        result_state.EXPORT_STATE_KEY: {"old": "recipe"},
        result_state.EXPORT_ZIP_BYTES_KEY: b"zip",
        result_state.INSPECTOR_CACHE_STATE_KEY: inspector_cache,
        inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY: {
            "analysis_id": "RX_COMP",
            "run_id": 42,
            "scope_token": "rall_dall",
            "station_identities": [
                {"callsign": "A1AAA", "locator": "AA00"}
            ],
        },
        inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY: {
            "analysis_id": "RX_COMP",
            "run_id": 42,
        },
    }

    result_state.clear_rendered_result_state(
        session_state,
        preserve_inspector_cache=True,
    )

    assert session_state[result_state.EXPORT_STATE_KEY] == {}
    assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert (
        session_state[result_state.INSPECTOR_CACHE_STATE_KEY]
        is inspector_cache
    )
    assert session_state[
        inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY
    ]["station_identities"] == [
        {"callsign": "A1AAA", "locator": "AA00"}
    ]
    assert session_state[
        inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY
    ]["run_id"] == 42


def test_outlier_opt_out_always_clears_station_insights_focus():
    """Do not retain report-only navigation semantics after the opt-in is off."""
    focus_record = {
        "analysis_id": "RX_COMP",
        "run_id": 42,
        "scope_token": "rall_dall",
        "station_identities": [
            {"callsign": "A1AAA", "locator": "AA00"}
        ],
    }
    session_state = {
        inspector_selection.RESULTS_REPORT_DELTA_SNR_OUTLIER_CANDIDATES_STATE_KEY: (
            False
        ),
        inspector_selection.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY: [
            {"callsign": "A1AAA", "locator": "AA00"}
        ],
        inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY: (
            focus_record
        ),
        inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY: focus_record,
    }

    selection_changed = (
        inspector_selection.normalize_compare_station_selection_for_outlier_reporting(
            session_state
        )
    )

    assert selection_changed is False
    assert (
        inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY
        not in session_state
    )
    assert inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY not in session_state


def test_enabled_outlier_reporting_preserves_station_insights_focus():
    """Keep a queued focus record intact until its enabled report consumes it."""
    focus_record = {
        "analysis_id": "RX_COMP",
        "run_id": 42,
        "scope_token": "rall_dall",
        "station_identities": [
            {"callsign": "A1AAA", "locator": "AA00"}
        ],
    }
    session_state = {
        inspector_selection.RESULTS_REPORT_DELTA_SNR_OUTLIER_CANDIDATES_STATE_KEY: (
            True
        ),
        inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY: (
            focus_record
        ),
        inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY: focus_record,
    }

    selection_changed = (
        inspector_selection.normalize_compare_station_selection_for_outlier_reporting(
            session_state
        )
    )

    assert selection_changed is False
    assert session_state[
        inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY
    ] is focus_record
    assert session_state[
        inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY
    ] is focus_record


def test_completed_run_snapshot_rejects_unknown_schema_versions():
    """Treat an incompatible result marker as unavailable, never reusable."""
    session_state = {
        result_state.COMPLETED_RUN_SNAPSHOT_KEY: {
            "schema_version": 999,
        }
    }

    assert result_state.get_completed_run_snapshot(session_state) is None
    with pytest.raises(ValueError, match="schema version"):
        result_state.publish_completed_run_snapshot(
            session_state,
            {"schema_version": 999},
        )


def test_active_database_source_is_committed_only_for_its_matching_run():
    session_state = {"run_id": 42}

    result_state.set_active_run_database_source(
        session_state,
        run_id=42,
        source_key="wd2",
    )

    assert result_state.get_active_run_database_source(session_state) == "wd2"
    session_state["run_id"] = 43
    assert result_state.get_active_run_database_source(session_state) is None

@pytest.mark.parametrize("preserve_inspector_cache", [False, True])
@pytest.mark.parametrize("preserve_export_state", [False, True])
def test_export_preservation_is_independent_and_keeps_registry_reference(
    preserve_inspector_cache, preserve_export_state,
):
    from types import MappingProxyType

    registry = MappingProxyType({"RX": "owned payload"})
    inspector_cache = object()
    prepared = {
        result_state.EXPORT_ZIP_BYTES_KEY: b"zip",
        result_state.EXPORT_ZIP_FILENAME_KEY: "results.zip",
        result_state.EXPORT_ZIP_SIGNATURE_KEY: "signature",
    }
    session_state = {
        "run_id": 42,
        result_state.EXPORT_RUN_ID_KEY: 42,
        result_state.EXPORT_STATE_KEY: registry,
        result_state.INSPECTOR_CACHE_STATE_KEY: inspector_cache,
        **prepared,
    }

    result_state.clear_rendered_result_state(
        session_state,
        preserve_inspector_cache=preserve_inspector_cache,
        preserve_export_state=preserve_export_state,
    )

    assert session_state[result_state.EXPORT_RUN_ID_KEY] == 42
    if preserve_export_state:
        assert session_state[result_state.EXPORT_STATE_KEY] is registry
        for key, value in prepared.items():
            assert session_state[key] is value
    else:
        assert session_state[result_state.EXPORT_STATE_KEY] == {}
        assert all(key not in session_state for key in prepared)
    if preserve_inspector_cache:
        assert session_state[result_state.INSPECTOR_CACHE_STATE_KEY] is inspector_cache
    else:
        assert result_state.INSPECTOR_CACHE_STATE_KEY not in session_state
