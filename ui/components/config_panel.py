"""
Config Panel Components Module.
Contains the UI rendering functions for the main configuration expanders.
Separating this from app.py keeps the main orchestrator file clean and focused.
"""

from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
import math
import re
from string import punctuation

import streamlit as st

from config import (
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
from core.time_utils import UtcWindowValidationError
from ui.callbacks import (
    reset_audit, handle_analysis_direction_change,
    handle_classic_benchmark_design_change,
    handle_classic_question_change,
    handle_population_exclusion_change,
    handle_reference_correction_context_change,
    handle_start_date_change,
    handle_time_window_change,
    handle_tx_ab_reference_start_change, handle_tx_ab_repeat_interval_change,
    handle_tx_ab_target_start_change, swap_tx_ab_starts,
)
from ui.analysis_question_state import ANALYSIS_QUESTION_CHOICES
from ui.classic_input_state import (
    CLASSIC_BENCHMARK_DESIGN_WIDGET_KEY,
    CLASSIC_QUESTION_KEY,
)
from ui.population_exclusion_state import (
    load_population_exclusion_widget_values,
    population_exclusion_widget_key,
)
from ui.time_window import (
    end_date_entry_bounds,
    time_window_validation_message_key,
    utc_window_from_state,
)


_PROFILE_TITLE_MARKDOWN_ESCAPES = str.maketrans(
    {character: f"\\{character}" for character in punctuation}
)
_REFERENCE_CORRECTION_TEXT_KEY = "_val_benchmark_offset_db_text"
_REFERENCE_CORRECTION_SYNCED_VALUE_KEY = (
    "_val_benchmark_offset_db_text_synced_value"
)
_REFERENCE_CORRECTION_ERROR_KEY = "_val_benchmark_offset_db_text_error"
_REFERENCE_CORRECTION_DECIMAL_PATTERN = re.compile(
    r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$"
)
_REFERENCE_CORRECTION_MIN_DB = -99.9
_REFERENCE_CORRECTION_MAX_DB = 99.9


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

    with st.expander(t["exp_metadata"], expanded=True):
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

def _normalize_reference_correction_state(
    callback=None,
    callback_args=(),
    callback_kwargs=None,
):
    """Parse decimal-point text and preserve the correction's semantic mode."""
    correction_text = st.session_state.get(_REFERENCE_CORRECTION_TEXT_KEY)
    if correction_text is None:
        correction_db = round(
            float(st.session_state.get("val_benchmark_offset_db", 0.0)),
            1,
        )
    else:
        normalized_text = str(correction_text).strip()
        if not normalized_text:
            correction_db = 0.0
        elif _REFERENCE_CORRECTION_DECIMAL_PATTERN.fullmatch(normalized_text):
            correction_db = round(float(normalized_text), 1)
            if (
                not math.isfinite(correction_db)
                or correction_db < _REFERENCE_CORRECTION_MIN_DB
                or correction_db > _REFERENCE_CORRECTION_MAX_DB
            ):
                correction_db = None
        else:
            correction_db = None

        if correction_db is None:
            retained_correction_db = round(
                float(st.session_state.get("val_benchmark_offset_db", 0.0)),
                1,
            )
            st.session_state[_REFERENCE_CORRECTION_TEXT_KEY] = (
                ""
                if retained_correction_db == 0.0
                else f"{retained_correction_db:.1f}"
            )
            st.session_state[_REFERENCE_CORRECTION_SYNCED_VALUE_KEY] = (
                retained_correction_db
            )
            st.session_state[_REFERENCE_CORRECTION_ERROR_KEY] = True
            return

        st.session_state[_REFERENCE_CORRECTION_TEXT_KEY] = (
            "" if correction_db == 0.0 else f"{correction_db:.1f}"
        )
        st.session_state[_REFERENCE_CORRECTION_SYNCED_VALUE_KEY] = correction_db
        st.session_state.pop(_REFERENCE_CORRECTION_ERROR_KEY, None)

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
    """Return the three visible Classic Benchmark designs in display order."""
    return [
        "hardware_ab",
        "reference_station",
        "local_neighborhood",
    ]


def _format_benchmark_mode(t, benchmark_mode):
    """Localize one stable benchmark-design token for display."""
    translation_keys = {
        "hardware_ab": "opt_benchmark_hardware_ab",
        "reference_station": "opt_benchmark_reference_station",
        "local_neighborhood": "opt_benchmark_local_neighborhood",
    }
    return t[translation_keys[benchmark_mode]]


def _classic_question_options():
    """Return the four stable direction/result questions in display order."""
    return ANALYSIS_QUESTION_CHOICES


def _format_classic_question(t, question):
    """Localize one stable four-way Classic question token for display."""
    return t[f"opt_question_{question}"]


def _classic_question_captions(t):
    """Return localized explanations aligned with the four question choices."""
    return tuple(
        t[f"desc_question_{question}"]
        for question in _classic_question_options()
    )


def _numbered_panel_heading(t, translation_key, step_number):
    """Prefix one localized Classic panel heading with its visible step."""
    heading = t[translation_key]
    return f"{step_number} · {heading}" if step_number is not None else heading


def _comparison_column_widths(t, comparison_mode, analysis_direction):
    """Return the consistent half-width split used by configuration panels."""
    return [0.5, 0.5]


def _tx_ab_threshold_label_and_help(t):
    """Return evidence-threshold wording for scheduled TX A/B pairs."""
    return (
        t["cfg_min_joint_pairs"],
        t["hlp_min_joint_pairs"],
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
            t["lbl_target_callsign"],
            value=target_callsign,
            disabled=True,
        )
    with reference_callsign_column:
        text_input_no_autocomplete(
            t["lbl_reference_callsign"],
            key="val_ref_callsign",
            placeholder=t["ph_reference_callsign"],
            help=help_overrides.get(
                "reference_callsign",
                t["hlp_callsign_entry"],
            ),
            max_chars=15,
            normalize_uppercase=True,
            on_change=on_change,
            args=on_change_args,
        )

    target_qth_column, reference_qth_column = st.columns(2, gap="large")
    with target_qth_column:
        text_input_no_autocomplete(
            (
                t["lbl_target_grid4"]
                if derives_hardware_grid4
                else t["lbl_target_qth"]
            ),
            value=hardware_grid4 if derives_hardware_grid4 else target_qth,
            disabled=True,
        )
    with reference_qth_column:
        if derives_hardware_grid4:
            text_input_no_autocomplete(
                t["lbl_reference_grid4"],
                value=hardware_grid4,
                disabled=True,
            )
        else:
            reference_qth_help = help_overrides.get("reference_qth")
            text_input_no_autocomplete(
                t["lbl_reference_grid4"],
                key="val_ref_qth",
                placeholder=t["ph_reference_qth"],
                max_chars=4,
                normalize_uppercase=True,
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
        st.error(t["err_reference_callsign_same"])


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
            t["lbl_tx_ab_method"],
            methods,
            key="val_tx_ab_method",
            format_func=lambda method: method_content[method]["label"],
            captions=tuple(
                method_content[method]["description"] for method in methods
            ),
            help=help_text,
            width="stretch",
            on_change=on_change,
            args=on_change_args,
        )
        return

    st.segmented_control(
        t["lbl_tx_ab_method"],
        methods,
        selection_mode="single",
        required=True,
        key="val_tx_ab_method",
        format_func=lambda method: t[f"opt_tx_ab_{method}"],
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
        st.markdown(f"**{t['lbl_tx_ab_schedule']}**")
        st.selectbox(
            t["lbl_tx_ab_repeat_interval"],
            TX_AB_REPEAT_INTERVAL_OPTIONS,
            key="val_tx_ab_repeat_interval_minutes",
            format_func=lambda minutes: f"{minutes} min",
            help=t["hlp_tx_ab_repeat_interval"],
            on_change=handle_tx_ab_repeat_interval_change,
            args=(on_change, on_change_args),
        )
        st.caption(t["txt_tx_ab_shared_interval"])

        target_column, swap_column, reference_column = st.columns(
            [0.46, 0.08, 0.46],
            gap="small",
            vertical_alignment="bottom",
        )
        with target_column:
            st.selectbox(
                t["lbl_tx_ab_target_start"],
                target_options,
                key="val_tx_ab_target_start_minute",
                format_func=_format_utc_minute,
                help=t["hlp_tx_ab_start"],
                on_change=handle_tx_ab_target_start_change,
                args=(on_change, on_change_args),
            )
        with swap_column:
            st.button(
                "⇄",
                key="swap_tx_ab_schedule_starts",
                help=t["hlp_tx_ab_swap"],
                on_click=swap_tx_ab_starts,
                args=(on_change, on_change_args),
                width="stretch",
            )
        with reference_column:
            st.selectbox(
                t["lbl_tx_ab_reference_start"],
                reference_options,
                key="val_tx_ab_reference_start_minute",
                format_func=_format_utc_minute,
                help=t["hlp_tx_ab_start"],
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
            f"**{t['txt_target']}:** `{target_preview}`  \n"
            f"**{t['txt_reference']}:** `{reference_preview}`"
        )
        transmissions_per_hour = 60 // repeat_interval
        st.success(
            t["txt_tx_ab_schedule_valid"].format(
                separation=separation_minutes,
                transmissions=transmissions_per_hour,
            ),
            icon=":material/check_circle:",
        )
        if repeat_interval in {4, 6}:
            st.warning(t["warn_tx_ab_high_duty"], icon=":material/warning:")

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
        callsign_label = (
            t[f"lbl_callsign_{direction}"]
            if direction in {"rx", "tx"}
            else t["lbl_callsign"]
        )
        text_input_no_autocomplete(
            callsign_label,
            key="val_callsign",
            help=help_overrides.get(
                "callsign",
                t["hlp_callsign_entry"],
            ),
            max_chars=15,
            normalize_uppercase=True,
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
            on_change=correction_context_on_change,
            args=correction_context_on_change_args,
        )

    with core_right:
        st.markdown(
            f"**{t['lbl_time_window']}**",
            help=help_overrides.get("time"),
        )
        current_utc = datetime.now(timezone.utc)
        today_utc = current_utc.date()
        minimum_end_date, maximum_end_date = end_date_entry_bounds(
            st.session_state,
            current_utc=current_utc,
        )

        date_start, date_end = st.columns(
            2, gap="large", vertical_alignment="bottom"
        )
        with date_start:
            st.date_input(
                t["lbl_start_d"],
                key="val_start_d",
                min_value=datetime(2008, 1, 1, tzinfo=timezone.utc).date(),
                max_value=today_utc,
                on_change=handle_start_date_change,
                args=(on_change, on_change_args),
                format="DD-MM-YYYY",
            )
        with date_end:
            st.date_input(
                t["lbl_end_d"],
                key="val_end_d",
                min_value=minimum_end_date,
                max_value=maximum_end_date,
                on_change=handle_time_window_change,
                args=(on_change, on_change_args),
                format="DD-MM-YYYY",
            )

        time_start, time_end = st.columns(
            2, gap="large", vertical_alignment="bottom"
        )
        with time_start:
            st.time_input(
                t["lbl_start_t"],
                key="val_start_t",
                step=timedelta(minutes=15),
                on_change=handle_time_window_change,
                args=(on_change, on_change_args),
            )
        with time_end:
            st.time_input(
                t["lbl_end_t"],
                key="val_end_t",
                step=timedelta(minutes=15),
                on_change=handle_time_window_change,
                args=(on_change, on_change_args),
            )

        try:
            utc_window_from_state(st.session_state, current_utc=current_utc)
        except UtcWindowValidationError as error:
            st.error(t[time_window_validation_message_key(error)])


def render_classic_question_expander(t, *, step_number=None):
    """Render the required four-way RX/TX Performance/Benchmark question."""
    with st.expander(
        _numbered_panel_heading(t, "exp_question", step_number),
        expanded=st.session_state.get("config_panels_expanded", True),
    ):
        st.markdown(t["txt_question_intro"])
        st.radio(
            t["lbl_question"],
            _classic_question_options(),
            key=CLASSIC_QUESTION_KEY,
            index=None,
            captions=_classic_question_captions(t),
            label_visibility="collapsed",
            on_change=handle_classic_question_change,
            format_func=lambda question: _format_classic_question(t, question),
            width="stretch",
        )


def render_core_expander(t, *, step_number=None):
    """Render Target identity, band, and absolute UTC-window controls."""
    with st.expander(
        _numbered_panel_heading(t, "exp_core", step_number),
        expanded=st.session_state.get("config_panels_expanded", True),
    ):
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
    correction_db = round(
        float(st.session_state.get("val_benchmark_offset_db", 0.0)),
        1,
    )
    synced_correction_db = st.session_state.get(
        _REFERENCE_CORRECTION_SYNCED_VALUE_KEY
    )
    if (
        _REFERENCE_CORRECTION_TEXT_KEY not in st.session_state
        or synced_correction_db != correction_db
    ):
        st.session_state[_REFERENCE_CORRECTION_TEXT_KEY] = (
            "" if correction_db == 0.0 else f"{correction_db:.1f}"
        )
        st.session_state[_REFERENCE_CORRECTION_SYNCED_VALUE_KEY] = correction_db
        st.session_state.pop(_REFERENCE_CORRECTION_ERROR_KEY, None)

    st.text_input(
        t["lbl_benchmark_offset_db"],
        key=_REFERENCE_CORRECTION_TEXT_KEY,
        placeholder="0.0",
        autocomplete="off",
        help=help_text or t["hlp_benchmark_offset_db"],
        on_change=_normalize_reference_correction_state,
        args=(
            on_change,
            on_change_args,
            {},
        ),
    )
    if st.session_state.pop(_REFERENCE_CORRECTION_ERROR_KEY, False):
        st.error(t["err_benchmark_offset_db"])


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

def render_benchmark_expander(t, *, step_number=None):
    """Render the conditional Classic Benchmark-design controls."""
    with st.expander(
        _numbered_panel_heading(t, "exp_comp", step_number),
        expanded=st.session_state.get("config_panels_expanded", True),
    ):
        comp_mode = st.session_state.val_comp_mode
        analysis_direction = st.session_state.get("val_analysis_direction")
        benchmark_modes = _benchmark_mode_options(t)
        st.session_state[CLASSIC_BENCHMARK_DESIGN_WIDGET_KEY] = (
            comp_mode if comp_mode in benchmark_modes else None
        )
        col_comp_l, col_comp_r = st.columns(
            _comparison_column_widths(t, comp_mode, analysis_direction),
            gap="large",
        )
        with col_comp_l:
            st.radio(
                t["lbl_comp_mode"],
                benchmark_modes,
                key=CLASSIC_BENCHMARK_DESIGN_WIDGET_KEY,
                index=None,
                label_visibility="collapsed",
                on_change=handle_classic_benchmark_design_change,
                format_func=lambda benchmark_mode: _format_benchmark_mode(
                    t, benchmark_mode
                ),
                width="stretch",
            )
            if comp_mode != "none":
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
    load_population_exclusion_widget_values(st.session_state)
    st.toggle(
        t["lbl_exclude_special"],
        key=population_exclusion_widget_key(
            "val_exclude_special_callsigns"
        ),
        help=t["tt_exclude_special"],
        on_change=handle_population_exclusion_change,
        args=(
            "val_exclude_special_callsigns",
            on_change,
            on_change_args,
        ),
    )
    st.toggle(
        t["lbl_filter_moving"],
        key=population_exclusion_widget_key("val_filter_moving"),
        help=t["tt_filter_moving"],
        on_change=handle_population_exclusion_change,
        args=(
            "val_filter_moving",
            on_change,
            on_change_args,
        ),
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
    """Render active thresholds with result- and direction-specific guidance."""
    if result_type is None:
        result_type = (
            "performance"
            if st.session_state.get("val_comp_mode") == "none"
            else "benchmark"
        )
    elif result_type == "success":
        result_type = "performance"
    elif result_type == "compare":
        result_type = "benchmark"
    if result_type not in {"performance", "benchmark"}:
        raise ValueError(f"Unsupported result type {result_type!r}.")
    analysis_direction = (
        "tx"
        if st.session_state.get("val_analysis_direction", "rx") == "tx"
        else "rx"
    )
    if result_type == "performance":
        minimum_opportunities_help = t[
            f"hlp_min_opportunities_{analysis_direction}"
        ]
        minimum_stations_help = t[
            f"hlp_min_stations_success_{analysis_direction}"
        ]
    else:
        minimum_opportunities_help = None
        minimum_stations_help = t["hlp_min_stations_compare"]

    min_spots_label = t["lbl_min_spots"]
    min_spots_help = t["hlp_min_spots"]
    if (
        result_type == "benchmark"
        and st.session_state.get("val_comp_mode") == "hardware_ab"
        and analysis_direction == "tx"
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
        if result_type == "benchmark":
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
                t["lbl_min_opportunities"],
                1,
                100,
                key="val_min_opportunities",
                help=minimum_opportunities_help,
                on_change=on_change,
                args=on_change_args,
            )
    with threshold_containers[1]:
        st.slider(
            t["lbl_min_stations"],
            1,
            10,
            key="val_min_stations",
            help=minimum_stations_help,
            on_change=on_change,
            args=on_change_args,
        )


def render_advanced_expander(t, *, result_type=None, step_number=None):
    """Render shared population, scope, and active-result evidence controls."""
    with st.expander(
        _numbered_panel_heading(t, "exp_adv", step_number),
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
            render_evidence_threshold_fields(t, result_type=result_type)
