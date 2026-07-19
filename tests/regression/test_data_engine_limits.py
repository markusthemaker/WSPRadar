from collections import OrderedDict
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import time
import uuid

import pandas as pd
import requests

from config import WSPR_DATABASE_PROVIDERS
from core import data_engine
from core.artifact_store import ArtifactNamespace
from core.fetch_models import (
    DatabaseSource,
    FetchError,
    FetchFailureScope,
    FetchSource,
)
from core.provider_dispatch import ProviderDispatchController


class _StreamingResponse:
    def __init__(
        self,
        chunks,
        *,
        status_code=200,
        encoding="utf-8",
        headers=None,
    ):
        self.chunks = list(chunks)
        self.status_code = status_code
        self.encoding = encoding
        self.headers = dict(headers or {})

    @property
    def text(self):
        return b"".join(self.chunks).decode(self.encoding)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def iter_content(self, chunk_size):
        assert chunk_size > 0
        yield from self.chunks


def test_csv_fetch_uses_configured_timeout_and_streaming(monkeypatch):
    request_kwargs = {}

    def fake_get(*_args, **kwargs):
        request_kwargs.update(kwargs)
        return _StreamingResponse([b"peer_sign,stat_val\nK1AAA,-12.3\n"])

    monkeypatch.setattr(data_engine.http_session, "get", fake_get)
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"

    result = data_engine.fetch_wspr_data(query)

    assert result.error is None
    assert request_kwargs["stream"] is True
    assert request_kwargs["timeout"] == (
        data_engine.WSPR_HTTP_CONNECT_TIMEOUT_SEC,
        data_engine.WSPR_HTTP_READ_TIMEOUT_SEC,
    )


def test_csv_fetch_avoids_arrow_parser(monkeypatch):
    parse_kwargs = {}

    def fake_read_csv(*_args, **kwargs):
        parse_kwargs.update(kwargs)
        return pd.DataFrame({"peer_sign": ["K1AAA"], "stat_val": [-12.3]})

    monkeypatch.setattr(
        data_engine.http_session,
        "get",
        lambda *_args, **_kwargs: _StreamingResponse(
            [b"peer_sign,stat_val\nK1AAA,-12.3\n"]
        ),
    )
    monkeypatch.setattr(data_engine.pd, "read_csv", fake_read_csv)
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"

    result = data_engine.fetch_wspr_data(query)

    assert result.error is None
    assert result.source == data_engine.FetchSource.WSPR_LIVE
    assert parse_kwargs["engine"] == "c"


def test_one_line_csv_body_is_preserved_for_schema_validation(monkeypatch):
    """Do not silently convert a maintenance page into scientific no-data."""
    monkeypatch.setattr(
        data_engine.http_session,
        "get",
        lambda *_args, **_kwargs: _StreamingResponse(
            [b"<html>temporarily unavailable</html>"]
        ),
    )
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"

    result = data_engine.fetch_wspr_data(query)

    assert result.error is None
    assert result.dataframe is not None
    assert result.dataframe.empty
    assert list(result.dataframe.columns) == ["<html>temporarily unavailable</html>"]


def test_csv_response_over_limit_returns_retryable_error(monkeypatch):
    monkeypatch.setattr(data_engine, "WSPR_CSV_MAX_RESPONSE_BYTES", 16)
    monkeypatch.setattr(
        data_engine.http_session,
        "get",
        lambda *_args, **_kwargs: _StreamingResponse([b"0123456789", b"abcdefghij"]),
    )
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"

    result = data_engine.fetch_wspr_data(query)

    assert result.dataframe is None
    assert result.error.code == "response_too_large"
    assert result.error.scope == FetchFailureScope.REQUEST
    assert "shorten the time range" in result.error.message


def test_csv_timeout_returns_clear_retry_message(monkeypatch):
    def raise_timeout(*_args, **_kwargs):
        raise requests.ReadTimeout("upstream stalled")

    monkeypatch.setattr(data_engine.http_session, "get", raise_timeout)
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"

    result = data_engine.fetch_wspr_data(query)

    assert result.error.code == "timeout"
    assert result.error.scope == FetchFailureScope.PROVIDER
    assert "try again shortly" in result.error.message.lower()


def test_selected_provider_url_and_provenance_are_used(monkeypatch):
    wd2 = WSPR_DATABASE_PROVIDERS[1]
    requested_urls = []

    def fake_get(url, *_args, **_kwargs):
        requested_urls.append(url)
        return _StreamingResponse([b"peer_sign,stat_val\nK1AAA,-12.3\n"])

    monkeypatch.setattr(data_engine.http_session, "get", fake_get)
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"

    result = data_engine.fetch_wspr_data(query, database_provider=wd2)

    assert requested_urls == [wd2.url]
    assert result.source == FetchSource.WD2
    assert result.database_source == DatabaseSource.WD2


def test_http_429_preserves_retry_after_for_provider_cooldown(monkeypatch):
    monkeypatch.setattr(
        data_engine.http_session,
        "get",
        lambda *_args, **_kwargs: _StreamingResponse(
            [b"rate limited"],
            status_code=429,
            headers={"Retry-After": "17"},
        ),
    )
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"

    result = data_engine.fetch_wspr_data(query)

    assert result.error.status_code == 429
    assert result.error.scope == FetchFailureScope.PROVIDER
    assert result.error.retry_after_seconds == 17.0


def test_retry_after_parser_handles_dates_and_rejects_nonfinite_values():
    now_utc = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    retry_at = now_utc + timedelta(seconds=45)

    assert data_engine._parse_retry_after_seconds(
        retry_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        now_utc=now_utc,
    ) == 45.0
    assert data_engine._parse_retry_after_seconds("NaN") is None
    assert data_engine._parse_retry_after_seconds("Infinity") is None


def test_cache_only_lease_refuses_an_unplanned_network_request(monkeypatch):
    provider = WSPR_DATABASE_PROVIDERS[0]
    controller = ProviderDispatchController(
        (provider,),
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    lease = controller.try_acquire_run({provider.key: 0})
    monkeypatch.setattr(
        data_engine.http_session,
        "get",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("An unreserved cache miss must not reach the network")
        ),
    )

    result = data_engine.fetch_wspr_data(
        f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames",
        database_provider=provider,
        request_permit=lease,
    )
    lease.release()

    assert result.error.code == "local_rate_limit"
    assert result.error.scope == FetchFailureScope.CAPACITY


def test_cached_strict_target_evidence_keeps_primary_eligible_during_cooldown(
    monkeypatch,
):
    """Do not reserve an impossible legacy request after strict evidence is known."""
    monkeypatch.setattr(data_engine, "_dataframe_cache", OrderedDict())
    strict_query = f"SELECT '{uuid.uuid4().hex}' STRICT"
    legacy_query = f"SELECT '{uuid.uuid4().hex}' LEGACY"
    analysis = {
        "analysis_kind": "comparison",
        "is_sequential": False,
        "query": strict_query,
        "legacy_query": legacy_query,
        "response_format": "csv",
    }
    primary = WSPR_DATABASE_PROVIDERS[0]
    cache_key = data_engine._memory_cache_key(
        strict_query,
        is_demo=False,
        database_provider=primary,
    )
    data_engine._dataframe_cache_put(
        cache_key,
        pd.DataFrame({"has_u": [1]}),
        ttl_seconds=60.0,
    )
    required_requests = {
        provider.key: data_engine.estimate_uncached_requests(
            [analysis],
            is_demo=False,
            database_provider=provider,
        )
        for provider in WSPR_DATABASE_PROVIDERS
    }
    assert required_requests["wspr_live"] == 0

    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    failing_lease = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    failing_lease.consume_request()
    failing_lease.report_failure(FetchError(
        code="http_error",
        message="rate limited",
        status_code=429,
        scope=FetchFailureScope.PROVIDER,
        retry_after_seconds=60.0,
    ))
    failing_lease.release()

    cached_lease = controller.try_acquire_run(required_requests)
    assert cached_lease.source_key == "wspr_live"
    cached_lease.release()

    data_engine._dataframe_cache_put(
        cache_key,
        pd.DataFrame({"has_u": [0]}),
        ttl_seconds=60.0,
    )
    assert data_engine.estimate_uncached_requests(
        [analysis],
        is_demo=False,
        database_provider=primary,
    ) == 1


def test_demo_compare_disk_cache_informs_strict_and_legacy_request_estimate(
    tmp_path,
    monkeypatch,
):
    """Reserve no HTTP slots when both possible demo Compare reads are on disk."""
    primary, wd2, _wd1 = WSPR_DATABASE_PROVIDERS
    strict_query = "SELECT demo_compare_strict"
    legacy_query = "SELECT demo_compare_legacy"
    analysis = {
        "analysis_kind": "comparison",
        "is_sequential": False,
        "query": strict_query,
        "legacy_query": legacy_query,
        "response_format": "csv",
    }
    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(data_engine, "_dataframe_cache", OrderedDict())

    strict_path = data_engine._query_cache_path(
        strict_query,
        primary,
        is_demo=True,
    )
    legacy_path = data_engine._query_cache_path(
        legacy_query,
        primary,
        is_demo=True,
    )
    strict_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"has_u": [0]}).to_parquet(strict_path, index=False)
    pd.DataFrame({"has_u": [1]}).to_parquet(legacy_path, index=False)
    strict_published_at = strict_path.stat().st_mtime
    legacy_published_at = legacy_path.stat().st_mtime

    assert data_engine.estimate_uncached_requests(
        [analysis],
        is_demo=True,
        database_provider=primary,
    ) == 0
    assert strict_path.stat().st_mtime == strict_published_at
    assert legacy_path.stat().st_mtime == legacy_published_at
    assert data_engine.estimate_uncached_requests(
        [analysis],
        is_demo=True,
        database_provider=wd2,
    ) == 2

    legacy_path.unlink()

    assert data_engine.estimate_uncached_requests(
        [analysis],
        is_demo=True,
        database_provider=primary,
    ) == 1


def test_future_demo_query_mtime_is_rejected_as_an_invalid_freshness_anchor(
    tmp_path,
    monkeypatch,
):
    """Never turn a future filesystem timestamp into a sliding demo lifetime."""
    provider = WSPR_DATABASE_PROVIDERS[0]
    query = "SELECT future_demo_cache_mtime"
    reference_time = time.time()
    future_mtime = reference_time + 300.0
    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(data_engine, "_dataframe_cache", OrderedDict())
    cache_path = data_engine._query_cache_path(
        query,
        provider,
        is_demo=True,
    )
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(b"future timestamp must not be trusted")
    os.utime(cache_path, (future_mtime, future_mtime))

    assert data_engine._query_cache_expiry_epoch(
        cache_path,
        data_engine.DEMO_QUERY_CACHE_TTL_SEC,
        now=reference_time,
    ) is None
    assert not data_engine.is_wspr_query_cached(
        query,
        is_demo=True,
        response_format="csv",
        database_provider=provider,
    )


def test_demo_compare_cache_invalidation_is_scoped_to_provider_and_mode(
    tmp_path,
    monkeypatch,
):
    """Remove one demo's RAM and disk tiers without evicting adjacent identities."""
    primary, wd2, _wd1 = WSPR_DATABASE_PROVIDERS
    query = "SELECT invalid_demo_compare"
    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(data_engine, "_dataframe_cache", OrderedDict())

    primary_demo_key = data_engine._memory_cache_key(
        query,
        is_demo=True,
        database_provider=primary,
    )
    wd2_demo_key = data_engine._memory_cache_key(
        query,
        is_demo=True,
        database_provider=wd2,
    )
    primary_standard_key = data_engine._memory_cache_key(
        query,
        is_demo=False,
        database_provider=primary,
    )
    for cache_key, marker in (
        (primary_demo_key, 1),
        (wd2_demo_key, 2),
        (primary_standard_key, 3),
    ):
        data_engine._dataframe_cache_put(
            cache_key,
            pd.DataFrame({"has_u": [marker]}),
            ttl_seconds=60.0,
        )

    primary_demo_path = data_engine._query_cache_path(
        query,
        primary,
        is_demo=True,
    )
    wd2_demo_path = data_engine._query_cache_path(
        query,
        wd2,
        is_demo=True,
    )
    primary_standard_path = data_engine._query_cache_path(
        query,
        primary,
        is_demo=False,
    )
    for cache_path, marker in (
        (primary_demo_path, 1),
        (wd2_demo_path, 2),
        (primary_standard_path, 3),
    ):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"has_u": [marker]}).to_parquet(cache_path, index=False)

    assert data_engine.invalidate_wspr_query_cache(
        query,
        is_demo=True,
        response_format="csv",
        database_provider=primary,
    )

    assert primary_demo_key not in data_engine._dataframe_cache
    assert not primary_demo_path.exists()
    assert wd2_demo_key in data_engine._dataframe_cache
    assert wd2_demo_path.exists()
    assert primary_standard_key in data_engine._dataframe_cache
    assert primary_standard_path.exists()
    assert data_engine.is_wspr_query_cached(
        query,
        is_demo=True,
        response_format="csv",
        database_provider=wd2,
    )
    assert data_engine.is_wspr_query_cached(
        query,
        is_demo=False,
        response_format="csv",
        database_provider=primary,
    )
    assert not data_engine.invalidate_wspr_query_cache(
        query,
        is_demo=True,
        response_format="csv",
        database_provider=primary,
    )


def test_parquet_response_over_limit_is_not_published(tmp_path, monkeypatch):
    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(data_engine, "WSPR_PARQUET_MAX_RESPONSE_BYTES", 16)
    monkeypatch.setattr(
        data_engine.http_session,
        "get",
        lambda *_args, **_kwargs: _StreamingResponse([b"0123456789", b"abcdefghij"]),
    )

    result = data_engine._fetch_wspr_parquet("SELECT oversized")

    assert result.dataframe is None
    assert result.error.code == "response_too_large"
    assert not Path(result.artifact_path).exists()
    assert list(tmp_path.rglob("*.tmp")) == []


def test_parquet_fetch_preserves_table_after_bounded_stream(tmp_path, monkeypatch):
    expected = pd.DataFrame({"time_slot": [1], "target_seen": [1]})
    source_path = tmp_path / "source.parquet"
    expected.to_parquet(source_path, index=False)
    payload = source_path.read_bytes()

    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(data_engine, "WSPR_PARQUET_MAX_RESPONSE_BYTES", len(payload) + 1)
    request_kwargs = {}

    def fake_get(*_args, **kwargs):
        request_kwargs.update(kwargs)
        return _StreamingResponse([payload[:17], payload[17:]])

    monkeypatch.setattr(data_engine.http_session, "get", fake_get)

    result = data_engine._fetch_wspr_parquet("SELECT bounded")

    pd.testing.assert_frame_equal(
        result.dataframe.reset_index(drop=True),
        expected.astype({"time_slot": "int8", "target_seen": "int8"}),
    )
    assert request_kwargs["stream"] is True
    assert request_kwargs["timeout"] == (
        data_engine.WSPR_HTTP_CONNECT_TIMEOUT_SEC,
        data_engine.WSPR_HTTP_READ_TIMEOUT_SEC,
    )


def test_demo_success_uses_absolute_24_hour_disk_cache_without_touching(
    tmp_path,
    monkeypatch,
):
    """Keep Success demo data in its own namespace with fixed freshness."""
    expected = pd.DataFrame({"time_slot": [1], "target_seen": [1]})
    source_path = tmp_path / "demo-success-source.parquet"
    expected.to_parquet(source_path, index=False)
    payload = source_path.read_bytes()
    request_count = 0

    def fake_get(*_args, **_kwargs):
        nonlocal request_count
        request_count += 1
        return _StreamingResponse([payload])

    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(data_engine.http_session, "get", fake_get)
    query = "SELECT demo_success FORMAT Parquet"

    direct_result = data_engine.fetch_wspr_data(
        query,
        is_demo=True,
        response_format="parquet",
    )
    cache_path = Path(direct_result.artifact_path)
    published_at = time.time() - (23 * 3600)
    os.utime(cache_path, (published_at, published_at))
    published_mtime = cache_path.stat().st_mtime

    first_disk_result = data_engine.fetch_wspr_data(
        query,
        is_demo=True,
        response_format="parquet",
    )
    second_disk_result = data_engine.fetch_wspr_data(
        query,
        is_demo=True,
        response_format="parquet",
    )

    assert request_count == 1
    assert direct_result.source == FetchSource.WSPR_LIVE
    assert first_disk_result.source == FetchSource.DISK_CACHE
    assert second_disk_result.source == FetchSource.DISK_CACHE
    assert cache_path.parent.parent.name == ArtifactNamespace.DEMO_QUERY.value
    assert cache_path.stat().st_mtime == published_mtime
    assert data_engine._query_cache_expiry_epoch(
        cache_path,
        data_engine.DEMO_QUERY_CACHE_TTL_SEC,
        now=published_mtime + data_engine.DEMO_QUERY_CACHE_TTL_SEC - 1.0,
    ) is not None
    assert data_engine._query_cache_expiry_epoch(
        cache_path,
        data_engine.DEMO_QUERY_CACHE_TTL_SEC,
        now=published_mtime + data_engine.DEMO_QUERY_CACHE_TTL_SEC + 1.0,
    ) is None


def test_standard_success_retains_sliding_one_hour_query_cache(
    tmp_path,
    monkeypatch,
):
    """Preserve the ordinary Parquet namespace and access-refresh behavior."""
    source_path = tmp_path / "standard-success-source.parquet"
    pd.DataFrame({"time_slot": [1], "target_seen": [1]}).to_parquet(
        source_path,
        index=False,
    )
    payload = source_path.read_bytes()
    request_count = 0

    def fake_get(*_args, **_kwargs):
        nonlocal request_count
        request_count += 1
        return _StreamingResponse([payload])

    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(data_engine.http_session, "get", fake_get)
    query = "SELECT standard_success FORMAT Parquet"

    direct_result = data_engine.fetch_wspr_data(
        query,
        is_demo=False,
        response_format="parquet",
    )
    cache_path = Path(direct_result.artifact_path)
    previous_access = time.time() - 3500.0
    os.utime(cache_path, (previous_access, previous_access))

    disk_result = data_engine.fetch_wspr_data(
        query,
        is_demo=False,
        response_format="parquet",
    )

    assert request_count == 1
    assert direct_result.source == FetchSource.WSPR_LIVE
    assert disk_result.source == FetchSource.DISK_CACHE
    assert cache_path.parent.parent.name == ArtifactNamespace.QUERY.value
    assert cache_path.stat().st_mtime > previous_access + 3000.0
    assert data_engine.STANDARD_QUERY_CACHE_TTL_SEC == 3600


def test_parquet_fetch_preserves_empty_schema_for_contract_validation(
    tmp_path,
    monkeypatch,
):
    """Keep an empty upstream table inspectable instead of erasing its schema."""
    source_path = tmp_path / "empty-source.parquet"
    pd.DataFrame({"unexpected": pd.Series(dtype="int64")}).to_parquet(
        source_path,
        index=False,
    )
    payload = source_path.read_bytes()
    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(data_engine, "WSPR_PARQUET_MAX_RESPONSE_BYTES", len(payload) + 1)
    monkeypatch.setattr(
        data_engine.http_session,
        "get",
        lambda *_args, **_kwargs: _StreamingResponse([payload]),
    )

    result = data_engine._fetch_wspr_parquet("SELECT empty_schema")

    assert result.error is None
    assert result.dataframe is not None
    assert result.dataframe.empty
    assert list(result.dataframe.columns) == ["unexpected"]
