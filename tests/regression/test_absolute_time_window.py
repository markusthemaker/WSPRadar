"""Regression contracts for the canonical absolute UTC analysis window."""

from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import pytest

from core.time_utils import (
    UtcWindowValidationError,
    format_utc_minute,
    normalize_utc_window,
    parse_utc_minute,
    resolve_default_utc_window,
)
from ui.time_window import (
    end_date_entry_bounds,
    initialize_utc_window_state,
    quantize_utc_window_state,
    set_default_utc_window_state,
    set_suggested_end_date_from_start_date,
    utc_window_from_state,
)


def test_default_window_is_one_absolute_quantized_24_hour_interval():
    """Resolve the default once from the current UTC timestamp."""
    current_utc = datetime(
        2026,
        7,
        27,
        12,
        29,
        58,
        tzinfo=timezone.utc,
    )

    start_utc, end_utc = resolve_default_utc_window(current_utc=current_utc)

    assert start_utc == datetime(2026, 7, 26, 12, 15, tzinfo=timezone.utc)
    assert end_utc == datetime(2026, 7, 27, 12, 15, tzinfo=timezone.utc)
    assert end_utc - start_utc == timedelta(hours=24)


def test_session_initialization_keeps_the_original_absolute_window_on_rerun():
    """Do not advance a session window when a later rerun observes a new time."""
    session_state = {}
    first_current_utc = datetime(2026, 7, 27, 12, 29, tzinfo=timezone.utc)
    later_current_utc = datetime(2026, 7, 27, 15, 2, tzinfo=timezone.utc)

    first_window = initialize_utc_window_state(
        session_state,
        current_utc=first_current_utc,
    )
    rerun_window = initialize_utc_window_state(
        session_state,
        current_utc=later_current_utc,
    )

    assert rerun_window == first_window
    assert session_state["val_start_d"] == date(2026, 7, 26)
    assert session_state["val_start_t"] == time(12, 15)
    assert session_state["val_end_d"] == date(2026, 7, 27)
    assert session_state["val_end_t"] == time(12, 15)


def test_reset_resolves_a_fresh_absolute_default_window():
    """Reset the canonical fields from the UTC clock instead of retaining them."""
    session_state = {}
    set_default_utc_window_state(
        session_state,
        current_utc=datetime(2026, 7, 27, 12, 29, tzinfo=timezone.utc),
    )

    start_utc, end_utc = set_default_utc_window_state(
        session_state,
        current_utc=datetime(2026, 7, 27, 15, 2, tzinfo=timezone.utc),
    )

    assert start_utc == datetime(2026, 7, 26, 15, 0, tzinfo=timezone.utc)
    assert end_utc == datetime(2026, 7, 27, 15, 0, tzinfo=timezone.utc)
    assert session_state["val_end_t"] == time(15, 0)


def test_ui_quantization_updates_the_canonical_state_fields():
    """Write effective query boundaries back before any serializer reads state."""
    session_state = {
        "val_start_d": date(2026, 7, 26),
        "val_start_t": time(12, 29, 59),
        "val_end_d": date(2026, 7, 27),
        "val_end_t": time(12, 44, 59),
    }

    start_utc, end_utc = quantize_utc_window_state(session_state)

    assert start_utc == datetime(2026, 7, 26, 12, 15, tzinfo=timezone.utc)
    assert end_utc == datetime(2026, 7, 27, 12, 30, tzinfo=timezone.utc)
    assert session_state["val_start_t"] == time(12, 15)
    assert session_state["val_end_t"] == time(12, 30)


def test_edited_start_date_suggests_an_end_date_seven_days_later():
    """Keep the existing times while making a historical date edit useful."""
    session_state = {
        "val_start_d": date(2026, 7, 1),
        "val_end_d": date(2026, 7, 27),
    }

    suggested_end_date = set_suggested_end_date_from_start_date(
        session_state,
        current_utc=datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc),
    )

    assert suggested_end_date == date(2026, 7, 8)
    assert session_state["val_end_d"] == date(2026, 7, 8)


def test_edited_start_date_suggestion_stops_at_today_utc():
    """Do not suggest a future End Date for a recent Start Date."""
    session_state = {
        "val_start_d": date(2026, 7, 25),
        "val_end_d": date(2026, 7, 26),
    }

    set_suggested_end_date_from_start_date(
        session_state,
        current_utc=datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc),
    )

    assert session_state["val_end_d"] == date(2026, 7, 27)


def test_end_date_entry_bounds_follow_start_date_and_the_31_day_limit():
    """Constrain the date picker without weakening exact time validation."""
    assert end_date_entry_bounds(
        {
            "val_start_d": date(2026, 6, 1),
            "val_end_d": date(2026, 7, 1),
        },
        current_utc=datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc),
    ) == (date(2026, 6, 1), date(2026, 7, 2))


@pytest.mark.parametrize(
    ("retained_end_date", "expected_bounds"),
    [
        (
            date(2026, 7, 3),
            (date(2026, 6, 1), date(2026, 7, 3)),
        ),
        (
            date(2026, 5, 31),
            (date(2026, 5, 31), date(2026, 7, 2)),
        ),
    ],
)
def test_end_date_entry_bounds_retain_invalid_dates_for_correction(
    retained_end_date,
    expected_bounds,
):
    """Render legacy invalid state without mutating or silently repairing it."""
    session_state = {
        "val_start_d": date(2026, 6, 1),
        "val_end_d": retained_end_date,
    }

    assert end_date_entry_bounds(
        session_state,
        current_utc=datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc),
    ) == expected_bounds
    assert session_state["val_end_d"] == retained_end_date


def test_exact_31_day_window_is_valid_but_31_days_15_minutes_is_not():
    """Keep elapsed time, rather than calendar dates alone, authoritative."""
    start_utc = datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc)
    exact_end_utc = datetime(2026, 7, 2, 0, 0, tzinfo=timezone.utc)
    current_utc = datetime(2026, 8, 2, 0, 0, tzinfo=timezone.utc)

    assert normalize_utc_window(
        start_utc,
        exact_end_utc,
        max_duration=timedelta(days=31),
        current_utc=current_utc,
    ) == (start_utc, exact_end_utc)
    with pytest.raises(UtcWindowValidationError) as validation_error:
        normalize_utc_window(
            start_utc,
            exact_end_utc + timedelta(minutes=15),
            max_duration=timedelta(days=31),
            current_utc=current_utc,
        )

    assert validation_error.value.reason == "duration"


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-07-27T12:15:00Z",
        "2026-07-27T12:15+00:00",
        "2026-07-27 12:15Z",
        "2026-02-30T12:15Z",
        202607271215,
    ],
)
def test_utc_minute_parser_rejects_noncanonical_or_invalid_values(timestamp):
    """Accept only the task-defined Z-suffixed minute representation."""
    with pytest.raises(UtcWindowValidationError):
        parse_utc_minute(timestamp)


def test_utc_minute_parser_and_formatter_round_trip_exactly():
    """Keep config and URL boundary text byte-for-byte canonical."""
    timestamp = parse_utc_minute("2026-07-27T12:15Z")

    assert timestamp == datetime(2026, 7, 27, 12, 15, tzinfo=timezone.utc)
    assert format_utc_minute(timestamp) == "2026-07-27T12:15Z"


@pytest.mark.parametrize(
    ("start_utc", "end_utc", "reason"),
    [
        (
            datetime(2026, 7, 27, 12, 15, tzinfo=timezone.utc),
            datetime(2026, 7, 27, 12, 15, tzinfo=timezone.utc),
            "order",
        ),
        (
            datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 7, 3, 0, 0, tzinfo=timezone.utc),
            "duration",
        ),
        (
            datetime(2026, 7, 27, 12, 15, tzinfo=timezone.utc),
            datetime(2026, 7, 27, 12, 45, tzinfo=timezone.utc),
            "future",
        ),
    ],
)
def test_window_validation_reports_order_duration_and_future_reasons(
    start_utc,
    end_utc,
    reason,
):
    """Expose stable reasons so Classic can render localized field guidance."""
    with pytest.raises(UtcWindowValidationError) as validation_error:
        normalize_utc_window(
            start_utc,
            end_utc,
            max_duration=timedelta(days=31),
            current_utc=datetime(
                2026,
                7,
                27,
                12,
                30,
                tzinfo=timezone.utc,
            ),
        )

    assert validation_error.value.reason == reason


def test_state_validation_returns_the_effective_half_open_query_endpoints():
    """Use the canonical state adapter for both serialization and execution."""
    session_state = {
        "val_start_d": date(2026, 7, 26),
        "val_start_t": time(12, 29),
        "val_end_d": date(2026, 7, 27),
        "val_end_t": time(12, 44),
    }

    assert utc_window_from_state(
        session_state,
        current_utc=datetime(2026, 7, 27, 12, 45, tzinfo=timezone.utc),
    ) == (
        datetime(2026, 7, 26, 12, 15, tzinfo=timezone.utc),
        datetime(2026, 7, 27, 12, 30, tzinfo=timezone.utc),
    )


def test_app_blocks_submission_while_entry_time_window_is_invalid():
    """Keep the immediate field error from becoming an avoidable Run click."""
    app_source = (
        Path(__file__).resolve().parents[2] / "app.py"
    ).read_text(encoding="utf-8")

    assert "or time_window_validation_error is not None" in app_source
    assert "time_window_validation_message_key(" in app_source
