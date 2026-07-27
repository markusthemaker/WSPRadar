"""Dependency-free UTC time helpers used by the idle application shell."""

import re
from datetime import datetime, timedelta, timezone


UTC_QUANTUM_MINUTES = 15
DEFAULT_UTC_WINDOW_DURATION = timedelta(hours=24)
_UTC_MINUTE_PATTERN = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"T(?P<hour>\d{2}):(?P<minute>\d{2})Z$"
)


class UtcWindowValidationError(ValueError):
    """Describe one invalid effective UTC analysis window with a stable reason."""

    def __init__(self, reason: str, message: str):
        """Store a machine-readable reason alongside the validation message."""
        super().__init__(message)
        self.reason = reason


def _aware_utc(timestamp: datetime, *, field: str) -> datetime:
    """Return one aware timestamp in UTC or raise a field-specific error."""
    if not isinstance(timestamp, datetime):
        raise UtcWindowValidationError(
            "invalid",
            f"{field} must be a datetime.",
        )
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise UtcWindowValidationError(
            "invalid",
            f"{field} must be timezone-aware.",
        )
    return timestamp.astimezone(timezone.utc)


def quantize_time(timestamp: datetime) -> datetime:
    """Floor a timestamp to a 15-minute boundary for stable query caching."""
    minute = (timestamp.minute // UTC_QUANTUM_MINUTES) * UTC_QUANTUM_MINUTES
    return timestamp.replace(minute=minute, second=0, microsecond=0)


def parse_utc_minute(value: str, *, field: str = "timestamp") -> datetime:
    """Parse the canonical ``YYYY-MM-DDTHH:MMZ`` UTC-minute representation."""
    if not isinstance(value, str) or _UTC_MINUTE_PATTERN.fullmatch(value) is None:
        raise UtcWindowValidationError(
            "invalid",
            f"{field} must use YYYY-MM-DDTHH:MMZ format.",
        )
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%MZ")
    except ValueError as error:
        raise UtcWindowValidationError(
            "invalid",
            f"{field} must contain a valid UTC date and time.",
        ) from error
    return parsed.replace(tzinfo=timezone.utc)


def format_utc_minute(timestamp: datetime) -> str:
    """Serialize one aware timestamp as canonical ``YYYY-MM-DDTHH:MMZ`` UTC."""
    return _aware_utc(timestamp, field="timestamp").strftime("%Y-%m-%dT%H:%MZ")


def normalize_utc_window(
    start_utc: datetime,
    end_utc: datetime,
    *,
    max_duration: timedelta,
    current_utc: datetime | None = None,
    minimum_start_utc: datetime | None = None,
) -> tuple[datetime, datetime]:
    """Return quantized UTC endpoints after validating the analysis interval.

    Validation applies to the effective 15-minute query boundaries. The
    interval is half-open, must have positive duration, must not exceed
    ``max_duration``, and cannot end after the current quantized UTC boundary.
    """
    if not isinstance(max_duration, timedelta) or max_duration <= timedelta(0):
        raise ValueError("max_duration must be a positive timedelta.")

    effective_start_utc = quantize_time(
        _aware_utc(start_utc, field="start_utc")
    )
    effective_end_utc = quantize_time(_aware_utc(end_utc, field="end_utc"))
    effective_current_utc = quantize_time(
        _aware_utc(
            current_utc or datetime.now(timezone.utc),
            field="current_utc",
        )
    )

    if minimum_start_utc is not None:
        effective_minimum_start_utc = quantize_time(
            _aware_utc(minimum_start_utc, field="minimum_start_utc")
        )
        if effective_start_utc < effective_minimum_start_utc:
            raise UtcWindowValidationError(
                "before_minimum",
                "start_utc is earlier than the supported analysis history.",
            )
    if effective_end_utc <= effective_start_utc:
        raise UtcWindowValidationError(
            "order",
            "end_utc must be after start_utc.",
        )
    if effective_end_utc - effective_start_utc > max_duration:
        raise UtcWindowValidationError(
            "duration",
            "The UTC analysis window exceeds the maximum duration.",
        )
    if effective_end_utc > effective_current_utc:
        raise UtcWindowValidationError(
            "future",
            "end_utc must not be after the current quantized UTC boundary.",
        )
    return effective_start_utc, effective_end_utc


def resolve_default_utc_window(
    *,
    current_utc: datetime | None = None,
    duration: timedelta = DEFAULT_UTC_WINDOW_DURATION,
) -> tuple[datetime, datetime]:
    """Resolve one stable absolute window ending at the current UTC quantum."""
    if not isinstance(duration, timedelta) or duration <= timedelta(0):
        raise ValueError("duration must be a positive timedelta.")
    effective_end_utc = quantize_time(
        _aware_utc(
            current_utc or datetime.now(timezone.utc),
            field="current_utc",
        )
    )
    return effective_end_utc - duration, effective_end_utc
