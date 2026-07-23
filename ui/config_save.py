"""Fragment-scoped saved-config preparation and download controls."""

from __future__ import annotations

import json

import streamlit as st

from i18n import T
from ui.config_io import build_config_payload, build_config_state_signature
from ui.result_state import get_active_run_time_window


CONFIG_SAVE_STATE_PREFIX = "config_save_"
_PROFILE_ID_WIDGET_KEY = f"{CONFIG_SAVE_STATE_PREFIX}profile_id"
_PROFILE_TITLE_WIDGET_KEY = f"{CONFIG_SAVE_STATE_PREFIX}profile_title"
_PROFILE_DESCRIPTION_WIDGET_KEY = f"{CONFIG_SAVE_STATE_PREFIX}profile_description"
_PROFILE_SOURCE_TOKEN_KEY = f"{CONFIG_SAVE_STATE_PREFIX}profile_source_token"
_TIME_POLICY_WIDGET_KEY = f"{CONFIG_SAVE_STATE_PREFIX}time_policy"
_TIME_POLICY_RUN_ID_KEY = f"{CONFIG_SAVE_STATE_PREFIX}time_policy_run_id"
_PREPARED_BYTES_KEY = f"{CONFIG_SAVE_STATE_PREFIX}prepared_bytes"
_PREPARED_FILENAME_KEY = f"{CONFIG_SAVE_STATE_PREFIX}prepared_filename"
_PREPARED_SIGNATURE_KEY = f"{CONFIG_SAVE_STATE_PREFIX}prepared_signature"

TIME_POLICY_FREEZE = "freeze"
TIME_POLICY_RELATIVE = "relative"


def _scoped_form_key(base_key, form_scope=None):
    """Return a unique widget key for one placement of the shared save form."""
    normalized_scope = str(form_scope or "").strip()
    return f"{base_key}_{normalized_scope}" if normalized_scope else base_key


def clear_config_save_state(session_state) -> None:
    """Clear transient save-form widgets and any prepared config download."""
    for state_key in tuple(session_state.keys()):
        if state_key.startswith(CONFIG_SAVE_STATE_PREFIX):
            session_state.pop(state_key, None)


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


def _initialize_time_policy(
    session_state,
    active_run_time_window,
    form_scope=None,
):
    """Default a newly resolved Last-X run to freezing its exact UTC interval."""
    time_policy_widget_key = _scoped_form_key(
        _TIME_POLICY_WIDGET_KEY,
        form_scope,
    )
    time_policy_run_id_key = _scoped_form_key(
        _TIME_POLICY_RUN_ID_KEY,
        form_scope,
    )
    active_run_id = (
        session_state.get("run_id") if active_run_time_window is not None else None
    )
    if active_run_id is not None:
        if session_state.get(time_policy_run_id_key) != active_run_id:
            session_state[time_policy_widget_key] = TIME_POLICY_FREEZE
            session_state[time_policy_run_id_key] = active_run_id
    else:
        session_state[time_policy_widget_key] = TIME_POLICY_RELATIVE
        session_state[time_policy_run_id_key] = None


@st.fragment
def render_config_save_control(
    *,
    popover_key="config_save_top_trigger",
    form_scope=None,
):
    """Render metadata, Last-X policy, preparation, and download in one fragment.

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
    time_policy_widget_key = _scoped_form_key(
        _TIME_POLICY_WIDGET_KEY,
        form_scope,
    )

    save_popover = st.popover(
        translations.get("btn_save_config", "Save Config"),
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
            translations.get(
                "txt_config_profile_intro",
                "Add reusable profile details, then prepare the config download.",
            )
        )
        title = st.text_input(
            translations.get("lbl_config_profile_title", "Title"),
            key=profile_title_widget_key,
        )
        description = st.text_area(
            translations.get(
                "lbl_config_profile_description",
                "Description (optional)",
            ),
            key=profile_description_widget_key,
        )
        profile_id = st.text_input(
            translations.get("lbl_config_profile_id", "Profile ID (optional)"),
            key=profile_id_widget_key,
            help=translations.get(
                "hlp_config_profile_id",
                "Leave blank to derive a stable ID from the title.",
            ),
        )

        is_last_x = session_state.get("val_time_mode") == "last_x"
        active_run_time_window = None
        time_policy = TIME_POLICY_RELATIVE
        if is_last_x:
            if session_state.get("run_mode"):
                active_run_time_window = get_active_run_time_window(session_state)
            _initialize_time_policy(
                session_state,
                active_run_time_window,
                form_scope,
            )
            time_policy_labels = {
                TIME_POLICY_FREEZE: translations.get(
                    "opt_config_time_freeze",
                    "Freeze the resolved UTC range",
                ),
                TIME_POLICY_RELATIVE: translations.get(
                    "opt_config_time_relative",
                    "Keep Last-X relative",
                ),
            }
            time_policy = st.radio(
                translations.get(
                    "lbl_config_time_policy",
                    "How should this Last-X time selection be saved?",
                ),
                (TIME_POLICY_FREEZE, TIME_POLICY_RELATIVE),
                key=time_policy_widget_key,
                format_func=time_policy_labels.__getitem__,
            )
            if active_run_time_window is not None:
                start_utc, end_utc = active_run_time_window
                st.caption(
                    translations.get(
                        "txt_config_resolved_window",
                        "Resolved run: {start} to {end}",
                    ).format(
                        start=start_utc.strftime("%Y-%m-%d %H:%M UTC"),
                        end=end_utc.strftime("%Y-%m-%d %H:%M UTC"),
                    )
                )
            elif time_policy == TIME_POLICY_FREEZE:
                st.warning(
                    translations.get(
                        "warn_config_freeze_unavailable",
                        "Run the analysis first to freeze its resolved UTC range.",
                    )
                )

        frozen_time_window = (
            active_run_time_window
            if is_last_x and time_policy == TIME_POLICY_FREEZE
            else None
        )
        can_prepare = bool(title.strip()) and not (
            is_last_x
            and time_policy == TIME_POLICY_FREEZE
            and active_run_time_window is None
        )
        prepare_clicked = st.button(
            translations.get("btn_prepare_config", "Prepare Config"),
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
                    frozen_time_window=frozen_time_window,
                    state=session_state,
                )
                prepared_signature = build_config_state_signature(
                    title=title,
                    description=description,
                    profile_id=profile_id,
                    language=language,
                    frozen_time_window=frozen_time_window,
                    state=session_state,
                )
                prepared_document = json.loads(config_bytes.decode("utf-8"))
                session_state.val_config_profile = prepared_document["profile"]
                session_state[_PREPARED_BYTES_KEY] = config_bytes
                session_state[_PREPARED_FILENAME_KEY] = config_filename
                session_state[_PREPARED_SIGNATURE_KEY] = prepared_signature
                st.success(
                    translations.get(
                        "msg_config_prepared",
                        "Config prepared. Download it below.",
                    )
                )
            except ValueError as exc:
                st.error(
                    translations.get(
                        "err_config_save",
                        "Config could not be prepared: {error}",
                    ).format(error=exc)
                )

        try:
            current_signature = build_config_state_signature(
                title=title,
                description=description,
                profile_id=profile_id,
                language=language,
                frozen_time_window=frozen_time_window,
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
                translations.get("btn_download_config", "Download Config"),
                data=session_state[_PREPARED_BYTES_KEY],
                file_name=session_state[_PREPARED_FILENAME_KEY],
                mime="application/json",
                icon=":material/save_alt:",
                type="primary",
                width="stretch",
                on_click="ignore",
            )
