"""
Segment Inspector & Results Components Module.
Contains the interactive drill-down UI (histograms, data tables) and 
compact recipes for lazy high-resolution result exports. Isolated as Streamlit fragments
to allow UI updates without triggering full-page reruns.
"""

import inspect
import json
from collections.abc import Mapping
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from functools import partial
from hashlib import sha256
from html import escape
from numbers import Integral
from pathlib import Path
from time import perf_counter
import pandas as pd
import numpy as np
import streamlit as st
from config import (
    COMPASS,
    INSPECTOR_CACHE_MAX_BYTES,
    INSPECTOR_CACHE_OPTIONS_MAX_ENTRIES,
    INSPECTOR_CACHE_PNG_MAX_ENTRIES,
    INSPECTOR_CACHE_SEGMENT_MAX_ENTRIES,
    INSPECTOR_CACHE_SELECTED_MAX_ENTRIES,
    SEGMENT_SELECTION_ALL,
    TEMPORAL_IQR_BAND_ALPHA,
)
from config.delta_snr_outlier import (
    DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
    DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD,
    DeltaSnrOutlierDetectionPolicy,
)
from core.input_validation import (
    is_valid_callsign,
    is_valid_locator,
    normalize_ascii_upper,
)
from ui.matplotlib_renderer import (
    dispose_matplotlib_figure,
    get_matplotlib_render_mode,
    matplotlib_render_span_label,
    render_matplotlib_figure,
    render_matplotlib_image_bytes,
)
from ui.results_export import register_inspector_export, render_download_all_results
from ui.url_state import (
    URL_QUERY_SYNCHRONIZER_FRAGMENT_KEY,
    render_current_url_synchronizer,
)
from core.opportunity_engine import (
    OPPORTUNITY_DRILLDOWN_VIEW_COLUMNS,
    OPPORTUNITY_SEGMENT_VIEW_COLUMNS,
    opportunity_utc_from_time_slot,
)
from core.artifact_store import ARTIFACT_STORE, read_parquet_artifact
from core.compare_engine import compare_footer_counts
from core.performance_timer import log_performance_event
from ui.inspector.evidence_data import (
    _build_compare_unit_rows,
    _build_segment_compare_units,
    _compare_joint_evidence_points,
    _prepare_identity_meta,
    _retain_thresholded_compare_outcomes,
)
from ui.inspector.drilldown import (
    _build_drilldown_table,
    _load_station_rows_for_drilldown,
    opportunity_drilldown_display_table,
)
from ui.inspector.view_models import (
    build_compare_inspector_view_model,
    build_inspector_options,
    build_opportunity_inspector_view_model,
    compare_scope_availability,
    filter_inspector_scope,
)
from ui.inspector.session_cache import SessionInspectorCache
from ui.inspector.outlier_candidates import (
    DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
    DELTA_SNR_OUTLIER_DETECTOR_VERSION,
    build_delta_snr_outlier_context_bounds,
    prepare_delta_snr_outlier_model,
)
from ui.inspector.outlier_report import (
    OUTLIER_UNAVAILABLE_VALUE,
    build_delta_snr_outlier_report_view_model,
)
from ui.inspector.outlier_export import (
    build_delta_snr_outlier_export_metadata,
    build_delta_snr_outlier_export_tables,
)
from ui.page_navigation import (
    DRILLDOWN_ANCHOR_ID,
    STATION_INSIGHTS_ANCHOR_ID,
    render_page_anchor,
    request_page_navigation,
)
from ui.result_state import (
    INSPECTOR_CACHE_STATE_KEY,
    RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY,
    RESULTS_REPORT_DELTA_SNR_OUTLIER_CANDIDATES_STATE_KEY,
    RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY,
    RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY,
)
from ui.inspector.drilldown_focus import (
    DRILLDOWN_FOCUS_SCHEMA_VERSION,
    DRILLDOWN_OUTLIER_CONTEXT_SCHEMA_VERSION,
    DRILLDOWN_OUTLIER_FOCUS_OPTION,
    DRILLDOWN_ZOOM_DURATION_HOURS,
    available_manual_zoom_options,
    default_focus_center_utc,
    drilldown_outlier_candidate_context_for_scope,
    filter_station_rows_to_focus_window,
    focus_center_utc,
    manual_zoom_center_bounds,
    resolve_centered_zoom_window,
    resolve_outlier_focus_window,
)
from ui.plots.evidence_figures import (
    _segment_figure_export_recipe,
    _segment_temporal_evidence_export_recipe,
    _selected_evidence_export_recipe,
    _time_agg_options_for_window,
    render_segment_insight_export_figure,
    render_segment_temporal_evidence_export_figure,
    render_segment_temporal_snr_export_figure,
    render_selected_evidence_export_figure,
)
from ui.plots.opportunity_figures import (
    SUCCESS_DISTANCE_BINNING_VERSION,
    SUCCESS_SNR_BASELINE_VERSION,
    SUCCESS_SNR_REPRESENTATION_ACTUAL,
    SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE,
    SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
    SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    _as_utc_timestamp,
    _opportunity_segment_recipe,
    _opportunity_temporal_recipe,
    _render_opportunity_segment_figure,
)
from ui.plots.benchmark_evidence_figures import (
    _compare_coverage_recipe,
    render_compare_temporal_coverage_export_figure,
    render_selected_compare_coverage_export_figure,
)
from ui.plots.temporal_layout import TEMPORAL_EVIDENCE_LAYOUT_VERSION
from ui.plots.drilldown_zoom_figures import (
    DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
    build_drilldown_zoom_benchmark_delta_snr_recipe,
    build_drilldown_zoom_outlier_overlay_recipe,
    build_drilldown_zoom_performance_snr_recipe,
    render_drilldown_zoom_benchmark_coverage_figure,
    render_drilldown_zoom_benchmark_delta_snr_figure,
    render_drilldown_zoom_performance_evidence_figure,
    render_drilldown_zoom_performance_snr_figure,
)
from ui.result_hierarchy import (
    active_scope_text,
    drilldown_subtitle,
    evidence_child_header_html,
    evidence_level_header_html,
    remote_station_type,
    scope_context_html,
    scope_evidence_text,
    scope_summary_html,
    segment_statistics_html,
    selected_station_context,
    selected_station_label,
    station_scope_text,
    transition_prompt_html,
)
from ui.result_guidance import (
    RESULT_GUIDANCE_COMPARISON_EVIDENCE,
    RESULT_GUIDANCE_DRILLDOWN,
    RESULT_GUIDANCE_OUTLIER_REPORT,
    RESULT_GUIDANCE_SEGMENT,
    RESULT_GUIDANCE_SELECTED_STATIONS,
    RESULT_GUIDANCE_STATION_INSIGHTS,
    RESULT_GUIDANCE_SUCCESS_EVIDENCE,
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    render_result_guidance_popover,
)
from ui.reference_correction import configured_snr_correction_notice

INSPECTOR_CACHE_VERSION = 48
INSPECTOR_PNG_RENDER_VERSION = 39
RESULTS_SHOW_NON_JOINT_STATE_KEY = "val_results_show_non_joint"
RESULTS_SHOW_ZERO_TARGET_STATE_KEY = "val_results_show_zero_target"
RESULTS_SELECTED_RANGES_COMPARE_STATE_KEY = "val_results_selected_ranges_compare"
RESULTS_SELECTED_DIRECTIONS_COMPARE_STATE_KEY = (
    "val_results_selected_directions_compare"
)
RESULTS_SELECTED_RANGES_ABSOLUTE_STATE_KEY = (
    "val_results_selected_ranges_absolute"
)
RESULTS_SELECTED_DIRECTIONS_ABSOLUTE_STATE_KEY = (
    "val_results_selected_directions_absolute"
)
RESULTS_TIME_BIN_COMPARE_STATE_KEY = "val_results_time_bin_compare"
RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY = "val_results_time_bin_absolute"
RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY = (
    "val_results_segment_time_bin_compare"
)
RESULTS_SEGMENT_TIME_BIN_ABSOLUTE_STATE_KEY = (
    "val_results_segment_time_bin_absolute"
)
RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY = (
    "val_results_selected_stations_absolute"
)
RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY = (
    "results_station_selection_revision_compare"
)
STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS = (5, 4, 3)
SUCCESS_STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS = (9, 2)
COMPACT_DATAFRAME_VISIBLE_BODY_ROWS = 5
COMPACT_DATAFRAME_ROW_HEIGHT_PX = 35
COMPACT_DATAFRAME_HEIGHT_PX = (
    (COMPACT_DATAFRAME_VISIBLE_BODY_ROWS + 1)
    * COMPACT_DATAFRAME_ROW_HEIGHT_PX
    + 2
)
INSPECTOR_CACHE_NAMESPACE_LIMITS = {
    "options": INSPECTOR_CACHE_OPTIONS_MAX_ENTRIES,
    "segment": INSPECTOR_CACHE_SEGMENT_MAX_ENTRIES,
    "selected": INSPECTOR_CACHE_SELECTED_MAX_ENTRIES,
    "png": INSPECTOR_CACHE_PNG_MAX_ENTRIES,
}


def _validate_inspector_analysis_mode(*, analysis_kind, is_compare):
    """Return whether the mode is Performance and reject retired combinations."""
    if analysis_kind == "opportunity" and not is_compare:
        return True
    if analysis_kind == "comparison" and is_compare:
        return False
    raise ValueError(
        "Segment Inspector mode must be Performance "
        "(analysis_kind='opportunity', is_compare=False) or Benchmark "
        "(analysis_kind='comparison', is_compare=True)."
    )


def _time_bin_persistent_state_key(is_compare):
    """Return the canonical saved-config state key for one evidence view."""
    return (
        RESULTS_TIME_BIN_COMPARE_STATE_KEY
        if is_compare
        else RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY
    )


def _selected_stations_persistent_state_key(is_compare):
    """Return the canonical selected-station state key for one result type."""
    return (
        RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY
        if is_compare
        else RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY
    )


def _segment_scope_persistent_state_keys(is_compare):
    """Return canonical range and direction keys for Benchmark or Performance."""
    if is_compare:
        return (
            RESULTS_SELECTED_RANGES_COMPARE_STATE_KEY,
            RESULTS_SELECTED_DIRECTIONS_COMPARE_STATE_KEY,
        )
    return (
        RESULTS_SELECTED_RANGES_ABSOLUTE_STATE_KEY,
        RESULTS_SELECTED_DIRECTIONS_ABSOLUTE_STATE_KEY,
    )


def _validated_time_bin(options, preferred, fallback):
    """Return a supported bin, preferring the configured deterministic fallback."""
    available_options = tuple(options)
    if not available_options:
        raise ValueError("At least one evidence time-bin option is required.")
    if preferred in available_options:
        return preferred
    if fallback in available_options:
        return fallback
    return available_options[0]


def _compare_temporal_time_bin_policy(
    analysis_start_t,
    analysis_end_t,
    preferred_time_bin,
):
    """Resolve adaptive bins plus a cache token for one retained extra choice."""
    adaptive_options, adaptive_default = _time_agg_options_for_window(
        analysis_start_t,
        analysis_end_t,
    )
    resolved_options, _resolved_default = _time_agg_options_for_window(
        analysis_start_t,
        analysis_end_t,
        retained_time_bin=preferred_time_bin,
    )
    retained_extra_cache_token = (
        str(preferred_time_bin)
        if (
            preferred_time_bin in resolved_options
            and preferred_time_bin not in adaptive_options
        )
        else None
    )
    return resolved_options, adaptive_default, retained_extra_cache_token


def _delta_snr_outlier_segment_cache_suffix(
    is_enabled,
    detection_policy=None,
):
    """Return no cache fields when disabled and detector identity when on."""
    if not is_enabled:
        return ()
    resolved_policy = (
        DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY
        if detection_policy is None
        else detection_policy
    )
    if not isinstance(resolved_policy, DeltaSnrOutlierDetectionPolicy):
        raise TypeError(
            "detection_policy must be a DeltaSnrOutlierDetectionPolicy."
        )
    return (
        "delta-snr-outlier-candidates",
        True,
        DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        resolved_policy.signature_tuple,
    )


def _enabled_delta_snr_outlier_detection_policy(session_state):
    """Return the valid enabled policy, pausing on invalid live edits."""
    if session_state.get(
        RESULTS_REPORT_DELTA_SNR_OUTLIER_CANDIDATES_STATE_KEY,
        False,
    ) is not True:
        return None
    try:
        return DeltaSnrOutlierDetectionPolicy(
            **{
                policy_field: session_state.get(
                    f"val_{config_field}",
                    getattr(
                        DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
                        policy_field,
                    ),
                )
                for config_field, policy_field in (
                    DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
                )
            }
        )
    except ValueError:
        return None


def _initialize_time_bin_widget_state(widget_key, persistent_key, options, fallback):
    """Initialize a transient widget from its validated canonical saved value."""
    selected_time_bin = _validated_time_bin(
        options,
        st.session_state.get(persistent_key),
        fallback,
    )
    st.session_state[persistent_key] = selected_time_bin
    st.session_state[widget_key] = selected_time_bin
    return selected_time_bin


def _render_stretched_time_bin_control(
    label,
    options,
    widget_key,
    *,
    on_change=None,
    on_change_args=(),
):
    """Render one compact time-bin selector across its available container width."""
    if hasattr(st, "segmented_control"):
        control_kwargs = {
            "key": widget_key,
            "label_visibility": "collapsed",
            "width": "stretch",
        }
        if on_change is not None:
            control_kwargs["on_change"] = on_change
            control_kwargs["args"] = tuple(on_change_args)
        return st.segmented_control(label, options, **control_kwargs)

    radio_kwargs = {
        "horizontal": True,
        "key": widget_key,
        "label_visibility": "collapsed",
    }
    if on_change is not None:
        radio_kwargs["on_change"] = on_change
        radio_kwargs["args"] = tuple(on_change_args)
    return st.radio(label, options, **radio_kwargs)


def _render_prompted_segment_time_bin_control(
    label,
    options,
    widget_key,
    *,
    on_change=None,
    on_change_args=(),
):
    """Render an instruction prompt above a full-width segment-bin selector."""
    st.markdown(
        transition_prompt_html(label),
        unsafe_allow_html=True,
    )
    return _render_stretched_time_bin_control(
        label,
        options,
        widget_key,
        on_change=on_change,
        on_change_args=on_change_args,
    )


def _segment_temporal_figure_title(title, analysis_id, selected_segment, t):
    """Build the localized Benchmark-temporal title with its scope text."""
    original_title = str(title)
    _, separator, comparison_title = original_title.partition(":")
    if not separator:
        comparison_title = original_title
    if str(analysis_id).upper().startswith("TX"):
        temporal_prefix = t["fig_tx_comp_temporal_prefix"]
    else:
        temporal_prefix = t["fig_rx_comp_temporal_prefix"]
    return (
        f"{temporal_prefix}: {comparison_title.strip()} - {selected_segment}"
    )


def _success_figure_labels(translations, analysis_id):
    """Return localized labels for the pure Performance evidence recipes."""
    is_tx = str(analysis_id).upper().startswith("TX")
    mode_suffix = "tx" if is_tx else "rx"
    return {
        "reach_title": translations[
            f"fig_success_reach_title_{mode_suffix}"
        ],
        "reach_y": translations[
            f"fig_success_reach_y_{mode_suffix}"
        ],
        "consistency_title": translations[
            f"fig_success_consistency_title_{mode_suffix}"
        ],
        "snr_distance_title": translations[
            f"fig_success_snr_distance_title_{mode_suffix}"
        ],
        "distance_x": translations["fig_success_distance_x"],
        "rate_y": translations["fig_success_rate_y"],
        "snr_y": translations["fig_success_snr_y"],
        "confirmed_opportunities": translations[
            "fig_success_confirmed_opportunities"
        ],
        "qualifying_stations": translations[
            "fig_success_qualifying_stations"
        ],
        "target_stations": translations[
            f"map_success_{mode_suffix}_station_target"
        ],
        "successful_snr_stations": translations[
            "fig_success_successful_snr_stations"
        ],
        "station_balanced": translations["fig_success_station_balanced"],
        "observation_level": translations[
            "fig_success_observation_level"
        ],
        "target_evidence": translations[
            f"success_{mode_suffix}_opportunity_success"
        ],
        "counter_evidence": translations[
            f"success_{mode_suffix}_opportunity_counter"
        ],
        "median": translations["fig_success_median"],
        "iqr": translations["fig_success_iqr"],
        "two_station_range": translations[
            "fig_success_two_station_range"
        ],
        "support": translations["fig_success_support"],
        "support_title": translations["fig_success_support_title"],
        "bin_width": translations["fig_success_bin_width"],
        "locator_precision_note": translations[
            "fig_success_locator_precision_note"
        ],
        "thousands_separator": translations[
            "fmt_results_thousands_separator"
        ],
        "snr_chronological_title": translations[
            f"fig_success_snr_chronological_title_{mode_suffix}"
        ],
        "snr_utc_hour_title": translations[
            f"fig_success_snr_utc_hour_title_{mode_suffix}"
        ],
        "evidence_chronological_title": translations[
            "fig_success_evidence_chronological_title"
        ],
        "evidence_utc_hour_title": translations[
            "fig_success_evidence_utc_hour_title"
        ],
        "station_vote_y": translations[
            f"fig_success_station_votes_y_{mode_suffix}"
        ],
        "station_support_folded_y": translations[
            f"fig_success_station_support_folded_y_{mode_suffix}"
        ],
        "opportunity_y": translations[
            "fig_success_opportunities_y"
        ],
        "opportunity_folded_y": translations[
            "fig_success_opportunities_folded_y"
        ],
        "rate_legend": translations["fig_success_rate_legend"],
        "time_x": translations["fig_success_time_x"],
        "utc_hour_x": translations["fig_success_utc_hour_x"],
        "snr_anomaly_y": translations[
            f"fig_success_snr_anomaly_y_{mode_suffix}"
        ],
        "snr_density": translations["fig_success_snr_density"],
        "station_baseline": translations[
            "fig_success_station_baseline"
        ],
        "bin_median_chronological": translations[
            "fig_success_bin_median_chronological"
        ],
        "bin_median_folded": translations[
            "fig_success_bin_median_folded"
        ],
        "bin_iqr": translations["fig_temporal_bin_iqr"],
        "snr_anomaly_unavailable": translations[
            "fig_success_snr_anomaly_unavailable"
        ],
        "temporal_unavailable": translations[
            "fig_success_temporal_unavailable"
        ],
        "utc_dates_folded": translations[
            "fig_success_utc_dates_folded"
        ],
        "selected_snr_chronological_title": translations[
            "fig_success_selected_snr_chronological_title"
        ],
        "selected_snr_utc_hour_title": translations[
            "fig_success_selected_snr_utc_hour_title"
        ],
        "selected_snr_y": translations[
            "fig_success_selected_temporal_snr_y"
        ],
        "selected_snr_density": translations[
            "fig_success_selected_snr_density"
        ],
        "selected_bin_median_chronological": translations[
            "fig_success_selected_bin_median"
        ],
        "selected_bin_median_folded": translations[
            "fig_success_selected_folded_median"
        ],
        "selected_snr_unavailable": translations[
            "fig_success_selected_snr_unavailable"
        ],
    }


def _compare_coverage_figure_labels(
    translations,
    analysis_id,
    *,
    is_sequential,
    target_only_label,
    joint_label,
    reference_only_label,
):
    """Return semantic labels for Benchmark evidence-coverage recipes."""
    if (
        target_only_label is None
        or joint_label is None
        or reference_only_label is None
    ):
        raise ValueError(
            "Benchmark temporal outcome labels must be localized strings."
        )
    mode_suffix = (
        "tx"
        if str(analysis_id).upper().startswith("TX")
        else "rx"
    )
    if is_sequential:
        unit_y = translations["fig_compare_coverage_unit_y_scheduled"]
        unit_folded_y = translations[
            "fig_compare_coverage_unit_folded_y_scheduled"
        ]
        selected_title_unit = translations[
            "fig_selected_compare_coverage_unit_scheduled"
        ]
        selected_unit_y = unit_y
        selected_unit_folded_y = unit_folded_y
        gate_note = translations[
            "fig_compare_coverage_gate_scheduled"
        ]
    else:
        unit_y = translations[
            f"fig_compare_coverage_unit_y_{mode_suffix}"
        ]
        unit_folded_y = translations[
            f"fig_compare_coverage_unit_folded_y_{mode_suffix}"
        ]
        selected_title_unit = translations[
            "fig_selected_compare_coverage_unit_simultaneous"
        ]
        selected_unit_y = translations[
            "fig_selected_compare_coverage_unit_y_simultaneous"
        ]
        selected_unit_folded_y = translations[
            "fig_selected_compare_coverage_unit_folded_y_simultaneous"
        ]
        gate_note = translations[
            "fig_compare_coverage_gate_simultaneous"
        ]
    return {
        "utc_dates_folded": translations["fig_segment_dates_folded"],
        "folded_unavailable": translations[
            "fig_compare_coverage_folded_unavailable"
        ],
        "time_x": translations["fig_segment_chronological_x"],
        "utc_hour_x": translations["fig_segment_utc_hour_x"],
        "evidence_chronological_title": translations[
            "fig_compare_coverage_chronological_title"
        ],
        "evidence_utc_hour_title": translations[
            "fig_compare_coverage_utc_hour_title"
        ],
        "station_vote_y": translations[
            f"fig_compare_coverage_station_y_{mode_suffix}"
        ],
        "station_folded_y": translations[
            f"fig_compare_coverage_station_folded_y_{mode_suffix}"
        ],
        "unit_y": unit_y,
        "unit_folded_y": unit_folded_y,
        "joint_share_y": translations["fig_compare_joint_share_y"],
        "station_joint_share": translations[
            "fig_compare_joint_share_station"
        ],
        "outcome_joint_share": translations[
            "fig_compare_joint_share_outcome"
        ],
        "target_only": str(target_only_label),
        "joint": str(joint_label),
        "reference_only": str(reference_only_label),
        "gate_note": gate_note,
        "selected_chronological_title": translations[
            "fig_selected_compare_coverage_chronological_title"
        ],
        "selected_utc_hour_title": translations[
            "fig_selected_compare_coverage_utc_hour_title"
        ],
        "selected_title_unit": selected_title_unit,
        "selected_unit_y": selected_unit_y,
        "selected_unit_folded_y": selected_unit_folded_y,
        "selected_joint_share": translations[
            "fig_selected_compare_joint_share"
        ],
    }


def _compare_temporal_coverage_title(
    translations,
    analysis_id,
    callsign,
):
    """Build the localized Benchmark Temporal Evidence Coverage title."""
    mode_suffix = (
        "tx"
        if str(analysis_id).upper().startswith("TX")
        else "rx"
    )
    return translations[f"fig_compare_coverage_title_{mode_suffix}"].format(
        callsign=str(callsign).strip().upper(),
    )


def _success_temporal_figure_title(
    callsign,
    analysis_id,
    translations,
    *,
    figure_kind,
):
    """Build one localized Performance temporal SNR or evidence figure title."""
    mode_suffix = (
        "tx"
        if str(analysis_id).upper().startswith("TX")
        else "rx"
    )
    if figure_kind == "snr":
        title_key = f"fig_success_temporal_snr_title_{mode_suffix}"
    elif figure_kind == "evidence":
        title_key = f"fig_success_temporal_title_{mode_suffix}"
    else:
        raise ValueError(
            "Performance temporal figure kind must be 'snr' or 'evidence'."
        )
    return translations[
        title_key
    ].format(
        callsign=str(callsign).strip().upper(),
    )


def _selected_success_temporal_figure_title(
    station,
    locator,
    analysis_id,
    translations,
    *,
    figure_kind,
):
    """Build one localized figure title for a selected Performance station."""
    mode_suffix = (
        "tx"
        if str(analysis_id).upper().startswith("TX")
        else "rx"
    )
    if figure_kind == "snr":
        title_key = (
            f"fig_success_selected_station_snr_title_{mode_suffix}"
        )
    elif figure_kind == "evidence":
        title_key = (
            f"fig_success_selected_station_temporal_title_{mode_suffix}"
        )
    else:
        raise ValueError(
            "Selected Performance figure kind must be 'snr' or 'evidence'."
        )
    return translations[title_key].format(
        station=str(station).strip().upper(),
        locator=str(locator).strip().upper(),
    )


def _folded_utc_hour_panel_title(t):
    """Return the complete localized title for the fixed one-hour folded panel."""
    return t["fig_segment_utc_hour_title"]


def _sync_time_bin_widget_state(widget_key, persistent_key, options, fallback):
    """Copy one widget selection into canonical state after option validation."""
    selected_time_bin = _validated_time_bin(
        options,
        st.session_state.get(widget_key),
        fallback,
    )
    st.session_state[persistent_key] = selected_time_bin
    return selected_time_bin


def _initialize_boolean_widget_state(widget_key, persistent_key, fallback):
    """Initialize a transient toggle from a canonical boolean saved-config value."""
    persistent_value = st.session_state.get(persistent_key)
    selected_value = (
        persistent_value
        if isinstance(persistent_value, bool)
        else bool(fallback)
    )
    st.session_state[persistent_key] = selected_value
    st.session_state[widget_key] = selected_value
    return selected_value


def _sync_boolean_widget_state(widget_key, persistent_key):
    """Copy one toggle value into canonical saved-config state."""
    selected_value = bool(st.session_state.get(widget_key, False))
    st.session_state[persistent_key] = selected_value
    return selected_value


def _station_identity_record(callsign, locator):
    """Return one stable station identity record, or ``None`` for blank values."""
    if callsign is None or locator is None:
        return None
    callsign_text = str(callsign).strip().upper()
    locator_text = str(locator).strip().upper()
    if not callsign_text or not locator_text:
        return None
    return {"callsign": callsign_text, "locator": locator_text}


def _validate_single_station_identity_records(configured_identities):
    """Validate durable state as automatic, empty, or one station identity.

    ``None`` means that no explicit selection exists and retains the normal
    first-row table default. An empty list records deliberate deselection.
    Every other accepted value is a one-item list containing an exact,
    normalized ``callsign``/``locator`` record.
    """
    if configured_identities is None:
        return None
    if not isinstance(configured_identities, list):
        raise ValueError(
            "Selected-station state must be null or a list containing at most "
            "one identity."
        )
    if len(configured_identities) > 1:
        raise ValueError(
            "Selected-station state must contain at most one identity."
        )
    if not configured_identities:
        return []

    configured_identity = configured_identities[0]
    if not isinstance(configured_identity, Mapping):
        raise ValueError("Selected-station identity must be an object.")
    if set(configured_identity) != {"callsign", "locator"}:
        raise ValueError(
            "Selected-station identity must contain only callsign and locator."
        )
    callsign = configured_identity["callsign"]
    locator = configured_identity["locator"]
    if not isinstance(callsign, str) or not is_valid_callsign(callsign):
        raise ValueError("Selected-station callsign is invalid.")
    if not isinstance(locator, str) or not is_valid_locator(locator):
        raise ValueError("Selected-station locator is invalid.")
    return [
        {
            "callsign": normalize_ascii_upper(callsign),
            "locator": normalize_ascii_upper(locator),
        }
    ]


def _validate_multiple_station_identity_records(configured_identities):
    """Validate an ordered Benchmark selection of exact station identities."""
    if configured_identities is None:
        return None
    if not isinstance(configured_identities, list):
        raise ValueError(
            "Benchmark selected-station state must be null or a list."
        )

    normalized_identities = []
    seen_identity_pairs = set()
    for configured_identity in configured_identities:
        if not isinstance(configured_identity, Mapping):
            raise ValueError("Selected-station identity must be an object.")
        if set(configured_identity) != {"callsign", "locator"}:
            raise ValueError(
                "Selected-station identity must contain only callsign and locator."
            )
        callsign = configured_identity["callsign"]
        locator = configured_identity["locator"]
        if not isinstance(callsign, str) or not is_valid_callsign(callsign):
            raise ValueError("Selected-station callsign is invalid.")
        if not isinstance(locator, str) or not is_valid_locator(locator):
            raise ValueError("Selected-station locator is invalid.")
        normalized_identity = {
            "callsign": normalize_ascii_upper(callsign),
            "locator": normalize_ascii_upper(locator),
        }
        identity_pair = (
            normalized_identity["callsign"],
            normalized_identity["locator"],
        )
        if identity_pair in seen_identity_pairs:
            continue
        seen_identity_pairs.add(identity_pair)
        normalized_identities.append(normalized_identity)
    return normalized_identities


def _station_selection_for_outlier_reporting_mode(
    configured_identities,
    *,
    is_outlier_reporting_enabled,
):
    """Restore the historical singleton selection when the opt-in is off."""
    if (
        is_outlier_reporting_enabled
        or not isinstance(configured_identities, list)
        or len(configured_identities) <= 1
    ):
        return configured_identities
    return configured_identities[:1]


def _station_selection_default_rows(
    station_table,
    station_column,
    locator_column,
    configured_identities,
    *,
    allow_multiple=False,
):
    """Resolve saved station identities to current display-row positions.

    A missing explicit identity is reported separately and never causes a
    substitute row to be selected. A ``None`` configuration retains the normal
    first-row default, whereas an empty list resolves to no selected rows.
    """
    normalized_identities = (
        _validate_multiple_station_identity_records(configured_identities)
        if allow_multiple
        else _validate_single_station_identity_records(configured_identities)
    )
    if normalized_identities is None:
        return ([0] if not station_table.empty else []), []
    if not normalized_identities:
        return [], []

    available_rows = {}
    for row_position, (callsign, locator) in enumerate(
        station_table[[station_column, locator_column]].itertuples(
            index=False,
            name=None,
        )
    ):
        identity_record = _station_identity_record(callsign, locator)
        if identity_record is None:
            continue
        identity_pair = (
            identity_record["callsign"],
            identity_record["locator"],
        )
        available_rows.setdefault(identity_pair, row_position)

    selected_rows = []
    missing_identities = []
    for identity_record in normalized_identities:
        identity_pair = (
            identity_record["callsign"],
            identity_record["locator"],
        )
        row_position = available_rows.get(identity_pair)
        if row_position is None:
            missing_identities.append(identity_record)
        else:
            selected_rows.append(row_position)
    return selected_rows, missing_identities


def _prioritize_focused_station_identities(
    station_table,
    station_column,
    locator_column,
    focused_identities,
):
    """Move exact focused identities to the top of a display-only table.

    Matching and non-matching rows each retain their existing relative order.
    The supplied table is never mutated, and a focus hidden by an active table
    filter remains absent rather than bypassing that filter.
    """
    normalized_identities = _validate_multiple_station_identity_records(
        focused_identities
    )
    if not normalized_identities or station_table.empty:
        return station_table
    focused_pairs = {
        (identity["callsign"], identity["locator"])
        for identity in normalized_identities
    }
    focused_positions = []
    remaining_positions = []
    for row_position, (callsign, locator) in enumerate(
        station_table[[station_column, locator_column]].itertuples(
            index=False,
            name=None,
        )
    ):
        identity_record = _station_identity_record(callsign, locator)
        identity_pair = (
            (
                identity_record["callsign"],
                identity_record["locator"],
            )
            if identity_record is not None
            else None
        )
        destination = (
            focused_positions
            if identity_pair in focused_pairs
            else remaining_positions
        )
        destination.append(row_position)
    if not focused_positions:
        return station_table
    return station_table.iloc[
        focused_positions + remaining_positions
    ].reset_index(drop=True)


def _focused_station_identities_for_scope(
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
):
    """Return one report-driven table focus only in its originating scope."""
    focus_record = session_state.get(
        RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY
    )
    if not isinstance(focus_record, dict):
        return None
    expected_scope = {
        "analysis_id": analysis_id,
        "run_id": run_id,
        "scope_token": scope_token,
    }
    if any(
        focus_record.get(field_name) != expected_value
        for field_name, expected_value in expected_scope.items()
    ):
        return None
    station_identities = focus_record.get("station_identities")
    if not isinstance(station_identities, list):
        return None
    return station_identities


def _station_identity_records_for_rows(
    station_table,
    selected_rows,
    station_column,
    locator_column,
    *,
    allow_multiple=False,
):
    """Return ordered exact identities for valid selected station rows."""
    valid_rows = [
        row_position
        for row_position in selected_rows
        if isinstance(row_position, Integral)
        and 0 <= row_position < len(station_table)
    ]
    if not allow_multiple and len(valid_rows) > 1:
        raise ValueError("Station selection must contain at most one row.")
    if not valid_rows:
        return []

    selected_identity_records = []
    for row_position in valid_rows:
        row = station_table.iloc[row_position]
        identity_record = _station_identity_record(
            row[station_column],
            row[locator_column],
        )
        if identity_record is None:
            raise ValueError(
                "Selected station row must contain a callsign and locator."
            )
        selected_identity_records.append(identity_record)
    if allow_multiple:
        return _validate_multiple_station_identity_records(
            selected_identity_records
        )
    return _validate_single_station_identity_records(
        selected_identity_records
    )


def _sync_selected_station_state(
    persistent_key,
    station_table,
    selected_rows,
    station_column,
    locator_column,
    *,
    allow_multiple=False,
):
    """Persist an explicit empty, single, or Benchmark multi-selection."""
    selected_identities = _station_identity_records_for_rows(
        station_table,
        selected_rows,
        station_column,
        locator_column,
        allow_multiple=allow_multiple,
    )
    st.session_state[persistent_key] = selected_identities
    return selected_identities


def _mark_station_selection_changed(selection_changed_key):
    """Record that a user, rather than a table default, changed selection."""
    st.session_state[selection_changed_key] = True
    st.session_state.pop(
        RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY,
        None,
    )
    st.session_state.pop(
        RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY,
        None,
    )


def _sync_selected_station_state_if_changed(
    selection_changed_key,
    persistent_key,
    station_table,
    selected_rows,
    station_column,
    locator_column,
    *,
    allow_multiple=False,
):
    """Persist visible rows only after a user-generated selection event.

    Applying a saved default, changing transient segment scope, or rendering a
    table that does not contain every saved identity must not rewrite the
    canonical config state. A real selection event replaces it exactly,
    including a deliberate empty selection.
    """
    if not st.session_state.pop(selection_changed_key, False):
        return st.session_state.get(persistent_key)
    return _sync_selected_station_state(
        persistent_key,
        station_table,
        selected_rows,
        station_column,
        locator_column,
        allow_multiple=allow_multiple,
    )


def _selection_requires_zero_hit_rows(
    station_table,
    station_column,
    locator_column,
    hit_column,
    configured_identities,
):
    """Return whether a Performance selection includes a hidden zero-hit row."""
    normalized_identities = _validate_single_station_identity_records(
        configured_identities
    )
    if not normalized_identities:
        return False
    selected_identity = normalized_identities[0]
    selected_pair = (
        selected_identity["callsign"],
        selected_identity["locator"],
    )
    hit_counts = pd.to_numeric(station_table[hit_column], errors="coerce")
    for row_position, (callsign, locator) in enumerate(
        station_table[[station_column, locator_column]].itertuples(
            index=False,
            name=None,
        )
    ):
        identity_record = _station_identity_record(callsign, locator)
        if identity_record is None:
            continue
        identity_pair = (
            identity_record["callsign"],
            identity_record["locator"],
        )
        if identity_pair != selected_pair:
            continue
        hit_count = hit_counts.iloc[row_position]
        if pd.isna(hit_count) or hit_count <= 0:
            return True
    return False


def _opportunity_export_station_rows(
    display_station_table,
    *,
    export_column_renames,
):
    """Rename only visible Performance station rows into the export schema."""
    if display_station_table is None:
        return pd.DataFrame()
    return display_station_table.rename(columns=export_column_renames)


def _warn_missing_station_identities(missing_identities, t):
    """Warn that saved identities are unavailable without choosing substitutes."""
    if not missing_identities:
        return
    missing_labels = ", ".join(
        f"{identity['callsign']} ({identity['locator']})"
        for identity in missing_identities
    )
    warning_template = t["warn_saved_station_unavailable"]
    st.warning(
        warning_template.format(stations=missing_labels),
        icon=":material/warning:",
    )


def _timed_span(timing_collector, label, detail=""):
    """Return a timing context when profiling is active."""
    if timing_collector is None:
        return nullcontext()
    return timing_collector.span(label, detail=detail)


def _log_artifact_read_failure(exc, *, parquet_path, analysis_id, run_id, stage):
    """Record enough context to distinguish lifecycle loss from schema failures."""
    path = Path(parquet_path)
    log_performance_event(
        "session_artifact_read",
        outcome="missing" if isinstance(exc, FileNotFoundError) else "invalid",
        stage=stage,
        analysis_id=analysis_id,
        run_id=run_id,
        artifact=path.name,
        exists=path.is_file(),
        error_type=type(exc).__name__,
    )


def _inspector_cache(run_id):
    """Return the current run's bounded cache from this Streamlit session."""
    cache = st.session_state.get(INSPECTOR_CACHE_STATE_KEY)
    if not isinstance(cache, SessionInspectorCache) or cache.run_id != run_id:
        cache = SessionInspectorCache(
            run_id,
            max_bytes=INSPECTOR_CACHE_MAX_BYTES,
            namespace_limits=INSPECTOR_CACHE_NAMESPACE_LIMITS,
        )
        st.session_state[INSPECTOR_CACHE_STATE_KEY] = cache
    return cache


def _inspector_cache_get(run_id, namespace, key, timing_collector=None, *, item=""):
    """Read one cache entry and expose the outcome to terminal profiling."""
    started_at = perf_counter()
    cache = _inspector_cache(run_id)
    value, hit = cache.get(namespace, key)
    elapsed = perf_counter() - started_at
    detail = (
        f"{'hit' if hit else 'miss'} | entries {cache.entry_count} | "
        f"cached {cache.total_bytes / 1024:.1f} KiB"
    )
    if timing_collector is not None:
        timing_collector.add(f"inspector cache {namespace}", elapsed, detail=detail)
    log_performance_event(
        "inspector_cache",
        namespace=namespace,
        item=item or namespace,
        outcome="hit" if hit else "miss",
        entries=cache.entry_count,
        cache_bytes=cache.total_bytes,
    )
    return value, hit


def _inspector_cache_put(run_id, namespace, key, value, *, size_bytes=None):
    cache = _inspector_cache(run_id)
    stored = cache.put(namespace, key, value, size_bytes=size_bytes)
    st.session_state[INSPECTOR_CACHE_STATE_KEY] = cache
    if not stored:
        log_performance_event(
            "inspector_cache",
            namespace=namespace,
            outcome="not_stored",
            entries=cache.entry_count,
            cache_bytes=cache.total_bytes,
        )
    return stored


def _render_cached_recipe(
    recipe,
    *,
    run_id,
    cache_key,
    subject,
    build_label,
    render_figure,
    timing_collector=None,
):
    """Render a compact recipe, reusing preview PNG bytes when available."""
    render_mode = get_matplotlib_render_mode()
    png_key = (
        INSPECTOR_CACHE_VERSION,
        INSPECTOR_PNG_RENDER_VERSION,
        TEMPORAL_EVIDENCE_LAYOUT_VERSION,
        TEMPORAL_IQR_BAND_ALPHA,
        render_mode,
        subject,
        cache_key,
    )
    if render_mode == "image":
        image_bytes, hit = _inspector_cache_get(
            run_id,
            "png",
            png_key,
            timing_collector,
            item=subject,
        )
        if hit:
            render_matplotlib_image_bytes(
                image_bytes,
                width="stretch",
                timing_collector=timing_collector,
                subject=subject,
                cache_detail="session cache hit",
            )
            return image_bytes

    with _timed_span(timing_collector, build_label):
        figure = render_figure(recipe)
    if figure is None:
        return None
    try:
        with _timed_span(timing_collector, matplotlib_render_span_label(subject)):
            image_bytes = render_matplotlib_figure(
                figure,
                width="stretch",
                timing_collector=timing_collector,
                subject=subject,
            )
    finally:
        dispose_matplotlib_figure(figure)
    if image_bytes is not None and render_mode == "image":
        _inspector_cache_put(
            run_id,
            "png",
            png_key,
            image_bytes,
            size_bytes=len(image_bytes),
        )
    return image_bytes





def _resolve_explicit_all_selection(current, previous, all_option, specific_options):
    """Normalize one multiselect where All is explicit and mutually exclusive."""
    allowed_specific = set(specific_options)
    current = [
        value for value in (current or [])
        if value == all_option or value in allowed_specific
    ]
    previous = [
        value for value in (previous or [])
        if value == all_option or value in allowed_specific
    ]
    specifics = [value for value in current if value != all_option]

    if all_option in current and specifics:
        return specifics if all_option in previous else [all_option]
    if specifics:
        return specifics
    return [all_option]

def _initialize_explicit_all_multiselect(
    key,
    previous_key,
    all_option,
    specific_options,
    persistent_key=None,
):
    """Initialize a scope widget from canonical saved state for a new run."""
    if key in st.session_state:
        current = st.session_state[key]
    else:
        persisted_selection = st.session_state.get(
            persistent_key,
            SEGMENT_SELECTION_ALL,
        )
        if persisted_selection == SEGMENT_SELECTION_ALL:
            current = [all_option]
        elif isinstance(persisted_selection, (list, tuple)):
            persisted_values = set(persisted_selection)
            if persisted_values and persisted_values.issubset(specific_options):
                current = [
                    option
                    for option in specific_options
                    if option in persisted_values
                ]
            else:
                current = [all_option]
                if persistent_key is not None:
                    st.session_state[persistent_key] = SEGMENT_SELECTION_ALL
        else:
            current = [all_option]
            if persistent_key is not None:
                st.session_state[persistent_key] = SEGMENT_SELECTION_ALL
    if isinstance(current, str):
        current = [current]
    previous = st.session_state.get(previous_key, [all_option])
    if isinstance(previous, str):
        previous = [previous]
    normalized = _resolve_explicit_all_selection(current, previous, all_option, specific_options)
    st.session_state[key] = normalized
    st.session_state[previous_key] = normalized

def _update_explicit_all_multiselect(
    key,
    previous_key,
    all_option,
    specific_options,
    persistent_key=None,
):
    """Apply explicit-All behavior and persist a user-generated scope change."""
    current = st.session_state.get(key, [])
    previous = st.session_state.get(previous_key, [all_option])
    normalized = _resolve_explicit_all_selection(current, previous, all_option, specific_options)
    st.session_state[key] = normalized
    st.session_state[previous_key] = normalized
    if persistent_key is not None:
        st.session_state[persistent_key] = (
            SEGMENT_SELECTION_ALL
            if normalized == [all_option]
            else [option for option in specific_options if option in normalized]
        )

def _canonical_specific_selection(selection, all_option, ordered_options):
    """Return selected specific options in their canonical UI order."""
    if all_option in selection:
        return ()
    selected = set(selection)
    return tuple(option for option in ordered_options if option in selected)


def _success_distance_scope_intervals(
    inspector_source_df,
    selected_ranges,
    *,
    max_peer_distance_km,
):
    """Resolve distance intervals before direction filtering for stable bins."""
    if not selected_ranges:
        return ((0.0, float(max_peer_distance_km)),)
    interval_rows = (
        inspector_source_df.loc[
            inspector_source_df["dist_label"].isin(selected_ranges),
            ["dist_label", "r_min", "r_max"],
        ]
        .drop_duplicates(subset=["dist_label"])
        .sort_values(["r_min", "r_max"], kind="stable")
    )
    intervals = tuple(
        (
            float(distance_row.r_min),
            float(distance_row.r_max),
        )
        for distance_row in interval_rows.itertuples(index=False)
    )
    if len(intervals) != len(selected_ranges):
        raise ValueError(
            "Every selected Performance distance range requires stable bounds."
        )
    return intervals


def _selection_summary(selection, all_option, item_kind, translations):
    """Build a compact scope label without losing single-selection detail."""
    if not selection:
        return all_option
    limit = 2 if item_kind == "range" else 4
    if len(selection) <= limit:
        return ", ".join(selection)
    template_key = (
        "fmt_results_selected_range_count"
        if item_kind == "range"
        else "fmt_results_selected_direction_count"
    )
    return translations[template_key].format(count=len(selection))



def _format_metric_or_none(value, decimals=0):
    """Format SNR-like display values, preserving None markers."""
    if pd.isna(value):
        return ""
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped.lower() == "none":
            return "None" if stripped.lower() == "none" else ""
        try:
            number = float(stripped)
        except ValueError:
            return value
    else:
        number = float(value)
    return f"{number:.{decimals}f}"

def _is_snr_display_column(column_name):
    text = str(column_name)
    return (
        "SNR" in text or
        "Norm@" in text or
        "Micro-Med" in text or
        "\u0394" in text or
        "Delta" in text
    )

def _format_snr_display_columns(df):
    """Return a display-only copy with SNR-like columns rendered compactly."""
    display_df = df.copy()
    for col in display_df.columns:
        if _is_snr_display_column(col):
            display_df[col] = display_df[col].map(lambda value: _format_metric_or_none(value, 1))
    return display_df


def _render_reference_correction_notice(
    t,
    *,
    is_compare,
    is_sequential,
    analysis_context,
):
    """Render the completed run's configured correction as a compact notice."""
    note = configured_snr_correction_notice(
        analysis_context,
        t,
        is_compare=is_compare,
        is_sequential=is_sequential,
    )
    if not note:
        return
    st.markdown(
        f"""
        <style>
            @media (min-width: 768px) {{
                .reference-correction-note {{
                    white-space: nowrap;
                    overflow-x: auto;
                }}
            }}
        </style>
        <div class="reference-correction-note" style="font-size:0.78em; color:#9aa4b2; margin-top:-0.15rem; margin-bottom:0.35rem; font-family:'Space Mono', monospace;">
            {escape(note)}
        </div>
        """,
        unsafe_allow_html=True
    )

def _segment_summary_lines(
    station_summary,
    spot_summary,
):
    """Return the available station- and observation-level metric summaries."""
    return [
        summary
        for summary in (station_summary, spot_summary)
        if summary
    ]


def _format_localized_integer(count, translations):
    """Format one evidence count with the active presentation separator."""
    formatted = f"{int(count):,}"
    separator = str(translations["fmt_results_thousands_separator"])
    return formatted if separator == "," else formatted.replace(",", separator)


def _format_localized_decimal(value, translations, *, decimals=1):
    """Format one finite display value without changing its stored precision."""
    numeric_value = float(value)
    if not np.isfinite(numeric_value):
        return "—"
    formatted = f"{numeric_value:.{int(decimals)}f}".replace("-", "−")
    if translations["fmt_results_thousands_separator"] == ".":
        formatted = formatted.replace(".", ",")
    return formatted


def _selected_success_context_line(recipe, translations):
    """Format complete-run context for one selected Performance path."""
    summary = dict((recipe or {}).get("selected_station_summary") or {})
    confirmed_opportunities = int(
        summary.get("confirmed_opportunities", 0)
    )
    opportunity_unit = translations[
        "unit_confirmed_opportunity_singular"
        if confirmed_opportunities == 1
        else "unit_confirmed_opportunity_plural"
    ]
    distance_km = summary.get("distance_km", np.nan)
    distance_text = (
        _format_localized_integer(round(float(distance_km)), translations)
        if pd.notna(distance_km) and np.isfinite(float(distance_km))
        else "—"
    )
    azimuth_degrees = summary.get("azimuth_degrees", np.nan)
    azimuth_text = _format_localized_decimal(
        azimuth_degrees,
        translations,
        decimals=0,
    )
    direction = str(summary.get("direction", "")).strip().upper()
    localized_east = translations["abbr_compass_east"]
    localized_direction = direction.replace("E", localized_east)
    successful_snr_median_db = summary.get(
        "successful_snr_median_db",
        np.nan,
    )
    median_snr_text = (
        f"{_format_localized_decimal(
            successful_snr_median_db,
            translations,
        )} dB"
        if pd.notna(successful_snr_median_db)
        and np.isfinite(float(successful_snr_median_db))
        else "—"
    )
    return translations["fmt_success_selected_context"].format(
        station=str(summary.get("peer_sign", "")).strip().upper(),
        locator=str(summary.get("peer_grid", "")).strip().upper(),
        distance_km=distance_text,
        azimuth_degrees=azimuth_text,
        direction=localized_direction,
        confirmed_opportunities=_format_localized_integer(
            confirmed_opportunities,
            translations,
        ),
        opportunity_unit=opportunity_unit,
        success_rate=_format_localized_decimal(
            summary.get("success_rate_pct", np.nan),
            translations,
        ),
        median_snr=median_snr_text,
    )


def _format_summary_count(count):
    """Format an integer summary count with an apostrophe thousands separator."""
    return f"{int(count):,}".replace(",", "'")


def _compare_metric_distribution_summary(
    values,
    template,
    *,
    total_count=None,
    joint_count=None,
    joint_label="Joint",
):
    """Format one Benchmark distribution summary with optional outcome counts."""
    numeric_values = np.asarray(values, dtype=float)
    numeric_values = numeric_values[np.isfinite(numeric_values)]
    if len(numeric_values) == 0:
        return None

    count_context = ""
    if total_count is not None and joint_count is not None:
        count_context = (
            f" (n={_format_summary_count(total_count)}; "
            f"{joint_label}={_format_summary_count(joint_count)})"
        )

    return template.format(
        count_context=count_context,
        median=f"{float(np.median(numeric_values)):+.1f}",
        mean=f"{float(np.mean(numeric_values)):+.1f}",
    )


def _supports_dataframe_selection_default():
    """Return True when the installed Streamlit version can preselect dataframe rows."""
    try:
        return "selection_default" in inspect.signature(st.dataframe).parameters
    except (TypeError, ValueError):
        return False


def _render_compact_dataframe(container, dataframe, **kwargs):
    """Render a scrollable table with five visible body rows plus its header."""
    return container.dataframe(
        dataframe,
        height=COMPACT_DATAFRAME_HEIGHT_PX,
        row_height=COMPACT_DATAFRAME_ROW_HEIGHT_PX,
        **kwargs,
    )


def _snr_column_config(df):
    """Keep numeric SNR columns right-aligned while controlling displayed precision."""
    config = {}
    for col in df.columns:
        if _is_snr_display_column(col) and pd.api.types.is_numeric_dtype(df[col]):
            config[col] = st.column_config.NumberColumn(format="%.1f")
    return config

























def _format_drilldown_focus_utc(value):
    """Format one UTC bound compactly while retaining non-minute precision."""
    timestamp = pd.Timestamp(value).tz_convert("UTC")
    if timestamp.second or timestamp.microsecond or timestamp.nanosecond:
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp.strftime("%Y-%m-%d %H:%M")


def _drilldown_focus_title(identity_label, focus_window, translations):
    """Return the compact selected-path identity plus exact focused interval."""
    if focus_window is None:
        return str(identity_label)
    return translations["fmt_drilldown_zoom_time_window"].format(
        identity=str(identity_label),
        start=_format_drilldown_focus_utc(focus_window.start_utc),
        end=_format_drilldown_focus_utc(focus_window.end_utc),
    )


def _drilldown_outlier_context_for_scope(
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
    selected_identity,
    analysis_start_utc,
    analysis_end_utc,
):
    """Return validated candidate provenance belonging to this run and path."""
    return drilldown_outlier_candidate_context_for_scope(
        session_state.get(RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY),
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
        selected_identity=selected_identity,
        analysis_start_utc=analysis_start_utc,
        analysis_end_utc=analysis_end_utc,
    )


def _drilldown_focus_time_bin(focus_window):
    """Return the cycle-sized companion-profile bin for one focused view."""
    if focus_window is None:
        return None
    return "2m"


def _drilldown_focus_identity_token(selected_identity):
    """Return a stable compact widget namespace for one selected station."""
    callsign, locator = selected_identity
    return sha256(
        f"{str(callsign).strip().upper()}\0{str(locator).strip().upper()}".encode(
            "utf-8"
        )
    ).hexdigest()[:12]


def _drilldown_focus_center_from_widget_values(date_value, time_value):
    """Combine direct calendar/time inputs into one timezone-aware UTC center."""
    return pd.Timestamp(
        datetime.combine(
            date_value,
            time_value.replace(tzinfo=None),
            tzinfo=timezone.utc,
        )
    )


def _store_drilldown_focus_center(
    session_state,
    *,
    date_key,
    time_key,
    focus_center,
):
    """Write one UTC center into the date/time widget value types."""
    normalized_center = pd.Timestamp(focus_center).tz_convert("UTC")
    session_state[date_key] = normalized_center.date()
    session_state[time_key] = normalized_center.time().replace(tzinfo=None)


def _normalize_drilldown_focus_center_state(
    session_state,
    date_key,
    time_key,
    analysis_start_utc,
    analysis_end_utc,
    option,
):
    """Clamp direct widget values while preserving the chosen full duration."""
    try:
        requested_center = _drilldown_focus_center_from_widget_values(
            session_state[date_key],
            session_state[time_key],
        )
        focus_window = resolve_centered_zoom_window(
            analysis_start_utc,
            analysis_end_utc,
            option,
            requested_center,
        )
    except (KeyError, TypeError, ValueError, OverflowError):
        requested_center = default_focus_center_utc(
            analysis_start_utc,
            analysis_end_utc,
            option,
        )
        focus_window = resolve_centered_zoom_window(
            analysis_start_utc,
            analysis_end_utc,
            option,
            requested_center,
        )
    if focus_window is None:
        return
    _store_drilldown_focus_center(
        session_state,
        date_key=date_key,
        time_key=time_key,
        focus_center=focus_center_utc(focus_window),
    )


def _shift_drilldown_focus_center_state(
    session_state,
    date_key,
    time_key,
    analysis_start_utc,
    analysis_end_utc,
    option,
    direction,
):
    """Move a manual focus center by one complete selected zoom window."""
    _normalize_drilldown_focus_center_state(
        session_state,
        date_key,
        time_key,
        analysis_start_utc,
        analysis_end_utc,
        option,
    )
    current_center = _drilldown_focus_center_from_widget_values(
        session_state[date_key],
        session_state[time_key],
    )
    shifted_center = current_center + int(direction) * pd.Timedelta(
        hours=DRILLDOWN_ZOOM_DURATION_HOURS[option]
    )
    focus_window = resolve_centered_zoom_window(
        analysis_start_utc,
        analysis_end_utc,
        option,
        shifted_center,
    )
    if focus_window is None:
        return
    _store_drilldown_focus_center(
        session_state,
        date_key=date_key,
        time_key=time_key,
        focus_center=focus_center_utc(focus_window),
    )


def _render_drilldown_heading(
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


def _render_drilldown_header_and_controls(
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
    analysis_start_utc,
    analysis_end_utc,
    selected_identity=None,
    allow_multiple_station_selection=False,
):
    """Render plot-focus controls; the table owns its separate filter row."""
    render_page_anchor(DRILLDOWN_ANCHOR_ID)
    _render_drilldown_heading(
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

    manual_options = list(
        available_manual_zoom_options(analysis_start_utc, analysis_end_utc)
    )
    outlier_context = _drilldown_outlier_context_for_scope(
        st.session_state,
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
        selected_identity=selected_identity,
        analysis_start_utc=analysis_start_utc,
        analysis_end_utc=analysis_end_utc,
    )
    if (
        st.session_state.get(RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY)
        is not None
        and outlier_context is None
    ):
        st.session_state.pop(RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY, None)

    if outlier_context is None:
        available_options = manual_options
    else:
        available_options = [
            "off",
            DRILLDOWN_OUTLIER_FOCUS_OPTION,
            *(option for option in manual_options if option != "off"),
        ]
    identity_token = _drilldown_focus_identity_token(selected_identity)
    widget_scope = f"{analysis_id}_{run_id}_{scope_token}_{identity_token}"
    zoom_key = f"d_zoom_{widget_scope}"
    focus_date_key = f"d_zoom_focus_date_{widget_scope}"
    focus_time_key = f"d_zoom_focus_time_{widget_scope}"
    applied_focus_key = f"{zoom_key}_applied_outlier_request"
    applied_option_key = f"{zoom_key}_applied_option"
    if outlier_context is not None:
        if st.session_state.get(applied_focus_key) != outlier_context.request_token:
            st.session_state[zoom_key] = DRILLDOWN_OUTLIER_FOCUS_OPTION
            st.session_state[applied_focus_key] = outlier_context.request_token
            _store_drilldown_focus_center(
                st.session_state,
                date_key=focus_date_key,
                time_key=focus_time_key,
                focus_center=outlier_context.representative_utc,
            )
    if st.session_state.get(zoom_key) not in available_options:
        st.session_state[zoom_key] = "off"

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
        prior_option = st.session_state.get(applied_option_key)
        if (
            focus_date_key not in st.session_state
            or focus_time_key not in st.session_state
            or (
                prior_option
                == DRILLDOWN_OUTLIER_FOCUS_OPTION
                and outlier_context is not None
            )
        ):
            initial_center = (
                outlier_context.representative_utc
                if outlier_context is not None
                else default_focus_center_utc(
                    analysis_start_utc,
                    analysis_end_utc,
                    selected_option,
                )
            )
            _store_drilldown_focus_center(
                st.session_state,
                date_key=focus_date_key,
                time_key=focus_time_key,
                focus_center=initial_center,
            )
        _normalize_drilldown_focus_center_state(
            st.session_state,
            focus_date_key,
            focus_time_key,
            analysis_start_utc,
            analysis_end_utc,
            selected_option,
        )
        earliest_center, latest_center = manual_zoom_center_bounds(
            analysis_start_utc,
            analysis_end_utc,
            selected_option,
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
                on_click=_shift_drilldown_focus_center_state,
                args=(
                    st.session_state,
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
                on_click=_shift_drilldown_focus_center_state,
                args=(
                    st.session_state,
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
                on_change=_normalize_drilldown_focus_center_state,
                args=(
                    st.session_state,
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
                on_change=_normalize_drilldown_focus_center_state,
                args=(
                    st.session_state,
                    focus_date_key,
                    focus_time_key,
                    analysis_start_utc,
                    analysis_end_utc,
                    selected_option,
                ),
            )
        selected_center = _drilldown_focus_center_from_widget_values(
            selected_focus_date,
            selected_focus_time,
        )
        focus_window = resolve_centered_zoom_window(
            analysis_start_utc,
            analysis_end_utc,
            selected_option,
            selected_center,
        )
    else:
        st.session_state.pop(
            RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY,
            None,
        )
        st.session_state.pop(applied_focus_key, None)

    st.session_state[applied_option_key] = selected_option
    if focus_window is not None:
        selected_window_text = translations[
            "fmt_drilldown_zoom_selected_window"
        ].format(
            start=_format_drilldown_focus_utc(focus_window.start_utc),
            end=_format_drilldown_focus_utc(focus_window.end_utc),
        )
        selected_window_display = selected_window_container.container(
            key=f"d_zoom_selected_window_{widget_scope}",
        )
        selected_window_display.caption(selected_window_text)

    focus_time_bin = _drilldown_focus_time_bin(focus_window)
    return focus_window, focus_time_bin, None


def _render_drilldown_dataframe(
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
        _render_drilldown_heading(
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
                        step = 1.0 if pd.api.types.is_integer_dtype(drill_df[col]) else 0.1
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

    _render_reference_correction_notice(
        t,
        is_compare=is_compare,
        is_sequential=is_sequential,
        analysis_context=analysis_context,
    )
    with _timed_span(timing_collector, "drilldown dataframe render"):
        drill_display_df = _format_snr_display_columns(display_drill_df)
        _render_compact_dataframe(
            st,
            drill_display_df,
            width="stretch",
            hide_index=True,
        )
    return canonical_drill_df.loc[display_drill_df.index].copy()


def _drilldown_zoom_export_metadata(
    focus_window,
    *,
    selected_identity,
    metric_recipe,
    outlier_context=None,
):
    """Return the strict optional export identity for one focused view."""
    if (
        focus_window is None
        or selected_identity is None
        or not isinstance(metric_recipe, Mapping)
    ):
        return None
    callsign, locator = selected_identity
    metadata = {
        "schema_version": DRILLDOWN_FOCUS_SCHEMA_VERSION,
        "station": {
            "callsign": str(callsign).strip().upper(),
            "locator": str(locator).strip().upper(),
        },
        "start_utc": focus_window.start_utc.isoformat(),
        "end_utc": focus_window.end_utc.isoformat(),
        "option": focus_window.option,
        "origin": focus_window.origin,
        "time_bin": str(metric_recipe.get("time_bin") or ""),
        "resolution": str(metric_recipe.get("resolution") or ""),
        "aggregation": str(metric_recipe.get("aggregation") or ""),
        "layout_version": DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
    }
    if outlier_context is not None:
        metadata["outlier_candidate"] = {
            "request_token": outlier_context.request_token,
            "detector_version": outlier_context.detector_version,
            "candidate_signature": outlier_context.candidate_signature,
            "representative_utc": (
                outlier_context.representative_utc.isoformat()
            ),
            "representative_delta_snr_db": (
                outlier_context.representative_delta_snr_db
            ),
            "event_start_utc": outlier_context.event_start_utc.isoformat(),
            "event_end_utc": outlier_context.event_end_utc.isoformat(),
            "pre_flank_start_utc": (
                outlier_context.pre_flank_start_utc.isoformat()
            ),
            "pre_flank_end_utc": (
                outlier_context.pre_flank_end_utc.isoformat()
            ),
            "post_flank_start_utc": (
                outlier_context.post_flank_start_utc.isoformat()
            ),
            "post_flank_end_utc": (
                outlier_context.post_flank_end_utc.isoformat()
            ),
            "local_baseline_db": outlier_context.local_baseline_db,
            "pre_baseline_db": outlier_context.pre_baseline_db,
            "post_baseline_db": outlier_context.post_baseline_db,
            "robust_spread_db": outlier_context.robust_spread_db,
            "robust_spread_method": outlier_context.robust_spread_method,
            "robust_z": outlier_context.robust_z,
            "minimum_robust_z": outlier_context.minimum_robust_z,
            "minimum_departure_db": outlier_context.minimum_departure_db,
        }
    return metadata


def _build_performance_drilldown_zoom_recipes(
    selected_base_recipe,
    selected_peer_rows,
    selected_station_rows,
    selected_identity_label,
    focus_window,
    focus_time_bin,
    translations,
):
    """Build native SNR plus cycle-resolution outcome evidence for one path."""
    if focus_window is None or selected_base_recipe is None:
        return None, None
    zoom_title = _drilldown_focus_title(
        selected_identity_label,
        focus_window,
        translations,
    )
    native_snr_recipe = build_drilldown_zoom_performance_snr_recipe(
        selected_station_rows,
        start_utc=focus_window.start_utc,
        end_utc=focus_window.end_utc,
        title=zoom_title,
        panel_title=translations[
            "fig_drilldown_native_performance_panel_title"
        ],
        x_label=translations["fig_drilldown_native_time_x"],
        y_label=translations["fig_drilldown_native_performance_y"],
        empty_text=translations[
            "fig_drilldown_native_performance_unavailable"
        ],
        evidence_unit_label=translations[
            "fig_drilldown_native_successful_opportunity"
        ],
    )
    focused_evidence_recipe = _opportunity_temporal_recipe(
        zoom_title,
        selected_base_recipe["selected_segment"],
        selected_peer_rows,
        selected_station_rows,
        focus_window.start_utc,
        focus_window.end_utc,
        selected_base_recipe["terminology"],
        figure_labels=selected_base_recipe["labels"],
        snr_title=zoom_title,
        population_mode=SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
        snr_representation=SUCCESS_SNR_REPRESENTATION_ACTUAL,
        time_bin_options=(focus_time_bin,),
        time_bin_default=focus_time_bin,
    )
    focused_evidence_recipe["time_bin"] = focus_time_bin
    return native_snr_recipe, dict(focused_evidence_recipe)


def _build_benchmark_drilldown_zoom_recipes(
    station_df,
    selected_identity_df,
    thresholded_station_rows,
    is_sequential,
    analysis_context,
    focus_window,
    focus_time_bin,
    full_delta_recipe,
    full_coverage_recipe,
    translations,
    outlier_context=None,
    outlier_model=None,
):
    """Build native selected-path Delta-SNR and focused coverage recipes."""
    if (
        focus_window is None
        or full_delta_recipe is None
        or full_coverage_recipe is None
    ):
        return None, None
    identity_meta = _prepare_identity_meta(selected_identity_df)
    if len(identity_meta) != 1:
        return None, None
    comparison_units = _build_compare_unit_rows(
        station_df,
        identity_meta,
        is_sequential,
        paired_identity_df=identity_meta,
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
    comparison_units = _retain_thresholded_compare_outcomes(
        comparison_units,
        thresholded_station_rows,
    )
    evidence_utc = pd.to_datetime(
        comparison_units.get("evidence_utc"),
        errors="coerce",
        utc=True,
    )
    comparison_units = comparison_units.loc[
        evidence_utc.notna()
        & evidence_utc.ge(focus_window.start_utc)
        & evidence_utc.lt(focus_window.end_utc)
    ].copy()
    evidence_df = _compare_joint_evidence_points(
        comparison_units,
        preserve_metric_precision=True,
    )
    selected_identity_label = str(identity_meta.iloc[0]["identity"])
    zoom_title = _drilldown_focus_title(
        selected_identity_label,
        focus_window,
        translations,
    )
    outlier_overlay = None
    qualifying_marker_recipe_builder = getattr(
        outlier_model,
        "qualifying_unit_marker_recipe",
        None,
    )
    has_current_outlier_model = (
        outlier_context is not None
        and getattr(outlier_model, "detector_version", None)
        == DELTA_SNR_OUTLIER_DETECTOR_VERSION
        and outlier_context.detector_version
        == DELTA_SNR_OUTLIER_DETECTOR_VERSION
        and getattr(outlier_model, "candidate_signature", None)
        == outlier_context.candidate_signature
        and callable(qualifying_marker_recipe_builder)
    )
    if (
        has_current_outlier_model
        and outlier_context.event_start_utc < focus_window.end_utc
        and outlier_context.event_end_utc > focus_window.start_utc
    ):
        qualifying_marker_times_utc = []
        qualifying_marker_delta_snr_db = []
        qualifying_marker_recipe = qualifying_marker_recipe_builder(
            [
                (
                    str(identity_meta.iloc[0]["peer_sign"]),
                    str(identity_meta.iloc[0]["peer_grid"]),
                )
            ],
            start_utc=focus_window.start_utc,
            end_utc=focus_window.end_utc,
        )
        if isinstance(qualifying_marker_recipe, Mapping):
            for marker in qualifying_marker_recipe.get("markers", ()):
                if not isinstance(marker, Mapping):
                    continue
                qualifying_marker_times_utc.append(
                    pd.Timestamp(
                        int(marker["marker_utc_ns"]),
                        unit="ns",
                        tz="UTC",
                    )
                )
                qualifying_marker_delta_snr_db.append(
                    float(marker["marker_delta_snr_db"])
                )

        native_evidence_unit_minutes = (
            analysis_context.tx_ab_repeat_interval_minutes
            if is_sequential
            else 2.0
        )
        outlier_overlay = build_drilldown_zoom_outlier_overlay_recipe(
            representative_utc=outlier_context.representative_utc,
            representative_delta_snr_db=(
                outlier_context.representative_delta_snr_db
            ),
            qualifying_marker_times_utc=qualifying_marker_times_utc,
            qualifying_marker_delta_snr_db=(
                qualifying_marker_delta_snr_db
            ),
            candidate_start_utc=outlier_context.event_start_utc,
            candidate_end_utc=outlier_context.event_end_utc,
            native_evidence_unit_minutes=native_evidence_unit_minutes,
            local_baseline_db=outlier_context.local_baseline_db,
            pre_baseline_db=outlier_context.pre_baseline_db,
            post_baseline_db=outlier_context.post_baseline_db,
            pre_flank_start_utc=outlier_context.pre_flank_start_utc,
            pre_flank_end_utc=outlier_context.pre_flank_end_utc,
            post_flank_start_utc=outlier_context.post_flank_start_utc,
            post_flank_end_utc=outlier_context.post_flank_end_utc,
            robust_spread_db=outlier_context.robust_spread_db,
            robust_spread_method=outlier_context.robust_spread_method,
            minimum_robust_z=outlier_context.minimum_robust_z,
            minimum_departure_db=outlier_context.minimum_departure_db,
            labels={
                "marker": translations["fig_drilldown_outlier_candidate"],
                "focused_episode": translations[
                    "fig_drilldown_outlier_focused_episode"
                ],
                "local_baseline": translations[
                    "fig_drilldown_outlier_expected_local_delta_snr"
                ],
                "flank_baseline": translations[
                    "fig_drilldown_outlier_flank_baseline"
                ],
                "robust_z": translations[
                    "fmt_drilldown_outlier_robust_z_guide"
                ],
                "qualifying_robust_z": translations[
                    "fmt_drilldown_outlier_qualifying_robust_z_guide"
                ],
                "absolute_departure": translations[
                    "fmt_drilldown_outlier_absolute_departure_gate"
                ],
            },
        )
    delta_recipe = build_drilldown_zoom_benchmark_delta_snr_recipe(
        evidence_df,
        start_utc=focus_window.start_utc,
        end_utc=focus_window.end_utc,
        title=zoom_title,
        panel_title=translations[
            "fig_drilldown_native_benchmark_panel_title"
        ],
        x_label=translations["fig_drilldown_native_time_x"],
        y_label=translations["fig_drilldown_native_benchmark_y"],
        empty_text=translations[
            "fig_drilldown_native_benchmark_unavailable"
        ],
        evidence_unit_label=translations[
            "fig_drilldown_native_scheduled_pair"
            if is_sequential
            else "fig_drilldown_native_joint_spot"
        ],
        is_sequential=is_sequential,
        reference_snr_correction_notice=full_delta_recipe.get(
            "reference_snr_correction_notice",
            "",
        ),
        outlier_overlay=outlier_overlay,
    )
    coverage_recipe = _compare_coverage_recipe(
        comparison_units,
        coverage_title=zoom_title,
        selected_segment=full_coverage_recipe["selected_segment"],
        analysis_start_t=focus_window.start_utc,
        analysis_end_t=focus_window.end_utc,
        time_bin_options=(focus_time_bin,),
        time_bin_default=focus_time_bin,
        figure_labels=full_coverage_recipe["labels"],
        population_mode=SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    )
    return delta_recipe, coverage_recipe




def _selected_evidence_figure_title(
    station_identities,
    evidence_count,
    *,
    analysis_id,
    is_sequential,
    translations,
    allow_multiple=False,
):
    """Build a localized selected-station figure title from semantic evidence."""
    heading = translations["hdr_results_selected_station_evidence"]
    selection_context = selected_station_context(
        station_identities,
        evidence_count,
        analysis_id=analysis_id,
        is_sequential=is_sequential,
        translations=translations,
        allow_multiple=allow_multiple,
    )
    return translations[
        "fmt_results_selected_station_evidence_title"
    ].format(
        heading=heading,
        selection_context=selection_context,
    )


def _delta_snr_outlier_marker_recipe(
    outlier_model,
    translations,
    station_identities=None,
):
    """Return localized markers at episode or selected-path resolution."""
    if outlier_model is None:
        return None
    marker_recipe = outlier_model.marker_recipe(station_identities)
    if marker_recipe is None:
        return None
    report_entries = getattr(outlier_model, "report_entries", None)
    if station_identities is None and report_entries is not None:
        representative_keys = {
            (
                strongest_candidate.station_identity.callsign,
                strongest_candidate.station_identity.locator,
                int(strongest_candidate.representative_utc.value),
            )
            for report_entry in report_entries
            if report_entry.candidates
            for strongest_candidate in (
                max(
                    report_entry.candidates,
                    key=lambda candidate: abs(
                        candidate.representative_delta_snr_db
                        - candidate.station_baseline_db
                    ),
                ),
            )
        }
        episode_markers = [
            marker
            for marker in marker_recipe["markers"]
            if (
                marker["callsign"],
                marker["locator"],
                int(marker["marker_utc_ns"]),
            )
            in representative_keys
        ]
        if not episode_markers:
            return None
        marker_recipe = dict(marker_recipe)
        marker_recipe["markers"] = episode_markers
        marker_recipe["candidate_count"] = len(episode_markers)
        marker_recipe["candidate_signature"] = sha256(
            json.dumps(
                episode_markers,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
        ).hexdigest()
    marker_recipe["legend_label"] = translations[
        "fig_delta_snr_outlier_candidate"
    ]
    return marker_recipe


def _outlier_station_direction_lookup(scope_rows):
    """Return exact station identities mapped to retained compass sectors."""
    required_columns = {"peer_sign", "peer_grid", "dir_name"}
    if (
        scope_rows is None
        or scope_rows.empty
        or not required_columns.issubset(scope_rows.columns)
    ):
        return {}
    direction_lookup = {}
    for callsign, locator, direction in scope_rows[
        ["peer_sign", "peer_grid", "dir_name"]
    ].itertuples(index=False, name=None):
        callsign_text = str(callsign).strip().upper()
        locator_text = str(locator).strip().upper()
        direction_text = str(direction).strip().upper()
        if (
            callsign_text
            and locator_text
            and direction_text in COMPASS
        ):
            direction_lookup.setdefault(
                (callsign_text, locator_text),
                direction_text,
            )
    return direction_lookup


def _format_signed_outlier_db(value, translations):
    """Format one signed dB value with the active decimal separator."""
    numeric_value = float(value)
    sign = "+" if numeric_value >= 0.0 else "\u2212"
    return f"{sign}{_format_localized_decimal(abs(numeric_value), translations)}"


def _format_outlier_utc_interval(start_utc, end_utc, translations):
    """Format one exact UTC interval without relying on process locale."""
    interval_start = pd.Timestamp(start_utc).tz_convert("UTC")
    interval_end = pd.Timestamp(end_utc).tz_convert("UTC")
    is_same_date = interval_start.date() == interval_end.date()
    month_names = str(translations["txt_outlier_utc_months"]).split("|")
    if len(month_names) != 12:
        raise ValueError("Outlier UTC month catalog must contain 12 entries.")

    def format_date(timestamp):
        return translations["fmt_outlier_utc_date"].format(
            day=timestamp.day,
            month=month_names[timestamp.month - 1],
            time=timestamp.strftime("%H:%M"),
        )

    start_text = format_date(interval_start)
    end_text = (
        interval_end.strftime("%H:%M")
        if is_same_date
        else format_date(interval_end)
    )
    return translations["fmt_outlier_utc_range"].format(
        start=start_text,
        end=end_text,
    )


def _format_outlier_utc_range(report_entry, translations):
    """Format exact observed UTC bounds without exposing half-open sentinels."""
    interval_start = pd.Timestamp(report_entry.start_utc).tz_convert("UTC")
    interval_end = pd.Timestamp(report_entry.end_utc).tz_convert("UTC")
    if interval_end - interval_start <= pd.Timedelta(nanoseconds=1):
        month_names = str(translations["txt_outlier_utc_months"]).split("|")
        if len(month_names) != 12:
            raise ValueError(
                "Outlier UTC month catalog must contain 12 entries."
            )
        timestamp_text = translations["fmt_outlier_utc_date"].format(
            day=interval_start.day,
            month=month_names[interval_start.month - 1],
            time=interval_start.strftime("%H:%M"),
        )
        return translations["fmt_outlier_utc_instant"].format(
            timestamp=timestamp_text,
        )
    if interval_end > interval_start:
        interval_end -= pd.Timedelta(nanoseconds=1)
    return _format_outlier_utc_interval(
        interval_start,
        interval_end,
        translations,
    )


def _localized_outlier_direction(direction, translations):
    """Localize the east component of one canonical compass sector."""
    return str(direction).replace(
        "E",
        translations["abbr_compass_east"],
    )


def _format_outlier_duration_minutes(value, translations):
    """Format an observed episode duration without false decimal precision."""
    numeric_value = float(value)
    decimals = 0 if np.isclose(numeric_value, round(numeric_value)) else 1
    return translations["fmt_outlier_minutes"].format(
        value=_format_localized_decimal(
            numeric_value,
            translations,
            decimals=decimals,
        )
    )


def _localized_outlier_event_kind(event_kind, translations):
    """Return the approved label for one detector event classification."""
    event_keys = {
        "spot_impulse": "txt_outlier_event_spot_impulse",
        "short_burst": "txt_outlier_event_short_burst",
        "sustained_excursion": "txt_outlier_event_sustained_excursion",
        "mixed_duration": "txt_outlier_event_mixed_duration",
    }
    try:
        return translations[event_keys[str(event_kind)]]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported Delta-SNR outlier event kind: {event_kind!r}."
        ) from exc


def _validate_outlier_report_entry_counts(report_entry):
    """Validate one episode's narrowing path denominators."""
    contributing_count = int(report_entry.contributing_station_count)
    evaluable_count = int(report_entry.evaluable_station_count)
    flagged_count = int(report_entry.flagged_station_count)
    sign_counts = (
        int(report_entry.segment_positive_station_count),
        int(report_entry.segment_negative_station_count),
        int(report_entry.segment_neutral_station_count),
    )
    if not 0 <= flagged_count <= evaluable_count <= contributing_count:
        raise ValueError(
            "Outlier episode path counts must satisfy "
            "flagged <= assessed <= paired evidence."
        )
    if any(count < 0 for count in sign_counts):
        raise ValueError("Outlier episode sign counts must be non-negative.")
    if sum(sign_counts) != evaluable_count:
        raise ValueError(
            "Outlier episode above, below, and unchanged counts must sum "
            "to the assessed-path count."
        )
    return contributing_count - evaluable_count


def _format_outlier_named_paired_unit_count(
    count,
    is_sequential,
    translations,
):
    """Name any complete paired-unit count in established WSPRadar terms."""
    unit_kind = "scheduled" if is_sequential else "joint"
    count = int(count)
    number = "singular" if count == 1 else "plural"
    return translations[f"fmt_outlier_{unit_kind}_count_{number}"].format(
        count=_format_localized_integer(count, translations)
    )


def _candidate_joint_evidence_times(candidate, episode_card):
    """Return the exact listed Joint timestamps belonging to one path episode."""
    episode_start_utc = pd.Timestamp(candidate.start_utc).tz_convert("UTC")
    episode_end_utc = pd.Timestamp(candidate.end_utc).tz_convert("UTC")
    evidence_times = tuple(
        sorted(
            {
                pd.Timestamp(evidence_row.evidence_utc).tz_convert("UTC")
                for evidence_row in episode_card.evidence_rows
                if evidence_row.station_identity == candidate.station_identity
                and episode_start_utc
                <= pd.Timestamp(evidence_row.evidence_utc).tz_convert("UTC")
                < episode_end_utc
            }
        )
    )
    if len(evidence_times) != int(candidate.paired_unit_count):
        raise ValueError(
            "Listed Joint evidence must match the detector episode count."
        )
    return evidence_times


def _format_outlier_optional_minutes(value, translations):
    """Format one minute interval or an em dash when no interval exists."""
    if value is None:
        return OUTLIER_UNAVAILABLE_VALUE
    return _format_outlier_duration_minutes(value, translations)


def _format_outlier_candidate_facts(
    candidate,
    episode_card,
    translations,
    is_sequential,
):
    """Format path-centred evidence timing and Delta-SNR interpretation facts."""
    evidence_times = _candidate_joint_evidence_times(candidate, episode_card)
    first_to_last_minutes = (
        evidence_times[-1] - evidence_times[0]
    ).total_seconds() / 60.0
    interval_minutes = [
        (later_utc - earlier_utc).total_seconds() / 60.0
        for earlier_utc, later_utc in zip(
            evidence_times,
            evidence_times[1:],
        )
    ]
    median_interval_minutes = (
        float(np.median(interval_minutes)) if interval_minutes else None
    )
    largest_gap_minutes = max(interval_minutes) if interval_minutes else None
    observation_context = translations[
        "fmt_outlier_path_observation_context"
    ].format(
        paired_count=_format_outlier_named_paired_unit_count(
            len(evidence_times),
            is_sequential,
            translations,
        ),
        first_to_last_span=_format_outlier_duration_minutes(
            first_to_last_minutes,
            translations,
        ),
        median_interval=_format_outlier_optional_minutes(
            median_interval_minutes,
            translations,
        ),
        largest_gap=_format_outlier_optional_minutes(
            largest_gap_minutes,
            translations,
        ),
    )
    delta_context = translations["fmt_outlier_path_delta_context"].format(
        expected_local=_format_signed_outlier_db(
            candidate.station_baseline_db,
            translations,
        ),
        observed_median=_format_signed_outlier_db(
            candidate.episode_median_delta_snr_db,
            translations,
        ),
        largest_departure=_format_signed_outlier_db(
            candidate.peak_anomaly_db,
            translations,
        ),
    )
    return f"{observation_context}\n\n{delta_context}"


def _format_outlier_table_db(value, translations):
    """Format one signed table value or an em dash for unavailable evidence."""
    if value is None:
        return OUTLIER_UNAVAILABLE_VALUE
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return OUTLIER_UNAVAILABLE_VALUE
    if not np.isfinite(numeric_value):
        return OUTLIER_UNAVAILABLE_VALUE
    return _format_signed_outlier_db(numeric_value, translations)


def _format_outlier_evidence_utc(evidence_utc, translations):
    """Format one exact native evidence timestamp in UTC."""
    timestamp = pd.Timestamp(evidence_utc).tz_convert("UTC")
    return translations["fmt_outlier_evidence_utc"].format(
        timestamp=timestamp.strftime("%Y-%m-%d %H:%M"),
    )


def _build_outlier_cycle_evidence_table(
    episode_card,
    translations,
):
    """Build the compact chronological table of episode-member Joint rows."""
    columns = [
        translations["col_outlier_evidence_utc"],
        translations["col_outlier_evidence_path"],
        translations["col_outlier_evidence_direction"],
        translations["col_outlier_evidence_local_baseline"],
        translations["col_outlier_evidence_delta_snr"],
        translations["col_outlier_evidence_residual"],
    ]
    rows = []
    for evidence_row in episode_card.evidence_rows:
        direction = (
            _localized_outlier_direction(
                evidence_row.direction_sector,
                translations,
            )
            if evidence_row.direction_sector in COMPASS
            else OUTLIER_UNAVAILABLE_VALUE
        )
        rows.append(
            {
                columns[0]: _format_outlier_evidence_utc(
                    evidence_row.evidence_utc,
                    translations,
                ),
                columns[1]: evidence_row.station_identity.label,
                columns[2]: direction,
                columns[3]: _format_outlier_table_db(
                    evidence_row.local_baseline_db,
                    translations,
                ),
                columns[4]: _format_outlier_table_db(
                    evidence_row.delta_snr_db,
                    translations,
                ),
                columns[5]: _format_outlier_table_db(
                    evidence_row.residual_db,
                    translations,
                ),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def _outlier_candidates_by_identity(report_entry):
    """Group one report entry's candidates in detector path order."""
    candidates_by_identity = {}
    for candidate in report_entry.candidates:
        candidates_by_identity.setdefault(
            candidate.station_identity,
            [],
        ).append(candidate)
    grouped_candidates = []
    for station_identity in report_entry.station_identities:
        path_candidates = tuple(
            candidates_by_identity.get(station_identity, ())
        )
        if not path_candidates:
            raise ValueError(
                "Every flagged episode path must retain a candidate."
            )
        grouped_candidates.append((station_identity, path_candidates))
    return tuple(grouped_candidates)


def _outlier_candidate_direction_text(candidates, translations):
    """Return the retained direction or an explicit unavailable label."""
    directions = tuple(
        dict.fromkeys(
            _localized_outlier_direction(
                candidate.direction_sector,
                translations,
            )
            for candidate in candidates
            if candidate.direction_sector in COMPASS
        )
    )
    return ", ".join(directions) or translations[
        "txt_outlier_direction_unavailable"
    ]


def _select_outlier_station_identities(
    station_identities,
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
    navigation_anchor_id=STATION_INSIGHTS_ANCHOR_ID,
    preserve_drilldown_focus=False,
):
    """Select, focus, and navigate to exact detector path identities."""
    selected_identities = [
        {
            "callsign": station_identity.callsign,
            "locator": station_identity.locator,
        }
        for station_identity in dict.fromkeys(station_identities)
    ]
    session_state[
        RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY
    ] = selected_identities
    if not preserve_drilldown_focus:
        session_state.pop(
            RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY,
            None,
        )
    current_revision = session_state.get(
        RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY,
        0,
    )
    if isinstance(current_revision, bool) or not isinstance(
        current_revision,
        Integral,
    ):
        current_revision = 0
    session_state[
        RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY
    ] = int(current_revision) + 1
    session_state[
        RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY
    ] = {
        "analysis_id": analysis_id,
        "run_id": run_id,
        "scope_token": scope_token,
        "station_identities": selected_identities,
    }
    request_page_navigation(
        session_state,
        navigation_anchor_id,
        should_scroll=True,
    )
    return selected_identities


def _select_outlier_path(
    station_identity,
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
):
    """Show exactly one qualifying detector path in Station Insights."""
    return _select_outlier_station_identities(
        (station_identity,),
        session_state,
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
    )


def _select_outlier_candidate(
    candidate,
    outlier_model,
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
    navigation_anchor_id,
):
    """Preload one exact Outlier Focus and navigate to its selected path."""
    context_bounds = build_delta_snr_outlier_context_bounds(
        candidate,
        analysis_start_utc=outlier_model.analysis_start_utc,
        analysis_end_utc=outlier_model.analysis_end_utc,
    )
    request_payload = {
        "schema_version": DRILLDOWN_OUTLIER_CONTEXT_SCHEMA_VERSION,
        "analysis_id": analysis_id,
        "run_id": run_id,
        "scope_token": scope_token,
        "callsign": candidate.station_identity.callsign,
        "locator": candidate.station_identity.locator,
        "event_start_utc_ns": int(candidate.start_utc.value),
        "event_end_utc_ns": int(candidate.end_utc.value),
        "representative_utc_ns": int(candidate.representative_utc.value),
        "representative_delta_snr_db": float(
            candidate.representative_delta_snr_db
        ),
        "local_baseline_db": float(candidate.station_baseline_db),
        "pre_baseline_db": float(candidate.pre_baseline_db),
        "post_baseline_db": float(candidate.post_baseline_db),
        "robust_spread_db": float(candidate.robust_spread_db),
        "robust_spread_method": candidate.robust_spread_method,
        "robust_z": float(candidate.robust_z),
        "minimum_robust_z": float(
            outlier_model.detection_policy.minimum_robust_z
        ),
        "minimum_departure_db": float(
            outlier_model.detection_policy.minimum_departure_db
        ),
        "baseline_anchor_start_utc_ns": int(
            candidate.baseline_anchor_start_utc.value
        ),
        "baseline_anchor_end_utc_ns": int(
            candidate.baseline_anchor_end_utc.value
        ),
        "episode_guard_minutes": float(candidate.episode_guard_minutes),
        "pre_flank_start_utc_ns": int(
            context_bounds.pre_flank_start_utc.value
        ),
        "pre_flank_end_utc_ns": int(
            context_bounds.pre_flank_end_utc.value
        ),
        "post_flank_start_utc_ns": int(
            context_bounds.post_flank_start_utc.value
        ),
        "post_flank_end_utc_ns": int(
            context_bounds.post_flank_end_utc.value
        ),
        "detector_version": outlier_model.detector_version,
        "candidate_signature": outlier_model.candidate_signature,
    }
    request_payload["request_token"] = sha256(
        json.dumps(
            request_payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    session_state[RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY] = request_payload
    return _select_outlier_station_identities(
        (candidate.station_identity,),
        session_state,
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
        navigation_anchor_id=navigation_anchor_id,
        preserve_drilldown_focus=True,
    )


def _select_outlier_episode_paths(
    report_entry,
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
):
    """Show all unique qualifying paths from one event in Station Insights."""
    return _select_outlier_station_identities(
        report_entry.station_identities,
        session_state,
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
    )


def _render_outlier_candidate_navigation(
    parent_container,
    candidate,
    outlier_model,
    *,
    candidate_key_suffix,
    analysis_id,
    run_id,
    scope_token,
    translations,
):
    """Render the two candidate-specific downward navigation actions."""
    action_container = parent_container.container(
        key=f"outlier_path_actions_{candidate_key_suffix}",
        horizontal=True,
        horizontal_alignment="right",
        vertical_alignment="center",
        gap="small",
    )
    if action_container.button(
        translations["btn_outlier_show_path_in_station_insights"],
        key=f"show_outlier_station_{candidate_key_suffix}",
        type="tertiary",
    ):
        _select_outlier_candidate(
            candidate,
            outlier_model,
            st.session_state,
            analysis_id=analysis_id,
            run_id=run_id,
            scope_token=scope_token,
            navigation_anchor_id=STATION_INSIGHTS_ANCHOR_ID,
        )
        st.rerun(scope="app")
    if action_container.button(
        translations["btn_outlier_show_drilldown_details"],
        key=f"show_outlier_drilldown_{candidate_key_suffix}",
        type="tertiary",
    ):
        _select_outlier_candidate(
            candidate,
            outlier_model,
            st.session_state,
            analysis_id=analysis_id,
            run_id=run_id,
            scope_token=scope_token,
            navigation_anchor_id=DRILLDOWN_ANCHOR_ID,
        )
        st.rerun(scope="app")


def _render_delta_snr_outlier_report(
    outlier_model,
    report_view_model,
    *,
    t,
    language,
    analysis_id,
    run_id,
    scope_token,
    is_sequential,
    analysis_context,
):
    """Render native shared-gate detector episodes as review cards."""
    if outlier_model is None or report_view_model is None:
        raise ValueError(
            "Enabled Delta-SNR outlier reporting requires detector and "
            "report view models."
        )
    report_title = t["hdr_results_outlier_report"]
    st.markdown(
        evidence_child_header_html(
            report_title,
            t["sub_results_outlier_report"],
        ),
        unsafe_allow_html=True,
    )
    render_result_guidance_popover(
        RESULT_GUIDANCE_OUTLIER_REPORT,
        report_title,
        language=language,
        translations=t,
        key=(
            f"results_guidance_outlier_report_"
            f"{analysis_id}_{run_id}_{scope_token}"
        ),
        analysis_id=analysis_id,
        is_compare=True,
        is_sequential=is_sequential,
        analysis_context=analysis_context,
    )
    report_entries = outlier_model.report_entries
    paired_evidence_name = t[
        "txt_outlier_paired_evidence_scheduled"
        if is_sequential
        else "txt_outlier_paired_evidence_joint"
    ]
    if outlier_model.populated_station_cycle_count == 0:
        st.info(
            t["msg_outlier_report_insufficient_paired_evidence"].format(
                paired_evidence=paired_evidence_name,
            ),
            icon=":material/info:",
        )
        return
    if outlier_model.evaluable_station_cycle_count == 0:
        st.info(
            t["msg_outlier_report_insufficient_local_baseline"].format(
                populated=_format_localized_integer(
                    outlier_model.populated_station_cycle_count,
                    t,
                ),
                abstained=_format_localized_integer(
                    outlier_model.abstained_station_cycle_count,
                    t,
                ),
                paired_evidence=paired_evidence_name,
            ),
            icon=":material/info:",
        )
        return
    if not report_entries:
        st.info(
            t["msg_outlier_report_no_candidates"].format(
                assessed=_format_localized_integer(
                    outlier_model.evaluable_station_cycle_count,
                    t,
                ),
                abstained=_format_localized_integer(
                    outlier_model.abstained_station_cycle_count,
                    t,
                ),
                populated=_format_localized_integer(
                    outlier_model.populated_station_cycle_count,
                    t,
                ),
                paired_evidence=paired_evidence_name,
            ),
            icon=":material/search_off:",
        )
        return

    if len(report_view_model.cards) != len(report_entries):
        raise ValueError(
            "Delta-SNR report view-model cards must match detector entries."
        )
    evidence_expander_key = (
        "exp_outlier_scheduled_pair_evidence"
        if is_sequential
        else "exp_outlier_wspr_cycle_evidence"
    )
    for episode_card, report_entry in zip(
        report_view_model.cards,
        report_entries,
    ):
        if episode_card.report_entry != report_entry:
            raise ValueError(
                "Delta-SNR report view-model entry order is inconsistent."
            )
        _validate_outlier_report_entry_counts(report_entry)
        episode_start_utc = pd.Timestamp(report_entry.start_utc)
        episode_end_utc = pd.Timestamp(report_entry.end_utc)
        episode_key_suffix = (
            f"{analysis_id}_{run_id}_{scope_token}_"
            f"{report_entry.episode_index}_"
            f"{episode_start_utc.value}_{episode_end_utc.value}_"
            f"{outlier_model.candidate_signature[:12]}"
        )
        episode_container = st.container(
            border=True,
            key=f"outlier_episode_{episode_key_suffix}",
        )
        episode_utc_range = _format_outlier_utc_range(report_entry, t)
        episode_container.markdown(
            f"##### {_localized_outlier_event_kind(report_entry.event_kind, t)} · "
            f"{episode_utc_range}"
        )
        grouped_candidates = _outlier_candidates_by_identity(report_entry)
        for path_index, (station_identity, path_candidates) in enumerate(
            grouped_candidates,
            start=1,
        ):
            path_heading = (
                "###### "
                + t["fmt_outlier_path_heading"].format(
                    index=_format_localized_integer(path_index, t),
                    identity=station_identity.label,
                    direction=_outlier_candidate_direction_text(
                        path_candidates,
                        t,
                    ),
                )
            )
            if len(path_candidates) > 1:
                episode_container.markdown(path_heading)
            for candidate in path_candidates:
                candidate_key_suffix = (
                    f"{episode_key_suffix}_{path_index}_"
                    f"{station_identity.callsign}_{station_identity.locator}_"
                    f"{int(candidate.start_utc.value)}_"
                    f"{int(candidate.end_utc.value)}"
                )
                path_heading_container = episode_container.container(
                    key=f"outlier_path_heading_{candidate_key_suffix}",
                    horizontal=True,
                    horizontal_alignment="distribute",
                    vertical_alignment="center",
                    gap="small",
                )
                if len(path_candidates) > 1:
                    path_heading_container.markdown(
                        "**"
                        + t["fmt_outlier_candidate_timeframe"].format(
                            utc_range=_format_outlier_utc_range(
                                candidate,
                                t,
                            )
                        )
                        + "**"
                    )
                else:
                    path_heading_container.markdown(path_heading)
                _render_outlier_candidate_navigation(
                    path_heading_container,
                    candidate,
                    outlier_model,
                    candidate_key_suffix=candidate_key_suffix,
                    analysis_id=analysis_id,
                    run_id=run_id,
                    scope_token=scope_token,
                    translations=t,
                )
                episode_container.caption(
                    _format_outlier_candidate_facts(
                        candidate,
                        episode_card,
                        t,
                        is_sequential,
                    )
                )
        if report_entry.flagged_station_count > 1:
            if episode_container.button(
                t["btn_outlier_show_all_paths_in_station_insights"],
                key=f"show_all_outlier_paths_{episode_key_suffix}",
                type="tertiary",
                icon=":material/checklist:",
            ):
                _select_outlier_episode_paths(
                    report_entry,
                    st.session_state,
                    analysis_id=analysis_id,
                    run_id=run_id,
                    scope_token=scope_token,
                )
                st.rerun(scope="app")
        if len(episode_card.evidence_rows) > 1:
            evidence_expander = episode_container.expander(
                t[evidence_expander_key].format(
                    utc_range=episode_utc_range,
                ),
                expanded=False,
                key=f"outlier_cycle_evidence_{episode_key_suffix}",
                icon=":material/table_view:",
            )
            _render_compact_dataframe(
                evidence_expander,
                _build_outlier_cycle_evidence_table(
                    episode_card,
                    t,
                ),
                width="stretch",
                hide_index=True,
            )


def _render_selected_station_evidence(
    station_df,
    selected_identity_df,
    is_sequential,
    tx_ab_repeat_interval_minutes,
    tx_ab_target_start_minute,
    tx_ab_reference_start_minute,
    *,
    t,
    analysis_id,
    run_id,
    scope_token,
    cache_key,
    analysis_context,
    language,
    thresholded_station_rows=None,
    analysis_start_t=None,
    analysis_end_t=None,
    target_only_label=None,
    reference_only_label=None,
    outlier_model=None,
    timing_collector=None,
):
    """Render pooled absolute Delta-SNR for selected Benchmark paths."""
    identity_meta = _prepare_identity_meta(selected_identity_df)
    if identity_meta.empty:
        return None
    if len(identity_meta) > 1 and outlier_model is None:
        raise ValueError(
            "Selected Station Evidence requires exactly one station identity "
            "when outlier reporting is disabled."
        )
    identity_labels = identity_meta["identity"].tolist()
    reference_snr_correction_notice = configured_snr_correction_notice(
        analysis_context,
        t,
        is_compare=True,
        is_sequential=is_sequential,
    )
    preferred_time_bin = st.session_state.get(
        _time_bin_persistent_state_key(True)
    )
    (
        adaptive_time_agg_options,
        adaptive_time_agg_default,
        retained_extra_cache_token,
    ) = _compare_temporal_time_bin_policy(
        analysis_start_t,
        analysis_end_t,
        preferred_time_bin,
    )
    cache_key = (
        *cache_key,
        "adaptive-time-bin-policy-v1",
        tuple(adaptive_time_agg_options),
        adaptive_time_agg_default,
        retained_extra_cache_token,
    )

    selected_bundle, selected_cache_hit = _inspector_cache_get(
        run_id,
        "selected",
        cache_key,
        timing_collector,
        item="selected evidence model",
    )
    if not selected_cache_hit:
        with _timed_span(
            timing_collector,
            "selected comparison units build",
        ):
            comparison_units = _build_compare_unit_rows(
                station_df,
                identity_meta,
                is_sequential,
                paired_identity_df=identity_meta,
                tx_ab_repeat_interval_minutes=tx_ab_repeat_interval_minutes,
                tx_ab_target_start_minute=tx_ab_target_start_minute,
                tx_ab_reference_start_minute=tx_ab_reference_start_minute,
            )
            comparison_units = _retain_thresholded_compare_outcomes(
                comparison_units,
                thresholded_station_rows,
            )
            evidence_df = _compare_joint_evidence_points(
                comparison_units,
            )

        if is_sequential:
            count_label = t["fig_scheduled_pair_count"]
            density_label = t["fig_relative_scheduled_pair_density"]
        else:
            count_label = t["fig_joint_spot_count"]
            density_label = t["fig_relative_joint_spot_density"]
        evidence_count = len(evidence_df)
        evidence_title = _selected_evidence_figure_title(
            identity_labels,
            evidence_count,
            analysis_id=analysis_id,
            is_sequential=is_sequential,
            translations=t,
            allow_multiple=(outlier_model is not None),
        )
        time_agg_options = tuple(adaptive_time_agg_options)
        time_agg_default = adaptive_time_agg_default
        folded_date_template = t[
            "fig_segment_dates_folded"
        ].replace(
            "{count}",
            "{utc_date_count}",
        )
        base_recipe = _selected_evidence_export_recipe(
            evidence_df,
            evidence_title,
            time_agg_default,
            is_sequential,
            analysis_start_t=analysis_start_t,
            analysis_end_t=analysis_end_t,
            reference_snr_correction_notice=(
                reference_snr_correction_notice
            ),
            count_label=count_label,
            chronological_title=t[
                "fig_selected_compare_chronological_title"
            ],
            chronological_x_label=t[
                "fig_segment_chronological_x"
            ],
            chronological_unavailable_text=t[
                "fig_compare_chronological_unavailable"
            ],
            metric_axis_label=t["tbl_col_delta_snr"],
            folded_title=t[
                "fig_selected_compare_folded_title"
            ],
            folded_date_annotation=folded_date_template,
            folded_x_label=t["fig_segment_utc_hour_x"],
            density_label=density_label,
            folded_unavailable_text=t[
                "fig_segment_folded_unavailable"
            ],
            median_focus_axis_label=t[
                "fig_compare_median_focus_axis"
            ],
            median_label=t["fig_median_label"],
            bin_median_label=t["fig_temporal_bin_median"],
            bin_iqr_label=t["fig_temporal_bin_iqr"],
            time_bin_options=time_agg_options,
        )
        selected_coverage_recipe = None
        if not comparison_units.empty and len(identity_meta) == 1:
            selected_identity = identity_meta.iloc[0]
            mode_suffix = (
                "tx"
                if analysis_id.startswith("TX")
                else "rx"
            )
            selected_coverage_title = t[
                f"fig_selected_compare_coverage_title_{mode_suffix}"
            ].format(
                station=str(selected_identity["peer_sign"]),
                locator=str(selected_identity["peer_grid"]),
            )
            selected_coverage_recipe = _compare_coverage_recipe(
                comparison_units,
                coverage_title=selected_coverage_title,
                selected_segment=identity_labels[0],
                analysis_start_t=analysis_start_t,
                analysis_end_t=analysis_end_t,
                time_bin_options=time_agg_options,
                time_bin_default=time_agg_default,
                figure_labels=_compare_coverage_figure_labels(
                    t,
                    analysis_id,
                    is_sequential=is_sequential,
                    target_only_label=target_only_label,
                    joint_label=t["txt_joint"],
                    reference_only_label=reference_only_label,
                ),
                population_mode=(
                    SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
                ),
            )
        selected_bundle = {
            "base_recipe": base_recipe,
            "coverage_recipe": selected_coverage_recipe,
            "time_agg_options": tuple(time_agg_options),
            "time_agg_default": time_agg_default,
            "title": evidence_title,
            "identity_labels": tuple(identity_labels),
            "evidence_count": int(evidence_count),
            "comparison_unit_count": int(len(comparison_units)),
            "selected_station_count": int(len(identity_meta)),
        }
        _inspector_cache_put(
            run_id,
            "selected",
            cache_key,
            selected_bundle,
        )
        del comparison_units, evidence_df

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
    persistent_time_bin_key = _time_bin_persistent_state_key(True)
    _initialize_time_bin_widget_state(
        agg_key,
        persistent_time_bin_key,
        time_agg_options,
        time_agg_default,
    )

    _render_prompted_segment_time_bin_control(
        t["lbl_selected_time_aggregation_bin_size"],
        time_agg_options,
        agg_key,
        on_change=_sync_time_bin_widget_state,
        on_change_args=(
            agg_key,
            persistent_time_bin_key,
            tuple(time_agg_options),
            time_agg_default,
        ),
    )
    time_agg = _sync_time_bin_widget_state(
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
        selected_marker_recipe = _delta_snr_outlier_marker_recipe(
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
        _render_cached_recipe(
            selected_recipe,
            run_id=run_id,
            cache_key=(
                cache_key
                + (time_agg, "dual-temporal")
                + selected_marker_cache_token
            ),
            subject="selected evidence",
            build_label="selected evidence figure build",
            render_figure=render_selected_evidence_export_figure,
            timing_collector=timing_collector,
        )

    selected_coverage_recipe = None
    if selected_bundle.get("coverage_recipe") is not None:
        selected_coverage_recipe = dict(
            selected_bundle["coverage_recipe"]
        )
        selected_coverage_recipe["time_bin"] = time_agg
        _render_cached_recipe(
            selected_coverage_recipe,
            run_id=run_id,
            cache_key=cache_key + (time_agg, "selected coverage"),
            subject="selected path evidence coverage",
            build_label="selected path evidence coverage figure build",
            render_figure=render_selected_compare_coverage_export_figure,
            timing_collector=timing_collector,
        )
    return {
        "export_recipe": selected_recipe,
        "coverage_export_recipe": selected_coverage_recipe,
        "time_bin": time_agg,
        "title": evidence_title,
        "comparison_unit_count": comparison_unit_count,
    }


def _render_segment_temporal_evidence(
    temporal_bundle,
    *,
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
        RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY
        if is_compare
        else RESULTS_SEGMENT_TIME_BIN_ABSOLUTE_STATE_KEY
    )
    widget_key = f"segment_evidence_time_agg_{analysis_id}_{run_id}_{scope_token}"
    selected_time_bin = _initialize_time_bin_widget_state(
        widget_key,
        persistent_state_key,
        time_bin_options,
        time_bin_default,
    )

    _render_prompted_segment_time_bin_control(
        t["lbl_time_aggregation_bin_size"],
        time_bin_options,
        widget_key,
        on_change=_sync_time_bin_widget_state,
        on_change_args=(
            widget_key,
            persistent_state_key,
            tuple(time_bin_options),
            time_bin_default,
        ),
    )

    selected_time_bin = _sync_time_bin_widget_state(
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
        outlier_marker_recipe = _delta_snr_outlier_marker_recipe(
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
        _render_cached_recipe(
            snr_export_recipe,
            run_id=run_id,
            cache_key=cache_key
            + ("segment temporal SNR deviation", selected_time_bin),
            subject="segment temporal SNR deviation",
            build_label="segment temporal SNR deviation figure build",
            render_figure=render_segment_temporal_snr_export_figure,
            timing_collector=timing_collector,
        )
    if temporal_recipe is not None:
        _render_cached_recipe(
            temporal_recipe,
            run_id=run_id,
            cache_key=cache_key
            + ("segment temporal evidence", selected_time_bin)
            + outlier_marker_cache_token,
            subject="segment temporal evidence",
            build_label="segment temporal evidence figure build",
            render_figure=render_segment_temporal_evidence_export_figure,
            timing_collector=timing_collector,
        )
    coverage_base_recipe = temporal_bundle.get("coverage_recipe")
    if is_compare and coverage_base_recipe:
        coverage_export_recipe = dict(coverage_base_recipe)
        coverage_export_recipe["time_bin"] = selected_time_bin
        _render_cached_recipe(
            coverage_export_recipe,
            run_id=run_id,
            cache_key=cache_key
            + ("segment temporal coverage", selected_time_bin),
            subject="segment temporal coverage",
            build_label="segment temporal coverage figure build",
            render_figure=render_compare_temporal_coverage_export_figure,
            timing_collector=timing_collector,
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






















def _render_opportunity_scope(
    *,
    analysis_id,
    title,
    df_seg,
    parquet_path,
    line1_str,
    t,
    selected_seg,
    selected_ranges,
    selected_directions,
    distance_scope_intervals,
    range_summary,
    direction_summary,
    scope_token,
    run_id,
    level_two_container,
    active_scope_summary,
    scope_summary_placeholder,
    analysis_start_t,
    analysis_end_t,
    show_export_button,
    analysis_context,
    presentation_context,
    timing_collector=None,
):
    """Render the opportunity-specific Performance inspector and export state."""
    opportunity_terms = presentation_context.absolute_terms(
        "TX" if analysis_id.startswith("TX") else "RX"
    )
    success_figure_labels = _success_figure_labels(t, analysis_id)
    retained_segment_time_bin = st.session_state.get(
        RESULTS_SEGMENT_TIME_BIN_ABSOLUTE_STATE_KEY
    )
    if analysis_start_t is not None and analysis_end_t is not None:
        (
            _segment_time_bin_options,
            _segment_time_bin_default,
            retained_segment_time_bin_cache_token,
        ) = _compare_temporal_time_bin_policy(
            analysis_start_t,
            analysis_end_t,
            retained_segment_time_bin,
        )
    else:
        retained_segment_time_bin_cache_token = retained_segment_time_bin

    segment_cache_key = (
        INSPECTOR_CACHE_VERSION,
        "opportunity",
        SUCCESS_DISTANCE_BINNING_VERSION,
        SUCCESS_SNR_BASELINE_VERSION,
        analysis_id,
        tuple(selected_ranges),
        tuple(selected_directions),
        tuple(
            (float(lower_km), float(upper_km))
            for lower_km, upper_km in distance_scope_intervals
        ),
        int(analysis_context.min_confirmed_opportunities_per_peer),
        str(analysis_start_t),
        str(analysis_end_t),
        presentation_context.language,
        presentation_context.theme,
        title,
        selected_seg,
        retained_segment_time_bin_cache_token,
    )
    segment_bundle, segment_cache_hit = _inspector_cache_get(
        run_id,
        "segment",
        segment_cache_key,
        timing_collector,
        item="opportunity segment model",
    )
    if not segment_cache_hit:
        identity_meta = df_seg[["peer_sign", "peer_grid"]].drop_duplicates()
        try:
            with _timed_span(timing_collector, "opportunity rows parquet read"):
                rows = read_parquet_artifact(
                    parquet_path,
                    columns=list(OPPORTUNITY_SEGMENT_VIEW_COLUMNS),
                    filters=[("peer_sign", "in", identity_meta["peer_sign"].astype(str).unique().tolist())],
                )
        except FileNotFoundError as exc:
            _log_artifact_read_failure(
                exc,
                parquet_path=parquet_path,
                analysis_id=analysis_id,
                run_id=run_id,
                stage="opportunity segment read",
            )
            st.warning(t["warn_analysis_cache_expired"])
            return
        except (KeyError, ValueError) as exc:
            _log_artifact_read_failure(
                exc,
                parquet_path=parquet_path,
                analysis_id=analysis_id,
                run_id=run_id,
                stage="opportunity segment read",
            )
            st.error(t["err_analysis_evidence_schema_invalid"])
            return
        with _timed_span(timing_collector, "opportunity segment prep"):
            rows["peer_sign"] = rows["peer_sign"].astype(str)
            rows["peer_grid"] = rows["peer_grid"].astype(str)
            rows = rows.merge(identity_meta, on=["peer_sign", "peer_grid"], how="inner")
            row_times = opportunity_utc_from_time_slot(rows["time_slot"]).dropna()
            if analysis_start_t is None:
                analysis_start_t = row_times.min() if not row_times.empty else pd.Timestamp.now(tz="UTC")
            if analysis_end_t is None:
                analysis_end_t = (
                    row_times.max() + pd.Timedelta(minutes=2)
                    if not row_times.empty
                    else _as_utc_timestamp(analysis_start_t) + pd.Timedelta(minutes=2)
                )
            del row_times

            opportunity_view_model = build_opportunity_inspector_view_model(
                df_seg,
                analysis_id=analysis_id,
                minimum_confirmed=analysis_context.min_confirmed_opportunities_per_peer,
                presentation_context=presentation_context,
            )

        with _timed_span(
            timing_collector,
            "opportunity exact-distance evidence prep",
        ):
            segment_recipe = _opportunity_segment_recipe(
                title,
                selected_seg,
                opportunity_view_model.confirmed_rows,
                analysis_start_t,
                analysis_end_t,
                opportunity_terms,
                minimum_trials=analysis_context.min_confirmed_opportunities_per_peer,
                figure_labels=success_figure_labels,
                distance_scope_intervals=distance_scope_intervals,
            )
        with _timed_span(
            timing_collector,
            "opportunity temporal evidence prep",
        ):
            temporal_base_recipe = _opportunity_temporal_recipe(
                _success_temporal_figure_title(
                    analysis_context.callsign,
                    analysis_id,
                    t,
                    figure_kind="evidence",
                ),
                selected_seg,
                opportunity_view_model.confirmed_rows,
                rows,
                analysis_start_t,
                analysis_end_t,
                opportunity_terms,
                figure_labels=success_figure_labels,
                snr_title=_success_temporal_figure_title(
                    analysis_context.callsign,
                    analysis_id,
                    t,
                    figure_kind="snr",
                ),
                population_mode=SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
                snr_representation=(
                    SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE
                ),
                retained_time_bin=retained_segment_time_bin,
            )
        temporal_bundle = {
            "base_recipe": temporal_base_recipe,
            "time_bin_options": tuple(
                temporal_base_recipe["time_bin_options"]
            ),
            "time_bin_default": temporal_base_recipe["time_bin_default"],
        }
        opportunity_display_model = {
            "summary_lines": list(opportunity_view_model.summary_lines),
            "confirmed_station_count": int(
                opportunity_view_model.confirmed_station_count
            ),
            "confirmed_opportunity_count": int(
                opportunity_view_model.confirmed_opportunity_count
            ),
            "full_station_table": opportunity_view_model.full_station_table,
            "export_column_renames": dict(
                opportunity_view_model.export_column_renames
            ),
            "station_column": opportunity_view_model.station_column,
            "locator_column": opportunity_view_model.locator_column,
            "distance_column": opportunity_view_model.distance_column,
            "azimuth_column": opportunity_view_model.azimuth_column,
            "hit_column": opportunity_view_model.hit_column,
            "export_station_column": (
                opportunity_view_model.export_station_column
            ),
            "export_locator_column": (
                opportunity_view_model.export_locator_column
            ),
        }
        segment_bundle = {
            "display_model": opportunity_display_model,
            "figure_recipe": segment_recipe,
            "temporal_bundle": temporal_bundle,
            "analysis_start_t": analysis_start_t,
            "analysis_end_t": analysis_end_t,
        }
        del identity_meta, opportunity_view_model, rows
        _inspector_cache_put(
            run_id,
            "segment",
            segment_cache_key,
            segment_bundle,
        )

    opportunity_display_model = segment_bundle["display_model"]
    segment_recipe = segment_bundle["figure_recipe"]
    temporal_bundle = segment_bundle["temporal_bundle"]
    analysis_start_t = segment_bundle["analysis_start_t"]
    analysis_end_t = segment_bundle["analysis_end_t"]

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

        _render_cached_recipe(
            segment_recipe,
            run_id=run_id,
            cache_key=segment_cache_key,
            subject="opportunity segment",
            build_label="opportunity segment figure build",
            render_figure=_render_opportunity_segment_figure,
            timing_collector=timing_collector,
        )
        segment_temporal_export = _render_segment_temporal_evidence(
            temporal_bundle,
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

    station_col = opportunity_display_model["station_column"]
    loc_col = opportunity_display_model["locator_column"]
    km_col = opportunity_display_model["distance_column"]
    az_col = opportunity_display_model["azimuth_column"]
    hit_col = opportunity_display_model["hit_column"]
    full_segment_disp_df = opportunity_display_model["full_station_table"]

    zero_hits_key = f"opp_show_zero_hits_{analysis_id}_{run_id}_{scope_token}"
    configured_station_identities = st.session_state.get(
        RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY
    )
    show_zero_hits = _initialize_boolean_widget_state(
        zero_hits_key,
        RESULTS_SHOW_ZERO_TARGET_STATE_KEY,
        _selection_requires_zero_hit_rows(
            full_segment_disp_df,
            station_col,
            loc_col,
            hit_col,
            configured_station_identities,
        ),
    )

    disp_df = full_segment_disp_df
    if not show_zero_hits:
        disp_df = full_segment_disp_df.loc[
            full_segment_disp_df[hit_col] > 0
        ].reset_index(drop=True)

    level_three_container = st.container(
        key=(
            f"results_evidence_level_3_"
            f"{analysis_id}_{run_id}_{scope_token}"
        )
    )
    station_type = remote_station_type(analysis_id)
    station_insights_title = t["lbl_insights"]
    level_three_container.markdown(
        evidence_level_header_html(
            3,
            t["lbl_results_level_stations"],
            station_insights_title,
            t["sub_results_station_insights_success"].format(
                station_type=station_type
            ),
            station_scope_text(
                range_summary,
                direction_summary,
                len(disp_df),
                analysis_id,
                t,
            ),
        ),
        unsafe_allow_html=True,
    )
    with level_three_container:
        render_result_guidance_popover(
            RESULT_GUIDANCE_STATION_INSIGHTS,
            station_insights_title,
            language=presentation_context.language,
            translations=t,
            key=(
                f"results_guidance_station_insights_"
                f"{analysis_id}_{run_id}_{scope_token}"
            ),
            analysis_id=analysis_id,
            is_compare=False,
            is_sequential=False,
            analysis_context=analysis_context,
        )

    col_toggle, col_filter = level_three_container.columns(
        SUCCESS_STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS,
        vertical_alignment="center",
    )
    with col_toggle:
        show_zero_hits = st.toggle(
            opportunity_terms["show_counter"],
            key=zero_hits_key,
            on_change=_sync_boolean_widget_state,
            args=(zero_hits_key, RESULTS_SHOW_ZERO_TARGET_STATE_KEY),
        )
        show_zero_hits = _sync_boolean_widget_state(
            zero_hits_key,
            RESULTS_SHOW_ZERO_TARGET_STATE_KEY,
        )

    disp_df = full_segment_disp_df
    if not show_zero_hits:
        disp_df = full_segment_disp_df.loc[
            full_segment_disp_df[hit_col] > 0
        ].reset_index(drop=True)

    with col_filter:
        with st.popover(
            t["lbl_filter"],
            icon=":material/filter_alt:",
            width="stretch",
        ):
            filter_cols = st.multiselect(
                t["lbl_select_columns"],
                disp_df.columns,
                label_visibility="collapsed",
                key=f"opp_filter_cols_{analysis_id}_{run_id}_{scope_token}",
            )
            for column in filter_cols:
                if pd.api.types.is_numeric_dtype(disp_df[column]):
                    numeric = pd.to_numeric(disp_df[column], errors="coerce").dropna()
                    if not numeric.empty and numeric.min() < numeric.max():
                        step = 1.0 if pd.api.types.is_integer_dtype(numeric) else 0.1
                        selected = st.slider(
                            column,
                            float(numeric.min()),
                            float(numeric.max()),
                            (float(numeric.min()), float(numeric.max())),
                            step=step,
                            key=f"opp_filter_{column}_{analysis_id}_{run_id}_{scope_token}",
                        )
                        disp_df = disp_df[
                            pd.to_numeric(disp_df[column], errors="coerce").between(selected[0], selected[1])
                        ]

    table_key = f"tbl_{analysis_id}_{run_id}_{scope_token}"
    selection_changed_key = f"{table_key}_selection_changed"
    dataframe_kwargs = {
        "width": "stretch",
        "hide_index": True,
        "selection_mode": "single-row",
        "on_select": partial(
            _mark_station_selection_changed,
            selection_changed_key,
        ),
        "key": table_key,
        "column_config": _snr_column_config(disp_df),
    }
    selection_default_rows, missing_station_identities = (
        _station_selection_default_rows(
            disp_df,
            station_col,
            loc_col,
            configured_station_identities,
        )
    )
    with level_three_container:
        _warn_missing_station_identities(missing_station_identities, t)
    if _supports_dataframe_selection_default():
        dataframe_kwargs["selection_default"] = {
            "selection": {"rows": selection_default_rows}
        }
    with _timed_span(timing_collector, "opportunity station table render"):
        table_event = _render_compact_dataframe(
            level_three_container,
            disp_df,
            **dataframe_kwargs,
        )

    selected_station_labels = []
    selected_evidence_recipe = None
    selected_station_snr_evidence_recipe = None
    selected_station_temporal_evidence_recipe = None
    selected_station_label_text = None
    selected_station_context_text = None
    selected_evidence_figure_descriptions = {}
    selected_time_bin = None
    drilldown_selected_df = pd.DataFrame()
    drilldown_zoom_metadata = None
    drilldown_zoom_performance_snr_recipe = None
    drilldown_zoom_performance_evidence_recipe = None
    selected_rows = [
        row
        for row in (table_event.selection.rows or [])
        if 0 <= row < len(disp_df)
    ][:1]
    _sync_selected_station_state_if_changed(
        selection_changed_key,
        RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY,
        disp_df,
        selected_rows,
        station_col,
        loc_col,
    )

    if selected_rows:
        selected_meta_df = disp_df.iloc[selected_rows][[station_col, loc_col, km_col, az_col]].copy()
        selected_meta_df = selected_meta_df.drop_duplicates(subset=[station_col, loc_col])
        selected_identity = selected_meta_df[[station_col, loc_col]].copy()
        selected_identity.columns = ["peer_sign", "peer_grid"]
        selected_station_labels = (
            selected_identity["peer_sign"].astype(str) +
            " (" + selected_identity["peer_grid"].astype(str) + ")"
        ).tolist()
        with _timed_span(timing_collector, "selected station rows load"):
            selected_station_rows = _load_station_rows_for_drilldown(
                parquet_path,
                selected_meta_df,
                station_col,
                loc_col,
                columns=OPPORTUNITY_DRILLDOWN_VIEW_COLUMNS,
            )

        selection_label = selected_station_label(
            selected_station_labels,
            analysis_id=analysis_id,
            translations=t,
        )
        selected_station = str(
            selected_identity.iloc[0]["peer_sign"]
        ).strip().upper()
        selected_locator = str(
            selected_identity.iloc[0]["peer_grid"]
        ).strip().upper()
        selected_peer_rows = df_seg.loc[
            (df_seg["peer_sign"].astype(str).str.upper() == selected_station)
            & (
                df_seg["peer_grid"].astype(str).str.upper()
                == selected_locator
            )
        ].copy()
        selected_cache_key = (
            INSPECTOR_CACHE_VERSION,
            "opportunity",
            "selected-success-temporal-v1",
            SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
            SUCCESS_SNR_REPRESENTATION_ACTUAL,
            analysis_id,
            scope_token,
            selected_station,
            selected_locator,
            str(analysis_start_t),
            str(analysis_end_t),
            presentation_context.language,
            presentation_context.theme,
            _compare_temporal_time_bin_policy(
                analysis_start_t,
                analysis_end_t,
                st.session_state.get(RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY),
            )[2],
        )
        selected_base_recipe, selected_cache_hit = _inspector_cache_get(
            run_id,
            "selected",
            selected_cache_key,
            timing_collector,
            item="opportunity selected temporal model",
        )
        if not selected_cache_hit:
            with _timed_span(
                timing_collector,
                "opportunity selected temporal evidence prep",
            ):
                selected_base_recipe = _opportunity_temporal_recipe(
                    _selected_success_temporal_figure_title(
                        selected_station,
                        selected_locator,
                        analysis_id,
                        t,
                        figure_kind="evidence",
                    ),
                    selected_seg,
                    selected_peer_rows,
                    selected_station_rows,
                    analysis_start_t,
                    analysis_end_t,
                    opportunity_terms,
                    figure_labels=success_figure_labels,
                    snr_title=_selected_success_temporal_figure_title(
                        selected_station,
                        selected_locator,
                        analysis_id,
                        t,
                        figure_kind="snr",
                    ),
                    population_mode=(
                        SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
                    ),
                    snr_representation=SUCCESS_SNR_REPRESENTATION_ACTUAL,
                    retained_time_bin=st.session_state.get(
                        RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY
                    ),
                )
            _inspector_cache_put(
                run_id,
                "selected",
                selected_cache_key,
                selected_base_recipe,
            )

        selected_station_label_text = selection_label
        selected_station_context_text = _selected_success_context_line(
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
                selected_station_context_text,
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
        persistent_time_bin_key = RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY
        _initialize_time_bin_widget_state(
            selected_time_key,
            persistent_time_bin_key,
            time_options,
            time_default,
        )
        with level_four_container:
            _render_prompted_segment_time_bin_control(
                t["lbl_selected_time_aggregation_bin_size"],
                time_options,
                selected_time_key,
                on_change=_sync_time_bin_widget_state,
                on_change_args=(
                    selected_time_key,
                    persistent_time_bin_key,
                    tuple(time_options),
                    time_default,
                ),
            )
        selected_time_bin = _sync_time_bin_widget_state(
            selected_time_key,
            persistent_time_bin_key,
            time_options,
            time_default,
        )
        selected_station_temporal_evidence_recipe = dict(
            selected_base_recipe
        )
        selected_station_temporal_evidence_recipe[
            "time_bin"
        ] = selected_time_bin
        selected_station_snr_evidence_recipe = dict(
            selected_station_temporal_evidence_recipe
        )
        selected_evidence_figure_descriptions = {
            "figure_selected_station_snr_evidence.png": (
                selected_base_recipe["snr_title"]
            ),
            "figure_selected_station_temporal_evidence.png": (
                selected_base_recipe["evidence_title"]
            ),
        }
        with level_four_container:
            _render_cached_recipe(
                selected_station_snr_evidence_recipe,
                run_id=run_id,
                cache_key=(
                    *selected_cache_key,
                    selected_time_bin,
                    "snr-evidence",
                ),
                subject="opportunity selected SNR evidence",
                build_label=(
                    "opportunity selected SNR evidence figure build"
                ),
                render_figure=render_segment_temporal_snr_export_figure,
                timing_collector=timing_collector,
            )
            _render_cached_recipe(
                selected_station_temporal_evidence_recipe,
                run_id=run_id,
                cache_key=(
                    *selected_cache_key,
                    selected_time_bin,
                    "temporal-evidence",
                ),
                subject="opportunity selected temporal evidence",
                build_label=(
                    "opportunity selected temporal evidence figure build"
                ),
                render_figure=render_segment_temporal_evidence_export_figure,
                timing_collector=timing_collector,
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
                _render_drilldown_header_and_controls(
                    selected_station_labels,
                    analysis_id,
                    run_id,
                    scope_token,
                    t,
                    False,
                    False,
                    analysis_context,
                    presentation_context.language,
                    analysis_start_utc=analysis_start_t,
                    analysis_end_utc=analysis_end_t,
                    selected_identity=(selected_station, selected_locator),
                )
            )
            focused_station_rows = filter_station_rows_to_focus_window(
                selected_station_rows,
                focus_window,
                is_sequential=False,
            )
            if focus_window is not None:
                (
                    drilldown_zoom_performance_snr_recipe,
                    drilldown_zoom_performance_evidence_recipe,
                ) = _build_performance_drilldown_zoom_recipes(
                    selected_base_recipe,
                    selected_peer_rows,
                    focused_station_rows,
                    selected_station_labels[0],
                    focus_window,
                    focus_time_bin,
                    t,
                )
                drilldown_zoom_metadata = _drilldown_zoom_export_metadata(
                    focus_window,
                    selected_identity=(selected_station, selected_locator),
                    metric_recipe=drilldown_zoom_performance_snr_recipe,
                )
                focus_cache_key = (
                    *selected_cache_key,
                    "drilldown-focus",
                    int(focus_window.start_utc.value),
                    int(focus_window.end_utc.value),
                    focus_time_bin,
                    DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
                )
                _render_cached_recipe(
                    drilldown_zoom_performance_snr_recipe,
                    run_id=run_id,
                    cache_key=(*focus_cache_key, "snr"),
                    subject="opportunity Drill-Down zoom SNR evidence",
                    build_label="opportunity Drill-Down zoom SNR figure build",
                    render_figure=(
                        render_drilldown_zoom_performance_snr_figure
                    ),
                    timing_collector=timing_collector,
                )
                _render_cached_recipe(
                    drilldown_zoom_performance_evidence_recipe,
                    run_id=run_id,
                    cache_key=(*focus_cache_key, "outcomes"),
                    subject="opportunity Drill-Down zoom temporal evidence",
                    build_label=(
                        "opportunity Drill-Down zoom temporal figure build"
                    ),
                    render_figure=(
                        render_drilldown_zoom_performance_evidence_figure
                    ),
                    timing_collector=timing_collector,
                )
            with _timed_span(timing_collector, "drilldown table build"):
                export_station_col = opportunity_display_model[
                    "export_station_column"
                ]
                selected_meta_export_df = selected_meta_df.rename(
                    columns={station_col: export_station_col}
                )
                selected_station_rows_export = focused_station_rows.rename(
                    columns={station_col: export_station_col}
                )
                drill_df, info_msg = _build_drilldown_table(
                    parquet_path,
                    selected_meta_export_df,
                    export_station_col,
                    loc_col,
                    km_col,
                    az_col,
                    analysis_id,
                    False,
                    False,
                    False,
                    analysis_context.callsign.upper(),
                    "",
                    t,
                    station_rows_df=selected_station_rows_export,
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
            elif not drill_df.empty:
                drilldown_selected_df = _render_drilldown_dataframe(
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
    else:
        level_three_container.markdown(
            transition_prompt_html(
                t["txt_results_transition_stations_success"]
            ),
            unsafe_allow_html=True,
        )

    export_station_col = opportunity_display_model["export_station_column"]
    export_loc_col = opportunity_display_model["export_locator_column"]
    export_column_renames = opportunity_display_model[
        "export_column_renames"
    ]
    full_meta_df = full_segment_disp_df[
        [station_col, loc_col, km_col, az_col]
    ].copy()
    full_meta_df.rename(
        columns={
            station_col: export_station_col,
            loc_col: export_loc_col,
        },
        inplace=True,
    )
    filtered_export_station_table = _opportunity_export_station_rows(
        disp_df,
        export_column_renames=export_column_renames,
    )
    all_drilldown_context = {
        "station_meta_df": full_meta_df,
        "station_col": export_station_col,
        "loc_col": export_loc_col,
        "km_col": km_col,
            "az_col": az_col,
            "analysis_id": analysis_id,
            "is_sequential": False,
        "show_non_joint": False,
        "is_local_median": False,
        "col_u_name": analysis_context.callsign.upper(),
        "ref_header": "",
        "tx_ab_repeat_interval_minutes": (
            analysis_context.tx_ab_repeat_interval_minutes
        ),
        "tx_ab_target_start_minute": analysis_context.tx_ab_target_start_minute,
        "tx_ab_reference_start_minute": (
            analysis_context.tx_ab_reference_start_minute
        ),
        "target_callsign": analysis_context.callsign,
        "lang": st.session_state.get("lang", "en"),
    }
    register_inspector_export(
        translations=t,
        analysis_id=analysis_id,
        selected_segment=selected_seg,
        selected_distance=range_summary,
        selected_direction=direction_summary,
        selected_ranges=list(selected_ranges),
        selected_directions=list(selected_directions),
        show_non_joint=False,
        show_zero_target=show_zero_hits,
        evidence_time_bin=selected_time_bin,
        segment_evidence_time_bin=(
            segment_temporal_export or {}
        ).get("time_bin"),
        selected_stations=selected_station_labels,
        segment_figure_recipe=segment_recipe,
        segment_temporal_evidence_figure_recipe=(
            segment_temporal_export or {}
        ).get("export_recipe"),
        segment_temporal_snr_deviation_figure_recipe=(
            segment_temporal_export or {}
        ).get("snr_export_recipe"),
        selected_evidence_figure_recipe=selected_evidence_recipe,
        selected_station_snr_evidence_figure_recipe=(
            selected_station_snr_evidence_recipe
        ),
        selected_station_temporal_evidence_figure_recipe=(
            selected_station_temporal_evidence_recipe
        ),
        station_insights_df=filtered_export_station_table,
        drilldown_selected_df=drilldown_selected_df,
        all_drilldown_context=all_drilldown_context,
        selected_station_label=selected_station_label_text,
        selected_station_context_label=selected_station_context_text,
        selected_station_role=remote_station_type(analysis_id),
        selected_evidence_figure_descriptions=(
            selected_evidence_figure_descriptions
        ),
        drilldown_zoom_metadata=drilldown_zoom_metadata,
        drilldown_zoom_performance_snr_figure_recipe=(
            drilldown_zoom_performance_snr_recipe
        ),
        drilldown_zoom_performance_temporal_figure_recipe=(
            drilldown_zoom_performance_evidence_recipe
        ),
    )
    st.markdown(
        f"<div style='font-size:11px; color:#ccc; margin-top:0.75rem; margin-bottom:1rem; font-family:monospace;'>{line1_str}</div>",
        unsafe_allow_html=True,
    )
    if show_export_button:
        render_download_all_results(t)

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
    with _timed_span(timing_collector, span_label):
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
    """
    Renders the interactive Segment Inspector directly below the map.
    Allows drill-down into specific Azimuth/Distance chunks to show histograms and tabular data.
    Runs as an independent Streamlit fragment to prevent full-page reruns on interaction.
    """
    is_opportunity = _validate_inspector_analysis_mode(
        analysis_kind=analysis_kind,
        is_compare=is_compare,
    )
    run_id = st.session_state.get("run_id", 0)
    reference_snr_correction_notice = configured_snr_correction_notice(
        analysis_context,
        t,
        is_compare=is_compare,
        is_sequential=is_sequential,
    )
    if not ARTIFACT_STORE.touch(parquet_path):
        log_performance_event(
            "session_artifact_read",
            outcome="missing",
            stage="inspector heartbeat",
            analysis_id=analysis_id,
            run_id=run_id,
            artifact=Path(parquet_path).name,
            exists=False,
            error_type="FileNotFoundError",
        )
    
    # Inspect station rows because they also contain non-joint evidence such as
    # target-only, reference-only, or async-both rows.
    options_cache_key = (
        INSPECTOR_CACHE_VERSION,
        analysis_id,
        float(max_peer_distance_km),
    )
    options_view_model, options_cache_hit = _inspector_cache_get(
        run_id,
        "options",
        options_cache_key,
        timing_collector,
        item="inspector options",
    )
    if not options_cache_hit:
        options_view_model = build_inspector_options(
            enriched_df,
            max_peer_distance_km=max_peer_distance_km,
        )
        _inspector_cache_put(
            run_id,
            "options",
            options_cache_key,
            options_view_model,
        )
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
        _segment_scope_persistent_state_keys(is_compare)
    )

    # Render stable explicit-All multiselects. The callback keeps All mutually
    # exclusive with specific values and restores All when the field is cleared.
    col_insp1, col_insp2 = level_two_container.columns(2)
    with col_insp1:
        dist_key = f"dist_multi_{analysis_id}_{run_id}"
        dist_previous_key = f"{dist_key}_previous"
        dist_options = [opt_full] + valid_distances
        _initialize_explicit_all_multiselect(
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
            on_change=_update_explicit_all_multiselect,
            args=(
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
        _initialize_explicit_all_multiselect(
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
            on_change=_update_explicit_all_multiselect,
            args=(
                dir_key,
                dir_previous_key,
                opt_all_dir,
                valid_dirs,
                direction_persistent_key,
            ),
        )

    selected_ranges = _canonical_specific_selection(
        selected_distance_values,
        opt_full,
        valid_distances,
    )
    selected_directions = _canonical_specific_selection(
        selected_direction_values,
        opt_all_dir,
        valid_dirs,
    )
    range_summary = _selection_summary(
        selected_ranges,
        opt_full,
        "range",
        t,
    )
    direction_summary = _selection_summary(
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
    success_distance_scope_intervals = (
        _success_distance_scope_intervals(
            enriched_df,
            selected_ranges,
            max_peer_distance_km=max_peer_distance_km,
        )
        if is_opportunity
        else ()
    )

    # If inspectable options exist, process the selected Cartesian scope.
    if valid_distances and valid_dirs:
        with _timed_span(timing_collector, "segment scope filter"):
            df_seg = filter_inspector_scope(
                enriched_df,
                max_peer_distance_km=max_peer_distance_km,
                selected_ranges=selected_ranges,
                selected_directions=selected_directions,
            )

        is_outlier_reporting_requested = (
            not is_opportunity
            and st.session_state.get(
                RESULTS_REPORT_DELTA_SNR_OUTLIER_CANDIDATES_STATE_KEY,
                False,
            )
            is True
        )
        outlier_detection_policy = (
            _enabled_delta_snr_outlier_detection_policy(st.session_state)
            if is_outlier_reporting_requested
            else None
        )
        is_outlier_reporting_enabled = (
            is_outlier_reporting_requested
            and outlier_detection_policy is not None
        )
        if (
            is_outlier_reporting_requested
            and not is_outlier_reporting_enabled
        ):
            st.warning(
                t["msg_outlier_report_invalid_detector_settings"],
                icon=":material/warning:",
            )

        if df_seg.empty:
            st.info(
                t["msg_results_no_stations_in_scope"],
                icon=":material/info:",
            )
            if is_outlier_reporting_enabled:
                outlier_model = prepare_delta_snr_outlier_model(
                    True,
                    pd.DataFrame(),
                    analysis_start_utc=analysis_start_t,
                    analysis_end_utc=analysis_end_t,
                    paired_unit_cadence_minutes=(
                        analysis_context.tx_ab_repeat_interval_minutes
                        if is_sequential
                        else 2.0
                    ),
                    detection_policy=outlier_detection_policy,
                )
                outlier_report_view_model = (
                    build_delta_snr_outlier_report_view_model(
                        outlier_model,
                        pd.DataFrame(),
                    )
                )
                delta_snr_outlier_export_tables = (
                    build_delta_snr_outlier_export_tables(
                        outlier_model,
                        outlier_report_view_model,
                        is_sequential=is_sequential,
                    )
                )
                delta_snr_outlier_export_metadata = (
                    build_delta_snr_outlier_export_metadata(
                        outlier_model,
                        delta_snr_outlier_export_tables,
                    )
                )
                _render_delta_snr_outlier_report(
                    outlier_model,
                    outlier_report_view_model,
                    t=t,
                    language=presentation_context.language,
                    analysis_id=analysis_id,
                    run_id=run_id,
                    scope_token=scope_token,
                    is_sequential=is_sequential,
                    analysis_context=analysis_context,
                )
            register_inspector_export(
                translations=t,
                analysis_id=analysis_id,
                selected_segment=selected_seg,
                selected_distance=range_summary,
                selected_direction=direction_summary,
                selected_ranges=list(selected_ranges) if selected_ranges else [opt_full],
                selected_directions=list(selected_directions) if selected_directions else [opt_all_dir],
                show_non_joint=False,
                evidence_time_bin=None,
                selected_stations=[],
                station_insights_df=pd.DataFrame(),
                drilldown_selected_df=pd.DataFrame(),
                allow_multiple_selected_stations=(
                    is_outlier_reporting_enabled
                ),
                report_delta_snr_outlier_candidates=(
                    is_outlier_reporting_enabled
                ),
                delta_snr_outlier_detector_version=(
                    DELTA_SNR_OUTLIER_DETECTOR_VERSION
                    if is_outlier_reporting_enabled
                    else None
                ),
                delta_snr_outlier_detection_policy=(
                    outlier_detection_policy
                    if is_outlier_reporting_enabled
                    else None
                ),
                delta_snr_outlier_export_tables=(
                    delta_snr_outlier_export_tables
                    if is_outlier_reporting_enabled
                    else None
                ),
                delta_snr_outlier_export_metadata=(
                    delta_snr_outlier_export_metadata
                    if is_outlier_reporting_enabled
                    else None
                ),
            )
            if show_export_button:
                render_download_all_results(t)
            return

        if is_opportunity:
            _render_opportunity_scope(
                analysis_id=analysis_id,
                title=title,
                df_seg=df_seg,
                parquet_path=parquet_path,
                line1_str=line1_str,
                t=t,
                selected_seg=selected_seg,
                selected_ranges=selected_ranges if selected_ranges else (opt_full,),
                selected_directions=selected_directions if selected_directions else (opt_all_dir,),
                distance_scope_intervals=success_distance_scope_intervals,
                range_summary=range_summary,
                direction_summary=direction_summary,
                scope_token=scope_token,
                run_id=run_id,
                level_two_container=level_two_container,
                active_scope_summary=active_scope_summary,
                scope_summary_placeholder=scope_summary_placeholder,
                analysis_start_t=analysis_start_t,
                analysis_end_t=analysis_end_t,
                show_export_button=show_export_button,
                analysis_context=analysis_context,
                presentation_context=presentation_context,
                timing_collector=timing_collector,
            )
            return
            
        has_joint_rows, has_non_joint_rows = compare_scope_availability(df_seg)
        toggle_key = f"tgl_{analysis_id}_{run_id}_{scope_token}"
        default_state = has_non_joint_rows and not has_joint_rows
        show_non_joint = _initialize_boolean_widget_state(
            toggle_key,
            RESULTS_SHOW_NON_JOINT_STATE_KEY,
            default_state,
        )
        preferred_segment_time_bin = st.session_state.get(
            RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY
        )
        (
            temporal_time_options,
            temporal_time_default,
            retained_segment_time_bin_cache_token,
        ) = _compare_temporal_time_bin_policy(
            analysis_start_t,
            analysis_end_t,
            preferred_segment_time_bin,
        )
        outlier_cache_key_suffix = (
            _delta_snr_outlier_segment_cache_suffix(
                is_outlier_reporting_enabled,
                outlier_detection_policy,
            )
        )

        segment_cache_key = (
            INSPECTOR_CACHE_VERSION,
            "comparison",
            analysis_id,
            tuple(selected_ranges),
            tuple(selected_directions),
            bool(is_sequential),
            int(analysis_context.tx_ab_repeat_interval_minutes),
            int(analysis_context.tx_ab_target_start_minute),
            int(analysis_context.tx_ab_reference_start_minute),
            str(analysis_start_t),
            str(analysis_end_t),
            retained_segment_time_bin_cache_token,
            presentation_context.language,
            presentation_context.theme,
            title,
            selected_seg,
        ) + outlier_cache_key_suffix
        segment_bundle, segment_cache_hit = _inspector_cache_get(
            run_id,
            "segment",
            segment_cache_key,
            timing_collector,
            item="segment insight model",
        )
        if not segment_cache_hit:
            compare_view_model = build_compare_inspector_view_model(
                df_seg,
                analysis_id=analysis_id,
                is_sequential=is_sequential,
                analysis_context=analysis_context,
                presentation_context=presentation_context,
            )
            vals = df_seg["stat_val"].dropna()
            col_u_name = compare_view_model.target_name
            evidence_meta_df = (
                compare_view_model.build_evidence_identities()
            )
            has_plot_data = compare_view_model.has_plot_data
            segment_figure_recipe = None
            segment_temporal_bundle = None
            segment_summary = []
            segment_station_count = 0
            segment_evidence_count = 0
            segment_station_total_count = None
            segment_station_joint_count = None
            segment_spot_total_count = None
            segment_spot_joint_count = None
            joint_lbl = t["txt_joint"]
            outlier_model = None
            outlier_report_view_model = None

            if has_plot_data:
                with _timed_span(
                    timing_collector,
                    "segment comparison units build",
                ):
                    segment_comparison_units = _build_segment_compare_units(
                        df_seg,
                        evidence_meta_df,
                        parquet_path,
                        is_sequential,
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
                    segment_evidence_df = _compare_joint_evidence_points(
                        segment_comparison_units,
                        require_paired_eligible=True,
                    )
                    if is_outlier_reporting_enabled:
                        with _timed_span(
                            timing_collector,
                            "Delta-SNR outlier candidate detection",
                        ):
                            outlier_model = prepare_delta_snr_outlier_model(
                                True,
                                segment_comparison_units,
                                analysis_start_utc=analysis_start_t,
                                analysis_end_utc=analysis_end_t,
                                station_directions=(
                                    _outlier_station_direction_lookup(df_seg)
                                ),
                                paired_unit_cadence_minutes=(
                                    analysis_context.tx_ab_repeat_interval_minutes
                                    if is_sequential
                                    else 2.0
                                ),
                                detection_policy=outlier_detection_policy,
                            )
                            outlier_report_view_model = (
                                build_delta_snr_outlier_report_view_model(
                                    outlier_model,
                                    segment_comparison_units,
                                )
                            )
                segment_raw_values = (
                    segment_evidence_df["metric"]
                    if not segment_evidence_df.empty
                    else pd.Series(dtype=float)
                )
                segment_station_count = len(vals)
                segment_evidence_count = len(segment_raw_values)
                outcome_counts = compare_footer_counts(
                    df_seg,
                    max_dist_km=float("inf"),
                )
                joint_lbl = (
                    t["tbl_col_joint_pairs"]
                    if is_sequential
                    else t["txt_joint"]
                )
                async_lbl = t["leg_both_async"]
                segment_panel_station_counts = [
                    outcome_counts["stat_only_u"],
                    outcome_counts["stat_joint"],
                    outcome_counts["stat_both_async"],
                    outcome_counts["stat_only_r"],
                ]
                segment_panel_spot_counts = [
                    outcome_counts["spot_only_u"],
                    outcome_counts["spot_joint"],
                    outcome_counts["spot_both_async"],
                    outcome_counts["spot_only_r"],
                ]
                segment_panel_labels = [
                    compare_view_model.target_only_label,
                    joint_lbl,
                    async_lbl,
                    compare_view_model.reference_only_label,
                ]
                segment_panel_series_labels = [
                    t["lbl_results_stations"],
                    (
                        t["lbl_results_scheduled_pairs"]
                        if is_sequential
                        else t["lbl_results_spots"]
                    ),
                ]
                segment_station_total_count = sum(segment_panel_station_counts)
                segment_station_joint_count = outcome_counts["stat_joint"]
                segment_spot_total_count = sum(segment_panel_spot_counts)
                segment_spot_joint_count = outcome_counts["spot_joint"]

                segment_figure_recipe = _segment_figure_export_recipe(
                    title=title,
                    selected_segment=selected_seg,
                    is_sequential=is_sequential,
                    reference_snr_correction_notice=(
                        reference_snr_correction_notice
                    ),
                    station_values=vals,
                    spot_values=segment_raw_values,
                    panel_labels=segment_panel_labels,
                    panel_y_label=t["fig_share_percent_axis"],
                    decode_outcomes_title=t["fig_decode_outcomes"],
                    station_medians_title=t[
                        "fig_station_medians_delta"
                    ],
                    metric_axis_label=t["tbl_col_delta_snr"],
                    median_label=t["fig_median_label"],
                    mean_label=t["fig_mean_label"],
                    no_data_label=t["fig_no_data"],
                    panel_station_counts=segment_panel_station_counts,
                    panel_spot_counts=segment_panel_spot_counts,
                    panel_series_labels=segment_panel_series_labels,
                    paired_evidence_title=(
                        t["fig_scheduled_pair_delta"]
                        if is_sequential
                        else t["fig_joint_spot_delta"]
                    ),
                )
                station_summary = _compare_metric_distribution_summary(
                    vals,
                    t["fmt_results_station_delta_summary"],
                    total_count=segment_station_total_count,
                    joint_count=segment_station_joint_count,
                    joint_label=joint_lbl,
                )
                observation_summary_key = (
                    "fmt_results_scheduled_pair_delta_summary"
                    if is_sequential
                    else "fmt_results_joint_spot_delta_summary"
                )
                spot_summary = _compare_metric_distribution_summary(
                    segment_raw_values,
                    t[observation_summary_key],
                    total_count=segment_spot_total_count,
                    joint_count=segment_spot_joint_count,
                    joint_label=joint_lbl,
                )
                segment_summary = _segment_summary_lines(
                    station_summary=station_summary,
                    spot_summary=spot_summary,
                )
                segment_temporal_rows = segment_evidence_df[
                    ["plot_time", "metric"]
                ].copy()
                del segment_evidence_df, segment_raw_values
                if not segment_comparison_units.empty:
                    chronological_title_label = t[
                        "fig_segment_chronological_delta"
                    ]
                    chronological_title_template = t[
                        "fmt_temporal_title_with_bins"
                    ].format(
                        title=chronological_title_label,
                        time_bin="{time_bin}",
                    )
                    folded_date_template = t[
                        "fig_segment_dates_folded"
                    ].replace("{count}", "{utc_date_count}")
                    temporal_figure_title = _segment_temporal_figure_title(
                        title,
                        analysis_id,
                        selected_seg,
                        t,
                    )
                    compare_figure_labels = (
                        _compare_coverage_figure_labels(
                            t,
                            analysis_id,
                            is_sequential=is_sequential,
                            target_only_label=t[
                                "leg_only_me"
                            ].format(
                                callsign=t["txt_target"]
                            ),
                            joint_label=t["txt_joint"],
                            reference_only_label=t[
                                "leg_only_ref"
                            ].format(
                                ref_callsign=t["txt_reference"]
                            ),
                        )
                    )
                    compare_coverage_recipe = _compare_coverage_recipe(
                        segment_comparison_units,
                        coverage_title=_compare_temporal_coverage_title(
                            t,
                            analysis_id,
                            analysis_context.callsign,
                        ),
                        selected_segment=selected_seg,
                        analysis_start_t=analysis_start_t,
                        analysis_end_t=analysis_end_t,
                        time_bin_options=temporal_time_options,
                        time_bin_default=temporal_time_default,
                        figure_labels=compare_figure_labels,
                    )
                    del segment_comparison_units
                    if is_sequential:
                        temporal_count_label = t[
                            "fig_scheduled_pair_count"
                        ]
                        temporal_density_label = t[
                            "fig_relative_scheduled_pair_density"
                        ]
                    else:
                        temporal_count_label = t[
                            "fig_joint_spot_count"
                        ]
                        temporal_density_label = t[
                            "fig_relative_joint_spot_density"
                        ]
                    with _timed_span(
                        timing_collector,
                        "segment temporal profiles build",
                    ):
                        temporal_base_recipe = (
                            _segment_temporal_evidence_export_recipe(
                                segment_temporal_rows,
                                temporal_figure_title,
                                temporal_time_default,
                                temporal_count_label,
                                analysis_start_t=analysis_start_t,
                                analysis_end_t=analysis_end_t,
                                reference_snr_correction_notice=(
                                    reference_snr_correction_notice
                                ),
                                chronological_title=(
                                    chronological_title_template
                                ),
                                chronological_x_label=t[
                                    "fig_segment_chronological_x"
                                ],
                                chronological_unavailable_text=t[
                                    "fig_compare_chronological_unavailable"
                                ],
                                metric_axis_label=t["tbl_col_delta_snr"],
                                folded_title=(
                                    _folded_utc_hour_panel_title(t)
                                ),
                                folded_date_annotation=folded_date_template,
                                folded_x_label=t[
                                    "fig_segment_utc_hour_x"
                                ],
                                density_label=temporal_density_label,
                                folded_unavailable_text=t[
                                    "fig_segment_folded_unavailable"
                                ],
                                median_focus_axis_label=t[
                                    "fig_compare_median_focus_axis"
                                ],
                                median_label=t["fig_median_label"],
                                bin_median_label=t[
                                    "fig_temporal_bin_median"
                                ],
                                bin_iqr_label=t[
                                    "fig_temporal_bin_iqr"
                                ],
                                time_bin_options=temporal_time_options,
                            )
                        )
                    segment_temporal_bundle = {
                        "base_recipe": temporal_base_recipe,
                        "coverage_recipe": compare_coverage_recipe,
                        "time_bin_options": tuple(temporal_time_options),
                        "time_bin_default": temporal_time_default,
                        "chronological_title_template": chronological_title_template,
                    }
                else:
                    del segment_comparison_units
                del segment_temporal_rows

            if is_outlier_reporting_enabled and outlier_model is None:
                outlier_model = prepare_delta_snr_outlier_model(
                    True,
                    pd.DataFrame(),
                    analysis_start_utc=analysis_start_t,
                    analysis_end_utc=analysis_end_t,
                    paired_unit_cadence_minutes=(
                        analysis_context.tx_ab_repeat_interval_minutes
                        if is_sequential
                        else 2.0
                    ),
                    detection_policy=outlier_detection_policy,
                )
                outlier_report_view_model = (
                    build_delta_snr_outlier_report_view_model(
                        outlier_model,
                        pd.DataFrame(),
                    )
                )

            del vals, evidence_meta_df
            segment_bundle = {
                "view_model": compare_view_model,
                "figure_recipe": segment_figure_recipe,
                "temporal_bundle": segment_temporal_bundle,
                "summary": segment_summary,
                "evidence_station_count": int(segment_station_count),
                "evidence_count": int(segment_evidence_count),
            }
            if is_outlier_reporting_enabled:
                segment_bundle["outlier_model"] = outlier_model
                segment_bundle["outlier_report_view_model"] = (
                    outlier_report_view_model
                )
            _inspector_cache_put(
                run_id,
                "segment",
                segment_cache_key,
                segment_bundle,
            )

        compare_view_model = segment_bundle["view_model"]
        segment_figure_recipe = segment_bundle["figure_recipe"]
        segment_temporal_bundle = segment_bundle.get("temporal_bundle")
        segment_summary = segment_bundle["summary"]
        segment_station_count = int(segment_bundle["evidence_station_count"])
        segment_evidence_count = int(segment_bundle["evidence_count"])
        outlier_model = segment_bundle.get("outlier_model")
        outlier_report_view_model = segment_bundle.get(
            "outlier_report_view_model"
        )
        ref_header = compare_view_model.reference_header
        col_u_name = compare_view_model.target_name
        is_local_median = compare_view_model.is_local_median
        seg_line2 = compare_view_model.scope_summary
        station_col = compare_view_model.station_column
        col_joint_name = compare_view_model.joint_column

        disp_df = compare_view_model.station_table
        if not show_non_joint and col_joint_name in disp_df.columns:
            disp_df = disp_df[disp_df[col_joint_name] > 0].reset_index(drop=True)
        sorted_disp_df = disp_df
        full_segment_disp_df = compare_view_model.station_table
        has_plot_data = compare_view_model.has_plot_data

        segment_temporal_export = None
        selected_evidence_export = None
        selected_station_labels = []
        drilldown_selected_df = pd.DataFrame()
        all_drilldown_context = None
        drilldown_zoom_metadata = None
        drilldown_zoom_benchmark_delta_recipe = None
        drilldown_zoom_benchmark_coverage_recipe = None

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
            _render_reference_correction_notice(
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
                _render_cached_recipe(
                    segment_figure_recipe,
                    run_id=run_id,
                    cache_key=segment_cache_key,
                    subject="segment insight",
                    build_label="segment insight figure build",
                    render_figure=render_segment_insight_export_figure,
                    timing_collector=timing_collector,
                )
                segment_temporal_export = _render_segment_temporal_evidence(
                    segment_temporal_bundle,
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
            if is_outlier_reporting_enabled:
                _render_delta_snr_outlier_report(
                    outlier_model,
                    outlier_report_view_model,
                    t=t,
                    language=presentation_context.language,
                    analysis_id=analysis_id,
                    run_id=run_id,
                    scope_token=scope_token,
                    is_sequential=is_sequential,
                    analysis_context=analysis_context,
                )

        render_page_anchor(STATION_INSIGHTS_ANCHOR_ID)
        level_three_container = st.container(
            key=(
                f"results_evidence_level_3_"
                f"{analysis_id}_{run_id}_{scope_token}"
            )
        )
        station_type = remote_station_type(analysis_id)
        station_insights_title = t["lbl_insights"]
        level_three_container.markdown(
            evidence_level_header_html(
                3,
                t["lbl_results_level_stations"],
                station_insights_title,
                t[
                    "sub_results_station_insights_multi"
                    if is_outlier_reporting_enabled
                    else "sub_results_station_insights"
                ].format(
                    station_type=station_type
                ),
                station_scope_text(
                    range_summary,
                    direction_summary,
                    len(sorted_disp_df),
                    analysis_id,
                    t,
                ),
            ),
            unsafe_allow_html=True,
        )
        with level_three_container:
            render_result_guidance_popover(
                RESULT_GUIDANCE_STATION_INSIGHTS,
                station_insights_title,
                language=presentation_context.language,
                translations=t,
                key=(
                    f"results_guidance_station_insights_"
                    f"{analysis_id}_{run_id}_{scope_token}"
                ),
                analysis_id=analysis_id,
                is_compare=True,
                is_sequential=is_sequential,
                analysis_context=analysis_context,
                allows_multiple_station_selection=(
                    is_outlier_reporting_enabled
                ),
            )
        # --- 1. Define layout columns ---
        # Give localized toggle labels enough room while preserving the filter width.
        col_ins1, col_ins2, col_ins3 = level_three_container.columns(
            STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS,
            vertical_alignment="center",
        )
        
        with col_ins1:
            sub_text = t["txt_station_insights_normalized_30dbm"]
            st.markdown(
                scope_context_html(sub_text.strip(" ()")),
                unsafe_allow_html=True,
            )
            
        with col_ins2:
            # Default to showing unpaired rows when the segment contains no joint
            # evidence but does contain target-only, reference-only, or async-both evidence.
            st.toggle(
                t["lbl_include_unpaired_evidence"],
                key=toggle_key,
                on_change=_sync_boolean_widget_state,
                args=(toggle_key, RESULTS_SHOW_NON_JOINT_STATE_KEY),
            )
            show_non_joint = _sync_boolean_widget_state(
                toggle_key,
                RESULTS_SHOW_NON_JOINT_STATE_KEY,
            )

        # --- DYNAMIC EXCEL-STYLE FILTER ---
        # sorted_disp_df is ready, so render the filter button in column 3.
        with col_ins3:
            # Subtle native Material Design filter button.
            with st.popover(
                t["lbl_filter"],
                icon=":material/filter_alt:",
                width="stretch",
            ):
                st.markdown(f"**{t['lbl_filter_columns']}**")
                filter_cols = st.multiselect(
                    t["lbl_select_columns"],
                    sorted_disp_df.columns,
                    label_visibility="collapsed",
                )
                
                for col in filter_cols:
                    if pd.api.types.is_numeric_dtype(sorted_disp_df[col]):
                        min_val = float(sorted_disp_df[col].min())
                        max_val = float(sorted_disp_df[col].max())
                        if min_val < max_val:
                            step = 1.0 if pd.api.types.is_integer_dtype(sorted_disp_df[col]) else 0.1
                            sel_range = st.slider(f"{col}", min_val, max_val, (min_val, max_val), step=step)
                            sorted_disp_df = sorted_disp_df[(sorted_disp_df[col] >= sel_range[0]) & (sorted_disp_df[col] <= sel_range[1])]
                    else:
                        unique_vals = sorted_disp_df[col].dropna().unique()
                        sel_vals = st.multiselect(f"{col}", unique_vals, default=[])
                        if sel_vals:
                            sorted_disp_df = sorted_disp_df[sorted_disp_df[col].isin(sel_vals)]

        # --- END FILTER ---

        station_insights_display_df = sorted_disp_df
        if is_outlier_reporting_enabled:
            focused_station_identities = (
                _focused_station_identities_for_scope(
                    st.session_state,
                    analysis_id=analysis_id,
                    run_id=run_id,
                    scope_token=scope_token,
                )
            )
            station_insights_display_df = (
                _prioritize_focused_station_identities(
                    sorted_disp_df,
                    station_col,
                    t['tbl_col_loc'],
                    focused_station_identities,
                )
            )

        with level_three_container:
            _render_reference_correction_notice(
                t,
                is_compare=True,
                is_sequential=is_sequential,
                analysis_context=analysis_context,
            )

        # Die Tabelle rendert nun den gefilterten Zustand
        tbl_key = f"tbl_{analysis_id}_{run_id}_{scope_token}"
        if is_outlier_reporting_enabled:
            selection_revision = st.session_state.get(
                RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY,
                0,
            )
            if isinstance(selection_revision, bool) or not isinstance(
                selection_revision,
                Integral,
            ):
                selection_revision = 0
            tbl_key += f"_multi_selection_{int(selection_revision)}"
        selected_stations_state_key = _selected_stations_persistent_state_key(
            True
        )
        allow_multiple_station_selection = is_outlier_reporting_enabled
        configured_station_identities = st.session_state.get(
            selected_stations_state_key
        )
        mode_appropriate_station_identities = (
            _station_selection_for_outlier_reporting_mode(
                configured_station_identities,
                is_outlier_reporting_enabled=(
                    is_outlier_reporting_enabled
                ),
            )
        )
        if (
            mode_appropriate_station_identities
            is not configured_station_identities
        ):
            # Turning the opt-in report off restores the historical singleton
            # Benchmark selection contract without discarding the first path.
            configured_station_identities = mode_appropriate_station_identities
            st.session_state[
                selected_stations_state_key
            ] = configured_station_identities
        selection_changed_key = f"{tbl_key}_selection_changed"
        dataframe_kwargs = {
            "width": "stretch",
            "hide_index": True,
            "selection_mode": (
                "multi-row"
                if allow_multiple_station_selection
                else "single-row"
            ),
            "on_select": partial(
                _mark_station_selection_changed,
                selection_changed_key,
            ),
            "key": tbl_key,
            "column_config": _snr_column_config(
                station_insights_display_df
            ),
        }
        selection_default_rows, missing_station_identities = (
            _station_selection_default_rows(
                station_insights_display_df,
                station_col,
                t['tbl_col_loc'],
                configured_station_identities,
                allow_multiple=allow_multiple_station_selection,
            )
        )
        with level_three_container:
            _warn_missing_station_identities(missing_station_identities, t)
        if _supports_dataframe_selection_default():
            dataframe_kwargs["selection_default"] = {
                "selection": {"rows": selection_default_rows}
            }
        with _timed_span(timing_collector, "station insights table render"):
            tbl_event = _render_compact_dataframe(
                level_three_container,
                station_insights_display_df,
                **dataframe_kwargs,
            )

        full_meta_df = full_segment_disp_df[[station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az']]].copy()
        all_drilldown_context = {
            "station_meta_df": full_meta_df,
            "station_col": station_col,
            "loc_col": t['tbl_col_loc'],
            "km_col": t['tbl_col_km'],
            "az_col": t['tbl_col_az'],
            "analysis_id": analysis_id,
            "is_sequential": bool(is_sequential),
            "show_non_joint": True,
            "is_local_median": bool(is_local_median),
            "col_u_name": col_u_name,
            "ref_header": ref_header,
            "tx_ab_repeat_interval_minutes": (
                analysis_context.tx_ab_repeat_interval_minutes
            ),
            "tx_ab_target_start_minute": (
                analysis_context.tx_ab_target_start_minute
            ),
            "tx_ab_reference_start_minute": (
                analysis_context.tx_ab_reference_start_minute
            ),
            "target_callsign": analysis_context.callsign,
            "lang": st.session_state.get("lang", "en"),
        }

        # ----------------------------------------------------
        # Render Raw Drill-Down Data (if user clicks a row)
        # ----------------------------------------------------
        # Streamlit selection remains user-driven after saved identities establish
        # the first render; deliberate deselection is persisted as an empty list.
        raw_sel_rows = tbl_event.selection.rows or []
        sel_rows = [
            row
            for row in raw_sel_rows
            if 0 <= row < len(station_insights_display_df)
        ]
        if not allow_multiple_station_selection:
            sel_rows = sel_rows[:1]
        _sync_selected_station_state_if_changed(
            selection_changed_key,
            selected_stations_state_key,
            station_insights_display_df,
            sel_rows,
            station_col,
            t['tbl_col_loc'],
            allow_multiple=allow_multiple_station_selection,
        )
        selected_station_table = station_insights_display_df
        selected_rows_for_evidence = sel_rows
        if allow_multiple_station_selection:
            # A report selection remains exact even when a local Station
            # Insights filter currently hides one of its station identities.
            selected_station_table = full_segment_disp_df
            selected_rows_for_evidence, _missing_from_active_scope = (
                _station_selection_default_rows(
                    selected_station_table,
                    station_col,
                    t['tbl_col_loc'],
                    st.session_state.get(selected_stations_state_key),
                    allow_multiple=True,
                )
            )
        if selected_rows_for_evidence:
            loc_col = t['tbl_col_loc']
            selected_meta_df = selected_station_table.iloc[
                selected_rows_for_evidence
            ][
                [station_col, loc_col, t['tbl_col_km'], t['tbl_col_az']]
            ].copy()
            selected_meta_df[station_col] = selected_meta_df[station_col].astype(str)
            selected_meta_df[loc_col] = selected_meta_df[loc_col].astype(str)
            selected_meta_df = selected_meta_df.drop_duplicates(subset=[station_col, loc_col])
            selected_identity_df = selected_meta_df[[station_col, loc_col]].copy()
            selected_identity_df.columns = ["peer_sign", "peer_grid"]
            selected_identity_df = selected_identity_df.drop_duplicates()
            selected_identity_pairs = tuple(
                (
                    str(callsign).strip().upper(),
                    str(locator).strip().upper(),
                )
                for callsign, locator in selected_identity_df[
                    ["peer_sign", "peer_grid"]
                ].itertuples(index=False, name=None)
            )
            selected_station_labels = (
                selected_identity_df["peer_sign"].astype(str) +
                " (" + selected_identity_df["peer_grid"].astype(str) + ")"
            ).tolist()
            selected_identity_pair_set = set(selected_identity_pairs)
            selected_thresholded_mask = [
                (callsign, locator) in selected_identity_pair_set
                for callsign, locator in zip(
                    df_seg["peer_sign"]
                    .astype(str)
                    .str.strip()
                    .str.upper(),
                    df_seg["peer_grid"]
                    .astype(str)
                    .str.strip()
                    .str.upper(),
                )
            ]
            selected_thresholded_rows = df_seg.loc[
                selected_thresholded_mask
            ].copy()
            selected_identity_cache_key = (
                selected_identity_pairs[0]
                if len(selected_identity_pairs) == 1
                else (
                    "multiple-selected-stations",
                    selected_identity_pairs,
                )
            )
            level_four_container = st.container(
                key=(
                    f"results_evidence_level_4_"
                    f"{analysis_id}_{run_id}_{scope_token}"
                )
            )
                
            try:
                with _timed_span(timing_collector, "selected station rows load"):
                    station_df = _load_station_rows_for_drilldown(
                        parquet_path,
                        selected_meta_df,
                        station_col,
                        loc_col
                    )
                with level_four_container:
                    selected_evidence_export = _render_selected_station_evidence(
                        station_df,
                        selected_identity_df,
                        is_sequential,
                        analysis_context.tx_ab_repeat_interval_minutes,
                        analysis_context.tx_ab_target_start_minute,
                        analysis_context.tx_ab_reference_start_minute,
                        t=t,
                        analysis_id=analysis_id,
                        run_id=run_id,
                        scope_token=scope_token,
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
                        thresholded_station_rows=(
                            selected_thresholded_rows
                        ),
                        analysis_start_t=analysis_start_t,
                        analysis_end_t=analysis_end_t,
                        target_only_label=(
                            t["leg_only_me"].format(
                                callsign=t["txt_target"]
                            )
                        ),
                        reference_only_label=(
                            t["leg_only_ref"].format(
                                ref_callsign=t["txt_reference"]
                            )
                        ),
                        language=presentation_context.language,
                        outlier_model=outlier_model,
                        timing_collector=timing_collector,
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
                    ) = _render_drilldown_header_and_controls(
                        selected_station_labels,
                        analysis_id,
                        run_id,
                        scope_token,
                        t,
                        True,
                        is_sequential,
                        analysis_context,
                        presentation_context.language,
                        analysis_start_utc=analysis_start_t,
                        analysis_end_utc=analysis_end_t,
                        selected_identity=selected_identity_for_zoom,
                        allow_multiple_station_selection=(
                            is_outlier_reporting_enabled
                        ),
                    )
                    focused_station_df = filter_station_rows_to_focus_window(
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
                        _drilldown_outlier_context_for_scope(
                            st.session_state,
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
                            drilldown_zoom_benchmark_delta_recipe,
                            drilldown_zoom_benchmark_coverage_recipe,
                        ) = _build_benchmark_drilldown_zoom_recipes(
                            focused_station_df,
                            selected_identity_df,
                            selected_thresholded_rows,
                            is_sequential,
                            analysis_context,
                            focus_window,
                            focus_time_bin,
                            (selected_evidence_export or {}).get(
                                "export_recipe"
                            ),
                            (selected_evidence_export or {}).get(
                                "coverage_export_recipe"
                            ),
                            t,
                            outlier_context=drilldown_outlier_context,
                            outlier_model=outlier_model,
                        )
                        drilldown_zoom_metadata = (
                            _drilldown_zoom_export_metadata(
                                focus_window,
                                selected_identity=selected_identity_for_zoom,
                                metric_recipe=(
                                    drilldown_zoom_benchmark_delta_recipe
                                ),
                                outlier_context=(
                                    drilldown_outlier_context
                                    if isinstance(
                                        drilldown_zoom_benchmark_delta_recipe,
                                        Mapping,
                                    )
                                    and drilldown_zoom_benchmark_delta_recipe.get(
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
                        if drilldown_zoom_benchmark_delta_recipe is not None:
                            _render_cached_recipe(
                                drilldown_zoom_benchmark_delta_recipe,
                                run_id=run_id,
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
                                timing_collector=timing_collector,
                            )
                        if drilldown_zoom_benchmark_coverage_recipe is not None:
                            _render_cached_recipe(
                                drilldown_zoom_benchmark_coverage_recipe,
                                run_id=run_id,
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
                                timing_collector=timing_collector,
                            )
                    with _timed_span(
                        timing_collector,
                        "drilldown table build",
                    ):
                        drill_df, info_msg = _build_drilldown_table(
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
                        drilldown_selected_df = _render_drilldown_dataframe(
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
                _log_artifact_read_failure(
                    exc,
                    parquet_path=parquet_path,
                    analysis_id=analysis_id,
                    run_id=run_id,
                    stage="selected station rows load",
                )
                level_four_container.warning(
                    t["warn_analysis_cache_expired"]
                )
        else:
            level_three_container.markdown(
                transition_prompt_html(
                    t[
                        "txt_results_transition_stations_multi"
                        if is_outlier_reporting_enabled
                        else "txt_results_transition_stations"
                    ]
                ),
                unsafe_allow_html=True,
            )

        delta_snr_outlier_export_tables = None
        delta_snr_outlier_export_metadata = None
        if is_outlier_reporting_enabled:
            delta_snr_outlier_export_tables = (
                build_delta_snr_outlier_export_tables(
                    outlier_model,
                    outlier_report_view_model,
                    is_sequential=is_sequential,
                )
            )
            delta_snr_outlier_export_metadata = (
                build_delta_snr_outlier_export_metadata(
                    outlier_model,
                    delta_snr_outlier_export_tables,
                )
            )

        register_inspector_export(
            translations=t,
            analysis_id=analysis_id,
            selected_segment=selected_seg,
            selected_distance=range_summary,
            selected_direction=direction_summary,
            selected_ranges=list(selected_ranges) if selected_ranges else [opt_full],
            selected_directions=list(selected_directions) if selected_directions else [opt_all_dir],
            show_non_joint=show_non_joint,
            evidence_time_bin=(selected_evidence_export or {}).get("time_bin"),
            segment_evidence_time_bin=(segment_temporal_export or {}).get("time_bin"),
            selected_stations=selected_station_labels,
            segment_figure_recipe=segment_figure_recipe,
            segment_temporal_evidence_figure_recipe=(
                segment_temporal_export or {}
            ).get("export_recipe"),
            segment_temporal_snr_deviation_figure_recipe=(
                segment_temporal_export or {}
            ).get("snr_export_recipe"),
            segment_temporal_coverage_figure_recipe=(
                segment_temporal_export or {}
            ).get("coverage_export_recipe"),
            selected_evidence_figure_recipe=(selected_evidence_export or {}).get("export_recipe"),
            selected_station_coverage_figure_recipe=(
                selected_evidence_export or {}
            ).get("coverage_export_recipe"),
            drilldown_zoom_metadata=drilldown_zoom_metadata,
            drilldown_zoom_benchmark_delta_snr_figure_recipe=(
                drilldown_zoom_benchmark_delta_recipe
            ),
            drilldown_zoom_benchmark_coverage_figure_recipe=(
                drilldown_zoom_benchmark_coverage_recipe
            ),
            station_insights_df=sorted_disp_df,
            drilldown_selected_df=drilldown_selected_df,
            all_drilldown_context=all_drilldown_context,
            reference_snr_header=f'{ref_header} SNR (dB)',
            allow_multiple_selected_stations=(
                allow_multiple_station_selection
            ),
            report_delta_snr_outlier_candidates=(
                is_outlier_reporting_enabled
            ),
            delta_snr_outlier_detector_version=(
                DELTA_SNR_OUTLIER_DETECTOR_VERSION
                if is_outlier_reporting_enabled
                else None
            ),
            delta_snr_outlier_detection_policy=(
                outlier_detection_policy
                if is_outlier_reporting_enabled
                else None
            ),
            delta_snr_outlier_export_tables=(
                delta_snr_outlier_export_tables
            ),
            delta_snr_outlier_export_metadata=(
                delta_snr_outlier_export_metadata
            ),
        )

        if show_export_button:
            render_download_all_results(t)
