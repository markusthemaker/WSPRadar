# WSPRadar Daily Changelog

This changelog summarizes major project changes by UTC day. It is intentionally grouped by day rather than by version because early version labels were not yet stable.

Source used for this file: reachable `origin/main` history available locally at generation time, ending at commit `96d978d` (`TX A/B Test Callsign fix`, 2026-05-15 19:02:37 UTC). If temporary branches were force-pushed, intermediate temp-only commits are not listed separately; their effects are captured when they became reachable from `main`.

## 2026-04-04

- Published the initial WSPRadar application structure, including the Streamlit app, core data/query utilities, map plotting, documentation, images, package metadata and licensing.
- Added the first public user documentation in English and German, plus PDF-generation support.
- Added the project website/static entry files and app configuration for deployment.
- Began decoupling demo configuration and reducing memory pressure in the main app.

## 2026-04-05

- Reworked the hardware A/B testing architecture and updated related configuration, plotting and documentation.
- Continued refining the analysis model for comparing station or antenna setups rather than only rendering absolute WSPR maps.

## 2026-04-06

- Introduced the bivariate evaluation model for distinguishing joint detections from target-only, reference-only and asynchronous evidence.
- Added structured demo profiles so different comparison modes can load context-aware demo data.
- Modularized the app into clearer components: core analysis logic, plotting, callbacks, state management, UI panels and segment inspection.
- Added vectorized execution and stricter filtering in the analysis path.
- Added input hardening and SQL-injection defenses around user-provided configuration values.
- Updated the README and user documentation to reflect the evolving comparison workflow.

## 2026-04-07

- Expanded vectorized cycle synchronization to both TX and RX comparative analyses.
- Introduced target-active cycle logic: TX comparisons require the target setup to be demonstrably transmitting, and RX comparisons require the target setup to be demonstrably receiving before reference evidence is counted.
- Reduced offline-cycle bias in compare-mode yield calculations.

## 2026-04-10
- Added dynamic table filtering and responsive UI refinements for result inspection.
- Continued synchronization and offline-cycle handling improvements.
- Fixed sequential TX A/B yield logic so asynchronous overlap is counted correctly instead of always showing zero.
- Renamed sequential-mode table terminology toward asynchronous/bin evidence where appropriate.
- Updated documentation table-of-contents structure.

## 2026-04-13

- Added vector-based time-binning for sequential TX A/B tests, creating paired samples to reduce macro-fading and QSB confounding.
- Fixed missing async/joint categories in map and segment-inspector yield charts.
- Standardized the default non-joint visibility behavior so compare-mode views start focused on joint evidence.
- Updated configuration, math helpers, plotting, documentation, i18n and state handling for the sequential pairing model.

## 2026-04-26

- Added experimental local-neighborhood benchmark modes.
- Introduced Local Median Neighborhood and Local Best Station concepts, with Local Median Neighborhood becoming the preferred/default benchmark concept in the documentation flow.
- Expanded local-median drill-down details so reference pools can be reconciled at the individual station level rather than appearing only as an opaque reference pool.
- Tuned local-neighborhood labels, segment labels and chart labels for clearer interpretation.
- Reworked advanced configuration for exclusion filters, including special callsign prefix filtering and moving-station filtering.

## 2026-05-09

- Added selected-station evidence plots below Station Insights, including distribution and time-evidence views.
- Added time aggregation controls for selected-station evidence.
- Preserved callsign plus locator identity in drill-down selection, preventing rare bad-grid rows from contaminating the normal station/grid row.
- Added a dynamic demo launcher and expanded demo profile support, including TX buddy-test demo configuration.

## 2026-05-10

- Added the joint-spot Delta SNR evidence figure to the Segment Insight figure block.
- Changed simultaneous TX/RX compare grouping from `time_slot + peer_sign` to `time_slot + peer_sign + peer_grid`, preventing one bad locator for a callsign from being duplicated across the entire station identity.
- Added SNR correction/offset support for compare modes.

## 2026-05-14
- Replaced selected-station time scatter plots with time-bin heatmaps.
- Updated demo-loading and SNR-correction documentation.
- Limited raincloud distribution display ranges using an IQR-based outlier rule, with outlier percentages shown in the plot.
- Added 90 percent stability intervals to Segment Insight and Station Insights evidence.
- Added save/load configuration support, including config serialization, UI integration and state handling.

## 2026-05-15

- Added Git workflow helper scripts and accompanying workflow documentation for baselining temp, pushing temp and releasing main.
- Added prepared-results export support, including high-resolution figures, station-insight tables, drill-down tables, config metadata and export packaging.
- Added light/paper-oriented export rendering for figures and maps.

## 2026-05-16

- Added a richer demo-profile model with ordered UI sections, per-demo advanced settings, default evidence-view settings and publication-oriented demo profiles.
- Added reproducibility and regression-test support: prepared exports now include the compact parquet analysis cache, and the test tooling can build regression fixtures from downloaded demo/result packages. Regression compare key scientific outputs such as station counts, joint/evidence counts, medians, means and segment medians.
- Updated documentation and README structure around map reading, Segment Insight, Station Insights, Drill-Down, export/download packages, configuration workflows and 90 percent stability interpretation.
- Renamed sequential TX A/B frame assignment from odd/even-minute wording to explicit UTC WSPR-frame start-minute wording, including config-schema compatibility for older `target_time_slot` / `reference_time_slot` files.

## 2026-05-30
- Replaced raincloud plots with histograms to reflect integer distributions better.

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

## 2026-06-20

- Consolidated the Absolute success-rate visual model around station-level and observation-level Target/counter-evidence rates instead of raw Absolute SNR maps.
- Changed Absolute map segments to average station Success Rate and introduced the shared nonlinear `0%`, `>0%`, `1%`, `2%`, `5%`, `10%`, `20%`, `40%`, `60%`, `80%`, `100%` color scale for maps and temporal panels.
- Rebuilt Absolute Segment Insight around three core views: station Success Rate by evidence count, Average Station Success Rate over time and Observation-Level Success Rate over time.
- Anchored Absolute temporal bins to the selected analysis start/end window, kept empty intervals visible and aligned selected-station evidence time plots to the same fixed bin-index time scale.
- Simplified Absolute Station Insights and drill-down views by focusing on threshold-qualified Target/counter-evidence rows, hiding zero-Target stations by default, removing redundant Opportunity/Target-only columns from the table and preserving row-level outcome classification in drill-down data.
- Updated selected-station Absolute evidence to show stacked Target/counter-evidence counts with a dynamically scaled Success Rate line, integer-only count ticks and Target SNR evidence.
- Improved Absolute figure readability by enlarging typography, replacing long range-bin labels with distance-boundary labels, increasing time-axis label density and sharing one colorbar across paired temporal heatmaps.
- Added explicit no-data/zero/nonzero color semantics and map markers for Target evidence tiers plus counter-evidence-only stations.

## 2026-06-21

- Added observation-level great-circle path illumination classification for Absolute evidence, with configurable daylight-fraction threshold and selected-station plots split into night, greyline/mixed and daylight Target/counter-evidence contributions.
- Refactor: Extracted compare-mode map aggregation into `core/compare_engine.py` and added focused regression coverage for simultaneous and sequential compare aggregation.
- Refactor: Extracted shared Cartopy map scaffolding into `core/map_base.py`, keeping mode-specific overlays, legends, colorbars and footer metrics in the plot engine.- Split visible Absolute terminology by mode: RX now uses Target/Elsewhere (`T/E`) and TX uses Target/Other Signals (`T/OS`), while the internal audit data can still retain lower-level cycle classification.
- Updated Absolute map titles to `RX Success: Target {callsign} vs. Same Signals Heard Elsewhere` and `TX Success: Target {callsign} vs. Other Signals at Same RX Stations`.
- Compact Absolute Station Insights labels to mode-specific `Target (T)`, `Elsewhere (E)` / `Other Signals (OS)` and `T/(T+E)` / `T/(T+OS)`.
- Changed selected-station evidence count axes to plus-count wording such as `Target + Elsewhere count` and `Target + Other Signals count`, avoiding slash notation for count bars.
