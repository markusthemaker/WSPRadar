# Vanhamel Figure 6 antenna-rotation reference

This fixture combines independently captured raw WSPR reports, an independent standard-library calculator, and previously recorded graphical readings from Figure 6 of Vanhamel, Machiels and Lamy (2022). It exercises the M7AEO/IO82 selected-station RX Benchmark reconstruction using a **+1.6 dB Reference SNR Correction**. Exact numerical expectations are derived from raw reports; only the explicitly identified graphical anchors are external published expectations.

## Published source and interpretation

Jurgen Vanhamel, Walter Machiels and Hervé Lamy, *Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*, International Journal of Antennas and Propagation, 2022, Article 4809313, [DOI 10.1155/2022/4809313](https://doi.org/10.1155/2022/4809313). Figure 6 is on printed page 6, PDF page 7 in the TU Delft copy, whose first page is a repository cover. The experimental discussion spans printed pages 5–7.

The caption identifies M7AEO, the ITA LWA II antenna fixed for two weeks, and the adapted shorted dipole parallel during the first week through reception 750, then rotated 90 degrees horizontally after reception 750. Blue is ITA LWA II, dotted red is the dipole, and black is their difference, visually interpreted as ITA minus dipole. The horizontal axis is reception number, not UTC time. The published figure has no exact total count, dates, raw identifiers, numerical slice medians, IQR values, or statistical outlier labels. The text describes an upward change and a 1–3 dB range across stations, without specifying a numerical M7AEO mean or median step.

The figure is a 1313 × 580 embedded JPEG, not vector data. Approximately 0.90 horizontal pixels represent each reception; connecting segments, stroke width, overlapping observations and JPEG artifacts prevent exact native-point recovery. The dark zero guide must not be mistaken for the black data trace. A median of ink pixels or column centers is not a median of the underlying paired observations.

`paper_features.json` is copied byte-for-byte from the independent source extraction. Its seven center-of-stroke landmarks and **±5 reception / ±0.4 dB** readout tolerances were communicated before the archive comparison. The source feature file itself was assembled afterwards, with those readings unchanged; its provenance explicitly preserves that timing. These tolerances describe graphical readout, not experimental uncertainty or statistical confidence. The rough visual band ranges in that file are descriptive, not numerical distribution constraints. The feature file's paths refer to the original extraction workspace; corresponding frozen copies are `paper_features.json` and `paper_figure6.png` here.

## Correction and limits of the reconstruction

The paper's text states a **1.2 dB** receiver-chain correction. The [authors' instrument website](https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-antenna-comparison-instrument) reports **1.573591164 dB**, which rounds to the user-selected **1.6 dB** used here; see also the authors' [receiver-correction instructions](https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-station-compare-app/wspr-station-compare-add-on?pli=1&authuser=0#h.8110v9yak2eo). This choice and graphical agreement support the reconstruction, but do not identify the exact correction used for Figure 6 or prove an error in the paper. The website value is not substituted into the unchanged paper feature file.

The published landmarks were read independently, but the choice of the 1.6 dB reconstruction was informed by the website and subsequent graphical comparison. Therefore this is a reconciled reference corpus, not a blind validation of a previously fixed correction. Keep the original graphical tolerance; do not tighten it to the observed approximately 0.1 dB residuals. Offset-invariant checks such as the largest peak-to-trough span add useful external support. The paper readout for that span is 15.8 dB with a conservative ±0.8 dB combined allowance; the raw-derived span is 16.0 dB.

`observed_landmark_comparison.csv` records the already-performed comparison and is explicitly **observed**, not an independent external expected-results table. `figure6_overlay_1p6.png` and `WSPRadar_Demo_Vanhamel_Figure6.pdf` are human-review artifacts with four aligned panels: **A** shows the original published image using the fixed tick calibration, **B** reconstructs all three traces from actual WSPRadar paired results at every reception, **C** projects the same native density values behind the unchanged black Delta-SNR trace on exact reception-number bin spans, and **D** shows the production Selected Station Evidence chronological figure with white export styling and **12h bins**. Seven independently read landmarks remain ringed in A and B. The reconstruction is not a pixel-difference test or an exact digitization of the paper. No translation, amplitude scaling or time warp was fitted; choosing the correction is the separate decision described above.

Panels A and B use the same linear reception-number and dB axis limits. For the two antenna traces, B removes the common +7 dB reported-power normalization from WSPRadar's endpoint values to display reported SNR, retaining the Reference's +1.6 dB correction. All 1,441 selected pairs report transmitter power 23 dBm, so that common display shift leaves every paired difference unchanged. Panel D keeps WSPRadar's actual UTC coordinates, median-centered nonlinear axis, 12h density cells, bin medians and IQR. Its different horizontal axis represents elapsed time rather than reception number; sparse and empty periods therefore retain their actual duration. These visual adaptations do not change the independent numerical expectations, including the retained 20-slice summaries.

The PDF is generated from the plotting objects, not converted from the PNG. Only the original publication image is raster; the reconstruction, WSPRadar density cells, colorbar, lines, markers, axes and labels remain vector graphics. `comparison_presentation.json` records the presentation builder, rendering boundary and observed landmark positions; it is not an independent oracle.

## Raw capture

`source_rows.parquet` is the original 169,876-byte public `https://db1.wspr.live/` response. Its SHA256 is `8f684384f12f15a0070cd0aae3167f07545f39ac050d625c15a70b4e9f3400fe`. `source_query.sql` preserves the capture query. The original capture session began on 2026-09-23 at 20:48:24.823263 UTC and completed at 20:48:31.158897 UTC; these bound the recorded capture session, not the exact HTTP request instant. `capture_provenance.json` distinguishes capture and fixture assembly times and records hashes.

The query captures every available report for receivers ON4AWM0 and ON4AWM1 on provider band code 1, in the half-open UTC interval **2021-05-01 17:15 through 2021-05-15 07:00**, across all endpoint locations, transmitter identities, decode codes and duplicates. No peer, locator, mode, coordinate or target-active filter was applied in that raw query. The response has 12,545 rows, well below its 1,000,001-row limit, and all reports happen to have code 1. This is complete for that requested current-archive population, not proof that the archive reproduces every report available to the authors in 2021. No reports outside the configured interval were requested; this fixture does not itself contain exterior time-boundary guards.

`source_rows.csv` is a deterministic time/id-sorted conversion of that Parquet response. It preserves all fourteen raw fields, integer identifiers and UTC timestamps. Float32 coordinates are promoted to float64 before CSV serialization to retain the stored float32 values rather than print a shortened decimal approximation. Pandas was used only for this one-time conversion. The independent calculator consumes CSV and requires only Python's standard library.

## Independent calculation contract

The maintenance script is `scripts/build_vanhamel_rotation_reference_fixture.py`. It imports no WSPRadar runtime code, uses no application-derived result files and makes no network request. Its narrowly scoped configuration checks fail when a different scientific setup is supplied.

1. Read the fixed config and original report CSV. Require unique source ids. Select code 1, band 1, nonzero transmitter latitude, endpoint locator prefix JO20, the two configured receivers, and timestamps inside the half-open configured window.
2. Form 120-second cycles by `floor(Unix timestamp / 120)` and group by cycle, full transmitter callsign and full transmitter locator. Assert that coordinates are unambiguous within each group.
3. For each endpoint, choose the maximum reported SNR normalized to 30 dBm: `reported_snr - reported_power + 30`. Add +1.6 dB to present Reference values; absent endpoint aggregates remain zero and are distinguished by their report counts. Decimal arithmetic expresses the chosen decimal correction without avoidable binary subtraction noise.
4. Retain only globally Target-active cycles and peers strictly closer than 5,000 km to the JO20OT cell center. The independent geometry uses a 6,371 km sphere and Maidenhead cell-center arithmetic. It yields 7,166 SQL-equivalent groups and 7,139 groups after these filters. There are 5,379 joint groups across all retained peers; these pooled results are not the selected-station Figure 6 series.
5. Select joint M7AEO/IO82 rows, retaining full identity and both source-report ids. The configured minimum of one joint spot is satisfied. The resulting **1,441 pairs** have no duplicate endpoint groups and both endpoint power reports are 23 dBm. Assign one-based reception numbers in chronological order. The Target normalized SNR is raw Target SNR +7 dB; Reference normalized SNR is raw Reference SNR +8.6 dB. Their difference equals raw Target minus raw Reference minus1.6 dB.
6. Compute exact archive-derived summaries with equal weight per paired observation. Medians use the ordinary midpoint of the middle pair when needed. Q1/Q3 use linear interpolation at zero-based positions `(N - 1) * p`. Standard deviation uses the sample definition (`N - 1` denominator). No outlier removal, clipping, winsorization or replacement occurs.

These are independently implemented calculations of the defined contract, not a second general-purpose WSPRadar implementation. They do not infer missing receptions or attempted transmissions.

## Expected files and bin semantics

| File | Scope |
|---|---|
| `expected_sql_rows.csv` | All 7,166 selected report groups before Target-active/distance filtering; includes normalized endpoint SNRs, counts, coordinates and full peer identity. |
| `expected_retained_rows.csv` | All 7,139 groups after Target-active/distance filtering. |
| `expected_paired_rows.csv` | The 1,441 selected M7AEO/IO82 pairs; reception number, cycle/UTC, raw and normalized SNR, power, source ids and geometry. |
| `expected_reception_slices_20.csv` | Twenty archive-derived reception-order slices with counts, endpoints and distribution summaries. |
| `expected_12h.csv` | All 28 actual chart intervals, including empty intervals, with counts and distribution summaries. |
| `expected_density_12h.csv` | Preserved legacy complete 28 × 17 time/difference grid: integer difference centers −7 through +9 dB, including zero cells; superseded for active density geometry by the versioned presentation-only revision below. |
| `expected_density_12h_correction_aware_v1.csv` | Current complete 28 × 17 grid: uncorrected comparison-coordinate bin IDs −5 through +11, corrected physical centres −6.6 through +9.4 dB, explicit half-open edges and every zero/nonzero count. |
| `temporal_density_revision_v1.json` | Independent density-only derivation, source hashes, contract and first-bin comparison; original scientific expectations remain unchanged. |
| `expected_halves.csv` | Equal elapsed-time halves and the separate published reception-750 split. |
| `expected_summary.json` | Population, selection, correction, timing, binning and whole-series audit values. |

Reception slices use `zero_based_reception_index * 20 // N`. The first contains 73 pairs and each remaining slice 72. This is a reception-count partition, not equal elapsed time; a slice spanning reception 750 deliberately mixes the two orientation phases. These exact medians and quantiles are archive-derived expectations, not statistics extracted from the figure's raster.

The following paragraph records the original density policy; the correction-aware revision below supersedes only its density-membership and cell-coordinate statements.

The chart bins begin at the configured window start, **17:15 UTC**, and advance in 12-hour steps. The final interval is shortened to the exact configured end. They are not midnight/noon UTC bins. Each interval is left-closed and right-open. Empty intervals 1, 17 and 25 have count zero and blank summary values; the production chart can represent the empty summary count as NaN, while the complete density grid has zero counts. The density metric is nearest integer `round(delta_snr_db)`, with half-even tie handling; no exact half-integer ties occur for this corpus. Metric centers are labels, not lower edges. Counts are paired-observation counts, not probability densities.

The elapsed-time midpoint is **2021-05-08 12:07:30 UTC**, in the paired-observation gap from05:34 to18:34. Its halves contain 759 and682 pairs: means −0.9056653491 and+2.8589442815 dB; medians −0.6 and+2.4 dB. The separate reception-750 split contains 750 and691 pairs: means −0.912 and+2.8167872648 dB, with the same medians. The mean elapsed-half increase is3.7646096307 dB and the median increase is3.0 dB. These are pooled observation summaries, not time-weighted averages or averages of bin medians. A constant correction shifts both halves equally and cannot change either between-half increase. Neither statistic is printed in the publication.

## Pipeline coverage and compatibility adapter

The associated regression is intended to execute the actual generated scientific SQL against this frozen raw population through the shared bounded SQLite adapter, followed by production post-fetch preparation, map/Inspector selected-station handling and the 12-hour evidence recipe. Only SQL `FORMAT` serialization is removed by that adapter. This is stronger than injecting precomputed processed rows, but it does **not** validate native ClickHouse execution, optimizer/type behavior, HTTP transport or live provider behavior. The independent calculator and frozen expectations remain separate from that execution path.

The external layer checks the unchanged graphical landmarks and peak-to-trough span. The exact layer checks raw-derived pairing, endpoint values, preserved extrema, distribution summaries and complete density counts. Mutation probes may show sensitivity to wrong correction, reversed subtraction, changed selection/timing or clipped extremes. Such checks validate this processing contract; they do not certify causal explanations, statistical anomaly flags, or the author's undocumented original averaging procedure.

## Reproduction and integrity

Run the calculator into a separate candidate directory; never overwrite the committed expected files during tests:

```powershell
.\.venv\Scripts\python.exe -S scripts/build_vanhamel_rotation_reference_fixture.py --source-csv tests/regression/reference_fixtures/vanhamel_fig6_rotation_v1/source_rows.csv --config tests/regression/reference_fixtures/vanhamel_fig6_rotation_v1/demo.config --output-directory tmp/vanhamel_rotation_reference_candidate
```

The API is `calculate_reference(source_path, config_path, output_directory)`, taking `pathlib.Path` arguments and returning the summary dictionary. It regenerates the eight `expected_*` files deterministically. `-S` demonstrates independence from site-installed dependencies. The raw capture, published image, manually recorded paper features, observed overlay and provenance are separately frozen inputs/review artifacts; they are not regenerated or silently revised by this calculator. `manifest.json` records byte counts and SHA256 values for all other fixture files, plus the calculator hash.

Regenerate only the comparison PNG, vector PDF and presentation metadata with the separate presentation builder:

```powershell
.\.venv\Scripts\python.exe -B scripts/build_vanhamel_rotation_comparison.py --output-directory tmp/vanhamel_rotation_comparison_candidate
```

This builder runs the existing offline production-SQL regression harness against `source_rows.csv`, checks the resulting paired trace against the independent frozen expectation, and renders the real production chronological chart. It does not refresh any `expected_*` file or paper feature. Review the candidate graphics before installing them and updating their manifest entries.

The plotting payload is prepared before any expected-results CSV is read. `prepare_reconstruction` selects the actual eligible production Joint Spot projection and joins its exact UTC/callsign/full-locator identities to production Inspector endpoint values. The expected paired CSV is read only by the separate `assert_reference_reconstruction` check and never supplies plotted SNR, Delta SNR, medians, IQR or density. A regression deliberately changes production endpoint/difference values, blocks expected-file reads during preparation, and verifies that both reconstructed traces and the production chart summaries change; the independent oracle then rejects the altered result. This follows the [shared reconstruction contract](../README.md).

## Source attribution and reuse

The PDF cover labels the publication **CC BY**. Printed page1 explicitly grants Creative Commons Attribution reuse, and its license hyperlinks identify [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Copyright ©2022 Jurgen Vanhamel et al. The reproduced `paper_figure6.png` is an RGB conversion of the embedded Figure6 image. `figure6_overlay_1p6.png` and its PDF sibling adapt that image by displaying its original traces with calibrated axes and landmark rings, alongside reconstructed evidence and the WSPRadar temporal view. Credit for the original figure remains with the cited authors; these adaptations are not presented as author-endorsed.

The paper's license does not confer a license on the separate WSPR archive. The raw files contain factual reception reports from the publicly queryable `db1.wspr.live` service; no separate provider license statement was captured with the response. Preserve the provider/query provenance when redistributing this fixture. No private correspondence, email attachment or full paper PDF is included.


### Demo PDF filenames (26 September 2026)

Embedded demo PDFs use `WSPRadar_Demo_LeadAuthor_FigureX.pdf`, with
`_diagnostic` before `.pdf` for a diagnostic. PNG filenames are unchanged.
The PDF content is byte-identical to the previously named output. Existing
generation hashes describe that original rendering, not the filename update.


### Four-panel mapping update (26 September 2026)

Panel C is an explanatory coordinate projection of Panel D’s native density mesh. The builder assigns each production paired timestamp to its existing half-open UTC bin and verifies membership counts against both the production summary and count grid. Reception support edges are `0.5 + cumulative paired counts`; repeated edges preserve empty UTC bins without inventing reception width. The native density values, masks, vertical cell boundaries, global normalization and colormap are reused unchanged. All 1,441 paired Delta-SNR values remain unsmoothed.

The strips use one-based bin numbers 1–28. Empty bins 2, 18 and 26 are hatched only in Panel D. The final bin spans 05:15–07:00 UTC on 15 May, a clipped 1 h 45 min interval. The bin grid still begins at 17:15 UTC on 1 May and alternates 17:15/05:15 boundaries. Panel C uses a linear dB axis; Panel D retains the native nonlinear axis and production median/IQR rendering. Shared colours summarize each whole bin, not a separate distribution at every reception.

The enlarged 22 × 20.2125 inch page preserves the previous 16:14.7 aspect ratio. Scientific sources, expected tables, paper features, original figure and observed-landmark records are unchanged. The current presentation metadata and manifest identify this new generation; the earlier filename-only rename record remains historical.


### Figure 6 review refinements (26 September 2026)

The shared trace/landmark legend uses one full-width row. Panel C places reception numbers above the plot and matching UTC-bin numbers below, adjacent to Panel D. The black trace is shown without additional minimum/maximum markers.

The next two paragraphs preserve the reviewed pre-fix geometry and its diagnosis. The correction-aware revision below supersedes their descriptions of the active renderer.

The native density rounds each Delta-SNR value to an integer-centred, 1 dB cell and paints that count across the whole time bin. Every plotted reception contributes to the same density grid. For bin 1, receptions 1–99 range from -3.6 to +1.4 dB, while their occupied density cells span -4.5 to +1.5 dB. The extra painted extent is cell geometry; no missing observations lie beyond the black trace. The existing values, masks, colours and density normalization remain unchanged.

The +1.6 dB reference correction places this dataset’s Delta-SNR values at integer +0.4 dB. With the native integer-centred cells, each value lies 0.9 dB above its cell’s lower edge and 0.1 dB below its upper edge. This accounts for the asymmetric visual padding. The painted extent is a histogram interval, not an exact minimum/maximum envelope. Recentring those cells on the corrected measurement grid would be a separate change to the production renderer and both Panels C and D.


### Correction-aware temporal density revision (26 September 2026)

The permanent production renderer now forms the 1 dB cell ID in the uncorrected comparison coordinate: `k = floor(d + c + 0.5)` for the already corrected Delta SNR `d` and authoritative numerical Reference correction `c`. It then draws `[k - 0.5 - c, k + 0.5 - c)`. Adding `c` is membership-coordinate arithmetic only: the stored Delta SNR, paired values, bin medians, Q1 and Q3 are not modified. The approved membership-only resolution first rounds the temporary uncorrected comparison coordinate to 0.1 dB (nearest tenth, ties-to-even), then applies the half-open whole-dB convention, assigning an exact half-dB boundary to the upper cell, including negative boundaries. Only at half-tenth rounding midpoints, an 8-ULP-scaled float64 arithmetic guard resolves correction noise; values beyond that narrow guard retain their side of the quantizer. Values below the declared 0.1 dB display resolution may intentionally share membership. No observation, stored corrected metric, median or quartile is rounded by this density policy.

A replay of the same frozen raw reports at corrections 0 and +1.6 dB retains all 1,441 observations and every timestamp/paired identity. Reference SNR increases once by 1.6 dB; every Delta SNR, median and quartile decreases by 1.6 dB. Comparison-coordinate cell IDs, membership, counts, masks and relative-density values are unchanged in both chronological and folded recipes. Corrected edges equal zero-correction edges minus 1.6 dB. For this integer-report dataset, that is +0.4 dB relative to the previous corrected-density geometry, with unchanged counts and colours. In the first UTC bin the same observations span -3.6 to +1.4 dB and the occupied cells now span -4.1 to +1.9 dB.

The independent scientific expectations, original `expected_density_12h.csv`, original `expected_summary.json` and all raw sources remain byte-identical. The new `expected_density_12h_correction_aware_v1.csv` and `temporal_density_revision_v1.json` supersede only the legacy density-coordinate expectations. Their standard-library calculator reads raw report SNR and power, uses frozen independently derived pair identities/timestamps and computes exact Decimal comparison coordinates, membership and edges. It does not import the production helper or refresh the scientific oracles. Reproduce only these two new files with:

```powershell
.\.venv\Scripts\python.exe -S scripts/build_vanhamel_temporal_density_reference.py --reference-directory tests/regression/reference_fixtures/vanhamel_fig6_rotation_v1 --output-directory tmp/vanhamel_density_revision
```

The unchanged seven paper landmarks, full paired trace, twenty reception slices, 28 UTC intervals, three empty bins, final 1 h 45 min bin and 3 dB before/after median step remain separately checked. Panels A and B retain their existing source/trace presentation. Panel C retains the exact black trace, reception-number scale above, matching bin-number scale below and no added extrema circles; it reuses Panel D's fixed production density mesh. Panel D remains the native UTC view with its nonlinear axis, median and IQR. The shared single-row trace legend and approved page layout remain unchanged. No PDF-specific density shift is applied.

### Balanced-margin layout follow-up (26 September 2026)

At the user's request, all four aligned panels and the shared legend now extend 76 points farther to the right; the shared colour bar moves by the same amount. The page size, aspect ratio, typography, text, trace coordinates, density values and scientific expectations remain unchanged. Including the outer axis labels, the PDF's measured left/right content margins are 43.148/43.133 points. The publication image and plotted panels are therefore horizontally wider than the immediately preceding approved rendering; this follow-up supersedes pixel-identity claims for that earlier layout. Demo #5 (`vanhamel_rx_buddy`) already links the stable published PDF path, which now serves this revised layout.

### WSPRadar header revision (2026-09-27)

The Figure 6 PDF now begins with **WSPRadar.org reconstruction & comparison**, followed by the descriptive title **Antenna rotation: from individual receptions to 12-hour evidence**. Explicit **Referenced publication:** and **Source figure:** lines attach the authors, publication title and Figure 6 reference to their source; a **Demo:** line retains the comparison context. Presentation-only records in `config/demo_pdf_headers.py` and the shared `scripts/demo_pdf_header.py` helper own this hierarchy and identify WSPRadar as the comparison author in PDF metadata. Earlier presentation records remain preserved. Source evidence, numerical expectations, scientific calculations and all body coordinates remain unchanged from the balanced-margin layout above.

The subsequent header refinement abbreviates the cited given names to J. Vanhamel, W. Machiels and H. Lamy. Publication, source-figure and demo lines all use 15 pt type with equal 35 pt baseline spacing; the enlarged citation spans approximately the plot width. The main headings, complete publication title, source reference, demo details and figure body are retained.

The compact-spacing follow-up replaces those 35 pt baseline intervals with 23.1 pt intervals, giving approximately 8 pt of visible whitespace between the three supporting lines. The gap from the descriptive subtitle to the publication line matches that whitespace. The demo line moves upward by 42.5 pt to increase separation from Panel A; wording, fonts, horizontal placement, page dimensions and the complete figure body remain unchanged.

The final publication-gap refinement moves those three supporting lines downward together by 7.21 pt. The visible gap before the publication line now matches the approximately 15.31 pt gap between the main heading and descriptive subtitle, while the supporting lines retain their compact 23.1 pt baseline intervals. All text, typography, horizontal placement and figure-body pixels remain unchanged.
