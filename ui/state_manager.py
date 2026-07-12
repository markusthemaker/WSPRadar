"""
State Management Module for WSPRadar.
Handles the initialization of all Streamlit session state variables
to ensure a consistent default state across user sessions and reruns.
"""

import streamlit as st
from datetime import datetime, timedelta, timezone, time as dt_time
from i18n import T

def _normalize_wspr_frame_state_value(value, lang, fallback_key):
    """Map current or legacy WSPR frame labels into the active UI language."""
    t_cur = T[lang]
    frame_00_values = {
        T["en"]["opt_wspr_frame_00_04_08"],
        T["de"]["opt_wspr_frame_00_04_08"],
        T["en"]["opt_slot_even"],
        T["de"]["opt_slot_even"],
        "Frame 00, 04, 08, ...",
        "Even Minutes (00, 04, 08...)",
        "Gerade Min (00, 04, 08...)",
    }
    frame_02_values = {
        T["en"]["opt_wspr_frame_02_06_10"],
        T["de"]["opt_wspr_frame_02_06_10"],
        T["en"]["opt_slot_odd"],
        T["de"]["opt_slot_odd"],
        "Frame 02, 06, 10, ...",
        "Odd Minutes (02, 06, 10...)",
        "Ungerade Min (02, 06, 10...)",
    }
    if value in frame_00_values:
        return t_cur["opt_wspr_frame_00_04_08"]
    if value in frame_02_values:
        return t_cur["opt_wspr_frame_02_06_10"]
    return t_cur[fallback_key]

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
    if "config_panels_expanded" not in st.session_state:
        st.session_state.config_panels_expanded = True
    if "_collapse_config_panels_once" not in st.session_state:
        st.session_state._collapse_config_panels_once = False
    if "show_config_loader" not in st.session_state:
        st.session_state.show_config_loader = False
    if "demo_view_defaults" not in st.session_state:
        st.session_state.demo_view_defaults = {}
        
    # --- Default User Inputs (Core Parameters) ---
    if "val_callsign" not in st.session_state: 
        st.session_state.val_callsign = ""
    if "val_qth" not in st.session_state: 
        st.session_state.val_qth = ""
    if "val_band" not in st.session_state: 
        st.session_state.val_band = "30m"
        
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
        st.session_state.val_comp_mode = T[st.session_state.lang]["opt_comp_self"]
    if "val_ref_stations" not in st.session_state: 
        st.session_state.val_ref_stations = 10
    if "val_ref_radius_km" not in st.session_state:
        st.session_state.val_ref_radius_km = 100
    if "val_benchmark_offset_db" not in st.session_state:
        st.session_state.val_benchmark_offset_db = 0.0
    if "val_local_benchmark" not in st.session_state:
        st.session_state.val_local_benchmark = T["en"]["opt_local_median"]
    t_cur = T[st.session_state.lang]
    if st.session_state.val_comp_mode in ["Nearest Peers (Local Average)", "Nearest Peers (Lokaler Durchschnitt)"]:
        st.session_state.val_comp_mode = t_cur["opt_comp_radius"]
    if st.session_state.val_local_benchmark not in [t_cur["opt_local_best"], t_cur["opt_local_median"]]:
        st.session_state.val_local_benchmark = t_cur["opt_local_median"]
    if "val_ref_callsign" not in st.session_state: 
        st.session_state.val_ref_callsign = "DL2XYZ"
    if "val_self_test_mode" not in st.session_state: 
        st.session_state.val_self_test_mode = T["en"]["opt_self_rx"]
    if "val_self_call_b" not in st.session_state: 
        st.session_state.val_self_call_b = ""
    if "val_target_wspr_frame" not in st.session_state:
        st.session_state.val_target_wspr_frame = _normalize_wspr_frame_state_value(
            st.session_state.get("val_slot_u"),
            st.session_state.lang,
            "opt_wspr_frame_00_04_08",
        )
    else:
        st.session_state.val_target_wspr_frame = _normalize_wspr_frame_state_value(
            st.session_state.val_target_wspr_frame,
            st.session_state.lang,
            "opt_wspr_frame_00_04_08",
        )
    if "val_reference_wspr_frame" not in st.session_state:
        st.session_state.val_reference_wspr_frame = _normalize_wspr_frame_state_value(
            st.session_state.get("val_slot_r"),
            st.session_state.lang,
            "opt_wspr_frame_02_06_10",
        )
    else:
        st.session_state.val_reference_wspr_frame = _normalize_wspr_frame_state_value(
            st.session_state.val_reference_wspr_frame,
            st.session_state.lang,
            "opt_wspr_frame_02_06_10",
        )
    if "val_tx_ab_bin_minutes" not in st.session_state: 
        st.session_state.val_tx_ab_bin_minutes = 8
        
    # --- Default Advanced Configurations ---
    if "val_solar" not in st.session_state: 
        st.session_state.val_solar = T["en"]["opt_solar_all"]
    if "val_max_dist" not in st.session_state: 
        st.session_state.val_max_dist = 22000
    if "val_exclude_special_callsigns" not in st.session_state:
        st.session_state.val_exclude_special_callsigns = False
    if "val_filter_moving" not in st.session_state: 
        st.session_state.val_filter_moving = False
    if "val_min_spots" not in st.session_state: 
        st.session_state.val_min_spots = 1
    if "val_min_opportunities" not in st.session_state:
        st.session_state.val_min_opportunities = 5
    if "val_min_stations" not in st.session_state: 
        st.session_state.val_min_stations = 1
