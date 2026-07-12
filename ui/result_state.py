"""Lightweight lifecycle helpers for analysis-result session state.

This module deliberately avoids importing export, inspector, DataFrame, or
plotting code so configuration callbacks can retire stale results without
loading the scientific runtime on the idle landing page.
"""

from __future__ import annotations

from typing import Any, MutableMapping

from core.artifact_store import retire_registered_session_artifacts


EXPORT_STATE_KEY = "result_export_blocks"
EXPORT_RUN_ID_KEY = "result_export_run_id"
EXPORT_ZIP_BYTES_KEY = "result_export_zip_bytes"
EXPORT_ZIP_FILENAME_KEY = "result_export_zip_filename"
EXPORT_ZIP_SIGNATURE_KEY = "result_export_zip_signature"
INSPECTOR_CACHE_STATE_KEY = "segment_inspector_cache"
STABILITY_CACHE_STATE_KEY = "segment_stability_cache"

PREPARED_RESULT_STATE_KEYS = (
    EXPORT_ZIP_BYTES_KEY,
    EXPORT_ZIP_FILENAME_KEY,
    EXPORT_ZIP_SIGNATURE_KEY,
)


def clear_prepared_result_state(session_state: MutableMapping[str, Any]) -> None:
    """Remove prepared ZIP bytes and metadata from one Streamlit session."""
    for state_key in PREPARED_RESULT_STATE_KEYS:
        session_state.pop(state_key, None)


def reset_result_state(session_state: MutableMapping[str, Any]) -> None:
    """Retire active artifacts and clear all cached state for the current run.

    Registered artifacts are retired through the shared artifact lifecycle;
    active leases remain readable until their normal cleanup becomes safe.
    """
    retire_registered_session_artifacts(session_state)
    session_state[EXPORT_STATE_KEY] = {}
    session_state[EXPORT_RUN_ID_KEY] = session_state.get("run_id", 0)
    session_state.pop(STABILITY_CACHE_STATE_KEY, None)
    session_state.pop(INSPECTOR_CACHE_STATE_KEY, None)
    clear_prepared_result_state(session_state)
