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
from ui.page_navigation import (
    PARAMETER_SETTINGS_ANCHOR_ID,
    RESULTS_INSPECTION_ANCHOR_ID,
    request_page_navigation,
)
from ui.result_state import reset_result_state
from ui.analysis_submission_state import (
    begin_analysis_submission,
    cancel_analysis_submission,
)


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
    had_current_result = bool(st.session_state.get("run_mode"))
    cancel_analysis_submission(st.session_state)
    st.session_state.run_mode = None
    st.session_state.active_demo_profile = None
    reset_result_state(st.session_state)
    if had_current_result:
        st.session_state.configuration_changed_since_run = True


def handle_reference_correction_context_change():
    """Clear a correction when its identity, band, or Reference design changes.

    Reference-side corrections are established for one controlled path or
    Target–Reference pair and operating design. Carrying one across a changed
    identity, QTH, band, local method, or TX schedule would silently alter every
    reported Delta SNR under a context for which it was not established.
    """
    active_mode = st.session_state.get("val_comp_mode")
    retained_mode = st.session_state.get("guided_last_compare_mode")
    comparison_modes = {
        "hardware_ab",
        "reference_station",
        "local_neighborhood",
    }
    if active_mode in comparison_modes or retained_mode in comparison_modes:
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.val_snr_correction_mode = "no_offset"
    reset_audit()


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


def _finish_tx_ab_schedule_change(after_change=None, after_change_args=()):
    """Run the requested editor callback after schedule normalization."""
    if after_change is None:
        reset_audit()
    else:
        after_change(*(after_change_args or ()))


def handle_tx_ab_repeat_interval_change(after_change=None, after_change_args=()):
    """Reconcile both UTC starts, then invalidate the owning editor's result."""
    _normalize_tx_ab_schedule_state()
    _finish_tx_ab_schedule_change(after_change, after_change_args)


def handle_tx_ab_target_start_change(after_change=None, after_change_args=()):
    """Keep Reference Start disjoint, then notify the owning editor."""
    _normalize_tx_ab_schedule_state(changed_start="target")
    _finish_tx_ab_schedule_change(after_change, after_change_args)


def handle_tx_ab_reference_start_change(after_change=None, after_change_args=()):
    """Keep Target Start disjoint, then notify the owning editor."""
    _normalize_tx_ab_schedule_state(changed_start="reference")
    _finish_tx_ab_schedule_change(after_change, after_change_args)


def swap_tx_ab_starts(after_change=None, after_change_args=()):
    """Swap schedule attribution, then notify the owning editor."""
    target_start = st.session_state.val_tx_ab_target_start_minute
    st.session_state.val_tx_ab_target_start_minute = (
        st.session_state.val_tx_ab_reference_start_minute
    )
    st.session_state.val_tx_ab_reference_start_minute = target_start
    _normalize_tx_ab_schedule_state()
    _finish_tx_ab_schedule_change(after_change, after_change_args)

def update_lang():
    """Apply the selected display language while canonical state stays unchanged."""
    new_lang = {"EN": "en", "DE": "de"}[st.session_state.lang_selector_ui]

    cancel_analysis_submission(st.session_state)
    st.session_state.lang = new_lang
    st.session_state.run_mode = None


def handle_input_view_change():
    """Reconstruct Guided presentation state without changing scientific state."""
    if st.session_state.get("input_view") == "guided":
        st.session_state.guided_reconstruct_requested = True
        st.session_state.guided_collapse_all = False

def _profile_matches_current_mode(profile, t):
    """Return True when a demo profile matches the currently selected comparison UI."""
    try:
        normalized_config = validate_config_document(_demo_config_document(profile))
    except ValueError:
        return False

    benchmark_mode = normalized_config.get("benchmark_mode")
    if benchmark_mode not in MODE_KEYS or benchmark_mode != st.session_state.val_comp_mode:
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
    st.session_state.guided_last_compare_mode = None
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
    st.session_state.show_demo_launcher = False
    st.session_state.show_config_loader = False
    st.session_state.config_panels_expanded = True
    st.session_state._collapse_config_panels_once = False
    st.session_state.run_mode = None
    _apply_demo_profile_values(profile_key)
    # The loaded values remain a trusted built-in demo until a scientific
    # configuration callback calls ``reset_audit`` after an edit.
    st.session_state.active_demo_profile = profile_key
    st.session_state.guided_loaded_demo_profile = profile_key
    st.session_state.guided_demo_metadata_open = True
    st.session_state.guided_reconstruct_requested = True
    st.session_state.guided_collapse_all = False
    st.session_state.configuration_changed_since_run = False
    request_page_navigation(
        st.session_state,
        PARAMETER_SETTINGS_ANCHOR_ID,
        should_scroll=True,
    )
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

    # A direct demo launch replaces any queued/running request whose editable
    # state this callback is about to overwrite.
    cancel_analysis_submission(st.session_state)
    st.session_state.is_demo_mode = False
    st.session_state.active_demo_profile = profile_key
    st.session_state.guided_loaded_demo_profile = profile_key
    st.session_state.guided_demo_metadata_open = False
    st.session_state.guided_reconstruct_requested = True
    st.session_state.guided_collapse_all = True
    st.session_state.configuration_changed_since_run = False
    st.session_state.show_demo_launcher = False
    st.session_state.config_panels_expanded = False
    st.session_state._collapse_config_panels_once = True
    _apply_demo_profile_values(profile_key)
    analysis_direction = st.session_state.get("val_analysis_direction")
    if analysis_direction not in {"rx", "tx"}:
        raise ValueError(f"Demo profile {profile_key!r} has no analysis direction.")
    st.session_state.run_mode = analysis_direction.upper()
    st.session_state.run_id = int(time.time())
    begin_analysis_submission(
        st.session_state,
        request_source="demo",
    )
    request_page_navigation(
        st.session_state,
        RESULTS_INSPECTION_ANCHOR_ID,
        should_scroll=True,
    )
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
    st.session_state.val_snr_correction_mode = "no_offset"
    reset_audit()
    apply_demo_profile()


def handle_analysis_direction_change():
    """
    Reset active results after selecting RX or TX analysis direction.

    Hardware A/B uses direction-specific parameters. Changing direction while
    that design is active or retained returns to Success-only mode so an RX
    identity can never become a TX schedule configuration, or vice versa.
    Reference Station and Local Neighborhood keep their identities/scope but
    clear any direction-specific correction.
    """
    active_mode = st.session_state.get("val_comp_mode")
    retained_mode = st.session_state.get("guided_last_compare_mode")
    if active_mode == "hardware_ab" or retained_mode == "hardware_ab":
        st.session_state.val_comp_mode = "none"
        st.session_state.guided_reference_design = None
        st.session_state.guided_last_compare_mode = None
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.val_snr_correction_mode = "no_offset"
        st.session_state.val_tx_ab_method = "simultaneous"
        st.session_state.val_tx_ab_repeat_interval_minutes = 10
        st.session_state.val_tx_ab_target_start_minute = 0
        st.session_state.val_tx_ab_reference_start_minute = 2
    elif active_mode in {"reference_station", "local_neighborhood"} or retained_mode in {
        "reference_station",
        "local_neighborhood",
    }:
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.val_snr_correction_mode = "no_offset"
    reset_audit()

def set_reset_config():
    """
    Resets all user inputs and configurations back to their default factory state.
    Exits demo mode securely and clears any active analysis run.
    """
    cancel_analysis_submission(st.session_state)
    st.session_state.is_demo_mode = False
    st.session_state.val_callsign = ""
    st.session_state.val_analysis_direction = None
    st.session_state.val_qth = ""
    st.session_state.val_band = DEFAULT_BAND
    st.session_state.val_time_mode = "last_x"
    st.session_state.val_hours = 24
    st.session_state.val_solar = "all"
    st.session_state.val_comp_mode = "none"
    st.session_state.val_ref_stations = 10
    st.session_state.val_ref_radius_km = 100
    st.session_state.val_benchmark_offset_db = 0.0
    st.session_state.val_snr_correction_mode = "no_offset"
    st.session_state.val_local_benchmark = "local_median"
    st.session_state.val_ref_callsign = ""
    st.session_state.val_ref_qth = ""
    st.session_state.val_tx_ab_method = "simultaneous"
    st.session_state.val_tx_ab_repeat_interval_minutes = 10
    st.session_state.val_tx_ab_target_start_minute = 0
    st.session_state.val_tx_ab_reference_start_minute = 2
    st.session_state.val_max_peer_distance_km = 22000
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
    st.session_state.guided_use_case = None
    st.session_state.guided_reference_design = None
    st.session_state.guided_last_compare_mode = None
    st.session_state.guided_scope_mode = "general"
    st.session_state.guided_active_node = "use_case"
    st.session_state.guided_reconstruct_requested = False
    st.session_state.guided_demo_metadata_open = False
    st.session_state.guided_loaded_demo_profile = None
    st.session_state.guided_collapse_all = False
    st.session_state.configuration_changed_since_run = False
    reset_result_state(st.session_state)
    for state_key in tuple(st.session_state.keys()):
        if state_key.startswith("config_save_"):
            st.session_state.pop(state_key, None)

def set_demo_config():
    """
    Activates the Guided Sandbox demo mode. Locks core UI elements against 
    unwanted edits and loads the initial demographic profile.
    """
    cancel_analysis_submission(st.session_state)
    st.session_state.is_demo_mode = True
    st.session_state.run_mode = None
    apply_demo_profile()
