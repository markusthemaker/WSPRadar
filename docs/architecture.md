# WSPRadar Architecture

This document describes the repository as inspected on 2026-07-11. It derives
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
- initializes Streamlit page and session state;
- renders language, demo, and analysis configuration controls;
- validates the requested time interval;
- starts TX or RX analysis through `ui/run_controller.py`;
- renders delayed documentation through `ui/documentation.py`.

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
| `config/app_config.py` | Application identity, URLs, time-window limit, cache and HTTP limits, analysis/export admission settings, inspector cache, and documentation delay. |
| `config/bands.py` | WSPR band labels and wspr.live numeric identifiers. |
| `config/demo_profiles.py` | Guided demo configuration and historical examples. |
| `config/plot_constants.py` | Map extent, projection/render constants, colors, and scientific display constants. |
| `config/__init__.py` | Compatibility re-exports for configuration consumers. |

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
- sequential WSPR frame comparisons;
- TX and RX opportunity analyses.

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
and sequential observations. `core/snr_utils.py` centralizes normalized-SNR
rounding and CSV formatting. `core/stability.py` performs deterministic,
optionally chunked bootstrap stability calculations.

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

`core/math_utils.py` contains callsign/locator validation, Maidenhead coordinate
conversion, time quantization, geometry, and solar helpers.

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

### Export Pipeline

`ui/results_export.py` registers export recipes and analysis context during a
run. Export preparation is lazy and protected by a separate admission controller
from `core/export_admission.py`. The configured policy allows one active export
and up to ten queued exports.

Preparing an export reuses completed analysis and projected artifacts; it does
not rerun the upstream scientific query. It renders paper-theme, high-resolution
figures and packages configuration, metadata, CSV tables, compact Parquet
evidence, and PNGs.

The ZIP is currently constructed in `io.BytesIO` and retained in Streamlit
session state for download. This is a known peak and idle-memory risk, partially
contained by single-export admission.

### Documentation Pipeline

`docs/doc_en.py` and `docs/doc_de.py` hold the full manuals as source strings.
`ui/documentation.py` renders the selected manual in a delayed Streamlit fragment
and applies CSS content visibility so initial page elements can appear first.

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
3. `analysis_runner` builds the mode-specific comparison SQL.
4. `data_engine` returns a RAM-cache, disk-cache, or wspr.live result.
5. Post-fetch logic synchronizes cycles and applies mode-specific rounding.
6. `compare_engine` builds station and segment aggregates.
7. The processed rows are written to a session Parquet artifact.
8. `map_data` and `plot_engine` render the map preview.
9. Inspector view models read the necessary evidence and render segment and
   selected-station views.
10. Export recipes are registered for optional later execution.
11. The permit is released in all completion/error paths.

### Opportunity Analysis

1. An active-cycle ClickHouse query returns one row per time slot and peer
   identity with target/external evidence and target SNR.
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
  paths directly.

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
