"""Streamlit rerun coverage for canonical Inspector state and candidate focus."""

import ast
import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.proto.WidgetStates_pb2 import WidgetStates
from streamlit.testing.v1 import AppTest

from ui.inspector.drilldown_focus import DRILLDOWN_OUTLIER_FOCUS_OPTION
from ui.inspector.selection_state import RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY


_SCOPE_CONTROL_APP = r'''
import streamlit as st

from ui.inspector.selection_state import (
    initialize_explicit_all_multiselect,
    update_explicit_all_multiselect,
)


scope_arguments = (
    st.session_state,
    "range_widget",
    "range_widget_previous",
    "Full Range",
    ["[0-2500km]", "[2500-5000km]"],
    "val_results_selected_ranges_compare",
)
if st.toggle("Show scope", key="show_scope"):
    initialize_explicit_all_multiselect(*scope_arguments)
    st.multiselect(
        "Distance range",
        ["Full Range", "[0-2500km]", "[2500-5000km]"],
        key="range_widget",
        select_all=False,
        on_change=update_explicit_all_multiselect,
        args=scope_arguments,
    )
'''


_DRILLDOWN_CONTROL_APP = r'''
import pandas as pd
import streamlit as st

from core.analysis_context import AnalysisContext, COMPARISON_REFERENCE_STATION
from i18n import T
from ui.components.inspector_selected import render_drilldown_header_and_controls


scope_token = st.selectbox(
    "Active scope", ["rall_dall", "r0_d0"], key="active_scope",
)
if st.toggle("Show Drill-Down", key="show_drilldown"):
    focus_window, focus_time_bin, _filter_container = render_drilldown_header_and_controls(
        ["A1AAA (AA00)"],
        "RX_COMP",
        7,
        scope_token,
        T["en"],
        True,
        AnalysisContext(comparison_mode=COMPARISON_REFERENCE_STATION),
        "en",
        analysis_start_utc=pd.Timestamp("2026-01-01T00:00:00Z"),
        analysis_end_utc=pd.Timestamp("2026-01-03T00:00:00Z"),
        selected_identity=("A1AAA", "AA00"),
        session_state=st.session_state,
    )
    st.session_state["observed_focus_option"] = (
        focus_window.option if focus_window is not None else "off"
    )
    st.session_state["observed_focus_time_bin"] = focus_time_bin
'''


_STATION_INSIGHTS_APP = r'''
from functools import partial
from types import SimpleNamespace

import pandas as pd
import streamlit as st

from core.analysis_context import AnalysisContext, COMPARISON_REFERENCE_STATION
from core.presentation_context import PresentationContext
from i18n import T
from ui.components.inspector_stations import (
    render_benchmark_station_insights,
    render_performance_station_insights,
)
from ui.inspector.contracts import InspectorContext, InspectorScope
from ui.inspector.selection import StationIdentity
from ui.inspector.selection_state import (
    read_inspector_selection,
    select_outlier_episode_paths,
)


is_compare = st.session_state["fixture_is_compare"]
report_outliers = st.session_state["fixture_report_outliers"]
analysis_id = "RX_COMP" if is_compare else "RX"
translations = T["en"]
station_column = translations["tbl_col_tx"]
locator_column = translations["tbl_col_loc"]
distance_column = translations["tbl_col_km"]
azimuth_column = translations["tbl_col_az"]
joint_column = translations["tbl_col_joint"]
station_identities = st.session_state["fixture_station_identities"]
station_table = pd.DataFrame({
    station_column: [identity[0] for identity in station_identities],
    locator_column: [identity[1] for identity in station_identities],
    distance_column: [598, 141, 127],
    azimuth_column: [291.2, 59.7, 42.1],
    joint_column: [1441, 357, 341],
})
scope = InspectorScope(
    selected_ranges=(),
    selected_directions=(),
    range_summary="Full Range",
    direction_summary="All Directions",
    selected_segment="All",
    active_scope_summary="Full Range; All Directions",
    scope_token="rall_dall",
)
context = InspectorContext(
    analysis_id=analysis_id,
    title="Station selection integration",
    is_compare=is_compare,
    parquet_path=None,
    line1_str="",
    translations=translations,
    max_peer_distance_km=5000,
    analysis_context=AnalysisContext(
        callsign="ON4AWM0",
        reference_callsign="ON4AWM1",
        comparison_mode=COMPARISON_REFERENCE_STATION if is_compare else "none",
    ),
    presentation_context=PresentationContext(solar_label="All", labels=translations),
    analysis_kind="comparison" if is_compare else "opportunity",
    run_id=7,
)
if report_outliers:
    report_entry = SimpleNamespace(station_identities=(
        StationIdentity("DF2JP", "JO31FP"),
        StationIdentity("DC0DX", "JO31LK"),
    ))
    st.button(
        "Show all qualifying paths in Station Insights",
        key="show_report_paths",
        on_click=partial(
            select_outlier_episode_paths,
            report_entry,
            st.session_state,
            analysis_id=analysis_id,
            run_id=7,
            scope_token=scope.scope_token,
        ),
    )
current_selection = read_inspector_selection(
    st.session_state,
    run_id=7,
    analysis_id=analysis_id,
    scope_token=scope.scope_token,
    is_compare=is_compare,
    selected_ranges=scope.selected_ranges,
    selected_directions=scope.selected_directions,
    is_outlier_reporting_enabled=report_outliers,
)
if is_compare:
    prepared_segment = SimpleNamespace(
        scope_rows=pd.DataFrame({
            "spot_count": [1], "count_only_u": [0], "count_only_r": [0],
        }),
        bundle={"view_model": SimpleNamespace(
            station_table=station_table,
            station_column=station_column,
            joint_column=joint_column,
        )},
    )
    renderer = render_benchmark_station_insights
else:
    prepared_segment = SimpleNamespace(bundle={"display_model": {
        "station_column": station_column,
        "locator_column": locator_column,
        "distance_column": distance_column,
        "azimuth_column": azimuth_column,
        "hit_column": joint_column,
        "full_station_table": station_table,
    }})
    renderer = render_performance_station_insights
view = renderer(
    context, scope, current_selection, prepared_segment,
    session_state=st.session_state,
)
st.session_state["observed_evidence_identities"] = list(
    view.selected_station_table.iloc[list(view.selected_rows)][
        [station_column, locator_column]
    ].itertuples(index=False, name=None)
)
st.session_state["observed_source_order"] = station_table[station_column].tolist()
'''


def _station_insights_application(
    *, is_compare, report_outliers=False, selected=None, station_identities=None,
):
    application = AppTest.from_string(_STATION_INSIGHTS_APP, default_timeout=30)
    application.session_state["fixture_is_compare"] = is_compare
    application.session_state["fixture_report_outliers"] = report_outliers
    application.session_state["fixture_station_identities"] = station_identities or [
        ("M7AEO", "IO82"), ("DC0DX", "JO31LK"), ("DF2JP", "JO31FP"),
    ]
    state_key = (
        "val_results_selected_stations_compare"
        if is_compare else "val_results_selected_stations_absolute"
    )
    application.session_state[state_key] = selected
    application.run()
    assert application.exception.values == []
    return application, state_key


def _select_station_dataframe_rows(application, rows):
    """Deliver native dataframe events because AppTest has no row-click API."""
    widget_states = WidgetStates()
    widget_states.CopyFrom(application._tree.get_widget_states())
    widget_states.widgets.add(
        id=application.dataframe[0].proto.id,
        string_value=json.dumps({
            "selection": {"rows": rows, "columns": [], "cells": []},
        }),
    )
    application._run(widget_states)
    assert application.exception.values == []


def _assert_station_insights_selection(
    application, expected_order, expected_identities, *, expected_evidence=None,
):
    dataframe = application.dataframe[0]
    assert dataframe.value.iloc[:, 0].tolist() == expected_order
    selected_rows = application.session_state[dataframe.key]["selection"]["rows"]
    checked_identities = list(
        dataframe.value.iloc[selected_rows, :2].itertuples(index=False, name=None)
    )
    assert set(checked_identities) == set(expected_identities)
    assert set(application.session_state["observed_evidence_identities"]) == set(
        expected_identities if expected_evidence is None else expected_evidence
    )
    assert application.session_state["observed_source_order"] == [
        identity[0] for identity in application.session_state["fixture_station_identities"]
    ]


def test_report_path_deselection_keeps_remaining_identity_after_table_reordering():
    """The reported DF2JP deselection must retain DC0DX, never row-zero M7AEO."""
    application, state_key = _station_insights_application(
        is_compare=True,
        report_outliers=True,
        selected=[{"callsign": "M7AEO", "locator": "IO82"}],
    )
    application.button("show_report_paths").click().run()
    assert application.exception.values == []
    _assert_station_insights_selection(
        application, ["DC0DX", "DF2JP", "M7AEO"],
        [("DC0DX", "JO31LK"), ("DF2JP", "JO31FP")],
    )

    _select_station_dataframe_rows(application, [0])
    _assert_station_insights_selection(
        application, ["DC0DX", "M7AEO", "DF2JP"], [("DC0DX", "JO31LK")],
    )
    assert application.session_state[state_key] == [
        {"callsign": "DC0DX", "locator": "JO31LK"},
    ]
    application.run()
    assert application.exception.values == []
    _assert_station_insights_selection(
        application, ["DC0DX", "M7AEO", "DF2JP"], [("DC0DX", "JO31LK")],
    )

    # Add a lower row manually, then remove the other selected station.
    _select_station_dataframe_rows(application, [0, 2])
    _assert_station_insights_selection(
        application, ["DC0DX", "DF2JP", "M7AEO"],
        [("DC0DX", "JO31LK"), ("DF2JP", "JO31FP")],
    )
    _select_station_dataframe_rows(application, [1])
    _assert_station_insights_selection(
        application, ["DF2JP", "M7AEO", "DC0DX"], [("DF2JP", "JO31FP")],
    )
    assert application.session_state[state_key] == [
        {"callsign": "DF2JP", "locator": "JO31FP"},
    ]
    _select_station_dataframe_rows(application, [])
    application.run()
    assert application.exception.values == []
    assert application.session_state[state_key] == []
    _assert_station_insights_selection(application, ["M7AEO", "DC0DX", "DF2JP"], [])


@pytest.mark.parametrize("is_compare", [False, True], ids=["performance", "benchmark"])
def test_manual_single_station_selection_moves_to_top_and_can_be_cleared(is_compare):
    application, state_key = _station_insights_application(is_compare=is_compare)
    _select_station_dataframe_rows(application, [2])
    _assert_station_insights_selection(
        application, ["DF2JP", "M7AEO", "DC0DX"], [("DF2JP", "JO31FP")],
    )
    assert application.session_state[state_key] == [
        {"callsign": "DF2JP", "locator": "JO31FP"},
    ]
    _select_station_dataframe_rows(application, [2])
    _assert_station_insights_selection(
        application, ["DC0DX", "M7AEO", "DF2JP"], [("DC0DX", "JO31LK")],
    )
    assert application.session_state[state_key] == [
        {"callsign": "DC0DX", "locator": "JO31LK"},
    ]
    _select_station_dataframe_rows(application, [])
    application.run()
    assert application.exception.values == []
    assert application.session_state[state_key] == []
    _assert_station_insights_selection(application, ["M7AEO", "DC0DX", "DF2JP"], [])


@pytest.mark.parametrize(
    ("is_compare", "report_outliers", "selected", "expected_order"),
    [
        (False, False, [("DF2JP", "JO31FP")], ["DF2JP", "M7AEO", "DC0DX"]),
        (True, False, [("DF2JP", "JO31FP")], ["DF2JP", "M7AEO", "DC0DX"]),
        (
            True, True, [("DF2JP", "JO31FP"), ("DC0DX", "JO31LK")],
            ["DC0DX", "DF2JP", "M7AEO"],
        ),
    ],
    ids=["performance", "benchmark-single", "benchmark-multiple"],
)
def test_restored_station_identities_start_at_top_without_report_focus(
    is_compare, report_outliers, selected, expected_order,
):
    saved_records = [
        {"callsign": callsign, "locator": locator} for callsign, locator in selected
    ]
    application, state_key = _station_insights_application(
        is_compare=is_compare, report_outliers=report_outliers, selected=saved_records,
    )
    _assert_station_insights_selection(application, expected_order, selected)
    application.run()
    assert application.exception.values == []
    _assert_station_insights_selection(application, expected_order, selected)
    assert application.session_state[state_key] == saved_records


@pytest.mark.parametrize(
    ("is_compare", "report_outliers"),
    [(False, False), (True, False), (True, True)],
    ids=["performance", "benchmark-single", "benchmark-multiple"],
)
def test_station_filter_hide_and_restore_preserves_identity_and_selected_first_order(
    is_compare, report_outliers,
):
    selected = [{"callsign": "DF2JP", "locator": "JO31FP"}]
    application, state_key = _station_insights_application(
        is_compare=is_compare, report_outliers=report_outliers, selected=selected,
    )
    _assert_station_insights_selection(
        application, ["DF2JP", "M7AEO", "DC0DX"], [("DF2JP", "JO31FP")],
    )
    application.multiselect[0].set_value(["km"]).run()
    assert application.exception.values == []
    application.slider[0].set_range(141.0, 598.0).run()
    assert application.exception.values == []
    assert application.session_state[state_key] == selected
    assert application.warning
    _assert_station_insights_selection(
        application, ["M7AEO", "DC0DX"], [],
        expected_evidence=[("DF2JP", "JO31FP")] if report_outliers else [],
    )
    application.run()
    assert application.exception.values == []
    assert application.session_state[state_key] == selected
    application.multiselect[0].set_value([]).run()
    assert application.exception.values == []
    assert not application.warning
    assert application.session_state[state_key] == selected
    _assert_station_insights_selection(
        application, ["DF2JP", "M7AEO", "DC0DX"], [("DF2JP", "JO31FP")],
    )


@pytest.mark.parametrize("is_compare", [False, True], ids=["performance", "benchmark"])
def test_station_reordering_keeps_same_callsign_at_distinct_locators_separate(is_compare):
    application, state_key = _station_insights_application(
        is_compare=is_compare,
        station_identities=[
            ("DF2JP", "IO82"), ("DC0DX", "JO31LK"), ("DF2JP", "JO31FP"),
        ],
        selected=[{"callsign": "DF2JP", "locator": "JO31FP"}],
    )
    _assert_station_insights_selection(
        application, ["DF2JP", "DF2JP", "DC0DX"], [("DF2JP", "JO31FP")],
    )
    assert application.dataframe[0].value.iloc[:, 1].tolist() == [
        "JO31FP", "IO82", "JO31LK",
    ]
    _select_station_dataframe_rows(application, [1])
    _assert_station_insights_selection(
        application, ["DF2JP", "DC0DX", "DF2JP"], [("DF2JP", "IO82")],
    )
    assert application.session_state[state_key] == [
        {"callsign": "DF2JP", "locator": "IO82"},
    ]
    _select_station_dataframe_rows(application, [2])
    _assert_station_insights_selection(
        application, ["DF2JP", "DF2JP", "DC0DX"], [("DF2JP", "JO31FP")],
    )
    assert application.session_state[state_key] == [
        {"callsign": "DF2JP", "locator": "JO31FP"},
    ]


def _candidate_context():
    """Retain exact candidate evidence independently of the operator's zoom."""
    representative = pd.Timestamp("2026-01-01T12:00:00Z")
    return {
        "schema_version": 1,
        "analysis_id": "RX_COMP",
        "run_id": 7,
        "scope_token": "rall_dall",
        "callsign": "A1AAA",
        "locator": "AA00",
        "request_token": "deterministic-candidate-request",
        "representative_utc_ns": int(representative.value),
        "representative_delta_snr_db": 10.0,
        "event_start_utc_ns": int((representative - pd.Timedelta(minutes=2)).value),
        "event_end_utc_ns": int((representative + pd.Timedelta(nanoseconds=1)).value),
        "baseline_anchor_start_utc_ns": int((representative - pd.Timedelta(minutes=10)).value),
        "baseline_anchor_end_utc_ns": int((representative + pd.Timedelta(minutes=10)).value),
        "episode_guard_minutes": 10.0,
        "pre_flank_start_utc_ns": int((representative - pd.Timedelta(hours=7)).value),
        "pre_flank_end_utc_ns": int((representative - pd.Timedelta(minutes=20)).value),
        "post_flank_start_utc_ns": int((representative + pd.Timedelta(minutes=20)).value),
        "post_flank_end_utc_ns": int((representative + pd.Timedelta(hours=7)).value),
        "local_baseline_db": 2.0,
        "pre_baseline_db": 1.8,
        "post_baseline_db": 2.2,
        "robust_spread_db": 1.0,
        "robust_spread_method": "mad",
        "robust_z": 5.4,
        "minimum_robust_z": 3.0,
        "minimum_departure_db": 6.0,
        "detector_version": "native-residual-episode-v7",
        "candidate_signature": "candidate-signature",
    }


def _drilldown_application():
    application = AppTest.from_string(_DRILLDOWN_CONTROL_APP, default_timeout=30)
    application.session_state["show_drilldown"] = True
    application.session_state[RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY] = _candidate_context()
    application.session_state["val_results_selected_stations_compare"] = [
        {"callsign": "A1AAA", "locator": "AA00"},
    ]
    application.run()
    assert application.exception.values == []
    return application


def _zoom_selectbox(application):
    return next(
        selectbox for selectbox in application.selectbox
        if selectbox.key.startswith("d_zoom_")
    )


def test_scope_callback_and_widget_cleanup_preserve_saved_station_intent():
    """Scope edits and hidden controls cannot erase an unavailable saved station."""
    application = AppTest.from_string(_SCOPE_CONTROL_APP, default_timeout=10)
    saved_stations = [{"callsign": "B2BBB", "locator": "BB11"}]
    application.session_state["val_results_selected_stations_compare"] = saved_stations
    application.session_state["val_results_selected_ranges_compare"] = ["[2500-5000km]"]
    application.session_state["show_scope"] = True
    application.run()
    assert application.exception.values == []
    assert application.multiselect("range_widget").value == ["[2500-5000km]"]

    application.multiselect("range_widget").set_value(["Full Range"]).run()
    assert application.exception.values == []
    assert application.session_state["val_results_selected_ranges_compare"] == "all"
    application.multiselect("range_widget").set_value(["[0-2500km]"]).run()
    assert application.exception.values == []
    assert application.session_state["val_results_selected_ranges_compare"] == ["[0-2500km]"]

    application.toggle("show_scope").set_value(False).run()
    assert application.exception.values == []
    assert "range_widget" not in application.session_state
    application.toggle("show_scope").set_value(True).run()
    assert application.exception.values == []
    assert application.multiselect("range_widget").value == ["[0-2500km]"]
    assert application.session_state["val_results_selected_stations_compare"] == saved_stations


def test_scope_repeated_raw_snapshot_preserves_widget_and_durable_selection():
    """Replay the mixed browser array after its first callback normalized it."""
    application = AppTest.from_string(_SCOPE_CONTROL_APP, default_timeout=10)
    application.session_state["show_scope"] = True
    application.run()
    assert application.exception.values == []
    assert application.multiselect("range_widget").value == ["Full Range"]

    raw_specific_selection = ["Full Range", "[0-2500km]"]
    for _ in range(2):
        application.multiselect("range_widget").set_value(raw_specific_selection).run()
        assert application.exception.values == []
        assert application.multiselect("range_widget").value == ["[0-2500km]"]
        assert application.session_state["val_results_selected_ranges_compare"] == ["[0-2500km]"]

    # The frontend appends a newly selected option after the current chips.
    # Reversing the raw order represents a real new request for Full Range.
    raw_all_selection = ["[0-2500km]", "Full Range"]
    for _ in range(2):
        application.multiselect("range_widget").set_value(raw_all_selection).run()
        assert application.exception.values == []
        assert application.multiselect("range_widget").value == ["Full Range"]
        assert application.session_state["val_results_selected_ranges_compare"] == "all"

    application.multiselect("range_widget").set_value(raw_specific_selection).run()
    application.toggle("show_scope").set_value(False).run()
    assert application.exception.values == []
    assert "range_widget" not in application.session_state
    application.toggle("show_scope").set_value(True).run()
    assert application.exception.values == []
    assert application.multiselect("range_widget").value == ["[0-2500km]"]
    assert application.session_state["val_results_selected_ranges_compare"] == ["[0-2500km]"]


def test_manual_zoom_preserves_candidate_provenance_and_cleanup_rehydrates_focus():
    """Exercise live controls, including Streamlit's removal of hidden widgets."""
    application = _drilldown_application()
    candidate_context = _candidate_context()
    assert _zoom_selectbox(application).value == DRILLDOWN_OUTLIER_FOCUS_OPTION
    assert application.session_state["observed_focus_time_bin"] == "2m"

    _zoom_selectbox(application).select("3h").run()
    assert application.exception.values == []
    assert application.session_state["observed_focus_option"] == "3h"
    assert application.session_state[RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY] == candidate_context
    application.run()
    assert application.exception.values == []
    assert _zoom_selectbox(application).value == "3h"

    zoom_widget_key = _zoom_selectbox(application).key
    application.toggle("show_drilldown").set_value(False).run()
    assert application.exception.values == []
    assert zoom_widget_key not in application.session_state
    application.toggle("show_drilldown").set_value(True).run()
    assert application.exception.values == []
    assert _zoom_selectbox(application).value == DRILLDOWN_OUTLIER_FOCUS_OPTION
    assert application.session_state[RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY] == candidate_context

    _zoom_selectbox(application).select("off").run()
    assert application.exception.values == []
    assert RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY not in application.session_state
    application.run()
    assert application.exception.values == []
    assert _zoom_selectbox(application).value == "off"
    assert application.session_state["observed_focus_option"] == "off"


def test_scope_change_retires_candidate_focus_without_replacing_station_intent():
    application = _drilldown_application()
    selected_stations = application.session_state["val_results_selected_stations_compare"]

    application.selectbox("active_scope").select("r0_d0").run()

    assert application.exception.values == []
    assert RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY not in application.session_state
    assert _zoom_selectbox(application).value == "off"
    assert application.session_state["val_results_selected_stations_compare"] == selected_stations


def test_renderer_delegates_selection_state_mutation_to_its_owner():
    """Keep all Inspector views from duplicating selection-state ownership."""
    project_root = Path(__file__).resolve().parents[2]
    renderer_tree = ast.Module(body=[
        statement
        for module_name in (
            "segment_inspector", "inspector_scope", "inspector_stations",
            "inspector_selected", "inspector_outliers", "inspector_common",
            "inspector_export",
        )
        for statement in ast.parse(
            (project_root / f"ui/components/{module_name}.py").read_text(encoding="utf-8-sig")
        ).body
    ], type_ignores=[])
    selection_owner_tree = ast.parse(
        (project_root / "ui/inspector/selection_state.py").read_text(encoding="utf-8-sig")
    )

    def is_session_state_reference(expression):
        return (isinstance(expression, ast.Name) and expression.id == "session_state") or (
            isinstance(expression, ast.Attribute)
            and expression.attr == "session_state"
            and isinstance(expression.value, ast.Name)
            and expression.value.id == "st"
        )

    def is_cache_key(expression):
        return (
            isinstance(expression, ast.Name)
            and expression.id == "INSPECTOR_CACHE_STATE_KEY"
        ) or (
            isinstance(expression, ast.Constant)
            and expression.value == "segment_inspector_cache"
        )

    unexpected_mutations = []
    for node in ast.walk(renderer_tree):
        if isinstance(node, (ast.Assign, ast.Delete)):
            targets = node.targets
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        else:
            targets = []
        for target in targets:
            if isinstance(target, ast.Subscript) and is_session_state_reference(target.value):
                if not is_cache_key(target.slice):
                    unexpected_mutations.append((node.lineno, ast.unparse(target)))
            elif isinstance(target, ast.Attribute) and is_session_state_reference(target.value):
                if target.attr != "segment_inspector_cache":
                    unexpected_mutations.append((node.lineno, ast.unparse(target)))
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and is_session_state_reference(node.func.value)
            and node.func.attr in {"clear", "update", "pop", "popitem", "setdefault", "__setitem__", "__delitem__"}
        ):
            is_cache_mutation = (
                node.func.attr in {"pop", "setdefault", "__setitem__", "__delitem__"}
                and node.args
                and is_cache_key(node.args[0])
            )
            if not is_cache_mutation:
                unexpected_mutations.append((node.lineno, ast.unparse(node)))

    assert unexpected_mutations == [], (
        "Inspector selection mutation belongs in selection_state.py: "
        f"{unexpected_mutations}"
    )
    owner_function_names = {
        node.name for node in selection_owner_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    }
    duplicate_helpers = {
        node.name for node in renderer_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.lstrip("_") in owner_function_names
    }
    assert duplicate_helpers == set(), (
        f"Renderer duplicates selection-owner helpers: {sorted(duplicate_helpers)}"
    )
