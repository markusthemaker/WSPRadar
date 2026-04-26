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
        st.error(f"Invalid callsign '{callsign}'. Only A?Z, 0?9, and '/' are allowed (3?15 characters).")
        return []

    comp_mode = st.session_state.val_comp_mode
    is_demo_run = st.session_state.get("is_demo_mode", False)
    time_filter = f"time BETWEEN '{start_t.strftime('%Y-%m-%d %H:%M:%S')}' AND '{end_t.strftime('%Y-%m-%d %H:%M:%S')}'"
    
    # --- Prefix Exclusion Filter ---
    # Dynamically appends NOT LIKE filters to the global time_filter to ensure 
    # telemetry balloons are purged from all layers (Subqueries & Outer Queries)
    if "val_exclude_prefixes" in st.session_state and st.session_state.val_exclude_prefixes.strip():
        prefixes = [p.strip().upper() for p in st.session_state.val_exclude_prefixes.split(',') if p.strip()]
        for p in prefixes:
            if p.isalnum():  # Basic sanitization
                time_filter += f" AND tx_sign NOT LIKE '{p}%' AND rx_sign NOT LIKE '{p}%'"
    
    is_sequential = False
    
    # Determine Reference / Buddy Parameters
    if comp_mode == t["opt_comp_radius"]:
        ref_radius_km = min(st.session_state.get("val_ref_radius_km", MAX_DYNAMIC_RADIUS_KM), MAX_DYNAMIC_RADIUS_KM)
    elif comp_mode == t["opt_comp_buddy"]:
        ref_callsign = st.session_state.val_ref_callsign.upper().strip()
        if not is_valid_callsign(ref_callsign):
            st.error(f"Invalid reference callsign '{ref_callsign}'. Only A?Z, 0?9, and '/' are allowed (3?15 characters).")
            return []
    elif comp_mode == t["opt_comp_self"]:
        ref_callsign = callsign  # defaults to target callsign (already validated above)
        if st.session_state.val_self_test_mode == t["opt_self_tx"]:
            is_sequential = True
        elif st.session_state.val_self_test_mode == t["opt_self_rx"]:
            ref_callsign = st.session_state.val_self_call_b.upper().strip()
            if not is_valid_callsign(ref_callsign):
                st.error(f"Invalid Setup B callsign '{ref_callsign}'. Only A?Z, 0?9, and '/' are allowed (3?15 characters).")
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
    # Dank HTTP POST in der data_engine sind wir nicht mehr an URL-L?ngenlimits gebunden.
    # Wir k?nnen die aktiven Zyklen bequem vorladen und als Liste einf?gen, 
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
        ref_radius_km = min(st.session_state.get("val_ref_radius_km", MAX_DYNAMIC_RADIUS_KM), MAX_DYNAMIC_RADIUS_KM)
        local_benchmark = st.session_state.get("val_local_benchmark", t["opt_local_median"])
        is_local_median = local_benchmark == t["opt_local_median"]
        max_rad = ref_radius_km * 1000
        
        # PRE-FILTER BOUNDING BOX: H?lt die geoDistance Berechnung extrem billig
        lat_diff = ref_radius_km / 111.0
        lon_diff = ref_radius_km / (111.0 * max(abs(np.cos(np.radians(lat_0))), 0.01))
        
        bbox_tx = f"AND tx_lat BETWEEN {lat_0 - lat_diff} AND {lat_0 + lat_diff} AND tx_lon BETWEEN {lon_0 - lon_diff} AND {lon_0 + lon_diff}"
        bbox_rx = f"AND rx_lat BETWEEN {lat_0 - lat_diff} AND {lat_0 + lat_diff} AND rx_lon BETWEEN {lon_0 - lon_diff} AND {lon_0 + lon_diff}"
        
        tx_peer_sql = f"tx_sign NOT LIKE '{callsign}%' {band_filter} AND {time_filter} {bbox_tx} AND tx_lat != 0 AND tx_lon != 0 AND geoDistance({lon_0}, {lat_0}, tx_lon, tx_lat) <= {max_rad}"
        
        rx_peer_sql = f"rx_sign NOT LIKE '{callsign}%' {band_filter} AND {time_filter} {bbox_rx} AND rx_lat != 0 AND rx_lon != 0 AND geoDistance({lon_0}, {lat_0}, rx_lon, rx_lat) <= {max_rad}"
        
        if is_local_median:
            comp_title = t["comp_title_local_median"].format(radius=ref_radius_km)
        else:
            comp_title = t["comp_title_local_best"].format(radius=ref_radius_km)
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
    local_ref_snr_sql = "maxIf(snr - power + 30, is_me = 0)"
    local_ref_sign_sql = "argMaxIf(local_sign, snr - power + 30, is_me = 0)"
    local_ref_dist_sql = "argMaxIf(local_dist, snr - power + 30, is_me = 0)"
    local_ref_detail_sql = ""
    if comp_mode == t["opt_comp_radius"] and st.session_state.get("val_local_benchmark", t["opt_local_median"]) == t["opt_local_median"]:
        local_ref_snr_sql = "quantileExactInclusiveIf(0.5)(snr - power + 30, is_me = 0)"
        local_ref_sign_sql = "concat(toString(countIf(is_me = 0)), ' stations')"
        local_ref_dist_sql = "quantileExactInclusiveIf(0.5)(local_dist, is_me = 0)"
        local_ref_detail_sql = ", groupArrayIf(tuple(local_sign, local_grid, local_dist, snr - power + 30), is_me = 0) AS ref_detail_rows"
    
    if st.session_state.run_mode == "TX":
        analyses.append({
            "id": "TX_ABS", "title": t["fig_tx_abs"].format(callsign=callsign), "is_compare": False, "is_sequential": False,
            "query": f"SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val FROM wspr.rx WHERE {tx_target_sql} {slot_sql_u} AND rx_lat != 0 FORMAT CSVWithNames"
        })
        if is_sequential:
            tx_comp_query = f"SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val, 1 AS is_me FROM wspr.rx WHERE {tx_target_sql} {slot_sql_u} AND rx_lat != 0 UNION ALL SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val, 0 AS is_me FROM wspr.rx WHERE {tx_peer_sql} {slot_sql_r} AND rx_lat != 0 FORMAT CSVWithNames"
        else:
            tx_comp_query = f"SELECT floor(toUnixTimestamp(time)/120) AS time_slot, peer_sign, any(peer_grid) AS peer_grid, any(peer_lat) AS peer_lat, any(peer_lon) AS peer_lon, maxIf(snr - power + 30, is_me = 1) AS snr_u_norm, {local_ref_snr_sql} AS snr_r_norm, countIf(is_me = 1) AS has_u, countIf(is_me = 0) AS has_r, {local_ref_sign_sql} AS best_ref_sign, {local_ref_dist_sql} AS best_ref_dist{local_ref_detail_sql} FROM (SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, tx_sign AS local_sign, tx_loc AS local_grid, 0.0 AS local_dist, snr, power, 1 AS is_me FROM wspr.rx WHERE {tx_target_sql} AND rx_lat != 0 UNION ALL SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, rx_lon AS peer_lon, tx_sign AS local_sign, tx_loc AS local_grid, geoDistance({lon_0}, {lat_0}, tx_lon, tx_lat) AS local_dist, snr, power, 0 AS is_me FROM wspr.rx WHERE {tx_peer_sql} AND rx_lat != 0) GROUP BY time_slot, peer_sign FORMAT CSVWithNames"        
        analyses.append({"id": "TX_COMP", "title": t["fig_tx_comp"].format(callsign=display_callsign, comp_title=comp_title), "is_compare": True, "is_sequential": is_sequential, "query": tx_comp_query})

    elif st.session_state.run_mode == "RX":
        analyses.append({
            "id": "RX_ABS", "title": t["fig_rx_abs"].format(callsign=callsign), "is_compare": False, "is_sequential": False,
            "query": f"SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val FROM wspr.rx WHERE {rx_target_sql} {slot_sql_u} AND tx_lat != 0 FORMAT CSVWithNames"
        })
        if is_sequential:
            rx_comp_query = f"SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val, 1 AS is_me FROM wspr.rx WHERE {rx_target_sql} {slot_sql_u} AND tx_lat != 0 UNION ALL SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, snr, power, (snr - power + 30) AS stat_val, 0 AS is_me FROM wspr.rx WHERE {rx_peer_sql} {slot_sql_r} AND tx_lat != 0 FORMAT CSVWithNames"
        else:
            rx_comp_query = f"SELECT floor(toUnixTimestamp(time)/120) AS time_slot, peer_sign, any(peer_grid) AS peer_grid, any(peer_lat) AS peer_lat, any(peer_lon) AS peer_lon, maxIf(snr - power + 30, is_me = 1) AS snr_u_norm, {local_ref_snr_sql} AS snr_r_norm, countIf(is_me = 1) AS has_u, countIf(is_me = 0) AS has_r, {local_ref_sign_sql} AS best_ref_sign, {local_ref_dist_sql} AS best_ref_dist{local_ref_detail_sql} FROM (SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, rx_sign AS local_sign, rx_loc AS local_grid, 0.0 AS local_dist, snr, power, 1 AS is_me FROM wspr.rx WHERE {rx_target_sql} AND tx_lat != 0 UNION ALL SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, tx_lon AS peer_lon, rx_sign AS local_sign, rx_loc AS local_grid, geoDistance({lon_0}, {lat_0}, rx_lon, rx_lat) AS local_dist, snr, power, 0 AS is_me FROM wspr.rx WHERE {rx_peer_sql} AND tx_lat != 0) GROUP BY time_slot, peer_sign FORMAT CSVWithNames"        
        analyses.append({"id": "RX_COMP", "title": t["fig_rx_comp"].format(callsign=display_callsign, comp_title=comp_title), "is_compare": True, "is_sequential": is_sequential, "query": rx_comp_query})

    return analyses

def apply_post_fetch_filters(df, analysis, lat_0, lon_0, t):
    """
    Applies mathematical and logical filters (Solar, Cycle-Sync, Moving Stations) 
    to the fetched dataframe before it is handed over to the plotting engine.
    """
    # --- 1. SOLAR FILTERING ---
    if st.session_state.val_solar != t["opt_solar_all"]:
        if analysis['is_compare'] and not analysis['is_sequential']: 
            df['dt_time'] = pd.to_datetime(df['time_slot'] * 120, unit='s')
        else: 
            df['dt_time'] = pd.to_datetime(df['time'])
            
        df['solar'] = df['dt_time'].apply(lambda dt: get_solar_state(dt, lat_0, lon_0))
        target_state = 'day' if st.session_state.val_solar == t["opt_solar_day"] else ('night' if st.session_state.val_solar == t["opt_solar_night"] else 'grey')
        df = df[df['solar'] == target_state]

    # --- 2. EXCLUDE MOVING STATIONS ---
    # Entfernt alle Gegenstationen, die mehr als ein 4-stelliges Grid in der Zeitperiode melden (Ballons, /M, /MM)
    if st.session_state.get("val_filter_moving", False) and not df.empty and 'peer_grid' in df.columns:
        # Extrahiere die ersten 4 Zeichen (um JN37 und JN37AB als "identisch" zu behandeln)
        grid4 = df['peer_grid'].astype(str).str[:4]
        # Finde Stationen, die exakt 1 eindeutiges 4er-Grid haben
        static_peers = df.assign(g4=grid4).groupby('peer_sign')['g4'].nunique()[lambda x: x == 1].index
        # Filtere den DataFrame
        df = df[df['peer_sign'].isin(static_peers)]

    
    # --- 3. VECTORIZED CYCLE SYNCHRONIZATION (RX & TX) ---
    # Verhindert massive "Offline-Strafen"! Ein Zyklus wird nur gewertet, wenn Setup A nachweislich aktiv war.
    # Bei TX: Transceiver muss in diesem Zyklus gesendet haben (mind. 1 Spot weltweit).
    # Bei RX: Empf?nger muss online gewesen sein (mind. 1 Spot von irgendwem weltweit empfangen).
    if analysis['is_compare'] and not analysis['is_sequential'] and 'has_u' in df.columns:
        active_slots = df[df['has_u'] > 0]['time_slot'].unique()
        df = df[df['time_slot'].isin(active_slots)]
    
    # --- 3. VECTORIZED CYCLE SYNCHRONIZATION (STRICTLY TX ONLY) ---
    # Im RX-Vergleich bedeutet "0 Spots" eine taube Antenne (wir behalten (!!!) den Zyklus als Niederlage). 
    # Im TX-Vergleich bedeutet "0 Spots", dass nicht gesendet wurde (wir l?schen den Zyklus aus Fairness).
    #is_tx = analysis['id'].startswith("TX")
    #if analysis['is_compare'] and not analysis['is_sequential'] and is_tx and 'has_u' in df.columns:
        #active_slots = df[df['has_u'] > 0]['time_slot'].unique()
        #df = df[df['time_slot'].isin(active_slots)]

    if df.empty:
        return df, t["warn_no_data"].format(title=analysis['title'])

    return df, None
