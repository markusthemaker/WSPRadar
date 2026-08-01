# WSPRadar.org

HAM RADIO STATION & ANTENNA BENCHMARKING

<a id="sec-1"></a>

### 0. Why WSPRadar?

Radio amateurs continually modify and improve their stations. A new antenna goes up, mast height changes, a feedline is replaced, a balun is reworked or a preamplifier is added. The same question follows almost automatically: **Did the change actually improve the station — and if so, where, when and by how much?**

On the air, this can initially seem easy to answer. With the new antenna, more contacts are completed, a remote operator gives a better signal report, a WebSDR shows a stronger signal or WSPR produces more spots. Such observations are valuable, but they do not measure the antenna or changed component alone. The observed result always arises from the complete station interacting with the radio path: antenna, feedline, radio, transmit power, receiver, local noise, interference, terrain, ionosphere, remote station and time all contribute at once.

This is the fundamental measurement problem. Different outcomes need not have been caused by the hardware under test. A better signal report may reflect a more favorable phase of propagation, an additional contact may involve a different remote station, and a higher spot count may reflect changing station activity or better conditions. Even completely accurate observations therefore do not automatically identify the cause.

Experienced radio amateurs address this problem with increasingly controlled methods: repeated comparisons, beacon transmissions, WebSDRs, analysis of the Reverse Beacon Network (RBN) or WSPR, and especially rapid live A/B switching. Such a live A/B test is far more informative than two contacts made at different times. Transmitter, transmit power, frequency, remote station and much of the radio path remain largely the same. Established WSPR comparison experiments likewise show that common conditions and the shortest practical — or simultaneous — comparisons are more robust than long separated measurement blocks <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-3">[Ref-3]</a> <a href="#ref-4">[Ref-4]</a> <a href="#ref-5">[Ref-5]</a>.

Yet even a careful rapid A/B comparison is normally a sequential rather than truly simultaneous measurement, made on one radio path within a short time window. QSB, multipath propagation, interference and local noise can change during the switch. AGC, S-meter resolution and subjective reports further limit the observable difference. An observed advantage may be real, but initially applies only to that remote station, direction, time and propagation state.

The real challenge is therefore not merely to observe a difference. It is to determine **whether that difference repeats under many comparable conditions, how large it typically is, on which radio paths it appears and how much evidence supports it.**

This is where WSPR provides an unusually suitable foundation. Its repeated, time-stamped and machine-decoded low-power transmissions create observations across many stations, distances, directions and propagation states within a worldwide volunteer network <a href="#ref-6">[Ref-6]</a> <a href="#ref-7">[Ref-7]</a> <a href="#ref-8">[Ref-8]</a>. WSPRadar does not turn those observations into a calibrated antenna range. It organizes them into a more controlled, semi-quantitative and auditable station experiment: comparable conditions are brought together, station activity is checked, differences in reported transmit power are accounted for, and the result remains traceable to the contributing stations and spots.

Depending on the band, station activity and selected time window, hundreds to thousands of observations can accumulate over hours or days. Repetition across many radio paths and propagation states helps distinguish chance events from recurring patterns and supports semi-quantitative statements about the magnitude, geographic distribution and persistence over time of an observed difference or pattern. This is not a calibrated laboratory measurement, but it can provide a solid technical and scientific evidence base for evaluating the complete station under real operating conditions.

Used this way, WSPR becomes more valuable to the wider amateur community as well. Accurate callsigns, locators and power reports, stable operation and documented changes turn routine WSPR beaconing into evidence that can be reused rather than merely watched.

<a id="sec-1-0"></a>

#### 0.0 What WSPRadar can show

WSPRadar evaluates one <strong class="defined-term">Target</strong> under one explicit experiment design. The Target can be a complete installed station or one controlled hardware path. It can be evaluated on its own or against a meaningful <strong class="defined-term">Reference</strong>. Depending on the question, the Reference can be a second controlled path at the same station, one known external station, the active local WSPR neighborhood or its strongest active member.

The Reference is part of the scientific question, not merely a display option. A <strong class="defined-term">Hardware A/B Test</strong> can narrow the comparison to two local antennas, feedlines, receivers or complete receive chains when the remaining variables are held stable. A <strong class="defined-term">Reference Station / Buddy Test</strong> compares two complete stations, including their QTHs, equipment, terrain and noise environments. A Local Neighborhood Benchmark asks how the Target compares with a changing population of active nearby WSPR stations. <strong class="defined-term">Performance</strong> evaluates the Target itself from independently confirmed opportunities. <strong class="defined-term">Compare</strong> evaluates the Target relative to a Reference using matched evidence. In Performance, <strong class="defined-term">qualifying evidence</strong> is the Target and independent-activity evidence retained after the run's eligibility rules.

Performance describes the observed conditional behavior of the complete Target station within independently confirmed WSPR opportunities. It is not an absolute measurement of receiver sensitivity, radiated power, antenna gain or antenna efficiency.

These designs are not interchangeable. A Buddy or neighborhood result cannot isolate antenna gain because station location, hardware and noise remain part of the comparison. A Hardware A/B result narrows the cause only as far as the experiment actually controls the rest of the chain. No later statistic can remove a variable that the operating design never controlled.

The method builds on established WSPR comparison ideas: same-receiver TX differences under common conditions, conditioned simultaneous RX comparisons, independent activity checks where operating schedules are unknown, and the practical lesson that slow alternation can be confounded by propagation <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-9">[Ref-9]</a> <a href="#ref-3">[Ref-3]</a>. WSPRadar integrates and extends that foundation with Target-activity qualification, purpose-built benchmark designs, same-cycle or deterministic schedule matching, reported-power normalization, separate Performance evidence, paired Delta SNR and Decode Outcomes, station-balanced geographic summaries and drill-down to the contributing evidence. [Chapter 6](#sec-d) documents this lineage, WSPRadar's additions and their boundaries.

The intended conclusion is therefore bounded but operationally useful: **under this band, UTC window, station population and experiment design, what conditional behavior did the Target show; when a Reference was selected, where and when did the relative difference appear; and how much evidence supports the result?** WSPRadar can show the Target's observed conditional behavior or an observed relative advantage and its geographic or temporal scope. It does not directly measure isolated gain in dBi, radiation efficiency, take-off angle, receiver sensitivity or radiated power; those require separate calibrated measurements.

<a id="sec-1-1"></a>

#### 0.1 WSPR in 2 Minutes

<strong class="defined-term">WSPR</strong> stands for **Weak Signal Propagation Reporter**. Joe Taylor, K1JT, and Bruce Walker, W1BW, described it as a worldwide network of low-power stations exchanging beacon-like transmissions to probe possible propagation paths. A WSPR-2 transmission lasts just under two minutes and occupies about 6 Hz. Its message normally contains a callsign, a four-character Maidenhead locator and reported power in dBm; `30 dBm` (`1 Watt`) is WSPRadar's normalization reference. It can be decoded at about `-28 dB` signal-to-noise ratio (SNR) in a 2500 Hz reference bandwidth <a href="#ref-6">[Ref-6]</a> <a href="#ref-8">[Ref-8]</a>. A less negative SNR means a stronger signal relative to noise.

When reporting is enabled, a receiver uploads each successful decode as a <strong class="defined-term">spot</strong>. A spot records transmitter and receiver identity, reported location, time, band, power and decoder-reported SNR. WSPRadar uses wspr.live as its primary WSPR data source <a href="#ref-10">[Ref-10]</a>, with WSPRDaemon WD2 and WD1 as fallback sources <a href="#ref-11">[Ref-11]</a>. wspr.live is a public ClickHouse database that stores WSPRnet-reported spots and checks for new reports every few minutes. A daily synchronization fills reports that were missed or uploaded late.

One limitation matters for every analysis: the archive contains successful decodes, not a complete log of every attempted transmission. WSPRadar therefore constructs an <strong class="defined-term">opportunity</strong>: a Target-active two-minute cycle with independent evidence that the relevant remote transmitter or receiver was active. In RX, another receiver must have decoded the same transmitter; in TX, the remote receiver must have decoded another signal on the same band. Without that supporting activity, a missing spot is not automatically counted as a radio failure.

<a id="sec-1-2"></a>

#### 0.2 Choose the question you want to answer

Start with the operating question, not with a map or metric. The question determines the Direction, Benchmark Design and evidence that can support the answer:

| Your question | Choose |
|---|---|
| Where is my transmitter decoded among receivers independently shown to be active? | TX Analysis with `Performance — no Reference` |
| Which signals independently confirmed elsewhere does my receiver also decode? | RX Analysis with `Performance — no Reference` |
| Did controlled local antenna, feedline or hardware path A differ from path B? | Hardware A/B Test |
| How does my complete station compare with one known station? | Reference Station / Buddy Test |
| Am I broadly typical for nearby active WSPR stations? | Local Neighborhood Benchmark with Local Median Neighborhood |
| How do I compare with the strongest active local peer on each path and cycle? | Local Neighborhood Benchmark with Local Best Station |

Choose <strong class="defined-term">TX (transmit) Analysis</strong> when the Target callsign is transmitting. The remote receiving stations that supply evidence become the mapped <strong class="defined-term">peers</strong>.

Choose <strong class="defined-term">RX (receive) Analysis</strong> when the Target callsign is receiving. The remote transmitting stations that supply evidence become the mapped peers. The configured <strong class="defined-term">QTH</strong> is the Target station location used as the map center and local-radius origin.

Choose the narrowest design that matches the intended claim. A hardware-cause question requires a controlled Hardware A/B design. A Buddy or Neighborhood result remains whole-station evidence because QTH, equipment and noise are part of the comparison. No amount of later aggregation can turn an uncontrolled station comparison into isolated antenna gain. [Chapter 1](#sec-2) provides the operating playbook for each choice.

<a id="sec-1-3"></a>

#### 0.3 What one run produces

Every run freezes one <strong class="defined-term">Direction</strong>, one exact band, one Target identity and one resolved UTC window. Its <strong class="defined-term">Benchmark Design</strong> selects exactly one active result type. A run produces an evidence package for that defined question, not a universal score for the station.

* <strong class="defined-term">Performance</strong> evaluates the Target itself from independently confirmed opportunities. It reports Decode Rate, at-least-once reach, successful Target SNR and temporal behavior without introducing a Reference.
* <strong class="defined-term">Compare</strong> evaluates the Target relative to a Reference using matched evidence. It reports paired **Delta SNR** and **Decode Outcomes**. Delta SNR is Target-side SNR minus Reference-side SNR after any configured Reference correction. Positive values favor the Target; negative values favor the Reference. Decode Outcomes retain both paired evidence and cases where only one side was decoded.

Performance and Compare answer different questions. WSPRadar keeps them separate so that a single attractive number cannot hide weak opportunity coverage, one-sided decodes or a paired subset that represents only part of the evidence.

Results open on a map and then follow the same concise evidence path for Performance and Compare: **Map → Segment Inspector → Station Insights → Drill-Down**.

The map locates the observed pattern; it is the start of the analysis, not the conclusion. The Segment Inspector defines the distance-and-direction scope inherited by the evidence sections and Station Insights. Station Insights shows which identities contribute. Selected Station Evidence and Drill-Down expose the station-specific views and the observations, same-cycle pairs or scheduled TX A/B pairs behind the summaries.

A strong result is one in which the run definition, station breadth, observation volume, geographic and time pattern, and underlying rows are mutually consistent and support the same bounded interpretation. Repeating the same design across another suitable window can show whether that interpretation persists.

The aim is a clear operating conclusion: **what differed, where and when, relative to which Reference, by how much, and with how much supporting evidence.**

<a id="sec-1-4"></a>

#### 0.4 Your first useful run: start with a guided demo

The quickest way to learn WSPRadar is to run a maintained demo before configuring your own station. In the default Guided input view, open `Load Demo`, select a profile and choose **`Load Selected Demo Configuration`**. Its title and description appear first, including a publication or source link when the profile supplies one; the preset scientific steps remain collapsed underneath. Choose **`Walk me through the setup`** to inspect the pre-populated applicable steps in order; **`Continue`** advances to the next applicable step. Choose **`Skip to review and run`** to open the complete final review immediately. Neither choice starts the analysis; start it explicitly with `Run RX Analysis` or `Run TX Analysis`. The Classic input view additionally offers **`Run Selected Demo`** for an immediate unchanged launch.

For the first pass, leave the scientific controls unchanged. An unchanged loaded profile remains a guided demo. Editing a scientific control changes the experimental question and turns the profile into an ordinary analysis. A demo is a worked example of WSPRadar's method, not evidence about your own station.

When the results open, follow the evidence path introduced above. The Performance Evidence, Comparison Evidence, Temporal Evidence and Selected Station Evidence sections remain available at their applicable points in that workflow.

Use [Section 2.1](#sec-3-2) when the demo's active result is Performance. When its active result is Compare, read [Section 2.2](#sec-3-3) before interpreting Delta SNR or Decode Outcomes. Then return to [Section 0.2](#sec-1-2), choose the experiment design that matches your station question, and configure your first station run.

<a id="documentation-toc"></a>

### Table of Contents

**Part 0: Preface**

* [0. Why WSPRadar?](#sec-1)
    * [0.0 What WSPRadar can show](#sec-1-0)
    * [0.1 WSPR in 2 Minutes](#sec-1-1)
    * [0.2 Choose the question you want to answer](#sec-1-2)
    * [0.3 What one run produces](#sec-1-3)
    * [0.4 Your first useful run: start with a guided demo](#sec-1-4)

**Part I: Operator Guide**

* [1. Experiment Playbooks](#sec-2)
    * [1.1 A strong foundation for every experiment](#sec-2-1)
    * [1.2 Performance only: evaluate the Target](#sec-2-2)
    * [1.3 RX Hardware A/B: compare simultaneous receive paths](#sec-2-3)
    * [1.4 TX Hardware A/B: choose simultaneous or sequential transmit paths](#sec-2-4)
        * [1.4.1 Simultaneous TX playbook](#sec-2-4-simultaneous)
        * [1.4.2 Sequential TX playbook](#sec-2-4-sequential)
    * [1.5 Reference Station / Buddy Test](#sec-2-5)
    * [1.6 Local Median Neighborhood](#sec-2-6)
    * [1.7 Local Best Station](#sec-2-7)
* [2. Read Your Results](#sec-3)
    * [2.1 Read a Performance result](#sec-3-2)
    * [2.2 Read a Compare result](#sec-3-3)
    * [2.3 Use the map to locate the observed pattern](#sec-3-4)
    * [2.4 Check map support counts](#sec-3-5)
    * [2.5a Inspect a Geographic Segment (Performance Mode)](#sec-3-6a)
    * [2.5b Inspect a Geographic Segment (Compare Mode)](#sec-3-6b)
    * [2.6a Inspect the Contributing Stations (Performance Mode)](#sec-3-7a)
    * [2.6b Inspect the Contributing Stations (Compare Mode)](#sec-3-7b)
    * [2.7 Verify the underlying evidence](#sec-3-8)
    * [2.8 Worked Compare example](#sec-3-9)
* [3. Strengthen and Communicate Your Result](#sec-4)
    * [3.1 Judge breadth, consistency and repeatability](#sec-4-1)
    * [3.2 Strengthen a result through repetition and control](#sec-4-2)
    * [3.3 Write an evidence-matched conclusion](#sec-4-3)
    * [3.4 Preserve the run and its context](#sec-4-4)

**Part II: Controls and Troubleshooting**

* [4. Controls and Configuration](#sec-5)
    * [4.1 Workflow controls](#sec-5-1)
    * [4.2 Target and measurement-window controls](#sec-5-2)
    * [4.3 Results-view and benchmark controls](#sec-5-3)
    * [4.4 Filters and evidence thresholds](#sec-5-4)
    * [4.5 Map, inspector and export controls](#sec-5-5)
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
    * [6.4 Analysis infrastructure and operator tools](#sec-d-4)
    * [6.5 What WSPRadar inherits, integrates and adds](#sec-d-5)
* [7. Scientific Methods](#sec-7)
    * [7.1 Data source, decode selection and time model](#sec-7-1)
    * [7.2 Identity and matching rules](#sec-7-2)
    * [7.3 Target-Active Gate](#sec-7-3)
    * [7.4 Performance classification and formulas](#sec-7-4)
    * [7.5 Power normalization, correction and Delta SNR](#sec-7-5)
    * [7.6 Paired evidence and Decode Outcomes](#sec-7-6)
    * [7.7 Aggregation hierarchy](#sec-7-7)
    * [7.8 Distributions and inspection-layer weighting](#sec-7-8)
    * [7.9 Geography and solar classification](#sec-7-9)
* [8. Evidence-Matched Claims and Reproducibility](#sec-8)
    * [8.1 Claims the evidence supports](#sec-8-1)
    * [8.2 Interpretation boundaries: what remains combined or unobserved](#sec-8-2)
    * [8.3 Reporting checklist](#sec-8-3)
    * [8.4 Analysis export package](#sec-8-4)
    * [8.5 Disclaimer](#sec-8-5)
* [References](#sec-ref)

**Part IV: Practical Supplements**

* [Appendix A: Parallel WSJT-X Instances](#sec-a)
    * [A.1 Create the second instance](#sec-a-1)
    * [A.2 Clone the starting configuration if required](#sec-a-2)
    * [A.3 Separate every data path](#sec-a-3)
    * [A.4 Configure distinguishable simultaneous TX](#sec-a-4)
* [Appendix B: Sequential TX A/B Scheduling and Switching](#sec-b)
    * [B.1 Requirements for a valid scheduled experiment](#sec-b-1)
    * [B.2 WSPRadar Timed A/B Relay Switch](#sec-b-2)
    * [B.3 Ultimate3S schedule example](#sec-b-3)
    * [B.4 QMX schedule examples](#sec-b-4)
    * [B.5 Verify mapping and preserve the experiment](#sec-b-5)
* [Appendix C: Reference SNR Calibration](#sec-c)
* [License](#sec-license)

---

<a id="part-i"></a>

## Part I: Operator Guide

This part takes you from an operating question to a well-supported result. Use Chapter 1 to choose and operate the experiment, Chapter 2 to inspect the evidence, and Chapter 3 to strengthen, report and preserve the conclusion. Exact controls, processing methods and reproducibility details are collected in Parts II and III.

In this guide, the **experiment** is the physical on-air operation and station configuration. A **run** or **analysis** is WSPRadar's configured processing of the resulting observations. A **result** is the Performance or Compare evidence produced by that run.

---

<a id="sec-2"></a>

### 1. Experiment Playbooks

Choose the playbook that matches the question in [Section 0.2](#sec-1-2). Each playbook describes the minimum valid operating setup, the result it creates and its principal interpretation boundary. Exact controls are in Part II; matching, normalization and aggregation are defined once in [Scientific Methods](#sec-7).

<a id="sec-2-1"></a>

#### 1.1 A strong foundation for every experiment

A clear question and a stable physical setup make the result easier to interpret.

**Define the experiment and run**

* State the question and the variable under test in one sentence.
* State whether this is an exploratory run or a confirmatory repetition of an earlier pattern.
* Choose TX or RX Analysis, one exact band and the Benchmark Design.
* Enter callsigns exactly as uploaded. Prefer standard callsign forms; when the archive identity actually uses a suffix, retain it exactly, including `/P`, `/1`, `/QRP` or a terminal hyphen form such as `-1`.
* Verify the Target QTH. Performance and Compare identify the Target using the exact callsign together with the configured QTH's first four locator characters.
* Select a UTC window in which the Target was actually operating. Use a window long enough to cover the propagation states named in the intended conclusion; multi-day runs are preferable when the conclusion spans complete daily cycles.
* Record the antennas, feedlines, tuner, transmitter or receiver, decoder, software version, power, schedule and intentional changes.

Every run uses one exact band; combining bands would mix different propagation, activity, station populations and observability.

**Keep the physical experiment stable**

* Keep every non-tested variable as stable as practical.
* Keep station clocks synchronized.
* For TX, keep actual and reported power synchronized and stable unless power itself is under test. WSPR is commonly operated at low power; `20-30 dBm` is a common low-power range.
* For RX, keep gain, filtering, audio routing, decoder settings and upload behavior stable unless one of those is the tested variable.
* Confirm that each benchmark side operates as intended. The <strong class="defined-term">Target-Active Gate</strong> protects periods without observable Target activity, but it does not prove Reference uptime.

For an exploratory run, use the evidence ladder in [Chapter 2](#sec-3) to identify a possible pattern. Before a confirmatory repetition, define the primary geographic and temporal scope and keep direction, band, benchmark, filters, thresholds and schedule fixed unless the change itself is part of the stated test.

<a id="sec-2-2"></a>

#### 1.2 Performance only: evaluate the Target

**Question answered**

Where, when and how consistently does the Target produce qualifying evidence among remote stations or signals independently shown to be active, and what SNR is observed for successful Target decodes?

**What WSPRadar shows**

For this playbook, <strong class="defined-term">qualifying evidence</strong> is the Target and independent activity evidence retained after the run's identity, band, time, Target-activity, filter and threshold rules.

* **RX Performance** compares Target receiver decodes with independently confirmed remote transmitter-cycles.
* **TX Performance** compares Target transmitter decodes with remote receiver-cycles shown to contain other same-band activity.

There is no Reference station or Reference path. Performance evaluates the Target itself from independently confirmed opportunities. Decode Rate describes the observed conditional behavior within those opportunities, while successful Target SNR is a separate signal-strength summary conditional on actual Target decodes or reports. [Section 2.1](#sec-3-2) explains the operator classifications and weighting, and [Section 7.4](#sec-7-4) defines the exact denominator.

**Set up the analysis**

Choose `RX Analysis` or `TX Analysis`, enter the exact Target callsign and QTH, choose one band and an active UTC window, then select `Performance — no Reference`.

**Strengthen the evidence**

Use an operating window with observable Target activity and enough independent WSPR activity. Check geographic scope, stations, confirmed opportunities and time views. If only a few peers survive, extend the observation window or narrow the geographic or temporal scope of the conclusion. Change filters or thresholds only for a stated experimental reason and report the changed configuration as a separate run.

**Evidence-matched conclusion**

> For this Target, band, UTC window and selected peer population, the displayed Station-balanced Decode Rate summarizes how often the Target also produced qualifying evidence among the independently confirmed WSPR opportunities represented in the selected evidence. WSPRadar calculates one Decode Rate per qualifying peer and then gives every peer one equal vote.

In everyday station terms: among the worldwide WSPR activity that this run could independently verify and fairly test, the result shows how consistently your station also produced the expected TX or RX evidence. The successful-decode SNR view separately shows the signal strengths of the Target evidence that was actually decoded.

<a id="sec-2-3"></a>

#### 1.3 RX Hardware A/B: compare simultaneous receive paths

**Question answered**

Did two local receive paths differ while observing the same remote WSPR transmissions?

For a radio amateur, this can mean comparing two antennas, each feeding its own independently reporting receiver/decoder chain; two receivers fed from one antenna through a characterized splitter; preamplifiers, filters or feedlines; or two complete parallel receive chains.

**What WSPRadar shows**

Simultaneous RX Hardware A/B compares two local receiving paths at one station. The Target and Reference receivers observe the same remote transmitter identities in the same WSPR cycles. This is WSPRadar's closest design to a controlled same-signal hardware comparison.

Unless receiver, audio and decoder differences have been characterized, the result compares the complete receive paths rather than the antennas alone.

**Set up the experiment**

Select the UI choice `Compare — Hardware A/B` and operate two receivers simultaneously with different exact reporting callsigns. The identity controls show `Target callsign` and `Reference callsign` on the first row, followed by disabled `Target Locator` and `Reference Locator` fields. Both grid-4 values are derived from the first four characters of the `Target and measurement window` panel's Target QTH; enter only the exact callsign uploaded by the Reference receiver.

* The Target receiver uses the Target callsign and QTH.
* The Reference receiver uses the Reference callsign and reports from the same Target grid-4.

Hardware A/B has no independent Reference-QTH setting and does not store one in a saved configuration. Archive matching for both callsigns uses the Target QTH's first four characters. Both receivers must also be operated at the same physical test QTH; shared grid-4 matching cannot prove physical co-location.

Keep clocks, antenna routing, gain, audio paths, decoder settings and uploads controlled. Components intended to be common must be physically common; measure or document unavoidable differences between the two chains.

The run produces one RX Hardware Compare result. To answer the separate non-comparative Target question, run a second configuration with `Performance — no Reference`.

**Strengthen the evidence**

Document splitter balance, feedline differences, receiver gain, automatic gain control (AGC) behavior, clipping, decoder configuration and upload behavior. A measured Reference SNR correction can compensate for a stable offset; it cannot correct nonlinear or time-varying behavior.

[Appendix A](#sec-a) describes parallel WSJT-X instances. [Appendix C](#sec-c) describes Reference SNR calibration.

**Evidence-matched conclusion**

> Under the documented simultaneous RX setup, paired Delta SNR showed the observed difference between the Target and Reference receive paths for the shared transmitters, cycles and geographic scope.

In everyday station terms: for remote signals that both paths observed at the same time, the result shows which receive path tended to produce stronger decodes, where that difference appeared and how much shared evidence supported it.

<a id="sec-2-4"></a>

#### 1.4 TX Hardware A/B: choose simultaneous or sequential transmit paths

**Question answered**

Did two local antennas, feedlines or RF paths differ at one controlled test QTH?

**Choose the comparison method**

TX Hardware A/B offers two methods. `Simultaneous TX` is the default for a new configuration; `Sequential TX` retains the deterministic TX A/B Schedule alternative.

| Method | Principal advantage | Principal cost and interpretation boundary |
|---|---|---|
| **Simultaneous TX** | Each Joint Delta SNR is formed from Target and Reference decoded by the same remote receiver in the same two-minute WSPR cycle. Shared receiver hardware, receive antenna, noise environment and propagation time remove the sequential time gap in which QRM, short-term fading and ionospheric conditions can change. | Requires two distinguishable transmitter chains, exact power/correction control, separate callsigns and separated frequencies. Frequency-selective QRM or fading, coupling, intermodulation, near/far effects and chain differences can still bias the result. It compares the documented complete transmit paths, not automatically the antennas alone. |
| **Sequential TX** | Works with one transmitter switched between two RF paths or with two transmitter chains on non-overlapping schedules; the one-transmitter arrangement retains a common callsign and frequency reference. Coupling between simultaneously active transmitters is avoided. | The two observations are time-separated. Short, balanced alternation reduces but cannot eliminate propagation, interference, schedule and switching differences. |

The WSPR-cycle definition and Joint-pair processing are specified in [Sections 7.1](#sec-7-1) and [7.7](#sec-7-7). [Section 6.3](#sec-d-zander) explains the scientific basis and remaining limits of same-receiver, same-cycle TX comparison.

Choose from the hardware actually available and the claim you need to support. Simultaneous operation is not automatically superior if the two transmitter chains cannot be calibrated or isolated. Sequential operation is not simultaneous, even with adjacent WSPR frames.

For either method, operate both paths at the same physical test QTH and report locators within the configured Target grid-4. Hardware A/B derives both displayed grid-4 values from Target QTH rather than accepting an independent Reference location. Report actual transmitter power and document everything that is not common. The Hardware A/B run produces Compare only; use a separate `Performance — no Reference` configuration when the non-comparative Target question is also relevant.

<a id="sec-2-4-simultaneous"></a>

##### 1.4.1 Simultaneous TX playbook

**What WSPRadar shows**

Simultaneous TX Hardware A/B compares two deliberately synchronized, distinguishable WSPR signals at each remote receiver. Delta SNR is calculated only when that receiver decodes both the Target and Reference in the same UTC cycle. The standard Decode Outcomes also retain Target-only, Reference-only and asynchronous evidence; `Include Unpaired Evidence` includes stations represented only by exclusive or asynchronous evidence even when they have no qualifying joint evidence. One UTC cycle can therefore be joint at one receiver and one-sided at another.

The Target-Active Gate remains Target-centric: a cycle is eligible only when the Target was decoded somewhere. Within an eligible cycle, a receiver may still contribute one-sided Reference evidence. A cycle in which Reference was decoded but Target was decoded nowhere is excluded rather than counted as a Target loss. [Section 7.3](#sec-7-3) defines this boundary.

**Set up the experiment**

Select `Simultaneous TX`. The identity controls show `Target callsign` and `Reference callsign` on the first row, followed by disabled `Target Locator` and `Reference Locator` fields. Both grid-4 values are the first four characters of Target QTH from `Target and measurement window`. Use two different exact callsigns, report both paths within that configured grid-4, and operate the two complete transmit paths at the same physical test QTH.

A simultaneous two-TX WSPR comparison normally needs:

* different callsigns, so the decoder and reporting database can identify the two paths; and
* different, non-overlapping TX frequencies within the approximately 200 Hz WSPR sub-band.

Each WSPR signal occupies about 6 Hz. Using the same frequency risks a collision or, for identical waveforms, an inseparable combined field. Signals placed too close together can fail to decode or produce unreliable SNR reports. Zander's simultaneous method likewise uses separate callsigns and different frequencies in the same two-minute slot. <a href="#ref-1">[Ref-1]</a>

Different radio dial frequencies are not required. With two WSJT-X instances or radios on the normal WSPR dial frequency, choose different audio TX offsets within the WSPR passband. Ignoring split, XIT and transverter offsets, the approximate relation is:

$$f_{RF} \approx f_{dial} + f_{TX\ audio}$$

For example, the Target could use `Tx Freq = 1450 Hz` and the Reference `Tx Freq = 1550 Hz`, with both transmissions starting in the same UTC cycle. These values are illustrative: inspect the band, leave comfortable separation, and allow for frequency error, strong-signal leakage and occupied signals. WSJT-X exposes a WSPR TX-frequency control and red waterfall marker, although their placement varies between versions and can be easy to overlook. Its randomized `Tx Pct` operation does not by itself guarantee deliberate two-radio synchronization. <a href="#ref-12">[Ref-12]</a>

Calibrate both transmitter chains at the comparison point appropriate to the variable under test. For an antenna-only comparison, measure the actual RF power delivered to each antenna feed point, or correct measured transmitter output for feedline loss. If the complete transmit paths are under test, retain transmitter and feedline differences as part of the compared systems and document them rather than correcting them away. Report the actual power for each WSPR identity; reported-power normalization cannot correct an unmeasured transmitter-chain or feedline offset. [Section 7.5](#sec-7-5) defines this limit.

Two transmitter chains can also be characterized without simultaneous radiation through the Sequential TX calibration approach in [Section 1.4.2](#sec-2-4-sequential).

The strongest hardware check is a crossover repetition: exchange the antenna or component under test between the two calibrated transmitter chains while holding the role definitions and analysis scope fixed. This helps distinguish the device-under-test effect from a persistent chain effect.

**Evidence-matched conclusion**

> Under the documented simultaneous two-transmitter setup, same-receiver, same-cycle Delta SNR showed the observed difference between the Target and Reference transmit paths for the selected receivers and geographic scope.

In everyday station terms: for receivers that decoded both distinguishable signals in the same cycle, the result shows which complete local transmit path tended to produce stronger reports. It does not by itself assign that difference to one antenna unless the rest of the paths were controlled or crossed over.

<a id="sec-2-4-sequential"></a>

##### 1.4.2 Sequential TX playbook

<a id="sec-2-4-why"></a>

**What WSPRadar shows**

Sequential TX Hardware A/B assigns complete WSPR transmissions to Target and Reference from a time-locked schedule. WSPRadar then forms deterministic one-to-one scheduled pairs for each remote receiver identity and reports scheduled-pair Delta SNR plus one-sided Decode Outcomes.

**Set up the experiment**

Use the station's normal valid exact callsign for both paths, and ensure that both paths report the configured Target grid-4. Path identity comes from the deterministic UTC schedule, not from `/1` and `/2` suffixes or different reported powers.

In `TX A/B Schedule`, enter each physical path's **actual recurrence and UTC phase**. Do not infer those values solely from a transmitter's `Frame` label. Use a deterministic scheduler or controller; standard WSJT-X randomized transmit-percentage operation does not create a valid fixed A/B sequence. Exact controls and supported phases are in [Section 4.3](#sec-5-3), while device-specific schedules and switching procedures are in [Appendix B](#sec-b). <a href="#ref-12">[Ref-12]</a>

WSPRadar forms scheduled pairs automatically. Exact pair assignment, edge-window eligibility and micro-median aggregation are defined in [Sections 7.1](#sec-7-1) and [7.7](#sec-7-7).

Report the actual transmit power. Do not encode path identity through false reported-power values: TX normalization would turn an invented power difference into an artificial comparison offset. [Section 7.5](#sec-7-5) defines the calculation, and [Appendix C](#sec-c) describes defensible Reference-side calibration.

A dedicated Sequential TX calibration run can characterize the offset between two transmitter chains without simultaneous radiation. Assign the chains to non-overlapping schedule phases and operate them alternately through the same downstream RF path, or measure both at the same calibrated RF reference plane. Correct actual output power and feedline loss only when they lie outside the variable under test; otherwise the observed Delta SNR includes the chain offset.

Verify the physical schedule-to-path mapping without RF before starting. A reversed mapping labels the paths backwards and reverses the practical interpretation of the Delta SNR sign.

The run produces one sequential TX Hardware Compare result. It does not run a separate Performance analysis; use a distinct `Performance — no Reference` run for non-comparative Target evidence.

**Strengthen the evidence**

Control switch loss, feedline differences, antenna coupling, clock accuracy, schedule-to-path mapping and switching timing. Use the shortest practical separation and extend the run across the propagation periods relevant to the question.

Across a balanced run, random short-term variation may average down because both paths are repeatedly exposed to changing conditions. Systematic schedule-, switching- or time-of-cycle effects do not necessarily average down. When a small difference matters, repeat the experiment with the Target/Reference schedule assignments reversed and compare like-for-like runs as described in [Section 3.2](#sec-4-2).

[Section 6.3](#sec-d-toledo) gives the experimental lineage and explains why short alternation is preferable to long blocks <a href="#ref-3">[Ref-3]</a>.

**Evidence-matched conclusion**

> Under the documented time-locked schedule, scheduled-pair Delta SNR showed the observed difference between the Target and Reference switched paths for the selected receivers, times and geographic scope.

In everyday station terms: after repeatedly alternating the two RF paths, the result shows whether the Target or Reference path tended to produce stronger reports for the receivers and propagation periods represented in the run, while remaining sequential rather than simultaneous.

<a id="sec-2-5"></a>

#### 1.5 Reference Station / Buddy Test

**Question answered**

How did the Target station compare with one known external station during overlapping operation?

**What WSPRadar shows**

A Buddy Test compares two complete installed station systems. The comparison includes their locations, antennas, feedlines, transmitters or receivers, local noise, terrain, software and operating environments.

* In TX, Target and Reference are compared at the same remote receiver when both were decoded in the same cycle.
* In RX, Target and Reference receivers are compared on the same remote transmitter identity in the same cycle.

Same-cycle TX pairs therefore share one remote receiver, while RX pairs share one remote transmitter. This controls one endpoint of the comparison; it does not remove differences in QTH, radio path, station hardware, terrain or local noise.

**Set up the analysis**

Select `Compare — Known Reference Station`. The identity controls show `Target callsign` and `Reference callsign` on the first row, followed by `Target QTH` and `Reference Locator`. The Target values come from `Target and measurement window`. Unlike Hardware A/B, both Reference fields remain editable: enter the Reference's exact reporting callsign and its independently chosen four-character Maidenhead grid. WSPRadar matches each fixed side by exact callsign plus its own grid-4. Choose a Reference whose location, hardware, reported power and operating schedule you understand.

Both stations need overlapping operation on the same band. Verify Reference uptime independently. Apply a Reference SNR correction only when its calibration basis is defensible.

The run produces one TX or RX Compare result against the buddy. A non-comparative Performance result for the Target requires a separate `Performance — no Reference` run.

**Strengthen the evidence**

Document terrain, local noise, antennas, polarization, feedline loss, transmitter or receiver calibration, reported power and operating schedules for both stations. Check locator identity and collect enough shared remote peers.

The Target-Active Gate is asymmetric. Swapping Target and Reference can therefore change one-sided Decode Outcomes even when the sign of the shared paired Delta SNR reverses as expected.

A known Reference station is a meaningful comparison partner, not automatically a calibrated reference standard.

**Evidence-matched conclusion**

> For the shared paths and cycles in this run, paired Delta SNR and Decode Outcomes showed how the two complete installed stations compared under their respective operating environments.

In everyday station terms: this shows how your complete on-air station performed against your buddy's complete station on shared paths; it does not assign the observed difference to one antenna, receiver or location by itself.

<a id="sec-2-6"></a>

#### 1.6 Local Median Neighborhood

**Question answered**

How does the Target compare with the typical active WSPR evidence from stations around its configured QTH?

**What WSPRadar shows**

Local Median Neighborhood forms a dynamic Reference from active station identities inside the selected radius. For each qualifying cycle and path, the neighborhood median represents the active local group without allowing one high-volume identity to dominate.

The Reference can change from cycle to cycle. It is a local activity benchmark rather than one fixed or calibrated station.

**Set up the analysis**

Select `Compare — local neighborhood benchmark`, choose a radius from 10 to 250 km and choose `Local Median Neighborhood` under `Local Benchmark Method`.

Verify the Target callsign and QTH: exact callsign plus grid-4 selects Target spots, the exact callsign excludes the Target from the local pool, and the QTH defines the radius origin. Choose the primary radius from local geography and expected station density before interpreting the result; it should have a clear local meaning and enough active identities.

The run produces one Local Compare result. A non-comparative Performance result for the Target requires a separate `Performance — no Reference` run.

**Strengthen the evidence**

Inspect which local identities contribute and their evidence counts. Alternative scientifically defensible radii can be reported as a sensitivity analysis: a smaller radius can describe a more similar local environment but leave a fragile pool, while a larger radius can add contributors but mix different terrain, noise and station conditions. Do not retain only the radius producing the most favorable result.

Local stations can differ in antenna, hardware, schedule and reported-power accuracy. Report the primary radius, method, contributors, evidence counts and any sensitivity runs.

**Evidence-matched conclusion**

> Relative to the active median neighborhood inside the selected radius, the Target showed the displayed paired Delta SNR and Decode Outcomes for the observed paths and cycles.

In everyday station terms: this shows whether your station tended to perform above, near or below the typical active nearby WSPR group for the paths and times both sides could compare.

<a id="sec-2-7"></a>

#### 1.7 Local Best Station

**Question answered**

How does the Target compare with the strongest active local Reference available for each qualifying path and cycle?

**What WSPRadar shows**

Local Best Station forms a changing best-peer envelope from active station identities inside the selected radius. It is intentionally stricter than the neighborhood median and does not represent a local average.

**Set up the analysis**

Select `Compare — local neighborhood benchmark`, choose a radius from 10 to 250 km and choose `Local Best Station` under `Local Benchmark Method`.

Verify the Target callsign and QTH: exact callsign plus grid-4 selects Target spots, the exact callsign excludes the Target from the local pool, and the QTH defines the radius origin. Choose the primary radius from local geography and expected station density before interpreting the result; it must retain a meaningful and adequately populated local pool.

The run produces one Local Compare result. A non-comparative Performance result for the Target requires a separate `Performance — no Reference` run.

**Strengthen the evidence**

Inspect the changing local Reference contributors. Alternative scientifically defensible radii can be reported as a sensitivity analysis when the conclusion depends strongly on pool membership; do not retain only the radius producing the most favorable comparison.

Local contributors can differ in terrain, equipment, noise, schedule and reported-power accuracy. Report the changing best-peer definition rather than describing the result as a comparison with one fixed station.

**Evidence-matched conclusion**

> Relative to the strongest active local Reference selected for each qualifying path and cycle inside the stated radius, the Target showed the displayed paired Delta SNR and Decode Outcomes.

In everyday station terms: this shows how your station compared with the strongest qualifying nearby station available on each path and cycle, rather than with one permanently fixed competitor.

Exact local-pool membership and aggregation rules are in [Sections 7.2](#sec-7-2) and [7.7](#sec-7-7).

<a id="sec-3"></a>

### 2. Read Your Results

Read every run through the same evidence ladder:

* **Performance:** Map → Segment Inspector → Station Insights → Drill-Down.
* **Compare:** Map → Segment Inspector → Station Insights → Drill-Down.

* Confirm the result and run definition.
* Use the map to locate the observed pattern.
* Select the relevant distance and direction for further inspection in Segment Inspector.
* Read the applicable evidence figures for breadth, depth, weighting and time pattern.
* Inspect station-level evidence in Station Insights.
* Inspect one selected station, then drill down to row-level evidence.

The exact formulas, matching rules and processing hierarchy are in [Scientific Methods](#sec-7).

<a id="sec-3-1"></a>

<a id="sec-3-2"></a>

#### 2.1 Read a Performance result

Performance is the non-comparative Target result. It evaluates the Target itself from independently confirmed opportunities. The <strong class="defined-term">Decode Rate</strong> is the fraction of those qualifying opportunities in which the Target also produced the required evidence:

* **RX Performance:** of the remote transmitter-cycles independently confirmed by another receiver, how many did the Target receiver also decode?
* **TX Performance:** of the active remote receiver-cycles confirmed by other same-band decodes, how many also decoded the Target transmitter?

Performance describes the observed conditional behavior of the complete Target station within the retained opportunities. It is not an absolute measurement of receiver sensitivity, radiated power, antenna gain or antenna efficiency.

WSPRadar uses one direction-specific plain-language vocabulary throughout the visible Performance result:

* **RX:** <strong class="defined-term">Heard by Target</strong> means that the Target receiver decoded the remote transmitter in a confirmed opportunity; <strong class="defined-term">Heard by others only</strong> means that another eligible receiver decoded it but the Target did not. At station level, the same labels mean that a qualifying remote TX station was heard by the Target at least once or was heard only by other receivers during the run.
* **TX:** <strong class="defined-term">Target heard</strong> means that the active remote RX station decoded the Target transmitter; <strong class="defined-term">Other signals heard only</strong> means that it decoded another qualifying same-band signal but not the Target. At station level, the same labels mean that a qualifying remote RX station heard the Target at least once or heard only other signals during the run.
* **Audit-only evidence:** RX displays <strong class="defined-term">Heard by Target without independent confirmation</strong>; TX displays <strong class="defined-term">Target heard without independent RX-activity confirmation</strong>. These rows remain auditable but do not enter Decode Rate.

The novice-facing formulas therefore read `Heard by Target / (Heard by Target + Heard by others only)` for RX and `Target heard / (Target heard + Other signals heard only)` for TX. [Section 7.4](#sec-7-4) maps this presentation vocabulary to the canonical scientific and export terms without changing the calculation.

For example, if a remote transmitter was independently confirmed in eight qualifying cycles and the Target receiver decoded it in three, that peer's RX Decode Rate is `3 of 8 = 37.5%`. If an active receiver produced ten qualifying cycles and decoded the Target transmitter in four, its TX Decode Rate is `4 of 10 = 40%`.

The raw candidate population is globally sourced:

* RX can grow toward the globally active transmitters on the band during cycles in which the Target receiver was active.
* TX can grow toward the globally active receivers on the band during Target transmit cycles.

Only peers surviving the selected time, band, filters, geographic analysis scope and evidence thresholds contribute to the retained result. Peer rows whose distance from Target QTH is not strictly less than `Maximum peer distance from Target (km)` are excluded from scientific calculations, processed artifacts and exports as well as from the map and Inspector.

The <strong class="defined-term">Target-Active Gate</strong> remains deliberately global. Evidence from outside the geographic analysis scope may establish that the Target was operating in a cycle, but that out-of-scope peer does not enter scoped outcomes, rates, counts or exported evidence. This preserves the activity check without allowing remote peers to change the selected geographic result.

Each peer Decode Rate is calculated first. A Performance map segment then gives every qualifying peer identity one equal vote and displays the arithmetic mean of those station rates. This is the <strong class="defined-term">Station-balanced Decode Rate</strong>. Segment Inspector also shows the <strong class="defined-term">Opportunity-level Decode Rate</strong>, which gives every qualifying confirmed opportunity equal weight.

Decode Rate is not power-normalized. The successful Target SNR displayed beside it is normalized to reported 30 dBm.

A displayed `100%` means that the Target succeeded in every qualifying opportunity for the station or selected scope. It does not mean that every possible or scheduled transmission was decoded. Because Performance starts from a demanding, globally sourced opportunity population and then applies the configured geographic analysis scope, its practical meaning comes from geography, qualifying stations, confirmed opportunities, time and repetition rather than proximity to `100%`.

<a id="sec-3-3"></a>

#### 2.2 Read a Compare result

Compare keeps two evidence questions separate.

**Delta SNR**

Delta SNR asks: when Target and Reference both produced comparable evidence, which side had the stronger SNR and by how much?

In the operator view, Delta SNR is the Target-side SNR minus the corrected Reference-side SNR. The exact equation and correction convention are in [Section 7.5](#sec-7-5). Positive values favor the Target; negative values favor the Reference.

Paired Delta SNR is normally the primary quantitative comparison because the two sides share the closest available conditions:

* In simultaneous RX Compare, Target and Reference receivers measure the same remote transmitter. This reduces transmitter-power, waveform and shared-path differences within the pair.
* In same-cycle TX Compare, including simultaneous TX Hardware A/B and applicable Buddy or Local Neighborhood comparisons, the same remote receiver measures Target and Reference. This reduces receiver-hardware, antenna, local-noise and reporting differences within the pair.
* Sequential TX Hardware A/B uses deterministic scheduled pairs rather than same-cycle evidence.

**Decode Outcomes**

Decode Outcomes show joint and one-sided evidence inside and outside the paired subset:

* <strong class="defined-term">Joint / Joint Spots / Joint Pairs:</strong> qualifying paired evidence exists.
* <strong class="defined-term">Only Target:</strong> Target evidence exists without Reference evidence in the relevant comparison unit.
* <strong class="defined-term">Only Reference:</strong> Reference evidence exists without Target evidence.
* <strong class="defined-term">Both (Async):</strong> both sides have evidence for the peer identity, but no qualifying joint unit survives for that category.

Use Delta SNR to describe the paired strength difference and Decode Outcomes to describe the joint and one-sided decode evidence. A result can have a clear paired median while retaining substantial one-sided evidence; both observations belong in the conclusion.

Decode Outcomes do not reconstruct or power-normalize a missing-side SNR. In TX comparisons, interpret one-sided outcomes together with actual and reported transmit power. [Section 7.6](#sec-7-6) defines this boundary.

Same-cycle pairing reduces shared confounders but does not make separated stations or different hardware chains physically identical. In same-cycle comparisons, the Target-Active Gate protects Target downtime from being counted as failure, while Reference uptime still needs independent confirmation.


The following Compare views keep these quantities separate rather than combining them into one score. Absolute Delta SNR shows the paired Target-minus-Reference level, while Joint Evidence Share shows how much retained evidence was pairable. Neither turns one-sided outcomes into symmetric wins and losses.

<a id="sec-3-4"></a>

#### 2.3 Use the map to locate the observed pattern

The map is the geographic overview. Use its colors, category labels and markers to identify the distance and direction worth inspecting next.

**Map summary**

A <strong class="defined-term">median</strong> is the middle value after sorting, or the midpoint of the two central values when the count is even. It is less strongly moved by one unusually high or low value than the arithmetic mean.

* Compare segments show the median of qualifying station-level Delta SNR medians. Positive favors Target; negative favors Reference.
* Performance segments show the arithmetic mean of qualifying station Decode Rates after giving every qualifying peer one equal vote.

The Compare map uses a symmetric stepped dB color scale: deep-navy-to-teal sectors have negative Delta SNR and favor the Reference, while ochre-to-chestnut sectors have positive Delta SNR and favor the Target. Light yellow-green marks the display-neutral interval centered on `0 dB`, and its width matches the active whole-dB color step. This grouping is a presentation choice rather than a claim of sub-dB measurement resolution. Only exactly `0 dB` means equality, so the numerical value remains authoritative even inside the display-neutral color. Let `A` be the larger of `6 dB` and the largest absolute displayed station-balanced segment median. The color step is `max(1, ceil(A / 6)) dB`, where `ceil` rounds upward to the next integer, and the symmetric outer labelled tick is the smallest multiple of that step not below `A`. Every displayed median therefore lies at or inside a labelled tick, the scale shows at most 13 color classes and never narrows below `-6 dB` to `+6 dB`, and the color-bin boundaries extend a further half-step beyond the outer ticks. Because its limits and step sizes can differ between runs, compare maps by their numerical color-bar values rather than by color alone.

**Station markers, segment status and footer categories**

Read the category label as well as its color:

* Performance: sector fill is the only quantitative color layer and shows the Station-balanced Decode Rate for the distance-and-direction segment. For RX, a small solid dark-green marker means `Heard by Target` and a small solid light-grey marker means `Heard by others only`. For TX, the corresponding labels are `Target heard` and `Other signals heard only`. All visible station markers use one fixed size and encode neither individual Decode Rate nor evidence depth. Where identities share plotted coordinates, dark-green markers are drawn above light-grey markers; one visible location can still represent multiple `callsign + locator` identities.
* Compare: Joint is green, Both (Async) is yellow-orange, Only Target is purple and Only Reference is white.

A valid Performance sector at `0%` remains on the Decode Rate scale. `Insufficient evidence` is a different state: the sector does not meet the configured qualifying-evidence requirements and remains unfilled so the neutral base map shows through outside that scale. Insufficient evidence must not be read as measured `0%` Performance.

**Distance rings**

Near rings can be consistent with shorter skip or near-vertical incidence skywave (NVIS) behavior; far rings can be consistent with DX behavior. The rings describe path distance and are not direct elevation-angle measurements.

Map color locates the observed pattern. The following evidence levels show how broad and well-supported it is.

<a id="sec-3-5"></a>

#### 2.4 Check map support counts

* On Performance maps, the upper <strong class="defined-term">OPPORTUNITIES</strong> row describes denominator depth as `Heard by Target` plus `Heard by others only` for RX or `Target heard` plus `Other signals heard only` for TX. The lower <strong class="defined-term">STATIONS</strong> row uses the same two direction-specific labels to describe footprint breadth across distinct qualifying `callsign + locator` identities.
* On Compare maps, <strong class="defined-term">SPOTS</strong> or <strong class="defined-term">PAIRS</strong> describes qualifying observation or scheduled-pair volume.

For Compare, both rows are divided into Only Target, Joint, Both (Async) and Only Reference. Station categories assign each identity to one main category. Spot or pair categories count evidence volume, including exclusive observations associated with identities that also have joint evidence.

For RX Performance, both footer rows use `Heard by Target` and `Heard by others only`; the row heading distinguishes individual confirmed opportunities from qualifying TX-station identities. For TX Performance, both rows use `Target heard` and `Other signals heard only`, with the same opportunity-versus-station distinction. Exact counts appear inside segments when they fit; narrow segments follow the compact Compare-footer behavior and omit overlapping count text. Evidence without the independent confirmation required for the denominator and ineligible evidence are excluded because they do not enter Decode Rate.

Footer counts follow the retained geographic analysis scope. Many confirmed opportunities, spots or pairs from only a few Stations mean repeated evidence from a narrow identity base. Many Stations show wider identity and geographic participation.

Within result grouping, a reported callsign plus its full reported locator is an analysis identity, not proof of one unique physical station. Selected Target and Reference query matching follows the mode-specific rules in [Section 7.2](#sec-7-2). Suffixes, stale locators and locator changes can split or move a physical station in the evidence.

<a id="sec-3-6"></a>
<a id="sec-3-6a"></a>

#### 2.5a Inspect a Geographic Segment (Performance Mode)

Use `Segment Inspector` to select one or more distance ranges and compass directions. This opens the evidence behind the corresponding map area. Inspector selections can narrow the completed run's geographic analysis scope, but they cannot widen it or restore peer rows excluded by the maximum-distance control.

The scope summary separates station breadth from confirmed-opportunity depth. The `Stations` line shows the mode-specific station groups — `Heard by Target` and `Heard by others only` for RX, `Target heard` and `Other signals heard only` for TX — and a `Decode Rate`. This is the Station-balanced Decode Rate: every qualifying station receives one vote through its own Decode Rate. The station-group counts describe at-least-once reach and therefore do not form that rate's arithmetic numerator and denominator. The `Opportunities` line uses the same direction-specific outcome labels and shows the Opportunity-level Decode Rate, for which every confirmed opportunity receives one vote. Its displayed counts do form that rate's numerator and denominator. The two lines can consequently show different Decode Rates when evidence volume differs among stations.

After selecting distance ranges and directions, WSPRadar rebuilds every following Performance view from the full qualifying station population in that active scope. Station Insights filters, sorting, the direction-specific `Heard only by other stations.` or `Only other signals heard.` control, and row selections do not alter these segment-level figures.

The left panel asks whether a qualifying radio path succeeded at least once during the selected interval. In RX, **TX Stations Heard by Target at Least Once by Distance** shows the proportion of qualifying transmitters heard by the Target receiver. In TX, **RX Stations Hearing the Target at Least Once by Distance** shows the proportion of qualifying active receivers that heard the Target transmitter. Because one success is sufficient, this reach measure normally increases with a longer measurement interval. It is a breadth measure, not a reliability measure.

The center panel is **RX Decode Rate by TX-Station Distance** or **TX Decode Rate by RX-Station Distance**. It asks how reliably the Target succeeded among all confirmed opportunities. The Station-balanced Decode Rate line gives every station one vote. The Opportunity-level Decode Rate line gives every confirmed opportunity one vote. Their difference shows whether high-volume stations behave differently from the wider station population. High at-least-once reach with low Decode Rate means many paths opened at least once but were intermittent; low reach with high Decode Rate means fewer paths opened, but those paths were comparatively reliable.

The right panel is **Successful Target SNR by TX-Station Distance** for RX or **Successful Target SNR by RX-Station Distance** for TX. It describes only successful Target outcomes. WSPRadar first gives each station one median successful SNR, then summarizes those station medians within the same exact-distance bins using their median and spread. This prevents a frequently reporting station from dominating the distance profile. A missed signal has no Target SNR and cannot appear in this panel. Read this with Decode Rate: a rising successful SNR while Decode Rate falls can mean that weaker signals disappeared below the decode threshold, leaving only stronger successful survivors.

All three panels use the same deterministic bins of exact, unrounded calculated distance from the Target QTH rather than the map's coarse distance ranges. Empty bins and gaps between disjoint selected ranges remain missing evidence, not measured `0%`. The underlying bin aggregates retain qualifying-station, station-status, confirmed-opportunity, Target, counter-evidence and successful-SNR-station counts for scientific traceability, but the figure does not draw a support-count strip. Calculated distance inherits the precision of the reported Maidenhead locator; Grid-4 is not survey-grade positioning.

**Temporal Evidence** separates the same active geographic scope into two vertically aligned figures. For RX, their main titles are **RX Performance Temporal SNR Evidence: Target {callsign}** and **RX Performance Temporal Evidence: Target {callsign}**; TX uses the corresponding **TX Performance** titles, and both append the active scope. The upper figure keeps **Successful RX SNR Deviation over Time/by UTC Hour** for RX or **Successful TX SNR Deviation over Time/by UTC Hour** for TX. Each contributing TX station in RX, or RX station in TX, is centered on its own run median; the dashed `0 dB` line is therefore that station's typical successful level, and the median line summarizes stations, or stations and dates in the folded view. Fine Q1–Q3 rails bound the middle 50% of that same population only when at least five values contribute: one station-bin median per station chronologically and one station-date-hour median per station and represented date when folded. Each station with at least three successful Target SNR observations uses its median successful SNR over the complete selected UTC window as its baseline. Positive values mean successful signals were stronger than usual for their respective paths; negative values mean they were weaker. Stations below that SNR threshold remain fully included in the lower 2×2 figure. Across that lower figure, the shared column headers are **Evidence over Time ({time_bin} bins)** and **Evidence by UTC Hour (1 h bins)**. The chronological station-balanced upper row keeps the short **TX Stations** or **RX Stations** y-axis title, while the folded station row uses the denominator-explicit **Avg. TX Stations / Represented UTC Date** or **Avg. RX Stations / Represented UTC Date** y-axis title. In each chronological bin, every contributing qualifying station gives one total vote split between `Heard by Target` and `Heard by others only` for RX or `Target heard` and `Other signals heard only` for TX according to that station's own within-bin outcome ratio; the right-axis line is the Station-balanced Decode Rate. In each folded UTC-hour bin, total station-bar height is the average number of distinct station-date-hour presences over represented dates whose hour overlaps the selected analysis window. A station can count once on each represented date, and a represented date-hour with no evidence remains in the denominator with zero support. The green/grey components are a rate-partitioned support display: they allocate that average support using the unchanged folded Station-balanced Decode Rate, formed by first pooling each station's outcomes at that UTC hour across represented dates and then giving every distinct station one equal rate vote. The components therefore reproduce the rate line but are neither averages of station-date split votes nor direct counts of successful or counter-only stations per date. The chronological lower row keeps the short **Opportunities** y-axis title, while the folded row uses the denominator-explicit **Avg. Opportunities / Represented UTC Date** y-axis title. It counts every confirmed opportunity once chronologically and averages those outcome counts over the same represented dates when folded; the right-axis line is the unchanged Opportunity-level Decode Rate. One shared legend below the lower figure title identifies the green successful outcome, grey counter outcome and Decode Rate line. All four right axes use one zero-based Decode Rate scale with rounded headroom, while the left support axes scale independently. Chronological panels preserve the actual run sequence at the chosen `1 h`, `2 h`, `3 h`, `6 h`, `12 h` or `24 h` aggregation. Chronological `1 h` bars whose bins are anchored to UTC-hour boundaries are directly comparable in units with the folded averages; wider chronological bins are not directly comparable by height. UTC-hour panels use fixed one-hour bins. The single `N UTC dates folded` annotation reports the global number of represented dates, while each hour excludes dates whose slot lies outside the selected window. A represented date-hour inside the window remains in the denominator with zero when it has no evidence. A first or last UTC-hour slot that only partly overlaps the window still counts as one represented slot rather than being weighted by its exposure fraction, so a boundary-hour mean can be depressed. Folding requires at least two UTC dates; otherwise the chronological column expands and the localized unavailable message is shown. Empty or sparse rate bins are missing or thin evidence, not failures.

Read Peer Reach, the exact Segment Inspector rates, both green/grey temporal stacks and their right-axis Decode Rate lines, successful SNR and their station/opportunity support together. Agreement across supported distance bins, stations, opportunities and recurring time bins is stronger descriptive evidence than one pooled count or one temporal spike. Successful-SNR censoring remains possible because missed signals have no Target SNR. These views still do not establish independence, calibration, propagation mode or physical cause.

<a id="sec-3-6b"></a>

#### 2.5b Inspect a Geographic Segment (Compare Mode)

**Decode Outcomes** compare Joint, Only Target, Both (Async) and Only Reference composition at two levels. The left, hatched bar in each category assigns every `callsign + locator` station identity to one station outcome; the right, solid-blue bar counts processed spot evidence, or scheduled-pair evidence for sequential TX A/B. Each level is normalized against its own total, so the integer percentages compare composition rather than absolute station and spot counts. The total and Joint counts for each level appear in the summary lines above the figure. Read both levels together: station breadth establishes whether the paired Delta SNR describes much of the footprint or a narrower joint subset, while the spot/pair distribution shows where repeated evidence is concentrated. Spot-level Both (Async) includes exclusive observations from identities that also have Joint evidence.

**Station Medians (Delta SNR)** gives each contributing station one value: its median paired Delta SNR. Stations therefore receive equal weight. A distribution concentrated above or below zero shows a consistent Target- or Reference-favoring direction across the available paths. A wide or split distribution shows that the observed difference varies by path.

**Joint-spot or scheduled-pair Delta SNR** shows every consolidated same-cycle pair or every valid scheduled pair in sequential TX A/B. This view exposes spread, quantization and outliers, while allowing active stations to contribute multiple values. A shift between this distribution and Station Medians shows how observation volume differs from the station-balanced picture.

**Joint-spot or scheduled-pair Delta SNR over time** uses exactly the same observation-level evidence rows and selected distance/direction scope as the top-right Joint-Spot or Scheduled-Pair Delta SNR histogram. Station Insights row selections do not change this segment-level view. The left panel preserves each row's actual UTC date and time; the right panel folds the same evidence from all contributing dates onto one 24-hour UTC-hour axis. Fine Q1–Q3 rails bound the middle 50% of the raw paired values in a bin only when at least five Joint Spots or complete Scheduled Pairs contribute; sparse medians remain visible without rails.


**Compare Temporal Evidence Coverage** uses all retained Only Target, Joint and Only Reference outcomes rather than only the paired subset. Its station row gives each contributing station one total vote split by that station's outcome composition in the bin. Its lower row counts the actual comparison units: transmitter-cycles for RX, receiver-cycles for simultaneous TX, or Scheduled A/B Pairs for sequential TX. The two Joint Evidence Share lines show the paired fraction under equal-station and pooled-outcome weighting. They measure how much evidence was available for Delta SNR, not which side won. In simultaneous Compare, the Target-Active Gate makes the one-sided categories asymmetric; in sequential TX A/B, the corresponding limitation is incomplete scheduled pairs and time separation.

Sequential TX A/B reports `scheduled pairs` instead of `joint spots`.

The UI term `Joint Spot` means a consolidated same-cycle comparison unit, not necessarily one untouched database row. Exact station and segment aggregation are defined in [Section 7.7](#sec-7-7).

<a id="sec-3-7"></a>
<a id="sec-3-7a"></a>

#### 2.6a Inspect the Contributing Stations (Performance Mode)

`Station Insights` lists the `callsign + locator` identities contributing to the selected segment. RX columns identify the `TX Station`, `Locator`, `km` and `Azimuth`, followed by `Heard by Target`, `Heard by others only`, `Decode Rate (%)` and `Median SNR @ 30 dBm`. TX uses `RX Station`, `Target heard` and `Other signals heard` with the same remaining columns. Read every rate together with both outcome counts; their sum is the station's confirmed-opportunity depth. Use `Heard only by other stations.` in RX or `Only other signals heard.` in TX to restore qualifying counter-only stations.

Select exactly one station row to open `Selected Station Evidence`. Selecting another row replaces the current station, and clearing the row hides the section; Performance and Compare both enforce this one-path scope. A compact two-line context identifies the selected `callsign + locator` path and its complete-run geometry on the first line, followed by confirmed-opportunity depth, Decode Rate and Median Target SNR on the second. The established independent time-bin selector is followed by two full-width figures that reuse the Segment Inspector temporal system. **Selected Station SNR Evidence** shows the path's actual normalized successful Target SNR: the chronological density uses every retained successful observation and its bin median, while the folded UTC-hour panel first forms one median per represented date-hour and then summarizes those medians across dates. Fine Q1–Q3 rails show the middle 50% of those same raw-observation or date-hour-median populations only from five contributed values onward. **Selected Station Temporal Evidence** separates station presence from opportunity depth with the same direction-aware outcomes and Decode Rate lines as the segment view. Folded UTC-hour panels require at least two represented UTC dates; otherwise the chronological panels expand and the unavailable-view message is shown. Selection changes use retained evidence and do not rerun the provider query.

<a id="sec-3-7b"></a>

#### 2.6b Inspect the Contributing Stations (Compare Mode)

Select one station to open the selected station evidence view. Selecting another row replaces the current station, while clearing the row hides the view. `Station Insights` continues to list the complete `callsign + locator` population contributing to the selected segment; Compare rows show joint and exclusive evidence plus station-level median Delta SNR, and `Include Unpaired Evidence` includes identities represented only by exclusive or asynchronous evidence.

Below the table, the Performance-style prompt `↓ Select time aggregation bin size:` controls both selected-path figures. The existing **Δ SNR over Time** and **Δ SNR by UTC Hour** panels retain the absolute paired result. For simultaneous Compare, the added **Selected Path Evidence Coverage** figure uses **Retained WSPR Cycles over Time** and **Retained WSPR Cycles by UTC Hour**; sequential TX A/B instead uses **Scheduled A/B Pairs over Time** and **Scheduled A/B Pairs by UTC Hour**. Each view stacks Only Target, Joint and Only Reference and adds a Joint Evidence Share line, while UTC-hour bars are averages per represented UTC date. It deliberately has no separate station-support row because exactly one station is selected. UTC-hour folding requires evidence from at least two distinct UTC dates; otherwise the chronological panel expands and the unavailable-view notice remains visible.

<a id="sec-3-8"></a>

#### 2.7 Verify the underlying evidence

`Drill-Down` is the row-level audit surface:

* RX Performance displays `Heard by Target` and `Heard by others only`; a row with neither count but with Target SNR preserves a Target decode without independent confirmation.
* TX Performance displays `Target heard` and `Other signals heard`; a row with neither count but with Target SNR preserves a Target report without independent RX-activity confirmation.
* Same-cycle Compare exposes Target/Reference evidence and Delta SNR from the shared cycle.
* Local Median Neighborhood expands the local Reference identities behind the cycle median.
* Sequential TX A/B exposes the planned UTC pair, `Target Micro-Median`, `Reference Micro-Median` and Pair Delta.

Use these rows to reconcile a surprising station or segment value, identify locator changes or isolated outliers, and confirm which observations were paired or excluded. Drill-Down is the audit trail behind the summaries rather than a separate performance metric.

<a id="sec-3-9"></a>

#### 2.8 Worked Compare example

The values below are neutral and hypothetical.

1. **Confirm the run:** the title identifies an RX Compare result with the expected Target, Reference, band, UTC window and Reference correction.
2. **Map:** the `2500-5000 km` north-east segment shows a mildly Target-favoring color. This locates the area to inspect.
3. **Stations and Spots:** the footer shows Joint evidence across several identities, together with some Only Target and Only Reference evidence.
4. **Segment Inspector:** the selected segment reports a station-balanced median Delta SNR of `+1.2 dB`, based on `6 joint stations | 47 joint spots`. The observation-level distribution has a `+0.8 dB` median, showing that repeated observations weight the raw evidence slightly differently from the equal-station summary.
5. **Station Insights:** four station medians are positive and two are near zero. No single identity supplies most of the 47 joint spots, and Decode Outcomes remain mixed.
6. **Drill-Down:** the rows confirm same-cycle Target and Reference pairs with the expected callsign and locator identities. Row-level Delta SNR values reflect the configured Reference correction, and no isolated row explains the segment median.
7. **Conclusion:** "For this Target, Reference, band, UTC window and selected NE `2500-5000 km` segment, station-balanced Delta SNR favored the Target by `+1.2 dB` across 6 joint station identities and 47 joint spots. The observation-level median was `+0.8 dB`; mixed Decode Outcomes remained."

This conclusion reports the run definition, geographic scope, both weighting levels, paired evidence counts and one-sided evidence. It is a descriptive result for the selected evidence and does not convert the comparison into a significance test or an isolated antenna-gain measurement.

---

<a id="sec-4"></a>

### 3. Strengthen and Communicate Your Result

A strong WSPRadar result combines a clear experiment, broad evidence and language that matches the actual observation.

<a id="sec-4-1"></a>

#### 3.1 Judge breadth, consistency and repeatability

Judge the result from the complete evidence picture:

* participating station identities;
* qualifying confirmed-opportunity, spot or scheduled-pair volume;
* agreement across stations;
* station-balanced and observation-level summaries;
* adjacent geographic segments;
* temporal views;
* Decode Outcomes;
* identity and locator quality;
* experiment control and repetition.

Evidence is **broader** when several identities and adjacent segments agree. It is **more internally consistent** when station-balanced, observation-level and time views tell a compatible story. It is **better controlled** when the selected playbook's operating requirements were followed and documented.

**Internal consistency and experimental repeatability are different.** Agreement among the station-balanced, observation-level, geographic and time views describes the evidence within one run. Repeating the experiment in another suitable window tests whether the observed pattern persists under new operating and propagation conditions.

WSPRadar deliberately does not collapse these dimensions into one proof grade. The visible counts, distributions and underlying rows let the operator judge the result in the context of the actual experiment.

<a id="sec-4-2"></a>

#### 3.2 Strengthen a result through repetition and control

Use an initial exploratory run to identify a possible pattern. Before a confirmatory repetition, freeze the direction, band, benchmark, filters, evidence thresholds, schedule and primary geographic or temporal evaluation scope, including `Maximum peer distance from Target (km)`. Run alternative maximum distances as separately preserved sensitivity analyses rather than selecting only the most favorable scope after seeing the result.

When the result will support an important station decision:

* extend the observation window across the propagation states named in the conclusion;
* prefer multi-day evidence for statements spanning complete daily cycles;
* repeat the experiment on another day or propagation period;
* for sequential TX Hardware A/B, reverse the Target/Reference schedule assignments;
* keep non-tested variables stable between repetitions;
* compare runs with the same direction, band, benchmark, filters and evidence thresholds;
* investigate any identity, locator or short interval that supplies a large fraction of the evidence;
* preserve setup notes so a later run can reproduce the station configuration.

Small observed differences become more useful when they recur across stations, time periods, adjacent segments and controlled repetitions. A reversed sequential TX assignment is especially useful because it can expose schedule-, switch-path- or time-of-cycle effects that ordinary repetition leaves in the same role.

TX and RX use different peer populations and opportunity definitions. Compare like-for-like TX and RX runs when investigating station balance or an "alligator" pattern.

<a id="sec-4-3"></a>

#### 3.3 Write an evidence-matched conclusion

A minimum operator statement identifies the Target and, for Compare where applicable, the fixed Reference or local benchmark definition. It also identifies the TX or RX direction, band, UTC window, geographic scope, result type, displayed value and supporting station/evidence count.

A full technical report also states:

* the applicable weighting levels: Station-balanced and Opportunity-level Decode Rate for Performance, or station-level and observation-level Delta SNR for Compare;
* qualifying-station and confirmed-opportunity counts for Performance, or joint-station and joint-spot/pair counts for Compare;
* Decode Outcomes for Compare;
* experiment conditions and any Reference correction;
* filters and evidence thresholds;
* whether the pattern repeated across time, stations or runs;
* any alternative radius or scope used as a sensitivity analysis.

**Performance wording**

> For this Target, band, UTC window and selected peer population, the displayed Decode Rate describes the fraction of independently confirmed opportunities in which the Target also produced qualifying evidence. State whether the reported value is the Station-balanced Decode Rate or the Opportunity-level Decode Rate. Qualifying stations, confirmed opportunities, geographic scope and temporal views describe the breadth, depth and recurrence supporting that result.

**Compare wording**

> For this Target, Reference, band, UTC window and selected segment, station-balanced Delta SNR favored the Target/Reference by the displayed amount. The observation-level Delta SNR, joint station and spot/pair counts and Decode Outcomes describe the supporting paired and one-sided evidence.

Match the design name to the quantity being described:

* A **Hardware A/B Test** compares the documented local paths.
* A **Buddy Test** compares complete installed stations and their environments.
* **Local Median Neighborhood** compares the Target with the active median-neighborhood definition inside the selected radius.
* **Local Best Station** compares the Target with a changing best-peer envelope.
* A directional result describes the observed WSPR paths and participating stations rather than an absolute radiation pattern.
* Compare-map colors use a run-scaled, symmetric dB color bar: blue favors the Reference, red favors the Target and `0 dB` is equality. Use the numerical color-bar values when comparing maps from different runs.

Use terms such as "observed difference," "favored in the selected evidence," "conditional reach" and "complete installed station comparison." Reserve isolated antenna gain, efficiency, receiver sensitivity, causation and statistical significance for experiments that actually measure or test those quantities.

The complete supported/unsupported wording reference is in [Chapter 8](#sec-8).

<a id="sec-4-4"></a>

#### 3.4 Preserve the run and its context

Use `Prepare All Results for Download` to build the current analysis export package. It contains the current configuration, run metadata, processed evidence, tables and high-resolution figures.

Preserve external notes alongside that package:

* physical antenna and feedline arrangement;
* switch or splitter topology;
* transmitter or receiver hardware;
* power measurements and reporting basis;
* decoder and software versions;
* operating schedule, physical schedule-to-path mapping and any reversed assignment;
* calibration procedure;
* weather, faults or intentional changes relevant to the run.

WSPRadar can preserve the configured analysis and processed evidence, but it cannot infer every physical detail of the station. Combining the export package with concise station notes makes comparison and reproduction substantially stronger. [Chapter 8](#sec-8) documents the exact export contents and remaining reproducibility boundaries.

<div style="page-break-before: always;"></div>

<a id="part-ii"></a>

## Part II: Controls and Troubleshooting

Use this part as a reference while setting up, repeating or diagnosing an analysis. The experiment playbooks explain which design fits your question; this part gives the exact controls, defaults, ranges and configuration behavior.

<a id="sec-5"></a>

### 4. Controls and Configuration

WSPRadar separates controls that change the scientific analysis from controls that only change how completed evidence is viewed. Knowing the difference makes it easier to refine a view without accidentally changing the experiment.

| Control class | What it changes | Configuration and reproducibility |
|---|---|---|
| **Scientific controls** | Query population, pairing, classification, normalization, eligibility or aggregation. These include direction, identity, band, time, benchmark, correction, solar filter, geographic analysis scope, exclusion filters and evidence thresholds. | Saved when applicable and recorded in the export package. Changing one clears the completed result so the analysis can be rerun with the new definition. |
| **View controls** | Which completed evidence is displayed or inspected, without changing the retained analysis population. These include selected Inspector segment, selected station, unpaired-evidence visibility or visibility of counter-only stations in Performance, and evidence time bins. | Segment Inspector range/direction and the applicable durable Compare/Performance result-view choices are saved. Inspector choices can narrow the completed geographic scope but cannot override it. Table filters and other incidental interactions remain transient. |
| **Transient UI state** | Panel expansion, table and Drill-Down filters, documentation visibility, prepared download bytes and other incidental session interaction state. | Not part of the scientific configuration and normally not serialized. |
| **Configuration fields preserved for reproducibility** | The applicable scientific input branch plus explicitly supported durable view settings. | Stored in the versioned `.config`. Inactive scientific input branches are omitted. Durable result-view preferences may retain their canonical mode-specific blocks, including `results_view.success` for the visible Performance view, without activating or producing that result. |

Exact formulas and processing rules remain in [Scientific Methods](#sec-7).

<a id="sec-5-1"></a>

#### 4.1 Workflow controls

**`Input view`** switches between `Guided` and `Classic`. Guided is the factory default and leads from the operating question through Target and time window, Reference design when applicable, the meaning of the Reference-side correction, scope and evidence, and a final review. Each Guided input explains what to enter, how WSPRadar uses it and which interpretation or evidence trade-off it introduces. Classic exposes the same scientific controls in compact panels. Both editors read and write one canonical configuration, so switching views preserves inputs and completed results; the selected editor is transient presentation state and is not saved in a `.config` file.

**`Load Demo`** opens maintained historical profiles. Guided mode loads the selected profile for inspection and shows its metadata before the collapsed preset steps. **`Walk me through the setup`** opens the first pre-populated applicable step, and **`Continue`** advances to the next applicable step. **`Skip to review and run`** opens Review and run immediately. Neither path launches an analysis. Classic mode can either load the profile or run it immediately. An unchanged loaded profile remains a guided demo when you subsequently use the main Run button, so it retains the demo query-cache policy. Editing a scientific control turns the edited configuration into an ordinary analysis. Each profile's standalone configuration explicitly supplies its correction mode and dB value; WSPRadar does not infer the mode from the profile identity or from a `0.0 dB` value.

**`Load Config`** strictly validates and loads a versioned JSON `.config` file. Invalid identities, dates, choices, ranges, duplicate fields and unsupported schema versions are rejected.

The pre-production contract remains schema version 1. Reference Station requires `Reference callsign` plus its independent four-character `Reference Locator`. RX and simultaneous TX Hardware A/B require the distinct `Reference callsign` but derive their shared grid-4 from Target QTH and therefore store no redundant `reference_qth`; TX Hardware A/B also requires its method-specific fields. Every comparison configuration records both the correction purpose and its numeric value: `no_offset` and `establish_offset` require `0.0 dB`, while `established_offset` records a documented signed correction and may explicitly record an established `0.0 dB`. Performance-only configurations omit both fields. Earlier unpublished v1 prototypes are not migrated; an applicable comparison file without the explicit correction purpose is rejected rather than guessed from an ambiguous numeric zero. Resave or recreate it with the current controls.

**`Save Config`** opens a compact profile form. Enter a title and optional description; an optional stable ID can be supplied or generated automatically. The resulting `<profile-id>.config` stores every applicable input and supported durable result-view preference, including the exact absolute UTC start and end boundaries. A Compare configuration may retain both the canonical `results_view.compare` block and the canonical `results_view.success` block used for the visible Performance view; this does not create a second result or activate an inactive scientific branch. A saved configuration does not contain result rows, external experiment notes or transient table filters.

**`Run RX Analysis` / `Run TX Analysis`** is one direction-aware button. It runs exactly the active result selected in `Results view and benchmark design`: Performance when `Performance — no Reference` is selected, or Compare when a benchmark is selected. Once submitted, the button is disabled while that session's unchanged analysis is queued or running. Changing a scientific control creates a different request, clears the old result and shows that the configuration must be run again. During a capacity wait, the status reports only your analysis's current queue position; it does not show unrelated users' queue totals.

**`Prepare All Results for Download`** builds the current analysis export package on demand.

**`Load full documentation` / `Hide full documentation`** explicitly loads or hides the complete web manual.

**`Prepare PDF`** builds the complete selected-language manual as a PDF on demand. The full web manual does not need to be open first.

<a id="sec-5-2"></a>

#### 4.2 Target and measurement-window controls

These controls define the Target, operating direction, band and evidence window.

| UI label | Factory default | What it controls |
|---|---|---|
| **RX Analysis / TX Analysis** | none; required | RX evaluates the Target as a receiving WSPR station; TX evaluates it as a transmitting WSPR station. `Run` and `Save Config` remain disabled until either option is selected. |
| **Target callsign (receiver under test)** / **Target callsign (transmitter under test)** | blank | Valid exact Target callsign; valid `/` variants and one terminal `-` suffix are accepted. |
| **Target QTH (4 or 6 characters)** | blank | Map center and local-radius origin; its first four characters constrain Target matching. |
| **Operating Band** | `20m` | Exactly one of `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` or `23cm`. |
| **UTC measurement window** | absolute 24-hour window ending at the current 15-minute UTC boundary | Selects fixed UTC evidence that remains unchanged across reruns. |
| **Start Date (UTC)**, **End Date (UTC)**, **Start Time (UTC)**, **End Time (UTC)** | exact default boundaries above | Dates start at 2008 and one window is limited to 31 days. End must follow start and cannot be later than the current 15-minute UTC boundary. Edited values are quantized down to 15-minute boundaries and the effective values are written back to the controls. |

Use the callsign exactly as uploaded. Prefer standard callsign forms and enter a hyphenated reporting identifier only when that is the exact archive identity you need to query. `DL1MKS`, `DL1MKS/P`, `DL1MKS/1`, `DL1MKS/QRP` and `DL1MKS-1` are separate identities; WSPRadar neither treats `/` and `-` as aliases nor applies hidden prefix matching.

A Maidenhead locator is a compact grid-square location code. Four characters identify a broad area; six characters identify a smaller area inside it. WSPRadar uses the configured QTH as the map center and local-radius origin. Performance and Compare match Target spots using its first four locator characters; grid-6 is not part of this selector.

<a id="sec-5-3"></a>

#### 4.3 Results-view and benchmark controls

**`Results view and benchmark design`** has the factory default `Performance — no Reference`. The current choices are:

- `Performance — no Reference`
- `Compare — Hardware A/B`
- `Compare — Known Reference Station`
- `Compare — local neighborhood benchmark`

The choices are mutually exclusive result types. No benchmark produces Performance only; every benchmark choice produces Compare only and does not render, inspect or export a separate Performance result.

| UI label | Default and range | When it appears and what it controls |
|---|---|---|
| **Is there an established Target–Reference offset?** | `No established offset — use 0.0 dB` | Guided Hardware A/B and Known Reference Station comparisons. Distinguishes no established offset, use of an established correction and a deliberate offset-establishment run. |
| **Reference-side SNR correction (dB)** | blank text field with grey `0.0` example; range `-99.9` to `+99.9 dB` | Added to the Reference-side SNR before Delta SNR is calculated. Enter decimal values with a point (`1.2`, not `1,2`); a blank field means `0.0 dB`. Guided displays the field for `Use an established correction`; Classic exposes it for every Compare design. A nonzero Classic edit selects `established_offset`, while a blank field or `0.0` preserves the current explicit mode. No-offset and offset-establishment runs keep the value at `0.0 dB`; an established correction may be signed or explicitly established as `0.0 dB`. |
| **Target callsign** | from Target and measurement window | Makes the Target side explicit. |
| **Target QTH** | from Target and measurement window | Makes the Target QTH explicit. |
| **Target Locator** | first four characters of Target QTH | Makes the Target grid-4 explicit. |
| **Reference callsign** | blank | Exact reporting callsign for the Reference side. |
| **Reference Locator** | independent grid-4 for Reference Station; Target grid-4 for Hardware A/B | Four-character Maidenhead grid for Reference matching. |
| **Local Benchmark Method** | `Local Median Neighborhood` | Local Neighborhood Benchmark. Selects `Local Median Neighborhood` or the strict `Local Best Station`. |
| **Neighborhood Radius (km)** | `100`; 10 to 250 km in 10 km steps | Local Neighborhood Benchmark. Includes local Reference coordinates around the configured QTH. |
| **TX A/B Method** | `Simultaneous TX` | TX Hardware A/B Test. Switches between `Simultaneous TX` and `Sequential TX`; the selected branch alone is displayed and saved. |
| **Repeat Interval** | `10 min`; `4, 6, 10, 12, 20, 30, 60 min` | Sequential TX Hardware A/B. Shared recurrence of each physical path. All choices are even WSPR-compatible divisors of one UTC hour. |
| **Target Start** | `00 UTC`; even phases below the Repeat Interval | Sequential TX Hardware A/B. Defines the Target UTC start phase. |
| **Reference Start** | `02 UTC`; even phases below the Repeat Interval | Sequential TX Hardware A/B. Defines the Reference UTC start phase and is kept disjoint from Target. |

Hardware A/B Test follows the selected **RX Analysis / TX Analysis** option. RX always displays the fixed Target/Reference identity block. TX first displays the method selector: simultaneous operation loads the same identity block, while sequential operation loads the shared Repeat Interval, two disjoint Start controls, a swap action and the resulting one-hour schedule preview. Pairing follows the applicable same-cycle or scheduled method automatically.

For TX Hardware A/B, `Repeat Interval` is each physical path's actual recurrence. It is not necessarily the `Frame` label shown by a transmitter that alternates one output between two paths. Check the preview against observed on-air starts and the physical switch mapping. Device-specific examples are in [Appendix B](#sec-b); exact pair construction is in [Sections 7.1](#sec-7-1) and [7.7](#sec-7-7).

Switching direction or benchmark mode hides the inapplicable branch. The current browser session may retain inactive values so Guided/Classic switching does not erase work, but saved configurations serialize only the active branch. A branch change clears values whose scientific meaning is no longer valid, such as a correction or identity being reinterpreted under another design. A saved Performance-only configuration therefore contains no dormant comparison parameters.

##### Reference-side SNR correction sign

A positive correction makes the corrected Reference SNR stronger and therefore reduces Target-minus-Reference Delta SNR. Enter a measured `target - reference` calibration offset with the same sign. For example, a common-input calibration of `+1.6 dB` is entered as `+1.6 dB`. The exact equations appear in [the Delta SNR method](#sec-7-5).

The correction applies to:

- the Reference receiver, transmitter or schedule in Hardware A/B Test;
- the Reference callsign in Reference Station / Buddy Test;
- the selected local value in Local Best Station; and
- every local contribution before Local Median Neighborhood aggregation.

A constant correction is suitable for a defensible constant offset. Clipping, unstable AGC, intermittent routing, frequency-dependent response and incorrect power reports require correction at the experiment or hardware level instead. [Appendix C](#sec-c) describes calibration.

Guided mode offers `No established offset — use 0.0 dB`, `Use an established correction` and `Set up an offset-establishment run` for controlled Hardware A/B and known Reference Station comparisons. The third choice keeps the existing Compare method, fixes the correction at `0.0 dB` and records the run as an offset-establishment run; it does not choose or apply an estimator automatically. The explicit mode is retained in the saved configuration and export metadata, while only the numeric dB value enters the Delta SNR calculation. This preserves why a zero value is being used: no established offset, a deliberately uncorrected establishment run, or a genuinely established zero correction remain distinct even though their numeric calculation can be identical. For Hardware A/B, establish a stable complete-path difference under a common input. For a Reference Station, establish only a repeatable baseline for that particular Target–Reference pair, band, setup and operating design; it is not an absolute calibration of geographically separated stations. Return to the offset step and enter the defensible value manually after reviewing the baseline evidence. Local Neighborhood comparisons can apply a documented established correction but do not offer the controlled offset-establishment workflow.

<a id="sec-5-4"></a>

#### 4.4 Filters and evidence thresholds

These controls let you shape the peer population, illumination period and minimum evidence required for display. Choose them from the intended population and evidence floor. Do not relax filters or thresholds after inspecting the result solely to obtain a denser or more favorable map; report a changed analysis as a separate configuration.

**`Exclude Special Callsigns Q, 0, 1`**

- **Default:** off
- **Applies to:** all results
- **Effect:** excludes qualifying peer identities beginning with `Q`, `0` or `1`.
- **Change this when:** the intended peer population excludes the balloon- or telemetry-style identities represented by these prefixes. State the choice in reports.

Use this control according to the question:

- In RX Compare, beacon-like or telemetry-style transmitters can provide valuable weak same-cycle signals seen by both receivers.
- In RX Performance, retain them when beacon reception is part of the question; exclude them when the intended population is ordinary amateur-station activity.
- In TX analysis, the filter applies to receiver-side peer identities. Use it when those identities are distorting the intended receiver population.

**`Exclude Moving Stations`**

- **Default:** off
- **Applies to:** mapped peers
- **Effect:** removes a peer callsign reporting more than one four-character locator across the complete otherwise eligible global candidate population before geographic scope is applied. Narrowing the distance therefore cannot make a changing-location callsign appear stationary.
- **Change this when:** mobile identities or changing locators would otherwise mix locations inside one callsign. Check Drill-Down to distinguish likely movement from incorrect locator data.

**`Solar state at Target QTH`**

- **Default:** `All 24h`
- **Choices:** `All 24h`, `Daylight (Elev > +6°)`, `Nighttime (Elev < -6°)`, `Greyline (-6° to +6°)`
- **Applies to:** all results
- **Effect:** keeps cycles classified by solar elevation at the Target QTH.
- **Change this when:** the scientific question is specifically about one local illumination state.

**`Maximum peer distance from Target (km)`**

- **Default:** `22000`
- **Choices:** `2500`, `5000`, `10000`, `15000`, `20000`, `22000`
- **Applies to:** all Performance and Compare results
- **Effect:** retains mapped-peer rows only when their distance from Target QTH is strictly less than the selected maximum; all other peer rows are excluded from scientific calculations, processed analysis artifacts and exports. The map, footer totals and Segment Inspector all use the same retained population; Inspector selections can narrow it but cannot restore excluded rows.
- **Global activity exception:** the Target-Active Gate may still use evidence outside this geographic scope solely to establish that the Target was operating. Those out-of-scope peers do not enter scoped outcomes, statistics, counts or exports.
- **Processing and integrity:** the filter is applied after retrieval, so provider queries and their raw query cache remain global and reusable. Moving-station integrity is evaluated globally before this distance filter.
- **Change this when:** the scientific question concerns a defensible regional peer population. Fix the primary maximum distance before a confirmatory run and report other distances as separate sensitivity analyses rather than choosing one because its result is favorable.

**`Minimum joint evidence per station`**

- **Default:** `1`
- **Range:** 1 to 50
- **Applies to:** simultaneous Compare
- **Effect:** requires this many joint peer-cycles before a station contributes paired Delta SNR.
- **Change this when:** you want more repeated paired evidence per station and accept reduced geographic coverage.

**`Minimum scheduled pairs per station`**

- **Default:** `1`
- **Range:** 1 to 50
- **Applies to:** sequential TX Hardware A/B
- **Effect:** requires this many joint scheduled pairs before a station contributes paired Delta SNR.
- **Change this when:** you want more repeated scheduled pairs per station and accept reduced geographic coverage.

The Compare joint threshold also suppresses exclusive categories whose own count is below the same numeric cutoff. In sequential TX Hardware A/B, paired eligibility is counted in scheduled pairs, while exclusive evidence is counted in one-sided scheduled pairs and compared with that numeric cutoff.

**`Minimum confirmed opportunities per station`**

- **Default:** `5`
- **Range:** 1 to 100
- **Applies to:** Performance
- **Effect:** requires this many `Heard by Target` plus `Heard by others only` RX outcomes, or `Target heard` plus `Other signals heard only` TX outcomes, before a peer contributes.
- **Change this when:** you want a different evidence floor.

Lowering this threshold increases map coverage, but station rates become more discrete when supported by only one or two qualifying opportunities. Values such as `0%`, `50%` or `100%` can then represent very little evidence. Read the count beside the rate and strengthen a small sample with a longer or repeated run.

**`Minimum qualifying stations per map segment`**

- **Default:** `1`
- **Range:** 1 to 10
- **Applies to:** all maps
- **Effect:** requires this many qualifying identities before a segment is drawn.
- **Change this when:** you want map color to require broader identity support and accept more blank segments.

<a id="sec-5-5"></a>

#### 4.5 Map, inspector and export controls

These controls work with completed evidence and do not rerun the upstream query unless explicitly stated otherwise.

- Segment range and direction selectors change the inspected scope. Compare and Performance selections are saved independently; the portable schema retains the canonical key `results_view.success` for the visible Performance view.
- `Heard only by other stations.` in RX or `Only other signals heard.` in TX restores qualifying counter-only Performance identities. Its setting is saved for Performance.
- `Include Unpaired Evidence` includes Compare identities represented only by exclusive or asynchronous evidence. Its durable value is saved when Compare applies.
- Station selection changes the selected-station figures and selected Drill-Down. Performance and Compare each save no more than one exact `callsign + locator` identity; selecting another row replaces the current identity, and clearing the row saves an explicit deselection. A loaded identity absent from the current segment scope remains unselected with a notice rather than being replaced; its saved identity is retained until you make a new table selection, so changing the segment scope can still make it available. Configurations containing `"all"`, duplicate identities or multiple selected identities are rejected.
- For the station selected in Performance, the prompt `↓ Select time aggregation bin size:` changes the chronological panels in **Selected Station SNR Evidence** and **Selected Station Temporal Evidence**. Their folded UTC-hour panels remain fixed at one-hour bins. A supported saved Performance time bin remains selected when the station identity changes, remains independent from the Segment Inspector temporal bin and never reruns the completed provider analysis. Compare retains its independent selected-station bin.
- For the station selected in Compare, the same prompt and full-width segmented selector change the left **Δ SNR over Time** panel. The right **Δ SNR by UTC Hour** panel remains visible at fixed one-hour bins. The selected Compare bin is stored independently in `.config`, remains independent from the Segment Inspector temporal bin and never reruns the completed provider analysis; there is no separate selected temporal-view preference.
- For Compare, the prompt `↓ Select time aggregation bin size` appears under `Temporal Evidence` immediately above the segment bin choices. The available choices adapt to the run duration, including minute bins for shorter windows and hour bins for longer windows. The control changes only the left segment-level temporal panel; it does not change the date-folded UTC-hour panel, the selected-station timeline, pairing or analysis. Its selected bin is stored independently in `.config`.
- For Performance, the prompt `↓ Select time aggregation bin size` appears immediately above the `1 h`, `2 h`, `3 h`, `6 h`, `12 h` and `24 h` choices under `Temporal Evidence`. This segment-level control changes only the chronological segment panel. The folded UTC-hour panel remains fixed at one-hour bins, and neither view changes the completed analysis or the independent selected-station timeline.
- Empty Performance time or distance bins remain blank; they are not converted to zero-rate evidence.
- `Prepare All Results for Download` exports the current result and inspector selections. Package contents are documented in [the export and reproducibility section](#sec-8-4).

<a id="sec-6"></a>

### 5. Troubleshooting and Data Quality

Most empty or unexpected results can be traced efficiently by confirming the run definition first and then following the symptom-specific checks. This keeps a threshold adjustment from masking a callsign, band, timing or operating-schedule mismatch.

<a id="sec-6-1"></a>

#### 5.1 Confirm the run definition first

Work through these checks in order:

1. **Target identity:** confirm the exact callsign, including any suffix, and the identity configured in WSJT-X.
2. **QTH:** confirm the configured locator and its first four characters against the locator actually uploaded.
3. **Band:** confirm one exact band and the band on which the station operated.
4. **UTC evidence window:** confirm the exact absolute start and end timestamps shown in the controls.
5. **Actual operation:** confirm that the Target was transmitting or receiving as intended and that WSPR uploading was enabled.
6. **Benchmark operation:** for Compare, confirm the exact Reference identity and that the counterpart was operating during the intended overlap.
7. **Design mechanics:** where applicable, confirm clock synchronization, TX schedule-to-path mapping, switching schedule, signal routing and reported power.

After these are established, inspect thresholds, exclusion filters, solar selection and geographic analysis scope. A looser filter or wider scope can retain more qualifying evidence, but it cannot repair a run aimed at the wrong identity, band or time.

<a id="sec-6-2"></a>

#### 5.2 Diagnose by symptom

After the shared checks in Section 5.1, follow the branch that matches the result:

| Symptom | Next checks |
|---|---|
| **No result or no Target evidence** | Inspect the reported strict `code = 1` or historical-fallback status and current upstream availability. |
| **Compare has no Delta SNR** | Confirm shared remote peers in overlapping cycles or scheduled pairs, then clocks, TX A/B schedule-to-path mapping, switching schedule, joint threshold, filters and scope. |
| **Performance has very few peers** | Confirm independent network activity, then `Minimum confirmed opportunities per station`, exclusion and solar filters, timeframe and `Maximum peer distance from Target (km)`. A longer window can add evidence without changing the intended population. |

<div style="page-break-before: always;"></div>

If evidence exists but looks unexpected, continue with these branches:

| Symptom | Next checks |
|---|---|
| **Many Performance rows without independent confirmation** | RX labels these rows `Heard by Target without independent confirmation`; TX labels them `Target heard without independent RX-activity confirmation`. They remain auditable but do not enter Decode Rate. |
| **`Only Reference = 0`** | Confirm Target-Active gating, evidence thresholds and selected scope; zero can be correct after those rules. |
| **Unexpected Hardware A/B Delta SNR sign** | Verify physical A/B mapping, Target/Reference order, schedule phases, correction sign, actual and reported power, and calibration notes. Reconcile one station in Drill-Down. |
| **Local result changes with radius** | Confirm QTH and radius, then inspect contributing local `callsign + locator` identities. Report useful radius sensitivity instead of selecting only the most favorable run. |
| **Old config with `band=All` is rejected** | Choose one exact band; automatic conversion would change the scientific question. |
| **Recent spots appear incomplete** | Allow about five minutes after the latest cycle, then check reporting and upstream status as described in Section 5.6. |

An upstream-data issue changes what the selected source supplies. An experiment-design issue changes whether the retained rows answer the intended question. Diagnose and report the two separately.

<a id="sec-6-3"></a>

#### 5.3 Callsign and locator checks

Performance and every Compare mode match Target spots by exact callsign plus the configured QTH's first four locator characters. A Target reporting `JN37` while configured as `JN38` matches neither result.

Every Reference Station is matched by exact callsign plus its independently configured, exactly four-character Reference Locator. RX and simultaneous TX Hardware A/B instead derive both disabled Locator displays from the first four Target-QTH characters and carry no independent Reference-QTH setting; sequential TX Hardware A/B uses the shared exact Target callsign and Target grid-4 on both scheduled sides. Local candidates remain selected geographically.

If a non-empty callsign or locator has invalid syntax, correct the field-specific message before diagnosing missing archive evidence. Callsigns must follow the 3-to-15-character ASCII token rule in [Section 4.2](#sec-5-2). Locators must be four or six Maidenhead characters with field letters `A-R`, digits in positions three and four, and optional subsquare letters `A-X`. These checks reject malformed input but do not establish legal callsign assignment, actual operation or physical location.

Peer identities use exact callsign plus the full reported locator string. Bad, stale or changing locators can split one physical station, move it into the wrong segment or trigger the moving-station filter.

<a id="sec-6-4"></a>

#### 5.4 Historical decode-code fallback

WSPRadar first requests rows using `code = 1` for WSPR-2 evidence. If the strict query returns no Target-side evidence, it retries without that predicate for historical compatibility and reports the fallback in run status.

The fallback broadens selection and can differ between Compare and Performance. WSPRadar applies it automatically; run status shows which query path was used for diagnosis.

<a id="sec-6-5"></a>

#### 5.5 How the Target-Active Gate shapes evidence

The Target-Active Gate keeps simultaneous comparisons focused on cycles in which Target participation is observable. It excludes Reference evidence outside those cycles, preventing known Target downtime from becoming automatic failure.

For example, if the Target station is shut down overnight, Reference spots from those offline hours are not counted as defeats. Within the retained cycles, Reference uptime and radio-path availability still need to be established from the experiment context.

Because the gate is intentionally Target-centric, swapping Target and Reference can change eligible cycles and Decode Outcomes. Sequential TX Hardware A/B uses its deterministic scheduled-pair method rather than the same simultaneous gate.

The exact eligibility rules and Target-centric asymmetry are defined in [Section 7.3](#sec-7-3).

<a id="sec-6-6"></a>

#### 5.6 Working with upstream data

wspr.live states that its data is raw WSPRnet-reported data and may contain duplicates, false spots and other errors. Its volunteer infrastructure provides no guarantee of correctness, availability or stability. <a href="#ref-10">[Ref-10]</a>

wspr.live describes real-time data as available with a delay of a few minutes and says its scraper checks for new spots every few minutes. As a practical operating estimate, wait about **five minutes** after the final WSPR cycle before expecting a fresh analysis window to be reasonably populated.

Five minutes is not a completeness guarantee. Delayed uploads, ingestion interruptions and later corrections can appear after that point. <a href="#ref-10">[Ref-10]</a>

WSPRadar uses pairing, identity grouping, medians, thresholds and Drill-Down to reduce sensitivity to isolated bad rows and make them easier to inspect. Repeated plausible errors can still survive those controls.

Reported power and locators are user-supplied. Correct mathematics applied to an incorrect power or locator remains physically wrong.

**Read System Audit Status**

System Audit Status names the database origin once for the complete run. Its reason is `primary` when the first-priority source was selected, `cache affinity` when a guided demo selected a complete fresh bundle from a lower-priority provider before normal network-backed provider selection, `capacity spillover` when a lower-priority ready source admitted the complete request bundle because higher-priority request capacity could not, `failure fallback` when this run restarted after a provider-scoped failure or a higher-priority source was already unavailable during provider-health cooldown or recovery probing, or `committed source` when a rerender retained the run's already committed source.

It then reports `database request`, `RAM cache` or `disk cache` plus timing for each strict and optional historical-fallback query separately. Those delivery labels describe how rows reached the analysis; they do not identify different databases or change the origin reason.

On the same deployment, a guided demo can reuse raw provider query rows for up to 24 hours from their original fetch. Before making a new demo request, WSPRadar prefers the first configured provider that already has the complete required demo bundle cached. The cached rows retain their actual provider origin and are never combined across providers. Cache hits do not renew the deadline. A process restart loses the RAM tier, but the disk tier remains reusable if local storage survives; storage eviction can remove it sooner.

<div style="page-break-before: always;"></div>

<a id="part-iii"></a>
## Part III: Scientific Foundations, Methods and Claims

This part places WSPRadar in its scientific and amateur-radio lineage, then defines exactly how it constructs, summarizes, interprets and preserves evidence. It supports method review, audit and serious reporting; the operator playbooks and result-reading chapters remain the practical route through the application.

<a id="sec-d"></a>
### 6. Literature, Prior Art and Positioning

This chapter explains which ideas WSPRadar inherits, integrates and extends. It highlights each source's useful contribution as well as the boundary of what that source demonstrates. It does not claim that the literature validates every WSPRadar metric or implementation choice.

<a id="sec-d-1"></a>
#### 6.1 From reporting network to experimental dataset

Taylor and Walker presented WSPRnet not merely as a live map but as an archive: "The WSPRnet database represents a rich source of experimental data for propagation studies." Their example groups observations by time of day over several weeks, illustrating both the value of accumulated reports and the need to interpret them as observational data. <a href="#ref-6">[Ref-6]</a>

Frissell et al. place WSPRNet alongside the Reverse Beacon Network and PSKReporter as established amateur-radio observation networks that provide "rich, ever-growing, long-term data of bottomside ionospheric observations." They distinguish those established networks from newer purpose-built citizen-science networks and recommend cross-calibration between instrument networks. The review supports the scientific value of amateur observations; it does not turn every individual receiver into a calibrated instrument. <a href="#ref-7">[Ref-7]</a>

The public WSPR archive is therefore unusually powerful, but it remains a successful-decode record produced by heterogeneous volunteer stations. Historical depth and geographic reach do not remove selection effects, identity errors, changing equipment or unknown operating schedules.

<a id="sec-d-2"></a>
#### 6.2 Making observational WSPR data interpretable

<a id="sec-d-lo"></a>
Lo et al. used 7 MHz WSPR observations to study greyline propagation and explicitly warned: "There is no official recording of the operating schedules for WSPR equipment." They checked whether a transmitter was heard anywhere, or whether a receiver heard anything from anywhere, before interpreting missing links as propagation behavior. They also stressed callsign/location consistency and the use of multiple sites. <a href="#ref-9">[Ref-9]</a>

That activity principle is direct prior art for WSPRadar's Target-Active Gate: silence should not become radio counter-evidence until operation is observable. Lo et al. do not, however, define WSPRadar's exact asymmetric gate, Performance denominator or Decode Outcomes. Those remain WSPRadar design choices for a different estimand.

<a id="sec-d-3"></a>
#### 6.3 Antenna and station-comparison lineage

<a id="sec-d-toledo"></a>
**Toledo (2010): why slow alternation fails.** Sivan Toledo tried one antenna for roughly an hour, then another, and found that path SNR changed on the same scale as the apparent antenna differences. His conclusion was blunt: "Clearly, you can't compare antennas using WSPR using the naive technique that I was using." He identified per-cycle switching and simultaneous transmissions with separate hardware as stronger designs. This is the practical reason WSPRadar uses deterministic interleaved TX A/B schedules rather than long blocks and favors the shortest practical separation. Short separation reduces, but cannot eliminate, temporal confounding. <a href="#ref-3">[Ref-3]</a>

<a id="sec-d-milazzo"></a>
**Milazzo (2011): an early operator-led end-to-end comparison.** Carol Milazzo compared two stations 29 km apart through a common receiver 1,750 km away, corrected their reported SNRs for transmit-power differences, compared the trend with VOACAP, noted unequal duty cycles and also examined reciprocal RX reports. Her first conclusion was: "The WSPR network data permitted a comparison of signals from two antennas to a distant destination." This is an unusually complete early amateur-radio case study and the earliest detailed comparison retained in this manual. It is not claimed as the first: Milazzo herself cites several earlier WSPR antenna experiments. Different QTHs, hardware and local noise, one selected remote receiver and no formal uncertainty analysis limit the causal claim. <a href="#ref-4">[Ref-4]</a>

<a id="sec-d-griffiths-squibb"></a>
**Griffiths and Squibb (2017): same-signal RX comparison as station diagnosis.** For two receivers at separate QTHs, they retained "only those reports of the same station at the same time selected for analysis" and inspected SNR difference against soil moisture, time, distance and station changes. The work shows how paired WSPR data can diagnose the whole receive system and reveal effects hidden by spot totals. Because antennas, QTH, noise and equipment differed, it supports comparative station evidence rather than calibrated antenna gain or a single causal explanation. <a href="#ref-5">[Ref-5]</a>

<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels and Lamy (2022): conditioned simultaneous RX.** Their peer-reviewed study states that "two identical 160-m band WSPR receiver stations are conditioned to compare the performance of different 160-m band antennas." A calibrated dual-receiver design then compares common remote transmissions simultaneously. This is the strongest direct precedent in this set for RX Hardware A/B Test and for characterizing receive-chain differences before comparing antennas. Their propagation experiment also shows that polarization and ionospheric effects can change reported SNR, so even a carefully conditioned setup does not produce one context-free antenna number. <a href="#ref-2">[Ref-2]</a>

<a id="sec-d-zander"></a>
**Zander (2022): a mathematical model for simultaneous TX comparison.** Zander analyzes two local antennas driven by separate nominally equal-power transmitters and callsigns in the same WSPR cycle. He retains a receiver only when both signals are "reported by the same station in the same time interval." Under the paper's same-time, common-path and equal-power model, shared path loss and receiver noise cancel in the SNR difference; separate narrowband interference, failed decodes and integer SNR quantization remain. Because each difference is formed within one remote receiver, "the method does not require any receiver calibration"; equality or correction of the two transmitter powers is still required. <a href="#ref-1">[Ref-1]</a>

In each preliminary experiment, Zander collected about 1,000 reports in roughly one hour and retained 150-200 joint reports from 15-35 receiving stations. The observed sample standard deviation was close to 3 dB; for about 100 useful samples, the paper estimates the standard deviation of the arithmetic mean below 0.5 dB. It then reports "accuracy of less than a dB" within hours. Scientifically, that calculation is evidence of repeatability or precision under the model, not traceable total accuracy: the paper separately identifies receiver-geography, directivity and unknown elevation-angle biases. Long runs reduce random congestion but not those systematic effects. The study is strong support for simultaneous same-receiver Delta SNR; it does not validate WSPRadar's sequential one-transmitter TX A/B, station-balanced medians, Decode Outcomes or other benchmark designs.

<a id="sec-d-4"></a>
#### 6.4 Analysis infrastructure and operator tools

Griffiths and Robinett showed how a relational time-series database enables a self-join for the "same sender at the same time in the same band for two different reporters." Their Grafana examples combine SNR-difference scatterplots, medians, quartiles, time heatmaps, distance and azimuth views, plus data export. This is important precedent for inspectable comparison infrastructure, but not for WSPRadar's exact eligibility rules, denominators or estimators. <a href="#ref-13">[Ref-13]</a>

WSPR.Rocks provides rapid WSPR exploration, SQL access, maps, tables, SpotQ and other analyses. WSPRadar differs by organizing the workflow around explicit experiment designs, pairing and row-level audit rather than a leaderboard. <a href="#ref-14">[Ref-14]</a>

WSPRdaemon focuses on robust multi-receiver acquisition, scheduling and added noise/Doppler metadata, illustrating why acquisition stability and noise context matter for RX analysis. <a href="#ref-11">[Ref-11]</a>

SOTABEAMS WSPRlite and DXplorer provide accessible WSPR-based antenna/location comparison and the DX10 metric. <a href="#ref-15">[Ref-15]</a>

WSPR-Station-Compare explicitly connects station-comparison software with the Vanhamel and Zander methods. <a href="#ref-16">[Ref-16]</a>

The Antenna Performance Analysis Tool is another user-oriented WSPR antenna-report service. Its existence means WSPRadar should not claim to be the first WSPR antenna-analysis tool. <a href="#ref-17">[Ref-17]</a>

WATT provides Excel/VBA reporting, mapping, filtering and timeline exploration, reinforcing the practical value of inspectable data rather than only a fixed score. <a href="#ref-18">[Ref-18]</a>

These tools demonstrate substantial prior art in acquisition, browsing, ranking, visualization and antenna reporting. Their existence is part of WSPRadar's lineage, not a weakness in its positioning.

<a id="sec-d-5"></a>
#### 6.5 What WSPRadar inherits, integrates and adds

WSPRadar inherits important ideas rather than claiming to have invented WSPR comparison: accumulated observations, activity checks, reported-power correction, common-condition pairing, calibrated receive chains, geographic/time views and database joins all have clear precedents above.

WSPRadar integrates those ideas into one operator workflow that includes:

* TX and RX analysis with the `Performance — no Reference`, Hardware A/B Test, Reference Station / Buddy Test and Local Neighborhood Benchmark designs;
* Target activity checks, same-cycle or deterministic scheduled-pair comparison, reported-power normalization and optional Reference-side SNR correction;
* conditional Performance evidence, paired Delta SNR and categorical Decode Outcomes as separate evidence questions;
* maps, Segment Inspector, Station Insights, time/solar views and row-level Drill-Down;
* evidence thresholds and station-versus-observation diagnostics;
* guided demos, versioned configurations, run metadata, processed evidence, tables, figures and practical supplements.

Within the literature and tools reviewed here, the clearest WSPRadar-specific additions are:

* the conditional Performance opportunity model and its explicit counter-evidence denominator for Decode Rate;
* the explicit separation of paired Delta SNR from `Joint`, `Only Target`, `Only Reference` and `Both Async` Decode Outcomes;
* dynamic Local Median Neighborhood and Local Best Station benchmark construction;
* hierarchical, station-balanced geographic aggregation, including one contribution per local station before a Local Median Neighborhood is formed;
* parallel `STATIONS` and `SPOTS` composition on every Compare map;
* an integrated map-to-segment-to-station-to-row audit path;
* a reproducibility package tied to the completed run and current inspector selections.

This is a bounded positioning claim, not a global priority claim. Median aggregation itself is not new; the contribution is its station-balanced application inside the complete experiment and inspection workflow. WSPRadar's distinctive value is the end-to-end integration and accessibility for all WSPR operators, not a claim to be the first comparison tool or to provide calibrated antenna measurement.

WSPRadar should not be described as replacing wspr.live, WSPR.Rocks, WSPRdaemon, DXplorer or controlled RF measurement. It operates one methodological level above a spot browser: **which observations are eligible for this experiment, what paired difference was observed, what one-sided evidence remains, and can the conclusion be audited?**

<a id="sec-7"></a>
### 7. Scientific Methods

WSPRadar turns public WSPR decodes into explicit comparison units, then summarizes those units without allowing one very active station to dominate the station-balanced result. This chapter is the authoritative home for formulas, matching rules, eligibility and aggregation.

**Method orientation**

| Analysis design | Target role | Reference or counter-evidence | Lowest observation/comparison unit | Activity requirement | Timing relationship | Power normalization | Station-level aggregation | Segment-level aggregation | Principal interpretation boundary |
|---|---|---|---|---|---|---|---|---|---|
| Performance — no Reference, RX or TX | Target receiver or transmitter | RX: same transmitter decoded elsewhere; TX: other same-band signal decoded by the peer receiver | one Target-active peer-cycle | observable Target participation | same two-minute cycle | rate: none; successful Target SNR display: reported 30 dBm | one Decode Rate per peer | Station-balanced Decode Rate; Opportunity-level Decode Rate retained | observed conditional behavior of the complete Target station, not unconditional decode probability or a calibrated hardware measurement |
| Hardware A/B Test, RX | Target receiver | simultaneous Reference receiver | one consolidated remote-transmitter peer-cycle | Target-Active Gate | same transmitter and cycle | common TX power cancels; correction applies to Reference | median Delta SNR | median of station medians | controlled local receive paths only to the extent the remaining chains are controlled |
| Hardware A/B Test, simultaneous TX | Target transmitter | simultaneous Reference transmitter | one consolidated remote-receiver peer-cycle | Target-Active Gate | same receiver and cycle | both sides normalized to reported 30 dBm; correction applies to Reference | median Delta SNR | median of station medians | two distinguishable complete TX chains; power, frequency response, isolation and coupling remain experimental controls |
| Hardware A/B Test, sequential TX | Target scheduled starts | Reference scheduled starts | one peer identity in one planned Target/Reference pair | deterministic disjoint schedules; no simultaneous gate | nearest one-to-one starts under one shared Repeat Interval | both sides normalized to reported 30 dBm; correction applies to Reference | median scheduled-pair Delta SNR | median of station medians | sequential, not simultaneous; timing and switching effects remain |
| Reference Station / Buddy Test, RX | Target receiver | external Reference receiver | one consolidated remote-transmitter peer-cycle | Target-Active Gate; Reference uptime controlled externally | same transmitter and cycle | common TX power cancels; correction applies to the Reference | median Delta SNR | median of station medians | complete installed stations and environments, not isolated receiver sensitivity |
| Reference Station / Buddy Test, TX | Target transmitter | external Reference transmitter | one consolidated remote-receiver peer-cycle | Target-Active Gate; Reference uptime controlled externally | same receiver and cycle | both sides normalized to reported 30 dBm; correction applies to the Reference | median Delta SNR | median of station medians | complete installed stations; depends on reported-power accuracy |
| Local Median Neighborhood | Target RX or TX | cycle/path median of one contribution per active local `callsign + locator` | one Target/local-Reference peer-cycle | Target-Active Gate | same peer path and cycle | TX values normalized to reported 30 dBm; correction applied before the local median | median Delta SNR | median of station medians | dynamic uncalibrated pool; result depends on radius and active membership |
| Local Best Station | Target RX or TX | strongest qualifying local station for that cycle/path | one Target/best-Reference peer-cycle | Target-Active Gate | same peer path and cycle | TX values normalized to reported 30 dBm; correction applied before best selection | median Delta SNR | median of station medians | changing best-peer envelope, not a local average or fixed Reference |

The matrix is an orientation aid. The definitions, formulas and processing rules below are authoritative.

<a id="sec-7-1"></a>
#### 7.1 Data source, decode selection and time model

WSPRadar reads the public `wspr.rx` table through the selected read-only ClickHouse HTTP interface. Spots are observational records from independently operated transmitters, receivers, software and networks. They are not a randomized or calibrated sample of possible paths. Decode selection, historical fallback and upstream-data behavior are documented once in [Sections 5.4-5.6](#sec-6-4).

The selected UTC endpoints are resolved when the run starts, then both are quantized down to 15-minute boundaries for query reuse. WSPRadar applies the resulting time window consistently to Performance and Compare.

A **WSPR cycle** is the two-minute interval aligned to an even UTC minute. WSPRadar derives simultaneous cycles from spot timestamps. Sequential TX A/B instead retains timestamps, admits only each path's configured modulo schedule, and attaches the planned Target and Reference starts of its nearest one-to-one pair. A scheduled pair is eligible only when both planned starts fall within the analysis window.

<a id="sec-7-2"></a>
#### 7.2 Identity and matching rules

WSPRadar retains the reported identity as part of the evidence. Callsign variants and reported locators are therefore scientifically meaningful inputs, not cosmetic labels.

| Analysis | Target matching | Peer / Reference identity | Lowest result unit |
|---|---|---|---|
| RX Performance | exact RX callsign plus Target QTH grid-4 | TX callsign + reported TX locator | one Target-active peer-cycle |
| TX Performance | exact TX callsign plus Target QTH grid-4 | RX callsign + reported RX locator | one Target-active peer-cycle |
| Buddy Compare | exact Target callsign plus Target QTH grid-4 | exact Reference callsign plus independent Reference Locator; remote callsign + reported locator | one consolidated peer-cycle |
| RX Hardware A/B | exact Target callsign plus Target QTH grid-4 | exact Reference callsign plus the same derived Target grid-4; remote TX callsign + reported locator | one consolidated peer-cycle |
| Simultaneous TX Hardware A/B | exact Target callsign plus Target QTH grid-4 | exact Reference callsign plus the same derived Target grid-4; RX callsign + reported locator | one consolidated peer-cycle |
| Sequential TX Hardware A/B | exact shared Target callsign plus Target QTH grid-4, split by configured UTC schedule | same callsign and grid-4 on the Reference schedule; RX callsign + reported locator | one planned Target/Reference pair |
| Local Compare | exact Target callsign plus Target QTH grid-4 | local callsign + reported locator inside the radius; remote peer as above | one Target/local-Reference peer-cycle |

Performance and all Compare modes use exact Target callsign plus the first four characters of configured Target QTH. A six-character Target QTH remains meaningful outside archive selection because its full value anchors maps, local-radius geometry, azimuth/distance and solar calculations. Reference Station uses an independent exact Reference callsign plus an exactly four-character Reference Locator. Hardware A/B derives the shared grid-4 from Target QTH and stores no separate Reference QTH. Thus grid-6 is not a query selector: `JN37AA` and `JN37XX` both select `JN37`, while `JN38` does not. Shared Hardware A/B grid-4 matching cannot establish physical co-location.

Peer identities use exact callsign plus the full reported locator string. Bad, stale or changing locators can split one physical station, move it into the wrong segment or trigger the moving-station filter.

Across four audited demos, 99.83% of 223,197 side station-cycles contained exactly one qualifying row; all 373 multi-row cases occurred in the 2017 legacy dataset, while the other three demos had none. When multiple rows occur, WSPRadar uses the strongest qualifying normalized SNR as the logical station identity's best-observed value. Exact repeats and weaker secondary decodes cannot lower it, consistent with best-SNR merging in some multi-receiver systems. <a href="#ref-11">[Ref-11]</a> This is not a central estimate for one physical receiver; differences between sides in the number or distribution of non-identical rows can favor one side. Local Median Neighborhood instead takes a median within each local identity and then across identities.

The local pool excludes the Target by exact callsign. A base callsign and a suffixed callsign are therefore distinct identities unless the exact Target form matches. Each local contribution retains its reported locator as part of identity.

<a id="sec-7-3"></a>
#### 7.3 Target-Active Gate

The Target-Active Gate anchors Performance and simultaneous Compare to cycles in which Target participation is observable:

* **TX:** at least one qualifying Target transmission spot exists somewhere in the cycle.
* **RX:** at least one qualifying decode uploaded by the Target receiver exists in the cycle.

The gate protects known Target downtime from becoming automatic failure. For example, Reference spots from hours when the Target station is shut down are not counted as defeats.

The asymmetry is deliberate: in the absence of authoritative operating schedules, WSPRadar defines Performance and simultaneous Compare around the designated Target and admits only cycles with observable Target participation. In Compare, Reference uptime is not a second gate and must therefore be controlled by the experimenter.

Because every Joint observation already demonstrates Target participation, the gate's asymmetry affects only one-sided or asynchronous Decode Outcomes and the counter-evidence denominator of the Decode Rate; the gate itself does not alter Joint-only Delta SNR summaries.

Swapping Target and Reference can therefore change eligible cycles and Decode Outcomes. Sequential TX A/B uses deterministic schedule assignment and planned pairs rather than this simultaneous gate. Its role-independent half-interval tie rule preserves the same physical pairs when Target and Reference are swapped.

<a id="sec-7-4"></a>
#### 7.4 Performance classification and formulas

Performance evaluates the Target itself from opportunities that have independent evidence of network activity. Its Decode Rate describes the Target's observed conditional behavior within that qualifying population.

For each Target-active peer-cycle, WSPRadar records Target evidence and independent external evidence:

* **RX external evidence:** a different receiver reported the same transmitter identity in the same cycle.
* **TX external evidence:** the peer receiver reported a non-Target same-band transmitter in the same cycle.

The canonical scientific and compatibility terms remain `Target`, `Elsewhere`, `Other Signals` and `Target-only`. Canonical `Target` requires both Target and external evidence. In RX, canonical `Elsewhere` means external evidence without Target; in TX, canonical `Other Signals` means external evidence without Target. Canonical `Target-only` means Target evidence exists without external evidence and is excluded from the denominator.

The visible Performance page maps those unchanged categories to direction-aware plain language. RX displays canonical `Target` as `Heard by Target`, canonical `Elsewhere` as `Heard by others only`, and Target-only audit rows as `Heard by Target without independent confirmation`. TX displays canonical `Target` as `Target heard`, canonical `Other Signals` as `Other signals heard only`, and Target-only audit rows as `Target heard without independent RX-activity confirmation`. This mapping is presentation-only: it changes interpretation clarity, not classification, formulas, stored fields or compatibility exports.

$$\text{Decode Rate}_{RX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Elsewhere}}$$

$$\text{Decode Rate}_{TX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Other Signals}}$$

The eligible peer population is globally sourced after band, time, gate, filters and thresholds. Decode Rate is therefore conditional on observable network activity and propagation. It is not an estimate of every attempted transmission or a calibrated receiver detection probability.

Decode Rate itself is not power-normalized. The successful Target SNR displayed beside it is normalized to reported 30 dBm.

<a id="sec-7-5"></a>
#### 7.5 Power normalization, correction and Delta SNR

Power normalization places successful TX evidence on a common reported-power basis. WSPR SNR is decoder-reported in dB on the WSJT scale, referenced to a 2500 Hz bandwidth. WSPR messages include reported transmit power in dBm. <a href="#ref-8">[Ref-8]</a>

WSPRadar normalizes successful SNR to a reported 30 dBm reference:

$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$

This removes the **reported** power term. It does not correct antenna gain, efficiency, feedline loss, effective isotropic radiated power (EIRP), receiver calibration or local noise.

Reference-side SNR correction is added to the Reference side:

$$SNR_{reference,corrected} = SNR_{reference} + Correction$$

The general comparison definition is:

$$\Delta SNR = SNR_{target} - SNR_{reference,corrected}$$

A positive correction strengthens the Reference before subtraction and lowers Delta SNR. A negative correction raises Delta SNR. The applicable branches, entry convention and calibration guidance are in [Section 4.3](#sec-5-3) and [Appendix C](#sec-c).

TX comparisons use normalized SNR because different transmitted powers can be involved. In same-transmitter RX pairs, the common power term cancels. TX comparisons between different callsigns depend directly on reported-power accuracy.

<a id="sec-7-6"></a>
#### 7.6 Paired evidence and Decode Outcomes

Compare keeps two complementary views of performance.

1. **Paired Delta SNR:** the conditional Target-minus-Reference value where both sides produced comparable evidence.
2. **Decode Outcomes:** Joint, Only Target, Only Reference and Both (Async) evidence outside or around that paired subset.

This separation matters because paired-only Delta SNR analysis has survivorship bias: both sides must produce comparable evidence. A setup that adds many marginal decodes can have a lower pooled SNR median simply because it reaches weaker signals.

Decode Outcomes are not power-normalized. An exclusive TX observation has no missing-side SNR to reconstruct. Unequal transmit powers can therefore dominate exclusive TX evidence even when joint Delta SNR is normalized.

Compare map `STATIONS` categories assign identities; `SPOTS` categories count evidence volume. Performance map bars place `OPPORTUNITIES` above `STATIONS` and use the same direction-specific display labels in both rows. The upper row counts canonical Target and counter-evidence outcomes in the Decode Rate denominator; the lower row assigns qualifying RX identities to `Heard by Target` or `Heard by others only` and qualifying TX identities to `Target heard` or `Other signals heard only`. A `Joint Spot` is a consolidated same-cycle comparison unit, not necessarily one untouched database row.

<a id="sec-7-7"></a>
#### 7.7 Aggregation hierarchy

WSPRadar calculates a peer-level value before the geographic segment value. This gives each qualifying peer one vote in station-balanced summaries, so a high-volume station cannot dominate solely because it uploaded more observations.

Medians reduce sensitivity to isolated extreme values, duplicate-like bursts and quantized SNR outliers. They do not remove systematic calibration error, propagation bias or correlation across time and stations.

**Performance**

1. Classify each Target-active peer-cycle.
2. Sum Target, counter-evidence and Target-only by peer `callsign + locator`.
3. Require the configured Target+counter threshold.
4. Calculate one Decode Rate per qualifying peer.
5. Calculate the segment arithmetic mean of peer rates.
6. Retain the pooled Opportunity-level Decode Rate as a diagnostic.

The Station-balanced Decode Rate and Opportunity-level Decode Rate answer different questions. The first describes the typical qualifying identity with equal peer weights; the second gives every qualifying confirmed opportunity equal weight.

**Simultaneous Compare**

1. Consolidate Target and Reference evidence by cycle and peer identity.
2. Calculate Delta SNR for joint cycles.
3. Require the configured joint count for each peer.
4. Calculate one station-level median Delta SNR.
5. Calculate the segment median across station medians.

A Joint comparison is formed only when the same remote receiver decodes both distinguishable signals in the same WSPR cycle. This removes the sequential time gap in which QRM, short-term fading, receiver state and ionospheric conditions can change. It does not remove frequency-selective QRM or fading, transmitter-chain response differences or other systematic offsets; repeated Joint cycles can reduce random variation but not systematic bias.

**Sequential TX A/B**

1. Retain exact-callsign spots only when their UTC start matches the configured Target or Reference schedule.
2. Pair scheduled Target and Reference starts one-to-one by nearest cyclic separation and require both planned starts to fall within the analysis window.
3. Group each side by planned pair and peer `callsign + locator`.
4. Calculate one micro-median per side and pair.
5. Calculate Pair Delta where both micro-medians exist; retain a one-sided pair as Only Target or Only Reference.
6. Require the configured joint-pair count.
7. Calculate station and segment medians.

The two sides remain sequential. Short separation and balanced operation reduce time separation compared with long blocks, but schedule-timing and switching effects can remain.

**Local Median Neighborhood Reference**

1. Group each local Reference `callsign + locator` within cycle and remote peer.
2. Calculate that local identity's median normalized SNR.
3. Give that identity one contribution regardless of how many repeated rows it supplied.
4. If an identity has no qualifying observation for that cycle/path, omit it; never invent a `0 dB` contribution.
5. Take the exact inclusive midpoint median across the contributing local identities.
6. Compare Target with that cycle-level Reference.

With an even local pool, the midpoint of the two central values is used. The pool can change every cycle.

**Local Best Station Reference**

For each cycle and path, Local Best Station uses the strongest qualifying local station as the Reference. Reference correction is applied before best selection. The result is therefore a changing best-peer envelope, not a local average or a fixed Reference.

<a id="sec-7-8"></a>
#### 7.8 Distributions and inspection-layer weighting

The Segment Compare Delta SNR histograms use fixed bins within a panel. They normally use 1 dB bins, use 0.5 dB only for a clear half-dB lattice and aggregate broad ranges to 1, 2, 3, 6 or 10 dB so a panel does not exceed 40 bars. A minimum visible span of 3 dB avoids visually magnifying tiny variation.

Compare temporal heatmaps first count evidence in cells formed by UTC-time, or folded UTC-hour, bins and rounded integer-dB Delta SNR bins. Each panel is scaled independently:

$$D_{relative} = 100 \times \frac{n_{cell}}{\max(n_{cell,panel})}$$

The densest occupied cell is therefore `100`, proportional occupied cells lie between `0` and `100`, and empty cells remain blank. This is a percentage of that panel's maximum cell count, not a percentage of all evidence. Values and colors therefore do not provide absolute-count comparability between separately normalized panels. Segment-level and selected-station Compare timelines use this rule. The separate successful-SNR-deviation figure in Performance Temporal SNR Evidence uses the same per-panel relative-density normalization. Its companion Temporal Evidence figure instead uses independent left support axes for chronological station votes and opportunity counts or folded per-date average station presence and opportunity counts, green and grey outcome stacks, and a Decode Rate line on the right of every panel. The four right axes share one scale within a run; the left axes scale independently.


Compare Evidence Coverage classifies each retained comparison unit as Only Target, Joint or Only Reference. For station \(s\) in bin \(b\), let those counts be \(T_{s,b}\), \(J_{s,b}\) and \(R_{s,b}\), with \(N_{s,b}=T_{s,b}+J_{s,b}+R_{s,b}\). A contributing station supplies one split support vote:

$$v_{T,s,b}=\frac{T_{s,b}}{N_{s,b}},\qquad v_{J,s,b}=\frac{J_{s,b}}{N_{s,b}},\qquad v_{R,s,b}=\frac{R_{s,b}}{N_{s,b}}$$

The station-balanced Joint Evidence Share is \(100\times\operatorname{mean}_s(J_{s,b}/N_{s,b})\). The outcome-level Joint Evidence Share is \(100\times\sum_sJ_{s,b}/\sum_sN_{s,b}\). Chronological station stacks sum the split votes, while the lower row stacks the raw retained comparison-unit counts. Folded station support is the average number of contributing station-date-hour presences per represented UTC date, partitioned by the folded station-balanced Joint Evidence Share; folded comparison-unit counts are direct per-date averages. Joint Evidence Share describes the paired fraction available to Delta SNR. It is not a Target win rate. In simultaneous Compare, Only Target and Only Reference remain asymmetric under the Target-Active Gate. Sequential TX A/B instead uses deterministic scheduled pairs, but one-sided pairs still lack Pair Delta SNR and the two transmissions remain time-separated.

Performance Evidence starts from the full qualifying station population in the active Segment Inspector scope, independently of Station Insights filters, sorting, counter-only-station visibility or selected rows. It groups stations by their exact unrounded calculated distance from the Target QTH, not by the map's coarse distance label. The shared deterministic width is selected from `125`, `250`, `500` or `1,000 km` according to the selected distance span; edges remain anchored at integer multiples from `0 km`, the final selected upper boundary is included, and changing only direction does not change the bins. Disjoint selected ranges retain visible gaps. Distance comes from reported Maidenhead locators, so the displayed numerical grouping inherits their precision; Grid-4 is not survey-grade positioning.

Within each exact-distance bin, Peer Reach is `100 × stations with at least one Target outcome / all qualifying stations`. The RX display label `Heard by Target` and the TX display label `Target heard` both denote this same `hits ≥ 1` condition; `Heard by others only` and `Other signals heard only` denote qualifying stations with `hits = 0`. The Station-balanced Decode Rate is the arithmetic mean of the stations' individual `Target / (Target + counter-evidence)` rates; the Opportunity-level Decode Rate is `sum(Target) / sum(Target + counter-evidence)`. Counter-only stations remain in both denominators. The successful-SNR panel first contributes one median normalized successful Target SNR per station and then reports the median of those station medians. With three or more stations it also reports their interquartile range; with two it shows their range without labelling it as a quartile estimate; with one it shows only the station point. Counter-only stations have no synthetic SNR. The retained support data include qualifying-station, target-positive-station, confirmed-opportunity, Target, counter-evidence and successful-SNR-station counts, although the figure does not render a support-count strip. Unpopulated bins remain missing.

Performance Temporal Evidence applies the same active Segment Inspector scope before grouping. A station enters the anomaly layer only when it has at least three successful normalized Target SNR observations in the complete selected UTC window; its baseline is the median of those observations, and each successful observation's anomaly is its SNR minus that baseline. The chronological density receives at most one station-bin median per station and selected time bin. The folded density receives one station-date-hour median per station, UTC date and UTC hour, preventing prolific reporters from dominating either view. A horizontal `0 dB` line marks station baseline and the overlay is the station-balanced median of the contributed station values in each bin. Q1 and Q3 are computed from those same unrounded contributed values and drawn as fine rails only where at least five values contribute; an unsupported bin breaks the rails but does not suppress its median. They describe the middle 50% within the bin, not uncertainty or a confidence interval. The linear y-axis continues to include the complete finite SNR envelope; the quartiles do not set or clip its limits.

All qualifying stations, including those omitted only from the SNR-deviation figure, remain in the temporal evidence calculations. In each chronological bin, every contributing qualifying station supplies one split vote: its `Target / (Target + counter-evidence)` ratio is the green component and its complement is the grey component. Summing those components makes total bar height equal the number of contributing stations, while `green / (green + grey)` exactly reproduces the unchanged Station-balanced Decode Rate line. The chronological Opportunities row instead stacks the raw Target and counter-evidence counts, so total height is confirmed-opportunity volume and the same green share exactly reproduces the unchanged Opportunity-level Decode Rate line. The labels remain direction-aware — `Heard by Target` and `Heard by others only` for RX, `Target heard` and `Other signals heard only` for TX — and the station-vote segments can be fractional. At each folded UTC hour, station support counts every distinct station-date-hour presence once and divides that count by the represented dates whose hour slot overlaps the selected analysis window. The total station-bar height is therefore the average number of contributing stations per represented date at that hour; a station can contribute once on each date. The folded station-balanced rate remains a separate pooled equal-station calculation: each station's outcomes at that UTC hour are first pooled across represented dates, its rate is calculated, and every distinct station then receives one equal vote. The folded green component is average station support multiplied by that rate, and the grey component is its complement. Their ratio exactly reproduces the unchanged rate, but the components are a rate-partitioned support display rather than averages of station-date split votes. Folded opportunity components divide the pooled Target and counter-evidence counts by the same per-hour date denominator, so they are direct per-date averages and their ratio preserves the unchanged Opportunity-level Decode Rate. A represented date-hour with no evidence contributes zero and remains in the denominator, while a date whose hour slot lies outside the selected window is excluded. The single folded-date annotation reports the global number of represented UTC dates, but first and last boundary hours can use fewer overlapping dates. A partially overlapping boundary-hour slot counts as one represented slot rather than being weighted by its exposure fraction, so its folded mean can be depressed. Chronological `1 h` bars are directly comparable in units only when their bins are anchored to UTC-hour boundaries; wider chronological bins cover multiple hours and are not directly comparable by height. UTC-hour folding remains available only when at least two UTC dates contribute. All four right axes start at zero and share a ceiling chosen from the maximum of the four rate series with about 20% rounded headroom, capped at `100%`. Each left support axis scales independently and uses compact ham-style notation such as `6k4` for `6,400` and `6M8` for `6,800,000`. A bin with no rate evidence remains missing rather than becoming a synthetic `0%`, and changing the chronological display bin does not reclassify opportunities or rerun the analysis.

A **represented UTC date** is a date with at least one confirmed opportunity from a qualifying station somewhere in the active scope and selected window. A date with no such evidence anywhere is treated as absent coverage and is not introduced as an all-zero day.

Both panels in each Compare temporal figure use a presentation-only, median-centered nonlinear Delta SNR scale. The two segment temporal panels share the observation-level median of all paired evidence in the selected segment. The two selected-station temporal panels instead share the median of the one selected station's evidence. Thus each two-panel temporal scope has one center, while absolute labels preserve interpretation between scopes. The retained Segment Compare histograms use the same presentation principle within their respective evidence scopes.

The white connected markers remain a separate statistic: the median within each populated time bin. Fine Q1 and Q3 rails use the same raw Joint-Spot or complete-Scheduled-Pair values before integer heatmap binning or the nonlinear display transform. They appear only from five contributed values onward, break at unsupported bins and leave sparse medians visible. The rails describe the middle 50% of a bin, not uncertainty or a confidence interval, and do not alter the full finite evidence envelope used by the axis.

Let `M` denote that scope's exact evidence median. For a broad range, equal visual steps are anchored at `M`, `M +/- 3`, `M +/- 6`, `M +/- 10`, `M +/- 20` and `M +/- 30 dB`; an unlabelled tail anchor continues at `M +/- 60 dB` and extrapolates farther when necessary. If every required deviation from `M` is at most `10 dB`, the tighter visible anchors are `M`, `M +/- 1`, `M +/- 3`, `M +/- 6` and `M +/- 10 dB`; unlabelled `M +/- 20` and `M +/- 40 dB` anchors define the compressed continuation outside that visible range. The required deviation includes the applicable raw histogram or rounded heatmap-bin edges, a minimum 3 dB half-span and absolute `0 dB`, so tails and the Target-equals-Reference reference are not silently clipped.

Tick labels show the resulting **absolute Delta SNR**, not distance from `M`. For example, `M = +6 dB` produces the broad labels `-24, -14, -4, 0, +3, +6 M, +9, +12, +16, +26, +36 dB`.

The transform does not change scientific values or grouping. Segment-histogram counts and bin edges remain in raw dB, temporal cells remain rounded integer-dB bins, medians and quartiles remain raw-dB statistics, and relative-density colors retain the calculation above. Because nonlinear vertical stretching gives equal raw-dB bins in the retained Segment Compare histograms unequal displayed heights, read histogram **bar length** against `Share (%)`; displayed bar area is not probability. Performance SNR figures remain linear.

Selected Station Evidence in Compare filters the retained active-scope rows to exactly one selected `callsign + locator` identity and prepares two full-width figures from the same selected time-bin control. The first figure preserves the established absolute Delta SNR views. **Δ SNR over Time** places every retained Joint Spot or Scheduled Pair from that path in its actual UTC sequence using the selected aggregation bin. **Δ SNR by UTC Hour** folds those same observation-level rows across all represented dates into fixed one-hour UTC slots. The selected-path medians and Q1–Q3 rails use those raw observation-level values in both panels; each rail pair requires at least five Joint Spots or complete Scheduled Pairs in its bin. Each panel normalizes density independently to its own most populated cell, while both share the selected path's median-centered nonlinear Delta SNR axis and absolute dB labels.

The second figure is **Selected Path Evidence Coverage**. For simultaneous Compare, its **Retained WSPR Cycles over Time** and **Retained WSPR Cycles by UTC Hour** panels stack Only Target, Joint and Only Reference retained WSPR-cycle counts chronologically and as per-represented-date UTC-hour averages. Sequential TX A/B instead uses **Scheduled A/B Pairs over Time** and **Scheduled A/B Pairs by UTC Hour** to stack scheduled-pair counts on the same bases. Joint Evidence Share remains on the right axis. The figure deliberately omits the segment figure's station-support row because exactly one identity is selected and that row would duplicate the same outcome ratio. For either simultaneous RX or TX, one retained unit on the selected path is one WSPR cycle; sequential TX instead uses one scheduled A/B pair. UTC-hour folding for both figures requires at least two represented dates; with fewer dates, the folded panel is omitted and the chronological panel expands. Changing the selected bin changes only these retained-evidence presentations and never changes pairing or reruns the provider analysis.

Selected Station Evidence in Performance filters the retained active-scope rows to exactly one selected `callsign + locator` identity. **Selected Station SNR Evidence** reuses the Segment Inspector's chronological and folded layout but changes the SNR representation from station-relative deviation to actual normalized successful Target SNR. The chronological density receives every retained successful observation from that path, and its line is the median within each selected time bin. Its Q1–Q3 rails use those same unrounded observations and require at least five in the bin. The folded density first forms one median for every represented UTC date and UTC hour, then uses those date-hour medians as its population and draws their cross-date median and, from five represented-date values onward, Q1–Q3 rails. This date-hour reduction prevents a date with unusually many successful reports from dominating the folded profile. The rails are descriptive middle-50% spread rather than uncertainty intervals. Both panels use one linear actual-SNR range covering the complete finite population and normalize density independently to the maximum occupied cell in that panel.

The SNR figure is conditional on successful Target decodes or reports. Counter outcomes have no recorded Target SNR, no SNR is synthesized for them, and a station with no successful Target SNR receives the explicit unavailable state. Read the SNR figure together with Decode Rate because apparently strong successful SNR can coexist with a falling rate when weaker signals are no longer decoded. This successful-decode censoring prevents the SNR-only population from describing missed opportunities.

**Selected Station Temporal Evidence** reuses the complete lower 2×2 Segment Inspector figure for the same one-station population. In a chronological bin with confirmed evidence, the selected station contributes one split station vote: the green component is its successful-opportunity fraction and the grey component is its counter-opportunity fraction, so total station height is one. The opportunity row stacks every confirmed successful and counter opportunity, so its total height is evidence depth. With exactly one station, the Station-balanced Decode Rate and the Opportunity-level Decode Rate are numerically identical in every populated bin; both series remain visible because the station row explains path presence and the opportunity row explains evidence volume.

At each folded UTC hour, the station row shows average selected-station presence per represented UTC date, between zero and one, partitioned by the selected path's folded Decode Rate. The opportunity row divides the selected station's successful and counter counts by the same represented-date denominator, retaining an overlapping represented date-hour with no evidence as zero and excluding a date-hour outside the selected window. UTC-hour folding requires at least two represented UTC dates; with fewer dates, only the expanded chronological panels are shown. Changing selection or the display bin recomputes these views from retained evidence without changing opportunity classification, map or Segment Inspector results, Drill-Down rows, pairing, or the completed provider query.

<a id="sec-7-9"></a>
#### 7.9 Geography and solar classification

WSPRadar calculates distance and azimuth using a spherical Earth radius of 6371 km and renders an Azimuthal Equidistant projection centered on Target QTH. Radial boundaries are 2500, 5000, 10000, 15000, 20000 and 22000 km; azimuth sectors are 22.5 degrees.

This gives internally consistent mapping geometry. It is not survey-grade geodesy, and reported locators represent grid-cell positions rather than measured antenna coordinates.

`Maximum peer distance from Target (km)` applies this same Target-QTH geometry to mapped-peer rows after the globally sourced provider result has been retrieved. Only peers strictly nearer than the selected maximum are retained. The other rows are removed before scientific aggregation and before the processed Parquet artifact is published, so calculations, map segments, footer counts, Inspector evidence and exports describe the same peer population. Segment Inspector can select a narrower distance/direction subset of that population, but it cannot override the run scope. Provider queries and their raw cache remain global.

Two integrity rules intentionally precede that geographic filter. The Target-Active Gate remains global because out-of-scope evidence can establish that the Target operated without becoming a scoped peer outcome. When `Exclude Moving Stations` is enabled, changing-location callsigns are identified across the otherwise eligible global population before scope is applied, so a narrow radius cannot conceal movement.

`Solar state at Target QTH` uses solar elevation at Target QTH. Normal same-cycle evidence uses its cycle timestamp. Automatic scheduled TX A/B uses the midpoint between the two planned starts, so Target and Reference in one pair cannot be split into different solar classes. Selected Station Evidence reuses the retained rows and does not introduce a separate path-illumination classification.

<div style="page-break-before: always;"></div>

<a id="sec-8"></a>
### 8. Evidence-Matched Claims and Reproducibility

WSPRadar supports precise statements about observed conditional Target behavior, at-least-once reach, paired differences, one-sided evidence and where those patterns appeared. Strong reporting describes the evidence actually produced, preserves the run definition and keeps laboratory quantities separate from network observables.

<a id="sec-8-1"></a>
#### 8.1 Claims the evidence supports

Use the result type that matches the statement:

* **Performance** supports a statement about the Target's observed conditional behavior within independently confirmed opportunities. Its separate at-least-once panel supports a statement about reach during the selected interval. Use the receiver-sensitivity and expected-100% rows below together with the denominator in [Section 7.4](#sec-7-4).
* **Compare Delta SNR** supports a statement about paired Target-minus-Reference evidence. Use the gain and significance rows together with [Sections 7.5](#sec-7-5) and [7.6](#sec-7-6).
* **Decode Outcomes** support a statement about joint and one-sided evidence. Use the exclusive-decode row and report the paired subset separately.
* **Distance-dependent patterns** support a statement about the observed distance segments. Use the take-off-angle row because distance is observed while radiation angle is not.
* **Local Neighborhood Benchmark** supports a statement about the selected dynamic neighborhood definition. Use the local-median row and report radius, method and active contributors.

| Avoid | Evidence-matched wording |
|---|---|
| "Antenna A has 3 dBi more gain." | "Path A produced a +3.0 dB median normalized Delta SNR against B for the paired evidence in this band, window and segment." |
| "My receiver sensitivity is 72%." | "The Target receiver's Decode Rate was 72% among qualifying peer-cycles independently confirmed elsewhere." |
| "Performance should be close to 100%." | "Decode Rate is conditional on the run's independently confirmed opportunities; 100% is not the expected baseline." |
| "A is statistically significantly better." | "The paired median favored A for the reported paired evidence and scope; no significance test was performed." |
| "The antenna has a lower take-off angle." | "The observed advantage was concentrated in the specified longer-distance segments; radiation angle was not measured." |
| "A is more efficient because it had more exclusive decodes." | "A produced more exclusive decode evidence under the reported power, schedule and network conditions; efficiency was not isolated." |
| "The local median is the average local station." | "The Reference was the cycle/path median of one contribution per active local callsign+locator identity." |

<a id="sec-8-2"></a>
#### 8.2 Interpretation boundaries: what remains combined or unobserved

WSPRadar results describe operating station systems under selected network and propagation conditions. They can reveal comparative patterns in installed configurations, while the following laboratory quantities are not directly measured:

* antenna gain in dBi;
* radiation efficiency;
* take-off angle;
* calibrated receiver sensitivity;
* absolute field strength;
* every attempted or scheduled transmission;
* formal statistical significance or causation.

The evidence must also be interpreted with these properties of the data and design in view:

* crowd-sourced callsigns, locators, powers and spots can be wrong;
* the archive contains successful decodes rather than complete attempt/failure logs;
* Decode Rate is conditional on globally sourced observable opportunities;
* a TX cycle decoded nowhere is indistinguishable from no transmission without an external log;
* Target-active gating is asymmetric;
* simultaneous TX A/B retains two-chain power, frequency-response, isolation and coupling differences;
* sequential TX A/B remains time-separated;
* reported-power normalization is only as accurate as the reported field;
* station hardware, software, terrain, noise, polarization and propagation remain combined;
* network density varies by geography, band and time;
* distance does not establish radiation angle or propagation mode;
* upstream availability and archive corrections remain external.

These boundaries do not prevent useful station comparisons. They determine which quantity the result represents and how precisely it should be reported.

<a id="sec-8-3"></a>
#### 8.3 Reporting checklist

For a serious result, preserve the analysis definition, the evidence supporting the conclusion and the external experiment record.

* Save the versioned `.config`. It records the settings applicable to the run:
    * **Core Parameters:** RX/TX direction, Target callsign and QTH, band, and absolute UTC start and end boundaries;
    * **Comparison Parameters:** Benchmark Design and, as applicable, TX Hardware A/B method, Reference callsign, the Reference Station's independent grid-4, local benchmark method and radius, scheduled TX A/B repeat interval and path phases, and the Reference-side SNR-correction purpose plus signed dB value; Hardware A/B does not serialize a redundant Reference QTH;
    * **Advanced Settings:** solar-state selection, geographic analysis scope, special-callsign and moving-station exclusions, and the applicable evidence thresholds;
    * **durable result-view settings:** selected ranges and directions, the selected station, evidence time bins, and visibility of unpaired evidence or counter-only stations in Performance.

  Inactive comparison branches, table and Drill-Down filters and other transient UI state are not stored. The saved absolute UTC window is the same effective interval used by the analysis and can be replayed without advancing with time.

* Retain the analysis export package and report the evidence actually used for the conclusion:
    * UTC period, band, direction, Target identity, comparison design and selected geographic and temporal scope;
    * Decode Rate with its denominator and weighting level;
    * for Compare, joint-station and joint-spot or pair counts, station-level median Delta SNR, Joint Evidence Share and any material disagreement between station- and observation-weighted results;
    * for Performance, the qualifying-station and confirmed-opportunity support behind the displayed weighting and scope;
    * for Compare, relevant Decode Outcomes and `STATIONS` / `SPOTS` distributions;
    * the bounded interpretation and any known evidence limitations.

* Separately record experimental context that WSPRadar cannot infer or independently verify:
    * physical antenna, feedline and RF-path arrangement;
    * switch or splitter topology and the mapping between configured identities and physical paths;
    * transmitter, receiver, decoder and supporting software;
    * actual transmit power, its WSPR reporting basis and any calibration measurements;
    * actual operating or switching schedule, interruptions and reversed assignments;
    * faults, intentional changes, local interference, weather or other conditions relevant to interpretation.

The saved configuration restores the applicable analysis settings automatically. Retain the original export package as the evidence record for that run because a later retrieval can reflect changes in upstream records or WSPRadar.

Replication, path swapping or independent calibration can strengthen a small observed difference before it supports an expensive decision.

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
  figure_segment_temporal_evidence.png
  figure_segment_temporal_coverage.png
  figure_selected_station_evidence.png
  figure_selected_station_coverage.png
  table_station_insights_current_segment.csv
  table_drilldown_selected_stations.csv
  table_drilldown_all_stations_current_segment.csv
  analysis_cache.parquet
success/                         # canonical compatibility folder for a Performance result
  figure_map_highres.png
  figure_segment_insight.png
  figure_segment_temporal_snr_deviation.png
  figure_segment_temporal_evidence.png
  figure_selected_station_snr_evidence.png
  figure_selected_station_temporal_evidence.png
  table_station_insights_current_segment.csv
  table_drilldown_selected_stations.csv
  table_drilldown_all_stations_current_segment.csv
  analysis_cache.parquet
```

Figures use a high-resolution light/paper presentation. Files without an applicable recipe or selected evidence can be absent. CSV files reflect current segment and station selections. Parquet files contain processed post-filter evidence, including only peer rows retained by the run's geographic analysis scope, not untouched upstream dumps.

For Performance, `figure_segment_insight.png` contains the direction-specific at-least-once station-reach panel, **RX/TX Decode Rate by TX-/RX-Station Distance**, and **Successful Target SNR by TX-/RX-Station Distance** for the active Inspector scope. `figure_segment_temporal_snr_deviation.png` contains the chronological/UTC-hour **RX/TX Performance Temporal SNR Evidence** figure, including its supported Q1–Q3 rails. `figure_segment_temporal_evidence.png` contains the aligned lower **RX/TX Performance Temporal Evidence** figure with shared **Evidence over Time ({time_bin} bins)** and **Evidence by UTC Hour (1 h bins)** column headers, short chronological station/opportunity y-axis labels, denominator-explicit folded average-per-represented-date y-axis labels, direction-specific green/grey outcome stacks, four common-scale Decode Rate axes and one shared legend. Its folded y-axis labels identify average station-date-hour support and average opportunities per UTC date; its chronological stacks remain counts per selected time bin. When fewer than two UTC dates contribute, the chronological panels expand and the folded-view fallback is retained.

The two stable filenames for a station selected in Performance preserve the shared temporal views independently. `figure_selected_station_snr_evidence.png` contains the full-width **Selected Station SNR Evidence** figure with actual normalized successful Target SNR, every successful observation in the chronological density, one median per represented date-hour in the folded density and supported Q1–Q3 rails in both panels. `figure_selected_station_temporal_evidence.png` contains the full-width **Selected Station Temporal Evidence** figure with station presence, opportunity depth and their equal one-station Decode Rate series. Both use the same selected identity, temporal recipes and renderers as their browser previews, and both omit folded UTC-hour panels when fewer than two represented dates contribute. For Compare, `figure_segment_temporal_evidence.png` remains the absolute paired Delta SNR timeline and `figure_segment_temporal_coverage.png` contains the station/outcome coverage view. `figure_selected_station_evidence.png` contains the selected path's absolute Delta SNR panels; both absolute Compare PNGs include supported Q1–Q3 rails. `figure_selected_station_coverage.png` contains its Only Target, Joint and Only Reference coverage plus Joint Evidence Share. The applicable figures use the same browser recipes and omit folded UTC-hour panels when fewer than two represented dates contribute.

The saved configuration records the applicable runnable settings. `run_metadata.json` automatically records the application name and version; export time; language; direction; band; benchmark choice; configured time selection; Reference-side correction mode and numeric value as `benchmark_snr_correction_mode` and `benchmark_snr_correction_db`; filters; thresholds; result blocks and inspector selections. For selected Performance evidence, metadata also populates `selected_station_label`, `selected_station_context`, `selected_station_count`, `selected_station_role`, `selected_evidence_weighting` and the stable filename-to-description mapping `selected_evidence_figures`; it records the one exact selected identity and a count of one. Compare records its zero-or-one exact identity in the compatibility field `selected_stations`, its selection count, selected chronological evidence bin and dual-panel evidence recipe; there is no selected active-view field because the figure contains both time panels. For each applicable complementary Compare figure, `compare_evidence_figures` maps its stable filename to the localized figure title; the export signature fingerprints the corresponding `compare_evidence_recipes` without duplicating their scientific arrays. The optional descriptive Performance fields remain unset. Both browser paths display one exact selected identity and never combine several station paths.

The package contains the processed evidence used by the completed analysis, not untouched upstream responses or authoritative external operating and calibration records. Retain the ZIP with the external experiment record described in [Section 8.3](#sec-8-3).

<a id="sec-8-5"></a>
#### 8.5 Disclaimer

WSPRadar is experimental open-source software provided "as is" without warranties. Its source and methods can be audited, but accuracy, completeness, availability and suitability are not guaranteed. Do not make major financial or safety decisions from WSPRadar alone.

<div style="page-break-before: always;"></div>

<a id="sec-ref"></a>
### References

* <a id="ref-1"></a><a href="https://arxiv.org/abs/2209.08989">[Ref-1]</a> **Preprint.** Zander, J. (2022). *Simple HF antenna efficiency comparisons using the WSPR system*. arXiv:2209.08989v1. doi:10.48550/arXiv.2209.08989.

* <a id="ref-2"></a><a href="https://doi.org/10.1155/2022/4809313">[Ref-2]</a> **Peer-reviewed article.** Vanhamel, J.; Machiels, W.; Lamy, H. (2022). *Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*. International Journal of Antennas and Propagation, 2022, 4809313. doi:10.1155/2022/4809313.

* <a id="ref-3"></a><a href="https://sivantoledotech.wordpress.com/2010/09/24/failure-to-use-wspr-to-compare-antennas/">[Ref-3]</a> **Operator technical account.** Toledo, S. / 4X6IZ (2010). *Failure to Use WSPR to Compare Antennas*.

* <a id="ref-4"></a><a href="https://www.qsl.net/kp4md/wspr.htm">[Ref-4]</a> **Amateur-radio technical article and club presentation.** Milazzo, C. F. / KP4MD (2011). *Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*.

* <a id="ref-5"></a><a href="https://www.researchgate.net/publication/319903566_Improving_HF_Band_SNR_from_analysis_of_WSPR_spots">[Ref-5]</a> **Amateur-radio magazine article.** Griffiths, G.; Squibb, N. J. (2017). *Improving HF Band SNR from analysis of WSPR spots*. Practical Wireless, October 2017, 23-26.

* <a id="ref-6"></a><a href="https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf">[Ref-6]</a> Taylor, J. H.; Walker, B. (2010). *WSPRing Around the World*. QST, 94(11), 30-32.

* <a id="ref-7"></a><a href="https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2023.1184171/full">[Ref-7]</a> **Peer-reviewed review article.** Frissell, N. A. et al. (2023). *Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations*. Frontiers in Astronomy and Space Sciences, 10, 1184171. doi:10.3389/fspas.2023.1184171.

* <a id="ref-8"></a><a href="https://www.arrl.org/wspr">[Ref-8]</a> **Official technical overview.** ARRL, *WSPR*: message format, coding, duration, timing, occupied bandwidth and SNR reference. Accessed 2026-07-12.

* <a id="ref-9"></a><a href="https://www.mdpi.com/2073-4433/13/8/1340">[Ref-9]</a> **Peer-reviewed article.** Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). *A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals*. Atmosphere, 13(8), 1340. doi:10.3390/atmos13081340.

* <a id="ref-10"></a><a href="https://wspr.live/">[Ref-10]</a> **Official data-service documentation.** WSPR.live, *Welcome to WSPR Live* and <a href="https://wspr.live/wspr_downloader.php">*WSPR Exporter*</a>: database description, schema, mode-code mapping, raw-data/availability disclaimer and real-time delay. Accessed 2026-07-15.

* <a id="ref-11"></a><a href="https://wsprdaemon.readthedocs.io/en/stable/description/how_it_works.html">[Ref-11]</a> **Tool documentation.** WSPRdaemon, *How wsprdaemon Works*: multi-receiver decoding, reporting, scheduling, noise and Doppler metadata.

* <a id="ref-12"></a><a href="https://wsjt.sourceforge.io/wsjtx-main_en.html">[Ref-12]</a> **Official operating documentation.** WSJT-X 3.0.1 User Guide: WSPR message formats and decoder performance; Windows `--rig-name` file isolation; Audio settings and file locations. QRP Labs, <a href="https://www.qrp-labs.com/images/qmx/manuals/operation_1_03_000.pdf">*QMX Operating Manual, firmware 1_03_000*</a>: Beacon `Frame` and `Start` scheduling and WSPR repetition guidance; <a href="https://qrp-labs.com/images/ultimate3s/operation3.12a.pdf">*Ultimate3S Operating Manual, firmware v3.12a*</a>: global Frame/Start behavior, sequential mode entries and per-entry `Aux` values; <a href="https://qrp-labs.com/images/appnotes/AN003_A4.pdf">*AN003: Ultimate3/3S relay-switched filters*</a>: filtered relay/driver interfacing and RF-off switching intervals. Accessed 2026-07-15.

* <a id="ref-13"></a><a href="https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf">[Ref-13]</a> **Conference paper.** Griffiths, G.; Robinett, R. (2020). *Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana*. ARRL/TAPR Digital Communications Conference 2020.

* <a id="ref-14"></a><a href="https://wspr.rocks/help.html">[Ref-14]</a> **Tool documentation.** WSPR.Rocks, *Help &amp; Documentation*: SpotQ, SQL access, duplicate analysis, maps, charts and heatmaps.

* <a id="ref-15"></a><a href="https://www.sotabeams.co.uk/wsprlite-classic">[Ref-15]</a> **Product documentation.** SOTABEAMS, *WSPRlite Classic / DXplorer*: WSPR-based antenna-performance analysis and DX10 metric.

* <a id="ref-16"></a><a href="https://sites.google.com/myuba.be/wspr-station-compare/home">[Ref-16]</a> **Project documentation.** WSPR-Station-Compare, project page referencing Vanhamel et al. and Zander.

* <a id="ref-17"></a><a href="https://wspr.bsdworld.org/">[Ref-17]</a> **Tool documentation.** Antenna Performance Analysis Tool, WSPR-based antenna report generator.

* <a id="ref-18"></a><a href="https://www.gm4eau.com/home-page/wspr/">[Ref-18]</a> **Tool documentation.** GM4EAU, *WATT WSPR Analysis Tool*: Excel/VBA reporting, mapping, filtering and timeline animation.

<div style="page-break-before: always;"></div>

<a id="part-iv"></a>
## Part IV: Practical Supplements

This part collects optional parallel WSJT-X and simultaneous-TX setup procedures, sequential TX A/B scheduling and switching guidance, Reference-side calibration and the project license. Use the sections that apply to your station and experiment.

<a id="sec-a"></a>
### Appendix A: Parallel WSJT-X Instances

This procedure creates a second isolated WSJT-X instance, for example for simultaneous RX or TX Hardware A/B Test on Windows. The current WSJT-X guide documents `--rig-name` as the supported way to isolate each instance's settings and writable files. WSJT-X versions and installation paths can change, so verify the current guide if your menus differ. <a href="#ref-12">[Ref-12]</a>

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
#### A.4 Configure distinguishable simultaneous TX

For simultaneous TX Hardware A/B, isolation of settings is only the software foundation. Before radiating, verify the complete two-transmitter arrangement into suitable loads or through a safely engineered low-power test path:

1. Assign the exact Target callsign and QTH to one instance and the different exact Reference callsign to the other. Configure the Reference instance to report from the same test QTH; WSPRadar displays disabled Target and Reference Locator fields derived from the first four Target-QTH characters and matches both uploaded identities within that shared grid-4.
2. Route each instance to its intended radio, control interface and audio output. A copied configuration must not key or feed the wrong transmitter.
3. Use the normal WSPR dial frequency on both radios if appropriate, but assign separated audio TX offsets such as `1450 Hz` and `1550 Hz`. Inspect the waterfall and choose clear, non-overlapping positions rather than assuming those illustrative values are free.
4. Configure deliberate same-cycle starts. Independent randomized `Tx Pct` settings do not define a synchronized comparison schedule.
5. Verify frequency, actual RF power, spectral cleanliness, clock alignment and uploaded callsign/QTH/power for both paths before collecting evidence.
6. Confirm adequate isolation between active transmitters and antennas. Coupled power can desensitize or damage equipment and can create intermodulation or misleading spots; use appropriate filtering, spacing, power levels and RF engineering for the station.

For a small observed difference, repeat with exchanged audio-frequency assignments and perform a hardware crossover where practical. Preserve both runs separately; do not pool them until the role, correction and analysis scope are aligned.

<div style="page-break-before: always;"></div>

<a id="sec-b"></a>
### Appendix B: Sequential TX A/B Scheduling and Switching

This appendix collects the practical schedule and switching guidance behind the TX Hardware A/B playbook. Exact UI controls are in [Section 4.3](#sec-5-3), and exact scheduled-pair construction is in [Sections 7.1](#sec-7-1) and [7.7](#sec-7-7).

<a id="sec-b-1"></a>
#### B.1 Requirements for a valid scheduled experiment

For sequential TX A/B antenna tests, one transmitter feeding two RF paths through a controlled switch is normally preferable to two independent transmitters. Transmitter, frequency reference, WSPR chain, callsign, power setting and timing remain common.

Use one normal valid callsign for both paths and identify the paths through different deterministic UTC phases. Enter the transmissions that actually occur on each RF path:

* `Repeat Interval` is each path's actual recurrence, not necessarily a transmitter's displayed `Frame` value.
* `Target Start` and `Reference Start` are different even UTC phases below that interval.
* Use the shortest practical separation compatible with reliable operation and an acceptable duty cycle.
* Report actual power; do not encode path identity through false dBm values.
* Verify clock synchronization and the physical schedule-to-path mapping before transmitting.

A deterministic scheduler or controller is required. Standard randomized WSJT-X transmit-percentage operation does not create a fixed A/B sequence.

<a id="sec-b-2"></a>
#### B.2 WSPRadar Timed A/B Relay Switch

WSPRadar includes:

`tools/Timed-AB-Relay-Switch`

Currently published version-0.1 release package:

[Download the Timed A/B Relay Switch release package](https://github.com/markusthemaker/WSPRadar/releases/download/timed-ab-relay-switch-v0.1.0/Timed-AB-Relay-Switch-v0.1.0.zip)

The repository helper uses the same schedule vocabulary and constraints as WSPRadar:

* `Repeat Interval` is shared by Target and Reference and accepts `4, 6, 10, 12, 20, 30` or `60 min`.
* `Target Start` and `Reference Start` are different even UTC phases below that interval.
* The default is `Repeat Interval = 10`, `Target Start = 00`, `Reference Start = 02`.

The relay selects each path before its configured start and holds the most recently selected path through unscheduled gaps. It does not switch at unused two-minute WSPR boundaries. Configure the helper and WSPRadar identically from the transmissions that actually occur on each RF path. If physical polarity is reversed, change whether relay ON means Target or swap the two Start assignments.

An optional lead time lets the RF path settle before every scheduled start. Manual physical relay ON/OFF control remains available independently of automatic scheduling. Existing version-0.1 modulo-4 configurations retain their old behavior as `4 / 00 / 02` or `4 / 02 / 00` when loaded. The helper targets common ATtiny45/V-USB HID relay boards with USB VID/PID `16c0:05df` and uses the Python HID stack on Windows, Linux and macOS. Consult its README for current installation, permissions and options.

The linked version-0.1 package still contains the former fixed modulo-4 scheduler. Until a newer package is published, use the repository version for the configurable schedule described here.

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

<a id="sec-b-3"></a>
#### B.3 Ultimate3S schedule example

The QRP Labs Ultimate3S can run a sequence of WSPR entries and apply a per-entry `Aux` output to external path-switching hardware. When a two-entry sequence begins at `00`, a global 10-minute frame can use Target at `00`, Reference at `02`, then pause until the next sequence at `10`; in WSPRadar this is `Repeat Interval = 10`, `Target Start = 00`, `Reference Start = 02`. The same arrangement with a 20-minute global frame gives each path a 20-minute recurrence while retaining two-minute A/B separation.

The Ultimate3S manual documents `Start = 00` specially as "not used", so verify the displayed and observed UTC sequence and enter its actual phases rather than assuming a literal setting-to-time mapping. The `Aux` lines share display signals; use the documented filtered driver or relay interface and switch only in the RF-off interval <a href="#ref-12">[Ref-12]</a>.

<a id="sec-b-4"></a>
#### B.4 QMX schedule examples

One QMX with `Frame = 10`, `Start = 0` transmits at `00, 10, 20, 30, 40, 50`. If an external switch alternates those transmissions between paths, Target is `00, 20, 40` and Reference is `10, 30, 50`; each path repeats every 20 minutes. Enter `Repeat Interval = 20`, `Target Start = 00`, `Reference Start = 10`; do not enter `10 / 00 / 02`.

A single QMX cannot produce an adjacent `00/02` pair followed by an eight-minute pause with that beacon scheduler. It can alternate adjacent paths only by transmitting every two minutes, which the QMX manual discourages as antisocial network use. Two independently scheduled QMX units with `Frame = 10`, Starts `00` and `02`, do implement WSPRadar's `10 / 00 / 02` schedule, but their transmitter chains and actual powers must be controlled as separate hardware <a href="#ref-12">[Ref-12]</a>.

<a id="sec-b-5"></a>
#### B.5 Verify mapping and preserve the experiment

Before transmitting:

* test without RF power;
* verify Target and Reference path polarity;
* verify no transition occurs during a WSPR transmission;
* use a dummy load or low-power continuity/SWR test;
* document relay channel, polarity, lead time, actual on-air schedule, schedule assignment and path mapping.

Switch loss, isolation, connectors, feedline differences and antenna surroundings remain part of the result. Swapping antennas between switch paths can help separate antenna effects from path effects. Repeating the experiment with reversed schedule assignments can help expose timing or role-dependent effects.

<div style="page-break-before: always;"></div>

<a id="sec-c"></a>
### Appendix C: Reference SNR Calibration

This procedure estimates a stable additive offset between receive chains or Reference-side paths.

1. **Common input:** feed both receive chains from one stable antenna through a suitable splitter and controlled cables.
2. **Characterize the splitter:** account for output imbalance and cable differences; swap outputs in a control run when practical.
3. **Collect paired evidence:** operate simultaneously across the intended signal levels without changing gain or decoder settings.
4. **Estimate the offset:** use paired Delta SNR evidence and state whether the estimator is station-balanced or raw-pair.
5. **Check consistency:** inspect by station, time and SNR. One constant is not defensible if offset changes with level, frequency, AGC or time.
6. **Apply the sign:** enter the observed `target - reference` offset with the same sign.
7. **Validate:** repeat or swap paths and confirm corrected common-input Delta is plausibly near zero.

Consistency across station, time and SNR views supports using one additive offset within the tested setup; it does not establish traceable laboratory accuracy. Splitter loss, mismatch, coupling and source instability can remain.

<a id="sec-license"></a>
### License

WSPRadar is licensed under the GNU Affero General Public License version 3 (AGPLv3). The repository `LICENSE` file is controlling.
