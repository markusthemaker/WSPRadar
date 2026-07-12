from pathlib import Path
import uuid

import pandas as pd
import requests

from core import data_engine


class _StreamingResponse:
    def __init__(self, chunks, *, status_code=200, encoding="utf-8"):
        self.chunks = list(chunks)
        self.status_code = status_code
        self.encoding = encoding

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
    assert "shorten the time range" in result.error.message


def test_csv_timeout_returns_clear_retry_message(monkeypatch):
    def raise_timeout(*_args, **_kwargs):
        raise requests.ReadTimeout("upstream stalled")

    monkeypatch.setattr(data_engine.http_session, "get", raise_timeout)
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"

    result = data_engine.fetch_wspr_data(query)

    assert result.error.code == "timeout"
    assert "try again shortly" in result.error.message.lower()


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
