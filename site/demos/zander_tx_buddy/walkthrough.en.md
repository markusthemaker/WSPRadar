<!-- section: hero -->
# Short Portable Vertical vs Larger Vertical

### How much signal do you give up for a smaller antenna?

Two transmitting antennas, the same remote receivers: use WSPRadar to compare their signals, see where the difference changes, and check the observations behind the result.

<!-- section: setup -->
## What were the operators testing?

**Can a short portable vertical compete with a larger antenna on the same radio paths?**

Prof. Jens Zander’s experiment compared two transmitting antennas on Gotland, Sweden. Each antenna was connected to a 200 mW WSPR transmitter, with both beacons configured to transmit during the same two-minute cycles on 20 meters.

**SK0WE/P — Target:** a **Difona HF-P1**, a 2.5 m center-loaded portable vertical with four radials.

**SK0WE/1 — Reference:** a **Hy-Gain AV620**, the larger vertical used for comparison.

This time, the antennas **transmit**. The stations reporting their signals are the global remote receivers.

WSPRadar finds occasions when the **same receiving station reports both transmitters in the same two-minute WSPR cycle**. Each matched comparison is a **Joint Spot**. Comparing at the same receiver and time avoids mixing reports from different receiving setups or different parts of the day.

The quantity we compare is signal-to-noise ratio, or SNR: how strongly a signal stands out relative to noise. Higher SNR is better. For this demo:

**ΔSNR = SK0WE/P SNR − SK0WE/1 SNR**

Positive values favor the short Difona vertical; negative values favor the larger Hy-Gain vertical. Zero means equal SNR in that comparison.

**Our question is: how much difference did the receivers observe, and was that difference the same on every path?**

<!-- section: step-1 -->
## Load the demo and check its settings

Select **Run in WSPRadar App** above to open the prepared **Short Portable Vertical vs Larger Vertical** demo.

You do not need to enter the experiment manually. Check the settings to understand what the analysis includes:

| Setting | Value in this demo | What it means |
|---|---|---|
| Analysis | TX Benchmark | Compare how two transmitting setups were heard. |
| Target | SK0WE/P, QTH JO97 | The short portable vertical being evaluated. |
| Reference | SK0WE/1, QTH JO97 | The larger vertical used for comparison. |
| Benchmark design | Reference Setup/Station | Compare simultaneous transmissions from these two setups. |
| Band | 20 m | Use reports from this band. |
| UTC window | 21 May 2022, 09:45 → 10:30 | Examine the prepared 45-minute window. |
| Reference SNR Correction | None; 0.0 dB | No additional Reference offset is applied. |

The overview includes receivers within **10 000 km** and requires **at least one Joint Spot per contributing station**. Some paths therefore have only a few comparisons; we will check their counts as we go.

Start with **Full Range | All Directions** selected.

<!-- section: step-2 -->
## Read the map: is the difference the same everywhere?

The Azimuthal Map is centered on the Target, SK0WE/P. Compass sectors represent directions from the transmitting station; rings separate distance ranges. **The station markers are remote receivers.**

Each contributing receiver supplies its own median SNR difference. WSPRadar then takes the middle value across those receiver medians. A receiver that reports more frequently therefore does not dominate the sector simply by supplying more observations.

Read the numerical color scale. Negative values favor the larger Reference vertical. Here, every colored sector is negative—but the size of the difference varies.

Use the **Segment Inspector** to compare these examples:

| Geographic scope | Station-balanced median ΔSNR | Receiving-station entries | Joint Spots |
|---|---:|---:|---:|
| 0–2 500 km, SSW | −10.0 dB | 7 | 41 |
| 0–2 500 km, WSW | −4.0 dB | 14 | 74 |
| 5 000–10 000 km, WNW | −4.0 dB | 3 | 10 |

The short vertical’s disadvantage is larger on the sampled south-southwestern European paths than toward west-southwestern Europe or North America. The North American comparison is also supported by fewer receivers and observations.

**Reaching a distant receiver is not the same as matching the other antenna’s SNR.** The short vertical reached North America, but the matched reports still favor the larger vertical overall on those paths.

Uncolored sectors have no qualifying comparison, i.e. a receiving station that has heard both SK0WE/P and SK0WE/1 in the same WSPR cycle. They do not demonstrate that either antenna radiates nothing in those directions.

Return the Segment Inspector to **Full Range | All Directions** before continuing.

<!-- section: step-3 -->
## Read Benchmark Evidence: how large is the difference?

### Which signals supplied a comparison?

In **Decode Outcomes**, the striped bars represent station entries; the solid bars represent observations.

**37 of 85 receiving-station entries—about 44%—supplied Joint Spots.** Together they contributed **166 matched comparisons**, approximately **36% of the retained observations**. These comparisons support the SNR results.

Another **47 entries reported only the larger vertical**, while **one reported only the short vertical**. A station entry means a callsign together with its reported locator.

**One possible explanation is that the short vertical’s signal was too weak for successful WSPR decoding** at some receivers, while the signal from the larger vertical was decoded in the same cycles. This would prevent a Joint Spot at those receivers. The missing reports alone cannot confirm this explanation; interference or gaps in reception and reporting could also contribute.

The **Both (Async)** observation bar includes unpaired reports from receivers that supplied Joint Spots at other times. A receiver can therefore appear in the Joint station category without every one of its reports forming a pair. The label does not necessarily indicate a clock problem.

The practical point is simple: **SNR differences describe the matched signals, not all reception reports.**

### What does the difference between the medians tell us?

**The two summaries agree on which antenna led, but describe a different typical advantage.** Here, the middle receiver result favors the larger vertical by **5 dB**, while the middle individual comparison favors it by **7 dB**. These are two views of the same experiment—not an uncertainty range within which the “true” advantage must lie.

To investigate the difference, open **Station Insights** and compare **Joint Spots** with **Median ΔSNR**. For example, **ON5KQ contributes 11 paired observations with a median of −7 dB**, whereas **SWLEI1763 contributes just one, at −1 dB**. Both contribute one value to Station Medians, but they contribute eleven observations versus one to the Joint-Spot panel.

A more negative Joint-Spot median **can occur when repeatedly observed paths show a larger disadvantage**. However, the spread of observations within each receiver also matters: the gap alone does not prove that the busiest receivers caused it.

### Which result should I use?

Use **Station Medians** for the question, **“How did the antennas compare across the receiving stations, giving each station equal weight?”** Use **Joint-Spot ΔSNR** for **“What was the typical difference across all matched observations?”**

Neither is automatically more accurate. Station balancing prevents frequently reporting receivers from dominating, but a receiver with only one comparison still contributes a station median. Check the counts alongside the result.

For your own comparisons, use this reading guide:

| When the medians… | How to interpret them |
|---|---|
| **Are close and favor the same setup** | The station-level and observation-level summaries tell a similar story. Still check coverage and variation between paths. |
| **Differ but favor the same setup** | Both summaries identify the same leader, but the typical advantage depends on how the evidence is summarized. Inspect report counts, directions and time periods. |
| **Favor different setups** | The overall conclusion depends on the summary chosen. Investigate which paths and periods favor each setup before declaring an overall winner. |

**For this demo, the conclusion is not reversed by the choice of summary:** both medians favor the larger vertical, and all 37 receiver medians are negative. Lead with the **5 dB station-balanced advantage**, while retaining the **7 dB observation-level advantage** as complementary information.

<!-- section: step-3-publication -->
## Verifying WSPRadar against published research

One way to check WSPRadar is to revisit a published experiment and reconstruct its results from historical WSPR observations.

Here, **the original Figure 4, the reconstruction and WSPRadar’s Joint-Spot histogram show the same broad distribution**. The 166 matched comparisons give a **mean difference of −6.8 dB** and a **standard deviation of 3.5 dB**, matching the published figure at its displayed precision. The standard deviation describes the spread of the individual comparisons.\*

[**Explore the original Figure 4, reconstruction and WSPRadar comparison (PDF) ↗**](app/static/reference_figures/zander_fig4_paper_v1/WSPRadar_Demo_Zander_Figure4.pdf)

<!-- section: step-4 -->
## Read Temporal Evidence: did the advantage persist?

### Left panel: follow the observations through time

In **Δ SNR over Time**, each circular marker shows the median difference for a **10-minute interval**.

The four populated intervals have medians of **−8, −6, −8 and −4 dB**. The Reference vertical leads throughout these interval summaries, rather than only at one point in the test.

The result nevertheless varies. Before treating the less-negative final point as an improvement in the short antenna, check how many observations support it.

The dashed line is the overall **−7 dB Joint-Spot median**. The shaded band contains the middle 50% of each interval’s observations; it shows spread, not a confidence interval. Background colors indicate where observations concentrate, not which antenna is better. Read the labeled dB values—the vertical scale is nonlinear.

### Right panel: why is there no UTC-hour profile?

The panel states **“UTC-hour pattern unavailable.”** This run contains observations from only one date; WSPRadar requires evidence from at least two UTC dates for that view.

That is appropriate for this example: a short test on one morning cannot establish a recurring daily pattern. Continue with the chronological evidence.

<!-- section: step-5 -->
## Check Temporal Evidence Coverage: what supports the pattern?

The SNR chart shows the differences. **Temporal Evidence Coverage** shows the observations available to support them.

The upper panel concerns receiving stations; the lower panel concerns **receiver-cycles**—one receiver in one WSPR cycle. Green represents Joint evidence, purple represents Target-only evidence, and the unfilled portions represent Reference-only evidence.

Read the lower panel alongside the SNR chart:

| UTC interval | Joint Spots | Median ΔSNR |
|---|---:|---:|
| 09:45–09:55 | 8 | −8 dB |
| 09:55–10:05 | 70 | −6 dB |
| 10:05–10:15 | 76 | −8 dB |
| 10:15–10:25 | 12 | −4 dB |

The two middle intervals supply **146 of the 166 comparisons**. The final −4 dB point rests on **12 comparisons, all from the 10:16 UTC cycle**. It is not evidence that the short antenna maintained that result for ten minutes.

The **Joint Evidence Share** lines describe how much retained evidence forms usable pairs. The station-balanced line gives receivers equal weight; the outcome-level line gives receiver-cycles equal weight. **Neither is a transmission success rate or a “percentage won.”**

Also note the warning below the figure: cycles without evidence that SK0WE/P was operating are excluded. The Reference transmitter’s uptime is not independently established by that rule, so one-sided outcomes are context rather than a symmetric scoreboard.

**Check the count behind a feature—not just its height or percentage.**

<!-- section: step-6 -->
## Open Station Insights: what did one receiver observe?

The **Station Insights** table lets you move from the overall comparison to a particular receiving station.

Select **ON5KQ at JO10os**, the receiver used in the figures below. It is about **1 267 km** from the Target, at an azimuth of **241°**.

Its **11 Joint Spots** give a median ΔSNR of **−7 dB**. All eleven comparisons favor the larger vertical, with differences ranging from **−12 to −6 dB**.

### Why does the chart show only one median marker?

The selected-station view uses **one-hour bins**, longer than this entire test window. The single marker therefore summarizes all eleven paired observations. It does **not** mean the SNR difference stayed constant throughout the test.

This is a useful distinction: the number of markers depends on the time grouping, while the observation count tells you how much data each marker summarizes.


<!-- section: step-6-coverage -->
## Selected Path Evidence Coverage: ON5KQ

The **Joint Evidence Share is approximately 85%**. Here, that means 11 of the 13 retained receiver-cycles supplied a pair—not that either antenna “won” 85% of the time.

The two Target-only observations do not contradict the negative paired SNR differences. They occurred when only the short antenna’s signal was reported, so no paired difference can be calculated for those cycles.

<!-- section: step-7 -->
## Use Drill-Down: check an individual comparison

**Drill-Down** exposes the observations behind the summaries. With ON5KQ selected, inspect the time and the two SNR columns.

For example, the exported rows include:

| UTC time on 21 May | SK0WE/P SNR | SK0WE/1 SNR | ΔSNR |
|---|---:|---:|---:|
| 09:54 | −13 dB | −1 dB | −12 dB |
| 09:56 | −13 dB | −6 dB | −7 dB |
| 10:02 | −11 dB | −5 dB | −6 dB |
| 10:10 | −14 dB | −4 dB | −10 dB |
| 10:12 | −5 dB | +1 dB | −6 dB |

At 09:54, **−13 − (−1) = −12 dB**. The larger vertical’s signal had the higher SNR at ON5KQ, but **both signals were decoded**. A negative ΔSNR is a relative disadvantage, not a failed reception.

The differences change from one cycle to the next, even though the selected-station chart summarizes them with one median marker.

These are WSPRadar’s exported SNR values. The ΔSNR column subtracts the Reference value from the Target value; no additional Reference correction is applied in this run.

You do not need to inspect every row. Use Drill-Down to verify the arithmetic, understand an unusual observation or check what contributed to a summary.

<!-- section: step-8 -->
## State the result—and preserve it

> **In this 20 m experiment, the larger Hy-Gain AV620 outperformed the short Difona vertical across the matched receiving paths. The 166 same-cycle comparisons from 37 receiving-station entries give a station-balanced median ΔSNR of −5 dB and a Joint-Spot median of −7 dB. Every contributing receiver has a negative median, but the size of the difference varies with direction and from one comparison to the next.**

The short vertical still reached distant receivers, including North America. **Being heard and matching a larger antenna’s SNR are different questions—and WSPRadar lets you examine both.**

This result describes these installed transmitting setups during the selected test. It is not a fixed penalty for every portable vertical or a measurement of antenna gain in every direction.

Save the results package to preserve the settings, figures and processed observations. For your own experiments, record the antennas, transmitter power and installation details alongside the results.

You have now used remote WSPR receivers to compare two transmitting antennas—from the map and overall difference, through time and one receiving station, down to an individual pair of reports.

---

\* **Figure note:** The original figure uses coarser histogram bins and a probability-density scale; WSPRadar uses finer 1 dB bins and percentages. The comparison PDF explains the different presentations. The reconstructed mean and sample standard deviation are −6.78 dB and 3.51 dB, rounding to the published −6.8 dB and 3.5 dB.
