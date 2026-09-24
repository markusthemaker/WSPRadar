# Milazzo Figure 6: all-candidate publication mapping audit

**Status update, 24 September 2026: the direction mismatch is resolved.** All 44 Figure 6 markers match the reciprocal reports of VE6PDQ transmitting to KP4MD and WB6RQN, with exact annotated SNRs and at most two minutes of graphical time error. See [the RX reconciliation](../milazzo_fig6_rx_v1/README.md). The figure's printed direction led the initial audit below to compare different observations. Its negative TX results remain reproducible, but do not demonstrate missing archive reports, a required SNR correction, or a WSPRadar defect. The TX demo's independent arithmetic remains valid; Figure 6 validates the separate RX path.

**Historical audit, retained for traceability:** the following investigation originally recorded unresolved publication-to-archive correspondence for the caption's TX direction. It compared every independently digitized Figure 6 marker with every VE6PDQ receive report in the frozen TX capture. It is not a passing publication-SNR oracle, and a passing regression of this historical audit must not be described as reproducing the article's numerical TX antenna comparison. Conclusions below that describe the cause as unresolved predate the reciprocal RX evidence.

## Source authority and frozen observations

Carol F. Milazzo, KP4MD, *Comparative Antenna Analysis with WSPR: Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*, posted 13 January 2011: [article](https://www.qsl.net/kp4md/wspr.htm), [original Figure 6](https://www.qsl.net/kp4md/WSPR%2040m%20at%20VE6PDQ.JPG).

The original Figure 6 title, HTML caption and image reference consistently identify 7 MHz transmissions **received at VE6PDQ**. Its legend assigns blue squares to KP4MD and red circles to WB6RQN. Its dated UTC axis runs from 19 December 2010 at 12:00 to 20 December at 20:00; it is not a folded time-of-day axis. The article separately identifies Figure 7 as transmissions **from VE6PDQ**, and Figures 9/10 as 14 MHz comparisons. Those printed labels initially gave no reason to reverse the direction; the subsequent 44 reciprocal report matches establish that the plotted direction contradicts those labels. Exchanging the two transmitter labels in this TX dataset, as checked below, is not the same diagnostic as reversing transmitter and receiver roles.

`publication_features.json` and `publication_markers.csv` are byte-for-byte copies of the independent source extraction. All 44 marker centers and the counts of 31 blue/13 red markers were computed before archive values were supplied. Conversion of those centers to UTC and writing the source artifacts occurred afterwards, using only the printed tick calibration. Their original **±4 minute** time allowance and **±0.25 dB** graphical amplitude allowance are unchanged. These are image-readout tolerances, not experimental uncertainty or statistical confidence. The visible marker count cannot rule out coincident observations concealed by overlapping symbols. Straight lines connect markers across long gaps and do not represent additional reports.

The article describes additive correction for transmitted-power differences but does not specify a common reference power, provide its spreadsheet, or define thinning, averaging, duplicate handling, same-cycle pairing or a global Target-Active Gate. It states KP4MD at 5 W/37 dBm and WB6RQN at 2 or 5 W/33–37 dBm. Those setup statements are useful external facts; they are not a definition of WSPRadar's conditional selection.

The source image and full HTML are retained only in the investigation workspace and are identified by hashes in the feature file. No explicit image reuse license was established, so this fixture does not bundle the original JPEG or a reproduced publication image. The CSV contains factual numerical readouts with source attribution. Workspace paths in the unchanged source feature file describe its extraction provenance, not additional required fixture files.

## Complete candidate rule

The raw input is the frozen 1,992-report capture from 18 December 00:00 inclusive to 21 December 00:00 exclusive, provider band 7, transmitters KP4MD and WB6RQN. Its original Parquet SHA256 is `a4a3970597bfa697ef85d0297dd0eadbbacafb49e432450c466eb79fbbc55d61`. All raw reports carry code 0, so this comparison uses the explicitly identified historical all-code selection. All endpoint locators start CM98 and all receiver latitudes are nonzero.

For each marker, inspect **every** raw report with the same transmitter callsign and receiver VE6PDQ whose timestamp differs from the fixed graphical readout by at most 240 seconds. Do not interpolate the publication line, choose only the nearest report, change a marker's date, adjust the tolerance after inspecting results, or label a temporal candidate as a confirmed match. The publication identifies the receiving callsign but not its full locator; the archive has only VE6PDQ/DO34ir in this capture, and the locator is retained explicitly in the tables.

Every candidate records its raw code, power, date, identities, SNR and the three declared-power transformations:

`normalized_snr = raw_snr - reported_power_dbm + reference_power_dbm`

The inspected reference powers are 30, 33 and 37 dBm: WSPRadar's standard reference, the lower published transmitter power, and the higher published transmitter power. Raw SNR is also checked. These are labelled interpretations, not inferred publication settings. No free SNR shift or scale was fitted. The per-candidate columns `paper_minus_*` consistently mean the published graphical value minus the corresponding archive value.

The algorithm retains all candidates and detects report reuse across marker candidate sets. In this capture each of the 18 candidate-bearing markers has exactly one candidate and no report belongs to multiple marker sets. That observed uniqueness does not convert the candidates into matches: amplitude agreement still fails.

## Exhaustive coverage and agreement

| Population or check | KP4MD | WB6RQN |
|---|---:|---:|
| Visible Figure 6 markers | 31 | 13 |
| Raw VE6PDQ reports, full 18–20 December capture | 63 | 26 |
| Raw VE6PDQ reports, article's 19–20 December dates | 63 | 24 |
| Raw VE6PDQ reports inside the plotted axis extent | 57 | 19 |
| Markers with a same-transmitter report within ±4 minutes | 16 | 2 |
| Markers without any such report | 15 | 11 |
| Archive reports without a nearby same-transmitter marker, full capture | 47 | 24 |
| Archive reports without a nearby marker, inside plotted axis extent | 41 | 17 |
| Markers agreeing in both time and raw SNR | 0 | 0 |
| Markers agreeing in both time and SNR at 30 dBm | 0 | 0 |
| Markers agreeing in both time and SNR at 33 dBm | 0 | 0 |
| Markers agreeing in both time and SNR at 37 dBm | 0 | 0 |

These counts explicitly include non-joint observations. Of the 89 raw reports, 62 are Target-only, 25 are Reference-only, and two are the two endpoints of one joint receiver-cycle. None of the 18 graphical time candidates belongs to that joint cycle. All 16 blue candidates are Target-only; both red candidates are Reference-only. There are therefore 26 markers without a temporal candidate even before applying the software gate, and no accepted SNR correspondence among the remaining 18.

The blue candidate differences `paper SNR - raw SNR` are **+4, +6, +9, +10, +11, +12 and +14 dB**, occurring 2, 3, 3, 4, 2, 1 and 1 times respectively. Both candidates with a +11 dB difference were initially conspicuous, but the complete comparison does not support applying +11 dB to the series. All blue reports have the same declared 37 dBm power; a common normalization baseline would add the same amount to every one, so it cannot reconcile this set of temporally nearby candidates. This does not prove those candidates are the author's actual observations; it establishes that they cannot all be treated as matched observations using one constant offset.

The two red candidates have paper-minus-raw differences **+1 and −8 dB** and both report 33 dBm. Neither agrees under raw, 30, 33 or 37 dBm interpretation. Three concrete checks show why a pair of selected examples would mislead:

| Marker | Published readout | Nearby archive report | Paper minus raw |
|---|---|---|---:|
| KP4MD_02 | 19 Dec ~14:47, +2 dB | id44625244, 14:44, −9 dB, 37 dBm | +11 dB |
| KP4MD_13 | 19 Dec ~22:47, −18 dB | id44690130, 22:50, −22 dB, 37 dBm | +4 dB |
| KP4MD_22 | 20 Dec ~09:04, −5 dB | id44733631, 09:02, −19 dB, 37 dBm | +14 dB |

An excess of archive reports by itself does not prove the figure wrong or incomplete: the article does not disclose whether it plotted every report. Conversely, a partial overlay or a few agreeing features would not prove complete recovery of the publication's selected population. Here the stronger limitation is the combination of missing temporal counterparts and incompatible amplitudes among the temporal candidates under the checked, declared-power interpretations.

## Global Target-Active Gate audit

The gate is derived independently from the entire selected raw population, before distance filtering: a 120-second cycle is Target-active if KP4MD was reported by **any** receiver. This yields 179 active cycles. Receiver identities retain the complete callsign and locator. The distance condition is strictly below 5,000 km from the configured CM98 center at latitude38.5, longitude−121, using a 6,371 km sphere. Every VE6PDQ report passes that radius.

All 63 KP4MD reports survive: 62 Target-only and one endpoint of the joint pair. Of the 26 WB6RQN reports, only the endpoint of that joint pair survives; **25 are excluded because the Target was inactive globally**. Those excluded reports are nevertheless retained in `publication_archive_reports.csv` and are included in the graphical candidate search. Thus the mapping failure is not created by applying the gate first. The gate does explain why a completed conditional chart cannot stand in for a complete plot of the article's independent station reports.

The sole joint cycle is 20 December at 00:22 UTC, source ids44698904/44698905. Raw Target/Reference SNRs are −13/−15 dB at powers37/33 dBm. At 30 dBm they become −20/−18 dB, producing a same-cycle difference of **−2 dB**. Neither endpoint has a Figure 6 marker within the fixed ±4-minute allowance. This is an auditable processing example, not a reproduced publication result.

The archive contains **seven** WB6RQN reports between 16:00 and 23:00 UTC on the article's dates: four on19 December and three on20 December. All seven fall inside the plotted axis extent, and all are globally Target-inactive. Consequently, using the gated absence of WB6RQN reports in that interval to corroborate the article's dropout description would confuse software conditioning with published propagation evidence. The source article itself does not state this global gate.

## Date, endpoint and location checks

`publication_alternative_mapping_summary.csv` records bounded diagnostic checks of the published dates, ±1 calendar day, and swapped transmitter assignments. These checks are explicitly **unsupported alternatives**, not adjusted acceptance criteria. At the published dates, swapping endpoints gives only five blue-series and nine red-series temporal candidates; at any single checked common power baseline, at most one of those markers agrees in SNR. It does not provide a coherent swapped interpretation.

Moving dates back one day gives three blue and one red candidate-bearing markers with the published endpoint assignments, and no SNR agreement at any checked baseline. Moving dates forward gives three blue and no red candidate-bearing markers in the available capture. However, 15 blue and seven red shifted neighborhoods then lie outside the frozen capture, and cannot support rejecting a later-date dataset. The tables count these unavailable neighborhoods explicitly. No date shift is accepted; the source dates are legible and unchanged.

There is also an unresolved location detail. The article describes VE6PDQ as Edmonton, approximately1,750 km away, without a locator. Every archived report here says **DO34ir**, with stored coordinates approximately54.7290°N,113.2920°W; its distance from the configured CM98 center is approximately1,895.44 km. The configured coarse transmitter cell center is itself an approximation. This discrepancy is a provenance question for further investigation, not proof of a different receiver or an archive error. The available data do not establish why the publication and current archive disagree.

## Files, reproducibility and permissible test claims

| File | Meaning |
|---|---|
| `publication_features.json` | Unchanged independent source features, calibration and original readout tolerances. |
| `publication_markers.csv` | Unchanged 44-marker source readout. |
| `publication_mapping_candidates.csv` | Every one of the 18 primary temporal candidates, its normalization alternatives, gate/outcome and residuals; no confirmed-match label. |
| `publication_mapping_markers.csv` | Every marker, including all26 without candidates, candidate ids and agreement counts. |
| `publication_archive_reports.csv` | Every one of the89 VE6PDQ raw reports, raw coordinates/code/power/SNR, normalized values, date-scope flags, ungated and retained outcomes, and nearby marker ids. |
| `publication_alternative_mapping_summary.csv` | All12 bounded date/assignment/series diagnostics, including unavailable shifted neighborhoods. |
| `publication_mapping_summary.json` | Aggregate counts, declared rules and original source hashes. |

The scratch calculation reads only the unchanged marker CSV/feature JSON and raw reports converted from the original Parquet response. It imports no application code and reads no application-derived outputs. Its mapping arithmetic is simple enough for the regression to recompute independently from the committed raw CSV: exhaustive same-transmitter timestamp-window joins, declared-power normalization and explicit gate membership. The fixture's main manifest protects these publication files along with the archive-method reference.

Tests may verify the external identities, band, printed date axis, stated power choices, marker counts and fixed graphical tolerances. They may verify the audit's complete candidate enumeration and its negative findings, and independently verify the software's normalization, gating and pairing against raw reports. A test asserting that the audit still has zero amplitude matches is a reproducibility check of this recorded investigation, **not a scientific validation of the article's conclusions**.

Before claiming a reproduced Figure 6 result, obtain the author's original spreadsheet or another explicit account of its source population and transformation, reconcile dated markers under that documented rule, and account for missing and additional reports. A fitted vertical shift, enlarged time tolerance, silent endpoint/date swap, or selective omission of unmatched markers would not resolve this evidential boundary.
