# docs/doc_en.py

"""Authoritative English end-user and scientific manual for WSPRadar."""

DOC_EN = r"""
---

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

The result is more than a spot count and more than a single winner-versus-loser number. WSPRadar can show whether a pattern is broad or path-specific, whether it is associated with distance or direction, whether it appears once or recurs by time of day, whether many stations agree, and whether the paired evidence represents the wider result. It helps move station experimentation from **“this looked better once”** toward **“this difference repeatedly appeared here, under these conditions, with this much support.”**

WSPRadar is not a calibrated antenna range, and it does not turn public WSPR reports into laboratory measurements. It provides a practical bridge between everyday station experimentation and amateur science: semi-quantitative, geographically rich, time-aware and auditable evidence about complete stations and controlled signal paths under real operating conditions.

Used this way, WSPR becomes more valuable to the wider amateur community as well. Accurate callsigns, locators and power reports, stable operation and documented changes turn routine beaconing into evidence that can be revisited, compared and learned from rather than merely watched on a map.

<a id="sec-1-1"></a>

#### 0.0 WSPR in 2 Minutes

<strong class="defined-term">WSPR</strong> stands for **Weak Signal Propagation Reporter**. Joe Taylor, K1JT, and Bruce Walker, W1BW, described it as a worldwide network of low-power stations exchanging beacon-like transmissions to explore possible propagation paths. A WSPR-2 transmission lasts just under two minutes and occupies only about 6 Hz. Its message normally contains a callsign, a four-character Maidenhead locator and reported transmit power in dBm. Decoder-reported signal-to-noise ratio (SNR) is referenced to a 2500 Hz bandwidth, and successful decodes are possible at approximately `-28 dB`; a less negative SNR means a stronger signal relative to the receiver noise <a href="#ref-6">[Ref-6]</a> <a href="#ref-8">[Ref-8]</a>.

When reporting is enabled, a receiver uploads each successful decode as a <strong class="defined-term">spot</strong>. A spot records the transmitter and receiver identities, their reported locations, time, band, transmit power and decoder-reported SNR. Public archives consequently contain a large, continuously growing record of successful radio observations contributed by independently operated stations around the world. Services such as wspr.live and WSPRDaemon preserve and expose this observational record for analysis <a href="#ref-10">[Ref-10]</a> <a href="#ref-11">[Ref-11]</a>.

One limitation is central to every analysis: the archive records successful decodes, not a complete log of every attempted transmission or every active receiver. WSPRadar therefore constructs an <strong class="defined-term">opportunity</strong> only when independent evidence shows that the relevant remote transmitter or receiver was active. For RX, another eligible receiver must have decoded the same transmitter. For TX, the remote receiver must have decoded another signal on the same band. Without such supporting activity, a missing Target spot is not automatically treated as a radio failure.

This distinction turns WSPR from a collection of successful spots into evidence that can support questions about practical reach, consistency and relative performance without pretending that every missing report represents a failed radio path.

<a id="sec-1-0"></a>
<a id="sec-1-2"></a>

#### 0.1 What WSPRadar can show

WSPRadar is a WSPR-based antenna and station performance analysis and benchmarking system. It evaluates one <strong class="defined-term">Target</strong>: either a complete installed station or a controlled transmit or receive path. It then answers one of two broad questions.

* <strong class="defined-term">Performance</strong> asks how the Target behaved across independently confirmed WSPR opportunities. It can reveal practical footprint, at-least-once reach, Decode Rate, successful signal levels, distance and direction structure, temporal behavior, and the breadth and depth of the supporting evidence.
* <strong class="defined-term">Benchmark</strong> asks how the Target behaved relative to a meaningful <strong class="defined-term">Reference</strong> under matched conditions. It can reveal paired Target-minus-Reference Delta SNR, joint and one-sided Decode Outcomes, how much evidence was pairable, and where and when the relative difference appeared.

The question determines the appropriate evidence design:

| Analysis | Question | Practical examples |
|---|---|---|
| <strong class="analysis-choice-single">RX Performance</strong> | How broadly and consistently does my receiver decode signals that were independently confirmed elsewhere? | Establish the receiving footprint of a newly commissioned antenna or station; see whether reception is broad but intermittent or narrower and consistent; identify recurring direction, distance or UTC-hour patterns, including periods that may warrant a separate check for local noise or intermittent hardware. |
| <strong class="analysis-choice-single">TX Performance</strong> | Where, when and how consistently is my transmitter decoded by receivers independently shown to be active? | Map where a QRP beacon or newly installed antenna is heard; see when and in which directions independently confirmed active receivers decode the station most consistently; establish a station baseline after commissioning, repair or relocation, and use comparable repeat runs to determine whether its observed behavior later changes. |
| <span class="analysis-choice"><span class="analysis-family">RX Benchmark</span><br><strong class="analysis-variant">Hardware A/B</strong></span> | Did two local receive paths differ while observing the same remote transmissions? | Compare two antennas, each feeding its own simultaneous receiver and decoder chain, as complete receive paths; attribute a difference specifically to the antennas only when the remaining chains are matched, characterized or confirmed by crossover; feed one antenna through a characterized splitter into two receivers to compare receiver or decoder paths; place a preamplifier, filter, feedline or common-mode choke in only one otherwise controlled path and benchmark the two documented complete receive paths. |
| <span class="analysis-choice"><span class="analysis-family">TX Benchmark</span><br><strong class="analysis-variant">Hardware A/B</strong></span> | Did two local transmit paths differ under simultaneous or tightly scheduled operation? | Feed two antennas from separate calibrated transmit chains and transmit simultaneously with synchronized cycles, distinguishable signals and adequate isolation; use one transmitter and a controlled RF switch to alternate between two antennas on a fixed UTC schedule; compare two feedlines, matching networks, filters or complete transmit paths while controlling actual power, timing and the remaining chain. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Reference Station / Buddy Test</strong></span> | How does my complete station compare with one known station? | <strong>RX:</strong> compare your receiver with a known Buddy receiver while both observe the same remote transmitters in the same cycles; <strong>TX:</strong> compare your transmitter with a Buddy transmitter at the same remote receivers in the same cycles; repeat a stable, well-understood Buddy design as a relative whole-station baseline before and after documented station work, without treating the Buddy as an absolute calibrated standard. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Local Median Neighborhood</strong></span> | How does my station compare with the typical active WSPR group nearby? | See whether your receive or transmit station is broadly above, near or below the cycle- and path-specific median of active local peers inside the selected radius; commission a station when no single suitable Buddy Reference is available; identify directions, distances or UTC periods where the station departs from that contextual local baseline, while checking neighborhood membership and radius sensitivity. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Local Best Station</strong></span> | How does my station compare with the strongest active nearby peer available on each path and cycle? | Compare your station with the strongest qualifying nearby station available on each path and cycle; find directions or distance ranges where your station approaches or trails the changing local-best envelope; in comparable repeat runs, track whether the observed gap narrows or widens while checking radius and pool membership, without treating the result as a ranking against one permanent competitor or a stable calibrated baseline. |

The Reference is part of the scientific question, not just a display choice. A controlled <strong class="defined-term">Hardware A/B Test</strong> provides the strongest basis for attributing an observed difference to local paths or components, but only to the extent that the remaining chains are controlled. A <strong class="defined-term">Reference Station / Buddy Test</strong> compares two complete installed stations, including their QTHs, equipment, terrain and local noise environments. Neighborhood benchmarks provide changing contextual baselines rather than fixed or calibrated standards.

These perspectives make WSPRadar useful for more than formal antenna comparisons. Performance can establish a station baseline, show where a station is dependably heard, reveal directional or distance-dependent behavior, identify recurring daily patterns, and help locate when an intermittent change appeared. Benchmark can compare antennas, feedlines, filters, preamplifiers, receivers or complete paths; contrast two complete stations; or place one station in the context of its active local neighborhood.

WSPRadar can identify the **shape, scope and timing** of an observation. It can show that a difference is broad, concentrated, intermittent, recurring or supported by only a narrow subset of stations. It cannot by itself determine that the cause was antenna gain, radiation efficiency, take-off angle, calibrated receiver sensitivity, local noise or one particular hardware component. No later statistic can remove a variable that the physical experiment did not control.

<a id="sec-1-3"></a>

#### 0.2 What one run produces

A WSPRadar run produces a connected evidence package for one clearly bounded station question — not a universal score and not a leaderboard.

A Performance run brings together practical reach, two complementary Decode Rate weightings, successful Target SNR, distance and direction structure, chronological change, recurring UTC-hour behavior, contributing stations and the underlying opportunities. A Benchmark run combines paired Delta SNR with Decode Outcomes and evidence coverage so that a favorable paired median cannot hide extensive one-sided evidence or a narrow pairable subset.

Every result follows the same evidence path:

> <strong class="defined-term">Map → Segment Inspector → Performance/Benchmark Evidence → Temporal Evidence → Station Insights → Selected Station Evidence → Drill-Down</strong>

The map provides the geographic overview. Segment-level evidence shows how the observation changes with distance and direction and how much support lies behind it. Performance or Benchmark Evidence separates the main result from its complementary evidence. Temporal Evidence shows whether the pattern changed during the run or recurred at particular UTC hours. Station Insights reveals which station identities contribute. Selected Station Evidence follows one exact radio path, and Drill-Down exposes the observations, same-cycle comparisons or scheduled A/B pairs behind the summaries.

This layered structure is one of WSPRadar's central strengths: the high-level pattern remains connected to its evidence. An operator can move from **where the effect appears**, through **how consistently it appears and how well it is supported**, down to **the individual observations from which the conclusion was built**.

A credible result is therefore not simply the largest value on the screen. It is one in which the experiment design, geographic pattern, temporal behavior, station breadth, evidence depth and row-level audit support the same bounded interpretation. Repeating the design in another suitable operating window can then test whether the observation is experimentally repeatable rather than only internally consistent within one run.

The complete run can also be preserved as a reproducibility package containing its analysis definition, processed evidence, tables, figures and metadata, ready to be reviewed later or shared with another operator alongside the physical station notes that WSPRadar cannot infer.

<a id="sec-1-4"></a>

#### 0.3 Your first useful run

The quickest way to understand WSPRadar is to begin with a maintained demo. A demo presents a complete historical Performance or Benchmark analysis with a prepared experimental context, allowing the evidence path to be explored before your own station is involved.

The value of the demo becomes clear in the connection between its layers: the geographic overview, distance and direction, isolated versus recurring temporal behavior, the number and diversity of supporting stations, the pairability of Benchmark evidence, and the selected-path and row-level observations behind the summary.

A demo is a worked example of WSPRadar's method, not evidence about your own station. Once the evidence path is familiar, the most useful first analysis of your own station begins with one clear question: establish its RX or TX Performance baseline, compare two controlled local paths, benchmark against a known station, or place it in its local WSPR context.

The aim is not to produce a flattering number. It is to obtain a result you can understand, question, repeat and use to make a better-informed decision about the station.

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
    * [2.1 RX Performance](#sec-3-rx-performance)
    * [2.2 TX Performance](#sec-3-tx-performance)
    * [2.3 RX Benchmark](#sec-3-rx-benchmark)
        * [2.3.1 Hardware A/B: simultaneous receive paths](#sec-3-rx-benchmark-hardware)
        * [2.3.2 Reference Station / Buddy Test](#sec-3-rx-benchmark-buddy)
        * [2.3.3 Local Median Neighborhood](#sec-3-rx-benchmark-local-median)
        * [2.3.4 Local Best Station](#sec-3-rx-benchmark-local-best)
    * [2.4 TX Benchmark](#sec-3-tx-benchmark)
        * [2.4.1 Hardware A/B: simultaneous transmit paths](#sec-3-tx-benchmark-simultaneous)
        * [2.4.2 Hardware A/B: sequential transmit paths](#sec-3-tx-benchmark-sequential)
        * [2.4.3 Reference Station / Buddy Test](#sec-3-tx-benchmark-buddy)
        * [2.4.4 Local Median Neighborhood](#sec-3-tx-benchmark-local-median)
        * [2.4.5 Local Best Station](#sec-3-tx-benchmark-local-best)
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
    * [7.1 Data source, observation units and time model](#sec-7-1)
    * [7.2 Identity, matching and row consolidation](#sec-7-2)
    * [7.3 Target-active conditioning and eligibility](#sec-7-3)
    * [7.4 Performance analysis target, classification and summary statistics](#sec-7-4)
    * [7.5 Power normalization, correction and Benchmark Delta SNR](#sec-7-5)
    * [7.6 Paired evidence, Decode Outcomes and missingness](#sec-7-6)
    * [7.7 Aggregation hierarchy and weighting](#sec-7-7)
    * [7.8 Geographic, temporal and selected-path summaries](#sec-7-8)
        * [7.8.1 Geographic summaries](#sec-7-8-1)
        * [7.8.2 Benchmark evidence coverage](#sec-7-8-2)
        * [7.8.3 Temporal summaries and UTC folding](#sec-7-8-3)
        * [7.8.4 Selected-path summaries](#sec-7-8-4)
        * [7.8.5 Descriptive spread and visualization transforms](#sec-7-8-5)
    * [7.9 Geography, solar classification and population filters](#sec-7-9)
    * [7.10 Dependence, uncertainty and validation scope](#sec-7-10)
* [8. Evidence-Matched Claims and Reproducibility](#sec-8)
    * [8.1 Claim classes and evidence-matched wording](#sec-8-1)
    * [8.2 Interpretation boundaries](#sec-8-2)
    * [8.3 Reporting and reproducibility checklist](#sec-8-3)
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

This part takes you from an operating question to an evidence-matched conclusion. Chapter 1 establishes the common experiment, selects RX or TX and Performance or Benchmark, and introduces the shared evidence path. Chapter 2 then follows that path within the exact analysis family and Reference design. Chapter 3 explains how to strengthen, report and preserve the result. Exact controls remain in Part II; exact calculations and scientific edge cases remain in Part III.

In this guide, the **experiment** is the physical on-air operation and station configuration. A **run** or **analysis** is WSPRadar's configured processing of the resulting observations. A **result** is the Performance or Benchmark evidence produced by that run.

---

<a id="sec-2"></a>

### 1. Choose and Prepare the Analysis

Start with the station question and the physical experiment. The interface choice follows from that question; it does not define it.

<a id="sec-2-1"></a>

#### 1.1 Build a strong experiment foundation

A useful WSPRadar result begins with one sentence stating what is being tested and what observation would count as support. Decide whether the run is exploratory—intended to find a possible pattern—or confirmatory—intended to test a pattern already identified.

Use one exact band and a UTC window in which the Target was operating. Enter callsigns exactly as uploaded and verify the Target QTH. Record the antenna, feedline, radio, tuner, gain or power settings, decoder, software version, schedule and any deliberate change. Keep every variable outside the question as stable as practical.

For TX, keep actual and reported power accurate and stable unless power is the tested variable. For RX, keep gain, filtering, audio routing, decoder settings and upload behavior stable unless one of them is under test. Keep clocks synchronized. In Benchmark, verify that the Reference was operating as intended: the Target-Active Gate establishes observable Target participation but does not prove Reference uptime.

Before a confirmatory repetition, fix the direction, band, Reference design, filters, thresholds, schedule and primary geographic or temporal scope. Treat alternative radii, time windows or scopes as separate sensitivity analyses rather than choosing only the version that looks most favorable.

<a id="sec-2-2"></a>

#### 1.2 Choose the analysis that matches the question

| Operating question | Analysis |
|---|---|
| Which independently confirmed signals does my receiver decode, where, when and how consistently? | **RX Performance** |
| Where and how consistently is my transmitter decoded by receivers independently shown to be active? | **TX Performance** |
| How do two local receive paths, two complete receiving stations, or my receiver and a local neighborhood Reference differ? | **RX Benchmark** |
| How do two local transmit paths, two complete transmitting stations, or my transmitter and a local neighborhood Reference differ? | **TX Benchmark** |

Choose **Performance** when the Target itself is the question and no Reference is required. Performance combines at-least-once reach, Decode Rate, successful Target SNR, geography, time and evidence support. It describes the complete Target station under the selected real-world conditions.

Choose **Benchmark** when the question is explicitly relative to a Reference. The Reference determines the meaning of the result:

<a id="sec-2-5"></a>

* **Hardware A/B** is the strongest design for a local component or path question, but it isolates that component only to the extent that the remaining paths are controlled.
* **Reference Station / Buddy Test** compares complete installed stations and their operating environments.

<a id="sec-2-6"></a>

* **Local Median Neighborhood** compares the Target with a changing typical local baseline inside the selected radius.

<a id="sec-2-7"></a>

* **Local Best Station** compares the Target with a changing strongest local peer on each qualifying path and cycle.

Use the narrowest Reference design that supports the intended claim. A complete-station or neighborhood benchmark cannot be turned into isolated antenna gain by later filtering or averaging.

<a id="sec-2-3-overview"></a>

#### 1.3 Follow the evidence path

Every completed result follows the same operator path:

> <strong class="defined-term">Map → Segment Inspector → Performance/Benchmark Evidence → Temporal Evidence → Station Insights → Selected Station Evidence → Drill-Down</strong>

<a id="sec-3-4"></a>
<a id="sec-3-5"></a>

**Map.** Locate the broad distance and direction pattern. Read sector color together with the station and opportunity, spot or pair support. A colored sector is a prompt to inspect, not the conclusion.

<a id="sec-3-6"></a>
<a id="sec-3-6a"></a>
<a id="sec-3-6b"></a>

**Segment Inspector.** Select the geographic scope relevant to the question. Every following evidence view uses that active scope, allowing a broad map pattern to be separated into distance- and direction-dependent behavior.

**Performance or Benchmark Evidence.** In Performance, combine reach, both Decode Rate weightings and successful Target SNR. In Benchmark, combine station-balanced and observation-level Delta SNR, Decode Outcomes and Joint Evidence Share. These quantities answer different questions and should not be collapsed into one score.

**Temporal Evidence.** Use the chronological view to see when behavior changed during the run and the UTC-hour view to see whether a time-of-day pattern recurred across dates. Read signal-level evidence together with its station, opportunity or pair support.

<a id="sec-3-7"></a>
<a id="sec-3-7a"></a>
<a id="sec-3-7b"></a>

**Station Insights.** Check whether the pattern is supported across many `callsign + locator` identities or is concentrated in a few paths. Read every station-level value together with its evidence counts.

**Selected Station Evidence.** Inspect one representative, surprising or high-impact path. This shows whether the segment summary also describes that path, whether its behavior is intermittent, and whether its time pattern differs from the wider scope.

<a id="sec-3-8"></a>

**Drill-Down.** Verify the retained opportunities, same-cycle pairs or scheduled pairs behind a result. Use it to check identities, locator changes, timing, one-sided evidence and isolated outliers.

The rest of Part I applies this same path to each analysis question without inventorying every title, axis or layout detail.

---

<a id="sec-3"></a>

### 2. Run and Interpret Your Analysis

Use the section matching the selected Direction and result type. Exact control labels, defaults and ranges are in [Chapter 4](#sec-5); exact eligibility, matching, weighting and aggregation are in [Chapter 7](#sec-7).

<a id="sec-3-1"></a>
<a id="sec-3-2"></a>
<a id="sec-3-rx-performance"></a>

#### 2.1 RX Performance

**Question answered.** Which remote transmitter-cycles, independently confirmed by another eligible receiver, did the Target receiver also decode; how consistently did it do so; what successful SNR did it observe; and where and when did that behavior occur?

**Minimum valid setup.** Use the exact Target reporting callsign and QTH, one band and a window with observable Target receiver activity. Keep the receive chain stable. Performance does not introduce a Reference and does not isolate one component of the receive system.

**What WSPRadar evaluates.** A confirmed RX opportunity exists when another eligible receiver decoded the same remote transmitter in the same Target-active cycle. `Heard by Target` means the Target also decoded it; `Heard by others only` means the independent receiver did but the Target did not. Evidence without independent confirmation remains auditable but does not enter Decode Rate. The exact classification is in [Section 7.4](#sec-7-4).

**Read the evidence path.** On the **Map**, sector color shows the Station-balanced Decode Rate of qualifying remote transmitters in each distance-and-direction segment. Station markers and the footer distinguish paths heard by the Target at least once from paths heard only elsewhere. Use this first to locate broad RX footprint and directional structure, not to judge receiver sensitivity from color alone.

In **Segment Inspector**, first compare station breadth with confirmed-opportunity depth. Many opportunities from only a few transmitters are deep but narrow evidence; agreement across many transmitters is broader. Then read the three Performance views together:

* **At-least-once reach** asks which qualifying transmitters were heard at least once during the window. It measures breadth and normally increases with a longer run.
* **Decode Rate** asks how consistently the Target decoded confirmed opportunities. The Station-balanced rate gives each transmitter one vote; the Opportunity-level rate gives each confirmed cycle one vote. A difference between them shows that high-volume transmitters behave differently from the wider station population.
* **Successful Target SNR** describes only successful decodes. It helps show whether the successful signals themselves differ with distance, but misses have no Target SNR and cannot appear there.

In **Temporal Evidence**, successful-SNR deviation compares each transmitter path with its own usual successful level during the run. Values above `0 dB` mean successful decodes were stronger than usual for their respective paths; values below `0 dB` mean weaker. The accompanying station and opportunity evidence shows whether a signal-level change coincided with changed Decode Rate and whether the pattern was broadly supported. The chronological view identifies changes during the run; the folded UTC-hour view identifies recurring daily behavior.

In **Station Insights**, read each transmitter's Decode Rate together with `Heard by Target` and `Heard by others only` counts. Select a typical path, an outlier and any path contributing unusually large evidence. **Selected Station Evidence** then shows the actual successful SNR and opportunity history of one transmitter path rather than the station-relative summary across the segment. **Drill-Down** verifies the contributing cycles and distinguishes confirmed opportunities from Target evidence that lacks independent confirmation.

**Common interpretation patterns.** Broad reach with high Decode Rate means many paths opened and were decoded consistently. Broad reach with lower Decode Rate means many paths opened at least once but were intermittent. Limited reach with high Decode Rate means fewer qualifying paths opened, but those that did were comparatively consistent. If successful SNR remains steady or rises while Decode Rate falls, weaker signals may have disappeared below the decoder threshold, leaving only stronger successful decodes. A pattern confined to one azimuth, distance range or UTC period can be operationally useful, but it describes the installed receiver under those paths and conditions rather than a context-free sensitivity number.

**Boundary and confirmation.** RX Performance combines antenna, feedline, receiver, gain, filtering, decoder, local noise, interference and propagation. It does not directly measure receiver sensitivity, antenna gain, absolute noise or propagation mode. Repeat a suspected pattern in another suitable window. When the intended conclusion is about one hardware change, use a controlled RX Benchmark or a crossover rather than relying only on separated before-and-after Performance runs.

<p class="evidence-conclusion-label"><strong>Evidence-matched conclusion.</strong></p>

<blockquote class="evidence-conclusion"><p>For this Target receiver, band, UTC window and selected transmitter population, RX Performance describes at-least-once reach, Decode Rate within independently confirmed transmitter-cycles, successful-decode SNR and the geographic and temporal scope in which those observations appeared. State the weighting used, the station and opportunity support, and whether the pattern was broad, intermittent, directional, distance-dependent or recurring.</p></blockquote>

<a id="sec-3-tx-performance"></a>

#### 2.2 TX Performance

**Question answered.** Which remote receivers independently shown to be active decoded the Target transmitter; how consistently did they do so; what successful SNR did they report; and where and when did that behavior occur?

**Minimum valid setup.** Use the exact Target callsign and QTH, one band and a window in which the Target transmitter was operating. Keep the RF path, schedule and actual power stable, and report power accurately. Performance evaluates the complete transmitted station rather than one isolated component.

**What WSPRadar evaluates.** A confirmed TX opportunity exists when the remote receiver was active in a Target transmit cycle, demonstrated by another qualifying same-band decode. `Target heard` means that receiver also decoded the Target; `Other signals heard only` means it decoded qualifying same-band activity but not the Target. A Target report without independent receiver-activity confirmation remains auditable but does not enter Decode Rate. The exact denominator is in [Section 7.4](#sec-7-4).

**Read the evidence path.** On the **Map**, sector color shows the Station-balanced Decode Rate of qualifying active receivers in each distance-and-direction segment. Markers and footer counts distinguish receivers that heard the Target at least once from receivers that heard only other qualifying signals. Use the map to locate practical transmitted footprint and directional structure.

In **Segment Inspector**, compare receiver breadth with confirmed-opportunity depth, then read the three Performance views together:

* **At-least-once reach** asks which qualifying active receivers heard the Target at least once during the window.
* **Decode Rate** asks how consistently the Target was reported within confirmed receiver opportunities. The Station-balanced and Opportunity-level rates reveal whether frequently reporting receivers behave differently from the wider receiver population.
* **Successful Target SNR** shows normalized SNR for successful Target reports. It is conditional on a decode and depends on the accuracy of reported transmit power.

In **Temporal Evidence**, successful-SNR deviation shows when successful reports were stronger or weaker than each receiver path's own usual successful level. The accompanying station and opportunity stacks show whether a change in successful SNR was accompanied by a change in practical detectability and how much support each time bin contains. Chronological change and recurring UTC-hour behavior should be distinguished.

In **Station Insights**, read each receiver's rate with its `Target heard` and `Other signals heard only` counts. **Selected Station Evidence** exposes one receiver path's actual successful SNR and opportunity history, which helps determine whether the segment summary reflects many receivers or masks a path-specific effect. **Drill-Down** verifies Target reports, independent receiver activity and any Target reports that lack independent receiver-activity confirmation.

**Common interpretation patterns.** Broad reach and high Decode Rate indicate that many qualifying active receivers heard the Target consistently. Broad reach and lower Decode Rate indicate a large but intermittent footprint. A persistent advantage in one azimuth or distance range can be consistent with installed antenna and terrain behavior; a short isolated improvement can instead reflect propagation or receiver availability. Stable successful SNR with falling Decode Rate can indicate that only stronger surviving reports remain. Differences between station-balanced and Opportunity-level rates reveal whether a few high-volume receivers are driving the pooled view.

**Boundary and confirmation.** TX Performance combines transmitter, actual power, feedline, matching, antenna, terrain, remote receiver systems, noise and propagation. Reported-power normalization cannot correct an incorrect power report or an unmeasured feedline loss. The result does not directly measure EIRP, efficiency, antenna gain or take-off angle. Repeat the pattern across another suitable window; use TX Benchmark when the question is specifically whether one transmit path differs from another.

<p class="evidence-conclusion-label"><strong>Evidence-matched conclusion.</strong></p>

<blockquote class="evidence-conclusion"><p>For this Target transmitter, band, UTC window and selected active-receiver population, TX Performance describes at-least-once reach, Decode Rate within independently confirmed receiver-cycles, successful reported SNR and the geographic and temporal scope in which those observations appeared. State the weighting, receiver and opportunity support, reported-power basis and whether the pattern was broad, intermittent, directional, distance-dependent or recurring.</p></blockquote>

<a id="sec-3-3"></a>
<a id="sec-3-rx-benchmark"></a>

#### 2.3 RX Benchmark

**Question answered.** How did the Target receive side differ from the selected Reference while both observed the same remote transmitter identities in the same WSPR cycles?

**Shared RX Benchmark evidence.** Paired Delta SNR is formed only where Target and Reference produced comparable same-transmitter, same-cycle evidence. Positive Delta SNR favors the Target; negative favors the Reference. Decode Outcomes preserve Joint, Only Target, Only Reference and asynchronous evidence around that paired subset. Joint Evidence Share describes how much retained evidence was pairable; it is not a win rate. Reference uptime must be understood independently, and the Target-Active Gate makes one-sided categories intentionally asymmetric.

**Read the evidence path.** On the **Map**, sector color summarizes the station-balanced median Delta SNR of the remote transmitters in each distance-and-direction segment. Marker categories show whether each transmitter identity contributed Joint or one-sided evidence. Read color with the station and spot counts: a strong-looking sector supported by only a few transmitters is narrower evidence than a similar result repeated across many paths.

In **Segment Inspector**, Decode Outcomes show two complementary compositions: station breadth and observation volume. Station Medians give each remote transmitter one Delta-SNR value and therefore equal weight; the Joint-Spot distribution shows every paired observation and can be influenced by high-volume transmitters. Agreement between them supports a broad shift, while disagreement shows that observation volume and station breadth tell different stories.

**Temporal Evidence** shows whether paired Delta SNR changed during the run or recurred by UTC hour. Read it with Benchmark Evidence Coverage: a Delta-SNR pattern supported by broad Joint coverage is different from a pattern visible only in a thin paired subset. One-sided evidence can reveal practical near-threshold differences that paired Delta SNR alone cannot describe, but it does not supply a missing-side SNR.

In **Station Insights**, inspect each transmitter's Joint and one-sided counts together with its median Delta SNR. **Selected Station Evidence** shows one transmitter path's paired Delta SNR and evidence coverage over time, helping distinguish a representative path from an outlier or intermittent path. **Drill-Down** verifies that Target and Reference rows match the intended transmitter, cycle, callsign and locator identities and that the configured correction has the expected sign.

**Common interpretation patterns.** A station-median distribution mostly on one side of zero, broad Joint coverage and recurrence across time or adjacent segments support a consistent complete-path difference. A pooled Joint-Spot shift without a similar station-median shift can be driven by a few prolific transmitters. A clear paired median alongside many Only Target or Only Reference outcomes means that the paired strength difference describes only part of the practical decode evidence. A difference confined to one direction or UTC period can be real and useful while remaining path- or condition-dependent.

**Boundary and confirmation.** Paired analysis is conditional on both sides producing comparable evidence and therefore cannot describe all missed signals. Same-cycle matching controls the remote transmitter and timing, but it does not remove local receiver-chain, antenna, noise or QTH differences. Strengthen the result with enough Joint stations, independent Reference-uptime knowledge, repetition and the design-specific control described below.

<a id="sec-2-3"></a>
<a id="sec-3-rx-benchmark-hardware"></a>

##### 2.3.1 Hardware A/B: simultaneous receive paths

Use this design for two local antennas, feedlines, filters, preamplifiers, receivers or complete receive chains operated simultaneously at the same physical test QTH. Target and Reference need distinct exact reporting callsigns and the same Target grid-4. Components intended to be common must be physically common; shared grid-4 matching does not prove co-location or path equality.

This is the strongest RX design for attributing a difference to a local path. The result still compares the complete documented receive paths unless receiver, audio, gain, decoder and routing differences have been characterized. A broad recurring Delta-SNR shift plus compatible one-sided evidence supports one path outperforming the other under the tested conditions. A common-input calibration, splitter-output swap or hardware crossover is the most useful confirmation because it can separate the tested component from a persistent chain offset. [Appendix C](#sec-c) describes Reference SNR calibration.

<blockquote class="evidence-conclusion"><p>Under the documented simultaneous RX Hardware A/B setup, paired Delta SNR and Decode Outcomes described the observed difference between the Target and Reference receive paths for the shared transmitters, cycles and selected geographic scope.</p></blockquote>

<a id="sec-3-rx-benchmark-buddy"></a>

##### 2.3.2 Reference Station / Buddy Test

Use a known external receiver whose QTH, identity, equipment, operating schedule and local environment are understood. RX pairs share the same remote transmitter and cycle, but the two receiving stations remain at different QTHs with different antennas, terrain, hardware and noise.

Interpret this as a benchmark of complete installed receiving stations. It can show where one station was relatively stronger, how that relationship changed with direction, distance or time, and whether one-sided reach differed. It cannot isolate receiver sensitivity, antenna gain or local noise as the cause. Repetition with the same well-understood Buddy and stable operating conditions is the most useful confirmation.

<blockquote class="evidence-conclusion"><p>For the shared transmitter paths and cycles in this run, paired Delta SNR and Decode Outcomes described how the two complete receiving stations compared under their respective environments.</p></blockquote>

<a id="sec-3-rx-benchmark-local-median"></a>

##### 2.3.3 Local Median Neighborhood

The Reference is the cycle- and path-specific median of one contribution from each active local receiver identity inside the selected radius. Membership can change from cycle to cycle, so the result is a contextual local baseline rather than a fixed station comparison.

Inspect the contributing local identities, Joint Evidence Share and radius sensitivity. A shift can reflect the Target, a changed neighborhood composition or both. Choose the primary radius from local geography and station density before interpreting the result; use other defensible radii as sensitivity analyses.

<blockquote class="evidence-conclusion"><p>Relative to the active median receiver neighborhood inside the selected radius, the Target showed the reported paired Delta SNR and Decode Outcomes for the observed transmitter paths and cycles.</p></blockquote>

<a id="sec-3-rx-benchmark-local-best"></a>

##### 2.3.4 Local Best Station

The Reference is the strongest qualifying local receiver evidence available for each remote transmitter path and cycle. The winning local identity can change continuously, creating a demanding best-peer envelope rather than a local average or one permanent competitor.

Inspect which local station supplies the Reference and whether the observed gap is broad or concentrated in a small set of winners. Radius and pool membership remain part of the result. Report it as the Target's gap to the changing strongest local receiver, not as a ranking against one fixed station.

<blockquote class="evidence-conclusion"><p>Relative to the strongest qualifying local receiver selected for each path and cycle inside the stated radius, the Target showed the reported paired Delta SNR and Decode Outcomes.</p></blockquote>

<a id="sec-3-tx-benchmark"></a>

#### 2.4 TX Benchmark

**Question answered.** How did the Target transmitter or scheduled path differ from the selected Reference at shared remote receivers?

**Shared TX Benchmark evidence.** Same-cycle TX Benchmark compares Target and Reference at the same remote receiver in the same WSPR cycle. Sequential Hardware A/B instead uses deterministic scheduled pairs at the same receiver. Successful TX SNR is normalized to reported power before Delta SNR is formed; the result therefore depends directly on accurate power reporting. Decode Outcomes preserve Joint and one-sided evidence, but an exclusive observation has no missing-side SNR and is not power-normalized.

**Read the evidence path.** On the **Map**, sector color summarizes station-balanced median Delta SNR across remote receivers. Marker and footer categories show Joint and one-sided receiver evidence. Read each sector with receiver breadth and spot or scheduled-pair depth.

In **Segment Inspector**, compare the station-level Decode Outcomes with the observation- or pair-level composition. Station Medians give each remote receiver one equal vote, while Joint-Spot or Scheduled-Pair Delta SNR shows the full paired observation distribution. A shift shared across many receivers is different from one dominated by a few high-volume receivers.

**Temporal Evidence** shows whether Delta SNR changed through the run or recurred by UTC hour. Benchmark Evidence Coverage shows whether paired evidence remained broad through those times. For sequential TX, inspect whether the result is tied to one schedule phase or switching period; for simultaneous TX, inspect whether it is tied to one receiver, audio-frequency assignment or short interval.

In **Station Insights**, read each receiver's median Delta SNR with its Joint and one-sided counts. **Selected Station Evidence** reveals the paired result and evidence coverage at one receiver path. **Drill-Down** verifies receiver identity, reported powers, same-cycle pairing or scheduled-pair assignment, and correction sign.

**Common interpretation patterns.** A consistent station-median shift across many receivers, directions and times supports a broad complete-transmit-path difference. A shift limited to one azimuth or distance range can indicate useful installed directional behavior without becoming a context-free gain value. Strong paired Delta SNR with substantial one-sided evidence means the strength difference and practical near-threshold reach must both be reported. A raw-pair median that differs from the station-median view indicates that high-volume receivers weight the observation-level evidence differently.

**Boundary and confirmation.** TX Benchmark remains conditional on pairable evidence and accurate reported power. Simultaneous designs retain transmitter-chain, frequency-response, isolation and coupling differences. Sequential designs remain time-separated. Same-cycle one-sided evidence is also affected by the Target-Active Gate. Strengthen the result with broad receiver support, accurate power measurement, repeated runs and the method-specific controls below.

<a id="sec-2-4"></a>
<a id="sec-2-4-simultaneous"></a>
<a id="sec-3-tx-benchmark-simultaneous"></a>

##### 2.4.1 Hardware A/B: simultaneous transmit paths

Use two distinguishable transmitter chains and callsigns at the same physical test QTH, deliberately synchronized in the same WSPR cycles and placed on clear, non-overlapping frequencies within the WSPR passband. Measure or otherwise establish actual power at the comparison point relevant to the question, and ensure adequate isolation between the active transmitters and antennas.

Same-receiver, same-cycle Delta SNR removes the sequential time gap and is the strongest TX design when the two transmitter chains can be controlled. It still compares the complete documented transmit paths. Frequency-selective QRM, chain response, coupling and power error can remain. Swap audio-frequency assignments and, where practical, cross the tested antennas or components between chains. [Appendix A](#sec-a) covers parallel WSJT-X setup.

<blockquote class="evidence-conclusion"><p>Under the documented simultaneous two-transmitter Hardware A/B setup, same-receiver, same-cycle Delta SNR and Decode Outcomes described the observed difference between the Target and Reference transmit paths for the selected receivers and geographic scope.</p></blockquote>

<a id="sec-2-4-sequential"></a>
<a id="sec-2-4-why"></a>
<a id="sec-3-tx-benchmark-sequential"></a>

##### 2.4.2 Hardware A/B: sequential transmit paths

Use a deterministic schedule that assigns complete WSPR transmissions to Target and Reference phases. One transmitter switched between two RF paths is normally the strongest arrangement because callsign, frequency reference and transmitter remain common. Enter each path's actual recurrence and UTC phase, verify the physical schedule-to-path mapping without RF, and report actual power. Device-specific scheduling and switching guidance is in [Appendix B](#sec-b).

WSPRadar forms one-to-one Scheduled A/B Pairs automatically. Pair Delta remains sequential: short balanced alternation reduces but does not eliminate propagation, interference, schedule-position and switching effects. Inspect incomplete pairs and chronological behavior with the paired median. Reverse the Target and Reference schedule assignments in a confirmatory run; persistence of the physical-path advantage after the role reversal is substantially more persuasive than repetition with the same phase assignment.

<blockquote class="evidence-conclusion"><p>Under the documented deterministic schedule, Scheduled-Pair Delta SNR and one-sided pair outcomes described the observed difference between the switched Target and Reference paths for the selected receivers, times and geographic scope.</p></blockquote>

<a id="sec-3-tx-benchmark-buddy"></a>

##### 2.4.3 Reference Station / Buddy Test

Use a known external transmitter whose QTH, identity, actual and reported power, equipment and operating schedule are understood. TX pairs share the same remote receiver and cycle, but Target and Reference remain complete stations at different QTHs with different antennas, feedlines, terrain and paths.

Interpret the result as a benchmark of complete installed transmitting stations. Same-receiver pairing controls the receiving endpoint, not the two transmit sites or radio paths. Power-reporting accuracy is especially important. Repeat with the same well-understood Buddy and stable configurations rather than treating the Buddy as an absolute calibrated standard.

<blockquote class="evidence-conclusion"><p>For the shared receiving stations and cycles in this run, paired Delta SNR and Decode Outcomes described how the two complete transmitting stations compared under their respective operating environments.</p></blockquote>

<a id="sec-3-tx-benchmark-local-median"></a>

##### 2.4.4 Local Median Neighborhood

The Reference is the cycle- and receiver-path median of one contribution from each active local transmitter identity inside the selected radius. It is a changing local baseline, not one fixed station, and it depends on the active membership and accuracy of their reported powers.

Inspect the local contributors, Joint Evidence Share and radius sensitivity. Report whether the Target tends to sit above, near or below the active local baseline for particular receivers, directions or times. A changed result can reflect the Target, the local pool or both.

<blockquote class="evidence-conclusion"><p>Relative to the active median transmitter neighborhood inside the selected radius, the Target showed the reported paired Delta SNR and Decode Outcomes for the observed receiver paths and cycles.</p></blockquote>

<a id="sec-3-tx-benchmark-local-best"></a>

##### 2.4.5 Local Best Station

The Reference is the strongest qualifying local transmitter evidence available at each remote receiver and cycle after the applicable correction. The winning local identity can change continuously, producing a best-peer envelope rather than a local average or permanent competitor.

Inspect which station supplies the Reference, its reported power and whether the Target gap persists across receivers, distance, direction and time. Report the result as comparison with a changing strongest local transmitter inside the stated radius.

<blockquote class="evidence-conclusion"><p>Relative to the strongest qualifying local transmitter selected for each receiver path and cycle inside the stated radius, the Target showed the reported paired Delta SNR and Decode Outcomes.</p></blockquote>

<a id="sec-3-9"></a>

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

The observed time, distance, direction, Decode Rate, successful-SNR or Delta-SNR pattern is the evidence. An explanation such as antenna directivity, a local-noise change, propagation mode, overload or an intermittent component is an interpretation. Match the wording to the observation first, then test the explanation through a controlled change, crossover, independent measurement or repetition.

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

A minimum operator statement identifies the Target and, for Benchmark where applicable, the fixed Reference or local benchmark definition. It also identifies the TX or RX direction, band, UTC window, geographic scope, result type, displayed value and supporting station/evidence count.

A full technical report also states:

* the applicable weighting levels: Station-balanced and Opportunity-level Decode Rate for Performance, or station-level and observation-level Delta SNR for Benchmark;
* qualifying-station and confirmed-opportunity counts for Performance, or joint-station and joint-spot/pair counts for Benchmark;
* Decode Outcomes for Benchmark;
* experiment conditions and any Reference correction;
* filters and evidence thresholds;
* whether the pattern repeated across time, stations or runs;
* any alternative radius or scope used as a sensitivity analysis.

**Performance wording**

> For this Target, band, UTC window and selected peer population, the displayed Decode Rate describes the fraction of independently confirmed opportunities in which the Target also produced qualifying evidence. State whether the reported value is the Station-balanced Decode Rate or the Opportunity-level Decode Rate. Qualifying stations, confirmed opportunities, geographic scope and temporal views describe the breadth, depth and recurrence supporting that result.

A complete Performance statement can additionally say whether at-least-once reach was broad or limited, whether participation was consistent or intermittent, where distance or directional patterns appeared, whether a UTC-hour pattern recurred and how successful Target SNR behaved. Describe these as observed WSPR behavior of the complete station under the selected conditions, not as isolated gain, sensitivity or efficiency.

**Benchmark wording**

> For this Target, Reference, band, UTC window and selected segment, station-balanced Delta SNR favored the Target/Reference by the displayed amount. The observation-level Delta SNR, joint station and spot/pair counts, Joint Evidence Share and Decode Outcomes describe the supporting paired and one-sided evidence.

For a controlled Hardware A/B result, name the complete paths compared and any crossover or calibration. For a Reference Station / Buddy Test, state that complete installed stations and their environments were benchmarked. For a Local Neighborhood Benchmark, state the radius, method and changing Reference definition.

Match the design name to the quantity being described:

* A **Hardware A/B Test** compares the documented local paths.
* A **Buddy Test** compares complete installed stations and their environments.
* **Local Median Neighborhood** compares the Target with the active median-neighborhood definition inside the selected radius.
* **Local Best Station** compares the Target with a changing best-peer envelope.
* A directional result describes the observed WSPR paths and participating stations rather than an absolute radiation pattern.
* Benchmark map colors use a run-scaled, symmetric dB color bar: blue favors the Reference, red favors the Target and `0 dB` is equality. Use the numerical color-bar values when comparing maps from different runs.

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

Use this part as an operating reference while setting up, repeating or diagnosing an analysis. It documents the exact controls, defaults, saved behavior and scientific consequences that affect the operator.

<a id="sec-5"></a>

### 4. Controls and Configuration

WSPRadar distinguishes controls that change the retained scientific evidence from controls that only change how completed evidence is inspected.

| Control class | Effect | Saved? | Rerun required? |
|---|---|---|---|
| **Scientific controls** | Change identity, band, time, Reference design, eligibility, normalization, filters, thresholds or geographic population. | When applicable | Yes; the previous result is cleared |
| **View controls** | Change the active inspection scope, selected station, evidence visibility or display aggregation without reclassifying retained evidence. | Supported durable choices only | No |
| **Temporary interface choices** | Change only the current on-screen arrangement, temporary table filters, documentation visibility or a prepared download. | No | No |

Versioned configurations store the applicable scientific settings and supported durable view choices. Exact calculations are defined in [Chapter 7](#sec-7); the supported machine-readable configuration and export names are documented in [Section 8.4](#sec-8-4).

<a id="sec-5-1"></a>

#### 4.1 Workflow controls

| Control | What it does | Important behavior |
|---|---|---|
| **`Input view`** | Switches between `Guided` and `Classic`. | Both expose the same scientific configuration. The chosen editor is not saved. |
| **`Load Demo`** | Loads a maintained historical profile. | Loading does not start an analysis. An unchanged profile remains a demo; editing a scientific control makes it an ordinary analysis. |
| **`Load Config`** | Loads a versioned JSON `.config`. | Invalid identities, dates, choices, ranges, duplicate fields and unsupported schema versions are rejected rather than guessed. |
| **`Save Config`** | Saves the applicable scientific inputs and supported durable view settings. | The file stores absolute UTC boundaries but not result rows, external experiment notes or transient table filters. In Classic, saving remains unavailable until the Question and, for a Benchmark, the Benchmark design are complete. |
| **`Run RX Analysis` / `Run TX Analysis`** | Runs the selected Performance or Benchmark result. | In Classic, running remains unavailable until the Question and, for a Benchmark, the Benchmark design are complete. Changing a scientific control after a run clears the result and requires a new run. |
| **`Prepare All Results for Download`** | Builds the current export package. | Uses the completed evidence and current inspector selections. |
| **`Load full documentation` / `Hide full documentation`** | Shows or hides the complete web manual. | Presentation state only. |
| **`Prepare PDF`** | Builds the selected-language manual as PDF. | The full web manual does not need to be open first. |

**Configuration compatibility.** Saved files preserve the inputs and durable view choices applicable to the selected analysis. Invalid or unsupported files are rejected rather than silently reinterpreted. The current machine-readable configuration contract is documented in [Section 8.4](#sec-8-4). Loading or saving a configuration does not create an additional result; only the selected Performance or Benchmark analysis is run.

<a id="sec-5-2"></a>

#### 4.2 Question, Target and measurement-window controls

Classic presents the scientific setup in a question-led order. The first panel, **`Question`**, requires one of four complete analysis choices: `RX Performance`, `TX Performance`, `RX Benchmark` or `TX Benchmark`. This single choice sets both the RX/TX direction and whether the run produces stand-alone Performance evidence or a Target-versus-Reference Benchmark. The second panel, **`Target and measurement window`**, then collects the existing Target identity, QTH, band and absolute UTC interval.

| UI label | Default | What it controls |
|---|---|---|
| **Question** | none; required | One of `RX Performance`, `TX Performance`, `RX Benchmark` or `TX Benchmark`; sets direction and result type together. |
| **Target callsign (receiver under test)** / **Target callsign (transmitter under test)** | blank | Exact archive reporting identity. Standard callsigns, valid `/` variants, letter-only reporting identifiers and one terminal `-` suffix are accepted. |
| **Target QTH (4 or 6 characters)** | blank | Target grid-4 matching, map center, geometry and local-radius origin. |
| **Operating Band** | `20m` | Exactly one of `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` or `23cm`. |
| **UTC measurement window** | fixed 24-hour window ending at the current 15-minute UTC boundary | The absolute evidence interval used by the run. |
| **Start Date/Time (UTC)** and **End Date/Time (UTC)** | the effective default window | Dates begin in 2008; one run is limited to 31 elapsed days. Edited values are rounded down to effective 15-minute boundaries and shown back in the controls. |

Use the callsign or reporting identifier exactly as uploaded. `KFS`, `KFS/SE`, `DL1MKS`, `DL1MKS/P`, `DL1MKS/1`, `DL1MKS/QRP` and `DL1MKS-1` are distinct identities; WSPRadar does not apply hidden prefix or suffix matching.

A four-character Maidenhead locator identifies a broad grid square; six characters identify a smaller subsquare. Performance and Benchmark select Target archive rows from the exact callsign plus the first four characters of Target QTH. The full configured QTH still anchors map, distance, azimuth, solar and local-neighborhood calculations.

<a id="sec-5-3"></a>

#### 4.3 Benchmark-design controls

For `RX Benchmark` and `TX Benchmark`, Classic displays a third panel named **`Benchmark design`** and requires one of:

- `Hardware A/B`
- `Known Reference Station`
- `Local Neighborhood`

Classic omits the **`Benchmark design`** panel entirely for `RX Performance` and `TX Performance`, because Performance has no Reference. `Run` and `Save Config` remain unavailable while the Question is incomplete or while a Benchmark question has no complete Benchmark design. Performance and Benchmark are mutually exclusive result types: one run produces only the selected result. The supported machine-readable configuration, URL and export names are documented in [Section 8.4](#sec-8-4).

| UI label | Default / range | Applies to | Scientific effect |
|---|---|---|---|
| **Is there an established Target–Reference offset?** | `No established offset — use 0.0 dB` | Guided Hardware A/B and Known Reference Station | Distinguishes no established correction, use of one established correction, and a deliberate offset-establishment run. |
| **Reference-side SNR correction (dB)** | blank = `0.0`; `-99.9` to `+99.9 dB` | Benchmark | Added to Reference SNR before Target-minus-Reference Delta SNR is calculated. Enter decimal points, for example `1.2`. |
| **Reference callsign** | blank | Hardware A/B and Reference Station | Exact Reference reporting identity. |
| **Reference Locator** | independent grid-4 for Reference Station; derived Target grid-4 for Hardware A/B | Benchmark | Controls Reference archive matching. |
| **Local Benchmark Method** | `Local Median Neighborhood` | Local Neighborhood Benchmark | Selects the median local Reference or the strict changing Local Best Station. |
| **Neighborhood Radius (km)** | `100`; 10–250 km in 10 km steps | Local Neighborhood Benchmark | Defines the local Reference pool around Target QTH. |
| **TX A/B Method** | `Simultaneous TX` | TX Hardware A/B | Selects same-cycle two-transmitter matching or deterministic sequential pairing. |
| **Repeat Interval** | `10 min`; `4, 6, 10, 12, 20, 30, 60 min` | Sequential TX A/B | Actual recurrence of each physical path. |
| **Target Start / Reference Start** | `00 UTC` / `02 UTC`; distinct even phases below Repeat Interval | Sequential TX A/B | Assigns transmissions to Target and Reference schedule phases. |

For TX Hardware A/B, `Repeat Interval` is each path's actual recurrence, not necessarily a transmitter's displayed `Frame` value. Compare the one-hour preview with the observed on-air starts and physical switch mapping. Device examples are in [Appendix B](#sec-b); pair construction is in [Sections 7.1](#sec-7-1) and [7.7](#sec-7-7) <a href="#ref-12">[Ref-12]</a>.

Switching the Question or Benchmark design hides controls that do not apply. Saved configurations contain only the inputs applicable to the selected analysis. Values whose scientific meaning changes under the new design are cleared rather than reinterpreted.

##### Reference-side SNR correction sign

A positive correction increases corrected Reference SNR and therefore reduces Target-minus-Reference Delta SNR. Enter a measured `target - reference` calibration offset with the same sign. For example, a common-input calibration of `+1.6 dB` is entered as `+1.6 dB`. [Section 7.5](#sec-7-5) defines the equations.

The correction applies to the Reference receive/transmit path or schedule in Hardware A/B, the known Reference Station, the selected Local Best Station value, or each local contribution before the Local Median Neighborhood is formed.

| Guided choice | Meaning | Required value |
|---|---|---|
| **No established offset** | No defensible correction has been established. | `0.0 dB` |
| **Use an established correction** | Apply a documented signed additive offset valid for this setup. | Enter the established value |
| **Set up an offset-establishment run** | Collect evidence from which an offset can be derived; WSPRadar does not choose or calculate the offset automatically. | `0.0 dB` during the establishment run |

A constant correction cannot repair clipping, unstable AGC, intermittent routing, frequency-dependent response or incorrect power reporting. Hardware A/B calibration should use a common input or calibrated reference plane. A geographically separated Reference Station can support only a repeatable baseline for that particular pair, band and setup—not an absolute calibration. [Appendix C](#sec-c) gives the practical procedure.

<a id="sec-5-4"></a>

#### 4.4 Filters and evidence thresholds

Choose filters and thresholds from the intended population and evidence floor before a confirmatory run. Changing them after inspecting the result creates a different analysis and should be retained separately.

| Control | Default | Applies to | Effect and use |
|---|---|---|---|
| **Exclude Special Callsigns Q, 0, 1** | Performance on; Benchmark off | all results | Excludes peer identities beginning with `Q`, `0` or `1`. Retain beacon/telemetry-like identities when they are part of the question; exclude them when the intended population is ordinary amateur activity. |
| **Exclude Moving Stations** | Performance on; Benchmark off | mapped peers | Excludes callsigns reporting more than one grid-4 in the otherwise eligible global population. Use Drill-Down to distinguish movement from bad locator data. |
| **Solar state at Target QTH** | `All 24h` | all results | Keeps `Daylight (Elev > +6°)`, `Nighttime (Elev < -6°)`, `Greyline (-6° to +6°)` or all cycles according to Target-QTH solar elevation. |
| **Maximum peer distance from Target (km)** | `22000`; choices `2500`, `5000`, `10000`, `15000`, `20000`, `22000` | all results | Removes peers at or beyond the selected distance from analysis, processed artifacts and exports. Target-Active gating may still use out-of-scope evidence solely to establish Target operation. |
| **Minimum joint evidence per station** | `1`; range 1–50 | simultaneous Benchmark | Requires repeated Joint peer-cycles before a station contributes paired Delta SNR; the same numeric floor also applies to exclusive categories. |
| **Minimum scheduled pairs per station** | `1`; range 1–50 | sequential TX A/B | Requires repeated complete scheduled pairs before a station contributes Pair Delta; one-sided pair categories use the same numeric floor. |
| **Minimum confirmed opportunities per station** | `5`; range 1–100 | Performance | Requires enough Target-plus-counter opportunities before a peer contributes. Low values increase coverage but make rates coarse and weakly supported. |
| **Minimum qualifying stations per map segment** | `1`; range 1–10 | all maps | Requires broader identity support before a segment is drawn. |

The two exclusion defaults apply only to untouched interactive setups. A Performance setup starts with both exclusions on; a Benchmark setup starts with both off. After the operator changes either exclusion manually, that explicit value persists across Question changes rather than being replaced by a result-type default. Loaded configurations, demos and analysis URLs likewise retain their explicitly saved choices.

`Maximum peer distance from Target (km)` limits the analysed population after the archive rows have been retrieved, so reducing it does not avoid the archive row limit. A smaller Local Neighborhood radius and `Exclude Special Callsigns Q, 0, 1` can reduce the population retrieved for some analyses; [Section 5.6](#sec-6-6) covers oversized requests.

<a id="sec-5-5"></a>

#### 4.5 Map, inspector and export controls

| Control | What it changes | Saved? | Reruns analysis? |
|---|---|---|---|
| Segment distance and direction | Active geographic inspection scope | Separately for Performance and Benchmark | No |
| `Heard only by other stations.` / `Only other signals heard.` | Visibility of Performance peers with only counter-evidence | Yes | No |
| `Include Unpaired Evidence` | Visibility of Benchmark identities represented only by exclusive or asynchronous evidence | Yes | No |
| Selected station row | Selected Station Evidence and selected Drill-Down identity | One exact `callsign + locator` per result type | No |
| Segment time aggregation | Chronological Segment Inspector temporal view | Yes | No |
| Selected-station time aggregation | Chronological selected-path view | Yes | No |
| `Prepare All Results for Download` | Export package and current inspection selections | n/a | No |

Chronological aggregation never changes opportunity classification, Benchmark pairing or the fixed one-hour UTC-folded profiles. Empty Performance time or distance bins remain missing evidence rather than synthetic zero-rate observations. Export contents are defined in [Section 8.4](#sec-8-4).

<a id="sec-6"></a>

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
7. **Design mechanics:** clock synchronization, TX schedule-to-path mapping, switching, signal routing, actual and reported power.

Only after these checks should you change evidence thresholds, exclusions, solar state or geographic scope.

<a id="sec-6-2"></a>

#### 5.2 Diagnose by symptom

| Symptom | Next checks |
|---|---|
| **No result or no Target evidence** | Check exact identity/QTH/band/window, actual operation, strict `code = 1` or historical-fallback status, and upstream availability. |
| **Benchmark has no Delta SNR** | Check shared remote peers in overlapping cycles or scheduled pairs, Reference uptime, clocks, schedule mapping, joint threshold, filters and scope. |
| **Benchmark has Delta SNR but little pairable evidence** | Read Joint Evidence Share and Decode Outcomes; check Reference uptime, power, thresholds, scope and whether the paired subset represents the wider station population. |
| **Performance has very few peers** | Check independent network activity, minimum confirmed opportunities, exclusions, solar state, time window and maximum peer distance. |
| **Many Performance rows lack independent confirmation** | The Target observations remain auditable but do not enter Decode Rate without the required independent activity evidence. |
| **`Only Reference = 0`** | Check Target-active conditioning, thresholds and active scope; zero can be correct. |
| **Unexpected Hardware A/B Delta SNR sign** | Verify physical A/B mapping, Target/Reference order, correction sign, schedule phases, actual/reported power and calibration. Reconcile one path in Drill-Down. |
| **Local result changes with radius** | Inspect local contributors and report radius sensitivity rather than selecting only the most favorable radius. |
| **Run stops because the source result is too large** | Shorten the UTC window. `Exclude Special Callsigns Q, 0, 1` or a smaller Local Neighborhood radius can reduce relevant source queries; maximum peer distance cannot because it is applied after retrieval. |
| **Recent spots appear incomplete** | Allow about five minutes after the final cycle, then check upload and upstream status. |

An upstream-data problem changes what the source supplied. An experiment-design problem changes whether the retained evidence answers the intended question. Diagnose and report them separately.

<a id="sec-6-3"></a>

#### 5.3 Callsign and locator checks

Performance and every Benchmark design match Target archive rows by exact callsign plus Target QTH grid-4. A Target uploading `JN37` while configured as `JN38` does not match.

Reference Station uses exact Reference callsign plus an independent four-character Reference Locator. RX and simultaneous TX Hardware A/B derive the Reference grid-4 from Target QTH; sequential TX Hardware A/B uses the shared Target identity and distinguishes paths by schedule. Local References are selected geographically.

Callsigns must satisfy the documented 3–15-character reporting-token rule. Locators must contain four or six valid Maidenhead characters. Syntax validation does not prove legal assignment, physical location or actual operation. Peer identity is exact `callsign + full reported locator`; stale or changing locators can split or move one physical station.

<a id="sec-6-4"></a>

#### 5.4 Historical decode-code fallback

WSPRadar first requests WSPR-2 rows with `code = 1`. If that strict request returns no Target-side evidence, it retries without the predicate for historical compatibility and reports the fallback in run status. The fallback broadens selection and can differ between Performance and Benchmark.

<a id="sec-6-5"></a>

#### 5.5 How the Target-Active Gate shapes evidence

The Target-Active Gate retains simultaneous cycles only when Target participation is observable. Reference reports from periods when the Target was offline are therefore not counted as automatic Target failures.

The gate is intentionally Target-centric. Reference uptime remains an experimental responsibility, and swapping Target and Reference can change one-sided Decode Outcomes and the eligible population. Sequential TX Hardware A/B uses deterministic scheduled pairs instead. [Section 7.3](#sec-7-3) defines the conditioning formally.

<a id="sec-6-6"></a>

#### 5.6 Working with upstream data

Public WSPR archives can contain duplicates, false spots, incorrect locators or power values, delayed uploads and later corrections. wspr.live describes fresh data as arriving after a delay of a few minutes; waiting about **five minutes** after the final cycle is a practical estimate, not a completeness guarantee <a href="#ref-10">[Ref-10]</a>.

WSPRadar reduces sensitivity to isolated bad rows through identity consolidation, medians, eligibility thresholds and Drill-Down, but repeated plausible errors can remain. Correct calculations cannot repair an incorrect reported power, locator or operating identity.

**System Audit Status** records the provenance needed to interpret the run:

| Status element | Meaning |
|---|---|
| **Data source** | The single upstream archive used for the completed run. Evidence from different archives is not combined within one run. |
| **Historical fallback** | Whether source selection was repeated without the strict WSPR-2 decode-code condition. |

These status items document where the evidence came from and whether the historical compatibility fallback was used; they do not define a different scientific method.

An archive retrieval larger than 1,000,000 complete rows is rejected before analysis rather than silently truncated. Shorten the window or use a relevant archive-side population filter as described in [Section 5.2](#sec-6-2).

<a id="part-iii"></a>
## Part III: Scientific Foundations, Methods and Claims

Part III is the scientific methods reference for technically critical radio amateurs, HamSCI contributors and reviewers. It defines the observational data, analysis targets, constructed evidence units, descriptive summaries, conditioning, missingness, weighting, dependence, transformations and reproducibility boundaries behind WSPRadar. It is intentionally more formal than the operator guide.

<a id="sec-d"></a>
### 6. Literature, Prior Art and Positioning

This chapter is a focused methodological review, not a systematic or exhaustive literature search. Peer-reviewed articles, preprints, amateur technical reports and software documentation support different kinds of claims; each source is used only for the contribution it actually demonstrates. The review does not imply that prior literature validates every WSPRadar metric or methodological choice.

<a id="sec-d-1"></a>
#### 6.1 From reporting network to experimental dataset

Taylor and Walker presented WSPRnet not merely as a live map but as an archive: “The WSPRnet database represents a rich source of experimental data for propagation studies.” Their example groups observations by time of day over several weeks, illustrating both the value of accumulated reports and the need to interpret them as observational rather than controlled laboratory data. <a href="#ref-6">[Ref-6]</a>

Frissell et al. place WSPRNet alongside the Reverse Beacon Network and PSKReporter as established amateur-radio observation networks that provide long-term bottomside-ionosphere observations. They distinguish these networks from purpose-built scientific instruments and recommend cross-calibration between instrument networks. The review supports scientific use of amateur observations; it does not make each contributing receiver a calibrated sensor. <a href="#ref-7">[Ref-7]</a>

The WSPR archive therefore combines unusual temporal depth and geographic reach with heterogeneous stations, successful-decode selection, user-supplied identities and powers, changing equipment and generally unknown operating schedules. These properties motivate explicit eligibility and conditioning rather than direct interpretation of spot absence.

<a id="sec-d-2"></a>
#### 6.2 Making observational WSPR data interpretable

<a id="sec-d-lo"></a>
Lo et al. used 7 MHz WSPR reports to study greyline propagation and warned that no authoritative operating schedules exist for WSPR equipment. Before interpreting a missing path, they checked whether a transmitter was heard elsewhere or whether a receiver heard another station, and they emphasized callsign/location consistency and multiple sites. <a href="#ref-9">[Ref-9]</a>

That activity-check principle is direct prior art for WSPRadar's Target-Active Gate and independently confirmed opportunities: silence should not become counter-evidence until relevant operation is observable. Lo et al. do not define WSPRadar's asymmetric Target conditioning, Performance analysis target, station balancing, Decode Outcomes or local References; those remain WSPRadar design choices for different analysis questions.

<a id="sec-d-3"></a>
#### 6.3 Antenna and station-comparison lineage

<a id="sec-d-toledo"></a>
**Toledo (2010): why slow alternation fails.** Sivan Toledo tested one antenna for roughly an hour and then another, finding path-SNR changes comparable with the apparent antenna difference. He concluded that this naive design could not isolate the antennas and proposed per-cycle switching or simultaneous transmissions with separate hardware. WSPRadar's deterministic interleaved TX A/B schedule follows the same practical logic: short separation reduces temporal confounding, but does not eliminate it. <a href="#ref-3">[Ref-3]</a>

<a id="sec-d-milazzo"></a>
**Milazzo (2011): operator-led end-to-end comparison.** Carol Milazzo compared two stations 29 km apart through one receiver 1,750 km away, corrected reported SNR for transmit-power differences, compared the trend with VOACAP, noted unequal duty cycles and examined reciprocal RX reports. The case study demonstrates the practical value of common-receiver WSPR comparison while also showing the limits imposed by different QTHs, hardware, local noise, a single selected receiver and no formal uncertainty analysis. <a href="#ref-4">[Ref-4]</a>

<a id="sec-d-griffiths-squibb"></a>
**Griffiths and Squibb (2017): same-signal RX comparison as station diagnosis.** For two receivers at separate QTHs, they retained reports of the same transmitter at the same time and related SNR difference to soil moisture, time, distance and station changes. The work shows how paired WSPR observations can diagnose complete receive systems and reveal structure hidden by spot totals. Because antennas, QTHs, noise and equipment differed, it supports comparative station evidence rather than isolated calibrated antenna gain. <a href="#ref-5">[Ref-5]</a>

<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels and Lamy (2022): conditioned simultaneous RX.** Their peer-reviewed experiment conditioned two nominally identical 160 m WSPR receiver stations and compared common remote transmissions simultaneously. This is the strongest direct precedent in this review set for RX Hardware A/B and for characterizing receive-chain offsets before interpreting antenna differences. Their propagation results also show that polarization and ionospheric effects remain coupled to reported SNR. <a href="#ref-2">[Ref-2]</a>

<a id="sec-d-zander"></a>
**Zander (2022): simultaneous same-receiver TX comparison.** Zander models two local antennas driven by separate nominally equal-power transmitters with different callsigns in the same WSPR cycle. A remote receiver contributes only when it reports both signals in the same interval. Under the same-time, common-path and equal-power assumptions, common path loss and receiver noise cancel in the SNR difference; frequency-selective interference, failed decodes, quantization and transmitter-chain differences remain. Because each difference is formed within one remote receiver, receiver calibration is not required for that pair, while equality or correction of the two transmitted powers remains essential. <a href="#ref-1">[Ref-1]</a>

Zander reports about 1,000 observations per preliminary experiment, of which roughly 150–200 joint reports from 15–35 receivers were retained, with sample standard deviation near 3 dB. The paper's sub-dB statement concerns precision of an arithmetic mean under its model and sample assumptions, not traceable total accuracy. Geographic sampling, antenna directivity and unknown elevation angles remain systematic limitations. The study supports simultaneous same-receiver Delta SNR, but not WSPRadar's sequential one-transmitter design, station-balanced medians, Decode Outcomes or neighborhood References.

<a id="sec-d-4"></a>
#### 6.4 Analysis infrastructure and related tools

Griffiths and Robinett demonstrated a relational time-series self-join for the same transmitter, time and band reported by two receivers, together with SNR-difference plots, medians, quartiles, time heatmaps, distance/azimuth views and export. This is important precedent for inspectable comparison infrastructure, not for WSPRadar's exact eligibility, conditioning or summary statistics. <a href="#ref-13">[Ref-13]</a>

WSPR.Rocks provides rapid SQL-based WSPR exploration, maps, tables, SpotQ and heatmaps. WSPRdaemon emphasizes robust multi-receiver acquisition, scheduling and added noise/Doppler metadata. SOTABEAMS WSPRlite/DXplorer, WSPR-Station-Compare, the Antenna Performance Analysis Tool and WATT provide additional comparison, reporting and visualization workflows <a href="#ref-14">[Ref-14]</a> <a href="#ref-15">[Ref-15]</a> <a href="#ref-16">[Ref-16]</a> <a href="#ref-17">[Ref-17]</a> <a href="#ref-18">[Ref-18]</a>.

These systems establish substantial prior art in data acquisition, exploration, ranking, comparison, mapping and reporting. WSPRadar's positioning therefore rests on its integrated experiment definitions, conditional populations, hierarchical weighting, complementary paired/one-sided evidence and audit path—not on being the first WSPR analysis tool.

<a id="sec-d-5"></a>
#### 6.5 What WSPRadar inherits, integrates and adds

WSPRadar inherits accumulated WSPR observations, activity checks, reported-power correction, common-condition pairing, calibrated receive-chain comparison, database joins and geographic/time inspection. It integrates them into one TX/RX workflow with:

* Performance based on independently confirmed opportunities;
* Hardware A/B, Reference Station and dynamic Local Neighborhood Benchmarks;
* same-cycle or deterministic scheduled-pair matching;
* reported-power normalization and optional Reference-side correction;
* paired Delta SNR separated from one-sided Decode Outcomes;
* station-balanced and observation-level summaries;
* map-to-segment-to-station-to-row audit; and
* versioned configuration, processed evidence and reproducibility export.

Within the reviewed sources, WSPRadar's clearest specific additions are the explicit conditional Performance denominator, the paired-versus-one-sided evidence split, dynamic Local Median/Best References, hierarchical station-balanced geographic aggregation and an integrated audit path across all supported designs.

This is a bounded integration and methods claim, not a global priority claim. Median aggregation itself is not novel. WSPRadar should be described as a structured experimental and audit layer above a spot browser, not as a substitute for the upstream archives, other analysis tools or calibrated RF measurement.

<a id="sec-7"></a>
### 7. Scientific Methods

This chapter defines the scientific contract of a WSPRadar run. WSPRadar starts from reported observations, constructs eligible evidence units, derives quantities such as normalized SNR and paired Delta SNR, and then calculates descriptive summaries. Those summaries are exact for the retained evidence under the selected rules. They become estimates of a broader or future population only if an additional sampling and dependence model is supplied; WSPRadar does not make that inferential step automatically.

It is useful to distinguish five levels:

1. **Reported observations:** uploaded WSPR spots with callsigns, locators, power, time and SNR.
2. **Constructed evidence units:** qualifying opportunities, peer-cycles, Joint units and scheduled A/B pairs formed by WSPRadar’s eligibility and matching rules.
3. **Derived quantities:** normalized SNR, Decode Outcomes and Target-minus-Reference Delta SNR for an individual evidence unit.
4. **Descriptive summaries:** rates, medians, reach, evidence shares and temporal or geographic summaries calculated from the retained evidence.
5. **Interpretation beyond the run:** statements about future behavior, a wider population or a physical cause. Such generalization requires additional assumptions and experimental control; the calculation alone is not sufficient.

The selected design therefore defines the analysis target—in formal statistical language, the estimand—through its conditioning, eligibility and weighting rules. This manual normally uses the plainer term analysis target. WSPRadar does not attach an inferential sampling model or confidence interval to that target.

**Notation used below**

| Symbol | Meaning |
|---|---|
| $i$ | one peer <strong class="defined-term">identity</strong>, defined as exact `callsign + reported locator` |
| $c$ | one eligible WSPR <strong class="defined-term">cycle</strong> or, for sequential TX A/B, one scheduled pair |
| $g$ | one retained <strong class="defined-term">geographic</strong> scope or segment |
| $b$ | one distance or time <strong class="defined-term">bin</strong> |
| $S_{i,c}$ | Target <strong class="defined-term">success</strong> indicator within an eligible Performance opportunity |
| $O_{i,c}$ | Performance <strong class="defined-term">opportunity</strong> indicator after activity, identity and population rules |
| $D_{i,c}$ | paired Target-minus-Reference <strong class="defined-term">Delta</strong> SNR where both sides are observed |
| $T_{i,b},J_{i,b},R_{i,b}$ | Only <strong class="defined-term">Target</strong>, <strong class="defined-term">Joint</strong> and Only <strong class="defined-term">Reference</strong> counts in Benchmark scope $b$ |

The selected design defines the **analysis target**—in formal statistical language, the estimand—through its eligibility, conditioning and weighting rules. This chapter uses **summary** or **descriptive statistic** for the rates, medians, shares and distributions calculated from the retained evidence. The distinction matters because a value can be calculated exactly for the retained rows while still describing a narrow or selected population.

**Method orientation**

| Design | Lowest comparison unit | Conditioning / eligibility | Principal summary | Primary boundary |
|---|---|---|---|---|
| RX Performance | one remote-transmitter peer-cycle | Target receiver active; same transmitter independently decoded elsewhere | peer Decode Rate, then equal-peer mean; pooled opportunity rate retained | conditional observability, not calibrated sensitivity |
| TX Performance | one remote-receiver peer-cycle | Target transmitter active; peer receiver independently active on band | peer Decode Rate, then equal-peer mean; pooled opportunity rate retained | conditional observability, not all attempted transmissions |
| RX Hardware A/B / Buddy | one remote-transmitter peer-cycle | Target active; both receivers report the same transmitter-cycle for Delta SNR | station median Delta SNR, then median across stations | complete receive paths unless chains are controlled |
| Simultaneous TX Hardware A/B / applicable Buddy or Local Benchmark | one remote-receiver peer-cycle | Target active; same receiver-cycle for paired Delta SNR | station median Delta SNR, then median across stations | power, chain and joint-decode selection |
| Sequential TX Hardware A/B | one remote receiver in one scheduled Target/Reference pair | deterministic disjoint schedule and complete in-window pair | station median Pair Delta, then median across stations | time separation and switching/schedule effects |
| Local Median Neighborhood | one Target/local-Reference peer-cycle | Target active; one contribution per active local identity | local median Reference, then station/segment Delta medians | changing uncalibrated membership |
| Local Best Station | one Target/best-local peer-cycle | Target active; strongest qualifying local identity | best-local Reference, then station/segment Delta medians | changing envelope, not fixed competitor |

The hierarchy can be read from left to right: WSPRadar first decides which evidence units belong to the analysis, then calculates a peer- or path-level quantity, and only then forms the displayed station-balanced summary. The formulas below make those steps auditable; the text following each formula explains the same operation in ordinary station terms.

<a id="sec-7-1"></a>
#### 7.1 Data source, observation units and time model

WSPRadar reads public WSPR reports from one selected read-only archive for each completed run. Reports are observational records produced by heterogeneous transmitters, receivers, decoders and reporting systems. A completed run does not combine data sources; the selected archive belongs to the run provenance.

A **spot** is one reported successful decode row. A **WSPR cycle** is the two-minute interval aligned to an even UTC minute. Same-cycle analyses consolidate qualifying rows by side, peer identity and cycle before classification. The effective UTC boundaries shown in the controls define the analysis window.

The lowest unit differs by design:

* Performance and simultaneous Benchmark use one peer identity in one eligible WSPR cycle.
* Sequential TX A/B retains exact scheduled starts, assigns them to Target or Reference by the configured modulo schedule and forms deterministic one-to-one Target/Reference pairs for each peer. Both planned starts must lie within the run window.
* Local Neighborhood Benchmark additionally constructs a cycle/path Reference from qualifying local identities before forming Target-minus-Reference evidence.

Historical `code = 1` fallback changes the source-row selection only when the strict request has no Target-side evidence. Run status records which source path was used. Upstream delay and data-quality limitations are described in [Section 5.6](#sec-6-6).

<a id="sec-7-2"></a>
#### 7.2 Identity, matching and row consolidation

WSPRadar treats reported identity as scientific data rather than a cosmetic label.

| Analysis | Target matching | Reference / peer identity | Lowest result unit |
|---|---|---|---|
| RX Performance | exact RX callsign + Target QTH grid-4 | TX callsign + full reported TX locator | Target-active peer-cycle |
| TX Performance | exact TX callsign + Target QTH grid-4 | RX callsign + full reported RX locator | Target-active peer-cycle |
| Reference Station / Buddy | exact Target callsign + Target grid-4 | exact Reference callsign + independent Reference grid-4; remote peer identity | consolidated peer-cycle |
| RX Hardware A/B | exact Target callsign + Target grid-4 | exact Reference callsign + same derived Target grid-4; remote TX identity | consolidated peer-cycle |
| Simultaneous TX Hardware A/B | exact Target callsign + Target grid-4 | exact Reference callsign + same derived Target grid-4; remote RX identity | consolidated peer-cycle |
| Sequential TX Hardware A/B | exact shared Target callsign + Target grid-4, split by schedule | same callsign/grid-4 on Reference schedule; remote RX identity | scheduled Target/Reference pair |
| Local Neighborhood Benchmark | exact Target callsign + Target grid-4 | local identity inside radius; remote peer identity | Target/local-Reference peer-cycle |

Target archive selection uses grid-4 even when a six-character QTH is configured. The full QTH remains relevant to distance, azimuth, solar elevation and local-radius geometry. Shared Hardware A/B grid-4 matching does not prove physical co-location.

If several qualifying non-identical rows represent one logical side/peer/cycle identity, WSPRadar retains the strongest qualifying normalized SNR as the best observed value for that logical identity. This prevents exact repeats or weaker secondary decodes from lowering the retained side value, but it is not a representative central value for one physical receiver. Different multi-receiver/reporting behavior on the two sides can therefore introduce asymmetry. Local Median Neighborhood instead forms a median within each local identity before aggregating across identities.

The local pool excludes the Target by exact callsign. A base callsign and suffixed callsign are distinct unless the exact Target form matches. Bad, stale or changing locators can split one physical station, move it geographically or trigger the moving-station exclusion.

<a id="sec-7-3"></a>
#### 7.3 Target-active conditioning and eligibility

Let $A_c$ indicate observable Target participation in cycle $c$:

* TX: at least one qualifying Target transmission report exists somewhere in the cycle.
* RX: the Target receiver uploaded at least one qualifying decode in the cycle.

Performance and simultaneous Benchmark condition on $A_c=1$. This protects known Target downtime from becoming automatic counter-evidence, but it changes the analysis population: the result describes cycles in which Target participation was observable, not all clock time or all planned attempts.

The conditioning is asymmetric. Reference uptime is not a second gate and must be controlled or documented externally. Swapping Target and Reference can therefore change eligible cycles and one-sided Decode Outcomes even when the sign of Joint-only Delta SNR reverses as expected.

Every Joint observation already implies Target participation, so the gate does not change Joint-only Delta SNR values. It changes the population of one-sided/asynchronous outcomes and, in Performance, the opportunity denominator. Sequential TX A/B uses deterministic scheduled eligibility rather than the simultaneous Target-Active Gate.

Target-active evidence may be established globally even when the peer that proves activity lies outside the selected geographic analysis scope. That peer establishes $A_c$ only; it does not enter scoped outcomes, summaries or exports.

<a id="sec-7-4"></a>
#### 7.4 Performance analysis target, classification and summary statistics

For peer $i$ and Target-active cycle $c$, let $O_{i,c}=1$ when independent activity evidence makes that peer-cycle a qualifying opportunity after the selected band, identity, filter and scope rules. Let $S_{i,c}=1$ when the Target also produces the required evidence in that opportunity, with $S_{i,c}\le O_{i,c}$.

* RX independent activity: another eligible receiver reports the same transmitter identity in the same cycle.
* TX independent activity: the peer receiver reports another same-band transmitter in the same cycle.

Target evidence without the independent activity needed for $O_{i,c}=1$ remains auditable but is excluded from Decode Rate. Within qualifying RX opportunities, WSPRadar distinguishes cycles heard by the Target from cycles heard only by other eligible receivers. Within qualifying TX opportunities, it distinguishes cycles in which the peer receiver heard the Target from cycles in which it heard only other qualifying signals on the same band.

For one qualifying peer:

$$n_i=\sum_c O_{i,c},\qquad h_i=\sum_c S_{i,c}$$

$$r_i=100\%\times\frac{h_i}{n_i}$$

Here, $n_i$ is the number of qualifying opportunities retained for peer $i$, $h_i$ is the number of those opportunities in which the Target succeeded, and $r_i$ is that peer's Decode Rate. A peer contributes only when $n_i$ meets the configured minimum.

For geographic scope $g$ with qualifying peer set $I_g$, the **Station-balanced Decode Rate** is:

$$R_{station}(g)=\frac{1}{|I_g|}\sum_{i\in I_g} r_i$$

The **Opportunity-level Decode Rate** is:

$$R_{opportunity}(g)=100\%\times\frac{\sum_{i\in I_g}h_i}{\sum_{i\in I_g}n_i}$$

In plain terms, the first calculates one rate per peer and then gives every peer one equal vote. The second pools all qualifying opportunities and therefore gives more influence to peers that contributed more opportunities. These are complementary summaries of the retained evidence, not competing estimates of one uniquely defined “true” Decode Rate.

At-least-once Peer Reach is:

$$Reach(g)=100\%\times\frac{|\{i\in I_g:h_i\ge1\}|}{|I_g|}$$

The numerator counts qualifying peer identities that produced at least one Target success; the denominator counts all qualifying peers in the scope. A peer with one success and a peer with many successes both count once for Reach.

Reach is a breadth measure and normally increases with observation duration. It does not describe how consistently those peers were decoded; Decode Rate answers that separate question.

Successful Target SNR is defined only where the Target was decoded/reported. It is therefore a success-conditioned distribution. Missed opportunities have no Target SNR and no synthetic value. Decode Rate and successful SNR must be interpreted jointly because a system that adds marginal decodes can show lower successful-SNR summaries while improving practical reach.

The Performance analysis target is the Target's conditional participation among independently observable opportunities in the retained population. It is not unconditional receiver sensitivity, the success probability of every attempted transmission or absolute station efficiency.

<a id="sec-7-5"></a>
#### 7.5 Power normalization, correction and Benchmark Delta SNR

WSPR reports SNR on the WSJT scale in dB relative to a 2500 Hz reference bandwidth and carries reported transmit power in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar normalizes successful TX-side SNR to reported 30 dBm:

$$SNR_{norm}=SNR_{measured}-P_{TX(dBm)}+30$$

In words, the reported transmit-power difference is removed by expressing every successful TX-side SNR as though the reported power had been `30 dBm`. This removes only the **reported** power term. It does not correct antenna gain, radiation efficiency, feedline loss, EIRP, receiver calibration or local noise.

Reference-side correction is additive:

$$SNR_{R,corr}=SNR_R+C_R$$

For a paired observation:

$$D_{i,c}=\Delta SNR_{i,c}=SNR_{T,i,c}-SNR_{R,corr,i,c}$$

This is simply corrected Target SNR minus corrected Reference SNR for one matched evidence unit. Positive $D_{i,c}$ favors the Target; negative favors the Reference. A positive correction makes the Reference stronger before subtraction and therefore lowers Delta SNR. The entered calibration offset uses the same `target - reference` sign.

In same-transmitter RX pairs, the common reported TX-power term cancels. TX pairs involving different signals depend directly on reported-power accuracy and on any uncorrected transmitter/feedline difference. A Reference correction is scientifically defensible only when the offset is approximately additive and stable over the relevant band, level, hardware state and time.

<a id="sec-7-6"></a>
#### 7.6 Paired evidence, Decode Outcomes and missingness

Benchmark answers two linked evidence questions:

1. the distribution of Target-minus-Reference Delta SNR among **Joint** comparison units; and
2. the composition of retained evidence into **Only Target**, **Joint**, **Only Reference** and, at identity level, **Both (Async)**.

Delta SNR exists only when both sides produce comparable evidence. The Joint subset is therefore selected on successful observation of both sides. This paired selection is not missing at random in the ordinary statistical sense: weak signals, collisions, QRM, decoder behavior, power differences and path conditions can affect whether a pair exists.

One-sided evidence has no missing-side SNR to reconstruct. It cannot be assigned an artificial Delta SNR and is not power-normalized as a pair. In TX Benchmark, unequal actual or reported powers can strongly affect one-sided outcomes even when Joint Delta SNR is normalized.

`Both (Async)` means that an identity has retained evidence from both sides but lacks a qualifying same-cycle or scheduled pair for the relevant station category. It indicates broader two-sided participation without contributing paired Delta SNR.

Successful-SNR censoring in Performance and Joint-decode selection in Benchmark are distinct selection processes. WSPRadar exposes Decode Outcomes and Joint Evidence Share so the paired Delta-SNR summary can be read against the wider retained evidence rather than treated as the complete station population.

<a id="sec-7-7"></a>
#### 7.7 Aggregation hierarchy and weighting

WSPRadar aggregates the evidence hierarchically so that one high-volume peer does not dominate station-balanced summaries solely by reporting more observations.

**Performance**

1. Classify each eligible peer-cycle.
2. Aggregate qualifying Target successes and counter-evidence by peer identity, while retaining Target observations without independent confirmation separately for audit.
3. Apply the minimum opportunity count.
4. Calculate one peer Decode Rate $r_i$.
5. Calculate the equal-peer mean $R_{station}$.
6. Retain $R_{opportunity}$ as the complementary volume-weighted summary.

**Simultaneous Benchmark**

1. Consolidate Target and Reference evidence by peer and cycle.
2. Calculate $D_{i,c}$ for Joint cycles.
3. Apply the minimum Joint count per peer.
4. Calculate the peer median:

    $$m_i=\operatorname{median}_{c}(D_{i,c})$$

5. For scope $g$, calculate the station-balanced segment summary:

    $$M_g=\operatorname{median}_{i\in I_g}(m_i)$$

In words, each peer is first reduced to one typical paired difference, $m_i$, and the segment summary $M_g$ is then the median across those peer values. A peer with many Joint observations therefore cannot dominate the station-balanced segment merely through volume.

The observation-level median of all $D_{i,c}$ is retained separately. It answers a different question because peers with more Joint observations receive more weight.

**Sequential TX A/B**

1. Retain exact-identity reports matching Target or Reference schedule phases.
2. Pair planned starts one-to-one by nearest cyclic separation under the common Repeat Interval.
3. Require both planned starts to lie within the run window.
4. Within each peer and scheduled pair, calculate a micro-median for each side.
5. Calculate Pair Delta when both micro-medians exist; otherwise retain the pair as one-sided evidence.
6. Apply the minimum complete-pair count per peer.
7. Calculate peer and segment medians as above.

The micro-median protects a scheduled side from duplicate-like repeated rows but does not make the two sequential transmissions simultaneous.

**Local Median Neighborhood**

For each remote peer-cycle, WSPRadar first calculates one normalized SNR contribution per active local `callsign + locator`, then takes the exact median across contributing local identities. An absent local identity is omitted rather than assigned zero. Reference correction is applied before the local pool is aggregated. The Target is compared with this cycle/path median, after which peer and segment Delta-SNR medians are calculated.

**Local Best Station**

For each remote peer-cycle, WSPRadar selects the strongest qualifying corrected local contribution as the Reference. The resulting Reference is a changing upper envelope. It is neither a local mean nor a comparison with one fixed station.

Medians reduce sensitivity to isolated extreme values, quantized SNR outliers and duplicate-like bursts. They do not remove systematic calibration error, propagation bias or dependence across cycles and stations.

<a id="sec-7-8"></a>
#### 7.8 Geographic, temporal and selected-path summaries

<a id="sec-7-8-1"></a>
##### 7.8.1 Geographic summaries

Segment Inspector starts from the complete qualifying peer population in the active retained scope; table sorting, row selection and visibility controls do not change these summaries.

Performance distance profiles group peers by exact calculated distance from Target QTH. A deterministic width of `125`, `250`, `500` or `1,000 km` is selected from the active distance span, with edges anchored at integer multiples from `0 km` and the final selected upper boundary included. Disjoint selected ranges retain missing gaps rather than treating them as zero evidence.

For each distance bin, WSPRadar calculates:

* at-least-once Peer Reach;
* station-balanced Decode Rate;
* Opportunity-level Decode Rate; and
* successful Target SNR, first reduced to one median per peer and then summarized across peer medians.

For successful-SNR spread, three or more peer medians produce an IQR, two produce a min–max interval, and one produces a single point. Counter-only peers receive no synthetic SNR. Distance inherits the precision of the reported Maidenhead locator and is not survey-grade positioning.

Benchmark geographic summaries use one peer median Delta SNR per qualifying identity and then the segment median of those peer medians. Observation-level Delta SNR remains available as a separately weighted distribution.

<a id="sec-7-8-2"></a>
##### 7.8.2 Benchmark evidence coverage

For station $i$ in bin $b$, let Only Target, Joint and Only Reference counts be $T_{i,b}$, $J_{i,b}$ and $R_{i,b}$, with:

$$N_{i,b}=T_{i,b}+J_{i,b}+R_{i,b}$$

A contributing station supplies one split support vote:

$$v_{T,i,b}=\frac{T_{i,b}}{N_{i,b}},\qquad v_{J,i,b}=\frac{J_{i,b}}{N_{i,b}},\qquad v_{R,i,b}=\frac{R_{i,b}}{N_{i,b}}$$

The station-balanced Joint Evidence Share is:

$$JES_{station}(b)=100\%\times\operatorname{mean}_{i}\left(\frac{J_{i,b}}{N_{i,b}}\right)$$

The outcome-level share is:

$$JES_{outcome}(b)=100\%\times\frac{\sum_iJ_{i,b}}{\sum_iN_{i,b}}$$

The station-balanced form first asks what fraction of each peer's retained units were Joint and then averages those fractions. The outcome-level form simply pools all retained units before taking the Joint fraction. The same distinction—equal peer weight versus equal evidence-unit weight—appears elsewhere in WSPRadar.

The first gives every contributing peer equal weight; the second gives every retained comparison unit equal weight. Joint Evidence Share measures pairability—the fraction of retained evidence that can contribute Delta SNR. It is not a Target win rate.

Under the Target-Active Gate, Only Target and Only Reference are directional and asymmetric. Sequential TX A/B instead uses deterministic complete or one-sided scheduled pairs, but a one-sided pair still has no Pair Delta.

<a id="sec-7-8-3"></a>
##### 7.8.3 Temporal summaries and UTC folding

Chronological views preserve the actual sequence of the run using the selected time-bin width. UTC-hour views fold evidence from represented dates onto fixed one-hour slots to describe recurring time-of-day structure.

For Performance successful-SNR deviation, a peer enters the anomaly population only when it has at least three successful normalized Target-SNR observations in the complete run window. Its baseline is the median of those successes. Each successful observation contributes:

$$A_{i,c}=SNR_{i,c}-\operatorname{median}_{c'}(SNR_{i,c'})$$

Thus `0 dB` means “at this path's own usual successful level,” not Target–Reference equality. A positive anomaly is a stronger-than-usual successful decode for that path, and a negative anomaly is weaker than usual.

Chronologically, each peer contributes at most one median anomaly per selected bin. In the UTC-folded view, each peer contributes one median per date and UTC hour before those peer-date-hour values are summarized across the folded population. This prevents prolific peers or dates from dominating through raw row count.

Performance temporal support uses the same qualifying peers but retains all confirmed opportunities, including peers omitted from the successful-SNR anomaly layer. In a chronological bin, each peer contributes one split vote according to its within-bin Decode Rate. The station-support total is therefore the number of contributing peers, while the split ratio reproduces the station-balanced rate. The opportunity-support total is the raw confirmed-opportunity count, and its split ratio reproduces the Opportunity-level rate.

For each folded UTC hour, station support is the average number of distinct peer-date-hour presences over represented dates whose hour slot overlaps the analysis window. The folded station-balanced rate is calculated by pooling each peer's outcomes at that UTC hour across represented dates, calculating one rate per peer, and then giving each peer equal weight. Folded opportunity counts are pooled outcome totals divided by the corresponding represented-date denominator.

For Performance, a **represented UTC date** is a date with at least one qualifying confirmed opportunity somewhere in the active scope and selected window. A represented date-hour inside the window contributes zero when it has no evidence; a date-hour outside the window is excluded. A partially overlapping first or last hour counts as one represented slot rather than receiving exposure weighting, so boundary-hour averages can be depressed. UTC-hour folding requires at least two represented dates.

Benchmark temporal Delta SNR uses retained Joint observations or complete scheduled pairs. Chronological bins summarize raw paired values in actual time; UTC-hour bins summarize the same paired population by hour across dates represented by retained Benchmark evidence. Benchmark temporal coverage uses all retained Only Target, Joint and Only Reference units and the two Joint Evidence Share summaries above. Benchmark folding likewise requires at least two represented evidence dates.

<a id="sec-7-8-4"></a>
##### 7.8.4 Selected-path summaries

Selected Station Evidence filters the active retained scope to one exact peer identity without changing the upstream analysis population.

For Performance, the selected path reports:

* actual normalized successful Target SNR in chronological bins;
* one date-hour median per represented date in the folded SNR profile;
* successful/counter opportunity counts; and
* Decode Rate through time.

With one peer, station-balanced and Opportunity-level Decode Rate are numerically identical within a populated bin; the separate support counts still distinguish path presence from evidence volume.

For Benchmark, the selected path reports observation-level Delta SNR for each Joint unit or complete scheduled pair and separately reports Only Target, Joint and Only Reference coverage. Changing the selected path or display bin changes only the retained-evidence view, not matching, eligibility or aggregation upstream.

<a id="sec-7-8-5"></a>
##### 7.8.5 Descriptive spread and visualization transforms

IQR and min–max displays are descriptive spread summaries, not confidence intervals. An IQR band is drawn only where at least five values contribute to the relevant bin; the median remains available with fewer values. Empty bins remain missing rather than becoming synthetic zero observations.

Benchmark histograms normally use 1 dB bins, use 0.5 dB only for a clear half-dB lattice, and coarsen broad ranges to keep the number of bins bounded. Temporal density cells use integer-dB classes. Each density panel is normalized independently:

$$D_{relative}=100\times\frac{n_{cell}}{\max(n_{cell,panel})}$$

Here $n_{cell}$ is the evidence count in one density cell. Dividing by the most populated cell converts the panel to a relative-density display while leaving the underlying counts unchanged.

Thus `100` means the most populated cell in that panel, not 100% of all evidence. Density colors cannot compare absolute evidence volume between independently normalized panels; support counts provide that information.

Benchmark temporal and histogram views use a presentation-only monotonic scale centered on the scope median $M$. For a broad range, equal visual steps are anchored at $M$, $M\pm3$, $M\pm6$, $M\pm10$, $M\pm20$ and $M\pm30$ dB, with a tail anchor at $M\pm60$ dB and extrapolation when required. When every required deviation is at most `10 dB`, the tighter anchors are $M$, $M\pm1$, $M\pm3$, $M\pm6$ and $M\pm10$ dB, with continuation anchors at $M\pm20$ and $M\pm40$ dB. The required range includes the applicable raw histogram or rounded heatmap-bin edges, a minimum `3 dB` half-span and absolute `0 dB`, so Target–Reference equality remains visible. The anchor mapping changes displayed spacing only: raw Delta SNR values, bin membership, counts, medians and quartiles remain unchanged. Because the vertical mapping is nonlinear, histogram bar **length** against its percentage axis—not displayed area—is the quantitative encoding.

Performance successful-SNR views remain on a linear dB axis.

<a id="sec-7-9"></a>
#### 7.9 Geography, solar classification and population filters

Distance and azimuth are calculated from the configured Target QTH and reported peer locators using a spherical Earth radius of 6371 km. The map uses an azimuthal equidistant projection centered on Target QTH, with radial boundaries at 2500, 5000, 10000, 15000, 20000 and 22000 km and 22.5-degree azimuth sectors.

Reported locators represent grid cells rather than measured antenna coordinates. Geographic summaries are internally consistent with those inputs but should not be interpreted as survey-grade position or direct take-off-angle measurement.

`Maximum peer distance from Target (km)` removes peers at or beyond the selected distance before scientific aggregation and processed-evidence export. Map segments, support counts, Segment Inspector and exports therefore use one retained peer population. Inspector selections can narrow that population but cannot restore excluded rows.

Two rules precede the geographic scope:

* Target-active conditioning remains global, so an out-of-scope peer can prove Target operation without becoming a scoped outcome.
* When moving-station exclusion is enabled, changing-location callsigns are identified in the otherwise eligible global population before distance scope is applied.

Solar classification uses solar elevation at Target QTH. Same-cycle evidence uses the cycle timestamp. Scheduled TX A/B uses the midpoint between the planned Target and Reference starts so one pair cannot be split across solar classes.

The archive row limit and the controls that can reduce the retrieved source population are operational matters documented in [Section 5.6](#sec-6-6); they do not change the scientific summaries after the retained population has been formed.

<a id="sec-7-10"></a>
#### 7.10 Dependence, uncertainty and validation scope

WSPRadar observations are clustered rather than independent. In ordinary station terms, 1,000 spots are not the same as 1,000 unrelated experiments. Repeated cycles from one peer share hardware and path characteristics; stations in nearby regions share propagation; time bins are autocorrelated; and one ionospheric or interference event can affect many observations simultaneously. A large row count is therefore not an independent sample size.

Station balancing reduces domination by prolific peers, and medians reduce sensitivity to isolated outliers. Neither creates independence, removes systematic bias nor supplies a sampling distribution. IQRs describe within-run spread and are not uncertainty intervals.

WSPRadar currently reports descriptive summaries of retained evidence. It does not automatically calculate standard errors, confidence intervals, p-values, statistical power or causal effects. The summaries can be exact for the retained evidence while uncertainty about a wider population or future run remains unresolved. Naive inferential calculations that treat every spot or pair as independent would generally understate that uncertainty.

Scientific support should therefore be described at several levels:

* **evidence depth:** number of opportunities, Joint units or scheduled pairs;
* **evidence breadth:** number and geographic diversity of peer identities;
* **within-run consistency:** agreement across station-balanced, observation-level, geographic and temporal summaries;
* **experimental repeatability:** recurrence in a new suitably controlled run; and
* **experimental control:** calibration, crossover, reversed schedule or independent measurement appropriate to the claim.

Empirical software-validation audits are not timeless method definitions. Any reported validation statistic should identify its datasets, date, WSPRadar version or source revision, and calculation method. Without that provenance it should be removed from the normative manual or labelled explicitly as a dated validation check.

<a id="sec-8"></a>
### 8. Evidence-Matched Claims and Reproducibility

WSPRadar supports bounded descriptive and comparative claims about retained observational evidence. Strong reporting identifies the conditioned population, reported summary and weighting, support, experiment design and remaining unobserved or uncontrolled variables.

<a id="sec-8-1"></a>
#### 8.1 Claim classes and evidence-matched wording

| Claim class | What WSPRadar can support | Additional requirement for a stronger claim |
|---|---|---|
| **Descriptive** | Reach, Decode Rate, successful SNR, Delta SNR, Decode Outcomes and where they appeared in the selected evidence. | State the population, weighting, scope and support. |
| **Comparative** | Target-versus-Reference difference under the selected Benchmark design. | State what the Reference represents and the matched subset. |
| **Component attribution** | A difference associated with a local path or component. | Controlled Hardware A/B, calibration and preferably crossover/reversal. |
| **Causal** | The tested change caused the observed effect. | A design that controls plausible alternatives; WSPRadar summaries alone are insufficient. |
| **Inferential** | Confidence, significance or a population-general effect. | A justified dependence model and inferential analysis not currently supplied by WSPRadar. |

Use the result type that matches the statement:

* **Performance** supports the Target's conditional behavior within independently confirmed opportunities and its at-least-once reach during the selected window.
* **Benchmark Delta SNR** supports paired Target-minus-Reference description within the Joint subset.
* **Decode Outcomes** support statements about pairability and one-sided evidence.
* **Distance or direction structure** supports statements about observed path segments, not direct radiation angle or gain pattern.
* **Local Neighborhood Benchmark** supports statements relative to the selected dynamic local definition, not a permanent station ranking.

| Avoid | Evidence-matched wording |
|---|---|
| “Antenna A has 3 dBi more gain.” | “Path A produced a +3.0 dB station-balanced median Delta SNR against B for the paired evidence in this band, window and segment.” |
| “My receiver sensitivity is 72%.” | “The Target receiver's station-balanced Decode Rate was 72% among qualifying peer-cycles independently confirmed elsewhere.” |
| “Performance should be close to 100%.” | “Decode Rate is conditional on independently confirmed opportunities; 100% is not an expected baseline.” |
| “A is statistically significantly better.” | “The descriptive paired median favored A in the selected evidence; no significance test was performed.” |
| “The antenna has a lower take-off angle.” | “The observed advantage was concentrated in the specified longer-distance segments; radiation angle was not measured.” |
| “A is more efficient because it had more exclusive decodes.” | “A produced more one-sided decode evidence under the documented power, schedule and network conditions; efficiency was not isolated.” |
| “The local median is the average local station.” | “The Reference was the cycle/path median of one contribution per active local callsign-plus-locator identity.” |

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
* archives contain successful decodes rather than complete attempt logs;
* Performance is conditioned on independently observable opportunities;
* Target-active conditioning is asymmetric;
* successful Target SNR is censored to successful decodes;
* Benchmark Delta SNR is selected on Joint observation of both sides;
* one-sided evidence has no missing-side SNR;
* simultaneous TX retains power, frequency-response, isolation and coupling differences between chains;
* sequential TX remains time-separated;
* station hardware, software, terrain, local noise, polarization and propagation remain coupled unless the experiment controls them;
* observations are clustered across station, time, geography and propagation; and
* upstream records and availability can change after the original run.

These boundaries define what the summaries describe; they do not make the observations useless. Broad, internally consistent and experimentally repeatable evidence can be operationally persuasive while remaining descriptive.

<a id="sec-8-3"></a>
#### 8.3 Reporting and reproducibility checklist

For a serious analysis, preserve three layers.

**1. Analysis definition**

* WSPRadar application version and, where available, source revision;
* RX/TX Direction, result type and Benchmark design;
* exact Target and Reference identities and locators;
* band and effective UTC boundaries;
* geographic scope, solar state, exclusions and evidence thresholds;
* Reference correction purpose, signed value and calibration basis;
* primary predeclared evaluation scope and any sensitivity analyses; and
* whether the run was exploratory or confirmatory.

**2. Evidence supporting the conclusion**

* reported summary and weighting level;
* qualifying peers and opportunities for Performance;
* Joint peers and Joint spots/pairs for Benchmark;
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

`Prepare All Results for Download` builds a package from the completed run and current inspection selections. A typical package contains:

```text
config/
  wspradar_config.config
  run_metadata.json
benchmark/
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
performance/
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

Files without an applicable result or selected station can be absent.

| Artifact | Scientific content and scope |
|---|---|
| `wspradar_config.config` | Versioned runnable definition and durable result-view settings. |
| `run_metadata.json` | Application/export provenance, Direction, band, time selection, Benchmark/correction definition, filters, thresholds and inspection selections. |
| `analysis_cache.parquet` | Processed retained evidence after scientific filters and geographic scope; not an untouched upstream dump. |
| `table_station_insights_current_segment.csv` | Per-peer summaries for the active Segment Inspector scope. |
| Drill-Down CSV files | Row-level retained evidence for selected or active-scope identities. |
| Map and segment figures | Geographic and segment-level descriptive summaries for the completed result. |
| Temporal figures | Chronological and UTC-folded summaries for the active segment. |
| Selected-station figures | One exact selected peer identity; paths are never pooled across several selected stations. |

**Machine-readable contract names.** The exact names below are included because they are supported external configuration, URL or export contracts. They are not vocabulary for explaining the scientific method.

| Contract surface | Exact names | Meaning |
|---|---|---|
| Configuration format | schema version `1` | Current pre-production `.config` contract; invalid or unsupported files are rejected rather than silently reinterpreted. |
| Result-type values | `performance`, `benchmark` | Values emitted by new analysis URLs, configurations and exports. |
| Durable result-view blocks | `results_view.performance`, `results_view.benchmark` | Saved inspection preferences. Their presence does not create or run an additional result. |
| Result folders | `performance/`, `benchmark/` | Top-level result folders in the export package. |
| Figure metadata | `selected_evidence_figures`, `benchmark_evidence_figures`, `benchmark_evidence_recipes` | Stable mappings for applicable exported figures and Benchmark recipes. |
| Correction metadata | `benchmark_snr_correction_mode`, `benchmark_snr_correction_db` | The semantic correction choice and its numeric dB value. |

The export package preserves the processed evidence and provenance recorded by WSPRadar. It does not contain authoritative external operating logs, physical setup measurements or unchanged upstream responses. Preserve those separately as described in [Section 8.3](#sec-8-3).

<a id="sec-8-5"></a>
#### 8.5 Disclaimer

WSPRadar is experimental open-source software provided “as is” without warranty. Its source and methods can be audited, but accuracy, completeness, availability and fitness for purpose are not guaranteed. Do not base major financial or safety decisions on WSPRadar alone.

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
4. **Derive the offset:** use paired Delta SNR evidence and state whether the value was calculated from station-balanced summaries or raw pairs.
5. **Check consistency:** inspect by station, time and SNR. One constant is not defensible if offset changes with level, frequency, AGC or time.
6. **Apply the sign:** enter the observed `target - reference` offset with the same sign.
7. **Validate:** repeat or swap paths and confirm corrected common-input Delta is plausibly near zero.

Consistency across station, time and SNR views supports using one additive offset within the tested setup; it does not establish traceable laboratory accuracy. Splitter loss, mismatch, coupling and source instability can remain.

<a id="sec-license"></a>
### License

WSPRadar is licensed under the GNU Affero General Public License version 3 (AGPLv3). The repository `LICENSE` file is controlling.

"""
