"""Browser-action contracts using real protocol messages and isolated fake pages.

These tests launch no browser or server and make no provider requests.
"""

import asyncio
from collections import deque
from contextlib import redirect_stderr
from io import StringIO
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch
import zipfile

from streamlit.proto.ForwardMsg_pb2 import ForwardMsg

try:
    from . import run
except ImportError:
    import run


def make_session(page):
    return {
        "user": 1, "page": page, "scenario": "fake-scenario",
        "script_starts": 0, "expected_script_start": 1,
        "finished_script_start": 0, "script_run_id": None,
        "script_fragment_ids": [], "last_script_status": None,
        "script_is_running": False, "protocol_error": None,
        "failure_event": asyncio.Event(), "browser_errors": [],
        "action_phase": "initial_analysis", "export_verified": False,
    }


def deliver(session, message):
    """Use the same protobuf wire representation received by a real browser."""
    decoded = ForwardMsg()
    decoded.ParseFromString(message.SerializeToString())
    run.observe_script_message(session, decoded)


def start_script(session, run_id, fragment_ids=()):
    message = ForwardMsg()
    message.new_session.script_run_id = run_id
    message.new_session.fragment_ids_this_run.extend(fragment_ids)
    deliver(session, message)


def finish_script(session, status=ForwardMsg.FINISHED_SUCCESSFULLY):
    deliver(session, ForwardMsg(script_finished=status))


def set_script_running(session, is_running):
    message = ForwardMsg()
    message.session_status_changed.script_is_running = is_running
    deliver(session, message)


class FakePage:
    def __init__(self):
        self.closed = False
        self.exception = None
        self.running = False
        self.evaluations = 0
        self.steps = deque()

    def is_closed(self):
        return self.closed

    async def evaluate(self, _expression):
        self.evaluations += 1
        if self.steps:
            self.steps.popleft()()
        return {"exception": self.exception, "running": self.running}


class AdvancingClock:
    """Advance only the harness clock; leave the event loop's clock untouched."""
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    async def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds
        await asyncio.sleep(0)


class ArgumentTests(unittest.TestCase):
    def test_scope_is_fixed_unless_explicitly_requested(self):
        self.assertFalse(run.parse_arguments([]).vary_scope)
        self.assertFalse(run.parse_arguments(["--smoke"]).vary_scope)
        self.assertTrue(run.parse_arguments(["--smoke", "--vary-scope"]).vary_scope)

    def test_regular_and_smoke_defaults_do_not_export(self):
        self.assertEqual(run.parse_arguments([]).export_users, 0)
        smoke = run.parse_arguments(["--smoke"])
        self.assertEqual(smoke.users, 1)
        self.assertEqual(smoke.export_users, 0)

    def test_export_user_count_is_validated_against_effective_users(self):
        self.assertEqual(run.parse_arguments(["--users", "10", "--export-users", "1"]).export_users, 1)
        self.assertEqual(run.parse_arguments(["--smoke", "--export-users", "1"]).export_users, 1)
        for arguments in (["--export-users", "-1"], ["--users", "3", "--export-users", "4"],
                          ["--smoke", "--users", "10", "--export-users", "2"], ["--export-users", "0.5"]):
            with self.subTest(arguments=arguments), redirect_stderr(StringIO()), self.assertRaises(SystemExit):
                run.parse_arguments(arguments)


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.session = make_session(FakePage())

    def test_native_bulk_commands_are_excluded_without_rejecting_scope_defaults(self):
        for label in ("Select all", "Select 3 matches"):
            self.assertTrue(run.is_bulk_scope_option(label))
        for label in ("Full Range", "All Directions", "NE", "0-1000 km"):
            self.assertFalse(run.is_bulk_scope_option(label))

    def test_arm_requires_a_new_start_after_previous_success(self):
        start_script(self.session, "previous")
        finish_script(self.session)
        run.expect_script_run(self.session, "scope")
        self.assertEqual(self.session["expected_script_start"], 2)
        self.assertEqual(self.session["finished_script_start"], 1)
        self.assertEqual(self.session["action_phase"], "scope")

    def test_early_rerun_does_not_complete_the_replacement_run(self):
        start_script(self.session, "interrupted")
        finish_script(self.session, ForwardMsg.FINISHED_EARLY_FOR_RERUN)
        self.assertEqual(self.session["finished_script_start"], 0)
        self.assertFalse(self.session["failure_event"].is_set())
        start_script(self.session, "replacement")
        self.assertIsNone(self.session["last_script_status"])
        finish_script(self.session)
        self.assertEqual(self.session["finished_script_start"], 2)
        self.assertEqual(self.session["script_run_id"], "replacement")

    def test_full_and_fragment_runs_have_successful_completion(self):
        for status, fragments in (
            (ForwardMsg.FINISHED_SUCCESSFULLY, []),
            (ForwardMsg.FINISHED_FRAGMENT_RUN_SUCCESSFULLY, ["inspector-fragment"]),
        ):
            with self.subTest(status=status):
                session = make_session(FakePage())
                start_script(session, "successful", fragments)
                set_script_running(session, True)
                self.assertTrue(session["script_is_running"])
                finish_script(session, status)
                set_script_running(session, False)
                self.assertEqual(session["finished_script_start"], 1)
                self.assertEqual(session["script_fragment_ids"], fragments)
                self.assertEqual(session["last_script_status"], ForwardMsg.ScriptFinishedStatus.Name(status))
                self.assertFalse(session["script_is_running"])

    def test_compile_failure_sets_a_fatal_event(self):
        start_script(self.session, "broken")
        finish_script(self.session, ForwardMsg.FINISHED_WITH_COMPILE_ERROR)
        self.assertTrue(self.session["failure_event"].is_set())
        self.assertIn("compile error", self.session["protocol_error"])
        self.assertEqual(self.session["finished_script_start"], 0)


class InteractionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.experiment = run.Experiment(
            SimpleNamespace(action_timeout_seconds=2, startup_timeout_seconds=2),
            Path(temporary.name), [],
        )
        self.page = FakePage()
        self.session = make_session(self.page)
        self.experiment.sessions.append(self.session)

    async def settle_with_clock(self):
        clock = AdvancingClock()
        with patch.object(run, "time", SimpleNamespace(monotonic=clock.monotonic)), \
                patch.object(run, "asyncio", SimpleNamespace(sleep=clock.sleep)):
            await self.experiment.settle(self.page)
        return clock

    async def test_settle_waits_for_replacement_start_success_and_quiet_page(self):
        start_script(self.session, "previous")
        finish_script(self.session)
        run.expect_script_run(self.session, "time_bin")

        def interrupted_run():
            start_script(self.session, "interrupted")
            finish_script(self.session, ForwardMsg.FINISHED_EARLY_FOR_RERUN)

        def replacement_run():
            start_script(self.session, "replacement", ["inspector"])

        self.page.steps.extend([
            lambda: None, interrupted_run, lambda: None, replacement_run,
            lambda: finish_script(self.session, ForwardMsg.FINISHED_FRAGMENT_RUN_SUCCESSFULLY),
        ])
        clock = await self.settle_with_clock()
        self.assertFalse(self.page.steps, "A stale or interrupted run must never settle the action")
        self.assertGreater(self.page.evaluations, 5, "Success still requires a quiet rendered page")
        self.assertGreaterEqual(clock.now, 0.25)
        self.assertEqual(self.session["script_run_id"], "replacement")

    async def test_protocol_and_visible_running_states_both_delay_completion(self):
        start_script(self.session, "complete")
        finish_script(self.session)
        set_script_running(self.session, True)
        self.page.running = True
        self.page.steps.extend([
            lambda: None,
            lambda: set_script_running(self.session, False),
            lambda: None,
            lambda: setattr(self.page, "running", False),
        ])
        await self.settle_with_clock()
        self.assertFalse(self.page.steps)
        self.assertGreater(self.page.evaluations, 4)

    async def test_visible_application_error_wins_over_success(self):
        start_script(self.session, "apparently-complete")
        finish_script(self.session)
        self.page.exception = "ValueError: invalid scientific input"
        with self.assertRaisesRegex(RuntimeError, "Application execution failed.*invalid scientific input"):
            await self.settle_with_clock()
        self.assertEqual(self.page.evaluations, 1)

    async def test_compile_error_fails_without_waiting_for_the_dom(self):
        start_script(self.session, "broken")
        finish_script(self.session, ForwardMsg.FINISHED_WITH_COMPILE_ERROR)
        with self.assertRaisesRegex(RuntimeError, "compile error"):
            await self.settle_with_clock()
        self.assertEqual(self.page.evaluations, 0)

    async def test_missing_new_run_reaches_the_action_deadline(self):
        start_script(self.session, "previous")
        finish_script(self.session)
        run.expect_script_run(self.session, "station")
        self.experiment.arguments.action_timeout_seconds = 0.1
        with self.assertRaisesRegex(TimeoutError, "expected browser action"):
            await self.settle_with_clock()

    async def test_browser_failure_interrupts_and_cancels_blocked_action(self):
        started = asyncio.Event()
        cancelled = asyncio.Event()

        async def blocked_action():
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        guarded = asyncio.create_task(self.experiment.run_guarded_action(self.session, blocked_action))
        try:
            await asyncio.wait_for(started.wait(), timeout=1)
            self.session["browser_errors"].append("Uncaught frontend failure")
            self.session["failure_event"].set()
            with self.assertRaisesRegex(RuntimeError, "Browser execution failed.*Uncaught frontend failure"):
                await asyncio.wait_for(guarded, timeout=1)
            self.assertTrue(cancelled.is_set())
        finally:
            guarded.cancel()
            await asyncio.gather(guarded, return_exceptions=True)

    async def test_guard_deadline_cancels_a_blocked_action(self):
        self.experiment.arguments.action_timeout_seconds = 0.01
        cancelled = asyncio.Event()

        async def blocked_action():
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        with self.assertRaisesRegex(TimeoutError, "Browser action exceeded its deadline"):
            await asyncio.wait_for(
                self.experiment.run_guarded_action(self.session, blocked_action), timeout=1,
            )
        self.assertTrue(cancelled.is_set())

    async def test_fatal_browser_event_wins_over_simultaneous_action_result(self):
        async def apparently_successful_action():
            self.session["browser_errors"].append("late frontend failure")
            self.session["failure_event"].set()
            return "ok"

        with self.assertRaisesRegex(RuntimeError, "late frontend failure"):
            await self.experiment.run_guarded_action(self.session, apparently_successful_action)

    async def test_initial_scope_requires_both_all_selections_and_matching_summary(self):
        expected_summary = "Active scope · Full Range · All Directions"
        for selections, scope_summary, should_pass in (
            (["Full Range", "All Directions"], expected_summary, True),
            (["Full Range", "ENE"], expected_summary, False),
            (["Full Range", "All Directions"], "Active scope · Full Range · ENE", False),
        ):
            with self.subTest(selections=selections, scope_summary=scope_summary):
                panel = SimpleNamespace(locator=Mock(side_effect={
                    '[data-testid="stMultiSelect"]': SimpleNamespace(all_inner_texts=AsyncMock(return_value=selections)),
                    '.result-scope-summary > p': SimpleNamespace(first=SimpleNamespace(
                        inner_text=AsyncMock(return_value=scope_summary))),
                }.__getitem__))
                self.page.locator = Mock(return_value=SimpleNamespace(first=panel))
                if should_pass:
                    observed = await self.experiment.verify_initial_scope(self.page)
                    self.assertEqual(observed, {"selections": selections, "active_scope": expected_summary})
                else:
                    with self.assertRaisesRegex(RuntimeError, "Initial results did not retain"):
                        await self.experiment.verify_initial_scope(self.page)

    async def test_time_bins_alternate_evidence_panels_only_after_success(self):
        control = SimpleNamespace(
            is_visible=AsyncMock(return_value=True), is_enabled=AsyncMock(return_value=True),
            evaluate=AsyncMock(), inner_text=AsyncMock(return_value="2m"), click=AsyncMock(),
        )
        controls = SimpleNamespace(count=AsyncMock(return_value=1), nth=Mock(return_value=control))
        controls.filter = Mock(return_value=controls)
        panel = SimpleNamespace(locator=Mock(return_value=controls))
        self.page.locator = Mock(return_value=SimpleNamespace(first=panel))
        self.experiment.settle = AsyncMock()
        for iteration, expected_panel in enumerate(("segment_inspector", "selected_station", "segment_inspector")):
            control.evaluate.side_effect = [False, True]
            status, details = await self.experiment.change_time_bin(self.session, iteration)
            self.assertEqual(status, "ok")
            self.assertEqual(details["panel"], expected_panel)
            self.assertEqual(details["choice"], "2m")
            self.assertEqual(self.session["successful_time_bin_actions"], iteration + 1)
        self.assertEqual([call.args[0] for call in self.page.locator.call_args_list], [
            '[class*="st-key-results_evidence_level_2_"]',
            '[class*="st-key-results_evidence_level_4_"]',
            '[class*="st-key-results_evidence_level_2_"]',
        ])
        self.assertIsNotNone(controls.filter.call_args.kwargs["has_text"].fullmatch("2m"))
        controls.count.return_value = 0
        status, details = await self.experiment.change_time_bin(self.session, 3)
        self.assertEqual(status, "unavailable")
        self.assertEqual(details["panel"], "selected_station")
        self.assertEqual(self.session["successful_time_bin_actions"], 3)

    async def test_perform_action_records_success_only_after_settle_and_action(self):
        order = []
        self.experiment.settle = AsyncMock(side_effect=lambda _page: order.append("settled"))

        async def change_scope(session, iteration):
            self.assertIs(session, self.session)
            self.assertEqual(iteration, 3)
            self.assertEqual(order, ["settled"])
            order.append("scope changed")
            return "ok", {"choice": "East"}

        self.experiment.change_scope = change_scope
        self.experiment.capture_failure = AsyncMock()
        status = await self.experiment.perform_action(self.session, "scope", 3)
        self.assertEqual(status, "ok")
        self.assertEqual(order, ["settled", "scope changed"])
        self.assertEqual(self.experiment.actions[-1]["choice"], "East")
        self.assertEqual(self.experiment.actions[-1]["status"], "ok")
        self.experiment.capture_failure.assert_not_awaited()

    async def test_scope_failure_captures_observed_selection_and_scope_with_bounds(self):
        previous_selection = "All Directions"
        previous_scope = "Active scope · Full Range · All Directions"
        for suffix in ("", "x" * 1100):
            with self.subTest(observation_length=len(suffix)):
                observed_selection = previous_selection + suffix
                observed_scope = previous_scope + suffix
                control = SimpleNamespace(
                    focus=AsyncMock(), get_attribute=AsyncMock(return_value="false"),
                    press=AsyncMock(),
                )
                widget = SimpleNamespace(
                    inner_text=AsyncMock(side_effect=[previous_selection, observed_selection]),
                    get_by_role=Mock(return_value=SimpleNamespace(first=control)),
                )
                widgets = SimpleNamespace(count=AsyncMock(return_value=2), nth=Mock(return_value=widget))
                scope_summary = SimpleNamespace(
                    inner_text=AsyncMock(side_effect=[previous_scope, observed_scope]),
                )
                panel = SimpleNamespace(locator=Mock(side_effect={
                    '[data-testid="stMultiSelect"]': widgets,
                    '.result-scope-summary > p': SimpleNamespace(first=scope_summary),
                }.__getitem__))
                option = SimpleNamespace(
                    wait_for=AsyncMock(), get_attribute=AsyncMock(return_value="false"),
                    click=AsyncMock(),
                )
                options = SimpleNamespace(
                    first=option, all_text_contents=AsyncMock(return_value=["ENE"]),
                    nth=Mock(return_value=option),
                )
                self.page.locator = Mock(side_effect={
                    '[class*="st-key-results_evidence_level_2_"]': SimpleNamespace(first=panel),
                    '[role="option"]:visible': options,
                }.__getitem__)
                self.page.keyboard = SimpleNamespace(press=AsyncMock())
                self.experiment.settle = AsyncMock()
                self.experiment.capture_failure = AsyncMock()

                status = await self.experiment.perform_action(self.session, "scope", 3)

                self.assertEqual(status, "failed")
                failure = self.experiment.actions[-1]
                details = failure["script"]["action_details"]
                self.assertEqual(details["scope_option"], "ENE")
                self.assertEqual(details["previous_selection"], previous_selection)
                self.assertEqual(details["previous_scope"], previous_scope)
                self.assertEqual(details["observed_selection"], observed_selection[:1000])
                self.assertEqual(details["observed_scope"], observed_scope[:1000])
                self.assertIn(f"observed selection={observed_selection[:250]!r}", failure["error"])
                self.assertIn(f"active scope={observed_scope[:250]!r}", failure["error"])
                widgets.nth.assert_called_once_with(1)
                option.click.assert_awaited_once()
                self.page.keyboard.press.assert_awaited_once_with("Escape")
                self.assertEqual(self.experiment.settle.await_count, 2)
                self.experiment.capture_failure.assert_awaited_once_with(self.session, "scope")

    async def test_perform_action_records_application_failure_and_captures_evidence(self):
        self.experiment.settle = AsyncMock(side_effect=RuntimeError("Application execution failed: test error"))
        self.experiment.change_station = AsyncMock(return_value=("ok", {}))
        self.experiment.capture_failure = AsyncMock()
        status = await self.experiment.perform_action(self.session, "station", 0)
        self.assertEqual(status, "failed")
        self.assertEqual(self.experiment.actions[-1]["status"], "failed")
        self.assertIn("test error", self.experiment.actions[-1]["error"])
        self.experiment.change_station.assert_not_awaited()
        self.experiment.capture_failure.assert_awaited_once_with(self.session, "station")

    async def test_failed_action_stops_workload_but_keeps_the_session_connected(self):
        self.experiment.arguments.seed = 1
        self.experiment.active_users = 1
        self.experiment.perform_action = AsyncMock(return_value="failed")
        clock = AdvancingClock()
        with patch.object(run, "time", SimpleNamespace(monotonic=clock.monotonic)), \
                patch.object(run, "asyncio", SimpleNamespace(sleep=clock.sleep)):
            await self.experiment.interact(self.session, deadline=10)
        self.experiment.perform_action.assert_awaited_once_with(self.session, "time_bin", 0)
        self.assertFalse(self.session["workload_running"])
        self.assertEqual(self.experiment.active_users, 1)
        self.assertFalse(self.page.is_closed())
        self.assertEqual(self.experiment.actions[-1]["action"], "interaction_stopped")
        self.assertEqual(self.experiment.actions[-1]["status"], "failed")
        self.assertGreater(self.experiment.actions[-1]["remaining_seconds"], 0)

    async def record_exploration_workload(self, *, user=1, export_users=None, vary_scope=False, action_count=18):
        self.experiment.arguments.seed = 1
        self.experiment.arguments.think_seconds = 0.01
        self.experiment.arguments.idle_seconds = 0.01
        self.experiment.arguments.vary_scope = vary_scope
        if export_users is not None:
            self.experiment.arguments.export_users = export_users
        self.session["user"] = user
        clock = AdvancingClock()
        calls = []
        deadline = 1000

        async def record_action(_session, action, iteration):
            calls.append((action, iteration))
            if len(calls) >= action_count:
                clock.now = deadline
            return "ok"

        async def advance_pause(awaitable, timeout):
            awaitable.close()
            clock.now += timeout
            raise asyncio.TimeoutError

        self.experiment.perform_action = record_action
        with patch.object(run, "time", SimpleNamespace(monotonic=clock.monotonic)), \
                patch.object(run, "asyncio", SimpleNamespace(
                    sleep=clock.sleep, wait_for=advance_pause, TimeoutError=asyncio.TimeoutError,
                )):
            await self.experiment.interact(self.session, deadline=deadline)
        return calls

    async def test_default_workload_retains_scope_and_explores_without_exports(self):
        calls = await self.record_exploration_workload()
        self.assertEqual([action for action, _ in calls], ["time_bin", "station", "drilldown"] * 6)
        self.assertNotIn("scope", [action for action, _ in calls])
        self.assertNotIn("export", [action for action, _ in calls])
        self.assertTrue(any(record["action"] == "idle_resume" for record in self.experiment.actions))
        self.assertFalse(self.session["workload_running"])

    async def test_opt_in_workload_alternates_scope_widgets(self):
        calls = await self.record_exploration_workload(vary_scope=True)
        self.assertEqual([action for action, _ in calls[:8]], [
            "time_bin", "station", "drilldown", "scope", "time_bin", "station", "drilldown", "scope",
        ])
        self.assertNotIn("export", [action for action, _ in calls])
        scope_iterations = [iteration for action, iteration in calls if action == "scope"]
        self.assertEqual(scope_iterations, [3, 4, 5, 6])
        self.assertEqual([iteration % 2 for iteration in scope_iterations], [1, 0, 1, 0])
        self.assertTrue(any(record["action"] == "idle_resume" for record in self.experiment.actions))
        self.assertFalse(self.session["workload_running"])

    async def test_selected_user_exports_once_after_first_exploration_cycle(self):
        calls = await self.record_exploration_workload(user=2, export_users=2, action_count=20)
        export_positions = [index for index, (action, _) in enumerate(calls) if action == "export"]
        self.assertEqual(export_positions, [6])
        self.assertEqual(calls[7], ("time_bin", 6))
        self.assertNotIn("scope", [action for action, _ in calls])

    async def test_opt_in_scope_workload_exports_after_its_complete_cycle(self):
        calls = await self.record_exploration_workload(export_users=1, vary_scope=True, action_count=20)
        self.assertEqual([index for index, (action, _) in enumerate(calls) if action == "export"], [8])
        self.assertEqual(calls[9], ("time_bin", 8))

    async def test_unselected_user_does_not_export(self):
        calls = await self.record_exploration_workload(user=2, export_users=1)
        self.assertNotIn("export", [action for action, _ in calls])

    async def test_selected_user_does_not_export_before_finishing_exploration_cycle(self):
        calls = await self.record_exploration_workload(export_users=1, action_count=6)
        self.assertEqual(len(calls), 6)
        self.assertNotIn("export", [action for action, _ in calls])

    async def test_browser_failure_at_final_idle_deadline_is_recorded(self):
        self.experiment.arguments.seed = 1
        self.experiment.arguments.think_seconds = 10
        self.experiment.perform_action = AsyncMock(return_value="ok")
        self.experiment.capture_failure = AsyncMock()
        clock = AdvancingClock()

        async def fail_at_end_of_pause(awaitable, timeout):
            clock.now += timeout
            self.session["browser_errors"].append("failure during the final reading pause")
            self.session["failure_event"].set()
            return await awaitable

        with patch.object(run, "time", SimpleNamespace(monotonic=clock.monotonic)), \
                patch.object(run, "asyncio", SimpleNamespace(
                    sleep=clock.sleep, wait_for=fail_at_end_of_pause, TimeoutError=asyncio.TimeoutError,
                )):
            await self.experiment.interact(self.session, deadline=1)
        self.experiment.perform_action.assert_awaited_once()
        self.assertFalse(self.session["workload_running"])
        self.assertEqual(self.experiment.actions[-1]["action"], "interaction_stopped")
        self.assertIn("final reading pause", self.experiment.actions[-1]["error"])
        self.assertEqual(self.experiment.actions[-1]["remaining_seconds"], 0)
        self.experiment.capture_failure.assert_awaited_once_with(self.session, "interaction_end")

    async def test_monitor_separates_connected_users_from_running_workloads(self):
        self.experiment.arguments.sample_seconds = 0.01
        self.experiment.active_users = 2
        self.session["workload_running"] = False
        self.experiment.sessions.append({"workload_running": True})
        sampled_users = []

        def sample(_phase, active_users):
            sampled_users.append(active_users)
            self.experiment.monitor_stop.set()
            return {"server_rss_bytes": 1234, "system_available_ram_bytes": 5678}

        async def call_without_thread(function, *arguments):
            return function(*arguments)

        with patch.object(run, "asyncio", SimpleNamespace(
            to_thread=call_without_thread, wait_for=asyncio.wait_for, TimeoutError=asyncio.TimeoutError,
        )):
            await self.experiment.monitor(SimpleNamespace(sample=sample))
        self.assertEqual(sampled_users, [2])
        self.assertEqual(self.experiment.samples[0]["workload_users"], 1)


class FakeExportButton:
    def __init__(self, page, purpose):
        self.page = page
        self.purpose = purpose
        self.first = self

    async def count(self):
        return 1

    async def is_visible(self):
        return not self.page.prepared if self.purpose == "prepare" else self.page.prepared

    async def wait_for(self, **_kwargs):
        if not await self.is_visible():
            raise AssertionError("Download was awaited before preparation completed")

    async def click(self):
        session = self.page.session
        self.page.clicks.append((self.purpose, session["action_phase"],
                                 session["script_starts"], session["expected_script_start"]))
        start_script(session, f"{self.purpose}-{len(self.page.clicks)}")
        finish_script(session)
        if self.purpose == "prepare":
            self.page.prepared = True


class FakeDownload:
    def __init__(self, metadata):
        self.metadata = metadata

    async def save_as(self, path):
        with zipfile.ZipFile(path, "w") as package:
            package.writestr("benchmark/run_metadata.json", json.dumps(self.metadata))
            package.writestr("benchmark/evidence.csv", "station,count\nTEST,1\n")


class FakePendingDownload:
    def __init__(self, artifact):
        self.value = asyncio.get_running_loop().create_future()
        self.value.set_result(artifact)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False


class FakeExportPage(FakePage):
    def __init__(self, metadata):
        super().__init__()
        self.session = None
        self.prepared = False
        self.clicks = []
        self.artifact = FakeDownload(metadata)

    def get_by_role(self, role, *, name):
        if role != "button":
            raise AssertionError(f"Unexpected role: {role}")
        if name.search("Prepare All Results for Download"):
            return FakeExportButton(self, "prepare")
        if name.search("Download Prepared Results"):
            return FakeExportButton(self, "download")
        raise AssertionError(f"Unexpected button selector: {name}")

    def expect_download(self, **_kwargs):
        return FakePendingDownload(self.artifact)


class ExportTests(unittest.IsolatedAsyncioTestCase):
    async def test_prepare_and_each_download_arm_distinct_runs_including_reuse(self):
        configuration = {
            "core_parameters": {"callsign": "TEST", "band": "20m", "analysis_direction": "rx",
                                "time_selection": {"start_utc": "2026-01-01T00:00:00Z",
                                                   "end_utc": "2026-01-01T01:00:00Z"}},
            "comparison_parameters": {"mode": "reference"},
        }
        metadata = {"callsign": "TEST", "band": "20m", "run_mode": "RX",
                    "reference_or_benchmark_mode": "reference",
                    "time_window": configuration["core_parameters"]["time_selection"]}
        page = FakeExportPage(metadata)
        session = make_session(page)
        session["configuration"] = configuration
        page.session = session
        start_script(session, "initial-results")
        finish_script(session)
        clock = AdvancingClock()
        with tempfile.TemporaryDirectory() as directory:
            experiment = run.Experiment(
                SimpleNamespace(action_timeout_seconds=2, startup_timeout_seconds=2), Path(directory), [],
            )
            experiment.sessions.append(session)
            with patch.object(run, "time", SimpleNamespace(monotonic=clock.monotonic)), \
                    patch.object(run, "asyncio", SimpleNamespace(sleep=clock.sleep)):
                first_status, first_details = await experiment.export(session)
                second_status, second_details = await experiment.export(session)
            self.assertEqual((first_status, second_status), ("ok", "ok"))
            self.assertTrue(session["export_verified"])
            self.assertGreater(first_details["download_bytes"], 0)
            self.assertEqual(second_details["zip_entries"], 2)
            self.assertEqual(page.clicks, [
                ("prepare", "export_prepare", 1, 2),
                ("download", "export_download", 2, 3),
                ("download", "export_download", 3, 4),
            ])
            self.assertEqual(session["finished_script_start"], 4)
            self.assertTrue((Path(directory) / "downloads" / "user-01.zip").is_file())


if __name__ == "__main__":
    unittest.main()
