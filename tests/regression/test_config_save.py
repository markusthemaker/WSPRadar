"""Focused regression coverage for fragment-scoped config-save state."""

from datetime import datetime, timezone

from ui import config_save


def test_loaded_profile_prefills_current_language_without_losing_fallbacks():
    """Initialize save widgets from reusable profile metadata exactly once."""
    session_state = {
        "val_config_profile": {
            "id": "portable-rx",
            "title": {"en": "Portable RX", "de": "Portabler RX"},
            "description": {
                "en": "Hilltop receiver",
                "de": "Empf\u00e4nger am H\u00fcgel",
            },
        }
    }

    config_save._sync_profile_widget_defaults(session_state, "en")

    assert session_state[config_save._PROFILE_ID_WIDGET_KEY] == "portable-rx"
    assert session_state[config_save._PROFILE_TITLE_WIDGET_KEY] == "Portable RX"
    assert (
        session_state[config_save._PROFILE_DESCRIPTION_WIDGET_KEY]
        == "Hilltop receiver"
    )

    session_state[config_save._PROFILE_TITLE_WIDGET_KEY] = "Benutzerentwurf"
    config_save._sync_profile_widget_defaults(session_state, "en")
    assert session_state[config_save._PROFILE_TITLE_WIDGET_KEY] == "Benutzerentwurf"

    config_save._sync_profile_widget_defaults(session_state, "de")
    assert (
        session_state[config_save._PROFILE_TITLE_WIDGET_KEY]
        == "Portabler RX"
    )


def test_results_save_form_uses_distinct_widget_keys_with_shared_profile_data():
    """Allow both Save Config placements without duplicate Streamlit widget keys."""
    session_state = {
        "val_config_profile": {
            "id": "portable-rx",
            "title": {"en": "Portable RX"},
        }
    }

    config_save._sync_profile_widget_defaults(
        session_state,
        "en",
        form_scope="results",
    )

    results_title_key = config_save._scoped_form_key(
        config_save._PROFILE_TITLE_WIDGET_KEY,
        "results",
    )
    assert results_title_key != config_save._PROFILE_TITLE_WIDGET_KEY
    assert session_state[results_title_key] == "Portable RX"
    assert config_save._PROFILE_TITLE_WIDGET_KEY not in session_state


def test_new_active_run_defaults_to_freeze_but_preserves_user_choice():
    """Default each newly resolved run once without fighting later radio input."""
    resolved_window = (
        datetime(2026, 7, 16, tzinfo=timezone.utc),
        datetime(2026, 7, 17, tzinfo=timezone.utc),
    )
    session_state = {"run_id": 42}

    config_save._initialize_time_policy(session_state, resolved_window)
    assert (
        session_state[config_save._TIME_POLICY_WIDGET_KEY]
        == config_save.TIME_POLICY_FREEZE
    )

    session_state[config_save._TIME_POLICY_WIDGET_KEY] = (
        config_save.TIME_POLICY_RELATIVE
    )
    config_save._initialize_time_policy(session_state, resolved_window)
    assert (
        session_state[config_save._TIME_POLICY_WIDGET_KEY]
        == config_save.TIME_POLICY_RELATIVE
    )

    session_state["run_id"] = 43
    config_save._initialize_time_policy(session_state, resolved_window)
    assert (
        session_state[config_save._TIME_POLICY_WIDGET_KEY]
        == config_save.TIME_POLICY_FREEZE
    )


def test_clear_config_save_state_preserves_unrelated_session_values():
    """Factory reset removes stale prepared downloads and form values only."""
    session_state = {
        config_save._PREPARED_BYTES_KEY: b"config",
        config_save._PROFILE_TITLE_WIDGET_KEY: "Portable RX",
        "run_id": 42,
    }

    config_save.clear_config_save_state(session_state)

    assert session_state == {"run_id": 42}
