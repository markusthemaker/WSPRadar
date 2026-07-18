"""Regression tests for deterministic periodic hardware A/B schedules."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from core.tx_ab_schedule import (
    TX_AB_REPEAT_INTERVAL_OPTIONS,
    assign_tx_ab_pair_columns,
    tx_ab_minutes_in_hour,
    tx_ab_schedule_sql,
    tx_ab_separation_minutes,
    tx_ab_start_minutes,
    validate_tx_ab_schedule,
)


def test_schedule_constants_and_hour_previews_are_stable():
    assert TX_AB_REPEAT_INTERVAL_OPTIONS == (4, 6, 10, 12, 20, 30, 60)
    assert tx_ab_start_minutes(10, 0) == (0, 10, 20, 30, 40, 50)
    assert tx_ab_start_minutes(20, 20) == (0, 20, 40)
    assert tx_ab_minutes_in_hour(10, 0, 2) == {
        "target": (0, 10, 20, 30, 40, 50),
        "reference": (2, 12, 22, 32, 42, 52),
    }


@pytest.mark.parametrize("repeat_interval_minutes", [4, 6, 10, 12, 20, 30, 60])
def test_validation_accepts_every_supported_repeat_interval(repeat_interval_minutes):
    assert validate_tx_ab_schedule(repeat_interval_minutes, 0, 2) == (
        repeat_interval_minutes,
        0,
        2,
    )


@pytest.mark.parametrize(
    ("repeat_interval_minutes", "target_start", "reference_start", "message"),
    [
        (8, 0, 2, "must be one of"),
        (True, 0, 2, "must be an integer"),
        (10, 1, 2, "must be an even UTC minute"),
        (10, 0, 3, "must be an even UTC minute"),
        (10, -2, 2, "must be between 0 and 59"),
        (10, 0, 60, "must be between 0 and 59"),
        (20, 0, 20, "must be disjoint"),
    ],
)
def test_validation_rejects_unsupported_or_overlapping_schedules(
    repeat_interval_minutes,
    target_start,
    reference_start,
    message,
):
    with pytest.raises(ValueError, match=message):
        validate_tx_ab_schedule(
            repeat_interval_minutes,
            target_start,
            reference_start,
        )


def test_sql_predicate_uses_canonical_phase_and_rejects_identifier_injection():
    assert tx_ab_schedule_sql(20, 20) == "toMinute(time) % 20 = 0"
    assert (
        tx_ab_schedule_sql(10, 2, time_column="spots.time")
        == "toMinute(spots.time) % 10 = 2"
    )
    with pytest.raises(ValueError, match="SQL identifier"):
        tx_ab_schedule_sql(10, 0, time_column="time) OR 1 = 1")


def test_cyclic_separation_reports_the_shortest_distance():
    assert tx_ab_separation_minutes(10, 0, 2) == 2
    assert tx_ab_separation_minutes(10, 0, 8) == 2
    assert tx_ab_separation_minutes(10, 8, 0) == 2
    assert tx_ab_separation_minutes(4, 0, 2) == 2


def test_pair_assignment_filters_schedule_rows_and_preserves_duplicate_decodes():
    source = pd.DataFrame(
        {
            "time": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:45Z",
                "2026-01-01T00:02:00Z",
                "2026-01-01T00:10:00Z",
                "2026-01-01T00:12:00Z",
                "2026-01-01T00:04:00Z",
                "2026-01-01T00:02:00Z",
                "not-a-time",
            ],
            "is_me": [1, 1, 0, 1, 0, 1, 1, 0],
            "receiver": ["A", "B", "A", "A", "A", "X", "X", "X"],
        },
        index=[10, 10, 12, 13, 14, 15, 16, 17],
    )
    original = source.copy(deep=True)

    paired = assign_tx_ab_pair_columns(
        source,
        repeat_interval_minutes=10,
        target_start_minute_utc=0,
        reference_start_minute_utc=2,
    )

    pd.testing.assert_frame_equal(source, original)
    assert paired["receiver"].tolist() == ["A", "B", "A", "A", "A"]
    expected_pair_times = pd.to_datetime(
        [
            "2026-01-01T00:00:00Z",
            "2026-01-01T00:00:00Z",
            "2026-01-01T00:00:00Z",
            "2026-01-01T00:10:00Z",
            "2026-01-01T00:10:00Z",
        ],
        utc=True,
    )
    expected_pair_times = pd.DatetimeIndex(
        expected_pair_times.to_numpy(dtype="datetime64[ns]"),
        tz="UTC",
    )
    assert paired["tx_ab_pair_id"].dtype == np.dtype("int64")
    np.testing.assert_array_equal(
        paired["tx_ab_pair_id"].to_numpy(),
        expected_pair_times.to_numpy(dtype="datetime64[ns]").astype("int64")
        // 60_000_000_000,
    )
    pd.testing.assert_series_equal(
        paired["tx_ab_pair_target_time"].reset_index(drop=True),
        pd.Series(expected_pair_times, name="tx_ab_pair_target_time"),
    )
    pd.testing.assert_series_equal(
        paired["tx_ab_pair_reference_time"].reset_index(drop=True),
        pd.Series(
            expected_pair_times + pd.Timedelta(minutes=2),
            name="tx_ab_pair_reference_time",
        ),
    )


def test_nearest_pairing_uses_the_previous_reference_when_it_is_closer():
    source = pd.DataFrame(
        {
            "time": [
                "2026-01-01T09:58:00Z",
                "2026-01-01T10:00:00Z",
                "2026-01-01T10:08:00Z",
                "2026-01-01T10:10:00Z",
            ],
            "path": ["reference", "target", "reference", "target"],
        }
    )

    paired = assign_tx_ab_pair_columns(
        source,
        repeat_interval_minutes=10,
        target_start_minute_utc=0,
        reference_start_minute_utc=8,
        path_column="path",
        target_path_value="target",
        reference_path_value="reference",
    )

    assert paired["tx_ab_pair_target_time"].tolist() == list(
        pd.to_datetime(
            [
                "2026-01-01T10:00:00Z",
                "2026-01-01T10:00:00Z",
                "2026-01-01T10:10:00Z",
                "2026-01-01T10:10:00Z",
            ],
            utc=True,
        )
    )
    assert paired["tx_ab_pair_reference_time"].tolist() == list(
        pd.to_datetime(
            [
                "2026-01-01T09:58:00Z",
                "2026-01-01T09:58:00Z",
                "2026-01-01T10:08:00Z",
                "2026-01-01T10:08:00Z",
            ],
            utc=True,
        )
    )


def test_equidistant_pairing_is_role_independent_within_the_same_cycle():
    source = pd.DataFrame(
        {
            "time": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:02:00Z",
                "2026-01-01T00:04:00Z",
            ],
            "path": ["reference", "target", "reference"],
        }
    )

    paired = assign_tx_ab_pair_columns(
        source,
        repeat_interval_minutes=4,
        target_start_minute_utc=2,
        reference_start_minute_utc=0,
        path_column="path",
        target_path_value="target",
        reference_path_value="reference",
    )

    assert paired["tx_ab_pair_target_time"].tolist() == list(
        pd.to_datetime(
            [
                "2026-01-01T00:02:00Z",
                "2026-01-01T00:02:00Z",
                "2026-01-01T00:06:00Z",
            ],
            utc=True,
        )
    )
    assert paired["tx_ab_pair_reference_time"].tolist() == list(
        pd.to_datetime(
            [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:04:00Z",
            ],
            utc=True,
        )
    )

    swapped = assign_tx_ab_pair_columns(
        source,
        repeat_interval_minutes=4,
        target_start_minute_utc=0,
        reference_start_minute_utc=2,
        path_column="path",
        target_path_value="reference",
        reference_path_value="target",
    )
    original_unordered_pairs = {
        frozenset((target_time, reference_time))
        for target_time, reference_time in paired[
            ["tx_ab_pair_target_time", "tx_ab_pair_reference_time"]
        ].itertuples(index=False, name=None)
    }
    swapped_unordered_pairs = {
        frozenset((target_time, reference_time))
        for target_time, reference_time in swapped[
            ["tx_ab_pair_target_time", "tx_ab_pair_reference_time"]
        ].itertuples(index=False, name=None)
    }
    assert swapped_unordered_pairs == original_unordered_pairs


def test_boundary_filter_requires_both_planned_starts_inside_inclusive_bounds():
    source = pd.DataFrame(
        {
            "time": pd.to_datetime(
                [
                    "2026-01-01T00:00:00Z",
                    "2026-01-01T00:08:00Z",
                    "2026-01-01T00:10:00Z",
                ],
                utc=True,
            ),
            "is_me": [1, 0, 1],
        }
    )

    paired = assign_tx_ab_pair_columns(
        source,
        repeat_interval_minutes=10,
        target_start_minute_utc=0,
        reference_start_minute_utc=8,
        start_time="2026-01-01T00:00:00Z",
        end_time="2026-01-01T00:10:00Z",
        exclude_boundary_pairs=True,
    )

    assert paired["time"].tolist() == list(
        pd.to_datetime(
            ["2026-01-01T00:08:00Z", "2026-01-01T00:10:00Z"],
            utc=True,
        )
    )
    assert paired["tx_ab_pair_target_time"].nunique() == 1
    assert paired.iloc[0]["tx_ab_pair_target_time"] == pd.Timestamp(
        "2026-01-01T00:10:00Z"
    )
    assert paired.iloc[0]["tx_ab_pair_reference_time"] == pd.Timestamp(
        "2026-01-01T00:08:00Z"
    )


def test_empty_pair_result_has_contract_dtypes_and_invalid_bounds_fail():
    source = pd.DataFrame(
        {"time": ["2026-01-01T00:04:00Z"], "is_me": [1]}
    )
    paired = assign_tx_ab_pair_columns(
        source,
        repeat_interval_minutes=10,
        target_start_minute_utc=0,
        reference_start_minute_utc=2,
    )

    assert paired.empty
    assert paired["tx_ab_pair_id"].dtype == np.dtype("int64")
    assert str(paired["tx_ab_pair_target_time"].dtype) == "datetime64[ns, UTC]"
    assert str(paired["tx_ab_pair_reference_time"].dtype) == "datetime64[ns, UTC]"

    with pytest.raises(ValueError, match="start_time must be less"):
        assign_tx_ab_pair_columns(
            source,
            repeat_interval_minutes=10,
            target_start_minute_utc=0,
            reference_start_minute_utc=2,
            start_time="2026-01-02T00:00:00Z",
            end_time="2026-01-01T00:00:00Z",
        )
