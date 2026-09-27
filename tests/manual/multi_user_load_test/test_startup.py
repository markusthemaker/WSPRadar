"""Startup diagnostics without replay preparation or an application server."""

import asyncio
import contextlib
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

try:
    from . import run
except ImportError:
    import run


class SourceSyntaxTests(unittest.TestCase):
    def test_source_is_compiled_without_execution_or_bytecode_files(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            (repository / "app.py").write_text("raise RuntimeError('must not execute')\n", encoding="utf-8")
            (repository / "note.txt").write_text("not Python syntax", encoding="utf-8")
            outcome = run.validate_source_syntax(
                [{"path": "app.py"}, {"path": "note.txt"}], repository)
            self.assertEqual(outcome["checked_python_files"], 1)
            self.assertEqual(outcome["status"], "passed")
            self.assertFalse((repository / "__pycache__").exists())

    def test_syntax_failure_names_interpreter_file_and_line(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            (repository / "broken.py").write_text("if True\n    pass\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, r"Python .*broken.py:1:.*No replay preparation"):
                run.validate_source_syntax([{"path": "broken.py"}], repository)

    def test_setup_failure_is_packaged_before_child_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "new-run"
            with patch.object(run, "version_record", return_value={"source_files": []}), \
                    patch.object(run, "validate_source_syntax", side_effect=RuntimeError("broken source")), \
                    patch.object(run, "run_owned_preparation") as prepare, \
                    patch.object(run, "Experiment") as experiment, \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(run.main(["--smoke", "--output", str(output)]), 1)
            prepare.assert_not_called()
            experiment.assert_not_called()
            self.assertTrue((output / "setup_failure.json").is_file())
            self.assertTrue(output.with_suffix(".zip").is_file())


class InitialResultsTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.experiment = run.Experiment(
            SimpleNamespace(startup_timeout_seconds=0.01), Path(self.temporary.name), [])
        self.exception = SimpleNamespace(
            is_visible=AsyncMock(return_value=False),
            inner_text=AsyncMock(return_value="SyntaxError: unterminated string literal"))
        self.button = SimpleNamespace(is_visible=AsyncMock(return_value=False))
        self.page = SimpleNamespace(
            is_closed=lambda: False,
            locator=lambda selector: SimpleNamespace(first=self.exception),
            get_by_role=lambda *args, **kwargs: SimpleNamespace(first=self.button))
        self.session = {"page": self.page, "user": 1, "scenario": "benchmark-large", "browser_errors": []}

    async def test_ready_result_returns_without_polling(self):
        self.button.is_visible.return_value = True
        await self.experiment.wait_for_initial_results(self.session)

    async def test_app_error_wins_even_if_stale_result_button_exists(self):
        self.exception.is_visible.return_value = True
        self.button.is_visible.return_value = True
        with self.assertRaisesRegex(RuntimeError, "Application failed.*SyntaxError.*server.log"):
            await self.experiment.wait_for_initial_results(self.session)
        self.button.is_visible.assert_not_awaited()

    async def test_browser_error_fails_without_waiting_for_timeout(self):
        self.session["browser_errors"].append("Uncaught frontend failure")
        with self.assertRaisesRegex(RuntimeError, "Browser error.*Uncaught frontend failure"):
            await self.experiment.wait_for_initial_results(self.session)
        self.button.is_visible.assert_not_awaited()

    async def test_closed_page_has_specific_diagnostic(self):
        self.page.is_closed = lambda: True
        with self.assertRaisesRegex(RuntimeError, "Browser page closed"):
            await self.experiment.wait_for_initial_results(self.session)

    async def test_timeout_explains_timer_and_where_to_find_evidence(self):
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(TimeoutError, "User 1.*server.log.*timer has not started"):
                await self.experiment.wait_for_initial_results(self.session)

    async def test_cancellation_is_not_converted_to_timeout(self):
        self.experiment.arguments.startup_timeout_seconds = 60
        waiting = asyncio.create_task(self.experiment.wait_for_initial_results(self.session))
        with contextlib.redirect_stdout(io.StringIO()):
            await asyncio.sleep(0)
            waiting.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await waiting


if __name__ == "__main__":
    unittest.main()
