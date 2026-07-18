# WSPRadar Daily Changelog

This changelog summarizes major project changes by GitHub submission date (UTC), with the newest entry first. It is grouped by submission rather than by version because early version labels were not yet stable; work completed across several unsubmitted days is consolidated under the date on which it is submitted.


## 2026-07-18

- Unified guided demos and personal saves under one strict, self-describing version-1 `wspradar.config` format with a formal JSON Schema and shared dependency-free codec. Filename-ordered standalone files under `config/demos/` now define the demo launcher, including Zander Experiment B; the required RX/TX Analysis selector drives direction-specific controls and Run Analysis behavior. Save Config captures applicable runnable settings plus stable Segment Inspector and station-view intent without rerunning analysis, while strict decoding rejects malformed, incomplete or unsupported documents with precise diagnostics.
- Replaced sequential TX A/B fixed-bin configuration for current runs with a shared `Repeat Interval` and disjoint `Target Start` / `Reference Start` schedule. Queries select the exact modulo schedules, TX Success admits the Target schedule, and Compare forms one-to-one receiver-specific scheduled pairs with per-side micro-medians; the TX hardware demo and standalone timed USB-relay utility use the same schedule vocabulary and cadence model.
- Added segment-level and selected-station Compare temporal evidence with chronological and 24-hour UTC-hour views. The views use the same qualifying joint spots or scheduled pairs as their distributions, expose selectable chronological bins, scale heatmaps by per-panel relative density, use median-centered nonlinear Delta SNR axes without changing the underlying statistics, and are retained in prepared exports and saved view state where applicable.
- Rebuilt the English and German operator manuals around progressive disclosure, practical experiment design, evidence interpretation and scientifically bounded claim language. The revision expands WSPR and prior-art context, sequential TX guidance, Target-Active Gate explanation and reproducibility guidance; standardizes compact source citations; aligns both languages; regenerates the README; and fixes nested PDF lists plus internal destinations so navigation remains usable.

## 2026-07-12

- Made the idle landing path import-light: page configuration, the header and controls now render before analysis-only dependencies; result/artifact reset state moved into a lightweight lifecycle module; callsign, locator and time validation no longer load NumPy-backed geometry; and Pandas, Matplotlib, Requests, Cartopy, plotting, export and inspector code load only after a TX/RX run becomes active. Replaced the automatic delayed full-manual render with an on-demand documentation fragment that initially sends only Section 1, loads the table of contents and remaining chapters once when Section 1.3 enters the viewport, provides race-safe localized Load/Hide fallbacks, suppresses scroll loading during analysis, and preserves independently lazy PDF preparation.
- Renamed the prepared analysis export package's Success result folder and metadata identifiers from the superseded `absolute` terminology to `success`; the offline fixture builder still accepts archived `absolute/` exports.
- Replaced hidden prefix callsign matching in compare-mode target/reference filters with one exact callsign per comparison side. Base callsigns and suffix/postfix forms such as `/P`, `/1` or `/QRP` are now separate exact run inputs rather than automatic wildcard matches; Buddy, RX A/B and local-neighborhood matching use `=` / `!=` predicates, the manuals surface the behavior, and the special-callsign `Q`, `0` and `1` prefix exclusion remains a separate advanced filter.
- Avoided the Arrow CSV parser on the standard wspr.live CSV fetch path after Streamlit Community Cloud showed a native `pyarrow._csv` segmentation fault during RX analysis startup. Standard CSV responses now use Pandas' C parser, while the existing Parquet artifact path remains unchanged; regression coverage guards the parser selection.
- Added `No benchmark (Success only)` as the first and default Benchmark Design. It builds only the requested TX or RX Success analysis, hides reference and joint-evidence inputs, and leaves Hardware A/B, Buddy and Local Neighborhood as explicit comparison designs that still produce Compare plus Success results. Every normal benchmark-design selection now resets Reference SNR Correction to its documented `0.0 dB` default before an explicit demo profile can override it. Renamed the compare categorical panel from `System Sensitivity (Yield)` to `Decode Outcomes` without changing its evidence classifications.
- Removed `Band = All`, rejected legacy all-band configs with a clear migration error, centralized `20m` as the consistent default, and exposed the exact `LF`, `MF`, `22m`, `8m` and `4m` buckets present in the live wspr.live `bands` table. Every analysis now requires one explicit band so opportunities and comparison evidence cannot be pooled across incompatible band conditions.
- Replaced the English and German manuals with the reviewed operator-first structure and regenerated `README.md` from the authoritative English source. The manuals now progress from WSPR and WSPRadar fundamentals through experiment choice, result interpretation, controls, troubleshooting, scientific methods and valid claim language; explain every Segment Insight, Station Insights, selected-evidence and Drill-Down view; document sequential TX A/B design, source-validated WSPR sensitivity and fresh-spot delay guidance; and retain operational procedures, literature, exact aggregation rules and export limitations in layered sections and appendices. PDF conversion now preserves the manuals' formulas, code blocks and numbered procedures, and descriptive tables keep wrapped cell text left-aligned.
- Made map footer summaries consistent across analyses: Local Neighborhood Compare maps now retain the `SPOTS` row alongside `STATIONS`, and Success maps add denominator-aligned `SPOTS` and `STATIONS` rows for Target versus Elsewhere/Other Signals evidence and qualifying Target versus counter-evidence-only station identities. Counts follow the visible map scope and exclude ineligible and Target-only evidence.
- Removed the heuristic `Very low`/`Low`/`Medium`/`Strong` grading from Compare Segment Insight. `Selected Segment Evidence` now reports only the factual number of joint stations and total joint spots, or paired spot bins for sequential TX A/B, leaving evidence-strength interpretation to the operator.
- Established the operator-first, progressively layered English-manual style as a contributor standard in `AGENTS.md`, and refined the Hardware A/B guide to explain why controlled local TX comparisons use sequential adjacent WSPR frames, how repeated balanced alternation reduces temporal confounding, and why it cannot guarantee exact cancellation of propagation or interference changes.
- Fixed the first analysis after a cold deployment repeatedly re-entering same-session admission and showing the identical-analysis message. Runtime source directories are now regular Python packages, preventing Streamlit's namespace-package directory watcher from treating first-import `__pycache__` writes as source changes; regression coverage protects the package/watch-path contract without changing scientific behavior or admission policy.
## 2026-07-11

- Multi-user artifact lifecycle: Added the shared `ArtifactStore` with separate query, derived-analysis and session-artifact namespaces; validated namespace-contained paths; fixed-size lock striping plus per-key cross-process lock files; unique sibling temporary paths with atomic replacement; stale-lock cleanup; coordinated Parquet reads/writes; and last-access touching, active leases, retirement and TTL-aware cleanup for session artifacts.
- Concurrent map and rendering safety: Made static basemap construction single-flight and atomic so simultaneous users cannot build or publish the same missing basemap concurrently, moved basemaps into the derived-analysis namespace, retained compact RGB cache pixels, and added a process-wide Matplotlib rendering lock with wait/held-time profiling and explicit figure disposal.
- Core/UI contract completion: Introduced structured `FetchResult`/`FetchError`/`FetchSource`, pure `MapData`, presentation-only `MapFigure`, and explicit `PresentationContext` contracts; separated scientific configuration from language, labels and theme; moved map aggregation behind a pure data boundary; and removed Streamlit error/session rendering from the core fetch path so localized presentation state cannot influence scientific branches or cache keys.
- Opportunity-processing memory reduction: Defined and enforced an explicit processed opportunity-row schema; removed stored `cycle_time` and centralized exact UTC reconstruction from `time_slot * 120`; made row preparation ownership-aware; avoided the full coordinate merge; stored repeated callsigns, locators, outcomes and path-illumination labels categorically; used `observed=True` for categorical grouping; and let solar-path enrichment mutate an owned frame without another full copy while preserving coordinate, SNR and solar-calculation precision.
- Projected artifact reads: Limited opportunity Segment view reads to `time_slot`, peer identity and hit/miss evidence; limited selected-station and drill-down reads to their required evidence columns; and limited map reconstruction reads to map-required columns, reducing transient DataFrame amplification without changing classifications, aggregates, tables or numerical results.
- Inspector view-model and preview caching: Added pure comparison/opportunity inspector view models and a bounded per-session LRU cache for options, segment models, selected-station models, figure recipes and preview PNG bytes. Inspector interactions now reuse compact prepared data instead of rebuilding figures and rereading broad evidence tables, while session artifact touching/lease revival keeps an active analysis inspectable across reruns and TTL cleanup.
- Analysis admission control: Added a configurable process-wide FIFO gate with two active analyses, up to ten queued requests, queue position/status reporting, bounded waiting, stale active-lease recovery and unconditional permit release. Added stable session ownership and scientific request fingerprints so an identical active/queued request from the same session is rejected without preventing different users from independently running the same demo.
- Export admission control: Serialized prepared-results ZIP construction to one active export with up to ten queued exports, user-visible queue position and capacity messages, bounded waiting, stale-lease recovery, unconditional release and export duration/RSS/ZIP-size telemetry. Export contents and the existing in-memory ZIP workflow remain otherwise unchanged.
- Upstream HTTP resilience and security: Added 10-second connect and 60-second socket-read timeouts, streamed CSV and Parquet downloads, 64 MiB decompressed response ceilings, bounded HTTP error-body capture, atomic cache publication and structured timeout/oversize/request errors with clear retry guidance. Same-query cache misses are coordinated under per-key locks so concurrent requests do not duplicate upstream work.
- Operational profiling: Extended terminal `PERF` output with DataFrame deep-memory snapshots, current and peak process RSS, analysis/export admission outcomes, queue positions and wait times, artifact/Matplotlib lock contention, inspector cache hits/misses, entry counts and retained bytes. This exposes NumPy/Matplotlib/Pillow and concurrency costs that Python allocation tracing alone misses.
- Documentation startup behavior: Changed documentation PDF generation to explicit on-demand preparation with process caching and serialized cache misses, then moved the complete web documentation into a parallel fragment with a configurable one-time 0.75-second session delay. Added automatic full-document loading, language-staleness protection and CSS `content-visibility: auto`/intrinsic sizing so the operational interface can paint before the long scientific manual is transmitted and laid out; raised the Streamlit minimum to 1.58 for parallel-fragment support.
- Regression coverage: Added focused concurrency, lifecycle, ownership, projection, categorical round-trip, UTC-equivalence, scientific-classification, map-figure, core/UI-boundary, HTTP-limit, admission/deduplication, inspector-cache, PDF-laziness, delayed-documentation and RSS/profiling tests. The expanded suite protects the scientific outputs while exercising race conditions, cleanup behavior and multi-user resource controls.

## 2026-07-05

- Refactor: Split the large Segment Inspector implementation into focused modules for evidence data extraction (`ui/inspector/evidence_data.py`), drill-down table construction (`ui/inspector/drilldown.py`), comparison evidence figures (`ui/plots/evidence_figures.py`) and opportunity figures (`ui/plots/opportunity_figures.py`), leaving `ui/components/segment_inspector.py` focused on Streamlit selection state, layout orchestration and export registration.
- Refactor: Moved shared statistical helpers into `core/stability.py`, including the bootstrap median stability interval and metric-axis limit helpers, so the scientific calculation path is reusable and regression-testable outside the Streamlit component.
- Refactor: Introduced canonical `AnalysisContext` handling and `ui/analysis_context_adapter.py`, reducing direct `st.session_state` access in core analysis logic and preventing localized UI labels from driving scientific branch decisions.
- Refactor: Split configuration from the former monolithic `config.py` into a package with app/cache settings, demo profiles, plot constants and band definitions (`config/app_config.py`, `config/demo_profiles.py`, `config/plot_constants.py`, `config/bands.py`), reducing the import-time blast radius of demo-profile edits.
- Refactor: Moved run orchestration into `ui/run_controller.py`, making `app.py` more focused on page composition while preserving the existing Streamlit run workflow, status messages, deferred Segment Inspector rendering and export registration behavior.
- Refactor: Split comparison SQL construction, opportunity query construction, post-fetch filtering and run orchestration boundaries more clearly, enabling targeted regression tests for config migration, TX/RX A/B WSPR-frame SQL, reference-SNR correction sign, exact callsign matching and decode-filter fallback behavior.
- Refactor: Removed the export layer's dependency on Segment Inspector internals by moving shared evidence, drill-down and figure builders into stable `ui/inspector/*` and `ui/plots/*` modules used by both live UI rendering and prepared-results export.
- Added regression coverage for the refactored contracts, including config package/import behavior, legacy config migration, analysis-runner SQL contracts, stability helper equivalence, opportunity-query behavior, path-illumination classification and sun-vector solar-elevation equivalence.
- Added nested terminal performance profiling via `core/performance_timer.py`, covering fetch, post-filtering, geometry bucketing, aggregation, basemap construction/cache behavior, wedge/scatter rendering, Matplotlib draw/serialization/display, first Segment Inspector render, stability calculation, evidence figure rendering and drill-down table rendering.
- Removed the in-page `Performance profile` expander/table from the results view while keeping the nested terminal `PERF ...` reports for development profiling.
- Improved live Matplotlib rendering by replacing `st.pyplot(fig)` with preview PNG rendering through `st.image`, using a lower default preview DPI and low PNG compression for web display while preserving full-resolution figure generation for prepared exports.
- Added detailed preview-render timing for Matplotlib canvas draw, PNG serialization, Streamlit image display, encoded byte size, pixel dimensions, DPI and PNG compression level, making rendering bottlenecks visible in terminal logs.
- Added a persistent static basemap preview cache under `.wspr_cache/basemaps`, keyed by map theme, QTH/center, radius, preview dimensions, DPI and map-style version, so repeated runs can reuse the expensive Cartopy basemap raster while still drawing dynamic wedges, station markers, titles, legends and footers per analysis.
- Vectorized the bootstrap median stability calculation with chunked NumPy resampling while preserving the existing deterministic seed/interval contract, reducing the first Segment Insight stability calculation from tens of seconds to roughly one to two seconds in the profiled RX Calibration A/B demo.
- Optimized Absolute path-illumination post-filtering by deduplicating repeated `(cycle_time, peer_lat, peer_lon)` keys, precomputing UTC-only solar terms once per unique cycle and using sun-vector dot products for great-circle sample solar elevation, reducing the profiled path-illumination sample loop from about 10.4 seconds to about 2.6 seconds on the RX Success demo.
- Added instrumentation and regression guards around the path-illumination optimization, including duplicate-row preservation, precomputed solar-term equivalence and sun-vector elevation agreement across equinox/solstice, high-latitude and date-line cases.
- Clarified cache behavior during profiling: `query_*.parquet` files are reusable exact-SQL disk query caches, while `spots_*.parquet` files are per-run Segment Inspector/export artifacts that remain subject to TTL cleanup and must not be aggressively deleted in a multi-user Streamlit deployment.
- Preserved the live dark-theme visual model while moving web-preview rendering to the faster preview path; prepared-results export remains the high-resolution/paper-oriented output path.

## 2026-06-21

- Added observation-level great-circle path illumination classification for Absolute evidence, with configurable daylight-fraction threshold and selected-station plots split into night, greyline/mixed and daylight Target/counter-evidence contributions.
- Refactor: Extracted compare-mode map aggregation into `core/compare_engine.py` and added focused regression coverage for simultaneous and sequential compare aggregation.
- Refactor: Extracted shared Cartopy map scaffolding into `core/map_base.py`, keeping mode-specific overlays, legends, colorbars and footer metrics in the plot engine.- Split visible Absolute terminology by mode: RX now uses Target/Elsewhere (`T/E`) and TX uses Target/Other Signals (`T/OS`), while the internal audit data can still retain lower-level cycle classification.
- Updated Absolute map titles to `RX Success: Target {callsign} vs. Same Signals Heard Elsewhere` and `TX Success: Target {callsign} vs. Other Signals at Same RX Stations`.
- Compact Absolute Station Insights labels to mode-specific `Target (T)`, `Elsewhere (E)` / `Other Signals (OS)` and `T/(T+E)` / `T/(T+OS)`.
- Changed selected-station evidence count axes to plus-count wording such as `Target + Elsewhere count` and `Target + Other Signals count`, avoiding slash notation for count bars.

## 2026-06-20

- Consolidated the Absolute success-rate visual model around station-level and observation-level Target/counter-evidence rates instead of raw Absolute SNR maps.
- Changed Absolute map segments to average station Success Rate and introduced the shared nonlinear `0%`, `>0%`, `1%`, `2%`, `5%`, `10%`, `20%`, `40%`, `60%`, `80%`, `100%` color scale for maps and temporal panels.
- Rebuilt Absolute Segment Insight around three core views: station Success Rate by evidence count, Average Station Success Rate over time and Observation-Level Success Rate over time.
- Anchored Absolute temporal bins to the selected analysis start/end window, kept empty intervals visible and aligned selected-station evidence time plots to the same fixed bin-index time scale.
- Simplified Absolute Station Insights and drill-down views by focusing on threshold-qualified Target/counter-evidence rows, hiding zero-Target stations by default, removing redundant Opportunity/Target-only columns from the table and preserving row-level outcome classification in drill-down data.
- Updated selected-station Absolute evidence to show stacked Target/counter-evidence counts with a dynamically scaled Success Rate line, integer-only count ticks and Target SNR evidence.
- Improved Absolute figure readability by enlarging typography, replacing long range-bin labels with distance-boundary labels, increasing time-axis label density and sharing one colorbar across paired temporal heatmaps.
- Added explicit no-data/zero/nonzero color semantics and map markers for Target evidence tiers plus counter-evidence-only stations.

## 2026-06-14
- Improved Segment Inspector performance by loading selected-station Parquet rows once and reusing them for evidence figures and drill-down tables.
- Added a small bounded cache for bootstrap stability results, preventing recalculation when selecting different stations within the same segment scope.
- Deferred all 300 DPI figure generation and full-segment drill-down preparation until Prepare All Results is explicitly requested.
- Replaced raw-SNR Absolute TX/RX analysis with conditional opportunity analysis: RX Confirmed-Reception Rate and TX Conditional Network Decode Rate.
- Added exact target-active 2-minute cycle classification into confirmed opportunities (`O`), hits (`H`), misses (`M`) and target-only evidence (`T`), with `T` excluded from the rate denominator.
- Added station-balanced map segments based on median eligible peer `H/O` rates, a configurable minimum-opportunity threshold, pooled-rate diagnostics and explicit low-evidence/target-only map markers.
- Rebuilt Absolute Segment Insight, Station Insights and drill-down views around opportunity outcomes, peer rates, rate/evidence time views and successful SNR as supporting evidence.
- Added a compact single-band ClickHouse query that returns station-cycle flags as Parquet, plus exact-query disk caching to reduce repeated database load and shared Streamlit RAM use.
- Extended configuration/export metadata and English/German documentation for the new Absolute method, its assumptions, query behavior and limitations; bumped WSPRadar to v0.94.
- Simplified Absolute evidence figures by removing redundant outcome-count charts, enlarging the remaining panels, dynamically scaling confirmation-rate axes and synchronizing the rate-over-time heatmap with the map color scale.
- Added dynamic Absolute map color limits for low-rate datasets and changed Absolute Station Insights to sort primarily by descending Hits (`H`).
- Replaced the Segment Inspector’s single range and direction selectors with multiselect controls.

## 2026-05-30
- Replaced raincloud plots with histograms to reflect integer distributions better.

## 2026-05-16

- Added a richer demo-profile model with ordered UI sections, per-demo advanced settings, default evidence-view settings and publication-oriented demo profiles.
- Added reproducibility and regression-test support: prepared exports now include the compact parquet analysis cache, and the test tooling can build regression fixtures from downloaded demo/result packages. Regression compare key scientific outputs such as station counts, joint/evidence counts, medians, means and segment medians.
- Updated documentation and README structure around map reading, Segment Insight, Station Insights, Drill-Down, export/download packages, configuration workflows and 90 percent stability interpretation.
- Renamed sequential TX A/B frame assignment from odd/even-minute wording to explicit UTC WSPR-frame start-minute wording, including config-schema compatibility for older `target_time_slot` / `reference_time_slot` files.

## 2026-05-15

- Added Git workflow helper scripts and accompanying workflow documentation for baselining temp, pushing temp and releasing main.
- Added prepared-results export support, including high-resolution figures, station-insight tables, drill-down tables, config metadata and export packaging.
- Added light/paper-oriented export rendering for figures and maps.

## 2026-05-14
- Replaced selected-station time scatter plots with time-bin heatmaps.
- Updated demo-loading and SNR-correction documentation.
- Limited raincloud distribution display ranges using an IQR-based outlier rule, with outlier percentages shown in the plot.
- Added 90 percent stability intervals to Segment Insight and Station Insights evidence.
- Added save/load configuration support, including config serialization, UI integration and state handling.

## 2026-05-10

- Added the joint-spot Delta SNR evidence figure to the Segment Insight figure block.
- Changed simultaneous TX/RX compare grouping from `time_slot + peer_sign` to `time_slot + peer_sign + peer_grid`, preventing one bad locator for a callsign from being duplicated across the entire station identity.
- Added SNR correction/offset support for compare modes.

## 2026-05-09

- Added selected-station evidence plots below Station Insights, including distribution and time-evidence views.
- Added time aggregation controls for selected-station evidence.
- Preserved callsign plus locator identity in drill-down selection, preventing rare bad-grid rows from contaminating the normal station/grid row.
- Added a dynamic demo launcher and expanded demo profile support, including TX buddy-test demo configuration.

## 2026-04-26

- Added experimental local-neighborhood benchmark modes.
- Introduced Local Median Neighborhood and Local Best Station concepts, with Local Median Neighborhood becoming the preferred/default benchmark concept in the documentation flow.
- Expanded local-median drill-down details so reference pools can be reconciled at the individual station level rather than appearing only as an opaque reference pool.
- Tuned local-neighborhood labels, segment labels and chart labels for clearer interpretation.
- Reworked advanced configuration for exclusion filters, including special callsign prefix filtering and moving-station filtering.

## 2026-04-13

- Added vector-based time-binning for sequential TX A/B tests, creating paired samples to reduce macro-fading and QSB confounding.
- Fixed missing async/joint categories in map and segment-inspector yield charts.
- Standardized the default non-joint visibility behavior so compare-mode views start focused on joint evidence.
- Updated configuration, math helpers, plotting, documentation, i18n and state handling for the sequential pairing model.

## 2026-04-10
- Added dynamic table filtering and responsive UI refinements for result inspection.
- Continued synchronization and offline-cycle handling improvements.
- Fixed sequential TX A/B yield logic so asynchronous overlap is counted correctly instead of always showing zero.
- Renamed sequential-mode table terminology toward asynchronous/bin evidence where appropriate.
- Updated documentation table-of-contents structure.

## 2026-04-07

- Expanded vectorized cycle synchronization to both TX and RX comparative analyses.
- Introduced target-active cycle logic: TX comparisons require the target setup to be demonstrably transmitting, and RX comparisons require the target setup to be demonstrably receiving before reference evidence is counted.
- Reduced offline-cycle bias in compare-mode yield calculations.

## 2026-04-06

- Introduced the bivariate evaluation model for distinguishing joint detections from target-only, reference-only and asynchronous evidence.
- Added structured demo profiles so different comparison modes can load context-aware demo data.
- Modularized the app into clearer components: core analysis logic, plotting, callbacks, state management, UI panels and segment inspection.
- Added vectorized execution and stricter filtering in the analysis path.
- Added input hardening and SQL-injection defenses around user-provided configuration values.
- Updated the README and user documentation to reflect the evolving comparison workflow.

## 2026-04-05

- Reworked the hardware A/B testing architecture and updated related configuration, plotting and documentation.
- Continued refining the analysis model for comparing station or antenna setups rather than only rendering absolute WSPR maps.

## 2026-04-04

- Published the initial WSPRadar application structure, including the Streamlit app, core data/query utilities, map plotting, documentation, images, package metadata and licensing.
- Added the first public user documentation in English and German, plus PDF-generation support.
- Added the project website/static entry files and app configuration for deployment.
- Began decoupling demo configuration and reducing memory pressure in the main app.
