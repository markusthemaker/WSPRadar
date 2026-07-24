import pytest

from core.evidence_statistics import (
    _expanded_metric_limits,
    _metric_distribution_summary,
    _metric_histogram_bins,
)


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


def test_success_distribution_keeps_empirical_ninety_percent_range():
    summary = _metric_distribution_summary(
        [-20.0, -10.0, 0.0, 10.0, 20.0],
        is_compare=False,
    )

    assert "90% range -18.0 .. 18.0 dB" in summary
    assert "Stability" not in summary
