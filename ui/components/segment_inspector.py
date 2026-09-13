"""The single Inspector fragment and its explicit page orchestration."""

from dataclasses import replace

import streamlit as st

from ui.components.inspector_common import timed_span
from ui.components.inspector_export import (
    register_benchmark_inspector_outputs,
    register_empty_inspector_outputs,
    register_performance_inspector_outputs,
)
from ui.components.inspector_outliers import render_delta_snr_outlier_report
from ui.components.inspector_scope import (
    render_benchmark_segment_evidence,
    render_performance_segment_evidence,
    render_scope_controls,
)
from ui.components.inspector_selected import (
    render_benchmark_selected_evidence,
    render_performance_selected_evidence,
)
from ui.components.inspector_stations import (
    render_benchmark_station_insights,
    render_performance_station_insights,
)
from ui.inspector import selection_state as inspector_selection
from ui.inspector.contracts import InspectorContext
from ui.inspector.preparation import (
    InspectorPreparation,
    InspectorArtifactReadError,
    enabled_delta_snr_outlier_detection_policy,
)
from ui.results_export import render_download_all_results
from ui.url_state import (
    URL_QUERY_SYNCHRONIZER_FRAGMENT_KEY,
    render_current_url_synchronizer,
)


@st.fragment
def render_segment_inspector(
    analysis_id,
    title,
    is_compare,
    is_sequential,
    enriched_df,
    parquet_path,
    line1_str,
    t,
    max_peer_distance_km,
    analysis_context,
    presentation_context,
    analysis_kind,
    analysis_start_t=None,
    analysis_end_t=None,
    show_export_button=False,
    timing_collector=None,
    timing_label=None,
):
    """Render the Segment Inspector fragment with an optional parent timing span."""
    span_label = timing_label or "Segment Inspector render"
    with timed_span(timing_collector, span_label):
        result = _render_segment_inspector_body(
            analysis_id,
            title,
            is_compare,
            is_sequential,
            enriched_df,
            parquet_path,
            line1_str,
            t,
            max_peer_distance_km,
            analysis_context,
            presentation_context,
            analysis_start_t=analysis_start_t,
            analysis_end_t=analysis_end_t,
            analysis_kind=analysis_kind,
            show_export_button=show_export_button,
            timing_collector=timing_collector,
        )
    if timing_collector is not None:
        timing_collector.log_report(analysis_title=title)
    render_current_url_synchronizer(
        st.session_state,
        key=(
            f"{URL_QUERY_SYNCHRONIZER_FRAGMENT_KEY}_"
            f"{analysis_id}_{st.session_state.get('run_id', 'current')}"
        ),
    )
    return result


def _render_segment_inspector_body(
    analysis_id,
    title,
    is_compare,
    is_sequential,
    enriched_df,
    parquet_path,
    line1_str,
    t,
    max_peer_distance_km,
    analysis_context,
    presentation_context,
    analysis_kind,
    analysis_start_t=None,
    analysis_end_t=None,
    show_export_button=False,
    timing_collector=None,
):
    """Bind completed-run inputs once, then render the inspector page flow."""
    context = InspectorContext(
        analysis_id=analysis_id, title=title, is_compare=is_compare,
        is_sequential=is_sequential, parquet_path=parquet_path,
        line1_str=line1_str, translations=t,
        max_peer_distance_km=max_peer_distance_km,
        analysis_context=analysis_context, presentation_context=presentation_context,
        analysis_kind=analysis_kind, run_id=st.session_state.get("run_id", 0),
        analysis_start_t=analysis_start_t, analysis_end_t=analysis_end_t,
        show_export_button=show_export_button, timing_collector=timing_collector,
    )
    render_inspector_page(context, enriched_df, session_state=st.session_state)


def render_inspector_page(context, enriched_df, *, session_state):
    """Express the existing scope, evidence, station, and Drill-Down flow."""
    preparation = InspectorPreparation(
        session_state, context.run_id, context.timing_collector,
    )
    preparation.touch_artifact(context.parquet_path, context.analysis_id)
    options = preparation.prepare_options(
        enriched_df, analysis_id=context.analysis_id,
        max_peer_distance_km=context.max_peer_distance_km,
    )
    controls = render_scope_controls(context, options, session_state=session_state)
    scope = controls.scope
    if context.is_opportunity:
        scope = replace(scope, distance_scope_intervals=preparation.success_distance_scope_intervals(
            enriched_df, scope.selected_ranges,
            max_peer_distance_km=context.max_peer_distance_km,
        ))
    if not options.valid_distances or not options.valid_directions:
        return
    with timed_span(context.timing_collector, "segment scope filter"):
        scope_rows = preparation.filter_scope_rows(
            enriched_df, max_peer_distance_km=context.max_peer_distance_km,
            selected_ranges=scope.selected_ranges,
            selected_directions=scope.selected_directions,
        )
    policy = _resolve_outlier_policy(context, session_state)
    if scope_rows.empty:
        _render_empty_scope(context, scope, preparation, policy, session_state)
        return
    if context.is_compare:
        inspector_selection.resolve_configured_station_selection_for_reporting(
            session_state, is_outlier_reporting_enabled=policy is not None,
        )
    selection = inspector_selection.read_inspector_selection(
        session_state, run_id=context.run_id, analysis_id=context.analysis_id,
        scope_token=scope.scope_token, is_compare=context.is_compare,
        selected_ranges=scope.selected_ranges, selected_directions=scope.selected_directions,
        is_outlier_reporting_enabled=policy is not None,
    )
    if context.is_opportunity:
        try:
            prepared_segment = preparation.prepare_performance_segment(
                context, scope, scope_rows, retained_time_bin=selection.segment_time_bin,
            )
        except InspectorArtifactReadError as exc:
            if exc.is_missing:
                st.warning(context.translations["warn_analysis_cache_expired"])
            else:
                st.error(context.translations["err_analysis_evidence_schema_invalid"])
            return
        segment_temporal_export = render_performance_segment_evidence(
            context, scope, controls, prepared_segment,
            preparation=preparation, session_state=session_state,
        )
        stations = render_performance_station_insights(
            context, scope, selection, prepared_segment, session_state=session_state,
        )
        selected = render_performance_selected_evidence(
            context, scope, selection, stations, prepared_segment=prepared_segment,
            preparation=preparation, session_state=session_state,
        )
        register_performance_inspector_outputs(
            context, scope, selection, stations, selected, prepared_segment,
            segment_temporal_export, preparation=preparation,
            language=session_state.get("lang", "en"),
        )
        st.markdown(
            f"<div style='font-size:11px; color:#ccc; margin-top:0.75rem; margin-bottom:1rem; font-family:monospace;'>{context.line1_str}</div>",
            unsafe_allow_html=True,
        )
    else:
        prepared_segment = preparation.prepare_benchmark_segment(
            context, scope, scope_rows, retained_time_bin=selection.segment_time_bin,
            outlier_detection_policy=policy,
        )
        segment_temporal_export = render_benchmark_segment_evidence(
            context, scope, controls, prepared_segment,
            preparation=preparation, session_state=session_state,
        )
        if selection.is_outlier_reporting_enabled:
            with controls.level_two_container:
                _render_prepared_outlier_report(
                    context, scope, prepared_segment.bundle["outlier_model"],
                    prepared_segment.bundle["outlier_report_view_model"], session_state,
                )
        stations = render_benchmark_station_insights(
            context, scope, selection, prepared_segment, session_state=session_state,
        )
        selected = render_benchmark_selected_evidence(
            context, scope, selection, stations, prepared_segment=prepared_segment,
            preparation=preparation, session_state=session_state,
        )
        register_benchmark_inspector_outputs(
            context, scope, selection, stations, selected, prepared_segment,
            segment_temporal_export, preparation=preparation,
            language=session_state.get("lang", "en"), outlier_detection_policy=policy,
        )
    if context.show_export_button:
        render_download_all_results(context.translations)


def _resolve_outlier_policy(context, session_state):
    """Pause reporting while its live detector settings are invalid."""
    if context.is_opportunity:
        return None
    policy = enabled_delta_snr_outlier_detection_policy(session_state)
    if (
        session_state.get(inspector_selection.RESULTS_REPORT_DELTA_SNR_OUTLIER_CANDIDATES_STATE_KEY) is True
        and policy is None
    ):
        st.warning(
            context.translations["msg_outlier_report_invalid_detector_settings"],
            icon=":material/warning:",
        )
    return policy


def _render_prepared_outlier_report(context, scope, model, report, session_state):
    render_delta_snr_outlier_report(
        model, report, t=context.translations, language=context.language,
        analysis_id=context.analysis_id, run_id=context.run_id,
        scope_token=scope.scope_token, is_sequential=context.is_sequential,
        analysis_context=context.analysis_context, session_state=session_state,
    )


def _render_empty_scope(context, scope, preparation, policy, session_state):
    st.info(context.translations["msg_results_no_stations_in_scope"], icon=":material/info:")
    outlier_exports = None
    if policy is not None:
        model, report = preparation.prepare_empty_outlier_report(context, detection_policy=policy)
        outlier_exports = preparation.prepare_outlier_exports(
            model, report, is_sequential=context.is_sequential,
        )
        _render_prepared_outlier_report(context, scope, model, report, session_state)
    register_empty_inspector_outputs(
        context, scope, outlier_detection_policy=policy, outlier_exports=outlier_exports,
    )
    if context.show_export_button:
        render_download_all_results(context.translations)
