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

- TX and RX Performance analyses that compare target opportunities with signals seen
  by other active stations.
- TX and RX comparison analyses for local/reference setups, hardware A/B cases,
  and deterministic scheduled TX A/B pairs.
- Interactive configuration through a novice-oriented Guided Input flow or the
  full Classic editor, with English and German presentation in both views.
- Geographic station and segment aggregation on an azimuthal-equidistant map.
- Segment Inspector views with station tables, evidence figures, and drilldown
  tables backed by projected Parquet reads.
- Optional Benchmark Delta-SNR outlier-candidate reporting at native Joint Spot
  or complete Scheduled Pair resolution, with robust local baselines,
  duration-descriptive grouping, path/cross-path review, and traceable paired
  evidence. Enabled exports add a qualified path-event summary and its linked
  chronological paired-evidence table; disabled exports retain the historical
  package contract without outlier files or metadata.
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
| `config/delta_snr_outlier.py` | Validated policy, defaults, ranges, and stable signature for optional Delta-SNR outlier-candidate reporting. |
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
- Delta-SNR outlier reporting defaults off. When enabled for Benchmark, its
  shared gates default to `6.0 dB` minimum absolute departure, `3.0` minimum
  robust z-score, and `3.0 dB` maximum pre/post baseline difference; each
  numeric setting accepts `0.1` through `100.0` inclusive.
- New untouched interactive Performance setups enable special-callsign and
  moving-station exclusion; untouched Benchmark setups disable both. A manual
  toggle edit remains explicit across result-family changes, while saved
  configurations, demos, and URLs retain their required explicit values.
- Maximum accepted result per analysis query: 1,000,000 rows; a max-plus-one
  SQL sentinel detects larger results before scientific processing.
- Analysis admission: 2 active, 10 queued, 600-second queue wait.
- Export admission: 1 active, 10 queued, 600-second queue wait.
- CSV and Parquet decompressed response ceiling: 64 MiB each.
- HTTP connect timeout: 10 seconds; read-inactivity timeout: 60 seconds.
- Ordinary query-cache TTL: 3600 seconds.
- Guided-demo query-cache TTL: 86400 seconds from publication; cache reads do
  not extend this absolute freshness window.
- Process-wide raw-query DataFrame L1: 64 MiB total, 16 MiB per entry, and 32
  entries; larger accepted results remain reusable from the disk L2 without a
  second retained DataFrame copy.
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
applicable setting is explicit. The time selection always contains exact
absolute `start_utc` and `end_utc` boundaries; fields belonging to an inactive
comparison branch are omitted rather than copied from hidden widget state.
Loading first resets inactive comparison controls to application defaults and
then applies the validated active branch, so a file cannot inherit stale values
from the preceding session.

The current runnable configuration schema is version 1 and remains explicitly
pre-production. It is not the first public production contract and may be
revised in place until the first production release; earlier unpublished
version-1 documents may therefore be rejected without migration. TX Hardware
Every active comparison stores `snr_correction_mode` separately from
`snr_correction_db`. `no_offset` and `establish_offset` require an applied
correction of exactly `0.0 dB`; `established_offset` carries a documented signed
value and may explicitly carry a genuinely established `0.0 dB`. Dynamic Local
Neighborhood comparisons support `no_offset` and `established_offset` but not
the controlled offset-establishment workflow. Performance-only configurations omit
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

`results_view` is divided into `performance` and, when applicable, `benchmark`.
It preserves each branch's Segment Inspector range/direction, segment temporal
time bin, selected-station chronological time bin, and station-selection intent.
Explicit stations use canonical callsign/locator pairs. Performance accepts
`null`, an empty list, or one identity. Benchmark uses the same singleton
contract normally, but accepts an ordered list of distinct identities while
optional Delta-SNR outlier reporting is enabled so one review card can be
opened in Station Insights. `"all"`, duplicates and malformed identities are
rejected without migration. `null` retains the normal initial table behavior,
while an empty list records deliberate deselection. Benchmark additionally
preserves `show_non_joint`; Performance preserves the canonical
`show_zero_target` field. Table filters, Drill-Down filters, and other transient
UI state remain outside the config contract. Optional non-core data belongs
under `extensions` and is preserved across load and re-save.

Benchmark advanced parameters preserve the outlier-reporting toggle and, only
when it is enabled, the three shared detector gates. The normal
configuration-changed lifecycle applies: editing these controls does not run an
analysis automatically. New analyses default to `6.0 dB`, `3.0`, and `3.0 dB`.
Version-1 saved configurations and public URLs that omit those fields retain
their original `3.0 dB`, `4.0`, and `3.0 dB` meaning; current writers serialize
the changed values explicitly.

`config/config_codec.py` owns document-envelope and current-version validation;
`ui/config_io.py` owns semantic settings validation, Streamlit-state
application, and writing. No migration is promised between unpublished
pre-production version-1 revisions. Once a configuration schema is published
for production, each subsequent schema bump must add ordered migrations from
every preceding supported production version before the writer changes.
Unsupported versions are rejected instead of being interpreted with guessed
defaults. The formal JSON Schema enumerates valid fields, values, and
conditional branches.

Local Neighborhood uses Local Median Neighborhood in both input views. The
scientific method remains explicit as `local_benchmark: "local_median"` in
saved configurations and public URLs, even though there is no method selector.
Unsupported local-method values are rejected at configuration, URL, and core
analysis boundaries; explicit invalid session values are retained for validation
until the operator resets the configuration. The neighborhood median retains
one contribution per observed local callsign-and-locator identity and permits
a single contributor for a remote peer-cycle.

Guided and Classic are two editors over the same canonical Streamlit session
fields; neither owns a separate scientific configuration. The selected
`input_view`, four-way Classic Question, and Guided navigation choices are
transient session UI state and are not added to the version-1 saved-config
contract. Classic asks RX/TX Performance or RX/TX Benchmark first, then reuses
the shared Target/window fields and conditionally requires a Benchmark design.
While Benchmark intent is selected but its design is still absent, Run, Save
Config, and public-URL synchronization remain gated, while the advanced panel
explicitly uses Benchmark thresholds rather than interpreting canonical
`val_comp_mode = "none"` as an operator-selected Performance setup. Correction
mode is durable
operator/configuration provenance rather than navigation state: both editors
preserve it, Guided renders its choice from the canonical mode, and the shared
Classic/Guided correction text field accepts point-decimal input, normalizes it
into the canonical numeric value, and generically selects `established_offset`
when a nonzero value is entered. Only the numeric correction enters
`AnalysisContext` and scientific
request identity. Guided reconstructs its question branch from canonical values
after loading a personal configuration or demo. Its order and conditions come
from the schema-validated
`config/guided_input_flow.json`, while registered Python renderers and the
separate bilingual `GUIDED_INPUTS` content in `i18n.py` provide controls and
novice explanations. A run produces exactly one active result family: Performance
when no benchmark is selected, or Benchmark when any benchmark is selected.

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

Publication comparison PDFs can be linked directly in a demo description using
`[Compare the publication, reconstruction and WSPRadar view (PDF)](app/static/reference_figures/<fixture-folder>/<figure>.pdf)`.
The corresponding source PDF belongs in
`tests/regression/reference_fixtures/<fixture-folder>/` and its fixture manifest.
Run `python scripts/sync_reference_figure_pdfs.py` after rebuilding a figure or
adding a link, then commit the generated copy under `static/reference_figures/`.
Run the same command with `--check` to verify every linked copy against the
source PDF and fixture hash. Links in demo descriptions determine the published
set; there is no demo-ID mapping, runtime schema change, or PNG dependency.
Streamlit serves these files locally and on deployments through the existing
`enableStaticServing` setting. Original publication images remain raster panels
inside the PDFs; reconstructed points, bars, axes and annotations retain vector
geometry. Keep the PNG companions for visual review until explicitly removed.

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
distance scope; in Benchmark, they follow solar selection in moving-then-activity
order. Provider SQL responses and raw-query cache entries likewise remain
global across scope choices.

The runtime source directories are regular Python packages with committed
`__init__.py` markers. Preserve those markers: Streamlit watches a PEP 420
namespace package as a directory, and first-import `__pycache__` writes inside
that watched directory can otherwise cause overlapping cold-start reruns.

Browser fonts are bundled under `static/fonts/`, with the upstream licenses
and source URLs recorded there. Keep `server.enableStaticServing` enabled so
the existing Rajdhani and Space Mono faces resolve from `app/static/fonts/`.
Custom icons reuse Streamlit's bundled Material Symbols Rounded font; do not
restore the former Google Fonts import or reference a private hashed Streamlit
asset URL. The header uses `img/WSPRadar-140x140.png`, while the original logos
remain available alongside it.

The idle-import regression checks framework-induced imports as well as direct
WSPRadar imports. Keep plain sequence values in the three browser-controller
payloads as tuples: their browser JSON is unchanged, but Streamlit 1.58 does
not invoke scientific DataFrame detection for them.

Useful files when tracing behavior:

- `ui/run_controller.py`: end-to-end analysis orchestration.
- `core/analysis_runner.py`: SQL and post-fetch analysis contracts.
- `core/callsign_filters.py`: shared direction-specific remote-peer SQL
  exclusions using the fixed prefix policy in `config/app_config.py`.
- `core/analysis_plan.py`: dependency-light, immutable execution plans with
  validated mode, time-window, and strict/legacy query provenance; existing
  scientific consumers retain mapping reads without copying the plan.
- `core/completed_run.py`: immutable completed-run metadata and the explicit
  version-2 snapshot codec; records contain artifact references, never evidence
  DataFrames or figures.
- `core/geographic_scope.py`: strict great-circle peer-scope validation and
  vectorized post-fetch filtering, plus conservative date-line/pole-aware
  bounding boxes for the SQL Local Neighborhood prefilter.
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
- `core/map_data_artifacts.py`: versioned persistence and validation of compact
  station/segment render aggregates for completed-run rerenders.
- `ui/result_hierarchy.py` and `ui/result_guidance.py`: semantic result-flow
  presentation, scope copy, and bilingual mode-aware interpretation help.
- `ui/components/segment_inspector.py` and `ui/inspector/`: inspector
  orchestration and pure view models.
- `ui/inspector/contracts.py`, `ui/inspector/preparation.py`, and
  `ui/inspector/presentation.py`: explicit completed-run/scope inputs, the
  run-scoped cache and artifact-read coordinator, and pure localized recipe
  labels/summary formatting.
- `ui/components/inspector_scope.py`, `inspector_stations.py`,
  `inspector_outliers.py`, and `inspector_selected.py`: focused views inside the
  existing Inspector fragment. `inspector_common.py` shares table and figure
  presentation; `inspector_export.py` preserves the existing registration
  boundary for prepared outputs.
- `ui/inspector/outlier_candidates.py`, `ui/inspector/outlier_report.py`, and
  `ui/inspector/outlier_export.py`: optional native-paired-unit detection,
  cross-path review aggregation, the pure localized Outlier Report view model,
  and fixed-schema event-path/paired-evidence export projections.
- `ui/components/config_fields.py`: shared canonical field-composition surface
  used by Guided and Classic without duplicating scientific controls.
- `ui/analysis_question_state.py`, `ui/classic_input_state.py`, and
  `ui/classic_inputs.py`: atomic four-way question transitions, transient
  Classic readiness, and question-first Classic panel composition.
- `ui/guided_inputs/`: validated flow loading/evaluation, transient Guided
  state, summaries, and Streamlit accordion composition.
- `ui/config_io.py` and `ui/config_save.py`: shared versioned-config semantics,
  fragment-scoped profile/save controls, and canonical absolute UTC-window
  writing.
- `ui/time_window.py`: once-per-session absolute UTC defaults, widget-state
  quantization, and effective-window validation.
- `ui/url_state.py`, `ui/url_synchronizer.py`, and `ui/share_analysis.py`:
  versioned public-URL adaptation through canonical config validation,
  fragment-safe browser synchronization, and data-only sharing controls.
- `ui/results_export.py`: lazy export recipe execution, conditional localized
  outlier-table serialization, and ZIP construction.
- `ui/analysis_submission_state.py`: lightweight, token-aware in-flight analysis
  ownership used to guard Streamlit reruns before admission.
- `ui/result_state.py`: lightweight result/export reset, database provenance,
  and completed-run snapshot lifecycle used by idle configuration callbacks.
- `ui/run_lifecycle.py`: named transitions for scientific edits, configuration
  replacement, run initialization, presentation handoff, failure, rendering,
  and completion; in-flight submission ownership remains token-aware.
- `ui/inspector/selection.py`: immutable exact station identities and Inspector
  selection intent, with shared scope, station, and time-bin validation.
- `ui/inspector/selection_state.py`: the dependency-light owner of durable
  Inspector selection values, transient widget synchronization, station
  defaults/deselection, outlier navigation, and separate candidate/zoom state.
  Configuration loading and lifecycle callbacks delegate their selection
  mutations here; the existing Inspector fragment consumes its typed record.
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

Run the complete regression suite on Windows through the foreground-only
repository runner:

```powershell
.\scripts\run_regression.cmd
```

The launcher applies `-ExecutionPolicy Bypass` only to the checked-in runner;
it does not change the user or machine execution policy. The runner validates
its five fixed serial fallback chunks, invokes
`.\.venv\Scripts\python.exe -u -m pytest` in the foreground without activation
or a `PYTHONPATH` workaround, and returns pytest's exit code. Use
`.\scripts\run_regression.cmd -ValidateChunks` to validate the partition and
`.\scripts\run_regression.cmd -Durations 30` to profile a canonical serial run.
If one complete foreground session cannot be retained, run `-Chunk 1` through
`-Chunk 5` serially; do not run chunks concurrently because they share the
`.test` workspace.

On Linux or macOS, invoke pytest directly:

```bash
python -m pytest tests/regression -q
```

The page-navigation event regressions execute the production JavaScript with
Node.js when `node` is available on `PATH`. Include Node.js to run those event
scenarios; otherwise pytest explicitly skips them. WSPRadar's application
runtime does not require Node.js.

pytest-xdist is not part of the development environment. Do not install it or
pass `-n` until the concurrency, filesystem, Streamlit, Matplotlib, cache, port,
and process-state tests have been audited for worker isolation.

For incremental work, select the directly affected test modules according to
the focused-verification contract in `AGENTS.md`. Figure, PDF, Streamlit
integration, and export-package tests are intentionally omitted from unrelated
focused runs; they remain mandatory when their implementation or direct callers
change and whenever the full-verification rules apply.

Pytest stores its disposable per-run files and cache under the ignored `.test/`
directory. The `.test/pytest-temp/` tree is cleared at the start of each pytest
session, preventing separately named root-level test directories from
accumulating across runs.

Focused verification on 2026-09-24 added the mandatory G3ZIL/G4HZX temporal
reference fixture. The new module and the existing prepared-export integrity,
segment temporal evidence, evidence-statistics and runner tests reported
**57 passed, 1 skipped, 1 existing warning in 28.07 seconds**. After making the
axis assertions explicitly UTC, the new module separately reported
**8 passed, 1 existing warning in 9.61 seconds**, with 2.82 seconds for its
shared numerical preparation. The skip still belongs to the absent
prepared-export package; the new scientific reference never skips. Four
temporary in-memory faults were rejected: reversed Delta SNR, a three-hour
timestamp shift, means substituted for bin medians, and an omitted geographic
filter. The 82-module chunk manifest, changed-test compilation and whitespace
checks passed. This was a test/data and engineering-documentation addition;
application runtime code was unchanged, so a full-suite or browser run was not
required for this focused work.

The companion Figure 6 fixture was integrated later on 2026-09-24 using the same
reference module. Both publication cases and the directly related modules
reported **69 passed, 1 skipped, 1 existing warning in 21.75 seconds**. Eight
in-memory erroneous results/configuration choices were rejected by the actual
reference assertion helpers: means, station-hour or date-hour medians used in
place of pooled medians; shifted UTC hours or density cells; reversed Delta SNR;
an extended final-hour boundary; and an omitted geographic cutoff. These checks
did not mutate application source or frozen expectations. The Figure 3 fixture
remained unchanged, and the same 82-module manifest registration applies.
Changed-test compilation and whitespace checks passed. This focused addition
changed only tests, fixture data and engineering documentation; full-suite,
browser and database-SQL checks were not performed.

The subsequent external Figure 6 source-image addition on 2026-09-24 passed
the same focused module set with **82 passed, 1 skipped, 1 existing warning in
25.03 seconds**. All 33 Griffiths reference tests are mandatory, including nine
paper-density sensitivity cases, qualitative density ordering and three
independently digitized isolated-point witnesses. Expected source positions
and tolerances remained fixed after their first comparisons. Five in-memory
faults were rejected: reversed Delta SNR, constant +5 dB differences, a +4 dB
offset, a six-hour UTC density shift and a uniform density grid. The 82-module
manifest, changed-test compilation and whitespace checks passed. The prior
archive fixtures and application runtime were unchanged; no full-suite,
browser, live-provider or SQL-execution run was performed for this addition.

Latest complete regression verification on 2026-09-25 covered the publication
comparison PDF additions, expanded Figure 3 tail review, demo PDF links and all
existing reference fixtures. The complete foreground Windows runner reported:

```text
3140 passed, 1 skipped, 3 xfailed, 1 warning in 359.67 seconds
```

The skip remains the absent prepared-export package; the three strict expected
failures remain the documented Griffiths paper/strongest-pair differences.
The warning is the existing Matplotlib `set_bad` pending deprecation. All eleven
reference-fixture manifests, full source compilation and whitespace checks
passed. The seven published PDF copies match their fixture sources and are
served as `application/pdf` with HTTP 200. Browser inspection confirmed the demo
links resolve to those routes and open in a new tab; the automation browser's
embedded viewer could not display PDFs, so visual inspection used Poppler
renderings. Each comparison PDF contains native generated plot geometry and
searchable text, with only its original publication panel stored as an image.
Existing demo settings and description text are preserved; no scientific
runtime calculation or frozen numerical oracle changed.

Previous complete regression verification on 2026-09-23 covered the shared remote-peer
special-callsign filter in `C:\Users\marku\Code\WSPRadar`, together with the
pre-existing working-tree changes to historical decode compatibility. The
complete foreground Windows runner reported:

```text
2996 passed, 1 skipped, 1 warning in 271.58 seconds
```

The warning is the existing Matplotlib pending deprecation. All 24 focused
peer-filter regression cases also passed. Generated Target/Reference predicates
were executed with SQLite for every supported Benchmark design and RX/TX
Performance, checking all three prefixes, enabled/disabled filtering, historical
fallback, and special-prefix Target, Reference and local-reference contributors.
The Performance check also preserves Target activity established through an
excluded remote peer. These are local predicate checks, not live ClickHouse
measurements. Full Python compilation, the runner's regression manifest
validation, README synchronization, JSON syntax and patch whitespace checks
passed. The full suite includes documentation rendering, localization, shared
Guided/Classic state, export and idle-import contracts. No live archive query,
browser walkthrough or deployment test was performed for this change.

The updated filter guidance is a completed co-authored English/German
integration under the approved remote-peer-only specification. Review covered
the manual filter row, shared tooltip, Guided explanation and compact review,
including RX/TX direction, eligible analysed endpoints and unchanged defaults.
German uses the established `Referenz` terminology. No semantic divergence or
unmatched unit remains in this scope. Integrated manual source SHA-256 hashes:

- `docs/doc_en.py`: `C789C9228E5F8133FBC60E57F4790A6A86B0FA4D253B1A82E450FE8CD1F871A7`
- `docs/doc_de.py`: `6E5288452C91F022C470988C37E75620F3C7C1529E6582D4DE6DE7F21AF4C02B`

Earlier regression verification on 2026-09-14 covered the initial-page import
boundary, bundled browser fonts, and the 140-pixel logo in
`C:\Users\marku\Code\WSPRadar`. The complete foreground Windows run reported:

```text
2887 passed, 1 skipped, 1 warning in 344.08 seconds
```

The warning is the existing Matplotlib pending deprecation. The focused
navigation, URL, documentation-controller, styling, and idle-import checks also
passed all 83 tests. Full Python compilation, the 81-module/five-chunk manifest,
and patch whitespace checks passed. The fresh-process audit confirms that the
idle app leaves NumPy, pandas, and PyArrow unloaded, including indirect framework
imports; controller payload JSON remains identical.

A bounded local Streamlit smoke check returned HTTP 200 `ok`, and all 15 bundled
font subsets returned HTTP 200 with exact file bytes. This Windows environment
labels those static fonts `application/octet-stream`; the Chromium browser check
rendered the intended text and icon styles without browser errors and confirmed
the header image's natural dimensions are 140 by 140 pixels. The temporary browser
and server were closed, with no matching server process remaining. These checks
do not establish deployed cold-browser timings or other browser/platform results.
The new PNG is 56,544 bytes versus 114,598 bytes for the original; its base64
payload is 75,392 bytes versus 152,800 bytes. Original logo files remain intact.

Earlier regression verification on 2026-09-14 covered the shared Guided/Classic
stale-result fix in `C:\Users\marku\Code\WSPRadar`. The complete foreground
Windows run reported:

```text
1 failed, 2882 passed, 1 skipped, 2 warnings in 415.47 seconds
```

The sole failure was an indentation-sensitive source assertion in
`test_url_state.py`; the new results-region context changed indentation without
changing the tested readiness condition. That assertion now compares the Python
syntax tree, and the complete affected module then passed all 88 tests in
2.65 seconds. No runtime code changed after the full run. The absent scientific
fixture remains skipped. The full-run warnings were the existing Matplotlib
pending deprecation and a local pytest cache-directory permission warning;
disabling cache writes for the follow-up produced an unused `cache_dir` option
warning. Full repository compilation and patch whitespace checks passed.

The full run used Node.js on `PATH` and fresh ignored temporary/cache paths
(`.test/pytest-stale-results-final` and
`.test/pytest-stale-results-final-cache`). Browser verification used the actual
app shell, configuration controls, map-block renderer, navigation controller,
and deferred Inspector placement with synthetic map data and controlled local
preparation delays. Guided-to-Classic, Classic-to-Guided, and Benchmark-to-
Performance transitions produced no misplaced or duplicate result headers.
Old maps cleared before a fresh run; the current map remained visible while
Inspector preparation waited. Status and first-map landings remained near the
80 px offset. A completed-result rerender retained exactly the measured scroll
position (1838.5966 px) and Inspector heading position (362.8015 px) during
preparation and after completion. The real app entry point returned HTTP 200
`ok`; all temporary browser tabs and bounded servers were closed. No Community
Cloud deployment was performed.

Earlier complete serial verification on 2026-09-14 ran in
`C:\Users\marku\Code\WSPRadar` after the approved processing-panel and first-map
scroll milestones, manual-navigation cancellation, and viewport-preserving
rerenders:

```text
2869 passed, 1 skipped, 1 warning in 295.21 seconds
```

The canonical foreground Windows runner used fresh ignored temporary/cache
directories through `PYTEST_ADDOPTS` (`--basetemp=.test/pytest-navigation-final-full-20260914`
and `--override-ini=cache_dir=.test/pytest-navigation-final-full-cache-20260914`)
because the older default pytest directories were owned by a different local
account. Node.js was on `PATH`, so all navigation event scenarios executed. The
remaining skip is the absent scientific fixture, and the warning is the existing
Matplotlib pending deprecation. Full Python compilation and patch whitespace
checks passed. The actual app started, returned HTTP 200 `ok`, and rendered its
idle interface. A separate controlled Streamlit browser fixture using the
production navigation controller verified status landing before map readiness,
map landing while Inspector preparation was held open, manual-scroll
cancellation, completion without another landing, and an ordinary rerender with
exactly unchanged scroll position. This browser check used synthetic map data;
the full regression suite separately verifies the real run-controller ordering,
first valid map after no-data blocks, token replacement, and failure cleanup.
English and German navigation guidance were updated together and README was
regenerated from the authoritative English manual.

Earlier complete serial verification on 2026-09-14 ran directly in
`C:\Users\marku\Code\WSPRadar` after the approved Performance temporal-key
preparation and shared temporal bar-collection changes. All charts and offered
time-bin variants remain prepared immediately. Temporal layout version 3
invalidates prior preview and prepared-export render caches; scientific recipe
schemas and persisted evidence remain unchanged.

```text
2831 passed, 1 skipped, 1 warning in 296.87 seconds
```

The canonical Windows launcher used
`--basetemp=.test/pytest-temporal-full-20260913` and
`--override-ini=cache_dir=.test/pytest-cache-temporal-full-20260913`, preserving
the existing ownership of older temporary directories. The 81-module manifest,
full Python compilation, tracked patch whitespace and new-file whitespace checks
passed. The suite includes 31 new cases for compact station/time keys, timestamp
resolution, count widening, selected-station raw SNR, categorical identity
matching, caller ownership, exact bar geometry and preview/export raster checks.

Offline comparisons loaded the actual cached Griffiths Performance and Benchmark
analyses from the supplied performance log. The 638,847-row Performance input
produced the exact same complete scope and selected-station recipes for all six
one-hour through 24-hour variants. Eight additional edge cases covered shared
callsigns at different locators, unequal coverage, unused categorical levels,
missing identities, empty evidence, count totals above 255, compatible nonbinary
inputs and unequal selected-station SNR depth. The original artifacts retained
their hashes and timestamps; full-chart comparisons also verified that source
DataFrames were unchanged.

Local timings below are medians of three alternating before/after samples against
saved pre-change functions, with no concurrent test or benchmark run. Renderer
measurements exclude one warm-up per implementation and include figure
construction plus a 100-DPI canvas draw, excluding PNG encoding and browser
painting. They are component measurements, not an end-to-end or concurrent
Community Cloud speedup.

| Component | Before | After | Component speedup |
| --- | ---: | ---: | ---: |
| Performance scope temporal preparation, all six variants | 5.617 s | 4.273 s | 1.31x |
| Performance selected temporal preparation, all six variants | 0.746 s | 0.729 s | Essentially unchanged |
| Performance selected outcome chart, six-hour bins | 1.902 s | 0.832 s | 2.29x |
| Performance scope outcome chart, one-hour bins | 6.473 s | 0.890 s | 7.28x |
| Benchmark scope coverage chart, one-hour bins | 9.376 s | 1.091 s | 8.60x |

The Performance scope's prepared temporal DataFrame decreased from 47,822,160
to 35,351,874 bytes (45.6 to 33.7 MiB, 26.1%). This is the materialized
DataFrame size, not peak process memory. The one-hour Performance scope chart
uses eight bar collections instead of 2,976 Rectangle artists; the Benchmark
scope chart uses twelve collections instead of 4,464 Rectangles.

Eight full-chart comparisons covered Performance and Benchmark, scope and
selected station, English 100-DPI previews and German 300-DPI exports. All
recipes, drawn polygon coordinates, axes and text matched exactly. Seven images
were pixel-identical. One Benchmark selected-station preview differed at 15
bar-edge pixels out of 728,000 (0.0021%) despite exact geometry; the corresponding
export image was identical. Visual inspection found no perceptible change.
No provider requests, commits, pushes, deployment or Cloud load test were made.

Previous complete serial verification on 2026-09-13 ran directly in
`C:\Users\marku\Code\WSPRadar` after selective transfer of the three
correctness fixes and four performance optimizations. The checkout retained its
newer Benchmark folded-date annotation behavior and temporal layout version 2.

```text
2800 passed, 1 skipped, 1 warning in 288.66 seconds
```

The canonical Windows launcher used
`--basetemp=.test/pytest-transfer-20260913` and
`--override-ini=cache_dir=.test/pytest-cache-transfer-20260913`. Its default
temporary and cache directories were owned by another Windows account and
rejected cleanup; the initial focused run therefore had 407 passes and 112
setup errors. The complete successful run supersedes that incomplete check.
Existing directory ownership and permissions were left unchanged.

A local offline AppTest replay used the exact cached `vanhamel_rx_buddy`
observations from the supplied profiling log. The real demo callback launched
the unchanged application before shell rendering, avoiding AppTest's inability
to serialize one existing shell widget for a synthetic second-run button click.
All scientific preparation and chart rendering remained real. The replay
verified all 110 imported project modules originated in the intended checkout.

The replay retained 7,139 evidence rows from 7,166 raw observations, with 75 map
stations and 13 segments. Complete evidence and both map-aggregate frames matched
the original run exactly. The map and all five Inspector PNGs were rendered;
the map read used ten projected columns, no network request was attempted, no
ZIP was prepared, and the original cache contents and timestamps were unchanged.
The recorded analysis duration was 11.650 seconds; the full AppTest execution,
including initial application work, took 15.856 seconds. This is one local
serial replay, excluding browser painting and concurrent Community Cloud load;
it does not establish a controlled end-to-end speedup against the earlier log.

Repeating the same 100,000-row component diagnostics in the intended checkout
gave the following medians of three alternating before/after samples, with exact
result equality checked before timing and no concurrent test or diagnostic run:

| Component | Before | After | Component speedup |
| --- | ---: | ---: | ---: |
| Map geometry and labels | 5.383 s | 0.159 s | 33.8x |
| Solar states, 1,000 distinct timestamps | 6.306 s | 0.069 s | 90.8x |
| Temporal summaries, 1,000 groups | 1.628 s | 0.073 s | 22.4x |
| Local Median Parquet read, five Reference detail entries per row | 0.042 s | 0.037 s | 1.15x |

The projected Local Median DataFrame again decreased from 28,390,132 to
10,190,132 bytes (64.1%). This measures materialized DataFrame size, not process
RSS. Full compilation, patch and new-file whitespace checks, and the 79-module
regression manifest passed. The existing fixture skip and Matplotlib warning
remain unchanged. No commit, push, deployment, or Cloud load test was performed.

Local component measurements in the Codex worktree on 2026-09-13 compared the implemented performance
changes against saved pre-change functions in the same Python 3.12.14 process
(pandas 3.0.3, NumPy 2.4.6). Each timing is the median of three alternating
before/after samples, following an exact-result comparison, without concurrent
pytest or another diagnostic process. All examples contain 100,000 rows:

| Component | Before | After | Component speedup |
| --- | ---: | ---: | ---: |
| Map geometry and labels | 5.983 s | 0.159 s | 37.5x |
| Solar states, 1,000 distinct two-minute timestamps | 6.161 s | 0.074 s | 83.4x |
| Temporal summaries, 1,000 groups | 1.507 s | 0.072 s | 20.9x |
| Local Median Parquet read, five Reference detail entries per row | 0.051 s | 0.038 s | 1.33x |

The map example uses seeded random coordinates plus missing/wrap/boundary cases;
the solar example repeats 1,000 instants starting on 2026-07-01 at Target
coordinates 52.5, 13.4. Temporal summaries use seeded normal values, a missing
value every 197 rows, and three additional empty bins. The random seed is
20260913. Exact quartile interpolation requires two native order-statistic
passes, so its measured speedup is lower than the earlier simple grouped-linear
prototype; the implementation preserves the prior scalar arithmetic.

In the synthetic Local Median example, projecting 12 stored columns to the 10
map-consumed columns reduces `DataFrame.memory_usage(deep=True)` from 28,390,132
to 10,190,132 bytes (64.1%). Complete Reference details remain in the staged
Parquet artifact. This is materialized DataFrame size, not process RSS, and the
read timings include a warm local filesystem cache. These component results do
not establish end-to-end application speedup or Community Cloud concurrency
capacity. No deployment or Community Cloud load test was performed.

Previous complete serial verification in the Codex worktree on 2026-09-13
through the Windows launcher,
under Python 3.12.14, covers map-label lookups, distinct-timestamp solar
classification, exact native grouped quartiles, and map-specific Parquet reads:

```text
2800 passed, 1 skipped, 1 warning in 292.73 seconds
```

The 86 additional cases cover geometry and bin-label equivalence, solar states
and timestamp alignment across analysis modes, exact quartile and dtype
compatibility, and full-versus-projected map aggregates and evidence ownership.
The existing controller lifecycle test also verifies use of the declared map
projection. Full repository compilation, patch/new-file whitespace checks, and
the 79-module serial regression manifest passed. The skipped fixture-integrity
test and Matplotlib pending-deprecation warning remain unchanged.

Previous complete serial verification in the Codex worktree on 2026-09-13
through the Windows launcher,
under Python 3.12.14, covers the admission cache-preparation split, localized
Performance Drill-Down filtering, and explicit export evidence failures:

```text
2714 passed, 1 skipped, 1 warning in 299.99 seconds
```

The 56 additional regression cases cover responsive permit/status operations
during blocked cache preparation, FIFO/provider reservation and timeout cleanup,
localized Target/Counter filters, and failed versus legitimately empty export
evidence. Four seeded Streamlit AppTests exercise the real filter multiselect
and slider in both languages and directions. Full compilation, tracked and
changed-untracked-file whitespace checks, and the 78-module manifest passed.
The worktree reused the existing project virtual environment through an ignored
`.venv` junction. Verification was local; no Community Cloud load test or
deployment was performed.

Previous complete serial measurement on 2026-09-13 through the Windows launcher,
including typed export payloads, detached content ownership, complete package
signatures and unchanged-rerender reuse, under Python 3.12.14:

```text
2658 passed, 1 skipped, 1 warning in 268.70 seconds
```

Full repository compilation, patch/new-file whitespace checks, the 78-module
serial regression manifest, and the idle-import boundary passed. Real Streamlit
AppTests verify that a committed profile edit removes an already rendered stale
download while retaining completed results, and that drafts and identical
commits preserve prepared exports. Export tests cover nested table/recipe
ownership, dtype and numerical precision, duplicate columns, complete content
invalidation, captured queue inputs, stale-publication rejection, current saved
configuration metadata, established schemas and filenames, and shared
preview/export recipes. A bounded startup check returned HTTP 200 with `ok`
and stopped its exact child process.

A local export-bookkeeping diagnostic used seven alternating before/after
samples with representative ten-column tables, a fixed 160 KB numerical recipe,
validated saved configuration, the English translation catalog, and three
session-owned artifacts. Median unchanged registration plus footer time was
16.27/18.11 ms for empty tables, 14.24/18.24 ms for 10 rows, 42.60/21.85 ms for
1,000 rows, and 280.81/35.15 ms for 10,000 rows. Warm footer signatures improved
at every measured size; complete registration checks add 2–4 ms for tiny inputs
whose full recipe/context content was previously omitted. Unchanged Inspector
and map registrations retained their owned blocks and prepared ZIP bytes;
changed map context invalidated the ZIP. These measurements cover export
bookkeeping only, excluding widgets, scientific preparation, network access,
figure rendering and ZIP construction; they are not whole-app latency claims.

Earlier complete serial measurement on 2026-09-13 through the Windows launcher,
including the Inspector preparation coordinator and focused presentation
components, under Python 3.12.14:

```text
2593 passed, 1 skipped, 1 warning in 267.59 seconds
```

Full repository compilation, patch/new-file whitespace checks, the 76-module
serial regression manifest, and the expanded idle-import boundary passed.
The Inspector orchestration module now has 265 lines, with a 99-line page-flow
function. Regression coverage exercises the production component flow,
selection/navigation callbacks, cache reuse, exact identities, native comparison
precision, compact display profiles, exported recipes, and unchanged source-frame
ownership. A real Streamlit scope-control check also passed stable widget keys,
language switching, hidden-widget rehydration, scope tokens, and clearing a
selection back to All. A bounded startup check returned HTTP 200 with `ok` and
stopped its exact child process.

An isolated before/after warm Inspector cache-access diagnostic measured median
lookup time at 7.48/7.22 microseconds with identical 684-byte cached values.
Five samples of 20,000 lookups alternated execution order, with logging stubbed
equally on both paths. This measures cache-access overhead only, not complete
application latency. Existing scientific helpers, cache versions, byte/entry
limits, complete presentation/scientific dependencies, and lazy artifact-read
branches were retained.

Earlier complete serial measurement on 2026-09-13 through the Windows launcher,
including the canonical Inspector selection contract and selection/navigation
state owner, under Python 3.12.14:

```text
2562 passed, 1 skipped, 1 warning in 278.43 seconds
```

Full repository compilation, patch/new-file whitespace checks, the 73-module
serial regression manifest, and the idle-import boundary passed. A bounded
Streamlit startup check returned HTTP 200 with `ok` and stopped its exact child
process. Real Streamlit AppTests exercised scope callbacks, conditional-widget
cleanup, candidate-focus rehydration, manual zoom, explicit Off, and stale
scope handling. The ownership audit allows only Inspector cache writes in the
renderer; selection mutations belong to the new adapter. Scientific and figure
preparation retain their existing implementations.

A local before/after comparison retained the same outcomes across 24 station
selection cases, including automatic selection, deliberate deselection, missing
identities, and exact ordered selections. Median lookup time for 1,000 rows
with one selected station was 12.39/10.82 milliseconds; eight selected stations
measured 12.87/11.31 milliseconds. The new path includes construction and
validation of `InspectorSelection`. A separate isolated 10,000-row comparison
measured 111.30/109.25 milliseconds for one selected station and
110.51/105.98 milliseconds for eight. Each comparison alternated execution
order over five samples of ten lookups. The adapter avoids the former temporary
two-column DataFrame allocation and reuses already validated station identities.
These are local lookup diagnostics, not browser-latency or multi-user load
measurements. The initial longer timing probe was stopped without using its
results; the largest fixture was measured again without concurrent verification.

Earlier complete serial measurement on 2026-09-13 through the Windows launcher,
including immutable analysis/completed-run contracts and centralized lifecycle
transitions:

```text
2509 passed, 1 skipped, 1 warning in 279.48 seconds
```

Full repository compilation, the idle-import boundary, and a bounded Streamlit
startup check passed; the health endpoint returned HTTP 200 with `ok`, and the
exact check process was stopped. Independent before/after comparison across 56
plan cases retained identical mappings, scientific fingerprints, and all 112
strict/legacy SQL texts.

A small comparison using three fresh processes per version and the same
browser-component stubs measured median server-side AppTest startup at
2.73/2.76 seconds and warm idle rerenders at 95.5/93.4 milliseconds
(before/after). Warm completed-snapshot reads measured 37.5/0.34 microseconds
after replacing recursive copies with immutable-record reuse. These are local
diagnostic timings, not browser latency or a multi-user load benchmark. The
Windows RSS helper returned unavailable values; no memory-performance result
was established.

Earlier complete serial measurement on 2026-09-13 through the Windows launcher,
including completed-result language switching and manifest-validation coverage:

```text
2440 passed, 1 skipped, 1 warning in 241.86 seconds
```

Earlier complete serial measurement on 2026-09-13, including the Benchmark
callsign-plus-full-locator weighting/support correction and its bilingual
explanations:

```text
2326 passed, 1 skipped, 1 warning in 275.67 seconds
```

Earlier complete serial measurement on 2026-09-13, including the conservative
Local Neighborhood date-line/pole bounding-box correction:

```text
2279 passed, 1 skipped, 1 warning in 263.53 seconds
```

Earlier complete serial measurement on 2026-08-17:

```text
2062 passed, 1 skipped, 1 warning in 234.55 seconds
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
or full regression workflow. The `regression-manifest.yml` GitHub workflow runs
`scripts\run_regression.cmd -ValidateChunks` on Windows for pushes, pull requests,
and manual dispatch, without installing application dependencies. It rejects
unassigned, duplicate, or stale test-module entries before they can break the
launcher. The `wake.yml` workflow opens the deployed application every six hours
and on manual dispatch. Compilation is a syntax check, not a substitute for
static analysis.

To build a regression fixture from an exported demo folder, inspect and use
`scripts/build_regression_fixture_from_demo_folder.py`. Folders placed under
`tests/demo/` are export-intake inputs, not current regression fixtures; only
generated packages under `tests/regression/fixtures/` are active prepared-export
fixtures.

Scientific reference datasets use the separate
`tests/regression/reference_fixtures/` directory. The mandatory
`test_griffiths_temporal_reference.py` replays the first G3ZIL/G4HZX demo from
frozen SQL-result rows through production post-fetch filtering, station
aggregation, paired evidence and temporal recipes. It compares all 57,767
paired observations and the daily, three-hour and folded UTC-hour profiles with
fixed reviewed expectations. Missing or corrupt reference files fail rather
than skip. The fixture README records the paper comparison, captured provider
and historical decode provenance, checksums, and baseline-update rules.
This offline test starts after SQL aggregation; it does not execute SQL or
validate upstream power normalization, provider selection or mode decoding.
The paper corroborates the approximate count and temporal pattern; it does not
supply the fixture's exact expected numerical values.

The same module also replays demo #3 with
`reference_fixtures/griffiths_fig6_diurnal_v1`, covering April 5 through April 7,
2017 at the demo's exact exclusive 23:45 UTC endpoint. Independently reconstructed
source pairs provide 6,459 Joint Spots and the complete folded UTC-hour count,
median, quartile and density profiles, plus chronological 1-hour, 3-hour,
6-hour and daily profiles. A separate 22,000 km replay retains 6,474 pairs with
unchanged hourly medians. Boundary assertions preserve the partial final hour;
exact hourly-profile comparisons preserve pooled-pair weighting, while folding
invariance checks keep the folded result independent of chronological bin
choices. Figure 6 corroborates the nighttime reversal and approximate
daytime advantage, but its density contours are not exact hourly medians.
Its fixture README distinguishes the independently reconstructed source
expectations from the publication's approximate evidence and documents the
remaining paper-count difference. Both reference cases are mandatory, run
offline and share the production replay helpers; neither executes database SQL.

A separate `reference_fixtures/griffiths_fig6_paper_v1` provides executable
external expectations extracted from the original Figure 6 image. Four
digitized contour-region boxes, an independent image review and a frozen
comparison policy precede the application comparison. Tests evaluate the
production folded density grid against those regions with periodic UTC
smoothing across nine fixed bandwidth combinations, require the strongest
density in the published evening island, and check the stated morning/evening
versus midday density ordering. Image-readout and histogram-resolution
allowances are explicit; unspecified author smoothing does not supply an
extra tolerance. These are selected density-feature checks, not recovery of
contour probabilities, exact medians or IQR from the paper. The exact archive
regressions continue to check medians and IQR separately. The first external
comparison passed without moving its source annotations or tuning bandwidths.
Three isolated extreme dots independently extracted from the paper also match
native paired Delta SNR and folded UTC time within fixed pixel-derived
tolerances. These are plotted-point witnesses, not author-supplied station/date
identities or validation of the optional outlier-candidate detector.

The additional `reference_fixtures/griffiths_fig3_paper_v1` freezes original
Figure 3 occupied-region annotations and the paper's first-half daily-average
trend, plus three dated means and two mean extrema digitized from Figure 4.
Source geometry and comparison rules were fixed before application comparison.
The first check exposed a duplicate-weighting distinction: retaining all raw
same-time report combinations reproduces all five Figure 4 anchors and the
April 16 deep negative plume, whereas WSPRadar's maximum-per-receiver policy
does not reproduce the plume or the April 13 mean. These three direct comparison
cases remain strict expected failures restricted to a dedicated comparison
exception; `--runxfail` exposes them as failures. They are documented evidence
unit differences, not successful reproduction or established runtime defects.
Additional ordinary tests verify the alternate raw-report interpretation and
independently recompute the maximum-report difference for every retained
production pair. The source README distinguishes this exploratory explanation
from knowledge of the authors' unavailable query. Original archive fixtures
and runtime calculations remain unchanged; SQL execution is still not tested.
Focused verification on 2026-09-24 reported **100 passed, 1 skipped,
3 xfailed, 1 existing warning in 34.70 seconds** across the reference module
and directly related fixture/evidence/runner modules. The three strict expected
failures are the documented publication-versus-production pairing differences;
the skip remains the absent prepared-export fixture. Compilation, whitespace,
82-module manifest validation and preservation hashes passed. This isolated
addition did not run the complete suite, browser, live provider or database SQL.

The Zander Experiment A reference adds
`test_zander_experiment_a_reference.py` with separate
`reference_fixtures/zander_experiment_a_v1` and `zander_fig4_paper_v1`
packages. A standard-library builder independently reconstructs the fixed
simultaneous TX demo from 731 original reports: 166 Joint receiver-cycles,
37 paired receiver identities, mean -6.783132530120482 dB and sample standard
deviation 3.51463845382668 dB. Paper-only extraction freezes the published
-6.8/3.5 dB annotations and nine visibly distinct histogram regions before
comparison. All external features agree within the original readout allowances;
the final equal-height bars are combined because their internal boundary is
not visible. Exact archive statistics and external paper features remain
separate sources of expectations.

This regression executes the generated production aggregation SQL against
frozen source rows using an in-memory SQLite compatibility adapter, retaining
the real predicates, UNION, groups, normalization and conditional aggregates.
The adapter and a captured native ClickHouse response provide complementary
checks; they do not validate ClickHouse engine behavior or its geographic
distance approximation. The real post-fetch, map/station, Inspector and
Segment Insight histogram calculations then run, with exact paired identities,
SNR components and 1 dB counts checked. A rendered-artist test checks the
right-hand Joint-Spot bar percentages and positions. Deliberate incorrect
mode, normalization, sign, offset and aggregation variants are rejected.

The paper fixture preserves uncertainty about the original date/callsigns,
source population and Figure 4's sample-unit notation. The observed histogram
match corroborates the installed pooled receiver-cycle reconstruction without
claiming recovered author code or direction-independent antenna gain.
The independent builder is `scripts/build_zander_reference_fixture.py`;
expectations are never regenerated by tests. Focused verification on
2026-09-24 reported **138 passed, 3 existing xfailed, 1 existing warning in
57.02 seconds** across Zander, Griffiths and related evidence/runner modules.
The three expected failures remain the documented Griffiths Figure 3 cases;
Zander has no expected failures. The new module is registered once in the
83-module, five-chunk manifest. This isolated test/fixture addition changes no
runtime behavior and does not run the complete suite or a live provider.

The Vanhamel receiver-chain calibration reference adds
`test_vanhamel_calibration_reference.py` and
`reference_fixtures/vanhamel_rx_calibration_v1`. The installed demo now selects
2021-02-06 06:00 inclusive through 2021-02-13 06:00 exclusive in UTC. A separate
standard-library calculator derives 1,143 qualifying Joint observations from
ten transmitter identities, with pooled mean +1.2143482064741906 dB and a
+1.0 dB median for each qualifying transmitter. The external paper supplies
the seven-day calibration design and rounded 1.2 dB average; it does not
identify the dates or averaging weights. Author-supplied shorter February
windows are documented as provenance,
without identifying this reconstruction as the paper's exact original dataset.

The mandatory offline test executes generated production SQL against frozen
raw reports using `tests/regression/reference_sql.py`, the compatibility
adapter also used by Zander. It then exercises post-fetch filtering,
station-threshold selection, Inspector pairing, Joint-Spot and Station Medians
histogram recipes, and seven 06:00-to-06:00 UTC temporal profiles. Independent
expectations pin SQL and retained rows, every qualifying pair and SNR
component, station counts/medians, 1 dB histogram counts, and daily median/IQR
and density. The paper comparison requires the pooled mean in [1.15, 1.25)
dB, an explicit nearest-tenth comparison policy rather than a claimed
measurement uncertainty. Deliberate correction errors that produce displayed
1.3 and 1.4 dB results are rejected, as are incorrect inclusivity changes at
the real source rows on both window boundaries. Exact archive checks also
detect changes that leave the rounded paper mean unchanged. The builder is
`scripts/build_vanhamel_reference_fixture.py`; tests never regenerate the
expected files. This fixture has no duplicate endpoint reports or non-code-1
rows and does not independently validate the native ClickHouse engine.

Focused verification on 2026-09-24 reported **317 passed, 3 existing xfailed,
1 existing warning in 50.07 seconds**, covering Vanhamel, Zander, Griffiths,
configuration/schema, regression-runner, temporal-evidence and evidence-statistic
modules. All nine new Vanhamel checks pass. The three expected failures remain
the documented Griffiths Figure 3 cases. The updated manifest validates 84
modules across five serial chunks; changed Python compilation and whitespace
checks pass. The ten independent expected files regenerate byte-identically.
This demo-data/test addition does not change scientific runtime calculations;
the complete suite and a native ClickHouse replay were not run for this step.

The Vanhamel Figure 6 antenna-rotation reference adds
`test_vanhamel_rotation_reference.py` and
`reference_fixtures/vanhamel_fig6_rotation_v1`. Its stored overlay PNG aligns
the published black trace with 1,441 M7AEO/IO82 paired observations using the
paper's reception-number axis. Seven independently read peaks and troughs
agree within one reception and 0.1 dB; executable paper checks retain the
original graphical tolerances of five receptions and 0.4 dB. The rotation
demo uses +1.6 dB Reference correction, rounding the authors' website value
1.573591164 dB. Both the calibration page and receiver-correction instructions
are linked in the demo and fixture. The paper text states 1.2 dB; neither
the overlay nor the website proves which correction generated the figure.

The independent standard-library builder
`scripts/build_vanhamel_rotation_reference_fixture.py` consumes frozen raw
reports and configuration. Expectations cover all SQL groups and retained
rows, each selected pair's SNR components, twenty reception slices and
before/after summaries. The mandatory offline regression executes generated
SQL through the bounded adapter, production post-fetch and Inspector
selection, and the actual Selected Station Evidence recipe. It checks all
28 twelve-hour counts, medians, quartiles and density cells, including empty
bins, the clipped final time interval and extreme tails. Deliberate wrong
corrections, reversed subtraction, tail clipping and reception-order shifts
must fail. Exact slice statistics are archive-derived expectations reconciled
with the paper, not exact statistics extracted from its raster. The historical
source has no duplicate endpoint reports for the selected path and supplies
no independent outlier-detector classifications. Tests never refresh the
expected files or require network access. `.gitattributes` disables line-ending
conversion for all frozen reference fixtures, preserving their byte-level
checksums across Git checkouts; PNG and Parquet files remain binary.

Focused verification on 2026-09-24 reported **377 passed, 3 existing xfailed,
1 existing warning in 78.32 seconds**, covering all four publication reference
modules plus configuration/schema, regression-runner, evidence-statistics,
segment-temporal and selected-station figure coverage. All thirteen new
Figure 6 checks pass; expected failures remain the documented Griffiths
Figure 3 cases, and the warning is the existing Matplotlib deprecation.
The eight expected files regenerate byte-identically with the standard-library
builder under `python -S`. All eighteen frozen files match the SHA256 manifest
and retain identical hashes with Git clean filters applied. The manifest
validates 85 modules across five serial chunks, and changed Python compilation
and whitespace checks pass. This isolated fixture/demo-data addition does not
change shared scientific algorithms; the full regression suite and native
ClickHouse execution were not rerun for this step.

The Milazzo TX reference adds `test_milazzo_reference.py` and
`reference_fixtures/milazzo_tx_reference_v1`. The demo description now uses
the configured 5,000 km population: 1,069 Only Target, 45 Joint and 21 Only
Reference receiver-cycles, rather than the unrestricted 1,093/46/21 counts.
The scientific demo settings and runtime calculations are unchanged.

The independent standard-library builder
`scripts/build_milazzo_reference_fixture.py` accounts for all 1,992 source
reports and 1,946 receiver-cycle groups, including every non-joint observation
and mutually exclusive activity/distance exclusion. Expected files retain
all raw IDs, normalization components, global activity witnesses, 1,135
native units, 45 pairs, 80 station identities and two sets of 24 three-hour
coverage bins. The regression executes actual generated SQL through the
bounded adapter, checks the historical retry predicate, then exercises
production filtering, station aggregation, Inspector selection, Drill-Down
with and without non-joint rows, and coverage preparation. It preserves null
SNR components for absent endpoints and verifies pooled versus station-balanced
Joint Evidence Share. Removing every Target witness in a real cycle must
remove its Reference-only evidence. VE6PDQ's one pair is independently
hand-calculated at -2 dB; its other retained evidence is 62 Only Target rows.

The separately digitized publication reference preserves 44 Figure 6 markers.
Its exhaustive mapping audit includes all 89 VE6PDQ reports, including the
25 Reference reports excluded by global activity. Only 18 markers have
same-transmitter timestamp candidates within the source-derived tolerance;
none agrees in SNR under the checked raw/30/33/37 dBm interpretations. The
regression checks candidate enumeration and retention linkage, not publication
SNR reproduction. `publication_mapping.md` records that initial TX-direction
investigation without fitting a time shift or SNR offset. Its unresolved
direction conclusion is superseded by the reciprocal RX evidence below.

All ten calculated expected files regenerate byte-identically under
`python -S`. The source CSV preserves the original Parquet values exactly,
including binary coordinate values; all 28 manifest files pass SHA256 and
Git clean-filter byte-preservation checks. The fixed runner validates
86 modules across five serial chunks. Changed Python compilation passes.

Focused verification on 2026-09-24 first passed all **17 new Milazzo tests**.
The related integration run reported **418 passed, 3 existing xfailed and
one failure in 93.63 seconds**: the new demo description lacked the required
spaces around em dashes. After that presentation-only correction, rerunning
the complete Milazzo and configuration modules reported **41 passed in
28.20 seconds**. Both runs emitted the one existing Matplotlib deprecation
warning. The expected failures remain the documented Griffiths Figure 3
cases. Related coverage included all publication reference modules,
configuration/schema, regression-runner, historical decode fallback,
non-joint evidence, temporal coverage and evidence statistics. No shared
scientific calculation changed; the complete regression suite and native
ClickHouse replay were not run for this isolated fixture/demo-copy addition.

The subsequent Milazzo Figure 6 reconciliation adds the separate
`reference_fixtures/milazzo_fig6_rx_v1` fixture. All 44 independently digitized
markers match user-supplied wspr.rocks reports in the reciprocal RX direction:
VE6PDQ transmitting, KP4MD and WB6RQN receiving. All annotated SNRs match
exactly, with a maximum two-minute graphical time residual and no fitted shift.
This contradicts the printed direction; it does not establish a Figure 6/7
image swap. The installed demo remains TX with unchanged scientific settings,
and its description now explains the RX publication reconciliation.

The independent standard-library RX builder regenerates all six calculated
files byte-identically under `python -B -S`. The 86 supplied reports select
44 paper reports and 39 full-identity SQL groups. The production SQL,
filtering and Inspector pipeline retains 34 native units within this bounded
path subset, including five hand-checked pairs with differences +8, +17,
+22, +7 and +7 dB. Three further shared cycles have unequal coarse/fine
transmitter locators and remain unpaired under the existing identity policy.
Graphical tolerance never relaxes synchronization; unknown mode remains null.
The supplied single path does not establish global activity at either receiver.

The later supplied TX tables also match all 89 original VE6PDQ receptions:
63 from KP4MD and 26 from WB6RQN. The complete 90-row KP4MD attachment and the
26 inline WB6RQN 40 m records are retained in the TX fixture. The comparison
checks time, endpoint callsigns and locators, raw SNR and nominal power, without
inferring mode codes or unavailable upstream IDs. This corroborates the frozen
archive through the user's wspr.rocks view, not a separate physical measurement.
The fixture manifests now cover 30 TX files and 13 RX files.

Focused verification on 2026-09-24 passed all **23 Milazzo tests** before the
additional TX-table cross-check. The final focused run, including that added
test, configuration/schema, non-joint evidence, decode fallback and runner
coverage, passed **296 tests with one existing Matplotlib warning in 70.47
seconds**. The final Milazzo module contains 24 tests. Changed Python source
compilation, 86-module/five-chunk manifest validation and whitespace checks
passed. No shared runtime calculation changed; the full suite and native
ClickHouse replay were not run for this fixture and demo-copy update.

The subsequent Milazzo overlay review adds
`reference_fixtures/milazzo_publication_overlays_v1` and
`scripts/build_milazzo_publication_overlays.py`. Original Figure 6/7 images
are retained alongside RX/TX overlays from freshly executed SQL components.
Figure 6 matches all 44 anchors; Figure 7 matches 47 compact image-derived
anchors (32 KP4MD, 15 WB6RQN), with maximum time residual 143.697 seconds and
exact integer SNR agreement on the common 37 dBm scale. These complementary
matches support reversed printed direction labels. All 76 TX archive reports
in the plotted interval remain overlaid, with the extra 19 December 13:38
WB6RQN report flagged. Overlapping markers are not claimed as individually
resolved, and the inferred plotting power basis is explicit.

The lower panels show five eligible RX pairs and one TX pair, separately from
the upper panels' complete endpoint observations before activity gating.
Figure 7 anchors reproduce from the source image; diagnostic negative checks
reject a one-dB shift, omitted power restoration and exchanged series. The
overlay files are supporting review artifacts, not replacement expected
results or an additional Figure 7 pytest oracle. On 2026-09-24 the complete
Milazzo module passed **24 tests with one existing warning in 27.55 seconds**.
Changed-script compilation, artifact hashes and whitespace checks passed.
No runtime calculation or demo settings changed; native ClickHouse and the
full suite were not rerun for this artifact addition.

The follow-up integration makes Figures 6 and 7 mandatory reference assets
in `test_milazzo_reference.py`, including both original JPEGs and overlay PNGs.
The module verifies all 44 RX and 76 TX endpoint observations within the
publication window against independent frozen-source arithmetic, before the
Target-Active Gate. The saved overlay CSVs are audited against that same
source arithmetic and never act as independent scientific expectations.
The retained endpoint counts (39 RX and 58 TX) separately protect the gate
boundary without dropping unpaired reports from the publication comparison.

Figure 7's 47 fixed image-derived anchors now have an executable paper oracle.
Raw source values bind each anchor to a unique identity before current SQL
components are inspected. The regression checks the -28 dB tail, an unplotted
archive report, and a graphical near-overlap that must remain two different
cycles. Negative controls reject a one-dB shift, wrong Reference power,
exchanged series and a removed extreme observation. All 29 TX reports without
selected paper anchors retain source-arithmetic coverage; the regression does
not pretend that overlapping or absent markers supply independent paper values.

Focused verification on 2026-09-24 passed **33 Milazzo tests with one existing
Matplotlib warning in 25.49 seconds**. Changed-test source compilation,
86-module/five-chunk manifest validation and whitespace checks passed.
This supersedes the earlier overlay-only Figure 7 coverage limit. No runtime
calculation, demo settings or original publication images changed; the complete
suite and native ClickHouse replay were not rerun for this isolated addition.

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

Ordinary query and session artifacts use one-hour access-aware cleanup. Every
ordinary Benchmark CSV exact query is written through as raw Parquet rows in the
same ordinary disk L2 used by Performance query artifacts. Guided demo query
artifacts use a separate 24-hour absolute freshness lifetime: reads do not touch
their publication timestamp. Benchmark keeps an optional process-memory DataFrame
L1 and a Parquet disk L2; demo Performance uses the same persistent demo namespace.
The process-wide DataFrame L1 admits at most 64 MiB total, 16 MiB per entry, and
32 entries after deep-byte accounting; larger frames remain disk-only. Both
tiers cache raw provider query results rather than completed scientific
analyses, and provider identity remains part of every query-cache key.
Geographic Analysis Scope is intentionally absent from this raw-query
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
policy. A completed run stores scoped evidence plus compact station/segment map
aggregates under its session-artifact owner. Later full Streamlit rerenders
validate a lightweight completed-run snapshot and reuse those aggregates without
another database request or full raw-frame map aggregation; stale or missing
artifacts require an explicit new run. Switching EN/DE preserves the completed
run and renders its evidence in the selected language. A language change retires
an in-flight UI submission; without a completed snapshot, a new Run action is
required. Derived basemaps
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
- A prepared-export regression package is still absent, so its package-integrity
  test is skipped. The separate G3ZIL/G4HZX scientific reference fixture is
  mandatory and exercises the numerical path after SQL aggregation; frozen-row
  SQL execution and broader independent reference coverage remain outstanding.
- Browser-level end-to-end behavior and multi-process deployment behavior are
  not covered by the current pytest suite.
- `README.md` synchronization rewrites the whole file. Repository engineering
  content belongs here, not in the generated README.

These are observed limits, not a claim that the application is unsafe or
incorrect. Prioritize changes according to measured cloud resource behavior and
the public deployment threat model.
