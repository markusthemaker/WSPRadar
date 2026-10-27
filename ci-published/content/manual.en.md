
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

A <strong class="defined-term">spot</strong> is a report of a successful decode. It records the transmitter and receiver identities and locations, time, band, reported transmit power and <strong class="defined-term">SNR</strong> — signal-to-noise ratio in dB. Higher SNR means a stronger signal relative to noise; a negative value does not mean decoding failed.

**WSPRadar analyzes uploaded reports; it does not receive or decode radio signals.** WSPRnet displays reception reports. WSPRadar normally reads **wspr.live**, with **WSPRDaemon WD2** and **WD1** as alternatives; each run uses one database without combining sources. See [data availability and source selection](#sec-6-6) <a href="#ref-10">[Ref-10]</a> <a href="#ref-11">[Ref-11]</a>.

Reports show successful decodes, not every attempted transmission or listening receiver. **A missing spot alone does not prove a failed reception.** How WSPRadar handles that uncertainty depends on the analysis you choose.

<a id="sec-1-0"></a>
<a id="sec-1-2"></a>

### 0.2 What WSPRadar can show

The <strong class="defined-term">Target</strong> is the station or signal path you want to investigate. A <strong class="defined-term">peer</strong> is a remote station whose radio path contributes to the analysis: a transmitter in RX, or a receiver in TX.

<strong class="defined-term">Performance</strong> examines the Target on its own. <strong class="defined-term">Benchmark</strong> compares it with one <strong class="defined-term">Reference</strong> — another controlled signal path or a known station.

| Your question | Choose | What it examines |
|---|---|---|
| What can this station receive, and how consistently? | <strong class="defined-term">RX Performance</strong> | Remote transmitters heard by the Target, with activity evidence supporting successes and misses. |
| Where is this station heard, and how consistently? | <strong class="defined-term">TX Performance</strong> | Remote receivers hearing the Target, with activity evidence supporting successes and misses. |
| How do two receiving setups compare? | <strong class="defined-term">RX Benchmark</strong> | Target and Reference receiving the same remote transmitters in the same WSPR cycles. |
| How do two transmitting setups compare? | <strong class="defined-term">TX Benchmark</strong> | The same remote receivers hearing Target and Reference in the same WSPR cycles. |

Performance is useful for establishing a station baseline or investigating geographic and time patterns. Benchmark can compare antennas, feedlines, receivers, filters, preamplifiers or complete setups. An independent Reference compares complete installed stations, including their sites and noise environments; it is not automatically a calibrated standard.

<a id="sec-1-3"></a>

### 0.3 What one run produces

A <strong class="defined-term">run</strong> processes reports for one analysis choice, band, UTC window and set of settings. It produces maps, summaries over distance and time, station tables and individual observations you can inspect.

The physical <strong class="defined-term">experiment</strong> is the on-air setup and operation that produced those reports. Changing how you display a completed run does not create a new experiment.

Use the results to ask whether a pattern is broad or limited to a few stations, whether it persists over time, and how much evidence supports it. The results and their settings can be downloaded for later review; your own setup notes complete the record.

<a id="sec-1-4"></a>

### 0.4 Your first useful run

Start with **Load Demo**. Choose a maintained example, read its experiment notes and follow the app's setup and run controls, keeping the prepared settings for the first run. Loading settings alone does not start an analysis. In Guided, **Walk me through the setup** opens the steps; **Skip to review and run** starts the valid loaded analysis directly.

Follow one feature from the map to its contributing stations and individual observations. Open **How to read this** beside any result for its metric, legend and interpretation. A demo teaches the method; it is not evidence about your station. Then use [Chapter 1](#sec-2) to prepare your own run.

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
            * [5.5.2.3 Shared timing, frequency lanes and verification](#sec-simultaneous-tx-setup-5-3-1)
    * [5.6 Confirm by exchange or crossover](#sec-simultaneous-tx-setup-6)
* [6. Reference SNR Calibration](#sec-reference-snr-calibration)

**Part III: Scientific Foundations, Methods and Claims**

* [7. Literature, Prior Art and Positioning](#sec-d)
    * [7.1 From reporting network to experimental dataset](#sec-d-1)
    * [7.2 Making observational WSPR data interpretable](#sec-d-2)
    * [7.3 Antenna and station-comparison lineage](#sec-d-3)
    * [7.4 Analysis infrastructure and related tools](#sec-d-4)
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
        * [8.4.4 Combining dates by UTC hour](#sec-7-view-folding)
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
2. **Verify the database identities.** Check the exact RX reporting callsign or TX callsign, reported locator and UTC times in WSPRnet, then in the database WSPRadar will use. Use the callsign exactly as recorded, including any existing suffix. Choose a completed period and allow reports to arrive; no fixed delay guarantees completeness. See [data troubleshooting](#sec-6-6).
3. **Keep the setup interpretable.** Record the antenna, feedline, radio, decoder, gain or power settings, software, schedule and deliberate changes. Keep other variables stable and clocks synchronized. For Benchmark, prepare both setups using [RX guidance](#sec-3-rx-benchmark-hardware) or [TX guidance](#sec-3-tx-benchmark-simultaneous) before collecting the comparison.

<a id="sec-2-2"></a>

#### 1.2 Configure your analysis

Choose the analysis from [Section 0.1](#sec-1-0). <strong class="defined-term">Guided</strong> leads you through the settings; <strong class="defined-term">Compact</strong> presents the same scientific choices in a shorter form.

Enter the exact **Target callsign**, **Target QTH** (Maidenhead locator), one **band**, and a completed **UTC window**. Target QTH accepts four or six locator characters: the first four select reports, while the full entered locator anchors the map, distances and directions. Longer windows add evidence but can mix operating and propagation conditions.

<a id="sec-2-5"></a>

**For Benchmark**, enter one exact Reference callsign different from the Target callsign. Leave its optional QTH blank to discover the location from reports, or enter its independently known four-character locator. Choose explicitly if several locations are found. A location does not prove operation or physical co-location.

Confirm the operating conditions independently:

- **RX Benchmark:** both receivers listened on the selected band with functioning uploads throughout the period. This does not require a decode in every cycle.
- **TX Benchmark:** both transmitters sent in the same WSPR cycles, with aligned schedules and message patterns.

Keep supporting operating records. WSPRadar records your confirmation; it cannot verify continuous operation from successful reports. <strong class="defined-term">Historical replay</strong>, used by the maintained Milazzo example and saved replay configurations, describes historical reports without independently verified common operation. It requires acknowledgement of those limits, rather than a claim of controlled operation; see [Section 10.3](#sec-5-3).

Leave **Reference SNR correction** at **No correction** unless you have an independently established offset valid for this setup. See [calibration guidance](#sec-reference-snr-calibration).

For the first run, review the displayed filters and evidence requirements without lowering them merely to obtain more colored map areas. **Maximum peer distance from Target (km)** changes which remote stations enter the analysis, not just the map zoom; choose it to match your question. See [scope and evidence controls](#sec-5-4). Check the final summary, then select **Run RX Analysis** or **Run TX Analysis**. Exact controls are in [Chapter 10](#sec-5); unexpected gaps are addressed in [Chapter 11](#sec-6).

<a id="sec-2-3-overview"></a>

#### 1.3 Navigate the results

Use one path through the results, rather than trying to read every panel at once. Open **How to read this** beside a view whenever you need its legend, counting rules or interpretation.

<a id="sec-3-4"></a>
<a id="sec-3-5"></a>

**1.** <strong class="defined-term">Global View</strong> **— where is the pattern?** A <strong class="defined-term">map segment</strong> covers a range of directions and distances from the Target. Read its numerical scale and supporting counts. An uncolored area is not automatically zero reception; check whether evidence is absent or below the required minimum.

<a id="sec-3-6"></a>
<a id="sec-3-6a"></a>
<a id="sec-3-6b"></a>

**2.** <strong class="defined-term">Segment Inspector</strong> **— how broad and persistent is it?** Choose the directions and distances to examine. This <strong class="defined-term">active scope</strong> controls the segment statistics and temporal figures. Compare station and observation counts, then check individual dates before calling a combined UTC-hour pattern recurring. In <strong class="defined-term">Benchmark Statistics</strong>, compare the spot-pair and station-median ΔSNR distributions: frequently observed stations contribute more to the first.

<a id="sec-3-7"></a>
<a id="sec-3-7a"></a>
<a id="sec-3-7b"></a>

**3.** <strong class="defined-term">Station Insights</strong> → <strong class="defined-term">Selected Station Evidence</strong> **— which stations explain it?** Select a typical station, an unusual one, or a station contributing many reports. Performance follows the Inspector scope. In Benchmark, the station list is global by default; **Filter by selected segment and distance** optionally narrows the list, while selected-station evidence keeps the full run. In Benchmark, enable **Include one-sided evidence** to inspect identities without spot pairs and one-sided Drill-Down observations.

<a id="sec-3-8"></a>

**4.** <strong class="defined-term">Drill-Down</strong> **— what happened in individual cycles?** Check exact identities, UTC times, SNR and outcomes. A focused time window helps inspect a particular interval. These are processed observations after matching and filtering, not an untouched database download.

<a id="sec-3"></a>

### 2. Run and Interpret Your Analysis

Read the section for your chosen analysis. The essentials below explain what the result means; **How to read this** beside each result explains its plots and controls in detail.

**Understand the counting unit.** A remote <strong class="defined-term">station identity</strong> is an exact callsign and full reported locator. One callsign at two reported locators counts as two identities, not necessarily two independent physical stations. Multiple qualifying reports for one setup, remote identity and cycle count as one observation.

**Benchmark compares signal quality and decoding.** A <strong class="defined-term">spot pair</strong> matches Target and Reference for one remote identity in the same WSPR cycle: the same transmitter in RX, or the same receiver in TX. <strong class="defined-term">Both observed</strong> is a station-level label and can include reports from different cycles; it does not by itself establish a spot pair.

- <strong class="defined-term">ΔSNR</strong> (delta SNR) is Target SNR minus corrected Reference SNR for a spot pair. Positive favors Target; negative favors Reference; **0 dB** means equal SNR. For example, **+3 dB** means 3 dB higher Target SNR in that comparison. It cannot describe a signal decoded on only one side.
- <strong class="defined-term">ΔDecode</strong> compares total observed decodes, including one-sided reports. The map's ratio legend is direct: **2× on the Target side** means twice the Reference decode total; **1×** means equal totals; <strong class="defined-term">Exclusive</strong> means only one side has decodes. Signals missed by both setups remain unknown, so ΔDecode is not a success rate over all transmissions. See [the exact calculation](#sec-7-benchmark-aggregation).

The ΔSNR map gives every station meeting its spot-pair minimum over the filtered run equal weight: first take each station's <strong class="defined-term">median</strong> — the middle ordered value, or the average of the two middle values — then the median of those station medians. ΔDecode uses <strong class="defined-term">pooled totals</strong>: it adds all retained decodes, so frequently observed stations contribute more. These measures can favor different setups. Benchmark ΔSNR time plots pool spot pairs from qualifying stations within each bin, so frequently observed paths can have more influence than on the ΔSNR map.

**Performance counts confirmed opportunities.** A <strong class="defined-term">confirmed opportunity</strong> is one remote identity and cycle in which a Target success occurred, or activity evidence at both ends supports counting a miss. <strong class="defined-term">Decode Rate</strong> is successes divided by successes plus confirmed misses, expressed as a percentage. Unknown activity is excluded; the RX and TX rules are explained below.

A <strong class="defined-term">qualifying station</strong> meets the configured evidence minimum for the metric: spot pairs for ΔSNR, confirmed opportunities for Performance. Map segments have separate support requirements. Counts establish how much evidence is present, not statistical confidence or independent physical stations.

**Check the SNR basis.** WSPRadar adjusts successful SNR to a common **reported transmit power of 1 W (30 dBm)**. This adjusts the comparison, not the observed decode counts, and cannot repair incorrect power reports. The cumulative plots between the Benchmark maps are the exception: they use <strong class="defined-term">raw reported SNR</strong>, without power adjustment or Reference correction. Details are in [Section 8.1.2](#sec-7-normalization-consolidation).

<a id="sec-3-3"></a>
<a id="sec-3-rx-benchmark"></a>

#### 2.1 RX Benchmark

**Question:** How did two receiving setups compare for the same transmitters and cycles?

For a controlled RX Benchmark, both receivers must have been listening and reporting throughout the selected period. Benchmark retains eligible reports from either side even in cycles with no Target report; interpretation relies on the operating conditions described in [Section 1.2](#sec-2-2), not a per-cycle Target-activity check.

**First checks:**

1. Compare the **ΔSNR** and **ΔDecode** maps: does higher SNR among shared decodes accompany more total decodes?
2. Use the cumulative SNR plots to distinguish additional decodes from additional distinct transmitters. A one-sided decode need not add a new station.
3. In the Inspector, check whether the difference persists across several transmitters and times. Inspect a representative path in Station Insights and Drill-Down.

The minimum spot-pair count qualifies a station for ΔSNR; it does not remove its observed decodes from ΔDecode. The two maps have different support requirements. Sparse evidence can produce a large value, so read counts as well as colors. See [evidence thresholds](#sec-5-4).

<a id="sec-2-3"></a>
<a id="sec-3-rx-benchmark-hardware"></a>

##### 2.1.1 Reference Setup/Station

**Controlled local setup.** Use simultaneous, separately identified receiving paths for the antennas, feedlines, filters, preamplifiers or receivers you want to compare. Verify both exact reporting callsigns and their locations in the database. A shared four-character locator does not establish physical co-location or identical signal paths.

Keep non-tested parts of the chains equal, or measure their differences: receiver, gain, filtering, audio, decoder and uploads can all affect the result. A common-input calibration or swapping components between chains helps check whether an observed difference follows the tested component. Components intended to be common must actually be shared. See [parallel WSJT-X instances](#sec-a) and [Reference calibration](#sec-reference-snr-calibration).

RX reporting identities such as `CALL` and `CALL/P` may distinguish paths if the software and database preserve them. They do not change the remote transmitter's message format.

<strong class="defined-term">Reference correction</strong> applies an independently established offset to Reference SNR before subtraction. A positive correction raises Reference SNR and reduces the displayed Target advantage. It does not recover missed decodes or change ΔDecode. A geographically separated Reference can provide a repeatable baseline for that pair, not an absolute calibration.

<a id="sec-3-rx-benchmark-buddy"></a>

**Independent station.** Choose a Reference whose identity, location, setup and operating schedule you understand. The comparison includes both stations' antennas, equipment, noise and propagation paths. Repeat with the same stable Reference; describe complete-station differences without attributing them to one antenna or receiver. The maintained Griffiths/Squibb demo provides an example.

<a id="sec-3-tx-benchmark"></a>

#### 2.2 TX Benchmark

**Question:** How did two transmitting setups compare at the same remote receivers in the same cycles?

Each spot pair holds the receiving endpoint and cycle in common. Unlike RX pairs observing one transmitter, TX pairs compare different transmissions, so accurate reported power is essential to normalized ΔSNR. Actual power differences can still affect decode counts, which are not power-normalized.

**First checks:** compare the two maps, inspect receiver and pair counts, then follow representative receivers through the time views and Drill-Down. Check whether a result depends on a few receivers, one interval or an audio-frequency assignment. Better paired SNR does not guarantee more total decodes.

One-sided evidence remains included without a separate Target-activity check. If one transmitter was silent or reporting was interrupted, ΔDecode can reflect unequal operating opportunities. Establish common operation before interpreting it as a difference between transmit paths.

<a id="sec-2-4"></a>
<a id="sec-2-4-simultaneous"></a>
<a id="sec-3-tx-benchmark-simultaneous"></a>

##### 2.2.1 Reference Setup/Station

**Controlled local setup.** Use two distinguishable transmitter chains with distinct valid exact callsigns, synchronized WSPR cycles, clear separated frequencies, measured and truthfully reported power, and adequate RF isolation. A single transmitter alternating between antennas cannot provide simultaneous spot pairs.

**Prefer two different valid ordinary callsigns.** Choose callsigns that each fit the one-transmission WSPR format, carrying callsign, locator and power together.

If <strong class="defined-term">compound callsigns</strong> — callsigns with an added prefix or suffix — are needed, two distinct valid compound callsigns can also work. For this controlled comparison, use matching, verified message sequences and align their corresponding transmissions. [Section 5.1](#sec-simultaneous-tx-setup-1) explains the callsign choices and the message formats they produce.

Verify firmware settings, actual schedules and both database identities before collecting evidence. WSPRadar compares individual two-minute cycles; unmatched schedules can create one-sided reports without any equipment advantage. Follow [Chapter 5's setup and database preflight](#sec-simultaneous-tx-setup).

The result compares complete transmit paths. Frequency response, QRM, coupling and power error can remain; swap frequency positions and, where practical, the tested antennas or components between chains. Use only a documented **Reference SNR correction** valid for the comparison; it affects ΔSNR, not decode counts. See [calibration guidance](#sec-reference-snr-calibration).

<a id="sec-3-tx-benchmark-buddy"></a>

**Independent station.** Choose a known Reference transmitter with understood identity, QTH, power, equipment and schedule. The same receiver and cycle can be shared while the transmitting sites and propagation paths differ. Equal four-character locators do not prove co-location. Describe the result as a comparison of complete installed stations.

Both arrangements use **Reference Setup/Station**. Spot pairs are required for ΔSNR, but one-sided evidence can still contribute to ΔDecode when no pairs exist. The physical arrangement determines what can be concluded, not whether the callsigns share a base.

<a id="sec-3-1"></a>
<a id="sec-3-2"></a>
<a id="sec-3-rx-performance"></a>

#### 2.3 RX Performance

**Question:** What did the Target receive, where, and how consistently during confirmed opportunities?

Use one exact Target receiving identity and QTH, one band, and a period with uploaded Target decodes. Keep the receiving chain stable; no Reference is needed.

**What counts:** a Target decode confirms a successful opportunity by itself, even if no other receiver reported that transmitter. A miss requires another receiver to report the transmitter **and** a Target decode of another transmitter to establish that the Target was active on the **same band in the same cycle**. Without that evidence, the missing decode remains unknown.

Read three complementary measures:

- <strong class="defined-term">At-least-once reach</strong>: the percentage of qualifying transmitters the Target heard at least once. One success does not imply regular reception.
- <strong class="defined-term">Station-balanced Decode Rate</strong>: the average of the qualifying transmitters' individual rates, with equal weight per identity. The map uses this rate. <strong class="defined-term">Opportunity-level Decode Rate</strong>: total successes divided by all their confirmed opportunities. Frequently observed stations influence this second rate more.
- <strong class="defined-term">Successful SNR</strong>: signal-to-noise ratio for decoded signals, adjusted to the common reported-power basis. Misses have no measured Target SNR.

For example, two qualifying stations with **90 successes out of 100 opportunities** and **5 out of 10** give a station-balanced rate of **70%**, but an opportunity-level rate of **86.4%** (95 out of 110). Neither weighting replaces the other.

Use the map to locate a pattern, compare reach and both rates in **Performance Evidence**, then inspect the contributing transmitters. The temporal overview shows departures from each station's median successful SNR over the run; the selected-station view shows its normalized SNR values. **How to read this** explains the weighting and chart details.

If Decode Rate falls while successful SNR rises, weak signals may have stopped being decoded; stronger surviving reports alone do not show an improvement. Repeat the affected paths and time periods. A claim about one hardware change needs a controlled comparison or crossover, because Performance also reflects local noise, other equipment and propagation.

<a id="sec-3-tx-performance"></a>

#### 2.4 TX Performance

**Question:** Which receivers heard the Target, where, and how consistently during confirmed opportunities?

Use one exact Target transmitting identity and QTH, one band, and a period with observed Target transmissions. Keep the RF path, schedule and actual power stable, and report power accurately; no Reference is needed.

**What counts:** a receiver's report of the Target confirms a successful opportunity, even if it reports no other transmitter. A miss requires that **same receiver** to report another transmitter on the selected band **and** a report of the Target somewhere to establish its activity in the **same cycle**. Another receiver hearing the Target does not prove that a silent receiver was listening. Each success counts once; unknown activity remains excluded.

Read **at-least-once reach** — the percentage of qualifying receivers that heard the Target at least once — alongside Decode Rate and successful SNR. **Station-balanced Decode Rate** averages receiver rates equally; **Opportunity-level Decode Rate** combines their success and opportunity counts. The map uses the station-balanced rate. Counts describe the confirmed opportunities, not every planned transmission or all possible receivers.

Use **Performance Evidence** and the time views to locate a pattern, then inspect representative receivers. The temporal overview shows deviations from each receiver's median successful SNR over the run; selected-station evidence shows normalized SNR values. Check individual dates before describing a recurring daily pattern.

A broad footprint with low Decode Rates can mean intermittent reception; a high rate across a few receivers does not establish broad coverage. Results include actual transmit power, antenna and feedline, terrain, propagation and remote receiving conditions. They do not measure radiated power, antenna gain or efficiency. Use **TX Benchmark** for a relative transmit-path question and repeat useful observations under comparable conditions.

<a id="sec-outlier"></a>

#### 2.5 Find and Review Temporary ΔSNR Departures

This optional expert diagnostic finds temporary changes in paired ΔSNR for one exact remote identity, or <strong class="defined-term">path</strong>. Complete the ordinary Benchmark review first; an outlier candidate is a prompt for investigation, not an identified physical event.

<a id="sec-outlier-1"></a>

##### 2.5.1 When to use this expert diagnostic

Use it when a temporary change matters to your question and enough spot pairs exist before, during and after it. One-sided reports provide context but no missing ΔSNR. An empty report may mean insufficient surrounding evidence, not an unchanged path.

Enable **Identify ΔSNR outlier candidates**, review the [three expert controls](#sec-5-6), then run the analysis. Changing the settings requires another explicit run.

<a id="sec-outlier-2"></a>
<a id="sec-outlier-3"></a>

##### 2.5.2 How detection works in practice

The <strong class="defined-term">local baseline</strong> estimates the path's usual ΔSNR from supported observations before and after a candidate, excluding the candidate. A <strong class="defined-term">departure</strong> is observed ΔSNR minus that baseline. Thus **+1 dB ΔSNR against a +8 dB baseline is a −7 dB departure**: Target still has higher SNR, but its advantage has fallen.

The detector checks departure size, a <strong class="defined-term">robust z-score</strong> measuring departure relative to nearby variation, agreement of the before/after baseline medians, and sign agreement within the candidate. It uses actual cycle observations before display aggregation; changing a chart's time-bin width does not change detections. Event classes and cross-path groupings do not establish different certainty or a common cause. See [the method](#sec-7-outliers).

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

Use a result to guide the next station decision, with a claim no broader than the evidence.

<a id="sec-4-1"></a>

#### 3.1 Judge breadth, consistency and repeatability

Check three things before drawing a conclusion:

- <strong class="defined-term">Breadth:</strong> how many station identities, observations, directions and time periods support it? Many reports from one station do not provide the same breadth as several paths. Reported identities are not guaranteed independent physical stations.
- <strong class="defined-term">Consistency within the run:</strong> do geography, time and station views support a similar description? If station-balanced and pooled results differ, inspect the stations contributing most observations. Read paired ΔSNR with one-sided decoding evidence, or Performance SNR with Decode Rate.
- <strong class="defined-term">Repeatability:</strong> does the pattern recur in a separate run under comparable, documented conditions? Agreement among views of the same data does not establish this.

An extreme value or a met evidence threshold is not proof of an equipment advantage or statistical confidence. First describe what was observed; test explanations such as noise, propagation or hardware changes through controlled changes, crossover tests or independent measurements. [Section 8.5](#sec-7-claims) explains dependence and bias.

<a id="sec-4-2"></a>

#### 3.2 Strengthen a result through repetition and control

An <strong class="defined-term">exploratory run</strong> finds a possible pattern. Before a <strong class="defined-term">confirmatory run</strong>, fix the question, direction, band, Reference where applicable, settings, thresholds, schedule and primary geographic or time scope. This includes **Maximum peer distance from Target (km)**. Preserve alternative scopes as separate checks; do not report only the most favorable selection.

Repeat on another day or propagation period while keeping non-tested variables stable. Use a long enough window to cover the conditions named in your conclusion; claims about daily patterns need evidence across dates, checked chronologically. Keep notes so the physical setup can be reproduced.

RX and TX use different remote populations and opportunity rules. Align band, period, scope and configuration when examining station balance, but interpret the directions separately: equal percentages do not imply equal receive and transmit capability.

<a id="sec-4-3"></a>

#### 3.3 Write an evidence-matched conclusion

Name the Target, analysis type, band, UTC window and geographic scope, then give the result **with its weighting and supporting counts**. For Benchmark, also name the Reference, applied Reference SNR correction (including zero), and the known common-operation conditions, or state the historical-replay limitation.

**Performance template**

> For [Target, band, UTC window and scope], the station-balanced Decode Rate was [x%] across [n qualifying stations]. The opportunity-level rate was [y%] across [m confirmed opportunities]. The observed pattern was [broad, directional, intermittent, or specific to the stated time period].

**Benchmark template**

> For [Target and Reference, band, UTC window and scope], the median of station-median ΔSNR favored [setup] by [x dB], supported by [n qualifying stations and m spot pairs]. The pooled decode totals were [Target total] and [Reference total], with [Paired, Target-only and Reference-only counts]. The comparison used [controlled paths, independent stations, or historical replay].

Include station reach and relevant time patterns where they support the claim. Compare numerical legend values rather than color intensity across maps. Avoid converting a complete-station difference into antenna gain, efficiency, calibrated sensitivity or a physical cause that the experiment did not measure. [Chapter 9](#sec-8) provides the full reporting checklist and examples of supported claims.

<a id="sec-4-4"></a>

#### 3.4 Preserve the run and its context

Select the Inspector scope, station evidence and any focus interval you want to preserve. Choose **Prepare All Results for Download**, then **Download Prepared Results**. Preparing alone does not save the file; prepare again after changing those selections.

The ZIP includes configuration, metadata, processed evidence, applicable tables and figures. The processed evidence covers the completed run; individual tables and figures use their relevant inspection scopes. **Save Config** or an analysis link preserves settings, not the original observations. A later query or rerun can produce different results.

Keep concise station notes with the ZIP: antennas and feedlines, chain or splitter arrangement, hardware/software, gain and power, schedules, calibration and deliberate changes or faults. WSPRadar cannot infer these physical details. See [the record checklist](#sec-8-3) and [export contents](#sec-8-4).

<div style="page-break-before: always;"></div>

<a id="part-iv"></a>

## Part II: Practical Setup Guide

**Practical setup guide.** Set up two receive paths, prepare a simultaneous transmit comparison, or measure an RX correction. Choose the route for your experiment and complete its checks before collecting the measurement period.

| Goal | Route | Ready when |
|---|---|---|
| **Simultaneous RX on Windows** | [Chapter 4](#sec-a): create, optionally clone, then verify the two WSJT-X paths. Continue to [Chapter 6](#sec-reference-snr-calibration) if calibration is needed. | Both intended receivers upload under verified identities, with correct audio/data paths and synchronized clocks. |
| **Controlled simultaneous TX** | [Chapter 5](#sec-simultaneous-tx-setup): plan the common requirements, apply the 5.5 model recipe, then complete 5.2–5.3 bench checks and 5.4 database preflight. 5.6 confirms the result. | Clean, correctly placed signals produce same-cycle reports from common receivers under both intended identities. |
| **Documented RX SNR correction** | [Chapter 6](#sec-reference-snr-calibration): common-input measurement, consistency checks, signed correction and independent validation. | The offset is stable within recorded conditions and supported by separate validation evidence. |

Use instructions for the exact hardware and firmware; the ZachTek split-lane recipe requires custom firmware. When ready, return to [Section 1.2](#sec-2-2). Keep **No correction** unless an offset is justified.



<a id="sec-a"></a>
### 4. Parallel WSJT-X Instances for Simultaneous RX

**Goal:** run two receive paths at the same time, with separate audio, reporting identities, settings and files. This Windows procedure uses WSJT-X's documented `--rig-name` option; it does not require a second installation of WSJT-X <a href="#ref-12">[Ref-12]</a>.

Create two named instances: **WSJT-X Target** and **WSJT-X Reference**. Optionally copy a working starting configuration, then check both paths before collecting measurements. These names identify the local software instances; they do not set the callsigns uploaded to the database.

For a simultaneous TX experiment, use [Chapter 5](#sec-simultaneous-tx-setup). [Section 4.4](#sec-a-4) explains why matching two WSJT-X `Tx Pct` settings does not establish a shared sparse transmit schedule.



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

**Optional:** configure **WSJT-X Target** first using [4.3](#sec-a-3), then copy its configuration so **WSJT-X Reference** starts with the same settings. Otherwise configure both instances directly in 9.3.

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

**A shared clock does not select shared transmit cycles.** In ordinary WSPR operation, WSJT-X chooses transmit periods randomly according to **Tx Pct**. Two instances set to the same value below `100%` can coincide in some cycles, but that setting does not guarantee a synchronized sparse A/B schedule <a href="#ref-12">[Ref-12]</a>.

With transmission enabled, `Tx Pct = 100%` makes both instances attempt every cycle. A WSPR-2 message lasts about **110.6 seconds** of the 120-second cycle, giving an approximately **92%** <strong class="defined-term">RF key-down duty cycle</strong> — the fraction of time the transmitter is actually emitting RF <a href="#ref-8">[Ref-8]</a>.

WSPRadar recommends using about **5–20% of available cycles** for this experiment, with the lower end preferred on busy bands or during longer tests. This is an operating recommendation, not a WSPR protocol limit. A percentage of selected cycles and the RF key-down duty cycle are different quantities.

For a sparse simultaneous-TX comparison, use hardware with a deterministic schedule and verify its actual starts. [Chapter 5](#sec-simultaneous-tx-setup) gives routes for QMX/QMX+ Virtual U3S, Ultimate3S, and an advanced, model-specific ZachTek firmware procedure.



<div style="page-break-before: always;"></div>

<a id="sec-simultaneous-tx-setup"></a>
### 5. Simultaneous TX Reference Setup

**Goal:** transmit two distinguishable signals from the Target and Reference paths in the same WSPR cycles, using either two setups at one station or two coordinated stations. Remote receivers then provide the common observations for a TX Benchmark. The result compares the complete documented paths, including any equipment differences left uncontrolled.

Use this order of work:

| Stage | Action |
|---|---|
| **1. Plan** | Choose valid transmitting identities and a matching message pattern in [5.1](#sec-simultaneous-tx-setup-1). Record which identity belongs to each physical path. |
| **2. Configure** | Follow the recipe for your hardware in [5.5](#sec-simultaneous-tx-setup-5). For QRP Labs, start with one enabled entry using your chosen callsign route. The ZachTek route requires the model-specific firmware modification before the bench checks. |
| **3. Check on the bench** | Verify timing and signal placement in [5.2](#sec-simultaneous-tx-setup-2), then actual power and simultaneous signal quality in [5.3](#sec-simultaneous-tx-setup-3). |
| **4. Check the reports** | Complete a short on-air and database preflight in [5.4](#sec-simultaneous-tx-setup-4), then open the measurement window. |
| **5. Confirm the finding** | Repeat with exchanged frequency positions or hardware assignments as described in [5.6](#sec-simultaneous-tx-setup-6). |

Use callsigns and operating conditions valid for your station and licence. Complete RF safety, filtering and isolation checks appropriate to the hardware before connecting antennas.



<a id="sec-simultaneous-tx-setup-1"></a>
#### 5.1 Choose the callsigns

Choose the route that matches the callsigns available for the experiment. Target and Reference can be two setups at one station or two coordinated stations. Keep each complete callsign attached to its documented physical path throughout the experiment.

**RX and TX identities work differently.** An [RX reporting suffix](#sec-rx-reporting-identities) is uploaded over the internet. In TX, the callsign must be encoded in the radiated WSPR message, so an ordinary or compound callsign determines the message sequence needed <a href="#ref-12">[Ref-12]</a>.

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
4. **Frequency separation:** for the fixed-frequency QRP Labs examples, place the signal centers nominally **100 Hz apart**, with both complete signals comfortably inside the 200 Hz WSPR transmit sub-band. The ZachTek custom build instead uses the disjoint lower and upper lanes in [5.5.2](#sec-simultaneous-tx-setup-5-3).

Use the worked 40 m or 20 m settings in [5.5.1](#sec-simultaneous-tx-setup-5-1). Those settings specify **radiated RF frequencies**, not a receiver's USB dial frequencies. The cited QRP Labs manuals define the WSPR setting as the signal center; the ZachTek source patch controls the lowest tone, or <strong class="defined-term">tone 0</strong>. Use the convention for your exact firmware <a href="#ref-12">[Ref-12]</a> <a href="#ref-29">[Ref-29]</a>.

Check individual frequencies with suitable measurement equipment, then use a receiver waterfall or spectrum display to inspect both signals together. Confirm the intended separation or lanes and the complete signals' edge margins. Increasing separation reduces those margins. Repeat the timing and frequency checks after a restart, firmware update or configuration change.



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

Use a short on-air preflight to establish that the configured experiment reaches WSPRadar correctly.

1. Transmit several complete synchronized sequences with the final callsign, QTH, power, schedule and frequency settings.
2. Search the [WSPRnet Spot Query](https://www.wsprnet.org/drupal/wsprnet/spotquery) for **each exact callsign**. Inspect reports, not only the map, which can show a last-known locator.
3. Check the intended grid-4, reported power, timestamps and distinct frequencies. Find cycles in which the **same remote receiver reported both callsigns**.
4. Run a short **TX Benchmark** with those identities, band and UTC window. Wait until the reports are available from the selected database. wspr.live describes delays of a few minutes; individual uploads and service availability can take longer. Proceed from actual data availability rather than a fixed waiting time; see [Section 11.6](#sec-6-6).
5. Inspect Paired and one-sided counts, ΔSNR and pooled ΔDecode. Investigate unexpected concentrations of Only Target or Only Reference before treating them as a performance difference.

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

**Start, observe one hour, then collect the comparison.**

Verify UTC before starting. On Virtual U3S, set the main `Enable` to `ENABLED` and exit the menu; on Ultimate3S, use the right-button Start action to enter Run mode. Observe the schedule for your selected route above; both units must transmit corresponding phases together.

If using GPS frequency calibration, ensure it finishes before the next expected start. For an internal QLG3 on QMX+, set `GPS source = QMX+ Internal`. On physical U3S, calibration requires a nonzero `Cal Step` and an idle gap longer than `Cal Time + 4 seconds`; GPS connection alone does not establish successful calibration.

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

This is an **advanced, model-specific route**: it combines ordinary configuration with a source change that keeps the two transmitters in separate frequency regions. The worked example uses the pinned ESP8285 firmware in [Ref-29](#ref-29), revision `1657468ea27052167191a7deda2440a535567ecd`, which selects **WSPR-TX XP Plus, `Product_Model = 1048`**. Other models require a separately checked recipe. In this file, the Mini/Pico long-pause sleep call is disabled, and Pico startup forces altitude reporting; the pause and power instructions below therefore apply to the selected 1048 build.

Choose the route that matches the **on-air transmitting identities** you will use:

| Route | Identities and message pattern |
|---|---|
| [**1. Two distinct callsigns**](#sec-zachtek-two-ordinary-callsigns) | Two distinct valid Type 1 callsigns, used by two setups at one station or by two stations. Each scheduled sequence contains one transmission per setup. |
| [**2. One base callsign with two suffixes**](#sec-simultaneous-tx-setup-5-3-2) | One base callsign with two distinct permitted single-character suffixes. Each scheduled sequence contains a Type 2/Type 3 pair per setup. |

**Both routes require the same preparation:** enable only the selected test band, set **`PowerOption = Normal`**, and use each transmitter's truthful QTH. Both units need valid GPS time **and location**, including when the transmitted locator is entered manually. Normal power reporting uses the configured dBm as message data; it does not set RF output power. Altitude mode replaces that value with telemetry. Before on-air use, measure actual power and choose its encoded value as described in [Section 5.3](#sec-simultaneous-tx-setup-3).

Two colocated setups should report their common physical QTH. At two different stations, each transmitter reports its own QTH; the result compares complete installed stations and their different propagation paths. Keep the identity-to-physical-path mapping in the experiment record.

After configuring either route below, complete the shared **frequency patch → build → bench → on-air** procedure in [Section 5.5.2.3](#sec-simultaneous-tx-setup-5-3-1). The custom lane build is required for both callsign routes.

<a id="sec-zachtek-two-ordinary-callsigns"></a>
###### 5.5.2.1 Two distinct callsigns

Use this route when the Target and Reference each have a different valid callsign that fits the ordinary Type 1 WSPR format. The callsigns can identify two permitted setups at one station or two separate stations; they do not need suffixes to become distinguishable.

**Configure both units:**

1. Enter the Target's ordinary callsign in the Target unit's base-call field, and the Reference's different ordinary callsign in the Reference unit's field.
2. Explicitly select **no prefix/suffix** (`SuPreFixOption = None` in the cited source). Do this even if the displayed base call is already ordinary: changing that text alone does not disable a previously selected suffix or prefix. Stored suffix characters can remain unused; the selector is what chooses Type 1.
3. Set **`LocationPrecision = 4`** on both units. Precision `6` would add a Type 3 transmission even with an ordinary callsign.
4. Enable the same single test band, use **`PowerOption = Normal`**, retain each unit's truthful QTH, and set **`TimeSlotCode = 7`** and **`TXPause = 480` seconds** on both.
5. Prepare the lower-lane and upper-lane builds in [Section 5.5.2.3](#sec-simultaneous-tx-setup-5-3-1), assigning one unit to each lane. Keep the callsigns attached to their documented physical paths.

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
5. Prepare the lower-lane and upper-lane builds in [Section 5.5.2.3](#sec-simultaneous-tx-setup-5-3-1), assigning one unit to each lane. Keep the complete suffixed callsigns attached to their documented physical paths.

The intended schedule repeats every twenty minutes:

| UTC minute in each hour | Target | Reference |
|---|---|---|
| `04, 24, 44` | Type 2: its complete suffixed callsign and power | Type 2: its complete suffixed callsign and power |
| `06, 26, 46` | Type 3: its hashed identity, grid-6 and power | Type 3: its hashed identity, grid-6 and power |

When this recurrence is maintained, each transmitter uses **6 of 30 WSPR cycles per hour: 20%** of the available cycles. Both phases use the same selected frequency within that sequence. The second message follows a fixed nine-second pause after the first finishes; it does not receive a separate GPS-slot start check. The configured `TXPause` follows the complete pair, not the gap between its two phases.

**Keep the source limitations in view.** The Type 3 hash construction for two-digit suffixes is disabled. The prefix-based Type 3 path also rebuilds its callsign string without writing the terminating zero before hashing, so it is not a reliable recipe in this revision. The single-character-suffix route above uses the implemented construction path; the frequency-lane patch does not repair either unsupported path. <a href="#ref-29">[Ref-29]</a>

Observe corresponding Type 2 and Type 3 phases together, including after a restart. Verify both complete identities in the receiver/database evidence for both phases through [Section 5.4](#sec-simultaneous-tx-setup-4). Matching configuration values alone do not establish correct hash resolution or complete synchronized transmissions.

<a id="sec-simultaneous-tx-setup-5-3-1"></a>
###### 5.5.2.3 Shared timing, frequency lanes and verification

**Keep the schedule and pause consistent.** Both worked routes use code `7`. If you choose a different fixed start, match `TimeSlotCode` on both units and use the following rules:

| `TimeSlotCode` | First-message schedule, when ready |
|---|---|
| `0–4` | Repeats every 10 minutes. Code `0`: `00, 10, 20, 30, 40, 50`; code `1`: `02, 12, 22, 32, 42, 52`; through code `4`: `08, 18, 28, 38, 48, 58`. |
| `5–14` | Repeats every 20 minutes. Code `5`: `00, 20, 40`; code `6`: `02, 22, 42`; code `7`: `04, 24, 44`; through code `14`: `18, 38, 58`. |

`TXPause` is a delay in **seconds after the enabled-band loop**, not a start-to-start period. With one band enabled, it follows each complete one- or two-message sequence. Leave enough time to finish, pause and become ready for the next scheduled start. An eight-minute pause after a two-message sequence can skip the next ten-minute start; the twenty-minute worked schedules leave room for their messages and that pause.

Use the fixed codes above for these recipes. Code `16` allows the next available even-minute start; code `17` responds to a changed location or the top of an hour. Neither establishes the selected fixed recurrence used here. Frequency randomization does not select the time slots, so check both actual starts during preflight. <a href="#ref-29">[Ref-29]</a>

**Patch the frequency placement.** Stock firmware draws an integer offset from **−100 through +99 Hz** around the band's nominal frequency. Two stock units can therefore select nearby positions. Prepare separately labelled source copies for transmitter A and transmitter B, with one assigned to each <strong class="defined-term">frequency lane</strong> — a restricted frequency range.

The offsets below are relative to the **center** of the 200 Hz WSPR transmit sub-band: for example, `7.040100 MHz` on 40 m or `14.097100 MHz` on 20 m. Confirm that both builds use the same correct nominal frequency. In this firmware, `freq` is **tone 0**, the lowest of the four transmitted tone frequencies.

In `DoWSPR()`, find this statement **twice**: after the first `NextFreq()` and after the later band-cycle `NextFreq()`:

```cpp
freq = freq + (100ULL * random (-100, 100));
```

Replace **both occurrences in A's source** with:

```cpp
freq = freq - (100ULL * random(31, 91));
// random lower lane: -90 through -31 Hz
```

Replace **both occurrences in B's source** with:

```cpp
freq = freq + (100ULL * random(30, 90));
// random upper lane: +30 through +89 Hz
```

The upper argument of `random()` is excluded. `freq` uses **0.01 Hz units**, so multiplying an integer draw by `100ULL` converts hertz to those units. The lower-lane edit subtracts a positive amount. Changing only one source occurrence leaves either the first or a later sequence at stock placement. <a href="#ref-29">[Ref-29]</a>

| Commanded quantity | Value |
|---|---:|
| A: lower-lane tone 0 | `−90…−31 Hz` from the center |
| B: upper-lane tone 0 | `+30…+89 Hz` from the center |
| Minimum tone-0 separation | **61 Hz** |
| Four-tone center span in this source | **4.38 Hz**, about **4.4 Hz** |
| Minimum gap between the nearest tone centers | **56.62 Hz**, about **57 Hz** |
| Outer tone-0 margin to the nominal sub-band edge | Lower edge: **10 Hz**; upper edge: **11 Hz** |
| Highest upper-lane tone's margin below the upper edge | **6.62 Hz**, about **6.6 Hz** |

These are commanded tone-center positions. Oscillator error, drift and actual spectral width still require measurement. Confirm that both complete signals remain comfortably inside the transmit sub-band.

Each new sequence draws a lane position again; consecutive draws **can repeat**. When precision `6` adds Type 3, that partner uses the **same selected frequency** as the preceding Type 1 or Type 2 message. The next draw occurs after the next `NextFreq()`; offsets do not accumulate.

**Build and preserve a recovery record.** Before compiling or flashing:

- Check the exact hardware model and revision, factory oscillator calibration, and installed filter configuration. The cited file selects model `1048`; changing a model number alone does not establish compatibility with different relay or filter hardware.
- Follow the pinned source header's build prerequisites: the ESP8266 board package, **Generic ESP8285 module**, **DTR** reset, **57,600** upload speed, the correct serial port, and **NeoGPS by Slash Devin**. Its `NMEAGPS_cfg.h` must enable `NMEAGPS_PARSE_GSV`, `NMEAGPS_PARSE_SATELLITE_INFO` and `NMEAGPS_PARSE_SATELLITES`.
- Keep a recoverable stock image and records of user settings and factory calibration/filter settings. Record the source revision, both lane patches, tool and library versions, build settings, and binary hashes. The source header does not pin every build dependency. <a href="#ref-29">[Ref-29]</a>

**Check on the bench, then on air.** After flashing, test each unit separately into suitable loads or a safely attenuated measurement arrangement; for colocated units, also test both together. Check actual frequency placement, complete message timing, output power, filtering and spectral purity before connecting antennas. For units at separate stations, inspect simultaneous reception during the subsequent common-receiver on-air preflight. Use the same PC-control conditions planned for the run; control commands can interrupt a transmission in this firmware.

Complete [Section 5.4's database preflight](#sec-simultaneous-tx-setup-4) at the intended low on-air power. Confirm that both identities remain in their assigned lanes and produce pairs from common receivers in the intended cycles. Repeat the start and placement checks after a restart.

Varying the position within a lane can reduce dependence on one fixed interfering frequency, but A still always occupies the lower region and B the upper region. For a confirmatory run, **reverse the lane assignments** while keeping the identities attached to their physical paths:

```text
Run 1: A = lower random lane, B = upper random lane
Run 2: A = upper random lane, B = lower random lane
```

An advantage that follows the antenna or transmit path through that reversal is stronger evidence than one that follows the lane. Use [Section 5.6](#sec-simultaneous-tx-setup-6) to document the repeated or crossed setup.



<a id="sec-simultaneous-tx-setup-6"></a>
#### 5.6 Confirm by exchange or crossover

Use the first run to identify a pattern worth confirming. For the next physical run, use a **new UTC window** with comparable duration and time-of-day coverage. Retain the intended band, schedule, powers, filters and primary evaluation scope, and record any unavoidable changes.

| Control | What to change | What it helps distinguish |
|---|---|---|
| **Frequency exchange** | Exchange the lower and upper fixed positions or randomized lanes while retaining the documented physical paths. | An effect following frequency position, such as narrowband interference, receiver passband response or frequency-dependent transmitter behavior. |
| **Hardware crossover, where practical** | Exchange the antennas or tested components between transmitter chains. Record the identity-to-component mapping for every run. | An effect following the tested component versus one following the transmitter chain. |

For a QRP Labs setup already using verified within-run frequency swapping, retain the per-position check and use a separate repetition or hardware crossover for confirmation. For the ZachTek lane recipe, exchange the lane assignments between runs.

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
4. **Choose and record the summary.** Use the ΔSNR summaries in **Benchmark Statistics** for the documented calibration period, filters and scope. Record both statistic and weighting: the **median of station-median ΔSNR** gives each qualifying identity one contribution; a **pooled median or mean of qualifying spot pairs** gives every included pair one contribution. Record station and pair counts and use the same summary definition for validation. WSPRadar does not determine the correction automatically.
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

**Joe Taylor, K1JT, and Bruce Walker, W1BW: a shared experimental resource.** Taylor introduced WSPR in 2008; Walker developed WSPRnet to collect and share reception reports. Their 2010 article showed how those reports could support propagation experiments. One example grouped three weeks of 30 m observations into 15-minute UTC intervals: averaging revealed recurring reception patterns that were difficult to judge from individual transmissions. Station operators supplied the distributed observations, while the protocol, software and reporting service made them accessible. The reports still reflected the participating equipment, locations and operating schedules. <a href="#ref-6">[Ref-6]</a>

> **Use in WSPRadar:** preserve this connection between reported observations and the question being asked. Geographic and time summaries organize the evidence, while the selected period and participating stations remain part of its meaning.

**Nathaniel Frissell and collaborators: amateur observations in space science.** Their 2019 study compared amateur-network reports during the September 2017 solar activity with a quiet-time baseline. It identified HF communication blackouts associated with flares and changes during geomagnetic disturbances, using the baseline to distinguish event responses from ordinary variations. <a href="#ref-13">[Ref-13]</a>

Their 2022 study used WSPRnet, Reverse Beacon Network and PSKReporter observations from 3 November 2017. Approximately 2.5-hour fluctuations in communication distance agreed with SuperDARN radar and satellite-navigation measurements of ionospheric electron content, supporting an interpretation as large-scale traveling ionospheric disturbances. The independent measurements were part of the evidence for that physical explanation. <a href="#ref-14">[Ref-14]</a>

Their 2023 review places these amateur networks alongside purpose-built scientific instruments and recommends cross-calibration between networks. It recognizes the scientific value of accumulated observations without treating every contributing receiver as a calibrated instrument. <a href="#ref-7">[Ref-7]</a>

> **Use in WSPRadar:** examine geographic and temporal structure in context, then use independent observations or a controlled experiment to test a physical explanation. WSPRadar's plots help formulate and inspect such questions; they do not themselves identify an ionospheric cause.


<a id="sec-d-2"></a>
#### 7.2 Making observational WSPR data interpretable

<a id="sec-d-lo"></a>
**Lo and collaborators, 2022: establish activity before interpreting silence.** Their study used a full year of 2017 observations on 7 MHz between Europe and Australasia. Half-hour activity checks asked whether a transmitter was heard elsewhere and whether a receiver heard other stations. Reception from the UK to New Zealand occurred around UK sunrise and sunset; reception in the reverse direction was concentrated around UK sunrise, with UK-sunset reception especially sparse in summer. The authors proposed higher European evening noise as a possible explanation, rather than treating the asymmetry as propagation evidence alone. <a href="#ref-9">[Ref-9]</a>

> **Use in WSPRadar:** apply the activity-check principle when defining Performance opportunities. WSPRadar's own same-cycle rules establish which endpoints have activity evidence; they are a separate design choice from the study's half-hour checks. Missing reports without the required evidence remain unknown outcomes.

**Gwyn Griffiths, G3ZIL, Rob Robinett, AI6VN, and Glenn Elmore, N6GN, 2019–2020: measure noise alongside reception.** Their 2019 report compared noise estimates from gaps between WSPR transmissions with frequency-domain estimates made during reception, and investigated calibration to the receiver's antenna input. At KPH, the 40 m noise record showed a daily minimum around local noon and greater evening/night variability. These measurements added information that ordinary SNR reports could not supply. The work was subsequently published in QEX in September/October 2020. <a href="#ref-15">[Ref-15]</a> <a href="#ref-16">[Ref-16]</a>

> **Use in WSPRadar:** interpret an SNR change as a change in the signal-to-noise relationship. WSPRadar does not independently measure noise; distinguishing stronger signals from lower noise requires additional measurements or controlled station tests.


<a id="sec-d-3"></a>
#### 7.3 Antenna and station-comparison lineage

**Patrick Destrem, F6IRF, 2008: automated switching and geographic comparison.** Destrem alternated a 30 m vertical and inverted-V every ten minutes and corrected reports to a common transmit power. These were <strong class="defined-term">interleaved measurements</strong>: the antennas were tested in alternating periods. He examined individual receivers and distance groups. The vertical's reported average advantage was about 4 dB on one approximately 14 000 km path, while the antennas were approximately equal on a 2 000 km path. The result depended on the path and installation; sequential measurements remained exposed to changing propagation. His follow-ups extended the investigation to reception and comparisons between stations. <a href="#ref-17">[Ref-17]</a>

> **Use in WSPRadar:** credit the early combination of power correction and geographic inspection. Compare directions and distances explicitly, while using concurrent pairs for ΔSNR and retaining one-sided reports as separate evidence.

**Charles Preston, KL7OA, later K7TAA, 2009 and 2017: simultaneous comparison.** Preston's March 2009 preliminary experiment used two colocated 2 W transmitters, a Buddipole and a horizontal loop on 30 m. Common distant receivers supplied simultaneous reports. Overall performance was similar in the short run, but the Buddipole stood inside the loop and antenna interaction limited the conclusion. Either transmission could also be reported alone; weak reception and frequency-specific interference were possible explanations. His report distinguished received SNR from signal strength. He later published *Antenna Comparisons Using Simultaneous WSPR Measurements* in QEX in July/August 2017; the preliminary report's June 2017 update points readers to that publication. <a href="#ref-18">[Ref-18]</a> <a href="#ref-19">[Ref-19]</a>

> **Use in WSPRadar:** compare transmissions observed by the same receiver in the same cycle. Keep paired ΔSNR and one-sided decoding evidence distinct, and document the physical arrangements that bound the comparison.

<a id="sec-d-toledo"></a>
**Sivan Toledo, 2010: a useful negative result about timing.** Toledo compared three loop antennas in successive blocks of approximately one hour. Reports changed substantially while he was still using the same antenna: one path varied by about 10 dB in forty minutes, and another receiver showed similar variability. Apparent differences between antennas were comparable with this background variation, so that experiment could not separate antenna performance from changing conditions. His account discussed automated switching and Preston's simultaneous approach as ways to improve the design. It was a limitation of the experiment, not a finding that WSPR comparisons are impossible. <a href="#ref-3">[Ref-3]</a>

> **Use in WSPRadar:** make the common operating period part of the comparison, inspect changes over time and repeat controlled tests. Collecting more reports does not by itself remove differences between the conditions being compared.

<a id="sec-d-milazzo"></a>
**Carol F. Milazzo, KP4MD, 2011: compare complete stations in both directions.** Published in January 2011 using December 2010 measurements, Milazzo's study compared stations 29 km apart through a common receiver about 1 750 km away. She corrected for transmit-power differences and examined the results alongside VOACAP estimates. On 40 m, the horizontal-loop station generally produced stronger transmitted reports, while the vertical-antenna station received the common distant station with better SNR. Different sites, radios and band schedules remained part of the comparison, and the selected distant station limited its geographic scope. <a href="#ref-4">[Ref-4]</a>

> **Use in WSPRadar:** analyze TX and RX separately, make the power basis explicit and check common activity. A stronger transmitted report does not establish better reception; interpret each result as evidence about the complete installations and paths tested.
>
> **Explore in WSPRadar:** the [Milazzo historical replay](https://wspradar.org/en/demos/milazzo_tx_buddy/) revisits Figures 6 and 7 in RX and TX. It shows how exact cycle/locator matching and reported-power normalization can leave very few usable pairs despite larger report totals, and why unverified schedules limit comparisons of those totals. The prepared profile starts in RX; the guide also provides the TX configuration.

<a id="sec-d-griffiths-squibb"></a>
**Gwyn Griffiths, G3ZIL, and Nigel Squibb, G4HZX, 2017: compare, investigate and retest.** In *Improving HF Band SNR*, they paired reception of the same transmitter at the same time and examined differences against time, distance, soil moisture and station changes. After three ground radials were added at G4HZX, the earlier moisture association was absent in the following test window. Replacing and relocating a nearby computer also coincided with an approximately 5 dB SNR improvement. The precise noise mechanism was unresolved, and both observations concerned complete receiving installations. The recorded changes made the comparisons useful for diagnosis without proving a universal antenna effect. <a href="#ref-5">[Ref-5]</a>

> **Use in WSPRadar:** use paired receiver comparisons and temporal or distance views alongside an operator's station log. Treat a pattern as a reason for a targeted intervention and repeat measurement, with causal claims proportional to the controls.
>
> **Explore in WSPRadar:** three prepared configurations revisit these historical reports:
>
> - [**Figure 3: RX Benchmark**](https://wspradar.org/en/demos/griffiths_squibb_fig3/) follows the April 2017 G3ZIL/G4HZX comparison through maps, time summaries and individual paths. It shows how a paired-SNR advantage and additional decodes complement one another, while varying with direction and time.
> - **Figure 6: UTC-hour comparison** narrows the same receivers to 5–7 April. Its separate configuration shows an early-hour vertical advantage changing to a daytime/evening dipole advantage; comparing folded and chronological views tests how consistently the pattern appears. The Figure 3 guide also explains this reconstruction.
> - [**RX Performance**](https://wspradar.org/en/demos/griffiths_squibb_rx_performance/) examines G3ZIL alone. Follow HB0QRP to distinguish at-least-once reach, Decode Rate within confirmed opportunities, and SNR among successful decodes. This is WSPRadar's additional analysis of the historical reports, without a Reference receiver.

<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels and Lamy, 2022: characterize the receiving chains.** Their 160 m experiment first connected two receiving chains to one antenna. Two seven-day calibration periods each produced a mean offset of about 1.2 dB, which they applied before comparing antennas simultaneously. With identical antennas placed at orthogonal orientations, they observed an SNR difference of approximately 3 dB in that installation. Polarization and ionospheric effects were discussed as possible explanations; the orientation result did not establish one physical cause. The calibration also made an equipment contribution visible before interpreting the antenna comparison. <a href="#ref-2">[Ref-2]</a>

> **Use in WSPRadar:** allow an independently measured receiving-chain offset to be expressed through the signed Reference correction, with its measurement procedure documented. Keep the corrected SNR comparison separate from claims about the antenna or polarization mechanism that produced it.
>
> **Explore in WSPRadar:** two prepared comparisons separate calibration from the subsequent antenna experiment:
>
> - [**Receiver calibration**](https://wspradar.org/en/demos/vanhamel_rx_calibration/) leaves the shared-antenna receiving-chain offset visible, with no correction applied. It shows why the mean, spot-pair median and station-balanced median can differ, and why a correction needs a documented measurement basis.
> - [**Antenna rotation**](https://wspradar.org/en/demos/vanhamel_rx_buddy/) follows M7AEO while the Reference dipole turns 90° and the Target long wire stays fixed. The approximately 3 dB step favors the fixed long wire relative to the dipole. It shows why one path's chronological evidence can reveal a transition hidden by its whole-period median. The guide documents the separate calibration estimate used in this configuration.

<a id="sec-d-zander"></a>
**Jens Zander, 2022: state the comparison model and its assumptions.** Zander's preprint models two local antennas transmitting simultaneously to common remote receivers. A same-receiver SNR difference cancels shared path loss and receiver noise under the model's assumptions; cross-calibration between those distant receivers is unnecessary for each within-receiver difference. His preliminary paired measurements had a sample standard deviation around 3 dB. The analysis considers interference, failed decodes, quantization and the precision gained by averaging, as well as directivity, geographic sampling and unknown elevation angles. Equal or corrected powers and differences between transmitting chains still matter. <a href="#ref-1">[Ref-1]</a>

> **Use in WSPRadar:** make same-cycle differencing and the reported-power basis explicit. WSPRadar defines its own qualification and aggregation rules; the preprint's uncertainty model is not automatically their uncertainty model, and observed ΔSNR does not directly measure absolute antenna efficiency.
>
> **Explore in WSPRadar:** [Zander's TX comparison](https://wspradar.org/en/demos/zander_tx_buddy/) revisits Experiment A / Figure 4, comparing a short portable vertical with the larger Hy-Gain AV620. It shows why station-balanced and pooled spot-pair summaries differ, how the result varies by direction, and why unequal reporting spans must be checked before interpreting decode totals. The short prepared window supports this experiment's observed comparison, not a daily pattern or a universal portable-antenna penalty.

**Thomas Rietdorf, DL2OAH, 2026: a synchronized multiband station comparison.** His DARC presentation of 17 January 2026 reports measurements from 12–21 January 2025. Synchronized transceivers compared a horizontal OCF/IC-7610 installation with a vertical/FT-991A installation in separate RX and TX runs on 40, 20, 15 and 10 m. Matched two-minute reports supported comparisons by time and direction, alongside one-sided reports. The presentation reports a 2.5–7 dB SNR advantage for the horizontal installation, depending on band, while maximum distances were approximately equal. Different radios and the distribution of remote stations limit attribution to the antennas alone. <a href="#ref-20">[Ref-20]</a>

> **Use in WSPRadar:** combine synchronized comparisons with several views of the evidence. Read paired SNR, one-sided decodes and geographic or temporal patterns together, retaining the complete-installation interpretation and the actual measurement dates.


<a id="sec-d-4"></a>
#### 7.4 Analysis infrastructure and related tools

**Gwyn Griffiths and Rob Robinett, 2020: reusable database analysis.** Their WSPRdaemon TimescaleDB and Grafana work joined reports from the same transmitter, time and band, then displayed SNR differences with medians, quartiles, time, distance and azimuth. One example separated nighttime differences westward toward North America from daytime differences involving nearer stations. Noise measurements and exports gave operators further ways to investigate these patterns. The contribution included both the comparison method and a reusable route from stored observations to interpretable displays. <a href="#ref-21">[Ref-21]</a>

> **Use in WSPRadar:** continue that practice of inspecting common-signal differences in time and geography, with a route back to the contributing observations. WSPRadar's own grouping and weighting rules are specified in [Chapter 8](#sec-7).

**Arne and the wspr.live project, with computing resources from HB9VQQ.** Arne's ClickHouse database work provides public queries over historical and recent WSPR reports; dashboards and exports make those records usable by operators and other applications. The official service documentation credits **HB9VQQ for computing resources**. Phil VK7JJ's documentation also explicitly credits Arne's database contribution. <a href="#ref-10">[Ref-10]</a> <a href="#ref-22">[Ref-22]</a>

**Rob Robinett, AI6VN, and the WSPRdaemon community.** Reception, multireceiver acquisition, reporting, database hosting and continued volunteer operation sustain these services. WSPRdaemon's documentation credits Arne's database development and the hosting collaboration. Its earlier TimescaleDB work and later ClickHouse services are distinct contributions. <a href="#ref-11">[Ref-11]</a>

> **Use in WSPRadar:** **wspr.live is the primary database, with WSPRdaemon's WD2 and WD1 as alternatives**. Each run uses one source. The developers, station operators, computing-resource providers and volunteer maintainers make this analysis possible; service availability and the quality of uploaded records remain part of the evidence context.
>
> **Our sincere thanks to everyone who sustains these services and contributes reports, computing resources and volunteer time.** Your work gives the amateur-radio community a shared foundation for learning, experimentation and better station design.

Other tools make complementary parts of experimentation accessible:

| Contributor or project | Practical contribution and relationship |
|---|---|
| **Phil, VK7JJ — WSPR.Rocks** | Interactive queries, maps, charts, duplicate and passband inspection, plus Head2Head comparisons of receivers, transmitters or software versions. SpotQ supplies a heuristic ranking using distance, reported power and SNR. These are useful ways to explore reports; their metrics have their own definitions. <a href="#ref-22">[Ref-22]</a> |
| **Richard Newstead and SOTABEAMS — WSPRlite/DXplorer** | Standalone low-power beacons and accessible comparisons, including the DX10 range indicator. In Newstead's 2017 indoor/outdoor test, two loops transmitted simultaneously at 200 mW; 133 same-receiver, same-time pairs gave an average indoor disadvantage of 6.8 dB. <blockquote><strong>Use in WSPRadar:</strong> credit the practical paired-test design, while treating the value as a result for that installation and operating period.</blockquote> <a href="#ref-23">[Ref-23]</a> <a href="#ref-24">[Ref-24]</a> |
| **Walter Machiels, ON4AWM — WSPR-Station-Compare** | An RX-comparison workflow with measured receiver-offset correction, observation thresholds, callsign filtering and azimuth selection. It makes controlled-comparison choices available in operator software. <a href="#ref-25">[Ref-25]</a> |
| **Fred, W6BSD — Antenna Performance Analysis** | Reports organizing where and when transmitted WSPR signals were received, across times and frequency bands. This makes an installation's observed coverage accessible without writing a custom analysis. <a href="#ref-26">[Ref-26]</a> |
| **Colin Murray, GM4EAU — WATT** | An editable Excel/VBA workflow for queries, filters, calculations, charts and map replay through successive time intervals, helping operators inspect changing propagation patterns. <a href="#ref-27">[Ref-27]</a> |

These tools overlap in purpose, but their filters, comparison units and summaries differ. Check the quantity behind a figure before comparing its value with a WSPRadar result.


<a id="sec-d-5"></a>
#### 7.5 What WSPRadar inherits, integrates and adds

WSPRadar brings these experimental lessons into a documented RX and TX workflow. Its deliberate choices are:

* **Define the comparison.** Controlled Benchmark compares a Target with one Reference Setup/Station under independently known common operation. Historical replay retains its explicitly unverified operating conditions.
* **Keep complementary evidence visible.** Same-cycle pairs support ΔSNR; paired and one-sided Decode Outcomes support the decode comparison. A path rarely heard on one side may be poorly represented by paired SNR alone.
* **Expose adjustments.** Reported-power normalization and optional signed Reference correction make the numerical basis inspectable.
* **Define opportunities.** Performance counts successful decodes within confirmed opportunities, using its explicit endpoint-activity rules for misses.
* **Distinguish weighting.** Station-balanced summaries and summaries of individual observations answer different questions about the same evidence.
* **Make results traceable.** Map, station and individual-observation views, saved settings and exports connect a conclusion to the data and choices behind it.

These definitions determine which observations qualify, how they are counted and how they influence a summary. They support reproducible comparisons conditional on the available reports and operating conditions; they do not directly establish unconditional reception probability or calibrated antenna efficiency. [Chapter 8](#sec-7) specifies the calculations, and [Chapter 9](#sec-8) explains how to report supported claims.


<a id="sec-7"></a>
### 8. Scientific Methods

**Benchmark** compares Target and Reference for the same remote station identities and WSPR cycles. It retains paired and one-sided decode outcomes; a usable SNR observation on both sides also supplies paired ΔSNR. **Performance** measures the Target's success within confirmed opportunities, without a Reference.

Follow three questions through the calculation:

| Question | What the method must establish |
|---|---|
| **What counts once?** | An exact remote identity and cycle, after the applicable matching and consolidation rules. Multiple reports do not automatically become multiple observations. |
| **Which evidence qualifies?** | The observations admitted by the selected analysis and filters, and the station or segment support required for the particular metric. Missing activity and insufficient support are different from a measured zero. |
| **What receives equal weight?** | Depending on the summary, one station, one spot pair, one confirmed opportunity or one station's contribution within a time interval. More reports do not always mean more weight. |

A database spot is a reported decode. Spot pairs and confirmed opportunities are constructed from reports under the rules below; medians, rates and other summaries describe those retained units.

Read the shared foundations in [Section 8.1](#sec-7-foundations), then [Benchmark](#sec-7-benchmark) or [Performance](#sec-7-performance). [Section 8.4](#sec-7-views) explains geographic and temporal summaries, [Section 8.5](#sec-7-claims) the strength of conclusions, and [Section 8.6](#sec-7-outliers) the optional event detector. A calculation can be correct for the retained evidence while its physical explanation remains uncertain; [Chapter 9](#sec-8) gives reporting guidance.


<a id="sec-7-foundations"></a>
#### 8.1 Shared evidence foundations

<a id="sec-7-spots-identities-cycles"></a>
<a id="sec-7-1"></a>
<a id="sec-7-2"></a>
##### 8.1.1 Spots, identities and cycles

Each completed run uses one WSPR database; it does not combine records from different sources. Record that source with the result, because the reports come from different transmitters, receivers, decoders and reporting systems.

A **spot** is a reported successful decode. A **WSPR cycle** is the two-minute interval beginning at an even UTC minute. WSPRadar's basic observation concerns one exact remote station identity in one eligible cycle on the selected band: a remote transmitter in RX, or a remote receiver in TX. Multiple qualifying reports are consolidated into one observation for each side, identity and cycle before outcomes are counted; [Section 8.1.2](#sec-7-normalization-consolidation) explains the selection rule.

A **spot pair** requires usable Target and Reference evidence for the same remote identity in the same cycle. RX compares two receivers observing the same transmitter; TX compares two transmitters observed by the same receiver. Reports from different cycles are never paired. Matching neither requires identical RF frequencies nor establishes identical physical propagation paths; simultaneous TX signals normally need clear separated frequencies.

**Identity depends on the station's role:**

| Role | Database identity |
|---|---|
| **Target** | Exact receiving callsign in RX, or transmitting callsign in TX, plus Target QTH's first four locator characters. |
| **Reference Setup/Station** | Exact Reference callsign plus its four-character locator, discovered from reports or independently supplied. |
| **Remote station** | Exact callsign plus the **full reported locator**: the transmitter in RX, or receiver in TX. |

Even with a six-character Target QTH, the first four characters select Target reports; the full configured locator anchors distance, azimuth and solar calculations. The same remote callsign at two full locators remains two identities, including when both are within one grid-4. Matching grid-4 values do not prove physical co-location.

Target and Reference require distinct exact callsigns; a base callsign and a suffixed callsign remain distinct. Each retained report must supply the identity fields required for matching: WSPRadar does not reconstruct compound callsigns from hashes or borrow a missing locator from a neighboring cycle. Incorrect or changing locators can split a physical station, move its mapped position or trigger moving-station exclusion.

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

**Successful SNR uses a common reported-power basis in both RX and TX, for Performance and Benchmark.** WSPR reports SNR in dB relative to a **2 500 Hz reference bandwidth**, and transmit power in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar adjusts successful SNR to **30 dBm (1 W)**:

$$SNR_{\mathrm{norm}}=SNR_{\mathrm{reported}}-P_{\mathrm{reported}}+30$$

The SNR terms are in dB; the power values are in dBm. For example, reported SNR of **−15 dB** at **20 dBm** becomes **−5 dB** at the 30 dBm comparison level: the 10 dB reported-power shortfall is added back.

This removes the **reported power difference** from the comparison. It does not recreate the decodes that would have occurred at 1 W, or correct antenna gain, radiation efficiency, feedline loss, EIRP, receiver calibration or local noise. Decode Outcomes and Performance opportunities remain those actually observed.

**Several reports still count as one observation for each side, remote identity and cycle.** WSPRadar retains the strongest qualifying normalized SNR for Performance and for each side of Benchmark. Consolidation never combines successive cycles.

This <strong class="defined-term">strongest-report rule</strong> is a best-observed policy: it describes the strongest reported reception, rather than a central value across the available reports. Weaker duplicate-like reports, secondary decodes or unwanted signal replicas cannot lower the retained maximum. Conversely, an erroneous high report can become the retained value, and a setup with more contributing receivers or reports has more chances to supply a high value. WsprDaemon also documents retaining the best SNR when merging receivers for WSPRnet <a href="#ref-11">[Ref-11]</a>.

That precedent does not establish that the maximum is the intended signal, or that both setups selected the same spectral component. Means and medians would describe different features of the available reports; none of these statistics identifies the intended component by itself. Later medians summarize the retained values and cannot undo this earlier selection.

**The Benchmark decoding-reach plots use a different SNR basis.** <strong class="defined-term">From Signal Quality to Decoding Reach</strong> retains each setup's strongest **original reported SNR** for each remote identity and cycle. It applies neither 30 dBm normalization nor Reference correction. Its curves count observed spots and stations at raw-SNR cutoffs; they do not replace normalized paired ΔSNR. See [RX Benchmark](#sec-3-rx-benchmark) and [TX Benchmark](#sec-3-tx-benchmark) for their place in the comparison.


<a id="sec-7-activity-eligibility"></a>
<a id="sec-7-3"></a>
##### 8.1.3 Operating conditions and eligibility

**Controlled Benchmark relies on independently known common operation.** In RX, both receivers must have listened on the selected band with functioning reporting throughout the comparison period. In simultaneous TX, both transmitters must have transmitted in the same WSPR cycles. The operator's declaration records this experimental prerequisite; successful database reports cannot independently verify it.

**Historical replay has a different interpretation.** It acknowledges that common operation is unverified rather than asserting a controlled experiment. The same observed-outcome and paired-ΔSNR calculations apply, but one-sided counts may also reflect schedules, outages or reporting interruptions. See [the acknowledgement controls](#sec-5-3) and [historical and retired designs](#sec-7-neighborhood).

Benchmark retains eligible observations from either exact setup under the same peer-cycle consolidation and population filters. A missing Target decode does not exclude Reference-only evidence, even if Target has no reports anywhere in that cycle or throughout the entire period. The converse applies to Target-only evidence. If neither side has a report, there is no observed outcome; WSPRadar adds no synthetic “both missed” row.

**Performance uses** <strong class="defined-term">Target-active conditioning</strong>**:** a cycle needs evidence that Target was operating on the selected band.

| Direction | What establishes Target activity in that cycle? |
|---|---|
| **RX** | The Target receiver uploaded at least one qualifying decode. |
| **TX** | At least one qualifying report of a Target transmission exists somewhere. |

Activity is established before geographic filtering. Its witness can lie outside the scientific distance limit or the area currently being inspected. A Target report involving a peer later removed by the special-callsign or moving-station exclusion can also establish activity. This does not restore an excluded peer to the retained population or add an out-of-scope outcome to a selected scope; artifact scopes remain as described in [Section 9.4](#sec-8-4).

A cycle without an activity witness is excluded. WSPRadar cannot distinguish downtime from operation that produced no reported decode, so Performance describes observable Target-active cycles rather than all elapsed time or planned transmissions.

Target activity alone does not turn every silent remote station into a miss. The particular remote endpoint also needs the activity evidence defined in [Section 8.3.1](#sec-7-performance-opportunities).


<a id="sec-7-benchmark"></a>
#### 8.2 Benchmark: differences and shared evidence

Benchmark describes two aspects of the same comparison: **the SNR difference when both setups produced a usable report**, and **the decoding outcomes across all retained observations**. The first needs a spot pair; the second also includes reports from only one side. Keep these populations distinct when interpreting a result.


<a id="sec-7-benchmark-outcomes"></a>
<a id="sec-7-6"></a>
##### 8.2.1 Decode Outcomes and missing observations

**First classify each remote station and WSPR cycle.** After consolidation and filtering, there are three outcomes:

| Outcome | Evidence in that station-cycle |
|---|---|
| <strong class="defined-term">Only Target</strong> | A Target-side report, without a Reference-side report. |
| <strong class="defined-term">Paired</strong> | Reports from both sides for the same remote identity and cycle. Usable SNR on both sides supplies ΔSNR. |
| <strong class="defined-term">Only Reference</strong> | A Reference-side report, without a Target-side report. |

These are <strong class="defined-term">native</strong> outcomes: matched, consolidated and scientifically filtered observations at the original WSPR-cycle level, before display aggregation.

There is no fourth, both-missed outcome: if neither side reported the station, the database supplies no observed event. Benchmark retains one-sided evidence symmetrically, without a separate Target-activity witness. A spot pair still exists when its station has too few pairs to qualify for displayed ΔSNR summaries.

**Then classify each station over the filtered comparison period.** A station can have different native outcomes in different cycles. The ΔSNR map summarizes that history in five mutually exclusive station classes:

| Station class | Meaning over the comparison period |
|---|---|
| <strong class="defined-term">Paired (qualifying)</strong> | At least the configured minimum number of spot pairs; shown in strong green. |
| <strong class="defined-term">Paired (not qualifying)</strong> | At least one pair, but fewer than the minimum; shown in pale green. |
| <strong class="defined-term">Both observed, no pairs</strong> | Each setup observed the station, but always in different cycles. |
| **Only Target** | All retained observations of this station are Target-only. |
| **Only Reference** | All retained observations of this station are Reference-only. |

These station classes do not relabel the underlying observations. A qualifying paired station can also supply Target-only and Reference-only events. **Both observed, no pairs** is a station class, never a fourth spot outcome. The ΔDecode map combines the two Paired station classes into one green category; all five original classes remain part of the observed population.

The Statistics subheaders identify the relevant support: stations and receiver decodes for ΔDecode, qualifying spot pairs for its ΔSNR histogram, and qualifying stations for the station-median histogram. Drill-Down retains the three native outcomes. Temporal coverage separately counts stations and station-cycle events as explained in [Section 8.2.4](#sec-7-benchmark-coverage).

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

After the run's population, UTC, solar-state and geographic filters, each exact remote callsign-plus-full-locator identity must meet **Minimum spot pairs per station for ΔSNR**. Qualification is calculated over the full filtered comparison period, not again within each time bin, station selection or zoom. Qualifying stations supply the ΔSNR map, histograms, temporal summaries and outlier analysis.

Below-threshold pairs and all one-sided observations remain in coverage, Station Insights, Drill-Down and exports. There is no separate minimum for a station's one-sided count. For example, at a minimum of five pairs, `100 Paired / 8 Only Target / 4 Only Reference` qualifies, while `4 / 100 / 100` does not. The observed counts stay unchanged in both cases. Changing ΔSNR qualification does not change ΔDecode or Station Reach Advantage.

**How the ΔSNR map balances stations**

1. Calculate each qualifying station's **median ΔSNR** from all its retained spot pairs.
2. Calculate the segment's **median of those station medians**, giving each station one contribution.
3. Color the segment only if it meets **Minimum qualifying stations per segment for ΔSNR**.

A median is the middle ordered value, or the average of the two middle values for an even count. The first median describes the typical retained difference on one station path; the second describes the typical qualifying station in that segment. Equal station weighting prevents a prolific reporter from dominating solely through its observation count.

The <strong class="defined-term">spot-pair median</strong> instead pools all pairs from qualifying stations and gives each pair equal weight. Using the default one-pair station minimum, these summaries can disagree:

| Qualifying station | ΔSNR values (dB) | Station median |
|---|---|---:|
| A | +6, +6, +6, +6, +6, +6 | +6 dB |
| B | −2, −2 | −2 dB |
| C | −1, −1 | −1 dB |

The **median of station medians is −1 dB**, while the **pooled spot-pair median is +6 dB**. The mean of the three station medians is **+1 dB**; the pooled pair mean is **+3 dB**. Every calculation is correct, but each gives different weight to stations or extreme values. The station histogram shows the station medians and labels both their median and mean. This three-station segment can be colored only when the segment minimum is three or fewer; it would not meet the default of five.

The defaults are **one pair per station** and **five qualifying stations per segment**, with allowed ranges of **1–50** and **1–10**, respectively. A callsign at `JO31AA` and the same callsign at `JO31AB` count separately if both qualify. Their medians of `+2` and `+4 dB` yield `+3 dB` and support count **2**. These are reported identities, not proven independent physical sites.

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

All retained stations in the active Inspector scope contribute, without another qualification gate. Separate **Exclusive** endpoint bars contain decodes from stations observed exclusively on one side. They do not contain all one-sided events from shared stations. The two ΔSNR histograms retain their separate pair and station qualification rules.

**When a ΔDecode segment has enough evidence to be colored**

The default minimum is **1% of the full filtered run's observed events**, adjustable from **0% to 5%** in **0.5%** steps. A segment must contain at least:

$$N_{\min}=\left\lceil\frac{p}{100}\,E_{\mathrm{run}}\right\rceil$$

Here `p` is the selected percentage, `E_run` counts each retained station-cycle event once, and `ceil` means round upward to a whole event count. The run total is fixed before segment qualification. Map cropping, Inspector selection and below-threshold colors do not change it. At **0%**, every nonempty segment qualifies. No paired observations or minimum station count are required. This gate limits sparse coloring relative to the run; it is not a confidence level or a guarantee of diverse paths.

Both maps retain observed station markers. An observed segment below its metric's requirement is **gray hatched**; an empty segment is unfilled; zero ΔSNR and **1× ΔDecode** are valid results. ΔSNR and ΔDecode qualification are independent. Their color scales and the ΔDecode ratio legend are explained in [Section 8.4.6](#sec-7-view-spread).

**Interpret the two maps together.** ΔSNR describes paired signal quality; ΔDecode describes the balance of total observed decodes. They can favor different setups. Equal decode totals can combine mostly paired events or substantial one-sided evidence that cancels. Events missed by both are absent, so ΔDecode is not an unconditional decoding probability or a Target win rate. Common-operation evidence, actual power, schedules and the observed station population remain essential context.


<a id="sec-7-benchmark-coverage"></a>
<a id="sec-7-8-2"></a>
##### 8.2.4 Temporal decode coverage

**<strong class="defined-term">ΔDecode Temporal Coverage</strong> separates station reach from decode volume.** Both rows use all retained outcomes, independently of ΔSNR qualification.

| Row | What the bars count within each bin | What the line compares |
|---|---|---|
| <strong class="defined-term">Station-level</strong> | Each exact remote identity once: **Both observed**, **Only Target** or **Only Reference**. | <strong class="defined-term">Station Reach Advantage</strong>, from the distinct-station totals for the two setups. |
| <strong class="defined-term">Spot-level</strong> | Each native station-cycle event once: **Paired**, **Only Target** or **Only Reference**. | **ΔDecode**, from pooled decode totals. |

**Both observed need not mean Paired.** A station seen by Target in one cycle and Reference in another belongs to Both observed within that bin, while its two events remain one-sided. Paired always requires the same station and cycle. In RX the remote identities are transmitters; in TX they are receivers.

For station coverage, let `C` count Both observed stations, `T_s` Only Target stations and `R_s` Only Reference stations. Target's station total is `A_s = C + T_s`; Reference's is `B_s = C + R_s`:

$$r_{\mathrm{stations}}=\frac{A_s}{B_s}$$

The upper bar total is the station union `C + T_s + R_s`. Repeated decodes cannot increase it. An additional station means additional relative to the other setup in that bin, not a first-ever contact or a cumulative discovery. Equal station totals need not mean identical station sets.

The lower row compares `(J + T) / (J + R)`, as defined in [Section 8.2.3](#sec-7-benchmark-aggregation). All paired events use one green category, regardless of ΔSNR qualification. Duplicate reports already consolidated into one station-cycle do not add counts.

**Both secondary axes use signed ratio labels.** Above the central **1×** favors Target; below it favors Reference. In the upper row **2×** means twice as many stations; in the lower row it means twice as many decodes. Read the factor on the favored setup's side; these are not linear ratio axes. Exclusive observations have an explicit endpoint; bins with no support remain gaps. Selected-station coverage uses that station's pooled ΔDecode, not Station Reach Advantage.

<strong class="defined-term">Chronological views</strong> preserve time order. UTC-hour views combine dates under [Section 8.4.4](#sec-7-view-folding), where station membership is assessed separately for each date and hour. The historical **Joint Evidence Share**, `J / (J + T + R)`, measures paired overlap and is no longer the temporal line. Neither current line verifies uptime, counts events missed by both, or establishes a causal antenna advantage.


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

Performance asks where and how consistently the Target succeeded when a reception opportunity could be established. A Target success confirms its own opportunity. Without that success, a miss requires evidence that both the Target and the relevant remote station were operating on the same band in the same cycle. A quiet cycle alone is insufficient.


<a id="sec-7-performance-opportunities"></a>
##### 8.3.1 What counts as an opportunity?

Each opportunity concerns one exact remote station identity and one WSPR cycle on the selected band, after the applicable population and geographic filters. Target activity follows [Section 8.1.3](#sec-7-activity-eligibility). The remote endpoint depends on direction:

- **RX:** the remote transmitter is decoded by the Target or another eligible receiver. If the Target did not decode it, another receiver's report supports a miss only when the Target also decoded another transmitter on that band in that cycle.
- **TX:** the remote receiver decodes the Target or another qualifying transmitter. If it did not decode the Target, its report of another transmitter supports a miss only when a qualifying report of the Target establishes Target transmission in that same band and cycle.

A Target-side success means reception **by the Target** in RX, or reception **of the Target at this receiver** in TX. With Target activity established, classify the identity-cycle once:

| Target-side success? | External evidence confirms remote activity? | Outcome | Count as an opportunity? |
|---|---|---|---|
| Yes | No | Success confirmed by the Target-side decode itself. | **Yes — once.** |
| Yes | Yes | Success also supported by external evidence. | **Yes — once.** |
| No | Yes | Confirmed miss: both endpoints were active, but no Target-side success was reported. | **Yes — once.** |
| No | No | Unknown: remote activity was not established. | **No.** |

Successes without external confirmation remain identifiable as a subset of successes; they are not added again. External confirmation of a success likewise creates no second opportunity. In TX, a report from a different receiver cannot establish that this particular remote receiver was listening. In RX, another receiver can confirm the transmitter's activity, but cannot replace evidence of the Target receiver's activity. Unknown cases stay excluded and receive no invented SNR.


<a id="sec-7-performance-rates"></a>
##### 8.3.2 Decode Rates and weighting

For a qualifying remote identity $i$, let $S_i$ be successful opportunities, $M_i$ confirmed misses, and $O_i=S_i+M_i$ all confirmed opportunities. Its Decode Rate is:

$$p_i=100\times\frac{S_i}{O_i}$$

Here $p_i$ is a percentage. The identity qualifies only when $O_i$ meets the configured **Minimum confirmed opportunities per station**. If $N$ identities qualify, WSPRadar summarizes the same $N$ identities in two ways:

| Summary | Calculation | What receives equal weight? |
|---|---|---|
| **Station-balanced Decode Rate** | $\frac{1}{N}\sum_{i=1}^{N}p_i$ | Each qualifying identity contributes one rate. |
| **Opportunity-level Decode Rate** | $100\times\frac{\sum_{i=1}^{N}S_i}{\sum_{i=1}^{N}O_i}$ | Each confirmed opportunity contributes once to the pooled totals. |

The station-balanced rate asks how consistently the Target succeeded across stations, giving each identity equal weight. The opportunity-level rate asks what fraction of all their confirmed opportunities succeeded. An empty qualifying population has no rate.

**Example.** Two qualifying stations have **90 successes out of 100 opportunities** and **5 out of 10**. Their rates are 90% and 50%, so the station-balanced rate is **70%**. Pooling gives **95 / 110 = 86.4%**: 95 successes and 15 misses, each counted once. The pooled rate is higher because the more successful station supplied more opportunities. The two values answer different weighting questions.


<a id="sec-7-performance-reach"></a>
##### 8.3.3 At-least-once Peer Reach

**At-least-once Peer Reach** measures breadth. Let $N$ be the number of qualifying remote identities and $H$ the number of those identities with at least one Target success:

$$\text{Reach (\%)}=100\times\frac{H}{N}$$

An identity with one success and one with many successes each contribute one to $H$. Both stations in the preceding example succeeded, so their Reach is **100%**, despite different Decode Rates. There is no Reach percentage when no identities qualify.

Adding observations cannot undo an earlier success for a fixed population. The qualifying population can change between runs, however, so reported Reach need not increase when the measurement window becomes longer.


<a id="sec-7-performance-snr"></a>
##### 8.3.4 Successful Target SNR

Successful Target SNR describes retained successful decodes after power normalization and strongest-report consolidation. Misses have no measured Target SNR. Adding marginal decodes can lower a successful-SNR summary even when reception and reach improve, so read SNR alongside Decode Rate and counts.

The temporal overview compares each path with its own usual successful level; selected-station evidence shows its normalized SNR values. [Sections 8.4.3](#sec-7-view-time) and [8.4.5](#sec-7-view-station) define those different summaries. Performance describes conditional behavior within the observed network, rather than unconditional receiver sensitivity, success over every attempted transmission or absolute station efficiency.


<a id="sec-7-views"></a>
<a id="sec-7-8"></a>
#### 8.4 Scope and summaries across space and time

The same evidence can answer different questions depending on what receives equal weight. A map usually compares stations; a Spot-pair distribution compares observations; a folded hourly view can combine several dates. The following rules define those distinctions.

<a id="sec-7-view-scope"></a>
<a id="sec-7-9"></a>
##### 8.4.1 Scope, geography and filters

Distance and azimuth use the configured Target QTH and reported peer locators on a spherical Earth of radius **6 371 km**. The azimuthal equidistant map is centered on Target QTH, with distance boundaries at **2 500**, **5 000**, **10 000**, **15 000**, **20 000** and **22 000 km**, and **22.5-degree** direction sectors. Locators describe grid cells, not measured antenna positions; these calculations are not survey-grade positioning or take-off-angle measurements.

**Maximum peer distance from Target** excludes stations **at or beyond** the chosen limit before scientific aggregation and processed-evidence export. Inspector selections narrow the displayed or summarized scope **within the retained population**; they neither discard completed-run evidence nor restore excluded stations.

For Performance, Target activity is established globally before geographic filtering. Moving-station exclusion likewise identifies changing-location callsigns in the otherwise eligible global population before applying the distance limit.

Solar classification uses solar elevation at **Target QTH at the WSPR-cycle timestamp**. It describes conditions at the Target, not illumination along the complete radio path or at every remote endpoint. [Section 11.6](#sec-6-6) explains database retrieval limits and source-population controls.


<a id="sec-7-view-geography"></a>
<a id="sec-7-8-1"></a>
##### 8.4.2 Geographic summaries

**Benchmark** segment evidence counts include all observed identities in the active geographic scope; ΔSNR summaries use only qualifying identities. Sorting or filtering the station table, or selecting a row, does not redefine that segment population. The ΔSNR map uses the median of qualifying station medians; the ΔDecode map uses pooled total-decode advantage. [Section 8.2.3](#sec-7-benchmark-aggregation) defines both, including the separate Spot-pair distribution.

**Performance distance profiles** group stations by their calculated distance from Target QTH. Bin width follows the configured maximum peer distance:

| Maximum peer distance | Distance-bin width |
|---|---|
| 2 500 km | 250 km |
| 5 000 km | 500 km |
| 10 000 km | 1 000 km |
| 15 000 km | 1 500 km |
| 20 000 or 22 000 km | 2 500 km |

Changing the Inspector's selected distance range retains that width. Bin edges are anchored at integer multiples from **0 km**, with the last bin shortened where necessary to end at the configured maximum. The final selected upper boundary is included **among already-retained peers**; this does not override the scientific maximum-distance exclusion. Gaps between disjoint selected ranges remain gaps, not zero-evidence bins.

Each distance bin reports at-least-once Reach, both Decode Rate weightings and successful Target SNR. For SNR, first take each contributing station's median successful value, then the median of those station medians. Stations with only Misses contribute no synthetic SNR.

An <strong class="defined-term">interquartile range (IQR)</strong> is the difference between the upper and lower quartiles, Q3 and Q1. The plotted **Q1–Q3 interval** spans the middle half of the contributing station medians. It is shown with **five or more** medians. With **two**, a <strong class="defined-term">min–max interval</strong> spans the two values; with **one, three or four**, the median is shown without a spread interval.


<a id="sec-7-view-time"></a>
<a id="sec-7-8-3"></a>
##### 8.4.3 Chronological evidence

**Chronological views preserve the sequence of the run.** Bins start at the selected UTC start and use the chosen width; the final bin can be shorter. Empty intervals remain missing evidence, not invented **0 dB** or **0%** observations. The usual offered widths and defaults depend on the complete run duration, not the span of observed reports. A valid saved choice can remain available outside those usual choices; see [Section 10.5](#sec-5-5).

**Benchmark ΔSNR** pools retained spot pairs from qualifying stations within each bin and shows their median and distribution. Frequently observed paths can therefore contribute more pairs than others. Coverage separately retains all eligible Paired and one-sided outcomes and distinct-station presence, using the two advantage metrics in [Section 8.2.4](#sec-7-benchmark-coverage). An empty ΔSNR layer can coexist with non-qualifying Paired or one-sided evidence; it does not prove that the database returned no reports.

**Performance successful-SNR deviation** compares each station with its own usual successful level. A station needs at least **three successful normalized observations** in the complete run window. Their median is its baseline; subtract that baseline from each successful SNR. For example, **−7 dB** against a **−10 dB** baseline gives a **+3 dB deviation**. Zero means that path's usual successful level, not Target–Reference equality.

Within each chronological bin, a station contributes at most one median deviation. The displayed median then summarizes those station-bin medians, giving each contributing station one value.

**Performance support** uses all confirmed opportunities from qualifying stations, including stations with too few successes for an SNR baseline. Within a chronological bin, each contributing station supplies one unit of support, split according to its Decode Rate. A **40%** station rate contributes **0.4** success support and **0.6** Miss support. The total counts station participation; its success fraction reproduces the station-balanced Decode Rate. Opportunity support instead counts every confirmed opportunity, so its success fraction reproduces the Opportunity-level Decode Rate.


<a id="sec-7-view-folding"></a>
##### 8.4.4 Combining dates by UTC hour

<strong class="defined-term">UTC-hour folding</strong> combines observations from the same clock hour across dates. It shows an hour-of-day association while removing the sequence of individual dates. It is separate from chronological binning: with a **12:17 UTC** start, a **1h** chronological bin spans **12:17 to 13:17**, while folding groups observations by clock hours such as **12:00 to 13:00**, using only the part inside the selected window.

Different layers combine their evidence differently:

| Layer | What contributes at one UTC hour | How it is summarized |
|---|---|---|
| **Benchmark ΔSNR** | Retained spot pairs from qualifying stations across represented dates. | Median and distribution of the pooled pairs; frequently observed paths contribute more values. |
| **Performance SNR deviation** | One median deviation per station, date and hour. | The median and distribution of those values. Stations present on more dates, and dates containing more stations, contribute more values. |
| **Performance station-balanced Decode Rate** | Each station's successes and opportunities pooled across dates at that hour. | Calculate each station's rate, then average the station rates equally. |
| **Performance Opportunity-level Decode Rate** | All confirmed successes and opportunities of the qualifying stations at that hour. | Divide pooled successes by pooled opportunities. |

Extra observations within one station/date/hour do not add weight to the Performance SNR-deviation layer. Its weighting is nevertheless **not equal weighting of stations or dates over the whole run**, and it differs from the station-balanced rate.

**Folded views require evidence from at least two represented dates.** For Performance, a represented date has at least one qualifying confirmed opportunity somewhere in the active scope and selected window. Those opportunity dates enable both support and SNR panels; usable SNR can occur on fewer dates. Benchmark coverage uses dates with any retained outcome; its ΔSNR layer separately needs dates with retained finite paired ΔSNR from qualifying stations. Thus one date with pairs and a second with only one-sided outcomes can enable folded coverage without enabling folded ΔSNR.

**Folded support bars are averages over included date-hour slots.** A represented date's clock hour counts in the denominator whenever it overlaps the selected window, even if that hour has no evidence. Hours outside the window do not count. A partly overlapping boundary hour counts as **one complete slot**, without weighting by the minutes covered, so its average can be depressed.

For Performance, total station support is the number of station/date/hour presences divided by that slot count. Its success/Miss split uses that hour's station-balanced Decode Rate, calculated from each station's pooled successes and opportunities. Opportunity support is the pooled opportunity count divided by the same denominator. For example, if two represented dates have **six** and **zero** opportunities in one included hour, its average support is **three**. The second date must have relevant evidence elsewhere to be represented. This averaging creates no extra misses: Decode Rate still uses the confirmed opportunities.

**Benchmark coverage keeps each date's station classifications separate.** Classify each identity within each UTC date and hour, sum the daily **Both observed**, **Only Target** and **Only Reference** counts, then divide by the represented date-hour count for the upper bars. A station seen only by Target on Monday and only by Reference on Tuesday does not become Both observed on either date. The Station Reach Advantage line uses the sums of the daily Target and Reference station totals, not an average of daily ratios.

The lower bars similarly divide pooled native outcome counts by the represented date-hour count. Their ΔDecode line uses pooled decode totals across dates. Neither line unions station membership across the whole period or averages the daily advantage values.

Check the chronological view before calling an hour-of-day pattern recurrent; folding does not show that it occurred on every date.


<a id="sec-7-view-station"></a>
<a id="sec-7-8-4"></a>
##### 8.4.5 Selected Station Evidence

Selected Station Evidence normally follows **one exact remote identity**. Selection does not change upstream matching or eligibility. In **Benchmark**, it uses that identity's full completed-run evidence, independently of Inspector geography and the optional station-list filter. **Performance** retains its active-scope behavior. An explicit Drill-Down focus can narrow the displayed interval.

| Analysis | Selected-station summaries |
|---|---|
| **Benchmark** | Chronological and folded ΔSNR summaries require the station to meet its spot-pair minimum over the full filtered period. Coverage separately retains Only Target, all Paired observations in one green category, and Only Reference. Its curve is that station's pooled ΔDecode, using the same signed ratio axis as the segment's Spot-level row. |
| **Performance** | Chronological SNR uses actual normalized successful Target values; folded SNR uses one date-hour median per represented date. Success/Miss counts and Decode Rate describe that same path. With one station, both Decode Rate weightings coincide within a populated bin, although station presence and opportunity volume remain different support counts. |

When outlier reporting is enabled, Benchmark can also select **multiple identities** and pool their qualifying spot pairs for ΔSNR. This gives each pair equal weight, not each path. ΔDecode Temporal Coverage is available only when **one path** is selected. Selection, station-list filtering and zoom do not recalculate qualification or rerun detection.

**Focused Drill-Down shows native retained observations:** one consolidated paired ΔSNR value for Benchmark, or one successful normalized Target SNR for Performance, at its actual WSPR-cycle time. These processed points are distinct from temporal-bin medians and density summaries; they are not untouched database rows. In Benchmark, retained pair rows remain available below the station minimum, but the focused ΔSNR plot also requires the station to qualify over the full filtered period.

**Outlier Focus** can include the candidate and its full supported baseline periods before and after, even when that exceeds an ordinary focus interval. It uses the completed detector result rather than fitting a new detector to the focused subset. Local baselines and departure guides apply to that candidate; they are not confidence intervals or independent qualification tests. Changing focus or display bins changes the view, not the completed scientific result.


<a id="sec-7-view-spread"></a>
<a id="sec-7-8-5"></a>
##### 8.4.6 Spread and display scales

**Spread is not confidence.** A Q1–Q3 band spans the middle half of the contributing values; a min–max interval spans their full range. Neither is a confidence interval.

In temporal views, median markers remain available from **one** contributing value. Adjacent bin medians connect only when **each bin has at least three** values. An IQR band spans adjacent bins only when **each has at least five**; isolated supported bins have no band, and unsupported bins break the connections. Depending on the view, those values are spot pairs, successful Target observations, station-bin medians or station/date/hour medians. Performance distance profiles instead use the station-median rules in [Section 8.4.2](#sec-7-view-geography), including the two-station min–max interval.

**<strong class="defined-term">Density colors</strong> are relative within each panel.** The most populated cell is assigned **100**, and other cells are scaled in proportion to its count. This does not mean that the cell contains 100% of the evidence. Use the accompanying support counts to compare absolute volume between panels.

**ΔSNR map colors.** Symmetric color limits adapt to the qualifying segment values. Compare the numerical legends across runs.

**ΔSNR binning and axes.** Benchmark histograms normally use **1 dB** bins, use **0.5 dB** for a clear half-dB lattice, and coarsen broad ranges. Temporal density cells remain **1 dB** high and shift with Reference correction. For the same retained population, the cells and observations move together while cell counts and relative colors stay unchanged. Display binning neither rounds the retained observations nor changes their statistics; fractional observations need not lie at cell centers.

Benchmark ΔSNR temporal and histogram axes can compress the tails around the scope median while keeping absolute **0 dB** visible. Read the labeled dB coordinates rather than estimating differences from spacing. Histogram bar **length against the percentage axis**, not displayed area, gives the share. These display transforms change neither values nor counts, medians or quartiles. Performance successful-SNR axes remain linear in dB.

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

<strong class="defined-term">Descriptive statistics</strong> summarize the observations retained in a run. <strong class="defined-term">Statistical inference</strong> uses observations and justified assumptions to estimate behavior beyond those observations, often with a measure of uncertainty. A correct descriptive result does not by itself establish how a station will perform in a new period or what caused the difference. Assess the support and experimental design before extending the claim; [Chapter 9](#sec-8) provides wording examples.


<a id="sec-7-dependence-bias"></a>
##### 8.5.1 Dependence and bias

**1 000 spots are not 1 000 independent experiments.** Repeated cycles share equipment and propagation; nearby stations share conditions; neighboring time bins are related; one interference or ionospheric event can affect many observations. The two phases of an extended-WSPR sequence add observations within a run, not independent experimental repetitions.

Station balancing reduces domination by prolific reporters, and medians reduce sensitivity to isolated extremes. Neither removes systematic calibration errors, reporting differences or propagation bias, or creates independence.

**A descriptive mean or standard deviation does not require Gaussian data.** A mean describes an arithmetic average; standard deviation describes spread around that mean. Both can summarize a finite observed dataset without assuming a normal, bell-shaped distribution. Their usefulness depends on the quantity being summarized and the distribution's tails or extreme values. A median describes the middle value, and IQR measures the width of the middle half; these answer different questions and are less sensitive to extreme magnitudes. Choose the statistic for the intended quantity, rather than treating a non-normal distribution as a reason that a mean is invalid <a href="#ref-30">[Ref-30]</a>.

Estimating uncertainty beyond the retained observations requires a justified sampling and dependence model. Non-normality alone does not make inference impossible. WSPRadar does not supply standard errors, confidence intervals, p-values, statistical power or causal-effect estimates. Treating related reports as independent would generally understate uncertainty about future performance or a broader population.


<a id="sec-7-repeatability-control"></a>
##### 8.5.2 Repeatability and experimental control

Assess support at several levels:

| Check | What to examine |
|---|---|
| <strong class="defined-term">Evidence depth</strong> | Confirmed opportunities or spot pairs per contributing identity. |
| **Breadth** | Number and geographic diversity of station identities and paths. |
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

**This experimental, optional detector identifies temporary departures from a path's usual local ΔSNR.** It is an expert diagnostic, not a required analysis step. [Section 2.5](#sec-outlier) explains its use and [Section 10.6](#sec-5-6) gives the controls. This overview explains the scientific interpretation and principal checks, rather than every algorithmic refinement.

<a id="sec-7-outlier-departure"></a>
##### 8.6.1 Departure from the local baseline

The detector uses native spot pairs from stations eligible for paired ΔSNR summaries, separately for each exact remote callsign-plus-full-locator identity. Native evidence has already undergone matching, consolidation and scientific filtering. Detection uses actual WSPR-cycle times before display aggregation; changing a plot's time-bin width does not change the events. With reporting off, the detector does not run.

**Departure is ΔSNR minus its local baseline.** Against a **+8 dB** baseline, a **+1 dB** spot pair has departure **+1 − (+8) = −7 dB**. Target still has higher SNR, but its advantage is 7 dB below the local baseline. A change in Target, Reference or both can produce that departure.

Candidate grouping follows the departure's sign, not the sign of ΔSNR relative to zero.


<a id="sec-7-outlier-baseline"></a>
##### 8.6.2 Baseline and nearby variability

A <strong class="defined-term">baseline flank</strong> is the surrounding evidence on one side of a candidate. WSPRadar calculates median ΔSNR in populated **UTC-aligned 10-minute cells**, using evidence up to **six hours before and after** the candidate. It excludes the candidate and a surrounding guard interval, keeping that nearby gap out of the baseline.

Each flank needs **at least four populated cells**. Its baseline is the median of its cell medians. The expected local ΔSNR is then the **average of the two flank baselines**, giving before and after equal weight. Missing cells are not filled; insufficient support on either side leaves the candidate unclassified.

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

Nearby same-sign departures form provisional candidates using the path's observed evidence cadence — the spacing of its retained timestamps. Final qualification uses a local baseline fitted with the **complete candidate excluded**.

The event's **median departure** is the median of its spot-pair ΔSNR values after subtracting that local baseline. It is not the magnitude of the observed median ΔSNR. All four checks below must pass:

| Required check | Passing condition |
|---|---|
| <strong class="defined-term">Absolute departure</strong> | The magnitude of the event's median departure reaches **Minimum absolute ΔSNR departure (dB)**, allowing **0.01 dB** tolerance. |
| <strong class="defined-term">Relative departure</strong> | Its absolute robust z-score reaches **Minimum robust z-score**, without tolerance. |
| <strong class="defined-term">Baseline agreement</strong> | The before/after flank medians differ by no more than **Maximum pre/post baseline difference (dB)** plus **0.01 dB**. |
| <strong class="defined-term">Sign agreement</strong> | At least **two thirds of the candidate's retained native spot pairs with finite ΔSNR**, including intervening pairs retained within the candidate in the denominator, share the median departure's sign. |

Baseline agreement tests agreement of the two medians, not low background variability. The dB tolerance affects comparisons, not stored observations or statistics. Duration gives no weaker threshold, and a single large point cannot replace the event-median checks.

**One-sided timestamps have a limited role.** The cadence estimate uses all retained Paired and one-sided timestamps for an identity eligible for paired summaries; it does not verify the physical operating schedule. A scientific change that retains additional one-sided observations can therefore change estimated cadence, permitted candidate gaps and baseline guard intervals. Grouping, baseline support and qualification can change even if every paired ΔSNR value is unchanged.

One-sided observations supply neither detector ΔSNR nor a vote in sign agreement. Display-only visibility changes do not alter the retained timestamps or rerun detection.


<a id="sec-7-outlier-boundaries"></a>
##### 8.6.4 Boundaries and event classes

Reported boundaries must be same-sign spot-pair observations that individually pass **both** departure thresholds. The interval is trimmed to these strong anchors and retested against the event-level requirements; weaker interior observations can remain. If a smaller strong core is retained, it keeps the complete candidate's baseline, scale and support rather than choosing a more favorable baseline. If no anchored interval qualifies, no event is reported.

| Event class | Retained spot pairs |
|---|---|
| <strong class="defined-term">Spot impulse</strong> | One spot pair. |
| <strong class="defined-term">Sustained excursion</strong> | At least three spot pairs spanning at least **30 minutes**. |
| <strong class="defined-term">Short burst</strong> | Every other event containing two or more spot pairs. |

All classes pass the same checks. The span from first to last observation describes retained evidence, not uninterrupted behavior between observations or the duration of an unseen physical event.


<a id="sec-7-outlier-context"></a>
##### 8.6.5 Context and limits

Each path qualifies separately. Grouping nearby same-sign events across paths provides review context — path-specific, directionally coherent, scope-wide or multiple paths. It adds neither significance nor stronger qualification.

Target/Reference decomposition and nearby one-sided counts attached **after qualification** help investigate a candidate. These attached diagnostics cannot qualify, extend or strengthen it. This is separate from the earlier use of one-sided timestamps in the cadence estimate, explained in [Section 8.6.3](#sec-7-outlier-qualification).

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
| **Inferential** | The result generalizes beyond these observations, with a stated confidence or significance. | A justified model of dependence and an inferential analysis, which WSPRadar does not supply. |

Match the statement to the quantity:

- **Performance** describes the Target's success within confirmed opportunities and its at-least-once reach during the selected window.
- **Benchmark ΔSNR** describes Target-minus-Reference SNR among retained spot pairs. Signals decoded on only one side have no paired SNR difference.
- **Decode Outcomes** describe paired and one-sided evidence. **Station Reach Advantage** compares distinct-station totals; **ΔDecode** compares pooled decode totals. Neither advantage is a Target win rate or an absolute decoding probability.
- **Direction and distance patterns** describe the observed radio paths, without directly measuring antenna radiation angle or gain pattern.

A controlled Benchmark relies on independently known common operation. **Historical replay** can describe the reported differences, but unverified schedules, uptime or uploads may explain one-sided counts. Do not present that replay as a controlled comparison of decoding success.

| Avoid | Evidence-matched wording |
|---|---|
| “Antenna A has 3 dB more gain than B.” | “For this band, UTC window and segment, the median of station-median ΔSNR was +3.0 dB for path A relative to B, supported by [n] qualifying identities and [m] spot pairs.” |
| “My receiver sensitivity is 72%.” | “The Target's station-balanced Decode Rate was 72% across [n] qualifying remote identities during the stated window, using confirmed opportunities.” |
| “Performance should be close to 100%.” | “Decode Rate is conditional on confirmed opportunities; 100% is not an expected baseline.” |
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
| **Dependence and generalization** | Reports share stations, time periods, geography and propagation. A row count is not an independent sample size. WSPRadar does not supply confidence intervals, significance tests or a causal conclusion. |

WSPRadar does not directly measure antenna gain relative to isotropic (**dBi**), radiation efficiency, take-off angle, propagation mode, calibrated receiver sensitivity or absolute field strength. A gain *difference* is expressed in **dB**, but an observed ΔSNR is not automatically a measurement of that difference.

Broad evidence, consistent results and repetition under documented controls can support a practical station decision. Keep the claim within what the experiment measured; [Section 8.5](#sec-7-claims) explains dependence and experimental control.


<a id="sec-8-3"></a>
#### 9.3 Reporting and reproducibility checklist

Preserve three layers when comparing, publishing or acting on a result. The export supplies much of the analysis definition and evidence; keep physical setup measurements and operating records separately.

**1. Analysis definition**

- WSPRadar application version and, where available, source revision;
- database source and original export date;
- RX/TX direction, result type and Benchmark design;
- exact Target and Reference identities and locators;
- band and effective UTC boundaries;
- geographic scope, solar state, exclusions and evidence thresholds;
- Reference correction purpose, signed value and calibration basis;
- applicable common-operation declaration or historical-replay acknowledgement and limitations;
- primary scope chosen before inspecting the result, and any alternative settings or scopes checked; and
- whether the run was exploratory or confirmatory.

If an outlier candidate contributes to the conclusion, also record that reporting was enabled, the three detector thresholds, detector version, exact path, UTC interval, event class and whether the finding was exploratory or assessed under a previously fixed confirmatory setup.

**2. Evidence supporting the conclusion**

- Reported metric and its weighting;
- qualifying identities and confirmed opportunities for Performance;
- stations with paired observations and spot-pair counts for Benchmark;
- station-level and observation-level summaries;
- Station Reach Advantage, pooled ΔDecode and relevant Paired, Target-only and Reference-only counts;
- geographic and temporal scope, including an influential identity or short interval; and
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
| <strong class="defined-term">Disclaimer</strong> | `disclaimer.txt` contains the complete [Experimental Use & Disclaimer](#sec-disclaimer) in the application language at export time. It accompanies every package. |
| **Configuration** | `wspradar_config.config` restores analysis settings and supported view choices for another run. It does not contain the original observations. |
| <strong class="defined-term">Run metadata</strong> | `run_metadata.json` records software version, database, actual data selection, analysis settings, corrections, inspection scope and enabled outlier settings. Benchmark also records its evidence mode, applicable operating declaration or historical-replay acknowledgement, and method version. These declarations are not independent proof of operation. |
| <strong class="defined-term">Processed evidence</strong> | `analysis_cache.parquet` contains retained evidence across the completed analysis's full geographic scope after scientific filtering. It is not restricted to the selected segment and is not an untouched database download. |
| <strong class="defined-term">Station Insights CSV</strong> | Benchmark `table_station_insights.csv` follows the global or optionally Inspector-filtered station list. Performance `table_station_insights_current_segment.csv` follows its active Inspector scope. Both also follow Station Insights column filters, with scope and filters recorded in metadata. Empty tables retain headers. |
| <strong class="defined-term">Drill-Down CSV files</strong> | Row-level evidence for selected stations or all stations in the active segment. The selected-station table can follow focus and table filters. Both files retain headers when empty. |
| <strong class="defined-term">Outlier CSV files</strong> | `table_delta_snr_outlier_event_paths.csv` summarizes qualifying path events; `table_delta_snr_outlier_paired_evidence.csv` contains their chronological spot pairs, including corrected Reference SNR. Both cover the active segment and join through IDs valid only within this package. Reporting off: files absent. Reporting on with no findings: headers only. Findings remain candidates, not confirmed physical events. |
| <strong class="defined-term">Map, segment and temporal figures</strong> | The map covers the completed analysis. Segment and temporal figures follow the active segment, including applicable chronological and UTC-hour views. |
| <strong class="defined-term">Selected-station figures</strong> | Benchmark uses the selected identity's full-run evidence; Performance follows its active scope. With outlier reporting enabled, Benchmark can instead show pooled ΔSNR for multiple selected paths. |
| <strong class="defined-term">Drill-Down focus figures</strong> | Additional figures for exactly one selected station and its active focus interval. They preserve individual observations and chronological context alongside the ordinary selected-station figures. Candidate guides apply to the focused episode. |

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

Changing the analysis choice, identities, band, UTC window, Reference correction, filters or evidence requirements clears the completed result and requires a new **Run**. Changing an Inspector selection, station-list filter, time aggregation or Drill-Down view does not rerun the analysis.

<a id="sec-5-1"></a>

#### 10.1 Workflow controls

| Control | What you need to know |
|---|---|
| **Input view** | Guided and Compact use the same analysis settings. The chosen input view is not saved. |
| **Load Demo** | Loads settings without running. In Guided, **Walk me through the setup** opens the steps; **Skip to review and run** starts the valid loaded analysis immediately. |
| **Start Fresh** | Clears settings and results and restores defaults, including the UTC window. Language and input view stay unchanged. |
| **Load Config / Save Config** | Load or save applicable analysis settings and supported view choices. Saved dates are fixed UTC boundaries, not a rolling period. A configuration contains no result data or station notes. |
| **Run RX Analysis / Run TX Analysis** | Starts the chosen analysis after validation. Resolve highlighted fields and any Reference location choice first. A map can appear before the remaining views are ready; wait for **Complete**. |
| **Prepare All Results for Download** | Builds the export for the current selections. Then choose **Download Prepared Results**. Prepare again after changing the selections. See [export contents](#sec-8-4). |

**Keyboard:** use `Tab` and `Shift+Tab` to move between controls. In Guided, forward `Tab` beyond a setup panel validates it and opens the next step, like **Continue**; errors return focus to the first invalid field. Reaching Review does not start the analysis. The separate `?` help icons require a pointer.

Loading or saving a configuration does not run it. Unsupported old formats are rejected. One compatibility exception accepts a complete valid pair of former ΔDecode count thresholds and replaces them with the **1% event-share default**, with a notice; it does not convert counts into percentages. Review loaded settings before running.

<a id="sec-5-2"></a>

#### 10.2 Question, Target and measurement-window controls

| Control | Default and essential rules |
|---|---|
| **Question** | Required: choose RX Performance, TX Performance, RX Benchmark or TX Benchmark. Only Benchmark needs a Reference. |
| **Target callsign** | Required: use the exact reporting identity, including any prefix or suffix. `CALL`, `CALL/P` and `CALL-1` are different identities. |
| **Target QTH (4 or 6 characters)** | Required: the first four locator characters select Target reports; the full entered locator anchors map, distance, direction and solar calculations. |
| **Operating Band** | Default **20m**. Select one band. |
| **Start / End Date/Time (UTC)** | Default: 24 hours ending at the current UTC minute. Dates start in 2008; a run may span at most **31 elapsed days**. Times retain minute precision. |

A four-character <strong class="defined-term">Maidenhead locator</strong> (grid-4) identifies a grid square; six characters identify a smaller subsquare.

<a id="sec-5-3"></a>

#### 10.3 Benchmark-design controls

| Control | What to enter |
|---|---|
| **Reference callsign** | One exact identity different from the Target. Reference Neighborhood is no longer supported. |
| **Known Reference QTH (4 characters, optional)** | Leave blank to discover the location from reports, or enter an independently known grid-4. One discovered grid resolves automatically; several require your choice. A known location does not establish operation. |
| **Reference SNR correction** | Default **No correction** applies **0.0 dB**. Choose **Use a documented correction** only for an established offset valid for this setup. The signed field accepts **−99.9 to +99.9 dB**; blank means **0.0**. Use a decimal point. A documented zero remains distinct from no established correction. |

**Operating confirmation:** for your own Benchmark, confirm common operation as described in [Section 1.2](#sec-2-2). Changing identities, direction, band or period clears the confirmation. Loading a personal configuration or ordinary analysis link requires fresh acknowledgement; saved declarations do not verify operation.

**Historical replay** uses a separate acknowledgement of uncertain historical operation, not a controlled-operation declaration. Ordinary replay loads require fresh acknowledgement, including legacy analysis links with `run=1`. Opening a link never starts an analysis. Built-in demos preselect the declaration appropriate to their documented mode; the Milazzo demo uses the historical-limits acknowledgement. A demo link opens **00 Guided demo** with that demo selected and the **Walk me through the setup** and **Skip to review and run** actions. Loading a demo alone still does not run it.

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
| **Maximum peer distance from Target (km)** | **22 000**; choices 2 500 / 5 000 / 10 000 / 15 000 / 20 000 / 22 000 | Removes peers **at or beyond** the limit from the analyzed population and exports. This changes the analysis, not just the map view. |
| **Minimum spot pairs per station for ΔSNR** | **1**; 1–50 | Benchmark: qualifies each exact station identity over the full filtered period. One-sided reports do not satisfy this requirement. |
| **Minimum confirmed opportunities per station** | **5**; 1–100 | Performance: requires this many successes plus confirmed misses per identity. Lower values produce coarser, less-supported rates. |
| **Minimum qualifying stations per map segment** | **1**; 1–10 | Performance: requires this many qualifying identities before a segment is drawn. |
| **Minimum qualifying stations per segment for ΔSNR** | **5**; 1–10 | Benchmark: requires this many identities meeting the spot-pair minimum before the segment receives ΔSNR coloring. |
| **Minimum observed-event share per segment for ΔDecode (%)** | **1%**; 0–5%, steps of 0.5% | Benchmark: requires this share of the full filtered run's observed events, rounded up to a whole event. At **0%**, every nonempty segment qualifies. |

The **one-pair default** for ΔSNR preserves sensitivity by keeping sparsely observed paths eligible. Use **Minimum qualifying stations per segment for ΔSNR** — default **5** — to prevent a single path alone from determining a segment's ΔSNR color. A station with one pair contributes just one ΔSNR observation.

The ΔDecode requirement's full-run denominator stays fixed when you crop or select a segment. ΔDecode has no separate per-station minimum. These requirements measure evidence volume, not confidence.

Benchmark segments with observed evidence but below the relevant threshold are gray hatched; retained station observations remain available. The ΔSNR pair minimum does not remove decodes from ΔDecode. In Performance, evidence outside the distance limit may still establish Target activity, without adding those peers to the analyzed population.

Once you manually change either exclusion, that choice persists across Question changes. Stored configurations, demos and analysis links also preserve their explicit exclusions.

<a id="sec-5-5"></a>

#### 10.5 Map, inspector and export controls

These controls inspect the completed evidence without changing its classification:

| Control | Scope and persistence |
|---|---|
| **Segment distance and direction** | Changes Inspector statistics and time views. Performance Station Insights follows this scope. Saved separately for Performance and Benchmark. |
| **Filter by selected segment and distance** | Optionally restricts the Benchmark station list; otherwise it is global. Selected-station evidence still covers the full run. This toggle is not saved. |
| **Station Insights → Filter** | Restricts the station list and its exported table, not maps or Inspector statistics. Column filters are saved; a station must meet every active condition, while any selected value within one callsign/locator filter can match. |
| **Heard only by other stations. / Only other signals heard.** | Shows Performance peers whose confirmed opportunities were all misses. This is a saved visibility choice. |
| **Include one-sided evidence** | Shows Benchmark identities without spot pairs and one-sided Drill-Down observations. This saved visibility choice changes neither coverage totals nor qualification. |
| **Selected station row** | Saves the exact callsign-plus-locator selection: normally one per result type; multiple Benchmark identities are supported when outlier reporting is enabled. |
| **Time aggregation** | Changes chronological display bins; Inspector and selected-station choices are saved separately. Pairing, opportunities and fixed one-hour UTC profiles remain unchanged. |
| **Zoom window / <strong class="defined-term">Outlier Focus</strong>** | Focuses Drill-Down on an interval for exactly one selected station. **Filter table** then narrows table rows only. Focus and Drill-Down table filters are not saved in configurations or analysis links. |

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

**Identify ΔSNR outlier candidates** is off by default. Enable it only when investigating temporary departures in paired evidence; see [Section 2.5](#sec-outlier).

| Control | Default / range | Effect |
|---|---|---|
| **Minimum absolute ΔSNR departure (dB)** | **6.0**; 0.1–100.0 dB | Requires a sufficiently large change from the path's local baseline. |
| **Minimum robust z-score** | **3.0**; 0.1–100.0 | Also requires the change to be large relative to nearby variation, using the absolute robust score. This score is not a probability. |
| **Maximum pre/post baseline difference (dB)** | **3.0**; 0.1–100.0 dB | Requires the baseline medians before and after the candidate to agree within this amount. It does not require low background scatter. |

All three requirements, plus the detector's support checks, apply to every event duration. Lowering either minimum or raising the allowed baseline difference makes reporting more permissive. Changing detector settings requires another **Run**; detections are independent of display-bin width and do not change the ordinary Benchmark maps. [Section 8.6](#sec-7-outliers) gives the exact method and limits.

<a id="sec-6"></a>
<a id="sec-5-7"></a>

### 11. Troubleshooting and Data Quality

Start with the run definition. Lower thresholds cannot repair a wrong identity, band, time window or transmission schedule.

<a id="sec-6-1"></a>

#### 11.1 Confirm the run definition first

Check the exact **Target identity and QTH**, **band** and **UTC window**, then actual operation and uploads. For Benchmark, also check Reference identity, common operating times, synchronized clocks and, for TX, [schedules and frequency separation](#sec-simultaneous-tx-setup-2). Verify signal routing and actual versus reported power before interpreting an unexpected difference.

<a id="sec-6-2"></a>

#### 11.2 Diagnose by symptom

Read notices against the settings of the **completed run**. An observed count and a required minimum are different: three observed opportunities do not meet a five-opportunity requirement.

| Symptom | What to check or do |
|---|---|
| **No Target/source evidence returned** | Check identity, locator, band, UTC window and uploads in the selected database. Review [historical mode filtering](#sec-6-4). Lowering evidence thresholds cannot create source reports. |
| **Reports returned, but none remain** | Review station exclusions, solar state and maximum peer distance. These may remove the retrieved population. |
| **No qualifying Performance stations** | Compare confirmed opportunities with the station minimum. Check both endpoint-activity evidence and population filters; unknown activity is not a confirmed miss. |
| **Performance stations exist, but no map segment qualifies** | Inspect station evidence and compare each segment's qualifying-station count with its minimum. Missing map output is not a zero Decode Rate. |
| **Benchmark ΔSNR is missing or hatched** | Check for the same remote identities in the same cycles, common operation and synchronized schedules. Then check station pair counts and the segment station minimum. One-sided evidence can still support ΔDecode. |
| **ΔDecode is hatched despite observed reports** | Compare the segment's event count with the full-run event-share requirement. Selecting a smaller area does not lower that requirement. |
| **Station list is unexpectedly empty** | Clear Station Insights column filters and review visibility toggles. In Benchmark, also check **Filter by selected segment and distance**. |
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

**Performance** counts each success as its own confirmed opportunity. A miss requires activity evidence at both endpoints on the same band in the same cycle; otherwise the outcome remains unknown. The direction-specific rules are in [Section 8.3.1](#sec-7-performance-opportunities).

<a id="sec-6-6"></a>

#### 11.6 Working with upstream data

<strong class="defined-term">System Audit Status</strong> identifies the database and any historical fallback used. Each run uses one source; reports from different databases are not combined. WSPRadar can switch sources for a new attempt, but Reference location discovery ties the ensuing analysis to that source. If it fails, restart and review the newly resolved Reference location.

For recent reports, allow about **five minutes** after the final cycle, then check uploads and availability in the selected database. This is a practical waiting estimate, not a completeness guarantee <a href="#ref-10">[Ref-10]</a>. Databases may contain incorrect identities, locators or power values, delayed reports and later corrections. Demo reruns may reuse previously retrieved data, so rerunning need not pick up later corrections.

A request exceeding **1 000 000 complete rows** is rejected, not silently truncated. Shorten the UTC window; **Exclude Special Callsigns Q, 0, 1** can reduce source queries when appropriate to your question. The distance limit is applied **after retrieval**, so reducing it does not avoid this limit.

<a id="sec-ref"></a>
<a id="part-v"></a>

## Part V: References

* <a id="ref-1"></a><a href="https://arxiv.org/abs/2209.08989">[Ref-1]</a> **Preprint.** Zander, J. (2022). *Simple HF antenna efficiency comparisons using the WSPR system*. arXiv:2209.08989v1. doi:10.48550/arXiv.2209.08989.

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

<div style="page-break-before: always;"></div>

<a id="sec-8-5"></a>
<a id="sec-disclaimer"></a>

## Experimental Use & Disclaimer

WSPRadar is a free, non-commercial hobby project developed for amateur-radio experimentation, education and scientific exploration.

WSPRadar analyzes observational data from publicly available WSPR reporting databases. Both the source data and the resulting analyses may contain errors, omissions, reporting biases or inaccuracies. Statistical assumptions, uncontrolled propagation conditions and software defects may further affect the reliability and interpretation of results.

WSPRadar is not a calibrated measurement instrument. Its findings are indicative and should be independently verified. Results must not be relied upon as the sole basis for significant personal, financial, safety-related, technical, legal or other consequential decisions. **WSPRadar is not intended for safety-critical applications, emergency decision-making or establishing compliance with legal or regulatory requirements.**

The software, service and results are provided **“as is” and “as available.”** No additional contractual guarantee is given regarding accuracy, completeness, reliability, fitness for a particular purpose or continuous availability. This statement does not exclude or restrict statutory rights.

Use and interpretation of the results remain the user's responsibility, including independently assessing their suitability before acting on them. Mandatory statutory rights remain unaffected.
