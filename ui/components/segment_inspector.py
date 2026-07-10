"""
Segment Inspector & Results Components Module.
Contains the interactive drill-down UI (histograms, data tables) and 
compact recipes for lazy high-resolution result exports. Isolated as Streamlit fragments
to allow UI updates without triggering full-page reruns.
"""

import inspect
from collections import OrderedDict
from contextlib import nullcontext
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
)
from ui.matplotlib_renderer import (
    dispose_matplotlib_figure,
    get_matplotlib_render_mode,
    matplotlib_render_span_label,
    render_matplotlib_figure,
    render_matplotlib_image_bytes,
)
from ui.results_export import register_inspector_export, render_download_all_results
from core.stability import (
    _bootstrap_median_interval,
    _format_stability_interval,
    _stability_summary,
)
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
    _add_horizontal_grid,
    _segment_figure_export_recipe,
    _selected_evidence_export_recipe,
    _time_agg_options_for_span,
    render_segment_insight_export_figure,
    render_selected_evidence_export_figure,
)
from ui.plots.opportunity_figures import (
    _as_utc_timestamp,
    _opportunity_selected_recipe,
    _opportunity_segment_recipe,
    _render_opportunity_selected_figure,
    _render_opportunity_segment_figure,
)

STABILITY_CACHE_STATE_KEY = "segment_stability_cache"
STABILITY_CACHE_MAX_ENTRIES = 4
INSPECTOR_CACHE_VERSION = 1
INSPECTOR_PNG_RENDER_VERSION = 1
INSPECTOR_CACHE_NAMESPACE_LIMITS = {
    "options": INSPECTOR_CACHE_OPTIONS_MAX_ENTRIES,
    "segment": INSPECTOR_CACHE_SEGMENT_MAX_ENTRIES,
    "selected": INSPECTOR_CACHE_SELECTED_MAX_ENTRIES,
    "png": INSPECTOR_CACHE_PNG_MAX_ENTRIES,
}


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

def _initialize_explicit_all_multiselect(key, previous_key, all_option, specific_options):
    """Prepare stable list state before constructing an explicit-All multiselect."""
    current = st.session_state.get(key, [all_option])
    if isinstance(current, str):
        current = [current]
    previous = st.session_state.get(previous_key, [all_option])
    if isinstance(previous, str):
        previous = [previous]
    normalized = _resolve_explicit_all_selection(current, previous, all_option, specific_options)
    st.session_state[key] = normalized
    st.session_state[previous_key] = normalized

def _update_explicit_all_multiselect(key, previous_key, all_option, specific_options):
    """Apply explicit-All behavior after the user changes a multiselect."""
    current = st.session_state.get(key, [])
    previous = st.session_state.get(previous_key, [all_option])
    normalized = _resolve_explicit_all_selection(current, previous, all_option, specific_options)
    st.session_state[key] = normalized
    st.session_state[previous_key] = normalized

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




def _cached_segment_stability(cache_key, station_values, segment_evidence_df):
    """Return compact bootstrap results without repeating work on station-selection reruns."""
    cache = st.session_state.get(STABILITY_CACHE_STATE_KEY)
    if not isinstance(cache, OrderedDict):
        cache = OrderedDict()

    if cache_key in cache:
        result = cache.pop(cache_key)
        cache[cache_key] = result
        st.session_state[STABILITY_CACHE_STATE_KEY] = cache
        return result

    station_interval = _bootstrap_median_interval(station_values)
    spot_values = (
        segment_evidence_df["metric"]
        if isinstance(segment_evidence_df, pd.DataFrame) and not segment_evidence_df.empty
        else pd.Series(dtype=float)
    )
    spot_interval = _bootstrap_median_interval(spot_values)
    stability_lookup = {}
    if isinstance(segment_evidence_df, pd.DataFrame) and not segment_evidence_df.empty:
        for identity, group_df in segment_evidence_df.groupby("identity", observed=True):
            _, low, high = _bootstrap_median_interval(group_df["metric"])
            stability_lookup[str(identity)] = (float(low), float(high))

    result = {
        "station_interval": station_interval,
        "spot_interval": spot_interval,
        "station_lookup": stability_lookup,
    }
    cache[cache_key] = result
    while len(cache) > STABILITY_CACHE_MAX_ENTRIES:
        cache.popitem(last=False)
    st.session_state[STABILITY_CACHE_STATE_KEY] = cache
    return result

















def _section_header(label, icon=""):
    """Render a compact section header matching the Station Insights style."""
    if icon.startswith("material:"):
        icon_name = icon.split(":", 1)[1]
        icon_text = f"<span class='material-symbols-rounded section-icon'>{icon_name}</span>"
    else:
        icon_text = f"{icon} " if icon else ""
    st.markdown(f"**{icon_text}{label}**", unsafe_allow_html=True)

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

def _evidence_strength(stations_count, evidence_count):
    """Classify evidence strength using WSPRadar's heuristic sample thresholds."""
    if stations_count >= 5 and evidence_count >= 20:
        return "Strong"
    if stations_count >= 3 and evidence_count >= 10:
        return "Medium"
    if stations_count >= 1 and evidence_count >= 3:
        return "Low"
    return "Very low"

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


def _evidence_labels(is_compare):
    """Return UI labels for the selected-station evidence plots."""
    if st.session_state.get("lang") == "de":
        if is_compare:
            return {
                "dist_title": "\u0394 SNR Verteilung",
                "time_title": "\u0394 SNR ueber Zeit",
                "y_label": "\u0394 SNR (dB)",
                "x_label": "Datum/Uhrzeit (UTC)",
                "aggregate": "Selected Stations",
            }
        return {
            "dist_title": "Normiertes SNR Verteilung",
            "time_title": "Normiertes SNR ueber Zeit",
            "y_label": "Normiertes SNR (dB @ 1W)",
            "x_label": "Datum/Uhrzeit (UTC)",
            "aggregate": "Selected Stations",
        }

    if is_compare:
        return {
            "dist_title": "\u0394 SNR Distribution",
            "time_title": "\u0394 SNR over Time",
            "y_label": "\u0394 SNR (dB)",
            "x_label": "Date/Time (UTC)",
            "aggregate": "Selected Stations",
        }
    return {
        "dist_title": "Normalized SNR Distribution",
        "time_title": "Normalized SNR over Time",
        "y_label": "Normalized SNR (dB @ 1 W)",
        "x_label": "Date/Time (UTC)",
        "aggregate": "Selected Stations",
    }






















def _render_drilldown_dataframe(
    drill_df,
    drill_title,
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

    col_d1, col_d2 = st.columns([0.7, 0.3], vertical_alignment="center")

    with col_d1:
        _section_header(drill_title, "material:table_rows")

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
    tx_ab_bin_minutes,
    *,
    run_id,
    cache_key,
    timing_collector=None,
):
    """Render selected-station distribution and time evidence between insights and drill-down."""
    identity_meta = _prepare_identity_meta(selected_identity_df)
    if identity_meta.empty:
        return None

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
                tx_ab_bin_minutes=tx_ab_bin_minutes,
            )
        if evidence_df.empty:
            return None

        labels = _evidence_labels(is_compare)
        identity_labels = identity_meta["identity"].tolist()
        selected_count = len(identity_labels)
        evidence_count = len(evidence_df)
        evidence_basis = "paired spot bins" if is_sequential else ("joint spots" if is_compare else "spots")
        evidence_title_base = "Ausgewaehlte Stations-Evidenz" if st.session_state.lang == "de" else "Selected Station Evidence"
        if selected_count == 1:
            evidence_title = f"{evidence_title_base}: {identity_labels[0]} | {evidence_count} {evidence_basis}"
        else:
            evidence_title = f"{evidence_title_base}: {selected_count} stations | {evidence_count} {evidence_basis}"
        time_agg_options, time_agg_default = _time_agg_options_for_span(evidence_df)
        base_recipe = _selected_evidence_export_recipe(
            evidence_df,
            evidence_title,
            labels,
            time_agg_default,
            is_compare,
            is_sequential,
        )
        selected_bundle = {
            "base_recipe": base_recipe,
            "time_agg_options": tuple(time_agg_options),
            "time_agg_default": time_agg_default,
            "title": evidence_title,
        }
        _inspector_cache_put(
            run_id,
            "selected",
            cache_key,
            selected_bundle,
        )

    ctrl_left, ctrl_time, ctrl_right = st.columns([1, 2, 0.05])
    with ctrl_time:
        time_agg_options = list(selected_bundle["time_agg_options"])
        time_agg_default = selected_bundle["time_agg_default"]
        view_defaults = st.session_state.get("demo_view_defaults", {})
        preferred_time_agg = (
            view_defaults.get("station_evidence_time_bin_compare")
            if is_compare
            else view_defaults.get("station_evidence_time_bin_absolute")
        )
        if preferred_time_agg in time_agg_options:
            time_agg_default = preferred_time_agg
        agg_key = f"evidence_time_agg_{st.session_state.get('run_id', 0)}_{is_compare}_{is_sequential}"
        if st.session_state.get(agg_key) not in time_agg_options:
            st.session_state[agg_key] = time_agg_default
        if hasattr(st, "segmented_control"):
            time_agg = st.segmented_control(
                "Time aggregation",
                time_agg_options,
                key=agg_key,
                label_visibility="collapsed"
            )
        else:
            time_agg = st.radio(
                "Time aggregation",
                time_agg_options,
                horizontal=True,
                key=agg_key,
                label_visibility="collapsed"
            )

    evidence_title = selected_bundle["title"]
    selected_recipe = dict(selected_bundle["base_recipe"])
    selected_recipe["time_bin"] = time_agg
    st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
    _render_cached_recipe(
        selected_recipe,
        run_id=run_id,
        cache_key=cache_key + (time_agg,),
        subject="selected evidence",
        build_label="selected evidence figure build",
        render_figure=render_selected_evidence_export_figure,
        timing_collector=timing_collector,
    )
    return {
        "export_recipe": selected_recipe,
        "time_bin": time_agg,
        "title": evidence_title,
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
                selected_segment=selected_seg,
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
    st.markdown(
        f"<div style='text-align:center; color:white; font-size:0.95rem; margin-top:-0.25rem; margin-bottom:1.0rem;'>{'<br>'.join(summary)}</div>",
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
    col_title, col_toggle, col_filter = st.columns(
        [0.56, 0.26, 0.18],
        vertical_alignment="center",
    )
    with col_title:
        sub_text = opportunity_terms["subtext"]
        st.markdown(
            f"**<span class='material-symbols-rounded section-icon'>monitoring</span>{t['lbl_insights']}**"
            f"<span style='font-size:0.85em; color:gray;'>{sub_text}</span>",
            unsafe_allow_html=True,
        )
    with col_toggle:
        show_zero_hits = st.toggle(
            t.get("lbl_show_zero_hits", "Show Zero-Target"),
            value=False,
            key=zero_hits_key,
        )

    disp_df = full_segment_disp_df.copy()
    if not show_zero_hits:
        disp_df = disp_df[disp_df[hit_col] > 0].reset_index(drop=True)

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
    dataframe_kwargs = {
        "width": "stretch",
        "hide_index": True,
        "selection_mode": "multi-row",
        "on_select": "rerun",
        "key": table_key,
        "column_config": _snr_column_config(disp_df),
    }
    if not disp_df.empty and _supports_dataframe_selection_default():
        dataframe_kwargs["selection_default"] = {"selection": {"rows": [0]}}
    with _timed_span(timing_collector, "opportunity station table render"):
        table_event = st.dataframe(disp_df, **dataframe_kwargs)

    selected_station_labels = []
    selected_evidence_recipe = None
    selected_time_bin = None
    drilldown_selected_df = pd.DataFrame()
    selected_rows = [row for row in (table_event.selection.rows or []) if 0 <= row < len(disp_df)]

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

        time_options, time_default = _time_agg_options_for_span(pd.DataFrame({
            "plot_time": [
                _as_utc_timestamp(analysis_start_t),
                _as_utc_timestamp(analysis_end_t),
            ],
        }))
        selected_time_key = f"opp_time_agg_{analysis_id}_{run_id}_{scope_token}"
        if st.session_state.get(selected_time_key) not in time_options:
            st.session_state[selected_time_key] = time_default
        if hasattr(st, "segmented_control"):
            selected_time_bin = st.segmented_control(
                "Time aggregation",
                time_options,
                key=selected_time_key,
                label_visibility="collapsed",
            )
        else:
            selected_time_bin = st.radio(
                "Time aggregation",
                time_options,
                horizontal=True,
                key=selected_time_key,
                label_visibility="collapsed",
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
        _render_cached_recipe(
            selected_evidence_recipe,
            run_id=run_id,
            cache_key=selected_cache_key,
            subject="opportunity selected",
            build_label="opportunity selected figure build",
            render_figure=_render_opportunity_selected_figure,
            timing_collector=timing_collector,
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
                tx_ab_bin_minutes=analysis_context.tx_ab_bin_minutes,
                target_callsign=analysis_context.callsign,
            )
        if info_msg:
            st.info(info_msg, icon=":material/info:")
        elif not drill_df.empty:
            drill_title = (
                t["lbl_drill_single"].format(station=selected_station_labels[0])
                if len(selected_station_labels) == 1
                else t["lbl_drill_multi"].format(count=len(selected_station_labels))
            )
            drilldown_selected_df = _render_drilldown_dataframe(
                drill_df,
                drill_title,
                analysis_id,
                run_id,
                scope_token,
                t,
                False,
                timing_collector=timing_collector,
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
        "tx_ab_bin_minutes": analysis_context.tx_ab_bin_minutes,
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
    max_dist_km,
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
            max_dist_km,
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
    max_dist_km,
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
        float(max_dist_km),
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
            max_dist_km=max_dist_km,
        )
        _inspector_cache_put(
            run_id,
            "options",
            options_cache_key,
            options_view_model,
        )
    inspector_source_df = options_view_model.source_rows
    valid_distances = options_view_model.valid_distances
    lbl_dist = t.get("opt_insp_dist", "---")
    lbl_dir = t.get("opt_insp_dir", "---")
    opt_full = t.get("opt_full_range", "Full Range")
    opt_all_dir = t.get("opt_all_dirs", "All Directions")

    valid_dirs = options_view_model.valid_directions

    # Render stable explicit-All multiselects. The callback keeps All mutually
    # exclusive with specific values and restores All when the field is cleared.
    col_insp1, col_insp2 = st.columns(2)
    with col_insp1:
        dist_key = f"dist_multi_{analysis_id}_{run_id}"
        dist_previous_key = f"{dist_key}_previous"
        dist_options = [opt_full] + valid_distances
        _initialize_explicit_all_multiselect(
            dist_key,
            dist_previous_key,
            opt_full,
            valid_distances,
        )
        selected_distance_values = st.multiselect(
            lbl_dist,
            dist_options,
            key=dist_key,
            on_change=_update_explicit_all_multiselect,
            args=(dist_key, dist_previous_key, opt_full, valid_distances),
            label_visibility="collapsed",
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
        )
        selected_direction_values = st.multiselect(
            lbl_dir,
            dir_options,
            key=dir_key,
            on_change=_update_explicit_all_multiselect,
            args=(dir_key, dir_previous_key, opt_all_dir, valid_dirs),
            label_visibility="collapsed",
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

    range_token = "all" if not selected_ranges else "-".join(
        str(valid_distances.index(value)) for value in selected_ranges
    )
    direction_token = "all" if not selected_directions else "-".join(
        str(COMPASS.index(value)) for value in selected_directions
    )
    scope_token = f"r{range_token}_d{direction_token}"

    st.markdown("<div style='height:0.38rem;'></div>", unsafe_allow_html=True)

    # If inspectable options exist, process the selected Cartesian scope.
    if valid_distances and valid_dirs:
        segment_insight_label = "Segment-Insight" if st.session_state.lang == "de" else "Segment Insight"
        _section_header(segment_insight_label, "material:data_usage")
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
        view_defaults = st.session_state.get("demo_view_defaults", {})
        if "show_non_joint" in view_defaults and view_defaults.get("show_non_joint") is not None:
            default_state = bool(view_defaults.get("show_non_joint"))
        else:
            default_state = has_non_joint_rows and not has_joint_rows
        show_non_joint = st.session_state.get(toggle_key, default_state) if is_compare else False

        segment_cache_key = (
            INSPECTOR_CACHE_VERSION,
            "comparison",
            analysis_id,
            tuple(selected_ranges),
            tuple(selected_directions),
            bool(is_compare),
            bool(is_sequential),
            int(analysis_context.tx_ab_bin_minutes),
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
            stability_lookup = {}
            segment_figure_recipe = None
            segment_summary = []

            if has_plot_data:
                with _timed_span(timing_collector, "segment evidence points build"):
                    segment_evidence_df = _build_segment_evidence_points(
                        evidence_meta_df,
                        parquet_path,
                        is_compare,
                        is_sequential,
                        tx_ab_bin_minutes=analysis_context.tx_ab_bin_minutes,
                    )
                segment_raw_values = (
                    segment_evidence_df["metric"]
                    if not segment_evidence_df.empty
                    else pd.Series(dtype=float)
                )
                with _timed_span(timing_collector, "segment stability calculation"):
                    stability_result = _cached_segment_stability(
                        (run_id, analysis_id, selected_ranges, selected_directions),
                        vals,
                        segment_evidence_df,
                    )
                station_stability_interval = stability_result["station_interval"]
                spot_stability_interval = stability_result["spot_interval"]
                stability_lookup = stability_result["station_lookup"]
                compare_layout = is_compare and "count_only_u" in df_seg.columns
                if compare_layout:
                    cnt_joint = len(df_seg[df_seg["spot_count"] > 0])
                    cnt_async = len(df_seg[(df_seg["spot_count"] == 0) & (df_seg["count_only_u"] > 0) & (df_seg["count_only_r"] > 0)])
                    cnt_u = len(df_seg[(df_seg["spot_count"] == 0) & (df_seg["count_only_u"] > 0) & (df_seg["count_only_r"] == 0)])
                    cnt_r = len(df_seg[(df_seg["spot_count"] == 0) & (df_seg["count_only_u"] == 0) & (df_seg["count_only_r"] > 0)])
                    joint_lbl = t.get("tbl_col_joint_bins", "Joint Bins") if is_sequential else t.get("tbl_col_joint", "Joint")
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
                    station_interval=station_stability_interval,
                    spot_interval=spot_stability_interval,
                    panel_counts=segment_panel_counts,
                    panel_labels=segment_panel_labels,
                    panel_y_label=segment_panel_y_label,
                )
                segment_strength = _evidence_strength(len(vals), len(segment_raw_values))
                spot_basis = "paired spot bins" if is_sequential else ("joint spots" if is_compare else "spots")
                segment_summary = [
                    f"Selected Segment: {selected_seg}",
                    f"Selected Segment Evidence: {segment_strength} | {len(vals)} stations | {len(segment_raw_values)} {spot_basis}",
                ]
                station_summary = _stability_summary(
                    vals,
                    is_compare,
                    "Station-median",
                    interval=station_stability_interval,
                )
                spot_summary = _stability_summary(
                    segment_raw_values,
                    is_compare,
                    "Joint-spot" if is_compare and not is_sequential else ("Paired spot-bin" if is_sequential else "Spot"),
                    interval=spot_stability_interval,
                )
                if station_summary:
                    segment_summary.append(station_summary)
                if spot_summary:
                    segment_summary.append(spot_summary)

            segment_bundle = {
                "view_model": compare_view_model,
                "figure_recipe": segment_figure_recipe,
                "summary": segment_summary,
                "stability_lookup": stability_lookup,
            }
            _inspector_cache_put(
                run_id,
                "segment",
                segment_cache_key,
                segment_bundle,
            )

        compare_view_model = segment_bundle["view_model"]
        segment_figure_recipe = segment_bundle["figure_recipe"]
        segment_summary = segment_bundle["summary"]
        stability_lookup = segment_bundle["stability_lookup"]
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

        selected_evidence_export = None
        selected_station_labels = []
        drilldown_selected_df = pd.DataFrame()
        all_drilldown_context = None

        if has_plot_data:
            st.markdown(
                f"<div style='text-align:center; color:white; font-size:0.95rem; margin-top:-0.25rem; margin-bottom:1.0rem;'>{'<br>'.join(segment_summary)}</div>",
                unsafe_allow_html=True
            )

            st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
            _render_cached_recipe(
                segment_figure_recipe,
                run_id=run_id,
                cache_key=segment_cache_key,
                subject="segment insight",
                build_label="segment insight figure build",
                render_figure=render_segment_insight_export_figure,
                timing_collector=timing_collector,
            )
        else:
            st.info(t["lbl_no_joint"], icon="??????")
            st.markdown(f"<div style='font-size:11px; color:#ccc; margin-bottom:1rem; font-family:monospace;'>{line1_str}<br>{seg_line2}</div>", unsafe_allow_html=True)

        stability_col = t.get("tbl_col_stability", "90% Stability")
        if stability_lookup and not sorted_disp_df.empty:
            row_identity = (
                sorted_disp_df[station_col].astype(str) +
                " (" + sorted_disp_df[t['tbl_col_loc']].astype(str) + ")"
            )
            formatted_stability_lookup = {
                identity: _format_stability_interval(low, high, is_compare)
                for identity, (low, high) in stability_lookup.items()
            }
            sorted_disp_df[stability_col] = row_identity.map(formatted_stability_lookup).fillna("n/a")

        # --- 1. Define layout columns ---
        # Three columns: 50% for title, 30% for toggle, 20% for filter button.
        col_ins1, col_ins2, col_ins3 = st.columns([0.6, 0.3, 0.3], vertical_alignment="center")
        
        with col_ins1:
            # Compact bilingual subtitle.
            sub_text = " (Norm. @ 1W. Details per Klick)" if st.session_state.lang == "de" else " (Norm. @ 1W. Click for details)"
            st.markdown(f"**<span class='material-symbols-rounded section-icon'>monitoring</span>{t['lbl_insights']}**<span style='font-size:0.85em; color:gray;'>{sub_text}</span>", unsafe_allow_html=True)
            
        with col_ins2:
            if is_compare:
                # Default to showing non-joint rows only when the selected segment has no joint
                # evidence but does contain target-only, reference-only, or async-both evidence.
                show_non_joint = st.toggle("Show Non-Joint", value=default_state, key=toggle_key)

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

        _render_reference_correction_notice(t, is_compare)

        # Die Tabelle rendert nun den gefilterten Zustand
        tbl_key = f"tbl_{analysis_id}_{run_id}_{scope_token}"
        dataframe_kwargs = {
            "width": "stretch",
            "hide_index": True,
            "selection_mode": "multi-row",
            "on_select": "rerun",
            "key": tbl_key,
            "column_config": _snr_column_config(sorted_disp_df),
        }
        if not sorted_disp_df.empty and _supports_dataframe_selection_default():
            dataframe_kwargs["selection_default"] = {"selection": {"rows": [0]}}
        with _timed_span(timing_collector, "station insights table render"):
            tbl_event = st.dataframe(sorted_disp_df, **dataframe_kwargs)

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
            "tx_ab_bin_minutes": analysis_context.tx_ab_bin_minutes,
            "target_callsign": analysis_context.callsign,
            "lang": st.session_state.get("lang", "en"),
        }

        # ----------------------------------------------------
        # Render Raw Drill-Down Data (if user clicks a row)
        # ----------------------------------------------------
        # Streamlit dataframe selection state is user-driven. The table can preselect row 0
        # on first render, but a deliberate deselect-all must stay empty.
        raw_sel_rows = tbl_event.selection.rows or []
        sel_rows = [row for row in raw_sel_rows if 0 <= row < len(sorted_disp_df)]
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
            
            # Titel vorbereiten (wird erst unten im Layout gerendert)
            if len(selected_meta_df) == 1:
                selected_station = selected_meta_df.iloc[0][station_col]
                selected_locator = selected_meta_df.iloc[0][loc_col]
                drill_title = t['lbl_drill_single'].format(station=f"{selected_station} ({selected_locator})")
            else: 
                drill_title = t['lbl_drill_multi'].format(count=len(selected_meta_df))
                
            try:
                with _timed_span(timing_collector, "selected station rows load"):
                    station_df = _load_station_rows_for_drilldown(
                        parquet_path,
                        selected_meta_df,
                        station_col,
                        loc_col
                    )
                selected_evidence_export = _render_selected_station_evidence(
                    station_df,
                    selected_identity_df,
                    is_compare,
                    is_sequential,
                    analysis_context.tx_ab_bin_minutes,
                    run_id=run_id,
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
                        int(analysis_context.tx_ab_bin_minutes),
                        presentation_context.language,
                        presentation_context.theme,
                    ),
                    timing_collector=timing_collector,
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
                        tx_ab_bin_minutes=analysis_context.tx_ab_bin_minutes,
                        target_callsign=analysis_context.callsign,
                    )

                if info_msg:
                    st.info(info_msg, icon=":material/info:")
                elif drill_df is not None and not drill_df.empty:
                    drilldown_selected_df = _render_drilldown_dataframe(
                        drill_df,
                        drill_title,
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
                st.warning("Cache file expired. Please Run Analysis again.")

        register_inspector_export(
            analysis_id=analysis_id,
            selected_segment=selected_seg,
            selected_distance=range_summary,
            selected_direction=direction_summary,
            selected_ranges=list(selected_ranges) if selected_ranges else [opt_full],
            selected_directions=list(selected_directions) if selected_directions else [opt_all_dir],
            show_non_joint=show_non_joint,
            evidence_time_bin=(selected_evidence_export or {}).get("time_bin"),
            selected_stations=selected_station_labels,
            segment_figure_recipe=segment_figure_recipe,
            selected_evidence_figure_recipe=(selected_evidence_export or {}).get("export_recipe"),
            station_insights_df=sorted_disp_df,
            drilldown_selected_df=drilldown_selected_df,
            all_drilldown_context=all_drilldown_context,
            reference_snr_header=f'{ref_header} SNR (dB)' if is_compare else None,
        )

        if show_export_button:
            render_download_all_results(t)
