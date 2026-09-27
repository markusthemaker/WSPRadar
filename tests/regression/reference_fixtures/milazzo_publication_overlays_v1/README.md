# Milazzo Figures 6 and 7: publication reference and overlays

These review artifacts compare the original publication rasters with freshly
executed WSPRadar SQL endpoint components. They support a reversal of the
printed direction labels: Figure 6 matches RX at KP4MD and WB6RQN from VE6PDQ;
Figure 7 matches TX from KP4MD and WB6RQN to VE6PDQ. The original embedded
titles are suppressed only in the review overlays, with the evidence-based
direction stated separately above each image. The original source JPEGs retain
their titles and remain unchanged.

- [Figure 6 / RX overlay](figure6_rx_overlay.png): all 44 digitized markers
  match exactly in SNR; the maximum graphical time residual is two minutes.
- [Figure 7 / TX overlay](figure7_tx_overlay.png): all 47 compact image-derived
  anchors match exactly in SNR (32 KP4MD, 15 WB6RQN); the maximum graphical
  time residual is 143.697 seconds. All 76 archived TX reports inside the
  plotted interval are overlaid, including densely overlapping observations.

Both images use chronological UTC, 19 December 2010 12:00 through 20 December
2010 20:00, without fitting a horizontal shift or vertical SNR offset.

## Power scale and evidence population

The upper overlays use a common 37 dBm scale. Production SQL normalizes to
30 dBm, so exactly 7 dB is added to its output for the graphical comparison.
This is a declared change of reference power, not a fitted correction:

- RX: VE6PDQ reports nominal 5 W (37 dBm); the upper points equal raw SNR.
- TX: KP4MD reports 5 W and WB6RQN reports 2 W (33 dBm) inside the plotted
  interval. KP4MD's plotted SNR equals raw SNR; WB6RQN's plotted SNR is raw
  SNR plus 4 dB. The article states that transmitted-power differences were
  compensated. The explicit 37 dBm plotting baseline is inferred from the
  matched values, rather than quoted as an explicit baseline in the article.

The upper panels use endpoint reports before the Target-Active Gate, including
non-joint observations. The lower panels use current production filtering and
full-locator pairing: five RX pairs (+8, +17, +22, +7, +7 dB) and one TX pair
(-2 dB). The RX source is the bounded user-supplied VE6PDQ path, not a full
archive population from which global receiver activity can be inferred.
The original publication's connecting lines bridge gaps; they do not represent
extra measurements or establish synchronized evidence.

### Outer rings: Target-Active Gate survival

The existing green/orange rings identify SQL-reconstructed KP4MD/WB6RQN
reports. A larger charcoal ring, separated by a white outline, marks each
report that passes the Target-Active Gate in the captured source. All original
reports remain visible, including those without an outer ring. Gate survival
uses exact native 120-second cycle membership across all captured eligible
peers; the paper's graphical time tolerance never establishes activity.

| Plotted population | All reports | Gate-retained reports | Retained Joint pairs |
| --- | ---: | ---: | ---: |
| Figure 6, RX | 44 | 39 (31 KP4MD + 8 WB6RQN) | 5 |
| Figure 7, TX | 76 | 58 (57 KP4MD + 1 WB6RQN) | 1 |

These counts use the plotted interval, 19 December 2010 12:00–20 December
2010 20:00 UTC, with an exclusive end. A Joint pair contributes two endpoint
reports. The RX population contains 26 Target-only, three Reference-only and
five Joint comparison units; TX contains 56 Target-only and one Joint unit.
The outer ring therefore does not assert that a report supplies a paired
Delta-SNR value. The three RX cycles with different full peer locators remain
non-joint even though both endpoint reports pass the activity gate.

For Figure 6, the source contains only VE6PDQ transmissions. Other transmitters
could provide Target-activity witnesses for the five unringed Reference
reports in the complete archive; their absence here does not prove historical
receiver inactivity. Figure 7 uses Target witnesses across all captured
receivers, then displays only the VE6PDQ path. For these plotted reports there
are no additional distance exclusions after the gate.

Of the independently resolved paper anchors, 39/44 RX and 33/47 TX anchors
pass the gate. These anchor counts are distinct from the 39/44 and 58/76
endpoint-report counts. The unplotted 19 December 13:38 WB6RQN TX report and
the 20 December 10:36 WB6RQN report both remain visible without outer rings;
the nearby 10:34 KP4MD observation cannot establish activity two minutes later.

The installed demo now starts with the Figure 6 RX comparison in this same
publication window; its description retains the Figure 7 TX configuration as
an optional reciprocal follow-up. The historical
three-day TX fixture remains unchanged as broader regression coverage: its
VE6PDQ population has 62 Target-only and one Joint unit, or 64 endpoint
reports. The six extra retained Target reports occur after the plotted end,
on 20 December between 22:42 and 23:56 UTC.

The 13:38 UTC WB6RQN TX report on 19 December is present in the archive at
raw -6 dB and 33 dBm, equivalent to -2 dB at 37 dBm, but has no visible paper
marker. It is explicitly flagged in the overlay. The WB6RQN report at 10:36
on 20 December is almost coincident with KP4MD's 10:34 report at the same
37 dBm-scale SNR of -19 dB; it is not counted as an isolated red anchor.
The reason for the unplotted 13:38 report is not established. No report was
removed from the overlay to make the comparison appear complete.

## Figure 7 extraction and limits

The source-only extraction uses the printed plot bounds (x 78..1164,
y 104..554) and a fixed color mask followed by 3x3 erosion and four-neighbor
components. Compact components have 35..90 eroded pixels and width/height
no greater than 10 pixels. This rejects connecting lines and merged marker
centers rather than assigning a false intermediate timestamp to a cluster.
Each retained center gives an axis-calibrated time and nearest integer SNR,
checked against the original image. The extracted rows are written before
archive matching or application execution. No production values supply their
coordinates or SNRs.

Matching requires exactly one same-series report within four minutes and
0.25 dB on the common power scale. The 47 anchors are a geometrically selected
subset, not a claim that the paper contains exactly 47 reports or that all
overlapping markers were independently resolved. Two early blue anchors have
multiple nearby timestamps; their distinct SNR values identify the match.
The four-minute allowance describes raster readout, never pairing tolerance.

## Files and reproducibility

`paper_figure6.jpg` and `paper_figure7.jpg` are original images retrieved through
the publication page's image assets. `overlay_summary.json` records URLs,
SHA256 hashes, fixed calibration, selection and matching rules, and limitations.
`figure7_paper_anchors.csv` records the independent Figure 7 anchors; both
`figure*_anchor_matches.csv` files record residuals. The two
`figure*_sql_endpoint_reports.csv` files are explicitly application outputs
for audit and plotting, not independent expected results.
Both endpoint and matched-anchor ledgers append `passes_target_active_gate`.
The endpoint identity and gate flag are resolved from native SQL cycle and
full peer identity before plotting; matched anchors inherit that endpoint's
flag. The regression independently derives Target-active cycles from frozen
raw source reports and checks every flag and retained endpoint identity,
including the distinct-cycle overlap and non-joint locator cases. The existing
paper coordinates, matching residuals, tolerances and scientific expected
results remain unchanged.

The builder invokes the current generated SQL through the existing bounded
SQLite adapter and the production post-fetch/Inspector preparation. This is
not a native ClickHouse comparison. It reads the existing TX/RX source fixtures
and changes no scientific runtime, demo settings or expected-result files.

The [shared reconstruction contract](../README.md) separates scientific
production results from declared presentation adaptations. The colored rings
are explicitly a **pre-gate SQL diagnostic**, included because the paper shows
reports that are ineligible for Benchmark comparison. Their SNR components
come from current generated SQL. The outer rings are supplied by membership
in the actual production `apply_post_fetch_filters` output and must also map
to the corresponding retained Inspector outcome at the exact UTC, callsign
and full locator. The captured-source activity-witness check is a fail-closed
assertion of the scope, not an alternative source of plotted gate flags.

The lower panel takes its values and eligible population directly from the
production `_compare_joint_evidence_points(require_paired_eligible=True)`
projection after map and Inspector preparation. It does not recompute Delta
SNR or recover pairs from earlier unfiltered units. Expected-result CSVs are
not plotting inputs. A regression changes current SQL and paired-point values,
blocks expected-file reads, and checks that the plot payload follows those
production values; separate checks reject a retained endpoint missing from
post-fetch output or its Inspector outcome. Diagnostic callout coordinates and
their numeric labels also come from those current SQL endpoints. The original
paper axes and the declared common +7 dB display shift remain presentation
choices. These checks do not execute live provider transport, runtime cache,
native ClickHouse or a complete interactive application session.

```powershell
.\.venv\Scripts\python.exe -B scripts/build_milazzo_publication_overlays.py `
  --figure6 tests/regression/reference_fixtures/milazzo_publication_overlays_v1/paper_figure6.jpg `
  --figure7 tests/regression/reference_fixtures/milazzo_publication_overlays_v1/paper_figure7.jpg `
  --output-directory tmp/milazzo_overlay_candidate
```

Use a separate candidate directory for regeneration and review. The manifest
preserves this reviewed snapshot; application-output CSVs must never replace
independent paper anchors or the existing independent calculation fixtures.
Both figures now have executable regression coverage in
`test_milazzo_reference.py`. All 44 RX and all 76 TX endpoint reports in the
plotted interval are compared with independent arithmetic from frozen source
rows, including reports removed by later activity gating. The corresponding
overlay CSVs must also preserve that complete population; they are audited
outputs and never supply the independent expectation. After gating, the
bounded RX input retains 39 endpoint reports and the TX path retains 58.

The Figure 6 oracle checks all 44 paper markers. The Figure 7 oracle checks
all 47 frozen image-derived anchors, binding each to a unique raw-source
identity before reading the current production SQL component. A one-dB shift,
incorrect reference-power normalization, series reversal or missing tail
observation must fail. `figure7_paper_features.json` records the fixed source
calibration, inferred common power basis, count limits, unplotted report and
near-overlap. The latter two cases have explicit regression checks and are
never turned into synthetic paper anchors or synchronized pairs.

All original JPEGs, both overlay PNGs, the extracted anchors and accompanying
ledgers/metadata are mandatory hash-verified reference files during pytest.
The test verifies image decoding and dimensions without regenerating plots.
This does not claim that all 76 TX reports are individually readable in the
publication: the 29 without selected anchors retain source-arithmetic and
selection coverage, rather than invented independent paper measurements.

## Vector PDF companions (2026-09-25)

`WSPRadar_Demo_Milazzo_Figure6.pdf` and `WSPRadar_Demo_Milazzo_Figure7.pdf` preserve the existing PNG layouts, reconciliation circles, Target-Active Gate outer rings, annotations and lower paired-evidence panels. The builder command above now emits both formats. The PDF retains those generated elements and its text as vectors; the original publication JPEG remains an embedded raster with the same title mask used in the PNG. The completed PNG is never used as the PDF source.

The PDF companions are included in the mandatory manifest inventory. Their addition changes no source images, paper anchors, endpoint reports, gate flags, numerical fixtures or PNG pixels.


### Demo PDF filenames (26 September 2026)

Embedded demo PDFs use `WSPRadar_Demo_LeadAuthor_FigureX.pdf`, with
`_diagnostic` before `.pdf` for a diagnostic. PNG filenames are unchanged.
The PDF content is byte-identical to the previously named output. Existing
generation hashes describe that original rendering, not the filename update.

### WSPRadar header revision (2026-09-27)

Both Milazzo PDFs now begin with **WSPRadar.org reconstruction & comparison**, followed by a descriptive title of the respective RX or TX comparison. Explicit **Referenced publication:** and **Source figure:** lines attach Milazzo's authorship, the publication title and Figure 6 or Figure 7 reference to their source; a **Demo:** line states the comparison context. Presentation-only records in `config/demo_pdf_headers.py` and the shared `scripts/demo_pdf_header.py` helper own this hierarchy and identify WSPRadar as the comparison author in PDF metadata. These two overlays use a compact five-line header to fit the existing page geometry; the earlier evidence-based direction correction remains directly below it. Earlier review records, source evidence, numerical expectations, scientific calculations and all body coordinates remain unchanged.

### Three-panel presentation revision (2026-09-27)

This subsequent presentation revision supersedes the compact geometry described above. Both PDFs and their PNG companions now follow the common demo typography and three-panel format. The five header lines retain their wording and source links, with 27-point WSPRadar and 20-point descriptive headings. The page grows proportionally from 16 × 10.8 to 24 × 16.2 inches; PNG companions are 3840 × 2592 pixels. The source publication JPEGs, scientific inputs, independent expectations, extracted anchors, matching residuals and endpoint ledgers remain byte-identical.

**Panel A - Original image from publication** retains the complete source JPEG, including its original printed title. The evidence-based direction correction is centered below this figure. **Panel B - Reconstruction** plots every existing SQL endpoint at its exact UTC and common 37 dBm-scale SNR, with the same colored circles, production-retained outer rings and both TX diagnostic callouts. The original image is fully opaque underneath these markers, preserving its original dots and connecting lines and using the inverse of the existing source-only paper-axis calibration without fitting a shift or SNR offset. Its plotting area aligns vertically with the original image. The earlier source-image title mask is no longer needed: Panel A preserves the complete source, while Panel B clips its calibrated underlay to the plot limits.

**Panel C - WSPRadar view** uses the production `_selected_evidence_export_recipe` and `render_selected_evidence_export_figure` with the configured three-hour station bins and exact publication interval. It retains the native chronological density, normalization, median, IQR behavior and median-centered nonlinear axis. Individually annotated Joint Spots preserve the old lower scatter's exact values and full locator identities: RX has five values (7, 7, 8, 17 and 22 dB) across DO34 and DO34ir; TX has one DO34ir value of -2 dB. The broader TX fixture's other receivers do not enter this selected-path view. Empty bins remain empty; the single TX cell cannot establish a temporal trend.

Panel B now sits directly above Panel C in the right column. Their plot widths, x positions and exact chronological UTC limits match; their size still derives from the original graph's pixel boundaries after the source image's aspect-ratio inset. The density scale remains beside Panel C, using the same plot-to-legend spacing as the original figure. Panel A and the complete explanatory text occupy the left column. The median, bin-median and exact-Joint-Spot legend is directly below Panel C. The two pre-gate series use an evenly spaced row below Panel B, followed by a separate full-width outer-ring legend row. The legends identify which symbols occur in Panel B or Panel C. Power normalization, gate counts, RX witness-scope limits, exact-cycle TX activity, full-locator pairing and offline execution provenance remain on each page. Original rasters remain embedded images; generated text, report circles, density cells and annotations remain vector graphics with embedded DejaVu fonts. `overlay_summary.json` adds presentation dimensions, selected populations, native density totals, measured layout bounds and panel roles while retaining the prior scientific/provenance fields. `test_milazzo_reference.py` checks the selected population, time boundaries, independent density-cell counts, calibrated underlay, requested panel/legend alignment, PDF structure and publication synchronization.

Faint dashed guides make the survival of individual Joint Spots visible. Each guide binds one eligible production pair to both KP4MD and WB6RQN endpoint reports at its exact UTC and full peer locator. A short same-UTC segment joins the two component SNRs in Panel B; the continuation reaches the unchanged paired Delta SNR in Panel C through its native nonlinear transform. There are five RX guides and one TX guide, recording ten RX and two TX endpoint relationships. Both endpoints must pass production filtering, and their common-power difference must equal the existing native pair metric. Missing/duplicate endpoints, locator mismatches, gate-ineligible reports or inconsistent Delta SNR fail closed. No guide is created from raster proximity, four-minute graphical tolerance or gate survival alone; the nearby 10:34/10:36 TX reports remain unlinked. Guides identify observations and do not interpolate additional measurements or alter selection.
