"""Focused regression coverage for fragment-scoped config-save state."""

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
