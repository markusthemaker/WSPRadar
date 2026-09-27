# WSPRadar multi-user load test

This harness runs the actual application with separate headless browser sessions and frozen provider responses. It measures application-server memory, browser/load-generator memory, disk use, interactions, rendering, and exports without directing a load test at public WSPR databases or the deployed WSPRadar service.

Start with one local user, then three local users. Use the same source snapshot for the ten-user Codespaces run: a 15-minute workload followed by five minutes of observation after the browsers close. Setup and startup add time beyond those 20 minutes. The output ZIP is the artifact to return for analysis.

The 15-minute interaction timer starts only after every requested session has finished its initial analysis and obtained results. Initial analysis, queue waiting, setup, and the baseline measurement therefore do not consume that interaction period.

## What the test establishes

- The real Streamlit application, analysis pipeline, figures, Inspector interactions, and export preparation run against deterministic replay data.
- Each browser context has independent session state. The application's existing analysis and export queues remain in place.
- Provider requests that cannot be satisfied by the replay fixture fail closed. Do not alter the harness to fall back to a public database.
- Frozen data makes runs comparable and avoids provider load. It does not measure upstream latency, provider failover, database freshness, or every possible query/data shape.
- Replay preparation executes the application's exact generated queries over frozen source reports through the repository's local SQL adapter, then prepopulates the raw-query disk caches. This is an offline provider replay with warm query caches: the measured workload exercises application memory and processing, not provider HTTP throughput or native ClickHouse execution.
- The server and browser generator share one machine. Their separate measurements help identify contention; the machine's total memory and CPU load still affect both.
- Fifteen minutes does not establish six-hour retention, 100-user capacity, or production-host performance. A completed run is useful evidence only for its recorded workload, source, dependency versions, machine, and duration.

The replay run can still need network access during setup: Python packages, the Playwright browser, and first-use Cartopy/Natural Earth map assets may require downloads. Replay describes the WSPR provider data boundary, not an entirely network-disconnected installation.

## Local Windows setup

Run from the WSPRadar repository root in PowerShell. Use the working repository environment; do not combine another interpreter with its packages through `PYTHONPATH`.

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r tests/manual/multi_user_load_test/requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe tests/manual/multi_user_load_test/run.py --help
```

The harness-only dependencies are pinned in this folder. They are not added to the application's production requirements. Playwright requires its matching browser installation; the official [browser installation instructions](https://playwright.dev/python/docs/browsers) explain this separate step.

An installed Microsoft Edge can be used instead of downloading Chromium: append `--browser-channel msedge` to each run command below. Use that option only on a machine with Edge installed, and retain the recorded browser version when comparing results.

Validate fixture preparation and then run the short smoke check:

```powershell
.\.venv\Scripts\python.exe tests/manual/multi_user_load_test/run.py --prepare-only
.\.venv\Scripts\python.exe tests/manual/multi_user_load_test/run.py --smoke
```

`--prepare-only` prepares replay artifacts without starting the server or browsers. `--smoke` selects one user, a 120-second workload, a 10-second cooldown, and a five-second baseline. It checks that the harness runs; it is not a capacity test. Smoke checks compress reading and idle pauses to two seconds; normal runs use approximately 25 seconds between actions and a two-minute connected idle pause once per action cycle, followed by a verified interaction. `--idle-seconds` changes that idle pause. An action already in progress is allowed to finish at the end of the requested interaction period, so recorded duration can be longer.

Run the local comparisons one after the other, keeping each command attached to its foreground terminal until it reports completion:

```powershell
.\.venv\Scripts\python.exe tests/manual/multi_user_load_test/run.py --users 1 --duration-seconds 900 --cooldown-seconds 300
.\.venv\Scripts\python.exe tests/manual/multi_user_load_test/run.py --users 3 --duration-seconds 900 --cooldown-seconds 300
```

Do not start a second harness run while the first is running. Avoid unrelated heavy work during the measurement. If you stop a run with Ctrl+C, keep its diagnostics and treat it as interrupted rather than a successful load test.

## Transfer the exact source to Codespaces

The new local harness folder is not automatically present in GitHub. Creating a codespace from the repository alone does not transfer uncommitted local changes.

Use the prepared `.test/multiuser-load-transfer.zip` source bundle. It contains the selected current source snapshot and this harness; Git metadata, virtual environments, caches, test output, and secrets are excluded. This is a source-transfer ZIP, distinct from the result ZIP produced after a test. No commit or push is needed for this route.

After changing source or the harness, rebuild the bundle from the repository root:

```powershell
.\.venv\Scripts\python.exe tests/manual/multi_user_load_test/make_bundle.py --overwrite
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

## Codespaces setup and ten-user run

The checked-in development container supplies Python 3.10 and the application's native packages. Create an isolated environment for this source snapshot, then install its runtime and test tooling:

```bash
python -m venv .venv-load
source .venv-load/bin/activate
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

The result package includes the measurement series (`metrics.csv`), action records (`actions.jsonl`), machine/source/dependency metadata, `summary.json`, `report.md`, the server log, and any captured failure screenshots. Raw replay caches and downloaded analysis ZIP payloads are excluded from the return package.

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
