"""Focused regression coverage for fragment-scoped config-save state."""

from types import SimpleNamespace
import json

import pytest
from streamlit.testing.v1 import AppTest

from ui import config_save, result_state


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

@pytest.mark.parametrize(
    "prepare_clicked,profile_changed,has_prepared_results,reject_save,expect_rerun",
    [
        (True, True, True, False, True),
        (True, True, False, False, False),
        (True, False, True, False, False),
        (False, True, True, False, False),
        (True, True, True, True, False),
    ],
    ids=["commit-invalidates-download", "commit-without-download", "no-op-commit", "draft", "rejected"],
)
def test_profile_save_refreshes_outer_download_only_after_changed_commit(
    monkeypatch, prepare_clicked, profile_changed, has_prepared_results,
    reject_save, expect_rerun,
):
    class OpenPopover:
        open = True
        def __enter__(self):
            return self
        def __exit__(self, *_args):
            return None

    class AppRerunRequested(BaseException):
        pass

    original_profile = {"id": "saved-run", "title": {"en": "Original title"}}
    new_profile = {
        "id": "saved-run",
        "title": {"en": "Changed title" if profile_changed else "Original title"},
    }
    completed_run = object()
    registry = {"RX": "registered evidence"}
    session_state = {
        "lang": "en", "val_analysis_direction": "rx", "run_mode": "RX",
        "run_id": 42, "val_config_profile": original_profile,
        "loaded_config_profile": original_profile,
        result_state.COMPLETED_RUN_SNAPSHOT_KEY: completed_run,
        result_state.EXPORT_STATE_KEY: registry,
    }
    if has_prepared_results:
        session_state.update({
            result_state.EXPORT_ZIP_BYTES_KEY: b"old prepared results",
            result_state.EXPORT_ZIP_FILENAME_KEY: "results.zip",
            result_state.EXPORT_ZIP_SIGNATURE_KEY: "old signature",
        })
    submitted_bytes = json.dumps({"profile": new_profile}).encode("utf-8")
    reruns = []
    downloads = []
    errors = []

    def rerun(*, scope):
        reruns.append(scope)
        raise AppRerunRequested

    def text_input(_label, *, key, **_kwargs):
        if key == config_save._PROFILE_ID_WIDGET_KEY:
            return "saved-run"
        return new_profile["title"]["en"]

    def build_config(**_kwargs):
        if reject_save:
            raise ValueError("Invalid saved profile")
        return submitted_bytes, "saved-run.config"

    fake_streamlit = SimpleNamespace(
        session_state=session_state,
        popover=lambda *_args, **_kwargs: OpenPopover(),
        caption=lambda *_args, **_kwargs: None,
        text_input=text_input,
        text_area=lambda *_args, **_kwargs: "",
        button=lambda *_args, **_kwargs: prepare_clicked,
        success=lambda *_args, **_kwargs: None,
        error=lambda text: errors.append(text),
        download_button=lambda *_args, **kwargs: downloads.append(kwargs),
        rerun=rerun,
    )
    monkeypatch.setattr(config_save, "st", fake_streamlit)
    monkeypatch.setattr(config_save, "_sync_profile_widget_defaults", lambda *_args: None)
    monkeypatch.setattr(config_save, "build_config_payload", build_config)
    monkeypatch.setattr(config_save, "build_config_state_signature", lambda **_kwargs: "new config signature")
    monkeypatch.setattr(config_save, "log_config_validation_error", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(config_save, "format_config_validation_error", lambda error, _labels: str(error))

    if expect_rerun:
        with pytest.raises(AppRerunRequested):
            config_save.render_config_save_control.__wrapped__()
    else:
        config_save.render_config_save_control.__wrapped__()

    committed = prepare_clicked and not reject_save
    assert reruns == (["app"] if expect_rerun else [])
    assert session_state[result_state.COMPLETED_RUN_SNAPSHOT_KEY] is completed_run
    assert session_state[result_state.EXPORT_STATE_KEY] is registry
    assert session_state["loaded_config_profile"] is original_profile
    assert session_state["run_mode"] == "RX"
    assert session_state["run_id"] == 42
    assert session_state["val_config_profile"] == (new_profile if committed else original_profile)
    if committed and profile_changed:
        assert all(key not in session_state for key in result_state.PREPARED_RESULT_STATE_KEYS)
    elif has_prepared_results:
        assert session_state[result_state.EXPORT_ZIP_BYTES_KEY] == b"old prepared results"
    if committed:
        assert session_state[config_save._PREPARED_BYTES_KEY] == submitted_bytes
        assert session_state[config_save._PREPARED_FILENAME_KEY] == "saved-run.config"
        assert session_state[config_save._PREPARED_SIGNATURE_KEY] == "new config signature"
    else:
        assert config_save._PREPARED_BYTES_KEY not in session_state
    assert bool(errors) is reject_save


_PROFILE_SAVE_APP = r'''
import streamlit as st
from ui import config_save, result_state

st.session_state["outer_render_count"] = st.session_state.get("outer_render_count", 0) + 1
if st.session_state.get(result_state.EXPORT_ZIP_BYTES_KEY):
    st.download_button(
        "Prepared results", st.session_state[result_state.EXPORT_ZIP_BYTES_KEY],
        file_name="prepared.zip", key="outer_prepared_results",
    )
config_save.render_config_save_control(
    popover_key="profile_editor", form_scope="results",
)
'''


@pytest.mark.parametrize("interaction", ["changed-commit", "draft", "no-op-commit"])
def test_profile_fragment_app_rerun_removes_rendered_stale_download(monkeypatch, interaction):
    """Exercise real widgets and app reruns around the independent save fragment."""
    def config_document(*, title, profile_id, **_kwargs):
        profile = {"id": profile_id, "title": {"en": title}}
        return json.dumps({"profile": profile}).encode("utf-8"), "saved-run.config"

    monkeypatch.setattr(config_save, "build_config_payload", config_document)
    monkeypatch.setattr(
        config_save, "build_config_state_signature",
        lambda *, title, **_kwargs: f"config:{title}",
    )
    application = AppTest.from_string(_PROFILE_SAVE_APP, default_timeout=15)
    profile = {"id": "saved-run", "title": {"en": "Original title"}}
    completed_marker = {"run_id": 42, "scientific_result": "retained"}
    seeded_state = {
        "lang": "en", "val_analysis_direction": "rx", "run_id": 42,
        "run_mode": "RX", "val_config_profile": profile, "profile_editor": True,
        result_state.COMPLETED_RUN_SNAPSHOT_KEY: completed_marker,
        result_state.EXPORT_ZIP_BYTES_KEY: b"already prepared evidence",
        result_state.EXPORT_ZIP_FILENAME_KEY: "prepared.zip",
        result_state.EXPORT_ZIP_SIGNATURE_KEY: "previous signature",
    }
    for key, value in seeded_state.items():
        application.session_state[key] = value

    application.run()
    assert not application.exception
    assert any(widget.proto.label == "Prepared results" for widget in application.get("download_button"))
    title_key = config_save._scoped_form_key(config_save._PROFILE_TITLE_WIDGET_KEY, "results")
    if interaction != "no-op-commit":
        application.text_input(key=title_key).set_value("Changed title").run()
        assert not application.exception
        assert application.session_state["val_config_profile"] == profile
        assert application.session_state[result_state.EXPORT_ZIP_BYTES_KEY] == b"already prepared evidence"
    before_commit_renders = application.session_state["outer_render_count"]
    if interaction != "draft":
        application.button[0].click().run()

    assert not application.exception
    assert application.session_state[result_state.COMPLETED_RUN_SNAPSHOT_KEY] == completed_marker
    assert application.session_state["run_mode"] == "RX"
    assert application.session_state["run_id"] == 42
    outer_downloads = [
        widget for widget in application.get("download_button")
        if widget.proto.label == "Prepared results"
    ]
    if interaction == "changed-commit":
        assert application.session_state["val_config_profile"]["title"]["en"] == "Changed title"
        assert all(key not in application.session_state for key in result_state.PREPARED_RESULT_STATE_KEYS)
        assert outer_downloads == []
        # AppTest's widget event starts one full run. The real st.rerun(scope="app")
        # must add another pass so the outer download drawn before commit disappears.
        assert application.session_state["outer_render_count"] == before_commit_renders + 2
    else:
        assert application.session_state["val_config_profile"] == profile
        assert application.session_state[result_state.EXPORT_ZIP_BYTES_KEY] == b"already prepared evidence"
        assert len(outer_downloads) == 1
        expected_renders = before_commit_renders + (interaction == "no-op-commit")
        assert application.session_state["outer_render_count"] == expected_renders
