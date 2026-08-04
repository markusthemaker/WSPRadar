"""
Segment Inspector & Results Components Module.
Contains the interactive drill-down UI (histograms, data tables) and 
compact recipes for lazy high-resolution result exports. Isolated as Streamlit fragments
to allow UI updates without triggering full-page reruns.
"""

import inspect
from collections.abc import Mapping
from contextlib import nullcontext
from functools import partial
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
from ui.result_state import INSPECTOR_CACHE_STATE_KEY
from ui.plots.evidence_figures import (
    _segment_figure_export_recipe,
    _segment_temporal_evidence_export_recipe,
    _selected_evidence_export_recipe,
    _time_agg_options_for_span,
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
    SUCCESS_TEMPORAL_TIME_BINS,
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
    RESULT_GUIDANCE_SEGMENT,
    RESULT_GUIDANCE_SELECTED_STATIONS,
    RESULT_GUIDANCE_STATION_INSIGHTS,
    RESULT_GUIDANCE_SUCCESS_EVIDENCE,
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    render_result_guidance_popover,
)
from ui.reference_correction import configured_snr_correction_notice

INSPECTOR_CACHE_VERSION = 44
INSPECTOR_PNG_RENDER_VERSION = 38
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
RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY = (
    "val_results_selected_stations_compare"
)
RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY = (
    "val_results_selected_stations_absolute"
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


def _compare_temporal_time_source(
    paired_evidence_rows,
    comparison_units,
):
    """Choose adaptive-bin timestamps without changing the absolute view.

    The established absolute Delta-SNR figure owns the segment control policy
    whenever paired evidence exists. Coverage-only scopes fall back to all
    retained comparison units so their shared control remains available.
    """
    if (
        isinstance(paired_evidence_rows, pd.DataFrame)
        and not paired_evidence_rows.empty
        and "plot_time" in paired_evidence_rows.columns
    ):
        return paired_evidence_rows[["plot_time"]].copy()
    if (
        isinstance(comparison_units, pd.DataFrame)
        and not comparison_units.empty
        and "evidence_utc" in comparison_units.columns
    ):
        return comparison_units[["evidence_utc"]].rename(
            columns={"evidence_utc": "plot_time"}
        )
    return pd.DataFrame(columns=["plot_time"])


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


def _station_selection_default_rows(
    station_table,
    station_column,
    locator_column,
    configured_identities,
):
    """Resolve saved station identities to current display-row positions.

    A missing explicit identity is reported separately and never causes a
    substitute row to be selected. A ``None`` configuration retains the normal
    first-row default, whereas an empty list resolves to no selected rows.
    """
    normalized_identities = _validate_single_station_identity_records(
        configured_identities
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

    identity_record = normalized_identities[0]
    identity_pair = (
        identity_record["callsign"],
        identity_record["locator"],
    )
    row_position = available_rows.get(identity_pair)
    if row_position is None:
        return [], [identity_record]
    return [row_position], []


def _station_identity_records_for_rows(
    station_table,
    selected_rows,
    station_column,
    locator_column,
):
    """Return the station identity for zero or one valid selected row."""
    valid_rows = [
        row_position
        for row_position in selected_rows
        if isinstance(row_position, Integral)
        and 0 <= row_position < len(station_table)
    ]
    if len(valid_rows) > 1:
        raise ValueError("Station selection must contain at most one row.")
    if not valid_rows:
        return []

    row = station_table.iloc[valid_rows[0]]
    identity_record = _station_identity_record(
        row[station_column],
        row[locator_column],
    )
    if identity_record is None:
        raise ValueError(
            "Selected station row must contain a callsign and locator."
        )
    return _validate_single_station_identity_records([identity_record])


def _sync_selected_station_state(
    persistent_key,
    station_table,
    selected_rows,
    station_column,
    locator_column,
):
    """Persist an explicit empty or single-station selection."""
    selected_identities = _station_identity_records_for_rows(
        station_table,
        selected_rows,
        station_column,
        locator_column,
    )
    st.session_state[persistent_key] = selected_identities
    return selected_identities


def _mark_station_selection_changed(selection_changed_key):
    """Record that a user, rather than a table default, changed selection."""
    st.session_state[selection_changed_key] = True


def _sync_selected_station_state_if_changed(
    selection_changed_key,
    persistent_key,
    station_table,
    selected_rows,
    station_column,
    locator_column,
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
    timing_collector=None,
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

    drilldown_title = t["hdr_results_drilldown"]
    st.markdown(
        evidence_level_header_html(
            5,
            t["lbl_results_level_rows"],
            drilldown_title,
            drilldown_subtitle(
                selected_station_labels,
                analysis_id,
                t,
            ),
        ),
        unsafe_allow_html=True,
    )
    render_result_guidance_popover(
        RESULT_GUIDANCE_DRILLDOWN,
        drilldown_title,
        language=language,
        translations=t,
        key=(
            f"results_guidance_drilldown_"
            f"{analysis_id}_{run_id}_{scope_token}"
        ),
        analysis_id=analysis_id,
        is_compare=is_compare,
        is_sequential=is_sequential,
        analysis_context=analysis_context,
    )
    normalization_note = t["txt_snr_values_normalized_30dbm"]
    filter_note = t["txt_results_drilldown_filter_note"]
    st.markdown(
        scope_context_html(f"{filter_note} · {normalization_note}"),
        unsafe_allow_html=True,
    )

    _filter_spacer, col_d2 = st.columns([0.7, 0.3], vertical_alignment="center")
    with col_d2:
        with st.popover(
            t["lbl_filter"],
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




def _selected_evidence_figure_title(
    station_identities,
    evidence_count,
    *,
    analysis_id,
    is_sequential,
    translations,
):
    """Build a localized selected-station figure title from semantic evidence."""
    heading = translations["hdr_results_selected_station_evidence"]
    selection_context = selected_station_context(
        station_identities,
        evidence_count,
        analysis_id=analysis_id,
        is_sequential=is_sequential,
        translations=translations,
    )
    return translations[
        "fmt_results_selected_station_evidence_title"
    ].format(
        heading=heading,
        selection_context=selection_context,
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
    timing_collector=None,
):
    """Render absolute Delta-SNR and coverage for one selected Benchmark path."""
    identity_meta = _prepare_identity_meta(selected_identity_df)
    if identity_meta.empty:
        return None
    if len(identity_meta) > 1:
        raise ValueError(
            "Selected Station Evidence requires exactly one station identity."
        )
    identity_labels = identity_meta["identity"].tolist()
    reference_snr_correction_notice = configured_snr_correction_notice(
        analysis_context,
        t,
        is_compare=True,
        is_sequential=is_sequential,
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
        )
        time_agg_options = tuple(SUCCESS_TEMPORAL_TIME_BINS)
        time_agg_default = "3h"
        base_recipe = None
        if not evidence_df.empty:
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
        if not comparison_units.empty:
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
    selected_evidence_heading = t["hdr_results_selected_station_evidence"]
    st.markdown(
        evidence_level_header_html(
            4,
            t["lbl_results_level_selection"],
            selected_evidence_heading,
            selected_station_context(
                identity_labels,
                evidence_count,
                analysis_id=analysis_id,
                is_sequential=is_sequential,
                translations=t,
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
        selected_station_count=1,
    )
    if selected_bundle.get("base_recipe") is None:
        st.markdown(
            scope_context_html(
                t["txt_results_selected_no_paired_evidence"]
            ),
            unsafe_allow_html=True,
        )
    if selected_bundle.get("coverage_recipe") is None:
        st.markdown(
            scope_context_html(
                t[
                    "fig_selected_compare_coverage_unavailable"
                ]
            ),
            unsafe_allow_html=True,
        )
        return None

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
        _render_cached_recipe(
            selected_recipe,
            run_id=run_id,
            cache_key=cache_key + (time_agg, "dual-temporal"),
            subject="selected evidence",
            build_label="selected evidence figure build",
            render_figure=render_selected_evidence_export_figure,
            timing_collector=timing_collector,
        )

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
            + ("segment temporal evidence", selected_time_bin),
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

        with _timed_span(timing_collector, "drilldown table build"):
            export_station_col = opportunity_display_model[
                "export_station_column"
            ]
            selected_meta_export_df = selected_meta_df.rename(
                columns={station_col: export_station_col}
            )
            selected_station_rows_export = selected_station_rows.rename(
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
            level_four_container.info(info_msg, icon=":material/info:")
        elif not drill_df.empty:
            level_five_container = st.container(
                key=(
                    f"results_evidence_level_5_"
                    f"{analysis_id}_{run_id}_{scope_token}"
                )
            )
            with level_five_container:
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

        if df_seg.empty:
            st.info(
                t["msg_results_no_stations_in_scope"],
                icon=":material/info:",
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
            presentation_context.language,
            presentation_context.theme,
            title,
            selected_seg,
        )
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
                    temporal_time_source = _compare_temporal_time_source(
                        segment_temporal_rows,
                        segment_comparison_units,
                    )
                    temporal_time_options, temporal_time_default = (
                        _time_agg_options_for_span(temporal_time_source)
                    )
                    del temporal_time_source
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
                    temporal_base_recipe = None
                    if not segment_temporal_rows.empty:
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
                                    reference_snr_correction_notice=(
                                        reference_snr_correction_notice
                                    ),
                                    chronological_title=(
                                        chronological_title_template
                                    ),
                                    chronological_x_label=t[
                                        "fig_segment_chronological_x"
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

            del vals, evidence_meta_df
            segment_bundle = {
                "view_model": compare_view_model,
                "figure_recipe": segment_figure_recipe,
                "temporal_bundle": segment_temporal_bundle,
                "summary": segment_summary,
                "evidence_station_count": int(segment_station_count),
                "evidence_count": int(segment_evidence_count),
            }
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
                t["sub_results_station_insights"].format(
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

        with level_three_container:
            _render_reference_correction_notice(
                t,
                is_compare=True,
                is_sequential=is_sequential,
                analysis_context=analysis_context,
            )

        # Die Tabelle rendert nun den gefilterten Zustand
        tbl_key = f"tbl_{analysis_id}_{run_id}_{scope_token}"
        selected_stations_state_key = _selected_stations_persistent_state_key(
            True
        )
        configured_station_identities = st.session_state.get(
            selected_stations_state_key
        )
        selection_changed_key = f"{tbl_key}_selection_changed"
        dataframe_kwargs = {
            "width": "stretch",
            "hide_index": True,
            "selection_mode": "single-row",
            "on_select": partial(
                _mark_station_selection_changed,
                selection_changed_key,
            ),
            "key": tbl_key,
            "column_config": _snr_column_config(sorted_disp_df),
        }
        selection_default_rows, missing_station_identities = (
            _station_selection_default_rows(
                sorted_disp_df,
                station_col,
                t['tbl_col_loc'],
                configured_station_identities,
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
                sorted_disp_df,
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
            if 0 <= row < len(sorted_disp_df)
        ][:1]
        _sync_selected_station_state_if_changed(
            selection_changed_key,
            selected_stations_state_key,
            sorted_disp_df,
            sel_rows,
            station_col,
            t['tbl_col_loc'],
        )
        if sel_rows:
            loc_col = t['tbl_col_loc']
            selected_meta_df = sorted_disp_df.iloc[sel_rows][[station_col, loc_col, t['tbl_col_km'], t['tbl_col_az']]].copy()
            selected_meta_df[station_col] = selected_meta_df[station_col].astype(str)
            selected_meta_df[loc_col] = selected_meta_df[loc_col].astype(str)
            selected_meta_df = selected_meta_df.drop_duplicates(subset=[station_col, loc_col])
            selected_identity_df = selected_meta_df[[station_col, loc_col]].copy()
            selected_identity_df.columns = ["peer_sign", "peer_grid"]
            selected_identity_df = selected_identity_df.drop_duplicates()
            selected_station = str(
                selected_identity_df.iloc[0]["peer_sign"]
            ).strip().upper()
            selected_locator = str(
                selected_identity_df.iloc[0]["peer_grid"]
            ).strip().upper()
            selected_station_labels = (
                selected_identity_df["peer_sign"].astype(str) +
                " (" + selected_identity_df["peer_grid"].astype(str) + ")"
            ).tolist()
            selected_thresholded_rows = df_seg[
                df_seg["peer_sign"].astype(str).str.strip().str.upper().eq(
                    selected_station
                )
                & df_seg[
                    "peer_grid"
                ].astype(str).str.strip().str.upper().eq(
                    selected_locator
                )
            ].copy()
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
                            selected_station,
                            selected_locator,
                            bool(is_sequential),
                            int(analysis_context.tx_ab_repeat_interval_minutes),
                            int(analysis_context.tx_ab_target_start_minute),
                            int(analysis_context.tx_ab_reference_start_minute),
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
                        timing_collector=timing_collector,
                    )
                level_four_container.markdown(
                    transition_prompt_html(
                        t["txt_results_transition_rows"]
                    ),
                    unsafe_allow_html=True,
                )
                with _timed_span(timing_collector, "drilldown table build"):
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
                        station_rows_df=station_df,
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
                    level_four_container.info(
                        info_msg,
                        icon=":material/info:",
                    )
                elif drill_df is not None and not drill_df.empty:
                    level_five_container = st.container(
                        key=(
                            f"results_evidence_level_5_"
                            f"{analysis_id}_{run_id}_{scope_token}"
                        )
                    )
                    with level_five_container:
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
                            timing_collector=timing_collector,
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
                    t["txt_results_transition_stations"]
                ),
                unsafe_allow_html=True,
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
            station_insights_df=sorted_disp_df,
            drilldown_selected_df=drilldown_selected_df,
            all_drilldown_context=all_drilldown_context,
            reference_snr_header=f'{ref_header} SNR (dB)',
        )

        if show_export_button:
            render_download_all_results(t)
