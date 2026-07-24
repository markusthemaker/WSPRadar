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
    STATION_SELECTION_ALL,
)
from ui.matplotlib_renderer import (
    dispose_matplotlib_figure,
    get_matplotlib_render_mode,
    matplotlib_render_span_label,
    render_matplotlib_figure,
    render_matplotlib_image_bytes,
)
from ui.results_export import register_inspector_export, render_download_all_results
from core.opportunity_engine import (
    OPPORTUNITY_DRILLDOWN_VIEW_COLUMNS,
    OPPORTUNITY_SEGMENT_VIEW_COLUMNS,
    opportunity_utc_from_time_slot,
)
from core.artifact_store import ARTIFACT_STORE, read_parquet_artifact
from core.performance_timer import log_performance_event
from ui.inspector.evidence_data import (
    _build_evidence_points,
    _build_segment_evidence_points,
    _prepare_identity_meta,
)
from ui.inspector.drilldown import (
    _build_drilldown_table,
    _load_station_rows_for_drilldown,
    _unique_station_order,
)
from ui.inspector.view_models import (
    build_compare_inspector_view_model,
    build_inspector_options,
    build_opportunity_inspector_view_model,
    compare_scope_availability,
    filter_inspector_scope,
)
from ui.inspector.session_cache import INSPECTOR_CACHE_STATE_KEY, SessionInspectorCache
from ui.plots.evidence_figures import (
    SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL,
    SELECTED_TEMPORAL_VIEW_UTC_HOUR,
    _add_horizontal_grid,
    _segment_figure_export_recipe,
    _segment_temporal_evidence_export_recipe,
    _selected_evidence_export_recipe,
    _time_agg_options_for_span,
    render_segment_insight_export_figure,
    render_segment_temporal_evidence_export_figure,
    render_selected_evidence_export_figure,
)
from ui.plots.opportunity_figures import (
    _as_utc_timestamp,
    _opportunity_selected_recipe,
    _opportunity_segment_recipe,
    _render_opportunity_selected_figure,
    _render_opportunity_segment_figure,
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
    selected_station_context,
    station_scope_text,
    transition_prompt_html,
)

INSPECTOR_CACHE_VERSION = 16
INSPECTOR_PNG_RENDER_VERSION = 12
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
RESULTS_STATION_TEMPORAL_VIEW_COMPARE_STATE_KEY = (
    "val_results_station_temporal_view_compare"
)
RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY = (
    "val_results_selected_stations_compare"
)
RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY = (
    "val_results_selected_stations_absolute"
)
SELECTED_TEMPORAL_CONTROL_COLUMN_WIDTHS = (1, 2)
SEGMENT_TEMPORAL_CONTROL_COLUMN_WIDTHS = (1.6, 4)
STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS = (5, 4, 3)
INSPECTOR_CACHE_NAMESPACE_LIMITS = {
    "options": INSPECTOR_CACHE_OPTIONS_MAX_ENTRIES,
    "segment": INSPECTOR_CACHE_SEGMENT_MAX_ENTRIES,
    "selected": INSPECTOR_CACHE_SELECTED_MAX_ENTRIES,
    "png": INSPECTOR_CACHE_PNG_MAX_ENTRIES,
}


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
    """Return canonical range and direction keys for Compare or Success."""
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


def _initialize_choice_widget_state(
    widget_key,
    persistent_key,
    options,
    fallback,
):
    """Initialize a bounded widget choice from canonical saved-config state."""
    available_options = tuple(options)
    if not available_options:
        raise ValueError("At least one display option is required.")
    selected_option = st.session_state.get(persistent_key)
    if selected_option not in available_options:
        selected_option = (
            fallback if fallback in available_options else available_options[0]
        )
    st.session_state[persistent_key] = selected_option
    st.session_state[widget_key] = selected_option
    return selected_option


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


def _render_labeled_segment_time_bin_control(
    label,
    options,
    widget_key,
    *,
    on_change=None,
    on_change_args=(),
):
    """Render the segment aggregation label immediately before its selector."""
    label_column, selector_column = st.columns(
        SEGMENT_TEMPORAL_CONTROL_COLUMN_WIDTHS,
        vertical_alignment="center",
    )
    with label_column:
        st.markdown(f"**{label}**")
    with selector_column:
        return _render_stretched_time_bin_control(
            label,
            options,
            widget_key,
            on_change=on_change,
            on_change_args=on_change_args,
        )


def _segment_temporal_figure_title(title, analysis_id, selected_segment, t):
    """Build the localized Compare-temporal title while preserving its scope text."""
    original_title = str(title)
    _, separator, comparison_title = original_title.partition(":")
    if not separator:
        comparison_title = original_title
    if str(analysis_id).upper().startswith("TX"):
        temporal_prefix = t.get(
            "fig_tx_comp_temporal_prefix",
            "TX Compare Temporal",
        )
    else:
        temporal_prefix = t.get(
            "fig_rx_comp_temporal_prefix",
            "RX Compare Temporal",
        )
    return (
        f"{temporal_prefix}: {comparison_title.strip()} - {selected_segment}"
    )


def _folded_utc_hour_panel_title(t):
    """Return the complete localized title for the fixed one-hour folded panel."""
    base_title = t.get(
        "fig_segment_utc_hour_delta",
        "\u0394 SNR by UTC Hour",
    )
    return t.get(
        "fig_segment_utc_hour_title",
        f"{base_title} (1 h bins)",
    )


def _sync_time_bin_widget_state(widget_key, persistent_key, options, fallback):
    """Copy one widget selection into canonical state after option validation."""
    selected_time_bin = _validated_time_bin(
        options,
        st.session_state.get(widget_key),
        fallback,
    )
    st.session_state[persistent_key] = selected_time_bin
    return selected_time_bin


def _sync_choice_widget_state(widget_key, persistent_key, options, fallback):
    """Copy one bounded widget choice into canonical saved-config state."""
    available_options = tuple(options)
    if not available_options:
        raise ValueError("At least one display option is required.")
    selected_option = st.session_state.get(widget_key)
    if selected_option not in available_options:
        selected_option = (
            fallback if fallback in available_options else available_options[0]
        )
    st.session_state[persistent_key] = selected_option
    return selected_option


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


def _normalize_station_identity_records(configured_identities):
    """Normalize and ordered-deduplicate saved ``callsign``/``locator`` pairs.

    ``None`` is preserved because it means that no explicit selection exists and
    the historical first-row default should apply. ``"all"`` preserves the
    dynamic all-stations intent. Invalid records are ignored; an explicit empty
    sequence remains an explicit empty selection.
    """
    if configured_identities is None:
        return None
    if configured_identities == STATION_SELECTION_ALL:
        return STATION_SELECTION_ALL
    if not isinstance(configured_identities, (list, tuple)):
        return []

    normalized_records = []
    seen_identities = set()
    for configured_identity in configured_identities:
        if not isinstance(configured_identity, Mapping):
            continue
        identity_record = _station_identity_record(
            configured_identity.get("callsign"),
            configured_identity.get("locator"),
        )
        if identity_record is None:
            continue
        identity_pair = (
            identity_record["callsign"],
            identity_record["locator"],
        )
        if identity_pair in seen_identities:
            continue
        seen_identities.add(identity_pair)
        normalized_records.append(identity_record)
    return normalized_records


def _station_selection_default_rows(
    station_table,
    station_column,
    locator_column,
    configured_identities,
):
    """Resolve saved station identities to current display-row positions.

    The returned row positions follow the configured identity order. Missing
    identities are reported separately and never cause a substitute row to be
    selected. A ``None`` configuration retains the legacy first-row default,
    whereas an empty list resolves to no selected rows.
    """
    normalized_identities = _normalize_station_identity_records(
        configured_identities
    )
    if normalized_identities is None:
        return ([0] if not station_table.empty else []), []
    if normalized_identities == STATION_SELECTION_ALL:
        return list(range(len(station_table))), []

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


def _station_identity_records_for_rows(
    station_table,
    selected_rows,
    station_column,
    locator_column,
):
    """Return ordered, deduplicated station records for valid selected rows."""
    valid_rows = [
        row_position
        for row_position in selected_rows
        if isinstance(row_position, Integral)
        and 0 <= row_position < len(station_table)
    ]
    selected_records = []
    seen_identities = set()
    for row_position in valid_rows:
        row = station_table.iloc[row_position]
        identity_record = _station_identity_record(
            row[station_column],
            row[locator_column],
        )
        if identity_record is None:
            continue
        identity_pair = (
            identity_record["callsign"],
            identity_record["locator"],
        )
        if identity_pair in seen_identities:
            continue
        seen_identities.add(identity_pair)
        selected_records.append(identity_record)
    return selected_records


def _sync_selected_station_state(
    persistent_key,
    station_table,
    selected_rows,
    station_column,
    locator_column,
    selection_universe_table=None,
):
    """Persist explicit identities or compact a complete selection to ``all``.

    ``selection_universe_table`` must represent the table after durable
    visibility controls but before transient table filters. This prevents a
    filtered subset from being broadened when ``all`` is restored later.
    """
    selected_identities = _station_identity_records_for_rows(
        station_table,
        selected_rows,
        station_column,
        locator_column,
    )
    selection_universe_table = (
        station_table
        if selection_universe_table is None
        else selection_universe_table
    )
    universe_identities = _station_identity_records_for_rows(
        selection_universe_table,
        range(len(selection_universe_table)),
        station_column,
        locator_column,
    )
    selected_identity_pairs = {
        (identity["callsign"], identity["locator"])
        for identity in selected_identities
    }
    universe_identity_pairs = {
        (identity["callsign"], identity["locator"])
        for identity in universe_identities
    }
    persisted_selection = (
        STATION_SELECTION_ALL
        if universe_identity_pairs
        and selected_identity_pairs == universe_identity_pairs
        else selected_identities
    )
    st.session_state[persistent_key] = persisted_selection
    return persisted_selection


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
    selection_universe_table=None,
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
        selection_universe_table,
    )


def _selection_requires_zero_hit_rows(
    station_table,
    station_column,
    locator_column,
    hit_column,
    configured_identities,
):
    """Return whether a saved Success selection includes a hidden zero-hit row."""
    normalized_identities = _normalize_station_identity_records(
        configured_identities
    )
    if (
        not normalized_identities
        or normalized_identities == STATION_SELECTION_ALL
    ):
        return False
    selected_pairs = {
        (identity["callsign"], identity["locator"])
        for identity in normalized_identities
    }
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
        if identity_pair not in selected_pairs:
            continue
        hit_count = hit_counts.iloc[row_position]
        if pd.isna(hit_count) or hit_count <= 0:
            return True
    return False


def _warn_missing_station_identities(missing_identities, t):
    """Warn that saved identities are unavailable without choosing substitutes."""
    if not missing_identities:
        return
    missing_labels = ", ".join(
        f"{identity['callsign']} ({identity['locator']})"
        for identity in missing_identities
    )
    warning_template = t.get(
        "warn_saved_station_unavailable",
        "Saved station selection could not be fully restored because these "
        "stations are not available in the current Station Insights table: "
        "{stations}. No substitute was selected.",
    )
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

def _selection_summary(selection, all_option, item_kind, lang):
    """Build a compact scope label without losing single-selection detail."""
    if not selection:
        return all_option
    limit = 2 if item_kind == "range" else 4
    if len(selection) <= limit:
        return ", ".join(selection)
    if lang == "de":
        noun = "Bereiche" if item_kind == "range" else "Richtungen"
    else:
        noun = "ranges" if item_kind == "range" else "directions"
    return f"{len(selection)} {noun}"



def _is_median_display_column(column_name):
    text = str(column_name).lower()
    return "median" in text or "micro-med" in text

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
        "Norm@1W" in text or
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


def _reference_correction_note(t, is_compare):
    """Return the active reference-SNR correction notice, or None when inactive."""
    if not is_compare:
        return None
    benchmark_offset_db = round(float(st.session_state.get("val_benchmark_offset_db", 0.0)), 1)
    if abs(benchmark_offset_db) < 0.05:
        return None
    offset_note = t.get(
        "txt_benchmark_offset_note",
        "Ref SNR Corr: {offset:+.1f} dB"
    )
    return offset_note.format(offset=benchmark_offset_db)

def _render_reference_correction_notice(t, is_compare):
    """Render the correction notice as a full-width one-liner on desktop."""
    note = _reference_correction_note(t, is_compare)
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
            {note}
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


def _compare_metric_distribution_summary(values, template):
    """Format the median and arithmetic mean of one plotted Compare distribution."""
    numeric_values = np.asarray(values, dtype=float)
    numeric_values = numeric_values[np.isfinite(numeric_values)]
    if len(numeric_values) == 0:
        return None

    return template.format(
        median=f"{float(np.median(numeric_values)):+.1f}",
        mean=f"{float(np.mean(numeric_values)):+.1f}",
    )


def _metric_median_summary(values, is_compare, prefix=""):
    """Return a compact median summary without inferential interval claims."""
    numeric_values = pd.to_numeric(
        pd.Series(values),
        errors="coerce",
    ).dropna()
    if numeric_values.empty:
        return None

    median = float(numeric_values.median())
    formatted_median = f"{median:+.1f}" if is_compare else f"{median:.1f}"
    metric_name = "\u0394 SNR" if is_compare else "SNR"
    prefix_text = f"{prefix} | " if prefix else ""
    return f"{prefix_text}median {metric_name} {formatted_median} dB"


def _supports_dataframe_selection_default():
    """Return True when the installed Streamlit version can preselect dataframe rows."""
    try:
        return "selection_default" in inspect.signature(st.dataframe).parameters
    except (TypeError, ValueError):
        return False

def _snr_column_config(df):
    """Keep numeric SNR columns right-aligned while controlling displayed precision."""
    config = {}
    for col in df.columns:
        if _is_snr_display_column(col) and pd.api.types.is_numeric_dtype(df[col]):
            config[col] = st.column_config.NumberColumn(format="%.1f")
    return config


def _evidence_labels(is_compare, translations):
    """Return localized UI labels for the selected-station evidence plots."""
    if st.session_state.get("lang") == "de":
        if is_compare:
            return {
                "dist_title": "\u0394 SNR Verteilung",
                "time_title": "\u0394 SNR ueber Zeit",
                "y_label": "\u0394 SNR (dB)",
                "x_label": "Datum/Uhrzeit (UTC)",
                "aggregate": "Selected Stations",
                "median_label": "Median",
                "bin_median_label": translations.get(
                    "fig_temporal_bin_median",
                    "Lokaler Median",
                ),
                "pooled_median_label": "Median",
                "mean_label": "Mittelwert",
                "pooled_mean_label": "Mittelwert",
                "count_label": "Anzahl Joint Spots",
                "density_label": "Relative Joint-Spot-Dichte (% des Panelmaximums)",
                "median_focus_axis_label": (
                    "\u0394 SNR (dB \u00b7 nichtlinear um Median zentriert)"
                ),
            }
        return {
            "dist_title": "Normiertes SNR Verteilung",
            "time_title": "Normiertes SNR ueber Zeit",
            "y_label": "Normiertes SNR (dB @ 1W)",
            "x_label": "Datum/Uhrzeit (UTC)",
            "aggregate": "Selected Stations",
            "median_label": "Median",
            "pooled_median_label": "Gepoolter Median",
            "mean_label": "Arithmetisches Mittel",
            "pooled_mean_label": "Gepooltes arithmetisches Mittel",
        }

    if is_compare:
        return {
            "dist_title": "\u0394 SNR Distribution",
            "time_title": "\u0394 SNR over Time",
            "y_label": "\u0394 SNR (dB)",
            "x_label": "Date/Time (UTC)",
            "aggregate": "Selected Stations",
            "median_label": "Median",
            "bin_median_label": translations.get(
                "fig_temporal_bin_median",
                "Bin median",
            ),
            "pooled_median_label": "Median",
            "mean_label": "Mean",
            "pooled_mean_label": "Mean",
            "count_label": "Joint spot count",
            "density_label": "Relative joint-spot density (% of panel maximum)",
            "median_focus_axis_label": (
                "\u0394 SNR (dB \u00b7 median-centered nonlinear)"
            ),
        }
    return {
        "dist_title": "Normalized SNR Distribution",
        "time_title": "Normalized SNR over Time",
        "y_label": "Normalized SNR (dB @ 1 W)",
        "x_label": "Date/Time (UTC)",
        "aggregate": "Selected Stations",
        "median_label": "Median",
        "pooled_median_label": "Pooled median",
        "mean_label": "Arithmetic mean",
        "pooled_mean_label": "Pooled arithmetic mean",
    }






















def _render_drilldown_dataframe(
    drill_df,
    selected_station_labels,
    analysis_id,
    run_id,
    scope_token,
    t,
    is_compare,
    timing_collector=None,
):
    """Render selected drill-down rows with local filters and return the displayed dataframe."""
    if drill_df is None or drill_df.empty:
        return pd.DataFrame()

    st.markdown(
        evidence_level_header_html(
            5,
            t.get("lbl_results_level_rows", "Row-level evidence"),
            t.get("hdr_results_drilldown", "Drill-Down Data"),
            drilldown_subtitle(
                selected_station_labels,
                analysis_id,
                t,
            ),
        ),
        unsafe_allow_html=True,
    )
    normalization_note = (
        "SNR-Werte sind auf 1 W normiert."
        if st.session_state.get("lang") == "de"
        else "SNR values are normalized to 1 W."
    )
    filter_note = t.get(
        "txt_results_drilldown_filter_note",
        "Filters change only the displayed table, not the completed analysis.",
    )
    st.markdown(
        scope_context_html(f"{filter_note} · {normalization_note}"),
        unsafe_allow_html=True,
    )

    _filter_spacer, col_d2 = st.columns([0.7, 0.3], vertical_alignment="center")
    with col_d2:
        with st.popover("Filter", icon=":material/filter_alt:", width="stretch"):
            st.markdown("**Filter column(s):**")
            d_filter_cols = st.multiselect(
                "Select Columns",
                drill_df.columns,
                label_visibility="collapsed",
                key=f"d_flt_{analysis_id}_{run_id}_{scope_token}"
            )

            for col in d_filter_cols:
                if pd.api.types.is_numeric_dtype(drill_df[col]):
                    min_val = float(drill_df[col].min())
                    max_val = float(drill_df[col].max())
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
                        drill_df = drill_df[(drill_df[col] >= sel_range[0]) & (drill_df[col] <= sel_range[1])]
                else:
                    unique_vals = drill_df[col].astype(str).dropna().unique()
                    sel_vals = st.multiselect(
                        f"{col}",
                        unique_vals,
                        default=[],
                        key=f"d_ms_{col}_{analysis_id}_{run_id}_{scope_token}"
                    )
                    if sel_vals:
                        drill_df = drill_df[drill_df[col].astype(str).isin(sel_vals)]

    _render_reference_correction_notice(t, is_compare)
    with _timed_span(timing_collector, "drilldown dataframe render"):
        drill_display_df = _format_snr_display_columns(drill_df)
        st.dataframe(drill_display_df, width='stretch', hide_index=True)
    return drill_df.copy()




def _render_selected_station_evidence(
    station_df,
    selected_identity_df,
    is_compare,
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
    timing_collector=None,
):
    """Render selected evidence with a saved Compare temporal-view selector."""
    identity_meta = _prepare_identity_meta(selected_identity_df)
    if identity_meta.empty:
        return None
    identity_labels = identity_meta["identity"].tolist()

    selected_bundle, selected_cache_hit = _inspector_cache_get(
        run_id,
        "selected",
        cache_key,
        timing_collector,
        item="selected evidence model",
    )
    if not selected_cache_hit:
        with _timed_span(timing_collector, "selected evidence points build"):
            evidence_df = _build_evidence_points(
                station_df,
                identity_meta,
                is_compare,
                is_sequential,
                tx_ab_repeat_interval_minutes=tx_ab_repeat_interval_minutes,
                tx_ab_target_start_minute=tx_ab_target_start_minute,
                tx_ab_reference_start_minute=tx_ab_reference_start_minute,
            )
        if evidence_df.empty:
            st.markdown(
                evidence_level_header_html(
                    4,
                    t.get("lbl_results_level_selection", "Selected stations"),
                    t.get(
                        "hdr_results_selected_station_evidence",
                        "Selected Station Evidence",
                    ),
                    selected_station_context(
                        identity_labels,
                        0,
                        analysis_id=analysis_id,
                        is_compare=is_compare,
                        is_sequential=is_sequential,
                        translations=t,
                    ),
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                scope_context_html(
                    t.get(
                        "txt_results_selected_no_paired_evidence",
                        "No paired evidence is available for this selection; "
                        "retained unpaired rows can still be audited below.",
                    )
                ),
                unsafe_allow_html=True,
            )
            return None

        labels = _evidence_labels(is_compare, t)
        if is_sequential:
            labels["count_label"] = t.get(
                "fig_scheduled_pair_count",
                "Scheduled pair count",
            )
            labels["density_label"] = t.get(
                "fig_relative_scheduled_pair_density",
                "Relative scheduled-pair density (% of panel maximum)",
            )
        selected_count = len(identity_labels)
        evidence_count = len(evidence_df)
        evidence_basis = (
            "scheduled pairs" if is_sequential
            else "joint spots"
            if is_compare
            else "spots"
        )
        evidence_title_base = "Ausgewaehlte Stations-Evidenz" if st.session_state.lang == "de" else "Selected Station Evidence"
        if selected_count == 1:
            evidence_title = f"{evidence_title_base}: {identity_labels[0]} | {evidence_count} {evidence_basis}"
        else:
            evidence_title = f"{evidence_title_base}: {selected_count} stations | {evidence_count} {evidence_basis}"
        time_agg_options, time_agg_default = _time_agg_options_for_span(evidence_df)
        folded_date_template = t.get(
            "fig_segment_dates_folded",
            "{count} UTC dates folded",
        ).replace("{count}", "{utc_date_count}")
        base_recipe = _selected_evidence_export_recipe(
            evidence_df,
            evidence_title,
            labels,
            time_agg_default,
            is_compare,
            is_sequential,
            folded_title=_folded_utc_hour_panel_title(t),
            folded_date_annotation=folded_date_template,
            folded_x_label=t.get(
                "fig_segment_utc_hour_x",
                "UTC hour",
            ),
            density_label=labels.get("density_label"),
            folded_unavailable_text=t.get(
                "fig_segment_folded_unavailable",
                "UTC-hour pattern unavailable - requires joint evidence from at least 2 UTC dates.",
            ),
            median_focus_axis_label=t.get(
                "fig_compare_median_focus_axis",
                "\u0394 SNR (dB \u00b7 median-centered nonlinear)",
            ),
        )
        if base_recipe["utc_date_count"] < 2:
            insufficient_date_label = t.get(
                "fig_segment_dates_insufficient",
                "{count} UTC dates available; folding unavailable",
            ).format(count=base_recipe["utc_date_count"])
            base_recipe["folded_date_annotation"] = insufficient_date_label
        selected_bundle = {
            "base_recipe": base_recipe,
            "time_agg_options": tuple(time_agg_options),
            "time_agg_default": time_agg_default,
            "title": evidence_title,
            "identity_labels": tuple(identity_labels),
            "evidence_count": int(evidence_count),
        }
        _inspector_cache_put(
            run_id,
            "selected",
            cache_key,
            selected_bundle,
        )

    identity_labels = list(selected_bundle["identity_labels"])
    evidence_count = int(selected_bundle["evidence_count"])
    st.markdown(
        evidence_level_header_html(
            4,
            t.get("lbl_results_level_selection", "Selected stations"),
            t.get(
                "hdr_results_selected_station_evidence",
                "Selected Station Evidence",
            ),
            selected_station_context(
                identity_labels,
                evidence_count,
                analysis_id=analysis_id,
                is_compare=is_compare,
                is_sequential=is_sequential,
                translations=t,
            ),
        ),
        unsafe_allow_html=True,
    )

    time_agg_options = list(selected_bundle["time_agg_options"])
    time_agg_default = selected_bundle["time_agg_default"]
    agg_key = (
        f"evidence_time_agg_{analysis_id}_{run_id}_{scope_token}_"
        f"{is_compare}_{is_sequential}"
    )
    persistent_time_bin_key = _time_bin_persistent_state_key(is_compare)
    _initialize_time_bin_widget_state(
        agg_key,
        persistent_time_bin_key,
        time_agg_options,
        time_agg_default,
    )

    temporal_view = SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL
    if is_compare:
        temporal_view_options = (
            SELECTED_TEMPORAL_VIEW_UTC_HOUR,
            SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL,
        )
        temporal_view_labels = {
            SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL: t.get(
                "opt_temporal_chronological",
                "Chronological",
            ),
            SELECTED_TEMPORAL_VIEW_UTC_HOUR: t.get(
                "opt_temporal_utc_hour",
                "UTC-Hour",
            ),
        }
        temporal_view_key = (
            f"evidence_temporal_view_{analysis_id}_{run_id}_{scope_token}_"
            f"{is_sequential}"
        )
        temporal_view = _initialize_choice_widget_state(
            temporal_view_key,
            RESULTS_STATION_TEMPORAL_VIEW_COMPARE_STATE_KEY,
            temporal_view_options,
            SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL,
        )
        view_control, detail_control = st.columns(
            SELECTED_TEMPORAL_CONTROL_COLUMN_WIDTHS,
            vertical_alignment="center",
        )
        with view_control:
            if hasattr(st, "segmented_control"):
                temporal_view = st.segmented_control(
                    t.get("lbl_selected_temporal_view", "Temporal view"),
                    temporal_view_options,
                    required=True,
                    format_func=temporal_view_labels.__getitem__,
                    key=temporal_view_key,
                    label_visibility="collapsed",
                    width="stretch",
                    on_change=_sync_choice_widget_state,
                    args=(
                        temporal_view_key,
                        RESULTS_STATION_TEMPORAL_VIEW_COMPARE_STATE_KEY,
                        temporal_view_options,
                        SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL,
                    ),
                )
            else:
                temporal_view = st.radio(
                    t.get("lbl_selected_temporal_view", "Temporal view"),
                    temporal_view_options,
                    format_func=temporal_view_labels.__getitem__,
                    horizontal=True,
                    key=temporal_view_key,
                    label_visibility="collapsed",
                    on_change=_sync_choice_widget_state,
                    args=(
                        temporal_view_key,
                        RESULTS_STATION_TEMPORAL_VIEW_COMPARE_STATE_KEY,
                        temporal_view_options,
                        SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL,
                    ),
                )
        temporal_view = _sync_choice_widget_state(
            temporal_view_key,
            RESULTS_STATION_TEMPORAL_VIEW_COMPARE_STATE_KEY,
            temporal_view_options,
            SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL,
        )
        with detail_control:
            if temporal_view == SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL:
                _render_stretched_time_bin_control(
                    t.get(
                        "lbl_chronological_bin_size",
                        "Chronological bin size",
                    ),
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
    else:
        control_spacer, time_control, control_margin = st.columns([1, 2, 0.05])
        with time_control:
            if hasattr(st, "segmented_control"):
                st.segmented_control(
                    "Time aggregation",
                    time_agg_options,
                    key=agg_key,
                    label_visibility="collapsed",
                    on_change=_sync_time_bin_widget_state,
                    args=(
                        agg_key,
                        persistent_time_bin_key,
                        tuple(time_agg_options),
                        time_agg_default,
                    ),
                )
            else:
                st.radio(
                    "Time aggregation",
                    time_agg_options,
                    horizontal=True,
                    key=agg_key,
                    label_visibility="collapsed",
                    on_change=_sync_time_bin_widget_state,
                    args=(
                        agg_key,
                        persistent_time_bin_key,
                        tuple(time_agg_options),
                        time_agg_default,
                    ),
                )

    if is_compare and temporal_view == SELECTED_TEMPORAL_VIEW_UTC_HOUR:
        time_agg = "1h"
    else:
        time_agg = _sync_time_bin_widget_state(
            agg_key,
            persistent_time_bin_key,
            time_agg_options,
            time_agg_default,
        )

    evidence_title = selected_bundle["title"]
    selected_recipe = dict(selected_bundle["base_recipe"])
    selected_recipe["time_bin"] = time_agg
    selected_recipe["temporal_view"] = temporal_view
    _render_cached_recipe(
        selected_recipe,
        run_id=run_id,
        cache_key=cache_key + (time_agg, temporal_view),
        subject="selected evidence",
        build_label="selected evidence figure build",
        render_figure=render_selected_evidence_export_figure,
        timing_collector=timing_collector,
    )
    return {
        "export_recipe": selected_recipe,
        "time_bin": time_agg,
        "temporal_view": temporal_view,
        "title": evidence_title,
    }


def _render_segment_temporal_evidence(
    temporal_bundle,
    *,
    analysis_id,
    run_id,
    scope_token,
    cache_key,
    t,
    timing_collector=None,
):
    """Render one segment-scoped Compare timeline with a saved bin selector."""
    if not temporal_bundle:
        return None

    st.markdown(
        evidence_child_header_html(
            t.get("hdr_results_temporal_evidence", "Temporal Evidence"),
            t.get(
                "sub_results_temporal_evidence",
                "The same paired evidence shown chronologically and by UTC hour.",
            ),
        ),
        unsafe_allow_html=True,
    )

    time_bin_options = list(temporal_bundle["time_bin_options"])
    time_bin_default = temporal_bundle["time_bin_default"]
    widget_key = f"segment_evidence_time_agg_{analysis_id}_{run_id}_{scope_token}"
    selected_time_bin = _initialize_time_bin_widget_state(
        widget_key,
        RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY,
        time_bin_options,
        time_bin_default,
    )

    _render_labeled_segment_time_bin_control(
        t.get(
            "lbl_time_aggregation_bin_size",
            "Time aggregation bin size:",
        ),
        time_bin_options,
        widget_key,
        on_change=_sync_time_bin_widget_state,
        on_change_args=(
            widget_key,
            RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY,
            tuple(time_bin_options),
            time_bin_default,
        ),
    )

    selected_time_bin = _sync_time_bin_widget_state(
        widget_key,
        RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY,
        time_bin_options,
        time_bin_default,
    )
    temporal_recipe = dict(temporal_bundle["base_recipe"])
    temporal_recipe["time_bin"] = selected_time_bin
    temporal_recipe["chronological_title"] = temporal_bundle[
        "chronological_title_template"
    ].format(time_bin=selected_time_bin)
    _render_cached_recipe(
        temporal_recipe,
        run_id=run_id,
        cache_key=cache_key + ("segment temporal", selected_time_bin),
        subject="segment temporal evidence",
        build_label="segment temporal evidence figure build",
        render_figure=render_segment_temporal_evidence_export_figure,
        timing_collector=timing_collector,
    )
    return {
        "export_recipe": temporal_recipe,
        "time_bin": selected_time_bin,
    }






















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
    """Render the opportunity-specific Absolute inspector and export state."""
    opportunity_terms = presentation_context.absolute_terms(
        "TX" if analysis_id.startswith("TX") else "RX"
    )

    segment_cache_key = (
        INSPECTOR_CACHE_VERSION,
        "opportunity",
        analysis_id,
        tuple(selected_ranges),
        tuple(selected_directions),
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
            st.warning("Cache file expired. Please Run Analysis again.")
            return
        except (KeyError, ValueError) as exc:
            _log_artifact_read_failure(
                exc,
                parquet_path=parquet_path,
                analysis_id=analysis_id,
                run_id=run_id,
                stage="opportunity segment read",
            )
            st.error("Analysis evidence could not be read because its schema is invalid.")
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

            opportunity_view_model = build_opportunity_inspector_view_model(
                df_seg,
                rows,
                analysis_id=analysis_id,
                minimum_confirmed=analysis_context.min_confirmed_opportunities_per_peer,
                presentation_context=presentation_context,
            )

        segment_recipe = _opportunity_segment_recipe(
            title,
            selected_seg,
            df_seg,
            rows,
            analysis_start_t,
            analysis_end_t,
            opportunity_terms,
            minimum_trials=analysis_context.min_confirmed_opportunities_per_peer,
        )
        opportunity_display_model = {
            "summary_lines": list(opportunity_view_model.summary_lines),
            "confirmed_station_count": int(
                opportunity_view_model.confirmed_station_count
            ),
            "confirmed_opportunity_count": int(
                opportunity_view_model.confirmed_opportunity_count
            ),
            "full_station_table": opportunity_view_model.full_station_table,
            "station_column": opportunity_view_model.station_column,
            "locator_column": opportunity_view_model.locator_column,
            "distance_column": opportunity_view_model.distance_column,
            "azimuth_column": opportunity_view_model.azimuth_column,
            "hit_column": opportunity_view_model.hit_column,
        }
        segment_bundle = {
            "display_model": opportunity_display_model,
            "figure_recipe": segment_recipe,
            "analysis_start_t": analysis_start_t,
            "analysis_end_t": analysis_end_t,
        }
        _inspector_cache_put(
            run_id,
            "segment",
            segment_cache_key,
            segment_bundle,
        )

    opportunity_display_model = segment_bundle["display_model"]
    segment_recipe = segment_bundle["figure_recipe"]
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

    with level_two_container:
        st.markdown(
            evidence_child_header_html(
                t.get(
                    "hdr_results_success_temporal",
                    "Success & Temporal Evidence",
                ),
                t.get(
                    "sub_results_success_temporal",
                    "Evidence depth, station-balanced and observation-level "
                    "Success Rate, and time pattern for the active scope.",
                ),
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='text-align:center; color:white; font-size:0.95rem; "
            f"margin-top:-0.25rem; margin-bottom:1.0rem;'>{'<br>'.join(summary)}</div>",
            unsafe_allow_html=True,
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

    disp_df = full_segment_disp_df.copy()
    if not show_zero_hits:
        disp_df = disp_df[disp_df[hit_col] > 0].reset_index(drop=True)
    selection_universe_df = disp_df.copy()

    level_three_container = st.container(
        key=(
            f"results_evidence_level_3_"
            f"{analysis_id}_{run_id}_{scope_token}"
        )
    )
    station_type = remote_station_type(analysis_id)
    level_three_container.markdown(
        evidence_level_header_html(
            3,
            t.get("lbl_results_level_stations", "Contributing stations"),
            t.get("lbl_insights", "Station Insights"),
            t.get(
                "sub_results_station_insights",
                "Contributing {station_type} stations in the active scope. "
                "Select one or more rows to inspect their evidence.",
            ).format(station_type=station_type),
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

    col_title, col_toggle, col_filter = level_three_container.columns(
        [0.56, 0.26, 0.18],
        vertical_alignment="center",
    )
    with col_title:
        sub_text = opportunity_terms["subtext"]
        st.markdown(
            scope_context_html(sub_text.strip(" ()")),
            unsafe_allow_html=True,
        )
    with col_toggle:
        show_zero_hits = st.toggle(
            t.get("lbl_show_zero_hits", "Show Zero-Target"),
            key=zero_hits_key,
            on_change=_sync_boolean_widget_state,
            args=(zero_hits_key, RESULTS_SHOW_ZERO_TARGET_STATE_KEY),
        )
        show_zero_hits = _sync_boolean_widget_state(
            zero_hits_key,
            RESULTS_SHOW_ZERO_TARGET_STATE_KEY,
        )

    disp_df = full_segment_disp_df.copy()
    if not show_zero_hits:
        disp_df = disp_df[disp_df[hit_col] > 0].reset_index(drop=True)
    selection_universe_df = disp_df.copy()

    with col_filter:
        with st.popover("Filter", icon=":material/filter_alt:", width="stretch"):
            filter_cols = st.multiselect(
                "Select Columns",
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
        "selection_mode": "multi-row",
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
        table_event = level_three_container.dataframe(
            disp_df,
            **dataframe_kwargs,
        )

    selected_station_labels = []
    selected_evidence_recipe = None
    selected_time_bin = None
    drilldown_selected_df = pd.DataFrame()
    selected_rows = [row for row in (table_event.selection.rows or []) if 0 <= row < len(disp_df)]
    _sync_selected_station_state_if_changed(
        selection_changed_key,
        RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY,
        disp_df,
        selected_rows,
        station_col,
        loc_col,
        selection_universe_df,
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

        confirmed_opportunity_count = int(
            pd.to_numeric(
                selected_station_rows.get("hit", pd.Series(dtype=float)),
                errors="coerce",
            ).fillna(0).sum()
            + pd.to_numeric(
                selected_station_rows.get("miss", pd.Series(dtype=float)),
                errors="coerce",
            ).fillna(0).sum()
        )
        level_four_container = st.container(
            key=(
                f"results_evidence_level_4_"
                f"{analysis_id}_{run_id}_{scope_token}"
            )
        )
        level_four_container.markdown(
            evidence_level_header_html(
                4,
                t.get("lbl_results_level_selection", "Selected stations"),
                t.get(
                    "hdr_results_selected_station_evidence",
                    "Selected Station Evidence",
                ),
                selected_station_context(
                    selected_station_labels,
                    confirmed_opportunity_count,
                    analysis_id=analysis_id,
                    is_compare=False,
                    is_sequential=False,
                    translations=t,
                ),
            ),
            unsafe_allow_html=True,
        )

        time_options, time_default = _time_agg_options_for_span(pd.DataFrame({
            "plot_time": [
                _as_utc_timestamp(analysis_start_t),
                _as_utc_timestamp(analysis_end_t),
            ],
        }))
        selected_time_key = f"opp_time_agg_{analysis_id}_{run_id}_{scope_token}"
        persistent_time_bin_key = RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY
        _initialize_time_bin_widget_state(
            selected_time_key,
            persistent_time_bin_key,
            time_options,
            time_default,
        )
        with level_four_container:
            _render_stretched_time_bin_control(
                "Time aggregation",
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
        evidence_title = (
            f"Selected Station Evidence: {selected_station_labels[0]}"
            if len(selected_station_labels) == 1
            else f"Selected Station Evidence: {len(selected_station_labels)} stations"
        )
        selected_cache_key = (
            INSPECTOR_CACHE_VERSION,
            "opportunity",
            analysis_id,
            scope_token,
            tuple(
                selected_identity[["peer_sign", "peer_grid"]]
                .astype(str)
                .itertuples(index=False, name=None)
            ),
            selected_time_bin,
            str(analysis_start_t),
            str(analysis_end_t),
            presentation_context.language,
            presentation_context.theme,
        )
        selected_evidence_recipe, selected_cache_hit = _inspector_cache_get(
            run_id,
            "selected",
            selected_cache_key,
            timing_collector,
            item="opportunity selected model",
        )
        if not selected_cache_hit:
            with _timed_span(timing_collector, "opportunity selected evidence prep"):
                selected_evidence_recipe = _opportunity_selected_recipe(
                    selected_station_rows,
                    evidence_title,
                    selected_time_bin,
                    analysis_start_t,
                    analysis_end_t,
                    opportunity_terms,
                )
            _inspector_cache_put(
                run_id,
                "selected",
                selected_cache_key,
                selected_evidence_recipe,
            )
        with level_four_container:
            _render_cached_recipe(
                selected_evidence_recipe,
                run_id=run_id,
                cache_key=selected_cache_key,
                subject="opportunity selected",
                build_label="opportunity selected figure build",
                render_figure=_render_opportunity_selected_figure,
                timing_collector=timing_collector,
            )
        level_four_container.markdown(
            transition_prompt_html(
                t.get(
                    "txt_results_transition_rows",
                    "Review the underlying evidence rows",
                )
            ),
            unsafe_allow_html=True,
        )

        with _timed_span(timing_collector, "drilldown table build"):
            drill_df, info_msg = _build_drilldown_table(
                parquet_path,
                selected_meta_df,
                station_col,
                loc_col,
                km_col,
                az_col,
                analysis_id,
                False,
                False,
                False,
                False,
                analysis_context.callsign.upper(),
                "",
                t,
                station_rows_df=selected_station_rows,
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
                    timing_collector=timing_collector,
                )
    else:
        level_three_container.markdown(
            transition_prompt_html(
                t.get(
                    "txt_results_transition_stations",
                    "Select one or more stations to inspect their evidence",
                )
            ),
            unsafe_allow_html=True,
        )

    full_meta_df = full_segment_disp_df[[station_col, loc_col, km_col, az_col]].copy()
    all_drilldown_context = {
        "station_meta_df": full_meta_df,
        "station_col": station_col,
        "loc_col": loc_col,
        "km_col": km_col,
        "az_col": az_col,
        "analysis_id": analysis_id,
        "is_compare": False,
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
        analysis_id=analysis_id,
        selected_segment=selected_seg,
        selected_distance=range_summary,
        selected_direction=direction_summary,
        selected_ranges=list(selected_ranges),
        selected_directions=list(selected_directions),
        show_non_joint=False,
        show_zero_target=show_zero_hits,
        evidence_time_bin=selected_time_bin,
        selected_stations=selected_station_labels,
        segment_figure_recipe=segment_recipe,
        selected_evidence_figure_recipe=selected_evidence_recipe,
        station_insights_df=disp_df,
        drilldown_selected_df=drilldown_selected_df,
        all_drilldown_context=all_drilldown_context,
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
    segs_df,
    parquet_path,
    line1_str,
    t,
    max_peer_distance_km,
    analysis_context,
    presentation_context,
    analysis_start_t=None,
    analysis_end_t=None,
    analysis_kind="comparison",
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
            segs_df,
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
    return result


def _render_segment_inspector_body(
    analysis_id,
    title,
    is_compare,
    is_sequential,
    enriched_df,
    segs_df,
    parquet_path,
    line1_str,
    t,
    max_peer_distance_km,
    analysis_context,
    presentation_context,
    analysis_start_t=None,
    analysis_end_t=None,
    analysis_kind="comparison",
    show_export_button=False,
    timing_collector=None,
):
    """
    Renders the interactive Segment Inspector directly below the map.
    Allows drill-down into specific Azimuth/Distance chunks to show histograms and tabular data.
    Runs as an independent Streamlit fragment to prevent full-page reruns on interaction.
    """
    run_id = st.session_state.get("run_id", 0)
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
    
    # Extract inspectable distance segments from enriched_df, not only rendered heatmap segments.
    # segs_df only contains segments with valid joint Delta-SNR heatmap data; enriched_df also
    # contains non-joint evidence such as only target, only reference, or async-both rows.
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
    inspector_source_df = options_view_model.source_rows
    valid_distances = options_view_model.valid_distances
    level_two_container = st.container(
        key=f"results_evidence_level_2_{analysis_id}_{run_id}"
    )
    level_two_container.markdown(
        evidence_level_header_html(
            2,
            t.get("lbl_results_level_scope", "Geographic scope"),
            t.get("hdr_results_segment_inspector", "Segment Inspector"),
            t.get(
                "sub_results_segment_inspector",
                "Choose one or more distance ranges and directions. "
                "All evidence below follows the active scope.",
            ),
        ),
        unsafe_allow_html=True,
    )

    lbl_dist = t.get("lbl_results_distance_range", "Distance range")
    lbl_dir = t.get("lbl_results_direction", "Direction")
    opt_full = t.get("opt_full_range", "Full Range")
    opt_all_dir = t.get("opt_all_dirs", "All Directions")

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
        st.session_state.lang,
    )
    direction_summary = _selection_summary(
        selected_directions,
        opt_all_dir,
        "direction",
        st.session_state.lang,
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

    # If inspectable options exist, process the selected Cartesian scope.
    if valid_distances and valid_dirs:
        with _timed_span(timing_collector, "segment scope filter"):
            df_seg = filter_inspector_scope(
                inspector_source_df,
                selected_ranges=selected_ranges,
                selected_directions=selected_directions,
            )

        if df_seg.empty:
            empty_scope_message = (
                "Keine Stationen im ausgewaehlten Bereich."
                if st.session_state.lang == "de"
                else "No stations in the selected scope."
            )
            st.info(empty_scope_message, icon=":material/info:")
            register_inspector_export(
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

        if analysis_kind == "opportunity":
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
            
        has_joint_rows, has_non_joint_rows = compare_scope_availability(
            df_seg,
            is_compare=is_compare,
        )
        toggle_key = f"tgl_{analysis_id}_{run_id}_{scope_token}"
        default_state = has_non_joint_rows and not has_joint_rows
        show_non_joint = (
            _initialize_boolean_widget_state(
                toggle_key,
                RESULTS_SHOW_NON_JOINT_STATE_KEY,
                default_state,
            )
            if is_compare
            else False
        )

        segment_cache_key = (
            INSPECTOR_CACHE_VERSION,
            "comparison",
            analysis_id,
            tuple(selected_ranges),
            tuple(selected_directions),
            bool(is_compare),
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
                is_compare=is_compare,
                is_sequential=is_sequential,
                show_non_joint=True,
                analysis_context=analysis_context,
                presentation_context=presentation_context,
            )
            vals = compare_view_model.values
            col_u_name = compare_view_model.target_name
            yield_ref_header = compare_view_model.yield_reference_header
            evidence_meta_df = compare_view_model.evidence_identities
            has_plot_data = compare_view_model.has_plot_data
            segment_figure_recipe = None
            segment_temporal_bundle = None
            segment_summary = []
            segment_station_count = 0
            segment_evidence_count = 0

            if has_plot_data:
                with _timed_span(timing_collector, "segment evidence points build"):
                    segment_evidence_df = _build_segment_evidence_points(
                        evidence_meta_df,
                        parquet_path,
                        is_compare,
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
                segment_raw_values = (
                    segment_evidence_df["metric"]
                    if not segment_evidence_df.empty
                    else pd.Series(dtype=float)
                )
                segment_station_count = len(vals)
                segment_evidence_count = len(segment_raw_values)
                compare_layout = is_compare and "count_only_u" in df_seg.columns
                if compare_layout:
                    cnt_joint = len(df_seg[df_seg["spot_count"] > 0])
                    cnt_async = len(df_seg[(df_seg["spot_count"] == 0) & (df_seg["count_only_u"] > 0) & (df_seg["count_only_r"] > 0)])
                    cnt_u = len(df_seg[(df_seg["spot_count"] == 0) & (df_seg["count_only_u"] > 0) & (df_seg["count_only_r"] == 0)])
                    cnt_r = len(df_seg[(df_seg["spot_count"] == 0) & (df_seg["count_only_u"] == 0) & (df_seg["count_only_r"] > 0)])
                    joint_lbl = (
                        t.get("tbl_col_joint_pairs", "Joint Pairs")
                        if is_sequential
                        else t.get("tbl_col_joint", "Joint")
                    )
                    async_lbl = t.get("leg_both_async", "Both (Async)")
                    segment_panel_counts = [cnt_u, cnt_joint, cnt_async, cnt_r]
                    segment_panel_labels = [col_u_name, joint_lbl, async_lbl, yield_ref_header]
                    segment_panel_y_label = t["lbl_hist_count"]
                else:
                    segment_panel_counts = [len(df_seg), int(df_seg["spot_count"].sum())]
                    segment_panel_labels = ["Stations", "Spots"]
                    segment_panel_y_label = "Count"

                segment_figure_recipe = _segment_figure_export_recipe(
                    title=title,
                    selected_segment=selected_seg,
                    is_compare=is_compare,
                    is_sequential=is_sequential,
                    compare_layout=compare_layout,
                    station_values=vals,
                    spot_values=segment_raw_values,
                    panel_counts=segment_panel_counts,
                    panel_labels=segment_panel_labels,
                    panel_y_label=segment_panel_y_label,
                    paired_evidence_title=(
                        t.get(
                            "fig_scheduled_pair_delta",
                            "Scheduled-Pair \u0394 SNR",
                        )
                        if is_sequential
                        else None
                    ),
                )
                if is_compare and not segment_evidence_df.empty:
                    if is_sequential:
                        temporal_count_label = t.get(
                            "fig_scheduled_pair_count",
                            "Scheduled pair count",
                        )
                        temporal_density_label = t.get(
                            "fig_relative_scheduled_pair_density",
                            "Relative scheduled-pair density (% of panel maximum)",
                        )
                    else:
                        temporal_count_label = t.get(
                            "fig_joint_spot_count",
                            "Joint spot count",
                        )
                        temporal_density_label = t.get(
                            "fig_relative_joint_spot_density",
                            "Relative joint-spot density (% of panel maximum)",
                        )

                    temporal_time_options, temporal_time_default = (
                        _time_agg_options_for_span(segment_evidence_df)
                    )
                    chronological_title_label = t.get(
                        "fig_segment_chronological_delta",
                        "\u0394 SNR over Time",
                    )
                    chronological_title_template = (
                        f"{chronological_title_label} ({{time_bin}} bins)"
                    )
                    folded_date_template = t.get(
                        "fig_segment_dates_folded",
                        "{count} UTC dates folded",
                    ).replace("{count}", "{utc_date_count}")
                    temporal_figure_title = _segment_temporal_figure_title(
                        title,
                        analysis_id,
                        selected_seg,
                        t,
                    )
                    temporal_base_recipe = _segment_temporal_evidence_export_recipe(
                        segment_evidence_df,
                        temporal_figure_title,
                        temporal_time_default,
                        temporal_count_label,
                        chronological_title=chronological_title_template,
                        chronological_x_label=t.get(
                            "fig_segment_chronological_x",
                            "Date/Time (UTC)",
                        ),
                        folded_title=_folded_utc_hour_panel_title(t),
                        folded_date_annotation=folded_date_template,
                        folded_x_label=t.get(
                            "fig_segment_utc_hour_x",
                            "UTC hour",
                        ),
                        density_label=temporal_density_label,
                        folded_unavailable_text=t.get(
                            "fig_segment_folded_unavailable",
                            "UTC-hour pattern unavailable - requires joint evidence from at least 2 UTC dates.",
                        ),
                        median_focus_axis_label=t.get(
                            "fig_compare_median_focus_axis",
                            "\u0394 SNR (dB \u00b7 median-centered nonlinear)",
                        ),
                        median_label=t.get(
                            "fig_median_label",
                            "Median",
                        ),
                        bin_median_label=t.get(
                            "fig_temporal_bin_median",
                            "Bin median",
                        ),
                    )
                    if temporal_base_recipe["utc_date_count"] < 2:
                        insufficient_date_label = t.get(
                            "fig_segment_dates_insufficient",
                            "{count} UTC dates available; folding unavailable",
                        ).format(count=temporal_base_recipe["utc_date_count"])
                        temporal_base_recipe[
                            "folded_date_annotation"
                        ] = insufficient_date_label
                    segment_temporal_bundle = {
                        "base_recipe": temporal_base_recipe,
                        "time_bin_options": tuple(temporal_time_options),
                        "time_bin_default": temporal_time_default,
                        "chronological_title_template": chronological_title_template,
                    }
                if is_compare:
                    station_summary = _compare_metric_distribution_summary(
                        segment_figure_recipe["station_values"],
                        t.get(
                            "fmt_results_station_delta_summary",
                            "Station-level · Median {median} dB · "
                            "Mean {mean} dB",
                        ),
                    )
                    observation_summary_key = (
                        "fmt_results_scheduled_pair_delta_summary"
                        if is_sequential
                        else "fmt_results_joint_spot_delta_summary"
                    )
                    observation_summary_fallback = (
                        "Scheduled-Pair level · Median {median} dB · "
                        "Mean {mean} dB"
                        if is_sequential
                        else "Joint-Spot level · Median {median} dB · "
                        "Mean {mean} dB"
                    )
                    spot_summary = _compare_metric_distribution_summary(
                        segment_figure_recipe["spot_values"],
                        t.get(
                            observation_summary_key,
                            observation_summary_fallback,
                        ),
                    )
                else:
                    station_summary = _metric_median_summary(
                        vals,
                        False,
                        "Station-median",
                    )
                    spot_summary = _metric_median_summary(
                        segment_raw_values,
                        False,
                        "Spot",
                    )
                segment_summary = _segment_summary_lines(
                    station_summary=station_summary,
                    spot_summary=spot_summary,
                )

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

        disp_df = compare_view_model.station_table.copy()
        if is_compare and not show_non_joint and col_joint_name in disp_df.columns:
            disp_df = disp_df[disp_df[col_joint_name] > 0].reset_index(drop=True)
        sorted_disp_df = disp_df.copy()
        full_segment_disp_df = compare_view_model.full_station_table
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
                    is_compare=is_compare,
                    is_sequential=is_sequential,
                    translations=t,
                ),
            ),
            unsafe_allow_html=True,
        )

        with level_two_container:
            st.markdown(
                evidence_child_header_html(
                    t.get(
                        "hdr_results_comparison_evidence",
                        "Comparison Evidence",
                    ),
                    t.get(
                        comparison_subtitle_key,
                        "Decode Outcomes, station medians, and paired ΔSNR "
                        "for the active scope.",
                    ),
                ),
                unsafe_allow_html=True,
            )

            if has_plot_data:
                if segment_summary:
                    st.markdown(
                        "<div style='text-align:center; color:white; "
                        "font-size:0.95rem; margin-top:-0.25rem; "
                        f"margin-bottom:1.0rem;'>{'<br>'.join(segment_summary)}</div>",
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
                    timing_collector=timing_collector,
                )
            else:
                no_joint_message = (
                    t.get(
                        "lbl_no_joint_pairs",
                        "No joint scheduled pairs are available in this segment.",
                    )
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

        selection_universe_df = sorted_disp_df.copy()
        level_three_container = st.container(
            key=(
                f"results_evidence_level_3_"
                f"{analysis_id}_{run_id}_{scope_token}"
            )
        )
        station_type = remote_station_type(analysis_id)
        level_three_container.markdown(
            evidence_level_header_html(
                3,
                t.get("lbl_results_level_stations", "Contributing stations"),
                t.get("lbl_insights", "Station Insights"),
                t.get(
                    "sub_results_station_insights",
                    "Contributing {station_type} stations in the active scope. "
                    "Select one or more rows to inspect their evidence.",
                ).format(station_type=station_type),
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

        # --- 1. Define layout columns ---
        # Give localized toggle labels enough room while preserving the filter width.
        col_ins1, col_ins2, col_ins3 = level_three_container.columns(
            STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS,
            vertical_alignment="center",
        )
        
        with col_ins1:
            # Compact bilingual subtitle.
            sub_text = " (Norm. @ 1W. Details per Klick)" if st.session_state.lang == "de" else " (Norm. @ 1W. Click for details)"
            st.markdown(
                scope_context_html(sub_text.strip(" ()")),
                unsafe_allow_html=True,
            )
            
        with col_ins2:
            if is_compare:
                # Default to showing non-joint rows only when the selected segment has no joint
                # evidence but does contain target-only, reference-only, or async-both evidence.
                st.toggle(
                    t.get(
                        "lbl_include_unpaired_evidence",
                        "Include Unpaired Evidence",
                    ),
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
            with st.popover("Filter", icon=":material/filter_alt:", width="stretch"):
                st.markdown("**Filter column(s):**")
                filter_cols = st.multiselect("Select Columns", sorted_disp_df.columns, label_visibility="collapsed")
                
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
            _render_reference_correction_notice(t, is_compare)

        # Die Tabelle rendert nun den gefilterten Zustand
        tbl_key = f"tbl_{analysis_id}_{run_id}_{scope_token}"
        selected_stations_state_key = _selected_stations_persistent_state_key(
            is_compare
        )
        configured_station_identities = st.session_state.get(
            selected_stations_state_key
        )
        selection_changed_key = f"{tbl_key}_selection_changed"
        dataframe_kwargs = {
            "width": "stretch",
            "hide_index": True,
            "selection_mode": "multi-row",
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
            tbl_event = level_three_container.dataframe(
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
            "is_compare": bool(is_compare),
            "is_sequential": bool(is_sequential),
            "show_non_joint": bool(is_compare),
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
        # the first render; a deliberate deselect-all is persisted as an empty list.
        raw_sel_rows = tbl_event.selection.rows or []
        sel_rows = [row for row in raw_sel_rows if 0 <= row < len(sorted_disp_df)]
        _sync_selected_station_state_if_changed(
            selection_changed_key,
            selected_stations_state_key,
            sorted_disp_df,
            sel_rows,
            station_col,
            t['tbl_col_loc'],
            selection_universe_df,
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
            selected_station_labels = (
                selected_identity_df["peer_sign"].astype(str) +
                " (" + selected_identity_df["peer_grid"].astype(str) + ")"
            ).tolist()
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
                        is_compare,
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
                            tuple(
                                selected_identity_df[["peer_sign", "peer_grid"]]
                                .astype(str)
                                .itertuples(index=False, name=None)
                            ),
                            bool(is_compare),
                            bool(is_sequential),
                            int(analysis_context.tx_ab_repeat_interval_minutes),
                            int(analysis_context.tx_ab_target_start_minute),
                            int(analysis_context.tx_ab_reference_start_minute),
                            presentation_context.language,
                            presentation_context.theme,
                        ),
                        timing_collector=timing_collector,
                    )
                level_four_container.markdown(
                    transition_prompt_html(
                        t.get(
                            "txt_results_transition_rows",
                            "Review the underlying evidence rows",
                        )
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
                        is_compare,
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
                            is_compare,
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
                    "Cache file expired. Please Run Analysis again."
                )
        else:
            level_three_container.markdown(
                transition_prompt_html(
                    t.get(
                        "txt_results_transition_stations",
                        "Select one or more stations to inspect their evidence",
                    )
                ),
                unsafe_allow_html=True,
            )

        register_inspector_export(
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
            selected_evidence_figure_recipe=(selected_evidence_export or {}).get("export_recipe"),
            station_insights_df=sorted_disp_df,
            drilldown_selected_df=drilldown_selected_df,
            all_drilldown_context=all_drilldown_context,
            reference_snr_header=f'{ref_header} SNR (dB)' if is_compare else None,
        )

        if show_export_button:
            render_download_all_results(t)
