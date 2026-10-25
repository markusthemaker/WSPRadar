<!-- section: hero -->

# A 90° Antenna Rotation, a 3 dB Difference

**See how antenna orientation changes reception.**

Keep one antenna fixed, rotate the other, and follow the difference. This 160 m experiment shows how to find a change in WSPRadar, check it on one radio path, and see what the decoded signals add to the story.

Throughout this guided demo, <strong class="defined-term">ΔSNR</strong><strong> compares signal quality when both setups decoded the same transmission</strong>, while <strong class="defined-term">ΔDecode</strong><strong> compares how many transmissions each setup reported, including one-sided reception</strong>. A better SNR margin and more decodes are related benefits, but one does not automatically imply the other.

<!-- section: summary -->

## The findings at a glance

- [**Change on one path**](#stations)

    <strong class="case-finding-value">3.0 <span>dB</span></strong>

    M7AEO's reconstructed median changes from **−0.6 to +2.4 dB**, favoring the fixed long wire relative to the rotated dipole.

- [**Across station results**](#difference)

    <strong class="case-finding-value">+1.4 <span>dB</span></strong>

    The full-period station-balanced median, based on **5 367 qualifying spot pairs from 50 transmitting-station entries**.

- [**More decoded signals**](#decoding-reach)

    <strong class="case-finding-value">1.29<span>×</span></strong>

    **7 054 versus 5 489** across the full period: **1 565 additional decodes** at the long-wire setup.

The whole-period results combine both antenna orientations. Follow the time charts to see the change associated with rotation.

<!-- section: setup -->

## What were the operators testing?

Can turning a receiving antenna through 90° make a visible difference in WSPR results?

Jurgen Vanhamel, Walter Machiels and Hervé Lamy compared two receiving setups on 160 meters:

- <strong>ON4AWM0 — </strong><strong class="defined-term">Target</strong><strong>:</strong> an ITA LWA II long-wire antenna, kept in the same orientation throughout the experiment.
- <strong>ON4AWM1 — </strong><strong class="defined-term">Reference</strong><strong>:</strong> an adapted shorted dipole, initially parallel to the long wire and then rotated 90° in the horizontal plane after the first week.

In this <strong class="defined-term">RX Benchmark</strong>, Target and Reference are the **two receiving setups**. The stations plotted on the maps are the remote WSPR transmitters they heard. A <strong class="defined-term">station entry</strong> identifies a transmitter by its callsign and reported locator. A reception report is a <strong class="defined-term">spot</strong>; repeated spots can strengthen the evidence without adding another station entry.

WSPRadar matches reports of the **same transmitter and reported locator in the same two-minute WSPR cycle**. These <strong class="defined-term">spot pairs</strong> let us compare the two setups at the same time. A <strong class="defined-term">Target-only</strong> observation means only ON4AWM0 reported that transmitter-cycle; <strong class="defined-term">Reference-only</strong> means only ON4AWM1 did.

A spot pair consists of one retained Target observation and one retained Reference observation matched on band, WSPR cycle, and the remote station’s callsign and full reported locator. Each pair supplies one ΔSNR observation.

When several reports exist for one setup, remote station, and cycle, WSPRadar consolidates them using its existing SNR-selection rules before forming the comparison.

<strong class="defined-term">Signal-to-noise ratio, or SNR,</strong> describes how strongly a signal stands out relative to noise. Higher SNR is better. Here:

**ΔSNR = ON4AWM0 SNR − (ON4AWM1 SNR + 1.6 dB)**

**Positive values favor the long-wire setup; negative values favor the dipole setup.** The dipole is the antenna that changes; the long wire stays fixed.

The prepared correction accounts for an established receiving-chain offset: the receiver chains themselves can introduce a difference in reported SNR. Applying it helps avoid mistaking that offset for an antenna advantage. The companion [**One Antenna, Two Receivers — Why Calibration Matters**](/en/demos/vanhamel_rx_calibration/) explains that check. A constant correction shifts the SNR differences without changing the size of a before-and-after step.

**Our question is: where, when and by how much did relative reception change—and did one setup also decode more transmissions?**

<!-- section: load-demo -->

## Load the demo and check its settings

Select **Run in WSPRadar App** to load the prepared settings; you do not need to enter the station details manually. Review the settings, then select **Run Analysis**.

| Setting | Value in this demo |
| :--- | :--- |
| Analysis | **RX Benchmark → Reference Setup/Station** |
| Target / Reference | **ON4AWM0, JO20OT / ON4AWM1, JO20** |
| Band | **160 m** |
| UTC window | **1 May 2021, 17:15 → 15 May 2021, 07:00** |
| Reference SNR Correction | **+1.6 dB — established offset** |
| Distance / solar state | **Within 5 000 km / All** |
| ΔSNR support | **≥3 spot pairs per station; ≥3 qualifying stations per map segment** |
| ΔDecode map support | **1% of the run's observed events per segment** |
| Chronological charts / station to select | **12h / M7AEO at IO82** |

After the run, follow **Global View → Segment Inspector → Station Insights → Drill-Down**, then **Download Evidence**. Global View shows the whole-run pattern; the Inspector lets you examine a direction and distance; Station Insights follows one transmitter; Drill-Down reveals individual comparisons.

Start with **Full Range | All Directions** in the Inspector. Both the Inspector and selected-station chronological charts use **12h** here; their aggregation settings are separate.

Each station needs **at least three spot pairs over the comparison period** to qualify for ΔSNR, and each colored map segment needs **at least three qualifying stations**. This reduces reliance on just one or two observations within a station, or just one or two station results within a segment. The segment minimum is **three rather than the default of five** to retain more directional coverage in this sparser 160 m dataset. The ΔDecode map uses a separate count requirement, explained below; its pooled decode counts are unaffected by these ΔSNR minimums. Neither display threshold is a test of statistical significance.

<!-- section: delta-snr-map -->

## Read the ΔSNR Map: does every direction agree?

Open **Global View → ΔSNR Map**. The map is centered on ON4AWM0. Compass sectors show direction from the Target; rings separate distance ranges. Each direction-and-distance region is a <strong class="defined-term">map segment</strong>.

For each transmitter, WSPRadar calculates its <strong class="defined-term">median ΔSNR</strong>: the middle difference when its spot pairs are sorted. It then takes the median across those station results within each segment. **Every qualifying station has one equal voice**, whether it contributed three pairs or hundreds. Frequently heard transmitters cannot dominate the map simply by supplying more reports.

The long wire leads on the sampled ENE and WNW paths; the dipole leads in SSE. **An overall advantage does not describe every direction.**

Select a direction and distance in **Segment Inspector** to examine its stations and counts. Gray hatching means observed evidence below the map's support requirement; blank segments have no observed station entries. The neutral color spans a range around zero. Read the numerical scale rather than treating every pale sector as an exact tie.

| Geographic scope | Station-balanced ΔSNR | Qualifying stations |
| :--- | ---: | ---: |
| **0–2 500 km, ENE** | **+1.4 dB** | **3** |
| **0–2 500 km, WNW** | **+2.4 dB** | **14** |
| **0–2 500 km, SSE** | **−3.6 dB** | **3** |

**Station markers show the type of reception, not which antenna had better SNR.** Green <strong class="defined-term">Paired (qualifying)</strong> markers identify transmitters meeting the three-pair minimum. Pale-green markers have paired observations but fewer than three pairs; they do not contribute to the ΔSNR summaries, though their decodes remain in ΔDecode. Magenta **Only ON4AWM0** and cyan **Only ON4AWM1** identify stations reported exclusively by that receiver.

This map combines both weeks. It shows the overall directional comparison, not the change caused by rotation. Its colored ΔSNR results require both receivers to decode the same transmission; the next view also includes one-sided reception. Return to **Full Range | All Directions** before continuing.

<!-- section: decoding-reach -->

## Open Decodes & Stations by SNR: what else was received?

Move to **Global View → Decodes & Stations by SNR**. Follow the curves **from stronger signals on the left toward weaker signals on the right**. These are <strong class="defined-term">cumulative curves</strong>: each point includes reports at the displayed SNR cutoff or stronger, so moving right progressively adds weaker reports. The upper row counts spots; the lower row counts distinct station entries. Each receiver's curves use its own **raw reported SNR**.

The **Paired spots** curves represent **5 379 spot pairs from 60 stations**, with **5 379 retained observations from each receiver** at their endpoints. Their separation before the endpoint reflects different reported SNRs for the shared transmissions; it does not represent extra decodes. These curves include all retained spot pairs, including those from stations below the three-pair ΔSNR minimum.

The upper-middle panel adds one-sided observations, which cannot supply paired ΔSNR. **The long wire records far more of these, mainly toward the weak-signal end.** This is consistent with extra reception margin helping weak signals produce a report. The same transmitter can contribute spot pairs in one cycle and a one-sided report in another.

The lower-middle **Stations without paired observations** panel shows transmitters reported exclusively by one receiver in this run. Its <strong class="defined-term">Both observed, no pairs: +0 stations</strong> annotation means there are none heard by both receivers only in different cycles.

Read the right-hand endpoints as the observed totals:

| Observed result | Long wire · ON4AWM0 | Dipole · ON4AWM1 |
| :--- | ---: | ---: |
| Observations in spot pairs | 5 379 | 5 379 |
| One-sided spots | 1 675 | 110 |
| **Total decodes** | **7 054** | **5 489** |
| **Distinct station entries** | **73** | **62** |

The long wire recorded **1.29× as many decodes**. It also heard **13 station entries that the dipole never reported**; the dipole heard **two that the long wire missed entirely**. More decodes and more stations are different benefits: repeated reception of a familiar transmitter increases the spot count without adding another station.

<strong class="defined-term">Either</strong> counts the combined observed set once, even if both receivers reported it. A Paired transmitter-cycle is therefore one observed event but contributes one decode to each receiver. In the lower row, a station enters each curve at its strongest relevant report. Use the time charts below to see how consistently it was received.

The **+1.6 dB correction does not move these curves or change any decode counts**. A one-sided report supplies no measured SNR for the receiver that missed it.

<!-- section: delta-decode-map -->

## Read the ΔDecode Map: where were more signals decoded?

Open **Global View → ΔDecode Map**. Each receiver's total is **Paired + its own one-sided decodes**. WSPRadar pools those counts across the selected segment; it does not average station ratios.

In **WNW at 0–2 500 km**, the totals are **2 143 for ON4AWM0 and 1 866 for ON4AWM1**:

**2 143 ÷ 1 866 = 1.15× as many long-wire decodes**, a net **277 additional decodes**.

<style>
#delta-decode-map .case-copy > .table-scroll {
  clear: none;
  width: fit-content;
  max-width: 100%;
}

#delta-decode-map .case-copy > .table-scroll table {
  width: auto;
}
</style>

Compare the same three directions with the SNR map:

| Scope, 0–2 500 km | Paired ΔSNR | Decode advantage |
| :--- | ---: | :--- |
| **ENE** | **+1.4 dB** | **Long wire 1.03×** |
| **WNW** | **+2.4 dB** | **Long wire 1.15×** |
| **SSE** | **−3.6 dB** | **Dipole 1.75×** |

**ENE has a positive paired-SNR margin but nearly equal decode totals.** WNW has both a larger paired-SNR margin and a larger decoding advantage. In SSE, both measures favor the dipole. Better SNR can provide additional margin even when both setups already decode most of the observed transmissions. The two measures also weight the evidence differently: qualifying station medians for ΔSNR, all retained decode counts for ΔDecode.

On the legend, **2× means twice as many decodes for the indicated setup**. Warm colors favor Target; blue colors favor Reference. Here, the central light-green band extends to the **1.1× boundaries in either direction**, so it is not necessarily a tie. The scale adapts to the results.

A segment needs **72 observed events** to receive a color: 1% of the run's **7 164 transmitter-cycle events**, rounded up, with each Paired event counted once. Hatching means insufficient volume for the map, not equal reception; the evidence remains available to inspect.

**Interpret decoding differences under comparable operation and reporting.** An outage or missing upload can also remove a report. Transmissions missed by both receivers remain unknown, so ΔDecode does not measure absolute decoding probability.

<!-- section: difference -->

## Read Benchmark Statistics: how large is the overall difference?

Open **Segment Inspector → Benchmark Statistics** with **Full Range | All Directions** selected.

These <strong class="defined-term">histograms</strong> group similar results into bars. Read the horizontal axis for the size of the difference and the bar height for the share of evidence in that range. The three panels use different evidence:

- **ΔDecode — Decode Volume:** stations are arranged by their decode advantage. Bar height shows their share of receiver decodes, not their share of stations. The dashed line marks the pooled **ON4AWM0 1.29×** result. The <strong class="defined-term">Exclusive</strong> endpoints contain decodes from stations heard only by one setup, not every one-sided spot.
- <strong class="defined-term">ΔSNR — Qualifying spot pairs</strong><strong>:</strong> every paired observation from a qualifying station contributes: **5 367 pairs** in total. The median is **+2.4 dB**, so frequently heard transmitters have more influence.
- <strong class="defined-term">ΔSNR — Qualifying Stations</strong><strong>:</strong> each of the **50 qualifying stations** contributes one median. The station-balanced result is **+1.4 dB**.

The large bar around **1×** in the decode panel shows that much of the reception came from paths with similar totals. The bars toward Target show where extra reports accumulated, shifting the pooled result toward the long wire.

**50 of the 60 stations with paired observations meet the three-pair minimum.** The other ten contribute just 12 pairs between them. Their reports remain in the decoding views but are excluded from the qualifying ΔSNR distributions. This explains the small difference between the spot-pair totals in the cumulative curves and the ΔSNR histogram.

**The spot-pair median describes a typical paired observation; the station-balanced median describes a typical transmitter path.** Both favor the long wire under these different ways of weighting the evidence. The map uses station balancing; the temporal SNR charts pool paired observations. **The two medians are not an uncertainty range**, and equal station weight does not mean equally strong supporting evidence. In Station Insights, compare **Spot pairs** with **Median ΔSNR** to see how much data supports each station result. The gap between the two medians alone does not identify which paths or periods produced it.

Both distributions also extend below zero: some comparisons favor the dipole. Most importantly, **neither full-period median measures the rotation effect**. For that, follow the comparison through time.

<!-- section: time -->

## Read ΔSNR Temporal Coverage: when did reception change?

Open **Segment Inspector → ΔSNR Temporal Coverage**. Keep **Full Range | All Directions** and **12h** selected for this comparison.

### Follow the experiment on the left

Each circular marker is the median of the spot pairs from qualifying stations in one **12-hour interval**. Look for the upward change around **8 May**. Several well-populated early intervals lie near **−0.6 dB**; later intervals often lie around **+2.4 to +4.4 dB**. Relative reception has shifted toward the fixed long-wire setup.

The dashed line is the overall **+2.4 dB spot-pair median**. The shaded band contains the **middle 50% of observations**, showing spread rather than a confidence interval. Background colors show where observations concentrate; they do not indicate which antenna is better. Read the labeled dB values because the vertical scale is nonlinear.

This view pools individual observations, so frequently heard transmitters carry more weight. Next we will check whether the change also appears on one path.

### Compare hours of the day on the right

The UTC-hour panel combines the same hour across dates. Most paired reception occurs in the evening, night and early morning; daytime coverage is sparse. This is consistent with the strong day–night changes in 160 m ionospheric propagation.

The hourly profile combines **both antenna orientations**. Use it to explore the daily pattern; use the chronological panel to follow the rotation experiment.

<!-- section: evidence -->

## Read ΔDecode Temporal Coverage: check the counts behind the pattern

Open **Segment Inspector → ΔDecode Temporal Coverage**. This view shows both the supporting reception and the advantage in the number of stations or transmissions decoded.

The **upper row counts distinct stations within each time bin**. Green <strong class="defined-term">Both observed</strong> means each receiver heard that station at least once in the bin; those receptions need not be in the same cycle. Magenta and cyan show stations heard only by Target or Reference in that interval.

The **lower row counts transmitter-cycle events**. Here green means **Paired**, requiring the same WSPR cycle. Magenta is Target-only; cyan is Reference-only. Extra decodes of an already-heard transmitter can enlarge the lower bars without increasing the upper station count.

Read the overlaid lines against the **right-hand axes**: **1× means equal totals; above favors Target; below favors Reference**. The upper line compares distinct-station totals; the lower line compares total decodes. The right-hand panels show average counts by UTC hour, with the advantage calculated from the combined counts.

The repeated overnight coverage supports the broad SNR pattern. Daytime ratios can look dramatic while the bars contain very few observations. For example, the all-station SNR point at **13:00 UTC is +7.4 dB—but rests on just one spot pair across the whole run**.

The three-spot-pair station minimum applies across the full comparison period, so an individual time bin can still contain only one pair.

**Check the count behind a striking value.** A large ratio on a tiny bar and a repeated advantage across hundreds of comparisons carry different amounts of evidence.

<!-- section: stations -->

## Open Station Insights: follow the rotation on one path

Open **Station Insights** and select **M7AEO at IO82**. It is about **598 km away at 291°** and supplies **1 441 spot pairs**. This gives us a well-observed path across both antenna orientations. Following the same transmitter lets us check whether the overall transition also appears without changing the transmitter being compared. It also connects the WSPRadar charts directly to the published experiment.

The station list covers the full analysis by default. **Filter by selected segment and distance** narrows the list; the selected station's evidence still covers its full run. **Include one-sided evidence** also lists stations without spot pairs.


### Follow M7AEO's ΔSNR

Open its **ΔSNR Temporal Coverage** chart. Use **12h** for the selected-station charts below; check this separately from the Inspector setting.

Most early 12-hour medians are below zero. After the change around **8 May**, they become positive; many later intervals settle around **+2.4 dB**. The change remains when we follow one transmitter, so a changing mix of transmitters cannot explain the entire pooled pattern.

Using the observation boundary from the published Figure 6 reconstruction:

| M7AEO observations | Median ΔSNR |
| :--- | ---: |
| **First 750 spot pairs** | **−0.6 dB** |
| **Remaining 691 spot pairs** | **+2.4 dB** |
| **Change** | **+3.0 dB** |

The full-period M7AEO median is only **+0.4 dB**. That single number hides the transition.

**Keep the sign in mind: the fixed long wire becomes stronger relative to the rotated dipole. This is not a 3 dB improvement for the antenna that was turned.**

<!-- section: published-figure6 -->

## Compare with the published experiment

The original **Figure 6**, the reconstruction and WSPRadar's M7AEO chart show the same upward transition. The publication plots successive receptions; WSPRadar groups observations by UTC time. Different horizontal axes reveal the same change in relative reception.

[**Explore Figure 6, the reconstruction and WSPRadar comparison ↗**](/assets/demos/vanhamel_fig6_rotation_v1/WSPRadar_Demo_Vanhamel_Figure6.pdf)

The split after **750 spot pairs** follows the publication's reconstruction boundary. It is **not an independently logged UTC rotation time**. WSPRadar adds the surrounding evidence: maps to compare directions, counts to distinguish extra signal margin from extra decoded transmissions, and Drill-Down to inspect the reports. These additions are not a claim that the paper published the same decoding analysis.

*Calibration note:* This demo uses **+1.6 dB**, rounded from **1.57 dB** documented on the [authors' website](https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-antenna-comparison-instrument). The paper reports **+1.2 dB**, as examined in the companion calibration demo. Using +1.2 dB here would move every paired difference **0.4 dB higher**, but leave the **3 dB step unchanged**. Agreement with the reconstructed figure does not establish which correction the authors used to draw it.

<!-- section: station-decodes -->

## Then check M7AEO's decodes

Open its **ΔDecode Temporal Coverage** chart. Across the run, this path supplies **1 550 long-wire decodes versus 1 448 dipole decodes**, or **1.07× as many at the long-wire setup**.

The large overnight bars contain mostly paired reception. Both setups often decoded the same transmissions, even while their relative SNR changed. A better SNR margin need not produce a proportional increase in decodes.

For a concrete contrast, the **00:00–01:00 UTC** bin, pooled across the run, has **+1.4 dB paired ΔSNR** but **138 decodes at each receiver: 1×**. Here the long wire supplied extra SNR margin without additional observed decodes.

Check sparse intervals too: the **9 May, 05:15–17:15 UTC** bin has a **+4.4 dB median from one spot pair**. The broad transition rests on the repeated observations, not on that isolated high point.

The **1.07×** total combines both orientations; it does not measure how much the rotation itself changed decoding.

<!-- section: drill-down -->

## Use Drill-Down: check an individual comparison

With **M7AEO** selected, open **Drill-Down** and compare the timestamp and SNR columns:

| UTC time, May 2021 | ON4AWM0 SNR | Corrected ON4AWM1 SNR | ΔSNR |
| :--- | ---: | ---: | ---: |
| **1 May, 18:24** | −20.0 dB | −19.4 dB | **−0.6 dB** |
| **7 May, 20:04** | −12.0 dB | −12.4 dB | **+0.4 dB** |
| **8 May, 20:16** | −16.0 dB | −20.4 dB | **+4.4 dB** |
| **14 May, 20:04** | −17.0 dB | −20.4 dB | **+3.4 dB** |

The first comparison favors the dipole. On 8 May, **−16.0 − (−20.4) = +4.4 dB**, favoring the long wire. These processed SNR values use a common **1 W (30 dBm) reported-power basis**. The Reference column also **already includes the +1.6 dB correction**; do not add it again. The earlier cumulative curves use raw reported SNR. The common power adjustment on both sides leaves ΔSNR unchanged.

Use **Zoom window** to focus the plots and table; **Filter table** changes only the displayed rows. You do not need to inspect thousands of rows: use this view to verify the arithmetic or investigate a surprising point. The before-and-after result comes from the full observation groups, not from choosing two individual rows.

<!-- section: takeaways -->

## Download Evidence: take the method to your own station

On the M7AEO path, **1 441 same-cycle comparisons reveal a 3 dB upward shift associated with rotating the Reference dipole**. Across both orientations and all sampled paths, the long-wire setup has a **+1.4 dB station-balanced SNR advantage** and **1.29× as many observed decodes**. The maps show where those advantages hold—and where the dipole leads.

These are results for the two installed receiving setups and the sampled paths. They do not establish a 3 dB antenna-gain change in every direction.

For your own antenna experiment, use the same sequence: **find the difference on the maps, follow it through time, check a well-observed transmitter, then inspect the underlying reports**. Keep notes on antenna orientation, the time of each change, receiver settings and common operating periods. If a sector or time interval remains sparsely sampled, collect more comparable nights before drawing a strong conclusion.

Under **Download Evidence**, select **Prepare All Results for Download**, then **Download Prepared Results**, to preserve the configuration, figures and processed observations. **Save Config** separately keeps the reusable analysis settings.

You have followed a physical antenna change down to individual WSPR reports—and learned to distinguish **a better SNR margin, additional decoded transmissions and additional stations heard**.

<!-- Source basis: WSPRadar_export_2026_10_22__21_37-vanhamel-fig-3.zip, exported 2026-10-22T19:37:39Z. The contents are the 90° rotation comparison associated with published Figure 6. Native light and dark figures are in benchmark/. Reproduction settings are in config/wspradar_config.config and config/run_metadata.json; numerical observations are in the three benchmark/table_*.csv files. Original experiment: Vanhamel, Machiels & Lamy (2022), DOI 10.1155/2022/4809313. -->
