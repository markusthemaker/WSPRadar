<!-- section: hero -->

# Short Portable Vertical vs Larger Vertical

### How much performance do you trade for portability?

Two transmitting antennas, the same remote receivers: use WSPRadar to compare their signals, see where the difference changes, and check the observations behind the result. Follow the signal from Europe to North America, then use the time charts and one receiver to understand what the numbers mean.

Throughout this guided demo, **ΔSNR compares signal quality when the same receiver decoded both transmissions in the same cycle**, while **ΔDecode compares observed report counts, including reception of only one setup**. Together, they help distinguish signal margin, additional reports and the number of receivers reached.

<!-- section: summary -->

## The findings at a glance

| Finding | What it describes |
| :--- | :--- |
| **−5.0 dB across receiver results** | The larger vertical led across **37 qualifying receivers**, contributing **166 spot pairs**. Each receiver has equal influence on this summary. |
| **North America was still reached** | Three qualifying receivers about **6 400–6 500 km** away give a segment median of **−4 dB**. The short vertical was heard, with a lower paired SNR. |
| **Decode counts need time context** | **202 short-vertical reports versus 528 larger-vertical reports** were recorded. Their reporting spans differ; check the timeline before attributing the full difference to the antennas. |

<!-- section: setup -->

## What were the operators testing?

**Can a short portable vertical compete with a larger antenna on the same radio paths?**

Prof. Jens Zander’s experiment compared two transmitting antennas on Gotland, Sweden. Each antenna was connected to a nominal **200 mW WSPR transmitter**, with both beacons configured to transmit during the same two-minute cycles on 20 meters.

- **SK0WE/P — Target:** a **Difona HF-P1**, a 2.5 m center-loaded portable vertical with four radials.
- **SK0WE/1 — Reference:** a **Hy-Gain AV620**, the larger vertical used for comparison.

In this **TX Benchmark**, Target and Reference are the **two transmitting setups**. The stations reporting their signals are the global remote receivers. A **station entry** identifies a receiver by its callsign and reported locator. A **spot** is a reception report; repeated spots from the same receiver add observations without adding another station entry.

WSPRadar finds occasions when the **same receiving station, identified by callsign and reported locator, reports both transmitters in the same two-minute WSPR cycle**. Each matched comparison is a <strong class="defined-term">spot pair</strong>. Comparing at the same receiver and time avoids mixing reports from different receiving setups or different parts of the day.

A spot pair consists of one retained Target observation and one retained Reference observation matched on band, WSPR cycle, and the remote station’s callsign and full reported locator. Each pair supplies one ΔSNR observation.

When several reports exist for one setup, remote station, and cycle, WSPRadar consolidates them using its existing SNR-selection rules before forming the comparison.

A **Target-only** observation means a receiver reported SK0WE/P but not SK0WE/1 in that cycle; **Reference-only** means the reverse. These **one-sided** observations still show reception, but there is no measured SNR for the missing report to subtract.

The quantity we compare is signal-to-noise ratio, or <strong class="defined-term">SNR</strong>: how strongly a signal stands out relative to noise. Higher SNR is better. For this demo:

**ΔSNR = SK0WE/P SNR − SK0WE/1 SNR**

Positive values favor the short Difona vertical; negative values favor the larger Hy-Gain vertical. Zero means equal SNR in that comparison.

**Our question is: how much difference did the receivers observe, and was that difference the same on every path?** The decoding views add a second question: which transmissions were reported from just one setup?

<!-- section: load-demo -->

## Load the demo and check its settings

Select **Run in WSPRadar App** above to open the prepared **Short Portable Vertical vs Larger Vertical** demo. Review the settings, then select **Run Analysis**.

You do not need to enter the experiment manually. Check the settings to understand what the analysis includes:

{{demo_settings_table}}

The overview includes receivers within **10 000 km**. For this very short run with very little data, each receiver needs only **one spot pair across the comparison period** to qualify for ΔSNR, allowing paths with little paired evidence to contribute. **Avoid this one-pair minimum when you have enough data to require 3, 5 or even 10 spot pairs per station**, so each station’s median rests on repeated comparisons. A colored ΔSNR map segment still needs **at least two qualifying receivers**, rather than the default of five: a compromise that retains directional coverage without letting one receiver alone determine a segment. Both receivers could still contribute just one pair each; a colored segment is a starting point for inspection, not a well-established regional result.

These minimums apply to **ΔSNR**. The decoding views retain one-sided reports and receivers without spot pairs; the ΔDecode map has its own event-count requirement, explained below.

Follow **Global View → Segment Inspector → Station Insights → Drill-Down**, then **Download Evidence**. Start with **Full Range | All Directions** selected.

Global View shows the overall pattern; the Inspector examines a direction and distance range; Station Insights follows one receiver; Drill-Down checks individual observations. Keep **10m** for the Inspector’s chronological charts. The selected-station figures use their separate **1h** setting.

<!-- section: delta-snr-map -->

## Read the ΔSNR Map: is the difference the same everywhere?

Open **Global View → ΔSNR Map**.

The Azimuthal Map is centered on the Target, SK0WE/P. Compass sectors represent directions from the transmitting station; rings separate distance ranges. Each direction-and-distance region is a **map segment**. **The station markers are remote receivers.**

Each qualifying receiver supplies its own median SNR difference. WSPRadar then takes the median across those receiver medians. A receiver that reports more frequently therefore does not dominate the sector simply by supplying more observations. A median is the middle value when sorted, or the average of the two middle values when the count is even. **Each qualifying receiver has one equal voice:** the map describes the typical sampled receiving path, rather than giving the busiest receiver the greatest influence.

Read the numerical color scale. Negative values favor the larger Reference vertical. Here, every colored sector is negative—but the size of the difference varies.

Use the **Segment Inspector** to compare these examples:

| Geographic scope | Station-balanced median ΔSNR | Qualifying receivers | Qualifying spot pairs |
| :--- | ---: | ---: | ---: |
| **0–2 500 km, SSW** | **−10.0 dB** | **7** | **41** |
| **0–2 500 km, WSW** | **−4.0 dB** | **14** | **74** |
| **5 000–10 000 km, WNW** | **−4.0 dB** | **3** | **10** |

The short vertical’s disadvantage is larger on the sampled south-southwestern European paths than toward west-southwestern Europe or North America. The North American comparison is also supported by fewer receivers and observations.

**Reaching a distant receiver is not the same as matching the other antenna’s SNR.** The short vertical reached North America, but the matched reports still favor the larger vertical overall on those paths.

Gray-hatched segments contain observed evidence but too few qualifying receivers for a ΔSNR map value. Blank segments have no observed station entries. Neither demonstrates that either antenna radiates nothing in those directions. Green receiver markers show qualifying paired observations. With the one-pair minimum, every receiver with a spot pair qualifies in this run. **Marker colors describe the reception category; sector colors describe the SNR difference.** Purple **Only SK0WE/P** and blue **Only SK0WE/1** markers identify receivers that reported just that transmitter during the run.

Return the Segment Inspector to **Full Range | All Directions** before continuing.

<!-- section: decoding-reach -->

## Open Decodes & Stations by SNR: what else was heard?

Move to **Global View → Decodes & Stations by SNR**. Follow the curves **from stronger signals on the left toward weaker signals on the right**. These are **cumulative curves**: each point includes reports at the displayed SNR cutoff or stronger, so moving right adds weaker reports. The upper row counts spots; the lower row counts distinct receiving-station entries. Purple is the short vertical; blue is the larger vertical.

These curves use the **raw SNR reported by the remote receivers for each transmitter**, without transmit-power normalization or a Reference SNR correction.

The upper-left **Paired spots** curves represent **166 spot pairs**, with **166 retained observations from each setup** at their endpoints. Before that endpoint, the larger vertical’s curve rises earlier: its matched reports tend to have higher SNR. That separation describes signal quality on shared observations; neither side has extra decodes within the Paired spots panel.

The upper-middle panel adds **36 short-vertical-only reports** and **362 larger-vertical-only reports**. A receiver can supply spot pairs in some cycles and one-sided reports in others. Those one-sided reports cannot provide a paired SNR difference.

The lower-middle **Stations without paired observations** panel asks a different question: which receivers never supplied a matched comparison? In this run, they reported only one of the transmitters. **Both observed, no pairs: +0 stations** means there are no receivers that reported both transmitters only in different cycles.

Read the right-hand endpoints:

| Observed result | Short vertical · SK0WE/P | Larger vertical · SK0WE/1 |
| :--- | ---: | ---: |
| **Total decodes** | **202** | **528** |
| **Distinct receiving-station entries** | **38** | **90** |

The larger vertical has **2.61× as many observed decodes** across the selected window. This is a report-count ratio, not an absolute transmission-success rate. Reports of the two setups cover different spans within that window; we will check this in the time charts before interpreting the size of the advantage.

The lower panels count receivers rather than reports. **The larger vertical also reached substantially more receivers**, including many that supplied no spot pairs. Its advantage therefore extends to additional receiving paths, beyond accumulating more reports on shared paths. A station entry means a callsign together with its reported locator. These curves include all retained reports, including receivers with no spot pairs.

**Either** counts each observed receiver-cycle or station entry once, even when both transmitters were reported. A Paired event therefore counts once in Either but contributes one decode to each setup’s total. Each lower curve admits a receiver at its strongest relevant report: its strongest paired report in the Paired spots panel, or its strongest report of any outcome in All stations. The station panels need not add at every intermediate SNR cutoff.

**Extra signal margin can help a weak path produce a decode rather than no report.** The larger vertical’s one-sided reports are typically weaker than its reports in paired comparisons, consistent with this benefit toward the weak-signal end. Missing reports alone cannot confirm the cause: interference, transmission schedules or gaps in reception and reporting can also contribute.

**Read the panels together: stronger paired signals, additional one-sided reports and wider receiver reach describe complementary benefits.** The differing reporting spans still limit how much of the count advantage can be attributed to signal strength.

<!-- section: delta-decode-map -->

## Read the ΔDecode Map: where were more reports recorded?

Open **Global View → ΔDecode Map**. This map includes receivers with no spot pairs, so it can show an observed decoding imbalance where the ΔSNR map has insufficient paired evidence.

For each segment, WSPRadar pools the reports: the short vertical’s total is **Paired + Target-only**; the larger vertical’s total is **Paired + Reference-only**. It compares these pooled totals, rather than averaging the receivers’ individual ratios. Read the fold scale and which setup it favors: warm colors favor Target; blue colors favor Reference. **2× means twice as many observed decodes**, not twice the signal strength or twice as many receivers.

**The two maps tell a consistent geographic story:** the larger vertical combines stronger paired signals with more observed reports. Within **0–2 500 km**, its decode advantage is greater toward **SSW Europe (3.14×)** than **WSW Europe (1.86×)**, matching the stronger SNR contrast toward SSW. Read the maps together, but remember: **there is no fixed conversion from dB to extra decodes**. These full-window ratios also include the different reporting spans.

The map requires **at least six observed receiver-cycle events per segment**: 1% of the run’s **564 events**, rounded up. Paired counts once for this requirement. This is independent of the one-pair/two-receiver ΔSNR minimums.

The central light band extends to the **1.25× boundaries** on each side; it does not mean an exact tie. **Exclusive** means only one setup has reports in that segment. Read that as observed coverage, with its count and time context. Gray hatching means insufficient events for this map’s requirement.

<!-- section: difference -->

## Read Benchmark Statistics: how large is the difference?

Open **Segment Inspector → Benchmark Statistics**, with **Full Range | All Directions** selected.

These **histograms** group similar results into bars. Bar height shows the share of the evidence in each range. The left panel counts decode volume, the middle panel counts qualifying spot pairs, and the right panel counts qualifying receiver medians.

### Which signals supplied a comparison?

With the one-spot-pair minimum, **all 166 spot pairs from 37 receivers qualify**. These are the observations and receivers shown in the two ΔSNR histograms. **Thirteen of these receivers contributed only one or two pairs each**, so check the counts behind their medians.

The left-hand **ΔDecode — Decode Volume** panel includes all **730 decodes**. Its bars show the share of decodes contributed by receivers with similar decode ratios; its dashed line marks the pooled **Reference 2.61×** result. It uses the full reporting window discussed above.

Most decode volume lies on the Reference side. The prominent **Reference Exclusive** bar comes from receivers that never reported the short vertical during this window. It does not contain every Reference-only report: receivers with paired observations can also supply one-sided reports in other cycles.

### What does the difference between the medians tell us?

The two SNR summaries agree on which antenna led, but describe a different typical advantage. Here, the middle receiver result favors the larger vertical by **5 dB**, while the middle qualifying individual comparison favors it by **7 dB**. These are two views of the same experiment—not an uncertainty range within which the “true” advantage must lie.

To investigate the difference, open **Station Insights** and compare **Spot pairs** with **Median ΔSNR**. For example, **ON5KQ contributes 11 spot pairs with a median of −7 dB**, whereas **N2HQI contributes three, with a median of −4 dB**. Both contribute one value to the receiver-median histogram, but eleven ΔSNR observations versus three to the spot-pair panel.

A more negative spot-pair median can occur when repeatedly observed paths show a larger disadvantage. However, the spread of observations within each receiver also matters: the gap alone does not prove that the busiest receivers caused it.

**Collecting more data is the practical next step.** With only one or two spot pairs, a receiver’s median can depend strongly on individual WSPR cycles. For your own test, run both setups together over several days and different times of day, keeping their installations and power unchanged. This gives more opportunity to sample the paths repeatedly and to raise the per-station minimum to **3, 5 or even 10 spot pairs**.

**If sparse sampling is driving the gap, the medians may move closer as the evidence builds.** They can still remain different: the station summary gives each receiver one equal voice, while the spot-pair summary gives frequently reported paths more influence. Check whether the results remain consistent across days and receivers as the data grow.

### Which result should I use?

Use **ΔSNR — Qualifying Stations** for the question, “How did the antennas compare across the receiving stations, giving each station equal weight?” Use **ΔSNR — Qualifying spot pairs** for “What was the typical difference across all matched observations from qualifying receivers?”

Neither is automatically more accurate. Station balancing prevents frequently reporting receivers from dominating, but a receiver with only one comparison still contributes one station median. Check the counts alongside the result.

For your own comparisons, use this reading guide:

| When the medians… | How to interpret them |
| :--- | :--- |
| **Are close and favor the same setup** | The station-level and observation-level summaries tell a similar story. Still check coverage and variation between paths. |
| **Differ but favor the same setup** | Both summaries identify the same leader, but the typical advantage depends on how the evidence is summarized. Inspect report counts, directions and time periods. |
| **Favor different setups** | The overall conclusion depends on the summary chosen. Investigate which paths and periods favor each setup before declaring an overall winner. |

For this demo, the conclusion is not reversed by the choice of summary: both medians favor the larger vertical, and **all 37 qualifying receiver medians are negative**. Lead with the **5 dB station-balanced advantage**, while retaining the **7 dB observation-level advantage** as complementary information. **Read the histogram shapes too:** they show a consistent leader across receiver medians, with variation from one comparison to the next. A few individual spot pairs tie or favor the short vertical even though every receiver’s median favors the larger one.

<!-- section: published-figure4 -->

## Optional: verifying WSPRadar against published research

How do we verify WSPRadar’s results? One approach is to revisit published WSPR experiments, reconstruct their figures from historical observations, and compare the findings. This helps us validate our calculations, investigate discrepancies, and make the same analysis capabilities available to amateur-radio operators.

The main finding agrees with Zander’s [published experiment](https://arxiv.org/abs/2209.08989): **the larger Hy-Gain vertical supplied stronger paired signals than the short Difona vertical**. WSPRadar adds a practical view of **where the difference changes, how much evidence supports it, and what one-sided reports contribute**. The time charts also help check whether report-count comparisons cover comparable periods.

The numerical agreement and reconstruction of Figure 4 are covered in the dedicated comparison PDF:

[**Explore the original Figure 4, reconstruction and WSPRadar comparison (PDF) ↗**](/assets/demos/zander_fig4_paper_v1/WSPRadar_Demo_Zander_Figure4.pdf)

<!-- section: time -->

## Read ΔSNR Temporal Coverage: did the advantage persist?

Open **Segment Inspector → ΔSNR Temporal Coverage** with **Full Range | All Directions** and **10m** selected.

### Left panel: follow the observations through time

Each circular marker shows the median difference for a **10-minute interval**, using spot pairs from qualifying receivers. The Reference vertical leads throughout these interval summaries, rather than only at one point in the test.

| UTC interval | Qualifying spot pairs | Median ΔSNR |
| :--- | ---: | ---: |
| **09:45–09:55** | **8** | **−8 dB** |
| **09:55–10:05** | **70** | **−6 dB** |
| **10:05–10:15** | **76** | **−8 dB** |
| **10:15–10:25** | **12** | **−4 dB** |

**The advantage persists, but apparent changes need supporting observations.** Most paired observations occur in the middle of the run. The less-negative final point comes entirely from the **10:16 UTC cycle**, so it does not establish a sustained improvement. Change **Time aggregation to 2m** to inspect the cycles behind the interval summaries. Return to **10m** before continuing to ΔDecode Temporal Coverage.

The dashed line is the overall **−7 dB qualifying spot-pair median**. The shaded band contains the middle 50% of each interval’s observations; it shows spread, not a confidence interval. Background colors indicate where observations concentrate, not which antenna is better. Read the labeled dB values—the vertical scale is nonlinear.

### Right panel: why is there no UTC-hour profile?

The panel states **“UTC-hour pattern unavailable.”** This run contains observations from only one date; WSPRadar requires evidence from at least two UTC dates for that view.

That is appropriate for this example: a short test on one morning cannot establish a recurring daily pattern. Continue with the chronological evidence.

<!-- section: evidence -->

## Check ΔDecode Temporal Coverage: do the reporting spans match?

Open **Segment Inspector → ΔDecode Temporal Coverage**. The SNR chart shows the paired differences. This view shows **which receivers reported each setup and how many observed decodes each accumulated over time**.

The **upper row counts receiving stations**; green **Both observed** means a receiver reported both transmitters somewhere within that interval, not necessarily in the same cycle. The **lower row counts receiver-cycles**; here, green means a spot pair. Purple is Target-only and blue is Reference-only. The overlaid lines use the right-hand ratio axes: **1× means equal totals; above favors Target and below favors Reference**. The upper line compares receiver reach; the lower line compares total decodes. These lines are comparisons of observed counts, not transmission-success percentages.

**The striking late decode advantage coincides with different reporting spans.** In the final **10:15–10:25** interval, the count ratio reaches **Reference 11.5×**, while the paired SNR median is **−4 dB**.

**No SK0WE/P reports appear in this run after 10:16 UTC**, while SK0WE/1 continues to be reported until **10:24**. At the start, the first two observed cycles contain only Target reports. The export does not establish why those reporting spans differ.

This explains why the final decode ratio cannot be read as a sudden antenna-performance change. It also limits what the full-window **2.61×** ratio tells us. For your own test, confirm the transmitters’ common operating period from your experiment notes, set the analysis window accordingly, and rerun before comparing decode totals as antenna performance.

**Check the count and the operating period behind a feature—not just its height or ratio.**

<!-- section: stations -->

## Open Station Insights: what did one receiver observe?

The **Station Insights** table lets you move from the overall comparison to a particular receiving station.

The station list covers the full analysis by default. **Filter by selected segment and distance** narrows the list; selected-station evidence still covers that receiver’s full run. **Include one-sided evidence** also lists receivers without spot pairs.

Select **ON5KQ at JO10os**, the receiver used in the figures below. It is about **1 267 km** from the Target, at an azimuth of **241°**. Open its **ΔSNR Temporal Coverage**.

ON5KQ supplied repeated spot pairs and also reported each transmitter alone in other cycles. This lets us examine signal margin, one-sided reception and time grouping on the same receiving path.

Its **11 spot pairs** give a median ΔSNR of **−7 dB**. All eleven comparisons favor the larger vertical, with differences ranging from **−12 to −6 dB**.

### Why does the chart show only one median marker?

Keep **1h** selected for these station charts; this control is separate from the Inspector’s **10m** setting. The selected-station view uses **one-hour bins**, longer than this entire test window. The single marker therefore summarizes all eleven spot pairs. It does not mean the SNR difference stayed constant throughout the test.

This is a useful distinction: the number of markers depends on the time grouping, while the observation count tells you how much data each marker summarizes.

<!-- section: station-decodes -->

## What does its ΔDecode view add?

Open the selected station’s **ΔDecode Temporal Coverage**.

The larger vertical’s **7 dB paired-SNR advantage** coexists with **13 short-vertical decodes versus 15 larger-vertical decodes**. **A weaker signal can still be decoded successfully**: extra margin does not necessarily produce extra reports on every path.

The two Target-only observations do not contradict the negative paired SNR differences. They occurred when only the short antenna’s signal was reported, so no paired difference can be calculated for those cycles. The four Reference-only observations are at **10:18–10:24**, the same reporting tail we just inspected. Even a single-receiver ratio needs that time context.

<!-- section: drill-down -->

## Use Drill-Down: check an individual comparison

**Drill-Down** exposes the observations behind the summaries. With ON5KQ selected, inspect the time and the two SNR columns.

The examples below are Paired rows in the selected-station export, `benchmark/table_drilldown_selected_stations.csv`:

| UTC time on 21 May | SK0WE/P SNR | SK0WE/1 SNR | ΔSNR |
| :--- | ---: | ---: | ---: |
| **09:54** | −13 dB | −1 dB | **−12 dB** |
| **09:56** | −13 dB | −6 dB | **−7 dB** |
| **10:02** | −11 dB | −5 dB | **−6 dB** |
| **10:10** | −14 dB | −4 dB | **−10 dB** |
| **10:12** | −5 dB | +1 dB | **−6 dB** |

At 09:54, **−13 − (−1) = −12 dB**. The larger vertical’s signal had the higher SNR at ON5KQ, but **both signals were decoded**. A negative ΔSNR is a relative disadvantage, not a failed reception.

The differences change from one cycle to the next, even though the selected-station chart summarizes them with one median marker.

These exported SNR values are normalized to **30 dBm (1 W)**; the earlier cumulative curves use raw reported SNR. The same adjustment on both sides leaves ΔSNR unchanged. The ΔSNR column subtracts the Reference value from the Target value; no additional Reference correction is applied in this run.

You do not need to inspect every row. Use Drill-Down to verify the arithmetic, understand an unusual observation or check what contributed to a summary.

<!-- section: takeaways -->

## State the result—and preserve it

> **In this 20 m experiment, the larger Hy-Gain AV620 outperformed the short Difona vertical across the matched receiving paths. The 166 qualifying same-cycle comparisons from 37 receiving-station entries give a station-balanced median ΔSNR of −5.0 dB and a spot-pair median of −7 dB. Every qualifying receiver has a negative median, but the size of the difference varies with direction and from one comparison to the next.**

The short vertical still reached distant receivers, including North America. **Being heard and matching a larger antenna’s SNR are different questions—and WSPRadar lets you examine both.** The decoding views add observed report counts and show why checking common operation matters before attributing those counts to antenna performance.

For a portable operator, this is the useful trade-off: the compact antenna can still reach distant stations, while the larger installation provides more signal margin on the sampled paths. Use the maps to examine the directions that matter to your operating, then check whether the margin is accompanied by more reports under comparable operation.

This result describes these installed transmitting setups during the selected test. It is not a fixed penalty for every portable vertical or a measurement of antenna gain in every direction.

Under **Download Evidence**, select **Prepare All Results for Download**, then **Download Prepared Results**, to save the results package and preserve the settings, figures and processed observations. **Save Config** separately preserves the reusable analysis settings. For your own experiments, record the antennas, transmitter power and installation details alongside the results, including when both transmitters were operating.

You have now used remote WSPR receivers to compare two transmitting antennas—from the map and overall difference, through time and one receiving station, down to an individual pair of reports.

<!-- Source: WSPRadar_export_2026_10_23__07_05.zip; exported 2026-10-23T05:05:33Z. Refined from the latest existing Zander guide using the supplied guided-demo prompt and walkthrough.demo1.reference(1).md. Current figures and tables are in benchmark/; reproduction settings are in config/wspradar_config.config and config/run_metadata.json. The export profile description retains legacy navigation and histogram positions; this guide follows the current figure titles and panel order. -->
