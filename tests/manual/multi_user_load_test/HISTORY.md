# WSPRadar multi-user load-test history

This file preserves the dated investigation, source-transfer commands and troubleshooting notes previously embedded in the manual load-test README. Follow [README.md](README.md) for the current Linux setup, capture, smoke and ten-user sequence. The historical text below is retained verbatim: statements such as "not yet passed" and instructions to wait for review describe the state at that point in the investigation, not the current run status.

## 2026-09-27 investigation and source-transfer record

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

The first Codespaces regression run for this change reported **170 passed, 2 failed, 3 warnings** in 6.02 seconds. Both new fragment-ownership cases and the config-save tests passed. The failures were the `empty_artifact` cases of `test_valid_empty_drilldown_evidence_preserves_package`: their empty inferred-object station columns became Parquet null fields, which reject the real reader's string station filter. The fixture now declares both identity columns as strings before empty slicing. Runtime preparation already skips empty evidence before artifact writing; the reader and its error handling are unchanged. The fixture correction still needs Codespaces verification. Operators with the original fragment-owner snapshot may proceed with its diagnostic smoke without another transfer; it contains the same application code. This exception is specific to the two identified fixture failures, not permission to ignore other regression failures or declare the suite passed.

### Continue with the full-scope Griffiths memory workload

The next diagnostic, `20260927-124830-b087e9`, completed both scope fragment runs without a browser error, and the result-footer Save Configuration deltas shared the Inspector's fragment ID. It nevertheless failed after 15.51 seconds: the first run applied ENE (`rall_d3`), then a second request with the same widget-state fingerprints restored All Directions (`rall_dall`). The captured page confirms the reversal in both the selected chip and active-scope summary. This is a real selection failure, not an early assertion or completed load test.

The Streamlit 1.64 multiselect close path can resend an unchanged selection. The explicit-All callback previously interpreted the same mixed selection twice against different normalized previous values. It now retains the last ordered selection event and its normalized result so an exact duplicate cannot undo the choice. A deliberate subsequent All selection remains a distinct ordered event. The optional scope interaction and its strict assertion are retained; failure diagnostics now also show the observed selection and scope. The prior empty-Parquet-fixture correction is included. All new execution remains deferred to Codespaces.

For the next capacity measurement, the operator chose to keep Full Range / All Directions and prioritize station changes, Drill-Down and different time-bin sizes. This is now the default workload. Scope variation is a separate opt-in diagnostic, so its browser validation does not block this full-scope memory experiment. The default smoke does not validate the scope replay fix; its focused application regressions and any later `--vary-scope` browser run remain distinct evidence.

The default `performance` scenario now uses the **Griffiths RX Performance** demo: G3ZIL at IO90HW, 40 m, 1 April through 1 May 2017 UTC, with the configured 10,000 km peer limit. The ten-user run alternates five large Griffiths Benchmark sessions and five Griffiths Performance sessions. It uses two shared datasets; it does not represent ten distinct analysis inputs. The previous Milazzo TX Performance fixture remains available explicitly as `--scenarios performance-small`. The three-day Griffiths Benchmark fixture remains `benchmark-small`.

The frozen large Benchmark source contains 184,352 reports from G3ZIL/G4HZX. It cannot supply the other-receiver evidence needed by Performance. Therefore `capture.py` performs a **separate, one-time live capture** of the Performance demo's exact production query results before any measurement. It keeps the production response and row limits, runs requests sequentially against one provider, and records the configuration, SQL, provider, timestamp, file hashes and actual query-result row counts. It does not start the application or browser and does not simulate users. The captured row count is not yet measured, and is not directly comparable to a raw-report count. The load run thereafter reads the frozen capture offline. An absent capture, changed configuration/SQL, corrupted file or failed capture stops setup; there is no automatic fallback to Milazzo or a live provider.

Upload the replacement `multiuser-load-transfer.zip` into `/workspaces/WSPRadar/`, then extract into this new, unused directory. The existing Linux environment already has the development requirements from the preceding regression run; no dependency upgrade is required:

```bash
cd /workspaces/WSPRadar
source /workspaces/WSPRadar/.venv/bin/activate
python -m zipfile -e multiuser-load-transfer.zip wspradar-load-test-griffiths
cd wspradar-load-test-griffiths
mkdir -p .test
```

Run the focused application regressions and the updated harness tests, stopping if either command fails:

```bash
python -m pytest tests/regression/test_inspector_selection_state.py tests/regression/test_inspector_selection_integration.py tests/regression/test_results_export_package.py::test_valid_empty_drilldown_evidence_preserves_package -q
python -m unittest discover -s tests/manual/multi_user_load_test -p 'test_*.py'
```

If both pass, capture the dataset once from this extracted source root:

```bash
python tests/manual/multi_user_load_test/capture.py --provider wd2
```

Wait until capture completes and prints the result location and row counts. Its default directory is `.test/multiuser-datasets/griffiths-performance/`, relative to this source root. Keep that directory for every subsequent run of this source/configuration. Do not rerun capture for each simulated user or each smoke. Capture time depends on the provider; it is outside the 15-minute measurement. If capture fails, stop and return the error output. A partial directory is never accepted as a completed capture. An intentional retry must use a new directory with `capture.py --output PATH` and pass the same directory to subsequent runs using `--performance-replay PATH`.

The first Griffiths capture received HTTP 500 from wspr.live before producing data. HTTP 500 alone does not identify the ClickHouse failure. The operator reports that this Performance analysis normally succeeds through WD2, so the current command explicitly selects `--provider wd2`. Without that option, capture retains its first-enabled-provider default. One capture stays pinned to one provider and does not automatically retry or fail over. Newer captures preserve the failed SQL and bounded provider response in `capture_failure.json` and print the response, if supplied. The prior package omitted this diagnostic and cannot recover it after the failed process exited.

For the **already uploaded package without `--provider`**, the following fresh-process wrapper selects WD2 without editing any source file or invalidating `source_snapshot.json`. Run it from the extracted source root in the existing activated environment, once:

```bash
python - <<'PY'
import sys
sys.path.insert(0, "tests/manual/multi_user_load_test")
import capture
import config
from config import app_config

providers = tuple(provider for provider in config.WSPR_DATABASE_PROVIDERS
                  if provider.key == "wd2" and provider.enabled)
if len(providers) != 1:
    raise SystemExit("Exactly one enabled WD2 provider is required")
config.WSPR_DATABASE_PROVIDERS = providers
app_config.WSPR_DATABASE_PROVIDERS = providers
raise SystemExit(capture.main([
    "--output", ".test/multiuser-datasets/griffiths-performance-wd2",
]))
PY
```

When this wrapper succeeds, add `--performance-replay .test/multiuser-datasets/griffiths-performance-wd2` to the Performance smoke and the ten-user command below. The Benchmark-only smoke requires no capture path. Preserve the earlier partial directory; no deletion, source re-extraction or rerun of the already passed 39 application and 117 harness tests is required for this in-memory provider selection. It has been source-reviewed, not executed locally. The replay manifest records WD2 as the capture origin separately from its offline cache namespace.

Run the short fixed-scope smoke for **each** dataset, stopping on a failed report:

```bash
python tests/manual/multi_user_load_test/run.py --smoke --scenarios benchmark-large
python tests/manual/multi_user_load_test/run.py --smoke --scenarios performance
```

An unqualified `--smoke` uses only the first configured scenario (Benchmark); it does not exercise Performance. These two explicit checks establish that each dataset supports the required interactions. If both reports say `passed`, proceed directly to the ten-user run; no intermediate ZIP review is required:

```bash
python tests/manual/multi_user_load_test/run.py --users 10 --duration-seconds 900 --cooldown-seconds 300
```

Keep both smoke ZIPs and return the ten-user result ZIP. If any run fails, return its diagnostic ZIP instead. The run must complete the required station, time-bin, Drill-Down and idle-return workload. A successful initial analysis alone is insufficient. Omit `--trace-ui-deltas` and `--vary-scope` for this memory baseline. The full release regression suite remains outstanding; local tests, compilation and application/browser checks were not run.

## Codespaces setup and ten-user run

The checked-in development container supplies Python 3.10 and the application's native packages. In the source directory you will test, use the Linux environment setup below. If you already completed the Linux setup above in this same directory, activate `.venv` and use the capture/smoke sequence above; if you just extracted a new source snapshot, create its own environment first unless reusing the unchanged Linux environment as described above:

```bash
if [ ! -d .venv ]; then python -m venv .venv; fi
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r tests/manual/multi_user_load_test/requirements.txt
python -m playwright install --with-deps chromium
```

After setup, capture once (skip capture when this source/configuration already has a valid capture) and run both smokes:

```bash
python tests/manual/multi_user_load_test/capture.py --provider wd2
python tests/manual/multi_user_load_test/run.py --smoke --scenarios benchmark-large
python tests/manual/multi_user_load_test/run.py --smoke --scenarios performance
```

The `--with-deps` installation also installs Chromium's Linux system dependencies and may request elevated package-manager access. It follows Playwright's [official browser installation procedure](https://playwright.dev/python/docs/browsers). If container setup or browser installation fails, resolve that before interpreting any load-test result.

Then run:

```bash
python tests/manual/multi_user_load_test/run.py --users 10 --duration-seconds 900 --cooldown-seconds 300
```

Leave that terminal open until the command finishes. The harness starts and stops its own local server and headless browsers; do not separately launch `streamlit run app.py`. Browser traffic uses the local loopback address. No public endpoint or port forwarding is needed. If Codespaces automatically forwards a detected port, leave its visibility **Private**; GitHub documents [private forwarding as the default](https://docs.github.com/en/codespaces/reference/security-in-github-codespaces).

The test is not an HTTP request-rate test against the Streamlit health endpoint. Browser completion and action failures matter: a reachable health endpoint alone does not establish that users can inspect or export their results.

## Earlier README navigation and status wording

The following introductory wording was replaced when the run guide and historical record were separated. It is retained here without alteration:

For the next run after the earlier diagnostics, follow **[Continue with the full-scope Griffiths memory workload](#continue-with-the-full-scope-griffiths-memory-workload)**. Earlier diagnostic sections are retained as the investigation record; their older source folders and smoke commands are not the current run sequence.

These changes improve test sequencing and diagnostics, but do not establish that the previously observed `ElementNode` browser crash is fixed.

Capture the Performance dataset once as described below, then optionally validate replay preparation and run one short smoke per default scenario:

```bash
python tests/manual/multi_user_load_test/run.py --prepare-only
python tests/manual/multi_user_load_test/run.py --smoke --scenarios benchmark-large
python tests/manual/multi_user_load_test/run.py --smoke --scenarios performance
```

## 2026-09-27 later observed results

The subsequent Benchmark smoke, Performance smoke and ten-user run passed. The WD2 Griffiths Performance capture contained 676,768 query-result rows. Griffiths Benchmark replay produced 125,759 query-result rows from 184,352 frozen source reports. Query-result rows and raw source reports are different data stages and are not interchangeable counts.

These results cover the recorded fixed-scope workload and its required measurements. They do not validate optional scope changes, 100-user capacity, hour-scale retention, exports that were not requested, or an unmeasured production host. The current procedure is maintained in [README.md](README.md).