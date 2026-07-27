"""Pure adapters between canonical UTC windows and editable UI state."""

from datetime import date, datetime, time, timedelta, timezone
from typing import Mapping, MutableMapping

from config import MAX_DAYS_HISTORY
from core.time_utils import (
    UtcWindowValidationError,
    normalize_utc_window,
    quantize_time,
    resolve_default_utc_window,
)


ABSOLUTE_TIME_WINDOW_INITIALIZED_KEY = "_absolute_time_window_initialized"
MINIMUM_ANALYSIS_UTC = datetime(2008, 1, 1, tzinfo=timezone.utc)
TIME_WINDOW_STATE_KEYS = (
    "val_start_d",
    "val_start_t",
    "val_end_d",
    "val_end_t",
)


def _combine_utc(date_value, time_value, *, field: str) -> datetime:
    """Combine one UI date/time pair into an aware UTC timestamp."""
    if (
        not isinstance(date_value, date)
        or isinstance(date_value, datetime)
        or not isinstance(time_value, time)
    ):
        raise UtcWindowValidationError(
            "invalid",
            f"{field} must contain a date and time.",
        )
    return datetime.combine(
        date_value,
        time_value.replace(tzinfo=None),
        tzinfo=timezone.utc,
    )


def write_utc_window_to_state(
    state: MutableMapping,
    start_utc: datetime,
    end_utc: datetime,
) -> None:
    """Write aware UTC endpoints into the four canonical widget-state fields."""
    start_utc = start_utc.astimezone(timezone.utc)
    end_utc = end_utc.astimezone(timezone.utc)
    state["val_start_d"] = start_utc.date()
    state["val_start_t"] = start_utc.time().replace(tzinfo=None)
    state["val_end_d"] = end_utc.date()
    state["val_end_t"] = end_utc.time().replace(tzinfo=None)
    state[ABSOLUTE_TIME_WINDOW_INITIALIZED_KEY] = True


def set_default_utc_window_state(
    state: MutableMapping,
    *,
    current_utc: datetime | None = None,
) -> tuple[datetime, datetime]:
    """Resolve and store a fresh absolute 24-hour UTC analysis window."""
    start_utc, end_utc = resolve_default_utc_window(current_utc=current_utc)
    write_utc_window_to_state(state, start_utc, end_utc)
    return start_utc, end_utc


def quantize_utc_window_state(
    state: MutableMapping,
) -> tuple[datetime, datetime]:
    """Floor both editable UTC endpoints and write the effective values back."""
    start_utc = quantize_time(
        _combine_utc(
            state.get("val_start_d"),
            state.get("val_start_t"),
            field="start_utc",
        )
    )
    end_utc = quantize_time(
        _combine_utc(
            state.get("val_end_d"),
            state.get("val_end_t"),
            field="end_utc",
        )
    )
    write_utc_window_to_state(state, start_utc, end_utc)
    return start_utc, end_utc


def initialize_utc_window_state(
    state: MutableMapping,
    *,
    current_utc: datetime | None = None,
) -> tuple[datetime, datetime]:
    """Initialize once per session, then preserve the stored absolute window."""
    if not state.get(ABSOLUTE_TIME_WINDOW_INITIALIZED_KEY):
        return set_default_utc_window_state(state, current_utc=current_utc)
    return quantize_utc_window_state(state)


def utc_window_from_state(
    state: Mapping,
    *,
    current_utc: datetime | None = None,
) -> tuple[datetime, datetime]:
    """Return validated effective UTC query boundaries from canonical UI state."""
    start_utc = _combine_utc(
        state.get("val_start_d"),
        state.get("val_start_t"),
        field="start_utc",
    )
    end_utc = _combine_utc(
        state.get("val_end_d"),
        state.get("val_end_t"),
        field="end_utc",
    )
    return normalize_utc_window(
        start_utc,
        end_utc,
        max_duration=timedelta(days=MAX_DAYS_HISTORY),
        current_utc=current_utc,
        minimum_start_utc=MINIMUM_ANALYSIS_UTC,
    )
