# WSPRadar.org

HAM RADIO STATION & ANTENNA BENCHMARKING

<a id="sec-1"></a>

### 0. Why WSPRadar?

Radio amateurs continually modify and improve their stations. A new antenna goes up, its height or orientation changes, a feedline is replaced, a common-mode choke is reworked, or a receiver, filter or preamplifier is added. The same question follows almost automatically: **did the change actually improve the station — and if so, where, when and by how much?**

On the air, this can initially seem easy to answer. More contacts are completed, a remote operator gives a better signal report, a WebSDR shows a stronger signal or WSPR produces more spots. Such observations are valuable, but they do not measure the changed component alone. The result always arises from the complete station interacting with the radio path: antenna, feedline, radio, transmit power, receiver, local noise, interference, terrain, ionosphere, remote station and time all contribute at once.

This is the fundamental measurement problem. A better report may reflect a favorable moment of propagation. An additional contact may involve a different remote station. A higher spot count may come from changing network activity or better conditions. Even completely accurate observations therefore do not automatically reveal the cause.

Experienced radio amateurs address this problem with increasingly controlled methods: repeated comparisons, beacon transmissions, WebSDRs, Reverse Beacon Network data, WSPR and especially rapid live A/B switching. A fast A/B test is far more informative than two contacts made hours apart because the transmitter, power, frequency, remote station and much of the radio path remain similar. Established WSPR comparison experiments likewise show that common conditions and the shortest practical — or simultaneous — comparisons are more robust than long separated measurement blocks <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-3">[Ref-3]</a> <a href="#ref-4">[Ref-4]</a> <a href="#ref-5">[Ref-5]</a>.

Yet even a careful rapid A/B comparison normally observes one radio path during one short interval. QSB, multipath propagation, QRM and local noise can change during the switch. AGC, S-meter resolution, unequal signal chains and subjective reports add further uncertainty. An observed advantage may be real, but at first it applies only to that station, direction, time and propagation state.

The real challenge is therefore not merely to observe a difference. It is to determine **whether the difference repeats under many comparable conditions, how large it typically is, on which radio paths it appears, when it recurs and how much evidence supports it.**

This is where WSPR provides an unusually powerful foundation. Its repeated, time-stamped and machine-decoded low-power transmissions create observations across many stations, distances, directions and propagation states in a worldwide volunteer network <a href="#ref-6">[Ref-6]</a> <a href="#ref-7">[Ref-7]</a> <a href="#ref-8">[Ref-8]</a>. Depending on band activity and the observation period, hundreds to thousands of reports can accumulate over hours or days.

WSPRadar turns that stream of reports into an experimental evidence system. It brings comparable observations together, checks whether relevant stations were demonstrably active, accounts for reported transmit power where appropriate, prevents a few prolific stations from silently dominating station-balanced summaries, and keeps every result traceable to the contributing stations and observations. The activity check follows an important observational principle: silence should not become counter-evidence until operation is independently observable <a href="#ref-9">[Ref-9]</a>.

The result is more than a spot count and more than a single winner-versus-loser number. WSPRadar can show whether a pattern is broad or path-specific, how it varies with distance, direction and time, whether many stations agree, and how much evidence comes from signals decoded by both sides or only one. It helps move station experimentation from **“this looked better once”** toward **“this difference repeatedly appeared here, under these conditions, with this much support.”**

WSPRadar is not a calibrated antenna range, and it does not turn public WSPR reports into laboratory measurements. It provides a practical bridge between everyday station experimentation and amateur science: semi-quantitative, geographically rich, time-aware and auditable evidence about complete stations and controlled signal paths under real operating conditions.

Used this way, WSPR becomes more valuable to the wider amateur community as well. Accurate callsigns, locators and power reports, stable operation and documented changes turn routine beaconing into evidence that can be revisited, compared and learned from rather than merely watched on a map.

<a id="sec-1-1"></a>

#### 0.0 WSPR in 2 Minutes

<strong class="defined-term">WSPR</strong> stands for **Weak Signal Propagation Reporter**. Joe Taylor, K1JT, and Bruce Walker, W1BW, described it as a worldwide network of low-power stations using beacon-like transmissions to explore propagation paths. WSPR operates in synchronized two-minute cycles. A WSPR-2 transmission lasts about 111 seconds and occupies about 6 Hz. An ordinary Type 1 message carries a callsign, a four-character Maidenhead locator and reported transmit power in dBm. Decoder SNR uses a 2500 Hz reference bandwidth; successful decodes around `-28 dB` illustrate how far below the noise a signal can be recovered, rather than defining a guaranteed reception threshold <a href="#ref-6">[Ref-6]</a> <a href="#ref-8">[Ref-8]</a>.

A receiving station with reporting enabled uploads each successful decode as a <strong class="defined-term">spot</strong>. This database report connects the transmitter and receiver identities and locations with time, band, reported transmit power and SNR. **WSPRnet** collects and displays reception reports; services including **wspr.live** and **WSPRDaemon** make large collections of these observations available for analysis <a href="#ref-10">[Ref-10]</a> <a href="#ref-11">[Ref-11]</a>.

**WSPRadar analyzes those database reports; it does not receive or decode radio signals.** In RX analysis, it examines the signals received by your station. In TX analysis, it examines how remote receivers hear your transmissions. **Benchmark** compares your station or setup with a Reference; **Performance** describes your station's own observed results.

Ordinary Type 1 messages are the simplest starting point when your transmitting callsign fits that format. Extended WSPR can distribute a compound callsign and six-character locator across separate transmissions. Receiver reporting identities are configured separately and do not determine the message format of the remote transmissions being received. WSPRadar uses the identities actually recorded in the database and does not reconstruct missing message phases <a href="#ref-12">[Ref-12]</a>.

For basic WSPR setup, see [Section 1.1](#sec-2-1). For preparing a comparison, see [RX Benchmark setup in Section 2.1.1](#sec-3-rx-benchmark-hardware) or [TX Benchmark setup in Section 2.2.1](#sec-3-tx-benchmark-simultaneous). These sections explain the identity and operating arrangements needed for an interpretable comparison.

**Data sources.** WSPRadar normally uses **wspr.live**, with **WSPRDaemon WD2** and **WD1** as alternatives. Each completed run uses one database; it never combines records from different sources. [Section 5.6](#sec-6-6) explains availability and source selection. The project is grateful to the people who provide and operate this public infrastructure.

The central limitation is simple: a database contains successful decodes, not a complete log of attempted transmissions or listening receivers. **A missing spot alone does not prove that a signal was missed.** In Performance analysis, WSPRadar checks for evidence that the relevant stations were active before counting a confirmed opportunity. When activity cannot be established, silence remains unknown. The practical guides to [RX Performance in Section 2.3](#sec-3-rx-performance) and [TX Performance in Section 2.4](#sec-3-tx-performance) explain how to interpret these results.

<a id="sec-1-0"></a>
<a id="sec-1-2"></a>

#### 0.1 What WSPRadar can show

WSPRadar evaluates one <strong class="defined-term">Target</strong>: the station under test, normally your station. This may be a complete installed station or a documented receive or transmit path. A <strong class="defined-term">peer</strong> is a remote station whose radio path contributes: a transmitter in RX, a receiver in TX. Choose between two questions:

* <strong class="defined-term">Benchmark</strong> asks how the Target compares with a <strong class="defined-term">Reference</strong>: a controlled local path, a known station or the observed nearby stations. It shows relative signal levels, which signals one or both sides decoded, and where and when differences appeared. The key quantity is **ΔSNR (Delta SNR)**: Target SNR minus Reference SNR for jointly decoded signals, with the applicable power normalization and Reference correction.
* <strong class="defined-term">Performance</strong> asks where, when and how consistently the Target was heard or received other stations, without a Reference. It combines at-least-once reach, successful signal levels and **Decode Rate**: the success percentage among confirmed opportunities. Station-balanced and opportunity-level summaries answer complementary questions, explained in [Chapter 2](#sec-3).

Start with your station question, then use the examples to choose the appropriate analysis.

| Your question | Practical examples | Analysis to choose |
|---|---|---|
| Which of my antennas receives better? | Compare two antennas using simultaneous receiver/decoder chains with distinct reporting callsigns, or compare receivers, feedlines, filters, preamplifiers or common-mode chokes. Use a characterized splitter for a shared antenna. Keep other conditions the same or confirm with a crossover before attributing differences to the antennas. | <span class="analysis-choice"><span class="analysis-family">RX Benchmark</span><br><strong class="analysis-variant">Reference Setup/Station</strong></span> |
| Which of my antennas is heard better? | Compare antennas, feedlines, matching networks or filters using two simultaneous transmitters with distinct identities, synchronized cycles, verified actual and reported power, clear separated frequencies and adequate RF isolation. Keep other conditions the same before attributing differences to the antennas. | <span class="analysis-choice"><span class="analysis-family">TX Benchmark</span><br><strong class="analysis-variant">Reference Setup/Station</strong></span> |
| How does my station compare with a known station? | Compare reception of the same transmitters, or compare how the same receivers hear both stations, within the same cycles. Repeat before and after station work. The result compares complete stations; your Reference is not an absolute calibrated standard. | <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Reference Setup/Station</strong></span> |
| How does my station compare with nearby WSPR stations? | Use the median SNR of qualifying observed stations within your chosen radius when no suitable single Reference is available. Look for differences by direction, distance or time. This changing whole-station baseline neither isolates antenna gain nor ranks every nearby station. | <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Reference Neighborhood (Local Median)</strong></span> |
| What can my antenna and receiver hear, and how consistently? | Map reception by direction, distance and time after installation, repair or equipment changes. Review Decode Rate across confirmed opportunities with evidence of station activity, rather than all elapsed time; investigate recurring gaps or possible local noise. | <strong class="analysis-choice-single">RX Performance</strong> |
| Where is my station heard, and how consistently? | Map where your QRP beacon or new antenna is heard, and when active receivers decode it most consistently. Use confirmed opportunities with evidence of station activity, rather than all elapsed time, and compare repeat runs after installation, repair or relocation. | <strong class="analysis-choice-single">TX Performance</strong> |

The Reference is part of the scientific question, not just a display choice. A controlled local setup provides the strongest basis for attributing an observed difference to local paths or components, but only to the extent that the remaining chains are controlled. An independent Reference Station compares complete installed stations, including QTH, equipment, terrain and the local interference and noise environment. A Reference Neighborhood describes the Target relative to a changing local population, not an isolated antenna or a fixed calibrated standard.

These perspectives make WSPRadar useful for more than formal antenna comparisons. Performance can establish a station baseline, show where a station is dependably heard, reveal directional or distance-dependent behavior, identify recurring daily patterns, and help locate when an intermittent change appeared. Benchmark can compare antennas, feedlines, filters, preamplifiers, receivers or complete paths; contrast two complete stations; or place one station in the context of its active local neighborhood.

WSPRadar can identify the **shape, scope and timing** of an observation. It can show that a difference is broad, concentrated, intermittent, recurring or supported by only a narrow subset of stations. It cannot by itself determine that the cause was antenna gain, radiation efficiency, take-off angle, calibrated receiver sensitivity, local noise or one particular hardware component. No later statistic can remove a variable that the physical experiment did not control.

<a id="sec-1-3"></a>

#### 0.2 What one run produces

One run answers one bounded station question and produces the selected Benchmark or Performance result.

**Benchmark** combines ΔSNR with Decode Outcomes and evidence coverage: a favorable signal-level difference must be read alongside the signals that only one side decoded. **Performance** combines reach, both Decode Rate weightings and successful Target SNR. Both show distance, direction, time and contributing stations.

The connected evidence path is a central strength of WSPRadar. Start with **where a pattern appears on the map**, select its geographic scope in the **Segment Inspector**, then examine **how large or consistent it is, when it occurs and which stations support it**. The station views and Drill-Down connect the summaries to individual observations. [Section 1.3](#sec-2-3-overview) introduces that path; [Chapter 2](#sec-3) explains how to interpret each analysis.

Within-run agreement between geography, time, stations and underlying observations strengthens a bounded description. A separate suitably controlled run is needed to test experimental repeatability. UTC-hour summaries combine observations from different dates; the chronological view is needed to check whether a daily pattern actually recurred.

The analysis definition, processed evidence, tables, figures and metadata can be downloaded for later review or sharing. Preserve the physical station notes alongside them: WSPRadar cannot infer the complete experimental setup. [Chapter 8](#sec-8) explains the reporting and reproduction boundaries.

<a id="sec-1-4"></a>

#### 0.3 Your first useful run

Begin with a maintained demo. Its prepared settings and experiment notes let you explore a complete historical Benchmark or Performance analysis before setting up your own station. [Section 1.1](#sec-2-1) explains how to start.

Follow one feature from the map through its geographic and temporal evidence to the contributing stations and Drill-Down. Check whether it appears across many stations or a few, whether it recurs on individual dates, and how much Benchmark evidence comes from jointly decoded signals. The demo is a worked example of the method, not evidence about your station.

For your own station, choose a comparison with a controlled path, known station or local neighborhood, or establish an RX/TX Performance baseline. The compact first-use procedure in [Section 1.1](#sec-2-1) starts with WSPR operation and database checks. Aim for a result you can understand, question, repeat and use to guide a station decision.

<a id="documentation-toc"></a>

### Table of Contents

**Part 0: Preface**

* [0. Why WSPRadar?](#sec-1)
    * [0.0 WSPR in 2 Minutes](#sec-1-1)
    * [0.1 What WSPRadar can show](#sec-1-0)
    * [0.2 What one run produces](#sec-1-3)
    * [0.3 Your first useful run](#sec-1-4)

**Part I: Operator Guide**

* [1. Choose and Prepare the Analysis](#sec-2)
    * [1.1 Build a strong experiment foundation](#sec-2-1)
    * [1.2 Choose the analysis that matches the question](#sec-2-2)
    * [1.3 Follow the evidence path](#sec-2-3-overview)
* [2. Run and Interpret Your Analysis](#sec-3)
    * [2.1 RX Benchmark](#sec-3-rx-benchmark)
        * [2.1.1 Reference Setup/Station](#sec-3-rx-benchmark-hardware)
        * [2.1.2 Reference Neighborhood](#sec-3-rx-benchmark-local-median)
    * [2.2 TX Benchmark](#sec-3-tx-benchmark)
        * [2.2.1 Reference Setup/Station](#sec-3-tx-benchmark-simultaneous)
        * [2.2.2 Reference Neighborhood](#sec-3-tx-benchmark-local-median)
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



**Part II: Controls and Troubleshooting**

* [4. Controls and Configuration](#sec-5)
    * [4.1 Workflow controls](#sec-5-1)
    * [4.2 Question, Target and measurement-window controls](#sec-5-2)
    * [4.3 Benchmark-design controls](#sec-5-3)
    * [4.4 Filters and evidence thresholds](#sec-5-4)
    * [4.5 Map, inspector and export controls](#sec-5-5)
    * [4.6 Benchmark outlier-detection controls](#sec-5-6)
* [5. Troubleshooting and Data Quality](#sec-6)
    * [5.1 Confirm the run definition first](#sec-6-1)
    * [5.2 Diagnose by symptom](#sec-6-2)
    * [5.3 Callsign and locator checks](#sec-6-3)
    * [5.4 Historical decode-code fallback](#sec-6-4)
    * [5.5 How the Target-Active Gate shapes evidence](#sec-6-5)
    * [5.6 Working with upstream data](#sec-6-6)

**Part III: Scientific Foundations, Methods and Claims**

* [6. Literature, Prior Art and Positioning](#sec-d)
    * [6.1 From reporting network to experimental dataset](#sec-d-1)
    * [6.2 Making observational WSPR data interpretable](#sec-d-2)
    * [6.3 Antenna and station-comparison lineage](#sec-d-3)
    * [6.4 Analysis infrastructure and related tools](#sec-d-4)
    * [6.5 What WSPRadar inherits, integrates and adds](#sec-d-5)
* [7. Scientific Methods](#sec-7)
    * [7.1 Shared evidence foundations](#sec-7-foundations)
        * [7.1.1 Spots, identities and cycles](#sec-7-spots-identities-cycles)
        * [7.1.2 Power normalization and consolidation](#sec-7-normalization-consolidation)
        * [7.1.3 Target activity and eligibility](#sec-7-activity-eligibility)
    * [7.2 Benchmark: differences and shared evidence](#sec-7-benchmark)
        * [7.2.1 Decode Outcomes and missing observations](#sec-7-benchmark-outcomes)
        * [7.2.2 Delta SNR and Reference correction](#sec-7-benchmark-delta)
        * [7.2.3 Station and map aggregation](#sec-7-benchmark-aggregation)
        * [7.2.4 Joint Evidence Share](#sec-7-benchmark-coverage)
        * [7.2.5 Reference Neighborhood](#sec-7-neighborhood)
    * [7.3 Performance: opportunities and success](#sec-7-performance)
        * [7.3.1 What counts as an opportunity?](#sec-7-performance-opportunities)
        * [7.3.2 Decode Rates and weighting](#sec-7-performance-rates)
        * [7.3.3 At-least-once Peer Reach](#sec-7-performance-reach)
        * [7.3.4 Successful Target SNR](#sec-7-performance-snr)
    * [7.4 Scope and summaries across space and time](#sec-7-views)
        * [7.4.1 Scope, geography and filters](#sec-7-view-scope)
        * [7.4.2 Geographic summaries](#sec-7-view-geography)
        * [7.4.3 Chronological evidence](#sec-7-view-time)
        * [7.4.4 Combining dates by UTC hour](#sec-7-view-folding)
        * [7.4.5 Selected Station Evidence](#sec-7-view-station)
        * [7.4.6 Spread and display scales](#sec-7-view-spread)
    * [7.5 How strong is the conclusion?](#sec-7-claims)
        * [7.5.1 Dependence and bias](#sec-7-dependence-bias)
        * [7.5.2 Repeatability and experimental control](#sec-7-repeatability-control)
        * [7.5.3 Validation scope](#sec-7-validation)
    * [7.6 Experimental ΔSNR event analysis](#sec-7-outliers)
        * [7.6.1 Departure from the local baseline](#sec-7-outlier-departure)
        * [7.6.2 Baseline and nearby variability](#sec-7-outlier-baseline)
        * [7.6.3 Candidate qualification](#sec-7-outlier-qualification)
        * [7.6.4 Boundaries and event classes](#sec-7-outlier-boundaries)
        * [7.6.5 Context and limits](#sec-7-outlier-context)
* [8. Evidence-Matched Claims and Reproducibility](#sec-8)
    * [8.1 Claim classes and evidence-matched wording](#sec-8-1)
    * [8.2 Interpretation boundaries](#sec-8-2)
    * [8.3 Reporting and reproducibility checklist](#sec-8-3)
    * [8.4 Analysis export package](#sec-8-4)
    * [8.5 Disclaimer](#sec-8-5)
* [References](#sec-ref)

**Part IV: Practical Supplements**

* [Appendix A: Parallel WSJT-X Instances for Simultaneous RX](#sec-a)
    * [A.1 Create the second instance](#sec-a-1)
    * [A.2 Clone the starting configuration if required](#sec-a-2)
    * [A.3 Separate every data path](#sec-a-3)
    * [A.4 Limitations of WSJT-X for simultaneous TX](#sec-a-4)
* [Appendix B: Simultaneous TX Reference Setup](#sec-simultaneous-tx-setup)
    * [B.1 Choose the callsigns](#sec-simultaneous-tx-setup-1)
    * [B.2 Align the schedule and separate the signals](#sec-simultaneous-tx-setup-2)
    * [B.3 Check power and simultaneous signal quality](#sec-simultaneous-tx-setup-3)
    * [B.4 Verify WSPRnet and the selected database](#sec-simultaneous-tx-setup-4)
    * [B.5 Device-specific setup](#sec-simultaneous-tx-setup-5)
        * [B.5.1–B.5.2 QMX and QMX+ Virtual U3S, and Ultimate3S](#sec-simultaneous-tx-setup-5-1)
        * [B.5.3 ZachTek firmware 2.19 randomized split-lane builds](#sec-simultaneous-tx-setup-5-3)
    * [B.6 Confirm by exchange or crossover](#sec-simultaneous-tx-setup-6)
* [Appendix C: Reference SNR Calibration](#sec-reference-snr-calibration)
* [License](#sec-license)

---

<a id="part-i"></a>

## Part I: Operator Guide

This part takes you from a station question to a result you can interpret and report. [Chapter 1](#sec-2) prepares WSPR operation, helps choose RX or TX and Benchmark or Performance, and introduces the common evidence path. [Chapter 2](#sec-3) applies it to each analysis and includes an optional expert diagnostic for temporary ΔSNR departures. [Chapter 3](#sec-4) helps decide what to check next and how to preserve the result. Use Part II for exact controls and troubleshooting, and Part III for the calculations and scientific limits.

In this guide, the **experiment** is the physical on-air operation and station configuration. A **run** or **analysis** is WSPRadar's configured processing of the resulting observations. A **result** is the Performance or Benchmark evidence produced by that run.

---

<a id="sec-2"></a>

### 1. Choose and Prepare the Analysis

Start with the station question and the physical experiment. The interface choice follows from that question; it does not define it.

<a id="sec-2-1"></a>

#### 1.1 Build a strong experiment foundation

Begin with one sentence stating what is being tested and what observation would count as support. An exploratory run looks for a possible pattern; a confirmatory run tests a pattern already identified.

**Start with a demo if WSPRadar is new to you.** Open `Load Demo`, choose a profile and use `Run Selected Demo`. Keep its prepared settings for the first run and read the experiment notes. Then follow the matching guide in [Chapter 2](#sec-3).

**From WSPR operation to your first own run:**

1. **Create usable WSPR reports.** For RX, configure a WSPR-capable receiver and decoder such as WSJT-X with the correct receiving callsign, locator, band, audio input and synchronized clock. Start receiving and enable spot uploads; a local decode that is never uploaded is unavailable to WSPRadar. For TX, configure a WSPR transmitter with the correct callsign, locator, band, synchronized timing and accurate reported power; remote receiving stations supply its spots. The WSJT-X guide explains its radio/audio setup and WSPR controls <a href="#ref-12">[Ref-12]</a>.
2. **Check the database before analyzing.** Verify successful reports under the exact receiving callsign for RX or transmitting callsign for TX in WSPRnet, then confirm availability in the database used by WSPRadar. Check the reported locator and UTC times. Allow uploads to arrive and choose a completed window containing the intended operation; no fixed waiting time guarantees completeness. For a step-by-step TX preflight, see [Appendix B.4](#sec-simultaneous-tx-setup-4). [Section 5.6](#sec-6-6) covers delayed data and source status.
3. **Prepare the comparison, if needed.** Benchmark needs suitable observations of Target and Reference in the same WSPR cycles. Check Reference operation independently; observing the Target does not prove Reference uptime. Use [Chapter 2](#sec-3) to choose the Reference design, [Appendix A](#sec-a) for parallel RX and [Appendix B](#sec-simultaneous-tx-setup) for simultaneous TX. Performance needs no Reference.
4. **Enter one clear analysis.** In Guided or Classic, select RX/TX and Benchmark/Performance, the exact uploaded Target callsign, Target QTH, one band and the UTC window. For Benchmark, also choose the Reference design and required identity or radius. Review the summary and any Reference correction, then use `Run RX Analysis` or `Run TX Analysis`. [Chapter 4](#sec-5) explains the controls. A run produces only the selected result.
5. **Inspect and preserve it.** Follow the matching [Chapter 2](#sec-3) guide from Map to individual stations. If evidence is missing or unexpectedly thin, check [Chapter 5](#sec-6) before relaxing thresholds. Save the export and experiment notes as described in [Section 3.4](#sec-4-4).

**Keep the physical experiment interpretable.** Record antenna, feedline, radio, tuner, gain or power settings, decoder, software version, schedule and deliberate changes. Keep variables outside the question as stable as practical: actual and reported power for TX; gain, filtering, audio routing, decoder settings and upload behavior for RX. Keep clocks synchronized throughout.

Before a confirmatory repetition, fix direction, band, Reference design where applicable, filters, thresholds, schedule and primary geographic or temporal scope. Preserve alternative radii, time windows or scopes as sensitivity analyses rather than choosing only the favorable result.

<a id="sec-2-2"></a>

#### 1.2 Choose the analysis that matches the question

| Operating question | Analysis |
|---|---|
| How do two local receive paths, two complete receiving stations, or my receiver and a local neighborhood Reference differ? | **RX Benchmark** |
| How do two local transmit paths, two complete transmitting stations, or my transmitter and a local neighborhood Reference differ? | **TX Benchmark** |
| Which signals does my receiver decode across confirmed opportunities, where, when and how consistently? | **RX Performance** |
| Where and how consistently is my transmitter decoded by receivers shown to be active? | **TX Performance** |

Choose **Benchmark** when the question is explicitly relative to a Reference. The Reference determines the meaning of the result:

<a id="sec-2-5"></a>

* **Reference Setup/Station** compares the Target with one exact Reference identity in the same WSPR cycles. A controlled local setup is the strongest arrangement for a component or path question, but isolates that component only to the extent that the remaining paths are controlled. An independent Reference compares complete installed stations and their operating environments. Both arrangements use the same pairing algorithm.

<a id="sec-2-6"></a>

* **Reference Neighborhood (Local Median)** compares your complete receiving or transmitting station with a changing Reference formed from qualifying nearby WSPR observations inside the selected radius. The Reference is calculated separately for each remote station and WSPR cycle.

Use it to investigate where your station’s observed performance lies above, near or below the contributing local peers when no suitable fixed Reference Station is available. It describes your station in its observed local context; it does not isolate antenna gain or establish a ranking of all nearby stations.

Use the narrowest Reference design that supports the intended claim. A complete-station or neighborhood benchmark cannot be turned into isolated antenna gain by later filtering or averaging.

Choose **Performance** when the Target itself is the question and no Reference is required. It combines at-least-once reach, Decode Rate, successful Target SNR, geography, time and evidence support for the complete Target station under the selected conditions.

<a id="sec-2-3-overview"></a>

#### 1.3 Follow the evidence path

Every completed result follows the same operator path:

> <strong class="defined-term">Map → Segment Inspector → Performance/Benchmark Evidence → Temporal Evidence → Station Insights → Selected Station Evidence → Drill-Down</strong>

<a id="sec-3-4"></a>
<a id="sec-3-5"></a>

**Map.** Locate the broad distance and direction pattern. Read sector color together with the contributing station count and the applicable opportunity or Joint Spot counts (the Benchmark comparison units defined in [Chapter 2](#sec-3)). A colored sector is a prompt to inspect, not the conclusion.

<a id="sec-3-6"></a>
<a id="sec-3-6a"></a>
<a id="sec-3-6b"></a>

**Segment Inspector.** Select the geographic scope relevant to the question. Every following evidence view uses that active scope, allowing a broad map pattern to be separated into distance- and direction-dependent behavior.

**Performance or Benchmark Evidence.** In Performance, combine reach, both Decode Rate weightings and successful Target SNR. In Benchmark, combine station-balanced and observation-level ΔSNR, Decode Outcomes and Joint Evidence Share. These quantities answer different questions and should not be collapsed into one score.

**Temporal Evidence.** Use the chronological view to see when behavior changed during the run. The UTC-hour view combines the same hours across dates; inspect the individual dates before calling a pattern recurrent. Read signal levels together with the supporting station, opportunity or Joint Spot counts.

<a id="sec-3-7"></a>
<a id="sec-3-7a"></a>
<a id="sec-3-7b"></a>

**Station Insights.** Check whether the pattern is supported across many `callsign + locator` identities or is concentrated in a few paths. Read every station-level value together with its evidence counts.

**Selected Station Evidence.** Inspect one representative, surprising or high-impact path. This shows whether the segment summary also describes that path, whether its behavior is intermittent, and whether its time pattern differs from the wider scope.

<a id="sec-3-8"></a>

**Drill-Down.** Verify the retained opportunities or Joint Spots behind the result. Use the rows to check exact identities, locator changes, timing, one-sided evidence and isolated outliers. Joint Spots and their ΔSNR values are introduced in [Chapter 2](#sec-3).

The rest of Part I applies this same path to each analysis question without inventorying every title, axis or layout detail.

---

<a id="sec-3"></a>

### 2. Run and Interpret Your Analysis

Use the section matching the selected Direction and result type. Exact control labels, defaults and ranges are in [Chapter 4](#sec-5); exact eligibility, matching, weighting and aggregation are in [Chapter 7](#sec-7).

**Joint Spots in Benchmark.** WSPRadar forms a Joint Spot when usable Target and Reference SNR are available for the same remote station and WSPR cycle: the same transmitter in RX, or the same receiver in TX. For Reference Neighborhood, the Reference value is calculated from qualifying local stations. A station here means one exact callsign plus full reported locator; it need not identify a separate physical station. Joint Spots supply **ΔSNR (Delta SNR)**; signals reported on only one side do not. Performance instead uses confirmed opportunities, explained in its own sections.

<a id="sec-3-3"></a>
<a id="sec-3-rx-benchmark"></a>

#### 2.1 RX Benchmark

**Question answered.** How did Target reception differ from the selected Reference for the same remote transmitters and WSPR cycles?

**The key value: ΔSNR.** Each Joint Spot supplies Target SNR minus Reference SNR, after any configured Reference correction. Positive favors Target; negative favors Reference; 0 dB means equality. For example, +3 dB means Target SNR is 3 dB above the Reference value used in the comparison; it does not establish antenna gain.

**Read the evidence path.**

**1. Map: where does reception differ?** Segment color shows the median of the qualifying transmitters' median ΔSNR values; each transmitter has equal weight. Read the dB scale and station counts. Uncolored segments lack a qualifying result. Station markers distinguish Joint and one-sided reception. **Segment Inspector** selects directions and distances for the results below.

**2. Benchmark Evidence: how large and widespread is the difference?**

| Figure | What to read and how to interpret it |
|---|---|
| **Station Medians (Δ SNR)** | Each transmitter contributes one median ΔSNR from its Joint Spots. Bars show the percentage of stations in each dB range. Mostly positive medians favor Target across most of these paths; values on both sides of zero show that the result varies by path. |
| **Joint-Spot Δ SNR** | Each Joint Spot contributes one ΔSNR value. Bars show the percentage of Joint Spots in each dB range. This reveals variation across stations and time; frequently observed stations contribute more. Compare its center and spread with Station Medians. |

Start with the medians; the means are arithmetic averages. If the distributions differ markedly, inspect the stations contributing the most Joint Spots. [Section 7.2.3](#sec-7-benchmark-aggregation) illustrates why the results can disagree.

**3. Temporal Evidence: when does the difference occur?** In **Δ SNR over Time**, follow the interval medians against the dashed overall median: does the difference persist, reverse or appear briefly? Read the labeled dB values on the nonlinear vertical axis. The Q1–Q3 band, when shown, contains the middle 50% of ΔSNR values from Joint Spots; it is not a confidence interval. Color shows the concentration of Joint Spots; blank intervals contain none.

**Δ SNR by UTC Hour** combines matching hours across dates. Look for daily patterns, then check individual dates before calling a pattern recurring.

**Check support.** In Decode Outcomes, check both the station percentages and the spot percentages. Joint station/spot counts, **Decode Outcomes**, and **Benchmark Temporal Evidence Coverage** show how many stations and Joint Spots support the comparison and where coverage is sparse. Joint Evidence Share summarizes how much of the retained activity forms Joint Spots; it is not a Target success rate. One-sided reception may reveal differences near the decode threshold but supplies no ΔSNR. Where one-sided reports are substantial, include them in your conclusion: ΔSNR describes only the Joint Spots. Only cycles with observed Target activity are retained, so one-sided counts are not symmetric wins and losses. [Section 7.2.1](#sec-7-benchmark-outcomes) explains the categories, including asynchronous observations.

**4. Station Insights: which paths explain the result?** Compare transmitter medians with Joint-Spot and one-sided counts. Select typical and unusual paths in turn; **Selected Station Evidence** shows whether they follow the overall time pattern or appear only intermittently. **Drill-Down** lets you verify individual cycles, callsign/locator identities and correction signs.

**What to do next.** Repeat promising comparisons in another run. A result across several transmitters, times and neighboring map segments describes more paths and conditions than a few isolated observations. Keep direction- or time-specific conclusions within those conditions. Same-cycle comparison controls transmitter and timing, but the result still includes antennas, receiver chains, local noise and QTH conditions. Check Reference availability independently and use the setup guidance below to strengthen the comparison.

<a id="sec-2-3"></a>
<a id="sec-3-rx-benchmark-hardware"></a>

##### 2.1.1 Reference Setup/Station

**Controlled local setup.**

Compare two local antennas, feedlines, filters, preamplifiers, receivers or complete receive chains simultaneously at the same physical test QTH. Before the run, verify distinct exact reporting callsigns and agreement of the resolved Reference location with the actual experiment. The intended difference is the component or path under test; keep other conditions equal or characterize their differences. Components intended to be common must be physically common; shared grid-4 proves neither co-location nor path equality.

Configure each receiving path's reporting identity separately in its receiver or decoder software, and verify that its spots appear under that exact identity in the database. For example, `CALL` and `CALL/P` can distinguish two receiving paths when the reporting software and database preserve those identities. A suffix used this way identifies the receiving path in the uploaded report; it does not change the remote transmitter's WSPR message format. The recommendation to use matching transmitted message patterns in controlled TX benchmarks therefore does not apply to these RX reporting identities.

This is the strongest RX design for local-path attribution. It still compares complete documented receive paths unless receiver, audio, gain, decoder and routing differences are characterized. A broad recurring ΔSNR shift with compatible one-sided evidence supports one path outperforming the other under the tested conditions. Use common-input calibration, a splitter-output swap or hardware crossover for confirmation; these can distinguish the tested component from a persistent chain offset. [Appendix C](#sec-reference-snr-calibration) explains Reference SNR calibration; [Appendix A](#sec-a) covers separate WSJT-X instances.

<blockquote class="evidence-conclusion"><p>Under the documented simultaneous controlled RX setup, ΔSNR and Decode Outcomes described the observed difference between the Target and Reference receive paths for the shared transmitters, cycles and selected geographic scope.</p></blockquote>

<a id="sec-3-rx-benchmark-buddy"></a>

**Independent station.**

Choose an identifiable complete Reference receiver with known QTH, callsign, equipment, operating schedule and local environment. In an RX Joint Spot, Target and Reference report the same transmitter and cycle; Target and Reference remain distinct complete receiving stations with their own antennas, hardware, signal paths and local noise. WSPRadar resolves the reported Reference grid-4 from database observations in the selected window. Matching Target grid-4 is allowed, but does not prove co-location.

This benchmarks complete installed receiving stations: relative strength by direction, distance and time, and differences in one-sided reach. It cannot isolate receiver sensitivity, antenna gain or local noise as the cause. Repeat with the same well-understood Reference and stable operating conditions. For a worked example, explore the maintained Griffiths/Squibb RX comparison demo (#1), following its Temporal Evidence and selected-path guidance.

<blockquote class="evidence-conclusion"><p>For the shared transmitter paths and cycles in this run, ΔSNR and Decode Outcomes described how the two complete receiving stations compared under their respective environments.</p></blockquote>

<a id="sec-3-rx-benchmark-local-median"></a>

##### 2.1.2 Reference Neighborhood

The Reference is the cycle- and path-specific median of one contribution from each active local receiver identity inside the selected radius. Membership can change from cycle to cycle, so the result is a contextual local baseline rather than a fixed station comparison.

Here, the contributing local receivers are those with qualifying reports of the same remote transmitter in the same WSPR cycle. The Reference therefore represents the receivers observed on that transmitter path and cycle, not every receiver inside the radius. ΔSNR additionally requires a qualifying Target report for that same transmitter and cycle.

Inspect the contributing local identities, Joint Evidence Share and radius sensitivity. A shift can reflect the Target, a changed neighborhood composition or both. Choose the primary radius from local geography and station density before interpreting the result; use other defensible radii as sensitivity analyses.

Interpret the comparison as evidence about complete installed receiving stations. Antennas, feedlines, receivers, decoder and SNR-reporting behavior, local noise and interference, terrain and propagation can all contribute to the observed difference. Sharing a remote transmitter and cycle does not remove differences between the receiving sites. A neighborhood containing only one contributing receiver provides that receiver’s value as its median; it does not provide evidence of agreement across several nearby stations.

<blockquote class="evidence-conclusion"><p>For the selected band, window, transmitter paths and cycles, the Target’s complete receiving station showed the reported ΔSNR and Decode Outcomes relative to the contributing local receiver neighborhood. This does not establish that its antenna has a corresponding gain advantage.</p></blockquote>

<a id="sec-3-tx-benchmark"></a>

#### 2.2 TX Benchmark

**Question answered.** How did the Target transmitter differ from the selected Reference at the same remote receivers in the same WSPR cycles?

**The key value: ΔSNR.** Each Joint Spot compares Target and Reference SNR at one receiver. WSPRadar first normalizes SNR to a common reported transmit power of 30 dBm (1 W), then applies any Reference correction. Positive ΔSNR favors Target; negative favors Reference; 0 dB means equality. Accurate reported power is essential: the comparison cannot correct an inaccurate power report or establish antenna gain.

**Read the evidence path.**

**1. Map: where is Target stronger or weaker?** Segment color shows the median of the qualifying receivers' median ΔSNR values; each receiver has equal weight. Read the dB scale with receiver and Joint-Spot counts. Uncolored segments lack a qualifying result. Station markers distinguish Joint and one-sided reports. **Segment Inspector** selects directions and distances for the results below.

**2. Benchmark Evidence: how large and widespread is the difference?**

| Figure | What to read and how to interpret it |
|---|---|
| **Station Medians (Δ SNR)** | Each receiver contributes one median ΔSNR from its Joint Spots. Bars show the percentage of receivers in each dB range. Mostly positive medians favor Target across most of these paths; values on both sides of zero show that the result depends on the receiving path. |
| **Joint-Spot Δ SNR** | Each Joint Spot contributes one ΔSNR value. Bars show the percentage of Joint Spots in each dB range. Frequently reporting receivers contribute more. Compare the center and spread with Station Medians to see whether the individual observations and station summaries tell a similar story. |

Start with the medians; the means are arithmetic averages. If the distributions differ markedly, inspect the receivers contributing the most Joint Spots. [Section 7.2.3](#sec-7-benchmark-aggregation) explains the weighting difference.

**3. Temporal Evidence: when does the difference occur?** In **Δ SNR over Time**, follow the interval medians against the dashed overall median. Check whether a shift persists or is confined to a short interval. Read the labeled dB values on the nonlinear vertical axis. The Q1–Q3 band, when shown, contains the middle 50% of ΔSNR values from Joint Spots, not a confidence interval. Color shows the concentration of Joint Spots; blank intervals contain none.

**Δ SNR by UTC Hour** combines matching hours across dates. Check the chronological results on individual dates before calling a daily pattern recurring.

**Check support.** In Decode Outcomes, check both the station percentages and the spot percentages. Read the receiver and Joint-Spot counts with **Decode Outcomes** and **Benchmark Temporal Evidence Coverage**. Joint Evidence Share summarizes how much of the retained activity forms Joint Spots; it is not a Target success rate. One-sided reports can reveal different near-threshold reach but supply no power-normalized Target–Reference SNR comparison. Where one-sided reports are substantial, include them in your conclusion: ΔSNR describes only the Joint Spots. Only cycles with observed Target activity are retained, so one-sided counts are not symmetric wins and losses. The categories are explained in [Section 7.2.1](#sec-7-benchmark-outcomes).

**4. Station Insights: which receivers explain the result?** Compare receiver medians with Joint-Spot and one-sided counts. Select typical and unusual receivers in turn; **Selected Station Evidence** shows whether they follow the overall time pattern. Check whether an apparent advantage depends on a particular receiver or audio-frequency assignment. **Drill-Down** lets you verify receiver identity, WSPR cycle, reported powers and correction signs.

**What to do next.** Repeat a result supported by several receivers with accurately measured and reported powers. A difference confined to one direction, distance range or time may still be useful; report those conditions. The comparison covers complete transmit paths, including transmitter-chain response, frequency response, RF isolation and coupling. Use the setup controls below before attributing the difference to a component.

<a id="sec-2-4"></a>
<a id="sec-2-4-simultaneous"></a>
<a id="sec-3-tx-benchmark-simultaneous"></a>

##### 2.2.1 Reference Setup/Station

**Controlled local setup.**

Use two distinguishable complete transmitter chains at the same physical test QTH, with different valid exact callsigns, synchronized WSPR cycles, separated clear frequencies, established actual and reported power, and adequate RF isolation.

For controlled simultaneous TX benchmarks, use two distinct station identities with the same verified message pattern and synchronized transmission schedule. The recommended arrangements are:

* **Two standard callsigns, each transmitting Type 1 messages.** This is the simplest arrangement.
* **Two compound callsigns, each transmitting a Type 2/Type 3 sequence.** The compound callsigns can share the same base callsign with different suffixes, such as `CALL/1` and `CALL/2`. When using the same base callsign, give both transmitters different suffixes. Check which suffixes are permitted for your callsign and operation in your country.

For the extended arrangement, align the sequences so that Type 2 coincides with Type 2 and Type 3 with Type 3. Each of the two cycles can contribute Joint Spots when the same remote receiver reports both identities in that cycle. WSPRadar evaluates the two-minute cycles separately; it does not merge the sequence into one four-minute observation.

Check the transmitter configuration and actual transmission schedule. Callsigns alone do not establish which message sequence the firmware sends or whether the two transmitters are synchronized.

**Why the schedule matters.** If one transmitter sends while the other is scheduled to be silent, the retained reports can increase one-sided Decode Outcomes and reduce Joint Evidence Share. Those figures then partly reflect unequal transmission opportunities. Check that both transmitters send the corresponding message types in the same two-minute cycles before interpreting one-sided reports as evidence of a difference between the transmit paths. Matching schedules improve comparability but do not eliminate decoding, identity-resolution or reporting gaps.

Verify both exact database identities and their truthful reported grid-4 values before the experiment. [Appendix B](#sec-simultaneous-tx-setup) gives the practical setup and preflight. [Section 7.1.1](#sec-7-spots-identities-cycles) explains the distinction between this recommended operating arrangement and WSPRadar's same-cycle matching rules.

Same-receiver, same-cycle ΔSNR avoids a comparison across different cycles and is the strongest TX design when the two transmitter chains can be controlled. It still compares the complete documented transmit paths. Frequency-selective QRM, chain response, coupling and power error can remain. Swap the frequency positions and, where practical, cross the tested antennas or components between chains.

<blockquote class="evidence-conclusion"><p>Under the documented simultaneous controlled two-transmitter setup, same-receiver, same-cycle ΔSNR and Decode Outcomes described the observed difference between the Target and Reference transmit paths for the selected receivers and geographic scope.</p></blockquote>

<a id="sec-3-tx-benchmark-buddy"></a>

**Independent station.**

Use a known, separately identifiable complete Reference transmitter whose QTH, callsign, actual and reported power, equipment and operating schedule are understood. In a TX Joint Spot, the same remote receiver reports both sides in one cycle, but Target and Reference remain distinct complete transmitting stations with their own transmitters, antennas, feedlines and installed environments. WSPRadar resolves the reported Reference grid-4 from the selected database window. It may equal Target grid-4; equal grid-4 does not prove physical co-location.

A controlled local setup and an independent station use the same Reference Setup/Station analysis. The physical arrangement, not whether two callsigns share a base, determines the interpretation. Both require two distinct valid exact reporting identities and Joint Spots; a single switched transmitter cannot supply this comparison.

Interpret the result as a benchmark of complete installed transmitting stations. Comparing Joint Spots controls the receiving endpoint, not the two transmit sites or radio paths. Power-reporting accuracy is especially important. Repeat with the same well-understood Reference and stable configurations rather than treating the Reference as an absolute calibrated standard.

<blockquote class="evidence-conclusion"><p>For the shared receiving stations and cycles in this run, ΔSNR and Decode Outcomes described how the two complete transmitting stations compared under their respective operating environments.</p></blockquote>

<a id="sec-3-tx-benchmark-local-median"></a>

##### 2.2.2 Reference Neighborhood

The Reference is the cycle- and receiver-path median of one contribution from each active local transmitter identity inside the selected radius. It is a changing local baseline, not one fixed station, and it depends on the active membership and accuracy of their reported powers.

The contributing local transmitters are those reported by the same remote receiver during the same WSPR cycle. ΔSNR additionally requires that receiver to report the Target in that cycle. The Reference therefore represents the qualifying local transmissions observed at that receiver, not every nearby transmitter or every attempted transmission.

Inspect the local contributors, Joint Evidence Share and radius sensitivity. Report whether the Target tends to sit above, near or below the active local baseline for particular receivers, directions or times. A changed result can reflect the Target, the local pool or both.

Reported-power normalization removes the reported transmit-power difference from the SNR values of Joint Spots. It does not verify actual transmitter power, measure radiated power or correct unknown feedline losses. Sharing a remote receiver and cycle controls the receiving endpoint and timing, but nearby transmitters can still have different installations, terrain and propagation paths. A neighborhood containing only one contributing transmitter provides that transmitter’s value as its median.

Choose the primary radius before interpreting the result, and report alternative defensible radii as sensitivity analyses. For a confirmatory run, fix the band, filters, thresholds and primary evaluation scope beforehand and inspect whether the contributing neighborhood changed.

<blockquote class="evidence-conclusion"><p>For the selected band, window, receiver paths and cycles, the Target’s complete transmitting station showed the reported power-normalized ΔSNR and the reported Decode Outcomes relative to the contributing local transmitter neighborhood. This does not establish that its antenna is the displayed number of decibels better.</p></blockquote>

<a id="sec-3-1"></a>
<a id="sec-3-2"></a>
<a id="sec-3-rx-performance"></a>

#### 2.3 RX Performance

**Question answered.** Which transmitters did the Target receive, how consistently and at what successful SNR, and how did reception vary with direction, distance and time?

**The key value: Decode Rate.** The percentage of confirmed opportunities that the Target decoded. A confirmed RX opportunity concerns one exact transmitter identity on the selected band in one WSPR cycle: the Target decodes its signal, or another eligible receiver reports it while Target activity is also confirmed. A successful Target decode confirms both endpoints and counts even without another receiver's report. Another receiver's report alone does not establish that the Target was listening. [Section 7.3](#sec-7-performance) defines the classification.

**Minimum valid setup.** Use the exact Target reporting callsign and QTH, one band and a window with observable Target receiver activity. Keep the receive chain stable. Performance evaluates the complete receiving station without a Reference; it does not isolate one component.

**Read the evidence path.**

**1. Map: where is reception broad or consistent?** Segment color shows the **Station-balanced Decode Rate**: the mean of the qualifying transmitters' individual rates, with equal weight per identity. Markers and footer counts distinguish transmitters heard at least once from those heard only elsewhere. Read the percentage scale and station counts to locate directional patterns; map color does not measure receiver sensitivity. **Segment Inspector** selects directions and distances for all results below.

**2. Performance Evidence: how do reach, consistency and signal strength compare?**

| Figure | What to read and how to interpret it |
|---|---|
| **TX Stations Heard by Target at Least Once by Distance** | The percentage of qualifying transmitters heard at least once in each distance range. This describes reception breadth, not regular reception. Read it alongside Decode Rate. More time gives more chances to hear each station; a changing qualifying population can still move this percentage either way. |
| **RX Decode Rate by TX-Station Distance** | **Station-balanced Decode Rate** gives each transmitter's rate equal weight. **Opportunity-level Decode Rate** divides all successful decodes by all confirmed opportunities, so frequently observed transmitters have more influence. If the lines differ, inspect those transmitters and their counts before describing the whole population. |
| **Successful Target SNR by TX-Station Distance** | The median of the transmitters' median successful SNR values in each distance range, normalized to a common **30 dBm (1 W)** transmit-power basis using reported power. Less-negative values mean stronger successful reception relative to noise. Missed signals have no Target SNR here; compare this figure with Decode Rate before inferring better reception. |

**Check support.** Compare qualifying station counts with confirmed-opportunity counts. Many opportunities from a few transmitters give repeated observations of few paths; agreement across more transmitters has broader support. In the SNR figure, Min-Max spans the two station medians when two contribute; IQR spans the middle 50% of station medians with three or more. These describe spread, not confidence in a wider population.

**3. Temporal Evidence: when does reception change?** **Successful RX SNR Deviation over Time** compares successful reception on each transmitter path with that path's median successful SNR over the run. Above **0 dB** means stronger than its usual successful level; below means weaker. Follow the median and read **Evidence over Time** alongside it: station and opportunity bars show support, and the two Decode Rate lines show whether detectability changed too. Color shows observation concentration, not stronger reception; any Q1–Q3 band describes spread, not a confidence interval.

**Successful RX SNR Deviation by UTC Hour** and **Evidence by UTC Hour (1 h bins)** combine matching hours across dates. Look for a possible daily pattern, then inspect individual dates before calling it recurring. A missing SNR value is not zero signal strength.

**4. Station Insights: which paths explain the result?** Read each transmitter's Decode Rate with **Heard by Target** and **Heard by others only** counts. Select a typical path, an unusual one and any path supplying many opportunities. **Selected Station Evidence** shows that path's successful SNR on the common 1 W basis and its opportunity history, rather than the segment's deviations from each path's usual level. Check whether its changes resemble the wider pattern. **Drill-Down** verifies individual cycles: **Heard by others only** is a missed decode supported by another receiver while the Target was active. It also distinguishes externally confirmed successes from successes reported only by the Target; the latter are already included once in successes and opportunities.

**What to do next.** Broad reach with high Decode Rate indicates many paths heard consistently; broad reach with lower rates indicates intermittent reception. Limited reach with high rates means fewer paths were heard, but comparatively consistently. If successful SNR stays steady or rises while Decode Rate falls, weaker signals may have disappeared below the decoding threshold. Inspect the affected paths and repeat useful direction-, distance- or UTC-specific patterns in another suitable window.

RX Performance combines antenna, feedline, receiver, gain, filtering, decoder, local noise, interference and propagation. It does not directly measure receiver sensitivity, antenna gain, absolute noise or propagation mode. For a claim about one hardware change, use a controlled RX Benchmark or crossover rather than relying only on separated before-and-after Performance runs.

<p class="evidence-conclusion-label"><strong>Evidence-matched conclusion.</strong></p>

<blockquote class="evidence-conclusion"><p>For this Target receiver, band, UTC window and selected transmitter population, RX Performance describes at-least-once reach, Decode Rate within confirmed transmitter-cycles, successful-decode SNR and the geographic and temporal scope in which those observations appeared. State the weighting used, the station and opportunity support, and whether the pattern was broad, intermittent, directional, distance-dependent or recurring.</p></blockquote>

<a id="sec-3-tx-performance"></a>

#### 2.4 TX Performance

**Question answered.** Which active receivers heard the Target, how consistently and at what successful SNR, and how did the result vary with direction, distance and time?

**The key value: Decode Rate.** The percentage of confirmed receiver opportunities in which the Target was decoded. A confirmed TX opportunity concerns one exact receiver identity on the selected band in one WSPR cycle: it decodes the Target, or it decodes another qualifying transmitter while Target activity is also confirmed. A successful Target report confirms both endpoints and counts even if that receiver reports no other transmitter. Hearing the Target at another receiver proves Target activity, not that this particular silent receiver was listening. [Section 7.3](#sec-7-performance) defines the denominator.

**Minimum valid setup.** Use the exact Target callsign and QTH, one band and a window when the Target was operating. Keep the RF path, schedule and actual power stable, and report power accurately. Performance evaluates the complete transmitting station, not one isolated component.

**Read the evidence path.**

**1. Map: where is the Target heard?** Segment color shows the **Station-balanced Decode Rate**: the mean of the qualifying receivers' individual rates, with equal weight per identity. Markers and footer counts distinguish receivers that heard the Target at least once from those that heard only other qualifying signals. Read the percentage scale and receiver counts to locate the transmitted footprint and directional patterns. **Segment Inspector** selects directions and distances for all results below.

**2. Performance Evidence: how do reach, consistency and signal strength compare?**

| Figure | What to read and how to interpret it |
|---|---|
| **RX Stations Hearing the Target at Least Once by Distance** | The percentage of qualifying active receivers that heard the Target at least once in each distance range. This describes reach, not regular reception. Read it alongside Decode Rate and remember that the observation window and available receivers affect that reach. |
| **TX Decode Rate by RX-Station Distance** | **Station-balanced Decode Rate** gives each receiver's rate equal weight. **Opportunity-level Decode Rate** divides all successful Target reports by all confirmed opportunities, so frequently observed receivers have more influence. If the lines differ, inspect those receivers and their counts before describing the whole population. |
| **Successful Target SNR by RX-Station Distance** | The median of the receivers' median successful Target SNR values in each distance range, normalized to a common **30 dBm (1 W)** basis using reported Target power. Less-negative values mean stronger successful reports relative to receiver noise. Missed Target signals have no SNR here; compare this figure with Decode Rate before inferring improved performance. |

**Check support.** Compare qualifying receiver counts with confirmed-opportunity counts. Many opportunities from a few receivers describe those paths repeatedly; agreement across more receivers is broader evidence. In the SNR figure, Min-Max spans the two receiver medians when two contribute; IQR spans the middle 50% of receiver medians with three or more. These describe spread, not confidence in a wider population.

**3. Temporal Evidence: when does the transmitted result change?** **Successful TX SNR Deviation over Time** compares successful Target reports at each receiver with that path's median successful SNR over the run. Above **0 dB** means stronger than its usual successful level; below means weaker. Follow the median and read **Evidence over Time** alongside it: receiver and opportunity bars show support, and the two Decode Rate lines show whether detectability changed too. Color shows observation concentration, not stronger reports; any Q1–Q3 band describes spread, not a confidence interval.

**Successful TX SNR Deviation by UTC Hour** and **Evidence by UTC Hour (1 h bins)** combine matching hours across dates. Look for a possible daily pattern, then inspect individual dates before calling it recurring. A missing SNR value is not zero signal strength.

**4. Station Insights: which receivers explain the result?** Read each receiver's Decode Rate with **Target heard** and **Other signals heard only** counts. Select representative and unusual paths, including receivers supplying many opportunities. **Selected Station Evidence** shows that receiver's successful Target SNR on the common 1 W basis and its opportunity history, rather than the segment's deviations from each path's usual level. Check whether it follows the wider pattern or reveals a path-specific effect. **Drill-Down** verifies Target reports and receiver activity: **Other signals heard only** is a missed Target decode where that same receiver heard another qualifying signal while the Target was active. Target successes without another qualifying signal at that receiver are already included once in successes and opportunities; their separate provenance is not an extra total.

**What to do next.** Broad reach with high Decode Rate indicates many active receivers heard the Target consistently; broad reach with lower rates indicates a large but intermittent footprint. A persistent directional or distance pattern can be consistent with the installed antenna and terrain; a short improvement can reflect propagation or receiver availability. Stable successful SNR with falling Decode Rate can mean that only stronger reports remain. Check the affected paths and repeat useful patterns in another suitable window.

TX Performance combines transmitter, actual power, feedline, matching, antenna, terrain, remote receiver systems, noise and propagation. Reported-power normalization cannot correct an incorrect power report or an unmeasured feedline loss. It does not directly measure EIRP, efficiency, antenna gain or take-off angle. Use TX Benchmark when the question is whether one transmit path differs from another.

<p class="evidence-conclusion-label"><strong>Evidence-matched conclusion.</strong></p>

<blockquote class="evidence-conclusion"><p>For this Target transmitter, band, UTC window and selected active-receiver population, TX Performance describes at-least-once reach, Decode Rate within confirmed receiver-cycles, successful reported SNR and the geographic and temporal scope in which those observations appeared. State the weighting, receiver and opportunity support, reported-power basis and whether the pattern was broad, intermittent, directional, distance-dependent or recurring.</p></blockquote>

<a id="sec-outlier"></a>

#### 2.5 Find and Review Temporary ΔSNR Departures

**Question answered.** Did one exact `callsign + locator` path temporarily move above or below its stable local expected ΔSNR far enough to meet the configured departure, robust-score and baseline-stability requirements?

**This is an optional expert diagnostic tool, not a routine step intended for every operator or every Benchmark analysis.** Start with the ordinary Benchmark evidence path. Enable outlier reporting when a controlled Benchmark has enough Joint Spots around the period of interest and the temporary change serves the investigation. The detector reports intervals for expert review; it neither ranks the largest raw ΔSNR values nor explains their physical cause.

<a id="sec-outlier-1"></a>

##### 2.5.1 When to use this expert diagnostic

Use the detector only with Benchmark evidence. Its native evidence unit is a simultaneous **Joint Spot**, containing both Target and corrected Reference SNR and therefore a ΔSNR value. Only Target and Only Reference outcomes remain useful diagnostic context but cannot themselves qualify an event.

Look for repeated Joint Spots before, during and after the suspected change. The detector abstains when a reliable local baseline cannot be supported on both sides. An empty report can mean that the retained Joint Spots failed the configured requirements, or that local evidence was insufficient or unstable. It does not establish that the path was unchanged.

Enable **`Report ΔSNR outlier candidates`**, set the three expert controls in [Section 4.6](#sec-5-6), then run the analysis manually. Changing the toggle or a threshold marks the analysis definition as changed but does not automatically start another run.

<a id="sec-outlier-2"></a>
<a id="sec-outlier-3"></a>

##### 2.5.2 How detection works in practice

For each exact path, WSPRadar retains Joint Spots at their native WSPR-cycle times, then:

1. estimates expected local ΔSNR from robust summaries before and after a possible departure, excluding the candidate itself;
2. requires enough populated evidence on both baseline sides and agreement within the configured maximum;
3. groups nearby departures from that baseline with the same sign, using the path's observed evidence cadence;
4. applies the same absolute-departure, robust-score and sign-agreement rules regardless of duration; and
5. trims weak leading and trailing Joint Spots so that both ends individually meet the departure and robust-score thresholds.

Weaker Joint Spots may connect stronger ones inside an interval but cannot extend its outer boundaries. A failed broad candidate can be split at a supported return to baseline: a strong internal section is then tested without choosing a new, more favorable baseline.

Detection finishes before **Temporal Evidence** display aggregation. Changing a `1h`, `6h` or other display bin cannot create, merge, split or remove an event. Once path events qualify separately, contemporaneous events with the same departure sign may share a review card:

| Cross-path context | Meaning |
|---|---|
| **Path-specific** | One path. |
| **Directionally coherent** | Several paths in adjacent compass sectors. |
| **Scope-wide** | Several separated directions. |
| **Multiple paths** | Several paths, with direction unavailable for at least one contributor. |

This context does not change whether an individual path qualifies. [Section 7.6](#sec-7-outliers) explains the experimental detector, its evidence and principal qualification checks.

<a id="sec-outlier-4"></a>
<a id="sec-outlier-5"></a>
<a id="sec-outlier-6"></a>

##### 2.5.3 Read and investigate a reported event

Read the event card from its interval to the Joint Spots that support it:

| Report item | What it means and what to inspect |
|---|---|
| **Spot impulse**, **Short burst**, **Sustained excursion** | Temporal shape after boundary trimming. The classes use the same qualification thresholds and do not express different certainty. |
| Exact path and direction | Each path line identifies `callsign + locator` and direction; investigate that exact path and timeframe. |
| **Expected local ΔSNR** | The two-sided baseline calculated with the candidate excluded. |
| **Observed median ΔSNR** | The median of retained Joint Spots inside the reported interval. |
| **Largest single-cycle departure** | The greatest departure in magnitude from the baseline among retained Joint Spots, retaining its sign. This report/export value is distinct from the all-path temporal `*`. |
| **Chronological WSPR-cycle evidence** | For an event containing several Joint Spots, the table lists UTC time, path, direction, local baseline, ΔSNR and departure from baseline (residual). An impulse with one Joint Spot needs no duplicate evidence table. |

In the all-path temporal view, one `*` per review event selects the Joint Spot with the greatest absolute residual **among those that individually qualify**. An unsupported or nonqualifying episode peak cannot supply that marker, even when it supplies the reported **Largest single-cycle departure**.

**Inspect the path next.** The two actions for each exact path timeframe select the path, preload Drill-Down and open **`Outlier Focus`**:

| Action | Where it takes you |
|---|---|
| **`↓ Show in Station Insights`** | Station Insights, for the path's wider run history. |
| **`↓ Show Drill-Down Details`** | Directly to Drill-Down, for detailed inspection. |

The focus covers the complete supported pre-event baseline flank, guarded provisional episode and post-event baseline flank. It is clipped only to the completed analysis window and may exceed 24 hours. The focused ΔSNR plot shows each retained Joint Spot at its native time, rather than a bin median, IQR or density layer.

**Read the focus markers and guides together.** Identical `*` markers identify every Joint Spot in the current window that individually meets both configured departure and robust-z requirements as part of a reported candidate, including every such Joint Spot in a burst or episode. This differs from the single representative star in the all-path temporal view.

A muted **Focused episode** band identifies the selected reported episode. It spans its retained Joint Spots, with half one native evidence-unit width added at each end and clipping to the focus window so an impulse with one Joint Spot remains visible. The band is neither a confidence interval nor a measurement of physical-event duration.

The overlays show expected local ΔSNR, the before/after baseline values over their actual support intervals, symmetric robust-z guides at 1, 2 and 3 plus the configured qualifying threshold, and the configured absolute-departure boundary. All these guides belong to the **focused episode only**: other starred Joint Spots may have been assessed against different baselines and robust spreads. The lines are detector guides, not confidence intervals; crossing one line alone cannot qualify a candidate.

**Check what changed before assigning a cause.** Compare Target SNR, corrected Reference SNR and nearby one-sided outcomes: did one side drive the ΔSNR movement, did either signal approach the decode edge, and did pairability change nearby? Compare the interval with contemporaneous paths, station logs, switching schedules, gain or power changes, interference observations and independent measurements. The displayed first-to-last span covers retained Joint Spots; it does not establish uninterrupted behavior between them.

<a id="sec-outlier-7"></a>

##### 2.5.4 Adjust selectivity and preserve the result

Use the three controls according to their literal meaning; [Section 4.6](#sec-5-6) gives their exact operating reference.

| Change | Effect on reporting |
|---|---|
| Increase **`Minimum absolute ΔSNR departure (dB)`** | Requires a larger departure from the local baseline. |
| Increase **`Minimum robust z-score`** | Requires a larger departure relative to nearby robust variability. |
| Decrease **`Maximum pre/post baseline difference (dB)`** | Requires a more stable two-sided baseline. |

The opposite changes make reporting more permissive. The same three values apply to Spot impulses, Short bursts and Sustained excursions; duration provides no hidden discount.

For exploratory work, use candidates to identify intervals worth auditing and record threshold changes. For confirmatory work, fix and preserve the thresholds, Benchmark design, correction, path population, band and UTC scope **before** inspecting the result. Then test whether a comparable departure recurs in a separate suitably controlled run.

Report a **temporary local ΔSNR departure in the retained Joint Spots**, with its exact path, interval, sign, supporting Joint Spots and detector settings. The detector is descriptive: it does not calculate a p-value, correct for the number of searched paths or events, or determine the physical cause.

When reporting is enabled, preserve the active-scope findings with the analysis export. It adds a path-event summary and a chronological CSV of the contributing Joint Spots, linked by package-local Event and Path event IDs. The evidence table repeats path, direction and path-event class so it remains readable on its own. [Section 8.4](#sec-8-4) defines the two files and their conditional inclusion.

<a id="sec-3-9"></a>

---

<a id="sec-4"></a>

### 3. Strengthen and Communicate Your Result

A strong WSPRadar result combines a clear experiment, broad evidence and language that matches the actual observation.

<a id="sec-4-1"></a>

#### 3.1 Judge breadth, consistency and repeatability

Judge the result from the complete evidence picture:

* participating station identities;
* confirmed-opportunity counts for Performance or Joint Spot counts for Benchmark;
* agreement across stations;
* station-balanced and observation-level summaries;
* adjacent geographic segments;
* temporal views;
* Decode Outcomes;
* identity and locator quality;
* experiment control and repetition.

Evidence is **broader** when several identities and adjacent segments agree. It is **more internally consistent** when station-balanced, observation-level and time views tell a compatible story. It is **better controlled** when the selected playbook's operating requirements were followed and documented.

**Internal consistency and experimental repeatability are different.** Agreement among the station-balanced, observation-level, geographic and time views describes the evidence within one run. Repeating the experiment in another suitable window tests whether the observed pattern persists under new operating and propagation conditions.

When a pattern is concentrated in one station or short interval, inspect that contributor before drawing a broad conclusion. When station-balanced and observation-level summaries differ, check which stations contribute most observations. These are reasons to narrow or investigate the claim, not automatically to discard the run. WSPRadar does not combine evidence breadth, consistency and experimental control into a single proof grade; the counts, distributions and underlying rows remain available for that judgment.

The observed time, distance, direction, Decode Rate, successful-SNR or Delta-SNR pattern is the evidence. An explanation such as antenna directivity, a local-noise change, propagation mode, overload or an intermittent component is an interpretation. Match the wording to the observation first, then test the explanation through a controlled change, crossover, independent measurement or repetition.

<a id="sec-4-2"></a>

#### 3.2 Strengthen a result through repetition and control

Use an initial exploratory run to identify a possible pattern. Before a confirmatory repetition, freeze the direction, band, benchmark, filters, evidence thresholds, schedule and primary geographic or temporal evaluation scope, including `Maximum peer distance from Target (km)` as defined in [Section 4.4](#sec-5-4). Run alternative maximum distances as separately preserved sensitivity analyses rather than selecting only the most favorable scope after seeing the result.

When the result will support an important station decision:

* extend the observation window across the propagation states named in the conclusion;
* prefer multi-day evidence for statements spanning complete daily cycles;
* repeat the experiment on another day or propagation period;
* keep non-tested variables stable between repetitions;
* compare runs with the same direction, band, benchmark, filters and evidence thresholds;
* investigate any identity, locator or short interval that supplies a large fraction of the evidence;
* preserve setup notes so a later run can reproduce the station configuration.

Small observed differences become more useful when they recur across stations, time periods, adjacent segments and controlled repetitions.

TX and RX use different peer populations and opportunity definitions. When investigating station balance or an “alligator” pattern, align band, period, geographic scope and physical configuration as far as practical, then examine the two directions separately. Equal percentages do not imply equal transmit and receive capability, and a percentage difference alone does not diagnose the cause.

<a id="sec-4-3"></a>

#### 3.3 Write an evidence-matched conclusion

A minimum operator statement identifies the Target and, for Benchmark where applicable, the fixed Reference or local benchmark definition. It also identifies the TX or RX direction, band, UTC window, geographic scope, result type, displayed value and supporting station/evidence count.

For a technical report, use the complete checklist in [Section 8.3](#sec-8-3): retain the weighting and evidence counts, Benchmark Decode Outcomes, experiment conditions and correction, filters and thresholds, repetition and sensitivity analyses.

**Performance wording**

> For this Target, band, UTC window and selected peer population, report the displayed Decode Rate and name its weighting. Station-balanced Decode Rate is the average of the qualifying stations’ individual rates; Opportunity-level Decode Rate is the success fraction across all their confirmed opportunities. For RX, success means the Target decoded the remote transmitter; for TX, a remote receiver decoded the Target. State the qualifying-station and confirmed-opportunity counts, geographic scope and relevant temporal pattern.

A complete Performance statement can additionally say whether at-least-once reach was broad or limited, whether participation was consistent or intermittent, where distance or directional patterns appeared, whether a UTC-hour pattern recurred and how successful Target SNR, normalized for reported transmitter power in both RX and TX, behaved. Describe these as observed WSPR behavior of the complete station under the selected conditions, not as isolated gain, sensitivity or efficiency.

**Benchmark wording**

> For this Target, Reference, band, UTC window and selected segment, the station-balanced median ΔSNR favored the Target/Reference by the displayed amount among Joint Spots. Report the observation-level ΔSNR, Joint-station and Joint Spot counts, Joint Evidence Share and Decode Outcomes alongside it so that both joint and one-sided evidence remain visible.

For a controlled-setup result, name the complete paths compared and any crossover or calibration. For an independent Reference station, state that complete installed stations and their environments were benchmarked. For a Reference Neighborhood, state the radius and changing local-median Reference definition.

Match the design name to the quantity being described:

* A **controlled setup** compares the documented local paths.
* An **independent-station comparison** compares complete installed stations and their environments.
* **Reference Neighborhood (Local Median)** compares the complete Target station with the median of the contributing nearby peers inside the selected radius under the observed conditions.
* A directional result describes the observed WSPR paths and participating stations rather than an absolute radiation pattern.
* Benchmark map colors use a run-scaled, symmetric dB color bar: blue favors the Reference, red favors the Target and `0 dB` is equality. Use the numerical color-bar values when comparing maps from different runs.

Use terms such as "observed difference," "favored in the selected evidence," "conditional reach" and "complete installed station comparison." Reserve isolated antenna gain, efficiency, receiver sensitivity, causation and statistical significance for experiments that actually measure or test those quantities.

The complete supported/unsupported wording reference is in [Chapter 8](#sec-8).

<a id="sec-4-4"></a>

#### 3.4 Preserve the run and its context

Select the geographic scope and station evidence that support the conclusion, then use `Prepare All Results for Download` followed by `Download Prepared Results`. The ZIP contains the completed run’s configuration, metadata, processed evidence, applicable tables and high-resolution figures. Preparing a package does not save it to your computer. Saving only a configuration or sharing an analysis link preserves settings, not the original evidence.

Keep concise station notes with the ZIP: the antenna and feedline arrangement, switch/splitter topology, hardware and software, measured/reported power, schedule and path assignments, calibration, weather, faults and deliberate changes. The complete record checklist is in [Section 8.3](#sec-8-3).

WSPRadar can preserve the configured analysis and processed evidence, but it cannot infer every physical detail of the station. Combining the export package with concise station notes makes comparison and reproduction substantially stronger. [Chapter 8](#sec-8) documents the exact export contents and remaining reproducibility boundaries.

<div style="page-break-before: always;"></div>

<a id="part-ii"></a>

## Part II: Controls and Troubleshooting

Use this part as an operating reference while setting up, repeating or diagnosing an analysis. It documents the exact controls, defaults, saved behavior and scientific consequences that affect the operator.

Optional expert use of Benchmark ΔSNR outlier detection is introduced in [Section 2.5](#sec-outlier). [Section 4.6](#sec-5-6) documents its controls; its scientific overview is in [Section 7.6](#sec-7-outliers).

<a id="sec-5"></a>

### 4. Controls and Configuration

WSPRadar distinguishes controls that change the retained scientific evidence from controls that only change how completed evidence is inspected.

| Control class | Effect | Saved? | Rerun required? |
|---|---|---|---|
| **Scientific controls** | Change identity, band, time, Reference design, eligibility, normalization, filters, thresholds or geographic population. | When applicable | Yes; the previous result is cleared |
| **View controls** | Change the active inspection scope, selected station, evidence visibility or display aggregation without reclassifying retained evidence. | Supported durable choices only | No |
| **Temporary interface choices** | Change only the current on-screen arrangement, temporary table filters, documentation visibility or a prepared download. | No | No |

Versioned configurations store the applicable scientific settings and supported durable view choices. Exact calculations are defined in [Chapter 7](#sec-7); [Section 8.4](#sec-8-4) explains how the export preserves settings and evidence. The formal JSON Schema is authoritative for the exhaustive saved-configuration field contract.

<a id="sec-5-1"></a>

#### 4.1 Workflow controls

| Control | What it does | Important behavior |
|---|---|---|
| **`EN` / `DE`** | Changes the display language. | A completed result is rendered again from its retained evidence without another analysis. When no completed result exists, changing language does not restart the analysis automatically; use Run to start it again. Missing or expired evidence also requires an explicit new run. |
| **`Input view`** | Switches between `Guided` and `Classic`. | Both expose the same scientific configuration. The chosen editor is not saved. |
| **`Load Demo`** | Loads a maintained historical profile. | Loading does not start an analysis. Filter, evidence-threshold and result-view changes retain the demo context; changing the experiment definition detaches it from the demo. |
| **`Load Config`** | Loads a versioned JSON `.config`. | Invalid identities, dates, choices, ranges, duplicate fields and unsupported schema versions are rejected rather than guessed. |
| **`Save Config`** | Saves the applicable scientific inputs and supported durable view settings from the terminal Review panel in Guided and Classic. | The file stores absolute UTC boundaries but not result rows, external experiment notes or transient table filters. Saving remains unavailable until the Question and, for a Benchmark, the Benchmark design are complete. |
| **`Run RX Analysis` / `Run TX Analysis`** | Runs the selected Performance or Benchmark result from the terminal Review panel in Guided and Classic. | Guided shows Run only when the applicable setup steps are valid and the terminal Review panel is available. In Classic, Run remains available to identify incomplete or invalid fields with local corrective guidance. In both views, analysis starts only after the required inputs and any Reference location choice are resolved. Changing a scientific control after a run clears the result and requires a new run. |
| **`Prepare All Results for Download`** | Builds the current export package. | Uses the completed evidence and current inspector selections. |
| **`Load full documentation` / `Hide full documentation`** | Shows or hides the complete web manual. | Presentation state only. |
| **`Prepare PDF`** | Builds the selected-language manual as PDF. | The full web manual does not need to be open first. |

In Guided, `Continue` checks the current setup panel and opens the next panel once its required inputs are valid. Correcting a field clears its error; correcting all errors in that panel also clears its error summary. An earlier unsuccessful attempt does not mark later, unattempted panels as invalid. The final Run action checks the complete configuration again before starting the analysis.

**Keyboard navigation.** In Guided and Classic, `Tab` moves forward through the native input controls and actions; `Shift+Tab` moves backward. The separate `?` help icons are mouse-only and never become a tab stop; focusing an input does not open a help overlay. In Guided, pressing forward `Tab` at the end of the active setup panel commits the current edit and validates that panel, just like `Continue`. If its inputs are valid, the next panel opens and its first input receives focus; otherwise the current panel stays open and its first invalid field receives focus. Native keyboard behavior within controls and backward navigation with `Shift+Tab` remain unchanged. At the end of setup, focus moves to the Review heading, then to Run on the next `Tab`; this keyboard transition does not start an analysis automatically. If `Continue` or Run reports invalid inputs, focus moves to the first invalid field so you can correct it directly.

Both input views finish with the same terminal configuration summary. Its **`Review — ready to run ✓`** state places `Run RX Analysis` / `Run TX Analysis` and `Save Config` inside that panel only after the configuration is valid. The Review panel remains open while the run starts and after it finishes, and the run-status panel remains open when it reaches **`Complete`**. Classic does not automatically collapse any configuration panel when either an ordinary or demo analysis starts; operators can still collapse or reopen individual panels manually. Guided may continue to compact earlier completed steps, but its terminal Review panel remains open.

After loading a demo in Guided, `Walk me through the setup` opens the setup steps for review. `Skip to review and run` opens the terminal Review panel and immediately starts the analysis with the current valid settings; no second click on `Run RX Analysis` / `Run TX Analysis` is needed. The shortcut remains unavailable while required settings are incomplete or an analysis is already in progress. Loading the demo itself still does not start an analysis.

After an accepted Run action, the page moves to the processing-status panel below Review. As soon as the first map image is ready, it moves to that result while Segment Inspector and Drill-Down data continue preparing automatically. The status reaches **`Complete`** only after all result views are ready. Each automatic move occurs once per submission; scrolling or navigating elsewhere while waiting cancels the move to the map. Result-view interactions and redisplaying a completed run do not restart these automatic moves.

**Current configuration format.** Only the current saved-configuration schema and public-URL contract are accepted; retired aliases, fields and earlier input formats are rejected without migration. Saved files preserve the inputs and durable view choices applicable to the selected analysis. Invalid or unsupported files are rejected rather than silently reinterpreted. The formal JSON Schema (`config/wspradar-config.schema.json`) is the authoritative exhaustive saved-configuration contract; [Section 8.4](#sec-8-4) describes the exported configuration and evidence files. Loading or saving a configuration does not create an additional result; only the selected Performance or Benchmark analysis is run.

**Demo context lifecycle.** A loaded demo keeps its visible context when only population filters, evidence thresholds, Inspector scope or other result-view controls are changed, so an adapted view can still be interpreted against the example from which it began. Changing the Question or direction, Target callsign or QTH, band, measurement window, Benchmark design or identity, neighborhood radius, or correction intent/value removes the demo metadata and profile identity from later saves because the setup no longer represents that documented experiment. Any scientific edit also ends exact-demo cache identity, even when the explanatory demo context remains visible. A population- or evidence-changing scientific edit clears any preselected Performance and Benchmark Station Insights identity; the path may no longer exist in the new result. Result-view-only controls do not clear that selection.

**Demo data reuse.** Running an unchanged demo retrieves any missing database query results and stores validated rows on the app server's disk. Later runs reuse matching entries without automatic expiry, including across sessions and app restarts while that disk is retained. A changed query or incompatible cache format, or missing or damaged files, requires retrieval again. Starting the app or loading a demo does not preload its data. Reuse preserves the retrieved database data rather than automatically incorporating later database corrections; each run still performs the analysis with the current application code.

<a id="sec-5-2"></a>

#### 4.2 Question, Target and measurement-window controls

Classic presents the scientific setup in a question-led order. The first panel, **`Question`**, requires one of four complete analysis choices: `RX Performance`, `TX Performance`, `RX Benchmark` or `TX Benchmark`. This single choice sets both the RX/TX direction and whether the run produces stand-alone Performance evidence or a Target-versus-Reference Benchmark. The second panel, **`Target and measurement window`**, then collects the existing Target identity, QTH, band and absolute UTC interval. A Benchmark adds **`Benchmark design`** next. Both result types then show **`Optional Filters, scope and evidence`** followed by the terminal Review panel, so Performance has four Classic panels and Benchmark has five.

| UI label | Default | What it controls |
|---|---|---|
| **Question** | none; required | One of `RX Performance`, `TX Performance`, `RX Benchmark` or `TX Benchmark`; sets direction and result type together. |
| **Target callsign (receiver under test)** / **Target callsign (transmitter under test)** | blank | Exact database reporting identity. Standard callsigns, valid `/` variants, letter-only reporting identifiers and one optional terminal alphanumeric hyphen suffix are accepted. |
| **Target QTH (4 or 6 characters)** | blank | Target grid-4 matching, map center, geometry and local-radius origin. |
| **Operating Band** | `20m` | Exactly one of `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` or `23cm`. |
| **UTC measurement window** | fixed 24-hour window ending at the current UTC minute | The absolute evidence interval used by the run. |
| **Start Date/Time (UTC)** and **End Date/Time (UTC)** | the effective default window | Dates begin in 2008; one run is limited to 31 elapsed days. Entered times use minute precision and are preserved without rounding to 15-minute boundaries. |

Use the callsign or reporting identifier exactly as uploaded. In schematic form, `CALL`, `CALL/1`, `CALL/2`, `CALL/P`, `CALL/QRP` and `CALL-1` are distinct exact identities; WSPRadar does not apply hidden prefix or suffix matching. These examples describe matching syntax, not whether a particular on-air identity is assigned or permitted.

A four-character Maidenhead locator identifies a broad grid square; six characters identify a smaller subsquare. Performance and Benchmark select Target database rows from the exact callsign plus the first four characters of Target QTH. The full configured QTH still anchors map, distance, azimuth, solar and local-neighborhood calculations.

<a id="sec-5-3"></a>

#### 4.3 Benchmark-design controls

For `RX Benchmark` and `TX Benchmark`, Classic displays a third panel named **`Benchmark design`** and offers:

- `Reference Setup/Station`
- `Reference Neighborhood`

Guided provides concise help for each Reference choice and separate help for the Reference callsign and Neighborhood Radius fields, explaining what to enter and what each field controls. In Classic, the help beside **Benchmark design** explains both Reference choices regardless of the current selection. The Reference callsign and Neighborhood Radius fields have their own help for entry guidance. Reference Neighborhood uses the Local Median described in the choice help; set the geographic extent with Neighborhood Radius.

Selecting RX or TX Benchmark without an existing design preselects **Reference Setup/Station** in Guided and Classic. An existing Reference Setup/Station or Reference Neighborhood choice is preserved.

Classic omits the **`Benchmark design`** panel entirely for `RX Performance` and `TX Performance`, because Performance has no Reference. The terminal Review panel appears after the shared **`Optional Filters, scope and evidence`** panel. On Run, invalid or incomplete fields are marked locally with red feedback and corrective guidance; correcting a field clears its issue. Database lookup failure is reported separately from an invalid callsign or an empty report window. Performance and Benchmark are mutually exclusive result types: one run produces only the selected result. [Section 8.4](#sec-8-4) describes the settings, evidence and figures included in the export.

| UI label | Default / range | Applies to | Scientific effect |
|---|---|---|---|
| **Is there an established Target–Reference offset?** | `No established offset — use 0.0 dB` | Guided Reference Setup/Station | Distinguishes no established correction, use of one established correction, and a deliberate offset-establishment run. |
| **Reference-side SNR correction (dB)** | blank = `0.0`; `-99.9` to `+99.9 dB` | Benchmark | Added to Reference SNR before Target-minus-Reference ΔSNR is calculated. Enter decimal points, for example `1.2`. |
| **Reference callsign** | blank | Reference Setup/Station | Exact Reference reporting identity. |
| **Reference location** | resolved from the selected database | Reference Setup/Station | One observed grid-4 resolves automatically; choose explicitly when several are reported. No separate manual Reference locator is required. |
| **Neighborhood Radius (km)** | `100`; 10–250 km in 10 km steps | Reference Neighborhood | Defines the local Reference pool around Target QTH. |


Switching the Question or Benchmark design hides controls that do not apply. Saved configurations contain only the inputs applicable to the selected analysis. Values whose scientific meaning changes under the new design are cleared rather than reinterpreted.

Enter only the exact Reference callsign; Target QTH is the sole manually entered analysis locator and remains the origin for map, distance, azimuth, solar and neighborhood geometry. Reference location discovery runs for the selected role, band, effective UTC window and database. One observed grid-4 resolves automatically; multiple candidates require your choice and show their full locator variants, report counts and first/last report times. A successful lookup with no qualifying reports is distinct from a source error. The same database supplies the ensuing analysis; a resolved grid-4 is retained with the saved analysis definition.

For TX Reference Setup/Station, entering one callsign with a slash and one without shows a non-blocking reminder to check the message patterns. This applies even when the base callsigns differ. The input check cannot verify firmware settings or transmission schedules; follow the controlled-TX guidance in [Section 2.2.1](#sec-3-tx-benchmark-simultaneous). This reminder does not apply to RX reporting identities, Performance or Reference Neighborhood.

One grid-4 is not proof of one physical site. Different fine locators within it remain visible as reported variants; a coarse/fine combination may be geographically compatible without proving one transmitter or receiver. Discovery does not merge the remote peer identities used for pairing.

Different reported grids can reflect separate sites or incorrect database metadata; the reported locators do not prove which explanation applies. If no eligible Target reports match the entered Target QTH, review the inputs; the analysis origin is never changed automatically.

##### Reference-side SNR correction sign

A positive correction increases corrected Reference SNR and therefore reduces Target-minus-Reference ΔSNR. Enter a measured `target - reference` calibration offset with the same sign. For example, a common-input calibration of `+1.6 dB` is entered as `+1.6 dB`. [Section 7.2.2](#sec-7-benchmark-delta) defines the equations.

The correction applies to the selected Reference receive/transmit path, or each local contribution before the Reference Neighborhood (Local Median) is formed.

| Guided choice | Meaning | Required value |
|---|---|---|
| **No established offset** | No defensible correction has been established. | `0.0 dB` |
| **Use an established correction** | Apply a documented signed additive offset valid for this setup. | Enter the established value |
| **Set up an offset-establishment run** | Collect evidence from which an offset can be derived; WSPRadar does not choose or calculate the offset automatically. | `0.0 dB` during the establishment run |

A constant correction cannot repair clipping, unstable AGC, intermittent routing, frequency-dependent response or incorrect power reporting. Controlled-setup calibration should use a common input or calibrated reference plane. A geographically separated Reference Station can support only a repeatable baseline for that particular pair, band and setup — not an absolute calibration. [Appendix C](#sec-reference-snr-calibration) gives the practical procedure.

For Reference Neighborhood (Local Median), use `0.0 dB` when no independently justified correction has been established. A nonzero correction requires a documented reason why the same additive offset applies to the contributing Reference population under the selected conditions. Adjusting the correction until the neighborhood matches the Target does not establish calibration. A common offset cannot correct different unknown errors in individual neighboring stations.

<a id="sec-5-4"></a>

#### 4.4 Filters and evidence thresholds

Guided and Classic use the same panel name, **`Optional Filters, scope and evidence`**, for these controls. Adjusting these settings is optional; their displayed values still apply. Guided always shows the applicable fields inside that step; there is no separate preset-choice gate. Untouched setups initialize the visible fields from the result-specific defaults below; loaded configurations and demos populate the same visible fields with their stored values. Displaying those values does not itself edit them or detach demo context. The displayed filter, scope and evidence settings apply even if you leave this panel unchanged.

Choose filters and thresholds from the intended population and evidence floor before a confirmatory run. Changing them after inspecting the result creates a different analysis and should be retained separately.

| Control | Default | Applies to | Effect and use |
|---|---|---|---|
| **Exclude Special Callsigns Q, 0, 1** | Performance on; Benchmark off | all results | Excludes remote peer callsigns beginning with `Q`, `0` or `1`: transmitters in RX analyses and receivers in TX analyses. Target and Reference stations, including Reference Neighborhood reference contributors, remain eligible under this filter. The prefix rule does not establish whether a station carries telemetry. Retain beacon/telemetry-like identities when they are part of the question; exclude them when the intended population is ordinary amateur activity. |
| **Exclude Moving Stations** | Performance on; Benchmark off | mapped peers | Excludes callsigns reporting more than one grid-4 in the otherwise eligible global population. Use Drill-Down to distinguish movement from bad locator data. |
| **Solar state at Target QTH** | `All 24h` | all results | Keeps `Daylight (Elev > +6°)`, `Nighttime (Elev < -6°)`, `Greyline (-6° to +6°)` or all cycles according to Target-QTH solar elevation. |
| **Maximum peer distance from Target (km)** | `22000`; choices `2500`, `5000`, `10000`, `15000`, `20000`, `22000` | all results | Removes peers at or beyond the selected distance from analysis, processed artifacts and exports. Target-Active gating may still use out-of-scope evidence solely to establish Target operation. |
| **Minimum joint evidence per station** | `1`; range 1–50 | Benchmark | Requires at least the selected number of Joint Spots before an exact station identity contributes its median ΔSNR. The same numeric floor applies separately to Only Target and Only Reference counts; one-sided observations do not satisfy the Joint requirement. |
| **Minimum confirmed opportunities per station** | `5`; range 1–100 | Performance | Requires at least the selected number of confirmed opportunities — successful Target decodes or Misses — before an exact peer identity contributes. Low values increase coverage but make rates coarse and weakly supported. |
| **Minimum qualifying stations per map segment** | `1`; range 1–10 | all maps | Requires broader identity support before a segment is drawn. |

The two exclusion defaults apply only to untouched interactive setups. A Performance setup starts with both exclusions on; a Benchmark setup starts with both off. After the operator changes either exclusion manually, that explicit value persists across Question changes rather than being replaced by a result-type default. Loaded configurations, demos and analysis URLs likewise retain their explicitly saved choices.

`Maximum peer distance from Target (km)` limits the analysed population after the database rows have been retrieved, so reducing it does not avoid the database row limit. A smaller Reference Neighborhood radius and `Exclude Special Callsigns Q, 0, 1` can reduce the population retrieved for some analyses; [Section 5.6](#sec-6-6) covers oversized requests.

<a id="sec-5-5"></a>

#### 4.5 Map, inspector and export controls

| Control | What it changes | Saved? | Reruns analysis? |
|---|---|---|---|
| Segment distance and direction | Active geographic inspection scope | Separately for Performance and Benchmark | No |
| `Heard only by other stations.` / `Only other signals heard.` | Visibility of Performance peers with only counter-evidence | Yes | No |
| `Include Unpaired Evidence` | Visibility of Benchmark identities represented only by exclusive or asynchronous evidence | Yes | No |
| Selected station row | Selected Station Evidence and selected Drill-Down identity | Exact `callsign + locator` identities: normally at most one per result type; multiple Benchmark identities when outlier reporting is enabled | No |
| Segment time aggregation | Chronological Segment Inspector temporal view; choices adapt to the run duration | Yes | No |
| Selected-station time aggregation | Chronological selected-path view; choices adapt to the run duration | Yes | No |
| **`Zoom window`**, **`Center date (UTC)`**, **`Center time (UTC)`**, **`← Earlier`**, **`Later →`**, **`Outlier Focus`** and **`Filter table`** | Optional native-time Drill-Down plots and centered table interval for exactly one selected station; table filtering affects displayed rows only | No | No |
| `Prepare All Results for Download` | Export package and current inspection selections | n/a | No |

Read-only evidence tables with more than 150,000 displayed rows load rows as you scroll. In this mode, the browser table's built-in search and direct CSV download are unavailable. Use **`Filter table`** to narrow the displayed Drill-Down rows and **`Prepare All Results for Download`** to obtain the reproducibility package. **Station Insights** remains selectable so you can open a station's evidence.

The chronological choices and the default used when no explicit compatible saved choice exists are:

| Complete run duration | Offered bins | Default |
|---|---|---|
| Up to and including 6 hours | `2m`, `10m`, `30m`, `1h`, `2h`, `3h`, `6h` | `10m` |
| More than 6 hours through 24 hours | `2m`, `10m`, `30m`, `1h`, `2h`, `3h`, `6h` | `30m` |
| More than 24 hours through 7 days | `30m`, `1h`, `2h`, `3h`, `6h`, `12h`, `24h` | `12h` |
| More than 7 days | `1h`, `2h`, `3h`, `6h`, `12h`, `24h` | `12h` |

The `2h` choice is therefore available for every run duration. Chronological aggregation never changes opportunity classification, Benchmark pairing or the fixed one-hour UTC-folded profiles. Empty Performance time or distance bins remain missing evidence rather than synthetic zero-rate observations.

**Choose a focus window.** Drill-Down zoom is transient and is available only for exactly one selected station. Choose **`Off`**, or a complete `1h`, `3h`, `6h`, `12h` or `24h` interval. **`Center date (UTC)`** and **`Center time (UTC)`** select the center of that interval; WSPRadar derives its exact start and end, moves the complete interval against a run boundary instead of shortening it, and lets **`← Earlier`** or **`Later →`** step by one complete selected window. The resolved bounds appear on one line as **`Selected window: {start} to {end} UTC`**. The zoom restricts the focused figures and Drill-Down table; **`Filter table`** then changes only the displayed table and never the focused plots or completed analysis.

**Read the individual observations.** Its metric plot is deliberately not a two-minute aggregate: Benchmark shows one actual ΔSNR dot per retained Joint Spot at its canonical cycle time; Performance shows the actual normalized Target SNR of each successful confirmed opportunity at its canonical cycle time. These are individual retained scientific evidence units after WSPRadar's consolidation, matching and filters, not untouched provider rows. No bin median, IQR, density background, colorbar, full-run median or UTC-hour-folded metric panel is drawn in the focused view. The companion Performance outcome or Benchmark coverage view may retain its chronological aggregation, while Segment and full-window Selected Station Evidence remain density-based aggregated views.

**Open an outlier focus.** An outlier action preloads **`Outlier Focus`** over the complete supported pre-event baseline flank, guarded provisional episode and post-event flank, clipped only to the completed analysis window and allowed to exceed 24 hours. Candidate provenance remains attached while the operator moves to a manual fixed window.

**Read markers and the episode band.** In a focused Benchmark plot, identical `*` markers identify every Joint Spot in the current window that individually meets both configured departure and robust-z gates as part of a reported candidate; a muted **Focused episode** band distinguishes the selected reported episode. The band covers its reported retained-evidence interval with half one native evidence-unit width of padding at each end, clipped to the focused window so an impulse remains visible. It is a selection cue rather than a confidence interval or physical-duration measurement.

**Read the detector guides.** Expected local ΔSNR, time-limited pre/post flank baselines, robust-z guides at 1, 2 and 3 plus the configured qualifying threshold, and the configured absolute-departure boundary belong only to the focused episode; other starred candidates can have different baselines and robust spreads. Robust-z and departure lines are detector guides rather than confidence intervals; crossing one line alone does not satisfy the detector's separate support, stability, event and agreement requirements.

**Save the evidence.** Manual and outlier-linked focus state stay outside the analysis definition, saved configuration and public URL. When focus is active, the export can add its separate figures without replacing the ordinary full-run selected-station figures. Export contents are defined in [Section 8.4](#sec-8-4).

<a id="sec-5-6"></a>

#### 4.6 Benchmark outlier-detection controls

Benchmark ΔSNR outlier detection is an optional expert analysis of retained **Joint Spots** at their native WSPR-cycle times. Detection runs separately for every exact peer `callsign + locator` path and is independent of the selected Temporal Evidence display bin. One-sided evidence cannot supply a missing ΔSNR. [Section 2.5](#sec-outlier) explains operation and interpretation; [Section 7.6](#sec-7-outliers) explains the experimental method and its limits.

| Control | Default / range | Method symbol | Scientific effect |
|---|---|---|---|
| **`Report ΔSNR outlier candidates`** | off | — | Enables the optional detector and Outlier Report for Benchmark results. When it is off, WSPRadar adds no outlier detection, fields, markers, report semantics or outlier export metadata to the result. |
| **`Minimum absolute ΔSNR departure (dB)`** | `6.0`; `0.1`–`100.0 dB` inclusive | $D_{\min}$ | Requires the event's median residual, and every reported boundary anchor, to depart from the local baseline by at least this magnitude. |
| **`Minimum robust z-score`** | `3.0`; `0.1`–`100.0` inclusive | $Z_{\min}$ | Requires the event median and every reported boundary anchor to meet this absolute robust local-variability score. The score is descriptive, not a calibrated probability or conventional Gaussian significance level. |
| **`Maximum pre/post baseline difference (dB)`** | `3.0`; `0.1`–`100.0 dB` inclusive | $H_{\max}$ | Rejects a candidate when the pre-event and post-event flank medians differ by more than this magnitude, so an unstable or shifted baseline is not reported as a temporary excursion. |

The departure and baseline-difference comparisons use a fixed `0.01 dB` tolerance, as explained in [Section 7.6.3](#sec-7-outlier-qualification); the configured thresholds and internal evidence values remain unrounded. The robust z-score comparison has no such tolerance.

The default combination prioritizes large absolute movements: the 6 dB gate sets the nominal floor, while the robust z-score gate still requires that movement to be large relative to the path's local robust variability.

The toggle and three thresholds are saved when applicable. Changing any of them marks the configuration as changed but does not automatically start an analysis; calculate a new result with the normal direction-specific **`Run RX Analysis`** / **`Run TX Analysis`** action. All three thresholds apply unchanged to Spot impulses, Short bursts and Sustained excursions. There is no duration bonus or weaker threshold for a longer event. Lowering $D_{\min}$ or $Z_{\min}$, or increasing $H_{\max}$, makes reporting more permissive; the opposite choices make it more selective. For confirmatory use, set and record the thresholds before inspecting the candidate events rather than tuning them until a desired event appears.

<a id="sec-6"></a>
<a id="sec-5-7"></a>

### 5. Troubleshooting and Data Quality

Confirm the run definition before changing filters or thresholds. A wider scope can retain more evidence, but it cannot repair a wrong identity, band, time window or physical schedule.

<a id="sec-6-1"></a>

#### 5.1 Confirm the run definition first

1. **Target identity:** exact callsign or reporting identifier, including suffix.
2. **QTH:** configured locator and the first four characters actually uploaded.
3. **Band:** one exact selected band and actual operating band.
4. **UTC evidence window:** exact effective start and end shown in the controls.
5. **Actual operation:** Target transmission/reception and spot uploading.
6. **Reference operation:** exact Reference identity and overlapping uptime for Benchmark.
7. **Design mechanics:** clock synchronization, simultaneous TX frequency placement, signal routing, actual and reported power.

Only after these checks should you change evidence thresholds, exclusions, solar state or geographic scope.

<a id="sec-6-2"></a>

#### 5.2 Diagnose by symptom

An empty-result notice reports the scope and evidence parameters captured for the completed run, not subsequently edited controls. It separates an observed diagnostic from its configured requirement: for example, “highest observed: `3` confirmed opportunities” and “required: at least `5` per station.” A configured minimum is never presented as an observed count, and an observed maximum is shown only when WSPRadar actually calculated and retained it. For Performance, Target-only successes are confirmed opportunities and contribute to station thresholds; their provenance count is a subset of successes, not an additional total.

| Symptom | Next checks |
|---|---|
| **No exact Target/source evidence was returned** | Check exact identity/QTH/band/window, actual operation, strict `code = 1` or historical-fallback status, and upstream availability. This is an input/source-evidence state, not evidence that configured filters were too narrow. |
| **Source evidence was returned, but filters or scope retained none** | Review the displayed station exclusions, solar state and maximum peer distance together with the completed run window. The notice says only that the applied filters and scope left no retained evidence; sparse operation or coverage can also contribute. |
| **Performance identities remain, but no station meets the confirmed-opportunity requirement** | Compare the displayed observed station count and highest confirmed-opportunity count with the configured minimum confirmed opportunities per station. Empty maps, Inspectors and tables are omitted rather than displayed as zero-valued results. |
| **Performance stations qualify, but no map segment meets its station requirement** | Keep and inspect the available station-level evidence. Only segment-dependent output is absent; compare its station support with the configured minimum qualifying stations per map segment. |
| **No qualifying Benchmark result remains** | Review the configured Joint-evidence requirement, minimum qualifying stations per map segment, filters and scope. WSPRadar reports those applied requirements but does not invent observed Benchmark maxima that the pipeline did not calculate. |
| **Benchmark has no ΔSNR** | Check shared remote peers in overlapping cycles, Reference uptime, clocks, schedule mapping, joint threshold, filters and scope. |
| **Benchmark has ΔSNR but little pairable evidence** | Read Joint Evidence Share and Decode Outcomes; check Reference uptime, power, thresholds and scope. Inspect which stations and times contribute Joint Spots versus one-sided outcomes, and limit the ΔSNR interpretation to the Joint subset. |
| **Performance has very few peers** | Check independent network activity, minimum confirmed opportunities, exclusions, solar state, time window and maximum peer distance. |
| **Many Performance successes lack external confirmation** | A valid Target decode itself confirms both endpoints. These Target-only successes enter Decode Rate once; their separate provenance count is not added again. Without a Target decode or the required external endpoint-activity evidence, the peer-cycle remains unknown and excluded. |
| **`Only Reference = 0`** | Check Target-active conditioning, thresholds and active scope; zero can be correct. |
| **Unexpected Reference Setup/Station ΔSNR sign** | Verify physical A/B mapping, Target/Reference order, correction sign, actual/reported power and calibration. Reconcile one path in Drill-Down. |
| **Local result changes with radius** | Inspect local contributors and report radius sensitivity rather than selecting only the most favorable radius. |
| **Run stops because the source result is too large** | Shorten the UTC window. `Exclude Special Callsigns Q, 0, 1` or a smaller Reference Neighborhood radius can reduce relevant source queries; maximum peer distance cannot because it is applied after retrieval. |
| **Recent spots appear incomplete** | Allow about five minutes after the final cycle, then check upload and upstream status. |

An upstream-data problem changes what the source supplied. An experiment-design problem changes whether the retained evidence answers the intended question. Diagnose and report them separately.

<a id="sec-6-3"></a>

#### 5.3 Callsign and locator checks

Performance and every Benchmark design match Target database rows by exact callsign plus Target QTH grid-4. A Target uploading `JN37` while configured as `JN38` does not match.

Reference Setup/Station uses the exact Reference callsign plus the grid-4 resolved from the selected database period. Discovery uses the Reference role (RX or TX), band, effective UTC window and selected data source. One reported grid-4 resolves automatically; several require an explicit choice. Full reported locator variants, report counts and first/last report times support that choice. The location is a database selector, not a verified physical site. Reference Neighborhood selects its contributors geographically.

WSPRadar does not reconstruct a compound callsign from Type 2 and Type 3 messages and does not infer a missing locator. Check the selected data source for both exact identities and their intended reported grid-4 values. If one identity is missing, appears only without the required locator, or is stored under a different grid-4, simultaneous Reference Setup/Station cannot match it merely because another database or map display looks correct.

Callsigns must satisfy the documented 3–15-character reporting-token rule. Locators must contain four or six valid Maidenhead characters. Syntax validation does not prove legal assignment, physical location or actual operation. Peer identity is exact `callsign + full reported locator`; stale or changing locators can split or move one physical station.

<a id="sec-6-4"></a>

#### 5.4 Historical decode-code fallback

WSPRadar first requests WSPR-2 rows with `code = 1`. If that strict request returns no Target-side evidence and the entire selected period is before 1 January 2022 at 00:00 UTC, it retries without the predicate for historical compatibility and reports the fallback in run status. Periods ending exactly at that boundary, crossing it or lying after it keep the strict filter throughout. The fallback broadens selection and can differ between Performance and Benchmark.

WSPR-2 is the standard WSPR mode with two-minute transmission cycles; `code` is the database's recorded mode information. Older database records may have missing or ambiguous mode information, and historical compatibility can include observations whose physical transmission mode cannot be established. The cutoff is a compatibility policy, not a verified date when all database mode information became reliable. Historical `code = 1` itself can also be ambiguous <a href="#ref-10">[Ref-10]</a>. Run status and exported `decode_filter_mode` document the query selection without proving that every selected observation is WSPR-2. When a period is ineligible for fallback and the strict query has no Target-side evidence, WSPRadar explains the WSPR-2 filter and historical cutoff; this does not prove that the Target used another mode.

<a id="sec-6-5"></a>

#### 5.5 How the Target-Active Gate shapes evidence

The Target-Active Gate retains simultaneous cycles only when Target participation is observable. Reference reports from periods when the Target was offline are therefore not counted as automatic Target failures.

The gate is intentionally Target-centric. Reference uptime remains an experimental responsibility, and swapping Target and Reference can change one-sided Decode Outcomes and the eligible population. [Section 7.1.3](#sec-7-activity-eligibility) defines the conditioning formally.

<a id="sec-6-6"></a>

#### 5.6 Working with upstream data

Public WSPR databases can contain duplicates, false spots, incorrect locators or power values, delayed uploads and later corrections. wspr.live describes fresh data as arriving after a delay of a few minutes; waiting about **five minutes** after the final cycle is a practical estimate, not a completeness guarantee <a href="#ref-10">[Ref-10]</a>.

**Check the source as well as the spots.** Use **System Audit Status** to identify the database used by the completed run. When recent data look incomplete, first verify the uploads and their identities, then check whether those rows are available in that database; a waiting period alone does not establish completeness.

**Database selection and retry.** Under concurrent load, WSPRadar can route a complete new run from its primary source, **wspr.live**, to **WSPRDaemon WD2** and then **WD1**, as capacity permits. This ordered capacity spillover is distinct from provider failover. If a source fails before the run is committed to that source, WSPRadar discards the unpublished attempt and can restart the complete run on the next eligible source. Reference location discovery commits the ensuing Reference Setup/Station analysis to the same database. If that committed source fails, the attempt stops and the failed location discovery is cleared; start again and review the newly resolved Reference location. Every completed run uses one database; records from different sources are never combined.

WSPRadar reduces sensitivity to isolated bad rows through identity consolidation, medians, eligibility thresholds and Drill-Down, but repeated plausible errors can remain. Correct calculations cannot repair an incorrect reported power, locator or operating identity.

**System Audit Status** records the provenance needed to interpret the run:

| Status element | Meaning |
|---|---|
| **Data source** | The single upstream database used for the completed run. Evidence from different databases is not combined within one run. |
| **Historical fallback** | Whether source selection was repeated without the strict WSPR-2 decode-code condition. |

These status items document where the evidence came from and whether the historical compatibility fallback was used; they do not define a different scientific method.

A database retrieval larger than 1,000,000 complete rows is rejected before analysis rather than silently truncated. Shorten the window or use a relevant database-side population filter as described in [Section 5.2](#sec-6-2).

<a id="part-iii"></a>
## Part III: Scientific Foundations, Methods and Claims

Part III explains why the comparisons are reasonable, how the numbers are calculated and what they support. It is written for technically interested radio amateurs, HamSCI contributors and reviewers. [Chapter 6](#sec-d) connects the method to earlier work; [Chapter 7](#sec-7) follows the data from reported spots to results; [Chapter 8](#sec-8) explains defensible claims and reproducibility. The scientific detail includes which observations qualify, what is missing, how stations are weighted, which observations depend on one another and how values are transformed. Plain-language explanations and worked examples accompany the calculations.

<a id="sec-d"></a>
### 6. Literature, Prior Art and Positioning

WSPR research has developed through contributions from radio amateurs, academic researchers, software developers and instrument builders. Their work established ways to compare antennas, diagnose station problems and study propagation using a worldwide reporting network.

This chapter recognizes selected contributions and explains their relevance to WSPRadar. It is a focused methodological review, not an exhaustive history. Published research, preprints, amateur technical reports and software documentation provide different kinds of evidence. Each deserves credit for what it demonstrates.

Three practical lessons connect much of this work: compare under common conditions, establish activity before interpreting silence, and examine the complete station before attributing a difference to an antenna.

<a id="sec-d-1"></a>
#### 6.1 From reporting network to experimental dataset

**Joe Taylor, K1JT, and Bruce Walker, W1BW: creating the shared experimental resource.** Taylor’s WSPR protocol and software made automated weak-signal measurements accessible to ordinary amateur stations; Walker developed WSPRnet to collect and share their reports. Their 2010 article explicitly identified the database’s value for propagation research. An example combined observations from several weeks by time of day, showing how accumulated reports could reveal patterns beyond an individual contact or operating session. The wider community of station operators and maintainers supplies the observations that make this possible. <a href="#ref-6">[Ref-6]</a>

**Nathaniel Frissell and collaborators: connecting amateur observations to space science.** Their 2019 study used WSPRNet and Reverse Beacon Network observations to investigate HF communication changes during the September 2017 solar activity. A defined quiet-time baseline helped distinguish solar-flare blackouts and geomagnetic-storm effects from ordinary variations in reported activity. <a href="#ref-13">[Ref-13]</a>

Their 2022 work showed that changes in communication distance recorded by WSPRNet, the Reverse Beacon Network and PSKReporter could reveal large-scale traveling ionospheric disturbances. Comparisons with SuperDARN radar and satellite-navigation measurements of ionospheric electron content supported the interpretation. These studies demonstrate how amateur reports can contribute to physical research when sampling, background conditions and independent observations are considered together. <a href="#ref-14">[Ref-14]</a>

Frissell et al. place WSPRNet alongside the Reverse Beacon Network and PSKReporter as established amateur-radio observation networks that provide long-term bottomside-ionosphere observations. They distinguish these networks from purpose-built scientific instruments and recommend cross-calibration between instrument networks. The review supports scientific use of amateur observations; it does not make each contributing receiver a calibrated sensor. <a href="#ref-7">[Ref-7]</a>

The WSPR database is therefore a valuable observational resource whose interpretation depends on the experiment. Equipment, local noise and operating schedules differ; callsigns, locators and powers are supplied by operators; and ordinary spot records contain successful decodes. A missing report needs additional context.

<a id="sec-d-2"></a>
#### 6.2 Making observational WSPR data interpretable

<a id="sec-d-lo"></a>
**Lo and collaborators: establish activity before interpreting silence.** Their 2022 study of 7 MHz greyline propagation examined whether transmitters were heard elsewhere and whether receivers heard other stations before interpreting missing reception. It also considered station identity, location and observations from multiple sites. This turns a practical question — “was the equipment actually operating?” — into part of the scientific method.

Their contribution extended beyond activity checks. Using a full year of observations between Europe and Australasia, they investigated daily and seasonal reception patterns and found differences between the two transmission directions. They proposed elevated European summer-evening noise as a possible explanation for missing sunset reception. The study connects propagation research with station diagnosis: reception depends on the receiving environment as well as propagation between the stations. <a href="#ref-9">[Ref-9]</a>

**Gwyn Griffiths, G3ZIL, Rob Robinett, AI6VN, and Glenn Elmore, N6GN, 2019–2020: measure noise alongside WSPR reception.** Their technical report developed noise estimates from the same receiver recordings used for WSPR decoding. They compared measurements in the gaps between transmissions with frequency-domain estimates that could operate during reception, and investigated calibration toward the receiver’s antenna input.

The distinctive contribution is additional measurement evidence for understanding why SNR changes: stronger signals and lower noise can both improve reception. Ordinary WSPR spot records alone cannot separate those causes. This work supported WSPRdaemon’s extended measurements and was subsequently published in QEX in September/October 2020. <a href="#ref-15">[Ref-15]</a> <a href="#ref-16">[Ref-16]</a>

Together, these approaches show why reception analysis needs evidence about station activity and the conditions under which SNR was measured.

<a id="sec-d-3"></a>
#### 6.3 Antenna and station-comparison lineage

**Patrick Destrem, F6IRF, 2008: automated switching and comparisons by direction and distance.** Destrem documented computer-controlled antenna switching at ten-minute intervals, correction of reports to a common transmit power, and examination of results by receiving station and geographic grouping. These were interleaved measurements: the antennas were tested in alternating periods.

His follow-up showed why an overall result and a result restricted to distant receivers could differ. He extended the approach to receiving antennas on 160 m and comparisons between stations through common remote receivers. These reports provide early practical examples of treating WSPR as an experimental measurement system, with attention to antenna interaction, local noise and limited observations. Their particular value is connecting the comparison to the directions, distances and operating conditions in which an installation performs well. <a href="#ref-17">[Ref-17]</a>

**Charles Preston, then KL7OA and later K7TAA, 2009: simultaneous comparison under shared conditions.** Preston described operating two antennas with separate transmitters or receivers at the same location and comparing simultaneous reports. For TX comparisons, the same distant receiver observes both transmissions, reducing differences caused by changing propagation and receiver conditions. He framed the practical question as which available antenna works better at the operator’s location.

His preliminary report distinguished received SNR from signal strength and acknowledged interaction between nearby antennas. It also examined one-sided reports: a missing counterpart could indicate a weak signal or interference at one transmission frequency. This is early recognition that reports received from only one side contain useful information, but require interpretation. The small initial experiment demonstrated the method while leaving its antenna findings provisional. <a href="#ref-18">[Ref-18]</a>

Preston subsequently published *Antenna Comparisons Using Simultaneous WSPR Measurements* in QEX, July/August 2017. <a href="#ref-19">[Ref-19]</a>

<a id="sec-d-toledo"></a>
**Sivan Toledo, 2010: a useful negative result about experimental timing.** Toledo tested antennas in roughly hour-long blocks and found that propagation-related SNR variation was comparable with the apparent antenna differences. He checked another receiver’s observations to investigate whether the fluctuations originated at his own station; similar variations were present there.

The experiment demonstrated why that measurement design could not reliably separate the effects. His discussion connected the problem to other operators’ automated switching and simultaneous-transmission approaches. The lesson is practical: more reports do not rescue a comparison if the antennas were tested under materially different conditions. <a href="#ref-3">[Ref-3]</a>

<a id="sec-d-milazzo"></a>
**Carol Milazzo, KP4MD, 2011: compare complete stations and examine both directions.** Milazzo compared stations 29 km apart through a common receiver about 1,750 km away, corrected SNR for transmit-power differences and compared the observed behavior with VOACAP. She also examined reciprocal reception: on 40 m, the transmit and receive comparisons favored different stations.

This makes the study especially useful for understanding the roles of equipment and local noise. A station that produces stronger reports when transmitting can still provide poorer reception. Unequal duty cycles, different sites and the selected common receiver limit how broadly the particular results can be generalized. <a href="#ref-4">[Ref-4]</a>

<a id="sec-d-griffiths-squibb"></a>
**Gwyn Griffiths, G3ZIL, and Nigel Squibb, G4HZX, 2017: use common-signal comparisons to diagnose a station.** They selected reports of the same transmitter at the same time and investigated SNR differences against time, distance, soil moisture and station changes.

Their work went beyond describing patterns. They examined rainfall and used an additional reference receiver to investigate the soil-moisture explanation. After three ground radials were added at G4HZX, the earlier moisture association was absent in the subsequent test period. They also documented improved SNR following a change in computer placement and the audio arrangement.

The distinctive contribution is a practical cycle of observation, hypothesis and intervention. Repeated comparisons, environmental information and recorded station changes made the diagnosis more informative than spot totals alone. The observations concern complete receiving installations; the proposed physical mechanisms remain interpretations supported to different degrees by the accompanying checks. <a href="#ref-5">[Ref-5]</a>

<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels and Lamy, 2022: characterize the receiving equipment before comparing antennas.** Their peer-reviewed 160 m experiment connected two receiving chains to a common antenna to measure their offset before making simultaneous antenna comparisons. Two seven-day calibration periods each produced a mean offset of about 1.2 dB, which they applied to the comparison.

They also investigated reception with identical antennas placed at orthogonal orientations. The measured orientation-dependent SNR prompted discussion of polarization and ionospheric effects as possible explanations. The practical contribution is making the receiving apparatus itself testable before interpreting antenna differences, while distinguishing observed behavior from its proposed causes. <a href="#ref-2">[Ref-2]</a>

<a id="sec-d-zander"></a>
**Jens Zander, 2022: explain the assumptions and precision of simultaneous TX comparison.** Zander’s preprint develops a mathematical account of two local antennas transmitting simultaneously, with separate callsigns, to common remote receivers. A receiver contributes to the SNR comparison when it reports both transmissions in the same WSPR cycle. Under the model’s assumptions, shared propagation loss and receiver noise cancel in each SNR difference.

Equal or corrected transmit powers remain essential; interference, failed decodes, quantization and differences between transmitting chains still matter. A difference formed within one remote receiver does not require calibration against other receivers.

His preliminary experiments retained approximately 150–200 paired observations from 15–35 receivers out of about 1,000 reports, with sample standard deviation near 3 dB. The analysis explains how averaging can improve precision and discusses geographic sampling, antenna directivity and unknown elevation angles. His distinctive contribution is the mathematical treatment of cancellation, interference and spatial sampling bias. <a href="#ref-1">[Ref-1]</a>

**Thomas Rietdorf, DL2OAH, 2026: bring synchronized comparisons into a practical multiband workflow.** His DARC presentation, based on January 2025 measurements, compares horizontal and vertical installations using synchronized transceivers in separate RX and TX runs on four bands.

It distinguishes Joint Spots from one-sided reports and examines SNR differences by time and direction. The accompanying R workflow, developed with programming assistance from AI tools, illustrates how an amateur can move from downloaded reports to a structured investigation.

Different transceiver models remain part of the compared installations; the results should therefore be read as station comparisons, with the author’s cautions about propagation and the distribution of remote stations. The contribution is a practical example combining synchronized measurements, statistical analysis and several complementary views of antenna use at one location. <a href="#ref-20">[Ref-20]</a>

<a id="sec-d-4"></a>
#### 6.4 Analysis infrastructure and related tools

**Griffiths and Robinett, 2020: make richer database analysis reusable.** Their WSPRdaemon TimescaleDB database and Grafana examples joined reports from the same transmitter, time and band, then displayed SNR differences, medians, quartiles, time patterns, distance and azimuth. They also brought noise measurements alongside spot data and supported exports.

The contribution was an accessible analysis workflow: operators could select stations and periods, inspect temporal and geographic structure, and investigate differences that spot totals concealed. <a href="#ref-21">[Ref-21]</a>

**Arne and wspr.live: public access to large-scale WSPR analysis.** The wspr.live project uses ClickHouse to make large collections of historical and recent WSPR reports directly queryable. Its documented SQL interface, dashboards and export facilities let researchers select and analyze observations for their own questions.

The engineering contribution combines data collection, database organization and public query access into a service that other applications can use. This makes independent research practical without each project having to collect and maintain its own historical database. The project also credits HB9VQQ for providing computing resources. <a href="#ref-10">[Ref-10]</a>

**Rob Robinett, AI6VN, and the WSPRdaemon community: collection, hosting and continuing operation.** WSPRdaemon contributes reliable reception and reporting, database hosting and public analysis services. Its documentation credits Arne’s ClickHouse database work and WSPRdaemon hosting, illustrating the collaboration behind this infrastructure. The earlier TimescaleDB work and the ClickHouse services are distinct parts of this development. <a href="#ref-11">[Ref-11]</a>

WSPRadar relies directly on these public services: **wspr.live is its primary database, with WSPRdaemon’s WD2 and WD1 as alternatives**. Their development, computing resources, hosting and continuing volunteer maintenance are essential contributions to WSPRadar and the wider research community.

Other tools make complementary parts of WSPR experimentation accessible:

| Contributor or project | Distinctive practical contribution |
|---|---|
| **Arne — wspr.live** | The public database and query foundation described above, with dashboards and downloads for research and external applications. <a href="#ref-10">[Ref-10]</a> |
| **Phil, VK7JJ — WSPR.Rocks** | Interactive queries, maps, tables and charts, including duplicate and passband inspection. Head2Head compares receivers, transmitters or software versions using selectable metrics. SpotQ provides a heuristic ranking based on distance, reported power and SNR. <a href="#ref-22">[Ref-22]</a> |
| **Rob Robinett, AI6VN, and collaborators — WSPRdaemon** | Multireceiver acquisition, band scheduling, cached reporting and recovery from outages. Additional noise and Doppler information supports investigations beyond conventional spot records. <a href="#ref-11">[Ref-11]</a> |
| **Richard Newstead and SOTABEAMS — WSPRlite/DXplorer** | Standalone low-power beacons combined with accessible antenna and location comparisons, including the DX10 range indicator. Newstead’s 2017 indoor/outdoor experiment explicitly compared SNR reports received by the same station at the same time. <a href="#ref-23">[Ref-23]</a> <a href="#ref-24">[Ref-24]</a> |
| **Walter Machiels, ON4AWM — WSPR-Station-Compare** | A dedicated RX-comparison workflow with measured receiver-offset correction, minimum observations per station, callsign filtering and azimuth selection. These controls translate experimental methods into reusable operator software. <a href="#ref-25">[Ref-25]</a> |
| **Fred, W6BSD — Antenna Performance Analysis Tool** | A report generator organizing reception evidence by time, band and receiving location, making observed station coverage easier to inspect without writing a custom analysis. <a href="#ref-26">[Ref-26]</a> |
| **Colin Murray, GM4EAU — WATT** | An editable Excel/VBA workflow for querying, filtering, further calculations and map replay through successive time intervals. The animation helps operators inspect changing propagation patterns. <a href="#ref-27">[Ref-27]</a> |

These tools address overlapping questions, but their filters, comparison units and summaries differ. Similar-looking figures should not be assumed to represent identical calculations.

<a id="sec-d-5"></a>
#### 6.5 What WSPRadar inherits, integrates and adds

WSPRadar builds on this community’s work: accumulated reports, activity checks, transmit-power correction, common-condition comparisons, receiving-chain calibration, database analysis and geographic interpretation.

It brings these ideas into a consistent RX and TX workflow:

* **Benchmark** compares a Target with a Reference Setup/Station or a dynamic Reference Neighborhood.
* **Same-cycle Joint Spots** provide ΔSNR, while one-sided Decode Outcomes describe additional reception evidence.
* Reported-power normalization and optional Reference-side correction make the applied adjustments explicit.
* **Performance** measures successful decodes within confirmed opportunities.
* Station-balanced and observation-level summaries distinguish equal station influence from the influence of report volume.
* Map, segment, station and individual-observation views provide a route back to the supporting evidence.
* Saved configurations, processed evidence and exports support reproducibility.

Joint-spot ΔSNR describes only comparisons with qualifying Target and Reference reports for the same remote station and WSPR cycle. Paths seldom heard on one side can therefore be underrepresented; one-sided Decode Outcomes provide complementary evidence. Performance’s Decode Rate describes Target success within confirmed opportunities, established by successful Target decodes or qualifying activity evidence. These results are conditional on the available reports and selected operating conditions; they do not directly establish unconditional reception probability or calibrated antenna efficiency.

Relative to the reviewed literature, WSPRadar’s methodological contribution lies in the particular combination and explicit definitions: which observations qualify, how Target activity conditions the analysis, how opportunities and outcomes are counted, how local References are constructed, and how station and geographic summaries are weighted. These rules connect the experimental question to an inspectable result and are explained in [Chapter 7](#sec-7).

<a id="sec-7"></a>
### 7. Scientific Methods

**Benchmark** asks how Target and Reference differed when the same remote station reported, or was reported by, both sides in the same WSPR cycle. **Performance** asks how often the Target succeeded within confirmed opportunities, without a Reference. This chapter explains exactly which observations count and how their results are combined.

The calculation follows a simple sequence: **reported spots → eligible station-and-cycle observations → SNR differences or decode outcomes → summaries**. These stages are distinct. A database spot is a reported decode; a Joint Spot or confirmed opportunity is an observation unit constructed from reports under the rules below. A median or percentage then summarizes those retained units. It is not another radio measurement.

Start with the shared foundations in [Section 7.1](#sec-7-foundations), then follow [Benchmark in Section 7.2](#sec-7-benchmark) or [Performance in Section 7.3](#sec-7-performance). [Section 7.4](#sec-7-views) explains scope and presentation, [Section 7.5](#sec-7-claims) the strength of conclusions, and [Section 7.6](#sec-7-outliers) the optional experimental event detector.

These are descriptive calculations for the selected evidence. A result can be exact for the retained observations without establishing a physical cause, future performance or a value for every station. [Section 7.5](#sec-7-claims) and [Chapter 8](#sec-8) explain those interpretation boundaries.

<a id="sec-7-foundations"></a>
#### 7.1 Shared evidence foundations

<a id="sec-7-spots-identities-cycles"></a>
<a id="sec-7-1"></a>
<a id="sec-7-2"></a>
##### 7.1.1 Spots, identities and cycles

Each completed run reads one selected WSPR database and does not combine sources. Its reports come from heterogeneous transmitters, receivers, decoders and reporting systems; the database used belongs to the run provenance.

A **spot** is one reported successful decode. A **WSPR cycle** is the two-minute interval beginning at an even UTC minute. The basic observation concerns one exact remote station identity in one eligible cycle on the selected band. That remote station is a transmitter in RX analysis and a receiver in TX analysis. Multiple qualifying reports are consolidated as described in [Section 7.1.2](#sec-7-normalization-consolidation) before outcomes are counted.

Benchmark forms a Joint Spot when both sides have qualifying evidence for that same remote identity in the same cycle. RX compares two receivers observing the same transmitter; TX compares two transmitters observed by the same receiver. Reference Neighborhood first constructs its Reference from qualifying local stations for that remote station and cycle. WSPRadar never pairs reports from different cycles. Matching does not require identical RF frequencies or establish identical physical propagation paths; simultaneous TX signals normally need clear separated frequencies.

**An identity is an exact callsign together with the locator required for that role.** Treating different reported locations as interchangeable could create a comparison between different stations or radio paths.

| Station or role | How WSPRadar identifies it |
|---|---|
| **Target — all analyses** | Exact receiving callsign in RX, or transmitting callsign in TX, together with the Target QTH's four-character locator. |
| **Reference — Reference Setup/Station** | Exact Reference callsign together with its four-character locator resolved from the database. |
| **Remote station — all analyses** | Exact callsign together with the full reported locator: the remote transmitter in RX, or the remote receiver in TX. |
| **Local contributors — Reference Neighborhood** | Local receiver identities in RX, or local transmitter identities in TX, distinguished by exact callsign and full reported locator within the selected radius. |

Target selection uses grid-4 even when a six-character QTH is configured. The full configured QTH remains the origin for distance, azimuth, solar elevation and neighborhood geometry. A matching grid-4 does not prove physical co-location. The same remote callsign at two full locators remains two identities, even when both locators lie in one grid-4.

The database must supply the required identity fields. WSPRadar does not reconstruct compound callsigns from hashes or borrow locators from neighboring Type 2/Type 3 cycles. A missing or differently represented callsign or locator does not become eligible by inference. The local Reference pool excludes the exact Target callsign; a base callsign and suffixed callsign remain distinct. Incorrect, stale or changing locators can split a physical station, move it geographically or trigger moving-station exclusion.

**Extended WSPR still provides separate two-minute observations.** WSPR-2 names the transmission mode; Type 1, Type 2 and Type 3 describe message contents. A Type 2 message carries a compound callsign and power without a locator. Its complementary Type 3 message carries a 15-bit callsign hash, six-character locator and power <a href="#ref-12">[Ref-12]</a>. WSPRadar does not classify these message types, reconstruct missing phases or combine them into a four-minute observation.

Either or both cycles can supply Joint Spots when the required identities resolve in the database. A Joint Spot in one cycle does not require another in the next. Matching message patterns and schedules is the controlled-TX recommendation in [Section 2.2.1](#sec-3-tx-benchmark-simultaneous), not a message-type eligibility check performed by WSPRadar. [Appendix B](#sec-simultaneous-tx-setup) gives the practical setup and database preflight.

The selected effective UTC window defines the run. For wholly pre-2022 periods with no Target evidence under the strict request, the historical fallback can relax the `code = 1` requirement; [Section 5.4](#sec-6-4) gives its exact boundary and mode uncertainty. Database availability, delay and source selection are explained in [Section 5.6](#sec-6-6).

<a id="sec-7-normalization-consolidation"></a>
##### 7.1.2 Power normalization and consolidation

**WSPRadar puts successful SNR observations on a common reported-power basis in both Benchmark and Performance.** WSPR reports SNR in dB relative to a 2500 Hz reference bandwidth and transmit power in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar expresses successful SNR observations in both RX and TX analyses at a common reported power of **30 dBm (1 W)**:

$$SNR_{\mathrm{norm}}=SNR_{\mathrm{reported}}-P_{\mathrm{reported}}+30$$

Here the SNR terms are in dB and reported power is in dBm. A signal reported at `-15 dB` with `20 dBm` transmit power becomes `-5 dB` at the 30 dBm comparison level: the 10 dB power shortfall is added back. This removes only the **reported power difference**. It does not recreate the decodes that would have occurred at 1 W or correct antenna gain, radiation efficiency, feedline loss, EIRP, receiver calibration or local noise. Decode Outcomes and Performance opportunities remain those actually observed.

**Several reports still count as one observation for that side, remote station and cycle.** WSPRadar retains the strongest qualifying normalized SNR for Performance, each side of Reference Setup/Station, and the Target side of Reference Neighborhood. Local Reference contributors instead use a within-identity median before the neighborhood median is formed; [Section 7.2.5](#sec-7-neighborhood) explains that two-stage calculation. Consolidation never combines successive cycles.

The strongest-report rule represents the **best observed reception**, not a central value for one physical receiver. Weaker duplicate-like reports, secondary decodes or unwanted signal replicas cannot lower the retained value. Their mean or median has no established interpretation as the intended main signal's SNR. WsprDaemon similarly documents reporting the best SNR when merging multiple receivers for WSPRnet <a href="#ref-11">[Ref-11]</a>.

That precedent does not prove that a stored report is the intended signal, or that both sides selected the same spectral component. Different multi-receiver or reporting arrangements can introduce asymmetry. Medians calculated later summarize the retained observations; they do not undo how each cycle's SNR was selected.

<a id="sec-7-activity-eligibility"></a>
<a id="sec-7-3"></a>
##### 7.1.3 Target activity and eligibility

**A missing report should count against the Target only when there is evidence that the Target was operating.** Both Benchmark and Performance therefore retain cycles with observable Target participation. This is called **Target-active conditioning**.

| Direction | What establishes Target activity in a cycle? |
|---|---|
| **RX** | The Target receiver uploaded at least one qualifying decode. |
| **TX** | At least one qualifying report of a Target transmission exists somewhere. |

The activity witness can lie outside the selected geographic scope. An out-of-scope witness establishes activity but does not itself enter that scope's outcomes, summaries or exports. A cycle without a witness is excluded; WSPRadar cannot distinguish downtime from operation that produced no reported decode. Results consequently describe observable Target-active cycles, not all elapsed time or planned transmissions.

This rule is **asymmetric**. Reference uptime is not a second gate and must be controlled or documented externally. Swapping Target and Reference can change retained cycles and one-sided Decode Outcomes. Every Joint Spot already establishes Target participation, so this gate does not alter its ΔSNR; it changes one-sided/asynchronous evidence and the Performance opportunity denominator.

**Population exclusions affect the activity witness differently.** In Performance, a Target report involving a peer later removed by the special-callsign or moving-station exclusion can still establish activity. In Benchmark, those exclusions apply first: the witness must involve a peer that survives them. Geographic scope is applied afterward in both analyses. Thus a cycle witnessed only by an excluded peer can retain a Performance opportunity for another eligible peer but no Benchmark outcome. The excluded peer contributes to neither result population.

Target activity alone is not enough to turn every silent remote station into a missed decode. Performance also needs the endpoint evidence defined in [Section 7.3.1](#sec-7-performance-opportunities).

<a id="sec-7-benchmark"></a>
#### 7.2 Benchmark: differences and shared evidence

<a id="sec-7-benchmark-outcomes"></a>
<a id="sec-7-6"></a>
##### 7.2.1 Decode Outcomes and missing observations

**Delta SNR and Decode Outcomes answer different questions.** ΔSNR describes the signal difference among Joint Spots. Decode Outcomes show how much retained evidence was available on both sides or on only one side.

| Outcome | Meaning |
|---|---|
| **Only Target** | Target evidence exists for this remote identity and cycle; Reference evidence does not. |
| **Joint** | Both sides have qualifying evidence for the same remote identity and cycle, allowing ΔSNR. |
| **Only Reference** | Reference evidence exists for this remote identity and cycle; Target evidence does not. The cycle is retained because Target activity was established elsewhere. |
| **Both (Async)** | At station level, both sides have retained evidence, but no qualifying same-cycle pair for the relevant station category. This supplies no ΔSNR. |

Joint Spots are selected by successful observation of both sides. Weak signals, collisions, QRM, decoder behavior, power differences and propagation can all affect whether a pair exists. Consequently, Joint evidence can underrepresent conditions near either side's decode threshold; missing pairs should not be assumed random.

One-sided reports have no missing-side SNR to reconstruct. They receive no artificial ΔSNR and cannot be normalized as an SNR pair. In TX, unequal actual or reported powers can affect one-sided outcomes even though Joint ΔSNR is normalized. Target-active conditioning also makes the two one-sided categories asymmetric; they are not symmetric wins and losses.

**Extended-WSPR identity errors need separate attention.** Type 3 uses a 15-bit callsign hash. An unresolved or colliding hash can leave a decode unidentified or associate it with an incorrect callsign, locator or power, as documented by QRP Labs <a href="#ref-28">[Ref-28]</a>. Isolated affected rows may leave a median almost unchanged, but clustered or unequal effects between Target and Reference can change coverage, one-sided outcomes and station or segment results. A large dataset alone offers no protection.

WSPRadar can check for the configured callsign and locator in the database; it cannot prove every upstream hash association correct. When using compound callsigns, carry out the database preflight and phase-specific audit in [Appendix B](#sec-simultaneous-tx-setup), checking message position, receiver, side and time.

Performance's successful-SNR selection and Benchmark's Joint-decode selection are different restrictions. Read their SNR summaries alongside the corresponding opportunities, Decode Outcomes and evidence coverage.

<a id="sec-7-benchmark-delta"></a>
<a id="sec-7-5"></a>
##### 7.2.2 Delta SNR and Reference correction

**Reference correction** accounts for an independently established additive offset. It is added to the normalized Reference SNR, never to the Target:

$$SNR_{\mathrm{Reference,corr}}=SNR_{\mathrm{Reference,norm}}+C_{\mathrm{Reference}}$$

The correction must be approximately stable over the relevant band, signal levels, hardware state and time. Enter a measured calibration offset with the `target - reference` sign. [Section 4.3](#sec-5-3) explains the controls and [Appendix C](#sec-reference-snr-calibration) the calibration procedure.

**Delta SNR compares one Joint Spot.** Subtract the corrected Reference value from the normalized Target value:

$$\Delta SNR=SNR_{\mathrm{Target,norm}}-SNR_{\mathrm{Reference,corr}}$$

| Result | Interpretation for that Joint Spot |
|---|---|
| **Positive ΔSNR** | Target SNR is higher. |
| **Zero ΔSNR** | Target and corrected Reference SNR are equal. |
| **Negative ΔSNR** | Reference SNR is higher. |

**Sign check.** Target `-10 dB` minus Reference `-12 dB` gives **+2 dB**. A Reference correction of `+1.5 dB` raises the Reference to `-10.5 dB`, so ΔSNR becomes **+0.5 dB**. A positive correction therefore reduces the reported Target advantage; the Target observation itself has not changed.

In RX Joint Spots, both receivers observe the same transmitter, so its common reported-power term cancels. TX Joint Spots compare different transmitted signals and depend directly on accurate power reporting and any uncorrected differences in the transmit equipment. The resulting ΔSNR is an observed difference between the complete documented setups; assigning it to one antenna or component still requires the physical controls described in [Chapter 2](#sec-3).

<a id="sec-7-benchmark-aggregation"></a>
<a id="sec-7-7"></a>
##### 7.2.3 Station and map aggregation

**Station balancing prevents one prolific station from dominating solely because it supplies more observations.** It does not turn repeated reports into independent experiments.

For **Reference Setup/Station**, WSPRadar first forms same-cycle Joint Spots, then applies the minimum Joint-evidence count separately to each exact remote callsign-plus-full-locator identity. It calculates that identity's median ΔSNR and then takes the median of those station medians for a map segment. A median is the middle ordered value, or the average of the two middle values when the count is even.

The **Joint-Spot median** instead pools the retained Joint values. It weights every Joint Spot equally, so stations supplying more Joint Spots have more influence. The two summaries can disagree without either calculation being wrong:

| Qualifying station | Retained ΔSNR values (dB) | Station median |
|---|---|---:|
| A | +6, +6, +6, +6, +6, +6 | +6 dB |
| B | -2, -2 | -2 dB |
| C | -1, -1 | -1 dB |

The station-balanced median is **-1 dB**, the middle of `-2, -1, +6`. The Joint-Spot median is **+6 dB**, because the two middle values among all ten observations are both `+6`. Inspect the contributing stations when these summaries disagree; neither alone establishes an antenna advantage.

For every Benchmark design, exactly the identities contributing a qualifying station median count toward the minimum stations per map segment. One-sided-only identities do not provide ΔSNR support. A callsign at `JO31AA` and the same callsign at `JO31AB` count separately if both qualify. Medians of `+2` and `+4 dB` give a segment median of `+3 dB` with support count **2**: a two-station minimum passes, a three-station minimum does not. This counts reported identities, not proven independent physical sites.

<a id="sec-7-benchmark-coverage"></a>
<a id="sec-7-8-2"></a>
##### 7.2.4 Joint Evidence Share

**Joint Evidence Share measures how much retained evidence can support ΔSNR.** For a station and time bin, its denominator is **Only Target + Joint + Only Reference**. It is neither all scheduled cycles nor only jointly decoded observations.

| Summary | Calculation in plain language |
|---|---|
| **Station-balanced Joint Evidence Share** | For each station, divide its Joint count by its total retained outcomes. Average those fractions and express the result as a percentage. |
| **Outcome-level Joint Evidence Share** | Pool the outcomes of all contributing stations. Divide the total Joint count by the total retained outcomes and express the result as a percentage. |

A station contributes if it has at least one retained outcome in the bin, including a station with **zero Joint Spots**. A station with no outcome contributes no fraction. In station-support bars, each station contributes one total count divided among its Only Target, Joint and Only Reference fractions. Outcome-support bars instead count every retained outcome.

For example, a station with 80 Joint outcomes out of 100 contributes 80%; another with 1 out of 10 contributes 10%. Their station-balanced share is **45%**, while pooling gives `81 / 110 = 73.6%`. The first gives stations equal weight; the second gives outcomes equal weight. Neither is a Target win rate. The Target-active asymmetry in [Section 7.1.3](#sec-7-activity-eligibility) still applies.

<a id="sec-7-neighborhood"></a>
##### 7.2.5 Reference Neighborhood

**Reference Neighborhood adds a local Reference before the same station-and-segment aggregation.** For each remote identity and cycle:

1. Normalize the qualifying reports and apply the Reference correction to local Reference values.
2. Reduce multiple reports from each local callsign-plus-full-locator identity to one within-identity median.
3. Take the median across those local identity values, giving each contributing identity one value.
4. Subtract that Reference from the Target's strongest qualifying normalized SNR, then form remote-station and segment ΔSNR medians as above.

Absent local identities are omitted, never assigned zero. There is no separate minimum number of local contributors per cycle: one contributor becomes the Reference; none means no Reference SNR or Joint ΔSNR. The other Joint-evidence and map-support thresholds do not impose a neighborhood-size minimum. Multiple local identities may share equipment or a site, so equal identity weight is not necessarily equal physical-site weight.

**Membership alone can move the result.** Corrected local SNR values `-18, -12, -6 dB` give a Reference of `-12 dB`. With Target SNR `-10 dB`, ΔSNR is `+2 dB`. If the `-6 dB` contributor disappears, the Reference becomes `-15 dB` and ΔSNR **+5 dB**, without any Target change. The local Reference is specific to the observed contributors, remote station and cycle.

<a id="sec-7-performance"></a>
<a id="sec-7-4"></a>
#### 7.3 Performance: opportunities and success

**Performance asks where and how consistently your station succeeds when a reception opportunity can be established.** It does not count every quiet two-minute cycle as a failure. A successful Target decode establishes its own opportunity; otherwise, a Miss requires evidence that the relevant remote station was active while the Target was also demonstrably operating.

<a id="sec-7-performance-opportunities"></a>
##### 7.3.1 What counts as an opportunity?

Each opportunity concerns one exact remote station identity in one Target-active WSPR cycle on the selected band, after the applicable population and geographic filters. The evidence needed depends on direction:

* **RX:** the remote transmitter is decoded by the Target, or by another eligible receiver. Another receiver's report confirms that the transmitter was on air; without a Target decode, it supports a Miss only if Target receiver activity is also established in that cycle.
* **TX:** the remote receiver decodes the Target, or another qualifying transmitter. Its report of another transmitter confirms that this receiver was operating; without a Target report there, it supports a Miss only if Target transmitter activity is also established in that cycle.

A Target-side success means the Target receiver decoded the remote transmitter in RX, or the remote receiver decoded the Target transmitter in TX. With Target activity established, classification is:

| Target-side success? | Other-station evidence confirms remote activity? | Classification | Count as an opportunity? |
|---|---|---|---|
| **Yes** | **No** | Success supported by the Target decode itself. | **Yes — once.** |
| **Yes** | **Yes** | Success also supported by external evidence. | **Yes — once.** |
| **No** | **Yes** | Miss: the required activity is confirmed but no Target-side success was reported. | **Yes — once.** |
| **No** | **No** | Unknown: insufficient endpoint-activity evidence. | **No.** |

A success without external confirmation remains identifiable as a subset of successes; it is not added again to the totals. External confirmation accompanying a success likewise creates no second opportunity. A report from a different receiving station cannot establish that the particular receiver required for this opportunity was listening. Unknown observations stay excluded, with no invented SNR.

<a id="sec-7-performance-rates"></a>
##### 7.3.2 Decode Rates and weighting

**Decode Rate** is the percentage of confirmed opportunities that succeeded:

$$\text{Decode Rate (\%)}=\frac{\text{successful opportunities}}{\text{confirmed opportunities}}\times100$$

Confirmed opportunities comprise **successes plus Misses**. WSPRadar calculates one rate per qualifying remote station; a station qualifies only when its opportunity count meets the configured minimum. It then provides two complementary summaries:

| Summary | How it is calculated | Question answered |
|---|---|---|
| **Station-balanced Decode Rate** | Average the individual qualifying stations' Decode Rates, giving each station equal weight. | How consistently did the Target succeed across the qualifying stations, giving each equal weight? |
| **Opportunity-level Decode Rate** | Pool the successes and confirmed opportunities of those qualifying stations, then divide total successes by total opportunities. | What fraction of all retained opportunities succeeded? |

**Example.** Two qualifying stations have `90 successes / 100 opportunities = 90%` and `5 / 10 = 50%`. Equal station weight gives **70%**. Pooling gives `95 / 110 = 86.4%`: 95 successes and 15 Misses, each counted once. The higher pooled rate reflects more opportunities on the more successful station; neither weighting is the uniquely “true” rate.

<a id="sec-7-performance-reach"></a>
##### 7.3.3 At-least-once Peer Reach

**At-least-once Peer Reach** measures breadth: the percentage of qualifying remote identities with at least one Target success. One success and many successes both count once for Reach. Both stations in the example have succeeded, so Reach is **100%**, despite their different Decode Rates. Adding observations cannot undo an earlier success for a fixed peer population, but the qualifying population can change between runs; reported Reach therefore need not rise with duration.

<a id="sec-7-performance-snr"></a>
##### 7.3.4 Successful Target SNR

**Successful Target SNR** describes only retained successful decodes after normalization and strongest-report consolidation. Misses have no Target SNR. The later sections explain how these values are grouped for medians, spread and extremes. Read SNR together with Decode Rate: adding marginal decodes can lower successful-SNR summaries while improving reception and reach.

Performance describes conditional participation in the observed network. It is not unconditional receiver sensitivity, success probability for every attempted transmission or absolute station efficiency.

<a id="sec-7-views"></a>
<a id="sec-7-8"></a>
#### 7.4 Scope and summaries across space and time

The same evidence can answer different questions depending on what receives equal weight. A map usually compares stations; a Joint-Spot distribution compares observations; a folded hourly view can combine several dates. The following rules define those distinctions.

<a id="sec-7-view-scope"></a>
<a id="sec-7-9"></a>
##### 7.4.1 Scope, geography and filters

Distance and azimuth use the configured Target QTH and reported peer locators on a spherical Earth of radius **6371 km**. The map is azimuthal equidistant, centered on Target QTH, with distance boundaries at `2500`, `5000`, `10000`, `15000`, `20000` and `22000 km` and **22.5-degree** direction sectors. Locators describe grid cells, not measured antenna positions; these results are not survey-grade positioning or take-off-angle measurements.

**Maximum peer distance from Target** excludes stations at or beyond the selected distance before scientific aggregation and processed-evidence export. Inspector selections can narrow the retained population but cannot restore excluded stations. Target activity is established globally before geographic filtering. Moving-station exclusion likewise identifies changing-location callsigns in the otherwise eligible global population before distance scope is applied.

Solar classification uses solar elevation at **Target QTH at the WSPR-cycle timestamp**. It describes conditions at the Target, not illumination along the complete propagation path or at every remote endpoint. Database retrieval limits and source-population controls are explained in [Section 5.6](#sec-6-6).

<a id="sec-7-view-geography"></a>
<a id="sec-7-8-1"></a>
##### 7.4.2 Geographic summaries

Segment summaries use the complete qualifying population in the active geographic scope. Sorting a table or selecting a row does not redefine that population. Benchmark maps use the median of qualifying station medians described in [Section 7.2.3](#sec-7-benchmark-aggregation); the Joint-Spot distribution remains separately available.

Performance distance profiles group stations by their calculated distance from Target QTH. Bin widths of `125`, `250`, `500` or `1,000 km` are selected deterministically from the active distance span. Edges are anchored at integer multiples from `0 km`, with the final selected upper boundary included. Disjoint selected ranges keep their gaps rather than filling them with zero evidence.

Each distance bin reports Reach, both Decode Rate weightings, and successful Target SNR. For SNR, each station first contributes its median successful value; the profile summarizes those station medians. Three or more medians support an IQR, two a min–max interval, and one a single value. Stations with only Misses receive no synthetic SNR.

<a id="sec-7-view-time"></a>
<a id="sec-7-8-3"></a>
##### 7.4.3 Chronological evidence

**Chronological views preserve the sequence of the run.** Bins start at the selected UTC start and use the chosen width; the final bin can be shorter. Empty intervals remain missing, not 0 dB. Offered widths depend on the complete run duration rather than the observed evidence span; [Section 4.5](#sec-5-5) lists the choices and defaults.

**Benchmark ΔSNR** summarizes retained Joint Spots within each chronological bin. Coverage separately includes all retained one-sided and Joint outcomes using the two shares defined in [Section 7.2.4](#sec-7-benchmark-coverage). An empty ΔSNR layer can therefore coexist with one-sided evidence; it does not establish that the database returned no reports.

**Performance successful-SNR deviation** asks whether each station was stronger or weaker than its own usual successful level. A station needs at least three successful normalized observations in the complete run window. Its baseline is their median; subtract that baseline from each success. Thus a path normally at `-10 dB` contributes a deviation of `+3 dB` when observed at `-7 dB`. Zero means this path's usual successful level, not Target–Reference equality.

Chronologically, each station contributes at most one median deviation per bin.

Performance support uses all confirmed opportunities from its qualifying stations, including stations without enough successes for the SNR-deviation layer. In a chronological bin, each station's support is divided between success and Miss in the proportions of its Decode Rate. Total station support therefore counts contributing stations; pooled opportunity support counts confirmed opportunities. The corresponding fractions reproduce the station-balanced and Opportunity-level rates.

<a id="sec-7-view-folding"></a>
##### 7.4.4 Combining dates by UTC hour

Benchmark ΔSNR pools retained Joint Spots by UTC hour across represented dates. For Performance successful-SNR deviation, each station first contributes one median per date and hour. Extra rows within that station-date-hour add no further weight, but stations present on more dates and dates containing more stations still contribute more values. This is not equal weighting of stations or dates over the whole run.

**UTC-hour folding combines dates and needs at least two dates represented by the relevant evidence.** For Performance support, a represented date has at least one qualifying confirmed opportunity somewhere in the active scope and selected window. Benchmark coverage uses dates with any retained outcome, whereas its ΔSNR layer needs dates with retained finite Joint ΔSNR. One Joint date plus a second date with only one-sided outcomes can therefore enable folded coverage without enabling folded ΔSNR. A represented date-hour overlapping the selected window contributes to the support-averaging denominator even if that hour has no evidence; hours outside the window do not. A partially overlapping boundary hour counts as one slot, without exposure weighting, so its average can be depressed.

For folded Performance rates, first pool each station's successes and opportunities at that UTC hour across represented dates, then average the individual station rates equally. Folded station support is the number of station-date-hour presences divided by the represented date-hour count; folded opportunity support is the pooled outcome count divided by that same denominator. Benchmark folded coverage likewise expresses outcome volume per represented date-hour while retaining its station-balanced and pooled Joint shares.

Folding can reveal an hour-of-day association but does not by itself prove repetition on each date. Check the chronological view before calling a pattern recurrent.

<a id="sec-7-view-station"></a>
<a id="sec-7-8-4"></a>
##### 7.4.5 Selected Station Evidence

Selected Station Evidence restricts the active retained scope to one exact remote identity. It does not change upstream matching or eligibility.

* **Benchmark:** chronological and folded summaries use that station's Joint-Spot ΔSNR; separate coverage includes Only Target, Joint and Only Reference.
* **Performance:** chronological summaries use actual normalized successful Target SNR, while the folded SNR profile uses one date-hour median per represented date. Success/Miss counts and Decode Rate describe the same path. With one station, both Decode Rate weightings coincide within a populated bin, although station presence and opportunity volume remain different support counts.

Focused Drill-Down shows native retained observations: consolidated Joint-Spot ΔSNR for Benchmark, or successful normalized Target SNR for Performance, at their actual WSPR-cycle times. “Native” means after matching, consolidation and scientific filtering, not untouched database rows. These points are different from temporal-bin medians or density summaries.

Outlier Focus can include the candidate and its full baseline flanks, even when this exceeds the ordinary focus interval. It uses the completed detector result rather than fitting a new detector to the focused subset. Local baselines and departure guides apply to that candidate; they are detector coordinates, not confidence intervals or independent qualification tests. Changing focus or display bins changes the view, not the completed scientific result.

<a id="sec-7-view-spread"></a>
<a id="sec-7-8-5"></a>
##### 7.4.6 Spread and display scales

**IQR describes the middle half of the contributing values; min–max describes their full range.** Neither is a confidence interval. Temporal IQR bands require at least five contributing values; a median remains available with fewer. Depending on the view, those values are Joint Spots, successful Target observations, station-bin medians or station-date-hour medians. Performance distance profiles use the separate three-station rule in [Section 7.4.2](#sec-7-view-geography).

**Density color is relative within each panel.** The most populated cell is assigned `100`; other cells are scaled in proportion to its count. This does not mean 100% of all evidence. Use support counts to compare absolute volume between panels.

Benchmark histograms normally use 1 dB bins, use 0.5 dB for a clear half-dB lattice, and coarsen broad ranges. Temporal density cells stay 1 dB high and shift with the Reference correction. For the same retained population, the cells and observations move together while cell counts and relative colors stay unchanged. Display binning does not round the retained observations or their statistics, and fractional observations need not lie at cell centers.

Benchmark temporal and histogram axes can compress the tails around the scope median while keeping absolute `0 dB` visible. Read the labeled dB coordinates rather than estimating differences from visual spacing. In histograms, bar **length against the percentage axis**, not displayed area, encodes the quantity. These transforms change neither values nor counts, medians or quartiles. Performance successful-SNR axes remain linear in dB.

<a id="sec-7-claims"></a>
<a id="sec-7-10"></a>
#### 7.5 How strong is the conclusion?

<a id="sec-7-dependence-bias"></a>
##### 7.5.1 Dependence and bias

**1,000 spots are not 1,000 independent experiments.** Repeated cycles share station equipment and propagation; nearby stations share conditions; neighboring time bins are related; one interference or ionospheric event can affect many observations. The two phases of an extended-WSPR sequence likewise add observations within a run, not independent experimental repetitions.

Station balancing reduces domination by prolific reporters, and medians reduce the influence of isolated extremes. Neither removes systematic calibration errors, reporting differences or propagation bias, or creates independence. WSPRadar supplies descriptive summaries, not automatic standard errors, confidence intervals, p-values, statistical power or causal effects. Treating every report as independent would generally understate uncertainty about a future run or broader population.

<a id="sec-7-repeatability-control"></a>
##### 7.5.2 Repeatability and experimental control

Assess support at several levels: **depth** of opportunities or Joint Spots; **breadth** and geographic diversity of station identities; **internal consistency** across weighting, geography and time; **repeatability** in a new controlled run; and **experimental control**, such as calibration, crossover, schedule reversal or independent measurement. Agreement among views of the same observations is internal consistency, not replication. [Chapter 8](#sec-8) explains how to bound the resulting claims.

<a id="sec-7-validation"></a>
##### 7.5.3 Validation scope

Software-validation statistics also need context: identify the dataset, date, WSPRadar version or source revision, and calculation method. A dated check is evidence about that test, not a timeless guarantee for every station or dataset.

<a id="sec-7-outliers"></a>
<a id="sec-7-11"></a>
#### 7.6 Experimental ΔSNR event analysis

**This experimental, optional detector identifies temporary departures from a path's usual local ΔSNR.** It is an expert diagnostic, not a required analysis step. [Section 2.5](#sec-outlier) explains its use and [Section 4.6](#sec-5-6) gives the controls. This overview explains the scientific interpretation and principal checks, rather than every algorithmic refinement.

<a id="sec-7-outlier-departure"></a>
##### 7.6.1 Departure from the local baseline

Only native Joint Spots provide detector ΔSNR, separately for each exact remote callsign-plus-locator identity. Native means after matching, consolidation and scientific filtering. Detection uses actual cycle times before display aggregation; changing Temporal Evidence bins cannot change events. With reporting off, the detector is not run.

**A positive ΔSNR can be a negative departure.** Against a **+8 dB** local baseline, a **+1 dB** Joint Spot has departure `+1 - (+8) = -7 dB`. Target remains stronger, but its advantage is 7 dB below its local baseline. The change can come from Target, Reference or both. Grouping follows the departure's sign, not ΔSNR's sign relative to zero.

<a id="sec-7-outlier-baseline"></a>
##### 7.6.2 Baseline and nearby variability

The baseline uses medians of populated **UTC-aligned 10-minute cells** up to **six hours before and after** a candidate, excluding the candidate and a surrounding guard interval. Each flank needs **at least four populated cells**. The expected local ΔSNR is the average of the two flank medians, giving both sides equal weight. Missing cells are not filled. Insufficient support on either side leaves the candidate unclassified.

Nearby variability is measured from the pooled cell residuals after centering each flank on its own median. The robust scale uses their **median absolute deviation (MAD)**; if zero, half the IQR; only if both are zero, **0.5 dB**. That fallback is not a universal minimum. The dimensionless robust z-score is `0.6745 × departure / robust scale`: with scale `1 dB`, the example scores about **-4.72**. This describes relative departure, not probability or statistical significance.

<a id="sec-7-outlier-qualification"></a>
##### 7.6.3 Candidate qualification

Nearby same-sign departures form provisional candidates using the path's observed operating cadence. Final qualification uses a baseline fitted with the complete candidate excluded. All four checks must pass together:

| Required check | Passing condition |
|---|---|
| **Absolute departure** | The event median's magnitude reaches **Minimum absolute ΔSNR departure (dB)**, allowing `0.01 dB` tolerance. |
| **Relative departure** | Its absolute robust z-score reaches **Minimum robust z-score**, without tolerance. |
| **Baseline agreement** | Before/after medians differ by no more than **Maximum pre/post baseline difference (dB)** plus `0.01 dB`. |
| **Sign agreement** | At least **two thirds of all retained native observations**, including any neutral bridge, share the median departure's sign. |

Baseline agreement concerns similar flank medians, not an extra low-variability requirement. The dB tolerance adjusts comparisons, not stored observations or statistics. Duration gives no weaker threshold; a large isolated point cannot substitute for the event-median checks.

<a id="sec-7-outlier-boundaries"></a>
##### 7.6.4 Boundaries and event classes

Reported boundaries must be same-sign observations that individually pass both departure thresholds. The interval is trimmed to these strong anchors and retested against the event-level requirements. Weaker interior observations can remain. A rescued strong core keeps the complete candidate's baseline, scale and support; it cannot select a more favorable baseline. No qualifying anchored interval means no event.

A **Spot impulse** contains one Joint Spot. A **Sustained excursion** contains at least three spanning at least 30 minutes. Every other multi-spot event is a **Short burst**. All classes pass the same checks. First-to-last span describes observed evidence, not uninterrupted behavior between observations.

<a id="sec-7-outlier-context"></a>
##### 7.6.5 Context and limits

Each path qualifies separately. Grouping nearby same-sign events across paths supplies review context: path-specific, directionally coherent, scope-wide or multiple paths. It adds neither significance nor stronger qualification.

Target/Reference decomposition and nearby one-sided outcomes help investigate a candidate; they cannot qualify, extend or strengthen it. The deterministic descriptive detector applies no multiple-event significance correction and does not make event counts independent samples. Assigning a cause still requires the controls discussed in [Chapter 2](#sec-3), [Chapter 3](#sec-4) and [Chapter 8](#sec-8).

<a id="sec-8"></a>
### 8. Evidence-Matched Claims and Reproducibility

Start with what was observed, then state how far the evidence supports an explanation. WSPRadar describes retained reports and the comparisons constructed from them. A report should identify the included stations and cycles, the summary and weighting, the evidence counts, the experiment design and the variables that remain unknown or uncontrolled.

<a id="sec-8-1"></a>
#### 8.1 Claim classes and evidence-matched wording

| Claim class | Statement being assessed | Evidence needed and limit |
|---|---|---|
| **Descriptive** | Reach, Decode Rate, successful SNR, ΔSNR, Decode Outcomes and where they appeared in the selected evidence. | State the population, weighting, scope and support. |
| **Comparative** | Target-versus-Reference difference under the selected Benchmark design. | State what the Reference represents and which Joint Spots support the ΔSNR result. |
| **Component attribution** | A difference associated with a local path or component. | Controlled setup, calibration and preferably crossover/reversal. |
| **Causal** | The tested change caused the observed effect. | A design that controls plausible alternatives; WSPRadar summaries alone are insufficient. |
| **Inferential** | Confidence, significance or a population-general effect. | A justified dependence model and inferential analysis not currently supplied by WSPRadar. |

Use the result type that matches the statement:

* **Performance** supports the Target's conditional behavior within confirmed opportunities and its at-least-once reach during the selected window.
* **Benchmark ΔSNR** describes Target-minus-Reference SNR for the retained Joint Spots; it does not describe signals decoded by only one side.
* **Decode Outcomes** support statements about pairability and one-sided evidence.
* **Distance or direction structure** supports statements about observed path segments, not direct radiation angle or gain pattern.
* **Reference Neighborhood** supports descriptions of how the complete Target station compared with the contributing nearby peers under the selected conditions. Its Reference changes with the qualifying observations, radius, remote path and cycle. It is neither a permanent station ranking nor a calibrated antenna comparison.

A positive or negative ΔSNR quantifies the observed SNR difference among Joint Spots under that construction. It does not identify which component or environmental difference caused it. Joint Evidence Share describes pairability or coverage of the retained evidence; it is not a Target win rate.

Report the direction, band, UTC window, neighborhood radius, geographic scope, applied correction and supporting evidence. Distinguish within-run consistency from reproduction in a separate suitably controlled run.

| Avoid | Evidence-matched wording |
|---|---|
| “Antenna A has 3 dBi more gain.” | “Path A produced a +3.0 dB station-balanced median ΔSNR against B among Joint Spots in this band, window and segment.” |
| “My receiver sensitivity is 72%.” | “The qualifying remote stations had a mean individual Decode Rate of 72% at the Target receiver, using confirmed opportunities established by Target decodes or external endpoint-activity evidence.” |
| “Performance should be close to 100%.” | “Decode Rate is conditional on confirmed opportunities; 100% is not an expected baseline.” |
| “A is statistically significantly better.” | “The descriptive median ΔSNR favored A among the selected Joint Spots; no significance test was performed.” |
| “The antenna has a lower take-off angle.” | “The observed advantage was concentrated in the specified longer-distance segments; radiation angle was not measured.” |
| “A is more efficient because it had more exclusive decodes.” | “A produced more one-sided decode evidence under the documented power, schedule and network conditions; efficiency was not isolated.” |
| “The local median is the average local station.” | “The Reference was the cycle/path median of one contribution per active local callsign-plus-locator identity.” |
| “My antenna is X dB better than nearby antennas.” | “For the stated band, window, radius and scope, my complete station’s station-balanced median ΔSNR was X dB relative to the observed local-neighborhood Reference. This describes the retained Joint evidence and does not isolate antenna gain.” |

<a id="sec-8-2"></a>
#### 8.2 Interpretation boundaries

WSPRadar does not directly measure:

* antenna gain in dBi or radiation efficiency;
* take-off angle or propagation mode;
* calibrated receiver sensitivity or absolute field strength;
* every attempted transmission or complete failure log;
* independent sample size, confidence intervals or statistical significance; or
* causation.

Important data and design boundaries include:

* user-supplied callsigns, locators and powers can be wrong;
* databases contain successful decodes rather than complete attempt logs;
* Performance is conditioned on observable opportunities;
* only cycles with observed Target activity qualify, so Target and Reference are not treated symmetrically;
* successful Target SNR contains only decoded signals; missing decodes have no measured SNR;
* Benchmark ΔSNR uses only Joint Spots with usable SNR on both sides;
* one-sided evidence has no missing-side SNR;
* simultaneous TX retains power, frequency-response, isolation and coupling differences between chains;
* station hardware, software, terrain, local noise, polarization and propagation remain coupled unless the experiment controls them;
* repeated observations share stations, time periods, geography and propagation; a row count is not an independent sample size; and
* upstream records and availability can change after the original run.

These boundaries define what the summaries describe; they do not make the observations useless. Broad, internally consistent and experimentally repeatable evidence can be operationally persuasive while remaining descriptive.

<a id="sec-8-3"></a>
#### 8.3 Reporting and reproducibility checklist

For a result you intend to compare, publish or use for a station change, preserve the following three layers. The export records much of the analysis definition and processed evidence; external notes are needed for the physical experiment. Identify the database source as well as the analysis settings.

**1. Analysis definition**

* WSPRadar application version and, where available, source revision;
* database source and original export date;
* RX/TX Direction, result type and Benchmark design;
* exact Target and Reference identities and locators;
* band and effective UTC boundaries;
* geographic scope, solar state, exclusions and evidence thresholds;
* Reference correction purpose, signed value and calibration basis;
* primary predeclared evaluation scope and any sensitivity analyses; and
* whether the run was exploratory or confirmatory.

When a ΔSNR outlier candidate contributes to the conclusion, also record that reporting was enabled, the three detector thresholds, detector version, exact path, UTC interval, descriptive event class and whether the event was identified exploratorily or assessed under a predeclared confirmatory setup.

**2. Evidence supporting the conclusion**

* reported summary and weighting level;
* qualifying peers and opportunities for Performance;
* Joint stations and Joint Spots for Benchmark;
* station-level and observation-level summaries;
* Joint Evidence Share and relevant one-sided Decode Outcomes;
* geographic/temporal scope and any influential identity or short interval; and
* within-run consistency versus repetition in a separate run.

**3. External experiment record**

* physical antenna, feedline and RF-path arrangement;
* switch/splitter topology and identity-to-path mapping;
* transmitter, receiver, decoder and software versions;
* actual transmit power and WSPR reporting basis;
* calibration measurements and reference plane;
* actual schedule, interruptions, crossovers and reversed assignments; and
* faults, interference, weather or intended changes relevant to interpretation.

Retain the original export package as the evidence record for that run. A later retrieval can reflect upstream corrections or a newer WSPRadar version.

<a id="sec-8-4"></a>
#### 8.4 Analysis export package

Before preparing the export, select the geographic scope, stations and any focus interval needed for your conclusion. `Prepare All Results for Download` builds the ZIP; `Download Prepared Results` saves it. Prepare it again after changing those selections.

Inside the ZIP, `config/` accompanies either `benchmark/` or `performance/`, according to the selected analysis. Figures depend on the available evidence and inspection selections.

| Artifact | Content and use |
|---|---|
| Configuration | `wspradar_config.config` restores the analysis settings and supported view choices for another run, not the original observations. |
| Run metadata | `run_metadata.json` records software version, database, actual data selection, analysis settings, corrections and inspection scope, including enabled outlier settings. Keep it with the evidence: configuration alone cannot reconstruct every selection. Missing selection metadata remains unknown, not proof that the standard filter was used; see [Section 5.4](#sec-6-4). |
| Processed evidence | `analysis_cache.parquet` contains retained evidence across the completed analysis's full geographic scope after its scientific filters. It is neither limited to the selected segment nor an untouched database download. |
| Station Insights CSV | `table_station_insights_current_segment.csv` contains per-peer summaries for the active Segment Inspector scope. It retains its headers when no rows qualify. |
| Drill-Down CSV files | Row-level evidence for selected stations or all stations in the active segment. The selected-station table can reflect focus and table filters. Both files retain their headers when empty. |
| Outlier CSV files | `table_delta_snr_outlier_event_paths.csv` summarizes qualifying path events; `table_delta_snr_outlier_paired_evidence.csv` contains their chronological Joint Spots, including corrected Reference SNR. Both cover the active segment and join through IDs valid only within this package. Reporting off: files absent. Reporting on with no findings: headers only. These are candidate findings, not confirmed physical events. |
| Map, segment and temporal figures | PNGs for presenting the result: the map covers the completed analysis; segment and temporal figures summarize the active segment, including chronological and UTC-hour views. |
| Selected-station figures | Evidence for one exact selected peer. With outlier reporting enabled, Benchmark can instead show pooled Delta SNR for multiple selected paths. |
| Drill-Down focus figures | Additional figures for one selected station and its active focus interval, preserving individual observations and their chronological context. They supplement the full-run selected-station figures; candidate guides refer to the focused episode. |

Keep the original package as the run's evidence record. Physical setup measurements and external operating logs must be retained separately, as described in [Section 8.3](#sec-8-3). A later database query or rerun may produce different records or results.

<a id="sec-8-5"></a>
#### 8.5 Disclaimer

WSPRadar is experimental open-source software provided “as is” without warranty. Its source and methods can be audited, but accuracy, completeness, availability and fitness for purpose are not guaranteed. Do not base major financial or safety decisions on WSPRadar alone.

<a id="sec-ref"></a>
### References

* <a id="ref-1"></a><a href="https://arxiv.org/abs/2209.08989">[Ref-1]</a> **Preprint.** Zander, J. (2022). *Simple HF antenna efficiency comparisons using the WSPR system*. arXiv:2209.08989v1. doi:10.48550/arXiv.2209.08989.

* <a id="ref-2"></a><a href="https://doi.org/10.1155/2022/4809313">[Ref-2]</a> **Peer-reviewed article.** Vanhamel, J.; Machiels, W.; Lamy, H. (2022). *Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*. International Journal of Antennas and Propagation, 2022, 4809313. doi:10.1155/2022/4809313.

* <a id="ref-3"></a><a href="https://sivantoledotech.wordpress.com/2010/09/24/failure-to-use-wspr-to-compare-antennas/">[Ref-3]</a> **Operator technical account.** Toledo, S. / 4X6IZ (2010). *Failure to Use WSPR to Compare Antennas*.

* <a id="ref-4"></a><a href="https://www.qsl.net/kp4md/wspr.htm">[Ref-4]</a> **Amateur-radio technical article and club presentation.** Milazzo, C. F. / KP4MD (2011). *Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*.

* <a id="ref-5"></a><a href="https://www.researchgate.net/publication/319903566_Improving_HF_Band_SNR_from_analysis_of_WSPR_spots">[Ref-5]</a> **Amateur-radio magazine article.** Griffiths, G.; Squibb, N. J. (2017). *Improving HF Band SNR from analysis of WSPR spots*. Practical Wireless, October 2017, 23-26. <a href="https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf">Author-hosted copy</a>.

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

* <a id="ref-20"></a><a href="https://www.darc.de/fileadmin/filemounts/distrikte/g/2026/Talk_in_G/Talk-G_Antennenvergleich_synchr_WSPR_T.Rietdorf_DL2OAH_V2.1_17012025.pdf">[Ref-20]</a> **Amateur-radio technical presentation.** Rietdorf, T. / DL2OAH (2026). *Antennenvergleich mit synchronen WSPR-Daten*. DARC OV R10, 2. Talk in G, TH Köln, 17 January 2026, version 2.1; measurements from January 2025.

* <a id="ref-21"></a><a href="https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf">[Ref-21]</a> **Conference paper.** Griffiths, G.; Robinett, R. (2020). *Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana*. ARRL/TAPR Digital Communications Conference 2020.

* <a id="ref-22"></a><a href="https://wspr.rocks/help.html">[Ref-22]</a> **Tool documentation.** WSPR.Rocks, *Help &amp; Documentation*: SpotQ, SQL access, duplicate analysis, maps, charts and heatmaps. <a href="https://wspr.rocks/head2head/">*Head2Head*</a>: comparisons of receivers, transmitters and software versions; passband inspection is also described in the help.

* <a id="ref-23"></a><a href="https://www.sotabeams.co.uk/wsprlite-classic">[Ref-23]</a> **Product documentation.** SOTABEAMS, *WSPRlite Classic / DXplorer*: WSPR-based antenna-performance analysis and DX10 metric.

* <a id="ref-24"></a><a href="https://www.sotabeams.co.uk/blog/indoor-hf-antennas-does-it-make-much-difference/">[Ref-24]</a> **Operator experiment and product application.** Newstead, R. / SOTABEAMS (2017). *Indoor HF antennas - does it make much difference?*. 5 May 2017.

* <a id="ref-25"></a><a href="https://sites.google.com/myuba.be/wspr-station-compare/home">[Ref-25]</a> **Project documentation.** WSPR-Station-Compare, project page referencing Vanhamel et al. and Zander. Machiels, W. / ON4AWM, <a href="https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-station-compare-app">*WSPR Station Compare App*</a>: RX comparison, receiver-offset correction, observation thresholds, callsign filtering and azimuth selection.

* <a id="ref-26"></a><a href="https://wspr.bsdworld.org/">[Ref-26]</a> **Tool documentation.** Antenna Performance Analysis Tool, WSPR-based antenna report generator.

* <a id="ref-27"></a><a href="https://www.gm4eau.com/home-page/wspr/">[Ref-27]</a> **Tool documentation.** GM4EAU, *WATT WSPR Analysis Tool*: Excel/VBA reporting, mapping, filtering and timeline animation.

* <a id="ref-28"></a><a href="https://qrp-labs.com/qmxp/wsprcorruption.html">[Ref-28]</a> **Manufacturer technical investigation.** QRP Labs, *WSPR Type 3 callsign corruption*: observed compound-callsign hash collision or misassociation behavior in large WSPR datasets and its mechanism. Accessed 2026-08-25.

* <a id="ref-29"></a><a href="https://github.com/HarrydeBug/WSPR-transmitters/blob/1657468ea27052167191a7deda2440a535567ecd/Standard%20Firmware/Release/Hardware_Version_2_ESP8285/WSPR-TX2.19/WSPR-TX2.19.ino">[Ref-29]</a> **Published firmware source, immutable revision.** ZachTek WSPR-TX firmware `2.19` for ESP8285 hardware: `DoWSPR()` frequency selection, centihertz frequency units, product-model selection and build prerequisites. Revision `1657468ea27052167191a7deda2440a535567ecd`. Accessed 2026-08-25.

<div style="page-break-before: always;"></div>

<a id="part-iv"></a>
## Part IV: Practical Supplements

This part collects parallel WSJT-X setup for simultaneous receive paths, the limitation of WSJT-X for sparse synchronized transmit tests, practical simultaneous TX Reference Setup procedures, Reference-side calibration and the project license. Use the sections that apply to your station and experiment.

<a id="sec-a"></a>
### Appendix A: Parallel WSJT-X Instances for Simultaneous RX

This procedure creates a second isolated WSJT-X instance for a simultaneous RX controlled setup comparison on Windows. The current WSJT-X guide documents `--rig-name` as the supported way to isolate each instance's settings and writable files. WSJT-X versions and installation paths can change, so verify the current guide if your menus differ. Parallel instances do not establish a sparse synchronized TX schedule; [Section A.4](#sec-a-4) explains that limitation. <a href="#ref-12">[Ref-12]</a>

<a id="sec-a-1"></a>
#### A.1 Create the second instance

1. Create a desktop shortcut for `wsjtx.exe`.
2. Open shortcut properties.
3. In the shortcut's **Target** field, add a distinct rig name outside the executable quotation marks. Use the actual executable path from your installation, for example:
   `"C:\WSJTX\bin\wsjtx.exe" --rig-name=SDR`
4. Start the shortcut once and close it. For `--rig-name=SDR`, Windows creates these isolated locations:
    * settings: `%LOCALAPPDATA%\WSJT-X - SDR\WSJT-X - SDR.ini`
    * log/writable directory: `%LOCALAPPDATA%\WSJT-X - SDR\`
    * default saved-audio directory: `%LOCALAPPDATA%\WSJT-X - SDR\save\`

<a id="sec-a-2"></a>
#### A.2 Clone the starting configuration if required

1. Close all WSJT-X instances.
2. Copy `%LOCALAPPDATA%\WSJT-X\WSJT-X.ini`.
3. Paste it into `%LOCALAPPDATA%\WSJT-X - SDR\`.
4. Rename the copy to `%LOCALAPPDATA%\WSJT-X - SDR\WSJT-X - SDR.ini`, replacing the newly initialized instance file if intended.

<a id="sec-a-3"></a>
#### A.3 Separate every data path

A cloned configuration can still point both instances at the same audio input or storage path. That can duplicate decoding of the same audio stream or create file conflicts. In the second instance, verify:

1. Open **File > Settings > Audio**.
2. Under **Soundcard**, set **Input** to the intended independent receiver or audio device. The WSJT-X guide specifies 48,000 Hz, 16-bit audio-device configuration.
3. Set **Save Directory** to an instance-specific path, normally `%LOCALAPPDATA%\WSJT-X - SDR\save\`.
4. Set **AzEl Directory** to an instance-specific path, for example `%LOCALAPPDATA%\WSJT-X - SDR\`.
5. Open **File > Settings > General** and set the exact Reference callsign and locator used for reporting.
6. Return to the main WSPR screen, confirm the intended band and audio level, enable spot uploading when required, and verify that uploaded rows use the Reference identity.
7. Confirm clock synchronization for both instances.

Separate directories do not prove RF-path independence. Confirm empirically that both streams use the intended hardware.

<a id="sec-a-4"></a>
#### A.4 Limitations of WSJT-X for simultaneous TX

Parallel isolated WSJT-X instances are useful for simultaneous RX, but ordinary WSPR transmit operation does not provide a sparse deterministic same-cycle A/B schedule. WSJT-X selects the enabled two-minute transmit periods randomly according to `Tx Pct`. Any value below `100%` therefore leaves the two instances unsynchronized; `Tx Pct = 100%` would be required for both to attempt every cycle <a href="#ref-12">[Ref-12]</a>.

That setting is not recommended for this experiment. A WSPR-2 transmission occupies about 110.6 seconds of each 120-second cycle, so every-cycle operation approaches a 92% RF key-down duty cycle and occupies the WSPR sub-band in every slot. As practical good practice rather than a protocol rule, WSPRadar recommends selecting only about `5–20%` of available cycles, with the lower end preferred on busy bands or for longer tests. At those percentages WSJT-X timing remains random rather than deterministic.

For a synchronized sparse simultaneous-TX benchmark, use deterministic beacon hardware instead: two QMX or QMX+ units using Virtual U3S, two Ultimate3S or compatible Virtual U3S implementations, or two ZachTek transmitters with verified randomized split-lane custom firmware. [Appendix B](#sec-simultaneous-tx-setup) gives the practical setup.

<div style="page-break-before: always;"></div>

<a id="sec-simultaneous-tx-setup"></a>
### Appendix B: Simultaneous TX Reference Setup

Use this appendix to prepare two locally controlled transmit paths that radiate distinguishable WSPR signals in the same cycles. The result compares the complete documented Target and Reference paths. Do the bench and database checks before opening the measurement window; callsign legality, RF safety, filtering and station licensing remain the operator's responsibility.

<a id="sec-simultaneous-tx-setup-1"></a>
#### B.1 Choose the callsigns

The simplest and most robust arrangement uses two different valid callsigns that each fit the ordinary one-transmission WSPR format. Each transmission then carries its callsign, grid-4 and power together, avoiding the two-cycle Type 2/Type 3 sequence and the hash limitation discussed in [Section 7.2.1](#sec-7-benchmark-outcomes).

Alternatively, use two compound callsigns, each transmitting the same verified Type 2/Type 3 sequence. When sharing one base callsign, give both transmitters different suffixes, such as `CALL/1` and `CALL/2`. Check which suffixes are permitted for your callsign and operation in your country. Use a suffix only when that on-air identity is valid for the operator and station; database syntax alone is not authorization. Align the sequences so their Type 2 phases coincide and their Type 3 phases coincide.

Do not mix an ordinary one-cycle pattern on one arm with a differently scheduled two-cycle compound pattern on the other. An additional or missing sequence position can produce one-sided evidence through the experimental design itself. Do not invent a suffix merely as a hardware label. This same-cycle comparison requires two distinct valid exact reporting identities. Configure both paths for the same truthful physical test QTH and verify that the reported locations of both identities agree with that actual test QTH.


<a id="sec-simultaneous-tx-setup-2"></a>
#### B.2 Align the schedule and separate the signals

1. Synchronize both transmitters to accurate UTC, preferably from GNSS, and select the same band.
2. Configure the same deterministic recurrence and the same observed even-minute start. Both paths must transmit complete WSPR messages in the same cycles.
3. If extended WSPR is used, confirm that both units start the same Type 2 phase together and the same Type 3 phase together after every restart.
4. On QMX, Virtual U3S or Ultimate3S, place the two directly programmed RF signals nominally `100 Hz` apart while keeping both complete signals comfortably inside the 200 Hz WSPR transmit sub-band. More separation is not automatically better because it consumes edge margin. For ZachTek randomized split-lane builds, use and verify the disjoint lower and upper lanes in [Section B.5.3](#sec-simultaneous-tx-setup-5-3) instead of expecting a fixed separation.

Practical fixed-frequency starting pairs for QMX, Virtual U3S and Ultimate3S are:

| Band | Lower signal | Upper signal |
|---|---:|---:|
| 40 m | `7.040050 MHz` | `7.040150 MHz` |
| 20 m | `14.097050 MHz` | `14.097150 MHz` |

These are actual radiated RF frequencies, not a receiver's USB dial frequency. A device may describe its programmed WSPR frequency as the signal center or as tone 0, depending on model and firmware. Follow the version-matched manual, then observe both transmitters together on a receiver, frequency counter or spectrum display and verify the expected placement: the actual 100 Hz separation for a fixed pair, or the intended lower and upper regions for randomized split lanes. Repeat the timing and frequency check after a restart or firmware change <a href="#ref-12">[Ref-12]</a>.

<a id="sec-simultaneous-tx-setup-3"></a>
#### B.3 Check power and simultaneous signal quality

1. Test each transmitter separately into a suitable dummy load or safely attenuated measurement path.
2. Measure actual RF power at the comparison plane appropriate to the question and report the nearest valid WSPR-encoded dBm value. For this test, WSPRadar recommends `20–30 dBm`; the valid encoded values in that range are `20`, `23`, `27` and `30 dBm`. Do not encode A/B identity through false dBm values. `20–30 dBm` is about `100 mW–1 W`. Do not use excessive power; use no more than the test needs <a href="#ref-12">[Ref-12]</a>.
3. Operate both transmitters together into loads and inspect frequencies, occupied bandwidth, harmonics, spurious products and intermodulation.

The two-transmitter result includes every uncontrolled difference between those complete paths. A clean individual signal is not enough; simultaneous operation is the condition that must be verified.

<a id="sec-simultaneous-tx-setup-4"></a>
#### B.4 Verify WSPRnet and the selected database

1. Transmit several complete synchronized sequences with the final callsign, locator, power, timing and frequency settings.
2. Search the [WSPRnet Spot Query](https://www.wsprnet.org/drupal/wsprnet/spotquery) for each exact callsign. Do not rely only on the map, which can show a last-known locator.
3. Check the intended grid-4, reported power, timestamps and separate frequencies.
4. Find cycles in which the same remote receiver reported both callsigns and verify matching timestamps.
5. For a two-transmission sequence, check both positions against the known schedule; the database need not label them explicitly as Type 2 and Type 3.
6. Run a short WSPRadar preflight and wait until the test spots are actually queryable there. wspr.live describes a delay of a few minutes; individual uploads or database availability can take longer. Start from actual data availability, not a fixed waiting period; see [Section 5.6](#sec-6-6).
7. Once the spots are available, inspect unexpected concentrations of Only Target or Only Reference, then compare Joint Evidence Share, one-sided outcomes and Joint-Spot ΔSNR between the two sequence positions. A persistent phase difference flags a need to check hash resolution, frequency placement, transmitter heating and power sag. Identify the sequence positions from the timestamps and known transmission schedule, using exported evidence or an external decoder log; WSPRadar does not label message phases or provide a message-phase filter.

Do not start the measurement window until both exact callsigns appear consistently at their intended reported locations and common receivers report both signals in the intended cycles. A successful preflight applies only to the tested combination of transmitters, firmware, decoders and data source.

<a id="sec-simultaneous-tx-setup-5"></a>
#### B.5 Device-specific setup

The following examples are starting procedures, not substitutes for the manual that matches the installed firmware. Re-run the full timing, frequency, power and database preflight whenever firmware or configuration changes.

<a id="sec-simultaneous-tx-setup-5-1"></a>
<a id="sec-simultaneous-tx-setup-5-2"></a>
##### B.5.1–B.5.2 QMX and QMX+ Virtual U3S, and Ultimate3S

The physical Ultimate3S provides a sequence of up to 16 programmable mode entries, each with its own frequency. QRP Labs describes current QMX and QMX+ Virtual U3S as an implementation of the Ultimate3S architecture, so the operator workflow is effectively the same where the exact installed Virtual U3S version exposes and follows these settings. Verify that version rather than assuming complete behavioral identity. The RF hardware is not the same: firmware, oscillator, filtering and output-stage differences remain part of the complete paths being compared <a href="#ref-12">[Ref-12]</a>.

1. For QMX or QMX+, install the current firmware approved for the exact model and follow its version-matched Virtual U3S instructions. Do not use the initial `1_04_000` release as a general QMX recipe; QRP Labs identifies it as QMX+-specific and later releases include Virtual U3S corrections. For a physical Ultimate3S, fit the correct output filter for the selected band.
2. Enter the two exact callsigns, the same truthful locator and each unit's measured power using the nearest valid WSPR-encoded dBm value. Ordinary Type 1 callsigns are preferred. If compound callsigns are used, configure the same extended-WSPR arrangement on both units and verify that the Type 2 and Type 3 phases remain aligned.
3. Give both units accurate UTC from GNSS or another documented time reference. Use the same deterministic global `Frame` and the same observed even-minute `Start`, and disable unrelated entries so one arm cannot insert an extra transmission. The physical Ultimate3S treats `Start = 00` specially as “not used,” so verify the displayed and observed starts.
4. Program full RF frequencies nominally 100 Hz apart and keep both complete signals comfortably inside the 200 Hz WSPR sub-band. Suitable starting pairs include `7.040050 MHz` and `7.040150 MHz` on 40 m, or `14.097050 MHz` and `14.097150 MHz` on 20 m. These are actual RF frequencies, not receiver USB dial frequencies. Follow the installed firmware's tone convention and verify the radiated signals rather than trusting the displayed values alone.
5. Test each unit alone, both together into loads, and finally at the intended low on-air power. Complete the power, simultaneous-signal and database checks above before collecting the experiment.

**Use a fixed frequency-swap schedule.** Do not permanently assign the Target to the lower frequency and the Reference to the upper frequency. Narrowband QRM, another WSPR signal, receiver passband response or frequency-dependent transmitter response could then favor one path. Instead, program complementary entry sequences so the paths exchange frequency positions between successive scheduled pairs while their callsigns continue to identify Target and Reference.

For ordinary Type 1 callsigns, a practical sparse Ultimate3S starting schedule uses two enabled WSPR entries per unit, a common `Frame = 20` and a common observed even-minute `Start`, for example `Start = 04`. Use the same plan on QMX or QMX+ only after confirming that its installed Virtual U3S version follows this sequence behavior. Program the Target entries lower then upper, and the Reference entries upper then lower. Each verified two-entry sequence produces two consecutive same-cycle A/B pairs and then pauses until the next 20-minute frame. Each transmitter therefore uses two of every ten WSPR cycles, or `20%` of the available cycles.

| Same-cycle observation | Target RF position | Reference RF position |
| ---: | ---: | ---: |
| 1 | lower (`+50 Hz`) | upper (`+150 Hz`) |
| 2 | upper (`+150 Hz`) | lower (`+50 Hz`) |
| 3 | lower (`+50 Hz`) | upper (`+150 Hz`) |
| 4 | upper (`+150 Hz`) | lower (`+50 Hz`) |

Here `+50 Hz` and `+150 Hz` are offsets from the lower edge of the selected 200 Hz WSPR sub-band; the exact full RF values depend on the band. Pairs 1–2 form one two-entry sequence and pairs 3–4 the next. Every A/B observation still shares the same WSPR cycle and propagation interval, while equal use of the two frequency positions balances sensitivity to fixed frequency-position effects over successive measurements. It reduces that confounding; it does not prove that frequency effects have been removed. Inspect both sequence positions separately during the preflight. If compound callsigns are used, do not copy this Type 1 example blindly: build and verify a version-matched schedule that preserves the complete Type 2/Type 3 sequence on both paths.

<a id="sec-simultaneous-tx-setup-5-3"></a>
##### B.5.3 ZachTek firmware 2.19 randomized split-lane builds

Stock ZachTek firmware `2.19` for the published ESP8285 source selects a new random offset from approximately `-100 Hz` through `+99 Hz` around the nominal WSPR frequency. Two stock units therefore do not retain separate A/B frequency regions and can occasionally transmit close to one another. For a controlled simultaneous pair, prepare two separately labelled custom firmware builds from the source that matches the exact transmitter <a href="#ref-29">[Ref-29]</a>.

Confirm that both units use the same nominal frequency at the center of the selected 200 Hz WSPR transmit sub-band. The custom offsets below then divide that range into separate lower and upper regions.

In `DoWSPR()`, the published source contains this statement twice: once after the first `NextFreq()` and again after the later band-cycle `NextFreq()`:

```cpp
freq = freq + (100ULL * random (-100, 100));
```

Replace **both** occurrences in transmitter A's source copy with:

```cpp
freq = freq - (100ULL * random(31, 91));
// random lower lane: -90 through -31 Hz
```

Replace **both** occurrences in transmitter B's source copy with:

```cpp
freq = freq + (100ULL * random(30, 90));
// random upper lane: +30 through +89 Hz
```

`freq` uses `0.01 Hz` units. The lower and upper lanes are therefore disjoint and command at least `61 Hz` separation between their tone-zero positions, while each transmitter still changes frequency from one WSPR sequence to the next. The four nominal WSPR tone frequencies span only about `4.4 Hz`, so the closest commanded tone centers of the two signals remain separated by roughly `57 Hz` or more even at the nearest lane positions. The tone-zero endpoints retain about `10 Hz` of margin relative to each outer edge of the roughly ±100 Hz range used by the stock randomization. Because of the tone span, however, the highest tone in the upper lane lies only about `6.6 Hz` below the nominal `+100 Hz` edge. Measure the actual radiated positions and confirm that both complete signals remain inside the transmit sub-band.

Randomized split lanes have an advantage over fixed A/B frequencies: a persistent narrow interferer or local decoder-frequency anomaly is less likely to affect every observation at exactly the same frequency. The design does not, however, remove a systematic lower-versus-upper passband effect because transmitter A always occupies one side and transmitter B the other. For a confirmatory repetition, exchange the lane assignments:

```text
Run 1: A = lower random lane, B = upper random lane
Run 2: A = upper random lane, B = lower random lane
```

An observed advantage that follows the physical antenna or transmit path after this reversal is stronger evidence than one that follows the frequency lane.

Changing only one occurrence of the source statement is insufficient because a later band cycle could return to stock random placement. A following Type 3 transmission uses the **same selected frequency** as its preceding Type 2 partner; the firmware selects a new random lane position only for the next band or sequence. This is a source-code modification, not an option in the ZachTek configuration program.

Before compiling, confirm that the source and its `Product_Model` match the exact hardware. The cited published file selects model `1048`; an incorrect model can select the wrong relay or filter behavior. Follow the ESP8285 and NeoGPS build prerequisites in the source header, retain a recoverable stock firmware image and configuration record, and record the source revision, patch and binary hash.

After flashing, test each transmitter separately and then both together into dummy loads or a safely attenuated arrangement. Verify actual RF frequency, timing, output power, filtering and spectral purity before connecting antennas. During a short on-air preflight, also confirm that the observed frequencies remain inside their intended lower and upper lanes and that both identities produce adequate Joint Spots from the same cycles before beginning the measurement run.

<a id="sec-simultaneous-tx-setup-6"></a>
#### B.6 Confirm by exchange or crossover

Use the first run to establish whether a pattern is worth confirming. Before a second run, keep the band, window, schedule, powers, filters and primary evaluation scope fixed, then exchange the two frequency positions. This exposes receiver-passband shape, local QRM and frequency-dependent transmitter response. Where practical, also cross the antennas or tested components between the two transmitter chains while documenting everything else that moved.

Preserve the original, frequency-exchanged and hardware-crossover runs separately. Do not pool them unless Target/Reference roles, corrections and analysis scope are aligned. Agreement across these controlled runs is experimental repeatability; agreement between Type 2 and Type 3 phases inside one run is only within-run consistency.

<div style="page-break-before: always;"></div>

<a id="sec-b"></a>
<a id="sec-reference-snr-calibration"></a>
### Appendix C: Reference SNR Calibration

This procedure estimates a stable additive offset between receive chains or Reference-side paths.

1. **Common input:** feed both receive chains from one stable antenna through a suitable splitter and controlled cables.
2. **Characterize the splitter:** account for output imbalance and cable differences; swap outputs in a control run when practical.
3. **Collect Joint Spots:** use `0.0 dB` Reference SNR Correction for the offset-estimation run, then operate simultaneously across the intended signal levels without changing gain or decoder settings.
4. **Derive the offset:** use the ΔSNR values of the Joint Spots and state whether the value was calculated from station-balanced summaries or pooled Joint Spots.
5. **Check consistency:** inspect by station, time and SNR. One constant is not defensible if offset changes with level, frequency, AGC or time.
6. **Apply the sign:** enter the observed `target - reference` offset with the same sign.
7. **Validate:** repeat or swap paths and confirm corrected common-input ΔSNR is plausibly near zero.

Consistency across station, time and SNR views supports using one additive offset within the tested setup; it does not establish traceable laboratory accuracy. Splitter loss, mismatch, coupling and source instability can remain.

<a id="sec-license"></a>
### License

WSPRadar is licensed under the GNU Affero General Public License version 3 (AGPLv3). The repository `LICENSE` file is controlling. Bundled Rajdhani and Space Mono font files retain their separate SIL Open Font License 1.1; see `static/fonts/` for copyright notices and license texts.
