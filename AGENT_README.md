# WSPRadar Repository Guide

This document is for maintainers and coding agents. The generated `README.md`
is the end-user and scientific manual. Code-level component boundaries and data
flows are documented in `docs/architecture.md`.

## Purpose

WSPRadar is a public Streamlit application for semi-quantitative comparison of
historical WSPR transmitting and receiving performance. It queries the public
wspr.live ClickHouse HTTP endpoint and turns the returned observations into maps,
segment summaries, evidence views, and export packages.

The application is an analysis and science-education tool. It is not a live
receiver, transmitter controller, propagation forecaster, or calibrated antenna
measurement system.

## Main Features

- TX and RX Success analyses that compare target opportunities with signals seen
  by other active stations.
- TX and RX comparison analyses for local/reference setups, hardware A/B cases,
  and sequential WSPR frame comparisons.
- Interactive configuration with English and German presentation.
- Geographic station and segment aggregation on an azimuthal-equidistant map.
- Segment Inspector views with station tables, evidence figures, and drilldown
  tables backed by projected Parquet reads.
- Path-illumination classification using vectorized solar geometry.
- Downloadable analysis exports containing configuration, metadata, tables,
  compact Parquet evidence, and high-resolution figures.
- Guided demo profiles for historical examples.
- Process-wide analysis and export admission queues, duplicate-request rejection,
  bounded HTTP reads, shared artifact locking, and performance/RSS logging.
- Full scientific documentation rendered in the page and generated as a lazy,
  process-cached PDF.

See `README.md` for the scientific method, UI walkthrough, interpretation, and
end-user limitations.

## Runtime Requirements

The root project does not declare a Python version in package metadata. The
development container is based on Python 3.10. The repository was verified with
Python 3.12.13 on 2026-07-11.

Python dependencies are listed in:

- `requirements.txt` for application runtime.
- `requirements-dev.txt` for runtime plus pytest.
- `packages.txt` for Streamlit Community Cloud native packages.

The Linux development container additionally installs GEOS, PROJ, Cairo, and
`pkg-config` development packages. Cartopy and PDF generation rely on these
native libraries. Most Python dependencies are not version-pinned, so a fresh
installation is not guaranteed to reproduce the verified environment exactly.

## Installation

From the repository root, create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Use `requirements.txt` instead of `requirements-dev.txt` for a runtime-only
environment. The `.devcontainer/devcontainer.json` definition is the available
reproducible Linux setup path.

Verification status on 2026-07-11:

- All runtime and test dependency imports succeeded under Python 3.12.13.
- `python -m pip check` reported no broken requirements.
- A fresh virtual-environment installation was not performed because the local
  environment already contained the installed dependency set.
- The development-container image was inspected but not built during this review.

## Configuration

Runtime configuration is code-based; no required secret or database credential
was found in the application path.

| File | Configuration owned |
| --- | --- |
| `config/app_config.py` | Application metadata, public URLs, wspr.live URL, cache path/TTL, query limits, HTTP timeouts/response ceilings, admission queues, inspector cache, and documentation delay. |
| `config/bands.py` | User-facing WSPR bands and wspr.live band identifiers. |
| `config/demo_profiles.py` | Guided demo inputs and historical time windows. |
| `config/plot_constants.py` | Map geometry, colors, and rendering/scientific plotting constants. |
| `.streamlit/config.toml` | Streamlit theme and server CORS/XSRF configuration. |
| `.gitignore` | Excludes a local `.streamlit/secrets.toml`; no example secrets file is committed. |

Do not put secrets in source-controlled configuration. `.streamlit/secrets.toml`
is ignored by Git.

Important defaults currently include:

- Maximum query interval: 31 days.
- Analysis admission: 2 active, 10 queued, 600-second queue wait.
- Export admission: 1 active, 10 queued, 600-second queue wait.
- CSV and Parquet decompressed response ceiling: 64 MiB each.
- HTTP connect timeout: 10 seconds; read-inactivity timeout: 60 seconds.
- Query cache TTL: 3600 seconds.
- Session inspector cache budget: 5 MiB.

These limits come directly from `config/app_config.py`; change them there and
update the associated regression tests.

## Running the Application

Start Streamlit from the repository root:

```powershell
python -m streamlit run app.py
```

The application uses port 8501 by default. A repository VS Code task runs the
same entry point with CORS and XSRF protection disabled, matching the committed
Streamlit server configuration.

The start command was verified headlessly on port 8503 on 2026-07-11. The
Streamlit health endpoint returned HTTP 200 with `ok`.

Typical use is:

1. Select English or German presentation.
2. Load a demo or configure callsigns, locator, band, time window, and mode.
3. Run TX or RX analysis.
4. Inspect the map, segment and selected-station evidence.
5. Prepare an export only when needed.

The exact scientific workflow and result interpretation are maintained in
`README.md`.

## Development

The principal boundary is:

```text
app.py -> ui/ orchestration and adapters -> core/ scientific and infrastructure code
```

`AnalysisContext` contains canonical scientific configuration. It must not carry
localized labels. `PresentationContext` contains language, labels, and theme.
Streamlit state is translated into these contexts in UI adapters before core
work begins.

Useful files when tracing behavior:

- `ui/run_controller.py`: end-to-end analysis orchestration.
- `core/analysis_runner.py`: SQL and post-fetch analysis contracts.
- `core/data_engine.py`: bounded upstream HTTP and query cache.
- `core/compare_engine.py` and `core/opportunity_engine.py`: scientific
  aggregation and classification.
- `core/map_data.py` and `core/plot_engine.py`: pure map aggregation and
  presentation rendering.
- `ui/components/segment_inspector.py` and `ui/inspector/`: inspector
  orchestration and pure view models.
- `ui/results_export.py`: lazy export recipe execution and ZIP construction.
- `core/artifact_store.py`: artifact namespaces and lifecycle.

The separate `tools/Timed-AB-Relay-Switch/` utility has its own README,
requirements, launch wrappers, and local configuration. Do not assume that
changes to it are exercised by the Streamlit regression suite.

## Testing and Checks

Run the complete regression suite:

```powershell
python -m pytest tests/regression -q
```

Verified result on 2026-07-11:

```text
116 passed, 1 skipped, 1 warning
```

The skipped test requires a generated fixture under
`tests/regression/fixtures/`. That directory currently contains only `.gitkeep`.
The warning is a Matplotlib pending deprecation for `set_bad` in
`ui/plots/evidence_figures.py`.

Compile the repository Python sources:

```powershell
python -m compileall -q app.py config core docs ui scripts tests tools
```

Check whitespace in the patch:

```powershell
git diff --check
```

Both commands passed during the 2026-07-11 review.

There is no configured project linter, formatter, type checker, pre-commit hook,
or GitHub test workflow. The sole GitHub workflow, `wake.yml`, opens the deployed
application every six hours and on manual dispatch. Compilation is a syntax
check, not a substitute for static analysis.

To build a regression fixture from an exported demo folder, inspect and use
`scripts/build_regression_fixture_from_demo_folder.py`. Do not treat
`tests/demo/Vanhamel_rx_compare/` as a current regression fixture; it is a
historical exported analysis package.

## Cache and Operational State

The application writes local transient state under `.wspr_cache/`, which is
ignored by Git:

```text
.wspr_cache/
  queries/
  derived-analysis/basemaps/
  session-artifacts/<owner>/run_<id>/
  .artifact-locks/
```

Query and session artifacts have TTL/access handling. Derived basemaps are
shared across sessions and are not currently subject to TTL cleanup. Process
memory also holds the query DataFrame LRU, admission state, inspector session
models/PNGs, and generated documentation PDF cache.

Deleting `.wspr_cache` is safe only when no active process is using it. The next
request will rebuild missing query, basemap, or session artifacts.

## Known Limitations and Risks

- The application depends on availability and behavior of the public wspr.live
  ClickHouse HTTP service. Requests are bounded by time and bytes, but upstream
  failure still causes analyses to fail and require retry.
- Analysis/export admission and duplicate tracking are process-local. Multiple
  application processes do not share a global queue or request budget.
- There is no authentication, IP rate limiting, or trusted-edge abuse control.
  A client can create multiple Streamlit sessions.
- Streamlit CORS and XSRF protection are disabled in committed configuration.
  This should be revisited for a public deployment and changed only after testing
  the deployment path that required it.
- Cache namespaces have TTL and locking but no configured maximum file count,
  byte quota, minimum-free-disk rule, or derived-basemap lifetime.
- Export ZIP construction is entirely memory-backed and the prepared ZIP remains
  in session state. Export concurrency is limited to one, but a large export can
  still raise process RSS.
- The process-wide `requests.Session` is used by potentially concurrent analysis
  workers. No explicit test establishing all aspects of Requests session
  thread-safety was found; treat this as an operational uncertainty.
- Matplotlib rendering is serialized with a process-wide lock. This protects
  shared state but limits concurrent rendering throughput.
- The first map for a new locator can incur Cartopy/Natural Earth asset loading
  and basemap construction. Later requests use the derived basemap cache.
- Session and in-memory caches are lost on process restart. Local filesystem
  persistence depends on the hosting environment retaining `.wspr_cache`.
- Most dependencies are unpinned and there is no automated vulnerability or
  dependency audit workflow.
- The committed historical demo export predates the current opportunity schema;
  the scientific regression fixture is absent, so the fixture-integrity test is
  skipped.
- Browser-level end-to-end behavior and multi-process deployment behavior are
  not covered by the current pytest suite.
- `README.md` synchronization rewrites the whole file. Repository engineering
  content belongs here, not in the generated README.

These are observed limits, not a claim that the application is unsafe or
incorrect. Prioritize changes according to measured cloud resource behavior and
the public deployment threat model.
