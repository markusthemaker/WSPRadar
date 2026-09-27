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

`figure4_histogram_overlay.png` and `WSPRadar_Demo_Zander_Figure4.pdf` retain the same A-B-C layout: original Figure 4, reconstruction in the paper's coarse bins, and the WSPRadar 1 dB percent-of-sample histogram. The residual comparison stays below panel B. The PDF contains vector bars, lines, labels and residuals; only the original publication panel is an embedded raster. It is rendered directly from the Matplotlib figure, not from the completed PNG.

Regenerate both formats from the repository root into a review directory:

```powershell
.\.venv\Scripts\python.exe -B scripts/build_zander_fig4_comparison.py --output-directory tmp/zander_fig4_comparison_candidate
```

The builder verifies all 166 pairs, the production 1 dB histogram counts and percentages, and the coarse-bin residual allowance before rendering. PDF export does not change frozen paper evidence, binning policy or expected numerical results.

## Production-derived comparison inputs (2026-09-25)

The comparison now follows the shared [reference comparison contract](../README.md). Its plotted reconstruction and WSPRadar histogram start with `zander_experiment_a_v1/source_rows.csv` and the frozen demo configuration, then execute the current generated SQL, production post-fetch filters, map preparation, Inspector identity selection, same-cycle pairing and Joint-Spot histogram recipe. `_calculate_run` in `test_zander_experiment_a_reference.py` is the reusable offline entry point shared by the regression and figure builder. SQL runs through the bounded SQLite adapter, not a live provider or native ClickHouse engine; the HTTP/cache path is outside this check.

Panel B rebins the actual production 1 dB histogram counts into the paper's fixed coarse regions, then divides by the complete sample count and region width. This is a paper-style presentation, not a replacement scientific pipeline. Panel C uses the production histogram centers and counts as percent-of-sample bars. Generated marker values, statistics and histogram heights never come from `expected_*` files. Those independent files are opened only by a separate verification step that can reject the computed figure before rendering. The numerical reconstruction still has 166 Joint pairs and production-histogram mean -6.78313253 dB. The separately labeled review sample standard deviation, 3.51463845 dB, is a supplemental paper-comparison calculation with denominator n-1 over those actual production pairs; it is not supplied by the WSPRadar histogram recipe.

`figure4_comparison_provenance.json` records pipeline stages, separate source and assertion-only hashes, the generated-query hash, observed sample/statistics and display rules. New regression cases forbid expected-result reads during plot-input construction, change a raw-report SNR, change a production SQL normalized-SNR result, and corrupt an expected histogram. The first two mutations must alter the calculated plotted distributions and fail verification; corrupt expectations must reject the comparison without modifying its computed values. Scientific source rows, external paper annotations, tolerances and independent expected results remain unchanged.


### Demo PDF filenames (26 September 2026)

Embedded demo PDFs use `WSPRadar_Demo_LeadAuthor_FigureX.pdf`, with
`_diagnostic` before `.pdf` for a diagnostic. PNG filenames are unchanged.
The PDF content is byte-identical to the previously named output. Existing
generation hashes describe that original rendering, not the filename update.

### Demo #6 presentation review (26 September 2026)

The subsequent style review follows `config/demo_pdf_style.md`. The centered
header gives the printed paper title, author, linked arXiv reference, Figure 4
subtitle and demo selectors. The white page uses DejaVu Sans, readable panel
headings and explanatory text, separate legends centered beneath Panels B and C,
and the standard WSPRadar credit. Physical dimensions are 24 by 14.4 inches; the previously
reviewed 5:3 aspect ratio is unchanged.

Panel A retains the complete original raster. Panel B retains the unchanged
paper-style rebinning and digitized-bar comparison. Panel C now retains the
actual right-hand axis produced by `render_segment_insight_export_figure`,
with the common white-paper export theme: native blue bars, red dashed median,
mean annotation, 1 dB bins, percentages, linear axes, limits and tick policy.
Its median key moves into the legend below Panel C, and its exact current English
figure/axis labels come from `i18n.py`. Font sizing and panel placement are
presentation adjustments only. The residual diagnostic remains below Panel B.

Calculated display values have at most two decimal places. The reconstructed
mean and sample standard deviation are displayed to one decimal place as -6.8
and 3.5 dB, following the annotated review. Small residuals use units of
`10^-4 per dB`: the maximum is displayed as 1.41, preserving its meaning instead
of rounding it to zero. The shaded residual band still represents the original
readout allowance of +/-5.00 in those units; its explanatory caption was removed
as requested. Native one-decimal summary formatting and the source raster's
printed statistics are retained. Full numerical precision remains in the
provenance and independent reference files; the arXiv identifier is unchanged.

The public page explains Joint Spots, the Target-minus-Reference sign, density
versus percent-of-sample bars. The reconstruction limits remain documented above.
Technical SQL-adapter and assertion-only provenance remains documented above and in
`figure4_comparison_provenance.json`. The novice demo description now uses the
current `Segment Inspector -> Benchmark Evidence` route and distinguishes the
Joint-Spot histogram from the equally weighted Station Medians histogram.
No demo settings, source observations, frozen paper annotations, binning policy
or independent numerical expectations changed in this presentation review.

The annotated review also removed the statements about all nine regions meeting
the allowance and the meaning of sample spread, plus the bottom LIMIT and SOURCE
lines. The linked publication title and citation in the header, the READ line,
the standard WSPRadar credit and the residual diagnostic are retained. Full
precision calculations and the demo description are unchanged by these PDF edits.

The reconstruction now labels its sample standard deviation `Sample σ` to match
the paper's symbol for an estimated sample standard deviation. This is a notation
change only: the reconstruction still uses `ddof=1` (denominator `n-1`), and the
paper's unspecified denominator convention remains an evidence limitation as
documented above.

### WSPRadar header revision (2026-09-27)

The Figure 4 PDF now begins with **WSPRadar.org reconstruction & comparison**, followed by the approved descriptive title **SNR differences between a short portable vertical and a reference vertical**. Explicit **Referenced publication:** and **Source figure:** lines attach Zander's authorship, the publication title and Figure 4 reference to their source; a **Demo:** line retains the Experiment A comparison context. Presentation-only records in `config/demo_pdf_headers.py` and the shared `scripts/demo_pdf_header.py` helper own this hierarchy and identify WSPRadar as the comparison author in PDF metadata. This supersedes the earlier paper-title-first header description while preserving its review history. Source evidence, numerical expectations, scientific calculations and all body coordinates remain unchanged.

The subsequent spacing refinement moves only the source-figure line downward, giving the publication, source-figure and demo lines equal baseline gaps of 25.0072 pt. All wording, font sizes, title positions, publication/demo endpoints and figure body are retained.

### Installed demo window alignment (2026-09-27)

The PDF's **Demo:** line now shows the installed Experiment A window, **09:45-10:30 UTC**. The archived reconstruction continues to use its frozen **09:30-10:30 UTC** configuration. A production replay checks that the narrower installed window retains exactly the same selected SQL rows, processed observations, station results and all **166 Joint Spots**. This header correction changes neither the plotted evidence nor the frozen source configuration, independent expectations, paper extraction, or numerical provenance.
