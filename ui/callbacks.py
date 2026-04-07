"""
Callbacks Module for WSPRadar.
Contains all event handlers triggered by UI interactions (on_change, on_click).
These functions modify the session state and dictate the application's flow.
"""

import streamlit as st
from i18n import T
from config import DEMO_PROFILES

def reset_audit():
    """
    Cancels the active analysis and returns the app to the idle/configuration state.
    Triggered whenever a core parameter is changed by the user, ensuring that 
    stale or outdated map data isn't displayed on the screen.
    """
    st.session_state.run_mode = None

def swap_tx_slots_u():
    """
    Swaps the target's transmission time slot for Sequential A/B testing.
    Ensures that the reference slot is automatically adjusted to the opposite parity 
    (e.g., if target switches to Even, reference is forced to Odd) to prevent collisions.
    """
    reset_audit()
    t_loc = T[st.session_state.lang]
    st.session_state.val_slot_r = t_loc["opt_slot_odd"] if st.session_state.val_slot_u == t_loc["opt_slot_even"] else t_loc["opt_slot_even"]

def swap_tx_slots_r():
    """
    Swaps the reference's transmission time slot for Sequential A/B testing.
    Ensures that the target slot is automatically adjusted to the opposite parity.
    """
    reset_audit()
    t_loc = T[st.session_state.lang]
    st.session_state.val_slot_u = t_loc["opt_slot_odd"] if st.session_state.val_slot_r == t_loc["opt_slot_even"] else t_loc["opt_slot_even"]

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
        "val_self_test_mode": ["opt_self_rx", "opt_self_tx"],
        "val_slot_u": ["opt_slot_even", "opt_slot_odd"],
        "val_slot_r": ["opt_slot_even", "opt_slot_odd"],
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

def apply_demo_profile():
    """
    Applies the appropriate demo profile based on the currently selected comparison mode.
    Injects predefined, validated values for callsigns, locations, and timeframes 
    to guarantee a working demo query (Guided Sandbox Mode).
    """
    if not st.session_state.get("is_demo_mode", False): 
        return
    
    t = T[st.session_state.lang]
    mode = st.session_state.val_comp_mode
    
    # Load the correct profile dictionary based on the active mode
    if mode == t["opt_comp_radius"]:
        p = DEMO_PROFILES["radius"]
        st.session_state.val_ref_stations = p["ref_stations"]
    elif mode == t["opt_comp_buddy"]:
        p = DEMO_PROFILES["buddy"]
        st.session_state.val_ref_callsign = p["ref_callsign"]
    elif mode == t["opt_comp_self"]:
        # Check if the user is in the RX or TX sub-mode of the self test
        if st.session_state.get("val_self_test_mode", t["opt_self_rx"]) == t["opt_self_rx"]:
            p = DEMO_PROFILES["self_rx"]
            st.session_state.val_self_call_b = p["self_call_b"]
        else:
            p = DEMO_PROFILES["self_tx"]
    else: 
        return

    # Override global parameters with the loaded profile's safe values
    st.session_state.val_callsign = p["callsign"]
    st.session_state.val_qth = p["qth"]
    st.session_state.val_band = p["band"]
    st.session_state.val_time_mode = t["opt_custom"]
    st.session_state.val_start_d = p["start_d"]
    st.session_state.val_end_d = p["end_d"]
    st.session_state.val_start_t = p["start_t"]
    st.session_state.val_end_t = p["end_t"]

def handle_comp_mode_change():
    """
    Event handler triggered when the user switches the main comparison mode 
    (Radius, Buddy, A/B Test). Resets any active audit and seamlessly applies 
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
    st.session_state.val_comp_mode = t["opt_comp_radius"]
    st.session_state.val_ref_stations = 25
    st.session_state.val_max_dist = 22000
    st.session_state.val_exclude_prefixes = "Q, 0, 1"
    st.session_state.val_filter_moving = True
    st.session_state.val_min_spots = 1
    st.session_state.val_min_stations = 1
    st.session_state.val_wilcoxon = "OFF"
    st.session_state.run_mode = None

def set_demo_config():
    """
    Activates the Guided Sandbox demo mode. Locks core UI elements against 
    unwanted edits and loads the initial demographic profile.
    """
    st.session_state.is_demo_mode = True
    st.session_state.run_mode = None
    apply_demo_profile()