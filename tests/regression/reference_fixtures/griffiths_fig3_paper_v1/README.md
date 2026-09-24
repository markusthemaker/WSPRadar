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
quantiles. This offline replay starts with frozen SQL-result rows and does
not execute SQL or query a live provider.

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
