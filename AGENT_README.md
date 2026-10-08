# WSPRadar Repository Guide

This document is for maintainers and coding agents. The generated `README.md`
is the end-user and scientific manual. Code-level component boundaries and data
flows are documented in `docs/architecture.md`.

Dated run results and archived verification details are preserved in
[verification history](docs/verification-history.md). Use the
[script index](scripts/README.md) for current commands: routine Git, regression
and README synchronization commands remain in `scripts/`; fixture builders,
publication tooling and specialist checks live in `scripts/internal/`.

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
  and exact same-cycle Reference comparisons.
- Interactive configuration through a novice-oriented Guided Input flow or the
  full Classic editor, with English and German presentation in both views.
- Geographic station and segment aggregation on an azimuthal-equidistant map.
- Segment Inspector views with station tables, evidence figures, and drilldown
  tables backed by projected Parquet reads.
- Optional Benchmark Delta-SNR outlier-candidate reporting at native Joint Spot
  resolution, with robust local baselines,
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

[Installation verification, 2026-07-11](docs/verification-history.md#installation-2026-07-11).

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
| `config/delta_snr_outlier.py` | Validated policy, defaults, ranges, fixed dB comparison tolerance and bounds, and stable signature for optional Delta-SNR outlier-candidate reporting. |
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
  The detector method applies a fixed `0.01 dB` acceptance tolerance only to
  departure and baseline-difference comparisons. Evidence and saved thresholds
  remain unrounded; robust-z comparisons retain their original strict bound.
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
- Guided-demo query-cache retention: no age-based expiry for valid entries;
  provider, exact SQL, and an explicit cache-format version define reuse.
  Oversized-query failure markers remain temporary (86400 seconds).
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
version-1 documents are rejected when they do not match the current schema; no input migration or retired-field aliases are supported.
Every active comparison stores `snr_correction_mode` separately from
`snr_correction_db`. `no_offset` and `establish_offset` require an applied
correction of exactly `0.0 dB`; `established_offset` carries a documented signed
value and may explicitly carry a genuinely established `0.0 dB`. Dynamic Local
Neighborhood comparisons support `no_offset` and `established_offset` but not
the controlled offset-establishment workflow. Performance-only configurations omit
both fields. Applicable unpublished version-1 documents that lack the mode are
rejected rather than interpreted from an ambiguous numeric zero.

Reference Setup/Station uses exact Target and Reference callsigns and same-cycle
remote-peer evidence. Target QTH is the only manually entered analysis locator;
the Reference grid-4 is resolved from the selected archive, role, band and effective
UTC window. One candidate resolves automatically; multiple candidates require explicit
selection with reported locator variants, counts and time coverage available for review.
No reports and source failure are distinct. Discovery and the analysis share one provider.
Reference Neighborhood uses the Local Median. Sequential TX A/B and its schedule fields
are retired; unsupported unpublished configurations are rejected without migration.

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
Saved configurations and public URLs use only the current shared detector fields
and defaults. Retired duration-specific fields and former omission-default
mappings are rejected; current writers serialize the applicable values.

`config/config_codec.py` owns document-envelope and current-version validation;
`ui/config_io.py` owns semantic settings validation, Streamlit-state
application, and writing. Only the current schema and canonical fields are
accepted. Unsupported versions, retired aliases and earlier formats are
rejected without migration or guessed defaults. The formal JSON Schema enumerates valid fields, values, and
conditional branches.

Reference Neighborhood uses the Local Median in both input views. Guided has
concise help for each Reference choice and separate help for the Reference
callsign and Neighborhood Radius fields. Classic keeps the native radio selector
in the left column, with one help icon beside its visible Benchmark design label.
That help explains both Reference choices regardless of the current selection;
entry guidance belongs to the separate help on the Reference callsign and
Neighborhood Radius fields. Both input views use the same localized help text.
The neighborhood input shows the radius without a separate method heading. The
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
the shared Target/window fields and adds the Benchmark design when applicable.
Selecting RX/TX Benchmark without an existing design initializes `reference_station`;
an existing Reference Setup/Station or Reference Neighborhood choice is preserved.
Run reports incomplete or invalid fields locally before submission; Save Config
and public-URL synchronization require a valid canonical configuration. The advanced
panel uses Benchmark thresholds for Benchmark intent. Correction
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
Run `python scripts/internal/sync_reference_figure_pdfs.py` after rebuilding a figure or
adding a link, then commit the generated copy under `static/reference_figures/`.
Run the same command with `--check` to verify every linked copy against the
source PDF and fixture hash. Links in demo descriptions determine the published
set; there is no demo-ID mapping, runtime schema change, or PNG dependency.
Streamlit serves these files locally and on deployments through the existing
`enableStaticServing` setting. Original publication images remain raster panels
inside the PDFs; reconstructed points, bars, axes and annotations retain vector
geometry. Keep the PNG companions for visual review until explicitly removed.

Author demo PDF headers through the presentation-only records in
`config/demo_pdf_headers.py` and the shared `scripts/internal/demo_pdf_header.py` helper.
The centered header identifies the sheet as **WSPRadar.org reconstruction & comparison**,
followed by its descriptive title, labelled publication citation and source figure,
and a demo-context line; the cited authors belong to the publication reference,
while PDF document properties identify WSPRadar as the comparison author.
Follow `config/demo_pdf_style.md` and preserve the existing scientific content,
panel geometry and source attribution when changing this authoring metadata.

Reconstruction builders follow the
[publication reconstruction contract](tests/regression/reference_fixtures/README.md):
frozen source reports enter the generated SQL and production post-fetch,
map/Inspector, pairing and figure-preparation stages. Independent expected
outputs check those results; they never supply the plotted observations.
Paper-style rebinning/smoothing and deliberate pre-gate or duplicate-report
diagnostics are separately identified. The offline SQL adapter and downstream
scientific pipeline are exercised; live transport, caches and native ClickHouse
engine behavior are outside this reconstruction check.

## Running the Application

Start Streamlit from the repository root:

```powershell
python -m streamlit run app.py
```

The application uses port 8501 by default. The repository VS Code task runs
`python -m streamlit run app.py`; the committed Streamlit configuration enables
both CORS and XSRF protection. Streamlit Community Cloud hosting is not a reason
to disable these protections. The
[configuration reference](https://docs.streamlit.io/develop/api-reference/configuration/config.toml)
and [remote-start guidance](https://docs.streamlit.io/knowledge-base/deploy/remote-start)
describe the settings and deployment troubleshooting. Browser connection,
reconnection and file-upload behavior still need verification with these enabled
settings in Codespaces and on the deployed Community Cloud app; no such runtime
verification was performed during this housekeeping change.

[Startup verification, 2026-07-11](docs/verification-history.md#startup-2026-07-11).

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

### Temporary files and retained evidence

Use automatically cleaned system temporary directories for intermediate files.
For reviewable PDF candidates, renders and diagnostic reports, use
`.tmp/<task>/` and remove the task directory after verification and delivery.
The name `.tmp` and its Git ignore rule do not provide automatic cleanup.
Do not create root `output/` or `tmp/` for new scratch work. These directories
are ignored to prevent accidental commits; approved PDFs remain in their
reference fixture and published `static/reference_figures/` locations.

Unique captures, scientific derivation scripts and useful verification records
must be preserved before deleting old scratch directories. Store required
reproducibility material in the appropriate maintained repository location;
archive historical material outside the checkout with an inventory and hashes.
Do not delete a directory while a process or another task is using it. Routine
cleanup of PDF scratch does not include `.test/` or `.wspr_cache/`.

[Scratch evidence archive, 2026-09-27](docs/verification-history.md#scratch-archive-2026-09-27).

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
- `core/reference_location.py`: bounded Reference-location discovery and candidate evidence.
- `ui/reference_location_state.py` and `ui/reference_location.py`: discovery state and UI.
- `ui/input_validation_state.py`: lightweight shared field-validation state.
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
  profile/save controls scoped to an independent top-level fragment or the
  existing Inspector fragment, and canonical absolute UTC-window
  writing.
- `ui/time_window.py`: once-per-session absolute UTC defaults, widget-state
  minute normalization, and effective-window validation.
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

## Testing and Checks

### Performance endpoint-participation contract (2026-09-25)

RX and TX Performance use `opportunity-v3`: `hit = target_seen`,
`opportunity = target_seen OR external_seen`, and
`miss = external_seen AND NOT target_seen`. Target-only is a provenance subset
of successes, not an additional outcome or total. A peer TX decoded by the
Target RX confirms both endpoints in RX; a Target TX decoded by the peer RX
confirms both in TX. External reports confirm that exact peer TX's transmission
(RX) or peer RX's listening activity (TX), within the unchanged Target-active,
same-band and same-cycle scope. Activity elsewhere does not establish that a
silent receiver was listening. Unknown activity remains excluded.

`tests/regression/test_performance_method_reference.py` supplies hand-authored
raw reports and arithmetic for both directions. Generated production SQL runs
through the bounded SQLite/ClickHouse-function adapter before real post-fetch,
map, Inspector, temporal/folded, Drill-Down and export preparation. This verifies
the generated expressions and predicates; it does not establish native
ClickHouse engine equivalence. Completed `opportunity-v1`/`opportunity-v2`
results and old Inspector/figure/export cache identities are incompatible;
unchanged raw query evidence remains reusable for reprocessing.

`scripts/internal/verify_performance_method_revision.py` independently reconstructs the
frozen Milazzo Performance consequences from configuration and raw reports,
then checks production processing. Its separate output directory preserves the
original review packet, source archive, expectations and human-review status;
At the 2026-09-25 method revision, the affected cards required regeneration
and review. The subsequent approval is recorded in
[Human-verified Milazzo regression reference](#human-verified-milazzo-regression-reference-2026-09-26).

[Performance endpoint-participation verification, 2026-09-25](docs/verification-history.md#performance-method-2026-09-25).

### Human-verified Milazzo regression reference (2026-09-26)

The user explicitly approved all revision-2 Milazzo cards **P01–P10 and
B01–B04** on 26 September 2026. The permanent fixture
`tests/regression/reference_fixtures/milazzo_human_review_v2` preserves that
approval separately from the original packets, the reviewed PDF/card definitions,
exact Performance/Benchmark configurations, raw reports and independent expected
ledgers. Historical pending-review wording in the byte-preserved packet is
superseded by the new fixture's `approval.json`; earlier review records remain
unchanged. The human-reviewed anchors and the independently derived exhaustive
supporting values are explicitly distinguished.

`test_milazzo_human_performance.py` exercises P01–P10 from the full 65,647-report
Performance capture. The human-card tests in `test_milazzo_reference.py` exercise
B01–B04 from the frozen Benchmark source and exact 32-hour review configuration.
Each replay validates configuration, generates SQL, evaluates it against raw
reports through the bounded offline adapter, and calls production processing,
station/map aggregation and Inspector/figure preparation. Expected files are
assertion inputs only. Selected Matplotlib artist checks cover the scientific
values actually drawn, including P10's final +1.5 dB marker and P09's sparse-IQR
rule. These tests are mandatory in every complete local regression run, including
the fixed serial fallback chunks; a missing fixture fails rather than skips.
Focused runs still execute only their explicitly selected modules.

The separate `scripts/internal/verify_milazzo_clickhouse.py` command is an occasional,
read-only check against a real configured ClickHouse provider. Run it before
completing a major development effort, or earlier when changing SQL/dialect or
provider behavior. It compares generated query results with the frozen reference
after local scientific verification. It does not upload fixture data, modify the
provider, use cached results or refresh expectations. It is **not** invoked by
the normal regression runner and adds no GitHub CI job. An unavailable provider
or unequal result is reported as an unsuccessful check; investigate query
semantics and possible upstream archive changes before changing expectations.

```powershell
# Validate the offline reference and save the exact query plan; no requests.
.\.venv\Scripts\python.exe scripts/internal/verify_milazzo_clickhouse.py --dry-run
# Explicit major-effort check against one provider; four read-only requests.
.\.venv\Scripts\python.exe scripts/internal/verify_milazzo_clickhouse.py --provider wspr_live
# Scope a check explicitly when comparing providers or investigating a failure.
.\.venv\Scripts\python.exe scripts/internal/verify_milazzo_clickhouse.py --provider wd2 --analysis performance
.\.venv\Scripts\python.exe scripts/internal/verify_milazzo_clickhouse.py --provider wspr_live --analysis benchmark
```

Each invocation creates a new timestamped `.tmp/milazzo_clickhouse_*` report
directory; `--output-directory` can specify another new directory. It records
input/code/query hashes and expected/actual query rows. A dry-run success is not
a live-provider verification. The native Benchmark capture supplies only the
`best_ref_dist` comparison baseline after its other columns have been checked
against the independent offline result; this preserves the native geographic
diagnostic despite the adapter's documented spherical approximation.

`--analysis` defaults to `both`; `performance` or `benchmark` sends only that
analysis's two strict/fallback queries and records a separately named scoped
success. Provider HTTP errors retain bounded diagnostic text. Do not interpret a
successful subset as a complete pass, or assume different providers have
identical historical coordinate metadata.

The offline tests remain deterministic. A real-provider comparison exercises
native execution on the provider's current historical archive; it is not a
native ClickHouse replay of an immutable local database. The source/configuration
checksums and query results in its report identify the exact comparison. A
deliberate change to an approved scientific expectation requires a separately
reviewed fixture revision, not automatic snapshot regeneration.

[Milazzo human-review and provider verification, 2026-09-26](docs/verification-history.md#milazzo-human-review-2026-09-26).

### Running checks

The 2026-09-28 Reference workflow and current-configuration cleanup passed the
complete foreground regression runner: **3,330 passed, 3 existing xfailed,
1 existing warning in 466.35 seconds**, exit 0. The initial failures, corrections,
and final focused follow-up are recorded in the
[Reference workflow regression debrief](docs/reference-workflow-regression-debrief.md).

[Runtime verification records, 2026-09-26 and 2026-09-27](docs/verification-history.md#recent-runtime-checks-2026-09-26-27).

Focused regression testing is the default for incremental work, including
bounded scientific, cache and export corrections. Trace the affected contracts
and callers, then pass the relevant modules or nodes directly to the repository
interpreter. For example, the detector and export portions of an outlier-policy
fix can be checked with:

```powershell
.\.venv\Scripts\python.exe -u -m pytest tests/regression/test_delta_snr_outlier_candidates.py tests/regression/test_delta_snr_outlier_export_tables.py -q
```

Add documentation, cache, marker or other integration modules only when their
contracts are affected. Compile the changed Python scope and check whitespace.
The example is not a complete fixed test set for every outlier change: selection
follows actual dependencies, not file names alone. Expand relevant coverage when
a failure or uncovered caller justifies it.

Reserve a complete run for major changes spanning independent features or
workflows, qualification of a concrete release candidate/tag/package,
substantial manual restructuring,
or an explicit user request, as defined in `AGENTS.md`. A small scientific fix,
multiple edited files, or an ordinary PR/GitHub submission does not automatically
require a complete run. Explain the concrete reason before starting one. When
required, run the complete suite on Windows through the foreground-only
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
For a focused module selection, use the direct Python command above. Appending
module paths to the full runner does not replace its complete-suite target.

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

For bounded work, select the directly affected test modules or nodes according
to the focused-verification contract in `AGENTS.md`. Figure, PDF, Streamlit
integration, and export-package tests are intentionally omitted from unrelated
focused runs; select their affected contracts and routes when their implementation
or direct callers change. Do not add every test in a subsystem merely because
one of its files changed. Complete runs still include every regression module.

Pytest stores its disposable per-run files and cache under the ignored `.test/`
directory. The `.test/pytest-temp/` tree is cleared at the start of each pytest
session, preventing separately named root-level test directories from
accumulating across runs.

[Regression and performance records, 2026-08-17 through 2026-09-25](docs/verification-history.md#regression-and-performance-records-2026-08-17-to-09-25).

The committed prepared-export fixture
`tests/regression/fixtures/milazzo_fig6_rx_prepared_export_v1/` supplies the
package-integrity checks in `test_demo_fixtures.py`; its separate mandatory
availability/provenance check fails if the fixture is absent. The snapshot
contains derivative production exports, while scientific expectations remain in
`tests/regression/reference_fixtures/`. See the
[fixture documentation](tests/regression/fixtures/milazzo_fig6_rx_prepared_export_v1/README.md).
Historical skipped-fixture statements apply only to the dated runs in the
[verification history](docs/verification-history.md). The existing Matplotlib
pending-deprecation warning originates in `ui/plots/evidence_figures.py`.

Compile the repository Python sources:

```powershell
python -m compileall -q app.py config core docs ui scripts tests
```

Check whitespace in the patch:

```powershell
git diff --check
```

[Source-compilation and whitespace record, 2026-07-11](docs/verification-history.md#source-and-whitespace-2026-07-11).

There is no configured project linter, formatter, type checker, pre-commit hook,
or full regression workflow. The `regression-manifest.yml` GitHub workflow runs
`scripts\run_regression.cmd -ValidateChunks` on Windows for pushes, pull requests,
and manual dispatch, without installing application dependencies. It rejects
unassigned, duplicate, or stale test-module entries before they can break the
launcher. The `wake.yml` workflow opens the deployed application every six hours
and on manual dispatch. Compilation is a syntax check, not a substitute for
static analysis.

To build a regression fixture from an exported demo folder, inspect and use
`scripts/internal/build_regression_fixture_from_demo_folder.py`. Folders placed under
`tests/demo/` are export-intake inputs, not current regression fixtures; only
generated packages under `tests/regression/fixtures/` are active prepared-export
fixtures.

Scientific reference datasets use the separate
`tests/regression/reference_fixtures/` directory. The mandatory
`test_griffiths_temporal_reference.py` replays the first G3ZIL/G4HZX demo from
frozen source reports through generated production SQL, post-fetch filtering,
station aggregation, paired evidence and temporal recipes. It compares all 57,767
paired observations and the daily, three-hour and folded UTC-hour profiles with
fixed reviewed expectations. Missing or corrupt reference files fail rather
than skip. The fixture README records the paper comparison, captured provider
and historical decode provenance, checksums, and baseline-update rules.
Since 2026-09-25 this offline test also executes the generated normalization
and aggregation SQL through the bounded SQLite compatibility adapter, using
the production strict/fallback decision. Captured SQL-result rows now serve
only as an additional assertion target. Native ClickHouse behavior, exact
database geographic distances, provider selection and the physical meaning of
historical mode codes remain outside this check.
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
offline and share the production source-to-evidence replay helpers. Their
generated SQL executes against frozen source rows without a live database.

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
The Figure 6 presentation revision of 2026-10-08 retains those three checks and
adds two source-image witnesses: a negative point at the lower plotting boundary
near 08:33 UTC and an isolated positive point near 15:52 UTC. Four witnesses are
displayed as P1-P4, with two of each sign; the former P3 remains an undisplayed
regression witness. Source-readout tolerances and production calculations remain
unchanged, and the lower-boundary point's clipped appearance is documented.
The second Figure 6 iteration on the same date moves displayed P3 to a complete
source dot near 08:45 UTC / -14 dB. Both earlier P3 witnesses remain hidden
regression checks, bringing the preserved source-witness total to six. A separate
Panel B overlay identifies additional weaker-report combinations from the same
production-selected cycle/callsign/full-locator identities: 17 combinations in
total, eight within the displayed -15 to +25 dB range. Red dots share the native
dot size and opacity and do not enter density or native Panel C calculations.
The Panel B note links Figure 3's pairing diagnostic without asserting a
physical cause for Figure 6. The overall median stays in Panel C but leaves its
legend; reconstruction entries now sit beneath Panel B.

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
and runtime calculations remained unchanged during that initial fixture
addition, which did not test SQL execution. The later 2026-09-25 offline SQL
coverage is described above and in the
[regression history](docs/verification-history.md#regression-and-performance-records-2026-08-17-to-09-25).
[Griffiths publication-reference verification, 2026-09-24](docs/verification-history.md#griffiths-paper-reference-2026-09-24).

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
The independent builder is `scripts/internal/build_zander_reference_fixture.py`;
expectations are never regenerated by tests. [Zander reference verification, 2026-09-24](docs/verification-history.md#zander-reference-2026-09-24).

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
`scripts/internal/build_vanhamel_reference_fixture.py`; tests never regenerate the
expected files. This fixture has no duplicate endpoint reports or non-code-1
rows and does not independently validate the native ClickHouse engine.

[Vanhamel calibration verification, 2026-09-24](docs/verification-history.md#vanhamel-calibration-2026-09-24).

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
`scripts/internal/build_vanhamel_rotation_reference_fixture.py` consumes frozen raw
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

[Vanhamel rotation verification, 2026-09-24](docs/verification-history.md#vanhamel-rotation-2026-09-24).

The Milazzo TX reference adds `test_milazzo_reference.py` and
`reference_fixtures/milazzo_tx_reference_v1`. The demo description now uses
the configured 5,000 km population: 1,069 Only Target, 45 Joint and 21 Only
Reference receiver-cycles, rather than the unrestricted 1,093/46/21 counts.
The scientific demo settings and runtime calculations are unchanged.

The independent standard-library builder
`scripts/internal/build_milazzo_reference_fixture.py` accounts for all 1,992 source
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

[Milazzo TX reference verification, 2026-09-24](docs/verification-history.md#milazzo-tx-reference-2026-09-24).

The subsequent Milazzo Figure 6 reconciliation adds the separate
`reference_fixtures/milazzo_fig6_rx_v1` fixture. All 44 independently digitized
markers match user-supplied wspr.rocks reports in the reciprocal RX direction:
VE6PDQ transmitting, KP4MD and WB6RQN receiving. All annotated SNRs match
exactly, with a maximum two-minute graphical time residual and no fitted shift.
This contradicts the printed direction; it does not establish a Figure 6/7
image swap. At this initial reconciliation stage the installed demo remained
TX with unchanged scientific settings, and its description explained the RX
publication reconciliation. The subsequent 2026-09-27 RX demo change and its
verification are preserved in the
[runtime verification history](docs/verification-history.md#recent-runtime-checks-2026-09-26-27).

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

[Milazzo RX reference verification, 2026-09-24](docs/verification-history.md#milazzo-rx-reference-2026-09-24).

The subsequent Milazzo overlay review adds
`reference_fixtures/milazzo_publication_overlays_v1` and
`scripts/internal/build_milazzo_publication_overlays.py`. Original Figure 6/7 images
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
results or an additional Figure 7 pytest oracle. [Milazzo overlay artifact verification, 2026-09-24](docs/verification-history.md#milazzo-overlay-artifact-2026-09-24).

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

[Milazzo overlay regression integration, 2026-09-24](docs/verification-history.md#milazzo-overlay-integration-2026-09-24).

## Cache and Operational State

The application writes local cached and transient state under `.wspr_cache/`, which is
ignored by Git:

```text
.wspr_cache/
  queries/<database-source>/
  demo-queries/<database-source>/v1/
  derived-analysis/basemaps/
  session-artifacts/<owner>/run_<id>/
  .artifact-locks/
```

Ordinary query and session artifacts use one-hour access-aware cleanup. Every
ordinary Benchmark CSV exact query is written through as raw Parquet rows in the
same ordinary disk L2 used by Performance query artifacts. Guided demo query
artifacts are populated on demand when a demo runs and have no age-based expiry:
reads do not touch their publication timestamp. An explicit
`DEMO_QUERY_CACHE_FORMAT_VERSION` in `core/data_engine.py` participates in both
disk and RAM identity; change it only for incompatible raw-cache representation
or interpretation changes, not routine application releases. Changed SQL already
selects a distinct entry. Previous unversioned or different-version entries are
not reused or automatically migrated. Missing, unreadable or invalid entries
follow the existing validation, invalidation and provider reacquisition paths.
There is no startup preload or automatic refresh for upstream archive corrections.
Permanent retention depends on the hosting environment retaining this directory;
it does not prevent explicit deletion or bounded RAM eviction. Benchmark keeps an optional process-memory DataFrame
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
strict/legacy request bundle from compatible cache. The selected cache retains its
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
ordinary query files are checked against a fresh clock reading with a five-second
tolerance before a future modification time is treated as invalid. Published
demo files are excluded from age and future-timestamp cleanup; abandoned atomic
temporary siblings remain eligible for cleanup. Oversized-query rejection markers
are finite even for demos and do not constitute valid retained query data.

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
- Streamlit CORS and XSRF protection are enabled in committed configuration.
  Browser connection, reconnection and file uploads with these settings still
  require Codespaces and Community Cloud deployment verification; the local
  launcher inherits the committed settings without command-line overrides.
- Cache namespaces have locking and lifecycle-specific retention but no configured
  maximum file count, byte quota, minimum-free-disk rule, or derived-basemap lifetime.
  Published demo query files, including obsolete query/format versions, do not
  expire automatically.
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
- The committed Milazzo prepared-export package exercises package integrity and
  has a mandatory availability check. It is a derivative export snapshot, not an
  independent scientific oracle. Separate frozen-source reference fixtures
  execute generated SQL through the bounded SQLite compatibility adapter and
  production numerical processing; native ClickHouse engine equivalence and
  behavior of the providers' changing historical archives remain outside those
  offline checks.
- Browser-level end-to-end behavior and multi-process deployment behavior are
  not covered by the current pytest suite.
- `README.md` synchronization rewrites the whole file. Repository engineering
  content belongs here, not in the generated README.

These are observed limits, not a claim that the application is unsafe or
incorrect. Prioritize changes according to measured cloud resource behavior and
the public deployment threat model.
