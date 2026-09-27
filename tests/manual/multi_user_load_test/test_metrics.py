"""Fast unit tests with fake process trees; these do not launch a load test."""

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

try:
    from .metrics import ProcessMetricsSampler, summarize_samples
except ImportError:
    from metrics import ProcessMetricsSampler, summarize_samples


class FakeProcessError(Exception):
    pass


class FakeNoSuchProcess(FakeProcessError):
    pass


class FakeAccessDenied(FakeProcessError):
    pass


class FakeProcess:
    def __init__(self, process_id, *, rss=100, private=80, uss=60, cpu=1.0, created_at=1000.0):
        self.pid = process_id
        self.created_at = created_at
        self.rss = rss
        self.private = private
        self.uss = uss
        self.cpu = cpu
        self.descendants = []
        self.deny_uss = False
        self.deny_creation = False
        self.deny_children = False
        self.deny_memory = False
        self.exit_on_read = None
        self.report_missing_but_alive = None
        self.is_dead = False

    def create_time(self):
        if self.deny_creation:
            raise FakeAccessDenied("sensitive error text must not be included")
        if self.is_dead:
            raise FakeNoSuchProcess()
        return self.created_at

    def children(self, recursive=True):
        if self.deny_children:
            raise FakeAccessDenied()
        return self.descendants

    def memory_info(self):
        self._before_read("memory")
        if self.deny_memory:
            raise FakeAccessDenied()
        return SimpleNamespace(rss=self.rss, private=self.private)

    def memory_full_info(self):
        self._before_read("uss")
        if self.deny_uss:
            raise FakeAccessDenied("sensitive error text must not be included")
        return SimpleNamespace(uss=self.uss)

    def cpu_times(self):
        self._before_read("cpu")
        return SimpleNamespace(user=self.cpu, system=0.0)

    def num_threads(self):
        self._before_read("threads")
        return 3

    def _before_read(self, field):
        if self.exit_on_read == field:
            self.is_dead = True
        if self.is_dead or self.report_missing_but_alive == field:
            raise FakeNoSuchProcess()


class FakeProcessAPI:
    Error = FakeProcessError
    NoSuchProcess = FakeNoSuchProcess
    __version__ = "fake"

    def __init__(self, *processes):
        self.processes = {process.pid: process for process in processes}

    def Process(self, process_id):
        if process_id not in self.processes:
            raise FakeNoSuchProcess()
        return self.processes[process_id]

    def virtual_memory(self):
        return SimpleNamespace(total=8000, available=2000, percent=75.0)

    def cpu_count(self, logical=True):
        return 4 if logical else 2


class Clock:
    def __init__(self):
        self.seconds = 0.0

    def monotonic(self):
        return self.seconds

    def utc_now(self):
        return datetime.fromtimestamp(2000.0 + self.seconds, tz=timezone.utc)


class ProcessMetricsTests(unittest.TestCase):
    def setUp(self):
        self.server = FakeProcess(10)
        self.child = FakeProcess(11, rss=40, private=30, uss=20)
        self.generator = FakeProcess(20, rss=300, private=200, uss=150)
        self.browser = FakeProcess(21, rss=500, private=400, uss=350)
        self.server.descendants = [self.child]
        self.generator.descendants = [self.server, self.child, self.browser]
        self.api = FakeProcessAPI(self.server, self.child, self.generator, self.browser)
        self.clock = Clock()

    def sampler(self, **keywords):
        return ProcessMetricsSampler(10, [20, 21], process_api=self.api, monotonic_clock=self.clock.monotonic, utc_now=self.clock.utc_now, platform_name=keywords.pop("platform_name", "win32"), **keywords)

    def test_overlapping_roots_do_not_duplicate_server_or_browser(self):
        sampled = self.sampler().sample("idle", 10)
        self.assertEqual(sampled["server_process_count"], 2)
        self.assertEqual(sampled["server_rss_bytes"], 140)
        self.assertEqual(sampled["generator_process_count"], 2)
        self.assertEqual(sampled["generator_rss_bytes"], 800)
        self.assertEqual(sampled["generator_private_bytes"], 600)
        self.assertIsNone(sampled["server_cpu_percent_one_core"])
        self.assertEqual(sampled["system_available_ram_bytes"], 2000)
        self.assertTrue(sampled["timestamp_utc"].endswith("Z"))
        self.assertTrue(all(isinstance(recorded, (str, int, float, bool, type(None))) for recorded in sampled.values()))

    def test_cpu_one_core_basis_can_exceed_one_hundred_percent(self):
        sampler = self.sampler()
        sampler.sample("baseline", 0)
        self.clock.seconds = 5.0
        self.server.cpu += 6.0
        self.child.cpu += 4.0
        sampled = sampler.sample("run", 10)
        self.assertEqual(sampled["server_cpu_percent_one_core"], 200.0)
        self.assertEqual(sampled["elapsed_seconds"], 5.0)

    def test_permission_failure_is_null_not_partial_or_sensitive_error(self):
        self.child.deny_uss = True
        sampled = self.sampler().sample("run", 1)
        self.assertIsNone(sampled["server_uss_bytes"])
        self.assertEqual(sampled["server_rss_bytes"], 140)
        self.assertIn("FakeAccessDenied", sampled["diagnostics"])
        self.assertNotIn("sensitive", sampled["diagnostics"])

    def test_unreadable_root_never_reports_zero_memory(self):
        self.server.deny_creation = True
        sampled = self.sampler().sample("run", 1)
        self.assertIsNone(sampled["server_rss_bytes"])
        self.assertFalse(sampled["server_discovery_complete"])
        self.assertIsNone(sampled["generator_rss_bytes"])

    def test_pid_reuse_does_not_measure_unrelated_replacement(self):
        sampler = self.sampler()
        sampler.sample("run", 1)
        self.api.processes[10] = FakeProcess(10, rss=9000, created_at=3000.0)
        self.generator.descendants = [self.browser]
        sampled = sampler.sample("after", 0)
        self.assertIsNone(sampled["server_rss_bytes"])
        self.assertFalse(sampled["server_discovery_complete"])
        self.assertEqual(sampled["server_process_count"], 1)
        self.assertIn("server.pid_reused.10", sampled["diagnostics"])

    def test_orphan_descendant_stays_attributed_to_original_group(self):
        sampler = self.sampler()
        sampler.sample("run", 1)
        del self.api.processes[10]
        self.generator.descendants = [self.browser]
        sampled = sampler.sample("cleanup", 0)
        self.assertIsNone(sampled["server_rss_bytes"])
        self.assertEqual(sampled["server_process_count"], 1)
        self.assertIn((11, 1000.0), sampler.process_identities("server"))
        del self.api.processes[11]
        sampled = sampler.sample("stopped", 0)
        self.assertIsNone(sampled["server_rss_bytes"])
        self.assertEqual(sampled["server_process_count"], 0)

    def test_descendant_exiting_mid_sample_is_omitted_as_one_whole_row(self):
        renderer = FakeProcess(23, rss=4000, private=3500, uss=3000)
        renderer.exit_on_read = "uss"
        self.browser.descendants = [renderer]
        self.api.processes[23] = renderer
        sampled = self.sampler().sample("run", 2)
        self.assertEqual(sampled["generator_rss_bytes"], 800)
        self.assertEqual(sampled["generator_private_bytes"], 600)
        self.assertEqual(sampled["generator_uss_bytes"], 500)
        self.assertEqual(sampled["generator_process_count"], 2)
        self.assertTrue(sampled["generator_discovery_complete"])
        self.assertIn("generator.23.exited_during_sample", sampled["diagnostics"])

    def test_missing_descendant_that_is_still_live_cannot_be_omitted(self):
        renderer = FakeProcess(23, rss=4000)
        renderer.report_missing_but_alive = "uss"
        self.browser.descendants = [renderer]
        self.api.processes[23] = renderer
        sampled = self.sampler().sample("run", 2)
        self.assertIsNone(sampled["generator_rss_bytes"])
        self.assertEqual(sampled["generator_process_count"], 3)
        self.assertFalse(sampled["generator_discovery_complete"])
        self.assertNotIn("exited_during_sample", sampled["diagnostics"])

    def test_inaccessible_live_descendant_does_not_produce_partial_sum(self):
        renderer = FakeProcess(23, rss=4000)
        renderer.deny_memory = True
        self.browser.descendants = [renderer]
        self.api.processes[23] = renderer
        sampled = self.sampler().sample("run", 2)
        self.assertIsNone(sampled["generator_rss_bytes"])
        self.assertEqual(sampled["generator_process_count"], 3)
        self.assertNotIn("exited_during_sample", sampled["diagnostics"])

    def test_supplied_root_exiting_mid_sample_invalidates_group(self):
        self.generator.exit_on_read = "uss"
        sampled = self.sampler().sample("run", 2)
        self.assertIsNone(sampled["generator_rss_bytes"])
        self.assertFalse(sampled["generator_discovery_complete"])
        self.assertIn("generator.20.missing_process_not_omitted", sampled["diagnostics"])

    def test_disappearing_child_does_not_lose_server_identity(self):
        self.child.is_dead = True
        sampler = self.sampler()
        sampler.sample("run", 1)
        self.server.descendants = []
        self.generator.descendants = [self.browser]
        sampled = sampler.sample("run", 1)
        self.assertEqual(sampled["server_rss_bytes"], 100)

    def test_cache_excludes_nested_report_recursion(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            cache = Path(temporary_directory) / "cache"
            report = cache / "report"
            report.mkdir(parents=True)
            (cache / "evidence.parquet").write_bytes(b"12345")
            (report / "samples.csv").write_bytes(b"not an artifact")
            sampled = self.sampler(cache_path=cache, cache_exclude_paths=[report]).sample("run", 1)
            self.assertEqual(sampled["cache_artifact_bytes"], 5)
            self.assertEqual(sampled["cache_artifact_files"], 1)
            self.assertGreater(sampled["disk_free_bytes"], 0)

    def test_cgroup_v2_unlimited_and_event_counts(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            proc_root = Path(temporary_directory) / "proc"
            (proc_root / "10").mkdir(parents=True)
            (proc_root / "10" / "cgroup").write_text("0::/job\n", encoding="utf-8")
            cgroup_root = Path(temporary_directory) / "cgroup"
            (cgroup_root / "job").mkdir(parents=True)
            (cgroup_root / "job" / "memory.current").write_text("1234\n", encoding="ascii")
            (cgroup_root / "job" / "memory.max").write_text("max\n", encoding="ascii")
            (cgroup_root / "job" / "memory.events").write_text("low 0\nhigh 4\nmax 2\noom 1\noom_kill 1\n", encoding="ascii")
            sampled = self.sampler(platform_name="linux", proc_root=proc_root, cgroup_root=cgroup_root).sample("run", 1)
            self.assertEqual(sampled["cgroup_memory_current_bytes"], 1234)
            self.assertIsNone(sampled["cgroup_memory_max_bytes"])
            self.assertTrue(sampled["cgroup_memory_max_unlimited"])
            self.assertEqual(sampled["cgroup_memory_events_oom_kill"], 1)
            self.assertIsNone(sampled["server_private_bytes"])
            self.assertEqual(json.loads(sampled["diagnostics"]), [])

    def test_missing_cgroup_files_are_not_reported_as_zero(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            sampled = self.sampler(platform_name="linux", proc_root=temporary_directory).sample("run", 1)
            self.assertIsNone(sampled["cgroup_memory_current_bytes"])
            self.assertIn("cgroup_discovery", sampled["diagnostics"])

    def test_summary_preserves_missing_metrics_and_sampled_peak(self):
        sampler = self.sampler()
        first = sampler.sample("baseline", 0)
        self.server.rss = 300
        self.clock.seconds = 5
        middle = sampler.sample("run", 10)
        self.server.rss = 120
        self.clock.seconds = 10
        final = sampler.sample("cleanup", 0)
        summary = summarize_samples([first, middle, final])
        self.assertEqual(summary["sampled_peaks_bytes"]["server_rss_bytes"], 340)
        self.assertEqual(summary["final_minus_first_bytes"]["server_rss_bytes"], 20)
        self.assertIsNone(summary["sampled_peaks_bytes"]["cgroup_memory_current_bytes"])
        self.assertEqual(summary["sampled_duration_seconds"], 10)
        self.assertEqual(summary["phases"]["run"]["maximum_active_users"], 10)
        self.assertEqual(summarize_samples([])["sample_count"], 0)


if __name__ == "__main__":
    unittest.main()
