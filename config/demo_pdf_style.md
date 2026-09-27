# Demo PDF style specification

This is the common authoring specification for WSPRadar demo PDFs. Follow it when creating or revising a demo figure. It is a Markdown specification for authors and figure builders; renderers do not read this file automatically. Apply it as each existing demo is reviewed.

## Panel roles

0. A standard publication comparison uses these panels:
   - **Panel A — Original image from publication:** show the original paper figure. Preserve its source image and scientific content; identify any enlargement, crop or comparison overlay.
   - **Panel B — Reconstruction:** reconstruct the observations using the WSPRadar production processing and analysis pipeline. Paper-derived annotations and expected reference tables are checks, not substitutes for processing the source reports. Identify any additional presentation operation, such as smoothing, and keep the underlying paired observations unchanged.
   - **Panel C — WSPRadar view:** use the WSPRadar native view, retaining its statistics, binning, colours and axis transformations. Explain any nonlinear axis so readers compare labelled values correctly.

Diagnostics may use fewer panels when their purpose requires it. Give each panel an explicit heading that describes what it contains. In explanatory prose, write **Panel A**, **Panel B** or **Panel C** rather than a bare letter; compact legend scope labels such as **(B)** are acceptable when their meaning is clear.

## Visual style

1. **DejaVu Sans**, white background, dark navy text. Use regular body text and bold headings. Muted slate may distinguish supporting notes. Preserve native WSPRadar chart colours; use consistent annotation colours and reinforce colour with symbols or labels.
2. **Centered hierarchy:** **WSPRadar.org reconstruction & comparison** → descriptive title → **Referenced publication:** → **Source figure:** → **Demo:**. The first line identifies the producer and purpose of this comparison sheet; the second names the scientific quantity or comparison shown, without a detached publication figure number. Put the cited authors and year beside the printed paper title in the explicitly labelled publication line, with the paper title in italics. Keep author names and relevant callsigns within that source citation, never as a standalone document byline. Put the bold source figure number and page, when established, beside the journal/date/pages, article identifier or version in the source-figure line. Retain the concise date/band/comparison details in the demo line. Link the WSPRadar heading to WSPRadar.org and both citation lines to the publication. PDF document properties must likewise identify WSPRadar as the comparison author. Shared rendering belongs to `scripts/demo_pdf_header.py`; `config/demo_pdf_headers.py` owns the presentation-only wording, source metadata and per-page header layout.
3. **Consistent typography:** WSPRadar heading **25–28 pt**, descriptive title **19–21 pt**, panel headings **15–17 pt**, explanatory text and legends **12–14 pt**. Use comparably readable axis labels and ticks. Confirm legibility at the intended display or slide size; retain the agreed page aspect ratio for each figure. The Milazzo Figure 6 and 7 revision of 27 September 2026 uses this standard typography and three-panel layout, superseding the earlier compact-header exception. Its 24 × 16.2-inch pages preserve the previous 16:10.8 aspect ratio and complete direction-correction note. Preserve every report, gate marker, diagnostic annotation and paired observation when reorganizing these comparisons.
4. **Aligned panels and one shared legend where applicable**, explicitly identifying symbols specific to a panel. Align plot edges and use consistent spacing between headings and plots. Group related legend entries; list numbered regions in order. Explain symbols such as density peaks, maximum-density stars, point matches, medians and IQR bands without implying that every symbol occurs in every panel.
5. **Separate colour scales where calculations differ**, with clear units and axis explanations. State the direction of ΔSNR and the meaning of its sign. Identify smoothing and density normalization where relevant. Preserve the distinction between comparison regions and confidence intervals, and between matching plotted positions and identifying the same transmission.
6. **Vector graphics and embedded fonts**, retaining the original publication image. Export text, reconstruction plots, markers, lines and annotations as vector content. Keep the original publication image as its source raster; do not create the entire PDF from a screenshot or completed PNG.

## Explanatory text and page layout

- Explain what readers see and how to interpret it. Keep implementation and capture provenance in the supporting documentation unless the reader needs it to understand the comparison.
- Public PDFs do not need labels such as "frozen demo", "frozen reports" or "fixture". Use "database reports" when that describes the source. Retain technical provenance and scientific checks in the supporting files.
- Preserve approved wording and scientific content during incremental edits; change or remove content only as requested or as needed to integrate approved changes.
- Use consistent margins and clear separation between plots, legends and explanatory text. Check for clipped text, overlapping labels and crowded colour bars.
- Add the right-aligned footer **WSPRadar.org by Dr. Markus Brosch (DL1MKS)** to every demo PDF, using the shared `scripts/demo_pdf_footer.py` helper. Use 12 pt DejaVu Sans in dark navy and align it with the approved right margin. Place it beside existing bottom notes when space permits, retaining those notes unless their removal was explicitly requested.
- Preserve the agreed aspect ratio. Figure 3 and its diagnostic are square; Figure 6 retains its landscape format. Do not force diagnostics into a three-panel layout or change a reviewed figure's aspect ratio without agreement.
- For Milazzo Figures 6 and 7, retain the fully opaque original dots and lines beneath Panel B's vector reconstruction markers. Stack Panel B directly above Panel C with identical plot widths, x positions and chronological UTC limits; use Panel A's actual printed graph dimensions after its source-image aspect inset as the size reference. Keep Panel A and the explanatory text in the left column, and retain the density scale beside Panel C. Put each panel's legend next to its own evidence: native statistics below Panel C; pre-gate series and gate rings in spacious rows below Panel B. Center the direction-correction note below Panel A. Faint dashed identity guides may join only production-eligible Joint Spots to both exact same-cycle, full-locator endpoints; graphical proximity and gate survival alone must not create a guide. Keep guide lines behind the captions and legend backgrounds and explain that they are not interpolated observations.

## Filenames and verification

- Keep intermediate PDFs, renders and comparison previews in an automatically
  cleaned system temporary directory, or in `.tmp/<task>/` while review is in
  progress. Remove the task's scratch files after verification and delivery.
  Never use root `output/` or commit previews. Preserve final approved PDFs and
  required source evidence in their established authoritative locations.
- Use `WSPRadar_Demo_LeadAuthor_FigureX.pdf`.
- For diagnostics, append `_diagnostic` before `.pdf`.
- Keep the demo link, generated PDF filename, published copy and presentation manifest consistent.
- Render and inspect the final PDF. Check page dimensions, embedded fonts, text bounds, legend meanings, links and colour scales.
- Verify that presentation edits preserve the selected observations, calculations, source evidence and numerical expectations. Keep source figures, paper annotations and independent checks separate from reconstruction outputs.


### Optional four-panel mapping comparison

For the Vanhamel Figure 6 comparison, preserve the original publication in **Panel A** and the production reception-order reconstruction in **Panel B**. Add **Panel C** as an explanatory mapping view: the unchanged black Delta-SNR trace over the native UTC-bin density values, projected onto each bin’s exact reception-number span. Use the original native UTC view as **Panel D**. The original three-panel layout remains the default for comparisons that do not need this additional step.

Panels C and D must retain identical density values, masks, colours and normalization, with matching one-based bin labels. Empty UTC bins have zero reception width in Panel C and retain their elapsed duration in Panel D. Panel C uses a linear dB axis; Panel D retains the native axis transformation, summaries and rendering rules. Label the colour scale as shared when both panels use the same calculation. Preserve the agreed page aspect ratio and increase physical page dimensions as needed for readable typography.
