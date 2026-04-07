"""
State Management Module for WSPRadar.
Handles the initialization of all Streamlit session state variables
to ensure a consistent default state across user sessions and reruns.
"""

import streamlit as st
from datetime import datetime, timedelta, timezone, time as dt_time
from i18n import T

def get_browser_language() -> str:
    """
    Attempts to determine the user's preferred language from browser request headers.
    Defaults to English ('en') if detection fails or headers are unavailable.
    """
    try:
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            accept_lang = st.context.headers.get("Accept-Language", "").lower()
            if accept_lang.startswith("de"): 
                return "de"
    except Exception: 
        pass
    
    return "en"

def init_session_state():
    """
    Initializes all required session state variables if they do not already exist.
    This prevents KeyError exceptions and ensures the UI loads with safe default values.
    """
    # --- Core Application States ---
    if "run_mode" not in st.session_state: 
        st.session_state.run_mode = None
    if "lang" not in st.session_state: 
        st.session_state.lang = get_browser_language()
    if "is_demo_mode" not in st.session_state: 
        st.session_state.is_demo_mode = False
        
    # --- Default User Inputs (Core Parameters) ---
    if "val_callsign" not in st.session_state: 
        st.session_state.val_callsign = "DL1MKS"
    if "val_qth" not in st.session_state: 
        st.session_state.val_qth = "JN37"
    if "val_band" not in st.session_state: 
        st.session_state.val_band = "20m"
        
    # --- Default Time Settings ---
    if "val_time_mode" not in st.session_state: 
        st.session_state.val_time_mode = T["en"]["opt_last_x"]
    if "val_hours" not in st.session_state: 
        st.session_state.val_hours = 24
    if "val_start_d" not in st.session_state: 
        st.session_state.val_start_d = datetime.now(timezone.utc).date() - timedelta(days=1)
    if "val_start_t" not in st.session_state: 
        st.session_state.val_start_t = dt_time(0, 0)
    if "val_end_d" not in st.session_state: 
        st.session_state.val_end_d = datetime.now(timezone.utc).date()
    if "val_end_t" not in st.session_state: 
        st.session_state.val_end_t = dt_time(23, 59)
        
    # --- Default Comparison Modes (Compare Engine) ---
    if "val_comp_mode" not in st.session_state: 
        st.session_state.val_comp_mode = T["en"]["opt_comp_radius"]
    if "val_ref_stations" not in st.session_state: 
        st.session_state.val_ref_stations = 25
    if "val_ref_callsign" not in st.session_state: 
        st.session_state.val_ref_callsign = "DL2XYZ"
    if "val_self_test_mode" not in st.session_state: 
        st.session_state.val_self_test_mode = T["en"]["opt_self_rx"]
    if "val_self_call_b" not in st.session_state: 
        st.session_state.val_self_call_b = ""
    if "val_slot_u" not in st.session_state: 
        st.session_state.val_slot_u = T["en"]["opt_slot_even"]
    if "val_slot_r" not in st.session_state: 
        st.session_state.val_slot_r = T["en"]["opt_slot_odd"]
        
    # --- Default Advanced Configurations ---
    if "val_solar" not in st.session_state: 
        st.session_state.val_solar = T["en"]["opt_solar_all"]
    if "val_max_dist" not in st.session_state: 
        st.session_state.val_max_dist = 22000
    if "val_exclude_prefixes" not in st.session_state: 
        st.session_state.val_exclude_prefixes = "Q, 0, 1"
    if "val_filter_moving" not in st.session_state: 
        st.session_state.val_filter_moving = True
    if "val_min_spots" not in st.session_state: 
        st.session_state.val_min_spots = 1
    if "val_min_stations" not in st.session_state: 
        st.session_state.val_min_stations = 1
    if "val_wilcoxon" not in st.session_state: 
        st.session_state.val_wilcoxon = "OFF"