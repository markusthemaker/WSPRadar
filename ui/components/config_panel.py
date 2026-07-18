"""
Config Panel Components Module.
Contains the UI rendering functions for the main configuration expanders.
Separating this from app.py keeps the main orchestrator file clean and focused.
"""

import streamlit as st
from datetime import datetime, timedelta, timezone
from string import punctuation
from config import (
    MAX_DAYS_HISTORY,
    BAND_MAP,
    MAX_DYNAMIC_RADIUS_KM,
    MAP_SCOPE_OPTIONS,
    TX_AB_REPEAT_INTERVAL_OPTIONS,
)
from config.demo_profiles import prepare_demo_description_markdown
from ui.callbacks import (
    reset_audit, handle_analysis_direction_change, handle_comp_mode_change,
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


def _strip_text_state(key, callback=None, callback_args=(), callback_kwargs=None):
    value = st.session_state.get(key)
    if isinstance(value, str):
        st.session_state[key] = value.strip()
    if callback:
        callback(*(callback_args or ()), **(callback_kwargs or {}))

def _round_float_state(key, digits=1, callback=None, callback_args=(), callback_kwargs=None):
    value = st.session_state.get(key)
    if value is not None:
        st.session_state[key] = round(float(value), digits)
    if callback:
        callback(*(callback_args or ()), **(callback_kwargs or {}))

def text_input_no_autocomplete(*args, **kwargs):
    kwargs.setdefault("autocomplete", "off")
    key = kwargs.get("key")
    if key:
        callback = kwargs.get("on_change")
        callback_args = kwargs.pop("args", ())
        callback_kwargs = kwargs.pop("kwargs", {})
        kwargs["on_change"] = _strip_text_state
        kwargs["args"] = (key, callback, callback_args, callback_kwargs)
    return st.text_input(*args, **kwargs)

def _benchmark_mode_options(t):
    """Return Success-only first, followed by the available benchmark designs."""
    return [
        t["opt_comp_none"],
        t["opt_comp_self"],
        t["opt_comp_buddy"],
        t["opt_comp_radius"],
    ]


def _comparison_column_widths(t, comparison_mode, analysis_direction):
    """Allocate more width to comparison designs with denser controls."""
    if comparison_mode == t["opt_comp_self"] and analysis_direction == "tx":
        return [0.32, 0.68]
    if comparison_mode in {t["opt_comp_self"], t["opt_comp_buddy"]}:
        return [0.40, 0.60]
    if comparison_mode == t["opt_comp_radius"]:
        return [0.48, 0.52]
    return [0.62, 0.38]


def _tx_ab_threshold_label_and_help(t):
    """Return evidence-threshold wording for scheduled TX A/B pairs."""
    return (
        t.get("cfg_min_joint_pairs", "Min. Joint Pairs"),
        t.get(
            "hlp_min_joint_pairs",
            "Sequential TX A/B requires joint scheduled pairs.",
        ),
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


def _render_tx_ab_schedule(t):
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
            )
        with swap_column:
            st.button(
                "⇄",
                key="swap_tx_ab_schedule_starts",
                help=t.get("hlp_tx_ab_swap", "Swap Target and Reference starts"),
                disabled=st.session_state.is_demo_mode,
                on_click=swap_tx_ab_starts,
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

def _render_analysis_direction_selector(t):
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
        on_change=handle_analysis_direction_change,
    )

def render_core_expander(t):
    """Render analysis direction, target identity, band, and time controls."""
    with st.expander(t["exp_core"], expanded=st.session_state.get("config_panels_expanded", True)):
        _render_analysis_direction_selector(t)

        # Build widgets column-first so keyboard navigation moves down the left
        # column before continuing at the top of the right column.
        core_left, core_right = st.columns([0.5, 0.5], gap="large")
        with core_left:
            direction = st.session_state.get("val_analysis_direction")
            callsign_label = t.get(
                f"lbl_callsign_{direction}",
                t["lbl_callsign"],
            )
            text_input_no_autocomplete(callsign_label, key="val_callsign", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
            text_input_no_autocomplete(t["lbl_qth"], key="val_qth", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
            st.selectbox(t["lbl_band"], list(BAND_MAP.keys()), key="val_band", disabled=st.session_state.is_demo_mode, on_change=reset_audit)

        with core_right:
            st.radio(t["lbl_time_mode"], [t["opt_last_x"], t["opt_custom"]], key="val_time_mode", horizontal=True, disabled=st.session_state.is_demo_mode, on_change=reset_audit)

            if st.session_state.val_time_mode == t["opt_last_x"]:
                st.slider(t["lbl_hours"], 1, 168, key="val_hours", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
            else:
                today_utc = datetime.now(timezone.utc).date()

                date_start, date_end = st.columns(2, gap="large", vertical_alignment="bottom")
                with date_start:
                    st.date_input(t["lbl_start_d"], key="val_start_d", min_value=datetime(2008, 1, 1, tzinfo=timezone.utc).date(), max_value=today_utc, disabled=st.session_state.is_demo_mode, on_change=reset_audit, format="DD-MM-YYYY")
                max_allowed_end = min(st.session_state.val_start_d + timedelta(days=MAX_DAYS_HISTORY), today_utc)
                min_allowed_end = st.session_state.val_start_d
                
                # Defensive check inside the render loop
                if st.session_state.val_end_d > max_allowed_end: st.session_state.val_end_d = max_allowed_end
                elif st.session_state.val_end_d < min_allowed_end: st.session_state.val_end_d = min_allowed_end

                with date_end:
                    st.date_input(t["lbl_end_d"], key="val_end_d", min_value=min_allowed_end, max_value=max_allowed_end, disabled=st.session_state.is_demo_mode, on_change=reset_audit, format="DD-MM-YYYY")

                time_start, time_end = st.columns(2, gap="large", vertical_alignment="bottom")
                with time_start:
                    st.time_input(t["lbl_start_t"], key="val_start_t", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
                with time_end:
                    st.time_input(t["lbl_end_t"], key="val_end_t", disabled=st.session_state.is_demo_mode, on_change=reset_audit)

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
            st.radio(t["lbl_comp_mode"], _benchmark_mode_options(t), key="val_comp_mode", on_change=handle_comp_mode_change)
            if st.session_state.val_comp_mode != t["opt_comp_none"]:
                st.number_input(
                    t["lbl_benchmark_offset_db"],
                    min_value=-99.9,
                    max_value=99.9,
                    step=0.1,
                    format="%.1f",
                    key="val_benchmark_offset_db",
                    help=t["hlp_benchmark_offset_db"],
                    on_change=_round_float_state,
                    args=("val_benchmark_offset_db", 1, reset_audit, (), {})
                )
        
        with col_comp_r:
            callsign = st.session_state.val_callsign.strip().upper()
            
            if comp_mode == t["opt_comp_radius"]:
                st.radio(
                    t["lbl_local_benchmark"],
                    [t["opt_local_median"], t["opt_local_best"]],
                    key="val_local_benchmark",
                    on_change=reset_audit
                )
                st.slider(t["lbl_ref_radius_km"], 10, MAX_DYNAMIC_RADIUS_KM, step=10, key="val_ref_radius_km", on_change=reset_audit)
            elif comp_mode == t["opt_comp_buddy"]:
                text_input_no_autocomplete(t["lbl_ref_call"], key="val_ref_callsign", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
                
                # Validation error
                if st.session_state.val_ref_callsign.strip().upper() == callsign and callsign != "":
                    st.error(t["err_self_test"])
                    
            elif comp_mode == t["opt_comp_self"]:
                if analysis_direction == "rx":
                    cs1, cs2 = st.columns(2, gap="large")
                    with cs1: text_input_no_autocomplete("Setup A Callsign", value=callsign, disabled=True)
                    with cs2: text_input_no_autocomplete("Setup B Callsign", key="val_self_call_b", placeholder="e.g. Callsign/P", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
                    
                    self_call_b = st.session_state.val_self_call_b.strip().upper()
                    if len(self_call_b) > 0 and self_call_b == callsign:
                        st.error("Setup B callsign must be different from Setup A (e.g., use a /P suffix).")
                elif analysis_direction == "tx":
                    _render_tx_ab_schedule(t)
                else:
                    st.info(t["msg_select_analysis_direction_hardware"])

def render_advanced_expander(t):
    """Renders the third expander: Advanced scientific configurations, filters, and exclusions."""
    with st.expander(t["exp_adv"], expanded=st.session_state.get("config_panels_expanded", True)):
        col3, col4 = st.columns(2, gap="large")

        with col3:
            st.toggle(t.get("lbl_exclude_special", "Exclude Special Callsigns Q, 0, 1"), key="val_exclude_special_callsigns", help=t.get("tt_exclude_special", "Filter out balloon telemetry."), on_change=reset_audit)
            st.toggle(t.get("lbl_filter_moving", "Exclude Moving Stations"), key="val_filter_moving", help=t.get("tt_filter_moving", ""), on_change=reset_audit)
            st.selectbox(t["lbl_solar"], [t["opt_solar_all"], t["opt_solar_day"], t["opt_solar_night"], t["opt_solar_grey"]], key="val_solar", on_change=reset_audit)
            st.selectbox(t["lbl_max_dist"], MAP_SCOPE_OPTIONS, key="val_max_dist", help=t["hlp_max_dist"], on_change=reset_audit)

        with col4:
            min_spots_label = t["lbl_min_spots"]
            min_spots_help = t["hlp_min_spots"]
            if st.session_state.val_comp_mode == t["opt_comp_self"] and st.session_state.get("val_analysis_direction") == "tx":
                min_spots_label, min_spots_help = (
                    _tx_ab_threshold_label_and_help(t)
                )

            st.session_state.val_min_spots = min(max(int(st.session_state.get("val_min_spots", 1)), 1), 50)
            st.session_state.val_min_opportunities = min(max(int(st.session_state.get("val_min_opportunities", 5)), 1), 100)
            st.session_state.val_min_stations = min(max(int(st.session_state.get("val_min_stations", 1)), 1), 10)
            if st.session_state.val_comp_mode != t["opt_comp_none"]:
                st.slider(min_spots_label, 1, 50, key="val_min_spots", help=min_spots_help, on_change=reset_audit)
            st.slider(
                t.get("lbl_min_opportunities", "Min. Confirmed H+M per Station"),
                1,
                100,
                key="val_min_opportunities",
                help=t.get(
                    "hlp_min_opportunities",
                    "Absolute success-rate views include a station only after this many confirmed H+M observations.",
                ),
                on_change=reset_audit,
            )
            st.slider(t["lbl_min_stations"], 1, 10, key="val_min_stations", help=t["hlp_min_stations"], on_change=reset_audit)
