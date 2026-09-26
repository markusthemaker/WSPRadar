# G3ZIL / G4HZX Figure 3 external temporal reference

This mandatory external fixture complements `../griffiths_fig3_temporal_v1`.
Its expectations come from the original paper's figures and text, not from
WSPRadar outputs. The existing archive fixture continues to preserve exact
paired observations, counts, temporal medians, quartiles and density cells.
Application runtime calculations are unchanged.

## Source and independent extraction

[Griffiths and Squibb, Practical Wireless, October 2017, pp. 23-26](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf),
Figure 3 on printed page 24, Figure 4 and accompanying text on printed page 25,
provide the source evidence. The supplied PDF's SHA-256 is
`9d3fe7e8b7230a6c0abbf86787591e5d140f470b72c18c10e44fd8ccd006819f`.
The two PNGs preserve the extracted original image dimensions and RGB pixels;
no screenshot of WSPRadar defines a reference coordinate.

Separate source-only tasks annotated Figure 3 and the Figure 3/4 relationship.
Those annotators had earlier task context, so this is retrospective validation,
not a blinded or preregistered study. A further reviewer received the original
Figure 3 image without application outputs or existing annotations. Both
Figure 3 reviews agree on the axes, broad temporal pattern and negative plume,
and independently reject treating black darkness as calibrated density.
The independent review uses broader descriptive regions; it is not a second
measurement of the primary rectangles' exact edges.

All six source/policy files were frozen and hashed before the first application
comparison. `frozen_inputs.json` preserves that record. The source JSON retains
its original candidate-stage wording and extraction paths as provenance;
installed PNGs are `paper_figure3.png` and `paper_figure4.png`.

## What Figure 3 can establish

The black scatter is G3ZIL minus G4HZX Delta SNR. The blue markers are daily
soil moisture on the inverted right-hand axis, not SNR averages or medians.
Saturation, overlap, rasterization and marker occlusion prevent recovery of
exact counts, density levels, statistical modes, medians or quartiles.

Four source-only rectangles identify populated regions: early April, mid-April,
late April and the conspicuous negative tail around April 16. The tail box
covers approximately -18.7 to -15.3 dB before readout allowances. It deliberately
avoids using the -20 dB plotting boundary as an observed minimum.

The comparison expands each rectangle by the sum of its recorded manual-edge
and axis-readout bounds: central regions use +/-7 pixels horizontally and
+/-10 vertically; the tail uses +/-5 and +/-4. These bounds were chosen from
the source image, not residuals against application results. At least one
native paired observation must lie in each expanded region, with the separate
strict condition Delta SNR < -15 dB for the tail. Both the production 3-hour
and daily count grids must also contain a populated cell intersecting that
region. Native membership prevents neighbouring observations in a broad cell
from supplying the only witness. These are necessary occupied-region checks,
not claims that an entire concentration or its density has been reproduced.

The text describes a rise over April 1-15 in daily averaged Delta SNR. Its
declared operational check requires a positive linear slope across those
15 daily means and a higher average over April 13-15 than April 1-3. The
three-day endpoint windows were selected from the source interval before
comparison. No minimum slope, significance or monotonic daily increase is
claimed. Daily recurrence remains supporting context without an invented
phase/amplitude threshold. The paper's approximate 2,000 spots/day is also
context; it supplies no defensible exact-count tolerance.

## Numerical daily means from Figure 4

Figure 4 explicitly plots daily averaged Delta SNR against moisture. Three
isolated blue diamonds have moisture intervals overlapping exactly one of
the 15 Figure 3 daily moisture intervals. Other dates remain ambiguous.
The lowest and highest first-half blue diamonds also provide date-independent
daily-mean extrema. Red second-half markers and the fitted regression line
are excluded.

| External anchor | Source readout interval (dB) |
| --- | ---: |
| April 6 daily mean | 5.5808 to 5.6962 |
| April 13 daily mean | 7.7447 to 7.8601 |
| April 15 daily mean | 8.6597 to 8.7750 |
| April 1-15 minimum daily mean | 2.3786 to 2.4940 |
| April 1-15 maximum daily mean | 8.6597 to 8.7750 |

Bounds combine +/-2 pixels for isolated-marker centroids with +/-1 pixel axis
readout. Their approximately +/-0.0577 dB width describes raster uncertainty,
not sampling uncertainty or unknown population differences. The maximum and
April 15 reuse the same paper marker; they are two assertions, not independent
pieces of evidence. The minimum cannot be uniquely assigned among April 1-3.

The regression calculates arithmetic means from the actual production daily
count grid. In this dataset, integer-dB differences coincide with one-dB cell
centres. All cells are retained, including observations beyond the paper's
displayed range. Pairs are pooled within a UTC day; daily means receive equal
weight in the trend check. This does not change the chart's displayed medians
or imply that its recipe contains a mean field.

## Limits, maintenance and execution

The paper does not supply its original SQL, detailed duplicate/weighting
policy, exact population or precise daily cutoffs. UTC interpretation follows
the WSPR convention and the article's time-of-day discussion; Figure 3 itself
labels its horizontal axis only as Time. A mismatch must remain visible and
be investigated as a reproduction discrepancy. Do not widen bounds to absorb
an unexplained difference, move source rectangles after comparison, or
regenerate these expectations from the application.

Neither the dated tail nor any occupied-region witness classifies an event
under the optional outlier detector. No soil-moisture or antenna-effect causal
claim is tested. Exact medians and IQR remain separately checked against the
reviewed archive and independent arithmetic, not against paper-derived
quantiles. Since 2026-09-25 this offline replay starts with frozen source
reports and executes newly generated production SQL through the bounded
SQLite adapter before post-fetch, map, Inspector and temporal preparation.
It does not query a live provider or validate the native ClickHouse engine.

`manifest.json` inventories all required fixture files with sizes and hashes;
missing or altered files fail rather than skip. The shared reference module
is already registered once in the regression runner manifest. Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/regression/test_griffiths_temporal_reference.py -q
```

The installed package contains the two source PNGs, `paper_features.json`,
`paper_daily_means.json`, `independent_image_review.json`, the separate
`comparison_policy.json`, the pre-comparison `frozen_inputs.json`, this README
and the package manifest.

## First comparison and duplicate-sensitive reconciliation

The first comparison produced **11 passed, 3 failed, 33 deselected**, with one
existing Matplotlib warning, in 19.77 seconds. The failures were the April 16
tail in both chronological grids and the April 13 daily mean. The source
annotations, readout intervals and comparison policy remain byte-identical
to the pre-comparison freeze; `known_discrepancies.json` separately records
the observations and resulting investigation.

| Evidence | Paper | Production | Duplicate-expanded raw join |
| --- | --- | ---: | ---: |
| April 6 mean | 5.5808-5.6962 dB | 5.6456 dB | 5.6457 dB |
| April 13 mean | 7.7447-7.8601 dB | 8.1416 dB | 7.8066 dB |
| April 15 mean / first-half maximum | 8.6597-8.7750 dB | 8.7654 dB | 8.7398 dB |
| First-half minimum daily mean | 2.3786-2.4940 dB | 2.4573 dB | 2.4395 dB |
| April 16 negative-tail region | Occupied below -15 dB | 0 native pairs | 38 report combinations |

The paper mean and tail are compatible with a same-time/transmitter join
that retains all duplicate report combinations. Such a join yields 59,019
combinations across the captured source population. WSPRadar instead selects
the maximum normalized SNR per receiver, transmitter identity and cycle, then
forms one paired difference. Its selected demo population has 57,767 pairs.

Independent maximum-report calculations over all captured distances give
8.1352 dB for April 13 and an April 16 minimum of -14 dB. The duplicate-expanded
calculation gives 7.8066 dB and restores the paper's dated negative region;
many witnesses involve multiple weaker G3ZIL reports of HB9MHB. This distinction
explains why checking only the maximum-collapsed archive initially suggested
missing raw evidence: the weaker raw observations are present.

All five Figure 4 anchors and the Figure 3 tail match under that alternate
pairing unit. This is an exploratory explanation chosen after the initial
comparison, not proof of the authors' undocumented SQL. It does not justify
changing WSPRadar to count duplicate combinations or asserting that one unit
is universally preferable. The alternate calculation uses the full captured
range; it is not a claim that every paper selection has been recovered.

The three direct production disagreements remain **strict expected failures**
restricted to `ExternalPaperMismatch`. They are not silently omitted or counted
as successful external validation. Unexpected agreement fails as a strict
XPASS and requires review; missing/corrupt fixtures, setup errors and failures
to carry an existing native witness into its histogram cells remain ordinary
failures. To expose the original direct-comparison failures explicitly, run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/regression/test_griffiths_temporal_reference.py --runxfail -q
```

Seven additional ordinary checks reproduce the five fixed Figure 4 anchors
and negative-tail region from duplicate-expanded raw reports, and independently
recompute the strongest-report difference for every retained production pair.
This separates reproduction of selected paper evidence from verification of
WSPRadar's different duplicate policy. The external region checks additionally
require all native witnesses to be represented in their corresponding plotted
cells; broad intersecting-cell occupancy alone is insufficient.

## Integration verification (2026-09-24)

The complete shared reference module reported **51 passed, 3 xfailed,
1 existing warning in 23.64 seconds**. Focused verification of this module,
prepared-export integrity, segment temporal evidence, evidence statistics and
the regression runner reported **100 passed, 1 skipped, 3 xfailed,
1 existing warning in 34.70 seconds**. The unrelated missing prepared-export
fixture explains the skip; the three strict expected failures are the explicit
paper/production pairing differences above. They must not be reported as
successful independent validation.

Changed-test compilation, whitespace checks and the 82-module/five-chunk
manifest validation passed. All prior Figure 3/Figure 6 fixture bytes and
unrelated working-tree changes were preserved. All six pre-comparison source
and policy hashes remain unchanged. The final inventory includes this README
and `known_discrepancies.json`; those outcome records were written after the
source freeze and are not used as paper-derived numerical expectations.

No complete-suite, browser, live-provider or SQL-execution check was performed
for this isolated test/fixture addition. Full verification remains necessary
before the accumulated changes are finalized for release or submission.

## Publication, reconstruction and WSPRadar graphics (2026-09-25)

`figure3_evidence_comparison.png` and its PDF sibling show three vertically
aligned panels, preserving the month-long time axis at a readable width:

- **A: Publication.** The complete original Figure 3 image, including the
  separate blue soil-moisture series and its right-hand axis.
- **B: Reconstruction.** Every one of the 57,767 WSPRadar paired
  observations freshly recalculated from frozen raw reports contributes to the
  production **1-hour by 1-dB count grid**, shown in grayscale on the paper's
  linear dB and calendar ranges. The scale is linear from zero to 100 percent
  of the full-month maximum cell count; empty cells are white. There is no
  per-hour normalization or smoothing. **All 57,767 original paired observations**
  are also drawn as black dots at their native time and Delta SNR, including
  coincident observations. Fixed marker area **7 points squared** and opacity
  **0.30** make them larger and darker than the initial density presentation's
  2.5-point-squared, 0.20-opacity markers in one/two-pair cells. The density
  background and its linear grayscale are unchanged. Its colorbar describes
  that background only; overlapping black markers add visual darkness without
  altering the represented counts. Production rounding and time-bin edges
  validate marker alignment; no observation is thinned, jittered or removed
  from the density or scatter population.
  This replaces the earlier unbinned scatter presentation, whose coincident
  points and small markers obscured dense regions. No time shift, SNR offset,
  jitter or synthetic moisture
  series is fitted. The calculation executes current generated SQL, then the
  production post-fetch, map, Inspector and paired-evidence path. Expected
  paired rows only assert the resulting values; they never supply the plot.
  The hourly grid contains all 57,767 pairs, and summing each twelve adjacent
  hourly columns exactly reproduces C's 12-hour counts. Publication darkness
  remains qualitative because the paper's marker opacity and raster processing
  are unknown; the grayscale is not fitted to its appearance.
  The paper's displayed range clips both tails; the retained
  observations themselves are not clipped or filtered before rendering C.
- **C: WSPRadar view.** The actual chronological temporal export renderer and
  white export theme, using 12-hour bins. Its production artists retain the
  one-dB density cells, median markers, IQR, pooled median and median-centered
  nonlinear dB axis. Thus equal numerical SNR does not occupy equal vertical
  pixel positions between B and C. The 60 bin counts, medians and quartiles
  are independently recalculated from the same pairs and checked against
  the production recipe and displayed artists during generation.

Matching magenta dashed rectangles in comparison panels A and B mark the
existing expanded negative-tail diagnostic interval, **-20 through -5 dB**
on 16 April. The publication rectangle uses the frozen axis calibration to
show the same physical interval as the reconstruction rectangle. Both callouts
and the footer link to the sibling `WSPRadar_Demo_Griffiths_Figure3_diagnostic.pdf`, described as
**repeated RX reports and weaker-report combinations**. This is a navigation
annotation, not a new paper-derived assertion or proof of the authors' exact
duplicate-handling procedure. Panel C and the numerical expectations are unchanged.

`figure3_tail_diagnostic.png` and its PDF sibling separately extend the
diagnostic inspection to **-20 through -5 dB, inclusive**. The horizontal
interval remains the original tail feature's source-defined pixel allowance:
16 April 2017 approximately 06:00:36 to 20:26:03 UTC. This wider diagnostic
contains **360 raw-report combinations: 17 retained strongest-report pairs
and 343 additional combinations involving at least one weaker report**.
Of the weaker combinations, 342 involve HB9MHB and one involves DL9GCW.
There are no strongest combinations outside the selected demo population
in this diagnostic window. `figure3_tail_report_combinations.csv` records
all 360 combinations, source report IDs, SNRs, reported powers and classifications.

These new counts are calculations from the frozen archive, not independently
recoverable marker counts from the paper. Raster overlap prevents a one-to-one
identification of every source dot. The independent source rectangle T and
its strict Delta SNR < -15 dB criterion remain unchanged: **0 strongest pairs and
38 duplicate-expanded combinations**. All original source annotations,
numerical expectations, comparison policy and known discrepancies are retained
byte-for-byte; the three strict expected failures are still required.

Regenerate the graphics and their diagnostic ledger with:

```powershell
.\.venv\Scripts\python.exe scripts/build_griffiths_figure3_comparisons.py
```

The builder also writes `figure3_render_checks.json` with source-input and
generated-query hashes, pipeline row counts, production-artist checks and
diagnostic counts. Strongest pairs in both graphics come from production;
the alternate all-combinations tail join remains explicitly independent.
The builder does not rewrite numerical
reference oracles or the manifest; update the manifest only after reviewing
regenerated outputs. The PDFs are rendered from the same Matplotlib artists,
with native vector text, scatter, density cells and curves. Only the original
publication image remains raster; converting it to PDF cannot restore vector
source detail that the publication did not supply. PNG copies remain available.


## Reviewed demo presentation (2026-09-26)

This revision supersedes the display layout and expanded diagnostic range in the
2026-09-25 presentation record above; the earlier record remains preserved.
Both comparison PDFs now use a square 17-by-17-inch page, the printed article
title and complete author/publication citation, with a subordinate Figure 3
heading. The complete title, citation, subtitle and context block is centered. Panel A clips only the decorative outer image frame for display;
`paper_figure3.png` is unchanged and retains the full original pixel content.
Panel headings have consistent clearance, the chronological chart title is
integrated into C's heading, and the compact footer is separated from C.
The footer explicitly distinguishes the demo's 24-hour default from C's
12-hour bins. Reconstruction and production evidence values are unchanged.

The diagnostic now displays -20 through 0 dB, inclusive, using the same
source-derived horizontal interval. It contains **648 report combinations:
94 retained strongest-report pairs and 554 additional weaker-report
combinations**, including 551 weaker combinations for HB9MHB, two for DL9GCW
and one for IZ1UKA. Twenty-five retained pairs are exactly 0 dB. These are
counts within the displayed range; they do not describe the entire day.
`figure3_tail_report_combinations.csv` records these 648 classified combinations.
The nested source-feature boxes and their original/expanded-window labels are
omitted from the diagnostic presentation. The original source-feature checks
remain unchanged: zero strongest pairs and 38 all-combinations witnesses in
the original strict negative-tail region. Matching navigation callouts in
comparison panels A/B now use the same -20 through 0 dB diagnostic range.

A four-row example shows the reported G3ZIL frequencies and SNRs for HB9MHB at
2017-04-16 10:46 UTC. Frequencies come from the WSPR Rocks example documented
in `docs/duplicate_report_snr_policy.md`; the raw fixture does not contain
frequency fields. The builder independently checks all four G3ZIL SNRs, both
G4HZX SNRs, equal 43 dBm reported power, eight all-combinations differences
and the retained +3 dB strongest-report difference against database rows.
The text explains that +3 dB is above the displayed range while five weaker
combinations appear inside it. Multiple reports need not be identical rows.

The possible explanation of weaker offset-frequency decodes is explicitly a
hypothesis: unwanted sidebands from modulation or mixing in the transmitter
or receiving chain. Its supporting primary report is Griffiths, Elmore and
Robinett, *Some Observations While Using the KiwiSDR to Spot WSPR Stations*,
sections 4 and 7:
<https://valentfx.com/vanilla/uploads/Uploader/a9/f19334bbbcca28d72b85cb1f5be6ce.pdf>.
Those observations establish plausible mechanisms generally; they do not
identify the cause of the HB9MHB example. The PDF includes a clickable source.
The visible copy uses “database” and omits fixture-freezing terminology; all
source provenance, policies and independent numerical expectations remain in
the fixture and generated machine-readable render checks.


Focused verification of this presentation revision: **88 passed, 3 expected
failures and 3 pre-existing configuration failures** across the Griffiths
reference and configuration-package modules. The three configuration failures
expect four unrelated demos already absent from the active demo directory
before this edit. The Griffiths scientific checks have no unexpected failure;
the original three expected publication/production discrepancies remain.
Both final PDFs were rendered and visually inspected, and both MediaBox and
CropBox are 1224 by 1224 points with no rotation. Title centering preserves all
numerical render-check results. Source hashes, compiler and whitespace checks,
and the seven-PDF static-link synchronization check passed. This was focused
verification, not a complete regression-suite or live-provider run.


The worked-example explanation now explicitly identifies the table as four
G3ZIL reports and the two G4HZX reports as not shown. It connects these
reports to the eight possible differences and the single strongest-report
pair. This explanatory-copy refinement preserves all data and other layout.
The diagnostic was re-rendered and visually checked; all numerical render
checks and the diagnostic CSV remain identical.


### Anonymized diagnostic research update (2026-09-26)

The public diagnostic now states that one transmitting callsign accounts for
551 of the 554 additional weaker-report combinations in its displayed window,
with the callsign available upon request. The worked-example heading and its
explanation also omit that identity. Underlying source rows, audit identities,
pairing rules and all numerical expectations remain unchanged.

The added explanation reports matching 30-31 Hz weaker components across the
wider receiver network and the widespread episode's observed 03:22 UTC onset
and marked 15:46 UTC decline. It distinguishes the leading interpretation of
additional transmitted spectral components from an unconfirmed physical cause
and the unresolved possibility of a shared decoding artifact. Monthly context
states that 211 of 57,767 selected paired cycles contain multiple reports and
that excluding the one callsign leaves the monthly median at +7 dB.

The frequency values were independently checked against database reports
retrieved on 2026-09-26. Additional research provenance is recorded in the
render-check JSON. The page retains its square 1224-by-1224-point format,
original worked arithmetic, plot population and publication-method caveat.


The reviewed diagnostic layout now places the two-entry legend directly beneath
panel B. Full-width explanatory paragraphs use measured text wrapping, and
all text below the panels is one point larger. The existing wording, numbers,
anonymization, one-page square format and diagnostic evidence remain intact.


### Demo PDF filenames (26 September 2026)

Embedded demo PDFs use `WSPRadar_Demo_LeadAuthor_FigureX.pdf`, with
`_diagnostic` before `.pdf` for a diagnostic. PNG filenames are unchanged.
Both Figure 3 PDFs were rendered with the renamed PDF outputs; the comparison
also displays and links to the renamed diagnostic. Scientific inputs and
numerical checks are unchanged.

### WSPRadar header revision (2026-09-27)

Both Figure 3 PDFs now begin with **WSPRadar.org reconstruction & comparison**, followed by the descriptive title of the comparison or diagnostic. Explicit **Referenced publication:** and **Source figure:** lines attach the authors, publication title and Figure 3 reference to their source; a **Demo:** line retains the relevant comparison context. Presentation-only records in `config/demo_pdf_headers.py` and the shared `scripts/demo_pdf_header.py` helper own this hierarchy and identify WSPRadar as the comparison author in PDF metadata. This supersedes the earlier paper-title-first header descriptions while preserving their review history. Source evidence, numerical expectations, scientific calculations and all body coordinates remain unchanged.
