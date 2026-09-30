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
)
from ui.input_validation_state import get_field_error
from config.demo_profiles import prepare_demo_description_markdown
from config.delta_snr_outlier import (
    DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD,
    DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD,
)
from core.input_validation import (
    is_valid_callsign,
    is_valid_grid4,
    is_valid_locator,
    normalize_ascii_upper,
)
from core.time_utils import UtcWindowValidationError
from ui.callbacks import (
    reset_audit,
    reset_experiment_definition,
    handle_analysis_direction_change,
    handle_classic_benchmark_design_change,
    handle_classic_question_change,
    handle_delta_snr_outlier_reporting_change,
    handle_population_exclusion_change,
    handle_reference_correction_context_change,
    handle_start_date_change,
    handle_time_window_change,
    reset_delta_snr_outlier_detector_defaults,
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
    state_key=None,
):
    """Show one localized point-of-entry error for a malformed identity."""
    if state_key and _render_field_error(state_key):
        return False
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
    """Return the two visible Classic Benchmark designs in display order."""
    return [
        "reference_station",
        "local_neighborhood",
    ]


def _format_benchmark_mode(t, benchmark_mode):
    """Localize one stable benchmark-design token for display."""
    translation_keys = {
        "reference_station": "opt_benchmark_reference_station",
        "local_neighborhood": "opt_benchmark_local_neighborhood",
    }
    return t[translation_keys[benchmark_mode]]


def _select_reference_design(widget_key, benchmark_mode, on_change):
    """Apply a new Reference choice through its existing editor callback."""
    if benchmark_mode not in _benchmark_mode_options(None):
        raise ValueError(f"Unsupported Reference design {benchmark_mode!r}.")
    if st.session_state.get(widget_key) == benchmark_mode:
        return
    st.session_state[widget_key] = benchmark_mode
    on_change()


def render_reference_design_selector(t, *, widget_key, on_change, descriptions=None):
    """Render single-selection Reference choices with independent native help."""
    descriptions = descriptions or {}
    help_keys = {
        "reference_station": "hlp_benchmark_reference_station",
        "local_neighborhood": "hlp_benchmark_local_neighborhood",
    }
    with st.container(key=widget_key):
        for benchmark_mode in _benchmark_mode_options(t):
            choice_label = _format_benchmark_mode(t, benchmark_mode)
            is_selected = st.session_state.get(widget_key) == benchmark_mode
            selection_column, help_column = st.columns(
                [0.9, 0.1], gap="small", vertical_alignment="center"
            )
            with selection_column:
                st.button(
                    (
                        t["fmt_reference_choice_selected"].format(choice=choice_label)
                        if is_selected else choice_label
                    ),
                    key=f"{widget_key}_{benchmark_mode}",
                    type="primary" if is_selected else "secondary",
                    icon=(
                        ":material/radio_button_checked:"
                        if is_selected else ":material/radio_button_unchecked:"
                    ),
                    on_click=_select_reference_design,
                    args=(widget_key, benchmark_mode, on_change),
                    width="stretch",
                )
            with help_column:
                with st.popover(
                    "?",
                    key=f"{widget_key}_{benchmark_mode}_help",
                    type="tertiary",
                    help=t["fmt_reference_choice_help"].format(choice=choice_label),
                    on_change="ignore",
                ):
                    st.markdown(f"**{choice_label}**")
                    st.markdown(t[help_keys[benchmark_mode]])
            if benchmark_mode in descriptions:
                st.caption(descriptions[benchmark_mode])


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


def _render_reference_identity(
    t, *, on_change=reset_experiment_definition, on_change_args=(),
):
    """Render the Reference callsign without a duplicate location display."""
    text_input_no_autocomplete(
        t["lbl_reference_callsign"], key="val_ref_callsign",
        placeholder=t["ph_reference_callsign"],
        help=t["hlp_reference_callsign"],
        max_chars=15, normalize_uppercase=True, on_change=on_change,
        args=on_change_args,
    )
    reference_callsign = normalize_ascii_upper(st.session_state.get("val_ref_callsign", ""))
    _render_identity_format_error(
        t, reference_callsign, identity_kind="callsign",
        message_key="err_reference_callsign_format", state_key="val_ref_callsign",
    )
    if reference_callsign and reference_callsign == normalize_ascii_upper(st.session_state.get("val_callsign", "")) and not get_field_error(st.session_state, "val_ref_callsign"):
        st.error(t["err_reference_callsign_same"])
    _render_field_error("val_ref_qth")


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
    on_change=reset_experiment_definition,
    on_change_args=(),
    correction_context_on_change=None,
    correction_context_on_change_args=(),
):
    """Render shared Target identity, band, and time controls.

    Both input editors use the same widget keys, normalization and scientific
    callbacks and concise field help. Identity/QTH/band changes may use a
    separate callback because they invalidate an established pair correction,
    while changing only the time window does not.
    """
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
            placeholder=t["ph_target_callsign"],
            help=t["hlp_callsign_entry"],
            max_chars=15,
            normalize_uppercase=True,
            on_change=correction_context_on_change,
            args=correction_context_on_change_args,
        )
        _render_identity_format_error(
            t,
            st.session_state.get("val_callsign", ""),
            identity_kind="callsign", state_key="val_callsign",
        )
        text_input_no_autocomplete(
            t["lbl_qth"],
            key="val_qth",
            help=t["hlp_target_qth"],
            max_chars=6,
            normalize_uppercase=True,
            on_change=correction_context_on_change,
            args=correction_context_on_change_args,
        )
        _render_identity_format_error(
            t,
            st.session_state.get("val_qth", ""),
            identity_kind="qth", state_key="val_qth",
        )
        st.selectbox(
            t["lbl_band"],
            list(BAND_MAP.keys()),
            key="val_band",
            help=t["hlp_band"],
            on_change=correction_context_on_change,
            args=correction_context_on_change_args,
        )
        _render_field_error('val_band')

    with core_right:
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
                help=t["hlp_time_window"],
                min_value=datetime(2008, 1, 1, tzinfo=timezone.utc).date(),
                max_value=today_utc,
                on_change=handle_start_date_change,
                args=(on_change, on_change_args),
                format="DD-MM-YYYY",
            )
            _render_field_error('val_start_d')
        with date_end:
            st.date_input(
                t["lbl_end_d"],
                key="val_end_d",
                help=t["hlp_time_window"],
                min_value=minimum_end_date,
                max_value=maximum_end_date,
                on_change=handle_time_window_change,
                args=(on_change, on_change_args),
                format="DD-MM-YYYY",
            )
            _render_field_error('val_end_d')

        time_start, time_end = st.columns(
            2, gap="large", vertical_alignment="bottom"
        )
        with time_start:
            st.time_input(
                t["lbl_start_t"],
                key="val_start_t",
                step=timedelta(minutes=1),
                on_change=handle_time_window_change,
                args=(on_change, on_change_args),
            )
            _render_field_error('val_start_t')
        with time_end:
            st.time_input(
                t["lbl_end_t"],
                key="val_end_t",
                step=timedelta(minutes=1),
                on_change=handle_time_window_change,
                args=(on_change, on_change_args),
            )
            _render_field_error('val_end_t')

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
        _render_field_error("classic_question")


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
    on_change=reset_experiment_definition,
    on_change_args=(),
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
        help=t["hlp_benchmark_offset_db"],
        on_change=_normalize_reference_correction_state,
        args=(
            on_change,
            on_change_args,
            {},
        ),
    )
    _render_field_error(_REFERENCE_CORRECTION_TEXT_KEY)
    if st.session_state.pop(_REFERENCE_CORRECTION_ERROR_KEY, False):
        st.error(t["err_benchmark_offset_db"])


def render_reference_design_fields(
    t,
    *,
    on_change=handle_reference_correction_context_change,
    on_change_args=(),
):
    """Render Reference fields with shared field-specific help in both editors."""
    comp_mode = st.session_state.get("val_comp_mode")
    if comp_mode == "local_neighborhood":
        if st.session_state.get("val_local_benchmark", "local_median") != "local_median":
            st.error(t["err_local_benchmark"])
        st.slider(
            t["lbl_ref_radius_km"],
            10,
            MAX_DYNAMIC_RADIUS_KM,
            step=10,
            key="val_ref_radius_km",
            help=t["hlp_reference_radius"],
            on_change=on_change,
            args=on_change_args,
        )
        _render_field_error('val_ref_radius_km')
    elif comp_mode == "reference_station":
        _render_reference_identity(
            t,
            on_change=on_change,
            on_change_args=on_change_args,
        )


def _classic_reference_design_help(t):
    """Explain both Reference choices independently of the current selection."""
    help_keys = {
        "reference_station": "hlp_benchmark_reference_station",
        "local_neighborhood": "hlp_benchmark_local_neighborhood",
    }
    return "\n\n".join(
        f"**{_format_benchmark_mode(t, mode)}**\n\n{t[help_keys[mode]]}"
        for mode in _benchmark_mode_options(t)
    )


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
                label_visibility="visible",
                help=_classic_reference_design_help(t),
                on_change=handle_classic_benchmark_design_change,
                format_func=lambda benchmark_mode: _format_benchmark_mode(
                    t, benchmark_mode
                ),
                width="stretch",
            )
            _render_field_error("val_comp_mode", widget_key=CLASSIC_BENCHMARK_DESIGN_WIDGET_KEY)
        
        with col_comp_r:
            render_reference_design_fields(t)
            if comp_mode != "none":
                render_reference_correction_field(t)

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
            help=t["hlp_solar"],
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
        _render_field_error('val_max_peer_distance_km')


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
            _render_field_error('val_min_spots')
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
            _render_field_error('val_min_opportunities')
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
        _render_field_error('val_min_stations')


def render_delta_snr_outlier_reporting_field(
    t,
    *,
    on_change=None,
    on_change_args=(),
):
    """Render the opt-in report and its three shared qualification gates."""
    owner_on_change = reset_audit if on_change is None else on_change
    toggle_kwargs = {
        "key": "val_report_delta_snr_outlier_candidates",
        "help": t["tt_report_delta_snr_outlier_candidates"],
        "on_change": handle_delta_snr_outlier_reporting_change,
        "args": (owner_on_change, on_change_args),
    }
    st.toggle(
        t["lbl_report_delta_snr_outlier_candidates"],
        **toggle_kwargs,
    )
    if not st.session_state.get(
        "val_report_delta_snr_outlier_candidates",
        False,
    ):
        return

    input_change_kwargs = {
        "on_change": owner_on_change,
        "args": on_change_args,
    }
    st.number_input(
        t["lbl_delta_snr_outlier_minimum_departure_db"],
        min_value=DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD,
        max_value=DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD,
        step=0.1,
        key="val_delta_snr_outlier_minimum_departure_db",
        help=t["tt_delta_snr_outlier_minimum_departure_db"],
        **input_change_kwargs,
    )
    _render_field_error('val_delta_snr_outlier_minimum_departure_db')
    st.number_input(
        t["lbl_delta_snr_outlier_minimum_robust_z"],
        min_value=DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD,
        max_value=DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD,
        step=0.1,
        key="val_delta_snr_outlier_minimum_robust_z",
        help=t["tt_delta_snr_outlier_minimum_robust_z"],
        **input_change_kwargs,
    )
    _render_field_error('val_delta_snr_outlier_minimum_robust_z')
    st.number_input(
        t["lbl_delta_snr_outlier_maximum_baseline_difference_db"],
        min_value=DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD,
        max_value=DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD,
        step=0.1,
        key="val_delta_snr_outlier_maximum_baseline_difference_db",
        help=t["tt_delta_snr_outlier_maximum_baseline_difference_db"],
        **input_change_kwargs,
    )
    _render_field_error('val_delta_snr_outlier_maximum_baseline_difference_db')
    st.button(
        t["btn_reset_delta_snr_outlier_detector_defaults"],
        key="reset_delta_snr_outlier_detector_defaults",
        on_click=reset_delta_snr_outlier_detector_defaults,
        args=(owner_on_change, on_change_args),
    )


def render_advanced_expander(t, *, result_type=None, step_number=None):
    """Render shared population, scope, and active-result evidence controls."""
    with st.expander(
        _numbered_panel_heading(t, "exp_adv", step_number),
        expanded=st.session_state.get("config_panels_expanded", True),
    ):
        col3, col4 = st.columns(2, gap="large")
        with col3:
            st.markdown(f"**{t['hdr_analysis_scope']}**")
            render_scope_fields(t)
            st.markdown(f"**{t['hdr_remote_station_filters']}**")
            render_station_population_fields(t)
        with col4:
            st.markdown(f"**{t['hdr_evidence_requirements']}**")
            render_evidence_threshold_fields(t, result_type=result_type)
            if result_type == "benchmark":
                render_delta_snr_outlier_reporting_field(t)


def _render_field_error(state_key, *, widget_key=None):
    """Render accessible text and a scoped visual error for one active field."""
    message = get_field_error(st.session_state, state_key)
    if not message:
        return False
    widget_key = widget_key or state_key
    if re.fullmatch(r"[A-Za-z0-9_]+", widget_key):
        st.markdown(
            f"<style>.st-key-{widget_key}{{outline:2px solid #ff4b4b;outline-offset:1px;}}</style>",
            unsafe_allow_html=True,
        )
    st.error(message)
    return True
