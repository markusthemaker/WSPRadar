"""Matplotlib evidence and Segment Insight figures for WSPRadar."""

from dataclasses import dataclass
import textwrap

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.dates as mdates

from config import APP_VERSION
from core.matplotlib_runtime import create_agg_figure, synchronized_matplotlib
from core.evidence_statistics import (
    _expanded_metric_limits,
    _format_metric_signed,
    _metric_histogram_bins,
    _metric_values,
)

EVIDENCE_AGG_COLOR = "#36aaf9"
STATION_EVIDENCE_HATCH = "//////"
SEGMENT_FIGURE_BOTTOM = 0.15
SEGMENT_FIGURE_FOOTER_Y = 0.055
SEGMENT_TEMPORAL_FIGURE_SIZE_INCHES = (13.0, 5.6)
SEGMENT_TEMPORAL_FIGURE_LEFT = 0.07
SEGMENT_TEMPORAL_FIGURE_RIGHT = 0.95
SEGMENT_TEMPORAL_FIGURE_TOP = 0.82
SEGMENT_TEMPORAL_COLUMN_WIDTH_RATIOS = (1.95, 1.0)
SEGMENT_TEMPORAL_COLUMN_SPACE = 0.20
SEGMENT_TEMPORAL_COLORBAR_PAD = 0.012
SEGMENT_TEMPORAL_COLORBAR_FRACTION = 0.03
EVIDENCE_TIME_AGG_PRESETS = [
    (pd.Timedelta(hours=6), ["5m", "15m", "30m", "1h", "3h"], "15m"),
    (pd.Timedelta(hours=24), ["15m", "30m", "1h", "3h", "6h"], "30m"),
    (pd.Timedelta(days=7), ["1h", "2h", "3h", "6h", "12h", "24h"], "3h"),
    (None, ["1h", "2h", "3h", "6h", "12h", "24h"], "6h"),
]
EVIDENCE_HEATMAP_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "wspr_evidence_heatmap",
    ["#1849a9", "#00b050", "#ffb000", "#d7191c"]
)
EVIDENCE_HEATMAP_CMAP.set_bad((0, 0, 0, 0))
EVIDENCE_DENSITY_MIN = 0.0
EVIDENCE_DENSITY_MAX = 100.0
TEMPORAL_MEDIAN_LINK_MIN_COUNT = 3
FOLDED_UTC_UNAVAILABLE_WRAP_WIDTH = 34
FOLDED_UTC_UNAVAILABLE_DETAIL_WRAP_WIDTH = 30
GRID_COLOR = "#777777"
GRID_LINEWIDTH = 1.0
GRID_ALPHA = 0.35
TEMPORAL_GUIDE_COLOR = "#d0d0d0"
TEMPORAL_ZERO_LINE_COLOR = "#f4f1e8"
TEMPORAL_ZERO_UNDERSTROKE_COLOR = "#050505"
METRIC_MEDIAN_COLOR = "red"
METRIC_MEDIAN_LINESTYLE = "dashed"
METRIC_MEDIAN_LINEWIDTH = 1.0
METRIC_LEGEND_FONTSIZE = 8
METRIC_ANNOTATION_FONTSIZE = 8
METRIC_AXIS_LABEL_FONTSIZE = 10
METRIC_TICK_LABEL_FONTSIZE = 9
METRIC_PANEL_TITLE_FONTSIZE = 12
METRIC_FIGURE_TITLE_FONTSIZE = 14
METRIC_FOOTER_FONTSIZE = 10
METRIC_FONT_FAMILY = "sans-serif"
METRIC_FOREGROUND_ZORDER = 10
COMPARE_MEDIAN_FOCUS_TIGHT_MAX_DEVIATION_DB = 10.0
COMPARE_MEDIAN_FOCUS_MIN_HALF_SPAN_DB = 3.0
COMPARE_MEDIAN_FOCUS_LIMIT_PADDING = 1.02
COMPARE_MEDIAN_FOCUS_TIGHT_ANCHORS_DB = (0.0, 1.0, 3.0, 6.0, 10.0, 20.0, 40.0)
COMPARE_MEDIAN_FOCUS_TIGHT_LABELS_DB = (0.0, 1.0, 3.0, 6.0, 10.0)
COMPARE_MEDIAN_FOCUS_BROAD_ANCHORS_DB = (0.0, 3.0, 6.0, 10.0, 20.0, 30.0, 60.0)
COMPARE_MEDIAN_FOCUS_BROAD_LABELS_DB = (0.0, 3.0, 6.0, 10.0, 20.0, 30.0)


@dataclass(frozen=True)
class _CompareMedianFocusSpec:
    """Describe one shared absolute-dB axis focused around a Compare median."""

    median_db: float
    anchor_offsets_db: tuple[float, ...]
    labelled_offsets_db: tuple[float, ...]
    half_span_db: float

    @property
    def lower_limit_db(self):
        """Return the symmetric lower absolute-dB display limit."""
        return self.median_db - self.half_span_db

    @property
    def upper_limit_db(self):
        """Return the symmetric upper absolute-dB display limit."""
        return self.median_db + self.half_span_db

    @property
    def tick_values_db(self):
        """Return ordered absolute-dB ticks derived from signed focus offsets."""
        positive_offsets = tuple(
            offset_db
            for offset_db in self.labelled_offsets_db
            if offset_db > 0.0 and offset_db <= self.half_span_db
        )
        signed_offsets = (
            tuple(-offset_db for offset_db in reversed(positive_offsets))
            + (0.0,)
            + positive_offsets
        )
        return tuple(self.median_db + offset_db for offset_db in signed_offsets)


def _piecewise_linear_with_tail(values, input_points, output_points):
    """Interpolate finite values and extrapolate beyond the final focus anchor."""
    numeric_values = np.asarray(values, dtype=float)
    flat_values = numeric_values.reshape(-1)
    transformed_values = flat_values.copy()
    finite_mask = np.isfinite(flat_values)
    if finite_mask.any():
        finite_values = flat_values[finite_mask]
        interpolated = np.interp(finite_values, input_points, output_points)
        tail_mask = finite_values > input_points[-1]
        if tail_mask.any():
            tail_slope = (
                (output_points[-1] - output_points[-2])
                / (input_points[-1] - input_points[-2])
            )
            interpolated[tail_mask] = output_points[-1] + (
                finite_values[tail_mask] - input_points[-1]
            ) * tail_slope
        transformed_values[finite_mask] = interpolated
    return transformed_values.reshape(numeric_values.shape)


def _compare_median_focus_forward(values, spec):
    """Map absolute Delta-SNR values to signed equal-anchor display coordinates."""
    numeric_values = np.asarray(values, dtype=float)
    offsets_db = numeric_values - spec.median_db
    offset_signs = np.sign(offsets_db)
    anchor_offsets = np.asarray(spec.anchor_offsets_db, dtype=float)
    anchor_positions = np.arange(len(anchor_offsets), dtype=float)
    magnitudes = _piecewise_linear_with_tail(
        np.abs(offsets_db),
        anchor_offsets,
        anchor_positions,
    )
    return offset_signs * magnitudes


def _compare_median_focus_inverse(values, spec):
    """Return absolute Delta-SNR values from signed focus coordinates."""
    numeric_values = np.asarray(values, dtype=float)
    coordinate_signs = np.sign(numeric_values)
    anchor_offsets = np.asarray(spec.anchor_offsets_db, dtype=float)
    anchor_positions = np.arange(len(anchor_offsets), dtype=float)
    magnitudes_db = _piecewise_linear_with_tail(
        np.abs(numeric_values),
        anchor_positions,
        anchor_offsets,
    )
    return spec.median_db + coordinate_signs * magnitudes_db


def _build_compare_median_focus_spec(values):
    """
    Build a display-only Compare scale from raw evidence values.

    The exact evidence median is the center. Raw histogram and integer heatmap
    bin edges, plus absolute zero, determine a symmetric non-clipping span. A
    tight ham-radio anchor profile is used only when every required deviation
    is at most 10 dB; otherwise the broad 3/6/10/20/30 dB profile is used.
    """
    metric_values = _metric_values(values)
    if len(metric_values) == 0:
        return None

    median_db = float(np.median(metric_values))
    histogram_edges, _, _ = _metric_histogram_bins(metric_values)
    rounded_metric_bins = np.rint(metric_values)
    lower_bound_db = min(
        float(np.min(metric_values)),
        float(histogram_edges[0]),
        float(np.min(rounded_metric_bins) - 0.5),
        0.0,
    )
    upper_bound_db = max(
        float(np.max(metric_values)),
        float(histogram_edges[-1]),
        float(np.max(rounded_metric_bins) + 0.5),
        0.0,
    )
    required_deviation_db = max(
        median_db - lower_bound_db,
        upper_bound_db - median_db,
        COMPARE_MEDIAN_FOCUS_MIN_HALF_SPAN_DB,
    )

    if required_deviation_db <= COMPARE_MEDIAN_FOCUS_TIGHT_MAX_DEVIATION_DB:
        anchor_offsets_db = COMPARE_MEDIAN_FOCUS_TIGHT_ANCHORS_DB
        labelled_offsets_db = COMPARE_MEDIAN_FOCUS_TIGHT_LABELS_DB
    else:
        anchor_offsets_db = COMPARE_MEDIAN_FOCUS_BROAD_ANCHORS_DB
        labelled_offsets_db = COMPARE_MEDIAN_FOCUS_BROAD_LABELS_DB

    containing_label_offset = next(
        (
            offset_db
            for offset_db in labelled_offsets_db[1:]
            if offset_db >= required_deviation_db
        ),
        None,
    )
    if containing_label_offset is None:
        half_span_db = required_deviation_db * COMPARE_MEDIAN_FOCUS_LIMIT_PADDING
    else:
        half_span_db = containing_label_offset * COMPARE_MEDIAN_FOCUS_LIMIT_PADDING

    extended_anchors = list(anchor_offsets_db)
    while extended_anchors[-1] <= half_span_db:
        extended_anchors.append(extended_anchors[-1] * 2.0)

    return _CompareMedianFocusSpec(
        median_db=median_db,
        anchor_offsets_db=tuple(float(value) for value in extended_anchors),
        labelled_offsets_db=tuple(float(value) for value in labelled_offsets_db),
        half_span_db=float(half_span_db),
    )


def _compare_median_focus_recipe(spec):
    """Serialize a focus specification into a compact figure-recipe mapping."""
    if spec is None:
        return None
    return {
        "median_db": float(spec.median_db),
        "anchor_offsets_db": [float(value) for value in spec.anchor_offsets_db],
        "labelled_offsets_db": [float(value) for value in spec.labelled_offsets_db],
        "half_span_db": float(spec.half_span_db),
    }


def _compare_median_focus_spec_from_recipe(recipe, fallback_values):
    """Validate a stored focus mapping or derive one from the supplied evidence."""
    if isinstance(recipe, dict):
        try:
            median_db = float(recipe["median_db"])
            anchor_offsets_db = tuple(
                float(value) for value in recipe["anchor_offsets_db"]
            )
            labelled_offsets_db = tuple(
                float(value) for value in recipe["labelled_offsets_db"]
            )
            half_span_db = float(recipe["half_span_db"])
            is_valid = (
                np.isfinite(median_db)
                and np.isfinite(half_span_db)
                and half_span_db > 0.0
                and len(anchor_offsets_db) >= 2
                and anchor_offsets_db[0] == 0.0
                and all(
                    np.isfinite(value) and value >= 0.0
                    for value in anchor_offsets_db
                )
                and all(
                    upper > lower
                    for lower, upper in zip(
                        anchor_offsets_db,
                        anchor_offsets_db[1:],
                    )
                )
                and labelled_offsets_db
                and labelled_offsets_db[0] == 0.0
                and all(
                    upper > lower
                    for lower, upper in zip(
                        labelled_offsets_db,
                        labelled_offsets_db[1:],
                    )
                )
                and all(
                    value in anchor_offsets_db for value in labelled_offsets_db
                )
            )
            if is_valid:
                return _CompareMedianFocusSpec(
                    median_db=median_db,
                    anchor_offsets_db=anchor_offsets_db,
                    labelled_offsets_db=labelled_offsets_db,
                    half_span_db=half_span_db,
                )
        except (KeyError, TypeError, ValueError):
            pass
    return _build_compare_median_focus_spec(fallback_values)

def _add_horizontal_grid(ax):
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)

def _format_absolute_delta_tick(value_db, median_db):
    """Format one absolute Delta-SNR tick and mark the focus median with M."""
    value_db = float(value_db)
    rounded_value = round(value_db)
    if np.isclose(value_db, rounded_value, atol=1e-9):
        if rounded_value > 0:
            numeric_label = f"+{int(rounded_value)}"
        elif rounded_value < 0:
            numeric_label = f"\u2212{abs(int(rounded_value))}"
        else:
            numeric_label = "0"
    else:
        numeric_label = (
            f"+{value_db:.1f}"
            if value_db > 0.0
            else f"\u2212{abs(value_db):.1f}"
        )
    if np.isclose(value_db, median_db, atol=1e-9):
        return f"{numeric_label} M"
    return numeric_label


def _add_metric_median_reference(
    ax,
    median_db,
    *,
    orientation,
    label,
    zorder=4.0,
    gid=None,
):
    """Draw and return one consistently styled horizontal or vertical median."""
    line_label = f"{label} {_format_metric_signed(float(median_db), True)} dB"
    line_kwargs = {
        "color": METRIC_MEDIAN_COLOR,
        "linestyle": METRIC_MEDIAN_LINESTYLE,
        "linewidth": METRIC_MEDIAN_LINEWIDTH,
        "alpha": 1.0,
        "zorder": zorder,
        "label": line_label,
    }
    if orientation == "horizontal":
        median_line = ax.axhline(float(median_db), **line_kwargs)
    elif orientation == "vertical":
        median_line = ax.axvline(float(median_db), **line_kwargs)
    else:
        raise ValueError(f"Unsupported median-reference orientation: {orientation}")
    if gid is not None:
        median_line.set_gid(gid)
    return median_line


def _add_compare_absolute_zero_reference(ax, spec):
    """Retain the raw zero-dB equality reference on a median-focused axis."""
    if not spec.lower_limit_db <= 0.0 <= spec.upper_limit_db:
        return

    zero_understroke = ax.axhline(
        0.0,
        color=TEMPORAL_ZERO_UNDERSTROKE_COLOR,
        linestyle="--",
        linewidth=1.7,
        alpha=0.92,
        zorder=2.9,
    )
    zero_understroke.set_gid("compare-temporal-zero-understroke")
    zero_line = ax.axhline(
        0.0,
        color=TEMPORAL_ZERO_LINE_COLOR,
        linestyle="--",
        linewidth=0.85,
        alpha=0.98,
        zorder=3.0,
    )
    zero_line.set_gid("compare-temporal-zero-line")

    if not any(np.isclose(tick_db, 0.0) for tick_db in spec.tick_values_db):
        zero_label = ax.text(
            0.99,
            0.0,
            "0 dB",
            transform=ax.get_yaxis_transform(),
            color=TEMPORAL_ZERO_LINE_COLOR,
            fontsize=8,
            ha="right",
            va="bottom",
            zorder=6,
            bbox={
                "boxstyle": "square,pad=0.12",
                "facecolor": "black",
                "edgecolor": "none",
                "alpha": 0.58,
            },
        )
        zero_label.set_gid("compare-temporal-zero-label")


def _apply_compare_median_focus_axis(
    ax,
    spec,
    *,
    axis_label,
    median_label,
    show_median_legend=True,
    draw_median_reference=True,
):
    """
    Apply a shared median-focused transform while retaining absolute dB labels.

    Statistical values, histogram bins, heatmap cells, and artist coordinates
    remain in raw dB. Only Matplotlib's data-to-display mapping is nonlinear.
    """
    if spec is None:
        return

    forward = lambda values: _compare_median_focus_forward(values, spec)
    inverse = lambda values: _compare_median_focus_inverse(values, spec)
    ax.set_yscale("function", functions=(forward, inverse))
    ax.set_ylim(spec.lower_limit_db, spec.upper_limit_db)
    ax.grid(axis="y", visible=False)
    ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(spec.tick_values_db))
    ax.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(
            lambda value_db, _position: _format_absolute_delta_tick(
                value_db,
                spec.median_db,
            )
        )
    )
    ax.set_ylabel(axis_label, color="white")

    median_reference_line = None
    for tick_db in spec.tick_values_db:
        is_median = np.isclose(tick_db, spec.median_db)
        if np.isclose(tick_db, 0.0) and not is_median:
            continue
        if is_median and not draw_median_reference:
            continue
        if is_median:
            median_reference_line = _add_metric_median_reference(
                ax,
                spec.median_db,
                orientation="horizontal",
                label=median_label,
                zorder=3.2,
                gid="compare-median-focus-center",
            )
            continue
        guide_line = ax.axhline(
            tick_db,
            color=TEMPORAL_GUIDE_COLOR,
            linestyle="-",
            linewidth=0.9,
            alpha=0.42,
            zorder=2.6,
        )
        guide_line.set_gid("compare-median-focus-guide")

    _add_compare_absolute_zero_reference(ax, spec)
    if show_median_legend and median_reference_line is not None:
        legend_handles = [median_reference_line]
        bin_median_markers = next(
            (
                collection
                for collection in ax.collections
                if collection.get_gid() == "temporal-bin-median-markers"
            ),
            None,
        )
        if bin_median_markers is not None:
            legend_handles.append(bin_median_markers)
        _place_metric_legend_top_right(ax, handles=legend_handles)

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

def _place_metric_legend(
    legend_owner,
    *,
    loc,
    handles=None,
    labels=None,
    fontsize=METRIC_LEGEND_FONTSIZE,
    gid="metric-evidence-legend",
    **layout_kwargs,
):
    """Place a shared foreground evidence legend on an Axes or Figure."""
    legend_kwargs = {
        "loc": loc,
        "ncol": 1,
        "facecolor": "#121212",
        "edgecolor": "#444444",
        "labelcolor": "white",
        "fontsize": fontsize,
        "framealpha": 0.9,
        "markerfirst": True,
        **layout_kwargs,
    }
    if handles is not None:
        legend_kwargs["handles"] = handles
    if labels is not None:
        legend_kwargs["labels"] = labels
    legend = legend_owner.legend(**legend_kwargs)
    for legend_text in legend.get_texts():
        legend_text.set_fontfamily(METRIC_FONT_FAMILY)
        legend_text.set_fontweight("normal")
    legend.set_gid(gid)
    legend.set_zorder(METRIC_FOREGROUND_ZORDER)
    return legend


def _place_metric_legend_top_right(ax, *, handles=None):
    """Place a shared metric legend in the conventional upper-right position."""
    return _place_metric_legend(
        ax,
        handles=handles,
        loc="upper right",
        borderaxespad=0.0,
        gid="compare-metric-summary-legend",
    )


def _set_temporal_panel_title(ax, title, *, y=None, pad=10):
    """Apply the panel-title typography shared by temporal evidence figures."""
    title_properties = {
        "color": "white",
        "fontweight": "bold",
        "fontfamily": METRIC_FONT_FAMILY,
        "pad": pad,
    }
    if y is not None:
        title_properties["y"] = y
    return ax.set_title(str(title), **title_properties)


def _format_temporal_time_bin_label(time_bin):
    """Format a compact hourly time-bin token for temporal panel copy."""
    compact_label = str(time_bin).strip()
    if compact_label.endswith("h") and compact_label[:-1].isdigit():
        return f"{compact_label[:-1]} h"
    return compact_label


def _place_temporal_panel_subtitle(
    axis,
    subtitle,
    *,
    gid="temporal-panel-subtitle",
    y=1.01,
):
    """Place one localized subtitle using the shared temporal typography."""
    subtitle_artist = axis.text(
        0.5,
        float(y),
        str(subtitle),
        transform=axis.transAxes,
        color="white",
        fontsize=METRIC_LEGEND_FONTSIZE,
        fontweight="normal",
        fontfamily=METRIC_FONT_FAMILY,
        ha="center",
        va="bottom",
        wrap=True,
    )
    subtitle_artist.set_gid(gid)
    return subtitle_artist


def _set_temporal_panel_title_with_subtitle(
    axis,
    title,
    subtitle,
    *,
    subtitle_gid="temporal-panel-subtitle",
):
    """Apply the title/subtitle hierarchy shared by temporal metric panels."""
    title_artist = _set_temporal_panel_title(
        axis,
        title,
        y=1.06,
        pad=0,
    )
    title_artist.set_wrap(True)
    _place_temporal_panel_subtitle(
        axis,
        subtitle,
        gid=subtitle_gid,
    )
    return title_artist


def _set_metric_axis_labels(
    ax,
    *,
    x_label=None,
    y_label=None,
    x_color="white",
    y_color="white",
):
    """Apply the shared evidence typography to optional x and y axis labels."""
    text_properties = {
        "fontsize": METRIC_AXIS_LABEL_FONTSIZE,
        "fontfamily": METRIC_FONT_FAMILY,
        "fontweight": "normal",
    }
    if x_label is not None:
        ax.set_xlabel(x_label, color=x_color, **text_properties)
    if y_label is not None:
        ax.set_ylabel(y_label, color=y_color, **text_properties)


def _add_metric_mean_annotation(ax, mean_db, *, label):
    """Place one signed arithmetic-mean summary at the lower-right foreground."""
    mean_annotation = ax.text(
        0.98,
        0.04,
        f"{label} {_format_metric_signed(mean_db, True)} dB",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color="#cccccc",
        fontsize=METRIC_ANNOTATION_FONTSIZE,
        zorder=METRIC_FOREGROUND_ZORDER,
        bbox={
            "boxstyle": "square,pad=0.15",
            "facecolor": "#121212",
            "edgecolor": "none",
            "alpha": 0.82,
        },
    )
    mean_annotation.set_gid("compare-metric-mean")
    return mean_annotation

def _style_evidence_axis(ax):
    ax.set_facecolor("black")
    ax.tick_params(colors="white")
    _add_horizontal_grid(ax)
    for spine in ax.spines.values():
        spine.set_color("#444444")

def _draw_vertical_metric_histogram(
    ax,
    values,
    color="#36aaf9",
    *,
    share_axis_label,
    hatch=None,
    artist_gid=None,
):
    """Draw a conventional horizontal-metric histogram and return its median."""
    values = _metric_values(values)
    if len(values) == 0:
        return np.nan

    edges, centers, bin_width = _metric_histogram_bins(values)
    counts, _ = np.histogram(values, bins=edges)
    if counts.sum() == 0:
        return np.nan

    shares = 100.0 * counts.astype(float) / float(counts.sum())
    rectangles = ax.bar(
        centers,
        shares,
        width=bin_width * 0.82,
        facecolor="none" if hatch else color,
        alpha=1.0 if hatch else 0.70,
        edgecolor=color if hatch else "#67c4ff",
        hatch=hatch,
        linewidth=0.7,
        align="center",
        zorder=2
    )
    if artist_gid:
        for rectangle in rectangles:
            rectangle.set_gid(artist_gid)
    ax.set_ylabel(share_axis_label, color="white")
    ax.set_ylim(bottom=0.0)
    ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=6))
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=5))
    ax.grid(axis="x", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=0.20)
    return float(np.median(values))

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


def _prepare_temporal_metric_rows(plot_df):
    """Return finite evidence rows with naive UTC plot times and integer metric bins."""
    if plot_df is None or plot_df.empty or not {"plot_time", "metric"}.issubset(plot_df.columns):
        return pd.DataFrame(columns=["plot_time", "metric", "metric_bin"])

    work_df = plot_df[["plot_time", "metric"]].copy()
    work_df["plot_time"] = (
        pd.to_datetime(work_df["plot_time"], errors="coerce", utc=True)
        .dt.tz_convert(None)
    )
    work_df["metric"] = pd.to_numeric(work_df["metric"], errors="coerce")
    work_df = work_df[
        work_df["plot_time"].notna()
        & work_df["metric"].notna()
        & np.isfinite(work_df["metric"])
    ].copy()
    if work_df.empty:
        work_df["metric_bin"] = pd.Series(dtype="int64")
        return work_df

    work_df["metric_bin"] = work_df["metric"].round().astype(int)
    return work_df


def _temporal_utc_date_count(work_df):
    """Count distinct UTC calendar dates represented by finite evidence rows."""
    if work_df is None or work_df.empty:
        return 0
    return int(work_df["plot_time"].dt.normalize().nunique())


def _relative_density_values(count_grid):
    """Scale one count grid so its densest populated cell equals 100 percent."""
    count_values = np.asarray(count_grid, dtype=float)
    if count_values.size == 0:
        return np.ma.masked_array(count_values, mask=np.ones_like(count_values, dtype=bool))
    maximum_count = float(np.nanmax(count_values))
    if not np.isfinite(maximum_count) or maximum_count <= 0.0:
        return np.ma.masked_array(count_values, mask=np.ones_like(count_values, dtype=bool))
    relative_values = EVIDENCE_DENSITY_MAX * count_values / maximum_count
    return np.ma.masked_where(count_values <= 0.0, relative_values)


def _draw_relative_density_mesh(ax, x_edges, y_edges, count_grid, *, density_norm=None):
    """Draw a zero-masked relative-density mesh with a fixed 0-to-100 scale."""
    if density_norm is None:
        density_norm = mpl.colors.Normalize(
            vmin=EVIDENCE_DENSITY_MIN,
            vmax=EVIDENCE_DENSITY_MAX,
        )
    return ax.pcolormesh(
        x_edges,
        y_edges,
        _relative_density_values(count_grid),
        cmap=EVIDENCE_HEATMAP_CMAP,
        norm=density_norm,
        shading="flat",
        zorder=1,
    )


def _draw_temporal_median_overlay(
    ax,
    x_centers,
    median_df,
    *,
    label,
):
    """Mark each nonempty-bin median for the legend and link supported neighbors."""
    medians = median_df["median"].to_numpy(dtype=float)
    counts = median_df["count"].fillna(0).to_numpy(dtype=float)
    has_median = ~np.isnan(medians) & (counts > 0)

    median_markers = None
    if has_median.any():
        median_markers = ax.scatter(
            x_centers[has_median],
            medians[has_median],
            s=26,
            color="#c8f4ff",
            edgecolors="#00384d",
            linewidths=0.5,
            label=label,
            zorder=5,
        )
        median_markers.set_gid("temporal-bin-median-markers")
    for index in range(len(x_centers) - 1):
        if (
            counts[index] >= TEMPORAL_MEDIAN_LINK_MIN_COUNT
            and counts[index + 1] >= TEMPORAL_MEDIAN_LINK_MIN_COUNT
            and not np.isnan(medians[index])
            and not np.isnan(medians[index + 1])
        ):
            ax.plot(
                [x_centers[index], x_centers[index + 1]],
                [medians[index], medians[index + 1]],
                color="#c8f4ff",
                linewidth=1.2,
                alpha=0.75,
                zorder=4,
            )
    return median_markers


def _chronological_density_components(work_df, bin_minutes, metric_bins):
    """Build chronological UTC count and median grids using existing floor alignment."""
    bin_delta = pd.to_timedelta(bin_minutes, unit="min")
    bin_freq = f"{bin_minutes}min"
    chronological_rows = work_df.copy()
    chronological_rows["time_bin"] = chronological_rows["plot_time"].dt.floor(bin_freq)
    time_bins = pd.date_range(
        start=chronological_rows["time_bin"].min(),
        end=chronological_rows["time_bin"].max(),
        freq=bin_freq,
    )
    count_grid = (
        chronological_rows
        .groupby(["metric_bin", "time_bin"], dropna=False)
        .size()
        .unstack(fill_value=0)
        .reindex(index=metric_bins, columns=time_bins, fill_value=0)
    )
    median_df = (
        chronological_rows
        .groupby("time_bin", dropna=False)["metric"]
        .agg(["median", "count"])
        .reindex(time_bins)
    )
    time_edges = time_bins.append(pd.DatetimeIndex([time_bins[-1] + bin_delta]))
    x_edges = mdates.date2num(time_edges.to_pydatetime())
    x_centers = mdates.date2num((time_bins + (bin_delta / 2)).to_pydatetime())
    return count_grid, median_df, x_edges, x_centers


def _folded_utc_hour_density_components(work_df, metric_bins):
    """Build a fixed 24-column UTC-hour count grid and exact hourly medians."""
    folded_rows = work_df.copy()
    folded_rows["utc_hour"] = folded_rows["plot_time"].dt.hour
    utc_hours = pd.Index(range(24), name="utc_hour")
    count_grid = (
        folded_rows
        .groupby(["metric_bin", "utc_hour"], dropna=False)
        .size()
        .unstack(fill_value=0)
        .reindex(index=metric_bins, columns=utc_hours, fill_value=0)
    )
    median_df = (
        folded_rows
        .groupby("utc_hour", dropna=False)["metric"]
        .agg(["median", "count"])
        .reindex(utc_hours)
    )
    x_edges = np.arange(25, dtype=float)
    x_centers = np.arange(24, dtype=float) + 0.5
    return count_grid, median_df, x_edges, x_centers


def _draw_folded_utc_unavailable_annotation(axis, message):
    """Draw an opaque, compact notice when a UTC-hour fold is unsupported."""
    normalized_message = " ".join(str(message).split())
    if " - " in normalized_message:
        headline, detail = normalized_message.split(" - ", maxsplit=1)
        detail = detail[:1].upper() + detail[1:]
        wrapped_lines = [headline]
        wrapped_lines.extend(
            textwrap.wrap(
                detail,
                width=FOLDED_UTC_UNAVAILABLE_DETAIL_WRAP_WIDTH,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
    else:
        wrapped_lines = textwrap.wrap(
            normalized_message,
            width=FOLDED_UTC_UNAVAILABLE_WRAP_WIDTH,
            break_long_words=False,
            break_on_hyphens=False,
        )
    annotation = axis.text(
        0.5,
        0.5,
        "\n".join(wrapped_lines),
        transform=axis.transAxes,
        color="white",
        ha="center",
        va="center",
        fontsize=9,
        fontfamily=METRIC_FONT_FAMILY,
        fontweight="normal",
        linespacing=1.3,
        bbox={
            "boxstyle": "round,pad=0.55",
            "facecolor": "black",
            "edgecolor": "#555555",
            "linewidth": 0.8,
            "alpha": 1.0,
        },
        zorder=METRIC_FOREGROUND_ZORDER,
    )
    annotation.set_gid("folded-utc-unavailable-annotation")
    return annotation


def _segment_temporal_evidence_export_recipe(
    plot_df,
    title,
    time_bin,
    count_label,
    *,
    chronological_title,
    chronological_x_label,
    metric_axis_label,
    folded_title,
    folded_x_label,
    folded_date_annotation,
    density_label,
    folded_unavailable_text,
    median_focus_axis_label,
    median_label,
    bin_median_label,
    chronological_subtitle=None,
    folded_subtitle=None,
    omit_folded_when_unavailable=False,
    show_folded_date_annotation=False,
    kind="segment_compare_temporal",
):
    """Return compact arrays and localized labels for Compare temporal evidence."""
    work_df = _prepare_temporal_metric_rows(plot_df)
    time_bin = str(time_bin)
    utc_date_count = _temporal_utc_date_count(work_df)
    chronological_title = str(chronological_title).replace(
        "{time_bin}",
        time_bin,
    )
    folded_title = str(folded_title).replace(
        "{utc_date_count}",
        str(utc_date_count),
    )
    folded_date_annotation = str(folded_date_annotation).replace(
        "{utc_date_count}",
        str(utc_date_count),
    )
    resolved_chronological_subtitle = (
        str(chronological_subtitle).replace(
            "{time_bin}",
            _format_temporal_time_bin_label(time_bin),
        )
        if chronological_subtitle is not None
        else None
    )
    resolved_folded_subtitle = (
        str(folded_subtitle).replace(
            "{utc_date_count}",
            str(utc_date_count),
        )
        if folded_subtitle is not None
        else None
    )
    median_focus = _compare_median_focus_recipe(
        _build_compare_median_focus_spec(work_df["metric"])
    )
    return {
        "kind": str(kind),
        "schema_version": 1,
        "title": str(title),
        "time_bin": time_bin,
        "count_label": str(count_label),
        "chronological_title": str(chronological_title),
        "chronological_subtitle": resolved_chronological_subtitle,
        "chronological_x_label": str(chronological_x_label),
        "metric_axis_label": str(metric_axis_label),
        "folded_title": str(folded_title),
        "folded_subtitle": resolved_folded_subtitle,
        "folded_x_label": str(folded_x_label),
        "folded_date_annotation": str(folded_date_annotation),
        "density_label": str(density_label),
        "folded_unavailable_text": str(folded_unavailable_text),
        "omit_folded_when_unavailable": bool(
            omit_folded_when_unavailable
        ),
        "show_folded_date_annotation": bool(
            show_folded_date_annotation
        ),
        "median_focus": median_focus,
        "median_focus_axis_label": str(median_focus_axis_label),
        "median_label": str(median_label),
        "bin_median_label": str(bin_median_label),
        "utc_date_count": utc_date_count,
        "plot_time_ns": (
            work_df["plot_time"]
            .to_numpy(dtype="datetime64[ns]")
            .astype(np.int64, copy=True)
        ),
        "metric": work_df["metric"].to_numpy(dtype=np.float64, copy=True),
    }


@synchronized_matplotlib
def render_segment_temporal_snr_export_figure(recipe):
    """Render shared Success temporal SNR evidence in its configured representation."""
    if not recipe or recipe.get("kind") != "opportunity_success_temporal":
        return None
    from ui.plots.opportunity_figures import (
        _render_opportunity_temporal_snr_figure,
    )

    return _render_opportunity_temporal_snr_figure(recipe)


@synchronized_matplotlib
def render_segment_temporal_evidence_export_figure(recipe):
    """Render a registered Compare temporal or Success evidence recipe."""
    if not recipe:
        return None
    if recipe.get("kind") == "opportunity_success_temporal":
        from ui.plots.opportunity_figures import (
            _render_opportunity_temporal_evidence_figure,
        )

        return _render_opportunity_temporal_evidence_figure(recipe)
    plot_time_ns = np.asarray(recipe.get("plot_time_ns", []), dtype=np.int64)
    metric_values = np.asarray(recipe.get("metric", []), dtype=float)
    if len(plot_time_ns) == 0 or len(plot_time_ns) != len(metric_values):
        return None

    plot_df = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(plot_time_ns, unit="ns", utc=True),
            "metric": metric_values,
        }
    )
    work_df = _prepare_temporal_metric_rows(plot_df)
    if work_df.empty:
        return None
    median_focus_spec = _compare_median_focus_spec_from_recipe(
        recipe.get("median_focus"),
        work_df["metric"],
    )

    time_bin = str(recipe["time_bin"])
    utc_date_count = _temporal_utc_date_count(work_df)
    is_folded_available = utc_date_count >= 2
    show_folded_axis = (
        is_folded_available
        or not bool(recipe.get("omit_folded_when_unavailable", False))
    )
    bin_minutes = _time_agg_minutes(time_bin)
    metric_min = int(work_df["metric_bin"].min())
    metric_max = int(work_df["metric_bin"].max())
    metric_bins = np.arange(metric_min, metric_max + 1)
    y_edges = np.arange(metric_min - 0.5, metric_max + 1.5, 1.0)

    chronological_grid, chronological_medians, chronological_edges, chronological_centers = (
        _chronological_density_components(work_df, bin_minutes, metric_bins)
    )
    folded_grid = None
    folded_medians = None
    folded_edges = np.arange(25, dtype=float)
    folded_centers = np.arange(24, dtype=float) + 0.5
    if is_folded_available:
        folded_grid, folded_medians, folded_edges, folded_centers = (
            _folded_utc_hour_density_components(work_df, metric_bins)
        )

    figure = create_agg_figure(
        figsize=SEGMENT_TEMPORAL_FIGURE_SIZE_INCHES,
        facecolor="black",
    )
    figure.subplots_adjust(
        left=SEGMENT_TEMPORAL_FIGURE_LEFT,
        right=SEGMENT_TEMPORAL_FIGURE_RIGHT,
        bottom=SEGMENT_FIGURE_BOTTOM,
        top=SEGMENT_TEMPORAL_FIGURE_TOP,
        wspace=SEGMENT_TEMPORAL_COLUMN_SPACE,
    )
    grid_spec_kwargs = {"nrows": 1, "ncols": 2 if show_folded_axis else 1}
    if show_folded_axis:
        grid_spec_kwargs["width_ratios"] = SEGMENT_TEMPORAL_COLUMN_WIDTH_RATIOS
    grid_spec = figure.add_gridspec(**grid_spec_kwargs)
    chronological_axis = figure.add_subplot(grid_spec[0, 0])
    chronological_axis.set_gid("compare-temporal-chronological-axis")
    folded_axis = None
    if show_folded_axis:
        folded_axis = figure.add_subplot(
            grid_spec[0, 1],
            sharey=chronological_axis,
        )
        folded_axis.set_gid("compare-temporal-folded-axis")
    for axis in (chronological_axis, folded_axis):
        if axis is not None:
            _style_evidence_axis(axis)

    density_norm = mpl.colors.Normalize(
        vmin=EVIDENCE_DENSITY_MIN,
        vmax=EVIDENCE_DENSITY_MAX,
    )
    chronological_mesh = _draw_relative_density_mesh(
        chronological_axis,
        chronological_edges,
        y_edges,
        chronological_grid,
        density_norm=density_norm,
    )
    _draw_temporal_median_overlay(
        chronological_axis,
        chronological_centers,
        chronological_medians,
        label=recipe["bin_median_label"],
    )
    folded_mesh = None
    if is_folded_available and folded_axis is not None:
        folded_mesh = _draw_relative_density_mesh(
            folded_axis,
            folded_edges,
            y_edges,
            folded_grid,
            density_norm=density_norm,
        )
        _draw_temporal_median_overlay(
            folded_axis,
            folded_centers,
            folded_medians,
            label=recipe["bin_median_label"],
        )
    elif folded_axis is not None:
        _draw_folded_utc_unavailable_annotation(
            folded_axis,
            recipe["folded_unavailable_text"],
        )
    else:
        chronological_axis.text(
            0.98,
            0.05,
            recipe["folded_unavailable_text"],
            transform=chronological_axis.transAxes,
            color="#cccccc",
            fontsize=METRIC_TICK_LABEL_FONTSIZE,
            ha="right",
            va="bottom",
            bbox={
                "facecolor": "none",
                "edgecolor": "#444444",
                "alpha": 1.0,
                "pad": 4,
            },
        )

    date_locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
    chronological_axis.xaxis.set_major_locator(date_locator)
    chronological_axis.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b\n%H:%M"))
    chronological_axis.set_xlim(chronological_edges[0], chronological_edges[-1])
    if recipe.get("chronological_subtitle") is None:
        _set_temporal_panel_title(
            chronological_axis,
            recipe["chronological_title"],
        )
    else:
        _set_temporal_panel_title_with_subtitle(
            chronological_axis,
            recipe["chronological_title"],
            recipe["chronological_subtitle"],
            subtitle_gid="compare-temporal-chronological-subtitle",
        )
    _set_metric_axis_labels(
        chronological_axis,
        x_label=recipe["chronological_x_label"],
        y_label=recipe["metric_axis_label"],
    )

    if folded_axis is not None:
        folded_axis.set_xlim(0.0, 24.0)
        folded_axis.set_xticks(np.arange(0.5, 24.0, 3.0))
        folded_axis.set_xticklabels(
            [f"{hour:02d}" for hour in range(0, 24, 3)]
        )
        if recipe.get("folded_subtitle") is None:
            _set_temporal_panel_title(
                folded_axis,
                recipe["folded_title"],
            )
        else:
            _set_temporal_panel_title_with_subtitle(
                folded_axis,
                recipe["folded_title"],
                recipe["folded_subtitle"],
                subtitle_gid="compare-temporal-folded-subtitle",
            )
        _set_metric_axis_labels(
            folded_axis,
            x_label=recipe["folded_x_label"],
        )
        if (
            is_folded_available
            and recipe.get("show_folded_date_annotation", False)
        ):
            folded_axis.text(
                0.02,
                0.04,
                recipe["folded_date_annotation"],
                transform=folded_axis.transAxes,
                color="#cccccc",
                fontsize=8,
                ha="left",
                va="bottom",
            )
    for axis in (chronological_axis, folded_axis):
        if axis is not None:
            _apply_compare_median_focus_axis(
                axis,
                median_focus_spec,
                axis_label=recipe["median_focus_axis_label"],
                median_label=recipe["median_label"],
            )

    colorbar_mesh = folded_mesh if folded_mesh is not None else chronological_mesh
    colorbar_axes = [chronological_axis]
    if folded_axis is not None:
        colorbar_axes.append(folded_axis)
    colorbar = figure.colorbar(
        colorbar_mesh,
        ax=colorbar_axes,
        pad=SEGMENT_TEMPORAL_COLORBAR_PAD,
        fraction=SEGMENT_TEMPORAL_COLORBAR_FRACTION,
        ticks=np.linspace(EVIDENCE_DENSITY_MIN, EVIDENCE_DENSITY_MAX, 5),
    )
    colorbar.ax.set_gid("compare-temporal-colorbar-axis")
    colorbar.set_label(recipe["density_label"], color="white")
    colorbar.ax.tick_params(colors="white", labelsize=8)
    colorbar.outline.set_edgecolor("#444444")

    figure.suptitle(
        recipe["title"],
        color="white",
        fontweight="bold",
        fontsize=METRIC_FIGURE_TITLE_FONTSIZE,
        y=0.96,
    )
    figure.text(
        0.98,
        SEGMENT_FIGURE_FOOTER_Y,
        f"WSPRadar.org {APP_VERSION}",
        color="#888888",
        ha="right",
        fontsize=METRIC_FOOTER_FONTSIZE,
    )
    return figure

def _selected_evidence_export_recipe(
    plot_df,
    evidence_title,
    time_agg,
    is_sequential,
    *,
    count_label,
    chronological_title,
    chronological_subtitle,
    chronological_x_label,
    metric_axis_label,
    folded_title,
    folded_subtitle,
    folded_x_label,
    folded_date_annotation,
    density_label,
    folded_unavailable_text,
    median_focus_axis_label,
    median_label,
    bin_median_label,
):
    """Return the shared dual-panel recipe for one selected Compare station."""
    plot_times = pd.to_datetime(plot_df["plot_time"], errors="coerce", utc=True)
    numeric_metrics = pd.to_numeric(plot_df["metric"], errors="coerce")
    valid = plot_times.notna() & numeric_metrics.notna() & np.isfinite(numeric_metrics)
    selected_identity_count = 1
    if "identity" in plot_df.columns:
        selected_identity_count = max(
            1,
            int(plot_df.loc[valid, "identity"].dropna().nunique()),
        )
    recipe = _segment_temporal_evidence_export_recipe(
        plot_df.loc[valid, ["plot_time", "metric"]],
        evidence_title,
        time_agg,
        count_label,
        chronological_title=chronological_title,
        chronological_subtitle=chronological_subtitle,
        chronological_x_label=chronological_x_label,
        metric_axis_label=metric_axis_label,
        folded_title=folded_title,
        folded_subtitle=folded_subtitle,
        folded_x_label=folded_x_label,
        folded_date_annotation=folded_date_annotation,
        density_label=density_label,
        folded_unavailable_text=folded_unavailable_text,
        median_focus_axis_label=median_focus_axis_label,
        median_label=median_label,
        bin_median_label=bin_median_label,
        omit_folded_when_unavailable=True,
        show_folded_date_annotation=True,
        kind="selected_compare_temporal",
    )
    recipe["is_sequential"] = bool(is_sequential)
    recipe["selected_identity_count"] = selected_identity_count
    return recipe

def render_selected_evidence_export_figure(recipe):
    """Render selected Compare evidence through the shared temporal renderer."""
    if not recipe or recipe.get("kind") != "selected_compare_temporal":
        return None
    return render_segment_temporal_evidence_export_figure(recipe)

def _segment_figure_export_recipe(
    *,
    title,
    selected_segment,
    is_sequential,
    station_values,
    spot_values,
    panel_labels,
    panel_y_label,
    decode_outcomes_title,
    station_medians_title,
    paired_evidence_title,
    metric_axis_label,
    median_label,
    mean_label,
    no_data_label,
    panel_station_counts=None,
    panel_spot_counts=None,
    panel_series_labels=None,
):
    """Store numeric inputs and localized labels for Compare segment evidence."""
    return {
        "title": title,
        "selected_segment": selected_segment,
        "is_sequential": bool(is_sequential),
        "station_values": _metric_values(station_values).astype(np.float64, copy=True),
        "spot_values": _metric_values(spot_values).astype(np.float64, copy=True),
        "panel_labels": [str(value) for value in panel_labels],
        "panel_y_label": str(panel_y_label),
        "decode_outcomes_title": str(decode_outcomes_title),
        "station_medians_title": str(station_medians_title),
        "paired_evidence_title": str(paired_evidence_title),
        "metric_axis_label": str(metric_axis_label),
        "median_label": str(median_label),
        "mean_label": str(mean_label),
        "no_data_label": str(no_data_label),
        "panel_station_counts": [
            int(value)
            for value in (
                [] if panel_station_counts is None else panel_station_counts
            )
        ],
        "panel_spot_counts": [
            int(value)
            for value in (
                [] if panel_spot_counts is None else panel_spot_counts
            )
        ],
        "panel_series_labels": [
            str(value)
            for value in (
                [] if panel_series_labels is None else panel_series_labels
            )
        ],
    }


def _percentage_shares(counts):
    """Return nonnegative count composition as percentages of its own total."""
    numeric_counts = np.asarray(counts, dtype=float)
    if np.any(~np.isfinite(numeric_counts)) or np.any(numeric_counts < 0):
        raise ValueError("Outcome counts must be finite and nonnegative")
    total_count = float(numeric_counts.sum())
    if total_count <= 0:
        return np.zeros(len(numeric_counts), dtype=float)
    return numeric_counts * 100.0 / total_count


def _format_integer_percentage(percentage):
    """Format a compact integer percentage without hiding a nonzero sub-1% share."""
    percentage = float(percentage)
    if percentage <= 0:
        return "0%"
    if percentage < 1:
        return "<1%"
    return f"{percentage:.0f}%"


def _draw_compare_outcome_bars(
    ax,
    *,
    panel_labels,
    station_counts,
    spot_counts,
    series_labels,
):
    """Draw station-left and spot-right outcome shares with stable visual encoding."""
    if not (
        len(panel_labels) == len(station_counts) == len(spot_counts)
    ):
        raise ValueError("Compare outcome labels and count series must align")
    if len(series_labels) != 2:
        raise ValueError("Compare outcome bars require station and spot labels")

    station_percentages = _percentage_shares(station_counts)
    spot_percentages = _percentage_shares(spot_counts)
    category_positions = np.arange(len(panel_labels), dtype=float)
    bar_width = 0.34
    bar_offset = 0.19

    station_bars = ax.bar(
        category_positions - bar_offset,
        station_percentages,
        width=bar_width,
        facecolor="none",
        edgecolor=EVIDENCE_AGG_COLOR,
        hatch=STATION_EVIDENCE_HATCH,
        linewidth=1.0,
        zorder=2,
    )
    spot_bars = ax.bar(
        category_positions + bar_offset,
        spot_percentages,
        width=bar_width,
        facecolor=EVIDENCE_AGG_COLOR,
        edgecolor="#67c4ff",
        alpha=0.80,
        linewidth=0.7,
        zorder=2,
    )
    for rectangle in station_bars:
        rectangle.set_gid("decode-outcome-stations")
    for rectangle in spot_bars:
        rectangle.set_gid("decode-outcome-spots")

    for rectangles, percentages in (
        (station_bars, station_percentages),
        (spot_bars, spot_percentages),
    ):
        for rectangle, percentage in zip(rectangles, percentages):
            annotation = ax.text(
                rectangle.get_x() + rectangle.get_width() / 2.0,
                rectangle.get_height() + 2.0,
                _format_integer_percentage(percentage),
                ha="center",
                va="bottom",
                color="white",
                fontsize=9,
                fontweight="bold",
            )
            annotation.set_gid("decode-outcome-percentage")

    station_key = mpl.patches.Patch(
        facecolor="none",
        edgecolor=EVIDENCE_AGG_COLOR,
        hatch=STATION_EVIDENCE_HATCH,
        linewidth=1.0,
        label=series_labels[0],
    )
    spot_key = mpl.patches.Patch(
        facecolor=EVIDENCE_AGG_COLOR,
        edgecolor="#67c4ff",
        linewidth=0.7,
        label=series_labels[1],
    )
    station_legend = _place_metric_legend(
        ax,
        handles=[station_key],
        loc="upper left",
        borderaxespad=0.35,
        gid="decode-outcome-station-legend",
    )
    ax.add_artist(station_legend)
    _place_metric_legend(
        ax,
        handles=[spot_key],
        loc="upper right",
        borderaxespad=0.35,
        gid="decode-outcome-spot-legend",
    )
    ax.set_xticks(category_positions)
    ax.set_xticklabels(panel_labels)
    ax.set_ylim(0.0, 120.0)
    ax.set_yticks(np.arange(0.0, 101.0, 20.0))
    return station_bars, spot_bars


@synchronized_matplotlib
def render_segment_insight_export_figure(recipe):
    """Rebuild the Segment Insight figure only when preparing the results ZIP."""
    if not recipe:
        return None
    recipe_kind = recipe.get("kind")
    if recipe_kind == "opportunity_success_evidence":
        from ui.plots.opportunity_figures import _render_opportunity_segment_figure
        return _render_opportunity_segment_figure(recipe)
    if recipe_kind is not None:
        return None

    station_values = np.asarray(recipe.get("station_values", []), dtype=float)
    spot_values = np.asarray(recipe.get("spot_values", []), dtype=float)
    panel_labels = list(recipe.get("panel_labels", []))
    panel_station_counts = list(recipe.get("panel_station_counts", []))
    panel_spot_counts = list(recipe.get("panel_spot_counts", []))
    panel_series_labels = list(recipe.get("panel_series_labels", []))

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

    _draw_compare_outcome_bars(
        ax_panel,
        panel_labels=panel_labels,
        station_counts=panel_station_counts,
        spot_counts=panel_spot_counts,
        series_labels=panel_series_labels,
    )
    ax_panel.set_ylabel(
        recipe["panel_y_label"],
        color="white",
    )
    ax_panel.set_title(
        recipe["decode_outcomes_title"],
        color="white",
        fontweight="bold",
        pad=10,
    )
    ax_hist.set_title(
        recipe["station_medians_title"],
        color="white",
        fontweight="bold",
        pad=10,
    )
    ax_spot.set_title(
        recipe["paired_evidence_title"],
        color="white",
        fontweight="bold",
        pad=10,
    )

    fig_hist.suptitle(
        f"\n{recipe['title']} - {recipe['selected_segment']}",
        color="white",
        fontweight="bold",
        fontsize=METRIC_FIGURE_TITLE_FONTSIZE,
        y=0.98,
    )
    fig_hist.text(
        0.98,
        SEGMENT_FIGURE_FOOTER_Y,
        f"WSPRadar.org {APP_VERSION}",
        color="#888888",
        ha="right",
        fontsize=METRIC_FOOTER_FONTSIZE,
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
        station_median = _draw_vertical_metric_histogram(
            ax_hist,
            station_values,
            color=EVIDENCE_AGG_COLOR,
            share_axis_label=recipe["panel_y_label"],
            hatch=STATION_EVIDENCE_HATCH,
            artist_gid="station-median-histogram",
        )
        station_median_line = _add_metric_median_reference(
            ax_hist,
            station_median,
            orientation="vertical",
            label=recipe["median_label"],
            zorder=4.0,
        )
        _apply_minimum_metric_xspan(ax_hist, center=station_median)
        _place_metric_legend_top_right(
            ax_hist,
            handles=[station_median_line],
        )
        _add_metric_mean_annotation(
            ax_hist,
            float(np.mean(station_values)),
            label=recipe["mean_label"],
        )
    else:
        ax_hist.text(
            0.5,
            0.5,
            recipe["no_data_label"],
            color="white",
            ha="center",
            va="center",
            fontsize=12,
            transform=ax_hist.transAxes,
        )
        ax_hist.set_xticks([])
        ax_hist.set_yticks([])

    spot_median = _draw_vertical_metric_histogram(
        ax_spot,
        spot_values,
        color=EVIDENCE_AGG_COLOR,
        share_axis_label=recipe["panel_y_label"],
        artist_gid="spot-metric-histogram",
    )
    if pd.notna(spot_median):
        spot_median_line = _add_metric_median_reference(
            ax_spot,
            spot_median,
            orientation="vertical",
            label=recipe["median_label"],
            zorder=4.0,
        )
        _apply_minimum_metric_xspan(ax_spot, center=spot_median)
        _place_metric_legend_top_right(
            ax_spot,
            handles=[spot_median_line],
        )
        if len(spot_values):
            _add_metric_mean_annotation(
                ax_spot,
                float(np.mean(spot_values)),
                label=recipe["mean_label"],
            )
    else:
        ax_spot.text(
            0.5,
            0.5,
            recipe["no_data_label"],
            color="white",
            ha="center",
            va="center",
            fontsize=12,
            transform=ax_spot.transAxes,
        )
        ax_spot.set_xticks([])
        ax_spot.set_yticks([])

    ax_hist.set_xlabel(recipe["metric_axis_label"], color="white")
    ax_spot.set_xlabel(recipe["metric_axis_label"], color="white")
    return fig_hist
