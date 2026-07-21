"""Focused regression coverage for loaded configuration metadata."""

from contextlib import nullcontext
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from config import DEMO_PROFILES
from i18n import T
from ui import callbacks, config_io
from ui.analysis_submission_state import (
    begin_analysis_submission,
    begin_main_analysis_submission,
    claim_analysis_submission_request,
    get_analysis_submission,
)
from ui.components import config_panel


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class _SessionState(dict):
    """Provide Streamlit-style attribute access over a test dictionary."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


class _FakeStreamlit:
    """Capture the small Streamlit surface used by the metadata expander."""

    def __init__(self, session_state):
        self.session_state = session_state
        self.expanders = []
        self.markdowns = []
        self.container_keys = []
        self.captions = []

    def expander(self, label, *, expanded):
        self.expanders.append((label, expanded))
        return nullcontext()

    def markdown(self, body, **kwargs):
        self.markdowns.append((body, kwargs))

    def container(self, *, key):
        self.container_keys.append(key)
        return nullcontext()

    def caption(self, body, **kwargs):
        self.captions.append((body, kwargs))


def _render_metadata(
    monkeypatch,
    profile,
    language="en",
    prepared_profile=None,
):
    """Render metadata with a capturing Streamlit replacement."""
    fake_streamlit = _FakeStreamlit(
        _SessionState(
            lang=language,
            loaded_config_profile=profile,
            val_config_profile=prepared_profile,
        )
    )
    monkeypatch.setattr(config_panel, "st", fake_streamlit)
    config_panel.render_metadata_expander(T[language])
    return fake_streamlit


def _demo_document(profile_id):
    """Return an independent ordinary config document for one built-in demo."""
    profile_record = DEMO_PROFILES[profile_id]
    return deepcopy(profile_record.get("configuration", profile_record))


def test_metadata_expander_is_hidden_without_loaded_profile(monkeypatch):
    """Do not show metadata for manual state or a merely prepared save profile."""
    fake_streamlit = _render_metadata(
        monkeypatch,
        None,
        prepared_profile={
            "id": "prepared-only",
            "title": {"en": "Prepared but not loaded"},
        },
    )

    assert fake_streamlit.expanders == []
    assert fake_streamlit.markdowns == []
    assert fake_streamlit.captions == []


def test_metadata_expander_precedes_core_parameters():
    """Keep loaded context immediately above the first editable parameter panel."""
    app_source = (REPOSITORY_ROOT / "app.py").read_text(encoding="utf-8")

    metadata_call_index = app_source.index("\nrender_metadata_expander(t)\n")
    core_call_index = app_source.index("\nrender_core_expander(t)\n")

    assert metadata_call_index < core_call_index


def test_metadata_expander_shows_a_title_without_requiring_description(monkeypatch):
    """Keep title-only valid profiles visible instead of requiring both fields."""
    fake_streamlit = _render_metadata(
        monkeypatch,
        {
            "id": "portable-rx",
            "title": {"en": "Portable RX"},
        },
    )

    assert fake_streamlit.expanders == [("🏷️ Metadata", True)]
    assert fake_streamlit.markdowns == [("**Portable RX**", {})]
    assert fake_streamlit.container_keys == []
    assert fake_streamlit.captions == []


def test_metadata_title_displays_markdown_punctuation_as_plain_text(monkeypatch):
    """Treat profile titles as text even though the title is visually bold."""
    fake_streamlit = _render_metadata(
        monkeypatch,
        {
            "id": "literal-title",
            "title": {
                "en": "Portable *RX* [paper](https://example.org)",
            },
        },
    )

    assert fake_streamlit.markdowns == [
        (
            "**Portable \\*RX\\* \\[paper\\]\\(https\\:\\/\\/example\\.org\\)**",
            {},
        )
    ]


@pytest.mark.parametrize(
    (
        "language",
        "titles",
        "descriptions",
        "expected_expander_label",
        "expected_title",
        "expected_description",
    ),
    [
        (
            "de",
            {"en": "English title", "de": "Deutscher Titel"},
            {"en": "English description", "de": "Deutsche Beschreibung"},
            "🏷️ Metadaten",
            "Deutscher Titel",
            "Deutsche Beschreibung",
        ),
        (
            "de",
            {"en": "English-only title"},
            {"en": "First line\n[Paper](https://example.org/paper)"},
            "🏷️ Metadaten",
            "English-only title",
            "First line  \n[Paper](https://example.org/paper)",
        ),
        (
            "en",
            {"fr": "Titre français"},
            {"fr": "Description française"},
            "🏷️ Metadata",
            "Titre français",
            "Description française",
        ),
    ],
)
def test_metadata_expander_resolves_localized_title_and_description(
    monkeypatch,
    language,
    titles,
    descriptions,
    expected_expander_label,
    expected_title,
    expected_description,
):
    """Resolve current language, English, then the first authored localization."""
    fake_streamlit = _render_metadata(
        monkeypatch,
        {
            "id": "localized-profile",
            "title": titles,
            "description": descriptions,
        },
        language,
    )

    assert fake_streamlit.expanders == [(expected_expander_label, True)]
    assert fake_streamlit.markdowns == [
        (
            config_panel._prepare_loaded_profile_title_markdown(expected_title),
            {},
        )
    ]
    assert fake_streamlit.container_keys == [
        "loaded_config_metadata_description"
    ]
    assert fake_streamlit.captions == [(expected_description, {})]


def test_config_load_replaces_or_clears_loaded_profile_snapshot():
    """Make the panel follow the latest loaded document, including profileless files."""
    session_state = _SessionState(lang="en")
    first_config = config_io.validate_config_document(
        _demo_document("vanhamel_rx_calibration")
    )
    second_document = _demo_document("milazzo_tx_buddy")
    second_config = config_io.validate_config_document(second_document)

    config_io.apply_config_state_values(first_config, session_state)
    assert session_state.loaded_config_profile == first_config["profile"]

    config_io.apply_config_state_values(second_config, session_state)
    assert session_state.loaded_config_profile == second_config["profile"]

    second_document.pop("profile")
    profileless_config = config_io.validate_config_document(second_document)
    config_io.apply_config_state_values(profileless_config, session_state)
    assert session_state.loaded_config_profile is None


def test_parameter_reset_preserves_loaded_profile_snapshot(monkeypatch):
    """Keep loaded metadata attached when an edit invalidates active results."""
    loaded_profile = {
        "id": "portable-rx",
        "title": {"en": "Portable RX"},
    }
    session_state = _SessionState(
        lang="en",
        run_mode="RX",
        active_demo_profile="portable-rx",
        loaded_config_profile=deepcopy(loaded_profile),
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_result_state", lambda _state: None)
    begin_analysis_submission(session_state, request_source="main_button")

    callbacks.reset_audit()

    assert session_state.run_mode is None
    assert session_state.active_demo_profile is None
    assert session_state.loaded_config_profile == loaded_profile
    assert get_analysis_submission(session_state) is None


@pytest.mark.parametrize(
    ("callback_name", "expected_run_mode"),
    [
        ("load_demo_profile_config", None),
        ("run_demo_profile", "RX"),
    ],
)
def test_public_demo_paths_preserve_loaded_metadata_after_execution(
    monkeypatch,
    callback_name,
    expected_run_mode,
):
    """Keep the selected demo metadata after either loading or executing it."""
    profile_id = "vanhamel_rx_calibration"
    rerun = Mock()
    session_state = _SessionState(
        lang="en",
        show_demo_launcher=True,
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state, rerun=rerun),
    )
    monkeypatch.setattr(callbacks, "reset_audit", lambda: None)
    monkeypatch.setattr(callbacks, "collapse_documentation", lambda _state: None)
    monkeypatch.setattr(callbacks, "reset_result_state", lambda _state: None)

    getattr(callbacks, callback_name)(profile_id)

    expected_profile = DEMO_PROFILES[profile_id]["configuration"]["profile"]
    assert session_state.loaded_config_profile == expected_profile
    assert session_state.active_demo_profile == profile_id
    assert session_state.run_mode == expected_run_mode
    assert session_state.show_demo_launcher is False
    rerun.assert_called_once_with()


def test_main_run_preserves_the_unchanged_loaded_demo_identity(monkeypatch):
    """Keep a green-button rerun in the demo query-cache policy."""
    profile_id = "vanhamel_rx_calibration"
    session_state = _SessionState(lang="en", show_demo_launcher=True)
    rerun = Mock()
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state, rerun=rerun),
    )
    monkeypatch.setattr(callbacks, "reset_result_state", lambda _state: None)

    callbacks.load_demo_profile_config(profile_id)
    begin_main_analysis_submission(session_state)
    request = claim_analysis_submission_request(session_state)

    assert request is not None
    assert request.source == "main_button"
    assert session_state.active_demo_profile == profile_id
    assert DEMO_PROFILES.get(session_state.active_demo_profile) is not None
    rerun.assert_called_once_with()

    app_source = (REPOSITORY_ROOT / "app.py").read_text(encoding="utf-8")
    assert "st.session_state.active_demo_profile = None" not in app_source
    assert "begin_main_analysis_submission(st.session_state)" in app_source
    assert "analysis_run_outcome == ANALYSIS_RUN_FOLLOWER_COMPLETED" in app_source


def test_factory_reset_clears_loaded_profile_snapshot(monkeypatch):
    """Hide metadata when the complete editable configuration returns to defaults."""
    session_state = _SessionState(
        lang="en",
        loaded_config_profile={
            "id": "portable-rx",
            "title": {"en": "Portable RX"},
        },
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_result_state", lambda _state: None)

    callbacks.set_reset_config()

    assert session_state.loaded_config_profile is None
