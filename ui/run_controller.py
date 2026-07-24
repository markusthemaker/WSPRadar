"""Streamlit run orchestration for WSPRadar analyses."""

from datetime import datetime, timezone
import gc
import hashlib
import json
import time
import uuid

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
    DECODE_FILTER_STRICT,
    AnalysisConfigError,
    build_analysis_batches,
)
from core.artifact_store import (
    ArtifactNamespace,
    read_parquet_artifact,
    register_session_artifact,
    retire_registered_session_artifacts,
    session_artifact_owner,
    session_artifact_path,
    touch_registered_session_artifacts,
)
from core.data_engine import cleanup_old_parquets, estimate_uncached_requests
from core.fetch_models import FetchFailureScope
from core.input_validation import is_valid_callsign, is_valid_locator
from core.math_utils import locator_to_latlon
from core.matplotlib_runtime import matplotlib_profile_collector
from core.performance_timer import (
    log_performance_event,
    process_peak_rss_bytes,
    process_rss_bytes,
)
from core.provider_dispatch import (
    NoProviderAvailable,
    ProviderAcquireTimeout,
    ProviderDispatchError,
    ProviderRunLease,
    ProviderSkipReason,
    UPSTREAM_PROVIDER_DISPATCH,
)
from core.run_data_preparation import (
    ProviderBundleFetchError,
    ProviderBundlePreparationError,
    prepare_provider_bundle,
)
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.analysis_submission_state import (
    SUBMISSION_PHASE_QUEUED,
    SUBMISSION_PHASE_RUNNING,
    get_analysis_submission,
    update_analysis_submission,
)
from ui.components.segment_inspector import render_segment_inspector
from ui.matplotlib_renderer import (
    dispose_matplotlib_figure,
    matplotlib_render_span_label,
    render_matplotlib_figure,
)
from ui.result_hierarchy import (
    build_result_context,
    evidence_level_header_html,
    remote_station_type,
    result_context_html,
    transition_prompt_html,
)
from ui.results_export import register_map_export_context
from ui.presentation_context_adapter import build_presentation_context_from_session_state
from ui.result_state import (
    clear_rendered_result_state,
    get_active_run_database_source,
    set_active_run_database_source,
)


ANALYSIS_RUN_FOLLOWER_COMPLETED = "duplicate_follower_completed"


def _analysis_request_fingerprint(
    *,
    analysis_context,
    start_t,
    end_t,
    band_filter,
    active_demo_profile,
):
    """Return a stable key for one session's complete analysis request."""
    payload = {
        "analysis_context": analysis_context.to_dict(),
        "start_t": start_t.isoformat(),
        "end_t": end_t.isoformat(),
        "band_filter": str(band_filter),
        "active_demo_profile": active_demo_profile,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _render_fetch_error(fetch_result):
    """Render one structured core fetch failure at the UI boundary."""
    error = fetch_result.error
    if error is None:
        return
    failure_diagnostics = {
        "source": fetch_result.database_source.value,
        "delivery_source": fetch_result.source.value,
        "failure_code": error.code,
        "failure_scope": error.scope.value,
    }
    if error.status_code is not None:
        failure_diagnostics["status_code"] = error.status_code
    if error.retry_after_seconds is not None:
        failure_diagnostics["retry_after_seconds"] = error.retry_after_seconds
    if error.failure_stage:
        failure_diagnostics["failure_stage"] = error.failure_stage
    if fetch_result.artifact_path is not None:
        artifact_parts = set(fetch_result.artifact_path.parts)
        if ArtifactNamespace.DEMO_QUERY.value in artifact_parts:
            failure_diagnostics["cache_namespace"] = ArtifactNamespace.DEMO_QUERY.value
            failure_diagnostics["cache_policy"] = "demo_absolute_24h"
        elif ArtifactNamespace.QUERY.value in artifact_parts:
            failure_diagnostics["cache_namespace"] = ArtifactNamespace.QUERY.value
            failure_diagnostics["cache_policy"] = "standard_access_1h"
    log_performance_event("analysis_fetch_failure", **failure_diagnostics)
    if error.status_code is not None:
        st.error(f"CLICKHOUSE DATABASE ERROR {error.status_code}")
    else:
        st.error(f"WSPR data request failed: {error.message}")
    if error.response_text:
        st.code(error.response_text, language="text")
    if error.query:
        st.warning("The failed SQL query was:")
        st.code(error.query, language="sql")


def _provider_request_counts(analyses, *, is_demo_run):
    """Estimate complete-bundle network reservations for every data source."""
    return {
        provider.key: estimate_uncached_requests(
            analyses,
            is_demo=is_demo_run,
            database_provider=provider,
        )
        for provider in UPSTREAM_PROVIDER_DISPATCH.providers
        if provider.enabled
    }


def _try_reserve_upstream_capacity(
    analyses,
    *,
    is_demo_run,
    allowed_sources,
):
    """Reinspect provider caches immediately before one reservation attempt."""
    request_counts_by_provider = _provider_request_counts(
        analyses,
        is_demo_run=is_demo_run,
    )
    provider_lease = UPSTREAM_PROVIDER_DISPATCH.try_acquire_run(
        request_counts_by_provider,
        allowed_sources=allowed_sources,
        prefer_cache_only=is_demo_run,
    )
    return provider_lease, request_counts_by_provider


def _staged_artifact_paths(analyses, *, provider_key):
    """Return unique unregistered paths for one transactional provider attempt."""
    attempt_token = f"{provider_key}_{uuid.uuid4().hex[:12]}"
    return {
        analysis["id"]: session_artifact_path(
            CACHE_DIR,
            st.session_state,
            run_id=f"{st.session_state.run_id}_{attempt_token}",
            analysis_id=analysis["id"],
        )
        for analysis in analyses
    }


def _database_selection_reason(
    provider_key,
    *,
    failed_sources,
    committed_source,
    skipped_source_reasons=(),
    used_cache_affinity=False,
):
    """Classify why this run committed its selected database source."""
    if committed_source is not None:
        return "committed_source"
    if failed_sources:
        return "failure_fallback"
    skip_reason_values = {
        reason.value if isinstance(reason, ProviderSkipReason) else str(reason)
        for _source_key, reason in skipped_source_reasons
    }
    provider_health_reasons = {
        ProviderSkipReason.CIRCUIT_OPEN.value,
        ProviderSkipReason.RECOVERY_PROBE_IN_FLIGHT.value,
    }
    if skip_reason_values.intersection(provider_health_reasons):
        return "failure_fallback"
    if used_cache_affinity:
        return "cache_affinity"
    primary_source = next(
        provider.key
        for provider in UPSTREAM_PROVIDER_DISPATCH.providers
        if provider.enabled
    )
    if provider_key == primary_source:
        return "primary"
    return "capacity_spillover"


def _database_origin_status(provider_key, *, selection_reason):
    """Return committed-run origin wording without implying a new request."""
    provider = UPSTREAM_PROVIDER_DISPATCH.provider(provider_key)
    role = selection_reason.replace("_", " ")
    return (
        "- Database origin for complete run: "
        f"**{provider.display_name}** ({role})"
    )


def _query_fetch_status(prepared_analysis):
    """Render strict and legacy delivery tiers from one committed query trace."""
    query_fetches = prepared_analysis.query_fetches
    if not query_fetches:
        return "query delivery details unavailable"

    has_legacy_fetch = any(
        query_fetch.decode_filter_mode == DECODE_FILTER_LEGACY
        for query_fetch in query_fetches
    )
    has_usable_result = (
        prepared_analysis.warning_message is None
        and prepared_analysis.artifact_path is not None
    )
    fetch_descriptions = []
    for query_index, query_fetch in enumerate(query_fetches):
        is_legacy_fetch = query_fetch.decode_filter_mode == DECODE_FILTER_LEGACY
        if is_legacy_fetch:
            phase_label = "legacy"
        elif query_fetch.decode_filter_mode == DECODE_FILTER_STRICT:
            phase_label = "strict"
        else:
            phase_label = query_fetch.decode_filter_mode
        is_selected_fetch = query_index == len(query_fetches) - 1

        if not is_legacy_fetch and has_legacy_fetch:
            outcome = "no target-side evidence"
        elif is_selected_fetch and has_usable_result:
            outcome = "used"
        elif is_selected_fetch:
            outcome = "completed; no usable result"
        else:
            outcome = "completed"
        if is_legacy_fetch:
            outcome += "; no code filter"

        fetch_descriptions.append(
            f"{phase_label}: **{query_fetch.delivery_source.delivery_label}** "
            f"in {query_fetch.elapsed_seconds:.2f}s ({outcome})"
        )

    if (
        prepared_analysis.analysis.get("legacy_query")
        and not has_legacy_fetch
    ):
        fetch_descriptions.append("legacy: not needed")
    return "; ".join(fetch_descriptions)


def _refresh_session_artifacts_before_cleanup():
    """Protect this session's retained artifacts before global TTL cleanup."""
    touch_registered_session_artifacts(st.session_state)
    return cleanup_old_parquets()


def render_analysis_run(
    *,
    t,
    run_status_slot,
    callsign,
    qth_locator,
    band_filter,
    start_t,
    end_t,
    generate_map_plot,
):
    """Admit one active run, then execute it with unconditional slot release."""
    if not st.session_state.run_mode:
        return

    submission_snapshot = get_analysis_submission(st.session_state)
    submission_token = (
        submission_snapshot.token
        if submission_snapshot is not None
        else None
    )

    if not is_valid_callsign(callsign):
        st.error(
            t.get(
                "err_callsign_format",
                "Enter a plausible 3-15 character callsign/reporting identifier.",
            )
        )
        st.session_state.run_mode = None
        return

    if not is_valid_locator(qth_locator):
        st.error(
            t.get(
                "err_qth_format",
                "Enter a valid 4- or 6-character Maidenhead locator.",
            )
        )
        st.session_state.run_mode = None
        return

    center_latitude, center_longitude = locator_to_latlon(qth_locator)
    active_demo_key = st.session_state.get("active_demo_profile")
    active_demo = DEMO_PROFILES.get(active_demo_key) if active_demo_key else None
    is_demo_run = active_demo is not None
    analysis_context = build_analysis_context_from_session_state(st.session_state)
    presentation_context = build_presentation_context_from_session_state(
        st.session_state,
        theme="dark",
    )
    try:
        analyses = build_analysis_batches(
            analysis_context,
            start_t,
            end_t,
            center_latitude,
            center_longitude,
            band_filter,
            presentation_context=presentation_context,
            warn=st.warning,
        )
    except AnalysisConfigError as exc:
        st.error(str(exc))
        st.session_state.run_mode = None
        return

    _refresh_session_artifacts_before_cleanup()
    request_counts_by_provider = {}
    committed_source = get_active_run_database_source(st.session_state)
    allowed_sources = {committed_source} if committed_source is not None else None

    def reserve_upstream_capacity():
        nonlocal request_counts_by_provider
        provider_lease, latest_request_counts = _try_reserve_upstream_capacity(
            analyses,
            is_demo_run=is_demo_run,
            allowed_sources=allowed_sources,
        )
        if provider_lease is not None:
            request_counts_by_provider = latest_request_counts
        return provider_lease

    waiting_status = None
    queue_profile = {
        "initial_position": 0,
        "maximum_position": 0,
    }
    admission_started = time.perf_counter()

    def show_waiting(snapshot):
        nonlocal waiting_status
        if queue_profile["initial_position"] == 0:
            queue_profile["initial_position"] = snapshot.position
        queue_profile["maximum_position"] = max(
            queue_profile["maximum_position"],
            snapshot.position,
        )
        label = t.get(
            "msg_analysis_queue_wait",
            "All analysis capacity is in use; queued at position {position}.",
        ).format(position=snapshot.position)
        update_analysis_submission(
            st.session_state,
            submission_token,
            phase=SUBMISSION_PHASE_QUEUED,
            position=snapshot.position,
        )
        if waiting_status is None:
            with run_status_slot.container():
                waiting_status = st.status(
                    label,
                    expanded=False,
                    state="running",
                )
        else:
            waiting_status.update(label=label, expanded=False, state="running")

    owner = session_artifact_owner(st.session_state)
    request_key = _analysis_request_fingerprint(
        analysis_context=analysis_context,
        start_t=start_t,
        end_t=end_t,
        band_filter=band_filter,
        active_demo_profile=st.session_state.get("active_demo_profile"),
    )

    def log_admission(outcome):
        active, queued = ANALYSIS_ADMISSION_GATE.counts()
        admission_values = {
            "outcome": outcome,
            "run_mode": st.session_state.get("run_mode"),
            "wait_seconds": time.perf_counter() - admission_started,
            "initial_queue_position": queue_profile["initial_position"],
            "maximum_queue_position": queue_profile["maximum_position"],
            "active": active,
            "queued": queued,
            "rss_bytes": process_rss_bytes(),
        }
        if outcome == "admitted":
            admission_values = {
                "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                **admission_values,
            }
        log_performance_event(
            "analysis_admission",
            leading_blank_line=(outcome == "admitted"),
            banner_label="ANALYSIS RUN START" if outcome == "admitted" else None,
            **admission_values,
        )

    try:
        permit = ANALYSIS_ADMISSION_GATE.acquire(
            owner=owner,
            request_key=request_key,
            on_wait=show_waiting,
            reserve_capacity=reserve_upstream_capacity,
        )
    except AnalysisDuplicateRequest:
        log_admission("duplicate")
        request_snapshot = getattr(
            ANALYSIS_ADMISSION_GATE,
            "request_snapshot",
            lambda **_kwargs: None,
        )(owner=owner, request_key=request_key)

        def show_existing_request(snapshot):
            """Mirror the original request while this duplicate script follows it."""
            nonlocal waiting_status
            if snapshot.position > 0:
                show_waiting(snapshot)
                return
            update_analysis_submission(
                st.session_state,
                submission_token,
                phase=SUBMISSION_PHASE_RUNNING,
            )
            running_label = t.get(
                "msg_analysis_submission_active",
                "Analysis submitted; Run Analysis is disabled until it finishes.",
            )
            if waiting_status is None:
                with run_status_slot.container():
                    waiting_status = st.status(
                        running_label,
                        expanded=False,
                        state="running",
                    )
            else:
                waiting_status.update(
                    label=running_label,
                    expanded=False,
                    state="running",
                )

        if request_snapshot is None:
            return
        show_existing_request(request_snapshot)
        wait_for_completion = getattr(
            ANALYSIS_ADMISSION_GATE,
            "wait_for_request_completion",
            None,
        )
        if callable(wait_for_completion):
            wait_for_completion(
                owner,
                request_key,
                on_update=show_existing_request,
            )
            return ANALYSIS_RUN_FOLLOWER_COMPLETED
        return
    except AnalysisQueueFull:
        log_admission("queue_full")
        st.session_state.run_mode = None
        run_status_slot.warning(t.get(
            "warn_analysis_queue_full",
            "High demand right now. The analysis queue is full. Please try again shortly.",
        ))
        return
    except AnalysisQueueTimeout:
        log_admission("queue_timeout")
        st.session_state.run_mode = None
        if waiting_status is not None:
            run_status_slot.empty()
        run_status_slot.warning(t.get(
            "warn_analysis_queue_timeout",
            "Analysis capacity did not become available in time. Please run the analysis again.",
        ))
        return
    except ProviderDispatchError as exc:
        log_admission(type(exc).__name__)
        st.session_state.run_mode = None
        if waiting_status is not None:
            run_status_slot.empty()
        run_status_slot.warning(str(exc))
        return

    log_admission("admitted")
    update_analysis_submission(
        st.session_state,
        submission_token,
        phase=SUBMISSION_PHASE_RUNNING,
    )
    if waiting_status is not None:
        run_status_slot.empty()
    run_started = time.perf_counter()
    rss_start = process_rss_bytes()
    run_outcome = "failed"
    try:
        with permit:
            run_outcome = _render_admitted_analysis_run(
                t=t,
                run_status_slot=run_status_slot,
                start_t=start_t,
                end_t=end_t,
                generate_map_plot=generate_map_plot,
                admission_permit=permit,
                analyses=analyses,
                analysis_context=analysis_context,
                presentation_context=presentation_context,
                center_latitude=center_latitude,
                center_longitude=center_longitude,
                active_demo=active_demo,
                active_demo_key=active_demo_key,
                is_demo_run=is_demo_run,
                request_counts_by_provider=request_counts_by_provider,
                committed_source=committed_source,
            )
    except BaseException as exc:
        run_outcome = type(exc).__name__
        raise
    finally:
        active, queued = ANALYSIS_ADMISSION_GATE.counts()
        log_performance_event(
            "analysis_run",
            trailing_blank_line=True,
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
    start_t,
    end_t,
    generate_map_plot,
    admission_permit,
    analyses,
    analysis_context,
    presentation_context,
    center_latitude,
    center_longitude,
    active_demo,
    active_demo_key,
    is_demo_run,
    request_counts_by_provider,
    committed_source,
):
    """Execute an admitted run and return its terminal telemetry outcome."""

    max_peer_distance_km = analysis_context.max_peer_distance_km
    touch_registered_session_artifacts(st.session_state)

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

    deferred_render_data = []
    loading_label = "⏳ Lade..." if st.session_state.lang == "de" else "⏳ Loading..."
    provider_lease = admission_permit.capacity_lease
    if not isinstance(provider_lease, ProviderRunLease):
        status_box.update(label="Database capacity error", state="error", expanded=True)
        st.error("The analysis was admitted without a database reservation.")
        st.session_state.run_mode = None
        return "failed"

    attempted_sources = []
    excluded_sources = set(provider_lease.skipped_sources)
    capacity_replans = 0
    prepared_bundle = None
    final_fetch_failure = None
    attempt_status_log = []

    def report_legacy_retry(index, analysis_count, _analysis):
        attempt_status_log.append(
            f"- Map {index + 1}/{analysis_count}: strict `code = 1` found no "
            "target-side evidence; retrying legacy decode compatibility mode..."
        )
        status_body.markdown("  \n".join(status_log + attempt_status_log))

    while prepared_bundle is None:
        attempt_status_log.clear()
        admission_permit.touch()
        provider = provider_lease.provider
        excluded_sources.update(provider_lease.skipped_sources)
        status_box.update(
            label=f"Preparing complete run from {provider.display_name}...",
            state="running",
            expanded=True,
        )
        try:
            prepared_bundle = prepare_provider_bundle(
                analyses,
                provider_lease=provider_lease,
                is_demo_run=is_demo_run,
                analysis_context=analysis_context,
                center_latitude=center_latitude,
                center_longitude=center_longitude,
                labels=t,
                artifact_paths=_staged_artifact_paths(
                    analyses,
                    provider_key=provider.key,
                ),
                on_legacy_retry=report_legacy_retry,
            )
        except ProviderBundleFetchError as exc:
            final_fetch_failure = exc.fetch_result
            error = final_fetch_failure.error
            is_provider_failure = bool(
                error is not None and error.scope == FetchFailureScope.PROVIDER
            )
            is_capacity_failure = bool(
                error is not None and error.scope == FetchFailureScope.CAPACITY
            )
            if is_provider_failure:
                provider_lease.report_failure(error)
                attempted_sources.append(provider.key)
                excluded_sources.add(provider.key)
            admission_permit.release_capacity_lease()

            may_fallback = is_provider_failure and committed_source is None
            may_replan_capacity = is_capacity_failure and capacity_replans < 3
            if not may_fallback and not may_replan_capacity:
                status_log.append(
                    f"- {provider.display_name} could not complete the data bundle."
                )
                status_body.markdown("  \n".join(status_log))
                status_box.update(
                    label="WSPR data request failed",
                    state="error",
                    expanded=True,
                )
                _render_fetch_error(final_fetch_failure)
                st.session_state.run_mode = None
                return "failed"

            if may_replan_capacity:
                capacity_replans += 1
                status_log.append(
                    "- Cached query availability changed; discarding partial "
                    "results and replanning database capacity..."
                )
                waiting_label = "Waiting for database capacity..."
                allowed_sources = (
                    {committed_source} if committed_source is not None else None
                )
            else:
                status_log.append(
                    f"- {provider.display_name} could not complete the data bundle; "
                    "discarding partial results and trying the next source..."
                )
                waiting_label = "Waiting for fallback database capacity..."
                allowed_sources = None
            status_body.markdown("  \n".join(status_log))

            def refreshed_fallback_request_counts():
                """Reinspect caches throughout a mid-run provider wait."""
                nonlocal request_counts_by_provider
                request_counts_by_provider = _provider_request_counts(
                    analyses,
                    is_demo_run=is_demo_run,
                )
                return request_counts_by_provider

            try:
                provider_lease = UPSTREAM_PROVIDER_DISPATCH.acquire_run(
                    refreshed_fallback_request_counts,
                    excluded_sources=excluded_sources,
                    allowed_sources=allowed_sources,
                    prefer_cache_only=is_demo_run,
                    on_wait=lambda _snapshot: status_box.update(
                        label=waiting_label,
                        state="running",
                        expanded=True,
                    ),
                )
            except (NoProviderAvailable, ProviderAcquireTimeout) as acquire_error:
                status_log.append(f"- No fallback source completed the run: {acquire_error}")
                status_body.markdown("  \n".join(status_log))
                status_box.update(
                    label="All WSPR database sources unavailable",
                    state="error",
                    expanded=True,
                )
                if final_fetch_failure is not None:
                    _render_fetch_error(final_fetch_failure)
                else:
                    st.error(str(acquire_error))
                st.session_state.run_mode = None
                return "failed"
            if not admission_permit.replace_capacity_lease(provider_lease):
                status_box.update(
                    label="Analysis capacity expired",
                    state="error",
                    expanded=True,
                )
                st.session_state.run_mode = None
                return "failed"
        except ProviderBundlePreparationError as exc:
            admission_permit.release_capacity_lease()
            log_performance_event(
                "analysis_preparation_failure",
                source=provider.key,
                failure_scope=FetchFailureScope.LOCAL.value,
                failure_type=type(exc).__name__,
            )
            status_log.append(f"- Local analysis preparation failed: {exc}")
            status_body.markdown("  \n".join(status_log))
            status_box.update(
                label="Analysis preparation failed",
                state="error",
                expanded=True,
            )
            st.error(str(exc))
            st.session_state.run_mode = None
            return "failed"
        else:
            status_log.extend(attempt_status_log)

    provider_lease.report_success()
    selected_provider = provider_lease.provider
    selected_source_key = provider_lease.source_key
    admission_permit.release_capacity_lease()
    set_active_run_database_source(
        st.session_state,
        run_id=st.session_state.run_id,
        source_key=selected_source_key,
    )
    retire_registered_session_artifacts(st.session_state)
    clear_rendered_result_state(st.session_state)
    for prepared_analysis in prepared_bundle.analyses:
        if prepared_analysis.artifact_path is not None:
            register_session_artifact(
                st.session_state,
                prepared_analysis.artifact_path,
            )

    selection_reason = _database_selection_reason(
        selected_source_key,
        failed_sources=attempted_sources,
        committed_source=committed_source,
        skipped_source_reasons=provider_lease.skipped_source_reasons,
        used_cache_affinity=provider_lease.used_cache_affinity,
    )
    status_log.append(
        _database_origin_status(
            selected_source_key,
            selection_reason=selection_reason,
        )
    )
    for index, prepared_analysis in enumerate(prepared_bundle.analyses):
        status_log.append(
            f"- Map {index + 1}/{len(prepared_bundle.analyses)}: "
            f"{prepared_analysis.analysis['title']} — "
            f"{_query_fetch_status(prepared_analysis)}"
        )
    status_body.markdown("  \n".join(status_log))
    is_nonprimary_source = (
        selected_provider != UPSTREAM_PROVIDER_DISPATCH.providers[0]
    )
    log_performance_event(
        "database_source_selected",
        source=selected_source_key,
        source_label=selected_provider.display_name,
        is_fallback=is_nonprimary_source,
        is_nonprimary_source=is_nonprimary_source,
        is_failure_fallback=(selection_reason == "failure_fallback"),
        selection_reason=selection_reason,
        cache_affinity_applied=provider_lease.used_cache_affinity,
        cache_affinity_bypassed_sources=(
            provider_lease.cache_affinity_bypassed_sources
        ),
        planned_network_requests=int(
            request_counts_by_provider.get(selected_source_key, 0)
        ),
        actual_network_requests=provider_lease.actual_requests,
        is_demo_run=is_demo_run,
        demo_profile=active_demo_key,
        failed_sources=attempted_sources,
        skipped_source_reasons=tuple(
            f"{source_key}:{reason.value}"
            for source_key, reason in provider_lease.skipped_source_reasons
        ),
    )

    for index, prepared_analysis in enumerate(prepared_bundle.analyses):
        admission_permit.touch()
        analysis = prepared_analysis.analysis
        profile_timer = prepared_analysis.profile_timer
        parquet_path = prepared_analysis.artifact_path

        if prepared_analysis.warning_message or parquet_path is None:
            profile_timer.log_report(analysis_title=analysis["title"])
            st.warning(
                prepared_analysis.warning_message
                or t["warn_no_data"].format(title=analysis["title"])
            )
            st.markdown("---")
            continue

        try:
            df = read_parquet_artifact(parquet_path)
        except (OSError, ValueError) as exc:
            status_box.update(
                label="Prepared analysis data became unavailable",
                state="error",
                expanded=True,
            )
            st.error(f"Error reading prepared analysis data: {exc}")
            st.session_state.run_mode = None
            log_performance_event(
                "analysis_preparation_failure",
                source=selected_source_key,
                failure_scope=FetchFailureScope.LOCAL.value,
                failure_type=type(exc).__name__,
                stage="read_prepared_artifact",
            )
            return "failed"

        profile_timer.add_memory(
            "staged post-filter dataframe",
            df=df,
            detail=prepared_bundle.database_source.display_name,
        )
        with st.spinner(t["msg_proc"].format(id=analysis["id"])):
            status_box.update(
                label=f"Rendering maps... ({index + 1}/{len(prepared_bundle.analyses)})",
                state="running",
                expanded=True,
            )
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
                    max_peer_distance_km,
                    analysis["id"],
                    st.session_state.val_min_stations,
                    center_latitude,
                    center_longitude,
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

            result_context = build_result_context(
                analysis,
                analysis_context,
                start_t,
                end_t,
                t,
            )
            station_type = remote_station_type(analysis["id"])
            if analysis["is_compare"]:
                map_subtitle = t.get(
                    "sub_results_map_compare",
                    "Geographic overview of station-balanced ΔSNR and "
                    "Decode Outcomes.",
                )
            else:
                map_subtitle = t.get(
                    "sub_results_map_success",
                    "Remote {station_type} stations grouped by distance and "
                    "direction, showing station-balanced Success Rate.",
                ).format(station_type=station_type)
            with st.container(
                key=f"results_evidence_flow_{analysis['id']}_{run_id}"
            ):
                st.markdown(
                    result_context_html(result_context),
                    unsafe_allow_html=True,
                )
                with st.container(
                    key=f"results_evidence_spine_{analysis['id']}_{run_id}"
                ):
                    level_one_container = st.container(
                        key=(
                            f"results_evidence_level_1_"
                            f"{analysis['id']}_{run_id}"
                        )
                    )
                    level_one_container.markdown(
                        evidence_level_header_html(
                            1,
                            t.get("lbl_results_level_run", "Complete run"),
                            t.get("hdr_results_map_view", "Map View"),
                            map_subtitle,
                        ),
                        unsafe_allow_html=True,
                    )
                    with level_one_container:
                        try:
                            with (
                                profile_timer.span(
                                    matplotlib_render_span_label("map render")
                                ),
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
                                analysis=analysis,
                                parquet_path=parquet_path,
                                start_t=start_t,
                                end_t=end_t,
                                max_peer_distance_km=max_peer_distance_km,
                                base_min_stations=st.session_state.val_min_stations,
                                lat_0=center_latitude,
                                lon_0=center_longitude,
                                analysis_context=analysis_context,
                                presentation_context=presentation_context,
                                database_source=selected_source_key,
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

                    level_one_container.markdown(
                        transition_prompt_html(
                            t.get(
                                "txt_results_transition_scope",
                                "Select distance and direction to inspect a "
                                "geographic scope",
                            )
                        ),
                        unsafe_allow_html=True,
                    )

                    inspector_container = st.container()
                    skeleton_ph = inspector_container.empty()

                    with skeleton_ph.container():
                        st.markdown(
                            evidence_level_header_html(
                                2,
                                t.get(
                                    "lbl_results_level_scope",
                                    "Geographic scope",
                                ),
                                t.get(
                                    "hdr_results_segment_inspector",
                                    "Segment Inspector",
                                ),
                                t.get(
                                    "sub_results_segment_inspector",
                                    "Choose one or more distance ranges and "
                                    "directions. All evidence below follows "
                                    "the active scope.",
                                ),
                            ),
                            unsafe_allow_html=True,
                        )
                        wait_left, wait_right = st.columns(2)
                        with wait_left:
                            st.selectbox(
                                t.get(
                                    "lbl_results_distance_range",
                                    "Distance range",
                                ),
                                [loading_label],
                                key=f"w_dist_{analysis['id']}_{run_id}",
                                disabled=True,
                                label_visibility="collapsed",
                            )
                        with wait_right:
                            st.selectbox(
                                t.get(
                                    "lbl_results_direction",
                                    "Direction",
                                ),
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
                    max_peer_distance_km,
                    analysis_context,
                    presentation_context,
                    analysis_start_t=data["start_t"],
                    analysis_end_t=data["end_t"],
                    analysis_kind=data["analysis"].get("analysis_kind", "comparison"),
                    show_export_button=(index == len(deferred_render_data) - 1),
                    timing_collector=data["profile_timer"],
                    timing_label=inspector_span,
                )

    return "completed"
