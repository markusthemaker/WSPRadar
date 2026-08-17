"""Pure UTC-window helpers for focused Drill-Down evidence and rows."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import timedelta
import math
from typing import Any

import pandas as pd

from core.input_validation import is_valid_callsign, is_valid_locator
from core.opportunity_engine import opportunity_utc_from_time_slot
from core.tx_ab_schedule import assign_tx_ab_pair_columns


DRILLDOWN_ZOOM_WINDOW_OPTIONS = ("off", "1h", "3h", "6h", "12h", "24h")
DRILLDOWN_ZOOM_DURATION_HOURS = {
    "1h": 1,
    "3h": 3,
    "6h": 6,
    "12h": 12,
    "24h": 24,
}
DRILLDOWN_OUTLIER_FOCUS_OPTION = "outlier_focus"
DRILLDOWN_FOCUS_SCHEMA_VERSION = 3
DRILLDOWN_OUTLIER_CONTEXT_SCHEMA_VERSION = 1


def _as_utc_timestamp(value: Any, *, field_name: str) -> pd.Timestamp:
    """Return one timezone-aware UTC timestamp or raise a field-specific error."""
    timestamp = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(timestamp):
        raise ValueError(f"{field_name} must be a valid UTC timestamp.")
    return pd.Timestamp(timestamp)


def _as_finite_float(
    value: Any,
    *,
    field_name: str,
    strictly_positive: bool = False,
) -> float:
    """Return one finite float, optionally requiring a positive value."""
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a finite number.")
    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a finite number.") from exc
    if not math.isfinite(numeric_value):
        raise ValueError(f"{field_name} must be a finite number.")
    if strictly_positive and numeric_value <= 0.0:
        raise ValueError(f"{field_name} must be positive.")
    return numeric_value


def _timestamp_from_mapping(
    record: Mapping[str, Any],
    field_name: str,
) -> pd.Timestamp:
    """Read an exact UTC nanosecond timestamp from a queued-state mapping."""
    try:
        raw_nanoseconds = record[field_name]
        if isinstance(raw_nanoseconds, bool):
            raise TypeError
        return pd.Timestamp(int(raw_nanoseconds), unit="ns", tz="UTC")
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            f"{field_name} must be a valid UTC nanosecond timestamp."
        ) from exc


@dataclass(frozen=True)
class DrilldownFocusWindow:
    """One validated half-open Drill-Down focus interval."""

    start_utc: pd.Timestamp
    end_utc: pd.Timestamp
    option: str
    origin: str

    def __post_init__(self) -> None:
        start_utc = _as_utc_timestamp(
            self.start_utc,
            field_name="Drill-Down focus start",
        )
        end_utc = _as_utc_timestamp(
            self.end_utc,
            field_name="Drill-Down focus end",
        )
        if end_utc <= start_utc:
            raise ValueError("Drill-Down focus end must be after its start.")
        option = str(self.option).strip()
        origin = str(self.origin).strip()
        if not option:
            raise ValueError("Drill-Down focus option must not be empty.")
        if not origin:
            raise ValueError("Drill-Down focus origin must not be empty.")
        object.__setattr__(self, "start_utc", start_utc)
        object.__setattr__(self, "end_utc", end_utc)
        object.__setattr__(self, "option", option)
        object.__setattr__(self, "origin", origin)

    @property
    def duration(self) -> pd.Timedelta:
        return self.end_utc - self.start_utc

    def as_export_metadata(self) -> dict[str, Any]:
        """Return stable, JSON-safe export/signature metadata."""
        return {
            "schema_version": DRILLDOWN_FOCUS_SCHEMA_VERSION,
            "start_utc": self.start_utc.isoformat(),
            "end_utc": self.end_utc.isoformat(),
            "option": self.option,
            "origin": self.origin,
        }


@dataclass(frozen=True)
class DrilldownOutlierCandidateContext:
    """Validated candidate provenance and local detector context for Drill-Down.

    This record is deliberately independent from :class:`DrilldownFocusWindow`.
    An operator can therefore move or resize the focused view without silently
    changing which detector candidate supplies the marker and local-baseline
    annotations.
    """

    analysis_id: str
    run_id: Any
    scope_token: str
    callsign: str
    locator: str
    request_token: str
    representative_utc: pd.Timestamp
    representative_delta_snr_db: float
    event_start_utc: pd.Timestamp
    event_end_utc: pd.Timestamp
    baseline_anchor_start_utc: pd.Timestamp
    baseline_anchor_end_utc: pd.Timestamp
    episode_guard_minutes: float
    pre_flank_start_utc: pd.Timestamp
    pre_flank_end_utc: pd.Timestamp
    post_flank_start_utc: pd.Timestamp
    post_flank_end_utc: pd.Timestamp
    local_baseline_db: float
    pre_baseline_db: float
    post_baseline_db: float
    robust_spread_db: float
    robust_spread_method: str
    robust_z: float
    minimum_robust_z: float
    minimum_departure_db: float
    detector_version: str
    candidate_signature: str

    def __post_init__(self) -> None:
        analysis_id = str(self.analysis_id).strip()
        scope_token = str(self.scope_token).strip()
        request_token = str(self.request_token).strip()
        callsign = str(self.callsign).strip().upper()
        locator = str(self.locator).strip().upper()
        detector_version = str(self.detector_version).strip()
        candidate_signature = str(self.candidate_signature).strip()
        if not analysis_id:
            raise ValueError("Outlier context analysis_id must not be empty.")
        if self.run_id is None:
            raise ValueError("Outlier context run_id must not be null.")
        if not scope_token:
            raise ValueError("Outlier context scope_token must not be empty.")
        if not request_token:
            raise ValueError("Outlier context request_token must not be empty.")
        if not is_valid_callsign(callsign):
            raise ValueError("Outlier context callsign is invalid.")
        if not is_valid_locator(locator):
            raise ValueError("Outlier context locator is invalid.")
        if not detector_version:
            raise ValueError("Outlier context detector_version must not be empty.")
        if not candidate_signature:
            raise ValueError("Outlier context candidate_signature must not be empty.")

        timestamp_fields = (
            "representative_utc",
            "event_start_utc",
            "event_end_utc",
            "baseline_anchor_start_utc",
            "baseline_anchor_end_utc",
            "pre_flank_start_utc",
            "pre_flank_end_utc",
            "post_flank_start_utc",
            "post_flank_end_utc",
        )
        timestamps = {
            field_name: _as_utc_timestamp(
                getattr(self, field_name),
                field_name=f"Outlier context {field_name}",
            )
            for field_name in timestamp_fields
        }
        event_start = timestamps["event_start_utc"]
        event_end = timestamps["event_end_utc"]
        representative = timestamps["representative_utc"]
        baseline_anchor_start = timestamps["baseline_anchor_start_utc"]
        baseline_anchor_end = timestamps["baseline_anchor_end_utc"]
        if event_end <= event_start:
            raise ValueError("Outlier event end must be after its start.")
        if not event_start <= representative < event_end:
            raise ValueError(
                "Outlier representative UTC must lie inside its half-open event."
            )
        if baseline_anchor_end < baseline_anchor_start:
            raise ValueError(
                "Outlier baseline-anchor end must not precede its start."
            )
        event_last_instant = event_end - pd.Timedelta(nanoseconds=1)
        if (
            event_start < baseline_anchor_start
            or event_last_instant > baseline_anchor_end
        ):
            raise ValueError(
                "Outlier event must lie inside its inclusive baseline anchors."
            )
        if not (
            timestamps["pre_flank_start_utc"]
            <= timestamps["pre_flank_end_utc"]
            <= baseline_anchor_start
        ):
            raise ValueError(
                "Outlier pre-flank bounds must precede the baseline anchor."
            )
        if not (
            baseline_anchor_end
            <= timestamps["post_flank_start_utc"]
            <= timestamps["post_flank_end_utc"]
        ):
            raise ValueError(
                "Outlier post-flank bounds must follow the baseline anchor."
            )

        numeric_fields = (
            "representative_delta_snr_db",
            "local_baseline_db",
            "pre_baseline_db",
            "post_baseline_db",
            "robust_z",
        )
        numeric_values = {
            field_name: _as_finite_float(
                getattr(self, field_name),
                field_name=f"Outlier context {field_name}",
            )
            for field_name in numeric_fields
        }
        positive_numeric_fields = (
            "episode_guard_minutes",
            "robust_spread_db",
            "minimum_robust_z",
            "minimum_departure_db",
        )
        numeric_values.update(
            {
                field_name: _as_finite_float(
                    getattr(self, field_name),
                    field_name=f"Outlier context {field_name}",
                    strictly_positive=True,
                )
                for field_name in positive_numeric_fields
            }
        )
        robust_spread_method = str(self.robust_spread_method).strip()
        if not robust_spread_method:
            raise ValueError(
                "Outlier context robust_spread_method must not be empty."
            )

        object.__setattr__(self, "analysis_id", analysis_id)
        object.__setattr__(self, "scope_token", scope_token)
        object.__setattr__(self, "request_token", request_token)
        object.__setattr__(self, "callsign", callsign)
        object.__setattr__(self, "locator", locator)
        object.__setattr__(self, "detector_version", detector_version)
        object.__setattr__(self, "candidate_signature", candidate_signature)
        object.__setattr__(self, "robust_spread_method", robust_spread_method)
        for field_name, timestamp in timestamps.items():
            object.__setattr__(self, field_name, timestamp)
        for field_name, numeric_value in numeric_values.items():
            object.__setattr__(self, field_name, numeric_value)

    @property
    def station_identity(self) -> tuple[str, str]:
        """Return the canonical callsign/locator pair."""
        return self.callsign, self.locator

    @property
    def outlier_focus_start_utc(self) -> pd.Timestamp:
        """Return the exact outer start of retained detector support."""
        return self.pre_flank_start_utc

    @property
    def outlier_focus_end_utc(self) -> pd.Timestamp:
        """Return the exact half-open outer end of retained detector support."""
        return self.post_flank_end_utc

    def as_session_mapping(self) -> dict[str, Any]:
        """Return the stable, exact queued-session representation."""
        timestamp_fields = (
            "representative_utc",
            "event_start_utc",
            "event_end_utc",
            "baseline_anchor_start_utc",
            "baseline_anchor_end_utc",
            "pre_flank_start_utc",
            "pre_flank_end_utc",
            "post_flank_start_utc",
            "post_flank_end_utc",
        )
        payload: dict[str, Any] = {
            "schema_version": DRILLDOWN_OUTLIER_CONTEXT_SCHEMA_VERSION,
            "analysis_id": self.analysis_id,
            "run_id": self.run_id,
            "scope_token": self.scope_token,
            "callsign": self.callsign,
            "locator": self.locator,
            "request_token": self.request_token,
            "representative_delta_snr_db": self.representative_delta_snr_db,
            "episode_guard_minutes": self.episode_guard_minutes,
            "local_baseline_db": self.local_baseline_db,
            "pre_baseline_db": self.pre_baseline_db,
            "post_baseline_db": self.post_baseline_db,
            "robust_spread_db": self.robust_spread_db,
            "robust_spread_method": self.robust_spread_method,
            "robust_z": self.robust_z,
            "minimum_robust_z": self.minimum_robust_z,
            "minimum_departure_db": self.minimum_departure_db,
            "detector_version": self.detector_version,
            "candidate_signature": self.candidate_signature,
        }
        payload.update(
            {
                f"{field_name}_ns": int(getattr(self, field_name).value)
                for field_name in timestamp_fields
            }
        )
        return payload


def parse_drilldown_outlier_candidate_context(
    record: Mapping[str, Any],
) -> DrilldownOutlierCandidateContext:
    """Parse one untrusted queued candidate mapping without clipping provenance."""
    if not isinstance(record, Mapping):
        raise ValueError("Queued Drill-Down outlier context must be a mapping.")
    schema_version = record.get(
        "schema_version",
        DRILLDOWN_OUTLIER_CONTEXT_SCHEMA_VERSION,
    )
    if (
        isinstance(schema_version, bool)
        or schema_version != DRILLDOWN_OUTLIER_CONTEXT_SCHEMA_VERSION
    ):
        raise ValueError("Queued Drill-Down outlier context schema is unsupported.")
    if "local_baseline_db" in record and "station_baseline_db" in record:
        local_baseline_db = _as_finite_float(
            record["local_baseline_db"],
            field_name="Outlier context local_baseline_db",
        )
        station_baseline_db = _as_finite_float(
            record["station_baseline_db"],
            field_name="Outlier context station_baseline_db",
        )
        if local_baseline_db != station_baseline_db:
            raise ValueError(
                "Queued Drill-Down outlier context has conflicting local baselines."
            )
    elif "local_baseline_db" in record:
        local_baseline_db = record["local_baseline_db"]
    elif "station_baseline_db" in record:
        local_baseline_db = record["station_baseline_db"]
    else:
        raise ValueError(
            "Queued Drill-Down outlier context lacks local_baseline_db."
        )
    try:
        return DrilldownOutlierCandidateContext(
            analysis_id=record["analysis_id"],
            run_id=record["run_id"],
            scope_token=record["scope_token"],
            callsign=record["callsign"],
            locator=record["locator"],
            request_token=record["request_token"],
            representative_utc=_timestamp_from_mapping(
                record,
                "representative_utc_ns",
            ),
            representative_delta_snr_db=record[
                "representative_delta_snr_db"
            ],
            event_start_utc=_timestamp_from_mapping(
                record,
                "event_start_utc_ns",
            ),
            event_end_utc=_timestamp_from_mapping(
                record,
                "event_end_utc_ns",
            ),
            baseline_anchor_start_utc=_timestamp_from_mapping(
                record,
                "baseline_anchor_start_utc_ns",
            ),
            baseline_anchor_end_utc=_timestamp_from_mapping(
                record,
                "baseline_anchor_end_utc_ns",
            ),
            episode_guard_minutes=record["episode_guard_minutes"],
            pre_flank_start_utc=_timestamp_from_mapping(
                record,
                "pre_flank_start_utc_ns",
            ),
            pre_flank_end_utc=_timestamp_from_mapping(
                record,
                "pre_flank_end_utc_ns",
            ),
            post_flank_start_utc=_timestamp_from_mapping(
                record,
                "post_flank_start_utc_ns",
            ),
            post_flank_end_utc=_timestamp_from_mapping(
                record,
                "post_flank_end_utc_ns",
            ),
            local_baseline_db=local_baseline_db,
            pre_baseline_db=record["pre_baseline_db"],
            post_baseline_db=record["post_baseline_db"],
            robust_spread_db=record["robust_spread_db"],
            robust_spread_method=record["robust_spread_method"],
            robust_z=record["robust_z"],
            minimum_robust_z=record["minimum_robust_z"],
            minimum_departure_db=record["minimum_departure_db"],
            detector_version=record["detector_version"],
            candidate_signature=record["candidate_signature"],
        )
    except KeyError as exc:
        raise ValueError(
            f"Queued Drill-Down outlier context lacks {exc.args[0]}."
        ) from exc


def drilldown_outlier_candidate_context_for_scope(
    record: object,
    *,
    analysis_id: Any,
    run_id: Any,
    scope_token: Any,
    selected_identity: tuple[Any, Any] | None,
    analysis_start_utc: Any,
    analysis_end_utc: Any,
) -> DrilldownOutlierCandidateContext | None:
    """Return a valid candidate only for its originating run, scope and path."""
    if not isinstance(record, Mapping) or selected_identity is None:
        return None
    try:
        context = parse_drilldown_outlier_candidate_context(record)
        selected_callsign = str(selected_identity[0]).strip().upper()
        selected_locator = str(selected_identity[1]).strip().upper()
        analysis_start = _as_utc_timestamp(
            analysis_start_utc,
            field_name="Analysis start",
        )
        analysis_end = _as_utc_timestamp(
            analysis_end_utc,
            field_name="Analysis end",
        )
    except (IndexError, TypeError, ValueError, OverflowError):
        return None
    if analysis_end <= analysis_start:
        raise ValueError("Analysis end must be after its start.")
    if (
        context.analysis_id != str(analysis_id).strip()
        or context.run_id != run_id
        or context.scope_token != str(scope_token).strip()
        or context.station_identity != (selected_callsign, selected_locator)
        or not (
            analysis_start <= context.representative_utc < analysis_end
        )
    ):
        return None
    return context


def available_manual_zoom_options(
    analysis_start_utc: Any,
    analysis_end_utc: Any,
) -> tuple[str, ...]:
    """Return Off plus only full-duration presets that fit the completed run."""
    analysis_start = _as_utc_timestamp(
        analysis_start_utc,
        field_name="Analysis start",
    )
    analysis_end = _as_utc_timestamp(
        analysis_end_utc,
        field_name="Analysis end",
    )
    if analysis_end <= analysis_start:
        raise ValueError("Analysis end must be after its start.")
    run_duration = analysis_end - analysis_start
    return (
        "off",
        *(
            option
            for option, duration_hours in DRILLDOWN_ZOOM_DURATION_HOURS.items()
            if run_duration >= pd.Timedelta(hours=duration_hours)
        ),
    )


def manual_zoom_center_bounds(
    analysis_start_utc: Any,
    analysis_end_utc: Any,
    option: str,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return the earliest and latest centers that preserve a full preset."""
    normalized_option = str(option)
    if normalized_option not in DRILLDOWN_ZOOM_DURATION_HOURS:
        raise ValueError(f"Unknown Drill-Down zoom option: {normalized_option!r}")
    if normalized_option not in available_manual_zoom_options(
        analysis_start_utc,
        analysis_end_utc,
    ):
        raise ValueError(
            f"Drill-Down zoom option {normalized_option!r} does not fit the run."
        )
    analysis_start = _as_utc_timestamp(
        analysis_start_utc,
        field_name="Analysis start",
    )
    analysis_end = _as_utc_timestamp(
        analysis_end_utc,
        field_name="Analysis end",
    )
    half_duration = pd.Timedelta(
        hours=DRILLDOWN_ZOOM_DURATION_HOURS[normalized_option]
    ) / 2
    return analysis_start + half_duration, analysis_end - half_duration


def default_focus_center_utc(
    analysis_start_utc: Any,
    analysis_end_utc: Any,
    option: str,
) -> pd.Timestamp:
    """Return the exact run midpoint after validating that a preset fits."""
    earliest_center, latest_center = manual_zoom_center_bounds(
        analysis_start_utc,
        analysis_end_utc,
        option,
    )
    return earliest_center + (latest_center - earliest_center) / 2


def focus_center_utc(focus_window: DrilldownFocusWindow) -> pd.Timestamp:
    """Return the exact center represented by one resolved focus interval."""
    if not isinstance(focus_window, DrilldownFocusWindow):
        raise TypeError("focus_window must be a DrilldownFocusWindow.")
    return focus_window.start_utc + focus_window.duration / 2


def resolve_centered_zoom_window(
    analysis_start_utc: Any,
    analysis_end_utc: Any,
    option: str,
    requested_focus_center_utc: Any,
    *,
    origin: str = "manual",
) -> DrilldownFocusWindow | None:
    """Resolve a full preset around a center, moving it intact at run edges."""
    normalized_option = str(option)
    if normalized_option == "off":
        return None
    earliest_center, latest_center = manual_zoom_center_bounds(
        analysis_start_utc,
        analysis_end_utc,
        normalized_option,
    )
    requested_center = _as_utc_timestamp(
        requested_focus_center_utc,
        field_name="Requested focus center",
    )
    duration = pd.Timedelta(
        hours=DRILLDOWN_ZOOM_DURATION_HOURS[normalized_option]
    )
    resolved_center = min(
        max(requested_center, earliest_center),
        latest_center,
    )
    resolved_start = resolved_center - duration / 2
    return DrilldownFocusWindow(
        start_utc=resolved_start,
        end_utc=resolved_start + duration,
        option=normalized_option,
        origin=origin,
    )


def resolve_manual_zoom_window(
    analysis_start_utc: Any,
    analysis_end_utc: Any,
    option: str,
    requested_start_utc: Any,
) -> DrilldownFocusWindow | None:
    """Compatibility wrapper for the unpublished start-based focus API."""
    normalized_option = str(option)
    if normalized_option == "off":
        return None
    if normalized_option not in DRILLDOWN_ZOOM_DURATION_HOURS:
        raise ValueError(f"Unknown Drill-Down zoom option: {normalized_option!r}")
    requested_start = _as_utc_timestamp(
        requested_start_utc,
        field_name="Requested zoom start",
    )
    duration = pd.Timedelta(
        hours=DRILLDOWN_ZOOM_DURATION_HOURS[normalized_option]
    )
    return resolve_centered_zoom_window(
        analysis_start_utc,
        analysis_end_utc,
        normalized_option,
        requested_start + duration / 2,
    )


def resolve_outlier_focus_window(
    analysis_start_utc: Any,
    analysis_end_utc: Any,
    candidate_context: DrilldownOutlierCandidateContext,
) -> DrilldownFocusWindow:
    """Clip one candidate's exact detector-support window to its analysis."""
    if not isinstance(candidate_context, DrilldownOutlierCandidateContext):
        raise TypeError(
            "candidate_context must be a DrilldownOutlierCandidateContext."
        )
    analysis_start = _as_utc_timestamp(
        analysis_start_utc,
        field_name="Analysis start",
    )
    analysis_end = _as_utc_timestamp(
        analysis_end_utc,
        field_name="Analysis end",
    )
    if analysis_end <= analysis_start:
        raise ValueError("Analysis end must be after its start.")
    if not analysis_start <= candidate_context.representative_utc < analysis_end:
        raise ValueError(
            "Outlier representative UTC lies outside the completed analysis."
        )
    context_start = candidate_context.outlier_focus_start_utc
    context_end = candidate_context.outlier_focus_end_utc
    resolved_start = max(analysis_start, context_start)
    resolved_end = min(analysis_end, context_end)
    if resolved_end <= resolved_start:
        raise ValueError(
            "Outlier context does not overlap the completed analysis window."
        )
    return DrilldownFocusWindow(
        start_utc=resolved_start,
        end_utc=resolved_end,
        option=DRILLDOWN_OUTLIER_FOCUS_OPTION,
        origin=DRILLDOWN_OUTLIER_FOCUS_OPTION,
    )


def _row_focus_timestamps(
    station_rows: pd.DataFrame,
    *,
    is_sequential: bool,
    tx_ab_repeat_interval_minutes: int,
    tx_ab_target_start_minute: int,
    tx_ab_reference_start_minute: int,
) -> tuple[pd.DataFrame, pd.Series]:
    """Return canonical rows and their non-splitting focus coordinate."""
    if station_rows is None:
        return pd.DataFrame(), pd.Series(dtype="datetime64[ns, UTC]")
    rows = station_rows.copy()
    if rows.empty:
        return rows, pd.Series(index=rows.index, dtype="datetime64[ns, UTC]")
    if is_sequential:
        if "tx_ab_pair_id" not in rows.columns:
            rows = assign_tx_ab_pair_columns(
                rows,
                repeat_interval_minutes=int(tx_ab_repeat_interval_minutes),
                target_start_minute_utc=int(tx_ab_target_start_minute),
                reference_start_minute_utc=int(tx_ab_reference_start_minute),
            )
        pair_ids = pd.to_numeric(rows.get("tx_ab_pair_id"), errors="coerce")
        timestamps = pd.to_datetime(pair_ids, unit="m", errors="coerce", utc=True)
        return rows, pd.Series(timestamps, index=rows.index)
    if "time_slot" not in rows.columns:
        raise ValueError("Cycle-based Drill-Down rows require time_slot.")
    timestamps = opportunity_utc_from_time_slot(rows["time_slot"])
    return rows, pd.Series(timestamps, index=rows.index)


def filter_station_rows_to_focus_window(
    station_rows: pd.DataFrame,
    focus_window: DrilldownFocusWindow | None,
    *,
    is_sequential: bool,
    tx_ab_repeat_interval_minutes: int = 10,
    tx_ab_target_start_minute: int = 0,
    tx_ab_reference_start_minute: int = 2,
) -> pd.DataFrame:
    """Filter canonical rows to ``[start, end)`` without splitting A/B pairs."""
    if station_rows is None:
        return pd.DataFrame()
    if focus_window is None:
        return station_rows
    rows, timestamps = _row_focus_timestamps(
        station_rows,
        is_sequential=is_sequential,
        tx_ab_repeat_interval_minutes=tx_ab_repeat_interval_minutes,
        tx_ab_target_start_minute=tx_ab_target_start_minute,
        tx_ab_reference_start_minute=tx_ab_reference_start_minute,
    )
    retained = timestamps.notna() & timestamps.ge(
        focus_window.start_utc
    ) & timestamps.lt(focus_window.end_utc)
    return rows.loc[retained].copy()


def datetime_input_step() -> timedelta:
    """Return the canonical cycle-sized step for a UTC focus-time input."""
    return timedelta(minutes=2)


def datetime_slider_step() -> timedelta:
    """Compatibility wrapper for the unpublished start-slider UI."""
    return datetime_input_step()
