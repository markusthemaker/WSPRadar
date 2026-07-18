"""Pure helpers for deterministic periodic hardware A/B transmission schedules."""

from __future__ import annotations

from numbers import Integral
import re

import numpy as np
import pandas as pd

from config.config_schema import TX_AB_REPEAT_INTERVAL_OPTIONS

_MINUTES_PER_HOUR = 60
_NANOSECONDS_PER_MINUTE = 60_000_000_000
_SQL_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$"
)


def _validated_repeat_interval(repeat_interval_minutes: int) -> int:
    """Return a supported integral repeat interval or raise ``ValueError``."""
    if isinstance(repeat_interval_minutes, bool) or not isinstance(
        repeat_interval_minutes, Integral
    ):
        raise ValueError("repeat_interval_minutes must be an integer")
    repeat_interval_minutes = int(repeat_interval_minutes)
    if repeat_interval_minutes not in TX_AB_REPEAT_INTERVAL_OPTIONS:
        allowed = ", ".join(str(option) for option in TX_AB_REPEAT_INTERVAL_OPTIONS)
        raise ValueError(
            f"repeat_interval_minutes must be one of: {allowed}"
        )
    return repeat_interval_minutes


def _validated_start_minute(start_minute_utc: int, *, field_name: str) -> int:
    """Return an even UTC minute within an hour or raise ``ValueError``."""
    if isinstance(start_minute_utc, bool) or not isinstance(start_minute_utc, Integral):
        raise ValueError(f"{field_name} must be an integer")
    start_minute_utc = int(start_minute_utc)
    if not 0 <= start_minute_utc < _MINUTES_PER_HOUR:
        raise ValueError(f"{field_name} must be between 0 and 59")
    if start_minute_utc % 2:
        raise ValueError(f"{field_name} must be an even UTC minute")
    return start_minute_utc


def _canonical_start_phase(
    repeat_interval_minutes: int,
    start_minute_utc: int,
    *,
    field_name: str,
) -> tuple[int, int]:
    """Return a validated interval and the start's canonical periodic phase."""
    repeat_interval_minutes = _validated_repeat_interval(repeat_interval_minutes)
    start_minute_utc = _validated_start_minute(
        start_minute_utc,
        field_name=field_name,
    )
    return repeat_interval_minutes, start_minute_utc % repeat_interval_minutes


def tx_ab_start_minutes(
    repeat_interval_minutes: int,
    start_minute_utc: int,
) -> tuple[int, ...]:
    """Return all UTC start minutes in an hour for one periodic transmitter path.

    ``start_minute_utc`` may name any occurrence in the hour. For example,
    interval 20 with start 20 is the same periodic phase as start 0 and returns
    ``(0, 20, 40)``.
    """
    repeat_interval_minutes, start_phase = _canonical_start_phase(
        repeat_interval_minutes,
        start_minute_utc,
        field_name="start_minute_utc",
    )
    return tuple(
        minute
        for minute in range(_MINUTES_PER_HOUR)
        if minute % repeat_interval_minutes == start_phase
    )


def validate_tx_ab_schedule(
    repeat_interval_minutes: int,
    target_start_minute_utc: int,
    reference_start_minute_utc: int,
) -> tuple[int, int, int]:
    """Validate a periodic A/B schedule and return its canonical phases.

    The two starts must be distinct modulo the repeat interval; otherwise both
    paths request the same physical transmission slots. Returned values are the
    validated interval, Target phase, and Reference phase.
    """
    repeat_interval_minutes, target_start_phase = _canonical_start_phase(
        repeat_interval_minutes,
        target_start_minute_utc,
        field_name="target_start_minute_utc",
    )
    _, reference_start_phase = _canonical_start_phase(
        repeat_interval_minutes,
        reference_start_minute_utc,
        field_name="reference_start_minute_utc",
    )
    if target_start_phase == reference_start_phase:
        raise ValueError(
            "Target and Reference starts must be disjoint modulo the repeat interval"
        )
    return repeat_interval_minutes, target_start_phase, reference_start_phase


def tx_ab_schedule_sql(
    repeat_interval_minutes: int,
    start_minute_utc: int,
    *,
    time_column: str = "time",
) -> str:
    """Return a ClickHouse predicate selecting one periodic UTC start family.

    The predicate is safe to interpolate into existing SQL only after the time
    column passes the strict dotted-identifier check performed here.
    """
    repeat_interval_minutes, start_phase = _canonical_start_phase(
        repeat_interval_minutes,
        start_minute_utc,
        field_name="start_minute_utc",
    )
    if not isinstance(time_column, str) or not _SQL_IDENTIFIER_PATTERN.fullmatch(
        time_column
    ):
        raise ValueError("time_column must be a plain or dotted SQL identifier")
    return f"toMinute({time_column}) % {repeat_interval_minutes} = {start_phase}"


def tx_ab_minutes_in_hour(
    repeat_interval_minutes: int,
    target_start_minute_utc: int,
    reference_start_minute_utc: int,
) -> dict[str, tuple[int, ...]]:
    """Return the Target and Reference UTC start-minute previews for one hour."""
    validate_tx_ab_schedule(
        repeat_interval_minutes,
        target_start_minute_utc,
        reference_start_minute_utc,
    )
    return {
        "target": tx_ab_start_minutes(
            repeat_interval_minutes,
            target_start_minute_utc,
        ),
        "reference": tx_ab_start_minutes(
            repeat_interval_minutes,
            reference_start_minute_utc,
        ),
    }


def tx_ab_separation_minutes(
    repeat_interval_minutes: int,
    target_start_minute_utc: int,
    reference_start_minute_utc: int,
) -> int:
    """Return the shortest cyclic separation between the two periodic starts."""
    (
        repeat_interval_minutes,
        target_start_phase,
        reference_start_phase,
    ) = validate_tx_ab_schedule(
        repeat_interval_minutes,
        target_start_minute_utc,
        reference_start_minute_utc,
    )
    forward_separation = (
        reference_start_phase - target_start_phase
    ) % repeat_interval_minutes
    backward_separation = repeat_interval_minutes - forward_separation
    return min(forward_separation, backward_separation)


def _reference_offset_minutes(
    repeat_interval_minutes: int,
    target_start_phase: int,
    reference_start_phase: int,
) -> int:
    """Return the nearest role-independent Reference offset from Target.

    On an exact half-interval tie, the lower and higher phases are paired in
    the same repeat cycle. This keeps the physical unordered pairs unchanged
    when the Target and Reference labels are swapped.
    """
    lower_start_phase = min(target_start_phase, reference_start_phase)
    higher_start_phase = max(target_start_phase, reference_start_phase)
    within_cycle_distance = higher_start_phase - lower_start_phase
    across_cycle_distance = repeat_interval_minutes - within_cycle_distance
    pairs_within_cycle = within_cycle_distance <= across_cycle_distance

    if pairs_within_cycle:
        return reference_start_phase - target_start_phase
    if target_start_phase == lower_start_phase:
        return -across_cycle_distance
    return across_cycle_distance


def _utc_bound(timestamp, *, field_name: str) -> pd.Timestamp | None:
    """Normalize one optional analysis bound to a timezone-aware UTC timestamp."""
    if timestamp is None:
        return None
    try:
        utc_timestamp = pd.Timestamp(timestamp)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid timestamp") from exc
    if pd.isna(utc_timestamp):
        raise ValueError(f"{field_name} must be a valid timestamp")
    if utc_timestamp.tzinfo is None:
        return utc_timestamp.tz_localize("UTC")
    return utc_timestamp.tz_convert("UTC")


def _attach_empty_pair_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Attach the stable pair-column dtypes to an empty copied frame."""
    frame["tx_ab_pair_id"] = pd.Series(index=frame.index, dtype="int64")
    frame["tx_ab_pair_target_time"] = pd.Series(
        pd.NaT,
        index=frame.index,
        dtype="datetime64[ns, UTC]",
    )
    frame["tx_ab_pair_reference_time"] = pd.Series(
        pd.NaT,
        index=frame.index,
        dtype="datetime64[ns, UTC]",
    )
    return frame


def assign_tx_ab_pair_columns(
    frame: pd.DataFrame,
    *,
    repeat_interval_minutes: int,
    target_start_minute_utc: int,
    reference_start_minute_utc: int,
    time_column: str = "time",
    path_column: str = "is_me",
    target_path_value=1,
    reference_path_value=0,
    start_time=None,
    end_time=None,
    exclude_boundary_pairs: bool = False,
) -> pd.DataFrame:
    """Filter decoded rows to a periodic schedule and attach planned pair slots.

    Each scheduled Target slot is paired bijectively with its nearest Reference
    slot. On an equal half-interval distance, the lower and higher phases are
    paired within the same repeat cycle, independent of their A/B roles. Multiple
    decode rows for one transmission are retained and receive the same pair identity.
    ``tx_ab_pair_id`` is the absolute planned Target-start epoch minute. Planned
    timestamps are timezone-aware UTC values.

    Observation timestamps are restricted to the optional inclusive analysis
    bounds. When ``exclude_boundary_pairs`` is true, a pair is retained only if
    both planned starts also fall inside every supplied bound. Invalid times,
    unknown paths, and rows outside their path's schedule are excluded. The
    input frame is never mutated.
    """
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame")
    missing_columns = [
        column for column in (time_column, path_column) if column not in frame.columns
    ]
    if missing_columns:
        raise KeyError(f"Missing required columns: {', '.join(missing_columns)}")
    if target_path_value == reference_path_value:
        raise ValueError("target_path_value and reference_path_value must differ")
    if not isinstance(exclude_boundary_pairs, bool):
        raise ValueError("exclude_boundary_pairs must be a boolean")

    (
        repeat_interval_minutes,
        target_start_phase,
        reference_start_phase,
    ) = validate_tx_ab_schedule(
        repeat_interval_minutes,
        target_start_minute_utc,
        reference_start_minute_utc,
    )
    analysis_start_time = _utc_bound(start_time, field_name="start_time")
    analysis_end_time = _utc_bound(end_time, field_name="end_time")
    if (
        analysis_start_time is not None
        and analysis_end_time is not None
        and analysis_start_time > analysis_end_time
    ):
        raise ValueError("start_time must be less than or equal to end_time")

    decoded_times = pd.to_datetime(frame[time_column], utc=True, errors="coerce")
    valid_times = decoded_times.notna().to_numpy()
    observation_mask = valid_times.copy()
    if analysis_start_time is not None:
        observation_mask &= decoded_times.ge(analysis_start_time).fillna(False).to_numpy()
    if analysis_end_time is not None:
        observation_mask &= decoded_times.le(analysis_end_time).fillna(False).to_numpy()

    epoch_minutes = np.floor_divide(
        decoded_times.to_numpy(dtype="datetime64[ns]").astype("int64"),
        _NANOSECONDS_PER_MINUTE,
    )
    target_rows = frame[path_column].eq(target_path_value).fillna(False).to_numpy()
    reference_rows = (
        frame[path_column].eq(reference_path_value).fillna(False).to_numpy()
    )
    target_schedule_rows = (
        target_rows
        & valid_times
        & (np.mod(epoch_minutes, repeat_interval_minutes) == target_start_phase)
    )
    reference_schedule_rows = (
        reference_rows
        & valid_times
        & (np.mod(epoch_minutes, repeat_interval_minutes) == reference_start_phase)
    )
    scheduled_rows = observation_mask & (target_schedule_rows | reference_schedule_rows)
    scheduled_positions = np.flatnonzero(scheduled_rows)
    paired_frame = frame.iloc[scheduled_positions].copy()
    if paired_frame.empty:
        return _attach_empty_pair_columns(paired_frame)

    reference_offset_minutes = _reference_offset_minutes(
        repeat_interval_minutes,
        target_start_phase,
        reference_start_phase,
    )
    scheduled_epoch_minutes = epoch_minutes[scheduled_positions]
    scheduled_target_rows = target_schedule_rows[scheduled_positions]
    pair_ids = np.where(
        scheduled_target_rows,
        scheduled_epoch_minutes,
        scheduled_epoch_minutes - reference_offset_minutes,
    ).astype("int64", copy=False)
    planned_target_times = pd.to_datetime(
        pair_ids * _NANOSECONDS_PER_MINUTE,
        unit="ns",
        utc=True,
    )
    planned_reference_times = planned_target_times + pd.Timedelta(
        minutes=reference_offset_minutes
    )

    if exclude_boundary_pairs:
        complete_boundary_pairs = np.ones(len(paired_frame), dtype=bool)
        if analysis_start_time is not None:
            complete_boundary_pairs &= (
                planned_target_times >= analysis_start_time
            ) & (planned_reference_times >= analysis_start_time)
        if analysis_end_time is not None:
            complete_boundary_pairs &= (
                planned_target_times <= analysis_end_time
            ) & (planned_reference_times <= analysis_end_time)
        retained_positions = np.flatnonzero(complete_boundary_pairs)
        paired_frame = paired_frame.iloc[retained_positions].copy()
        pair_ids = pair_ids[retained_positions]
        planned_target_times = planned_target_times[retained_positions]
        planned_reference_times = planned_reference_times[retained_positions]

    paired_frame["tx_ab_pair_id"] = pair_ids
    paired_frame["tx_ab_pair_target_time"] = planned_target_times
    paired_frame["tx_ab_pair_reference_time"] = planned_reference_times
    return paired_frame
