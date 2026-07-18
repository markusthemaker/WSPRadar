"""Matplotlib evidence and Segment Insight figures for WSPRadar."""

from dataclasses import dataclass
import textwrap

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.dates as mdates

from config import APP_VERSION
from core.matplotlib_runtime import create_agg_figure, synchronized_matplotlib
from core.solar_path import ILLUMINATION_CLASSES
from core.stability import (
    _bootstrap_median_interval,
    _expanded_metric_limits,
    _format_metric_signed,
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
SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL = "chronological"
SELECTED_TEMPORAL_VIEW_UTC_HOUR = "utc_hour"
FOLDED_UTC_UNAVAILABLE_TEXT = (
    "UTC-hour pattern unavailable - requires joint evidence from at least 2 UTC dates."
)
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

def _default_evidence_labels(is_compare):
    if is_compare:
        return {
            "dist_title": "\u0394 SNR Distribution",
            "time_title": "\u0394 SNR over Time",
            "y_label": "\u0394 SNR (dB)",
            "x_label": "Date/Time (UTC)",
            "aggregate": "Selected Stations",
            "median_label": "Median",
            "pooled_median_label": "Median",
            "mean_label": "Mean",
            "pooled_mean_label": "Mean",
            "stability_label": "90% Stability",
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
        "stability_label": "90% Stability",
    }

def _add_horizontal_grid(ax):
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)

def _add_foreground_horizontal_grid(ax):
    ax.set_axisbelow(False)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA, zorder=3)


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
    label="Median",
    signed=True,
    zorder=4.0,
    gid=None,
):
    """Draw and return one consistently styled horizontal or vertical median."""
    line_label = (
        f"{label} {_format_metric_signed(float(median_db), signed)} dB"
    )
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
    axis_label="\u0394 SNR (dB \u00b7 median-centered nonlinear)",
    median_label="Median",
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
        _place_metric_legend_top_right(ax, handles=[median_reference_line])

def _add_stability_band(ax, low, high, *, label="90% Stability"):
    """Draw and return the true horizontal Stability artist."""
    if pd.isna(low) or pd.isna(high):
        return None
    low = float(low)
    high = float(high)
    if high < low:
        low, high = high, low
    if high - low <= STABILITY_LINE_THRESHOLD_DB:
        center = (low + high) / 2.0
        return ax.axhline(
            center,
            color="red",
            alpha=0.24,
            linewidth=4.0,
            zorder=1,
            label=label,
        )
    return ax.axhspan(low, high, color="red", alpha=0.12, zorder=1, label=label)

def _add_vertical_stability_band(ax, low, high, *, label="90% Stability"):
    """Draw and return the true vertical Stability artist."""
    if pd.isna(low) or pd.isna(high):
        return None
    low = float(low)
    high = float(high)
    if high < low:
        low, high = high, low
    if high - low <= STABILITY_LINE_THRESHOLD_DB:
        center = (low + high) / 2.0
        return ax.axvline(
            center,
            color="red",
            alpha=0.24,
            linewidth=4.0,
            zorder=1,
            label=label,
        )
    return ax.axvspan(
        low,
        high,
        color="red",
        alpha=0.12,
        zorder=1,
        label=label,
    )

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


def _set_metric_colorbar_label(colorbar, label, *, color="white"):
    """Apply the shared evidence typography to one colorbar label."""
    colorbar.set_label(
        label,
        color=color,
        fontsize=METRIC_AXIS_LABEL_FONTSIZE,
        fontfamily=METRIC_FONT_FAMILY,
        fontweight="normal",
    )


def _add_metric_mean_annotation(ax, mean_db, *, label="Mean", signed=True):
    """Place one signed arithmetic-mean summary at the lower-right foreground."""
    mean_annotation = ax.text(
        0.98,
        0.04,
        f"{label} {_format_metric_signed(mean_db, signed)} dB",
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


def _annotate_selected_compare_distribution(
    ax,
    values,
    stability_interval,
    labels,
):
    """Annotate the exact pooled evidence median, mean, and median stability."""
    metric_values = _metric_values(values)
    if len(metric_values) <= 1:
        return

    median = float(np.median(metric_values))
    arithmetic_mean = float(np.mean(metric_values))
    if stability_interval is None:
        stability_interval = _bootstrap_median_interval(metric_values)
    _, stability_low, stability_high = stability_interval

    median_label = labels.get("median_label", "Median")
    mean_label = labels.get("mean_label", "Mean")
    stability_label = labels.get("stability_label", "90% Stability")

    stability_artist = _add_stability_band(
        ax,
        stability_low,
        stability_high,
        label=stability_label,
    )
    median_line = _add_metric_median_reference(
        ax,
        median,
        orientation="horizontal",
        label=median_label,
        zorder=4,
    )
    _add_metric_mean_annotation(
        ax,
        arithmetic_mean,
        label=mean_label,
    )
    legend_handles = [median_line]
    if stability_artist is not None:
        legend_handles.append(stability_artist)
    _place_metric_legend_top_right(ax, handles=legend_handles)


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

def _draw_single_time_point(ax, plot_df, labels, *, is_compare=False):
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
    if not is_compare:
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


def _relative_density_label(count_label):
    """Describe panel-relative density using the supplied evidence-count basis."""
    raw_label = str(count_label or "Evidence count").strip()
    if "% of panel maximum" in raw_label.casefold():
        return raw_label

    known_bases = {
        "joint spot count": "joint-spot",
        "scheduled pair count": "scheduled-pair",
        "spot count": "spot",
    }
    normalized_label = " ".join(raw_label.casefold().split())
    evidence_basis = known_bases.get(normalized_label)
    if evidence_basis is None:
        evidence_basis = raw_label
        if normalized_label.endswith(" count"):
            evidence_basis = raw_label[:-6].strip()
        evidence_basis = evidence_basis.casefold() or "evidence"
    return f"Relative {evidence_basis} density (% of panel maximum)"


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


def _draw_temporal_median_overlay(ax, x_centers, median_df):
    """Mark every nonempty-bin median and link adjacent well-supported bins."""
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
        zorder=5,
    )
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


def _default_folded_utc_hour_title(utc_date_count=None):
    """Return the compact English title for a fixed one-hour UTC fold."""
    return "\u0394 SNR by UTC Hour (1 h bins)"


def _default_folded_utc_date_annotation(utc_date_count):
    """Describe the UTC-date depth separately from the folded panel title."""
    utc_date_count = int(utc_date_count)
    if utc_date_count >= 2:
        return f"{utc_date_count} UTC dates folded"
    date_noun = "date" if utc_date_count == 1 else "dates"
    return f"{utc_date_count} UTC {date_noun} available; folding unavailable"


def _draw_folded_utc_unavailable_annotation(axis, message):
    """Draw an opaque, compact notice when a UTC-hour fold is unsupported."""
    normalized_message = " ".join(
        str(message or FOLDED_UTC_UNAVAILABLE_TEXT).split()
    )
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


def _draw_time_heatmap(fig, ax, plot_df, time_agg, labels, is_compare, is_sequential):
    """Draw UTC time-bin evidence, using panel-relative density for Compare."""
    bin_minutes = _time_agg_minutes(time_agg)
    work_df = _prepare_temporal_metric_rows(plot_df)

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

    metric_min = int(work_df["metric_bin"].min())
    metric_max = int(work_df["metric_bin"].max())
    metric_bins = np.arange(metric_min, metric_max + 1)
    count_grid, median_df, x_edges, x_centers = _chronological_density_components(
        work_df,
        bin_minutes,
        metric_bins,
    )
    y_edges = np.arange(metric_min - 0.5, metric_max + 1.5, 1.0)
    if is_compare:
        mesh = _draw_relative_density_mesh(
            ax,
            x_edges,
            y_edges,
            count_grid,
        )
    else:
        raw_counts = count_grid.to_numpy(dtype=float)
        mesh = ax.pcolormesh(
            x_edges,
            y_edges,
            np.ma.masked_where(raw_counts <= 0.0, raw_counts),
            cmap=EVIDENCE_HEATMAP_CMAP,
            shading="flat",
            zorder=1,
        )
    _draw_temporal_median_overlay(ax, x_centers, median_df)

    count_label = labels.get("count_label")
    if not count_label:
        count_label = (
            "Scheduled pair count"
            if is_sequential
            else "Joint spot count"
            if is_compare
            else "Spot count"
        )
    colorbar_kwargs = {
        "ax": ax,
        "pad": 0.012,
        "fraction": 0.03,
    }
    if is_compare:
        colorbar_kwargs["ticks"] = np.linspace(
            EVIDENCE_DENSITY_MIN,
            EVIDENCE_DENSITY_MAX,
            5,
        )
    cbar = fig.colorbar(mesh, **colorbar_kwargs)
    if is_compare:
        colorbar_label = labels.get("density_label") or _relative_density_label(
            count_label
        )
    else:
        colorbar_label = count_label
    cbar.set_label(colorbar_label, color="white")
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
    if not is_compare:
        _add_foreground_horizontal_grid(ax)


def _draw_folded_utc_hour_heatmap(
    fig,
    ax,
    plot_df,
    labels,
    is_sequential,
    *,
    folded_title=None,
    folded_x_label=None,
    density_label=None,
    folded_unavailable_text=None,
):
    """Draw selected Compare evidence in 24 fixed UTC-hour density slots."""
    work_df = _prepare_temporal_metric_rows(plot_df)
    utc_date_count = _temporal_utc_date_count(work_df)
    resolved_folded_title = (
        str(folded_title).replace("{utc_date_count}", str(utc_date_count))
        if folded_title is not None
        else _default_folded_utc_hour_title(utc_date_count)
    )
    ax.set_xlim(0.0, 24.0)
    ax.set_xticks(np.arange(0, 25, 3))
    ax.set_xticklabels([f"{hour:02d}" for hour in range(0, 25, 3)])
    ax.set_title(
        resolved_folded_title,
        color="white",
        fontweight="bold",
        pad=10,
    )
    ax.set_xlabel(folded_x_label or "UTC hour", color="white")
    ax.set_ylabel(labels["y_label"], color="white")

    if work_df.empty:
        ax.text(
            0.5,
            0.5,
            "No selected evidence available.",
            transform=ax.transAxes,
            color="#cccccc",
            ha="center",
            va="center",
        )
        return None

    metric_min = int(work_df["metric_bin"].min())
    metric_max = int(work_df["metric_bin"].max())
    ax.set_ylim(metric_min - 0.5, metric_max + 0.5)
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=7, integer=True))

    if utc_date_count < 2:
        _draw_folded_utc_unavailable_annotation(
            ax,
            folded_unavailable_text
            or FOLDED_UTC_UNAVAILABLE_TEXT,
        )
        return None

    metric_bins = np.arange(metric_min, metric_max + 1)
    y_edges = np.arange(metric_min - 0.5, metric_max + 1.5, 1.0)
    count_grid, median_df, x_edges, x_centers = (
        _folded_utc_hour_density_components(work_df, metric_bins)
    )
    mesh = _draw_relative_density_mesh(ax, x_edges, y_edges, count_grid)
    _draw_temporal_median_overlay(ax, x_centers, median_df)

    count_label = labels.get("count_label")
    if not count_label:
        count_label = "Scheduled pair count" if is_sequential else "Joint spot count"
    resolved_density_label = density_label or labels.get("density_label")
    if not resolved_density_label:
        resolved_density_label = _relative_density_label(count_label)
    colorbar = fig.colorbar(
        mesh,
        ax=ax,
        pad=0.012,
        fraction=0.03,
        ticks=np.linspace(EVIDENCE_DENSITY_MIN, EVIDENCE_DENSITY_MAX, 5),
    )
    colorbar.set_label(resolved_density_label, color="white")
    colorbar.ax.tick_params(colors="white", labelsize=8)
    colorbar.outline.set_edgecolor("#444444")
    return mesh


def _segment_temporal_evidence_export_recipe(
    plot_df,
    title,
    time_bin,
    count_label,
    *,
    chronological_title=None,
    chronological_x_label=None,
    folded_title=None,
    folded_x_label=None,
    folded_date_annotation=None,
    density_label=None,
    folded_unavailable_text=None,
    median_focus_axis_label=None,
    median_label=None,
):
    """Return compact arrays and optional localized labels for segment time evidence."""
    work_df = _prepare_temporal_metric_rows(plot_df)
    time_bin = str(time_bin)
    utc_date_count = _temporal_utc_date_count(work_df)
    if chronological_title is None:
        chronological_title = f"\u0394 SNR over Time ({time_bin} bins)"
    else:
        chronological_title = str(chronological_title).replace(
            "{time_bin}",
            time_bin,
        )
    if folded_title is None:
        folded_title = _default_folded_utc_hour_title(utc_date_count)
    else:
        folded_title = str(folded_title).replace(
            "{utc_date_count}",
            str(utc_date_count),
        )
    if folded_date_annotation is None:
        folded_date_annotation = _default_folded_utc_date_annotation(
            utc_date_count
        )
    else:
        folded_date_annotation = str(folded_date_annotation).replace(
            "{utc_date_count}",
            str(utc_date_count),
        )
    if density_label is None:
        density_label = _relative_density_label(count_label)
    median_focus = _compare_median_focus_recipe(
        _build_compare_median_focus_spec(work_df["metric"])
    )
    return {
        "kind": "segment_compare_temporal",
        "schema_version": 1,
        "title": str(title),
        "time_bin": time_bin,
        "count_label": str(count_label),
        "chronological_title": str(chronological_title),
        "chronological_x_label": str(
            chronological_x_label or "Date/Time (UTC)"
        ),
        "folded_title": str(folded_title),
        "folded_x_label": str(folded_x_label or "UTC hour"),
        "folded_date_annotation": str(folded_date_annotation),
        "density_label": str(density_label),
        "folded_unavailable_text": str(
            folded_unavailable_text
            or FOLDED_UTC_UNAVAILABLE_TEXT
        ),
        "median_focus": median_focus,
        "median_focus_axis_label": str(
            median_focus_axis_label
            or "\u0394 SNR (dB \u00b7 median-centered nonlinear)"
        ),
        "median_label": str(median_label or "Median"),
        "utc_date_count": utc_date_count,
        "plot_time_ns": (
            work_df["plot_time"]
            .to_numpy(dtype="datetime64[ns]")
            .astype(np.int64, copy=True)
        ),
        "metric": work_df["metric"].to_numpy(dtype=np.float64, copy=True),
    }


@synchronized_matplotlib
def render_segment_temporal_evidence_export_figure(recipe):
    """Render chronological and date-folded segment Compare relative densities."""
    if not recipe:
        return None
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

    time_bin = str(recipe.get("time_bin", "3h"))
    utc_date_count = _temporal_utc_date_count(work_df)
    is_folded_available = utc_date_count >= 2
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

    figure = create_agg_figure(figsize=(13, 5.6), facecolor="black")
    figure.subplots_adjust(
        left=0.07,
        right=0.95,
        bottom=SEGMENT_FIGURE_BOTTOM,
        top=0.82,
        wspace=0.20,
    )
    grid_spec = figure.add_gridspec(1, 2, width_ratios=[1.95, 1])
    chronological_axis = figure.add_subplot(grid_spec[0, 0])
    folded_axis = figure.add_subplot(grid_spec[0, 1], sharey=chronological_axis)
    for axis in (chronological_axis, folded_axis):
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
    )
    folded_mesh = None
    if is_folded_available:
        folded_mesh = _draw_relative_density_mesh(
            folded_axis,
            folded_edges,
            y_edges,
            folded_grid,
            density_norm=density_norm,
        )
        _draw_temporal_median_overlay(folded_axis, folded_centers, folded_medians)
    else:
        _draw_folded_utc_unavailable_annotation(
            folded_axis,
            recipe.get(
                "folded_unavailable_text",
                FOLDED_UTC_UNAVAILABLE_TEXT,
            ),
        )

    date_locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
    chronological_axis.xaxis.set_major_locator(date_locator)
    chronological_axis.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b\n%H:%M"))
    chronological_axis.set_xlim(chronological_edges[0], chronological_edges[-1])
    chronological_axis.set_title(
        recipe.get(
            "chronological_title",
            f"\u0394 SNR over Time ({time_bin} bins)",
        ),
        color="white",
        fontweight="bold",
        pad=10,
    )
    chronological_axis.set_xlabel(
        recipe.get("chronological_x_label", "Date/Time (UTC)"),
        color="white",
    )
    chronological_axis.set_ylabel("\u0394 SNR (dB)", color="white")

    folded_axis.set_xlim(0.0, 24.0)
    folded_axis.set_xticks(np.arange(0, 25, 3))
    folded_axis.set_xticklabels([f"{hour:02d}" for hour in range(0, 25, 3)])
    default_folded_title = _default_folded_utc_hour_title(utc_date_count)
    folded_axis.set_title(
        recipe.get("folded_title", default_folded_title),
        color="white",
        fontweight="bold",
        pad=10,
    )
    folded_axis.set_xlabel(
        recipe.get("folded_x_label", "UTC hour"),
        color="white",
    )
    for axis in (chronological_axis, folded_axis):
        _apply_compare_median_focus_axis(
            axis,
            median_focus_spec,
            axis_label=recipe.get(
                "median_focus_axis_label",
                "\u0394 SNR (dB \u00b7 median-centered nonlinear)",
            ),
            median_label=recipe.get("median_label", "Median"),
        )

    density_label = recipe.get("density_label") or _relative_density_label(
        recipe.get("count_label", "Joint spot count")
    )
    colorbar_mesh = folded_mesh if folded_mesh is not None else chronological_mesh
    colorbar = figure.colorbar(
        colorbar_mesh,
        ax=[chronological_axis, folded_axis],
        pad=0.012,
        fraction=0.03,
        ticks=np.linspace(EVIDENCE_DENSITY_MIN, EVIDENCE_DENSITY_MAX, 5),
    )
    colorbar.set_label(density_label, color="white")
    colorbar.ax.tick_params(colors="white", labelsize=8)
    colorbar.outline.set_edgecolor("#444444")

    figure.suptitle(
        recipe.get("title", "Compare Temporal Evidence"),
        color="white",
        fontweight="bold",
        fontsize=14,
        y=0.96,
    )
    figure.text(
        0.98,
        SEGMENT_FIGURE_FOOTER_Y,
        f"WSPRadar.org {APP_VERSION}",
        color="#888888",
        ha="right",
        fontsize=10,
    )
    return figure

@synchronized_matplotlib
def _create_selected_station_evidence_figure(
    plot_df,
    evidence_title,
    labels,
    time_agg,
    is_compare,
    is_sequential,
    *,
    stability_interval=None,
    temporal_view=SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL,
    folded_title=None,
    folded_x_label=None,
    density_label=None,
    folded_unavailable_text=None,
    median_focus=None,
    median_focus_axis_label=None,
):
    """Build selected evidence with a chronological or folded Compare time view."""
    temporal_view = (
        SELECTED_TEMPORAL_VIEW_UTC_HOUR
        if is_compare and temporal_view == SELECTED_TEMPORAL_VIEW_UTC_HOUR
        else SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL
    )
    labels = dict(labels)
    if density_label:
        labels["density_label"] = density_label
    evidence_count = len(plot_df)
    metric_values = _metric_values(plot_df["metric"])
    median_focus_spec = (
        _compare_median_focus_spec_from_recipe(median_focus, metric_values)
        if is_compare
        else None
    )
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
        if temporal_view == SELECTED_TEMPORAL_VIEW_UTC_HOUR:
            _draw_folded_utc_hour_heatmap(
                fig_ev,
                ax_time,
                plot_df,
                labels,
                is_sequential,
                folded_title=folded_title,
                folded_x_label=folded_x_label,
                density_label=density_label,
                folded_unavailable_text=folded_unavailable_text,
            )
        else:
            _draw_single_time_point(
                ax_time,
                plot_df,
                labels,
                is_compare=is_compare,
            )
    else:
        _draw_horizontal_metric_histogram(ax_cloud, metric_values, color=EVIDENCE_AGG_COLOR)
        ax_cloud.set_ylabel(labels["y_label"], color="white")
        if temporal_view == SELECTED_TEMPORAL_VIEW_UTC_HOUR:
            _draw_folded_utc_hour_heatmap(
                fig_ev,
                ax_time,
                plot_df,
                labels,
                is_sequential,
                folded_title=folded_title,
                folded_x_label=folded_x_label,
                density_label=density_label,
                folded_unavailable_text=folded_unavailable_text,
            )
        else:
            _draw_time_heatmap(
                fig_ev,
                ax_time,
                plot_df,
                time_agg,
                labels,
                is_compare,
                is_sequential,
            )
        if is_compare:
            _annotate_selected_compare_distribution(
                ax_cloud,
                metric_values,
                stability_interval,
                labels,
            )
    if is_compare and median_focus_spec is not None:
        resolved_axis_label = (
            median_focus_axis_label
            or labels.get(
                "median_focus_axis_label",
                "\u0394 SNR (dB \u00b7 median-centered nonlinear)",
            )
        )
        _apply_compare_median_focus_axis(
            ax_cloud,
            median_focus_spec,
            axis_label=resolved_axis_label,
            median_label=labels.get("median_label", "Median"),
            show_median_legend=False,
            draw_median_reference=False,
        )
        _apply_compare_median_focus_axis(
            ax_time,
            median_focus_spec,
            axis_label=resolved_axis_label,
            median_label=labels.get("median_label", "Median"),
            show_median_legend=True,
        )
    ax_time.tick_params(axis="x", labelrotation=0, labelsize=9)
    return fig_ev

def _selected_evidence_export_recipe(
    plot_df,
    evidence_title,
    labels,
    time_agg,
    is_compare,
    is_sequential,
    *,
    temporal_view=SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL,
    folded_title=None,
    folded_x_label=None,
    folded_date_annotation=None,
    density_label=None,
    folded_unavailable_text=None,
    median_focus_axis_label=None,
):
    """Store compact selected evidence and optional folded-view presentation state."""
    plot_times = pd.to_datetime(plot_df["plot_time"], errors="coerce", utc=True)
    numeric_metrics = pd.to_numeric(plot_df["metric"], errors="coerce")
    valid = plot_times.notna() & numeric_metrics.notna() & np.isfinite(numeric_metrics)
    metric_values = numeric_metrics.loc[valid].to_numpy(dtype=np.float64, copy=True)
    selected_identity_count = 1
    if "identity" in plot_df.columns:
        selected_identity_count = max(
            1,
            int(plot_df.loc[valid, "identity"].dropna().nunique()),
        )
    temporal_view = (
        SELECTED_TEMPORAL_VIEW_UTC_HOUR
        if is_compare and temporal_view == SELECTED_TEMPORAL_VIEW_UTC_HOUR
        else SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL
    )
    utc_date_count = int(plot_times.loc[valid].dt.normalize().nunique())
    if folded_title is None:
        folded_title = _default_folded_utc_hour_title(utc_date_count)
    else:
        folded_title = str(folded_title).replace(
            "{utc_date_count}",
            str(utc_date_count),
        )
    if folded_date_annotation is None:
        folded_date_annotation = _default_folded_utc_date_annotation(
            utc_date_count
        )
    else:
        folded_date_annotation = str(folded_date_annotation).replace(
            "{utc_date_count}",
            str(utc_date_count),
        )
    labels_copy = dict(labels)
    count_label = labels_copy.get("count_label")
    if not count_label:
        count_label = (
            "Scheduled pair count"
            if is_sequential
            else "Joint spot count"
            if is_compare
            else "Spot count"
        )
    if density_label is None and is_compare:
        density_label = labels_copy.get("density_label") or _relative_density_label(
            count_label
        )
    if is_compare:
        resolved_median_focus = _compare_median_focus_recipe(
            _build_compare_median_focus_spec(metric_values)
        )
    else:
        resolved_median_focus = None
    return {
        "title": evidence_title,
        "labels": labels_copy,
        "time_bin": time_agg,
        "is_compare": bool(is_compare),
        "is_sequential": bool(is_sequential),
        "temporal_view": temporal_view,
        "folded_title": str(folded_title),
        "folded_x_label": str(folded_x_label or "UTC hour"),
        "folded_date_annotation": str(folded_date_annotation),
        "density_label": str(density_label) if density_label else None,
        "folded_unavailable_text": str(
            folded_unavailable_text
            or FOLDED_UTC_UNAVAILABLE_TEXT
        ),
        "median_focus": resolved_median_focus,
        "median_focus_axis_label": str(
            median_focus_axis_label
            or labels_copy.get(
                "median_focus_axis_label",
                "\u0394 SNR (dB \u00b7 median-centered nonlinear)",
            )
        ),
        "utc_date_count": utc_date_count,
        "selected_identity_count": selected_identity_count,
        "stability_interval": (
            _bootstrap_median_interval(metric_values)
            if is_compare
            else None
        ),
        "plot_time_ns": (
            plot_times[valid]
            .dt.tz_convert(None)
            .to_numpy(dtype="datetime64[ns]")
            .astype(np.int64, copy=True)
        ),
        "metric": metric_values,
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
        stability_interval=recipe.get("stability_interval"),
        temporal_view=recipe.get(
            "temporal_view",
            SELECTED_TEMPORAL_VIEW_CHRONOLOGICAL,
        ),
        folded_title=recipe.get("folded_title"),
        folded_x_label=recipe.get("folded_x_label"),
        density_label=recipe.get("density_label"),
        folded_unavailable_text=recipe.get("folded_unavailable_text"),
        median_focus=recipe.get("median_focus"),
        median_focus_axis_label=recipe.get("median_focus_axis_label"),
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
    paired_evidence_title=None,
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
        "paired_evidence_title": (
            str(paired_evidence_title) if paired_evidence_title else None
        ),
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
        ax_panel.set_title("Decode Outcomes", color="white", fontweight="bold", pad=10)
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
            recipe.get("paired_evidence_title")
            or (
                "Scheduled-Pair \u0394 SNR"
                if is_sequential
                else "Joint-Spot \u0394 SNR"
            ),
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
        station_stability_artist = _add_vertical_stability_band(
            ax_hist,
            station_interval[1],
            station_interval[2],
        )
        station_median_line = _add_metric_median_reference(
            ax_hist,
            station_median,
            orientation="vertical",
            zorder=4.0 if is_compare else 2.0,
        )
        _apply_minimum_metric_xspan(ax_hist, center=station_median)
        station_legend_handles = [station_median_line]
        if station_stability_artist is not None:
            if is_compare:
                station_legend_handles.append(station_stability_artist)
            else:
                station_legend_handles.insert(0, station_stability_artist)
        _place_metric_legend_top_right(
            ax_hist,
            handles=station_legend_handles,
        )
        if is_compare:
            _add_metric_mean_annotation(
                ax_hist,
                float(np.mean(station_values)),
            )
    else:
        ax_hist.text(0.5, 0.5, "No data", color="white", ha="center", va="center", fontsize=12, transform=ax_hist.transAxes)
        ax_hist.set_xticks([])
        ax_hist.set_yticks([])

    spot_median = _draw_vertical_metric_histogram(ax_spot, spot_values, color="#36aaf9")
    if pd.notna(spot_median):
        spot_stability_artist = _add_vertical_stability_band(
            ax_spot,
            spot_interval[1],
            spot_interval[2],
        )
        spot_median_line = _add_metric_median_reference(
            ax_spot,
            spot_median,
            orientation="vertical",
            zorder=4.0 if is_compare else 2.0,
        )
        _apply_minimum_metric_xspan(ax_spot, center=spot_median)
        spot_legend_handles = [spot_median_line]
        if spot_stability_artist is not None:
            if is_compare:
                spot_legend_handles.append(spot_stability_artist)
            else:
                spot_legend_handles.insert(0, spot_stability_artist)
        _place_metric_legend_top_right(
            ax_spot,
            handles=spot_legend_handles,
        )
        if is_compare and len(spot_values):
            _add_metric_mean_annotation(
                ax_spot,
                float(np.mean(spot_values)),
            )
    else:
        ax_spot.text(0.5, 0.5, "No data", color="white", ha="center", va="center", fontsize=12, transform=ax_spot.transAxes)
        ax_spot.set_xticks([])
        ax_spot.set_yticks([])

    metric_label = "\u0394 SNR (dB)" if is_compare else "Normalized SNR (dB @ 1 W)"
    ax_hist.set_xlabel(metric_label, color="white")
    ax_spot.set_xlabel(metric_label, color="white")
    return fig_hist
