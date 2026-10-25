# Milazzo selected-path verification data

This package accompanies the WSPRadar Milazzo guided demo. It preserves the small archive sample used to verify the two supplied reconstruction PDFs. It contains selected VE6PDQ-path evidence, not an all-stations WSPRadar export.

## Scope and source

- Band: 40 m, archived band code 7.
- Window: 2010-12-19 12:00:00 through 2010-12-20 20:00:00 UTC, inclusive in the saved query.
- Compared setups: Target KP4MD and Reference WB6RQN.
- RX records: VE6PDQ transmitting to KP4MD or WB6RQN.
- TX records: KP4MD or WB6RQN transmitting to VE6PDQ.
- Source: the public [WSPR.live archive](https://wspr.live/), queried on 2026-10-23. The exact SQL and reproducible GET URL are in `milazzo-public-archive-query.txt`.
- Historical source: Carol F. Milazzo / KP4MD (2011), [Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance](https://www.qsl.net/kp4md/wspr.htm).

The raw response contains 120 reports with distinct archive IDs: 44 RX-path reports and 76 TX-path reports. There are no duplicate reports within a compared endpoint, exact peer identity and cycle in this selected sample. These checks therefore do not test WSPRadar's behavior on duplicate-report cases.

The original publication labels Figures 6 and 7 in the opposite directions to those established by the matched archived transmitter and receiver fields. The guide follows the reconciled directions in the supplied comparison PDFs: Figure 6 is RX and Figure 7 is TX. Neither the source PDFs nor the raw records are altered in this package.

## Files

| File | Contents |
| :--- | :--- |
| `milazzo-public-archive-records.json` | Original API response, including column metadata and retrieval statistics. |
| `milazzo-public-archive-records.csv` | Readable version of the same 120 raw reports. |
| `milazzo-public-archive-query.txt` | Exact SQL and public query URL. |
| `milazzo-six-pair-ledger.csv` | All six accepted pairs, record IDs, reported SNRs and powers, and values on 30 and 37 dBm bases. |
| `milazzo-scope-summary.csv` | Counts and paired medians for the two RX identities and the one TX identity. |
| `milazzo-coverage-bin-ledger.csv` | The 33 identity-specific three-hour bin rows; the last bin ends at 20:00 UTC. |
| `milazzo-cross-locator-comparisons.csv` | The three additional RX comparisons a callsign-only match would admit. These are excluded from the defined exact-identity result. |

## Pairing and identity

In RX, match the same timestamp, band, remote transmitter callsign and full remote transmitter locator across KP4MD and WB6RQN reports. In TX, match the same timestamp, band, remote receiver callsign and full remote receiver locator across reports of KP4MD and WB6RQN. The selected records use WSPR cycle timestamps; no nearest-time matching, timestamp shift or interpolation is applied.

Locator capitalization is equivalent, so `DO34ir` and `DO34IR` denote the same identity. Preserve the difference between the four-character `DO34` and six-character `DO34ir`. The latter lies within the former, so the distinction here is reported precision, not evidence of movement or two physical stations.

The minimum qualifying count is one Joint Spot per station entry. This preserves all six accepted pairs for inspection. The PDFs specify a Reference correction of zero, all directions and solar states, peer distance less than 5,000 km, and special-callsign and moving-station exclusions off. No map-segment qualification value or all-station result is inferred from these documents.

## Power normalization and ΔSNR

For each report, with power in dBm and SNR in dB:

`SNR_at_30dBm = raw_SNR + 30 - reported_power_dBm`

`SNR_at_37dBm = raw_SNR + 37 - reported_power_dBm`

`Delta_SNR = Target_SNR_at_30dBm - Reference_SNR_at_30dBm`

The same ΔSNR is obtained at 37 dBm because the common basis shifts both sides equally. No additional Reference correction is applied.

All RX-path reports specify VE6PDQ transmitting at 37 dBm. This is the remote transmitter's power, not a receiver power setting. In the TX-path records, KP4MD specifies 37 dBm and WB6RQN 33 dBm throughout.

The sole TX pair, 2010-12-20 00:22 UTC, has raw SNRs −13 and −15 dB. At 30 dBm these become −20 and −18 dB, giving −2 dB. Raw subtraction alone would incorrectly treat the different reported powers as comparable and give +2 dB.

## Expected results

All report totals below refer to retained observations; they are not transmission-attempt counts or absolute decoding probabilities.

| Scope | Target-only | Joint | Reference-only | Target reports | Reference reports | Observed union units | Combined reports | T/R factor | Paired median |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| RX, VE6PDQ / DO34ir | 8 | 3 | 5 | 11 | 8 | 16 | 19 | 1.375 | +8 dB |
| RX, VE6PDQ / DO34 | 18 | 2 | 3 | 20 | 5 | 23 | 25 | 4 | +12 dB |
| RX, both identities pooled | 26 | 5 | 8 | 31 | 13 | 39 | 44 | 2.384615… | +8 dB |
| TX, VE6PDQ / DO34ir | 56 | 1 | 18 | 57 | 19 | 75 | 76 | 3 | −2 dB |

The RX individual differences sort to 7, 7, 8, 17, 22 dB. Their pooled median is +8 dB. The two identity medians are +8 and +12 dB; their median would be +10 dB, a different weighting of the evidence. The guide's +8 dB pooled result must not be labelled a station-balanced map result.

## Count arithmetic and ΔDecode

For Joint `J`, Target-only `T` and Reference-only `R` observed units:

- Target reports `A = J + T`.
- Reference reports `B = J + R`.
- Observed union units `= J + T + R`.
- Combined endpoint reports `= 2J + T + R = A + B`.
- T/R factor `= A / B` when `B > 0`.
- Symmetric ΔDecode percentage `= 100 × (A - B) / (A + B)` when `A + B > 0`.

The two pooled examples therefore give approximately +40.9% for RX (31/13, Target 2.38×) and +50% for TX (57/19, Target 3×). The symmetric percentage is not the conventional percentage increase over Reference and is not a success probability.

Target-only bins have an infinite T/R ratio and +100% symmetric ΔDecode; Reference-only bins have a zero T/R ratio and −100%. No observations on either side means the ratio and percentage are undefined, not parity. The PDF's right-hand axis names the favored side using fold labels.

Decode counts are observed at the actual reported powers and schedules. Power normalization of SNR does not normalize reception counts or recreate missing reports.

## Checks that expose the matching rules

Ignoring the RX locator would admit three cross-locator comparisons with differences +5, +15 and +24 dB. That produces eight pairs and a pooled median of +11.5 dB. The endpoint report totals remain 31 and 13, but the Joint/one-sided classification and number of union units change. This diagnostic does not establish that merging identities is physically justified.

On 2010-12-20, the TX reports at 10:34 (KP4MD) and 10:36 (WB6RQN) have equal normalized SNR but different cycle timestamps. They are not a Joint Spot. Their archive IDs are 44741687 and 44741893.

For the RX DO34ir identity, 2010-12-19 15:00–18:00 contains one report on each side and zero Joint Spots. Equal bin totals do not imply simultaneous observations.

## What this verifies

An independent grouping and calculation from these archived rows reproduces the six accepted pairs, identity-specific counts, pooled counts and all 33 identity-specific temporal bin rows in the supplied PDFs. It checks these selected examples' identities, arithmetic and count reconciliation.

It does not independently establish every publication-marker-to-archive association, validate the full software across all cases, establish the broader all-station maps, or isolate antenna gain from installation and operating differences. The PDFs' 44 and 47 paper-anchor claims should not be treated as complete marker audits supplied by this data package.
