"""WSPR data access with structured results and concurrency-safe caching."""

from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import io
import math
import threading
import time

import pandas as pd
import requests

from config import (
    CACHE_DIR,
    DEMO_QUERY_CACHE_TTL_SEC,
    SESSION_ARTIFACT_TTL_SEC,
    STANDARD_QUERY_CACHE_TTL_SEC,
    WSPR_CSV_MAX_RESPONSE_BYTES,
    WSPR_DATABASE_PROVIDERS,
    WSPR_HTTP_CONNECT_TIMEOUT_SEC,
    WSPR_HTTP_READ_TIMEOUT_SEC,
    WSPR_PARQUET_MAX_RESPONSE_BYTES,
    WsprDatabaseProviderConfig,
)
from core.artifact_store import (
    ARTIFACT_STORE,
    ArtifactNamespace,
    cleanup_artifact_namespaces,
)
from core.fetch_models import (
    DatabaseSource,
    FetchError,
    FetchFailureScope,
    FetchResult,
    FetchSource,
)
from core.provider_dispatch import ProviderRateLimitExceeded
from core.snr_utils import round_snr_like_columns


http_session = requests.Session()
http_session.headers.update({"Accept-Encoding": "gzip, deflate"})

_DATAFRAME_CACHE_MAX_ENTRIES = 32
_HTTP_CHUNK_BYTES = 1024 * 1024
_HTTP_ERROR_BODY_MAX_BYTES = 64 * 1024
_dataframe_cache = OrderedDict()
_dataframe_cache_guard = threading.RLock()
_CSV_PARSE_ENGINE = "c"


class FetchResponseTooLarge(ValueError):
    """Raised before an upstream response exceeds its configured byte ceiling."""

    def __init__(self, max_bytes):
        self.max_bytes = int(max_bytes)
        super().__init__(f"WSPR response exceeded {self.max_bytes} bytes")


_PRIMARY_DATABASE_PROVIDER = WSPR_DATABASE_PROVIDERS[0]


def _database_provider(database_provider=None) -> WsprDatabaseProviderConfig:
    """Return a validated provider, defaulting to the configured primary."""
    provider = database_provider or _PRIMARY_DATABASE_PROVIDER
    if not isinstance(provider, WsprDatabaseProviderConfig):
        raise TypeError("database_provider must be WsprDatabaseProviderConfig")
    return provider


def _database_source(provider: WsprDatabaseProviderConfig) -> DatabaseSource:
    """Map one configured provider key to stable result provenance."""
    try:
        return DatabaseSource(provider.key)
    except ValueError as exc:
        raise ValueError(f"Unsupported WSPR database provider '{provider.key}'") from exc


def _direct_fetch_source(provider: WsprDatabaseProviderConfig) -> FetchSource:
    """Map one provider to the legacy direct-fetch source enum."""
    return {
        "wspr_live": FetchSource.WSPR_LIVE,
        "wd2": FetchSource.WD2,
        "wd1": FetchSource.WD1,
    }[provider.key]


def _dataframe_cache_get(cache_key):
    now = time.time()
    with _dataframe_cache_guard:
        cached = _dataframe_cache.get(cache_key)
        if cached is None:
            return None
        expires_at, frame = cached
        if expires_at is not None and expires_at <= now:
            _dataframe_cache.pop(cache_key, None)
            return None
        _dataframe_cache.move_to_end(cache_key)
        return frame.copy(deep=True)


def _dataframe_cache_contains(cache_key):
    """Return whether an unexpired in-process entry exists without copying it."""
    now = time.time()
    with _dataframe_cache_guard:
        cached = _dataframe_cache.get(cache_key)
        if cached is None:
            return False
        expires_at, _frame = cached
        if expires_at is not None and expires_at <= now:
            _dataframe_cache.pop(cache_key, None)
            return False
        return True


def _dataframe_cache_peek(cache_key):
    """Return an immutable cache reference for lightweight admission inspection."""
    now = time.time()
    with _dataframe_cache_guard:
        cached = _dataframe_cache.get(cache_key)
        if cached is None:
            return None
        expires_at, frame = cached
        if expires_at is not None and expires_at <= now:
            _dataframe_cache.pop(cache_key, None)
            return None
        return frame


def _dataframe_cache_put(
    cache_key,
    frame,
    *,
    ttl_seconds=None,
    expires_at_epoch=None,
):
    """Store a copy with either a relative or absolute wall-clock expiry."""
    if ttl_seconds is not None and expires_at_epoch is not None:
        raise ValueError("Specify ttl_seconds or expires_at_epoch, not both")
    if expires_at_epoch is not None:
        expires_at = float(expires_at_epoch)
    elif ttl_seconds is not None:
        expires_at = time.time() + float(ttl_seconds)
    else:
        expires_at = None
    with _dataframe_cache_guard:
        _dataframe_cache[cache_key] = (expires_at, frame.copy(deep=True))
        _dataframe_cache.move_to_end(cache_key)
        while len(_dataframe_cache) > _DATAFRAME_CACHE_MAX_ENTRIES:
            _dataframe_cache.popitem(last=False)


def _query_digest(sql_query):
    """Return the stable digest shared by source-specific cache identities."""
    return hashlib.sha256(sql_query.encode("utf-8")).hexdigest()


def _memory_cache_key(sql_query, *, is_demo, database_provider):
    cache_mode = "demo" if is_demo else "standard"
    return f"{database_provider.key}:{cache_mode}:{_query_digest(sql_query)}"


def _query_cache_path(sql_query, database_provider=None, *, is_demo=False):
    """Return a mode- and provider-scoped exact-query Parquet cache path."""
    provider = _database_provider(database_provider)
    digest = hashlib.sha256(sql_query.encode("utf-8")).hexdigest()
    return ARTIFACT_STORE.namespace_path(
        CACHE_DIR,
        (
            ArtifactNamespace.DEMO_QUERY
            if is_demo
            else ArtifactNamespace.QUERY
        ),
        provider.key,
        f"query_{digest}.parquet",
    )


def _query_cache_expiry_epoch(cache_path, ttl_seconds, *, now=None):
    """Return an mtime-anchored expiry, or ``None`` when stale or missing."""
    reference_time = time.time() if now is None else float(now)
    try:
        freshness_anchor = cache_path.stat().st_mtime
    except OSError:
        return None
    # Re-anchoring a future timestamp to ``now`` on every read would silently
    # turn an absolute lifetime into a sliding one until the clock caught up.
    if freshness_anchor > reference_time:
        return None
    expires_at = freshness_anchor + float(ttl_seconds)
    return expires_at if expires_at > reference_time else None


def _query_cache_ttl_seconds(*, is_demo):
    """Return the freshness lifetime for one query-cache policy."""
    return (
        DEMO_QUERY_CACHE_TTL_SEC
        if is_demo
        else STANDARD_QUERY_CACHE_TTL_SEC
    )


def is_wspr_query_cached(
    sql_query,
    *,
    is_demo=False,
    response_format="csv",
    database_provider=None,
):
    """Return whether one provider-scoped query can avoid an HTTP request."""
    provider = _database_provider(database_provider)
    memory_cache_key = _memory_cache_key(
        sql_query,
        is_demo=is_demo,
        database_provider=provider,
    )
    if _dataframe_cache_contains(memory_cache_key):
        return True

    if str(response_format).lower() == "parquet":
        cache_path = _query_cache_path(sql_query, provider, is_demo=is_demo)
        return _query_cache_expiry_epoch(
            cache_path,
            _query_cache_ttl_seconds(is_demo=is_demo),
        ) is not None
    if is_demo:
        cache_path = _query_cache_path(sql_query, provider, is_demo=True)
        return _query_cache_expiry_epoch(
            cache_path,
            DEMO_QUERY_CACHE_TTL_SEC,
        ) is not None
    return False


def invalidate_wspr_query_cache(
    sql_query,
    *,
    is_demo=False,
    response_format="csv",
    database_provider=None,
):
    """Remove one provider- and policy-scoped raw query from every cache tier.

    This is used when downstream row-contract validation proves that a decoded
    provider response is unsafe to reuse. The same key lock as the fetch path
    prevents invalidation from racing publication or a coordinated disk read.
    """
    provider = _database_provider(database_provider)
    memory_cache_key = _memory_cache_key(
        sql_query,
        is_demo=is_demo,
        database_provider=provider,
    )
    has_disk_cache = is_demo or str(response_format).lower() == "parquet"
    cache_path = _query_cache_path(
        sql_query,
        provider,
        is_demo=is_demo,
    )
    lock_path = (
        cache_path
        if has_disk_cache
        else cache_path.with_suffix(".standard-memory-cache")
    )

    # Avoid creating cross-process lock state for injected/test fetchers that
    # did not publish through this engine.
    with _dataframe_cache_guard:
        has_memory_cache = memory_cache_key in _dataframe_cache
    if not has_memory_cache and not (has_disk_cache and cache_path.is_file()):
        return False

    removed = False
    with ARTIFACT_STORE.key_lock(lock_path):
        with _dataframe_cache_guard:
            removed = _dataframe_cache.pop(memory_cache_key, None) is not None
        if has_disk_cache:
            try:
                cache_path.unlink()
                removed = True
            except FileNotFoundError:
                pass
    return removed


def _cached_strict_target_evidence(
    analysis,
    *,
    is_demo,
    database_provider,
):
    """Return cached strict target evidence, or ``None`` when not inspectable."""
    sql_query = analysis.get("query")
    if not sql_query:
        return None
    response_format = analysis.get("response_format", "csv")
    if str(response_format).lower() == "parquet":
        cache_path = _query_cache_path(
            sql_query,
            database_provider,
            is_demo=is_demo,
        )
        if not is_wspr_query_cached(
            sql_query,
            is_demo=is_demo,
            response_format=response_format,
            database_provider=database_provider,
        ):
            return None
        marker_column = "target_seen"
        try:
            with ARTIFACT_STORE.lease(
                cache_path,
                refresh_access=not is_demo,
            ) as leased_path:
                frame = pd.read_parquet(leased_path, columns=[marker_column])
        except (OSError, ValueError, KeyError):
            return None
    else:
        cache_key = _memory_cache_key(
            sql_query,
            is_demo=is_demo,
            database_provider=database_provider,
        )
        frame = _dataframe_cache_peek(cache_key)
        if analysis.get("analysis_kind") == "opportunity":
            marker_column = "target_seen"
        elif analysis.get("is_sequential"):
            marker_column = "is_me"
        else:
            marker_column = "has_u"
        if frame is None and is_demo:
            cache_path = _query_cache_path(
                sql_query,
                database_provider,
                is_demo=True,
            )
            if _query_cache_expiry_epoch(
                cache_path,
                DEMO_QUERY_CACHE_TTL_SEC,
            ) is None:
                return None
            try:
                with ARTIFACT_STORE.lease(
                    cache_path,
                    refresh_access=False,
                ) as leased_path:
                    frame = pd.read_parquet(
                        leased_path,
                        columns=[marker_column],
                    )
            except (OSError, ValueError, KeyError):
                return None

    if frame is None or marker_column not in frame.columns:
        return None
    if frame.empty:
        return False
    marker_values = pd.to_numeric(frame[marker_column], errors="coerce").fillna(0)
    return bool((marker_values > 0).any())


def estimate_uncached_requests(analyses, *, is_demo, database_provider):
    """Count requests needed by strict plans and any still-possible legacy query."""
    provider = _database_provider(database_provider)
    request_count = 0
    for analysis in analyses:
        response_format = analysis.get("response_format", "csv")
        strict_query = analysis.get("query")
        if not strict_query:
            continue
        is_strict_cached = is_wspr_query_cached(
            strict_query,
            is_demo=is_demo,
            response_format=response_format,
            database_provider=provider,
        )
        cached_target_evidence = (
            _cached_strict_target_evidence(
                analysis,
                is_demo=is_demo,
                database_provider=provider,
            )
            if is_strict_cached
            else None
        )
        if not is_strict_cached or cached_target_evidence is None:
            request_count += 1

        legacy_query = analysis.get("legacy_query")
        legacy_may_run = (
            bool(legacy_query)
            and cached_target_evidence is not True
        )
        if legacy_may_run and not is_wspr_query_cached(
            legacy_query,
            is_demo=is_demo,
            response_format=response_format,
            database_provider=provider,
        ):
            request_count += 1
    return request_count


def cleanup_old_parquets():
    """Clean stale query and session artifacts using coordinated namespace locks."""
    return cleanup_artifact_namespaces(
        CACHE_DIR,
        query_ttl_seconds=STANDARD_QUERY_CACHE_TTL_SEC,
        demo_query_ttl_seconds=DEMO_QUERY_CACHE_TTL_SEC,
        session_ttl_seconds=SESSION_ARTIFACT_TTL_SEC,
    )


def _decode_response_bytes(payload, response):
    encoding = response.encoding or "utf-8"
    return payload.decode(encoding, errors="replace")


def _bounded_response_bytes(response, max_bytes):
    payload = io.BytesIO()
    total_bytes = 0
    for chunk in response.iter_content(chunk_size=_HTTP_CHUNK_BYTES):
        if not chunk:
            continue
        total_bytes += len(chunk)
        if total_bytes > max_bytes:
            raise FetchResponseTooLarge(max_bytes)
        payload.write(chunk)
    return payload.getvalue()


def _bounded_error_text(response):
    payload = io.BytesIO()
    remaining = _HTTP_ERROR_BODY_MAX_BYTES
    truncated = False
    for chunk in response.iter_content(chunk_size=min(_HTTP_CHUNK_BYTES, remaining)):
        if not chunk:
            continue
        if len(chunk) > remaining:
            payload.write(chunk[:remaining])
            truncated = True
            break
        payload.write(chunk)
        remaining -= len(chunk)
        if remaining == 0:
            truncated = True
            break
    text = _decode_response_bytes(payload.getvalue(), response)
    return f"{text}\n[response truncated]" if truncated else text


def _read_wspr_csv_response(response_text):
    """Parse a bounded WSPR CSV response without using Arrow's native CSV reader.

    The standard query path already holds the full bounded response in memory.
    Pandas' C engine is sufficient for these CSVWithNames responses and avoids
    the pyarrow CSV parser, whose native failures can terminate the whole
    Streamlit process before Python can return a structured fetch error.
    """
    return pd.read_csv(io.StringIO(response_text), engine=_CSV_PARSE_ENGINE)


def _parse_retry_after_seconds(value, *, now_utc=None):
    """Parse an HTTP Retry-After delta or date into non-negative seconds."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed_seconds = float(text)
        return max(parsed_seconds, 0.0) if math.isfinite(parsed_seconds) else None
    except ValueError:
        pass
    try:
        retry_at = parsedate_to_datetime(text)
    except (TypeError, ValueError, OverflowError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)
    reference = now_utc or datetime.now(timezone.utc)
    return max((retry_at.astimezone(timezone.utc) - reference).total_seconds(), 0.0)


def _http_failure_scope(status_code):
    """Classify HTTP failures that can reasonably improve on another source."""
    status_code = int(status_code)
    if status_code in {408, 429} or 500 <= status_code <= 599:
        return FetchFailureScope.PROVIDER
    return FetchFailureScope.REQUEST


def _http_error_result(
    response,
    sql_query,
    *,
    database_provider,
    artifact_path=None,
    response_text=None,
):
    provider = _database_provider(database_provider)
    headers = getattr(response, "headers", {}) or {}
    return FetchResult(
        artifact_path=artifact_path,
        source=_direct_fetch_source(provider),
        database_source=_database_source(provider),
        error=FetchError(
            code="http_error",
            message=f"ClickHouse returned HTTP {response.status_code}",
            scope=_http_failure_scope(response.status_code),
            status_code=int(response.status_code),
            retry_after_seconds=_parse_retry_after_seconds(headers.get("Retry-After")),
            response_text=response.text if response_text is None else response_text,
            query=sql_query,
        ),
    )


def _request_error_result(
    exc,
    sql_query,
    *,
    database_provider,
    artifact_path=None,
):
    provider = _database_provider(database_provider)
    if isinstance(exc, requests.Timeout):
        code = "timeout"
        scope = FetchFailureScope.PROVIDER
        message = (
            f"{provider.display_name} did not respond within the time limit. "
            "Please try again shortly."
        )
    elif isinstance(exc, ProviderRateLimitExceeded):
        code = "local_rate_limit"
        scope = FetchFailureScope.CAPACITY
        message = str(exc)
    elif isinstance(exc, FetchResponseTooLarge):
        code = "response_too_large"
        scope = FetchFailureScope.REQUEST
        message = (
            f"{provider.display_name} returned more data than this deployment can process safely. "
            "Please shorten the time range and try again."
        )
    elif isinstance(exc, requests.RequestException):
        code = "request_error"
        scope = FetchFailureScope.PROVIDER
        message = str(exc)
    elif isinstance(exc, OSError):
        code = "local_io_error"
        scope = FetchFailureScope.LOCAL
        message = str(exc)
    else:
        code = "decode_error"
        scope = FetchFailureScope.PROVIDER
        message = str(exc)
    return FetchResult(
        artifact_path=artifact_path,
        source=_direct_fetch_source(provider),
        database_source=_database_source(provider),
        error=FetchError(
            code=code,
            message=message,
            scope=scope,
            query=sql_query,
        ),
    )


def _consume_request(request_permit, provider, sql_query, *, artifact_path=None):
    """Consume provider budget and return a structured local refusal if needed."""
    if request_permit is None:
        return None
    lease_provider = getattr(request_permit, "provider", None)
    if lease_provider is None or lease_provider.key != provider.key:
        raise ValueError("Request permit does not match the selected database provider")
    try:
        request_permit.consume_request()
    except ProviderRateLimitExceeded as exc:
        return _request_error_result(
            exc,
            sql_query,
            database_provider=provider,
            artifact_path=artifact_path,
        )
    return None


def _fetch_wspr_data_standard(
    sql_query,
    *,
    is_demo=False,
    database_provider=None,
    request_permit=None,
):
    """Fetch source-pinned CSV rows through RAM and optional demo disk cache.

    Standard requests retain the existing one-hour RAM-only policy. Demo
    requests add a provider-scoped Parquet L2 containing transport-decoded
    query rows before scientific post-fetch filtering.
    """
    provider = _database_provider(database_provider)
    cache_mode = "demo" if is_demo else "standard"
    cache_key = _memory_cache_key(
        sql_query,
        is_demo=is_demo,
        database_provider=provider,
    )
    demo_cache_path = (
        _query_cache_path(sql_query, provider, is_demo=True)
        if is_demo
        else None
    )
    lock_path = (
        demo_cache_path
        if demo_cache_path is not None
        else _query_cache_path(sql_query, provider).with_suffix(
            f".{cache_mode}-memory-cache"
        )
    )
    with ARTIFACT_STORE.key_lock(lock_path):
        cached = _dataframe_cache_get(cache_key)
        if cached is not None:
            return FetchResult(
                dataframe=cached,
                source=FetchSource.MEMORY_CACHE,
                database_source=_database_source(provider),
            )

        if demo_cache_path is not None:
            demo_expires_at = _query_cache_expiry_epoch(
                demo_cache_path,
                DEMO_QUERY_CACHE_TTL_SEC,
            )
            if demo_expires_at is not None:
                try:
                    frame = _read_query_parquet(
                        demo_cache_path,
                        downcast_integer_columns=False,
                    )
                except (OSError, ValueError):
                    try:
                        demo_cache_path.unlink()
                    except OSError:
                        pass
                else:
                    _dataframe_cache_put(
                        cache_key,
                        frame,
                        expires_at_epoch=demo_expires_at,
                    )
                    return FetchResult(
                        dataframe=frame,
                        artifact_path=demo_cache_path,
                        source=FetchSource.DISK_CACHE,
                        database_source=_database_source(provider),
                    )

        budget_error = _consume_request(
            request_permit,
            provider,
            sql_query,
        )
        if budget_error is not None:
            return budget_error

        start_time = time.time()
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] EXECUTING "
            f"{provider.display_name} QUERY:\n{sql_query}\n"
        )
        try:
            with http_session.get(
                provider.url,
                params={"query": sql_query},
                stream=True,
                timeout=(
                    WSPR_HTTP_CONNECT_TIMEOUT_SEC,
                    WSPR_HTTP_READ_TIMEOUT_SEC,
                ),
            ) as response:
                if response.status_code != 200:
                    return _http_error_result(
                        response,
                        sql_query,
                        database_provider=provider,
                        response_text=_bounded_error_text(response),
                    )
                payload = _bounded_response_bytes(
                    response,
                    WSPR_CSV_MAX_RESPONSE_BYTES,
                )
                response_text = _decode_response_bytes(payload, response)
                payload_bytes = len(payload)
        except (requests.RequestException, FetchResponseTooLarge) as exc:
            return _request_error_result(
                exc,
                sql_query,
                database_provider=provider,
            )

        try:
            frame = _read_wspr_csv_response(response_text)
        except (OSError, ValueError) as exc:
            return FetchResult(
                source=_direct_fetch_source(provider),
                database_source=_database_source(provider),
                error=FetchError(
                    code="decode_error",
                    message=str(exc),
                    scope=FetchFailureScope.PROVIDER,
                    response_text=response_text,
                    query=sql_query,
                ),
            )

        if demo_cache_path is not None:
            try:
                with ARTIFACT_STORE.atomic_output_path(
                    demo_cache_path
                ) as temporary_path:
                    frame.to_parquet(temporary_path, index=False)
            except Exception as exc:
                # A valid provider response remains usable from RAM even when
                # the optional persistent demo tier cannot be published.
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"DEMO DISK CACHE WRITE FAILED for {provider.display_name}: {exc}"
                )
        else:
            float_columns = [
                "snr",
                "power",
                "stat_val",
                "snr_u_norm",
                "snr_r_norm",
                "peer_lat",
                "peer_lon",
                "best_ref_dist",
            ]
            for column in float_columns:
                if column in frame.columns:
                    frame[column] = pd.to_numeric(frame[column], downcast="float")
            for column in ["has_u", "has_r", "is_me", "time_slot"]:
                if column in frame.columns:
                    frame[column] = pd.to_numeric(frame[column], downcast="integer")

        frame = round_snr_like_columns(frame)
        _dataframe_cache_put(
            cache_key,
            frame,
            **(
                {
                    "expires_at_epoch": (
                        _query_cache_expiry_epoch(
                            demo_cache_path,
                            DEMO_QUERY_CACHE_TTL_SEC,
                        )
                        or time.time() + DEMO_QUERY_CACHE_TTL_SEC
                    )
                }
                if demo_cache_path is not None
                else {"ttl_seconds": STANDARD_QUERY_CACHE_TTL_SEC}
            ),
        )
        elapsed = time.time() - start_time
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] CACHE MISS: "
            f"{provider.display_name} Query Executed in {elapsed:.2f}s | "
            f"Payload: {payload_bytes / 1024:.1f} KB"
        )
        return FetchResult(
            dataframe=frame,
            source=_direct_fetch_source(provider),
            database_source=_database_source(provider),
        )


def _read_query_parquet(path, *, downcast_integer_columns=True):
    """Read one raw query cache and reapply transport normalization."""
    frame = pd.read_parquet(path)
    integer_columns = [
        "time_slot",
        "target_seen",
        "external_seen",
        "opportunity",
        "hit",
        "miss",
        "target_only",
    ]
    if downcast_integer_columns:
        for column in integer_columns:
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], downcast="integer")
    return round_snr_like_columns(frame)


def _fetch_wspr_parquet(
    sql_query,
    is_demo=False,
    *,
    database_provider=None,
    request_permit=None,
):
    """Stream source-pinned Parquet rows to an isolated exact-query cache."""
    provider = _database_provider(database_provider)
    cache_path = _query_cache_path(sql_query, provider, is_demo=is_demo)

    with ARTIFACT_STORE.key_lock(cache_path):
        cache_expires_at = _query_cache_expiry_epoch(
            cache_path,
            _query_cache_ttl_seconds(is_demo=is_demo),
        )
        if cache_expires_at is not None:
            try:
                if not is_demo:
                    ARTIFACT_STORE.touch_unlocked(cache_path)
                return FetchResult(
                    dataframe=_read_query_parquet(cache_path),
                    artifact_path=cache_path,
                    source=FetchSource.DISK_CACHE,
                    database_source=_database_source(provider),
                )
            except (OSError, ValueError):
                try:
                    cache_path.unlink()
                except OSError:
                    pass

        budget_error = _consume_request(
            request_permit,
            provider,
            sql_query,
            artifact_path=cache_path,
        )
        if budget_error is not None:
            return budget_error

        start_time = time.time()
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] EXECUTING "
            f"{provider.display_name} PARQUET QUERY:\n{sql_query}\n"
        )
        try:
            with http_session.get(
                provider.url,
                params={"query": sql_query},
                stream=True,
                timeout=(
                    WSPR_HTTP_CONNECT_TIMEOUT_SEC,
                    WSPR_HTTP_READ_TIMEOUT_SEC,
                ),
            ) as response:
                if response.status_code != 200:
                    return _http_error_result(
                        response,
                        sql_query,
                        database_provider=provider,
                        artifact_path=cache_path,
                        response_text=_bounded_error_text(response),
                    )

                with ARTIFACT_STORE.atomic_output_path(cache_path) as temporary_path:
                    with temporary_path.open("wb") as handle:
                        payload_bytes = 0
                        for chunk in response.iter_content(chunk_size=_HTTP_CHUNK_BYTES):
                            if chunk:
                                payload_bytes += len(chunk)
                                if payload_bytes > WSPR_PARQUET_MAX_RESPONSE_BYTES:
                                    raise FetchResponseTooLarge(
                                        WSPR_PARQUET_MAX_RESPONSE_BYTES
                                    )
                                handle.write(chunk)
                    if temporary_path.stat().st_size == 0:
                        raise ValueError("WSPR Parquet response was empty")

            frame = _read_query_parquet(cache_path)
            elapsed = time.time() - start_time
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] CACHE MISS: "
                f"{provider.display_name} Parquet Query Executed in {elapsed:.2f}s | "
                f"Payload: {cache_path.stat().st_size / 1024:.1f} KB"
            )
            return FetchResult(
                dataframe=frame,
                artifact_path=cache_path,
                source=_direct_fetch_source(provider),
                database_source=_database_source(provider),
            )
        except (requests.RequestException, OSError, ValueError, FetchResponseTooLarge) as exc:
            return _request_error_result(
                exc,
                sql_query,
                database_provider=provider,
                artifact_path=cache_path,
            )


def fetch_wspr_data(
    sql_query,
    is_demo=False,
    response_format="csv",
    *,
    database_provider=None,
    request_permit=None,
):
    """Fetch from one pinned database and preserve cache/source provenance."""
    if str(response_format).lower() == "parquet":
        return _fetch_wspr_parquet(
            sql_query,
            is_demo=is_demo,
            database_provider=database_provider,
            request_permit=request_permit,
        )
    return _fetch_wspr_data_standard(
        sql_query,
        is_demo=is_demo,
        database_provider=database_provider,
        request_permit=request_permit,
    )
