import inspect

from ui import documentation_state
from ui.documentation_state import (
    DOCUMENTATION_EXPANDED_KEY,
    DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY,
    collapse_documentation,
    expand_documentation,
    hide_documentation,
)


def test_explicit_expansion_consumes_one_shot_scroll_trigger():
    """Manual or scroll-driven expansion must share one consumed state."""
    session_state = {}

    expand_documentation(session_state)

    assert session_state[DOCUMENTATION_EXPANDED_KEY] is True
    assert session_state[DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY] is True


def test_documentation_visibility_changes_are_idempotent_without_rearming():
    """Explicit load and hide actions must retain the consumed trigger."""
    session_state = {}

    expand_documentation(session_state)
    assert session_state[DOCUMENTATION_EXPANDED_KEY] is True
    assert session_state[DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY] is True

    expand_documentation(session_state)
    assert session_state[DOCUMENTATION_EXPANDED_KEY] is True
    assert session_state[DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY] is True

    hide_documentation(session_state)
    assert session_state[DOCUMENTATION_EXPANDED_KEY] is False
    assert session_state[DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY] is True

    hide_documentation(session_state)
    assert session_state[DOCUMENTATION_EXPANDED_KEY] is False
    assert session_state[DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY] is True


def test_run_collapse_preserves_consumed_state_and_does_not_consume_unarmed_state():
    """Run-start collapse must suppress visibility without rearming the session."""
    consumed_session_state = {
        DOCUMENTATION_EXPANDED_KEY: True,
        DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY: True,
    }

    collapse_documentation(consumed_session_state)

    assert consumed_session_state[DOCUMENTATION_EXPANDED_KEY] is False
    assert consumed_session_state[DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY] is True

    unconsumed_session_state = {}
    collapse_documentation(unconsumed_session_state)

    assert unconsumed_session_state[DOCUMENTATION_EXPANDED_KEY] is False
    assert DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY not in unconsumed_session_state


def test_documentation_state_stays_dependency_free():
    """The idle state helper must not acquire Streamlit or scientific imports."""
    module_source = inspect.getsource(documentation_state)

    assert "streamlit" not in module_source
    assert "pandas" not in module_source
    assert "matplotlib" not in module_source
