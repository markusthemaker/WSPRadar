# WSPRadar.org

HAM RADIO STATION & ANTENNA BENCHMARKING

<a id="sec-1"></a>
### 1. Why WSPRadar

<a id="sec-1-0"></a>
#### 1.0 Why WSPRadar is different

WSPR can tell you that a signal was heard. WSPRadar asks the more useful next question: **how did the station or setup I am testing perform against a meaningful reference under comparable conditions?**

Throughout this guide, the station or setup being evaluated is called the **Target**. WSPRadar can examine that Target on its own, compare two local hardware paths, compare it with a known reference station, or compare it with active stations in its local WSPR neighborhood.

WSPRadar goes beyond a spot map or a station score. Its distinctive power comes from combining several capabilities in one operator workflow:

* **TX and RX analysis:** investigate where your transmitted signal is decoded and which independently confirmed signals your receiver decodes.
* **Purpose-built experiment designs:** choose Hardware A/B, a Reference Station / Buddy Test, a Local Neighborhood benchmark, or Success without a benchmark.
* **Comparable evidence:** pair Target and Reference observations in the same WSPR cycle, or in controlled time bins for sequential TX A/B.
* **Two views of performance:** separate paired signal-strength difference from decode/no-decode outcomes instead of forcing both into one score.
* **Stations and Spots:** see both the geographic breadth of participating station identities and the volume of qualifying observations.
* **Evidence you can inspect:** move from map, to segment, to station, to the rows behind the result, then export the current analysis package.

That combination turns "I received more spots" into a stronger and more useful statement about **what happened, where it happened, against what reference, and under which conditions**.

WSPRadar remains a real-world observational tool. It is not a calibrated antenna range or receiver test set, and it does not isolate antenna gain, efficiency or receiver sensitivity from the rest of the station system. Its value is different: it makes WSPR-based station experiments substantially more controlled, transparent and reproducible.

<a id="sec-1-1"></a>
#### 1.1 WSPR in two minutes

**WSPR** stands for **Weak Signal Propagation Reporter**. It is a narrow-band digital protocol used by radio amateurs to probe propagation with low-power transmissions. A normal WSPR-2 transmission lasts about 110.6 seconds, starts two seconds into an even UTC minute and occupies about 6 Hz. Its message normally contains a callsign, a four-character Maidenhead locator and reported transmitter power in dBm. Depending on decoder and conditions, reception is commonly quoted at roughly `-27 to -31 dB` SNR on the 2500 Hz WSJT reference scale. <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a>

A receiving station decodes as many WSPR signals as it can and, when reporting is enabled, uploads each successful decode as a **spot**. A spot records the transmitter and receiver identities, their reported locators, time, band, reported power and decoder-reported Signal-to-Noise Ratio (SNR). WSPRadar reads the historical spot record through wspr.live. <a href="#ref-3">[Ref-3]</a>

One limitation matters immediately: the database records successful decodes, not every attempted transmission and every failed reception. A missing spot can mean no transmission, no decode, no upload, an incorrect identity, an unavailable service or a closed path. WSPRadar therefore builds explicit activity and comparison rules; it never assumes that every missing spot is a radio failure.

<a id="sec-1-2"></a>
#### 1.2 What you can learn about your station

WSPRadar is designed around practical amateur-radio questions:

* Where is my transmitter being decoded, and by which active receivers?
* Which signals confirmed elsewhere does my receiver also decode?
* Did antenna or receive path A outperform path B at my station?
* How does my station compare with a known buddy on the same band?
* Am I broadly typical for active WSPR stations near my QTH?
* Can I match the strongest active local station?
* Is an advantage concentrated in particular directions, distances or times?
* Am I an "alligator": heard well but hearing poorly?

The last question requires comparable TX and RX runs against the same benchmark concept. Even then, treat the difference as station-system evidence: TX and RX use different peer populations and opportunity rules.

<a id="sec-1-3"></a>
#### 1.3 What one WSPRadar run produces

Before running an analysis, choose:

* **Direction:** TX if the Target is transmitting; RX if the Target is receiving.
* **Benchmark Design:** no benchmark, local Hardware A/B, one Reference Station, or a Local Neighborhood.

The choices determine the result blocks:

* **Success** is the Target-only operating result. It reports a conditional Success Rate against qualifying activity across the WSPR network. It is not a benchmark score.
* **Compare** is added when a benchmark is selected. It reports the paired SNR difference between Target and Reference together with **Decode Outcomes** for joint and one-sided evidence.

The thing compared with the Target is the **Reference**. Depending on the design, that can be Setup B, one buddy callsign, a cycle-level local median, or the strongest active local peer.

A **peer** is a remote station identity supplying evidence. WSPRadar treats one exact `callsign + reported locator` pair as one peer identity.

You first see a geographic map. From there, the Segment Inspector lets you inspect a selected distance/direction scope, Station Insights lists the contributing identities, and Drill-Down exposes the underlying observations, pairs or time bins.

<a id="documentation-toc"></a>
### Table of Contents

* [1. Why WSPRadar](#sec-1)
* [2. Five-Minute Quick Start](#sec-2)
* [3. Choose and Design Your Analysis](#sec-3)
  * [3.1 Choose TX or RX](#sec-3-1)
  * [3.2 No benchmark: Success only](#sec-3-2)
  * [3.3 Hardware A/B](#sec-3-3)
  * [3.4 Reference Station / Buddy Test](#sec-3-4)
  * [3.5 Local Neighborhood Benchmark](#sec-3-5)
  * [3.6 Pre-run experiment checklist](#sec-3-6)
* [4. Read Your Results](#sec-4)
* [5. Controls and Configuration](#sec-5)
* [6. Troubleshooting and Data Quality](#sec-6)
* [7. Scientific Methods](#sec-7)
* [8. Limits, Valid Claims and Reproducibility](#sec-8)
* [Appendix A: Parallel WSJT-X Instances](#sec-a)
* [Appendix B: Timed A/B Relay Switch](#sec-b)
* [Appendix C: Reference SNR Calibration](#sec-c)
* [Appendix D: Literature, Prior Art and Positioning](#sec-d)
* [References](#sec-ref)

<a id="sec-2"></a>
### 2. Five-Minute Quick Start

The safest first run uses a maintained historical demo. This lets you learn the UI before designing your own experiment.

1. Click `Load Demo`.
2. Select a demo whose title matches a question you want to explore.
3. Click `Run Selected Demo`.
4. Check the result titles. A benchmark demo normally produces a **Compare** result and a separate **Success** result.
5. Read the map at a glance:
   * Map color shows the segment result.
   * `STATIONS` shows how the participating station identities are distributed.
   * `SPOTS` shows how the qualifying observation volume is distributed.
6. Open `Segment Inspector` and select a distance range and direction.
7. Read the segment summary. For Compare, it reports factual counts such as `Selected Segment Evidence: 4 joint stations | 17 joint spots`.
8. Select one Station Insights row and inspect the selected-station evidence and Drill-Down rows.
9. Use `Prepare All Results for Download` when you want the current configuration, metadata, processed evidence, tables and high-resolution figures.

Do not decide that an antenna "won" from map color alone. First confirm the result type, station count, spot/bin count, Decode Outcomes, time window and selected geographic scope.

**A defensible first Compare statement**

> For this Target, benchmark, band, UTC window and selected segment, the paired station-median SNR difference favored the Target/Reference by the displayed amount. The joint station and spot counts state how much paired evidence contributed, while Decode Outcomes show the one-sided evidence outside that paired subset.

**A defensible first Success statement**

> For this Target, band, UTC window and selected peer population, the displayed Success Rate describes the fraction of independently confirmed opportunities in which the Target also produced qualifying evidence. It is a conditional network indicator, not an unconditional decode probability or a score expected to reach 100%.

Before running your own callsign, choose the experiment in [Section 3](#sec-3). A correct sequence of button clicks cannot repair an uncontrolled test.

<a id="sec-3"></a>
### 3. Choose and Design Your Analysis

This chapter is the single home for analysis selection and experiment design. Shared calculations are defined later in [Scientific Methods](#sec-7).

| Your question | Benchmark Design | Essential requirement |
|---|---|---|
| Where am I heard, or which confirmed signals do I hear? | `No benchmark (Success only)` | Correct Target identity, band and active time window. |
| Did local Setup A differ from Setup B? | `Hardware A/B-Test (Local Setup)` | Hold every non-tested variable stable. |
| How do I compare with one known station? | `Reference Station (Buddy Test)` | Overlapping operation and enough shared remote peers. |
| Am I typical for nearby active WSPR stations? | `Local Neighborhood Benchmark` with Local Median | A meaningful radius and enough active local stations. |
| Can I match the strongest active local peer? | `Local Neighborhood Benchmark` with Local Best | Treat the reference as a changing best-peer envelope. |

<a id="sec-3-1"></a>
#### 3.1 Choose TX or RX

Choose **TX** when the Target callsign is the transmitting station or Setup A transmit path. Remote receiving stations become the mapped peers.

Choose **RX** when the Target callsign is the receiving station or Setup A receive chain. Remote transmitting stations become the mapped peers.

Every run requires one exact band. Combining bands would mix different propagation, station populations, activity and observability into one result.

<a id="sec-3-2"></a>
#### 3.2 No benchmark: Success only

**Use this when:** you want to understand the Target's TX reach or RX reach without comparing it with another station or setup.

**Set it up:** enter the exact Target callsign, QTH, one band and a time window in which the Target was operating. Select `No benchmark (Success only)`, then run TX or RX.

**You get:** one TX Success or RX Success result. Comparison-only inputs disappear and no Compare query is built.

**What it means:** Success is a conditional, propagation-weighted network-reach indicator built from qualifying global WSPR activity. It is not a Target-versus-reference score. [Section 4.2](#sec-4-2) explains how to interpret the percentage.

**Watch for:** do not judge equipment from the percentage alone. Check geographic scope, evidence counts and consistency across time.

<a id="sec-3-3"></a>
#### 3.3 Hardware A/B

**Use this when:** you want to test two local antennas, feedlines, receiver paths or other station configurations.

**Set it up for simultaneous RX:** run two receivers at the same time with different exact reporting callsigns. Setup A uses the Target Callsign; Setup B uses the Setup B Callsign. The current UI does not use separate Target/Reference locator controls for RX A/B. Keep clocks, antenna routing, gain, audio paths, decoder settings and uploads controlled.

**Set it up for sequential TX:** use one callsign and alternate complete WSPR transmissions between two paths:

* Target frames: UTC start minutes `00, 04, 08, ...`
* Reference frames: UTC start minutes `02, 06, 10, ...`

WSPRadar groups those transmissions into fixed 4, 8, 12, 16 or 20 minute bins. A deterministic scheduler or controller is required; normal randomized transmit-percentage behavior is not a fixed A/B schedule.

Use the station's normal exact callsign for both paths. Do not invent `/1` and `/2` suffixes to label Setup A and Setup B: the configured frame sequence identifies the two sides. Compound WSPR callsigns use different message formats; depending on the format, the locator can be omitted or the callsign represented by a hash. That can make identity and locator evidence less directly comparable across decoders and uploads. A suffix can also have regulatory meaning, so use one only when it is valid for the actual operation. <a href="#ref-2">[Ref-2]</a>

**Why TX A/B is sequential:** if two nearby antennas at one QTH radiate the same WSPR waveform and callsign in the same cycle and frequency channel, a remote receiver observes their combined field; its spot cannot be attributed to antenna A or antenna B. Making the simultaneous signals distinguishable normally requires separate callsigns and transmit chains. That adds transmitter calibration, power, timing and frequency differences, while closely spaced antennas and feed systems can mutually couple or inject RF into the other chain. Simultaneous local TX is therefore not physically impossible, but it is usually the wrong design for the controlled single-transmitter RF-path comparison WSPRadar intends.

Alternating complete neighboring WSPR frames keeps Setup A and Setup B observations only two minutes apart. With a balanced schedule over many hours or days, short-term propagation and receiver changes should repeatedly affect both sides and tend to average down, so the practical disadvantage of sequential rather than simultaneous TX should become small. It is not exactly zero: systematic frame-timing or switching effects can remain, and swapping the frame assignments is a useful control.

**You get:** a Hardware Compare result plus the Target's separate Success result. For sequential TX, Success is limited to the configured Target frame sequence and describes Setup A only.

**What it means:** simultaneous RX is the closest WSPRadar design to a controlled same-signal hardware comparison. Sequential TX reduces many equipment differences when one transmitter switches only the RF path, but the two sides are still observed at different times.

**Watch for:** shared hardware, splitter imbalance, switch loss, unequal feedlines, AGC behavior, clipping, clock error, incorrect frame polarity and any configuration change beyond the tested variable.

**Related appendices:** use [Appendix A](#sec-a) for parallel WSJT-X instances, [Appendix B](#sec-b) for WSPRadar's timed USB-relay helper, and [Appendix C](#sec-c) for Reference SNR calibration.

<a id="sec-3-4"></a>
#### 3.4 Reference Station / Buddy Test

**Use this when:** you want to compare your Target with one known external station.

**Set it up:** enter one exact Target callsign and one different exact Reference Callsign. Choose a station whose location, hardware, power and operating schedule you understand. Both sides need overlapping operation on the same band.

**You get:** a TX or RX Compare result against the buddy plus a separate Target Success result.

**What it means:** in TX, the same remote receiver compares Target and Reference where both were observed in the same cycle. In RX, Target and Reference receivers compare the same remote transmitter identity in the same cycle. This pairing reduces shared fading and endpoint differences, but it does not make two stations physically identical.

**Watch for:** different terrain, local noise, antennas, polarization, feedline loss, transmitter or receiver calibration, reported power and operating schedule. The Target-Active Gate is asymmetric, so swapping Target and Reference can change one-sided Decode Outcomes even when shared paired differences reverse sign.

<a id="sec-3-5"></a>
#### 3.5 Local Neighborhood Benchmark

**Use this when:** you want context from active WSPR stations around the configured QTH rather than one hand-picked reference.

**Set it up:** choose a radius from 10 to 250 km and select one of two methods:

* **Local Median Neighborhood:** the recommended starting point for "am I broadly typical for my area?"
* **Local Best Station:** a stricter test against the strongest active local reference for each cycle and path.

**You get:** a Local Compare result plus the Target's separate Success result.

**What it means:** Local Median gives every active local `callsign + locator` identity one reference contribution per cycle/path before taking the neighborhood median. A very active local station therefore does not receive one vote for every duplicate or repeated row. If a local station has no qualifying observation for that cycle/path, WSPRadar does not invent `0 dB`; that station simply contributes nothing to that reference pool. The Target is excluded from the local pool by exact callsign only, so a base callsign and a suffixed identity remain distinct. Local Best instead uses a changing best-peer envelope; it is not a local average.

**Watch for:** the reference pool changes as stations come and go. Local stations remain uncalibrated and may differ in antenna, terrain, noise, hardware and reported-power accuracy. A radius that is too large can stop representing a common local environment.

<a id="sec-3-6"></a>
#### 3.6 Pre-run experiment checklist

**Before collecting data**

* State the question and tested variable in one sentence.
* Choose TX or RX, one exact band and the benchmark design.
* Verify exact callsign forms, including any `/P`, `/1` or `/QRP` suffix.
* Verify the Target QTH. Success matches the Target callsign together with the first four locator characters.
* Choose a UTC window long enough for the propagation states covered by the claim. Multi-day runs are preferable for claims spanning complete daily cycles.
* Record antennas, feedlines, tuner, transmitter or receiver, decoder, software version, power, schedule and intentional changes.

**During the experiment**

* Keep every non-tested variable as stable as practical.
* Keep clocks synchronized.
* For TX, keep actual and reported power realistic and stable unless power is under test.
* For RX, keep gain, filtering, audio routing, decoder settings and upload behavior stable unless they are under test.
* Confirm that both benchmark sides operate as intended. The Target-Active Gate does not prove Reference uptime.

**Before accepting the result**

* Confirm title, Target, Reference, band, UTC window and filters.
* Inspect both `STATIONS` and `SPOTS`, not only map color.
* Check the selected segment's joint station and spot/bin counts.
* Inspect Decode Outcomes alongside paired SNR difference.
* Look for one identity, locator or short interval dominating the result.
* Repeat the experiment or swap paths when a small difference would support an important decision.
* Prepare the export package and preserve external setup notes WSPRadar cannot infer.

<a id="sec-4"></a>
### 4. Read Your Results

This chapter is the single home for interpreting the UI. The exact formulas and processing hierarchy are in [Scientific Methods](#sec-7).

<a id="sec-4-1"></a>
#### 4.1 Identify the result block

Start with the title:

* **TX Success / RX Success:** conditional Target reach against qualifying network activity.
* **TX Compare / RX Compare:** Target-versus-Reference evidence using paired SNR difference and Decode Outcomes.
* **Sequential TX A/B Compare:** a special Compare result whose paired unit is a fixed time bin rather than one WSPR cycle.

Do not compare colors from unlike result types. Also confirm the band, time window, benchmark design, callsigns, filters and evidence thresholds.

<a id="sec-4-2"></a>
#### 4.2 Understand Success Rate

Success Rate answers a practical but deliberately limited question:

* **RX Success:** of the peer transmitter-cycles independently confirmed by another receiver, how many did the Target receiver also decode?
* **TX Success:** of the active peer receiver-cycles confirmed by other same-band decodes, how many also decoded the Target transmitter?

WSPRadar uses four user-facing classifications:

* **Target:** the Target succeeded and independent confirmation also exists.
* **Elsewhere:** in RX, the transmitter was heard by another receiver but not by the Target.
* **Other Signals:** in TX, the receiver heard other same-band signals but not the Target.
* **Target-only:** the Target succeeded without the independent confirmation required by the denominator. It remains available for audit but does not enter Success Rate.

Example: if a remote transmitter was confirmed elsewhere in eight qualifying cycles and your receiver heard it in three, that peer's RX Success Rate is `3 of 8 = 37.5%`. If an active receiver produced ten qualifying cycles and heard your transmitter in four, its TX Success Rate is `4 of 10 = 40%`.

**Success Rate is not a score out of 100.** The candidate population is globally sourced:

* RX can grow toward the globally active transmitters on that band during cycles in which the Target receiver was active.
* TX can grow toward the globally active receivers on that band during Target transmit cycles.

Only peers surviving the selected time, band, filters and evidence thresholds contribute, and the displayed map scope can show a geographic subset. Even so, many paths will be difficult or unavailable. A lower percentage does not automatically indicate poor equipment.

A displayed 100% means the Target succeeded in every qualifying opportunity for that station or selected scope. It does not mean every possible or scheduled transmission was decoded.

Each peer rate is calculated first. A Success map segment then gives every qualifying peer identity equal weight and shows the arithmetic mean of those station rates. Segment Insight also shows the observation-level pooled rate, which gives every qualifying observation equal weight.

The Success Rate classification itself is not power-normalized. The successful Target SNR displayed beside it is normalized to reported 1 W.

<a id="sec-4-3"></a>
#### 4.3 Understand Compare

Compare separates two questions that a single score cannot answer well.

**Paired SNR difference** asks: when Target and Reference both produced comparable evidence, which side had the stronger SNR and by how much? The UI calls this difference **Delta SNR**. Positive values favor the Target; negative values favor the Reference. The formula appears once in [Section 7.5](#sec-7-5).

**Decode Outcomes** asks: what happened outside that paired subset?

* **Joint / Joint Spots / Joint Bins:** qualifying paired evidence exists.
* **Only Target:** Target evidence exists without Reference evidence in the relevant comparison unit.
* **Only Reference:** Reference evidence exists without Target evidence.
* **Both (Async):** both sides have evidence for the peer identity, but no qualifying joint unit survives for that category.

Paired Delta SNR is normally the primary quantitative comparison because both sides are observed under more comparable conditions. Decode Outcomes show whether one side also reached signals or paths absent from the paired subset.

The shared endpoint depends on direction. In simultaneous TX Compare, the same remote receiver measures Target and Reference, reducing receiver hardware, antenna, local-noise and reporting differences within the pair. In simultaneous RX Compare, Target and Reference receivers measure the same remote transmitter, reducing transmitter power, waveform and shared propagation-path differences. Same-cycle pairing reduces these confounders; it does not make separated stations or hardware chains physically identical.

In simultaneous comparisons, the Target-Active Gate protects Target downtime from being counted as failure, but it does not prove symmetric Reference uptime. Sequential TX A/B instead uses scheduled frames and paired time bins.

<a id="sec-4-4"></a>
#### 4.4 Read the map

**Median and arithmetic mean**

A **median** is the middle value after values are sorted, or the midpoint of the two central values when the count is even. Unlike the arithmetic mean, it is not pulled as strongly by one unusually high or low value. WSPRadar uses medians for paired SNR differences and local reference values where robustness matters; Success map segments use the arithmetic mean after giving each qualifying peer one equal vote. The two summaries answer different questions and are not interchangeable.

**Heatmap color**

* Compare segments show the median of qualifying station-level Delta-SNR medians. Positive favors Target; negative favors Reference. The comparison scale uses the amateur-radio display convention `1 S-unit = 6 dB`; this is a scale annotation, not a claim that every S-meter is calibrated.
* Success segments show the arithmetic mean of qualifying station Success Rates. The fixed nonlinear scale distinguishes no evidence, exactly `0%`, a positive value below `1%`, then `1, 2, 5, 10, 20, 40, 60, 80, 100%`.

**STATIONS and SPOTS**

Every current WSPRadar map uses two footer rows:

* `STATIONS` describes footprint breadth across distinct qualifying `callsign + locator` identities.
* `SPOTS` describes the volume of qualifying observations.

For Compare, both rows are divided into Only Target, Joint, Both (Async) and Only Reference. Station categories assign each identity to one main category. Spot categories count evidence volume, including exclusive observations associated with identities that also have joint evidence.

For Success, `SPOTS` divides qualifying denominator evidence into Target and Elsewhere for RX, or Target and Other Signals for TX. `STATIONS` divides qualifying identities into peers with at least one Target observation and peers with counter-evidence only. Target-only and ineligible evidence are excluded because they do not enter Success Rate.

The footer counts only evidence inside the visible map scope.

**Station markers**

* Success: green `T` markers have at least one confirmed Target observation. Grey `E` or `OS` markers are qualifying zero-Target peers with Elsewhere or Other-Signals evidence.
* Compare: green is Joint, yellow-orange is Both (Async), purple is Only Target and white is Only Reference.

**Distance rings**

Near rings can be consistent with shorter skip or NVIS behavior; far rings can be consistent with DX behavior. Distance is not a direct elevation-angle measurement.

<a id="sec-4-5"></a>
#### 4.5 Segment Insight

Select one or more distance ranges and compass directions to inspect the evidence behind that part of the map.

**Success Segment Insight**

**Target/counter summary and rates.** The Target and Elsewhere/Other-Signals counts show the observations entering the selected segment's Success denominator. **Average by Station** gives every qualifying peer one equal vote and is the map value. **Observation-Level** pools all observations, so a difference between the two means high-volume peers are pulling the pooled result away from the typical peer. Neither weighting is universally correct; they answer different questions.

**Station Success Rate by Evidence Count.** Each point is one station with Target evidence. The vertical position is its Success Rate; the horizontal base-2 log axis is its `Target + counter-evidence` count. Upper-right points combine high rate with repeated evidence, while left-side points need more caution because little evidence can create extreme percentages. Zero-Target stations are omitted because all would sit at `0%`; they remain in map counts, temporal evidence and Station Insights when `Show Zero-Target` is enabled.

**Success over time.** The station-balanced and Observation-Level panels show whether reach is sustained or concentrated in a short propagation window. Similar panels suggest that result volume is not changing the story; divergence suggests a few busy peers or intervals dominate the pooled rate. Empty cells mean no qualifying evidence, not a measured `0%`.

**Compare Segment Insight**

**Decode Outcomes.** The category view shows the breadth of Joint, Only Target, Both (Async) and Only Reference stations in the selected segment. Use it to check whether the paired Delta-SNR result describes most of the footprint or only a narrow joint subset. A strong paired median with substantial one-sided evidence still needs both stories reported.

**Station Medians (Delta SNR).** Each contributing station supplies one value: its median paired Delta SNR. The distribution therefore gives stations equal weight. A distribution concentrated above or below zero indicates a geographically consistent Target or Reference advantage; a wide or split distribution means the effect varies strongly by path and the overall median hides that variation.

**Joint-spot or paired-bin Delta SNR.** This distribution shows every consolidated same-cycle pair, or every valid paired bin in sequential TX A/B. It reveals raw spread, quantization and outliers, but active stations can contribute many values. Compare it with Station Medians: a large shift between them indicates that high-volume stations differ from the station-balanced picture.

**Median, Stability and evidence counts.** The median summarizes direction and typical size; the 90% Stability interval shows how much that median moves under resampling, not statistical significance. The factual count states the scale of paired evidence, for example:

`Selected Segment Evidence: 4 joint stations | 17 joint spots`

Sequential TX A/B uses `paired spot bins` instead of `joint spots`.

The UI term `Joint Spot` refers to a consolidated same-cycle comparison unit, not necessarily one untouched database row.

<a id="sec-4-6"></a>
#### 4.6 Station Insights and Drill-Down

`Station Insights` lists the identities contributing to the selected scope.

* Success rows show Target, Elsewhere or Other Signals, Success Rate and median successful Target SNR normalized to 1 W. Qualified zero-Target rows are hidden by default and can be restored with `Show Zero-Target`.
* Compare rows show joint and exclusive evidence plus the station-level median Delta SNR. `Show Non-Joint` restores identities without qualifying paired evidence.
* Missing SNR is shown as `None`, not `0.0 dB`.
* If no row is selected, the first evidence-sorted row is selected by default.

**How to read the table.** In Success, read rate together with Target/counter count: a high rate with little evidence is less persuasive than a similar rate repeated many times. The normalized Target SNR describes successful decodes only and does not enter the rate. In Compare, look for agreement in Delta-SNR direction across several stations and check joint versus exclusive counts; one high-volume or unusual path should not silently define the conclusion.

Selecting one or more rows opens a selected-station evidence view:

**Selected Success evidence.** The time panel plots station Success Rate with Target/counter counts, split by night, greyline/mixed and daylight path classes. Use it to see whether a result persists across illumination states or comes from one short opening. The successful Target-SNR distribution shows the strength of decoded Target evidence normalized to 1 W; it does not describe missed opportunities or isolated antenna gain.

**Selected Compare evidence.** The distribution shows the center, spread and possible clusters of the selected Delta-SNR evidence. The UTC heatmap shows whether that distribution stays stable or moves with time. Sequential TX A/B uses paired-bin Delta SNR. Median markers in neighboring time bins are connected only when both bins contain at least three values; isolated markers therefore indicate sparse evidence, not necessarily a physical discontinuity.

The available time bins adapt to the selected date span, from minute-scale bins for short runs to 24-hour bins for long runs. This control changes only the selected evidence view, not map aggregation, opportunity classification or pairing.

`Drill-Down` is the row-level audit surface:

* Success exposes target-active peer-cycle classifications, including Target-only.
* Simultaneous Compare exposes same-cycle Target/Reference evidence and Delta SNR.
* Local Median expands the local reference identities behind the cycle median.
* Sequential TX A/B exposes time bin, `Micro-Med A`, `Micro-Med B` and bin Delta.

**How to use Drill-Down.** Use these rows to reconcile a surprising station or segment value, identify locator changes or isolated outliers, and confirm which observations were paired or excluded. Drill-Down is the audit trail behind the summaries, not a separate performance metric.

<a id="sec-4-7"></a>
#### 4.7 Stability and evidence adequacy

`90% Stability` is a descriptive bootstrap interval around a median. A narrow interval means the displayed median changes little when the available values are resampled. It does not prove independence, eliminate data bias or establish statistical significance.

Judge evidence adequacy from the complete picture:

* joint station count;
* joint spot or paired-bin count;
* consistency across stations, time and adjacent geographic segments;
* Decode Outcomes;
* identity and data quality;
* experiment control and replication.

There is deliberately no automatic proof grade.

<a id="sec-5"></a>
### 5. Controls and Configuration

This chapter owns defaults, applicability and side effects. Scientific formulas are not repeated here.

<a id="sec-5-1"></a>
#### 5.1 Workflow controls

| Control | Purpose |
|---|---|
| `Load Demo` | Opens maintained historical profiles. Load the configuration for inspection or run it immediately. |
| `Load Config` | Validates and loads a saved JSON-based `.config` file. Invalid identities, dates, choices and ranges are rejected. |
| `Save Config` | Downloads current inputs. It does not contain result data or external experiment notes. |
| `Run TX Analysis` | Runs TX Success and, when selected, TX Compare. |
| `Run RX Analysis` | Runs RX Success and, when selected, RX Compare. |
| `Prepare All Results for Download` | Builds the current analysis export package on demand. |
| `Load full documentation` / `Hide full documentation` | The landing page initially sends only Section 1. When Section 1.3 enters the viewport, the table of contents and remaining manual load automatically at most once per session while you finish Section 1.3; this full-width button is the explicit fallback and can also hide the loaded content. Starting an analysis suppresses scroll-triggered loading. |
| `Prepare PDF` | Builds the complete selected-language manual as a process-cached PDF on demand; opening the full web manual is not required. |

<a id="sec-5-2"></a>
#### 5.2 Core controls

| UI label | Factory default | Scientific effect |
|---|---|---|
| **Your Callsign (Target under Test)** | blank | Exact Target identity. Accepted syntax is 3 to 15 characters from `A-Z`, `0-9` and `/`. |
| **QTH Locator (4-6 Chars)** | blank | Map center and local-radius origin. Success also uses the first four characters to match Target identity. |
| **Operating Band** | `20m` | Exactly one of `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` or `23cm`. |
| **Time Selection** | `Last X Hours` | Recent or custom UTC evidence. Recent mode allows 1 to 168 hours and defaults to 24. |
| **Custom dates/times** | previous day to current day | Custom windows are limited to 31 days and dates from 2008 onward. Endpoints are quantized down to 15-minute boundaries. |

Use the callsign exactly as uploaded. `DL1MKS`, `DL1MKS/P`, `DL1MKS/1` and `DL1MKS/QRP` are separate identities; WSPRadar does not apply hidden prefix matching.

A Maidenhead locator is a compact grid-square location code. Four characters identify a broad area; six characters identify a smaller area inside it. WSPRadar uses the configured QTH as the map center and local-radius origin, while Success matches the Target using its first four locator characters.

<a id="sec-5-3"></a>
#### 5.3 Benchmark controls

| UI label | Default | Applies to | Effect |
|---|---|---|---|
| **Benchmark Design** | `No benchmark (Success only)` | run composition | Success-only skips Compare. Other choices add Compare to Success. |
| **Reference SNR Correction (dB)** | `0.0` | Compare | Added to the Reference-side SNR before Delta SNR. Hidden for Success-only. |
| **Reference Callsign** | `DL2XYZ` example | Buddy | Replace with one exact callsign different from Target. |
| **Local Benchmark Method** | `Local Median Neighborhood` | Local | Selects neighborhood median or strict Local Best. |
| **Neighborhood Radius (km)** | `100` | Local | Includes local Reference coordinates from 10 to 250 km around QTH. |
| **A/B-Test Setup** | simultaneous RX | Hardware A/B | Selects two-receiver RX or one-transmitter time-sliced TX. |
| **Setup B Callsign** | blank | RX Hardware A/B | One exact callsign different from Setup A. |
| **Target WSPR Frame** | `00, 04, 08, ...` | TX Hardware A/B | Target / Setup A frame starts. |
| **Reference WSPR Frame** | `02, 06, 10, ...` | TX Hardware A/B | Reference / Setup B frame starts. |
| **Time Window (Bins)** | `8 min` | TX Hardware A/B | Fixed 4 to 20 minute pairing bin in 4-minute steps. |

Comparison-specific values remain in session state and saved configuration when Success-only is selected. They reappear if you select a benchmark again, but they do not alter the Success-only query or result.

**Reference SNR Correction sign**

A positive correction makes the corrected Reference SNR stronger and therefore reduces Target-minus-Reference Delta SNR. Enter a measured `target - reference` calibration offset with the same sign: a common-input calibration of `+1.6 dB` is entered as `+1.6 dB`. The exact equations appear in [Section 7.5](#sec-7-5).

The correction applies to Setup B / the Reference frame in Hardware A/B, the buddy callsign in Buddy, the selected local value in Local Best and every local contribution before Local Median aggregation.

A constant correction cannot repair clipping, unstable AGC, intermittent routing, frequency-dependent response or incorrect power reports. [Appendix C](#sec-c) describes calibration.

<a id="sec-5-4"></a>
#### 5.4 Filters and thresholds

| UI label | Default | Applies to | Exact effect |
|---|---|---|---|
| **Exclude Special Callsigns Q, 0, 1** | off | all results | Excludes qualifying peer identities beginning with `Q`, `0` or `1`. |
| **Exclude Moving Stations** | off | mapped peers | Removes a peer callsign reporting more than one four-character locator after other filters. |
| **Local QTH Solar State** | `All 24h` | all results | Keeps cycles classified at Target QTH as day (`>+6 deg`), night (`<-6 deg`) or greyline. |
| **Map Scope (Max Distance km)** | `22000` | map/inspection | Sets visible and inspectable radial scope; it does not narrow the upstream query. |
| **Min. Joint Spots per Station** | `1` | simultaneous Compare | Requires this many joint peer-cycles before a station contributes paired Delta SNR. |
| **Min. Joint Bins** | `1` | sequential TX A/B | Requires this many paired bins before a station contributes paired Delta SNR. |
| **Min. Target+Counter-Evidence per Station** | `5` | Success | Requires this many Target+Elsewhere RX or Target+Other Signals TX observations. |
| **Min. Qualifying Stations per Map Segment** | `1` | all maps | Requires this many qualifying identities before a segment is drawn. |

The Compare joint threshold also suppresses exclusive categories whose own count is below the same numeric cutoff. In sequential TX A/B, paired eligibility is counted in bins while exclusive evidence is counted in spots and compared with that numeric cutoff.

Lowering **Min. Target+Counter-Evidence per Station** increases map coverage but also makes station rates more discrete and fragile. With one or two qualifying opportunities, values such as `0%`, `50%` or `100%` can reflect very little evidence. Read the count beside the rate and prefer replication before acting on a small sample.

Use **Exclude Special Callsigns Q, 0, 1** according to the question rather than enabling it automatically:

* In RX Compare, beacon-like or telemetry-style transmitters can be valuable weak same-cycle signals seen by both receivers.
* In RX Success, retain them when beacon reception is part of the question; exclude them when the intended population is ordinary amateur-station activity.
* In TX analysis, the filter applies to receiver-side peer identities. Use it only when those identities are distorting the intended receiver population.

State the choice in serious reports.

<a id="sec-5-5"></a>
#### 5.5 Map, inspector and export controls

* Segment range and direction selectors change inspected scope, not the completed analysis.
* `Show Zero-Target` restores qualifying Success identities with zero Target confirmations.
* `Show Non-Joint` restores Compare identities represented only by exclusive/asynchronous evidence.
* Station selection changes selected-station figures and selected Drill-Down.
* The selected-station time-bin control changes only the selected timeline.
* Empty Success time bins remain blank; they are not converted to zero-rate evidence.
* `Prepare All Results for Download` exports the current result and inspector selections. Package contents are documented in [Section 8.4](#sec-8-4).

<a id="sec-6"></a>
### 6. Troubleshooting and Data Quality

<a id="sec-6-1"></a>
#### 6.1 Common symptoms

| Symptom | Check first |
|---|---|
| No result or no Target evidence | Exact callsign including suffix, Target QTH grid-4, band, UTC window and actual Target operation. |
| Compare has no Delta SNR | Shared peer identities, overlapping cycles, joint threshold, clocks and Reference operation. |
| Success map has few peers | Target+counter threshold, short timeframe, filters and availability of independent confirmation. |
| Many Target-only Success rows | Independent confirmation is absent; these rows do not enter Success Rate. |
| `Only Reference = 0` | This can be correct after Target-Active gating, thresholds and scope selection. |
| A/B result has unexpected sign | Setup/path mapping, frame polarity, correction sign, actual power and Target/Reference order. |
| Local result changes with radius | The active local Reference pool changed; inspect its contributors. |
| Old config with `band=All` is rejected | Choose one exact band; automatic conversion would change the scientific question. |
| Recent spots appear incomplete | Allow about five minutes after the latest cycle, then check reporting and upstream status; see [Section 6.5](#sec-6-5). |

<a id="sec-6-2"></a>
#### 6.2 Callsign and locator problems

Compare callsigns are matched exactly. Success Target matching is stricter: exact callsign plus the configured QTH's first four characters. A Target uploading `JN37` while the configuration says `JN38` will not satisfy the Success Target condition.

Peer identities use exact callsign plus the full reported locator string. Bad, stale or changing locators can split one physical station, move it into the wrong segment or trigger the moving-station filter.

<a id="sec-6-3"></a>
#### 6.3 Historical decode-code fallback

WSPRadar first requests rows using wspr.live `code = 1` for WSPR-2 evidence. If the strict query returns no Target-side evidence, it retries without that predicate for historical compatibility and reports the fallback in run status.

The fallback broadens selection. Current export metadata does not preserve which variant was used, so record the visible fallback message when it matters.

<a id="sec-6-4"></a>
#### 6.4 Target-Active Gate warnings

The gate is intentionally Target-centric. It confirms Target participation, excludes Reference evidence outside those cycles and protects known Target downtime from becoming automatic failure. It does not prove Reference uptime or that every radio path was open.

For example, if the Target station is shut down overnight, Reference spots from those offline hours are not counted as defeats. This is the practical reason for the gate. It still cannot tell whether the Reference was continuously operating during every retained Target-active cycle.

Swapping Target and Reference can therefore change eligible cycles and Decode Outcomes. Sequential TX A/B does not use the same simultaneous gate.

<a id="sec-6-5"></a>
#### 6.5 Upstream-data warnings

wspr.live states that its data is raw WSPRnet-reported data and may contain duplicates, false spots and other errors. Its volunteer infrastructure provides no guarantee of correctness, availability or stability. <a href="#ref-3">[Ref-3]</a>

wspr.live describes its real-time data as available with a delay of a few minutes and says its scraper checks for new spots every few minutes. As a practical operating estimate, wait about **five minutes** after the final WSPR cycle before expecting a fresh analysis window to be reasonably populated. Five minutes is not a completeness guarantee: delayed uploads, ingestion interruptions and later corrections can appear after that. <a href="#ref-3">[Ref-3]</a>

WSPRadar uses pairing, identity grouping, medians, thresholds and Drill-Down to reduce sensitivity to isolated bad rows. These controls do not make repeated plausible errors disappear.

Reported power and locators are user-supplied. Correct mathematics applied to an incorrect power or locator remains physically wrong.

<a id="sec-7"></a>
### 7. Scientific Methods

This chapter is the authoritative home for formulas, matching rules and aggregation. Operators can use the earlier chapters without reading every implementation detail; scientifically serious reporting should use both.

<a id="sec-7-1"></a>
#### 7.1 Data source and time model

WSPRadar reads the public `wspr.rx` table through the read-only wspr.live HTTP interface. Spots are observational records from independently operated transmitters, receivers, software and networks. They are not a randomized or calibrated sample of possible paths.

Selected endpoints are quantized down to 15-minute boundaries for query reuse. Success queries use a half-open interval, `start <= time < end`. Compare queries currently use database `BETWEEN` and include an observation exactly at the end timestamp. A boundary cycle can therefore appear in Compare but not Success.

A **WSPR cycle** is the two-minute interval aligned to an even UTC minute. WSPRadar derives simultaneous cycles from spot timestamps. Sequential TX A/B instead retains timestamps and assigns frame evidence to fixed wall-clock bins.

<a id="sec-7-2"></a>
#### 7.2 Identity and matching rules

| Analysis | Target matching | Peer / Reference identity | Lowest result unit |
|---|---|---|---|
| RX Success | exact RX callsign plus Target QTH grid-4 | TX callsign + reported TX locator | one Target-active peer-cycle |
| TX Success | exact TX callsign plus Target QTH grid-4 | RX callsign + reported RX locator | one Target-active peer-cycle |
| Simultaneous Compare | exact Target and Reference callsigns | remote callsign + reported locator | one consolidated peer-cycle |
| Sequential TX A/B | exact Target callsign split by WSPR frame | RX callsign + reported locator | one fixed time bin |
| Local Reference pool | exact local callsign + locator inside radius | remote peer as above | one local-identity contribution per cycle/path |

Multiple qualifying rows for one side of a normal simultaneous peer-cycle are consolidated; the maximum normalized SNR represents that side. Local Median instead takes a within-local-identity median and then a median across local identities.

<a id="sec-7-3"></a>
#### 7.3 Target-Active Gate

Success and simultaneous Compare keep evidence only in Target-active cycles:

* **TX:** at least one qualifying Target transmission spot exists somewhere in the cycle.
* **RX:** at least one qualifying decode uploaded by the Target receiver exists in the cycle.

Reference evidence outside those cycles is excluded. This reduces offline bias but creates a Target-centric estimand; there is no symmetric Reference-activity gate.

Joint Delta SNR still requires both sides for the same peer identity, which is stronger than the cycle gate. Decode Outcomes include one-sided evidence and need more cautious uptime interpretation.

Sequential TX A/B uses deterministic frame assignment and paired bins rather than this simultaneous gate.

<a id="sec-7-4"></a>
#### 7.4 Success classification and formulas

For each Target-active peer-cycle, WSPRadar records Target evidence and independent external evidence.

* **RX external evidence:** a different receiver reported the same transmitter identity in the same cycle.
* **TX external evidence:** the peer receiver reported a non-Target same-band transmitter in the same cycle.

Target requires both Target and external evidence. Elsewhere / Other Signals requires external evidence without Target. Target-only means Target evidence exists without external evidence and is excluded from the denominator.

$$\text{Success Rate}_{RX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Elsewhere}}$$

$$\text{Success Rate}_{TX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Other Signals}}$$

The eligible peer population is globally sourced after band, time, gate, filters and thresholds. Success Rate is therefore conditional on observable network activity and propagation, not an estimate of every attempted transmission or a calibrated receiver detection probability.

<a id="sec-7-5"></a>
#### 7.5 Power normalization, correction and Delta SNR

WSPR SNR is decoder-reported in dB on the WSJT scale, referenced to a 2500 Hz bandwidth. WSPR messages include reported transmit power in dBm. <a href="#ref-1">[Ref-1]</a>

WSPRadar normalizes successful SNR to a reported 1 W / 30 dBm reference:

$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$

This removes the **reported** power term. It does not correct antenna gain, efficiency, feedline loss, EIRP, receiver calibration or local noise.

Reference SNR Correction is added to the Reference side:

$$SNR_{reference,corrected} = SNR_{reference} + Correction$$

The general comparison definition is:

$$\Delta SNR = SNR_{target} - SNR_{reference,corrected}$$

A positive correction strengthens the Reference before subtraction and lowers Delta SNR. A negative correction raises Delta SNR.

TX comparisons use normalized SNR because different transmitted powers can be involved. In same-transmitter RX pairs, the common power term cancels. TX comparisons between different callsigns depend directly on reported-power accuracy.

<a id="sec-7-6"></a>
#### 7.6 Paired evidence and Decode Outcomes

Paired-only SNR analysis has survivorship bias: both sides must produce comparable evidence. A setup that adds many marginal decodes can have a lower pooled SNR median simply because it reaches weaker signals.

WSPRadar therefore keeps:

1. **Paired Delta SNR:** conditional signal-strength difference where both sides produced comparable evidence.
2. **Decode Outcomes:** Joint, Only Target, Only Reference and Both (Async) evidence outside or around that paired subset.

Decode Outcomes are not power-normalized. An exclusive TX observation has no missing-side SNR to reconstruct. Unequal transmit powers can therefore dominate exclusive TX evidence even when joint Delta SNR is normalized.

Compare map `STATIONS` categories assign identities; `SPOTS` categories count evidence volume. Success map bars use the same two levels but align them with the Success denominator.

<a id="sec-7-7"></a>
#### 7.7 Aggregation hierarchy

Medians reduce sensitivity to isolated extreme values, duplicate-like bursts and quantized SNR outliers, but they do not remove systematic calibration error, propagation bias or correlation across time and stations. Calculating a peer-level value before the segment value is also a weighting decision: each qualifying peer contributes once, so a high-volume station cannot dominate only because it uploaded more observations.

**Success**

1. Classify each Target-active peer-cycle.
2. Sum Target, counter-evidence and Target-only by peer `callsign + locator`.
3. Require the configured Target+counter threshold.
4. Calculate one Success Rate per qualifying peer.
5. Calculate the segment arithmetic mean of peer rates.
6. Retain the pooled observation-level rate as a diagnostic.

**Simultaneous Compare**

1. Consolidate Target and Reference evidence by cycle and peer identity.
2. Calculate Delta SNR for joint cycles.
3. Require the configured joint count for each peer.
4. Calculate one station-level median Delta SNR.
5. Calculate the segment median across station medians.

**Sequential TX A/B**

1. Assign spots to Target and Reference frame sequences.
2. Group each side by time bin and peer identity.
3. Calculate one micro-median per side and bin.
4. Calculate bin Delta where both micro-medians exist.
5. Require the configured paired-bin count.
6. Calculate station and segment medians.

**Local Median Reference**

1. Group each local Reference `callsign + locator` within cycle and remote peer.
2. Calculate that local identity's median normalized SNR.
3. Take the exact inclusive midpoint median across local identities.
4. Compare Target with that cycle-level Reference.

With an even local pool, the midpoint of the two central values is used. The pool can change every cycle.

<a id="sec-7-8"></a>
#### 7.8 Stability and histogram construction

WSPRadar uses a deterministic 500-resample percentile bootstrap with replacement and reports the central 90% interval around the median. Station-level intervals resample station medians. Raw paired intervals resample peer-cycle or paired-bin Delta values.

The calculation treats values as exchangeable even though WSPR observations can remain correlated by station, time and geography. It is a descriptive **Stability** interval, not a confidence interval or significance test.

Compare Delta-SNR histograms use fixed bins within a panel. They normally use 1 dB bins, use 0.5 dB only for a clear half-dB lattice and aggregate broad ranges to 1, 2, 3, 6 or 10 dB so a panel does not exceed 40 bars. A minimum visible span of 3 dB avoids visually magnifying tiny variation.

<a id="sec-7-9"></a>
#### 7.9 Geography and solar classification

WSPRadar calculates distance and azimuth using a spherical Earth radius of 6371 km and renders an Azimuthal Equidistant projection centered on Target QTH. Radial boundaries are 2500, 5000, 10000, 15000, 20000 and 22000 km; azimuth sectors are 22.5 degrees.

This is internally consistent mapping geometry, not survey-grade geodesy. Reported locators represent grid-cell positions rather than measured antenna coordinates.

`Local QTH Solar State` uses solar elevation at Target QTH. Success evidence plots separately classify sampled great-circle path illumination as night, greyline/mixed or daylight. These answer different questions.

<a id="sec-8"></a>
### 8. Limits, Valid Claims and Reproducibility

<a id="sec-8-1"></a>
#### 8.1 What WSPRadar does not isolate

WSPRadar results describe operating station systems under selected network and propagation conditions. They do not directly measure:

* antenna gain in dBi;
* radiation efficiency;
* take-off angle;
* calibrated receiver sensitivity;
* absolute field strength;
* every attempted or scheduled transmission;
* formal statistical significance or causation.

Principal limitations include:

* crowd-sourced callsigns, locators, powers and spots can be wrong;
* the archive contains successful decodes rather than complete attempt/failure logs;
* Success Rate is conditional on globally sourced observable opportunities;
* a TX cycle decoded nowhere is indistinguishable from no transmission without an external log;
* Target-active gating is asymmetric;
* sequential TX A/B remains time-separated;
* reported-power normalization is only as accurate as the reported field;
* station hardware, software, terrain, noise, polarization and propagation remain combined;
* network density varies by geography, band and time;
* distance does not establish radiation angle or propagation mode;
* upstream availability and archive corrections remain external.

<a id="sec-8-2"></a>
#### 8.2 Supported and unsupported wording

| Avoid | Evidence-matched wording |
|---|---|
| "Antenna A has 3 dBi more gain." | "Path A produced a +3.0 dB median normalized Delta SNR against B for the paired evidence in this band, window and segment." |
| "My receiver sensitivity is 72%." | "The Target receiver's Success Rate was 72% among qualifying peer-cycles independently confirmed elsewhere." |
| "Success should be close to 100%." | "Success is a conditional global network-reach factor; 100% is not the expected baseline." |
| "A is statistically significantly better." | "The paired median favored A and its descriptive 90% Stability interval was [range]; no significance test was performed." |
| "The antenna has a lower take-off angle." | "The observed advantage was concentrated in the specified longer-distance segments; radiation angle was not measured." |
| "A is more efficient because it had more exclusive decodes." | "A produced more exclusive decode evidence under the reported power, schedule and network conditions; efficiency was not isolated." |
| "The local median is the average local station." | "The Reference was the cycle/path median of one contribution per active local callsign+locator identity." |

<a id="sec-8-3"></a>
#### 8.3 Reporting checklist

For a serious result, report:

* WSPRadar version and preferably Git commit;
* exact UTC start and end;
* exact band and TX/RX direction;
* Target callsign and configured QTH;
* Benchmark Design, Reference identity or local radius/method;
* Hardware frame/bin design where applicable;
* Reference SNR Correction and calibration basis;
* special, moving-station and solar filters;
* all evidence thresholds;
* joint station and joint spot/bin counts;
* station-level median Delta SNR and 90% Stability interval;
* Decode Outcomes and `STATIONS` / `SPOTS` distributions;
* Success Rate with its denominator and weighting level;
* equipment, power, schedule and known limitations;
* export package plus external experiment notes.

Use replication, path swapping or independent calibration before making expensive decisions from a small difference.

<a id="sec-8-4"></a>
#### 8.4 Analysis export package

`Prepare All Results for Download` builds a package from the completed run and current inspector selections. A typical ZIP contains:

```text
config/
  wspradar_config.config
  run_metadata.json
compare/                         # when a benchmark result exists
  figure_map_highres.png
  figure_segment_insight.png
  figure_selected_station_evidence.png
  table_station_insights_current_segment.csv
  table_drilldown_selected_stations.csv
  table_drilldown_all_stations_current_segment.csv
  analysis_cache.parquet
success/                         # when a Success result exists
  ...same figure/table pattern...
  analysis_cache.parquet
```

Figures use a high-resolution light/paper presentation. Files without an applicable recipe or selected evidence can be absent. CSV files reflect current segment and station selections. Parquet files contain processed post-filter evidence, not untouched wspr.live dumps.

Configuration and run metadata record application version, export time, language, direction, band, benchmark choice, configured time selection, correction, filters, thresholds, result blocks and inspector selections.

The package supports audit and reproducibility but is not a complete computational snapshot. It does not currently include:

* exact SQL or untouched upstream responses;
* a dependency lock or operating-system description;
* Git commit identifier;
* strict-versus-fallback decode-filter state;
* dedicated exact resolved/quantized endpoints for a `Last X Hours` run.

Retain the ZIP with station notes, switching schedule, power measurements and calibration data.

<a id="sec-8-5"></a>
#### 8.5 Disclaimer and license

WSPRadar is experimental open-source software provided "as is" without warranties. Its source and methods can be audited, but accuracy, completeness, availability and suitability are not guaranteed. Do not make major financial or safety decisions from WSPRadar alone.

WSPRadar is licensed under the GNU Affero General Public License version 3 (AGPLv3). The repository `LICENSE` file is controlling.

<a id="sec-a"></a>
### Appendix A: Parallel WSJT-X Instances

This procedure creates a second isolated WSJT-X instance, for example for simultaneous RX Hardware A/B on Windows. The current WSJT-X guide documents `--rig-name` as the supported way to isolate each instance's settings and writable files. WSJT-X versions and installation paths can change, so verify the current guide if your menus differ. <a href="#ref-2">[Ref-2]</a>

#### A.1 Create the second instance

1. Create a desktop shortcut for `wsjtx.exe`.
2. Open shortcut properties.
3. In the shortcut's **Target** field, add a distinct rig name outside the executable quotation marks. Use the actual executable path from your installation, for example:
   `"C:\WSJTX\bin\wsjtx.exe" --rig-name=SDR`
4. Start the shortcut once and close it. For `--rig-name=SDR`, Windows creates these isolated locations:
   * settings: `%LOCALAPPDATA%\WSJT-X - SDR\WSJT-X - SDR.ini`
   * log/writable directory: `%LOCALAPPDATA%\WSJT-X - SDR\`
   * default saved-audio directory: `%LOCALAPPDATA%\WSJT-X - SDR\save\`

#### A.2 Clone the starting configuration if required

1. Close all WSJT-X instances.
2. Copy `%LOCALAPPDATA%\WSJT-X\WSJT-X.ini`.
3. Paste it into `%LOCALAPPDATA%\WSJT-X - SDR\`.
4. Rename the copy to `%LOCALAPPDATA%\WSJT-X - SDR\WSJT-X - SDR.ini`, replacing the newly initialized instance file if intended.

#### A.3 Separate every data path

A cloned configuration can still point both instances at the same audio input or storage path. That can duplicate decoding of the same audio stream or create file conflicts. In the second instance, verify:

1. Open **File > Settings > Audio**.
2. Under **Soundcard**, set **Input** to the intended independent receiver or audio device. The WSJT-X guide specifies 48,000 Hz, 16-bit audio-device configuration.
3. Set **Save Directory** to an instance-specific path, normally `%LOCALAPPDATA%\WSJT-X - SDR\save\`.
4. Set **AzEl Directory** to an instance-specific path, for example `%LOCALAPPDATA%\WSJT-X - SDR\`.
5. Open **File > Settings > General** and set the exact Setup B callsign and locator used for reporting.
6. Return to the main WSPR screen, confirm the intended band and audio level, enable spot uploading when required, and verify that uploaded rows use the Setup B identity.
7. Confirm clock synchronization for both instances.

Separate directories do not prove RF-path independence. Confirm empirically that both streams use the intended hardware.

<a id="sec-b"></a>
### Appendix B: Timed A/B Relay Switch

For sequential TX A/B antenna tests, one transmitter feeding two RF paths through a controlled switch is normally preferable to two independent transmitters. Transmitter, frequency reference, WSPR chain, callsign, power setting and timing remain common.

WSPRadar includes:

`tools/Timed-AB-Relay-Switch`

Release package:

https://github.com/markusthemaker/WSPRadar/releases/download/timed-ab-relay-switch-v0.1.0/Timed-AB-Relay-Switch-v0.1.0.zip

The helper drives supported USB HID relay hardware on the two WSPR-frame sequences:

* Target frames: UTC `00, 04, 08, ...`
* Reference frames: UTC `02, 06, 10, ...`

An optional lead time lets the RF path settle before transmission. The helper targets common ATtiny45/V-USB HID relay boards with USB VID/PID `16c0:05df` and uses the Python HID stack on Windows, Linux and macOS. Consult its README for current installation, permissions and options.

Install from the tool directory:

```bat
py -3 -m pip install -r requirements-relay.txt
```

or on Linux/macOS:

```sh
python3 -m pip install -r requirements-relay.txt
```

Windows setup and dry run:

```bat
Start-Timed-AB-Relay-Switch.cmd --setup
Start-Timed-AB-Relay-Switch.cmd --dry-run
```

Linux/macOS setup and dry run:

```sh
chmod +x ./Start-Timed-AB-Relay-Switch.sh
./Start-Timed-AB-Relay-Switch.sh --setup
./Start-Timed-AB-Relay-Switch.sh --dry-run
```

A small USB relay should not normally switch RF directly. It should control a properly rated RF switch or relay system. Verify voltage, current, polarity, fail-safe state, RF power, isolation and interlocks.

Before transmitting:

* test without RF power;
* verify Target and Reference path polarity;
* verify no transition occurs during a WSPR transmission;
* use a dummy load or low-power continuity/SWR test;
* document relay channel, polarity, lead time, frame assignment and path mapping.

Switch loss, isolation, connectors, feedline differences and antenna surroundings remain part of the result. Swapping antennas between switch paths can help separate antenna effects from path effects.

<a id="sec-c"></a>
### Appendix C: Reference SNR Calibration

This procedure estimates a stable additive offset between receive chains or Reference-side paths.

1. **Common input:** feed both receive chains from one stable antenna through a suitable splitter and controlled cables.
2. **Characterize the splitter:** account for output imbalance and cable differences; swap outputs in a control run when practical.
3. **Collect paired evidence:** operate simultaneously across the intended signal levels without changing gain or decoder settings.
4. **Estimate the offset:** use paired Delta-SNR evidence and state whether the estimator is station-balanced or raw-pair.
5. **Check stability:** inspect by station, time and SNR. One constant is not defensible if offset changes with level, frequency, AGC or time.
6. **Apply the sign:** enter the observed `target - reference` offset with the same sign.
7. **Validate:** repeat or swap paths and confirm corrected common-input Delta is plausibly near zero.

A narrow Stability interval indicates repeatability of the available sample, not traceable laboratory accuracy. Splitter loss, mismatch, coupling and source instability can remain.

<a id="sec-d"></a>
### Appendix D: Literature, Prior Art and Positioning

This appendix supports WSPRadar's positioning without interrupting the operator guide. It does not claim that the literature validates every WSPRadar metric or implementation choice.

#### D.1 WSPR as an observation network

Taylor and Walker describe WSPR's purpose and practical global use as a weak-signal propagation reporter. <a href="#ref-4">[Ref-4]</a>

The public archive is not laboratory instrumentation. The combination of broad geographic participation, historical depth and successful-decode records makes it powerful for observational analysis while requiring explicit handling of station activity, identity and sampling.

#### D.2 WSPR in radio science

Lo et al. used 7 MHz WSPR observations to study greyline propagation. They discuss inconsistent station information, the lack of official operating schedules and the value of checking transmitter or receiver activity elsewhere in the network. That activity logic is relevant prior art for WSPRadar's Target-Active Gate, although the estimands differ. <a href="#ref-5">[Ref-5]</a>

Frissell et al. describe WSPRNet, the Reverse Beacon Network and PSKReporter as important amateur-radio observation networks for heliophysics and citizen science. They distinguish those broad networks from purpose-built finely calibrated instruments. <a href="#ref-6">[Ref-6]</a>

The conclusion is deliberately limited: WSPR can support systematic radio-science questions when activity, sampling, identity and confounding are handled explicitly. Peer-reviewed use does not make every station comparison valid by default.

#### D.3 Antenna and station-comparison precedents

Vanhamel, Machiels and Lamy used two conditioned near-identical 160 m WSPR receive stations to compare antennas and propagation. Their simultaneous common-signal design supports RX Hardware A/B and the need to characterize receive-chain offsets. <a href="#ref-7">[Ref-7]</a>

Zander evaluates relative HF antenna efficiency through the global WSPR receiver network and discusses accuracy and limitations. It is relevant TX-side prior art, but it does not prove that every WSPR Delta SNR is calibrated efficiency. <a href="#ref-8">[Ref-8]</a>

Milazzo provides earlier amateur-radio technical precedent for WSPR antenna comparison. It demonstrates long-standing practical demand rather than a peer-reviewed standardized protocol. <a href="#ref-9">[Ref-9]</a>

Griffiths and Squibb used WSPR spot and SNR information to investigate practical HF receive-system improvements, supporting a whole-station interpretation that includes antenna, feedline, local noise and receiver. <a href="#ref-10">[Ref-10]</a>

#### D.4 Tools and practical prior art

WSPR.Rocks provides rapid WSPR exploration, SQL access, maps, tables, SpotQ and other analyses. WSPRadar differs by organizing the workflow around explicit experiment designs, pairing and row-level audit rather than a leaderboard. <a href="#ref-11">[Ref-11]</a>

Griffiths and Robinett demonstrate database joins and time-series views for comparing common WSPR senders, times and bands. <a href="#ref-12">[Ref-12]</a>

WSPRdaemon focuses on robust multi-receiver acquisition, scheduling and added noise/Doppler metadata, illustrating why acquisition stability and noise context matter for RX analysis. <a href="#ref-13">[Ref-13]</a>

SOTABEAMS WSPRlite and DXplorer provide accessible WSPR-based antenna/location comparison and the DX10 metric. <a href="#ref-14">[Ref-14]</a>

WSPR-Station-Compare explicitly connects station-comparison software with the Vanhamel and Zander methods. <a href="#ref-15">[Ref-15]</a>

The Antenna Performance Analysis Tool is another user-oriented WSPR antenna-report service. Its existence means WSPRadar should not claim to be the first WSPR antenna-analysis tool. <a href="#ref-16">[Ref-16]</a>

WATT provides Excel/VBA reporting, mapping, filtering and timeline exploration, reinforcing the practical value of inspectable data rather than only a fixed score. <a href="#ref-17">[Ref-17]</a>

#### D.5 WSPRadar's position

WSPRadar's contribution is the integration of:

* Target activity checks;
* same-cycle or controlled-bin comparison;
* reported-power normalization;
* Hardware, Buddy and Local benchmark designs;
* conditional Success analysis;
* paired Delta SNR and categorical Decode Outcomes;
* station-balanced geographic aggregation;
* `STATIONS` and `SPOTS` composition;
* Drill-Down and exportable processed evidence.

It should not be described as replacing wspr.live, WSPR.Rocks, WSPRdaemon, DXplorer or controlled RF measurement. It operates one methodological level above a spot browser: **which observations are eligible for this experiment, what paired difference was observed, what one-sided evidence remains, and can the conclusion be audited?**

<a id="sec-ref"></a>
### References

* <a id="ref-1"></a><a href="#ref-1">[Ref-1]</a> **Official technical overview.** ARRL, *WSPR*: message format, coding, duration, timing, occupied bandwidth and SNR reference. Accessed 2026-07-12.
  https://www.arrl.org/wspr

* <a id="ref-2"></a><a href="#ref-2">[Ref-2]</a> **Official software documentation.** WSJT-X 3.0.1 User Guide: WSPR message formats and decoder performance; Windows `--rig-name` file isolation; Audio settings and file locations. Accessed 2026-07-12.
  https://wsjt.sourceforge.io/wsjtx-main_en.html

* <a id="ref-3"></a><a href="#ref-3">[Ref-3]</a> **Official data-service documentation.** WSPR.live, *Welcome to WSPR Live* and *WSPR Exporter*: database description, schema, mode-code mapping, raw-data/availability disclaimer and real-time delay. Accessed 2026-07-12.
  https://wspr.live/
  https://wspr.live/wspr_downloader.php

* <a id="ref-4"></a><a href="#ref-4">[Ref-4]</a> Taylor, J. H.; Walker, B. (2010). *WSPRing Around the World*. QST, 94(11), 30-32.
  https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf

* <a id="ref-5"></a><a href="#ref-5">[Ref-5]</a> **Peer-reviewed article.** Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). *A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals*. Atmosphere, 13(8), 1340. doi:10.3390/atmos13081340.
  https://www.mdpi.com/2073-4433/13/8/1340

* <a id="ref-6"></a><a href="#ref-6">[Ref-6]</a> **Peer-reviewed review article.** Frissell, N. A. et al. (2023). *Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations*. Frontiers in Astronomy and Space Sciences, 10, 1184171. doi:10.3389/fspas.2023.1184171.
  https://www.frontiersin.org/articles/10.3389/fspas.2023.1184171/full

* <a id="ref-7"></a><a href="#ref-7">[Ref-7]</a> **Peer-reviewed article.** Vanhamel, J.; Machiels, W.; Lamy, H. (2022). *Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*. International Journal of Antennas and Propagation, 2022, 4809313. doi:10.1155/2022/4809313.
  https://research.tudelft.nl/en/publications/using-the-wspr-mode-for-antenna-performance-evaluation-and-propag/

* <a id="ref-8"></a><a href="#ref-8">[Ref-8]</a> **Preprint.** Zander, J. (2022). *Simple HF antenna efficiency comparisons using the WSPR system*. arXiv:2209.08989. doi:10.48550/arXiv.2209.08989.
  https://arxiv.org/abs/2209.08989

* <a id="ref-9"></a><a href="#ref-9">[Ref-9]</a> **Amateur-radio technical article.** Milazzo, C. F. / KP4MD (2011). *Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*.
  https://www.qsl.net/kp4md/wspr.htm

* <a id="ref-10"></a><a href="#ref-10">[Ref-10]</a> Griffiths, G.; Squibb, N. J. (2017). *Improving HF Band SNR from analysis of WSPR spots*. Practical Wireless, October 2017, 23-26.
  https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf

* <a id="ref-11"></a><a href="#ref-11">[Ref-11]</a> **Tool documentation.** WSPR.Rocks, *Help &amp; Documentation*: SpotQ, SQL access, duplicate analysis, maps, charts and heatmaps.
  https://wspr.rocks/help.html

* <a id="ref-12"></a><a href="#ref-12">[Ref-12]</a> Griffiths, G.; Robinett, R. (2020). *Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana*. ARRL/TAPR Digital Communications Conference 2020.
  https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf

* <a id="ref-13"></a><a href="#ref-13">[Ref-13]</a> **Tool documentation.** WSPRdaemon, *How wsprdaemon Works*: multi-receiver decoding, reporting, scheduling, noise and Doppler metadata.
  https://wsprdaemon.readthedocs.io/en/stable/description/how_it_works.html

* <a id="ref-14"></a><a href="#ref-14">[Ref-14]</a> **Product documentation.** SOTABEAMS, *WSPRlite Classic / DXplorer*: WSPR-based antenna-performance analysis and DX10 metric.
  https://www.sotabeams.co.uk/wsprlite-classic

* <a id="ref-15"></a><a href="#ref-15">[Ref-15]</a> **Project documentation.** WSPR-Station-Compare, project page referencing Vanhamel et al. and Zander.
  https://sites.google.com/myuba.be/wspr-station-compare/home

* <a id="ref-16"></a><a href="#ref-16">[Ref-16]</a> **Tool documentation.** Antenna Performance Analysis Tool, WSPR-based antenna report generator.
  https://wspr.bsdworld.org/

* <a id="ref-17"></a><a href="#ref-17">[Ref-17]</a> **Tool documentation.** GM4EAU, *WATT WSPR Analysis Tool*: Excel/VBA reporting, mapping, filtering and timeline animation.
  https://www.gm4eau.com/home-page/wspr/
