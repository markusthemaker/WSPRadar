# Source and handoff notes

## Scope

This page covers the **2022 Zander Experiment A**: SK0WE/P (Difona HF-P1 portable vertical) versus SK0WE/1 (Hy-Gain AV620), 20 m, 21 May 2022. It does not cover Zander’s T2FD experiment or the later 2023 comparison.

The page text is in `Zander_Portable_Vertical_Comparison.md`. All six figure files in `assets/` are unchanged copies from the supplied export, not new renderings. Exported tables and configuration are preserved in `sources/`.

## Source basis

Primary run: `WSPRadar_export_2026_10_16__19_00.zip`, exported at 2026-10-16T19:00:44Z, WSPRadar v1.0 RC2. The supplied configuration and metadata establish the antenna assignments, callsigns, settings, analysis mode and figure-reconstruction reference. Numerical results were recalculated from the exported CSV tables and checked against the figures.

The original paper linked in the configuration is Jens Zander, *Simple HF antenna efficiency comparisons using the WSPR system* (2022), arXiv:2209.08989: https://arxiv.org/abs/2209.08989 . Its experimental setup confirms the Difona model, 2.5 m length, four radials, Reference antenna, Gotland location and 200 mW transmitters. Figure 4, on PDF page 4, was visually checked; it displays mean −6.8 dB and sigma 3.5 dB. No broader external antenna-performance claims were added.

## Page wiring

Use the existing application demo profile **`zander_tx_buddy`** for the Run in WSPRadar App action. The page uses its new reader-facing title; the existing internal profile ID is unchanged. No unverified launch URL or new parameter syntax has been invented.

Use **Reference Setup/Station** in the settings table. This matches the actual `mode: reference_station` configuration and run metadata; do not substitute another benchmark mode based on unrelated demo copy.

The exported selected-station figures use **ON5KQ (JO10os)**. However, the saved configuration has `selected_stations: null`; the selected receiver is recorded in the run metadata. The page therefore explicitly asks the visitor to select ON5KQ instead of promising that the preset preselects it. Set the selection explicitly during implementation only when it is intended to become part of the preset.

Preserve the supplied temporal settings: **10-minute Segment Inspector bins** and **one-hour selected-station bins**. The single selected-station marker is intentional. The UTC-hour panels are unavailable because the run spans one UTC date; the page does not invent an hourly or day/night pattern.

## Figure 4 comparison link

The input configuration supplies this existing application path:

`app/static/reference_figures/zander_fig4_paper_v1/WSPRadar_Demo_Zander_Figure4.pdf`

It is retained in the Markdown and should be connected through the website’s existing static-file/link handling. The comparison PDF itself is not contained in the supplied export and is not included in this package. Its description comes from the supplied profile. The existing hosted comparison PDF could not be retrieved in this environment; the original publication figure and the exported numerical results were checked independently. No new comparison PDF has been created or passed off as the existing one.

## Numerical checks

`verification.json` contains the calculations and the input archive checksum. Core results are 166 Joint Spots from 37 contributing receiving-station entries, among 457 retained observation rows and 85 total receiving-station entries. The median of receiver medians is −5.0 dB, the pooled Joint-Spot median −7.0 dB, the pooled mean −6.7831325 dB, and the sample standard deviation 3.5146385 dB. Every contributing receiver median is negative.

The map examples use the median of receiver medians, not the pooled observation median. Directions use the compass sectors centred at multiples of 22.5 degrees. The bins are anchored to 09:45 UTC, as in the exported figure; the four populated bins contain 8, 70, 76 and 12 Joint Spots. All twelve comparisons in the last populated bin occurred at 10:16 UTC. The broader input window extends to 10:30, but the retained paired observations do not.

ON5KQ contributes 11 paired and two Target-only observations. Its paired differences range from −12 to −6 dB, with median −7 dB. Its one-hour aggregation should not be described as a flat observed time series.

## Interpretation boundaries

The copy treats the results as relative performance on sampled paths, not a direction-independent antenna-gain or efficiency measurement. A negative ΔSNR is not a failed decode. Joint Evidence Share is not transmission success, and the Target-activity gate does not establish symmetric uptime for both transmitters. Paper comparisons remain in the short reconstruction callout and its footer note.
