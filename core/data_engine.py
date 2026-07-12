"""WSPR data access with structured results and concurrency-safe caching."""

from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
import hashlib
import io
import threading
import time

import pandas as pd
import requests

from config import (
    CACHE_DIR,
    CACHE_TTL_SEC,
    DB_URL,
    WSPR_CSV_MAX_RESPONSE_BYTES,
    WSPR_HTTP_CONNECT_TIMEOUT_SEC,
    WSPR_HTTP_READ_TIMEOUT_SEC,
    WSPR_PARQUET_MAX_RESPONSE_BYTES,
)
from core.artifact_store import (
    ARTIFACT_STORE,
    ArtifactNamespace,
    cleanup_artifact_namespaces,
)
from core.fetch_models import FetchError, FetchResult, FetchSource
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
        super().__init__(f"WSPR.live response exceeded {self.max_bytes} bytes")


def _dataframe_cache_get(cache_key):
    now = time.monotonic()
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


def _dataframe_cache_put(cache_key, frame, *, ttl_seconds):
    expires_at = None if ttl_seconds is None else time.monotonic() + float(ttl_seconds)
    with _dataframe_cache_guard:
        _dataframe_cache[cache_key] = (expires_at, frame.copy(deep=True))
        _dataframe_cache.move_to_end(cache_key)
        while len(_dataframe_cache) > _DATAFRAME_CACHE_MAX_ENTRIES:
            _dataframe_cache.popitem(last=False)


def _query_cache_path(sql_query):
    digest = hashlib.sha256(sql_query.encode("utf-8")).hexdigest()
    return ARTIFACT_STORE.namespace_path(
        CACHE_DIR,
        ArtifactNamespace.QUERY,
        f"query_{digest}.parquet",
    )


def cleanup_old_parquets():
    """Clean stale query and session artifacts using coordinated namespace locks."""
    return cleanup_artifact_namespaces(CACHE_DIR, ttl_seconds=CACHE_TTL_SEC)


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


def _http_error_result(response, sql_query, *, artifact_path=None, response_text=None):
    return FetchResult(
        artifact_path=artifact_path,
        source=FetchSource.WSPR_LIVE,
        error=FetchError(
            code="http_error",
            message=f"ClickHouse returned HTTP {response.status_code}",
            status_code=int(response.status_code),
            response_text=response.text if response_text is None else response_text,
            query=sql_query,
        ),
    )


def _request_error_result(exc, sql_query, *, artifact_path=None):
    if isinstance(exc, requests.Timeout):
        code = "timeout"
        message = "WSPR.live did not respond within the time limit. Please try again shortly."
    elif isinstance(exc, FetchResponseTooLarge):
        code = "response_too_large"
        message = (
            "WSPR.live returned more data than this deployment can process safely. "
            "Please shorten the time range and try again."
        )
    else:
        code = "request_error"
        message = str(exc)
    return FetchResult(
        artifact_path=artifact_path,
        source=FetchSource.WSPR_LIVE,
        error=FetchError(
            code=code,
            message=message,
            query=sql_query,
        ),
    )


def _fetch_wspr_data_standard(sql_query, *, is_demo=False):
    """Fetch CSV rows with a bounded, copy-on-read in-process cache."""
    query_digest = hashlib.sha256(sql_query.encode("utf-8")).hexdigest()
    cache_mode = "demo" if is_demo else "standard"
    cache_key = f"{cache_mode}:{query_digest}"
    lock_path = _query_cache_path(sql_query).with_suffix(f".{cache_mode}-memory-cache")
    with ARTIFACT_STORE.key_lock(lock_path):
        cached = _dataframe_cache_get(cache_key)
        if cached is not None:
            return FetchResult(dataframe=cached, source=FetchSource.MEMORY_CACHE)

        start_time = time.time()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] EXECUTING QUERY:\n{sql_query}\n")
        try:
            with http_session.get(
                DB_URL,
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
                        response_text=_bounded_error_text(response),
                    )
                payload = _bounded_response_bytes(
                    response,
                    WSPR_CSV_MAX_RESPONSE_BYTES,
                )
                response_text = _decode_response_bytes(payload, response)
                payload_bytes = len(payload)
        except (requests.RequestException, FetchResponseTooLarge) as exc:
            return _request_error_result(exc, sql_query)

        if len(response_text.strip().split("\n")) <= 1:
            return FetchResult(source=FetchSource.WSPR_LIVE)

        try:
            frame = _read_wspr_csv_response(response_text)
        except (OSError, ValueError) as exc:
            return FetchResult(
                source=FetchSource.WSPR_LIVE,
                error=FetchError(
                    code="decode_error",
                    message=str(exc),
                    response_text=response_text,
                    query=sql_query,
                ),
            )

        if not is_demo:
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
            ttl_seconds=None if is_demo else CACHE_TTL_SEC,
        )
        elapsed = time.time() - start_time
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] CACHE MISS: "
            f"DB Query Executed in {elapsed:.2f}s | "
            f"Payload: {payload_bytes / 1024:.1f} KB"
        )
        return FetchResult(dataframe=frame, source=FetchSource.WSPR_LIVE)


def _read_query_parquet(path):
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
    for column in integer_columns:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], downcast="integer")
    return round_snr_like_columns(frame)


def _fetch_wspr_parquet(sql_query, is_demo=False):
    """Stream a compact Parquet result to an exact-query disk cache."""
    cache_path = _query_cache_path(sql_query)

    with ARTIFACT_STORE.key_lock(cache_path):
        if cache_path.exists():
            age = time.time() - cache_path.stat().st_mtime
            if is_demo or age <= CACHE_TTL_SEC:
                try:
                    ARTIFACT_STORE.touch_unlocked(cache_path)
                    return FetchResult(
                        dataframe=_read_query_parquet(cache_path),
                        artifact_path=cache_path,
                        source=FetchSource.DISK_CACHE,
                    )
                except (OSError, ValueError):
                    try:
                        cache_path.unlink()
                    except OSError:
                        pass

        start_time = time.time()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] EXECUTING PARQUET QUERY:\n{sql_query}\n")
        try:
            with http_session.get(
                DB_URL,
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
                f"DB Parquet Query Executed in {elapsed:.2f}s | "
                f"Payload: {cache_path.stat().st_size / 1024:.1f} KB"
            )
            return FetchResult(
                dataframe=frame if not frame.empty else None,
                artifact_path=cache_path,
                source=FetchSource.WSPR_LIVE,
            )
        except (requests.RequestException, OSError, ValueError) as exc:
            return _request_error_result(
                exc,
                sql_query,
                artifact_path=cache_path,
            )


def fetch_wspr_data(sql_query, is_demo=False, response_format="csv"):
    """Fetch WSPR data and return source/error metadata without UI side effects."""
    if str(response_format).lower() == "parquet":
        return _fetch_wspr_parquet(sql_query, is_demo=is_demo)
    return _fetch_wspr_data_standard(sql_query, is_demo=is_demo)
