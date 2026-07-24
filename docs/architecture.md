# WSPRadar Architecture

This document describes the repository as inspected through 2026-07-23. It derives
component boundaries and behavior from the application code, configuration, and
regression tests. Items explicitly marked uncertain were not established by the
code or by the verification run.

## System Context

WSPRadar is a single Streamlit application process that queries historical WSPR
observations from public read-only ClickHouse HTTP endpoints. wspr.live is the
primary source, followed by WSPRDaemon WD2 and WD1. Scientific work is performed
in core modules, while Streamlit state, controls, presentation, and downloads are
managed in UI modules. Local process memory and a local artifact directory
provide caching and session continuity.

```text
Browser
  -> Streamlit app.py
     -> UI configuration and context adapters
     -> analysis/export admission controllers
     -> analysis runner and data engine
        -> provider dispatcher
           -> wspr.live -> WD2 -> WD1 ClickHouse HTTP APIs
        -> source-isolated query/session artifact store
     -> compare or opportunity engines
     -> map data and presentation rendering
     -> inspector view models and projected evidence reads
     -> optional export preparation
```

The application reads one selected source per complete run. No upstream write
path or database credential was found.

## Entry Points

### Application

`app.py` is the Streamlit entry point. It:

- enables Python fault handling;
- emits page configuration and the lightweight application shell before
  importing scientific analysis dependencies;
- initializes Streamlit session state;
- renders language, demo, the persistent Guided/Classic input-view selector,
  and analysis configuration controls;
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
| `config/app_config.py` | Application identity, ordered provider URLs and process-local budgets/cooldowns, time-window limit, cache and HTTP limits, analysis/export admission settings, and inspector-cache limits. |
| `config/bands.py` | WSPR band labels and wspr.live numeric identifiers. |
| `config/demos/*.config` | Authoritative guided demos. Each file is a standalone saved configuration and lexicographic filename order defines launcher order. |
| `config/demo_profiles.py` | Strict dependency-free demo discovery, schema/profile validation, duplicate-ID protection, and stable filename-ordered `DEMO_PROFILES` mapping. |
| `config/config_schema.py` | Saved-config format identifier, current schema version, grouped settings contract, and canonical enum values. |
| `config/config_codec.py` | Dependency-free document-envelope and schema-version validation shared by personal-config and demo readers. |
| `config/wspradar-config.schema.json` | Formal JSON Schema for every saved and demo configuration. |
| `config/guided_input_flow.json` | Ordered Guided Input nodes, branch conditions, required state fields, and registered renderer names. |
| `config/guided_input_flow.schema.json` | Strict Draft 2020-12 schema for the declarative Guided Input flow. |
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
schema version, while `ui/config_io.py` validates and applies the semantic
settings. Version 1 is explicitly pre-production, not a first public production
contract. It may be revised in place before the first production release, and
earlier unpublished version-1 prototypes are rejected rather than migrated or
guessed. After a configuration schema has been published for production, a
subsequent schema bump is incomplete until every preceding supported production
version has an explicit ordered migration; unsupported versions are rejected
rather than interpreted with current defaults.

Every active comparison carries an explicit `snr_correction_mode` beside
`snr_correction_db`. `no_offset` means that no established correction is
applied; `establish_offset` marks a deliberately uncorrected baseline run; both
require exactly `0.0 dB`. `established_offset` applies a documented signed value
and explicitly permits a genuinely established `0.0 dB`. Local Neighborhood
supports `no_offset` and `established_offset` but not the controlled
offset-establishment workflow. Success-only documents omit both correction
fields. Applicable unpublished v1 documents without the mode are rejected:
neither the numeric value nor profile identity is used to guess its meaning.

Reference Station comparison state stores `reference_callsign` plus an
independent `reference_qth` constrained to exactly four Maidenhead characters.
RX Hardware A/B stores only the distinct `reference_callsign`; both displayed
grid-4 values and both SQL locator predicates derive from core Target `qth`.

The TX Hardware A/B branch records a required `tx_ab_method`. New session state
defaults to `simultaneous`; that active branch stores `reference_callsign` and
derives both comparison grid-4 values from the first four characters of core
Target `qth`. It deliberately omits redundant `reference_qth`. The `sequential`
branch instead stores a shared
`repeat_interval_minutes` plus disjoint `target_start_minute` and
`reference_start_minute` phases. The UI exposes **Repeat Interval**,
**Target Start**, and **Reference Start** only for sequential operation, offers
intervals of 4, 6, 10, 12, 20, 30, or 60 minutes, restricts starts to distinct
even phases below the interval, and defaults them to 10, 0, and 2 minutes.
Sequential Compare always assigns planned pairs from this schedule; the
unpublished fixed-bin prototype is not a supported runtime branch. This remains
schema version 1: pre-production v1 documents without the now-required active
branch fields are rejected rather than migrated or guessed.

The reusable configuration's optional `profile` carries the stable ID and
localized presentation text used by built-in demos. `config/demo_profiles.py`
discovers regular `config/demos/*.config` files in lexicographic filename order.
Each filename is an opaque ordering key independent of the document's required
`profile.id`. Profile IDs provide generic identity for loading, cache policy and
request ownership; runtime code must not use a literal profile ID as a feature
flag or record-specific dispatch key. There is no second demo envelope or schema: a personal
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

### Input Editors

Guided Input and Classic Input are two Streamlit compositions over the same
canonical `val_*` session fields. `input_view` defaults to `guided` and persists
for the browser session, but the editor choice and Guided navigation keys are
transient presentation state outside `AnalysisContext` and the version-1 saved
configuration. Correction mode is different: it is durable operator provenance
stored in the configuration, held in the canonical
`val_snr_correction_mode` field, and preserved when editors switch. Guided
renders the three-way choice directly from this field. Classic keeps its
numeric editor; entering a nonzero value generically selects
`established_offset`, while an explicit established `0.0 dB` remains
distinguishable from `no_offset`. Switching editors therefore does not
translate, copy, or reset the scientific values. `ui/components/config_fields.py` is the shared
composition surface for Target/window, Reference, scope, station-population,
offset, and evidence-threshold controls; its established implementations remain
in `ui/components/config_panel.py` so both editors retain the same widget keys,
normalization, and callbacks.

`config/guided_input_flow.json` declares the ordered question graph from use
case through review. `ui/guided_inputs/flow_loader.py` performs bounded strict
JSON decoding, Draft 2020-12 schema validation, registered-renderer checks,
bilingual content-key checks, and graph reachability/cycle validation before
the flow is rendered. `ui/guided_inputs/flow_engine.py` evaluates its restricted
condition vocabulary without arbitrary session-state access.
`ui/guided_inputs/state.py` derives and validates transient Guided decisions
from canonical fields, including reconstruction after a saved configuration or
demo is loaded. It consumes correction mode generically and never dispatches on
profile identity or infers the mode from `snr_correction_db`.
`ui/guided_inputs/renderer.py` composes the accordion and
registered renderers, while the separate bilingual `GUIDED_INPUTS` structure in
`i18n.py` owns Guided explanations and choice consequences. Built-in demos are
load-only in Guided Input so their metadata and preset settings can be reviewed;
Classic retains the immediate demo-run action.

### Context Boundary

`core/analysis_context.py` defines an immutable `AnalysisContext` containing
canonical scientific settings. `ui/analysis_context_adapter.py` translates
canonical Streamlit session values into that context. Reference
Station identity consists of `reference_callsign` plus an independently entered,
exactly four-character `reference_qth` grid. RX and simultaneous TX Hardware A/B
carry only the distinct `reference_callsign`; both sides use the grid-4 derived
from core Target `qth`. TX Hardware A/B additionally carries the canonical
`tx_ab_method`. Target and Reference role names are presentation terms and do
not replace these scientific identity fields.

`snr_correction_mode` does not enter `AnalysisContext`, SQL, cache identity or
the scientific request fingerprint. It records why a correction value is being
used; only the validated numeric `snr_correction_db` becomes
`AnalysisContext.reference_snr_correction_db`. Runs with the same numeric value
therefore remain scientifically identical even when one is explicitly marked
as an offset-establishment workflow.

`AnalysisContext.max_peer_distance_km` is a canonical scientific input. The UI
presents it as **Maximum peer distance from Target (km)**. A peer row
is in scope only when its distance from Target QTH is strictly less than this
value. The scope therefore participates in request identity and constrains
retained evidence, calculations, artifacts, exports, the map/footer, and the
Segment Inspector; it is not merely a rendering extent.

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

`ui/result_hierarchy.py` owns the pure, escaped HTML builders and localized
scope-copy helpers for the progressive result flow from map overview through
row-level evidence. `ui/run_controller.py` places the map and deferred Inspector
inside one keyed presentation container so CSS can draw a responsive evidence
spine without coupling the hierarchy to scientific data or figure recipes.
Keyed level containers delimit the five semantic zoom stages, allowing each
stage to retain its own node and rerender boundary while all stages overlay the
same fine spine width. The parent retains one continuous fallback line and
removes the decoration at the mobile breakpoint.

Provider readiness participates in the same FIFO admission decision as the two
active-analysis slots. Once admitted, the controller prepares every block
required by the selected active result against one provider before publishing
it. A no-benchmark run prepares Success only; a run with any benchmark prepares
Compare only. Strict and legacy compatibility requests remain on that provider.
A classified provider failure deletes the attempt's unregistered session
artifacts, releases its reservation, and restarts the complete active-result
bundle from Map 1 on the next source.
Valid empty/scientific no-evidence results and local processing failures do not
selectively switch databases.

It also implements compatibility retry behavior for historical rows where a
strict `code = 1` query returns no target evidence. The retry metadata is exposed
in results and tested. This is scientific compatibility behavior and should not
be changed as a generic query optimization.

### Query and Fetch Layer

`core/analysis_runner.py` builds ClickHouse SQL for:

- TX and RX comparison analyses;
- local, fixed-reference and same-cycle hardware A/B comparisons;
- periodic scheduled TX A/B comparisons;
- TX and RX opportunity analyses.

All analysis SQL uses the half-open UTC predicate `start <= time < end`.
Scheduled TX A/B post-fetch eligibility applies the same convention to both
planned starts, so adjacent windows cannot share an observation or planned
pair.

Every Success and Compare Target branch requires the exact direction-specific
callsign and a reported endpoint locator whose first four characters equal the
configured Target QTH grid-4. The complete four- or six-character Target QTH is
retained separately as the geographic origin for map, radius, distance/azimuth,
and solar calculations. Reference Station requires the exact Reference callsign
and a reported endpoint locator matching its independently configured, exactly
four-character Reference grid-4. RX and simultaneous TX Hardware A/B require
distinct callsigns but derive the shared grid-4 for both sides from Target QTH;
there is no independent Hardware `reference_qth`. Physical co-location remains
an experiment invariant that archive rows cannot prove. Local benchmarks select
geographically eligible callsign/full-locator identities. Sequential TX
Hardware A/B applies the shared Target callsign and grid-4 to both schedule
branches.

For periodic hardware A/B Compare work, SQL applies the exact UTC-minute modulo
predicate for each path's repeat interval and start phase. Comparison post-fetch
processing rejects rows outside their assigned path schedule and attaches stable
`tx_ab_pair_id`, `tx_ab_pair_target_time`, and
`tx_ab_pair_reference_time` columns before evidence is written to Parquet.
It also applies mode-specific post-fetch synchronization and filtering.

Geographic Analysis Scope is deliberately a post-fetch scientific gate, not a
provider-SQL predicate. Provider responses and their raw-query cache entries
therefore remain global and reusable across scope choices. Post-fetch
processing resolves each peer's coordinates and retains the row only when its
great-circle distance from Target QTH is strictly less than
`AnalysisContext.max_peer_distance_km`. The retained population is then used for
thresholds, aggregation, session Parquet artifacts, exports, map/footer, and
Inspector evidence.

Two integrity rules intentionally operate on the geographically global,
otherwise eligible post-fetch population before this geographic gate. In
Compare, solar selection occurs first, followed by moving-station integrity and
then Target-Active synchronization before geographic scope. Target-Active
synchronization may therefore use an out-of-scope row to establish that the
Target was active, but that row cannot subsequently contribute an outcome,
rate, count, artifact, or export. When moving-station exclusion is enabled, a
peer's locator history is likewise evaluated before scope filtering, so
choosing a narrower scope cannot hide evidence that the peer moved. Scheduled
TX A/B pair assignment also precedes geographic filtering.

`core/data_engine.py` executes HTTP requests and returns structured
`FetchResult`, delivery-tier, database-source, and error data without rendering
Streamlit UI. It provides:

- a process-memory DataFrame LRU;
- provider-scoped exact-query SHA-256 disk-cache keys;
- a separate provider-scoped demo-query namespace with an absolute 24-hour
  freshness lifetime;
- CSV and Parquet response handling;
- connect/read deadlines;
- streamed byte accounting and decompressed response ceilings;
- unique temporary files and atomic promotion through the artifact store;
- bounded error-response capture.

The engine logs query and performance information to the terminal. Structured
fetch failures carry a safe lifecycle stage; the `analysis_fetch_failure`
performance event adds that stage and, when an artifact path is available, the
cache namespace and policy. It deliberately excludes the SQL text and captured
error body. The engine holds a module-level Requests session. Explicit proof of
all concurrent session-use semantics was not found, so thread-safety beyond the
exercised tests remains an operational uncertainty.

`core/provider_dispatch.py` owns ordered provider selection, conservative
complete-run request reservations, rolling actual-request timestamps, HTTP 429
cooldowns, transient-failure circuits and half-open probes. A cache hit consumes
no request token. For guided demos, the dispatcher can stably promote the
configured-first zero-request provider ahead of network-backed candidates after
allowed/excluded-source filtering. `core/run_data_preparation.py` owns the
transactional source-pinned prepare phase and writes processed blocks to unique,
unregistered session artifacts so potentially large frames can be released one
at a time. Database provenance is distinct from RAM/disk delivery tier.

### Scientific Engines

`core/compare_engine.py` performs pure comparison aggregation for simultaneous
and scheduled observations. Simultaneous TX Hardware A/B follows the same
Target-Active, peer-cycle consolidation, joint Delta SNR and one-sided outcome
path as other fixed-reference same-cycle comparisons. For periodic TX A/B
analysis, each planned Target
slot is paired bijectively with its nearest planned Reference slot. An exact
half-interval tie pairs the lower and higher phases in the same repeat cycle,
independent of which path is called Target. Aggregation includes peer identity
in the pair key, takes a micro-median when one peer has multiple decoded rows
on either side of a scheduled pair, and computes Delta only for a pair with
both sides. Boundary pairs are admitted only when both planned transmission
starts satisfy `start <= planned_start < end`.

`core/tx_ab_schedule.py` owns supported repeat-interval and start validation,
the exact ClickHouse schedule predicate, hourly previews, cyclic separation,
and stable planned-pair assignment. `core/snr_utils.py` centralizes
normalized-SNR rounding and CSV formatting. `core/evidence_statistics.py`
centralizes neutral evidence-metric formatting, histogram-bin selection and
plot-limit helpers.

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

`core/input_validation.py` contains dependency-free callsign and Maidenhead
locator validation. Core Target QTH accepts four or six characters; the
Reference Station comparison field requires exactly one grid-4, while Hardware
A/B derives its grid-4 from Target QTH rather than accepting Reference locator
state. `core/time_utils.py` contains dependency-free query-time
quantization. Keeping these idle-shell helpers separate prevents NumPy-backed
geometry from loading before an analysis is requested. `core/math_utils.py`
retains compatibility exports while owning Maidenhead conversion, geometry, and
solar helpers for the scientific path.

### Map Pipeline

`core/map_data.py` converts comparison or opportunity rows into pure `MapData`
aggregates. `core/map_models.py` defines the `MapData` and `MapFigure` contracts.
These consumers receive evidence already constrained by Geographic Analysis
Scope. The same maximum distance controls the rendered extent and footer, so
the visible map and its reported scope describe the scientific population
rather than applying a second presentation-only filter.

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

Inspector range and direction controls may narrow the retained geographic
population for exploration, but they cannot widen the completed run or
re-admit peer rows excluded by Geographic Analysis Scope. A broader scientific
scope requires a new analysis run.

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
session artifacts and clear export, inspector, and resolved-time
state without importing Pandas, Matplotlib, the inspector, or export rendering.
`ui/analysis_submission_state.py` separately owns the UUID-token lifecycle for
one session's in-flight analysis. Keeping submission state separate from
`run_mode` is required because `run_mode` remains set while completed results
are reconstructed on later Streamlit reruns.

Preparing an export reuses completed analysis and projected artifacts; it does
not rerun the upstream scientific query. It renders paper-theme, high-resolution
figures and packages configuration, metadata, CSV tables, compact Parquet
evidence, and PNGs. Comparison artifacts are grouped under `compare/`; Success
artifacts are grouped under `success/`, with the same names reflected in run
metadata.

The ZIP is currently constructed in `io.BytesIO` and retained in Streamlit
session state for download. This is a known peak and idle-memory risk, partially
contained by single-export admission.

### Page Navigation

`ui/page_navigation.py` owns the language-independent, always-mounted runtime
anchors `wspradar-page-top`, `wspradar-parameter-settings`, and
`wspradar-results-inspection`. Its one-pixel browser controller tracks the
active application region only while the viewport is above the documentation
boundary; the documentation controller owns fragments from that boundary
downward. Passive scrolling replaces the current fragment without adding
browser-history entries. Guided Continue replaces a stale manual fragment with
the parameter-settings anchor without forcing a scroll. Loading a demo and
either demo navigation action (Walkthrough or Skip) may request a one-shot
scroll to the appropriate application region. The main Run action clears stale
manual navigation without issuing a scroll request, so the processing statements
and their in-place System Audit Status replacement remain in the current
viewport while passive location tracking continues. Application and manual
anchors have disjoint ownership, unknown fragments remain untouched, and Back
or Forward scrolls the anchor owned by the corresponding controller without
adding another history entry. Application navigation also cancels any
unresolved manual-navigation request so a later documentation fragment rerun
cannot reclaim the viewport.

### Documentation Pipeline

`docs/doc_en.py` and `docs/doc_de.py` hold the full manuals as source strings.
`ui/documentation.py` initially renders only the Part 0 preface in a Streamlit fragment.
`ui/documentation_scroll_trigger.py` mounts a one-pixel browser controller
immediately before visible Section 0.3 (the stable `sec-1-3` anchor). Its
visibility sentinel renders the table of contents and remaining chapters once
per session when that boundary enters the viewport while the reader finishes
Section 0.3. The same controller intercepts an explicit preface link only when
its known manual anchor is not yet mounted, retains that anchor across the
documentation-fragment rerun, expands the manual, and completes the deferred
same-page navigation after the target enters the DOM. Existing mounted anchors,
external links, modified clicks, and middle clicks retain native browser
behavior. A fresh direct URL fragment for a deferred manual anchor uses the same
expansion path. While the reader scrolls through the mounted manual, the browser
controller replaces the current URL fragment with the last explicit manual
anchor that crosses the existing landing offset; scrolling therefore keeps a
meaningful return location without adding browser-history entries. Explicit
internal-link navigation still creates a history step. Back and Forward
explicitly scroll an already mounted manual anchor, or reuse the expansion path
when that history target is not mounted.
After lazy content mounts, the same controller assigns documentation-only
weighted column layouts to four anchor-bounded tables. Each multiplier is
applied to the localized table's natural browser widths and normalized back to
the unchanged total table width.
Hiding an already loaded manual does not immediately re-expand it.
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
2. The controller validates inputs and obtains one combined analysis/provider
   permit from the bounded FIFO queue.
3. `analysis_runner` builds the mode-specific comparison SQL. Reference Station
   uses its exact callsign plus independent Reference grid-4; simultaneous
   Hardware A/B uses distinct callsigns plus one Target-derived grid-4. Periodic
   TX A/B predicates select each path by its exact repeat interval and UTC start
   phase.
4. `run_data_preparation` fetches and processes every block required by the
   active Compare result against the selected provider. Any provider failover
   restarts this unpublished phase.
5. Post-fetch logic applies solar selection, evaluates moving-station integrity
   and then Target-Active synchronization against the geographically global
   population that otherwise remains eligible, and finally retains only peers
   strictly nearer than Geographic Analysis Scope. For
   periodic TX A/B data it also filters schedule mismatches, excludes a boundary
   pair unless both planned starts satisfy `start <= planned_start < end`, and
   assigns the stable planned-pair columns before geographic filtering.
6. The geographically scoped processed rows, including planned-pair columns,
   are staged as an unregistered session Parquet artifact. All successful blocks
   are registered together after complete active-result preparation succeeds.
7. `compare_engine` groups periodic pairs by peer identity and pair ID, applies
   per-side micro-medians, and builds station and segment aggregates.
8. `map_data` and `plot_engine` render the map preview.
9. Inspector view models read the necessary evidence and render segment and
   selected-station views.
10. Export recipes are registered for optional later execution.
11. The permit is released in all completion/error paths.

### Opportunity Analysis

1. In a no-benchmark Success run, an active-cycle ClickHouse query returns one
   row per time slot and peer identity with target/external evidence and target
   SNR. Hidden benchmark and scheduled TX A/B settings do not participate in
   this standalone Success query.
2. The fetched globally Target-Active frame is normalized into the explicit
   opportunity schema. Peer coordinates are assigned without a full coordinate
   merge, outcomes are classified, and solar path enrichment operates on the
   owned frame.
3. Target-QTH solar selection and global moving-station integrity are applied,
   followed by Geographic Analysis Scope; only peers strictly nearer than the
   configured maximum remain.
4. The final categorized, geographically scoped artifact is written as session
   Parquet.
5. Map and segment aggregates use the corresponding narrow projections.
6. The inspector loads selected evidence only when required.

### Duplicate and Admission Flow

`core/analysis_admission.py` implements FIFO admission with a condition variable,
active leases, queue timeouts, and bounded active/queued counts. Each Streamlit
session receives a stable owner identifier. The request key includes canonical
scientific inputs, including `max_peer_distance_km`, and demo identity. Changing
Geographic Analysis Scope therefore defines a distinct scientific request even
though provider raw-query cache entries remain reusable because the gate is
post-fetch.

A session cannot enqueue an identical request while its matching work is active
or queued. Different sessions may run the same demo; this avoids turning popular
demos into a cross-user single-result dependency. Admission state and deduplication
are process-local and do not coordinate multiple application processes.

The Run callback creates a session-scoped UUID submission token before the
blocking script rerun begins. While that token is owned by a queued or active
script, the Run action is disabled and another Streamlit rerun does not enter
admission again. Terminal paths clear only the token they own, preventing an
interrupted older script from clearing newer state. As a defensive fallback,
the admission controller can look up an existing owner/request pair: duplicate
rendering restores that request's personal queue position, or reports it as
active, and follows it until release instead of replacing its status with an
unrelated duplicate notice or acquiring a second permit. After release, that
latest script performs one controlled rerun to reconstruct the published result
and remove its final waiting status.
Scientific configuration callbacks explicitly retire the current UI token when
their new request replaces the queued or active one; Streamlit interruption then
unwinds the old admission permit or ticket. The visible queue status deliberately
omits global active and queued counts.

Loading a built-in demo marks the applied inputs with that profile's trusted
demo identity, and the ordinary direction-aware Run action preserves it.
Scientific-control callbacks clear the identity after an edit, returning the
modified configuration to the ordinary one-hour query-cache policy. Thus an
unchanged loaded demo and an immediately launched demo share the same 24-hour
cache namespace and provider-affinity behavior.

The first FIFO ticket can become active only when an analysis slot and a
complete-run provider reservation are both available. Provider reservation uses
the maximum currently uncached strict/legacy request count. The front ticket
reinspects source-specific caches on every reservation attempt, and fallback
recalculates them again. For a guided demo, a zero-request estimate means one
provider has the complete currently required bundle, so the first such provider
in configured order is preferred before any network-backed candidate. Each
actual HTTP attempt converts one reservation into a rolling-window timestamp;
unused slots are released. If every provider is temporarily unavailable, the
request stays in the existing bounded queue and eventually reaches its normal
timeout or causes later requests to receive the existing queue-full response.

This combined FIFO decision applies to initial admission. If a provider fails
after a run has become active, that run keeps its analysis slot while it waits
for an eligible fallback reservation; at most the configured active-run limit
can therefore be waiting in this mid-run state.

### Provider Selection and Failover Flow

1. Inspect source-specific caches and calculate a conservative request
   reservation for each enabled provider.
2. For a guided demo, first select the configured-first eligible provider whose
   complete current bundle requires zero HTTP requests. If none exists, or for
   an ordinary run, select the first eligible source in
   `wspr.live -> WD2 -> WD1` order.
3. Pin the selected active result's complete strict/legacy request bundle to
   that source.
4. Stage processed artifacts without exposing maps, inspectors or export blocks.
5. On a provider-scoped failure, delete staged attempt artifacts, mark the
   provider's cooldown/circuit state and restart Map 1 on the next source.
6. If a cache entry disappears after reservation planning, or cached raw rows
   fail the required schema, make no unreserved HTTP request. Remove an invalid
   entry, discard the attempt, recalculate capacity without marking the provider
   unhealthy, and restart the unpublished bundle. Providers bypassed only by
   cache affinity remain eligible during this replan.
7. On complete preparation, commit the run source, register all staged artifacts
   and publish results. A later rerender of the same `run_id` remains pinned.

HTTP 408/429/5xx responses, transport timeouts/errors, malformed payloads and
incompatible non-empty response schemas are provider-scoped. Valid empty data,
the response-size safety ceiling, normal request/input errors, local filesystem
errors, post-filter warnings and scientific no-evidence outcomes do not trigger
cross-database selection.

## Persistence and Cache Lifecycles

`core/artifact_store.py` divides local artifacts into four namespaces:

| Namespace | Contents | Lifecycle |
| --- | --- | --- |
| `queries` | Provider-scoped ordinary exact-query Parquet responses | One-hour last-access freshness and cleanup. |
| `demo-queries` | Provider-scoped raw Compare and Success demo-query rows, stored as Parquet | Absolute 24-hour freshness and cleanup; reads never extend publication time. |
| `derived-analysis` | Shared basemap PNGs | Reused across sessions; no current TTL cleanup. |
| `session-artifacts` | Per-owner, per-run analysis Parquet evidence | Active leases/touches plus one-hour cleanup. |

All artifact paths are validated to remain under the configured cache root.
Publication uses unique sibling temporary paths and `os.replace`. Lock
bookkeeping is bounded with 64 in-process stripes, while lock files provide
cross-process exclusion when processes share the same filesystem and cache root.

Submission-triggered TTL cleanup is process-local single-flight and throttled to
one completed sweep per 60 seconds. Overlapping or more-recent callers return
without rescanning; a failed sweep does not advance the throttle. Consequently,
physical deletion can lag a TTL boundary, while read-time freshness checks still
prevent an expired query artifact from being reused.

Ordinary namespace sweeps exclude every recognized unique atomic temporary
sibling from TTL and future-timestamp decisions. A separate orphan pass considers
only temporary names that encode the store's atomic-publication contract and are
older than the stale-lock horizon, then acquires and rechecks under the encoded
destination's key lock before deletion. Query and demo-query timestamps are
compared with a fresh clock reading at each decision; only a modification time
more than five seconds ahead is treated as materially future-dated. Routine
cleanup deliberately does not prune empty namespace or provider directories,
because removing a writer's parent between directory creation and temporary-file
open would violate the atomic-publication lifecycle. Published derived basemaps
remain untimed, but their recognized stale temporary siblings participate in
the orphan pass.

Read leases and access touching prevent normal TTL cleanup from deleting a file
that an active session is inspecting. An active rerun refreshes its registered
session artifacts before global TTL cleanup and again after any admission wait.
Old run fragments can remain until their lease/access state permits cleanup.
Demo-query reads still take the same-key coordination lock but deliberately do
not touch the file: its publication mtime is the immutable freshness anchor,
and any RAM L1 entry expires at that same absolute deadline.

Compare continues to request upstream CSV because that is its established
transport and parser path, but guided-demo CSV rows are converted to raw
Parquet in the disk L2 before scientific post-fetch processing. Success keeps
its upstream Parquet transport and publishes it in the same demo namespace.
Consequently both demo analysis types survive a process-memory eviction or
restart when the local cache filesystem survives, without caching completed
scientific output across code changes.

The following state is process-memory only:

- DataFrame query LRU;
- analysis/export controller state;
- provider rolling request timestamps, reservations and circuit/probe state;
- inspector view-model and PNG cache;
- generated documentation PDF cache;
- Streamlit session state, including prepared export bytes.

Process restart loses these memory caches. Persistence of `.wspr_cache` across a
hosting restart depends on the platform filesystem and is not guaranteed by the
repository.

No namespace-wide byte quota, file-count quota, or minimum-free-disk policy is
implemented. Derived basemaps do not currently expire.

## External Services and Assets

### WSPR ClickHouse sources

The ordered external data dependencies configured in `config/app_config.py` are:

1. wspr.live: `https://db1.wspr.live/`;
2. WSPRDaemon WD2: `https://wd2.wsprdaemon.org/`;
3. WSPRDaemon WD1: `https://wd1.wsprdaemon.org/`.

SQL is sent over read-only HTTP and results are requested as CSV with names or
Parquet. Response time, schema compatibility, data synchronization and
availability are outside this repository's control. The configured WD request
budgets are conservative local policies, not claims about published service
quotas.

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
columns. These artifacts contain only the peer rows retained by Geographic
Analysis Scope, so neither Inspector controls nor export preparation can
reconstruct or re-admit excluded peers. Leases preserve interactive continuity
across Streamlit reruns.

### Local Single-Flight and Atomic Publication

Expensive shared artifact construction is coordinated by key. Unique temporary
files plus atomic replacement prevent readers from observing partial output.
Bounded lock stripes prevent unbounded in-memory lock growth.

### Admission Before Expensive Work

Analysis and export work enters explicit FIFO gates before consuming upstream,
CPU, rendering, or ZIP resources. Duplicate rejection limits accidental
same-session amplification while preserving independent demo use by other users.

### One Database Source per Published Run

Provider choice is scientifically material because the public databases are not
assumed perfectly synchronized. The single active Compare or Success result and
every strict/legacy request in one published run therefore share one stable
`DatabaseSource`. Provider failure restarts the unpublished active-result bundle
rather than continuing another block elsewhere. Query cache keys include
provider identity, while cache medium
remains separate provenance. The committed source is shown in System Audit
Status and stored once in export run metadata; each map's strict and optional
legacy query reports its own database-request, RAM-cache, or disk-cache delivery
tier and timing. Provider leases retain ordered skip reasons plus separate
cache-affinity metadata, so the origin annotation distinguishes selection of the
primary source, request-capacity spillover to a lower-priority ready source,
demo cache affinity for a complete zero-request bundle, fallback after a
provider-scoped failure or existing provider-health cooldown/recovery probe, and
reuse of an already committed source on rerender. Cache affinity changes only
selection order: provider-scoped keys, actual origin, and the one-source bundle
remain intact. Database origin is not a user configuration or scientific
fingerprint input.

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

1. **Public resource exhaustion:** The process-local gates and per-provider
   rolling budgets cap this process's work, but there is no authentication,
   client/IP admission limit or distributed quota. Multiple sessions can be
   created by one client.
2. **Process scope:** Admission, provider budgets/circuits, deduplication,
   Matplotlib serialization, and RAM caches do not coordinate separate hosts or
   processes. Several replicas sharing one egress IP can therefore exceed a
   provider limit even when each local counter is compliant. Artifact file locks
   only coordinate processes sharing the same cache filesystem.
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
7. **External availability and divergence:** wspr.live, WD2, WD1 and first-use
   Cartopy asset downloads are outside application control. Bounded HTTP work and
   failover improve availability but cannot guarantee synchronized database
   contents or make every unavailable/incompatible service succeed.
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
