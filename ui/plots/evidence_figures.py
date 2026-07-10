"""Matplotlib evidence and Segment Insight figures for WSPRadar."""

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.dates as mdates

from config import APP_VERSION
from core.matplotlib_runtime import create_agg_figure, synchronized_matplotlib
from core.solar_path import ILLUMINATION_CLASSES
from core.stability import (
    _expanded_metric_limits,
    _metric_histogram_bins,
    _metric_values,
)

EVIDENCE_COLORS = ["#36aaf9", "#ffbe33", "#72fe5e", "#cc00ff", "#f66b19"]
EVIDENCE_AGG_COLOR = "#36aaf9"
EVIDENCE_SEPARATE_STATION_LIMIT = 5
STABILITY_LINE_THRESHOLD_DB = 0.1
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

def _default_evidence_labels(is_compare):
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

def _add_horizontal_grid(ax):
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)

def _add_foreground_horizontal_grid(ax):
    ax.set_axisbelow(False)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA, zorder=3)

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

def _draw_stacked_vertical_metric_histogram(ax, grouped_values, colors):
    """Draw a percent histogram split by observation classes."""
    cleaned = {
        key: _metric_values(values)
        for key, values in grouped_values.items()
    }
    all_values = np.concatenate([values for values in cleaned.values() if len(values)]) if cleaned else np.asarray([])
    if len(all_values) == 0:
        return np.nan

    edges, centers, bin_width = _metric_histogram_bins(all_values)
    total_count = float(len(all_values))
    bottom = np.zeros(len(centers), dtype=float)
    for key in ILLUMINATION_CLASSES:
        values = cleaned.get(key, np.asarray([]))
        if len(values) == 0:
            continue
        counts, _ = np.histogram(values, bins=edges)
        shares = 100.0 * counts.astype(float) / total_count
        ax.bar(
            centers,
            shares,
            bottom=bottom,
            width=bin_width * 0.82,
            color=colors.get(key, "#36aaf9"),
            alpha=0.80,
            edgecolor="#111111",
            linewidth=0.45,
            align="center",
            zorder=2,
        )
        bottom += shares

    ax.set_ylabel("Share (%)", color="white")
    ax.set_ylim(bottom=0.0)
    ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=6))
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=5))
    ax.grid(axis="x", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=0.20)
    return float(np.median(all_values))

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

@synchronized_matplotlib
def _create_selected_station_evidence_figure(plot_df, evidence_title, labels, time_agg, is_compare, is_sequential):
    """Build the selected-station evidence figure for UI or lazy export rendering."""
    evidence_count = len(plot_df)
    fig_ev = create_agg_figure(figsize=(13, 5.6), facecolor="black")
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
    if recipe.get("kind") == "opportunity":
        from ui.plots.opportunity_figures import _render_opportunity_selected_figure
        return _render_opportunity_selected_figure(recipe)
    plot_df = pd.DataFrame({
        "plot_time": pd.to_datetime(np.asarray(recipe.get("plot_time_ns", []), dtype=np.int64), unit="ns", utc=True),
        "metric": np.asarray(recipe.get("metric", []), dtype=float),
    })
    if plot_df.empty:
        return None
    labels = recipe.get("labels")
    if not labels:
        labels = _default_evidence_labels(bool(recipe.get("is_compare")))
    return _create_selected_station_evidence_figure(
        plot_df,
        recipe.get("title", "Selected Station Evidence"),
        labels,
        recipe.get("time_bin", "3h"),
        bool(recipe.get("is_compare")),
        bool(recipe.get("is_sequential")),
    )

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

@synchronized_matplotlib
def render_segment_insight_export_figure(recipe):
    """Rebuild the Segment Insight figure only when preparing the results ZIP."""
    if not recipe:
        return None
    if recipe.get("kind") == "opportunity":
        from ui.plots.opportunity_figures import _render_opportunity_segment_figure
        return _render_opportunity_segment_figure(recipe)

    is_compare = bool(recipe.get("is_compare"))
    is_sequential = bool(recipe.get("is_sequential"))
    compare_layout = bool(recipe.get("compare_layout"))
    station_values = np.asarray(recipe.get("station_values", []), dtype=float)
    spot_values = np.asarray(recipe.get("spot_values", []), dtype=float)
    station_interval = recipe.get("station_interval", (np.nan, np.nan, np.nan))
    spot_interval = recipe.get("spot_interval", (np.nan, np.nan, np.nan))
    panel_counts = list(recipe.get("panel_counts", []))
    panel_labels = list(recipe.get("panel_labels", []))

    fig_hist = create_agg_figure(figsize=(13, 5.6), facecolor="black")
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
