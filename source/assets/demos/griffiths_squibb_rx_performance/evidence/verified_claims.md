# Verified evidence for the G3ZIL RX Performance guided demo

This is the audit companion to `RX_Performance_Guided_Demo.md`. It supports the guide's examples without turning the reader-facing tour into a data audit. All numerical findings below were recomputed from the supplied processed CSVs and checked against the exported figures where the quantities are shown.

## Source and limits

The unchanged source archive is [original_export.zip](../source/original_export.zip), originally named `WSPRadar_export_2026_10_24__22_01.zip`. It contains the top-level directory `WSPRadar_export_2026_10_24__22_01/`.

- Archive SHA-256: `ba2e68b9cb82d000eaf472ba9da4504dae1114afa05c23e198eae842390385ae`.
- Completed-run metadata: [run_metadata.json](../source/config/run_metadata.json).
- Original settings: [wspradar_config.config](../source/config/wspradar_config.config).
- Methods: supplied [README §§7.1, 7.3 and 7.4](../source/README.md#sec-7-performance).
- Software: v1.0 RC3; Performance method `opportunity-v3`; source `wd2`; historical selection `legacy_no_code`; exported `2026-10-24T20:01:00Z`.
- Export signature: `4d53866c6385c4ced2e88587884cc0b1833f8e23ccc83cbf9e8bed805cceaaa6`.

The all-stations Drill-Down CSV covers the full active Inspector scope in this export: **Full Range | All Directions**, within the completed run's distance restriction. It is sufficient to reproduce all numerical examples in this guide. No Parquet reader was available, so `analysis_cache.parquet` is retained unchanged in the original ZIP but was not decoded. Original upstream database rows were not queried. This audit verifies the processed export's internal calculations; it does not independently revalidate all upstream filtering, activity witnesses, strongest-report consolidation or reported-power normalization.

The selected Miss example has a separate, directly visible in-scope Target-activity witness, described below. Of 20,016 represented cycles, 20,010 contain a success from a qualifying in-scope identity; six have no such success in this CSV. The documented activity gate is established before final population filtering. This audit cannot independently identify the upstream witness used for those six cycles and does not infer its cause. Their absence from the retained qualifying population is not evidence of a method error or an uptime result.

## Definitions and calculation

Primary input: `performance/table_drilldown_all_stations_current_segment.csv` inside the original ZIP. Identity is **TX Station + full Locator**; each row is one retained identity-cycle opportunity.

For identity i:

- Tᵢ = sum of `Target (T)`; Eᵢ = sum of `Elsewhere (E)`; Oᵢ = Tᵢ + Eᵢ.
- Individual Decode Rate = 100 × Tᵢ / Oᵢ.
- Station-balanced rate = arithmetic mean of qualifying identities' individual rates.
- Opportunity-level rate = 100 × ΣTᵢ / ΣOᵢ.
- At-least-once reach = 100 × number of qualifying identities with Tᵢ > 0 / number of qualifying identities.

**E is a Miss count, not an external-report flag.** `T - Target` and `Target-only` are both successes with T=1, E=0. The former has external confirmation; the latter does not. `E - Elsewhere` has T=0, E=1 and blank Target SNR. Target-only successes are already included once in the success and opportunity totals.

Successful SNR calculations use `Target SNR (dB @ 30 dBm)` only on successful rows. The exported CSV has no original reported-SNR or transmit-power column, so normalization is taken from the documented method and supplied normalized values; it is not reconstructed from raw power here. The method is `normalized SNR = reported SNR − reported power (dBm) + 30`. Outcomes are not recalculated at 1 W.

## Preserved run definition

| Item | Actual saved value |
| :--- | :--- |
| Analysis / Reference | RX Performance / none |
| Target and configured QTH | G3ZIL / IO90HW |
| Band | 40 m |
| Window | 2017-04-01 00:00 to 2017-05-01 00:00 UTC |
| Maximum peer distance | Strictly below 22,000 km; worldwide scope |
| Solar selection | All |
| Special-callsign / moving-station exclusions | Both off |
| Minimum opportunities per identity | 3 |
| Minimum qualifying identities per map segment | 1 |
| Inspector | Full Range / All Directions |
| Inspector / selected-station chronology | 12h / 12h, separate controls |
| Selected transmitter | HB0QRP (JN47) |
| Zero-success visibility | Off; `show_zero_target=false` |
| Station Insights column filters | None |

The embedded original profile description still says peers below 10,000 km; the actual saved setting and figures use **22,000 km**. Its **HB0QRP / 12h** description agrees with the settings, metadata, selected CSV and figures. The prepared configuration in `config/` changes only that distance wording in the English and German profile descriptions; the titles and every non-profile field are identical to the original.

## Headline findings and the hidden-population distinction

See [overview.json](overview.json) and [stations.csv](stations.csv).

| Quantity | Recomputed value | Guide presentation |
| :--- | ---: | :--- |
| Qualifying transmitter identities | 2,107 | 2,107 |
| Heard at least once | 996 | 996 |
| Heard only elsewhere | 1,111 | 1,111 |
| At-least-once reach | 47.2710014% | 47.3% |
| Successes | 114,086 | 114,086 |
| Misses | 559,325 | Used in the denominator and figure |
| Confirmed opportunities | 673,411 | 673,411 |
| Station-balanced rate | 17.8960291% | 17.9% |
| Opportunity-level rate | 16.9415112% | 16.9% |
| Externally confirmed successes | 113,699 | Not narrated in the guide |
| Target-only successes | 387 | Subset of successes; not added again |

The supplied Station Insights CSV has **996 rows**, because the saved view hides zero-success identities. Its Miss total is **391,200**, not the full population's 559,325. Therefore that table alone cannot reproduce the full-population rate. The all-stations Drill-Down CSV retains the 2,107 qualifying identities and the complete denominator. The documented **Heard only by other stations.** visibility control reveals the remaining 1,111 identities without recalculating scientific results.

Compared with the earlier 10,000 km export, all **636,673 retained rows below 10,000 km are value-identical after sorting**; only their order differs. The expanded scope adds **157 qualifying identities**, including **27 heard**, and **208 successes in 36,738 confirmed opportunities**. The original path results are unchanged. The lower worldwide percentages reflect the enlarged population and denominator, not a deterioration in those original observations. The HB0QRP selected-station CSV is byte-identical to the earlier export.

## Geographic examples

Distance and bearing were reconstructed from the cell centers of the reported Maidenhead locators and configured IO90HW, using the documented spherical radius of 6,371 km. The results reproduce the exported distance and azimuth rounding. This avoids classifying boundary cases from rounded CSV distances alone.

Map sectors are 22.5° wide; the selected rings are 0–2,500, 2,500–5,000, 5,000–10,000, 10,000–15,000, 15,000–20,000 and 20,000–22,000 km. See [map_segments.csv](map_segments.csv).

| Map scope | Heard / qualifying | Station-balanced rate | Pooled rate | Successes / opportunities |
| :--- | ---: | ---: | ---: | ---: |
| ESE · 0–2,500 km | 112 / 123 | 51.6% | 41.4% | 28,077 / 67,805 |
| WNW · 5,000–10,000 km | 138 / 481 | 5.1% | 3.2% | 4,443 / 140,254 |

These are different path populations, not a controlled antenna-pattern estimate. The distant scope contains more heard identities but much lower consistency. The guide deliberately uses well-populated examples: the map also permits one-identity segments, such as NE at 2,500–5,000 km with 24 successes in 32 opportunities. A warm sparse sector is not broad evidence.

The current statistics figure uses separate **2,500 km distance bins**, with a final **20,000–22,000 km** bin of width 2,000 km. See [distance.csv](distance.csv).

| Distance | Heard / qualifying | Reach | Station-balanced rate | Pooled rate | Median of successful station SNR medians |
| :--- | ---: | ---: | ---: | ---: | ---: |
| 0–2,500 km | 776 / 1,080 | 71.9% | 30.7% | 26.9% | −14.75 dB (about −15 dB) |
| 5,000–7,500 km | 143 / 473 | 30.2% | 5.4% | 3.4% | −28 dB |
| 17,500–20,000 km | 5 / 18 | 27.8% | 3.4% | 0.33% | −31 dB |

The distance SNR statistic first takes each heard transmitter's successful-SNR median, then the median across those station medians. Miss-only identities have no synthetic SNR. The IQR describes the middle half of station medians, not uncertainty in a population estimate.

The current figure's legend specifies **IQR (5+ stations)**. The unchanged supplied README describes the earlier distance-bin range and a three-station IQR rule; those presentation details do not describe this newer figure. The current figure's own bin labels, footer and legend govern the examples above.

The 17,500–20,000 km bin contains **39 successes and 11,713 misses in 11,752 opportunities**. Its five heard identities establish reach, but the low pooled rate and smaller population do not support a claim of dependable coverage. The **20,000–22,000 km** bin has no qualifying identities or opportunities; missing rate/SNR there is not measured zero.

The farthest actually heard identity is **ZL4KT (RE54GD)**, **19,193.979 km** from the configured QTH (displayed as **19,194 km**), at **49.640° NE**. Its **3 successes / 61 opportunities** give a **4.918% Decode Rate**; its median successful normalized SNR is **−33 dB**. This is an example of distant reach, not evidence of frequent reception or a reconstruction of the raw decoder threshold.

## Segment temporal examples

See [global_12h.csv](global_12h.csv) and [global_hourly.csv](global_hourly.csv).

**831 identities** meet the separate requirement of at least three successful observations for a deviation baseline. Those identities supply 113,841 successful rows. Their baselines are full-run median successful normalized SNRs. Each chronological station-bin contributes one median deviation; the plotted line is the median across those contributions.

| 12-hour interval, UTC | Median deviation | Contributing station-bin medians |
| :--- | ---: | ---: |
| 16 April 00:00–12:00 | 0 dB | 142 |
| 22 April 00:00–12:00 | −5 dB | 91 |

The populations differ, so the guide describes the comparison as a change in the summaries and then checks a fixed selected path. It is not a controlled matched-station effect estimate.

The folded SNR-deviation profile has medians between **−3 and −4 dB at 09–14 UTC**, then **+2, +3 and +2.5 dB at 18, 19 and 20 UTC**. The guide rounds this to an accessible broad pattern. Folded contributions are transmitter/date/hour medians; additional rows in one such group add no weight, but additional represented dates do. This is not a globally equal-station or equal-date average.

Temporal support includes all confirmed opportunities of qualifying identities, including zero-success transmitters and paths without enough successes for a deviation baseline. Upper chronological bars divide each station's unit support into success and miss fractions according to its rate; lower bars count actual opportunity outcomes. Folded bars show average daily hourly support over 30 represented dates. The two units must not be added together, and the upper green area is not at-least-once reach.

## Selected HB0QRP (JN47)

Reconstructed geometry: **843.898 km, 112.896°**, displayed as 844 km / 113° ESE. It has **3,412 successes + 4,350 misses = 7,762 opportunities**, rate **43.9577428%**, and monthly median successful SNR **−15 dB**. Its 44 Target-only successes are included in those 3,412 successes.

See [HB0QRP_hourly.csv](HB0QRP_hourly.csv). Folded successful SNR is a median of daily hourly medians, rather than one pooled median of all successful observations.

| UTC hour | Successes / opportunities | Rate | Folded successful SNR | Dates with successes / opportunities |
| :--- | ---: | ---: | ---: | ---: |
| 07:00–08:00 | 309 / 435 | 71.0% | −15 dB | 30 / 30 |
| 11:00–12:00 | 67 / 416 | 16.1% | −19 dB | 22 / 30 |
| 16:00–17:00 | 311 / 418 | 74.4% | −14 dB | 30 / 30 |
| 20:00–21:00 | 248 / 379 | 65.4% | −11.25 dB | 28 / 30 |

The guide uses three of these rows, rounds rates to whole percentages and describes the evening SNR as approximately −11 dB. Stronger successful SNR at 20 UTC does not give a higher rate than at 07 UTC. This illustrates the distinction between conditional successful signal levels and the complete opportunity outcomes; it does not reconstruct the missing signals' SNR.

See [HB0QRP_12h.csv](HB0QRP_12h.csv) for the corresponding date comparison:

| UTC interval | Successes / opportunities | Decode Rate | Median successful SNR |
| :--- | ---: | ---: | ---: |
| 16 April 00:00–12:00 | 61 / 108 | 56.4815% | −13 dB |
| 22 April 00:00–12:00 | 14 / 98 | 14.2857% | −20 dB |

## Four real Drill-Down rows and a real activity witness

All four rows are present in the original `performance/table_drilldown_selected_stations.csv`. They are also supplied in [recommended_drilldown_rows.csv](recommended_drilldown_rows.csv).

| 9 April 2017 UTC | Exact Outcome | T | E | Normalized Target SNR |
| :--- | :--- | ---: | ---: | ---: |
| 18:08 | `T - Target` | 1 | 0 | −8 dB |
| 18:12 | `Target-only` | 1 | 0 | −8 dB |
| 18:16 | `T - Target` | 1 | 0 | **0 dB** |
| 18:20 | `E - Elsewhere` | 0 | 1 | **Blank** |

At 18:20 the original all-stations CSV also contains **eight successful G3ZIL decodes of other transmitters**, including **HB9TSO (JN47)** at normalized **+4 dB**. These are preserved in [the activity-witness extract](2017-04-09_1820_Target_activity_witnesses.csv). They establish G3ZIL's activity in that cycle. HB0QRP's separate Miss outcome carries the external transmitter-activity evidence. Hearing HB9TSO alone would not establish an HB0QRP opportunity.

The planned app inspection uses a 1h focus centered on 9 April 18:30 UTC. The method/control documentation supports this instruction; it has not been executed in the live app in this preparation. The four rows' presence in the selected CSV is verified. Live filtering and rendering remain Codex integration checks.

## Reproduction and checks completed

Run the case-specific, read-only-source audit with Python, pandas ≥2.2 and numpy after extracting the source ZIP:

```sh
python evidence/audit_rx.py /path/to/WSPRadar_export_2026_10_24__22_01 /path/to/new-audit-output --figure-distance-bin-km 2500
```

Paths are portable. The audit reads QTH, time window, distance cap and qualification threshold from configuration. It uses this case's verified map-ring boundaries, clipped to the configured cap; the displayed 2,500 km distance-bin width is an explicit argument checked against the figure. It retains this case's verified 12h grouping and selected transmitter. An optional `--baseline-export-root /path/to/earlier-export` checks the unchanged original-scope rows. This is not a general replacement for WSPRadar's methods.

Checks completed on the retained CSV evidence:

- 673,411 rows and no duplicate transmitter-identity/cycle rows; each row has exactly one success or miss.
- No missing identity fields, malformed locators, off-cycle timestamps, out-of-window rows or peers at/beyond the distance cap.
- Every retained identity meets the three-opportunity minimum.
- Every success has finite normalized SNR; every miss has blank SNR. Genuine successful 0 dB values remain distinct from blanks.
- Selected-station CSV exactly matches its subset of the all-stations CSV.
- All six current light figures inspected; all six theme pairs retained exactly as exported. Numerical examples agree with the supplied figures and saved state.

The original paper supplies setup context only: Griffiths and Squibb, *Improving HF Band SNR*, *Practical Wireless*, October 2017, pp.23–26, [author-hosted PDF](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf). Its low-dipole dimensions, shed receiver and 8 April retuning entry were checked. The Performance figures and rates are this WSPRadar run's results, not numerical claims copied from the paper.
