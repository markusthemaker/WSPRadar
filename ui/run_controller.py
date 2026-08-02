"""Streamlit run orchestration for WSPRadar analyses."""

from dataclasses import dataclass
from datetime import datetime, timezone
import gc
import hashlib
import json
import math
from pathlib import Path
import time
import uuid

import streamlit as st

from config import CACHE_DIR, DEMO_PROFILES, MAX_ANALYSIS_RESULT_ROWS
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
    validate_registered_session_artifacts,
)
from core.data_engine import cleanup_old_parquets, estimate_uncached_requests
from core.fetch_models import (
    DatabaseSource,
    FetchFailureScope,
    FetchSource,
    RESULT_ROW_LIMIT_EXCEEDED_CODE,
)
from core.input_validation import is_valid_callsign, is_valid_locator
from core.map_data_artifacts import (
    MAP_DATA_ARTIFACT_SCHEMA_VERSION,
    MapDataArtifactPaths,
    read_map_data_artifacts,
    write_map_data_artifacts,
)
from core.math_utils import locator_to_latlon
from core.matplotlib_runtime import matplotlib_profile_collector
from core.performance_timer import (
    PerformanceTimer,
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
    PreparedQueryFetch,
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
from ui.result_guidance import (
    RESULT_GUIDANCE_CONTEXT,
    RESULT_GUIDANCE_MAP,
    render_result_guidance_popover,
)
from ui.results_export import register_map_export_context
from ui.presentation_context_adapter import build_presentation_context_from_session_state
from ui.result_state import (
    COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
    clear_rendered_result_state,
    get_active_run_database_source,
    get_completed_run_snapshot,
    publish_completed_run_snapshot,
    reset_result_state,
    set_active_run_database_source,
)


ANALYSIS_RUN_FOLLOWER_COMPLETED = "duplicate_follower_completed"
COMPLETED_RUN_RERENDER_UNAVAILABLE = "completed_rerender_unavailable"

_SNAPSHOT_OUTCOME_RENDERABLE = "renderable"
_SNAPSHOT_OUTCOME_PREPARED_NO_DATA = "prepared_no_data"
_SNAPSHOT_OUTCOME_MAP_NO_DATA = "map_no_data"
_SNAPSHOT_OUTCOMES = frozenset({
    _SNAPSHOT_OUTCOME_RENDERABLE,
    _SNAPSHOT_OUTCOME_PREPARED_NO_DATA,
    _SNAPSHOT_OUTCOME_MAP_NO_DATA,
})


@dataclass(frozen=True)
class _StagedAnalysisArtifactPaths:
    """Hold the evidence and compact render paths for one provider attempt."""

    evidence_path: Path
    map_data_paths: MapDataArtifactPaths


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


def _analysis_plan_fingerprint(analyses) -> str:
    """Fingerprint ordered scientific plans without localized presentation text."""
    plan_rows = []
    for analysis in analyses:
        plan_rows.append({
            "id": str(analysis.get("id", "")),
            "analysis_kind": str(analysis.get("analysis_kind", "")),
            "is_compare": bool(analysis.get("is_compare")),
            "is_sequential": bool(analysis.get("is_sequential")),
            "is_local_median": bool(analysis.get("is_local_median")),
            "response_format": str(analysis.get("response_format", "csv")),
            "absolute_mode": analysis.get("absolute_mode"),
            "absolute_method_version": analysis.get("absolute_method_version"),
            "query_sha256": hashlib.sha256(
                str(analysis.get("query", "")).encode("utf-8")
            ).hexdigest(),
            "legacy_query_sha256": hashlib.sha256(
                str(analysis.get("legacy_query", "")).encode("utf-8")
            ).hexdigest(),
        })
    canonical = json.dumps(plan_rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _render_fetch_error(
    fetch_result,
    labels,
    *,
    exclude_special_callsigns,
):
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
    if error.code == RESULT_ROW_LIMIT_EXCEEDED_CODE:
        failure_diagnostics["max_result_rows"] = MAX_ANALYSIS_RESULT_ROWS
    if fetch_result.artifact_path is not None:
        artifact_parts = set(fetch_result.artifact_path.parts)
        if ArtifactNamespace.DEMO_QUERY.value in artifact_parts:
            failure_diagnostics["cache_namespace"] = ArtifactNamespace.DEMO_QUERY.value
            failure_diagnostics["cache_policy"] = "demo_absolute_24h"
        elif ArtifactNamespace.QUERY.value in artifact_parts:
            failure_diagnostics["cache_namespace"] = ArtifactNamespace.QUERY.value
            failure_diagnostics["cache_policy"] = "standard_access_1h"
    log_performance_event("analysis_fetch_failure", **failure_diagnostics)
    if error.code == RESULT_ROW_LIMIT_EXCEEDED_CODE:
        special_callsign_advice = ""
        if not exclude_special_callsigns:
            special_callsign_advice = labels[
                "warn_analysis_result_row_limit_special_callsign_advice"
            ].format(
                special_callsign_label=labels["lbl_exclude_special"],
            )
        max_rows = f"{MAX_ANALYSIS_RESULT_ROWS:,}".replace(
            ",",
            str(labels["fmt_results_thousands_separator"]),
        )
        st.warning(
            labels["warn_analysis_result_row_limit"].format(
                max_rows=max_rows,
                special_callsign_advice=special_callsign_advice,
                max_peer_distance_label=labels["lbl_max_dist"],
                neighborhood_radius_label=labels["lbl_ref_radius_km"],
            )
        )
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
    """Return all unique unregistered paths for one provider attempt."""
    attempt_token = f"{provider_key}_{uuid.uuid4().hex[:12]}"
    return {
        analysis["id"]: _StagedAnalysisArtifactPaths(
            evidence_path=session_artifact_path(
                CACHE_DIR,
                st.session_state,
                run_id=f"{st.session_state.run_id}_{attempt_token}",
                analysis_id=analysis["id"],
            ),
            map_data_paths=MapDataArtifactPaths(
                station_rows_path=session_artifact_path(
                    CACHE_DIR,
                    st.session_state,
                    run_id=f"{st.session_state.run_id}_{attempt_token}",
                    analysis_id=analysis["id"],
                    artifact_kind="map_stations",
                ),
                segment_rows_path=session_artifact_path(
                    CACHE_DIR,
                    st.session_state,
                    run_id=f"{st.session_state.run_id}_{attempt_token}",
                    analysis_id=analysis["id"],
                    artifact_kind="map_segments",
                ),
            ),
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


def _format_query_fetch_status(
    query_fetches,
    *,
    has_legacy_query,
    has_usable_result,
):
    """Render strict and legacy delivery tiers from normalized query metadata."""
    if not query_fetches:
        return "query delivery details unavailable"

    has_legacy_fetch = any(
        query_fetch.decode_filter_mode == DECODE_FILTER_LEGACY
        for query_fetch in query_fetches
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

    if has_legacy_query and not has_legacy_fetch:
        fetch_descriptions.append("legacy: not needed")
    return "; ".join(fetch_descriptions)


def _query_fetch_status(prepared_analysis):
    """Render query delivery status from one newly prepared analysis."""
    return _format_query_fetch_status(
        prepared_analysis.query_fetches,
        has_legacy_query=bool(prepared_analysis.analysis.get("legacy_query")),
        has_usable_result=(
            prepared_analysis.warning_message is None
            and prepared_analysis.artifact_path is not None
        ),
    )


def _refresh_session_artifacts_before_cleanup():
    """Protect this session's retained artifacts before global TTL cleanup."""
    touch_registered_session_artifacts(st.session_state)
    return cleanup_old_parquets()


def _analysis_snapshot_contract(analysis) -> dict:
    """Return the stable non-presentation contract for one result block."""
    return {
        "id": str(analysis.get("id", "")),
        "analysis_kind": str(analysis.get("analysis_kind", "")),
        "is_compare": bool(analysis.get("is_compare")),
        "is_sequential": bool(analysis.get("is_sequential")),
        "absolute_method_version": analysis.get("absolute_method_version"),
    }


def _serialize_query_fetches(query_fetches) -> tuple[dict, ...]:
    """Return session-safe strict/legacy provenance for one completed query."""
    return tuple({
        "decode_filter_mode": str(query_fetch.decode_filter_mode),
        "elapsed_seconds": float(query_fetch.elapsed_seconds),
        "delivery_source": query_fetch.delivery_source.value,
    } for query_fetch in query_fetches)


def _validate_completed_run_snapshot(
    *,
    analyses,
    request_fingerprint,
    analysis_plan_fingerprint,
    committed_source,
    session_owner,
):
    """Return a reusable snapshot only when identity and artifacts still match."""
    snapshot = get_completed_run_snapshot(st.session_state)
    if snapshot is None:
        return None
    if snapshot.get("run_id") != st.session_state.get("run_id"):
        return None
    if snapshot.get("request_fingerprint") != request_fingerprint:
        return None
    if snapshot.get("analysis_plan_fingerprint") != analysis_plan_fingerprint:
        return None
    if snapshot.get("database_source") != committed_source or not committed_source:
        return None
    try:
        DatabaseSource(snapshot["database_source"])
    except (KeyError, TypeError, ValueError):
        return None
    if (
        snapshot.get("map_data_schema_version")
        != MAP_DATA_ARTIFACT_SCHEMA_VERSION
    ):
        return None

    snapshot_analyses = snapshot.get("analyses")
    if not isinstance(snapshot_analyses, (list, tuple)):
        return None
    if len(snapshot_analyses) != len(analyses) or not analyses:
        return None

    valid_delivery_sources = {source.value for source in FetchSource}
    for analysis, snapshot_analysis in zip(analyses, snapshot_analyses):
        if not isinstance(snapshot_analysis, dict):
            return None
        if snapshot_analysis.get("analysis") != _analysis_snapshot_contract(analysis):
            return None
        outcome = snapshot_analysis.get("outcome")
        if outcome not in _SNAPSHOT_OUTCOMES:
            return None

        evidence_path = snapshot_analysis.get("evidence_path")
        station_rows_path = snapshot_analysis.get("station_rows_path")
        segment_rows_path = snapshot_analysis.get("segment_rows_path")
        required_path_specs = []
        if outcome == _SNAPSHOT_OUTCOME_RENDERABLE:
            required_path_specs.extend([
                (evidence_path, "spots"),
                (station_rows_path, "map_stations"),
                (segment_rows_path, "map_segments"),
            ])
        elif outcome == _SNAPSHOT_OUTCOME_MAP_NO_DATA:
            required_path_specs.append((evidence_path, "spots"))
            if station_rows_path is not None or segment_rows_path is not None:
                return None
        elif any(
            path is not None
            for path in (evidence_path, station_rows_path, segment_rows_path)
        ):
            return None
        if any(
            not isinstance(path, str) or not path
            for path, _artifact_kind in required_path_specs
        ):
            return None
        if required_path_specs:
            try:
                validate_registered_session_artifacts(
                    CACHE_DIR,
                    st.session_state,
                    analysis_id=analysis["id"],
                    artifact_paths_by_kind={
                        artifact_kind: path
                        for path, artifact_kind in required_path_specs
                    },
                    expected_session_owner=session_owner,
                )
            except (OSError, RuntimeError, TypeError, ValueError):
                return None

        selected_decode_filter_mode = snapshot_analysis.get(
            "selected_decode_filter_mode"
        )
        if selected_decode_filter_mode not in {
            DECODE_FILTER_STRICT,
            DECODE_FILTER_LEGACY,
        }:
            return None
        query_fetches = snapshot_analysis.get("query_fetches")
        if not isinstance(query_fetches, (list, tuple)) or not query_fetches:
            return None
        for query_fetch in query_fetches:
            if not isinstance(query_fetch, dict):
                return None
            if query_fetch.get("decode_filter_mode") not in {
                DECODE_FILTER_STRICT,
                DECODE_FILTER_LEGACY,
            }:
                return None
            elapsed_seconds = query_fetch.get("elapsed_seconds")
            if (
                isinstance(elapsed_seconds, bool)
                or not isinstance(elapsed_seconds, (int, float))
                or not math.isfinite(elapsed_seconds)
                or elapsed_seconds < 0
            ):
                return None
            if query_fetch.get("delivery_source") not in valid_delivery_sources:
                return None
        if (
            query_fetches[-1].get("decode_filter_mode")
            != selected_decode_filter_mode
        ):
            return None
    return snapshot


def _snapshot_analysis_entry(
    prepared_analysis,
    *,
    outcome,
    map_data_paths=None,
) -> dict:
    """Build one language-free completed-analysis snapshot entry."""
    evidence_path = prepared_analysis.artifact_path
    return {
        "analysis": _analysis_snapshot_contract(prepared_analysis.analysis),
        "outcome": str(outcome),
        "evidence_path": (
            str(Path(evidence_path).resolve())
            if evidence_path is not None
            else None
        ),
        "station_rows_path": (
            str(Path(map_data_paths.station_rows_path).resolve())
            if map_data_paths is not None
            else None
        ),
        "segment_rows_path": (
            str(Path(map_data_paths.segment_rows_path).resolve())
            if map_data_paths is not None
            else None
        ),
        "selected_decode_filter_mode": str(
            prepared_analysis.analysis.get("decode_filter_mode", "")
        ),
        "query_fetches": _serialize_query_fetches(
            prepared_analysis.query_fetches
        ),
    }


def _invalidate_completed_rerender(translations) -> str:
    """Retire an unusable implicit result without starting replacement work."""
    st.session_state.run_mode = None
    reset_result_state(st.session_state)
    st.warning(translations["warn_analysis_cache_expired"])
    return COMPLETED_RUN_RERENDER_UNAVAILABLE


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
    render_map_figure=None,
    is_existing_run_rerender=False,
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
        st.error(t["err_callsign_format"])
        st.session_state.run_mode = None
        return

    if not is_valid_locator(qth_locator):
        st.error(t["err_qth_format"])
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
        log_performance_event(
            "analysis_configuration_failure",
            failure_type=type(exc).__name__,
            technical_error=str(exc),
        )
        st.error(t["err_analysis_configuration_invalid"])
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
    analysis_plan_key = _analysis_plan_fingerprint(analyses)
    execution_kind = (
        "completed_rerender"
        if is_existing_run_rerender
        else "analysis"
    )
    completed_run_snapshot = None
    if is_existing_run_rerender:
        completed_run_snapshot = _validate_completed_run_snapshot(
            analyses=analyses,
            request_fingerprint=request_key,
            analysis_plan_fingerprint=analysis_plan_key,
            committed_source=committed_source,
            session_owner=owner,
        )
        if completed_run_snapshot is None or not callable(render_map_figure):
            return _invalidate_completed_rerender(t)

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
            "execution_kind": execution_kind,
        }
        if outcome == "admitted":
            admission_values = {
                "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                **admission_values,
            }
        log_performance_event(
            "analysis_admission",
            leading_blank_line=(outcome == "admitted"),
            banner_label=(
                "COMPLETED RESULT RERENDER START"
                if outcome == "admitted" and is_existing_run_rerender
                else "ANALYSIS RUN START" if outcome == "admitted" else None
            ),
            **admission_values,
        )

    try:
        permit = ANALYSIS_ADMISSION_GATE.acquire(
            owner=owner,
            request_key=request_key,
            on_wait=show_waiting,
            reserve_capacity=(
                None
                if is_existing_run_rerender
                else reserve_upstream_capacity
            ),
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
        if not is_existing_run_rerender:
            st.session_state.run_mode = None
        run_status_slot.warning(t.get(
            "warn_analysis_queue_full",
            "High demand right now. The analysis queue is full. Please try again shortly.",
        ))
        return
    except AnalysisQueueTimeout:
        log_admission("queue_timeout")
        if not is_existing_run_rerender:
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
            if is_existing_run_rerender:
                run_outcome = _render_completed_analysis_run(
                    t=t,
                    run_status_slot=run_status_slot,
                    start_t=start_t,
                    end_t=end_t,
                    render_map_figure=render_map_figure,
                    admission_permit=permit,
                    analyses=analyses,
                    analysis_context=analysis_context,
                    presentation_context=presentation_context,
                    center_latitude=center_latitude,
                    center_longitude=center_longitude,
                    completed_run_snapshot=completed_run_snapshot,
                )
            else:
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
                    request_fingerprint=request_key,
                    analysis_plan_fingerprint=analysis_plan_key,
                )
    except Exception as exc:
        run_outcome = type(exc).__name__
        if is_existing_run_rerender:
            return _invalidate_completed_rerender(t)
        st.session_state.run_mode = None
        reset_result_state(st.session_state)
        raise
    except BaseException as exc:
        run_outcome = type(exc).__name__
        raise
    finally:
        active, queued = ANALYSIS_ADMISSION_GATE.counts()
        log_performance_event(
            "analysis_run",
            trailing_blank_line=True,
            outcome=run_outcome,
            execution_kind=execution_kind,
            run_mode=st.session_state.get("run_mode"),
            duration_seconds=time.perf_counter() - run_started,
            active_after_release=active,
            queued_after_release=queued,
            rss_start_bytes=rss_start,
            rss_end_bytes=process_rss_bytes(),
            process_peak_rss_bytes=process_peak_rss_bytes(),
        )


def _render_map_result_block(
    *,
    t,
    analysis,
    plot_result,
    parquet_path,
    map_data_paths,
    start_t,
    end_t,
    loading_label,
    max_peer_distance_km,
    center_latitude,
    center_longitude,
    analysis_context,
    presentation_context,
    database_source,
    profile_timer,
):
    """Render one map block and return its deferred Inspector inputs."""
    fig = plot_result.figure
    enriched_df = plot_result.map_data.station_rows
    line1_str = plot_result.footer_text
    run_id = st.session_state.get("run_id", 0)
    profile_timer.add_memory("map station dataframe", df=enriched_df)

    result_context = build_result_context(
        analysis,
        analysis_context,
        start_t,
        end_t,
        t,
    )
    station_type = remote_station_type(analysis["id"])
    if analysis["is_compare"]:
        map_subtitle = t["sub_results_map_compare"]
    else:
        map_subtitle = t["sub_results_map_success"].format(
            station_type=station_type
        )
    with st.container(
        key=f"results_evidence_flow_{analysis['id']}_{run_id}"
    ):
        st.markdown(
            result_context_html(result_context),
            unsafe_allow_html=True,
        )
        render_result_guidance_popover(
            RESULT_GUIDANCE_CONTEXT,
            result_context.title,
            language=presentation_context.language,
            translations=t,
            key=(
                f"results_guidance_context_"
                f"{analysis['id']}_{run_id}"
            ),
            analysis_id=analysis["id"],
            is_compare=analysis["is_compare"],
            is_sequential=analysis["is_sequential"],
            analysis_context=analysis_context,
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
                    t["lbl_results_level_run"],
                    t["hdr_results_map_view"],
                    map_subtitle,
                ),
                unsafe_allow_html=True,
            )
            with level_one_container:
                render_result_guidance_popover(
                    RESULT_GUIDANCE_MAP,
                    t["hdr_results_map_view"],
                    language=presentation_context.language,
                    translations=t,
                    key=(
                        f"results_guidance_map_"
                        f"{analysis['id']}_{run_id}"
                    ),
                    analysis_id=analysis["id"],
                    is_compare=analysis["is_compare"],
                    is_sequential=analysis["is_sequential"],
                    analysis_context=analysis_context,
                )
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
                        map_data_paths=map_data_paths,
                        start_t=start_t,
                        end_t=end_t,
                        max_peer_distance_km=max_peer_distance_km,
                        base_min_stations=st.session_state.val_min_stations,
                        lat_0=center_latitude,
                        lon_0=center_longitude,
                        analysis_context=analysis_context,
                        presentation_context=presentation_context,
                        database_source=database_source,
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
                    t["txt_results_transition_scope"]
                ),
                unsafe_allow_html=True,
            )

            inspector_container = st.container()
            skeleton_ph = inspector_container.empty()

            with skeleton_ph.container():
                st.markdown(
                    evidence_level_header_html(
                        2,
                        t["lbl_results_level_scope"],
                        t["hdr_results_segment_inspector"],
                        t["sub_results_segment_inspector"],
                    ),
                    unsafe_allow_html=True,
                )
                wait_left, wait_right = st.columns(2)
                with wait_left:
                    st.selectbox(
                        t["lbl_results_distance_range"],
                        [loading_label],
                        key=f"w_dist_{analysis['id']}_{run_id}",
                        disabled=True,
                        label_visibility="collapsed",
                    )
                with wait_right:
                    st.selectbox(
                        t["lbl_results_direction"],
                        [loading_label],
                        key=f"w_dir_{analysis['id']}_{run_id}",
                        disabled=True,
                        label_visibility="collapsed",
                    )

    return {
        "analysis": analysis,
        "enriched_df": enriched_df,
        "parquet_path": parquet_path,
        "line1_str": line1_str,
        "skeleton_ph": skeleton_ph,
        "inspector_container": inspector_container,
        "start_t": start_t,
        "end_t": end_t,
        "profile_timer": profile_timer,
    }


def _render_deferred_inspectors(
    deferred_render_data,
    *,
    t,
    admission_permit,
    max_peer_distance_km,
    analysis_context,
    presentation_context,
):
    """Render every Inspector after its map skeleton is visible."""
    for index, data in enumerate(deferred_render_data):
        admission_permit.touch()
        data["skeleton_ph"].empty()
        with data["inspector_container"]:
            inspector_span = (
                "first Segment Inspector render"
                if index == 0
                else "Segment Inspector render"
            )
            with matplotlib_profile_collector(data["profile_timer"]):
                render_segment_inspector(
                    data["analysis"]["id"],
                    data["analysis"]["title"],
                    data["analysis"]["is_compare"],
                    data["analysis"]["is_sequential"],
                    data["enriched_df"],
                    data["parquet_path"],
                    data["line1_str"],
                    t,
                    max_peer_distance_km,
                    analysis_context,
                    presentation_context,
                    analysis_start_t=data["start_t"],
                    analysis_end_t=data["end_t"],
                    analysis_kind=data["analysis"]["analysis_kind"],
                    show_export_button=(
                        index == len(deferred_render_data) - 1
                    ),
                    timing_collector=data["profile_timer"],
                    timing_label=inspector_span,
                )


def _render_completed_analysis_run(
    *,
    t,
    run_status_slot,
    start_t,
    end_t,
    render_map_figure,
    admission_permit,
    analyses,
    analysis_context,
    presentation_context,
    center_latitude,
    center_longitude,
    completed_run_snapshot,
):
    """Render a validated completed snapshot without provider or query work."""
    max_peer_distance_km = analysis_context.max_peer_distance_km
    selected_source_key = completed_run_snapshot["database_source"]
    source_label = DatabaseSource(selected_source_key).display_name
    clear_rendered_result_state(
        st.session_state,
        preserve_inspector_cache=True,
    )

    with run_status_slot.container():
        status_box = st.status(
            f"Restoring completed {st.session_state.run_mode} analysis...",
            expanded=True,
            state="running",
        )
        with status_box:
            status_body = st.empty()

    status_log = [
        "**System Audit Status:**",
        "- Reusing completed station and segment aggregates; no database request was made.",
        (
            "- Database origin for complete run: "
            f"**{source_label}** (committed source)"
        ),
    ]
    prepared_render_entries = []
    for analysis, snapshot_analysis in zip(
        analyses,
        completed_run_snapshot["analyses"],
    ):
        restored_analysis = dict(analysis)
        restored_analysis["decode_filter_mode"] = snapshot_analysis[
            "selected_decode_filter_mode"
        ]
        query_fetches = tuple(
            PreparedQueryFetch(
                decode_filter_mode=query_fetch["decode_filter_mode"],
                elapsed_seconds=float(query_fetch["elapsed_seconds"]),
                delivery_source=FetchSource(query_fetch["delivery_source"]),
            )
            for query_fetch in snapshot_analysis["query_fetches"]
        )
        query_fetch_status = _format_query_fetch_status(
            query_fetches,
            has_legacy_query=bool(restored_analysis.get("legacy_query")),
            has_usable_result=(
                snapshot_analysis["outcome"]
                != _SNAPSHOT_OUTCOME_PREPARED_NO_DATA
            ),
        )
        status_log.append(
            f"- Map {len(prepared_render_entries) + 1}/{len(analyses)}: "
            f"{restored_analysis['title']} — "
            f"{query_fetch_status}"
        )
        prepared_render_entries.append((restored_analysis, snapshot_analysis))
    status_body.markdown("  \n".join(status_log))

    deferred_render_data = []
    loading_label = t["msg_loading"]

    def fail_completed_rerender(exc, *, stage, plot_result=None):
        """Retire a completed snapshot that failed during local restoration."""
        if plot_result is not None:
            try:
                dispose_matplotlib_figure(plot_result.figure)
            except Exception:
                pass
        status_box.update(
            label="Completed analysis data became unavailable",
            state="error",
            expanded=True,
        )
        log_performance_event(
            "analysis_preparation_failure",
            source=selected_source_key,
            failure_scope=FetchFailureScope.LOCAL.value,
            failure_type=type(exc).__name__,
            stage=stage,
        )
        return _invalidate_completed_rerender(t)

    for index, (analysis, snapshot_analysis) in enumerate(prepared_render_entries):
        admission_permit.touch()
        outcome = snapshot_analysis["outcome"]
        if outcome != _SNAPSHOT_OUTCOME_RENDERABLE:
            st.warning(t["warn_no_data"].format(title=analysis["title"]))
            st.markdown("---")
            continue

        profile_timer = PerformanceTimer()
        map_data_paths = MapDataArtifactPaths(
            station_rows_path=Path(snapshot_analysis["station_rows_path"]),
            segment_rows_path=Path(snapshot_analysis["segment_rows_path"]),
        )
        plot_result = None
        try:
            with profile_timer.span("completed map aggregate read"):
                map_data = read_map_data_artifacts(
                    map_data_paths,
                    analysis_id=analysis["id"],
                    is_compare=analysis["is_compare"],
                    is_sequential=analysis["is_sequential"],
                    analysis_kind=analysis["analysis_kind"],
                )
            profile_timer.add_memory(
                "completed map station dataframe",
                df=map_data.station_rows,
            )
            status_box.update(
                label=f"Rendering maps... ({index + 1}/{len(analyses)})",
                state="running",
                expanded=True,
            )
            with (
                profile_timer.span("map generation"),
                matplotlib_profile_collector(profile_timer),
            ):
                plot_result = render_map_figure(
                    map_data,
                    title=analysis["title"],
                    start_t=start_t,
                    end_t=end_t,
                    max_dist_km=max_peer_distance_km,
                    base_min_stations=st.session_state.val_min_stations,
                    lat_0=center_latitude,
                    lon_0=center_longitude,
                    analysis_context=analysis_context,
                    presentation_context=presentation_context,
                    timing_collector=profile_timer,
                )
            del map_data
            deferred_render_entry = _render_map_result_block(
                t=t,
                analysis=analysis,
                plot_result=plot_result,
                parquet_path=Path(snapshot_analysis["evidence_path"]),
                map_data_paths=map_data_paths,
                start_t=start_t,
                end_t=end_t,
                loading_label=loading_label,
                max_peer_distance_km=max_peer_distance_km,
                center_latitude=center_latitude,
                center_longitude=center_longitude,
                analysis_context=analysis_context,
                presentation_context=presentation_context,
                database_source=selected_source_key,
                profile_timer=profile_timer,
            )
            plot_result = None
        except Exception as exc:
            return fail_completed_rerender(
                exc,
                stage="restore_completed_map",
                plot_result=plot_result,
            )
        deferred_render_data.append(deferred_render_entry)
        gc.collect()
        st.markdown("---")

    try:
        _render_deferred_inspectors(
            deferred_render_data,
            t=t,
            admission_permit=admission_permit,
            max_peer_distance_km=max_peer_distance_km,
            analysis_context=analysis_context,
            presentation_context=presentation_context,
        )
    except Exception as exc:
        return fail_completed_rerender(
            exc,
            stage="restore_completed_inspectors",
        )
    status_box.update(label="Complete", state="complete", expanded=False)
    return "completed"


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
    request_fingerprint,
    analysis_plan_fingerprint,
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
    snapshot_analysis_entries = []
    loading_label = t["msg_loading"]
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
    staged_artifact_paths = None
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
            staged_artifact_paths = _staged_artifact_paths(
                analyses,
                provider_key=provider.key,
            )
            prepared_bundle = prepare_provider_bundle(
                analyses,
                provider_lease=provider_lease,
                is_demo_run=is_demo_run,
                analysis_context=analysis_context,
                center_latitude=center_latitude,
                center_longitude=center_longitude,
                labels=t,
                artifact_paths={
                    analysis_id: paths.evidence_path
                    for analysis_id, paths in staged_artifact_paths.items()
                },
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
                if (
                    error is not None
                    and error.code == RESULT_ROW_LIMIT_EXCEEDED_CODE
                ):
                    terminal_status_label = t["status_analysis_result_row_limit"]
                    status_log.append(f"- {terminal_status_label}.")
                else:
                    terminal_status_label = "WSPR data request failed"
                    status_log.append(
                        f"- {provider.display_name} could not complete the data bundle."
                    )
                status_body.markdown("  \n".join(status_log))
                status_box.update(
                    label=terminal_status_label,
                    state="error",
                    expanded=True,
                )
                _render_fetch_error(
                    final_fetch_failure,
                    t,
                    exclude_special_callsigns=(
                        analysis_context.exclude_special_callsigns
                    ),
                )
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
                    _render_fetch_error(
                        final_fetch_failure,
                        t,
                        exclude_special_callsigns=(
                            analysis_context.exclude_special_callsigns
                        ),
                    )
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
                technical_error=str(exc),
            )
            localized_preparation_error = t["err_analysis_processing_failed"]
            status_log.append(f"- {localized_preparation_error}")
            status_body.markdown("  \n".join(status_log))
            status_box.update(
                label=localized_preparation_error,
                state="error",
                expanded=True,
            )
            st.error(localized_preparation_error)
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
            snapshot_analysis_entries.append(_snapshot_analysis_entry(
                prepared_analysis,
                outcome=_SNAPSHOT_OUTCOME_PREPARED_NO_DATA,
            ))
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
            reset_result_state(st.session_state)
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
                    analysis_kind=analysis["analysis_kind"],
                    theme="dark",
                    timing_collector=profile_timer,
                )
            del df
            gc.collect()

            if plot_result is None:
                snapshot_analysis_entries.append(_snapshot_analysis_entry(
                    prepared_analysis,
                    outcome=_SNAPSHOT_OUTCOME_MAP_NO_DATA,
                ))
                profile_timer.log_report(analysis_title=analysis["title"])
                st.warning(t["warn_no_data"].format(title=analysis["title"]))
                st.markdown("---")
                continue

            map_data_paths = staged_artifact_paths[analysis["id"]].map_data_paths
            try:
                write_map_data_artifacts(plot_result.map_data, map_data_paths)
                register_session_artifact(
                    st.session_state,
                    map_data_paths.station_rows_path,
                )
                register_session_artifact(
                    st.session_state,
                    map_data_paths.segment_rows_path,
                )
            except Exception as exc:
                dispose_matplotlib_figure(plot_result.figure)
                del plot_result
                gc.collect()
                status_box.update(
                    label=t["err_analysis_processing_failed"],
                    state="error",
                    expanded=True,
                )
                st.error(t["err_analysis_processing_failed"])
                st.session_state.run_mode = None
                reset_result_state(st.session_state)
                log_performance_event(
                    "analysis_preparation_failure",
                    source=selected_source_key,
                    failure_scope=FetchFailureScope.LOCAL.value,
                    failure_type=type(exc).__name__,
                    stage="publish_map_data_artifacts",
                )
                return "failed"
            snapshot_analysis_entries.append(_snapshot_analysis_entry(
                prepared_analysis,
                outcome=_SNAPSHOT_OUTCOME_RENDERABLE,
                map_data_paths=map_data_paths,
            ))
            deferred_render_data.append(_render_map_result_block(
                t=t,
                analysis=analysis,
                plot_result=plot_result,
                parquet_path=parquet_path,
                map_data_paths=map_data_paths,
                start_t=start_t,
                end_t=end_t,
                loading_label=loading_label,
                max_peer_distance_km=max_peer_distance_km,
                center_latitude=center_latitude,
                center_longitude=center_longitude,
                analysis_context=analysis_context,
                presentation_context=presentation_context,
                database_source=selected_source_key,
                profile_timer=profile_timer,
            ))
            del plot_result
            gc.collect()

        st.markdown("---")

    _render_deferred_inspectors(
        deferred_render_data,
        t=t,
        admission_permit=admission_permit,
        max_peer_distance_km=max_peer_distance_km,
        analysis_context=analysis_context,
        presentation_context=presentation_context,
    )

    publish_completed_run_snapshot(
        st.session_state,
        {
            "schema_version": COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
            "map_data_schema_version": MAP_DATA_ARTIFACT_SCHEMA_VERSION,
            "run_id": st.session_state.get("run_id"),
            "request_fingerprint": request_fingerprint,
            "analysis_plan_fingerprint": analysis_plan_fingerprint,
            "database_source": selected_source_key,
            "analyses": tuple(snapshot_analysis_entries),
        },
    )

    status_box.update(label="Complete", state="complete", expanded=False)

    return "completed"
