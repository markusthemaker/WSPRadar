<!-- section: hero -->

# #1 Low Dipole vs Radial-Free Vertical

A low dipole versus a vertical on 40 m — a real-world comparison using WSPR data.

Does a better signal-to-noise ratio also mean more signals decoded? Follow this experiment from two geographic maps to changing signal levels, time of day, an individual transmitter and the underlying WSPR reports. Throughout the results, **ΔSNR** compares signal quality on shared transmissions and **ΔDecode** compares total observed decodes. The paired SNR comparison tells one part of the story; signals decoded by only one setup tell another.

<!-- section: summary -->

## The findings at a glance

- [**Better paired SNR**](#difference)

    <strong class="case-finding-value">+6.5 <span>dB</span></strong>

    The median across station results favored **G3ZIL**. Each station has equal influence.

    57 767 paired observations · 792 station entries

- [**More decoded signals**](#decoding-reach)

    <strong class="case-finding-value">1.65<span>×</span></strong>

    As many decodes at **G3ZIL**: 114 027 versus 69 258. **44 769 additional decodes** overall.

    1 083 station entries versus 876 · a net 207 more

- [**Direction and distance matter**](#delta-decode-map)

    <span class="case-finding-scope">E · 0–2 500 km</span><strong class="case-finding-comparison">+8 dB · 1.67×</strong>

    <span class="case-finding-scope">WNW · 5 000–10 000 km</span><strong class="case-finding-comparison">0 dB · 1.02×</strong>

    Station-balanced ΔSNR · G3ZIL decode factor. Distant WNW was **close to parity**.

<!-- section: setup -->

## Setup: How were the operators testing

In *Improving HF Band SNR*, published in *Practical Wireless* in October 2017, Gwyn Griffiths, G3ZIL, and Nigel Squibb, G4HZX, investigated ways to improve reception on 40 meters. Both used essentially the same homebuilt direct-conversion receiver design, but at different locations and with different antennas. [Original paper](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

**G3ZIL — IO90HW:** A low horizontal dipole, with its center raised to about 4 meters and its ends at 1.5 meters. The receiver had been moved to a garden shed.

**G4HZX — IO91:** A Hustler 5-BTV vertical connected to a ground spike, without radials, at the far end of the garden.

**G3ZIL is the Target receiver; G4HZX is the Reference receiver.** A **station entry** in the results identifies a remote transmitter by its callsign and reported locator.

The paper also records retuning G3ZIL’s dipole on **8 April**. This was an investigation of real installed stations, not an untouched laboratory setup.

**Our question is: how did these two receiving stations compare during April 2017?**

Each station uploaded reports of the WSPR signals it decoded. WSPRadar matches occasions when both reported the **same transmitter in the same two-minute WSPR cycle**. These <strong class="defined-term">Joint Spots</strong> let us compare their SNR at the same time, rather than comparing one station’s good afternoon with the other’s reception on a different day.

A <strong class="defined-term">Target-only</strong> observation means G3ZIL reported that transmitter-cycle and G4HZX did not; <strong class="defined-term">Reference-only</strong> means the reverse. These are useful observations too: when only one setup decodes, there is no second measured SNR to subtract, but there is still evidence of reception.

<!-- section: load-demo -->

## Load the demo and check its settings

Select **Run in WSPRadar App** above to open **demo #1: Low Dipole vs Radial-Free Vertical** with its prepared settings. You do not need to enter the station details manually. Review the prepared settings, then select **Run Analysis**. Loading the link does not establish historical uptime. The settings explain what the analysis includes:

{{demo_settings_table}}

For ΔSNR, the per-station minimum of **1 Joint Spot** preserves a potentially valuable paired observation. Requiring **5 stations per segment** reduces reliance on one path. ΔDecode includes every retained event and colors a segment when it contains at least **1% of the full run’s observed events**.

After the run, follow **Global View → Segment Inspector → Station Insights → Drill-Down**, then **Download Evidence**. The maps show where the two setups differ; the following views examine the size, timing and supporting observations of those differences.

Keep **Segment Inspector → Full Range | All Directions** selected unless you want to examine a particular segment.

**Station Insights is independent of the Inspector.** Its station list covers this completed analysis by default. Enable **Filter by selected segment and distance** only when you want to browse stations inside the Inspector's current scope; selected-station evidence still uses that station's full April record.

<!-- section: delta-snr-map -->

## ΔSNR (Signal Quality): where is the SNR advantage?

*How much better is the SNR when both setups decode the same signals in the same WSPR cycle?*

<strong class="defined-term">Signal-to-noise ratio, or SNR</strong><strong>, describes how strongly a signal stands out relative to noise. Higher SNR is better.</strong> For this demo:

<strong class="defined-term">ΔSNR</strong><strong> = G3ZIL SNR − G4HZX SNR</strong>

For example, −22 dB at G3ZIL and −29 dB at G4HZX gives **+7 dB**. **Positive differences favor G3ZIL; negative differences favor G4HZX.** Zero means equal SNR on an individual comparison.

The map is always centered on the target station, here G3ZIL. Compass sectors represent directions from that station; the rings separate distance ranges. This is an **azimuthal map**, with distance measured outward from the target.

A transmitter **qualifies** when it meets the configured **minimum number of Joint Spots per station** (here set to 1 per above settings). We refer to this as a <strong class="defined-term">qualified station</strong>. For each remote transmitter, WSPRadar first examines all its paired WSPR observations—often hundreds or thousands—and calculates the <strong class="defined-term">median ΔSNR</strong>: the middle SNR difference when all measurements are sorted. This gives each station **one representative result**.

Next, for each map segment, WSPRadar takes these station results and again finds the **median (middle value)**. **Every station has one equal voice:** whether it contributed 5 or 500 Joint Spots, it contributes just one value to the segment.

**Why does this matter?** Some WSPR stations transmit far more frequently than others. Without balancing, one very active transmitter could dominate an entire sector, even when most other stations show a different SNR advantage. **Station balancing reveals the typical advantage across different transmitter paths—not simply where the most spots were collected.**

#### Start with Europe, then compare distant West-North-West (WNW) paths

The first visible finding is that **G3ZIL’s advantage is not geographically uniform**. Many nearer European sectors favor G3ZIL clearly, while the distant west-northwest sector containing many North American stations is much closer to equality.

| Geographic scope | Station-balanced ΔSNR | Qualifying station entries | Joint WSPR Spots |
| :--- | ---: | ---: | ---: |
| **0–2 500 km, E** | **+8.0 dB** | **172** | **19 205** |
| **5 000–10 000 km, WNW** | **0.0 dB** | **113** | **2 911** |

Notice the weighting: The 19 205 paired observations from the eastern segment are first reduced to 172 station medians. The middle of those station values gives +8.0 dB. Each station contributes equally, whether it supplied one or thousands of Joint Spots.

That is already a useful result: an overall advantage does not mean that G3ZIL heard every direction better. For an operator interested in European paths versus distant DX, the map is more informative than one monthly number.

**Markers answer a different question from sector colors.** Green **Both (Joint, Qualifying)** identifies a station with enough same-cycle pairs. Pale green indicates Joint evidence below the station minimum. **This does not apply here:** we set the minimum to **1 Joint Spot per station** to retain as many paths as possible, while requiring **at least 5 qualifying stations** before coloring a map segment. <strong class="defined-term">Both (Async)</strong> means both receivers reported that station during the period, but never in the same cycle; it does not imply a clock fault. **Only G3ZIL** and **Only G4HZX** identify stations observed exclusively by that receiver. A Joint station can still have many one-sided observations at other times.

Gray hatching means there is observed evidence but too little qualifying support for a colored segment. Blank segments contain no observed station entries. The neutral color covers values around zero, not necessarily exact equality. Read the numerical scale: it adapts to the results.

> **What is missing from ΔSNR?** ΔSNR requires both receivers to decode the same signal in the same WSPR cycle. When only one succeeds, no paired SNR difference can be calculated—even though that reception may represent a meaningful advantage.
>
> One-sided decodes can occur near the WSPR detection limit, but they can also occur at stronger reported SNRs. Differences in antennas, propagation paths, local noise, interference, decoding or reporting may explain why one setup misses a signal the other receives.
>
> **The next view bridges this gap**, showing how these one-sided observations translate into additional decoded spots and stations.

Return **Segment Inspector** to **Full Range | All Directions** before continuing.

<!-- section: decoding-reach -->

## Decodes & Stations by SNR

*See how reception diverges as signals weaken—and how this translates into more decoded spots and stations.*

#### Read from stronger signals toward weaker signals

Move **left to right** along the SNR axis. The cutoff is lowered in 1 dB steps, progressively including weaker reports. The upper row accumulates spots; the lower row accumulates distinct station entries. Each curve uses **that receiver’s own raw reported SNR**, without power normalization or the Reference SNR correction. Multiple reports for the same transmitter, receiver and WSPR cycle count as one spot, using the strongest raw SNR.

In **Joint**, both receivers decoded the **same transmitter in the same WSPR cycle**, providing directly comparable SNR measurements. Both curves therefore finish at exactly **57 767 paired spots from 792 stations**. Their horizontal separation reflects differences in reported SNR for these shared signals: one receiver generally decoded them at higher SNR than the other. This relates to the **ΔSNR advantage** examined earlier. **Separation before the endpoint is not, by itself, an extra decode**—a Joint observation can enter the two curves at different SNR cutoffs.

The upper middle panel, <strong class="defined-term">One-sided spots — unpaired</strong>, adds the second perspective. It shows **56 260 G3ZIL-only spots** and **11 491 G4HZX-only spots**. These signals were decoded by just one receiver in their respective WSPR cycles. They cannot contribute to paired ΔSNR but remain valuable decoding evidence, regardless of map qualification.

The lower middle panel, **Stations without Joint evidence**, plots stations heard **exclusively by one receiver**: **256 at G3ZIL** and **49 at G4HZX**. The **35 stations heard by both receivers, but never in the same WSPR cycle (Both Async)**, are shown separately as **“Async: +35 stations.”** Including them gives **291 station entries at G3ZIL** and **84 at G4HZX** without any Joint Spots.

The distinction matters: **a one-sided spot does not necessarily represent a new station**. The same transmitter may supply Joint Spots in some cycles and one-sided spots in others. The upper panel includes all one-sided observations; the lower panel plots exclusively heard stations and notes the additional Async stations separately. None of these lower-panel stations supplied a Joint Spot.

#### Read the right-hand endpoints as the observed result

To reconcile the station totals, add **Joint + exclusive + Async** for each receiver. The **All stations** endpoints already include the 35 Async stations; do not add them again.

| Observed evidence | G3ZIL | G4HZX | Net difference |
| :--- | ---: | ---: | ---: |
| Joint Spots (same WSPR cycle) | 57 767 | 57 767 | 0 |
| One-sided spots | 56 260 | 11 491 | +44 769 |
| **Total decoded spots** | **114 027** | **69 258** | **+44 769** |
| Stations with Joint evidence | 792 | 792 | 0 |
| Stations without Joint evidence | 291 | 84 | +207 |
| ↳ Exclusive to this receiver | 256 | 49 | +207 |
| ↳ Both (Async) | 35 | 35 | 0 |
| **Total distinct station entries** | **1 083** | **876** | **+207** |

The **Either** totals are the unions: **125 518 transmitter-cycle events** and **1 132 station entries**, counted once even when both receivers report them. The 35 Async stations contribute to both receivers' station totals but only once to the combined total. At intermediate SNR cutoffs, the Joint-station curves use each receiver’s strongest Joint report, while the All stations curves use its strongest report of any outcome. Their counts therefore need not add at every cutoff.

These results describe **both more observations and additional stations**. Most G3ZIL-only events—**54 030 of 56 260 (96%)**—actually come from stations that also provided Joint evidence. Much of the benefit is additional reception on already-observed paths, rather than only adding new dots to the map.

#### Where do the extra observations sit in SNR?

The raw-SNR median for G3ZIL is **−12 dB on Joint reports**, but **−19 dB on G3ZIL-only reports**. At G4HZX, the corresponding medians are **−19 dB** and **−23 dB**. One-sided reception is therefore shifted toward weaker reported signals at each receiver.

This supports the practical reason for adding decoding evidence: **as signals become harder to decode, paired observations can disappear while one-sided reception remains**. However, Demo #1's one-sided reports span a broad SNR range; they are not all clustered at a single detection limit. Other demos provide a more pronounced weak-signal example, with one-sided observations concentrated at very low reported SNRs. A signal strong at one site may be weak at the other, whose missing SNR is unknown. Different noise, propagation, equipment or reporting can also contribute.

> **A useful surprise:** G3ZIL decoded **256 station entries that G4HZX never reported**. Yet G4HZX also decoded **49 station entries that G3ZIL missed entirely**. Even with a clear overall advantage, G3ZIL did not hear everything. **The Reference still contributed unique reception paths** that would otherwise have been missed.

The count differences here supply the **net additional decodes** used by ΔDecode. The next map divides each segment’s Target-minus-Reference total by the sum of those totals, giving a symmetric measure of decoding advantage. Neither view includes transmissions missed by both receivers, so neither measures absolute decoding probability or a calibrated sensitivity gain.

<!-- section: delta-decode-map -->

## ΔDecode (Decoding Advantage): where are additional signals decoded?

**Which setup decoded more transmissions—and by how much?**

The previous view showed that G3ZIL recorded **1.65× as many decodes overall**. This map shows where that advantage occurred, and where G4HZX came out ahead.

#### From decode counts to a map value

Each setup’s total includes **Joint plus its own one-sided decodes**. WSPRadar pools these counts across all stations in a segment before comparing the totals. Stations contribute their actual decode counts; station ratios are not averaged, and distinct-station reach is a separate result.

For example, in **E at 0–2 500 km**, G3ZIL recorded **34 747 decodes** and G4HZX **20 815**:

**34 747 ÷ 20 815 = 1.67× as many G3ZIL decodes**, a net **13 932 additional decodes**.

#### Read the fold legend

**2× means twice as many decodes for the setup indicated by that side of the legend.** Warm bands favor G3ZIL; blue bands favor G4HZX.

**The central light-green band is not a tie.** Its center marks equal totals, but the band includes advantages up to the **1.25× boundaries in either direction**. A sector can therefore favor Reference by about 20% and still have this central color.

Colors represent intervals: **1.67× falls between 1.5× and 1.75×**. Check the labels when comparing maps because the legend range adapts to the visible results.

#### Compare with ΔSNR

| Geographic scope         |         ΔSNR | Decode advantage | Net extra for that setup |
| :----------------------- | -----------: | :--------------- | -----------------------: |
| **0–2 500 km, E**        |  **+8.0 dB** | **G3ZIL 1.67×**  |               **13 932** |
| **5 000–10 000 km, WNW** |   **0.0 dB** | **G3ZIL 1.02×**  |                  **102** |
| **0–2 500 km, SSW**      |  **+5.5 dB** | **G3ZIL 1.52×**  |                  **987** |
| **0–2 500 km, NE**       | **+5.25 dB** | **G4HZX 1.20×**  |                  **944** |

**E and SSW: both maps favor G3ZIL.** These sectors share the **1.5×–1.75× band**, but supply very different numbers of additional decodes. The factor expresses the relative advantage; the net count shows its volume.

**Distant WNW: nearly equal totals can hide different reception.** The paired ΔSNR median is zero and G3ZIL records only slightly more decodes. This does not mean every paired SNR was equal or that both receivers decoded the same transmissions: opposing one-sided outcomes can largely cancel.

**NE: better paired SNR, fewer total decodes.** G3ZIL leads in ΔSNR, yet G4HZX records **944 more decodes**. ΔSNR summarizes shared observations through station medians; ΔDecode includes all retained decode totals. The two measures can therefore favor different setups. This Reference advantage also explains why a central-colored sector should not be read as equality.

#### How much evidence supports the color?

Here, a sector needs **1 256 observed events**: **1% of the full run’s 125 518 events**, rounded up, with Joint counted once. **Eleven sectors qualify.** Selecting an Inspector segment or changing the map view does not rebase this threshold.

No Joint observation or separate per-station minimum is required for ΔDecode. Exclusively heard and **Both (Async)** stations contribute; Async observations remain one-sided events. ΔSNR keeps its own paired-evidence requirements.

**Hatching means observed evidence below the display minimum, not equal reception.** That evidence remains inspectable. The minimum filters volume, not confidence: use the Segment Inspector to check contributing stations and counts before treating a sector as a regional pattern.

> **ΔSNR compares SNR on shared transmissions; ΔDecode compares total observed decodes.** Interpret both under comparable common operation and reporting. Transmissions missed by both receivers remain unknown, so these results do not measure absolute decoding probability or calibrated sensitivity gain.

<!-- section: difference -->

## Read Benchmark Statistics: how large is the difference?

Below the maps, use **Segment Inspector** to select **Full Range | All Directions**. **Benchmark Statistics**, **ΔSNR Temporal Coverage** and **ΔDecode Temporal Coverage** summarize that same selection. For a closer look at a map region, select its distance range and direction here; restore the full scope to follow the numbers below.

Benchmark Statistics combines which signals were decoded with the SNR difference where both receivers decoded them. It shows how the overall results are distributed, beyond the single summary value on each map.

#### Which stations supply the decoding advantage?

The left panel, **ΔDecode — Decode Volume**, places each station by its Target-versus-Reference decode advantage. **Purple favors G3ZIL; blue favors G4HZX.** The horizontal labels express that advantage as fold ratios, with **1×** at equal totals. Bar height shows the **share of receiver decodes** in each interval, not the number of stations: a frequently decoded transmitter contributes more than one heard only a few times.

Each station contributes its **G3ZIL plus G4HZX decode counts**. Joint contributes once to each receiver, so the histogram represents **183 285 receiver decodes** across the **125 518 observed events**. The red line marks the pooled result, **G3ZIL 1.65×**, not a median of station ratios. All retained stations in this Inspector scope contribute; the map's segment threshold does not filter this distribution.

The separate **Exclusive** endpoints contain decodes from stations heard only by one setup. Large finite ratios remain in the interior bins. These endpoint bars do not contain every one-sided decode: a station heard by both receivers can also supply many Target-only or Reference-only observations.

**Substantial decode volume from stations heard by both receivers lies on G3ZIL’s side of 1×.** Its lead is not confined to exclusively heard stations. This matches the earlier [Decoding Reach finding](/en/demos/griffiths_squibb_fig3/#decoding-reach): much of the additional reception comes from paths that also supplied Joint observations.

About **70% of observed station entries supplied Joint Spots**, but those pairs account for only **46% of observed transmitter-cycle events**. The paired-SNR comparison therefore covers most observed stations while leaving out more than half the observed events—another reason to read the decoding and SNR panels together.

#### What is the typical SNR advantage?

The middle and right panels summarize the matched evidence differently: individual Joint Spots first, then a histogram of station medians. **Both show a clear peak around a positive ΔSNR**, with relatively few extreme values. Together with the close agreement of the two medians, this makes the overall advantage a meaningful summary of the observations. **A broad, strongly skewed or multi-peaked distribution would warrant more caution**, as a single median might conceal important differences between stations, so always consider the full picture.

**Qualifying Joint Spots: +7.0 dB.** Every matched observation contributes to this distribution. Transmitters heard more frequently consequently have more influence.

**Qualifying Stations: +6.5 dB.** Each transmitter contributes one median difference, regardless of how often it was heard. The middle value across those station summaries is +6.5 dB. Most station medians are positive, although some favor G4HZX.

The two medians are close and both positive: the typical station result and the typical individual comparison tell a compatible overall story.

> **Our overall conclusion so far:** G3ZIL had a clear paired-SNR advantage in this April dataset and more observed decoding. The maps have already shown where that conclusion needs to be narrowed. Next, check whether the difference stayed the same throughout the month.

<!-- section: time -->

## Read ΔSNR Temporal Coverage: did the difference change?

**Benchmark Statistics** summarized April as a whole. Here, the qualifying Joint observations are grouped by time, showing when the paired-SNR advantage changes within the same Inspector scope. These are medians of individual Joint Spots, corresponding to the middle statistics panel; the map gives each station one median instead.

Keep **24h** selected for the chronological charts in this part of the guided demo. The right-hand panels use **1h UTC bins**, combining the same hour across April.

#### Left panel: follow the month

In **ΔSNR over Time**, each circular marker is the median paired difference for one day. The result changes substantially: the daily median rises from **+2 dB on 1 April to +9 dB on 15 April**, with fluctuations along the way. Later in the month it generally lies between **+6 and +8 dB**.

The advantage was not merely a fixed offset between two receivers. Its size changed over the observation period—something the single monthly median cannot show.

The authors proposed drying soil as an explanation for the first-half trend. The export contains no soil-moisture measurements, so this guided demo demonstrates the changing SNR difference, not a test of that explanation. [Original paper](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

A few display details help you read the chart correctly. The dashed line is the overall **+7 dB Joint-Spot median**. The shaded band contains the **middle 50% of observations** in each bin; it shows spread, not a confidence interval. Background colors indicate where observations are concentrated, not which receiver is better. Read the labeled dB values—the vertical scale is nonlinear.

#### Right panel: compare hours of the day

**ΔSNR by UTC Hour** gathers observations from the same UTC hour across April. G3ZIL’s paired-SNR advantage is approximately **+7 to +8 dB during much of the daytime**, falling to **+1 to +2 dB after midnight**.

This is consistent with the changing mix of paths discussed in the original study: nearby European daytime reception favored the low dipole, while distant nighttime reception was more competitive for the vertical. The paper’s Figure 6 examines **5–7 April**, whereas this profile covers the whole month. Neither the time-of-day profile nor the map alone measures arrival angle or identifies a propagation mode. [Original paper, Figure 6](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

<!-- section: published-figure3 -->

## Verifying WSPRadar against published research

*A month of paired reception. Compare the original publication, reconstruction and WSPRadar analysis in the reference illustration. It uses 12-hour bins for the WSPRadar panel, while this demo’s current chronological chart uses 24-hour bins. Enlarge the figure to read the pairing-diagnostic reference.*

How do we verify WSPRadar’s results? One approach is to revisit published WSPR experiments, reconstruct their figures from historical observations, and compare the findings. This helps us validate our calculations, investigate discrepancies, and make the same analysis capabilities available to amateur-radio operators.

Here we compare Griffiths and Squibb’s original **Figure 3**, our reconstruction, and WSPRadar’s temporal analysis. The original dot plot contains many overlapping observations. The reconstruction adds a density representation to reveal where observations concentrate, while WSPRadar highlights the evolving median SNR difference and its variability. All three show the increasing advantage of G3ZIL during the first half of April.

Some details differ because multiple reports from the same transmission cycle can be combined differently. We document and investigate these discrepancies rather than forcing an exact match. This reference comparison concerns **paired SNR**; the new decoding analysis adds another perspective rather than claiming that the paper published the same ΔDecode result.

[**Original Figure 3, reconstruction and WSPRadar comparison (PDF, page 1) ↗**](/static/reference_figures/griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3.pdf)

The paired-SNR trend is now clear. Next, check whether the changing advantage also appears in the number of transmissions decoded.

<!-- section: evidence -->

## Read ΔDecode Temporal Coverage: do the extra decodes persist?

**The [earlier ΔDecode map](/en/demos/griffiths_squibb_fig3/#delta-decode-map) showed where the decoding advantage occurred; this view shows when it occurred.** The map grouped decode outcomes by direction and distance. The lower row here groups them by date and UTC hour within the selected Inspector scope. Keep **Full Range | All Directions** and **24h** for the daily examples below.

The SNR chart shows the differences on matched observations. **ΔDecode Temporal Coverage** follows both additional stations reached and additional observed decodes, including one-sided reception that cannot supply paired ΔSNR.

The **Station-level upper row** counts each exact callsign-plus-locator identity once within each time bin: **Both observed**, **Only Target**, or **Only Reference**. Both observed means each receiver heard that station at least once in the bin, even in different WSPR cycles. Repeated decodes of one transmitter cannot increase its station count. This measures additional stations relative to the other receiver in that interval, not first-ever discoveries.

The **Spot-level lower row** counts individual transmitter-cycle events. Here, **Both (Joint)** requires the same transmitter in the same WSPR cycle; one green category includes all Joint observations, regardless of ΔSNR qualification. Target-only is magenta and Reference-only cyan. Station-level Both and Spot-level Joint therefore answer different questions.

The right-hand panels combine the same UTC hour across dates and display average counts.

**Read the lower ΔDecode line.** Add **Joint + G3ZIL-only** for G3ZIL’s total decodes and **Joint + G4HZX-only** for G4HZX’s. The line plots their normalized difference, with the **right-hand axis** expressing the same **× comparison** used on the map.

The upper **Station Reach Advantage** line applies the same signed normalization to the two distinct-station totals. In both rows, **up favors Target G3ZIL, down favors Reference G4HZX**, and **1× (0)** at the center means equal totals. A Target-side **2×** means twice as many distinct stations above, or twice as many decodes below. Neither is an unconditional receiver success rate or a “percentage won”; transmissions missed by both remain unknown. Equality also does not require identical station sets or identical decoded transmissions.

**Read the two rows together:** extra decodes can come from more frequent reception of already-observed stations as well as from hearing additional stations. This is the distinction introduced in [Decoding Reach](/en/demos/griffiths_squibb_fig3/#decoding-reach), now resolved by time.

<details class="case-evidence-details">

<summary>How the UTC-hour panels combine dates</summary>

<p>For stations, membership is classified separately on each date before averaging: a station heard only by G3ZIL on Monday and only by G4HZX on Tuesday does not become Both on either day. The lines use the summed side totals, not an average of daily ratios.</p>

</details>

#### The additional reception is not confined to one day

**G3ZIL-only observations outnumber G4HZX-only observations on all 30 days.** Adding the same Joint count to both sides means G3ZIL also recorded more total decodes on every day. The changing paired SNR has a complementary decoding pattern:

| UTC date | Joint Spots | G3ZIL-only | G4HZX-only | G3ZIL decode advantage | Median paired ΔSNR |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **1 April** | **1 557** | **1 017** | **747** | **1.12×** | **+2 dB** |
| **15 April** | **1 905** | **2 159** | **250** | **1.89×** | **+9 dB** |
| **20 April** | **860** | **1 631** | **150** | **2.47×** | **+6 dB** |

Between the first and middle of April, the paired-SNR advantage rises and the one-sided imbalance widens. This is a complementary description of the observed change, not proof that SNR alone caused the difference. Day-to-day transmitter activity, paths and reporting still affect the totals.

Every day has matched evidence from **70 to 172 transmitting-station entries**, but not equally many observations: the total ranges from **860 Joint Spots on 20 April** to **2 903 on 11 April**. The UTC-hour panels also show less paired evidence in the early hours than in the late afternoon and evening. Those station counts refer specifically to same-cycle Joint evidence; the upper row’s **Both observed** category also includes stations heard on different cycles.

#### A sparse SNR day can still contain substantial reception evidence

On **20 April**, most observed transmitter-cycles were one-sided, so the smaller Joint sample does not mean little reception took place. G3ZIL’s decode advantage was greater than on **15 April**, despite a smaller paired-SNR advantage. **The two measures need not move together:** ΔSNR describes the shared transmissions, while ΔDecode also includes reception that only one setup reported.

<details class="case-evidence-details">

<summary>Space-weather context</summary>

<p>NOAA reported <strong>G2 (moderate) geomagnetic storm conditions at 04:33 UTC on 20 April</strong>, associated with coronal-hole effects. This may be relevant context for the sparse paired reception, but the coincidence does not establish causation. In this export, 22 and 23 April have <strong>1 312 and 2 002 Joint Spots</strong>, respectively—more than 20 April. Establishing how geomagnetic disturbance affected individual paths requires more than comparing daily spot counts. <a href="https://www.spaceweather.gov/news/g2-moderate-geomagnetic-storm-conditions-met">NOAA’s original 20 April report</a></p>

</details>

**Reference-only reports remain included even in cycles with no Target reports.** This symmetry is essential for reading both sides, but missing reports can still reflect operation or reporting differences as well as reception. **For a first reading, check both how many comparisons support a striking SNR feature and what the one-sided observations add.**

<!-- section: stations -->

## Open Station Insights: do individual paths agree?

The **Station Insights** table lets you move from the maps and Inspector’s summaries across many paths to a particular transmitter. Select **DJ0ABR at JN68nt**, already prepared in the demo. **Selected Station Evidence** now follows one transmitter path, rather than pooling transmitters from many locations.

Use **12h** for the selected-station charts below; the Inspector uses its separate **24h** setting. DJ0ABR lets us check the month’s broad SNR change on one path, then compare signal margin with additional decodes.

Leave **Filter by selected segment and distance** off to browse stations across the full analysis scope. Enable **Include one-sided evidence** when you also want to list stations without Joint evidence. The segment-and-distance filter restricts only the station list. Moving the Inspector or hiding DJ0ABR through that filter does not change its full-run evidence or silently select another station; the page indicates when the selected station lies outside the current list filter.

The three subsections follow the same two metrics down to their supporting observations:

- **DJ0ABR (JN68nt) ΔSNR Temporal Coverage**
- **DJ0ABR (JN68nt) ΔDecode Temporal Coverage**
- **DJ0ABR (JN68nt) Drill-Down Data**

Both selected-station figures retain **RX Benchmark** and **G3ZIL (Target) vs. G4HZX (Reference)** in their main title. The subtitle **Selected TX: DJ0ABR (JN68nt)** identifies the transmitter path; the footer records the analysis scope and relevant parameters.

Looking at ΔSNR, the overall median is **+5 dB**, based on **2 334 Joint Spots**. The 12-hour medians fluctuate around zero or below during parts of the first few days, then generally become more positive, often around **+5 to +8 dB**. The broad early-to-later change therefore appears on this individual path as well as in the all-station view that we have discussed earlier.

The hourly profile on the right hand side differs from the all-station profile. That is informative: a summary across many paths need not describe every path’s daily behavior. Late-night observations are relatively sparse, consistent with a change in the reception conditions on this path.

#### The midnight example: nearly equal paired SNR, very different reception

Read the **00:00–01:00 UTC** bin in the right-hand panels, pooled across April:

| DJ0ABR evidence in this UTC hour | Result |
| :--- | ---: |
| Joint observations | **14** |
| Median paired ΔSNR | **−0.5 dB** |
| G3ZIL-only observations | **38** |
| G4HZX-only observations | **1** |

The paired median slightly favors G4HZX. But G3ZIL reported **52 of the 53 observed transmitter-cycles**, while G4HZX reported **15**: **3.47× as many decodes, a net 37 additional decodes**. This is the same comparison of total decodes used on the earlier ΔDecode map.

<details class="case-evidence-details">

<summary>Calculation detail</summary>

<p>For this single path and hour, ΔDecode is <strong>+55.2%</strong>: <strong>100 × (52 − 15) / (52 + 15)</strong>. This symmetric percentage uses the sum of both receivers’ totals; it is not a conventional percentage more than Reference.</p>

</details>

**This is why a near-zero paired SNR difference cannot describe the whole reception comparison.** The shared observations are only part of the evidence. Under common operation, the additional G3ZIL decodes show a practical reception advantage even though the paired median does not. They do not prove that every missing G4HZX report resulted from a threshold crossing.

For contrast, during **06:00–07:00 UTC**, the same path has **134 Joint observations, no one-sided observations, and a paired median of +5 dB**. Both receivers therefore recorded **134 decodes: 1×**, despite G3ZIL’s **+5 dB** paired-SNR advantage.

Here G3ZIL’s SNR advantage provides extra margin, but no extra observed decodes in that hour’s sample. **The value of an SNR advantage depends on the reception conditions in which it occurs.**

**For your own station:** check whether better SNR provides additional margin, more decoded transmissions, or both. The answer can change with the hour—even for the same transmitter.

#### 20 April: sparse reception on the G2 storm day

During **20 April, 12:00–24:00 UTC**, DJ0ABR supplies **just one Joint Spot and three Target-only observations**. That one pair at **17:56 UTC** sets the **+25 dB median**; it does not establish a sustained half-day advantage. The G2 storm discussed earlier provides context.

<!-- section: drill-down -->

## Use Drill-Down: follow one evening, cycle by cycle

With **DJ0ABR (JN68nt)** selected, inspect **18 April 2017 from 21:00 UTC**. One short sequence connects the SNR and decoding charts to their underlying observations.

The selected-station CSV contains the Joint comparisons. To inspect the two Target-only examples below, use the all-stations CSV in the results package or the linked source records.

| UTC       | G3ZIL SNR | G4HZX SNR | ΔSNR    | Outcome     |
| :-------- | --------: | --------: | ------: | :---------- |
| 21:00     | +6        | −3        | +9      | Joint       |
| 21:08     | +7        | −3        | +10     | Joint       |
| 21:36     | +6        | −1        | +7      | Joint       |
| 21:48     | +9        | −5        | +14     | Joint       |
| **21:56** | **+11**   | **−24**   | **+35** | **Joint**   |
| 22:00     | +8        | −1        | +9      | Joint       |
| 22:12     | +11       | +3        | +8      | Joint       |
| 22:20     | +12       | —         | —       | Target-only |
| 22:24     | +5        | —         | —       | Target-only |

*Selected observations; SNR values in dB on the common 1 W basis. Decoding Reach uses raw reported SNR. [Source records](https://db1.wspr.live/?query=SELECT%20id%2Ctime%2Cband%2Ccode%2Crx_sign%2Crx_loc%2Ctx_sign%2Ctx_loc%2Csnr%2Cpower%20FROM%20wspr.rx%20PREWHERE%20band%20%3D%207%20AND%20time%20%3E%3D%20%272017-04-18%2020%3A30%3A00%27%20AND%20time%20%3C%20%272017-04-19%2001%3A00%3A00%27%20WHERE%20rx_sign%20IN%20%28%27G3ZIL%27%2C%27G4HZX%27%29%20AND%20tx_sign%20%3D%20%27DJ0ABR%27%20ORDER%20BY%20time%2Cid%20LIMIT%2010000%20FORMAT%20CSVWithNames).*

**The +35 dB outlier at 21:56 reflects a brief dip in G4HZX’s reported SNR.** The following paired observations return close to the earlier differences.

**Later, paired ΔSNR disappears while decoding continues.** The Target-only rows still contribute to **ΔDecode**. A dash means no reported decode; the missing SNR is unknown.

Use **Zoom window** to focus the plots and table; **Filter table** changes only the displayed rows.

<!-- section: takeaways -->

## Download Evidence: state the result and preserve it

We can now answer the original station question with more than a single number:

> **During April 2017 on 40 m, G3ZIL’s installed receiving setup showed an overall station-balanced median SNR advantage of +6.5 dB over G4HZX, based on 57 767 same-cycle comparisons from 792 transmitting-station entries within 10 000 km. G3ZIL also reported 114 027 spots from 1 083 station entries, compared with 69 258 spots from 876 entries at G4HZX: 1.65× as many decodes, a net 44 769 additional Target decodes. Under comparable common operation and reporting, these observations support an advantage in both paired signal quality and additional observed decoding—but not on every path or at every time.**

Under **Download Evidence**, select **Prepare All Results for Download**, then **Download Prepared Results**, to preserve the configuration, figures and processed observations in the **results package**. **Save Config** separately preserves the reusable analysis settings, so does Share Analysis encoding the settings into the URL. For your own experiments, keep station notes alongside it so a later comparison includes what was physically connected, when both setups were operating and what changed.

[**Run this comparison in WSPRadar ↗**]({{demo_launch_url}})
