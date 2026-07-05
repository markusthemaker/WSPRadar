import pytest
import numpy as np

import core.stability as stability
from core.stability import (
    _bootstrap_median_interval,
    _expanded_metric_limits,
    _metric_histogram_bins,
)


def _reference_loop_bootstrap_median_interval(values, iterations=500, confidence=0.90, seed=42):
    value_array = np.asarray(values, dtype=float)
    median = float(np.median(value_array))
    rng = np.random.default_rng(seed)
    boot_medians = np.empty(iterations, dtype=float)
    for index in range(iterations):
        sample = value_array[rng.integers(0, len(value_array), len(value_array))]
        boot_medians[index] = np.median(sample)
    alpha = (1.0 - confidence) / 2.0
    low, high = np.quantile(boot_medians, [alpha, 1.0 - alpha])
    return median, float(low), float(high)


def test_bootstrap_median_interval_matches_reference_loop_contract():
    values = [-4.0, -1.0, 0.0, 2.0, 3.0, 9.0]
    optimized = _bootstrap_median_interval(values, iterations=37, confidence=0.80, seed=123)
    reference = _reference_loop_bootstrap_median_interval(values, iterations=37, confidence=0.80, seed=123)

    assert optimized == pytest.approx(reference)


def test_bootstrap_median_interval_matches_reference_loop_when_chunked(monkeypatch):
    values = [-4.0, -1.0, 0.0, 2.0, 3.0, 9.0]
    monkeypatch.setattr(stability, "STABILITY_BOOTSTRAP_MAX_SAMPLE_CELLS", 12)
    optimized = stability._bootstrap_median_interval(values, iterations=37, confidence=0.80, seed=123)
    reference = _reference_loop_bootstrap_median_interval(values, iterations=37, confidence=0.80, seed=123)

    assert optimized == pytest.approx(reference)


def test_bootstrap_median_interval_is_degenerate_for_identical_values():
    median, low, high = _bootstrap_median_interval([1.0, 1.0, 1.0, 1.0])

    assert median == pytest.approx(1.0)
    assert low == pytest.approx(1.0)
    assert high == pytest.approx(1.0)


def test_expanded_metric_limits_enforce_three_db_visible_span():
    lower, upper = _expanded_metric_limits(1.0, 1.0, center=1.0)

    assert lower == pytest.approx(-0.5)
    assert upper == pytest.approx(2.5)
    assert upper - lower == pytest.approx(3.0)


def test_expanded_metric_limits_preserve_existing_asymmetric_bounds():
    lower, upper = _expanded_metric_limits(0.0, 2.8, center=0.0)

    assert lower <= 0.0
    assert upper >= 2.8
    assert upper - lower == pytest.approx(3.0)


def test_metric_histogram_bins_include_single_value_without_zero_width():
    edges, centers, bin_width = _metric_histogram_bins([1.0, 1.0, 1.0])

    assert bin_width > 0.0
    assert edges[0] <= 1.0 <= edges[-1]
    assert len(centers) == len(edges) - 1
