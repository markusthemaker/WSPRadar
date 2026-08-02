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
from typing import NamedTuple

import pandas as pd
import requests

from config import (
    CACHE_DIR,
    DEMO_QUERY_CACHE_TTL_SEC,
    MAX_ANALYSIS_RESULT_ROWS,
    QUERY_DATAFRAME_CACHE_MAX_BYTES,
    QUERY_DATAFRAME_CACHE_MAX_ENTRIES,
    QUERY_DATAFRAME_CACHE_MAX_ENTRY_BYTES,
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
    RESULT_ROW_LIMIT_EXCEEDED_CODE,
)
from core.provider_dispatch import ProviderRateLimitExceeded
from core.snr_utils import round_snr_like_columns


http_session = requests.Session()
http_session.headers.update({"Accept-Encoding": "gzip, deflate"})

_RESULT_ROW_LIMIT_CACHE_MAX_ENTRIES = 128
_HTTP_CHUNK_BYTES = 1024 * 1024
_HTTP_ERROR_BODY_MAX_BYTES = 64 * 1024
_dataframe_cache = OrderedDict()
_dataframe_cache_guard = threading.RLock()
_result_row_limit_cache = OrderedDict()
_result_row_limit_cache_guard = threading.RLock()
_CSV_PARSE_ENGINE = "c"
_STANDARD_CSV_FLOAT_COLUMNS = (
    "snr",
    "power",
    "stat_val",
    "snr_u_norm",
    "snr_r_norm",
    "peer_lat",
    "peer_lon",
    "best_ref_dist",
)
_STANDARD_CSV_INTEGER_COLUMNS = ("has_u", "has_r", "is_me", "time_slot")
_ARTIFACT_CLEANUP_MIN_INTERVAL_SECONDS = 60.0
_artifact_cleanup_guard = threading.Lock()
_last_artifact_cleanup_monotonic: float | None = None


class _DataFrameCacheEntry(NamedTuple):
    """One isolated raw-query L1 value and its accounted retained bytes."""

    expires_at_epoch: float | None
    dataframe: pd.DataFrame
    retained_bytes: int


class FetchResponseTooLarge(ValueError):
    """Raised before an upstream response exceeds its configured byte ceiling."""

    def __init__(self, max_bytes):
        self.max_bytes = int(max_bytes)
        super().__init__(f"WSPR response exceeded {self.max_bytes} bytes")


class FetchResultRowLimitExceeded(Exception):
    """Raised before a query result beyond the configured row ceiling is loaded."""

    def __init__(self, max_result_rows):
        self.max_result_rows = int(max_result_rows)
        super().__init__(
            f"WSPR query result exceeded {self.max_result_rows} rows"
        )


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


def _dataframe_memory_bytes(frame: pd.DataFrame) -> int:
    """Estimate logical bytes retained by one DataFrame, including its index."""
    return int(frame.memory_usage(index=True, deep=True).sum())


def _dataframe_cache_total_bytes_unlocked() -> int:
    """Return accounted L1 bytes while the caller holds the cache guard."""
    return sum(entry.retained_bytes for entry in _dataframe_cache.values())


def _prune_expired_dataframe_cache_entries_unlocked(now: float) -> None:
    """Remove every expired L1 entry before byte-capacity decisions."""
    expired_keys = [
        cache_key
        for cache_key, entry in _dataframe_cache.items()
        if entry.expires_at_epoch is not None
        and entry.expires_at_epoch <= now
    ]
    for cache_key in expired_keys:
        _dataframe_cache.pop(cache_key, None)


def _dataframe_cache_get(cache_key):
    now = time.time()
    with _dataframe_cache_guard:
        cached = _dataframe_cache.get(cache_key)
        if cached is None:
            return None
        if (
            cached.expires_at_epoch is not None
            and cached.expires_at_epoch <= now
        ):
            _dataframe_cache.pop(cache_key, None)
            return None
        _dataframe_cache.move_to_end(cache_key)
        try:
            return cached.dataframe.copy(deep=True)
        except Exception:
            # L1 is optional. Discard an entry that cannot be isolated so the
            # caller can continue through the persistent tier or a cache miss.
            _dataframe_cache.pop(cache_key, None)
            return None


def _dataframe_cache_contains(cache_key):
    """Return whether an unexpired in-process entry exists without copying it."""
    now = time.time()
    with _dataframe_cache_guard:
        cached = _dataframe_cache.get(cache_key)
        if cached is None:
            return False
        if (
            cached.expires_at_epoch is not None
            and cached.expires_at_epoch <= now
        ):
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
        if (
            cached.expires_at_epoch is not None
            and cached.expires_at_epoch <= now
        ):
            _dataframe_cache.pop(cache_key, None)
            return None
        return cached.dataframe


def _dataframe_cache_put(
    cache_key,
    frame,
    *,
    ttl_seconds=None,
    expires_at_epoch=None,
):
    """Store an isolated L1 copy when it fits all configured RAM limits.

    Returns ``False`` without affecting row delivery when the frame exceeds the
    per-entry or total byte policy, or when optional accounting/copying fails.
    Expired and least-recently-used entries are removed under the process-local
    guard before the new copy is retained.
    """
    if ttl_seconds is not None and expires_at_epoch is not None:
        raise ValueError("Specify ttl_seconds or expires_at_epoch, not both")
    if expires_at_epoch is not None:
        expires_at = float(expires_at_epoch)
    elif ttl_seconds is not None:
        expires_at = time.time() + float(ttl_seconds)
    else:
        expires_at = None

    try:
        retained_bytes = _dataframe_memory_bytes(frame)
    except Exception:
        # Deep accounting is cache policy, not part of delivering valid rows.
        return False
    if (
        QUERY_DATAFRAME_CACHE_MAX_ENTRIES <= 0
        or retained_bytes > QUERY_DATAFRAME_CACHE_MAX_ENTRY_BYTES
        or retained_bytes > QUERY_DATAFRAME_CACHE_MAX_BYTES
    ):
        return False

    with _dataframe_cache_guard:
        _prune_expired_dataframe_cache_entries_unlocked(time.time())
        _dataframe_cache.pop(cache_key, None)
        retained_total = _dataframe_cache_total_bytes_unlocked()
        while _dataframe_cache and (
            len(_dataframe_cache) >= QUERY_DATAFRAME_CACHE_MAX_ENTRIES
            or retained_total + retained_bytes
            > QUERY_DATAFRAME_CACHE_MAX_BYTES
        ):
            _evicted_key, evicted_entry = _dataframe_cache.popitem(last=False)
            retained_total -= evicted_entry.retained_bytes

        if retained_total + retained_bytes > QUERY_DATAFRAME_CACHE_MAX_BYTES:
            return False
        try:
            cached_frame = frame.copy(deep=True)
        except Exception:
            return False
        _dataframe_cache[cache_key] = _DataFrameCacheEntry(
            expires_at_epoch=expires_at,
            dataframe=cached_frame,
            retained_bytes=retained_bytes,
        )
        _dataframe_cache.move_to_end(cache_key)
        return True


def _result_row_limit_cache_contains(cache_key):
    """Return whether an unexpired overflow marker exists for one exact query."""
    now = time.time()
    with _result_row_limit_cache_guard:
        expires_at = _result_row_limit_cache.get(cache_key)
        if expires_at is None:
            return False
        if expires_at <= now:
            _result_row_limit_cache.pop(cache_key, None)
            return False
        _result_row_limit_cache.move_to_end(cache_key)
        return True


def _result_row_limit_cache_put(
    cache_key,
    *,
    ttl_seconds=None,
    expires_at_epoch=None,
):
    """Remember an oversized exact query without retaining any of its rows."""
    if (ttl_seconds is None) == (expires_at_epoch is None):
        raise ValueError("Specify exactly one row-limit marker expiry")
    expires_at = (
        float(expires_at_epoch)
        if expires_at_epoch is not None
        else time.time() + float(ttl_seconds)
    )
    with _result_row_limit_cache_guard:
        _result_row_limit_cache[cache_key] = expires_at
        _result_row_limit_cache.move_to_end(cache_key)
        while len(_result_row_limit_cache) > _RESULT_ROW_LIMIT_CACHE_MAX_ENTRIES:
            _result_row_limit_cache.popitem(last=False)


def _replace_dataframe_cache_with_row_limit_marker(cache_key, *, is_demo):
    """Evict oversized cached rows while preserving their original expiry."""
    with _dataframe_cache_guard:
        cached_entry = _dataframe_cache.pop(cache_key, None)
    expires_at = (
        cached_entry.expires_at_epoch
        if cached_entry is not None
        else None
    )
    if expires_at is not None:
        _result_row_limit_cache_put(
            cache_key,
            expires_at_epoch=expires_at,
        )
    else:
        _result_row_limit_cache_put(
            cache_key,
            ttl_seconds=_query_cache_ttl_seconds(is_demo=is_demo),
        )


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
    """Return whether one provider-scoped query can avoid an HTTP request.

    The complete SQL text, including its ``FORMAT`` clause, is authoritative
    cache identity. ``response_format`` selects the matching transport path and
    must therefore agree with that clause; production analysis plans enforce
    this invariant.
    """
    provider = _database_provider(database_provider)
    memory_cache_key = _memory_cache_key(
        sql_query,
        is_demo=is_demo,
        database_provider=provider,
    )
    if _result_row_limit_cache_contains(memory_cache_key):
        return True
    if _dataframe_cache_contains(memory_cache_key):
        return True

    cache_path = _query_cache_path(sql_query, provider, is_demo=is_demo)
    return _query_cache_expiry_epoch(
        cache_path,
        _query_cache_ttl_seconds(is_demo=is_demo),
    ) is not None


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
    The SQL ``FORMAT`` clause is part of identity; ``response_format`` is routing
    metadata and must match the plan that produced the SQL.
    """
    provider = _database_provider(database_provider)
    memory_cache_key = _memory_cache_key(
        sql_query,
        is_demo=is_demo,
        database_provider=provider,
    )
    cache_path = _query_cache_path(
        sql_query,
        provider,
        is_demo=is_demo,
    )

    removed = False
    # Inspect only after taking the same key lock as publication. Otherwise an
    # absent pre-lock snapshot can return while an in-flight fetch later
    # publishes the artifact that this call was meant to invalidate.
    with ARTIFACT_STORE.key_lock(cache_path):
        with _dataframe_cache_guard:
            removed = _dataframe_cache.pop(memory_cache_key, None) is not None
        with _result_row_limit_cache_guard:
            removed = (
                _result_row_limit_cache.pop(memory_cache_key, None) is not None
                or removed
            )
        try:
            cache_path.unlink()
            removed = True
        except FileNotFoundError:
            pass
    return removed


def _read_validated_cached_marker(
    cache_path,
    marker_column,
    *,
    refresh_access,
):
    """Read one admission marker without refreshing an unusable query artifact.

    Footer admission and projected marker decoding run under the artifact key
    lock before an ordinary-cache access touch. Invalid or oversized files are
    removed best-effort while still coordinated; callers retain policy-specific
    overflow markers separately.
    """
    with ARTIFACT_STORE.lease(cache_path, refresh_access=False) as leased_path:
        try:
            _raise_if_parquet_result_exceeds_row_limit(leased_path)
            frame = pd.read_parquet(leased_path, columns=[marker_column])
        except (FetchResultRowLimitExceeded, OSError, ValueError, KeyError):
            try:
                leased_path.unlink()
            except OSError:
                pass
            raise
        if refresh_access:
            ARTIFACT_STORE.touch_unlocked(leased_path)
        return frame


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
    cache_key = _memory_cache_key(
        sql_query,
        is_demo=is_demo,
        database_provider=database_provider,
    )
    if str(response_format).lower() == "parquet":
        cache_path = _query_cache_path(
            sql_query,
            database_provider,
            is_demo=is_demo,
        )
        cache_expires_at = _query_cache_expiry_epoch(
            cache_path,
            _query_cache_ttl_seconds(is_demo=is_demo),
        )
        if cache_expires_at is None:
            return None
        marker_column = "target_seen"
        try:
            frame = _read_validated_cached_marker(
                cache_path,
                marker_column,
                refresh_access=not is_demo,
            )
        except FetchResultRowLimitExceeded:
            _result_row_limit_cache_put(
                cache_key,
                **(
                    {"expires_at_epoch": cache_expires_at}
                    if is_demo
                    else {"ttl_seconds": STANDARD_QUERY_CACHE_TTL_SEC}
                ),
            )
            return None
        except (OSError, ValueError, KeyError):
            return None
    else:
        frame = _dataframe_cache_peek(cache_key)
        if analysis.get("analysis_kind") == "opportunity":
            marker_column = "target_seen"
        elif analysis.get("is_sequential"):
            marker_column = "is_me"
        else:
            marker_column = "has_u"
        if frame is None:
            cache_path = _query_cache_path(
                sql_query,
                database_provider,
                is_demo=is_demo,
            )
            cache_expires_at = _query_cache_expiry_epoch(
                cache_path,
                _query_cache_ttl_seconds(is_demo=is_demo),
            )
            if cache_expires_at is None:
                return None
            try:
                frame = _read_validated_cached_marker(
                    cache_path,
                    marker_column,
                    refresh_access=not is_demo,
                )
            except FetchResultRowLimitExceeded:
                _result_row_limit_cache_put(
                    cache_key,
                    **(
                        {"expires_at_epoch": cache_expires_at}
                        if is_demo
                        else {"ttl_seconds": STANDARD_QUERY_CACHE_TTL_SEC}
                    ),
                )
                return None
            except (OSError, ValueError, KeyError):
                return None

    if frame is not None and len(frame) > MAX_ANALYSIS_RESULT_ROWS:
        _replace_dataframe_cache_with_row_limit_marker(
            cache_key,
            is_demo=is_demo,
        )
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
        strict_cache_key = _memory_cache_key(
            strict_query,
            is_demo=is_demo,
            database_provider=provider,
        )
        if _result_row_limit_cache_contains(strict_cache_key):
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
        if _result_row_limit_cache_contains(strict_cache_key):
            continue
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
    """Run at most one process-local artifact sweep per cleanup interval.

    Submission bursts can call this hook concurrently. One caller performs the
    coordinated namespace scan while overlapping or recently completed calls
    return zero removal counts. A failed sweep does not advance the throttle,
    allowing the next submission to retry.
    """
    global _last_artifact_cleanup_monotonic

    empty_counts = {
        ArtifactNamespace.QUERY.value: 0,
        ArtifactNamespace.DEMO_QUERY.value: 0,
        ArtifactNamespace.SESSION_ARTIFACT.value: 0,
    }
    if not _artifact_cleanup_guard.acquire(blocking=False):
        return empty_counts

    try:
        started_at = time.monotonic()
        if (
            _last_artifact_cleanup_monotonic is not None
            and started_at - _last_artifact_cleanup_monotonic
            < _ARTIFACT_CLEANUP_MIN_INTERVAL_SECONDS
        ):
            return empty_counts

        removed = cleanup_artifact_namespaces(
            CACHE_DIR,
            query_ttl_seconds=STANDARD_QUERY_CACHE_TTL_SEC,
            demo_query_ttl_seconds=DEMO_QUERY_CACHE_TTL_SEC,
            session_ttl_seconds=SESSION_ARTIFACT_TTL_SEC,
        )
        _last_artifact_cleanup_monotonic = time.monotonic()
        return removed
    finally:
        _artifact_cleanup_guard.release()


def _decode_response_bytes(payload, response):
    encoding = response.encoding or "utf-8"
    return payload.decode(encoding, errors="replace")


def _bounded_csv_response_buffer(response, max_bytes, max_result_rows):
    """Buffer bounded CSV bytes while counting logical records in constant space.

    The byte-level state machine recognizes doubled quotes and quoted CR/LF
    characters across transport chunks. UTF-8 and single-byte encodings retain
    the ASCII quote/newline bytes, so overflow can be rejected before decoding
    the payload or allocating Pandas columns. The first non-blank record is the
    required ``CSVWithNames`` header and is not counted as a result row.
    """
    payload = io.BytesIO()
    total_bytes = 0
    is_inside_quotes = False
    has_pending_quote = False
    should_skip_line_feed = False
    record_has_content = False
    has_header = False
    result_rows = 0

    def finish_record():
        """Count one non-blank logical record and raise on the sentinel row."""
        nonlocal record_has_content, has_header, result_rows
        if not record_has_content:
            return
        record_has_content = False
        if not has_header:
            has_header = True
            return
        result_rows += 1
        if result_rows > max_result_rows:
            raise FetchResultRowLimitExceeded(max_result_rows)

    for chunk in response.iter_content(chunk_size=_HTTP_CHUNK_BYTES):
        if not chunk:
            continue
        total_bytes += len(chunk)
        if total_bytes > max_bytes:
            raise FetchResponseTooLarge(max_bytes)
        for byte in chunk:
            if has_pending_quote:
                has_pending_quote = False
                if byte == 34:  # Doubled quote inside a quoted CSV field.
                    record_has_content = True
                    continue
                is_inside_quotes = False

            if is_inside_quotes:
                record_has_content = True
                if byte == 34:
                    has_pending_quote = True
                continue

            if should_skip_line_feed:
                should_skip_line_feed = False
                if byte == 10:
                    continue

            if byte == 34:
                is_inside_quotes = True
                record_has_content = True
            elif byte == 13:
                finish_record()
                should_skip_line_feed = True
            elif byte == 10:
                finish_record()
            else:
                record_has_content = True
        payload.write(chunk)
    finish_record()
    payload.seek(0)
    return payload


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


def _read_wspr_csv_response(response_buffer, *, encoding="utf-8"):
    """Parse a bounded WSPR CSV byte buffer without an intermediate text copy.

    Pandas' C engine reads the transport buffer directly and avoids both a large
    ``StringIO`` allocation and the pyarrow CSV parser, whose native failures
    can terminate the Streamlit process before Python returns a structured
    fetch error.
    """
    return pd.read_csv(
        response_buffer,
        engine=_CSV_PARSE_ENGINE,
        encoding=encoding,
    )


def _normalize_csv_query_frame(frame: pd.DataFrame, *, is_demo: bool) -> pd.DataFrame:
    """Reapply the established standard or demo CSV transport normalization.

    Ordinary Compare rows downcast their known numeric transport columns before
    SNR-like rounding. Demo rows deliberately retain their parser-inferred
    numeric widths. Both direct responses and raw Parquet L2 reloads use this
    helper so delivery tier cannot change the returned values or dtypes.
    """
    if not is_demo:
        for column in _STANDARD_CSV_FLOAT_COLUMNS:
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], downcast="float")
        for column in _STANDARD_CSV_INTEGER_COLUMNS:
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], downcast="integer")
    return round_snr_like_columns(frame, owns_input=True)


def _parquet_result_row_count(path):
    """Read only Parquet footer metadata and return its logical row count."""
    import pyarrow.parquet as parquet

    return int(parquet.read_metadata(path).num_rows)


def _raise_if_parquet_result_exceeds_row_limit(path):
    """Reject an oversized Parquet result before Pandas allocates its columns."""
    if _parquet_result_row_count(path) > MAX_ANALYSIS_RESULT_ROWS:
        raise FetchResultRowLimitExceeded(MAX_ANALYSIS_RESULT_ROWS)


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


def _result_row_limit_error_result(
    sql_query,
    *,
    database_provider,
    source=None,
    failure_stage="",
):
    """Return the stable request-scoped failure for an oversized query result."""
    provider = _database_provider(database_provider)
    return FetchResult(
        source=source or _direct_fetch_source(provider),
        database_source=_database_source(provider),
        error=FetchError(
            code=RESULT_ROW_LIMIT_EXCEEDED_CODE,
            message=(
                "Search result exceeded the configured safe limit of "
                f"{MAX_ANALYSIS_RESULT_ROWS} rows."
            ),
            scope=FetchFailureScope.REQUEST,
            query=sql_query,
            failure_stage=str(failure_stage or ""),
        ),
    )


def _request_error_result(
    exc,
    sql_query,
    *,
    database_provider,
    artifact_path=None,
    failure_stage="",
):
    provider = _database_provider(database_provider)
    if isinstance(exc, FetchResultRowLimitExceeded):
        return _result_row_limit_error_result(
            sql_query,
            database_provider=provider,
            failure_stage=failure_stage,
        )
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
            failure_stage=str(failure_stage or ""),
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
    """Fetch source-pinned CSV rows through a byte-bounded L1 and raw disk L2.

    Every accepted exact query is written through to a provider- and
    policy-isolated raw Parquet artifact before CSV transport normalization.
    Standard artifacts have sliding one-hour freshness; demos retain their
    absolute 24-hour publication deadline. Large frames remain disk-only when
    the optional process-memory L1 declines them by byte policy.
    """
    provider = _database_provider(database_provider)
    cache_mode = "demo" if is_demo else "standard"
    cache_key = _memory_cache_key(
        sql_query,
        is_demo=is_demo,
        database_provider=provider,
    )
    cache_path = _query_cache_path(
        sql_query,
        provider,
        is_demo=is_demo,
    )
    cache_ttl_seconds = _query_cache_ttl_seconds(is_demo=is_demo)
    with ARTIFACT_STORE.key_lock(cache_path):
        if _result_row_limit_cache_contains(cache_key):
            return _result_row_limit_error_result(
                sql_query,
                database_provider=provider,
                source=FetchSource.MEMORY_CACHE,
                failure_stage="result_row_limit_cache",
            )
        cached_reference = _dataframe_cache_peek(cache_key)
        if (
            cached_reference is not None
            and len(cached_reference) > MAX_ANALYSIS_RESULT_ROWS
        ):
            _replace_dataframe_cache_with_row_limit_marker(
                cache_key,
                is_demo=is_demo,
            )
            return _result_row_limit_error_result(
                sql_query,
                database_provider=provider,
                source=FetchSource.MEMORY_CACHE,
                failure_stage="validate_memory_cache_rows",
            )
        cached = _dataframe_cache_get(cache_key)
        if cached is not None:
            if len(cached) > MAX_ANALYSIS_RESULT_ROWS:
                _replace_dataframe_cache_with_row_limit_marker(
                    cache_key,
                    is_demo=is_demo,
                )
                return _result_row_limit_error_result(
                    sql_query,
                    database_provider=provider,
                    source=FetchSource.MEMORY_CACHE,
                    failure_stage="validate_memory_cache_rows",
                )
            if (
                not is_demo
                and _query_cache_expiry_epoch(
                    cache_path,
                    STANDARD_QUERY_CACHE_TTL_SEC,
                )
                is not None
            ):
                ARTIFACT_STORE.touch_unlocked(cache_path)
            return FetchResult(
                dataframe=cached,
                source=FetchSource.MEMORY_CACHE,
                database_source=_database_source(provider),
            )

        cache_expires_at = _query_cache_expiry_epoch(
            cache_path,
            cache_ttl_seconds,
        )
        if cache_expires_at is not None:
            try:
                frame = _read_csv_query_parquet(
                    cache_path,
                    is_demo=is_demo,
                )
            except FetchResultRowLimitExceeded:
                try:
                    cache_path.unlink()
                except OSError:
                    pass
                _result_row_limit_cache_put(
                    cache_key,
                    **(
                        {"expires_at_epoch": cache_expires_at}
                        if is_demo
                        else {"ttl_seconds": STANDARD_QUERY_CACHE_TTL_SEC}
                    ),
                )
                return _result_row_limit_error_result(
                    sql_query,
                    database_provider=provider,
                    source=FetchSource.DISK_CACHE,
                    failure_stage="validate_query_cache_rows",
                )
            except (OSError, ValueError):
                try:
                    cache_path.unlink()
                except OSError:
                    pass
            else:
                if not is_demo:
                    ARTIFACT_STORE.touch_unlocked(cache_path)
                _dataframe_cache_put(
                    cache_key,
                    frame,
                    **(
                        {"expires_at_epoch": cache_expires_at}
                        if is_demo
                        else {"ttl_seconds": STANDARD_QUERY_CACHE_TTL_SEC}
                    ),
                )
                return FetchResult(
                    dataframe=frame,
                    artifact_path=cache_path,
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
                response_buffer = _bounded_csv_response_buffer(
                    response,
                    WSPR_CSV_MAX_RESPONSE_BYTES,
                    MAX_ANALYSIS_RESULT_ROWS,
                )
                response_buffer.seek(0, io.SEEK_END)
                payload_bytes = response_buffer.tell()
                response_buffer.seek(0)
                response_encoding = response.encoding or "utf-8"
        except (
            requests.RequestException,
            FetchResponseTooLarge,
            FetchResultRowLimitExceeded,
        ) as exc:
            if isinstance(exc, FetchResultRowLimitExceeded):
                _result_row_limit_cache_put(
                    cache_key,
                    ttl_seconds=_query_cache_ttl_seconds(is_demo=is_demo),
                )
            return _request_error_result(
                exc,
                sql_query,
                database_provider=provider,
                failure_stage=(
                    "stream_validate_csv_result_rows"
                    if isinstance(exc, FetchResultRowLimitExceeded)
                    else ""
                ),
            )

        try:
            frame = _read_wspr_csv_response(
                response_buffer,
                encoding=response_encoding,
            )
        except (OSError, ValueError) as exc:
            response_buffer.seek(0)
            error_payload = response_buffer.read(_HTTP_ERROR_BODY_MAX_BYTES)
            response_text = error_payload.decode(
                response_encoding,
                errors="replace",
            )
            if payload_bytes > len(error_payload):
                response_text = f"{response_text}\n[response truncated]"
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
        finally:
            response_buffer.close()

        if len(frame) > MAX_ANALYSIS_RESULT_ROWS:
            _result_row_limit_cache_put(
                cache_key,
                ttl_seconds=cache_ttl_seconds,
            )
            return _result_row_limit_error_result(
                sql_query,
                database_provider=provider,
                failure_stage="validate_materialized_csv_rows",
            )

        try:
            with ARTIFACT_STORE.atomic_output_path(cache_path) as temporary_path:
                frame.to_parquet(temporary_path, index=False)
        except Exception as exc:
            # A valid provider response remains usable even when the optional
            # persistent tier cannot be published. A frame above the L1 byte
            # policy will intentionally be fetched again after this run.
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"{cache_mode.upper()} DISK CACHE WRITE FAILED for "
                f"{provider.display_name}: {exc}"
            )

        frame = _normalize_csv_query_frame(frame, is_demo=is_demo)
        _dataframe_cache_put(
            cache_key,
            frame,
            **(
                {
                    "expires_at_epoch": (
                        _query_cache_expiry_epoch(
                            cache_path,
                            DEMO_QUERY_CACHE_TTL_SEC,
                        )
                        or time.time() + DEMO_QUERY_CACHE_TTL_SEC
                    )
                }
                if is_demo
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


def _read_raw_query_parquet(path) -> pd.DataFrame:
    """Read one raw query artifact after footer-only row admission."""
    _raise_if_parquet_result_exceeds_row_limit(path)
    return pd.read_parquet(path)


def _read_csv_query_parquet(path, *, is_demo: bool) -> pd.DataFrame:
    """Read raw CSV query rows and reapply their policy-specific normalization."""
    return _normalize_csv_query_frame(
        _read_raw_query_parquet(path),
        is_demo=is_demo,
    )


def _read_query_parquet(path, *, downcast_integer_columns=True):
    """Read one raw query cache and reapply transport normalization."""
    frame = _read_raw_query_parquet(path)
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
    return round_snr_like_columns(frame, owns_input=True)


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
    cache_key = _memory_cache_key(
        sql_query,
        is_demo=is_demo,
        database_provider=provider,
    )

    with ARTIFACT_STORE.key_lock(cache_path):
        if _result_row_limit_cache_contains(cache_key):
            return _result_row_limit_error_result(
                sql_query,
                database_provider=provider,
                source=FetchSource.MEMORY_CACHE,
                failure_stage="result_row_limit_cache",
            )
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
            except FetchResultRowLimitExceeded:
                try:
                    cache_path.unlink()
                except OSError:
                    pass
                _result_row_limit_cache_put(
                    cache_key,
                    **(
                        {"expires_at_epoch": cache_expires_at}
                        if is_demo
                        else {"ttl_seconds": STANDARD_QUERY_CACHE_TTL_SEC}
                    ),
                )
                return _result_row_limit_error_result(
                    sql_query,
                    database_provider=provider,
                    source=FetchSource.DISK_CACHE,
                    failure_stage="validate_query_cache_rows",
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
        failure_stage = "provider_request"
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

                failure_stage = "open_query_cache_temporary"
                with ARTIFACT_STORE.atomic_output_path(cache_path) as temporary_path:
                    failure_stage = "stream_response_to_query_cache"
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
                    failure_stage = "validate_query_cache_temporary"
                    if temporary_path.stat().st_size == 0:
                        raise ValueError("WSPR Parquet response was empty")
                    _raise_if_parquet_result_exceeds_row_limit(temporary_path)
                    failure_stage = "publish_query_cache"

            failure_stage = "read_published_query_cache"
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
        except (
            requests.RequestException,
            OSError,
            ValueError,
            FetchResponseTooLarge,
            FetchResultRowLimitExceeded,
        ) as exc:
            if isinstance(exc, FetchResultRowLimitExceeded):
                _result_row_limit_cache_put(
                    cache_key,
                    ttl_seconds=_query_cache_ttl_seconds(is_demo=is_demo),
                )
                try:
                    cache_path.unlink()
                except OSError:
                    pass
            return _request_error_result(
                exc,
                sql_query,
                database_provider=provider,
                artifact_path=cache_path,
                failure_stage=failure_stage,
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
