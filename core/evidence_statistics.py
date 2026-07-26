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
