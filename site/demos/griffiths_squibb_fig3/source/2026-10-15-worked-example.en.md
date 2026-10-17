## 1. Your first WSPRadar result

### A worked example: a low dipole versus a vertical on 40 metres

Start with an existing experiment. You do not need a radio connected or your own WSPR reports.

This example uses **RX Benchmark** to compare reception at two stations. It is one of WSPRadar’s four analysis choices; **TX Benchmark, RX Performance and TX Performance** answer different station questions.

We will follow the experiment from its setup to an overall result, then investigate **where the difference appears, how it changes over time and what individual stations reveal**.

*The figures and numerical results below come from the supplied WSPRadar_export_2026_10_15__10_39.zip[demo export](sandbox:/mnt/data/WSPRadar_export_2026_10_15__10_39.zip).*

### 1.1 What were the operators testing?

In *Improving HF Band SNR*, published in *Practical Wireless* in October 2017, Gwyn Griffiths, G3ZIL, and Nigel Squibb, G4HZX, investigated ways to improve reception on 40 metres. Both used essentially the same homebuilt direct-conversion receiver design, but at different locations and with different antennas. [WSPRnet](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

| Station | Receiving arrangement |
|---|---|
| **G3ZIL — Southampton** | A low horizontal dipole, with its centre raised to about 4 metres and its ends at 1.5 metres. The receiver had been moved to a garden shed. |
| **G4HZX — Beckenham** | A Hustler 5-BTV vertical connected to a ground spike, without radials, at the far end of the garden. |

The paper also records retuning G3ZIL’s dipole on **8 April**. This was an investigation of real installed stations, not an untouched laboratory setup. [WSPRnet](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

**Our question is: how did these two receiving stations compare during April 2017?**

Each station uploaded reports of the WSPR signals it decoded. WSPRadar finds occasions when both stations reported **the same transmitter in the same two-minute WSPR cycle**. That matched comparison is called a **Joint Spot**. Comparing the same transmission avoids comparing one station’s reception on a good afternoon with the other’s reception on a different day. It does not make their locations or local noise identical. 

The quantity we compare is **signal-to-noise ratio, or SNR**: how strongly the signal stands out relative to noise. Higher SNR is better. For this demo:

**ΔSNR = G3ZIL SNR − G4HZX SNR**

A positive difference favours G3ZIL; a negative difference favours G4HZX. Zero means equal SNR in that comparison. 

### 1.2 Load the demo and check its settings

Open **Load Demo** and choose **demo #1: Low Dipole vs Radial-Free Vertical**. Keep the prepared settings and run the RX analysis.

You do not need to enter everything manually. The settings explain what the analysis includes:

| Setting | Value in this demo | What it means |
|---|---|---|
| Analysis | **RX Benchmark** | Compare reception, rather than transmission or standalone Performance. |
| Target | **G3ZIL**, QTH **IO90HW** | The station being evaluated and the centre of the map. |
| Reference | **G4HZX**, reported grid **IO91** | The receiving station used for comparison. |
| Benchmark design | **Reference Setup/Station** | Compare against this particular station, not a neighbourhood reference. |
| Band | **40 m** | Use reports from this band. |
| UTC window | **1 April 2017, 00:00 → 1 May 2017, 00:00** | Examine April’s observations. |
| Reference SNR correction | **0.0 dB** | Apply no additional receiver-chain offset. This does not establish that the two chains were perfectly calibrated. |
| Maximum distance | **10,000 km** | Limit the included transmitter paths. |
| Minimum evidence | **1 Joint Spot per station; 1 joint station per map segment** | Keep sparse results visible; check their counts before interpreting them. |

For the walkthrough, start with **Full Range | All Directions**, **24-hour** segment time bins and **DJ0ABR at JN68NT** selected with **12-hour** station time bins. These values are recorded in the wspradar_config.config[exported configuration](sandbox:/mnt/data/demo1_export/WSPRadar_export_2026_10_15__10_39/config/wspradar_config.config).

**The time bins change the presentation, not the pairing.** A daily median still summarizes comparisons made within individual two-minute WSPR cycles—it does not compare whole-day averages from the two receivers. 

### 1.3 Read the map: is the advantage widespread?







The map is centred on G3ZIL. Compass sectors represent directions from that station; the rings separate distance ranges.

The **sector colours show the station-balanced median ΔSNR**. Each contributing transmitter supplies its own median difference, then WSPRadar takes the middle value across those station medians. A frequently heard transmitter therefore does not dominate the map simply by supplying more reports. 

Read the numerical colour scale: positive values favour G3ZIL, negative values favour G4HZX. Uncoloured sectors have no qualifying comparison, rather than a measured difference of zero.

**The first visible finding is that G3ZIL’s advantage is not geographically uniform.** Many nearer European sectors favour G3ZIL clearly, while the distant west-northwest sector containing many North American stations is much closer to equality.

Use the **Segment Inspector** to look more closely. For example, the exported station entries give:

| Geographic scope | Station-balanced median ΔSNR | Contributing station entries |
|---|---:|---:|
| **0–2,500 km, E** | **+8.0 dB** | **172** |
| **5,000–10,000 km, WNW** | **0.0 dB** | **113** |

These values are derived from the table_station_insights_current_segment.csv[exported Station Insights table](sandbox:/mnt/data/demo1_export/WSPRadar_export_2026_10_15__10_39/benchmark/table_station_insights_current_segment.csv).

**That is already a useful result:** an overall advantage would not mean that G3ZIL heard every direction better. The map helps distinguish an advantage on certain paths from an advantage across the whole observed area.

The station markers carry a different message from the sector colours: they show whether a transmitter was reported jointly or only in other reception categories. We will examine those categories next.

Return the Segment Inspector to **Full Range | All Directions** before continuing, so the following numbers match.

### 1.4 Read Benchmark Evidence: how large is the difference?







This section combines **which signals were decoded** with **the SNR difference where both receivers decoded them**.

#### Which signals supplied a comparison?

In **Decode Outcomes**, the striped bars count station entries; the solid bars count observations.

In this run, **792 station entries—about 70%—supplied at least one Joint Spot**. Together they supplied **57,767 matched comparisons**, approximately **46% of the retained observations**. Those comparisons support the ΔSNR results.

The other station categories add context: **258 entries appeared only at G3ZIL**, **47 only at G4HZX**, and **33 at both, but without a same-cycle pair**. Here, a station entry means a callsign together with its reported locator.

One label needs care: **Both (Async)**. In the station bars, it means both receivers reported that transmitter, but never together in a qualifying cycle. In the observation bars, it also includes unpaired reports from transmitters that supplied Joint Spots at other times. It does **not** mean that the receivers’ clocks were necessarily wrong. The table_drilldown_all_stations_current_segment.csv[exported observations](sandbox:/mnt/data/demo1_export/WSPRadar_export_2026_10_15__10_39/benchmark/table_drilldown_all_stations_current_segment.csv) and the aggregation rules distinguish these two levels. 

The practical point is simple: **SNR differences describe the matched signals, not everything either station heard.** Keep the reception outcomes alongside the SNR result.

#### What is the typical SNR advantage?

The other two panels summarize the matched evidence differently:

**Station Medians: +6.5 dB.** Each transmitter contributes one median difference, regardless of how often it was heard. Most station medians are positive, although some favour G4HZX.

**Joint-Spot ΔSNR: +7.0 dB.** Every matched comparison contributes. Transmitters heard more frequently consequently have more influence.

A *median* is the middle value when the values are placed in order. Here, the two medians are close and both clearly positive: the typical station result and the typical individual comparison tell a compatible story.

**Our first overall conclusion: G3ZIL had a clear SNR advantage in the matched April observations.** The map has already shown where that conclusion needs to be narrowed. Next, check whether the advantage stayed the same throughout the month.

### 1.5 Read Temporal Evidence: did the difference change?







#### Left panel: follow the month

In **Δ SNR over Time**, each circular marker is the median for one day.

The result changes substantially: the daily median rises from **+2 dB on 1 April** to **+9 dB on 15 April**, with fluctuations along the way. Later in the month it generally lies between **+6 and +8 dB**. These values can be checked against the demo1_verified_export_summary.json[daily summaries calculated from the export](sandbox:/mnt/data/demo1_verified_export_summary.json).

**The advantage was not merely a fixed offset between two receivers.** Its size changed over the observation period—something the single monthly median cannot show.

The authors proposed drying soil as an explanation for the first-half trend. The export contains no soil-moisture measurements, so this walkthrough demonstrates the changing SNR difference, not a test of that explanation. [WSPRnet](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

A few display details help you read the chart correctly. The dashed line is the overall **+7 dB Joint-Spot median**. The shaded band contains the middle 50% of the observations in each bin; it shows spread, not a confidence interval. The background colours indicate where observations are concentrated, not which receiver is better. Read the labelled dB values—the vertical scale is nonlinear.

#### Right panel: compare hours of the day

**Δ SNR by UTC Hour** gathers together observations from the same UTC hour across April.

In this full-month view, the hourly median advantage is only about **+1 dB at 01:00–03:00 UTC**, compared with about **+8 dB at 11:00–13:00 UTC**. G3ZIL’s median remains positive in every hourly bin, but the size of its advantage varies considerably.

This is a pattern in the selected observations, not a universal operating schedule. Different transmitters contribute at different hours, and folding the dates together can hide day-to-day differences. Use the chronological view—and individual stations—to investigate it further.

### 1.6 Check Temporal Evidence Coverage: what supports the pattern?







The SNR chart shows the differences. **Temporal Evidence Coverage** shows the observations available to support them.

The upper panels concern transmitting stations; the lower panels concern their transmitter-cycles. Green represents Joint evidence, purple represents Target-only evidence, and the unfilled portions represent Reference-only evidence.

**Every day in this run has matched observations**, but not equally many: the daily total ranges from **860 Joint Spots on 20 April** to **2,903 on 11 April**. The lower coverage on 20 April is visible alongside that day’s SNR result. The UTC-hour panels also show that the early hours have less paired evidence than the late afternoon and evening.

The **Joint Evidence Share** lines describe how much retained evidence forms usable pairs. The station-balanced line gives stations equal weight; the outcome-level line gives observations equal weight. **Neither is a receiver success rate or a “percentage won.”**

Also note the short warning below the figure: cycles without evidence that G3ZIL was operating are excluded. G4HZX’s uptime is not independently established by that rule. Consequently, the one-sided outcomes are useful context, but not a symmetric scoreboard. 

For a first reading, concentrate on one habit: **check whether a striking SNR feature is supported by many comparisons or only a few.**

### 1.7 Open Station Insights: do individual paths agree?

The **Station Insights** table lets you move from a broad summary to a particular transmitter.

The first entries in the exported table include:

| Transmitter | Joint Spots | Median ΔSNR |
|---|---:|---:|
| **OK1FCX — JN79** | 2,763 | **+6 dB** |
| **DJ0ABR — JN68nt** | 2,334 | **+5 dB** |
| **EA4URA — IN80ci** | 2,140 | **+7 dB** |
| **DL5RBD — JN69kb** | 2,005 | **+6 dB** |

These heavily observed paths all favour G3ZIL, but by different amounts. They provide concrete examples behind the positive distribution—not a reason to ignore the stations whose results differ. See the complete table_station_insights_current_segment.csv[Station Insights table](sandbox:/mnt/data/demo1_export/WSPRadar_export_2026_10_15__10_39/benchmark/table_station_insights_current_segment.csv).

Select **DJ0ABR at JN68nt**, already prepared in the demo. It is about **1,064 km** from G3ZIL, at an azimuth of approximately **97°**.







**Selected Station Evidence** now follows one transmitter path, rather than pooling transmitters from many locations.

Its overall median is **+5 dB**, based on **2,334 Joint Spots**. The 12-hour medians fluctuate around zero or below during parts of the first few days, then generally become more positive. The broad early-to-later change therefore appears on this individual path as well as in the all-station view.

The hourly profile differs from the all-station profile. That is informative: a summary across many paths need not describe every path’s daily behaviour.

#### Investigate the conspicuous peak

There is a point at **+25 dB on 20 April**. Did the station suddenly become dramatically better for half a day?

Check the selected path’s coverage before drawing that conclusion.







During **20 April, 12:00–24:00 UTC**, there is just **one Joint Spot**. Its ΔSNR is +25 dB, so it is also that bin’s median. The retained data contain three additional G3ZIL-only observations in that interval, but those cannot supply an SNR difference.

**The +25 dB observation is present in the data. A sustained twelve-hour improvement is not established by it.** This is why a prominent point should be read together with its supporting count.

Across the whole month, this path has **2,334 Joint Spots**, **247 G3ZIL-only observations** and **6 G4HZX-only observations**. The matched evidence is substantial overall, even though individual intervals can be sparse.

### 1.8 Use Drill-Down: check an individual comparison

**Drill-Down** exposes the observations behind the summaries. With DJ0ABR selected, inspect the time and the two SNR columns.

For example, the exported rows include:

| UTC time | G3ZIL SNR | G4HZX SNR | ΔSNR |
|---|---:|---:|---:|
| **1 April, 06:14** | +1 dB | +6 dB | **−5 dB** |
| **1 April, 10:40** | −22 dB | −29 dB | **+7 dB** |
| **20 April, 17:56** | −7 dB | −32 dB | **+25 dB** |

The first comparison favours G4HZX. The second favours G3ZIL: **−22 dB is higher than −29 dB**. The third is the lone paired observation behind the conspicuous 20 April point. All three appear in the table_drilldown_selected_stations.csv[selected-station Drill-Down export](sandbox:/mnt/data/demo1_export/WSPRadar_export_2026_10_15__10_39/benchmark/table_drilldown_selected_stations.csv).

These SNR columns use WSPRadar’s common **1 W reported-power basis**, rather than necessarily reproducing the original reported SNR unchanged. The ΔSNR column subtracts the Reference value from the Target value. 

You do not need to examine thousands of rows. Use Drill-Down when you want to verify an example, understand a surprising point or check exactly what contributed to a summary.

### 1.9 State the result—and preserve it

We can now answer the original station question with more than a single number:

> **During April 2017 on 40 m, G3ZIL’s receiving station showed an overall station-balanced median SNR advantage of +6.5 dB over G4HZX, based on 57,767 same-cycle comparisons from 792 transmitting-station entries within 10,000 km. The advantage was clearer on many nearer European paths than on distant west-northwest paths, and it increased during the first half of April. The DJ0ABR path also favoured G3ZIL overall, while showing substantial variation over time.**

The demo1_verified_export_summary.json[exported figures and checked summaries](sandbox:/mnt/data/demo1_verified_export_summary.json) support that description.

**This is meaningful evidence about how the two installed receiving stations compared.** It is not a measurement of the gain difference between dipoles and verticals in general. Their locations, local noise and complete receiving arrangements remain part of the result.

Save the results package to preserve the configuration, figures and processed observations. For your own experiments, keep station notes alongside it so a later comparison includes what was physically connected and what changed.

You have now followed one result from **the map to the overall comparison, through time and individual stations, down to an actual WSPR observation**. The next chapter applies that process to your own question—whether it concerns **RX or TX, Performance or Benchmark**.