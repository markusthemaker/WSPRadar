from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import threading
import time
from types import SimpleNamespace

import pytest
import pandas as pd

from config import WSPR_DATABASE_PROVIDERS
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
    demo_query_path = store.namespace_path(
        tmp_path,
        ArtifactNamespace.DEMO_QUERY,
        "same.parquet",
    )
    derived_path = store.namespace_path(tmp_path, ArtifactNamespace.DERIVED_ANALYSIS, "same.parquet")
    session_path = store.namespace_path(tmp_path, ArtifactNamespace.SESSION_ARTIFACT, "same.parquet")

    assert query_path.parent.name == "queries"
    assert demo_query_path.parent.name == "demo-queries"
    assert derived_path.parent.name == "derived-analysis"
    assert session_path.parent.name == "session-artifacts"
    assert len(
        {
            query_path.resolve(),
            demo_query_path.resolve(),
            derived_path.resolve(),
            session_path.resolve(),
        }
    ) == 4
    with pytest.raises(ValueError):
        store.namespace_path(tmp_path, ArtifactNamespace.QUERY, "..", "escape.parquet")


@pytest.mark.skipif(os.name != "nt", reason="Windows extended-path normalization")
def test_lock_key_normalizes_windows_extended_length_prefix(monkeypatch):
    """Treat transient extended and ordinary spellings as one lock key."""
    extended_path = Path(r"\\?\C:\cache\query.parquet")
    monkeypatch.setattr(Path, "resolve", lambda _path: extended_path)

    assert ArtifactStore._canonical_key("ignored") == os.path.normcase(
        r"C:\cache\query.parquet"
    )


@pytest.mark.skipif(os.name != "nt", reason="Windows extended-path normalization")
def test_namespace_validation_normalizes_mixed_windows_path_spellings(monkeypatch):
    """Do not reject one safe path when resolve transiently adds its prefix."""
    def mixed_resolve(path):
        if path.name == ArtifactNamespace.QUERY.value:
            return Path(r"C:\cache\queries")
        return Path(r"\\?\C:\cache\queries\wspr_live\query.parquet")

    monkeypatch.setattr(Path, "resolve", mixed_resolve)
    store = ArtifactStore()

    path = store.namespace_path(
        r"C:\cache",
        ArtifactNamespace.QUERY,
        "wspr_live",
        "query.parquet",
    )

    assert path == Path(r"C:\cache\queries\wspr_live\query.parquet")


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


def test_query_cleanup_does_not_delete_an_active_atomic_output(tmp_path):
    """Keep a writer's unique sibling and parent intact during cleanup."""
    store = ArtifactStore(lock_stripes=4)
    destination = store.namespace_path(
        tmp_path,
        ArtifactNamespace.QUERY,
        "wspr_live",
        "query.parquet",
    )
    temporary_path_ready = threading.Event()
    allow_publication = threading.Event()
    active_temporary_path = None

    def publish_artifact():
        nonlocal active_temporary_path
        with store.key_lock(destination):
            with store.atomic_output_path(destination) as temporary_path:
                active_temporary_path = temporary_path
                temporary_path.write_bytes(b"complete")
                temporary_path_ready.set()
                assert allow_publication.wait(timeout=2.0)

    with ThreadPoolExecutor(max_workers=2) as executor:
        publication_future = executor.submit(publish_artifact)
        assert temporary_path_ready.wait(timeout=1.0)

        cleanup_future = executor.submit(
            store.cleanup_namespace,
            tmp_path,
            ArtifactNamespace.QUERY,
            ttl_seconds=3600.0,
            now=time.time() - 1.0,
        )
        try:
            assert cleanup_future.result(timeout=1.0) == 0
            assert active_temporary_path is not None
            assert active_temporary_path.read_bytes() == b"complete"
            assert destination.parent.is_dir()
        finally:
            allow_publication.set()

        publication_future.result(timeout=1.0)

    assert destination.read_bytes() == b"complete"
    assert list(destination.parent.glob("*.tmp")) == []


def test_stale_atomic_temporary_cleanup_uses_destination_key_coordination(
    tmp_path,
):
    """Remove only old orphan siblings and wait for the destination owner."""
    store = ArtifactStore(
        lock_stripes=4,
        lock_timeout_seconds=1.0,
        stale_lock_seconds=2.0,
    )
    destination = store.namespace_path(
        tmp_path,
        ArtifactNamespace.QUERY,
        "wspr_live",
        "query.parquet",
    )
    temporary_path = destination.with_name(
        f".{destination.name}.{'a' * 32}.tmp"
    )
    temporary_path.parent.mkdir(parents=True)
    temporary_path.write_bytes(b"orphan")
    reference_time = time.time()

    assert store.cleanup_stale_temporary_files(
        tmp_path,
        ArtifactNamespace.QUERY,
        now=reference_time,
    ) == 0
    assert temporary_path.read_bytes() == b"orphan"

    os.utime(
        temporary_path,
        (reference_time - 3.0, reference_time - 3.0),
    )
    destination_lock_acquired = threading.Event()
    release_destination_lock = threading.Event()
    cleanup_call_started = threading.Event()

    def hold_destination_lock():
        with store.key_lock(destination):
            destination_lock_acquired.set()
            assert release_destination_lock.wait(timeout=2.0)

    def clean_orphan():
        cleanup_call_started.set()
        return store.cleanup_stale_temporary_files(
            tmp_path,
            ArtifactNamespace.QUERY,
            now=reference_time,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        lock_future = executor.submit(hold_destination_lock)
        assert destination_lock_acquired.wait(timeout=1.0)
        cleanup_future = executor.submit(clean_orphan)
        assert cleanup_call_started.wait(timeout=1.0)
        time.sleep(0.05)
        assert not cleanup_future.done()
        assert temporary_path.read_bytes() == b"orphan"

        os.utime(temporary_path, None)
        release_destination_lock.set()
        lock_future.result(timeout=1.0)
        assert cleanup_future.result(timeout=1.0) == 0

    assert temporary_path.read_bytes() == b"orphan"
    os.utime(
        temporary_path,
        (reference_time - 3.0, reference_time - 3.0),
    )
    assert store.cleanup_stale_temporary_files(
        tmp_path,
        ArtifactNamespace.QUERY,
        now=reference_time,
    ) == 1

    assert not temporary_path.exists()


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


def test_no_touch_lease_preserves_demo_query_publication_time(tmp_path):
    """Keep demo freshness absolute while coordinating a disk-cache read."""
    store = ArtifactStore(lock_stripes=4)
    artifact_path = store.namespace_path(
        tmp_path,
        ArtifactNamespace.DEMO_QUERY,
        "wspr_live",
        "query.parquet",
    )
    store.write(
        artifact_path,
        lambda temporary_path: temporary_path.write_bytes(b"demo-query"),
    )
    published_at = time.time() - 3600.0
    os.utime(artifact_path, (published_at, published_at))

    with store.lease(artifact_path, refresh_access=False) as leased_path:
        assert leased_path.read_bytes() == b"demo-query"

    assert artifact_path.stat().st_mtime == pytest.approx(published_at, abs=0.01)


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
    assert artifact_path.parent.is_dir()


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


def test_namespace_cleanup_applies_independent_query_lifetimes(tmp_path):
    """Expire ordinary data before demo queries and never age derived data here."""
    store = ArtifactStore(lock_stripes=4)
    paths = {
        namespace: store.namespace_path(tmp_path, namespace, "stale.bin")
        for namespace in ArtifactNamespace
    }
    for path in paths.values():
        store.write(path, lambda temporary_path: temporary_path.write_bytes(b"stale"))
        _make_stale(path)

    removed = cleanup_artifact_namespaces(
        tmp_path,
        query_ttl_seconds=60.0,
        demo_query_ttl_seconds=3600.0,
        session_ttl_seconds=60.0,
    )

    assert removed == {
        "queries": 1,
        "demo-queries": 0,
        "session-artifacts": 1,
    }
    assert not paths[ArtifactNamespace.QUERY].exists()
    assert paths[ArtifactNamespace.DEMO_QUERY].exists()
    assert not paths[ArtifactNamespace.SESSION_ARTIFACT].exists()
    assert paths[ArtifactNamespace.DERIVED_ANALYSIS].exists()

    _make_stale(paths[ArtifactNamespace.DEMO_QUERY], seconds=3700.0)
    second_removed = cleanup_artifact_namespaces(
        tmp_path,
        query_ttl_seconds=60.0,
        demo_query_ttl_seconds=3600.0,
        session_ttl_seconds=60.0,
    )

    assert second_removed[ArtifactNamespace.DEMO_QUERY.value] == 1
    assert not paths[ArtifactNamespace.DEMO_QUERY].exists()
    assert paths[ArtifactNamespace.DERIVED_ANALYSIS].exists()


def test_namespace_cleanup_reaps_only_orphaned_derived_temporary_outputs(
    tmp_path,
    monkeypatch,
):
    """Leave published basemaps untimed while reaping stale atomic siblings."""
    published_path = ARTIFACT_STORE.namespace_path(
        tmp_path,
        ArtifactNamespace.DERIVED_ANALYSIS,
        "basemaps",
        "map.png",
    )
    temporary_path = published_path.with_name(
        f".{published_path.name}.{'a' * 32}.tmp"
    )
    published_path.parent.mkdir(parents=True)
    published_path.write_bytes(b"published")
    temporary_path.write_bytes(b"orphan")
    monkeypatch.setattr(
        ARTIFACT_STORE,
        "_stale_lock_seconds",
        60.0,
    )
    _make_stale(temporary_path, seconds=61.0)

    cleanup_artifact_namespaces(tmp_path, ttl_seconds=60.0)

    assert published_path.read_bytes() == b"published"
    assert not temporary_path.exists()


def test_query_cleanup_rejects_future_mtimes_without_expiring_session_data(
    tmp_path,
):
    """Treat future query timestamps as corrupt while preserving session safety."""
    store = ArtifactStore(lock_stripes=4)
    reference_time = time.time()
    future_mtime = reference_time + 300.0
    paths = {
        namespace: store.namespace_path(tmp_path, namespace, "future.bin")
        for namespace in (
            ArtifactNamespace.QUERY,
            ArtifactNamespace.DEMO_QUERY,
            ArtifactNamespace.SESSION_ARTIFACT,
        )
    }
    for artifact_path in paths.values():
        store.write(
            artifact_path,
            lambda temporary_path: temporary_path.write_bytes(b"future"),
        )
        os.utime(artifact_path, (future_mtime, future_mtime))

    assert store.cleanup_namespace(
        tmp_path,
        ArtifactNamespace.QUERY,
        ttl_seconds=60.0,
        now=reference_time,
    ) == 1
    assert store.cleanup_namespace(
        tmp_path,
        ArtifactNamespace.DEMO_QUERY,
        ttl_seconds=60.0,
        now=reference_time,
    ) == 1
    assert store.cleanup_namespace(
        tmp_path,
        ArtifactNamespace.SESSION_ARTIFACT,
        ttl_seconds=60.0,
        now=reference_time,
    ) == 0

    assert not paths[ArtifactNamespace.QUERY].exists()
    assert not paths[ArtifactNamespace.DEMO_QUERY].exists()
    assert paths[ArtifactNamespace.SESSION_ARTIFACT].exists()


@pytest.mark.parametrize(
    "namespace",
    (ArtifactNamespace.QUERY, ArtifactNamespace.DEMO_QUERY),
)
def test_query_cleanup_preserves_files_written_after_its_scan_reference(
    tmp_path,
    namespace,
):
    """Do not mistake a concurrent publication for a corrupt future timestamp."""
    store = ArtifactStore(lock_stripes=4)
    cleanup_scan_started_at = time.time()
    artifact_path = store.namespace_path(
        tmp_path,
        namespace,
        "wspr_live",
        "query.parquet",
    )
    store.write(
        artifact_path,
        lambda temporary_path: temporary_path.write_bytes(b"concurrent"),
    )

    assert artifact_path.stat().st_mtime > cleanup_scan_started_at
    assert store.cleanup_namespace(
        tmp_path,
        namespace,
        ttl_seconds=60.0,
        now=cleanup_scan_started_at,
    ) == 0
    assert artifact_path.read_bytes() == b"concurrent"


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
    monkeypatch.setattr(data_engine, "STANDARD_QUERY_CACHE_TTL_SEC", 3600)
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
    assert cache_path.parent.name == "wspr_live"
    assert cache_path.parent.parent.name == "queries"
    assert cache_path.read_bytes() == b"parquet-payload"
    assert list(cache_path.parent.glob("*.tmp")) == []
    assert list((tmp_path / ".artifact-locks").glob("*.lock")) == []


def test_query_cache_paths_are_isolated_by_database_and_demo_policy(
    tmp_path,
    monkeypatch,
):
    """Prevent provider or lifecycle identity from sharing one raw cache file."""
    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path))
    query = "SELECT source_isolation"

    standard_paths = [
        data_engine._query_cache_path(query, provider)
        for provider in WSPR_DATABASE_PROVIDERS
    ]
    demo_paths = [
        data_engine._query_cache_path(query, provider, is_demo=True)
        for provider in WSPR_DATABASE_PROVIDERS
    ]
    paths = standard_paths + demo_paths

    assert len({path.resolve() for path in paths}) == 6
    assert [path.parent.name for path in standard_paths] == ["wspr_live", "wd2", "wd1"]
    assert [path.parent.name for path in demo_paths] == ["wspr_live", "wd2", "wd1"]
    assert all(path.parent.parent.name == "queries" for path in standard_paths)
    assert all(path.parent.parent.name == "demo-queries" for path in demo_paths)
