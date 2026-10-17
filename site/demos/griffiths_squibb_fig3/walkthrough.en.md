<!-- section: hero -->

# #1 Low Dipole vs Radial-Free Vertical

A low dipole versus a vertical on 40 m — a real-world comparison using WSPR data.

<!-- section: setup -->

## What were the operators testing?

In *Improving HF Band SNR*, published in *Practical Wireless* in October 2017, Gwyn Griffiths, G3ZIL, and Nigel Squibb, G4HZX, investigated ways to improve reception on 40 metres. Both used essentially the same homebuilt direct-conversion receiver design, but at different locations and with different antennas. [Original paper](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

**G3ZIL — IO90HW:** A low horizontal dipole, with its centre raised to about 4 metres and its ends at 1.5 metres. The receiver had been moved to a garden shed.

**G4HZX — IO91:** A Hustler 5-BTV vertical connected to a ground spike, without radials, at the far end of the garden.

The paper also records retuning G3ZIL’s dipole on **8 April**. This was an investigation of real installed stations, not an untouched laboratory setup.

**Our question is: how did these two receiving stations compare during April 2017?**

Each station uploaded reports of the WSPR signals it decoded. WSPRadar finds occasions when both stations reported **the same transmitter in the same two-minute WSPR cycle**. A **Joint Spot** occurs when both receivers report the same transmitter in the same two-minute WSPR cycle, allowing us to compare their SNR at the same time. Comparing the same transmission avoids comparing one station’s reception on a good afternoon with the other’s reception on a different time or even day. 

The quantity we compare is **signal-to-noise ratio, or SNR**: how strongly the signal stands out relative to noise. Higher SNR is better. For this demo:

**ΔSNR = G3ZIL SNR − G4HZX SNR**

A positive difference favours G3ZIL; a negative difference favours G4HZX. Zero means equal SNR in that comparison.

<!-- section: load -->

## Load the demo and check its settings

Select **Run in WSPRadar App** (above) to open **demo #1: Low Dipole vs Radial-Free Vertical** with its prepared settings and start the RX analysis automatically.

You do not need to enter anything manually. The settings explain what the analysis includes:

| Setting | Value in this demo | What it means |
|---|---|---|
| Analysis | **RX Benchmark** | Compare reception, rather than transmission or standalone Performance. |
| Target | **G3ZIL**, QTH **IO90HW** | The station being evaluated and the centre of the map. |
| Reference | **G4HZX**, reported grid **IO91** | The receiving station used for comparison. |
| Benchmark design | **Reference Setup/Station** | Compare against this particular station, not a neighbourhood reference. |
| Band | **40 m** | Use reports from this band. |
| UTC window | **1 April 2017, 00:00 → 1 May 2017, 00:00** | Examine April’s observations. |

<!-- section: map -->

## Read the map: is the advantage widespread?

The map is centred on the target, G3ZIL. Compass sectors represent directions from that station; the rings separate distance ranges. This is known as an [Azimuthal Map](https://en.wikipedia.org/wiki/Azimuthal_equidistant_projection), widely used in ham radio.

The **sector colours show the station-balanced median ΔSNR** in dB. Each contributing transmitter supplies its own median difference, then WSPRadar takes the middle value across those station medians. A frequently heard transmitter therefore does not dominate the map simply by supplying more reports. 

Read the numerical colour scale: positive values favour G3ZIL, negative values favour G4HZX. Uncoloured sectors have no qualifying comparison, rather than a measured difference of zero.

**The first visible finding is that G3ZIL’s advantage is not geographically uniform.** Many nearer European sectors favour G3ZIL clearly, while the distant west-northwest sector containing many North American stations is much closer to equality.

Use the **Segment Inspector** to look more closely. For example, the exported station entries give:

| Geographic scope | Station-balanced median ΔSNR | Contributing station entries |
|---|---:|---:|
| **0–2 500 km, E** | **+8.0 dB** | **172** |
| **5 000–10 000 km, WNW** | **0.0 dB** | **113** |



**That is already a useful result:** an overall advantage would not mean that G3ZIL heard every direction better. The map helps distinguish an advantage on certain paths from an advantage across the whole observed area.

The station markers carry a different message from the sector colours: they show whether a transmitter was reported jointly or only in other reception categories. We will examine those categories next.

Return the Segment Inspector to **Full Range | All Directions** before continuing, so the following numbers match.

<!-- section: difference -->

## Read Benchmark Evidence: how large is the difference?

This section looks at the Segment you want to investigate, here Full Range | All Directions. It combines **which signals were decoded** with **the SNR difference where both receivers decoded them**.

#### Which signals supplied a comparison?

In **Decode Outcomes**, the striped bars count station entries; the solid bars count observations.

In this run, **792 station entries—about 70%—supplied at least one Joint Spot**. Together they supplied **57 767 matched comparisons**, approximately **46% of the retained observations**. Those comparisons support the ΔSNR results.

The other station categories add context: **258 entries appeared only at G3ZIL**, **47 only at G4HZX**, and **33 at both, but without a same-cycle pair**. Here, a station entry means a callsign together with its reported locator.

One label needs care: **Both (Async)**. In the station bars, it means both receivers reported that transmitter, but never together in a qualifying cycle. In the observation bars, it also includes unpaired reports from transmitters that supplied Joint Spots at other times. It does **not** mean that the receivers’ clocks were necessarily wrong. The [exported observations](/assets/demos/griffiths_squibb_fig3/export/benchmark/table_drilldown_all_stations_current_segment.csv) and the aggregation rules distinguish these two levels. 

The practical point is simple: **SNR differences describe the matched signals, not everything either station heard.** Keep the reception outcomes alongside the SNR result.

#### What is the typical SNR advantage?

The other two panels summarize the matched evidence differently:

**Station Medians: +6.5 dB.** Each transmitter contributes one median difference, regardless of how often it was heard. Most station medians are positive, although some favour G4HZX.

**Joint-Spot ΔSNR: +7.0 dB.** Every matched comparison contributes. Transmitters heard more frequently consequently have more influence.

A *median* is the middle value when the values are placed in order. Here, the two medians are close and both clearly positive: the typical station result and the typical individual comparison tell a compatible story.

**Our first overall conclusion: G3ZIL had a clear SNR advantage in the matched April observations.** The map has already shown where that conclusion needs to be narrowed. Next, check whether the advantage stayed the same throughout the month.

<!-- section: time -->

## Read Temporal Evidence: did the difference change?

#### Left panel: follow the month

In **Δ SNR over Time**, each circular marker is the median for one day.

The result changes substantially: the daily median rises from **+2 dB on 1 April** to **+9 dB on 15 April**, with fluctuations along the way. Later in the month it generally lies between **+6 and +8 dB**.

**The advantage was not merely a fixed offset between two receivers.** Its size changed over the observation period—something the single monthly median cannot show.

The authors proposed drying soil as an explanation for the first-half trend. The export contains no soil-moisture measurements, so this walkthrough demonstrates the changing SNR difference, not a test of that explanation. [Original paper ↗](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

**Space-weather context:** Interestingly, the sparse ΔSNR observations on **20 April 2017** coincides with a documented **G2 (moderate) geomagnetic storm**. NOAA reported G2 conditions at **04:33 UTC**, caused by a coronal-hole high-speed solar-wind stream. Such disturbances can affect HF propagation and may have contributed to the reduced coverage. However, this temporal coincidence does not establish causation, particularly as 22–23 April experienced even stronger daily geomagnetic disturbances.

[**Read NOAA's original 20 April 2017 storm report ↗**](https://www.spaceweather.gov/news/g2-moderate-geomagnetic-storm-conditions-met)

A few display details help you read the chart correctly. The dashed line is the overall **+7 dB Joint-Spot median**. The shaded band contains the middle 50% of the observations in each bin; it shows spread, not a confidence interval. The background colours indicate where observations are concentrated, not which receiver is better. Read the labelled dB values—the vertical scale is nonlinear.

#### Right panel: compare hours of the day

**Δ SNR by UTC Hour** gathers together observations from the same UTC hour across April.

G3ZIL's SNR advantage increases during the first half of April and varies strongly with time of day. The UTC-hour view shows approximately **+7 to +8 dB during daytime**, falling to **+1 to +2 dB after midnight**. This is consistent with changing 40 m propagation: the low dipole favours higher-angle European paths, while the vertical is better suited to lower-angle, long-distance nighttime reception—also observed in the original study (Figure 6).

<!-- section: published-figure3 -->

## Verifying WSPRadar against published research

**How do we verify WSPRadar's results?** One approach is to revisit published WSPR experiments, reconstruct their figures from historical observations, and compare the findings. This helps us validate our calculations, investigate discrepancies, and make the same powerful analysis capabilities available to amateur-radio operators.

Here we compare **Griffiths and Squibb's original Figure 3**, our reconstruction, and **WSPRadar's temporal analysis**. The original dot plot contains many overlapping observations. Our reconstruction adds a density representation to reveal where observations concentrate, while WSPRadar highlights the evolving median SNR difference and its variability. All three show the increasing advantage of G3ZIL during the first half of April.

Some details differ because multiple reports from the same transmission cycle can be combined differently. We document and investigate these discrepancies rather than forcing an exact match.

[**Original Figure 3, reconstruction and WSPRadar comparison (PDF) ↗**](https://wspradar.streamlit.app/~/+/app/static/reference_figures/griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3.pdf)

[**Pairing and multiple reports — detailed investigation (PDF) ↗**](https://wspradar.streamlit.app/~/+/app/static/reference_figures/griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3_diagnostic.pdf)

<!-- section: coverage -->

## Check Temporal Evidence Coverage: what supports the pattern?

The SNR chart shows the differences. **Temporal Evidence Coverage** shows the observations available to support them.

The upper panels concern transmitting stations; the lower panels concern their transmitter-cycles. Green represents Joint evidence, purple represents Target-only evidence, and the unfilled portions represent Reference-only evidence.

**Every day in this run has matched observations from 70 to 172 TX station entries**, but not equally many: the daily total ranges from **860 Joint Spots on 20 April** to **2 903 on 11 April**. The lower coverage on 20 April is visible alongside that day’s SNR result.

**Space-weather context:** The low Joint evidence on **20 April 2017** also coincides with the mentioned documented **G2 (moderate) geomagnetic storm**.

The UTC-hour panels also show that the early hours have less paired evidence than the late afternoon and evening.

The **Joint Evidence Share** lines describe how much retained evidence forms usable pairs. The station-balanced line gives stations equal weight; the outcome-level line gives observations equal weight. **Neither is a receiver success rate or a “percentage won.”**

Also note, cycles without evidence that G3ZIL was operating are excluded. G4HZX’s uptime is not independently established because WSPRadar filters on Target activity. Consequently, the one-sided outcomes are useful context, but not a symmetric scoreboard. 

For a first reading, concentrate on one habit: **check whether a striking SNR feature is supported by many comparisons or only a few.**

<!-- section: stations -->

## Open Station Insights: do individual paths agree?

The **Station Insights** table lets you move from a broad summary to a particular transmitter.

Select **DJ0ABR at JN68nt**, already prepared in the demo. It is about **1 064 km** from G3ZIL, at an azimuth of approximately **97°**.







**Selected Station Evidence** now follows one transmitter path, rather than pooling transmitters from many locations.

Its overall median is **+5 dB**, based on **2 334 Joint Spots**. The 12-hour medians fluctuate around zero or below during parts of the first few days, then generally become more positive. The broad early-to-later change therefore appears on this individual path as well as in the all-station view.

The hourly profile differs from the all-station profile. That is informative: a summary across many paths need not describe every path’s daily behaviour.

#### Investigate the conspicuous peak

There is a point at **+25 dB on 20 April**. Did the station suddenly become dramatically better for half a day?

Check the selected path’s coverage before drawing that conclusion.







During **20 April, 12:00–24:00 UTC**, there is just **one Joint Spot**. Its ΔSNR is +25 dB, so it is also that bin’s median. As noted earlier, NOAA reported a **G2 (moderate) geomagnetic storm** on the same day, which may have affected HF propagation.

Across the whole month, this path has **2 334 Joint Spots**, **247 G3ZIL-only observations** and **6 G4HZX-only observations**. The matched evidence is substantial overall, even though individual intervals can be sparse.

<!-- section: drilldown -->

## Use Drill-Down: check an individual comparison

**Drill-Down** exposes the observations behind the summaries. With DJ0ABR selected, inspect the time and the two SNR columns.

For example, the exported rows include:

| UTC time | G3ZIL SNR | G4HZX SNR | ΔSNR |
|---|---:|---:|---:|
| **1 April, 06:14** | +1 dB | +6 dB | **−5 dB** |
| **1 April, 10:40** | −22 dB | −29 dB | **+7 dB** |
| **4 April, 11:58** | −16 dB | −16 dB | **0 dB** |
| **8 April, 11:48** | −13 dB | −25 dB | **+12 dB** |
| **12 April, 11:58** | −8 dB | −8 dB | **0 dB** |
| **16 April, 11:58** | −13 dB | −18 dB | **+5 dB** |
| **19 April, 12:00** | −5 dB | −20 dB | **+15 dB** |
| **20 April, 17:56** | −7 dB | −32 dB | **+25 dB** |
| **24 April, 11:58** | −23 dB | −23 dB | **0 dB** |
| **28 April, 11:58** | −10 dB | −14 dB | **+4 dB** |

The first comparison favours G4HZX. The second favours G3ZIL: **−22 dB is higher than −29 dB**.

The **20 April, 17:56 UTC** observation stands out at **+25 dB**: the export lists −7 dB for G3ZIL and −32 dB for G4HZX. It is the lone paired observation behind the conspicuous 20 April point.

These SNR columns use WSPRadar’s common **1 W reported-power basis**, rather than necessarily reproducing the original reported SNR unchanged. The ΔSNR column subtracts the Reference value from the Target value. 

You do not need to examine thousands of rows. Use Drill-Down when you want to verify an example, understand a surprising point or check exactly what contributed to a summary.

<!-- section: takeaways -->

## State the result—and preserve it

We can now answer the original station question with more than a single number:

> **During April 2017 on 40 m, G3ZIL’s receiving station showed an overall station-balanced median SNR advantage of +6.5 dB over G4HZX, based on 57 767 same-cycle comparisons from 792 transmitting-station entries within 10 000 km. The advantage was clearer on many nearer European paths than on distant west-northwest paths, and it increased during the first half of April. The DJ0ABR path also favoured G3ZIL overall, while showing substantial variation over time.**

**This is meaningful evidence about how the two installed receiving stations compared.** It is not a measurement of the gain difference between dipoles and verticals in general. Their locations, local noise and complete receiving arrangements remain part of the result.

Save the results package to preserve the configuration, figures and processed observations. For your own experiments, keep station notes alongside it so a later comparison includes what was physically connected and what changed.

You have now followed one result from **the map to the overall comparison, through time and individual stations, down to an actual WSPR observation**.

