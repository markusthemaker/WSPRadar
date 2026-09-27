"""Lifecycle checks use fake processes and never launch the application."""

import asyncio
import io
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

try:
    from . import run
except ImportError:
    import run


class FakeProcessError(Exception):
    pass


class FakeNoSuchProcess(FakeProcessError):
    pass


class FakeProcess:
    def __init__(self, process_id, created_at=1.0, *, ignores_terminate=False, ignores_kill=False):
        self.pid = process_id
        self.created_at = created_at
        self.descendants = []
        self.alive = True
        self.ignores_terminate = ignores_terminate
        self.ignores_kill = ignores_kill
        self.terminated = False
        self.killed = False

    def create_time(self):
        if not self.alive:
            raise FakeNoSuchProcess()
        return self.created_at

    def children(self, recursive=True):
        return self.descendants

    def terminate(self):
        self.terminated = True
        if not self.ignores_terminate:
            self.alive = False

    def kill(self):
        self.killed = True
        if not self.ignores_kill:
            self.alive = False


class FakePopen:
    def __init__(self, owned_process):
        self.owned_process = owned_process
        self.pid = owned_process.pid

    def poll(self):
        return None if self.owned_process.alive else 0

    def wait(self, timeout=None):
        if self.owned_process.alive:
            raise subprocess.TimeoutExpired("fake-owned-process", timeout)
        return 0

    def terminate(self):
        self.owned_process.terminate()

    def kill(self):
        self.owned_process.kill()


class FakeProcessAPI:
    Error = FakeProcessError
    NoSuchProcess = FakeNoSuchProcess

    def __init__(self, *processes):
        self.processes = {process.pid: process for process in processes}
        self.wait_calls = []

    def Process(self, process_id):
        candidate = self.processes.get(process_id)
        if candidate is None or not candidate.alive:
            raise FakeNoSuchProcess()
        return candidate

    def wait_procs(self, processes, timeout):
        self.wait_calls.append(timeout)
        return ([process for process in processes if not process.alive],
                [process for process in processes if process.alive])


class ProcessLifecycleTests(unittest.TestCase):
    def test_reused_root_pid_is_not_signaled_and_orphan_is_stopped(self):
        original_root = FakeProcess(10)
        original_root.alive = False
        unrelated_replacement = FakeProcess(10, created_at=2.0)
        orphan = FakeProcess(11)
        api = FakeProcessAPI(unrelated_replacement, orphan)
        with patch.dict(sys.modules, {"psutil": api}):
            cleanup = run.terminate_owned_process(FakePopen(original_root), (10, 1.0), ((11, 1.0),))
        self.assertFalse(unrelated_replacement.terminated)
        self.assertFalse(unrelated_replacement.killed)
        self.assertTrue(orphan.terminated)
        self.assertEqual(cleanup["skipped_reused_pids"], [10])

    def test_child_and_root_are_confirmed_after_forced_termination(self):
        root = FakeProcess(10, ignores_terminate=True)
        child = FakeProcess(11, ignores_terminate=True)
        root.descendants = [child]
        api = FakeProcessAPI(root, child)
        with patch.dict(sys.modules, {"psutil": api}):
            run.terminate_owned_process(FakePopen(root), (10, 1.0))
        self.assertTrue(root.killed)
        self.assertTrue(child.killed)
        self.assertEqual(api.wait_calls, [10, 5])

    def test_survivor_is_reported_as_cleanup_failure(self):
        root = FakeProcess(10)
        child = FakeProcess(11, ignores_terminate=True, ignores_kill=True)
        root.descendants = [child]
        api = FakeProcessAPI(root, child)
        with patch.dict(sys.modules, {"psutil": api}):
            with self.assertRaisesRegex(RuntimeError, "11"):
                run.terminate_owned_process(FakePopen(root), (10, 1.0))

    def test_failed_identity_capture_still_stops_exact_popen_child(self):
        root = FakeProcess(10)
        api = FakeProcessAPI(root)
        with patch.dict(sys.modules, {"psutil": api}):
            with self.assertRaisesRegex(RuntimeError, "identity was unavailable"):
                run.terminate_owned_process(FakePopen(root), None)
        self.assertTrue(root.terminated)

    def test_preparation_timeout_stops_launcher_and_observed_child(self):
        root = FakeProcess(10)
        child = FakeProcess(11)
        root.descendants = [child]
        api = FakeProcessAPI(root, child)
        command = ["python", "replay.py", "--prepare", "output"]
        with patch.dict(sys.modules, {"psutil": api}):
            with patch.object(run.subprocess, "Popen", return_value=FakePopen(root)) as launch:
                with patch.object(run.time, "monotonic", side_effect=[0.0, 0.0, 2.0]):
                    with self.assertRaises(subprocess.TimeoutExpired):
                        run.run_owned_preparation(command, cwd=Path("."), timeout_seconds=1)
        launch.assert_called_once_with(command, cwd=Path("."))
        self.assertTrue(root.terminated)
        self.assertTrue(child.terminated)

    def test_preparation_interrupt_still_stops_owned_tree(self):
        root = FakeProcess(10)
        child = FakeProcess(11)
        root.descendants = [child]
        api = FakeProcessAPI(root, child)

        class InterruptedPopen(FakePopen):
            def wait(self, timeout=None):
                if self.owned_process.alive:
                    raise KeyboardInterrupt()
                return 0

        with patch.dict(sys.modules, {"psutil": api}):
            with patch.object(run.subprocess, "Popen", return_value=InterruptedPopen(root)):
                with self.assertRaises(KeyboardInterrupt):
                    run.run_owned_preparation(["python", "replay.py"], cwd=Path("."))
        self.assertTrue(root.terminated)
        self.assertTrue(child.terminated)

    def test_successful_preparation_does_not_signal_reused_root_pid(self):
        root = FakeProcess(10)
        child = FakeProcess(11)
        unrelated_replacement = FakeProcess(10, created_at=2.0)
        root.descendants = [child]
        api = FakeProcessAPI(root, child)

        class SuccessfulPopen(FakePopen):
            def wait(self, timeout=None):
                self.owned_process.alive = False
                api.processes[10] = unrelated_replacement
                return 0

        with patch.dict(sys.modules, {"psutil": api}):
            with patch.object(run.subprocess, "Popen", return_value=SuccessfulPopen(root)):
                return_code = run.run_owned_preparation(["python", "replay.py"], cwd=Path("."))
        self.assertEqual(return_code, 0)
        self.assertFalse(unrelated_replacement.terminated)
        self.assertTrue(child.terminated)

    def test_failed_metrics_task_cannot_skip_server_cleanup(self):
        root = FakeProcess(10)
        api = FakeProcessAPI(root)
        sampler = SimpleNamespace(system_metadata=lambda: {}, process_identities=lambda group: ((10, 1.0),))
        metrics_module = SimpleNamespace(ProcessMetricsSampler=lambda *args: sampler)

        class BrokenBrowserContext:
            async def start(self):
                raise RuntimeError("browser setup failed")

            async def __aexit__(self, *arguments):
                return False

        async def exercise():
            with tempfile.TemporaryDirectory() as temporary_directory:
                (Path(temporary_directory) / "scenarios.json").write_text("{}", encoding="utf-8")
                options = SimpleNamespace(startup_timeout_seconds=1, baseline_seconds=0,
                                          browser_channel=None, sample_seconds=0.01)
                experiment = run.Experiment(options, Path(temporary_directory), [])
                experiment.monitor = AsyncMock(side_effect=RuntimeError("metrics failure"))
                with patch.dict(sys.modules, {"psutil": api, "metrics": metrics_module}):
                    with patch.object(run.subprocess, "Popen", return_value=FakePopen(root)):
                        with patch.object(run, "wait_for_server", new=AsyncMock()):
                            with patch("playwright.async_api.async_playwright", return_value=BrokenBrowserContext()):
                                with self.assertRaisesRegex(RuntimeError, "browser setup failed"):
                                    await experiment.execute()
                self.assertTrue(root.terminated)
                self.assertTrue(any(event["action"] == "server_cleanup" for event in experiment.actions))
                self.assertTrue(any(event["action"] == "monitor_cleanup" and event["status"] == "failed"
                                    for event in experiment.actions))
        asyncio.run(exercise())

    def test_initialization_tasks_finish_cancellation_before_contexts_close(self):
        root = FakeProcess(10)
        api = FakeProcessAPI(root)
        sampler = SimpleNamespace(system_metadata=lambda: {}, process_identities=lambda group: ((10, 1.0),))
        order = []

        async def exercise():
            initialized = asyncio.Event()
            user_cancelled = asyncio.Event()

            class Context:
                async def close(self):
                    self_test.assertTrue(user_cancelled.is_set())
                    order.append("context closed")

            class Browser:
                version = "fake"

                async def close(self):
                    order.append("browser closed")

            class Manager:
                async def start(self):
                    return SimpleNamespace(chromium=SimpleNamespace(launch=AsyncMock(return_value=Browser())))

                async def __aexit__(self, *arguments):
                    order.append("playwright stopped")

            with tempfile.TemporaryDirectory() as temporary_directory:
                output = Path(temporary_directory)
                (output / "scenarios.json").write_text("{}", encoding="utf-8")
                options = SimpleNamespace(startup_timeout_seconds=1, baseline_seconds=0,
                                          browser_channel=None, sample_seconds=0.01, users=2)
                experiment = run.Experiment(options, output, [])

                async def monitor(_sampler):
                    await experiment.monitor_stop.wait()

                async def initialize(_browser, _port, user):
                    experiment.sessions.append({"user": user + 1, "context": Context()})
                    initialized.set()
                    try:
                        await asyncio.Event().wait()
                    finally:
                        await asyncio.sleep(0)
                        order.append("user cancelled")
                        user_cancelled.set()

                experiment.monitor = monitor
                experiment.initialise_user = initialize
                with patch.dict(sys.modules, {"psutil": api, "metrics": SimpleNamespace(ProcessMetricsSampler=lambda *args: sampler)}):
                    with patch.object(run.subprocess, "Popen", return_value=FakePopen(root)):
                        with patch.object(run, "wait_for_server", new=AsyncMock()):
                            with patch("playwright.async_api.async_playwright", return_value=Manager()):
                                task = asyncio.create_task(experiment.execute())
                                await initialized.wait()
                                task.cancel()
                                with self_test.assertRaises(asyncio.CancelledError):
                                    await task
                self_test.assertTrue(root.terminated)
                self_test.assertEqual(order, ["user cancelled", "context closed", "browser closed", "playwright stopped"])
        self_test = self
        asyncio.run(exercise())

    def test_bounded_cleanup_reports_timeout_after_cancellation_finishes(self):
        async def exercise():
            task = asyncio.create_task(asyncio.Event().wait())
            errors, pending = await run.wait_for_tasks_bounded([task], timeout_seconds=0.01)
            self.assertFalse(pending)
            self.assertTrue(task.cancelled())
            self.assertTrue(any(isinstance(exception, TimeoutError) for exception in errors))
        asyncio.run(exercise())

    def test_loop_runner_preserves_primary_exception_and_calls_sync_fallback(self):
        cleanup_calls = []

        async def operation():
            raise ValueError("original startup failure")

        def cleanup():
            cleanup_calls.append("called")
            raise RuntimeError("cleanup failure")

        stderr = io.StringIO()
        with patch.object(sys, "stderr", stderr):
            with self.assertRaisesRegex(ValueError, "original startup failure"):
                run.run_with_interrupt_cleanup(operation, final_cleanup=cleanup)
        self.assertEqual(cleanup_calls, ["called"])
        self.assertIn("cleanup failure", stderr.getvalue())

    def test_two_real_sigints_leave_loop_running_until_cleanup_finishes(self):
        # Signal only this short-lived child; never the developer's terminal.
        script = r'''
import asyncio, signal, sys
sys.path.insert(0, sys.argv[1])
from run import run_with_interrupt_cleanup
async def operation():
    loop = asyncio.get_running_loop()
    loop.call_later(0.03, signal.raise_signal, signal.SIGINT)
    try:
        await asyncio.Event().wait()
    finally:
        print("CLEANUP_STARTED", flush=True)
        loop.call_later(0.01, signal.raise_signal, signal.SIGINT)
        await asyncio.sleep(0.06)
        print("CLEANUP_FINISHED", flush=True)
try:
    run_with_interrupt_cleanup(operation, final_cleanup=lambda: print("SYNC_FALLBACK", flush=True))
except KeyboardInterrupt:
    print("INTERRUPTED_AFTER_CLEANUP", flush=True)
'''
        import psutil
        child = subprocess.Popen([sys.executable, "-c", script, str(Path(run.__file__).parent)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        identity = (child.pid, psutil.Process(child.pid).create_time())
        observed = {}
        try:
            try:
                stdout, stderr = child.communicate(timeout=1)
            except subprocess.TimeoutExpired:
                for descendant in psutil.Process(child.pid).children(recursive=True):
                    observed[descendant.pid] = descendant.create_time()
                stdout, stderr = child.communicate(timeout=9)
            self.assertEqual(child.returncode, 0, stdout + stderr)
            self.assertLess(stdout.index("CLEANUP_STARTED"), stdout.index("CLEANUP_FINISHED"))
            self.assertLess(stdout.index("CLEANUP_FINISHED"), stdout.index("SYNC_FALLBACK"))
            self.assertLess(stdout.index("SYNC_FALLBACK"), stdout.index("INTERRUPTED_AFTER_CLEANUP"))
            self.assertNotIn("no running event loop", stderr)
            self.assertNotIn("Task was destroyed", stderr)
        finally:
            run.terminate_owned_process(child, identity, tuple(observed.items()))


if __name__ == "__main__":
    unittest.main()
