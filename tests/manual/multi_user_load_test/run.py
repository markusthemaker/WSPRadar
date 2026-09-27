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


def parse_arguments(arguments=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--users", type=int, default=10)
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
    parser.add_argument("--output", type=Path)
    parser.add_argument("--browser-channel", default=None,
                        help="Optional installed browser channel, e.g. msedge on Windows.")
    parser.add_argument("--prepare-only", action="store_true")
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
        if root_identity is not None or process.poll() is None:
            terminate_owned_process(process, root_identity, tuple(observed_identities.items()))


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
        return record

    async def monitor(self, sampler):
        previous_progress = 0.0
        with (self.output / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = None
            while not self.monitor_stop.is_set():
                sample = await asyncio.to_thread(sampler.sample, self.phase, self.active_users)
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
                          f"server RSS={format_mib(rss)}; available={format_mib(available)}", flush=True)
                    previous_progress = time.monotonic()
                try:
                    await asyncio.wait_for(self.monitor_stop.wait(), self.arguments.sample_seconds)
                except asyncio.TimeoutError:
                    pass

    async def settle(self, page):
        """Wait for the real Streamlit script to finish, then reject visible failures."""
        session = next(session for session in self.sessions if session["page"] is page)
        deadline = time.monotonic() + self.arguments.action_timeout_seconds
        while (session["script_completions"] < session["expected_completions"]
               or session["script_is_running"]):
            if time.monotonic() >= deadline:
                raise TimeoutError("Streamlit did not confirm script completion for the browser action")
            await asyncio.sleep(0.05)
        await page.wait_for_timeout(250)
        await page.wait_for_function("""() => {
            const visible = el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
            return !Array.from(document.querySelectorAll('[data-testid="stStatusWidget"]'))
                .some(el => visible(el) && /Running|Rerunning/i.test(el.innerText));
        }""", timeout=self.arguments.action_timeout_seconds * 1000)
        failures = page.locator('[data-testid="stException"]')
        if await failures.count():
            raise RuntimeError((await failures.first.inner_text())[:2500])

    async def initialise_user(self, browser, port, user):
        from streamlit.proto.ForwardMsg_pb2 import ForwardMsg

        scenario = self.scenarios[user % len(self.scenarios)]
        context = await browser.new_context(viewport={"width": 1440, "height": 1000},
                                            accept_downloads=True)
        page = await context.new_page()
        page.set_default_timeout(self.arguments.action_timeout_seconds * 1000)
        session = {"user": user + 1, "scenario": scenario["id"], "context": context,
                   "page": page, "export_verified": False,
                   "script_completions": 0, "expected_completions": 1,
                   "script_is_running": False,
                   "configuration": json.loads((self.output / scenario["config_path"]).read_text(encoding="utf-8"))["settings"]}
        self.sessions.append(session)
        def observe_frame(payload):
            # Observe real browser traffic only. Completion acknowledgements are
            # required so a fast click cannot overtake an in-flight fragment.
            if not isinstance(payload, bytes):
                return
            message = ForwardMsg()
            message.ParseFromString(payload)
            message_type = message.WhichOneof("type")
            if message_type == "script_finished":
                session["script_completions"] += 1
            elif message_type == "session_status_changed":
                session["script_is_running"] = message.session_status_changed.script_is_running
        page.on("websocket", lambda websocket: websocket.on("framereceived", observe_frame))
        page.on("pageerror", lambda error: self.event(user + 1, "browser_page_error", "failed", error=str(error)))
        started = time.monotonic()
        try:
            await page.goto(f"http://127.0.0.1:{port}/?{scenario['query_string']}", wait_until="domcontentloaded")
            await page.get_by_role("button", name=re.compile(r"Prepare All Results for Download$")).first.wait_for(
                state="visible", timeout=self.arguments.startup_timeout_seconds * 1000)
            await self.settle(page)
            self.active_users += 1
            self.event(user + 1, "initial_analysis", "ok", time.monotonic() - started,
                       scenario=scenario["id"])
        except Exception as exc:
            self.event(user + 1, "initial_analysis", "failed", time.monotonic() - started,
                       scenario=scenario["id"], error=str(exc))
            await self.capture_failure(session, "initial_analysis")
            raise

    async def capture_failure(self, session, action):
        stem = f"user-{session['user']:02d}-{action}-{len(self.failures):03d}"
        with contextlib.suppress(Exception):
            await session["page"].screenshot(path=str(self.output / f"{stem}.png"), full_page=False, timeout=10000)
        with contextlib.suppress(Exception):
            text = await session["page"].locator("body").inner_text(timeout=10000)
            (self.output / f"{stem}.txt").write_text(text, encoding="utf-8")

    async def change_time_bin(self, session, iteration):
        page = session["page"]
        # These are native segmented buttons, not dropdowns. Select a currently
        # inactive choice, and verify the widget's selected-state transition.
        controls = page.locator('button[kind="segmented_control"]').filter(
            has_text=re.compile(r"^(30m|1h|2h|3h|6h|12h|24h)$"))
        count = await controls.count()
        if count == 0:
            return "unavailable", {"reason": "No inactive time-bin button in the rendered result"}
        control = controls.nth(iteration % count)
        choice = await control.inner_text()
        # Confirm the selected-state transition using the visible label.
        occurrence = await page.get_by_role("button", name=choice, exact=True).count()
        before = await page.locator('button[kind="segmented_controlActive"]').all_text_contents()
        await control.click()
        await page.wait_for_function("""({choice, before}) => {
            const selected = Array.from(document.querySelectorAll('button[kind="segmented_controlActive"]')).map(el => el.innerText);
            return selected.includes(choice) && JSON.stringify(selected) !== JSON.stringify(before);
        }""", arg={"choice": choice, "before": before})
        await self.settle(page)
        return "ok", {"choice": choice, "matching_controls": occurrence}

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
        await page.mouse.click(bounds["x"] + 17, bounds["y"] + 35 * (index + 1.5))
        await page.wait_for_function("""({callsign, before}) => {
            const el = document.querySelector('[class*="st-key-results_evidence_level_4_"]');
            return el && el.innerText !== before && el.innerText.includes(callsign);
        }""", arg={"callsign": callsign, "before": before})
        await self.settle(page)
        return "ok", {"choice": callsign, "visible_row": index}

    async def change_scope(self, session, iteration):
        page = session["page"]
        controls = page.get_by_role("combobox", name=re.compile("Distance.*range|Direction|Distance.*scope", re.I))
        if await controls.count() == 0:
            return "unavailable", {"reason": "No matching scope combobox"}
        control = controls.nth(iteration % await controls.count())
        previous_label = await control.get_attribute("aria-label")
        await control.click()
        options = page.get_by_role("option")
        await options.first.wait_for(state="visible")
        count = await options.count()
        labels = await options.all_text_contents()
        if not count:
            await page.keyboard.press("Escape")
            return "unavailable", {"reason": "Scope has no selectable options"}
        candidates = [index for index, label in enumerate(labels) if label.strip() not in previous_label]
        if not candidates:
            await page.keyboard.press("Escape")
            return "unavailable", {"reason": "Scope has no alternative option"}
        index = candidates[iteration % len(candidates)]
        label = labels[index]
        await options.nth(index).click()
        await page.keyboard.press("Escape")
        await page.wait_for_function("""previous => !Array.from(document.querySelectorAll('[role="combobox"]'))
            .some(el => el.getAttribute('aria-label') === previous)""", arg=previous_label)
        await self.settle(page)
        return "ok", {"choice": label}

    async def export(self, session):
        page = session["page"]
        prepare = page.get_by_role("button", name=re.compile(r"Prepare All Results for Download$"))
        if await prepare.count() and await prepare.first.is_visible():
            await prepare.first.click()
        else:
            # Reusing a prepared download does not necessarily rerun Streamlit.
            session["expected_completions"] = session["script_completions"]
        download = page.get_by_role("button", name=re.compile(r"Download Prepared Results$")).first
        await download.wait_for(state="visible", timeout=self.arguments.startup_timeout_seconds * 1000)
        await self.settle(page)
        async with page.expect_download(timeout=self.arguments.action_timeout_seconds * 1000) as pending:
            await download.click()
        artifact = await pending.value
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
        session["expected_completions"] = session["script_completions"] + (action != "drilldown")
        try:
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
            self.event(session["user"], action, status, time.monotonic() - started, **details)
            if status == "unavailable":
                await self.capture_failure(session, action)
            return status
        except Exception as exc:
            self.event(session["user"], action, "failed", time.monotonic() - started, error=str(exc))
            await self.capture_failure(session, action)
            return "failed"

    async def interact(self, session, deadline):
        rng = random.Random(self.arguments.seed + session["user"])
        actions = ("time_bin", "station", "export", "scope", "time_bin", "station", "drilldown", "export")
        iteration = 0
        resumed_after_idle = False
        await asyncio.sleep(min(session["user"] * 0.4, max(0, deadline - time.monotonic())))
        while time.monotonic() < deadline:
            status = await self.perform_action(session, actions[iteration % len(actions)], iteration)
            if resumed_after_idle:
                self.event(session["user"], "idle_resume", status,
                           idle_seconds=self.arguments.idle_seconds)
                resumed_after_idle = False
            iteration += 1
            # Once per cycle, pause longer and then resume the same connected result.
            pause = self.arguments.think_seconds * rng.uniform(0.6, 1.4)
            if iteration % len(actions) == 4:
                pause = self.arguments.idle_seconds
                self.event(session["user"], "reading_pause", "ok", planned_seconds=round(pause, 2))
                resumed_after_idle = True
            await asyncio.sleep(min(pause, max(0, deadline - time.monotonic())))

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
        with (self.output / "server.log").open("w", encoding="utf-8") as server_log:
            process = subprocess.Popen(command, cwd=REPOSITORY, env=environment,
                                       stdout=server_log, stderr=subprocess.STDOUT)
            server_identity = None
            sampler = None
            try:
                import psutil
                owned_server = psutil.Process(process.pid)
                server_identity = (process.pid, float(owned_server.create_time()))
                sampler = ProcessMetricsSampler(process.pid, [os.getpid()], self.output / "cache")
                write_json(self.output / "system.json", sampler.system_metadata())
                monitor_task = asyncio.create_task(self.monitor(sampler))
                await wait_for_server(process, port, self.arguments.startup_timeout_seconds)
                self.phase = "baseline"
                await asyncio.sleep(self.arguments.baseline_seconds)
                async with async_playwright() as playwright:
                    launch_options = {"headless": True}
                    if self.arguments.browser_channel:
                        launch_options["channel"] = self.arguments.browser_channel
                    browser = await playwright.chromium.launch(**launch_options)
                    write_json(self.output / "browser.json", {"version": browser.version,
                               "channel": self.arguments.browser_channel or "playwright-chromium"})
                    try:
                        self.phase = "ramp_up"
                        # Stagger arrivals; actual analysis admission remains unchanged.
                        initialisation = []
                        for user in range(self.arguments.users):
                            initialisation.append(asyncio.create_task(self.initialise_user(browser, port, user)))
                            await asyncio.sleep(1)
                        outcomes = await asyncio.gather(*initialisation, return_exceptions=True)
                        if any(isinstance(outcome, BaseException) for outcome in outcomes):
                            raise RuntimeError("At least one user failed to obtain results; interaction test was not started")
                        self.phase = "interaction"
                        self.interaction_started_at = utc_now()
                        deadline = time.monotonic() + self.arguments.duration_seconds
                        await asyncio.gather(*(self.interact(session, deadline) for session in self.sessions))
                        self.interaction_finished_at = utc_now()
                        self.phase = "connected_idle"
                        await asyncio.sleep(max(self.arguments.sample_seconds, 2))
                    finally:
                        for session in self.sessions:
                            with contextlib.suppress(Exception):
                                await session["context"].close()
                        self.active_users = 0
                        await browser.close()
                self.phase = "recovery"
                await asyncio.sleep(self.arguments.cooldown_seconds)
            finally:
                self.monitor_stop.set()
                try:
                    if monitor_task is not None:
                        await monitor_task
                finally:
                    observed_identities = sampler.process_identities("server") if sampler is not None else ()
                    cleanup_task = asyncio.create_task(asyncio.to_thread(
                        terminate_owned_process, process, server_identity, observed_identities,
                    ))
                    try:
                        cleanup = await asyncio.shield(cleanup_task)
                    except asyncio.CancelledError:
                        # A first Ctrl+C must not skip the bounded child cleanup.
                        await cleanup_task
                        raise
                    self.event(None, "server_cleanup", "ok", **cleanup)


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

    required_actions = ("initial_analysis", "time_bin", "station", "scope", "export", "drilldown", "idle_resume")
    per_user_coverage = {}
    for user in range(1, experiment.arguments.users + 1):
        successful_actions = {row["action"] for row in experiment.actions
                              if row.get("user") == user and row.get("status") == "ok"}
        user_coverage = {action: action in successful_actions for action in required_actions}
        per_user_coverage[str(user)] = {
            "actions": user_coverage,
            "complete": all(user_coverage.values()),
            "missing_actions": [action for action, covered in user_coverage.items() if not covered],
        }
    coverage = {action: all(user["actions"][action] for user in per_user_coverage.values())
                for action in required_actions}

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
        if not user_coverage["complete"]:
            incomplete_reasons.append(f"User {user} is missing successful actions: {', '.join(user_coverage['missing_actions'])}.")
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
            "observed_interaction_seconds": observed_seconds,
            "interaction_duration_verified": duration_complete,
            "fatal_error": fatal_error, "failure_count": failure_count,
            "status": "passed" if not incomplete_reasons else "incomplete_or_failed",
            "incomplete_reasons": incomplete_reasons,
            "required_actions_per_user": list(required_actions),
            "per_user_coverage": per_user_coverage,
            "action_coverage": coverage, "memory_coverage": memory_coverage,
            "metric_diagnostic_sample_count": diagnostic_sample_count,
            "metric_diagnostics": dict(sorted(diagnostic_counts.items())),
            "phases": phases, "actions": action_summaries,
            "limitations": ["Frozen offline provider query replay; upstream availability and SQL engine throughput are not tested.",
                "Browser generator and application share host CPU and memory; process groups are reported separately.",
                "This duration does not establish hour-scale retention, 100-user capacity or Community Cloud performance.",
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
    lines += ["", "## Coverage for each user", "", "| User | Initial run | Time bin | Station | Scope | Export | Drill-down | Idle resume |",
              "| ---: | --- | --- | --- | --- | --- | --- | --- |"]
    for user, coverage in summary["per_user_coverage"].items():
        cells = ["ok" if coverage["actions"][action] else "missing" for action in summary["required_actions_per_user"]]
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
        write_json(output / "versions.json", version_record())
        write_json(output / "arguments.json", vars(options))
        import psutil
        if not options.prepare_only:
            import playwright.async_api  # Fail before any child server is launched.
        available = psutil.virtual_memory().available
        print(f"Available host memory: {format_mib(available)}", flush=True)
        if available < 2 * 1024**3:
            print("WARNING: less than 2 GiB available. Memory pressure may distort timings; prefer --users 1 locally.", flush=True)
        run_owned_preparation([sys.executable, str(HARNESS_DIRECTORY / "replay.py"), "--prepare", str(output)],
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
        asyncio.run(experiment.execute())
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
