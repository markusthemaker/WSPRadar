<!-- section: hero -->

# Guided Demo · Milazzo study

*Horizontal loop vs GAP Titan on 40 m — follow the reports and check the result.*

What makes two WSPR reports comparable? And what can we learn from the reports that do not form a pair?

This guided demo revisits an early WSPR antenna study with a small enough sample to inspect ourselves. We will start with the published graphs, follow individual reports into WSPRadar, reproduce a few results, and then explore the wider analysis. Along the way, we will see why the WSPR cycle, grid locator and transmit power matter.

The two measures answer different practical questions. <strong class="defined-term">ΔSNR</strong> compares signal quality on matched observations. <strong class="defined-term">ΔDecode</strong> compares how many reports were actually recorded, including reception observed by only one setup. Understanding both helps you assess your own station.

<!-- section: setup -->

## Meet the experiment

In her 2011 study, *Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*, Carol Milazzo, KP4MD, compared a full-wave 40 m horizontal loop, about 5 m above ground, with WB6RQN's GAP Titan DX vertical. The stations were 29 km apart in the Sacramento area. VE6PDQ in Edmonton supplied the selected distant path. [Read the original study](https://www.qsl.net/kp4md/wspr.htm).

The article examined both **transmission and reception**. It also recorded different operating schedules: WB6RQN used frequency hopping, while KP4MD remained on the frequency under study. Keep that difference in mind when we count reports.

Our replay covers **19 December 2010, 12:00 UTC to 20 December 2010, 20:00 UTC**, on **40 m**. **KP4MD is always Target; WB6RQN is always Reference.** Their roles change when we reverse the direction:

| Example in this guide | Who transmits? | Who receives? | What is compared? |
| :--- | :--- | :--- | :--- |
| **Figure 6 reconstruction — RX** | VE6PDQ | KP4MD and WB6RQN | The two receiving setups observing the same remote transmission. |
| **Figure 7 reconstruction — TX** | KP4MD and WB6RQN | VE6PDQ | The two transmitted signals observed at the same remote receiving-station entry. |

**A note on the historical labels:** the original Figure 6 and 7 titles and captions assign the opposite directions to those established by the matching database records. This guide follows the database's transmitter and receiver fields and the reconciled directions in the comparison PDFs. The original images are retained unchanged. The website displays a dark color adaptation, with the white PDFs still available.

<!-- section: published-figures -->

## Start with Figure 6: what does the graph show?


Read time along the horizontal axis and SNR vertically. A higher SNR means the signal stands out more strongly relative to noise. The cyan and coral traces show how reports from the two setups vary over the period.

The pattern invites comparison, but the dots do not all occur at the same times. The lines connect observations; they do not supply an SNR measurement between them. WSPRadar therefore checks which actual reports can be compared directly.

The accompanying PDFs preserve the historical graphs, reconstruct observations from the database and show the paired results and reception counts:

- [**Figure 6 — RX reconstruction, paired ΔSNR and observed coverage**](/assets/demos/milazzo_tx_buddy/references/WSPRadar_Demo_Milazzo_Figure6.pdf)
- [**Figure 7 — TX reconstruction, paired ΔSNR and observed coverage**](/assets/demos/milazzo_tx_buddy/references/WSPRadar_Demo_Milazzo_Figure7.pdf)

<!-- section: load-demo -->

## Open WSPRadar and check the settings

Begin with a historical RX replay in [**WSPRadar**]({{demo_launch_url}}). The prepared link loads the respective RX settings and starts the historical replay. Later, repeat the historical comparison in TX mode with the same Target, Reference, band and time window.

| Setting | Value for these worked examples |
| :--- | :--- |
| First comparison | Historical RX replay — RX benchmark |
| Target | **KP4MD** |
| Reference | **WB6RQN** |
| Band | **40 m** |
| Start | **19 December 2010, 12:00 UTC** |
| End | **20 December 2010, 20:00 UTC** |
| Minimum spot pairs per station for ΔSNR | **1** |
| Reference SNR correction | **0 dB** |

The minimum of **1 spot pair per station** keeps the sparse paired evidence available for inspection. It allows us to check a calculation based on one observation; it does not establish a reliable typical advantage. For a new experiment, collect enough data to examine results with **3, 5 or 10 pairs per station**, across repeated operating periods and several independent paths.

After the run, go to **Station Insights**. Leave **Filter by selected segment and distance** off so the list uses the completed analysis as its scope. The demo applies **TX Station = VE6PDQ** within that scope. We will start with VE6PDQ, then return to **Global View** and **Segment Inspector** to investigate the other paths.

<!-- section: stations -->

## Find the station: the locator is part of its identity

The demo opens **Station Insights** with **TX Station = VE6PDQ** already applied. The caption reads **Station list: Filtered stations · 2 TX station identities · TX Station = VE6PDQ**. The RX records contain two entries: **VE6PDQ / DO34IR** and **VE6PDQ / DO34**. The database writes the longer locator as `DO34ir`; the difference in letter case is immaterial. Open **Filter** to inspect, edit or clear the setting.

A <strong class="defined-term">station entry</strong> in WSPRadar identifies a remote station by its **callsign and full reported grid locator**. A callsign can appear from different locations, potentially hundreds or thousands of kilometres apart, invalidating many metrics and statistics. Keeping the locator prevents those reports from being automatically mixed into one path.

Here, **DO34IR lies within DO34**. These entries have different reported precision; they do not demonstrate that VE6PDQ moved, or that there were two physical VE6PDQ stations. WSPRadar nevertheless keeps their reported identities separate when matching and summarizing observations. In this case more to illustrate the underlying rationale and reasoning. 

**VE6PDQ / DO34IR** is selected initially. **Selected Station Evidence** follows that entry, with the selected-station time aggregation already set to **3h**. In this RX comparison, VE6PDQ is the remote transmitter; KP4MD and WB6RQN remain the receivers being compared.

### Which reports form a spot pair?

For this RX comparison, a <strong class="defined-term">spot pair</strong> occurs when both compared receivers report the **same remote callsign-and-locator entry in the same two-minute WSPR cycle**. We can then subtract their SNRs for that shared transmission.

A spot pair consists of one retained Target observation and one retained Reference observation matched on band, WSPR cycle, and the remote station’s callsign and full reported locator. Each pair supplies one ΔSNR observation.

When several reports exist for one setup, remote station, and cycle, WSPRadar consolidates them using its existing SNR-selection rules before forming the comparison.

If only KP4MD reports that entry in the cycle, it is **Target-only**. If only WB6RQN reports it, it is **Reference-only**. A station may supply paired observations in some cycles and one-sided observations in others.

These one-sided reports still document reception. They have no second measured SNR to subtract, so they contribute to ΔDecode rather than paired ΔSNR. A missing report does not reveal whether the other setup failed to decode, was operating elsewhere, or did not upload a report.

<!-- section: drill-down -->

## Follow one pair into ΔSNR

With **VE6PDQ / DO34IR** selected, open **Drill-Down Data** and inspect **19 December at 14:46 UTC**. Check the time and locator before comparing the SNR values.

**Drill-Down Data shows the normalized SNR values** (−5 and −13 dB for this pair). The raw reported SNRs and transmit powers used below are available in the [verification ledger](/assets/demos/milazzo_tx_buddy/evidence/milazzo-six-pair-ledger.csv).

The two SNRs recorded in the database are **+2 dB at KP4MD** and **−6 dB at WB6RQN**, for VE6PDQ transmitting at a reported **37 dBm**, approximately 5 W. On the common **1 W / 30 dBm** basis used for the paired comparison, both SNRs are reduced by 7 dB, becoming **−5 dB** and **−13 dB**.

**ΔSNR = Target SNR − Reference SNR = −5 − (−13) = +8 dB.**

The positive sign favors KP4MD. For this one shared transmission, its reported signal-to-noise ratio was 8 dB higher. The comparison concerns the installed receiving setups, including their antennas, receiver chains and local noise conditions.

The Figure 6 reconstruction lets us follow all accepted pairs. Dashed guides connect the reports in the upper plot with their ΔSNR observations below.


Switch between **VE6PDQ / DO34IR** and **VE6PDQ / DO34** to check the five pairs. Each selected-station view contains only its own locator entry.

| UTC | VE6PDQ locator | Target SNR at 1 W | Reference SNR at 1 W | ΔSNR |
| :--- | :--- | ---: | ---: | ---: |
| 19 Dec, 14:46 | DO34IR | −5 dB | −13 dB | **+8 dB** |
| 20 Dec, 07:46 | DO34 | −12 dB | −29 dB | **+17 dB** |
| 20 Dec, 09:04 | DO34IR | −12 dB | −34 dB | **+22 dB** |
| 20 Dec, 15:24 | DO34 | −13 dB | −20 dB | **+7 dB** |
| 20 Dec, 15:46 | DO34IR | −17 dB | −24 dB | **+7 dB** |

*All dates are in 2010. Values are power-normalized for comparison, rather than the raw SNRs at which decoding occurred. [Six-pair verification ledger, including database record IDs](/assets/demos/milazzo_tx_buddy/evidence/milazzo-six-pair-ledger.csv).*

Sorted from lowest to highest, the five differences are **7, 7, 8, 17, 22 dB**. Their median—the middle value—is **+8 dB**.

**All five spot pairs favor KP4MD's receiving setup, but their differences vary from 7 to 22 dB.** That supports a consistent direction within this small sample. It does not establish a constant 8 dB advantage throughout the 32-hour window.

Keep the scope of each summary clear:

| Selected evidence | Spot pairs | Median ΔSNR |
| :--- | ---: | ---: |
| VE6PDQ / DO34IR | 3 | +8 dB |
| VE6PDQ / DO34 | 2 | +12 dB |
| Both entries' individual pairs pooled, as in the PDF | 5 | +8 dB |

With an even number of observations, the median averages the two middle values; DO34's +12 dB therefore summarizes its +7 and +17 dB pairs.

**The PDF's +8 dB line summarizes the five individual pairs.** A map segment instead summarizes qualifying station medians, giving each station entry one value. These are different ways of weighting the evidence; the pooled five-pair result is not an all-station or map result.

<details class="case-evidence-details">

<summary>Why the locator matters here: what changes if we match on callsign alone?</summary>

<p>A separate check of these same database records finds three additional same-cycle comparisons if the locator is ignored. In each, one receiver reports VE6PDQ as DO34 and the other as DO34IR. They do not meet the exact callsign-and-locator matching rule.</p>

<p>Including those cross-locator comparisons would change <strong>five pairs to eight</strong> and the pooled median from <strong>+8 dB to +11.5 dB</strong>. This is a different matching assumption, not a correction to WSPRadar's result. The extra comparisons are not proven physically unrelated transmissions; their reported identities differ.</p>

<p>The same endpoint reports still total <strong>31 at KP4MD and 13 at WB6RQN</strong>, so their overall report-count ratio is unchanged. What changes is which observations count as Paired and which enter paired ΔSNR. Identity is part of the measurement definition, not just a label on a map.</p>

<p><a href="/assets/demos/milazzo_tx_buddy/evidence/milazzo-cross-locator-comparisons.csv">Inspect the three cross-locator comparisons and their database IDs.</a></p>

</details>

<!-- section: evidence -->

## Count what else was heard

Return to **VE6PDQ / DO34IR** and open its **ΔDecode Temporal Coverage**. Use **3h** to match the reconstruction's time bins.

The spot-level colours show three outcomes: **Paired in green**, **Target-only in magenta**, and **Reference-only in cyan**. A three-hour bin groups observations for display; pairing still uses the individual WSPR cycle and station identity.


Across this entry's full window, there are **8 Target-only, 3 Paired and 5 Reference-only** observations. Each paired observation contributes one report to each receiver:

| Receiver | Reports counted | Total |
| :--- | :--- | ---: |
| KP4MD — Target | 8 Target-only + 3 Paired | **11** |
| WB6RQN — Reference | 5 Reference-only + 3 Paired | **8** |

**11 ÷ 8 = 1.38×:** KP4MD recorded 1.38 times as many reports from this station entry. This is an observed decode-count ratio. It is not the fraction of all attempted transmissions successfully received; cycles with no report from either receiver are absent from this evidence.

The line uses the right-hand fold scale: **1×** means equal counts; values above or below it name the favored side. **Exclusive** means only one side was observed in that bin. A blank bin has no retained observations, so it supplies no ratio.

The colours also explain why the SNR plot contains so few points. Many cycles produced a report at only one receiver. Those observations add reception evidence even though they cannot add a paired SNR difference.

For a useful check, look at **19 December, 15:00–18:00 UTC**. Each receiver has one report, giving **1×**, but there are **zero spot pairs**. Both heard this station entry within the bin, at different times. Equal counts do not create a matched SNR measurement.

The separate **DO34** entry contributes **20 versus 5 reports**. Adding the two entries gives **31 versus 13**, or **2.38×**, for the selected RX path as represented in the PDF. Selecting either entry alone in WSPRadar will show its own evidence.

<!-- section: tx-comparison -->

## Reverse the direction: Figure 7

Before switching to TX, save the RX results: under **Download Evidence**, select **Prepare All Results for Download**, then **Download Prepared Results**. Use **Save Config** to retain the RX settings too.

Use **Run in WSPRadar App · TX** beside this section heading to run a historical **TX benchmark** for the same Target, Reference, band, dates and other settings. The prepared TX link filters **Station Insights** to **VE6PDQ** and preselects **VE6PDQ / DO34IR**. VE6PDQ is now the remote receiver reporting the two compared transmitters.


For a **TX spot pair**, the same remote receiving-station entry must report **both compared transmitters in the same WSPR cycle**. This aligns the receiver and observation time. It does not remove differences between the transmitting installations.

The selected TX records contain **76 reports but only one spot pair**. Open **Drill-Down Data** at **20 December, 00:22 UTC** to inspect it. Its normalized SNR columns show **−20 and −18 dB**; the raw values and reported powers in the following table come from the linked verification ledger.

### Check transmit power before subtracting SNR

KP4MD's reports specify **37 dBm**, approximately 5 W; WB6RQN's specify **33 dBm**, approximately 2 W. To compare their SNR on a common power basis, WSPRadar accounts for that reported power difference.

| Transmitter | Raw reported SNR | Reported TX power | SNR on the common 1 W basis |
| :--- | ---: | ---: | ---: |
| KP4MD — Target | −13 dB | 37 dBm | **−20 dB** |
| WB6RQN — Reference | −15 dB | 33 dBm | **−18 dB** |

Raw subtraction would give **+2 dB**. On the common power basis, **ΔSNR = −20 − (−18) = −2 dB**, favoring WB6RQN for this one paired observation.

That change of sign shows why the power basis matters. In the PDF's common 37 dBm presentation, the same pair is −13 versus −11 dB and still gives −2 dB. The detailed scale reconstruction remains in the linked PDF.

**One pair can verify a calculation, but cannot establish a typical TX advantage or a time trend.** A median marker and the exact observation may both appear in the chart; they still represent one pair.

<!-- section: tx-cycle-matching -->

## Why the nearby points do not form another pair


Look at **20 December, 10:34 UTC** for KP4MD and **10:36 UTC** for WB6RQN. They have equal SNR after power normalization, but belong to different cycles. They therefore supply **no paired comparison**.

This is what same-cycle pairing means here: use the same WSPR cycle, rather than moving timestamps, pairing the nearest dots or subtracting the connecting lines. The unpaired observations remain useful in the reconstructed traces and in the reception counts.

### Compare signal margin with the recorded decodes

Open the selected receiver's **ΔDecode Temporal Coverage**. Across the window, VE6PDQ reported **57 KP4MD transmissions and 19 WB6RQN transmissions**: **3× as many Target reports**. They comprise **56 Target-only, 1 Paired and 18 Reference-only** events. [See the full TX coverage plot and bin counts](/assets/demos/milazzo_tx_buddy/references/WSPRadar_Demo_Milazzo_Figure7.pdf#page=2).

The one paired SNR result favors Reference; the total count favors Target. Each result describes its own evidence: comparable signal levels on one matched observation, and accumulated reports across the window.

**The decode counts retain the actual transmit powers and operating schedules.** Normalizing SNR does not change how many reports were received. Here, 5 W versus 2 W and the documented frequency-hopping difference prevent us from attributing the 3× count ratio to the antennas alone.

<!-- section: wider-results -->

## Expand from VE6PDQ to the other observed paths

We have checked one remote callsign, with two RX locator entries and one TX receiving entry. Now ask whether its pattern appears elsewhere in the same analysis.

Keep the current analysis mode explicit: in RX, the remote entries are transmitters; in TX, they are receivers. The figures and numbers above concern VE6PDQ only. The wider views combine the other retained station entries too.

<!-- section: delta-snr-map -->

## Global View: where is there paired evidence?

Open the **ΔSNR map**. Read a segment's direction, distance, median and support together. A positive value favors KP4MD; a negative value favors WB6RQN.

Each qualifying station entry contributes its median ΔSNR, and the segment summarizes those station medians. A frequently observed entry therefore cannot dominate simply by supplying more pairs. Check how many entries support the segment, remembering that different locator entries do not necessarily represent different physical stations.

An unqualified segment gives no displayed ΔSNR conclusion. It need not mean that no signals were heard there. The decoding view can still contain reception evidence from that direction.

<!-- section: decoding-reach -->

## Decodes & Stations by SNR: what does the paired sample leave out?

Open **Global View → Decodes & Stations by SNR**. Read from stronger signals on the left toward weaker signals on the right. The upper row accumulates reports; the lower row accumulates distinct station entries. These curves use each side's **raw reported SNR**, rather than the common-power values in our paired calculation.

In **Paired spots**, the two report curves end at the same count: each accepted pair contains one retained observation from each side. Separation before the endpoint describes different reported SNRs for shared observations. **One-sided spots** add the reports heard by only one side in their respective cycles.

Ask whether additional reports mainly repeat paths already observed, or also add station entries. A station can contribute both paired and one-sided reports, so extra one-sided spots do not automatically mean extra stations. If the station panels show **Both observed, no pairs**, those entries were heard by both sides during the window, but never in a shared cycle.

Notice where one-sided reports enter along the SNR axis. Extra weak reports can be consistent with additional reception margin, but this historical comparison also contains different powers and operating opportunities. The curves do not establish why any particular report is missing.

<!-- section: delta-decode-map -->

## ΔDecode map: where were more reports recorded?

Open the **ΔDecode map** and compare the same directions and distances as on the SNR map. Its fold labels express observed report-count advantage, with **1×** representing parity. Check which side the legend favors and how much evidence supports the segment.

The segment pools the observed counts; it does not average individual stations' ratios. Both maps can agree, or they can emphasize different paths because paired signal quality and total observed reception use different evidence. Use the support information before giving a large factor much weight.

<!-- section: difference -->

## Segment Inspector: is the summary representative?

Start with **Segment Inspector → Full Range | All Directions** to inspect the wider sample, then select a geographic segment if you want to narrow the question.

In **Benchmark Statistics**, compare the distribution of station results with that of individual paired observations. Station summaries give each qualifying entry one value; the spot-pair summary gives more influence to paths that contributed more pairs. Look at the distribution and sample size as well as the median.

The five-pair Figure 6 median already showed how a small sample can hide considerable variation. A narrow-looking distribution based on very few observations is not evidence of a precisely established antenna advantage.

<!-- section: time -->

## Both temporal views: does the pattern persist?

Open **ΔSNR Temporal Coverage** and **ΔDecode Temporal Coverage** for the same scope. Check where paired measurements exist, how their differences vary, and whether reception continues through one-sided reports when the SNR evidence disappears.

Inspect the chronological view before the profile by UTC hour. This run spans only 32 hours, so an hourly profile contains very few repetitions of each hour. Change the time aggregation to examine the evidence more closely; larger bins combine observations but do not create new pairs or additional operating time.

Where station-level and spot-level coverage are shown, distinguish their questions. A station can be observed by both sides within a bin at different times; a spot-level Paired event requires the same cycle. The equal-count, zero-pair RX example demonstrated that difference.

Finally, return to **Station Insights** and clear the **VE6PDQ** callsign filter through **Filter**. Choose another entry with a clear purpose—more paired evidence or a different result—and follow it into **Drill-Down Data**. Use **Include one-sided evidence** if you also want to list entries without paired observations. Check the chart's selected identity and scope before comparing it with VE6PDQ.

<!-- section: paper-comparison -->

## What does WSPRadar add to the historical comparison?

The reconstructed traces retain the observed changes and gaps that made the original study informative. The complete PDFs explain their correspondence with the published figures and the power scales used. The database also lets us inspect exact timestamps, reported locators and records that a plotted line cannot explain by itself.

WSPRadar adds explicit matching, separate treatment of one-sided reception, and summaries whose contributing observations can be inspected. We have independently checked the six accepted pairs and the reception totals against the database records. This verifies the arithmetic and grouping for these selected examples; it does not establish every paper-marker correspondence or validate all possible analysis cases.

The RX observations favor KP4MD's receiving setup in all five accepted comparisons. The TX sample contains just one common-power comparison, favoring WB6RQN by 2 dB. Those small, differently sampled sets do not demonstrate an antenna advantage reversing between transmission and reception. Their value here is that we can follow precisely what each result measures.

<!-- section: takeaways -->

## Save the evidence and apply the method to your own station

We can now account for the selected-path results:

| Evidence checked | Paired signal-quality result | Observed reception |
| :--- | :--- | :--- |
| RX, both VE6PDQ locator entries | Five pairs; pooled median **+8 dB** for KP4MD | **31 versus 13 reports**, or **2.38×** as many at KP4MD |
| TX, VE6PDQ / DO34IR | One pair; **−2 dB** on a common power basis | **57 versus 19 reports**, or **3×** as many for KP4MD |

These results become useful because we know their identities, timing, power basis and support. The sparse matched sample and differing operating opportunities limit the antenna conclusions, while leaving the individual calculations fully checkable.

Under **Download Evidence**, select **Prepare All Results for Download**, then **Download Prepared Results**. Save the RX and TX results separately. **Save Config** preserves the reusable settings, including the active Station Insights filters and selected identity; shared analysis URLs preserve those filters too. Keep operating notes alongside them so a later analysis records which antennas were connected, the powers used and when each setup was active.

For this manual check, the companion files include the **120 endpoint reports from the database**, their record IDs, the **six-pair ledger**, and the **identity-specific and three-hour count tables**:

- [**Download the selected-path verification data**](/assets/demos/milazzo_tx_buddy/evidence/Milazzo_Verification_Data.zip)
- [Read the data scope, calculation rules and source query](/assets/demos/milazzo_tx_buddy/evidence/README.md)
- [Open the Figure 6 RX comparison PDF](/assets/demos/milazzo_tx_buddy/references/WSPRadar_Demo_Milazzo_Figure6.pdf)
- [Open the Figure 7 TX comparison PDF](/assets/demos/milazzo_tx_buddy/references/WSPRadar_Demo_Milazzo_Figure7.pdf)

For your own experiment, arrange comparable operation on the same band, record transmit powers and receiver changes, and check the reported locators. Collect more paired observations across several periods and paths, then examine whether the result persists when you raise the evidence requirements. If you want to compare decoding performance, make the actual powers and operating opportunities comparable too; SNR normalization cannot do that retrospectively.

You can now follow a result back to its reports: identify the stations and locators, check the cycle, compare SNR on the appropriate basis, and count the reception outside the paired sample. Use that same sequence whenever a map colour or a large difference catches your attention.
