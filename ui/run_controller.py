"""Streamlit run orchestration for WSPRadar analyses."""

import gc
import time
import uuid

import streamlit as st

from config import CACHE_DIR, DEMO_PROFILES
from core.analysis_runner import (
    DECODE_FILTER_LEGACY,
    AnalysisConfigError,
    apply_post_fetch_filters,
    build_analysis_batches,
    should_retry_without_decode_filter,
)
from core.data_engine import cleanup_old_parquets, fetch_wspr_data
from core.math_utils import is_valid_callsign, is_valid_locator, locator_to_latlon
from core.performance_timer import PerformanceTimer
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.components.segment_inspector import render_segment_inspector
from ui.matplotlib_renderer import (
    dispose_matplotlib_figure,
    matplotlib_render_span_label,
    render_matplotlib_figure,
)
from ui.results_export import register_map_export_context


def render_analysis_run(
    *,
    t,
    run_status_slot,
    callsign,
    qth_locator,
    band_filter,
    start_t,
    end_t,
    max_dist_km,
    generate_map_plot,
):
    """Execute the active Streamlit run and render maps plus deferred inspectors."""
    if not st.session_state.run_mode:
        return

    if not is_valid_callsign(callsign):
        st.error(f"Invalid callsign '{callsign}'. Only A-Z, 0-9, and '/' are allowed (3-15 chars).")
        st.session_state.run_mode = None
        st.stop()

    if not is_valid_locator(qth_locator):
        err_msg = (
            "Fehler: Bitte einen gültigen 4- oder 6-stelligen Locator (z.B. JN37 oder JN37AA) eingeben."
            if st.session_state.lang == "de"
            else "Error: Please enter a valid 4- or 6-character locator (e.g., JN37 or JN37AA)."
        )
        st.error(err_msg)
        st.session_state.run_mode = None
        st.stop()

    lat_0, lon_0 = locator_to_latlon(qth_locator)
    cleanup_old_parquets()

    active_demo_key = st.session_state.get("active_demo_profile")
    active_demo = DEMO_PROFILES.get(active_demo_key) if active_demo_key else None
    is_demo_run = active_demo is not None
    analysis_context = build_analysis_context_from_session_state(st.session_state)

    if active_demo:
        demo_label = active_demo.get("label", {}).get(
            st.session_state.lang,
            active_demo.get("label", {}).get("en", active_demo_key),
        )
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

    try:
        analyses = build_analysis_batches(
            analysis_context,
            start_t,
            end_t,
            lat_0,
            lon_0,
            band_filter,
            warn=st.warning,
        )
    except AnalysisConfigError as exc:
        st.error(str(exc))
        st.session_state.run_mode = None
        st.stop()

    deferred_render_data = []
    loading_label = "⏳ Lade..." if st.session_state.lang == "de" else "⏳ Loading..."

    for index, analysis in enumerate(analyses):
        profile_timer = PerformanceTimer()
        st.session_state._db_hit = False
        fetch_start = time.time()

        with st.spinner(t["msg_proc"].format(id=analysis["id"])):
            df = fetch_wspr_data(
                analysis["query"],
                is_demo=is_demo_run,
                response_format=analysis.get("response_format", "csv"),
            )
            fetch_time = time.time() - fetch_start

            if should_retry_without_decode_filter(df, analysis):
                status_log.append(
                    f"- Map {index + 1}/{len(analyses)}: strict `code = 1` found no target-side evidence; "
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

            if analysis.get("response_format") == "parquet":
                source_str = st.session_state.get("_data_source", "disk cache")
            else:
                source_str = "wspr.live" if st.session_state.get("_db_hit", False) else "RAM cache"
            decode_note = (
                " (legacy decode compatibility: no code filter)"
                if analysis.get("decode_filter_mode") == DECODE_FILTER_LEGACY
                else ""
            )
            status_log.append(
                f"- Map {index + 1}/{len(analyses)}: {analysis['title']} loaded from "
                f"**{source_str}** in {fetch_time:.2f}s{decode_note}"
            )
            profile_timer.add("fetch", fetch_time, detail=source_str + decode_note)
            status_body.markdown("  \n".join(status_log))

            if df is None or df.empty:
                profile_timer.log_report(analysis_title=analysis["title"])
                st.warning(t["warn_no_data"].format(title=analysis["title"]))
                st.markdown("---")
                continue

            with profile_timer.span("post-filtering"):
                df, warning_msg = apply_post_fetch_filters(
                    df,
                    analysis,
                    analysis_context,
                    lat_0,
                    lon_0,
                    t,
                    timing_collector=profile_timer,
                )

            if warning_msg or df.empty:
                profile_timer.log_report(analysis_title=analysis["title"])
                st.warning(warning_msg or t["warn_no_data"].format(title=analysis["title"]))
                st.markdown("---")
                continue

            parquet_path = (
                f"{CACHE_DIR}/spots_{analysis['id']}_{st.session_state.run_id}_"
                f"{uuid.uuid4().hex}.parquet"
            )
            try:
                df.to_parquet(parquet_path, index=False)
            except Exception as exc:
                st.error(f"Error writing cache: {exc}")

            status_box.update(label=f"Rendering maps... ({index + 1}/{len(analyses)})", state="running", expanded=True)
            with profile_timer.span("map generation"):
                plot_result = generate_map_plot(
                    df,
                    analysis["title"],
                    analysis["is_compare"],
                    analysis["is_sequential"],
                    start_t,
                    end_t,
                    max_dist_km,
                    analysis["id"],
                    st.session_state.val_min_stations,
                    lat_0,
                    lon_0,
                    analysis_kind=analysis.get("analysis_kind", "comparison"),
                    theme="dark",
                    timing_collector=profile_timer,
                )
            del df
            gc.collect()

            if plot_result is None:
                profile_timer.log_report(analysis_title=analysis["title"])
                st.warning(t["warn_no_data"].format(title=analysis["title"]))
                st.markdown("---")
                continue

            fig, enriched_df, segs_df, line1_str = plot_result
            run_id = st.session_state.get("run_id", 0)

            try:
                with profile_timer.span(matplotlib_render_span_label("map render")):
                    render_matplotlib_figure(
                        fig,
                        width="stretch",
                        bbox_inches=None,
                        timing_collector=profile_timer,
                        subject="map",
                    )
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
            finally:
                with profile_timer.span("map figure disposal"):
                    dispose_matplotlib_figure(fig)
                    del fig
                    del plot_result
                    gc.collect()

            inspector_container = st.container()
            skeleton_ph = inspector_container.empty()

            with skeleton_ph.container():
                wait_left, wait_right = st.columns(2)
                with wait_left:
                    st.selectbox(
                        "Distance",
                        [loading_label],
                        key=f"w_dist_{analysis['id']}_{run_id}",
                        disabled=True,
                        label_visibility="collapsed",
                    )
                with wait_right:
                    st.selectbox(
                        "Direction",
                        [loading_label],
                        key=f"w_dir_{analysis['id']}_{run_id}",
                        disabled=True,
                        label_visibility="collapsed",
                    )

            deferred_render_data.append({
                "analysis": analysis,
                "enriched_df": enriched_df,
                "segs_df": segs_df,
                "parquet_path": parquet_path,
                "line1_str": line1_str,
                "skeleton_ph": skeleton_ph,
                "inspector_container": inspector_container,
                "start_t": start_t,
                "end_t": end_t,
                "profile_timer": profile_timer,
            })

        st.markdown("---")

    status_box.update(label="Complete", state="complete", expanded=False)

    for index, data in enumerate(deferred_render_data):
        data["skeleton_ph"].empty()
        with data["inspector_container"]:
            inspector_span = "first Segment Inspector render" if index == 0 else "Segment Inspector render"
            render_segment_inspector(
                data["analysis"]["id"],
                data["analysis"]["title"],
                data["analysis"]["is_compare"],
                data["analysis"]["is_sequential"],
                data["enriched_df"],
                data["segs_df"],
                data["parquet_path"],
                data["line1_str"],
                t,
                max_dist_km,
                analysis_start_t=data["start_t"],
                analysis_end_t=data["end_t"],
                analysis_kind=data["analysis"].get("analysis_kind", "comparison"),
                show_export_button=(index == len(deferred_render_data) - 1),
                timing_collector=data["profile_timer"],
                timing_label=inspector_span,
            )
