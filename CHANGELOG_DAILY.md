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
- Replace raincloud with histogram to reflect integer distribution better 

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

## 2026-06-15

- Simplified the visible Absolute-analysis vocabulary to `H (Hit)`, `M (Miss)` and `Success Rate = H/(H+M)` while retaining `O` and `T` in the internal audit data.
- Changed Absolute map segments from median peer rates to average station Success Rate and introduced a fixed nonlinear `0, 1, 2, 5, 10, 20, 40, 60, 80, 100%` scale shared by maps and temporal panels.
- Replaced Absolute map markers with threshold-qualified H/M stations: Hits use rate-dependent green intensity, while stations with confirmed Misses and no Hits use light gray.
- Rebuilt Absolute Segment Insight around a station Success Rate versus confirmed-evidence scatter plot, Average Station Success Rate over time and Overall Success Rate over time.
- Anchored contiguous Absolute time bins to the exact analysis start/end window so empty intervals remain visible and time axes are chronologically stable.
- Reduced Absolute Segment Insight summaries and Station Insights tables to threshold-qualified H/M evidence, removed redundant Opportunity/Target-only/eligibility columns and sorted stations by Hits, Misses and Success Rate.
- Updated selected-station Absolute evidence to show stacked H/M counts with a dynamically scaled Success Rate line, and updated English/German UI text and documentation.
- Added a default-off `Show Zero-Hits` control for Absolute Station Insights without removing zero-Hit stations from any calculated rate or full-segment evidence.
- Simplified the station evidence scatter to stations with Hits, formatted its log2 axis with actual evidence counts, renamed the pooled temporal metric to Observation-Level Success Rate and enlarged Absolute figure typography.
- Replaced temporal range-bin strings with distance-boundary labels and increased time-axis label density across Absolute temporal charts.
- Anchored Absolute temporal labels to a regular clock-stable interval from the selected analysis start, moved both temporal panels closer together and replaced their duplicate colorbars with one shared Success Rate scale.
- Renamed the Absolute station-evidence scatter to `Station Success Rate by Evidence Count`, simplified its axes and shortened the table Success Rate header to `H/(H+M) (%)`.
- Removed redundant `Opportunity (O)` and `Target-Only (T)` columns from the Absolute drill-down table while keeping the row-level `Outcome` classification.
- Reordered selected-station H/M stacks so Hits are drawn from the baseline and Misses stack above them, matching the visual fraction implied by `H/(H+M)`.
- Forced the selected-station H/M count axis to integer-only labels.
- Aligned selected-station H/M time plots with the same fixed bin-index time scale and clock-stable tick scheduler used by the Absolute segment temporal heatmaps.
- Split the Absolute Success Rate color scale into `0%`, `>0%`, `1%`, `2%`, `5%`, ... bins and added a black-outlined `No H/M evidence` swatch to the Absolute map legend.
- Made the Absolute map `No H/M evidence` legend swatch follow the render theme and changed Hit markers to evidence tiers `H = 1`, `H = 2-5`, and `H > 5`.

- Renamed the visible Absolute Success Rate evidence vocabulary from H/M to Target/Elsewhere: Segment Insight now spells out Target+Elsewhere evidence and Success Rate Target/(Target+Elsewhere), while maps, tables, selected-station evidence and documentation use T/E labels consistently.
- Split Absolute Success Rate terminology by mode: RX now uses Target/Elsewhere (T/E) with Same Signals Heard Elsewhere titles, while TX uses Target/Other Signals (T/OS) with Other Signals at Same RX Stations titles.
- Compact Absolute Station Insights labels to mode-specific `Target (T)`, `Elsewhere (E)` / `Other Signals (OS)` and `T/(T+E)` / `T/(T+OS)`, moved Absolute map legends below the long titles and changed selected-station evidence count axes to plus-count wording.
