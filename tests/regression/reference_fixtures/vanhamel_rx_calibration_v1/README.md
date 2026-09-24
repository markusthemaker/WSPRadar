# Vanhamel receiver calibration: independent seven-day archive reference

This mandatory offline reference exercises the installed RX Hardware A/B calibration demo using frozen original WSPR reports and independently calculated expectations. The selected UTC window is **2021-02-06 06:00 inclusive through 2021-02-13 06:00 exclusive**, exactly 168 hours. Target is **ON4AWM0**, Reference **ON4AWM1**, configured QTH **JO20OT**, band **160 m**. It is an archive reconstruction consistent with the paper's rounded receiver-offset result; it is not an authenticated identification of the paper's original seven-day dataset.

## Published evidence and its limits

Vanhamel, Machiels and Lamy, [*Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*](https://doi.org/10.1155/2022/4809313), report a common-antenna calibration of two receiver chains for seven consecutive days, followed by a later separate seven-day confirmation. Both gave an average difference of **1.2 dB**. The calibration narrative is on printed article pages 4-5; the shared-antenna arrangement is Figure 1 and Section 3 on printed page 3. In the repository PDF used for the review, a cover page shifts PDF page numbers by one. `paper_features.json` records the source PDF hash, exact evidence locations and scientific qualifications.

The calibration uses one ITA LWA II antenna and a splitter feeding both RTL receiver chains, identical WSJT settings, disabled hardware/audio AGC, matched coaxial lines and band-pass filters. The publication does not supply the calibration calendar endpoints, receiver-callsign direction, exact pairing procedure, or averaging weights. It calls the result an average, not a median. Its later antenna-rotation experiments and approximately 3 dB results are distinct experiments and do not date this calibration.

The paper selects stations received **more than 50** times; the installed demo uses **at least 50 joint observations per full transmitter identity**. There is no identity with exactly 50 joint observations in this frozen population, so the strict and inclusive thresholds select the same peers here. This numerical equivalence does not resolve the paper's unreported pairing and weighting details.

The publication anchor is the independently read **1.2 dB average**. The regression comparison policy uses the conventional one-decimal interval **[1.15, 1.25) dB**. This is a declared rounding comparison, not measurement uncertainty, a confidence interval, or a fitted tolerance. Exact archive means, counts, histogram heights, station values and time-bin values come from the raw-report calculation, not the rounded paper number.

Available author correspondence identified an approximate February 9 21:58-February 13 05:34 interval and subsequently a more specific complete-filter-chain interval of February 9 21:54-February 12 06:46, using the timestamps as written. The correspondence does not explicitly label their time zone; the current reconstruction interprets the WSPR timestamps as UTC. Their concise date provenance and this assumption are retained in `capture_provenance.json`; neither interval is presented as an original seven-day publication interval. No private email file or full message is redistributed. The hardware state across every earlier day of the selected seven-day archive interval is not independently established by this fixture. Stable archive statistics and a matching seven-day duration do not establish that missing historical provenance.

## Frozen raw population and calculation

The original sources are two direct provider Parquet captures covering February 6-8 and February 9-16, 2021. Their query texts, file hashes and observed filesystem modification timestamps are recorded. An exact network acquisition timestamp was not separately recorded; filesystem timestamps are labelled as such. `source_rows.parquet` freezes the union trimmed to **2021-02-06 05:58 inclusive through 2021-02-13 06:02 exclusive**, preserving all captured modes and locators for the two receivers on this band. This includes one nominal cycle before and after the demo window. The earlier guard cycle contains no report; the exact start boundary contains two genuine reports, and the exclusive end boundary contains two genuine reports. These permit start-inclusion and end-exclusion checks without synthetic rows.

The raw fixture has **3,233 reports**, all with `code = 1`; **3,231** fall inside the demo window. The capture contains no non-code-1 negative example. Source IDs are unique and records are ordered by time and ID. The CSV preserves strings and integers and expands original Float32 coordinates to their exact Float64 values before serialization. Use pandas `float_precision="round_trip"` for exact coordinate-preservation checks against the Parquet source.

[build_vanhamel_reference_fixture.py](../../../../scripts/build_vanhamel_reference_fixture.py) uses only the Python standard library and reads only the frozen CSV and configuration. It has no WSPRadar imports or application-output inputs. The bounded calculation follows these declared contracts:

1. Select exact receiver callsigns, configured receiver grid-4 JO20, band code 1 for 160 m, strict decode `code = 1`, nonzero transmitter latitude and the start-inclusive/end-exclusive window. The configured six-character QTH supplies the geographic center; receiver selection follows the established grid-4 contract.
2. Group by 120-second UTC slot and **transmitter callsign plus complete reported locator**. Each receiver contributes its maximum `snr - power + 30` within a group; absent endpoints use the SQL default zero while presence remains represented separately.
3. Retain slots where Target received at least one report, then retain peers strictly within 2,500 km of the JO20OT cell center. Distances and bearings use an independent spherical calculation. There is no ambiguity in within-group transmitter coordinates in this corpus.
4. Determine each transmitter identity's joint count over the complete seven-day population and retain its paired evidence when that count is at least 50. Form **Target-minus-Reference** differences. All qualifying pairs have equal reported transmitter power on both receiver reports, so normalization cancels in each difference; this does not constitute independent power calibration.
5. Compute pooled mean/median, sample standard deviation with denominator n-1, and quartiles by linear interpolation at `(n-1)*p`. Station summaries are computed separately. Build the exact 1 dB histogram and seven 24-hour bins anchored at 06:00 UTC. Station eligibility is determined once over the full window, not independently inside each daily bin.

There are **1,781 SQL groups**, of which **1,770** survive activity/geographic selection: 1,450 joint, 316 Target-only and four Reference-only groups across 59 transmitter identities. Before the minimum-support threshold, 50 identities have some joint evidence. **Ten qualifying identities contribute 1,143 joint observations over 973 distinct cycles**. No endpoint group contains duplicate reports. `expected_station_audit_rows.csv` preserves support and statistics for all retained identities; `expected_station_rows.csv` contains the ten qualifying identities.

The qualifying pooled mean is **+1.2143482064741906 dB**, median **+1 dB**, Q1 **+1 dB**, Q3 **+2 dB**, and sample standard deviation **0.6168139491150979 dB**. The exact histogram is:

| Difference, dB | Joint observations |
| --- | ---: |
| -1 | 4 |
| 0 | 98 |
| +1 | 701 |
| +2 | 329 |
| +3 | 11 |

Each of the ten station medians is +1 dB; the mean of station medians is therefore +1 dB. The equal-station average of the station means is +1.2265613143551892 dB. These differ from the pooled mean and are intentionally distinct weighting choices.

## Temporal expectations

`expected_24h.csv` records seven 06:00-to-06:00 UTC bins, including counts, mean, median, Q1, Q3, sample spread and extrema. `expected_density_24h.csv` records the count at every integer Delta-SNR bin for each time bin, including zero cells. These are independent expectations for the application's temporal recipe; the paper publishes no corresponding temporal curve.

| UTC bin start | Joint observations | Mean Delta-SNR, dB |
| --- | ---: | ---: |
| February 6, 06:00 | 185 | 1.2054054054 |
| February 7, 06:00 | 119 | 1.0000000000 |
| February 8, 06:00 | 208 | 1.2211538462 |
| February 9, 06:00 | 177 | 1.2881355932 |
| February 10, 06:00 | 124 | 1.3306451613 |
| February 11, 06:00 | 216 | 1.2546296296 |
| February 12, 06:00 | 114 | 1.1228070175 |

Every daily median is +1 dB. The daily means are not all 1.2 dB, and the publication rounding interval is applied to the chosen full-window mean, not asserted for every day.

## SQL replay and scope

The regression builds current production SQL and executes its scientific SELECT, predicates, UNION, grouping and aggregations over the raw fixture in SQLite. The shared test adapter removes only the ClickHouse output-format serialization directive and provides the required timestamp, conditional-aggregate and diagnostic-distance functions. This exercises generated SQL against independent expected rows, but does not validate native ClickHouse engine semantics, provider behavior, aggregate ties or general cross-engine equivalence. Diagnostic receiver distance is not a native ClickHouse distance oracle. This corpus has no duplicate endpoint groups or conflicting group coordinates.

The source was originally restricted to the two receiver callsigns, selected band and wider acquisition dates. It is not a general population for testing every possible broadening of those acquisition predicates. All rows happen to use code 1, so mode-selection edge cases remain covered by other regressions. The exact boundary reports specifically strengthen window inclusivity coverage. No network is needed for the fixture tests.

The reference can substantiate compatibility of the selected archive population, scientific processing, native paired evidence, distributions and temporal aggregation with independently calculated expectations. It cannot authenticate the original paper dataset, certify historical antenna connections, or supply physical receiver calibration uncertainty.

## Maintenance and files

`manifest.json` hashes all installed fixture files. `source_query_february_6_8.sql` and `source_query_february_9_16.sql` preserve the original acquisition queries; `capture_provenance.json` records how their original responses were combined. `demo.config` freezes the installed demo. The expected SQL and retained-row tables precede station minimum-support filtering; `expected_all_paired_rows.csv` retains all 1,450 geographic/activity-qualified joint observations; `expected_paired_rows.csv` retains only the 1,143 observations from qualifying identities, including both SNR components, original powers and source report IDs.

To review an intentional baseline update, run the independent builder into a separate directory:

```powershell
.\.venv\Scripts\python.exe scripts/build_vanhamel_reference_fixture.py --source-csv tests/regression/reference_fixtures/vanhamel_rx_calibration_v1/source_rows.csv --config tests/regression/reference_fixtures/vanhamel_rx_calibration_v1/demo.config --output-directory tmp/vanhamel_reference_candidate
```

Tests never regenerate expectations. Review source provenance and differences before replacing any baseline or updating its hashes. Keep the limited paper anchor separate from the exact independently calculated archive expectations.
