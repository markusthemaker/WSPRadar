<!-- section: hero -->
# A 90° Antenna Rotation, a 3 dB Difference

### See how antenna orientation changes reception

Keep one antenna fixed, rotate the other, and follow the difference.

<!-- section: setup -->
## What were the operators testing?

**Can turning a receiving antenna through 90° make a visible difference in WSPR results?**

Jurgen Vanhamel, Walter Machiels and Hervé Lamy compared two receiving setups on 160 meters:

**ON4AWM0 — Target:** an ITA LWA II long-wire antenna, kept in the same orientation throughout the experiment.

**ON4AWM1 — Reference:** an adapted shorted dipole, initially parallel to the long wire and then **rotated 90° in the horizontal plane after the first week**.

Both receivers reported WSPR signals throughout the comparison. WSPRadar matches reports of the **same transmitter and reported locator in the same two-minute cycle**. A **Joint Spot** occurs when both receivers report the same transmitter in the same two-minute WSPR cycle, allowing us to compare their SNR at the same time.

SNR describes how strongly a signal stands out relative to noise. Higher SNR is better. Our comparison is:

**ΔSNR = ON4AWM0 SNR − (ON4AWM1 SNR + SNR Correction)**

Positive values favor the long-wire receiving setup; negative values favor the dipole receiving setup. **The dipole is the antenna that changes—not the long wire.**

The companion [**One Antenna, Two Receivers — Why Calibration Matters**](/en/demos/vanhamel_rx_calibration/) explains how to check the receiving equipment first. Here, the prepared demo loads a receiver correction so we can concentrate on the antenna comparison.

**Our question is: where, when and by how much did relative reception change?**

<!-- section: step-1 -->
## Load the demo and check its settings

Select **Run in WSPRadar App** above to open the prepared antenna-rotation demo.

| Setting | Value in this demo | What it means |
|---|---|---|
| Analysis | RX Benchmark | Compare reception by the two antenna setups. |
| Target | ON4AWM0, QTH JO20OT | The fixed long-wire setup and map center. |
| Reference | ON4AWM1, reported grid JO20 | The setup with the rotated dipole. |
| Benchmark design | Reference Setup/Station | Compare against this particular Reference. |
| Band | 160 m | Use reports from this band. |
| UTC window | 1 May 2021, 17:15 → 15 May 2021, 07:00 | Cover both antenna orientations. |
| Reference SNR Correction | +1.6 dB; established offset\* | Account for the receiving-chain difference. |

The overview includes transmitters within **5 000 km**. The chronological charts use **12-hour bins**, and **M7AEO at IO82** is preselected for the individual-station walkthrough.

Start with **Full Range | All Directions** selected.

<!-- section: step-2 -->
## Read the map: does every direction tell the same story?

The Azimuthal Map is centered on ON4AWM0. Compass sectors represent directions from the Target; rings separate distance ranges.

Each contributing transmitter supplies its own median SNR difference, then WSPRadar takes the middle value across those station medians. Frequently heard transmitters therefore do not dominate a sector simply by supplying more reports.

Read the numerical color scale: positive values favor the long wire; negative values favor the dipole. Uncolored sectors have no qualifying comparison, rather than a measured difference of zero.

The result varies with direction. For example:

| Geographic scope | Station-balanced median ΔSNR | Contributing station entries |
|---|---:|---:|
| 0–2 500 km, ENE | +4.4 dB | 4 |
| 0–2 500 km, WNW | +0.4 dB | 17 |
| 0–2 500 km, SSE | −3.6 dB | 4 |

The long-wire setup leads in some sampled directions, while the dipole leads in others. **There is no single advantage that describes every path.**

Use the **Segment Inspector** to explore a sector and check how many stations and Joint Spots support it. This demo allows stations with as few as one Joint Spot, so a strong color does not necessarily mean strong supporting evidence.

Remember that this map combines both weeks. To see the change associated with rotation, we will also need the chronological view.

Return to **Full Range | All Directions** before continuing.

<!-- section: step-3 -->
## Read Benchmark Evidence: how large is the overall difference?

### Which signals supplied a comparison?

In **Decode Outcomes**, the striped bars count station entries; the solid bars count observations.

**60 of 75 station entries—80%—supplied Joint Spots.** Together they contributed **5 379 matched comparisons**, approximately **75% of the retained observations**. These comparisons support the SNR results.

Another 13 station entries appeared only at ON4AWM0, and two only at ON4AWM1. Here, a station entry means a callsign together with its reported locator.

The observation-level **Both (Async)** category contains unpaired reports from transmitters heard by both receivers. A transmitter can supply Joint Spots at some times and unpaired reports at others.

The practical distinction is simple: **SNR differences describe the matched signals, not everything either receiver heard.**

### What is the typical advantage?

**Station Medians: +1.4 dB.** Each transmitter contributes one median difference, regardless of how often it was heard.

**Joint-Spot ΔSNR: +2.4 dB.** Every matched comparison contributes, giving frequently heard transmitters greater influence.

A median is the middle value when the values are placed in order. Both summaries favor the long-wire receiving setup overall. They need not be identical because they weight the observations differently.

#### What does the difference between the medians tell us?

**The two summaries agree on which setup leads, but describe a different typical advantage.** Giving each transmitter equal weight produces +1.4 dB; including every matched observation produces +2.4 dB. These are complementary results—not an uncertainty range within which the “true” advantage must lie.

A more positive Joint-Spot median can occur when paths or periods with larger advantages contribute more observations. However, the spread of differences within each transmitter’s reports also matters: **the gap alone does not tell us which stations or periods caused it.**

To investigate, open **Station Insights** and compare **Joint Spots** with **Median ΔSNR**. A transmitter with hundreds of paired observations contributes one median to Station Medians, but hundreds of observations to the Joint-Spot panel. Check the counts, too: equal station weight does not mean equally well-supported station results.

#### Which result should I use?

Use **Station Medians** to answer, **“How did the receiving setups compare across transmitters, giving each transmitter equal weight?”** Use **Joint-Spot ΔSNR** to answer, **“What was the typical difference across all matched observations?”**

Here, both favor the long wire. The difference between them tells us that the size of the overall advantage depends on how the evidence is summarized—not that either result is wrong.

These are results for the **whole two-week period**, combining both dipole orientations. **Neither overall median—and not the 1 dB gap between them—measures the rotation effect.** They do not yet tell us how much changed when the dipole was rotated. For that, follow the results through time.

<!-- section: step-4 -->
## Read Temporal Evidence: when did the difference change?

### Left panel: follow the experiment

In **Δ SNR over Time**, each circular marker shows the median difference for a 12-hour interval.

Look for the upward change around **8 May**. Several well-populated early intervals lie near **−0.6 dB**; later intervals often lie around **+2.4 to +4.4 dB**. Relative reception has shifted toward the fixed long-wire setup.

The difference was therefore not constant throughout the experiment. A single overall median would conceal that change.

The dashed line is the **+2.4 dB overall Joint-Spot median**. The shaded band covers the middle 50% of observations in each bin: it shows spread, not a confidence interval. Background colors show where observations concentrate. Read the labeled dB values—the vertical scale is nonlinear.

This view pools transmitters, with more frequently heard stations contributing more observations. We will shortly check whether the change also appears on one individual path.

### Right panel: compare hours of the day

**Δ SNR by UTC Hour** combines observations from the same UTC hour across the run.

Most paired evidence comes from the evening, night and early morning. Daytime hours have very little evidence, so isolated points deserve a closer look. This is consistent with the drastically changing propagation between daylight and dark due to the behavior of the Earth's ionosphere.

This hourly profile also combines both antenna orientations. Use it to explore the daily pattern; use the chronological chart to follow the rotation experiment.

<!-- section: step-5 -->
## Check Temporal Evidence Coverage: what supports the pattern?

The SNR chart shows the differences. **Temporal Evidence Coverage** shows the observations available to support them.

The upper panels concern transmitting stations; the lower panels concern transmitter-cycles. Green represents Joint evidence, purple represents Target-only evidence, and the unfilled portions represent Reference-only evidence. The UTC-hour panels show averages across the run.

The repeated overnight coverage supports the broad change. Daytime results are much less consistently sampled.

For example, the **+7.4 dB point at 13:00 UTC** in the all-station SNR profile is supported by **just one Joint Spot across the entire run**. That is a real observation, but not enough to establish a typical daytime advantage.

The **Joint Evidence Share** lines describe how much retained evidence forms usable pairs. The station-balanced line gives stations equal weight; the outcome-level line gives observations equal weight. **Neither is a receiver success rate or a “percentage won.”**

Also note, cycles without evidence that ON4AWM0 was operating are excluded. ON4AWM1’s uptime is not independently established because WSPRadar filters on Target activity, so the one-sided outcomes are useful context rather than a symmetric scoreboard.

**Check the count behind a feature—not just its height or percentage.**

<!-- section: step-6 -->
## Open Station Insights: does the change appear on one path?

The **Station Insights** table lets you move from the broad comparison to one transmitting station.

Select **M7AEO at IO82**, already prepared in the demo. It is about **598 km** from ON4AWM0, at an azimuth of **291°**. This path supplies **1 441 Joint Spots**.

In the chronological chart, most early 12-hour medians are below zero. After the change around 8 May, the medians become positive; many later intervals settle around **+2.4 dB**.

The upward change therefore appears on this individual path as well as in the all-station overview. A change in which transmitters contribute to the pooled view is not the whole explanation.

Keep the sign in mind: **the fixed long-wire setup becomes stronger relative to the rotated dipole setup**. This is not a 3 dB improvement for the antenna that was turned.

<!-- section: step-6-coverage -->
## Selected Path Evidence Coverage: M7AEO

Across the run, this path has **1 441 Joint Spots**, **109 Target-only** observations and **five Reference-only** observations.

Check these counts alongside the SNR chart. The well-populated overnight intervals support the broad change, but not every point has equal support: the **9 May, 05:15–17:15 UTC** bin has a **+4.4 dB median based on only one Joint Spot**.

<!-- section: step-6-publication -->
## Verifying WSPRadar against published research

One way to check WSPRadar is to revisit a published experiment and compare its results with a reconstruction from historical WSPR observations.

For M7AEO, **the original Figure 6, our reconstruction and WSPRadar’s chronological chart show the same upward transition**. The reconstructed before-and-after medians are **−0.6 dB and +2.4 dB—a 3.0 dB difference**.†

The publication plots successive receptions, while WSPRadar groups observations by UTC time. The charts therefore look different, but reveal the same change in relative reception.

[**Explore the original Figure 6, reconstruction and WSPRadar comparison (PDF) ↗**](/assets/demos/vanhamel_rx_buddy/WSPRadar_Demo_Vanhamel_Figure6.pdf)

<!-- section: step-7 -->
## Use Drill-Down: check an individual comparison

**Drill-Down** exposes the observations behind the summaries. With M7AEO selected, inspect the time and the two SNR columns.

For example, the table includes:

| UTC time | ON4AWM0 SNR | Corrected ON4AWM1 SNR | ΔSNR |
|---|---:|---:|---:|
| 1 May, 18:24 | −20.0 dB | −19.4 dB | −0.6 dB |
| 7 May, 20:04 | −12.0 dB | −12.4 dB | +0.4 dB |
| 8 May, 20:16 | −16.0 dB | −20.4 dB | +4.4 dB |
| 14 May, 20:04 | −17.0 dB | −20.4 dB | +3.4 dB |

The first comparison favors the dipole setup. The 8 May comparison favors the long-wire setup: **−16.0 − (−20.4) = +4.4 dB**.

These are WSPRadar’s processed SNR values. The Reference column already includes the correction; do not add it again.

You do not need to inspect thousands of rows. Use Drill-Down to verify the arithmetic, understand a surprising point or check what contributed to a summary. The broad before-and-after result comes from the full groups of observations, not from choosing two individual rows.

<!-- section: step-8 -->
## State the result—and preserve it

> **WSPRadar reveals a clear change in relative reception around 8 May. On the M7AEO path, 1 441 same-cycle comparisons reconstruct a 3 dB upward shift associated with rotating the Reference dipole. Across the broader selection, 5 379 Joint Spots from 60 transmitting-station entries give a full-period station-balanced median of +1.4 dB in favor of the long-wire setup. Pooling all Joint Spots gives a median of +2.4 dB. Stations contributing more observations have more influence in this pooled distribution; the station-balanced calculation gives each station’s median equal weight. The map and time views show why that overall result does not describe every path or every period.**

You have now followed an antenna change from the map to the overall comparison, through time and one transmitting station, down to an individual WSPR observation.

---

\* **Calibration note:** This May example uses +1.6 dB, rounded from the 1.57 dB calibration documented on the authors’ [website](https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-station-compare-app/wspr-station-compare-add-on#h.jj74yhtflcn2). The [February calibration walkthrough](/en/demos/vanhamel_rx_calibration/) gives a +1.2 dB mean, matching the paper’s text. Using +1.2 dB here would move all differences 0.4 dB higher, but would not change the 3 dB step.

† **Reconstruction note:** The two medians split the reconstructed observations at the Figure 6 boundary: the first 750 Joint Spots and the remaining 691. This is a reconstruction boundary, not an independently logged rotation time.
