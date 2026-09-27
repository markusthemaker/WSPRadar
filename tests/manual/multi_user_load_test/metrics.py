"""External process and cache measurements for the optional multi-user harness.

The caller samples every five seconds; this module never starts, stops, or sleeps
for a process. RSS is resident memory, Windows private bytes are committed private
memory (including paged-out memory), and USS is resident uniquely owned memory
when the OS permits that measurement. Summed RSS may count shared pages more than
once. CPU percentage uses one fully occupied logical core as 100%, so a process
tree can exceed 100%. Short-lived processes between samples can be missed.

psutil is an optional *harness* dependency, loaded only when constructing a real
sampler. Tests inject a fake process API. No command lines or environments are
collected. PID/create-time pairs prevent measuring an unrelated reused PID.
"""

from __future__ import annotations

from datetime import datetime, timezone
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import sys
import time
from typing import Iterable


DEFAULT_SAMPLE_INTERVAL_SECONDS = 5.0
_PROCESS_FIELDS = (
    "rss_bytes", "private_bytes", "uss_bytes", "cpu_seconds", "thread_count",
)
_CGROUP_EVENTS = ("low", "high", "max", "oom", "oom_kill", "oom_group_kill")


def _diagnostic(diagnostics: list[str], operation: str, exception: Exception) -> None:
    # Error text can contain paths or other unrelated process details.
    diagnostics.append(f"{operation}: {type(exception).__name__}")


def _cache_measurements(cache_path: Path | None, excluded_paths: tuple[Path, ...], diagnostics: list[str]) -> dict:
    measurements = {"cache_artifact_bytes": None, "cache_artifact_files": None, "disk_free_bytes": None}
    if cache_path is None:
        return measurements
    try:
        disk_path = cache_path
        while not disk_path.exists() and disk_path.parent != disk_path:
            disk_path = disk_path.parent
        measurements["disk_free_bytes"] = shutil.disk_usage(disk_path).free
    except OSError as exception:
        _diagnostic(diagnostics, "disk_free", exception)
    artifact_bytes = artifact_files = 0
    pending_directories = [cache_path]
    try:
        if not cache_path.exists():
            measurements.update(cache_artifact_bytes=0, cache_artifact_files=0)
            return measurements
        while pending_directories:
            directory_path = pending_directories.pop()
            if any(directory_path == excluded or excluded in directory_path.parents for excluded in excluded_paths):
                continue
            with os.scandir(directory_path) as entries:
                for entry in entries:
                    entry_path = Path(entry.path)
                    if entry_path in excluded_paths or entry.is_symlink():
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        pending_directories.append(entry_path)
                    elif entry.is_file(follow_symlinks=False):
                        artifact_bytes += entry.stat(follow_symlinks=False).st_size
                        artifact_files += 1
        measurements.update(cache_artifact_bytes=artifact_bytes, cache_artifact_files=artifact_files)
    except OSError as exception:
        # A racing publication/deletion is an incomplete sample, not zero bytes.
        _diagnostic(diagnostics, "cache_scan", exception)
    return measurements


def _cgroup_measurements(server_pid: int, diagnostics: list[str], *, proc_root: Path, cgroup_root: Path) -> dict:
    measurements = {
        "cgroup_version": None,
        "cgroup_memory_current_bytes": None,
        "cgroup_memory_max_bytes": None,
        "cgroup_memory_max_unlimited": None,
        **{f"cgroup_memory_events_{event}": None for event in _CGROUP_EVENTS},
    }
    try:
        membership_lines = (proc_root / str(server_pid) / "cgroup").read_text(encoding="utf-8").splitlines()
        membership = next((line.split(":", 2)[2] for line in membership_lines if line.startswith("0::")), None)
        if membership is None:
            diagnostics.append("cgroup: unified cgroup v2 unavailable")
            return measurements
        measurements["cgroup_version"] = 2
        relative_membership = membership.lstrip("/")
        # Account for a mounted subtree, as used by container cgroup namespaces.
        mountinfo_path = proc_root / str(server_pid) / "mountinfo"
        if mountinfo_path.exists():
            for mount_line in mountinfo_path.read_text(encoding="utf-8").splitlines():
                if " - cgroup2 " not in mount_line:
                    continue
                mount_fields = mount_line.split(" - ", 1)[0].split()
                mount_root = PurePosixPath(mount_fields[3].replace("\\040", " "))
                mount_path = Path(mount_fields[4].replace("\\040", " "))
                try:
                    relative_membership = str(PurePosixPath(membership).relative_to(mount_root))
                except ValueError:
                    continue
                if cgroup_root == Path("/sys/fs/cgroup"):
                    cgroup_root = mount_path
                break
        memory_directory = cgroup_root / relative_membership
    except (OSError, ValueError, IndexError) as exception:
        _diagnostic(diagnostics, "cgroup_discovery", exception)
        return measurements
    for filename, field_name in (
        ("memory.current", "cgroup_memory_current_bytes"),
        ("memory.max", "cgroup_memory_max_bytes"),
    ):
        try:
            recorded_text = (memory_directory / filename).read_text(encoding="ascii").strip()
            if filename == "memory.max":
                measurements["cgroup_memory_max_unlimited"] = recorded_text == "max"
            if filename != "memory.max" or recorded_text != "max":
                recorded_bytes = int(recorded_text)
                if recorded_bytes < 0:
                    raise ValueError("negative cgroup byte count")
                measurements[field_name] = recorded_bytes
        except (OSError, ValueError) as exception:
            _diagnostic(diagnostics, f"cgroup_{filename}", exception)
    try:
        recorded_events = dict(line.split() for line in (memory_directory / "memory.events").read_text(encoding="ascii").splitlines())
        for event in _CGROUP_EVENTS:
            if event in recorded_events:
                measurements[f"cgroup_memory_events_{event}"] = int(recorded_events[event])
    except (OSError, ValueError) as exception:
        _diagnostic(diagnostics, "cgroup_memory.events", exception)
    return measurements


class ProcessMetricsSampler:
    """Sample exact server and generator process trees without changing either.

    Supply the harness PID as a generator root when it launches the browser.
    Overlapping roots are deduplicated and the server tree is excluded from the
    generator tree. Previously observed descendants remain tracked after they
    become orphans. Use ``cache_exclude_paths`` if a report is inside the cache.
    Missing/inaccessible measurements are None plus JSON diagnostics. An ordinary
    descendant verified to have exited during measurement is omitted as one whole
    row; loss of a supplied root invalidates group totals. Measurements are live
    process observations, not an atomic snapshot. Host available RAM and cgroup
    usage are separate scopes.
    """

    def __init__(
        self,
        server_pid: int,
        generator_root_pids: Iterable[int] = (),
        cache_path: str | Path | None = None,
        *,
        cache_exclude_paths: Iterable[str | Path] = (),
        process_api=None,
        monotonic_clock=time.monotonic,
        utc_now=lambda: datetime.now(timezone.utc),
        platform_name: str = sys.platform,
        proc_root: str | Path = "/proc",
        cgroup_root: str | Path = "/sys/fs/cgroup",
    ):
        if isinstance(server_pid, bool) or not isinstance(server_pid, int) or server_pid <= 0:
            raise ValueError("server_pid must be a positive integer")
        if process_api is None:
            try:
                process_api = importlib.import_module("psutil")
            except ImportError as exception:
                raise RuntimeError("Install tests/manual/multi_user_load_test/requirements.txt to provide psutil.") from exception
        self._process_api = process_api
        self._monotonic_clock = monotonic_clock
        self._utc_now = utc_now
        self._platform_name = platform_name
        self._started_monotonic = monotonic_clock()
        self._previous_monotonic = None
        self._previous_wall_seconds = None
        self._previous_cpu = {"server": {}, "generator": {}}
        self._server_pid = server_pid
        self._cache_path = Path(cache_path).resolve() if cache_path is not None else None
        self._cache_excluded_paths = tuple(Path(path).resolve() for path in cache_exclude_paths)
        self._proc_root = Path(proc_root)
        self._cgroup_root = Path(cgroup_root)
        self._initial_diagnostics: list[str] = []
        self._known_processes = {"server": {}, "generator": {}}
        self._root_identities = {"server": set(), "generator": set()}
        self._unbound_roots = {"server": set(), "generator": set()}
        self._bind_root(server_pid, "server", self._initial_diagnostics)
        self.set_generator_root_pids(generator_root_pids)

    def _bind_root(self, process_id: int, group: str, diagnostics: list[str]) -> None:
        if isinstance(process_id, bool) or not isinstance(process_id, int) or process_id <= 0:
            raise ValueError("generator root PIDs must be positive integers")
        try:
            process = self._process_api.Process(process_id)
            created_at = float(process.create_time())
            self._known_processes[group][process_id] = created_at
            self._root_identities[group].add((process_id, created_at))
        except self._process_api.NoSuchProcess as exception:
            self._unbound_roots[group].add(process_id)
            _diagnostic(diagnostics, f"{group}.root.{process_id}", exception)
        except self._process_api.Error as exception:
            self._unbound_roots[group].add(process_id)
            _diagnostic(diagnostics, f"{group}.root.{process_id}", exception)

    def set_generator_root_pids(self, process_ids: Iterable[int]) -> None:
        """Add explicitly supplied roots; keep observed descendants for teardown."""
        for process_id in process_ids:
            if process_id not in self._known_processes["generator"]:
                self._bind_root(process_id, "generator", self._initial_diagnostics)

    def process_identities(self, group: str = "server") -> tuple[tuple[int, float], ...]:
        """Return observed PID/create-time pairs for independently verified cleanup.

        The caller must revalidate these identities before signaling anything.
        Read after stopping the sampler to avoid concurrent tree updates.
        """
        if group not in self._known_processes:
            raise ValueError("process group must be server or generator")
        return tuple(self._known_processes[group].items())

    def _collect_processes(self, group: str, diagnostics: list[str]) -> tuple[dict, bool]:
        processes = {}
        is_complete = not self._unbound_roots[group]
        for process_id, created_at in tuple(self._known_processes[group].items()):
            try:
                process = self._process_api.Process(process_id)
                if float(process.create_time()) != created_at:
                    diagnostics.append(f"{group}.pid_reused.{process_id}")
                    del self._known_processes[group][process_id]
                    continue
                processes[(process_id, created_at)] = process
                for descendant in process.children(recursive=True):
                    try:
                        descendant_created_at = float(descendant.create_time())
                        self._known_processes[group][descendant.pid] = descendant_created_at
                        processes[(descendant.pid, descendant_created_at)] = descendant
                    except self._process_api.NoSuchProcess:
                        continue
                    except self._process_api.Error as exception:
                        is_complete = False
                        _diagnostic(diagnostics, f"{group}.discover.{descendant.pid}", exception)
            except self._process_api.NoSuchProcess:
                self._known_processes[group].pop(process_id, None)
                processes.pop((process_id, created_at), None)
            except self._process_api.Error as exception:
                is_complete = False
                _diagnostic(diagnostics, f"{group}.discover.{process_id}", exception)
        for process_id, created_at in self._root_identities[group] - processes.keys():
            is_complete = False
            diagnostics.append(f"{group}.root_unavailable.{process_id}")
        return processes, is_complete

    def _verify_process_has_exited(self, identity: tuple[int, float], diagnostics: list[str], group: str) -> bool:
        """Verify the exact process has gone, including replacement of its PID."""
        process_id, created_at = identity
        try:
            process = self._process_api.Process(process_id)
            return float(process.create_time()) != created_at
        except self._process_api.NoSuchProcess:
            return True
        except self._process_api.Error as exception:
            _diagnostic(diagnostics, f"{group}.{process_id}.verify_exit", exception)
            return False

    def _measure_group(self, group: str, processes: dict, is_complete: bool, elapsed_seconds: float | None, diagnostics: list[str]) -> dict:
        fields = {field: [] for field in _PROCESS_FIELDS}
        current_cpu = {}
        included_process_count = 0
        for identity, process in processes.items():
            measured = dict.fromkeys(_PROCESS_FIELDS)
            reported_missing = False
            try:
                memory = process.memory_info()
                measured["rss_bytes"] = int(memory.rss)
                measured["private_bytes"] = getattr(memory, "private", None)
            except self._process_api.NoSuchProcess as exception:
                reported_missing = True
                _diagnostic(diagnostics, f"{group}.{process.pid}.memory", exception)
            except self._process_api.Error as exception:
                _diagnostic(diagnostics, f"{group}.{process.pid}.memory", exception)
            try:
                measured["uss_bytes"] = getattr(process.memory_full_info(), "uss", None)
            except self._process_api.NoSuchProcess as exception:
                reported_missing = True
                _diagnostic(diagnostics, f"{group}.{process.pid}.uss", exception)
            except (self._process_api.Error, AttributeError, NotImplementedError) as exception:
                _diagnostic(diagnostics, f"{group}.{process.pid}.uss", exception)
            try:
                cpu_times = process.cpu_times()
                measured["cpu_seconds"] = float(cpu_times.user + cpu_times.system)
                measured["thread_count"] = int(process.num_threads())
            except self._process_api.NoSuchProcess as exception:
                reported_missing = True
                _diagnostic(diagnostics, f"{group}.{process.pid}.cpu_threads", exception)
            except self._process_api.Error as exception:
                _diagnostic(diagnostics, f"{group}.{process.pid}.cpu_threads", exception)
            if reported_missing:
                if identity not in self._root_identities[group] and self._verify_process_has_exited(identity, diagnostics, group):
                    # Do not mix earlier RSS reads from this dead process with
                    # missing USS/CPU reads. Omit its complete observation.
                    if self._known_processes[group].get(identity[0]) == identity[1]:
                        self._known_processes[group].pop(identity[0], None)
                    diagnostics.append(f"{group}.{process.pid}.exited_during_sample")
                    continue
                is_complete = False
                diagnostics.append(f"{group}.{process.pid}.missing_process_not_omitted")
            included_process_count += 1
            if measured["cpu_seconds"] is not None:
                current_cpu[identity] = measured["cpu_seconds"]
            for field in _PROCESS_FIELDS:
                fields[field].append(measured[field])
        measurements = {
            f"{group}_process_count": included_process_count,
            f"{group}_discovery_complete": is_complete,
        }
        for field, recorded_values in fields.items():
            measurements[f"{group}_{field}"] = (
                sum(recorded_values) if is_complete and all(recorded is not None for recorded in recorded_values) else None
            )
        if self._platform_name != "win32":
            measurements[f"{group}_private_bytes"] = None
        cpu_percent = None
        if elapsed_seconds is not None and elapsed_seconds > 0 and is_complete and len(current_cpu) == included_process_count:
            cpu_delta = 0.0
            has_cpu_baseline = True
            for identity, cpu_seconds in current_cpu.items():
                previous_cpu = self._previous_cpu[group].get(identity)
                if previous_cpu is None:
                    if identity[1] >= self._previous_wall_seconds:
                        previous_cpu = 0.0
                    else:
                        has_cpu_baseline = False
                        break
                cpu_delta += max(0.0, cpu_seconds - previous_cpu)
            if has_cpu_baseline:
                cpu_percent = cpu_delta / elapsed_seconds * 100.0
        measurements[f"{group}_cpu_percent_one_core"] = cpu_percent
        self._previous_cpu[group] = current_cpu
        return measurements

    def sample(self, phase: str, active_users: int) -> dict:
        """Return one flat CSV-serializable sample; None means unavailable."""
        if isinstance(active_users, bool) or not isinstance(active_users, int) or active_users < 0:
            raise ValueError("active_users must be a nonnegative integer")
        sampled_monotonic = self._monotonic_clock()
        sampled_utc = self._utc_now().astimezone(timezone.utc)
        elapsed_seconds = None if self._previous_monotonic is None else sampled_monotonic - self._previous_monotonic
        diagnostics = list(self._initial_diagnostics)
        measurements = {
            "timestamp_utc": sampled_utc.isoformat().replace("+00:00", "Z"),
            "elapsed_seconds": sampled_monotonic - self._started_monotonic,
            "phase": str(phase),
            "active_users": active_users,
        }
        server_processes, server_complete = self._collect_processes("server", diagnostics)
        generator_processes, generator_complete = self._collect_processes("generator", diagnostics)
        generator_processes = {
            identity: process for identity, process in generator_processes.items()
            if identity not in server_processes and identity[0] != self._server_pid
            and self._known_processes["server"].get(identity[0]) != identity[1]
        }
        generator_complete = generator_complete and server_complete
        measurements.update(self._measure_group("server", server_processes, server_complete, elapsed_seconds, diagnostics))
        measurements.update(self._measure_group("generator", generator_processes, generator_complete, elapsed_seconds, diagnostics))
        measurements.update(system_total_ram_bytes=None, system_available_ram_bytes=None, system_memory_percent=None)
        try:
            memory = self._process_api.virtual_memory()
            measurements.update(system_total_ram_bytes=memory.total, system_available_ram_bytes=memory.available, system_memory_percent=memory.percent)
        except (OSError, self._process_api.Error) as exception:
            _diagnostic(diagnostics, "system_memory", exception)
        measurements.update(_cache_measurements(self._cache_path, self._cache_excluded_paths, diagnostics))
        if self._platform_name.startswith("linux"):
            measurements.update(_cgroup_measurements(self._server_pid, diagnostics, proc_root=self._proc_root, cgroup_root=self._cgroup_root))
        else:
            measurements.update(cgroup_version=None, cgroup_memory_current_bytes=None, cgroup_memory_max_bytes=None, cgroup_memory_max_unlimited=None)
            measurements.update({f"cgroup_memory_events_{event}": None for event in _CGROUP_EVENTS})
        measurements["diagnostics"] = json.dumps(sorted(set(diagnostics)), separators=(",", ":"))
        self._previous_monotonic = sampled_monotonic
        self._previous_wall_seconds = sampled_utc.timestamp()
        return measurements

    def system_metadata(self) -> dict:
        """Return non-secret platform and metric interpretation metadata."""
        diagnostics: list[str] = []
        logical_cpus = physical_cpus = None
        try:
            logical_cpus = self._process_api.cpu_count(logical=True)
            physical_cpus = self._process_api.cpu_count(logical=False)
        except (OSError, self._process_api.Error) as exception:
            _diagnostic(diagnostics, "cpu_count", exception)
        return {
            "platform": self._platform_name,
            "os_release": platform.release(),
            "python_version": platform.python_version(),
            "psutil_version": getattr(self._process_api, "__version__", "unknown"),
            "server_pid": self._server_pid,
            "logical_cpu_count": logical_cpus,
            "physical_cpu_count": physical_cpus,
            "recommended_sample_interval_seconds": DEFAULT_SAMPLE_INTERVAL_SECONDS,
            "cpu_percent_basis": "100 percent equals one logical core; sampled live-process deltas can miss exited processes",
            "rss_scope": "sum of process working sets; shared pages may be counted more than once",
            "process_churn": "verified exited descendants are omitted as whole rows; root loss or inaccessible live-process fields remain unavailable",
            "private_scope": "Windows private committed bytes; null on other platforms",
            "uss_scope": "resident uniquely owned bytes when accessible",
            "cgroup_scope": "server cgroup including other processes and charged file cache; memory.events are cumulative",
            "cache_scope": "logical file sizes in supplied cache directory, excluding symlinks and configured exclusions",
            "diagnostics": diagnostics,
        }


def summarize_samples(samples: Iterable[dict]) -> dict:
    """Summarize sampled high-water marks, never claiming a continuous peak.

    A null metric remains null if every measurement was unavailable. The change
    between first and final samples describes those two endpoints only; it is
    neither a leak diagnosis nor an estimate of bytes per concurrent user.
    """
    recorded_samples = list(samples)
    peak_fields = (
        "server_rss_bytes", "server_private_bytes", "server_uss_bytes",
        "generator_rss_bytes", "generator_private_bytes", "generator_uss_bytes",
        "cgroup_memory_current_bytes", "cache_artifact_bytes",
    )
    sampled_peaks = {
        field: max((sample[field] for sample in recorded_samples if sample.get(field) is not None), default=None)
        for field in peak_fields
    }
    phases = {}
    for sample in recorded_samples:
        phase = str(sample.get("phase", "unknown"))
        phase_summary = phases.setdefault(phase, {"sample_count": 0, "maximum_active_users": 0})
        phase_summary["sample_count"] += 1
        phase_summary["maximum_active_users"] = max(phase_summary["maximum_active_users"], sample.get("active_users", 0))
    first_sample = recorded_samples[0] if recorded_samples else {}
    final_sample = recorded_samples[-1] if recorded_samples else {}
    endpoint_changes = {
        field: final_sample[field] - first_sample[field]
        if first_sample.get(field) is not None and final_sample.get(field) is not None else None
        for field in peak_fields
    }
    available_ram = [sample["system_available_ram_bytes"] for sample in recorded_samples if sample.get("system_available_ram_bytes") is not None]
    return {
        "sample_count": len(recorded_samples),
        "sampled_duration_seconds": final_sample.get("elapsed_seconds", 0) - first_sample.get("elapsed_seconds", 0),
        "sampled_peaks_bytes": sampled_peaks,
        "final_minus_first_bytes": endpoint_changes,
        "minimum_system_available_ram_bytes": min(available_ram, default=None),
        "phases": phases,
        "samples_with_diagnostics": sum(sample.get("diagnostics", "[]") != "[]" for sample in recorded_samples),
        "interpretation": "Peaks are sampled; brief spikes and processes that exit between samples may be missed. Endpoint growth alone does not establish a leak.",
    }
