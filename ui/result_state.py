"""Lightweight lifecycle helpers for analysis-result session state.

This module deliberately avoids importing export, inspector, DataFrame, or
plotting code so configuration callbacks can retire stale results without
loading the scientific runtime on the idle landing page.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, MutableMapping

from core.artifact_store import retire_registered_session_artifacts


EXPORT_STATE_KEY = "result_export_blocks"
EXPORT_RUN_ID_KEY = "result_export_run_id"
EXPORT_ZIP_BYTES_KEY = "result_export_zip_bytes"
EXPORT_ZIP_FILENAME_KEY = "result_export_zip_filename"
EXPORT_ZIP_SIGNATURE_KEY = "result_export_zip_signature"
INSPECTOR_CACHE_STATE_KEY = "segment_inspector_cache"
ACTIVE_RUN_TIME_WINDOW_KEY = "active_run_time_window"
ACTIVE_RUN_DATABASE_SOURCE_KEY = "active_run_database_source"

PREPARED_RESULT_STATE_KEYS = (
    EXPORT_ZIP_BYTES_KEY,
    EXPORT_ZIP_FILENAME_KEY,
    EXPORT_ZIP_SIGNATURE_KEY,
)


def clear_prepared_result_state(session_state: MutableMapping[str, Any]) -> None:
    """Remove prepared ZIP bytes and metadata from one Streamlit session."""
    for state_key in PREPARED_RESULT_STATE_KEYS:
        session_state.pop(state_key, None)


def clear_rendered_result_state(session_state: MutableMapping[str, Any]) -> None:
    """Invalidate export and inspector state before publishing refreshed artifacts.

    This deliberately preserves the active run's resolved time window and
    database source. It is used when a same-run rerender replaces its staged
    data without changing the run's scientific identity or provenance.
    """
    session_state[EXPORT_STATE_KEY] = {}
    session_state[EXPORT_RUN_ID_KEY] = session_state.get("run_id", 0)
    session_state.pop(INSPECTOR_CACHE_STATE_KEY, None)
    clear_prepared_result_state(session_state)


def clear_active_run_time_window(session_state: MutableMapping[str, Any]) -> None:
    """Remove the resolved UTC query window associated with the active run."""
    session_state.pop(ACTIVE_RUN_TIME_WINDOW_KEY, None)


def clear_active_run_database_source(session_state: MutableMapping[str, Any]) -> None:
    """Remove database provenance associated with the active analysis run."""
    session_state.pop(ACTIVE_RUN_DATABASE_SOURCE_KEY, None)


def set_active_run_database_source(
    session_state: MutableMapping[str, Any],
    *,
    run_id: Any,
    source_key: str,
) -> None:
    """Commit one stable database source only after full bundle preparation."""
    normalized_source_key = str(source_key).strip()
    if not normalized_source_key:
        raise ValueError("The active run database source cannot be empty.")
    session_state[ACTIVE_RUN_DATABASE_SOURCE_KEY] = {
        "run_id": run_id,
        "source_key": normalized_source_key,
    }


def get_active_run_database_source(
    session_state: MutableMapping[str, Any],
) -> str | None:
    """Return database provenance only when it belongs to the active run."""
    stored_source = session_state.get(ACTIVE_RUN_DATABASE_SOURCE_KEY)
    if not isinstance(stored_source, dict):
        return None
    if stored_source.get("run_id") != session_state.get("run_id"):
        return None
    source_key = stored_source.get("source_key")
    if not isinstance(source_key, str) or not source_key.strip():
        return None
    return source_key.strip()


def set_active_run_time_window(
    session_state: MutableMapping[str, Any],
    *,
    run_id: Any,
    start_utc: datetime,
    end_utc: datetime,
) -> None:
    """Store one run's resolved, timezone-aware UTC analysis interval.

    The interval is keyed by ``run_id`` so later full-page rerenders cannot
    silently move a Last-X analysis window forward in time.
    """
    if start_utc.tzinfo is None or end_utc.tzinfo is None:
        raise ValueError("The active run time window must be timezone-aware.")
    normalized_start_utc = start_utc.astimezone(timezone.utc)
    normalized_end_utc = end_utc.astimezone(timezone.utc)
    if normalized_end_utc <= normalized_start_utc:
        raise ValueError("The active run end must be after its start.")
    session_state[ACTIVE_RUN_TIME_WINDOW_KEY] = {
        "run_id": run_id,
        "start_utc": normalized_start_utc,
        "end_utc": normalized_end_utc,
    }


def get_active_run_time_window(
    session_state: MutableMapping[str, Any],
) -> tuple[datetime, datetime] | None:
    """Return the stored UTC interval only when it belongs to the active run."""
    stored_window = session_state.get(ACTIVE_RUN_TIME_WINDOW_KEY)
    if not isinstance(stored_window, dict):
        return None
    if stored_window.get("run_id") != session_state.get("run_id"):
        return None
    start_utc = stored_window.get("start_utc")
    end_utc = stored_window.get("end_utc")
    if not isinstance(start_utc, datetime) or not isinstance(end_utc, datetime):
        return None
    if start_utc.tzinfo is None or end_utc.tzinfo is None or end_utc <= start_utc:
        return None
    return (
        start_utc.astimezone(timezone.utc),
        end_utc.astimezone(timezone.utc),
    )


def reset_result_state(session_state: MutableMapping[str, Any]) -> None:
    """Retire active artifacts and clear all cached state for the current run.

    Registered artifacts are retired through the shared artifact lifecycle;
    active leases remain readable until their normal cleanup becomes safe.
    """
    retire_registered_session_artifacts(session_state)
    clear_rendered_result_state(session_state)
    clear_active_run_time_window(session_state)
    clear_active_run_database_source(session_state)
