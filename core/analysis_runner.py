"""
Analysis Runner Module.
Handles the construction of complex ClickHouse SQL queries based on user UI state,
and provides data-filtering utilities (Solar, Min-Spots) before plotting.
"""

import pandas as pd
import numpy as np
import streamlit as st
from core.data_engine import fetch_wspr_data
from core.math_utils import get_solar_state

def build_analysis_batches(t, start_t, end_t, lat_0, lon_0, band_filter, callsign):
    """
    Reads the user configuration from the session state and generates the necessary
    SQL queries and execution batches for the map plots (Absolute & Comparison).
    """
    comp_mode = st.session_state.val_comp_mode
    is_demo_run = st.session_state.get("is_demo_mode", False)
    time_filter = f"time BETWEEN '{start_t.strftime('%Y-%m-%d %H:%M:%S')}' AND '{end_t.strftime('%Y-%m-%d %H:%M:%S')}'"
    
    is_sequential = False
    
    # Determine Reference / Buddy Parameters
    if comp_mode == t["opt_comp_radius"]:
        ref_radius = st.session_state.val_ref_radius
    elif comp_mode == t["opt_comp_buddy"]:
        ref_callsign = st.session_state.val_ref_callsign.upper()
    elif comp_mode == t["opt_comp_self"]:
        ref_callsign = callsign
        if st.session_state.val_self_test_mode == t["opt_self_tx"]:
            is_sequential = True
        elif st.session_state.val_self_test_mode == t["opt_self_rx"]:
            ref_callsign = st.session_state.val_self_call_b
    
    def get_slot_sql(slot_val):
        if slot_val == t["opt_slot_even"]: return "AND toMinute(time) % 4 = 0"
        if slot_val == t["opt_slot_odd"]: return "AND toMinute(time) % 4 = 2"
        return ""

    slot_sql_u = get_slot_sql(st.session_state.val_slot_u) if is_sequential else ""
    slot_sql_r = get_slot_sql(st.session_state.val_slot_r) if is_sequential else ""
    
    # Target SQL Filters
    if comp_mode == t["opt_comp_self"] and st.session_state.val_self_test_mode == t["opt_self_rx"]:
        # Strict exact match needed to prevent 'DL1MKS%' from swallowing 'DL1MKS/P' spots
        tx_target_sql = f"tx_sign = '{callsign}' {band_filter} AND {time_filter}"
        rx_target_sql = f"rx_sign = '{callsign}' {band_filter} AND {time_filter}"
    else:
        tx_target_sql = f"tx_sign LIKE '{callsign}%' {band_filter} AND {time_filter}"
        rx_target_sql = f"rx_sign LIKE '{callsign}%' {band_filter} AND {time_filter}"

    # Peer SQL Filters
    if comp_mode == t["opt_comp_radius"]:
        lat_diff, lon_diff = ref_radius / 111.0, ref_radius / (111.0 * np.cos(np.radians(lat_0)))
        tx_peer_sql = f"tx_sign NOT LIKE '{callsign}%' {band_filter} AND tx_lat BETWEEN {lat_0 - lat_diff} AND {lat_0 + lat_diff} AND tx_lon BETWEEN {lon_0 - lon_diff} AND {lon_0 + lon_diff} AND {time_filter}"
        rx_peer_sql = f"rx_sign NOT LIKE '{callsign}%' {band_filter} AND rx_lat BETWEEN {lat_0 - lat_diff} AND {lat_0 + lat_diff} AND rx_lon BETWEEN {lon_0 - lon_diff} AND {lon_0 + lon_diff} AND {time_filter}"
        comp_title = t["comp_title_ref_radius"].format(radius=ref_radius)
        display_callsign = callsign
    else:
        if comp_mode == t["opt_comp_self"] and st.session_state.val_self_test_mode == t["opt_self_rx"]:
            tx_peer_sql = f"tx_sign = '{ref_callsign}' {band_filter} AND {time_filter}"
            rx_peer_sql = f"rx_sign = '{ref_callsign}' {band_filter} AND {time_filter}"
        else:
            tx_peer_sql = f"tx_sign LIKE '{ref_callsign}%' {band_filter} AND {time_filter}"
            rx_peer_sql = f"rx_sign LIKE '{ref_callsign}%' {band_filter} AND {time_filter}"
            
        if comp_mode == t["opt_comp_self"]:
            if st.session_state.val_self_test_mode == t["opt_self_rx"]:
                display_callsign = f"{callsign} (Setup A)"
                comp_title = f"{ref_callsign} (Setup B)"
            else:
                display_callsign = f"{callsign} (Setup A)"
                comp_title = f"{callsign} (Setup B)"
        else:
            display_callsign = callsign
            comp_title = t["comp_title_ref"].format(callsign=ref_callsign)

    rx_cycle_filter = ""
    # Explicit synchronization layer for RX tests
    if st.session_state.run_mode == "RX" and not is_sequential:
        with st.spinner(t["msg_sync"]):
            rx_cycles_query = f"SELECT DISTINCT floor(toUnixTimestamp(time)/120) AS ts FROM wspr.rx WHERE {rx_target_sql} AND tx_lat != 0 FORMAT CSVWithNames"
            rx_cycles_df = fetch_wspr_data(rx_cycles_query, is_demo=is_demo_run)
            rx_cycle_filter = f"AND floor(toUnixTimestamp(time)/120) IN ({','.join(rx_cycles_df['ts'].astype(int).astype(str))})" if rx_cycles_df is not None and not rx_cycles_df.empty else "AND 1=0"

    # Assemble Analysis Batches
    analyses = []
    
    if st.session_state.run_mode == "TX":
        analyses.append({
            "id": "TX_ABS", "title": t["fig_tx_abs"].format(callsign=callsign), "is_compare": False, "is_sequential": False,
            "query": f"SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val FROM wspr.rx WHERE {tx_target_sql} {slot_sql_u} AND rx_lat != 0 FORMAT CSVWithNames"
        })
        if is_sequential:
            tx_comp_query = f"SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val, 1 AS is_me FROM wspr.rx WHERE {tx_target_sql} {slot_sql_u} AND rx_lat != 0 UNION ALL SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val, 0 AS is_me FROM wspr.rx WHERE {tx_peer_sql} {slot_sql_r} AND rx_lat != 0 FORMAT CSVWithNames"
        else:
            tx_comp_query = f"SELECT floor(toUnixTimestamp(time)/120) AS time_slot, peer_sign, any(peer_grid) AS peer_grid, any(peer_lat) AS peer_lat, any(peer_lon) AS peer_lon, maxIf(snr - power + 30, is_me = 1) AS snr_u_norm, maxIf(snr - power + 30, is_me = 0) AS snr_r_norm, countIf(is_me = 1) AS has_u, countIf(is_me = 0) AS has_r FROM (SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, snr, power, 1 AS is_me FROM wspr.rx WHERE {tx_target_sql} AND rx_lat != 0 UNION ALL SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, snr, power, 0 AS is_me FROM wspr.rx WHERE {tx_peer_sql} AND rx_lat != 0) GROUP BY time_slot, peer_sign FORMAT CSVWithNames"
        
        analyses.append({"id": "TX_COMP", "title": t["fig_tx_comp"].format(callsign=display_callsign, comp_title=comp_title), "is_compare": True, "is_sequential": is_sequential, "query": tx_comp_query})

    elif st.session_state.run_mode == "RX":
        analyses.append({
            "id": "RX_ABS", "title": t["fig_rx_abs"].format(callsign=callsign), "is_compare": False, "is_sequential": False,
            "query": f"SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val FROM wspr.rx WHERE {rx_target_sql} {slot_sql_u} AND tx_lat != 0 FORMAT CSVWithNames"
        })
        if is_sequential:
            rx_comp_query = f"SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val, 1 AS is_me FROM wspr.rx WHERE {rx_target_sql} {slot_sql_u} AND tx_lat != 0 UNION ALL SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val, 0 AS is_me FROM wspr.rx WHERE {rx_peer_sql} {slot_sql_r} AND tx_lat != 0 FORMAT CSVWithNames"
        else:
            rx_comp_query = f"SELECT floor(toUnixTimestamp(time)/120) AS time_slot, peer_sign, any(peer_grid) AS peer_grid, any(peer_lat) AS peer_lat, any(peer_lon) AS peer_lon, maxIf(snr - power + 30, is_me = 1) AS snr_u_norm, maxIf(snr - power + 30, is_me = 0) AS snr_r_norm, countIf(is_me = 1) AS has_u, countIf(is_me = 0) AS has_r FROM (SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, 1 AS is_me FROM wspr.rx WHERE {rx_target_sql} AND tx_lat != 0 UNION ALL SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, 0 AS is_me FROM wspr.rx WHERE {rx_peer_sql} {rx_cycle_filter} AND tx_lat != 0) GROUP BY time_slot, peer_sign FORMAT CSVWithNames"
        
        analyses.append({"id": "RX_COMP", "title": t["fig_rx_comp"].format(callsign=display_callsign, comp_title=comp_title), "is_compare": True, "is_sequential": is_sequential, "query": rx_comp_query})

    return analyses

def apply_post_fetch_filters(df, analysis, lat_0, lon_0, t):
    """
    Applies mathematical and logical filters (Solar, Min-Spots) to the fetched dataframe
    before it is handed over to the plotting engine.
    Returns the filtered dataframe and an optional warning string if data was depleted.
    """
    # Apply Solar Filtering locally
    if st.session_state.val_solar != t["opt_solar_all"]:
        if analysis['is_compare'] and not analysis['is_sequential']: 
            df['dt_time'] = pd.to_datetime(df['time_slot'] * 120, unit='s')
        else: 
            df['dt_time'] = pd.to_datetime(df['time'])
            
        df['solar'] = df['dt_time'].apply(lambda dt: get_solar_state(dt, lat_0, lon_0))
        target_state = 'day' if st.session_state.val_solar == t["opt_solar_day"] else ('night' if st.session_state.val_solar == t["opt_solar_night"] else 'grey')
        df = df[df['solar'] == target_state]
        
        if df.empty:
            return df, t["warn_no_data"].format(title=analysis['title'])

    # Apply Global Min. Spots Filter (Unique Cycles)
    min_spots = st.session_state.val_min_spots
    if min_spots > 1:
        if 'time_slot' in df.columns:
            cycle_col = 'time_slot'
        else:
            df['tmp_cycle'] = (pd.to_datetime(df['time'], utc=True) - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta('120s')
            cycle_col = 'tmp_cycle'
        
        unique_cycles = df.groupby('peer_sign')[cycle_col].nunique()
        valid_peers = unique_cycles[unique_cycles >= min_spots].index
        df = df[df['peer_sign'].isin(valid_peers)]
        
        if 'tmp_cycle' in df.columns:
            df = df.drop(columns=['tmp_cycle'])
        
        if df.empty:
            return df, f"Keine Stationen mit mindestens {min_spots} Spots (Zyklen) gefunden für {analysis['title']}."

    return df, None