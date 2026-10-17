<!-- section: hero -->
# #6 Prof. Zander et al. TX Antenna Comparison: Short Portable Vertical vs 5/8 λ Vertical

<!-- section: setup -->
## Reproduce this setup

Select ‘Run in WSPRadar App’ to load this demo and start its analysis.

<!-- section: step-1 -->
## Identify the two transmitting setups

The Target is **SK0WE/P's short Difona vertical** and the Reference is **SK0WE/1's Hy-Gain AV620**. Both are at JO97. Preserve the installed **21 May 2022, 09:45–10:30 UTC** window when following the published comparison. A Joint Spot requires reports of both transmitters from the same remote receiver and locator in the same two-minute cycle.

<!-- section: step-2 -->
## Compare histograms with the same observation unit

In **Segment Inspector → Benchmark Evidence**, keep all directions and distance ranges selected and use the **Joint-Spot Δ SNR** histogram. Its mean is **−6.78 dB** across **166 joint receiver-cycles**, favoring the Reference. The **Station Medians (Δ SNR)** histogram gives each receiver one median instead; use it to inspect a different weighting, not as a like-for-like replacement for the publication's Joint-Spot distribution.

<!-- section: step-3 -->
## Understand the different bar heights

The publication and native WSPRadar histogram use different bin widths and vertical units. The reconstruction panel connects the coarser, density-based publication view to WSPRadar's **1 dB bins** and percentage of matched observations. Compare bin boundaries and axis labels before comparing bar heights. The finer native display does not imply a different set of paired observations.

<!-- section: step-4 -->
## Explore where the relative advantage varies

Use **Map View** to compare the sampled North American paths with European directions, then examine those directions in **Segment Inspector**. Map sectors summarize receivers' median ΔSNR values with equal receiver weight; they are not the all-Joint-Spot mean. Select individual receivers in **Station Insights** to inspect contributing paths. Uncolored sectors lack a supported estimate and do not demonstrate antenna nulls.
