"""Explicit context and rendering ownership at Inspector component boundaries."""

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from ui.components import inspector_common, inspector_outliers
from ui.page_navigation import DRILLDOWN_ANCHOR_ID, STATION_INSIGHTS_ANCHOR_ID


@pytest.mark.parametrize(("button_prefix", "expected_anchor"), [
    ("show_outlier_station_", STATION_INSIGHTS_ANCHOR_ID),
    ("show_outlier_drilldown_", DRILLDOWN_ANCHOR_ID),
])
def test_outlier_navigation_delegates_the_supplied_session_to_its_owner(
    monkeypatch, button_prefix, expected_anchor,
):
    """A view cannot silently discover a different session when an action fires."""
    supplied_state = {"run_id": 7}
    candidate = object()
    outlier_model = object()
    navigation_calls = []
    rerun_calls = []

    class ActionContainer:
        def container(self, **_kwargs):
            return self

        def button(self, _label, *, key, **_kwargs):
            return key.startswith(button_prefix)

    def select_candidate(selected_candidate, selected_model, session_state, **context):
        navigation_calls.append((selected_candidate, selected_model, session_state, context))

    monkeypatch.setattr(
        inspector_outliers,
        "st",
        SimpleNamespace(rerun=lambda **kwargs: rerun_calls.append(kwargs)),
    )
    monkeypatch.setattr(
        inspector_outliers.inspector_selection, "select_outlier_candidate", select_candidate,
    )

    inspector_outliers.render_outlier_candidate_navigation(
        ActionContainer(),
        candidate,
        outlier_model,
        session_state=supplied_state,
        candidate_key_suffix="candidate-1",
        analysis_id="RX_COMP",
        run_id=7,
        scope_token="rall_dall",
        translations={
            "btn_outlier_show_path_in_station_insights": "Show station",
            "btn_outlier_show_drilldown_details": "Show details",
        },
    )

    assert len(navigation_calls) == 1
    selected_candidate, selected_model, selected_state, context = navigation_calls[0]
    assert selected_candidate is candidate
    assert selected_model is outlier_model
    assert selected_state is supplied_state
    assert context == {
        "analysis_id": "RX_COMP",
        "run_id": 7,
        "scope_token": "rall_dall",
        "navigation_anchor_id": expected_anchor,
    }
    assert rerun_calls == [{"scope": "app"}]


def test_cached_recipe_disposes_its_figure_when_presentation_fails(monkeypatch):
    """A failed view render must release Matplotlib ownership and cache nothing."""
    figure = object()
    disposed_figures = []
    cache_writes = []
    preparation = SimpleNamespace(
        timing_collector=None,
        cache_get=lambda *_args, **_kwargs: (None, False),
        cache_put=lambda *args, **kwargs: cache_writes.append((args, kwargs)),
    )

    def fail_render(_figure, **_kwargs):
        raise RuntimeError("render failed")

    monkeypatch.setattr(inspector_common, "get_matplotlib_render_mode", lambda: "image")
    monkeypatch.setattr(inspector_common, "render_matplotlib_figure", fail_render)
    monkeypatch.setattr(inspector_common, "dispose_matplotlib_figure", disposed_figures.append)

    with pytest.raises(RuntimeError, match="render failed"):
        inspector_common.render_cached_recipe(
            {},
            preparation=preparation,
            cache_key=("selected-path",),
            subject="selected evidence",
            build_label="build selected evidence",
            render_figure=lambda _recipe: figure,
        )

    assert disposed_figures == [figure]
    assert cache_writes == []


def test_view_components_do_not_discover_global_session_state():
    """View components receive state owners or mappings through explicit inputs."""
    project_root = Path(__file__).resolve().parents[2]
    for module_name in (
        "inspector_common.py", "inspector_outliers.py", "inspector_scope.py",
        "inspector_stations.py", "inspector_selected.py", "inspector_export.py",
    ):
        source_path = project_root / "ui/components" / module_name
        module_tree = ast.parse(source_path.read_text(encoding="utf-8-sig"))
        discovered_state = [
            node.lineno for node in ast.walk(module_tree)
            if isinstance(node, ast.Attribute)
            and node.attr == "session_state"
            and isinstance(node.value, ast.Name)
            and node.value.id == "st"
        ]
        assert discovered_state == [], f"{module_name} discovers session state at {discovered_state}"

        artifact_reads = [
            node.lineno for node in ast.walk(module_tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {
                "read_parquet_artifact", "_load_station_rows_for_drilldown",
                "_build_segment_compare_units", "_build_compare_unit_rows",
                "build_opportunity_inspector_view_model", "build_compare_inspector_view_model",
            }
        ]
        assert artifact_reads == [], f"{module_name} independently prepares evidence at {artifact_reads}"
