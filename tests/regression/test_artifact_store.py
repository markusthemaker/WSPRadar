from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import threading
import time
from types import SimpleNamespace

import pytest
import pandas as pd

from core import data_engine
from core.artifact_store import (
    ARTIFACT_STORE,
    ArtifactNamespace,
    ArtifactStore,
    SESSION_ARTIFACT_LEASE_FILENAME,
    SESSION_ARTIFACT_PATHS_KEY,
    cleanup_artifact_namespaces,
    register_session_artifact,
    release_registered_session_artifacts,
    retire_registered_session_artifacts,
    session_artifact_path,
    touch_registered_session_artifacts,
)


def _make_stale(path: Path, *, seconds: float = 120.0) -> None:
    stale_time = time.time() - seconds
    os.utime(path, (stale_time, stale_time))


def test_artifact_namespaces_are_separate_and_reject_traversal(tmp_path):
    store = ArtifactStore(lock_stripes=4)

    query_path = store.namespace_path(tmp_path, ArtifactNamespace.QUERY, "same.parquet")
    derived_path = store.namespace_path(tmp_path, ArtifactNamespace.DERIVED_ANALYSIS, "same.parquet")
    session_path = store.namespace_path(tmp_path, ArtifactNamespace.SESSION_ARTIFACT, "same.parquet")

    assert query_path.parent.name == "queries"
    assert derived_path.parent.name == "derived-analysis"
    assert session_path.parent.name == "session-artifacts"
    assert len({query_path.resolve(), derived_path.resolve(), session_path.resolve()}) == 3
    with pytest.raises(ValueError):
        store.namespace_path(tmp_path, ArtifactNamespace.QUERY, "..", "escape.parquet")


def test_atomic_output_is_unique_and_invisible_until_replace(tmp_path):
    store = ArtifactStore(lock_stripes=4)
    destination = store.namespace_path(tmp_path, ArtifactNamespace.QUERY, "artifact.bin")
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"old")

    with store.key_lock(destination):
        with store.atomic_output_path(destination) as temporary_path:
            assert temporary_path.parent == destination.parent
            assert temporary_path != destination
            temporary_path.write_bytes(b"new")
            assert destination.read_bytes() == b"old"

    assert destination.read_bytes() == b"new"
    assert list(destination.parent.glob("*.tmp")) == []


def test_same_key_builds_once_and_lock_bookkeeping_is_bounded(tmp_path):
    worker_count = 8
    store = ArtifactStore(lock_stripes=8)
    destination = store.namespace_path(tmp_path, ArtifactNamespace.DERIVED_ANALYSIS, "shared.bin")
    start_barrier = threading.Barrier(worker_count)
    build_count = 0
    build_count_guard = threading.Lock()

    def ensure_artifact(_index):
        nonlocal build_count
        start_barrier.wait()
        with store.key_lock(destination):
            if destination.exists():
                return "hit"
            with build_count_guard:
                build_count += 1
            with store.atomic_output_path(destination) as temporary_path:
                time.sleep(0.03)
                temporary_path.write_bytes(b"complete")
            return "miss"

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        statuses = list(executor.map(ensure_artifact, range(worker_count)))

    assert build_count == 1
    assert statuses.count("miss") == 1
    assert statuses.count("hit") == worker_count - 1
    assert destination.read_bytes() == b"complete"
    assert store.lock_bookkeeping_size == 8
    assert list((tmp_path / ".artifact-locks").glob("*.lock")) == []


def test_active_read_lease_serializes_ttl_cleanup(tmp_path):
    store = ArtifactStore(lock_stripes=4)
    artifact_path = store.namespace_path(
        tmp_path,
        ArtifactNamespace.SESSION_ARTIFACT,
        "session-a",
        "artifact.bin",
    )
    store.write(artifact_path, lambda temporary_path: temporary_path.write_bytes(b"leased"))
    lease_started = threading.Event()
    release_lease = threading.Event()

    def hold_stale_lease():
        with store.lease(artifact_path):
            _make_stale(artifact_path)
            lease_started.set()
            release_lease.wait(timeout=2.0)

    with ThreadPoolExecutor(max_workers=2) as executor:
        lease_future = executor.submit(hold_stale_lease)
        assert lease_started.wait(timeout=1.0)
        cleanup_future = executor.submit(
            store.cleanup_namespace,
            tmp_path,
            ArtifactNamespace.SESSION_ARTIFACT,
            ttl_seconds=60.0,
        )
        time.sleep(0.05)
        assert artifact_path.exists()
        assert not cleanup_future.done()
        release_lease.set()
        lease_future.result(timeout=1.0)
        assert cleanup_future.result(timeout=1.0) == 1

    assert not artifact_path.exists()


def test_registered_session_artifacts_are_touched_and_released(tmp_path):
    state = {}
    artifact_path = session_artifact_path(
        tmp_path,
        state,
        run_id=123,
        analysis_id="RX_ABS",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"session")
    register_session_artifact(state, artifact_path)
    register_session_artifact(state, artifact_path)
    lease_path = artifact_path.parent / SESSION_ARTIFACT_LEASE_FILENAME
    _make_stale(artifact_path)

    assert len(state[SESSION_ARTIFACT_PATHS_KEY]) == 1
    assert lease_path.is_file()
    assert touch_registered_session_artifacts(state) == 1
    assert artifact_path.stat().st_mtime > time.time() - 5.0
    assert lease_path.stat().st_mtime > time.time() - 5.0
    assert release_registered_session_artifacts(state) == 1
    assert SESSION_ARTIFACT_PATHS_KEY not in state
    assert not artifact_path.exists()
    assert not lease_path.exists()


def test_active_session_lease_prevents_ttl_cleanup(tmp_path):
    state = {}
    artifact_path = session_artifact_path(
        tmp_path,
        state,
        run_id=123,
        analysis_id="RX_COMP",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"active-session")
    register_session_artifact(state, artifact_path)
    _make_stale(artifact_path)

    removed = cleanup_artifact_namespaces(tmp_path, ttl_seconds=60.0)

    assert removed[ArtifactNamespace.SESSION_ARTIFACT.value] == 0
    assert artifact_path.read_bytes() == b"active-session"


def test_retired_session_artifact_remains_readable_until_lease_ttl(tmp_path):
    state = {}
    artifact_path = session_artifact_path(
        tmp_path,
        state,
        run_id=123,
        analysis_id="RX_COMP",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"retired-session")
    register_session_artifact(state, artifact_path)
    lease_path = artifact_path.parent / SESSION_ARTIFACT_LEASE_FILENAME

    assert retire_registered_session_artifacts(state) == 1
    assert SESSION_ARTIFACT_PATHS_KEY not in state
    assert artifact_path.read_bytes() == b"retired-session"

    _make_stale(artifact_path)
    _make_stale(lease_path)
    removed = cleanup_artifact_namespaces(tmp_path, ttl_seconds=60.0)

    assert removed[ArtifactNamespace.SESSION_ARTIFACT.value] == 2
    assert not artifact_path.exists()
    assert not lease_path.exists()


def test_old_fragment_access_revives_a_retired_run_lease(tmp_path):
    state = {}
    artifact_path = session_artifact_path(
        tmp_path,
        state,
        run_id=123,
        analysis_id="RX_COMP",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"fragment-access")
    register_session_artifact(state, artifact_path)
    lease_path = artifact_path.parent / SESSION_ARTIFACT_LEASE_FILENAME
    retire_registered_session_artifacts(state)
    _make_stale(artifact_path)
    _make_stale(lease_path)

    assert ARTIFACT_STORE.touch(artifact_path)
    removed = cleanup_artifact_namespaces(tmp_path, ttl_seconds=60.0)

    assert removed[ArtifactNamespace.SESSION_ARTIFACT.value] == 0
    assert artifact_path.read_bytes() == b"fragment-access"
    assert lease_path.stat().st_mtime > time.time() - 5.0


def test_result_export_reset_retires_without_deleting_active_parquet(tmp_path, monkeypatch):
    from ui import results_export

    state = {"run_id": 456}
    artifact_path = session_artifact_path(
        tmp_path,
        state,
        run_id=456,
        analysis_id="RX_COMP",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"still-readable")
    register_session_artifact(state, artifact_path)
    monkeypatch.setattr(results_export, "st", SimpleNamespace(session_state=state))

    results_export.reset_result_export_state()

    assert artifact_path.read_bytes() == b"still-readable"
    assert SESSION_ARTIFACT_PATHS_KEY not in state


def test_namespace_cleanup_expires_query_and_session_but_not_derived(tmp_path):
    store = ArtifactStore(lock_stripes=4)
    paths = {
        namespace: store.namespace_path(tmp_path, namespace, "stale.bin")
        for namespace in ArtifactNamespace
    }
    for path in paths.values():
        store.write(path, lambda temporary_path: temporary_path.write_bytes(b"stale"))
        _make_stale(path)

    removed = cleanup_artifact_namespaces(tmp_path, ttl_seconds=60.0)

    assert removed == {"queries": 1, "session-artifacts": 1}
    assert not paths[ArtifactNamespace.QUERY].exists()
    assert not paths[ArtifactNamespace.SESSION_ARTIFACT].exists()
    assert paths[ArtifactNamespace.DERIVED_ANALYSIS].exists()


def test_query_cache_constructs_once_under_concurrency(tmp_path, monkeypatch):
    worker_count = 6
    start_barrier = threading.Barrier(worker_count)
    request_count = 0
    request_count_guard = threading.Lock()

    class FakeResponse:
        status_code = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def iter_content(self, chunk_size):
            assert chunk_size == 1024 * 1024
            time.sleep(0.03)
            yield b"parquet-payload"

    def fake_get(*_args, **_kwargs):
        nonlocal request_count
        with request_count_guard:
            request_count += 1
        return FakeResponse()

    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(data_engine, "CACHE_TTL_SEC", 3600)
    monkeypatch.setattr(data_engine.http_session, "get", fake_get)
    monkeypatch.setattr(
        data_engine,
        "_read_query_parquet",
        lambda _path: pd.DataFrame({"value": [1]}),
    )

    def fetch_query(_index):
        start_barrier.wait()
        return data_engine._fetch_wspr_parquet("SELECT 1")

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = list(executor.map(fetch_query, range(worker_count)))

    cache_path = data_engine._query_cache_path("SELECT 1")
    assert request_count == 1
    assert all(
        result.dataframe.equals(pd.DataFrame({"value": [1]}))
        for result in results
    )
    assert cache_path.parent.name == "queries"
    assert cache_path.read_bytes() == b"parquet-payload"
    assert list(cache_path.parent.glob("*.tmp")) == []
    assert list((tmp_path / ".artifact-locks").glob("*.lock")) == []
