"""Lightweight lifecycle helpers for analysis-result session state.

This module deliberately avoids importing export, inspector, DataFrame, or
plotting code so configuration callbacks can retire stale results without
loading the scientific runtime on the idle landing page.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, MutableMapping

from core.artifact_store import retire_registered_session_artifacts


EXPORT_STATE_KEY = "result_export_blocks"
EXPORT_RUN_ID_KEY = "result_export_run_id"
EXPORT_ZIP_BYTES_KEY = "result_export_zip_bytes"
EXPORT_ZIP_FILENAME_KEY = "result_export_zip_filename"
EXPORT_ZIP_SIGNATURE_KEY = "result_export_zip_signature"
INSPECTOR_CACHE_STATE_KEY = "segment_inspector_cache"
ACTIVE_RUN_DATABASE_SOURCE_KEY = "active_run_database_source"
COMPLETED_RUN_SNAPSHOT_KEY = "completed_run_snapshot"
COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION = 1

PREPARED_RESULT_STATE_KEYS = (
    EXPORT_ZIP_BYTES_KEY,
    EXPORT_ZIP_FILENAME_KEY,
    EXPORT_ZIP_SIGNATURE_KEY,
)


def clear_prepared_result_state(session_state: MutableMapping[str, Any]) -> None:
    """Remove prepared ZIP bytes and metadata from one Streamlit session."""
    for state_key in PREPARED_RESULT_STATE_KEYS:
        session_state.pop(state_key, None)


def clear_rendered_result_state(
    session_state: MutableMapping[str, Any],
    *,
    preserve_inspector_cache: bool = False,
) -> None:
    """Invalidate export and inspector state before publishing refreshed artifacts.

    This deliberately preserves the active run's database source. It is used
    when a same-run rerender replaces its staged data without changing the
    run's scientific identity or provenance. A validated completed-result
    rerender may retain its versioned Inspector cache because neither its
    scientific request nor its registered artifacts changed.
    """
    session_state[EXPORT_STATE_KEY] = {}
    session_state[EXPORT_RUN_ID_KEY] = session_state.get("run_id", 0)
    if not preserve_inspector_cache:
        session_state.pop(INSPECTOR_CACHE_STATE_KEY, None)
    clear_prepared_result_state(session_state)


def clear_active_run_database_source(session_state: MutableMapping[str, Any]) -> None:
    """Remove database provenance associated with the active analysis run."""
    session_state.pop(ACTIVE_RUN_DATABASE_SOURCE_KEY, None)


def get_completed_run_snapshot(
    session_state: MutableMapping[str, Any],
) -> dict[str, Any] | None:
    """Return an independent current-version completed-run snapshot, if present."""
    snapshot = session_state.get(COMPLETED_RUN_SNAPSHOT_KEY)
    if not isinstance(snapshot, dict):
        return None
    if snapshot.get("schema_version") != COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION:
        return None
    return deepcopy(snapshot)


def publish_completed_run_snapshot(
    session_state: MutableMapping[str, Any],
    snapshot: dict[str, Any],
) -> None:
    """Publish one versioned snapshot as the final completed-result commit marker."""
    if not isinstance(snapshot, dict):
        raise TypeError("Completed-run snapshot must be a dictionary")
    if snapshot.get("schema_version") != COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION:
        raise ValueError(
            "Completed-run snapshot schema version must be "
            f"{COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION}"
        )
    session_state[COMPLETED_RUN_SNAPSHOT_KEY] = deepcopy(snapshot)


def clear_completed_run_snapshot(
    session_state: MutableMapping[str, Any],
) -> None:
    """Remove the completed-result commit marker without importing runtime data."""
    session_state.pop(COMPLETED_RUN_SNAPSHOT_KEY, None)


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


def reset_result_state(session_state: MutableMapping[str, Any]) -> None:
    """Retire active artifacts and clear all cached state for the current run.

    Registered artifacts are retired through the shared artifact lifecycle;
    active leases remain readable until their normal cleanup becomes safe.
    """
    retire_registered_session_artifacts(session_state)
    clear_rendered_result_state(session_state)
    clear_active_run_database_source(session_state)
    clear_completed_run_snapshot(session_state)
