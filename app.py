# streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
# python -m streamlit run app.py

import base64
import time
from datetime import datetime, timedelta, timezone

import streamlit as st

import faulthandler
import sys
faulthandler.enable(file=sys.stderr, all_threads=True)

st.set_page_config(
    page_title="WSPRadar.org | Antenna Benchmarking",
    page_icon="📡",
    layout="centered",
)

# Everything imported below this point belongs to the lightweight landing shell.
# Scientific analysis imports remain inside the active-run branch near the end.
from config import APP_URL, APP_VERSION, BAND_MAP, DEMO_PROFILES, LOGO_URL, MAX_DAYS_HISTORY
from config.demo_profiles import (
    prepare_demo_description_markdown,
    resolve_demo_profile_text,
)
from core.time_utils import quantize_time
from i18n import T
from ui.callbacks import (
    handle_comp_mode_change,
    load_demo_profile_config,
    reset_audit,
    run_demo_profile,
    set_reset_config,
    update_lang,
)
from ui.components.config_panel import render_advanced_expander, render_compare_expander, render_core_expander
from ui.config_io import apply_config_values, validate_config_upload
from ui.config_save import render_config_save_control
from ui.css import apply_custom_css
from ui.documentation_state import collapse_documentation
from ui.result_state import (
    get_active_run_time_window,
    reset_result_state,
    set_active_run_time_window,
)
from ui.state_manager import init_session_state


def get_base64_of_bin_file(bin_file):
    """Read a local binary image file and return a base64 string."""
    try:
        with open(bin_file, "rb") as handle:
            return base64.b64encode(handle.read()).decode()
    except FileNotFoundError:
        return ""


init_session_state()

if not st.session_state.get("_initial_config_loaded", False):
    set_reset_config()
    st.session_state._initial_config_loaded = True

t = T[st.session_state.lang]
apply_custom_css()

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


def render_demo_launcher():
    demo_keys = list(DEMO_PROFILES.keys())
    if not demo_keys:
        return

    def demo_profile_metadata(profile_key):
        """Return profile metadata from the ordinary config or UI adapter."""
        demo_record = DEMO_PROFILES[profile_key]
        configuration = demo_record.get("configuration", demo_record)
        profile_metadata = configuration.get("profile")
        if isinstance(profile_metadata, dict):
            return profile_metadata
        return {
            "id": demo_record.get("id", profile_key),
            "title": demo_record.get("label", {}),
            "description": demo_record.get("description", {}),
        }

    def format_demo_label(profile_key):
        profile_metadata = demo_profile_metadata(profile_key)
        return resolve_demo_profile_text(
            profile_metadata,
            "title",
            st.session_state.lang,
            fallback=profile_metadata.get("id", profile_key),
        )

    if st.session_state.get("selected_demo_profile") not in demo_keys:
        st.session_state.selected_demo_profile = demo_keys[0]

    with st.expander(t.get("lbl_demo_select", "Select demo profile"), expanded=True):
        selected_demo = st.radio(
            t.get("lbl_demo_select", "Select demo profile"),
            demo_keys,
            key="selected_demo_profile",
            format_func=format_demo_label,
            label_visibility="collapsed",
        )
        demo_profile = demo_profile_metadata(selected_demo)
        demo_description = resolve_demo_profile_text(
            demo_profile,
            "description",
            st.session_state.lang,
        )
        if demo_description:
            with st.container(key="demo_description"):
                st.caption(prepare_demo_description_markdown(demo_description))
        col_load_demo, col_run_demo = st.columns(2)
        with col_load_demo:
            if st.button(t.get("btn_load_demo_selected", "Load selected demo configuration"), width="stretch"):
                load_demo_profile_config(selected_demo)
        with col_run_demo:
            if st.button(t.get("btn_run_demo_selected", "Run selected demo"), width="stretch"):
                run_demo_profile(selected_demo)


def render_config_loader():
    with st.expander(t.get("btn_load_config", "Load Config"), expanded=True):
        uploaded_config = st.file_uploader(
            t.get("lbl_config_file", "Select WSPRadar .config file"),
            type=["config", "json"],
            accept_multiple_files=False,
            key="uploaded_config_file",
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

col_lang, col_b1, col_b2, col_b3 = st.columns(4, vertical_alignment="bottom")

with col_lang:
    def format_lang_ui(lang_key):
        return "🇬🇧 English" if lang_key == "EN" else "🇩🇪 Deutsch"

    lang_index = 0 if st.session_state.lang == "en" else 1
    st.selectbox(
        "Lang",
        ["EN", "DE"],
        index=lang_index,
        key="lang_selector_ui",
        label_visibility="collapsed",
        on_change=update_lang,
        format_func=format_lang_ui,
    )

with col_b1:
    if st.button(t["btn_demo"], icon=":material/rocket_launch:", width="stretch"):
        next_demo_state = not st.session_state.get("show_demo_launcher", False)
        st.session_state.show_demo_launcher = next_demo_state
        if next_demo_state:
            st.session_state.show_config_loader = False
        reset_audit()

with col_b2:
    if st.button(t.get("btn_load_config", "Load Config"), icon=":material/upload_file:", width="stretch"):
        next_config_state = not st.session_state.get("show_config_loader", False)
        st.session_state.show_config_loader = next_config_state
        if next_config_state:
            st.session_state.show_demo_launcher = False
        reset_audit()

with col_b3:
    reset_label = "Exit Demo & Reset" if st.session_state.is_demo_mode else t["btn_reset"]
    st.button(reset_label, icon=":material/restart_alt:", on_click=set_reset_config, width="stretch")

if st.session_state.get("show_demo_launcher", False):
    render_demo_launcher()

if st.session_state.get("show_config_loader", False):
    render_config_loader()

if st.session_state.is_demo_mode:
    st.markdown("""
    <style>
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

render_core_expander(t)
render_compare_expander(t)
render_advanced_expander(t)

if st.session_state.get("_collapse_config_panels_once", False):
    st.session_state.config_panels_expanded = True
    st.session_state._collapse_config_panels_once = False

run_status_slot = st.empty()

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

band_value = BAND_MAP.get(band, "")
band_filter = f"AND band = '{band_value}'"

if time_mode == t["opt_last_x"]:
    end_t_base = datetime.now(timezone.utc)
    start_t_base = end_t_base - timedelta(hours=hours)
else:
    start_t_base = datetime.combine(start_d, start_t_input).replace(tzinfo=timezone.utc)
    end_t_base = datetime.combine(end_d, end_t_input).replace(tzinfo=timezone.utc)

if (end_t_base - start_t_base).total_seconds() > MAX_DAYS_HISTORY * 24 * 3600:
    start_t_base = end_t_base - timedelta(days=MAX_DAYS_HISTORY)
candidate_start_t = quantize_time(start_t_base)
candidate_end_t = quantize_time(end_t_base)
active_run_time_window = get_active_run_time_window(st.session_state)
if st.session_state.get("run_mode") and active_run_time_window is not None:
    start_t, end_t = active_run_time_window
else:
    start_t, end_t = candidate_start_t, candidate_end_t
    if st.session_state.get("run_mode"):
        set_active_run_time_window(
            st.session_state,
            run_id=st.session_state.get("run_id"),
            start_utc=start_t,
            end_utc=end_t,
        )


def collapse_config_panels():
    st.session_state.config_panels_expanded = False
    st.session_state._collapse_config_panels_once = True


analysis_direction = st.session_state.get("val_analysis_direction")
run_button_labels = {
    "rx": t["btn_run_analysis_rx"],
    "tx": t["btn_run_analysis_tx"],
}
run_button_icons = {
    "rx": ":material/headphones:",
    "tx": ":material/cell_tower:",
}
run_col, save_col = st.columns([0.65, 0.35], gap="large")
run_analysis_clicked = False

with run_col:
    if st.button(
        run_button_labels.get(
            analysis_direction,
            t["btn_select_analysis_direction"],
        ),
        icon=run_button_icons.get(analysis_direction, ":material/play_arrow:"),
        key="run_analysis_button",
        type="primary",
        width="stretch",
        disabled=analysis_direction not in {"rx", "tx"},
        on_click=collapse_config_panels,
    ):
        run_analysis_clicked = True

with save_col:
    render_config_save_control(popover_key="config_save_top_trigger")

if run_analysis_clicked:
    st.session_state.active_demo_profile = None
    if comp_mode == t["opt_comp_self"] and analysis_direction == "rx":
        setup_b_callsign = st.session_state.val_self_call_b
        if not setup_b_callsign or setup_b_callsign == callsign:
            st.error("Please configure a distinct callsign for Setup B (e.g., DL1MKS/P).")
            st.stop()
    st.session_state.run_mode = analysis_direction.upper()
    st.session_state.run_id = int(time.time())
    collapse_documentation(st.session_state)
    reset_result_state(st.session_state)
    set_active_run_time_window(
        st.session_state,
        run_id=st.session_state.run_id,
        start_utc=candidate_start_t,
        end_utc=candidate_end_t,
    )
    start_t, end_t = candidate_start_t, candidate_end_t
    for key in list(st.session_state.keys()):
        if key.startswith("img_buf_"):
            del st.session_state[key]

st.markdown('<hr style="border: none; border-top: 1px solid rgba(57, 255, 20, 0.3); margin: 2rem 0;">', unsafe_allow_html=True)

if st.session_state.run_mode:
    try:
        with run_status_slot.container():
            with st.spinner(t.get(
                "msg_loading_analysis_engine",
                "Preparing analysis engine...",
            )):
                from core.plot_engine import generate_map_plot
                from ui.run_controller import render_analysis_run
    except ImportError as exc:
        st.session_state.run_mode = None
        st.error(
            "WSPRadar could not load the scientific analysis engine. "
            "Please verify the deployment's Python and native dependencies."
        )
        st.code(str(exc))
    else:
        render_analysis_run(
            t=t,
            run_status_slot=run_status_slot,
            callsign=callsign,
            qth_locator=qth_locator,
            band_filter=band_filter,
            start_t=start_t,
            end_t=end_t,
            max_dist_km=max_dist_km,
            generate_map_plot=generate_map_plot,
        )

# Load the small documentation preview only after the operational interface.
from ui.documentation import render_documentation_section

render_documentation_section(
    t,
    st.session_state.lang,
    logo_base64,
    APP_VERSION,
)
