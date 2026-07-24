"""Shared numeric helpers for WSPRadar evidence distributions and axes."""

import numpy as np
import pandas as pd


METRIC_MIN_VISIBLE_SPAN_DB = 3.0
METRIC_HISTOGRAM_INTEGER_LATTICE_THRESHOLD = 0.95
METRIC_HISTOGRAM_HALF_DB_LATTICE_THRESHOLD = 0.95
METRIC_HISTOGRAM_MAX_BARS = 40
METRIC_HISTOGRAM_AGGREGATE_BIN_WIDTHS = (1.0, 2.0, 3.0, 6.0, 10.0)


def _format_metric_signed(value, is_compare):
    """Format one SNR-like value, using an explicit sign for comparisons."""
    if pd.isna(value):
        return "n/a"
    if is_compare:
        return f"{float(value):+.1f}"
    return f"{float(value):.1f}"


def _format_metric_interval(low, high, is_compare):
    """Format finite lower and upper metric bounds for compact display."""
    if pd.isna(low) or pd.isna(high):
        return "n/a"
    return (
        f"{_format_metric_signed(low, is_compare)} .. "
        f"{_format_metric_signed(high, is_compare)}"
    )


def _metric_values(values):
    """Return finite numeric SNR-like values as a one-dimensional numpy array."""
    numeric_values = (
        pd.to_numeric(pd.Series(values), errors="coerce")
        .dropna()
        .to_numpy(dtype=float)
    )
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
    """Return the number of centered bars needed to span the supplied bounds."""
    if not np.isfinite(min_value) or not np.isfinite(max_value) or bin_width <= 0:
        return 0
    start_center = (
        anchor + np.floor((min_value - anchor) / bin_width) * bin_width
    )
    end_center = (
        anchor + np.ceil((max_value - anchor) / bin_width) * bin_width
    )
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

    if (
        _metric_histogram_bar_count(
            min_value,
            max_value,
            anchor,
            base_width,
        )
        <= METRIC_HISTOGRAM_MAX_BARS
    ):
        return base_width, anchor

    for candidate_width in METRIC_HISTOGRAM_AGGREGATE_BIN_WIDTHS:
        if candidate_width < base_width:
            continue
        if (
            _metric_histogram_bar_count(
                min_value,
                max_value,
                anchor,
                candidate_width,
            )
            <= METRIC_HISTOGRAM_MAX_BARS
        ):
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
    start_center = (
        anchor + np.floor((min_value - anchor) / bin_width) * bin_width
    )
    end_center = (
        anchor + np.ceil((max_value - anchor) / bin_width) * bin_width
    )
    centers = np.arange(
        start_center,
        end_center + (bin_width * 0.5),
        bin_width,
    )
    if len(centers) == 0:
        centers = np.array([anchor])
    edges = np.concatenate(
        (
            centers - (bin_width / 2.0),
            [centers[-1] + (bin_width / 2.0)],
        )
    )
    return edges, centers, bin_width


def _format_bin_width(bin_width):
    """Format one histogram bin width with its dB unit."""
    return f"{float(bin_width):.1f} dB"


def _histogram_mode_summary(values):
    """Return the modal histogram center and its percentage share."""
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
    return (
        float(centers[mode_index]),
        100.0 * float(counts[mode_index]) / float(counts.sum()),
    )


def _zero_bin_share(values):
    """Return the percentage of values assigned to the histogram bin containing zero."""
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
        within_1_pct = (
            100.0 * float(np.sum(np.abs(values) <= 1.0)) / float(len(values))
        )
        tail_3_pct = (
            100.0 * float(np.sum(np.abs(values) >= 3.0)) / float(len(values))
        )
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
        f"90% range {_format_metric_interval(q05, q95, False)} dB"
    )


def _expanded_metric_limits(
    lower,
    upper,
    center=None,
    min_span=METRIC_MIN_VISIBLE_SPAN_DB,
):
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
