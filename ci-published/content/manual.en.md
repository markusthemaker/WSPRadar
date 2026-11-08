
---

<a id="sec-1"></a>
<a id="part-0"></a>

## Part 0: Why WSPRadar

You change an antenna, feedline, receiver or station setting. **Did it help — and where, when and by how much?** A stronger report or extra WSPR spot is a useful observation, but propagation, remote-station activity and local noise may have changed too.

WSPRadar helps investigate that question across many radio paths. It analyzes WSPR reception reports to show geographic reach, signal differences and decoding consistency over time. You can follow a map pattern down to the stations and individual reports behind it.

Repeated or simultaneous comparisons provide a stronger basis than unrelated reports collected hours apart. Published WSPR experiments demonstrate the value of comparable operating conditions <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-3">[Ref-3]</a> <a href="#ref-4">[Ref-4]</a> <a href="#ref-5">[Ref-5]</a>.

**WSPRadar describes complete stations and documented signal paths under real operating conditions.** It does not directly measure antenna gain, efficiency or receiver sensitivity. To attribute a difference to one component, control the other differences and repeat the comparison.

<a id="sec-1-1"></a>

### 0.1 WSPR in 2 Minutes

<strong class="defined-term">WSPR</strong> means **Weak Signal Propagation Reporter**. Low-power stations transmit timed digital signals that other stations decode and report. A <strong class="defined-term">WSPR cycle</strong> is a two-minute interval beginning at an even UTC minute <a href="#ref-6">[Ref-6]</a> <a href="#ref-8">[Ref-8]</a>.

A <strong class="defined-term">spot</strong> is an uploaded reception report of a successful decode. It records the transmitter and receiver callsigns and locations, time, band, reported transmit power and <strong class="defined-term">SNR</strong> — signal-to-noise ratio in dB. Higher SNR means a stronger signal relative to noise; a negative value does not mean decoding failed.

**WSPRadar analyzes uploaded reports; it does not receive or decode radio signals.** WSPRnet displays reception reports. WSPRadar normally reads **wspr.live**, with **WSPRDaemon WD2** and **WD1** as alternatives; each run uses one database without combining sources. See [data availability and source selection](#sec-6-6) <a href="#ref-10">[Ref-10]</a> <a href="#ref-11">[Ref-11]</a>.

Reports show successful decodes, not every attempted transmission or listening receiver. **A missing spot alone does not prove a failed reception.** How WSPRadar handles that uncertainty depends on the analysis you choose.

<a id="sec-1-0"></a>
<a id="sec-1-2"></a>

### 0.2 What WSPRadar can show

The <strong class="defined-term">Target</strong> is the station or signal path you want to investigate. A <strong class="defined-term">remote station</strong>, also called a peer, is a transmitter in RX or a receiver in TX. Its radio path to the Target contributes to the analysis.

<strong class="defined-term">Performance</strong> examines the Target on its own. <strong class="defined-term">Benchmark</strong> compares it with one <strong class="defined-term">Reference</strong> — another controlled signal path or a known station.

| Your question | Choose | What it examines |
|---|---|---|
| What can this station receive, and how consistently? | <strong class="defined-term">RX Performance</strong> | Which transmitters Target hears and how regularly. Missed decodes also count when reports establish the required station activity. |
| Where is this station heard, and how consistently? | <strong class="defined-term">TX Performance</strong> | Which receivers hear Target and how regularly. Missed decodes also count when reports establish the required station activity. |
| How do two receiving setups compare? | <strong class="defined-term">RX Benchmark</strong> | Target and Reference receiving the same remote transmitters in the same WSPR cycles. |
| How do two transmitting setups compare? | <strong class="defined-term">TX Benchmark</strong> | The same remote receivers hearing Target and Reference in the same WSPR cycles. |

Performance is useful for establishing a station baseline or investigating geographic and time patterns. Benchmark can compare antennas, feedlines, receivers, filters, preamplifiers or complete setups. An independent Reference compares complete installed stations, including their sites and noise environments; it is not automatically a calibrated standard.

<a id="sec-1-3"></a>

### 0.3 What one run produces

A <strong class="defined-term">run</strong> analyzes reports for your chosen analysis, band, UTC window and settings. It produces maps, summaries over distance and time, station tables and individual observations you can inspect.

The physical <strong class="defined-term">experiment</strong> is the on-air setup and operation that produced those reports. Changing how you display a completed run does not create a new experiment.

Use the results to ask whether a pattern is broad or limited to a few stations, whether it persists over time, and how much evidence supports it. The results and their settings can be downloaded for later review; your own setup notes complete the record.

<a id="sec-1-4"></a>

### 0.4 Your first useful run

Start with **Load Demo**. Choose a maintained example, read its experiment notes and keep the prepared settings for the first run. Both input views offer two routes:

- **Load and walk through setup** opens the Guided steps.
- **Load and review to run** opens Guided Review directly, as do website demo links and shared demo URLs.

Loading alone does not start an analysis. Check the settings, then select **Run RX Analysis** or **Run TX Analysis**, as appropriate.

Follow one feature from the map to the stations and reports behind it. Open **How to read this** beside a result for its metric, legend and interpretation. A demo teaches the method; it does not describe your station. Then use [Chapter 1](#sec-2) to prepare your own run.

<a id="documentation-toc"></a>

### Table of Contents

**[Part 0: Why WSPRadar](#part-0)**

* [0.1 WSPR in 2 Minutes](#sec-1-1)
* [0.2 What WSPRadar can show](#sec-1-0)
* [0.3 What one run produces](#sec-1-3)
* [0.4 Your first useful run](#sec-1-4)

**Part I: Operator Guide**

* [1. Choose and Prepare the Analysis](#sec-2)
    * [1.1 Prepare your station and reports](#sec-2-1)
    * [1.2 Configure your analysis](#sec-2-2)
    * [1.3 Navigate the results](#sec-2-3-overview)
* [2. Run and Interpret Your Analysis](#sec-3)
    * [2.1 RX Benchmark](#sec-3-rx-benchmark)
        * [2.1.1 Reference Setup/Station](#sec-3-rx-benchmark-hardware)
    * [2.2 TX Benchmark](#sec-3-tx-benchmark)
        * [2.2.1 Reference Setup/Station](#sec-3-tx-benchmark-simultaneous)
    * [2.3 RX Performance](#sec-3-rx-performance)
    * [2.4 TX Performance](#sec-3-tx-performance)
    * [2.5 Find and Review Temporary ΔSNR Departures](#sec-outlier)
        * [2.5.1 When to use this expert diagnostic](#sec-outlier-1)
        * [2.5.2 How detection works in practice](#sec-outlier-2)
        * [2.5.3 Read and investigate a reported event](#sec-outlier-4)
        * [2.5.4 Adjust selectivity and preserve the result](#sec-outlier-7)
* [3. Strengthen and Communicate Your Result](#sec-4)
    * [3.1 Judge breadth, consistency and repeatability](#sec-4-1)
    * [3.2 Strengthen a result through repetition and control](#sec-4-2)
    * [3.3 Write an evidence-matched conclusion](#sec-4-3)
    * [3.4 Preserve the run and its context](#sec-4-4)


**Part II: Practical Setup Guide**

* [4. Parallel WSJT-X Instances for Simultaneous RX](#sec-a)
    * [4.1 Create the Target and Reference instances](#sec-a-1)
    * [4.2 Clone the starting configuration if required](#sec-a-2)
    * [4.3 Separate every data path](#sec-a-3)
    * [4.4 Limitations of WSJT-X for simultaneous TX](#sec-a-4)
* [5. Simultaneous TX Reference Setup](#sec-simultaneous-tx-setup)
    * [5.1 Choose the callsigns](#sec-simultaneous-tx-setup-1)
        * [5.1.1 Two distinct callsigns](#sec-tx-two-distinct-callsigns)
        * [5.1.2 One callsign with two suffixes](#sec-tx-one-callsign-two-suffixes)
    * [5.2 Align the schedule and separate the signals](#sec-simultaneous-tx-setup-2)
    * [5.3 Check power and simultaneous signal quality](#sec-simultaneous-tx-setup-3)
    * [5.4 Verify WSPRnet and the selected database](#sec-simultaneous-tx-setup-4)
    * [5.5 Device-specific setup](#sec-simultaneous-tx-setup-5)
        * [5.5.1 QMX and QMX+ Virtual U3S, and Ultimate3S](#sec-simultaneous-tx-setup-5-1)
            * [5.5.1.1 Two distinct callsigns](#sec-qrp-two-distinct-callsigns)
            * [5.5.1.2 One callsign with two suffixes](#sec-qrp-one-callsign-two-suffixes)
            * [5.5.1.3 Shared power, frequency and verification steps](#sec-qrp-common-setup)
        * [5.5.2 ZachTek firmware 2.19](#sec-simultaneous-tx-setup-5-3)
            * [5.5.2.1 Two distinct callsigns](#sec-zachtek-two-ordinary-callsigns)
            * [5.5.2.2 One callsign with two suffixes](#sec-simultaneous-tx-setup-5-3-2)
            * [5.5.2.3 Shared timing, frequency randomization and verification](#sec-simultaneous-tx-setup-5-3-1)
    * [5.6 Confirm by exchange or crossover](#sec-simultaneous-tx-setup-6)
* [6. Reference SNR Calibration](#sec-reference-snr-calibration)

**Part III: Scientific Foundations, Methods and Claims**

* [7. Literature, Prior Art and Positioning](#sec-d)
    * [7.1 From reporting network to experimental dataset](#sec-d-1)
        * [7.1.1 Joe Taylor, K1JT, and Bruce Walker, W1BW: a shared experimental resource.](#sec-d-taylor-walker)
        * [7.1.2 Nathaniel Frissell and collaborators: amateur observations in space science.](#sec-d-frissell)
    * [7.2 Making observational WSPR data interpretable](#sec-d-2)
        * [7.2.1 Lo and collaborators, 2022: establish activity before interpreting silence.](#sec-d-lo)
        * [7.2.2 Gwyn Griffiths, G3ZIL, Rob Robinett, AI6VN, and Glenn Elmore, N6GN, 2019–2020: measure noise alongside reception.](#sec-d-griffiths-robinett-elmore)
    * [7.3 Antenna and station-comparison lineage](#sec-d-3)
        * [7.3.1 Patrick Destrem, F6IRF, 2008: automated switching and geographic comparison.](#sec-d-destrem)
        * [7.3.2 Charles Preston, KL7OA, later K7TAA, 2009 and 2017: simultaneous comparison.](#sec-d-preston)
        * [7.3.3 Sivan Toledo, 2010: a useful negative result about timing.](#sec-d-toledo)
        * [7.3.4 Carol F. Milazzo, KP4MD, 2011: compare complete stations in both directions.](#sec-d-milazzo)
        * [7.3.5 Gwyn Griffiths, G3ZIL, and Nigel Squibb, G4HZX, 2017: compare, investigate and retest.](#sec-d-griffiths-squibb)
        * [7.3.6 Vanhamel, Machiels and Lamy, 2022: characterize the receiving chains.](#sec-d-vanhamel)
        * [7.3.7 Jens Zander, 2022: state the comparison model and its assumptions.](#sec-d-zander)
        * [7.3.8 Thomas Rietdorf, DL2OAH, 2026: a synchronized multiband station comparison.](#sec-d-rietdorf)
        * [7.3.9 Dale Ostergaard, N3HXZ, 2026: practical sequential antenna comparisons.](#sec-d-ostergaard)
    * [7.4 Analysis infrastructure and related tools](#sec-d-4)
        * [7.4.1 Gwyn Griffiths and Rob Robinett, 2020: reusable database analysis.](#sec-d-griffiths-robinett)
        * [7.4.2 Arne and the wspr.live project, with computing resources from HB9VQQ.](#sec-d-wspr-live)
        * [7.4.3 Rob Robinett, AI6VN, and the WSPRdaemon community.](#sec-d-wsprdaemon)
        * [7.4.4 Tim, K5OHY — FarField Lab: accessible sequential antenna benchmarking.](#sec-d-farfield-lab)
        * [7.4.5 Phil, VK7JJ — WSPR.Rocks](#sec-d-wspr-rocks)
        * [7.4.6 Richard Newstead and SOTABEAMS — WSPRlite/DXplorer](#sec-d-wsprlite-dxplorer)
        * [7.4.7 Walter Machiels, ON4AWM — WSPR-Station-Compare](#sec-d-wspr-station-compare)
        * [7.4.8 Fred, W6BSD — Antenna Performance Analysis](#sec-d-antenna-performance-analysis)
        * [7.4.9 Colin Murray, GM4EAU — WATT](#sec-d-watt)
    * [7.5 What WSPRadar inherits, integrates and adds](#sec-d-5)
* [8. Scientific Methods](#sec-7)
    * [8.1 Shared evidence foundations](#sec-7-foundations)
        * [8.1.1 Spots, identities and cycles](#sec-7-spots-identities-cycles)
        * [8.1.2 Power normalization and consolidation](#sec-7-normalization-consolidation)
        * [8.1.3 Operating conditions and eligibility](#sec-7-activity-eligibility)
    * [8.2 Benchmark: differences and shared evidence](#sec-7-benchmark)
        * [8.2.1 Decode Outcomes and missing observations](#sec-7-benchmark-outcomes)
        * [8.2.2 Delta SNR and Reference correction](#sec-7-benchmark-delta)
        * [8.2.3 Station and map aggregation](#sec-7-benchmark-aggregation)
        * [8.2.4 Temporal decode coverage](#sec-7-benchmark-coverage)
        * [8.2.5 Controlled operation and retired designs](#sec-7-neighborhood)
    * [8.3 Performance: opportunities and success](#sec-7-performance)
        * [8.3.1 What counts as an opportunity?](#sec-7-performance-opportunities)
        * [8.3.2 Decode Rates and weighting](#sec-7-performance-rates)
        * [8.3.3 At-least-once Peer Reach](#sec-7-performance-reach)
        * [8.3.4 Successful Target SNR](#sec-7-performance-snr)
    * [8.4 Scope and summaries across space and time](#sec-7-views)
        * [8.4.1 Scope, geography and filters](#sec-7-view-scope)
        * [8.4.2 Geographic summaries](#sec-7-view-geography)
        * [8.4.3 Chronological evidence](#sec-7-view-time)
        * [8.4.4 Combining dates by UTC or local solar hour](#sec-7-view-folding)
        * [8.4.5 Selected Station Evidence](#sec-7-view-station)
        * [8.4.6 Spread and display scales](#sec-7-view-spread)
    * [8.5 How strong is the conclusion?](#sec-7-claims)
        * [8.5.1 Dependence and bias](#sec-7-dependence-bias)
        * [8.5.2 Repeatability and experimental control](#sec-7-repeatability-control)
        * [8.5.3 Validation scope](#sec-7-validation)
    * [8.6 Experimental ΔSNR event analysis](#sec-7-outliers)
        * [8.6.1 Departure from the local baseline](#sec-7-outlier-departure)
        * [8.6.2 Baseline and nearby variability](#sec-7-outlier-baseline)
        * [8.6.3 Candidate qualification](#sec-7-outlier-qualification)
        * [8.6.4 Boundaries and event classes](#sec-7-outlier-boundaries)
        * [8.6.5 Context and limits](#sec-7-outlier-context)
* [9. Evidence-Matched Claims and Reproducibility](#sec-8)
    * [9.1 Claim classes and evidence-matched wording](#sec-8-1)
    * [9.2 Interpretation boundaries](#sec-8-2)
    * [9.3 Reporting and reproducibility checklist](#sec-8-3)
    * [9.4 Analysis export package](#sec-8-4)

**Part IV: Controls and Troubleshooting**

* [10. Controls and Configuration](#sec-5)
    * [10.1 Workflow controls](#sec-5-1)
    * [10.2 Question, Target and measurement-window controls](#sec-5-2)
    * [10.3 Benchmark-design controls](#sec-5-3)
    * [10.4 Filters and evidence thresholds](#sec-5-4)
    * [10.5 Map, inspector and export controls](#sec-5-5)
    * [10.6 Benchmark outlier-detection controls](#sec-5-6)
* [11. Troubleshooting and Data Quality](#sec-6)
    * [11.1 Confirm the run definition first](#sec-6-1)
    * [11.2 Diagnose by symptom](#sec-6-2)
    * [11.3 Callsign and locator checks](#sec-6-3)
    * [11.4 Historical decode-code fallback](#sec-6-4)
    * [11.5 Operating conditions and activity evidence](#sec-6-5)
    * [11.6 Working with upstream data](#sec-6-6)

**Part V: References**

* [References](#sec-ref)

**Experimental Use & Disclaimer**

---

<a id="part-i"></a>

## Part I: Operator Guide

[Chapter 1](#sec-2) prepares a run, [Chapter 2](#sec-3) explains the essential meaning of each analysis, and [Chapter 3](#sec-4) helps you check and preserve a conclusion. Use **How to read this** beside a result for detailed chart guidance, [Part IV](#part-ii) for controls and troubleshooting, and [Part III](#part-iii) for calculations and scientific limits.

---

<a id="sec-2"></a>

### 1. Choose and Prepare the Analysis

Start with one station question. State what you changed or want to investigate, and which observation would help answer it.

<a id="sec-2-1"></a>

#### 1.1 Prepare your station and reports

1. **Create usable reports.** For RX, configure a WSPR-capable receiver and decoder, such as WSJT-X, with the correct receiving callsign, locator, band, audio input and synchronized clock. Enable uploads: a local decode that was never uploaded is unavailable to WSPRadar. For TX, configure the callsign, locator, band, timing and truthful transmit-power report; remote receivers provide the spots. The [WSJT-X reference](#ref-12) covers basic setup.
2. **Check your callsign and locator in the database.** Check the exact RX reporting callsign or TX callsign, reported locator and UTC times in WSPRnet, then in the database WSPRadar will use. Use the callsign exactly as recorded, including any suffix. Choose a completed period and allow reports to arrive; no fixed delay guarantees completeness. See [data troubleshooting](#sec-6-6).
3. **Keep the setup interpretable.** Record the antenna, feedline, radio, decoder, gain or power settings, software, schedule and deliberate changes. Keep other variables stable and clocks synchronized. For Benchmark, prepare both setups using [RX guidance](#sec-3-rx-benchmark-hardware) or [TX guidance](#sec-3-tx-benchmark-simultaneous) before collecting the comparison.

<a id="sec-2-2"></a>

#### 1.2 Configure your analysis

Choose the analysis from [Section 0.2](#sec-1-0). <strong class="defined-term">Guided</strong> leads you through the settings; <strong class="defined-term">Compact</strong> presents the same analysis choices in a shorter form.

Enter the exact **Target callsign**, **Target QTH** (Maidenhead locator), one **band**, and a completed **UTC window**. Target QTH accepts four or six locator characters: the first four select reports, while the full entered locator anchors the map, distances and directions. Longer windows add evidence but can mix operating and propagation conditions.

<a id="sec-2-5"></a>

**For Benchmark**, enter the Reference callsign exactly as reported; it must differ from Target. Leave its optional QTH blank to find the location from reports, or enter its independently known four-character locator. If several locations appear, choose one. A location alone does not establish operation or a shared physical site.

Confirm the operating conditions independently:

- **RX Benchmark:** both receivers listened on the selected band with functioning uploads throughout the period. This does not require a decode in every cycle.
- **TX Benchmark:** both transmitters sent in the same WSPR cycles, with aligned schedules and message patterns.

Keep the operating records that support this. WSPRadar cannot establish continuous operation from successful reports alone. Before you run a Benchmark, go to **RUN ANALYSIS** in Review and select **I have confirmed common operation, or accept the limitations when it is unverified.** This includes the maintained Milazzo example and other historical reports without independently verified common operation. The acceptance does not record which alternative applies and is not proof of operation; see [Section 10.3](#sec-5-3).

Leave **Reference SNR correction** at **No correction** unless you have an independently established offset valid for this setup. See [calibration guidance](#sec-reference-snr-calibration).

For the first run, review the displayed filters and evidence requirements without lowering them merely to obtain more colored map areas. **Maximum peer distance from Target (km)** changes which remote stations enter the analysis, not just the map zoom; choose it to match your question. See [scope and evidence controls](#sec-5-4). Check the final summary, then select **Run RX Analysis** or **Run TX Analysis**. Exact controls are in [Chapter 10](#sec-5); unexpected gaps are addressed in [Chapter 11](#sec-6).

<a id="sec-2-3-overview"></a>

#### 1.3 Navigate the results

Follow one pattern through the results. Open **How to read this** beside a view when you need its legend, counting rules or interpretation.

In Performance, **At a glance** above **Global View** summarizes the whole completed analysis: decoding frequency, station reach, the mean of the stations' individual decode rates and the distances of decoded signals. [Section 8.4.2](#sec-7-view-geography) explains which stations enter these summaries and how the rates and distances are weighted.

<a id="sec-3-4"></a>
<a id="sec-3-5"></a>

**1.** <strong class="defined-term">Global View</strong> **— where is the pattern?** A <strong class="defined-term">map segment</strong> covers directions and distances from Target. Read its numerical scale and supporting counts. Gray diagonal hatching (**Not qualifying**) means observations remain for this map but its coloring requirements are unmet. An unfilled segment (**No observations**) has none remaining. Performance uses stations meeting its station requirements; Benchmark retains all observed stations within the selected area and filters. A zero value stays colored when requirements are met. Hatching and unfilled areas do not mean a measured zero reception rate.

<a id="sec-3-6"></a>
<a id="sec-3-6a"></a>
<a id="sec-3-6b"></a>

**2.** <strong class="defined-term">Segment Inspector</strong> **— how broad and persistent is it?** Select directions and distances. This <strong class="defined-term">active scope</strong> determines the stations and observations in Decodes & Stations, population counts, segment statistics and time plots. Decodes & Stations follows the Active scope summary; its count cards precede Benchmark Statistics. Compare station and observation counts, then check individual dates before calling a combined hour-of-day pattern recurring. In <strong class="defined-term">Benchmark Statistics</strong>, compare the spot-pair, station-mean and station-median ΔSNR distributions. Frequently observed stations supply more spot pairs; each included station contributes one mean or median to the station distributions.

<a id="sec-3-7"></a>
<a id="sec-3-7a"></a>
<a id="sec-3-7b"></a>

**3.** <strong class="defined-term">Station Insights</strong> → <strong class="defined-term">Selected Station Evidence</strong> **— which stations explain it?** Select a typical station, an unusual one, or one with many reports. Both Performance and Benchmark list the whole completed analysis by default. **Filter by selected segment and distance** narrows the list; station metrics and plots still cover the full run, even if the filter hides the selected station. This list filter lasts only for the session. In Benchmark, **Include one-sided evidence** also shows stations without spot pairs and one-sided Drill-Down observations.

<a id="sec-3-8"></a>

**4.** <strong class="defined-term">Drill-Down</strong> **— what happened in individual cycles?** Check exact callsigns and locators, UTC times, SNR and outcomes. Focus the time window to inspect an interval. These observations have already been matched and filtered; they are not an untouched database download.

**Reading the statistical summaries.** The charts use the following terms:

| Term | Meaning |
|---|---|
| <strong class="defined-term">Arithmetic mean (Mean)</strong> | Add the values and divide by their count. |
| <strong class="defined-term">Median</strong> | The middle value after sorting; with an even count, average the two middle values. Mean and Median summarize the same observations but respond differently to extreme values. |
| <strong class="defined-term">Confidence interval (CI)</strong> | Describes uncertainty in an estimated mean under the stated sampling model. |
| <strong class="defined-term">Sample standard deviation (SD)</strong> | Describes how widely the observed values vary. |
| <strong class="defined-term">Standard error</strong> | Describes the model-based uncertainty of the mean. Under the independent-observation model, it is sample SD divided by the square root of the observation count. |
| <strong class="defined-term">Interquartile range (IQR)</strong> | Q3 minus Q1. The plotted Q1–Q3 interval covers the middle 50% of the values: it shows their spread, not uncertainty of the mean. |

A <strong class="defined-term">time bin</strong> groups observations in one displayed interval. Its <strong class="defined-term">pointwise confidence interval</strong>, labelled <strong class="defined-term">Bin 95% CI</strong>, applies to that bin's mean, not simultaneously to the whole curve. The percentage follows the selected confidence level. That level describes the procedure over repeated samples, not a probability assigned to this particular interval. [Section 8.5.1](#sec-7-dependence-bias) explains the calculation and independence assumptions.

<a id="sec-3"></a>

### 2. Run and Interpret Your Analysis

Read the section for your chosen analysis. The essentials below explain what the result means; **How to read this** beside each result explains its plots and controls in detail.

**Counting stations and observations.** WSPRadar treats each exact callsign and full reported locator as one <strong class="defined-term">station identity</strong>, usually called a station below. A callsign at two locators counts twice; these are not necessarily independent physical stations. Multiple retained reports for one setup, remote station and WSPR cycle count as one observation.

**Benchmark compares signal quality and decoding.** A <strong class="defined-term">spot pair</strong> matches Target and Reference reports for the same remote station and WSPR cycle: one transmitter in RX or one receiver in TX. <strong class="defined-term">Both observed</strong> means the station appears on both sides during the period, possibly in different cycles; this alone does not establish a spot pair.

- <strong class="defined-term">ΔSNR</strong> (delta SNR) is Target SNR minus corrected Reference SNR for a spot pair. Positive favors Target; negative favors Reference; **0 dB** means equal SNR. For example, **+3 dB** means 3 dB higher Target SNR in that comparison. It cannot describe a signal decoded on only one side.
- <strong class="defined-term">ΔDecode</strong> compares total observed decodes, including one-sided reports. The map's ratio legend is direct: **2× on the Target side** means twice the Reference decode total; **1×** means equal totals; <strong class="defined-term">Exclusive</strong> means only one side has decodes. Signals missed by both setups remain unknown, so ΔDecode is not a success rate over all transmissions. See [the exact calculation](#sec-7-benchmark-aggregation).

The ΔSNR map calculates the <strong class="defined-term">arithmetic mean</strong> of usable paired ΔSNR values from stations with retained pairs in the filtered run, giving every pair equal weight. Coloring requires both the station minimum and the pooled-pair CI precision requirement. ΔDecode adds all retained decodes into <strong class="defined-term">pooled totals</strong>. The measures can favor different setups. Benchmark ΔSNR time plots likewise combine usable pairs within each time bin. Frequently observed stations therefore contribute more to the decode totals and can contribute more pairs to both map and time summaries.

**Performance counts confirmed opportunities.** A <strong class="defined-term">confirmed opportunity</strong> concerns one remote station and one WSPR cycle. Successful reception by Target (RX) or of Target (TX) confirms it directly; otherwise reports must establish activity at both ends before a miss counts. <strong class="defined-term">Decode Rate</strong> is successes divided by successes plus confirmed misses, expressed as a percentage. Unknown activity is excluded. The RX and TX sections below explain who must have heard whom.

**Which stations enter a result?** A <strong class="defined-term">qualifying station</strong> has retained spot pairs for ΔSNR, or meets Performance's opportunity minimum and any required confirmation by other receivers. Each map segment must also meet its own coloring requirements. For ΔSNR, the CI must meet the selected precision limit. [Section 8.5.1](#sec-7-dependence-bias) explains its statistical assumptions and the exact coloring conditions.

**Check how SNR is expressed.** RX Performance and Benchmark adjust successful SNR to a common **reported transmit power of 1 W (30 dBm)**. New TX Performance analyses use raw reported received SNR by default; **SNR TX Normalization to 30 dBm** enables the same adjustment. Older TX settings without this field keep normalization on. This changes SNR comparisons, not observed decode counts, and cannot correct inaccurate power reports.

The cumulative Benchmark Decodes & Stations plots in the Segment Inspector use <strong class="defined-term">raw reported SNR</strong>, without power normalization or Reference correction. Performance uses the completed run's selected SNR basis. See [Section 8.1.2](#sec-7-normalization-consolidation).

<a id="sec-3-3"></a>
<a id="sec-3-rx-benchmark"></a>

#### 2.1 RX Benchmark

**Question:** How did two receiving setups compare for the same transmitters and cycles?

For a controlled RX Benchmark, both receivers must have been listening and uploading reports throughout the selected period. Benchmark includes reports from either side even in cycles with no Target report. Interpretation therefore relies on the operating conditions in [Section 1.2](#sec-2-2); Benchmark does not check Target activity separately in each cycle.

**First checks:**

1. Compare the **ΔSNR** and **ΔDecode** maps: does higher SNR among shared decodes accompany more total decodes?
2. Use the cumulative SNR plots to distinguish additional decodes from additional distinct transmitters. A one-sided decode need not add a new station.
3. In the Inspector, check whether the difference persists across several transmitters and times. Inspect a representative path in Station Insights and Drill-Down.

A station needs spot pairs for ΔSNR; all its observed decodes still count toward ΔDecode. The two maps have different requirements. A large value can come from only a few observations, so read the counts as well as the colors. See [evidence thresholds](#sec-5-4).

<a id="sec-2-3"></a>
<a id="sec-3-rx-benchmark-hardware"></a>

##### 2.1.1 Reference Setup/Station

**Controlled local setup.** Run separately identified receiving paths at the same time for the antennas, feedlines, filters, preamplifiers or receivers you want to compare. Check both exact reporting callsigns and locations in the database. A shared four-character locator does not establish that the equipment is at the same physical site or uses identical signal paths.

Keep non-tested parts of the chains equal, or measure their differences: receiver, gain, filtering, audio, decoder and uploads can all affect the result. A common-input calibration or swapping components between chains helps check whether an observed difference follows the tested component. Components intended to be common must actually be shared. See [parallel WSJT-X instances](#sec-a) and [Reference calibration](#sec-reference-snr-calibration).

RX reporting callsigns such as `CALL` and `CALL/P` can distinguish the receiving paths if the software and database preserve them. They do not change the remote transmitter's message format.

<strong class="defined-term">Reference correction</strong> applies an independently established offset to Reference SNR before subtraction. A positive correction raises Reference SNR and reduces the displayed Target advantage. It does not recover missed decodes or change ΔDecode. A geographically separated Reference can provide a repeatable baseline for that pair, not an absolute calibration.

<a id="sec-3-rx-benchmark-buddy"></a>

**Independent station.** Choose a Reference whose callsign, location, setup and schedule you understand. The comparison includes both stations' antennas, equipment, noise and propagation paths. Repeat with the same stable Reference and describe complete-station differences; attributing them to one antenna or receiver needs additional control. The maintained Griffiths/Squibb demo provides an example.

<a id="sec-3-tx-benchmark"></a>

#### 2.2 TX Benchmark

**Question:** How did two transmitting setups compare at the same remote receivers in the same cycles?

Each spot pair compares reports from the same receiver in the same cycle. RX pairs observe one transmitter; TX pairs compare two transmissions, so accurate reported power is essential to normalized ΔSNR. Actual power differences can still affect decode counts, which are not power-normalized.

**First checks:** compare the two maps, inspect receiver and pair counts, then follow representative receivers through the time views and Drill-Down. Check whether a result depends on a few receivers, one interval or an audio-frequency assignment. Better paired SNR does not guarantee more total decodes.

One-sided evidence remains included without a separate Target-activity check. If one transmitter was silent or reporting was interrupted, ΔDecode can reflect unequal operating opportunities. Establish common operation before interpreting it as a difference between transmit paths.

<a id="sec-2-4"></a>
<a id="sec-2-4-simultaneous"></a>
<a id="sec-3-tx-benchmark-simultaneous"></a>

##### 2.2.1 Reference Setup/Station

**Controlled local setup.** Use two separately identifiable transmit chains with different valid callsigns, synchronized WSPR cycles, clear separated frequencies, measured and truthfully reported power, and adequate RF isolation. One transmitter alternating between antennas cannot provide simultaneous spot pairs.

**Prefer two different valid ordinary callsigns.** Choose callsigns that each fit the one-transmission WSPR format, carrying callsign, locator and power together.

If <strong class="defined-term">compound callsigns</strong> — callsigns with an added prefix or suffix — are needed, two distinct valid compound callsigns can also work. For this controlled comparison, use matching, verified message sequences and align their corresponding transmissions. [Section 5.1](#sec-simultaneous-tx-setup-1) explains the callsign choices and the message formats they produce.

Before collecting reports, check the firmware settings, actual schedules and both transmitters' callsigns and locators in the database. WSPRadar compares individual two-minute cycles; different schedules can create one-sided reports without an equipment advantage. Follow [Chapter 5's setup and database checks](#sec-simultaneous-tx-setup).

The result compares complete transmit paths. Frequency response, QRM, coupling and power error can remain; swap frequency positions and, where practical, the tested antennas or components between chains. Use only a documented **Reference SNR correction** valid for the comparison; it affects ΔSNR, not decode counts. See [calibration guidance](#sec-reference-snr-calibration).

<a id="sec-3-tx-benchmark-buddy"></a>

**Independent station.** Choose a known Reference transmitter whose callsign, QTH, power, equipment and schedule you understand. Reports can come from the same receiver in the same cycle even though the transmitting sites and propagation paths differ. Equal four-character locators do not prove a shared physical site. Describe the result as a comparison of complete installed stations.

Both arrangements use **Reference Setup/Station**. Spot pairs are required for ΔSNR, but one-sided evidence can still contribute to ΔDecode when no pairs exist. The physical arrangement determines what can be concluded, not whether the callsigns share a base.

<a id="sec-3-1"></a>
<a id="sec-3-2"></a>
<a id="sec-3-rx-performance"></a>

#### 2.3 RX Performance

**Question:** Which transmitters did the Target hear, from which directions and distances, and how regularly?

Enter the Target receiver's callsign exactly as reported and its QTH locator. Choose one band and a period with uploaded Target decodes. Keep the receiving chain stable; no Reference is needed.

**What counts:** each Target decode confirms a successful opportunity, even if no other receiver reported that transmitter. A missing decode counts as a miss only when another receiver reported that transmitter and Target decoded a different transmitter, both on the **same band in the same WSPR cycle**. Otherwise the outcome is unknown and is excluded from the rate.

The counts and rates use stations that pass the filters and station requirements, including transmitters that Target never decoded. Read three complementary measures:

- <strong class="defined-term">At-least-once reach</strong> (**Station Reach**): the percentage of these transmitters that Target heard at least once. One success does not imply regular reception.
- <strong class="defined-term">Station-averaged Decode Rate</strong>: calculate each transmitter's decode rate, then average those percentages. Each station counts equally, including one with 0%. The map uses this rate. <strong class="defined-term">Opportunity-level Decode Rate</strong> pools all their successes and divides by all their confirmed opportunities. Stations with more opportunities influence this second rate more.
- <strong class="defined-term">Successful SNR</strong>: signal-to-noise ratio for decoded signals, adjusted to the common reported-power basis. Misses have no measured Target SNR.

For example, two stations with **90 successes out of 100 opportunities** and **5 out of 10** give a station-averaged rate of **70%**, but an opportunity-level rate of **86.4%** (95 out of 110). The two rates answer different questions; neither replaces the other.

Use the map to find a pattern, then compare reach and both rates in **Spot & Station Decodes**, including the distance rows in the Spots and Stations cards. The time plots show successful SNR, Decode Rate and supporting opportunities; a heatmap shows the pooled Decode Rate by distance and time. For a selected transmitter, two plots show absolute normalized successful SNR and Decode Rate with its supporting counts over the full run, without a distance heatmap or deviation plot. **How to read this** explains the weighting and chart details.

**Expert Review** shows how each station's SNR departs from its own mean or median over the run. Open it to investigate changes relative to that station's usual SNR; [Section 8.4.3](#sec-7-view-time) explains the calculation.

If Decode Rate falls while successful SNR rises, weak signals may have stopped being decoded. Stronger surviving reports alone do not show an improvement. Repeat the observations on the affected paths and at the relevant times. To attribute a change to one hardware component, use a controlled comparison or crossover: Performance also reflects local noise, other equipment and propagation.

<a id="sec-3-tx-performance"></a>

#### 2.4 TX Performance

**Question:** Which receivers heard the Target, from which directions and distances, and how regularly?

Enter the Target transmitter's callsign exactly as reported and its QTH locator. Choose one band and a period with reported Target transmissions. Keep the RF path, schedule and actual power stable, and report power accurately; no Reference is needed.

**What counts:** a receiver's report of Target confirms a successful opportunity, even if it reports no other transmitter. A missing Target decode counts as a miss only when **that receiver** reports another transmitter and a report elsewhere confirms that Target transmitted, both on the **same band in the same WSPR cycle**. A different receiver hearing Target does not show that a silent receiver was listening. Each success counts once; unknown activity remains excluded.

The counts and rates include receivers passing the filters and station requirements, even if they never decoded Target. **At-least-once reach** (**Station Reach**) is the percentage that heard Target at least once. Read it alongside Decode Rate and successful SNR. **Station-averaged Decode Rate** averages receiver percentages equally, including zeros; the map uses this mean. **Opportunity-level Decode Rate** divides combined successes by combined opportunities. These are confirmed opportunities, not every planned transmission or every possible receiver.

Use **Spot & Station Decodes** and the time plots to find a pattern, then inspect representative receivers. The plots show the SNR of successful decodes on the selected basis, Decode Rate and its supporting opportunities, plus the pooled rate by distance and time. For a selected receiver, two plots show absolute successful SNR and Decode Rate with its supporting counts over the full run; there is no distance heatmap or deviation plot. Check individual dates before describing a recurring daily pattern.

**Expert Review** compares each receiver's SNR with its own mean or median over the run; see [Section 8.4.3](#sec-7-view-time).

A broad footprint with low Decode Rates can mean intermittent reception; a high rate at a few receivers does not establish broad coverage. Results reflect actual transmit power, antenna and feedline, terrain, propagation and receiving conditions at the remote stations. They do not measure radiated power, antenna gain or efficiency. Use **TX Benchmark** to compare transmit paths and repeat useful observations under comparable conditions.

<a id="sec-outlier"></a>

#### 2.5 Find and Review Temporary ΔSNR Departures

This optional expert diagnostic looks for temporary changes in paired ΔSNR separately for each remote station. The report treats each exact callsign and full reported locator as one <strong class="defined-term">path</strong>. Complete the ordinary Benchmark review first. A possible outlier is a reason to investigate, not an identified physical event.

<a id="sec-outlier-1"></a>

##### 2.5.1 When to use this expert diagnostic

Use it when a temporary change matters to your question and enough spot pairs exist before, during and after it. One-sided reports provide context but no missing ΔSNR. An empty report may mean insufficient surrounding evidence, not an unchanged path.

Enable **Identify ΔSNR outlier candidates**, review the [three expert controls](#sec-5-6), then run the analysis. Changing the settings requires another explicit run.

<a id="sec-outlier-2"></a>
<a id="sec-outlier-3"></a>

##### 2.5.2 How detection works in practice

The <strong class="defined-term">local baseline</strong> estimates the path's usual ΔSNR from supported observations before and after a candidate, excluding the candidate. A <strong class="defined-term">departure</strong> is observed ΔSNR minus that baseline. Thus **+1 dB ΔSNR against a +8 dB baseline is a −7 dB departure**: Target still has higher SNR, but its advantage has fallen.

The detector checks departure size, a <strong class="defined-term">robust z-score</strong> comparing it with nearby variation, agreement of baseline medians before and after it, and sign agreement within the candidate. It uses individual cycle observations before display grouping, so changing a chart's time-bin width does not change detections. Event classes and cross-path groups establish neither different certainty nor a common cause. See [the method](#sec-7-outliers).

<a id="sec-outlier-4"></a>
<a id="sec-outlier-5"></a>
<a id="sec-outlier-6"></a>

##### 2.5.3 Read and investigate a reported event

Compare **Expected local ΔSNR** with **Observed median ΔSNR**, then inspect the pair count, timing gaps and underlying observations. **↓ Show in Station Insights** opens the path's wider history; **↓ Show Drill-Down Details** opens its detail. Both prepare **Outlier Focus** with surrounding baseline evidence.

Use **How to read this** in Outlier Report and Outlier Focus for event classes, stars, shading and detector guides. The highlighted interval describes retained observations, not the duration of an unseen physical event.

Check Target and corrected Reference SNR separately: either or both can drive a change. Compare nearby one-sided reports, other paths, station logs, switching, power or gain changes and independent measurements before assigning a cause.

<a id="sec-outlier-7"></a>

##### 2.5.4 Adjust selectivity and preserve the result

Larger minimum departure or robust-score thresholds make reporting more selective. A smaller allowed before/after baseline difference requires closer agreement of those medians, not lower background variability. The same requirements apply to all event durations; [Section 10.6](#sec-5-6) lists the controls.

Record exploratory changes. For confirmation, fix the settings and path population before examining a new run. Report the path, interval, departure, supporting pairs and detector settings. The detector does not supply a p-value or correction for the number of searched paths and events.

Save the analysis export to retain enabled outlier findings and their contributing pairs. File contents and availability are defined in [Section 9.4](#sec-8-4).

<a id="sec-3-9"></a>

---

<a id="sec-4"></a>

### 3. Strengthen and Communicate Your Result

Use the result to guide your next station decision. State what the observations support and what you still need to check.

<a id="sec-4-1"></a>

#### 3.1 Judge breadth, consistency and repeatability

Check three things before drawing a conclusion:

- <strong class="defined-term">Breadth:</strong> how many stations, observations, directions and time periods support it? Many reports from one station do not provide the same breadth as several paths. Remember that distinct callsign–locator combinations do not necessarily represent independent physical stations.
- <strong class="defined-term">Consistency within the run:</strong> do the map, time plots and station views tell a similar story? If equal-station and pooled results differ, inspect the stations with the most observations. Read paired ΔSNR alongside one-sided decodes, or Performance SNR alongside Decode Rate.
- <strong class="defined-term">Repeatability:</strong> does the pattern recur in a separate run under comparable, documented conditions? Agreement among views of the same data does not establish this.

A large value or a passed minimum requirement alone does not establish an equipment advantage or statistical confidence. Describe what was observed, then investigate possible explanations such as noise, propagation or hardware changes through controlled changes, crossover tests or independent measurements. [Section 8.5](#sec-7-claims) explains dependence and bias.

<a id="sec-4-2"></a>

#### 3.2 Strengthen a result through repetition and control

An <strong class="defined-term">exploratory run</strong> helps you find a possible pattern. Before a <strong class="defined-term">confirmatory run</strong>, fix the question, RX/TX direction, band, Reference where applicable, settings, thresholds, schedule and main geographic or time range. This includes **Maximum peer distance from Target (km)**. Keep alternative ranges as separate checks and report them, rather than selecting only the most favorable result.

Repeat on another day or propagation period while keeping non-tested variables stable. Use a long enough window to cover the conditions named in your conclusion; claims about daily patterns need evidence across dates, checked chronologically. Keep notes so the physical setup can be reproduced.

RX examines remote transmitters; TX examines remote receivers, with different opportunity rules. Match band, period, area and configuration when comparing your station's RX and TX results, but interpret them separately: equal percentages do not imply equal receive and transmit capability.

<a id="sec-4-3"></a>

#### 3.3 Write an evidence-matched conclusion

Name the Target, analysis type, band, UTC window and geographic area, then give the result **with its weighting and supporting counts**. For Benchmark, also name the Reference and its applied SNR correction, including zero. State how common operation was established, or identify the limitation of using historical reports without that confirmation.

**Performance template**

> For [Target, band, UTC window and scope], the Station-averaged Decode Rate was [x%] across [n included stations]. The opportunity-level rate was [y%] across [m confirmed opportunities]. The observed pattern was [broad, directional, intermittent, or specific to the stated time period].

**Benchmark template — station-median summary**

> For [Target and Reference, band, UTC window and scope], the median of station-median ΔSNR favored [setup] by [x dB], supported by [n stations with pairs and m spot pairs]. The pooled decode totals were [Target total] and [Reference total], with [Paired, Target-only and Reference-only counts]. The comparison used [controlled paths, independent stations, or historical replay].

For a **ΔSNR map segment**, report its **pooled mean paired ΔSNR and CI** instead. Name the segment and its station and spot-pair counts; [Section 8.2.3](#sec-7-benchmark-aggregation) explains the different weighting.

Include the count or percentage of reached stations and relevant time patterns where they support the claim. Compare the numerical legend values across maps. A difference between complete stations does not by itself establish antenna gain, efficiency, calibrated sensitivity or a physical cause that the experiment did not measure. [Chapter 9](#sec-8) gives the full reporting checklist and examples.

<a id="sec-4-4"></a>

#### 3.4 Preserve the run and its context

Select the Inspector area, station and any focus interval you want to preserve. Choose **Prepare All Results for Download**, then **Download Prepared Results**. Preparing alone does not save the file; prepare again after changing those selections.

The ZIP includes the configuration, metadata, processed observations, and applicable tables and figures. The processed observations cover the completed run; individual tables and figures cover their respective selected areas or stations. **Save Config** or an analysis link preserves settings, not the original observations. A later query or rerun can produce different results.

Keep concise station notes with the ZIP: antennas and feedlines, chain or splitter arrangement, hardware/software, gain and power, schedules, calibration and deliberate changes or faults. WSPRadar cannot infer these physical details. See [the record checklist](#sec-8-3) and [export contents](#sec-8-4).

<div style="page-break-before: always;"></div>

<a id="part-iv"></a>

## Part II: Practical Setup Guide

Set up two receive paths, prepare a simultaneous transmit comparison, or measure an RX correction. Choose the route for your experiment and complete its checks before recording the measurement data.

| Goal | Route | Ready when |
|---|---|---|
| **Simultaneous RX on Windows** | [Chapter 4](#sec-a): create, optionally clone, then verify the two WSJT-X paths. Continue to [Chapter 6](#sec-reference-snr-calibration) if calibration is needed. | Both receivers upload under the expected callsigns and locators, with correct audio/data paths and synchronized clocks. |
| **Controlled simultaneous TX** | [Chapter 5](#sec-simultaneous-tx-setup): plan the setup, follow the [hardware recipe](#sec-simultaneous-tx-setup-5), then check [timing and signals](#sec-simultaneous-tx-setup-2), [power](#sec-simultaneous-tx-setup-3) and [database reports](#sec-simultaneous-tx-setup-4). Use [5.6](#sec-simultaneous-tx-setup-6) to confirm the result. | Common receivers report both clean, correctly placed signals in the intended cycles, under the expected callsigns and locators. |
| **Documented RX SNR correction** | [Chapter 6](#sec-reference-snr-calibration): common-input measurement, consistency checks, signed correction and independent validation. | The offset is stable within recorded conditions and supported by separate validation evidence. |

Use instructions for the exact hardware and firmware; the ZachTek recipe uses standard scheduling and frequency randomization. When ready, return to [Section 1.2](#sec-2-2). Keep **No correction** unless an offset is justified.



<a id="sec-a"></a>
### 4. Parallel WSJT-X Instances for Simultaneous RX

**Goal:** run two receive paths at the same time, with separate audio inputs, reporting callsigns, settings and files. This Windows procedure uses WSJT-X's documented `--rig-name` option; it does not require a second installation of WSJT-X <a href="#ref-12">[Ref-12]</a>.

Create two named instances: **WSJT-X Target** and **WSJT-X Reference**. Optionally copy a working starting configuration, then check both paths before collecting measurements. These names identify the local software instances; they do not set the callsigns uploaded to the database.

For a simultaneous TX experiment, use [Chapter 5](#sec-simultaneous-tx-setup). [Section 4.4](#sec-a-4) explains why matching two WSJT-X `Tx Pct` settings does not establish a shared schedule that uses only some transmit cycles.



<a id="sec-a-1"></a>
#### 4.1 Create the Target and Reference instances

1. Create two desktop shortcuts for your installed `wsjtx.exe`. Name them **WSJT-X Target** and **WSJT-X Reference**.
2. Open each shortcut's **Properties**. In the Windows **Target** field, add its rig name **after** the executable's closing quotation mark. Replace the example executable path with your installation path:

| Shortcut | Windows shortcut **Target** field |
|---|---|
| **WSJT-X Target** | `"C:\WSJTX\bin\wsjtx.exe" --rig-name=Target` |
| **WSJT-X Reference** | `"C:\WSJTX\bin\wsjtx.exe" --rig-name=Reference` |

3. Start each shortcut once, then close it to initialize its files.

The Windows locations are:

| File or folder | WSJT-X Target | WSJT-X Reference |
|---|---|---|
| Settings | `%LOCALAPPDATA%\WSJT-X - Target\WSJT-X - Target.ini` | `%LOCALAPPDATA%\WSJT-X - Reference\WSJT-X - Reference.ini` |
| Logs and writable files | `%LOCALAPPDATA%\WSJT-X - Target\` | `%LOCALAPPDATA%\WSJT-X - Reference\` |
| Default saved audio | `%LOCALAPPDATA%\WSJT-X - Target\save\` | `%LOCALAPPDATA%\WSJT-X - Reference\save\` |

**Open these folders in File Explorer:** press **Windows+E**, then **Ctrl+L** to select the address bar. Type `%LOCALAPPDATA%` and press **Enter** to open your user account's local application-data folder. Open `WSJT-X - Target` or `WSJT-X - Reference`. You can also paste a complete folder path from the table into the address bar. You do not need to enable **Hidden items**.

Always launch the two instances with their named shortcuts. A different rig name creates a different set of locations. If your WSJT-X version uses different menus or paths, check its matching user guide <a href="#ref-12">[Ref-12]</a>.



<a id="sec-a-2"></a>
#### 4.2 Clone the starting configuration if required

**Optional:** configure **WSJT-X Target** first using [4.3](#sec-a-3), then copy its configuration so **WSJT-X Reference** starts with the same settings. Otherwise configure both instances directly in 4.3.

1. Close **all** WSJT-X instances and retain a backup of any settings you intend to replace.
2. Copy the Target settings file `%LOCALAPPDATA%\WSJT-X - Target\WSJT-X - Target.ini` into the Reference folder `%LOCALAPPDATA%\WSJT-X - Reference\`.
3. Rename the copy to `WSJT-X - Reference.ini`, replacing the newly initialized Reference file only if that is your intention.

The resulting Reference settings file must be `%LOCALAPPDATA%\WSJT-X - Reference\WSJT-X - Reference.ini`. Cloning also copies hardware, directory and station settings; complete every applicable check below on **both** instances before starting reception.

**Reusing an existing configuration:** you can first seed **WSJT-X Target** with the settings you already use, following the same close, back up, copy and rename procedure. For an existing default configuration, the source file is `%LOCALAPPDATA%\WSJT-X\WSJT-X.ini`; copy it into the Target folder and name it `WSJT-X - Target.ini`. You can then clone Target to Reference as above.



<a id="sec-a-3"></a>
#### 4.3 Separate every data path

Open **WSJT-X Target** and **WSJT-X Reference** in turn and check the following for their respective physical paths. A copied configuration can still select the Target's audio or radio in the Reference instance.

| Check | What to set or verify |
|---|---|
| **Audio input** | In **File > Settings > Audio**, select the intended receiver's **Input**. If independent paths share a stereo audio interface, select the correct channel for each instance. |
| **Audio format** | Configure the Windows audio device for **48 000 Hz, 16-bit** sampling, as specified by the WSJT-X guide. Disable Windows audio enhancements for these devices. |
| **Radio control** | In **File > Settings > Radio**, use the intended radio and control connection. Select **None** when this audio-only setup does not need CAT control, and manually tune the receiver or SDR to the matching WSPR USB dial frequency. |
| **Saved audio** | Set **Save Directory** to `%LOCALAPPDATA%\WSJT-X - Target\save\` for Target and `%LOCALAPPDATA%\WSJT-X - Reference\save\` for Reference. |
| **AzEl output, if used** | Give **AzEl Directory** its own location: `%LOCALAPPDATA%\WSJT-X - Target\` for Target and `%LOCALAPPDATA%\WSJT-X - Reference\` for Reference. This output is used by the Astronomical Data feature; it is not required for WSPR analysis. |
| **Reporting identity** | In **File > Settings > General**, enter each instance's exact reporting identity in **My Call** and that receiver setup's truthful locator in **My Grid**. Use the two-callsign or one-callsign choice below; the identities must remain distinguishable in the database. |
| **WSPR operation** | Select **Mode > WSPR** and the intended band, enable **Monitor**, check the audio level and decoder settings, leave **Enable Tx** off for this RX experiment, and enable spot uploading. |
| **Time** | Check that the computer is synchronized to UTC within ±1 second. Instances on the same PC share its clock; separate PCs each need synchronization. |

These settings and the instance-specific paths follow the WSJT-X guide <a href="#ref-12">[Ref-12]</a>.

<a id="sec-rx-reporting-identities"></a>
<blockquote class="setup-important">
<p class="setup-important-lead"><strong>Choose the RX reporting identities.</strong> If two appropriate callsigns are available, use one for each receive path. With one base callsign, use two distinct reporting suffixes, for example <code>CALL/1</code> for Target and <code>CALL/2</code> for Reference. Replace <code>CALL</code> with your actual base callsign and confirm that the reporting service accepts and retains both exact identities. Enter each receiver's actual locator; colocated setups normally share it, while receivers at different sites retain their own locations.</p>
<p>WSJT-X sends the <strong>receiver's reporting identity over the internet</strong> with each uploaded spot. A suffix here does not change the remote transmitter's WSPR message and does not require extra on-air transmissions. Keep <strong>Enable Tx</strong> off for this RX setup. For an on-air compound callsign, use the TX route in <a href="#sec-tx-one-callsign-two-suffixes">Section 5.1.2</a>; acceptance of an RX reporting label does not establish its validity for transmission <a href="#ref-12">[Ref-12]</a>.</p>
</blockquote>

**Ready for an RX test:** both instances receive the intended independent streams and upload under the correct identities on the selected band. Confirm the hardware routing empirically; separate folders alone do not prove separate RF paths. Check that the reports reach the database selected in WSPRadar, allowing for [upstream delay](#sec-6-6).

If the comparison needs a measured receiving-chain correction, continue with [Chapter 6](#sec-reference-snr-calibration). Otherwise use the [RX Benchmark procedure](#sec-3-rx-benchmark) with the documented setup.



<a id="sec-a-4"></a>
#### 4.4 Limitations of WSJT-X for simultaneous TX

**Matching clocks do not create a common transmit schedule.** In ordinary WSPR operation, WSJT-X chooses transmit periods randomly according to **Tx Pct**. Two instances set to the same value below `100%` can coincide in some cycles, but that setting does not guarantee a synchronized sparse A/B schedule <a href="#ref-12">[Ref-12]</a>.

With transmission enabled, `Tx Pct = 100%` makes both instances attempt every cycle. A WSPR-2 message lasts about **110.6 seconds** of the 120-second cycle, giving an approximately **92%** <strong class="defined-term">RF key-down duty cycle</strong> — the fraction of time the transmitter is actually emitting RF <a href="#ref-8">[Ref-8]</a>.

WSPRadar recommends using about **5–20% of available cycles** for this experiment, with the lower end preferred on busy bands or during longer tests. This is an operating recommendation, not a WSPR protocol limit. A percentage of selected cycles and the RF key-down duty cycle are different quantities.

To transmit together in only selected cycles, use hardware with a fixed schedule and verify its actual starts. [Chapter 5](#sec-simultaneous-tx-setup) gives routes for QMX/QMX+ Virtual U3S, Ultimate3S, and a model-specific ZachTek configuration procedure using standard firmware.



<div style="page-break-before: always;"></div>

<a id="sec-simultaneous-tx-setup"></a>
### 5. Simultaneous TX Reference Setup

**Goal:** transmit two distinguishable signals from the Target and Reference paths in the same WSPR cycles, using either two setups at one station or two coordinated stations. Remote receivers can then report both signals in the same cycles for a TX Benchmark. The result compares the complete documented paths, including any equipment differences left uncontrolled.

Use this order of work:

| Stage | Action |
|---|---|
| **1. Plan** | Choose valid transmitting identities and a matching message pattern in [5.1](#sec-simultaneous-tx-setup-1). Record which identity belongs to each physical path. |
| **2. Configure** | Follow the recipe for your hardware in [5.5](#sec-simultaneous-tx-setup-5). For QRP Labs, start with one enabled entry using your chosen callsign route. The ZachTek route uses the model-specific standard configuration before the bench checks. |
| **3. Check on the bench** | Verify timing and signal placement in [5.2](#sec-simultaneous-tx-setup-2), then actual power and simultaneous signal quality in [5.3](#sec-simultaneous-tx-setup-3). |
| **4. Check the reports** | Complete a short on-air and database preflight in [5.4](#sec-simultaneous-tx-setup-4), then open the measurement window. |
| **5. Confirm the finding** | Repeat with exchanged frequency positions or hardware assignments as described in [5.6](#sec-simultaneous-tx-setup-6). |

Use callsigns and operating conditions valid for your station and licence. Complete RF safety, filtering and isolation checks appropriate to the hardware before connecting antennas.



<a id="sec-simultaneous-tx-setup-1"></a>
#### 5.1 Choose the callsigns

Choose the route that matches the callsigns available for the experiment. Target and Reference can be two setups at one station or two coordinated stations. Keep each complete callsign attached to its documented physical path throughout the experiment.

**Reporting callsigns in RX and transmitting them in TX work differently.** An [RX reporting suffix](#sec-rx-reporting-identities) is uploaded over the internet. In TX, the callsign must be encoded in the radiated WSPR message, so an ordinary or compound callsign determines the message sequence needed <a href="#ref-12">[Ref-12]</a>.

<a id="sec-tx-two-distinct-callsigns"></a>
##### 5.1.1 Two distinct callsigns

Use this route when two different callsigns are valid for the intended operation and **both fit the ordinary <strong class="defined-term">Type 1</strong> WSPR format**. Each transmission carries its callsign, a four-character locator (<strong class="defined-term">grid-4</strong>) and reported power together.

| Arrangement | Callsigns and locations |
|---|---|
| **Two setups at one station** | Assign one valid callsign to Target and the other to Reference. Report the common physical QTH truthfully. |
| **Two stations** | Each station uses its own valid callsign and actual QTH. Coordinate the band, selected cycles and message pattern; the result includes the different sites and propagation paths. |

Disable extended messaging on both units for the one-message route. On the cited ZachTek firmware, explicitly select **no prefix/suffix** and use `LocationPrecision = 4`. A normal base callsign alone does not disable an existing suffix selection, and precision `6` adds a second transmission even after an ordinary Type 1 message. Match the **actual transmitted pattern**, not just the callsign format.

Open the [QMX/QMX+ or Ultimate3S recipe](#sec-simultaneous-tx-setup-5-1) or [ZachTek recipe](#sec-simultaneous-tx-setup-5-3), complete its shared preparation, then choose **Two distinct callsigns**.

<a id="sec-tx-one-callsign-two-suffixes"></a>
##### 5.1.2 One callsign with two suffixes

Use this route when you have one base callsign and need to distinguish two transmitting setups with two valid compound callsigns. For example, `CALL/1` and `CALL/2` illustrate the pattern; replace `CALL` with your actual base callsign. Use only suffixes permitted for the operator, station and operation and supported by the selected firmware. Do not invent an on-air suffix merely as a hardware label.

The firmware generates the extended sequence automatically:

| Message | Information carried |
|---|---|
| <strong class="defined-term">Type 2</strong> | The complete compound callsign and reported power, without a locator. |
| <strong class="defined-term">Type 3</strong> | The six-character locator (<strong class="defined-term">grid-6</strong>) and reported power, with a compact callsign code (a <strong class="defined-term">hash</strong>) that the receiver must associate with the full callsign. |

Reserve **two consecutive two-minute slots** for each complete sequence. Align both transmitters' Type 2 phases with each other and both Type 3 phases with each other. WSPRadar still compares the reports from each individual two-minute cycle; it does not combine the sequence into one four-minute observation.

Open the [QMX/QMX+ or Ultimate3S recipe](#sec-simultaneous-tx-setup-5-1) or [ZachTek recipe](#sec-simultaneous-tx-setup-5-3), complete its shared preparation, then choose **One callsign with two suffixes**.

**For both routes:** enter each setup's truthful locator. Colocated paths normally share a locator; distinct stations must retain their own locations. Do not mix a one-cycle pattern on one path with a differently scheduled two-cycle pattern on the other: the extra phase can create one-sided evidence through the setup itself. Check the [identity rules](#sec-7-spots-identities-cycles) and [hash limitations](#sec-7-benchmark-outcomes) before using extended WSPR <a href="#ref-12">[Ref-12]</a> <a href="#ref-29">[Ref-29]</a>.




<a id="sec-simultaneous-tx-setup-2"></a>
#### 5.2 Align the schedule and separate the signals

After applying the [hardware recipe](#sec-simultaneous-tx-setup-5), verify the pair together:

1. **Time and band:** synchronize both transmitters to accurate UTC, preferably satellite time such as GPS, and select the same band.
2. **Selected cycles:** use the same deterministic recurrence and verify the same even-minute starts. Both paths must transmit complete messages in each intended comparison cycle.
3. **Sequence phases:** when extended WSPR is enabled, verify corresponding phases together, including after a restart. Matching the first phase alone is insufficient.
4. **Frequency separation:** for the fixed-frequency QRP Labs examples, place the signal centers nominally **100 Hz apart**, with both complete signals comfortably inside the 200 Hz WSPR transmit sub-band. The ZachTek route instead uses standard frequency randomization as described in [5.5.2](#sec-simultaneous-tx-setup-5-3); it does not guarantee a minimum separation.

Use the worked 40 m or 20 m settings in [5.5.1](#sec-simultaneous-tx-setup-5-1). Those settings specify **radiated RF frequencies**, not a receiver's USB dial frequencies. The cited QRP Labs manuals define the WSPR setting as the signal center; the cited ZachTek firmware uses the lowest tone, or <strong class="defined-term">tone 0</strong>. Use the convention for your exact firmware <a href="#ref-12">[Ref-12]</a> <a href="#ref-29">[Ref-29]</a>.

Check individual frequencies with suitable measurement equipment, then use a receiver waterfall or spectrum display to inspect both signals together. For fixed-frequency setups, confirm the intended separation; for ZachTek's standard randomization, inspect frequency placement over several sequences and investigate persistently identical selections. In both cases, check the complete signals' edge margins. Increasing fixed-frequency separation reduces those margins. Repeat the timing and frequency checks after a restart, firmware update or configuration change.



<a id="sec-simultaneous-tx-setup-3"></a>
#### 5.3 Check power and simultaneous signal quality

**Measure physical power first; then configure its reported value.** The WSPR dBm field describes power. Entering a different value does not itself set the transmitter's RF output.

1. **Choose the measurement point.** Decide whether the comparison includes feedline or other path losses, and record where power is measured. Use a consistent basis for both paths.
2. **Set and measure each transmitter separately.** Use a suitable dummy load or a safely attenuated measurement path. Adjust actual output with the equipment's supported method or suitable external attenuation. WSPRadar recommends about **100 mW–1 W (20–30 dBm)** for this test; use no more than it needs. Keep the actual-power measurement in the experiment record.
3. **Enter truthful reported power.** Use the nearest valid WSPR-encoded value. In this range the choices are **20, 23, 27 and 30 dBm**, approximately **100 mW, 200 mW, 500 mW and 1 W**. Do not use false power values as A/B labels. On the cited ZachTek build, use **Normal** power reporting rather than altitude encoding <a href="#ref-12">[Ref-12]</a> <a href="#ref-29">[Ref-29]</a>.
4. **Test simultaneous operation.** For two colocated transmitters, operate both into loads and inspect their combined signals through suitable attenuated and isolated sampling connections. Check frequencies, occupied bandwidth, harmonics, spurious products and intermodulation. For transmitters at separate stations, complete the individual bench checks at each site and inspect simultaneous reception at a common receiver during the on-air preflight.

**Ready for the on-air preflight:** actual powers and their reporting basis are documented, the signals occupy the intended positions, and simultaneous operation introduces no identified defect that invalidates the comparison. A clean signal from each transmitter alone does not establish the quality of the simultaneous pair.



<a id="sec-simultaneous-tx-setup-4"></a>
#### 5.4 Verify WSPRnet and the selected database

Make a short test transmission sequence and check that the expected reports reach WSPRadar.

1. Transmit several complete synchronized sequences with the final callsign, QTH, power, schedule and frequency settings.
2. Search the [WSPRnet Spot Query](https://www.wsprnet.org/drupal/wsprnet/spotquery) for **each exact callsign**. Inspect reports, not only the map, which can show a last-known locator.
3. Check the intended grid-4, reported power, timestamps and distinct frequencies. Find cycles in which the **same remote receiver reported both callsigns**.
4. Run a short **TX Benchmark** with those identities, band and UTC window. Wait until the reports are available from the selected database. wspr.live describes delays of a few minutes; individual uploads and service availability can take longer. Proceed from actual data availability rather than a fixed waiting time; see [Section 11.6](#sec-6-6).
5. Inspect the counts of Paired and one-sided decodes, ΔSNR and ΔDecode calculated from the combined decode counts. Investigate unexpected concentrations of Only Target or Only Reference before treating them as a performance difference.

**For an extended sequence, check each phase separately.** Identify the sequence positions from their timestamps and your recorded schedule, using exported evidence or an external decoder log. Compare paired and one-sided counts, ΔSNR and ΔDecode between those positions. Persistent differences can prompt checks of callsign-hash resolution, frequency placement, heating and power sag. The database need not label Type 2 or Type 3, and WSPRadar does not supply message-phase labels or a phase filter.

**Ready to measure:** both exact identities appear consistently at their truthful locations, common receivers report both signals in the intended cycles, and unexplained phase or frequency-position effects have been investigated. Start a new measurement window after these checks. Successful preflight establishes data flow for the tested hardware, firmware, decoders and source; it does not by itself establish an antenna advantage.



<a id="sec-simultaneous-tx-setup-5"></a>
#### 5.5 Device-specific setup

Choose the recipe for your equipment below, then complete the common power and signal checks in [5.3](#sec-simultaneous-tx-setup-3) and the database check in [5.4](#sec-simultaneous-tx-setup-4). Record the firmware and settings that passed. Repeat those checks after changing firmware, timing, frequency, power or message format.



<a id="sec-simultaneous-tx-setup-5-1"></a>
<a id="sec-simultaneous-tx-setup-5-2"></a>
##### 5.5.1 QMX and QMX+ Virtual U3S, and Ultimate3S

Use one unit for the Target and one for the Reference. Both products support up to 16 entries, but **start with one WSPR entry on each unit**. That entry sends either one Type 1 message or an automatic Type 2/Type 3 pair, according to the callsign route below. Their RF hardware differs, so oscillator, filtering and output-stage differences remain part of the paths being compared <a href="#ref-12">[Ref-12]</a>.

First check the hardware and firmware below. Then choose [two distinct callsigns](#sec-qrp-two-distinct-callsigns) or [one callsign with two suffixes](#sec-qrp-one-callsign-two-suffixes). Both routes then use the [shared power, frequency and verification steps](#sec-qrp-common-setup).

**1. Check the hardware and firmware.**

The physical Ultimate3S referred to here is the kit with the Si5351A synthesizer. The original Ultimate3 with an AD9850 sends extended-WSPR messages in alternate transmission cycles rather than consecutively, so it is not an ideal candidate for the extended-message recipe below.

Use a band supported by both units. Check the QMX hardware variant and band configuration; on a physical Ultimate3S, fit/select the correct output low-pass filter.

For QMX/QMX+, the [official firmware history](https://www.qrp-labs.com/qmx.html) labels `1_04_010` the stable release as of **25 October 2026**; later listed releases are beta. The initial `1_04_000` was QMX+-only. Release `1_04_009` corrected WSPR transmission **250 Hz below the intended frequency**, and `1_04_010` includes further Virtual U3S fixes. Use a supported release with those corrections and check the history when updating.

The instructions here refer to the Virtual U3S manual for firmware `1_04_008` (document revision `1_04_008a`) and the Ultimate3S manual for firmware `v3.12a` (file `operation3.12a2.pdf`). Physical U3S firmware `v3.12` introduced consecutive extended-message transmission; do not assume older firmware behaves the same <a href="#ref-12">[Ref-12]</a>.

<a id="sec-qrp-two-distinct-callsigns"></a>
###### 5.5.1.1 Two distinct callsigns

Use this route for two valid ordinary callsigns, whether they identify two setups at one station or two separate stations, as described in [Section 5.1.1](#sec-tx-two-distinct-callsigns).

1. Enter each unit's own complete ordinary callsign in **Callsign**.
2. Enter each setup's truthful **six-character locator**. Type 1 transmits its first four characters.
3. On Virtual U3S, set **`Extended WSPR = DISABLED`**. On Ultimate3S, set **`XW = 0`**.
4. Use **entry `0` only**, mode **`WSPR`**, **`Frame = 20` minutes** and **`Start = 04`**, then complete the shared steps below.

With the single Type 1 entry, the expected starts are **`:04`, `:24` and `:44` each hour**. Each start should contain both signals. This uses **3 of the 30 two-minute cycles per hour: 10% cycle occupancy**.

<a id="sec-qrp-one-callsign-two-suffixes"></a>
###### 5.5.1.2 One callsign with two suffixes

Use this route for two setups identified by one base callsign and two valid suffixes, as described in [Section 5.1.2](#sec-tx-one-callsign-two-suffixes).

1. Enter the **complete suffixed callsign** in each unit's **Callsign** setting, for example `CALL/1` for Target and `CALL/2` for Reference. Replace `CALL` with your actual base callsign and use only valid on-air suffixes supported by the firmware.
2. Enter each setup's truthful **six-character locator**. Type 3 transmits all six characters.
3. On Virtual U3S, set **`Extended WSPR = ENABLED`**. On Ultimate3S, set **`XW = 1`** on both units.
4. Use **entry `0` only**, mode **`WSPR`**, **`Frame = 20` minutes** and **`Start = 04`**, then complete the shared steps below. Do not create separate entries for Type 2 and Type 3: supported firmware generates both automatically.

Allow **four minutes per entry**. The expected single-entry schedule is:

| Sequence position | Expected UTC minutes on both units |
|---|---|
| Type 2: complete compound callsign and power | `04, 24, 44` |
| Type 3: hashed identity, grid-6 and power | `06, 26, 46` |

When this recurrence is maintained, each transmitter uses **6 of the 30 two-minute cycles per hour: 20% cycle occupancy**. The Type 1 route's 10% figure does not apply. Keep both units on corresponding message phases and preserve the whole pair at one frequency before changing frequency. Verify the complete extended sequence and the resulting database identities before measuring <a href="#ref-12">[Ref-12]</a>.

<a id="sec-qrp-common-setup"></a>
###### 5.5.1.3 Shared power, frequency and verification steps

**Set actual power and one transmission entry.**

Edit TX column `0` in the Virtual U3S schedule table, or mode screen `0` on physical Ultimate3S.

Enter the callsign and truthful six-character locator specified by your chosen route. Keep each callsign attached to its Target or Reference path throughout the experiment.

For Virtual U3S, `PA Voltage` controls actual RF output: `6.0 V` is an approximate 1 W starting point on a 12 V-built QMX; other builds and bands differ. Measure the result. For substantially lower power, use suitable external attenuation and measure after it; the main QMX manual advises against trying to obtain less than about 1 W through voltage reduction alone. Set physical Ultimate3S output using its documented hardware arrangement or external attenuation.

Then enter the nearest valid encoded dBm value: `20`, `23`, `27` and `30 dBm` represent approximately `100`, `200`, `500 mW` and `1 W`. The Virtual U3S `Power/Speed` field and the Ultimate3S WSPR power field **report power in the message; changing them does not set RF output**. Follow [5.3](#sec-simultaneous-tx-setup-3) for the measurement plane <a href="#ref-12">[Ref-12]</a>.

| Setting | Starting value on both units |
| --- | --- |
| Enabled entries | Entry `0` only; disable every other entry |
| Mode | `WSPR` |
| Extended messages | Use the setting for your chosen callsign route above |
| `Frame` | `20` minutes |
| `Start` | `04` minutes |
| UTC | Correct and checked against the time reference |

Both products treat `Start = 00` as unused. Choose an explicit even start such as `04`.

Choose **one** band below. Initially put the Target at the lower frequency and the Reference at the upper frequency. Keep each frequency fixed for the complete message or extended pair. These settings are **RF signal-center frequencies**, not USB dial frequencies or the lowest WSPR tone.

| Band | Lower center | Upper center |
| --- | ---: | ---: |
| 40 m | `7.040050 MHz` | `7.040150 MHz` |
| 20 m | `14.097050 MHz` | `14.097150 MHz` |

The centers are 100 Hz apart; each is 50 Hz from its nearer edge of the 200 Hz WSPR sub-band. Confirm the complete radiated signals remain inside it <a href="#ref-12">[Ref-12]</a>.

On QMX, `Real time clock = Software` loses its time when power is removed; restore UTC from GPS or set it manually after power-up. On QMX+, retaining time while powered off requires `Real time clock = QMX+ Internal` and an installed CR2032 battery. This clock-source setting is separate from `GPS source`; selecting the internal GPS alone does not enable clock retention.

**Start, observe one hour, then collect the comparison.**

Verify UTC before starting. On Virtual U3S, set the main `Enable` to `ENABLED` and exit the menu; on Ultimate3S, use the right-button Start action to enter Run mode. Observe the schedule for your selected route above; both units must transmit corresponding phases together.

If using GPS frequency calibration, ensure it finishes before the next expected start.

For an internal QLG3 on QMX+, set `GPS source = QMX+ Internal`. For an external GPS on QMX, select `GPS source = Paddle port`, connect the 1 PPS signal to the jack tip and 9600-baud NMEA serial data to the ring, following the manufacturer's wiring instructions. Power the GPS module separately; QMX does not supply its power through this connector.

On physical U3S, calibration requires a nonzero `Cal Step` and an idle gap longer than `Cal Time + 4 seconds`; GPS connection alone does not establish successful calibration. For automatic UTC and locator setting as well as frequency calibration, connect both NMEA serial data and 1 PPS. In `GPS {Mode Baud}`, use `Mode = 2` for a receiver whose timing reference is the rising PPS edge, and set `Baud` to match its serial output, commonly `009,600`. PPS alone does not supply UTC or the locator.

Observe the transmitted frequencies and starts, including after a restart. Complete the individual-unit, simultaneous-signal and database checks in [5.3–5.4](#sec-simultaneous-tx-setup-3). Begin the measurement window only when both exact identities appear in the intended cycles and locations. Then repeat with the **frequency assignments exchanged**, following [5.6](#sec-simultaneous-tx-setup-6), so the result is not tied to a permanent lower/upper assignment.

**Optional: two-entry frequency exchange for the two-ordinary-callsign route.**

Keep the same callsigns, band and measured power, and enable two WSPR entries per unit:

| Entry | Target center | Reference center |
| --- | --- | --- |
| `0` | Lower | Upper |
| `1` | Upper | Lower |

Use `Frame = 20`, `Start = 04` as a **bench starting configuration**. Before using it, record a full hour's actual entry order and UTC starts on both units. The intended trace is entry 0 at `:04/:24/:44` and entry 1 at `:06/:26/:46`. **Only if that trace is observed** does the setup provide adjacent pairs and 6 of 30 cycles, or `20%` occupancy. The manuals do not provide this exact two-entry trace for every installed version; if entry 1 waits for a later frame, the frequency exchange also occurs later. Resolve that timing or return to the single-entry recipe.

Compare both frequency positions separately. Balanced use helps reveal or reduce a fixed frequency-position advantage from QRM or the equipment, but does not prove that every frequency effect has disappeared.

For the one-callsign/two-suffix route, use the between-run frequency exchange in [5.6](#sec-simultaneous-tx-setup-6). One extended entry already uses two cycles; adding a second extended entry changes the sequence length and occupancy, so the ordinary-route trace and 20% calculation above do not apply. Preserve the whole Type 2/Type 3 pair before changing frequency.



<a id="sec-simultaneous-tx-setup-5-3"></a>
##### 5.5.2 ZachTek firmware 2.19

This setup uses ZachTek's built-in scheduling and standard frequency randomization; **no custom frequency-lane firmware is required**. The worked example uses the pinned ESP8285 firmware in [Ref-29](#ref-29), revision `1657468ea27052167191a7deda2440a535567ecd`, which selects **WSPR-TX XP Plus, `Product_Model = 1048`**. Other models require a separately checked recipe. In this file, the Mini/Pico long-pause sleep call is disabled, and Pico startup forces altitude reporting; the pause and power instructions below therefore apply to the selected 1048 build.

Use the configuration software for your exact hardware and installed firmware. The parameter names below follow the cited source; they are not instructions to edit or compile firmware. **This recipe has not been validated by WSPRadar on ZachTek hardware.** The manufacturer's clarification supports using the standard scheduling and randomization functions; it is not a validation of every model-specific setting below.

Choose the route that matches the **on-air transmitting identities** you will use:

| Route | Identities and message pattern |
|---|---|
| [**1. Two distinct callsigns**](#sec-zachtek-two-ordinary-callsigns) | Two distinct valid Type 1 callsigns, used by two setups at one station or by two stations. Each scheduled sequence contains one transmission per setup. |
| [**2. One base callsign with two suffixes**](#sec-simultaneous-tx-setup-5-3-2) | One base callsign with two distinct permitted single-character suffixes. Each scheduled sequence contains a Type 2/Type 3 pair per setup. |

**Both routes require the same preparation:** enable only the selected test band, set **`PowerOption = Normal`**, and use each transmitter's truthful QTH. Both units need valid GPS time **and location**, including when the transmitted locator is entered manually. Normal power reporting uses the configured dBm as message data; it does not set RF output power. Altitude mode replaces that value with telemetry. Before on-air use, measure actual power and choose its encoded value as described in [Section 5.3](#sec-simultaneous-tx-setup-3).

Two colocated setups should report their common physical QTH. At two different stations, each transmitter reports its own QTH; the result compares complete installed stations and their different propagation paths. Record which complete callsign and locator belong to each physical signal path.

After configuring either route below, complete the shared **timing → bench → on-air** procedure in [Section 5.5.2.3](#sec-simultaneous-tx-setup-5-3-1). Keep standard frequency randomization on both units; no lower/upper frequency-lane assignment is needed.

<a id="sec-zachtek-two-ordinary-callsigns"></a>
###### 5.5.2.1 Two distinct callsigns

Use this route when the Target and Reference each have a different valid callsign that fits the ordinary Type 1 WSPR format. The callsigns can identify two permitted setups at one station or two separate stations; they do not need suffixes to become distinguishable.

**Configure both units:**

1. Enter the Target's ordinary callsign in the Target unit's base-call field, and the Reference's different ordinary callsign in the Reference unit's field.
2. Explicitly select **no prefix/suffix** (`SuPreFixOption = None` in the cited source). Do this even if the displayed base call is already ordinary: changing that text alone does not disable a previously selected suffix or prefix. Stored suffix characters can remain unused; the selector is what chooses Type 1.
3. Set **`LocationPrecision = 4`** on both units. Precision `6` would add a Type 3 transmission even with an ordinary callsign.
4. Enable the same single test band, use **`PowerOption = Normal`**, retain each unit's truthful QTH, and set **`TimeSlotCode = 7`** and **`TXPause = 480` seconds** on both.
5. Keep standard frequency randomization on both units and continue with [Section 5.5.2.3](#sec-simultaneous-tx-setup-5-3-1). Keep the callsigns attached to their documented physical paths.

The intended schedule repeats every twenty minutes:

| UTC minute in each hour | Target | Reference |
|---|---|---|
| `04, 24, 44` | Type 1: its callsign, grid-4 and power | Type 1: its callsign, grid-4 and power |
| `06, 26, 46` | No additional phase in this route | No additional phase in this route |

When this recurrence is maintained, each transmitter uses **3 of 30 WSPR cycles per hour: 10%** of the available cycles. `TXPause` starts after each Type 1 transmission; it does not schedule extra transmissions at eight-minute intervals. Confirm the actual starts, then perform the shared bench and database checks before beginning the measurement window. <a href="#ref-29">[Ref-29]</a>

<a id="sec-simultaneous-tx-setup-5-3-2"></a>
###### 5.5.2.2 One callsign with two suffixes

Use this route when two transmitting setups use one base callsign with two distinct valid suffixes. For example, `CALL/1` and `CALL/2` illustrate the identity pattern; replace `CALL` with your actual callsign and use only suffixes permitted for the operator, station and operation. In this pinned firmware, use **single-digit or single-letter suffixes**.

**Configure both units:**

1. Enter the same base callsign in each unit's base-call field, without the slash or suffix.
2. Select the **suffix option** on both units (`SuPreFixOption = Sufix` in the source). Enter a different permitted single-character suffix in each unit's separate suffix field. Record which complete on-air identity belongs to Target and which belongs to Reference.
3. Set **`LocationPrecision = 6`** on both units. This adds Type 3 after Type 2 automatically; precision `4` would send Type 2 alone. You do not switch the message types by hand.
4. Enable the same single test band, use **`PowerOption = Normal`**, retain each unit's truthful QTH, and set **`TimeSlotCode = 7`** and **`TXPause = 480` seconds** on both.
5. Keep standard frequency randomization on both units and continue with [Section 5.5.2.3](#sec-simultaneous-tx-setup-5-3-1). Keep the complete suffixed callsigns attached to their documented physical paths.

The intended schedule repeats every twenty minutes:

| UTC minute in each hour | Target | Reference |
|---|---|---|
| `04, 24, 44` | Type 2: its complete suffixed callsign and power | Type 2: its complete suffixed callsign and power |
| `06, 26, 46` | Type 3: its hashed identity, grid-6 and power | Type 3: its hashed identity, grid-6 and power |

When this recurrence is maintained, each transmitter uses **6 of 30 WSPR cycles per hour: 20%** of the available cycles. Both phases use the same selected frequency within that sequence. The second message follows a fixed nine-second pause after the first finishes; it does not receive a separate GPS-slot start check. The configured `TXPause` follows the complete pair, not the gap between its two phases.

**Keep the source limitations in view.** The Type 3 hash construction for two-digit suffixes is disabled. The prefix-based Type 3 path also rebuilds its callsign string without writing the terminating zero before hashing, so it is not a reliable recipe in this revision. The single-character-suffix route above uses the implemented construction path. <a href="#ref-29">[Ref-29]</a>

Observe corresponding Type 2 and Type 3 phases together, including after a restart. Verify both complete identities in the receiver/database evidence for both phases through [Section 5.4](#sec-simultaneous-tx-setup-4). Matching configuration values alone do not establish correct hash resolution or complete synchronized transmissions.

<a id="sec-simultaneous-tx-setup-5-3-1"></a>
###### 5.5.2.3 Shared timing, frequency randomization and verification

**Keep the schedule and pause consistent.** Both worked routes use code `7`. If you choose a different fixed start, match `TimeSlotCode` on both units and use the following rules:

| `TimeSlotCode` | First-message schedule, when ready |
|---|---|
| `0–4` | Repeats every 10 minutes. Code `0`: `00, 10, 20, 30, 40, 50`; code `1`: `02, 12, 22, 32, 42, 52`; through code `4`: `08, 18, 28, 38, 48, 58`. |
| `5–14` | Repeats every 20 minutes. Code `5`: `00, 20, 40`; code `6`: `02, 22, 42`; code `7`: `04, 24, 44`; through code `14`: `18, 38, 58`. |

`TXPause` is a delay in **seconds after the enabled-band loop**, not a start-to-start period. With one band enabled, it follows each complete one- or two-message sequence. Leave enough time to finish, pause and become ready for the next scheduled start. An eight-minute pause after a two-message sequence can skip the next ten-minute start; the twenty-minute worked schedules leave room for their messages and that pause.

Use the fixed codes above for these recipes. Code `16` allows the next available even-minute start; code `17` responds to a changed location or the top of an hour. Neither establishes the selected fixed recurrence used here. Frequency randomization does not select the time slots, so check both actual starts during preflight. <a href="#ref-29">[Ref-29]</a>

**Use standard frequency randomization.** Stock firmware draws an integer offset from **−100 through +99 Hz** around the band's nominal frequency. Keep this standard behavior on both units rather than assigning separate frequency lanes. <a href="#ref-29">[Ref-29]</a>

According to **Harry Zachrisson (ZachTek, personal communication)**, each unit seeds its random-number generator at startup using **thermal noise sampled by the built-in analog-to-digital converter (ADC)**. This is noise-based seeding, not temperature measurement. It is intended to give the transmitters different frequency sequences even when they start at the same time; matching the transmission schedule does not force matching frequency selections.

**Occasional overlap remains possible.** Different seeds do not guarantee different frequencies in every sequence. Assuming independent, uniform selection among the 200 one-hertz offsets in this source, the probability of choosing **exactly the same offset is 0.5% per new selection**; offsets **no more than 5 Hz apart occur with approximately 5.4% probability**. These calculated examples describe frequency proximity between the two test transmitters, not a measured interference rate, a safe spacing threshold or an estimate of SNR error. Independent randomization makes persistently identical frequency sequences unlikely, but does not guarantee a minimum separation.

The offsets are relative to the **center** of the 200 Hz WSPR transmit sub-band: for example, `7.040100 MHz` on 40 m or `14.097100 MHz` on 20 m. Confirm that both units use the same correct nominal frequency. In this firmware, `freq` is **tone 0**, the lowest of the four transmitted tone frequencies, and uses **0.01 Hz units**. Oscillator error, drift and actual spectral width still require measurement. <a href="#ref-29">[Ref-29]</a>

Each new sequence draws a frequency position again; consecutive draws **can repeat**. When precision `6` adds Type 3, that partner uses the **same selected frequency** as the preceding Type 1 or Type 2 message. The next draw occurs after the next `NextFreq()`; offsets do not accumulate. <a href="#ref-29">[Ref-29]</a>

**Keep a configuration record.** Check the exact hardware model and revision, factory oscillator calibration, and installed filter configuration. Record the installed firmware version and all settings used in the experiment. The cited source selects model `1048`; do not install that build on a different model merely to reproduce this example. Retain the manufacturer's firmware for your hardware.

**Check on the bench, then on air.** After configuring, test each unit separately into suitable loads or a safely attenuated measurement arrangement; for colocated units, also test both together. Check actual frequency placement, complete message timing, output power, filtering and spectral purity before connecting antennas. For units at separate stations, inspect simultaneous reception during the subsequent common-receiver on-air preflight. Use the same PC-control conditions planned for the run; control commands can interrupt a transmission in this firmware.

Complete [Section 5.4's database preflight](#sec-simultaneous-tx-setup-4) at the intended low on-air power. Confirm that both identities use the intended band, that frequency positions vary over a series of sequences, and that common receivers produce pairs in the intended cycles. Repeat the start and frequency checks after a restart. Investigate persistently identical frequency selections or unexpected timing before beginning the measurement window.

**Confirm by repetition or hardware crossover.** Both units use the same randomization range, so there are no fixed lower/upper frequency assignments to reverse. Use a new measurement window and, where practical, exchange the tested antennas or components between transmitter chains while recording which reported station corresponds to each component. Use [Section 5.6](#sec-simultaneous-tx-setup-6) to document the repeated or crossed setup.



<a id="sec-simultaneous-tx-setup-6"></a>
#### 5.6 Confirm by exchange or crossover

Use the first run to identify a pattern worth confirming. For the next physical run, use a **new UTC window** with comparable duration and time-of-day coverage. Retain the intended band, schedule, powers, filters and primary evaluation scope, and record any unavoidable changes.

| Control | What to change | What it helps distinguish |
|---|---|---|
| **Frequency exchange** | For setups with controllable frequency assignments, exchange the lower and upper fixed positions while retaining the documented physical paths. | An effect following frequency position, such as narrowband interference, receiver passband response or frequency-dependent transmitter behavior. |
| **Hardware crossover, where practical** | Exchange the antennas or tested components between transmitter chains. Record the identity-to-component mapping for every run. | An effect following the tested component versus one following the transmitter chain. |

For a QRP Labs setup already using verified within-run frequency swapping, retain the per-position check and use a separate repetition or hardware crossover for confirmation. For the ZachTek standard-randomization route, use a separate repetition or hardware crossover; there are no fixed lane assignments to exchange.

Preserve the original, frequency-exchanged and hardware-crossover results separately. Pool them only when Target/Reference roles, correction signs and analysis scopes have been aligned. Keep the setup and operating records described in [Section 9.3](#sec-8-3).

Agreement in a new controlled run supports experimental repeatability. Agreement between two message phases within one run is within-run consistency. Propagation can still differ between runs; interpret the confirmation in the context of what was controlled.



<div style="page-break-before: always;"></div>

<a id="sec-b"></a>
<a id="sec-reference-snr-calibration"></a>
### 6. Reference SNR Calibration

**Goal:** establish a stable reported-SNR offset between **two receive chains supplied from a common input**, then validate it independently. Decide what the experiment should correct: unequal downstream receive chains may need correction when comparing antennas; subtracting that difference when the receivers themselves are under test could remove the result being measured. A shared-antenna example appears in <a href="#ref-2">[Ref-2]</a>.

This receiver-splitter procedure does not establish a TX correction. TX needs an independently established basis appropriate to its transmit paths and truthful power reports; see [Section 8.2.2](#sec-7-benchmark-delta).

1. **Define the calibration boundary.** Record the <strong class="defined-term">reference plane</strong>: the corresponding connection point in each chain where the common input is applied. List the downstream cables, filters, amplifiers, receiver and decoder settings. Keep each exact Target or Reference reporting identity attached to its documented physical chain.
2. **Provide a common input.** Feed both chains simultaneously from one stable antenna through a suitable splitter and controlled cables. Characterize output imbalance and cable differences, and record the feed-arm assignments. Nominal splitter loss alone is not an SNR correction.
3. **Collect uncorrected evidence.** In RX Benchmark, choose **Reference SNR correction → No correction**, which applies **0.0 dB**. Verify simultaneous reception and uploads, then collect pairs on the intended band across relevant signal levels with unchanged gain, filtering and decoder settings. When practical, also record a control run with the splitter feed arms exchanged, keeping identities with their receiver chains.
4. **Choose and record the summary.** Use the ΔSNR summaries in **Benchmark Statistics** for the documented calibration period, filters and scope. Record both statistic and weighting: the **median of station-median ΔSNR** and the **mean of station-mean ΔSNR** give every included station equal weight; a **pooled median or mean of qualifying spot pairs** gives every included pair equal weight. Record station and pair counts and use the same summary definition for validation. WSPRadar does not determine the correction automatically.
5. **Check that one constant is justified.** Inspect differences by station, time and SNR, and across the frequencies and settings where the correction will be used. Investigate a difference that follows the splitter feed arm. A constant is not defensible if it changes materially with level, frequency, AGC, equipment state or time. Resolve fixture imbalance, clipping, unstable gain or intermittent routing, and recheck after changes to the calibrated setup.
6. **Apply the sign.** Choose **Use a documented correction** and enter the value in **Reference-side SNR correction (dB)**. For an uncorrected Target-minus-Reference offset of **+1.6 dB**, enter **+1.6 dB**: Reference SNR rises and ΔSNR falls by 1.6 dB. Enter a negative offset with its negative sign. A documented **0.0 dB** remains distinct from **No correction**. Correction changes ΔSNR, not decode counts, ΔDecode or raw cumulative-SNR curves.
7. **Validate with new evidence.** Keep the correction fixed and collect a separate common-input period with the same chain definitions and settings. Check for a corrected summary plausibly near zero and consistency across stations, time and SNR; record residual offset and variation. Zero obtained from the same observations used to estimate the offset is not independent validation. Keep identities with their chains during feed-arm exchanges. If only the Target and Reference roles of the same calibrated chains are exchanged, negate the correction and update the identity mapping.

**Ready to proceed:** the fixture checks support the comparison, the offset is stable for the intended conditions, and separate validation supports using it. Reconnect the experimental inputs at the recorded reference planes, preserve the calibrated chains and settings, then return to [Section 1.2](#sec-2-2).

**Calibration record:** keep exact identities and physical-chain mapping; band, reference plane, settings and splitter/cable assignments; calibration periods, filters and scope; statistic, weighting and station/pair counts; estimated offset, applied signed value and independent validation residuals. Save the uncorrected, optional feed-arm-control and validation runs separately. [Section 9.3](#sec-8-3) gives the full experiment record.

Repeatability supports one additive offset within the tested arrangement, not traceable laboratory accuracy. Splitter loss, mismatch, coupling, cable effects and source instability can remain. A geographically separate Reference can provide a repeatable baseline for that pair, band and setup, but not this common-input calibration or an absolute calibration.

<div style="page-break-before: always;"></div>

<a id="part-iii"></a>
## Part III: Scientific Foundations, Methods and Claims

Part III explains how WSPRadar turns reception reports into evidence and what conclusions that evidence supports. It is written for radio amateurs who want to understand the calculations, with formulas and worked examples for checking them.

For the calculations, start with [Chapter 8](#sec-7): what counts as an observation, which observations qualify, and what receives equal weight in each summary. [Chapter 7](#sec-d) connects the approach to earlier amateur and scientific work. [Chapter 9](#sec-8) explains how to state and preserve a result. The same details also support HamSCI contributors and reviewers.


<a id="sec-d"></a>
### 7. Literature, Prior Art and Positioning

WSPR experimentation rests on contributions from radio amateurs, researchers, software developers and the volunteers who operate the reporting network. Earlier work established practical ways to compare installations, investigate reception problems and study propagation.

This chapter gives selected contributors credit for their methods and findings. The **Use in WSPRadar** statements explain our design relationship to that work; they are our interpretations, not endorsements by the cited authors. A technical report, a controlled experiment and a software service contribute different kinds of evidence.

Three lessons recur: compare under shared conditions, establish activity before interpreting silence, and examine the complete station before attributing a difference to its antenna.


<a id="sec-d-1"></a>
#### 7.1 From reporting network to experimental dataset

<a id="sec-d-taylor-walker"></a>
##### 7.1.1 Joe Taylor, K1JT, and Bruce Walker, W1BW: a shared experimental resource.

Taylor introduced WSPR in 2008; Walker developed WSPRnet to collect and share reception reports. Their 2010 article showed how those reports could support propagation experiments. One example grouped three weeks of 30 m observations into 15-minute UTC intervals: averaging revealed recurring reception patterns that were difficult to judge from individual transmissions. Station operators supplied the distributed observations, while the protocol, software and reporting service made them accessible. The reports still reflected the participating equipment, locations and operating schedules. <a href="#ref-6">[Ref-6]</a>

> **Use in WSPRadar:** preserve this connection between reported observations and the question being asked. Geographic and time summaries organize the evidence, while the selected period and participating stations remain part of its meaning.

<a id="sec-d-frissell"></a>
##### 7.1.2 Nathaniel Frissell and collaborators: amateur observations in space science.

Their 2019 study compared amateur-network reports during the September 2017 solar activity with a quiet-time baseline. It identified HF communication blackouts associated with flares and changes during geomagnetic disturbances, using the baseline to distinguish event responses from ordinary variations. <a href="#ref-13">[Ref-13]</a>

Their 2022 study used WSPRnet, Reverse Beacon Network and PSKReporter observations from 3 November 2017. Approximately 2.5-hour fluctuations in communication distance agreed with SuperDARN radar and satellite-navigation measurements of ionospheric electron content, supporting an interpretation as large-scale traveling ionospheric disturbances. The independent measurements were part of the evidence for that physical explanation. <a href="#ref-14">[Ref-14]</a>

Their 2023 review places these amateur networks alongside purpose-built scientific instruments and recommends cross-calibration between networks. It recognizes the scientific value of accumulated observations without treating every contributing receiver as a calibrated instrument. <a href="#ref-7">[Ref-7]</a>

> **Use in WSPRadar:** examine geographic and temporal structure in context, then use independent observations or a controlled experiment to test a physical explanation. WSPRadar's plots help formulate and inspect such questions; they do not themselves identify an ionospheric cause.


<a id="sec-d-2"></a>
#### 7.2 Making observational WSPR data interpretable

<a id="sec-d-lo"></a>
##### 7.2.1 Lo and collaborators, 2022: establish activity before interpreting silence.

Their study used a full year of 2017 observations on 7 MHz between Europe and Australasia. Half-hour activity checks asked whether a transmitter was heard elsewhere and whether a receiver heard other stations. Reception from the UK to New Zealand occurred around UK sunrise and sunset; reception in the reverse direction was concentrated around UK sunrise, with UK-sunset reception especially sparse in summer. The authors proposed higher European evening noise as a possible explanation, rather than treating the asymmetry as propagation evidence alone. <a href="#ref-9">[Ref-9]</a>

> **Use in WSPRadar:** apply the activity-check principle when defining Performance opportunities. WSPRadar's own same-cycle rules establish which endpoints have activity evidence; they are a separate design choice from the study's half-hour checks. Missing reports without the required evidence remain unknown outcomes.

<a id="sec-d-griffiths-robinett-elmore"></a>
##### 7.2.2 Gwyn Griffiths, G3ZIL, Rob Robinett, AI6VN, and Glenn Elmore, N6GN, 2019–2020: measure noise alongside reception.

Their 2019 report compared noise estimates from gaps between WSPR transmissions with frequency-domain estimates made during reception, and investigated calibration to the receiver's antenna input. At KPH, the 40 m noise record showed a daily minimum around local noon and greater evening/night variability. These measurements added information that ordinary SNR reports could not supply. The work was subsequently published in QEX in September/October 2020. <a href="#ref-15">[Ref-15]</a> <a href="#ref-16">[Ref-16]</a>

> **Use in WSPRadar:** interpret an SNR change as a change in the signal-to-noise relationship. WSPRadar does not independently measure noise; distinguishing stronger signals from lower noise requires additional measurements or controlled station tests.


<a id="sec-d-3"></a>
#### 7.3 Antenna and station-comparison lineage

<a id="sec-d-destrem"></a>
##### 7.3.1 Patrick Destrem, F6IRF, 2008: automated switching and geographic comparison.

Destrem alternated a 30 m vertical and inverted-V every ten minutes and corrected reports to a common transmit power. These were <strong class="defined-term">interleaved measurements</strong>: the antennas were tested in alternating periods. He examined individual receivers and distance groups. The vertical's reported average advantage was about 4 dB on one approximately 14 000 km path, while the antennas were approximately equal on a 2 000 km path. The result depended on the path and installation; sequential measurements remained exposed to changing propagation. His follow-ups extended the investigation to reception and comparisons between stations. <a href="#ref-17">[Ref-17]</a>

> **Use in WSPRadar:** credit the early combination of power correction and geographic inspection. Compare directions and distances explicitly, while using concurrent pairs for ΔSNR and retaining one-sided reports as separate evidence.

<a id="sec-d-preston"></a>
##### 7.3.2 Charles Preston, KL7OA, later K7TAA, 2009 and 2017: simultaneous comparison.

Preston's March 2009 preliminary experiment used two colocated 2 W transmitters, a Buddipole and a horizontal loop on 30 m. Common distant receivers supplied simultaneous reports. Overall performance was similar in the short run, but the Buddipole stood inside the loop and antenna interaction limited the conclusion. Either transmission could also be reported alone; weak reception and frequency-specific interference were possible explanations. His report distinguished received SNR from signal strength. He later published *Antenna Comparisons Using Simultaneous WSPR Measurements* in QEX in July/August 2017; the preliminary report's June 2017 update points readers to that publication. <a href="#ref-18">[Ref-18]</a> <a href="#ref-19">[Ref-19]</a>

> **Use in WSPRadar:** compare transmissions observed by the same receiver in the same cycle. Keep paired ΔSNR and one-sided decoding evidence distinct, and document the physical arrangements that bound the comparison.

<a id="sec-d-toledo"></a>
##### 7.3.3 Sivan Toledo, 2010: a useful negative result about timing.

Toledo compared three loop antennas in successive blocks of approximately one hour. Reports changed substantially while he was still using the same antenna: one path varied by about 10 dB in forty minutes, and another receiver showed similar variability. Apparent differences between antennas were comparable with this background variation, so that experiment could not separate antenna performance from changing conditions. His account discussed automated switching and Preston's simultaneous approach as ways to improve the design. It was a limitation of the experiment, not a finding that WSPR comparisons are impossible. <a href="#ref-3">[Ref-3]</a>

> **Use in WSPRadar:** make the common operating period part of the comparison, inspect changes over time and repeat controlled tests. Collecting more reports does not by itself remove differences between the conditions being compared.

<a id="sec-d-milazzo"></a>
##### 7.3.4 Carol F. Milazzo, KP4MD, 2011: compare complete stations in both directions.

Published in January 2011 using December 2010 measurements, Milazzo's study compared stations 29 km apart through a common receiver about 1 750 km away. She corrected for transmit-power differences and examined the results alongside VOACAP estimates. On 40 m, the horizontal-loop station generally produced stronger transmitted reports, while the vertical-antenna station received the common distant station with better SNR. Different sites, radios and band schedules remained part of the comparison, and the selected distant station limited its geographic scope. <a href="#ref-4">[Ref-4]</a>

> **Use in WSPRadar:** analyze TX and RX separately, make the power basis explicit and check common activity. A stronger transmitted report does not establish better reception; interpret each result as evidence about the complete installations and paths tested.
>
> **Explore in WSPRadar:** the [Milazzo historical replay](https://wspradar.org/en/demos/milazzo_tx_buddy/) revisits Figures 6 and 7 in RX and TX. It shows how exact cycle/locator matching and reported-power normalization can leave very few usable pairs despite larger report totals, and why unverified schedules limit comparisons of those totals. The prepared profile starts in RX; the guide also provides the TX configuration.

<a id="sec-d-griffiths-squibb"></a>
##### 7.3.5 Gwyn Griffiths, G3ZIL, and Nigel Squibb, G4HZX, 2017: compare, investigate and retest.

In *Improving HF Band SNR*, they paired reception of the same transmitter at the same time and examined differences against time, distance, soil moisture and station changes. After three ground radials were added at G4HZX, the earlier moisture association was absent in the following test window. Replacing and relocating a nearby computer also coincided with an approximately 5 dB SNR improvement. The precise noise mechanism was unresolved, and both observations concerned complete receiving installations. The recorded changes made the comparisons useful for diagnosis without proving a universal antenna effect. <a href="#ref-5">[Ref-5]</a>

> **Use in WSPRadar:** use paired receiver comparisons and temporal or distance views alongside an operator's station log. Treat a pattern as a reason for a targeted intervention and repeat measurement, with causal claims proportional to the controls.
>
> **Explore in WSPRadar:** three prepared configurations revisit these historical reports:
>
> - [**Figure 3: RX Benchmark**](https://wspradar.org/en/demos/griffiths_squibb_fig3/) follows the April 2017 G3ZIL/G4HZX comparison through maps, time summaries and individual paths. It shows how a paired-SNR advantage and additional decodes complement one another, while varying with direction and time.
> - **Figure 6: UTC-hour comparison** narrows the same receivers to 5–7 April. Its separate configuration shows an early-hour vertical advantage changing to a daytime/evening dipole advantage; comparing folded and chronological views tests how consistently the pattern appears. The Figure 3 guide also explains this reconstruction.
> - [**RX Performance**](https://wspradar.org/en/demos/griffiths_squibb_rx_performance/) examines G3ZIL alone. Follow HB0QRP to distinguish at-least-once reach, Decode Rate within confirmed opportunities, and SNR among successful decodes. This is WSPRadar's additional analysis of the historical reports, without a Reference receiver.

<a id="sec-d-vanhamel"></a>
##### 7.3.6 Vanhamel, Machiels and Lamy, 2022: characterize the receiving chains.

Their 160 m experiment first connected two receiving chains to one antenna. Two seven-day calibration periods each produced a mean offset of about 1.2 dB, which they applied before comparing antennas simultaneously. With identical antennas placed at orthogonal orientations, they observed an SNR difference of approximately 3 dB in that installation. Polarization and ionospheric effects were discussed as possible explanations; the orientation result did not establish one physical cause. The calibration also made an equipment contribution visible before interpreting the antenna comparison. <a href="#ref-2">[Ref-2]</a>

> **Use in WSPRadar:** allow an independently measured receiving-chain offset to be expressed through the signed Reference correction, with its measurement procedure documented. Keep the corrected SNR comparison separate from claims about the antenna or polarization mechanism that produced it.
>
> **Explore in WSPRadar:** two prepared comparisons separate calibration from the subsequent antenna experiment:
>
> - [**Receiver calibration**](https://wspradar.org/en/demos/vanhamel_rx_calibration/) leaves the shared-antenna receiving-chain offset visible, with no correction applied. It shows why the mean, spot-pair median and station-balanced median can differ, and why a correction needs a documented measurement basis.
> - [**Antenna rotation**](https://wspradar.org/en/demos/vanhamel_rx_buddy/) follows M7AEO while the Reference dipole turns 90° and the Target long wire stays fixed. The approximately 3 dB step favors the fixed long wire relative to the dipole. It shows why one path's chronological evidence can reveal a transition hidden by its whole-period median. The guide documents the separate calibration estimate used in this configuration.

<a id="sec-d-zander"></a>
##### 7.3.7 Jens Zander, 2022: state the comparison model and its assumptions.

Zander's preprint models two local antennas transmitting simultaneously to common remote receivers. A same-receiver SNR difference cancels shared path loss and receiver noise under the model's assumptions; cross-calibration between those distant receivers is unnecessary for each within-receiver difference. His preliminary paired measurements had a sample standard deviation around 3 dB. The analysis considers interference, failed decodes, quantization and the precision gained by averaging, as well as directivity, geographic sampling and unknown elevation angles. Equal or corrected powers and differences between transmitting chains still matter. <a href="#ref-1">[Ref-1]</a>

> **Use in WSPRadar:** make same-cycle differencing and the reported-power basis explicit. WSPRadar defines its own qualification and aggregation rules; the preprint's uncertainty model is not automatically their uncertainty model, and observed ΔSNR does not directly measure absolute antenna efficiency.
>
> **Explore in WSPRadar:** [Zander's TX comparison](https://wspradar.org/en/demos/zander_tx_buddy/) revisits Experiment A / Figure 4, comparing a short portable vertical with the larger Hy-Gain AV620. It shows why station-balanced and pooled spot-pair summaries differ, how the result varies by direction, and why unequal reporting spans must be checked before interpreting decode totals. The short prepared window supports this experiment's observed comparison, not a daily pattern or a universal portable-antenna penalty.

<a id="sec-d-rietdorf"></a>
##### 7.3.8 Thomas Rietdorf, DL2OAH, 2026: a synchronized multiband station comparison.

His DARC presentation of 17 January 2026 reports measurements from 12–21 January 2025. Synchronized transceivers compared a horizontal OCF/IC-7610 installation with a vertical/FT-991A installation in separate RX and TX runs on 40, 20, 15 and 10 m. Matched two-minute reports supported comparisons by time and direction, alongside one-sided reports. The presentation reports a 2.5–7 dB SNR advantage for the horizontal installation, depending on band, while maximum distances were approximately equal. Different radios and the distribution of remote stations limit attribution to the antennas alone. <a href="#ref-20">[Ref-20]</a>

> **Use in WSPRadar:** combine synchronized comparisons with several views of the evidence. Read paired SNR, one-sided decodes and geographic or temporal patterns together, retaining the complete-installation interpretation and the actual measurement dates.

<a id="sec-d-ostergaard"></a>
##### 7.3.9 Dale Ostergaard, N3HXZ, 2026: practical sequential antenna comparisons.

Ostergaard has advanced WSPR-based antenna testing for portable and field operation, documenting a repeatable approach using one transmitter and an antenna switch. His March/April 2026 *QEX* article, *Using WSPR to Predict Relative Antenna Gain of Directional Antennas*, describes alternating antenna configurations, commonly in 30-minute blocks, and estimating relative signal strength at common receiving stations. Reported SNR values are converted from dB to linear power ratios before averaging; he recommends at least 40 reports per antenna at each receiving station. His published case studies include comparisons of elevated and ground-mounted vertical antennas. This makes quantitative field comparisons accessible with modest equipment, while changing propagation between blocks and the absence of undecoded signals remain important limitations. <a href="#ref-34">[Ref-34]</a>

> **Use in WSPRadar:** credit the practical sequential method, explicit switching schedules and receiver-level evidence requirements. Sequential relative-gain estimates complement synchronized paired ΔSNR but are not directly interchangeable with them.


<a id="sec-d-4"></a>
#### 7.4 Analysis infrastructure and related tools

> **Use in WSPRadar:** **wspr.live is the primary database, with WSPRdaemon's WD2 and WD1 as alternatives**. Each run uses one source. The developers, station operators, computing-resource providers and volunteer maintainers make this analysis possible; service availability and the quality of uploaded records remain part of the evidence context.
>
> **Our sincere thanks to everyone who sustains these services and contributes reports, computing resources and volunteer time.** Your work gives the amateur-radio community a shared foundation for learning, experimentation and better station design.

<a id="sec-d-griffiths-robinett"></a>
##### 7.4.1 Gwyn Griffiths and Rob Robinett, 2020: reusable database analysis.

Their WSPRdaemon TimescaleDB and Grafana work joined reports from the same transmitter, time and band, then displayed SNR differences with medians, quartiles, time, distance and azimuth. One example separated nighttime differences westward toward North America from daytime differences involving nearer stations. Noise measurements and exports gave operators further ways to investigate these patterns. The contribution included both the comparison method and a reusable route from stored observations to interpretable displays. <a href="#ref-21">[Ref-21]</a>

> **Use in WSPRadar:** continue that practice of inspecting common-signal differences in time and geography, with a route back to the contributing observations. WSPRadar's own grouping and weighting rules are specified in [Chapter 8](#sec-7).

<a id="sec-d-wspr-live"></a>
##### 7.4.2 Arne and the wspr.live project, with computing resources from HB9VQQ.

Arne's ClickHouse database work provides public queries over historical and recent WSPR reports; dashboards and exports make those records usable by operators and other applications. The official service documentation credits **HB9VQQ for computing resources**. Phil VK7JJ's documentation also explicitly credits Arne's database contribution. <a href="#ref-10">[Ref-10]</a> <a href="#ref-22">[Ref-22]</a>

<a id="sec-d-wsprdaemon"></a>
##### 7.4.3 Rob Robinett, AI6VN, and the WSPRdaemon community.

Reception, multireceiver acquisition, reporting, database hosting and continued volunteer operation sustain these services. WSPRdaemon's documentation credits Arne's database development and the hosting collaboration. Its earlier TimescaleDB work and later ClickHouse services are distinct contributions. <a href="#ref-11">[Ref-11]</a>

<a id="sec-d-farfield-lab"></a>
##### 7.4.4 Tim, K5OHY — FarField Lab: accessible sequential antenna benchmarking.

[FarField Lab](https://farfieldlab.streamlit.app/) is a free, open-source application that makes practical WSPR antenna comparisons accessible to radio amateurs using a **single transmitter or transceiver and an antenna switch**. It supports rapid **ABAB and ABBA** alternation between transmissions, longer sequential block comparisons with editable switching schedules, and Reverse Beacon Network analysis. Its short-test method pairs observations from neighbouring transmissions, limiting the influence of changing propagation; balanced ABBA sequences can additionally compensate for approximately linear drift under suitable conditions. Repeated measurements and averaging help reduce random variability, while longer block comparisons remain more exposed to propagation changes. FarField Lab evaluates relative SNR differences at common receivers, reception reach, direction and distance, supported by receiver-activity checks, evidence thresholds, uncertainty estimates and statistical validation. Its long-block implementation reproduces published results from Dale Ostergaard, N3HXZ. **FarField Lab offers a genuine and practical alternative to WSPRadar**, particularly for operators without synchronized dual-station hardware. Its sequential approach complements WSPRadar's simultaneous, same-cycle paired RX/TX benchmarking, giving radio amateurs distinct but equally valuable ways to investigate antenna and station performance using public WSPR data. [Ref-35](https://github.com/K5OHY/FarField-Lab) [Ref-34](https://www.n3hxz.net/wspr-methodology)

> **Use in WSPRadar:** recognize FarField Lab as a complementary sequential antenna-analysis tool and help operators choose the experimental approach best suited to their equipment and objectives.

Other tools make complementary parts of experimentation accessible:

<a id="sec-d-wspr-rocks"></a>
##### 7.4.5 Phil, VK7JJ — WSPR.Rocks

Interactive queries, maps, charts, duplicate and passband inspection, plus Head2Head comparisons of receivers, transmitters or software versions. SpotQ supplies a heuristic ranking using distance, reported power and SNR. These are useful ways to explore reports; their metrics have their own definitions. <a href="#ref-22">[Ref-22]</a>

<a id="sec-d-wsprlite-dxplorer"></a>
##### 7.4.6 Richard Newstead and SOTABEAMS — WSPRlite/DXplorer

Standalone low-power beacons and accessible comparisons, including the DX10 range indicator. In Newstead's 2017 indoor/outdoor test, two loops transmitted simultaneously at 200 mW; 133 same-receiver, same-time pairs gave an average indoor disadvantage of 6.8 dB.

> **Use in WSPRadar:** credit the practical paired-test design, while treating the value as a result for that installation and operating period.

<a href="#ref-23">[Ref-23]</a> <a href="#ref-24">[Ref-24]</a>

<a id="sec-d-wspr-station-compare"></a>
##### 7.4.7 Walter Machiels, ON4AWM — WSPR-Station-Compare

An RX-comparison workflow with measured receiver-offset correction, observation thresholds, callsign filtering and azimuth selection. It makes controlled-comparison choices available in operator software. <a href="#ref-25">[Ref-25]</a>

<a id="sec-d-antenna-performance-analysis"></a>
##### 7.4.8 Fred, W6BSD — Antenna Performance Analysis

Reports organizing where and when transmitted WSPR signals were received, across times and frequency bands. This makes an installation's observed coverage accessible without writing a custom analysis. <a href="#ref-26">[Ref-26]</a>

<a id="sec-d-watt"></a>
##### 7.4.9 Colin Murray, GM4EAU — WATT

An editable Excel/VBA workflow for queries, filters, calculations, charts and map replay through successive time intervals, helping operators inspect changing propagation patterns. <a href="#ref-27">[Ref-27]</a>

These tools overlap in purpose, but their filters, comparison units and summaries differ. Check the quantity behind a figure before comparing its value with a WSPRadar result.


<a id="sec-d-5"></a>
#### 7.5 What WSPRadar inherits, integrates and adds

WSPRadar brings these experimental lessons into a documented RX and TX workflow. Its deliberate choices are:

* **Define the comparison.** Controlled Benchmark compares a Target with one Reference Setup/Station under independently known common operation. Historical replay retains its explicitly unverified operating conditions.
* **Keep complementary results visible.** Same-cycle pairs support ΔSNR; paired and one-sided Decode Outcomes support the decode comparison. A station rarely heard on one side may contribute few spot pairs, so paired SNR alone can give an incomplete picture.
* **Expose adjustments.** Reported-power normalization and optional signed Reference correction make the numerical basis inspectable.
* **Define opportunities.** Performance relates successful decodes to confirmed reception opportunities. A missing decode counts as a miss only when the required reports establish both the transmitter’s and receiver’s activity.
* **Distinguish weighting.** Giving each station equal weight answers a different question from giving each individual observation equal weight.
* **Make results traceable.** Map, station and individual-observation views, saved settings and exports connect a conclusion to the data and choices behind it.

These definitions determine which observations qualify, how they are counted and how they influence a summary. They support reproducible comparisons conditional on the available reports and operating conditions; they do not directly establish unconditional reception probability or calibrated antenna efficiency. [Chapter 8](#sec-7) specifies the calculations, and [Chapter 9](#sec-8) explains how to report supported claims.


<a id="sec-7"></a>
### 8. Scientific Methods

**Benchmark** compares Target and Reference for the same remote stations and WSPR cycles. It keeps both paired and one-sided decode outcomes. A pair with usable SNR on both sides also supplies ΔSNR. **Performance** measures the Target’s success within confirmed reception opportunities, without a Reference. The counting rules below define a station by its reported callsign and locator.

Follow three questions through the calculation:

| Question | What the method must establish |
|---|---|
| **What counts once?** | One remote station in one WSPR cycle, after matching and combining reports under the rules below. Several reports do not automatically count as several observations. |
| **Which observations enter the result?** | The selected analysis and filters determine which observations are included. Each metric also has requirements for the data per station or segment. Unknown activity and unmet requirements differ from a measured zero. |
| **What receives equal weight?** | Depending on the summary, one station, one spot pair, one confirmed opportunity or one station's contribution within a time interval. More reports do not always mean more weight. |

A database spot records a successful decode. WSPRadar combines reports into spot pairs and confirmed opportunities using the rules below. Medians, rates and other summaries describe those included observations.

Read the shared foundations in [Section 8.1](#sec-7-foundations), then [Benchmark](#sec-7-benchmark) or [Performance](#sec-7-performance). [Section 8.4](#sec-7-views) explains geographic and temporal summaries, [Section 8.5](#sec-7-claims) the strength of conclusions, and [Section 8.6](#sec-7-outliers) the optional event detector. A calculation can be correct for the retained evidence while its physical explanation remains uncertain; [Chapter 9](#sec-8) gives reporting guidance.


<a id="sec-7-foundations"></a>
#### 8.1 Shared evidence foundations

<a id="sec-7-spots-identities-cycles"></a>
<a id="sec-7-1"></a>
<a id="sec-7-2"></a>
##### 8.1.1 Spots, identities and cycles

Each completed run uses one WSPR database; it does not combine records from different sources. Record that source with the result, because the reports come from different transmitters, receivers, decoders and reporting systems.

A **spot** is a reported successful decode. A **WSPR cycle** is the two-minute interval beginning at an even UTC minute. WSPRadar counts observations for one remote station in one cycle retained by the analysis, on the selected band: a transmitter in RX or a receiver in TX. Before counting outcomes, it combines reports that meet the requirements into one observation per setup, station and cycle. [Section 8.1.2](#sec-7-normalization-consolidation) explains which report is kept.

A **spot pair** requires usable reports for Target and Reference relating to the same remote station in the same cycle. RX compares two receivers hearing the same transmitter; TX compares two transmitters heard by the same receiver. Reports from different cycles are never paired. Pairing neither requires identical RF frequencies nor establishes identical physical propagation paths; simultaneous TX signals normally need clearly separated frequencies.

**Identity depends on the station's role:**

| Role | Database identity |
|---|---|
| **Target** | Exact receiving callsign in RX, or transmitting callsign in TX, plus Target QTH's first four locator characters. |
| **Reference Setup/Station** | Exact Reference callsign plus its four-character locator, discovered from reports or independently supplied. |
| **Remote station** | Exact callsign plus the **full reported locator**: the transmitter in RX, or receiver in TX. |

**In the explanations below, a remote station means one exact callsign and full reported locator.** Even with a six-character Target QTH, its first four characters select Target reports; the full configured locator anchors distance, azimuth and solar calculations. The same remote callsign at two full locators counts as two stations, even within one grid-4. Matching grid-4 values do not prove physical co-location.

Target and Reference require distinct exact callsigns; a base callsign and a suffixed callsign remain distinct. Each report kept for analysis must contain the callsign and locator fields needed for matching. WSPRadar does not reconstruct compound callsigns from hashes or borrow a missing locator from a neighboring cycle. Incorrect or changing locators can split one physical station into several counted stations, move its mapped position or trigger moving-station exclusion.

**Extended WSPR still supplies separate two-minute observations.** WSPR-2 names the transmission mode; the following message types describe its contents:

| Message type | Contents |
|---|---|
| <strong class="defined-term">Type 1</strong> | An ordinary callsign, four-character locator and power in one transmission. |
| <strong class="defined-term">Type 2</strong> | A compound callsign and power, without a locator. |
| <strong class="defined-term">Type 3</strong> | The complementary message with a compact 15-bit callsign code (a <strong class="defined-term">hash</strong>), six-character locator and power. The receiver must associate the code with the callsign. |

These message formats are documented in the WSJT-X reference <a href="#ref-12">[Ref-12]</a>. WSPRadar does not classify them, reconstruct missing phases or combine them into a four-minute observation. Either or both cycles can supply pairs when the required identities resolve in the database; a pair in one cycle does not require another in the next. Matching TX message patterns and schedules is an experimental recommendation, not a message-type eligibility test; see [Section 2.2.1](#sec-3-tx-benchmark-simultaneous) and [Chapter 5](#sec-simultaneous-tx-setup).

The configured UTC window defines the run. For wholly pre-2022 periods, an empty strict request can trigger the historical decode-code fallback: no Target source evidence in Performance, or no source evidence from either setup in Benchmark. [Section 11.4](#sec-6-4) gives the exact cutoff and mode uncertainty; [Section 11.6](#sec-6-6) covers database availability and source selection.


<a id="sec-7-normalization-consolidation"></a>
##### 8.1.2 Power normalization and consolidation

**RX Performance and Benchmark use a common reported-power basis; TX Performance can retain reported received SNR or normalize it.** WSPR reports SNR in dB relative to a **2 500 Hz reference bandwidth**, and transmit power in dBm <a href="#ref-8">[Ref-8]</a>. With TX normalization enabled, and for RX Performance and Benchmark, WSPRadar adjusts successful SNR to **30 dBm (1 W)**:

$$SNR_{\mathrm{norm}}=SNR_{\mathrm{reported}}-P_{\mathrm{reported}}+30$$

The SNR terms are in dB; the power values are in dBm. For example, reported SNR of **−15 dB** at **20 dBm** becomes **−5 dB** at the 30 dBm comparison level: the 10 dB reported-power shortfall is added back.

This removes the **reported power difference** from the comparison. It does not recreate the decodes that would have occurred at 1 W, or correct antenna gain, radiation efficiency, feedline loss, EIRP, receiver calibration or local noise. Decode Outcomes and Performance opportunities remain those actually observed.

The WSPR transmit-power field is a reported value set in software, not a continuous measurement of instantaneous RF output. When the reported transmit power is the same for every observation being summarized, and the included observations are unchanged, normalization adds a constant offset: absolute means, medians and CI endpoints shift, while station-relative residuals and CI widths remain unchanged. Actual power fluctuations not reflected in that reported field remain in both representations. An operator can change the configured field during the run; then the adjustment can differ between observations and the constant-offset conclusion no longer applies. Neither raw nor normalized SNR isolates transmitter power, propagation or receiver conditions as the cause of a change.

**Several reports still count as one observation per setup, remote station and cycle.** TX Performance keeps the strongest qualifying SNR on the completed run’s selected basis: reported received SNR with normalization off, or normalized SNR with it on. RX Performance and each side of Benchmark keep their strongest qualifying normalized SNR. Successive cycles are never combined. When reports contain different power values, the raw and normalized maxima can come from different reports. The selection happens during acquisition; an already-normalized maximum cannot generally be converted back into the strongest raw report.

The <strong class="defined-term">strongest-report rule</strong> describes the strongest reported reception, rather than a central value across the available reports. Weaker duplicate-like reports, secondary decodes or unwanted signal replicas cannot lower that maximum. Conversely, an erroneously high report can become the retained value. A setup with more contributing receivers or reports has more chances to supply a high value. WsprDaemon also documents keeping the best SNR when merging receivers for WSPRnet <a href="#ref-11">[Ref-11]</a>.

That precedent does not establish that the maximum is the intended signal, or that both setups selected the same spectral component. Means and medians would describe different features of the available reports; none of these statistics identifies the intended component by itself. Later medians summarize the retained values and cannot undo this earlier selection.

**The Benchmark Decodes & Stations plots use a different SNR basis.** <strong class="defined-term">Decodes & Stations: From Strong Signals to Weak-Signal Reception</strong> keeps each setup’s strongest **original reported SNR** per remote station and cycle. It applies neither 30 dBm normalization nor Reference correction. The curves count observed spots and stations at raw-SNR cutoffs; they do not replace normalized paired ΔSNR. They use the included stations and observations within the Inspector’s selected distances and directions, including all paired and one-sided observations. Changing that selection updates the curves and counts, while the SNR basis stays the same. See [RX Benchmark](#sec-3-rx-benchmark) and [TX Benchmark](#sec-3-tx-benchmark) for their role in the comparison.

As signals weaken relative to noise and approach the limits of WSPR decoding, how do the two setups compare? These curves progressively include lower-SNR reports, showing how decoded-spot and distinct-station totals grow. They also include **one-sided decodes** — reception recorded for only one setup — which paired ΔSNR cannot capture.

The upper panels are **Paired spots**, **One-sided spots**, and **All decoded spots**. The lower panels are **Stations with paired spots**, **Exclusive stations**, and **All observed stations**. **Exclusive stations** means stations with reports for only one setup anywhere within the selected scope. Stations with reports for both setups but no spot pair appear separately in the **Both observed, no pairs: +n stations** annotation; they are included in **All observed stations**, not in the exclusive-station curves.

At **“≥ −20 dB”**, read the number of reports with a reported SNR of −20 dB or higher. Station panels count stations with at least one eligible report meeting that cutoff. Moving right lowers the cutoff and includes weaker reports. Each endpoint includes all observations belonging to that panel in the selected scope. For example, **≥ −20 dB** includes reports at −20 dB and all higher SNR values, such as −15 or −10 dB; it excludes reports at −21 or −25 dB. **This is a counting filter applied to already-decoded reports, not a receiver sensitivity setting.** All three panels within a row use identical zero-based Y-axis limits, ticks and count units; spot and station rows have separate scales.

Each curve uses that setup’s raw reported SNR, without power or Reference-offset correction. Right-hand endpoints show each panel’s totals. In **All decoded spots** and **All observed stations**: spots = paired + one-sided; stations = stations with pairs + both observed without pairs + stations exclusive to that setup. The three station categories are not a decomposition of spot counts. Their endpoint identity need not hold at earlier cutoffs: a station's strongest one-sided report can exceed its strongest paired report.

A rise between adjacent cutoffs counts reports — or newly included stations — in that SNR interval. Horizontal separation between paired curves is not the paired ΔSNR distribution. Missing-side SNR is unknown.


<a id="sec-7-activity-eligibility"></a>
<a id="sec-7-3"></a>
##### 8.1.3 Operating conditions and eligibility

**Controlled Benchmark relies on independently known common operation.** In RX, both receivers must have listened on the selected band with functioning reporting throughout the comparison period. In simultaneous TX, both transmitters must have transmitted in the same WSPR cycles. The shared Benchmark acceptance records that common operation was confirmed or its limitations were accepted; successful database reports cannot independently verify operation.

**When common operation is unverified, interpretation is limited.** Historical reports can describe observed differences without establishing a controlled experiment. The same observed-outcome and paired-ΔSNR calculations apply, but one-sided counts may also reflect schedules, outages or reporting interruptions. Every Benchmark uses [the same acceptance control](#sec-5-3); see also [historical and retired designs](#sec-7-neighborhood).

Benchmark applies the same station-and-cycle consolidation rules and population filters to observations for both setups. A missing Target decode does not exclude Reference-only observations, even if Target has no reports anywhere in that cycle or throughout the entire period. The converse applies to Target-only observations. If neither side has a report, there is no observed outcome; WSPRadar adds no artificial “both missed” row.

**Performance includes a cycle only when reports show that Target was operating on the selected band.** This selection is called <strong class="defined-term">Target-active conditioning</strong>.

| Direction | What establishes Target activity in that cycle? |
|---|---|
| **RX** | The Target receiver uploaded at least one qualifying decode. |
| **TX** | At least one qualifying report of a Target transmission exists somewhere. |

Target activity is checked before geographic filtering. The report establishing activity can come from outside the analysis distance limit or the area currently being inspected. It can also involve a station later removed by the special-callsign or moving-station exclusion. Such a report confirms activity without restoring that station to the analysis or adding its out-of-scope outcome to the selected area. The scopes of exported files remain as described in [Section 9.4](#sec-8-4).

A cycle without a report establishing activity is excluded. WSPRadar cannot distinguish downtime from operation that produced no reported decode. Performance therefore describes cycles with observable Target activity, rather than all elapsed time or planned transmissions.

Target activity alone does not make every unreported remote station a miss. Reports must also establish activity of the particular remote transmitter or receiver, as defined in [Section 8.3.1](#sec-7-performance-opportunities).


<a id="sec-7-benchmark"></a>
#### 8.2 Benchmark: differences and shared evidence

Benchmark describes two aspects of the same comparison: **the SNR difference when usable reports exist for both setups**, and **the decoding outcomes across all retained observations**. The first needs a spot pair; the second also includes reports from only one side. Keep these populations distinct when interpreting a result.


<a id="sec-7-benchmark-outcomes"></a>
<a id="sec-7-6"></a>
##### 8.2.1 Decode Outcomes and missing observations

**First classify each remote station and WSPR cycle.** After consolidation and filtering, there are three outcomes:

| Outcome | Evidence in that station-cycle |
|---|---|
| <strong class="defined-term">Only Target</strong> | A Target-side report, without a Reference-side report. |
| <strong class="defined-term">Paired</strong> | Reports for both setups relating to the same remote station and cycle. Usable SNR on both sides supplies ΔSNR. |
| <strong class="defined-term">Only Reference</strong> | A Reference-side report, without a Target-side report. |

These are <strong class="defined-term">native</strong> outcomes: matched, consolidated and scientifically filtered observations at the original WSPR-cycle level, before display aggregation.

There is no fourth, both-missed outcome: if neither side reported the station, the database supplies no observed event. Benchmark retains one-sided evidence symmetrically, without a separate Target-activity witness. A spot pair still supplies ΔSNR when its map segment does not meet the station-count or CI precision requirement.

**Then classify each station over the filtered comparison period.** A station can have different native outcomes in different cycles. The ΔSNR map summarizes that history in four mutually exclusive station classes:

| Station class | Meaning over the comparison period |
|---|---|
| <strong class="defined-term">Paired (qualifying)</strong> | Retained paired evidence; shown in strong green. |
| <strong class="defined-term">Both observed, no pairs</strong> | Reports relate this station to both setups, but always in different cycles. |
| **Only Target** | All retained observations of this station are Target-only. |
| **Only Reference** | All retained observations of this station are Reference-only. |

A station’s class does not change its individual observations. A station with pairs can also supply Target-only and Reference-only events. **Both observed, no pairs** is a station class, never a fourth spot outcome. The ΔDecode map uses one green category for Paired stations; all four station classes remain included in the observed population.

Below Decodes & Stations, the **Spots** card is on the left and the **Stations** card on the right; both describe all retained observed evidence in the same active scope. Each card introduces its counting unit, then shows the <strong class="defined-term">Union</strong> total: evidence observed by **Either** setup, with shared evidence counted once. The colored partition bar and legend divide that union into mutually exclusive groups. Green denotes Paired, amber denotes stations observed on both sides without pairs, magenta denotes Target-only evidence and cyan denotes Reference-only evidence.

The tables use a **Breakdown** column, **Target** and **Reference** columns labeled with the actual callsigns, and a **Union** column. In **Spots**, the rows are **Paired spots**, **One-sided · Target decoded**, **One-sided · Reference decoded** and **All decoded spots**. A pair contributes one to each setup's total but only one to Union. Thus, **Union = Target total + Reference total − Paired**. One-sided spots remain in their native outcome rows even when their station also has paired observations elsewhere.

In **Stations**, each exact callsign and full locator belongs to one of four groups: **Stations with paired spots**, **Both observed, no pairs**, **Exclusive to Target**, or **Exclusive to Reference**. The final **All observed stations** row adds those groups. A station with reports for both setups contributes one to each setup total and one to Union, whether or not it has a same-cycle pair. Thus, **Union = Target total + Reference total − stations with pairs − Both observed, no pairs**. The aligned Spots row for **Both observed, no pairs** is intentionally blank because this is a station-history category, not a fourth spot outcome. These observed-count tables retain all paired and one-sided evidence; ΔSNR uses the paired evidence.

The later **Benchmark Statistics** cards contain Median, Mean, applicable CI and ΔDecode. The Stations card averages the means of the stations included in ΔSNR and gives that average’s CI. The Spots card pools their pairs and gives the pooled mean and its separate CI.

The Statistics subheaders identify the relevant support: stations and receiver decodes for ΔDecode, qualifying spot pairs for its ΔSNR histogram, and the same qualifying stations for both the station-mean and station-median histograms. Drill-Down retains the three native outcomes. Temporal coverage separately counts stations and station-cycle events as explained in [Section 8.2.4](#sec-7-benchmark-coverage).

**Missing reports have no measured SNR.** WSPRadar neither reconstructs a missing-side SNR nor assigns an artificial ΔSNR. Actual transmit power, propagation, interference and decoder behavior affect which signals are decoded. Incorrect reported power can distort normalized ΔSNR; power normalization does not change the decode outcomes already observed. Requiring both sides to decode can underrepresent weak-signal conditions, so missing pairs should not be treated as random omissions.

For controlled Benchmark, interpret one-sided evidence under the independently established common operation in [Section 8.1.3](#sec-7-activity-eligibility). Historical replay leaves that operating premise unverified.

**Extended-WSPR identity errors are a separate data-quality issue.** Type 3 uses a 15-bit callsign hash. An unresolved or colliding hash can leave a decode unidentified or associate it with an incorrect callsign, locator or power, as documented by QRP Labs <a href="#ref-28">[Ref-28]</a>. WSPRadar can match the stored identity but cannot prove every upstream association correct. Clustered or unequal errors can change station counts, one-sided outcomes and SNR summaries; a large dataset or a median does not guarantee protection. For compound callsigns, use the database preflight and phase-specific audit in [Chapter 5](#sec-simultaneous-tx-setup).


<a id="sec-7-benchmark-delta"></a>
<a id="sec-7-5"></a>
##### 8.2.2 Delta SNR and Reference correction

**Reference correction** represents an independently established additive offset. It is added to normalized Reference SNR:

$$SNR_{\mathrm{Reference,corr}}=SNR_{\mathrm{Reference,norm}}+C_{\mathrm{Reference}}$$

Here `C_Reference` is the signed correction in dB. Enter a measured calibration offset with the `target - reference` sign. The offset must be approximately stable over the relevant band, signal levels, equipment state and time. [Section 10.3](#sec-5-3) describes the control and [Chapter 6](#sec-reference-snr-calibration) the calibration procedure.

For each spot pair, subtract corrected Reference SNR from normalized Target SNR:

$$\Delta SNR=SNR_{\mathrm{Target,norm}}-SNR_{\mathrm{Reference,corr}}$$

| ΔSNR | Meaning for this pair |
|---|---|
| **Positive** | Target SNR is higher. |
| **Zero** | Target and corrected Reference SNR are equal. |
| **Negative** | Reference SNR is higher. |

**Sign check.** On the normalized basis, Target `−10 dB` minus Reference `−12 dB` gives **+2 dB**. A Reference correction of `+1.5 dB` raises Reference to `−10.5 dB`, leaving **+0.5 dB**. A positive correction reduces the reported Target advantage; it does not change the Target observation.

In RX, both receivers observe the same transmitter. Its reported-power terms cancel **when both retained reports carry the same power value**. TX compares different transmissions, so the normalized difference depends directly on their reported powers. Uncorrected equipment differences remain in either comparison. ΔSNR describes the documented complete setups; assigning it to an antenna or another component requires the controls in [Chapter 2](#sec-3).


<a id="sec-7-benchmark-aggregation"></a>
<a id="sec-7-7"></a>
##### 8.2.3 Station and map aggregation

**What qualifies for ΔSNR?**

A remote station **qualifies for ΔSNR** when paired observations remain after the run’s population, UTC, solar-state and geographic filters. Each station is counted by exact callsign and full reported locator, as defined in [Section 8.1.1](#sec-7-spots-identities-cycles). This requirement is checked over the full filtered comparison period, not again for each time bin, station selection or zoom. These stations supply the ΔSNR map, histograms, temporal summaries and outlier analysis.

All pairs and one-sided observations remain in coverage, Station Insights, Drill-Down and exports. There is no separate minimum for a station's one-sided count. For example, both `100 Paired / 8 Only Target / 4 Only Reference` and `4 / 100 / 100` supply paired ΔSNR. The observed counts stay unchanged in both cases. The paired-evidence requirement for ΔSNR does not change ΔDecode or Station Reach Advantage.

**How the ΔSNR map pools qualifying pairs**

1. Identify each station’s retained pairs over the full filtered comparison period, after the scientific filters and before display-only map-segment or time selections.
2. Within the map segment, pool the eligible paired ΔSNR values from these stations. Each native pair contributes once; one-sided observations supply no paired ΔSNR.
3. Calculate the <strong class="defined-term">arithmetic mean of the pooled paired differences</strong>, with **one equal weight per pair**. A station with more qualifying pairs contributes more to this map value.
4. Calculate the nominal two-sided <strong class="defined-term">IID Student-t CI</strong> from those same paired differences, using their sample SD, pair count N and the shared confidence level.
5. Count the stations that meet the ΔSNR requirements and contribute at least one eligible pair to this segment. Color the segment only if their count reaches the configured minimum and the CI is available and non-degenerate, with an **unrounded half-width at or below the selected CI ± limit**.

This map estimator matches the **Spots** mean and CI in the separate **Benchmark Statistics** section when the selected scope contains exactly the same qualifying pairs, SNR adjustments and confidence level. It is distinct from the equally weighted **mean of station means** in the Stations card and station-means histogram.

The map mean describes the average retained paired difference in the segment. Each pair counts equally, so a station contributing more pairs influences the result more. Station inclusion is determined over the full filtered period. In contrast, the separate Stations summary gives each included station one equal contribution. The map neither gives station means or medians equal weight nor averages individual-station or segment CIs. Its CI uses the sample SD of all contributing paired differences, including variation within and between stations. Including that variation does not correct the standard error for dependence between observations.

The <strong class="defined-term">spot-pair median</strong> uses the same eligible pairs as the map mean. It is the middle value after sorting, or the average of the two middle values for an even count. The mean and median both give each pair equal weight. The separate station-median summary gives each included station one contribution. Even with paired observations for every station, the summaries can disagree:

| Station | ΔSNR values (dB) | Station median |
|---|---|---:|
| A | +6, +6, +6, +6, +6, +6 | +6 dB |
| B | −2, −2 | −2 dB |
| C | −1, −1 | −1 dB |

The **median of station medians is −1 dB**, while the **pooled spot-pair median is +6 dB**. The mean of the three station medians is **+1 dB**; the pooled pair mean is **+3 dB**. Every calculation is correct, but each gives different weight to stations or extreme values. The lower-right station histogram shows the station medians and labels their median. The upper-right histogram shows station means and labels their mean. In this example every station's observations are identical, so its mean equals its median; the mean of station means is also **+1 dB**. This three-station segment can meet the station-count requirement only when its minimum is three or fewer; it meets the default of three. For the map, each of the ten pairs has equal weight, giving the pooled mean **+3 dB**, not the **+1 dB** equal-station mean. Its pooled-pair CI must also meet the selected half-width requirement before the segment can be colored. All the station and pooled-pair summaries in the separate **Benchmark Statistics** section retain their existing definitions.

**Benchmark Statistics keeps two station summaries and two pooled-pair summaries.** In the Stations table, **Mean ΔSNR ± 95% CI** averages the individual station means and reports the CI half-width when available. The label shows 95% by default and follows the shared confidence level. **Median ΔSNR** is the median of the individual station medians, without a median CI. Both summaries use the same stations that meet the ΔSNR requirements, giving each station equal weight. The Spots table’s Mean and Median pool those stations’ paired differences, giving each pair equal weight. All means are arithmetic averages of Target-minus-Reference differences in dB, after the existing processing and correction.

In the Spots summary card, **Mean ΔSNR ± 95% CI** presents the mean and its CI half-width together in one row, for example **+1.21 ± 0.04 dB**; the confidence percentage in the label follows the configured level. A double rule separates **ΔDecode** from the ΔSNR summaries in both cards.

A separate example with unequal pair counts and a skewed path distinguishes the three means. For this arithmetic illustration, both stations have retained paired evidence:

| Qualifying station | Retained paired ΔSNR values (dB) | Pair count | Station mean | Station median |
|---|---|---:|---:|---:|
| A | 0, 0, +12 | 3 | +4 dB | 0 dB |
| B | +8, +8 | 2 | +8 dB | +8 dB |

The **mean of station means is +6 dB**: `(4 + 8) / 2`. The **pooled pair mean is +5.6 dB**: `(0 + 0 + 12 + 8 + 8) / 5`. The **mean of station medians is +4 dB**, and the **median of station medians is +4 dB**. Their equality here does not make them the same definition. These are different calculations on the same five pairs; no observation is removed.

The four-panel **Benchmark Statistics** figure separates these quantities:

| Position | English panel title | Weighting |
|---|---|---|
| Top left | **ΔSNR ± 95% CI - Qualifying spot pairs** | One ΔSNR value per qualifying spot pair. |
| Bottom left | **ΔDecode - Spot Decodes** | Each station is weighted by its Target plus Reference decode count. |
| Top right | **ΔSNR ± 95% CI - Qualifying station means** | One arithmetic mean per qualifying station. |
| Bottom right | **ΔSNR - Qualifying station medians** | One median per station, using the same stations as the means panel. |

The summary tables follow the same grouping: Spots on the left, Stations on the right. Both right-hand panels show the same station count, one equally weighted value per station, common bin edges and common axis ranges. Their sole reference lines and numerical legend entries are **Mean of station means** above and **Median of station medians** below, matching the Stations table. The mean of station medians remains separately named in the metadata.

The spot-pair panel labels both mean and median above the plot. Coincident markers keep their true positions and both legend entries. The confidence percentage in both mean-CI panel titles follows the shared level (95% by default). The **Mean of station means** legend gives the same estimate and aggregate CI half-width as the Stations card; this CI uses the spread across the station means. A zero-width interval is explicitly marked as degenerate, and an unavailable interval is identified without replacing it with zero.

In the spot-pair panel, the **Mean** legend entry combines the pooled pair mean and available CI half-width as **mean ± half-width** in dB. This CI describes uncertainty of the pooled pair mean under the stated model, rather than histogram spread or uncertainty of the median. The **Median** legend entry remains separate.

Both station histograms use one adaptive bin width chosen from the finer positive Freedman–Diaconis or Sturges candidate calculated separately for the two distributions, rounded upward to a 1/2/5 step and widened if needed to keep the full combined range within 40 bars. Spot-pair histogram bins are unchanged. Negative bins use Reference cyan, positive bins use Target magenta, and the bin containing zero is neutral grey. A neutral bin can also contain nonzero values.

The Stations and Spots tables and all four histograms describe the selected analysis and Inspector scope. The temporal **ΔSNR statistic** selector does not change them. The Stations <strong class="defined-term">mean-of-means CI</strong> is calculated directly from the included station means, including contributions from hatched map segments. Each station’s mean uses its eligible pairs within that scope; each station has equal weight. The Spots summary pools eligible pairs and gives its own mean and CI.

For exactly the same single-segment pairs, SNR adjustments and confidence level, the map mean and CI match the pooled Spots result. To combine segments, pool their eligible pairs instead of averaging their means or CIs. Changing only the map half-width limit changes which segments receive a color, while the Inspector’s eligible observations and summaries stay the same. Changing shared confidence changes the reported mean CIs and may change map coloring; means and contributing observations stay the same.

The map defaults to **three qualifying stations per segment**. The station-count control accepts **1–50**. A callsign at `JO31AA` and the same callsign at `JO31AB` count separately if both qualify and contribute an eligible pair to the segment; these are reported identities, not proven independent physical sites.

For example, if the two identities each contribute one pair, `+2` and `+4 dB`, the map's pooled pair mean is `+3 dB`, its pair count N is **2**, and its station support count is **2**. With unequal pair counts, the map follows pair weights rather than assigning equal station weights. The station minimum and CI requirement both apply. A one-station segment can meet a configured station minimum of one. To receive a color, it must also have at least two contributing pairs, nonzero observed pair variance, and an available CI whose unrounded half-width meets the selected limit.

**What medians protect against**

Medians reduce the influence of isolated extremes without deleting observations. Within one station, `0, 0, 0, +2, +3 dB` has median **0 dB** and mean **+1 dB**. Across station medians `+2, +3, +3, +4, −30 dB`, the median is **+3 dB** and the mean **−3.6 dB**. The extreme value changes the mean much more; the median does not establish that it is an error.

With one value the median is that value; with two it is their arithmetic average. Sparse evidence offers little protection, and medians do not remove systematic errors, make observations independent or isolate an antenna effect. Choose a statistic for the question it answers, not for which setup it favors. [Section 8.5](#sec-7-claims) discusses inference and repeatability.

**How ΔDecode counts evidence**

For the segment, let `J` be Paired events, `T` Target-only events and `R` Reference-only events. Target's decode total is `A = J + T`; Reference's is `B = J + R`. Pool all retained events, including stations without qualifying ΔSNR:

$$r=\frac{A}{B}=\frac{J+T}{J+R}$$

Each Paired event contributes **one decode to each side**, but counts **once** in the observed-event union `E = J + T + R`. The net additional Target decodes are `A − B = T − R`.

For **70 Paired, 20 Target-only and 10 Reference-only** events:

| Quantity | Result |
|---|---:|
| Observed events, `E` | 100 |
| Target / Reference decode totals | 90 / 80 |
| Net additional Target decodes | 10 |
| ΔDecode, Target-to-Reference ratio `90 / 80` | 1.125× |

**Read ΔDecode as fold change.** A Target-to-Reference ratio of **2×** means twice as many Target decodes; **0.5×** means twice as many Reference decodes. Equal nonzero totals give **1×**. Maps and signed chart axes show the larger-to-smaller factor on the favored setup's side: **2× on the Reference side** therefore means the same comparison as a Target-to-Reference ratio of **0.5×**. If only one side has decodes, the result is **Exclusive**; with no observed events it is undefined.

Where both totals are nonzero, the displayed advantage factor is the larger total divided by the smaller. In the Target-to-Reference table ratio, Target-only evidence gives **∞×** and Reference-only evidence gives **0×**; these are the two exclusive cases, not finite fold changes.

For unchanged retained events and scope, exchanging Target and Reference reverses the favored side and takes the reciprocal of the finite Target-to-Reference ratio. A new run with a different Target may also change Target-centered geography or solar filtering, so it need not retain the same events.

ΔDecode is **pooled**, not an average of station ΔDecode values. Frequently observed stations contribute more decodes. Every retained event counts, including one-sided events from stations that also have pairs and stations observed by the two setups in different cycles. Distinct-station counts alone cannot reproduce this metric.

**How the ΔDecode histogram represents that volume**

For each station, let `A_i` and `B_i` be its retained Target and Reference decode totals. Place its advantage on the symmetric ratio axis and weight it by `A_i + B_i`. The vertical axis, **Share of receiver decodes (%)**, therefore counts each paired event twice. This percentage describes the share of the evidence, not the size of the decoding advantage. The red line marks ΔDecode calculated from the pooled Target and Reference totals, **not a median, an arithmetic mean of station ratios or a mean of bin centers**. The ratio axis is not linear.

All retained stations in the active Inspector scope contribute, without another qualification gate. Separate **Exclusive** endpoint bars contain decodes from stations observed exclusively on one side. They do not contain all one-sided events from shared stations. The three ΔSNR histograms retain their separate pair and station qualification rules; the station-mean and station-median panels use exactly the same included stations.

**When a ΔDecode segment has enough evidence to be colored**

Both ΔDecode evidence requirements must be met. **Minimum observed stations per segment for ΔDecode** defaults to **3**, adjustable from **1 to 50**. Count each station with at least one retained event in the segment once, including Target-only and Reference-only stations. The counting unit remains **callsign + full reported locator**. No paired observations or ΔSNR qualification are required.

The event-share default minimum is **1% of the full filtered run's observed events**, adjustable from **0% to 5%** in **0.5%** steps. A segment must also contain at least:

$$N_{\min}=\left\lceil\frac{p}{100}\,E_{\mathrm{run}}\right\rceil$$

Here `p` is the selected percentage, `E_run` counts each retained station-cycle event once, and `ceil` means round upward to a whole event count. The run total is fixed before segment qualification. Map cropping, Inspector selection and below-threshold colors do not change it. At **0%**, every nonempty segment meets the event-share requirement, but the station minimum still applies. The station requirement sets breadth across observed stations; the event-share requirement limits sparse coloring relative to the run. Neither is a confidence level or a guarantee of independent paths, and one frequently observed station can still dominate the pooled totals. Both requirements govern coloring only: all retained events remain in the pooled ΔDecode calculation and Inspector statistics.

Both maps retain observed station markers. An observed segment below its metric's requirement has **gray diagonal hatching (Not qualifying)**; an unfilled segment is labelled **No observations** because it has no retained observations within the selected scope and filters. This does not establish physical absence of reception. Zero ΔSNR and **1× ΔDecode** are valid results and remain colored when their requirements are met. ΔSNR and ΔDecode qualification are independent. Their color scales and the ΔDecode ratio legend are explained in [Section 8.4.6](#sec-7-view-spread).

For ΔSNR, <strong class="defined-term">gray hatching</strong> can mean too few stations meeting the ΔSNR requirements, an unavailable or degenerate pooled-pair CI, or a half-width above the selected limit. To investigate, select the segment's exact distance and direction in **Segment Inspector**, then read the **Spots** mean and **± half-width** in the separate **Benchmark Statistics** section and check the contributing station and pair counts. The map itself has no numerical CI card. For the exact full-precision reason and interval status, use `benchmark/map_segments.parquet` in the analysis download; the Stations card's status concerns its different, equally weighted station-mean CI.

With no contributing pairs, no map mean or CI is available. With one pair, its mean is defined but its sample SD, SE and CI are unavailable. With **two or more contributing pairs**, identical paired ΔSNR values give exactly zero unrounded sample SD: the export retains the calculated zero-width bounds with **degenerate** status, and the segment stays hatched. A zero-width interval does not establish zero physical uncertainty.

Identical **station means** alone do not make the pooled-pair CI degenerate: within-station differences may still vary. Small positive widths retain enough displayed digits to distinguish them from zero. Qualification uses the unrounded width and does not require the CI to exclude zero; a zero mean can qualify when both requirements are met. Hatching does not remove eligible pairs or stations from Inspector scope statistics. Examine the contributing paths and dated evidence before changing the requirements; a broader interval limit or lower station minimum changes the acceptance rule, not the quality or independence of the observations.

**Interpret the two maps together.** ΔSNR describes paired signal quality; ΔDecode describes the balance of total observed decodes. They can favor different setups. Equal decode totals can combine mostly paired events or substantial one-sided evidence that cancels. Events missed by both are absent, so ΔDecode is not an unconditional decoding probability or a Target win rate. Common-operation evidence, actual power, schedules and the observed station population remain essential context.


<a id="sec-7-benchmark-coverage"></a>
<a id="sec-7-8-2"></a>
##### 8.2.4 Temporal decode coverage

**<strong class="defined-term">ΔDecode over Time</strong> separates station reach from decode volume.** Both rows use all retained outcomes, independently of ΔSNR qualification.

| Row | What the bars count within each bin | What the line compares |
|---|---|---|
| <strong class="defined-term">Station-level</strong> | Each remote station once: **Both observed**, **Only Target** or **Only Reference**. | <strong class="defined-term">Station Reach Advantage</strong>, from the distinct-station totals for the two setups. |
| <strong class="defined-term">Spot-level</strong> | Each native station-cycle event once: **Paired**, **Only Target** or **Only Reference**. | **ΔDecode**, from pooled decode totals. |

**Both observed need not mean Paired.** If a station has a report for Target in one cycle and for Reference in another, it belongs to Both observed within that bin, while the two events remain one-sided. Paired always requires the same station and cycle. The remote stations are transmitters in RX and receivers in TX.

For station coverage, let `C` count Both observed stations, `T_s` Only Target stations and `R_s` Only Reference stations. Target's station total is `A_s = C + T_s`; Reference's is `B_s = C + R_s`:

$$r_{\mathrm{stations}}=\frac{A_s}{B_s}$$

The upper bar total is the station union `C + T_s + R_s`. Repeated decodes cannot increase it. An additional station means additional relative to the other setup in that bin, not a first-ever contact or a cumulative discovery. Equal station totals need not mean identical station sets.

The lower row compares `(J + T) / (J + R)`, as defined in [Section 8.2.3](#sec-7-benchmark-aggregation). All paired events use one green category, regardless of ΔSNR qualification. Duplicate reports already consolidated into one station-cycle do not add counts.

**Both secondary axes use signed ratio labels.** Above the central **1×** favors Target; below it favors Reference. In the upper row **2×** means twice as many stations; in the lower row it means twice as many decodes. Read the factor on the favored setup's side; these are not linear ratio axes. Exclusive observations have an explicit endpoint; bins with no support remain gaps. Selected-station coverage uses that station's pooled ΔDecode, not Station Reach Advantage.

<strong class="defined-term">Chronological views</strong> preserve time order. Folded-hour views combine dates under [Section 8.4.4](#sec-7-view-folding), where station membership is assessed separately for each date and hour. The historical **Joint Evidence Share**, `J / (J + T + R)`, measures paired overlap and is no longer the temporal line. Neither current line verifies uptime, counts events missed by both, or establishes a causal antenna advantage.


<a id="sec-2-6"></a>
<a id="sec-3-rx-benchmark-local-median"></a>
<a id="sec-3-tx-benchmark-local-median"></a>
<a id="sec-7-neighborhood"></a>
##### 8.2.5 Controlled operation and retired designs

A controlled Benchmark needs two exact setups with independently established common operation. A changing neighborhood median does not supply that fixed Reference. **Reference Neighborhood has been retired**, and earlier configurations using it are rejected. Select an explicit Reference and establish the operating conditions for a new controlled comparison. The retirement concerns the comparison design; a median remains a valid description of its observed contributors.

The **historical Milazzo example** remains available as an acknowledged observational replay. It permits a reproducible examination of paired and one-sided reports, but those reports alone do not establish synchronized transmission schedules or continuous operation. Unequal schedules can contribute to one-sided counts. Interpret the reconstruction descriptively unless external operating records establish the conditions needed for a controlled decoding comparison.


<a id="sec-7-performance"></a>
<a id="sec-7-4"></a>
#### 8.3 Performance: opportunities and success

Performance shows where and how regularly signals were decoded during confirmed reception opportunities. A successful decode by Target in RX, or of Target in TX, confirms the opportunity by itself. To count a miss, WSPRadar needs reports showing that both Target and the relevant remote station were active on the same band in the same WSPR cycle. A cycle without reports is not enough.


<a id="sec-7-performance-opportunities"></a>
##### 8.3.1 What counts as an opportunity?

An opportunity concerns one remote station and one WSPR cycle on the selected band, after the station and geographic filters. Here, **station** means the exact callsign and full reported locator; different combinations are counted separately. Target activity is established as described in [Section 8.1.3](#sec-7-activity-eligibility). Who must have reported what depends on the analysis direction:

- **RX:** Target or another eligible receiver decoded the remote transmitter. If Target did not decode it, count a miss only when another receiver reported that transmitter and Target decoded another transmitter on the same band in the same cycle.
- **TX:** the remote receiver decoded Target or another qualifying transmitter. If it did not decode Target, count a miss only when this receiver reported another transmitter and a qualifying report of Target establishes that Target transmitted on the same band in the same cycle.

A successful decode means reception **by Target** in RX, or reception **of Target by this receiver** in TX. Once Target activity is established, count each station and cycle only once:

| Successful Target decode? | Other reports confirm the remote station's activity? | Outcome | Count as an opportunity? |
|---|---|---|---|
| Yes | No | The successful decode confirms its own opportunity. | **Yes — once.** |
| Yes | Yes | Successful decode with additional activity evidence. | **Yes — once.** |
| No | Yes | Confirmed miss: both stations were active, but no successful Target decode was reported. | **Yes — once.** |
| No | No | Unknown: the remote station's activity was not established. | **No.** |

Successes without additional activity evidence remain identifiable within the successful decodes. Confirmation by additional reports does not count the success again. In TX, a different receiver's report cannot show that this particular receiver was listening. In RX, another receiver can confirm the transmitter's activity, but cannot establish Target's activity. Unknown cases are excluded, and no SNR is invented for them.


**Additional confirmation for stations with few opportunities.** By default, a server-configured filter checks stations with **one or two confirmed opportunities**. Count these opportunities after the station, solar and geographic filters, but **before applying the station inclusion requirements**. As elsewhere, the counting unit is the normalized callsign and full reported locator. At least **one** of the station's opportunity cycles must satisfy the following rule:

- **RX Performance:** at least **three distinct receiver callsigns other than Target** must report the same transmitter callsign and full locator, on the same band in the same WSPR cycle.
- **TX Performance:** the receiver being checked must report a transmission during one of its opportunity cycles. At least **three additional receiver callsigns**, excluding that receiver and Target, must report the same transmitter callsign and full locator, on the same band in the same cycle. This may be a Target transmission or another transmission used to establish the receiver's activity. Reports of different transmissions cannot be combined to reach the required count.

Each normalized receiver callsign counts once for the matched transmission and cycle, regardless of duplicate reports or receiver locators. The check uses the underlying reports before they are reduced to activity flags.

The selected **Minimum confirmed opportunities per station** still applies. With the default ceiling of two, the extra check can affect minima of one or two; it has no additional effect at a minimum of three or more. Stations with three or more opportunities follow the existing inclusion rule. Server configuration can disable the extra check or change its opportunity-count ceiling; the requirement of **three other reporters** is fixed.

This check decides whether to include a station, rather than removing individual cycles. For a station that passes, all its original opportunities, successes, confirmed misses and SNR observations remain available. A station excluded by this rule is **insufficiently corroborated**, not a proven false decode. Different reporter callsigns also do not prove that the reports came from independent physical receivers. The analysis export records the completed run's effective policy and corroboration information.


<a id="sec-7-performance-rates"></a>
##### 8.3.2 Decode Rates and weighting

For each included station $i$, let $S_i$ be successful opportunities, $M_i$ confirmed misses, and $O_i=S_i+M_i$ all confirmed opportunities. Its Decode Rate is:

$$p_i=100\times\frac{S_i}{O_i}$$

Here $p_i$ is a percentage. A station enters this calculation only if $O_i$ meets **Minimum confirmed opportunities per station** and it passes the additional confirmation check when that check applies. These are the qualifying stations. The same $N$ stations enter both summaries:

| Summary | Calculation | What receives equal weight? |
|---|---|---|
| **Station-averaged Decode Rate** | $\frac{1}{N}\sum_{i=1}^{N}p_i$ | Each included station contributes one rate. |
| **Opportunity-level Decode Rate** | $100\times\frac{\sum_{i=1}^{N}S_i}{\sum_{i=1}^{N}O_i}$ | Each confirmed opportunity contributes once to the pooled totals. |

The station-averaged rate describes reception across stations: each station counts equally, including a station with 0% success. The opportunity-level rate describes the share of all confirmed opportunities that succeeded. If no stations meet the requirements, neither rate is defined. Where **Median Station Decode Rate** is selected, WSPRadar takes the median of the individual station rates, including zeros; see [Section 8.4.2](#sec-7-view-geography).

**Example.** Two stations have **90 successes out of 100 opportunities** and **5 out of 10**. Their rates are 90% and 50%, so the station-averaged rate is **70%**. Pooling gives **95 / 110 = 86.4%**: 95 successes and 15 misses, each counted once. The pooled rate is higher because the more successful station supplied more opportunities. The two values answer different weighting questions.


<a id="sec-7-performance-reach"></a>
##### 8.3.3 At-least-once Peer Reach

**At-least-once Peer Reach** is the percentage of included stations with at least one successful decode. In RX, these are transmitters heard by Target; in TX, they are receivers that heard Target. Let $N$ be the number of included stations and $H$ the number with at least one success:

$$\text{Reach (\%)}=100\times\frac{H}{N}$$

The count is $H$; **Reach** expresses it as a percentage of $N$. A station with one success and a station with many successes each add one to $H$. Both stations in the preceding example succeeded, so their Reach is **100%**, despite different Decode Rates. With no included stations, the Reach percentage is undefined.

For a fixed set of stations, adding observations cannot undo an earlier success. However, the stations meeting the requirements can change between runs, so a longer measurement window need not produce a higher Reach percentage.


<a id="sec-7-performance-snr"></a>
##### 8.3.4 Successful Target SNR

Successful Target SNR describes retained successful decodes, with strongest-report consolidation performed on the completed run’s selected SNR basis, as described in [Section 8.1.2](#sec-7-normalization-consolidation). Misses have no measured Target SNR. Adding marginal decodes can lower a successful-SNR summary even when reception and reach improve, so read SNR alongside Decode Rate and counts.

The time views show successful SNR, Decode Rate and the supporting counts, Decode Rate by distance and time, and each station's SNR deviations from its own run mean or median. The selected-station view shows the first two, with absolute SNR on the selected basis. See [Section 8.4.3](#sec-7-view-time) for the time plots and [Section 8.4.5](#sec-7-view-station) for the selected-station view. These results describe the confirmed opportunities visible in the reporting network; they do not measure unconditional receiver sensitivity, success over every attempted transmission or absolute station efficiency.

Open **Expert Review** to inspect SNR deviations from each station's own run mean or median. [Section 8.4.3](#sec-7-view-time) explains this optional view and its calculation.


<a id="sec-7-views"></a>
<a id="sec-7-8"></a>
#### 8.4 Scope and summaries across space and time

The same data can answer different questions depending on what counts equally. The Performance map gives each station equal weight; the Benchmark ΔSNR map and Spot-pair distribution give each pair equal weight. A view grouped by clock hour can combine several dates. This section explains which observations each view uses and how it combines them.

<a id="sec-7-view-scope"></a>
<a id="sec-7-9"></a>
##### 8.4.1 Scope, geography and filters

Distance and azimuth are calculated from Target QTH and the reported remote locators, using a spherical Earth of radius **6 371 km**. The azimuthal equidistant map is centered on Target QTH. Its distance boundaries are **2 500**, **5 000**, **10 000**, **15 000** and approximately **20 015 km**, with **22.5-degree** direction sectors. Locators identify grid cells, not measured antenna positions; these calculations are neither survey-grade positioning nor take-off-angle measurements.

**Maximum peer distance from Target** excludes stations **at or beyond** the chosen numeric limit before calculating summaries and exporting processed observations. **Worldwide (≈20 015 km)** includes every geographic location, subject to the other filters and evidence requirements. An Inspector selection narrows the displayed area **within the retained stations**. It neither deletes completed-run data nor restores stations excluded from the analysis.

The greatest shortest-path distance in this spherical model is approximately **20 015.087 km**, at the point opposite Target. The Worldwide map ends there, with an outer label of **≈20 015 km** and no empty outer ring. Its final distance class runs from **15 000 km** to this maximum; there is no separate class beyond 20 000 km. Labels round the endpoint, but station assignment uses the unrounded distance.

Existing configurations and shared links with a **20 000 km** limit retain that exact cutoff. A saved **22 000 km** limit opens as **Worldwide** with the same global coverage. An explicitly saved older distance-range selection also retains its original interval when loaded; it is not widened to the new final class.

For Performance, Target activity is established from global reports before geographic filtering. The moving-station filter likewise checks for changing-location callsigns among the otherwise eligible global reports before applying the distance limit.

The solar filter uses the Sun's elevation at **Target QTH at the WSPR-cycle timestamp**. This describes conditions at Target, not along the entire radio path or at every remote station. [Section 11.6](#sec-6-6) explains database retrieval limits and which source reports are considered.


<a id="sec-7-view-geography"></a>
<a id="sec-7-8-1"></a>
##### 8.4.2 Geographic summaries

**Map colors, hatching and unfilled segments.** Performance and Benchmark share the gray diagonal hatching and the English legend labels **Not qualifying** and **No observations**. Hatching means the map retains observations in that segment, but its metric's coloring requirements are not met. An unfilled segment has no observations retained for that map; it does not prove that no reception occurred. The **Map shading:** footer states the requirements.

Performance uses the same included stations for markers and map shading. Each station must first meet the station-level requirements. The segment then follows this rule:

| Stations meeting the station-level requirements in a segment | Appearance |
|---|---|
| At least the configured segment minimum | Colored by the station-averaged Decode Rate, including **0%**. |
| At least one, but fewer than the segment minimum | Gray hatched: **Not qualifying**. |
| None | Unfilled: **No observations**. |

A segment containing only stations that fail the station-level requirements remains unfilled, even if excluded observations exist. A valid **0% Decode Rate** means confirmed opportunities existed but no Target decode succeeded. Hatching changes neither which stations enter the rates nor the Inspector and statistics populations.

Benchmark retains all observed stations within the selected scope and filters. Its coloring requirements remain separate: station count and CI for ΔSNR; observed-station count and event share for ΔDecode.

**Benchmark** segment counts include all observed stations in the selected geographic area; ΔSNR summaries use only stations that meet the paired-evidence requirements. Sorting or filtering the station table, or selecting a row, does not change this segment population. The ΔSNR map pools the qualifying paired differences and calculates their arithmetic mean, giving every pair equal weight. That mean receives a color only when its pooled-pair CI and station count meet the requirements. The ΔDecode map uses the advantage in pooled total decodes. [Section 8.2.3](#sec-7-benchmark-aggregation) defines these summaries and the separate Spot-pair distribution.

**Performance At a glance** summarizes the entire completed analysis, using the configured **Minimum confirmed opportunities per station**.

| Card | What it summarizes |
|---|---|
| **Spot Decode Rate** | Successful decodes as a percentage of confirmed spot opportunities, with both pooled counts. |
| **Station Reach** | Stations with at least one successful decode as a percentage of all included stations, with both station counts. Each station is one callsign and full reported locator. |
| **Station Decode Rate** | The mean of the included stations' individual rates over the whole run. Every station counts equally, including 0% rates; the card also shows the contributing station count. |
| **Spot Path Distances** | Maximum, median and arithmetic mean distance in kilometres from Target QTH to the remote locator. Each successful spot contributes its distance once, so stations with more decodes have more weight in the median and mean. Without successful decodes, these values appear as dashes. |

A station's Decode Rate is its successful decodes divided by its confirmed opportunities. Inspector selections and the minimum station count per map segment do not change these whole-run summaries.

In Performance, <strong class="defined-term">Spot & Station Decodes</strong> in the Segment Inspector contains the Spots and Stations cards, followed by the SNR-band figure. Below the tables, the blue heading **Spot & Station Decodes: From Weak to Strong-Signal Reception** introduces that figure. **How to read this** beside it opens its reading guide.

The cards use the same layout as Benchmark and summarize the selected geographic area:

| Card | Counts and percentage | Meaning of its **Opportunities** column |
|---|---|---|
| **Spots**, left | Successful decodes / confirmed opportunities, and **Spot Decode Rate**. | Confirmed spot opportunities. |
| **Stations**, right | Stations with a success / all included stations, and **Station Reach**. | Included stations, counted by exact callsign and full reported locator. |

The selected distances and directions, minimum confirmed opportunities and any applicable additional confirmation requirement apply to both cards and the figure. Filtering the station table does not change their station population.

The Stations card shows counts on the left, **Station Reach** in the centre, and **Station-averaged Decode Rate** or **Median Station Decode Rate** in green on the right. The same selected rate appears in the green final table column, with a subtle background for every distance band and **All distances**. The asterisk refers to the Mean/Median explanation at the card footer. Displayed percentages use one decimal place; calculations use unrounded values.

**Summary statistic** selects **Mean** (default) or **Median** of the individual station rates over the complete selected scope. Every station counts equally, including stations with zero successes. This differs from the pooled Spot Decode Rate. **All distances** combines the individual station rates directly, rather than averaging the distance-band summaries. Station Reach and the complete-scope outcome bars keep their existing meanings.

The **Outcome of the complete selected scope (100.0%)** bar partitions all opportunities into successes and confirmed misses, or all included stations into those with and without a success. The cards retain four distance bands: **0–2 500**, **2 500–5 000**, **5 000–10 000** and **10 000–≈20 015 km**. A shared boundary belongs to the band starting there; the exact worldwide endpoint belongs to the last band.

Each table lists these bands and an **All distances** total. Spots shows successes, misses, opportunities and **Decode Rate**; Stations shows reached, never-reached and eligible counts, and **Reach**. Each band uses its own denominator: confirmed opportunities for Decode Rate and eligible stations for Reach. The all-distance percentages pool the relevant counts across the complete selected scope. The opportunity-level rate gives more weight to frequently observed stations. A percentage is undefined when its denominator is empty. The SNR-band figure below combines all selected distances.

In RX, a spot heard elsewhere only is a confirmed opportunity decoded by other receivers, with no Target decode or Target SNR measurement. In TX, a miss means the receiver did not decode Target during a confirmed opportunity; that receiver must itself have reported another transmitter. Target activity must still be established by a qualifying report on the same band in that cycle, as defined in [Section 8.3.1](#sec-7-performance-opportunities).

A station with a success is a transmitter heard by Target in RX, or a receiver that heard Target in TX. The cards and separate **All SNR** summaries include all successful decodes and these stations, including successes without usable SNR. The SNR-band bars exclude successes without usable SNR. At-least-once reception depends on the observation window and available activity; one success does not establish a high Decode Rate.

The figure **Spot & Station Decodes by SNR Band for CALLSIGN (RX/TX)** identifies Target and the analysis direction. It follows the selected distances and directions and **Minimum confirmed opportunities per station**. RX uses successful Target SNR normalized to **30 dBm TX**, with the axis **Successful Target SNR (dB, normalized to 30 dBm TX)**. TX uses the completed run's reported or normalized received-SNR basis, as stated on its axes. The figure has three rows and two columns.

Five plots group successful decodes into **5 dB SNR bands**, from weak signals on the left to strong signals on the right. Each band includes its lower boundary and excludes its upper boundary: **[−20, −15) dB** includes −20 dB but not −15 dB. An exact multiple of 5 dB belongs to the band starting there. The bands combine all selected Inspector distances and directions; they do not show separate distance series.

The station population follows the configured minimum opportunities and any additional confirmation requirement, with one station per callsign and full reported locator. The bottom-left plot groups individual station Decode Rates instead of SNR. In the five SNR plots, the blue **All SNR** bars are separate summaries of the complete selected scope. They are not extra SNR bands. The bottom-left summary is labelled **All** and divides all included stations into decoded and not decoded.

**Top left — Successful Spot Decodes.** Each successful spot with usable SNR counts once in its band. The Y-axis uses a **log₁₀** count scale; zero counts leave gaps. Its **All SNR** bar counts all successful decodes, including those without usable SNR.

**Top right — Stations with Successful Decodes.** The count scale is linear. Each station counts once in every band where it has a successful decode. The solid part identifies the station's **Weakest successful SNR band**; the hatched part, **Also heard at weaker SNR**, identifies stations already counted in a weaker band. A station may therefore appear in several band totals. Add only the solid parts to count distinct stations with usable SNR. The separate **All SNR** bar counts all distinct stations with a success, including those without usable SNR.

**Middle left — Spot Decode Rate.** Successful decodes in each SNR band are divided by **all confirmed spot opportunities** in the selected scope, including confirmed misses. The denominator stays fixed across bands. Each bar therefore contributes to the full-scope Decode Rate; it is not the probability of decoding a signal at that SNR, because misses have no measured successful SNR.

**Middle right — Station Reach.** Stations with a success in each band are divided by **all included stations**, including those never heard. The solid and hatched parts follow the same distinction as the top-right plot. This denominator also stays fixed, but stations can appear in several bands, so the percentages must not be added. The blue **All SNR** bars show the full-scope Spot Decode Rate and unique Station Reach.

**Bottom left — Station Decode Frequency.** Each station enters exactly one category according to its full-scope **Decode Rate**, successful decodes / confirmed opportunities: **0%**, **>0–10%**, **>10–25%**, **>25–50%**, **>50–75%** or **>75–100%**. Use unrounded rates. Positive categories exclude the lower boundary and include the upper boundary; exactly 10%, 25%, 50% and 75% belong to the category ending there.

The Y-axis is the share of all included stations, including zero-success stations. The X-axis is **Station Decode Rate (%)**, not SNR. For a nonempty population, the six categories sum to 100%. The five positive categories together give Station Reach. The **0%** category has **Not Decoded** above its percentage.

The separate **All** bar also totals 100%: gray **Not Decoded** counts stations without a success, and blue **Decoded** counts stations heard at least once. This narrow bar has the same displayed width and horizontal centre as the summary bars above it. The distribution includes successes without usable SNR and does not change with Mean/Median.

**Bottom right — Station-averaged Decode Rate or Median Station Decode Rate.** For each station, divide its successes in an SNR band by **all its confirmed opportunities** in the selected scope. Then take the selected **mean** or **median** of these percentages. Every station counts equally, including those with zero successes in that band. The station population and each station's opportunity denominator stay fixed.

The blue **All SNR** bar is calculated separately from each station's full-scope rate, including successes without usable SNR. It is not an average of the band summaries. Its **Mean** matches the map estimator for the same stations; combining map-sector means requires weighting them by the included station count.

Mean contributions across SNR bands add to the full-scope mean when all successes have usable SNR. **Medians are not additive**: every band median can be 0% even when the separately calculated overall median is positive. A zero median is a valid result, not missing evidence.

**Summary statistic** selects **Mean** (default) or **Median**, independently of the temporal controls. It also sets the red dashed vertical SNR markers in the five SNR-band plots. Their legends show the selected SNR value in dB to one decimal place.

| Marker location | Values summarized | Figure labels |
|---|---|---|
| Two left-column SNR plots | Individual successful spot SNRs. | **Mean spot SNR** / **Median spot SNR** |
| Top right and middle right | One weakest successful SNR per station with at least one usable successful SNR. | **Mean weakest station SNR** / **Median weakest station SNR** |
| Bottom right | First summarize each station's successful SNR, then combine these station summaries with equal weight. | **Mean of station mean SNR** / **Median of station median SNR** |

Only stations with usable successful SNR contribute to these markers. Stations never heard still contribute zeros to the rate population but have no SNR value. The markers locate SNR summaries; they are neither uncertainty intervals nor means or medians of bar heights. The selector changes these markers and the mean/median station rates in the figure and Stations card. Counts, station overlap, Spot Decode Rate, Station Reach and the frequency categories remain unchanged.

**Successes without usable SNR** remain in the cards, **All SNR** summaries and Station Decode Frequency categories, but not in the five SNR-band distributions or their markers. SNR-band counts and additive mean contributions can therefore fall short of the full-scope summaries. Empty denominators have no defined percentage.

The band-by-band **Station Reach** percentages describe successes within each band. The **All SNR** bar and Stations card count each station with a success only once over the complete selected scope.

**Retained distance-summary evidence.** Historical Decode Rate distance profiles grouped stations by calculated distance from Target QTH. Their finer distance bins were separate from the four broad bands in the card tables. Bin width followed the configured maximum peer distance:

| Maximum peer distance | Distance-bin width |
|---|---|
| 2 500 km | 250 km |
| 5 000 km | 500 km |
| 10 000 km | 1 000 km |
| 15 000 km | 1 500 km |
| Worldwide, or 20 000 km from an existing configuration or shared link | 2 500 km |

Changing the Inspector's selected distance range retained that width. Bin edges started at integer multiples from **0 km**; the last bin was adjusted to the configured maximum or physical global endpoint. In Worldwide view, the final bin spans **17 500 km** to approximately **20 015 km**, combining the former 17 500–20 000 km bin with the small possible region beyond 20 000 km. The final selected upper boundary is included **among already-retained peers**; this does not override the analysis's maximum-distance exclusion. Gaps between disjoint selected ranges remain gaps rather than bins with zero evidence.

For each distance bin, these retained summaries distinguish the arithmetic mean of individual station rates from the opportunity-level rate calculated from pooled successes and confirmed opportunities.


<a id="sec-7-view-time"></a>
<a id="sec-7-8-3"></a>
##### 8.4.3 Chronological evidence

**Chronological views keep the sequence of the run.** Time bins start at the selected UTC start and use the chosen width; the final bin can be shorter. **Time basis** changes the displayed clock and dates, not the bin boundaries, observations in each bin or statistics. Empty intervals stay empty; no **0 dB** or **0%** observations are inserted. Offered widths and defaults depend on the complete run duration, not on the span of available reports. A valid saved width can remain available outside the usual choices; see [Section 10.5](#sec-5-5).

**Benchmark ΔSNR** pools retained spot pairs from qualifying stations within each time bin. **ΔSNR statistic: Median / Mean** selects the median with IQR or the arithmetic mean with its configured pointwise CI. The density, eligible pairs, bin membership and equal-pair weighting do not change; stations with more pairs contribute more.

New analyses default to Mean independently for segment and selected-station plots. A current configuration without a saved statistic also defaults to Mean at that level; explicit saved choices are honored. The Milazzo demo opens both levels with Median. Coverage separately keeps all eligible Paired and one-sided outcomes and the presence of distinct stations, using the two advantage metrics in [Section 8.2.4](#sec-7-benchmark-coverage). Paired observations below the ΔSNR requirements and one-sided observations can still appear in coverage even when ΔSNR is empty.

**1. Successful SNR over Time and by clock hour**

**TX Performance SNR basis:** **SNR TX Normalization to 30 dBm**, to the right of **Operating Band**, is off for a new analysis: successful SNR then uses the received value reported by the remote receiver. On applies `reported SNR + 30 − reported TX power (dBm)` and labels the result as normalized to 30 dBm (1 W).

RX Performance and Benchmark ΔSNR retain their normalized SNR basis; Benchmark’s raw-SNR decoding-reach views also remain unchanged. This scientific choice applies consistently to station medians, the SNR-band figure, temporal means/medians and intervals, segment run baselines and residuals, selected-station/focused evidence, and exports. It does not change success/miss counts or Decode Rates. Changing it requires a new analysis run; it is not a display-only switch over previously normalized evidence.

The two density panels show successful Target SNR on the completed run's selected basis: raw reported received SNR for TX Performance with normalization off; otherwise the **1 W (30 dBm) reported-power basis**. The axis names the basis; **Normalized Target SNR (dB @ 30 dBm)** applies only to the normalized view. Absolute SNR means no station baseline has been subtracted.

**Mean** adds the arithmetic mean and its configured pointwise CI; **Median** adds the median and IQR, showing the middle half of the same observations. Switching between them leaves the absolute-SNR density unchanged. This figure does not require the three successful observations needed for a station baseline, so it can include stations missing from the deviation figure. A changing mix of decoded stations can change absolute SNR even if no individual radio path changes.

**2. Decode Rate over Time and temporal support**

The **TX Stations** row in RX and **RX Stations** row in TX show station participation. In each chronological bin, every contributing station adds one unit to the station bar, divided according to its own Decode Rate. A rate of 40% adds **0.4** success support and **0.6** miss support. RX labels these parts **Heard by Target** and **Heard by others only**; TX uses **Target heard** and **Other signals heard only**.

These fractions are not counts of stations heard at least once. Their success share is the existing equal-station diagnostic, whereas **both displayed rate lines use pooled confirmed opportunities**, H divided by H + M. The opportunity row counts each confirmed success and miss directly. For a single selected station, the station fraction and pooled rate agree within a populated bin, but the station bar and opportunity bar still describe different counts.

Both rows include stations that meet the opportunity requirements even if they have too few successes for an SNR baseline. In the clock-hour view, bars show average station participation or opportunities per represented date, while rate lines pool successes and opportunities across dates. The exact date-hour denominators, station-bar split and an example are given in [Section 8.4.4](#sec-7-view-folding).


**3. Decode Rate by Distance over Time and by clock hour**

Each colored heatmap cell shows **Decode rate (%)** as `100 × H / (H + M)`, where H counts retained Target successes and M counts confirmed opportunities without a Target decode. Folded cells sum those counts for the same clock hour across dates before dividing; they do not average station percentages, daily percentages or chronological-cell percentages.

Both panels use one shared color range from **0% to the highest finite observed Decode Rate** across the chronological cells and the visible folded cells for the selected scope, time-bin width and time basis. An unavailable folded panel does not contribute a hidden maximum. Values remain actual percentages: the strongest color at a maximum of 20% still means 20%, not a relative score of 100%. The range can change between figures when scope, binning or time basis changes, so read the numerical legend before comparing colors across different figures.

If all available rates are zero or there is no valid numerical rate, the plot explicitly identifies a **0–1% display fallback** so that the legend has a visible range; this creates no 1% observation. A cell with 20 successes in 100 opportunities is 20% even if it is the panel's highest rate. No opportunities means missing evidence; zero successes with a positive denominator is a valid 0% cell.

The vertical axis shows calculated distance, increasing from zero at the bottom. Both panels use the Performance distance-bin boundaries and selected geographic scope. The existing rule for displaying support dots is unchanged. **Time aggregation** sets the chronological bin width; clock-hour bins remain one hour in the selected **Time basis**.

For one selected station, identified by exact callsign and full locator, the distance heatmap is omitted: its single distance bin would repeat the temporal Decode Rate. The calculated distance from Target follows the locator in each selected-station figure subtitle. Multi-station views retain the distance heatmap.

In the SNR density panels, **Relative spot density (% of panel maximum)** is `100 × cell observation count / maximum cell count in that panel`. Each chronological or clock-hour panel has its own maximum across all time/hour and SNR cells; columns are not normalized separately. Thus 100 identifies the busiest cell, not 100% of the observations. A shared colorbar does not make raw counts comparable between panels; compare their supporting counts instead. Lower density is blue and higher density orange/red. Vertical position shows SNR in the absolute-SNR figure and SNR deviation in the fourth segment figure.

**Segment Temporal Evidence** contains successful SNR as figure 1, Decode Rate and supporting counts as figure 2, Decode Rate by distance/time as figure 3, and station-baseline deviations as figure 4. **Selected Station Evidence** contains figures 1–2 only. These temporal weightings do not change the station-averaged and opportunity-level definitions of the standalone map and distance statistics.

**Expert Review** holds figure 4 and is collapsed by default; the first three segment figures are directly visible. Its label is **Expert Review — SNR deviation from each station’s own run mean** in Mean mode or **Expert Review — SNR deviation from each station’s own run median** in Median mode. Opening it changes neither data nor calculations. All four segment figures remain in the results package, even when the panel is collapsed; selected-station results contain two figures, without a distance heatmap or deviation view.

**Performance successful-SNR deviation** compares each station with its own run baseline. The remote stations are transmitters in RX and receivers in TX. A station needs at least **three successful observations with valid numerical SNR on the selected basis** over the complete included run window. **Mean** subtracts their arithmetic mean; **Median** subtracts their median. Each exact callsign and full reported locator has its own baseline.

For example, **−7 dB** against a **−10 dB** baseline gives a **+3 dB deviation**. Zero means the station's selected successful-SNR baseline, not equality between Target and Reference. Changing time bins, display clock or Inspector selection does not recalculate that run baseline.

Each successful Target observation with valid numerical SNR contributes one value on the completed run's selected basis. One observation means one included opportunity after duplicate reports have been consolidated, not one value per duplicate database report. Chronological bins pool these individual observations; clock-hour bins pool those from matching hours across represented dates. Neither first averages stations, station/date/hour groups or daily summaries. Stations and dates with more observations therefore contribute more weight. A confirmed miss enters the Decode Rate denominator but has no Target SNR; no zero or invented weak SNR is inserted.

The deviation view likewise pools individual residuals directly within time bins or matching clock hours. Density, Mean/CI and Median/IQR are calculated from these deviations, not from prior station-bin or daily summaries. Station identity chooses the baseline but does not give each station equal weight. Switching Mean/Median can change both the residuals and their summaries. The CI calculation treats the observed run baselines as fixed and does not add uncertainty from estimating them. Selected-station views omit this fourth figure and retain absolute SNR on the selected basis.

<a id="sec-7-view-folding"></a>
##### 8.4.4 Combining dates by UTC or local solar hour

With **Time basis: UTC**, <strong class="defined-term">UTC-hour folding</strong> groups observations from the same clock hour across dates. It reveals hour-of-day patterns but removes the sequence of individual dates. This differs from chronological binning: starting at **12:17 UTC**, a **1h** chronological bin spans **12:17 to 13:17**. Folding uses clock hours such as **12:00 to 13:00**, counting only the part inside the selected window.

**Time aggregation** controls only the chronological panels and retains the existing interval choices. The adjacent **Time basis** control selects **UTC** or **Local Solar** for the chronological and folded SNR, decode and coverage panels at that level. Segment plots and selected-station plots keep independent clock choices; focused plots follow the selected-station clock. Folded panels always use fixed one-hour bins. New analyses default to UTC at both levels; explicit saved values are honored. The Milazzo demo explicitly uses Local Solar and Median at both levels; the other Benchmark demos use UTC and Mean.

For Benchmark, **ΔSNR statistic** sits beside **Time basis** and applies to both chronological and folded ΔSNR plots at that level. Segment and selected-station statistics can be selected independently, with Mean as the new-analysis default at both levels. It changes the statistic and interval within the existing bins, not pairing, calibration, qualification or weighting. **Median** retains IQR; **Mean** uses the CI for the mean of those same pooled pairs. Benchmark Statistics remains fixed to the selected analysis and scope.

In Performance, **Time aggregation**, **Time basis**, and **SNR statistic: Median / Mean** have the same layout as Benchmark. The segment and selected-station views can set these three controls independently; they share the confidence level. New analyses use **Mean**, **UTC**, and **95%** confidence; explicit saved choices are honored.

The statistic applies to both SNR panels at its level and reuses completed-run observations without a database request. It changes the summary line and interval, and for segment deviations also the run baseline and density. It leaves the absolute-SNR density observations, opportunity counts, Decode Rates, map qualification, the SNR-band summary and fixed station-table median unchanged. Changing confidence refreshes the pointwise mean intervals without invalidating the completed run.

Changing **Time basis** relabels dates and times in the chronological panel without changing its bins or statistics. In the clock-hour panel, it regroups observations and can therefore change hourly summaries. **Local Solar** uses the Sun's time at Target QTH, with solar noon at 12:00. It is neither civil time nor daylight-saving time. Source timestamps remain UTC.

The solar reference applies to Target, not to every remote station or the whole radio path.

Local Solar means **local apparent solar time**. Target's locator supplies the longitude correction. The date-dependent equation of time is sampled daily across the run and its boundaries, then interpolated to the distinct WSPR-cycle times; the offset is not constant for the entire run.

Observations are regrouped before hourly summaries. Previously calculated medians are not shifted, and pairing, filters, qualification, raw evidence and whole-run statistics do not change. Switching clocks reuses retained data without a database request. Folded date membership, represented dates and hourly coverage denominators all follow the selected clock, including solar-date rollover. [US Naval Observatory: The Equation of Time](https://aa.usno.navy.mil/faq/eqtime).

Different layers combine their evidence differently:

| Layer | What contributes at one hour in the selected basis | How it is summarized |
|---|---|---|
| **Benchmark ΔSNR** | Retained spot pairs from qualifying stations across represented dates. | Selected Median with IQR, or Mean with its configured pointwise CI, over the same pooled pairs; frequently observed paths contribute more values. |
| **Performance absolute SNR** | Every included successful Target observation with valid numerical SNR on the selected basis in that clock hour across dates. | Mean with its pointwise CI or Median with IQR of those individual observations; no prior station/date summary or run-baseline subtraction. |
| **Performance SNR deviation** | Every successful observation minus its exact station/full-locator run mean in Mean mode or run median in Median mode; at least three successes with valid numerical SNR establish the baseline. | Pool the individual residual observations at that clock hour, then calculate Mean/CI or Median/IQR. More observations mean more contributions; total weights follow observation counts, without forcing equal totals for stations or dates. |
| **Performance station participation by clock hour** | Station/date/hour presences and each station's successes and opportunities pooled across dates at that hour. | Average station presences per date, with the station-based fractional success/miss split. This supplies context; its fraction is not the pooled rate line. |
| **Performance temporal Decode Rate** | All retained successes and confirmed opportunities in the selected hour, pooled across dates. | Divide pooled successes by pooled confirmed opportunities. Both temporal support-row lines and distance/time cells use this rate; the station-support stack remains context, not its denominator. |

Successful SNR uses the individual observations defined in [Section 8.4.3](#sec-7-view-time): duplicate reports contribute no extra values, and confirmed misses contribute no SNR. Pooling these observations gives greater weight to stations and dates with more successful decodes.

**Clock-hour views require at least two represented dates.** For Performance, a represented date has at least one qualifying confirmed opportunity somewhere in the selected area and window. These dates enable both supporting-count and SNR panels, even if usable SNR is available on fewer dates.

Benchmark coverage uses dates with any retained outcome. Its ΔSNR layer separately requires dates with finite paired ΔSNR from qualifying stations. A date with spot pairs and a second date with only one-sided outcomes can therefore enable folded coverage without enabling folded ΔSNR.

**Clock-hour support bars average over included date-hour slots.** A represented date's clock hour enters the denominator whenever it overlaps the selected window, even if that hour contains no observations. Hours outside the window do not count. A partly overlapping boundary hour counts as **one complete slot**, without weighting by minutes covered; this can lower the average.

These bars include stations that meet the opportunity requirements even if they lack the three successes needed for an SNR baseline. They show the average number of station presences or opportunities in the clock hour across represented dates. For example, six and zero opportunities in the same included hour on two represented dates give an average of three; no extra misses are invented.

To split the station bar, first pool each station's successes and opportunities for that clock hour across dates and calculate its rate. Then average these station rates with equal weight to obtain the success and miss shares. The rate curves instead pool H and M across all stations and dates. Their percentages are calculated independently of the station-bar split and the daily averaging of bar heights.

**Benchmark coverage classifies stations separately on each date.** For each date and hour in the selected clock, count **Both observed**, **Only Target** and **Only Reference**, then sum these daily counts and divide by the represented date-hour count for the upper bars. A station observed only on Target's side on Monday and only on Reference's side on Tuesday is not Both observed on either day. The Station Reach Advantage line uses sums of the daily Target and Reference station totals, rather than averaging daily ratios.

The lower bars similarly divide pooled native outcome counts by the represented date-hour count. Their ΔDecode line uses pooled decode totals across dates. Neither line unions station membership across the whole period or averages the daily advantage values.

Check the chronological view before calling an hour-of-day pattern recurrent; folding does not show that it occurred on every date.

Folding changes the grouping for display, while preserving the dated UTC timestamps and station identities in the retained data. The IID calculation assumes the pairs pooled into a bin are independent, including pairs from different stations or dates. Neither folding nor an available per-station CI establishes that assumption.


<a id="sec-7-view-station"></a>
<a id="sec-7-8-4"></a>
##### 8.4.5 Selected Station Evidence

Selected Station Evidence normally follows **one station, identified by exact callsign and full reported locator**. In **Benchmark and Performance**, it uses that station's full completed-run data, independently of Inspector geography and the optional station-list filter. Hiding the station from the list does not deselect it or change its full-run metrics. Selection does not alter earlier matching or inclusion rules. An explicit Drill-Down focus can narrow the displayed interval.

In Benchmark Station Insights, **Median ΔSNR** and **Mean ΔSNR** use the same retained paired differences for the selected callsign and full locator. The adjacent CI column, **ΔSNR 95% CI (dB)** at the default level, shows the symmetric **± half-width** for that station's mean at the configured confidence level.

After the station identifiers, the default columns are **Median ΔSNR → Mean ΔSNR → ΔSNR CI → ΔDecode → Paired spots → One-sided spots**. The CI heading includes the confidence percentage. Pair counts and separate Target-only and Reference-only counts stay visible. Sample **SD of paired ΔSNR** is available through optional columns and exports, but hidden by default. Full CI bounds and numerical details remain in the export. Station inclusion rules, list filters and full-analysis metric scope are unchanged.

| Analysis | Selected-station summaries |
|---|---|
| **Benchmark** | Chronological and folded ΔSNR summaries use the station's retained paired evidence over the full filtered period. Coverage separately retains Only Target, all Paired observations in one green category, and Only Reference. Its curve is that station's pooled ΔDecode, using the same signed ratio axis as the segment's Spot-level row. |
| **Performance** | Two figures: absolute successful Target SNR on the selected basis and Decode Rate with temporal support. The calculated distance from Target follows the locator in each figure subtitle; the redundant single-station distance heatmap is omitted. Chronological and folded Mean/CI or Median/IQR use individual successful observations directly. No run baseline is subtracted and no deviation figure appears. Success/Miss counts and pooled Decode Rate describe that same full-run path. With one station, its station fraction and pooled rate coincide in populated bins, while station presence and opportunity volume remain different support measures. |

With outlier reporting enabled, Benchmark can also select **multiple stations** and pool their qualifying spot pairs for ΔSNR. Each pair counts equally; stations do not receive equal weight. **ΔDecode over Time** is available only for **one selected station**. Selecting stations, filtering the list or zooming does not recalculate qualification or rerun detection.

**Focused Drill-Down shows individual retained observations at their actual WSPR-cycle times:** one consolidated paired ΔSNR value for Benchmark, or one successful Target SNR on the completed run's selected basis for Performance. These are processed observations, not untouched database rows or time-bin summaries. Benchmark's focused ΔSNR plot uses the retained pairs; one-sided observations have no paired ΔSNR.

Focused plots use the selected **Time basis** for their displayed clock, including event markers and baseline intervals. The Drill-Down table and focus editors retain UTC so every observation remains traceable to its original cycle.

**Outlier Focus** can show a candidate together with its complete supported baseline periods before and after, even when they extend beyond an ordinary focus interval. It uses the completed detector result without fitting the detector again to the focused data. The local baselines and departure guides describe that candidate; they are neither confidence intervals nor independent qualification tests. Changing focus or display bins changes the view, not the completed result.


<a id="sec-7-view-spread"></a>
<a id="sec-7-8-5"></a>
##### 8.4.6 Spread and display scales

**Spread is not confidence.** A Q1–Q3 band spans the middle half of the contributing values; a min–max interval spans their full range. Neither is a confidence interval.

In temporal median views, including Benchmark **Median** mode, a median marker needs only **one** value. Adjacent medians are connected only if **each bin has at least three** values. An IQR band joins adjacent bins only if **each has at least five**; isolated supported bins have no band, and unsupported bins break the connections. Depending on the view, the values are spot pairs, individual successful Target observations or individual station-baseline deviations.

The red dashed Mean/Median markers in Performance **Spot & Station Decodes** instead summarize successful SNR as described in [Section 8.4.2](#sec-7-view-geography). They do not show IQR or confidence intervals.

**Mean-mode intervals describe uncertainty in a mean.** Benchmark Mean mode shows the configured CI for each bin mean, using its unrounded lower and upper bounds. The legend is **Bin 95% CI** at the default confidence level and follows the chosen percentage. These are pointwise intervals for individual bins, not a simultaneous confidence band for the whole curve. If a mean is defined but its CI is unavailable, the mean remains visible without a band; no IQR is substituted.

A mean marker can appear with **one pair**. Adjacent mean markers connect only when **each bin has at least three pairs**. An available CI needs at least **two pairs** and spans the actual bin edges, including an isolated supported bin. These rules establish mathematical availability, not statistical coverage.

In Median mode, the red global reference line and the nonlinear ΔSNR axis centre use the median of all retained qualifying pairs in the displayed scope. Mean mode uses the arithmetic mean of those same pooled pairs and a gold reference line. Both chronological and clock-hour panels share this reference. Changing time bins or folding does not average station means or bin means. The axis still shows individual paired ΔSNR values; the selected statistic describes the bin overlay.

**Performance uses the same Student-t method for individual observations.** Absolute segment and selected-station CIs use retained successful SNR values on the selected basis; segment-deviation CIs use the corresponding individual deviations. Chronological and clock-hour bins do not replace these observations with station-bin or daily means. Confidence level changes the interval bounds, not the mean or contributing observations. Performance dB axes remain linear.

**CI continuation beyond the displayed range.** Each temporal SNR or ΔSNR figure uses a shared vertical range for its chronological and clock-hour panels. The range comes from all contributing observations and density-bin edges, with display padding. Benchmark also keeps absolute 0 dB and its statistic-centered scale. CIs do not enlarge the range; changing time aggregation alone leaves it unchanged when the contributing values are the same.

A hollow △ at a bin's upper plot edge means its upper CI bound extends above the displayed range; a hollow ▽ at the lower edge means its lower bound extends below it. Both appear when both bounds extend beyond the range. If any interval extends off-scale, the footer says **△ ▽ CI extends beyond displayed range**. Only the drawn band is clipped: the numerical bounds do not change, and the plot edge is not an interval endpoint.

A CI can extend beyond the observed sample range, especially with few observations. Unavailable CIs have no continuation marker. These markers apply to Mean-mode CIs, not Median-mode IQR bands, and work identically in previews, enlarged figures and exports.

Mean intervals assume independent contributing observations; pooling across stations or dates does not establish independence. For segment figure 4, the run baselines are treated as fixed, without adding uncertainty from their estimation. A calculated, narrow or zero-width CI therefore does not establish independence, zero uncertainty, a causal hardware effect or simultaneous coverage of all bins. The CI describes uncertainty of a mean under this model; IQR describes the observed spread.

**Read ±h as a half-width.** The **Spots** table and **Station Insights** show the CI beside its mean as **± half-width**. A Mean ΔSNR of **+3.20 dB** beside a CI entry of **±0.49** corresponds to **[+2.71, +3.69] dB**. The displayed value is not the full interval width, SD or standard error. Where no mean is adjacent, readouts show both, for example **Mean ΔSNR +3.20 dB; 95% CI ±0.49 dB** at the default level. Confidence-level headings and tooltips follow `ci_alpha`. A missing CI is unavailable, not **±0.00**; a positive half-width small enough to round to zero retains additional digits. Numeric exports retain full-precision bounds and half-width.

The symmetric ± display applies only when bounds are symmetric about the estimate. A future asymmetric method must show its full interval or separate lower and upper margins, without recentering or averaging them.

**<strong class="defined-term">Density colors</strong> are relative within each panel.** The busiest cell is assigned **100**, and other cells are scaled in proportion to their counts. This does not mean that cell contains 100% of the observations. Compare the accompanying counts when judging the amount of data in different panels.

**ΔSNR map colors** show the <strong class="defined-term">pooled mean paired ΔSNR</strong>. Symmetric color limits adapt to the segment means that meet the requirements, so compare numerical legends across runs. Coloring requires the station minimum and an available, non-degenerate pooled-pair CI within the selected half-width limit. Changing confidence changes the CI, not the mean, and can change which segments receive a color. Coverage is <strong class="defined-term">nominal for each segment separately</strong>, not simultaneous across the map. The precision limit is not a significance test; a qualifying interval may include zero.

**ΔSNR binning and axes.** The Spot-pair histogram normally uses **1 dB** bins, **0.5 dB** for a clear half-dB lattice, and wider bins for broad ranges. The two station histograms use the shared adaptive binning described in [Section 8.2.3](#sec-7-benchmark-aggregation). Temporal density cells remain **1 dB** high and shift with Reference correction. For the same retained observations, cells and observations move together without changing cell counts or relative colors. Display binning does not round the observations or change their statistics; fractional values need not lie at cell centres.

Benchmark ΔSNR time axes compress the tails around the selected scope-wide statistic: pooled median in Median mode or pooled mean in Mean mode. Histogram axes retain their own centres. Absolute **0 dB** stays visible. Read the labelled dB coordinates rather than estimating differences from spacing. In histograms, bar **length along the percentage axis**, not displayed area, gives the share. These display transformations change neither values nor counts, means, medians, quartiles or CI bounds. Performance successful-SNR axes remain linear in dB.

**ΔDecode ratio legend.** **2×** on the Target side means twice as many Target decodes as Reference; **2×** on the Reference side reverses that comparison. Blue favors Reference; warm colors favor Target. The center **1×** marks exact equality, but its central color band also contains near-equal ratios below the first boundary on either side. That band does not establish statistical equivalence.

The legend chooses the finest preset that covers the largest finite advantage among the **visible, supported segments**, using the larger setup total divided by the smaller. Exclusive reception uses preset C. Preset selection changes presentation only, not the decode totals, their ratio or qualification.

| Preset | Ratio boundaries on each side of 1× | Covers largest finite ratio up to |
|---|---|---:|
| AA | 1.05×, 1.10×, 1.15×, 1.20×, 1.25× | 1.25× |
| A | 1.25×, 1.5×, 1.75×, 2×, 2.5×, 3× | 3× |
| B | 1.25×, 1.5×, 2×, 3×, 5×, 10× | 10× |
| C | 1.25×, 2×, 3×, 5×, 10×, ≥20× | Larger ratios and exclusive reception |

For preset C, **≥20×** includes large finite ratios. **Exclusive** means the other setup has zero decodes; it is not a finite ratio of 20. Boundaries describe color intervals — for example, **1.5×–1.75×** is one band. Equal-width swatches are categories, not a linear ratio scale. Read the numerical boundaries across runs: matching color intensities under different presets need not represent matching advantages.


<a id="sec-7-claims"></a>
<a id="sec-7-10"></a>
#### 8.5 How strong is the conclusion?

<strong class="defined-term">Descriptive statistics</strong> summarize the observations included in a run. <strong class="defined-term">Statistical inference</strong> uses those observations and justified assumptions to estimate behavior beyond the recorded data, often with a measure of uncertainty. A correct summary does not by itself establish how a station will perform in another period or what caused a difference. Check the supporting data and experimental design before extending the claim; [Chapter 9](#sec-8) provides wording examples.


<a id="sec-7-dependence-bias"></a>
##### 8.5.1 Dependence and bias

**Why WSPRadar reports confidence intervals for mean ΔSNR**

Each included spot pair supplies a Target–Reference SNR difference for the same remote station, band and WSPR cycle. This controls the timing of the comparison and allows propagation fluctuations shared by both setups to cancel in their SNR difference. The resulting paired differences provide a practical basis for estimating an average relative advantage — a measurement approach supported by standard paired-analysis methods and WSPR antenna-comparison models. <a href="#ref-31">[Ref-31]</a>, <a href="#ref-1">[Ref-1]</a>

Averaging can reduce the influence of random fluctuations, making the mean more precisely estimated than an individual observation. With sufficiently many independent, identically distributed observations of finite variance, the sampling distribution of the mean approaches a normal distribution even when individual ΔSNR values are not normally distributed. A confidence interval describes the precision of this estimated average under the statistical model, rather than the spread of individual spot pairs. <a href="#ref-31">[Ref-31]</a>, <a href="#ref-32">[Ref-32]</a>

WSPRadar uses a **nominal Student‑t confidence interval**, calculated from the observed sample variability and the number of contributing observations. The calculation accounts for the variance being estimated from the data and is exact for independent observations from a common normal distribution. For individual-station and pooled-pair results, the contributing observations are paired ΔSNR values. For the mean of station means, they are the individual station means. <a href="#ref-31">[Ref-31]</a>, <a href="#ref-32">[Ref-32]</a>

**Independence remains an assumption.** Pairing does not guarantee that repeated observations on a path, or station means sharing propagation and operating conditions, are independent. The calculation uses the observed contributing count without correcting for dependence; its stated confidence level is therefore conditional on that working model. The CI concerns the selected paired-observation population and does not include systematic calibration uncertainty or establish calibrated antenna gain. <a href="#ref-1">[Ref-1]</a>, <a href="#ref-32">[Ref-32]</a>, <a href="#ref-33">[Ref-33]</a>

**1 000 spots are not 1 000 independent experiments.** Repeated cycles share equipment and propagation; nearby stations share conditions; neighboring time bins are related; one interference or ionospheric event can affect many observations. The two phases of an extended-WSPR sequence add observations within a run, not independent experimental repetitions.

Giving each station equal weight reduces the influence of prolific reporters. Medians reduce sensitivity to isolated extremes. Neither removes systematic calibration errors, reporting differences or propagation bias, or makes observations independent.

**A descriptive mean or standard deviation does not require Gaussian data.** A mean describes an arithmetic average; standard deviation describes spread around that mean. Both can summarize a finite observed dataset without assuming a normal, bell-shaped distribution. Their usefulness depends on the quantity being summarized and the distribution's tails or extreme values. A median describes the middle value, and IQR measures the width of the middle half; these answer different questions and are less sensitive to extreme magnitudes. Choose the statistic for the intended quantity, rather than treating a non-normal distribution as a reason that a mean is invalid <a href="#ref-30">[Ref-30]</a>.

Estimating uncertainty beyond the included observations requires a justified model of sampling and dependence. Non-normal data alone do not make inference impossible. WSPRadar provides an <strong class="defined-term">IID Student-t baseline</strong>: IID means independent and identically distributed observations. It applies to individual station means, qualifying pooled-pair means, temporal/folded-bin means, pooled-pair map means and equally weighted averages of qualifying station means. Pairing alone does not establish its independence assumption. WSPRadar supplies no p-values, statistical power, automatic significance badges or causal-effect estimates. Treating positively dependent reports as independent can understate uncertainty about future performance or a wider population.

**How the baseline is calculated.** For retained paired differences `d₁, …, dₙ` in the exact displayed scope, the arithmetic mean is `d̄`. Sample SD uses denominator `n − 1`, and the baseline standard error is `s / √n`. The two-sided interval is:

$$\bar d \pm t_{1-\alpha/2,\,n-1}\frac{s}{\sqrt n}$$

Internally, `ci_alpha` is the total two-sided tail probability, not a calculated p-value; it must satisfy `0 < ci_alpha < 1`. The confidence level is `100 × (1 − ci_alpha)%`: the default `0.05` gives **95%**, while `0.10` gives **90%**. `evidence_confidence_interval_method = iid_student_t` names this initial baseline in saved configurations. The current version-1 default `evidence_confidence_level_percent = 95` corresponds to the internal `ci_alpha = 0.05`. The count `n` is the observed qualifying pair count, not an estimated effective independent sample size. [NIST's mean-CI definition](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm) gives the same symmetric Student-t form; its [sample-SD definition](https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm) uses `n − 1`.

With no retained values, no mean is defined. With one value, the mean can be calculated, but sample SD, standard error and CI are unavailable; the existing qualification rules still govern whether that mean is displayed. Zero sample variance gives a degenerate sample and a zero-width model interval. It does not establish an exact physical offset. Evidence thresholds describe support; they do not guarantee interval coverage.

For the aggregate <strong class="defined-term">mean of station means</strong> in the Stations summary, the CI is unavailable with fewer than two contributing stations, while any defined mean is preserved. With two or more station means, zero unrounded across-station SD yields a degenerate zero-width interval with explicit status. The map uses a different interval: it counts qualifying pairs and calculates SD across their paired differences. A degenerate station-mean CI does not by itself determine the map’s pooled-pair CI status.

**What the interval assumes and excludes.** Student-t coverage is exact under the usual independent, common normal-distribution sampling model and is otherwise an approximation where its conditions are adequate. A normal-looking histogram or a nonsignificant diagnostic test does not prove independence. The interval concerns the mean of the process represented by the retained pairs and selected scope. It is not a prediction interval for an individual spot, does not include systematic calibration error, and does not remove selection caused by requiring both decodes. A narrow interval does not establish a stable advantage on every cycle.

This baseline has not been established as a WSPR-wide calibrated method. Before making that claim, representative retained paired datasets need assessment of chronological behavior, gaps, dependence, distribution shape, small samples, changing station composition and weak-signal selection, together with interval-width and known-effect simulation-coverage comparisons against at least one time-aware method. A universal `n ≥ 30` rule is not a substitute for that assessment. The runtime performs no automatic bootstrap in this increment.

**<strong class="defined-term">CI for the equally weighted mean of station means</strong>.** Let `m_i` be each qualifying station's mean paired ΔSNR in the selected scope, and let `M` count the stations contributing at least one eligible pair in that scope. For M ≥ 2, calculate:

$$\bar m=\frac{1}{M}\sum_{i=1}^{M}m_i,\qquad s_m^2=\frac{\sum_{i=1}^{M}(m_i-\bar m)^2}{M-1}$$

$$h=t_{1-\alpha/2,\,M-1}\frac{s_m}{\sqrt M},\qquad CI=[\bar m-h,\bar m+h]$$

Here `M` counts station means, not spot pairs. The confidence level is `1 − α`; at 95%, `α = 0.05`. The SD describes the observed spread across station means, and `s_m / √M` is the <strong class="defined-term">standard error</strong> under the stated model. With one contributing station, its mean remains defined but this aggregate CI is unavailable.

This is a model-based interval under station-independence and sampling assumptions. The Student-t calculation is exact when those station means are independent observations from the same normal distribution; otherwise it is an approximation. Equal weighting alone does not establish these assumptions, especially with few stations or unequal numbers of pairs per station. Distinct callsigns and locators do not establish independence, and two stations do not establish robustness.

The spread across station means reflects both path differences and uncertainty in each estimated station mean. The calculation does not separately propagate individual-station SEs or correlations, use precision weights, or average station CIs. Correlated paths, common propagation, unequal numbers or timing of observations within paths and selection of jointly decoded signals can limit interpretation. This equal-station interval uses the station means from the selected Inspector scope. The map has its own pooled-pair CI, using pair count N and the sample SD of paired differences; it does not use the station-mean CI.

The Stations scope result is recalculated directly from eligible station means. Map count and precision requirements control coloring and do not remove contributing stations in hatched segments from this estimate. Shared confidence changes this interval and the pooled map interval, but the map half-width threshold does not filter Stations or Spots summaries.

**<strong class="defined-term">Pooled-pair map mean and CI</strong>.** For example, **+3.20 ± 0.49 dB** represents bounds **[+2.71, +3.69] dB** at the stated confidence level. Its half-width meets a **0.5 dB** precision limit, but coloring still requires the station minimum and a non-degenerate available CI. Within one map segment, let `d_1,...,d_N` be the eligible <strong class="defined-term">paired ΔSNR values</strong> from stations meeting the ΔSNR requirements after the existing pairing, corrections and scientific filters. N counts each contributing pair once, not decoded reports or stations. For N ≥ 2, calculate:

$$\bar d=\frac{1}{N}\sum_{i=1}^{N}d_i,\qquad s_d^2=\frac{\sum_{i=1}^{N}(d_i-\bar d)^2}{N-1}$$

$$SE=\frac{s_d}{\sqrt N},\qquad h=t_{1-\alpha/2,N-1}SE,\qquad CI=[\bar d-h,\bar d+h]$$

The confidence level is `1 − α`; at the default 95%, `α = 0.05`. With no contributing pairs, the mean and CI are unavailable. With one pair, the mean is defined, but <strong class="defined-term">sample SD</strong>, SE and CI are unavailable. A station represented by one usable pair may contribute that pair to the pooled calculation even though its individual-station CI is unavailable.

The pooled sample SD includes variation within and between stations. It is not the SD of station means, an average of station SDs or an average of individual CIs. A segment receives a color only when all these conditions hold:

- The configured minimum number of qualifying stations is met. Count only stations that meet the ΔSNR requirements and contribute at least one usable pair to this segment.
- N is at least two, and the CI calculation is finite and available.
- The observed pair SD is positive.
- The **unrounded** CI half-width is positive and no greater than the configured maximum.

With N ≥ 2, a calculable degenerate zero-width interval is retained numerically and marked as degenerate in the export; the segment is hatched. Exactly zero pair variance differs from positive variance, including a positive interval width that merely rounds to zero.

The mean and CI must describe the same complete qualifying pair population. Missing required variance information makes the CI unavailable; silently omitting affected groups to calculate a partial-population CI is not valid.

This is a <strong class="defined-term">nominal IID Student-t baseline</strong>, exact under independent, identically distributed normal pair differences and otherwise approximate. Repeated observations on a path, adjacent WSPR cycles and shared propagation may be dependent. N is the observed pair count; the calculation makes no effective-sample-size adjustment for dependence. The interval does not incorporate systematic calibration error or remove paired-decode selection. A narrow interval does not establish independence, representative sampling or a physical cause. Coverage is nominal for each segment separately, not simultaneous over the map. The precision requirement is not a significance test: the interval may include zero and a mean of zero can qualify.

For identical qualifying pairs, adjustments and confidence, this calculation matches the existing pooled Spots mean/CI in the separate **Benchmark Statistics** section. Its Stations equal-weight aggregate and across-station CI remain unchanged.


<a id="sec-7-repeatability-control"></a>
##### 8.5.2 Repeatability and experimental control

Assess support at several levels:

| Check | What to examine |
|---|---|
| <strong class="defined-term">Evidence depth</strong> | Confirmed opportunities or spot pairs per contributing station. |
| **Breadth** | Number and geographic diversity of stations and paths. |
| **Internal consistency** | Whether different weightings, geographic selections and time views tell a compatible story. |
| **Repeatability** | Whether the pattern appears in a new run under comparable, documented conditions. |
| <strong class="defined-term">Experimental control</strong> | Calibration, crossover or reversed assignments, schedule reversal, and independent measurements that test alternative explanations. |

Agreement among views of the same observations establishes internal consistency, not replication. [Chapter 9](#sec-8) explains how to match the wording of a conclusion to this support.


<a id="sec-7-validation"></a>
##### 8.5.3 Validation scope

Software-validation statistics also need context. Identify the dataset, test date, WSPRadar version or source revision, and calculation method. A dated check establishes what was assessed for that test; it is not a general guarantee for every station, period or dataset.


<a id="sec-7-outliers"></a>
<a id="sec-7-11"></a>
#### 8.6 Experimental ΔSNR event analysis

**This experimental, optional detector finds temporary departures from the usual local ΔSNR for a remote station.** It is an expert diagnostic, not a required analysis step. [Section 2.5](#sec-outlier) explains its use and [Section 10.6](#sec-5-6) lists the controls. The sections below explain the scientific interpretation and main checks, rather than every algorithmic refinement.

<a id="sec-7-outlier-departure"></a>
##### 8.6.1 Departure from the local baseline

The detector examines each station separately, using its spot pairs at the original WSPR-cycle times. A station is identified by its exact callsign and full reported locator and must meet the requirements for paired ΔSNR summaries. These observations have already been matched, consolidated and scientifically filtered. Detection happens before display aggregation, so changing a plot’s time-bin width does not change the events. With reporting off, the detector does not run.

**Departure is ΔSNR minus its local baseline.** Against a **+8 dB** baseline, a **+1 dB** spot pair has departure **+1 − (+8) = −7 dB**. Target still has higher SNR, but its advantage is 7 dB below the local baseline. A change in Target, Reference or both can produce that departure.

Candidate grouping follows the departure's sign, not the sign of ΔSNR relative to zero.


<a id="sec-7-outlier-baseline"></a>
##### 8.6.2 Baseline and nearby variability

A <strong class="defined-term">baseline flank</strong> is the set of surrounding observations before or after a candidate. WSPRadar calculates median ΔSNR in **UTC-aligned 10-minute cells** that contain observations, using data up to **six hours before and after** the candidate. It excludes the candidate and a surrounding guard interval from the baseline.

Each flank needs **at least four populated cells**. Its baseline is the median of its cell medians. The expected local ΔSNR is the **average of the two flank baselines**, so the periods before and after the candidate count equally. Missing cells are not filled. If either flank lacks enough data, the candidate remains unclassified.

To measure nearby variation, subtract each flank's baseline from its cell medians and pool these <strong class="defined-term">residuals</strong> — the remaining deviations about the respective flank. Their <strong class="defined-term">median absolute deviation (MAD)</strong> is the median absolute distance from the pooled residuals' median.

The <strong class="defined-term">robust scale</strong> is selected as follows:

| Condition | Scale used |
|---|---|
| MAD is greater than zero | MAD |
| MAD is zero but IQR is greater than zero | Half the IQR |
| Both MAD and IQR are zero | **0.5 dB** |

The IQR here is also calculated from the pooled residuals. The 0.5 dB fallback is **not a universal minimum**.

The dimensionless robust z-score is **0.6745 × departure / robust scale**. A **−7 dB** departure with a **1 dB** scale scores about **−4.72**. It describes the departure relative to nearby variation; it is not a probability or statistical significance level.


<a id="sec-7-outlier-qualification"></a>
##### 8.6.3 Candidate qualification

Nearby departures with the same sign form provisional candidates. Their grouping uses the spacing of the station’s retained timestamps. Final qualification uses a local baseline fitted with the **complete candidate excluded**.

The event's **median departure** is the median of its spot-pair ΔSNR values after subtracting that local baseline. It is not the magnitude of the observed median ΔSNR. All four checks below must pass:

| Required check | Passing condition |
|---|---|
| <strong class="defined-term">Absolute departure</strong> | The magnitude of the event's median departure reaches **Minimum absolute ΔSNR departure (dB)**, allowing **0.01 dB** tolerance. |
| <strong class="defined-term">Relative departure</strong> | Its absolute robust z-score reaches **Minimum robust z-score**, without tolerance. |
| <strong class="defined-term">Baseline agreement</strong> | The before/after flank medians differ by no more than **Maximum pre/post baseline difference (dB)** plus **0.01 dB**. |
| <strong class="defined-term">Sign agreement</strong> | For at least **two thirds of the candidate’s retained native spot pairs with finite ΔSNR**, the departure from the local baseline has the same sign as the median departure. The denominator includes all such pairs retained within the candidate, including intervening pairs. |

Baseline agreement tests agreement of the two medians, not low background variability. The dB tolerance affects comparisons, not stored observations or statistics. Duration gives no weaker threshold, and a single large point cannot replace the event-median checks.

**One-sided timestamps have a limited role.** The cadence estimate uses all retained Paired and one-sided timestamps for a station eligible for paired summaries; it does not verify the physical operating schedule. A scientific change that retains additional one-sided observations can therefore change estimated cadence, permitted candidate gaps and baseline guard intervals. Grouping, baseline support and qualification can change even if every paired ΔSNR value is unchanged.

One-sided observations supply neither detector ΔSNR nor a vote in sign agreement. Display-only visibility changes do not alter the retained timestamps or rerun detection.


<a id="sec-7-outlier-boundaries"></a>
##### 8.6.4 Boundaries and event classes

The reported start and end must be spot-pair observations whose departures have the same sign and individually pass **both** departure thresholds. The interval is trimmed to these qualifying endpoints and tested again against the event-level requirements; weaker observations between them can remain. If only a smaller qualifying core remains, it keeps the complete candidate’s baseline, scale and support. A more favorable baseline is not fitted to that core. If no interval with qualifying endpoints passes, no event is reported.

| Event class | Retained spot pairs |
|---|---|
| <strong class="defined-term">Spot impulse</strong> | One spot pair. |
| <strong class="defined-term">Sustained excursion</strong> | At least three spot pairs spanning at least **30 minutes**. |
| <strong class="defined-term">Short burst</strong> | Every other event containing two or more spot pairs. |

All classes pass the same checks. The span from first to last observation describes retained evidence, not uninterrupted behavior between observations or the duration of an unseen physical event.


<a id="sec-7-outlier-context"></a>
##### 8.6.5 Context and limits

Each station’s event must pass the checks separately. Grouping nearby same-sign events across stations provides review context — path-specific, directionally coherent, scope-wide or multiple paths. **Scope-wide** means the group spans nonadjacent direction sectors. Grouping adds neither significance nor stronger qualification.

After a candidate passes the checks, separate Target and Reference SNR views and nearby one-sided counts help investigate it. These diagnostics are attached **after qualification**; they cannot make the candidate qualify, extend it or strengthen it. This differs from the earlier use of one-sided timestamps to estimate cadence, described in [Section 8.6.3](#sec-7-outlier-qualification).

The detector is deterministic and descriptive. It supplies no multiple-event significance correction, and event counts are not independent samples. Assigning a cause still requires the experimental controls discussed in [Chapter 2](#sec-3), [Chapter 3](#sec-4) and [Chapter 9](#sec-8).


<a id="sec-8"></a>
### 9. Evidence-Matched Claims and Reproducibility

A useful report states what was observed, how it was summarized, and what the comparison can establish. Name the included stations, band, UTC window, geographic scope, weighting and supporting counts. Then distinguish the observed result from any proposed explanation. This chapter provides wording examples and the records needed to preserve the result.


<a id="sec-8-1"></a>
#### 9.1 Claim classes and evidence-matched wording

Different statements require different evidence:

| Claim class | What the statement means | Evidence needed |
|---|---|---|
| **Descriptive** | What appeared in the retained observations. | Identify the population, scope, metric, weighting and supporting counts. |
| <strong class="defined-term">Comparative</strong> | How Target and Reference differed. | Describe the Reference and the observed paired and one-sided evidence. State whether common operation was independently established or the run was historical replay. |
| <strong class="defined-term">Component attribution</strong> | The difference follows a particular antenna, feedline, receiver or other tested component. | A controlled arrangement, appropriate calibration and preferably a crossover or reversal of assignments. |
| <strong class="defined-term">Causal</strong> | The tested change caused the effect. | A design that controls plausible alternative explanations; WSPRadar summaries alone are insufficient. |
| **Inferential** | The result generalizes beyond these observations, with a stated confidence or significance. | A justified sampling and dependence model and an analysis suited to that wider claim. WSPRadar’s supplied nominal CI calculation does not by itself provide that broader analysis. |

Match the statement to the quantity:

- **Performance** describes the Target's success within confirmed opportunities and its at-least-once reach during the selected window.
- **Benchmark ΔSNR** describes Target-minus-Reference SNR among retained spot pairs. Signals decoded on only one side have no paired SNR difference.
- **Decode Outcomes** describe paired and one-sided evidence. **Station Reach Advantage** compares distinct-station totals; **ΔDecode** compares pooled decode totals. Neither advantage is a Target win rate or an absolute decoding probability.
- **Direction and distance patterns** describe the observed radio paths, without directly measuring antenna radiation angle or gain pattern.

A controlled Benchmark relies on independently known common operation. **Historical replay** can describe the reported differences, but unverified schedules, uptime or uploads may explain one-sided counts. Do not present that replay as a controlled comparison of decoding success.

| Avoid | Evidence-matched wording |
|---|---|
| “Antenna A has 3 dB more gain than B.” | “For this band, UTC window and segment, the pooled mean paired ΔSNR was [mean] dB, with a [confidence]% CI of ±[half-width] dB for path A relative to B, supported by [n] stations meeting the ΔSNR requirements and [m] spot pairs.” |
| “My receiver sensitivity is 72%.” | “The Target's Station-averaged Decode Rate was 72% across [n] included stations during the stated window, with each station weighted equally and rates based on confirmed opportunities.” |
| “Performance should be close to 100%.” | “Decode Rate describes success within confirmed opportunities; 100% is not an expected baseline.” |
| “A is statistically significantly better.” | “The descriptive median ΔSNR favored A among the selected spot pairs; no significance test was performed.” |
| “The antenna has a lower take-off angle.” | “The observed advantage was concentrated in the specified longer-distance segments; radiation angle was not measured.” |
| “A is more efficient because it had more exclusive decodes.” | “A produced more one-sided decode evidence under the documented power, schedule and network conditions; efficiency was not isolated.” |

An SNR difference between complete setups does not identify its component or environmental cause. Keep within-run consistency separate from repeatability in a new, suitably controlled run. Include the applicable operating declaration or historical-replay limitation, applied Reference correction and evidence counts using the checklist in [Section 9.3](#sec-8-3).


<a id="sec-8-2"></a>
#### 9.2 Interpretation boundaries

The calculations describe the evidence selected by the run. Their limits arise from the reports, the selection rules and the physical comparison:

| Boundary | Consequence for interpretation |
|---|---|
| **Reported data** | Callsigns, locators and powers can be wrong. Databases contain successful decodes, not every attempted transmission or a complete failure log. Records and availability can change after the run. |
| **Selection of opportunities and SNR** | Performance is conditioned on observable Target activity and confirmed opportunities. Its successful SNR contains only decoded signals. Benchmark ΔSNR requires usable SNR on both sides; one-sided observations have no missing-side SNR to reconstruct. |
| **Operating conditions** | Controlled Benchmark requires independently known common operation and retains eligible one-sided evidence symmetrically. Historical replay leaves that operating premise unverified. Neither observed coverage nor a confirmation checkbox independently proves uptime or equal schedules. |
| **Physical causes** | Hardware, software, terrain, local noise, polarization and propagation remain combined unless the experiment separates them. Simultaneous TX can still include power, frequency-response, isolation and coupling differences. |
| **Dependence and generalization** | Reports share stations, time periods, geography and propagation. A row count alone does not establish the number of independent observations. Benchmark mean CIs use the named IID Student-t baseline and assume independence; their availability does not establish WSPR-wide coverage. WSPRadar does not supply automatic significance tests or a causal conclusion. |

WSPRadar does not directly measure antenna gain relative to isotropic (**dBi**), radiation efficiency, take-off angle, propagation mode, calibrated receiver sensitivity or absolute field strength. A gain *difference* is expressed in **dB**, but an observed ΔSNR is not automatically a measurement of that difference.

Broad evidence, consistent results and repetition under documented controls can support a practical station decision. Keep the claim within what the experiment measured; [Section 8.5](#sec-7-claims) explains dependence and experimental control.


<a id="sec-8-3"></a>
#### 9.3 Reporting and reproducibility checklist

Preserve three layers when comparing, publishing or acting on a result. The export supplies much of the analysis definition and evidence; keep physical setup measurements and operating records separately.

**1. Analysis definition**

- WSPRadar application version and, where available, source revision;
- database source and original export date;
- RX/TX direction, result type and Benchmark design;
- exact Target and Reference callsigns and locators;
- band and effective UTC boundaries;
- geographic scope, solar state, exclusions and evidence thresholds;
- Reference correction purpose, signed value and calibration basis;
- applicable common-operation declaration or historical-replay acknowledgement and limitations;
- primary scope chosen before inspecting the result, and any alternative settings or scopes checked; and
- whether the run was exploratory or confirmatory.

If an outlier candidate contributes to the conclusion, also record that reporting was enabled, the three detector thresholds, detector version, exact path, UTC interval, event class and whether the finding was exploratory or assessed under a previously fixed confirmatory setup.

**2. Evidence supporting the conclusion**

- Reported metric and its weighting;
- included stations and confirmed opportunities for Performance;
- stations with paired observations and spot-pair counts for Benchmark;
- station-level and observation-level summaries;

- for a reported mean CI: the mean and estimator, confidence level, method, contributing unit and count, half-width or full bounds, availability/status and independence assumption;
- for the Stations aggregate: also retain station count and across-station SD/SE;
- for a pooled map mean: also retain qualifying pair count N, paired-difference SD/SE, qualifying station count, the station-count requirement actually used, maximum half-width and qualification reason;
- Station Reach Advantage, pooled ΔDecode and relevant Paired, Target-only and Reference-only counts;
- geographic and temporal scope, including any station or short interval that strongly influences the result; and
- within-run consistency and any repetition in a separate run.

**3. External experiment record**

- Antennas, feedlines and RF-path arrangement;
- switch/splitter connections and the mapping of reporting identities to physical paths;
- transmitter, receiver, decoder and software versions;
- actual transmit power and its WSPR reporting basis;
- calibration measurements and reference plane;
- actual schedules, records supporting the Benchmark operating declaration, interruptions, crossovers and reversed assignments; and
- faults, interference, weather or deliberate changes relevant to interpretation.

Keep the original export package with these notes. A later retrieval can reflect database corrections or a newer WSPRadar version.


<a id="sec-8-4"></a>
#### 9.4 Analysis export package

Select the geographic scope, station evidence and any focus interval to preserve. **Prepare All Results for Download** builds the ZIP; **Download Prepared Results** saves it. Prepare again after changing those selections.

The ZIP contains `config/` and either `benchmark/` or `performance/`, according to the analysis. Available figures depend on the retained evidence and current selections. Each available figure is supplied as high-resolution light and dark PNGs showing the same evidence. The light file uses its `figure_*.png` filename; the dark file adds `_dark` before `.png` in the same folder.

| Artifact | Content, scope and availability |
|---|---|
| <strong class="defined-term">Disclaimer</strong> | `disclaimer.txt` contains the complete [Experimental Use & Disclaimer](#sec-disclaimer) in English. It accompanies every package. |
| **Configuration** | `wspradar_config.config` restores analysis settings and supported view choices for another run. It does not contain the original observations. |
| <strong class="defined-term">Run metadata</strong> | `run_metadata.json` records software version, database, actual data selection, analysis settings, corrections, inspection scope and enabled outlier settings. Benchmark also records its conditions acceptance, method version, selected segment and station temporal statistics, CI alpha and method, and the aggregation definitions used for the station and pooled-pair summaries. Acceptance does not identify whether common operation was confirmed or its limitations accepted, and is not independent proof of operation. TX Performance preserves the scientific `tx_snr_normalization_to_30dbm` choice and records its effective basis under `performance_snr`: `value_basis`, `normalization_to_30dbm`, the applied formula, and `decode_outcomes_changed: false`. The formula is `reported_snr` with normalization off or `reported_snr - reported_tx_power_dbm + 30` with it on. Each Performance result block also records `performance_corroboration`, including the enabled state, opportunity-count ceiling, fixed three-other-reporter requirement, exclusions, evidence-acquisition status and station-eligibility interpretation. |
| <strong class="defined-term">Processed evidence</strong> | `analysis_cache.parquet` contains retained evidence across the completed analysis's full geographic scope after scientific filtering. It is not restricted to the selected segment and is not an untouched database download. Performance `target_snr` is stored on the completed run's chosen basis; it is not simultaneously a raw and normalized column. The additional `corroborated_cycle` flag is 1 when at least one matching transmission in that identity-cycle meets the fixed three-other-reporter requirement, otherwise 0. Read it with the run metadata: `evidence_acquired: false` means corroboration was not collected because the filter was disabled or the selected opportunity minimum exceeded its ceiling; a zero value then is not a measured lack of corroboration. |
| <strong class="defined-term">Benchmark map-segment results</strong> | `benchmark/map_segments.parquet` records the map's pooled qualifying-pair mean, pair count N, paired-difference sample SD and SE, CI bounds and half-width, confidence/alpha and method, CI status, qualifying station count and station-count requirement, maximum CI half-width, and qualification reason. Existing segment fields and descriptive summaries retain their own estimator names. Hatched segments retain any calculable mean and numeric interval/status. |
| <strong class="defined-term">Station Insights CSV</strong> | `table_station_insights.csv` follows the full-analysis or optionally Inspector-filtered station list in both Performance and Benchmark. Both also follow the counter-only/one-sided visibility choice and Station Insights column filters, with scope and filters recorded in metadata. Station metrics retain their full-run values. Empty tables retain headers. The separate `table_drilldown_all_stations_current_segment.csv` still follows the active Inspector scope. |
| <strong class="defined-term">Drill-Down CSV files</strong> | Row-level evidence for selected stations or all stations in the active segment. The selected-station table can follow focus and table filters. Both files retain headers when empty. |
| <strong class="defined-term">Outlier CSV files</strong> | `table_delta_snr_outlier_event_paths.csv` summarizes qualifying path events; `table_delta_snr_outlier_paired_evidence.csv` contains their chronological spot pairs, including corrected Reference SNR. Both cover the active segment and join through IDs valid only within this package. Reporting off: files absent. Reporting on with no findings: headers only. Findings remain candidates, not confirmed physical events. |
| **Spots and Stations summary** | `figure_spots_stations.png` preserves the active Inspector scope's complete Spots and Stations summaries in one image in `benchmark/` or `performance/`; `figure_spots_stations_dark.png` provides the dark version. |
| <strong class="defined-term">Map, segment and temporal figures</strong> | The map covers the completed analysis. Segment and temporal figures follow the active segment, including applicable chronological and folded-hour views. |
| <strong class="defined-term">Selected-station figures</strong> | Benchmark and Performance use the selected station’s full-run evidence, independently of the station-list filter. With outlier reporting enabled, Benchmark can instead show pooled ΔSNR for multiple selected paths. Performance contains two selected-station temporal figures: absolute SNR and Decode Rate with temporal support; the redundant distance heatmap and segment-only deviation figure are omitted. Each subtitle gives the calculated distance from Target after the locator. |
| <strong class="defined-term">Drill-Down focus figures</strong> | Additional figures for exactly one selected station and its active focus interval. They preserve individual observations and chronological context alongside the ordinary selected-station figures. Candidate guides apply to the focused episode. |

| Temporal figure | Performance package file |
|---|---|
| Segment 1: absolute successful SNR | `performance/figure_segment_temporal_snr_absolute.png` |
| Segment 2: temporal support and pooled Decode Rate | `performance/figure_segment_temporal_evidence.png` |
| Segment 3: distance/time Decode Rate | `performance/figure_segment_temporal_decode_distance.png` |
| Segment 4: SNR deviations from each station’s run mean or median | `performance/figure_segment_temporal_snr_deviation.png` |
| Selected 1: absolute successful SNR | `performance/figure_selected_station_snr_evidence.png` |
| Selected 2: temporal support and pooled Decode Rate | `performance/figure_selected_station_temporal_evidence.png` |

The package's `config/run_metadata.json` preserves `performance_temporal_statistics`. `segment` retains the segment-deviation metadata role; `segment_absolute` describes the absolute view, `selected_station` remains absolute, and `segment_decode_distance` describes distance cells. These metadata distinguish individual-observation weights, folded pooling, density relative to each panel's maximum, actual pooled percentages, the shared displayed rate range and fallback status, interval availability and fixed-baseline treatment. Figure paths above are within the package root.

All four segment temporal figures are included in the results package even when the Expert Review panel is collapsed. The selected-station package contains two temporal figures; it includes neither the redundant distance heatmap nor a deviation figure.

The Performance SNR-band figure follows the active Inspector scope. The package includes `performance/figure_decodes_stations_by_snr.png` and `performance/figure_decodes_stations_by_snr_dark.png` when the figure is available. The `performance_snr_reach` entry in `config/run_metadata.json` records the scope, marker statistic, SNR basis, counting rules and fixed denominators.

Use the numeric `performance_corroboration.minimum_other_reporters` field to read the effective reporter threshold. The current export still writes `mode_specific_five_other_reporter_requirement_met` as its `evidence_definition` string, although the implemented threshold is three.

TX Performance exports preserve `tx_snr_normalization_to_30dbm` and the effective SNR basis. The retained `target_snr` values and all derived SNR tables, figures, baselines and intervals use that one completed-run basis. Raw and normalized results must not share a misleading 30 dBm label.

Benchmark numeric exports preserve the mean, sample SD, standard error, CI lower and upper bounds, symmetric half-width, alpha, method, contributing count and availability/status at full precision. The count denotes pairs for individual-station and pooled-pair CIs, but station means for aggregate station CIs. The displayed **±h** presents the bounds without replacing them. Missing and degenerate states remain distinguishable. Metadata identifies the temporal statistic and the summarized population.

**Mean of station means**, **median of station medians** and **mean of station medians** remain separately named. The first has its own CI calculated across the station means. These Stations definitions are unchanged. Map-segment exports describe the pooled qualifying-pair mean and its own CI, together with pair count N, paired-difference SD/SE, qualifying station count, station-count requirement, maximum CI half-width and qualification reason. Degenerate intervals retain numeric zero-width bounds and explicit status. Processed observations preserve dated UTC timestamps and full station identities even when a figure combines dates by hour, allowing later analyses that account for dependence.

The shared result fields are `n`, `mean`, `sample_sd`, `standard_error`, `lower`, `upper`, `half_width`, `alpha`, `method`, `available` and `status`. Temporal-bin exports retain bounds as `ci_lower` and `ci_upper` and the observed integer pair count as `ci_n`, including zero for empty bins. Top-level `statistics_availability` and `spots.distribution_status` distinguish unavailable raw spot distributions from valid cached summary statistics and CI values.

The selected-scope equal-station aggregate remains recorded in `benchmark_mean_statistics.stations.mean_ci`; the pooled Spots result remains separate. `benchmark_maps.delta_snr` identifies the pooled qualifying-pair map estimator, equal-pair weighting, CI method and contributing unit, count and precision qualification settings, and segment-result file. An Inspector scope can contain multiple segments and must not be confused with a single map segment. When the Inspector selects exactly that segment's qualifying pairs, adjustments and confidence level, the map and pooled Spots results agree.

Keep metadata with the evidence: configuration alone cannot reconstruct every selection. Missing data-selection metadata remains unknown; it does not establish that the standard filter was used. See [Section 11.4](#sec-6-4). Inspector scope, station-list scope and selected-station/focus scope are distinct; a Benchmark station figure must not be read as limited to the Inspector's direction and distance.

Benchmark figure filenames identify their quantities:

- `figure_map_delta_snr.png` and `figure_map_delta_decode.png`;
- `figure_decodes_over_snr.png` and `figure_segment_statistics.png`;
- `figure_segment_temporal_delta_snr.png` and `figure_segment_temporal_delta_decode.png`;
- `figure_selected_station_temporal_delta_snr.png` and `figure_selected_station_temporal_delta_decode.png`; and
- `figure_drilldown_zoom_delta_snr.png` and `figure_drilldown_zoom_delta_decode.png`.

These files are included when the necessary evidence and selections are available. The archive name remains `WSPRadar_export_YYYY_MM_DD__HH_MM.zip`. Retain the original package together with the external records in [Section 9.3](#sec-8-3); a later query or rerun may produce different records or results.


<div style="page-break-before: always;"></div>

<a id="part-ii"></a>

## Part IV: Controls and Troubleshooting

Use this part to look up a setting or resolve a problem. [Part I](#part-i) explains how to use WSPRadar; **How to read this** beside each result explains its charts; [Part III](#part-iii) defines the calculations and their limits.

<a id="sec-5"></a>

### 10. Controls and Configuration

Changing the analysis type, station callsigns or locators, band, UTC window, Reference correction, filters or evidence requirements clears the completed result and requires a new **Run**. Changing an Inspector selection, station-list filter, time aggregation, time basis or Drill-Down view does not rerun the analysis. In Performance, changing **Shared confidence level** updates the temporal mean intervals in the completed result. In Benchmark, that setting requires a new run.

<a id="sec-5-1"></a>

#### 10.1 Workflow controls

| Control | What you need to know |
|---|---|
| **Input view** | Guided and Compact use the same analysis settings. The chosen input view is not saved. |
| **Load Demo** | Loads settings without running. In either input view, **Load and walk through setup** opens the Guided steps; **Load and review to run** opens Guided Review directly. The collapsed **Guided demo** panel retains the experiment notes and the **Walk me through the setup** / **Skip to review** navigation actions. Only **Run RX Analysis** or **Run TX Analysis** starts the analysis. |
| **Start Fresh** | Clears settings and results and restores defaults, including the UTC window. Language and input view stay unchanged. |
| **Load Config / Save Config** | Load or save applicable analysis settings and supported view choices. Saved dates are fixed UTC boundaries, not a rolling period. A configuration contains no result data or station notes. |
| **Run RX Analysis / Run TX Analysis** | Starts the chosen analysis after validation. Resolve highlighted fields and any Reference location choice first. A map can appear before the remaining views are ready; wait for **Complete**. |
| **Prepare All Results for Download** | Builds the export for the current selections. Then choose **Download Prepared Results**. Prepare again after changing the selections. See [export contents](#sec-8-4). |

After a run, an edit that clears the completed result reopens a collapsed **Review** panel in Guided or Compact once the settings are valid. Under **RUN ANALYSIS**, the panel shows **Save Config** and the Run button for the selected direction. For Benchmark, the operating-conditions explanation and checkbox appear directly above these buttons. You can reach Review and save otherwise valid settings while the box is unchecked. Starting a Benchmark requires checking the box.

**Keyboard:** use `Tab` and `Shift+Tab` to move between controls. In Guided, forward `Tab` beyond a setup panel validates it and opens the next step, like **Continue**; errors return focus to the first invalid field. Reaching Review does not start the analysis. The separate `?` help icons require a pointer.

Loading or saving a configuration does not run it. Unsupported old formats are rejected. One compatibility exception accepts a complete valid pair of former ΔDecode count thresholds and replaces them with the **1% event-share default**, with a notice; it does not convert counts into percentages. Review loaded settings before running.

<a id="sec-5-2"></a>

#### 10.2 Question, Target and measurement-window controls

| Control | Default and essential rules |
|---|---|
| **Question** | Required: choose RX Performance, TX Performance, RX Benchmark or TX Benchmark. Only Benchmark needs a Reference. |
| **Target callsign** | Required. In RX, use **Target callsign (receiver under test)**. In TX, use **Target callsign (transmitter under test)**. Enter the callsign exactly as reported, including any prefix or suffix. `CALL`, `CALL/P` and `CALL-1` are distinct reported callsigns. |
| **Target QTH (4 or 6 characters)** | Required: the first four locator characters select Target reports; the full entered locator anchors map, distance, direction and solar calculations. |
| **Operating Band** | Default **20m**. Select one band. |
| **SNR TX Normalization to 30 dBm** | TX Performance only, to the right of Operating Band. Off for a new analysis: received SNR as reported. On: normalize using reported transmit power to 30 dBm (1 W). This is a scientific setting requiring an analysis rerun. Older settings without the field retain On. RX Performance and Benchmark remain normalized. |
| **Start / End Date/Time (UTC)** | Default: 24 hours ending at the current UTC minute. Dates start in 2008; a run may span at most **31 elapsed days**. Times retain minute precision. |

New TX Performance analyses default to the raw reported-SNR basis. Saved TX Performance configurations and links explicitly preserve the on/off boolean `tx_snr_normalization_to_30dbm`: in configurations it is `core_parameters.tx_snr_normalization_to_30dbm`, and the URL parameter has the same field name. An older configuration, link or completed-run record that lacks the field retains normalization on, preserving its former interpretation. Explicit true/false choices survive save, link, load and completed-run restoration. The setting is active only for TX Performance; it does not change RX Performance or Benchmark. Changing the scientific basis requires an analysis rerun; the observations and cached results for the two settings are kept separate. A loaded old run is not silently reinterpreted as raw SNR.

A four-character <strong class="defined-term">Maidenhead locator</strong> (grid-4) identifies a grid square; six characters identify a smaller subsquare.

<a id="sec-5-3"></a>

#### 10.3 Benchmark-design controls

| Control | What to enter |
|---|---|
| **Reference callsign** | Enter the Reference callsign exactly as reported. It must differ from Target. Reference Neighborhood is no longer supported. |
| **Known Reference QTH (4 characters, optional)** | Leave blank to discover the location from reports, or enter an independently known grid-4. One discovered grid resolves automatically; several require your choice. A known location does not establish operation. |
| **Reference SNR correction** | Default **No correction** applies **0.0 dB**. Choose **Use a documented correction** only for an established offset valid for this setup. The signed field accepts **−99.9 to +99.9 dB**; blank means **0.0**. Use a decimal point. A documented zero remains distinct from no established correction. |

**Benchmark acceptance:** every Benchmark run requires **I have confirmed common operation, or accept the limitations when it is unverified.** Check common operation as described in [Section 1.2](#sec-2-2); when it is unverified, interpret the observations within the stated limitations. Changing station identities, direction or band clears acceptance. Changing the period also clears it, except when you select an eligible cycle-aligned subwindow of the completed acquisition with unchanged acquisition settings. In that case the chosen Reference site and existing acceptance carry over, and a new **Run** is still required. Loading a personal configuration or ordinary analysis link requires fresh acceptance; a saved acceptance does not verify operation.

The same acceptance applies to **historical observations**, including Milazzo; there is no separate historical mode. Ordinary analysis links require fresh acceptance, including links with the inert `run=1` parameter. Opening a link never starts an analysis. Built-in demos preselect this acceptance; their experiment notes explain known operating conditions and uncertainties. A link selecting an installed demo opens Guided Review directly with that demo selected; its experiment notes remain available in the collapsed **00 Guided demo** panel. This shortcut does not apply to ordinary shared-settings URLs, which still require fresh Benchmark acceptance. Loading a demo alone still does not run it.

##### Reference-side SNR correction sign

A **positive correction raises Reference SNR and reduces ΔSNR**. If a common-input calibration measured Target minus Reference as **+1.6 dB**, enter **+1.6 dB**. Correction does not change decode counts or raw cumulative-SNR curves. To collect a baseline, use **No correction**; WSPRadar does not determine an offset automatically. See [Chapter 6](#sec-reference-snr-calibration) for calibration and its limits.

<a id="sec-5-4"></a>

#### 10.4 Filters and evidence thresholds

The values shown in **Optional Filters, scope and evidence** apply even when you leave that panel untouched. The table gives fresh-setup defaults; demos and loaded configurations use their stored values. Choose the intended population and evidence requirements before a confirmatory run.

For ΔDecode, an <strong class="defined-term">observed event</strong> is one remote identity and WSPR cycle with at least one retained report for Target or Reference. A paired event counts **once** toward its evidence requirement.

| Control | Default / range | Effect |
|---|---|---|
| **Exclude Special Callsigns Q, 0, 1** | Performance **on**; Benchmark **off** | Excludes remote callsigns beginning with `Q`, `0` or `1`: transmitters in RX, receivers in TX. Target and Reference are exempt. A prefix alone does not identify telemetry. |
| **Exclude Moving Stations** | Performance **on**; Benchmark **off** | Excludes peer callsigns reported in more than one grid-4 in the otherwise eligible global reports, **before distance filtering**. This may reflect movement or incorrect metadata. |
| **Solar state at Target QTH** | **All 24h** | Keeps all cycles, daylight above **+6°**, nighttime below **−6°**, or greyline between those elevations at the Target. |
| **Maximum peer distance from Target (km)** | **Worldwide (≈20 015 km)**; choices 2 500 / 5 000 / 10 000 / 15 000 km / Worldwide | Numeric limits remove peers **at or beyond** the limit from the analyzed population and exports; Worldwide retains all geographic locations. This changes the analysis, not just the map view. A loaded 20 000 km limit remains available while selected and keeps its original meaning. |
| **Minimum confirmed opportunities per station** | **1**; 1–50 | Performance: each station needs at least this many successes plus confirmed misses. Lower values produce coarser rates based on fewer observations. The server-configured corroboration filter also applies to stations with few opportunities; see [Section 8.3.1](#sec-7-performance-opportunities). |
| **Minimum qualifying stations per map segment** | **5**; 1–25 | Performance: A segment at or above this minimum shows its Decode Rate color, including 0%. A segment with at least one qualifying station but below the minimum is gray hatched. A segment with no qualifying stations is unfilled. |
| **Minimum qualifying stations per segment for ΔSNR** | **3**; 1–50 | The minimum number of stations contributing at least one usable spot pair to the segment after the applicable requirements. A segment also needs an available, non-degenerate pooled-pair CI within the maximum half-width. |
| **Shared confidence level** | **95%**; 70%, 80%, 90%, 95%, 99% | In Benchmark, one shared setting governs map and Inspector mean CIs: pooled map pairs, individual stations, pooled Spots, temporal/folded bins and the existing equal-station aggregate. Higher confidence widens an interval with nonzero width for the same data and can change map qualification; it does not change contributing observations or means. In Performance it governs chronological and folded SNR mean CIs at segment and selected-station level, without changing map qualification, counts, means, or the Median/IQR view. Valid custom imported levels are retained. |
| **Maximum ΔSNR map CI (± dB)** | **0.5**; finite positive value | Editable numeric map setting: 0.5 means a CI no wider than **mean ±0.5 dB**. Coloring requires the unrounded pooled-pair CI half-width to be no greater than this value. The station-count requirement remains in force. |
| **Minimum observed stations per segment for ΔDecode** | **3**; 1–50 | Count distinct callsign/full-reported-locator identities with at least one retained event in the segment, including one-sided identities. The observed-event share requirement must also be met. |
| **Minimum observed-event share per segment for ΔDecode (%)** | **1%**; 0–5%, steps of 0.5% | Benchmark: requires this share of the full filtered run's observed events, rounded up to a whole event. At **0%**, every nonempty segment meets this requirement; the observed-station minimum still applies. |

**For the Benchmark ΔSNR map**, the station minimum is **three** by default, with range **1–50**. Coloring additionally requires an available, non-degenerate pooled-pair CI at the shared level, **95%** by default, with unrounded half-width no greater than **0.5 dB** by default. A half-width of **0.5004 dB fails a 0.5 dB limit**, even if a display rounds it to 0.50. The half-width setting changes map qualification and shading only; the confidence setting governs existing mean CIs as well. Neither setting deletes eligible evidence from the Inspector. The compact summary reads **CI ± 0.5 dB** and **Shared confidence level: 95%** at the defaults; both values follow the current settings.

The ΔDecode requirement's full-run denominator stays fixed when you crop or select a segment. ΔDecode has no separate per-station event minimum and does not reuse ΔSNR station qualification. Its observed-station minimum and event-share requirement both apply. These requirements describe station breadth and evidence volume, not confidence.

The **ΔSNR evidence requirements** and **ΔDecode evidence requirements** appear side by side where screen width permits, with the relevant station minimum first in each section. On narrow screens they stack. **Expert Settings** follows these requirements and contains **Identify ΔSNR outlier candidates** and its optional controls.

Benchmark segments with observed evidence but below the relevant threshold are gray hatched; retained station observations remain available. The paired-evidence requirement for ΔSNR does not remove decodes from ΔDecode. In Performance, evidence outside the distance limit may still establish Target activity, without adding those peers to the analyzed population.

Once you manually change either exclusion, that choice persists across Question changes. Stored configurations, demos and analysis links also preserve their explicit exclusions.

<a id="sec-5-5"></a>

#### 10.5 Map, inspector and export controls

These controls let you explore the completed analysis without changing which observations count:

| Control | Scope and persistence |
|---|---|
| **Segment distance and direction** | Changes Inspector statistics and time views. Station Insights follows this scope only when its optional segment-and-distance filter is enabled; station metrics and selected evidence retain the full run. Saved separately for Performance and Benchmark. |
| **Filter by selected segment and distance** | Optionally restricts the Performance or Benchmark station list; otherwise it is global. Selected-station evidence still covers the full run. It sits to the left of the counter-only/one-sided visibility control. This toggle is session-only and is not saved in configurations or shared links. |
| **Station Insights → Filter** | Restricts the station list and its exported table, not maps or Inspector statistics. Column filters are saved; a station must meet every active condition, while any selected value within one callsign/locator filter can match. |
| **Heard only by other stations. / Only other signals heard.** | Shows Performance stations with confirmed opportunities but no successful decode. This visibility choice is saved. |
| **Include one-sided evidence** | Shows Benchmark stations without spot pairs and one-sided Drill-Down observations. This saved visibility choice changes neither coverage totals nor qualification. |
| **Selected station row** | Saves the exact callsign-plus-locator selection: normally one per result type; multiple Benchmark identities are supported when outlier reporting is enabled. |
| **Time aggregation** | Changes chronological display bins; Inspector and selected-station choices are saved separately. Pairing, opportunities and fixed one-hour folded bins remain unchanged. |
| **Time basis** | Selects UTC or Local Solar independently for segment and selected-station plots, with UTC as the new-analysis default at both levels. Each choice applies to that level’s chronological and folded SNR, decode and coverage panels; focused plots follow the selected-station choice. Both choices are saved in configurations, shared analysis links and export metadata. Switching changes the displayed chronological clock while preserving UTC bins and their statistics; folded observations are regrouped before their hourly summaries. Whole-run statistics remain unchanged. |
| **ΔSNR statistic: Median / Mean** | Benchmark temporal ΔSNR only. Mean is the default for new analyses. Segment and selected-station plots keep independent choices. If a current configuration omits a statistic, that level defaults to Mean; explicit saved choices are honored. The Milazzo demo opens both levels with Median. Median shows the existing median and Bin IQR; Mean shows the arithmetic mean and its available configured pointwise CI. Both preserve eligible observations, bins and pair weighting. Both choices are saved in configurations, shared analysis links and export metadata. Benchmark Statistics, maps, ΔDecode and evidence counts remain unchanged. |
| **Retained Performance SNR-marker setting** | The optional Performance-only `results_view.performance_snr_statistic` still accepts `mean` or `median` and defaults to `mean` when omitted. Configurations and shared links retain this compatibility setting. This setting was used by the former successful-SNR histogram. The current **Spot & Station Decodes** selector uses the independent setting below. |
| **Spot & Station Decodes → Summary statistic (Performance)** | Selects **Mean** or **Median** for the five SNR markers and the bottom-right mean/median station rates by band and over All SNR, and the mean/median station rates in the Stations card. The frequency categories, counts, Spot Decode Rate and Station Reach stay fixed. The optional Performance-only `results_view.performance_snr_reach_statistic` accepts `mean` or `median`, independently of temporal controls. Omission uses `mean`. Configurations, shared links, restored completed runs and exports retain the selection. |
| **SNR statistic: Median / Mean** | Performance temporal SNR at both independent levels, default Mean. Both chronological and folded views pool individual successful observations directly. Absolute SNR keeps those values; segment deviations subtract each station's selected run mean or median before pooling individual residuals. Mean shows its configured pointwise CI; Median shows IQR. Absolute density stays unchanged by the toggle; residual density can change with its baseline. Saved configurations, shared links, resumed completed runs and exports retain the selections. Decode Rates, counts, map qualification, the SNR-band summary and fixed station-table medians are unchanged. |
| **Zoom window / <strong class="defined-term">Outlier Focus</strong>** | Focuses Drill-Down on an interval for exactly one selected station. **Filter table** then narrows the displayed rows and the selected Drill-Down table in the download. The focused plots use the full zoom window. Focus and Drill-Down table filters are not saved in configurations or analysis links. |

**Saved confidence settings.** The following fields are useful when inspecting configurations, shared links or exports.

These settings are stored under `advanced_parameters` and preserved in shared analysis links and export metadata. The independent `segment_temporal_statistic` and `station_temporal_statistic` remain under `results_view`. `evidence_confidence_level_percent` defaults to `95` and must be strictly between 0 and 100. The corresponding internal `ci_alpha = 1 − evidence_confidence_level_percent / 100` specifies the total two-sided tail probability and must be strictly between 0 and 1; the confidence level is `100 × (1 − ci_alpha)%`. `evidence_confidence_interval_method` defaults to `iid_student_t`. In Benchmark, the same confidence configuration governs individual station means, pooled qualifying-pair means, temporal/folded-bin means, pooled map-pair means and the existing equal-station aggregate for the selected Inspector scope. Each interval uses its own contributing unit and sample SD: pairs for the map and pooled Spots, station means for the Stations aggregate. Benchmark Statistics estimators and populations remain unchanged. The map additionally has its own maximum CI half-width requirement; that threshold does not filter Inspector scope statistics. See [Section 8.5.1](#sec-7-dependence-bias) for the calculation and assumptions.

In Performance, the same saved confidence fields govern absolute and segment-deviation temporal means described above; each uses individual contributing successful observations or residuals. An omitted temporal statistic defaults to Mean independently at each level, and omitted confidence fields use 95% and `iid_student_t`. Explicit valid values are honored. These settings change the summaries and their presentation without changing the source-data query or which observations are included. Performance does not gain the Benchmark map CI-half-width threshold.

Saved configurations express the shared confidence setting as `advanced_parameters.evidence_confidence_level_percent` and `advanced_parameters.evidence_confidence_interval_method`; the internal `ci_alpha` remains the corresponding two-sided tail probability. The map limit is stored as `advanced_parameters.evidence_max_segment_ci_half_width_db`. Saved configurations preserve the effective station-count requirements, shared confidence and map CI limit. An absent half-width uses the default **0.5 dB**; an explicitly supplied value must be finite and strictly positive. Invalid values require correction rather than silent replacement.

**ΔDecode configuration:** Benchmark configuration documents explicitly require `settings.advanced_parameters.evidence_min_decode_stations_per_segment`, alongside `settings.advanced_parameters.evidence_min_decode_event_share_percent`. The station minimum is an integer from **1 to 50**; new analyses default to **3**. Existing installed Benchmark demos explicitly use **1** to preserve their reviewed coloring. Older Benchmark configuration documents missing the required field are rejected rather than silently assigned a new map requirement. Shared links use `min_decode_stations_per_segment` for this separate ΔDecode setting.

Shared links record the effective Benchmark station minimum explicitly. A link with unresolved, retired or invalid optional parameters restores its recognized valid settings and lists the parameter names that need manual selection before running. Retired names are not aliases and are not silently migrated. Invalid or ambiguous required identity, comparison design or time settings prevent loading. Links load settings only; they do not authorize a new analysis.

Chronological bin choices depend on the **complete run duration**. A valid saved choice takes precedence over the default and remains available even outside the usual choices below:

| Run duration | Usual bins | Default |
|---|---|---|
| Up to 6 hours | 2m, 10m, 30m, 1h, 2h, 3h, 6h | **10m** |
| More than 6 through 24 hours | 2m, 10m, 30m, 1h, 2h, 3h, 6h | **30m** |
| More than 24 hours through 7 days | 30m, 1h, 2h, 3h, 6h, 12h, 24h | **12h** |
| More than 7 days | 1h, 2h, 3h, 6h, 12h, 24h | **12h** |

Manual zoom offers **Off** and the **1h**, **3h**, **6h**, **12h** or **24h** windows that fit within the completed run. Choose a UTC center or move with **Earlier / Later**. Outlier Focus includes the event and its surrounding baseline evidence and may exceed 24 hours. The export can include separate focused figures; [Section 9.4](#sec-8-4) defines their scope.

<a id="sec-5-6"></a>

#### 10.6 Benchmark outlier-detection controls

Under **Expert Settings**, **Identify ΔSNR outlier candidates** is off by default. Enable it only when investigating temporary departures in paired evidence; see [Section 2.5](#sec-outlier).

| Control | Default / range | Effect |
|---|---|---|
| **Minimum absolute ΔSNR departure (dB)** | **6.0**; 0.1–100.0 dB | Requires a sufficiently large change from the path's local baseline. |
| **Minimum robust z-score** | **3.0**; 0.1–100.0 | Also requires the change to be large relative to nearby variation, using the absolute robust score. This score is not a probability. |
| **Maximum pre/post baseline difference (dB)** | **3.0**; 0.1–100.0 dB | Requires the baseline medians before and after the candidate to agree within this amount. It does not require low background scatter. |

All three requirements, plus the detector's support checks, apply to every event duration. Lowering either minimum or raising the allowed baseline difference makes reporting more permissive. Changing detector settings requires another **Run**; detections are independent of display-bin width and do not change the ordinary Benchmark maps. [Section 8.6](#sec-7-outliers) gives the exact method and limits.

<a id="sec-6"></a>
<a id="sec-5-7"></a>

### 11. Troubleshooting and Data Quality

Start with the analysis settings. Lower thresholds cannot repair a wrong callsign or locator, band, time window or transmission schedule.

<a id="sec-6-1"></a>

#### 11.1 Confirm the run definition first

Check the exact **Target callsign and QTH**, **band** and **UTC window**, then actual operation and uploads. For Benchmark, also check Reference identity, common operating times, synchronized clocks and, for TX, [schedules and frequency separation](#sec-simultaneous-tx-setup-2). Verify signal routing and actual versus reported power before interpreting an unexpected difference.

<a id="sec-6-2"></a>

#### 11.2 Diagnose by symptom

Read notices against the settings of the **completed run**. An observed count and a required minimum are different: three observed opportunities do not meet a five-opportunity requirement.

| Symptom | What to check or do |
|---|---|
| **No Target/source evidence returned** | Check identity, locator, band, UTC window and uploads in the selected database. Review [historical mode filtering](#sec-6-4). Lowering evidence thresholds cannot create source reports. |
| **Reports returned, but none remain** | Review station exclusions, solar state and maximum peer distance. These may remove the retrieved population. |
| **No stations meet the Performance requirements** | Compare each station’s confirmed opportunities with the required minimum. Check the filters and the reports used to establish transmitter and receiver activity; unknown activity is not a confirmed miss. |
| **Performance stations are available, but no segment is colored** | Compare the number of included stations in each segment with its required minimum. Gray hatching (**Not qualifying**) means at least one station meets the station requirements, but too few remain to color the segment. An unfilled segment (**No observations**) has no station left for this map after those requirements. A valid 0% Decode Rate is colored; hatching or an unfilled segment does not establish that no reception occurred. |
| **Benchmark ΔSNR is missing or hatched** | Check for the same remote identities in the same cycles, common operation and synchronized schedules. Then check station pair eligibility and the segment's contributing station count. Select the exact segment in **Segment Inspector** and compare the pooled **Spots** mean and ± half-width in the separate **Benchmark Statistics** section with the selected CI ± limit. The full-precision interval status and qualification reason are in `benchmark/map_segments.parquet`. A CI may be unavailable, degenerate or wider than the selected limit. With at least two contributing pairs, exactly zero variance across their differences gives a degenerate interval and the segment remains hatched; equal station means alone do not imply zero pair variance. Check paths and dated evidence before changing the requirements. One-sided evidence can still support ΔDecode, and eligible observations in hatched segments remain in Inspector scope statistics. |
| **ΔDecode is hatched despite observed reports** | Check the segment’s minimum observed-station count and compare its event count with the full-run event-share requirement. Both must be met. Selecting a smaller area does not lower the event-share requirement. |
| **Station list is unexpectedly empty** | Clear Station Insights column filters and review visibility toggles. In Performance and Benchmark, also check **Filter by selected segment and distance**. |
| **Unexpected ΔSNR sign** | Check Target/Reference and physical path assignments, correction sign and power reports. Reconcile an individual pair in Drill-Down. |
| **One-sided reports dominate, or no outlier is found** | Check operating logs and paired support before, during and after the interval. One-sided reports alone provide no ΔSNR; see [activity evidence](#sec-6-5). |
| **Large table has no search or direct CSV download** | Above **150 000 displayed rows**, read-only tables load while scrolling. Narrow Drill-Down with **Filter table**, or use the prepared results ZIP. |
| **Run exceeds the source row limit, recent reports are missing, or a source fails** | Follow [upstream-data checks](#sec-6-6). A smaller map distance does not reduce retrieved rows. |

<a id="sec-6-3"></a>

#### 11.3 Callsign and locator checks

Check identities in the **database used by the run**, not only in another website's map. Target and Reference selection uses exact callsign plus grid-4; a Target reported at `JN37` does not match configured `JN38`. The Target map origin is never changed automatically to fit reports.

Reporting tokens must be 3–15 characters; locators must be valid four- or six-character Maidenhead locators. Reference QTH input uses four characters. Valid syntax does not verify location or operation. Remote identities use the **full reported locator**, so locator variants can split one physical station into several identities.

WSPRadar neither reconstructs compound callsigns from separate messages nor supplies missing locators. See [Section 5.1](#sec-simultaneous-tx-setup-1) when a TX identity is missing or incomplete.

<a id="sec-6-4"></a>

#### 11.4 Historical decode-code fallback

WSPRadar normally requests <strong class="defined-term">WSPR-2</strong>, the two-minute mode, using the database condition `code = 1`. For a window **entirely before 1 January 2022, 00:00 UTC**, it retries without that condition if the strict query finds no Target source evidence for Performance, or no source evidence from either setup for Benchmark. A window ending exactly at that boundary or later keeps the strict filter.

This historical <strong class="defined-term">fallback</strong> broadens selection because older mode records may be incomplete or ambiguous <a href="#ref-10">[Ref-10]</a>. Run status and exported `decode_filter_mode` identify the selection used; they do not establish the physical mode of every historical report. The cutoff is a compatibility rule, not a guarantee of data quality.

<a id="sec-6-5"></a>

#### 11.5 Operating conditions and activity evidence

**Benchmark** retains eligible paired and one-sided reports without requiring a separate Target-activity witness in each cycle. Even an entire period observed on only one side remains usable as descriptive decode evidence, but provides no ΔSNR. A one-sided interval may reflect reception, schedules, outages or missing uploads; WSPRadar does not identify its cause or remove it automatically. Check logs and use a documented common operating period.

**Performance** counts each success as its own confirmed opportunity. A miss requires reports establishing activity at both the transmitter and receiver on the same band in the same cycle; otherwise the outcome remains unknown. The direction-specific rules are in [Section 8.3.1](#sec-7-performance-opportunities).

<a id="sec-6-6"></a>

#### 11.6 Working with upstream data

<strong class="defined-term">System Audit Status</strong> identifies the database and any historical fallback used. Each run uses one source; reports from different databases are not combined. WSPRadar can switch sources for a new attempt, but Reference location discovery ties the ensuing analysis to that source. If it fails, restart and review the newly resolved Reference location. When WSPRadar resolves the Reference location for the run, **Complete** lists the lookup database and filter, the Reference location used, and the locators reported for that location.

For recent reports, allow about **five minutes** after the final cycle, then check uploads and availability in the selected database. This is a practical waiting estimate, not a completeness guarantee <a href="#ref-10">[Ref-10]</a>. Databases may contain incorrect identities, locators or power values, delayed reports and later corrections. Demo reruns may reuse previously retrieved data, so rerunning need not pick up later corrections.

A request exceeding **1 000 000 complete rows** is rejected, not silently truncated. Shorten the UTC window; **Exclude Special Callsigns Q, 0, 1** can reduce source queries when appropriate to your question. The distance limit is applied **after retrieval**, so reducing it does not avoid this limit.

<a id="sec-ref"></a>
<a id="part-v"></a>

## Part V: References

* <a id="ref-1"></a><a href="https://arxiv.org/abs/2209.08989">[Ref-1]</a> **Preprint.** Zander, J. (2022). *Simple HF antenna efficiency comparisons using the WSPR system*. arXiv:2209.08989v1. doi:10.48550/arXiv.2209.08989. Particularly §IV for the paired-comparison measurement model.

* <a id="ref-2"></a><a href="https://doi.org/10.1155/2022/4809313">[Ref-2]</a> **Peer-reviewed article.** Vanhamel, J.; Machiels, W.; Lamy, H. (2022). *Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*. International Journal of Antennas and Propagation, 2022, 4809313. doi:10.1155/2022/4809313.

* <a id="ref-3"></a><a href="https://sivantoledotech.wordpress.com/2010/09/24/failure-to-use-wspr-to-compare-antennas/">[Ref-3]</a> **Operator technical account.** Toledo, S. / 4X6IZ (2010). *Failure to Use WSPR to Compare Antennas*.

* <a id="ref-4"></a><a href="https://www.qsl.net/kp4md/wspr.htm">[Ref-4]</a> **Amateur-radio technical article and club presentation.** Milazzo, C. F. / KP4MD (2011). *Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*. Posted 13 January 2011; measurements from December 2010; presented 1 March 2011.

* <a id="ref-5"></a><a href="https://www.researchgate.net/publication/319903566_Improving_HF_Band_SNR_from_analysis_of_WSPR_spots">[Ref-5]</a> **Amateur-radio magazine article.** Griffiths, G.; Squibb, N. J. (2017). *Improving HF Band SNR*. Practical Wireless, October 2017, 23-26. <a href="https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf">Author-hosted copy</a>.

* <a id="ref-6"></a><a href="https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf">[Ref-6]</a> Taylor, J. H.; Walker, B. (2010). *WSPRing Around the World*. QST, 94(11), 30-32.

* <a id="ref-7"></a><a href="https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2023.1184171/full">[Ref-7]</a> **Peer-reviewed review article.** Frissell, N. A. et al. (2023). *Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations*. Frontiers in Astronomy and Space Sciences, 10, 1184171. doi:10.3389/fspas.2023.1184171.

* <a id="ref-8"></a><a href="https://www.arrl.org/wspr">[Ref-8]</a> **Official technical overview.** ARRL, *WSPR*: message format, coding, duration, timing, occupied bandwidth and SNR reference. Accessed 2026-07-12.

* <a id="ref-9"></a><a href="https://www.mdpi.com/2073-4433/13/8/1340">[Ref-9]</a> **Peer-reviewed article.** Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). *A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals*. Atmosphere, 13(8), 1340. doi:10.3390/atmos13081340.

* <a id="ref-10"></a><a href="https://wspr.live/">[Ref-10]</a> **Official data-service documentation.** WSPR.live, *Welcome to WSPR Live*: database access, schema, mode-code mapping, raw-data and availability disclaimer, and data-update behavior. Accessed 2026-08-06. Public ClickHouse SQL access, dashboards, exports and computing-resource credit to HB9VQQ. Accessed 2026-10-06.

* <a id="ref-11"></a><a href="https://www.wsprdaemon.org/">[Ref-11]</a> **Official project website.** WSPRDaemon, *WSPR Daemon*: multi-channel spot acquisition, WSPR/FST4W decoding and reporting, noise estimation, database/Grafana output, and services for third-party applications. Accessed 2026-08-06. **Official operating documentation.** WsprDaemon, <a href="https://wsprdaemon.readthedocs.io/en/master/FAQ.html#how-does-spot-merging-work-with-multiple-receivers">*FAQ: How does spot merging work with multiple receivers?*</a>: best-SNR reporting to WSPRnet when merging receiver reports. Accessed 2026-09-24. Additional project documentation: <a href="https://wsprdaemon.readthedocs.io/en/master/results/wspr.html">*WSPR*</a>, <a href="https://www.wsprdaemon.org/grafana">*Grafana*</a> and <a href="https://wsprdaemon.readthedocs.io/en/master/description/how_it_works.html">*How it works*</a>: database access, ClickHouse development and hosting credits, acquisition, reporting, noise and Doppler measurements. Accessed 2026-10-06.

* <a id="ref-12"></a><a href="https://wsjt.sourceforge.io/wsjtx-main_en.html">[Ref-12]</a> **Official operating documentation.** WSJT-X 3.0.1 User Guide: WSPR Type 1, Type 2 and Type 3 message formats; random `Tx Pct` scheduling; Windows `--rig-name` file isolation; Audio settings and file locations. QRP Labs, <a href="https://qrp-labs.com/qmx">*QMX firmware history and manuals*</a> and <a href="https://www.qrp-labs.com/images/qmx/manuals/operation_1_04_004.pdf">*QMX Operating Manual, firmware 1_04_004*</a> and <a href="https://qrp-labs.com/images/qmx/manuals/VirtualU3S_1_04_008a.pdf">*Virtual U3S Manual, firmware 1_04_008a*</a>: model-specific firmware, Virtual U3S operation and scheduling; <a href="https://www.qrp-labs.com/images/ultimate3s/operation3.12a2.pdf">*Ultimate3S Operating Manual, firmware v3.12a2*</a>: WSPR frequency range, global Frame/Start behavior, extended WSPR, sequential mode entries and per-entry `Aux` values; <a href="https://qrp-labs.com/images/appnotes/AN003_A4.pdf">*AN003: Ultimate3/3S relay-switched filters*</a>: filtered relay/driver interfacing and RF-off switching intervals. Accessed 2026-10-03.

* <a id="ref-13"></a><a href="https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018SW002008">[Ref-13]</a> **Peer-reviewed article.** Frissell, N. A. et al. (2019). *High-Frequency Communications Response to Solar Activity in September 2017 as Observed by Amateur Radio Networks*. Space Weather, 17(1), 118–132. doi:10.1029/2018SW002008.

* <a id="ref-14"></a><a href="https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2022GL097879">[Ref-14]</a> **Peer-reviewed article.** Frissell, N. A. et al. (2022). *First Observations of Large Scale Traveling Ionospheric Disturbances Using Automated Amateur Radio Receiving Networks*. Geophysical Research Letters, 49(5), e2022GL097879. doi:10.1029/2022GL097879.

* <a id="ref-15"></a><a href="https://www.researchgate.net/publication/334612025_Estimating_LF-HF_band_noise_while_acquiring_WSPR_spots">[Ref-15]</a> **Technical report.** Griffiths, G.; Robinett, R.; Elmore, G. (2019). *Estimating LF–HF band noise while acquiring Weak Signal Propagation Reporter (WSPR) spots*. Version 12, March–November 2019.

* <a id="ref-16"></a><a href="https://www.arrl.org/files/file/QEX_Next_Issue/SeptOct2020/TOFC.pdf">[Ref-16]</a> **Amateur-radio technical journal article; issue contents.** Griffiths, G.; Robinett, R.; Elmore, G. (2020). *Estimating LF-HF Band Noise While Acquiring WSPR Spots*. QEX, September/October 2020, starting on p. 25.

* <a id="ref-17"></a><a href="https://f6irf.blogspot.com/2008/04/">[Ref-17]</a> **Operator technical reports.** Destrem, P. / F6IRF (2008). *A statiscal method to evaluate TX antenna performance using WSPR* (24 April), follow-up TX analysis, 160 m RX comparison and station comparisons (April 2008).

* <a id="ref-18"></a><a href="https://www.charlespreston.net/antenna/WSPR-Antenna-Prop-Exp-PR.pdf">[Ref-18]</a> **Preliminary technical report.** Preston, C. / KL7OA (later K7TAA) (2009). *WSPR Antenna and Propagation Experiment: Preliminary Results*. Version 1.0, 31 March 2009; the available copy includes an update dated 25 June 2017.

* <a id="ref-19"></a><a href="https://www.arrl.org/files/file/QEX_Next_Issue/July-August2017/TOFC.pdf">[Ref-19]</a> **Amateur-radio technical journal article; issue contents.** Preston, C. / K7TAA (2017). *Antenna Comparisons Using Simultaneous WSPR Measurements*. QEX, July/August 2017, 8–14.

* <a id="ref-20"></a><a href="https://www.darc.de/fileadmin/filemounts/distrikte/g/2026/Talk_in_G/Talk-G_Antennenvergleich_synchr_WSPR_T.Rietdorf_DL2OAH_V2.1_17012025.pdf">[Ref-20]</a> **Amateur-radio technical presentation.** Rietdorf, T. / DL2OAH (2026). *Antennenvergleich mit synchronen WSPR-Daten*. DARC OV R10, 2. Talk in G, TH Köln, 17 January 2026, version 2.1; measurements from 12–21 January 2025. The presentation date is printed on slide 1; the PDF filename ending in 2025 does not give its presentation year.

* <a id="ref-21"></a><a href="https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf">[Ref-21]</a> **Conference paper.** Griffiths, G.; Robinett, R. (2020). *Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana*. ARRL/TAPR Digital Communications Conference 2020.

* <a id="ref-22"></a><a href="https://wspr.rocks/help.html">[Ref-22]</a> **Tool documentation.** WSPR.Rocks, *Help &amp; Documentation*: SpotQ, SQL access, duplicate analysis, maps, charts and heatmaps. <a href="https://wspr.rocks/head2head/">*Head2Head*</a>: comparisons of receivers, transmitters and software versions; passband inspection is also described in the help.

* <a id="ref-23"></a><a href="https://www.sotabeams.co.uk/wsprlite-classic">[Ref-23]</a> **Product documentation.** SOTABEAMS, *WSPRlite Classic / DXplorer*: WSPR-based antenna-performance analysis and DX10 metric.

* <a id="ref-24"></a><a href="https://www.sotabeams.co.uk/blog/indoor-hf-antennas-does-it-make-much-difference/">[Ref-24]</a> **Operator experiment and product application.** Newstead, R. / SOTABEAMS (2017). *Indoor HF antennas - does it make much difference?*. 5 May 2017.

* <a id="ref-25"></a><a href="https://sites.google.com/myuba.be/wspr-station-compare/home">[Ref-25]</a> **Project documentation.** WSPR-Station-Compare, project page referencing Vanhamel et al. and Zander. Machiels, W. / ON4AWM, <a href="https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-station-compare-app">*WSPR Station Compare App*</a>: RX comparison, receiver-offset correction, observation thresholds, callsign filtering and azimuth selection.

* <a id="ref-26"></a><a href="https://tools.bsdworld.org/wap">[Ref-26]</a> **Tool documentation.** Fred, W6BSD, *Antenna Performance Analysis*: WSPR report generator showing observed reception by time, location and band. The former wspr.bsdworld.org address redirects to the current tools site.

* <a id="ref-27"></a><a href="https://www.gm4eau.com/home-page/wspr/">[Ref-27]</a> **Tool documentation.** GM4EAU, *WATT WSPR Analysis Tool*: Excel/VBA reporting, mapping, filtering and timeline animation. <a href="https://rsgb.org/main/blog/tonight-at-eight-archive/2023/12/18/4-december-amateur-radio-construction/">RSGB presentation notice</a>: attribution to Colin Murray, GM4EAU.

* <a id="ref-28"></a><a href="https://qrp-labs.com/qmxp/wsprcorruption.html">[Ref-28]</a> **Manufacturer technical investigation.** QRP Labs, *WSPR Type 3 callsign corruption*: observed compound-callsign hash collision or misassociation behavior in large WSPR datasets and its mechanism. Accessed 2026-08-25.

* <a id="ref-29"></a><a href="https://github.com/HarrydeBug/WSPR-transmitters/blob/1657468ea27052167191a7deda2440a535567ecd/Standard%20Firmware/Release/Hardware_Version_2_ESP8285/WSPR-TX2.19/WSPR-TX2.19.ino">[Ref-29]</a> **Published firmware source, immutable revision.** ZachTek WSPR-TX firmware `2.19` for ESP8285 hardware: `DoWSPR()` message sequencing and frequency selection, `CorrectTimeslot()` scheduling, `WSPRCallHash()` suffix limitation, centihertz frequency units, product-model selection and build prerequisites. Revision `1657468ea27052167191a7deda2440a535567ecd`. Accessed 2026-08-25; sequencing and timing rechecked 2026-10-25.

* <a id="ref-30"></a><a href="https://www.itl.nist.gov/div898/handbook/eda/section3/eda351.htm">[Ref-30]</a> **Statistical reference.** NIST/SEMATECH, *e-Handbook of Statistical Methods*: *Measures of Location* (Section 1.3.5.1) and <a href="https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm">*Measures of Scale* (Section 1.3.5.6)</a>. Definitions and interpretation of mean, median, standard deviation, median absolute deviation and interquartile range. Accessed 2026-10-25.

* <a id="ref-31"></a><a href="https://www.itl.nist.gov/div898/handbook/prc/section3/prc311.htm">[Ref-31]</a> **Statistical reference.** NIST/SEMATECH. *e-Handbook of Statistical Methods*: *Analysis of paired observations*, §7.3.1.1, and <a href="https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm">*Confidence limits for the mean*, §1.3.5.2</a>.

* <a id="ref-32"></a><a href="https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf">[Ref-32]</a> **Metrology guide.** JCGM (2008). *Evaluation of measurement data — Guide to the expression of uncertainty in measurement*. JCGM 100:2008, particularly §4.2.7 on correlated observations and Annex G.2–G.3 on the normal approximation and Student‑t distribution.

* <a id="ref-33"></a><a href="https://www.nist.gov/publications/calculation-uncertainty-mean-autocorrelated-measurements">[Ref-33]</a> **Peer-reviewed article.** Zhang, N.-F. (2006). *Calculation of the uncertainty of the mean of autocorrelated measurements*. *Metrologia*, 43, S276–S281. DOI: 10.1088/0026-1394/43/4/S15.

* <a id="ref-34"></a><a href="https://www.arrl.org/files/file/QEX%20Binaries/March%202026/Contents.pdf">[Ref-34]</a> **Amateur-radio technical journal article; issue contents.** Ostergaard, D. / N3HXZ (2026). *Using WSPR to Predict Relative Antenna Gain of Directional Antennas*. *QEX*, March/April 2026, starting p. 19. Additional primary documentation: [Whispering Antenna — WSPR Methodology](https://www.n3hxz.net/wspr-methodology) and [Case Studies](https://www.n3hxz.net/case-studies): sequential antenna switching, linear-power averaging, receiver evidence requirements and practical antenna comparisons.

* <a id="ref-35"></a><a href="https://github.com/K5OHY/FarField-Lab">[Ref-35]</a> **Open-source application and technical documentation.** Tim / K5OHY (2026). *FarField Lab*: WSPR and RBN antenna comparison software supporting sequential ABAB/ABBA experiments, alternating-block analysis, receiver-level relative-gain estimates and statistical validation. [Live application](https://farfieldlab.streamlit.app/); [technical methodology](https://github.com/K5OHY/FarField-Lab/blob/main/docs/METHODOLOGY.md); [published-study validation](https://github.com/K5OHY/FarField-Lab/blob/main/tests/test_dale_study.py). Accessed 2026-11-08.

<div style="page-break-before: always;"></div>

<a id="sec-8-5"></a>
<a id="sec-disclaimer"></a>

## Experimental Use & Disclaimer

WSPRadar is a free, non-commercial hobby project developed for amateur-radio experimentation, education and scientific exploration.

WSPRadar analyzes observational data from publicly available WSPR reporting databases. Both the source data and the resulting analyses may contain errors, omissions, reporting biases or inaccuracies. Statistical assumptions, uncontrolled propagation conditions and software defects may further affect the reliability and interpretation of results.

WSPRadar is not a calibrated measurement instrument. Its findings are indicative and should be independently verified. Results must not be relied upon as the sole basis for significant personal, financial, safety-related, technical, legal or other consequential decisions. **WSPRadar is not intended for safety-critical applications, emergency decision-making or establishing compliance with legal or regulatory requirements.**

The software, service and results are provided **“as is” and “as available.”** No additional contractual guarantee is given regarding accuracy, completeness, reliability, fitness for a particular purpose or continuous availability. This statement does not exclude or restrict statutory rights.

Use and interpretation of the results remain the user's responsibility, including independently assessing their suitability before acting on them. Mandatory statutory rights remain unaffected.
