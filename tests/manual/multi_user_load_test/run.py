"""Opt-in browser load experiment; never imported by the WSPRadar application.

Run this file directly. All child processes belong to this foreground command and
are closed in its finally path. Production configuration and caches are untouched.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import re
import signal
import socket
import statistics
import subprocess
import sys
import time
import traceback
import uuid
import zipfile

HARNESS_DIRECTORY = Path(__file__).resolve().parent
REPOSITORY = next(parent for parent in HARNESS_DIRECTORY.parents
                  if (parent / "app.py").is_file() and (parent / "AGENT_README.md").is_file())

# Prefer accessibility state over Streamlit's version-dependent styling names.
BUTTON_SELECTION_JAVASCRIPT = """element => {
    for (const name of ['aria-pressed', 'aria-checked', 'aria-selected']) {
        const value = element.getAttribute(name);
        if (value === 'true' || value === 'false') return value === 'true';
    }
    if (element.getAttribute('data-variant') === 'segmented_control') {
        return element.hasAttribute('data-selected');
    }
    const state = element.getAttribute('data-state');
    if (['on', 'checked', 'active'].includes(state)) return true;
    if (['off', 'unchecked', 'inactive'].includes(state)) return false;
    const kind = element.getAttribute('kind');
    if (kind === 'segmented_controlActive') return true;
    if (kind === 'segmented_control') return false;
    if (element.matches('input[type="radio"]')) return element.checked;
    return null;
}"""


def parse_arguments(arguments=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--export-users", type=int, default=0,
                        help="First N users each export once after a full exploration cycle; default: none.")
    parser.add_argument("--vary-scope", action="store_true",
                        help="Also change distance/direction scope for diagnostics; default: retain Full Range and All Directions.")
    parser.add_argument("--duration-seconds", type=float, default=900,
                        help="Interaction period AFTER every session has completed a run.")
    parser.add_argument("--cooldown-seconds", type=float, default=300)
    parser.add_argument("--baseline-seconds", type=float, default=20)
    parser.add_argument("--sample-seconds", type=float, default=5)
    parser.add_argument("--think-seconds", type=float, default=25,
                        help="Mean reading pause between actions, with seeded variation.")
    parser.add_argument("--idle-seconds", type=float, default=120,
                        help="Connected idle pause once per action cycle, followed by a verified interaction.")
    parser.add_argument("--action-timeout-seconds", type=float, default=180)
    parser.add_argument("--startup-timeout-seconds", type=float, default=600)
    parser.add_argument("--seed", type=int, default=27092026)
    parser.add_argument("--scenarios", default="benchmark-large,performance")
    parser.add_argument("--performance-replay", type=Path,
                        default=REPOSITORY / ".test" / "multiuser-datasets" / "griffiths-performance",
                        help="Directory captured once with capture.py; required for the Griffiths Performance scenario.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--browser-channel", default=None,
                        help="Optional installed browser channel, e.g. msedge on Windows.")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--trace-ui-deltas", action="store_true",
                        help="Diagnostic smoke: retain bounded UI structure and browser stack traces; no table/image payloads.")
    parser.add_argument("--smoke", action="store_true",
                        help="One user, 120 seconds interacting, 10 seconds recovery.")
    arguments = parser.parse_args(arguments)
    if arguments.smoke:
        arguments.users = 1
        arguments.duration_seconds = 120
        arguments.cooldown_seconds = 10
        arguments.baseline_seconds = 5
        arguments.think_seconds = 2
        arguments.idle_seconds = 2
    if not 1 <= arguments.users <= 100:
        parser.error("--users must be between 1 and 100")
    if not 0 <= arguments.export_users <= arguments.users:
        parser.error("--export-users must be between 0 and --users after smoke settings are applied")
    for field in ("duration_seconds", "sample_seconds", "think_seconds", "idle_seconds",
                  "action_timeout_seconds", "startup_timeout_seconds"):
        if not 0 < getattr(arguments, field) <= 86400:
            parser.error(f"--{field.replace('_', '-')} must be positive and <= 86400")
    for field in ("cooldown_seconds", "baseline_seconds"):
        if not 0 <= getattr(arguments, field) <= 86400:
            parser.error(f"--{field.replace('_', '-')} must be between 0 and 86400")
    return arguments


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, content):
    path.write_text(json.dumps(content, indent=2, default=str) + "\n", encoding="utf-8")


def observe_script_message(session, message):
    """Track full and fragment runs without accepting interrupted runs as done."""
    from streamlit.proto.ForwardMsg_pb2 import ForwardMsg

    message_type = message.WhichOneof("type")
    if message_type == "new_session":
        session["script_starts"] += 1
        session["script_run_id"] = message.new_session.script_run_id
        session["script_fragment_ids"] = list(message.new_session.fragment_ids_this_run)
        session["last_script_status"] = None
    elif message_type == "script_finished":
        status = message.script_finished
        session["last_script_status"] = ForwardMsg.ScriptFinishedStatus.Name(status)
        if status in (ForwardMsg.FINISHED_SUCCESSFULLY,
                      ForwardMsg.FINISHED_FRAGMENT_RUN_SUCCESSFULLY):
            session["finished_script_start"] = session["script_starts"]
        elif status == ForwardMsg.FINISHED_WITH_COMPILE_ERROR:
            session["protocol_error"] = "Streamlit reported a script compile error; see server.log"
            session["failure_event"].set()
        # EARLY_FOR_RERUN leaves the action pending for the replacement run.
    elif message_type == "session_status_changed":
        session["script_is_running"] = message.session_status_changed.script_is_running


def script_diagnostics(session):
    return {name: session.get(name) for name in (
        "action_phase", "action_details", "script_starts", "expected_script_start", "finished_script_start",
        "script_run_id", "script_fragment_ids", "last_script_status", "script_is_running",
        "protocol_error", "browser_errors",
    )}


def expect_script_run(session, phase):
    """Arm immediately before a real action, never for an unavailable control."""
    session["action_phase"] = phase
    session["expected_script_start"] = session["script_starts"] + 1


def is_bulk_scope_option(label):
    """The English replay UI's native bulk command is not an application value."""
    return label == "Select all" or re.fullmatch(r"Select \d+ matches", label) is not None


def validate_source_syntax(source_files, repository=REPOSITORY):
    """Check source with the executing interpreter, without importing the app."""
    from make_bundle import validated_source_path

    checked_files = 0
    for record in source_files:
        if Path(record["path"]).suffix != ".py":
            continue
        source_path = validated_source_path(repository, record["path"])
        try:
            compile(source_path.read_bytes(), str(source_path), "exec", dont_inherit=True)
        except SyntaxError as error:
            raise RuntimeError(
                f"Source syntax check failed with Python {platform.python_version()}: "
                f"{record['path']}:{error.lineno}: {error.msg}. "
                "No replay preparation, server or browser was launched."
            ) from error
        checked_files += 1
    return {"python": sys.version, "checked_python_files": checked_files, "status": "passed"}


def create_output_directory(requested):
    if requested is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        requested = REPOSITORY / ".test" / "multiuser-load" / f"{stamp}-{uuid.uuid4().hex[:6]}"
    output = requested.resolve()
    if output.exists():
        raise ValueError(f"Output already exists; choose a NEW directory: {output}")
    output.mkdir(parents=True)
    return output


def available_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def version_record():
    from make_bundle import inspect_checkout, source_digest, validated_source_path

    versions = {}
    for name in ("streamlit", "pandas", "numpy", "matplotlib", "cartopy", "pyarrow",
                 "playwright", "psutil"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    snapshot_path = REPOSITORY / "source_snapshot.json"
    if snapshot_path.exists():
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        names = [record["path"] for record in snapshot["files"]]
        revision = snapshot["git_revision"]
        dirty = snapshot["dirty"]
    else:
        snapshot = None
        checkout = inspect_checkout(REPOSITORY)
        names = checkout["files"]
        revision = checkout["git_revision"]
        dirty = checkout["dirty"]
    source_files = []
    for name in sorted(set(names)):
        path = validated_source_path(REPOSITORY, name)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        source_files.append({"path": name.replace("\\", "/"), "sha256": digest})
    digest = source_digest(source_files)
    if snapshot is not None and (source_files != snapshot["files"] or digest != snapshot["source_digest"]):
        raise ValueError("Extracted source differs from source_snapshot.json; extract a fresh transfer ZIP into a new folder")
    return {"python": sys.version, "platform": platform.platform(), "packages": versions,
            "git_revision": revision, "working_tree_dirty": dirty,
            "snapshot_verified": snapshot is not None,
            "source_digest": digest, "source_files": source_files}


def terminate_owned_process(process, root_identity, observed_identities=()):
    """Stop verified owned processes, preserving unrelated reused process IDs.

    Retained observed identities allow cleanup of a Windows launcher child after
    its parent has exited. Every signal uses a fresh PID/create-time check.
    Graceful termination and forced termination both have bounded confirmation.
    """
    import psutil
    if root_identity is None:
        # The Popen object retains the exact child handle on Windows. An identity
        # acquisition failure must still stop this child, but cannot prove that
        # a launcher descendant was discovered.
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        raise RuntimeError("Server process identity was unavailable; owned root stopped, descendant cleanup is unverified")
    identities = dict(observed_identities)
    identities[root_identity[0]] = root_identity[1]
    skipped_reused_pids = set()
    unverified_pids = set()

    def verified_process(process_id, created_at):
        try:
            candidate = psutil.Process(process_id)
            if float(candidate.create_time()) != float(created_at):
                skipped_reused_pids.add(process_id)
                return None
            return candidate
        except psutil.NoSuchProcess:
            return None
        except psutil.Error:
            unverified_pids.add(process_id)
            return None

    # Discover any children created since the last sample before stopping roots.
    for process_id, created_at in tuple(identities.items()):
        candidate = verified_process(process_id, created_at)
        if candidate is None:
            continue
        try:
            for descendant in candidate.children(recursive=True):
                try:
                    identities[descendant.pid] = float(descendant.create_time())
                except psutil.NoSuchProcess:
                    continue
                except psutil.Error:
                    unverified_pids.add(descendant.pid)
        except psutil.NoSuchProcess:
            continue
        except psutil.Error:
            unverified_pids.add(process_id)
    ordered_identities = sorted(identities.items(), key=lambda identity: identity[0] == root_identity[0])
    terminated = []
    for process_id, created_at in ordered_identities:
        candidate = verified_process(process_id, created_at)
        if candidate is not None:
            try:
                candidate.terminate()
                terminated.append(candidate)
            except psutil.NoSuchProcess:
                continue
            except psutil.Error:
                unverified_pids.add(process_id)
    _, survivors = psutil.wait_procs(terminated, timeout=10)
    forced = []
    for survivor in survivors:
        candidate = verified_process(survivor.pid, identities[survivor.pid])
        if candidate is not None:
            try:
                candidate.kill()
                forced.append(candidate)
            except psutil.NoSuchProcess:
                continue
            except psutil.Error:
                unverified_pids.add(candidate.pid)
    _, survivors = psutil.wait_procs(forced, timeout=5)
    # Reap the actual Popen child even when psutil performed the signal/wait.
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        unverified_pids.add(process.pid)
    surviving_pids = sorted({candidate.pid for candidate in survivors} | unverified_pids)
    if surviving_pids:
        raise RuntimeError(f"Could not confirm server cleanup for owned process IDs: {surviving_pids}")
    return {"tracked_process_count": len(identities), "skipped_reused_pids": sorted(skipped_reused_pids)}


def run_owned_preparation(command, *, cwd, timeout_seconds=900):
    """Run preparation in the foreground, retaining identities for bounded cleanup.

    Standard streams are inherited. One-second waits keep descendant ownership
    current without starting a supervisor or detaching the preparation command.
    """
    import psutil
    process = subprocess.Popen(command, cwd=cwd)
    root_identity = None
    observed_identities = {}
    deadline = time.monotonic() + timeout_seconds
    try:
        try:
            owned_root = psutil.Process(process.pid)
            root_identity = (process.pid, float(owned_root.create_time()))
        except psutil.NoSuchProcess:
            # A very short successful command can exit before identity capture.
            return_code = process.poll()
            if return_code is None:
                raise
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, command)
            return return_code
        observed_identities[root_identity[0]] = root_identity[1]
        while True:
            for process_id, created_at in tuple(observed_identities.items()):
                try:
                    owned_process = psutil.Process(process_id)
                    if float(owned_process.create_time()) != created_at:
                        continue
                    for descendant in owned_process.children(recursive=True):
                        try:
                            observed_identities[descendant.pid] = float(descendant.create_time())
                        except psutil.NoSuchProcess:
                            continue
                except psutil.NoSuchProcess:
                    continue
            return_code = process.poll()
            if return_code is not None:
                break
            remaining_seconds = deadline - time.monotonic()
            if remaining_seconds <= 0:
                raise subprocess.TimeoutExpired(command, timeout_seconds)
            try:
                return_code = process.wait(timeout=min(1.0, remaining_seconds))
                break
            except subprocess.TimeoutExpired:
                continue
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, command)
        return return_code
    finally:
        original_exception = sys.exc_info()[1]
        previous_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            if root_identity is not None or process.poll() is None:
                terminate_owned_process(process, root_identity, tuple(observed_identities.items()))
        except BaseException as exception:
            if original_exception is None:
                raise
            print(f"Additional preparation cleanup error: {type(exception).__name__}: {exception}", file=sys.stderr, flush=True)
        finally:
            signal.signal(signal.SIGINT, previous_sigint)


async def wait_for_tasks_bounded(tasks, *, timeout_seconds, cancel=False):
    """Retrieve task outcomes without letting one stuck cancellation block cleanup."""
    tasks = set(tasks)
    if cancel:
        for task in tasks:
            if not task.done():
                task.cancel()
    if not tasks:
        return [], set()
    done, pending = await asyncio.wait(tasks, timeout=timeout_seconds)
    timed_out_count = len(pending)
    if pending:
        for task in pending:
            task.cancel()
        cancelled, pending = await asyncio.wait(pending, timeout=2)
        done.update(cancelled)
    errors = ([TimeoutError(f"{timed_out_count} tasks exceeded the {timeout_seconds:g}-second cleanup wait")]
              if timed_out_count else [])
    for task in done:
        if not task.cancelled():
            exception = task.exception()
            if exception is not None:
                errors.append(exception)
    return errors, pending


def run_with_interrupt_cleanup(async_operation, *, final_cleanup=None):
    """Run one experiment with cooperative, repeat-safe SIGINT handling on 3.10.

    The first Ctrl+C cancels the main task. Further Ctrl+C events never interrupt
    bounded resource cleanup or close its running event loop underneath it.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_task = loop.create_task(async_operation(), name="load-test-experiment")
    previous_sigint = signal.getsignal(signal.SIGINT)
    was_interrupted = False
    repeated_notice_sent = False
    primary_exception = None
    primary_traceback = None
    result = None

    def request_interrupt(_signal_number, _frame):
        nonlocal was_interrupted, repeated_notice_sent
        if not was_interrupted:
            was_interrupted = True
            print("Interrupt requested; cancelling users and preserving partial results. Waiting for bounded cleanup.", flush=True)
            if not main_task.done():
                loop.call_soon_threadsafe(main_task.cancel)
        elif not repeated_notice_sent:
            repeated_notice_sent = True
            print("Cleanup is still running; repeated Ctrl+C will not close its event loop.", flush=True)

    signal.signal(signal.SIGINT, request_interrupt)
    try:
        try:
            result = loop.run_until_complete(main_task)
        except BaseException as exception:
            primary_exception = exception
            primary_traceback = exception.__traceback__
        finally:
            try:
                remaining = {task for task in asyncio.all_tasks(loop) if not task.done()}
                if remaining:
                    errors, pending = loop.run_until_complete(wait_for_tasks_bounded(
                        remaining, timeout_seconds=5, cancel=True,
                    ))
                    if pending:
                        raise RuntimeError(f"{len(pending)} asynchronous tasks did not finish during bounded loop cleanup")
                    for exception in errors:
                        print(f"Additional task cleanup error: {type(exception).__name__}: {exception}", file=sys.stderr)
                loop.run_until_complete(loop.shutdown_asyncgens())
            except BaseException as exception:
                if primary_exception is None:
                    primary_exception, primary_traceback = exception, exception.__traceback__
                else:
                    print(f"Additional loop cleanup error: {type(exception).__name__}: {exception}", file=sys.stderr)
            finally:
                try:
                    if final_cleanup is not None:
                        final_cleanup()
                except BaseException as exception:
                    if primary_exception is None:
                        primary_exception, primary_traceback = exception, exception.__traceback__
                    else:
                        print(f"Additional process cleanup error: {type(exception).__name__}: {exception}", file=sys.stderr)
    finally:
        loop.close()
        asyncio.set_event_loop(None)
        signal.signal(signal.SIGINT, previous_sigint)
    if was_interrupted and (primary_exception is None or isinstance(primary_exception, asyncio.CancelledError)):
        raise KeyboardInterrupt("Interrupted by the operator after resource cleanup")
    if primary_exception is not None:
        raise primary_exception.with_traceback(primary_traceback)
    return result


async def wait_for_server(process, port, timeout_seconds):
    import urllib.request
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Dedicated server exited with code {process.returncode}; see server.log")
        try:
            def probe():
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=2) as response:
                    return response.status == 200
            if await asyncio.to_thread(probe):
                return
        except OSError:
            pass
        await asyncio.sleep(0.5)
    raise TimeoutError("Dedicated server health endpoint did not become ready")


class Experiment:
    def __init__(self, arguments, output, scenarios):
        self.arguments = arguments
        self.output = output
        self.scenarios = scenarios
        self.phase = "startup"
        self.active_users = 0
        self.samples = []
        self.actions = []
        self.failures = []
        self.sessions = []
        self.monitor_stop = asyncio.Event()
        self.started_at = utc_now()
        self.interaction_started_at = None
        self.interaction_finished_at = None
        self.console_error_count = 0

    def event(self, user, action, status, duration_seconds=0, **details):
        record = {"timestamp_utc": utc_now(), "phase": self.phase, "user": user,
                  "action": action, "status": status,
                  "duration_seconds": round(duration_seconds, 4), **details}
        self.actions.append(record)
        with (self.output / "actions.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, default=str) + "\n")
        if status == "failed":
            self.failures.append(record)
        if status in {"failed", "unavailable"}:
            print(f"[{utc_now()}] {status.upper()} user={user} action={action}: "
                  f"{str(details.get('error', details.get('reason', 'See actions.jsonl')))[:2500]}",
                  flush=True)
        return record

    async def monitor(self, sampler):
        previous_progress = 0.0
        with (self.output / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = None
            while not self.monitor_stop.is_set():
                sample = await asyncio.to_thread(sampler.sample, self.phase, self.active_users)
                sample["workload_users"] = sum(session.get("workload_running", False) for session in self.sessions)
                self.samples.append(sample)
                if writer is None:
                    writer = csv.DictWriter(stream, fieldnames=list(sample))
                    writer.writeheader()
                writer.writerow(sample)
                stream.flush()
                if time.monotonic() - previous_progress >= 30:
                    rss = sample.get("server_rss_bytes")
                    available = sample.get("system_available_ram_bytes")
                    print(f"[{utc_now()}] {self.phase}: users={self.active_users}; "
                          f"workload_users={sample['workload_users']}; "
                          f"server RSS={format_mib(rss)}; available={format_mib(available)}", flush=True)
                    previous_progress = time.monotonic()
                try:
                    await asyncio.wait_for(self.monitor_stop.wait(), self.arguments.sample_seconds)
                except asyncio.TimeoutError:
                    pass

    async def settle(self, page):
        """Wait for the latest expected run and a quiet, error-free rendered page."""
        session = next(session for session in self.sessions if session["page"] is page)
        deadline = time.monotonic() + self.arguments.action_timeout_seconds
        quiet_since = None
        quiet_script_start = None
        while True:
            self.raise_session_failure(session)
            rendered = await page.evaluate("""() => {
                const visible = el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
                const exception = Array.from(document.querySelectorAll('[data-testid="stException"]')).find(visible);
                return {
                    exception: exception ? exception.innerText : null,
                    running: Array.from(document.querySelectorAll('[data-testid="stStatusWidget"]'))
                        .some(el => visible(el) && /Running|Rerunning/i.test(el.innerText))
                };
            }""")
            if rendered["exception"]:
                raise RuntimeError(f"Application execution failed: {rendered['exception'][:2500]}")
            has_finished = (
                session["script_starts"] >= session["expected_script_start"]
                and session["finished_script_start"] == session["script_starts"]
                and session["last_script_status"] in (
                    "FINISHED_SUCCESSFULLY", "FINISHED_FRAGMENT_RUN_SUCCESSFULLY")
                and not session["script_is_running"] and not rendered["running"]
            )
            if has_finished:
                if quiet_since is None or quiet_script_start != session["script_starts"]:
                    quiet_since = time.monotonic()
                    quiet_script_start = session["script_starts"]
                elif time.monotonic() - quiet_since >= 0.25:
                    self.raise_session_failure(session)
                    return
            else:
                quiet_since = None
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Streamlit did not complete the expected browser action: {script_diagnostics(session)}")
            await asyncio.sleep(0.05)

    def raise_session_failure(self, session):
        if session["browser_errors"]:
            raise RuntimeError(f"Browser execution failed: {session['browser_errors'][-1]}")
        if session.get("protocol_error"):
            raise RuntimeError(session["protocol_error"])
        if session["page"].is_closed():
            raise RuntimeError("Browser page closed during the workload")

    async def run_guarded_action(self, session, operation):
        """Interrupt even a blocked DOM wait on a fatal browser/protocol error."""
        action_task = asyncio.create_task(operation())
        failure_task = asyncio.create_task(session["failure_event"].wait())
        try:
            completed, _ = await asyncio.wait(
                [action_task, failure_task], timeout=self.arguments.action_timeout_seconds,
                return_when=asyncio.FIRST_COMPLETED,
            )
            self.raise_session_failure(session)
            if action_task not in completed:
                raise TimeoutError(f"Browser action exceeded its deadline: {script_diagnostics(session)}")
            return await action_task
        finally:
            for task in (action_task, failure_task):
                if not task.done():
                    task.cancel()
            await asyncio.gather(action_task, failure_task, return_exceptions=True)

    async def wait_for_initial_results(self, session):
        """Reject visible application failures while waiting for a real result."""
        page = session["page"]
        started = time.monotonic()
        deadline = started + self.arguments.startup_timeout_seconds
        next_progress = started
        result_button = page.get_by_role(
            "button", name=re.compile(r"Prepare All Results for Download$")).first
        while True:
            if page.is_closed():
                raise RuntimeError("Browser page closed before the initial analysis completed")
            if session["browser_errors"]:
                raise RuntimeError(f"Browser error during initial analysis: {session['browser_errors'][-1]}")
            if session.get("protocol_error"):
                raise RuntimeError(session["protocol_error"])
            exception = page.locator('[data-testid="stException"]').first
            if await exception.is_visible():
                message = await exception.inner_text(timeout=5000)
                raise RuntimeError(f"Application failed during initial analysis: {message[:2500]}. See server.log.")
            if await result_button.is_visible():
                return
            now = time.monotonic()
            if now >= deadline:
                raise TimeoutError(
                    f"User {session['user']} ({session['scenario']}) did not obtain initial results "
                    f"within {self.arguments.startup_timeout_seconds:g} seconds. See server.log "
                    "and the initial_analysis failure screenshot. The interaction timer has not started."
                )
            if now >= next_progress:
                print(f"[{utc_now()}] Waiting for user {session['user']} initial results "
                      f"({session['scenario']}, {now - started:.0f}s); "
                      "interaction timer has not started.", flush=True)
                next_progress = now + 30
            await asyncio.sleep(min(0.25, deadline - now))

    async def initialise_user(self, browser, port, user):
        from streamlit.proto.ForwardMsg_pb2 import ForwardMsg

        scenario = self.scenarios[user % len(self.scenarios)]
        context = await browser.new_context(viewport={"width": 1440, "height": 1000},
                                            accept_downloads=True)
        page = await context.new_page()
        page.set_default_timeout(self.arguments.action_timeout_seconds * 1000)
        session = {"user": user + 1, "scenario": scenario["id"], "context": context,
                   "page": page, "export_verified": False,
                   "script_starts": 0, "expected_script_start": 1, "finished_script_start": 0,
                   "script_run_id": None, "script_fragment_ids": [], "last_script_status": None,
                   "protocol_error": None, "failure_event": asyncio.Event(), "action_phase": "initial_analysis",
                   "action_details": {}, "ui_trace": None,
                   "workload_running": False,
                   "closing": False,
                   "script_is_running": False, "browser_errors": [],
                   "configuration": json.loads((self.output / scenario["config_path"]).read_text(encoding="utf-8"))["settings"]}
        if getattr(self.arguments, "trace_ui_deltas", False):
            from ui_trace import UITrace
            session["ui_trace"] = UITrace()
        self.sessions.append(session)
        def observe_frame(payload):
            # Observe real browser traffic only. Completion acknowledgements are
            # required so a fast click cannot overtake an in-flight fragment.
            if not isinstance(payload, bytes):
                return
            message = ForwardMsg()
            message.ParseFromString(payload)
            message_type = message.WhichOneof("type")
            if message_type in {"new_session", "script_finished", "session_status_changed"}:
                previous_protocol_error = session["protocol_error"]
                observe_script_message(session, message)
                if session["protocol_error"] and not previous_protocol_error:
                    self.event(user + 1, "script_protocol_error", "failed", error=session["protocol_error"])
                with (self.output / "script_events.jsonl").open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps({"timestamp_utc": utc_now(), "user": user + 1,
                                             "message": message_type, **script_diagnostics(session)}) + "\n")
            if session["ui_trace"] is not None:
                session["ui_trace"].observe(
                    message, script_run_id=session["script_run_id"],
                    fragment_ids=session["script_fragment_ids"], action_phase=session["action_phase"],
                )
        def observe_sent_frame(payload):
            if session["ui_trace"] is None or not isinstance(payload, bytes):
                return
            from streamlit.proto.BackMsg_pb2 import BackMsg
            message = BackMsg()
            message.ParseFromString(payload)
            session["ui_trace"].observe_back_message(
                message, script_run_id=session["script_run_id"],
                fragment_ids=session["script_fragment_ids"], action_phase=session["action_phase"],
            )

        def observe_websocket(websocket):
            websocket.on("framereceived", observe_frame)
            if session["ui_trace"] is not None:
                websocket.on("framesent", observe_sent_frame)
        page.on("websocket", observe_websocket)
        def observe_page_error(error):
            session["browser_errors"].append(str(error))
            session["failure_event"].set()
            self.event(user + 1, "browser_page_error", "failed", error=str(error))
            if session["ui_trace"] is not None:
                # Snapshot synchronously at the error, before queued replacement
                # runs or cleanup can obscure the original structural transition.
                write_json(self.output / f"user-{user + 1:02d}-browser-error-{len(session['browser_errors']):03d}-ui.json", {
                    "error": str(error), "stack": str(getattr(error, "stack", ""))[:16000],
                    "script": script_diagnostics(session), "trace": session["ui_trace"].snapshot(),
                })
        page.on("pageerror", observe_page_error)
        def observe_page_close():
            session["failure_event"].set()
            if not session["closing"]:
                self.event(user + 1, "browser_page_closed", "failed",
                           error="The browser page closed before harness cleanup")
        page.on("close", observe_page_close)
        started = time.monotonic()
        try:
            await page.goto(f"http://127.0.0.1:{port}/?{scenario['query_string']}", wait_until="domcontentloaded")
            await self.wait_for_initial_results(session)
            await self.settle(page)
            initial_scope = await self.verify_initial_scope(page)
            self.active_users += 1
            self.event(user + 1, "initial_analysis", "ok", time.monotonic() - started,
                       scenario=scenario["id"], initial_scope=initial_scope)
        except Exception as exc:
            self.event(user + 1, "initial_analysis", "failed", time.monotonic() - started,
                       scenario=scenario["id"], error=str(exc))
            await self.capture_failure(session, "initial_analysis")
            raise

    async def capture_failure(self, session, action):
        stem = f"user-{session['user']:02d}-{action}-{len(self.failures):03d}"
        write_json(self.output / f"{stem}-script.json", script_diagnostics(session))
        if session.get("ui_trace") is not None:
            write_json(self.output / f"{stem}-ui.json", session["ui_trace"].snapshot())
        with contextlib.suppress(Exception):
            await session["page"].screenshot(path=str(self.output / f"{stem}.png"), full_page=False, timeout=10000)
        with contextlib.suppress(Exception):
            text = await session["page"].locator("body").inner_text(timeout=10000)
            (self.output / f"{stem}.txt").write_text(text, encoding="utf-8")
        with contextlib.suppress(Exception):
            widgets = await session["page"].locator(
                'button, [role="radio"], [role="combobox"], [role="option"], [role="listbox"]'
            ).evaluate_all("""elements => elements.map(element => ({
                tag: element.tagName, text: element.innerText,
                visible: !!(element.offsetWidth || element.offsetHeight || element.getClientRects().length),
                attributes: Object.fromEntries(Array.from(element.attributes)
                    .filter(attribute => /^(id|role|class|kind|data-|aria-)/.test(attribute.name))
                    .map(attribute => [attribute.name, attribute.value]))
            }))""")
            write_json(self.output / f"{stem}-widgets.json", widgets)

    async def verify_initial_scope(self, page):
        """Require the replay's broad initial scope before counting a ready user."""
        panel = page.locator('[class*="st-key-results_evidence_level_2_"]').first
        selections = [text.strip() for text in await panel.locator(
            '[data-testid="stMultiSelect"]').all_inner_texts()]
        scope_summary = await panel.locator('.result-scope-summary > p').first.inner_text()
        expected_selections = ["Full Range", "All Directions"]
        expected_summary = "Active scope · Full Range · All Directions"
        if selections != expected_selections or scope_summary != expected_summary:
            raise RuntimeError(
                "Initial results did not retain Full Range and All Directions; "
                f"observed selections={str(selections)[:500]!r}; active scope={scope_summary[:250]!r}"
            )
        return {"selections": selections, "active_scope": scope_summary}

    async def change_time_bin(self, session, iteration):
        page = session["page"]
        successful_changes = session.get("successful_time_bin_actions", 0)
        panel_name, level = (("segment_inspector", 2) if successful_changes % 2 == 0
                             else ("selected_station", 4))
        # Alternate the two evidence views and exclude the input editor. A
        # missing selected-station control must not silently become a scope bin.
        panel = page.locator(f'[class*="st-key-results_evidence_level_{level}_"]').first
        controls = panel.locator('button, [role="radio"]').filter(
            has_text=re.compile(r"^\d+(?:m|h)$"))
        count = await controls.count()
        if count == 0:
            return "unavailable", {"reason": f"No time-bin buttons in {panel_name}", "panel": panel_name}
        candidates = []
        for index in range(count):
            candidate = controls.nth(index)
            if await candidate.is_visible() and await candidate.is_enabled():
                if await candidate.evaluate(BUTTON_SELECTION_JAVASCRIPT) is False:
                    candidates.append(index)
        if not candidates:
            return "unavailable", {"reason": "No inactive time-bin button with a readable selection state; see widget diagnostics", "panel": panel_name}
        control = controls.nth(candidates[iteration % len(candidates)])
        choice = (await control.inner_text()).strip()
        expect_script_run(session, "time_bin")
        await control.click()
        await self.settle(page)
        if await control.evaluate(BUTTON_SELECTION_JAVASCRIPT) is not True:
            raise RuntimeError(f"Time-bin button {choice!r} did not become selected after the application completed")
        session["successful_time_bin_actions"] = successful_changes + 1
        return "ok", {"choice": choice, "control_count": count, "panel": panel_name}

    async def change_station(self, session, iteration):
        page = session["page"]
        panel = page.locator('[class*="st-key-results_evidence_level_3_"]').first
        canvas = panel.locator('canvas[data-testid="data-grid-canvas"]').first
        if await canvas.count() == 0:
            return "unavailable", {"reason": "No Station Insights table"}
        rows = canvas.locator('tbody tr')
        count = min(await rows.count(), 5)
        if count == 0:
            return "unavailable", {"reason": "No visible station rows"}
        details = page.locator('[class*="st-key-results_evidence_level_4_"]').first
        before = await details.inner_text() if await details.count() else ""
        index = iteration % count
        for offset in range(count):
            index = (iteration + offset) % count
            callsign = await rows.nth(index).locator('td').first.inner_text()
            if callsign not in before:
                break
        else:
            return "unavailable", {"reason": "Visible station rows are already selected"}
        await canvas.scroll_into_view_if_needed()
        bounds = await canvas.bounding_box()
        # Streamlit's Glide scroller overlays its canvas. Dispatch a real mouse
        # click at the row marker through that overlay; no widget state injection.
        # The repository's compact table uses a 35px header and 35px rows.
        expect_script_run(session, "station")
        await page.mouse.click(bounds["x"] + 17, bounds["y"] + 35 * (index + 1.5))
        await self.settle(page)
        await page.wait_for_function("""({callsign, before}) => {
            const el = document.querySelector('[class*="st-key-results_evidence_level_4_"]');
            return el && el.innerText !== before && el.innerText.includes(callsign);
        }""", arg={"callsign": callsign, "before": before})
        await self.settle(page)
        return "ok", {"choice": callsign, "visible_row": index}

    async def change_scope(self, session, iteration):
        page = session["page"]
        panel = page.locator('[class*="st-key-results_evidence_level_2_"]').first
        widgets = panel.locator('[data-testid="stMultiSelect"]')
        if await widgets.count() == 0:
            return "unavailable", {"reason": "No scope multiselect in the Segment Inspector"}
        widget = widgets.nth(iteration % await widgets.count())
        control = widget.get_by_role("combobox").first
        previous_selection = (await widget.inner_text()).strip()
        scope_summary = panel.locator('.result-scope-summary > p').first
        previous_scope = await scope_summary.inner_text()
        # Use the combobox's keyboard-open action instead of relying on the
        # version-dependent interaction between pointer clicks and focus.
        await control.focus()
        if await control.get_attribute("aria-expanded") != "true":
            await control.press("ArrowDown")
        options = page.locator('[role="option"]:visible')
        await options.first.wait_for(state="visible", timeout=10000)
        labels = await options.all_text_contents()
        candidates = []
        for index, option_label in enumerate(labels):
            option = options.nth(index)
            if (option_label.strip() and not is_bulk_scope_option(option_label.strip())
                    and option_label.strip() not in previous_selection):
                if (await option.get_attribute("aria-disabled") != "true"
                        and await option.get_attribute("aria-selected") != "true"):
                    candidates.append(index)
        if not candidates:
            await page.keyboard.press("Escape")
            return "unavailable", {"reason": "Scope has no alternative option"}
        index = candidates[iteration % len(candidates)]
        label = labels[index].strip()
        session["action_details"] = {
            "scope_option": label, "previous_selection": previous_selection[:1000],
            "previous_scope": previous_scope[:1000],
        }
        expect_script_run(session, "scope")
        await options.nth(index).click()
        await page.keyboard.press("Escape")
        await self.settle(page)
        selected_text = (await widget.inner_text()).strip()
        selected_scope = await scope_summary.inner_text()
        session["action_details"].update({
            "observed_selection": selected_text[:1000],
            "observed_scope": selected_scope[:1000],
        })
        if selected_text == previous_selection or label not in selected_text or selected_scope == previous_scope:
            raise RuntimeError(
                f"Scope option {label!r} did not change both the selected values and active scope; "
                f"observed selection={selected_text[:250]!r}; active scope={selected_scope[:250]!r}"
            )
        return "ok", {"choice": label}

    async def export(self, session):
        page = session["page"]
        prepare = page.get_by_role("button", name=re.compile(r"Prepare All Results for Download$"))
        if await prepare.count() and await prepare.first.is_visible():
            expect_script_run(session, "export_prepare")
            await prepare.first.click()
            await self.settle(page)
        download = page.get_by_role("button", name=re.compile(r"Download Prepared Results$")).first
        await download.wait_for(state="visible", timeout=self.arguments.startup_timeout_seconds * 1000)
        await self.settle(page)
        # Both production download buttons use Streamlit's default on_click="rerun".
        # This is a separate run from preparing the archive, including on reuse.
        expect_script_run(session, "export_download")
        async with page.expect_download(timeout=self.arguments.action_timeout_seconds * 1000) as pending:
            await download.click()
        artifact = await pending.value
        await self.settle(page)
        path = self.output / "downloads" / f"user-{session['user']:02d}.zip"
        path.parent.mkdir(exist_ok=True)
        await artifact.save_as(str(path))
        with zipfile.ZipFile(path) as package:
            names = package.namelist()
            metadata_names = [name for name in names if name.endswith("run_metadata.json")]
            if len(metadata_names) != 1:
                raise RuntimeError("Downloaded ZIP has no run_metadata.json")
            if package.testzip() is not None:
                raise RuntimeError("Downloaded ZIP failed CRC verification")
            metadata = json.loads(package.read(metadata_names[0]))
            core = session["configuration"]["core_parameters"]
            comparison = session["configuration"]["comparison_parameters"]
            expected = {"callsign": core["callsign"], "band": core["band"],
                        "run_mode": core["analysis_direction"].upper(),
                        "reference_or_benchmark_mode": comparison["mode"],
                        "time_window": core["time_selection"]}
            for key, expected_value in expected.items():
                if metadata.get(key) != expected_value:
                    raise RuntimeError(f"Export scenario mismatch for {key}: {metadata.get(key)!r} != {expected_value!r}")
        session["export_verified"] = True
        await self.settle(page)
        return "ok", {"download_bytes": path.stat().st_size, "zip_entries": len(names)}

    async def perform_action(self, session, action, iteration):
        started = time.monotonic()
        session["action_phase"] = f"before_{action}"
        session["action_details"] = {}

        async def operation():
            await self.settle(session["page"])
            if action == "time_bin":
                status, details = await self.change_time_bin(session, iteration)
            elif action == "station":
                status, details = await self.change_station(session, iteration)
            elif action == "scope":
                status, details = await self.change_scope(session, iteration)
            elif action == "export":
                status, details = await self.export(session)
            else:
                drilldown = session["page"].get_by_text("Drill-Down Data", exact=True).first
                if await drilldown.count():
                    await drilldown.scroll_into_view_if_needed()
                    await self.settle(session["page"])
                    status, details = "ok", {}
                else:
                    status, details = "unavailable", {"reason": "No station is selected for Drill-Down"}
            self.raise_session_failure(session)
            return status, details

        try:
            self.raise_session_failure(session)
            status, details = await self.run_guarded_action(session, operation)
            self.event(session["user"], action, status, time.monotonic() - started, **details)
            if status == "unavailable":
                await self.capture_failure(session, action)
            return status
        except Exception as exc:
            self.event(session["user"], action, "failed", time.monotonic() - started,
                       error=str(exc), script=script_diagnostics(session))
            await self.capture_failure(session, action)
            return "failed"

    async def interact(self, session, deadline):
        session["workload_running"] = True
        workload_started = time.monotonic()
        rng = random.Random(self.arguments.seed + session["user"])
        actions = ("time_bin", "station", "drilldown")
        if getattr(self.arguments, "vary_scope", False):
            actions += ("scope",)
        actions *= 2
        iteration = 0
        scope_iteration = 3
        should_export = session["user"] <= getattr(self.arguments, "export_users", 0)
        export_attempted = False
        resumed_after_idle = False
        await asyncio.sleep(min(session["user"] * 0.4, max(0, deadline - time.monotonic())))
        while time.monotonic() < deadline:
            if should_export and not export_attempted and iteration >= len(actions):
                action = "export"
                export_attempted = True
            else:
                action = actions[iteration % len(actions)]
            action_iteration = scope_iteration if action == "scope" else iteration
            status = await self.perform_action(session, action, action_iteration)
            if resumed_after_idle:
                self.event(session["user"], "idle_resume", status,
                           idle_seconds=self.arguments.idle_seconds)
                resumed_after_idle = False
            if status == "failed":
                session["workload_running"] = False
                self.event(session["user"], "interaction_stopped", "failed",
                           reason="The session remains open for memory observation; no further actions are attempted.",
                           workload_seconds=time.monotonic() - workload_started,
                           remaining_seconds=max(0, deadline - time.monotonic()))
                return
            if action == "scope":
                scope_iteration += 1
            if action != "export":
                iteration += 1
            # Once per cycle, pause longer and then resume the same connected result.
            pause = self.arguments.think_seconds * rng.uniform(0.6, 1.4)
            if action != "export" and iteration % len(actions) == len(actions) // 2:
                pause = self.arguments.idle_seconds
                self.event(session["user"], "reading_pause", "ok", planned_seconds=round(pause, 2))
                resumed_after_idle = True
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(session["failure_event"].wait(),
                                       min(pause, max(0, deadline - time.monotonic())))
        session["workload_running"] = False
        try:
            self.raise_session_failure(session)
        except Exception as exc:
            self.event(session["user"], "interaction_stopped", "failed", error=str(exc),
                       workload_seconds=time.monotonic() - workload_started, remaining_seconds=0)
            await self.capture_failure(session, "interaction_end")

    def _record_cleanup_failure(self, operation, exception):
        detail = f"{type(exception).__name__}: {exception}"
        self._cleanup_failures.append(f"{operation}: {detail}")
        try:
            self.event(None, operation, "failed", error=detail)
        except Exception:
            print(f"Cleanup failure: {operation}: {detail}", file=sys.stderr, flush=True)

    async def _finish_cleanup_tasks(self, tasks, operation, *, timeout_seconds, cancel=False, report_errors=True):
        errors, pending = await wait_for_tasks_bounded(tasks, timeout_seconds=timeout_seconds, cancel=cancel)
        for exception in errors:
            if report_errors or isinstance(exception, TimeoutError):
                self._record_cleanup_failure(operation, exception)
        if pending:
            self._record_cleanup_failure(operation, TimeoutError(f"{len(pending)} tasks did not finish within bounded cleanup"))
        return pending

    async def _close_client_resources(self, user_tasks, browser, playwright_manager):
        # Cancellation must finish before a context is closed underneath a user.
        pending_users = await self._finish_cleanup_tasks(
            user_tasks, "user_task_cleanup", timeout_seconds=10, cancel=True, report_errors=False,
        )
        for session in self.sessions:
            session["closing"] = True
            if session.get("ui_trace") is not None:
                try:
                    write_json(self.output / f"user-{session['user']:02d}-ui-final.json", session["ui_trace"].snapshot())
                except Exception as exception:
                    self._record_cleanup_failure("ui_trace_capture", exception)
        context_closes = [asyncio.create_task(session["context"].close(), name=f"close-user-{session['user']}")
                          for session in self.sessions if session.get("context") is not None]
        await self._finish_cleanup_tasks(context_closes, "context_cleanup", timeout_seconds=10)
        self.active_users = 0
        for session in self.sessions:
            session["workload_running"] = False
        if browser is not None:
            await self._finish_cleanup_tasks(
                [asyncio.create_task(browser.close(), name="close-browser")],
                "browser_cleanup", timeout_seconds=10,
            )
        if playwright_manager is not None:
            await self._finish_cleanup_tasks(
                [asyncio.create_task(playwright_manager.__aexit__(None, None, None), name="stop-playwright")],
                "playwright_cleanup", timeout_seconds=10,
            )
        if pending_users:
            # Closing the transport releases requests that did not initially
            # respond to cancellation; still retrieve every user task outcome.
            await self._finish_cleanup_tasks(
                pending_users, "user_task_cleanup_after_browser", timeout_seconds=5,
                cancel=True, report_errors=False,
            )

    def stop_owned_server(self):
        """Idempotent synchronous fallback; safe even when no event loop exists."""
        process = getattr(self, "_owned_server_process", None)
        if process is None or getattr(self, "_server_cleanup_complete", False):
            return
        observed_identities = ()
        sampler = getattr(self, "_metrics_sampler", None)
        if sampler is not None:
            try:
                observed_identities = sampler.process_identities("server")
            except Exception as exception:
                self._record_cleanup_failure("server_identity_snapshot", exception)
        cleanup = terminate_owned_process(process, self._owned_server_identity, observed_identities)
        self._server_cleanup_complete = True
        self.event(None, "server_cleanup", "ok", **cleanup)

    async def _finish_resources(self, client_cleanup_task, monitor_task):
        try:
            try:
                await client_cleanup_task
            except BaseException as exception:
                self._record_cleanup_failure("client_cleanup", exception)
            self.monitor_stop.set()
            if monitor_task is not None:
                await self._finish_cleanup_tasks([monitor_task], "monitor_cleanup", timeout_seconds=10)
        finally:
            try:
                # All ordinary async cleanup is now settled. No new loop task
                # or worker thread is needed to guarantee server termination.
                self.stop_owned_server()
            except BaseException as exception:
                self._record_cleanup_failure("server_cleanup", exception)

    async def execute(self):
        from playwright.async_api import async_playwright
        from metrics import ProcessMetricsSampler

        port = available_port()
        environment = os.environ.copy()
        environment["WSPRADAR_LOAD_TEST_DIR"] = str(self.output)
        environment["PYTHONUNBUFFERED"] = "1"
        environment["MPLBACKEND"] = "Agg"
        environment["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        manifest = json.loads((self.output / "scenarios.json").read_text(encoding="utf-8"))
        entrypoint = self.output / manifest.get("entrypoint", "runtime/streamlit_app.py")
        command = [sys.executable, "-u", "-m", "streamlit", "run", str(entrypoint),
                   "--server.address=127.0.0.1", f"--server.port={port}", "--server.headless=true",
                   "--server.fileWatcherType=none", "--server.runOnSave=false",
                   "--browser.gatherUsageStats=false"]
        monitor_task = None
        user_tasks = []
        browser = None
        playwright_manager = None
        client_cleanup_task = None
        primary_exception = None
        self._cleanup_failures = []
        with (self.output / "server.log").open("w", encoding="utf-8") as server_log:
            process = subprocess.Popen(command, cwd=REPOSITORY, env=environment,
                                       stdout=server_log, stderr=subprocess.STDOUT)
            self._owned_server_process = process
            self._owned_server_identity = None
            self._metrics_sampler = None
            self._server_cleanup_complete = False
            try:
                import psutil
                owned_server = psutil.Process(process.pid)
                self._owned_server_identity = (process.pid, float(owned_server.create_time()))
                sampler = ProcessMetricsSampler(process.pid, [os.getpid()], self.output / "cache")
                self._metrics_sampler = sampler
                write_json(self.output / "system.json", sampler.system_metadata())
                monitor_task = asyncio.create_task(self.monitor(sampler))
                await wait_for_server(process, port, self.arguments.startup_timeout_seconds)
                self.phase = "baseline"
                await asyncio.sleep(self.arguments.baseline_seconds)
                playwright_manager = async_playwright()
                playwright = await playwright_manager.start()
                # The foreground harness owns cooperative SIGINT cleanup. The
                # browser's independent default handler races context.close().
                launch_options = {"headless": True, "handle_sigint": False}
                if self.arguments.browser_channel:
                    launch_options["channel"] = self.arguments.browser_channel
                browser = await playwright.chromium.launch(**launch_options)
                write_json(self.output / "browser.json", {"version": browser.version,
                           "channel": self.arguments.browser_channel or "playwright-chromium"})
                self.phase = "ramp_up"
                # Keep every task handle even if interruption happens while the
                # next arrival is being staggered.
                for user in range(self.arguments.users):
                    user_tasks.append(asyncio.create_task(
                        self.initialise_user(browser, port, user), name=f"initialise-user-{user + 1}",
                    ))
                    await asyncio.sleep(1)
                outcomes = await asyncio.gather(*user_tasks, return_exceptions=True)
                if any(isinstance(outcome, BaseException) for outcome in outcomes):
                    raise RuntimeError("At least one user failed to obtain results; interaction test was not started")
                self.phase = "interaction"
                self.interaction_started_at = utc_now()
                deadline = time.monotonic() + self.arguments.duration_seconds
                interaction_tasks = [asyncio.create_task(self.interact(session, deadline), name=f"interact-user-{session['user']}")
                                     for session in self.sessions]
                user_tasks.extend(interaction_tasks)
                await asyncio.gather(*interaction_tasks)
                self.interaction_finished_at = utc_now()
                self.phase = "connected_idle"
                await asyncio.sleep(max(self.arguments.sample_seconds, 2))
                client_cleanup_task = asyncio.create_task(
                    self._close_client_resources(user_tasks, browser, playwright_manager), name="close-clients",
                )
                await asyncio.shield(client_cleanup_task)
                if self._cleanup_failures:
                    raise RuntimeError("Client cleanup was incomplete; see cleanup events in actions.jsonl")
                self.phase = "recovery"
                await asyncio.sleep(self.arguments.cooldown_seconds)
            except BaseException as exception:
                primary_exception = exception
                raise
            finally:
                if client_cleanup_task is None:
                    client_cleanup_task = asyncio.create_task(
                        self._close_client_resources(user_tasks, browser, playwright_manager), name="close-clients",
                    )
                cleanup_task = asyncio.create_task(self._finish_resources(client_cleanup_task, monitor_task), name="finish-resources")
                try:
                    await asyncio.shield(cleanup_task)
                except asyncio.CancelledError:
                    # The signal runner never issues a second cancellation.
                    await cleanup_task
                    if primary_exception is None:
                        raise
                if primary_exception is None and self._cleanup_failures:
                    raise RuntimeError("Resource cleanup was incomplete; see cleanup events in actions.jsonl")


def format_mib(number):
    return "unavailable" if number is None else f"{number / 1024**2:.1f} MiB"


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, int((len(ordered) - 1) * fraction + 0.5)))]


def build_summary(experiment, fatal_error):
    """Require complete workload and measurement evidence before reporting a pass."""
    import math

    def valid_number(number, *, positive=False):
        return (not isinstance(number, bool) and isinstance(number, (int, float))
                and math.isfinite(number) and (number > 0 if positive else number >= 0))

    samples = experiment.samples
    phases = {}
    for phase in dict.fromkeys(sample.get("phase", "unknown") for sample in samples):
        rows = [sample for sample in samples if sample.get("phase", "unknown") == phase]
        fields = {}
        for key in ("server_rss_bytes", "server_private_bytes", "server_uss_bytes",
                    "generator_rss_bytes", "generator_private_bytes", "generator_uss_bytes",
                    "system_available_ram_bytes", "cache_artifact_bytes", "disk_free_bytes",
                    "cgroup_memory_current_bytes", "cgroup_memory_max_bytes"):
            values = [row[key] for row in rows if valid_number(row.get(key))]
            fields[key] = {"first": values[0], "last": values[-1], "min": min(values),
                           "max": max(values), "median": statistics.median(values)} if values else None
        phases[phase] = {"sample_count": len(rows), **fields}
    action_summaries = {}
    for action in sorted({row["action"] for row in experiment.actions}):
        rows = [row for row in experiment.actions if row["action"] == action]
        durations = [row["duration_seconds"] for row in rows
                     if row["status"] == "ok" and valid_number(row.get("duration_seconds"))]
        action_summaries[action] = {"successful": sum(row["status"] == "ok" for row in rows),
            "failed": sum(row["status"] == "failed" for row in rows),
            "unavailable": sum(row["status"] == "unavailable" for row in rows),
            "median_seconds": statistics.median(durations) if durations else None,
            "p95_seconds": percentile(durations, 0.95)}

    vary_scope = bool(getattr(experiment.arguments, "vary_scope", False))
    required_actions = ("initial_analysis", "time_bin", "station")
    if vary_scope:
        required_actions += ("scope",)
    required_actions += ("drilldown", "idle_resume")
    tracked_actions = ("initial_analysis", "time_bin", "station", "scope", "drilldown", "idle_resume", "export")
    required_time_bin_panels = ("segment_inspector", "selected_station")
    export_users = getattr(experiment.arguments, "export_users", 0)
    selected_export_users = list(range(1, export_users + 1))
    per_user_coverage = {}
    for user in range(1, experiment.arguments.users + 1):
        successful_actions = {row["action"] for row in experiment.actions
                              if row.get("user") == user and row.get("status") == "ok"}
        user_required_actions = (*required_actions, "export") if user <= export_users else required_actions
        user_coverage = {action: action in successful_actions for action in tracked_actions}
        successful_time_bin_panels = {row.get("panel") for row in experiment.actions
                                     if row.get("user") == user and row.get("action") == "time_bin"
                                     and row.get("status") == "ok"}
        time_bin_panels = {panel: panel in successful_time_bin_panels for panel in required_time_bin_panels}
        per_user_coverage[str(user)] = {
            "actions": user_coverage,
            "scope_required": vary_scope,
            "export_required": user <= export_users,
            "time_bin_panels": time_bin_panels,
            "missing_time_bin_panels": [panel for panel, complete in time_bin_panels.items() if not complete],
            "complete": (all(user_coverage[action] for action in user_required_actions)
                         and all(time_bin_panels.values())),
            "missing_actions": [action for action in user_required_actions if not user_coverage[action]],
        }
    coverage = {action: all(user["actions"][action] for user in per_user_coverage.values())
                for action in required_actions}
    coverage["time_bin"] = all(all(user["time_bin_panels"].values()) for user in per_user_coverage.values())
    successful_export_users = [user for user in selected_export_users
                               if per_user_coverage[str(user)]["actions"]["export"]]
    export_policy = {
        "requested_users": export_users,
        "selected_user_ids": selected_export_users,
        "maximum_exports_per_selected_user": 1,
        "successful_users": len(successful_export_users),
        "complete": len(successful_export_users) == export_users,
    }

    server_session_ids = set()
    completed_session_ids = set()
    checkpoint_parse_errors = 0
    log_path = experiment.output / "server.log"
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "LOAD_TEST_SESSION " in line:
                try:
                    record = json.loads(line.split("LOAD_TEST_SESSION ", 1)[1])
                    session_id = record.get("session_id")
                    if not isinstance(session_id, str) or not session_id.strip():
                        raise ValueError("Checkpoint has no session identity")
                    server_session_ids.add(session_id)
                    if record.get("phase") == "end" and record.get("has_completed_run") is True:
                        completed_session_ids.add(session_id)
                except (ValueError, TypeError, AttributeError):
                    checkpoint_parse_errors += 1
    sufficient_sessions = len(completed_session_ids) >= experiment.arguments.users

    required_phases = {"interaction": True,
                       "baseline": experiment.arguments.baseline_seconds > 0,
                       "recovery": experiment.arguments.cooldown_seconds > 0}
    requested_phase_durations = {"interaction": experiment.arguments.duration_seconds,
                                 "baseline": experiment.arguments.baseline_seconds,
                                 "recovery": experiment.arguments.cooldown_seconds}
    sampling_tolerance = max(2 * experiment.arguments.sample_seconds, 1.0)
    memory_coverage = {}
    for phase, is_required in required_phases.items():
        phase_samples = [sample for sample in samples if sample.get("phase") == phase]
        valid_samples = [sample for sample in phase_samples
                         if valid_number(sample.get("server_rss_bytes"), positive=True)
                         and valid_number(sample.get("generator_rss_bytes"))
                         and valid_number(sample.get("system_available_ram_bytes"))
                         and valid_number(sample.get("elapsed_seconds"))
                         and sample.get("server_discovery_complete") is True
                         and sample.get("generator_discovery_complete") is True]
        has_expected_users = (phase != "interaction" or any(
            sample.get("active_users") == experiment.arguments.users for sample in valid_samples))
        sample_times = [sample["elapsed_seconds"] for sample in valid_samples]
        gaps = [later - earlier for earlier, later in zip(sample_times, sample_times[1:])]
        observed_span = sample_times[-1] - sample_times[0] if sample_times else None
        minimum_span = max(0.0, requested_phase_durations[phase] - sampling_tolerance)
        cadence_complete = (observed_span is not None and observed_span >= minimum_span
                            and all(0 <= gap <= sampling_tolerance for gap in gaps))
        memory_coverage[phase] = {
            "required": is_required,
            "sample_count": len(phase_samples),
            "valid_memory_sample_count": len(valid_samples),
            "invalid_memory_sample_count": len(phase_samples) - len(valid_samples),
            "sampled_span_seconds": observed_span,
            "minimum_sampled_span_seconds": minimum_span,
            "maximum_gap_seconds": max(gaps, default=None),
            "sampling_tolerance_seconds": sampling_tolerance,
            "cadence_complete": cadence_complete,
            "requested_users_observed": has_expected_users if phase == "interaction" else None,
            "complete": not is_required or bool(phase_samples) and len(valid_samples) == len(phase_samples) and has_expected_users and cadence_complete,
        }
    diagnostic_counts = {}
    diagnostic_sample_count = 0
    for sample in samples:
        try:
            diagnostics = json.loads(sample.get("diagnostics", "[]"))
            if not isinstance(diagnostics, list) or not all(isinstance(entry, str) for entry in diagnostics):
                raise ValueError("Invalid diagnostic list")
        except (ValueError, TypeError):
            diagnostics = ["Invalid metric diagnostics encoding"]
        if diagnostics:
            diagnostic_sample_count += 1
        for diagnostic in set(diagnostics):
            diagnostic_counts[diagnostic] = diagnostic_counts.get(diagnostic, 0) + 1
    observed_seconds = None
    if experiment.interaction_started_at and experiment.interaction_finished_at:
        try:
            start = datetime.fromisoformat(experiment.interaction_started_at.replace("Z", "+00:00"))
            finish = datetime.fromisoformat(experiment.interaction_finished_at.replace("Z", "+00:00"))
            duration = (finish - start).total_seconds()
            if duration >= 0:
                observed_seconds = duration
        except (ValueError, TypeError):
            pass
    duration_complete = (observed_seconds is not None
                         and observed_seconds + 0.001 >= experiment.arguments.duration_seconds)
    failure_count = max(len(experiment.failures), sum(row.get("status") == "failed" for row in experiment.actions))
    incomplete_reasons = []
    if fatal_error:
        incomplete_reasons.append("The run ended with a fatal error.")
    if failure_count:
        incomplete_reasons.append(f"{failure_count} failed action or browser events were recorded.")
    if not sufficient_sessions:
        incomplete_reasons.append(f"Only {len(completed_session_ids)} unique server sessions recorded completed results; {experiment.arguments.users} required.")
    for user, user_coverage in per_user_coverage.items():
        if user_coverage["missing_actions"]:
            incomplete_reasons.append(f"User {user} is missing successful actions: {', '.join(user_coverage['missing_actions'])}.")
        if user_coverage["missing_time_bin_panels"]:
            incomplete_reasons.append(f"User {user} is missing successful time-bin changes in: {', '.join(user_coverage['missing_time_bin_panels'])}.")
    if not duration_complete:
        incomplete_reasons.append("The recorded completed interaction period is missing or shorter than requested.")
    for phase, phase_coverage in memory_coverage.items():
        if not phase_coverage["complete"]:
            incomplete_reasons.append(f"Memory evidence for {phase} is incomplete: {phase_coverage['valid_memory_sample_count']}/{phase_coverage['sample_count']} valid samples; sampled span {phase_coverage['sampled_span_seconds']} seconds; cadence complete: {phase_coverage['cadence_complete']}; requested users observed: {phase_coverage['requested_users_observed']}.")
    return {"schema_version": 2, "started_at": experiment.started_at, "finished_at": utc_now(),
            "interaction_started_at": experiment.interaction_started_at,
            "interaction_finished_at": experiment.interaction_finished_at,
            "requested_users": experiment.arguments.users,
            "server_session_count": len(server_session_ids),
            "completed_server_session_count": len(completed_session_ids),
            "session_count_verified": sufficient_sessions,
            "server_checkpoint_parse_errors": checkpoint_parse_errors,
            "requested_interaction_seconds": experiment.arguments.duration_seconds,
            "diagnostic_ui_tracing": bool(getattr(experiment.arguments, "trace_ui_deltas", False)),
            "observed_interaction_seconds": observed_seconds,
            "interaction_duration_verified": duration_complete,
            "fatal_error": fatal_error, "failure_count": failure_count,
            "status": "passed" if not incomplete_reasons else "incomplete_or_failed",
            "incomplete_reasons": incomplete_reasons,
            "required_actions_per_user": list(required_actions),
            "required_time_bin_panels_per_user": list(required_time_bin_panels),
            "scope_policy": {
                "vary_scope": vary_scope,
                "initial_selected_ranges": "all",
                "initial_selected_directions": "all",
            },
            "export_policy": export_policy,
            "per_user_coverage": per_user_coverage,
            "stopped_session_workloads": [row for row in experiment.actions
                                          if row["action"] == "interaction_stopped"],
            "action_coverage": coverage, "memory_coverage": memory_coverage,
            "metric_diagnostic_sample_count": diagnostic_sample_count,
            "metric_diagnostics": dict(sorted(diagnostic_counts.items())),
            "phases": phases, "actions": action_summaries,
            "limitations": ["Frozen offline provider query replay; upstream availability and SQL engine throughput are not tested.",
                "Browser generator and application share host CPU and memory; process groups are reported separately.",
                "This duration does not establish hour-scale retention, 100-user capacity or Community Cloud performance.",
                ("Scope changes are exercised; narrower selections can reduce the displayed evidence during this run."
                 if vary_scope else "Full Range and All Directions remain fixed; scope-changing controls are not exercised."),
                "Passed means required interactions and measurement coverage completed; it does not certify a memory ceiling or rule out memory leaks.",
                "Sampled RSS can miss brief peaks and double-count shared pages across processes; private committed bytes and USS have different meanings.",
                "Working-set changes and allocator-retained memory are not themselves proof of a leak or successful reclamation.",
                "Private bytes, USS and cgroup measurements may be unavailable; their diagnostics remain visible even when required RSS evidence is complete."]}


def write_report(output, summary):
    """Write a reviewable evidence report without deriving capacity or leak claims."""
    observed_duration = summary["observed_interaction_seconds"]
    observed_label = "unavailable" if observed_duration is None else f"{observed_duration:.2f}"
    lines = ["# WSPRadar multi-user baseline", "", f"Status: **{summary['status']}**", "",
             f"Requested users: {summary['requested_users']}; unique server sessions: {summary['server_session_count']}; sessions with completed results: {summary['completed_server_session_count']}.",
             f"Interaction period after initial results: requested {summary['requested_interaction_seconds']} seconds; observed {observed_label} seconds.", "",
             "A pass confirms workload and measurement coverage. It does not certify a safe memory ceiling or rule out leaks."]
    export_policy = summary["export_policy"]
    lines += ["", f"Exploration workload: {summary['requested_users']} users; users selected for one optional export after their first exploration cycle: {export_policy['requested_users']}; successful exports by selected users: {export_policy['successful_users']}."]
    if summary["scope_policy"]["vary_scope"]:
        lines += ["", "Scope policy: start with Full Range and All Directions, then exercise distance and direction changes (--vary-scope)."]
    else:
        lines += ["", "Scope policy: retain Full Range and All Directions throughout exploration. Scope changes are not requested or required for this run."]
    if summary["diagnostic_ui_tracing"]:
        lines += ["", "UI structural tracing was enabled. Its instrumentation overhead makes this a diagnostic run, not an ordinary memory baseline."]
    if summary["incomplete_reasons"]:
        lines += ["", "## Incomplete evidence or failures", ""]
        lines += [f"- {reason}" for reason in summary["incomplete_reasons"]]
    lines += ["", "## Memory by phase", "",
              "RSS is resident process memory. Windows private bytes include private committed pages outside RAM; USS measures resident pages unique to a process. Values are sums over the recorded process tree.", "",
              "| Phase | Server RSS median / max | Private max | USS max | Generator RSS max | Available RAM min | Samples |",
              "| --- | --- | --- | --- | --- | --- | ---: |"]
    for phase, measurements in summary["phases"].items():
        server = measurements.get("server_rss_bytes") or {}
        private = measurements.get("server_private_bytes") or {}
        unique = measurements.get("server_uss_bytes") or {}
        generator = measurements.get("generator_rss_bytes") or {}
        available = measurements.get("system_available_ram_bytes") or {}
        lines.append(f"| {phase} | {format_mib(server.get('median'))} / {format_mib(server.get('max'))} | {format_mib(private.get('max'))} | {format_mib(unique.get('max'))} | {format_mib(generator.get('max'))} | {format_mib(available.get('min'))} | {measurements['sample_count']} |")
    lines += ["", "## Measurement coverage", "", "| Phase | Required | Valid / recorded memory samples | Sampled span / minimum seconds | Complete |",
              "| --- | --- | ---: | --- | --- |"]
    for phase, coverage in summary["memory_coverage"].items():
        lines.append(f"| {phase} | {coverage['required']} | {coverage['valid_memory_sample_count']} / {coverage['sample_count']} | {coverage['sampled_span_seconds']} / {coverage['minimum_sampled_span_seconds']} | {coverage['complete']} |")
    lines += ["", "## Coverage for each user", "", "| User | Initial run | Time bins (both panels) | Station | Scope | Export | Drill-down | Idle resume |",
              "| ---: | --- | --- | --- | --- | --- | --- | --- |"]
    for user, coverage in summary["per_user_coverage"].items():
        cells = []
        for action in ("initial_analysis", "time_bin", "station", "scope", "export", "drilldown", "idle_resume"):
            if ((action == "export" and not coverage["export_required"])
                    or (action == "scope" and not coverage["scope_required"])):
                cells.append("not requested")
            elif action == "time_bin":
                cells.append("ok" if all(coverage["time_bin_panels"].values()) else "missing")
            else:
                cells.append("ok" if coverage["actions"][action] else "missing")
        lines.append(f"| {user} | {' | '.join(cells)} |")
    lines += ["", "## Action timings", "", "| Action | Successful | Failed | Unavailable | Median / p95 seconds |",
              "| --- | ---: | ---: | ---: | --- |"]
    for action, counts in summary["actions"].items():
        lines.append(f"| {action} | {counts['successful']} | {counts['failed']} | {counts['unavailable']} | {counts['median_seconds']} / {counts['p95_seconds']} |")
    lines += ["", "## Measurement diagnostics", "",
              f"Samples with diagnostics: {summary['metric_diagnostic_sample_count']}; invalid server checkpoints: {summary['server_checkpoint_parse_errors']}."]
    if summary["metric_diagnostics"]:
        lines += ["", "| Diagnostic | Samples |", "| --- | ---: |"]
        for diagnostic, count in summary["metric_diagnostics"].items():
            safe_diagnostic = diagnostic.replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {safe_diagnostic} | {count} |")
    else:
        lines += ["", "No sampler diagnostics were recorded."]
    if summary["fatal_error"]:
        lines += ["", "## Run error", "", "```text", summary["fatal_error"], "```"]
    lines += ["", "## Interpretation limits", ""] + [f"- {text}" for text in summary["limitations"]]
    lines += ["", "The raw time series, action log, exact package versions and source hashes accompany this report.",
              "Unavailable required interactions make this run incomplete; they are never counted as successful activity.",
              "Prepared ZIP payloads and replay caches are retained locally but omitted from the portable report archive.", ""]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")


def archive_results(output):
    destination = output.with_suffix(".zip")
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output.iterdir()):
            if path.is_file() and path.suffix in {".json", ".jsonl", ".csv", ".md", ".log", ".png", ".txt"}:
                archive.write(path, f"{output.name}/{path.name}")
    return destination


def main(arguments=None):
    options = parse_arguments(arguments)
    output = create_output_directory(options.output)
    print(f"Output: {output}", flush=True)
    experiment = None
    fatal_error = None
    try:
        versions = version_record()
        write_json(output / "versions.json", versions)
        write_json(output / "arguments.json", vars(options))
        preflight = validate_source_syntax(versions["source_files"])
        write_json(output / "syntax_check.json", preflight)
        print(f"Source syntax check passed: {preflight['checked_python_files']} Python files "
              f"with Python {platform.python_version()}", flush=True)
        import psutil
        if not options.prepare_only:
            import playwright.async_api  # Fail before any child server is launched.
        available = psutil.virtual_memory().available
        print(f"Available host memory: {format_mib(available)}", flush=True)
        if available < 2 * 1024**3:
            print("WARNING: less than 2 GiB available. Memory pressure may distort timings; prefer --users 1 locally.", flush=True)
        run_owned_preparation([sys.executable, str(HARNESS_DIRECTORY / "replay.py"), "--prepare", str(output),
                               "--scenarios", options.scenarios, "--performance-replay", str(options.performance_replay)],
                              cwd=REPOSITORY, timeout_seconds=900)
        manifest = json.loads((output / "scenarios.json").read_text(encoding="utf-8"))
        requested = options.scenarios.split(",")
        indexed = {scenario["id"]: scenario for scenario in manifest["scenarios"]}
        if any(name not in indexed for name in requested):
            raise ValueError(f"Unknown scenarios; available: {', '.join(indexed)}")
        if options.prepare_only:
            print("Replay preparation complete. No server or browser was launched.", flush=True)
            return 0
        experiment = Experiment(options, output, [indexed[name] for name in requested])
        run_with_interrupt_cleanup(experiment.execute, final_cleanup=experiment.stop_owned_server)
    except KeyboardInterrupt:
        fatal_error = "Interrupted by the operator. Partial measurements are preserved."
    except Exception:
        fatal_error = traceback.format_exc()
        print(fatal_error, file=sys.stderr)
    finally:
        if experiment is not None:
            summary = build_summary(experiment, fatal_error)
            write_json(output / "summary.json", summary)
            write_report(output, summary)
            package = archive_results(output)
            print(f"Report: {output / 'report.md'}\nReturn this archive: {package}", flush=True)
        elif fatal_error:
            write_json(output / "setup_failure.json", {"error": fatal_error})
            print(f"Partial setup diagnostics: {archive_results(output)}", flush=True)
    return 1 if fatal_error or experiment is not None and summary["status"] != "passed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
