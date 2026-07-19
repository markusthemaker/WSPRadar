"""Transactional preparation of one source-pinned analysis data bundle."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import gc
import time
from typing import Callable, Mapping

from core.analysis_runner import (
    DECODE_FILTER_LEGACY,
    DECODE_FILTER_STRICT,
    apply_post_fetch_filters,
    should_retry_without_decode_filter,
)
from core.artifact_store import ARTIFACT_STORE, write_parquet_artifact
from core.data_engine import fetch_wspr_data, invalidate_wspr_query_cache
from core.fetch_models import (
    DatabaseSource,
    FetchError,
    FetchFailureScope,
    FetchResult,
    FetchSource,
)
from core.opportunity_engine import OPPORTUNITY_QUERY_COLUMNS
from core.performance_timer import PerformanceTimer
from core.provider_dispatch import ProviderRunLease


@dataclass(frozen=True)
class PreparedQueryFetch:
    """Record one strict or legacy query's delivery tier and elapsed time."""

    decode_filter_mode: str
    elapsed_seconds: float
    delivery_source: FetchSource


@dataclass
class PreparedAnalysisData:
    """One staged artifact with a non-empty, execution-ordered query trace."""

    analysis: dict
    artifact_path: Path | None
    warning_message: str | None
    query_fetches: tuple[PreparedQueryFetch, ...]
    profile_timer: PerformanceTimer

    @property
    def fetch_seconds(self) -> float:
        """Return total strict-plus-legacy fetch time from the query trace."""
        return sum(query_fetch.elapsed_seconds for query_fetch in self.query_fetches)

    @property
    def delivery_source(self) -> FetchSource:
        """Return the tier that delivered the query selected for analysis."""
        if not self.query_fetches:
            raise ValueError("Prepared analysis has no query fetch trace")
        return self.query_fetches[-1].delivery_source


@dataclass
class PreparedProviderBundle:
    """All staged analysis blocks produced by exactly one database source."""

    database_source: DatabaseSource
    analyses: list[PreparedAnalysisData]


class ProviderBundleFetchError(RuntimeError):
    """Stop one provider attempt after a structured upstream fetch failure."""

    def __init__(self, fetch_result: FetchResult, analysis: dict) -> None:
        self.fetch_result = fetch_result
        self.analysis = analysis
        error = fetch_result.error
        message = error.message if error is not None else "Unknown WSPR fetch failure"
        super().__init__(message)


class ProviderBundlePreparationError(RuntimeError):
    """Stop a run for a local processing or staging failure, without failover."""


_SIMULTANEOUS_COMPARISON_QUERY_COLUMNS = frozenset({
    "time_slot",
    "peer_sign",
    "peer_grid",
    "peer_lat",
    "peer_lon",
    "snr_u_norm",
    "snr_r_norm",
    "has_u",
    "has_r",
    "best_ref_sign",
    "best_ref_dist",
})
_SEQUENTIAL_COMPARISON_QUERY_COLUMNS = frozenset({
    "time",
    "peer_sign",
    "peer_grid",
    "peer_lat",
    "peer_lon",
    "snr",
    "power",
    "stat_val",
    "is_me",
})


def _expected_database_source(provider_key: str) -> DatabaseSource:
    """Return stable source provenance for one configured provider key."""
    try:
        return DatabaseSource(provider_key)
    except ValueError as exc:
        raise ProviderBundlePreparationError(
            f"Unknown WSPR database source '{provider_key}'"
        ) from exc


def _schema_error(fetch_result: FetchResult, analysis: dict) -> FetchResult | None:
    """Return a provider error when a supplied frame violates its row contract."""
    frame = fetch_result.dataframe
    if frame is None:
        return None

    if analysis.get("analysis_kind") == "opportunity":
        required_columns = frozenset(OPPORTUNITY_QUERY_COLUMNS)
    else:
        required_columns = (
            _SEQUENTIAL_COMPARISON_QUERY_COLUMNS
            if analysis.get("is_sequential")
            else _SIMULTANEOUS_COMPARISON_QUERY_COLUMNS
        )
        if analysis.get("is_local_median"):
            required_columns = required_columns.union({"ref_detail_rows"})
    missing_columns = sorted(required_columns.difference(frame.columns))
    if not missing_columns:
        return None

    return FetchResult(
        artifact_path=fetch_result.artifact_path,
        source=fetch_result.source,
        database_source=fetch_result.database_source,
        error=FetchError(
            code="schema_error",
            message=(
                "ClickHouse response omitted required analysis columns: "
                + ", ".join(missing_columns)
            ),
            scope=(
                FetchFailureScope.PROVIDER
                if fetch_result.database_hit
                else FetchFailureScope.CAPACITY
            ),
            query=analysis.get("query", ""),
        ),
    )


def _raise_for_invalid_query_schema(
    fetch_result: FetchResult,
    analysis: dict,
    *,
    is_demo_run: bool,
    database_provider,
    query_cache_invalidator: Callable,
) -> None:
    """Invalidate a schema-failed raw query and raise its structured error.

    Direct provider failures remain provider-scoped. A schema failure delivered
    by RAM or disk is capacity-scoped so the controller can replan after the
    invalid cache entry has been removed instead of penalizing the provider.
    """
    schema_error = _schema_error(fetch_result, analysis)
    if schema_error is None:
        return
    query_cache_invalidator(
        analysis.get("query", ""),
        is_demo=is_demo_run,
        response_format=analysis.get("response_format", "csv"),
        database_provider=database_provider,
    )
    raise ProviderBundleFetchError(schema_error, analysis)


def _delete_staged_artifacts(paths) -> None:
    """Best-effort delete unregistered artifacts created by the current attempt."""
    for path in paths:
        try:
            ARTIFACT_STORE.delete(path)
        except OSError:
            continue


def prepare_provider_bundle(
    analyses,
    *,
    provider_lease: ProviderRunLease,
    is_demo_run: bool,
    analysis_context,
    center_latitude: float,
    center_longitude: float,
    labels,
    artifact_paths: Mapping[str, Path],
    on_legacy_retry: Callable[[int, int, dict], None] | None = None,
    fetch_data: Callable = fetch_wspr_data,
    post_fetch_filter: Callable = apply_post_fetch_filters,
    artifact_writer: Callable = write_parquet_artifact,
    query_cache_invalidator: Callable = invalidate_wspr_query_cache,
    clock: Callable[[], float] = time.perf_counter,
) -> PreparedProviderBundle:
    """Process and stage a complete bundle without publishing partial results.

    Every strict and optional historical-compatibility query uses
    ``provider_lease``. A structured fetch error stops the attempt before a
    legacy decision or any map/export publication. Successfully processed rows
    are written one analysis at a time so the complete raw bundle need not be
    retained in memory.
    """
    expected_source = _expected_database_source(provider_lease.source_key)
    prepared_analyses: list[PreparedAnalysisData] = []
    staged_paths: list[Path] = []
    analysis_count = len(analyses)
    analysis: dict = {}

    try:
        for index, original_analysis in enumerate(analyses):
            analysis = dict(original_analysis)
            profile_timer = PerformanceTimer()
            query_fetches: list[PreparedQueryFetch] = []
            fetch_started = clock()
            fetch_result = fetch_data(
                analysis["query"],
                is_demo=is_demo_run,
                response_format=analysis.get("response_format", "csv"),
                database_provider=provider_lease.provider,
                request_permit=provider_lease,
            )
            strict_fetch_seconds = clock() - fetch_started
            query_fetches.append(PreparedQueryFetch(
                decode_filter_mode=analysis.get(
                    "decode_filter_mode",
                    DECODE_FILTER_STRICT,
                ),
                elapsed_seconds=strict_fetch_seconds,
                delivery_source=fetch_result.source,
            ))

            if fetch_result.error is not None:
                raise ProviderBundleFetchError(fetch_result, analysis)
            if fetch_result.database_source != expected_source:
                raise ProviderBundlePreparationError(
                    "Fetched data source does not match the provider bound to the run"
                )
            _raise_for_invalid_query_schema(
                fetch_result,
                analysis,
                is_demo_run=is_demo_run,
                database_provider=provider_lease.provider,
                query_cache_invalidator=query_cache_invalidator,
            )

            frame = fetch_result.dataframe
            if should_retry_without_decode_filter(frame, analysis):
                if on_legacy_retry is not None:
                    on_legacy_retry(index, analysis_count, analysis)
                frame = None
                fetch_result.dataframe = None
                legacy_analysis = dict(analysis)
                legacy_analysis["query"] = analysis["legacy_query"]
                legacy_analysis["decode_filter_mode"] = analysis.get(
                    "legacy_decode_filter_mode",
                    DECODE_FILTER_LEGACY,
                )
                retry_started = clock()
                fetch_result = fetch_data(
                    legacy_analysis["query"],
                    is_demo=is_demo_run,
                    response_format=legacy_analysis.get("response_format", "csv"),
                    database_provider=provider_lease.provider,
                    request_permit=provider_lease,
                )
                legacy_fetch_seconds = clock() - retry_started
                query_fetches.append(PreparedQueryFetch(
                    decode_filter_mode=legacy_analysis["decode_filter_mode"],
                    elapsed_seconds=legacy_fetch_seconds,
                    delivery_source=fetch_result.source,
                ))
                analysis = legacy_analysis
                if fetch_result.error is not None:
                    raise ProviderBundleFetchError(fetch_result, analysis)
                if fetch_result.database_source != expected_source:
                    raise ProviderBundlePreparationError(
                        "Legacy data source does not match the provider bound to the run"
                    )
                _raise_for_invalid_query_schema(
                    fetch_result,
                    analysis,
                    is_demo_run=is_demo_run,
                    database_provider=provider_lease.provider,
                    query_cache_invalidator=query_cache_invalidator,
                )
                frame = fetch_result.dataframe

            for query_fetch in query_fetches:
                is_legacy_fetch = (
                    query_fetch.decode_filter_mode == DECODE_FILTER_LEGACY
                )
                timing_label = (
                    "fetch legacy compatibility"
                    if is_legacy_fetch
                    else "fetch strict"
                )
                fetch_detail = (
                    f"{expected_source.display_name} via "
                    f"{query_fetch.delivery_source.delivery_label}"
                )
                profile_timer.add(
                    timing_label,
                    query_fetch.elapsed_seconds,
                    detail=fetch_detail,
                )

            selected_fetch_detail = (
                f"{expected_source.display_name} via "
                f"{query_fetches[-1].delivery_source.delivery_label}"
            )

            if frame is None or frame.empty:
                prepared_analyses.append(PreparedAnalysisData(
                    analysis=analysis,
                    artifact_path=None,
                    warning_message=labels["warn_no_data"].format(
                        title=analysis["title"]
                    ),
                    query_fetches=tuple(query_fetches),
                    profile_timer=profile_timer,
                ))
                continue

            profile_timer.add_memory(
                "fetched dataframe",
                df=frame,
                detail=selected_fetch_detail,
            )
            with profile_timer.span("post-filtering"):
                frame, warning_message = post_fetch_filter(
                    frame,
                    analysis,
                    analysis_context,
                    center_latitude,
                    center_longitude,
                    labels,
                    timing_collector=profile_timer,
                )

            if warning_message or frame.empty:
                prepared_analyses.append(PreparedAnalysisData(
                    analysis=analysis,
                    artifact_path=None,
                    warning_message=(
                        warning_message
                        or labels["warn_no_data"].format(title=analysis["title"])
                    ),
                    query_fetches=tuple(query_fetches),
                    profile_timer=profile_timer,
                ))
                del frame
                fetch_result.dataframe = None
                gc.collect()
                continue

            profile_timer.add_memory("post-filter dataframe", df=frame)
            artifact_path = Path(artifact_paths[analysis["id"]])
            try:
                artifact_writer(frame, artifact_path, index=False)
            except Exception as exc:
                raise ProviderBundlePreparationError(
                    f"Could not stage analysis artifact for {analysis['id']}: {exc}"
                ) from exc
            staged_paths.append(artifact_path)
            prepared_analyses.append(PreparedAnalysisData(
                analysis=analysis,
                artifact_path=artifact_path,
                warning_message=None,
                query_fetches=tuple(query_fetches),
                profile_timer=profile_timer,
            ))
            del frame
            fetch_result.dataframe = None
            gc.collect()
    except (ProviderBundleFetchError, ProviderBundlePreparationError):
        _delete_staged_artifacts(staged_paths)
        raise
    except Exception as exc:
        _delete_staged_artifacts(staged_paths)
        analysis_id = analysis.get("id", "unknown")
        raise ProviderBundlePreparationError(
            f"Could not prepare analysis {analysis_id}: {exc}"
        ) from exc
    except BaseException:
        _delete_staged_artifacts(staged_paths)
        raise

    return PreparedProviderBundle(
        database_source=expected_source,
        analyses=prepared_analyses,
    )
