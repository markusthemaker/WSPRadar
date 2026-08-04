"""Focused regression coverage for fragment-scoped config-save state."""

from types import SimpleNamespace

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


def test_incomplete_configuration_disables_save_control(monkeypatch):
    """Do not open Save Config while Classic Benchmark design is incomplete."""
    popover_calls = []

    fake_streamlit = SimpleNamespace(
        session_state={"lang": "en", "val_analysis_direction": "rx"},
        popover=lambda *args, **kwargs: (
            popover_calls.append((args, kwargs))
            or SimpleNamespace(open=False)
        ),
    )
    monkeypatch.setattr(config_save, "st", fake_streamlit)

    config_save.render_config_save_control.__wrapped__(
        is_configuration_ready=False,
    )

    assert len(popover_calls) == 1
    assert popover_calls[0][1]["disabled"] is True
