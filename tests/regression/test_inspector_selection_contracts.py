"""Canonical Inspector intent, identity and compatibility boundary contracts."""

from dataclasses import FrozenInstanceError, replace

import pytest

from config.config_schema import SEGMENT_DIRECTION_OPTIONS, STATION_EVIDENCE_TIME_BINS
from ui.inspector.selection import (
    InspectorSelection,
    StationIdentity,
    parse_segment_selection,
    parse_station_identities,
    segment_selection_value,
    station_identity_records,
    validate_evidence_time_bin,
)


def _selection(**overrides):
    selection_values = dict(
        run_id=17, analysis_id="RX_BENCHMARK", scope_token="scope-north", is_compare=True,
    )
    selection_values.update(overrides)
    return InspectorSelection(**selection_values)


def test_station_intent_preserves_automatic_deselection_and_exact_locator():
    assert parse_station_identities(None) is None
    assert parse_station_identities([]) == ()
    assert station_identity_records(None) is None
    assert station_identity_records(()) == []
    identities = parse_station_identities([
        {"callsign": " k1abc ", "locator": " fn42 "},
        {"callsign": "K1ABC", "locator": "FN42AB"},
    ], maximum_count=None)

    assert tuple(identity.pair for identity in identities) == (
        ("K1ABC", "FN42"), ("K1ABC", "FN42AB"),
    )
    serialized = station_identity_records(identities)
    serialized[0]["callsign"] = "CHANGED"
    assert identities[0].callsign == "K1ABC"
    with pytest.raises(FrozenInstanceError):
        identities[0].locator = "IO91"


@pytest.mark.parametrize(
    ("records", "error"),
    [
        ("all", "JSON array"),
        ([{"callsign": "K1ABC"}], "locator"),
        ([{"callsign": "K1ABC", "locator": "FN42", "label": "station"}], "Unknown"),
        ([{"callsign": "K1Aß", "locator": "FN42"}], "callsign"),
        ([{"callsign": "K1ABC", "locator": "FN42AA00"}], "locator"),
        ([{"callsign": 123, "locator": "FN42"}], "callsign must be a string"),
        ([{"callsign": "k1abc", "locator": "fn42"}, {"callsign": "K1ABC", "locator": "FN42"}], "duplicate station identity"),
    ],
)
def test_station_boundary_rejects_ambiguous_or_invalid_authored_intent(records, error):
    with pytest.raises(ValueError, match=error):
        parse_station_identities(records, field="results_view.benchmark.selected_stations", maximum_count=None)


def test_scope_all_is_distinct_from_explicit_selection_and_preserves_order():
    assert parse_segment_selection("all", field="directions", choices=SEGMENT_DIRECTION_OPTIONS) is None
    selected = parse_segment_selection(["NW", "N"], field="directions", choices=SEGMENT_DIRECTION_OPTIONS)
    assert selected == ("NW", "N")
    assert segment_selection_value(selected) == ["NW", "N"]
    assert segment_selection_value(None) == "all"
    assert selected != parse_segment_selection(["N", "NW"], field="directions", choices=SEGMENT_DIRECTION_OPTIONS)


@pytest.mark.parametrize("selection", ([], None, "N", ["N", "N"], ["north"]))
def test_scope_boundary_rejects_empty_or_invalid_explicit_scope(selection):
    with pytest.raises(ValueError):
        parse_segment_selection(selection, field="directions", choices=SEGMENT_DIRECTION_OPTIONS)


@pytest.mark.parametrize("time_bin", sorted(STATION_EVIDENCE_TIME_BINS))
def test_selection_retains_every_supported_and_legacy_temporal_bin(time_bin):
    selected = _selection(segment_time_bin=time_bin, station_time_bin=time_bin)
    assert selected.station_time_bin == selected.segment_time_bin == time_bin


def test_uninitialized_station_bin_and_auto_segment_bin_have_distinct_roles():
    assert _selection().station_time_bin is None
    assert _selection().segment_time_bin == "auto"
    with pytest.raises(ValueError):
        validate_evidence_time_bin("auto", field="station_time_bin")
    with pytest.raises(ValueError):
        validate_evidence_time_bin(None, field="station_time_bin")


@pytest.mark.parametrize(
    ("is_compare", "is_outlier_reporting_enabled", "is_allowed"),
    ((False, False, False), (False, True, False), (True, False, False), (True, True, True)),
)
def test_multiple_paths_require_benchmark_outlier_reporting(
    is_compare, is_outlier_reporting_enabled, is_allowed,
):
    identities = (StationIdentity("K1ABC", "FN42"), StationIdentity("G0IDE", "IO83"))
    arguments = dict(
        is_compare=is_compare,
        is_outlier_reporting_enabled=is_outlier_reporting_enabled,
        selected_stations=identities,
    )
    if is_allowed:
        assert _selection(**arguments).selected_stations is identities
    else:
        with pytest.raises(ValueError):
            _selection(**arguments)


def test_selection_snapshot_binds_intent_to_run_and_scope_without_mutability():
    selected = _selection(selected_stations=(), selected_directions=("N",))
    assert selected != replace(selected, run_id=18)
    assert selected != replace(selected, scope_token="scope-south")
    with pytest.raises(FrozenInstanceError):
        selected.scope_token = "changed"
    with pytest.raises(ValueError):
        replace(selected, selected_directions=())
    with pytest.raises(TypeError):
        replace(selected, selected_stations=[])
    with pytest.raises(ValueError):
        replace(selected, run_id=True)
