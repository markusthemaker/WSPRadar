"""
Config Panel Components Module.
Contains the UI rendering functions for the main configuration expanders.
Separating this from app.py keeps the main orchestrator file clean and focused.
"""

import streamlit as st
from datetime import datetime, timedelta, timezone
from config import MAX_DAYS_HISTORY, DEMO_PROFILES
from ui.callbacks import (
    reset_audit, handle_comp_mode_change, handle_self_test_mode_change,
    swap_tx_slots_u, swap_tx_slots_r
)

def render_core_expander(t):
    """Renders the first expander: Core Parameters (Callsign, Grid, Time, Band)."""
    with st.expander(t["exp_core"], expanded=True):
        # Zeile 1: Callsign & Time Mode
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.text_input(t["lbl_callsign"], key="val_callsign", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
        with r1c2:
            st.radio(t["lbl_time_mode"], [t["opt_last_x"], t["opt_custom"]], key="val_time_mode", horizontal=True, disabled=st.session_state.is_demo_mode, on_change=reset_audit)

        # Zeile 2 & 3: Dynamisches Layout basierend auf Zeitmodus
        if st.session_state.val_time_mode == t["opt_last_x"]:
            r2c1, r2c2 = st.columns(2)
            with r2c1: st.text_input(t["lbl_qth"], key="val_qth", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
            with r2c2: st.slider(t["lbl_hours"], 1, 168, key="val_hours", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
            
            r3c1, r3c2 = st.columns(2)
            with r3c1: st.selectbox(t["lbl_band"], ["160m", "80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m", "All"], key="val_band", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
            
        else:
            today_utc = datetime.now(timezone.utc).date()
            
            r2c1, r2c2, r2c3 = st.columns([0.5, 0.25, 0.25], vertical_alignment="bottom")
            with r2c1: st.text_input(t["lbl_qth"], key="val_qth", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
            with r2c2: st.date_input(t["lbl_start_d"], key="val_start_d", max_value=today_utc, disabled=st.session_state.is_demo_mode, on_change=reset_audit, format="DD-MM-YYYY")
            with r2c3:
                max_allowed_end = min(st.session_state.val_start_d + timedelta(days=MAX_DAYS_HISTORY), today_utc)
                min_allowed_end = st.session_state.val_start_d
                
                # Defensive check inside the render loop
                if st.session_state.val_end_d > max_allowed_end: st.session_state.val_end_d = max_allowed_end
                elif st.session_state.val_end_d < min_allowed_end: st.session_state.val_end_d = min_allowed_end
                
                st.date_input(t["lbl_end_d"], key="val_end_d", min_value=min_allowed_end, max_value=max_allowed_end, disabled=st.session_state.is_demo_mode, on_change=reset_audit, format="DD-MM-YYYY")

            r3c1, r3c2, r3c3 = st.columns([0.5, 0.25, 0.25], vertical_alignment="bottom")
            with r3c1: st.selectbox(t["lbl_band"], ["160m", "80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m", "All"], key="val_band", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
            with r3c2: st.time_input(t["lbl_start_t"], key="val_start_t", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
            with r3c3: st.time_input(t["lbl_end_t"], key="val_end_t", disabled=st.session_state.is_demo_mode, on_change=reset_audit)

def render_compare_expander(t):
    """Renders the second expander: The A/B Compare Engine configurations."""
    with st.expander(t["exp_comp"], expanded=True):
        col_comp_l, col_comp_r = st.columns([0.4, 0.6])
        with col_comp_l:
            st.radio(t["lbl_comp_mode"], [t["opt_comp_radius"], t["opt_comp_buddy"], t["opt_comp_self"]], key="val_comp_mode", on_change=handle_comp_mode_change)
        
        with col_comp_r:
            comp_mode = st.session_state.val_comp_mode
            callsign = st.session_state.val_callsign.upper()
            
            if comp_mode == t["opt_comp_radius"]:
                st.slider(t["lbl_radius"], 5, 50, key="val_ref_stations", disabled=st.session_state.is_demo_mode, on_change=reset_audit)         
            elif comp_mode == t["opt_comp_buddy"]:
                buddy_locked = st.session_state.is_demo_mode and bool(DEMO_PROFILES["buddy"]["ref_callsign"])
                st.text_input(t["lbl_ref_call"], key="val_ref_callsign", disabled=buddy_locked, on_change=reset_audit)
                
                # Validation error
                if st.session_state.val_ref_callsign.upper() == callsign and callsign != "":
                    st.error(t["err_self_test"])
                    
            elif comp_mode == t["opt_comp_self"]:
                disp_call = callsign if callsign else "..."
                st.radio(t["lbl_self_test_mode"].format(callsign=disp_call), [t["opt_self_rx"], t["opt_self_tx"]], key="val_self_test_mode", on_change=handle_self_test_mode_change)
                
                if st.session_state.val_self_test_mode == t["opt_self_rx"]:
                    cs1, cs2 = st.columns(2)
                    with cs1: st.text_input("Setup A Callsign (Your Callsign)", value=callsign, disabled=True)
                    with cs2: st.text_input("Setup B Callsign", key="val_self_call_b", placeholder="e.g. Callsign/P", disabled=st.session_state.is_demo_mode, on_change=reset_audit)
                    
                    self_call_b = st.session_state.val_self_call_b.upper()
                    if len(self_call_b) > 0 and self_call_b == callsign:
                        st.error("Setup B callsign must be different from Setup A (e.g., use a /P suffix).")
                else:
                    cs1, cs2 = st.columns(2)
                    with cs1: st.selectbox(t["lbl_slot_u"], [t["opt_slot_even"], t["opt_slot_odd"]], key="val_slot_u", disabled=st.session_state.is_demo_mode, on_change=swap_tx_slots_u)
                    with cs2: st.selectbox(t["lbl_slot_r"], [t["opt_slot_odd"], t["opt_slot_even"]], key="val_slot_r", disabled=st.session_state.is_demo_mode, on_change=swap_tx_slots_r)

def render_advanced_expander(t):
    """Renders the third expander: Advanced scientific configurations (Filters, Wilcoxon)."""
    with st.expander(t["exp_adv"], expanded=True):
        col3, col4 = st.columns(2)
        with col3: 
            st.selectbox(t["lbl_solar"], [t["opt_solar_all"], t["opt_solar_day"], t["opt_solar_night"], t["opt_solar_grey"]], key="val_solar", on_change=reset_audit)
            st.selectbox(t["lbl_max_dist"], [5000, 10000, 15000, 22000], key="val_max_dist", help=t["hlp_max_dist"], on_change=reset_audit)
        with col4:
            st.slider(t["lbl_min_spots"], 1, 25, key="val_min_spots", help=t["hlp_min_spots"], on_change=reset_audit)
            st.slider(t["lbl_min_stations"], 1, 20, key="val_min_stations", help=t["hlp_min_stations"], on_change=reset_audit)
            st.select_slider(t["lbl_wilcoxon"], options=["OFF", "80%", "90%", "95%", "99%"], key="val_wilcoxon", on_change=reset_audit)