# Zander Figure 4: external histogram reference

Source: Jens Zander, *Simple HF antenna efficiency comparisons using the WSPR system*, [arXiv:2209.08989v1](https://arxiv.org/abs/2209.08989), 19 September 2022. Figure 4 is on PDF page 4; Section V spans pages 4-5. The source PDF SHA-256 is recorded in `paper_features.json`. The original 640 x 480 embedded raster is preserved as `paper_figure4.png`.

An independent reviewer read the paper and its images without inspecting the WSPRadar demo, archive rows or application results. The source features and pixel tolerances were frozen at 2026-09-24 15:00:52.639708 UTC. Integration choices in `comparison_policy.json` and their hashes in `frozen_inputs.json` were recorded before the first production-replay comparison. Expected values and tolerances are not fitted to WSPRadar.

## Paper evidence used by regression

Figure 4 prints mean -6.8 dB and sigma 3.5 dB. Page 5 calls sigma an estimated sample standard deviation, without giving its denominator convention. The test uses the conventional nearest-decimal display intervals [-6.85, -6.75] dB and [3.45, 3.55] dB; these are readout/rounding bounds, not confidence intervals. Archive expectations separately define the sample standard deviation with denominator n-1.

The source histogram is consistent with ten equal-width 2.1 dB bins between -17 and +4 dB. Pixel-calibrated bar heights integrate to approximately 1.00082, supporting density normalization even though the y-axis has no normalization label. Readout tolerances are +/-0.10 dB for visible boundaries and +/-0.0005 per dB for heights, approximately 1.5 source pixels. The final two bars have equal height and no visible interior seam, so the regression conservatively combines them into one 4.2 dB region. It checks all nine visibly distinguishable regions:

| Nominal interval, dB | Source density per dB |
| --- | ---: |
| -17.0 to -14.9 | 0.00585905 |
| -14.9 to -12.8 | 0.02301898 |
| -12.8 to -10.7 | 0.04600681 |
| -10.7 to -8.6 | 0.07741272 |
| -8.6 to -6.5 | 0.09457265 |
| -6.5 to -4.4 | 0.08906852 |
| -4.4 to -2.3 | 0.09748660 |
| -2.3 to -0.2 | 0.03143706 |
| -0.2 to +4.0 | 0.00585905 |

The actual Joint-Spot recipe provides 1 dB counts. The tests rebin those counts at the nominal source boundaries and calculate `density = count / (total sample count * bin width in dB)`. Bins are left-inclusive/right-exclusive except the final upper edge, which is included. The original-image boundary uncertainty supports the nominal reconstruction; the tests do not move edges or optimize them against archive values. All sample counts must remain represented; out-of-span evidence cannot be silently discarded and renormalized. Percent-of-sample plot bars and density bars are different presentations of these counts.

The source-only extractor also found that, conditional on ten equal bins, density normalization and an integer sample count in the paper's approximate 150-200 range, 166 samples with counts `2,8,16,27,33,31,34,11,2,2` fit uniquely at the declared readout tolerance. This is a useful independent consistency observation, not an exact sample count printed in the paper. The paper test does not require that inferred count; the separate archive fixture independently establishes the demo's exact population.

## Interpretation and scope

The paper establishes 14 MHz, Gotland JO97, the short Difona HF-P1 versus Hy-Gain AV620 setup, equal stated transmitter power, same-receiver/same-cycle comparison and measured-minus-reference sign. It does not supply Experiment A's exact date, time, callsigns, complete locators, raw data or processing script. The existing demo supplies those selectors. Matching the published distribution corroborates the reconstruction but does not independently authenticate all experiment provenance.

There is an unresolved notation ambiguity: Figure 4 calls its samples Delta S_k, while Equation 6 defines that quantity as an average over joint receivers in a slot. The experimental prose also describes 150-200 valid reports from 15-35 receivers in roughly one hour. The regression explicitly tests the installed demo's pooled receiver-cycle interpretation against the figure; it does not silently treat that interpretation as unambiguously specified by the paper.

The paper's roughly 1,000 source reports, 150-200 valid reports and 15-35 receiver descriptions are approximate context across both experiments. Our independent archive reconstruction has 731 source reports, 166 joint pairs and 37 paired receiver identities; do not turn those approximate descriptions into exact oracle counts. Likewise, the prose about a bulk of 14 MHz paths at 1,500-2,000 km and a southwest concentration supplies no exact geographic pass/fail distribution. The archive audit records 75/166 pairs in that distance interval and 147/166 in the southwest quadrant; these diagnostics are not used to tune selection or tolerances.

The orange fitted normal curve is not additional independent measurement data and does not establish Gaussianity, independent samples or a confidence interval for antenna efficiency. The reference validates the plotted path-sampled SNR distribution, not direction-independent antenna gain or the paper's inferential accuracy claim.

`source_digitization.py` preserves the original extraction code. To reproduce its source-only calculation, place the arXiv PDF beside it as `2209.08989v1.pdf` in a separate review directory and run it with NumPy, Pillow and pypdf; it writes the original review filenames. It is not imported by the regression suite. Preserve all files listed in `frozen_inputs.json` unchanged after first comparison; later verification notes may be added separately.

## Observed comparison, 2026-09-24

All nine visible regions and both printed statistics matched on the first comparison, without changing source annotations, selectors, bins or tolerances. `comparison_observed.json` records the observed counts and densities separately from expected paper features. The largest absolute density residual is 0.0001413812 per dB, below the source-only allowance of 0.0005 per dB.

The pooled receiver-cycle distribution gives mean -6.78313253 dB and sample standard deviation 3.51463845 dB. As diagnostics of the notation ambiguity, averaging within each of the 12 joint cycles first gives a mean of cycle means of -6.71214145 dB and a sample standard deviation of 0.97705122 dB, while the mean of receiver medians is -6.05405405 dB. Those are different distributions. The close pooled histogram match supports the chosen reconstruction; it does not prove the original author's implementation. The regression also rejects substituting either station medians or cycle means for the pooled observations.

The first complete new-module run exposed only a test-setup omission of outcome-series labels in the renderer call; all scientific and paper comparisons passed. Supplying the required labels resolved that setup failure. Focused integration with the Griffiths reference, comparison-evidence, statistics and runner tests passed 138 tests with the three existing Griffiths expected failures and one existing Matplotlib warning. Native ClickHouse, live-provider and full-suite execution were not performed for this isolated addition.

## Comparison graphics and vector PDF (2026-09-25)

`figure4_histogram_overlay.png` and `figure4_histogram_overlay.pdf` retain the same A-B-C layout: original Figure 4, reconstruction in the paper's coarse bins, and the WSPRadar 1 dB percent-of-sample histogram. The residual comparison stays below panel B. The PDF contains vector bars, lines, labels and residuals; only the original publication panel is an embedded raster. It is rendered directly from the Matplotlib figure, not from the completed PNG.

Regenerate both formats from the repository root into a review directory:

```powershell
.\.venv\Scripts\python.exe -B scripts/build_zander_fig4_comparison.py --output-directory tmp/zander_fig4_comparison_candidate
```

The builder verifies all 166 pairs, the production 1 dB histogram counts and percentages, and the coarse-bin residual allowance before rendering. PDF export does not change frozen paper evidence, binning policy or expected numerical results.
