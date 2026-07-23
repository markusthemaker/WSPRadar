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
    SNR_CORRECTION_MODES,
    TX_AB_REPEAT_INTERVAL_OPTIONS,
)
from i18n import LEGACY_LOCALIZED_STATE_VALUES, T


def _canonicalize_localized_state(value, canonical_to_translation_key, fallback):
    """Return a stable token for legacy sessions that still hold display text."""
    if value in canonical_to_translation_key:
        return value
    legacy_canonical_value = LEGACY_LOCALIZED_STATE_VALUES.get(value)
    if legacy_canonical_value in canonical_to_translation_key:
        return legacy_canonical_value
    for translations in T.values():
        for canonical, translation_key in canonical_to_translation_key.items():
            if value == translations.get(translation_key):
                return canonical
    return fallback

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
    if st.session_state.get("input_view") not in {"guided", "classic"}:
        st.session_state.input_view = "guided"
    if st.session_state.get("guided_use_case") not in {
        None,
        "rx_success",
        "tx_success",
        "rx_compare",
        "tx_compare",
    }:
        st.session_state.guided_use_case = None
    if "guided_use_case" not in st.session_state:
        st.session_state.guided_use_case = None
    if "guided_reference_design" not in st.session_state:
        st.session_state.guided_reference_design = None
    if "guided_last_compare_mode" not in st.session_state:
        st.session_state.guided_last_compare_mode = None
    if st.session_state.get("guided_scope_mode") not in {
        "general",
        "custom",
        "demo",
    }:
        st.session_state.guided_scope_mode = "general"
    if "guided_active_node" not in st.session_state:
        st.session_state.guided_active_node = "use_case"
    if "guided_reconstruct_requested" not in st.session_state:
        st.session_state.guided_reconstruct_requested = False
    if "guided_demo_metadata_open" not in st.session_state:
        st.session_state.guided_demo_metadata_open = False
    if "guided_loaded_demo_profile" not in st.session_state:
        st.session_state.guided_loaded_demo_profile = None
    if "guided_collapse_all" not in st.session_state:
        st.session_state.guided_collapse_all = False
    if "configuration_changed_since_run" not in st.session_state:
        st.session_state.configuration_changed_since_run = False
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
    st.session_state.val_time_mode = _canonicalize_localized_state(
        st.session_state.get("val_time_mode"),
        {"last_x": "opt_last_x", "custom": "opt_custom"},
        "last_x",
    )
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
    st.session_state.val_comp_mode = _canonicalize_localized_state(
        st.session_state.get("val_comp_mode"),
        {
            "none": "opt_comp_none",
            "hardware_ab": "opt_comp_self",
            "reference_station": "opt_comp_buddy",
            "local_neighborhood": "opt_comp_radius",
        },
        "none",
    )
    if "val_ref_stations" not in st.session_state: 
        st.session_state.val_ref_stations = 10
    if "val_ref_radius_km" not in st.session_state:
        st.session_state.val_ref_radius_km = 100
    if "val_benchmark_offset_db" not in st.session_state:
        st.session_state.val_benchmark_offset_db = 0.0
    if st.session_state.get("val_snr_correction_mode") not in SNR_CORRECTION_MODES:
        st.session_state.val_snr_correction_mode = "no_offset"
    if (
        st.session_state.val_comp_mode == "local_neighborhood"
        and st.session_state.val_snr_correction_mode == "establish_offset"
    ):
        st.session_state.val_snr_correction_mode = "no_offset"
    if st.session_state.val_snr_correction_mode in {
        "no_offset",
        "establish_offset",
    }:
        st.session_state.val_benchmark_offset_db = 0.0
    st.session_state.val_local_benchmark = _canonicalize_localized_state(
        st.session_state.get("val_local_benchmark"),
        {"local_median": "opt_local_median", "local_best": "opt_local_best"},
        "local_median",
    )
    if "val_ref_callsign" not in st.session_state: 
        st.session_state.val_ref_callsign = ""
    if "val_ref_qth" not in st.session_state:
        st.session_state.val_ref_qth = ""
    if st.session_state.get("val_tx_ab_method") not in {
        "simultaneous",
        "sequential",
    }:
        st.session_state.val_tx_ab_method = "simultaneous"
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
    st.session_state.val_solar = _canonicalize_localized_state(
        st.session_state.get("val_solar"),
        {
            "all": "opt_solar_all",
            "day": "opt_solar_day",
            "night": "opt_solar_night",
            "greyline": "opt_solar_grey",
        },
        "all",
    )
    if "val_max_peer_distance_km" not in st.session_state:
        st.session_state.val_max_peer_distance_km = 22000
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
    if "loaded_config_profile" not in st.session_state:
        st.session_state.loaded_config_profile = None
    if "val_config_extensions" not in st.session_state:
        st.session_state.val_config_extensions = {}

    # Streamlit normally deletes widget-bound state when a conditional widget is
    # not rendered. Self-assignment at the start of each rerun keeps canonical
    # scientific values independent of which editor or Guided branch is visible.
    canonical_state_keys = (
        "val_analysis_direction",
        "val_callsign",
        "val_qth",
        "val_band",
        "val_time_mode",
        "val_hours",
        "val_start_d",
        "val_start_t",
        "val_end_d",
        "val_end_t",
        "val_comp_mode",
        "val_local_benchmark",
        "val_ref_callsign",
        "val_ref_qth",
        "val_ref_radius_km",
        "val_benchmark_offset_db",
        "val_snr_correction_mode",
        "val_tx_ab_method",
        "val_tx_ab_repeat_interval_minutes",
        "val_tx_ab_target_start_minute",
        "val_tx_ab_reference_start_minute",
        "val_solar",
        "val_max_peer_distance_km",
        "val_exclude_special_callsigns",
        "val_filter_moving",
        "val_min_spots",
        "val_min_opportunities",
        "val_min_stations",
    )
    for state_key in canonical_state_keys:
        if state_key in st.session_state:
            st.session_state[state_key] = st.session_state[state_key]
