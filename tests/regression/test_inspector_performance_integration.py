"""Performance selection rerenders retain prepared scope and avoid provider work."""

from types import SimpleNamespace

import pandas as pd

from i18n import T
from ui.components import (
    inspector_common, inspector_export, inspector_scope, inspector_selected,
    inspector_stations, segment_inspector,
)
from ui.inspector import preparation as inspector_preparation
from ui.inspector import selection_state as inspector_selection
from ui.inspector.contracts import InspectorContext, InspectorScope, ScopeControlsView
from ui.inspector.preparation import InspectorPreparation
from ui.plots import opportunity_figures
from ui.result_hierarchy import transition_prompt_html


def _set_component_streamlit(monkeypatch, streamlit_ui):
    """Give separately owned views one consistent fake Streamlit surface."""
    for component in (
        segment_inspector, inspector_common, inspector_scope,
        inspector_selected, inspector_stations,
    ):
        monkeypatch.setattr(component, "st", streamlit_ui)

def _patch_shared_render_dependency(monkeypatch, name, replacement):
    """Record the same presentation dependency in segment and selected views."""
    for component in (inspector_scope, inspector_selected, inspector_stations):
        if hasattr(component, name):
            monkeypatch.setattr(component, name, replacement)


def test_success_new_station_builds_after_segment_cache_hit_without_provider_request(
    monkeypatch,
):
    """Replace A with B, then clear, without rebuilding or querying the segment."""
    from core import data_engine

    class FakeContainer:
        """Provide the context/container surface used by the Performance inspector."""

        def __init__(self, fake_streamlit):
            self.fake_streamlit = fake_streamlit

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def markdown(self, *_args, **_kwargs):
            return None

        def columns(self, widths, **kwargs):
            self.fake_streamlit.column_calls.append((list(widths), kwargs))
            return tuple(FakeContainer(self.fake_streamlit) for _ in widths)

        def dataframe(self, *_args, **kwargs):
            self.fake_streamlit.dataframe_calls.append(dict(kwargs))
            on_select = kwargs.get("on_select")
            if callable(on_select):
                on_select()
            return SimpleNamespace(
                selection=SimpleNamespace(
                    rows=list(self.fake_streamlit.selected_rows)
                )
            )

    class FakeStreamlit:
        """Retain session cache state while exposing controlled table selections."""

        def __init__(self):
            self.session_state = {}
            self.selected_rows = [0]
            self.markdown_calls = []
            self.column_calls = []
            self.dataframe_calls = []

        def container(self, **_kwargs):
            return FakeContainer(self)

        def columns(self, widths, **kwargs):
            self.column_calls.append((list(widths), kwargs))
            return tuple(FakeContainer(self) for _ in widths)

        def markdown(self, body, **kwargs):
            self.markdown_calls.append((body, kwargs))
            return None

        def toggle(self, *_args, **_kwargs):
            return False

        def popover(self, *_args, **_kwargs):
            return FakeContainer(self)

        def multiselect(self, *_args, **_kwargs):
            return []

        def selectbox(self, _label, options, *, key, **_kwargs):
            return self.session_state.get(key, options[0])

        def caption(self, *_args, **_kwargs):
            return None

    fake_streamlit = FakeStreamlit()
    fake_streamlit.session_state[
        inspector_selection.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY
    ] = "2h"
    _set_component_streamlit(monkeypatch, fake_streamlit)

    provider_requests = []

    def reject_provider_request(*args, **kwargs):
        provider_requests.append((args, kwargs))
        raise AssertionError("Inspector rerenders must not contact a provider.")

    monkeypatch.setattr(
        data_engine.http_session,
        "get",
        reject_provider_request,
    )
    monkeypatch.setattr(
        inspector_preparation,
        'log_performance_event',
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        inspector_stations,
        "supports_dataframe_selection_default",
        lambda: False,
    )
    _patch_shared_render_dependency(monkeypatch, 'render_result_guidance_popover', lambda *_args, **_kwargs: None)
    selected_render_calls = []

    def record_cached_recipe(_recipe, **kwargs):
        if str(kwargs.get("subject", "")).startswith(
            "opportunity selected"
        ):
            selected_render_calls.append(
                {"recipe": _recipe, **kwargs}
            )
        return None

    _patch_shared_render_dependency(monkeypatch, 'render_cached_recipe', record_cached_recipe)
    monkeypatch.setattr(
        inspector_scope,
        'render_segment_temporal_evidence',
        lambda *_args, **_kwargs: None,
    )
    _patch_shared_render_dependency(monkeypatch, 'render_prompted_segment_time_bin_control', lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        inspector_selected,
        "selected_success_context_line",
        lambda *_args, **_kwargs: "Selected station context",
    )
    drilldown_builds = []
    drilldown_renders = []
    export_calls = []

    def record_drilldown_build(
        _parquet_path,
        selected_meta,
        selected_station_column,
        selected_locator_column,
        *_args,
        station_rows_df,
        **_kwargs,
    ):
        selected_identities = tuple(
            selected_meta[
                [selected_station_column, selected_locator_column]
            ].itertuples(index=False, name=None)
        )
        evidence_identities = tuple(
            station_rows_df[
                ["peer_sign", "peer_grid"]
            ].itertuples(index=False, name=None)
        )
        drilldown_builds.append(
            {
                "selected_identities": selected_identities,
                "evidence_identities": evidence_identities,
            }
        )
        return (
            pd.DataFrame(
                {
                    "Selected station": [
                        selected_identities[0][0]
                    ]
                }
            ),
            None,
        )

    def record_drilldown_render(
        drilldown_table,
        selected_station_labels,
        *_args,
        **_kwargs,
    ):
        drilldown_renders.append(
            {
                "labels": tuple(selected_station_labels),
                "stations": tuple(
                    drilldown_table["Selected station"].astype(str)
                ),
            }
        )
        return drilldown_table

    monkeypatch.setattr(
        inspector_preparation,
        '_build_drilldown_table',
        record_drilldown_build,
    )
    monkeypatch.setattr(
        inspector_selected,
        'render_drilldown_dataframe',
        record_drilldown_render,
    )
    monkeypatch.setattr(
        inspector_export,
        "register_inspector_export",
        lambda payload, **kwargs: export_calls.append({
            **payload.to_registration_values(), **kwargs,
        }),
    )

    station_column = "RX Station"
    locator_column = "Locator"
    distance_column = "km"
    azimuth_column = "Azimuth"
    hit_column = "Heard by Target"
    station_table = pd.DataFrame(
        {
            station_column: [
                "A1AAA",
                "B2BBB",
                "C3CCC",
                "D4DDD",
                "E5EEE",
                "F6FFF",
            ],
            locator_column: [
                "AA00",
                "BB11",
                "CC22",
                "DD33",
                "EE44",
                "FF55",
            ],
            distance_column: [100.0, 200.0, 300.0, 400.0, 500.0, 600.0],
            azimuth_column: [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
            hit_column: [1, 1, 1, 1, 1, 1],
        }
    )
    opportunity_view_model = SimpleNamespace(
        summary_lines=[],
        confirmed_station_count=6,
        confirmed_opportunity_count=6,
        full_station_table=station_table,
        export_column_renames={},
        station_column=station_column,
        locator_column=locator_column,
        distance_column=distance_column,
        azimuth_column=azimuth_column,
        hit_column=hit_column,
        export_station_column=station_column,
        export_locator_column=locator_column,
        confirmed_rows=pd.DataFrame(),
    )
    monkeypatch.setattr(
        inspector_preparation,
        "build_opportunity_inspector_view_model",
        lambda *_args, **_kwargs: opportunity_view_model,
    )
    monkeypatch.setattr(
        inspector_preparation,
        "_opportunity_segment_recipe",
        lambda *_args, **_kwargs: {"kind": "segment"},
    )
    selected_recipe_builds = []

    def build_temporal_recipe(
        evidence_title,
        _selected_segment,
        peer_rows,
        temporal_evidence_rows,
        *_args,
        snr_title,
        population_mode,
        snr_representation,
        **_kwargs,
    ):
        if (
            population_mode
            == opportunity_figures.SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
        ):
            selected_recipe_builds.append(
                {
                    "peer_identities": tuple(
                        peer_rows[
                            ["peer_sign", "peer_grid"]
                        ].itertuples(index=False, name=None)
                    ),
                    "evidence_identities": tuple(
                        temporal_evidence_rows[
                            ["peer_sign", "peer_grid"]
                        ].itertuples(index=False, name=None)
                    ),
                    "population_mode": population_mode,
                    "snr_representation": snr_representation,
                }
            )
        return {
            "evidence_title": evidence_title,
            "snr_title": snr_title,
            "time_bin_options": ["1h", "2h"],
            "time_bin_default": "1h",
            "population_mode": population_mode,
            "snr_representation": snr_representation,
        }

    monkeypatch.setattr(
        inspector_preparation,
        '_opportunity_temporal_recipe',
        build_temporal_recipe,
    )

    evidence_rows = pd.DataFrame(
        {
            "time_slot": [1, 1, 1, 1, 1, 1],
            "peer_sign": [
                "A1AAA",
                "B2BBB",
                "C3CCC",
                "D4DDD",
                "E5EEE",
                "F6FFF",
            ],
            "peer_grid": [
                "AA00",
                "BB11",
                "CC22",
                "DD33",
                "EE44",
                "FF55",
            ],
            "hit": [1, 1, 1, 1, 1, 1],
            "miss": [0, 0, 0, 0, 0, 0],
            "target_snr": [-10.0, -11.0, -12.0, -13.0, -14.0, -15.0],
        }
    )
    segment_read_count = 0

    def read_segment_rows(*_args, **_kwargs):
        nonlocal segment_read_count
        segment_read_count += 1
        return evidence_rows.copy()

    monkeypatch.setattr(
        inspector_preparation,
        "read_parquet_artifact",
        read_segment_rows,
    )

    selected_station_loads = []

    def load_selected_station_rows(
        _parquet_path,
        selected_meta,
        selected_station_column,
        selected_locator_column,
        *,
        columns,
    ):
        del columns
        selected_pairs = [
            (str(callsign), str(locator))
            for callsign, locator in selected_meta[
                [selected_station_column, selected_locator_column]
            ].itertuples(index=False, name=None)
        ]
        selected_station_loads.append(
            tuple(callsign for callsign, _locator in selected_pairs)
        )
        return pd.DataFrame(
            {
                "time_slot": list(range(1, len(selected_pairs) + 1)),
                "peer_sign": [
                    callsign for callsign, _locator in selected_pairs
                ],
                "peer_grid": [
                    locator for _callsign, locator in selected_pairs
                ],
                "hit": [1] * len(selected_pairs),
                "miss": [0] * len(selected_pairs),
                "target_only": [0] * len(selected_pairs),
                "target_snr": [
                    -10.0 - row_index
                    for row_index in range(len(selected_pairs))
                ],
            }
        )

    monkeypatch.setattr(
        inspector_preparation,
        '_load_station_rows_for_drilldown',
        load_selected_station_rows,
    )

    cache_events = []
    original_cache_get = InspectorPreparation.cache_get

    def recording_cache_get(self, namespace, key, *, item=""):
        cached_value, is_cache_hit = original_cache_get(
            self, namespace, key, item=item,
        )
        if namespace in {"segment", "selected"}:
            cache_events.append((namespace, is_cache_hit))
        return cached_value, is_cache_hit

    monkeypatch.setattr(
        InspectorPreparation,
        'cache_get',
        recording_cache_get,
    )

    analysis_start = pd.Timestamp("2026-07-01T00:00:00Z")
    analysis_end = pd.Timestamp("2026-07-01T02:00:00Z")
    analysis_context = SimpleNamespace(
        min_confirmed_opportunities_per_peer=1,
        callsign="G3ZIL",
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )
    opportunity_terms = {
        "mode": "RX",
        "show_counter": "Heard only by other stations.",
    }
    presentation_context = SimpleNamespace(
        language="en",
        theme="dark",
        absolute_terms=lambda _mode: opportunity_terms,
    )
    scope_rows = pd.DataFrame(
        {
            "peer_sign": [
                "A1AAA",
                "B2BBB",
                "C3CCC",
                "D4DDD",
                "E5EEE",
                "F6FFF",
            ],
            "peer_grid": [
                "AA00",
                "BB11",
                "CC22",
                "DD33",
                "EE44",
                "FF55",
            ],
        }
    )
    level_two_container = FakeContainer(fake_streamlit)
    scope_summary_placeholder = FakeContainer(fake_streamlit)
    context = InspectorContext(
        analysis_id="RX_ABS",
        title="RX Performance",
        is_compare=False,
        is_sequential=False,
        parquet_path="unused-session-artifact.parquet",
        line1_str="audit",
        translations=T["en"],
        max_peer_distance_km=1000.0,
        analysis_context=analysis_context,
        presentation_context=presentation_context,
        analysis_kind="opportunity",
        run_id=101,
        analysis_start_t=analysis_start,
        analysis_end_t=analysis_end,
    )
    scope = InspectorScope(
        selected_ranges=(),
        selected_directions=(),
        range_summary="Full Range",
        direction_summary="All Directions",
        selected_segment="Full Range | All Directions",
        active_scope_summary="Full Range | All Directions",
        scope_token="rall_dall",
        distance_scope_intervals=((0.0, 1000.0),),
    )
    # The existing regression starts at an already chosen scope. Keep real
    # preparation, station controls, selected rendering, and export registration.
    monkeypatch.setattr(
        segment_inspector, "render_scope_controls",
        lambda *_args, **_kwargs: ScopeControlsView(
            scope=scope,
            level_two_container=level_two_container,
            scope_summary_placeholder=scope_summary_placeholder,
        ),
    )
    monkeypatch.setattr(
        InspectorPreparation, "touch_artifact", lambda *_args: None,
    )
    monkeypatch.setattr(
        InspectorPreparation, "prepare_options",
        lambda *_args, **_kwargs: SimpleNamespace(
            valid_distances=("Full Range",), valid_directions=("All Directions",),
        ),
    )
    monkeypatch.setattr(
        InspectorPreparation, "success_distance_scope_intervals",
        staticmethod(lambda *_args, **_kwargs: scope.distance_scope_intervals),
    )
    monkeypatch.setattr(
        InspectorPreparation, "filter_scope_rows",
        staticmethod(lambda *_args, **_kwargs: scope_rows),
    )
    monkeypatch.setattr(
        inspector_selected, "render_page_anchor", lambda *_args: None,
    )

    persisted_success_selections = []
    for selected_rows in ([0], [1], []):
        fake_streamlit.selected_rows = list(selected_rows)
        segment_inspector.render_inspector_page(
            context, scope_rows, session_state=fake_streamlit.session_state,
        )
        persisted_success_selections.append(
            [
                dict(identity)
                for identity in fake_streamlit.session_state[
                    inspector_selection.RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY
                ]
            ]
        )

    assert cache_events == [
        ("segment", False),
        ("selected", False),
        ("segment", True),
        ("selected", False),
        ("segment", True),
    ]
    assert segment_read_count == 1
    assert selected_station_loads == [
        ("A1AAA",),
        ("B2BBB",),
    ]
    assert [
        recipe_build["peer_identities"]
        for recipe_build in selected_recipe_builds
    ] == [
        (("A1AAA", "AA00"),),
        (("B2BBB", "BB11"),),
    ]
    assert [
        recipe_build["evidence_identities"]
        for recipe_build in selected_recipe_builds
    ] == [
        (("A1AAA", "AA00"),),
        (("B2BBB", "BB11"),),
    ]
    assert all(
        recipe_build["population_mode"]
        == opportunity_figures.SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
        for recipe_build in selected_recipe_builds
    )
    assert all(
        recipe_build["snr_representation"]
        == opportunity_figures.SUCCESS_SNR_REPRESENTATION_ACTUAL
        for recipe_build in selected_recipe_builds
    )
    assert drilldown_builds == [
        {
            "selected_identities": (("A1AAA", "AA00"),),
            "evidence_identities": (("A1AAA", "AA00"),),
        },
        {
            "selected_identities": (("B2BBB", "BB11"),),
            "evidence_identities": (("B2BBB", "BB11"),),
        },
    ]
    assert drilldown_renders == [
        {
            "labels": ("A1AAA (AA00)",),
            "stations": ("A1AAA",),
        },
        {
            "labels": ("B2BBB (BB11)",),
            "stations": ("B2BBB",),
        },
    ]
    assert persisted_success_selections == [
        [{"callsign": "A1AAA", "locator": "AA00"}],
        [{"callsign": "B2BBB", "locator": "BB11"}],
        [],
    ]
    assert [
        render_call["render_figure"]
        for render_call in selected_render_calls
    ] == [
        inspector_scope.render_segment_temporal_snr_export_figure,
        inspector_scope.render_segment_temporal_evidence_export_figure,
        inspector_scope.render_segment_temporal_snr_export_figure,
        inspector_scope.render_segment_temporal_evidence_export_figure,
    ]
    assert [
        render_call["recipe"]["time_bin"]
        for render_call in selected_render_calls
    ] == ["2h", "2h", "2h", "2h"]
    assert [
        dataframe_call["selection_mode"]
        for dataframe_call in fake_streamlit.dataframe_calls
    ] == ["single-row", "single-row", "single-row"]
    assert all(
        callable(dataframe_call["on_select"])
        for dataframe_call in fake_streamlit.dataframe_calls
    )
    assert all(
        dataframe_call["height"]
        == inspector_common.COMPACT_DATAFRAME_HEIGHT_PX
        for dataframe_call in fake_streamlit.dataframe_calls
    )
    assert all(
        dataframe_call["row_height"]
        == inspector_common.COMPACT_DATAFRAME_ROW_HEIGHT_PX
        for dataframe_call in fake_streamlit.dataframe_calls
    )
    assert (
        list(
            inspector_stations.SUCCESS_STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS
        ),
        {"vertical_alignment": "center"},
    ) in fake_streamlit.column_calls
    assert (
        inspector_stations.SUCCESS_STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS
        == (9, 2)
    )
    assert all(
        "Heard by Target | Heard by others only" not in markdown_body
        for markdown_body, _kwargs in fake_streamlit.markdown_calls
    )
    assert (
        [0.64, 0.36],
        {"vertical_alignment": "top"},
    ) not in fake_streamlit.column_calls
    assert [
        tuple(export_call["selected_stations"])
        for export_call in export_calls
    ] == [
        ("A1AAA (AA00)",),
        ("B2BBB (BB11)",),
        (),
    ]
    assert [
        export_call["selected_station_snr_evidence_figure_recipe"] is not None
        for export_call in export_calls
    ] == [True, True, False]
    assert [
        export_call[
            "selected_station_temporal_evidence_figure_recipe"
        ] is not None
        for export_call in export_calls
    ] == [True, True, False]
    assert all(
        export_call["selected_evidence_figure_recipe"] is None
        for export_call in export_calls
    )
    assert [
        tuple(
            export_call["drilldown_selected_df"][
                "Selected station"
            ].astype(str)
        )
        if not export_call["drilldown_selected_df"].empty
        else ()
        for export_call in export_calls
    ] == [
        ("A1AAA",),
        ("B2BBB",),
        (),
    ]
    assert (
        fake_streamlit.session_state[
            inspector_selection.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY
        ]
        == "2h"
    )
    assert (
        fake_streamlit.session_state[
            inspector_selection.RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY
        ]
        == []
    )
    assert provider_requests == []
