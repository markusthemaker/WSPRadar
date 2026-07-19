"""Lightweight session state for one in-flight analysis submission.

This module intentionally has no Streamlit or scientific-runtime imports so the
idle application shell and configuration callbacks can use it safely.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, MutableMapping


ANALYSIS_SUBMISSION_TOKEN_KEY = "_analysis_submission_token"
ANALYSIS_SUBMISSION_REQUESTED_TOKEN_KEY = "_analysis_submission_requested_token"
ANALYSIS_SUBMISSION_REQUEST_SOURCE_KEY = "_analysis_submission_request_source"
ANALYSIS_SUBMISSION_PHASE_KEY = "_analysis_submission_phase"
ANALYSIS_SUBMISSION_POSITION_KEY = "_analysis_submission_position"

SUBMISSION_PHASE_SUBMITTED = "submitted"
SUBMISSION_PHASE_QUEUED = "queued"
SUBMISSION_PHASE_RUNNING = "running"


@dataclass(frozen=True)
class AnalysisSubmissionSnapshot:
    """Describe the current session-owned submission without scientific data."""

    token: str
    phase: str
    position: int


@dataclass(frozen=True)
class AnalysisSubmissionRequest:
    """Describe one claimed request to execute an analysis script run."""

    token: str
    source: str


def begin_analysis_submission(
    session_state: MutableMapping[str, Any],
    *,
    request_execution: bool = True,
    request_source: str = "analysis",
) -> str:
    """Create one UUID submission token, or return the existing in-flight token.

    When ``request_execution`` is true, the token also records a one-shot request
    for the next top-to-bottom Streamlit run to enter the analysis controller.
    """
    existing_token = session_state.get(ANALYSIS_SUBMISSION_TOKEN_KEY)
    if isinstance(existing_token, str) and existing_token:
        return existing_token

    token = uuid.uuid4().hex
    session_state[ANALYSIS_SUBMISSION_TOKEN_KEY] = token
    session_state[ANALYSIS_SUBMISSION_PHASE_KEY] = SUBMISSION_PHASE_SUBMITTED
    session_state[ANALYSIS_SUBMISSION_POSITION_KEY] = 0
    if request_execution:
        session_state[ANALYSIS_SUBMISSION_REQUESTED_TOKEN_KEY] = token
        session_state[ANALYSIS_SUBMISSION_REQUEST_SOURCE_KEY] = str(request_source)
    return token


def begin_main_analysis_submission(
    session_state: MutableMapping[str, Any],
) -> str:
    """Schedule the main Run action without changing its scientific/demo identity."""
    return begin_analysis_submission(
        session_state,
        request_source="main_button",
    )


def claim_analysis_submission_request(
    session_state: MutableMapping[str, Any],
) -> AnalysisSubmissionRequest | None:
    """Consume and return a valid one-shot execution request for this session."""
    requested_token = session_state.pop(
        ANALYSIS_SUBMISSION_REQUESTED_TOKEN_KEY,
        None,
    )
    request_source = session_state.pop(
        ANALYSIS_SUBMISSION_REQUEST_SOURCE_KEY,
        "analysis",
    )
    if (
        isinstance(requested_token, str)
        and requested_token
        and requested_token == session_state.get(ANALYSIS_SUBMISSION_TOKEN_KEY)
    ):
        return AnalysisSubmissionRequest(
            token=requested_token,
            source=str(request_source),
        )
    return None


def get_analysis_submission(
    session_state: MutableMapping[str, Any],
) -> AnalysisSubmissionSnapshot | None:
    """Return the current submission snapshot, or ``None`` while idle."""
    token = session_state.get(ANALYSIS_SUBMISSION_TOKEN_KEY)
    if not isinstance(token, str) or not token:
        return None
    phase = session_state.get(
        ANALYSIS_SUBMISSION_PHASE_KEY,
        SUBMISSION_PHASE_SUBMITTED,
    )
    position = session_state.get(ANALYSIS_SUBMISSION_POSITION_KEY, 0)
    try:
        normalized_position = max(int(position), 0)
    except (TypeError, ValueError):
        normalized_position = 0
    return AnalysisSubmissionSnapshot(
        token=token,
        phase=str(phase),
        position=normalized_position,
    )


def update_analysis_submission(
    session_state: MutableMapping[str, Any],
    token: str | None,
    *,
    phase: str,
    position: int = 0,
) -> bool:
    """Update status only when ``token`` still owns the current submission."""
    if not token or session_state.get(ANALYSIS_SUBMISSION_TOKEN_KEY) != token:
        return False
    session_state[ANALYSIS_SUBMISSION_PHASE_KEY] = str(phase)
    session_state[ANALYSIS_SUBMISSION_POSITION_KEY] = max(int(position), 0)
    return True


def finish_analysis_submission(
    session_state: MutableMapping[str, Any],
    token: str | None,
) -> bool:
    """Clear a terminal submission without allowing an older run to clear a newer one."""
    if not token or session_state.get(ANALYSIS_SUBMISSION_TOKEN_KEY) != token:
        return False
    session_state.pop(ANALYSIS_SUBMISSION_TOKEN_KEY, None)
    if session_state.get(ANALYSIS_SUBMISSION_REQUESTED_TOKEN_KEY) == token:
        session_state.pop(ANALYSIS_SUBMISSION_REQUESTED_TOKEN_KEY, None)
        session_state.pop(ANALYSIS_SUBMISSION_REQUEST_SOURCE_KEY, None)
    session_state.pop(ANALYSIS_SUBMISSION_PHASE_KEY, None)
    session_state.pop(ANALYSIS_SUBMISSION_POSITION_KEY, None)
    return True


def cancel_analysis_submission(
    session_state: MutableMapping[str, Any],
) -> bool:
    """Retire the current UI submission when its scientific request is replaced."""
    snapshot = get_analysis_submission(session_state)
    if snapshot is None:
        return False
    return finish_analysis_submission(session_state, snapshot.token)
