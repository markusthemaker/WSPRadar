"""
Callbacks Module for WSPRadar.
Contains all event handlers triggered by UI interactions (on_change, on_click).
These functions modify the session state and dictate the application's flow.
"""

import streamlit as st
import time
from i18n import T
from config import (
    DEFAULT_BAND,
    DEMO_PROFILES,
    SEGMENT_SELECTION_ALL,
    TX_AB_REPEAT_INTERVAL_OPTIONS,
)
from ui.documentation_state import collapse_documentation
from ui.config_io import (
    MODE_KEYS,
    apply_config_state_values,
    validate_config_document,
)
from ui.result_state import reset_result_state


def _demo_config_document(profile):
    """Return the ordinary config document exposed directly or by the UI adapter."""
    if isinstance(profile, dict) and isinstance(profile.get("configuration"), dict):
        return profile["configuration"]
    return profile

def reset_audit():
    """
    Cancels the active analysis and returns the app to the idle/configuration state.
    Triggered whenever a core parameter is changed by the user, ensuring that 
    stale or outdated map data isn't displayed on the screen.
    """
    st.session_state.run_mode = None
    st.session_state.active_demo_profile = None
    reset_result_state(st.session_state)


def _normalize_tx_ab_schedule_state(changed_start=None):
    """Keep periodic TX A/B starts valid and disjoint after one UI change."""
    repeat_interval = st.session_state.get(
        "val_tx_ab_repeat_interval_minutes",
        10,
    )
    if repeat_interval not in TX_AB_REPEAT_INTERVAL_OPTIONS:
        repeat_interval = 10
    permitted_starts = tuple(range(0, int(repeat_interval), 2))

    target_start = st.session_state.get("val_tx_ab_target_start_minute", 0)
    reference_start = st.session_state.get("val_tx_ab_reference_start_minute", 2)
    if target_start not in permitted_starts:
        target_start = permitted_starts[0]
    if reference_start not in permitted_starts:
        reference_start = next(
            start for start in permitted_starts if start != target_start
        )
    if target_start == reference_start:
        if changed_start == "reference":
            target_start = next(
                start for start in permitted_starts if start != reference_start
            )
        else:
            reference_start = next(
                start for start in permitted_starts if start != target_start
            )

    st.session_state.val_tx_ab_repeat_interval_minutes = int(repeat_interval)
    st.session_state.val_tx_ab_target_start_minute = int(target_start)
    st.session_state.val_tx_ab_reference_start_minute = int(reference_start)


def handle_tx_ab_repeat_interval_change():
    """Reconcile both UTC starts after changing the shared repeat interval."""
    _normalize_tx_ab_schedule_state()
    reset_audit()


def handle_tx_ab_target_start_change():
    """Keep Reference Start disjoint after changing Target Start."""
    _normalize_tx_ab_schedule_state(changed_start="target")
    reset_audit()


def handle_tx_ab_reference_start_change():
    """Keep Target Start disjoint after changing Reference Start."""
    _normalize_tx_ab_schedule_state(changed_start="reference")
    reset_audit()


def swap_tx_ab_starts():
    """Swap Target and Reference schedule attribution without allowing overlap."""
    target_start = st.session_state.val_tx_ab_target_start_minute
    st.session_state.val_tx_ab_target_start_minute = (
        st.session_state.val_tx_ab_reference_start_minute
    )
    st.session_state.val_tx_ab_reference_start_minute = target_start
    _normalize_tx_ab_schedule_state()
    reset_audit()

def update_lang():
    """
    Handles UI language changes globally. 
    Translates all string-based session states to the new language to prevent 
    StreamlitAPIExceptions and preserve user settings across hidden and visible fields.
    """
    old_lang = st.session_state.lang
    new_lang = {"EN": "en", "DE": "de"}[st.session_state.lang_selector_ui]
    
    t_old = T[old_lang]
    t_new = T[new_lang]
    
    # Mapping of session_state keys to their possible translation dictionary keys
    state_map = {
        "val_time_mode": ["opt_last_x", "opt_custom"],
        "val_comp_mode": ["opt_comp_none", "opt_comp_radius", "opt_comp_buddy", "opt_comp_self"],
        "val_local_benchmark": ["opt_local_median", "opt_local_best"],
        "val_solar": ["opt_solar_all", "opt_solar_day", "opt_solar_night", "opt_solar_grey"]
    }
    
    # Translate the current values to the new language
    for state_key, dict_keys in state_map.items():
        if state_key in st.session_state:
            current_val = st.session_state[state_key]
            for d_key in dict_keys:
                if current_val == t_old.get(d_key):
                    st.session_state[state_key] = t_new[d_key]
                    break
                    
    st.session_state.lang = new_lang
    st.session_state.run_mode = None

def _profile_matches_current_mode(profile, t):
    """Return True when a demo profile matches the currently selected comparison UI."""
    try:
        normalized_config = validate_config_document(_demo_config_document(profile))
    except ValueError:
        return False

    benchmark_mode = normalized_config.get("benchmark_mode")
    mode_key = MODE_KEYS.get(benchmark_mode)
    if not mode_key or t.get(mode_key) != st.session_state.val_comp_mode:
        return False

    selected_direction = st.session_state.get("val_analysis_direction")
    return (
        selected_direction is None
        or normalized_config.get("analysis_direction") == selected_direction
    )

def _demo_profile_for_current_mode(t):
    """Return the first configured demo profile matching the currently selected mode."""
    for profile_key, profile in DEMO_PROFILES.items():
        if _profile_matches_current_mode(profile, t):
            return profile_key
    return None

def _apply_demo_profile_values(profile_key):
    """Apply one explicit runnable demo profile to the normal editable config state."""
    profile = DEMO_PROFILES.get(profile_key)
    if not profile:
        return

    normalized_config = validate_config_document(_demo_config_document(profile))
    apply_config_state_values(normalized_config, st.session_state)

def apply_demo_profile(profile_key=None):
    """
    Applies the appropriate demo profile based on the selected benchmark design.
    Injects predefined, validated values for callsigns, locations, and timeframes 
    to guarantee a working demo query (Guided Sandbox Mode).
    """
    t = T[st.session_state.lang]
    if profile_key is None:
        if not st.session_state.get("is_demo_mode", False):
            return
        profile_key = _demo_profile_for_current_mode(t)

    if profile_key is None:
        return

    _apply_demo_profile_values(profile_key)

def load_demo_profile_config(profile_key):
    """
    Applies a selected demo profile to the editable config state without
    starting an analysis or collapsing the configuration panels.
    """
    profile = DEMO_PROFILES.get(profile_key)
    if not profile:
        return

    reset_audit()
    st.session_state.is_demo_mode = False
    st.session_state.active_demo_profile = None
    st.session_state.show_demo_launcher = False
    st.session_state.show_config_loader = False
    st.session_state.config_panels_expanded = True
    st.session_state._collapse_config_panels_once = False
    st.session_state.run_mode = None
    _apply_demo_profile_values(profile_key)
    for key in list(st.session_state.keys()):
        if key.startswith("img_buf_"):
            del st.session_state[key]
    st.rerun()

def run_demo_profile(profile_key):
    """
    Applies a selected demo profile, leaves the config editable, and immediately
    starts the profile's TX or RX analysis.
    """
    profile = DEMO_PROFILES.get(profile_key)
    if not profile:
        return

    st.session_state.is_demo_mode = False
    st.session_state.active_demo_profile = profile_key
    st.session_state.show_demo_launcher = False
    st.session_state.config_panels_expanded = False
    st.session_state._collapse_config_panels_once = True
    _apply_demo_profile_values(profile_key)
    analysis_direction = st.session_state.get("val_analysis_direction")
    if analysis_direction not in {"rx", "tx"}:
        raise ValueError(f"Demo profile {profile_key!r} has no analysis direction.")
    st.session_state.run_mode = analysis_direction.upper()
    st.session_state.run_id = int(time.time())
    collapse_documentation(st.session_state)
    reset_result_state(st.session_state)
    for key in list(st.session_state.keys()):
        if key.startswith("img_buf_"):
            del st.session_state[key]
    st.rerun()

def handle_comp_mode_change():
    """
    Reset active results and correction when the benchmark design changes.

    Normal benchmark designs start with no reference-SNR correction. Guided
    demo mode can then load an explicit profile correction when one exists.
    """
    st.session_state.val_benchmark_offset_db = 0.0
    reset_audit()
    apply_demo_profile()


def handle_analysis_direction_change():
    """
    Reset active results after selecting RX or TX analysis direction.

    Hardware A/B uses direction-specific parameters. Changing direction while
    that design is active returns to Success-only mode so an RX Setup-B
    callsign can never be reinterpreted as a TX schedule configuration, or vice
    versa.
    """
    t = T[st.session_state.lang]
    if st.session_state.get("val_comp_mode") == t["opt_comp_self"]:
        st.session_state.val_comp_mode = t["opt_comp_none"]
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.val_self_call_b = ""
        st.session_state.val_tx_ab_repeat_interval_minutes = 10
        st.session_state.val_tx_ab_target_start_minute = 0
        st.session_state.val_tx_ab_reference_start_minute = 2
    reset_audit()

def set_reset_config():
    """
    Resets all user inputs and configurations back to their default factory state.
    Exits demo mode securely and clears any active analysis run.
    """
    st.session_state.is_demo_mode = False
    t = T[st.session_state.lang]
    
    st.session_state.val_callsign = ""
    st.session_state.val_analysis_direction = None
    st.session_state.val_qth = ""
    st.session_state.val_band = DEFAULT_BAND
    st.session_state.val_time_mode = t["opt_last_x"]
    st.session_state.val_hours = 24
    st.session_state.val_solar = t["opt_solar_all"]
    st.session_state.val_comp_mode = t["opt_comp_none"]
    st.session_state.val_ref_stations = 10
    st.session_state.val_ref_radius_km = 100
    st.session_state.val_benchmark_offset_db = 0.0
    st.session_state.val_local_benchmark = t["opt_local_median"]
    st.session_state.val_ref_callsign = "DL2XYZ"
    st.session_state.val_self_call_b = ""
    st.session_state.val_tx_ab_repeat_interval_minutes = 10
    st.session_state.val_tx_ab_target_start_minute = 0
    st.session_state.val_tx_ab_reference_start_minute = 2
    st.session_state.val_max_dist = 22000
    st.session_state.val_exclude_special_callsigns = False
    st.session_state.val_filter_moving = False
    st.session_state.val_min_spots = 1
    st.session_state.val_min_opportunities = 5
    st.session_state.val_min_stations = 1
    st.session_state.val_results_show_non_joint = None
    st.session_state.val_results_show_zero_target = False
    st.session_state.val_results_selected_ranges_compare = SEGMENT_SELECTION_ALL
    st.session_state.val_results_selected_directions_compare = SEGMENT_SELECTION_ALL
    st.session_state.val_results_selected_ranges_absolute = SEGMENT_SELECTION_ALL
    st.session_state.val_results_selected_directions_absolute = SEGMENT_SELECTION_ALL
    st.session_state.val_results_time_bin_compare = None
    st.session_state.val_results_time_bin_absolute = None
    st.session_state.val_results_segment_time_bin_compare = "auto"
    st.session_state.val_results_station_temporal_view_compare = "chronological"
    st.session_state.val_results_selected_stations_compare = None
    st.session_state.val_results_selected_stations_absolute = None
    st.session_state.val_config_profile = None
    st.session_state.loaded_config_profile = None
    st.session_state.val_config_extensions = {}
    st.session_state.active_demo_profile = None
    st.session_state.show_demo_launcher = False
    st.session_state.show_config_loader = False
    st.session_state.config_panels_expanded = True
    st.session_state._collapse_config_panels_once = False
    st.session_state.run_mode = None
    reset_result_state(st.session_state)
    for state_key in tuple(st.session_state.keys()):
        if state_key.startswith("config_save_"):
            st.session_state.pop(state_key, None)

def set_demo_config():
    """
    Activates the Guided Sandbox demo mode. Locks core UI elements against 
    unwanted edits and loads the initial demographic profile.
    """
    st.session_state.is_demo_mode = True
    st.session_state.run_mode = None
    apply_demo_profile()
