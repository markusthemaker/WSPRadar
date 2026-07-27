"""Fragment-scoped saved-config preparation and download controls."""

from __future__ import annotations

import json

import streamlit as st

from i18n import T
from ui.config_io import (
    build_config_payload,
    build_config_state_signature,
    format_config_validation_error,
    log_config_validation_error,
)


CONFIG_SAVE_STATE_PREFIX = "config_save_"
_PROFILE_ID_WIDGET_KEY = f"{CONFIG_SAVE_STATE_PREFIX}profile_id"
_PROFILE_TITLE_WIDGET_KEY = f"{CONFIG_SAVE_STATE_PREFIX}profile_title"
_PROFILE_DESCRIPTION_WIDGET_KEY = f"{CONFIG_SAVE_STATE_PREFIX}profile_description"
_PROFILE_SOURCE_TOKEN_KEY = f"{CONFIG_SAVE_STATE_PREFIX}profile_source_token"
_PREPARED_BYTES_KEY = f"{CONFIG_SAVE_STATE_PREFIX}prepared_bytes"
_PREPARED_FILENAME_KEY = f"{CONFIG_SAVE_STATE_PREFIX}prepared_filename"
_PREPARED_SIGNATURE_KEY = f"{CONFIG_SAVE_STATE_PREFIX}prepared_signature"

def _scoped_form_key(base_key, form_scope=None):
    """Return a unique widget key for one placement of the shared save form."""
    normalized_scope = str(form_scope or "").strip()
    return f"{base_key}_{normalized_scope}" if normalized_scope else base_key


def _localized_profile_text(profile, field, language):
    """Return current-language profile text with English/first-value fallback."""
    localized_values = profile.get(field, {}) if isinstance(profile, dict) else {}
    if not isinstance(localized_values, dict):
        return ""
    if localized_values.get(language):
        return localized_values[language]
    if localized_values.get("en"):
        return localized_values["en"]
    return next(iter(localized_values.values()), "")


def _sync_profile_widget_defaults(session_state, language, form_scope=None):
    """Refresh save fields once when a different config profile is loaded."""
    profile_source_token_key = _scoped_form_key(
        _PROFILE_SOURCE_TOKEN_KEY,
        form_scope,
    )
    profile_id_widget_key = _scoped_form_key(_PROFILE_ID_WIDGET_KEY, form_scope)
    profile_title_widget_key = _scoped_form_key(
        _PROFILE_TITLE_WIDGET_KEY,
        form_scope,
    )
    profile_description_widget_key = _scoped_form_key(
        _PROFILE_DESCRIPTION_WIDGET_KEY,
        form_scope,
    )
    profile = session_state.get("val_config_profile")
    profile = profile if isinstance(profile, dict) else {}
    profile_source_token = json.dumps(
        {"language": language, "profile": profile},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    if session_state.get(profile_source_token_key) == profile_source_token:
        return
    session_state[profile_source_token_key] = profile_source_token
    session_state[profile_id_widget_key] = profile.get("id", "")
    session_state[profile_title_widget_key] = _localized_profile_text(
        profile,
        "title",
        language,
    )
    session_state[profile_description_widget_key] = _localized_profile_text(
        profile,
        "description",
        language,
    )


@st.fragment
def render_config_save_control(
    *,
    popover_key="config_save_top_trigger",
    form_scope=None,
):
    """Render metadata, preparation, and download in one fragment.

    Preparing within this fragment reads inspector state at click time, including
    selections changed by the independent Segment Inspector fragment.
    """
    session_state = st.session_state
    language = session_state.get("lang", "en")
    translations = T[language]
    analysis_direction = session_state.get("val_analysis_direction")
    is_save_available = analysis_direction in {"rx", "tx"}
    profile_title_widget_key = _scoped_form_key(
        _PROFILE_TITLE_WIDGET_KEY,
        form_scope,
    )
    profile_description_widget_key = _scoped_form_key(
        _PROFILE_DESCRIPTION_WIDGET_KEY,
        form_scope,
    )
    profile_id_widget_key = _scoped_form_key(_PROFILE_ID_WIDGET_KEY, form_scope)

    save_popover = st.popover(
        translations["btn_save_config"],
        icon=":material/save:",
        type="primary",
        width="stretch",
        disabled=not is_save_available,
        key=popover_key,
        on_change="rerun",
    )
    if not save_popover.open:
        return

    with save_popover:
        _sync_profile_widget_defaults(session_state, language, form_scope)
        st.caption(
            translations["txt_config_profile_intro"]
        )
        title = st.text_input(
            translations["lbl_config_profile_title"],
            key=profile_title_widget_key,
        )
        description = st.text_area(
            translations["lbl_config_profile_description"],
            key=profile_description_widget_key,
        )
        profile_id = st.text_input(
            translations["lbl_config_profile_id"],
            key=profile_id_widget_key,
            help=translations["hlp_config_profile_id"],
        )

        can_prepare = bool(title.strip())
        prepare_clicked = st.button(
            translations["btn_prepare_config"],
            icon=":material/download:",
            type="primary",
            width="stretch",
            disabled=not can_prepare,
        )

        if prepare_clicked:
            try:
                config_bytes, config_filename = build_config_payload(
                    title=title,
                    description=description,
                    profile_id=profile_id,
                    language=language,
                    state=session_state,
                )
                prepared_signature = build_config_state_signature(
                    title=title,
                    description=description,
                    profile_id=profile_id,
                    language=language,
                    state=session_state,
                )
                prepared_document = json.loads(config_bytes.decode("utf-8"))
                session_state.val_config_profile = prepared_document["profile"]
                session_state[_PREPARED_BYTES_KEY] = config_bytes
                session_state[_PREPARED_FILENAME_KEY] = config_filename
                session_state[_PREPARED_SIGNATURE_KEY] = prepared_signature
                st.success(translations["msg_config_prepared"])
            except ValueError as exc:
                log_config_validation_error(exc, operation="save")
                st.error(format_config_validation_error(exc, translations))

        try:
            current_signature = build_config_state_signature(
                title=title,
                description=description,
                profile_id=profile_id,
                language=language,
                state=session_state,
            )
        except ValueError:
            current_signature = None

        if (
            current_signature is not None
            and current_signature == session_state.get(_PREPARED_SIGNATURE_KEY)
            and session_state.get(_PREPARED_BYTES_KEY)
        ):
            st.download_button(
                translations["btn_download_config"],
                data=session_state[_PREPARED_BYTES_KEY],
                file_name=session_state[_PREPARED_FILENAME_KEY],
                mime="application/json",
                icon=":material/save_alt:",
                type="primary",
                width="stretch",
                on_click="ignore",
            )
