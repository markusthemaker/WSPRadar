"""Dependency-free session state for on-demand documentation visibility."""

from typing import Any, MutableMapping


DOCUMENTATION_EXPANDED_KEY = "_documentation_is_expanded"
DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY = (
    "_documentation_scroll_trigger_consumed"
)


def expand_documentation(session_state: MutableMapping[str, Any]) -> None:
    """Expand the manual and consume its one-shot scroll trigger."""
    session_state[DOCUMENTATION_EXPANDED_KEY] = True
    session_state[DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY] = True


def hide_documentation(session_state: MutableMapping[str, Any]) -> None:
    """Hide the manual without allowing the scroll trigger to reopen it."""
    session_state[DOCUMENTATION_EXPANDED_KEY] = False
    session_state[DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY] = True


def collapse_documentation(session_state: MutableMapping[str, Any]) -> None:
    """Collapse the manual while preserving one-shot trigger consumption."""
    session_state[DOCUMENTATION_EXPANDED_KEY] = False
