"""
Segment Inspector & Results Components Module.
Contains the interactive drill-down UI (histograms, data tables) and 
compact recipes for lazy high-resolution result exports. Isolated as Streamlit fragments
to allow UI updates without triggering full-page reruns.
"""

import ast
import inspect
from collections import OrderedDict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import streamlit as st
from config import APP_VERSION, COMPASS
from ui.results_export import register_inspector_export, render_download_all_results

EVIDENCE_COLORS = ["#36aaf9", "#ffbe33", "#72fe5e", "#cc00ff", "#f66b19"]
EVIDENCE_AGG_COLOR = "#36aaf9"
EVIDENCE_SEPARATE_STATION_LIMIT = 5
STABILITY_BOOTSTRAP_ITERATIONS = 500
STABILITY_CONFIDENCE = 0.90
STABILITY_LINE_THRESHOLD_DB = 0.1
STABILITY_CACHE_STATE_KEY = "segment_stability_cache"
STABILITY_CACHE_MAX_ENTRIES = 4
METRIC_MIN_VISIBLE_SPAN_DB = 3.0
METRIC_HISTOGRAM_INTEGER_LATTICE_THRESHOLD = 0.95
METRIC_HISTOGRAM_HALF_DB_LATTICE_THRESHOLD = 0.95
METRIC_HISTOGRAM_MAX_BARS = 40
METRIC_HISTOGRAM_AGGREGATE_BIN_WIDTHS = (1.0, 2.0, 3.0, 6.0, 10.0)
SEGMENT_FIGURE_BOTTOM = 0.15
SEGMENT_FIGURE_FOOTER_Y = 0.055
EVIDENCE_TIME_AGG_PRESETS = [
    (pd.Timedelta(hours=6), ["5m", "15m", "30m", "1h", "3h"], "15m"),
    (pd.Timedelta(hours=24), ["15m", "30m", "1h", "3h", "6h"], "30m"),
    (pd.Timedelta(days=7), ["1h", "3h", "6h", "12h", "24h"], "3h"),
    (None, ["3h", "6h", "12h", "24h"], "6h"),
]
EVIDENCE_HEATMAP_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "wspr_evidence_heatmap",
    ["#1849a9", "#00b050", "#ffb000", "#d7191c"]
)
EVIDENCE_HEATMAP_CMAP.set_bad((0, 0, 0, 0))
GRID_COLOR = "#777777"
GRID_LINEWIDTH = 1.0
GRID_ALPHA = 0.35

def _add_horizontal_grid(ax):
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)

def _add_foreground_horizontal_grid(ax):
    ax.set_axisbelow(False)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA, zorder=3)

def _unique_station_order(stations):
    """Return station labels once, preserving the table selection order."""
    return list(dict.fromkeys([str(s) for s in stations if pd.notna(s)]))

def _empty_evidence_df():
    return pd.DataFrame(columns=["identity", "station", "grid", "plot_time", "metric", "identity_order"])

def _prepare_identity_meta(identity_df):
    """Normalize selected station identities to callsign+locator rows with stable labels."""
    if identity_df is None or identity_df.empty or not {"peer_sign", "peer_grid"}.issubset(identity_df.columns):
        return pd.DataFrame(columns=["peer_sign", "peer_grid", "identity", "identity_order"])

    meta = identity_df[["peer_sign", "peer_grid"]].dropna().copy()
    meta["peer_sign"] = meta["peer_sign"].astype(str)
    meta["peer_grid"] = meta["peer_grid"].astype(str)
    meta = meta.drop_duplicates().reset_index(drop=True)
    meta["identity"] = meta["peer_sign"] + " (" + meta["peer_grid"] + ")"
    meta["identity_order"] = np.arange(len(meta))
    return meta

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

def _format_metric_signed(value, is_compare):
    """Format SNR-like values for compact stability labels."""
    if pd.isna(value):
        return "n/a"
    if is_compare:
        return f"{float(value):+.1f}"
    return f"{float(value):.1f}"

def _format_stability_interval(low, high, is_compare):
    if pd.isna(low) or pd.isna(high):
        return "n/a"
    return f"{_format_metric_signed(low, is_compare)} .. {_format_metric_signed(high, is_compare)}"

def _bootstrap_median_interval(values, iterations=STABILITY_BOOTSTRAP_ITERATIONS, confidence=STABILITY_CONFIDENCE, seed=42):
    """Return median and central bootstrap interval for the median."""
    values = pd.to_numeric(pd.Series(values), errors="coerce").dropna().to_numpy(dtype=float)
    if len(values) == 0:
        return np.nan, np.nan, np.nan

    median = float(np.median(values))
    if len(values) == 1:
        return median, median, median

    rng = np.random.default_rng(seed)
    boot_medians = np.empty(iterations, dtype=float)
    for idx in range(iterations):
        sample = values[rng.integers(0, len(values), len(values))]
        boot_medians[idx] = np.median(sample)

    alpha = (1.0 - confidence) / 2.0
    low, high = np.quantile(boot_medians, [alpha, 1.0 - alpha])
    return median, float(low), float(high)

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

def _stability_summary(values, is_compare, prefix="", interval=None):
    """Build a short human-readable resampling summary for selected evidence."""
    median, low, high = interval if interval is not None else _bootstrap_median_interval(values)
    if pd.isna(median):
        return None

    metric_name = "\u0394 SNR" if is_compare else "SNR"
    prefix_text = f"{prefix} | " if prefix else ""
    return (
        f"{prefix_text}median {metric_name} {_format_metric_signed(median, is_compare)} dB | "
        f"90% stability {_format_stability_interval(low, high, is_compare)} dB"
    )

def _metric_values(values):
    """Return finite numeric SNR-like values as a one-dimensional numpy array."""
    numeric_values = pd.to_numeric(pd.Series(values), errors="coerce").dropna().to_numpy(dtype=float)
    return numeric_values[np.isfinite(numeric_values)]

def _dominant_tenth_remainder(tenths, modulus):
    """Return the dominant remainder on a one-decimal lattice and its fraction."""
    if len(tenths) == 0:
        return 0, 0.0
    remainders = np.mod(tenths, modulus)
    counts = np.bincount(remainders, minlength=modulus)
    index = int(np.argmax(counts))
    return index, float(counts[index]) / float(len(tenths))

def _metric_histogram_bar_count(min_value, max_value, anchor, bin_width):
    if not np.isfinite(min_value) or not np.isfinite(max_value) or bin_width <= 0:
        return 0
    start_center = anchor + np.floor((min_value - anchor) / bin_width) * bin_width
    end_center = anchor + np.ceil((max_value - anchor) / bin_width) * bin_width
    return int(np.floor((end_center - start_center) / bin_width + 0.5)) + 1

def _metric_histogram_bin_width_and_anchor(values):
    """
    Choose one global SNR-bin width for a plot.

    Raw WSPR SNR is integer-dB, while corrections and medians can shift the
    lattice. Prefer 1 dB bins, but use 0.5 dB when the data clearly occupy a
    half-dB lattice. Never infer sub-0.5 dB visual precision.
    """
    values = _metric_values(values)
    if len(values) == 0:
        return 1.0, 0.0

    min_value = float(np.min(values))
    max_value = float(np.max(values))
    tenths = np.rint(values * 10.0).astype(int)
    integer_remainder, integer_fraction = _dominant_tenth_remainder(tenths, 10)
    if integer_fraction >= METRIC_HISTOGRAM_INTEGER_LATTICE_THRESHOLD:
        base_width = 1.0
        anchor = integer_remainder / 10.0
    else:
        half_remainder, half_fraction = _dominant_tenth_remainder(tenths, 5)
        if half_fraction >= METRIC_HISTOGRAM_HALF_DB_LATTICE_THRESHOLD:
            base_width = 0.5
            anchor = half_remainder / 10.0
        else:
            base_width = 1.0
            anchor = 0.0

    if _metric_histogram_bar_count(min_value, max_value, anchor, base_width) <= METRIC_HISTOGRAM_MAX_BARS:
        return base_width, anchor

    for candidate_width in METRIC_HISTOGRAM_AGGREGATE_BIN_WIDTHS:
        if candidate_width < base_width:
            continue
        if _metric_histogram_bar_count(min_value, max_value, anchor, candidate_width) <= METRIC_HISTOGRAM_MAX_BARS:
            return candidate_width, anchor

    return METRIC_HISTOGRAM_AGGREGATE_BIN_WIDTHS[-1], anchor

def _metric_histogram_bins(values):
    """Return centered histogram edges, centers and bin width for SNR-like values."""
    values = _metric_values(values)
    bin_width, anchor = _metric_histogram_bin_width_and_anchor(values)
    if len(values) == 0:
        return np.array([]), np.array([]), bin_width

    min_value = float(np.min(values))
    max_value = float(np.max(values))
    start_center = anchor + np.floor((min_value - anchor) / bin_width) * bin_width
    end_center = anchor + np.ceil((max_value - anchor) / bin_width) * bin_width
    centers = np.arange(start_center, end_center + (bin_width * 0.5), bin_width)
    if len(centers) == 0:
        centers = np.array([anchor])
    edges = np.concatenate((centers - (bin_width / 2.0), [centers[-1] + (bin_width / 2.0)]))
    return edges, centers, bin_width

def _format_bin_width(bin_width):
    return f"{float(bin_width):.1f} dB"

def _histogram_mode_summary(values):
    values = _metric_values(values)
    if len(values) == 0:
        return np.nan, np.nan
    edges, centers, _ = _metric_histogram_bins(values)
    if len(edges) == 0:
        return np.nan, np.nan
    counts, _ = np.histogram(values, bins=edges)
    if counts.sum() == 0:
        return np.nan, np.nan
    mode_index = int(np.argmax(counts))
    return float(centers[mode_index]), 100.0 * float(counts[mode_index]) / float(counts.sum())

def _zero_bin_share(values):
    values = _metric_values(values)
    if len(values) == 0:
        return np.nan
    edges, _, _ = _metric_histogram_bins(values)
    if len(edges) == 0:
        return np.nan
    counts, _ = np.histogram(values, bins=edges)
    zero_index = np.searchsorted(edges, 0.0, side="right") - 1
    if zero_index < 0 or zero_index >= len(counts):
        return 0.0
    return 100.0 * float(counts[zero_index]) / float(counts.sum())

def _metric_distribution_summary(values, is_compare):
    """Summarize the visible distribution without adding labels to every bar."""
    values = _metric_values(values)
    if len(values) == 0:
        return None

    _, _, bin_width = _metric_histogram_bins(values)
    mode_value, mode_pct = _histogram_mode_summary(values)
    if pd.isna(mode_value) or pd.isna(mode_pct):
        return f"bin {_format_bin_width(bin_width)}"

    if is_compare:
        zero_pct = _zero_bin_share(values)
        within_1_pct = 100.0 * float(np.sum(np.abs(values) <= 1.0)) / float(len(values))
        tail_3_pct = 100.0 * float(np.sum(np.abs(values) >= 3.0)) / float(len(values))
        return (
            f"bin {_format_bin_width(bin_width)} | "
            f"mode {_format_metric_signed(mode_value, True)} dB ({mode_pct:.1f}%) | "
            f"\u0394\u22480 dB {zero_pct:.1f}% | "
            f"|\u0394|\u22641 dB {within_1_pct:.1f}% | "
            f"|\u0394|\u22653 dB {tail_3_pct:.1f}%"
        )

    q05, q95 = np.percentile(values, [5, 95])
    return (
        f"bin {_format_bin_width(bin_width)} | "
        f"mode {_format_metric_signed(mode_value, False)} dB ({mode_pct:.1f}%) | "
        f"90% range {_format_stability_interval(q05, q95, False)} dB"
    )

def _add_stability_band(ax, low, high):
    """Draw the true 90% stability interval without inflating narrow ranges."""
    if pd.isna(low) or pd.isna(high):
        return
    low = float(low)
    high = float(high)
    if high < low:
        low, high = high, low
    if high - low <= STABILITY_LINE_THRESHOLD_DB:
        center = (low + high) / 2.0
        ax.axhline(center, color="red", alpha=0.24, linewidth=4.0, zorder=1, label="90% Stability")
    else:
        ax.axhspan(low, high, color="red", alpha=0.12, zorder=1, label="90% Stability")

def _add_vertical_stability_band(ax, low, high):
    """Draw the true 90% stability interval on a metric x-axis."""
    if pd.isna(low) or pd.isna(high):
        return
    low = float(low)
    high = float(high)
    if high < low:
        low, high = high, low
    if high - low <= STABILITY_LINE_THRESHOLD_DB:
        center = (low + high) / 2.0
        ax.axvline(center, color="red", alpha=0.24, linewidth=4.0, zorder=1, label="90% Stability")
    else:
        ax.axvspan(low, high, color="red", alpha=0.12, zorder=1, label="90% Stability")

def _expanded_metric_limits(lower, upper, center=None, min_span=METRIC_MIN_VISIBLE_SPAN_DB):
    """Return limits with a minimum SNR-scale span while preserving the data center."""
    if not np.isfinite(lower) or not np.isfinite(upper):
        return None
    lower = float(lower)
    upper = float(upper)
    if upper < lower:
        lower, upper = upper, lower
    if center is None or not np.isfinite(center):
        center = (lower + upper) / 2.0
    center = float(center)
    span = upper - lower
    if span >= min_span:
        return lower, upper
    half_span = min_span / 2.0
    expanded_lower = center - half_span
    expanded_upper = center + half_span
    if expanded_lower > lower:
        shift = expanded_lower - lower
        expanded_lower -= shift
        expanded_upper -= shift
    if expanded_upper < upper:
        shift = upper - expanded_upper
        expanded_lower += shift
        expanded_upper += shift
    return expanded_lower, expanded_upper

def _apply_minimum_metric_yspan(ax, center=None):
    """Keep SNR/Delta-SNR panels from visually magnifying tiny intervals."""
    lower, upper = ax.get_ylim()
    expanded = _expanded_metric_limits(lower, upper, center=center)
    if expanded is not None:
        ax.set_ylim(*expanded)

def _apply_minimum_metric_xspan(ax, center=None):
    """Keep SNR/Delta-SNR x-axes from visually magnifying tiny intervals."""
    lower, upper = ax.get_xlim()
    expanded = _expanded_metric_limits(lower, upper, center=center)
    if expanded is not None:
        ax.set_xlim(*expanded)

def _place_metric_legend_top_right(ax):
    """Place compact metric legends inside the plot in the usual empty corner."""
    ax.legend(
        loc="upper right",
        ncol=1,
        facecolor="#121212",
        edgecolor="#444444",
        labelcolor="white",
        fontsize=8,
        framealpha=0.9,
        borderaxespad=0.0
    )

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

def _parse_ref_detail_rows(value):
    """Parse ClickHouse Array(Tuple(...)) CSV output for Local Median drill-down display."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        raw_rows = value
    else:
        text = str(value).strip()
        if not text or text.lower() in {"nan", "none", "null"}:
            return []
        try:
            raw_rows = ast.literal_eval(text)
        except (SyntaxError, ValueError):
            return []

    parsed_rows = []
    for row in raw_rows:
        if isinstance(row, (list, tuple)) and len(row) >= 4:
            parsed_rows.append({
                "ref_sign": row[0],
                "ref_grid": row[1],
                "ref_dist": row[2],
                "ref_snr": row[3]
            })
    return parsed_rows

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

def _build_evidence_points(station_df, identity_df, is_compare, is_sequential):
    """Build raw evidence points for the selected station+locator distribution and time plots."""
    identity_meta = _prepare_identity_meta(identity_df)
    if identity_meta.empty or station_df.empty:
        return _empty_evidence_df()

    station_df = station_df.copy()
    if not {"peer_sign", "peer_grid"}.issubset(station_df.columns):
        return _empty_evidence_df()
    station_df["peer_sign"] = station_df["peer_sign"].astype(str)
    station_df["peer_grid"] = station_df["peer_grid"].astype(str)
    station_df = station_df.merge(identity_meta, on=["peer_sign", "peer_grid"], how="inner")
    if station_df.empty:
        return _empty_evidence_df()

    if not is_compare:
        if "time" not in station_df.columns or "stat_val" not in station_df.columns:
            return _empty_evidence_df()

        evidence_df = station_df[["peer_sign", "peer_grid", "identity", "identity_order", "time", "stat_val"]].copy()
        evidence_df["plot_time"] = pd.to_datetime(evidence_df["time"], errors="coerce")
        evidence_df["metric"] = pd.to_numeric(evidence_df["stat_val"], errors="coerce")
    elif is_sequential:
        required_cols = {"peer_sign", "peer_grid", "identity", "identity_order", "time", "is_me", "stat_val"}
        if not required_cols.issubset(station_df.columns):
            return _empty_evidence_df()

        bin_minutes = st.session_state.get("val_tx_ab_bin_minutes", 8)
        work_df = station_df[list(required_cols)].copy()
        work_df["dt_time"] = pd.to_datetime(work_df["time"], errors="coerce")
        work_df = work_df.dropna(subset=["dt_time"])
        work_df["time_bin"] = work_df["dt_time"].dt.floor(f"{bin_minutes}min")
        work_df["is_me"] = pd.to_numeric(work_df["is_me"], errors="coerce")
        work_df["stat_val"] = pd.to_numeric(work_df["stat_val"], errors="coerce")

        target_df = (
            work_df[work_df["is_me"] == 1]
            .groupby(["peer_sign", "peer_grid", "identity", "identity_order", "time_bin"], dropna=False)["stat_val"]
            .median()
            .reset_index(name="target_snr")
        )
        ref_df = (
            work_df[work_df["is_me"] == 0]
            .groupby(["peer_sign", "peer_grid", "identity", "identity_order", "time_bin"], dropna=False)["stat_val"]
            .median()
            .reset_index(name="ref_snr")
        )
        evidence_df = target_df.merge(
            ref_df,
            on=["peer_sign", "peer_grid", "identity", "identity_order", "time_bin"],
            how="inner"
        )
        evidence_df["plot_time"] = evidence_df["time_bin"]
        evidence_df["metric"] = evidence_df["target_snr"] - evidence_df["ref_snr"]
    else:
        required_cols = {"peer_sign", "peer_grid", "identity", "identity_order", "time_slot", "has_u", "has_r", "snr_u_norm", "snr_r_norm"}
        if not required_cols.issubset(station_df.columns):
            return _empty_evidence_df()

        evidence_df = station_df[list(required_cols)].copy()
        for col in ["time_slot", "has_u", "has_r", "snr_u_norm", "snr_r_norm"]:
            evidence_df[col] = pd.to_numeric(evidence_df[col], errors="coerce")
        evidence_df = evidence_df[(evidence_df["has_u"] > 0) & (evidence_df["has_r"] > 0)]
        evidence_df["plot_time"] = pd.to_datetime(evidence_df["time_slot"] * 120, unit="s", errors="coerce")
        evidence_df["metric"] = (
            pd.to_numeric(evidence_df["snr_u_norm"], errors="coerce") -
            pd.to_numeric(evidence_df["snr_r_norm"], errors="coerce")
        )

    evidence_df = evidence_df[["identity", "peer_sign", "peer_grid", "identity_order", "plot_time", "metric"]].copy()
    evidence_df.columns = ["identity", "station", "grid", "identity_order", "plot_time", "metric"]
    evidence_df = evidence_df.dropna(subset=["identity", "plot_time", "metric"])
    if evidence_df.empty:
        return evidence_df

    evidence_df["metric"] = evidence_df["metric"].round(1)
    identity_labels = identity_meta["identity"].tolist()
    evidence_df["identity"] = pd.Categorical(evidence_df["identity"], categories=identity_labels, ordered=True)
    return evidence_df.sort_values(["identity_order", "plot_time"]).reset_index(drop=True)

def _style_evidence_axis(ax):
    ax.set_facecolor("black")
    ax.tick_params(colors="white")
    _add_horizontal_grid(ax)
    for spine in ax.spines.values():
        spine.set_color("#444444")

def _draw_raincloud(ax, grouped_values, group_labels, colors):
    positions = np.arange(1, len(grouped_values) + 1)
    rng = np.random.default_rng(42)

    violin_values = []
    violin_positions = []
    violin_colors = []
    for pos, values, color in zip(positions, grouped_values, colors):
        if len(values) >= 2:
            violin_values.append(values)
            violin_positions.append(pos)
            violin_colors.append(color)

    if violin_values:
        violins = ax.violinplot(
            violin_values,
            positions=violin_positions,
            widths=0.62,
            showmeans=False,
            showmedians=False,
            showextrema=False,
        )
        for body, pos, color in zip(violins["bodies"], violin_positions, violin_colors):
            verts = body.get_paths()[0].vertices
            verts[:, 0] = np.maximum(verts[:, 0], pos)
            body.set_facecolor(color)
            body.set_edgecolor(color)
            body.set_alpha(0.28)

    for pos, values, color in zip(positions, grouped_values, colors):
        jitter_x = pos - 0.18 + rng.normal(0, 0.045, len(values))
        ax.scatter(jitter_x, values, s=12, color=color, alpha=0.58, edgecolors="none", zorder=3)

    box = ax.boxplot(
        grouped_values,
        positions=positions,
        widths=0.14,
        patch_artist=True,
        showfliers=False,
        manage_ticks=False,
    )
    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.45)
        patch.set_edgecolor("#cccccc")
    for key in ["whiskers", "caps", "medians"]:
        for artist in box[key]:
            artist.set_color("#cccccc")
            artist.set_linewidth(1.0)

    ax.set_xticks(positions)
    ax.set_xticklabels(group_labels, rotation=20, ha="right", color="white", fontsize=9)
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=6))

def _draw_single_vertical_raincloud(ax, values, label, color="#36aaf9"):
    """Draw one vertical raincloud and return the median of its plotted values."""
    values = pd.to_numeric(pd.Series(values), errors="coerce").dropna().to_numpy(dtype=float)
    if len(values) == 0:
        return np.nan
    _draw_raincloud(ax, [values], [label], [color])
    return float(np.median(values))

def _draw_vertical_metric_histogram(ax, values, color="#36aaf9"):
    """Draw a conventional histogram with the SNR metric on the horizontal axis."""
    values = _metric_values(values)
    if len(values) == 0:
        return np.nan

    edges, centers, bin_width = _metric_histogram_bins(values)
    counts, _ = np.histogram(values, bins=edges)
    if counts.sum() == 0:
        return np.nan

    shares = 100.0 * counts.astype(float) / float(counts.sum())
    ax.bar(
        centers,
        shares,
        width=bin_width * 0.82,
        color=color,
        alpha=0.70,
        edgecolor="#67c4ff",
        linewidth=0.7,
        align="center",
        zorder=2
    )
    ax.set_ylabel("Share (%)", color="white")
    ax.set_ylim(bottom=0.0)
    ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=6))
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=5))
    ax.grid(axis="x", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=0.20)
    return float(np.median(values))

def _draw_horizontal_metric_histogram(ax, values, color="#36aaf9"):
    """Draw a histogram with the SNR metric on the vertical axis."""
    values = _metric_values(values)
    if len(values) == 0:
        return np.nan

    edges, centers, bin_width = _metric_histogram_bins(values)
    counts, _ = np.histogram(values, bins=edges)
    if counts.sum() == 0:
        return np.nan

    shares = 100.0 * counts.astype(float) / float(counts.sum())
    ax.barh(
        centers,
        shares,
        height=bin_width * 0.82,
        color=color,
        alpha=0.70,
        edgecolor="#67c4ff",
        linewidth=0.7,
        zorder=2
    )
    ax.set_xlabel("Share (%)", color="white")
    ax.set_xlim(left=0.0)
    ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=5))
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=6))
    ax.grid(axis="x", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=0.20)
    return float(np.median(values))

def _draw_single_value_distribution(ax, value, labels, color=EVIDENCE_AGG_COLOR):
    """Render one selected evidence point without implying distribution width."""
    value = float(value)
    ax.axhline(value, color=color, linewidth=2.0, alpha=0.95, zorder=3)
    ax.scatter(
        [0.5],
        [value],
        s=42,
        color=color,
        edgecolors="#c8f4ff",
        linewidths=0.7,
        zorder=4
    )
    ax.text(
        0.5,
        0.58,
        f"{value:+.1f} dB" if "\u0394" in labels["y_label"] else f"{value:.1f} dB",
        transform=ax.transAxes,
        color="white",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )
    ax.text(
        0.5,
        0.42,
        "single evidence point",
        transform=ax.transAxes,
        color="#cccccc",
        ha="center",
        va="top",
        fontsize=9
    )
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks([])
    ax.set_yticks([value])
    ax.set_yticklabels([f"{value:.1f}"], color="white")
    ax.set_ylabel(labels["y_label"], color="white")
    _apply_minimum_metric_yspan(ax, center=value)

def _draw_single_time_point(ax, plot_df, labels):
    """Render one selected evidence timestamp without a heatmap/color scale."""
    work_df = plot_df[["plot_time", "metric"]].copy()
    work_df["plot_time"] = pd.to_datetime(work_df["plot_time"], errors="coerce", utc=True).dt.tz_convert(None)
    work_df["metric"] = pd.to_numeric(work_df["metric"], errors="coerce")
    work_df = work_df.dropna(subset=["plot_time", "metric"])
    if work_df.empty:
        return

    timestamp = work_df["plot_time"].iloc[0]
    value = float(work_df["metric"].iloc[0])
    x_value = mdates.date2num(timestamp.to_pydatetime())
    ax.scatter(
        [x_value],
        [value],
        s=42,
        color="#c8f4ff",
        edgecolors="#00384d",
        linewidths=0.7,
        zorder=5
    )
    ax.annotate(
        f"{value:+.1f} dB" if "\u0394" in labels["y_label"] else f"{value:.1f} dB",
        xy=(x_value, value),
        xytext=(8, 8),
        textcoords="offset points",
        color="white",
        fontsize=9,
        ha="left",
        va="bottom"
    )
    half_window = pd.Timedelta(minutes=90)
    ax.set_xlim(
        mdates.date2num((timestamp - half_window).to_pydatetime()),
        mdates.date2num((timestamp + half_window).to_pydatetime())
    )
    ax.set_yticks([value])
    ax.set_yticklabels([f"{value:.1f}"], color="white")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b\n%H:%M"))
    ax.set_title(f"{labels['time_title']} (single point)", color="white", fontweight="bold", pad=10)
    ax.set_xlabel(labels["x_label"], color="white")
    ax.set_ylabel(labels["y_label"], color="white")
    _apply_minimum_metric_yspan(ax, center=value)
    _add_foreground_horizontal_grid(ax)

def _draw_horizontal_raincloud(ax, values, color="#36aaf9"):
    """Draw one horizontal raw-observation raincloud for segment-level evidence."""
    values = pd.to_numeric(pd.Series(values), errors="coerce").dropna().to_numpy(dtype=float)
    if len(values) == 0:
        return np.nan

    pos = 1.0
    rng = np.random.default_rng(42)

    if len(values) >= 2:
        violins = ax.violinplot(
            [values],
            positions=[pos],
            vert=False,
            widths=0.65,
            showmeans=False,
            showmedians=False,
            showextrema=False,
        )
        for body in violins["bodies"]:
            verts = body.get_paths()[0].vertices
            verts[:, 1] = np.maximum(verts[:, 1], pos)
            body.set_facecolor(color)
            body.set_edgecolor(color)
            body.set_alpha(0.28)

    jitter_y = pos - 0.16 + rng.normal(0, 0.04, len(values))
    ax.scatter(values, jitter_y, s=12, color=color, alpha=0.58, edgecolors="none", zorder=3)

    box = ax.boxplot(
        [values],
        positions=[pos],
        vert=False,
        widths=0.14,
        patch_artist=True,
        showfliers=False,
        manage_ticks=False,
    )
    for patch in box["boxes"]:
        patch.set_facecolor(color)
        patch.set_alpha(0.45)
        patch.set_edgecolor("#cccccc")
    for key in ["whiskers", "caps", "medians"]:
        for artist in box[key]:
            artist.set_color("#cccccc")
            artist.set_linewidth(1.0)

    ax.set_yticks([])
    ax.set_ylim(0.55, 1.55)
    ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=6))
    ax.grid(axis="x", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)
    return float(np.median(values))

def _robust_metric_limits(values):
    """Return robust visible y-limits and hidden-tail percentages using the 1.5 IQR rule."""
    values = pd.to_numeric(pd.Series(values), errors="coerce").dropna().to_numpy(dtype=float)
    if len(values) == 0:
        return None

    q1, q3 = np.percentile(values, [25, 75])
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    if not np.isfinite(lower) or not np.isfinite(upper):
        return None
    if upper <= lower:
        center = float(np.median(values))
        lower = center
        upper = center
    else:
        padding = 0.10 * (upper - lower)
        lower -= padding
        upper += padding

    expanded_limits = _expanded_metric_limits(lower, upper, center=float(np.median(values)))
    if expanded_limits is None:
        return None
    lower, upper = expanded_limits

    below_pct = 100.0 * float(np.sum(values < lower)) / len(values)
    above_pct = 100.0 * float(np.sum(values > upper)) / len(values)
    return lower, upper, below_pct, above_pct

def _annotate_outlier_range(ax, below_pct, above_pct):
    """Show how much selected evidence sits outside the visible robust range."""
    ax.text(
        0.98,
        0.96,
        f"outlier above range: {above_pct:.1f}%",
        transform=ax.transAxes,
        color="#cccccc",
        fontsize=8,
        ha="right",
        va="top",
        zorder=8
    )
    ax.text(
        0.98,
        0.04,
        f"outlier below range: {below_pct:.1f}%",
        transform=ax.transAxes,
        color="#cccccc",
        fontsize=8,
        ha="right",
        va="bottom",
        zorder=8
    )

def _build_segment_evidence_points(df_seg, parquet_path, is_compare, is_sequential):
    """Build raw segment-level evidence points from parquet using station+locator identity."""
    if df_seg.empty or not {"peer_sign", "peer_grid"}.issubset(df_seg.columns):
        return _empty_evidence_df()

    segment_meta = df_seg[["peer_sign", "peer_grid"]].dropna().copy()
    segment_meta["peer_sign"] = segment_meta["peer_sign"].astype(str)
    segment_meta["peer_grid"] = segment_meta["peer_grid"].astype(str)
    segment_meta = segment_meta.drop_duplicates()
    if segment_meta.empty:
        return _empty_evidence_df()

    read_columns = ["peer_sign", "peer_grid"]
    if not is_compare:
        read_columns += ["time", "stat_val"]
    elif is_sequential:
        read_columns += ["time", "is_me", "stat_val"]
    else:
        read_columns += ["time_slot", "has_u", "has_r", "snr_u_norm", "snr_r_norm"]

    try:
        raw_df = pd.read_parquet(
            parquet_path,
            columns=read_columns,
            filters=[("peer_sign", "in", segment_meta["peer_sign"].unique().tolist())]
        )
    except (FileNotFoundError, KeyError, ValueError):
        return _empty_evidence_df()

    if raw_df.empty:
        return _empty_evidence_df()

    raw_df["peer_sign"] = raw_df["peer_sign"].astype(str)
    raw_df["peer_grid"] = raw_df["peer_grid"].astype(str)
    segment_raw_df = raw_df.merge(segment_meta, on=["peer_sign", "peer_grid"], how="inner")
    if segment_raw_df.empty:
        return _empty_evidence_df()

    return _build_evidence_points(
        segment_raw_df,
        segment_meta,
        is_compare,
        is_sequential
    )

def _time_agg_minutes(time_agg):
    """Parse a compact minute/hour selector label such as '15m' or '3h' into minutes."""
    text = str(time_agg).strip().lower()
    multiplier = 60
    if text.endswith("m"):
        multiplier = 1
        text = text[:-1]
    elif text.endswith("h"):
        text = text[:-1]
    try:
        value = int(text)
    except (TypeError, ValueError):
        return 180
    return max(value * multiplier, 1)

def _time_agg_options_for_span(plot_df):
    """Return adaptive time-bin options and default based on selected evidence duration."""
    if plot_df.empty or "plot_time" not in plot_df.columns:
        return EVIDENCE_TIME_AGG_PRESETS[2][1], EVIDENCE_TIME_AGG_PRESETS[2][2]

    times = pd.to_datetime(plot_df["plot_time"], errors="coerce", utc=True).dropna()
    if times.empty:
        return EVIDENCE_TIME_AGG_PRESETS[2][1], EVIDENCE_TIME_AGG_PRESETS[2][2]

    span = times.max() - times.min()
    for max_span, options, default in EVIDENCE_TIME_AGG_PRESETS:
        if max_span is None or span <= max_span:
            return options, default

    return EVIDENCE_TIME_AGG_PRESETS[-1][1], EVIDENCE_TIME_AGG_PRESETS[-1][2]

def _draw_time_heatmap(fig, ax, plot_df, time_agg, labels, is_compare, is_sequential):
    """Draw selected-station evidence as UTC time-bin x integer-SNR density."""
    bin_minutes = _time_agg_minutes(time_agg)
    work_df = plot_df[["plot_time", "metric"]].copy()
    work_df["plot_time"] = pd.to_datetime(work_df["plot_time"], errors="coerce", utc=True).dt.tz_convert(None)
    work_df["metric"] = pd.to_numeric(work_df["metric"], errors="coerce")
    work_df = work_df.dropna(subset=["plot_time", "metric"])

    if work_df.empty:
        ax.text(
            0.5, 0.5, "No selected evidence available.",
            transform=ax.transAxes,
            color="#cccccc",
            ha="center",
            va="center"
        )
        ax.set_title(f"{labels['time_title']} ({time_agg} bins)", color="white", fontweight="bold", pad=10)
        ax.set_xlabel(labels["x_label"], color="white")
        ax.set_ylabel(labels["y_label"], color="white")
        return

    bin_delta = pd.to_timedelta(bin_minutes, unit="min")
    bin_freq = f"{bin_minutes}min"
    work_df["time_bin"] = work_df["plot_time"].dt.floor(bin_freq)
    work_df["metric_bin"] = work_df["metric"].round().astype(int)

    time_bins = pd.date_range(
        start=work_df["time_bin"].min(),
        end=work_df["time_bin"].max(),
        freq=bin_freq
    )
    if len(time_bins) == 0:
        return

    metric_min = int(work_df["metric_bin"].min())
    metric_max = int(work_df["metric_bin"].max())
    metric_bins = np.arange(metric_min, metric_max + 1)

    count_grid = (
        work_df
        .groupby(["metric_bin", "time_bin"], dropna=False)
        .size()
        .unstack(fill_value=0)
        .reindex(index=metric_bins, columns=time_bins, fill_value=0)
    )
    masked_counts = np.ma.masked_where(count_grid.to_numpy(dtype=float) == 0, count_grid.to_numpy(dtype=float))

    time_edges = time_bins.append(pd.DatetimeIndex([time_bins[-1] + bin_delta]))
    x_edges = mdates.date2num(time_edges.to_pydatetime())
    y_edges = np.arange(metric_min - 0.5, metric_max + 1.5, 1.0)
    mesh = ax.pcolormesh(
        x_edges,
        y_edges,
        masked_counts,
        cmap=EVIDENCE_HEATMAP_CMAP,
        shading="flat",
        zorder=1
    )

    median_df = (
        work_df
        .groupby("time_bin", dropna=False)["metric"]
        .agg(["median", "count"])
        .reindex(time_bins)
    )
    x_centers = mdates.date2num((time_bins + (bin_delta / 2)).to_pydatetime())
    medians = median_df["median"].to_numpy(dtype=float)
    counts = median_df["count"].fillna(0).to_numpy(dtype=float)
    has_median = ~np.isnan(medians) & (counts > 0)

    ax.scatter(
        x_centers[has_median],
        medians[has_median],
        s=26,
        color="#c8f4ff",
        edgecolors="#00384d",
        linewidths=0.5,
        zorder=5
    )
    for idx in range(len(x_centers) - 1):
        if counts[idx] >= 3 and counts[idx + 1] >= 3 and not np.isnan(medians[idx]) and not np.isnan(medians[idx + 1]):
            ax.plot(
                [x_centers[idx], x_centers[idx + 1]],
                [medians[idx], medians[idx + 1]],
                color="#c8f4ff",
                linewidth=1.2,
                alpha=0.75,
                zorder=4
            )

    count_label = "Paired spot-bin count" if is_sequential else ("Joint spot count" if is_compare else "Spot count")
    cbar = fig.colorbar(mesh, ax=ax, pad=0.012, fraction=0.03)
    cbar.set_label(count_label, color="white")
    cbar.ax.tick_params(colors="white", labelsize=8)
    cbar.outline.set_edgecolor("#444444")

    locator = mdates.AutoDateLocator(minticks=4, maxticks=10)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b\n%H:%M"))
    ax.set_xlim(x_edges[0], x_edges[-1])
    ax.set_ylim(metric_min - 0.5, metric_max + 0.5)
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=7, integer=True))
    ax.set_title(f"{labels['time_title']} ({time_agg} bins)", color="white", fontweight="bold", pad=10)
    ax.set_xlabel(labels["x_label"], color="white")
    ax.set_ylabel(labels["y_label"], color="white")
    _add_foreground_horizontal_grid(ax)

def _sort_drilldown_default(drill_df):
    """Sort drill-down rows by UTC timestamp, then station label when available."""
    if drill_df is None or drill_df.empty or "Date/Time (UTC)" not in drill_df.columns:
        return drill_df

    sort_df = drill_df.copy()
    sort_df["_sort_time"] = pd.to_datetime(sort_df["Date/Time (UTC)"], format="%d-%b-%Y %H:%M:%S", errors="coerce")

    sort_cols = ["_sort_time"]
    for candidate in ["TX Station", "RX Station"]:
        if candidate in sort_df.columns:
            sort_cols.append(candidate)
            break

    sort_df = sort_df.sort_values(sort_cols, ascending=[True] * len(sort_cols), na_position="last")
    return sort_df.drop(columns=["_sort_time"]).reset_index(drop=True)

def _sequential_tx_drilldown_labels(col_u_name, ref_header):
    """Use actual callsign plus role/setup for TX A/B drill-down traceability."""
    if col_u_name == "Setup A" and ref_header == "Setup B":
        base_call = str(st.session_state.get("val_callsign", "")).strip().upper()
        if base_call:
            return f"{base_call} (Target / Setup A)", f"{base_call} (Reference / Setup B)"
    return col_u_name, ref_header

def _load_station_rows_for_drilldown(parquet_path, selected_meta_df, station_col, loc_col):
    """Load raw parquet rows for selected callsign+locator identities."""
    if selected_meta_df is None or selected_meta_df.empty:
        return pd.DataFrame()

    selected_meta_df = selected_meta_df.copy()
    selected_meta_df[station_col] = selected_meta_df[station_col].astype(str)
    selected_meta_df[loc_col] = selected_meta_df[loc_col].astype(str)
    selected_meta_df = selected_meta_df.drop_duplicates(subset=[station_col, loc_col])
    sel_stations = _unique_station_order(selected_meta_df[station_col].tolist())
    if not sel_stations:
        return pd.DataFrame()

    station_df = pd.read_parquet(parquet_path, filters=[('peer_sign', 'in', sel_stations)])
    station_df['peer_sign'] = station_df['peer_sign'].astype(str)
    station_df['peer_grid'] = station_df['peer_grid'].astype(str)

    return station_df.merge(
        selected_meta_df,
        left_on=['peer_sign', 'peer_grid'],
        right_on=[station_col, loc_col],
        how='inner'
    )

def _build_drilldown_table(
    parquet_path,
    selected_meta_df,
    station_col,
    loc_col,
    km_col,
    az_col,
    analysis_id,
    is_compare,
    is_sequential,
    show_non_joint,
    is_local_median,
    col_u_name,
    ref_header,
    t,
    station_rows_df=None,
):
    """Build the drill-down dataframe for selected or all current segment identities."""
    if selected_meta_df is None or selected_meta_df.empty:
        return pd.DataFrame(), "No stations selected."

    selected_meta_df = selected_meta_df[[station_col, loc_col, km_col, az_col]].copy()
    selected_meta_df[station_col] = selected_meta_df[station_col].astype(str)
    selected_meta_df[loc_col] = selected_meta_df[loc_col].astype(str)
    selected_meta_df = selected_meta_df.drop_duplicates(subset=[station_col, loc_col])
    if station_rows_df is None:
        station_df = _load_station_rows_for_drilldown(parquet_path, selected_meta_df, station_col, loc_col)
    else:
        station_df = station_rows_df.copy()

    drill_df = None
    info_msg = None

    if station_df.empty:
        return pd.DataFrame(), "No spots available."

    if not is_compare:
        station_df['Date/Time (UTC)'] = pd.to_datetime(station_df['time']).dt.strftime('%d-%b-%Y %H:%M:%S')
        drill_df = station_df[['Date/Time (UTC)', station_col, loc_col, km_col, az_col, 'snr', 'power', 'stat_val']].copy()
        drill_df.columns = ['Date/Time (UTC)', station_col, loc_col, km_col, az_col, 'SNR (Raw)', 'TX Power (dBm)', 'Norm@1W']
        for col in ['SNR (Raw)', 'Norm@1W']:
            drill_df[col] = pd.to_numeric(drill_df[col], errors='coerce').round(1)
    else:
        if is_sequential:
            bin_minutes = st.session_state.get('val_tx_ab_bin_minutes', 8)
            station_df['dt_time'] = pd.to_datetime(station_df['time'])
            station_df['time_bin'] = station_df['dt_time'].dt.floor(f'{bin_minutes}min')

            df_t = station_df[station_df['is_me'] == 1]
            df_r = station_df[station_df['is_me'] == 0]

            bin_t = df_t.groupby('time_bin')['stat_val'].median().reset_index().rename(columns={'stat_val': 'micro_med_a'})
            bin_r = df_r.groupby('time_bin')['stat_val'].median().reset_index().rename(columns={'stat_val': 'micro_med_b'})

            station_df = pd.merge(station_df, bin_t, on='time_bin', how='left')
            station_df = pd.merge(station_df, bin_r, on='time_bin', how='left')
            station_df['bin_delta'] = np.where(
                station_df['micro_med_a'].notna() & station_df['micro_med_b'].notna(),
                station_df['micro_med_a'] - station_df['micro_med_b'],
                np.nan
            )

            if not show_non_joint:
                station_df = station_df[station_df['micro_med_a'].notna() & station_df['micro_med_b'].notna()]
                if station_df.empty:
                    return pd.DataFrame(), "No joint spots available for the selected station(s)."

            station_df['micro_med_b'] = np.where(station_df['is_me'] == 1, np.nan, station_df['micro_med_b'])
            station_df['micro_med_a'] = np.where(station_df['is_me'] == 0, np.nan, station_df['micro_med_a'])

            station_df = station_df.sort_values('dt_time', ascending=False)
            station_df['time_bin_str'] = station_df['time_bin'].dt.strftime('%H:%M') + ' - ' + (station_df['time_bin'] + pd.Timedelta(minutes=bin_minutes)).dt.strftime('%H:%M')
            station_df['Date/Time (UTC)'] = station_df['dt_time'].dt.strftime('%d-%b-%Y %H:%M:%S')
            target_tx_label, ref_tx_label = _sequential_tx_drilldown_labels(col_u_name, ref_header)
            station_df['tx_callsign'] = np.where(station_df['is_me'] == 1, target_tx_label, ref_tx_label)

            drill_df = station_df[['Date/Time (UTC)', 'time_bin_str', 'tx_callsign', 'power', 'snr', 'stat_val', 'micro_med_a', 'micro_med_b', 'bin_delta']].copy()
            drill_df.columns = [
                'Date/Time (UTC)', t.get('tbl_col_bin', 'Time-Bin'), 'TX Station',
                'TX Power (dBm)', 'SNR (Raw)', 'Norm@1W',
                t.get('tbl_col_micro_a', 'Micro-Med A'), t.get('tbl_col_micro_b', 'Micro-Med B'), t.get('tbl_col_bin_delta', 'Bin \u0394')
            ]

            for col in ['Norm@1W', t.get('tbl_col_micro_a', 'Micro-Med A'), t.get('tbl_col_micro_b', 'Micro-Med B'), t.get('tbl_col_bin_delta', 'Bin \u0394')]:
                drill_df[col] = drill_df[col].map(lambda x: f"{x:+.1f}" if pd.notna(x) else "")
        else:
            joint_df = station_df.copy() if show_non_joint else station_df[(station_df['has_u'] > 0) & (station_df['has_r'] > 0)].copy()
            if joint_df.empty:
                return pd.DataFrame(), "No spots available." if show_non_joint else "No joint spots available for the selected station(s)."

            joint_df['Date/Time (UTC)'] = pd.to_datetime(joint_df['time_slot'] * 120, unit='s').dt.strftime('%d-%b-%Y %H:%M:%S')
            joint_df.loc[joint_df['has_u'] == 0, 'snr_u_norm'] = np.nan
            joint_df.loc[joint_df['has_r'] == 0, 'snr_r_norm'] = np.nan

            col_u = f'{col_u_name} SNR (dB)'
            col_r = f'{ref_header} SNR (dB)'
            col_delta_lbl = t.get('tbl_col_delta_snr', '\u0394 SNR (dB)')
            station_type = 'RX Station' if analysis_id.startswith("TX") else 'TX Station'

            if is_local_median and 'ref_detail_rows' in joint_df.columns:
                expanded_rows = []
                for _, row in joint_df.iterrows():
                    refs = _parse_ref_detail_rows(row.get('ref_detail_rows'))
                    has_u = row.get('has_u', 0) > 0
                    has_r = row.get('has_r', 0) > 0
                    own_snr = row.get('snr_u_norm', np.nan) if has_u else np.nan
                    cycle_ref_median = row.get('snr_r_norm', np.nan) if has_r else np.nan
                    delta_snr = round(own_snr - cycle_ref_median, 1) if pd.notna(own_snr) and pd.notna(cycle_ref_median) else np.nan

                    if refs:
                        for ref in refs:
                            try:
                                ref_dist_km = round(float(ref["ref_dist"]) / 1000)
                            except (TypeError, ValueError):
                                ref_dist_km = np.nan
                            try:
                                ref_snr = round(float(ref["ref_snr"]), 1)
                            except (TypeError, ValueError):
                                ref_snr = np.nan
                            expanded_rows.append({
                                'Date/Time (UTC)': row['Date/Time (UTC)'],
                                station_type: row[station_col],
                                loc_col: row[loc_col],
                                km_col: row[km_col],
                                az_col: row[az_col],
                                t.get('tbl_col_ref_station', 'Ref Station'): ref["ref_sign"],
                                loc_col + ' (Ref)': ref["ref_grid"],
                                'Ref km': ref_dist_km,
                                t.get('tbl_col_ref_snr', 'Ref SNR (dB)'): ref_snr,
                                t.get('tbl_col_cycle_ref_median', 'Cycle Ref Median SNR (dB)'): round(cycle_ref_median, 1) if pd.notna(cycle_ref_median) else np.nan,
                                col_u: round(own_snr, 1) if pd.notna(own_snr) else np.nan,
                                col_delta_lbl: delta_snr
                            })
                    elif has_u:
                        expanded_rows.append({
                            'Date/Time (UTC)': row['Date/Time (UTC)'],
                            station_type: row[station_col],
                            loc_col: row[loc_col],
                            km_col: row[km_col],
                            az_col: row[az_col],
                            t.get('tbl_col_ref_station', 'Ref Station'): np.nan,
                            loc_col + ' (Ref)': np.nan,
                            'Ref km': np.nan,
                            t.get('tbl_col_ref_snr', 'Ref SNR (dB)'): np.nan,
                            t.get('tbl_col_cycle_ref_median', 'Cycle Ref Median SNR (dB)'): np.nan,
                            col_u: round(own_snr, 1) if pd.notna(own_snr) else np.nan,
                            col_delta_lbl: np.nan
                        })

                if expanded_rows:
                    drill_df = pd.DataFrame(expanded_rows).sort_values('Date/Time (UTC)', ascending=False)
                else:
                    info_msg = "No reference station details available for the selected station(s)."
            elif 'best_ref_sign' in joint_df.columns:
                joint_df[col_delta_lbl] = np.where((joint_df['has_u'] > 0) & (joint_df['has_r'] > 0), (joint_df['snr_u_norm'] - joint_df['snr_r_norm']).round(1), np.nan)
                joint_df['snr_u_norm'] = pd.to_numeric(joint_df['snr_u_norm'], errors='coerce').round(1)
                joint_df['snr_r_norm'] = pd.to_numeric(joint_df['snr_r_norm'], errors='coerce').round(1)
                joint_df['snr_u_norm'] = joint_df['snr_u_norm'].astype(object).fillna("None")
                joint_df['snr_r_norm'] = joint_df['snr_r_norm'].astype(object).fillna("None")
                joint_df[col_delta_lbl] = joint_df[col_delta_lbl].astype(object).fillna("None")
                joint_df['best_ref_sign'] = joint_df['best_ref_sign'].fillna("None")
                joint_df['best_ref_dist_km'] = (joint_df['best_ref_dist'] / 1000).round(0).astype('Int64')

                drill_df = joint_df[['Date/Time (UTC)', station_col, loc_col, km_col, az_col, 'best_ref_sign', 'best_ref_dist_km', 'snr_r_norm', 'snr_u_norm', col_delta_lbl]].copy()
                drill_df.columns = ['Date/Time (UTC)', station_type, loc_col, km_col, az_col, 'Best Ref', 'Ref km', col_r, col_u, col_delta_lbl]
            else:
                joint_df[col_delta_lbl] = np.where((joint_df['has_u'] > 0) & (joint_df['has_r'] > 0), (joint_df['snr_u_norm'] - joint_df['snr_r_norm']).round(1), np.nan)
                joint_df['snr_u_norm'] = pd.to_numeric(joint_df['snr_u_norm'], errors='coerce').round(1)
                joint_df['snr_r_norm'] = pd.to_numeric(joint_df['snr_r_norm'], errors='coerce').round(1)
                joint_df['snr_u_norm'] = joint_df['snr_u_norm'].astype(object).fillna("None")
                joint_df['snr_r_norm'] = joint_df['snr_r_norm'].astype(object).fillna("None")
                joint_df[col_delta_lbl] = joint_df[col_delta_lbl].astype(object).fillna("None")
                drill_df = joint_df[['Date/Time (UTC)', station_col, loc_col, km_col, az_col, 'snr_r_norm', 'snr_u_norm', col_delta_lbl]].copy()
                drill_df.columns = ['Date/Time (UTC)', station_type, loc_col, km_col, az_col, col_r, col_u, col_delta_lbl]

    if drill_df is not None and not drill_df.empty:
        drill_df = _sort_drilldown_default(drill_df)
    return drill_df if drill_df is not None else pd.DataFrame(), info_msg

def _render_drilldown_dataframe(drill_df, drill_title, analysis_id, run_id, selected_seg, t, is_compare):
    """Render selected drill-down rows with local filters and return the displayed dataframe."""
    if drill_df is None or drill_df.empty:
        return pd.DataFrame()

    col_d1, col_d2 = st.columns([0.7, 0.3], vertical_alignment="center")

    with col_d1:
        _section_header(drill_title, "material:table_rows")

    with col_d2:
        with st.popover("Filter", icon=":material/filter_alt:", use_container_width=True):
            st.markdown("**Filter column(s):**")
            d_filter_cols = st.multiselect(
                "Select Columns",
                drill_df.columns,
                label_visibility="collapsed",
                key=f"d_flt_{analysis_id}_{run_id}_{selected_seg}"
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
                            key=f"d_sld_{col}_{analysis_id}_{run_id}_{selected_seg}"
                        )
                        drill_df = drill_df[(drill_df[col] >= sel_range[0]) & (drill_df[col] <= sel_range[1])]
                else:
                    unique_vals = drill_df[col].astype(str).dropna().unique()
                    sel_vals = st.multiselect(
                        f"{col}",
                        unique_vals,
                        default=[],
                        key=f"d_ms_{col}_{analysis_id}_{run_id}_{selected_seg}"
                    )
                    if sel_vals:
                        drill_df = drill_df[drill_df[col].astype(str).isin(sel_vals)]

    _render_reference_correction_notice(t, is_compare)
    drill_display_df = _format_snr_display_columns(drill_df)
    st.dataframe(drill_display_df, width='stretch', hide_index=True)
    return drill_df.copy()

def _create_selected_station_evidence_figure(plot_df, evidence_title, labels, time_agg, is_compare, is_sequential):
    """Build the selected-station evidence figure for UI or lazy export rendering."""
    evidence_count = len(plot_df)
    fig_ev = plt.figure(figsize=(13, 5.6), facecolor="black")
    fig_ev.subplots_adjust(left=0.05, right=0.98, bottom=SEGMENT_FIGURE_BOTTOM, top=0.80, wspace=0.24)
    fig_ev.suptitle(f"\n{evidence_title}", color="white", fontweight="bold", fontsize=14, y=0.98)
    fig_ev.text(0.98, SEGMENT_FIGURE_FOOTER_Y, f"WSPRadar.org {APP_VERSION}", color="#888888", ha="right", fontsize=10)
    gs = fig_ev.add_gridspec(1, 3)
    ax_cloud = fig_ev.add_subplot(gs[0, 0])
    ax_time = fig_ev.add_subplot(gs[0, 1:], sharey=ax_cloud)
    ax_cloud.set_box_aspect(1)

    _style_evidence_axis(ax_cloud)
    _style_evidence_axis(ax_time)

    ax_cloud.set_title(labels["dist_title"], color="white", fontweight="bold", pad=10)
    if evidence_count == 1:
        single_value = pd.to_numeric(plot_df["metric"], errors="coerce").dropna()
        if not single_value.empty:
            _draw_single_value_distribution(ax_cloud, single_value.iloc[0], labels, color=EVIDENCE_AGG_COLOR)
        _draw_single_time_point(ax_time, plot_df, labels)
    else:
        _draw_horizontal_metric_histogram(ax_cloud, plot_df["metric"], color=EVIDENCE_AGG_COLOR)
        ax_cloud.set_ylabel(labels["y_label"], color="white")
        _draw_time_heatmap(fig_ev, ax_time, plot_df, time_agg, labels, is_compare, is_sequential)
    ax_time.tick_params(axis="x", labelrotation=0, labelsize=9)
    return fig_ev

def _selected_evidence_export_recipe(plot_df, evidence_title, labels, time_agg, is_compare, is_sequential):
    """Store only compact arrays and labels needed to rebuild the high-resolution figure."""
    plot_times = pd.to_datetime(plot_df["plot_time"], errors="coerce", utc=True)
    valid = plot_times.notna() & pd.to_numeric(plot_df["metric"], errors="coerce").notna()
    return {
        "title": evidence_title,
        "labels": dict(labels),
        "time_bin": time_agg,
        "is_compare": bool(is_compare),
        "is_sequential": bool(is_sequential),
        "plot_time_ns": (
            plot_times[valid]
            .dt.tz_convert(None)
            .to_numpy(dtype="datetime64[ns]")
            .astype(np.int64, copy=True)
        ),
        "metric": pd.to_numeric(plot_df.loc[valid, "metric"], errors="coerce").to_numpy(dtype=np.float64, copy=True),
    }

def render_selected_evidence_export_figure(recipe):
    """Rebuild a selected-station evidence figure only when preparing the results ZIP."""
    if not recipe:
        return None
    plot_df = pd.DataFrame({
        "plot_time": pd.to_datetime(np.asarray(recipe.get("plot_time_ns", []), dtype=np.int64), unit="ns", utc=True),
        "metric": np.asarray(recipe.get("metric", []), dtype=float),
    })
    if plot_df.empty:
        return None
    labels = recipe.get("labels")
    if not labels:
        labels = _evidence_labels(bool(recipe.get("is_compare")))
    return _create_selected_station_evidence_figure(
        plot_df,
        recipe.get("title", "Selected Station Evidence"),
        labels,
        recipe.get("time_bin", "3h"),
        bool(recipe.get("is_compare")),
        bool(recipe.get("is_sequential")),
    )

def _render_selected_station_evidence(station_df, selected_identity_df, is_compare, is_sequential):
    """Render selected-station distribution and time evidence between insights and drill-down."""
    identity_meta = _prepare_identity_meta(selected_identity_df)
    if identity_meta.empty:
        return None

    evidence_df = _build_evidence_points(station_df, identity_meta, is_compare, is_sequential)
    if evidence_df.empty:
        return None

    labels = _evidence_labels(is_compare)
    identity_labels = identity_meta["identity"].tolist()
    separate_stations = len(identity_labels) <= EVIDENCE_SEPARATE_STATION_LIMIT

    if separate_stations:
        group_labels = [label for label in identity_labels if label in set(evidence_df["identity"].astype(str))]
        plot_df = evidence_df.copy()
        plot_df["plot_group"] = plot_df["identity"].astype(str)
        colors = EVIDENCE_COLORS[:len(group_labels)]
    else:
        group_labels = [labels["aggregate"]]
        plot_df = evidence_df.copy()
        plot_df["plot_group"] = labels["aggregate"]
        colors = [EVIDENCE_AGG_COLOR]

    if not group_labels:
        return

    grouped_values = [
        plot_df.loc[plot_df["plot_group"] == group, "metric"].to_numpy(dtype=float)
        for group in group_labels
    ]
    non_empty = [(label, values, color) for label, values, color in zip(group_labels, grouped_values, colors) if len(values) > 0]
    if not non_empty:
        return

    ctrl_left, ctrl_time, ctrl_right = st.columns([1, 2, 0.05])
    with ctrl_time:
        time_agg_options, time_agg_default = _time_agg_options_for_span(plot_df)
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
                default=time_agg_default,
                key=agg_key,
                label_visibility="collapsed"
            )
        else:
            time_agg = st.radio(
                "Time aggregation",
                time_agg_options,
                index=time_agg_options.index(time_agg_default),
                horizontal=True,
                key=agg_key,
                label_visibility="collapsed"
            )

    selected_count = len(identity_labels)
    evidence_count = len(plot_df)
    evidence_basis = "paired spot bins" if is_sequential else ("joint spots" if is_compare else "spots")
    evidence_title_base = "Ausgewaehlte Stations-Evidenz" if st.session_state.lang == "de" else "Selected Station Evidence"
    if selected_count == 1:
        evidence_title = f"{evidence_title_base}: {identity_labels[0]} | {evidence_count} {evidence_basis}"
    else:
        evidence_title = f"{evidence_title_base}: {selected_count} stations | {evidence_count} {evidence_basis}"
    st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
    fig_ev = _create_selected_station_evidence_figure(
        plot_df,
        evidence_title,
        labels,
        time_agg,
        is_compare,
        is_sequential,
    )

    st.pyplot(fig_ev, width="stretch")
    plt.close(fig_ev)
    return {
        "export_recipe": _selected_evidence_export_recipe(
            plot_df,
            evidence_title,
            labels,
            time_agg,
            is_compare,
            is_sequential,
        ),
        "time_bin": time_agg,
        "title": evidence_title,
    }

def _segment_figure_export_recipe(
    *,
    title,
    selected_segment,
    is_compare,
    is_sequential,
    compare_layout,
    station_values,
    spot_values,
    station_interval,
    spot_interval,
    panel_counts,
    panel_labels,
    panel_y_label,
):
    """Store compact numeric inputs needed to rebuild the Segment Insight figure."""
    return {
        "title": title,
        "selected_segment": selected_segment,
        "is_compare": bool(is_compare),
        "is_sequential": bool(is_sequential),
        "compare_layout": bool(compare_layout),
        "station_values": _metric_values(station_values).astype(np.float64, copy=True),
        "spot_values": _metric_values(spot_values).astype(np.float64, copy=True),
        "station_interval": tuple(float(value) for value in station_interval),
        "spot_interval": tuple(float(value) for value in spot_interval),
        "panel_counts": [int(value) for value in panel_counts],
        "panel_labels": [str(value) for value in panel_labels],
        "panel_y_label": str(panel_y_label),
    }

def render_segment_insight_export_figure(recipe):
    """Rebuild the Segment Insight figure only when preparing the results ZIP."""
    if not recipe:
        return None

    is_compare = bool(recipe.get("is_compare"))
    is_sequential = bool(recipe.get("is_sequential"))
    compare_layout = bool(recipe.get("compare_layout"))
    station_values = np.asarray(recipe.get("station_values", []), dtype=float)
    spot_values = np.asarray(recipe.get("spot_values", []), dtype=float)
    station_interval = recipe.get("station_interval", (np.nan, np.nan, np.nan))
    spot_interval = recipe.get("spot_interval", (np.nan, np.nan, np.nan))
    panel_counts = list(recipe.get("panel_counts", []))
    panel_labels = list(recipe.get("panel_labels", []))

    fig_hist = plt.figure(figsize=(13, 5.6), facecolor="black")
    fig_hist.subplots_adjust(left=0.05, right=0.98, bottom=SEGMENT_FIGURE_BOTTOM, top=0.80, wspace=0.24)
    gs = fig_hist.add_gridspec(1, 3)
    ax_panel = fig_hist.add_subplot(gs[0, 0])
    ax_hist = fig_hist.add_subplot(gs[0, 1])
    ax_spot = fig_hist.add_subplot(gs[0, 2])
    ax_panel.set_box_aspect(1)
    ax_hist.set_box_aspect(1)
    ax_spot.set_box_aspect(1)

    ax_panel.set_facecolor("black")
    ax_panel.tick_params(axis="y", colors="white")
    ax_panel.tick_params(axis="x", colors="white", labelrotation=20, labelsize=9)
    for spine in ax_panel.spines.values():
        spine.set_color("#444444")
    _add_horizontal_grid(ax_panel)

    bars = ax_panel.bar(panel_labels, panel_counts, color="#36aaf9", alpha=0.8, edgecolor="black")
    ax_panel.set_ylabel(recipe.get("panel_y_label", "Count"), color="white")
    if compare_layout:
        ax_panel.set_title("System Sensitivity (Yield)", color="white", fontweight="bold", pad=10)
        total_count = sum(panel_counts)
        if total_count > 0:
            for bar in bars:
                height = bar.get_height()
                ax_panel.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + (max(panel_counts) * 0.02),
                    f"{(height / total_count) * 100:.1f}%",
                    ha="center",
                    va="bottom",
                    color="white",
                    fontsize=10,
                    fontweight="bold",
                )
        ax_hist.set_title("Station Medians (\u0394 SNR)", color="white", fontweight="bold", pad=10)
        ax_spot.set_title(
            "Paired Spot Bin \u0394 SNR" if is_sequential else "Joint-Spot \u0394 SNR",
            color="white",
            fontweight="bold",
            pad=10,
        )
    else:
        ax_panel.set_title("Segment Activity", color="white", fontweight="bold", pad=10)
        if panel_counts and max(panel_counts) > 0:
            for bar in bars:
                height = bar.get_height()
                ax_panel.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + (max(panel_counts) * 0.02),
                    f"{int(height)}",
                    ha="center",
                    va="bottom",
                    color="white",
                    fontsize=10,
                    fontweight="bold",
                )
        ax_hist.set_title("Station Medians (SNR @ 1W)", color="white", fontweight="bold", pad=10)
        ax_spot.set_title("Spot SNR (SNR @ 1W)", color="white", fontweight="bold", pad=10)

    fig_hist.suptitle(
        f"\n{recipe.get('title', '')} - {recipe.get('selected_segment', '')}",
        color="white",
        fontweight="bold",
        fontsize=14,
        y=0.98,
    )
    fig_hist.text(
        0.98,
        SEGMENT_FIGURE_FOOTER_Y,
        f"WSPRadar.org {APP_VERSION}",
        color="#888888",
        ha="right",
        fontsize=10,
    )

    ax_hist.set_facecolor("black")
    ax_hist.tick_params(colors="white")
    for spine in ax_hist.spines.values():
        spine.set_color("#444444")
    _add_horizontal_grid(ax_hist)

    ax_spot.set_facecolor("black")
    ax_spot.tick_params(colors="white")
    for spine in ax_spot.spines.values():
        spine.set_color("#444444")

    if len(station_values):
        station_median = _draw_vertical_metric_histogram(ax_hist, station_values, color="#36aaf9")
        _add_vertical_stability_band(ax_hist, station_interval[1], station_interval[2])
        ax_hist.axvline(station_median, color="red", linestyle="dashed", linewidth=1, label=f"{station_median:.1f} dB")
        _apply_minimum_metric_xspan(ax_hist, center=station_median)
        _place_metric_legend_top_right(ax_hist)
    else:
        ax_hist.text(0.5, 0.5, "No data", color="white", ha="center", va="center", fontsize=12, transform=ax_hist.transAxes)
        ax_hist.set_xticks([])
        ax_hist.set_yticks([])

    spot_median = _draw_vertical_metric_histogram(ax_spot, spot_values, color="#36aaf9")
    if pd.notna(spot_median):
        _add_vertical_stability_band(ax_spot, spot_interval[1], spot_interval[2])
        ax_spot.axvline(spot_median, color="red", linestyle="dashed", linewidth=1, label=f"{spot_median:.1f} dB")
        _apply_minimum_metric_xspan(ax_spot, center=spot_median)
        _place_metric_legend_top_right(ax_spot)
        if is_compare and len(spot_values):
            ax_spot.text(
                0.98,
                0.04,
                f"mean={float(np.mean(spot_values)):.1f} dB",
                transform=ax_spot.transAxes,
                ha="right",
                va="bottom",
                color="#cccccc",
                fontsize=10,
            )
    else:
        ax_spot.text(0.5, 0.5, "No data", color="white", ha="center", va="center", fontsize=12, transform=ax_spot.transAxes)
        ax_spot.set_xticks([])
        ax_spot.set_yticks([])

    metric_label = "\u0394 SNR (dB)" if is_compare else "Normalized SNR (dB @ 1 W)"
    ax_hist.set_xlabel(metric_label, color="white")
    ax_spot.set_xlabel(metric_label, color="white")
    return fig_hist

@st.fragment
def render_segment_inspector(analysis_id, title, is_compare, is_sequential, enriched_df, segs_df, parquet_path, line1_str, t, max_dist_km, show_export_button=False):
    """
    Renders the interactive Segment Inspector directly below the map.
    Allows drill-down into specific Azimuth/Distance chunks to show histograms and tabular data.
    Runs as an independent Streamlit fragment to prevent full-page reruns on interaction.
    """
    run_id = st.session_state.get("run_id", 0)
    
    # Extract inspectable distance segments from enriched_df, not only rendered heatmap segments.
    # segs_df only contains segments with valid joint Delta-SNR heatmap data; enriched_df also
    # contains non-joint evidence such as only target, only reference, or async-both rows.
    inspector_source_df = enriched_df[enriched_df['SegmentID'] != "Out of Bounds"].copy()
    inspector_source_df = inspector_source_df[inspector_source_df['r_min'] < max_dist_km]

    valid_distances = sorted(
        [d for d in inspector_source_df['dist_label'].dropna().unique()],
        key=lambda x: int(x.strip('[]km').split('-')[0])
    )
    filtered_distances = valid_distances
    
    lbl_dist = t.get("opt_insp_dist", "---")
    lbl_dir = t.get("opt_insp_dir", "---")
    opt_full = t.get("opt_full_range", "Full Range")
    opt_all_dir = t.get("opt_all_dirs", "All Directions")
    
    # Render Dropdowns
    col_insp1, col_insp2 = st.columns(2)
    with col_insp1: 
        dist_key = f"dist_{analysis_id}_{run_id}"
        dist_options = [opt_full] + filtered_distances
        if st.session_state.get(dist_key) in (None, lbl_dist) or st.session_state.get(dist_key) not in dist_options:
            st.session_state[dist_key] = opt_full
        sel_dist = st.selectbox("Distance", dist_options, key=dist_key, label_visibility="collapsed")
    with col_insp2:
        dir_key = f"dir_{analysis_id}_{run_id}"
        if sel_dist == opt_full:
            valid_dirs = sorted(
                [d for d in inspector_source_df['dir_name'].dropna().unique() if d in COMPASS],
                key=lambda x: COMPASS.index(x)
            )
        else:
            valid_dirs = sorted(
                [d for d in inspector_source_df[inspector_source_df['dist_label'] == sel_dist]['dir_name'].dropna().unique() if d in COMPASS],
                key=lambda x: COMPASS.index(x)
            )

        if not valid_dirs:
            dir_options = [t.get("opt_no_station", "No Stations")]
            sel_dir = st.selectbox("Direction", dir_options, key=dir_key, disabled=True, label_visibility="collapsed")
        else: 
            dir_options = [opt_all_dir] + valid_dirs
            if st.session_state.get(dir_key) in (None, lbl_dir) or st.session_state.get(dir_key) not in dir_options:
                st.session_state[dir_key] = opt_all_dir
            sel_dir = st.selectbox("Direction", dir_options, key=dir_key, label_visibility="collapsed")

    st.markdown("<div style='height:0.38rem;'></div>", unsafe_allow_html=True)

    # If user selected a valid segment, process the inspection data
    if sel_dir != t.get("opt_no_station", "No Stations"):
        selected_seg = f"{sel_dist if sel_dist != opt_full else t['opt_full_range']} | {sel_dir if sel_dir != opt_all_dir else t['opt_all_dirs']}"
        segment_insight_label = "Segment-Insight" if st.session_state.lang == "de" else "Segment Insight"
        _section_header(segment_insight_label, "material:data_usage")
        df_seg = enriched_df[enriched_df['SegmentID'] != "Out of Bounds"].copy()
        
        # Apply user filters
        if sel_dist != opt_full: df_seg = df_seg[df_seg['dist_label'] == sel_dist]
        if sel_dir != opt_all_dir: df_seg = df_seg[df_seg['dir_name'] == sel_dir]
            
        has_joint_rows = False
        has_non_joint_rows = False
        if is_compare and 'count_only_u' in df_seg.columns:
            has_joint_rows = (df_seg['spot_count'] > 0).any()
            has_non_joint_rows = ((df_seg['count_only_u'] > 0) | (df_seg['count_only_r'] > 0)).any()

        vals = df_seg['stat_val'].dropna()
        target_call = st.session_state.val_callsign.upper()
        
        # Setup specific labels based on the active test mode (Self vs Compare)
        if st.session_state.val_comp_mode == t["opt_comp_self"]:
            if st.session_state.val_self_test_mode == t["opt_self_rx"]:
                lbl_only_me = t['leg_only_me'].format(callsign=target_call)
                lbl_only_ref = t['leg_only_ref'].format(ref_callsign=st.session_state.val_self_call_b.upper())
                ref_header = st.session_state.val_self_call_b.upper()
                col_u_name = target_call
            else:
                lbl_only_me = t['leg_only_me'].format(callsign="Setup A")
                lbl_only_ref = t['leg_only_ref'].format(ref_callsign="Setup B")
                ref_header = "Setup B"
                col_u_name = "Setup A"
        else:
            lbl_only_me = t['leg_only_me'].format(callsign=target_call)
            col_u_name = target_call
            if st.session_state.val_comp_mode == t["opt_comp_radius"]: 
                lbl_only_ref = t['leg_only_ref_radius']
                ref_header = "Best Ref"
            else: 
                lbl_only_ref = t['leg_only_ref'].format(ref_callsign=st.session_state.val_ref_callsign.upper())
                ref_header = st.session_state.val_ref_callsign.upper()

        remote_str = t['txt_rx_stations'] if analysis_id.startswith("TX") else t['txt_tx_stations']
        is_local_median = (
            st.session_state.val_comp_mode == t["opt_comp_radius"] and
            st.session_state.get("val_local_benchmark", t.get("opt_local_median", "Local Median Neighborhood")) == t.get("opt_local_median", "Local Median Neighborhood")
        )
        yield_ref_header = t.get("lbl_neighborhood", "Neighborhood") if is_local_median else ref_header
        if is_local_median:
            ref_header = t.get("opt_local_median", "Local Median Neighborhood")
        
        # Build the sub-footer info string detailing decode counts
        if is_compare and 'count_only_u' in df_seg.columns:
            if is_sequential:
                seg_line2 = f"Both (Async): {len(df_seg[(df_seg['count_only_u']>0) & (df_seg['count_only_r']>0)])}  |  {lbl_only_me}: {int(df_seg['count_only_u'].sum())}  |  {lbl_only_ref}: {int(df_seg['count_only_r'].sum())}  |  {t['txt_remote']} {remote_str}: {len(df_seg)}"
            else:
                seg_joint = df_seg[df_seg['spot_count'] > 0]
                seg_line2 = f"{t['txt_joint_decodes']}: {int(df_seg['spot_count'].sum())}  |  {lbl_only_me}: {int(df_seg['count_only_u'].sum())}  |  {lbl_only_ref}: {int(df_seg['count_only_r'].sum())}  |  {t['txt_joint']} {remote_str}: {len(seg_joint)}  |  {t['txt_remote']} {remote_str}: {len(df_seg)}"
        else:
            seg_line2 = f"{t['txt_total_decodes']}: {int(df_seg['spot_count'].sum())}  |  {t['txt_remote']} {remote_str}: {len(df_seg)}"

        station_col = t['tbl_col_rx'] if analysis_id.startswith("TX") else t['tbl_col_tx']
        station_type = t['tbl_col_rx'] if analysis_id.startswith("TX") else t['tbl_col_tx']
        toggle_key = f"tgl_{analysis_id}_{run_id}_{selected_seg}"
        view_defaults = st.session_state.get("demo_view_defaults", {})
        if "show_non_joint" in view_defaults and view_defaults.get("show_non_joint") is not None:
            default_state = bool(view_defaults.get("show_non_joint"))
        else:
            default_state = has_non_joint_rows and not has_joint_rows
        show_non_joint = st.session_state.get(toggle_key, default_state) if is_compare else False

        if not is_compare:
            disp_df = df_seg[['peer_sign', 'peer_grid', 'calc_dist', 'calc_azimuth', 'spot_count', 'stat_val']].copy()
            disp_df.columns = [station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], t['tbl_col_spots'], t['tbl_col_med_snr']]
            col_joint_name = None
        else:
            if is_sequential:
                col_joint_name = t.get('tbl_col_joint_bins', 'Joint Bins')
                disp_df = df_seg[['peer_sign', 'peer_grid', 'calc_dist', 'calc_azimuth', 'joint_bins_count', 'count_only_u', 'count_only_r', 'stat_val']].copy()
            else:
                col_joint_name = t['tbl_col_joint']
                disp_df = df_seg[['peer_sign', 'peer_grid', 'calc_dist', 'calc_azimuth', 'spot_count', 'count_only_u', 'count_only_r', 'stat_val']].copy()

            disp_df.columns = [station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], col_joint_name, t['tbl_col_only_u'].format(callsign=col_u_name), lbl_only_ref, t['tbl_col_med_delta']]

        km_col = t['tbl_col_km']
        az_col = t['tbl_col_az']
        disp_df[km_col] = disp_df[km_col].round(0).astype('Int64')
        disp_df[az_col] = disp_df[az_col].round(1)

        metric_col = disp_df.columns[-1]
        disp_df[metric_col] = pd.to_numeric(disp_df[metric_col], errors='coerce').round(1)
        if is_compare:
            sort_cols = [col_joint_name, metric_col] if col_joint_name != metric_col else [col_joint_name]
        else:
            sort_cols = [t['tbl_col_spots'], metric_col] if t['tbl_col_spots'] != metric_col else [t['tbl_col_spots']]

        full_segment_disp_df = disp_df.sort_values(by=sort_cols, ascending=[False] * len(sort_cols), na_position='last').reset_index(drop=True)

        if is_compare and not show_non_joint and col_joint_name in disp_df.columns:
            disp_df = disp_df[disp_df[col_joint_name] > 0]

        sorted_disp_df = disp_df.sort_values(by=sort_cols, ascending=[False] * len(sort_cols), na_position='last').reset_index(drop=True)
        disp_df = sorted_disp_df.copy()

        evidence_meta_df = sorted_disp_df
        if is_compare and col_joint_name in sorted_disp_df.columns:
            evidence_meta_df = sorted_disp_df[sorted_disp_df[col_joint_name] > 0]
        evidence_meta_df = evidence_meta_df[[station_col, t['tbl_col_loc']]].copy()
        evidence_meta_df.columns = ["peer_sign", "peer_grid"]

        # ----------------------------------------------------
        # Render Histogram & Yield Chart
        # ----------------------------------------------------
        has_plot_data = False
        if not vals.empty: 
            has_plot_data = True
        elif is_compare and 'count_only_u' in df_seg.columns and (df_seg['count_only_u'].sum() > 0 or df_seg['count_only_r'].sum() > 0): 
            has_plot_data = True

        segment_evidence_df = _empty_evidence_df()
        segment_raw_values = pd.Series(dtype=float)
        station_stability_interval = (np.nan, np.nan, np.nan)
        spot_stability_interval = (np.nan, np.nan, np.nan)
        stability_lookup = {}
        segment_figure_recipe = None
        selected_evidence_export = None
        selected_station_labels = []
        drilldown_selected_df = pd.DataFrame()
        all_drilldown_context = None

        if has_plot_data:
            segment_evidence_df = _build_segment_evidence_points(evidence_meta_df, parquet_path, is_compare, is_sequential)
            segment_raw_values = segment_evidence_df["metric"] if not segment_evidence_df.empty else pd.Series(dtype=float)
            stability_result = _cached_segment_stability(
                (run_id, analysis_id, selected_seg),
                vals,
                segment_evidence_df,
            )
            station_stability_interval = stability_result["station_interval"]
            spot_stability_interval = stability_result["spot_interval"]
            stability_lookup = stability_result["station_lookup"]
            compare_layout = is_compare and 'count_only_u' in df_seg.columns
            if compare_layout:
                # System Sensitivity (Yield) counts unique stations, not spots.
                cnt_joint = len(df_seg[df_seg['spot_count'] > 0])
                cnt_async = len(df_seg[(df_seg['spot_count'] == 0) & (df_seg['count_only_u'] > 0) & (df_seg['count_only_r'] > 0)])
                cnt_u = len(df_seg[(df_seg['spot_count'] == 0) & (df_seg['count_only_u'] > 0) & (df_seg['count_only_r'] == 0)])
                cnt_r = len(df_seg[(df_seg['spot_count'] == 0) & (df_seg['count_only_u'] == 0) & (df_seg['count_only_r'] > 0)])
                joint_lbl = t.get('tbl_col_joint_bins', 'Joint Bins') if is_sequential else t.get('tbl_col_joint', 'Joint')
                async_lbl = t.get('leg_both_async', 'Both (Async)')
                segment_panel_counts = [cnt_u, cnt_joint, cnt_async, cnt_r]
                segment_panel_labels = [col_u_name, joint_lbl, async_lbl, yield_ref_header]
                segment_panel_y_label = t["lbl_hist_count"]
            else:
                segment_panel_counts = [len(df_seg), int(df_seg['spot_count'].sum())]
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
            fig_hist = render_segment_insight_export_figure(segment_figure_recipe)

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
            st.markdown(
                f"<div style='text-align:center; color:white; font-size:0.95rem; margin-top:-0.25rem; margin-bottom:1.0rem;'>{'<br>'.join(segment_summary)}</div>",
                unsafe_allow_html=True
            )

            st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
            # Richtiges Streamlit-Parameter f??r volle Breite
            st.pyplot(fig_hist, width='stretch')
            plt.close(fig_hist)
        else:
            st.info(t["lbl_no_joint"], icon="??????")
            st.markdown(f"<div style='font-size:11px; color:#ccc; margin-bottom:1rem; font-family:monospace;'>{line1_str}<br>{seg_line2}</div>", unsafe_allow_html=True)

        stability_col = t.get("tbl_col_stability", "90% Stability")
        if not segment_evidence_df.empty and not sorted_disp_df.empty:
            row_identity = (
                sorted_disp_df[station_col].astype(str) +
                " (" + sorted_disp_df[t['tbl_col_loc']].astype(str) + ")"
            )
            formatted_stability_lookup = {
                identity: _format_stability_interval(low, high, is_compare)
                for identity, (low, high) in stability_lookup.items()
            }
            sorted_disp_df[stability_col] = row_identity.map(formatted_stability_lookup).fillna("n/a")

        # --- 1. Layout-Spalten definieren ---
        # 3 Spalten: 50% f??r Titel, 30% f??r Toggle, 20% f??r Filter-Button
        col_ins1, col_ins2, col_ins3 = st.columns([0.6, 0.3, 0.3], vertical_alignment="center")
        
        with col_ins1:
            # Platzsparende, zweisprachige Kurzform f??r den Subtitel
            sub_text = " (Norm. @ 1W. Details per Klick)" if st.session_state.lang == "de" else " (Norm. @ 1W. Click for details)"
            st.markdown(f"**<span class='material-symbols-rounded section-icon'>monitoring</span>{t['lbl_insights']}**<span style='font-size:0.85em; color:gray;'>{sub_text}</span>", unsafe_allow_html=True)
            
        with col_ins2:
            if is_compare:
                # Default to showing non-joint rows only when the selected segment has no joint
                # evidence but does contain target-only, reference-only, or async-both evidence.
                show_non_joint = st.toggle("Show Non-Joint", value=default_state, key=toggle_key)

        # --- DYNAMIC EXCEL-STYLE FILTER ---
        # Da wir sorted_disp_df jetzt vorbereitet haben, springen wir zur??ck in Spalte 3 f??r den Button
        with col_ins3:
            # Dezenter Button mit nativem Material-Design Trichter-Icon!
            with st.popover("Filter", icon=":material/filter_alt:", use_container_width=True):
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
        tbl_key = f"tbl_{analysis_id}_{run_id}_{selected_seg}"
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
                station_df = _load_station_rows_for_drilldown(
                    parquet_path,
                    selected_meta_df,
                    station_col,
                    loc_col
                )
                selected_evidence_export = _render_selected_station_evidence(station_df, selected_identity_df, is_compare, is_sequential)
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
                )

                if info_msg:
                    st.info(info_msg, icon=":material/info:")
                elif drill_df is not None and not drill_df.empty:
                    drilldown_selected_df = _render_drilldown_dataframe(
                        drill_df,
                        drill_title,
                        analysis_id,
                        run_id,
                        selected_seg,
                        t,
                        is_compare,
                    )

            except FileNotFoundError: 
                st.warning("Cache file expired. Please Run Analysis again.")

        register_inspector_export(
            analysis_id=analysis_id,
            selected_segment=selected_seg,
            selected_distance=sel_dist if sel_dist != opt_full else opt_full,
            selected_direction=sel_dir if sel_dir != opt_all_dir else opt_all_dir,
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
