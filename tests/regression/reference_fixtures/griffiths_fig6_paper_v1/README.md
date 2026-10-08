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

Missing or altered source files fail rather than skip. Tests never refresh paper annotations or expected archive values. A mismatch or bandwidth-sensitive result must be reported and investigated separately; changing expectations to make it pass is not validation. Since 2026-09-25 the replay executes freshly generated production SQL on frozen source reports through the bounded SQLite adapter, then the production post-fetch, map, Inspector and temporal preparation. Native ClickHouse-engine behavior and live providers remain outside its scope.

## Integration verification (2026-09-24)

The first external density comparison passed all nine fixed bandwidth combinations and the qualitative density ordering: **10 passed, 20 deselected, 1 existing warning in 5.92 seconds**. All three separately frozen scatter-point witnesses then passed on their first comparison: **3 passed, 30 deselected, 1 existing warning in 6.07 seconds**. No source coordinate, bandwidth or acceptance tolerance was adjusted after comparison.

The final focused run of both archive references, the external paper reference and the directly related prepared-export integrity, segment temporal evidence, evidence-statistics and regression-runner modules reported **82 passed, 1 skipped, 1 existing Matplotlib warning in 25.03 seconds**. The missing prepared-export fixture accounts for the skip; all 33 tests in the Griffiths reference module are mandatory. The existing module remains registered once in the 82-module runner manifest. Changed-test compilation and patch whitespace checks passed.

At the nominal 1-hour/1-dB smoothing choice, the morning matched modes are +6 dB, the strongest evening grid cell is +6 dB at 18:30 UTC, and the late-night matched modes are -3 dB. These are observed outcomes, not paper-derived expected numbers. Morning, midday and evening three-hour counts were 1,017, 785 and 1,488 respectively. The publication supplies their qualitative ordering, not those exact counts.

The installed external assertions rejected five temporary erroneous results: reversed Delta SNR, all differences collapsed to +5 dB, a +4 dB offset, a six-hour UTC density shift and a uniform density grid. These were in-memory assertion-sensitivity checks, not production-source mutation testing. The original Figure 3/Figure 6 archive fixtures and runtime calculations remained unchanged. No full-suite, browser, live-provider or database-SQL run was performed for this isolated test/data addition.

## Comparison graphics and vector PDF (2026-09-25)

`figure6_evidence_comparison.png` and `WSPRadar_Demo_Griffiths_Figure6.pdf` retain the same A-B-C layout: original publication, fixed-policy reconstruction and the native WSPRadar folded UTC-hour view. R1-R4 contour-region labels and P1-P3 isolated-point witnesses are retained in all three panels. The PDF contains vector count-grid cells, markers, lines, annotations and text; the original publication panel remains its unchanged embedded raster. The PDF is rendered directly from the Matplotlib figure, not from the completed PNG.

Regenerate both formats from the repository root into a review directory:

```powershell
.\.venv\Scripts\python.exe -B scripts/build_griffiths_fig6_comparison.py --output-directory tmp/griffiths_fig6_comparison_candidate
```

The builder recalculates all 6,459 paired observations through that raw-source production replay; expected paired tables and captured SQL results never supply plotted values. It checks all 24 hourly counts, medians and quartiles, all 1,392 density cells, and the production median/IQR artists against the existing frozen numerical fixtures. `render_checks.json` records source hashes, the executed query hash and pipeline counts. Fixed Gaussian smoothing is only a declared comparison presentation; it does not enter the native paired values or change the unsmoothed WSPRadar view. No source coordinates, smoothing policy, acceptance tolerances or scientific data are changed by PDF export.


### Demo PDF filenames (26 September 2026)

Embedded demo PDFs use `WSPRadar_Demo_LeadAuthor_FigureX.pdf`, with
`_diagnostic` before `.pdf` for a diagnostic. PNG filenames are unchanged.
The PDF content is byte-identical to the previously named output. Existing
generation hashes describe that original rendering, not the filename update.


## Figure 6 presentation review (26 September 2026)

Following the filename-only update above, the Figure 6 comparison was rendered
again with its existing 23 by 12.5 inch landscape page size. It now uses a white
background, a centered printed publication title and citation, a separate
Figure 6 subtitle, aligned panel headings, larger type and one shared symbol
legend across all three panels. R1-R4 descriptions appear together in order.
The legend explicitly identifies B-only density peaks and maximum, and C-only
median and IQR symbols; B and C retain their separate density colour scales.

The public PDF no longer includes the requested frozen-demo/fixture wording
or the sentence concerning the authors' unspecified smoothing. The documented
comparison policy and evidence limits above remain unchanged. The public
method notes still state B's smoothing parameters, the nonlinear C axis,
point-matching limits and the interpretation of the contour regions.

All 6,459 paired observations, 24 hourly counts/medians/quartiles, 1,392 density
cells, four feature matches, three point witnesses and scientific input hashes
match the previous rendering. `render_checks.json` records the updated builder
hash. The approved beginner-oriented description is installed in the `griffiths_squibb_fig6` demo.

### WSPRadar header revision (2026-09-27)

The Figure 6 PDF now begins with **WSPRadar.org reconstruction & comparison**, followed by the descriptive title **SNR difference by time of day**. Explicit **Referenced publication:** and **Source figure:** lines attach the authors, publication title and Figure 6 reference to their source; a **Demo:** line retains the comparison context. Presentation-only records in `config/demo_pdf_headers.py` and the shared `scripts/demo_pdf_header.py` helper own this hierarchy and identify WSPRadar as the comparison author in PDF metadata. This supersedes the earlier paper-title-first header description while preserving its review history. Source evidence, numerical expectations, scientific calculations and all body coordinates remain unchanged.

## Figure 6 region and point review (8 October 2026)

The revised comparison retains R1-R4 as labels in all three panels and removes
their visible rectangles. The original paper-derived bounds remain unchanged
in `paper_features.json` and continue to constrain the external density checks.
Both orange and gray hourly local-mode crosses are removed from Panel B; their
position-only matches remain recorded in `render_checks.json`. The maximum-density
star remains. Labels locate paper regions without claiming that every original
contour island has been reproduced. R4 continues toward R1 across midnight.

Panel B applies one global power color mapping with gamma 0.7 to the existing
density divided by its maximum. The colorbar reports the actual relative density,
not its transformed color coordinate. This improves visibility of weaker
concentrations without changing counts, smoothing, per-hour weighting or the
underlying paired observations. Native dot opacity increases from 0.23 to 0.45.
Panel C retains the production color scale, nonlinear axis, medians and IQR.
The PDF now explains that a density concentration can lie outside the hourly
middle 50%; an IQR is not a boundary around every local mode.

P1-P4 are selected plotted-point verification witnesses, with no additional
scientific classification. P1 and P2 retain their original source coordinates.
The new displayed P3 selects the rightmost bottom-boundary dot near 08-09 UTC,
approximately 0.84 hour after the former P3. P4 supplies a later positive
witness. The former P3 remains in the annotation file and regression checks
without a displayed label, preserving all earlier coverage.

| Displayed witness | Source pixel readout x/y | Digitized UTC hour | Digitized Delta SNR |
| --- | --- | ---: | ---: |
| P1 | 210.278 / 751.889 | 1.75675 | -12.91631 dB |
| P2 | 473.412 / 78.118 | 6.82108 | +22.08480 dB |
| P3 | 563.222222 / 789.555556 | 8.549586 | -14.873016 dB |
| P4 | 943.588235 / 39.882353 | 15.870183 | +24.071047 dB |

The new selection is retrospective and user-directed, with prior familiarity
with the comparison. Source-image coordinates were fixed before checking the
new native matches. P3's visible upper marker cap merges into the bottom axis;
its readout is not a recovered centroid of an unclipped dot. This limitation
is explicit in `paper_points.json`. The existing +/-0.08-hour and +/-0.21-dB
tolerances are unchanged. Neither annotation is moved to fit native results.
The regression now checks all five paper witnesses; four are displayed, with
two negative and two positive examples. All matching remains a check of folded
time/SNR positions, not author-confirmed date or station identity.

The generator remains `scripts/internal/build_griffiths_fig6_comparison.py`.
It reconstructs observations from database reports through the production
processing pipeline and asserts unchanged paired rows, 24 hourly summaries and
all 1,392 density cells. The original source raster, region annotations,
comparison smoother and numerical archive expectations are preserved.

Verification for this revision: the complete Griffiths temporal-reference and
demo-PDF-header modules passed with **75 passed and 3 existing expected
failures**. The run emitted the existing Matplotlib pending-deprecation warning
and a non-fatal permission warning while writing pytest's node-ID cache.
Changed-file compilation, patch whitespace, all seven linked PDF synchronization
checks, input and manifest hashes, embedded fonts, retained page dimensions,
PDF text checks and Poppler visual review passed. The generator also confirmed
unchanged scientific metadata and all three original point matches. This is an
offline production replay; no live-provider or full regression-suite claim is
made.

### Second iteration: point placement and duplicate-report overlay (8 October 2026)

This iteration supersedes the displayed P3 selection above while preserving
its annotation and regression coverage. P3 now labels the complete 18-pixel
source dot centered at (573.5, 771.222222), corresponding to 8.747394 UTC hours
and -13.920635 dB. Its bounding box is x=572-575, y=769-773; unlike the prior
selection, it is clear of the plotting boundary. The source-image readout was
fixed before native comparison and matches the retained 08:46 UTC / -14 dB
coordinate. These are folded-coordinate checks, not identification of the
paper's observation date or transmitter. Both earlier P3 witnesses remain
hidden checks, so all six source witnesses are tested and four are displayed.
The established +/-0.08-hour and +/-0.21-dB tolerances are unchanged.

The overall-median legend entry is removed; Panel C's native median line and
the explanatory pooled-median value remain. Shared R/P keys sit below A,
individual paired observations and the highest-density star below B, and hourly
median/IQR keys below C. A small box at the right of the reading notes contains
the red-dot key, duplicate-report explanation and linked Figure 3 reference.

Panel B now overlays additional combinations involving a weaker report at one
or both receivers, using the same 3.3-point-squared area and 0.45 opacity as
its retained-pair dots. Color alone distinguishes them. The diagnostic joins
the frozen raw reports by canonical 120-second cycle, transmitter callsign
and full locator, restricts them to production-selected identities, and checks
the retained normalized endpoint SNR values against independently calculated
raw maxima. The archive already scopes the band, interval and local endpoints.
The resulting 17 additional combinations include eight within the -15 to +25 dB
display range. They do not contribute to density, medians, IQR or Panel C.
The complete report-ID provenance is retained in `render_checks.json`.

This explains two negative differences near the apparent missing source dot:
DK3RU/JO31ws on 7 April at 18:26 and 18:30 UTC produces -13 dB when a weaker
G3ZIL report is paired with the stronger G4HZX report, whereas production
retains +11 dB at both cycles. One weaker/weaker combination at 18:26 also
equals +11 dB; it remains additional by report provenance even though it
coincides with the retained coordinate. Consequently these are additional
report combinations, not a classification of statistical outliers. Their
agreement with folded source positions does not establish the authors' exact
join or report identities. The Figure 3 reference mentions related pairing
effects and possible spurs without claiming a physical cause for Figure 6.

Verification for the second iteration: the complete Griffiths temporal-reference
and demo-PDF-header modules passed with **78 passed and 3 existing expected
failures**. The same Matplotlib pending-deprecation and non-fatal pytest node-ID
cache permission warnings remain. Focused coverage includes the new P3 source
witness, both prior P3 witnesses, raw combination counts, report-ID provenance,
power normalization, canonical cycles and full-locator separation. Changed-file
compilation, patch whitespace, final manifest/input/builder hashes, all seven
linked PDF synchronization checks, embedded fonts, page dimensions, PDF text
and relative links, and final Poppler visual inspection passed. Paired rows,
all hourly summary values and all 1,392 density cells remain unchanged. No live
provider or complete regression-suite verification is claimed.

### Third iteration: concise panel notes and integrated legend (8 October 2026)

The approved revision replaces the long reading notes with short explanations
under Panels A, B and C, in that order. The detailed R1-R4 description row is
removed while the region labels and shared key remain. P1-P4 are labeled
"verification examples only" and described as checks of selected time-of-day
and Delta SNR matches. All six source witnesses and their coordinates remain
unchanged, including the two undisplayed earlier P3 selections.

Panel B's note now explains the additional weaker-report combinations and
their exclusion from density, specifies strongest-report selection at each
receiver per cycle/path, describes fixed smoothing and links the Figure 3
pairing diagnostic. This supersedes the separate right-hand box introduced
in the second iteration. The legend beneath B lists retained paired
observations, additional weaker-report combinations and highest reconstructed
density, in that order. Its dark and red dot symbols both use a readable
6-point diameter at full opacity; the actual plotted points retain their
3.3-point-squared area and 0.45 opacity.

The numerical color adjustment and detailed pipeline explanation leave the
reader-facing notes, with the existing method and validation details retained
in this document, `comparison_policy.json` and `render_checks.json`. The
underlying color mapping, smoothing, selected observations and native Panel C
presentation are unchanged. The notes retain the nonlinear-axis and IQR
interpretation needed to read Panel C.

Verification for the third iteration: **3 focused checks passed** (the two
Figure 6 PDF-header contracts and the displayed-source-provenance check), with
78 unrelated cases deselected. The same two existing warnings remain. The
generator again confirmed all 6,459 pairs, hourly summaries, 1,392 density cells
and six source witnesses. A direct comparison with the second iteration found
unchanged scientific/provenance metadata and input hashes, and pixel-identical
header and chart regions. Changed-builder compilation, patch whitespace,
manifest integrity, seven linked PDF synchronization checks, extracted caption
order and wording, embedded fonts, retained page dimensions, Figure 3 link and
Poppler visual review passed. This is a presentation-only verification; no
runtime, live-provider or complete-suite verification is claimed.

Final copy edit on 8 October 2026: the sentence about density concentrations
outside the IQR is removed from Panel C. Panel B's prose now marks
"additional* weaker-report combinations" and the corresponding note reads
"*see Figure 3 Pairing and duplicate reports", with the diagnostic title in
bold and the existing PDF link retained. The legend and all plot content are
unchanged.
The same three focused checks passed, with the two existing warnings. Poppler
review, exact caption and bold-link checks, compilation, whitespace and PDF
synchronization passed. Header, plots and legends are pixel-identical to the
preceding revision; scientific metadata and input provenance are unchanged.
