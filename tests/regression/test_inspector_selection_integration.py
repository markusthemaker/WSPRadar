"""Streamlit rerun coverage for canonical Inspector state and candidate focus."""

import ast
from pathlib import Path

import pandas as pd
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
        False,
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
