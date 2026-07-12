"""
Callbacks Module for WSPRadar.
Contains all event handlers triggered by UI interactions (on_change, on_click).
These functions modify the session state and dictate the application's flow.
"""

import streamlit as st
import time
from i18n import T
from config import DEMO_PROFILES
from ui.results_export import reset_result_export_state

def reset_audit():
    """
    Cancels the active analysis and returns the app to the idle/configuration state.
    Triggered whenever a core parameter is changed by the user, ensuring that 
    stale or outdated map data isn't displayed on the screen.
    """
    st.session_state.run_mode = None
    st.session_state.active_demo_profile = None
    st.session_state.demo_view_defaults = {}
    reset_result_export_state()

def swap_tx_target_wspr_frame():
    """
    Swaps the target's WSPR frame sequence for Sequential A/B testing.
    Ensures that the reference sequence is automatically adjusted to the opposite
    modulo-4 UTC start-minute sequence to prevent collisions.
    """
    reset_audit()
    t_loc = T[st.session_state.lang]
    st.session_state.val_reference_wspr_frame = (
        t_loc["opt_wspr_frame_02_06_10"]
        if st.session_state.val_target_wspr_frame == t_loc["opt_wspr_frame_00_04_08"]
        else t_loc["opt_wspr_frame_00_04_08"]
    )

def swap_tx_reference_wspr_frame():
    """
    Swaps the reference's WSPR frame sequence for Sequential A/B testing.
    Ensures that the target sequence is automatically adjusted to the opposite
    modulo-4 UTC start-minute sequence.
    """
    reset_audit()
    t_loc = T[st.session_state.lang]
    st.session_state.val_target_wspr_frame = (
        t_loc["opt_wspr_frame_02_06_10"]
        if st.session_state.val_reference_wspr_frame == t_loc["opt_wspr_frame_00_04_08"]
        else t_loc["opt_wspr_frame_00_04_08"]
    )

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
        "val_comp_mode": ["opt_comp_radius", "opt_comp_buddy", "opt_comp_self"],
        "val_local_benchmark": ["opt_local_median", "opt_local_best"],
        "val_self_test_mode": ["opt_self_rx", "opt_self_tx"],
        "val_target_wspr_frame": ["opt_wspr_frame_00_04_08", "opt_wspr_frame_02_06_10", "opt_slot_even", "opt_slot_odd"],
        "val_reference_wspr_frame": ["opt_wspr_frame_00_04_08", "opt_wspr_frame_02_06_10", "opt_slot_even", "opt_slot_odd"],
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
    comparison = profile.get("comparison", {})
    mode_key = comparison.get("comp_mode_key")
    if not mode_key or t.get(mode_key) != st.session_state.val_comp_mode:
        return False

    if mode_key != "opt_comp_self":
        return True

    self_mode_key = comparison.get("self_test_mode_key")
    if not self_mode_key:
        return False

    return t.get(self_mode_key) == st.session_state.get("val_self_test_mode", t["opt_self_rx"])

def _demo_profile_for_current_mode(t):
    """Return the first configured demo profile matching the currently selected mode."""
    for profile_key, profile in DEMO_PROFILES.items():
        if _profile_matches_current_mode(profile, t):
            return profile_key
    return None

def _set_translated_state(t, section, state_key, profile_key, legacy_profile_key=None):
    """Set a localized session-state value from a profile translation-key field."""
    translation_key = section.get(profile_key)
    if translation_key is None and legacy_profile_key:
        translation_key = section.get(legacy_profile_key)
    if translation_key:
        st.session_state[state_key] = t[translation_key]

def _apply_demo_profile_values(profile_key):
    """Apply one explicit runnable demo profile to the normal editable config state."""
    profile = DEMO_PROFILES.get(profile_key)
    if not profile:
        return

    t = T[st.session_state.lang]
    core = profile.get("core_parameters", {})
    comparison = profile.get("comparison", {})
    advanced = profile.get("advanced", {})
    results_view = profile.get("results_view", {})

    _set_translated_state(t, comparison, "val_comp_mode", "comp_mode_key")
    _set_translated_state(t, comparison, "val_local_benchmark", "local_benchmark_key")
    _set_translated_state(t, comparison, "val_self_test_mode", "self_test_mode_key")
    _set_translated_state(t, comparison, "val_target_wspr_frame", "target_wspr_frame_key", legacy_profile_key="slot_u_key")
    _set_translated_state(t, comparison, "val_reference_wspr_frame", "reference_wspr_frame_key", legacy_profile_key="slot_r_key")

    st.session_state.val_callsign = str(core.get("callsign", "")).strip().upper()
    st.session_state.val_qth = str(core.get("qth", "")).strip().upper()
    st.session_state.val_band = core.get("band", "20m")
    st.session_state.val_time_mode = t[core.get("time_mode_key", "opt_custom")]
    st.session_state.val_hours = int(core.get("last_hours", st.session_state.get("val_hours", 24)))
    if st.session_state.val_time_mode == t["opt_custom"]:
        st.session_state.val_start_d = core["start_d"]
        st.session_state.val_end_d = core["end_d"]
        st.session_state.val_start_t = core["start_t"]
        st.session_state.val_end_t = core["end_t"]

    st.session_state.val_ref_radius_km = int(comparison.get("ref_radius_km", st.session_state.get("val_ref_radius_km", 100)))
    st.session_state.val_benchmark_offset_db = round(float(comparison.get("reference_snr_correction_db", 0.0)), 1)
    st.session_state.val_ref_callsign = str(comparison.get("ref_callsign", "")).strip().upper()
    st.session_state.val_self_call_b = str(comparison.get("self_call_b", "")).strip().upper()
    st.session_state.val_tx_ab_bin_minutes = int(comparison.get("tx_ab_bin_minutes", st.session_state.get("val_tx_ab_bin_minutes", 8)))

    st.session_state.val_max_dist = int(advanced.get("max_dist", 22000))
    st.session_state.val_solar = t[advanced.get("solar_key", "opt_solar_all")]
    st.session_state.val_exclude_special_callsigns = bool(advanced.get("exclude_special_callsigns", False))
    st.session_state.val_filter_moving = bool(advanced.get("exclude_moving_stations", False))
    st.session_state.val_min_spots = int(advanced.get("min_joint_spots_per_station", 1))
    st.session_state.val_min_opportunities = int(advanced.get("min_confirmed_opportunities_per_peer", 5))
    st.session_state.val_min_stations = int(advanced.get("min_joint_stations_per_segment", 1))
    st.session_state.demo_view_defaults = {
        "show_non_joint": bool(results_view.get("show_non_joint", False)),
        "station_evidence_time_bin_compare": results_view.get("station_evidence_time_bin_compare"),
        "station_evidence_time_bin_absolute": results_view.get("station_evidence_time_bin_absolute"),
    }

def apply_demo_profile(profile_key=None):
    """
    Applies the appropriate demo profile based on the currently selected comparison mode.
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
    st.session_state.run_mode = profile.get("run", {}).get("run_mode")
    st.session_state.run_id = int(time.time())
    reset_result_export_state()
    for key in list(st.session_state.keys()):
        if key.startswith("img_buf_"):
            del st.session_state[key]
    st.rerun()

def handle_comp_mode_change():
    """
    Event handler triggered when the user switches the main comparison mode 
    (A/B Test, Buddy, Radius). Resets any active audit and seamlessly applies
    the relevant demo profile if the sandbox mode is active.
    """
    reset_audit()
    apply_demo_profile()

def handle_self_test_mode_change():
    """
    Event handler triggered when the user toggles between RX and TX modes 
    inside the A/B test expander. Resets the audit and applies the profile.
    """
    reset_audit()
    apply_demo_profile()

def set_reset_config():
    """
    Resets all user inputs and configurations back to their default factory state.
    Exits demo mode securely and clears any active analysis run.
    """
    st.session_state.is_demo_mode = False
    t = T[st.session_state.lang]
    
    st.session_state.val_callsign = ""
    st.session_state.val_qth = ""
    st.session_state.val_band = "20m"
    st.session_state.val_time_mode = t["opt_last_x"]
    st.session_state.val_hours = 24
    st.session_state.val_solar = t["opt_solar_all"]
    st.session_state.val_comp_mode = t["opt_comp_self"]
    st.session_state.val_ref_stations = 10
    st.session_state.val_ref_radius_km = 100
    st.session_state.val_benchmark_offset_db = 0.0
    st.session_state.val_local_benchmark = t["opt_local_median"]
    st.session_state.val_ref_callsign = "DL2XYZ"
    st.session_state.val_self_test_mode = t["opt_self_rx"]
    st.session_state.val_self_call_b = ""
    st.session_state.val_target_wspr_frame = t["opt_wspr_frame_00_04_08"]
    st.session_state.val_reference_wspr_frame = t["opt_wspr_frame_02_06_10"]
    st.session_state.val_tx_ab_bin_minutes = 8
    st.session_state.val_max_dist = 22000
    st.session_state.val_exclude_special_callsigns = False
    st.session_state.val_filter_moving = False
    st.session_state.val_min_spots = 1
    st.session_state.val_min_opportunities = 5
    st.session_state.val_min_stations = 1
    st.session_state.active_demo_profile = None
    st.session_state.demo_view_defaults = {}
    st.session_state.show_demo_launcher = False
    st.session_state.show_config_loader = False
    st.session_state.config_panels_expanded = True
    st.session_state._collapse_config_panels_once = False
    st.session_state.run_mode = None

def set_demo_config():
    """
    Activates the Guided Sandbox demo mode. Locks core UI elements against 
    unwanted edits and loads the initial demographic profile.
    """
    st.session_state.is_demo_mode = True
    st.session_state.run_mode = None
    apply_demo_profile()
