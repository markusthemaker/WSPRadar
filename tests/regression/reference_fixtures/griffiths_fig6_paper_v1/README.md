# Figure 6 external density reference

This fixture contains expectations extracted from the publication, separately from the archived WSPR reports and exact numerical regression baseline. Its tests compare the current production folded UTC-hour density grid with paper-derived feature regions. No application result supplied the expected Delta SNR coordinates, contour boxes or comparison tolerances.

## Source and extraction

[Griffiths and Squibb, Improving HF band SNR from analysis of WSPR spots, Practical Wireless, October 2017](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf), printed pages 25-26, Figure 6, plots G3ZIL minus G4HZX for April 5-7, 2017. The paper describes negative nighttime density concentrations, positive daytime advantage and morning/evening spot-density peaks with fewer midday spots.

`paper_figure6.png` is the original 1,382 by 908 pixel Figure 6 raster extracted from page 3's embedded `Im1.tif` in the user-supplied PDF. Its CMYK colors were converted to RGB for inspection; no resizing, cropping or geometric transformation was applied. The PDF SHA-256 is recorded in `paper_features.json`. The PDF itself is not required at test time.

Pixel calibration is x=119 to 1366 for 0 to 24 UTC hours, and y=22 to 792 for +25 to -15 dB. Accordingly, one pixel represents approximately 0.01925 hour horizontally and 0.05195 dB vertically. The paper's fractional-day axis is converted to UTC hours, preserving its stated midnight wrap.

The primary reviewer selected the innermost clearly traceable closed contour spanning at least one planned comparison cell in both axes: 1 hour and 1 dB. The very small innermost night loops cannot meet that resolution rule, so their next enclosing closed contours are used. These are bounding boxes of density features, not probability intervals or quantiles.

| External feature | Source box, x min/max; y min/max (pixels) | Source UTC extent | Source Delta SNR extent |
| --- | --- | --- | --- |
| Early-night negative branch | 138/226; 519/595 | 0.366-2.059 h | -4.766 to -0.818 dB |
| Morning positive branch | 482/563; 376/413 | 6.986-8.545 h | +4.688 to +6.610 dB |
| Strongest evening positive island | 1047/1158; 355/446 | 17.860-19.997 h | +2.974 to +7.701 dB |
| Late-night negative branch | 1268/1343; 540/579 | 22.114-23.557 h | -3.935 to -1.909 dB |

The fixed search slices [00,03), [06,09), [18,21) and [21,24) UTC follow the printed three-hour tick spacing. The mode search scans the complete available Delta SNR axis before considering any paper acceptance box. Multiple vertical modes may coexist, particularly during the morning and late evening; a median or a global vertical mode cannot represent every visible branch.

## Independence and uncertainty

The primary annotation task read the source PDF and image without consulting archive result tables. That reviewer had earlier seen WSPRadar results, so this is a retrospective external validation, not a blinded study or preregistration. A second reviewer received only the source image with no previous task context. Its independent axes and resolved daytime boxes agreed within approximately four pixels; it also flagged the tiny late-night inner loop as ambiguous. Both reviews support using the larger resolvable enclosures for sub-bin night features.

The primary annotations retain their original +/-3-pixel readout estimate. Before the first comparison, the integration policy adopted the larger +/-4-pixel estimate supported by the independent review for resolved contours. Tests calculate bounds from source pixels, then add this raster allowance and the actual histogram's half-cell localization allowance: +/-0.5 hour and +/-0.5 dB. The total allowance on each side is therefore about 0.577 hour and 0.708 dB. The contour box width remains an externally read feature extent; it is not an additional fitted tolerance.

No allowance is added for the undocumented original smoothing method. Smoothing sensitivity is examined separately. The source coordinates and policy were frozen and hashed before the first comparison performed for this external fixture. The observed comparison must never be used to move a paper box, change a bandwidth or widen an acceptance interval.

## Executable comparison

The companion `../../test_griffiths_temporal_reference.py` obtains the actual production folded count grid, hour centers and Delta SNR edges from the existing Figure 6 replay. It does not use the archive fixture's expected medians or expected density CSVs as external reference inputs.

1. Require a 1-hour by 1-dB grid and retain pooled observation counts; do not equalize stations, dates or hour totals.
2. Apply a separable discrete Gaussian to the complete grid. Each kernel is normalized and truncated at `ceil(3*sigma/bin_width)`. UTC time wraps periodically; SNR uses zero padding without edge renormalization. The nominal comparison uses sigma=1 hour and 1 dB. All nine combinations of 0.75, 1 and 1.25 in those respective units are mandatory sensitivity cases. This is an explicitly selected comparison estimator, not a claim to reproduce the authors' unspecified estimator.
3. Enumerate all strict vertical local maxima before reading acceptance regions. A tied plateau up to one SNR-bin spacing is represented by its midpoint; broader unresolved plateaus do not count as a located mode.
4. Require each of the four externally annotated branches to have a mode within its source-derived time/SNR box with only the declared localization allowances, in every bandwidth combination. This checks branch existence and position; it does not require each branch to dominate every other local mode.
5. Independently require the global maximum of the full smoothed grid to fall in the externally annotated strongest evening island. All equally highest cells must satisfy that criterion, preventing a favorable choice among disconnected maxima.
6. Check the paper's qualitative morning/evening versus midday density ordering. Raw counts in [06,09) and [18,21) must each exceed [12,15), using equal-duration windows fixed from the source tick spacing. No exact observation count or numerical contour level is inferred from the publication.

No assertion treats the paper's displayed -15 to +25 dB range as the complete sample range. The smoother retains the full production count grid, including observations beyond those plotting limits. Dawn's contour fan near 04-06 UTC and the prose's approximate 21:30 transition remain contextual annotations: neither defines an exact zero crossing of a median or a unique modal branch.

## Isolated plotted-point witnesses

The independent image-only reviewer also selected three isolated black dots before comparing them with native application pairs. The fixed rule scans chronologically and alternates negative, positive, negative extremes. Eligible dots lie below -10 dB or above +20 dB, are at least 20 pixels from another identified black dot, and more than 10 pixels from contours and axes. This produces three witnesses before 08 UTC; it does not cover the complete day.

| Paper witness | Centroid x/y (pixels) | Digitized UTC hour | Digitized Delta SNR |
| --- | --- | ---: | ---: |
| Isolated negative 1 | 210.278 / 751.889 | 1.75675 | -12.91631 dB |
| Isolated positive 1 | 473.412 / 78.118 | 6.82108 | +22.08480 dB |
| Isolated negative 2 | 519.722 / 751.889 | 7.71238 | -12.91631 dB |

`paper_points.json` records the source-only selection, dark-pixel component centroids and uncertainty. The stated decimal precision describes pixel arithmetic, not physical measurement precision. The fixed comparison allowances of +/-0.08 hour and +/-0.21 dB conservatively combine +/-2-pixel centroid readout and approximately +/-2-pixel axis calibration. These witnesses use native paired Delta SNR and circular UTC time-of-day; no hourly-bin or smoothing allowance is added.

Each witness must match at least one current native pair within both tolerances. This independently checks selected point values and UTC folding. The three-day folded figure does not reveal a point's date, transmitter or complete paired identity, so the test neither requires a unique match nor claims author-confirmed pairing provenance. These extreme plotted points do not establish membership in WSPRadar's optional outlier-candidate detector. All three matched on the first comparison without changing the digitized values or tolerance.

## Files, limits and maintenance

- `paper_features.json`: unchanged primary paper-only annotation, pixel geometry, physical coordinates, selection rules and source provenance.
- `paper_figure6.png`: inspectable external source figure, stored as binary.
- `independent_image_review.json`: the independent review and treatment of sub-bin ambiguous contours.
- `comparison_policy.json`: the frozen estimator, sensitivity cases, uncertainty budget and failure policy.
- `paper_points.json`: three independently extracted extreme scatter-point witnesses and their source-readout tolerances.
- `manifest.json`: mandatory inventory and checksums for the external reference.

The archive fixture's 6,459 pairs and its exact medians/quartiles/counts remain a separate numerical regression. The paper's precise raw population, contour levels, kernel, bandwidth and normalization are unavailable, and the paper-count difference remains unresolved. Passing the external test demonstrates agreement in selected density-feature positions and qualitative density ordering at the declared resolution. It does not prove equality of entire distributions, absolute densities, sample counts, quartiles, hourly medians or causal antenna effects.

Missing or altered source files fail rather than skip. Tests never refresh paper annotations or expected archive values. A mismatch or bandwidth-sensitive result must be reported and investigated separately; changing expectations to make it pass is not validation. Production SQL execution is still outside this offline replay.

## Integration verification (2026-09-24)

The first external density comparison passed all nine fixed bandwidth combinations and the qualitative density ordering: **10 passed, 20 deselected, 1 existing warning in 5.92 seconds**. All three separately frozen scatter-point witnesses then passed on their first comparison: **3 passed, 30 deselected, 1 existing warning in 6.07 seconds**. No source coordinate, bandwidth or acceptance tolerance was adjusted after comparison.

The final focused run of both archive references, the external paper reference and the directly related prepared-export integrity, segment temporal evidence, evidence-statistics and regression-runner modules reported **82 passed, 1 skipped, 1 existing Matplotlib warning in 25.03 seconds**. The missing prepared-export fixture accounts for the skip; all 33 tests in the Griffiths reference module are mandatory. The existing module remains registered once in the 82-module runner manifest. Changed-test compilation and patch whitespace checks passed.

At the nominal 1-hour/1-dB smoothing choice, the morning matched modes are +6 dB, the strongest evening grid cell is +6 dB at 18:30 UTC, and the late-night matched modes are -3 dB. These are observed outcomes, not paper-derived expected numbers. Morning, midday and evening three-hour counts were 1,017, 785 and 1,488 respectively. The publication supplies their qualitative ordering, not those exact counts.

The installed external assertions rejected five temporary erroneous results: reversed Delta SNR, all differences collapsed to +5 dB, a +4 dB offset, a six-hour UTC density shift and a uniform density grid. These were in-memory assertion-sensitivity checks, not production-source mutation testing. The original Figure 3/Figure 6 archive fixtures and runtime calculations remained unchanged. No full-suite, browser, live-provider or database-SQL run was performed for this isolated test/data addition.

## Comparison graphics and vector PDF (2026-09-25)

`figure6_evidence_comparison.png` and `figure6_evidence_comparison.pdf` retain the same A-B-C layout: original publication, fixed-policy reconstruction and the native WSPRadar folded UTC-hour view. R1-R4 contour-region labels and P1-P3 isolated-point witnesses are retained in all three panels. The PDF contains vector count-grid cells, markers, lines, annotations and text; the original publication panel remains its unchanged embedded raster. The PDF is rendered directly from the Matplotlib figure, not from the completed PNG.

Regenerate both formats from the repository root into a review directory:

```powershell
.\.venv\Scripts\python.exe -B scripts/build_griffiths_fig6_comparison.py --output-directory tmp/griffiths_fig6_comparison_candidate
```

The builder checks all 24 hourly counts, medians and quartiles, all 1,392 density cells, and the production median/IQR artists against the existing frozen numerical fixtures. No source coordinates, smoothing policy, acceptance tolerances or scientific data are changed by PDF export.
