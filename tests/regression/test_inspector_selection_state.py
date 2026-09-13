"""Selection-state ownership, preservation, and bounded-work contracts."""

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pandas as pd
import pytest

from ui.inspector import selection_state


def test_seed_defaults_preserves_initialized_intent_and_factory_reset_overwrites():
    configured_stations = []
    session_state = {
        selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY: configured_stations,
        selection_state.RESULTS_TIME_BIN_COMPARE_STATE_KEY: "15m",
        "unrelated": "retained",
    }

    selection_state.seed_inspector_selection_state(session_state)

    assert session_state[selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY] is configured_stations
    assert session_state[selection_state.RESULTS_TIME_BIN_COMPARE_STATE_KEY] == "15m"
    assert session_state[selection_state.RESULTS_SELECTED_RANGES_COMPARE_STATE_KEY] == "all"
    assert session_state[selection_state.RESULTS_SEGMENT_TIME_BIN_ABSOLUTE_STATE_KEY] == "auto"

    selection_state.seed_inspector_selection_state(session_state, overwrite=True)

    assert session_state[selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY] is None
    assert session_state[selection_state.RESULTS_TIME_BIN_COMPARE_STATE_KEY] is None
    assert session_state["unrelated"] == "retained"


def test_seed_loaded_selection_applies_only_supplied_keys_without_copying_records():
    configured_stations = [{"callsign": "K1ABC", "locator": "FN42"}]
    session_state = {selection_state.RESULTS_TIME_BIN_COMPARE_STATE_KEY: "15m"}

    selection_state.seed_inspector_selection_state(
        session_state,
        {selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY: configured_stations},
        overwrite=True,
    )

    assert session_state[selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY] is configured_stations
    assert session_state[selection_state.RESULTS_TIME_BIN_COMPARE_STATE_KEY] == "15m"
    assert selection_state.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY not in session_state


def test_seed_unknown_field_is_rejected_before_any_state_write():
    session_state = {}

    with pytest.raises(ValueError, match="Unknown Inspector selection fields"):
        selection_state.seed_inspector_selection_state(
            session_state,
            {selection_state.RESULTS_TIME_BIN_COMPARE_STATE_KEY: "15m", "run_id": 2},
            overwrite=True,
        )

    assert session_state == {}


def test_default_station_rows_preserve_identity_order_without_dataframe_projection():
    class IdentityColumnsOnlyFrame(pd.DataFrame):
        def __getitem__(self, column):
            if isinstance(column, list):
                raise AssertionError("Selection lookup must not build a projected DataFrame")
            return super().__getitem__(column)

    station_table = IdentityColumnsOnlyFrame({
        "Station": ["K1ABC", "N1DEF", "K1ABC"],
        "Locator": ["FN42", "JO62QM", "FN42AA"],
    })
    configured_stations = [
        {"callsign": "K1ABC", "locator": "FN42AA"},
        {"callsign": "W1XYZ", "locator": "FN31"},
        {"callsign": "N1DEF", "locator": "JO62QM"},
    ]

    selected_rows, missing_identities = selection_state.station_selection_default_rows(
        station_table, "Station", "Locator", configured_stations,
        allow_multiple=True,
    )

    assert selected_rows == [2, 1]
    assert missing_identities == [{"callsign": "W1XYZ", "locator": "FN31"}]
    assert station_table["Locator"].tolist() == ["FN42", "JO62QM", "FN42AA"]


def test_table_default_and_real_deselection_have_distinct_persistence():
    station_table = pd.DataFrame({"Station": ["K1ABC"], "Locator": ["FN42"]})
    saved_identity = [{"callsign": "W1XYZ", "locator": "FN31"}]
    persistent_key = selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY
    session_state = {persistent_key: saved_identity}

    selection_state.sync_selected_station_state_if_changed(
        session_state, "selection_changed", persistent_key,
        station_table, [], "Station", "Locator",
    )
    assert session_state[persistent_key] is saved_identity

    selection_state.mark_station_selection_changed(session_state, "selection_changed")
    selection_state.sync_selected_station_state_if_changed(
        session_state, "selection_changed", persistent_key,
        station_table, [], "Station", "Locator",
    )
    assert session_state[persistent_key] == []
    assert "selection_changed" not in session_state


def test_ui_multi_selection_retains_first_normalized_identity_once():
    assert selection_state.validate_multiple_station_identity_records([
        {"callsign": "k1abc", "locator": "fn42"},
        {"callsign": "N1DEF", "locator": "JO62QM"},
        {"callsign": "K1ABC", "locator": "FN42"},
    ]) == [
        {"callsign": "K1ABC", "locator": "FN42"},
        {"callsign": "N1DEF", "locator": "JO62QM"},
    ]


def test_typed_default_selection_reuses_validated_identities_without_codec_roundtrip(monkeypatch):
    station_table = pd.DataFrame({"Station": ["K1ABC"], "Locator": ["FN42"]})
    selection = selection_state.read_inspector_selection(
        {selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY: [
            {"callsign": "K1ABC", "locator": "FN42"},
        ]},
        run_id=42, analysis_id="RX_COMP", scope_token="rall_dall",
        is_compare=True, selected_ranges=(), selected_directions=(),
    )

    def fail_revalidation(*args, **kwargs):
        raise AssertionError("Typed selection must not be serialized and revalidated")

    monkeypatch.setattr(selection_state, "parse_station_identities", fail_revalidation)
    monkeypatch.setattr(selection_state, "station_identity_records", fail_revalidation)

    assert selection_state.station_selection_default_rows(
        station_table, "Station", "Locator", selection,
    ) == ([0], [])


def test_report_opt_out_clears_focus_and_truncates_multi_without_resetting_other_intent():
    configured_stations = [
        {"callsign": "K1ABC", "locator": "FN42"},
        {"callsign": "N1DEF", "locator": "JO62QM"},
    ]
    session_state = {
        selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY: configured_stations,
        selection_state.RESULTS_REPORT_DELTA_SNR_OUTLIER_CANDIDATES_STATE_KEY: False,
        selection_state.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY: {},
        selection_state.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY: {},
        selection_state.RESULTS_TIME_BIN_COMPARE_STATE_KEY: "15m",
        "completed_run_snapshot": object(),
    }
    completed_run = session_state["completed_run_snapshot"]

    assert selection_state.normalize_compare_station_selection_for_outlier_reporting(session_state)

    assert session_state[selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY] == configured_stations[:1]
    assert selection_state.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY not in session_state
    assert selection_state.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY not in session_state
    assert session_state[selection_state.RESULTS_TIME_BIN_COMPARE_STATE_KEY] == "15m"
    assert session_state["completed_run_snapshot"] is completed_run


def test_stale_outlier_actions_cannot_mutate_selection_focus_or_navigation():
    session_state = {"run_id": 42, "retained": {"selection": []}}
    unchanged_state = deepcopy(session_state)

    assert selection_state.select_outlier_station_identities(
        object(), session_state, analysis_id="RX_COMP", run_id=41, scope_token="rall_dall",
    ) is None
    assert selection_state.select_outlier_candidate(
        object(), object(), session_state,
        analysis_id="RX_COMP", run_id=41, scope_token="rall_dall",
        navigation_anchor_id="unused",
    ) is None
    assert session_state == unchanged_state


@pytest.mark.parametrize("invalid_field,invalid_value", [
    ("callsign", "not a callsign"),
    ("locator", "invalid"),
])
@pytest.mark.parametrize("action_kind", ["station_paths", "candidate"])
def test_invalid_outlier_identity_fails_before_any_action_state_is_changed(
    invalid_field, invalid_value, action_kind,
):
    identity_fields = {"callsign": "K1ABC", "locator": "FN42"}
    identity_fields[invalid_field] = invalid_value
    invalid_identity = SimpleNamespace(**identity_fields)
    session_state = {
        "run_id": 42,
        selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY: [],
        selection_state.RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY: 8,
        selection_state.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY: {"prior": "station"},
        selection_state.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY: {"prior": "candidate"},
        "_application_page_navigation_request": {"prior": "navigation"},
        "prior_applied_outlier_request": "retained",
    }
    unchanged_state = deepcopy(session_state)

    with pytest.raises(ValueError, match=invalid_field):
        if action_kind == "candidate":
            # No other candidate/model fields are exposed: identity validation
            # must precede both candidate preparation and its first state write.
            selection_state.select_outlier_candidate(
                SimpleNamespace(station_identity=invalid_identity), object(), session_state,
                analysis_id="RX_COMP", run_id=42, scope_token="rall_dall",
                navigation_anchor_id="unused",
            )
        else:
            selection_state.select_outlier_station_identities(
                (SimpleNamespace(callsign="N1DEF", locator="JO62QM"), invalid_identity),
                session_state,
                analysis_id="RX_COMP", run_id=42, scope_token="rall_dall",
            )

    assert session_state == unchanged_state


def test_outlier_action_normalizes_and_deduplicates_exact_paths_through_shared_parser(monkeypatch):
    from ui import page_navigation
    from ui.inspector.outlier_candidates import OutlierStationIdentity

    parsed_identity_records = []
    canonical_parser = selection_state.parse_station_identities

    def record_identity_validation(records, **kwargs):
        parsed_identity_records.extend(records)
        return canonical_parser(records, **kwargs)

    navigation_requests = []
    monkeypatch.setattr(selection_state, "parse_station_identities", record_identity_validation)
    monkeypatch.setattr(
        page_navigation,
        "request_page_navigation",
        lambda state, anchor, **kwargs: navigation_requests.append((anchor, kwargs)),
    )
    session_state = {
        "run_id": 42,
        selection_state.RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY: 8,
        selection_state.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY: {"prior": "candidate"},
    }

    selected_records = selection_state.select_outlier_station_identities(
        (
            OutlierStationIdentity("k1abc", "fn42"),
            OutlierStationIdentity("K1ABC", "FN42AA"),
            OutlierStationIdentity("K1ABC", "FN42"),
            OutlierStationIdentity("n1def", "jo62qm"),
        ),
        session_state,
        analysis_id="RX_COMP", run_id=42, scope_token="rall_dall",
    )

    assert selected_records == [
        {"callsign": "K1ABC", "locator": "FN42"},
        {"callsign": "K1ABC", "locator": "FN42AA"},
        {"callsign": "N1DEF", "locator": "JO62QM"},
    ]
    assert len(parsed_identity_records) == 4
    assert session_state[selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY] == selected_records
    assert session_state[selection_state.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY]["station_identities"] == selected_records
    assert session_state[selection_state.RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY] == 9
    assert selection_state.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY not in session_state
    assert navigation_requests == [(page_navigation.STATION_INSIGHTS_ANCHOR_ID, {"should_scroll": True})]


@pytest.mark.parametrize("configured_stations, expected_stations", [(None, None), ([], ())])
def test_active_selection_record_retains_automatic_versus_empty_intent(
    configured_stations, expected_stations,
):
    session_state = {
        selection_state.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY: configured_stations,
        selection_state.RESULTS_TIME_BIN_COMPARE_STATE_KEY: "15m",
    }

    selection = selection_state.read_inspector_selection(
        session_state,
        run_id=42,
        analysis_id="RX_COMP",
        scope_token="rall_dall",
        is_compare=True,
        selected_ranges=(),
        selected_directions=(),
    )

    assert selection.selected_stations == expected_stations
    assert selection.selected_ranges is None
    assert selection.selected_directions is None
    assert selection.station_time_bin == "15m"


def test_adapter_import_and_idle_lifecycle_helpers_do_not_load_scientific_runtime():
    audit_script = r'''
import sys
from ui.inspector import selection_state
state = {}
selection_state.seed_inspector_selection_state(state)
selection_state.mark_station_selection_changed(state, "changed")
selection_state.normalize_compare_station_selection_for_outlier_reporting(state)
selection_state.release_selected_station_state(state)
forbidden = (
    "streamlit", "pandas", "numpy", "matplotlib", "requests", "cartopy",
    "ui.inspector.drilldown_focus", "ui.inspector.outlier_candidates",
    "ui.components.segment_inspector", "ui.results_export",
)
loaded = [name for name in sys.modules
          if any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden)]
assert not loaded, loaded
'''
    completed_audit = subprocess.run(
        [sys.executable, "-c", audit_script],
        cwd=Path(__file__).resolve().parents[2],
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert completed_audit.returncode == 0, completed_audit.stdout + completed_audit.stderr
