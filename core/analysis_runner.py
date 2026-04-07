"""
Analysis Runner Module.
Handles the construction of complex ClickHouse SQL queries based on user UI state,
and provides data-filtering utilities (Solar) before plotting.
"""

import pandas as pd
import numpy as np
import streamlit as st
from config import MAX_DYNAMIC_RADIUS_KM
from core.data_engine import fetch_wspr_data
from core.math_utils import get_solar_state, is_valid_callsign

def build_analysis_batches(t, start_t, end_t, lat_0, lon_0, band_filter, callsign):
    """
    Reads the user configuration from the session state and generates the necessary
    SQL queries and execution batches for the map plots (Absolute & Comparison).
    """
    # --- Defense-in-depth: validate callsign before any SQL is assembled ---
    if not is_valid_callsign(callsign):
        st.error(f"Invalid callsign '{callsign}'. Only A–Z, 0–9, and '/' are allowed (3–15 characters).")
        return []

    comp_mode = st.session_state.val_comp_mode
    is_demo_run = st.session_state.get("is_demo_mode", False)
    time_filter = f"time BETWEEN '{start_t.strftime('%Y-%m-%d %H:%M:%S')}' AND '{end_t.strftime('%Y-%m-%d %H:%M:%S')}'"
    
    is_sequential = False
    
    # Determine Reference / Buddy Parameters
    if comp_mode == t["opt_comp_radius"]:
        ref_stations = st.session_state.val_ref_stations
    elif comp_mode == t["opt_comp_buddy"]:
        ref_callsign = st.session_state.val_ref_callsign.upper().strip()
        if not is_valid_callsign(ref_callsign):
            st.error(f"Invalid reference callsign '{ref_callsign}'. Only A–Z, 0–9, and '/' are allowed (3–15 characters).")
            return []
    elif comp_mode == t["opt_comp_self"]:
        ref_callsign = callsign  # defaults to target callsign (already validated above)
        if st.session_state.val_self_test_mode == t["opt_self_tx"]:
            is_sequential = True
        elif st.session_state.val_self_test_mode == t["opt_self_rx"]:
            ref_callsign = st.session_state.val_self_call_b.upper().strip()
            if not is_valid_callsign(ref_callsign):
                st.error(f"Invalid Setup B callsign '{ref_callsign}'. Only A–Z, 0–9, and '/' are allowed (3–15 characters).")
                return []
    
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

    # --- Explicit Synchronization Layer ---
    # Dank HTTP POST in der data_engine sind wir nicht mehr an URL-Längenlimits gebunden.
    # Wir können die aktiven Zyklen bequem vorladen und als Liste einfügen, 
    # was die geforderte ClickHouse Subquery-Tiefe massiv reduziert!
    
    tx_cycle_filter = ""
    if st.session_state.run_mode == "TX" and not is_sequential:
        sync_msg = "Synchronisiere TX Zyklen..." if st.session_state.lang == "de" else "Syncing TX cycles..."
        with st.spinner(sync_msg):
            tx_cycles_query = f"SELECT DISTINCT floor(toUnixTimestamp(time)/120) AS ts FROM wspr.rx WHERE {tx_target_sql} AND rx_lat != 0 FORMAT CSVWithNames"
            tx_cycles_df = fetch_wspr_data(tx_cycles_query, is_demo=is_demo_run)
            tx_cycle_filter = f"AND floor(toUnixTimestamp(time)/120) IN ({','.join(tx_cycles_df['ts'].astype(int).astype(str))})" if tx_cycles_df is not None and not tx_cycles_df.empty else "AND 1=0"

    rx_cycle_filter = ""
    if st.session_state.run_mode == "RX" and not is_sequential:
        sync_msg = "Synchronisiere RX Zyklen..." if st.session_state.lang == "de" else "Syncing RX cycles..."
        with st.spinner(sync_msg):
            rx_cycles_query = f"SELECT DISTINCT floor(toUnixTimestamp(time)/120) AS ts FROM wspr.rx WHERE {rx_target_sql} AND tx_lat != 0 FORMAT CSVWithNames"
            rx_cycles_df = fetch_wspr_data(rx_cycles_query, is_demo=is_demo_run)
            rx_cycle_filter = f"AND floor(toUnixTimestamp(time)/120) IN ({','.join(rx_cycles_df['ts'].astype(int).astype(str))})" if rx_cycles_df is not None and not rx_cycles_df.empty else "AND 1=0"

    # --- Explicit Synchronization Layer ---
    # Moved to Pandas (apply_post_fetch_filters) to avoid ClickHouse Subquery Depth Limits (162)
    # and HTTP 414 URL Length limits. This makes the database queries radically faster.

    # --- Peer SQL Filters ---
    if comp_mode == t["opt_comp_radius"]:
        ref_stations = st.session_state.val_ref_stations
        max_rad = MAX_DYNAMIC_RADIUS_KM * 1000
        
        # PRE-FILTER BOUNDING BOX: Hält die geoDistance Berechnung extrem billig
        lat_diff = MAX_DYNAMIC_RADIUS_KM / 111.0
        lon_diff = MAX_DYNAMIC_RADIUS_KM / (111.0 * np.cos(np.radians(lat_0)))
        
        bbox_tx = f"AND tx_lat BETWEEN {lat_0 - lat_diff} AND {lat_0 + lat_diff} AND tx_lon BETWEEN {lon_0 - lon_diff} AND {lon_0 + lon_diff}"
        bbox_rx = f"AND rx_lat BETWEEN {lat_0 - lat_diff} AND {lat_0 + lat_diff} AND rx_lon BETWEEN {lon_0 - lon_diff} AND {lon_0 + lon_diff}"
        
        # Extrem flache GLOBAL IN Abfrage (Depth = 2, erlaubt Limit von wspr.live)
        # ClickHouse gruppiert hier autark und blitzschnell die N nächsten Stationen pro Zyklus.
        tx_peer_sql = f"tx_sign NOT LIKE '{callsign}%' {band_filter} AND {time_filter} {bbox_tx} AND (floor(toUnixTimestamp(time)/120), tx_sign) GLOBAL IN (SELECT floor(toUnixTimestamp(time)/120) AS ts, tx_sign FROM wspr.rx WHERE tx_sign NOT LIKE '{callsign}%' {band_filter} AND {time_filter} {bbox_tx} AND tx_lat != 0 AND tx_lon != 0 GROUP BY ts, tx_sign HAVING geoDistance({lon_0}, {lat_0}, any(tx_lon), any(tx_lat)) <= {max_rad} ORDER BY geoDistance({lon_0}, {lat_0}, any(tx_lon), any(tx_lat)) ASC LIMIT {ref_stations} BY ts)"
        
        rx_peer_sql = f"rx_sign NOT LIKE '{callsign}%' {band_filter} AND {time_filter} {bbox_rx} AND (floor(toUnixTimestamp(time)/120), rx_sign) GLOBAL IN (SELECT floor(toUnixTimestamp(time)/120) AS ts, rx_sign FROM wspr.rx WHERE rx_sign NOT LIKE '{callsign}%' {band_filter} AND {time_filter} {bbox_rx} AND rx_lat != 0 AND rx_lon != 0 GROUP BY ts, rx_sign HAVING geoDistance({lon_0}, {lat_0}, any(rx_lon), any(rx_lat)) <= {max_rad} ORDER BY geoDistance({lon_0}, {lat_0}, any(rx_lon), any(rx_lat)) ASC LIMIT {ref_stations} BY ts)"
        
        comp_title = t["comp_title_ref_radius"].format(stations=ref_stations)
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
            tx_comp_query = f"SELECT floor(toUnixTimestamp(time)/120) AS time_slot, peer_sign, any(peer_grid) AS peer_grid, any(peer_lat) AS peer_lat, any(peer_lon) AS peer_lon, maxIf(snr - power + 30, is_me = 1) AS snr_u_norm, maxIf(snr - power + 30, is_me = 0) AS snr_r_norm, countIf(is_me = 1) AS has_u, countIf(is_me = 0) AS has_r, argMaxIf(local_sign, snr - power + 30, is_me = 0) AS best_ref_sign, argMaxIf(local_dist, snr - power + 30, is_me = 0) AS best_ref_dist FROM (SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, tx_sign AS local_sign, 0.0 AS local_dist, snr, power, 1 AS is_me FROM wspr.rx WHERE {tx_target_sql} AND rx_lat != 0 UNION ALL SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, tx_sign AS local_sign, geoDistance({lon_0}, {lat_0}, tx_lon, tx_lat) AS local_dist, snr, power, 0 AS is_me FROM wspr.rx WHERE {tx_peer_sql} AND rx_lat != 0) GROUP BY time_slot, peer_sign FORMAT CSVWithNames"        
        analyses.append({"id": "TX_COMP", "title": t["fig_tx_comp"].format(callsign=display_callsign, comp_title=comp_title), "is_compare": True, "is_sequential": is_sequential, "query": tx_comp_query})

    elif st.session_state.run_mode == "RX":
        analyses.append({
            "id": "RX_ABS", "title": t["fig_rx_abs"].format(callsign=callsign), "is_compare": False, "is_sequential": False,
            "query": f"SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val FROM wspr.rx WHERE {rx_target_sql} {slot_sql_u} AND tx_lat != 0 FORMAT CSVWithNames"
        })
        if is_sequential:
            rx_comp_query = f"SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val, 1 AS is_me FROM wspr.rx WHERE {rx_target_sql} {slot_sql_u} AND tx_lat != 0 UNION ALL SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val, 0 AS is_me FROM wspr.rx WHERE {rx_peer_sql} {slot_sql_r} AND tx_lat != 0 FORMAT CSVWithNames"
        else:
            rx_comp_query = f"SELECT floor(toUnixTimestamp(time)/120) AS time_slot, peer_sign, any(peer_grid) AS peer_grid, any(peer_lat) AS peer_lat, any(peer_lon) AS peer_lon, maxIf(snr - power + 30, is_me = 1) AS snr_u_norm, maxIf(snr - power + 30, is_me = 0) AS snr_r_norm, countIf(is_me = 1) AS has_u, countIf(is_me = 0) AS has_r, argMaxIf(local_sign, snr - power + 30, is_me = 0) AS best_ref_sign, argMaxIf(local_dist, snr - power + 30, is_me = 0) AS best_ref_dist FROM (SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, rx_sign AS local_sign, 0.0 AS local_dist, snr, power, 1 AS is_me FROM wspr.rx WHERE {rx_target_sql} AND tx_lat != 0 UNION ALL SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, rx_sign AS local_sign, geoDistance({lon_0}, {lat_0}, rx_lon, rx_lat) AS local_dist, snr, power, 0 AS is_me FROM wspr.rx WHERE {rx_peer_sql} AND tx_lat != 0) GROUP BY time_slot, peer_sign FORMAT CSVWithNames"        
        analyses.append({"id": "RX_COMP", "title": t["fig_rx_comp"].format(callsign=display_callsign, comp_title=comp_title), "is_compare": True, "is_sequential": is_sequential, "query": rx_comp_query})

    return analyses

def apply_post_fetch_filters(df, analysis, lat_0, lon_0, t):
    """
    Applies mathematical and logical filters (Solar) to the fetched dataframe
    before it is handed over to the plotting engine.
    Note: The global min-spots filter has been removed from this stage to allow 
    for strict, symmetric statistical classification downstream in the plot engine.
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

    # NO global spot filtering here anymore. Filtering is strictly enforced in plot_engine.py
    return df, None