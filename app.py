# streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
# python -m streamlit run app.py

import io
import time
import gc
import base64
import uuid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta, timezone, time as dt_time
import streamlit as st

# ==========================================
# CUSTOM MODULE IMPORTS (Separation of Concerns)
# ==========================================
from config import (
    APP_VERSION, LOGO_URL, APP_URL, DB_URL, CACHE_DIR, MAX_DAYS_HISTORY,
    COMPASS, BAND_MAP, DEMO_PROFILES
)
from i18n import T

# UI Modules
from ui.css import apply_custom_css
from ui.state_manager import init_session_state
from ui.callbacks import (
    reset_audit, update_lang,
    handle_comp_mode_change, handle_self_test_mode_change,
    set_reset_config, run_demo_profile, load_demo_profile_config
)
from ui.components.config_panel import render_core_expander, render_compare_expander, render_advanced_expander
from ui.components.segment_inspector import render_segment_inspector
from ui.config_io import build_config_payload, validate_config_upload, apply_config_values
from ui.results_export import register_map_export_context, reset_result_export_state

# Core Execution Engines
from core.math_utils import locator_to_latlon, is_valid_6char_locator, quantize_time, is_valid_callsign, is_valid_locator
from core.data_engine import fetch_wspr_data, cleanup_old_parquets
from core.analysis_runner import (
    DECODE_FILTER_LEGACY,
    build_analysis_batches,
    apply_post_fetch_filters,
    should_retry_without_decode_filter,
)
try:
    from core.plot_engine import generate_map_plot
    CARTOPY_IMPORT_ERROR = None
except ImportError as exc:
    generate_map_plot = None
    CARTOPY_IMPORT_ERROR = exc

# Documentation & Export
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
# MAIN UI & APPLICATION FLOW
# ==========================================
st.set_page_config(page_title="WSPRadar.org | Antenna Benchmarking", page_icon="📡", layout="centered")

if CARTOPY_IMPORT_ERROR is not None:
    st.error(
        "WSPRadar could not load Cartopy, which is required for map rendering. "
        "Please verify the Python version and Cartopy environment used by this deployment."
    )
    st.code(str(CARTOPY_IMPORT_ERROR))
    st.stop()

# Bootstrap the session state explicitly AFTER page config and BEFORE any UI rendering
init_session_state()

if not st.session_state.get("_initial_config_loaded", False):
    set_reset_config()
    st.session_state._initial_config_loaded = True

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

# Apply global custom CSS styling
apply_custom_css()

def render_demo_launcher():
    demo_keys = list(DEMO_PROFILES.keys())

    if not demo_keys:
        return

    def format_demo_label(profile_key):
        profile = DEMO_PROFILES[profile_key]
        label = profile.get("label", {})
        return label.get(st.session_state.lang, label.get("en", profile_key))

    if demo_keys and st.session_state.get("selected_demo_profile") not in demo_keys:
        st.session_state.selected_demo_profile = demo_keys[0]

    with st.expander(t.get("lbl_demo_select", "Select demo profile"), expanded=True):
        selected_demo = st.radio(
            t.get("lbl_demo_select", "Select demo profile"),
            demo_keys,
            key="selected_demo_profile",
            format_func=format_demo_label,
            label_visibility="collapsed"
        )
        demo_profile = DEMO_PROFILES[selected_demo]
        demo_description = demo_profile.get("description", {}).get(
            st.session_state.lang,
            demo_profile.get("description", {}).get("en", "")
        )
        if demo_description:
            st.caption(demo_description)
        col_load_demo, col_run_demo = st.columns(2)
        with col_load_demo:
            if st.button(t.get("btn_load_demo_selected", "Load selected demo configuration"), width='stretch'):
                load_demo_profile_config(selected_demo)
        with col_run_demo:
            if st.button(t.get("btn_run_demo_selected", "Run selected demo"), width='stretch'):
                run_demo_profile(selected_demo)

def render_config_loader():
    with st.expander(t.get("btn_load_config", "Load Config"), expanded=True):
        uploaded_config = st.file_uploader(
            t.get("lbl_config_file", "Select WSPRadar .config file"),
            type=["config", "json"],
            accept_multiple_files=False,
            key="uploaded_config_file"
        )
        if uploaded_config is not None:
            if st.button(t.get("btn_apply_config", "Load selected config"), icon=":material/file_upload:", width="stretch"):
                try:
                    config_values, config_warnings = validate_config_upload(uploaded_config.getvalue())
                    apply_config_values(config_values)
                    st.success(t.get("msg_config_loaded", "Config loaded. Existing results were cleared."))
                    for warning in config_warnings:
                        st.warning(warning)
                    st.rerun()
                except ValueError as exc:
                    st.error(t.get("err_config_load", "Config could not be loaded: {error}").format(error=exc))

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

# Configuration Controls
col_lang, col_b1, col_b2, col_b3 = st.columns(4, vertical_alignment="bottom")

with col_lang:
    def format_lang_ui(lang_key):
        return "🇬🇧 English" if lang_key == "EN" else "🇩🇪 Deutsch"
    idx = 0 if st.session_state.lang == "en" else 1
    st.selectbox("Lang", ["EN", "DE"], index=idx, key="lang_selector_ui", label_visibility="collapsed", on_change=update_lang, format_func=format_lang_ui)

with col_b1:
    if st.button(t["btn_demo"], icon=":material/rocket_launch:", width='stretch'):
        next_demo_state = not st.session_state.get("show_demo_launcher", False)
        st.session_state.show_demo_launcher = next_demo_state
        if next_demo_state:
            st.session_state.show_config_loader = False
        reset_audit()

with col_b2:
    if st.button(t.get("btn_load_config", "Load Config"), icon=":material/upload_file:", width='stretch'):
        next_config_state = not st.session_state.get("show_config_loader", False)
        st.session_state.show_config_loader = next_config_state
        if next_config_state:
            st.session_state.show_demo_launcher = False
        reset_audit()

with col_b3:
    btn_reset_lbl = "Exit Demo & Reset" if st.session_state.is_demo_mode else t["btn_reset"]
    st.button(btn_reset_lbl, icon=":material/restart_alt:", on_click=set_reset_config, width='stretch')

if st.session_state.get("show_demo_launcher", False):
    render_demo_launcher()

if st.session_state.get("show_config_loader", False):
    render_config_loader()

# Dynamischer CSS Glow für den Exit-Button
if st.session_state.is_demo_mode:
    st.markdown("""
    <style>
        /* Zielt exakt auf den Reset/Exit-Button in der vierten Spalte des ersten Blocks ab */
        div[data-testid="stHorizontalBlock"] > div:nth-child(4) div.stButton > button {
            border-color: #39ff14 !important;
            color: #39ff14 !important;
            text-shadow: 0 0 5px rgba(57, 255, 20, 0.5);
            box-shadow: 0 0 15px rgba(57, 255, 20, 0.8), inset 0 0 8px rgba(57, 255, 20, 0.3) !important;
            transition: all 0.3s ease;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-child(4) div.stButton > button:hover {
            background-color: rgba(57, 255, 20, 0.1) !important;
            box-shadow: 0 0 25px rgba(57, 255, 20, 1.0), inset 0 0 15px rgba(57, 255, 20, 0.5) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# UI COMPONENTS RENDER BLOCK
# ==========================================
render_core_expander(t)
render_compare_expander(t)
render_advanced_expander(t)

if st.session_state.get("_collapse_config_panels_once", False):
    st.session_state.config_panels_expanded = True
    st.session_state._collapse_config_panels_once = False

run_status_slot = st.empty()

# ==========================================
# STATE TO LOCAL VARIABLES BRIDGE
# ==========================================
# Extract values from session state to local variables so the execution engine 
# below can run without any structural changes.
callsign = st.session_state.val_callsign.strip().upper()
qth_locator = st.session_state.val_qth.strip()
band = st.session_state.val_band
time_mode = st.session_state.val_time_mode
hours = st.session_state.val_hours
start_d = st.session_state.val_start_d
end_d = st.session_state.val_end_d
start_t_input = st.session_state.val_start_t
end_t_input = st.session_state.val_end_t
comp_mode = st.session_state.val_comp_mode
max_dist_km = st.session_state.val_max_dist

# ==========================================
# MATHEMATICAL PREPARATIONS
# ==========================================
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
def collapse_config_panels():
    st.session_state.config_panels_expanded = False
    st.session_state._collapse_config_panels_once = True

c_run1, c_save, c_run2 = st.columns([0.38, 0.24, 0.38], gap="large")
run_tx_clicked = False
run_rx_clicked = False

with c_run1:
    if st.button(t["btn_run_tx"], icon=":material/cell_tower:", type="primary", width='stretch', on_click=collapse_config_panels):
        run_tx_clicked = True

with c_save:
    config_bytes, config_filename = build_config_payload()
    st.download_button(
        t.get("btn_save_config", "Save Config"),
        data=config_bytes,
        file_name=config_filename,
        mime="application/json",
        icon=":material/save:",
        type="primary",
        width="stretch"
    )

with c_run2:
    if st.button(t["btn_run_rx"], icon=":material/headphones:", type="primary", width='stretch', on_click=collapse_config_panels):
        run_rx_clicked = True

# Validate user logic before assigning run_mode
if run_tx_clicked:
    st.session_state.active_demo_profile = None
    if comp_mode == t["opt_comp_self"] and st.session_state.val_self_test_mode == t["opt_self_rx"]:
        st.error(t["err_wrong_run"].format(cfg="RX", run="TX"))
        st.stop()
    st.session_state.run_mode = "TX"
    st.session_state.run_id = int(time.time())
    reset_result_export_state()
    plt.close('all')
    for k in list(st.session_state.keys()):
        if k.startswith("img_buf_"): del st.session_state[k]

if run_rx_clicked:
    st.session_state.active_demo_profile = None
    if comp_mode == t["opt_comp_self"] and st.session_state.val_self_test_mode == t["opt_self_tx"]:
        st.error(t["err_wrong_run"].format(cfg="TX", run="RX"))
        st.stop()
    if comp_mode == t["opt_comp_self"] and st.session_state.val_self_test_mode == t["opt_self_rx"]:
        cb = st.session_state.val_self_call_b
        if not cb or cb == callsign:
            st.error("Please configure a distinct callsign for Setup B (e.g., DL1MKS/P).")
            st.stop()
    st.session_state.run_mode = "RX"
    st.session_state.run_id = int(time.time())
    reset_result_export_state()
    plt.close('all')
    for k in list(st.session_state.keys()):
        if k.startswith("img_buf_"): del st.session_state[k]

st.markdown('<hr style="border: none; border-top: 1px solid rgba(57, 255, 20, 0.3); margin: 2rem 0;">', unsafe_allow_html=True)

# ==========================================
# ANALYSIS EXECUTION BLOCK
# ==========================================
if st.session_state.run_mode:

    # Validations before execution (greift NUR, wenn eine Analyse gestartet wird)
    if not is_valid_callsign(callsign):
        st.error(f"Invalid callsign '{callsign}'. Only A-Z, 0-9, and '/' are allowed (3-15 chars).")
        st.session_state.run_mode = None  # Reset state
        st.stop()

    if not is_valid_locator(qth_locator):
        err_msg = "Fehler: Bitte einen gültigen 4- oder 6-stelligen Locator (z.B. JN37 oder JN37AA) eingeben." if st.session_state.lang == "de" else "Error: Please enter a valid 4- or 6-character locator (e.g., JN37 or JN37AA)."
        st.error(err_msg)
        st.session_state.run_mode = None  # Reset state
        st.stop()

    lat_0, lon_0 = locator_to_latlon(qth_locator)
        
    # Storage Management: Purge expired parquet cache files before starting a new run
    cleanup_old_parquets()

    active_demo_key = st.session_state.get("active_demo_profile")
    active_demo = DEMO_PROFILES.get(active_demo_key) if active_demo_key else None
    is_demo_run = active_demo is not None

    # Initialize the visual audit log before any SQL work starts, including cycle-sync prequeries.
    if active_demo:
        demo_label = active_demo.get("label", {}).get(st.session_state.lang, active_demo.get("label", {}).get("en", active_demo_key))
        status_label = f"Running {st.session_state.run_mode} demo: loading WSPR data... ({demo_label})"
    else:
        status_label = f"Running {st.session_state.run_mode} analysis: loading WSPR data..."

    with run_status_slot.container():
        status_box = st.status(status_label, expanded=True, state="running")
        with status_box:
            status_body = st.empty()
    status_log = ["**System Audit Status:**"]
    status_log.append("- Preparing synchronized WSPR cycles and analysis queries...")
    status_body.markdown("  \n".join(status_log))

    # Delegate complex SQL query generation to the analysis runner engine
    analyses = build_analysis_batches(t, start_t, end_t, lat_0, lon_0, band_filter, callsign)

    # Buffers to hold UI fragments that must be rendered AFTER the maps are drawn
    deferred_render_data = []
    lbl_wait_seg = "⏳ Lade..." if st.session_state.lang == "de" else "⏳ Loading..."
    
    # Iterate through the generated SQL batches (e.g., Target vs. Reference)
    for i, analysis in enumerate(analyses):
        st.session_state._db_hit = False 
        t_start = time.time() 
        
        with st.spinner(t["msg_proc"].format(id=analysis['id'])):
            
            # Step 1: Fetch raw spot data from the backend (Cache or ClickHouse)
            df = fetch_wspr_data(
                analysis['query'],
                is_demo=is_demo_run,
                response_format=analysis.get("response_format", "csv"),
            )
            fetch_time = time.time() - t_start 

            if should_retry_without_decode_filter(df, analysis):
                status_log.append(
                    f"- Map {i+1}/{len(analyses)}: strict `code = 1` found no target-side evidence; "
                    "retrying legacy decode compatibility mode..."
                )
                status_body.markdown("  \n".join(status_log))
                retry_start = time.time()
                legacy_analysis = dict(analysis)
                legacy_analysis["query"] = analysis["legacy_query"]
                legacy_analysis["decode_filter_mode"] = analysis.get(
                    "legacy_decode_filter_mode",
                    DECODE_FILTER_LEGACY,
                )
                st.session_state._db_hit = False
                df = fetch_wspr_data(
                    legacy_analysis["query"],
                    is_demo=is_demo_run,
                    response_format=legacy_analysis.get("response_format", "csv"),
                )
                fetch_time += time.time() - retry_start
                analysis = legacy_analysis
            
            # Update the UI audit log with fetch performance metrics
            if analysis.get("response_format") == "parquet":
                source_str = st.session_state.get("_data_source", "disk cache")
            else:
                source_str = "wspr.live" if st.session_state.get("_db_hit", False) else "RAM cache"
            decode_note = (
                " (legacy decode compatibility: no code filter)"
                if analysis.get("decode_filter_mode") == DECODE_FILTER_LEGACY
                else ""
            )
            status_log.append(f"- Map {i+1}/{len(analyses)}: {analysis['title']} loaded from **{source_str}** in {fetch_time:.2f}s{decode_note}")
            status_body.markdown("  \n".join(status_log))
            
            if df is not None and not df.empty:
                
                # Step 2: Apply mathematical filters (Solar, Minimum Spot thresholds)
                df, warning_msg = apply_post_fetch_filters(df, analysis, lat_0, lon_0, t)
                
                # Halt execution for this specific map if filters depleted all valid data
                if warning_msg or df.empty:
                    st.warning(warning_msg or t["warn_no_data"].format(title=analysis['title']))
                    continue

                # Step 3: Dump the validated dataframe to disk (Parquet) 
                # This enables ultra-fast, memory-efficient drill-downs in the segment inspector later
                parquet_path = (
                    f"{CACHE_DIR}/spots_{analysis['id']}_{st.session_state.run_id}_"
                    f"{uuid.uuid4().hex}.parquet"
                )
                try: 
                    df.to_parquet(parquet_path, index=False)
                except Exception as e: 
                    st.error(f"Error writing cache: {e}")

                # Step 4: Pass the data to the backend plotting engine to generate the Matplotlib figure
                status_box.update(label=f"Rendering maps... ({i+1}/{len(analyses)})", state="running", expanded=True)
                plot_result = generate_map_plot(
                    df, analysis['title'], analysis['is_compare'], analysis['is_sequential'],
                    start_t, end_t, max_dist_km, analysis['id'], 
                    st.session_state.val_min_stations,
                    lat_0, lon_0,
                    analysis_kind=analysis.get("analysis_kind", "comparison"),
                    theme="dark"
                )
                # Force garbage collection to free up RAM immediately after plotting
                del df
                gc.collect()
                
                if plot_result is None:
                    st.warning(t["warn_no_data"].format(title=analysis['title']))
                    continue
                    
                # Unpack the results from the plotting engine
                fig, enriched_df, segs_df, line1_str = plot_result
                run_id = st.session_state.get("run_id", 0)
                
                # Render the map to the UI and register the light-theme export context.
                st.pyplot(fig, width='stretch', bbox_inches=None)
                register_map_export_context(
                    analysis,
                    parquet_path,
                    start_t,
                    end_t,
                    max_dist_km,
                    st.session_state.val_min_stations,
                    lat_0,
                    lon_0,
                )
                
                # Step 5: Setup placeholder containers for the interactive Segment Inspector.
                # We defer the actual rendering of the inspector until the loop finishes 
                # to prevent layout jumping while the second map is still loading.
                inspector_container = st.container()
                skeleton_ph = inspector_container.empty()
                
                with skeleton_ph.container():
                    c_wait1, c_wait2 = st.columns(2)
                    with c_wait1: st.selectbox("Distance", [lbl_wait_seg], key=f"w_dist_{analysis['id']}_{run_id}", disabled=True, label_visibility="collapsed")
                    with c_wait2: st.selectbox("Direction", [lbl_wait_seg], key=f"w_dir_{analysis['id']}_{run_id}", disabled=True, label_visibility="collapsed")
                
                # Append all necessary data to the buffer for deferred rendering
                deferred_render_data.append({
                    'analysis': analysis, 'enriched_df': enriched_df, 'segs_df': segs_df, 
                    'parquet_path': parquet_path, 'line1_str': line1_str, 'skeleton_ph': skeleton_ph,
                    'inspector_container': inspector_container, 'start_t': start_t, 'end_t': end_t
                })
            else:
                st.warning(t["warn_no_data"].format(title=analysis['title']))
        st.markdown("---")
        
    status_box.update(label="Complete", state="complete", expanded=False)

    # Flush deferred inspector fragments dynamically into the DOM
    for idx, data in enumerate(deferred_render_data):
        data['skeleton_ph'].empty()  
        with data['inspector_container']:
            render_segment_inspector(
                data['analysis']['id'],
                data['analysis']['title'],
                data['analysis']['is_compare'],
                data['analysis']['is_sequential'],
                data['enriched_df'],
                data['segs_df'],
                data['parquet_path'],
                data['line1_str'],
                t,
                max_dist_km,
                analysis_start_t=data['start_t'],
                analysis_end_t=data['end_t'],
                analysis_kind=data['analysis'].get("analysis_kind", "comparison"),
                show_export_button=(idx == len(deferred_render_data) - 1),
            )

# ==========================================
# DOCUMENTATION FOOTER
# ==========================================
doc_lang = st.session_state.lang
doc_title = "Dokumentation" if doc_lang == "de" else "Documentation"

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
col_doc_title, col_doc_download, col_doc_spacer = st.columns([0.28, 0.11, 0.61], vertical_alignment="center")
with col_doc_title:
    st.markdown(f"<h2 style='text-align: left; color: #ffffff; margin: 0; padding: 0; line-height: 1; font-family: \"Rajdhani\", sans-serif; letter-spacing: 1px; white-space: nowrap;'>{doc_title}</h2>", unsafe_allow_html=True)
with col_doc_download:
    # Generate the heavy PDF on demand via the imported engine
    pdf_bytes = generate_pdf_doc(doc_lang, logo_base64, APP_VERSION)
    if pdf_bytes:
        st.download_button(label="PDF", icon=":material/picture_as_pdf:", data=pdf_bytes, file_name=f"WSPRadar_Doc_{doc_lang.upper()}.pdf", mime="application/pdf", width='stretch')
    else:
        st.button("PDF", icon=":material/picture_as_pdf:", disabled=True, help="PDF Export requires 'markdown' and 'xhtml2pdf' packages.", width='stretch')

# Inject the localized documentation string
st.markdown(get_docs(st.session_state.lang), unsafe_allow_html=True)

# Add the dev_credit footer as a bookend at the very bottom of the page
st.markdown(f"<div style='text-align: center; color: #888888; font-size: 0.9rem; margin-top: 4rem; margin-bottom: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(57, 255, 20, 0.3);'>{t['dev_credit']}</div>", unsafe_allow_html=True)
