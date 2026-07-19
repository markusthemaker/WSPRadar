from concurrent.futures import ThreadPoolExecutor
import threading

import pytest

from core import data_engine
from core.artifact_store import ArtifactNamespace


def _zero_cleanup_counts():
    """Return the stable result shape used when a cleanup sweep is skipped."""
    return {
        ArtifactNamespace.QUERY.value: 0,
        ArtifactNamespace.DEMO_QUERY.value: 0,
        ArtifactNamespace.SESSION_ARTIFACT.value: 0,
    }


def _reset_cleanup_gate(monkeypatch):
    """Give one test an isolated process-local cleanup gate and timestamp."""
    monkeypatch.setattr(data_engine, "_artifact_cleanup_guard", threading.Lock())
    monkeypatch.setattr(data_engine, "_last_artifact_cleanup_monotonic", None)


def test_cleanup_old_parquets_allows_only_one_concurrent_sweep(monkeypatch):
    """Skip an overlapping trigger instead of starting or waiting for another scan."""
    _reset_cleanup_gate(monkeypatch)
    cleanup_started = threading.Event()
    release_cleanup = threading.Event()
    cleanup_calls = 0
    cleanup_calls_guard = threading.Lock()
    completed_counts = {
        ArtifactNamespace.QUERY.value: 2,
        ArtifactNamespace.DEMO_QUERY.value: 3,
        ArtifactNamespace.SESSION_ARTIFACT.value: 4,
    }

    def blocking_cleanup(*_args, **_kwargs):
        nonlocal cleanup_calls
        with cleanup_calls_guard:
            cleanup_calls += 1
        cleanup_started.set()
        assert release_cleanup.wait(timeout=2.0)
        return completed_counts

    monkeypatch.setattr(
        data_engine,
        "cleanup_artifact_namespaces",
        blocking_cleanup,
    )

    with ThreadPoolExecutor(max_workers=2) as executor:
        active_cleanup = executor.submit(data_engine.cleanup_old_parquets)
        assert cleanup_started.wait(timeout=1.0)

        overlapping_cleanup = executor.submit(data_engine.cleanup_old_parquets)
        assert overlapping_cleanup.result(timeout=0.5) == _zero_cleanup_counts()

        release_cleanup.set()
        assert active_cleanup.result(timeout=1.0) == completed_counts

    assert cleanup_calls == 1


def test_cleanup_old_parquets_throttles_after_a_successful_sweep(monkeypatch):
    """Return zero counts until the post-success minimum interval has elapsed."""
    _reset_cleanup_gate(monkeypatch)
    monotonic_time = [100.0]
    cleanup_calls = 0
    completed_counts = {
        ArtifactNamespace.QUERY.value: 1,
        ArtifactNamespace.DEMO_QUERY.value: 0,
        ArtifactNamespace.SESSION_ARTIFACT.value: 2,
    }

    def successful_cleanup(*_args, **_kwargs):
        nonlocal cleanup_calls
        cleanup_calls += 1
        return completed_counts

    monkeypatch.setattr(data_engine.time, "monotonic", lambda: monotonic_time[0])
    monkeypatch.setattr(
        data_engine,
        "cleanup_artifact_namespaces",
        successful_cleanup,
    )

    assert data_engine.cleanup_old_parquets() == completed_counts

    monotonic_time[0] += data_engine._ARTIFACT_CLEANUP_MIN_INTERVAL_SECONDS - 0.001
    assert data_engine.cleanup_old_parquets() == _zero_cleanup_counts()
    assert cleanup_calls == 1

    monotonic_time[0] += 0.001
    assert data_engine.cleanup_old_parquets() == completed_counts
    assert cleanup_calls == 2


def test_cleanup_old_parquets_retries_after_a_failed_sweep(monkeypatch):
    """Release the gate without advancing the throttle timestamp after failure."""
    _reset_cleanup_gate(monkeypatch)
    cleanup_calls = 0
    completed_counts = {
        ArtifactNamespace.QUERY.value: 0,
        ArtifactNamespace.DEMO_QUERY.value: 1,
        ArtifactNamespace.SESSION_ARTIFACT.value: 0,
    }

    def fail_then_succeed(*_args, **_kwargs):
        nonlocal cleanup_calls
        cleanup_calls += 1
        if cleanup_calls == 1:
            raise OSError("simulated cleanup failure")
        return completed_counts

    monkeypatch.setattr(
        data_engine,
        "cleanup_artifact_namespaces",
        fail_then_succeed,
    )

    with pytest.raises(OSError, match="simulated cleanup failure"):
        data_engine.cleanup_old_parquets()

    assert data_engine._last_artifact_cleanup_monotonic is None
    assert data_engine.cleanup_old_parquets() == completed_counts
    assert cleanup_calls == 2
