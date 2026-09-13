"""Scope controls and prepared segment evidence presentation."""

import streamlit as st

from config import COMPASS
from ui.components.inspector_common import (
    render_cached_recipe,
    render_prompted_segment_time_bin_control,
    render_reference_correction_notice,
)
from ui.inspector import selection_state as inspector_selection
from ui.inspector.contracts import InspectorContext, InspectorScope, ScopeControlsView
from ui.inspector.presentation import selection_summary
from ui.plots.evidence_figures import (
    render_segment_insight_export_figure,
    render_segment_temporal_evidence_export_figure,
    render_segment_temporal_snr_export_figure,
)
from ui.plots.opportunity_figures import _render_opportunity_segment_figure
from ui.plots.benchmark_evidence_figures import render_compare_temporal_coverage_export_figure
from ui.result_hierarchy import (
    active_scope_text,
    evidence_child_header_html,
    evidence_level_header_html,
    scope_evidence_text,
    scope_summary_html,
    segment_statistics_html,
)
from ui.result_guidance import (
    RESULT_GUIDANCE_COMPARISON_EVIDENCE,
    RESULT_GUIDANCE_SEGMENT,
    RESULT_GUIDANCE_SUCCESS_EVIDENCE,
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    render_result_guidance_popover,
)


def render_scope_controls(context: InspectorContext, options_view_model, *, session_state) -> ScopeControlsView:
    """Render the existing scope widgets and return their resolved scope."""
    analysis_id = context.analysis_id
    run_id = context.run_id
    t = context.translations
    analysis_context = context.analysis_context
    presentation_context = context.presentation_context
    is_compare = context.is_compare
    is_sequential = context.is_sequential
    valid_distances = options_view_model.valid_distances
    level_two_container = st.container(
        key=f"results_evidence_level_2_{analysis_id}_{run_id}"
    )
    segment_inspector_title = t["hdr_results_segment_inspector"]
    level_two_container.markdown(
        evidence_level_header_html(
            2,
            t["lbl_results_level_scope"],
            segment_inspector_title,
            t["sub_results_segment_inspector"],
        ),
        unsafe_allow_html=True,
    )
    with level_two_container:
        render_result_guidance_popover(
            RESULT_GUIDANCE_SEGMENT,
            segment_inspector_title,
            language=presentation_context.language,
            translations=t,
            key=f"results_guidance_segment_{analysis_id}_{run_id}",
            analysis_id=analysis_id,
            is_compare=is_compare,
            is_sequential=is_sequential,
            analysis_context=analysis_context,
        )

    lbl_dist = t["lbl_results_distance_range"]
    lbl_dir = t["lbl_results_direction"]
    opt_full = t["opt_full_range"]
    opt_all_dir = t["opt_all_dirs"]

    valid_dirs = options_view_model.valid_directions
    range_persistent_key, direction_persistent_key = (
        inspector_selection.segment_scope_persistent_state_keys(is_compare)
    )

    # Render stable explicit-All multiselects. The callback keeps All mutually
    # exclusive with specific values and restores All when the field is cleared.
    col_insp1, col_insp2 = level_two_container.columns(2)
    with col_insp1:
        dist_key = f"dist_multi_{analysis_id}_{run_id}"
        dist_previous_key = f"{dist_key}_previous"
        dist_options = [opt_full] + valid_distances
        inspector_selection.initialize_explicit_all_multiselect(
            session_state,
            dist_key,
            dist_previous_key,
            opt_full,
            valid_distances,
            range_persistent_key,
        )
        selected_distance_values = st.multiselect(
            lbl_dist,
            dist_options,
            key=dist_key,
            placeholder=lbl_dist,
            label_visibility="collapsed",
            on_change=inspector_selection.update_explicit_all_multiselect,
            args=(
                session_state,
                dist_key,
                dist_previous_key,
                opt_full,
                valid_distances,
                range_persistent_key,
            ),
        )

    with col_insp2:
        dir_key = f"dir_multi_{analysis_id}_{run_id}"
        dir_previous_key = f"{dir_key}_previous"
        dir_options = [opt_all_dir] + valid_dirs
        inspector_selection.initialize_explicit_all_multiselect(
            session_state,
            dir_key,
            dir_previous_key,
            opt_all_dir,
            valid_dirs,
            direction_persistent_key,
        )
        selected_direction_values = st.multiselect(
            lbl_dir,
            dir_options,
            key=dir_key,
            placeholder=lbl_dir,
            label_visibility="collapsed",
            on_change=inspector_selection.update_explicit_all_multiselect,
            args=(
                session_state,
                dir_key,
                dir_previous_key,
                opt_all_dir,
                valid_dirs,
                direction_persistent_key,
            ),
        )

    selected_ranges = inspector_selection.canonical_specific_selection(
        selected_distance_values,
        opt_full,
        valid_distances,
    )
    selected_directions = inspector_selection.canonical_specific_selection(
        selected_direction_values,
        opt_all_dir,
        valid_dirs,
    )
    range_summary = selection_summary(
        selected_ranges,
        opt_full,
        "range",
        t,
    )
    direction_summary = selection_summary(
        selected_directions,
        opt_all_dir,
        "direction",
        t,
    )
    selected_seg = f"{range_summary} | {direction_summary}"
    active_scope_summary = active_scope_text(
        range_summary,
        direction_summary,
        t,
    )
    scope_summary_placeholder = level_two_container.empty()
    scope_summary_placeholder.markdown(
        scope_summary_html(active_scope_summary),
        unsafe_allow_html=True,
    )

    range_token = "all" if not selected_ranges else "-".join(
        str(valid_distances.index(value)) for value in selected_ranges
    )
    direction_token = "all" if not selected_directions else "-".join(
        str(COMPASS.index(value)) for value in selected_directions
    )
    scope_token = f"r{range_token}_d{direction_token}"
    return ScopeControlsView(
        scope=InspectorScope(
            selected_ranges=tuple(selected_ranges),
            selected_directions=tuple(selected_directions),
            range_summary=range_summary,
            direction_summary=direction_summary,
            selected_segment=selected_seg,
            active_scope_summary=active_scope_summary,
            scope_token=scope_token,
        ),
        level_two_container=level_two_container,
        scope_summary_placeholder=scope_summary_placeholder,
    )



def render_segment_temporal_evidence(
    temporal_bundle,
    *,
    preparation,
    session_state,
    analysis_id,
    run_id,
    scope_token,
    cache_key,
    t,
    is_compare,
    is_sequential,
    analysis_context,
    language,
    outlier_model=None,
    timing_collector=None,
):
    """Render one segment-scoped Benchmark or Performance temporal view."""
    if not temporal_bundle:
        return None

    temporal_evidence_title = t["hdr_results_temporal_evidence"]
    st.markdown(
        evidence_child_header_html(
            temporal_evidence_title,
            t[
                (
                    "sub_results_temporal_evidence"
                    if is_compare
                    else "sub_results_success_temporal"
                )
            ],
        ),
        unsafe_allow_html=True,
    )
    render_result_guidance_popover(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        temporal_evidence_title,
        language=language,
        translations=t,
        key=(
            f"results_guidance_temporal_evidence_"
            f"{analysis_id}_{run_id}_{scope_token}"
        ),
        analysis_id=analysis_id,
        is_compare=is_compare,
        is_sequential=is_sequential,
        analysis_context=analysis_context,
    )

    time_bin_options = list(temporal_bundle["time_bin_options"])
    time_bin_default = temporal_bundle["time_bin_default"]
    persistent_state_key = (
        inspector_selection.RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY
        if is_compare
        else inspector_selection.RESULTS_SEGMENT_TIME_BIN_ABSOLUTE_STATE_KEY
    )
    widget_key = f"segment_evidence_time_agg_{analysis_id}_{run_id}_{scope_token}"
    selected_time_bin = inspector_selection.initialize_time_bin_widget_state(
        session_state,
        widget_key,
        persistent_state_key,
        time_bin_options,
        time_bin_default,
    )

    render_prompted_segment_time_bin_control(
        t["lbl_time_aggregation_bin_size"],
        time_bin_options,
        widget_key,
        on_change=inspector_selection.sync_time_bin_widget_state,
        on_change_args=(
            session_state,
            widget_key,
            persistent_state_key,
            tuple(time_bin_options),
            time_bin_default,
        ),
    )

    selected_time_bin = inspector_selection.sync_time_bin_widget_state(
        session_state,
        widget_key,
        persistent_state_key,
        time_bin_options,
        time_bin_default,
    )
    temporal_base_recipe = temporal_bundle.get("base_recipe")
    temporal_recipe = (
        dict(temporal_base_recipe)
        if temporal_base_recipe is not None
        else None
    )
    if temporal_recipe is not None:
        temporal_recipe["time_bin"] = selected_time_bin
        if "chronological_title_template" in temporal_bundle:
            temporal_recipe["chronological_title"] = temporal_bundle[
                "chronological_title_template"
            ].format(time_bin=selected_time_bin)
    outlier_marker_cache_token = ()
    if is_compare and temporal_recipe is not None:
        outlier_marker_recipe = preparation.delta_snr_outlier_marker_recipe(
            outlier_model,
            t,
        )
        if outlier_marker_recipe is not None:
            temporal_recipe[
                "delta_snr_outlier_markers"
            ] = outlier_marker_recipe
            outlier_marker_cache_token = (
                "delta-snr-outlier-markers",
                outlier_marker_recipe["schema_version"],
                outlier_marker_recipe["detector_version"],
                outlier_marker_recipe["detection_resolution"],
                outlier_marker_recipe["candidate_signature"],
            )
    snr_export_recipe = None
    coverage_export_recipe = None
    if not is_compare:
        snr_export_recipe = dict(temporal_recipe)
        render_cached_recipe(
            snr_export_recipe,
            preparation=preparation,
            cache_key=cache_key
            + ("segment temporal SNR deviation", selected_time_bin),
            subject="segment temporal SNR deviation",
            build_label="segment temporal SNR deviation figure build",
            render_figure=render_segment_temporal_snr_export_figure,
        )
    if temporal_recipe is not None:
        render_cached_recipe(
            temporal_recipe,
            preparation=preparation,
            cache_key=cache_key
            + ("segment temporal evidence", selected_time_bin)
            + outlier_marker_cache_token,
            subject="segment temporal evidence",
            build_label="segment temporal evidence figure build",
            render_figure=render_segment_temporal_evidence_export_figure,
        )
    coverage_base_recipe = temporal_bundle.get("coverage_recipe")
    if is_compare and coverage_base_recipe:
        coverage_export_recipe = dict(coverage_base_recipe)
        coverage_export_recipe["time_bin"] = selected_time_bin
        render_cached_recipe(
            coverage_export_recipe,
            preparation=preparation,
            cache_key=cache_key
            + ("segment temporal coverage", selected_time_bin),
            subject="segment temporal coverage",
            build_label="segment temporal coverage figure build",
            render_figure=render_compare_temporal_coverage_export_figure,
        )
    temporal_result = {
        "export_recipe": temporal_recipe,
        "snr_export_recipe": snr_export_recipe,
        "time_bin": selected_time_bin,
    }
    if coverage_export_recipe is not None:
        temporal_result[
            "coverage_export_recipe"
        ] = coverage_export_recipe
    return temporal_result


def render_performance_segment_evidence(
    context: InspectorContext, scope: InspectorScope, controls: ScopeControlsView,
    prepared_segment, *, preparation, session_state,
):
    """Render prepared Performance evidence inside the existing scope container."""
    analysis_id = context.analysis_id
    run_id = context.run_id
    t = context.translations
    analysis_context = context.analysis_context
    presentation_context = context.presentation_context
    timing_collector = context.timing_collector
    scope_token = scope.scope_token
    active_scope_summary = scope.active_scope_summary
    segment_bundle = prepared_segment.bundle
    segment_cache_key = prepared_segment.cache_key
    level_two_container = controls.level_two_container
    scope_summary_placeholder = controls.scope_summary_placeholder
    opportunity_display_model = segment_bundle["display_model"]
    segment_recipe = segment_bundle["figure_recipe"]
    temporal_bundle = segment_bundle["temporal_bundle"]

    summary = opportunity_display_model["summary_lines"]
    scope_summary_placeholder.markdown(
        scope_summary_html(
            active_scope_summary,
            scope_evidence_text(
                opportunity_display_model["confirmed_station_count"],
                opportunity_display_model["confirmed_opportunity_count"],
                analysis_id=analysis_id,
                is_compare=False,
                is_sequential=False,
                translations=t,
            ),
        ),
        unsafe_allow_html=True,
    )

    segment_temporal_export = None
    with level_two_container:
        st.markdown(
            segment_statistics_html(summary),
            unsafe_allow_html=True,
        )
        success_evidence_title = t["hdr_results_success_evidence"]
        st.markdown(
            evidence_child_header_html(
                success_evidence_title,
                t["sub_results_success_evidence"],
            ),
            unsafe_allow_html=True,
        )
        render_result_guidance_popover(
            RESULT_GUIDANCE_SUCCESS_EVIDENCE,
            success_evidence_title,
            language=presentation_context.language,
            translations=t,
            key=(
                f"results_guidance_success_evidence_"
                f"{analysis_id}_{run_id}_{scope_token}"
            ),
            analysis_id=analysis_id,
            is_compare=False,
            is_sequential=False,
            analysis_context=analysis_context,
        )

        render_cached_recipe(
            segment_recipe,
            preparation=preparation,
            cache_key=segment_cache_key,
            subject="opportunity segment",
            build_label="opportunity segment figure build",
            render_figure=_render_opportunity_segment_figure,
        )
        segment_temporal_export = render_segment_temporal_evidence(
            temporal_bundle,
            preparation=preparation,
            session_state=session_state,
            analysis_id=analysis_id,
            run_id=run_id,
            scope_token=scope_token,
            cache_key=segment_cache_key,
            t=t,
            is_compare=False,
            is_sequential=False,
            analysis_context=analysis_context,
            language=presentation_context.language,
            timing_collector=timing_collector,
        )

    return segment_temporal_export



def render_benchmark_segment_evidence(
    context: InspectorContext, scope: InspectorScope, controls: ScopeControlsView,
    prepared_segment, *, preparation, session_state,
):
    """Render prepared Benchmark evidence without repeating numerical work."""
    analysis_id = context.analysis_id
    run_id = context.run_id
    t = context.translations
    analysis_context = context.analysis_context
    presentation_context = context.presentation_context
    is_sequential = context.is_sequential
    line1_str = context.line1_str
    timing_collector = context.timing_collector
    scope_token = scope.scope_token
    active_scope_summary = scope.active_scope_summary
    segment_bundle = prepared_segment.bundle
    segment_cache_key = prepared_segment.cache_key
    level_two_container = controls.level_two_container
    scope_summary_placeholder = controls.scope_summary_placeholder
    compare_view_model = segment_bundle["view_model"]
    segment_figure_recipe = segment_bundle["figure_recipe"]
    segment_temporal_bundle = segment_bundle.get("temporal_bundle")
    segment_summary = segment_bundle["summary"]
    segment_station_count = int(segment_bundle["evidence_station_count"])
    segment_evidence_count = int(segment_bundle["evidence_count"])
    outlier_model = segment_bundle.get("outlier_model")
    seg_line2 = compare_view_model.scope_summary
    has_plot_data = compare_view_model.has_plot_data
    segment_temporal_export = None
    comparison_subtitle_key = (
        "sub_results_comparison_evidence_scheduled"
        if is_sequential
        else "sub_results_comparison_evidence_joint"
    )
    scope_summary_placeholder.markdown(
        scope_summary_html(
            active_scope_summary,
            scope_evidence_text(
                segment_station_count,
                segment_evidence_count,
                analysis_id=analysis_id,
                is_compare=True,
                is_sequential=is_sequential,
                translations=t,
            ),
        ),
        unsafe_allow_html=True,
    )

    with level_two_container:
        comparison_evidence_title = t[
            "hdr_results_comparison_evidence"
        ]
        st.markdown(
            evidence_child_header_html(
                comparison_evidence_title,
                t[comparison_subtitle_key],
            ),
            unsafe_allow_html=True,
        )
        render_result_guidance_popover(
            RESULT_GUIDANCE_COMPARISON_EVIDENCE,
            comparison_evidence_title,
            language=presentation_context.language,
            translations=t,
            key=(
                f"results_guidance_comparison_evidence_"
                f"{analysis_id}_{run_id}_{scope_token}"
            ),
            analysis_id=analysis_id,
            is_compare=True,
            is_sequential=is_sequential,
            analysis_context=analysis_context,
        )
        render_reference_correction_notice(
            t,
            is_compare=True,
            is_sequential=is_sequential,
            analysis_context=analysis_context,
        )

        if has_plot_data:
            if segment_summary:
                st.markdown(
                    segment_statistics_html(segment_summary),
                    unsafe_allow_html=True,
                )
            st.markdown(
                "<div style='height:0.9rem;'></div>",
                unsafe_allow_html=True,
            )
            render_cached_recipe(
                segment_figure_recipe,
                preparation=preparation,
                cache_key=segment_cache_key,
                subject="segment insight",
                build_label="segment insight figure build",
                render_figure=render_segment_insight_export_figure,
            )
            segment_temporal_export = render_segment_temporal_evidence(
                segment_temporal_bundle,
                preparation=preparation,
                session_state=session_state,
                analysis_id=analysis_id,
                run_id=run_id,
                scope_token=scope_token,
                cache_key=segment_cache_key,
                t=t,
                is_compare=True,
                is_sequential=is_sequential,
                analysis_context=analysis_context,
                language=presentation_context.language,
                outlier_model=outlier_model,
                timing_collector=timing_collector,
            )
        else:
            no_joint_message = (
                t["lbl_no_joint_pairs"]
                if is_sequential
                else t["lbl_no_joint"]
            )
            st.info(no_joint_message, icon="??????")
            st.markdown(
                "<div style='font-size:11px; color:#ccc; "
                f"margin-bottom:1rem; font-family:monospace;'>{line1_str}"
                f"<br>{seg_line2}</div>",
                unsafe_allow_html=True,
            )
    return segment_temporal_export
