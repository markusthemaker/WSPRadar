"""
State Management Module for WSPRadar.
Handles the initialization of all Streamlit session state variables
to ensure a consistent default state across user sessions and reruns.
"""

import streamlit as st
from datetime import datetime, timedelta, timezone, time as dt_time
from config import (
    BAND_MAP,
    DEFAULT_BAND,
    SEGMENT_SELECTION_ALL,
    TX_AB_REPEAT_INTERVAL_OPTIONS,
)
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
    if "config_panels_expanded" not in st.session_state:
        st.session_state.config_panels_expanded = True
    if "_collapse_config_panels_once" not in st.session_state:
        st.session_state._collapse_config_panels_once = False
    if "show_config_loader" not in st.session_state:
        st.session_state.show_config_loader = False
    # --- Default User Inputs (Core Parameters) ---
    if "val_callsign" not in st.session_state: 
        st.session_state.val_callsign = ""
    if st.session_state.get("val_analysis_direction") not in {"rx", "tx"}:
        st.session_state.val_analysis_direction = None
    if "val_qth" not in st.session_state: 
        st.session_state.val_qth = ""
    if "val_band" not in st.session_state: 
        st.session_state.val_band = DEFAULT_BAND
    elif st.session_state.val_band not in BAND_MAP:
        st.session_state.val_band = DEFAULT_BAND
        
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
        
    # --- Default Benchmark Design ---
    if "val_comp_mode" not in st.session_state: 
        st.session_state.val_comp_mode = T[st.session_state.lang]["opt_comp_none"]
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
    if "val_self_call_b" not in st.session_state: 
        st.session_state.val_self_call_b = ""
    if "val_tx_ab_repeat_interval_minutes" not in st.session_state:
        st.session_state.val_tx_ab_repeat_interval_minutes = 10
        st.session_state.val_tx_ab_target_start_minute = 0
        st.session_state.val_tx_ab_reference_start_minute = 2

    repeat_interval = st.session_state.get("val_tx_ab_repeat_interval_minutes", 10)
    if repeat_interval not in TX_AB_REPEAT_INTERVAL_OPTIONS:
        repeat_interval = 10
    permitted_starts = tuple(range(0, int(repeat_interval), 2))
    target_start = st.session_state.get("val_tx_ab_target_start_minute", 0)
    reference_start = st.session_state.get("val_tx_ab_reference_start_minute", 2)
    if target_start not in permitted_starts:
        target_start = permitted_starts[0]
    if reference_start not in permitted_starts or reference_start == target_start:
        reference_start = next(
            start for start in permitted_starts if start != target_start
        )

    st.session_state.val_tx_ab_repeat_interval_minutes = int(repeat_interval)
    st.session_state.val_tx_ab_target_start_minute = int(target_start)
    st.session_state.val_tx_ab_reference_start_minute = int(reference_start)
        
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

    # --- Stable Result-View Configuration ---
    if "val_results_show_non_joint" not in st.session_state:
        st.session_state.val_results_show_non_joint = None
    if "val_results_show_zero_target" not in st.session_state:
        st.session_state.val_results_show_zero_target = False
    if "val_results_selected_ranges_compare" not in st.session_state:
        st.session_state.val_results_selected_ranges_compare = SEGMENT_SELECTION_ALL
    if "val_results_selected_directions_compare" not in st.session_state:
        st.session_state.val_results_selected_directions_compare = SEGMENT_SELECTION_ALL
    if "val_results_selected_ranges_absolute" not in st.session_state:
        st.session_state.val_results_selected_ranges_absolute = SEGMENT_SELECTION_ALL
    if "val_results_selected_directions_absolute" not in st.session_state:
        st.session_state.val_results_selected_directions_absolute = SEGMENT_SELECTION_ALL
    if "val_results_time_bin_compare" not in st.session_state:
        st.session_state.val_results_time_bin_compare = None
    if "val_results_time_bin_absolute" not in st.session_state:
        st.session_state.val_results_time_bin_absolute = None
    if "val_results_segment_time_bin_compare" not in st.session_state:
        st.session_state.val_results_segment_time_bin_compare = "auto"
    if "val_results_station_temporal_view_compare" not in st.session_state:
        st.session_state.val_results_station_temporal_view_compare = "chronological"
    if "val_results_selected_stations_compare" not in st.session_state:
        st.session_state.val_results_selected_stations_compare = None
    if "val_results_selected_stations_absolute" not in st.session_state:
        st.session_state.val_results_selected_stations_absolute = None

    # --- Loaded/Saved Config Document State ---
    if "val_config_profile" not in st.session_state:
        st.session_state.val_config_profile = None
    if "val_config_extensions" not in st.session_state:
        st.session_state.val_config_extensions = {}
