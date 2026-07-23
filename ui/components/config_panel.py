"""
Config Panel Components Module.
Contains the UI rendering functions for the main configuration expanders.
Separating this from app.py keeps the main orchestrator file clean and focused.
"""

from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from string import punctuation

import streamlit as st

from config import (
    MAX_DAYS_HISTORY,
    BAND_MAP,
    MAX_DYNAMIC_RADIUS_KM,
    MAP_SCOPE_OPTIONS,
    SNR_CORRECTION_MODES,
    TX_AB_REPEAT_INTERVAL_OPTIONS,
)
from config.demo_profiles import prepare_demo_description_markdown
from core.input_validation import (
    is_valid_callsign,
    is_valid_grid4,
    is_valid_locator,
    normalize_ascii_upper,
)
from ui.callbacks import (
    reset_audit, handle_analysis_direction_change, handle_comp_mode_change,
    handle_reference_correction_context_change,
    handle_tx_ab_reference_start_change, handle_tx_ab_repeat_interval_change,
    handle_tx_ab_target_start_change, swap_tx_ab_starts,
)


_PROFILE_TITLE_MARKDOWN_ESCAPES = str.maketrans(
    {character: f"\\{character}" for character in punctuation}
)


def _resolve_loaded_profile_text(profile, field, language):
    """Resolve loaded profile text in the UI language with safe fallbacks."""
    localized_values = profile.get(field, {}) if isinstance(profile, dict) else {}
    if not isinstance(localized_values, dict):
        return ""

    preferred_languages = tuple(
        dict.fromkeys((str(language or "").strip(), "en", *localized_values))
    )
    for language_key in preferred_languages:
        localized_text = localized_values.get(language_key)
        if isinstance(localized_text, str) and localized_text.strip():
            return localized_text.strip()
    return ""


def _prepare_loaded_profile_title_markdown(title):
    """Bold a profile title while preserving every punctuation character."""
    escaped_title = str(title or "").translate(_PROFILE_TITLE_MARKDOWN_ESCAPES)
    return f"**{escaped_title}**"


def render_metadata_expander(t):
    """Render available title and description from the last loaded profile."""
    loaded_profile = st.session_state.get("loaded_config_profile")
    language = st.session_state.get("lang", "en")
    title = _resolve_loaded_profile_text(loaded_profile, "title", language)
    description = _resolve_loaded_profile_text(
        loaded_profile,
        "description",
        language,
    )
    if not title and not description:
        return

    with st.expander(t.get("exp_metadata", "🏷️ Metadata"), expanded=True):
        if title:
            st.markdown(_prepare_loaded_profile_title_markdown(title))
        if description:
            with st.container(key="loaded_config_metadata_description"):
                st.caption(prepare_demo_description_markdown(description))


def _normalize_text_state(
    key,
    should_uppercase=False,
    callback=None,
    callback_args=(),
    callback_kwargs=None,
):
    """Normalize one identity field before its ordinary change callback."""
    value = st.session_state.get(key)
    if isinstance(value, str):
        normalized_value = value.strip()
        if should_uppercase:
            normalized_value = normalize_ascii_upper(normalized_value)
        st.session_state[key] = normalized_value
    if callback:
        callback(*(callback_args or ()), **(callback_kwargs or {}))

def _round_float_state(key, digits=1, callback=None, callback_args=(), callback_kwargs=None):
    value = st.session_state.get(key)
    if value is not None:
        st.session_state[key] = round(float(value), digits)
    if callback:
        callback(*(callback_args or ()), **(callback_kwargs or {}))


def _normalize_reference_correction_state(
    callback=None,
    callback_args=(),
    callback_kwargs=None,
):
    """Normalize the correction value and preserve its explicit semantic mode."""
    correction_db = round(
        float(st.session_state.get("val_benchmark_offset_db", 0.0)),
        1,
    )
    st.session_state.val_benchmark_offset_db = correction_db
    correction_mode = st.session_state.get("val_snr_correction_mode")
    if correction_db != 0.0:
        correction_mode = "established_offset"
    elif correction_mode not in SNR_CORRECTION_MODES:
        correction_mode = "no_offset"
    if (
        st.session_state.get("val_comp_mode") == "local_neighborhood"
        and correction_mode == "establish_offset"
    ):
        correction_mode = "no_offset"
    st.session_state.val_snr_correction_mode = correction_mode
    if callback:
        callback(*(callback_args or ()), **(callback_kwargs or {}))


def text_input_no_autocomplete(*args, **kwargs):
    """Render a text input with optional identity normalization."""
    kwargs.setdefault("autocomplete", "off")
    should_uppercase = bool(kwargs.pop("normalize_uppercase", False))
    key = kwargs.get("key")
    if key:
        callback = kwargs.get("on_change")
        callback_args = kwargs.pop("args", ())
        callback_kwargs = kwargs.pop("kwargs", {})
        kwargs["on_change"] = _normalize_text_state
        kwargs["args"] = (
            key,
            should_uppercase,
            callback,
            callback_args,
            callback_kwargs,
        )
    return st.text_input(*args, **kwargs)


def _render_identity_format_error(
    t,
    value,
    *,
    identity_kind,
    message_key=None,
):
    """Show one localized point-of-entry error for a malformed identity."""
    normalized_value = str(value or "").strip()
    if not normalized_value:
        return True
    if identity_kind == "callsign":
        is_valid = is_valid_callsign(normalized_value)
        default_message_key = "err_callsign_format"
    elif identity_kind == "grid4":
        is_valid = is_valid_grid4(normalized_value)
        default_message_key = "err_reference_grid4_format"
    elif identity_kind == "qth":
        is_valid = is_valid_locator(normalized_value)
        default_message_key = "err_qth_format"
    else:
        raise ValueError(f"Unknown identity kind {identity_kind!r}.")
    if not is_valid:
        st.error(t[message_key or default_message_key])
    return is_valid

def _benchmark_mode_options(t):
    """Return stable Success/Compare design tokens in their displayed order."""
    return [
        "none",
        "hardware_ab",
        "reference_station",
        "local_neighborhood",
    ]


def _format_benchmark_mode(t, benchmark_mode):
    """Localize one stable benchmark-design token for display."""
    translation_keys = {
        "none": "opt_comp_none",
        "hardware_ab": "opt_comp_self",
        "reference_station": "opt_comp_buddy",
        "local_neighborhood": "opt_comp_radius",
    }
    return t[translation_keys[benchmark_mode]]


def _comparison_column_widths(t, comparison_mode, analysis_direction):
    """Return the consistent half-width split used by configuration panels."""
    return [0.5, 0.5]


def _tx_ab_threshold_label_and_help(t):
    """Return evidence-threshold wording for scheduled TX A/B pairs."""
    return (
        t.get("cfg_min_joint_pairs", "Min. Joint Pairs"),
        t.get(
            "hlp_min_joint_pairs",
            "Sequential TX A/B requires joint scheduled pairs.",
        ),
    )


def _render_reference_identity(
    t,
    *,
    derives_hardware_grid4,
    on_change=reset_audit,
    on_change_args=(),
    help_overrides=None,
):
    """Render Target/Reference identities and the mode-specific QTH contract.

    Reference Station owns an editable four-character Reference grid. Hardware
    A/B instead displays one shared grid-4 derived from Target QTH, without
    mutating the inactive Reference Station field in session state.
    """
    help_overrides = help_overrides or {}
    target_callsign = normalize_ascii_upper(
        st.session_state.get("val_callsign", "")
    )
    target_qth = normalize_ascii_upper(st.session_state.get("val_qth", ""))
    hardware_grid4 = target_qth[:4] if is_valid_locator(target_qth) else ""

    target_callsign_column, reference_callsign_column = st.columns(
        2,
        gap="large",
    )
    with target_callsign_column:
        text_input_no_autocomplete(
            t.get("lbl_target_callsign", "Target Callsign"),
            value=target_callsign,
            disabled=True,
        )
    with reference_callsign_column:
        text_input_no_autocomplete(
            t.get("lbl_reference_callsign", "Reference Callsign"),
            key="val_ref_callsign",
            placeholder=t.get(
                "ph_reference_callsign",
                "e.g. DL1MKS/P or DL1MKS-1",
            ),
            help=help_overrides.get(
                "reference_callsign",
                t.get(
                    "hlp_callsign_entry",
                    "Use the exact WSPR archive identifier; standard callsign forms are recommended.",
                ),
            ),
            max_chars=15,
            normalize_uppercase=True,
            disabled=st.session_state.is_demo_mode,
            on_change=on_change,
            args=on_change_args,
        )

    target_qth_column, reference_qth_column = st.columns(2, gap="large")
    with target_qth_column:
        text_input_no_autocomplete(
            (
                t.get("lbl_target_grid4", "Target Grid-4")
                if derives_hardware_grid4
                else t.get("lbl_target_qth", "Target QTH")
            ),
            value=hardware_grid4 if derives_hardware_grid4 else target_qth,
            disabled=True,
        )
    with reference_qth_column:
        if derives_hardware_grid4:
            text_input_no_autocomplete(
                t.get("lbl_reference_grid4", "Reference Grid-4"),
                value=hardware_grid4,
                disabled=True,
            )
        else:
            reference_qth_help = help_overrides.get("reference_qth")
            text_input_no_autocomplete(
                t.get("lbl_reference_grid4", "Reference Grid-4"),
                key="val_ref_qth",
                placeholder=t.get("ph_reference_qth", "e.g. JN37"),
                max_chars=4,
                normalize_uppercase=True,
                disabled=st.session_state.is_demo_mode,
                on_change=on_change,
                args=on_change_args,
                **(
                    {"help": reference_qth_help}
                    if reference_qth_help
                    else {}
                ),
            )

    reference_callsign = normalize_ascii_upper(
        st.session_state.get("val_ref_callsign", "")
    )
    is_reference_callsign_valid = _render_identity_format_error(
        t,
        reference_callsign,
        identity_kind="callsign",
        message_key="err_reference_callsign_format",
    )
    if not derives_hardware_grid4:
        _render_identity_format_error(
            t,
            st.session_state.get("val_ref_qth", ""),
            identity_kind="grid4",
        )
    if (
        is_reference_callsign_valid
        and reference_callsign
        and reference_callsign == target_callsign
    ):
        st.error(t.get("err_reference_callsign_same", t["err_self_test"]))


def _render_tx_ab_method_selector(
    t,
    *,
    on_change=reset_audit,
    on_change_args=(),
    method_content=None,
    help_text=None,
):
    """Render the governing TX A/B method in its editor-specific presentation."""
    methods = ("simultaneous", "sequential")
    if method_content is not None:
        st.radio(
            t.get("lbl_tx_ab_method", "TX A/B Method"),
            methods,
            key="val_tx_ab_method",
            format_func=lambda method: method_content[method]["label"],
            captions=tuple(
                method_content[method]["description"] for method in methods
            ),
            help=help_text,
            disabled=st.session_state.is_demo_mode,
            width="stretch",
            on_change=on_change,
            args=on_change_args,
        )
        return

    st.segmented_control(
        t.get("lbl_tx_ab_method", "TX A/B Method"),
        methods,
        selection_mode="single",
        required=True,
        key="val_tx_ab_method",
        format_func=lambda method: t.get(
            f"opt_tx_ab_{method}",
            method.title(),
        ),
        disabled=st.session_state.is_demo_mode,
        width="stretch",
        on_change=on_change,
        args=on_change_args,
    )


def _tx_ab_schedule_preview(repeat_interval, target_start, reference_start):
    """Return one-hour schedule rows and the nearest cyclic separation."""
    target_minutes = tuple(range(int(target_start), 60, int(repeat_interval)))
    reference_minutes = tuple(
        range(int(reference_start), 60, int(repeat_interval))
    )
    forward_gap = (int(reference_start) - int(target_start)) % int(repeat_interval)
    separation_minutes = min(forward_gap, int(repeat_interval) - forward_gap)
    return target_minutes, reference_minutes, separation_minutes


def _format_utc_minute(minute):
    """Format one UTC minute phase for compact schedule controls and previews."""
    return f"{int(minute):02d} UTC"


def _render_tx_ab_schedule(
    t,
    *,
    on_change=reset_audit,
    on_change_args=(),
):
    """Render the shared repeat interval, coupled starts, and schedule preview."""
    repeat_interval = int(
        st.session_state.get("val_tx_ab_repeat_interval_minutes", 10)
    )
    target_start = int(st.session_state.get("val_tx_ab_target_start_minute", 0))
    reference_start = int(
        st.session_state.get("val_tx_ab_reference_start_minute", 2)
    )
    permitted_starts = tuple(range(0, repeat_interval, 2))
    target_options = tuple(
        start for start in permitted_starts if start != reference_start
    )
    reference_options = tuple(
        start for start in permitted_starts if start != target_start
    )

    with st.container(border=True):
        st.markdown(f"**{t.get('lbl_tx_ab_schedule', 'TX A/B Schedule')}**")
        st.selectbox(
            t.get("lbl_tx_ab_repeat_interval", "Repeat Interval"),
            TX_AB_REPEAT_INTERVAL_OPTIONS,
            key="val_tx_ab_repeat_interval_minutes",
            format_func=lambda minutes: f"{minutes} min",
            disabled=st.session_state.is_demo_mode,
            help=t.get("hlp_tx_ab_repeat_interval", ""),
            on_change=handle_tx_ab_repeat_interval_change,
            args=(on_change, on_change_args),
        )
        st.caption(
            t.get(
                "txt_tx_ab_shared_interval",
                "Shared by Target and Reference paths",
            )
        )

        target_column, swap_column, reference_column = st.columns(
            [0.46, 0.08, 0.46],
            gap="small",
            vertical_alignment="bottom",
        )
        with target_column:
            st.selectbox(
                t.get("lbl_tx_ab_target_start", "Target Start"),
                target_options,
                key="val_tx_ab_target_start_minute",
                format_func=_format_utc_minute,
                disabled=st.session_state.is_demo_mode,
                help=t.get("hlp_tx_ab_start", ""),
                on_change=handle_tx_ab_target_start_change,
                args=(on_change, on_change_args),
            )
        with swap_column:
            st.button(
                "⇄",
                key="swap_tx_ab_schedule_starts",
                help=t.get("hlp_tx_ab_swap", "Swap Target and Reference starts"),
                disabled=st.session_state.is_demo_mode,
                on_click=swap_tx_ab_starts,
                args=(on_change, on_change_args),
                width="stretch",
            )
        with reference_column:
            st.selectbox(
                t.get("lbl_tx_ab_reference_start", "Reference Start"),
                reference_options,
                key="val_tx_ab_reference_start_minute",
                format_func=_format_utc_minute,
                disabled=st.session_state.is_demo_mode,
                help=t.get("hlp_tx_ab_start", ""),
                on_change=handle_tx_ab_reference_start_change,
                args=(on_change, on_change_args),
            )

        target_minutes, reference_minutes, separation_minutes = (
            _tx_ab_schedule_preview(
                repeat_interval,
                target_start,
                reference_start,
            )
        )
        target_preview = ", ".join(f"{minute:02d}" for minute in target_minutes)
        reference_preview = ", ".join(
            f"{minute:02d}" for minute in reference_minutes
        )
        st.markdown(
            f"**{t.get('txt_target', 'Target')}:** `{target_preview}`  \n"
            f"**{t.get('txt_reference', 'Reference')}:** `{reference_preview}`"
        )
        transmissions_per_hour = 60 // repeat_interval
        st.success(
            t.get(
                "txt_tx_ab_schedule_valid",
                "Disjoint schedules · {separation} min separation · "
                "{transmissions} transmissions/hour/path",
            ).format(
                separation=separation_minutes,
                transmissions=transmissions_per_hour,
            ),
            icon=":material/check_circle:",
        )
        if repeat_interval in {4, 6}:
            st.warning(t.get("warn_tx_ab_high_duty", ""), icon=":material/warning:")

def _render_analysis_direction_selector(
    t,
    *,
    on_change=handle_analysis_direction_change,
    on_change_args=(),
):
    """Render the required RX/TX choice as one full-width segmented control."""
    st.segmented_control(
        t["lbl_analysis_selector"],
        ("rx", "tx"),
        selection_mode="single",
        required=True,
        key="val_analysis_direction",
        format_func=lambda direction: t[f"opt_analysis_{direction}"],
        disabled=st.session_state.is_demo_mode,
        label_visibility="collapsed",
        width="stretch",
        on_change=on_change,
        args=on_change_args,
    )

def render_target_and_window_fields(
    t,
    *,
    on_change=reset_audit,
    on_change_args=(),
    correction_context_on_change=None,
    correction_context_on_change_args=(),
    help_overrides=None,
):
    """Render shared Target identity, band, and time controls.

    Both input editors use the same widget keys, normalization and scientific
    callbacks. ``help_overrides`` adds Guided explanations without changing the
    canonical values or Classic wording. Identity/QTH/band changes may use a
    separate callback because they invalidate an established pair correction,
    while changing only the time window does not.
    """
    help_overrides = help_overrides or {}
    correction_context_on_change = correction_context_on_change or on_change
    correction_context_on_change_args = (
        correction_context_on_change_args
        if correction_context_on_change_args
        else on_change_args
    )

    # Build widgets column-first so keyboard navigation moves down the left
    # column before continuing at the top of the right column.
    core_left, core_right = st.columns([0.5, 0.5], gap="large")
    with core_left:
        direction = st.session_state.get("val_analysis_direction")
        callsign_label = t.get(f"lbl_callsign_{direction}", t["lbl_callsign"])
        text_input_no_autocomplete(
            callsign_label,
            key="val_callsign",
            help=help_overrides.get(
                "callsign",
                t.get(
                    "hlp_callsign_entry",
                    "Use the exact WSPR archive identifier; standard callsign forms are recommended.",
                ),
            ),
            max_chars=15,
            normalize_uppercase=True,
            disabled=st.session_state.is_demo_mode,
            on_change=correction_context_on_change,
            args=correction_context_on_change_args,
        )
        _render_identity_format_error(
            t,
            st.session_state.get("val_callsign", ""),
            identity_kind="callsign",
        )
        text_input_no_autocomplete(
            t["lbl_qth"],
            key="val_qth",
            help=help_overrides.get("qth"),
            max_chars=6,
            normalize_uppercase=True,
            disabled=st.session_state.is_demo_mode,
            on_change=correction_context_on_change,
            args=correction_context_on_change_args,
        )
        _render_identity_format_error(
            t,
            st.session_state.get("val_qth", ""),
            identity_kind="qth",
        )
        st.selectbox(
            t["lbl_band"],
            list(BAND_MAP.keys()),
            key="val_band",
            help=help_overrides.get("band"),
            disabled=st.session_state.is_demo_mode,
            on_change=correction_context_on_change,
            args=correction_context_on_change_args,
        )

    with core_right:
        st.radio(
            t["lbl_time_mode"],
            ["last_x", "custom"],
            key="val_time_mode",
            horizontal=True,
            help=help_overrides.get("time"),
            disabled=st.session_state.is_demo_mode,
            on_change=on_change,
            args=on_change_args,
            format_func=lambda time_mode: t[
                "opt_last_x" if time_mode == "last_x" else "opt_custom"
            ],
        )

        if st.session_state.val_time_mode == "last_x":
            st.slider(
                t["lbl_hours"],
                1,
                168,
                key="val_hours",
                disabled=st.session_state.is_demo_mode,
                on_change=on_change,
                args=on_change_args,
            )
        else:
            today_utc = datetime.now(timezone.utc).date()

            date_start, date_end = st.columns(
                2, gap="large", vertical_alignment="bottom"
            )
            with date_start:
                st.date_input(
                    t["lbl_start_d"],
                    key="val_start_d",
                    min_value=datetime(2008, 1, 1, tzinfo=timezone.utc).date(),
                    max_value=today_utc,
                    disabled=st.session_state.is_demo_mode,
                    on_change=on_change,
                    args=on_change_args,
                    format="DD-MM-YYYY",
                )
            max_allowed_end = min(
                st.session_state.val_start_d + timedelta(days=MAX_DAYS_HISTORY),
                today_utc,
            )
            min_allowed_end = st.session_state.val_start_d

            # Defensive check inside the render loop.
            if st.session_state.val_end_d > max_allowed_end:
                st.session_state.val_end_d = max_allowed_end
            elif st.session_state.val_end_d < min_allowed_end:
                st.session_state.val_end_d = min_allowed_end

            with date_end:
                st.date_input(
                    t["lbl_end_d"],
                    key="val_end_d",
                    min_value=min_allowed_end,
                    max_value=max_allowed_end,
                    disabled=st.session_state.is_demo_mode,
                    on_change=on_change,
                    args=on_change_args,
                    format="DD-MM-YYYY",
                )

            time_start, time_end = st.columns(
                2, gap="large", vertical_alignment="bottom"
            )
            with time_start:
                st.time_input(
                    t["lbl_start_t"],
                    key="val_start_t",
                    disabled=st.session_state.is_demo_mode,
                    on_change=on_change,
                    args=on_change_args,
                )
            with time_end:
                st.time_input(
                    t["lbl_end_t"],
                    key="val_end_t",
                    disabled=st.session_state.is_demo_mode,
                    on_change=on_change,
                    args=on_change_args,
                )


def render_core_expander(t):
    """Render analysis direction, target identity, band, and time controls."""
    with st.expander(
        t["exp_core"],
        expanded=st.session_state.get("config_panels_expanded", True),
    ):
        _render_analysis_direction_selector(t)
        render_target_and_window_fields(
            t,
            correction_context_on_change=handle_reference_correction_context_change,
        )


def render_reference_correction_field(
    t,
    *,
    on_change=reset_audit,
    on_change_args=(),
    help_text=None,
):
    """Render the shared Reference-side SNR correction field."""
    st.number_input(
        t["lbl_benchmark_offset_db"],
        min_value=-99.9,
        max_value=99.9,
        step=0.1,
        format="%.1f",
        key="val_benchmark_offset_db",
        help=help_text or t["hlp_benchmark_offset_db"],
        on_change=_normalize_reference_correction_state,
        args=(
            on_change,
            on_change_args,
            {},
        ),
    )


def render_reference_design_fields(
    t,
    *,
    on_change=handle_reference_correction_context_change,
    on_change_args=(),
    help_overrides=None,
    local_benchmark_content=None,
    tx_ab_method_content=None,
):
    """Render canonical Reference fields with optional Guided choice captions."""
    help_overrides = help_overrides or {}
    comp_mode = st.session_state.get("val_comp_mode")
    analysis_direction = st.session_state.get("val_analysis_direction")
    if comp_mode == "local_neighborhood":
        local_methods = ("local_median", "local_best")
        local_radio_kwargs = {}
        if local_benchmark_content is not None:
            format_local_benchmark = (
                lambda method: local_benchmark_content[method]["label"]
            )
            local_radio_kwargs = {
                "captions": tuple(
                    local_benchmark_content[method]["description"]
                    for method in local_methods
                ),
                "width": "stretch",
            }
        else:
            format_local_benchmark = lambda method: t[
                (
                    "opt_local_median"
                    if method == "local_median"
                    else "opt_local_best"
                )
            ]
        st.radio(
            t["lbl_local_benchmark"],
            local_methods,
            key="val_local_benchmark",
            help=help_overrides.get("local_benchmark"),
            on_change=on_change,
            args=on_change_args,
            format_func=format_local_benchmark,
            **local_radio_kwargs,
        )
        st.slider(
            t["lbl_ref_radius_km"],
            10,
            MAX_DYNAMIC_RADIUS_KM,
            step=10,
            key="val_ref_radius_km",
            help=help_overrides.get("local_radius"),
            on_change=on_change,
            args=on_change_args,
        )
    elif comp_mode == "reference_station":
        _render_reference_identity(
            t,
            derives_hardware_grid4=False,
            on_change=on_change,
            on_change_args=on_change_args,
            help_overrides=help_overrides,
        )
    elif comp_mode == "hardware_ab":
        if analysis_direction == "rx":
            _render_reference_identity(
                t,
                derives_hardware_grid4=True,
                on_change=on_change,
                on_change_args=on_change_args,
                help_overrides=help_overrides,
            )
        elif analysis_direction == "tx":
            _render_tx_ab_method_selector(
                t,
                on_change=on_change,
                on_change_args=on_change_args,
                method_content=tx_ab_method_content,
                help_text=help_overrides.get("tx_ab_method"),
            )
            if st.session_state.get("val_tx_ab_method") == "sequential":
                _render_tx_ab_schedule(
                    t,
                    on_change=on_change,
                    on_change_args=on_change_args,
                )
            else:
                _render_reference_identity(
                    t,
                    derives_hardware_grid4=True,
                    on_change=on_change,
                    on_change_args=on_change_args,
                    help_overrides=help_overrides,
                )
        else:
            st.info(t["msg_select_analysis_direction_hardware"])

def render_compare_expander(t):
    """Render the Success-only choice and optional benchmark-design controls."""
    with st.expander(t["exp_comp"], expanded=st.session_state.get("config_panels_expanded", True)):
        comp_mode = st.session_state.val_comp_mode
        analysis_direction = st.session_state.get("val_analysis_direction")
        col_comp_l, col_comp_r = st.columns(
            _comparison_column_widths(t, comp_mode, analysis_direction),
            gap="large",
        )
        with col_comp_l:
            st.radio(
                t["lbl_comp_mode"],
                _benchmark_mode_options(t),
                key="val_comp_mode",
                label_visibility="collapsed",
                on_change=handle_comp_mode_change,
                format_func=lambda benchmark_mode: _format_benchmark_mode(
                    t, benchmark_mode
                ),
            )
            if st.session_state.val_comp_mode != "none":
                render_reference_correction_field(t)
        
        with col_comp_r:
            render_reference_design_fields(t)

def render_station_population_fields(
    t,
    *,
    on_change=reset_audit,
    on_change_args=(),
):
    """Render shared identity-population exclusions."""
    st.toggle(
        t.get("lbl_exclude_special", "Exclude Special Callsigns Q, 0, 1"),
        key="val_exclude_special_callsigns",
        help=t.get("tt_exclude_special", "Filter out balloon telemetry."),
        on_change=on_change,
        args=on_change_args,
    )
    st.toggle(
        t.get("lbl_filter_moving", "Exclude Moving Stations"),
        key="val_filter_moving",
        help=t.get("tt_filter_moving", ""),
        on_change=on_change,
        args=on_change_args,
    )


def render_scope_fields(
    t,
    *,
    on_change=reset_audit,
    on_change_args=(),
    use_two_column_layout=False,
):
    """Render scope controls vertically or in two equal-width columns."""
    scope_containers = (
        st.columns(2, gap="large")
        if use_two_column_layout
        else (nullcontext(), nullcontext())
    )
    with scope_containers[0]:
        st.selectbox(
            t["lbl_solar"],
            ["all", "day", "night", "greyline"],
            key="val_solar",
            on_change=on_change,
            args=on_change_args,
            format_func=lambda solar_state: t[
                {
                    "all": "opt_solar_all",
                    "day": "opt_solar_day",
                    "night": "opt_solar_night",
                    "greyline": "opt_solar_grey",
                }[solar_state]
            ],
        )
    with scope_containers[1]:
        st.selectbox(
            t["lbl_max_dist"],
            MAP_SCOPE_OPTIONS,
            key="val_max_peer_distance_km",
            help=t["hlp_max_dist"],
            on_change=on_change,
            args=on_change_args,
        )


def render_evidence_threshold_fields(
    t,
    *,
    result_type=None,
    on_change=reset_audit,
    on_change_args=(),
    use_two_column_layout=False,
):
    """Render active evidence thresholds vertically or in equal-width columns."""
    if result_type is None:
        result_type = (
            "success" if st.session_state.get("val_comp_mode") == "none" else "compare"
        )
    min_spots_label = t["lbl_min_spots"]
    min_spots_help = t["hlp_min_spots"]
    if (
        st.session_state.get("val_comp_mode") == "hardware_ab"
        and st.session_state.get("val_analysis_direction") == "tx"
        and st.session_state.get("val_tx_ab_method") == "sequential"
    ):
        min_spots_label, min_spots_help = _tx_ab_threshold_label_and_help(t)

    st.session_state.val_min_spots = min(
        max(int(st.session_state.get("val_min_spots", 1)), 1), 50
    )
    st.session_state.val_min_opportunities = min(
        max(int(st.session_state.get("val_min_opportunities", 5)), 1), 100
    )
    st.session_state.val_min_stations = min(
        max(int(st.session_state.get("val_min_stations", 1)), 1), 10
    )
    threshold_containers = (
        st.columns(2, gap="large")
        if use_two_column_layout
        else (nullcontext(), nullcontext())
    )
    with threshold_containers[0]:
        if result_type == "compare":
            st.slider(
                min_spots_label,
                1,
                50,
                key="val_min_spots",
                help=min_spots_help,
                on_change=on_change,
                args=on_change_args,
            )
        else:
            st.slider(
                t.get("lbl_min_opportunities", "Min. Confirmed H+M per Station"),
                1,
                100,
                key="val_min_opportunities",
                help=t.get(
                    "hlp_min_opportunities",
                    "Absolute success-rate views include a station only after this many confirmed H+M observations.",
                ),
                on_change=on_change,
                args=on_change_args,
            )
    with threshold_containers[1]:
        st.slider(
            t["lbl_min_stations"],
            1,
            10,
            key="val_min_stations",
            help=t["hlp_min_stations"],
            on_change=on_change,
            args=on_change_args,
        )


def render_advanced_expander(t):
    """Render shared population, scope, and active-result evidence controls."""
    with st.expander(
        t["exp_adv"],
        expanded=st.session_state.get("config_panels_expanded", True),
    ):
        col3, col4 = st.columns(2, gap="large")
        with col3:
            st.markdown(f"**{t['hdr_remote_station_filters']}**")
            render_station_population_fields(t)
            st.markdown(f"**{t['hdr_analysis_scope']}**")
            render_scope_fields(t)
        with col4:
            st.markdown(f"**{t['hdr_evidence_requirements']}**")
            render_evidence_threshold_fields(t)
