"""Exact grouping, time-key and compact-count contracts for temporal evidence."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ui.inspector import preparation
from ui.plots import opportunity_figures as figures


def _assert_arrays_equal(expected, actual):
    assert expected.keys() == actual.keys()
    for key in expected:
        assert expected[key].dtype == actual[key].dtype, key
        np.testing.assert_array_equal(expected[key], actual[key], err_msg=key)


def _rows(unit="ns", nonbinary=False):
    size = 900
    times = pd.date_range("2026-01-01T00:14Z", periods=size, freq="2min").as_unit(unit)
    hits = (np.arange(size) % 3 != 0).astype("int64")
    misses = 1 - hits
    if nonbinary:
        hits *= 200
        misses *= 300
    return pd.DataFrame({
        "peer_sign": np.resize(["Z9", "A1", "A1", None], size),
        "peer_grid": np.resize(["JO62", "JO62", "JO63", "JO62"], size),
        "evidence_utc": times,
        "hit": hits, "miss": misses,
        "target_snr": np.resize([-17.0, -4.0, np.nan, -3.5, -8.0], size),
    })


@pytest.mark.parametrize("unit", ["s", "us", "ns"])
@pytest.mark.parametrize("nonbinary", [False, True])
def test_prepared_keys_preserve_every_temporal_reducer(unit, nonbinary):
    start = pd.Timestamp("2026-01-01T00:13:17.123456Z")
    end = pd.Timestamp("2026-01-03T03:17:22.654321Z")
    original = _rows(unit, nonbinary)
    untouched = original.copy(deep=True)
    compact = figures._prepare_success_temporal_keys(original.copy(), start)
    expected_elapsed = np.array([(value - start).value for value in original.evidence_utc])
    np.testing.assert_array_equal(compact["_elapsed_nanoseconds"], expected_elapsed)
    assert compact["hit"].dtype == np.dtype("int64" if nonbinary else "int8")
    for time_bin in ("1h", "2h", "3h", "6h", "12h", "24h"):
        _assert_arrays_equal(
            figures._aggregate_success_chronological_profile(original, start, end, time_bin),
            figures._aggregate_success_chronological_profile(compact, start, end, time_bin),
        )
    _assert_arrays_equal(
        figures._aggregate_success_folded_profile(original, start, end),
        figures._aggregate_success_folded_profile(compact, start, end),
    )
    baseline_anomalies, baseline_stations = figures._prepare_success_snr_anomalies(original)
    compact_anomalies, compact_stations = figures._prepare_success_snr_anomalies(compact)
    identity_columns = list(baseline_stations.columns)
    pd.testing.assert_frame_equal(baseline_stations, compact_stations[identity_columns], check_exact=True)
    centers, edges = figures._success_snr_anomaly_axis(baseline_anomalies.snr_anomaly_db)
    for time_bin in ("1h", "2h", "3h", "6h", "12h", "24h"):
        _assert_arrays_equal(
            figures._aggregate_success_chronological_snr(baseline_anomalies, start, end, time_bin, centers, edges),
            figures._aggregate_success_chronological_snr(compact_anomalies, start, end, time_bin, centers, edges),
        )
    _assert_arrays_equal(
        figures._aggregate_success_folded_snr(baseline_anomalies, centers, edges),
        figures._aggregate_success_folded_snr(compact_anomalies, centers, edges),
    )
    pd.testing.assert_frame_equal(original, untouched, check_exact=True)


@pytest.mark.parametrize("missing_start,missing_end", [(False, False), (True, False), (False, True), (True, True)])
def test_explicit_performance_bounds_avoid_unused_timestamp_materialization(monkeypatch, missing_start, missing_end):
    source = pd.DataFrame({"peer_sign": ["A1", "A1"], "peer_grid": ["JO62", "JO63"], "time_slot": [1, 2]})
    scope = source[["peer_sign", "peer_grid"]].copy()
    monkeypatch.setattr(preparation, "read_parquet_artifact", lambda *args, **kwargs: source.copy(deep=True))
    conversions = []
    times = pd.Series(pd.to_datetime(["2026-01-01T00:02Z", "2026-01-01T00:04Z"]))
    def convert(slots):
        conversions.append(slots.tolist())
        return times.copy()
    monkeypatch.setattr(preparation, "opportunity_utc_from_time_slot", convert)
    start = None if missing_start else pd.Timestamp("2026-01-01T00:00Z")
    end = None if missing_end else pd.Timestamp("2026-01-01T01:00Z")
    rows, actual_start, actual_end = preparation.InspectorPreparation({}, 1)._prepare_performance_rows(
        scope, parquet_path="unused.parquet", analysis_id="RX_PERFORMANCE",
        analysis_start_t=start, analysis_end_t=end,
    )
    assert len(conversions) == int(missing_start or missing_end)
    assert actual_start == (times.min() if missing_start else start)
    assert actual_end == (times.max() + pd.Timedelta(minutes=2) if missing_end else end)
    assert len(rows) == len(source)
    assert isinstance(rows.peer_sign.dtype, pd.CategoricalDtype)
    assert isinstance(rows.peer_grid.dtype, pd.CategoricalDtype)
    pd.testing.assert_frame_equal(scope, source[["peer_sign", "peer_grid"]])


@pytest.mark.parametrize("unit", ["s", "us", "ns"])
@pytest.mark.parametrize("empty", [False, True])
def test_prepared_keys_preserve_selected_actual_snr_reducers(unit, empty):
    start = pd.Timestamp("2026-01-01T00:13:17.123456Z")
    end = pd.Timestamp("2026-01-03T03:17:22.654321Z")
    original = _rows(unit)
    original = original.loc[
        (original.peer_sign == "A1") & (original.peer_grid == "JO62")
    ].copy()
    if empty:
        original = original.iloc[:0].copy()
    untouched = original.copy(deep=True)
    compact = figures._prepare_success_temporal_keys(original.copy(), start)
    expected_rows = figures._prepare_success_actual_snr(original)
    actual_rows = figures._prepare_success_actual_snr(compact)
    edges = figures._success_actual_snr_axis(expected_rows.target_snr)
    for time_bin in ("1h", "2h", "3h", "6h", "12h", "24h"):
        _assert_arrays_equal(
            figures._aggregate_success_chronological_actual_snr(
                expected_rows, start, end, time_bin, edges,
            ),
            figures._aggregate_success_chronological_actual_snr(
                actual_rows, start, end, time_bin, edges,
            ),
        )
    _assert_arrays_equal(
        figures._aggregate_success_folded_actual_snr(expected_rows, edges),
        figures._aggregate_success_folded_actual_snr(actual_rows, edges),
    )
    pd.testing.assert_frame_equal(original, untouched, check_exact=True)


def test_full_recipe_preserves_category_identity_join_and_exact_eligibility():
    from core.presentation_context import PresentationContext
    from i18n import T
    from ui.inspector.presentation import success_figure_labels

    start = pd.Timestamp("2026-01-01T00:00Z")
    end = pd.Timestamp("2026-01-03T00:00Z")
    first_slot = start.value // pd.Timedelta(minutes=2).value
    records = []
    for sign, grid, values in (
        ("A1", "JO62", [-10.0, -8.0, -6.0]),
        ("A1", "JO63", [-4.0, -2.0, 0.0]),
        ("X9", "JO62", [-1.0, -1.0, -1.0]),
        ("A1", "JO99", [-1.0, -1.0, -1.0]),
    ):
        for offset, value in enumerate(values, start=1):
            records.append((first_slot + offset, sign, grid, 1, 0, value))
    records.extend([
        (first_slot + 1, "Z9", "JO62", 0, 1, np.nan),
        (first_slot + 2, "Z9", "JO62", 1, 0, -12.0),
        (first_slot + 720, None, "JO62", 0, 1, np.nan),
    ])
    rows = pd.DataFrame(records, columns=[
        "time_slot", "peer_sign", "peer_grid", "hit", "miss", "target_snr",
    ])
    peers = pd.DataFrame({
        "peer_sign": ["Z9", "A1", "A1", "X9", None],
        "peer_grid": ["JO62", "JO63", "JO62", "JO62", "JO62"],
        "eligible": [True, True, True, False, True],
        "rate_pct": [50.0, 100.0, 100.0, 100.0, 0.0],
    })
    categorical_rows = rows.copy(deep=True)
    categorical_peers = peers.copy(deep=True)
    for column, categories in (
        ("peer_sign", ["Z9", "UNUSED", "X9", "A1"]),
        ("peer_grid", ["JO99", "UNUSED", "JO63", "JO62"]),
    ):
        categorical_rows[column] = pd.Categorical(
            rows[column], categories=categories, ordered=True,
        )
        categorical_peers[column] = pd.Categorical(
            peers[column], categories=list(reversed(categories)), ordered=True,
        )
    untouched_rows = categorical_rows.copy(deep=True)
    untouched_peers = categorical_peers.copy(deep=True)
    context = PresentationContext(solar_label="All", labels=T["en"])

    def build(peer_rows, evidence_rows):
        return figures._opportunity_temporal_recipe(
            "Performance", "All", peer_rows, evidence_rows, start, end,
            context.absolute_terms("RX"),
            figure_labels=success_figure_labels(T["en"], "RX_PERFORMANCE"),
            time_bin_options=("1h", "6h", "24h"), time_bin_default="6h",
        )

    expected = build(peers, rows)
    actual = build(categorical_peers, categorical_rows)
    for time_bin in expected["time_bin_options"]:
        _assert_arrays_equal(
            expected["chronological_profiles"][time_bin],
            actual["chronological_profiles"][time_bin],
        )
    _assert_arrays_equal(expected["folded_profile"], actual["folded_profile"])
    numerical_profiles = {"chronological_profiles", "folded_profile"}
    assert {key: value for key, value in expected.items() if key not in numerical_profiles} == {
        key: value for key, value in actual.items() if key not in numerical_profiles
    }
    # Hand-counted oracle prevents identical join mistakes in the two routes
    # from being hidden by an equivalence-only assertion: X9 is ineligible and
    # A1/JO99 is not an eligible callsign-plus-locator identity.
    chronological = actual["chronological_profiles"]["1h"]
    assert chronological["target_counts"].sum() == 7
    assert chronological["counter_counts"].sum() == 2
    assert chronological["station_counts"][0] == 3
    assert chronological["station_counts"][24] == 1
    assert actual["snr_baseline_station_count"] == 2
    assert actual["utc_date_count"] == 2
    assert actual["folded_profile"]["represented_utc_date_counts"][13] == 2
    pd.testing.assert_frame_equal(categorical_rows, untouched_rows, check_exact=True)
    pd.testing.assert_frame_equal(categorical_peers, untouched_peers, check_exact=True)
