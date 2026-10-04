# Whole-manual accessibility and correctness review

Accepted source model: parallel/co-authored English/German manuals at the recorded hashes. The common specification is the approved Benchmark-first, Performance-equal-depth manual for technically interested radio amateurs, with practical meaning before formulas, natural German, established terminology and retained scientific/operating qualifications.

This review follows the completed Chapter 2 rollout. Its baseline already includes those changes. It does not overwrite unrelated runtime work.

## Baseline

- `en`: `574cc1b41fa2b15a1d76b6ec97db59f4fc51f20295816c67110f867611c2d999`

## EN: preserved original passages

The following original paragraphs or table/list blocks were replaced, condensed, corrected or relocated. Their factual/operating meaning is accounted for in the chapter review records below; verbatim text is retained here so no superseded wording disappears without a record.

### Original in 0. Why WSPRadar?

<details><summary>Verbatim baseline passage</summary>

````text
The result is more than a spot count and more than a single winner-versus-loser number. WSPRadar can show whether a pattern is broad or path-specific, whether it is associated with distance or direction, whether it appears once or recurs by time of day, whether many stations agree, and whether the paired evidence represents the wider result. It helps move station experimentation from **“this looked better once”** toward **“this difference repeatedly appeared here, under these conditions, with this much support.”**
````

</details>

### Original in 0.0 WSPR in 2 Minutes

<details><summary>Verbatim baseline passage</summary>

````text
<strong class="defined-term">WSPR</strong> stands for **Weak Signal Propagation Reporter**. Joe Taylor, K1JT, and Bruce Walker, W1BW, described it as a worldwide network of low-power stations exchanging beacon-like transmissions to explore possible propagation paths. A WSPR-2 transmission lasts just under two minutes and occupies only about 6 Hz. A normal Type 1 message carries one ordinary callsign, a four-character Maidenhead locator and reported transmit power in dBm in that single transmission. Decoder-reported signal-to-noise ratio (SNR) is referenced to a 2500 Hz bandwidth, and successful decodes are possible at approximately `-28 dB`; a less negative SNR means a stronger signal relative to the receiver noise <a href="#ref-6">[Ref-6]</a> <a href="#ref-8">[Ref-8]</a>.
````

</details>

### Original in 0.0 WSPR in 2 Minutes

<details><summary>Verbatim baseline passage</summary>

````text
When reporting is enabled, a receiver uploads each successful decode as a <strong class="defined-term">spot</strong>. A spot records the transmitter and receiver identities, their reported locations, time, band, transmit power and decoder-reported SNR. Public <strong class="defined-term">archives</strong> consequently contain a large, continuously growing record of successful radio observations contributed by independently operated stations around the world. Services such as wspr.live and WSPRDaemon preserve and expose this observational record for analysis <a href="#ref-10">[Ref-10]</a> <a href="#ref-11">[Ref-11]</a>.
````

</details>

### Original in 0.0 WSPR in 2 Minutes

<details><summary>Verbatim baseline passage</summary>

````text
Extended WSPR can instead convey a compound callsign and precise six-character locator across two complementary transmissions. A Type 2 message carries the compound callsign and power but no locator; the matching Type 3 message carries a 15-bit hash of that callsign, the six-character locator and power. The two transmissions are separate WSPR cycles, not two fields of one archive row <a href="#ref-12">[Ref-12]</a>.
````

</details>

### Original in 0.0 WSPR in 2 Minutes

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar does not decode these radio messages or reconstruct a compound identity from Type 2 and Type 3 phases. It analyzes the callsign, locator, time and power fields preserved by the selected reporting archive. For simultaneous TX A/B, both exact identities must therefore appear in the archive with their truthful reported locations and aligned message phases; [Sections 2.2.1](#sec-3-tx-benchmark-simultaneous), [7.1](#sec-7-1), [7.2](#sec-7-2) and [7.6](#sec-7-6) explain the practical and scientific consequences.
````

</details>

### Original in 0.0 WSPR in 2 Minutes

<details><summary>Verbatim baseline passage</summary>

````text
**Data sources.** WSPRadar uses **wspr.live** as its primary data source. The WSPRadar project is grateful to the people behind wspr.live and WSPRDaemon who make this public database infrastructure available and keep it running.
````

</details>

### Original in 0.0 WSPR in 2 Minutes

<details><summary>Verbatim baseline passage</summary>

````text
Under concurrent load, WSPRadar can route a complete new run to **WSPRDaemon WD2** and then **WD1**, as capacity permits. This ordered capacity spillover is distinct from provider failover: if a selected source fails, WSPRadar discards the unpublished attempt and restarts the complete run on the next source. Every completed run remains pinned to one archive; records from different sources are never combined.
````

</details>

### Original in 0.0 WSPR in 2 Minutes

<details><summary>Verbatim baseline passage</summary>

````text
One limitation is central to every analysis: the archive records successful decodes, not a complete log of every attempted transmission or every active receiver. A valid successful decode directly confirms participation of both endpoints. Within a Target-active cycle, WSPRadar therefore constructs an <strong class="defined-term">opportunity</strong> when the Target-side decode succeeds or external evidence confirms the relevant peer activity. For RX, the Target RX decoding the peer TX is a success; another eligible RX decoding that same peer TX confirms the peer TX activity needed to assess a missing Target RX decode. For TX, the peer RX decoding the Target TX is a success; that same peer RX decoding another qualifying same-band TX confirms the peer RX activity needed to assess a missing Target TX decode. All evidence must match the selected band, cycle and exact peer identity. Without sufficient endpoint-activity evidence, silence remains unknown and excluded; activity somewhere else never establishes that a particular silent receiver was listening.
````

</details>

### Original in 0.0 WSPR in 2 Minutes

<details><summary>Verbatim baseline passage</summary>

````text
This distinction turns WSPR from a collection of successful spots into evidence that can support questions about practical reach, consistency and relative performance without pretending that every missing report represents a failed radio path.
````

</details>

### Original in 0.1 What WSPRadar can show

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar is a WSPR-based antenna and station performance analysis and benchmarking system. It evaluates one <strong class="defined-term">Target</strong>: the station under test, normally your station, represented either as a complete installed station or as a controlled transmit or receive path. A <strong class="defined-term">peer</strong> is a remote station whose radio path contributes to the analysis. <strong class="defined-term">Decode Rate</strong> is the percentage of confirmed opportunities in which the Target-side decode succeeded: the Target decoded the peer in RX, or the peer decoded the Target in TX. WSPRadar then answers one of two broad questions.
````

</details>

### Original in 0.1 What WSPRadar can show

<details><summary>Verbatim baseline passage</summary>

````text
* <strong class="defined-term">Performance</strong> asks how the Target behaved across confirmed WSPR opportunities. It can reveal practical footprint, at-least-once reach, Decode Rate, successful signal levels, distance and direction structure, temporal behavior, and the breadth and depth of the supporting evidence.
* <strong class="defined-term">Benchmark</strong> asks how the Target behaved relative to a meaningful <strong class="defined-term">Reference</strong> under matched conditions. It can reveal paired Target-minus-Reference Delta SNR, joint and one-sided Decode Outcomes, how much evidence was pairable, and where and when the relative difference appeared.
````

</details>

### Original in 0.1 What WSPRadar can show

<details><summary>Verbatim baseline passage</summary>

````text
| Analysis | Question | Practical examples |
|---|---|---|
| <strong class="analysis-choice-single">RX Performance</strong> | How broadly and consistently does my receiver decode signals across confirmed opportunities? | Establish the receiving footprint of a newly commissioned antenna or station; see whether reception is broad but intermittent or narrower and consistent; identify recurring direction, distance or UTC-hour patterns, including periods that may warrant a separate check for local noise or intermittent hardware. |
| <strong class="analysis-choice-single">TX Performance</strong> | Where, when and how consistently is my transmitter decoded by receivers shown to be active? | Map where a QRP beacon or newly installed antenna is heard; see when and in which directions confirmed active receivers decode the station most consistently; establish a station baseline after commissioning, repair or relocation, and use comparable repeat runs to determine whether its observed behavior later changes. |
| <span class="analysis-choice"><span class="analysis-family">RX Benchmark</span><br><strong class="analysis-variant">Reference Setup/Station</strong></span> | Did two local receive paths differ while observing the same remote transmissions? | Compare two antennas, each feeding its own simultaneous receiver and decoder chain, as complete receive paths; attribute a difference specifically to the antennas only when the remaining chains are matched, characterized or confirmed by crossover; feed one antenna through a characterized splitter into two receivers to compare receiver or decoder paths; place a preamplifier, filter, feedline or common-mode choke in only one otherwise controlled path and benchmark the two documented complete receive paths. |
| <span class="analysis-choice"><span class="analysis-family">TX Benchmark</span><br><strong class="analysis-variant">Reference Setup/Station</strong></span> | Did two local transmit paths differ in the same WSPR cycles? | Feed two antennas from separate calibrated transmit chains and transmit simultaneously with synchronized cycles, distinguishable signals and adequate isolation; compare two feedlines, matching networks, filters or complete transmit paths while controlling actual power, timing and the remaining chain. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Reference Setup/Station</strong></span> | How does my complete station compare with one known station? | <strong>RX:</strong> compare your receiver with a known Buddy receiver while both observe the same remote transmitters in the same cycles; <strong>TX:</strong> compare your transmitter with a Buddy transmitter at the same remote receivers in the same cycles; repeat a stable, well-understood Buddy design as a relative whole-station baseline before and after documented station work, without treating the Buddy as an absolute calibrated standard. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Reference Neighborhood (Local Median)</strong></span> | How does my complete station compare with the observed nearby WSPR peers? | See whether your receive or transmit station is broadly above, near or below the cycle- and path-specific median of qualifying observed local peers inside the selected radius; commission a station when no single suitable Buddy Reference is available; identify directions, distances or UTC periods where the station departs from that contextual local baseline, while checking neighborhood membership and radius sensitivity. This compares complete stations under the observed conditions; it does not isolate antenna gain or rank all nearby stations. |
````

</details>

### Original in 0.2 What one run produces

<details><summary>Verbatim baseline passage</summary>

````text
A WSPRadar run produces a connected evidence package for one clearly bounded station question — not a universal score and not a leaderboard.
````

</details>

### Original in 0.2 What one run produces

<details><summary>Verbatim baseline passage</summary>

````text
A Performance run brings together practical reach, two complementary Decode Rate weightings, successful Target SNR, distance and direction structure, chronological change, recurring UTC-hour behavior, contributing stations and the underlying opportunities. A Benchmark run combines paired Delta SNR with Decode Outcomes and evidence coverage so that a favorable paired median cannot hide extensive one-sided evidence or a narrow pairable subset.
````

</details>

### Original in 0.2 What one run produces

<details><summary>Verbatim baseline passage</summary>

````text
Every result follows the same evidence path:
````

</details>

### Original in 0.2 What one run produces

<details><summary>Verbatim baseline passage</summary>

````text
The map provides the geographic overview. Segment-level evidence shows how the observation changes with distance and direction and how much support lies behind it. Performance or Benchmark Evidence separates the main result from its complementary evidence. Temporal Evidence shows whether the pattern changed during the run or recurred at particular UTC hours. Station Insights reveals which station identities contribute. Selected Station Evidence follows one exact radio path, and Drill-Down exposes the observations and same-cycle comparisons behind the summaries.
````

</details>

### Original in 0.2 What one run produces

<details><summary>Verbatim baseline passage</summary>

````text
This layered structure is one of WSPRadar's central strengths: the high-level pattern remains connected to its evidence. An operator can move from **where the effect appears**, through **how consistently it appears and how well it is supported**, down to **the individual observations from which the conclusion was built**.
````

</details>

### Original in 0.2 What one run produces

<details><summary>Verbatim baseline passage</summary>

````text
A credible result is therefore not simply the largest value on the screen. It is one in which the experiment design, geographic pattern, temporal behavior, station breadth, evidence depth and row-level audit support the same bounded interpretation. Repeating the design in another suitable operating window can then test whether the observation is experimentally repeatable rather than only internally consistent within one run.
````

</details>

### Original in 0.2 What one run produces

<details><summary>Verbatim baseline passage</summary>

````text
The complete run can also be preserved as a reproducibility package containing its analysis definition, processed evidence, tables, figures and metadata, ready to be reviewed later or shared with another operator alongside the physical station notes that WSPRadar cannot infer.
````

</details>

### Original in 0.3 Your first useful run

<details><summary>Verbatim baseline passage</summary>

````text
The quickest way to understand WSPRadar is to begin with a maintained demo. A demo presents a complete historical Performance or Benchmark analysis with a prepared experimental context, allowing the evidence path to be explored before your own station is involved.
````

</details>

### Original in 0.3 Your first useful run

<details><summary>Verbatim baseline passage</summary>

````text
The value of the demo becomes clear in the connection between its layers: the geographic overview, distance and direction, isolated versus recurring temporal behavior, the number and diversity of supporting stations, the pairability of Benchmark evidence, and the selected-path and row-level observations behind the summary.
````

</details>

### Original in 0.3 Your first useful run

<details><summary>Verbatim baseline passage</summary>

````text
A demo is a worked example of WSPRadar's method, not evidence about your own station. Once the evidence path is familiar, the most useful first analysis of your own station begins with one clear question: establish its RX or TX Performance baseline, compare two controlled local paths, benchmark against a known station, or place it in its local WSPR context.
````

</details>

### Original in 0.3 Your first useful run

<details><summary>Verbatim baseline passage</summary>

````text
The aim is not to produce a flattering number. It is to obtain a result you can understand, question, repeat and use to make a better-informed decision about the station.
````

</details>

### Original in Table of Contents

<details><summary>Verbatim baseline passage</summary>

````text
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
    * [7.11 Robust local-baseline Delta SNR event detection](#sec-7-11)
* [8. Evidence-Matched Claims and Reproducibility](#sec-8)
    * [8.1 Claim classes and evidence-matched wording](#sec-8-1)
    * [8.2 Interpretation boundaries](#sec-8-2)
    * [8.3 Reporting and reproducibility checklist](#sec-8-3)
    * [8.4 Analysis export package](#sec-8-4)
    * [8.5 Disclaimer](#sec-8-5)
* [References](#sec-ref)
````

</details>

### Original in Table of Contents

<details><summary>Verbatim baseline passage</summary>

````text
* [Appendix A: Parallel WSJT-X Instances for Simultaneous RX](#sec-a)
    * [A.1 Create the second instance](#sec-a-1)
    * [A.2 Clone the starting configuration if required](#sec-a-2)
    * [A.3 Separate every data path](#sec-a-3)
    * [A.4 Limitations of WSJT-X for simultaneous TX](#sec-a-4)
* [Appendix B: Simultaneous TX Reference Setup](#sec-simultaneous-tx-setup)
    * [B.1 Choose the callsigns](#sec-simultaneous-tx-setup-1)
    * [B.2 Align the schedule and separate the signals](#sec-simultaneous-tx-setup-2)
    * [B.3 Check power and simultaneous signal quality](#sec-simultaneous-tx-setup-3)
    * [B.4 Verify WSPRnet and the selected archive](#sec-simultaneous-tx-setup-4)
    * [B.5 Device-specific setup](#sec-simultaneous-tx-setup-5)
        * [B.5.1–B.5.2 QMX and QMX+ Virtual U3S, and Ultimate3S](#sec-simultaneous-tx-setup-5-1)
        * [B.5.3 ZachTek firmware 2.19 randomized split-lane builds](#sec-simultaneous-tx-setup-5-3)
    * [B.6 Confirm by exchange or crossover](#sec-simultaneous-tx-setup-6)
* [Appendix C: Reference SNR Calibration](#sec-reference-snr-calibration)
* [License](#sec-license)
````

</details>

### Original in Part I: Operator Guide

<details><summary>Verbatim baseline passage</summary>

````text
This part takes you from an operating question to an evidence-matched conclusion. Chapter 1 establishes the common experiment, selects RX or TX and Performance or Benchmark, and introduces the shared evidence path. Chapter 2 then follows that path within the exact analysis family and Reference design and closes with an optional expert diagnostic for temporary Delta SNR departures. Chapter 3 explains how to strengthen, report and preserve the result. Exact controls remain in Part II; exact calculations and scientific edge cases remain in Part III.
````

</details>

### Original in 1.1 Build a strong experiment foundation

<details><summary>Verbatim baseline passage</summary>

````text
A useful WSPRadar result begins with one sentence stating what is being tested and what observation would count as support. Decide whether the run is exploratory — intended to find a possible pattern — or confirmatory — intended to test a pattern already identified.
````

</details>

### Original in 1.1 Build a strong experiment foundation

<details><summary>Verbatim baseline passage</summary>

````text
Use one exact band and a UTC window in which the Target was operating. Enter callsigns exactly as uploaded and verify the Target QTH. Record the antenna, feedline, radio, tuner, gain or power settings, decoder, software version, schedule and any deliberate change. Keep every variable outside the question as stable as practical.
````

</details>

### Original in 1.1 Build a strong experiment foundation

<details><summary>Verbatim baseline passage</summary>

````text
For TX, keep actual and reported power accurate and stable unless power is the tested variable. For RX, keep gain, filtering, audio routing, decoder settings and upload behavior stable unless one of them is under test. Keep clocks synchronized. In Benchmark, verify that the Reference was operating as intended: the Target-Active Gate establishes observable Target participation but does not prove Reference uptime.
````

</details>

### Original in 1.1 Build a strong experiment foundation

<details><summary>Verbatim baseline passage</summary>

````text
Before a confirmatory repetition, fix the direction, band, Reference design, filters, thresholds, schedule and primary geographic or temporal scope. Treat alternative radii, time windows or scopes as separate sensitivity analyses rather than choosing only the version that looks most favorable.
````

</details>

### Original in 1.2 Choose the analysis that matches the question

<details><summary>Verbatim baseline passage</summary>

````text
| Operating question | Analysis |
|---|---|
| Which signals does my receiver decode across confirmed opportunities, where, when and how consistently? | **RX Performance** |
| Where and how consistently is my transmitter decoded by receivers shown to be active? | **TX Performance** |
| How do two local receive paths, two complete receiving stations, or my receiver and a local neighborhood Reference differ? | **RX Benchmark** |
| How do two local transmit paths, two complete transmitting stations, or my transmitter and a local neighborhood Reference differ? | **TX Benchmark** |
````

</details>

### Original in 1.2 Choose the analysis that matches the question

<details><summary>Verbatim baseline passage</summary>

````text
Choose **Performance** when the Target itself is the question and no Reference is required. Performance combines at-least-once reach, Decode Rate, successful Target SNR, geography, time and evidence support. It describes the complete Target station under the selected real-world conditions.
````

</details>

### Original in 1.3 Follow the evidence path

<details><summary>Verbatim baseline passage</summary>

````text
**Map.** Locate the broad distance and direction pattern. Read sector color together with the station and opportunity, spot or pair support. A colored sector is a prompt to inspect, not the conclusion.
````

</details>

### Original in 1.3 Follow the evidence path

<details><summary>Verbatim baseline passage</summary>

````text
**Performance or Benchmark Evidence.** In Performance, combine reach, both Decode Rate weightings and successful Target SNR. In Benchmark, combine station-balanced and observation-level Delta SNR, Decode Outcomes and Joint Evidence Share. These quantities answer different questions and should not be collapsed into one score.
````

</details>

### Original in 1.3 Follow the evidence path

<details><summary>Verbatim baseline passage</summary>

````text
**Temporal Evidence.** Use the chronological view to see when behavior changed during the run and the UTC-hour view to see whether a time-of-day pattern recurred across dates. Read signal-level evidence together with its station, opportunity or pair support.
````

</details>

### Original in 1.3 Follow the evidence path

<details><summary>Verbatim baseline passage</summary>

````text
**Drill-Down.** Verify the retained opportunities, same-cycle pairs behind a result. Use it to check identities, locator changes, timing, one-sided evidence and isolated outliers.
````

</details>

### Original in 2.5.3 Read and investigate a reported event

<details><summary>Verbatim baseline passage</summary>

````text
**Inspect the path next.** Two green actions appear to the right of each exact path timeframe. Both select the path, preload Drill-Down and open **`Outlier Focus`**:
````

</details>

### Original in 3.1 Judge breadth, consistency and repeatability

<details><summary>Verbatim baseline passage</summary>

````text
* participating station identities;
* qualifying confirmed-opportunity, Joint-Spot volume;
* agreement across stations;
* station-balanced and observation-level summaries;
* adjacent geographic segments;
* temporal views;
* Decode Outcomes;
* identity and locator quality;
* experiment control and repetition.
````

</details>

### Original in 3.1 Judge breadth, consistency and repeatability

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar deliberately does not collapse these dimensions into one proof grade. The visible counts, distributions and underlying rows let the operator judge the result in the context of the actual experiment.
````

</details>

### Original in 3.2 Strengthen a result through repetition and control

<details><summary>Verbatim baseline passage</summary>

````text
TX and RX use different peer populations and opportunity definitions. Compare like-for-like TX and RX runs when investigating station balance or an "alligator" pattern.
````

</details>

### Original in 3.3 Write an evidence-matched conclusion

<details><summary>Verbatim baseline passage</summary>

````text
A full technical report also states:
````

</details>

### Original in 3.3 Write an evidence-matched conclusion

<details><summary>Verbatim baseline passage</summary>

````text
* the applicable weighting levels: Station-balanced and Opportunity-level Decode Rate for Performance, or station-level and observation-level Delta SNR for Benchmark;
* qualifying-station and confirmed-opportunity counts for Performance, or joint-station and joint-spot/pair counts for Benchmark;
* Decode Outcomes for Benchmark;
* experiment conditions and any Reference correction;
* filters and evidence thresholds;
* whether the pattern repeated across time, stations or runs;
* any alternative radius or scope used as a sensitivity analysis.
````

</details>

### Original in 3.3 Write an evidence-matched conclusion

<details><summary>Verbatim baseline passage</summary>

````text
> For this Target, band, UTC window and selected peer population, the displayed Decode Rate describes the fraction of confirmed opportunities in which the Target also produced qualifying evidence. State whether the reported value is the Station-balanced Decode Rate or the Opportunity-level Decode Rate. Qualifying stations, confirmed opportunities, geographic scope and temporal views describe the breadth, depth and recurrence supporting that result.
````

</details>

### Original in 3.3 Write an evidence-matched conclusion

<details><summary>Verbatim baseline passage</summary>

````text
A complete Performance statement can additionally say whether at-least-once reach was broad or limited, whether participation was consistent or intermittent, where distance or directional patterns appeared, whether a UTC-hour pattern recurred and how successful Target SNR behaved. Describe these as observed WSPR behavior of the complete station under the selected conditions, not as isolated gain, sensitivity or efficiency.
````

</details>

### Original in 3.3 Write an evidence-matched conclusion

<details><summary>Verbatim baseline passage</summary>

````text
> For this Target, Reference, band, UTC window and selected segment, station-balanced Delta SNR favored the Target/Reference by the displayed amount. The observation-level Delta SNR, joint station and spot/pair counts, Joint Evidence Share and Decode Outcomes describe the supporting paired and one-sided evidence.
````

</details>

### Original in 3.4 Preserve the run and its context

<details><summary>Verbatim baseline passage</summary>

````text
Use `Prepare All Results for Download` to build the current analysis export package. It contains the current configuration, run metadata, processed evidence, tables and high-resolution figures.
````

</details>

### Original in 3.4 Preserve the run and its context

<details><summary>Verbatim baseline passage</summary>

````text
Preserve external notes alongside that package:
````

</details>

### Original in 3.4 Preserve the run and its context

<details><summary>Verbatim baseline passage</summary>

````text
* physical antenna and feedline arrangement;
* switch or splitter topology;
* transmitter or receiver hardware;
* power measurements and reporting basis;
* decoder and software versions;
* operating schedule, physical schedule-to-path mapping and any reversed assignment;
* calibration procedure;
* weather, faults or intentional changes relevant to the run.
````

</details>

### Original in Part II: Controls and Troubleshooting

<details><summary>Verbatim baseline passage</summary>

````text
Optional expert use of Benchmark Delta SNR outlier detection is introduced in [Section 2.5](#sec-outlier). Section 4.6 owns its controls; its formal scientific definition is in [Section 7.11](#sec-7-11).
````

</details>

### Original in 4.1 Workflow controls

<details><summary>Verbatim baseline passage</summary>

````text
**Demo data reuse.** Running an unchanged demo retrieves any missing database query results and stores validated rows on the app server's disk. Later runs reuse matching entries without automatic expiry, including across sessions and app restarts while that disk is retained. A changed query or incompatible cache format, or missing or damaged files, requires retrieval again. Starting the app or loading a demo does not preload its data. Reuse preserves the retrieved archive data rather than automatically incorporating later archive corrections; each run still performs the analysis with the current application code.
````

</details>

### Original in 4.2 Question, Target and measurement-window controls

<details><summary>Verbatim baseline passage</summary>

````text
| UI label | Default | What it controls |
|---|---|---|
| **Question** | none; required | One of `RX Performance`, `TX Performance`, `RX Benchmark` or `TX Benchmark`; sets direction and result type together. |
| **Target callsign (receiver under test)** / **Target callsign (transmitter under test)** | blank | Exact archive reporting identity. Standard callsigns, valid `/` variants, letter-only reporting identifiers and one optional terminal alphanumeric hyphen suffix are accepted. |
| **Target QTH (4 or 6 characters)** | blank | Target grid-4 matching, map center, geometry and local-radius origin. |
| **Operating Band** | `20m` | Exactly one of `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` or `23cm`. |
| **UTC measurement window** | fixed 24-hour window ending at the current UTC minute | The absolute evidence interval used by the run. |
| **Start Date/Time (UTC)** and **End Date/Time (UTC)** | the effective default window | Dates begin in 2008; one run is limited to 31 elapsed days. Entered times use minute precision and are preserved without rounding to 15-minute boundaries. |
````

</details>

### Original in 4.2 Question, Target and measurement-window controls

<details><summary>Verbatim baseline passage</summary>

````text
A four-character Maidenhead locator identifies a broad grid square; six characters identify a smaller subsquare. Performance and Benchmark select Target archive rows from the exact callsign plus the first four characters of Target QTH. The full configured QTH still anchors map, distance, azimuth, solar and local-neighborhood calculations.
````

</details>

### Original in 4.3 Benchmark-design controls

<details><summary>Verbatim baseline passage</summary>

````text
Classic omits the **`Benchmark design`** panel entirely for `RX Performance` and `TX Performance`, because Performance has no Reference. The terminal Review panel appears after the shared filters, scope and evidence panel. On Run, invalid or incomplete fields are marked locally with red feedback and corrective guidance; correcting a field clears its issue. Archive lookup failure is reported separately from an invalid callsign or an empty report window. Performance and Benchmark are mutually exclusive result types: one run produces only the selected result. [Section 8.4](#sec-8-4) summarizes selected public machine-readable configuration, URL and export names; it is not an exhaustive field or parameter catalog.
````

</details>

### Original in 4.3 Benchmark-design controls

<details><summary>Verbatim baseline passage</summary>

````text
| UI label | Default / range | Applies to | Scientific effect |
|---|---|---|---|
| **Is there an established Target–Reference offset?** | `No established offset — use 0.0 dB` | Guided Reference Setup/Station | Distinguishes no established correction, use of one established correction, and a deliberate offset-establishment run. |
| **Reference-side SNR correction (dB)** | blank = `0.0`; `-99.9` to `+99.9 dB` | Benchmark | Added to Reference SNR before Target-minus-Reference Delta SNR is calculated. Enter decimal points, for example `1.2`. |
| **Reference callsign** | blank | Reference Setup/Station | Exact Reference reporting identity. |
| **Reference location** | resolved from the selected archive | Reference Setup/Station | One observed grid-4 resolves automatically; choose explicitly when several are reported. No separate manual Reference locator is required. |
| **Neighborhood Radius (km)** | `100`; 10–250 km in 10 km steps | Reference Neighborhood | Defines the local Reference pool around Target QTH. |
````

</details>

### Original in 4.3 Benchmark-design controls

<details><summary>Verbatim baseline passage</summary>

````text
Enter only the exact Reference callsign; Target QTH is the sole manually entered analysis locator and remains the origin for map, distance, azimuth, solar and neighborhood geometry. Reference location discovery runs for the selected role, band, effective UTC window and archive. One observed grid-4 resolves automatically; multiple candidates require your choice and show their full locator variants, report counts and first/last report times. A successful lookup with no qualifying reports is distinct from a source error. The same archive supplies the ensuing analysis; a resolved grid-4 is retained with the saved analysis definition.
````

</details>

### Original in 4.3 Benchmark-design controls

<details><summary>Verbatim baseline passage</summary>

````text
Different reported grids can reflect separate sites or incorrect archive metadata; the reported locators do not prove which explanation applies. If no eligible Target reports match the entered Target QTH, review the inputs; the analysis origin is never changed automatically.
````

</details>

### Original in Reference-side SNR correction sign

<details><summary>Verbatim baseline passage</summary>

````text
A positive correction increases corrected Reference SNR and therefore reduces Target-minus-Reference Delta SNR. Enter a measured `target - reference` calibration offset with the same sign. For example, a common-input calibration of `+1.6 dB` is entered as `+1.6 dB`. [Section 7.5](#sec-7-5) defines the equations.
````

</details>

### Original in 4.4 Filters and evidence thresholds

<details><summary>Verbatim baseline passage</summary>

````text
| Control | Default | Applies to | Effect and use |
|---|---|---|---|
| **Exclude Special Callsigns Q, 0, 1** | Performance on; Benchmark off | all results | Excludes remote peer callsigns beginning with `Q`, `0` or `1`: transmitters in RX analyses and receivers in TX analyses. Target and Reference stations, including Reference Neighborhood reference contributors, remain eligible under this filter. The prefix rule does not establish whether a station carries telemetry. Retain beacon/telemetry-like identities when they are part of the question; exclude them when the intended population is ordinary amateur activity. |
| **Exclude Moving Stations** | Performance on; Benchmark off | mapped peers | Excludes callsigns reporting more than one grid-4 in the otherwise eligible global population. Use Drill-Down to distinguish movement from bad locator data. |
| **Solar state at Target QTH** | `All 24h` | all results | Keeps `Daylight (Elev > +6°)`, `Nighttime (Elev < -6°)`, `Greyline (-6° to +6°)` or all cycles according to Target-QTH solar elevation. |
| **Maximum peer distance from Target (km)** | `22000`; choices `2500`, `5000`, `10000`, `15000`, `20000`, `22000` | all results | Removes peers at or beyond the selected distance from analysis, processed artifacts and exports. Target-Active gating may still use out-of-scope evidence solely to establish Target operation. |
| **Minimum joint evidence per station** | `1`; range 1–50 | Benchmark | Requires repeated Joint peer-cycles before a station contributes paired Delta SNR; the same numeric floor also applies to exclusive categories. |
| **Minimum confirmed opportunities per station** | `5`; range 1–100 | Performance | Requires enough Target-plus-counter opportunities before a peer contributes. Low values increase coverage but make rates coarse and weakly supported. |
| **Minimum qualifying stations per map segment** | `1`; range 1–10 | all maps | Requires broader identity support before a segment is drawn. |
````

</details>

### Original in 4.4 Filters and evidence thresholds

<details><summary>Verbatim baseline passage</summary>

````text
`Maximum peer distance from Target (km)` limits the analysed population after the archive rows have been retrieved, so reducing it does not avoid the archive row limit. A smaller Reference Neighborhood radius and `Exclude Special Callsigns Q, 0, 1` can reduce the population retrieved for some analyses; [Section 5.6](#sec-6-6) covers oversized requests.
````

</details>

### Original in 4.5 Map, inspector and export controls

<details><summary>Verbatim baseline passage</summary>

````text
| Control | What it changes | Saved? | Reruns analysis? |
|---|---|---|---|
| Segment distance and direction | Active geographic inspection scope | Separately for Performance and Benchmark | No |
| `Heard only by other stations.` / `Only other signals heard.` | Visibility of Performance peers with only counter-evidence | Yes | No |
| `Include Unpaired Evidence` | Visibility of Benchmark identities represented only by exclusive or asynchronous evidence | Yes | No |
| Selected station row | Selected Station Evidence and selected Drill-Down identity | One exact `callsign + locator` per result type | No |
| Segment time aggregation | Chronological Segment Inspector temporal view; choices adapt to the run duration | Yes | No |
| Selected-station time aggregation | Chronological selected-path view; choices adapt to the run duration | Yes | No |
| **`Zoom window`**, **`Center date (UTC)`**, **`Center time (UTC)`**, **`← Earlier`**, **`Later →`**, **`Outlier Focus`** and **`Filter table`** | Optional native-time Drill-Down plots and centered table interval for exactly one selected station; table filtering affects displayed rows only | No | No |
| `Prepare All Results for Download` | Export package and current inspection selections | n/a | No |
````

</details>

### Original in 4.5 Map, inspector and export controls

<details><summary>Verbatim baseline passage</summary>

````text
Drill-Down zoom is transient and is available only for exactly one selected station. Choose **`Off`**, or a complete `1h`, `3h`, `6h`, `12h` or `24h` interval. **`Center date (UTC)`** and **`Center time (UTC)`** select the center of that interval; WSPRadar derives its exact start and end, moves the complete interval against a run boundary instead of shortening it, and lets **`← Earlier`** or **`Later →`** step by one complete selected window. The resolved bounds appear on one line as **`Selected window: {start} to {end} UTC`**. The zoom restricts the focused figures and Drill-Down table; **`Filter table`** then changes only the displayed table and never the focused plots or completed analysis. Its metric plot is deliberately not a two-minute aggregate: Benchmark shows one actual Delta SNR dot per retained Joint Spot at its canonical cycle time; Performance shows the actual normalized Target SNR of each successful confirmed opportunity at its canonical cycle time. These are individual retained scientific evidence units after WSPRadar's consolidation, matching and filters, not untouched provider rows. No bin median, IQR, density background, colorbar, full-run median or UTC-hour-folded metric panel is drawn in the focused view. The companion Performance outcome or Benchmark coverage view may retain its chronological aggregation, while Segment and full-window Selected Station Evidence remain density-based aggregated views. Focused figure titles use the compact format **`DG2CAD (JN47mv) - Time Window: {start} to {end} UTC`**.
````

</details>

### Original in 4.5 Map, inspector and export controls

<details><summary>Verbatim baseline passage</summary>

````text
An outlier action preloads **`Outlier Focus`** over the complete supported pre-event baseline flank, guarded provisional episode and post-event flank, clipped only to the completed analysis window and allowed to exceed 24 hours. Candidate provenance remains attached while the operator moves to a manual fixed window. In a focused Benchmark plot, identical `*` markers identify every native unit in the current window that individually meets both configured departure and robust-z gates as part of a reported candidate; a muted **Focused episode** band distinguishes the selected reported episode. The band covers its reported retained-evidence interval with half one native evidence-unit width of padding at each end, clipped to the focused window so an impulse remains visible. It is a selection cue rather than a confidence interval or physical-duration measurement. Expected local Delta SNR, time-limited pre/post flank baselines, robust-z guides at 1, 2 and 3 plus the configured qualifying threshold, and the configured absolute-departure boundary belong only to the focused episode; other starred candidates can have different baselines and robust spreads. Robust-z and departure lines are detector guides rather than confidence intervals; crossing one line alone does not satisfy the detector's separate support, stability, event and agreement requirements. Manual and outlier-linked focus state stay outside the analysis definition, saved configuration and public URL. When focus is active, the export can add its separate figures without replacing the ordinary full-run selected-station figures. Export contents are defined in [Section 8.4](#sec-8-4).
````

</details>

### Original in 4.6 Benchmark outlier-detection controls

<details><summary>Verbatim baseline passage</summary>

````text
Benchmark Delta SNR outlier detection is an optional expert analysis over retained native paired evidence. A native paired unit is a simultaneous **Joint Spot**. Detection runs separately for every exact peer `callsign + locator` path and is independent of the selected Temporal Evidence display bin. One-sided evidence cannot supply a missing Delta SNR. [Section 2.5](#sec-outlier) explains operation and interpretation; [Section 7.11](#sec-7-11) defines the method formally.
````

</details>

### Original in 5.2 Diagnose by symptom

<details><summary>Verbatim baseline passage</summary>

````text
| Symptom | Next checks |
|---|---|
| **No exact Target/source evidence was returned** | Check exact identity/QTH/band/window, actual operation, strict `code = 1` or historical-fallback status, and upstream availability. This is an input/source-evidence state, not evidence that configured filters were too narrow. |
| **Source evidence was returned, but filters or scope retained none** | Review the displayed station exclusions, solar state and maximum peer distance together with the completed run window. The notice says only that the applied filters and scope left no retained evidence; sparse operation or coverage can also contribute. |
| **Performance identities remain, but no station meets the confirmed-opportunity requirement** | Compare the displayed observed station count and highest confirmed-opportunity count with the configured minimum confirmed opportunities per station. Empty maps, Inspectors and tables are omitted rather than displayed as zero-valued results. |
| **Performance stations qualify, but no map segment meets its station requirement** | Keep and inspect the available station-level evidence. Only segment-dependent output is absent; compare its station support with the configured minimum qualifying stations per map segment. |
| **No qualifying Benchmark result remains** | Review the configured Joint-evidence requirement, minimum qualifying stations per map segment, filters and scope. WSPRadar reports those applied requirements but does not invent observed Benchmark maxima that the pipeline did not calculate. |
| **Benchmark has no Delta SNR** | Check shared remote peers in overlapping cycles, Reference uptime, clocks, schedule mapping, joint threshold, filters and scope. |
| **Benchmark has Delta SNR but little pairable evidence** | Read Joint Evidence Share and Decode Outcomes; check Reference uptime, power, thresholds, scope and whether the paired subset represents the wider station population. |
| **Performance has very few peers** | Check independent network activity, minimum confirmed opportunities, exclusions, solar state, time window and maximum peer distance. |
| **Many Performance successes lack external confirmation** | A valid Target decode itself confirms both endpoints. These Target-only successes enter Decode Rate once; their separate provenance count is not added again. Without a Target decode or the required external endpoint-activity evidence, the peer-cycle remains unknown and excluded. |
| **`Only Reference = 0`** | Check Target-active conditioning, thresholds and active scope; zero can be correct. |
| **Unexpected Reference Setup/Station Delta SNR sign** | Verify physical A/B mapping, Target/Reference order, correction sign, actual/reported power and calibration. Reconcile one path in Drill-Down. |
| **Local result changes with radius** | Inspect local contributors and report radius sensitivity rather than selecting only the most favorable radius. |
| **Run stops because the source result is too large** | Shorten the UTC window. `Exclude Special Callsigns Q, 0, 1` or a smaller Reference Neighborhood radius can reduce relevant source queries; maximum peer distance cannot because it is applied after retrieval. |
| **Recent spots appear incomplete** | Allow about five minutes after the final cycle, then check upload and upstream status. |
````

</details>

### Original in 5.3 Callsign and locator checks

<details><summary>Verbatim baseline passage</summary>

````text
Performance and every Benchmark design match Target archive rows by exact callsign plus Target QTH grid-4. A Target uploading `JN37` while configured as `JN38` does not match.
````

</details>

### Original in 5.3 Callsign and locator checks

<details><summary>Verbatim baseline passage</summary>

````text
Reference Setup/Station uses the exact Reference callsign plus the grid-4 resolved from the selected archive period. Discovery uses the Reference role (RX or TX), band, effective UTC window and selected data source. One reported grid-4 resolves automatically; several require an explicit choice. Full reported locator variants, report counts and first/last report times support that choice. The location is an archive selector, not a verified physical site. Reference Neighborhood selects its contributors geographically.
````

</details>

### Original in 5.3 Callsign and locator checks

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar does not reconstruct a compound callsign from Type 2 and Type 3 messages and does not infer a missing locator. Check the selected data source for both exact identities and their intended reported grid-4 values. If one identity is missing, appears only without the required locator, or is stored under a different grid-4, simultaneous Reference Setup/Station cannot match it merely because another archive or map display looks correct.
````

</details>

### Original in 5.4 Historical decode-code fallback

<details><summary>Verbatim baseline passage</summary>

````text
WSPR-2 is the standard WSPR mode with two-minute transmission cycles; `code` is the database's recorded mode information. Older archive records may have missing or ambiguous mode information, and historical compatibility can include observations whose physical transmission mode cannot be established. The cutoff is a compatibility policy, not a verified date when all archive mode information became reliable. Historical `code = 1` itself can also be ambiguous [Ref-10]. Run status and exported `decode_filter_mode` document the query selection without proving that every selected observation is WSPR-2. When a period is ineligible for fallback and the strict query has no Target-side evidence, WSPRadar explains the WSPR-2 filter and historical cutoff; this does not prove that the Target used another mode.
````

</details>

### Original in 5.6 Working with upstream data

<details><summary>Verbatim baseline passage</summary>

````text
Public WSPR archives can contain duplicates, false spots, incorrect locators or power values, delayed uploads and later corrections. wspr.live describes fresh data as arriving after a delay of a few minutes; waiting about **five minutes** after the final cycle is a practical estimate, not a completeness guarantee <a href="#ref-10">[Ref-10]</a>.
````

</details>

### Original in 5.6 Working with upstream data

<details><summary>Verbatim baseline passage</summary>

````text
| Status element | Meaning |
|---|---|
| **Data source** | The single upstream archive used for the completed run. Evidence from different archives is not combined within one run. |
| **Historical fallback** | Whether source selection was repeated without the strict WSPR-2 decode-code condition. |
````

</details>

### Original in 5.6 Working with upstream data

<details><summary>Verbatim baseline passage</summary>

````text
An archive retrieval larger than 1,000,000 complete rows is rejected before analysis rather than silently truncated. Shorten the window or use a relevant archive-side population filter as described in [Section 5.2](#sec-6-2).
````

</details>

### Original in Part III: Scientific Foundations, Methods and Claims

<details><summary>Verbatim baseline passage</summary>

````text
Part III is the scientific methods reference for technically critical radio amateurs, HamSCI contributors and reviewers. It defines the observational data, analysis targets, constructed evidence units, descriptive summaries, conditioning, missingness, weighting, dependence, transformations and reproducibility boundaries behind WSPRadar. It is intentionally more formal than the operator guide.
````

</details>

### Original in 6. Literature, Prior Art and Positioning

<details><summary>Verbatim baseline passage</summary>

````text
This chapter is a focused methodological review, not a systematic or exhaustive literature search. Peer-reviewed articles, preprints, amateur technical reports and software documentation support different kinds of claims; each source is used only for the contribution it actually demonstrates. The review does not imply that prior literature validates every WSPRadar metric or methodological choice.
````

</details>

### Original in 6.1 From reporting network to experimental dataset

<details><summary>Verbatim baseline passage</summary>

````text
Taylor and Walker presented WSPRnet not merely as a live map but as an archive: “The WSPRnet database represents a rich source of experimental data for propagation studies.” Their example groups observations by time of day over several weeks, illustrating both the value of accumulated reports and the need to interpret them as observational rather than controlled laboratory data. <a href="#ref-6">[Ref-6]</a>
````

</details>

### Original in 6.1 From reporting network to experimental dataset

<details><summary>Verbatim baseline passage</summary>

````text
The WSPR archive therefore combines unusual temporal depth and geographic reach with heterogeneous stations, successful-decode selection, user-supplied identities and powers, changing equipment and generally unknown operating schedules. These properties motivate explicit eligibility and conditioning rather than direct interpretation of spot absence.
````

</details>

### Original in 6.2 Making observational WSPR data interpretable

<details><summary>Verbatim baseline passage</summary>

````text
That activity-check principle is direct prior art for WSPRadar's Target-Active Gate and confirmed opportunities: silence should not become counter-evidence until relevant operation is observable. Lo et al. do not define WSPRadar's asymmetric Target conditioning, Performance analysis target, station balancing, Decode Outcomes or local References; those remain WSPRadar design choices for different analysis questions.
````

</details>

### Original in 6.3 Antenna and station-comparison lineage

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-d-toledo"></a>
**Toledo (2010): why slow alternation fails.** Sivan Toledo tested one antenna for roughly an hour and then another, finding path-SNR changes comparable with the apparent antenna difference. He concluded that this naive design could not isolate the antennas and proposed per-cycle switching or simultaneous transmissions with separate hardware. WSPRadar supports the same-cycle alternative; its analysis does not pair different transmission cycles. <a href="#ref-3">[Ref-3]</a>
````

</details>

### Original in 6.3 Antenna and station-comparison lineage

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-d-milazzo"></a>
**Milazzo (2011): operator-led end-to-end comparison.** Carol Milazzo compared two stations 29 km apart through one receiver 1,750 km away, corrected reported SNR for transmit-power differences, compared the trend with VOACAP, noted unequal duty cycles and examined reciprocal RX reports. The case study demonstrates the practical value of common-receiver WSPR comparison while also showing the limits imposed by different QTHs, hardware, local noise, a single selected receiver and no formal uncertainty analysis. <a href="#ref-4">[Ref-4]</a>
````

</details>

### Original in 6.3 Antenna and station-comparison lineage

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels and Lamy (2022): conditioned simultaneous RX.** Their peer-reviewed experiment conditioned two nominally identical 160 m WSPR receiver stations and compared common remote transmissions simultaneously. This is the strongest direct precedent in this review set for controlled RX comparisons and for characterizing receive-chain offsets before interpreting antenna differences. Their propagation results also show that polarization and ionospheric effects remain coupled to reported SNR. <a href="#ref-2">[Ref-2]</a>
````

</details>

### Original in 6.3 Antenna and station-comparison lineage

<details><summary>Verbatim baseline passage</summary>

````text
Zander reports about 1,000 observations per preliminary experiment, of which roughly 150–200 joint reports from 15–35 receivers were retained, with sample standard deviation near 3 dB. The paper's sub-dB statement concerns precision of an arithmetic mean under its model and sample assumptions, not traceable total accuracy. Geographic sampling, antenna directivity and unknown elevation angles remain systematic limitations. The study supports simultaneous same-receiver Delta SNR, but not station-balanced medians, Decode Outcomes or neighborhood References.
````

</details>

### Original in 6.4 Analysis infrastructure and related tools

<details><summary>Verbatim baseline passage</summary>

````text
Griffiths and Robinett demonstrated a relational time-series self-join for the same transmitter, time and band reported by two receivers, together with SNR-difference plots, medians, quartiles, time heatmaps, distance/azimuth views and export. This is important precedent for inspectable comparison infrastructure, not for WSPRadar's exact eligibility, conditioning or summary statistics. <a href="#ref-13">[Ref-13]</a>
````

</details>

### Original in 6.4 Analysis infrastructure and related tools

<details><summary>Verbatim baseline passage</summary>

````text
These systems establish substantial prior art in data acquisition, exploration, ranking, comparison, mapping and reporting. WSPRadar's positioning therefore rests on its integrated experiment definitions, conditional populations, hierarchical weighting, complementary paired/one-sided evidence and audit path — not on being the first WSPR analysis tool.
````

</details>

### Original in 6.5 What WSPRadar inherits, integrates and adds

<details><summary>Verbatim baseline passage</summary>

````text
* Performance based on confirmed opportunities;
* Reference Setup/Station and dynamic Reference Neighborhoods;
* same-cycle matching;
* reported-power normalization and optional Reference-side correction;
* paired Delta SNR separated from one-sided Decode Outcomes;
* station-balanced and observation-level summaries;
* map-to-segment-to-station-to-row audit; and
* versioned configuration, processed evidence and reproducibility export.
````

</details>

### Original in 6.5 What WSPRadar inherits, integrates and adds

<details><summary>Verbatim baseline passage</summary>

````text
This is a bounded integration and methods claim, not a global priority claim. Median aggregation itself is not novel. WSPRadar should be described as a structured experimental and audit layer above a spot browser, not as a substitute for the upstream archives, other analysis tools or calibrated RF measurement.
````

</details>

### Original in 7. Scientific Methods

<details><summary>Verbatim baseline passage</summary>

````text
This chapter defines the scientific contract of a WSPRadar run. WSPRadar starts from reported observations, constructs eligible evidence units, derives quantities such as normalized SNR and paired Delta SNR, and then calculates descriptive summaries. Those summaries are exact for the retained evidence under the selected rules. They become estimates of a broader or future population only if an additional sampling and dependence model is supplied; WSPRadar does not make that inferential step automatically.
````

</details>

### Original in 7. Scientific Methods

<details><summary>Verbatim baseline passage</summary>

````text
1. **Reported observations:** uploaded WSPR spots with callsigns, locators, power, time and SNR.
2. **Constructed evidence units:** qualifying opportunities, peer-cycles, Joint units formed by WSPRadar’s eligibility and matching rules.
3. **Derived quantities:** normalized SNR, Decode Outcomes and Target-minus-Reference Delta SNR for an individual evidence unit.
4. **Descriptive summaries:** rates, medians, reach, evidence shares and temporal or geographic summaries calculated from the retained evidence.
5. **Interpretation beyond the run:** statements about future behavior, a wider population or a physical cause. Such generalization requires additional assumptions and experimental control; the calculation alone is not sufficient.
````

</details>

### Original in 7. Scientific Methods

<details><summary>Verbatim baseline passage</summary>

````text
| Design | Lowest comparison unit | Conditioning / eligibility | Principal summary | Primary boundary |
|---|---|---|---|---|
| RX Performance | one remote-transmitter peer-cycle | Target RX active; peer TX decoded by Target RX or another eligible RX | peer Decode Rate, then equal-peer mean; pooled opportunity rate retained | conditional observability, not calibrated sensitivity |
| TX Performance | one remote-receiver peer-cycle | Target TX active; peer RX decodes Target TX or another qualifying same-band TX | peer Decode Rate, then equal-peer mean; pooled opportunity rate retained | conditional observability, not all attempted transmissions |
| RX Reference Setup/Station | one remote-transmitter peer-cycle | Target active; both receivers report the same transmitter-cycle for Delta SNR | station median Delta SNR, then median across stations | complete receive paths unless chains are controlled |
| TX Reference Setup/Station | one remote-receiver peer-cycle | Target active; same receiver-cycle for paired Delta SNR | station median Delta SNR, then median across stations | power, chain and joint-decode selection |
| Reference Neighborhood (Local Median) | one Target/local-Reference peer-cycle | Target active; one contribution per active local identity | local median Reference, then station/segment Delta medians | changing uncalibrated membership |
````

</details>

### Original in 7.1 Data source, observation units and time model

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar reads public WSPR reports from one selected read-only archive for each completed run. Reports are observational records produced by heterogeneous transmitters, receivers, decoders and reporting systems. A completed run does not combine data sources; the selected archive belongs to the run provenance.
````

</details>

### Original in 7.1 Data source, observation units and time model

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar does not classify a row as Type 1, Type 2 or Type 3 and does not join complementary extended-WSPR transmissions across cycles. Each archive row belongs to its reported cycle. In same-cycle TX Benchmark, the resolved Target and Reference rows must therefore occur in the same cycle; aligned Type 2 phases can pair with each other and aligned Type 3 phases can pair with each other, but WSPRadar never crosses from one phase or cycle to the next.
````

</details>

### Original in 7.1 Data source, observation units and time model

<details><summary>Verbatim baseline passage</summary>

````text
Same-cycle matching means the same two-minute UTC archive slot and exact remote callsign plus full reported locator on the same band. It does not require identical RF frequencies or prove equal physical propagation paths; simultaneous TX signals normally need distinct clear frequencies. Only Joint evidence supplies Delta SNR. One-sided evidence and station-level Both (Async) remain available without an invented missing-side SNR.
````

</details>

### Original in 7.1 Data source, observation units and time model

<details><summary>Verbatim baseline passage</summary>

````text
Historical `code = 1` fallback changes the source-row selection only when the strict request has no Target-side evidence and the entire selected period ends before 1 January 2022 at 00:00 UTC. Run status records which source path was used. The eligibility boundary and historical mode uncertainty are described in [Section 5.4](#sec-6-4). Upstream delay and data-quality limitations are described in [Section 5.6](#sec-6-6).
````

</details>

### Original in 7.2 Identity, matching and row consolidation

<details><summary>Verbatim baseline passage</summary>

````text
Target archive selection uses grid-4 even when a six-character QTH is configured. The full QTH remains relevant to distance, azimuth, solar elevation and local-radius geometry. A matching grid-4 does not prove physical co-location.
````

</details>

### Original in 7.2 Identity, matching and row consolidation

<details><summary>Verbatim baseline passage</summary>

````text
This matching uses the exact callsign and locator fields supplied by the selected archive. WSPRadar neither reconstructs a compound callsign from its hash nor borrows a locator from a neighboring Type 2 or Type 3 cycle. A simultaneous extended-WSPR sequence can therefore contribute one same-phase comparison unit in each aligned cycle when both archive sides resolve consistently; a missing or differently represented callsign/grid-4 does not become eligible by inference.
````

</details>

### Original in 7.2 Identity, matching and row consolidation

<details><summary>Verbatim baseline passage</summary>

````text
This best-report interpretation is consistent with WsprDaemon's documented multi-receiver merging: when several receivers contribute reports for the same transmission, it reports the best SNR to WSPRnet. This is a reporting precedent, not proof that a particular archived report represents the intended signal or that both comparison endpoints selected the same spectral component. <a href="#ref-11">[Ref-11]</a>
````

</details>

### Original in 7.3 Target-active conditioning and eligibility

<details><summary>Verbatim baseline passage</summary>

````text
Performance and Benchmark condition on $A_c=1$. This protects known Target downtime from becoming automatic counter-evidence, but it changes the analysis population: the result describes cycles in which Target participation was observable, not all clock time or all planned attempts.
````

</details>

### Original in 7.3 Target-active conditioning and eligibility

<details><summary>Verbatim baseline passage</summary>

````text
The conditioning is asymmetric. Reference uptime is not a second gate and must be controlled or documented externally. Swapping Target and Reference can therefore change eligible cycles and one-sided Decode Outcomes even when the sign of Joint-only Delta SNR reverses as expected.
````

</details>

### Original in 7.3 Target-active conditioning and eligibility

<details><summary>Verbatim baseline passage</summary>

````text
Every Joint observation already implies Target participation, so the gate does not change Joint-only Delta SNR values. It changes the population of one-sided/asynchronous outcomes and, in Performance, the opportunity denominator.
````

</details>

### Original in 7.4 Performance analysis target, classification and summary statistics

<details><summary>Verbatim baseline passage</summary>

````text
For one qualifying peer:
````

</details>

### Original in 7.4 Performance analysis target, classification and summary statistics

<details><summary>Verbatim baseline passage</summary>

````text
For geographic scope $g$ with qualifying peer set $I_g$, the **Station-balanced Decode Rate** is:
````

</details>

### Original in 7.4 Performance analysis target, classification and summary statistics

<details><summary>Verbatim baseline passage</summary>

````text
Reach is a breadth measure and normally increases with observation duration. It does not describe how consistently those peers were decoded; Decode Rate answers that separate question.
````

</details>

### Original in 7.4 Performance analysis target, classification and summary statistics

<details><summary>Verbatim baseline passage</summary>

````text
Successful Target SNR is defined only where the Target was decoded/reported, including Target-only successes. It is therefore a success-conditioned distribution. Its medians, IQR and extremes use all retained successes after unchanged strongest-report consolidation and normalization. The same classification supplies station thresholds, both Decode Rate weightings, maps, Peer Reach, chronological and folded profiles, Station Insights, Selected Station Evidence, Drill-Down and exports. Missed opportunities have no Target SNR and no synthetic value. Decode Rate and successful SNR must be interpreted jointly because a system that adds marginal decodes can show lower successful-SNR summaries while improving practical reach.
````

</details>

### Original in 7.5 Power normalization, correction and Benchmark Delta SNR

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-7-5"></a>
#### 7.5 Power normalization, correction and Benchmark Delta SNR
````

</details>

### Original in 7.5 Power normalization, correction and Benchmark Delta SNR

<details><summary>Verbatim baseline passage</summary>

````text
WSPR reports SNR on the WSJT scale in dB relative to a 2500 Hz reference bandwidth and carries reported transmit power in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar normalizes successful TX-side SNR to reported 30 dBm:
````

</details>

### Original in 7.5 Power normalization, correction and Benchmark Delta SNR

<details><summary>Verbatim baseline passage</summary>

````text
In practical terms, a signal with `10 dB` less reported transmit power is raised by `10 dB` for this comparison. For example, an SNR reported as `-15 dB` at `20 dBm` is normalized to `-5 dB` at `30 dBm`. In words, the reported transmit-power difference is removed by expressing every successful TX-side SNR as though the reported power had been `30 dBm`. This removes only the **reported** power term. It does not correct antenna gain, radiation efficiency, feedline loss, EIRP, receiver calibration or local noise.
````

</details>

### Original in 7.5 Power normalization, correction and Benchmark Delta SNR

<details><summary>Verbatim baseline passage</summary>

````text
For a paired observation:
````

</details>

### Original in 7.5 Power normalization, correction and Benchmark Delta SNR

<details><summary>Verbatim baseline passage</summary>

````text
Here $C_R$ is the signed additive Reference-side correction. In the first equation, $SNR_R$ and $SNR_{R,corr}$ denote Reference SNR before and after correction. In the paired equation, the indices $i,c$ identify the peer and matched evidence unit; $SNR_{T,i,c}$ is the corresponding normalized Target SNR and $SNR_{R,corr,i,c}$ is the corrected Reference SNR. This is simply corrected Target SNR minus corrected Reference SNR for one matched evidence unit. Positive $D_{i,c}$ favors the Target; negative favors the Reference. A positive correction makes the Reference stronger before subtraction and therefore lowers Delta SNR. The entered calibration offset uses the same `target - reference` sign.
````

</details>

### Original in 7.6 Paired evidence, Decode Outcomes and missingness

<details><summary>Verbatim baseline passage</summary>

````text
1. the distribution of Target-minus-Reference Delta SNR among **Joint** comparison units; and
2. the composition of retained evidence into **Only Target**, **Joint**, **Only Reference** and, at identity level, **Both (Async)**.
````

</details>

### Original in 7.6 Paired evidence, Decode Outcomes and missingness

<details><summary>Verbatim baseline passage</summary>

````text
Delta SNR exists only when both sides produce comparable evidence. The Joint subset is therefore selected on successful observation of both sides. This paired selection is not missing at random in the ordinary statistical sense: weak signals, collisions, QRM, decoder behavior, power differences and path conditions can affect whether a pair exists.
````

</details>

### Original in 7.6 Paired evidence, Decode Outcomes and missingness

<details><summary>Verbatim baseline passage</summary>

````text
Extended-WSPR Type 3 rows identify a compound callsign through a 15-bit hash. QRP Labs documented a rare archive corruption or misassociation mechanism involving this limited hash space <a href="#ref-19">[Ref-19]</a>. If the affected rows are a tiny, non-clustered fraction among tens of thousands of observations, robust median readings will ordinarily be unchanged or nearly unchanged. Dataset size alone is not protection, however: a systematic, clustered or Target/Reference-asymmetric artifact can still change Joint coverage, one-sided outcomes, individual station medians or a narrow segment. WSPRadar can check whether the configured exact callsign and grid-4 are present in the selected archive; it cannot prove that every upstream hash association was physically correct. The archive preflight and phase-specific audit in [Appendix B](#sec-simultaneous-tx-setup) are therefore required when compound callsigns are used.
````

</details>

### Original in 7.6 Paired evidence, Decode Outcomes and missingness

<details><summary>Verbatim baseline passage</summary>

````text
One-sided evidence has no missing-side SNR to reconstruct. It cannot be assigned an artificial Delta SNR and is not power-normalized as a pair. In TX Benchmark, unequal actual or reported powers can strongly affect one-sided outcomes even when Joint Delta SNR is normalized.
````

</details>

### Original in 7.6 Paired evidence, Decode Outcomes and missingness

<details><summary>Verbatim baseline passage</summary>

````text
`Both (Async)` means that an identity has retained evidence from both sides but lacks a qualifying same-cycle pair for the relevant station category. It indicates broader two-sided participation without contributing paired Delta SNR.
````

</details>

### Original in 7.6 Paired evidence, Decode Outcomes and missingness

<details><summary>Verbatim baseline passage</summary>

````text
Successful-SNR censoring in Performance and Joint-decode selection in Benchmark are distinct selection processes. WSPRadar exposes Decode Outcomes and Joint Evidence Share so the paired Delta-SNR summary can be read against the wider retained evidence rather than treated as the complete station population.
````

</details>

### Original in 7.7 Aggregation hierarchy and weighting

<details><summary>Verbatim baseline passage</summary>

````text
| Peer identity | Retained Delta SNR values (dB) | Peer median (dB) |
|---|---|---:|
| A | +6, +6, +6, +6, +6, +6 | +6 |
| B | -2, -2 | -2 |
| C | -1, -1 | -1 |
````

</details>

### Original in 7.7 Aggregation hierarchy and weighting

<details><summary>Verbatim baseline passage</summary>

````text
For every Benchmark design, a station is one exact `callsign + full reported locator` identity for both weighting and segment support. Each identity must separately meet the configured minimum Joint-evidence count. The identities contributing one peer median each are exactly the identities counted toward the minimum qualifying stations per map segment. Identities with only one-sided evidence do not contribute to this Delta-SNR support count. The same callsign at different full locators counts separately, including two locators in the same grid-4. This counts reported path identities; it does not establish independent physical stations or sites.
````

</details>

### Original in 7.7 Aggregation hierarchy and weighting

<details><summary>Verbatim baseline passage</summary>

````text
For each remote peer-cycle, WSPRadar first calculates one normalized SNR contribution per active local `callsign + locator`, then takes the exact median across contributing local identities. An absent local identity is omitted rather than assigned zero. Reference correction is applied before the local pool is aggregated. The Target is compared with this cycle/path median, after which peer and segment Delta-SNR medians are calculated.
````

</details>

### Original in 7.7 Aggregation hierarchy and weighting

<details><summary>Verbatim baseline passage</summary>

````text
There is no separate minimum number of local contributors per peer-cycle. With one contributor, the Reference equals that contributor’s value. With no contributors, no Reference SNR or paired Delta SNR is available. The minimum joint-evidence and station-support requirements elsewhere in the analysis do not impose a minimum neighborhood size.
````

</details>

### Original in 7.8.1 Geographic summaries

<details><summary>Verbatim baseline passage</summary>

````text
Benchmark geographic summaries use one peer median Delta SNR per qualifying identity and then the segment median of those peer medians. Observation-level Delta SNR remains available as a separately weighted distribution.
````

</details>

### Original in 7.8.2 Benchmark evidence coverage

<details><summary>Verbatim baseline passage</summary>

````text
The first gives every contributing peer equal weight; the second gives every retained comparison unit equal weight. Joint Evidence Share measures pairability — the fraction of retained evidence that can contribute Delta SNR. It is not a Target win rate.
````

</details>

### Original in 7.8.2 Benchmark evidence coverage

<details><summary>Verbatim baseline passage</summary>

````text
Under the Target-Active Gate, Only Target and Only Reference are directional and asymmetric. One-sided evidence still has no Delta SNR.
````

</details>

### Original in 7.8.3 Temporal summaries and UTC folding

<details><summary>Verbatim baseline passage</summary>

````text
Chronological views preserve the actual sequence of the run across the full selected UTC window using the selected time-bin width. Bins begin at the selected start; the final interval may be shorter, and intervals without evidence remain blank rather than becoming 0 dB. UTC-hour views fold evidence from represented dates onto fixed one-hour slots to describe recurring time-of-day structure.
````

</details>

### Original in 7.8.3 Temporal summaries and UTC folding

<details><summary>Verbatim baseline passage</summary>

````text
For Performance successful-SNR deviation, a peer enters the anomaly population only when it has at least three successful normalized Target-SNR observations in the complete run window. Its baseline is the median of those successes. Each successful observation contributes:
````

</details>

### Original in 7.8.3 Temporal summaries and UTC folding

<details><summary>Verbatim baseline passage</summary>

````text
Chronologically, each peer contributes at most one median anomaly per selected bin. In the UTC-folded view, each peer contributes one median per date and UTC hour before those peer-date-hour values are summarized across the folded population. This prevents prolific peers or dates from dominating through raw row count.
````

</details>

### Original in 7.8.3 Temporal summaries and UTC folding

<details><summary>Verbatim baseline passage</summary>

````text
Benchmark temporal Delta SNR uses retained Joint observations. If no paired values remain, the Delta SNR panel still shows the full selected UTC window and states that paired Δ SNR evidence is absent. This means no retained Joint observation remains in the displayed scope; it does not by itself mean that the data source returned no observations, and temporal coverage can still show one-sided outcomes. Chronological bins summarize raw paired values in actual time; UTC-hour bins summarize the same paired population by hour across dates represented by retained Benchmark evidence. Benchmark temporal coverage uses all retained Only Target, Joint and Only Reference units and the two Joint Evidence Share summaries above. Benchmark folding likewise requires at least two represented evidence dates.
````

</details>

### Original in 7.8.4 Selected-path summaries

<details><summary>Verbatim baseline passage</summary>

````text
With one peer, station-balanced and Opportunity-level Decode Rate are numerically identical within a populated bin; the separate support counts still distinguish path presence from evidence volume.
````

</details>

### Original in 7.8.4 Selected-path summaries

<details><summary>Verbatim baseline passage</summary>

````text
For Benchmark, the selected path reports observation-level Delta SNR for each Joint unit and separately reports Only Target, Joint and Only Reference coverage. Changing the selected path or display bin changes only the retained-evidence view, not matching, eligibility or aggregation upstream.
````

</details>

### Original in 7.8.4 Selected-path summaries

<details><summary>Verbatim baseline passage</summary>

````text
Drill-Down can temporarily restrict this same selected-path evidence to one centered `1h`, `3h`, `6h`, `12h` or `24h` interval before ordinary table filters run. Its focused metric recipe retains one scientific unit at its native coordinate: one consolidated Joint Spot and actual Delta SNR at canonical cycle UTC for Benchmark; or one successful confirmed opportunity and actual normalized Target SNR at canonical cycle UTC for Performance. Thus “native” describes processed retained evidence after consolidation, matching and scientific filters, not untouched provider rows. The focused metric recipe contains neither temporal-bin medians or quartiles nor a density grid, colorbar, full-run median or folded profile. Companion outcome/coverage panels may retain their chronological aggregation, and the segment and full-window selected-path recipes remain unchanged density summaries.
````

</details>

### Original in 7.8.4 Selected-path summaries

<details><summary>Verbatim baseline passage</summary>

````text
Candidate-linked **`Outlier Focus`** uses the full retained pre-event flank, guarded provisional episode and post-event flank and may exceed 24 hours. The Benchmark overlay uses the already completed detector model rather than redetecting from the focused subset. For every reported candidate intersecting the focus window, it marks with the same `*` each native unit that individually meets both $D_{\min}$ and $Z_{\min}$ against that candidate's final baseline and robust spread; weaker grouped units retained between strong anchors remain ordinary dots. A muted **Focused episode** band distinguishes the selected candidate's reported retained-evidence interval. The renderer pads each end by half one native evidence-unit width and clips the band to the focused window, making a one-unit impulse visible without representing unobserved physical duration or a confidence interval. Expected local Delta SNR across the focus, the pre/post flank medians over their respective support intervals, symmetric guide boundaries for robust-z magnitudes 1, 2, 3 and $Z_{\min}$, and the absolute-departure boundary $D_{\min}$ all belong only to that focused episode; another starred candidate can have a different baseline and robust spread. From the detector definition in [Section 7.11](#sec-7-11), a guide of magnitude `k` lies at the local baseline plus or minus `k × robust spread / 0.6745`. These guides visualize detector coordinates; they are not standard deviations, confidence intervals or independent qualification tests, and crossing one guide alone is insufficient to qualify a candidate. Focus selection and candidate provenance are presentation state only; they do not alter `AnalysisContext`, matching, eligibility, detector results, the provider query, saved configuration or public URL.
````

</details>

### Original in 7.8.5 Descriptive spread and visualization transforms

<details><summary>Verbatim baseline passage</summary>

````text
IQR and min–max displays are descriptive spread summaries, not confidence intervals. An IQR band is drawn only where at least five values contribute to the relevant bin; the median remains available with fewer values. Empty bins remain missing rather than becoming synthetic zero observations.
````

</details>

### Original in 7.8.5 Descriptive spread and visualization transforms

<details><summary>Verbatim baseline passage</summary>

````text
Benchmark histograms normally use 1 dB bins, use 0.5 dB only for a clear half-dB lattice, and coarsen broad ranges to keep the number of bins bounded. Benchmark temporal density cells remain 1 dB high and follow the applied Reference SNR correction. For corrected Delta SNR `d` and numerical correction `c`, the ideal membership rule in the uncorrected comparison coordinate is `k = floor(d + c + 0.5)`; the numerical convention below evaluates this coordinate at 0.1 dB resolution. Cell `k` is centered at `k - c` and covers the half-open interval `[k - 0.5 - c, k + 0.5 - c)`: its lower boundary belongs to the cell, its upper boundary to the next cell, also for negative values. Adding `c` for membership is only a coordinate transformation; it does not apply the correction again to the stored observations, medians or quartiles. For the same retained population, changing `c` translates the density grid together with the corrected observations while retaining cell counts and relative-density colors. Fractional observations, including Local Median comparisons, need not lie at cell centers.
````

</details>

### Original in 7.8.5 Descriptive spread and visualization transforms

<details><summary>Verbatim baseline passage</summary>

````text
For membership only, `d + c` is rounded to the nearest tenth of a decibel before assigning its integer cell ID; exact half-tenth ties choose the even tenth. A float64 roundoff guard only at these rounding midpoints prevents correction noise from choosing opposite tenths. This explicitly limits membership resolution to 0.1 dB and absorbs numerical noise such as `-0.7000000000000028` in a corrected value expected at `-0.7 dB`; distinctions smaller than that membership resolution can share a cell. Exact half-dB coordinates at that resolution enter the upper cell, including negative values. The original corrected observations and their statistics are not rounded by this grid policy. A full-precision fractional observation can consequently lie up to 0.05 dB beyond its assigned cell edge; axis coverage still includes the observation itself. This temporal presentation policy replaces ties-to-even integer rounding, so exact half-dB assignments can change even with zero correction. It does not change ordinary histograms, Performance views or native-point Drill-Down plots. Each density panel is normalized independently:
````

</details>

### Original in 7.8.5 Descriptive spread and visualization transforms

<details><summary>Verbatim baseline passage</summary>

````text
Benchmark temporal and histogram views use a presentation-only monotonic scale centered on the scope median $M$. For a broad range, equal visual steps are anchored at $M$, $M\pm3$, $M\pm6$, $M\pm10$, $M\pm20$ and $M\pm30$ dB, with a tail anchor at $M\pm60$ dB and extrapolation when required. When every required deviation is at most `10 dB`, the tighter anchors are $M$, $M\pm1$, $M\pm3$, $M\pm6$ and $M\pm10$ dB, with continuation anchors at $M\pm20$ and $M\pm40$ dB. The required range includes the applicable raw histogram or correction-shifted temporal cell edges, a minimum `3 dB` half-span and absolute `0 dB`, so Target–Reference equality remains visible. The anchor mapping changes displayed spacing only: raw Delta SNR values, bin membership, counts, medians and quartiles remain unchanged. Because the vertical mapping is nonlinear, histogram bar **length** against its percentage axis — not displayed area — is the quantitative encoding.
````

</details>

### Original in 7.9 Geography, solar classification and population filters

<details><summary>Verbatim baseline passage</summary>

````text
The archive row limit and the controls that can reduce the retrieved source population are operational matters documented in [Section 5.6](#sec-6-6); they do not change the scientific summaries after the retained population has been formed.
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-7-11"></a>
#### 7.11 Robust local-baseline Delta SNR event detection
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
The detector's analysis target is a temporary same-sign departure in one path's paired Delta SNR from a stable local expected value. It is not a ranking of the largest raw values and does not estimate an event probability. [Section 2.5](#sec-outlier) explains when and how an operator should use the diagnostic; this section defines the exact scientific construction.
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
| Symbol | English mnemonic and meaning in this section |
|---|---|
| $i$ | one exact peer `callsign + locator` path identity |
| $u$ | one native paired unit: a same-cycle Joint Spot |
| $k$ | one UTC-aligned 10-minute baseline-cell index |
| $D_{i,u}$ | corrected paired Target-minus-Reference Delta SNR for unit $u$, following Section 7.5 |
| $\widetilde D_{i,k}$ | median Delta SNR in populated baseline cell $k$ |
| $\mathcal{B}_{\mathrm{pre}},\mathcal{B}_{\mathrm{post}}$ | retained pre-event and post-event Baseline evidence values |
| $B_{\mathrm{pre}},B_{\mathrm{post}},B$ | pre-event, post-event and final local Baseline |
| $B^P_{i,k}$ | Pilot Baseline for path $i$ and cell $k$ |
| $r^P_{i,u},r_{i,u}$ | Pilot and final Residual for native unit $u$ |
| $\mathcal{V},S_{\mathrm{robust}}$ | centred flank Variability sample and robust local Scale |
| $z_{i,u}$ | robust z-score of one native paired unit |
| $C_i,G_i,F$ | typical path Cadence, maximum internal Gap and provisional grouping Floor |
| $W_i^P,W_i^B$ | Pilot- and final-Baseline exclusion Widths |
| $E,m_E,z_E,\operatorname{agree}(E)$ | candidate Event, its Median residual, event robust z-score and sign-agreement fraction |
| $\varepsilon$ | fixed `0.01 dB` comparison tolerance for the minimum-departure and maximum-baseline-difference gates |
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
**1. Evidence and resolution.** Only native paired units supply detector Delta SNR. One-sided outcomes have no paired value and cannot qualify an event, although their times contribute to cadence estimation and the outcomes remain diagnostic context. Detection runs independently for each path $i$ before Temporal Evidence display aggregation. Changing a display bin cannot create, merge, split or remove an event. When **`Report ΔSNR outlier candidates`** is off, the detector is not run and no outlier semantics are added to the result.
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
The final expected local Delta SNR gives the two flanks equal weight, while the stability gate limits their disagreement:
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
To measure nearby variability without treating a baseline shift as noise, each flank is centred on its own baseline:
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
The robust local scale is:
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
MAD is the median absolute deviation and IQR is the interquartile range. The `0.5 dB` floor prevents division by zero for locally quantized evidence. Against the final baseline, one native unit has:
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
A positive residual is above the expected local Target-minus-Reference Delta SNR and a negative residual is below it; this residual sign, not the sign of raw $D_{i,u}$ relative to `0 dB`, drives grouping and qualification. The factor `0.6745` supplies conventional modified-score scaling when MAD is active. The score remains descriptive rather than a calibrated probability, p-value or Gaussian significance level.
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
**3. Cadence-aware pilot grouping.** The typical path cadence $C_i$ is estimated in minutes from unique eligible paired and one-sided outcome times. Positive intervals no longer than 45 minutes are retained, and at least two are required; otherwise the configured paired-unit cadence supplies $C_i$. The maximum internal gap is:
````

</details>

### Original in 7.11 Robust local-baseline Delta SNR event detection

<details><summary>Verbatim baseline passage</summary>

````text
The event qualifies only when every gate holds:
````

</details>

### Original in 8. Evidence-Matched Claims and Reproducibility

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar supports bounded descriptive and comparative claims about retained observational evidence. Strong reporting identifies the conditioned population, reported summary and weighting, support, experiment design and remaining unobserved or uncontrolled variables.
````

</details>

### Original in 8.1 Claim classes and evidence-matched wording

<details><summary>Verbatim baseline passage</summary>

````text
| Claim class | What WSPRadar can support | Additional requirement for a stronger claim |
|---|---|---|
| **Descriptive** | Reach, Decode Rate, successful SNR, Delta SNR, Decode Outcomes and where they appeared in the selected evidence. | State the population, weighting, scope and support. |
| **Comparative** | Target-versus-Reference difference under the selected Benchmark design. | State what the Reference represents and the matched subset. |
| **Component attribution** | A difference associated with a local path or component. | Controlled setup, calibration and preferably crossover/reversal. |
| **Causal** | The tested change caused the observed effect. | A design that controls plausible alternatives; WSPRadar summaries alone are insufficient. |
| **Inferential** | Confidence, significance or a population-general effect. | A justified dependence model and inferential analysis not currently supplied by WSPRadar. |
````

</details>

### Original in 8.1 Claim classes and evidence-matched wording

<details><summary>Verbatim baseline passage</summary>

````text
* **Performance** supports the Target's conditional behavior within confirmed opportunities and its at-least-once reach during the selected window.
* **Benchmark Delta SNR** supports paired Target-minus-Reference description within the Joint subset.
* **Decode Outcomes** support statements about pairability and one-sided evidence.
* **Distance or direction structure** supports statements about observed path segments, not direct radiation angle or gain pattern.
* **Reference Neighborhood** supports descriptions of how the complete Target station compared with the contributing nearby peers under the selected conditions. Its Reference changes with the qualifying observations, radius, remote path and cycle. It is neither a permanent station ranking nor a calibrated antenna comparison.
````

</details>

### Original in 8.1 Claim classes and evidence-matched wording

<details><summary>Verbatim baseline passage</summary>

````text
A positive or negative Delta SNR quantifies the observed paired SNR difference under that construction. It does not identify which component or environmental difference caused it. Joint Evidence Share describes pairability or coverage of the retained evidence; it is not a Target win rate.
````

</details>

### Original in 8.1 Claim classes and evidence-matched wording

<details><summary>Verbatim baseline passage</summary>

````text
| Avoid | Evidence-matched wording |
|---|---|
| “Antenna A has 3 dBi more gain.” | “Path A produced a +3.0 dB station-balanced median Delta SNR against B for the paired evidence in this band, window and segment.” |
| “My receiver sensitivity is 72%.” | “The Target receiver's station-balanced Decode Rate was 72% among qualifying peer-cycles confirmed by a Target decode or external endpoint-activity evidence.” |
| “Performance should be close to 100%.” | “Decode Rate is conditional on confirmed opportunities; 100% is not an expected baseline.” |
| “A is statistically significantly better.” | “The descriptive paired median favored A in the selected evidence; no significance test was performed.” |
| “The antenna has a lower take-off angle.” | “The observed advantage was concentrated in the specified longer-distance segments; radiation angle was not measured.” |
| “A is more efficient because it had more exclusive decodes.” | “A produced more one-sided decode evidence under the documented power, schedule and network conditions; efficiency was not isolated.” |
| “The local median is the average local station.” | “The Reference was the cycle/path median of one contribution per active local callsign-plus-locator identity.” |
| “My antenna is X dB better than nearby antennas.” | “For the stated band, window, radius and scope, my complete station’s station-balanced median Delta SNR was X dB relative to the observed local-neighborhood Reference. This describes the retained Joint evidence and does not isolate antenna gain.” |
````

</details>

### Original in 8.2 Interpretation boundaries

<details><summary>Verbatim baseline passage</summary>

````text
* user-supplied callsigns, locators and powers can be wrong;
* archives contain successful decodes rather than complete attempt logs;
* Performance is conditioned on observable opportunities;
* Target-active conditioning is asymmetric;
* successful Target SNR is censored to successful decodes;
* Benchmark Delta SNR is selected on Joint observation of both sides;
* one-sided evidence has no missing-side SNR;
* simultaneous TX retains power, frequency-response, isolation and coupling differences between chains;
* station hardware, software, terrain, local noise, polarization and propagation remain coupled unless the experiment controls them;
* observations are clustered across station, time, geography and propagation; and
* upstream records and availability can change after the original run.
````

</details>

### Original in 8.3 Reporting and reproducibility checklist

<details><summary>Verbatim baseline passage</summary>

````text
For a serious analysis, preserve three layers.
````

</details>

### Original in 8.3 Reporting and reproducibility checklist

<details><summary>Verbatim baseline passage</summary>

````text
* WSPRadar application version and, where available, source revision;
* RX/TX Direction, result type and Benchmark design;
* exact Target and Reference identities and locators;
* band and effective UTC boundaries;
* geographic scope, solar state, exclusions and evidence thresholds;
* Reference correction purpose, signed value and calibration basis;
* primary predeclared evaluation scope and any sensitivity analyses; and
* whether the run was exploratory or confirmatory.
````

</details>

### Original in 8.3 Reporting and reproducibility checklist

<details><summary>Verbatim baseline passage</summary>

````text
When a Delta SNR outlier candidate contributes to the conclusion, also record that reporting was enabled, the three detector thresholds, detector version, exact path, UTC interval, descriptive event class and whether the event was identified exploratorily or assessed under a predeclared confirmatory setup.
````

</details>

### Original in 8.3 Reporting and reproducibility checklist

<details><summary>Verbatim baseline passage</summary>

````text
* reported summary and weighting level;
* qualifying peers and opportunities for Performance;
* Joint peers and Joint spots/pairs for Benchmark;
* station-level and observation-level summaries;
* Joint Evidence Share and relevant one-sided Decode Outcomes;
* geographic/temporal scope and any influential identity or short interval; and
* within-run consistency versus repetition in a separate run.
````

</details>

### Original in 8.4 Analysis export package

<details><summary>Verbatim baseline passage</summary>

````text
`Prepare All Results for Download` builds a package from the completed run and current inspection selections. A typical package contains:
````

</details>

### Original in 8.4 Analysis export package

<details><summary>Verbatim baseline passage</summary>

````text
Files without an applicable result or selected station can be absent.
````

</details>

### Original in 8.4 Analysis export package

<details><summary>Verbatim baseline passage</summary>

````text
| Artifact | Scientific content and scope |
|---|---|
| `wspradar_config.config` | Versioned runnable definition and durable result-view settings. |
| `run_metadata.json` | Application/export provenance, Direction, band, time selection, Benchmark/correction definition, filters, thresholds and inspection selections. |
| `analysis_cache.parquet` | Processed retained evidence after scientific filters and geographic scope; not an untouched upstream dump. |
| `table_station_insights_current_segment.csv` | Per-peer summaries for the active Segment Inspector scope. |
| Drill-Down CSV files | Row-level retained evidence for selected or active-scope identities. |
| Delta-SNR outlier CSV files | When optional outlier reporting is enabled, qualified path-event summaries and their chronological native paired evidence for the active Segment Inspector scope. |
| Map and segment figures | Geographic and segment-level descriptive summaries for the completed result. |
| Temporal figures | Chronological and UTC-folded summaries for the active segment. |
| Selected-station figures | One exact selected peer identity in normal use; while optional Delta SNR outlier reporting enables an ordered multi-path selection, Benchmark can instead export the corresponding pooled multi-path Delta SNR view. |
| Drill-Down focus figures | Optional native-time metric and chronological companion figures for the exact selected station and active manual or candidate-linked focus interval; they supplement rather than replace the full-run selected-station figures. |
````

</details>

### Original in 8.4 Analysis export package

<details><summary>Verbatim baseline passage</summary>

````text
When a Drill-Down focus is active at preparation time, Performance can add `figure_drilldown_zoom_snr_evidence.png` and `figure_drilldown_zoom_temporal_evidence.png`; Benchmark can add `figure_drilldown_zoom_delta_snr_evidence.png` and `figure_drilldown_zoom_coverage.png`. Each title uses only the selected `callsign (locator)` followed by ` - Time Window: {start} to {end} UTC`. The metric figure preserves the same individual retained native points as the browser focus rather than substituting temporal medians; the companion figure preserves the applicable chronological outcome or coverage recipe. `run_metadata.json` records one `drilldown_zoom` block with its schema version, callsign, locator, exact `start_utc` and `end_utc`, selected focus option, `manual` or `outlier_focus` origin and render contract. When a candidate overlay is present, its registered recipe and signature preserve the focused episode and every individually qualifying candidate unit in the window, the muted focused-episode band, local and pre/post baseline values, robust spread and method, robust-z threshold and absolute-departure threshold used by the exported guides. The guide coordinates remain specific to the focused episode even when another starred candidate in the exported window was assessed against another baseline or spread. No focus block or focus figure is included while focus is off or the one-station requirement is not met.
````

</details>

### Original in 8.4 Analysis export package

<details><summary>Verbatim baseline passage</summary>

````text
When Delta SNR outlier reporting is enabled, `table_delta_snr_outlier_event_paths.csv` contains one row per qualified path event. It records the combined review-event class and observed UTC bounds, cross-path context and departure direction, then identifies the exact path, direction, path-event class, paired-evidence timing and count, expected and observed Delta SNR, largest departure, robust score, pre/post baseline diagnostics and nearby Decode Outcome diagnostics. One exact path can occur in more than one row of the same combined review event when it contributes more than one qualifying timeframe. The qualifying-path count remains the number of distinct `callsign + locator` identities.
````

</details>

### Original in 8.4 Analysis export package

<details><summary>Verbatim baseline passage</summary>

````text
`table_delta_snr_outlier_paired_evidence.csv` contains one row per retained native paired unit inside those path events, in chronological order. Event ID and Path event ID link it to the summary. For stand-alone readability it repeats the observed event bounds, path, direction and path-event class; the combined event class remains only in the summary because it can differ from an individual path's class. The table includes Target SNR, already-corrected Reference SNR, Delta SNR, expected local Delta SNR, departure from that baseline, per-unit robust score, strong-anchor status and reported-boundary role. Timestamps use ISO UTC and numeric fields remain numeric rather than embedding signs or units in the cells.
````

</details>

### Original in 8.4 Analysis export package

<details><summary>Verbatim baseline passage</summary>

````text
The export package preserves the processed evidence and provenance recorded by WSPRadar. It does not contain authoritative external operating logs, physical setup measurements or unchanged upstream responses. Preserve those separately as described in [Section 8.3](#sec-8-3).
````

</details>

### Original in References

<details><summary>Verbatim baseline passage</summary>

````text
* <a id="ref-12"></a><a href="https://wsjt.sourceforge.io/wsjtx-main_en.html">[Ref-12]</a> **Official operating documentation.** WSJT-X 3.0.1 User Guide: WSPR Type 1, Type 2 and Type 3 message formats; random `Tx Pct` scheduling; Windows `--rig-name` file isolation; Audio settings and file locations. QRP Labs, <a href="https://qrp-labs.com/qmx">*QMX firmware history and manuals*</a> and <a href="https://www.qrp-labs.com/images/qmx/manuals/operation_1_04_004.pdf">*QMX Operating Manual, firmware 1_04_004*</a>: model-specific firmware, Virtual U3S operation and scheduling; <a href="https://www.qrp-labs.com/images/ultimate3s/operation3.12a2.pdf">*Ultimate3S Operating Manual, firmware v3.12a2*</a>: WSPR frequency range, global Frame/Start behavior, extended WSPR, sequential mode entries and per-entry `Aux` values; <a href="https://qrp-labs.com/images/appnotes/AN003_A4.pdf">*AN003: Ultimate3/3S relay-switched filters*</a>: filtered relay/driver interfacing and RF-off switching intervals. Accessed 2026-08-25.
````

</details>

### Original in Appendix A: Parallel WSJT-X Instances for Simultaneous RX

<details><summary>Verbatim baseline passage</summary>

````text
This procedure creates a second isolated WSJT-X instance for a simultaneous RX controlled setup comparison on Windows. The current WSJT-X guide documents `--rig-name` as the supported way to isolate each instance's settings and writable files. WSJT-X versions and installation paths can change, so verify the current guide if your menus differ. <a href="#ref-12">[Ref-12]</a>
````

</details>

### Original in Appendix B: Simultaneous TX Reference Setup

<details><summary>Verbatim baseline passage</summary>

````text
Use this appendix to prepare two locally controlled transmit paths that radiate distinguishable WSPR signals in the same cycles. The result compares the complete documented Target and Reference paths. Do the bench and archive checks before opening the measurement window; callsign legality, RF safety, filtering and station licensing remain the operator's responsibility.
````

</details>

### Original in B.1 Choose the callsigns

<details><summary>Verbatim baseline passage</summary>

````text
If only one ordinary callsign is available, a permitted suffix can create a second distinguishable identity, but it may also create a compound callsign. Use a suffix only when that on-air identity is valid for the operator and station; archive syntax alone is not authorization. Avoid compound callsigns unless necessary. If one is unavoidable, configure both transmitters for the same extended-WSPR message pattern so their Type 2 phases coincide and their Type 3 phases coincide. Do not mix an ordinary one-cycle pattern on one arm with a two-cycle compound pattern on the other.
````

</details>

### Original in B.4 Verify WSPRnet and the selected archive

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-simultaneous-tx-setup-4"></a>
#### B.4 Verify WSPRnet and the selected archive
````

</details>

### Original in B.4 Verify WSPRnet and the selected archive

<details><summary>Verbatim baseline passage</summary>

````text
1. Transmit several complete synchronized sequences with the final callsign, locator, power, timing and frequency settings.
2. Search the [WSPRnet Spot Query](https://www.wsprnet.org/drupal/wsprnet/spotquery) for each exact callsign. Do not rely only on the map, which can show a last-known locator.
3. Check the intended grid-4, reported power, timestamps and separate frequencies.
4. Find cycles in which the same remote receiver reported both callsigns and verify matching timestamps.
5. For a two-transmission sequence, check both positions against the known schedule; the archive need not label them explicitly as Type 2 and Type 3.
6. Run a short WSPRadar preflight and wait until the test spots are actually queryable there. Population of wspr.live and other databases can take `15 minutes or more`.
7. Once the spots are available, inspect unexpected concentrations of Only Target or Only Reference, then compare Joint Evidence Share, one-sided outcomes and paired Delta SNR between the two sequence positions. A persistent phase difference flags a need to check hash resolution, frequency placement, transmitter heating and power sag.
````

</details>

### Original in B.5 Device-specific setup

<details><summary>Verbatim baseline passage</summary>

````text
The following examples are starting procedures, not substitutes for the manual that matches the installed firmware. Re-run the full timing, frequency, power and archive preflight whenever firmware or configuration changes.
````

</details>

### Original in B.5.1–B.5.2 QMX and QMX+ Virtual U3S, and Ultimate3S

<details><summary>Verbatim baseline passage</summary>

````text
1. For QMX or QMX+, install the current firmware approved for the exact model and follow its version-matched Virtual U3S instructions. Do not use the initial `1_04_000` release as a general QMX recipe; QRP Labs identifies it as QMX+-specific and later releases include Virtual U3S corrections. For a physical Ultimate3S, fit the correct output filter for the selected band.
2. Enter the two exact callsigns, the same truthful locator and each unit's measured power using the nearest valid WSPR-encoded dBm value. Ordinary Type 1 callsigns are preferred. If compound callsigns are unavoidable, configure the same extended-WSPR arrangement on both units and verify that the Type 2 and Type 3 phases remain aligned.
3. Give both units accurate UTC from GNSS or another documented time reference. Use the same deterministic global `Frame` and the same observed even-minute `Start`, and disable unrelated entries so one arm cannot insert an extra transmission. The physical Ultimate3S treats `Start = 00` specially as “not used,” so verify the displayed and observed starts.
4. Program full RF frequencies nominally 100 Hz apart and keep both complete signals comfortably inside the 200 Hz WSPR sub-band. Suitable starting pairs include `7.040050 MHz` and `7.040150 MHz` on 40 m, or `14.097050 MHz` and `14.097150 MHz` on 20 m. These are actual RF frequencies, not receiver USB dial frequencies. Follow the installed firmware's tone convention and verify the radiated signals rather than trusting the displayed values alone.
5. Test each unit alone, both together into loads, and finally at the intended low on-air power. Complete the power, simultaneous-signal and archive checks above before collecting the experiment.
````

</details>

### Original in B.5.3 ZachTek firmware 2.19 randomized split-lane builds

<details><summary>Verbatim baseline passage</summary>

````text
After flashing, test each transmitter separately and then both together into dummy loads or a safely attenuated arrangement. Verify actual RF frequency, timing, output power, filtering and spectral purity before connecting antennas. During a short on-air preflight, also confirm that the observed frequencies remain inside their intended lower and upper lanes and that both identities produce adequate same-cycle Joint reports before beginning the measurement run.
````

</details>

### Original in Appendix C: Reference SNR Calibration

<details><summary>Verbatim baseline passage</summary>

````text
1. **Common input:** feed both receive chains from one stable antenna through a suitable splitter and controlled cables.
2. **Characterize the splitter:** account for output imbalance and cable differences; swap outputs in a control run when practical.
3. **Collect paired evidence:** operate simultaneously across the intended signal levels without changing gain or decoder settings.
4. **Derive the offset:** use paired Delta SNR evidence and state whether the value was calculated from station-balanced summaries or raw pairs.
5. **Check consistency:** inspect by station, time and SNR. One constant is not defensible if offset changes with level, frequency, AGC or time.
6. **Apply the sign:** enter the observed `target - reference` offset with the same sign.
7. **Validate:** repeat or swap paths and confirm corrected common-input Delta is plausibly near zero.
````

</details>

- `de`: `09110629042cb4fabecd163ef6b9ebe8e698148cc1e9f91718691a82be2aa319`

## DE: preserved original passages

The following original paragraphs or table/list blocks were replaced, condensed, corrected or relocated. Their factual/operating meaning is accounted for in the chapter review records below; verbatim text is retained here so no superseded wording disappears without a record.

### Original in 0. Warum WSPRadar?

<details><summary>Verbatim baseline passage</summary>

````text
Erfahrene Funkamateure begegnen diesem Problem mit zunehmend kontrollierten Verfahren: wiederholten Vergleichen, Bakenaussendungen, WebSDRs, Daten des Reverse Beacon Network, WSPR und insbesondere einer schnellen A/B-Umschaltung im laufenden Betrieb. Ein schneller A/B-Test ist wesentlich aussagekräftiger als zwei Stunden auseinanderliegende QSOs, weil Sender, Leistung, Frequenz, Gegenstation und ein großer Teil des Funkwegs ähnlich bleiben. Etablierte WSPR-Vergleichsversuche zeigen ebenfalls, dass gemeinsame Bedingungen und möglichst kurze – oder simultane – Vergleiche belastbarer sind als lange getrennte Messblöcke <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-3">[Ref-3]</a> <a href="#ref-4">[Ref-4]</a> <a href="#ref-5">[Ref-5]</a>.
````

</details>

### Original in 0. Warum WSPRadar?

<details><summary>Verbatim baseline passage</summary>

````text
Das Ergebnis ist mehr als eine Spotzahl und mehr als eine einzelne Gewinner-Verlierer-Kennzahl. WSPRadar kann zeigen, ob ein Muster breit oder funkwegabhängig ist, ob es mit Entfernung oder Richtung zusammenhängt, ob es nur einmal auftritt oder zu bestimmten Tageszeiten wiederkehrt, ob viele Stationen übereinstimmen und ob die gepaarte Evidenz das breitere Ergebnis tatsächlich repräsentiert. Damit wird aus **„Das sah einmal besser aus“** zunehmend **„Dieser Unterschied trat hier, unter diesen Bedingungen, wiederholt und mit dieser Evidenz auf.“**
````

</details>

### Original in 0.0 WSPR in 2 Minuten

<details><summary>Verbatim baseline passage</summary>

````text
<strong class="defined-term">WSPR</strong> steht für **Weak Signal Propagation Reporter**. Joe Taylor, K1JT, und Bruce Walker, W1BW, beschrieben WSPR als weltweites Netz von QRP-Stationen, die bakenartige Aussendungen austauschen, um mögliche Ausbreitungswege zu untersuchen. Eine WSPR-2-Aussendung dauert knapp zwei Minuten und belegt nur etwa 6 Hz. Eine normale Typ-1-Nachricht überträgt in dieser einen Aussendung ein reguläres Rufzeichen, einen vierstelligen Maidenhead-Locator und die gemeldete Sendeleistung in dBm. Das vom Decoder gemeldete Signal-Rausch-Verhältnis (SNR) bezieht sich auf eine Bandbreite von 2500 Hz; Decodes sind bis ungefähr `-28 dB` möglich. Ein weniger negativer SNR-Wert bedeutet ein stärkeres Signal relativ zum Empfängerrauschen <a href="#ref-6">[Ref-6]</a> <a href="#ref-8">[Ref-8]</a>.
````

</details>

### Original in 0.0 WSPR in 2 Minuten

<details><summary>Verbatim baseline passage</summary>

````text
Ist das Reporting aktiviert, lädt ein Empfänger jeden erfolgreichen Decode als <strong class="defined-term">Spot</strong> hoch. Ein Spot enthält die Identität von Sender und Empfänger, deren gemeldete Standorte, Zeit, Band, Sendeleistung und den vom Decoder gemeldeten SNR. Öffentliche <strong class="defined-term">Archive</strong> enthalten dadurch eine große und fortlaufend wachsende Sammlung erfolgreicher Funkbeobachtungen, die von unabhängig betriebenen Stationen in aller Welt beigetragen werden. Dienste wie wspr.live und WSPRDaemon bewahren diese Beobachtungsdaten auf und stellen sie für Analysen bereit <a href="#ref-10">[Ref-10]</a> <a href="#ref-11">[Ref-11]</a>.
````

</details>

### Original in 0.0 WSPR in 2 Minuten

<details><summary>Verbatim baseline passage</summary>

````text
Erweitertes WSPR kann stattdessen ein zusammengesetztes Rufzeichen und einen präzisen sechsstelligen Locator über zwei sich ergänzende Aussendungen übertragen. Eine Typ-2-Nachricht überträgt das zusammengesetzte Rufzeichen und die Leistung, jedoch keinen Locator; die zugehörige Typ-3-Nachricht überträgt einen 15-Bit-Hash dieses Rufzeichens, den sechsstelligen Locator und die Leistung. Die beiden Aussendungen liegen in getrennten WSPR-Zyklen; sie sind nicht zwei Felder einer einzigen Archivzeile <a href="#ref-12">[Ref-12]</a>.
````

</details>

### Original in 0.0 WSPR in 2 Minuten

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar decodiert diese Funknachrichten nicht und rekonstruiert aus Typ-2- und Typ-3-Phasen keine zusammengesetzte Identität. Es analysiert die Rufzeichen-, Locator-, Zeit- und Leistungsfelder, die das ausgewählte Reporting-Archiv bewahrt. Bei simultanem TX A/B müssen deshalb beide exakten Identitäten mit dem gemeinsamen wahrheitsgemäßen Grid-4 und ausgerichteten Nachrichtenphasen im Archiv erscheinen; die praktischen und wissenschaftlichen Folgen beschreiben die [Abschnitte 2.2.1](#sec-3-tx-benchmark-simultaneous), [7.1](#sec-7-1), [7.2](#sec-7-2) und [7.6](#sec-7-6).
````

</details>

### Original in 0.0 WSPR in 2 Minuten

<details><summary>Verbatim baseline passage</summary>

````text
**Datenquellen.** WSPRadar verwendet **wspr.live** als primäre Datenquelle. Das WSPRadar-Projekt dankt den Menschen hinter wspr.live und WSPRDaemon, die diese öffentlich zugängliche Datenbankinfrastruktur bereitstellen und betreiben.
````

</details>

### Original in 0.0 WSPR in 2 Minuten

<details><summary>Verbatim baseline passage</summary>

````text
Bei gleichzeitiger Last kann WSPRadar einen vollständigen neuen Lauf je nach verfügbarer Kapazität an **WSPRDaemon WD2** und danach **WD1** weiterleiten. Dieser geordnete Kapazitätsausgleich unterscheidet sich von einem Quellenwechsel nach einem Ausfall: Fällt eine ausgewählte Quelle aus, verwirft WSPRadar den noch nicht veröffentlichten Versuch und startet den vollständigen Lauf mit der nächsten Quelle neu. Jeder abgeschlossene Lauf bleibt an genau ein Archiv gebunden; Datensätze aus verschiedenen Quellen werden niemals zusammengeführt.
````

</details>

### Original in 0.0 WSPR in 2 Minuten

<details><summary>Verbatim baseline passage</summary>

````text
Eine Einschränkung ist für jede Analyse zentral: Das Archiv erfasst erfolgreiche Decodes, aber kein vollständiges Protokoll aller Sendeversuche oder aller aktiven Empfänger. Ein gültiger erfolgreicher Decode bestätigt unmittelbar die Beteiligung beider Endpunkte. Innerhalb eines Target-aktiven Zyklus bildet WSPRadar deshalb eine <strong class="defined-term">Gelegenheit</strong>, wenn der Target-seitige Decode gelingt oder externe Evidenz die betreffende Peer-Aktivität bestätigt. Bei RX ist der Decode des Peer-TX durch den Target-RX ein Erfolg; ein anderer geeigneter RX, der denselben Peer-TX decodiert, bestätigt dessen Sendeaktivität zur Bewertung eines fehlenden Target-RX-Decodes. Bei TX ist der Decode des Target-TX durch den Peer-RX ein Erfolg; decodiert derselbe Peer-RX einen anderen qualifizierenden TX auf demselben Band, bestätigt dies seine Empfangsaktivität zur Bewertung eines fehlenden Target-TX-Decodes. Alle Nachweise müssen zum gewählten Band, Zyklus und zur exakten Peer-Identität passen. Ohne ausreichenden Aktivitätsnachweis der Endpunkte bleibt Funkstille unbekannt und ausgeschlossen; Aktivität andernorts belegt niemals, dass ein bestimmter stiller Empfänger zugehört hat.
````

</details>

### Original in 0.0 WSPR in 2 Minuten

<details><summary>Verbatim baseline passage</summary>

````text
Durch diese Unterscheidung wird aus einer Sammlung erfolgreicher Spots Evidenz, die Fragen nach praktischer Reichweite, Beständigkeit und relativer Performance stützen kann, ohne so zu tun, als sei jede fehlende Meldung ein gescheiterter Funkweg.
````

</details>

### Original in 0.1 Was WSPRadar zeigen kann

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar ist ein WSPR-basiertes System zur Analyse und zum Benchmarking der Performance von Antennen und Stationen. Es wertet ein <strong class="defined-term">Target</strong> aus: die zu untersuchende Station, normalerweise deine Station, dargestellt entweder als vollständig aufgebaute Station oder als kontrollierter Sende- beziehungsweise Empfangspfad. Ein <strong class="defined-term">Peer</strong> ist eine entfernte Gegenstation, deren Funkweg zur Analyse beiträgt. Die <strong class="defined-term">Dekodierrate</strong> ist der Prozentsatz bestätigter Gelegenheiten mit einem erfolgreichen Decode auf der Target-Seite: Bei RX decodiert das Target den Peer, bei TX decodiert der Peer das Target. Dabei beantwortet WSPRadar eine von zwei grundlegenden Fragen.
````

</details>

### Original in 0.1 Was WSPRadar zeigen kann

<details><summary>Verbatim baseline passage</summary>

````text
* <strong class="defined-term">Performance</strong> fragt, wie sich das Target innerhalb bestätigter WSPR-Gelegenheiten verhalten hat. Sie kann die praktische Funkabdeckung, Mindestens-einmal-Reichweite, Dekodierrate, erfolgreiche Signalpegel, Distanz- und Richtungsstruktur, zeitliches Verhalten sowie Breite und Tiefe der stützenden Evidenz sichtbar machen.
* <strong class="defined-term">Benchmark</strong> fragt, wie sich das Target unter zugeordneten Bedingungen relativ zu einer aussagekräftigen <strong class="defined-term">Referenz</strong> verhalten hat. Er kann gepaartes Delta SNR Target minus Referenz, gemeinsame und einseitige Decode Outcomes, den Anteil paarbarer Evidenz sowie Ort und Zeit des relativen Unterschieds zeigen.
````

</details>

### Original in 0.1 Was WSPRadar zeigen kann

<details><summary>Verbatim baseline passage</summary>

````text
| Analyse | Fragestellung | Praktische Beispiele |
|---|---|---|
| <strong class="analysis-choice-single">RX Performance</strong> | Wie breit und wie beständig decodiert mein Empfänger Signale innerhalb bestätigter Gelegenheiten? | Empfangsbereich einer neu aufgebauten Antenne oder Station erfassen; unterscheiden, ob der Empfang breit, aber wechselhaft oder schmaler und beständig ist; wiederkehrende Richtungs-, Entfernungs- oder UTC-Stunden-Muster erkennen – einschließlich Zeiträume, die eine separate Prüfung auf lokalen Störpegel oder intermittierende Hardware nahelegen. |
| <strong class="analysis-choice-single">TX Performance</strong> | Wo, wann und wie beständig wird mein Sender von Empfängern decodiert, deren Aktivität nachgewiesen ist? | Abbilden, wo eine QRP-Bake oder neu installierte Antenne gehört wird; erkennen, zu welchen Zeiten und in welchen Richtungen nachweislich aktive Empfänger die Station besonders beständig decodieren; nach Inbetriebnahme, Reparatur oder Standortänderung eine Ausgangsbasis schaffen und mit vergleichbaren Wiederholungsläufen prüfen, ob sich das beobachtete Verhalten später verändert. |
| <span class="analysis-choice"><span class="analysis-family">RX Benchmark</span><br><strong class="analysis-variant">Referenzaufbau/-station</strong></span> | Unterschieden sich zwei lokale Empfangspfade beim gleichzeitigen Beobachten derselben entfernten Aussendungen? | Zwei Antennen vergleichen, die jeweils eine eigene simultane Empfänger- und Decoderkette speisen, wobei das Ergebnis zunächst die vollständigen Empfangspfade beschreibt; einen Unterschied nur dann gezielt den Antennen zuschreiben, wenn die übrigen Ketten abgeglichen, charakterisiert oder durch einen Kreuztausch bestätigt wurden; eine Antenne über einen charakterisierten Verteiler an zwei Empfänger führen, um Empfänger oder Decoderpfade zu vergleichen; Vorverstärker, Filter, Speiseleitung oder Mantelwellensperre nur in einen ansonsten kontrollierten Pfad einfügen und die beiden dokumentierten vollständigen Empfangspfade benchmarken. |
| <span class="analysis-choice"><span class="analysis-family">TX Benchmark</span><br><strong class="analysis-variant">Referenzaufbau/-station</strong></span> | Unterschieden sich zwei lokale Sendepfade in denselben WSPR-Zyklen? | Zwei Antennen über getrennte, kalibrierte Sendeketten speisen und mit synchronisierten Zyklen, unterscheidbaren Signalen und ausreichender Entkopplung gleichzeitig senden; zwei Speiseleitungen, Anpassnetzwerke, Filter oder vollständige Sendepfade vergleichen und dabei tatsächliche Leistung, Zeitsteuerung und die übrige Kette kontrollieren. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Referenzaufbau/-station</strong></span> | Wie schneidet meine vollständige Station gegenüber einer bekannten Station ab? | <strong>RX:</strong> den eigenen Empfänger mit dem bekannten Empfänger eines Funkfreunds vergleichen, während beide in denselben Zyklen dieselben entfernten Sender beobachten; <strong>TX:</strong> den eigenen Sender mit dem Sender eines Funkfreunds an denselben entfernten Empfängern und in denselben Zyklen vergleichen; ein stabiles, gut verstandenes Buddy-Design vor und nach dokumentierten Stationsarbeiten als relative Basislinie für die Gesamtstation wiederholen, ohne die Buddy-Station als absolut kalibrierten Standard zu behandeln. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Referenznachbarschaft (Lokaler Median)</strong></span> | Wie schneidet meine vollständige Station gegenüber den beobachteten WSPR-Peers in der Umgebung ab? | Prüfen, ob die eigene Empfangs- oder Sendestation insgesamt über, nahe oder unter dem zyklus- und funkwegspezifischen Median der qualifizierenden beobachteten lokalen Peers im gewählten Radius liegt; eine Station in Betrieb nehmen, wenn keine einzelne geeignete Buddy-Referenz verfügbar ist; Richtungen, Entfernungen oder UTC-Zeiträume erkennen, in denen die Station von dieser kontextbezogenen lokalen Basislinie abweicht, und dabei Zusammensetzung der Nachbarschaft sowie Radiusabhängigkeit prüfen. Verglichen werden vollständige Stationen unter den beobachteten Bedingungen; daraus ergeben sich weder isolierter Antennengewinn noch eine Rangliste aller Stationen in der Umgebung. |
````

</details>

### Original in 0.2 Was ein Lauf liefert

<details><summary>Verbatim baseline passage</summary>

````text
Ein WSPRadar-Lauf erzeugt ein zusammenhängendes Evidenzpaket für eine klar begrenzte Stationsfrage – keine universelle Kennzahl und keine Rangliste.
````

</details>

### Original in 0.2 Was ein Lauf liefert

<details><summary>Verbatim baseline passage</summary>

````text
Ein Performance-Lauf verbindet praktische Reichweite, zwei ergänzende Gewichtungen der Dekodierrate, erfolgreiches Target-SNR, Distanz- und Richtungsstruktur, zeitliche Veränderungen, wiederkehrendes Verhalten nach UTC-Stunde, beitragende Stationen und die zugrunde liegenden Gelegenheiten. Ein Benchmark-Lauf verbindet gepaartes Delta SNR mit Decode Outcomes und Evidenzabdeckung, sodass ein günstiger gepaarter Median weder umfangreiche einseitige Evidenz noch eine schmale paarbare Teilmenge verdecken kann.
````

</details>

### Original in 0.2 Was ein Lauf liefert

<details><summary>Verbatim baseline passage</summary>

````text
Jedes Ergebnis folgt demselben Evidenzpfad:
````

</details>

### Original in 0.2 Was ein Lauf liefert

<details><summary>Verbatim baseline passage</summary>

````text
Die Karte liefert den geografischen Überblick. Evidenz auf Segmentebene zeigt, wie sich die Beobachtung nach Entfernung und Richtung verändert und wie viel Unterstützung dahintersteht. Performance- beziehungsweise Benchmark-Evidenz trennt das Hauptergebnis von seiner ergänzenden Evidenz. Zeitliche Evidenz zeigt, ob sich das Muster während des Laufs veränderte oder zu bestimmten UTC-Stunden wiederkehrte. Station Insights legt offen, welche Stationsidentitäten beitragen. Die Evidenz der ausgewählten Station verfolgt einen exakten Funkweg; Drill-Down zeigt die Beobachtungen, Vergleiche desselben Zyklus hinter den Zusammenfassungen.
````

</details>

### Original in 0.2 Was ein Lauf liefert

<details><summary>Verbatim baseline passage</summary>

````text
Diese abgestufte Struktur ist eine der zentralen Stärken von WSPRadar: Das übergeordnete Muster bleibt mit seiner Evidenz verbunden. Der Operator kann von **wo der Effekt auftritt** über **wie beständig er ist und wie gut er gestützt wird** bis zu **den einzelnen Beobachtungen, aus denen die Schlussfolgerung entstanden ist**, hinabsteigen.
````

</details>

### Original in 0.2 Was ein Lauf liefert

<details><summary>Verbatim baseline passage</summary>

````text
Ein belastbares Ergebnis ist deshalb nicht einfach der größte Wert auf dem Bildschirm. Versuchsdesign, geografisches Muster, zeitliches Verhalten, Stationsbreite, Evidenztiefe und Prüfung auf Zeilenebene müssen dieselbe begrenzte Interpretation stützen. Eine Wiederholung des Designs in einem weiteren geeigneten Betriebsfenster kann anschließend prüfen, ob die Beobachtung experimentell wiederholbar ist und nicht nur innerhalb eines Laufs konsistent erscheint.
````

</details>

### Original in 0.2 Was ein Lauf liefert

<details><summary>Verbatim baseline passage</summary>

````text
Der vollständige Lauf lässt sich außerdem als Reproduzierbarkeitspaket mit Analysedefinition, verarbeiteter Evidenz, Tabellen, Abbildungen und Metadaten sichern. Zusammen mit den physischen Stationsnotizen, die WSPRadar nicht selbst erschließen kann, kann er später erneut geprüft oder mit anderen Funkamateuren geteilt werden.
````

</details>

### Original in 0.3 Der erste sinnvolle Lauf

<details><summary>Verbatim baseline passage</summary>

````text
Am schnellsten erschließt sich WSPRadar mit einer gepflegten Demo. Eine Demo zeigt eine vollständige historische Performance- oder Benchmark-Analyse mit vorbereitetem Versuchskontext. So lässt sich der Evidenzpfad erkunden, bevor die eigene Station beteiligt ist.
````

</details>

### Original in 0.3 Der erste sinnvolle Lauf

<details><summary>Verbatim baseline passage</summary>

````text
Der Nutzen der Demo wird im Zusammenhang ihrer Ebenen sichtbar: geografischer Überblick, Entfernung und Richtung, einmaliges oder wiederkehrendes zeitliches Verhalten, Anzahl und Vielfalt der stützenden Stationen, Paarbarkeit der Benchmark-Evidenz sowie die ausgewählten Funkwege und Beobachtungen auf Zeilenebene hinter der Zusammenfassung.
````

</details>

### Original in 0.3 Der erste sinnvolle Lauf

<details><summary>Verbatim baseline passage</summary>

````text
Eine Demo ist ein durchgearbeitetes Beispiel für die Methode von WSPRadar und keine Evidenz über die eigene Station. Sobald der Evidenzpfad vertraut ist, beginnt die erste sinnvolle Analyse der eigenen Station mit einer klaren Frage: eine RX- oder TX-Performance-Basislinie bestimmen, zwei kontrollierte lokale Pfade vergleichen, gegen eine bekannte Station benchmarken oder die Station in ihren lokalen WSPR-Kontext einordnen.
````

</details>

### Original in 0.3 Der erste sinnvolle Lauf

<details><summary>Verbatim baseline passage</summary>

````text
Ziel ist keine schmeichelhafte Zahl. Ziel ist ein Ergebnis, das sich verstehen, hinterfragen, wiederholen und für eine fundiertere Stationsentscheidung nutzen lässt.
````

</details>

### Original in Inhaltsverzeichnis

<details><summary>Verbatim baseline passage</summary>

````text
* [6. Literatur, Vorarbeiten und Einordnung](#sec-d)
    * [6.1 Vom Meldenetz zum Versuchsdatensatz](#sec-d-1)
    * [6.2 WSPR-Beobachtungsdaten interpretierbar machen](#sec-d-2)
    * [6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen](#sec-d-3)
    * [6.4 Analyseinfrastruktur und verwandte Werkzeuge](#sec-d-4)
    * [6.5 Was WSPRadar übernimmt, integriert und ergänzt](#sec-d-5)
* [7. Wissenschaftliche Methoden](#sec-7)
    * [7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell](#sec-7-1)
    * [7.2 Identität, Zuordnung und Zeilenkonsolidierung](#sec-7-2)
    * [7.3 Konditionierung auf Target-Aktivität und Zulässigkeit](#sec-7-3)
    * [7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen](#sec-7-4)
    * [7.5 Leistungsnormierung, Korrektur und Benchmark-Delta-SNR](#sec-7-5)
    * [7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen](#sec-7-6)
    * [7.7 Aggregationshierarchie und Gewichtung](#sec-7-7)
    * [7.8 Geografische, zeitliche und funkwegbezogene Zusammenfassungen](#sec-7-8)
        * [7.8.1 Geografische Zusammenfassungen](#sec-7-8-1)
        * [7.8.2 Abdeckung der Benchmark-Evidenz](#sec-7-8-2)
        * [7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung](#sec-7-8-3)
        * [7.8.4 Zusammenfassungen für den ausgewählten Funkweg](#sec-7-8-4)
        * [7.8.5 Deskriptive Streuung und Visualisierungstransformationen](#sec-7-8-5)
    * [7.9 Geografie, Sonnenstandsklassifikation und Populationsfilter](#sec-7-9)
    * [7.10 Abhängigkeit, Unsicherheit und Geltungsbereich der Validierung](#sec-7-10)
    * [7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie](#sec-7-11)
* [8. Evidenzgerechte Aussagen und Reproduzierbarkeit](#sec-8)
    * [8.1 Aussageklassen und evidenzgerechte Formulierungen](#sec-8-1)
    * [8.2 Interpretationsgrenzen](#sec-8-2)
    * [8.3 Checkliste für Berichterstattung und Reproduzierbarkeit](#sec-8-3)
    * [8.4 Exportpaket der Analyse](#sec-8-4)
    * [8.5 Haftungsausschluss](#sec-8-5)
* [Literatur und Quellen](#sec-ref)
````

</details>

### Original in Teil I: Leitfaden für den Funkbetrieb

<details><summary>Verbatim baseline passage</summary>

````text
Dieser Teil führt von der betrieblichen Fragestellung zu einer evidenzgerechten Schlussfolgerung. Kapitel 1 schafft die gemeinsame Versuchsgrundlage, wählt RX oder TX sowie Performance oder Benchmark und führt den gemeinsamen Evidenzpfad ein. Kapitel 2 folgt diesem Pfad anschließend innerhalb der konkreten Analysefamilie und des jeweiligen Referenzdesigns und schließt mit einem optionalen Diagnosewerkzeug für erfahrene Anwender zur Prüfung vorübergehender Delta-SNR-Abweichungen. Kapitel 3 erläutert, wie ein Ergebnis abgesichert, berichtet und bewahrt wird. Die exakten Bedienelemente stehen in Teil II; genaue Berechnungen und wissenschaftliche Randfälle in Teil III.
````

</details>

### Original in 1.1 Solide Versuchsgrundlage schaffen

<details><summary>Verbatim baseline passage</summary>

````text
Ein nützliches WSPRadar-Ergebnis beginnt mit einem Satz, der festhält, was geprüft wird und welche Beobachtung als Unterstützung gelten würde. Lege fest, ob der Lauf explorativ ist – also ein mögliches Muster aufspüren soll – oder ob er ein bereits erkanntes Muster bestätigend prüfen soll.
````

</details>

### Original in 1.1 Solide Versuchsgrundlage schaffen

<details><summary>Verbatim baseline passage</summary>

````text
Verwende genau ein Band und ein UTC-Zeitfenster, in dem das Target tatsächlich in Betrieb war. Gib Rufzeichen exakt so ein, wie sie hochgeladen wurden, und prüfe das Target-QTH. Dokumentiere Antenne, Speiseleitung, Funkgerät, Tuner, Verstärkungs- oder Leistungseinstellungen, Decoder, Softwareversion, Zeitplan und jede beabsichtigte Änderung. Halte alle Variablen außerhalb der Fragestellung so stabil wie praktisch möglich.
````

</details>

### Original in 1.1 Solide Versuchsgrundlage schaffen

<details><summary>Verbatim baseline passage</summary>

````text
Halte bei TX die tatsächliche und die gemeldete Sendeleistung korrekt und stabil, sofern nicht gerade die Leistung untersucht wird. Halte bei RX Verstärkung, Filterung, Audioführung, Decoder-Einstellungen und Upload-Verhalten stabil, sofern nicht einer dieser Punkte Gegenstand des Tests ist. Synchronisiere die Uhren. Prüfe bei Benchmark, ob die Referenz wie vorgesehen in Betrieb war: Das Target-Active Gate belegt eine beobachtbare Beteiligung des Targets, aber nicht die Betriebsbereitschaft der Referenz.
````

</details>

### Original in 1.1 Solide Versuchsgrundlage schaffen

<details><summary>Verbatim baseline passage</summary>

````text
Lege vor einer bestätigenden Wiederholung Richtung, Band, Referenzdesign, Filter, Schwellen, Zeitplan und den primären geografischen oder zeitlichen Auswertungsbereich fest. Behandle alternative Radien, Zeitfenster oder Bereiche als getrennte Sensitivitätsanalysen, statt nur die günstigste Variante auszuwählen.
````

</details>

### Original in 1.2 Die zur Fragestellung passende Analyse wählen

<details><summary>Verbatim baseline passage</summary>

````text
| Betriebliche Fragestellung | Analyse |
|---|---|
| Welche Signale decodiert mein Empfänger innerhalb bestätigter Gelegenheiten, wo, wann und wie beständig? | **RX Performance** |
| Wo und wie beständig wird mein Sender von Empfängern decodiert, deren Aktivität nachgewiesen ist? | **TX Performance** |
| Wie unterscheiden sich zwei lokale Empfangspfade, zwei vollständige Empfangsstationen oder mein Empfänger und eine lokale Nachbarschaftsreferenz? | **RX Benchmark** |
| Wie unterscheiden sich zwei lokale Sendepfade, zwei vollständige Sendestationen oder mein Sender und eine lokale Nachbarschaftsreferenz? | **TX Benchmark** |
````

</details>

### Original in 1.2 Die zur Fragestellung passende Analyse wählen

<details><summary>Verbatim baseline passage</summary>

````text
Wähle **Performance**, wenn das Target selbst Gegenstand der Frage ist und keine Referenz benötigt wird. Performance verbindet Mindestens-einmal-Reichweite, Dekodierrate, erfolgreiches Target-SNR, Geografie, Zeit und Evidenzunterstützung. Sie beschreibt die vollständige Target-Station unter den ausgewählten realen Betriebsbedingungen.
````

</details>

### Original in 1.3 Dem Evidenzpfad folgen

<details><summary>Verbatim baseline passage</summary>

````text
**Karte.** Lokalisiere das grobe Muster nach Entfernung und Richtung. Lies die Sektorfarbe stets zusammen mit der Unterstützung durch Stationen und Gelegenheiten, Spots beziehungsweise Paare. Ein eingefärbter Sektor ist eine Aufforderung zur näheren Prüfung und noch keine Schlussfolgerung.
````

</details>

### Original in 1.3 Dem Evidenzpfad folgen

<details><summary>Verbatim baseline passage</summary>

````text
**Performance- oder Benchmark-Evidenz.** Verbinde bei Performance Reichweite, beide Gewichtungen der Dekodierrate und erfolgreiches Target-SNR. Verbinde bei Benchmark stationsgleichgewichtetes und beobachtungsbezogenes Delta SNR, Decode Outcomes und Joint-Evidenzanteil. Diese Größen beantworten unterschiedliche Fragen und sollten nicht zu einer einzigen Kennzahl verdichtet werden.
````

</details>

### Original in 1.3 Dem Evidenzpfad folgen

<details><summary>Verbatim baseline passage</summary>

````text
**Zeitliche Evidenz.** Nutze die chronologische Ansicht, um Veränderungen während des Laufs zu erkennen, und die UTC-Stunden-Ansicht, um wiederkehrende Tageszeitmuster über mehrere Tage zu sehen. Lies Signalpegel stets gemeinsam mit der Unterstützung durch Stationen, Gelegenheiten oder Paare.
````

</details>

### Original in 1.3 Dem Evidenzpfad folgen

<details><summary>Verbatim baseline passage</summary>

````text
**Drill-Down.** Prüfe die beibehaltenen Gelegenheiten, Vergleiche desselben Zyklus hinter dem Ergebnis. Nutze Drill-Down, um Identitäten, Locatorwechsel, Zeitsteuerung, einseitige Evidenz und einzelne Ausreißer nachzuvollziehen.
````

</details>

### Original in 2.5.3 Ein berichtetes Ereignis lesen und untersuchen

<details><summary>Verbatim baseline passage</summary>

````text
**Als Nächstes den Funkweg prüfen.** Rechts neben jedem exakten Funkwegzeitraum stehen zwei grüne Aktionen. Beide wählen den Funkweg aus, laden den Drill-Down vor und öffnen den **`Ausreißerfokus`**:
````

</details>

### Original in 3.1 Breite, Konsistenz und Wiederholbarkeit beurteilen

<details><summary>Verbatim baseline passage</summary>

````text
* Identitäten der beteiligten Stationen;
* Umfang der qualifizierenden bestätigten Gelegenheiten, Spots;
* Übereinstimmung zwischen Stationen;
* stationsgleichgewichtete und beobachtungsbezogene Zusammenfassungen;
* benachbarte geografische Segmente;
* zeitliche Ansichten;
* Decode Outcomes;
* Qualität von Identitäten und Locator-Angaben;
* Kontrolle und Wiederholung des Versuchs.
````

</details>

### Original in 3.1 Breite, Konsistenz und Wiederholbarkeit beurteilen

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar verdichtet diese Dimensionen bewusst nicht zu einer einzigen Beweisstufe. Die sichtbaren Anzahlen, Verteilungen und zugrunde liegenden Zeilen ermöglichen eine Beurteilung im Kontext des tatsächlich durchgeführten Versuchs.
````

</details>

### Original in 3.1 Breite, Konsistenz und Wiederholbarkeit beurteilen

<details><summary>Verbatim baseline passage</summary>

````text
Das beobachtete zeitliche, entfernungs- oder richtungsabhängige Muster der Dekodierrate, des erfolgreichen SNR oder des Delta SNR ist die Evidenz. Eine Erklärung wie Antennenrichtwirkung, veränderter lokaler Störpegel, Ausbreitungsart, Übersteuerung oder ein intermittierendes Bauteil ist eine Interpretation. Formuliere zuerst passend zur Beobachtung und prüfe die Erklärung anschließend durch eine kontrollierte Änderung, einen Kreuztausch, eine unabhängige Messung oder Wiederholung.
````

</details>

### Original in 3.2 Ergebnis durch Wiederholung und Kontrolle absichern

<details><summary>Verbatim baseline passage</summary>

````text
TX und RX verwenden unterschiedliche Peer-Populationen und Gelegenheitsdefinitionen. Vergleiche gleichartige TX- und RX-Läufe, wenn du die Stationsbalance oder ein „Alligator“-Muster untersuchst.
````

</details>

### Original in 3.3 Evidenzgerechte Schlussfolgerung formulieren

<details><summary>Verbatim baseline passage</summary>

````text
Ein vollständiger technischer Bericht nennt zusätzlich:
````

</details>

### Original in 3.3 Evidenzgerechte Schlussfolgerung formulieren

<details><summary>Verbatim baseline passage</summary>

````text
* die zutreffenden Gewichtungsebenen: stationsgleichgewichtete Dekodierrate und Dekodierrate auf Gelegenheitsebene bei Performance beziehungsweise Delta SNR auf Stations- und Beobachtungsebene bei Benchmark;
* bei Performance die Anzahl qualifizierender Stationen und bestätigter Gelegenheiten, bei Benchmark die Anzahl der Joint-Stationen und Joint-Spots beziehungsweise -Paare;
* Decode Outcomes bei Benchmark;
* Versuchsbedingungen und eine etwaige Referenzkorrektur;
* Filter und Evidenzschwellen;
* ob sich das Muster über Zeit, Stationen oder Läufe wiederholte;
* jeden alternativen Radius oder Bereich, der als Sensitivitätsanalyse verwendet wurde.
````

</details>

### Original in 3.3 Evidenzgerechte Schlussfolgerung formulieren

<details><summary>Verbatim baseline passage</summary>

````text
> Für dieses Target, dieses Band, dieses UTC-Zeitfenster und die ausgewählte Peer-Population beschreibt die angezeigte Dekodierrate den Anteil der bestätigten Gelegenheiten, in denen auch das Target qualifizierende Evidenz lieferte. Gib an, ob die stationsgleichgewichtete Dekodierrate oder die Dekodierrate auf Gelegenheitsebene berichtet wird. Qualifizierende Stationen, bestätigte Gelegenheiten, geografischer Bereich und zeitliche Ansichten beschreiben Breite, Tiefe und Wiederkehr der stützenden Evidenz.
````

</details>

### Original in 3.3 Evidenzgerechte Schlussfolgerung formulieren

<details><summary>Verbatim baseline passage</summary>

````text
Eine vollständige Performance-Aussage kann zusätzlich nennen, ob die Mindestens-einmal-Reichweite breit oder begrenzt war, ob die Beteiligung beständig oder intermittierend war, wo Entfernungs- oder Richtungsmuster auftraten, ob sich ein UTC-Stunden-Muster wiederholte und wie sich das erfolgreiche Target-SNR verhielt. Beschreibe dies als beobachtetes WSPR-Verhalten der vollständigen Station unter den ausgewählten Bedingungen und nicht als isolierten Gewinn, Empfindlichkeit oder Wirkungsgrad.
````

</details>

### Original in 3.3 Evidenzgerechte Schlussfolgerung formulieren

<details><summary>Verbatim baseline passage</summary>

````text
> Für dieses Target, diese Referenz, dieses Band, dieses UTC-Zeitfenster und das ausgewählte Segment begünstigte das stationsgleichgewichtete Delta SNR Target/Referenz um den angezeigten Betrag. Das Delta SNR auf Beobachtungsebene, die Anzahlen der Joint-Stationen und Joint-Spots/-Paare, der Joint-Evidenzanteil und die Decode Outcomes beschreiben die stützende gepaarte und einseitige Evidenz.
````

</details>

### Original in 3.3 Evidenzgerechte Schlussfolgerung formulieren

<details><summary>Verbatim baseline passage</summary>

````text
Nenne bei einem Ergebnis eines kontrollierten Aufbaus die vollständigen verglichenen Pfade und jeden Kreuztausch oder jede Kalibrierung. Stelle bei einem Vergleich mit einer unabhängigen Referenzstation klar, dass vollständig aufgebaute Stationen und ihre Umgebungen gebenchmarkt wurden. Nenne bei einem Referenznachbarschaft den Radius und die wechselnde Referenzdefinition des lokalen Nachbarschafts-Medians.
````

</details>

### Original in 3.4 Lauf und Kontext sichern

<details><summary>Verbatim baseline passage</summary>

````text
Mit `Alle Ergebnisse zum Download vorbereiten` erstellst du das Exportpaket der aktuellen Analyse. Es enthält die aktuelle Konfiguration, Laufmetadaten, verarbeitete Evidenz, Tabellen und hochauflösende Abbildungen.
````

</details>

### Original in 3.4 Lauf und Kontext sichern

<details><summary>Verbatim baseline passage</summary>

````text
Bewahre zusammen mit diesem Paket externe Notizen auf zu:
````

</details>

### Original in 3.4 Lauf und Kontext sichern

<details><summary>Verbatim baseline passage</summary>

````text
* physischem Aufbau von Antenne und Speiseleitung;
* Umschalter- oder Splittertopologie;
* Sender- oder Empfängerhardware;
* Leistungsmessungen und Grundlage der Leistungsangaben;
* Decoder- und Softwareversionen;
* Betriebsplan, physischer Zuordnung des Zeitplans zu den Pfaden und jeder vertauschten Zuordnung;
* Kalibrierverfahren;
* Wetter, Störungen oder beabsichtigten Änderungen, die für den Lauf relevant waren.
````

</details>

### Original in Teil II: Bedienelemente und Fehlersuche

<details><summary>Verbatim baseline passage</summary>

````text
Die optionale fachkundige Nutzung der Delta-SNR-Ausreißererkennung für Benchmark wird in [Abschnitt 2.5](#sec-outlier) eingeführt. [Abschnitt 4.6](#sec-5-6) enthält ihre Bedienelemente; die formale wissenschaftliche Definition steht in [Abschnitt 7.11](#sec-7-11).
````

</details>

### Original in 4.1 Ablaufsteuerung

<details><summary>Verbatim baseline passage</summary>

````text
**Wiederverwendung von Demo-Daten.** Beim Ausführen einer unveränderten Demo werden fehlende Datenbank-Abfrageergebnisse abgerufen und validierte Zeilen auf dem Datenträger des App-Servers gespeichert. Spätere Läufe verwenden passende Einträge ohne automatischen Ablauf erneut, auch über Sitzungen und App-Neustarts hinweg, solange dieser Datenträger erhalten bleibt. Eine geänderte Abfrage, ein inkompatibles Cache-Format oder fehlende beziehungsweise beschädigte Dateien erfordern einen erneuten Abruf. Weder beim App-Start noch beim Laden einer Demo werden deren Daten vorab abgerufen. Die Wiederverwendung bewahrt die abgerufenen Archivdaten, statt spätere Archivkorrekturen automatisch zu übernehmen; jeder Lauf führt die Analyse weiterhin mit dem aktuellen Anwendungscode aus.
````

</details>

### Original in 4.2 Frage, Target und Messzeitraum

<details><summary>Verbatim baseline passage</summary>

````text
| UI-Bezeichnung | Standard | Funktion |
|---|---|---|
| **Frage** | keine; erforderlich | Eine Auswahl aus `RX Performance`, `TX Performance`, `RX-Benchmark` oder `TX-Benchmark`; legt Richtung und Ergebnistyp gemeinsam fest. |
| **Target-Rufzeichen (Empfänger im Test)** / **Target-Rufzeichen (Sender im Test)** | leer | Exakte Meldeidentität im Archiv. Standardrufzeichen, gültige Varianten mit `/`, reine Buchstabenkennungen und ein optionales abschließendes alphanumerisches Bindestrich-Suffix sind zulässig. |
| **Target-QTH (4 oder 6 Zeichen)** | leer | Target-Zuordnung über Grid-4, Kartenmittelpunkt, Geometrie und Ursprung des lokalen Radius. |
| **Frequenzband** | `20m` | Genau eines aus `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` oder `23cm`. |
| **UTC-Messzeitraum** | festes 24-Stunden-Fenster bis zur aktuellen UTC-Minute | Das absolute Evidenzintervall des Laufs. |
| **Startdatum/-zeit (UTC)** und **Enddatum/-zeit (UTC)** | das wirksame Standardfenster | Datumswerte beginnen im Jahr 2008; ein Lauf ist auf 31 verstrichene Tage begrenzt. Eingegebene Zeiten bleiben mit Minutengenauigkeit erhalten, ohne Rundung auf 15-Minuten-Grenzen. |
````

</details>

### Original in 4.2 Frage, Target und Messzeitraum

<details><summary>Verbatim baseline passage</summary>

````text
Verwende das Rufzeichen oder die Meldekennung exakt so, wie es beziehungsweise sie hochgeladen wurde. Nur als schematische Platzhalter stehen `CALL`, `CALL/1`, `CALL/2`, `CALL/P`, `CALL/QRP` und `CALL-1` für verschiedene exakte Archividentitäten. WSPRadar führt sie weder anhand des Basisrufzeichens zusammen noch wendet es eine verdeckte Präfix- oder Suffixzuordnung an. Die Beispiele zeigen lediglich die Zuordnungssyntax; sie begründen weder die Zuteilung noch die Berechtigung, eine dieser Identitäten zu senden. Verwende nur ein vollständiges Rufzeichen, das für den Bediener und die Betriebsumstände zulässig ist.
````

</details>

### Original in 4.2 Frage, Target und Messzeitraum

<details><summary>Verbatim baseline passage</summary>

````text
Ein vierstelliger Maidenhead-Locator bezeichnet ein größeres Locator-Feld, sechs Zeichen ein kleineres Unterfeld darin. WSPRadar verwendet das konfigurierte QTH als Kartenmittelpunkt und Ursprung des lokalen Radius. Performance und Benchmark wählen Target-Zeilen im Archiv anhand des exakten Rufzeichens plus der ersten vier Zeichen des Target-QTHs. Das vollständige QTH verankert weiterhin Karte, Entfernung, Azimut, Sonnenstand und lokale Nachbarschaftsgeometrie.
````

</details>

### Original in 4.3 Benchmark-Design und -Einstellungen

<details><summary>Verbatim baseline passage</summary>

````text
Bei `RX Performance` und `TX Performance` entfällt der Bereich **`Benchmark-Design`** vollständig, weil Performance keine Referenz verwendet. Der abschließende Prüfbereich erscheint nach dem gemeinsamen Bereich für Filter, Umfang und Evidenz. Beim Start werden ungültige oder unvollständige Felder direkt mit roter Rückmeldung und konkreter Korrekturhilfe markiert; die Korrektur eines Feldes entfernt dessen Hinweis. Fehler beim Archivzugriff werden von einem ungültigen Rufzeichen oder einem leeren Meldezeitfenster getrennt ausgewiesen. Performance und Benchmark sind sich gegenseitig ausschließende Ergebnistypen: Ein Lauf erzeugt nur das ausgewählte Ergebnis. [Abschnitt 8.4](#sec-8-4) fasst ausgewählte öffentliche maschinenlesbare Bezeichnungen für Konfiguration, URL und Export zusammen; er ist kein vollständiger Feld- oder Parameterkatalog.
````

</details>

### Original in 4.3 Benchmark-Design und -Einstellungen

<details><summary>Verbatim baseline passage</summary>

````text
| UI-Bezeichnung | Standard / Wertebereich | Gilt für | Wissenschaftliche Wirkung |
|---|---|---|---|
| **Gibt es einen ermittelten Target–Referenz-<br>Offset?** | `Kein ermittelter Offset — 0,0 dB verwenden` | Geführtes Referenzaufbau/<br>-station | Unterscheidet keinen ermittelten Offset, die Verwendung einer ermittelten Korrektur und einen gezielten Offset-Ermittlungslauf. |
| **Referenzseitige SNR-Korrektur (dB)** | leer = `0.0`; `-99.9` bis `+99.9 dB` | Benchmark | Wird zum Referenz-SNR addiert, bevor Delta SNR Target minus Referenz berechnet wird. Dezimalwerte werden mit Punkt eingegeben, beispielsweise `1.2`. |
| **Referenz-<br>Rufzeichen** | leer | Referenzaufbau/<br>-station | Exakte Meldeidentität der Referenz. |
| **Referenzstandort** | aus dem ausgewählten Archiv ermittelt | Referenzaufbau/<br>-station | Ein beobachtetes Grid-4 wird automatisch aufgelöst; bei mehreren gemeldeten Grid-4 ist eine ausdrückliche Auswahl nötig. Ein zusätzlicher manueller Referenz-Locator ist nicht erforderlich. |
| **Nachbarschafts-<br>radius (km)** | `100`; 10–250 km in 10-km-Schritten | Referenz-<br>nachbarschaft | Definiert den lokalen Referenzpool um das Target-QTH. |
````

</details>

### Original in 4.3 Benchmark-Design und -Einstellungen

<details><summary>Verbatim baseline passage</summary>

````text
Gib nur das exakte Referenzrufzeichen ein. Das Target-QTH bleibt der einzige manuell eingegebene Analyse-Locator und der Ursprung für Karte, Entfernung, Azimut, Sonnenstand und Nachbarschaftsgeometrie. Die Referenzstandortsuche gilt für die ausgewählte Rolle, das Band, das effektive UTC-Zeitfenster und das Archiv. Ein beobachtetes Grid-4 wird automatisch aufgelöst; bei mehreren Kandidaten ist deine Auswahl erforderlich. Angezeigt werden die vollständigen Locatorvarianten, Meldungszahlen sowie erste und letzte Meldezeit. Eine erfolgreiche Suche ohne passende Meldungen ist von einem Datenquellenfehler getrennt. Dasselbe Archiv liefert die anschließende Analyse; das aufgelöste Grid-4 bleibt in der gespeicherten Analysedefinition erhalten.
````

</details>

### Original in 4.3 Benchmark-Design und -Einstellungen

<details><summary>Verbatim baseline passage</summary>

````text
Unterschiedliche gemeldete Felder können getrennte Standorte oder falsche Archivmetadaten bedeuten; die gemeldeten Locator beweisen keine der beiden Erklärungen. Passen keine geeigneten Target-Meldungen zum eingegebenen Target-QTH, prüfe die Eingaben; der Analyseursprung wird niemals automatisch geändert.
````

</details>

### Original in Vorzeichen der referenzseitigen SNR-Korrektur

<details><summary>Verbatim baseline passage</summary>

````text
Eine positive Korrektur erhöht das korrigierte Referenz-SNR und verringert dadurch Delta SNR Target minus Referenz. Gib einen gemessenen Kalibrierversatz `target - reference` mit demselben Vorzeichen ein. Ergibt eine Kalibrierung mit gemeinsamem Eingang beispielsweise `+1.6 dB`, wird `+1.6 dB` eingetragen. [Abschnitt 7.5](#sec-7-5) definiert die Gleichungen.
````

</details>

### Original in 4.4 Filter und Evidenzschwellen

<details><summary>Verbatim baseline passage</summary>

````text
| Bedienelement | Standard | Gilt für | Wirkung und Verwendung |
|---|---|---|---|
| **Spezial-Rufzeichen Q, 0, 1 ausschließen** | bei Performance ein; bei Benchmark aus | alle Ergebnisse | Schließt entfernte Peer-Rufzeichen aus, die mit `Q`, `0` oder `1` beginnen: sendende Peers in RX-Analysen und empfangende Peers in TX-Analysen. Target- und Referenzstationen einschließlich der Stationen, die zur Referenz der lokalen Nachbarschaft beitragen, bleiben von diesem Filter unberührt. Die Präfixregel stellt nicht fest, ob eine Station Telemetrie überträgt. Behalte baken- oder telemetrieartige Identitäten, wenn sie zur Fragestellung gehören; schließe sie aus, wenn reguläre Amateurfunkaktivität untersucht werden soll. |
| **Bewegliche Stationen filtern** | bei Performance ein; bei Benchmark aus | kartierte Peers | Schließt Rufzeichen aus, die in der ansonsten qualifizierenden globalen Population mehr als ein Grid-4 melden. Nutze Drill-Down, um Bewegung von fehlerhaften Locator-Angaben zu unterscheiden. |
| **Sonnenstand am Target-QTH** | `Ganze 24h` | alle Ergebnisse | Behält je nach Sonnenhöhe am Target-QTH `Tag (Elev > +6°)`, `Nacht (Elev < -6°)`, `Greyline (-6° bis +6°)` oder alle Zyklen bei. |
| **Maximale Peer-Entfernung vom Target (km)** | `22000`; Auswahl `2500`, `5000`, `10000`, `15000`, `20000`, `22000` | alle Ergebnisse | Entfernt Peers ab der ausgewählten Entfernung aus Analyse, verarbeiteten Artefakten und Exporten. Das Target-Active Gate darf Evidenz außerhalb des Bereichs weiterhin ausschließlich dazu verwenden, Target-Betrieb nachzuweisen. |
| **Minimale Joint-Evidenz pro Station** | `1`; Bereich 1–50 | simultaner Benchmark | Verlangt wiederholte Joint-Peer-Zyklen, bevor eine Station gepaartes Delta SNR beiträgt; derselbe Zahlenwert gilt auch als Untergrenze für exklusive Kategorien. |
| **Minimale bestätigte Gelegenheiten pro Station** | `5`; Bereich 1–100 | Performance | Verlangt ausreichend Target- plus Gegen-Gelegenheiten, bevor ein Peer beiträgt. Niedrige Werte erhöhen die Abdeckung, machen die Raten aber grob und schwach gestützt. |
| **Minimale qualifizierte Stationen pro Kartensegment** | `1`; Bereich 1–10 | alle Karten | Verlangt breitere Identitätsunterstützung, bevor ein Segment gezeichnet wird. |
````

</details>

### Original in 4.4 Filter und Evidenzschwellen

<details><summary>Verbatim baseline passage</summary>

````text
`Maximale Peer-Entfernung vom Target (km)` begrenzt die ausgewertete Population erst, nachdem die Archivzeilen abgerufen wurden. Eine Verringerung umgeht deshalb nicht die Zeilengrenze des Archivs. Ein kleinerer lokaler Nachbarschaftsradius und `Spezial-Rufzeichen Q, 0, 1 ausschließen` können bei bestimmten Analysen die abgerufene Population verkleinern; [Abschnitt 5.6](#sec-6-6) behandelt zu große Abrufe.
````

</details>

### Original in 4.5 Karten-, Inspektor- und Exporteinstellungen

<details><summary>Verbatim baseline passage</summary>

````text
| Bedienelement | Wirkung | Gespeichert? | Neuer Lauf? |
|---|---|---|---|
| Entfernung und Richtung des Segments | Aktiver geografischer Inspektionsbereich | getrennt für Performance und Benchmark | Nein |
| `Nur von anderen Stationen gehört.` / `Nur andere Signale gehört.` | Sichtbarkeit von Performance-Peers mit ausschließlich Gegen-Evidenz | Ja | Nein |
| `Ungepaarte Evidenz einbeziehen` | Sichtbarkeit von Benchmark-Identitäten, die nur exklusive oder asynchrone Evidenz besitzen | Ja | Nein |
| Ausgewählte Stationszeile | Evidenz der ausgewählten Station und ausgewählte Drill-Down-Identität | genau ein `Rufzeichen + Locator` je Ergebnistyp | Nein |
| Zeitaggregation des Segments | Chronologische zeitliche Ansicht des Segment-Inspektors; die Auswahl passt sich an die Laufdauer an | Ja | Nein |
| Zeitaggregation der ausgewählten Station | Chronologische Ansicht des ausgewählten Funkwegs; die Auswahl passt sich an die Laufdauer an | Ja | Nein |
| **`Zoom-Zeitfenster`**, **`Datum der Fenstermitte (UTC)`**, **`Uhrzeit der Fenstermitte (UTC)`**, **`← Früher`**, **`Später →`**, **`Ausreißerfokus`** und **`Tabelle filtern`** | Optionale Drill-Down-Abbildungen in nativer Zeitauflösung und zentriertes Tabellenintervall für genau eine ausgewählte Station; die Tabellenfilterung betrifft nur angezeigte Zeilen | Nein | Nein |
| `Alle Ergebnisse zum Download vorbereiten` | Exportpaket und aktuelle Inspektor-Auswahlen | nicht zutreffend | Nein |
````

</details>

### Original in 4.5 Karten-, Inspektor- und Exporteinstellungen

<details><summary>Verbatim baseline passage</summary>

````text
Der Drill-Down-Zoom ist flüchtig und nur für genau eine ausgewählte Station verfügbar. Wähle **`Aus`** oder ein vollständiges Intervall von `1h`, `3h`, `6h`, `12h` beziehungsweise `24h`. **`Datum der Fenstermitte (UTC)`** und **`Uhrzeit der Fenstermitte (UTC)`** wählen die Mitte dieses Intervalls; WSPRadar leitet daraus exakten Start und exaktes Ende ab, verschiebt das vollständige Intervall an einer Laufgrenze, statt es zu kürzen, und lässt es mit **`← Früher`** beziehungsweise **`Später →`** um ein vollständiges ausgewähltes Fenster versetzen. Die aufgelösten Grenzen erscheinen in einer Zeile als **`Ausgewähltes Zeitfenster: {start} bis {end} UTC`**. Der Zoom begrenzt die fokussierten Abbildungen und die Drill-Down-Tabelle; **`Tabelle filtern`** verändert anschließend nur die angezeigte Tabelle und niemals die fokussierten Abbildungen oder die abgeschlossene Analyse. Seine Messwertabbildung ist bewusst kein Zwei-Minuten-Aggregat: Der simultane Benchmark zeigt einen tatsächlichen Delta-SNR-Punkt je beibehaltenem Joint Spot zu seiner kanonischen Zykluszeit; Performance zeigt das tatsächliche normierte Target-SNR jeder erfolgreichen bestätigten Gelegenheit zu ihrer kanonischen Zykluszeit. Dies sind einzelne beibehaltene wissenschaftliche Evidenzeinheiten nach Zusammenführung, Zuordnung und Filtern durch WSPRadar und keine unveränderten Provider-Zeilen. In der fokussierten Messwertansicht entfallen Binmedian, IQR, Dichtehintergrund, Farbskala, Median des vollständigen Laufs und nach UTC-Stunde gefaltetes Messwertpanel. Die ergänzende Performance-Outcome- beziehungsweise Benchmark-Abdeckungsansicht darf ihre chronologische Aggregation beibehalten; Segmentansicht und Evidenz der ausgewählten Station über das vollständige Fenster bleiben dichtebasierte aggregierte Ansichten. Titel fokussierter Abbildungen verwenden das kompakte Format **`DG2CAD (JN47mv) - Zeitfenster: {start} bis {end} UTC`**.
````

</details>

### Original in 4.5 Karten-, Inspektor- und Exporteinstellungen

<details><summary>Verbatim baseline passage</summary>

````text
Eine Ausreißeraktion lädt den **`Ausreißerfokus`** über die vollständige gestützte Baseline-Flanke vor dem Ereignis, die geschützte vorläufige Episode und die Flanke danach vor; begrenzt wird dieses Intervall nur durch das abgeschlossene Analysefenster, und es darf länger als 24 Stunden sein. Die Kandidatenprovenienz bleibt erhalten, wenn der Bediener zu einem manuellen festen Fenster wechselt. In einer fokussierten Benchmark-Abbildung kennzeichnen identische `*`-Marker jede native Einheit im aktuellen Fenster, die innerhalb eines gemeldeten Kandidaten einzeln sowohl das konfigurierte Abweichungs- als auch das robuste-z-Kriterium erfüllt; ein dezentes Band **Fokussierte Episode** unterscheidet die ausgewählte berichtete Episode. Das Band umfasst deren berichtetes Intervall der beibehaltenen Evidenz mit einer halben Breite der nativen Evidenzeinheit als Erweiterung an jedem Ende und wird am Fokusfenster abgeschnitten, damit ein Impuls sichtbar bleibt. Es ist ein Auswahlhinweis und kein Konfidenzintervall oder Maß der physischen Dauer. Erwartetes lokales Delta SNR, zeitlich begrenzte Baselines der Flanken davor und danach, robuste-z-Hilfslinien bei 1, 2 und 3 sowie an der konfigurierten Qualifikationsschwelle und die konfigurierte Grenze der absoluten Abweichung gehören ausschließlich zur fokussierten Episode; andere markierte Kandidaten können andere Baselines und robuste Streuungen besitzen. Robuste-z- und Abweichungslinien sind Detektorhilfen und keine Konfidenzintervalle; das Überschreiten einer einzelnen Linie erfüllt nicht die getrennten Anforderungen des Detektors an Stützung, Stabilität, Ereignis und Vorzeichenübereinstimmung. Manueller und ausreißerverknüpfter Fokus gehören weder zur Analysedefinition noch zur gespeicherten Konfiguration oder öffentlichen URL. Bei aktivem Fokus kann der Export getrennte Fokusabbildungen ergänzen, ohne die normalen Abbildungen der ausgewählten Station über den vollständigen Lauf zu ersetzen. Die Exportinhalte stehen in [Abschnitt 8.4](#sec-8-4).
````

</details>

### Original in 4.6 Bedienelemente der Benchmark-Ausreißererkennung

<details><summary>Verbatim baseline passage</summary>

````text
Die Delta-SNR-Ausreißererkennung für Benchmark ist eine optionale fachkundige Analyseebene über der beibehaltenen nativen gepaarten Evidenz. Eine native gepaarte Einheit ist ein simultaner **Joint Spot**. Die Erkennung läuft getrennt für jeden exakten Peer-Funkweg `Rufzeichen + Locator` und unabhängig vom ausgewählten Darstellungs-Bin der **Zeitlichen Evidenz**. Einseitige Evidenz kann ein fehlendes Delta SNR nicht ersetzen. [Abschnitt 2.5](#sec-outlier) erklärt Bedienung und Interpretation; [Abschnitt 7.11](#sec-7-11) definiert die Methode formal.
````

</details>

### Original in 5.2 Fehler nach Symptom eingrenzen

<details><summary>Verbatim baseline passage</summary>

````text
| Symptom | Nächste Prüfungen |
|---|---|
| **Keine exakte Target-/Quellenevidenz wurde geliefert** | Prüfe genaue Identität, QTH, Band, Zeitfenster und tatsächlichen Betrieb sowie den gemeldeten Status der strengen Abfrage mit `code = 1`, des historischen Fallbacks und der Upstream-Verfügbarkeit. Dieser Zustand betrifft Eingabe beziehungsweise Quellenevidenz und belegt nicht, dass die konfigurierten Filter zu eng waren. |
| **Quellenevidenz wurde geliefert, aber Filter oder Umfang behielten nichts bei** | Prüfe die angezeigten Stationsausschlüsse, den Sonnenstand und die maximale Peer-Entfernung zusammen mit dem Zeitraum des abgeschlossenen Laufs. Der Hinweis sagt nur, dass angewandte Filter und Umfang keine Evidenz beibehielten; geringe Betriebsaktivität oder Abdeckung können ebenfalls beitragen. |
| **Performance-Identitäten bleiben erhalten, aber keine Station erfüllt die Anforderung an bestätigte Gelegenheiten** | Vergleiche die angezeigte beobachtete Stationsanzahl und die höchste Anzahl bestätigter Gelegenheiten mit dem konfigurierten Minimum bestätigter Gelegenheiten pro Station. Leere Karten, Inspektoren und Tabellen entfallen, statt als Nullergebnisse angezeigt zu werden. |
| **Performance-Stationen qualifizieren sich, aber kein Kartensegment erfüllt seine Stationsanforderung** | Behalte und untersuche die verfügbare Evidenz auf Stationsebene. Nur segmentabhängige Ausgaben fehlen; vergleiche deren Stationsunterstützung mit der konfigurierten Mindestanzahl qualifizierter Stationen pro Kartensegment. |
| **Kein qualifizierendes Benchmark-Ergebnis bleibt erhalten** | Prüfe die konfigurierte Anforderung an Joint-Evidenz, die Mindestanzahl qualifizierter Stationen pro Kartensegment, Filter und Umfang. WSPRadar nennt diese angewandten Anforderungen, erfindet jedoch keine beobachteten Benchmark-Maxima, die die Pipeline nicht berechnet hat. |
| **Benchmark enthält kein Delta SNR** | Prüfe gemeinsame entfernte Peers in überlappenden Zyklen, Referenzbetriebszeit, Uhren, Zeitplanzuordnung, Joint-Schwelle, Filter und Bereich. |
| **Benchmark enthält Delta SNR, aber wenig paarbare Evidenz** | Lies Joint-Evidenzanteil und Decode Outcomes; prüfe Referenzbetriebszeit, Leistung, Schwellen, Bereich und ob die gepaarte Teilmenge die breitere Stationspopulation repräsentiert. |
| **Performance enthält nur sehr wenige Peers** | Prüfe unabhängige Netzaktivität, minimale bestätigte Gelegenheiten, Ausschlüsse, Sonnenstand, Zeitfenster und maximale Peer-Entfernung. |
| **Viele Performance-Erfolge ohne externe Bestätigung** | Ein gültiger Target-Decode bestätigt selbst beide Endpunkte. Diese Target-only-Erfolge gehen einmal in die Dekodierrate ein; ihre separate Herkunftsanzahl wird nicht nochmals addiert. Ohne Target-Decode und ohne den erforderlichen externen Aktivitätsnachweis bleibt der Peer-Zyklus unbekannt und ausgeschlossen. |
| **`Only Reference = 0`** | Prüfe die Konditionierung auf Target-Aktivität, Schwellen und aktiven Bereich; null kann korrekt sein. |
| **Unerwartetes Vorzeichen des Delta SNR bei Referenzaufbau/-station** | Prüfe physische A/B-Zuordnung, Reihenfolge von Target und Referenz, Korrekturvorzeichen, tatsächliche und gemeldete Leistung sowie Kalibrierung. Gleiche einen Funkweg im Drill-Down ab. |
| **Lokales Ergebnis verändert sich mit dem Radius** | Untersuche die lokalen Beitragenden und berichte die Radiusabhängigkeit, statt nur den günstigsten Radius auszuwählen. |
| **Der Lauf wird wegen zu großer Quellmenge beendet** | Verkürze das UTC-Zeitfenster. `Spezial-Rufzeichen Q, 0, 1 ausschließen` oder ein kleinerer lokaler Nachbarschaftsradius können zutreffende Quellabfragen verkleinern; die maximale Peer-Entfernung nicht, weil sie erst nach dem Abruf angewandt wird. |
| **Aktuelle Spots erscheinen unvollständig** | Warte nach dem letzten Zyklus ungefähr fünf Minuten und prüfe danach Upload und Upstream-Status. |
````

</details>

### Original in 5.3 Rufzeichen und Locator prüfen

<details><summary>Verbatim baseline passage</summary>

````text
Referenzaufbau/-station verwendet das exakte Referenzrufzeichen zusammen mit dem aus dem ausgewählten Archivzeitfenster aufgelösten Grid-4. Die Suche berücksichtigt Referenzrolle (RX oder TX), Band, effektives UTC-Zeitfenster und Datenquelle. Ein gemeldetes Grid-4 wird automatisch aufgelöst; mehrere erfordern eine ausdrückliche Auswahl. Vollständige gemeldete Locatorvarianten, Meldungszahlen sowie erste und letzte Meldezeit unterstützen die Auswahl. Der Standort dient als Archivselektor und ist kein bestätigter physischer Standort. Die Referenznachbarschaft wählt ihre Beiträge geografisch aus.
````

</details>

### Original in 5.3 Rufzeichen und Locator prüfen

<details><summary>Verbatim baseline passage</summary>

````text
**Simultanes TX mit zusammengesetzten Rufzeichen.** WSPRadar rekonstruiert Typ-2- und Typ-3-Nachrichten nicht und leitet einen fehlenden Sender-Locator nicht aus einer benachbarten Aussendung ab. Prüfe vor dem Sammeln von Evidenz mehrere Upstream-Spots und bestätige, dass die für den WSPRadar-Lauf ausgewählte Datenquelle beide exakten Identitäten im gemeinsamen Target-Grid-4 meldet. Wird eine Identität ohne verwendbaren Locator oder mit einem anderen Grid-4 bereitgestellt, erfüllen diese Zeilen die Identitätszuordnung von Referenzaufbau/-station nicht.
````

</details>

### Original in 5.4 Fallback für historische Decode-Codes

<details><summary>Verbatim baseline passage</summary>

````text
WSPR-2 ist der Standard-WSPR-Modus mit zweiminütigen Sendezyklen; `code` enthält die in der Datenbank gespeicherte Modusangabe. Bei älteren Archivmeldungen können Modusangaben fehlen oder mehrdeutig sein, und die historische Kompatibilitätsabfrage kann Beobachtungen einschließen, deren physikalische Übertragungsart nicht festgestellt werden kann. Der Stichtag ist eine Kompatibilitätsregel und kein belegtes Datum, ab dem sämtliche Modusangaben im Archiv zuverlässig wurden. Auch historisches `code = 1` kann mehrdeutig sein [Ref-10]. Laufstatus und exportiertes `decode_filter_mode` dokumentieren die Abfrageauswahl, ohne zu belegen, dass jede ausgewählte Beobachtung WSPR-2 ist. Ist ein Zeitraum nicht für den Fallback zulässig und liefert die strenge Abfrage keine Target-seitige Evidenz, erläutert WSPRadar den WSPR-2-Filter und den historischen Stichtag; dies belegt nicht, dass das Target einen anderen Modus verwendet hat.
````

</details>

### Original in 5.6 Umgang mit Upstream-Daten

<details><summary>Verbatim baseline passage</summary>

````text
Öffentliche WSPR-Archive können Duplikate, falsche Spots, fehlerhafte Locator oder Leistungsangaben, verspätete Uploads und spätere Korrekturen enthalten. wspr.live beschreibt aktuelle Daten als um einige Minuten verzögert. Etwa **fünf Minuten** nach dem letzten Zyklus zu warten ist eine praktische Schätzung und keine Vollständigkeitsgarantie <a href="#ref-10">[Ref-10]</a>.
````

</details>

### Original in 5.6 Umgang mit Upstream-Daten

<details><summary>Verbatim baseline passage</summary>

````text
| Statuselement | Bedeutung |
|---|---|
| **Datenquelle** | Das eine Upstream-Archiv, das für den abgeschlossenen Lauf verwendet wurde. Evidenz verschiedener Archive wird innerhalb eines Laufs nicht vermischt. |
| **Historischer Fallback** | Ob die Auswahl ohne die strenge Bedingung für den WSPR-2-Decode-Code wiederholt wurde. |
````

</details>

### Original in 5.6 Umgang mit Upstream-Daten

<details><summary>Verbatim baseline passage</summary>

````text
Ein Archivabruf mit mehr als 1.000.000 vollständigen Zeilen wird vor der Analyse abgelehnt und nicht stillschweigend abgeschnitten. Verkürze das Zeitfenster oder verwende einen passenden archivseitigen Populationsfilter wie in [Abschnitt 5.2](#sec-6-2) beschrieben.
````

</details>

### Original in Teil III: Wissenschaftliche Grundlagen, Methoden und Aussagen

<details><summary>Verbatim baseline passage</summary>

````text
Teil III ist die wissenschaftliche Methodenreferenz für technisch kritisch arbeitende Funkamateure, HamSCI-Mitwirkende und Gutachter. Er definiert Beobachtungsdaten, gebildete Evidenzeinheiten, Analyseziele, deskriptive Zusammenfassungen, Konditionierung, fehlende Beobachtungen, Gewichtung, Abhängigkeiten, Transformationen und Reproduzierbarkeitsgrenzen von WSPRadar. Dieser Teil ist bewusst formaler als der Leitfaden für den Funkbetrieb, erklärt die Formeln aber zusätzlich in verständlicher Stationssprache.
````

</details>

### Original in 6. Literatur, Vorarbeiten und Einordnung

<details><summary>Verbatim baseline passage</summary>

````text
Dieses Kapitel ist eine fokussierte methodische Übersicht und keine systematische oder erschöpfende Literaturrecherche. Begutachtete Fachartikel, Preprints, technische Erfahrungsberichte aus dem Amateurfunk und Softwaredokumentation stützen unterschiedliche Arten von Aussagen; jede Quelle wird nur für den Beitrag verwendet, den sie tatsächlich belegt. Die Übersicht bedeutet nicht, dass die Vorarbeiten jede WSPRadar-Kennzahl oder methodische Entscheidung validieren.
````

</details>

### Original in 6.1 Vom Meldenetz zum Versuchsdatensatz

<details><summary>Verbatim baseline passage</summary>

````text
Taylor und Walker stellten WSPRnet nicht nur als Live-Karte, sondern auch als Archiv vor: „The WSPRnet database represents a rich source of experimental data for propagation studies.“ Ihr Beispiel gruppiert Beobachtungen über mehrere Wochen nach Tageszeit. Es zeigt sowohl den Wert angesammelter Meldungen als auch die Notwendigkeit, sie als Beobachtungsdaten und nicht als kontrollierte Labordaten zu interpretieren. <a href="#ref-6">[Ref-6]</a>
````

</details>

### Original in 6.1 Vom Meldenetz zum Versuchsdatensatz

<details><summary>Verbatim baseline passage</summary>

````text
Frissell et al. ordnen WSPRNet zusammen mit dem Reverse Beacon Network und PSKReporter als etablierte Amateurfunk-Beobachtungsnetze ein, die langfristige Beobachtungen der unteren Ionosphäre liefern. Sie unterscheiden diese Netze von zweckgebundenen wissenschaftlichen Instrumenten und empfehlen eine Kreuzkalibrierung zwischen Instrumentennetzen. Die Übersicht stützt die wissenschaftliche Nutzung von Amateurfunkbeobachtungen; sie macht nicht jeden beitragenden Empfänger zu einem kalibrierten Sensor. <a href="#ref-7">[Ref-7]</a>
````

</details>

### Original in 6.1 Vom Meldenetz zum Versuchsdatensatz

<details><summary>Verbatim baseline passage</summary>

````text
Das WSPR-Archiv verbindet damit eine ungewöhnliche zeitliche Tiefe und geografische Reichweite mit heterogenen Stationen, einer Auswahl erfolgreicher Decodes, von Nutzern gemeldeten Identitäten und Leistungen, wechselnder Ausrüstung und meist unbekannten Betriebsplänen. Diese Eigenschaften erfordern ausdrücklich definierte Zulässigkeit und Konditionierung, statt das Ausbleiben eines Spots unmittelbar zu interpretieren.
````

</details>

### Original in 6.2 WSPR-Beobachtungsdaten interpretierbar machen

<details><summary>Verbatim baseline passage</summary>

````text
Dieses Prinzip der Aktivitätsprüfung ist eine direkte methodische Vorarbeit für das Target-Active Gate und die bestätigten Gelegenheiten von WSPRadar: Funkstille sollte erst dann zu Gegen-Evidenz werden, wenn der relevante Betrieb beobachtbar ist. Lo et al. definieren jedoch weder die asymmetrische Target-Konditionierung von WSPRadar noch dessen Performance-Analyseziel, Stationsgewichtung, Decode Outcomes oder lokale Referenzen; diese bleiben WSPRadar-Designentscheidungen für andere Analysefragen.
````

</details>

### Original in 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-d-toledo"></a>
**Toledo (2010): Warum langsames Abwechseln scheitert.** Sivan Toledo erprobte ungefähr eine Stunde lang eine Antenne und anschließend eine andere. Dabei änderte sich das SNR des Funkwegs in derselben Größenordnung wie der scheinbare Antennenunterschied. Er folgerte, dass dieser naive Aufbau die Antennen nicht isolieren konnte, und schlug eine Umschaltung in jedem Zyklus oder simultane Aussendungen mit getrennter Hardware vor. WSPRadar unterstützt die Alternative desselben Zyklus; die Analyse paart keine unterschiedlichen Sendezyklen. <a href="#ref-3">[Ref-3]</a>
````

</details>

### Original in 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-d-milazzo"></a>
**Milazzo (2011): Vom Funkamateur durchgeführter End-to-End-Vergleich.** Carol Milazzo verglich zwei 29 km voneinander entfernte Stationen über einen gemeinsamen Empfänger in 1.750 km Entfernung, korrigierte die gemeldeten SNR-Werte um Unterschiede der Sendeleistung, verglich den Verlauf mit VOACAP, berücksichtigte unterschiedliche Tastgrade und untersuchte reziproke RX-Meldungen. Die Fallstudie zeigt den praktischen Wert eines WSPR-Vergleichs über denselben Empfänger, macht aber zugleich die Grenzen durch unterschiedliche QTHs, Hardware, lokalen Störpegel, nur einen ausgewählten Empfänger und eine fehlende formale Unsicherheitsanalyse sichtbar. <a href="#ref-4">[Ref-4]</a>
````

</details>

### Original in 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels und Lamy (2022): Konditioniertes simultanes RX.** Ihr begutachteter Versuch konditionierte zwei nominell identische 160-m-WSPR-Empfangsstationen und verglich gemeinsame entfernte Aussendungen simultan. Innerhalb der hier betrachteten Quellen ist dies die stärkste direkte Vorarbeit für RX Referenzaufbau/-station und für die Charakterisierung von Offsets zwischen Empfangsketten vor der Interpretation von Antennenunterschieden. Die Ausbreitungsergebnisse zeigen außerdem, dass Polarisation und ionosphärische Effekte mit dem gemeldeten SNR gekoppelt bleiben. <a href="#ref-2">[Ref-2]</a>
````

</details>

### Original in 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen

<details><summary>Verbatim baseline passage</summary>

````text
Zander berichtet je Vorversuch ungefähr 1.000 Beobachtungen, von denen etwa 150–200 gemeinsame Meldungen aus 15–35 Empfängern beibehalten wurden; die Stichproben-Standardabweichung lag nahe 3 dB. Die Aussage der Arbeit im Sub-dB-Bereich betrifft die Präzision eines arithmetischen Mittels unter den Modell- und Stichprobenannahmen und keine rückführbare Gesamtgenauigkeit. Geografische Stichprobe, Antennenrichtwirkung und unbekannte Elevationswinkel bleiben systematische Grenzen. Die Studie stützt simultanes Delta SNR am selben Empfänger, nicht jedoch stationsgleichgewichtete Mediane, Decode Outcomes oder Nachbarschaftsreferenzen.
````

</details>

### Original in 6.4 Analyseinfrastruktur und verwandte Werkzeuge

<details><summary>Verbatim baseline passage</summary>

````text
Griffiths und Robinett demonstrierten einen relationalen Zeitreihen-Self-Join für denselben Sender, dieselbe Zeit und dasselbe Band, gemeldet von zwei Empfängern, zusammen mit Diagrammen der SNR-Differenz, Medianen, Quartilen, Zeit-Heatmaps, Entfernungs-/Azimutansichten und Export. Dies ist eine wichtige Vorarbeit für prüfbare Vergleichsinfrastruktur, nicht jedoch für die exakten Zulässigkeits-, Konditionierungs- oder Zusammenfassungsdefinitionen von WSPRadar. <a href="#ref-13">[Ref-13]</a>
````

</details>

### Original in 6.4 Analyseinfrastruktur und verwandte Werkzeuge

<details><summary>Verbatim baseline passage</summary>

````text
Diese Systeme belegen umfangreiche Vorarbeiten bei Datenerfassung, Exploration, Rangbildung, Vergleich, Kartendarstellung und Berichterstattung. Die Einordnung von WSPRadar beruht daher auf integrierten Versuchsdefinitionen, konditionierten Populationen, hierarchischer Gewichtung, ergänzender gepaarter und einseitiger Evidenz sowie dem Auditpfad – nicht auf der Behauptung, das erste WSPR-Analysewerkzeug zu sein.
````

</details>

### Original in 6.5 Was WSPRadar übernimmt, integriert und ergänzt

<details><summary>Verbatim baseline passage</summary>

````text
* Performance auf Grundlage bestätigter Gelegenheiten;
* Referenzaufbau/-station und dynamischer Referenznachbarschaft;
* Zuordnung im selben Zyklus;
* Normierung anhand gemeldeter Leistung und optionaler referenzseitiger Korrektur;
* gepaartem Delta SNR, getrennt von einseitigen Decode Outcomes;
* stationsgleichgewichteten und beobachtungsbezogenen Zusammenfassungen;
* einem Auditpfad von Karte über Segment und Station bis zur Zeile; und
* versionierter Konfiguration, verarbeiteter Evidenz und Reproduzierbarkeitsexport.
````

</details>

### Original in 6.5 Was WSPRadar übernimmt, integriert und ergänzt

<details><summary>Verbatim baseline passage</summary>

````text
Dies ist eine begrenzte Aussage über Integration und Methode und kein globaler Prioritätsanspruch. Medianaggregation an sich ist nicht neu. WSPRadar sollte als strukturierte Versuchs- und Auditschicht oberhalb eines Spot-Browsers beschrieben werden und nicht als Ersatz für Upstream-Archive, andere Analysewerkzeuge oder kalibrierte HF-Messtechnik.
````

</details>

### Original in 7. Wissenschaftliche Methoden

<details><summary>Verbatim baseline passage</summary>

````text
Dieses Kapitel definiert den wissenschaftlichen Vertrag eines WSPRadar-Laufs. WSPRadar beginnt mit gemeldeten Beobachtungen, bildet daraus zulässige Evidenzeinheiten, leitet Größen wie normiertes SNR und gepaartes Delta SNR ab und berechnet anschließend deskriptive Zusammenfassungen. Diese Werte sind für die Evidenz exakt, die nach den ausgewählten Regeln beibehalten wurde. Sie sind nicht automatisch Aussagen über alle möglichen Stationen, künftige Betriebsbedingungen oder eine isolierte physikalische Eigenschaft der Station.
````

</details>

### Original in 7. Wissenschaftliche Methoden

<details><summary>Verbatim baseline passage</summary>

````text
1. **Gemeldete Beobachtungen:** hochgeladene WSPR-Spots mit Rufzeichen, Locator, Leistung, Zeit und SNR.
2. **Gebildete Evidenzeinheiten:** qualifizierende Gelegenheiten, Peer-Zyklen, Joint-Einheiten, die nach den Zulässigkeits- und Zuordnungsregeln von WSPRadar entstehen.
3. **Abgeleitete Größen:** normiertes SNR, Decode Outcomes und Target-minus-Referenz-Delta-SNR einer einzelnen Evidenzeinheit.
4. **Deskriptive Zusammenfassungen:** Raten, Mediane, Reichweite, Evidenzanteile sowie zeitliche und geografische Zusammenfassungen der beibehaltenen Evidenz.
5. **Interpretation über den Lauf hinaus:** Aussagen über künftiges Verhalten, eine breitere Population oder eine physische Ursache. Solche Verallgemeinerungen benötigen zusätzliche Annahmen und experimentelle Kontrolle; die reine Berechnung genügt dafür nicht.
````

</details>

### Original in 7. Wissenschaftliche Methoden

<details><summary>Verbatim baseline passage</summary>

````text
| Design | Kleinste Vergleichseinheit | Konditionierung / Zulässigkeit | Hauptzusammenfassung | Wichtigste Grenze |
|---|---|---|---|---|
| RX Performance | ein Peer-Zyklus eines entfernten Senders | Target-RX aktiv; Peer-TX vom Target-RX oder einem anderen geeigneten RX decodiert | Peer-Dekodierrate, danach Mittel mit gleicher Peer-Gewichtung; gepoolte Gelegenheitsrate bleibt erhalten | bedingte Beobachtbarkeit, keine kalibrierte Empfindlichkeit |
| TX Performance | ein Peer-Zyklus eines entfernten Empfängers | Target-TX aktiv; Peer-RX decodiert Target-TX oder einen anderen qualifizierenden TX auf demselben Band | Peer-Dekodierrate, danach Mittel mit gleicher Peer-Gewichtung; gepoolte Gelegenheitsrate bleibt erhalten | bedingte Beobachtbarkeit, nicht alle Sendeversuche |
| RX Referenzaufbau/-station | ein Peer-Zyklus eines entfernten Senders | Target aktiv; beide Empfänger melden denselben Sender-Zyklus für Delta SNR | Stationsmedian des Delta SNR, danach Median über Stationen | vollständige Empfangspfade, sofern Ketten nicht kontrolliert sind |
| TX Referenzaufbau/-station | ein Peer-Zyklus eines entfernten Empfängers | Target aktiv; derselbe Empfänger-Zyklus für gepaartes Delta SNR | Stationsmedian des Delta SNR, danach Median über Stationen | Leistung, Kettenunterschiede und Auswahl nach Joint-Decode |
| Referenznachbarschaft (Lokaler Median) | ein Target-/lokaler-Referenz-Peer-Zyklus | Target aktiv; ein Beitrag je aktiver lokaler Identität | lokaler Median als Referenz, danach Stations- und Segmentmediane des Delta SNR | wechselnde, unkalibrierte Zusammensetzung |
````

</details>

### Original in 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar liest öffentliche WSPR-Meldungen für jeden abgeschlossenen Lauf aus genau einem ausgewählten, schreibgeschützten Archiv. Die Meldungen sind Beobachtungsdaten heterogener Sender, Empfänger, Decoder und Meldesysteme. Ein abgeschlossener Lauf mischt keine Datenquellen; das ausgewählte Archiv gehört zur Provenienz des Laufs.
````

</details>

### Original in 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar klassifiziert archivierte WSPR-Meldungen nicht als Typ 1, Typ 2 oder Typ 3. Beim simultanen Benchmark ist die wissenschaftliche Einheit der nach den Identitätsregeln aus Abschnitt 7.2 aufgelöste Peer-Zyklus des Archivs. Aufeinanderfolgende Aussendungen einer erweiterten WSPR-Folge bleiben getrennte zweiminütige Zyklen; jede kann getrennt eine Joint-Einheit bilden, wenn derselbe entfernte Empfänger in diesem Zyklus sowohl Target als auch Referenz meldet. Ein simultaner Benchmark verbindet niemals das Target aus einem Zyklus mit der Referenz aus einem anderen Zyklus.
````

</details>

### Original in 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell

<details><summary>Verbatim baseline passage</summary>

````text
Die Zuordnung desselben Zyklus bedeutet denselben zweiminütigen UTC-Archivslot und dasselbe entfernte Rufzeichen mit vollständigem gemeldeten Locator im selben Band. Sie verlangt keine identischen HF-Frequenzen und beweist keine gleichen physischen Ausbreitungswege; simultane TX-Signale benötigen normalerweise getrennte freie Frequenzen. Nur Joint-Evidenz liefert Delta SNR. Einseitige Evidenz und Both (Async) auf Stationsebene bleiben ohne erfundenes SNR der fehlenden Seite erhalten.
````

</details>

### Original in 7.2 Identität, Zuordnung und Zeilenkonsolidierung

<details><summary>Verbatim baseline passage</summary>

````text
Für die Auswahl der Target-Zeilen im Archiv verwendet WSPRadar Grid-4, auch wenn ein sechsstelliges QTH konfiguriert ist. Das vollständige QTH bleibt für Entfernung, Azimut, Sonnenhöhe und die Geometrie des lokalen Radius relevant. Ein gemeinsames Grid-4 belegt keine physische Ko-Lokation.
````

</details>

### Original in 7.2 Identität, Zuordnung und Zeilenkonsolidierung

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar arbeitet mit der Darstellung des Archivs: exaktes Target-Rufzeichen plus Target-Grid-4 sowie exaktes Referenzrufzeichen plus aufgelöstes Referenz-Grid-4. Es leitet keinen Locator aus einer benachbarten Typ-2- oder Typ-3-Aussendung ab und verlangt nicht, dass beide Folgenpositionen vorliegen, bevor eine Einheit desselben Zyklus zugelassen wird. Beide Positionen einer korrekt ausgerichteten Folge können deshalb getrennt beitragen, wenn das ausgewählte Archiv beide Identitäten wie erforderlich auflöst.
````

</details>

### Original in 7.2 Identität, Zuordnung und Zeilenkonsolidierung

<details><summary>Verbatim baseline passage</summary>

````text
Diese Interpretation als bester gemeldeter Empfang entspricht dem dokumentierten Zusammenführen mehrerer Empfänger in WsprDaemon: Liefern mehrere Empfänger Meldungen für dieselbe Aussendung, meldet es das beste SNR an WSPRnet. Dies ist ein Beispiel einer bestehenden Meldepraxis und kein Beleg dafür, dass eine bestimmte Archivmeldung das beabsichtigte Signal darstellt oder beide Vergleichsseiten dieselbe Spektralkomponente ausgewählt haben. <a href="#ref-11">[Ref-11]</a>
````

</details>

### Original in 7.3 Konditionierung auf Target-Aktivität und Zulässigkeit

<details><summary>Verbatim baseline passage</summary>

````text
Performance und simultaner Benchmark konditionieren auf $A_c=1$. Dadurch werden bekannte Target-Ausfallzeiten nicht automatisch zu Gegen-Evidenz. Zugleich verändert diese Regel die Analysepopulation: Das Ergebnis beschreibt Zyklen mit beobachtbarer Target-Beteiligung und nicht die gesamte Uhrzeit oder sämtliche geplanten Versuche.
````

</details>

### Original in 7.3 Konditionierung auf Target-Aktivität und Zulässigkeit

<details><summary>Verbatim baseline passage</summary>

````text
Die Konditionierung ist asymmetrisch. Die Betriebszeit der Referenz bildet kein zweites Gate und muss extern kontrolliert oder dokumentiert werden. Ein Tausch von Target und Referenz kann deshalb zulässige Zyklen und einseitige Decode Outcomes verändern, selbst wenn sich das Vorzeichen des reinen Joint-Delta-SNR erwartungsgemäß umkehrt.
````

</details>

### Original in 7.3 Konditionierung auf Target-Aktivität und Zulässigkeit

<details><summary>Verbatim baseline passage</summary>

````text
Jede Joint-Beobachtung belegt bereits eine Target-Beteiligung. Das Gate verändert daher nicht die Delta-SNR-Werte der Joint-Beobachtungen. Es verändert die Population einseitiger oder asynchroner Outcomes und bei Performance den Gelegenheitsnenner.
````

</details>

### Original in 7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen

<details><summary>Verbatim baseline passage</summary>

````text
Für einen qualifizierenden Peer gilt:
````

</details>

### Original in 7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen

<details><summary>Verbatim baseline passage</summary>

````text
Für den geografischen Bereich $g$ mit der qualifizierenden Peer-Menge $I_g$ lautet die stationsgleichgewichtete Dekodierrate:
````

</details>

### Original in 7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen

<details><summary>Verbatim baseline passage</summary>

````text
In Funkpraxis-Sprache ist dies der Prozentsatz qualifizierender Peers, bei denen das Target in mindestens einer qualifizierenden Gelegenheit erfolgreich war. Die Reichweite beschreibt Breite und nimmt mit der Beobachtungsdauer normalerweise zu; sie sagt nicht, wie beständig diese Funkwege funktionierten.
````

</details>

### Original in 7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen

<details><summary>Verbatim baseline passage</summary>

````text
Erfolgreiches Target-SNR ist nur definiert, wenn das Target decodiert oder gemeldet wurde, einschließlich Target-only-Erfolgen. Es ist damit eine auf erfolgreiche Decodes bedingte Verteilung. Mediane, IQR und Extremwerte verwenden alle beibehaltenen Erfolge nach unveränderter Zusammenfassung auf die stärkste Meldung und unveränderter Normierung. Dieselbe Klassifikation gilt für Stationsschwellen, beide Gewichtungen der Dekodierrate, Karten, Mindestens-einmal-Reichweite, chronologische und gefaltete Profile, Station Insights, Evidenz der ausgewählten Station, Drill-Down und Exporte. Verpasste Gelegenheiten besitzen kein Target-SNR und erhalten keinen künstlichen Wert. Dekodierrate und erfolgreiches SNR müssen gemeinsam gelesen werden: Ein System, das zusätzliche schwache Signale decodiert, kann die praktische Reichweite verbessern und zugleich den Median der erfolgreichen SNR-Werte absenken.
````

</details>

### Original in 7.5 Leistungsnormierung, Korrektur und Benchmark-Delta-SNR

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-7-5"></a>
#### 7.5 Leistungsnormierung, Korrektur und Benchmark-Delta-SNR
````

</details>

### Original in 7.5 Leistungsnormierung, Korrektur und Benchmark-Delta-SNR

<details><summary>Verbatim baseline passage</summary>

````text
WSPR meldet SNR auf der WSJT-Skala in dB bezogen auf eine Referenzbandbreite von 2500 Hz und überträgt die gemeldete Sendeleistung in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar normiert erfolgreiches TX-seitiges SNR auf gemeldete 30 dBm:
````

</details>

### Original in 7.5 Leistungsnormierung, Korrektur und Benchmark-Delta-SNR

<details><summary>Verbatim baseline passage</summary>

````text
Praktisch wird ein Signal mit 10 dB geringerer gemeldeter Sendeleistung für diesen Vergleich um 10 dB angehoben. Ein mit `-15 dB` gemeldetes SNR bei `20 dBm` wird beispielsweise auf `-5 dB` bei `30 dBm` normiert. Die Rechnung entfernt ausschließlich den **gemeldeten** Leistungsanteil. Sie korrigiert weder Antennengewinn, Strahlungswirkungsgrad, Speiseleitungsverlust, EIRP, Empfängerkalibrierung noch lokalen Stör- oder Rauschpegel.
````

</details>

### Original in 7.5 Leistungsnormierung, Korrektur und Benchmark-Delta-SNR

<details><summary>Verbatim baseline passage</summary>

````text
Für eine gepaarte Beobachtung gilt:
````

</details>

### Original in 7.5 Leistungsnormierung, Korrektur und Benchmark-Delta-SNR

<details><summary>Verbatim baseline passage</summary>

````text
Dabei ist $C_R$ die vorzeichenbehaftete additive referenzseitige Korrektur. In der ersten Gleichung bezeichnen $SNR_R$ und $SNR_{R,corr}$ das Referenz-SNR vor und nach der Korrektur. In der Gleichung für das Paar kennzeichnen die Indizes $i,c$ den Peer und die zugeordnete Evidenzeinheit; $SNR_{T,i,c}$ ist das zugehörige normierte Target-SNR und $SNR_{R,corr,i,c}$ das korrigierte Referenz-SNR. Positives $D_{i,c}$ spricht für das Target, negatives für die Referenz. Eine positive Korrektur macht die Referenz vor der Subtraktion stärker und senkt deshalb Delta SNR. Der eingegebene Kalibrierversatz verwendet dasselbe Vorzeichen `target - reference`.
````

</details>

### Original in 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

<details><summary>Verbatim baseline passage</summary>

````text
1. die Verteilung des Target-minus-Referenz-Delta-SNR unter **Joint**-Vergleichseinheiten und
2. die Zusammensetzung der beibehaltenen Evidenz aus **Only Target**, **Joint**, **Only Reference** sowie auf Identitätsebene **Both (Async)**.
````

</details>

### Original in 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

<details><summary>Verbatim baseline passage</summary>

````text
Delta SNR existiert nur, wenn beide Seiten vergleichbare Evidenz erzeugen. Die Joint-Teilmenge wird daher durch den erfolgreichen Decode beider Seiten ausgewählt. In statistischer Sprache sind die fehlenden Paare normalerweise nicht „zufällig fehlend“: Schwache Signale, Kollisionen, QRM, Decoderverhalten, Leistungsunterschiede und Funkwegbedingungen können alle beeinflussen, ob ein Paar entsteht. In Stationssprache heißt das: Die überlebenden Paare müssen nicht jede Gelegenheit nahe der Decode-Schwelle gleich gut repräsentieren.
````

</details>

### Original in 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

<details><summary>Verbatim baseline passage</summary>

````text
Einseitige Evidenz besitzt kein SNR der fehlenden Seite, das rekonstruiert werden könnte. Ihr darf kein künstliches Delta SNR zugewiesen werden, und sie wird nicht als Paar leistungsnormiert. Bei TX Benchmark können unterschiedliche tatsächliche oder gemeldete Leistungen einseitige Outcomes stark beeinflussen, selbst wenn das Joint-Delta-SNR normiert ist.
````

</details>

### Original in 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

<details><summary>Verbatim baseline passage</summary>

````text
`Both (Async)` bedeutet, dass für eine Identität beibehaltene Evidenz beider Seiten existiert, aber für die betreffende Stationskategorie keine qualifizierende Einheit desselben Zyklus erhalten bleibt. Die Kategorie zeigt eine breitere Beteiligung beider Seiten, trägt jedoch kein gepaartes Delta SNR bei.
````

</details>

### Original in 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

<details><summary>Verbatim baseline passage</summary>

````text
Findet eine Prüfung nur wenige vereinzelte Fehlzuordnungen unter Zehntausenden von Beobachtungen und keine Häufung nach Target- oder Referenzseite, Folgenphase, Empfänger oder Zeit, werden sie die Medianwerte in der Regel nicht oder nur geringfügig verändern. Diese Robustheit darf nicht allein aus der Datenmenge abgeleitet werden: Systematische oder asymmetrische Fehlzuordnungen können die Joint-Zulässigkeit, einseitige Decode Outcomes und Stationsmediane verändern. WSPRadar kann nur prüfen, ob das konfigurierte exakte Rufzeichen und Grid-4 im ausgewählten Archiv vorliegen; es kann nicht beweisen, dass jede Upstream-Hash-Zuordnung physisch korrekt war.
````

</details>

### Original in 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

<details><summary>Verbatim baseline passage</summary>

````text
Die Zensierung auf erfolgreiches SNR bei Performance und die Auswahl nach gemeinsamem Decode bei Benchmark sind verschiedene Selektionsprozesse. WSPRadar zeigt Decode Outcomes und Joint-Evidenzanteil, damit die gepaarten Delta-SNR-Zusammenfassungen im Verhältnis zur breiteren beibehaltenen Evidenz gelesen und nicht mit der vollständigen Stationspopulation gleichgesetzt werden.
````

</details>

### Original in 7.7 Aggregationshierarchie und Gewichtung

<details><summary>Verbatim baseline passage</summary>

````text
| Peer-Identität | Beibehaltene Delta-SNR-Werte (dB) | Peer-Median (dB) |
|---|---|---:|
| A | +6, +6, +6, +6, +6, +6 | +6 |
| B | -2, -2 | -2 |
| C | -1, -1 | -1 |
````

</details>

### Original in 7.7 Aggregationshierarchie und Gewichtung

<details><summary>Verbatim baseline passage</summary>

````text
Bei jedem Benchmark-Design gilt für Gewichtung und Segmentunterstützung dieselbe Stationsidentität: das exakte `Rufzeichen + vollständig gemeldeter Locator`. Jede Identität muss für sich die konfigurierte Mindestzahl an Joint-Evidenz erfüllen. Genau die Identitäten, die jeweils einen Peer-Median beitragen, zählen auch für die Mindestanzahl qualifizierender Stationen pro Kartensegment. Identitäten mit ausschließlich einseitiger Evidenz tragen nicht zu dieser Delta-SNR-Unterstützungszahl bei. Dasselbe Rufzeichen mit unterschiedlichen vollständigen Locatorn zählt getrennt, auch wenn beide Locator im selben Grid-4 liegen. Gezählt werden gemeldete Funkwegidentitäten; daraus folgen keine unabhängigen physischen Stationen oder Standorte.
````

</details>

### Original in 7.7 Aggregationshierarchie und Gewichtung

<details><summary>Verbatim baseline passage</summary>

````text
Für jeden entfernten Peer-Zyklus berechnet WSPRadar zunächst je aktiver lokaler Identität aus `Rufzeichen + Locator` genau einen normierten SNR-Beitrag und danach den exakten Median über die beitragenden lokalen Identitäten. Eine nicht beobachtete lokale Identität wird weggelassen und nicht mit null angesetzt. Die Referenzkorrektur wird vor der Aggregation des lokalen Pools angewendet. Anschließend wird das Target mit diesem zyklus- und funkwegspezifischen Median verglichen; daraus entstehen Peer- und Segmentmediane des Delta SNR.
````

</details>

### Original in 7.7 Aggregationshierarchie und Gewichtung

<details><summary>Verbatim baseline passage</summary>

````text
Es gibt keine gesonderte Mindestzahl lokaler Beitragender pro Peer-Zyklus. Bei einem Beitrag entspricht die Referenz dessen Wert. Ohne Beitragende steht weder ein Referenz-SNR noch gepaartes Delta SNR zur Verfügung. Die an anderer Stelle geltenden Anforderungen an die Mindestmenge gemeinsamer Evidenz und stützender Stationen legen keine Mindestgröße der Nachbarschaft fest.
````

</details>

### Original in 7.8.1 Geografische Zusammenfassungen

<details><summary>Verbatim baseline passage</summary>

````text
Geografische Benchmark-Zusammenfassungen verwenden je qualifizierender Identität genau einen Peer-Median des Delta SNR und danach den Segmentmedian dieser Peer-Mediane. Das Delta SNR auf Beobachtungsebene bleibt als getrennt gewichtete Verteilung verfügbar. Die erste Sicht beantwortet „Was zeigte der typische qualifizierende Peer?“, die zweite „Was zeigten die beibehaltenen gepaarten Beobachtungen, wenn jedes Paar zählt?“.
````

</details>

### Original in 7.8.2 Abdeckung der Benchmark-Evidenz

<details><summary>Verbatim baseline passage</summary>

````text
Die erste Größe gibt jedem beitragenden Peer dasselbe Gewicht, die zweite jeder beibehaltenen Vergleichseinheit. Der Joint-Evidenzanteil misst die Paarbarkeit – also welcher Anteil der beibehaltenen Evidenz zu Delta SNR beitragen kann. Er ist keine Gewinnquote des Targets.
````

</details>

### Original in 7.8.2 Abdeckung der Benchmark-Evidenz

<details><summary>Verbatim baseline passage</summary>

````text
Unter dem Target-Active Gate sind Only Target und Only Reference gerichtet und asymmetrisch. Einseitige Evidenz besitzt weiterhin kein Delta SNR.
````

</details>

### Original in 7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung

<details><summary>Verbatim baseline passage</summary>

````text
Für die Abweichung des erfolgreichen Performance-SNR geht ein Peer nur dann in die Anomaliepopulation ein, wenn er im vollständigen Laufzeitfenster mindestens drei erfolgreiche normierte Target-SNR-Beobachtungen besitzt. Seine Basislinie ist der Median dieser Erfolge. Jede erfolgreiche Beobachtung trägt bei:
````

</details>

### Original in 7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung

<details><summary>Verbatim baseline passage</summary>

````text
Dabei kennzeichnet $c$ die aktuelle erfolgreiche Beobachtung; $c'$ durchläuft alle erfolgreichen Beobachtungen des Peers $i$ im vollständigen Laufzeitfenster, aus denen seine Basislinie entsteht. `0 dB` bedeutet damit „auf dem für diesen Funkweg üblichen erfolgreichen Pegel“ und nicht Target–Referenz-Gleichheit. Ein positiver Wert bedeutet, dass dieser erfolgreiche Decode stärker als der für diesen Peer übliche erfolgreiche Pegel im Lauf war; ein negativer Wert bedeutet schwächer. Es handelt sich um eine Abweichung innerhalb eines Funkwegs und nicht um Target-minus-Referenz-Delta-SNR.
````

</details>

### Original in 7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung

<details><summary>Verbatim baseline passage</summary>

````text
Chronologisch trägt jeder Peer je ausgewähltem Bin höchstens einen Median der Abweichung bei. In der UTC-gefalteten Sicht trägt jeder Peer zunächst je Datum und UTC-Stunde einen Median bei; erst danach werden diese Peer-Datum-Stunden-Werte über die gefaltete Population zusammengefasst. Dadurch dominieren besonders häufig meldende Peers oder Tage nicht allein durch ihre Rohzeilenzahl.
````

</details>

### Original in 7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung

<details><summary>Verbatim baseline passage</summary>

````text
Das zeitliche Benchmark-Delta-SNR verwendet beibehaltene Joint-Beobachtungen. Wenn keine gepaarten Werte verbleiben, zeigt das Delta-SNR-Panel weiterhin das vollständige ausgewählte UTC-Zeitfenster und weist auf die fehlende gepaarte Evidenz für Δ SNR hin. Das bedeutet, dass im dargestellten Bereich keine beibehaltene Joint-Beobachtung verbleibt; daraus folgt nicht, dass die Datenquelle keine Beobachtungen lieferte, und die zeitliche Abdeckung kann weiterhin einseitige Outcomes zeigen. Chronologische Bins fassen gepaarte Werte in tatsächlicher Zeit zusammen; UTC-Stunden-Bins fassen dieselbe gepaarte Population nach Stunde über die Tage zusammen, die in der beibehaltenen Benchmark-Evidenz vertreten sind. Die zeitliche Benchmark-Abdeckung verwendet alle beibehaltenen Einheiten Only Target, Joint und Only Reference sowie die beiden oben definierten Zusammenfassungen des Joint-Evidenzanteils. Auch die Benchmark-Faltung erfordert mindestens zwei Tage mit Evidenz.
````

</details>

### Original in 7.8.4 Zusammenfassungen für den ausgewählten Funkweg

<details><summary>Verbatim baseline passage</summary>

````text
Bei Benchmark zeigt der ausgewählte Funkweg das Delta SNR jeder Joint-Einheit auf Beobachtungsebene und getrennt die Abdeckung durch Only Target, Joint und Only Reference. Ein Wechsel des ausgewählten Funkwegs oder Darstellungs-Bins verändert nur die Ansicht der beibehaltenen Evidenz, nicht die vorgelagerte Zuordnung, Zulässigkeit oder Aggregation.
````

</details>

### Original in 7.8.4 Zusammenfassungen für den ausgewählten Funkweg

<details><summary>Verbatim baseline passage</summary>

````text
Der Drill-Down kann dieselbe Evidenz des ausgewählten Funkwegs vor Anwendung gewöhnlicher Tabellenfilter vorübergehend auf ein zentriertes Intervall von `1h`, `3h`, `6h`, `12h` oder `24h` begrenzen. Sein fokussiertes Messwertrezept behält je nativer Koordinate eine wissenschaftliche Einheit: beim simultanen Benchmark einen zusammengeführten Joint Spot mit tatsächlichem Delta SNR zur kanonischen Zykluszeit, bei Performance eine erfolgreiche bestätigte Gelegenheit mit tatsächlichem normiertem Target-SNR zur kanonischen Zykluszeit. „Nativ“ bezeichnet damit verarbeitete beibehaltene Evidenz nach Zusammenführung, Zuordnung und wissenschaftlichen Filtern und keine unveränderten Provider-Zeilen. Das fokussierte Messwertrezept enthält weder Mediane oder Quartile zeitlicher Bins noch Dichtegitter, Farbskala, Median des vollständigen Laufs oder gefaltetes Profil. Ergänzende Outcome- beziehungsweise Abdeckungspanels dürfen ihre chronologische Aggregation beibehalten; Segment- und ausgewählte Funkwegrezepte über das vollständige Fenster bleiben unveränderte Dichtezusammenfassungen.
````

</details>

### Original in 7.8.4 Zusammenfassungen für den ausgewählten Funkweg

<details><summary>Verbatim baseline passage</summary>

````text
Der kandidatenverknüpfte **`Ausreißerfokus`** verwendet die vollständige beibehaltene Flanke vor dem Ereignis, die geschützte vorläufige Episode und die Flanke danach und darf länger als 24 Stunden sein. Das Benchmark-Overlay verwendet das bereits abgeschlossene Detektormodell, statt auf der fokussierten Teilmenge erneut zu erkennen. Für jeden gemeldeten Kandidaten, der das Fokusfenster schneidet, markiert es mit demselben `*` jede native Einheit, die gegen die endgültige Baseline und robuste Streuung dieses Kandidaten einzeln sowohl $D_{\min}$ als auch $Z_{\min}$ erfüllt; schwächere gruppierte Einheiten, die zwischen starken Ankern beibehalten werden, bleiben normale Punkte. Ein dezentes Band **Fokussierte Episode** unterscheidet das berichtete Intervall der beibehaltenen Evidenz des ausgewählten Kandidaten. Der Renderer erweitert jedes Ende um eine halbe Breite der nativen Evidenzeinheit und schneidet das Band am Fokusfenster ab; dadurch bleibt ein Impuls aus einer Einheit sichtbar, ohne eine unbeobachtete physische Dauer oder ein Konfidenzintervall darzustellen. Erwartetes lokales Delta SNR über den Fokus, die Mediane der Flanken davor und danach über deren jeweilige Stützintervalle, symmetrische Hilfsgrenzen für robuste z-Beträge 1, 2, 3 und $Z_{\min}$ sowie die Grenze der absoluten Abweichung $D_{\min}$ gehören ausschließlich zu dieser fokussierten Episode; ein anderer markierter Kandidat kann eine andere Baseline und robuste Streuung besitzen. Aus der Detektordefinition in [Abschnitt 7.11](#sec-7-11) folgt: Eine Hilfsgrenze des Betrags `k` liegt bei der lokalen Baseline plus oder minus `k × robuste Streuung / 0,6745`. Diese Linien visualisieren Detektorkoordinaten; sie sind weder Standardabweichungen oder Konfidenzintervalle noch eigenständige Qualifikationstests, und das Überschreiten einer einzelnen Hilfslinie reicht nicht zur Qualifikation eines Kandidaten. Fokusauswahl und Kandidatenprovenienz sind ausschließlich Darstellungszustand; sie verändern weder `AnalysisContext`, Zuordnung, Zulässigkeit, Detektorergebnisse oder Provider-Abfrage noch gespeicherte Konfiguration oder öffentliche URL.
````

</details>

### Original in 7.8.5 Deskriptive Streuung und Visualisierungstransformationen

<details><summary>Verbatim baseline passage</summary>

````text
IQR- und Min-Max-Darstellungen sind deskriptive Streuungsmaße und keine Konfidenzintervalle. Ein IQR-Band wird nur gezeichnet, wenn mindestens fünf Werte zum jeweiligen Bin beitragen; der Median bleibt auch bei weniger Werten sichtbar. Leere Bins bleiben fehlend und werden nicht zu künstlichen Nullbeobachtungen.
````

</details>

### Original in 7.8.5 Deskriptive Streuung und Visualisierungstransformationen

<details><summary>Verbatim baseline passage</summary>

````text
Benchmark-Histogramme verwenden normalerweise 1-dB-Klassen, 0,5 dB nur bei einem klaren Halb-dB-Raster und gröbere Klassen bei großen Wertebereichen, damit die Bin-Anzahl begrenzt bleibt. Zeitliche Benchmark-Dichtezellen bleiben 1 dB hoch und folgen der angewandten Referenz-SNR-Korrektur. Für das korrigierte Delta SNR `d` und die numerische Korrektur `c` lautet die ideale Zuordnungsregel in der unkorrigierten Vergleichskoordinate `k = floor(d + c + 0.5)`; die folgende numerische Konvention wertet diese Koordinate mit 0,1 dB Auflösung aus. Zelle `k` ist bei `k - c` zentriert und umfasst das halboffene Intervall `[k - 0.5 - c, k + 0.5 - c)`: Die untere Grenze gehört zur Zelle, die obere zur nächsten Zelle, auch bei negativen Werten. Die Addition von `c` zur Bestimmung der Zugehörigkeit ist ausschließlich eine Koordinatentransformation; sie wendet die Korrektur nicht erneut auf die gespeicherten Beobachtungen, Mediane oder Quartile an. Bei derselben beibehaltenen Population verschiebt eine Änderung von `c` das Dichtegitter gemeinsam mit den korrigierten Beobachtungen; Belegungszahlen der Zellen und Farben der relativen Dichte bleiben erhalten. Nicht ganzzahlige Beobachtungen, einschließlich Vergleichen mit dem lokalen Median, müssen nicht in den Zellzentren liegen.
````

</details>

### Original in 7.8.5 Deskriptive Streuung und Visualisierungstransformationen

<details><summary>Verbatim baseline passage</summary>

````text
Ausschließlich für die Zellzuordnung wird `d + c` vor Bestimmung der ganzzahligen Zell-ID auf das nächste Zehntel Dezibel gerundet; bei einem exakten halben Zehntel wird das gerade Zehntel gewählt. Ein ausschließlich an diesen Rundungsmittelpunkten wirksamer Float64-Rundungsfehlerbereich verhindert, dass Korrekturrauschen unterschiedliche Zehntel auswählt. Damit ist die Auflösung der Zuordnung ausdrücklich auf 0,1 dB begrenzt; numerisches Rauschen wie `-0.7000000000000028` bei einem korrigierten Wert, der bei `-0,7 dB` erwartet wird, wird aufgefangen. Unterschiede unterhalb dieser Zuordnungsauflösung können derselben Zelle zugewiesen werden. Exakte Halb-dB-Koordinaten bei dieser Auflösung gehören zur oberen Zelle, auch bei negativen Werten. Die ursprünglichen korrigierten Beobachtungen und ihre Statistiken werden durch diese Gitterkonvention nicht gerundet. Eine nicht ganzzahlige Beobachtung mit voller Präzision kann deshalb bis zu 0,05 dB außerhalb der zugewiesenen Zellgrenze liegen; der Achsenbereich umfasst weiterhin die Beobachtung selbst. Diese zeitliche Darstellungskonvention ersetzt die Ganzzahlrundung zur nächsten geraden Zahl bei Gleichstand; deshalb können sich Zuordnungen exakt auf Halb-dB-Grenzen auch ohne Korrektur ändern. Gewöhnliche Histogramme, Performance-Ansichten und Drill-Down-Abbildungen mit nativen Einzelpunkten bleiben unverändert. Jedes Dichtepanel wird unabhängig normiert:
````

</details>

### Original in 7.8.5 Deskriptive Streuung und Visualisierungstransformationen

<details><summary>Verbatim baseline passage</summary>

````text
Zeitliche Benchmark-Ansichten und Histogramme verwenden eine rein darstellungsbezogene monotone Skala, die um den Bereichsmedian $M$ zentriert ist. Bei großer Spannweite liegen gleichmäßige visuelle Schritte bei $M$, $M\pm3$, $M\pm6$, $M\pm10$, $M\pm20$ und $M\pm30$ dB; ein Randanker liegt bei $M\pm60$ dB und wird bei Bedarf fortgesetzt. Wenn jede erforderliche Abweichung höchstens `10 dB` beträgt, lauten die engeren Anker $M$, $M\pm1$, $M\pm3$, $M\pm6$ und $M\pm10$ dB; Fortsetzungsanker liegen bei $M\pm20$ und $M\pm40$ dB. Der erforderliche Bereich umfasst die zutreffenden Rohgrenzen des Histogramms beziehungsweise die durch die Korrektur verschobenen zeitlichen Zellgrenzen, eine Mindesthalbspanne von `3 dB` und den absoluten Wert `0 dB`, damit Target-Referenz-Gleichheit sichtbar bleibt. Die Ankerabbildung verändert ausschließlich die dargestellten Abstände: Rohe Delta-SNR-Werte, Bin-Zuordnung, Anzahlen, Mediane und Quartile bleiben unverändert. Wegen der nichtlinearen vertikalen Abbildung ist die **Balkenlänge** entlang der Prozentachse – nicht die dargestellte Fläche – die quantitative Kodierung.
````

</details>

### Original in 7.9 Geografie, Sonnenstandsklassifikation und Populationsfilter

<details><summary>Verbatim baseline passage</summary>

````text
Die Zeilengrenze des Archivs und die Bedienelemente, mit denen sich die abgerufene Population verkleinern lässt, sind betriebliche Fragen aus [Abschnitt 5.6](#sec-6-6). Sie verändern die wissenschaftlichen Zusammenfassungen nicht, nachdem die beibehaltene Population gebildet wurde.
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
<a id="sec-7-11"></a>
#### 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
Das Analyseziel des Detektors ist eine vorübergehende gleichgerichtete Abweichung des gepaarten Delta SNR eines Funkwegs von einem stabilen lokalen Erwartungswert. Er erstellt weder eine Rangfolge der größten Rohwerte noch schätzt er eine Ereigniswahrscheinlichkeit. [Abschnitt 2.5](#sec-outlier) erklärt, wann und wie dieses Diagnosewerkzeug fachkundig eingesetzt werden sollte; dieser Abschnitt definiert die exakte wissenschaftliche Konstruktion.
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
| Symbol | Englischer Merkbezug und Bedeutung in diesem Abschnitt |
|---|---|
| $i$ | ein exakter Peer-Funkweg mit der Identität `Rufzeichen + Locator` |
| $u$ | eine native gepaarte Einheit: ein Joint Spot aus demselben Zyklus |
| $k$ | Index einer UTC-ausgerichteten 10-Minuten-Baseline-Zelle |
| $D_{i,u}$ | korrigiertes gepaartes Delta SNR Target minus Referenz der Einheit $u$ gemäß Abschnitt 7.5 |
| $\widetilde D_{i,k}$ | Delta-SNR-Median in der belegten Baseline-Zelle $k$ |
| $\mathcal{B}_{\mathrm{pre}},\mathcal{B}_{\mathrm{post}}$ | beibehaltene Baseline-Evidenzwerte vor und nach dem Ereignis |
| $B_{\mathrm{pre}},B_{\mathrm{post}},B$ | Baseline vor dem Ereignis, nach dem Ereignis und abschließende lokale Baseline |
| $B^P_{i,k}$ | `B` = Baseline, `P` = Pilot: Pilot-Baseline für Funkweg $i$ und Zelle $k$ |
| $r^P_{i,u},r_{i,u}$ | `r` = residual: Pilot- und abschließendes Residuum der nativen Einheit $u$ |
| $\mathcal{V},S_{\mathrm{robust}}$ | `V` = variability, `S` = scale: zentrierte Stichprobe der Flankenvariabilität und robuste lokale Skala |
| $z_{i,u}$ | robuster z-Wert einer nativen gepaarten Einheit |
| $C_i,G_i,F$ | `C` = cadence, `G` = gap, `F` = floor: typische Funkwegkadenz, größte interne Lücke und vorläufige Gruppierungsuntergrenze |
| $W_i^P,W_i^B$ | `W` = width: Ausschlussbreiten der Pilot- und abschließenden Baseline |
| $E,m_E,z_E,\operatorname{agree}(E)$ | `E` = event, `m` = median, `agree` = agreement: Ereigniskandidat, medianes Residuum, robuster Ereignis-z-Wert und Anteil der Vorzeichenübereinstimmung |
| $\varepsilon$ | feste Vergleichstoleranz von `0.01 dB` für die Mindestabweichung und den maximalen Baseline-Unterschied |
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
**1. Evidenz und Auflösung.** Nur native gepaarte Einheiten liefern Delta-SNR-Werte für den Detektor. Einseitige Outcomes besitzen keinen gepaarten Wert und können kein Ereignis qualifizieren; ihre Zeitpunkte tragen jedoch zur Kadenzschätzung bei, und die Outcomes bleiben Diagnosekontext. Die Erkennung läuft für jeden Funkweg $i$ getrennt und vor der Darstellungsaggregation der **Zeitlichen Evidenz**. Ein anderes Darstellungs-Bin kann deshalb kein Ereignis erzeugen, zusammenführen, teilen oder entfernen. Ist **`ΔSNR-Ausreißerkandidaten melden`** ausgeschaltet, wird der Detektor nicht ausgeführt, und dem Ergebnis werden keine Ausreißerbegriffe hinzugefügt.
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
Das abschließende erwartete lokale Delta SNR gewichtet beide Flanken gleich, während das Stabilitätskriterium ihre Abweichung begrenzt:
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
Damit eine Verschiebung der Baseline nicht als Rauschen behandelt wird, wird jede Flanke zur Messung der nahen Variabilität um ihre eigene Baseline zentriert:
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
Die robuste lokale Skala ist:
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
MAD bezeichnet die mediane absolute Abweichung und IQR den Interquartilsabstand. Der Mindestwert von `0.5 dB` verhindert eine Division durch null bei lokal quantisierter Evidenz. Gegenüber der abschließenden Baseline besitzt eine native Einheit:
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
Ein positives Residuum liegt über dem erwarteten lokalen Delta SNR Target minus Referenz, ein negatives darunter. Gruppierung und Qualifikation richten sich nach diesem Vorzeichen und nicht nach dem Vorzeichen des Rohwerts $D_{i,u}$ relativ zu `0 dB`. Der Faktor `0.6745` liefert die konventionelle Skalierung des modifizierten Werts, wenn MAD aktiv ist. Der Wert bleibt deskriptiv und ist weder eine kalibrierte Wahrscheinlichkeit noch ein p-Wert oder ein gaußsches Signifikanzniveau.
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
**3. Kadenzabhängige Pilotgruppierung.** Die typische Funkwegkadenz $C_i$ wird in Minuten aus eindeutigen Zeitpunkten zulässiger gepaarter und einseitiger Outcomes geschätzt. Positive Intervalle bis einschließlich 45 Minuten werden beibehalten; mindestens zwei sind erforderlich. Andernfalls liefert die konfigurierte Kadenz gepaarter Einheiten den Wert $C_i$. Die größte interne Lücke ist:
````

</details>

### Original in 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline passage</summary>

````text
Das Ereignis qualifiziert sich nur, wenn jedes Kriterium erfüllt ist:
````

</details>

### Original in 8. Evidenzgerechte Aussagen und Reproduzierbarkeit

<details><summary>Verbatim baseline passage</summary>

````text
WSPRadar stützt begrenzte deskriptive und vergleichende Aussagen über beibehaltene Beobachtungsevidenz. Eine belastbare Berichterstattung nennt die konditionierte Population, die berichtete Zusammenfassung und Gewichtung, die Unterstützung, das Versuchsdesign und die verbleibenden unbeobachteten oder unkontrollierten Variablen.
````

</details>

### Original in 8.1 Aussageklassen und evidenzgerechte Formulierungen

<details><summary>Verbatim baseline passage</summary>

````text
| Aussageklasse | Was WSPRadar stützen kann | Zusätzliche Voraussetzung für eine stärkere Aussage |
|---|---|---|
| **Deskriptiv** | Reichweite, Dekodierrate, erfolgreiches SNR, Delta SNR, Decode Outcomes und wo sie in der ausgewählten Evidenz auftraten. | Population, Gewichtung, Bereich und Unterstützung angeben. |
| **Vergleichend** | Unterschied Target gegenüber Referenz unter dem gewählten Benchmark-Design. | Angeben, was die Referenz darstellt und welche zugeordnete Teilmenge verwendet wurde. |
| **Bauteilzuordnung** | Ein mit einem lokalen Pfad oder Bauteil verbundener Unterschied. | Kontrolliertes Referenzaufbau/-station, Kalibrierung und möglichst Kreuztausch beziehungsweise Rollentausch. |
| **Kausal** | Die geprüfte Änderung verursachte den beobachteten Effekt. | Ein Design, das plausible Alternativerklärungen kontrolliert; WSPRadar-Zusammenfassungen allein reichen nicht aus. |
| **Inferenzstatistisch** | Konfidenz, Signifikanz oder ein auf eine Population verallgemeinerbarer Effekt. | Ein begründetes Abhängigkeitsmodell und eine inferenzstatistische Analyse, die WSPRadar derzeit nicht liefert. |
````

</details>

### Original in 8.1 Aussageklassen und evidenzgerechte Formulierungen

<details><summary>Verbatim baseline passage</summary>

````text
* **Performance** stützt das konditionale Verhalten des Targets innerhalb bestätigter Gelegenheiten und seine Mindestens-einmal-Reichweite während des ausgewählten Zeitfensters.
* **Benchmark-Delta-SNR** stützt die gepaarte Beschreibung Target minus Referenz innerhalb der Joint-Teilmenge.
* **Decode Outcomes** stützen Aussagen über Paarbarkeit und einseitige Evidenz.
* **Entfernungs- oder Richtungsstruktur** stützt Aussagen über beobachtete Funkwegsegmente und nicht über einen direkten Abstrahlwinkel oder ein Gewinnmuster.
* **Referenznachbarschaft** stützt Beschreibungen, wie die vollständige Target-Station unter den ausgewählten Bedingungen gegenüber den beitragenden Peers in der Umgebung abschnitt. Seine Referenz ändert sich mit den qualifizierenden Beobachtungen, dem Radius, dem entfernten Funkweg und dem Zyklus. Sie ist weder eine dauerhafte Stationsrangliste noch ein kalibrierter Antennenvergleich.
````

</details>

### Original in 8.1 Aussageklassen und evidenzgerechte Formulierungen

<details><summary>Verbatim baseline passage</summary>

````text
Ein positives oder negatives Delta SNR beziffert den nach dieser Konstruktion beobachteten gepaarten SNR-Unterschied. Es bestimmt nicht, welches Bauteil oder welcher Umgebungsunterschied ihn verursacht hat. Der Joint-Evidenzanteil beschreibt Paarbarkeit oder Abdeckung der beibehaltenen Evidenz; er ist keine Gewinnrate des Targets.
````

</details>

### Original in 8.1 Aussageklassen und evidenzgerechte Formulierungen

<details><summary>Verbatim baseline passage</summary>

````text
| Vermeiden | Evidenzgerechte Formulierung |
|---|---|
| „Antenne A hat 3 dBi mehr Gewinn.“ | „Pfad A ergab gegenüber B ein stationsgleichgewichtetes medianes Delta SNR von +3,0 dB für die gepaarte Evidenz in diesem Band, Zeitfenster und Segment.“ |
| „Die Empfindlichkeit meines Empfängers beträgt 72 %.“ | „Die stationsgleichgewichtete Dekodierrate des Target-Empfängers betrug 72 % unter qualifizierenden Peer-Zyklen, die durch einen Target-Decode oder externe Aktivitätsevidenz bestätigt wurden.“ |
| „Performance sollte nahe 100 % liegen.“ | „Die Dekodierrate ist durch bestätigte Gelegenheiten bedingt; 100 % ist kein zu erwartender Ausgangswert.“ |
| „A ist statistisch signifikant besser.“ | „Der deskriptive gepaarte Median begünstigte A in der ausgewählten Evidenz; ein Signifikanztest wurde nicht durchgeführt.“ |
| „Die Antenne hat einen flacheren Abstrahlwinkel.“ | „Der beobachtete Vorteil konzentrierte sich auf die angegebenen größeren Entfernungssegmente; der Abstrahlwinkel wurde nicht gemessen.“ |
| „A ist effizienter, weil es mehr exklusive Decodes hatte.“ | „A erzeugte unter den dokumentierten Leistungs-, Zeitplan- und Netzwerkbedingungen mehr einseitige Decode-Evidenz; der Wirkungsgrad wurde nicht isoliert.“ |
| „Der lokale Median ist die durchschnittliche lokale Station.“ | „Die Referenz war der Zyklus-/Funkwegmedian aus je einem Beitrag jeder aktiven lokalen Identität aus Rufzeichen plus Locator.“ |
| „Meine Antenne ist X dB besser als benachbarte Antennen.“ | „Für das angegebene Band, Zeitfenster, den Radius und Bereich betrug das stationsgleichgewichtete mediane Delta SNR meiner vollständigen Station X dB relativ zur beobachteten lokalen Nachbarschaftsreferenz. Dies beschreibt die beibehaltene Joint-Evidenz und isoliert keinen Antennengewinn.“ |
````

</details>

### Original in 8.2 Interpretationsgrenzen

<details><summary>Verbatim baseline passage</summary>

````text
* von Nutzern gemeldete Rufzeichen, Locator und Leistungen können falsch sein;
* Archive enthalten erfolgreiche Decodes und keine vollständigen Versuchsprotokolle;
* Performance ist auf beobachtbare Gelegenheiten konditioniert;
* die Konditionierung auf Target-Aktivität ist asymmetrisch;
* erfolgreiches Target-SNR ist auf erfolgreiche Decodes zensiert;
* Benchmark-Delta-SNR wird durch die gemeinsame Beobachtung beider Seiten ausgewählt;
* einseitige Evidenz besitzt kein SNR der fehlenden Seite;
* simultanes TX behält Unterschiede zwischen den Ketten bei Leistung, Frequenzgang, Entkopplung und Kopplung bei;
* Stationshardware, Software, Gelände, lokaler Störpegel, Polarisation und Ausbreitung bleiben gekoppelt, sofern der Versuch sie nicht kontrolliert;
* Beobachtungen sind über Station, Zeit, Geografie und Ausbreitung geclustert; und
* Upstream-Datensätze und Verfügbarkeit können sich nach dem ursprünglichen Lauf verändern.
````

</details>

### Original in 8.3 Checkliste für Berichterstattung und Reproduzierbarkeit

<details><summary>Verbatim baseline passage</summary>

````text
Bewahre für eine ernsthafte Analyse drei Ebenen auf.
````

</details>

### Original in 8.3 Checkliste für Berichterstattung und Reproduzierbarkeit

<details><summary>Verbatim baseline passage</summary>

````text
* WSPRadar-Anwendungsversion und, soweit verfügbar, Quellrevision;
* RX-/TX-Richtung, Ergebnistyp und Benchmark-Design;
* exakte Target- und Referenzidentitäten und Locator;
* Band und wirksame UTC-Grenzen;
* geografischer Bereich, Sonnenstand, Ausschlüsse und Evidenzschwellen;
* Zweck der Referenzkorrektur, vorzeichenbehafteter Wert und Kalibriergrundlage;
* primärer vorab festgelegter Auswertungsbereich und alle Sensitivitätsanalysen; und
* ob der Lauf explorativ oder bestätigend war.
````

</details>

### Original in 8.3 Checkliste für Berichterstattung und Reproduzierbarkeit

<details><summary>Verbatim baseline passage</summary>

````text
* berichtete Zusammenfassung und Gewichtungsebene;
* qualifizierende Peers und Gelegenheiten bei Performance;
* Joint-Peers und Joint-Spots/-Paare bei Benchmark;
* stations- und beobachtungsbezogene Zusammenfassungen;
* Joint-Evidenzanteil und relevante einseitige Decode Outcomes;
* geografischer/zeitlicher Bereich sowie jede einflussreiche Identität oder kurze Zeitspanne; und
* Konsistenz innerhalb des Laufs im Unterschied zur Wiederholung in einem getrennten Lauf.
````

</details>

### Original in 8.3 Checkliste für Berichterstattung und Reproduzierbarkeit

<details><summary>Verbatim baseline passage</summary>

````text
Bewahre das ursprüngliche Exportpaket als Evidenznachweis dieses Laufs auf. Ein späterer Abruf kann Korrekturen im Upstream-Archiv oder eine neuere WSPRadar-Version widerspiegeln.
````

</details>

### Original in 8.4 Exportpaket der Analyse

<details><summary>Verbatim baseline passage</summary>

````text
`Alle Ergebnisse zum Download vorbereiten` erstellt aus dem abgeschlossenen Lauf und den aktuellen Inspektor-Auswahlen ein Paket. Ein typisches Paket enthält:
````

</details>

### Original in 8.4 Exportpaket der Analyse

<details><summary>Verbatim baseline passage</summary>

````text
Dateien ohne anwendbares Ergebnis oder ohne ausgewählte Station können fehlen.
````

</details>

### Original in 8.4 Exportpaket der Analyse

<details><summary>Verbatim baseline passage</summary>

````text
| Artefakt | Wissenschaftlicher Inhalt und Bereich |
|---|---|
| `wspradar_config.config` | Versionierte ausführbare Definition und dauerhafte Einstellungen der Ergebnisansicht. |
| `run_metadata.json` | Provenienz von Anwendung und Export, Richtung, Band, Zeitauswahl, Benchmark-/Korrekturdefinition, Filter, Schwellen und Inspektor-Auswahlen. |
| `analysis_cache.parquet` | Verarbeitete beibehaltene Evidenz nach wissenschaftlichen Filtern und geografischem Bereich; kein unveränderter Upstream-Dump. |
| `table_station_insights_current_segment.csv` | Zusammenfassungen je Peer für den aktiven Bereich des Segment-Inspektors. |
| Drill-Down-CSV-Dateien | Beibehaltene Evidenz auf Zeilenebene für ausgewählte Identitäten oder Identitäten im aktiven Bereich. |
| Delta-SNR-Ausreißer-CSV-Dateien | Bei aktivierter optionaler Ausreißermeldung Zusammenfassungen qualifizierter Funkwegereignisse und deren chronologische native gepaarte Evidenz für den aktiven Bereich des Segment-Inspektors. |
| Karten- und Segmentabbildungen | Geografische und segmentbezogene deskriptive Zusammenfassungen des abgeschlossenen Ergebnisses. |
| Zeitliche Abbildungen | Chronologische und nach UTC-Stunde gefaltete Zusammenfassungen für das aktive Segment. |
| Abbildungen der ausgewählten Station | Im Normalfall genau eine ausgewählte Peer-Identität; solange die optionale Delta-SNR-Ausreißererkennung eine geordnete Mehrfachauswahl von Funkwegen ermöglicht, kann Benchmark stattdessen die zugehörige zusammengefasste Mehrwegeansicht des Delta SNR exportieren. |
| Drill-Down-Fokusabbildungen | Optionale Messwertabbildungen in nativer Zeitauflösung und chronologische Ergänzungsabbildungen für die exakte ausgewählte Station und das aktive manuelle oder kandidatenverknüpfte Fokusintervall; sie ergänzen die Abbildungen der ausgewählten Station über den vollständigen Lauf, statt sie zu ersetzen. |
````

</details>

### Original in 8.4 Exportpaket der Analyse

<details><summary>Verbatim baseline passage</summary>

````text
Ist bei der Vorbereitung ein Drill-Down-Fokus aktiv, kann Performance `figure_drilldown_zoom_snr_evidence.png` und `figure_drilldown_zoom_temporal_evidence.png` ergänzen; Benchmark kann `figure_drilldown_zoom_delta_snr_evidence.png` und `figure_drilldown_zoom_coverage.png` ergänzen. Jeder Titel besteht nur aus ausgewähltem `Rufzeichen (Locator)` und ` - Zeitfenster: {start} bis {end} UTC`. Die Messwertabbildung bewahrt dieselben einzelnen beibehaltenen nativen Punkte wie der Browserfokus, statt Zeitmediane einzusetzen; die Ergänzungsabbildung bewahrt das zutreffende chronologische Outcome- oder Abdeckungsrezept. `run_metadata.json` enthält einen Block `drilldown_zoom` mit Schemaversion, Rufzeichen, Locator, exaktem `start_utc` und `end_utc`, gewählter Fokusoption, Ursprung `manual` oder `outlier_focus` und Rendervertrag. Ist ein Kandidaten-Overlay vorhanden, bewahren dessen registriertes Rezept und Signatur die fokussierte Episode und jede einzeln qualifizierende Kandidateneinheit im Fenster, das dezente Band der fokussierten Episode, lokale Baseline und Baselines davor/danach, robuste Streuung und Methode, robuste-z-Schwelle sowie absolute Abweichungsschwelle der exportierten Hilfslinien. Die Koordinaten der Hilfslinien bleiben auf die fokussierte Episode beschränkt, selbst wenn ein anderer markierter Kandidat im exportierten Fenster gegen eine andere Baseline oder Streuung bewertet wurde. Bei ausgeschaltetem Fokus oder nicht erfüllter Ein-Stations-Bedingung fehlen Fokusblock und Fokusabbildungen.
````

</details>

### Original in 8.4 Exportpaket der Analyse

<details><summary>Verbatim baseline passage</summary>

````text
Bei aktivierter Delta-SNR-Ausreißermeldung enthält `table_delta_snr_outlier_event_paths.csv` je qualifiziertem Funkwegereignis eine Zeile. Sie erfasst die zusammengefasste Klasse und die beobachteten UTC-Grenzen des Prüfereignisses, den funkwegübergreifenden Zusammenhang und die Abweichungsrichtung sowie exakten Funkweg, Richtung, Ereignisklasse des Funkwegs, Zeitlage und Anzahl gepaarter Evidenzeinheiten, erwartetes und beobachtetes Delta SNR, größte Abweichung, robusten z-Wert, Baseline-Diagnostik davor/danach und nahe Decode Outcomes. Derselbe exakte Funkweg kann im selben zusammengefassten Prüfereignis in mehreren Zeilen erscheinen, wenn er mehr als einen qualifizierenden Zeitraum beiträgt. Die Anzahl qualifizierender Funkwege zählt weiterhin die unterschiedlichen Identitäten aus `Rufzeichen + Locator`.
````

</details>

### Original in 8.4 Exportpaket der Analyse

<details><summary>Verbatim baseline passage</summary>

````text
`table_delta_snr_outlier_paired_evidence.csv` enthält für jede beibehaltene native gepaarte Einheit innerhalb dieser Funkwegereignisse eine chronologisch geordnete Zeile. Ereignis-ID und Funkwegereignis-ID verknüpfen sie mit der Zusammenfassung. Damit sie eigenständig lesbar bleibt, wiederholt sie die beobachteten Ereignisgrenzen, Funkweg, Richtung und Ereignisklasse des Funkwegs; die zusammengefasste Ereignisklasse steht nur in der Zusammenfassung, weil sie von der Klasse eines einzelnen Funkwegs abweichen kann. Die Tabelle enthält Target-SNR, bereits korrigiertes Reference-SNR, Delta SNR, erwartetes lokales Delta SNR, Abweichung von dieser Baseline, robusten z-Wert der einzelnen Einheit, Status der starken Ankerkriterien und Rolle als berichtete Grenze. Zeitstempel verwenden ISO-UTC; numerische Felder bleiben numerisch, statt Vorzeichen oder Einheiten in die Zellen einzubetten.
````

</details>

### Original in 8.4 Exportpaket der Analyse

<details><summary>Verbatim baseline passage</summary>

````text
Das Exportpaket bewahrt die verarbeitete Evidenz und die von WSPRadar erfasste Provenienz. Es enthält keine maßgeblichen externen Betriebsprotokolle, physischen Aufbaumessungen oder unveränderten Antworten der Upstream-Archive. Bewahre diese wie in [Abschnitt 8.3](#sec-8-3) beschrieben getrennt auf.
````

</details>

### Original in Literatur und Quellen

<details><summary>Verbatim baseline passage</summary>

````text
* <a id="ref-12"></a><a href="https://wsjt.sourceforge.io/wsjtx-main_en.html">[Ref-12]</a> **Offizielle Betriebsdokumentation.** WSJT-X 3.0.1 User Guide: WSPR-Nachrichtenformate Typ 1, Typ 2 und Typ 3; zufällige Zeitplanung über `Tx Pct`; Dateitrennung unter Windows mit `--rig-name`; Audioeinstellungen und Dateispeicherorte. QRP Labs, <a href="https://qrp-labs.com/qmx">*QMX firmware history and manuals*</a> und <a href="https://www.qrp-labs.com/images/qmx/manuals/operation_1_04_004.pdf">*QMX Operating Manual, firmware 1_04_004*</a>: modellspezifische Firmware sowie Betrieb und Zeitplanung mit Virtual U3S; <a href="https://www.qrp-labs.com/images/ultimate3s/operation3.12a2.pdf">*Ultimate3S Operating Manual, firmware v3.12a2*</a>: WSPR-Frequenzbereich, globales Frame-/Start-Verhalten, erweitertes WSPR, sequenzielle Mode-Einträge und `Aux`-Werte je Eintrag; <a href="https://qrp-labs.com/images/appnotes/AN003_A4.pdf">*AN003: Ultimate3/3S relay-switched filters*</a>: gefilterte Relais-/Treiberansteuerung und Schaltintervalle ohne HF. Abgerufen am 2026-08-25.
````

</details>

### Original in Anhang A: Parallele WSJT-X-Instanzen für simultanes RX

<details><summary>Verbatim baseline passage</summary>

````text
Mit diesem Verfahren wird unter Windows eine zweite isolierte WSJT-X-Instanz für einen simultanen RX-Vergleich im kontrollierten Aufbau eingerichtet. Das aktuelle WSJT-X-Handbuch nennt `--rig-name` als unterstützten Weg, die Einstellungen und beschreibbaren Dateien jeder Instanz zu trennen. Da sich WSJT-X-Versionen und Installationspfade ändern können, sollte bei abweichenden Menüs das aktuelle Handbuch geprüft werden. Parallele WSJT-X-Instanzen lösen dagegen nicht die Zeitplanung eines sparsamen simultanen TX-Hardware-A/B-Laufs; diese Grenze beschreibt Abschnitt A.4. <a href="#ref-12">[Ref-12]</a>
````

</details>

### Original in B.4 WSPRnet und ausgewählte Datenquelle prüfen

<details><summary>Verbatim baseline passage</summary>

````text
1. Sende mehrere vollständige synchronisierte Folgen.
2. Suche in der [WSPRnet-Spotabfrage](https://www.wsprnet.org/drupal/wsprnet/spotquery) nach jedem exakten Rufzeichen. Verlasse dich nicht nur auf die Karte; sie kann einen zuletzt bekannten Locator anzeigen.
3. Prüfe das vorgesehene Grid-4, die gemeldete Leistung, die Zeitstempel und die getrennten Frequenzen.
4. Suche Zyklen, in denen derselbe entfernte Empfänger beide Rufzeichen gemeldet hat, und prüfe übereinstimmende Zeitstempel.
5. Prüfe bei einer Folge aus zwei Aussendungen anhand des bekannten Zeitplans beide Positionen; das Archiv kennzeichnet sie nicht zwingend als Typ 2 beziehungsweise Typ 3.
6. Führe eine kurze WSPRadar-Vorabprüfung durch und warte, bis die Testspots dort tatsächlich abfragbar sind. Die Übernahme in wspr.live und andere Datenbanken kann `15 Minuten oder länger` dauern.
7. Untersuche nach der Bereitstellung unerwartete Häufungen von Only Target oder Only Reference und vergleiche Joint-Anteil, einseitige Outcomes sowie gepaartes Delta SNR zwischen den beiden Folgenpositionen. Ein beständiger Phasenunterschied kann auf Hash-Auflösung, Frequenzplatzierung, Erwärmung des Senders oder Leistungsabfall hinweisen.
````

</details>

### Original in B.5 Gerätespezifische Einrichtung

<details><summary>Verbatim baseline passage</summary>

````text
Die folgenden Beispiele sind Ausgangsverfahren und kein Ersatz für das Handbuch der installierten Firmware. Wiederhole die vollständige Vorabprüfung von Zeit, Frequenz, Leistung und Archiv nach jeder Firmware- oder Konfigurationsänderung.
````

</details>

### Original in B.5.1–B.5.2 QMX und QMX+ Virtual U3S sowie Ultimate3S

<details><summary>Verbatim baseline passage</summary>

````text
1. Installiere beim QMX oder QMX+ die aktuelle, exakt für das jeweilige Modell freigegebene Firmware, und folge deren versionspassender Virtual-U3S-Anleitung. Verwende die erste Version `1_04_000` nicht als allgemeines QMX-Rezept; QRP Labs kennzeichnet sie als QMX+-spezifisch, und spätere Versionen enthalten Korrekturen für Virtual U3S. Bestücke einen physischen Ultimate3S mit dem richtigen Ausgangsfilter für das ausgewählte Band.
2. Trage die beiden exakten Rufzeichen, denselben wahrheitsgemäßen Locator und die gemessene Leistung jedes Geräts als nächstgelegenen gültigen WSPR-kodierten dBm-Wert ein. Reguläre Typ-1-Rufzeichen sind vorzuziehen. Sind zusammengesetzte Rufzeichen unvermeidbar, konfiguriere auf beiden Geräten dieselbe erweiterte WSPR-Folge und prüfe, dass die Typ-2- und Typ-3-Phasen ausgerichtet bleiben.
3. Versorge beide Geräte über GNSS oder eine andere dokumentierte Zeitreferenz mit genauer UTC. Verwende denselben deterministischen globalen `Frame` und denselben beobachteten Start in einer geraden Minute. Deaktiviere nicht benötigte Einträge, damit kein Pfad eine zusätzliche Aussendung einfügt. Beim physischen Ultimate3S hat `Start = 00` die besondere Bedeutung „not used“; prüfe deshalb die angezeigten und beobachteten Starts.
4. Programmiere vollständige HF-Frequenzen nominal 100 Hz auseinander und halte beide vollständigen Signale mit ausreichendem Rand innerhalb des 200-Hz-WSPR-Unterbands. Geeignete Ausgangspaare sind `7.040050 MHz` und `7.040150 MHz` auf 40 m oder `14.097050 MHz` und `14.097150 MHz` auf 20 m. Dies sind tatsächliche HF-Frequenzen und nicht die USB-Einstellfrequenzen eines Empfängers. Beachte die Tonkonvention der installierten Firmware und prüfe die abgestrahlten Signale, statt allein den angezeigten Werten zu vertrauen.
5. Prüfe jedes Gerät einzeln, beide gemeinsam an Kunstantennen und zuletzt mit der vorgesehenen niedrigen Leistung auf Sendung. Schließe die obigen Prüfungen von Leistung, simultaner Signalqualität und Archiv ab, bevor du den Versuch aufzeichnest.
````

</details>

### Original in B.5.3 ZachTek-Firmware 2.19: Zufallswahl in getrennten Frequenzfenstern

<details><summary>Verbatim baseline passage</summary>

````text
Prüfe nach dem Flashen jeden Sender einzeln und anschließend beide gemeinsam an Kunstantennen oder über einen sicher gedämpften Messpfad. Prüfe tatsächliche HF-Frequenz, Zeitplanung, Ausgangsleistung, Filterung und spektrale Reinheit, bevor du Antennen anschließt. Bestätige bei einer kurzen Vorabprüfung auf Sendung außerdem, dass die beobachteten Frequenzen innerhalb des vorgesehenen unteren beziehungsweise oberen Fensters bleiben und beide Identitäten ausreichend Joint-Meldungen im selben Zyklus erzeugen, bevor du den Messlauf beginnst.
````

</details>

### Original in Anhang C: Referenz-SNR-Kalibrierung

<details><summary>Verbatim baseline passage</summary>

````text
1. **Gemeinsames Eingangssignal:** Beide Empfangsketten über einen geeigneten Verteiler und charakterisierte Kabel aus einer stabilen Antenne speisen.
2. **Verteiler charakterisieren:** Pegelunterschiede zwischen den Ausgängen und Kabeldifferenzen berücksichtigen; wenn praktikabel, die Ausgänge in einem Kontrolllauf vertauschen.
3. **Gepaarte Evidenz sammeln:** Beide Ketten gleichzeitig über den vorgesehenen Signalpegelbereich betreiben, ohne Verstärkung oder Decoder-Einstellungen zu verändern.
4. **Offset ableiten:** Gepaarte Delta-SNR-Evidenz verwenden und angeben, ob der berichtete Wert stationsgleichgewichtet oder aus den Rohpaaren berechnet ist.
5. **Konsistenz prüfen:** Nach Station, Zeit und SNR untersuchen. Ein konstanter Wert ist nicht vertretbar, wenn sich der Offset mit Pegel, Frequenz, AGC oder Zeit ändert.
6. **Vorzeichen anwenden:** Den beobachteten Offset `target - reference` mit demselben Vorzeichen eingeben.
7. **Validieren:** Messung wiederholen oder Pfade tauschen und prüfen, ob das korrigierte Delta des gemeinsamen Eingangssignals plausibel nahe null liegt.
````

</details>


## Review record: operator

Operator-scope review and staged implementation
==============================================

Accepted source model
---------------------
Parallel/co-authored English and German update against the shared approved specification: HAM basics assumed; WSPR familiarity not assumed; Benchmark first with Performance equally complete; compact first use linked to detailed setup; practical interpretation and next actions; selective removal of genuine repetition while preserving unique conditions, examples and scientific limits. Both baseline files were read before rewriting. Neither language was treated as the sole master.

EN baseline SHA256: 574cc1b41fa2b15a1d76b6ec97db59f4fc51f20295816c67110f867611c2d999
DE baseline SHA256: 09110629042cb4fabecd163ef6b9ebe8e698148cc1e9f91718691a82be2aa319

Drafts: drafts/operator_en.py and drafts/operator_de.py are complete source copies. Only Part 0, Part I introduction, Chapter 1, Chapter 3 and Chapter 8 differ. Chapter 2, all other chapters, references, TOC, imports/string wrappers and anchors are preserved. Source copies are staged only; no repository files changed by this agent.

Read applicable AGENTS.md sections on manual audience, ownership, exact labels, preservation, bilingual source models and semantic parity. The drafting script asserts unchanged content outside the assigned ranges and parses both completed Python sources with ast.parse. No regression tests or PDF generation run by this agent.

Subsection coverage and preservation dispositions
-------------------------------------------------
0 Why WSPRadar: retained physical station examples, complete-path measurement problem, controlled A/B history and citations, propagation/receiver caveats, repeatability question, WSPR network value, power/activity/station-weighting provenance, experimental limits and community value. Changed the overstrong assertion that WSPRadar could determine whether paired evidence represents the wider result to the observable distinction between jointly and one-sided decoded evidence. No inference of representativeness is claimed.

0.0 WSPR in 2 Minutes: retained acronym/authors, low-power propagation purpose, Type1 contents, narrow bandwidth, SNR reference and approximately -28 dB example, successful-uploaded-spot meaning, recorded identity/location/time/band/power/SNR, database sources, no radio decoder in WSPRadar, extended-message caution, source-pinned completed runs/no mixed sources, source acknowledgements, and missing-report/unknown-activity boundary. Added WSPRnet explicitly, synchronized two-minute cadence and approximately 111 s actual transmission duration. The -28 dB example is not presented as a guaranteed fixed decoder threshold.
  Relocation: exact Type2/Type3 paragraph (compound callsign and power without locator; 15-bit hash, six-character locator and power; separate cycles, not one row) goes to scientific §7.1. Science agent confirmed the transfer of BOTH baseline paragraphs and Ref12.
  Dedup: full RX/TX opportunity construction remains in authoritative §§7.3/7.4 and the direction-specific §2 guides; introductory activity/unknown distinction remains here with link. Do not remove those homes.
  Relocation: provider-capacity/failure paragraph goes to §5.6. Operations agent confirmed transfer and identified a needed factual qualification: automatic retry on another source only before Reference discovery commits a source; thereafter failure aborts/clears discovery. Preface now names sources and the single-database boundary without a blanket retry claim.
  Audience-level removal: explanation that less-negative SNR means stronger relative to noise is unnecessary HAM basics here; it remains where needed to interpret Performance figures in Chapter 2.

0.1 What WSPRadar can show: retains first-use Target and peer definitions, complete station versus controlled path, both analysis types, all six original practical-example rows and every example/validity qualifier, three Reference meanings, wider use cases and attribution limits. Benchmark bullet and table rows lead. Decode Rate and ΔSNR explanations are shorter but maintain opportunities, successful decode, both weights, joint-decode selection, normalization/correction, and cross-link to direction-specific guides. No practical table example was deleted.

0.2 What one run produces: preserves one bounded question, Benchmark signal difference plus one-sided outcomes, Performance reach/two rates/SNR, geography/time/stations, evidence traceability, within-run versus repeat-run distinction, export contents and external station-note boundary. Condenses the complete step inventory because its authoritative operational home is §1.3. Added explicit warning that folded UTC-hour views alone do not establish recurrence across dates.

0.3 Your first useful run: retains maintained historical demo, experiment context, prescribed first unchanged settings (operation in §1.1), many/few contributing stations, temporal recurrence, Benchmark joint coverage, selected path and row-level tracing, no evidence about own station, all four own-station question choices and decision purpose. Keeps invitation/link here; exact demo button recipe lives in §1.1.

Part I introduction: preserves experiment versus configured run/analysis versus result definitions and ownership of Chapters1–3, exact controls/troubleshooting in PartII and science in PartIII. Names Benchmark before Performance; retains optional expert diagnostic boundary.

1.1 Experiment foundation: retains question/support sentence, exploration versus confirmation, one band and actual-operating UTC window, exact uploaded identity and QTH, complete antenna/feedline/radio/tuner/gain/power/decoder/software/schedule/change record, stabilizing non-tested variables, RX audio/decoder/upload specifics, accurate actual/reported TX power, synchronized clocks, independent Reference uptime check, predeclared primary scope and separately preserved sensitivity analyses. Adds compact first-use bridge: receiving/decoding/uploading versus transmitting/remotely reported spots; WSPRnet and database availability check; completed interval instead of promised waiting time; appropriate comparison setup links; actual Run controls; first result inspection and saving. Demo button instructions live here, outside the product preface. Detailed WSJT-X or device instructions remain in the linked guide/appendices.

1.2 Analysis selection: all four questions preserved in Benchmark-first order. Both Performance and Benchmark meanings retained; complete fixed/local Reference meanings, same-cycle algorithm, component attribution limits and radius context remain. Peer defined earlier in §0.1, avoiding duplicate definition here. Performance explanation follows Benchmark designs without reduced depth.

1.3 Evidence path: all original seven stops, anchors and practical purposes retained. Segment Inspector explicitly remains geographic selection. Corrected temporal-folding/repetition inference; clarified malformed original 'opportunities, same-cycle pairs' to opportunities or Joint Spots. Added first-use forward reference to Chapter2's exact Joint Spot definition. Preserved full locator identities, counts, representative/unusual/high-impact path checks, locator changes, timing, one-sided evidence and isolated outliers.

3.1 Breadth/consistency/repeatability: all nine assessment dimensions retained. DE generic 'Spots' reconciled with EN Performance opportunity / Benchmark Joint Spot split. Retains broad versus internally consistent versus controlled distinction, no proof score, separate repeat-run criterion and observation-versus-cause distinction. Adds next action for contributor concentration and differing weightings; neither difference automatically invalidates a run.

3.2 Repetition/control: full predeclaration and explicit maximum-peer-distance rule retained, all seven strengthening actions retained, small-difference recurrence retained. Clarifies TX/RX comparison: align context as far as practical, inspect each direction separately, percentages are not interchangeable receiver/transmitter capability scores and do not diagnose an 'alligator' cause alone.

3.3 Reporting: minimum statement fields retained; detailed technical-report list shortened to signpost the complete §8.3 checklist, retaining a concise enumeration of all previous categories. Both conclusion templates retained in purpose but corrected: station-balanced Decode Rate is a mean of station rates, opportunity-level is the pooled opportunity fraction; RX/TX success direction explicit. Benchmark template now explicitly reports median ΔSNR only among Joint Spots, with one-sided supporting evidence visible. All design-specific reporting requirements, neighborhood radius/change, directional-pattern limit, color-scale convention and unsupported-claim boundary retained. Successful Target SNR explicitly normalized for reported TX power in both directions.

3.4 Preservation: correct two-stage prepare/download action; distinguishes completed-run package from settings-only config/link; current inspection selections preserved. External-note list compacted into a paragraph, retaining every original item and linking the exhaustive §8.3 record. Original limitation that software cannot infer the entire physical setup remains.

8 introduction: same bounded descriptive/comparative contract in direct language (included stations/cycles, weighting, counts, design, uncontrolled variables).
8.1 Claim classes: all five rows and three columns' meanings, all five result-type guidance bullets, local-neighborhood boundaries, positive/negative difference noncausality, Joint Evidence Share not win rate, scope reporting and repeatability retained. Renamed table's misleading 'What WSPRadar can support' header to 'Statement being assessed', since causal/inferential rows require external design/analysis. All eight avoid/preferred wording examples retained. Corrected 72% station-balanced example so it does not imply pooled weighting. Joint Spot terminology replaces routine paired-evidence synonyms; scientific attribution limit unchanged.
8.2 Boundaries: all six non-measurements and all eleven data/design boundaries retained. Jargon translated to operating consequences: Target-active asymmetry, successful-only SNR/no missing-side value, joint-only ΔSNR and dependent observations/row count. No limitation relaxed.
8.3 Reporting checklist: all three layers and all original items retained; adds database source and export date. Outlier enabled state/three thresholds/version/path/time/class/exploratory versus confirmation retained. Original export as evidence record and later-source/version change boundary retained.
8.4 Exports: both complete alternative file listings retained. Explicit ZIP root, one selected result folder, two-stage save operation, applicable inspection/focus selections, reprepare after change, exact table-inclusion behavior, processed Parquet versus inspection subset, source metadata and practical uses added. All ten artifact-table rows retained. Historical decode-selection metadata values, 2022 cutoff, prior-export provenance, null meaning and physical-mode caveat retained. All focus recipe/metadata scientific content, exact one-station applicability, selected multi-path Benchmark allowance, outlier row units/linkage/content/classes/IDs, enabled-empty and disabled-absent distinctions, metadata/signature claims and all public contract table identifiers retained. Removed only figure-title literal (self-evident presentation detail) from focus paragraph; actual identity/time metadata remains. Config cannot restore the original data, PNG/table/Parquet purposes and raw/external-record boundaries made explicit.
8.5 Disclaimer: unchanged.

Baseline language divergences resolved
-------------------------------------
1. DE §0.0 simultaneous TX says a common truthful Grid-4 while EN says truthful reported locations. The introductory caution is now common and defers physical local-setup requirements and exact database identity to AppendixB/§7.1–7.2. Those existing detailed homes retain co-location/reporting requirements. No new false-location allowance.
2. DE §3.1 said generic qualifying opportunities/spots where EN identified Joint Spots. Both now distinguish Performance opportunities and Benchmark Joint Spots.
3. DE §3.3 'bei einem Referenznachbarschaft' corrected to grammatical feminine construction.
4. DE §8.1 'Kontrolliertes Referenzaufbau/-station' corrected to 'Kontrollierter Aufbau' and incorrect neighborhood pronoun repaired.
5. DE export Reference-SNR adapted to Referenz-SNR in prose; filenames and field identifiers unchanged.
Intentional localization: exact German demo button remains 'Ausgewaehlte Demo starten' because i18n.py uses that spelling; surrounding German retains natural umlauts. Product names and file/field names retained unchanged.

Independent reverse outline — English final scope
-------------------------------------------------
0: station changes motivate comparison; confounders require controlled/repeated paths; WSPR's network gives broad traceable observations without isolated gain proof.
0.0: protocol orientation -> report/database chain including WSPRnet -> analyst/decoder distinction and extended identity caution -> one source per run -> missing observation is not automatic failure.
0.1: Target/peer -> relative Benchmark versus own-station Performance -> six use-case designs -> physical Reference meaning -> useful pattern finding without causal component attribution.
0.2: one result -> metrics plus supporting evidence -> geographic-to-row traceability -> repetition distinct from internal agreement -> package plus notes.
0.3: maintained historical demo -> follow one feature and its support -> own-station question and first-use link.
I/1.1: experiment/run/result -> question and exploratory purpose -> demo action -> WSPR reports, database availability, comparison setup, analysis inputs, inspection/export -> stable station record -> confirmatory scope.
1.2: Benchmark/RX/TX question matrix -> fixed or constructed Reference and limits -> Performance without Reference.
1.3: Map -> geographic selection -> metric/weighting/outcome views -> time and actual recurrence -> identities -> representative path -> evidence rows.
3.1: breadth/support/control dimensions -> repeatability distinction -> investigate concentrated or disagreeing evidence -> separate observation from explanation.
3.2: freeze primary scope -> extend/repeat/control/audit -> small effect support -> unlike RX/TX denominators.
3.3: minimum statement -> full checklist -> correctly weighted Performance statement -> joint-only Benchmark statement -> design, scope and language limits.
3.4: select view, prepare, download -> settings alone not evidence -> external physical record -> reproducibility boundary.
8.1: five strengths of claim and prerequisites -> each result's supported statement -> eight overclaim/replacement examples.
8.2: quantities not measured -> observation/selection/dependence limits -> useful descriptive evidence remains possible.
8.3: analysis, supporting evidence, external experiment -> original package vs later retrieval.
8.4: capture current view -> alternative inventory -> artifact scopes -> historical provenance -> optional focus -> outlier summary and Joint-unit linkage -> conditional presence/public contract -> how to use data without treating config as a data snapshot.
8.5: auditability does not create warranty.

Independent reverse outline — German final scope
-------------------------------------------------
0: Umbau und Stationsverbesserung als Ausgangsfrage; mehrere Einflussgrößen am vollständigen Funkweg; kontrollierte Vergleiche, Wiederholung und prüfbare WSPR-Beobachtungen; keine isolierte Bauteilmessung.
0.0: Zwei-Minuten-Betrieb und Typ1 -> Spot-Upload in Datenbanken -> WSPRadar als Auswertung, nicht Decoder -> erweiterte Meldekennungen -> eine Datenquelle je Lauf -> fehlende Meldung ohne Aktivitätsnachweis bleibt unbekannt.
0.1: Target und Peer -> relativer Benchmark zuerst, Performance ohne Referenz -> sechs unveränderte Anwendungsfelder -> Bedeutung des Referenzaufbaus/der Station/Nachbarschaft -> Muster beschreiben, Ursache nicht automatisch bestimmen.
0.2: ein gewähltes Ergebnis mit komplementären Größen -> Karte, Bereich und beitragende Beobachtungen -> Wiederholung an Einzeltagen und in weiteren Läufen -> Export samt Aufbaunotizen.
0.3: historische Demo erkunden -> Stationsbreite, Tagesmuster und gemeinsame Decodes prüfen -> eigene Frage auswählen und Einstieg verlinken.
I/1.1: Versuch, Lauf und Ergebnis unterscheiden -> Frage/Prüfabsicht -> Demo starten -> WSPR erzeugen/hochladen, Daten prüfen, Vergleich vorbereiten, Lauf konfigurieren, Ergebnis prüfen/sichern -> dokumentierter stabiler Aufbau -> Bereich vorab festlegen.
1.2: Frage nach RX/TX-Unterschied oder eigenem Betrieb -> exakte Referenz beziehungsweise wechselnder lokaler Median -> Zuordnungsgrenzen -> vollständige Performance-Station ohne Referenz.
1.3: Übersicht und geografische Auswahl -> Gewichtungen/Signalpegel/Outcomes -> Tagesstunden nicht mit Wiederkehr verwechseln -> Stationskennungen und Einzelpfade -> Zeilenprüfung.
3.1: Breite, Mengen, Übereinstimmung, Geografie/Zeit, Kennungsqualität und Kontrolle -> Wiederholbarkeit eigenständig -> dominante Beiträge untersuchen -> Beobachtung von Erklärung trennen.
3.2: festgelegter Hauptbereich und Sensitivität -> länger beobachten, wiederholen, Bedingungen festhalten -> kleine Unterschiede absichern -> Sende-/Empfangsprozentsätze nicht gleichsetzen.
3.3: Mindestangaben und vollständige Checkliste -> unterschiedliche Mittelung der Dekodierraten -> ΔSNR-Aussage innerhalb Joint Spots -> Design und Grenzen korrekt benennen.
3.4: passende Ansicht sichern, Paket vorbereiten und wirklich herunterladen -> Konfiguration/Link sind keine Evidenzdatei -> externe Versuchsnotizen.
8.1: deskriptive bis inferenzstatistische Aussagen und ihre Voraussetzungen -> Aussage je Ergebnistyp -> acht unzulässige Verkürzungen mit sachgerechter Alternative.
8.2: keine Gewinn-/Empfindlichkeits-/Kausalitätsmessung -> Auswahl-, Fehlstellen- und Abhängigkeitsgrenzen -> nützliche deskriptive Ergebnisse dennoch möglich.
8.3: Analysedefinition, Evidenz und physischer Versuch als drei Aufzeichnungsebenen -> ursprünglichen Export behalten.
8.4: Ansicht und Download -> alternative Ordner, bedingte Dateien -> Tabellen-/Parquet-Bereiche -> historische Abfrageprovenienz -> Fokus nur für eine exakte Station, optionale Mehrwegeansicht sonst -> Ereignis- und Einzelevidenzdateien/IDs -> öffentlicher Feldvertrag -> Dateien ihrem Zweck entsprechend nutzen.
8.5: geprüfter Quellcode ersetzt keine Gewährleistung.

The two outlines were compared for conditions, exceptions, population definitions, weighting, scope, attribution and reproduction requirements. No unresolved one-language-only semantic unit remains within the assigned final draft. Cross-agent relocations require root integration of both §7.1 and §5.6 transfers before publication.

Factual evidence inspected
--------------------------
* i18n.py:146,159–162,406–407,802,815–818,1062–1063: exact demo, analysis and prepare/download labels.
* i18n.py:1724 and 2125: existing shared result help confirms two-stage export and processed evidence/current scope.
* ui/plots/opportunity_figures.py:369,406,432 (and temporal analogs 1087/1096): per-peer rate, arithmetic mean of per-peer rates, pooled hits/opportunities. Establishes required §3.3 and §8.1 correction.
* ui/results_export.py:1866–1960: one normalized database source; provenance, export date, version, config-derived analysis settings, actual decode mode, selected scope and station selections.
* ui/results_export.py:2494–2649: named ZIP root, config files, applicable result folder, figure lists, all three ordinary CSVs always written, enabled-only outlier CSVs, processed Parquet copied from completed map context.
* ui/results_export.py:2790–2850: current package signature invalidation, preparation action and separate download action.
* ui/inspector/outlier_export.py:32–35 and fixed schemas/metadata builder: stable filenames, event-path/native paired rows and conditional status contract. Existing detailed outlier semantics preserved.
* config/app_config.py:29–64: wspr.live, WD2, WD1 configured source order. Provider retry qualification found by operations agent at ui/run_controller.py:1538; no retry promise remains in this draft's preface.
* Chapter2 existing Performance guides explicitly state common 30 dBm/1 W SNR basis in RX and TX; verified implementation review by science agent. These meanings retained.
* Official ARRL WSPR overview https://www.arrl.org/wspr (retrieved 2026-10-03): message fields, 110.6 s, even-UTC-minute timing, about6Hz, 2500Hz SNR reference, decoder uploads to WSPR database. Existing Ref8 retained; old approximately -28dB example qualified, not converted into a fixed decoder guarantee.
* Official WSJT-X User Guide https://wsjtx.github.io/wsjtx/guide-full.html (retrieved 2026-10-03) WSPR section: WSPR mode, Monitor, Tx Pct, power; official documentation supports receiver/audio/reporting setup distinction. Original Ref12 URL failed the browser size limit; official indexed guide used as verification fallback. Reference block itself unchanged per assignment.
* https://wsprnet.org/drupal/wsprnet/spots could not be fetched by the web tool; no claim about the current WSPRnet website control layout made.

Chapter 2 review only / integration notes
-----------------------------------------
No Chapter2 edits in these copies. Existing RX/TX Performance figures already state normalized1W SNR correctly and distinguish mean station rates from pooled opportunities; no extra correction needed there. Existing recurrence cautions already require individual-date checks and are now consistent with Chapters0/1. Existing Joint Spot definition remains authoritative in Chapter2; §1.3 points forward to it. Optional diagnostic scope and enabled-only export link remain consistent with Chapter8. No heading changes in assigned chapters, so no TOC label changes requested.

Remaining verification boundaries
---------------------------------
Scope, syntax, links and semantic parity checked on staged text. Root must integrate coordinated relocations, regenerate README, perform required documentation/test checks, and render final EN/DE PDFs. No physical WSPR setup, live database completeness, application browser flow or exported ZIP was run in this draft review.


Final static verification and word counts
-----------------------------------------
{
  "en": {
    "sha256": "5f18c7517926252006106b0b0c700a1474c3f16ee7a36d980389ca55dde07165",
    "counts": {
      "Preface": {
        "baseline": 2705,
        "draft": 2267
      },
      "Part I intro + Chapter1": {
        "baseline": 1018,
        "draft": 1326
      },
      "Chapter3": {
        "baseline": 1080,
        "draft": 1160
      },
      "Chapter8": {
        "baseline": 2243,
        "draft": 2493
      },
      "Assigned total": {
        "baseline": 7046,
        "draft": 7246
      }
    },
    "missing_links": [],
    "anchors_unchanged": true,
    "syntax": "pass"
  },
  "de": {
    "sha256": "9da947711eeeb57a46183990e429826287e2eb745a4e01fb630561bfe25ec504",
    "counts": {
      "Preface": {
        "baseline": 2573,
        "draft": 2139
      },
      "Part I intro + Chapter1": {
        "baseline": 993,
        "draft": 1265
      },
      "Chapter3": {
        "baseline": 1089,
        "draft": 1150
      },
      "Chapter8": {
        "baseline": 2176,
        "draft": 2391
      },
      "Assigned total": {
        "baseline": 6831,
        "draft": 6945
      }
    },
    "missing_links": [],
    "anchors_unchanged": true,
    "syntax": "pass"
  }
}

Counts use whitespace-separated tokens including Markdown; they are diagnostic, not parity proof. Added first-use procedure increases Chapter1 while repeated overviews/reporting checklists shrink other operator sections. Final text outside assigned scopes remains unchanged by the drafting script assertion.


## Review record: operations

Operational manual review and staged implementation — 2026-10-03

Scope and source model
----------------------
Owned: Part II introduction; Chapters 4 and 5; Part IV introduction; Appendices A, B and C. License unchanged. Full draft source copies are drafts/operations_en.py and drafts/operations_de.py. The parent must merge only those owned spans, not replace whole manuals with these copies.

Both language baselines are co-authoritative. This was a parallel EN/DE edit from their current semantic content, not a translation of a newly preferred English source.
EN baseline SHA256: 574cc1b41fa2b15a1d76b6ec97db59f4fc51f20295816c67110f867611c2d999
DE baseline SHA256: 09110629042cb4fabecd163ef6b9ebe8e698148cc1e9f91718691a82be2aa319

Pre-edit parity: scientific values, defaults, timings, sign convention, detector scope and hardware safeguards agree. Minor exposition differences: German Appendix A already points explicitly to the TX scheduling limitation; English now has the same pointer. English §5.3 explicitly says a correct display in another database does not establish matching in the selected database; German now says this explicitly too. German §4.2 repeats the configured-QTH map origin already present in both §4.3; retained. German B.4 says shared grid-4 while English says intended reported locations; both refer to the same controlled, collocated TX setup already defined in B.1/B.2. No scientific disagreement inferred from those wording differences.

Confirmed corrections
---------------------
1. §4.4 Joint minimum: default 1 does not require repeated observations. The revised table says at least the selected number of Joint Spots per exact station identity. The same threshold applies separately to Only Target and Only Reference; neither satisfies the Joint requirement. Evidence: ui/state_manager.py:137–142; ui/components/config_panel.py:797–844; core/compare_engine.py:55–95.
2. §4.5 persistence: the baseline says one exact identity per result type. Benchmark permits and persists multiple selected identities when outlier reporting is enabled. Ordinary Benchmark and Performance remain at most one. Evidence: ui/config_io.py:648–660,1247–1257; ui/components/inspector_stations.py:541–550. The separate exactly-one-station native focus constraint remains unchanged. Parent/operator agent notified to check §8.4.
3. §5.6 relocated routing: automatic provider failover is conditional, not guaranteed for every failed source. A Reference location discovery commits the ensuing run to its database; failed committed source aborts the attempt and clears discovery. Evidence: ui/run_controller.py:663–667,1538–1569; ui/reference_location_state.py discard_failed_discovery_source; core/provider_dispatch.py:295–305; config/app_config.py:29–74. Revised text includes restarting explicitly and reviewing the resolved location. Ordered capacity spillover, whole-run retry and no mixed database records are preserved.
4. Appendix C: explicitly use 0.0 dB correction for the offset-estimation run. This is already the contract in §4.3 and i18n.py establish_offset option/guidance; makes procedure complete, avoids estimating a residual after an old correction. Preserve sign, weighting disclosure, common input, level/time/frequency/AGC checks and repeat/swap validation.
5. B.4: the fixed '15 minutes or more' database delay is not documented by the cited primary service. wspr.live says every few minutes. Revised wording retains possible longer delays and requires actual queryability, with link to §5.6's explicitly non-guaranteed five-minute estimate. No claim of a fixed maximum or complete dataset was added.
6. §5.4 reference token [Ref-10] is made a working internal link in both languages.
7. §4.4 replaces 'Target-plus-counter opportunities' with confirmed opportunities (successful Target decodes or Misses), preserving the denominator and numerical minimum.
8. §5.2 replaces the suggestion to assess representativeness in-app with a concrete comparison of which stations and times contribute Joint Spots versus one-sided outcomes, limiting ΔSNR conclusions to Joint evidence.

Practical presentation changes
------------------------------
§4.5's two long focus paragraphs are split under six short inline leads: choose focus; individual observations; open outlier focus; markers/band; detector guides; save evidence. All original behavior, limits, range values and caveats remain in their original authoritative subsection. The cosmetic literal figure-title example was removed on the parent's explicit review instruction; identity and displayed window information remain elsewhere in the same section. No new table design was introduced.
Database/Datenbank replaces queried-data archive narrative inside owned spans. Literal commands, paths, software identifiers, UI labels, reference block and license are untouched. ΔSNR consistently denotes the value; Joint Spots denotes the Benchmark observation unit. Include Unpaired Evidence/Ungepaarte Evidenz einbeziehen remains literal UI wording. Ordinary 'pairing/paired subset' remains where it explains matching or missingness rather than inventing another unit name.

Per-subsection audit and preservation/reverse outline
----------------------------------------------------
Part II: operating-reference role and 2.5/4.6/7.11 routing preserved; 4.6 made a direct English link and ΔSNR normalized.
4 introduction: scientific versus saved view versus transient state, invalidation and formal-schema authority preserved; no structural changes.
4.1: all nine workflow rows, Review placement/open behavior, Guided demo shortcut, delayed completion/navigation, schema rejection, demo lifecycle and permanent raw-query reuse retained. Only database terminology changed. Evidence reviewed: ui/config_io.py, ui/run_controller.py, config/app_config.py, i18n.py; no live browser claim.
4.2: four questions, roles, exact callsign syntax, QTH 4/6, band list/default, fixed 24h UTC window, 2008/31-day/minute precision, identity not legal authority and grid4 versus full-QTH geometry retained. Database terminology only. Evidence: ui/components/config_panel.py date controls, ui/state_manager.py, config/app_config.py MAX_DAYS_HISTORY, core/analysis_runner.py matching.
4.3: design choices/default and preservation, Guided/Classic help, complete-input validation, all five control rows, blank correction=0 and ±99.9 range, decimal point, 100km/10–250km step10, reference discovery, full locator variants and uncertainty retained. Sign example +1.6, pre-median correction, three calibration intents, no automatic offset, unstable-chain limits and neighborhood common-offset requirement unchanged. Evidence: ui/components/config_panel.py:604–624, ui/reference_location_state.py, i18n.py, config/plot_constants.py.
4.4: filters before confirmatory run; prefix filter only peers; movement versus metadata; solar thresholds; distance inclusive exclusion; gate outside range; numeric defaults/ranges; manual values persist; distance applied after retrieval retained. Joint minimum wording corrected as above. Evidence: config/plot_constants.py:6,27; ui/components/config_panel.py:797–844; core/compare_engine.py:55–95; ui/population_exclusion_state.py.
4.5: saved scope/time bins/counter-only and non-Joint visibility, large-table fallback, all four duration tiers and 2h availability, missing bins not zero retained. Multi-selection persistence corrected. Zoom options/center/edge translation/stepping/bounds/filter effect; native values after consolidation; removed plot layers; companion aggregation/full-window panels; title placeholders; full supported outlier flank span; >24h; provenance/manual switches; stars; selection band padding/clipping/not CI; focused guides and other-candidate baselines; separate qualification gates; focus not saved/URL and additive exports all retained. Evidence: config/config_schema.py:45–75; ui/inspector/drilldown_focus.py; ui/config_io.py; ui/components/inspector_stations.py. The 150,000-row Streamlit browser behavior was preserved as established baseline; not independently exercised in a browser in this subtask.
4.6: optional expert-only Benchmark detector; exact identity; native Joint Spots and display-bin independence; no one-sided ΔSNR; off behavior; 6/3/3 defaults; inclusive 0.1–100; 0.01 dB tolerance only for dB comparisons; no rounding; no probability interpretation; saved thresholds/re-run; all duration classes same gates; no duration discount; predeclared thresholds retained. Evidence: config/delta_snr_outlier.py:10–39,53–87; i18n.py first detector labels; previously reviewed outlier_candidates.py.
5 introduction and5.1: definition before changing filters, all seven checks and postcheck order unchanged.
5.2: all symptom rows and observed-versus-configured counts retained. No inventing maxima; Target-only successes once; partial Performance availability; missing Joint values; pair coverage; independent activity; OnlyReference0; sign/power/calibration; radius dependence; rowlimit remedies; recent-upload check retained. Only ΔSNR terminology changed. Runtime evidence includes ui/run_controller.py failure/rowlimit handling and core/compare_engine.py; no new diagnostic classifier claimed.
5.3: exact Target/grid4, Reference discovery role/window/source and variants; physicalsite uncertainty; neighbor geography; Type2/3 not reconstructed; missing locator; callsign3–15 and4/6 locator validation; full peer identity retained. English explicit selected-database versus other display caution added to German for parity. Database terminology only otherwise.
5.4: strictcode1 first, Target-side-empty trigger, end strictly before2022-01-01, boundary behavior, broader/nonphysical certainty and exported decode_filter_mode retained. Evidence: core/analysis_runner.py:49–50,262. Link repair only beyond terminology.
5.5: Target activity observation, downtime not automatic failure, Target-centering, reference uptime and swapping effects all unchanged.
5.6: source errors/duplicates/power/locator/delay/corrections, fewminutes and qualifiedfive-minute wait, robust-method limits, status/provenance table, no changed scientific method, >1,000,000 complete-row rejection and remedies retained. Adds concrete database availability check and moved routing paragraph, corrected for committed-source failure.
Part IV: scope of practical supplements and use applicable sections unchanged.
A introduction: Windows isolatedRX scope, supportedrig-name/current-version caution retained; EN now has the TX limitation pointer already present in DE.
A.1: exact Windows command, settings/log/save paths and startup/close steps unchanged; verified official WSJT-X guide file-location/FAQ sections.
A.2: allclose/copy/paste/rename/intentionalreplace steps unchanged.
A.3: independentaudio,48kHz16bit,Save/AzEl paths, Reference callsign/location, band/inputlevel/uploadidentity/clocks and no automaticRF independence unchanged; official WSJT-X guide Audio section.
A.4: randomTxPct,100%necessaryeverycycle,110.6/120≈92%RFduty,5–20%cycle recommendation notprotocol,lowerbusy/longtests and deterministic beacon alternatives unchanged; official WSJT-X WSPR section and QRP manual WSPR duration.
B introduction/B.1: completepaths, bench/database beforemeasurement, RF/licensing/callsign cautions, two valididentities, Type1preference, Type2/3 alignedschedule/samephysicalQTH retained. Database terminology only.
B.2: accurateUTC/GNSS, commonband/evenstarts/restartchecks, alignedType2/3, fixed100Hzversusrandomlanes,200Hzlimits, actualRFversusdial/toneconventions, four exactfreqexamples retained. Official QRP manuals confirm frequency bands and Frame/Start roles; no claim hardware benchtested here.
B.3: loads/safeattenuation, actualpowerreferenceplane, nearestvaliddBm,20/23/27/30 values,100mW–1W, no falseidentitypower/no excessRF, two-signal bandwidth/harmonics/spurious/IMD checks and uncontrolledcompletepaths all unchanged.
B.4: allseven preflightsteps, spotquerylink/maplimitations, timestamp/receiver overlap, two-phasesequenceavailability, outcomephasecomparison, physicalfault hypotheses, stableidentitiesbeforemeasurement and tested-combination boundary retained. Delayclaim corrected; ΔSNR/JointSpot terminology normalized.
B.5 introduction: version-matching and repeatallpreflightafterchanges retained. Database terminology only.
B.5.1–2:16physicalU3Sentries,conditionalVirtualequivalence, hardwaredifferences,1_04_000QMX+specificversioncaution, filters,identities,powers,phasealignment,Frame/Start00caution,fixedfrequencies/observedplacement,benchandairtest,swappedfrequencyschedule,20minFrame/Start04/twoentries=20%cycles,allfourswaprows,bandedgeoffsets,balancedfrequencycaveat and compoundmessageexception retained. No firmware recipe changes. Official U3S3.12a2 and currentVirtualU3Smanual confirm these relevant mechanics.
B.5.3: publishedimmutable2.19ESP8285source,stockrange,twoeditlocations,allthreeCppcodeblocks,centihertz,laneranges,min61Hz tone0sep/≈57Hznearesttones,10Hzendpoint/6.6Hzhightoneedge,randomizationlimits,swapconfirmation,two-phase samefreq,Product_Model1048/modelrisk,ESP8285/NeoGPS,stockrecovery/config/sourcehash andpostflashRFpreflight retained. Source fetched read-only to reviews/zachtek-2.19.ino. SHA256 f45aabac7688c8dd5ae73559de7fb58485029b79c65e3cd40ac04dd09d9d28df. Exact source:126 model1048;1483/1555 random statements;1520–1531 secondmessage no freq reselection;1619 tone increment146centihertz; header97–109 buildprerequisites. No compiler/device test performed.
B.6: frequencyexchange, separaterun, hardwarecrossover, keepactualroles/corrections/scope records, careful pooling, between-runrepeatability versuswithin-runphaseconsistency unchanged.
C: commoninput/splitter/cables/outputswap/stablegain, weightedversuspooledestimator, time/level/freq/AGC check,sign,repeat/swapvalidation, nottraceable and residualimperfections retained. Added0dBcalibrationstart; replaced 'raw pairs' with pooledJointSpots to distinguish retainedscientificobservations from rawproviderrecords.
License: exact unchanged source bytes in both languages.

Relocation ledger
-----------------
Baseline EN/DE §0.0 paragraph at line48 moves to §5.6 by parent-approved coordination with operator_review. All unique roles retained: ordered capacity spillover vs provider-failure retry, unpublished attempt discard, complete-run restart, one completed-run source, no cross-source mixing. Qualification for committed Reference discovery added from runtime evidence above. §0.0 removal is owned by operator_review; these full draft copies intentionally retain its original line48 because it is outside this agent's edit spans.
No other content relocated out of owned scope. No unique correct operating guidance dropped. The parent explicitly authorized removing the cosmetic figure-title template; it remains in the verbatim baseline and changes ledger. Explicitly superseded content is logged in operations-changes.json with exact before/after strings: repeated Joint evidence at minimum 1; only one saved identity; unconditional source failover; unsupported fixed 15-minute delay claim; raw-pairs terminology; representativeness implication; unclear Target-plus-counter denominator wording. Parent preserves verbatim baseline originals globally.

Primary web sources checked and reference recommendations
--------------------------------------------------------
WSJT-X User Guide, current page identifies3.0.1: https://wsjt.sourceforge.io/wsjtx-main_en.html . Relevant sections Audio, WSPR, filelocations, multipleinstanceFAQ. Large-page open failed but targeted official search exposed relevant manual content; official2.7PDF Audio corroborates48kHz16bit. Existing Ref12 URL remains appropriate, no mandatory URL change.
QRP Labs QMX page https://qrp-labs.com/qmx (page updated24Sep2026): directs users to matchingmanual/firmware and separateVirtualU3S manual;1_04_009 changelog corrects WSPR250Hz-too-low behavior. This supports existing on-devicefrequencyverification/versioncaution.
ADD to Ref12 (parent ownsreferences): Virtual U3S manual https://qrp-labs.com/images/qmx/manuals/VirtualU3S_1_04_008a.pdf . Officialpage lists document28Aug2026; manual footer1_04_008a. §§3.1/3.2 Frame/Start/schedule and§5.10WSPR, including evenminutes and Start00unused, support deviceprocedure.
Ultimate3S3.12a2 officialmanual: https://www.qrp-labs.com/images/ultimate3s/operation3.12a2.pdf . Sixteenentries,Frame/Start mechanics and specialStart00 verified; preservematchingfirmwarecaution.
wspr.live https://wspr.live/ describes scrapingWSPRnet everyfewminutes; nofixed15minutecompleteness rule.
ZachTekimmutablemanufacturer source (existingRef20): https://github.com/HarrydeBug/WSPR-transmitters/blob/1657468ea27052167191a7deda2440a535567ecd/Standard%20Firmware/Release/Hardware_Version_2_ESP8285/WSPR-TX2.19/WSPR-TX2.19.ino . Retrieved samepublicrevision through raw.githubusercontent.com after webreader cachemiss; directread succeeded with automaticreadapproval. Preserveimmutablehashreference; no update needed.

Content and parity checks
-------------------------
Every changed semantic unit was checked in both languages: same objects, thresholds, conditions, before/after/rerun scope, exactidentity, savedstate, evidenceunit, correctiondirection and causalitylimits. New German prose was composed for natural technical usage, not wordwise substitution; final inspection fixed grammatical gender/article consequences of database terminology. Both languages retain exact commands,paths,codeblocks,frequencies,versions andpublicidentifiers. The correction changes apply in both. DE-specificdisplaylabels remaintheircurrentUIvalues. No new blanket table layout or headers were introduced.
Reverse outline confirms operatingreference → diagnosis → platform/deviceprocedures → calibration is unchanged. New inline focus leads organize existing meanings rather than moving optional detector material into first-useflow. Scope compares confirm PartI,PartIII,References andLicense are unchanged in each stagedcopy. Bothsources parse with Python ast.parse. These are documentation-only checks; parent owns integrateddocs/PDF/tests/READMEverification. No runtimecode changed and no broadregressions, liveprovidercomplete-run, physicalhardware,firmwarecompile,orbrowserlarge-table tests claimed.

Owned-scope whitespace word counts: EN 8774→9036 (+262); DE 8719→8975 (+256). Most increase is §0.0 routing material moved into this scope plus its necessary failure qualification and the zero-correction step. Per-heading counts are recorded in operations-wordcounts.json. Final automated preservation checks passed: Python parse, identical owned anchors, unchanged fenced commands/code, unchanged inline mathematics and unchanged license. Neither the device firmware nor the app was executed by these checks.

Final root-review dispositions: §4.5 no longer retains the cosmetic title-template sentence (the earlier per-subsection outline described the initial draft). §5.2 retains all original operational checks while replacing the representativeness wording as recorded above. Parent assembly normalizes the new em-dash spacing. Ref12 remains untouched in these drafts; the integrated parent version adds the independently verified Virtual U3S manual link.


## Review record: literature

Scope: complete Chapter 6, Part III introduction and source list review, 3 October 2026.
Accepted source model: parallel/co-authored English/German pair in baseline, with the approved shared audience, Benchmark-first priority, Joint Spots/Delta SNR vocabulary, practical explanations and scientific preservation.

Section-by-section audit:
6 introduction: retained focused/non-exhaustive review and evidence-class limitations; added a practical reading purpose (common conditions, activity checks, chain controls).
6.1: retained Taylor/Walker direct quote unchanged; replaced archive narrative with database. Preserved observation selection, heterogeneity, user-supplied identity/power, changing equipment and unknown operating schedules in simpler prose.
6.2: verified Lo et al. on 7 MHz, callsign/location checks and observed-activity qualification. Retained distinction between this prior art and WSPRadar-specific conditioning, denominators, station weighting, outcomes and local References.
6.3: all five case studies reviewed against primary papers/operator articles. Corrected Toledo attribution: he discussed per-cycle switching and simultaneous experiments by other operators, rather than proposing those experiments himself. Replaced 'conditioned simultaneous RX' with common-antenna chain-offset check before antenna comparison; preserved strongest-precedent qualification and polarization/ionosphere boundary. German 'RX Reference Setup/Station' was broader than English controlled-RX claim; harmonized to controlled comparisons. Numerical details and all Zander qualifications retained.
6.4: retained all named tools and specific capabilities. Explained relational self-join in ordinary language; retained two receivers/same transmitter/time/band and all summary/export types. Preserved distinctions from WSPRadar method. No global novelty claim.
6.5: Benchmark listed first, Performance equal and explicit. Combined same-cycle matching with Joint Spots and Delta SNR to avoid introducing synonymous comparison objects. All eight original integration capabilities remain; unique method contribution claims remain bounded to reviewed sources.
References: all 20 anchor identities/publication titles/URLs retained. Stable publications checked against sources where assigned below; device/service reference updates coordinated with other reviewers. No new or renumbered citations.

Primary sources actually inspected:
https://arxiv.org/html/2209.08989v1 (sections III-VI; same-receiver model, power assumptions, 150-200 joint reports from 15-35 receivers, near-3dB spread, mean precision versus systematic uncertainty)
https://pure.tudelft.nl/ws/portalfiles/portal/125931824/4809313.pdf (published Vanhamel article via author institution; DOI landing unavailable to retrieval tool; sections3-5 show common antenna calibration and 1.2dB offset, simultaneous chains, polarization discussion)
https://sivantoledotech.wordpress.com/2010/09/24/failure-to-use-wspr-to-compare-antennas/ (hour-long blocks, rapid variation; credits Destrem switching and Preston simultaneous TX)
https://www.qsl.net/kp4md/wspr.htm (29km local separation, VE6PDQ at1750km, power correction, frequency-hopping mismatch, VOACAP and reciprocal reports)
https://www.researchgate.net/publication/319903566_Improving_HF_Band_SNR_from_analysis_of_WSPR_spots (author-posted article text; same sender/time, soil moisture/time/distance/station changes)
https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf (3-page original QST article; database quotation and multi-week UTC folding)
https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2023.1184171/full (network observations, bottomside ionosphere, cross-calibration recommendations)
https://www.mdpi.com/2073-4433/13/8/1340 (search-indexed full article after direct fetch error; method3.1 activity/schedule/location, discussion)
https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf (database self-join, SNR differences, medians/quartiles/time/geography and exports)
https://wspr.rocks/help.html (SQL, SpotQ, maps/heatmaps)
https://www.sotabeams.co.uk/wsprlite-classic (DXplorer/DX10)
https://sites.google.com/myuba.be/wspr-station-compare/home (references Vanhamel and Zander)
https://wspr.bsdworld.org/ (WSPR-based antenna analysis service)
https://www.gm4eau.com/home-page/wspr/ (Excel/VBA, reporting/filtering/mapping/timeline)

Semantic preservation:
All literature case studies, numerical sample details, source-class distinctions and uncertainty boundaries retained. Formal jargon replaced by its meaning, not removed as a concept. Sole factual correction is precise Toledo attribution; German controlled-RX scope aligned. No formulas present/changed in this scope.

Independent reverse outlines:
EN: why read methods -> focused evidence review -> database value and selection -> activity before interpreting silence -> slow-block comparison failure -> common-receiver whole-station comparison -> same-signal RX station diagnosis -> controlled common-antenna chain check -> same-receiver simultaneous TX model and systematic limits -> database/tool prior art -> Benchmark-first integrated contributions with explicit non-priority boundary.
DE: Zweck der Methoden -> begrenzte Quellenübersicht -> Wert und Auswahl der Datenbankmeldungen -> Aktivitätsprüfung vor Deutung fehlender Meldungen -> Fehler langsamer Vergleichsblöcke -> vollständige Stationen am gemeinsamen Empfänger -> RX-Stationsdiagnose mit gleichem Signal -> Prüfung beider Ketten an gemeinsamer Antenne -> simultanes TX-Modell und systematische Grenzen -> Vorarbeiten bei Datenbanken/Werkzeugen -> Benchmark zuerst, Integration ohne Prioritätsanspruch.
No intentional scientific divergence. Source quotations/publication titles retained in original language.


## Review record: science

Chapter 7 review and staged revision — 2026-10-03

Scope and source model
----------------------
Owned scope: <a id="sec-7"></a> through immediately before <a id="sec-8"></a>, both languages. Accepted source model: parallel/co-authored EN and DE. The full source copies in drafts/science_en.py and drafts/science_de.py contain changes ONLY within that scope. Root integrates them and owns tests, README synchronization, full-manual integration and rendered QA. No repository file was edited by this agent.

Accepted baseline SHA256:
EN 574cc1b41fa2b15a1d76b6ec97db59f4fc51f20295816c67110f867611c2d999
DE 09110629042cb4fabecd163ef6b9ebe8e698148cc1e9f91718691a82be2aa319
Final hashes, section word counts and totals are machine-recorded in science_metadata.json.

Review result
-------------
The scientific construction is substantially sound: exact peer identity, the union Performance denominator, strongest-report versus local-median consolidation, conditional SNR, station-balanced Benchmark medians, explicit one-sided outcomes and descriptive uncertainty boundaries all match the reviewed implementation. The chief accessibility problem was that readers had to infer the radio meaning from notation and long uninterrupted specification paragraphs. The revision brings the practical question before the formal definition, explains operators/denominators/units, and adds four small examples addressing actual interpretation traps. The existing Benchmark weighting example is retained unchanged numerically.

Confirmed technical corrections/clarifications
---------------------------------------------
1. Power normalization is used in both RX and TX, not just TX analysis. Source: core/opportunity_engine.py:244-285 shares snr-power+30 across both roles; core/analysis_runner.py:205,410-411 covers RX Benchmark and shared normalized/corrected endpoint expressions. The formula was already correct and remains unchanged. The text now distinguishes re-expressing successful measured levels from recreating decodes at another transmit power. Positive Reference correction still lowers Target-minus-Reference ΔSNR.
2. The five-value IQR threshold is temporal, not a rule for every IQR. ui/plots/evidence_figures.py:62,1364-1388 requires five temporal contributors. ui/plots/opportunity_figures.py:494-521 uses IQR for >=3 peer medians, min-max for two, one point for one in distance profiles. Section7.8.5 now limits the five-value statement and links7.8.1.
3. The detector's0.5dB scale is a zero-spread fallback, not a universal floor. ui/inspector/outlier_candidates.py:875-898 returns every positive MAD or half-IQR unchanged; only both zero yields0.5dB. The existing piecewise equation was correct. Prose now agrees with it and explicitly permits smaller positive scales.
4. Performance folded SNR gives one value to each peer/date/hour combination. It does not equalize total peer weights or total date weights across the full fold. ui/plots/opportunity_figures.py:1664-1685 takes those medians and then directly summarizes their combined hourly population. The revised wording limits raw-row protection to its actual level and states the remaining weighting. Folded Decode Rate has a different construction and remains separately documented.
5. Reach is not necessarily monotonic across reruns of different duration. With a fixed eligible peer set and retained earlier evidence, additional observations cannot remove an earlier success. Changing minimum-count eligibility, peer membership or exclusions can change the denominator and lower the reported percentage. The text replaces the unqualified duration tendency with this exact distinction. Sources: core/opportunity_engine.py:447-448,518-530,575-576; ui/plots/opportunity_figures.py:407-429.
6. Absence of a Target-activity witness is not diagnosed downtime.7.3 now distinguishes unobserved participation from actual downtime. The gate remains observational and asymmetric.
7. There is a material current activity-source asymmetry between Performance and Benchmark. Performance establishes global Target-active cycles before special-peer exclusions; moving-peer exclusion follows retrieval. Benchmark excludes special peers in both source branches and moving peers before establishing its Target-active cycles. Sources: core/opportunity_engine.py:244-294; core/analysis_runner.py:448-455,675-686,718-735. Existing test: tests/regression/test_opportunity_engine.py:869-926. Both apply geographic scope afterward. A Target decode involving only an excluded peer can establish Performance activity supporting a Miss for another eligible peer, while the comparable Benchmark cycle has no surviving activity witness.7.3 now states this difference in domain language. Whether the modes should adopt one shared activity policy remains a separate runtime/scientific decision; no runtime change was made, and no new contamination claim is inferred.
8. QRP Labs Ref19 establishes a hash-misassociation mechanism, not its general prevalence. Removed the unsourced general adjective“rare”; preserved the mechanism, size/isolation caveat, population-specific review and causal limitations. Replaced median reassurance derived from a large row count with a conditional statement requiring an affected-population check. This is a precision improvement, not a claim that the underlying median algorithm is faulty.

Section-by-section review and reverse outlines
----------------------------------------------
7 introductory scope
EN: Benchmark and Performance questions -> five scientific levels -> Benchmark-first method matrix -> notation -> descriptive-statistic boundary.
DE: Benchmark-/Performance-Fragen -> fünf wissenschaftliche Ebenen -> Benchmark zuerst in Methodenmatrix -> Notation -> Grenze deskriptiver Kennzahlen.
Disposition: moved the existing orientation ahead of the symbol table; all rows retained. Added a short interpretation of indices, sums and even-count medians. Added the EN explicit sampling/dependence model boundary to DE, where the original described broader physical/population limitations but not that model. No new inferential promise.

7.1 data, units, time
EN: one database/run -> spot and cycle -> extended-message construction -> same-cycle units and matching -> history/data-quality boundary.
DE: eine Datenbank/Lauf -> Spot/Zyklus -> erweiterte Nachrichten -> kleinste Einheit und Zuordnung -> historische Auswahl/Datenqualität.
Disposition: retained one-source provenance, two-minute cycles, full peer matching, separate message cycles, no inferred missing side. Accepted relocation from Chapter0 owner: baseline paragraph beginning“Extended WSPR can instead convey...” /“Erweitertes WSPR kann stattdessen...” now has its complete home here, with Ref12. Only connective“instead” and database terminology adjusted. DE's useful explanation that both message phases are not a precondition is now explicit in EN7.1; DE retains that point in7.2. Historical fallback wording now clearly says it relaxes the code=1 requirement, without altering the pre-2022/empty-Target conditions.

7.2 identity and consolidation
EN: exact identity table -> grid4 selection/full-QTH geometry -> reported fields -> strongest normalized observation and its bias -> WsprDaemon precedent -> local-median exception -> changing identity limits.
DE: exakte Identitätstabelle -> Grid4/volle QTH-Geometrie -> gemeldete Felder -> stärkstes normiertes SNR und Asymmetrie -> WsprDaemon-Praxis -> lokale Median-Ausnahme -> Locatorgrenzen.
Disposition: substance already strong; retained all identity/consolidation distinctions and best-report caveats. EN explicitly disclaimed hash reconstruction; DE now does so too. Code: core/analysis_runner.py:83-108,152,205; core/opportunity_engine.py:244-285. A peer identity remains callsign plus FULL reported locator, including separate subsquares within grid4. No scientific grouping changed.

7.3 activity and eligibility
EN: ambiguous silent cycle -> activity indicator -> observed-population condition -> Reference asymmetry -> Joint/one-sided consequences -> global geographic witness -> mode-specific exclusion order.
DE: mehrdeutiger stiller Zyklus -> Aktivitätsindikator -> bedingte Population -> Referenzasymmetrie -> Joint/einseitige Folgen -> globaler Zeuge -> designspezifische Ausschlussreihenfolge.
Disposition: added actual ambiguity and actual current exclusion-order difference. No fabricated baseline/no downtime diagnosis. See confirmed findings6-7.

7.4 Performance
EN: conditional question/denominator -> success/opportunity/Miss rules -> RX/TX endpoint roles -> provenance truth table -> per-peer counts/rate -> equal-peer/pooled rates -> numerical comparison -> Reach -> successful-SNR selection and limits.
DE: bedingte Frage/Nenner -> Erfolg/Gelegenheit/Miss -> RX-/TX-Endpunkte -> Herkunftstabelle -> Peer-Anzahlen/Rate -> Peer-/Gelegenheitsgewichtung -> Zahlenbeispiel -> Reichweite -> SNR-Selektion/Grenzen.
Disposition: retained complete union classification and truth table. Explained Boolean symbols and peer-count denominator. New example: A90/100 and B5/10, already qualifying, gives70% equal-peer and95/110=86.4% pooled;95successes+15Misses=110opportunities; Reach100%. DE now explicitly preserves EN's one-success/many-success peer counting distinction. SNR evidence sentence now points to later view-specific grouping/weighting, avoiding any impression that every summary pools raw successes identically.

7.5 normalization and correction
EN: recorded SNR/power units -> common30dBm reference in both directions -> existing normalization example -> correction equation -> Joint subtraction -> sign example -> physical-calibration boundary.
DE: SNR-/Leistungseinheiten -> gemeinsamer30dBm-Bezug RX/TX -> bestehendes Normierungsbeispiel -> Korrekturgleichung -> Joint-Differenz -> Vorzeichenbeispiel -> Kalibriergrenze.
Disposition: three display equations unchanged. New sign example -10−(-12)=+2; Reference+1.5makes-10.5andΔSNR+0.5. Preserved cancellation of a COMMON reported TX-power term in same-transmitter RX, and different-signal TX exposure to reported power/chain errors. Normalization does not change outcomes.

7.6 pairing and missingness
EN: two Benchmark evidence questions -> Joint selection -> hash-resolution caveats/preflight -> no invented missing SNR -> asynchronous category -> Performance versus Benchmark selection.
DE: zwei Benchmark-Fragen -> Joint-Selektion -> keine erfundenen Werte -> asynchrone Kategorie -> Hash-Auflösung/Vorprüfung -> zwei Selektionsarten.
Disposition: order can differ locally without changing argument. DE uniquely had unresolved hash and affected-field details; EN now includes them. EN uniquely required AppendixB preflight and warned about a narrow segment; DE now does too. Both contain large-data/isolation qualification rather than automatic assurance.

7.7 aggregation
EN: Performance hierarchy -> Benchmark hierarchy/formulas -> existing three-peer example -> exact identity/support -> neighborhood construction/asymmetric consolidation -> minimum-contributor boundary -> membership example -> robustness limits.
DE: Performance-Hierarchie -> Benchmark-Hierarchie/Formeln -> bestehendes Drei-Peer-Beispiel -> Identität/Stützung -> lokaler Aufbau/asymmetrische Konsolidierung -> Beitragsminimum -> Zusammensetzungsbeispiel -> Robustheitsgrenzen.
Disposition: existing Benchmark numeric table retained: stationmedian-1 versus pooled+6; existing JO31AA/JO31AB support2 example retained. New local example -18,-12,-6=>median-12; absent-6=>median-15; fixedTarget-10 gives+2then+5. Demonstrates changing Reference composition, not a Target change. No minimum-neighborhood-size guarantee added. Code: core/compare_engine.py:68-95,142-156; core/analysis_runner.py:83-108.

7.8.1 geography
EN/DE: retained population -> deterministic distance bins -> four Performance summaries -> spread support -> locator limits -> Benchmark identity medians versus paired distribution.
Disposition: all detail retained; DE's existing useful paired-versus-peer question translated into EN. Three-peer IQR support stays here as authoritative.

7.8.2 Benchmark coverage
EN/DE: pairability question -> three-outcome denominator -> per-peer split vote -> equal-peer versus pooled Joint share -> absent-peer rule -> asymmetry.
Disposition: added question/denominator before formulas; explicitly exclude zero-evidence peers from division and explain one split vote. Both languages now translate the averaging/pooling arithmetic. Preserved not-a-win-rate and no one-sidedΔSNR boundary.

7.8.3 chronological and folded time
EN/DE: actual sequence versus recurring hour -> available resolution -> path-relative successful-SNR baseline -> anomaly formula -> chronological versus peer/date/hour aggregation -> opportunity support -> folded denominators -> represented-date boundaries -> Benchmark paired/one-sided coverage.
Disposition: added path-relative meaning before formula; aligned EN with DE's useful chronological/folded questions; precisely bounded folded weighting. Kept full-run≥3success requirement, represented-date denominator, zero versus missing distinctions, partial-hour unweighted exposure and≥2dates rule. Kept different Benchmark weighting and full selected window when no pairs survive. Sources: opportunity_figures.py:1155-1190,1249-1396,1428-1485,1650-1685.

7.8.4 selected path
EN/DE: exact selected identity -> Performance quantities/single-peer equality -> Benchmark quantities -> native focused evidence versus provider rows -> completed detector model -> qualifying stars -> padded episode interval -> local diagnostic guides -> presentation-only state.
Disposition: no scientific detail removed; divided the giant outlier-focus paragraph at distinct concepts. Replaced private AnalysisContext identifier with“completed analysis context”/“abgeschlossener Analysekontext”; all its actual invariance claims remain. No new UI design constraint added.

7.8.5 spread and transforms
EN/DE: middle-half versus full range -> temporal support rule -> what density/axis spacing mean -> exact correction-aware density grid -> numerical assignment -> relative normalization formula -> nonlinear median-focused axis -> linear Performance axis.
Disposition: corrected IQR scope; added brief reading meaning before retaining full reproducibility mathematics, membership resolution/ties, shifted grid, density count invariance,0.05dB edge effect, anchored axis and bar-length warning. None of the technical transform policy was silently dropped. Exact half-open CELL membership is scientific binning and remains; this is distinct from the prohibited query-window narration in AGENTS.

7.9 geography and solar filters
EN/DE: distance/projection -> locator precision -> maximum-distance population -> global integrity/activity ordering -> solar state at Target -> source-row limitations cross-reference.
Disposition: retained existing mechanics; added that Target solar elevation does not classify illumination along the entire path or at remote endpoints. This follows directly from Target-QTH-only input and avoids an overinterpretation. Sources: core/analysis_runner.py:619-638,667-673,706-715.

7.10 dependence and uncertainty
EN/DE: exact within-run calculation versus uncertain generalization -> clustered observations/extended phases -> balancing/robustness limits -> no automatic inference -> five evidence-support levels -> consistency versus replication -> dated validation provenance.
Disposition: aligned EN with DE's helpful opening distinction, kept no-CI/no-p-value/no-causal estimate claims. Added that alternative views of the SAME run are internal consistency, not independent replication. Preserved controlled separate-run requirement and linked Chapter8 reporting. Existing observation count is not independent sample size remains prominent.

7.11 native event detector
EN/DE: three practical tasks and terms -> local notation/control symbols/tolerance -> native evidence -> flank baseline -> centered robust spread -> residual/score with numeric sign example -> cadence-aware pilot grouping -> candidate-excluded refits -> all event gates -> rescue/strong anchors -> classes/cross-path context -> noncausal deterministic diagnostic boundary.
Disposition: every existing formula and threshold preserved. Added scale/score units and intuitive terms, explained sign-agreement denominator including neutral bridges, corrected zero-spread fallback wording, and specified median of retained cadence intervals (previous wording omitted the exact statistic). New example+8baseline/+1observed gives-7residual, robustscale1=>z-4.7215≈-4.72; explicitly insufficient alone to report an event. Preserved exclusion flanks, neutral bridging, unsupported evidence, three refits, rescue on unchanged baseline,0.01dB tolerance only at dB gates, no z tolerance, trimmed requalification, descriptive class thresholds, marker versus true peak, no duration bonus, no independence/multiple-testing claims. Sources: ui/inspector/outlier_candidates.py:38-56,875-905,948-974,1098-1137,1430-1485; config/delta_snr_outlier.py:10-39.

Cross-language differences and disposition
------------------------------------------
No conflicting scientific formulas were found between the accepted Chapter7 versions. Most differences were intentional explanatory localization or ordering. Material one-language-only details were reconciled as recorded above: EN sampling/dependence-model condition, DE both-phase-not-required clarification, EN no hash reconstruction, DE missing-pair interpretation, DE corruption checks/fields, EN AppendixB requirement/narrow-segment caveat, EN Reach counting, DE geographic and temporal reading questions, DE split-vote explanation, DE uncertainty introductory interpretation. All new numerical examples, caveats and current-runtime clarifications exist in both languages. Decimal punctuation in ordinary German prose is localized; code/formula literals retain periods. Visible localized detector labels were preserved.

User terminology and preservation
---------------------------------
Query-source narrative uses database/Datenbank; this scope contains no official publication title requiring the old archive term. Narrative metric naming is ΔSNR while formal math spans preserve their exact original notation. Formal paired-unit terminology remains where construction or conditioning is defined; Joint Spot is used for the resulting familiar evidence unit. No display equation was changed, added, removed or reordered. All17section anchors and inbound section destinations remain. No unique scientific mechanics were removed. The sole non-scientific identifier replacement is AnalysisContext -> completed analysis context; its meaning remains. The extended-message transfer from Chapter0 is explicitly coordinated with operator_review, which removes its duplicate there and retains practical links.

External source checks, accessed2026-10-03
-----------------------------------------
https://www.arrl.org/wspr — official technical overview confirms2500Hz reference SNR bandwidth, reported power units and even-minute protocol timing. ExistingRef8 retained.
https://wsjt.sourceforge.io/wsjtx-main_en.html — official user guide searchable content, section20.2.8, confirms Type2 compound call/no locator and Type3 15-bit hash/6-character locator/power. Direct open transiently failed; official-domain indexed text provided the exact technical description. ExistingRef12 retained. No new timing/firmware claim made.
https://wsprdaemon.readthedocs.io/en/master/FAQ.html#how-does-spot-merging-work-with-multiple-receivers — official FAQ confirms best-SNR reporting when merging multiple receivers. ExistingRef11 retained, bounded as a precedent rather than proof of physical intended-signal correctness.
https://qrp-labs.com/qmxp/wsprcorruption.html — manufacturer technical investigation demonstrates hash-collision identity/locator/power misassociation and an observed case. Does not estimate universal incidence. ExistingRef19 retained; wording was narrowed accordingly.
https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm — NIST engineering statistics handbook confirms conventional0.6745 modified-z scaling and the distinction between labeling candidates and formal outlier tests. Used to fact-check existing scaling prose, not to import its3.5threshold or its distributional assumptions into WSPRadar. No new numbered reference required for an unchanged pre-existing claim; root may choose to add one in the literature section later.

Validation and remaining limits
--------------------------------
Staging script revise_science.py asserts exact original byte preservation before sec-7 and from sec-8 onward, all17anchors unchanged and all30display-equation strings unchanged; both full source copies parse with ast.parse. Script uses CRLF matching the accepted source and writes only workspace files. Pure arithmetic checks cover all numerical examples. No pytest or repository-mutating command was run for this subtask. Root owns rendering verification, final table widths/glyphs/formula rendering and regression tests.

Word counts count whitespace-separated tokens after removal of HTML tags; equations and Markdown table tokens remain in this reproducible measure. Baseline EN8069/DE8191; staged totals and per-section counts in science_metadata.json (currently approximately9541/9568, plus18.2%/16.8%). The increase is chiefly four concise worked interpretation examples, meaning-first explanations, previously missing bilingual detail, and honest current-runtime gate clarification. The formal scientific content was retained rather than compressed.

Open further-method work, not implemented here: decide whether Performance and Benchmark should share one activity-witness policy; validate historical mode-relaxed data against known mode semantics without asserting contamination from fallback alone; quantify detector sensitivity/false candidates on named datasets if calibrated performance claims are ever desired. Current manual accurately limits the detector to deterministic descriptive classification.

Independent review follow-up
----------------------------
Added two precision sentences in both staged sources at root's request after independent review: (1) Section 7.11 now explicitly interprets the braces/union as pooled evidence samples that retain duplicate cell residual values, matching concatenation in outlier_candidates.py:1441-1446; the existing formula remains byte-identical. (2) Section 7.8.5's list of possible IQR contributors now also names individual successful normalized Target-SNR observations, which supply selected-path chronological Performance plots. All prior preservation and arithmetic assertions passed again; current word totals and hashes are in science_metadata.json.


## Independent review: science-cross-review-operations.txt

Independent Chapter 7 cross-review — operations reviewer — 2026-10-03

Reviewed staged science_en.py/science_de.py changes, with closer reading of activity conditioning, Performance classification/weighting, power normalization/correction, temporal summaries/spread, and detector construction.

Two actionable precision findings sent to parent:
1. §7.11 uses ordinary set-union notation for the variability sample V, while outlier_candidates.py concatenates the centered flank samples and retains repeated values. Add an explicit multiplicity/pooled-sample convention if the existing formula is preserved. This is a pre-existing notation issue, not an introduced detector change.
2. §7.8.5's contributing-value examples omit individual successful normalized Target-SNR observations in the selected-path Performance chronological view (described correctly in §7.8.4). Add this value type in both languages alongside Joint Spots, peer-bin medians and peer-date-hour medians. The five-value temporal IQR threshold versus three-peer distance rule is otherwise clear.

No other material discrepancy found in the reviewed additions. The Performance example is arithmetically correct: 70% station-balanced, 95/110 = 86.36% pooled, 95 successes +15 Misses. The power example is -15-20+30=-5 dB. The Reference correction example moves +2 to +0.5 dB. The detector example gives residual -7 dB and modified score -4.7215 at scale1. Both languages preserve the conditioned denominator, missing-SNR boundary, declared weighting, observational interpretation, and separate-repeat requirement. The zero-spread 0.5 dB replacement is correctly distinguished from a general floor. German new explanatory prose has matching meaning and is understandable technical German.

Visual review of the generated final PDFs, initial inspected rendering:
EN pages41–48 and65–81; DE pages49–56 and81–97 were inspected through contact sheets; EN45/71 andDE56/86/94 were inspected individually at full image resolution.

Actionable rendering findings sent to parent:
- EN71 andDE86: public contract table long exact identifiers overlap the Meaning column (outlier CSV names and correction metadata). Needs identifier wrapping or width allocation.
- DE56: method matrix long design labels and Hauptzusammenfassung header overlap adjacent cells. EN45 is readable at current8pt and does not overlap. Wrap German labels/header; retain readable font size.
- DE94→95: transmitterB replacement lead remains at bottom94 while its code block begins95. Keep the lead with its code block where feasible.

Remaining inspected pages: no clipping, missing glyphs, lost repeated table headers or isolated section headings found. Intentional new-appendix page starts leave white space at prior section ends; no hidden content inferred. Ref12 visually includes the new Virtual U3S manual link in the integrated parent PDF. Await parent rerender before confirming the three layout repairs.


## Independent review: independent_operator_pdf_review.txt

Independent operator/text and early-PDF review — 2026-10-03

Text scope: operator_en.py and operator_de.py Chapters 0, 1, 3 and 8. Read-only review after author handoff.

No substantive technical or meaning-parity defect found. Performance wording correctly separates the mean of individual peer rates from pooled opportunities. Joint-only signal comparison remains paired with one-sided outcome reporting. Fixed, independent and neighborhood Reference meanings remain distinct. Recurrence, internal consistency, controlled repetition and causal attribution are properly separated. Export configuration versus retained data, conditional files, native evidence and original-package provenance are consistent between languages.

Two minor language corrections reported to root:
- German Section 8.3: “Korrekturen im Quelldatenbank” must be “Korrekturen in der Quelldatenbank”.
- German preface: “zwei Stunden auseinanderliegende QSOs” narrows English “two contacts made hours apart” to exactly two hours. A neutral wording such as “zwei zeitlich weit auseinanderliegende QSOs” preserves the intended comparison.

PDF inspection scope: rendered 81-page EN and 97-page DE version, contact sheets generated around 19:04 local file time. Reviewed every EN page 1–40 and DE page 1–48 on contact sheets. Detailed single-page inspection: EN 3, 11, 21; DE 4, 5, 28, 31. These were selected to inspect the densest matrices, guide labels, action table, pagination and a suspected overlap.

Required correction:
- DE page 31, Chapter 4 control-class table: “Ansichtsbedienelemente” overruns the first column and visibly overlaps “Verändern” in the next cell. A deliberate line break or fitted column width is needed.

Useful pagination/layout improvements:
- DE page 28 ends with “Wenn das Ergebnis eine wichtige Stationsentscheidung stützen soll:” while its list starts page 29. Keep that short lead-in with the first list item.
- DE Section 0.1 matrix spans pages 4–7, with only one row and substantial bottom whitespace on page 5. The equivalent English matrix uses the dedicated compact layout and wider example column on pages 3–4. Baseline docs__pdf_generator.py:725 recognizes only the English header triple (“Analysis”, “Question”, “Practical examples”), while German uses (“Analyse”, “Fragestellung”, “Praktische Beispiele”). Exact German recognition should use the intended introductory-table treatment without changing other tables. This is inefficient pagination, not missing content.
- Minor widow: DE page 14 starts with the last word “eingeführt.” from the preceding Chapter 1 paragraph. No section heading is stranded there.

Otherwise: no clipped tables, missing Δ/arrow glyphs, orphan section headings or footer collisions found in the inspected range. Continuation tables repeat headers. Chapter 2 guide tables preserve actual figure labels with readable wrapping, and the action introduction stays with the action table (EN page 21, DE page 26). Ordinary paragraph/list continuations across pages are present and generally sensible. Full scientific-method pages after this range are owned by root's separate visual review. Any subsequent pagination change needs targeted rerender verification; page numbers above refer only to the inspected 81/97-page version.


## Integration dispositions

The independent review clarified the detector sample notation as pooling with multiplicity and explicitly included individual successful selected-path SNR observations in temporal spread. The German source-database grammatical error was repaired; the introductory two-hour example was aligned with the English non-specific separation. Chapter 6 now distinguishes Zander's own accuracy wording from our narrower interpretation of the numerical precision argument, and translates bottomside without suggesting the lower ionospheric layers.

Ref-12 retains the older version-matched operating manual and adds the verified dedicated Virtual U3S 1_04_008a guide, accessed 2026-10-03. Existing reference anchors and order are retained.

PDF inspection identified and repaired undersized scientific-matrix text, a German introductory-table selector omission, long German labels and code identifiers overlapping columns, missing continuation headers, and stranded short list/code introductions. The renderer changes affect presentation only. The authoritative Markdown, exact public identifiers and scientific formulas remain intact.

The preface is shorter, but the whole manual is approximately six percent longer: worked scientific interpretation and technical corrections were retained rather than hiding their conditions. Runtime scientific algorithms are unchanged. Live provider completeness, physical station setups and detector error rates were not validated by this documentation change.

## Final verification, 2026-10-03

- Final documentation/PDF checks: 127 passed.
- Complete canonical regression run: 3,467 passed, 3 xfailed, 3 pre-existing failures in 535.97 seconds. The two Guided introductory-SNR markup assertions and one navigation JSON assertion expecting no panelKey were already failing before this work; their test files and UI sources remain unchanged.
- Seven reference PDFs checked; README exactly regenerated from DOC_EN; Python source syntax and Git whitespace checks passed.
- Each language retains 146 unique anchors with valid internal links and all 30 original display equations.
- Final PDFs: 81 English pages, 93 German pages. All-page contact-sheet review plus detailed scientific/table checks completed; identified overlaps and orphan introductions repaired and rechecked. Final rendered source and artifact hashes agree.
- Scientific runtime algorithms unchanged. Live-provider completeness, physical RF setups and empirical outlier error rates remain outside this documentation verification.
