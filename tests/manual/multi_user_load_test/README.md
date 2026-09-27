# WSPRadar multi-user load test

This harness runs the actual application with separate headless browser sessions and frozen provider responses. It measures application-server memory, browser/load-generator memory, disk use, interactions, rendering, and optional exports without directing a load test at public WSPR databases or the deployed WSPRadar service.

Start with one user, then three users. Use the same source snapshot for the ten-user Codespaces run: a 15-minute workload followed by five minutes of observation after the browsers close. Setup and startup add time beyond those 20 minutes. The output ZIP is the artifact to return for analysis. All commands in this README use Linux Bash, as provided by GitHub Codespaces.

The 15-minute interaction timer starts only after every requested session has finished its initial analysis and obtained results. Initial analysis, queue waiting, setup, and the baseline measurement therefore do not consume that interaction period.

## What the test establishes

- The real Streamlit application, analysis pipeline, figures, Inspector interactions, and, when enabled, export preparation run against deterministic replay data.
- Each browser context has independent session state. The application's existing analysis and export queues remain in place.
- Provider requests that cannot be satisfied by the replay fixture fail closed. Do not alter the harness to fall back to a public database.
- Frozen data makes runs comparable and avoids provider load. It does not measure upstream latency, provider failover, database freshness, or every possible query/data shape.
- Replay preparation executes the application's exact generated queries over frozen source reports through the repository's local SQL adapter, then prepopulates the raw-query disk caches. This is an offline provider replay with warm query caches: the measured workload exercises application memory and processing, not provider HTTP throughput or native ClickHouse execution.
- The server and browser generator share one machine. Their separate measurements help identify contention; the machine's total memory and CPU load still affect both.
- Fifteen minutes does not establish six-hour retention, 100-user capacity, or production-host performance. A completed run is useful evidence only for its recorded workload, source, dependency versions, machine, and duration.

The replay run can still need network access during setup: Python packages, the Playwright browser, and first-use Cartopy/Natural Earth map assets may require downloads. Replay describes the WSPR provider data boundary, not an entirely network-disconnected installation.

## Linux setup (GitHub Codespaces)

Open a Bash terminal in the WSPRadar source root: the directory containing `app.py`, `requirements.txt`, and `tests/manual/multi_user_load_test/`. This can be the repository checkout or the extracted source snapshot described below. Use a Linux virtual environment created in that directory; do not copy a Windows `.venv` or combine another interpreter with its packages through `PYTHONPATH`.

The repository's development-container configuration installs the application's `requirements.txt` into its default Python environment during container creation. It does not create or activate `.venv`, install this harness's additional dependencies, or install Playwright's browser. A new virtual environment is isolated from that default environment, so install both sets of dependencies explicitly:

```bash
if [ ! -d .venv ]; then python -m venv .venv; fi
source .venv/bin/activate
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r tests/manual/multi_user_load_test/requirements.txt
python -m playwright install --with-deps chromium
python tests/manual/multi_user_load_test/run.py --help
```

If you already completed this setup in the same Linux source directory, reuse that environment. In each new terminal, run `source .venv/bin/activate` before the test commands; repeat dependency installation only when the requirements or environment change. `.venv/` is excluded from Git and must not be committed.

The harness-only dependencies are pinned in this folder. They are not added to the application's production requirements. Playwright requires its matching browser installation; the official [browser installation instructions](https://playwright.dev/python/docs/browsers) explain this separate step.

The application's root `requirements.txt` pins Streamlit to **1.64.0**, shared by production, Codespaces, and local development. Reinstall the root requirements after updating a checkout so that an existing environment receives the pin; editing the file alone does not change installed packages. Production receives the pin when that source revision is deployed and its dependencies are installed. Use `versions.json` to confirm the version actually used in a load-test result. Matching Streamlit versions removes one compatibility variable; Python, the remaining packages, the operating system, and the browser version are still recorded separately.

The Linux commands use Playwright's installed Chromium browser. `--browser-channel` is only needed when deliberately using a different, already installed supported browser; retain the recorded browser version when comparing results.

The harness locates time-bin controls inside the Segment Inspector by their visible labels and verifies the selected state. It supports accessibility state, React Aria's `data-selected` marker, and the older Streamlit `kind` marker. Scope changes use keyboard navigation to open the native multiselect, then verify both the selected values and the rendered active-scope summary after the application finishes. A missing control or unverifiable state is printed as `UNAVAILABLE` and makes workload coverage incomplete. It is not counted as a successful interaction. These selectors avoid relying exclusively on styling attributes that can differ between installed Streamlit versions; keep `versions.json` with every result.

The scope controls retain WSPRadar's explicit **Full Range** and **All Directions** defaults and disable Streamlit's separate native **Select all** command. The harness also excludes native bulk commands from its candidate options. Read-only Inspector tables retain Streamlit 1.64.0's automatic lazy loading above 150,000 rows; Station Insights retains interactive row selection. Lazy loading reduces browser transfers for large tables but does not move ordinary pandas DataFrames out of server memory.

The default workload concentrates on exploring completed results: time-bin changes, station selection, Drill-Down, distance/direction scope changes and returning after connected idle periods. It performs no exports by default (`--export-users 0`). Set `--export-users 1` to add one prepared download by the first user after that user's first complete exploration cycle; other users continue exploring. Each selected export user downloads at most once during the run. One exporting user out of ten is a separate 10% export-participation scenario, not a simulation of 1% usage; with ten users the main exploration run is the more useful baseline for an estimated rare export workflow. The report requires export coverage only for the explicitly selected export users.

Each rerun-triggering action waits for a new Streamlit run and its successful full-script or fragment completion. An interrupted run that requests another rerun is not accepted as completion, and a compile error fails promptly. Export preparation and clicking the prepared download have separate completion expectations. A short quiet interval and visible error checks follow completion; time-bin, station and scope actions still verify the resulting UI state. The action timeout covers the complete action, including its DOM and download waits. A browser error interrupts a pending action rather than waiting for its normal timeout.

After a failed action, that user's interaction loop stops and its page stays open until shared cleanup; the harness does not reload or replace it. `users` / `active_users` counts initialized sessions retained until cleanup, while `workload_users` counts sessions whose interaction loop is still running (including their planned reading pauses). `interaction_stopped` records the stopped workload's duration and remaining scheduled time. Failures always make the report incomplete. If all users stop early, the run proceeds to cleanup and recovery early and reports the shortened interaction duration; it does not claim a completed 15-minute workload. These changes improve test sequencing and diagnostics, but do not establish that the previously observed `ElementNode` browser crash is fixed.

Validate fixture preparation and then run the short smoke check:

```bash
python tests/manual/multi_user_load_test/run.py --prepare-only
python tests/manual/multi_user_load_test/run.py --smoke
```

`--prepare-only` prepares replay artifacts without starting the server or browsers. `--smoke` selects one user, a 120-second workload, a 10-second cooldown, and a five-second baseline. It checks that the harness runs; it is not a capacity test. Smoke checks compress reading and idle pauses to two seconds; normal runs use approximately 25 seconds between actions and a two-minute connected idle pause once per action cycle, followed by a verified interaction. `--idle-seconds` changes that idle pause. An action already in progress is allowed to finish at the end of the requested interaction period, so recorded duration can be longer.

Allow roughly three to five minutes for a smoke check as an initial estimate, with additional time possible for first-use asset downloads or slow analysis/export rendering. Its 120 seconds begin only when the initial result is ready. Progress passes through `startup`, `baseline`, `ramp_up`, `interaction`, `connected_idle`, and `recovery`; the periodic output can skip a short phase between samples. During `ramp_up`, `users=0` means that no session has completed its initial analysis yet. Per-user waiting messages explicitly state that the interaction timer has not started. Initial results have a 600-second timeout by default (`--startup-timeout-seconds`), but visible application exceptions and browser errors fail promptly instead of consuming that entire wait.

Every invocation first compiles the source with the interpreter actually executing the test, without importing or running the application. An incompatible Python syntax error therefore stops setup before replay preparation or server launch, with the interpreter version, file, and line in the diagnostic archive. This checks syntax, not dependency compatibility or application correctness. Both commands above prepare their own isolated replay artifacts; `--prepare-only` is an optional setup check and does not supply a cache to the later smoke run.

A normal smoke run closes its browsers and server, prints `Report:` and `Return this archive:` paths, then returns to the shell prompt. A completed command can still report failed or incomplete evidence: read `report.md`; a successful run exits with code zero.

Run the one-user and three-user comparisons one after the other, keeping each command attached to its foreground terminal until it reports completion:

```bash
python tests/manual/multi_user_load_test/run.py --users 1 --duration-seconds 900 --cooldown-seconds 300
python tests/manual/multi_user_load_test/run.py --users 3 --duration-seconds 900 --cooldown-seconds 300
```

Do not start a second harness run while the first is running. Avoid unrelated heavy work during the measurement. If you stop a run with Ctrl+C, keep its diagnostics and treat it as interrupted rather than a successful load test.

Press Ctrl+C once and leave the foreground command attached while it cancels pending work, closes browser sessions, stops its owned server processes, and writes the partial report. It prints a shutdown message; repeated Ctrl+C during this cleanup does not interrupt the same tasks again. Cleanup has bounded waits and can take tens of seconds if a child does not exit promptly. An operating-system kill or terminal/container termination can still prevent cleanup and report creation; use the diagnostic recovery instructions below in that case.

## Transfer the exact source to Codespaces

If your Codespaces checkout already contains the intended committed application and `tests/manual/multi_user_load_test/`, use that checkout directly and skip the ZIP transfer. Creating a codespace from the repository does not transfer uncommitted local changes; use the bundle workflow below when the source to test is not yet available in that checkout.

Use the prepared `.test/multiuser-load-transfer.zip` source bundle. It contains the selected current source snapshot and this harness; Git metadata, virtual environments, caches, test output, and secrets are excluded. This is a source-transfer ZIP, distinct from the result ZIP produced after a test. No commit or push is needed for this route.

After changing source or the harness, rebuild the bundle from the source Git checkout's root, not from an extracted snapshot. On Linux, with its virtual environment activated, run:

```bash
python tests/manual/multi_user_load_test/make_bundle.py --overwrite
```

The extracted snapshot includes `source_snapshot.json`. The runner verifies its file hashes before starting and records them with the measurements; extracting inside another Git repository does not substitute that outer repository's revision.

The bundle preserves paths relative to the repository root. Extracting it into `wspradar-load-test` places `app.py` directly in that directory and this harness in `wspradar-load-test/tests/manual/multi_user_load_test/`. Run from that extracted source snapshot, rather than copying only the harness onto a potentially different GitHub revision.

1. On GitHub, create or open a codespace for WSPRadar using the repository's existing development container. Let its setup finish.
2. For the ten-user run, select an available **four-core machine with 16 GB RAM** as a starting point for hosting both server and browsers. GitHub's [machine API documentation](https://docs.github.com/en/rest/codespaces/machines) illustrates that configuration; actual choices and storage depend on account/repository policy. Confirm the offered resources rather than assuming a machine name. The [machine-type guide](https://docs.github.com/en/codespaces/customizing-your-codespace/changing-the-machine-type-for-your-codespace) shows how to change them.
3. In the Codespaces VS Code Explorer, upload `multiuser-load-transfer.zip` into the open repository directory using **Upload** from the Explorer context menu, or drag the ZIP into Explorer.
4. Open a terminal in that directory and extract into a separate, previously unused folder:

```bash
python -m zipfile -e multiuser-load-transfer.zip wspradar-load-test
cd wspradar-load-test
```

For a later source bundle, choose a new extraction folder so that stale files cannot survive from an earlier snapshot. Run all remaining commands inside the extracted directory, where `app.py` and `tests/manual/multi_user_load_test/` are visible.

When a replacement bundle changes only application or harness code and both requirements files are unchanged, you can reuse the working Linux environment from the original Codespaces checkout. Activate it before changing directories, for example `source /workspaces/WSPRadar/.venv/bin/activate`, then enter the fresh extraction folder and run the test there. This uses that environment's actual interpreter and installed browser; it does not copy an environment or mix packages through `PYTHONPATH`. Otherwise, create and install the snapshot's own environment as described below.

### Continue the existing Codespace with the Streamlit 1.64.0 update

Upload the newly rebuilt `multiuser-load-transfer.zip` into `/workspaces/WSPRadar/`. The previously supplied ZIP predates the approved scope and harness fixes. Preserve earlier result folders and use the new extraction folder below only if it does not already exist; if it does, choose a different unused folder name in both commands. This update pins the Streamlit version already recorded in the last Codespaces result, so the existing Linux environment and Chromium installation can be reused after reinstalling the declared requirements:

```bash
cd /workspaces/WSPRadar
source /workspaces/WSPRadar/.venv/bin/activate
python -m zipfile -e multiuser-load-transfer.zip wspradar-load-test-streamlit164
cd wspradar-load-test-streamlit164
python -m pip install -r requirements.txt -r tests/manual/multi_user_load_test/requirements.txt
```

Then run the new isolated harness regression cases in Codespaces, followed by the real browser smoke check only if those cases pass:

```bash
python -m unittest discover -s tests/manual/multi_user_load_test -p test_interactions.py
python tests/manual/multi_user_load_test/run.py --smoke
```

Wait for the smoke check's `Return this archive:` line and inspect its `report.md`. Proceed to the ten-user command below only when the report is `passed`; otherwise return the smoke result ZIP first. These changes were prepared without running local tests or starting a local application/browser, at the operator's request. The Codespaces smoke and load runs exercise the default image renderer; the optional legacy `pyplot` setting now serializes the figure explicitly and uses `st.image`, and its added renderer regression cases remain separate from that default-mode smoke coverage.

### Diagnose the scope-rendering crash before the next load run

The Codespaces smoke on 2026-09-27 passed all 19 then-current harness tests but reproduced `'setIn' cannot be called on an ElementNode` during scope exploration with one user. Its protocol log shows the preceding download fragment had completed about 3.5 seconds before scope selection began. This establishes a browser rendering failure, not a successful capacity result or evidence of memory exhaustion. The application fix was unresolved at that point; the subsequent structural trace and targeted change are recorded below.

For the replacement diagnostic bundle, upload the new `multiuser-load-transfer.zip` into `/workspaces/WSPRadar/` and extract into a new unused directory:

```bash
cd /workspaces/WSPRadar
source /workspaces/WSPRadar/.venv/bin/activate
python -m zipfile -e multiuser-load-transfer.zip wspradar-load-test-ui-trace
cd wspradar-load-test-ui-trace
```

The requirements are unchanged from the previous Streamlit 1.64.0 bundle, so reuse the existing Linux environment and Chromium installation. Run the harness tests in Codespaces first; their intentionally simulated failures can print `FAILED` diagnostics even when unittest's final result is `OK`:

```bash
python -m unittest discover -s tests/manual/multi_user_load_test -p 'test_*.py'
```

If the tests end with `OK`, run this one-user diagnostic, which performs no downloads:

```bash
python tests/manual/multi_user_load_test/run.py --smoke --trace-ui-deltas
```

`--trace-ui-deltas` retains bounded structural message records and cached-message summaries: UI paths, block/element types, run/fragment IDs, outgoing rerun requests and fingerprints of changed widget states. It records no table contents, image bytes, Markdown bodies or raw widget values. On a browser error it writes the browser stack and the structural trace immediately, followed by the usual screenshots and diagnostics. This instrumentation adds overhead and is for diagnosis, so omit it from later memory-baseline runs. Return the complete result ZIP even if this diagnostic passes; do not start the ten-user run until the scope failure has been reviewed.

### Validate the Inspector fragment-ownership fix

The diagnostic result `20260927-123400-59eec8` reproduced the crash with exports disabled, after all 97 manual-harness unit tests passed in Codespaces. Initial analysis, time-bin selection, station selection and Drill-Down succeeded; changing the direction scope to ENE failed. The interaction period ended after 14.94 seconds, so this is incomplete load evidence. The sampled server RSS reached 343.5 MiB during interaction while at least 9,816 MiB of host memory remained available in that phase.

The trace identifies the first invalid UI update. The Inspector wrapper is at `0/6/3/0/3/1/2`. Its child `5` was a Markdown element in the preceding completed station run (record 382). Scope selection excluded that station and removed its selected-evidence sections, moving the result-footer columns from child `7` to child `5`. After a second Inspector rerun request arrived during rendering, record 442 delivered a nested Save Configuration fragment block beneath `5/1/0` without first delivering its new parent columns. The browser consequently tried to descend through the old Markdown element. Streamlit 1.64.0's pending-message queue retains other fragment IDs when clearing the interrupted parent's deltas; that source behavior explains how the child updates can survive without their parents. The trace records the resulting missing parents, not the server's intermediate queue contents.

The application now renders the results-footer Save Configuration content directly in the existing Inspector fragment. Its parents and descendants therefore share one fragment owner. The top-level save control keeps its independent fragment and both placements retain the same save workflow. This change is prepared but has not yet passed a Codespaces browser run; it is not a claimed resolution or capacity result. The workload still performs no exports by default, and its scope interaction sequence is unchanged.

Upload the replacement `multiuser-load-transfer.zip` into `/workspaces/WSPRadar/` and use a new, unused extraction directory:

```bash
cd /workspaces/WSPRadar
source /workspaces/WSPRadar/.venv/bin/activate
python -m zipfile -e multiuser-load-transfer.zip wspradar-load-test-fragment-owner
cd wspradar-load-test-fragment-owner
mkdir -p .test
python -m pip install -r requirements-dev.txt -r tests/manual/multi_user_load_test/requirements.txt
```

Application and browser requirements are unchanged. The development requirements additionally ensure pytest is available for the focused application regressions. Run each command only after the preceding one succeeds:

```bash
python -m pytest tests/regression/test_config_save.py tests/regression/test_export_admission.py tests/regression/test_export_ownership.py tests/regression/test_results_export_package.py -q
python -m unittest discover -s tests/manual/multi_user_load_test -p 'test_*.py'
python tests/manual/multi_user_load_test/run.py --smoke --trace-ui-deltas
```

Return the smoke result ZIP for review, even if it passes. The trace should establish that footer Save Configuration deltas share the Inspector's fragment ID through the previously failing scope transition. After that smoke is confirmed, run the ten-user command below without `--trace-ui-deltas` to obtain the ordinary memory baseline. Local tests, compilation, application/browser startup and whitespace checks remain deferred at the operator's request. These focused checks and the smoke do not replace the full regression suite required before release or GitHub submission.

## Codespaces setup and ten-user run

The checked-in development container supplies Python 3.10 and the application's native packages. In the source directory you will test, use the Linux environment setup below. If you already completed the Linux setup above in this same directory, activate `.venv` and go straight to the smoke check; if you just extracted a new source snapshot, create its own environment first unless reusing the unchanged Linux environment as described above:

```bash
if [ ! -d .venv ]; then python -m venv .venv; fi
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r tests/manual/multi_user_load_test/requirements.txt
python -m playwright install --with-deps chromium
python tests/manual/multi_user_load_test/run.py --smoke
```

The `--with-deps` installation also installs Chromium's Linux system dependencies and may request elevated package-manager access. It follows Playwright's [official browser installation procedure](https://playwright.dev/python/docs/browsers). If container setup or browser installation fails, resolve that before interpreting any load-test result.

Then run:

```bash
python tests/manual/multi_user_load_test/run.py --users 10 --duration-seconds 900 --cooldown-seconds 300
```

Leave that terminal open until the command finishes. The harness starts and stops its own local server and headless browsers; do not separately launch `streamlit run app.py`. Browser traffic uses the local loopback address. No public endpoint or port forwarding is needed. If Codespaces automatically forwards a detected port, leave its visibility **Private**; GitHub documents [private forwarding as the default](https://docs.github.com/en/codespaces/reference/security-in-github-codespaces).

The test is not an HTTP request-rate test against the Streamlit health endpoint. Browser completion and action failures matter: a reachable health endpoint alone does not establish that users can inspect or export their results.

## Results to return

By default, each invocation creates a unique directory under `.test/multiuser-load/`, named with its timestamp and a unique suffix, and writes a sibling result ZIP. The terminal prints the exact paths. `--output` can select a new explicit output directory; use a different directory for every invocation.

The result package includes the measurement series (`metrics.csv`), action records (`actions.jsonl`), machine/source/dependency metadata, `summary.json`, `report.md`, the server log, and any captured failure screenshots. Failure captures also include visible page text and `*-widgets.json` files containing control labels and DOM attributes, including selection and menu-opening state, to diagnose frontend-version differences. Raw replay caches and downloaded analysis ZIP payloads are excluded from the return package.

`script_events.jsonl` records observed run starts, full/fragment completion status, run IDs, fragment IDs and the active action phase. Each failure also includes a `*-script.json` snapshot with the expected and observed run sequence and sticky browser/protocol errors. Keep these records with the result ZIP so a queued or interrupted rerun can be distinguished from a UI assertion failure. `summary.json` separately lists stopped session workloads; successful initial analyses alone do not establish successful concurrent exploration.

Download the printed result ZIP through the Codespaces Explorer: find the file, right-click it, and choose **Download**. Return that ZIP, including failed-run diagnostics if the test failed. Keep the one-user, three-user, and ten-user ZIPs together so that source and environment differences can be checked before comparing them.

If the operating system kills the process before it can write a ZIP, preserve the output directory. From the extracted source root, replace the final argument below with that run's actual directory to package the diagnostics already on disk:

```bash
python -c 'import sys; from pathlib import Path; sys.path.insert(0, "tests/manual/multi_user_load_test"); from run import archive_results; print(archive_results(Path(sys.argv[1])))' .test/multiuser-load/YOUR-RUN-DIRECTORY
```

This recovery command does not start the application or browser and does not turn an interrupted run into a pass.

Use these questions to read the report:

1. Did every expected browser complete its analysis and required actions? Were failures, timeouts, or rejected submissions reported?
2. How much memory belongs to the application server, and how much belongs to the browser generator? Did the machine approach its memory limit or sustain CPU saturation?
3. Did server memory settle while sessions remained open, or continue growing with interactions and export preparation?
4. What remained after the browsers closed and the cooldown completed? A nonzero plateau can include shared caches and allocator-retained memory; it is not by itself proof of a leak.
5. Did disk use grow with retained sessions and prepared exports, and were the source/fixture versions identical across comparisons?

The harness measures the checked-out implementation. It does not implement the proposed disk-offload, quota, or inactivity policies by running the test.

## Stop the Codespace

After downloading the result ZIP, use **Codespaces: Stop Current Codespace** in the Command Palette or **Stop codespace** in the codespace's menu at [github.com/codespaces](https://github.com/codespaces). Closing the browser tab does not stop the machine. GitHub distinguishes [stopping a codespace](https://docs.github.com/en/codespaces/developing-in-a-codespace/stopping-and-starting-a-codespace) from closing its client.

Active compute uses the account's included quota or billing allowance; four-core usage has a four-core-hour multiplier. Storage can continue to accrue while the codespace is stopped and still exists. Check the current [Codespaces billing policy](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces) before running. Delete the codespace only after the result ZIP and any source work you need are safely downloaded.
