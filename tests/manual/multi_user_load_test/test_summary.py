"""Strict report gates using fabricated telemetry; no browser or server launch."""

import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

try:
    from . import run
except ImportError:
    import run


REQUIRED_ACTIONS = ("initial_analysis", "time_bin", "station", "scope", "drilldown", "idle_resume")


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.output = Path(self.temporary_directory.name)
        self.experiment = SimpleNamespace(
            output=self.output,
            arguments=SimpleNamespace(users=2, export_users=0, duration_seconds=60, baseline_seconds=5,
                                      cooldown_seconds=5, sample_seconds=5),
            started_at="2026-09-27T09:00:00+00:00",
            interaction_started_at="2026-09-27T09:00:05+00:00",
            interaction_finished_at="2026-09-27T09:01:05+00:00",
            failures=[],
            actions=[{"user": user, "action": action, "status": "ok", "duration_seconds": 0.2}
                     for user in (1, 2) for action in REQUIRED_ACTIONS],
            samples=[self.sample("baseline", 0, 0)]
                    + [self.sample("interaction", second, 2) for second in range(5, 65, 5)]
                    + [self.sample("recovery", 65, 0)],
        )
        self.write_checkpoints([
            {"phase": "end", "session_id": "session-1", "has_completed_run": True},
            {"phase": "end", "session_id": "session-2", "has_completed_run": True},
        ])

    @staticmethod
    def sample(phase, elapsed_seconds, active_users):
        return {"phase": phase, "elapsed_seconds": elapsed_seconds, "active_users": active_users,
                "server_rss_bytes": 1000, "generator_rss_bytes": 500,
                "server_private_bytes": 1500, "server_uss_bytes": 800,
                "system_available_ram_bytes": 2000,
                "server_discovery_complete": True, "generator_discovery_complete": True,
                "diagnostics": "[]"}

    def write_checkpoints(self, checkpoints):
        (self.output / "server.log").write_text(
            "\n".join("LOAD_TEST_SESSION " + json.dumps(record) for record in checkpoints),
            encoding="utf-8",
        )

    def summary(self, experiment=None, fatal_error=None):
        return run.build_summary(experiment or self.experiment, fatal_error)

    def test_complete_evidence_passes_without_claiming_capacity(self):
        summary = self.summary()
        self.assertEqual(summary["status"], "passed")
        self.assertEqual(summary["completed_server_session_count"], 2)
        self.assertEqual(summary["observed_interaction_seconds"], 60)
        self.assertTrue(summary["per_user_coverage"]["2"]["complete"])
        self.assertIn("memory ceiling", " ".join(summary["limitations"]))

    def test_default_exploration_needs_no_exports_and_reports_them_as_not_requested(self):
        del self.experiment.arguments.export_users
        summary = self.summary()
        self.assertEqual(summary["status"], "passed")
        self.assertNotIn("export", summary["required_actions_per_user"])
        self.assertNotIn("export", summary["action_coverage"])
        self.assertEqual(summary["export_policy"], {
            "requested_users": 0,
            "selected_user_ids": [],
            "maximum_exports_per_selected_user": 1,
            "successful_users": 0,
            "complete": True,
        })
        self.assertFalse(summary["per_user_coverage"]["1"]["export_required"])
        self.assertFalse(summary["per_user_coverage"]["1"]["actions"]["export"])
        run.write_report(self.output, summary)
        report = (self.output / "report.md").read_text(encoding="utf-8")
        self.assertEqual(report.count("not requested"), 2)

    def test_only_selected_users_require_an_export(self):
        self.experiment.arguments.export_users = 1
        summary = self.summary()
        self.assertEqual(summary["status"], "incomplete_or_failed")
        self.assertEqual(summary["per_user_coverage"]["1"]["missing_actions"], ["export"])
        self.assertTrue(summary["per_user_coverage"]["2"]["complete"])
        self.assertFalse(summary["export_policy"]["complete"])
        self.experiment.actions.append({"user": 1, "action": "export", "status": "ok", "duration_seconds": 1})
        summary = self.summary()
        self.assertEqual(summary["status"], "passed")
        self.assertEqual(summary["export_policy"]["selected_user_ids"], [1])
        self.assertEqual(summary["export_policy"]["successful_users"], 1)
        self.assertTrue(summary["export_policy"]["complete"])
        self.assertFalse(summary["per_user_coverage"]["2"]["export_required"])

    def test_an_unselected_users_export_does_not_cover_the_selected_user(self):
        self.experiment.arguments.export_users = 1
        self.experiment.actions.append({"user": 2, "action": "export", "status": "ok", "duration_seconds": 1})
        summary = self.summary()
        self.assertEqual(summary["status"], "incomplete_or_failed")
        self.assertEqual(summary["export_policy"]["successful_users"], 0)
        self.assertEqual(summary["per_user_coverage"]["1"]["missing_actions"], ["export"])

    def test_ui_tracing_is_reported_as_diagnostic_instrumentation(self):
        self.assertFalse(self.summary()["diagnostic_ui_tracing"])
        self.experiment.arguments.trace_ui_deltas = True
        summary = self.summary()
        self.assertTrue(summary["diagnostic_ui_tracing"])
        run.write_report(self.output, summary)
        report = (self.output / "report.md").read_text(encoding="utf-8")
        self.assertIn("instrumentation overhead", report)
        self.assertIn("not an ordinary memory baseline", report)

    def test_one_users_action_does_not_cover_another_user(self):
        self.experiment.actions = [record for record in self.experiment.actions
                                   if not (record["user"] == 2 and record["action"] == "station")]
        summary = self.summary()
        self.assertEqual(summary["status"], "incomplete_or_failed")
        self.assertEqual(summary["actions"]["station"]["successful"], 1)
        self.assertFalse(summary["action_coverage"]["station"])
        self.assertEqual(summary["per_user_coverage"]["2"]["missing_actions"], ["station"])

    def test_started_or_invalid_sessions_do_not_count_as_completed(self):
        self.write_checkpoints([
            {"phase": "start", "session_id": "session-1", "has_completed_run": True},
            {"phase": "end", "session_id": "session-2", "has_completed_run": False},
            {"phase": "end", "session_id": None, "has_completed_run": True},
            {"phase": "end", "session_id": "session-3", "has_completed_run": "true"},
        ])
        summary = self.summary()
        self.assertEqual(summary["server_session_count"], 3)
        self.assertEqual(summary["completed_server_session_count"], 0)
        self.assertFalse(summary["session_count_verified"])
        self.assertEqual(summary["server_checkpoint_parse_errors"], 1)

    def test_repeated_completed_checkpoints_do_not_multiply_sessions(self):
        checkpoint = {"phase": "end", "session_id": "same-session", "has_completed_run": True}
        self.write_checkpoints([checkpoint, checkpoint])
        self.assertEqual(self.summary()["status"], "incomplete_or_failed")

    def test_missing_or_invalid_required_memory_never_passes(self):
        for field, recorded in (("server_rss_bytes", None), ("server_rss_bytes", 0),
                                ("generator_rss_bytes", float("nan")),
                                ("system_available_ram_bytes", None),
                                ("server_discovery_complete", False),
                                ("generator_discovery_complete", False),
                                ("elapsed_seconds", True)):
            with self.subTest(field=field, recorded=recorded):
                experiment = copy.deepcopy(self.experiment)
                experiment.samples[1][field] = recorded
                summary = self.summary(experiment)
                self.assertEqual(summary["status"], "incomplete_or_failed")
                self.assertEqual(summary["memory_coverage"]["interaction"]["invalid_memory_sample_count"], 1)

    def test_missing_required_phase_fails_but_disabled_phases_are_exempt(self):
        self.experiment.samples = [sample for sample in self.experiment.samples if sample["phase"] == "interaction"]
        self.assertEqual(self.summary()["status"], "incomplete_or_failed")
        self.experiment.arguments.baseline_seconds = 0
        self.experiment.arguments.cooldown_seconds = 0
        self.assertEqual(self.summary()["status"], "passed")

    def test_monitor_requires_sustained_samples_not_one_token_observation(self):
        self.experiment.samples = [sample for sample in self.experiment.samples
                                   if sample["phase"] != "interaction" or sample["elapsed_seconds"] == 5]
        summary = self.summary()
        self.assertEqual(summary["status"], "incomplete_or_failed")
        self.assertFalse(summary["memory_coverage"]["interaction"]["cadence_complete"])

    def test_long_monitor_gap_is_reported_even_when_endpoints_exist(self):
        self.experiment.samples = [sample for sample in self.experiment.samples
                                   if not 10 <= sample["elapsed_seconds"] <= 25]
        summary = self.summary()
        self.assertEqual(summary["memory_coverage"]["interaction"]["maximum_gap_seconds"], 25)
        self.assertEqual(summary["status"], "incomplete_or_failed")

    def test_requested_simultaneous_users_must_be_observed(self):
        for sample in self.experiment.samples:
            sample["active_users"] = 1
        self.assertEqual(self.summary()["status"], "incomplete_or_failed")

    def test_short_or_unfinished_interaction_period_does_not_pass(self):
        for finished_at in (None, "2026-09-27T09:01:04+00:00"):
            with self.subTest(finished_at=finished_at):
                self.experiment.interaction_finished_at = finished_at
                self.assertEqual(self.summary()["status"], "incomplete_or_failed")

    def test_optional_measurement_diagnostics_are_visible(self):
        self.experiment.samples[1]["server_uss_bytes"] = None
        self.experiment.samples[1]["diagnostics"] = '["server.100.uss: AccessDenied"]'
        summary = self.summary()
        self.assertEqual(summary["status"], "passed")
        self.assertEqual(summary["metric_diagnostic_sample_count"], 1)
        self.assertEqual(summary["metric_diagnostics"]["server.100.uss: AccessDenied"], 1)
        run.write_report(self.output, summary)
        report = (self.output / "report.md").read_text(encoding="utf-8")
        self.assertIn("AccessDenied", report)
        self.assertIn("observed 60.00 seconds", report)
        self.assertIn("Coverage for each user", report)
        self.assertIn("does not certify a safe memory ceiling", report)

    def test_fatal_or_recorded_failure_prevents_pass_despite_coverage(self):
        self.assertEqual(self.summary(fatal_error="monitor failed")["status"], "incomplete_or_failed")
        self.experiment.arguments.export_users = 1
        self.experiment.actions.append({"user": 1, "action": "export", "status": "failed", "duration_seconds": 1})
        summary = self.summary()
        self.assertEqual(summary["failure_count"], 1)
        self.assertEqual(summary["status"], "incomplete_or_failed")


if __name__ == "__main__":
    unittest.main()
