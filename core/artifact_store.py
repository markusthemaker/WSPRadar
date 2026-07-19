"""Concurrency-safe lifecycle helpers for WSPRadar disk artifacts."""

from __future__ import annotations

from contextlib import contextmanager
from enum import Enum
import hashlib
import os
from pathlib import Path
import re
import threading
import time
from typing import Callable, Iterator, MutableMapping
import uuid


class ArtifactNamespace(str, Enum):
    """Independent cache lifecycles rooted below ``CACHE_DIR``."""

    QUERY = "queries"
    DEMO_QUERY = "demo-queries"
    DERIVED_ANALYSIS = "derived-analysis"
    SESSION_ARTIFACT = "session-artifacts"


SESSION_ARTIFACT_OWNER_KEY = "_artifact_session_id"
SESSION_ARTIFACT_PATHS_KEY = "_session_artifact_paths"
SESSION_ARTIFACT_LEASE_FILENAME = ".active-lease"


def _session_run_directory(path: Path) -> Path | None:
    """Return the owning session-run directory for one session artifact path."""
    path = Path(path)
    for directory in path.parents:
        try:
            if directory.parent.parent.name == ArtifactNamespace.SESSION_ARTIFACT.value:
                return directory
        except IndexError:
            break
    return None


def _session_lease_path(path: Path) -> Path | None:
    run_directory = _session_run_directory(Path(path))
    if run_directory is None:
        return None
    return run_directory / SESSION_ARTIFACT_LEASE_FILENAME


def _safe_path_token(value, fallback: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_-]+", "-", str(value or "").strip()).strip("-_")
    return token or fallback


class ArtifactStore:
    """Coordinate keyed construction, atomic publication, reads, and cleanup."""

    def __init__(
        self,
        *,
        lock_stripes: int = 64,
        lock_timeout_seconds: float = 300.0,
        stale_lock_seconds: float = 3600.0,
    ) -> None:
        stripe_count = max(int(lock_stripes), 1)
        self._lock_stripes = tuple(threading.Lock() for _ in range(stripe_count))
        self._lock_timeout_seconds = max(float(lock_timeout_seconds), 1.0)
        self._stale_lock_seconds = max(float(stale_lock_seconds), self._lock_timeout_seconds * 2.0)

    @property
    def lock_bookkeeping_size(self) -> int:
        """Return the fixed number of in-process lock stripes."""
        return len(self._lock_stripes)

    def namespace_path(
        self,
        cache_root,
        namespace: ArtifactNamespace | str,
        *parts,
    ) -> Path:
        """Return a validated path inside one artifact namespace."""
        namespace = ArtifactNamespace(namespace)
        base_path = Path(cache_root) / namespace.value
        candidate = base_path.joinpath(*(str(part) for part in parts))
        canonical_base = self._canonical_key(base_path)
        canonical_candidate = self._canonical_key(candidate)
        try:
            is_inside_namespace = (
                os.path.commonpath((canonical_base, canonical_candidate))
                == canonical_base
            )
        except ValueError:
            is_inside_namespace = False
        if not is_inside_namespace:
            raise ValueError(f"Artifact path escapes namespace: {candidate}")
        return candidate

    @staticmethod
    def _canonical_key(path) -> str:
        """Return one stable lock key, including during Windows path creation.

        Windows can expose the same resolved local path both with and without
        its extended-length prefix while parent directories are being
        created concurrently. Treating those spellings as different keys would
        defeat in-process single-flight coordination.
        """
        canonical_path = os.path.normcase(str(Path(path).resolve()))
        if os.name == "nt" and canonical_path.startswith("\\\\?\\"):
            canonical_path = canonical_path[4:]
            if canonical_path.startswith("unc\\"):
                canonical_path = "\\\\" + canonical_path[4:]
        return canonical_path

    @staticmethod
    def _cache_root_for(path: Path) -> Path:
        namespace_names = {namespace.value for namespace in ArtifactNamespace}
        for parent in (path, *path.parents):
            if parent.name in namespace_names:
                return parent.parent
        return path.parent

    def _lock_file_path(self, path: Path, key_digest: str) -> Path:
        return self._cache_root_for(path) / ".artifact-locks" / f"{key_digest}.lock"

    def _acquire_file_lock(self, lock_path: Path) -> str:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        token = uuid.uuid4().hex
        deadline = time.monotonic() + self._lock_timeout_seconds

        while True:
            try:
                descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                try:
                    lock_age = time.time() - lock_path.stat().st_mtime
                except FileNotFoundError:
                    continue
                if lock_age > self._stale_lock_seconds:
                    try:
                        lock_path.unlink()
                    except FileNotFoundError:
                        pass
                    except OSError:
                        time.sleep(0.02)
                    continue
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Timed out waiting for artifact lock: {lock_path}")
                time.sleep(0.02)
                continue

            try:
                os.write(descriptor, token.encode("ascii"))
            finally:
                os.close(descriptor)
            return token

    @staticmethod
    def _release_file_lock(lock_path: Path, token: str) -> None:
        try:
            if lock_path.read_text(encoding="ascii") == token:
                lock_path.unlink()
        except (FileNotFoundError, OSError, UnicodeError):
            pass

    @contextmanager
    def key_lock(self, path) -> Iterator[None]:
        """Serialize one artifact key across threads and cooperating processes."""
        artifact_path = Path(path)
        key = self._canonical_key(artifact_path)
        key_digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        stripe = self._lock_stripes[int(key_digest[:16], 16) % len(self._lock_stripes)]
        lock_path = self._lock_file_path(artifact_path, key_digest)

        with stripe:
            token = self._acquire_file_lock(lock_path)
            try:
                yield
            finally:
                self._release_file_lock(lock_path, token)

    @contextmanager
    def atomic_output_path(self, destination) -> Iterator[Path]:
        """Yield a unique sibling path and atomically publish it on success."""
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = destination.with_name(
            f".{destination.name}.{uuid.uuid4().hex}.tmp"
        )
        try:
            yield temporary_path
            if not temporary_path.is_file():
                raise FileNotFoundError(f"Artifact writer produced no file: {temporary_path}")
            os.replace(temporary_path, destination)
            self.touch_unlocked(destination)
        finally:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                pass

    def write(self, destination, writer: Callable[[Path], None]) -> Path:
        """Write one artifact under its key lock and publish it atomically."""
        destination = Path(destination)
        with self.key_lock(destination):
            with self.atomic_output_path(destination) as temporary_path:
                writer(temporary_path)
        return destination

    @staticmethod
    def touch_unlocked(path) -> bool:
        """Refresh one artifact while its caller already owns the key lock."""
        try:
            os.utime(path, None)
            return True
        except OSError:
            return False

    @staticmethod
    def touch_session_lease_unlocked(path) -> bool:
        """Refresh the owning session-run heartbeat when ``path`` is session data."""
        lease_path = _session_lease_path(Path(path))
        if lease_path is None:
            return False
        try:
            lease_path.parent.mkdir(parents=True, exist_ok=True)
            lease_path.touch(exist_ok=True)
            return True
        except OSError:
            return False

    @staticmethod
    def _has_active_session_lease(path, cutoff: float) -> bool:
        lease_path = _session_lease_path(Path(path))
        if lease_path is None:
            return False
        try:
            return lease_path.stat().st_mtime >= cutoff
        except OSError:
            return False

    def touch(self, path) -> bool:
        """Refresh one artifact's last-access timestamp when it still exists."""
        path = Path(path)
        with self.key_lock(path):
            touched = self.touch_unlocked(path)
            if touched:
                self.touch_session_lease_unlocked(path)
            return touched

    @contextmanager
    def lease(self, path, *, refresh_access: bool = True) -> Iterator[Path]:
        """Protect an artifact from cleanup for one coordinated read.

        ``refresh_access`` remains enabled for sliding-lifetime query and
        session artifacts. Demo-query readers disable it so the file's
        publication mtime remains an absolute fetched-at timestamp.
        """
        path = Path(path)
        with self.key_lock(path):
            if not path.is_file():
                raise FileNotFoundError(path)
            if refresh_access:
                self.touch_unlocked(path)
                self.touch_session_lease_unlocked(path)
            yield path

    def delete(self, path) -> bool:
        """Delete one artifact only while no coordinated reader or writer uses it."""
        path = Path(path)
        with self.key_lock(path):
            try:
                path.unlink()
                return True
            except FileNotFoundError:
                return False

    def cleanup_namespace(
        self,
        cache_root,
        namespace: ArtifactNamespace | str,
        *,
        ttl_seconds: float,
        now: float | None = None,
    ) -> int:
        """Delete stale files in one namespace without racing active operations."""
        namespace = ArtifactNamespace(namespace)
        namespace_root = self.namespace_path(cache_root, namespace)
        if not namespace_root.exists():
            return 0

        reference_time = time.time() if now is None else float(now)
        cutoff = reference_time - max(float(ttl_seconds), 0.0)
        rejects_future_timestamp = namespace in {
            ArtifactNamespace.QUERY,
            ArtifactNamespace.DEMO_QUERY,
        }
        removed = 0
        candidates = [path for path in namespace_root.rglob("*") if path.is_file()]
        for path in candidates:
            try:
                modified_at = path.stat().st_mtime
                if modified_at >= cutoff and not (
                    rejects_future_timestamp and modified_at > reference_time
                ):
                    continue
            except OSError:
                continue

            with self.key_lock(path):
                try:
                    if (
                        namespace == ArtifactNamespace.SESSION_ARTIFACT
                        and self._has_active_session_lease(path, cutoff)
                    ):
                        continue
                    modified_at = path.stat().st_mtime
                    if modified_at >= cutoff and not (
                        rejects_future_timestamp and modified_at > reference_time
                    ):
                        continue
                    path.unlink()
                    removed += 1
                except OSError:
                    continue

        self.prune_empty_directories(namespace_root)
        return removed

    def cleanup_stale_lock_files(self, cache_root, *, now: float | None = None) -> int:
        """Remove abandoned cross-process lock files after their stale horizon."""
        lock_root = Path(cache_root) / ".artifact-locks"
        if not lock_root.exists():
            return 0
        cutoff = (time.time() if now is None else float(now)) - self._stale_lock_seconds
        removed = 0
        for lock_path in lock_root.glob("*.lock"):
            try:
                if lock_path.stat().st_mtime >= cutoff:
                    continue
                lock_path.unlink()
                removed += 1
            except OSError:
                continue
        return removed

    @staticmethod
    def prune_empty_directories(root) -> None:
        """Remove empty namespace subdirectories from deepest to shallowest."""
        root = Path(root)
        if not root.exists():
            return
        directories = sorted(
            (path for path in root.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        )
        for directory in directories:
            try:
                directory.rmdir()
            except OSError:
                continue


ARTIFACT_STORE = ArtifactStore()


def read_parquet_artifact(path, **kwargs):
    """Read a Parquet artifact while holding a last-access lease."""
    import pandas as pd

    with ARTIFACT_STORE.lease(path) as leased_path:
        return pd.read_parquet(leased_path, **kwargs)


def write_parquet_artifact(frame, path, **kwargs) -> Path:
    """Write a DataFrame to Parquet through atomic artifact publication."""
    return ARTIFACT_STORE.write(
        path,
        lambda temporary_path: frame.to_parquet(temporary_path, **kwargs),
    )


def session_artifact_owner(session_state: MutableMapping) -> str:
    """Return a stable filesystem-safe owner token for one UI session."""
    owner = str(session_state.get(SESSION_ARTIFACT_OWNER_KEY, "")).strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,128}", owner):
        owner = uuid.uuid4().hex
        session_state[SESSION_ARTIFACT_OWNER_KEY] = owner
    return owner


def session_artifact_path(
    cache_root,
    session_state: MutableMapping,
    *,
    run_id,
    analysis_id,
) -> Path:
    """Return the deterministic Parquet path for one session analysis result."""
    owner = session_artifact_owner(session_state)
    run_token = _safe_path_token(run_id, "run")
    analysis_token = _safe_path_token(analysis_id, "analysis")
    return ARTIFACT_STORE.namespace_path(
        cache_root,
        ArtifactNamespace.SESSION_ARTIFACT,
        owner,
        f"run_{run_token}",
        f"spots_{analysis_token}.parquet",
    )


def register_session_artifact(session_state: MutableMapping, path) -> None:
    """Remember one artifact as referenced by the current UI session."""
    canonical_path = str(Path(path).resolve())
    paths = list(session_state.get(SESSION_ARTIFACT_PATHS_KEY, []))
    if canonical_path not in paths:
        paths.append(canonical_path)
    session_state[SESSION_ARTIFACT_PATHS_KEY] = paths
    ARTIFACT_STORE.touch_session_lease_unlocked(Path(path))


def touch_registered_session_artifacts(session_state: MutableMapping) -> int:
    """Refresh all current-session references before global TTL cleanup."""
    retained_paths = []
    for raw_path in list(session_state.get(SESSION_ARTIFACT_PATHS_KEY, [])):
        path = Path(raw_path)
        if ARTIFACT_STORE.touch(path):
            retained_paths.append(str(path.resolve()))
    session_state[SESSION_ARTIFACT_PATHS_KEY] = retained_paths
    return len(retained_paths)


def release_registered_session_artifacts(session_state: MutableMapping) -> int:
    """Release and remove artifacts no longer referenced by one UI session."""
    paths = list(session_state.pop(SESSION_ARTIFACT_PATHS_KEY, []))
    run_directories = {
        directory
        for path in paths
        if (directory := _session_run_directory(Path(path))) is not None
    }
    removed = sum(1 for path in paths if ARTIFACT_STORE.delete(path))
    for run_directory in run_directories:
        try:
            (run_directory / SESSION_ARTIFACT_LEASE_FILENAME).unlink()
        except OSError:
            pass
        ARTIFACT_STORE.prune_empty_directories(run_directory.parent)
    return removed


def retire_registered_session_artifacts(session_state: MutableMapping) -> int:
    """Stop tracking prior-run artifacts without deleting data visible to old fragments."""
    paths = list(session_state.pop(SESSION_ARTIFACT_PATHS_KEY, []))
    retained = 0
    for path in paths:
        if ARTIFACT_STORE.touch(path):
            retained += 1
    return retained


def cleanup_artifact_namespaces(
    cache_root,
    *,
    query_ttl_seconds: float | None = None,
    demo_query_ttl_seconds: float | None = None,
    session_ttl_seconds: float | None = None,
    ttl_seconds: float | None = None,
) -> dict[str, int]:
    """Clean each TTL-managed namespace according to its own lifecycle.

    ``ttl_seconds`` is retained as an internal compatibility fallback for
    callers that have not yet separated the three policies.
    """
    query_ttl_seconds = (
        ttl_seconds if query_ttl_seconds is None else query_ttl_seconds
    )
    demo_query_ttl_seconds = (
        ttl_seconds if demo_query_ttl_seconds is None else demo_query_ttl_seconds
    )
    session_ttl_seconds = (
        ttl_seconds if session_ttl_seconds is None else session_ttl_seconds
    )
    if None in (
        query_ttl_seconds,
        demo_query_ttl_seconds,
        session_ttl_seconds,
    ):
        raise TypeError(
            "query, demo-query, and session TTL values must all be provided"
        )

    removed = {
        ArtifactNamespace.QUERY.value: ARTIFACT_STORE.cleanup_namespace(
            cache_root,
            ArtifactNamespace.QUERY,
            ttl_seconds=query_ttl_seconds,
        ),
        ArtifactNamespace.DEMO_QUERY.value: ARTIFACT_STORE.cleanup_namespace(
            cache_root,
            ArtifactNamespace.DEMO_QUERY,
            ttl_seconds=demo_query_ttl_seconds,
        ),
        ArtifactNamespace.SESSION_ARTIFACT.value: ARTIFACT_STORE.cleanup_namespace(
            cache_root,
            ArtifactNamespace.SESSION_ARTIFACT,
            ttl_seconds=session_ttl_seconds,
        ),
    }
    ARTIFACT_STORE.cleanup_stale_lock_files(cache_root)
    return removed
