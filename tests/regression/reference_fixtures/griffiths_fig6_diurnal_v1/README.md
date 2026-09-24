# G3ZIL / G4HZX Figure 6 diurnal reference

This fixture independently reconstructs a frozen archive population behind the Griffiths and Squibb Figure 6 demo. It protects the same-cycle Delta SNR calculation, geographic selection, chronological bins and pooled UTC-hour summaries. Exact expectations come from the original endpoint reports using a separate standard-library calculation, with no WSPRadar imports. The paper supplies external qualitative corroboration; it is not the source of these exact numeric expectations.

## Fixed configuration

- Target: G3ZIL, IO90HW; Reference: G4HZX, IO91; RX Benchmark, 40 m.
- Selected UTC interval: **2017-04-05 00:00 inclusive to 2017-04-07 23:45 exclusive**.
- Scope: Full Range | All Directions, within a strict 10,000 km Target-centered radius.
- Solar selection: all; special-callsign and moving-station exclusions off; minimum one Joint Spot per peer identity; no SNR correction.
- Evidence identity: transmitter callsign plus full reported locator, within one 120-second cycle.
- Historical source mode: `legacy_no_code`. All 18,791 captured reports have `code=0`; this observation does not independently establish their physical decode mode.
- Frozen source: public wspr.live query captured on 2026-09-23. The original capture records the then-current dirty working tree and provider provenance.

The additional 22,000 km case changes only `max_peer_distance_km`. It uses exactly the same frozen SQL-result input, time window, endpoint identities and remaining scientific settings. It tests whether the production radius setting genuinely determines the retained evidence population.

## Numerical anchors

| Quantity | 10,000 km demo | 22,000 km counterfactual |
| --- | ---: | ---: |
| Captured SQL-result rows | 12,290 | 12,290 |
| Retained post-fetch rows | 12,148 | 12,185 |
| Station identities before paired-only selection | 279 | 287 |
| Joint Spots | 6,459 | 6,474 |
| Only Target | 4,090 | 4,111 |
| Only Reference | 1,599 | 1,600 |
| Paired transmitter identities | 200 | 203 |
| Full-window pooled median | +5 dB | +5 dB |
| Full-window pooled mean | +5.116581514166279 dB | +5.116156935434044 dB |
| Full-window pooled Q1 / Q3 | +1 / +9 dB | +1 / +9 dB |

The full-window median alone cannot distinguish the two geographic populations. Tests should assert identities, per-bin counts and complete numeric profiles as well as the global summaries.

Folded UTC-hour medians for hours 00 through 23 at 10,000 km, in dB:

`0, -2, -3, -2, -1, 2, 3, 5, 5, 6, 6, 6, 6, 8, 6, 6, 6, 6, 6, 5, 6, 4, 3, 1`

The negative medians at 01-04 UTC corroborate the reported reversal. The medians become positive at 05 UTC, initially +2 and +3 dB at 05 and 06 UTC; the +5 to +8 dB daytime range starts around 07 UTC. Most nighttime IQRs overlap zero. These summaries are descriptive paired evidence, not a universal per-path advantage, a significance test or an independent causal attribution.

Pooling the native paired observations in the daily clock-time interval **[05:00, 21:30) UTC**, across all three dates, gives **5,568 observations**, mean **+5.765086206896552 dB** and median **+6 dB**. The upper clock-time boundary is exclusive: including the 21:30 cycle would instead select 5,572 observations. This practical daytime anchor is distinct from averaging the hourly medians or giving every day equal weight.

## Independent derivation

1. Read `source_rows.parquet`, preserving every raw report, its reported power, full locator, coordinates, callsign and timestamp. Apply the captured band, half-open time window, exact receiver callsigns and grid-4 endpoint matches. Exclude transmitter latitude zero, matching the declared source selection. No decode-code predicate is applied to this historical compatibility case.
2. Group by `floor(UTC epoch seconds / 120)`, transmitter callsign and full transmitter locator. Keep separate raw-report counts for each receiver. Normalize each report as `snr - power + 30` and take the maximum separately for each receiver within that group. There are 20 endpoint groups with duplicate reports; duplicates do not become extra paired temporal units.
3. Determine the set of Target-active cycles globally, before geographic filtering. Keep a Reference-only group only if the Target has evidence somewhere in that cycle.
4. Independently decode the Target locator to its cell center, latitude 50.9375 degrees and longitude -1.375 degrees. Apply a standard-library spherical haversine distance using Earth radius 6,371 km and strict distance less than the selected radius. Every source group has one unambiguous transmitter coordinate pair. The closest considered group to the 10,000 km boundary is more than 1,543 km away, so minor geodesic numerical differences cannot change this case's classification.
5. For each retained group with both receivers, subtract the Reference maximum normalized SNR from the Target maximum normalized SNR. Sort the expected paired table by cycle, callsign and locator. Unpaired groups contribute to outcome counts, not the Delta SNR population.
6. Compute chronological bins from the selected start, preserving the exact exclusive end. Compute folded bins by UTC hour directly from individual paired observations across the represented dates. Each paired observation has one contribution; neither transmitters nor dates receive equalized weight.
7. Use sorted standard-library arithmetic for statistics. An even-sample median averages its two central values. Quartiles linearly interpolate the sorted sample at index `(n - 1) * p`. Form integer Delta-SNR density bins and count every cell explicitly, including zero cells.

The one-off derivation script was retained at `tmp/build_griffiths_fig6_reference_20260924.py`; its checksum is recorded in `verification.json`. It imports no WSPRadar modules. Pandas is used only for table serialization. The script is not needed by the regression tests and must never be invoked automatically to refresh expectations.

Only after deriving the expectations were the independently grouped source reports compared with the frozen SQL output. All 12,290 group keys, receiver counts and present-side normalized SNR maxima matched exactly. This is a crosscheck of the captured SQL output; it is not execution of the current SQL against the fixture.

## Temporal contracts

The base fixture includes 24-hour, 3-hour, 1-hour and 6-hour chronological profiles plus the 24 folded UTC hours. They contain 3, 24, 72, 12 and 24 bins respectively. Every profile contains the same 6,459 Joint Spots. The folded profile should remain unchanged when the chronological selector changes.

There are 58 integer Delta-SNR density bins, from -17 through +40 dB, with edges at -17.5 through +40.5 dB. Density CSVs store integer counts rather than rendered colors. The renderer scales each panel relative to its largest populated density cell; that presentation normalization must not alter scientific counts or summaries.

The last hourly bin is **2017-04-07 23:00-23:45 UTC**, with 13 Joint Spots, median 0 dB, Q1 -3 dB and Q3 +2 dB. It is a 45-minute final bin, not a full hour and not an extension to midnight. Its midpoint is 23:22:30 UTC. This fixture cannot supply observations after the captured exclusive end.

The smallest chronological hourly support is six Joint Spots, and the smallest folded-hour support is 79. Thus every hourly and folded bin meets the current minimum of five observations for displaying IQR. The separately installed Figure 3 reference covers a sparse bin below that threshold. Storing a quartile is distinct from deciding whether the renderer should draw an IQR rail.

Arithmetic means are included for human review and comparison of statistical summaries. The production temporal recipe currently stores counts, medians and quartiles, not means. The mean-per-day metadata divides by three represented UTC calendar dates; it does not extrapolate the partial final day into a full 24-hour exposure.

## Relationship to the publication

[Griffiths and Squibb, Improving HF band SNR from analysis of WSPR spots, Practical Wireless, October 2017](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf), Figure 6, presents the diurnal density visualization. **6,390 is the sum of the printed distance-bin observation counts in Figure 7**, which covers the same stated period; it is not an exact measurement count printed for Figure 6. The present 10,000 km reconstruction contains 6,459 paired observations, 69 more than that Figure 7 sum. Widening the radius gives 6,474, not the published distance-bin total.

These populations must not be presented as exactly equivalent. The publication does not provide the complete machine-readable selection and aggregation inputs needed to identify the cause of the difference. Archive changes and selection differences remain possible explanations, not established findings. In particular, the density visualization is not itself an hourly median or IQR curve, so its colors are not exact median expectations.

The external agreement is the qualitative UTC-hour reversal and its approximate amplitude. Exact expected arrays in this fixture come from a reproducible calculation on the frozen source reports, not digitized paper pixels or the application's screenshot. No broad paper-derived tolerance is used to weaken the exact regression assertions.

## Files and provenance

- `demo.config`, `analysis_context.json`: fixed base configuration and captured canonical context. The 22,000 km variant is a single explicit override recorded in `expected_summary.json`.
- `source_rows.parquet`: the original 18,791 raw endpoint reports, copied byte-for-byte from the capture. `source_rows_query.sql` records their acquisition query.
- `input_sql_rows.parquet`: the 12,290 captured SQL-result rows, converted without scientific transformation from `sql_output_legacy.csv` for offline production replay. `query_legacy.sql` preserves the original aggregation query.
- `expected_paired_rows.parquet` and `expected_paired_rows_22000km.parquet`: independently reconstructed paired units, including exact cycle/time identity, both normalized SNR components and their difference.
- `expected_24h.csv`, `expected_3h.csv`, `expected_1h.csv`, `expected_6h.csv`, `expected_utc_hour.csv`: fixed temporal summaries at the base radius.
- `expected_density_*.csv`: complete integer count grids for those base profiles.
- `expected_utc_hour_22000km.csv`, `expected_density_utc_hour_22000km.csv`: wider-scope folded summaries and density counts.
- `expected_summary.json`: stage counts, global summaries, profile metadata, wider-scope metadata, paper qualifications and temporal anchors.
- `capture_provenance.json`: original capture date, provider, selected legacy mode, timings and historical source-revision hashes. Its inventory describes the original capture, not this fixture's installed inventory. Historical implementation hashes are provenance, not assertions against the current checkout.
- `verification.json`: independent source reconstruction and comparison with the separately performed headless production analysis, before integrated pytest execution. It makes no claim that the new tests have already passed.
- `manifest.json`: mandatory installed-file inventory, canonical byte lengths and SHA-256 hashes.

Text files use UTF-8 without BOM and LF line endings. Parquet is binary. The manifest describes the actual installed bytes; do not silently normalize corrupt or edited expectations inside the test.

## Regression scope and maintenance

The companion regression replays the frozen SQL-result rows through the real post-fetch filters, geographic selection, station aggregation, Inspector paired eligibility and temporal recipes. Expected rows and summaries must be read only for assertions, never substituted into the calculation. Required files must fail loudly when absent or corrupt.

The regression does not run a database, contact a provider, exercise automatic provider failover, establish the scientific meaning of historical `code=0`, or execute the current SQL against raw source rows. Independent derivation of the expectations covers normalization and grouping arithmetic for the captured population, but a production SQL change requires a separate SQL-execution test to be checked end-to-end.

Use exact comparisons for identities, timestamps, counts and this dataset's integer/half/quarter-dB statistics. An absolute tolerance of 1e-12 dB is sufficient for ordinary floating arithmetic summaries such as means. Do not use a broad +/-1 dB tolerance to accommodate unexplained changes.

A changed result with fixed input and settings is a regression until explained. An intentional scientific correction may warrant a reviewed new fixture version, but expected values must never be regenerated simply to make a failing test pass. Keep fixed-source inputs, independently derived expectations and observational verification distinct. Fixture generation did not edit application code or run pytest; integration checks are recorded separately by the implementing task.

## Integration verification (2026-09-24)

The installed Figure 3 and Figure 6 reference tests ran together with the prepared-export integrity, segment temporal evidence, evidence-statistics and regression-runner modules: **69 passed, 1 skipped, 1 existing Matplotlib warning in 21.75 seconds**. The skip belongs to the absent prepared-export fixture; neither scientific reference is optional. Before that combined run, the preserved Figure 3 case passed separately: **8 passed, 12 deselected, 1 existing warning in 7.88 seconds**.

Eight temporary in-memory erroneous results or configuration choices were each rejected by the installed reference assertion helpers: means substituted for medians, equal weighting of station-hour medians, equal weighting of date-hour medians, a one-hour UTC shift, a one-dB displacement of density cells, reversed Delta SNR, an extension of the partial final hour to midnight, and omission of the 10,000 km geographic cutoff. These were assertion-sensitivity checks without application-source mutations or changes to frozen expected files; they are not a full production mutation-testing campaign.

The regression module remains registered once in the 82-module serial chunk manifest. Changed-test compilation and patch whitespace checks passed. Application runtime code and the Figure 3 fixture were unchanged. No full regression suite, browser run, live provider request or database SQL execution was required or performed for this test/data-only addition. The independently derived exact profiles passed without adjusting their expected values to accommodate the production result.
