# Multiple reports within one cycle: SNR reduction policy review

Review date: 2026-09-24. Initial review status: **median is a proposed policy, not an implemented change**. This review changes neither runtime calculations nor existing regression expectations.

Current status: **accepted decision: retain strongest SNR**, recorded on 2026-09-24 in the final section below. The original proposal assessment, sensitivity results and conditional implementation requirements are preserved as the decision's evidence trail; they do not describe a pending runtime change.

## Recommendation and evidence unit

Retain one detection outcome per existing cycle/path identity and one paired Delta SNR when both endpoints are present. Several reports of the same transmitter in the same cycle do not establish several independent propagation observations. Do not expand them into an all-combinations join for the primary analysis.

A median is a coherent summary of the typical reported SNR and reduces sensitivity to an isolated extreme report. However, replacing the maximum is a change in the quantity being estimated, not an established correction. The maximum represents the strongest retained normalized report; the median represents the center of the retained report distribution. Neither identifies the intended physical signal when reports can refer to different spectral components or receiving systems.

**Recommendation:** retain the current maximum policy while reviewing this proposal and the frequency-separated reports. A switch to median should explicitly choose the typical-report interpretation and acknowledge its limits. Matching a publication more closely is insufficient grounds for choosing the reducer. An advanced setting is not necessary to resolve this review and would not resolve the ambiguity in the input observations.

## What the reported example establishes

The supplied WSPR Rocks screenshot shows four G3ZIL reports for HB9MHB / JN36su on 2017-04-16 at 12:46 local time. Their frozen-source timestamps are 10:46 UTC. The reported frequencies and SNR values are:

| Frequency, MHz | Reported SNR, dB |
| --- | ---: |
| 7.040194 | -27 |
| 7.040125 | -15 |
| 7.040094 | -5 |
| 7.040033 | -26 |

These frequencies span 161 Hz. They are distinct frequency reports, not identical copies of one row. The frozen source has two corresponding G4HZX reports, -18 and -8 dB. All six reports use 43 dBm reported transmitter power, so normalization shifts both receivers' SNR values by the same amount and leaves their difference unchanged.

| Reducer | G3ZIL reported SNR summary | G4HZX reported SNR summary | G3ZIL minus G4HZX |
| --- | ---: | ---: | ---: |
| Maximum | -5 dB | -8 dB | +3 dB |
| Median | -20.5 dB | -13 dB | -7.5 dB |

If the weaker reports are unwanted replicas of one stronger signal, taking their median can move away from that signal. Conversely, when reports are repeated noisy estimates of the same intended signal, selecting the maximum can favor an endpoint with more estimates. Those are conditional explanations, not diagnoses of this historical cycle. The screenshot and captured source do not establish the physical cause or which component should be paired across receivers.

The [wsprd manual](https://manpages.debian.org/testing/wsjtx-improved/wsprd.1.en.html) describes decoding spectral peaks and possible duplicate decodes from one signal, with frequency-based duplicate checking. This documents a relevant mechanism; it does not establish the exact behavior of the screenshot's 1.7.0-rc1 decoder. The [WsprDaemon FAQ](https://wsprdaemon.readthedocs.io/en/master/FAQ.html#how-does-spot-merging-work-with-multiple-receivers) also documents merging multiple receivers by retaining the best SNR. Thus an archive's report population can already reflect upstream selection. These sources do not show that either mechanism caused this example.

## Precise candidate median contract

For Reference Benchmark, within the selected band, mode policy, endpoints and 120-second cycle, preserve the existing transmitter/peer identity including its full locator. For each endpoint separately:

1. Normalize each eligible report using the existing power and configured SNR corrections. For the frozen examples, this is `normalized_snr_db = snr - power + 30`.
2. Take the median of those normalized report values. For an even number of reports, average the two central values.
3. Form one paired difference: `median(target_reports) - median(reference_reports)`.

Do not take a median over all pairwise Target/Reference report combinations: that is generally a different statistic. Preserve fractional-dB values through subsequent aggregation. The existence of an endpoint's reports determines detection; the SNR reducer does not determine whether it was detected.

Changing only this reducer must preserve eligible cycles, path identities, Hit/Miss/Target-only outcomes, joint-observation counts, coverage denominators and count-based support gates. SNR summaries, distributions, maps and outlier candidates can change.

A median is not invariant to repeating only some input records. Before adoption, distinguish accidental replay of the same archive record from separate decoder reports using reliable provenance where available. Do not identify replay duplicates solely from equal SNR values. Retain raw report counts and, where available, frequency and receiver/decoder provenance for diagnosis. The current frozen Parquet source contains report IDs but does not contain frequency, drift or decoder-version fields; the four example frequencies come from the supplied screenshot.

## Measured sensitivity on the frozen demo populations

The comparison holds each installed demo's selected paired identities fixed. It recomputes both endpoint maxima and medians directly from `source_rows.parquet`, without WSPRadar calculation imports. Every recomputed endpoint maximum matches the stored endpoint value exactly. The stored paired table supplies the retained population and the maximum-policy cross-check, not the median expectations or an independent proof of geographic selection.

| Quantity | Figure 3, April 1-30 | Figure 6, selected April 5-7 interval |
| --- | ---: | ---: |
| Retained paired units, both policies | 57,767 | 6,459 |
| Pairs with multiple reports at either endpoint | 211 | 11 |
| Paired differences changed by median reduction | 204 (0.3531%) | 10 (0.1548%) |
| Strict positive-to-negative or negative-to-positive changes | 93 | 6 |
| Changes between zero and a nonzero difference | 11 | 0 |
| Largest absolute change to one paired difference | 38 dB | 16.5 dB |
| Pooled mean, maximum to median policy | 6.549085 to 6.512698 dB | 5.116582 to 5.106828 dB |
| Pooled median, maximum to median policy | 7 to 7 dB | 5 to 5 dB |
| Pooled Q1, maximum to median policy | 3 to 2 dB | 1 to 1 dB |
| Pooled Q3, maximum to median policy | 10 to 10 dB | 9 to 9 dB |
| Pooled minimum, maximum to median policy | -24 to -31 dB | -17 to -17 dB |

The Figure 3 folded medians at UTC hours 11 and 12 change from +8 to +7 dB; its other hourly medians do not change. All 24 Figure 6 hourly medians remain unchanged. Small affected fractions therefore do not imply that every summary is stable: the Figure 3 lower quartile changes by 1 dB because discrete observations move across the quartile's rank boundary. Individual paired differences and tails can change substantially despite stable pooled medians.

The April 13 Figure 3 daily mean changes from 8.141611 to 7.929194 dB. The independently digitized Figure 4 interval remains approximately [7.744731, 7.860115] dB. Median reduction moves toward this anchor but still falls outside it. It does not remove the evidence of a different report-weighting interpretation in the publication. The paper's exact duplicate-handling query remains unknown.

These are numerical sensitivity results, not a production implementation or a replay of the paper-feature tests under a new policy. Count invariance follows here from fixing the selected population; a future implementation must additionally demonstrate it through the actual analysis pipeline.

### Reproduction and source identity

The two source directories are:

- [Figure 3 temporal fixture](../tests/regression/reference_fixtures/griffiths_fig3_temporal_v1/README.md).
- [Figure 6 diurnal fixture](../tests/regression/reference_fixtures/griffiths_fig6_diurnal_v1/README.md).

Group source reports by `(floor(UTC_epoch_seconds / 120), tx_sign, tx_loc, rx_sign)`. Convert signed SNR and power fields to a sufficiently wide numeric type before normalization. Calculate each group's maximum and median, then select the identities in `expected_paired_rows.parquet`. Subtract the endpoint summaries and calculate the statistics above. Quartiles use linear interpolation at index `(n - 1) * p`; folded-hour medians pool paired observations by UTC hour. Preserve each fixture's declared interval, including the Figure 6 exclusive end at 2017-04-07 23:45 UTC.

The calculations were performed with pandas grouping and independently cross-checked using dictionary grouping, Python `statistics.mean` / `statistics.median`, and explicit sorted-sample quartiles. Both calculations matched for all baseline paired differences, changed-pair counts, strict sign reversals and pooled means/medians/quartiles. Neither executed production SQL.

SHA-256 input identities:

| Fixture | File | SHA-256 |
| --- | --- | --- |
| Figure 3 | source_rows.parquet | `b15d2c30540f91150da908c6eeb59afd44463f6f345ba3dd5e61624e5de530dd` |
| Figure 3 | expected_paired_rows.parquet | `fd5538a4c9f6cafc92592f6bd9f8e98b66f0834b27b43f60d9ce851cd9626fc8` |
| Figure 6 | source_rows.parquet | `cce5cc7bc0ab1cc5c8d352f11f4087ae487592874bbcc983b1b26ab5aefe0b64` |
| Figure 6 | expected_paired_rows.parquet | `df10db992a7dae591de2fe7247f2daff94cb5269a630bd3535166fe800feff12` |

## Existing methods require separate treatment

| Method | Current reduction | Implication of adopting the candidate |
| --- | --- | --- |
| Reference Benchmark, RX and TX | Maximum normalized SNR at each endpoint within the cycle/peer group | Change both endpoints symmetrically. |
| Local Median Benchmark | Target maximum; median within each local contributor, then median across contributor stations | Evaluate changing the Target summary while preserving equal contributor weighting. Do not pool all local reports into one median. |
| Performance | Binary detection flags and maximum normalized Target SNR per opportunity; later summaries use hit rows | Keep detection/outcome counts unchanged; successful-SNR summaries may change. Audit the additional post-fetch maximum reduction. |
| Sequential A/B | Per-side micro-medians within each scheduled comparison pair | Already uses medians over a different unit. A new per-cycle stage would alter weighting and must not be introduced implicitly. |

The implementations reviewed are [analysis_runner.py](../core/analysis_runner.py), [opportunity_engine.py](../core/opportunity_engine.py), [compare_engine.py](../core/compare_engine.py), and [evidence_data.py](../ui/inspector/evidence_data.py). Existing Local Median and Sequential A/B medians do not establish that every stage should use the same reducer or grouping unit.

## Requirements if the policy is adopted

1. Define the intended report population and its physical interpretation. Use frequency/provenance to investigate the disputed cycle; do not infer independent transmissions from repeated callsign/time rows.
2. Add hand-calculated cases for odd/even report counts, singleton groups, unequal endpoint multiplicities, differing reported powers, missing endpoints, replay duplicates, and fractional medians. Verify normalization before reduction and endpoint reduction before subtraction.
3. Execute the actual aggregation SQL against frozen source rows and compare with independent expectations. A post-fetch replay of previously aggregated maxima cannot test a median SQL implementation.
4. Verify unchanged opportunity identities, outcomes and support counts through production paths, then compare complete temporal/folded profiles, quartiles, densities and downstream outlier evidence. Preserve the paper-derived features and tolerances; do not adjust external anchors to make the new method pass.
5. Review changes to the two archive-derived baselines explicitly. Keep the distinction between an intentional method change and an unexpected regression. Passing paper-feature checks would provide limited corroboration, not proof that median is the physically correct reducer.
6. Record the policy in result provenance and invalidate incompatible processed caches. If a selectable policy is introduced, make it validated scientific configuration and include it in saved settings, analysis/cache identity and exports. A single fixed policy change still requires an explicit method/version transition.
7. Update the English and German scientific manuals and regenerate README only after adoption. Run the full regression suite for a scientific calculation change. This review alone does not authorize describing median as current runtime behavior.

## Accepted decision: retain strongest SNR (2026-09-24)

The user accepted retaining the strongest qualifying normalized SNR wherever the current methods use it. Multiple reports still contribute one detection outcome or paired observation per existing cycle/path identity. No mean/median alternative or advanced setting is introduced, and no runtime calculation or fixture expectation is changed.

When weaker reports are transmitter/receiver replicas, spurious components or secondary decodes, their mean or median has no established interpretation as the main signal's SNR. Maximum selection deliberately represents the best observed reception and prevents weaker additional reports from lowering that value. WsprDaemon's documented best-SNR reporting when merging receivers provides a compatible reporting precedent. Neither this precedent nor maximum selection establishes which historical component was the intended signal or whether both endpoints selected the same component. The existing caution about unequal receiver/reporting behavior remains applicable.

For the example's G3ZIL reports, retain -5 dB rather than the arithmetic mean -18.25 dB or median -20.5 dB, before the common power-normalization adjustment. Together with G4HZX's strongest report of -8 dB, the retained paired difference is +3 dB. This illustrates the selected best-report interpretation; it is not a physical diagnosis of the weaker reports.

The method boundary is unchanged: Performance and simultaneous fixed-Reference Benchmark retain their maximum-based SNR values; the Local Median Target retains its maximum while Reference contributors retain their within-identity medians followed by a median across identities; Sequential A/B retains per-side medians within scheduled comparison pairs. Subsequent medians and IQR across retained observations remain valid descriptive summaries and are not replaced by maxima.

The rationale and scope are documented in Section 7.2 of both authoritative manuals, with the WsprDaemon FAQ added to Ref-11 and the English README regenerated from its source. The earlier recommendation and median-candidate sections above remain historical review material, superseded as an action proposal by this accepted decision.

### Meaning for the Figure 3 and Figure 6 reference comparisons

Figures 3 and 6 are suitable external regression baselines for the temporal patterns and density features covered by the installed tests. Together with the independent archive calculations, they provide a solid baseline for those parts of WSPRadar. Multiple-report cases are rare in the selected populations: 211 of 57,767 Figure 3 pairs (about 0.37%) and 11 of 6,459 Figure 6 pairs (about 0.17%) have multiple reports at either endpoint. They do not undermine the main patterns used for validation. The specific tail and daily-mean differences remain separately documented exceptions, so the unaffected paper-derived features remain firm regression checks.

The references provide selected external agreement and an explained difference in evidence handling, not complete numerical reproduction of both figures. The [Figure 3 discrepancy record](../tests/regression/reference_fixtures/griffiths_fig3_paper_v1/known_discrepancies.json) shows that retaining all same-time/transmitter report combinations reproduces 38 witnesses in the unchanged negative-tail region and all five selected Figure 4 daily-mean anchors. WSPRadar instead selects one strongest-report difference per cycle/path. This supports a report-selection and weighting explanation for the selected disagreement; it does not recover the authors' exact query or prove that weaker reports are physical artifacts.

This difference arises before chronological binning or UTC-hour folding. Calling it a folding artifact would conflate report pairing with time aggregation. The two Figure 3 tail comparisons (3-hour and 24-hour representations) and April 13 mean comparison remain strict expected failures, with all source annotations and tolerances unchanged. They remain explicit boundaries of paper agreement, not passed reproduction tests.

The [Figure 6 external comparison](../tests/regression/reference_fixtures/griffiths_fig6_paper_v1/README.md) agrees with the selected density-feature positions across the declared smoothing cases, qualitative density ordering and three isolated point witnesses. Its exact medians and IQR are separately checked against independently reconstructed archive expectations; the paper does not supply those exact statistics. Equality of complete contours, distributions and exact source populations is not established, and production SQL execution remains outside these offline replays. These comparisons have not demonstrated a serious computational defect, but they do not close every scientific validation gap.
