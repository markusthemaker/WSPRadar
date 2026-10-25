<!-- section: hero -->

# A Month on 40 m with a Low Dipole

What did this receiver hear—and how consistently?

A distant WSPR spot is satisfying. A month of spots can tell you much more: which directions your station receives, which paths are dependable, and when reception changes. This guided demo follows **G3ZIL on 40 m during April 2017**, from a map of the transmitting stations to the individual observations behind one path.

**RX Performance examines one receiving station without a Reference receiver.** We will read three complementary measures: **reach**—which transmitters were heard at least once; **Decode Rate**—how often reception succeeded when an opportunity could be established; and **successful SNR**—the signal-to-noise ratio of the reports that were decoded. Together, they give a more useful station baseline than a list of distant contacts alone.

**For a deeper look at relative reception, explore [Low Dipole vs Radial-Free Vertical](/en/demos/griffiths_squibb_fig3/).** Its **RX Benchmark** analysis compares G3ZIL and G4HZX using paired SNR differences and decoding outcomes, showing where, when, and by how much the two receiving setups differ.

<!-- section: summary -->

## The findings at a glance

- [**Broad reception over the month**](#performance-evidence)

    <strong class="case-finding-value">996 <span>TX station identities heard</span></strong>

    Out of **2,107 qualifying identities** in the worldwide 22,000 km scope: **47.3% heard at least once**. Hearing a transmitter once does not mean hearing it regularly.

- [**Consistency is a different measure**](#performance-evidence)

    <strong class="case-finding-value">17.9<span>%</span></strong>

    **Station-balanced Decode Rate**, giving each qualifying transmitter equal weight. Pooling all confirmed opportunities instead gives **16.9%**.

- [**One path, different times of day**](#selected-station-evidence)

    <span class="case-finding-scope">HB0QRP · 844 km ESE</span><strong class="case-finding-comparison">71% morning · 16% noon</strong>

    Decode Rates for **07:00–08:00** and **11:00–12:00 UTC**, combining April's observations. We will check the successful SNR, supporting opportunities and individual days before interpreting that contrast.

<!-- section: setup -->

## The station and the question

Gwyn Griffiths, G3ZIL, and Nigel Squibb, G4HZX, described their practical investigations in *Improving HF Band SNR*, published in *Practical Wireless* in October 2017. G3ZIL used a homebuilt direct-conversion receiver in a garden shed and a low dipole with its center about 4 m high and its ends at 1.5 m. Their account also records retuning the dipole on **8 April**. These were working stations with real installation changes. [Original paper](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

Here we ask a question you could ask about your own station: **what reception did this complete receiving setup achieve, across which paths and at which times?** The paper supplies the station context; the Performance results below are a WSPRadar analysis of the historical reports.

**G3ZIL, at IO90HW, is the Target receiver.** The remote stations in this RX analysis are **transmitters**. A **station identity** means an exact callsign together with its full reported grid locator. The same callsign at different locators remains separate: combining them could mix different paths. Counts of identities therefore need not equal counts of individual operators or physical transmitters.

### What is a confirmed opportunity?

A WSPR **spot** is a report of a successful decode. The database does not contain a complete list of everything that was transmitted or every receiver that was listening. WSPRadar therefore needs evidence before treating an absent report as a missed opportunity.

An RX **confirmed opportunity** concerns one transmitter identity in one two-minute WSPR cycle on the selected band:

| Evidence in that cycle | How WSPRadar treats it |
| :--- | :--- |
| G3ZIL reports the transmitter. | **Success.** The decode itself confirms the transmission and G3ZIL's activity. It counts even if nobody else reports that transmitter. |
| Another eligible receiver reports the transmitter, and G3ZIL reports another signal on the same band in that cycle—but does not report this transmitter. | **Miss**, shown as **Heard by others only**. Both the transmission and G3ZIL's receiving activity have supporting evidence. |
| The necessary activity cannot be established. | **Unknown; excluded.** Silence alone does not create a miss or an SNR value. |

If several receivers report the same transmitter in one cycle, that still gives one opportunity for G3ZIL. An additional external report also does not count a Target success twice.

This gives the central calculation:

**Decode Rate = successful opportunities ÷ confirmed opportunities × 100.**

Confirmed opportunities are successes plus supported misses. Cycles in which G3ZIL reported nothing cannot establish its activity, so they are excluded rather than scored as failures. This analysis consequently describes **observable receiving activity**, not station uptime or every transmission attempted during April.

Also remember what another receiver proves: the transmitter was on air. It does not prove that the propagation path to G3ZIL should have supported a decode. **100% is not an expected score for a receiver listening to a geographically varied beacon population.**

<!-- section: load-demo -->

## Load the demo and check its settings

Open this demo with **Run in WSPRadar App**, or choose the G3ZIL **RX Performance** profile under **Load Demo**. The prepared settings save you entering the station and dates manually.

For a first visit, choose **Walk me through the setup**. Check **Question → RX Performance**, then **Target and measurement window** and **Optional Filters, scope and evidence**. At **Review — ready to run ✓**, select **Run RX Analysis**. The alternative **Skip to review and run** shortcut starts the prepared analysis immediately.

{{demo_settings_table}}

The run covers **1 April 2017 at 00:00 UTC to 1 May 2017 at 00:00 UTC**, on **40 m**, with **Maximum peer distance from Target set to 22,000 km** for worldwide coverage. **All 24h** retains every solar state. The saved **Exclude Special Callsigns Q, 0, 1** and **Exclude Moving Stations** choices are both off, preserving this demo's selected population. Keep those settings to reproduce the supplied results.

Two thresholds deserve attention:

- **Minimum confirmed opportunities per station: 3.** This is a minimum of successes **plus misses**, not three successful spots. A transmitter with three supported misses can qualify with a 0% Decode Rate. The setting retains sparsely observed identities; with only three opportunities, possible rates are very coarse. For your own investigation, check whether a higher threshold or a longer comparable run gives the same broad pattern.
- **Minimum qualifying stations per map segment: 1.** One qualifying transmitter can color a segment. This preserves geographical detail, but a colored sector is not automatically a well-supported regional result. Inspect its station and opportunity counts before drawing a conclusion.

The usual interactive opportunity minimum is five; this guide preserves the supplied run's value of three. Neither threshold is a statistical confidence level. A separate requirement for constructing each path's SNR-deviation baseline will appear in the time view.

Wait for the run to show **Complete**, then follow:

**Global View → Segment Inspector → Performance Evidence → Temporal Evidence → Station Insights → Selected Station Evidence → Drill-Down.**

Begin with **Full Range | All Directions** in **Segment Inspector**. In this run, “Full Range” means the worldwide population retained by the 22,000 km setting. Performance's statistics, time views and station browsing follow the Inspector's scope; restore that full selection after exploring a region.

Keep **12h** for the Inspector's chronological time grouping. The selected-station view has its **own** time control; keep that at **12h** too. The right-hand **By UTC Hour** panels always combine matching one-hour periods across dates.

<!-- section: performance-map -->

## Read the map: where was reception more consistent?

In **Global View**, open the **RX Performance Decode Rate** map. G3ZIL is at the center; compass sectors show direction from its QTH, and rings separate distance ranges.

**Sector color is the Station-balanced Decode Rate.** WSPRadar calculates a rate for each qualifying transmitter, then takes the **arithmetic mean** of those rates. Each identity has one equal contribution, whether it supplied ten opportunities or ten thousand. Read the percentage legend: warmer colors indicate higher rates.

The markers answer a different question. **Green** means G3ZIL heard that transmitter at least once during the run. **Gray** means there were confirmed opportunities, but that transmitter was heard only elsewhere. A green marker can still represent a path with many misses.

### Compare nearer Europe with distant WNW paths

The broad pattern is a stronger concentration of successful reception on nearer European paths, with much less consistent reception in the distant west-northwest direction. Use **Segment Inspector** to inspect these two scopes:

| Inspector selection | Transmitters heard at least once / qualifying identities | Station-balanced Decode Rate |
| :--- | ---: | ---: |
| **ESE · 0–2,500 km** | **112 / 123** | **51.6%** |
| **WNW · 5,000–10,000 km** | **138 / 481** | **5.1%** |

The distant sector actually supplied more individually heard transmitters. Yet those successes came from a larger candidate population, and reception was far less consistent. **A useful DX footprint and a low Decode Rate can coexist.** That is why counting green markers alone misses much of the story.

Now look beyond 10,000 km. Green markers extend to Australia and New Zealand. **ZL4KT (RE54GD)**, about **19,200 km** from G3ZIL, supplied **three successful decodes in 61 confirmed opportunities**. That is a striking addition to the station's observed reach, while the small number of successes makes it an example of occasional reception rather than dependable coverage.

A colored **0%** sector means qualifying opportunities existed but produced no Target successes. An unfilled or insufficient-evidence sector does not establish a measured 0% rate. With this demo's one-station segment minimum, small isolated patches also need more caution than these well-populated examples.

These are results for the sampled paths and complete receiving setup. The map does not isolate an antenna radiation pattern: transmitter installations, propagation and the distribution of reporting stations also contribute.

Return the Inspector to **Full Range | All Directions** before continuing.

<!-- section: performance-evidence -->

## Open Performance Evidence: reach, consistency and successful SNR

The three distance panels give the map more context. In the supplied export they are grouped as **RX Performance Statistics**, under the app's **Performance Evidence** view.

### Hearing a station once is different from hearing it regularly

The totals above the plots give the starting point: **996 qualifying transmitter identities heard by G3ZIL**, and **1,111 heard only elsewhere**. Thus, G3ZIL reached **47.3%** of the 2,107 qualifying identities at least once.

The left panel, **Station Reach by Distance**, asks whether each transmitter was ever heard. One successful decode is enough. The middle panel, **Decode Rate by Distance**, asks how often reception succeeded across the confirmed opportunities.

Compare a nearby range, a common DX range and the farthest populated range, keeping their different station counts in view:

| Distance | Heard at least once | Station-balanced Decode Rate | Opportunity-level Decode Rate | Median of station successful-SNR medians |
| :--- | ---: | ---: | ---: | ---: |
| **0–2,500 km** | **776 / 1,080 · 71.9%** | **30.7%** | **26.9%** | **≈−15 dB** |
| **5,000–7,500 km** | **143 / 473 · 30.2%** | **5.4%** | **3.4%** | **−28 dB** |
| **17,500–20,000 km** | **5 / 18 · 27.8%** | **3.4%** | **0.3%** | **−31 dB** |

At 5,000–7,500 km, many transmitters made it into the log over the month, but only a small fraction of their confirmed opportunities succeeded. **Distance affects more than the chance of a memorable spot; it also changes how dependable reception is.** The overall pattern is not perfectly monotonic, so inspect support before treating a bump in one distance bin as a general rule. The outer populated bins contain far fewer identities; the empty 20,000–22,000 km bin contains no qualifying identities and does not represent a measured 0% rate.

### Why are there two Decode Rate lines?

**Station-balanced** means averaging the individual transmitters' rates, giving each equal influence. **Opportunity-level** means pooling all successes and all confirmed opportunities, so a frequently observed transmitter contributes more.

For the full selected population, those summaries are **17.9%** and **16.9%**, respectively. The pooled rate uses **114,086 successes out of 673,411 confirmed opportunities**. Both describe relatively intermittent reception across this broad population, but they weight its paths differently.

**Scope also matters.** Expanding this same April record beyond 10,000 km adds **27 heard transmitter identities**, but those added paths supply only **208 successes in 36,738 confirmed opportunities**. The worldwide percentages are consequently lower than in the earlier 10,000 km view, even though its original observations are unchanged. When comparing your own runs, keep the geographic scope consistent so a change in the included paths is not mistaken for a change in the station.

The distinction becomes clearer in the distance plots, where the two lines sometimes separate. A lower opportunity-level rate means the more frequently observed paths pull the pooled result downward in that bin. Use **Station Insights** to see which stations and counts contribute; neither line is a universal rating of the receiver.

### Successful SNR shows the signals that made it through

The right panel, **Successful SNR by Distance**, first calculates each heard transmitter's median successful SNR, then takes the median of those station medians. The shaded **IQR** contains the middle half of the contributing station medians; it shows variation across paths, not a confidence interval.

All Performance SNR values use a common **30 dBm, or 1 W, reported transmit-power basis**. WSPRadar adjusts the reported SNR for the transmitter's reported power. This helps compare successful reports from stations using different powers, but it does not recreate the decodes that would have occurred if everyone had actually transmitted at 1 W.

**The success and miss counts remain the observations at the powers actually used.** Power normalization changes the SNR values, not those counts. A normalized SNR can therefore be below the raw SNR at which the decoder received the signal.

The distant successful reports are generally weaker in this dataset, alongside lower Decode Rates. But misses have **no measured Target SNR** and do not appear in the SNR profile. If a station starts decoding additional marginal signals, its successful-SNR median can even fall while its reception improves. Always read successful SNR together with reach and Decode Rate.

<!-- section: snr-deviation -->

## Read Temporal Evidence: when were paths stronger or weaker than usual?

Keep **Full Range | All Directions** and **12h** selected. Open **Successful RX SNR Deviation over Time** and its **By UTC Hour** companion.

### The zero line is each path's own usual level

A nearby transmitter and a distant one can have very different normal SNRs. Simply averaging their absolute SNRs could move the summary when a different mixture of stations appears. This view instead asks: **was each observed path stronger or weaker than its own usual successful level?**

For each transmitter, WSPRadar subtracts its median successful SNR over the run. If a path's usual value is −15 dB and a successful observation is −10 dB, its deviation is **+5 dB**. **0 dB means that path's usual successful level**; it is neither zero signal nor equality with another receiver.

A path needs **at least three successful observations** to establish this baseline. That is separate from the earlier minimum of three confirmed opportunities, which can include misses. Here, **831 transmitter identities** support an SNR-deviation baseline; the Decode Rate views can include the larger population of qualifying transmitters, including those never heard.

### Read the pattern, then the contributing evidence

I’d use **15–19 April** for the near-zero comparison: the decline is already present on 20 April. “Dip” is more defensible than a statistical “outlier,” and “paired reception” does not apply to this Performance view.

The chronological panel shows an unsettled month rather than one fixed reception level. Focus on **15–19 April**, when the median path deviation stays close to **0 dB**. On **20 April**, it drops to **-5 dB** in both 12-hour intervals. This indicates weaker successful reception relative to the contributing paths’ own median successful SNR over the run, although the contributing station population also changed.

**Space-weather context**
NOAA reported **G2 (moderate) geomagnetic storm conditions at 04:33 UTC on 20 April 2017**, associated with continued coronal-hole effects. This provides relevant context for the same-day dip in median path deviation, but the coincidence does not establish that the storm caused the observed weakening. [NOAA’s original 20 April report](https://www.spaceweather.gov/news/g2-moderate-geomagnetic-storm-conditions-met)

The right-hand panel makes the time-of-day association easier to see: successful signals are generally **around 3–4 dB below their path baselines through late morning and early afternoon**, rising to **about 2–3 dB above them in the early evening**. These are departures from each path's own baseline, not changes in antenna gain.

The line with circular markers follows the median and the shaded band the middle half of contributions. The colored background shows where values are concentrated. Its density scale is relative within each panel: the hottest cell is the most populated, not the strongest reception or 100% of all observations.

<details class="case-evidence-details">
<summary>What receives equal weight in these time summaries?</summary>

<p>In the chronological panel, each transmitter contributes at most one median deviation per 12-hour bin. The right-hand panel first forms one median for each transmitter, date and UTC hour, then summarizes those contributions. A transmitter present on more dates can therefore contribute more values to the folded panel. The folded view combines matching hours; it does not follow one continuous day or guarantee that every day repeated the same pattern.</p>

</details>

Next, check the supporting opportunities and Decode Rates. A successful-SNR pattern alone cannot show which signals disappeared from the decoded sample.

<!-- section: temporal-evidence -->

## Read the reception history alongside the SNR pattern

In **Temporal Evidence**, compare **Evidence over Time** with **Evidence by UTC Hour (1 h bins)**. Keep the Inspector's chronological grouping at **12h**.

The most useful first reading is the **Decode Rate line with circular markers**, together with how much evidence supports it. Reception is generally less consistent in the early UTC hours and more consistent through the afternoon and early evening. The chronological panels show that the size of the result still varies between days.

### Understand the two rows

The **upper line** averages the contributing transmitters' rates equally. The full height of each chronological bar is the number of contributing identities. Each station's one unit of support is divided between green success and gray miss in the proportions of that station's Decode Rate. For example, a transmitter with a 25% rate contributes **0.25 green and 0.75 gray**.

Those green portions are therefore **not a count of whole stations heard at least once**. That was the separate reach measure in the distance profile. This distinction matters when a station is heard sometimes but missed often.

The **lower row** is simpler to count: green represents successful opportunities and gray represents supported misses. Its line shows the pooled **Opportunity-level Decode Rate**. Read the left axis for support and the right axis for the percentage.

In the right-hand panels, **Avg. TX Stations** and **Avg. Opportunities** describe average support per represented date at that hour. They are not the month's unique-station or opportunity totals. The rates use the retained opportunities at each hour, rather than an unweighted average of daily percentages.

### A useful pattern is also a useful question

Across the two temporal figures, weaker-than-usual successful SNR around midday and higher Decode Rates later in the day suggest useful periods to investigate. They do not identify the cause. The mix of paths and transmitters changes with time, and local noise, interference, reporting and propagation can all affect the observations.

For your own station, use the hourly profile to choose a time worth examining, then use the chronological view to see whether the behavior appears on several dates. Changing the chronological grouping to **6h** or **1h** can reveal detail without rerunning the analysis; the fixed one-hour folded panels remain unchanged. Restore **12h** to match this guide's figures.

A missing interval means no eligible evidence for that summary, not a measured 0% rate or 0 dB SNR. The next step is to follow one well-observed transmitter, so changing station populations no longer dominate the comparison.

<!-- section: stations -->

## Open Station Insights: choose a path with something to teach

Restore **Full Range | All Directions**, then open **Station Insights**. In RX Performance, the table lists transmitting station identities within the Inspector's current scope.

Read a station's Decode Rate with its counts. In the export, **Target (T)** counts successful opportunities, **Elsewhere (E)** counts supported misses, and **T/(T+E) (%)** is the station's Decode Rate. The median SNR column describes its successful reports on the common 1 W basis.

The saved view initially hides identities G3ZIL never heard. Enable **Heard only by other stations.** to reveal them. The visible list then expands from **996 heard identities** to the full **2,107 qualifying identities**, including **1,111 with no Target successes**. Those zero-success stations already contributed to the map, reach denominator and Decode Rates; the control changes their visibility, not the results.

**Station Insights → Filter** can narrow the table by callsign or other columns. A table filter does not change the map or Inspector statistics. Clear it when returning to the full list.

Select **HB0QRP (JN47)**, the path saved with this demo, and open **Selected Station Evidence**. At approximately **844 km, 113° ESE**, it lies in the nearby region examined earlier. It supplies **7,762 confirmed opportunities**, including **3,412 successes**, for a **44.0% Decode Rate**. Its median successful normalized SNR is **−15 dB**.

We use this station because it has substantial evidence through the month and a clear daily contrast. It lets us ask whether the wider time pattern also appears on one fixed reported path. It is an informative example, not a claim that every European transmitter behaves the same way.

<!-- section: selected-station-snr -->

## Follow HB0QRP: what did its successful signals look like?

Keep **HB0QRP (JN47)** selected and set the selected-station time control to **12h**. This control is separate from the Inspector's setting.

The hourly profile shows a clear weaker period around late morning, followed by stronger successful reception toward the evening. The chronological panel adds another dimension: some dates are noticeably weaker than others, even before comparing times of day.

Return to the earlier comparison of **00:00–12:00 UTC on 16 and 22 April**. HB0QRP's median successful SNR is **−13 dB** in the first interval and **−20 dB** in the second. The selected path therefore also weakens in the interval where the wider population's deviation was lower. This is useful agreement between views of the same run; it does not identify whether propagation, noise or another factor caused the change.

For this one path, the chronological median summarizes the successful observations in each 12-hour bin. The hourly profile first summarizes each date's successful reports in that hour, then takes the median across those daily summaries. The shaded band shows the middle half of the contributing values where there is enough support.

Now keep the same station and look at how often it was decoded. A path can supply respectable SNR when heard and still be missed frequently.

<!-- section: selected-station-evidence -->

## Check HB0QRP's Decode Rate: when was it more dependable?

Read the selected station's opportunity history alongside its successful-SNR figure.

The hourly view shows a morning opening and a stronger afternoon/evening period, with much less dependable reception around late morning. Three points illustrate the pattern without needing to read every hour:

| UTC hour, combined across April | Confirmed opportunities | Decode Rate | Hourly successful-SNR profile, approximately |
| :--- | ---: | ---: | ---: |
| **07:00–08:00** | **435** | **71%** | **−15 dB** |
| **11:00–12:00** | **416** | **16%** | **−19 dB** |
| **20:00–21:00** | **379** | **65%** | **−11 dB** |

These are supported by hundreds of opportunities in each hour over the month. The late-morning reduction accompanies weaker successful signals. Yet the evening's stronger successful SNR does not translate into a higher Decode Rate than the morning's. **Successful signal level and reception consistency are related observations, not interchangeable scores.**

The comparison between individual dates is similarly useful. On **16 April, 00:00–12:00 UTC**, G3ZIL decoded **61 of 108** confirmed HB0QRP opportunities, about **56%**. In the same interval on **22 April**, it decoded **14 of 98**, about **14%**. The opportunity counts are of a similar order, while both the rate and successful SNR are lower on the later date.

This is a practical way to investigate an apparent change: keep the transmitter identity and time interval comparable, then check both outcomes and successful signal levels. At your own station, those dates would be candidates to compare with operating notes, equipment changes or noise observations.

Because only one transmitter is selected, there is no difference between an equal-station and pooled rate within a populated bin. In the upper chronological panel its total support is one station, split fractionally between success and miss; the lower panel shows how many opportunities produced that result. A high percentage based on very few opportunities would need more caution than the percentage alone suggests.

<!-- section: drill-down -->

## Use Drill-Down to verify what the summaries count

With **HB0QRP (JN47)** still selected, open **Drill-Down**. The supplied selected-station CSV contains the full retained path record. A short sequence on **9 April** shows how the classification works:

| Date/time, UTC | Exported Outcome | Target (T) | Elsewhere (E) | Target SNR, dB @ 30 dBm |
| :--- | :--- | ---: | ---: | ---: |
| **9 Apr 18:08** | `T - Target` | 1 | 0 | −8 |
| **9 Apr 18:12** | `Target-only` | 1 | 0 | −8 |
| **9 Apr 18:16** | `T - Target` | 1 | 0 | **0** |
| **9 Apr 18:20** | `E - Elsewhere` | 0 | 1 | **—** |

*Source: `performance/table_drilldown_selected_stations.csv` in the supplied analysis export. The dash represents an empty SNR field.*

The first row is a successful G3ZIL decode with external confirmation. The second is a success reported **only by G3ZIL**. It still establishes its own opportunity and counts once. The **Elsewhere (E)** column remains zero in both: it counts misses, not every occurrence of another receiver reporting the transmitter.

The third row contains a genuine **0 dB normalized SNR**. The final row has **no Target SNR** because G3ZIL did not report a successful decode; the external transmission evidence and Target-activity evidence support a miss. Missing SNR must not become zero, a weak invented value or a point on the successful-SNR chart.

You can also check the activity evidence: at **18:20**, the all-stations Drill-Down CSV contains a successful G3ZIL report of **HB9TSO (JN47)**. That confirms G3ZIL was receiving in that cycle. HB0QRP's separate miss row records the external evidence of its transmission; hearing HB9TSO alone would not establish an HB0QRP opportunity.

To inspect this interval in the app, choose **Zoom window → 1h**, **Center date (UTC) → 2017-04-09** and **Center time (UTC) → 18:30**. Check the displayed **Selected window** bounds. The focused SNR plot shows the retained successful observations at their actual cycle times, rather than the 12-hour medians used above. **Filter table** can further narrow displayed rows without changing the calculations or focused plots. Set **Zoom window** back to **Off** and clear any **Filter table** conditions to restore the full selected-station record.

The four rows are a teaching example within a much larger record, not an estimate of the month's Decode Rate. Their value is that you can trace the summarized successes and misses to individual evidence and see why not every blank or absent report has the same meaning.

<!-- section: takeaways -->

## What this run teaches—and how to use it at your station

G3ZIL's low-dipole receiving setup heard a broad set of transmitters during April, including occasional reception nearly 19,200 km away. Reception was substantially more consistent on nearer paths, while the time views revealed useful hourly and day-to-day variation. The HB0QRP example connects that wider picture to one transmitter with enough observations to examine closely.

The main lesson is to **read reach, Decode Rate and successful SNR together**. Reach records the paths that made it into the log. Decode Rate adds how consistently they succeeded within confirmed opportunities. Successful SNR describes the signals that made it through, while the deviation view shows when paths were stronger or weaker than their own usual levels.

The original paper used station comparisons and installation notes to investigate reception. This Performance tour adds a different perspective: a baseline for one receiver, with an explicit opportunity denominator and a route from regional patterns to individual observations. It does not reconstruct the paper's comparative figures or isolate the dipole's gain.

For your own first run, start with a stable receiving setup and a documented period. Look for a meaningful distance, direction or UTC-hour pattern, then choose a path with enough support to examine it. Extend or repeat the observation period to see which patterns persist; more observations improve the evidence, but changing propagation and station populations still matter. A later Performance run can help you investigate a change. A controlled **RX Benchmark** is the appropriate next step when you want to compare two setups under known common operating conditions.

### Save the evidence behind the story

Before saving this demo, restore **Full Range | All Directions**, select **HB0QRP (JN47)**, keep both chronological settings at **12h**, return Drill-Down **Zoom window** to **Off**, and clear any Drill-Down **Filter table** conditions. To match the supplied Station Insights table, clear its column filters and turn **Heard only by other stations.** off again.

Select **Prepare All Results for Download**, then **Download Prepared Results**. Prepare the package again after changing the scope, selected station or other inspection choices. The ZIP preserves the figures, tables, processed evidence, configuration and run metadata. **Save Config** is useful for restoring settings and supported view choices, but does not preserve the observations themselves.

Keep operating notes alongside your own exports: antenna and receiver arrangement, changes, outages and any independent noise measurements. The data can point to a period worth investigating; those notes help explain it.

<details class="case-evidence-details">
<summary>About this saved evidence</summary>

<p>This guide uses the worldwide export prepared on <strong>24 October 2026 at 20:01 UTC</strong>, with <strong>WSPRadar v1.0 RC3</strong>, using <strong>WSPRDaemon WD2</strong>. Its historical compatibility fallback relaxed the strict database mode-code filter; the metadata records that selection. It should not be read as independent verification of the physical mode of every historical record. A later database query can differ, so retain the supplied package when reproducing these examples.</p>
<p>The <a href="/assets/demos/griffiths_squibb_rx_performance/source/original_export.zip">original analysis export</a>, <a href="/assets/demos/griffiths_squibb_rx_performance/evidence/verified_claims.md">verified examples and calculations</a>, and <a href="/en/documentation/full/#sec-3-rx-performance">RX Performance documentation</a> accompany this guide. The configuration restores the settings; the original package is the evidence record.</p>

</details>

[Run this guided demo in WSPRadar]({{demo_launch_url}})
