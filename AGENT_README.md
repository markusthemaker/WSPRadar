# WSPRadar Repository Guide

This document is for maintainers and coding agents. The generated `README.md`
is the end-user and scientific manual. Code-level component boundaries and data
flows are documented in `docs/architecture.md`.

Repository-wide contributor rules, including end-user manual content ownership,
relocation, bilingual parity, and validation requirements, are maintained in
`AGENTS.md`.

## Purpose

WSPRadar is a public Streamlit application for semi-quantitative comparison of
historical WSPR transmitting and receiving performance. It queries read-only
public ClickHouse HTTP endpoints, using wspr.live as primary and WSPRDaemon WD2
then WD1 as fallbacks, and turns the returned observations into maps,
segment summaries, evidence views, and export packages.

The application is an analysis and science-education tool. It is not a live
receiver, transmitter controller, propagation forecaster, or calibrated antenna
measurement system.

## Main Features

- TX and RX Success analyses that compare target opportunities with signals seen
  by other active stations.
- TX and RX comparison analyses for local/reference setups, hardware A/B cases,
  and deterministic scheduled TX A/B pairs.
- Interactive configuration through a novice-oriented Guided Input flow or the
  full Classic editor, with English and German presentation in both views.
- Geographic station and segment aggregation on an azimuthal-equidistant map.
- Segment Inspector views with station tables, evidence figures, and drilldown
  tables backed by projected Parquet reads.
- Path-illumination classification using vectorized solar geometry.
- Downloadable analysis exports containing configuration, metadata, tables,
  compact Parquet evidence, and high-resolution figures.
- Guided demo profiles for historical examples.
- Process-wide analysis and export admission queues, duplicate-request rejection,
  bounded HTTP reads, shared artifact locking, and performance/RSS logging.
- Source-pinned database failover with process-local rolling request budgets,
  provider cooldowns, source-isolated query caches, demo cache affinity, and run
  provenance.
- The preface rendered initially, with the table of contents and remaining manual
  loaded near its viewport boundary, through an explicit fallback, or when an
  unresolved preface link requests a deferred chapter/reference anchor; PDF
  generation remains process-cached and explicitly requested.

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

For automated Windows checks, use `.\.venv\Scripts\python.exe` directly instead
of activating the environment or combining another Python runtime with `.venv`
packages through `PYTHONPATH`. Confirm that the interpreter starts and imports
the declared dependencies first. If the launcher fails, inspect
`.venv/pyvenv.cfg` and access to its recorded base interpreter before concluding
that the dependency set is missing or broken.

Verification status on 2026-07-11:

- All runtime and test dependency imports succeeded under Python 3.12.13.
- `python -m pip check` reported no broken requirements.
- A fresh virtual-environment installation was not performed because the local
  environment already contained the installed dependency set.
- The development-container image was inspected but not built during this review.

## Configuration

Source-controlled configuration is split between typed policy/constants in
Python modules and schema-validated JSON data for standalone configurations and
Guided flow. Runtime code interprets these inputs generically; record identity
does not select behavior. No required secret or database credential was found in
the application path.

| File | Configuration owned |
| --- | --- |
| `config/app_config.py` | Application metadata, ordered WSPR database providers, provider budgets/cooldowns, cache path/TTL, query limits, HTTP timeouts/response ceilings, admission queues, and inspector-cache limits. |
| `config/bands.py` | User-facing WSPR bands and wspr.live band identifiers. |
| `config/demos/*.config` | Authoritative guided demos. Each file is an ordinary standalone configuration; lexicographic filename order defines launcher order. |
| `config/demo_profiles.py` | Dependency-free demo discovery, validation, duplicate-ID protection, stable filename ordering, and `DEMO_PROFILES` compatibility export. |
| `config/config_schema.py` | Version-1 saved-configuration format identifier, schema version, grouped settings contract, and canonical enum values shared by demos and user files. |
| `config/config_codec.py` | Dependency-free document-envelope and schema-version validation shared by demo and upload readers. |
| `config/wspradar-config.schema.json` | Formal JSON Schema for every standalone saved or demo configuration. |
| `config/guided_input_flow.json` | Ordered, conditional Guided Input steps and registered renderer keys. |
| `config/guided_input_flow.schema.json` | Strict JSON Schema for the declarative Guided Input flow. |
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
- Ordinary query-cache TTL: 3600 seconds.
- Guided-demo query-cache TTL: 86400 seconds from publication; cache reads do
  not extend this absolute freshness window.
- Fresh guided-demo runs prefer the configured-first provider with a complete
  zero-request cache bundle before normal network-backed provider selection.
- Session-artifact TTL: 3600 seconds, with active leases and access touches.
- WSPR database priority: wspr.live, WD2, then WD1; each currently has a
  process-local 20-request/60-second application budget.
- Session inspector cache budget: 5 MiB.

These limits come directly from `config/app_config.py`; change them there and
update the associated regression tests.

Saved configurations and demos use the same strict standalone JSON document
identified by `format: "wspradar.config"`. Its optional `profile` object carries
a stable ID plus localized title and description, while its `settings`
object mirrors the durable UI sections: `core_parameters`,
`comparison_parameters`, `advanced_parameters`, and `results_view`. Every
applicable setting is explicit, but fields belonging to an inactive time or
comparison branch are omitted rather than copied from hidden widget state.
Loading first resets inactive controls to application defaults and then applies
the validated active branch, so a file cannot inherit stale values from the
preceding session.

The current runnable configuration schema is version 1 and remains explicitly
pre-production. It is not the first public production contract and may be
revised in place until the first production release; earlier unpublished
version-1 documents may therefore be rejected without migration. TX Hardware
Every active comparison stores `snr_correction_mode` separately from
`snr_correction_db`. `no_offset` and `establish_offset` require an applied
correction of exactly `0.0 dB`; `established_offset` carries a documented signed
value and may explicitly carry a genuinely established `0.0 dB`. Dynamic Local
Neighborhood comparisons support `no_offset` and `established_offset` but not
the controlled offset-establishment workflow. Success-only configurations omit
both fields. Applicable unpublished version-1 documents that lack the mode are
rejected rather than interpreted from an ambiguous numeric zero.

TX Hardware A/B settings select a `tx_ab_method`. The simultaneous branch stores
the distinct `reference_callsign` and derives both paths' grid-4 from the core Target QTH, so
it does not serialize a redundant `reference_qth`. The sequential branch uses a
shared `repeat_interval_minutes` plus disjoint `target_start_minute` and
`reference_start_minute` phases. The visible UI names these three controls
**Repeat Interval**, **Target Start**, and **Reference Start**; supported
intervals are 4, 6, 10, 12, 20, 30, and 60 minutes, starts are even phases below
the selected interval, and new sessions default to 10, 0, and 2 minutes
respectively. Scheduled transmissions are paired by their planned starts; the
unpublished fixed-bin prototype is not part of the public contract.

`results_view` is divided into `success` and, when applicable, `compare`.
It preserves each branch's Segment Inspector range/direction, selected-station
chronological time bin, and station-selection intent. Explicit stations use
canonical callsign/locator pairs, while `all` dynamically selects the complete
reconstructed table under the saved visibility controls. Compare also preserves
its selected temporal view, segment time bin, and `show_non_joint`; Success
preserves `show_zero_target`. Table filters, Drill-Down filters, and other
transient UI state remain outside the config contract. Optional non-core data
belongs under `extensions` and is preserved across load and re-save.

`config/config_codec.py` owns document-envelope and current-version validation;
`ui/config_io.py` owns semantic settings validation, Streamlit-state
application, and writing. No migration is promised between unpublished
pre-production version-1 revisions. Once a configuration schema is published
for production, each subsequent schema bump must add ordered migrations from
every preceding supported production version before the writer changes.
Unsupported versions are rejected instead of being interpreted with guessed
defaults. The formal JSON Schema enumerates valid fields, values, and
conditional branches.

Guided and Classic are two editors over the same canonical Streamlit session
fields; neither owns a separate scientific configuration. The selected
`input_view` and Guided navigation choices are transient session UI state and
are not added to the version-1 saved-config contract. Correction mode is durable
operator/configuration provenance rather than navigation state: both editors
preserve it, Guided renders its choice from the canonical mode, and Classic
numeric edits generically select `established_offset` when a nonzero value is
entered. Only the numeric correction enters `AnalysisContext` and scientific
request identity. Guided reconstructs its question branch from canonical values
after loading a personal configuration or demo. Its order and conditions come
from the schema-validated
`config/guided_input_flow.json`, while registered Python renderers and the
separate bilingual `GUIDED_INPUTS` content in `i18n.py` provide controls and
novice explanations. A run produces exactly one active result family: Success
when no benchmark is selected, or Compare when any benchmark is selected.

`config/demo_profiles.py` discovers regular `config/demos/*.config` files in
lexicographic filename order. The filename is an opaque ordering key and is
independent of the document's required, stable `profile.id`. Profile IDs are
opaque identity and may participate generically in demo/cache ownership; they
must never act as runtime feature flags or select record-specific behavior. A
configuration saved by the UI can therefore become a demo without format conversion: choose
any `.config` filename that places it at the desired launcher position and put
it in that directory. Installed demos require `profile.title.en` and, when a
description is supplied, `profile.description.en`. German `de` values are
optional; the launcher falls back to English when they are absent. Description
strings accept GitHub-flavored Markdown links, and JSON `\n` escapes render as
visible line breaks. Raw HTML remains escaped by the Streamlit caption renderer.

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
2. Use Guided Input (the default) for the question-led workflow, switch to
   Classic for direct access to all controls, or load a demo into either view.
3. Run the single direction-aware analysis action.
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

`AnalysisContext.max_peer_distance_km`, displayed as **Maximum peer distance
from Target (km)**, is scientific rather than presentation state.
Post-fetch processing retains only peer rows strictly nearer than this
great-circle distance from Target QTH before scientific thresholds,
aggregation, session artifacts, and exports. The map, footer, and Segment
Inspector consume that same retained population, and Inspector controls cannot
widen it. Target-Active eligibility and moving-station integrity remain
geographically global checks on the otherwise eligible population before
distance scope; in Compare, they follow solar selection in moving-then-activity
order. Provider SQL responses and raw-query cache entries likewise remain
global across scope choices.

The runtime source directories are regular Python packages with committed
`__init__.py` markers. Preserve those markers: Streamlit watches a PEP 420
namespace package as a directory, and first-import `__pycache__` writes inside
that watched directory can otherwise cause overlapping cold-start reruns.

Useful files when tracing behavior:

- `ui/run_controller.py`: end-to-end analysis orchestration.
- `core/analysis_runner.py`: SQL and post-fetch analysis contracts.
- `core/geographic_scope.py`: strict great-circle peer-scope validation and
  vectorized post-fetch filtering.
- `core/tx_ab_schedule.py`: periodic TX A/B validation, exact schedule SQL, and
  stable planned-pair assignment.
- `core/data_engine.py`: bounded upstream HTTP and query cache.
- `core/provider_dispatch.py`: provider priority, rolling request reservations,
  circuit cooldowns, and complete-run leases.
- `core/run_data_preparation.py`: transactional source-pinned fetch,
  strict/legacy selection, processing, and unpublished artifact staging.
- `core/compare_engine.py` and `core/opportunity_engine.py`: scientific
  aggregation and classification.
- `core/map_data.py` and `core/plot_engine.py`: pure map aggregation and
  presentation rendering.
- `ui/components/segment_inspector.py` and `ui/inspector/`: inspector
  orchestration and pure view models.
- `ui/components/config_fields.py`: shared canonical field-composition surface
  used by Guided and Classic without duplicating scientific controls.
- `ui/guided_inputs/`: validated flow loading/evaluation, transient Guided
  state, summaries, and Streamlit accordion composition.
- `ui/config_io.py` and `ui/config_save.py`: shared versioned-config semantics,
  fragment-scoped profile/save controls, and relative-versus-frozen Last-X
  writing.
- `ui/results_export.py`: lazy export recipe execution and ZIP construction.
- `ui/analysis_submission_state.py`: lightweight, token-aware in-flight analysis
  ownership used to guard Streamlit reruns before admission.
- `ui/result_state.py`: lightweight result/export reset and active-run time-window
  lifecycle used by idle configuration callbacks.
- `ui/page_navigation.py`: stable application-region anchors, coarse scroll
  tracking, and one-shot browser navigation requests above the manual boundary.
- `ui/documentation_scroll_trigger.py`: browser viewport, history/navigation,
  and anchor-bounded table-layout controller for demand-driven full-manual
  rendering.
- `core/artifact_store.py`: artifact namespaces and lifecycle.

The separate `tools/Timed-AB-Relay-Switch/` utility has its own README,
requirements, launch wrappers, and local configuration. Do not assume that
changes to it are exercised by the Streamlit regression suite.

## Testing and Checks

Run the complete regression suite:

```powershell
python -m pytest tests/regression -q
```

In automated Windows sessions, use the direct equivalent
`.\.venv\Scripts\python.exe -m pytest tests\regression -q` to run the provisioned
test environment without a `PYTHONPATH` workaround.

Pytest stores its disposable per-run files and cache under the ignored `.test/`
directory. The `.test/pytest-temp/` tree is cleared at the start of each pytest
session, preventing separately named root-level test directories from
accumulating across runs.

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
  queries/<database-source>/
  demo-queries/<database-source>/
  derived-analysis/basemaps/
  session-artifacts/<owner>/run_<id>/
  .artifact-locks/
```

Ordinary query and session artifacts use one-hour access-aware cleanup. Guided
demo query artifacts use a separate 24-hour absolute freshness lifetime: reads
do not touch their publication timestamp. Demo Compare keeps a process-memory
DataFrame L1 and a Parquet disk L2; demo Success uses the same persistent demo
namespace. Both tiers cache raw provider query results rather than completed
scientific analyses, and provider identity remains part of every query-cache
key. Geographic Analysis Scope is intentionally absent from this raw-query
identity because its scientific filtering happens post-fetch; the scope remains
part of the canonical analysis request and processed artifacts. Before issuing
demo requests, provider selection prefers the first enabled
source that can supply the selected active result's complete current
strict/legacy request bundle from fresh cache. The selected cache retains its
actual provider origin;
artifacts are neither relabelled nor combined across sources. Loading a built-in
demo establishes this demo identity without immediately running it; the normal
Run action preserves the identity while its scientific controls remain
unchanged, and a scientific edit returns the configuration to ordinary cache
policy. Derived basemaps
are shared across sessions and are not currently subject to TTL cleanup. Process
memory also holds the query DataFrame LRU, admission state, inspector session
models/PNGs, generated documentation PDF cache, and provider rolling-request,
reservation, cooldown, and half-open probe state.

Runtime TTL cleanup is process-local single-flight. After a successful sweep,
further triggers are suppressed for 60 seconds; a failed sweep can be retried
immediately. Physical deletion can therefore lag a freshness deadline even
though an expired artifact is no longer reusable. A live sweep ignores atomic
temporary siblings, reaps only recognized abandoned siblings older than the
stale-lock horizon while holding the corresponding destination lock, and
retains empty namespace directories so pruning cannot race a writer. Published
query files are checked against a fresh clock reading with a five-second
tolerance before a future modification time is treated as invalid.

Structured fetch-failure telemetry records a safe lifecycle stage and, when a
cache artifact is involved, its namespace and freshness policy. The performance
event deliberately does not duplicate the SQL text or captured error body.

Deleting `.wspr_cache` is safe only when no active process is using it. The next
request will rebuild missing query, basemap, or session artifacts.

## Known Limitations and Risks

- The application depends on the availability and compatible behavior of the
  public wspr.live, WSPRDaemon WD2, and WSPRDaemon WD1 ClickHouse HTTP services.
  One complete run is pinned to one source; a provider failure restarts its full
  unpublished data bundle on the next source.
- Analysis/export admission and duplicate tracking are process-local. Multiple
  application processes do not share a global queue, provider circuit, or
  request budget. The WD budgets are conservative application settings, not
  documented upstream quota guarantees.
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
- In-memory caches are lost on process restart. Query and session disk artifacts
  survive only when the hosting environment retains `.wspr_cache`.
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
