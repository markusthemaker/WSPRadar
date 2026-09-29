"""
State Management Module for WSPRadar.
Handles the initialization of all Streamlit session state variables
to ensure a consistent default state across user sessions and reruns.
"""

import streamlit as st
from config import (
    BAND_MAP,
    DEFAULT_BAND,
    SNR_CORRECTION_MODES,
)
from config.delta_snr_outlier import (
    DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
    DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD,
)
from ui.classic_input_state import initialize_classic_input_state
from ui.inspector.selection_state import seed_inspector_selection_state
from ui.population_exclusion_state import initialize_population_exclusion_state
from ui.time_window import initialize_utc_window_state


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
    if "config_panels_expanded" not in st.session_state:
        st.session_state.config_panels_expanded = True
    if "_collapse_config_panels_once" not in st.session_state:
        st.session_state._collapse_config_panels_once = False
    if "show_config_loader" not in st.session_state:
        st.session_state.show_config_loader = False
    if st.session_state.get("input_view") not in {"guided", "classic"}:
        st.session_state.input_view = "guided"
    guided_use_case = st.session_state.get("guided_use_case")
    if guided_use_case not in {
        None,
        "rx_performance",
        "tx_performance",
        "rx_benchmark",
        "tx_benchmark",
    }:
        st.session_state.guided_use_case = None
    if "guided_use_case" not in st.session_state:
        st.session_state.guided_use_case = None
    if "guided_reference_design" not in st.session_state:
        st.session_state.guided_reference_design = None
    if "guided_last_benchmark_mode" not in st.session_state:
        st.session_state.guided_last_benchmark_mode = None
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
    initialize_utc_window_state(st.session_state)
        
    # --- Default Benchmark Design ---
    if st.session_state.get("val_comp_mode") not in {"none", "reference_station", "local_neighborhood"}:
        st.session_state.val_comp_mode = "none"
    initialize_classic_input_state(st.session_state)
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
    if "val_local_benchmark" not in st.session_state:
        st.session_state.val_local_benchmark = "local_median"
    if "val_ref_callsign" not in st.session_state: 
        st.session_state.val_ref_callsign = ""
    if "val_ref_qth" not in st.session_state:
        st.session_state.val_ref_qth = ""

    # --- Default Advanced Configurations ---
    if st.session_state.get("val_solar") not in {"all", "day", "night", "greyline"}:
        st.session_state.val_solar = "all"
    if "val_max_peer_distance_km" not in st.session_state:
        st.session_state.val_max_peer_distance_km = 22000
    initialize_population_exclusion_state(st.session_state)
    if "val_min_spots" not in st.session_state: 
        st.session_state.val_min_spots = 1
    if "val_min_opportunities" not in st.session_state:
        st.session_state.val_min_opportunities = 5
    if "val_min_stations" not in st.session_state: 
        st.session_state.val_min_stations = 1
    if "val_report_delta_snr_outlier_candidates" not in st.session_state:
        st.session_state.val_report_delta_snr_outlier_candidates = False
    for config_field, policy_field in (
        DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
    ):
        state_key = f"val_{config_field}"
        if state_key not in st.session_state:
            st.session_state[state_key] = getattr(
                DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
                policy_field,
            )

    # --- Stable Result-View Configuration ---
    seed_inspector_selection_state(st.session_state)

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
        "val_solar",
        "val_max_peer_distance_km",
        "val_exclude_special_callsigns",
        "val_filter_moving",
        "val_min_spots",
        "val_min_opportunities",
        "val_min_stations",
        "val_report_delta_snr_outlier_candidates",
        *(
            f"val_{config_field}"
            for config_field, _policy_field in (
                DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
            )
        ),
    )
    for state_key in canonical_state_keys:
        if state_key in st.session_state:
            st.session_state[state_key] = st.session_state[state_key]
