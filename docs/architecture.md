# WSPRadar Architecture

This document describes the repository as inspected through 2026-07-17. It derives
component boundaries and behavior from the application code, configuration, and
regression tests. Items explicitly marked uncertain were not established by the
code or by the verification run.

## System Context

WSPRadar is a single Streamlit application process that queries historical WSPR
observations from the public wspr.live ClickHouse HTTP endpoint. Scientific work
is performed in core modules, while Streamlit state, controls, presentation, and
downloads are managed in UI modules. Local process memory and a local artifact
directory provide caching and session continuity.

```text
Browser
  -> Streamlit app.py
     -> UI configuration and context adapters
     -> analysis/export admission controllers
     -> analysis runner and data engine
        -> wspr.live ClickHouse HTTP API
        -> local query/session artifact store
     -> compare or opportunity engines
     -> map data and presentation rendering
     -> inspector view models and projected evidence reads
     -> optional export preparation
```

The application reads wspr.live data. No upstream write path or database
credential was found.

## Entry Points

### Application

`app.py` is the Streamlit entry point. It:

- enables Python fault handling;
- emits page configuration and the lightweight application shell before
  importing scientific analysis dependencies;
- initializes Streamlit session state;
- renders language, demo, and analysis configuration controls;
- validates the requested time interval;
- imports `ui/run_controller.py`, plotting, inspector, DataFrame, HTTP, and
  Cartopy dependencies only after a TX or RX run is active;
- renders a Part 0 preface preview and loads the remaining manual after
  browser scroll intent or an explicit request through `ui/documentation.py`.

The supported start command is:

```powershell
python -m streamlit run app.py
```

### Static Redirect

`index.html` and `CNAME` provide a static redirect/domain path to the deployed
Streamlit application. They are not part of analysis execution.

### Separate Relay Utility

`tools/Timed-AB-Relay-Switch/` is a separate console program for timed USB HID
relay switching. It has independent requirements, configuration, wrappers, and
operating risks. The Streamlit application neither imports nor starts it.

## Component Responsibilities

### Configuration

| Module | Responsibility |
| --- | --- |
| `config/app_config.py` | Application identity, URLs, time-window limit, cache and HTTP limits, analysis/export admission settings, and inspector-cache limits. |
| `config/bands.py` | WSPR band labels and wspr.live numeric identifiers. |
| `config/demos/*.config` | Authoritative guided demos. Each file is a standalone saved configuration and lexicographic filename order defines launcher order. |
| `config/demo_profiles.py` | Strict dependency-free demo discovery, schema/profile validation, duplicate-ID protection, and stable filename-ordered `DEMO_PROFILES` mapping. |
| `config/config_schema.py` | Saved-config format identifier, current schema version, grouped settings contract, and canonical enum values. |
| `config/config_codec.py` | Dependency-free document-envelope and schema-version validation shared by personal-config and demo readers. |
| `config/wspradar-config.schema.json` | Formal JSON Schema for every saved and demo configuration. |
| `config/json_utils.py` | Shared strict UTF-8 JSON decoder rejecting duplicate keys and non-finite numbers. |
| `config/plot_constants.py` | Map extent, projection/render constants, colors, and scientific display constants. |
| `config/__init__.py` | Compatibility re-exports for configuration consumers. |

User-saved configuration files and demos share the version-1
`wspradar.config` document format. A document contains a schema version,
optional writer metadata, an optional self-describing `profile` with stable ID
and localized title/description, one canonical `settings` object, and an
optional `extensions` object for non-core namespaced data. `settings` is grouped into
`core_parameters`, `comparison_parameters`, `advanced_parameters`, and
`results_view`, matching the durable UI sections. The selected analysis
direction is a core parameter. Conditional branches are active-only: the
document contains every setting applicable to the selected time and comparison
modes and omits inactive hidden fields. Applying a document resets inactive
controls before loading the validated active branch.

`results_view` has an always-present `success` branch and a conditional
`compare` branch. Both preserve canonical Segment Inspector range/direction,
selected-station chronological bins, and station-selection intent. Explicit
stations are canonical callsign/locator pairs; `all` dynamically selects the
complete reconstructed table after saved visibility controls and before
transient table filters. Compare additionally preserves `show_non_joint`, its
segment temporal bin, and the selected-station `chronological` versus `utc_hour`
view; Success preserves `show_zero_target`. Table and Drill-Down filters,
expander state, and other transient controls are deliberately not serialized.
`config/config_codec.py` validates the current document envelope and exact
initial schema version, while `ui/config_io.py` validates and applies the
semantic settings. There is no migration from unpublished prototypes. A future
public schema bump is incomplete until the preceding published version has an
explicit migration; unsupported versions are rejected rather than interpreted
with current defaults.

The hardware TX A/B branch records a shared `repeat_interval_minutes` and
disjoint `target_start_minute` and `reference_start_minute` phases. The UI
exposes **Repeat Interval**, **Target Start**, and **Reference Start**,
offers intervals of 4, 6, 10, 12, 20, 30, or 60 minutes, restricts starts to
distinct even phases below the interval, and defaults them to 10, 0, and 2
minutes. Sequential Compare always assigns planned pairs from this schedule;
the unpublished fixed-bin prototype is not a supported runtime branch.

The reusable configuration's optional `profile` carries the stable ID and
localized presentation text used by built-in demos. `config/demo_profiles.py`
discovers regular `config/demos/*.config` files in lexicographic filename order.
Each filename is an opaque ordering key independent of the document's required
`profile.id`. There is no second demo envelope or schema: a personal
configuration becomes a built-in demo by choosing any `.config` filename that
places it at the desired launcher position and putting the unchanged document
in that directory. Installed demos use English as their required presentation
baseline; German title and description values are optional and fall back to
English. The launcher renders descriptions as escaped GitHub-flavored Markdown,
preserving JSON newline escapes as visible line breaks and allowing Markdown
links without enabling raw HTML.

`ui/config_save.py` renders the interactive save workflow as a Streamlit
fragment. It collects the profile title, optional description and stable ID,
then prepares bytes from the current durable inspector state without rerunning
the scientific analysis. For a `last_x` selection it explicitly chooses between
retaining the relative duration and converting the active run's resolved UTC
interval to `custom`. `ui/result_state.py` keeps that quantized interval keyed
by `run_id`, so full-page rerenders cannot move the bounds of an already active
run; result reset or config load clears it.

### Context Boundary

`core/analysis_context.py` defines an immutable `AnalysisContext` containing
canonical scientific settings. `ui/analysis_context_adapter.py` translates
Streamlit session values and localized choices into that context.

`core/presentation_context.py` defines an immutable `PresentationContext` for
language, labels, theme, and solar display. `ui/presentation_context_adapter.py`
constructs it from UI state.

This split is deliberate: localized text and theme must not alter SQL,
classification, aggregation, or scientific cache keys. Regression tests verify
that language changes presentation titles without changing generated queries.

### Analysis Orchestration

`ui/run_controller.py` coordinates a complete run. It validates user input,
builds contexts, computes a request fingerprint, acquires admission, asks
`core/analysis_runner.py` for analysis batches, fetches data, applies post-fetch
processing, stores session evidence, renders maps and previews, registers export
recipes, and invokes the Segment Inspector.

It also implements compatibility retry behavior for historical rows where a
strict `code = 1` query returns no target evidence. The retry metadata is exposed
in results and tested. This is scientific compatibility behavior and should not
be changed as a generic query optimization.

### Query and Fetch Layer

`core/analysis_runner.py` builds ClickHouse SQL for:

- TX and RX comparison analyses;
- local/reference and hardware A/B comparisons;
- periodic scheduled TX A/B comparisons;
- TX and RX opportunity analyses.

For periodic hardware A/B work, SQL applies the exact UTC-minute modulo
predicate for each path's repeat interval and start phase. TX Success applies
only the Target path's schedule. Comparison post-fetch processing rejects rows
outside their assigned path schedule and attaches stable
`tx_ab_pair_id`, `tx_ab_pair_target_time`, and
`tx_ab_pair_reference_time` columns before evidence is written to Parquet.
It also applies mode-specific post-fetch synchronization and filtering.

`core/data_engine.py` executes HTTP requests and returns structured
`FetchResult`, source, and error data without rendering Streamlit UI. It provides:

- a process-memory DataFrame LRU;
- exact-query SHA-256 disk-cache keys;
- CSV and Parquet response handling;
- connect/read deadlines;
- streamed byte accounting and decompressed response ceilings;
- unique temporary files and atomic promotion through the artifact store;
- bounded error-response capture.

The engine logs query and performance information to the terminal. It holds a
module-level Requests session. Explicit proof of all concurrent session-use
semantics was not found, so thread-safety beyond the exercised tests remains an
operational uncertainty.

### Scientific Engines

`core/compare_engine.py` performs pure comparison aggregation for simultaneous
and scheduled observations. For periodic TX A/B analysis, each planned Target
slot is paired bijectively with its nearest planned Reference slot. An exact
half-interval tie pairs the lower and higher phases in the same repeat cycle,
independent of which path is called Target. Aggregation includes peer identity
in the pair key, takes a micro-median when one peer has multiple decoded rows
on either side of a scheduled pair, and computes Delta only for a pair with
both sides. Boundary pairs are admitted only when both planned transmission
starts lie inside the selected analysis interval.

`core/tx_ab_schedule.py` owns supported repeat-interval and start validation,
the exact ClickHouse schedule predicate, hourly previews, cyclic separation,
and stable planned-pair assignment. `core/snr_utils.py` centralizes
normalized-SNR rounding and CSV formatting. `core/stability.py` performs
deterministic, optionally chunked bootstrap stability calculations.

`core/opportunity_engine.py` owns opportunity-row normalization,
classification, aggregation, evidence projections, and map projections. Its
processed schema deliberately:

- stores `time_slot` as an integer and derives UTC timestamps from
  `time_slot * 120` through one helper;
- stores repeated peer callsign, locator, outcome, and path-illumination values
  categorically;
- retains peer coordinates and target SNR at their existing precision;
- uses reduced precision only for designated solar summary columns;
- distinguishes hits, misses, target-only observations, and eligible evidence;
- uses peer-balanced segment aggregation while retaining pooled diagnostics;
- allows owned-input mutation to avoid unnecessary full DataFrame copies;
- projects only the columns needed by segment, drilldown, and map consumers.

`core/solar_path.py` computes vectorized solar time terms, Sun vectors,
great-circle samples, endpoint solar states, and path-illumination classes. The
opportunity pipeline transfers frame ownership so enrichment does not create an
additional full-frame copy.

`core/input_validation.py` contains dependency-free callsign and locator
validation, and `core/time_utils.py` contains dependency-free query-time
quantization. Keeping these idle-shell helpers separate prevents NumPy-backed
geometry from loading before an analysis is requested. `core/math_utils.py`
retains compatibility exports while owning Maidenhead conversion, geometry, and
solar helpers for the scientific path.

### Map Pipeline

`core/map_data.py` converts comparison or opportunity rows into pure `MapData`
aggregates. `core/map_models.py` defines the `MapData` and `MapFigure` contracts.

`core/map_base.py` builds a Cartopy azimuthal-equidistant basemap with Natural
Earth land, ocean, coastline, and border data, plus distance rings and compass
features. Rendered static basemaps are stored in the derived-analysis namespace.
Same-key construction is coordinated and publication uses a unique temporary
path followed by atomic replacement.

`core/plot_engine.py` applies presentation labels and renders a figure from pure
map aggregates. It does not access Streamlit state. `ui/matplotlib_renderer.py`
serializes lower-DPI preview PNGs and displays them through Streamlit.

`core/matplotlib_runtime.py` owns a process-wide re-entrant lock because
Matplotlib has shared mutable state. Rendering is intentionally serialized, and
figures use the Agg backend and are disposed after serialization rather than
being retained in pyplot's global registry.

### Segment Inspector

`ui/components/segment_inspector.py` remains the Streamlit fragment responsible
for selections and rendering. Preparation is split into pure modules:

- `ui/inspector/view_models.py` builds compare and opportunity view models and
  figure recipes;
- `ui/inspector/evidence_data.py` performs projected Parquet reads;
- `ui/inspector/drilldown.py` builds selected-station evidence tables;
- `ui/inspector/session_cache.py` maintains a run-scoped bounded LRU for options,
  segment models, selected models, and PNGs;
- `ui/plots/` renders evidence figures from pure recipes.

Opportunity segment reads request only `time_slot`, `peer_sign`, `peer_grid`,
`hit`, and `miss`. Selected-station reads request only evidence columns required
by the corresponding table and figure. This keeps the raw opportunity artifact
out of initial inspector rendering and avoids rereading all Parquet columns.
Periodic hardware A/B projections additionally carry the stable planned-pair
identifier and timestamps so inspectors and exports replay the same pairing
used for the map aggregation.

### Export Pipeline

`ui/results_export.py` registers export recipes and analysis context during a
run. Export preparation is lazy and protected by a separate admission controller
from `core/export_admission.py`. The configured policy allows one active export
and up to ten queued exports.

`ui/result_state.py` owns the lightweight result/export session-state keys,
active-run UTC interval, and reset lifecycle. Configuration callbacks can retire
session artifacts and clear export, inspector, stability, and resolved-time
state without importing Pandas, Matplotlib, the inspector, or export rendering.

Preparing an export reuses completed analysis and projected artifacts; it does
not rerun the upstream scientific query. It renders paper-theme, high-resolution
figures and packages configuration, metadata, CSV tables, compact Parquet
evidence, and PNGs. Comparison artifacts are grouped under `compare/`; Success
artifacts are grouped under `success/`, with the same names reflected in run
metadata.

The ZIP is currently constructed in `io.BytesIO` and retained in Streamlit
session state for download. This is a known peak and idle-memory risk, partially
contained by single-export admission.

### Documentation Pipeline

`docs/doc_en.py` and `docs/doc_de.py` hold the full manuals as source strings.
`ui/documentation.py` initially renders only the Part 0 preface in a Streamlit fragment.
`ui/documentation_scroll_trigger.py` mounts a one-pixel browser visibility
sentinel immediately before visible Section 0.3 (the stable `sec-1-3` anchor).
When that boundary enters the viewport,
the fragment renders the table of contents and remaining chapters once per
session while the reader finishes Section 0.3.
`Load full documentation` is a prominent explicit fallback, and the same control
can hide the loaded content. Starting an analysis collapses the manual and
suppresses the viewport trigger while the run remains active, without rearming a
trigger already consumed earlier in the session. A collapsed expander is not
used as a lazy-load boundary because Streamlit would still execute and transmit
its contents.

`docs/pdf_generator.py` converts the manual to PDF only when requested. PDF
generation is single-flight and process-cached, so the first requester waits and
subsequent requesters reuse the cached bytes until process restart or cache loss.
`scripts/sync_readme_from_doc_en.py` rewrites `README.md` from a fixed header plus
the complete English manual. Consequently, repository engineering documentation
must remain outside `README.md`.

## Major Data Flows

### Comparison Analysis

1. Streamlit state is converted to canonical analysis and presentation contexts.
2. The controller validates inputs and obtains an analysis permit.
3. `analysis_runner` builds the mode-specific comparison SQL. Periodic TX A/B
   predicates select each path by its exact repeat interval and UTC start phase.
4. `data_engine` returns a RAM-cache, disk-cache, or wspr.live result.
5. Post-fetch logic synchronizes cycles and applies mode-specific rounding. For
   periodic TX A/B data it also filters schedule mismatches, excludes a boundary
   pair unless both planned starts are within the analysis interval, and assigns
   the stable planned-pair columns.
6. The processed rows, including planned-pair columns, are written to a session
   Parquet artifact.
7. `compare_engine` groups periodic pairs by peer identity and pair ID, applies
   per-side micro-medians, and builds station and segment aggregates.
8. `map_data` and `plot_engine` render the map preview.
9. Inspector view models read the necessary evidence and render segment and
   selected-station views.
10. Export recipes are registered for optional later execution.
11. The permit is released in all completion/error paths.

### Opportunity Analysis

1. An active-cycle ClickHouse query returns one row per time slot and peer
   identity with target/external evidence and target SNR. Hardware TX Success
   additionally restricts active cycles to the configured Target repeat
   interval and start phase; the Reference schedule is not part of this query.
2. The fetched frame is normalized into the explicit opportunity schema.
3. Peer coordinates are resolved and assigned without a full coordinate merge.
4. Hit, miss, target-only, outcome, and eligibility columns are computed.
5. Solar path enrichment operates on the owned frame.
6. The final categorized artifact is written as session Parquet.
7. Map and segment aggregates use the corresponding narrow projections.
8. The inspector loads selected evidence only when required.

### Duplicate and Admission Flow

`core/analysis_admission.py` implements FIFO admission with a condition variable,
active leases, queue timeouts, and bounded active/queued counts. Each Streamlit
session receives a stable owner identifier. The request key includes canonical
scientific inputs and demo identity.

A session cannot enqueue an identical request while its matching work is active
or queued. Different sessions may run the same demo; this avoids turning popular
demos into a cross-user single-result dependency. Admission state and deduplication
are process-local and do not coordinate multiple application processes.

## Persistence and Cache Lifecycles

`core/artifact_store.py` divides local artifacts into three namespaces:

| Namespace | Contents | Lifecycle |
| --- | --- | --- |
| `queries` | Exact-query Parquet responses | TTL and last-access cleanup. |
| `derived-analysis` | Shared basemap PNGs | Reused across sessions; no current TTL cleanup. |
| `session-artifacts` | Per-owner, per-run analysis Parquet evidence | Active leases/touches plus TTL cleanup. |

All artifact paths are validated to remain under the configured cache root.
Publication uses unique sibling temporary paths and `os.replace`. Lock
bookkeeping is bounded with 64 in-process stripes, while lock files provide
cross-process exclusion when processes share the same filesystem and cache root.

Read leases and access touching prevent normal TTL cleanup from deleting a file
that an active session is inspecting. Old run fragments can remain until their
lease/access state permits cleanup.

The following state is process-memory only:

- DataFrame query LRU;
- analysis/export controller state;
- inspector view-model and PNG cache;
- generated documentation PDF cache;
- Streamlit session state, including prepared export bytes.

Process restart loses these memory caches. Persistence of `.wspr_cache` across a
hosting restart depends on the platform filesystem and is not guaranteed by the
repository.

No namespace-wide byte quota, file-count quota, or minimum-free-disk policy is
implemented. Derived basemaps do not currently expire.

## External Services and Assets

### wspr.live

The primary external dependency is `https://db1.wspr.live/`, configured in
`config/app_config.py`. SQL is sent over HTTP and results are requested as CSV
with names or Parquet. Response time, schema compatibility, and availability are
outside this repository's control.

### Cartopy and Natural Earth

Cartopy supplies map projection support and obtains Natural Earth geographic
assets when they are not already available locally. First-use asset retrieval or
first construction of a unique basemap can be materially slower than a cache hit.

### Deployment Wake Workflow

`.github/workflows/wake.yml` uses Playwright on a six-hour schedule or manual
dispatch to open the deployed Streamlit URL. It is a keep-awake mechanism, not a
health assertion suite and not CI for repository changes.

### Relay Utility Services

The separate timed relay tool uses HID hardware and can use network time. Those
dependencies are isolated from the Streamlit application and are documented in
the tool directory.

## Module Dependency Rules

The intended dependency direction is:

```text
app.py
  -> ui/ Streamlit orchestration and adapters
     -> core/ contexts, scientific engines, data, artifacts, and rendering
        -> config/ constants and policy
```

Specific constraints enforced by code and tests include:

- core scientific and map modules must not import Streamlit;
- pure inspector view-model modules must not import Streamlit;
- UI adapters may read localized session values but must produce canonical core
  context values;
- map aggregation produces `MapData`; presentation rendering consumes it;
- fetch operations return structured results/errors rather than rendering UI;
- inspector and export consumers use declared evidence projections rather than
  loading arbitrary full artifacts;
- artifact consumers use the store API rather than constructing unsafe cache
  paths directly;
- runtime source directories remain regular packages with `__init__.py` markers
  so Streamlit watches their source files rather than recursively watching PEP
  420 namespace-package directories and reacting to first-import bytecode files.

`config/__init__.py` exposes compatibility imports, so dependency searches should
check both direct module imports and package-level re-exports.

## Important Design Decisions

### Scientific and Presentation Separation

Scientific inputs use canonical identifiers while localization is deferred to
presentation. This protects query and cache-key correctness and allows language
changes without changing numerical results.

### Explicit Evidence Schema

Opportunity evidence has an explicit schema and narrow consumer projections.
Categorical repeated values and ownership-aware processing reduce DataFrame
memory without reducing coordinate, SNR, or solar-calculation precision.

### File-Backed Evidence

Large opportunity evidence is stored as session Parquet rather than retained as
a complete Streamlit object graph. The inspector and exports reload only required
columns. Leases preserve interactive continuity across Streamlit reruns.

### Local Single-Flight and Atomic Publication

Expensive shared artifact construction is coordinated by key. Unique temporary
files plus atomic replacement prevent readers from observing partial output.
Bounded lock stripes prevent unbounded in-memory lock growth.

### Admission Before Expensive Work

Analysis and export work enters explicit FIFO gates before consuming upstream,
CPU, rendering, or ZIP resources. Duplicate rejection limits accidental
same-session amplification while preserving independent demo use by other users.

### Serialized Matplotlib Rendering

Matplotlib access is serialized because global rendering state is not treated as
concurrently safe. This favors correctness and stable multi-user behavior over
parallel figure throughput.

### Lazy Secondary Work

Documentation rendering, PDF creation, inspector selected-station preparation,
and export construction are delayed until needed. This reduces initial page and
analysis work while retaining the complete educational documentation and export
capabilities.

## Technical and Operational Risks

1. **Public resource exhaustion:** The process-local gates cap active and queued
   work but there is no IP rate limit, authentication, rolling request budget, or
   distributed quota. Multiple sessions can be created by one client.
2. **Process scope:** Admission, deduplication, Matplotlib serialization, and RAM
   caches do not coordinate separate hosts or processes. Artifact file locks only
   coordinate processes sharing the same cache filesystem.
3. **Streamlit security settings:** `.streamlit/config.toml` disables CORS and
   XSRF protection. The deployment reason is not documented in code. Restoring
   protection requires deployment testing, but the current state is a real public
   deployment risk.
4. **Unbounded persistent cache size:** TTL cleanup exists for queries and
   session artifacts, but there are no byte/file quotas and derived basemaps do
   not expire.
5. **Export memory:** ZIPs are built and retained in memory. Single-export gating
   limits concurrency but not the size of one export.
6. **Dependency reproducibility:** Most Python dependencies are unpinned. There
   is no lock file, hash checking, automated vulnerability audit, or test CI.
7. **External availability:** wspr.live and first-use Cartopy asset downloads are
   outside application control. Bounded HTTP work prevents indefinite or
   unlimited responses but cannot make an unavailable service succeed.
8. **Regression-fixture gap:** The generated scientific fixture is absent, so one
   fixture-integrity test is skipped. Historical demo export files use an older
   schema and do not close this gap.
9. **Browser/multi-process coverage:** The regression suite covers pure logic,
   contracts, concurrency primitives, and documentation behavior, but no current
   browser end-to-end or multi-process deployment suite was found.
10. **Generated documentation ownership:** Running the README sync script
    overwrites the entire README. Changes made only to generated output will be
    lost.
11. **Requests session concurrency:** A shared Requests session is used. The
    repository does not contain an explicit comprehensive thread-safety contract
    test for that library object, so this remains uncertain.

## Verification Record

The following checks were run during this documentation review on 2026-07-11:

```text
Python: 3.12.13
Streamlit: 1.58.0
pandas: 3.0.3
NumPy: 2.4.6
pytest: 9.1.1
runtime dependency imports: passed
python -m pip check: passed
python -m compileall: passed
python -m pytest tests/regression -q: 116 passed, 1 skipped
Streamlit /_stcore/health: 200 ok
```

No project linter is configured, so no lint command could be run. A clean
dependency installation, development-container build, Streamlit Community Cloud
deployment, browser end-to-end test, and multi-process load test were not run.
