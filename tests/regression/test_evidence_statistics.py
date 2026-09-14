import numpy as np
import pandas as pd
import pytest

from core.evidence_statistics import (
    _expanded_metric_limits,
    _metric_histogram_bins,
)
from ui.plots.evidence_figures import _temporal_metric_summary


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


def _scalar_temporal_summary(grouped_metrics, complete_bins):
    """Retain the scalar scientific contract independently of the native path."""
    return grouped_metrics.agg(
        median="median",
        count="count",
        q1=lambda values: values.quantile(0.25),
        q3=lambda values: values.quantile(0.75),
    ).reindex(complete_bins)


@pytest.mark.parametrize("observations_per_bin", range(1, 10))
def test_native_temporal_quartiles_preserve_sparse_raw_values_exactly(
    observations_per_bin,
):
    random = np.random.default_rng(20260913)
    metric = pd.Series(
        random.uniform(-60.0, 60.0, observations_per_bin * 50),
        name="metric",
    )
    grouped_metrics = metric.groupby(np.arange(len(metric)) % 50)
    complete_bins = pd.RangeIndex(52, name="time_bin")

    actual = _temporal_metric_summary(grouped_metrics, complete_bins)
    expected = _scalar_temporal_summary(grouped_metrics, complete_bins)

    # Sparse groups exercise both interpolation endpoints. Native grouped
    # "linear" quartiles alone are not bitwise equal to Series.quantile here.
    pd.testing.assert_frame_equal(actual, expected, check_exact=True)
    assert actual.loc[50:].isna().all().all()


@pytest.mark.parametrize("sort_groups", [False, True])
def test_native_temporal_quartiles_preserve_missing_values_and_group_order(
    sort_groups,
):
    metric = pd.Series(
        [1.1, -7.7, np.nan, 2.2, np.nan, -2.3, 8.6, 1.0],
        name="metric",
    )
    keys = pd.Series([7.0, 3.0, 5.0, 7.0, 5.0, 3.0, np.nan, np.nan])
    grouped_metrics = metric.groupby(keys, sort=sort_groups, dropna=False)
    complete_bins = pd.Index([np.nan, 3.0, 5.0, 7.0, 9.0], name="time_bin")

    actual = _temporal_metric_summary(grouped_metrics, complete_bins)
    expected = _scalar_temporal_summary(grouped_metrics, complete_bins)

    pd.testing.assert_frame_equal(actual, expected, check_exact=True)
    assert actual.loc[5.0, "count"] == 0
    assert actual.loc[5.0, ["median", "q1", "q3"]].isna().all()
    assert actual.loc[9.0].isna().all()


def test_native_temporal_quartiles_preserve_unobserved_categorical_bins():
    metric = pd.Series([1.1, 3.7, np.nan], name="metric")
    keys = pd.Categorical([2, 2, 4], categories=[4, 2, 6])
    grouped_metrics = metric.groupby(keys, observed=False, sort=False)
    complete_bins = pd.Index([6, 4, 2, 8], name="time_bin")

    pd.testing.assert_frame_equal(
        _temporal_metric_summary(grouped_metrics, complete_bins),
        _scalar_temporal_summary(grouped_metrics, complete_bins),
        check_exact=True,
    )


@pytest.mark.parametrize(
    "dtype", ["float64", "float32", "Float32", "Float64", "Int64", "object"]
)
@pytest.mark.parametrize("values", [[], [1, 2, None, 5], [None, None]])
def test_temporal_quartiles_preserve_empty_and_alternative_numeric_dtypes(
    dtype,
    values,
):
    metric = pd.Series(values, dtype=dtype, name="metric")
    grouped_metrics = metric.groupby(np.arange(len(metric)) % 2)
    complete_bins = pd.RangeIndex(3, name="utc_hour")

    pd.testing.assert_frame_equal(
        _temporal_metric_summary(grouped_metrics, complete_bins),
        _scalar_temporal_summary(grouped_metrics, complete_bins),
        check_exact=True,
    )


def test_float64_temporal_quartiles_do_not_call_python_for_each_group(monkeypatch):
    metric = pd.Series([1.1, 2.7, 3.1, 4.9], name="metric")
    grouped_metrics = metric.groupby([0, 0, 1, 1])
    native_aggregate = grouped_metrics.agg

    def aggregate_without_callbacks(*args, **kwargs):
        assert all(not callable(value) for value in kwargs.values())
        return native_aggregate(*args, **kwargs)

    monkeypatch.setattr(grouped_metrics, "agg", aggregate_without_callbacks)

    result = _temporal_metric_summary(grouped_metrics, pd.RangeIndex(2))

    assert list(result.columns) == ["median", "count", "q1", "q3"]
    assert result["count"].tolist() == [2, 2]


@pytest.mark.parametrize(
    "values",
    [
        [1.0, 2.0, np.inf, np.inf, np.inf],
        [-np.inf, -np.inf, -np.inf, 2.0, 3.0],
        [-np.inf, 1.0, 2.0, 3.0, np.inf],
    ],
)
def test_temporal_quartiles_preserve_infinite_value_interpolation(values):
    metric = pd.Series(values, name="metric")
    grouped_metrics = metric.groupby(np.zeros(len(metric), dtype=int))
    complete_bins = pd.RangeIndex(2, name="time_bin")

    with np.errstate(invalid="ignore"):
        actual = _temporal_metric_summary(grouped_metrics, complete_bins)
        expected = _scalar_temporal_summary(grouped_metrics, complete_bins)

    pd.testing.assert_frame_equal(actual, expected, check_exact=True)
