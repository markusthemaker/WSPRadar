"""Selected-station evidence and Drill-Down presentation components.

The enclosing inspector owns the sole Streamlit fragment. These views receive
prepared evidence and explicit state for the selection/navigation adapter.
"""

from collections.abc import Mapping
from datetime import timedelta
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
import streamlit as st

from ui.components.inspector_common import (
    format_snr_display_columns,
    render_compact_dataframe,
    render_cached_recipe,
    render_prompted_segment_time_bin_control,
    render_reference_correction_notice,
    timed_span,
)
from ui.inspector import selection_state as inspector_selection
from ui.inspector.selection import InspectorSelection
from ui.inspector.drilldown import opportunity_drilldown_display_table
from ui.inspector.drilldown_focus import (
    DRILLDOWN_OUTLIER_FOCUS_OPTION,
    resolve_centered_zoom_window,
    resolve_outlier_focus_window,
)
from ui.inspector.presentation import (
    format_drilldown_focus_utc,
    drilldown_focus_time_bin,
    selected_success_context_line,
)
from ui.inspector.preparation import (
    INSPECTOR_CACHE_VERSION,
)
from ui.page_navigation import DRILLDOWN_ANCHOR_ID, render_page_anchor
from ui.plots.evidence_figures import (
    render_selected_evidence_export_figure,
    render_segment_temporal_evidence_export_figure,
    render_segment_temporal_snr_export_figure,
)
from ui.plots.drilldown_zoom_figures import (
    DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
    render_drilldown_zoom_benchmark_coverage_figure,
    render_drilldown_zoom_benchmark_delta_snr_figure,
    render_drilldown_zoom_performance_evidence_figure,
    render_drilldown_zoom_performance_snr_figure,
)
from ui.plots.benchmark_evidence_figures import render_selected_compare_coverage_export_figure
from ui.result_hierarchy import (
    drilldown_subtitle,
    evidence_level_header_html,
    scope_context_html,
    selected_station_context,
    transition_prompt_html,
)
from ui.result_guidance import (
    RESULT_GUIDANCE_DRILLDOWN,
    RESULT_GUIDANCE_SELECTED_STATIONS,
    render_result_guidance_popover,
)


@dataclass(slots=True)
class SelectedStationView:
    """Selected-view outputs retained for the existing export assembly."""

    selected_station_labels: list[str] = field(default_factory=list)
    selected_evidence_export: Any = None
    selected_evidence_recipe: Any = None
    selected_station_snr_evidence_recipe: Any = None
    selected_station_temporal_evidence_recipe: Any = None
    selected_station_label_text: str | None = None
    selected_station_context_text: str | None = None
    selected_evidence_figure_descriptions: dict[str, str] = field(default_factory=dict)
    selected_time_bin: str | None = None
    drilldown_selected_df: Any = field(default_factory=pd.DataFrame)
    drilldown_zoom_metadata: Any = None
    drilldown_zoom_performance_snr_recipe: Any = None
    drilldown_zoom_performance_evidence_recipe: Any = None
    drilldown_zoom_benchmark_delta_recipe: Any = None
    drilldown_zoom_benchmark_coverage_recipe: Any = None


def render_drilldown_heading(
    selected_station_labels,
    analysis_id,
    run_id,
    scope_token,
    translations,
    is_compare,
    is_sequential,
    analysis_context,
    language,
    *,
    allow_multiple_station_selection,
):
    """Render the one canonical Drill-Down heading and guidance placement."""
    drilldown_title = translations["hdr_results_drilldown"]
    st.markdown(
        evidence_level_header_html(
            5,
            translations["lbl_results_level_rows"],
            drilldown_title,
            drilldown_subtitle(
                selected_station_labels,
                analysis_id,
                translations,
                allow_multiple=allow_multiple_station_selection,
            ),
        ),
        unsafe_allow_html=True,
    )
    render_result_guidance_popover(
        RESULT_GUIDANCE_DRILLDOWN,
        drilldown_title,
        language=language,
        translations=translations,
        key=(
            f"results_guidance_drilldown_"
            f"{analysis_id}_{run_id}_{scope_token}"
        ),
        analysis_id=analysis_id,
        is_compare=is_compare,
        is_sequential=is_sequential,
        analysis_context=analysis_context,
    )
    normalization_note = translations["txt_snr_values_normalized_30dbm"]
    filter_note = translations["txt_results_drilldown_filter_note"]
    st.markdown(
        scope_context_html(f"{filter_note} · {normalization_note}"),
        unsafe_allow_html=True,
    )


def render_drilldown_header_and_controls(
    selected_station_labels,
    analysis_id,
    run_id,
    scope_token,
    translations,
    is_compare,
    is_sequential,
    analysis_context,
    language,
    *,
    session_state,
    analysis_start_utc,
    analysis_end_utc,
    selected_identity=None,
    allow_multiple_station_selection=False,
):
    """Render plot-focus controls; the table owns its separate filter row."""
    render_page_anchor(DRILLDOWN_ANCHOR_ID)
    render_drilldown_heading(
        selected_station_labels,
        analysis_id,
        run_id,
        scope_token,
        translations,
        is_compare,
        is_sequential,
        analysis_context,
        language,
        allow_multiple_station_selection=allow_multiple_station_selection,
    )

    if selected_identity is None:
        if allow_multiple_station_selection:
            st.markdown(
                scope_context_html(
                    translations["txt_drilldown_zoom_single_station_only"]
                ),
                unsafe_allow_html=True,
            )
        return None, None, None

    controls = inspector_selection.prepare_drilldown_controls(
        session_state,
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
        selected_identity=selected_identity,
        analysis_start_utc=analysis_start_utc,
        analysis_end_utc=analysis_end_utc,
    )
    outlier_context = controls.outlier_context
    available_options = controls.available_options
    zoom_state_keys = controls.keys
    widget_scope = zoom_state_keys.widget_scope
    zoom_key = zoom_state_keys.zoom_widget
    focus_date_key = zoom_state_keys.focus_date_widget
    focus_time_key = zoom_state_keys.focus_time_widget

    zoom_container, selected_window_container = st.columns(
        [0.28, 0.72],
        vertical_alignment="center",
    )
    option_labels = {
        "off": translations["lbl_drilldown_zoom_off"],
        DRILLDOWN_OUTLIER_FOCUS_OPTION: translations[
            "lbl_drilldown_zoom_outlier_focus"
        ],
    }
    with zoom_container:
        selected_option = st.selectbox(
            translations["lbl_drilldown_zoom_window"],
            available_options,
            format_func=lambda option: option_labels.get(option, option),
            key=zoom_key,
        )

    focus_window = None
    if selected_option == DRILLDOWN_OUTLIER_FOCUS_OPTION:
        if outlier_context is not None:
            focus_window = resolve_outlier_focus_window(
                analysis_start_utc,
                analysis_end_utc,
                outlier_context,
            )
    elif selected_option != "off":
        earliest_center, latest_center = (
            inspector_selection.prepare_manual_focus_center(
                session_state,
                zoom_keys=zoom_state_keys,
                selected_option=selected_option,
                outlier_context=outlier_context,
                analysis_start_utc=analysis_start_utc,
                analysis_end_utc=analysis_end_utc,
            )
        )
        (
            center_date_container,
            center_time_container,
            earlier_container,
            later_container,
            _manual_control_spacer,
        ) = st.columns(
            [0.24, 0.20, 0.12, 0.12, 0.32],
            vertical_alignment="bottom",
        )
        with earlier_container:
            st.button(
                translations["btn_drilldown_zoom_earlier"],
                key=f"d_zoom_earlier_{widget_scope}",
                type="tertiary",
                on_click=inspector_selection.shift_drilldown_focus_center_state,
                args=(
                    session_state,
                    focus_date_key,
                    focus_time_key,
                    analysis_start_utc,
                    analysis_end_utc,
                    selected_option,
                    -1,
                ),
            )
        with later_container:
            st.button(
                translations["btn_drilldown_zoom_later"],
                key=f"d_zoom_later_{widget_scope}",
                type="tertiary",
                on_click=inspector_selection.shift_drilldown_focus_center_state,
                args=(
                    session_state,
                    focus_date_key,
                    focus_time_key,
                    analysis_start_utc,
                    analysis_end_utc,
                    selected_option,
                    1,
                ),
            )
        with center_date_container:
            selected_focus_date = st.date_input(
                translations["lbl_drilldown_center_date_utc"],
                min_value=earliest_center.date(),
                max_value=latest_center.date(),
                key=focus_date_key,
                on_change=inspector_selection.normalize_drilldown_focus_center_state,
                args=(
                    session_state,
                    focus_date_key,
                    focus_time_key,
                    analysis_start_utc,
                    analysis_end_utc,
                    selected_option,
                ),
            )
        with center_time_container:
            selected_focus_time = st.time_input(
                translations["lbl_drilldown_center_time_utc"],
                step=timedelta(minutes=2),
                key=focus_time_key,
                on_change=inspector_selection.normalize_drilldown_focus_center_state,
                args=(
                    session_state,
                    focus_date_key,
                    focus_time_key,
                    analysis_start_utc,
                    analysis_end_utc,
                    selected_option,
                ),
            )
        selected_center = inspector_selection.drilldown_focus_center_from_widget_values(
            selected_focus_date,
            selected_focus_time,
        )
        focus_window = resolve_centered_zoom_window(
            analysis_start_utc,
            analysis_end_utc,
            selected_option,
            selected_center,
        )
    inspector_selection.finish_drilldown_option(
        session_state,
        zoom_state_keys,
        selected_option,
    )
    if focus_window is not None:
        selected_window_text = translations[
            "fmt_drilldown_zoom_selected_window"
        ].format(
            start=format_drilldown_focus_utc(focus_window.start_utc),
            end=format_drilldown_focus_utc(focus_window.end_utc),
        )
        selected_window_display = selected_window_container.container(
            key=f"d_zoom_selected_window_{widget_scope}",
        )
        selected_window_display.caption(selected_window_text)

    focus_time_bin = drilldown_focus_time_bin(focus_window)
    return focus_window, focus_time_bin, None


def render_drilldown_dataframe(
    drill_df,
    selected_station_labels,
    analysis_id,
    run_id,
    scope_token,
    t,
    is_compare,
    is_sequential,
    analysis_context,
    language,
    allow_multiple_station_selection=False,
    timing_collector=None,
    filter_container=None,
    render_header=True,
):
    """Render selected drill-down rows with local filters and return the displayed dataframe."""
    if drill_df is None or drill_df.empty:
        return pd.DataFrame()
    canonical_drill_df = drill_df.copy()
    display_drill_df = (
        drill_df.copy()
        if is_compare
        else opportunity_drilldown_display_table(
            drill_df,
            t,
            analysis_id,
        )
    )

    if render_header:
        render_drilldown_heading(
            selected_station_labels,
            analysis_id,
            run_id,
            scope_token,
            t,
            is_compare,
            is_sequential,
            analysis_context,
            language,
            allow_multiple_station_selection=(
                allow_multiple_station_selection
            ),
        )
    if filter_container is None:
        _filter_spacer, filter_container = st.columns(
            [0.7, 0.3],
            vertical_alignment="center",
        )
    with filter_container:
        with st.popover(
            t["lbl_filter_table"],
            icon=":material/filter_alt:",
            width="stretch",
        ):
            st.markdown(f"**{t['lbl_filter_columns']}**")
            d_filter_cols = st.multiselect(
                t["lbl_select_columns"],
                display_drill_df.columns,
                label_visibility="collapsed",
                key=f"d_flt_{analysis_id}_{run_id}_{scope_token}"
            )

            for col in d_filter_cols:
                if pd.api.types.is_numeric_dtype(display_drill_df[col]):
                    min_val = float(display_drill_df[col].min())
                    max_val = float(display_drill_df[col].max())
                    if min_val < max_val:
                        step = 1.0 if pd.api.types.is_integer_dtype(display_drill_df[col]) else 0.1
                        sel_range = st.slider(
                            f"{col}",
                            min_val,
                            max_val,
                            (min_val, max_val),
                            step=step,
                            key=f"d_sld_{col}_{analysis_id}_{run_id}_{scope_token}"
                        )
                        display_drill_df = display_drill_df[
                            display_drill_df[col].between(
                                sel_range[0],
                                sel_range[1],
                            )
                        ]
                else:
                    unique_vals = (
                        display_drill_df[col]
                        .astype(str)
                        .dropna()
                        .unique()
                    )
                    sel_vals = st.multiselect(
                        f"{col}",
                        unique_vals,
                        default=[],
                        key=f"d_ms_{col}_{analysis_id}_{run_id}_{scope_token}"
                    )
                    if sel_vals:
                        display_drill_df = display_drill_df[
                            display_drill_df[col].astype(str).isin(sel_vals)
                        ]

    render_reference_correction_notice(
        t,
        is_compare=is_compare,
        is_sequential=is_sequential,
        analysis_context=analysis_context,
    )
    with timed_span(timing_collector, "drilldown dataframe render"):
        drill_display_df = format_snr_display_columns(display_drill_df)
        render_compact_dataframe(
            st,
            drill_display_df,
            width="stretch",
            hide_index=True,
        )
    return canonical_drill_df.loc[display_drill_df.index].copy()


def render_selected_station_evidence(
    prepared_evidence,
    selected_identity_df,
    *,
    selection: InspectorSelection,
    session_state,
    preparation,
    t,
    analysis_context,
    language,
    is_sequential,
    outlier_model=None,
):
    """Render pooled Benchmark evidence from the coordinator's compact model."""
    if prepared_evidence is None:
        return None
    selected_bundle = prepared_evidence.bundle
    cache_key = prepared_evidence.cache_key
    analysis_id = selection.analysis_id
    run_id = selection.run_id
    scope_token = selection.scope_token
    identity_labels = list(selected_bundle["identity_labels"])
    evidence_count = int(selected_bundle["evidence_count"])
    comparison_unit_count = int(
        selected_bundle.get("comparison_unit_count", 0)
    )
    selected_station_count = int(
        selected_bundle.get("selected_station_count", len(identity_labels))
    )
    selected_evidence_heading = t["hdr_results_selected_station_evidence"]
    st.markdown(
        evidence_level_header_html(
            4,
            t[
                "lbl_results_level_selection_success"
                if selected_station_count == 1
                else "lbl_results_level_selection"
            ],
            selected_evidence_heading,
            selected_station_context(
                identity_labels,
                evidence_count,
                analysis_id=analysis_id,
                is_sequential=is_sequential,
                translations=t,
                allow_multiple=(outlier_model is not None),
            ),
        ),
        unsafe_allow_html=True,
    )
    render_result_guidance_popover(
        RESULT_GUIDANCE_SELECTED_STATIONS,
        selected_evidence_heading,
        language=language,
        translations=t,
        key=(
            f"results_guidance_selected_stations_"
            f"{analysis_id}_{run_id}_{scope_token}"
        ),
        analysis_id=analysis_id,
        is_compare=True,
        is_sequential=is_sequential,
        analysis_context=analysis_context,
        selected_station_count=selected_station_count,
        allows_multiple_station_selection=(outlier_model is not None),
    )
    if evidence_count == 0:
        st.markdown(
            scope_context_html(
                t["txt_results_selected_no_paired_evidence"]
            ),
            unsafe_allow_html=True,
        )
    if selected_bundle.get("coverage_recipe") is None:
        coverage_unavailable_key = (
            "fig_selected_compare_coverage_unavailable_multi"
            if selected_station_count > 1
            else "fig_selected_compare_coverage_unavailable"
        )
        st.markdown(
            scope_context_html(
                t[coverage_unavailable_key]
            ),
            unsafe_allow_html=True,
        )

    time_agg_options = list(selected_bundle["time_agg_options"])
    time_agg_default = selected_bundle["time_agg_default"]
    agg_key = (
        f"evidence_time_agg_{analysis_id}_{run_id}_{scope_token}_"
        f"{is_sequential}"
    )
    persistent_time_bin_key = inspector_selection.time_bin_persistent_state_key(True)
    inspector_selection.initialize_time_bin_widget_state(
        session_state,
        agg_key,
        persistent_time_bin_key,
        time_agg_options,
        time_agg_default,
    )

    render_prompted_segment_time_bin_control(
        t["lbl_selected_time_aggregation_bin_size"],
        time_agg_options,
        agg_key,
        on_change=inspector_selection.sync_time_bin_widget_state,
        on_change_args=(
            session_state,
            agg_key,
            persistent_time_bin_key,
            tuple(time_agg_options),
            time_agg_default,
        ),
    )
    time_agg = inspector_selection.sync_time_bin_widget_state(
        session_state,
        agg_key,
        persistent_time_bin_key,
        time_agg_options,
        time_agg_default,
    )

    evidence_title = selected_bundle["title"]
    selected_recipe = None
    if selected_bundle.get("base_recipe") is not None:
        selected_recipe = dict(selected_bundle["base_recipe"])
        selected_recipe["time_bin"] = time_agg
        selected_marker_recipe = preparation.delta_snr_outlier_marker_recipe(
            outlier_model,
            t,
            selected_identity_df,
        )
        selected_marker_cache_token = ()
        if selected_marker_recipe is not None:
            selected_recipe[
                "delta_snr_outlier_markers"
            ] = selected_marker_recipe
            selected_marker_cache_token = (
                "delta-snr-outlier-markers",
                selected_marker_recipe["schema_version"],
                selected_marker_recipe["detector_version"],
                selected_marker_recipe["detection_resolution"],
                selected_marker_recipe["candidate_signature"],
            )
        render_cached_recipe(
            selected_recipe,
            preparation=preparation,
            cache_key=(
                cache_key
                + (time_agg, "dual-temporal")
                + selected_marker_cache_token
            ),
            subject="selected evidence",
            build_label="selected evidence figure build",
            render_figure=render_selected_evidence_export_figure,
        )

    selected_coverage_recipe = None
    if selected_bundle.get("coverage_recipe") is not None:
        selected_coverage_recipe = dict(
            selected_bundle["coverage_recipe"]
        )
        selected_coverage_recipe["time_bin"] = time_agg
        render_cached_recipe(
            selected_coverage_recipe,
            preparation=preparation,
            cache_key=cache_key + (time_agg, "selected coverage"),
            subject="selected path evidence coverage",
            build_label="selected path evidence coverage figure build",
            render_figure=render_selected_compare_coverage_export_figure,
        )
    return {
        "export_recipe": selected_recipe,
        "coverage_export_recipe": selected_coverage_recipe,
        "time_bin": time_agg,
        "title": evidence_title,
        "comparison_unit_count": comparison_unit_count,
    }


def render_performance_selected_evidence(
    context,
    scope,
    current_selection: InspectorSelection,
    station_view,
    *,
    prepared_segment,
    preparation,
    session_state,
):
    """Render selected Performance evidence and its optional focused rows."""
    view = SelectedStationView()
    t = context.translations
    if not station_view.selected_rows:
        station_view.level_three_container.markdown(
            transition_prompt_html(t["txt_results_transition_stations_success"]),
            unsafe_allow_html=True,
        )
        return view
    selected = preparation.prepare_selected_performance(
        context, scope, station_view, prepared_segment,
        preferred_time_bin=current_selection.station_time_bin,
    )
    analysis_id = context.analysis_id
    run_id = context.run_id
    scope_token = scope.scope_token
    analysis_context = context.analysis_context
    presentation_context = context.presentation_context
    analysis_start_t = prepared_segment.bundle["analysis_start_t"]
    analysis_end_t = prepared_segment.bundle["analysis_end_t"]
    timing_collector = context.timing_collector
    selected_meta_df = selected["selected_meta_df"]
    selected_station_rows = selected["selected_station_rows"]
    selected_station = selected["selected_station"]
    selected_locator = selected["selected_locator"]
    selected_peer_rows = selected["selected_peer_rows"]
    selected_cache_key = selected["selected_cache_key"]
    selected_base_recipe = selected["selected_base_recipe"]
    opportunity_display_model = prepared_segment.bundle["display_model"]
    selected_station_labels = selected["selected_station_labels"]
    view.selected_station_labels = selected_station_labels
    view.selected_station_label_text = selected["selection_label"]
    view.selected_station_context_text = selected_success_context_line(
        selected_base_recipe,
        t,
    )
    level_four_container = st.container(
        key=(
            f"results_evidence_level_4_"
            f"{analysis_id}_{run_id}_{scope_token}"
        )
    )
    selected_evidence_heading = t[
        "hdr_results_selected_station_evidence"
    ]
    level_four_container.markdown(
        evidence_level_header_html(
            4,
            t["lbl_results_level_selection_success"],
            selected_evidence_heading,
            view.selected_station_context_text,
        ),
        unsafe_allow_html=True,
    )
    with level_four_container:
        render_result_guidance_popover(
            RESULT_GUIDANCE_SELECTED_STATIONS,
            selected_evidence_heading,
            language=presentation_context.language,
            translations=t,
            key=(
                f"results_guidance_selected_stations_"
                f"{analysis_id}_{run_id}_{scope_token}"
            ),
            analysis_id=analysis_id,
            is_compare=False,
            is_sequential=False,
            analysis_context=analysis_context,
            selected_station_count=1,
        )

    time_options = tuple(selected_base_recipe["time_bin_options"])
    time_default = selected_base_recipe["time_bin_default"]
    selected_time_key = f"opp_time_agg_{analysis_id}_{run_id}_{scope_token}"
    persistent_time_bin_key = inspector_selection.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY
    inspector_selection.initialize_time_bin_widget_state(
        session_state,
        selected_time_key,
        persistent_time_bin_key,
        time_options,
        time_default,
    )
    with level_four_container:
        render_prompted_segment_time_bin_control(
            t["lbl_selected_time_aggregation_bin_size"],
            time_options,
            selected_time_key,
            on_change=inspector_selection.sync_time_bin_widget_state,
            on_change_args=(
                session_state,
                selected_time_key,
                persistent_time_bin_key,
                tuple(time_options),
                time_default,
            ),
        )
    view.selected_time_bin = inspector_selection.sync_time_bin_widget_state(
        session_state,
        selected_time_key,
        persistent_time_bin_key,
        time_options,
        time_default,
    )
    view.selected_station_temporal_evidence_recipe = dict(
        selected_base_recipe
    )
    view.selected_station_temporal_evidence_recipe[
        "time_bin"
    ] = view.selected_time_bin
    view.selected_station_snr_evidence_recipe = dict(
        view.selected_station_temporal_evidence_recipe
    )
    view.selected_evidence_figure_descriptions = {
        "figure_selected_station_snr_evidence.png": (
            selected_base_recipe["snr_title"]
        ),
        "figure_selected_station_temporal_evidence.png": (
            selected_base_recipe["evidence_title"]
        ),
    }
    with level_four_container:
        render_cached_recipe(
            view.selected_station_snr_evidence_recipe,
            preparation=preparation,
            cache_key=(
                *selected_cache_key,
                view.selected_time_bin,
                "snr-evidence",
            ),
            subject="opportunity selected SNR evidence",
            build_label=(
                "opportunity selected SNR evidence figure build"
            ),
            render_figure=render_segment_temporal_snr_export_figure,
        )
        render_cached_recipe(
            view.selected_station_temporal_evidence_recipe,
            preparation=preparation,
            cache_key=(
                *selected_cache_key,
                view.selected_time_bin,
                "temporal-evidence",
            ),
            subject="opportunity selected temporal evidence",
            build_label=(
                "opportunity selected temporal evidence figure build"
            ),
            render_figure=render_segment_temporal_evidence_export_figure,
        )
    level_four_container.markdown(
        transition_prompt_html(
            t["txt_results_transition_rows"]
        ),
        unsafe_allow_html=True,
    )

    level_five_container = st.container(
        key=(
            f"results_evidence_level_5_"
            f"{analysis_id}_{run_id}_{scope_token}"
        )
    )
    with level_five_container:
        focus_window, focus_time_bin, drilldown_filter_container = (
            render_drilldown_header_and_controls(
                selected_station_labels,
                analysis_id,
                run_id,
                scope_token,
                t,
                False,
                False,
                analysis_context,
                presentation_context.language,
                session_state=session_state,
                analysis_start_utc=analysis_start_t,
                analysis_end_utc=analysis_end_t,
                selected_identity=(selected_station, selected_locator),
            )
        )
        focused_station_rows = preparation.filter_station_rows_to_focus_window(
            selected_station_rows,
            focus_window,
            is_sequential=False,
        )
        if focus_window is not None:
            (
                view.drilldown_zoom_performance_snr_recipe,
                view.drilldown_zoom_performance_evidence_recipe,
            ) = preparation.build_performance_drilldown_zoom_recipes(
                selected_base_recipe,
                selected_peer_rows,
                focused_station_rows,
                selected_station_labels[0],
                focus_window,
                focus_time_bin,
                t,
            )
            view.drilldown_zoom_metadata = preparation.drilldown_zoom_export_metadata(
                focus_window,
                selected_identity=(selected_station, selected_locator),
                metric_recipe=view.drilldown_zoom_performance_snr_recipe,
            )
            focus_cache_key = (
                *selected_cache_key,
                "drilldown-focus",
                int(focus_window.start_utc.value),
                int(focus_window.end_utc.value),
                focus_time_bin,
                DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
            )
            render_cached_recipe(
                view.drilldown_zoom_performance_snr_recipe,
                preparation=preparation,
                cache_key=(*focus_cache_key, "snr"),
                subject="opportunity Drill-Down zoom SNR evidence",
                build_label="opportunity Drill-Down zoom SNR figure build",
                render_figure=(
                    render_drilldown_zoom_performance_snr_figure
                ),
            )
            render_cached_recipe(
                view.drilldown_zoom_performance_evidence_recipe,
                preparation=preparation,
                cache_key=(*focus_cache_key, "outcomes"),
                subject="opportunity Drill-Down zoom temporal evidence",
                build_label=(
                    "opportunity Drill-Down zoom temporal figure build"
                ),
                render_figure=(
                    render_drilldown_zoom_performance_evidence_figure
                ),
            )
        with timed_span(timing_collector, "drilldown table build"):
            drill_df, info_msg = preparation.build_performance_drilldown_table(
                context,
                station_view,
                selected_meta_df,
                focused_station_rows,
                export_station_column=opportunity_display_model[
                    "export_station_column"
                ],
            )
        if info_msg:
            st.info(info_msg, icon=":material/info:")
        elif not drill_df.empty:
            view.drilldown_selected_df = render_drilldown_dataframe(
                drill_df,
                selected_station_labels,
                analysis_id,
                run_id,
                scope_token,
                t,
                False,
                False,
                analysis_context,
                presentation_context.language,
                timing_collector=timing_collector,
                filter_container=drilldown_filter_container,
                render_header=False,
            )
    return view


def render_benchmark_selected_evidence(
    context,
    scope,
    current_selection: InspectorSelection,
    station_view,
    *,
    prepared_segment,
    preparation,
    session_state,
):
    """Render selected Benchmark evidence and its optional focused rows."""
    view = SelectedStationView()
    t = context.translations
    is_outlier_reporting_enabled = current_selection.is_outlier_reporting_enabled
    if not station_view.selected_rows:
        station_view.level_three_container.markdown(
            transition_prompt_html(t[
                "txt_results_transition_stations_multi"
                if is_outlier_reporting_enabled
                else "txt_results_transition_stations"
            ]),
            unsafe_allow_html=True,
        )
        return view
    analysis_id = context.analysis_id
    run_id = context.run_id
    scope_token = scope.scope_token
    analysis_context = context.analysis_context
    presentation_context = context.presentation_context
    analysis_start_t = context.analysis_start_t
    analysis_end_t = context.analysis_end_t
    parquet_path = context.parquet_path
    timing_collector = context.timing_collector
    is_sequential = context.is_sequential
    station_col = station_view.station_column
    loc_col = station_view.locator_column
    show_non_joint = station_view.show_non_joint
    compare_view_model = prepared_segment.bundle["view_model"]
    is_local_median = compare_view_model.is_local_median
    col_u_name = compare_view_model.target_name
    ref_header = compare_view_model.reference_header
    outlier_model = prepared_segment.bundle.get("outlier_model")
    selected = preparation.prepare_selected_benchmark(
        context, scope, station_view, prepared_segment,
    )
    selected_meta_df = selected["selected_meta_df"]
    selected_identity_df = selected["selected_identity_df"]
    selected_identity_pairs = selected["selected_identity_pairs"]
    selected_station_labels = selected["selected_station_labels"]
    selected_thresholded_rows = selected["selected_thresholded_rows"]
    selected_identity_cache_key = selected["selected_identity_cache_key"]
    view.selected_station_labels = selected_station_labels
    level_four_container = st.container(
        key=f"results_evidence_level_4_{analysis_id}_{run_id}_{scope_token}"
    )
    try:
        station_df = preparation.load_selected_benchmark_rows(
            context, station_view, selected_meta_df,
        )
        with level_four_container:
            prepared_evidence = preparation.prepare_selected_benchmark_evidence(
                station_df,
                selected_identity_df,
                is_sequential,
                analysis_context.tx_ab_repeat_interval_minutes,
                analysis_context.tx_ab_target_start_minute,
                analysis_context.tx_ab_reference_start_minute,
                t=t,
                analysis_id=analysis_id,
                cache_key=(
                    INSPECTOR_CACHE_VERSION,
                    "comparison",
                    analysis_id,
                    scope_token,
                    *selected_identity_cache_key,
                    bool(is_sequential),
                    int(analysis_context.tx_ab_repeat_interval_minutes),
                    int(analysis_context.tx_ab_target_start_minute),
                    int(analysis_context.tx_ab_reference_start_minute),
                    str(analysis_start_t),
                    str(analysis_end_t),
                    presentation_context.language,
                    presentation_context.theme,
                ),
                analysis_context=analysis_context,
                preferred_time_bin=current_selection.station_time_bin,
                thresholded_station_rows=selected_thresholded_rows,
                analysis_start_t=analysis_start_t,
                analysis_end_t=analysis_end_t,
                target_only_label=t["leg_only_me"].format(callsign=t["txt_target"]),
                reference_only_label=t["leg_only_ref"].format(ref_callsign=t["txt_reference"]),
                outlier_model=outlier_model,
            )
            view.selected_evidence_export = render_selected_station_evidence(
                prepared_evidence,
                selected_identity_df,
                selection=current_selection,
                session_state=session_state,
                preparation=preparation,
                t=t,
                analysis_context=analysis_context,
                language=presentation_context.language,
                is_sequential=is_sequential,
                outlier_model=outlier_model,
            )
        level_four_container.markdown(
            transition_prompt_html(
                t["txt_results_transition_rows"]
            ),
            unsafe_allow_html=True,
        )
        level_five_container = st.container(
            key=(
                f"results_evidence_level_5_"
                f"{analysis_id}_{run_id}_{scope_token}"
            )
        )
        with level_five_container:
            selected_identity_for_zoom = (
                selected_identity_pairs[0]
                if len(selected_identity_pairs) == 1
                else None
            )
            (
                focus_window,
                focus_time_bin,
                drilldown_filter_container,
            ) = render_drilldown_header_and_controls(
                selected_station_labels,
                analysis_id,
                run_id,
                scope_token,
                t,
                True,
                is_sequential,
                analysis_context,
                presentation_context.language,
                session_state=session_state,
                analysis_start_utc=analysis_start_t,
                analysis_end_utc=analysis_end_t,
                selected_identity=selected_identity_for_zoom,
                allow_multiple_station_selection=(
                    is_outlier_reporting_enabled
                ),
            )
            focused_station_df = preparation.filter_station_rows_to_focus_window(
                station_df,
                focus_window,
                is_sequential=is_sequential,
                tx_ab_repeat_interval_minutes=(
                    analysis_context.tx_ab_repeat_interval_minutes
                ),
                tx_ab_target_start_minute=(
                    analysis_context.tx_ab_target_start_minute
                ),
                tx_ab_reference_start_minute=(
                    analysis_context.tx_ab_reference_start_minute
                ),
            )
            drilldown_outlier_context = (
                inspector_selection.drilldown_outlier_context_for_scope(
                    session_state,
                    analysis_id=analysis_id,
                    run_id=run_id,
                    scope_token=scope_token,
                    selected_identity=selected_identity_for_zoom,
                    analysis_start_utc=analysis_start_t,
                    analysis_end_utc=analysis_end_t,
                )
            )
            if focus_window is not None:
                (
                    view.drilldown_zoom_benchmark_delta_recipe,
                    view.drilldown_zoom_benchmark_coverage_recipe,
                ) = preparation.build_benchmark_drilldown_zoom_recipes(
                    focused_station_df,
                    selected_identity_df,
                    selected_thresholded_rows,
                    is_sequential,
                    analysis_context,
                    focus_window,
                    focus_time_bin,
                    (view.selected_evidence_export or {}).get(
                        "export_recipe"
                    ),
                    (view.selected_evidence_export or {}).get(
                        "coverage_export_recipe"
                    ),
                    t,
                    outlier_context=drilldown_outlier_context,
                    outlier_model=outlier_model,
                )
                view.drilldown_zoom_metadata = (
                    preparation.drilldown_zoom_export_metadata(
                        focus_window,
                        selected_identity=selected_identity_for_zoom,
                        metric_recipe=(
                            view.drilldown_zoom_benchmark_delta_recipe
                        ),
                        outlier_context=(
                            drilldown_outlier_context
                            if isinstance(
                                view.drilldown_zoom_benchmark_delta_recipe,
                                Mapping,
                            )
                            and view.drilldown_zoom_benchmark_delta_recipe.get(
                                "outlier_overlay"
                            )
                            is not None
                            else None
                        ),
                    )
                )
                focus_cache_key = (
                    INSPECTOR_CACHE_VERSION,
                    "comparison-drilldown-focus",
                    analysis_id,
                    scope_token,
                    selected_identity_for_zoom,
                    bool(is_sequential),
                    int(focus_window.start_utc.value),
                    int(focus_window.end_utc.value),
                    focus_time_bin,
                    (
                        drilldown_outlier_context.request_token
                        if drilldown_outlier_context is not None
                        else None
                    ),
                    presentation_context.language,
                    presentation_context.theme,
                    DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
                )
                if view.drilldown_zoom_benchmark_delta_recipe is not None:
                    render_cached_recipe(
                        view.drilldown_zoom_benchmark_delta_recipe,
                        preparation=preparation,
                        cache_key=(*focus_cache_key, "delta-snr"),
                        subject=(
                            "Benchmark Drill-Down zoom Delta-SNR evidence"
                        ),
                        build_label=(
                            "Benchmark Drill-Down zoom Delta-SNR figure build"
                        ),
                        render_figure=(
                            render_drilldown_zoom_benchmark_delta_snr_figure
                        ),
                    )
                if view.drilldown_zoom_benchmark_coverage_recipe is not None:
                    render_cached_recipe(
                        view.drilldown_zoom_benchmark_coverage_recipe,
                        preparation=preparation,
                        cache_key=(*focus_cache_key, "coverage"),
                        subject=(
                            "Benchmark Drill-Down zoom coverage"
                        ),
                        build_label=(
                            "Benchmark Drill-Down zoom coverage figure build"
                        ),
                        render_figure=(
                            render_drilldown_zoom_benchmark_coverage_figure
                        ),
                    )
            with timed_span(
                timing_collector,
                "drilldown table build",
            ):
                drill_df, info_msg = preparation.build_drilldown_table(
                    parquet_path,
                    selected_meta_df,
                    station_col,
                    loc_col,
                    t['tbl_col_km'],
                    t['tbl_col_az'],
                    analysis_id,
                    is_sequential,
                    show_non_joint,
                    is_local_median,
                    col_u_name,
                    ref_header,
                    t,
                    station_rows_df=focused_station_df,
                    tx_ab_repeat_interval_minutes=(
                        analysis_context.tx_ab_repeat_interval_minutes
                    ),
                    tx_ab_target_start_minute=(
                        analysis_context.tx_ab_target_start_minute
                    ),
                    tx_ab_reference_start_minute=(
                        analysis_context.tx_ab_reference_start_minute
                    ),
                    target_callsign=analysis_context.callsign,
                )
            if info_msg:
                st.info(info_msg, icon=":material/info:")
            elif drill_df is not None and not drill_df.empty:
                view.drilldown_selected_df = render_drilldown_dataframe(
                    drill_df,
                    selected_station_labels,
                    analysis_id,
                    run_id,
                    scope_token,
                    t,
                    True,
                    is_sequential,
                    analysis_context,
                    presentation_context.language,
                    allow_multiple_station_selection=(
                        is_outlier_reporting_enabled
                    ),
                    timing_collector=timing_collector,
                    filter_container=drilldown_filter_container,
                    render_header=False,
                )

    except FileNotFoundError as exc:
        preparation.log_artifact_read_failure(
            exc,
            parquet_path=parquet_path,
            analysis_id=analysis_id,
            stage="selected station rows load",
        )
        level_four_container.warning(
            t["warn_analysis_cache_expired"]
        )
    return view
