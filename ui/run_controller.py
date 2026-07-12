"""Streamlit run orchestration for WSPRadar analyses."""

import gc
import hashlib
import json
import time

import streamlit as st

from config import CACHE_DIR, DEMO_PROFILES
from core.analysis_admission import (
    ANALYSIS_ADMISSION_GATE,
    AnalysisDuplicateRequest,
    AnalysisQueueFull,
    AnalysisQueueTimeout,
)
from core.analysis_runner import (
    DECODE_FILTER_LEGACY,
    AnalysisConfigError,
    apply_post_fetch_filters,
    build_analysis_batches,
    should_retry_without_decode_filter,
)
from core.artifact_store import (
    register_session_artifact,
    session_artifact_owner,
    session_artifact_path,
    touch_registered_session_artifacts,
    write_parquet_artifact,
)
from core.data_engine import cleanup_old_parquets, fetch_wspr_data
from core.input_validation import is_valid_callsign, is_valid_locator
from core.math_utils import locator_to_latlon
from core.matplotlib_runtime import matplotlib_profile_collector
from core.performance_timer import (
    PerformanceTimer,
    log_performance_event,
    process_peak_rss_bytes,
    process_rss_bytes,
)
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.components.segment_inspector import render_segment_inspector
from ui.matplotlib_renderer import (
    dispose_matplotlib_figure,
    matplotlib_render_span_label,
    render_matplotlib_figure,
)
from ui.results_export import register_map_export_context
from ui.presentation_context_adapter import build_presentation_context_from_session_state


def _analysis_request_fingerprint(
    *,
    analysis_context,
    start_t,
    end_t,
    band_filter,
    max_dist_km,
    active_demo_profile,
):
    """Return a stable key for one session's complete analysis request."""
    payload = {
        "analysis_context": analysis_context.to_dict(),
        "start_t": start_t.isoformat(),
        "end_t": end_t.isoformat(),
        "band_filter": str(band_filter),
        "max_dist_km": int(max_dist_km),
        "active_demo_profile": active_demo_profile,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _render_fetch_error(fetch_result):
    """Render one structured core fetch failure at the UI boundary."""
    error = fetch_result.error
    if error is None:
        return
    if error.status_code is not None:
        st.error(f"CLICKHOUSE DATABASE ERROR {error.status_code}")
    else:
        st.error(f"WSPR data request failed: {error.message}")
    if error.response_text:
        st.code(error.response_text, language="text")
    if error.query:
        st.warning("The failed SQL query was:")
        st.code(error.query, language="sql")


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
    """Admit one active run, then execute it with unconditional slot release."""
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

    waiting_status = None
    waiting_body = None
    queue_profile = {
        "initial_position": 0,
        "maximum_position": 0,
    }
    admission_started = time.perf_counter()

    def show_waiting(snapshot):
        nonlocal waiting_status, waiting_body
        if queue_profile["initial_position"] == 0:
            queue_profile["initial_position"] = snapshot.position
        queue_profile["maximum_position"] = max(
            queue_profile["maximum_position"],
            snapshot.position,
        )
        label = t.get(
            "msg_analysis_queue_wait",
            "Waiting for analysis capacity: position {position}",
        ).format(position=snapshot.position)
        detail = t.get(
            "msg_analysis_queue_detail",
            "{active}/{maximum} analyses active; {queued} waiting.",
        ).format(
            active=snapshot.active,
            maximum=snapshot.max_active,
            queued=snapshot.queued,
        )
        if waiting_status is None:
            with run_status_slot.container():
                waiting_status = st.status(label, expanded=True, state="running")
                with waiting_status:
                    waiting_body = st.empty()
        else:
            waiting_status.update(label=label, expanded=True, state="running")
        waiting_body.markdown(detail)

    owner = session_artifact_owner(st.session_state)
    request_key = _analysis_request_fingerprint(
        analysis_context=build_analysis_context_from_session_state(st.session_state),
        start_t=start_t,
        end_t=end_t,
        band_filter=band_filter,
        max_dist_km=max_dist_km,
        active_demo_profile=st.session_state.get("active_demo_profile"),
    )

    def log_admission(outcome):
        active, queued = ANALYSIS_ADMISSION_GATE.counts()
        log_performance_event(
            "analysis_admission",
            outcome=outcome,
            run_mode=st.session_state.get("run_mode"),
            wait_seconds=time.perf_counter() - admission_started,
            initial_queue_position=queue_profile["initial_position"],
            maximum_queue_position=queue_profile["maximum_position"],
            active=active,
            queued=queued,
            rss_bytes=process_rss_bytes(),
        )

    try:
        permit = ANALYSIS_ADMISSION_GATE.acquire(
            owner=owner,
            request_key=request_key,
            on_wait=show_waiting,
        )
    except AnalysisDuplicateRequest:
        log_admission("duplicate")
        if waiting_status is not None:
            run_status_slot.empty()
        st.info(t.get(
            "msg_analysis_duplicate",
            "This identical analysis is already active or queued for this session.",
        ))
        return
    except AnalysisQueueFull:
        log_admission("queue_full")
        st.session_state.run_mode = None
        st.warning(t.get(
            "warn_analysis_queue_full",
            "High demand right now. The analysis queue is full. Please try again shortly.",
        ))
        return
    except AnalysisQueueTimeout:
        log_admission("queue_timeout")
        st.session_state.run_mode = None
        if waiting_status is not None:
            run_status_slot.empty()
        st.warning(t.get(
            "warn_analysis_queue_timeout",
            "Analysis capacity did not become available in time. Please run the analysis again.",
        ))
        return

    log_admission("admitted")
    if waiting_status is not None:
        run_status_slot.empty()
    run_started = time.perf_counter()
    rss_start = process_rss_bytes()
    run_outcome = "completed"
    try:
        with permit:
            return _render_admitted_analysis_run(
                t=t,
                run_status_slot=run_status_slot,
                callsign=callsign,
                qth_locator=qth_locator,
                band_filter=band_filter,
                start_t=start_t,
                end_t=end_t,
                max_dist_km=max_dist_km,
                generate_map_plot=generate_map_plot,
                admission_permit=permit,
            )
    except BaseException as exc:
        run_outcome = type(exc).__name__
        raise
    finally:
        active, queued = ANALYSIS_ADMISSION_GATE.counts()
        log_performance_event(
            "analysis_run",
            outcome=run_outcome,
            run_mode=st.session_state.get("run_mode"),
            duration_seconds=time.perf_counter() - run_started,
            active_after_release=active,
            queued_after_release=queued,
            rss_start_bytes=rss_start,
            rss_end_bytes=process_rss_bytes(),
            process_peak_rss_bytes=process_peak_rss_bytes(),
        )


def _render_admitted_analysis_run(
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
    admission_permit,
):
    """Execute one analysis run after the caller has acquired capacity."""

    lat_0, lon_0 = locator_to_latlon(qth_locator)
    touch_registered_session_artifacts(st.session_state)
    cleanup_old_parquets()

    active_demo_key = st.session_state.get("active_demo_profile")
    active_demo = DEMO_PROFILES.get(active_demo_key) if active_demo_key else None
    is_demo_run = active_demo is not None
    analysis_context = build_analysis_context_from_session_state(st.session_state)
    presentation_context = build_presentation_context_from_session_state(
        st.session_state,
        theme="dark",
    )

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
            presentation_context=presentation_context,
            warn=st.warning,
        )
    except AnalysisConfigError as exc:
        st.error(str(exc))
        st.session_state.run_mode = None
        st.stop()

    deferred_render_data = []
    loading_label = "⏳ Lade..." if st.session_state.lang == "de" else "⏳ Loading..."

    for index, analysis in enumerate(analyses):
        admission_permit.touch()
        profile_timer = PerformanceTimer()
        fetch_start = time.time()

        with st.spinner(t["msg_proc"].format(id=analysis["id"])):
            fetch_result = fetch_wspr_data(
                analysis["query"],
                is_demo=is_demo_run,
                response_format=analysis.get("response_format", "csv"),
            )
            _render_fetch_error(fetch_result)
            df = fetch_result.dataframe
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
                fetch_result = fetch_wspr_data(
                    legacy_analysis["query"],
                    is_demo=is_demo_run,
                    response_format=legacy_analysis.get("response_format", "csv"),
                )
                _render_fetch_error(fetch_result)
                df = fetch_result.dataframe
                fetch_time += time.time() - retry_start
                analysis = legacy_analysis

            source_str = fetch_result.source.value
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

            profile_timer.add_memory("fetched dataframe", df=df, detail=source_str)
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

            profile_timer.add_memory("post-filter dataframe", df=df)
            parquet_path = session_artifact_path(
                CACHE_DIR,
                st.session_state,
                run_id=st.session_state.run_id,
                analysis_id=analysis["id"],
            )
            try:
                write_parquet_artifact(df, parquet_path, index=False)
                register_session_artifact(st.session_state, parquet_path)
            except Exception as exc:
                st.error(f"Error writing cache: {exc}")

            status_box.update(label=f"Rendering maps... ({index + 1}/{len(analyses)})", state="running", expanded=True)
            with (
                profile_timer.span("map generation"),
                matplotlib_profile_collector(profile_timer),
            ):
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
                    analysis_context=analysis_context,
                    presentation_context=presentation_context,
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

            fig = plot_result.figure
            enriched_df = plot_result.map_data.station_rows
            segs_df = plot_result.map_data.segment_rows
            line1_str = plot_result.footer_text
            run_id = st.session_state.get("run_id", 0)
            profile_timer.add_memory("map station dataframe", df=enriched_df)
            profile_timer.add_memory("map segment dataframe", df=segs_df)

            try:
                with (
                    profile_timer.span(matplotlib_render_span_label("map render")),
                    matplotlib_profile_collector(profile_timer),
                ):
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
                    analysis_context,
                    presentation_context,
                )
            finally:
                with (
                    profile_timer.span("map figure disposal"),
                    matplotlib_profile_collector(profile_timer),
                ):
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
        admission_permit.touch()
        data["skeleton_ph"].empty()
        with data["inspector_container"]:
            inspector_span = "first Segment Inspector render" if index == 0 else "Segment Inspector render"
            with matplotlib_profile_collector(data["profile_timer"]):
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
                    analysis_context,
                    presentation_context,
                    analysis_start_t=data["start_t"],
                    analysis_end_t=data["end_t"],
                    analysis_kind=data["analysis"].get("analysis_kind", "comparison"),
                    show_export_button=(index == len(deferred_render_data) - 1),
                    timing_collector=data["profile_timer"],
                    timing_label=inspector_span,
                )
