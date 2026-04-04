# streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false

import io
import time
import gc
import base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.feature as cfeature
from datetime import datetime, timedelta, timezone, time as dt_time
import streamlit as st

# ==========================================
# CUSTOM MODULE IMPORTS (Separation of Concerns)
# ==========================================
from config import (
    APP_VERSION, LOGO_URL, APP_URL, DB_URL, CACHE_DIR, MAX_DAYS_HISTORY,
    COMPASS, BAND_MAP,
    DEMO_CALLSIGN, DEMO_QTH, DEMO_BAND, DEMO_START_D, DEMO_END_D, 
    DEMO_START_T, DEMO_END_T, DEMO_HOURS, DEMO_REF_RADIUS, DEMO_REF_CALLSIGN,
    DEMO_SELF_QTH_A, DEMO_SELF_QTH_B, DEMO_MAX_DIST, 
    DEMO_MIN_SPOTS, DEMO_MIN_STATIONS, DEMO_WILCOXON
)
from i18n import T
from core.math_utils import locator_to_latlon, is_valid_6char_locator, get_solar_state, quantize_time
from core.data_engine import fetch_wspr_data, cleanup_old_parquets
from core.plot_engine import generate_map_plot
from docs.pdf_generator import generate_pdf_doc, get_docs

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_base64_of_bin_file(bin_file):
    """Reads a binary image file from the local filesystem and returns its base64 encoded string."""
    try:
        with open(bin_file, 'rb') as f: 
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError: 
        return "" 

# ==========================================
# STATE MANAGEMENT & CALLBACKS
# ==========================================
def get_browser_language():
    """Attempts to determine the user's preferred language from browser request headers."""
    try:
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            accept_lang = st.context.headers.get("Accept-Language", "").lower()
            if accept_lang.startswith("de"): return "de"
    except Exception: 
        pass
    return "en"

# Initialize default session states to persist values across reruns
if "run_mode" not in st.session_state: st.session_state.run_mode = None
if "lang" not in st.session_state: st.session_state.lang = get_browser_language()
if "val_callsign" not in st.session_state: st.session_state.val_callsign = "DL1MKS"
if "val_qth" not in st.session_state: st.session_state.val_qth = "JN37"
if "val_band" not in st.session_state: st.session_state.val_band = "20m"
if "val_time_mode" not in st.session_state: st.session_state.val_time_mode = T["en"]["opt_last_x"]
if "val_hours" not in st.session_state: st.session_state.val_hours = 24
if "val_start_d" not in st.session_state: st.session_state.val_start_d = datetime.now(timezone.utc).date() - timedelta(days=1)
if "val_start_t" not in st.session_state: st.session_state.val_start_t = dt_time(0, 0)
if "val_end_d" not in st.session_state: st.session_state.val_end_d = datetime.now(timezone.utc).date()
if "val_end_t" not in st.session_state: st.session_state.val_end_t = dt_time(23, 59)
if "val_solar" not in st.session_state: st.session_state.val_solar = T["en"]["opt_solar_all"]
if "val_comp_mode" not in st.session_state: st.session_state.val_comp_mode = T["en"]["opt_comp_radius"]
if "val_ref_radius" not in st.session_state: st.session_state.val_ref_radius = 250
if "val_ref_callsign" not in st.session_state: st.session_state.val_ref_callsign = "DL2XYZ"
if "val_self_test_mode" not in st.session_state: st.session_state.val_self_test_mode = T["en"]["opt_self_rx"]
if "val_self_qth_a" not in st.session_state: st.session_state.val_self_qth_a = st.session_state.get("val_qth", "")
if "val_self_qth_b" not in st.session_state: st.session_state.val_self_qth_b = ""
if "val_slot_u" not in st.session_state: st.session_state.val_slot_u = T["en"]["opt_slot_even"]
if "val_slot_r" not in st.session_state: st.session_state.val_slot_r = T["en"]["opt_slot_odd"]
if "val_max_dist" not in st.session_state: st.session_state.val_max_dist = 22000
if "val_min_spots" not in st.session_state: st.session_state.val_min_spots = 1
if "val_min_stations" not in st.session_state: st.session_state.val_min_stations = 1
if "val_wilcoxon" not in st.session_state: st.session_state.val_wilcoxon = "OFF"

def reset_audit():
    """Cancels the active analysis and returns the app to the idle/configuration state."""
    st.session_state.run_mode = None

def swap_tx_slots_u():
    """Swaps the target's transmission time slot for Sequential A/B testing."""
    reset_audit()
    t_loc = T[st.session_state.lang]
    st.session_state.val_slot_r = t_loc["opt_slot_odd"] if st.session_state.val_slot_u == t_loc["opt_slot_even"] else t_loc["opt_slot_even"]

def swap_tx_slots_r():
    """Swaps the reference's transmission time slot for Sequential A/B testing."""
    reset_audit()
    t_loc = T[st.session_state.lang]
    st.session_state.val_slot_u = t_loc["opt_slot_odd"] if st.session_state.val_slot_r == t_loc["opt_slot_even"] else t_loc["opt_slot_even"]

def update_lang():
    """Handles UI language changes and gracefully resets dependent dropdown states."""
    lang_map = {"EN": "en", "DE": "de"}
    st.session_state.lang = lang_map[st.session_state.lang_selector_ui]
    st.session_state.val_comp_mode = T[st.session_state.lang]["opt_comp_radius"]
    st.session_state.val_self_test_mode = T[st.session_state.lang]["opt_self_rx"]
    st.session_state.run_mode = None  

def set_reset_config():
    """Resets all user inputs and configurations back to their default factory state."""
    t = T[st.session_state.lang]
    st.session_state.val_callsign = ""
    st.session_state.val_qth = ""
    st.session_state.val_band = "20m"
    st.session_state.val_time_mode = t["opt_last_x"]
    st.session_state.val_hours = 24
    st.session_state.val_solar = t["opt_solar_all"]
    st.session_state.val_comp_mode = t["opt_comp_radius"]
    st.session_state.val_ref_radius = 100
    st.session_state.val_max_dist = 22000
    st.session_state.val_min_spots = 1
    st.session_state.val_min_stations = 1
    st.session_state.val_wilcoxon = "OFF"
    st.session_state.run_mode = None

def set_demo_config():
    """Pre-populates the configuration with specific values from config.py to showcase a successful test run, ensuring 100% deterministic UI state."""
    t = T[st.session_state.lang]
    st.session_state.val_callsign = DEMO_CALLSIGN
    st.session_state.val_qth = DEMO_QTH
    st.session_state.val_band = DEMO_BAND
    st.session_state.val_time_mode = t["opt_custom"]
    st.session_state.val_hours = DEMO_HOURS
    st.session_state.val_start_d = DEMO_START_D
    st.session_state.val_end_d = DEMO_END_D
    st.session_state.val_start_t = DEMO_START_T
    st.session_state.val_end_t = DEMO_END_T
    st.session_state.val_solar = t["opt_solar_all"]
    st.session_state.val_comp_mode = t["opt_comp_radius"]
    st.session_state.val_ref_radius = DEMO_REF_RADIUS
    st.session_state.val_ref_callsign = DEMO_REF_CALLSIGN
    st.session_state.val_self_test_mode = t["opt_self_rx"]
    st.session_state.val_self_qth_a = DEMO_SELF_QTH_A
    st.session_state.val_self_qth_b = DEMO_SELF_QTH_B
    st.session_state.val_slot_u = t["opt_slot_even"]
    st.session_state.val_slot_r = t["opt_slot_odd"]
    st.session_state.val_max_dist = DEMO_MAX_DIST
    st.session_state.val_min_spots = DEMO_MIN_SPOTS
    st.session_state.val_min_stations = DEMO_MIN_STATIONS
    st.session_state.val_wilcoxon = DEMO_WILCOXON
    st.session_state.run_mode = None

# ==========================================
# UI COMPONENTS (FRAGMENTS)
# ==========================================
@st.fragment
def render_segment_inspector(analysis_id, title, is_compare, is_sequential, enriched_df, segs_df, parquet_path, line1_str, t, max_dist_km):
    """
    Renders the interactive Segment Inspector directly below the map.
    Allows drill-down into specific Azimuth/Distance chunks to show histograms and tabular data.
    Runs as an independent Streamlit fragment to prevent full-page reruns on interaction.
    """
    run_id = st.session_state.get("run_id", 0)
    valid_distances = sorted([d for d in segs_df['dist_label'].dropna().unique()], key=lambda x: int(x.strip('[]km').split('-')[0]))
    filtered_distances = [d for d in valid_distances if int(d.strip('[]km').split('-')[0]) < max_dist_km]
    
    lbl_dist = t.get("opt_insp_dist", "---")
    lbl_dir = t.get("opt_insp_dir", "---")
    opt_full = t.get("opt_full_range", "Full Range")
    opt_all_dir = t.get("opt_all_dirs", "All Directions")
    
    col_insp1, col_insp2 = st.columns(2)
    with col_insp1: sel_dist = st.selectbox("Distance", [lbl_dist] + filtered_distances + [opt_full], key=f"dist_{analysis_id}_{run_id}", label_visibility="collapsed")
    with col_insp2:
        if sel_dist != lbl_dist:
            if sel_dist == opt_full: valid_dirs = sorted([d for d in segs_df['dir_name'].dropna().unique() if d in COMPASS], key=lambda x: COMPASS.index(x))
            else: valid_dirs = sorted([d for d in segs_df[segs_df['dist_label'] == sel_dist]['dir_name'].dropna().unique() if d in COMPASS], key=lambda x: COMPASS.index(x))
            if not valid_dirs: valid_dirs = [t.get("opt_no_station", "No Stations")]
            if valid_dirs != [t.get("opt_no_station", "No Stations")]: sel_dir = st.selectbox("Direction", [lbl_dir] + valid_dirs + [opt_all_dir], key=f"dir_{analysis_id}_{run_id}", label_visibility="collapsed")
            else: sel_dir = st.selectbox("Direction", [lbl_dir] + valid_dirs, key=f"dir_{analysis_id}_{run_id}", disabled=True, label_visibility="collapsed")
        else: sel_dir = st.selectbox("Direction", [lbl_dir], key=f"dir_{analysis_id}_{run_id}", disabled=True, label_visibility="collapsed")

    # If user selected a valid segment, process the inspection data
    if sel_dist != lbl_dist and sel_dir != lbl_dir and sel_dir != t.get("opt_no_station", "No Stations"):
        selected_seg = f"{sel_dist if sel_dist != opt_full else t['opt_full_range']} | {sel_dir if sel_dir != opt_all_dir else t['opt_all_dirs']}"
        df_seg = enriched_df[enriched_df['SegmentID'] != "Out of Bounds"].copy()
        
        if sel_dist != opt_full: df_seg = df_seg[df_seg['dist_label'] == sel_dist]
        if sel_dir != opt_all_dir: df_seg = df_seg[df_seg['dir_name'] == sel_dir]
            
        vals = df_seg['stat_val'].dropna()
        target_call = st.session_state.val_callsign.upper()
        
        # Setup specific labels based on the active test mode
        if st.session_state.val_comp_mode == t["opt_comp_self"]:
            if st.session_state.val_self_test_mode == t["opt_self_rx"]:
                lbl_only_me = t['leg_only_me'].format(callsign=st.session_state.val_self_qth_a)
                lbl_only_ref = t['leg_only_ref'].format(ref_callsign=st.session_state.val_self_qth_b)
                ref_header = st.session_state.val_self_qth_b
                col_u_name = st.session_state.val_self_qth_a
            else:
                lbl_only_me = t['leg_only_me'].format(callsign="Ant A")
                lbl_only_ref = t['leg_only_ref'].format(ref_callsign="Ant B")
                ref_header = "Ant B"
                col_u_name = "Ant A"
        else:
            lbl_only_me = t['leg_only_me'].format(callsign=target_call)
            col_u_name = target_call
            if st.session_state.val_comp_mode == t["opt_comp_radius"]: 
                lbl_only_ref = t['leg_only_ref_radius']
                ref_header = t['tbl_col_only_ref']
            else: 
                lbl_only_ref = t['leg_only_ref'].format(ref_callsign=st.session_state.val_ref_callsign.upper())
                ref_header = st.session_state.val_ref_callsign.upper()

        remote_str = t['txt_rx_stations'] if analysis_id.startswith("TX") else t['txt_tx_stations']
        
        # Build the sub-footer info string detailing decode counts
        if is_compare and 'count_only_u' in df_seg.columns:
            if is_sequential:
                seg_line2 = f"Both (Async): {len(df_seg[(df_seg['count_only_u']>0) & (df_seg['count_only_r']>0)])}  |  {lbl_only_me}: {int(df_seg['count_only_u'].sum())}  |  {lbl_only_ref}: {int(df_seg['count_only_r'].sum())}  |  {t['txt_remote']} {remote_str}: {len(df_seg)}"
            else:
                seg_joint = df_seg[df_seg['spot_count'] > 0]
                seg_line2 = f"{t['txt_joint_decodes']}: {int(df_seg['spot_count'].sum())}  |  {lbl_only_me}: {int(df_seg['count_only_u'].sum())}  |  {lbl_only_ref}: {int(df_seg['count_only_r'].sum())}  |  {t['txt_joint']} {remote_str}: {len(seg_joint)}  |  {t['txt_remote']} {remote_str}: {len(df_seg)}"
        else:
            seg_line2 = f"{t['txt_total_decodes']}: {int(df_seg['spot_count'].sum())}  |  {t['txt_remote']} {remote_str}: {len(df_seg)}"

        # Render Histogram
        if not vals.empty:
            fig_hist = plt.figure(figsize=(12, 4.5), facecolor='black')
            fig_hist.subplots_adjust(left=0.05, right=0.85, bottom=0.25, top=0.85)
            ax_hist = fig_hist.add_subplot(1,1,1)
            ax_hist.set_facecolor('black')
            ax_hist.tick_params(colors='white')
            for spine in ax_hist.spines.values(): spine.set_color('#444444')
                
            med = vals.median()
            val_counts = vals.value_counts().sort_index()
            ax_hist.bar(val_counts.index, val_counts.values, width=0.4, align='center', color='#36aaf9', alpha=0.8, edgecolor='black')
            
            if (vals.max() - vals.min()) <= 30:
                ticks = np.arange(np.floor(vals.min()), np.ceil(vals.max()) + 1, 1.0)
                ax_hist.set_xticks(ticks)
                
            ax_hist.yaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
            ax_hist.axvline(med, color='red', linestyle='dashed', linewidth=2, label=t["lbl_med_seg"].format(med=med))
            ax_hist.legend(facecolor='#121212', edgecolor='#444444', labelcolor='white')
            ax_hist.set_title(f"{title} - {selected_seg}", color='white', fontweight='bold', pad=15)
            
            station_type = t['tbl_col_rx'] if analysis_id.startswith("TX") else t['tbl_col_tx']
            if not is_compare: ax_hist.set_xlabel(t["lbl_hist_x_abs"].format(station_type=station_type), color='white')
            else: ax_hist.set_xlabel(t["lbl_hist_x_comp"].format(station_type=station_type), color='white')
                
            ax_hist.set_ylabel(t["lbl_hist_count"], color='white')
            fig_hist.text(0.05, 0.02, f"{line1_str}\n{seg_line2}", fontsize=11, color='#cccccc', ha='left', va='bottom', linespacing=1.6)
            st.pyplot(fig_hist, width='stretch')
            plt.close(fig_hist)
        else:
            st.info(t["lbl_no_joint"], icon="ℹ️")
            st.markdown(f"<div style='font-size:11px; color:#ccc; margin-bottom:1rem; font-family:monospace;'>{line1_str}<br>{seg_line2}</div>", unsafe_allow_html=True)

        st.markdown(f"**{t['lbl_insights']}**{t['lbl_insights_sub']}")
        
        station_col = t['tbl_col_rx'] if analysis_id.startswith("TX") else t['tbl_col_tx']
        
        # Render Interactive Master Table
        if not is_compare:
            disp_df = df_seg[['peer_sign', 'peer_grid', 'calc_dist', 'calc_azimuth', 'spot_count', 'stat_val']].copy()
            disp_df.columns = [station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], t['tbl_col_spots'], t['tbl_col_med_snr']]
        else:
            disp_df = df_seg[['peer_sign', 'peer_grid', 'calc_dist', 'calc_azimuth', 'spot_count', 'count_only_u', 'count_only_r', 'stat_val']].copy()
            disp_df.columns = [station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], t['tbl_col_joint'], t['tbl_col_only_u'].format(callsign=col_u_name), lbl_only_ref, t['tbl_col_med_delta']]
        
        km_col = t['tbl_col_km']
        az_col = t['tbl_col_az']
        disp_df[km_col] = disp_df[km_col].round(0).astype(int)
        disp_df[az_col] = disp_df[az_col].round(1)
        
        sorted_disp_df = disp_df.sort_values(by=disp_df.columns[-1], ascending=False, na_position='last').reset_index(drop=True)
        
        tbl_event = st.dataframe(sorted_disp_df, use_container_width=True, hide_index=True, selection_mode="multi-row", on_select="rerun", key=f"tbl_{analysis_id}_{run_id}_{selected_seg}")
        
        # Render Raw Drill-Down Data (if user clicks a row)
        sel_rows = tbl_event.selection.rows
        if sel_rows:
            if len(sel_rows) == 1: st.markdown(t['lbl_drill_single'].format(station=sorted_disp_df.iloc[sel_rows[0]][station_col]))
            else: st.markdown(t['lbl_drill_multi'].format(count=len(sel_rows)))
            sel_stations = sorted_disp_df.iloc[sel_rows][station_col].tolist()
            
            try:
                # Load the raw spots straight from the parquet cache for blazing fast drill-downs
                station_df = pd.read_parquet(parquet_path, filters=[('peer_sign', 'in', sel_stations)])
                meta_df = sorted_disp_df[[station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], t['tbl_col_med_snr']]] if not is_compare else sorted_disp_df[[station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], t['tbl_col_med_delta']]]
                station_df = station_df.merge(meta_df, left_on='peer_sign', right_on=station_col, how='left')
                
                if not is_compare:
                    station_df['Date/Time (UTC)'] = pd.to_datetime(station_df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    drill_df = station_df[['Date/Time (UTC)', station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], 'snr', 'power', 'stat_val', t['tbl_col_med_snr']]].copy()
                    drill_df.columns = ['Date/Time (UTC)', station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], 'SNR (Raw)', 'TX Power (dBm)', 'Norm. SNR (dB)', t['tbl_col_med_snr']]
                    st.dataframe(drill_df, use_container_width=True, hide_index=True)
                    
                else:
                    if is_sequential:
                        joint_df = station_df.copy()
                        if not joint_df.empty:
                            joint_df['Date/Time (UTC)'] = pd.to_datetime(joint_df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
                            col_u = f'{col_u_name} SNR (dB)'
                            col_r = f'{ref_header} SNR (dB)'
                            joint_df[col_u] = np.where(joint_df['is_me'] == 1, joint_df['stat_val'], np.nan)
                            joint_df[col_r] = np.where(joint_df['is_me'] == 0, joint_df['stat_val'], np.nan)
                            col_delta_lbl = t['tbl_col_med_delta'].replace("Median ", "")
                            joint_df[col_delta_lbl] = np.nan
                            drill_df = joint_df[['Date/Time (UTC)', station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], col_u, col_r, col_delta_lbl, t['tbl_col_med_delta']]].copy()
                            st.dataframe(drill_df, use_container_width=True, hide_index=True)
                        else: st.info("No spots available for the selected station(s).", icon="ℹ️")
                    else:
                        joint_df = station_df[(station_df['has_u'] > 0) & (station_df['has_r'] > 0)].copy()
                        if not joint_df.empty:
                            joint_df['Date/Time (UTC)'] = pd.to_datetime(joint_df['time_slot'] * 120, unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
                            joint_df['Δ SNR (dB)'] = (joint_df['snr_u_norm'] - joint_df['snr_r_norm']).round(1)
                            col_u = f'{col_u_name} SNR (dB)'
                            col_r = f'{ref_header} SNR (dB)'
                            col_delta_lbl = t['tbl_col_med_delta'].replace("Median ", "")
                            drill_df = joint_df[['Date/Time (UTC)', station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], 'snr_u_norm', 'snr_r_norm', 'Δ SNR (dB)', t['tbl_col_med_delta']]].copy()
                            drill_df.columns = ['Date/Time (UTC)', station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], col_u, col_r, col_delta_lbl, t['tbl_col_med_delta']]
                            st.dataframe(drill_df, use_container_width=True, hide_index=True)
                        else: st.info("No joint spots available for the selected station(s).", icon="ℹ️")
            except FileNotFoundError: st.warning("Cache file expired. Please Run Analysis again.")

@st.fragment
def render_lazy_download(analysis_id, fig, callsign, t):
    """
    Renders a subtle 'Render High-Res Map' button that dynamically generates
    a 300 DPI PNG map for download upon user request without blocking the UI layout.
    """
    run_id = st.session_state.get("run_id", 0)
    buf_key = f"img_buf_{analysis_id}_{run_id}"
    if buf_key in st.session_state:
        st.download_button("💾 Download", data=st.session_state[buf_key], file_name=f"WSPR_Map_{analysis_id}_{callsign}.png", mime="image/png", type="tertiary", use_container_width=True, key=f"dl_{analysis_id}_{run_id}")
    else:
        if st.button("Render High-Res Map ⚙️", key=f"prep_{analysis_id}_{run_id}", type="tertiary", use_container_width=True):
            with st.spinner("⏳"):
                if fig.axes:
                    ax = fig.axes[0]
                    # Apply country borders explicitly for the high-res export
                    ax.add_feature(cfeature.BORDERS, linewidth=0.6, edgecolor="#414040", zorder=5, alpha=0.5)
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format="png", dpi=300, facecolor='black', edgecolor='none')
                st.session_state[buf_key] = img_buf.getvalue()
            st.rerun(scope="fragment")

# ==========================================
# MAIN UI & APPLICATION FLOW
# ==========================================
st.set_page_config(page_title="WSPRadar.org | Antenna Benchmarking", page_icon="📡", layout="centered")

# Open Graph Meta Tags for rich sharing previews
st.markdown(f"""
    <meta property="og:title" content="WSPRadar.org | Antenna Benchmarking" />
    <meta property="og:description" content="HAM RADIO STATION & ANTENNA BENCHMARKING" />
    <meta property="og:image" content="{LOGO_URL}" />
    <meta property="og:url" content="{APP_URL}" />
    <meta property="og:type" content="website" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="WSPRadar.org" />
    <meta name="twitter:description" content="HAM RADIO STATION & ANTENNA BENCHMARKING" />
    <meta name="twitter:image" content="{LOGO_URL}" />
""", unsafe_allow_html=True)

# Select the appropriate localization dictionary
t = T[st.session_state.lang]

# Main Custom CSS injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');
    html, body, [class*="css"] { font-family: 'Space Mono', monospace !important; }
    .stApp { background-color: #050a15; background-image: radial-gradient(circle at 50% 50%, #0a1428 0%, #02040a 100%); color: #e0e0e0; }
    
    .block-container { max-width: 1024px !important; padding-top: 2rem !important; }
    
    div.stButton > button[kind="primary"] {
        background-color: transparent !important; color: #39ff14 !important; border: 2px solid #39ff14 !important;
        font-family: 'Space Mono', monospace !important; font-size: 1.0rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 1px; box-shadow: 0 0 10px rgba(57, 255, 20, 0.2), inset 0 0 10px rgba(57, 255, 20, 0.1); transition: all 0.3s ease;
    }
    div.stButton > button[kind="primary"]:hover { background-color: rgba(57, 255, 20, 0.1) !important; box-shadow: 0 0 20px rgba(57, 255, 20, 0.6), inset 0 0 15px rgba(57, 255, 20, 0.3); }
    
    /* Sekundäre Buttons (Reset, Demo) */
    div.stButton > button[kind="secondary"] { border-color: rgba(57, 255, 20, 0.5) !important; color: #e0e0e0 !important; font-size: 0.85rem !important; padding: 0.2rem 0.5rem !important; margin-top: 10px; transition: all 0.3s ease; }
    div.stButton > button[kind="secondary"]:hover { border-color: #39ff14 !important; color: #39ff14 !important; box-shadow: 0 0 10px rgba(57, 255, 20, 0.2) !important; }

    /* Selectbox (Sprachauswahl) an den Button-Style anpassen */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: transparent !important;
        border: 1px solid rgba(57, 255, 20, 0.5) !important;
        border-radius: 0.5rem !important;
        color: #e0e0e0 !important;
        font-family: 'Space Mono', monospace !important;
        min-height: 40px !important; 
        margin-top: 10px; 
        transition: all 0.3s ease;
        cursor: pointer;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
        border-color: #39ff14 !important;
        box-shadow: 0 0 10px rgba(57, 255, 20, 0.2) !important;
    }
    
    /* NEU: Zwingt den inneren Text-Container der Selectbox zur absoluten Zentrierung */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div > div:first-child {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        padding-left: 24px; /* Visueller Ausgleich für das Pfeil-Icon rechts */
    }

    /* Die Schriftart und Größe im geschlossenen Select-Feld erzwingen */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
        font-family: 'Space Mono', monospace !important;
        font-size: 0.85rem !important;
        color: inherit !important;
        text-align: center !important;
    }
    /* Das Dropdown-Pfeil-Icon einfärben */
    div[data-testid="stSelectbox"] svg {
        fill: #39ff14 !important;
    }
    
    /* Das geöffnete Dropdown-Menü (Popover) stylen */
    div[data-baseweb="popover"] ul {
        background-color: #0a1428 !important;
        border: 1px solid #39ff14 !important;
        border-radius: 0.5rem !important;
    }
    div[data-baseweb="popover"] ul li {
        font-family: 'Space Mono', monospace !important;
        font-size: 0.85rem !important;
        color: #e0e0e0 !important;
        background-color: transparent !important;
        text-align: center !important;
    }
    div[data-baseweb="popover"] ul li:hover {
        color: #39ff14 !important;
        background-color: rgba(57, 255, 20, 0.1) !important;
    }

    label[data-testid="stWidgetLabel"] p, label[data-testid="stWidgetLabel"] div, div[data-testid="stRadio"] p, label[data-testid="stCheckbox"] p, label[data-testid="stCheckbox"] span { font-family: 'Space Mono', monospace !important; font-size: 14px !important; font-weight: 700 !important; color: #cccccc !important; }
    summary[data-testid="stExpanderToggle"] p { font-family: 'Space Mono', monospace !important; font-size: 16px !important; font-weight: 700 !important; color: #39ff14 !important; text-transform: uppercase; letter-spacing: 1px; }
    h3.section-title { font-family: 'Rajdhani', sans-serif !important; font-size: 2rem !important; color: #ffffff !important; border-bottom: 1px solid rgba(57, 255, 20, 0.3); padding-bottom: 10px; margin-top: 1.5rem; margin-bottom: 1.5rem; letter-spacing: 1px; }
    .stMarkdown h3 { color: #39ff14 !important; border-bottom: 1px solid rgba(57, 255, 20, 0.3); padding-bottom: 8px; margin-top: 2.5rem; font-family: 'Rajdhani', sans-serif !important; font-size: 1.8rem; letter-spacing: 1px; }
    .stMarkdown h4 { color: #ffffff !important; margin-top: 1.8rem; font-size: 1.2rem; font-weight: 700; text-transform: uppercase; }
    .stMarkdown ol, .stMarkdown ul { padding-left: 2.5rem !important; margin-top: 0.5rem; }
    .stMarkdown li { margin-bottom: 0.8rem; }
    
    a.header-anchor { display: none !important; }
    
    .pc-break { display: inline; }
    .mobile-pipe { display: none; }
    
    @media (max-width: 768px) {
        .block-container { padding-top: 1.5rem !important; } 
        
        /*Mobile List Indentation Fix: Weniger Padding spart Platz */
        .stMarkdown ol, .stMarkdown ul { padding-left: 1.1rem !important; }
        .stMarkdown li { margin-bottom: 0.5rem; font-size: 0.9rem; }
            
        .header-container { 
            flex-wrap: wrap !important; 
            padding-bottom: 0.3rem !important; 
            margin-bottom: 0.5rem !important; 
            justify-content: center !important;
            align-items: center !important;
        }
        .text-container { display: contents !important; }
        img.main-logo { display: block !important; width: 65px !important; height: 65px !important; margin-right: 12px !important; margin-bottom: 0 !important; }
        h1.main-title { font-size: 2.8rem !important; text-align: left !important; line-height: 1.0 !important; margin: 0 !important; }
        h2.main-subtitle { 
            width: 100% !important; 
            font-size: 0.83rem !important; 
            letter-spacing: 0.5px !important; 
            margin-top: 2px !important; 
            text-align: center !important; 
            margin-left: 0px !important; 
            white-space: normal !important; 
            line-height: 1.3 !important; 
        }
        
        .dev-credit-container { font-size: 0.7rem !important; line-height: 1.3 !important; padding: 0 5px !important; margin-bottom: 1rem !important; }
        .pc-break { display: none !important; }
        .mobile-pipe { display: inline !important; }
    }
</style>
""", unsafe_allow_html=True)

# Header Section: Logo and Titles for PC 
logo_base64 = get_base64_of_bin_file("img/WSPRadar.png")
st.markdown(f"""
<div class="header-container" style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(57, 255, 20, 0.3); padding-top: 0px;">
    <img class="main-logo" src="data:image/png;base64,{logo_base64}" alt="WSPRadar Logo" style="width: 140px; height: 140px; margin-right: 25px; filter: drop-shadow(0 0 10px rgba(57, 255, 20, 0.6)); padding: 5px;">
    <div class="text-container" style="display: flex; flex-direction: column; align-items: flex-start;">
        <h1 class="main-title" style="font-family: 'Rajdhani', sans-serif; font-size: 5rem; font-weight: 700; color: #ffffff; margin: 0; line-height: 0.9; letter-spacing: 2px; text-shadow: 0 0 15px rgba(255,255,255,0.2);">{t["title"]}</h1>
        <h2 class="main-subtitle" style="font-family: 'Space Mono', monospace; font-size: 1.13rem; color: #39ff14; margin: -15px 0 0 4px; font-weight: 700; letter-spacing: 1px; text-align: left;">{t["subtitle"]}</h2>
    </div>
</div>
<div class="dev-credit-container" style='text-align: center; color: #888888; font-size: 0.85rem; margin-top: 0.5rem; margin-bottom: 1.5rem; line-height: 1.3;'>{t["dev_credit"]}</div>
""", unsafe_allow_html=True)

# Configuration Controls (Titel entfernt für mehr Platz)
col_lang, col_b1, col_b2 = st.columns(3, vertical_alignment="bottom")

with col_lang:
    # Formatiert die internen Keys ("EN"/"DE") für die UI in Flaggen + Text
    def format_lang_ui(lang_key):
        return "🇬🇧 English" if lang_key == "EN" else "🇩🇪 Deutsch"

    idx = 0 if st.session_state.lang == "en" else 1
    st.selectbox("Lang", ["EN", "DE"], index=idx, key="lang_selector_ui", label_visibility="collapsed", on_change=update_lang, format_func=format_lang_ui)

with col_b1: 
    st.button(t["btn_reset"], on_click=set_reset_config, use_container_width=True)

with col_b2: 
    st.button(t["btn_demo"], on_click=set_demo_config, use_container_width=True)

# ----------------------------------------
# Expander 1: Core Parameters
# ----------------------------------------
with st.expander(t["exp_core"], expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        callsign = st.text_input(t["lbl_callsign"], key="val_callsign", on_change=reset_audit).upper()
        qth_locator = st.text_input(t["lbl_qth"], key="val_qth", on_change=reset_audit)
        band = st.selectbox(t["lbl_band"], ["160m", "80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m", "All"], key="val_band", on_change=reset_audit)
    with col2:
        time_mode = st.radio(t["lbl_time_mode"], [t["opt_last_x"], t["opt_custom"]], key="val_time_mode", horizontal=True, on_change=reset_audit)
        if time_mode == t["opt_last_x"]: hours = st.slider(t["lbl_hours"], 1, 168, key="val_hours", on_change=reset_audit)
        else:
            c_start, c_end = st.columns(2)
            today_utc = datetime.now(timezone.utc).date()
            with c_start:
                start_d = st.date_input(t["lbl_start_d"], key="val_start_d", max_value=today_utc, on_change=reset_audit)
                start_t_input = st.time_input(t["lbl_start_t"], key="val_start_t", on_change=reset_audit)
            with c_end:
                max_allowed_end = min(start_d + timedelta(days=MAX_DAYS_HISTORY), today_utc)
                min_allowed_end = start_d
                if st.session_state.val_end_d > max_allowed_end: st.session_state.val_end_d = max_allowed_end
                elif st.session_state.val_end_d < min_allowed_end: st.session_state.val_end_d = min_allowed_end
                end_d = st.date_input(t["lbl_end_d"], key="val_end_d", min_value=min_allowed_end, max_value=max_allowed_end, on_change=reset_audit)
                end_t_input = st.time_input(t["lbl_end_t"], key="val_end_t", on_change=reset_audit)

# ----------------------------------------
# Expander 2: Compare Engine
# ----------------------------------------
with st.expander(t["exp_comp"], expanded=True):
    col_comp_l, col_comp_r = st.columns([0.4, 0.6])
    with col_comp_l:
        comp_mode = st.radio(t["lbl_comp_mode"], [t["opt_comp_radius"], t["opt_comp_buddy"], t["opt_comp_self"]], key="val_comp_mode", on_change=reset_audit)
    
    with col_comp_r:
        if comp_mode == t["opt_comp_radius"]:
            st.slider(t["lbl_radius"], 10, 250, key="val_ref_radius", on_change=reset_audit)
        
        elif comp_mode == t["opt_comp_buddy"]:
            ref_callsign_input = st.text_input(t["lbl_ref_call"], key="val_ref_callsign", on_change=reset_audit).upper()
            if ref_callsign_input == callsign and callsign != "":
                st.error(t["err_self_test"])
                
        elif comp_mode == t["opt_comp_self"]:
            disp_call = callsign if callsign else "..."
            self_test_mode = st.radio(t["lbl_self_test_mode"].format(callsign=disp_call), [t["opt_self_rx"], t["opt_self_tx"]], key="val_self_test_mode", on_change=reset_audit)
            
            if self_test_mode == t["opt_self_rx"]:
                cs1, cs2 = st.columns(2)
                with cs1: self_qth_a = st.text_input(t["lbl_qth_a"], key="val_self_qth_a", max_chars=6, placeholder="e.g. JN37AA", on_change=reset_audit).upper()
                with cs2: self_qth_b = st.text_input(t["lbl_qth_b"], key="val_self_qth_b", max_chars=6, placeholder="e.g. JN37AB", on_change=reset_audit).upper()
                
                # Defensive UI validation for locators
                if len(self_qth_a) > 0 and len(self_qth_b) > 0:
                    if len(self_qth_a) != 6 or len(self_qth_b) != 6:
                        st.warning(t["err_loc_length"])
                    elif not is_valid_6char_locator(self_qth_a) or not is_valid_6char_locator(self_qth_b):
                        st.error(t["err_loc_format"])
                    elif self_qth_a[:4] != self_qth_b[:4]:
                        st.error(t["err_loc_match"])
                    elif self_qth_a == self_qth_b:
                        st.error(t["err_loc_identical"])
            else:
                cs1, cs2 = st.columns(2)
                with cs1: st.selectbox(t["lbl_slot_u"], [t["opt_slot_even"], t["opt_slot_odd"]], key="val_slot_u", on_change=swap_tx_slots_u)
                with cs2: st.selectbox(t["lbl_slot_r"], [t["opt_slot_odd"], t["opt_slot_even"]], key="val_slot_r", on_change=swap_tx_slots_r)

# ----------------------------------------
# Expander 3: Advanced Configurations
# ----------------------------------------
with st.expander(t["exp_adv"], expanded=True):
    col3, col4 = st.columns(2)
    with col3: 
        st.selectbox(t["lbl_solar"], [t["opt_solar_all"], t["opt_solar_day"], t["opt_solar_night"], t["opt_solar_grey"]], key="val_solar", on_change=reset_audit)
        max_dist_km = st.selectbox(t["lbl_max_dist"], [5000, 10000, 15000, 22000], key="val_max_dist", help=t["hlp_max_dist"], on_change=reset_audit)
    with col4:
        min_spots = st.slider(t["lbl_min_spots"], 1, 50, key="val_min_spots", help=t["hlp_min_spots"], on_change=reset_audit)
        min_stations = st.slider(t["lbl_min_stations"], 1, 20, key="val_min_stations", help=t["hlp_min_stations"], on_change=reset_audit)
        st.select_slider(t["lbl_wilcoxon"], options=["OFF", "80%", "90%", "95%", "99%"], key="val_wilcoxon", on_change=reset_audit)

# ==========================================
# MATHEMATICAL PREPARATIONS
# ==========================================
lat_0, lon_0 = locator_to_latlon(qth_locator)
band_val = BAND_MAP.get(band, '')
band_filter = f"AND band = '{band_val}'" if band != 'All' else ""

if time_mode == t["opt_last_x"]:
    end_t_base = datetime.now(timezone.utc)
    start_t_base = end_t_base - timedelta(hours=hours)
else:
    start_t_base = datetime.combine(start_d, start_t_input).replace(tzinfo=timezone.utc)
    end_t_base = datetime.combine(end_d, end_t_input).replace(tzinfo=timezone.utc)

if (end_t_base - start_t_base).total_seconds() > MAX_DAYS_HISTORY * 24 * 3600: start_t_base = end_t_base - timedelta(days=MAX_DAYS_HISTORY)
start_t, end_t = quantize_time(start_t_base), quantize_time(end_t_base)

# ----------------------------------------
# Execute Buttons
# ----------------------------------------
c_run1, c_run2 = st.columns(2)
run_tx_clicked = False
run_rx_clicked = False

with c_run1:
    if st.button(t["btn_run_tx"], type="primary", use_container_width=True):
        run_tx_clicked = True

with c_run2:
    if st.button(t["btn_run_rx"], type="primary", use_container_width=True):
        run_rx_clicked = True

# Validate user logic before assigning run_mode
if run_tx_clicked:
    if comp_mode == t["opt_comp_self"] and st.session_state.val_self_test_mode == t["opt_self_rx"]:
        st.error(t["err_wrong_run"].format(cfg="RX", run="TX"))
        st.stop()
    st.session_state.run_mode = "TX"
    st.session_state.run_id = int(time.time())
    plt.close('all')
    for k in list(st.session_state.keys()):
        if k.startswith("img_buf_"): del st.session_state[k]

if run_rx_clicked:
    if comp_mode == t["opt_comp_self"] and st.session_state.val_self_test_mode == t["opt_self_tx"]:
        st.error(t["err_wrong_run"].format(cfg="TX", run="RX"))
        st.stop()
    if comp_mode == t["opt_comp_self"] and st.session_state.val_self_test_mode == t["opt_self_rx"]:
        qa, qb = st.session_state.val_self_qth_a, st.session_state.val_self_qth_b
        if len(qa) != 6 or len(qb) != 6 or qa[:4] != qb[:4] or qa == qb or not is_valid_6char_locator(qa) or not is_valid_6char_locator(qb):
            st.error(t["err_loc_incomplete"])
            st.stop()
    st.session_state.run_mode = "RX"
    st.session_state.run_id = int(time.time())
    plt.close('all')
    for k in list(st.session_state.keys()):
        if k.startswith("img_buf_"): del st.session_state[k]

st.markdown('<hr style="border: none; border-top: 1px solid rgba(57, 255, 20, 0.3); margin: 2rem 0;">', unsafe_allow_html=True)
status_ui = st.empty()

# ==========================================
# ANALYSIS EXECUTION BLOCK
# ==========================================
if st.session_state.run_mode:
    
    # Speichermanagement: Veraltete Parquet-Dateien vor dem neuen Lauf bereinigen
    cleanup_old_parquets()
    
    # Strikte Prüfung auf Demo-Run komplett ohne Hardcoding (inklusive Band-Check für mehr Präzision)
    is_demo_run = False
    if (time_mode == t["opt_custom"] and 
        callsign == DEMO_CALLSIGN and 
        start_d == DEMO_START_D and 
        end_d == DEMO_END_D and 
        band == DEMO_BAND):
        is_demo_run = True
        
    time_filter = f"time BETWEEN '{start_t.strftime('%Y-%m-%d %H:%M:%S')}' AND '{end_t.strftime('%Y-%m-%d %H:%M:%S')}'"
    
    is_sequential = False
    rx_strict_grid = False
    
    if comp_mode == t["opt_comp_radius"]:
        ref_radius = st.session_state.val_ref_radius
    elif comp_mode == t["opt_comp_buddy"]:
        ref_callsign = st.session_state.val_ref_callsign.upper()
    elif comp_mode == t["opt_comp_self"]:
        ref_callsign = callsign
        if st.session_state.val_self_test_mode == t["opt_self_tx"]:
            is_sequential = True
        elif st.session_state.val_self_test_mode == t["opt_self_rx"]:
            rx_strict_grid = True
            ref_qth = st.session_state.val_self_qth_b
    
    def get_slot_sql(slot_val):
        if slot_val == t["opt_slot_even"]: return "AND toMinute(time) % 4 = 0"
        if slot_val == t["opt_slot_odd"]: return "AND toMinute(time) % 4 = 2"
        return ""

    slot_sql_u = get_slot_sql(st.session_state.val_slot_u) if is_sequential else ""
    slot_sql_r = get_slot_sql(st.session_state.val_slot_r) if is_sequential else ""
    
    # Target SQL Filters
    tx_target_sql = f"tx_sign LIKE '{callsign}%' {band_filter} AND {time_filter}"
    rx_target_sql = f"rx_sign LIKE '{callsign}%' {band_filter} AND {time_filter}"
    if rx_strict_grid and st.session_state.run_mode == "RX":
        rx_target_sql += f" AND rx_loc = '{st.session_state.val_self_qth_a}'"

    # Peer SQL Filters
    if comp_mode == t["opt_comp_radius"]:
        lat_diff, lon_diff = ref_radius / 111.0, ref_radius / (111.0 * np.cos(np.radians(lat_0)))
        tx_peer_sql = f"tx_sign NOT LIKE '{callsign}%' {band_filter} AND tx_lat BETWEEN {lat_0 - lat_diff} AND {lat_0 + lat_diff} AND tx_lon BETWEEN {lon_0 - lon_diff} AND {lon_0 + lon_diff} AND {time_filter}"
        rx_peer_sql = f"rx_sign NOT LIKE '{callsign}%' {band_filter} AND rx_lat BETWEEN {lat_0 - lat_diff} AND {lat_0 + lat_diff} AND rx_lon BETWEEN {lon_0 - lon_diff} AND {lon_0 + lon_diff} AND {time_filter}"
        comp_title = t["comp_title_ref_radius"].format(radius=ref_radius)
        display_callsign = callsign
    else:
        tx_peer_sql = f"tx_sign LIKE '{ref_callsign}%' {band_filter} AND {time_filter}"
        rx_peer_sql = f"rx_sign LIKE '{ref_callsign}%' {band_filter} AND {time_filter}"
        if rx_strict_grid and st.session_state.run_mode == "RX":
            rx_peer_sql += f" AND rx_loc = '{ref_qth}'"
            
        if comp_mode == t["opt_comp_self"]:
            if st.session_state.val_self_test_mode == t["opt_self_rx"]:
                display_callsign = f"{callsign} ({st.session_state.val_self_qth_a})"
                comp_title = f"{callsign} ({st.session_state.val_self_qth_b})"
            else:
                display_callsign = f"{callsign} (Ant A)"
                comp_title = f"{callsign} (Ant B)"
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

    # Prepare batch rendering buffers
    deferred_render_data = []
    lbl_wait_seg = "⏳ Lade..." if st.session_state.lang == "de" else "⏳ Loading..."

    status_log = ["**📡 System Audit Status:**"]
    status_ui.markdown("  \n".join(status_log))
    
    # Process Map Loop
    for i, analysis in enumerate(analyses):
        st.session_state._db_hit = False 
        t_start = time.time() 
        
        with st.spinner(t["msg_proc"].format(id=analysis['id'])):
            # 1. Fetch raw data from backend module
            df = fetch_wspr_data(analysis['query'], is_demo=is_demo_run)
            fetch_time = time.time() - t_start 
            
            source_str = "🌐 wspr.live DB" if st.session_state.get("_db_hit", False) else "⚡ RAM Cache"
            status_log.append(f"- Map {i+1}/2 ({analysis['title']}): Loaded from **{source_str}** in {fetch_time:.2f}s")
            status_ui.markdown("  \n".join(status_log))
            
            if df is not None and not df.empty:
                
                # Apply Solar Filtering locally if requested
                if st.session_state.val_solar != t["opt_solar_all"]:
                    if analysis['is_compare'] and not analysis['is_sequential']: df['dt_time'] = pd.to_datetime(df['time_slot'] * 120, unit='s')
                    else: df['dt_time'] = pd.to_datetime(df['time'])
                    
                    df['solar'] = df['dt_time'].apply(lambda dt: get_solar_state(dt, lat_0, lon_0))
                    target_state = 'day' if st.session_state.val_solar == t["opt_solar_day"] else ('night' if st.session_state.val_solar == t["opt_solar_night"] else 'grey')
                    df = df[df['solar'] == target_state]
                    
                    if df.empty:
                        st.warning(t["warn_no_data"].format(title=analysis['title']))
                        continue

                # Dump current valid data frame to disk-cache for ultra-fast inspector drill-downs later
                parquet_path = f"{CACHE_DIR}/spots_{analysis['id']}_{st.session_state.run_id}.parquet"
                try: df.to_parquet(parquet_path, index=False)
                except Exception as e: st.error(f"Error writing cache: {e}")

                # 2. Fire up the backend plotting engine
                plot_result = generate_map_plot(
                    df, analysis['title'], analysis['is_compare'], analysis['is_sequential'], 
                    start_t, end_t, max_dist_km, analysis['id'], 
                    st.session_state.val_wilcoxon, st.session_state.val_min_stations,
                    lat_0, lon_0
                )
                
                del df
                gc.collect()
                
                if plot_result is None:
                    st.warning(t["warn_no_data"].format(title=analysis['title']))
                    continue
                    
                fig, enriched_df, segs_df, line1_str = plot_result
                run_id = st.session_state.get("run_id", 0)
                
                col_spacer, col_btn = st.columns([0.76, 0.24], vertical_alignment="bottom")
                with col_btn: render_lazy_download(analysis['id'], fig, callsign, t)
                st.pyplot(fig, use_container_width=True, bbox_inches=None)
                
                # Prepare skeleton placeholders for the interactive inspector fragment
                inspector_container = st.container()
                skeleton_ph = inspector_container.empty()
                
                with skeleton_ph.container():
                    c_wait1, c_wait2 = st.columns(2)
                    with c_wait1: st.selectbox("Distance", [lbl_wait_seg], key=f"w_dist_{analysis['id']}_{run_id}", disabled=True, label_visibility="collapsed")
                    with c_wait2: st.selectbox("Direction", [lbl_wait_seg], key=f"w_dir_{analysis['id']}_{run_id}", disabled=True, label_visibility="collapsed")
                
                deferred_render_data.append({
                    'analysis': analysis, 'enriched_df': enriched_df, 'segs_df': segs_df, 
                    'parquet_path': parquet_path, 'line1_str': line1_str, 'skeleton_ph': skeleton_ph, 'inspector_container': inspector_container
                })
            else:
                st.warning(t["warn_no_data"].format(title=analysis['title']))
        st.markdown("---")
        
    status_ui.empty()

    # Flush deferred inspector fragments dynamically into the DOM
    for data in deferred_render_data:
        data['skeleton_ph'].empty()  
        with data['inspector_container']:
            render_segment_inspector(data['analysis']['id'], data['analysis']['title'], data['analysis']['is_compare'], data['analysis']['is_sequential'], data['enriched_df'], data['segs_df'], data['parquet_path'], data['line1_str'], t, max_dist_km)

# ==========================================
# DOCUMENTATION FOOTER
# ==========================================
doc_lang = st.session_state.lang
doc_title = "Dokumentation" if doc_lang == "de" else "Documentation"

col_d1, col_d2, col_d3 = st.columns([0.1, 0.8, 0.1], vertical_alignment="bottom")
with col_d2:
    st.markdown(f"<h2 style='text-align: center; color: #ffffff; margin-bottom: 0; font-family: \"Rajdhani\", sans-serif; letter-spacing: 1px;'>{doc_title}</h2>", unsafe_allow_html=True)
with col_d3:
    # Generate the heavy PDF on demand via the imported engine
    pdf_bytes = generate_pdf_doc(doc_lang, logo_base64, APP_VERSION)
    if pdf_bytes:
        st.download_button(label="💾", data=pdf_bytes, file_name=f"WSPRadar_Doc_{doc_lang.upper()}.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.button("💾", disabled=True, help="PDF Export requires 'markdown' and 'xhtml2pdf' packages.")

# Inject the localized documentation string
st.markdown(get_docs(st.session_state.lang), unsafe_allow_html=True)

# Add the dev_credit footer as a bookend at the very bottom of the page
st.markdown(f"<div style='text-align: center; color: #888888; font-size: 0.9rem; margin-top: 4rem; margin-bottom: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(57, 255, 20, 0.3);'>{t['dev_credit']}</div>", unsafe_allow_html=True)