# docs/doc_en.py

"""Authoritative English end-user and scientific manual for WSPRadar."""

DOC_EN = r"""
---

<a id="sec-1"></a>

### 0. Start Here

<a id="sec-1-0"></a>

#### 0.0 What WSPRadar can show

WSPRadar shows how a complete station or setup performs under real operating conditions—on its own and against a meaningful reference. A <strong class="defined-term">Hardware A/B Test</strong> compares two controlled local paths, such as antennas, feedlines or receive chains. A <strong class="defined-term">Reference Station / Buddy Test</strong> compares two complete stations, including their locations, equipment and noise environments.

The station or setup being evaluated is the <strong class="defined-term">Target</strong>. Its comparison baseline is the <strong class="defined-term">Reference</strong>. Depending on the experiment, the Reference can be Setup B at the same station, one known external station, the active local WSPR neighborhood or its strongest active member.

These comparisons answer the practical question: **How did the station or setup I am testing perform on its own or relative to a meaningful Reference? Where, when and by how much did it differ?** The result can show an observed advantage and where it appeared. Laboratory quantities such as isolated antenna gain, efficiency or receiver sensitivity still require separate calibrated measurements.

The method builds on peer-reviewed research and established technical experiments: same-receiver TX comparisons under shared propagation conditions, conditioned simultaneous RX comparisons, and independent activity checks for stations whose operating schedules are unknown <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-3">[Ref-3]</a>. WSPRadar builds on that foundation and extends it substantially. It adds Target-activity qualification, several purpose-built benchmark designs, cycle- and schedule-based matching, reported-power normalization, separate Success, Delta SNR and Decode Outcomes, station-balanced geographic summaries, and drill-down to the contributing evidence. Together, these capabilities form an integrated experiment and audit workflow for complete installed stations - well beyond a spot-count comparison or a single A/B calculation. [Chapter 6](#sec-d) documents the scientific lineage, WSPRadar's extensions and their boundaries.

<a id="sec-1-1"></a>

#### 0.1 WSPR in 2 Minutes

<strong class="defined-term">WSPR</strong> stands for **Weak Signal Propagation Reporter**. Joe Taylor, K1JT, and Bruce Walker, W1BW, described it as a worldwide network of low-power stations exchanging beacon-like transmissions to probe possible propagation paths. A WSPR-2 transmission lasts just under two minutes and occupies about 6 Hz. Its message normally contains a callsign, a four-character Maidenhead locator and reported power in dBm; `30 dBm` is `1 W`. It can be decoded at about `-28 dB` signal-to-noise ratio (SNR) in a 2500 Hz reference bandwidth <a href="#ref-4">[Ref-4]</a>. A less negative SNR means a stronger signal relative to noise.

When reporting is enabled, a receiver uploads each successful decode as a <strong class="defined-term">spot</strong>. A spot records transmitter and receiver identity, reported location, time, band, power and decoder-reported SNR. WSPRadar uses wspr.live as its primary WSPR data source, with WSPRDaemon WD2 and WD1 as fallback sources. wspr.live is a public ClickHouse database that stores WSPRnet-reported spots and checks for new reports every few minutes. A daily synchronization fills reports that were missed or uploaded late <a href="#ref-5">[Ref-5]</a>.

One limitation matters for every analysis: the archive contains successful decodes, not a complete log of every attempted transmission. WSPRadar therefore constructs an <strong class="defined-term">opportunity</strong>: a Target-active two-minute cycle with independent evidence that the relevant remote transmitter or receiver was active. In RX, another receiver must have decoded the same transmitter; in TX, the remote receiver must have decoded another signal on the same band. Without that supporting activity, a missing spot is not automatically counted as a radio failure.

<a id="sec-1-2"></a>

#### 0.2 Choose the question you want to answer

Start with the operating question. The matching design follows directly:

| Your question | Choose |
|---|---|
| Where is my transmitter decoded among receivers shown to be active? | TX Analysis with `No benchmark (Success only)` |
| Which independently confirmed signals does my receiver also decode? | RX Analysis with `No benchmark (Success only)` |
| Did local antenna, feedline or hardware path A differ from path B? | Hardware A/B Test |
| How does my complete station compare with one known station? | Reference Station / Buddy Test |
| Am I broadly typical for nearby active WSPR stations? | Local Neighborhood Benchmark with Local Median Neighborhood |
| How do I compare with the strongest active local peer on each path and cycle? | Local Neighborhood Benchmark with Local Best Station |

Choose <strong class="defined-term">TX (transmit) Analysis</strong> when the Target callsign is transmitting. The remote receiving stations that supply evidence become the mapped <strong class="defined-term">peers</strong>.

Choose <strong class="defined-term">RX (receive) Analysis</strong> when the Target callsign is receiving. The remote transmitting stations that supply evidence become the mapped peers. The configured <strong class="defined-term">QTH</strong> is the Target station location used as the map center and local-radius origin.

Once the question is chosen, WSPRadar helps in four practical ways:

* **Use the right experiment:** choose Target reach, a controlled local Hardware A/B Test, a complete-station Buddy Test or a local-neighborhood comparison instead of relying on raw spot totals.
* **Compare like with like:** WSPRadar first checks that the Target was observably active, then compares the same two-minute <strong class="defined-term">WSPR cycle</strong> or deterministic scheduled TX pairs. Where transmitted powers differ, it places decoded SNR on the same reported-power basis.
* **Keep different performance questions separate:** <strong class="defined-term">Success</strong> shows conditional Target reach among independently confirmed opportunities. <strong class="defined-term">Delta SNR</strong> shows the Target-minus-Reference signal difference when both sides produced comparable decoded evidence. <strong class="defined-term">Decode Outcomes</strong> show joint evidence and cases where only one side was decoded.
* **Find and verify the pattern:** maps and inspectors show where a difference appears by distance, direction, UTC and day/night/greyline conditions. You can see whether the pattern is broad or based on little evidence, then inspect the contributing stations and underlying spots.

Repeated runs can validate an antenna, feedline or receiver-chain change. Comparable TX and RX runs can also investigate the familiar amateur-radio "alligator" pattern: a station decoded well but receiving poorly. Directional results describe the observed WSPR paths and station population, not a calibrated radiation pattern.

<a id="sec-1-3"></a>

#### 0.3 What one run produces

Every run has one <strong class="defined-term">Direction</strong>, one exact band, one Target identity and a resolved UTC window. Its <strong class="defined-term">Benchmark Design</strong> determines which results are produced:

* <strong class="defined-term">Success</strong> is the non-comparative Target result. Its conditional Success Rate shows how often the Target produced qualifying evidence among independently confirmed opportunities.
* <strong class="defined-term">Compare</strong> is added when a benchmark is selected. It reports paired **Delta SNR** and **Decode Outcomes**. Delta SNR is Target-side SNR minus Reference-side SNR after any configured Reference correction. Positive values favor the Target; negative values favor the Reference. Decode Outcomes show both paired evidence and cases where only one side was decoded.

Results open on a map and can be followed through one evidence path:

**Run identity -> Map -> Stations and Spots -> Segment Inspector -> Station Insights -> Drill-Down**

The map locates the effect. The Segment Inspector shows the evidence for a selected distance and direction. Station Insights shows which identities contribute. Drill-Down exposes the observations, same-cycle pairs or scheduled TX A/B pairs behind the summaries.

The aim is a clear operating conclusion: **what differed, where and when, relative to which Reference, by how much, and with how much supporting evidence.**

<a id="documentation-toc"></a>

### Table of Contents

**Part 0: Preface**

* [0. Start Here](#sec-1)
    * [0.0 What WSPRadar can show](#sec-1-0)
    * [0.1 WSPR in 2 Minutes](#sec-1-1)
    * [0.2 Choose the question you want to answer](#sec-1-2)
    * [0.3 What one run produces](#sec-1-3)

**Part I: Operator Guide**

* [1. Experiment Playbooks](#sec-2)
    * [1.1 A strong foundation for every experiment](#sec-2-1)
    * [1.2 Success only: explore Target reach](#sec-2-2)
    * [1.3 RX Hardware A/B: compare simultaneous receive paths](#sec-2-3)
    * [1.4 TX Hardware A/B: compare alternating transmit paths](#sec-2-4)
    * [1.5 Reference Station / Buddy Test](#sec-2-5)
    * [1.6 Local Median Neighborhood](#sec-2-6)
    * [1.7 Local Best Station](#sec-2-7)
* [2. Read Your Results](#sec-3)
    * [2.1 Read a Success result](#sec-3-2)
    * [2.2 Read a Compare result](#sec-3-3)
    * [2.3 Use the map to locate the effect](#sec-3-4)
    * [2.4 Check Stations and Spots](#sec-3-5)
    * [2.5a Inspect a Geographic Segment (Success Mode)](#sec-3-6a)
    * [2.5b Inspect a Geographic Segment (Compare Mode)](#sec-3-6b)
    * [2.6a Inspect the Contributing Stations (Success Mode)](#sec-3-7a)
    * [2.6b Inspect the Contributing Stations (Compare Mode)](#sec-3-7b)
    * [2.7 Verify the underlying evidence](#sec-3-8)
    * [2.8 Worked Compare example](#sec-3-9)
* [3. Strengthen and Communicate Your Result](#sec-4)
    * [3.1 Recognize broad and stable evidence](#sec-4-1)
    * [3.2 Strengthen a result through repetition and control](#sec-4-2)
    * [3.3 Write an evidence-matched conclusion](#sec-4-3)
    * [3.4 Preserve the run and its context](#sec-4-4)

**Part II: Controls and Troubleshooting**

* [4. Controls and Configuration](#sec-5)
    * [4.1 Workflow controls](#sec-5-1)
    * [4.2 Core controls](#sec-5-2)
    * [4.3 Benchmark controls](#sec-5-3)
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
    * [7.4 Success classification and formulas](#sec-7-4)
    * [7.5 Power normalization, correction and Delta SNR](#sec-7-5)
    * [7.6 Paired evidence and Decode Outcomes](#sec-7-6)
    * [7.7 Aggregation hierarchy](#sec-7-7)
    * [7.8 Stability, distributions and inspection-layer weighting](#sec-7-8)
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
* [Appendix B: Timed A/B Relay Switch](#sec-b)
* [Appendix C: Reference SNR Calibration](#sec-c)
* [License](#sec-license)

---

<a id="part-i"></a>

## Part I: Operator Guide

This part takes you from an operating question to a well-supported result. Use it to choose an analysis, set up the experiment, inspect the evidence and describe what WSPRadar found. Exact controls, processing methods and reproducibility details are collected in Parts II and III.

---

<a id="sec-2"></a>

### 1. Experiment Playbooks

Choose the playbook that matches the question in [Section 0.2](#sec-1-2). Each playbook describes the operating setup and the result it creates. Exact matching, normalization and aggregation are defined once in [Scientific Methods](#sec-7).

<a id="sec-2-1"></a>

#### 1.1 A strong foundation for every experiment

A clear question and a stable operating setup make the result easier to interpret.

**Define the run**

* State the question and the variable under test in one sentence.
* Choose TX or RX Analysis, one exact band and the Benchmark Design.
* Enter callsigns exactly as uploaded, including any valid `/P`, `/1` or `/QRP` suffix.
* Verify the Target QTH. Success identifies the Target using the exact callsign together with the first four locator characters.
* Select a UTC window in which the Target was actually operating. Use a window long enough to cover the propagation states named in the intended conclusion; multi-day runs are preferable when the conclusion spans complete daily cycles.
* Record the antennas, feedlines, tuner, transmitter or receiver, decoder, software version, power, schedule and intentional changes.

Every run uses one exact band; combining bands would mix different propagation, activity, station populations and observability.

**Keep the experiment stable**

* Keep every non-tested variable as stable as practical.
* Keep station clocks synchronized.
* For TX, keep actual and reported power synchronized and stable unless power itself is under test. WSPR is commonly operated at low power; `20-30 dBm` corresponds to approximately `0.1-1 W`.
* For RX, keep gain, filtering, audio routing, decoder settings and upload behavior stable unless one of those is the tested variable.
* Confirm that each benchmark side operates as intended. The <strong class="defined-term">Target-Active Gate</strong> protects periods without observable Target activity, but it does not prove Reference uptime.

Once the run completes, use the evidence ladder in [Chapter 2](#sec-3) to inspect its geographic breadth, observation volume and underlying rows.

<a id="sec-2-2"></a>

#### 1.2 Success only: explore Target reach

<strong class="defined-term">Qualifying evidence</strong> means the decoded WSPR observations retained after the run's identity, locator, band, UTC-window, Target-activity and filter rules, for peers and segments that also satisfy the configured evidence thresholds. For Success, this includes Target decodes and the independent same-cycle activity used to establish opportunities that are fair to count.

**Question answered**

Where, when and at what signal strength does the Target produce qualifying evidence among remote stations or signals independently shown to be active?

**What WSPRadar shows**

* **RX Success** compares Target receiver decodes with independently confirmed remote transmitter-cycles.
* **TX Success** compares Target transmitter decodes with remote receiver-cycles shown to contain other same-band activity.

There is no Reference station or Setup B.

**Set up the analysis**

Choose `RX Analysis` or `TX Analysis`, enter the exact Target callsign and QTH, choose one band and an active UTC window, then select `No benchmark (Success only)`.

**Strengthen the evidence**

Use an operating window with observable Target activity and enough independent WSPR activity. Check the geographic scope, Stations, Spots and time views. If only a few peers survive the selected filters or evidence thresholds, extend the run or broaden the evidence before drawing a wide conclusion.

**Evidence-matched conclusion**

> For this Target, band, UTC window and selected peer population, the displayed Success Rate summarizes the fraction of independently confirmed global WSPR-network opportunities in which the Target also produced qualifying evidence, calculated per peer and then balanced across qualifying peers.

In everyday station terms: among the worldwide WSPR activity that this run could independently verify and fairly test, the result shows how consistently your station also produced the expected TX or RX evidence.

Success describes conditional network reach. [Section 2.1](#sec-3-2) explains its classifications and weighting.

<a id="sec-2-3"></a>

#### 1.3 RX Hardware A/B: compare simultaneous receive paths

**Question answered**

Did two local receive paths differ while observing the same remote WSPR transmissions?

For a ham operator, this can mean comparing two antennas with one receiver and decoder path per antenna; comparing two receivers fed from the same antenna through a characterized splitter; comparing preamplifiers, filters or feedlines; or comparing two complete parallel receive chains. Keep everything outside the item under test as similar and stable as practical.

**What WSPRadar shows**

Simultaneous RX Hardware A/B compares two local receiving paths at one station. Setup A and Setup B observe the same remote transmitter identities in the same WSPR cycles. This is WSPRadar's closest design to a controlled same-signal hardware comparison.

**Set up the experiment**

Select the UI choice `Hardware A/B-Test (Local Setup)` and operate two receivers simultaneously with different exact reporting callsigns:

* Setup A uses the Target callsign.
* Setup B uses the `Setup B Callsign`.

Keep clocks, antenna routing, gain, audio paths, decoder settings and uploads controlled.

The run produces an RX Hardware Compare result and the Target's separate RX Success result.

**Strengthen the evidence**

Document splitter balance, feedline differences, receiver gain, automatic gain control (AGC) behavior, clipping, decoder configuration and upload behavior. Keep shared hardware genuinely common. A measured Reference SNR correction can compensate for a stable offset; it cannot correct nonlinear or time-varying behavior.

[Appendix A](#sec-a) describes parallel WSJT-X instances. [Appendix C](#sec-c) describes Reference SNR calibration.

**Evidence-matched conclusion**

> Under the documented simultaneous RX setup, paired Delta SNR showed the observed difference between receive paths A and B for the shared transmitters, cycles and geographic scope.

In everyday station terms: for remote signals that both paths observed at the same time, the result shows which receive path tended to produce stronger decodes, where that difference appeared and how much shared evidence supported it.

<a id="sec-2-4"></a>

#### 1.4 TX Hardware A/B: compare alternating transmit paths

**Question answered**

Did two local antennas, feedlines or switched RF paths differ when driven by one common station setup?

**What WSPRadar shows**

Sequential TX Hardware A/B alternates complete WSPR transmissions between Setup A and Setup B. The configured schedule identifies the two sides, and WSPRadar compares evidence from deterministic one-to-one scheduled pairs.

This design keeps one callsign and normally one transmitter chain. Target and Reference can be two minutes apart, but lower-duty-cycle schedules with a greater separation are also valid. Shorter separation limits the time available for propagation, interference and receiver conditions to change; it does not make a sequential comparison simultaneous.

**Set up the experiment**

The time-locked schedule, rather than callsign `/1` and `/2` suffixes, identifies the two paths.

Use the station's normal valid exact callsign for both paths. In `TX A/B Schedule`, enter the actual recurrence and UTC phase of each physical path:

* `Repeat Interval` is shared by Target and Reference. The available intervals are `4, 6, 10, 12, 20, 30` and `60 min`; each is an even WSPR-compatible divisor of one UTC hour.
* `Target Start` is the even UTC minute phase used by Setup A.
* `Reference Start` is the different even UTC minute phase used by Setup B.

The default is `Repeat Interval = 10 min`, `Target Start = 00 UTC` and `Reference Start = 02 UTC`. The preview then shows Target at `00, 10, 20, 30, 40, 50` and Reference at `02, 12, 22, 32, 42, 52`. WSPRadar keeps the starts disjoint and reports the cyclic separation and transmissions per hour. The repeat interval describes **each physical path's actual schedule**; it is not necessarily the `Frame` value shown by a transmitter that alternates one output between two paths.

Pairing is automatic. For each receiver `callsign + locator`, WSPRadar pairs every scheduled Target start one-to-one with the nearest scheduled Reference start. An exact half-interval tie uses the same lower/higher-phase pairing regardless of which path is called Target, so swapping A/B preserves the physical pairs and reverses only the Delta sign. Multiple retained observations on one side of one pair are reduced to a micro-median. A pair decoded on both sides contributes one Pair Delta; a one-sided decode remains Only Target or Only Reference; a pair with neither side decoded produces no row. A pair is excluded when either of its two planned starts falls outside the selected comparison window.

Use a deterministic scheduler or controller. Standard WSJT-X randomized transmit-percentage operation does not create the required fixed A/B sequence.

**Ultimate3S: adjacent A/B slots followed by a pause.** The QRP Labs Ultimate3S can run a sequence of WSPR entries and apply a per-entry `Aux` output to external path-switching hardware. When a two-entry sequence begins at `00`, a global 10-minute frame can therefore use Target at `00`, Reference at `02`, then pause until the next sequence at `10`; in WSPRadar this is `Repeat Interval = 10`, `Target Start = 00`, `Reference Start = 02`. The same arrangement with a 20-minute global frame gives each path a 20-minute recurrence while retaining two-minute A/B separation. The Ultimate3S manual documents `Start = 00` specially as "not used", so verify the displayed and observed UTC sequence and enter its actual phases rather than assuming a literal setting-to-time mapping. The `Aux` lines share display signals; use the documented filtered driver or relay interface and switch only in the RF-off interval <a href="#ref-6">[Ref-6]</a>.

**QMX: distinguish one-transmitter and two-transmitter schedules.** One QMX with `Frame = 10`, `Start = 0` transmits at `00, 10, 20, 30, 40, 50`. If an external switch alternates those transmissions between paths, Target is `00, 20, 40` and Reference is `10, 30, 50`; each path repeats every 20 minutes, so enter `Repeat Interval = 20`, `Target Start = 00`, `Reference Start = 10`. A single QMX cannot produce an adjacent `00/02` pair followed by an eight-minute pause with that beacon scheduler. It can alternate adjacent paths only by transmitting every two minutes, which the QMX manual discourages as antisocial network use. Two independently scheduled QMX units with `Frame = 10`, Starts `00` and `02`, do implement WSPRadar's `10 / 00 / 02` schedule, but their transmitter chains and actual powers must be controlled as separate hardware <a href="#ref-6">[Ref-6]</a>.

Do not encode path identity by reporting false values such as `30 dBm` for one path and `33 dBm` for the other. WSPRadar normalizes TX SNR as `SNR - reported power + 30`; an invented 3 dB report difference therefore creates an artificial 3 dB comparison offset. Time-locking identifies the paths. Report the actual power and use a measured Reference correction for a real, defensible path offset.

The physical schedule-to-path mapping determines which antenna or path is Target and which is Reference. Verify it without RF first. A reversed mapping labels the paths backwards and reverses the practical interpretation of the Delta SNR sign.

The run produces a sequential TX Hardware Compare result and a separate TX Success result. Success is limited to the configured Target schedule and therefore describes Setup A.

<a id="sec-2-4-why"></a>

**Why alternating transmissions are useful**

When two nearby antennas radiate the same WSPR waveform and callsign in the same cycle and frequency channel, a remote receiver observes their combined field. Its spot cannot identify how much came from antenna A or antenna B.

Distinguishable simultaneous signals normally require separate callsigns and transmit chains. That introduces transmitter calibration, power, timing and frequency differences; closely spaced antennas and feed systems can also couple or inject RF into the other chain.

Alternating complete scheduled transmissions retains one common transmitter chain and gives both paths repeated exposure to changing propagation and receiver conditions. Over a balanced run lasting many hours or days, short-term changes repeatedly affect both sides and tend to average down.

**Strengthen the evidence**

Control switch loss, feedline differences, antenna coupling, clock accuracy, schedule-to-path mapping and switching timing. Keep actual and reported power stable. Extend the run across the propagation periods relevant to the question, and reverse the A/B schedule assignments in a repeated experiment when a small difference matters.

Scheduled TX A/B remains sequential: Setup A and Setup B are observed at different times. Use the shortest practical separation, because a longer gap gives propagation, interference and receiver conditions more time to change. Reversed assignments and repeated balanced runs help reveal systematic timing or switching effects. [Section 6.3](#sec-d-toledo) gives the experimental lineage and explains why short alternation is preferable to long blocks <a href="#ref-7">[Ref-7]</a>.

[Appendix B](#sec-b) describes WSPRadar's timed USB-relay helper. [Appendix C](#sec-c) describes Reference SNR calibration.

**Evidence-matched conclusion**

> Under the documented time-locked schedule, scheduled-pair Delta SNR showed the observed difference between switched paths A and B for the selected receivers, times and geographic scope.

In everyday station terms: after repeatedly alternating the two RF paths, the result shows whether path A or B tended to produce stronger reports for the receivers and propagation periods represented in the run. [Why alternating transmissions are useful](#sec-2-4-why) and [Section 6.3](#sec-d-toledo) explain why this comparison is defensible while still remaining sequential rather than simultaneous.

<a id="sec-2-5"></a>

#### 1.5 Reference Station / Buddy Test

**Question answered**

How did the Target station compare with one known external station during overlapping operation?

**What WSPRadar shows**

A Buddy Test compares two complete installed station systems. The comparison includes their locations, antennas, feedlines, transmitters or receivers, local noise, terrain, software and operating environments.

* In TX, the same remote receiver compares Target and Reference where both were decoded in the same cycle.
* In RX, Target and Reference receivers compare the same remote transmitter identity in the same cycle.

Same-cycle pairing gives the two sides a shared endpoint and reduces many path, transmitter or receiver differences within each pair.

**Set up the analysis**

Select `Reference Station (Buddy Test)`. Enter one exact Target callsign and one different exact `Reference Callsign`. Choose a Reference whose location, hardware, reported power and operating schedule you understand.

Both stations need overlapping operation on the same band. Verify Reference uptime independently. Apply a Reference SNR correction only when its calibration basis is defensible.

The run produces a TX or RX Compare result against the buddy and a separate non-comparative Target Success result.

**Strengthen the evidence**

Document terrain, local noise, antennas, polarization, feedline loss, transmitter or receiver calibration, reported power and operating schedules for both stations. Check locator identity and collect enough shared remote peers.

The Target-Active Gate is asymmetric. Swapping Target and Reference can therefore change one-sided Decode Outcomes even when the sign of the shared paired Delta SNR reverses as expected.

A known Reference station is a meaningful comparison partner, not automatically a calibrated reference standard.

**Evidence-matched conclusion**

> For the shared paths and cycles in this run, paired Delta SNR and Decode Outcomes showed how the two complete installed stations compared under their respective operating environments.

In everyday station terms: this shows how your complete on-air station performed against your buddy's complete station on shared paths; it does not assign the observed difference to one antenna, receiver or location by itself.

<div style="page-break-before: always;"></div>

<a id="sec-2-6"></a>

#### 1.6 Local Median Neighborhood

**Question answered**

How does the Target compare with the typical active WSPR evidence from stations around its configured QTH?

**What WSPRadar shows**

Local Median Neighborhood forms a dynamic Reference from active station identities inside the selected radius. For each qualifying cycle and path, the neighborhood median represents the active local group without allowing one high-volume identity to dominate.

The Reference can change from cycle to cycle. It is a local activity benchmark rather than one fixed or calibrated station.

**Set up the analysis**

Select `Local Neighborhood Benchmark`, choose a radius from 10 to 250 km and choose `Local Median Neighborhood` under `Local Benchmark Method`.

Verify the Target callsign and QTH because they determine Target exclusion from the local pool and define the radius origin. Choose a radius with a clear local meaning and enough active station identities.

The run produces a Local Compare result and the Target's separate non-comparative Success result.

**Strengthen the evidence**

Inspect which local identities contribute, their evidence counts and how the result changes with radius. A smaller radius can describe a more similar local environment but may leave a fragile pool; a larger radius can provide more contributors while including different terrain, noise and station conditions.

Local stations can differ in antenna, hardware, schedule and reported-power accuracy. Report the selected radius, method, contributors and evidence counts with the result.

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

Select `Local Neighborhood Benchmark`, choose a radius from 10 to 250 km and choose `Local Best Station` under `Local Benchmark Method`.

Verify the Target callsign and QTH, then choose a radius that retains a meaningful and adequately populated local pool.

The run produces a Local Compare result and the Target's separate non-comparative Success result.

**Strengthen the evidence**

Inspect the local Reference contributors and repeat the analysis with scientifically defensible radii when the conclusion depends strongly on pool membership. Report the changing best-peer definition rather than describing the result as a comparison with one fixed station.

As with the median method, local contributors can differ in terrain, equipment, noise, schedule and reported-power accuracy.

**Evidence-matched conclusion**

> Relative to the strongest active local Reference selected for each qualifying path and cycle inside the stated radius, the Target showed the displayed paired Delta SNR and Decode Outcomes.

In everyday station terms: this shows how your station compared with the strongest qualifying nearby station available on each path and cycle, rather than with one permanently fixed competitor.

Exact local-pool membership and aggregation rules are in [Sections 7.2](#sec-7-2) and [7.7](#sec-7-7).

<a id="sec-3"></a>

### 2. Read Your Results

Read every run through the same evidence ladder:

**Map -> Stations and Spots -> Segment Inspector -> Station Insights -> Drill-Down**

* Confirm the result and run definition.
* Use the map to locate the effect.
* Select the relevant distance and direction for further inspection in Segment Inspector.
* Inspect station-level evidence in Station Insights.
* Drill down to observation-level evidence.

The exact formulas, matching rules and processing hierarchy are in [Scientific Methods](#sec-7).

<a id="sec-3-1"></a>

<a id="sec-3-2"></a>

#### 2.1 Read a Success result

Success is the non-comparative Target result. Think of Success Rate as <strong class="defined-term">conditional reach</strong> among independently confirmed opportunities:

* **RX Success:** of the remote transmitter-cycles independently confirmed by another receiver, how many did the Target receiver also decode?
* **TX Success:** of the active remote receiver-cycles confirmed by other same-band decodes, how many also decoded the Target transmitter?

WSPRadar uses four user-facing classifications:

* <strong class="defined-term">Target:</strong> the Target succeeded and the required independent confirmation also exists.
* <strong class="defined-term">Elsewhere:</strong> in RX, another receiver decoded the transmitter but the Target did not.
* <strong class="defined-term">Other Signals:</strong> in TX, the receiver decoded other same-band signals but did not decode the Target.
* <strong class="defined-term">Target-only:</strong> the Target was decoded without the independent confirmation required by the denominator. It remains available for audit but does not enter Success Rate.

For example, if a remote transmitter was independently confirmed in eight qualifying cycles and the Target receiver decoded it in three, that peer's RX Success Rate is `3 of 8 = 37.5%`. If an active receiver produced ten qualifying cycles and decoded the Target transmitter in four, its TX Success Rate is `4 of 10 = 40%`.

The candidate population is globally sourced:

* RX can grow toward the globally active transmitters on the band during cycles in which the Target receiver was active.
* TX can grow toward the globally active receivers on the band during Target transmit cycles.

Only peers surviving the selected time, band, filters and evidence thresholds contribute. The displayed map scope can show a geographic subset.

Each peer rate is calculated first. A Success map segment then gives every qualifying peer identity one equal vote and displays the arithmetic mean of those station rates. This is the <strong class="defined-term">station-balanced</strong> value. Segment Inspector also shows the <strong class="defined-term">observation-level</strong> pooled rate, which gives every qualifying observation equal weight.

Success Rate is not power-normalized. The successful Target SNR displayed beside it is normalized to reported 1 W.

A displayed `100%` means that the Target succeeded in every qualifying opportunity for the station or selected scope. It does not mean that every possible or scheduled transmission was decoded. Because Success measures a demanding, globally sourced opportunity population, its practical meaning comes from geography, Stations, Spots, time and repetition rather than proximity to `100%`.

<a id="sec-3-3"></a>

#### 2.2 Read a Compare result

Compare keeps two evidence questions separate.

**Delta SNR**

Delta SNR asks: when Target and Reference both produced comparable evidence, which side had the stronger SNR and by how much?

In the operator view, Delta SNR is the Target-side SNR minus the corrected Reference-side SNR. The exact equation and correction convention are in [Section 7.5](#sec-7-5). Positive values favor the Target; negative values favor the Reference.

Paired Delta SNR is normally the primary quantitative comparison because the two sides share the closest available conditions:

* In simultaneous RX Compare, Target and Reference receivers measure the same remote transmitter. This reduces transmitter-power, waveform and shared-path differences within the pair.
* In simultaneous TX Compare, the same remote receiver measures Target and Reference. This reduces receiver-hardware, antenna, local-noise and reporting differences within the pair.
* Sequential TX A/B uses deterministic scheduled pairs rather than same-cycle evidence.

**Decode Outcomes**

Decode Outcomes show what happened inside and outside the paired subset:

* <strong class="defined-term">Joint / Joint Spots / Joint Pairs:</strong> qualifying paired evidence exists.
* <strong class="defined-term">Only Target:</strong> Target evidence exists without Reference evidence in the relevant comparison unit.
* <strong class="defined-term">Only Reference:</strong> Reference evidence exists without Target evidence.
* <strong class="defined-term">Both (Async):</strong> both sides have evidence for the peer identity, but no qualifying joint unit survives for that category.

Use Delta SNR to describe the paired strength difference and Decode Outcomes to describe comparative reach. A result can have a clear paired median while retaining substantial one-sided evidence; both observations belong in the conclusion.

Same-cycle pairing reduces shared confounders but does not make separated stations or different hardware chains physically identical. In simultaneous comparisons, the Target-Active Gate protects Target downtime from being counted as failure, while Reference uptime still needs independent confirmation.

<a id="sec-3-4"></a>

#### 2.3 Use the map to locate the effect

The map is the geographic overview. Use its colors, category labels and markers to identify the distance and direction worth inspecting next.

**Map summary**

A <strong class="defined-term">median</strong> is the middle value after sorting, or the midpoint of the two central values when the count is even. It is less strongly moved by one unusually high or low value than the arithmetic mean.

* Compare segments show the median of qualifying station-level Delta SNR medians. Positive favors Target; negative favors Reference.
* Success segments show the arithmetic mean of qualifying station Success Rates after giving every qualifying peer one equal vote.

The Compare scale uses the amateur-radio display convention `1 S-unit = 6 dB`. This is a scale annotation, not a claim that every S-meter is calibrated.

**Station categories**

Read the category label as well as its color:

* Success: Target evidence is shown by `T` markers in green. Qualifying zero-Target peers are shown as `E` for Elsewhere or `OS` for Other Signals in grey.
* Compare: Joint is green, Both (Async) is yellow-orange, Only Target is purple and Only Reference is white.

**Distance rings**

Near rings can be consistent with shorter skip or near-vertical incidence skywave (NVIS) behavior; far rings can be consistent with DX behavior. The rings describe path distance and are not direct elevation-angle measurements.

Map color points to the effect. The following evidence levels show how broad and well-supported it is.

<a id="sec-3-5"></a>

#### 2.4 Check Stations and Spots

* <strong class="defined-term">STATIONS</strong> describes footprint breadth across distinct qualifying `callsign + locator` identities.
* <strong class="defined-term">SPOTS</strong> describes qualifying observation volume.

For Compare, both rows are divided into Only Target, Joint, Both (Async) and Only Reference. Station categories assign each identity to one main category. Spot categories count evidence volume, including exclusive observations associated with identities that also have joint evidence.

For Success, `SPOTS` divides denominator evidence into Target and Elsewhere for RX, or Target and Other Signals for TX. `STATIONS` divides qualifying identities into peers with at least one Target observation and peers with counter-evidence only. Target-only and ineligible evidence are excluded because they do not enter Success Rate.

Footer counts follow the visible map scope. A large number of Spots from only a few Stations means repeated evidence from a narrow identity base. Many Stations show wider identity and geographic participation.

<a id="sec-3-6"></a>
<a id="sec-3-6a"></a>

#### 2.5a Inspect a Geographic Segment (Success Mode)

Use `Segment Inspector` to select one or more distance ranges and compass directions. This opens the evidence behind the corresponding map area.

**Target and counter-evidence.** Target and Elsewhere/Other-Signals counts show the observations entering the selected segment's Success denominator.

**Average by Station** gives every qualifying peer one equal vote and matches the map value. **Observation-Level** pools all qualifying observations. When the two differ, high-volume peers are influencing the pooled result differently from the typical peer.

**Station Success Rate by Evidence Count** plots one station with Target evidence at each point. The vertical position is its Success Rate; the horizontal base-2 log axis is its `Target + counter-evidence` count. Upper-right points combine a high rate with repeated evidence. Left-side points show where relatively little evidence can produce an extreme percentage.

Zero-Target stations are omitted from that scatter plot because they would all appear at `0%`. They remain in map counts, temporal evidence and Station Insights when `Show Zero-Target` is enabled.

**Success over time** shows station-balanced and Observation-Level panels. Similar patterns indicate that evidence volume is not changing the story substantially. Divergence shows where busy peers or intervals affect the pooled rate. Empty cells mean no qualifying evidence, not a measured `0%`.

<a id="sec-3-6b"></a>

#### 2.5b Inspect a Geographic Segment (Compare Mode)

**Decode Outcomes** show the breadth of Joint, Only Target, Both (Async) and Only Reference stations. This establishes whether the paired Delta SNR describes much of the footprint or a narrower joint subset.

**Station Medians (Delta SNR)** gives each contributing station one value: its median paired Delta SNR. Stations therefore receive equal weight. A distribution concentrated above or below zero shows a consistent Target- or Reference-favoring direction across the available paths. A wide or split distribution shows that the effect varies by path.

**Joint-spot or scheduled-pair Delta SNR** shows every consolidated same-cycle pair or every valid scheduled pair in sequential TX A/B. This view exposes spread, quantization and outliers, while allowing active stations to contribute multiple values. A shift between this distribution and Station Medians shows how observation volume differs from the station-balanced picture.

**Joint-spot or scheduled-pair Delta SNR over time** uses exactly the same observation-level evidence rows and selected distance/direction scope as the top-right Joint-Spot or Scheduled-Pair Delta SNR histogram. Station Insights row selections do not change this segment-level view. The left panel preserves each row's actual UTC date and time; the right panel folds the same evidence from all contributing dates onto one 24-hour UTC-hour axis.

Sequential TX A/B reports `scheduled pairs` instead of `joint spots`.

The UI term `Joint Spot` means a consolidated same-cycle comparison unit, not necessarily one untouched database row. Exact station and segment aggregation are defined in [Section 7.7](#sec-7-7).

<a id="sec-3-7"></a>
<a id="sec-3-7a"></a>

#### 2.6a Inspect the Contributing Stations (Success Mode)

`Station Insights` lists the `callsign + locator` identities contributing to the selected segment. Success rows show Target and Elsewhere or Other Signals evidence, Success Rate, and median successful Target SNR normalized to 1 W. Read each rate together with its Target and counter-evidence counts; use `Show Zero-Target` to restore qualifying stations without Target evidence.

Select one or multiple stations to open the selected station evidence view. Below `Station Insights`, the chronological panel shows Success Rate and Target/counter-evidence over time across night, greyline/mixed and daylight path classes, next to the successful Target-SNR distribution. If multiple stations are selected, their aggregated evidence is visualized together.

<a id="sec-3-7b"></a>

#### 2.6b Inspect the Contributing Stations (Compare Mode)

Select one or multiple stations to open the selected station evidence view. `Station Insights` lists the `callsign + locator` identities contributing to the selected segment; Compare rows show joint and exclusive evidence plus station-level median Delta SNR, and `Show Non-Joint` includes identities without qualifying paired evidence. Below the station table, a Delta SNR histogram appears next to either a `Chronological` time plot or the date-folded `UTC-Hour` plot. These plots use the selected joint spots or scheduled pairs; the `UTC-Hour` view requires evidence from at least two distinct UTC dates. If multiple stations are selected, their aggregated evidence is visualized together. The histogram and active time plot use the median of the selected evidence, not the segment median above.

<a id="sec-3-8"></a>

#### 2.7 Verify the underlying evidence

`Drill-Down` is the row-level audit surface:

* Success exposes target-active peer-cycle classifications, including Target-only.
* Simultaneous Compare exposes same-cycle Target/Reference evidence and Delta SNR.
* Local Median Neighborhood expands the local Reference identities behind the cycle median.
* Sequential TX A/B exposes the planned UTC pair, `Micro-Med A`, `Micro-Med B` and Pair Delta.

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

#### 3.1 Recognize broad and stable evidence

Judge the result from the complete evidence picture:

* participating station identities;
* qualifying spot or scheduled-pair volume;
* agreement across stations;
* station-balanced and observation-level summaries;
* adjacent geographic segments;
* time and path-illumination views;
* Decode Outcomes;
* identity and locator quality;
* experiment control and repetition.

Evidence is **broader** when several identities and adjacent segments agree. It is **more stable** when the station-balanced view, observation-level view, time views and repeated runs tell a compatible story. It is **better controlled** when the selected playbook's operating requirements were followed and documented.

<strong class="defined-term">90% Stability</strong> is a descriptive bootstrap interval around a median. A narrow interval means the displayed median changes little when the available values are resampled. Use it to describe sensitivity to the observed sample. It is not a confidence interval or statistical significance test, and it does not establish independence or eliminate data bias.

WSPRadar deliberately does not collapse these dimensions into one proof grade. The visible counts, distributions and underlying rows let the operator judge the result in the context of the actual experiment.

<a id="sec-4-2"></a>

#### 3.2 Strengthen a result through repetition and control

When the result will support an important station decision:

* extend the observation window across the propagation states named in the conclusion;
* prefer multi-day evidence for statements spanning complete daily cycles;
* repeat the experiment on another day or propagation period;
* for sequential TX Hardware A/B, reverse the A/B schedule assignments;
* keep non-tested variables stable between repetitions;
* compare runs with the same direction, band, benchmark, filters and evidence thresholds;
* investigate any identity, locator or short interval that supplies a large fraction of the evidence;
* preserve setup notes so a later run can reproduce the station configuration.

Small observed differences become more useful when they recur across stations, time periods, adjacent segments and controlled repetitions.

TX and RX use different peer populations and opportunity definitions. Compare like-for-like TX and RX runs when investigating station balance or an "alligator" pattern.

<a id="sec-4-3"></a>

#### 3.3 Write an evidence-matched conclusion

A useful conclusion states:

* Target and Reference definition;
* TX or RX direction;
* band and resolved UTC window;
* selected geographic scope;
* result type;
* station-balanced value;
* observation-level value where relevant;
* Stations and Spots or joint-station and joint-spot/pair counts;
* Decode Outcomes for Compare;
* experiment conditions and any Reference correction;
* whether the pattern repeated across time, stations or runs.

**Success wording**

> For this Target, band, UTC window and selected peer population, the displayed Success Rate describes the fraction of independently confirmed opportunities in which the Target also produced qualifying evidence. The Stations, Spots, geographic scope and time views describe the breadth and repetition supporting that result.

**Compare wording**

> For this Target, Reference, band, UTC window and selected segment, station-balanced Delta SNR favored the Target/Reference by the displayed amount. The observation-level Delta SNR, joint station and spot/pair counts and Decode Outcomes describe the supporting paired and one-sided evidence.

Match the design name to the quantity being described:

* A **Hardware A/B Test** compares the documented local paths.
* A **Buddy Test** compares complete installed stations and their environments.
* **Local Median Neighborhood** compares the Target with the active median-neighborhood definition inside the selected radius.
* **Local Best Station** compares the Target with a changing best-peer envelope.
* A directional result describes the observed WSPR paths and participating stations rather than an absolute radiation pattern.
* The `1 S-unit = 6 dB` annotation describes the map scale rather than calibration of the participating receivers.

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
* operating schedule;
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
| **Scientific controls** | Query population, pairing, classification, normalization, eligibility or aggregation. These include direction, identity, band, time, benchmark, correction, solar filter, exclusion filters and evidence thresholds. | Saved when applicable and recorded in the export package. Changing one clears the completed result so the analysis can be rerun with the new definition. |
| **View controls** | Which completed evidence is displayed or inspected, without rerunning the upstream query. These include map scope, selected segment, selected stations, non-joint or zero-Target visibility, temporal view and evidence time bin. | Map scope, Segment Inspector range/direction and the applicable durable Compare/Success result-view choices are saved. Table filters and other incidental interactions remain transient. |
| **Transient UI state** | Panel expansion, table and Drill-Down filters, documentation visibility, prepared download bytes and other incidental session interaction state. | Not part of the scientific configuration and normally not serialized. |
| **Configuration fields preserved for reproducibility** | The applicable scientific branch plus explicitly supported durable view settings. | Stored in the versioned `.config`. Inactive hidden branches are omitted instead of being preserved as dormant values. |

Exact formulas and processing rules remain in [Scientific Methods](#sec-7).

<a id="sec-5-1"></a>

#### 4.1 Workflow controls

**`Load Demo`** opens maintained historical profiles. You can load a profile for inspection or run it immediately.

**`Load Config`** strictly validates and loads a versioned JSON `.config` file. Invalid identities, dates, choices, ranges, duplicate fields and unsupported schema versions are rejected.

**`Save Config`** opens a compact profile form. Enter a title and optional description; an optional stable ID can be supplied or generated automatically. The resulting `<profile-id>.config` stores every applicable input and durable Compare/Success result-view choice. When the configured time mode is `Last X Hours`, saving also asks whether to retain that moving relative window or replace it with the active run's resolved absolute UTC start/end window. Choose the absolute form when a later run should address the same dates. A saved configuration does not contain result rows, external experiment notes or transient table filters.

**`Run RX Analysis` / `Run TX Analysis`** is one direction-aware button. It runs Success and, when a benchmark is selected, Compare for the RX or TX Analysis chosen in Core Parameters.

**`Prepare All Results for Download`** builds the current analysis export package on demand.

**`Load full documentation` / `Hide full documentation`** explicitly loads or hides the complete web manual.

**`Prepare PDF`** builds the complete selected-language manual as a PDF on demand. The full web manual does not need to be open first.

<a id="sec-5-2"></a>

#### 4.2 Core controls

These controls define the Target, operating direction, band and evidence window.

| UI label | Factory default | What it controls |
|---|---|---|
| **RX Analysis / TX Analysis** | none; required | RX evaluates the Target as a receiving WSPR station; TX evaluates it as a transmitting WSPR station. `Run` and `Save Config` remain disabled until either option is selected. |
| **Your Callsign (Receiver under Test)** / **Your Callsign (Transmitter under Test)** | blank | Direction-specific exact Target identity. Accepted syntax is 3 to 15 characters from `A-Z`, `0-9` and `/`. |
| **QTH Locator (4-6 Chars)** | blank | Map center and local-radius origin. Success also uses the first four characters to match Target identity. |
| **Operating Band** | `20m` | Exactly one of `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` or `23cm`. |
| **Time Selection** | `Last X Hours` | Selects recent or custom UTC evidence. Recent mode allows 1 to 168 hours and defaults to 24. |
| **Last hours back (DB updated every 15 min)** | `24` | Appears for `Last X Hours`; accepts 1 to 168 hours. The absolute endpoints are resolved when the run starts and retained for that active run. At save time, choose whether the file keeps `Last X Hours` or freezes those resolved UTC endpoints. |
| **Start Date**, **End Date**, **Start Time (UTC)**, **End Time (UTC)** | previous day `00:00` through current day `23:59` | Appear for `Custom Date/Time`. Dates start at 2008 and one window is limited to 31 days. Resolved endpoints are quantized down to 15-minute boundaries. Success and Compare currently differ at the exact end boundary, as documented in [the time model](#sec-7-1). |

Use the callsign exactly as uploaded. `DL1MKS`, `DL1MKS/P`, `DL1MKS/1` and `DL1MKS/QRP` are separate identities; WSPRadar does not apply hidden prefix matching.

A Maidenhead locator is a compact grid-square location code. Four characters identify a broad area; six characters identify a smaller area inside it. WSPRadar uses the configured QTH as the map center and local-radius origin, while Success matches the Target using its first four locator characters.

<a id="sec-5-3"></a>

#### 4.3 Benchmark controls

**`Benchmark Design`** has the factory default `No benchmark (Success only)`. The current choices are:

- `No benchmark (Success only)`
- `Hardware A/B-Test (Local Setup)`
- `Reference Station (Buddy Test)`
- `Local Neighborhood Benchmark`

Success-only skips Compare. The other choices add Compare while retaining the separate Success result.

| UI label | Default and range | When it appears and what it controls |
|---|---|---|
| **Reference SNR Correction (dB)** | `0.0`; `-99.9` to `+99.9` in `0.1 dB` steps | Appears for Compare and is hidden for Success-only. The value is added to the Reference-side SNR before Delta SNR is calculated. |
| **Reference Callsign** | `DL2XYZ` example | Reference Station / Buddy Test. Replace the example with one exact callsign different from the Target. |
| **Local Benchmark Method** | `Local Median Neighborhood` | Local Neighborhood Benchmark. Selects `Local Median Neighborhood` or the strict `Local Best Station`. |
| **Neighborhood Radius (km)** | `100`; 10 to 250 km in 10 km steps | Local Neighborhood Benchmark. Includes local Reference coordinates around the configured QTH. |
| **Setup B Callsign** | blank | RX Hardware A/B Test. Enter one exact callsign different from Setup A. |
| **Repeat Interval** | `10 min`; `4, 6, 10, 12, 20, 30, 60 min` | TX Hardware A/B Test. Shared recurrence of each physical path. All choices are even WSPR-compatible divisors of one UTC hour. |
| **Target Start** | `00 UTC`; even phases below the Repeat Interval | TX Hardware A/B Test. Defines the Target / Setup A UTC start phase. |
| **Reference Start** | `02 UTC`; even phases below the Repeat Interval | TX Hardware A/B Test. Defines the Reference / Setup B UTC start phase and is kept disjoint from Target. |

Hardware A/B Test follows the selected **RX Analysis / TX Analysis** option. RX displays the two-receiver Setup B callsign; TX displays the shared Repeat Interval, two disjoint Start controls, a swap action and the resulting one-hour schedule preview. Pairing follows that schedule automatically.

Switching direction or benchmark mode hides the inapplicable branch. Its previous widget values are neither saved nor restored. A Success-only configuration therefore contains no dormant comparison parameters.

##### Reference SNR Correction sign

A positive correction makes the corrected Reference SNR stronger and therefore reduces Target-minus-Reference Delta SNR. Enter a measured `target - reference` calibration offset with the same sign. For example, a common-input calibration of `+1.6 dB` is entered as `+1.6 dB`. The exact equations appear in [the Delta SNR method](#sec-7-5).

The correction applies to:

- Setup B or the Reference schedule in Hardware A/B Test;
- the Reference callsign in Reference Station / Buddy Test;
- the selected local value in Local Best Station; and
- every local contribution before Local Median Neighborhood aggregation.

A constant correction is suitable for a defensible constant offset. Clipping, unstable AGC, intermittent routing, frequency-dependent response and incorrect power reports require correction at the experiment or hardware level instead. [Appendix C](#sec-c) describes calibration.

<a id="sec-5-4"></a>

#### 4.4 Filters and evidence thresholds

These controls let you shape the peer population, illumination period and minimum evidence required for display.

**`Exclude Special Callsigns Q, 0, 1`**

- **Default:** off
- **Applies to:** all results
- **Effect:** excludes qualifying peer identities beginning with `Q`, `0` or `1`.
- **Change this when:** the intended peer population excludes the balloon- or telemetry-style identities represented by these prefixes. State the choice in reports.

Use this control according to the question:

- In RX Compare, beacon-like or telemetry-style transmitters can provide valuable weak same-cycle signals seen by both receivers.
- In RX Success, retain them when beacon reception is part of the question; exclude them when the intended population is ordinary amateur-station activity.
- In TX analysis, the filter applies to receiver-side peer identities. Use it when those identities are distorting the intended receiver population.

**`Exclude Moving Stations`**

- **Default:** off
- **Applies to:** mapped peers
- **Effect:** removes a peer callsign reporting more than one four-character locator after other filters.
- **Change this when:** mobile identities or changing locators would otherwise mix locations inside one callsign. Check Drill-Down to distinguish likely movement from incorrect locator data.

**`Local QTH Solar State`**

- **Default:** `All 24h`
- **Choices:** `All 24h`, `Daylight (Elev > +6°)`, `Nighttime (Elev < -6°)`, `Greyline (-6° to +6°)`
- **Applies to:** all results
- **Effect:** keeps cycles classified by solar elevation at the Target QTH.
- **Change this when:** the scientific question is specifically about one local illumination state. This is different from the path-illumination classes shown in Success evidence.

**`Map Scope (Max Distance km)`**

- **Default:** `22000`
- **Choices:** `2500`, `5000`, `10000`, `15000`, `20000`, `22000`
- **Applies to:** map and inspection views
- **Effect:** sets the visible and inspectable radial scope; it does not narrow the upstream query.
- **Change this when:** a regional view is useful. Map scope is a reproducibility-relevant view control, not an upstream data filter.

**`Min. Joint Spots per Station`**

- **Default:** `1`
- **Range:** 1 to 50
- **Applies to:** simultaneous Compare
- **Effect:** requires this many joint peer-cycles before a station contributes paired Delta SNR.
- **Change this when:** you want more repeated paired evidence per station and accept reduced geographic coverage.

**`Min. Joint Pairs`**

- **Default:** `1`
- **Range:** 1 to 50
- **Applies to:** sequential TX Hardware A/B
- **Effect:** requires this many joint scheduled pairs before a station contributes paired Delta SNR.
- **Change this when:** you want more repeated scheduled pairs per station and accept reduced geographic coverage.

The Compare joint threshold also suppresses exclusive categories whose own count is below the same numeric cutoff. In sequential TX Hardware A/B, paired eligibility is counted in scheduled pairs, while exclusive evidence is counted in one-sided scheduled pairs and compared with that numeric cutoff.

**`Min. Target+Counter-Evidence per Station`**

- **Default:** `5`
- **Range:** 1 to 100
- **Applies to:** Success
- **Effect:** requires this many Target+Elsewhere RX or Target+Other Signals TX observations before a peer contributes.
- **Change this when:** you want a different evidence floor.

Lowering this threshold increases map coverage, but station rates become more discrete when supported by only one or two qualifying opportunities. Values such as `0%`, `50%` or `100%` can then represent very little evidence. Read the count beside the rate and strengthen a small sample with a longer or repeated run.

**`Min. Qualifying Stations per Map Segment`**

- **Default:** `1`
- **Range:** 1 to 10
- **Applies to:** all maps
- **Effect:** requires this many qualifying identities before a segment is drawn.
- **Change this when:** you want map color to require broader identity support and accept more blank segments.

<a id="sec-5-5"></a>

#### 4.5 Map, inspector and export controls

These controls work with completed evidence and do not rerun the upstream query unless explicitly stated otherwise.

- Segment range and direction selectors change the inspected scope. Compare and Success selections are saved independently.
- `Show Zero-Target` restores qualifying Success identities with zero Target confirmations. Its setting is saved for Success.
- `Show Non-Joint` restores Compare identities represented only by exclusive or asynchronous evidence. Its durable value is saved when Compare applies.
- Station selection changes the selected-station figures and selected Drill-Down. Compare and Success selections are saved independently as exact `callsign + locator` identities. Selecting every station stores an all-stations intent instead of enumerating the current table; with a moving `Last X Hours` window, the reconstructed membership can therefore change with the evidence. A loaded explicit identity absent from the current segment scope remains unselected with a notice rather than being replaced; its saved identity is retained until you make a new table selection, so changing the segment scope can still make it available.
- The selected-station time-bin control changes only its chronological timeline. The applicable Compare and Success/absolute values are saved.
- The Selected Compare view group selects `Chronological` or `UTC-Hour`. `UTC-Hour` uses fixed one-hour slots and neither changes nor overwrites the saved chronological bin. The selected view is stored in `.config`.
- The Segment Compare time-bin buttons change only the left segment-level temporal panel. The control does not change the dates-folded UTC-hour panel, the selected-station timeline, pairing or analysis; its selected bin is stored independently in `.config`.
- Empty Success time bins remain blank; they are not converted to zero-rate evidence.
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
4. **UTC evidence window:** confirm the resolved start and end timestamps, not only the relative `Last X Hours` selection.
5. **Actual operation:** confirm that the Target was transmitting or receiving as intended and that WSPR uploading was enabled.
6. **Benchmark operation:** for Compare, confirm the exact Reference or Setup B identity and that the counterpart was operating during the intended overlap.
7. **Design mechanics:** where applicable, confirm clock synchronization, TX schedule-to-path mapping, switching schedule, signal routing and reported power.

After these are established, inspect thresholds, exclusion filters, solar selection and map scope. A looser filter can reveal more qualifying evidence, but it cannot repair a run aimed at the wrong identity, band or time.

<a id="sec-6-2"></a>

#### 5.2 Diagnose by symptom

After the shared checks in Section 5.1, follow the branch that matches the result:

| Symptom | Next checks |
|---|---|
| **No result or no Target evidence** | Inspect the reported strict `code = 1` or historical-fallback status and current upstream availability. |
| **Compare has no Delta SNR** | Confirm shared remote peers in overlapping cycles or scheduled pairs, then clocks, TX A/B schedule-to-path mapping, switching schedule, joint threshold, filters and scope. |
| **Success has very few peers** | Confirm independent network activity, then `Min. Target+Counter-Evidence per Station`, exclusion and solar filters, timeframe and map scope. A longer window can add evidence without changing the intended population. |

<div style="page-break-before: always;"></div>

If evidence exists but looks unexpected, continue with these branches:

| Symptom | Next checks |
|---|---|
| **Many Target-only Success rows** | Target evidence exists without the independent confirmation required by the denominator. The rows remain auditable but do not enter Success Rate. |
| **`Only Reference = 0`** | Confirm Target-Active gating, evidence thresholds and selected scope; zero can be correct after those rules. |
| **Unexpected Hardware A/B Delta SNR sign** | Verify physical A/B mapping, Target/Reference order, schedule phases, correction sign, actual and reported power, and calibration notes. Reconcile one station in Drill-Down. |
| **Local result changes with radius** | Confirm QTH and radius, then inspect contributing local `callsign + locator` identities. Report useful radius sensitivity instead of selecting only the most favorable run. |
| **Old config with `band=All` is rejected** | Choose one exact band; automatic conversion would change the scientific question. |
| **Recent spots appear incomplete** | Allow about five minutes after the latest cycle, then check reporting and upstream status as described in Section 5.6. |

An upstream-data issue changes what the selected source supplies. An experiment-design issue changes whether the retained rows answer the intended question. Diagnose and report the two separately.

System Audit Status names the database origin once for the complete run. Its reason is `primary` when the first-priority source was selected, `cache affinity` when a guided demo selected a complete fresh bundle from a lower-priority provider before normal network-backed provider selection, `capacity spillover` when a lower-priority ready source admitted the complete request bundle because higher-priority request capacity could not, `failure fallback` when this run restarted after a provider-scoped failure or a higher-priority source was already unavailable during provider-health cooldown or recovery probing, or `committed source` when a rerender retained the run's already committed source. It then reports `database request`, `RAM cache` or `disk cache` plus timing for each strict and optional historical-fallback query separately. Those delivery labels describe how rows reached the analysis; they do not identify different databases or change the origin reason. On the same deployment, a guided demo can reuse raw provider query rows for up to 24 hours from their original fetch. Before making a new demo request, WSPRadar prefers the first configured provider that already has the complete required demo bundle cached. The cached rows retain their actual provider origin and are never combined across providers. Cache hits do not renew the deadline. A process restart loses the RAM tier, but the disk tier remains reusable if local storage survives; storage eviction can remove it sooner.

<a id="sec-6-3"></a>

#### 5.3 Callsign and locator checks

Compare callsigns are matched exactly. Success Target matching is stricter: exact callsign plus the configured QTH's first four characters. A Target uploading `JN37` while the configuration says `JN38` will not satisfy the Success Target condition.

Peer identities use exact callsign plus the full reported locator string. Bad, stale or changing locators can split one physical station, move it into the wrong segment or trigger the moving-station filter.

<a id="sec-6-4"></a>

#### 5.4 Historical decode-code fallback

WSPRadar first requests rows using `code = 1` for WSPR-2 evidence. If the strict query returns no Target-side evidence, it retries without that predicate for historical compatibility and reports the fallback in run status.

The fallback broadens selection. The current export package does not preserve the effective decode-filter or fallback state. Retain the reported run status in the experiment notes, especially because Compare and Success can take different paths.

<a id="sec-6-5"></a>

#### 5.5 How the Target-Active Gate shapes evidence

The Target-Active Gate keeps simultaneous comparisons focused on cycles in which Target participation is observable. It excludes Reference evidence outside those cycles, preventing known Target downtime from becoming automatic failure.

For example, if the Target station is shut down overnight, Reference spots from those offline hours are not counted as defeats. Within the retained cycles, Reference uptime and radio-path availability still need to be established from the experiment context.

Because the gate is intentionally Target-centric, swapping Target and Reference can change eligible cycles and Decode Outcomes. Sequential TX Hardware A/B uses its deterministic scheduled-pair method rather than the same simultaneous gate.

<a id="sec-6-6"></a>

#### 5.6 Working with upstream data

wspr.live states that its data is raw WSPRnet-reported data and may contain duplicates, false spots and other errors. Its volunteer infrastructure provides no guarantee of correctness, availability or stability. <a href="#ref-5">[Ref-5]</a>

wspr.live describes real-time data as available with a delay of a few minutes and says its scraper checks for new spots every few minutes. As a practical operating estimate, wait about **five minutes** after the final WSPR cycle before expecting a fresh analysis window to be reasonably populated.

Five minutes is not a completeness guarantee. Delayed uploads, ingestion interruptions and later corrections can appear after that point. <a href="#ref-5">[Ref-5]</a>

WSPRadar uses pairing, identity grouping, medians, thresholds and Drill-Down to reduce sensitivity to isolated bad rows and make them easier to inspect. Repeated plausible errors can still survive those controls.

Reported power and locators are user-supplied. Correct mathematics applied to an incorrect power or locator remains physically wrong.

<div style="page-break-before: always;"></div>

<a id="part-iii"></a>
## Part III: Scientific Foundations, Methods and Claims

This part places WSPRadar in its scientific and amateur-radio lineage, then defines exactly how it constructs, summarizes, interprets and preserves evidence. It supports method review, audit and serious reporting; the operator playbooks and result-reading chapters remain the practical route through the application.

<a id="sec-d"></a>
### 6. Literature, Prior Art and Positioning

This chapter explains which ideas WSPRadar inherits, integrates and extends. It highlights each source's useful contribution as well as the boundary of what that source demonstrates. It does not claim that the literature validates every WSPRadar metric or implementation choice.

<a id="sec-d-1"></a>
#### 6.1 From reporting network to experimental dataset

Taylor and Walker presented WSPRnet not merely as a live map but as an archive: "The WSPRnet database represents a rich source of experimental data for propagation studies." Their example groups observations by time of day over several weeks, illustrating both the value of accumulated reports and the need to interpret them as observational data. <a href="#ref-4">[Ref-4]</a>

Frissell et al. place WSPRNet alongside the Reverse Beacon Network and PSKReporter as established amateur-radio observation networks that provide "rich, ever-growing, long-term data of bottomside ionospheric observations." They distinguish those established networks from newer purpose-built citizen-science networks and recommend cross-calibration between instrument networks. The review supports the scientific value of amateur observations; it does not turn every individual receiver into a calibrated instrument. <a href="#ref-8">[Ref-8]</a>

The public WSPR archive is therefore unusually powerful, but it remains a successful-decode record produced by heterogeneous volunteer stations. Historical depth and geographic reach do not remove selection effects, identity errors, changing equipment or unknown operating schedules.

<a id="sec-d-2"></a>
#### 6.2 Making observational WSPR data interpretable

<a id="sec-d-lo"></a>
Lo et al. used 7 MHz WSPR observations to study greyline propagation and explicitly warned: "There is no official recording of the operating schedules for WSPR equipment." They checked whether a transmitter was heard anywhere, or whether a receiver heard anything from anywhere, before interpreting missing links as propagation behavior. They also stressed callsign/location consistency and the use of multiple sites. <a href="#ref-3">[Ref-3]</a>

That activity principle is direct prior art for WSPRadar's Target-Active Gate: silence should not become radio counter-evidence until operation is observable. Lo et al. do not, however, define WSPRadar's exact asymmetric gate, Success denominator or Decode Outcomes. Those remain WSPRadar design choices for a different estimand.

<a id="sec-d-3"></a>
#### 6.3 Antenna and station-comparison lineage

<a id="sec-d-toledo"></a>
**Toledo (2010): why slow alternation fails.** Sivan Toledo tried one antenna for roughly an hour, then another, and found that path SNR changed on the same scale as the apparent antenna differences. His conclusion was blunt: "Clearly, you can't compare antennas using WSPR using the naive technique that I was using." He identified per-cycle switching and simultaneous transmissions with separate hardware as stronger designs. This is the practical reason WSPRadar uses deterministic interleaved TX A/B schedules rather than long blocks and favors the shortest practical separation. Short separation reduces, but cannot eliminate, temporal confounding. <a href="#ref-7">[Ref-7]</a>

<a id="sec-d-milazzo"></a>
**Milazzo (2011): an early operator-led end-to-end comparison.** Carol Milazzo compared two stations 29 km apart through a common receiver 1,750 km away, corrected their reported SNRs for transmit-power differences, compared the trend with VOACAP, noted unequal duty cycles and also examined reciprocal RX reports. Her first conclusion was: "The WSPR network data permitted a comparison of signals from two antennas to a distant destination." This is an unusually complete early amateur-radio case study and the earliest detailed comparison retained in this manual. It is not claimed as the first: Milazzo herself cites several earlier WSPR antenna experiments. Different QTHs, hardware and local noise, one selected remote receiver and no formal uncertainty analysis limit the causal claim. <a href="#ref-9">[Ref-9]</a>

<a id="sec-d-griffiths-squibb"></a>
**Griffiths and Squibb (2017): same-signal RX comparison as station diagnosis.** For two receivers at separate QTHs, they retained "only those reports of the same station at the same time selected for analysis" and inspected SNR difference against soil moisture, time, distance and station changes. The work shows how paired WSPR data can diagnose the whole receive system and reveal effects hidden by spot totals. Because antennas, QTH, noise and equipment differed, it supports comparative station evidence rather than calibrated antenna gain or a single causal explanation. <a href="#ref-10">[Ref-10]</a>

<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels and Lamy (2022): conditioned simultaneous RX.** Their peer-reviewed study states that "two identical 160-m band WSPR receiver stations are conditioned to compare the performance of different 160-m band antennas." A calibrated dual-receiver design then compares common remote transmissions simultaneously. This is the strongest direct precedent in this set for RX Hardware A/B Test and for characterizing receive-chain differences before comparing antennas. Their propagation experiment also shows that polarization and ionospheric effects can change reported SNR, so even a carefully conditioned setup does not produce one context-free antenna number. <a href="#ref-2">[Ref-2]</a>

<a id="sec-d-zander"></a>
**Zander (2022): a mathematical model for simultaneous TX comparison.** Zander analyzes two local antennas driven by separate nominally equal-power transmitters and callsigns in the same WSPR cycle. He retains a receiver only when both signals are "reported by the same station in the same time interval." Under the paper's same-time, common-path and equal-power model, shared path loss and receiver noise cancel in the SNR difference; separate narrowband interference, failed decodes and integer SNR quantization remain. Because each difference is formed within one remote receiver, "the method does not require any receiver calibration"; equality or correction of the two transmitter powers is still required. <a href="#ref-1">[Ref-1]</a>

In each preliminary experiment, Zander collected about 1,000 reports in roughly one hour and retained 150-200 joint reports from 15-35 receiving stations. The observed sample standard deviation was close to 3 dB; for about 100 useful samples, the paper estimates the standard deviation of the arithmetic mean below 0.5 dB. It then reports "accuracy of less than a dB" within hours. Scientifically, that calculation is evidence of repeatability or precision under the model, not traceable total accuracy: the paper separately identifies receiver-geography, directivity and unknown elevation-angle biases. Long runs reduce random congestion but not those systematic effects. The study is strong support for simultaneous same-receiver Delta SNR; it does not validate WSPRadar's sequential one-transmitter TX A/B, station-balanced medians, Decode Outcomes or other benchmark designs.

<a id="sec-d-4"></a>
#### 6.4 Analysis infrastructure and operator tools

Griffiths and Robinett showed how a relational time-series database enables a self-join for the "same sender at the same time in the same band for two different reporters." Their Grafana examples combine SNR-difference scatterplots, medians, quartiles, time heatmaps, distance and azimuth views, plus data export. This is important precedent for inspectable comparison infrastructure, but not for WSPRadar's exact eligibility rules, denominators or estimators. <a href="#ref-11">[Ref-11]</a>

WSPR.Rocks provides rapid WSPR exploration, SQL access, maps, tables, SpotQ and other analyses. WSPRadar differs by organizing the workflow around explicit experiment designs, pairing and row-level audit rather than a leaderboard. <a href="#ref-12">[Ref-12]</a>

WSPRdaemon focuses on robust multi-receiver acquisition, scheduling and added noise/Doppler metadata, illustrating why acquisition stability and noise context matter for RX analysis. <a href="#ref-13">[Ref-13]</a>

SOTABEAMS WSPRlite and DXplorer provide accessible WSPR-based antenna/location comparison and the DX10 metric. <a href="#ref-14">[Ref-14]</a>

WSPR-Station-Compare explicitly connects station-comparison software with the Vanhamel and Zander methods. <a href="#ref-15">[Ref-15]</a>

The Antenna Performance Analysis Tool is another user-oriented WSPR antenna-report service. Its existence means WSPRadar should not claim to be the first WSPR antenna-analysis tool. <a href="#ref-16">[Ref-16]</a>

WATT provides Excel/VBA reporting, mapping, filtering and timeline exploration, reinforcing the practical value of inspectable data rather than only a fixed score. <a href="#ref-17">[Ref-17]</a>

These tools demonstrate substantial prior art in acquisition, browsing, ranking, visualization and antenna reporting. Their existence is part of WSPRadar's lineage, not a weakness in its positioning.

<a id="sec-d-5"></a>
#### 6.5 What WSPRadar inherits, integrates and adds

WSPRadar inherits important ideas rather than claiming to have invented WSPR comparison: accumulated observations, activity checks, reported-power correction, common-condition pairing, calibrated receive chains, geographic/time views and database joins all have clear precedents above.

WSPRadar integrates those ideas into one operator workflow that includes:

* TX and RX analysis with No benchmark (Success only), Hardware A/B Test, Reference Station / Buddy Test and Local Neighborhood Benchmark designs;
* Target activity checks, same-cycle or deterministic scheduled-pair comparison, reported-power normalization and optional Reference-side SNR correction;
* conditional Success, paired Delta SNR and categorical Decode Outcomes as separate evidence questions;
* maps, Segment Inspector, Station Insights, time/solar views and row-level Drill-Down;
* evidence thresholds, station-versus-observation diagnostics and descriptive Stability checks;
* guided demos, versioned configurations, run metadata, processed evidence, tables, figures and practical supplements.

Within the literature and tools reviewed here, the clearest WSPRadar-specific additions are:

* the conditional Success opportunity model and its explicit counter-evidence denominator;
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
| No benchmark (Success only), RX or TX | Target receiver or transmitter | RX: same transmitter decoded elsewhere; TX: other same-band signal decoded by the peer receiver | one Target-active peer-cycle | observable Target participation | same two-minute cycle | rate: none; successful Target SNR display: reported 1 W | one Success Rate per peer | arithmetic mean of peer rates; pooled rate retained | conditional network reach, not unconditional decode probability |
| Hardware A/B Test, RX | Setup A receiver | simultaneous Setup B receiver | one consolidated remote-transmitter peer-cycle | Target-Active Gate | same transmitter and cycle | common TX power cancels; correction applies to Setup B | median Delta SNR | median of station medians | controlled local receive paths only to the extent the remaining chains are controlled |
| Hardware A/B Test, TX | Setup A scheduled starts | Setup B scheduled starts | one peer identity in one planned Target/Reference pair | deterministic disjoint schedules; no simultaneous gate | nearest one-to-one starts under one shared Repeat Interval | both sides normalized to reported 1 W; correction applies to Setup B | median scheduled-pair Delta SNR | median of station medians | sequential, not simultaneous; timing and switching effects remain |
| Reference Station / Buddy Test, RX | Target receiver | external Reference receiver | one consolidated remote-transmitter peer-cycle | Target-Active Gate; Reference uptime controlled externally | same transmitter and cycle | common TX power cancels; correction applies to the Reference | median Delta SNR | median of station medians | complete installed stations and environments, not isolated receiver sensitivity |
| Reference Station / Buddy Test, TX | Target transmitter | external Reference transmitter | one consolidated remote-receiver peer-cycle | Target-Active Gate; Reference uptime controlled externally | same receiver and cycle | both sides normalized to reported 1 W; correction applies to the Reference | median Delta SNR | median of station medians | complete installed stations; depends on reported-power accuracy |
| Local Median Neighborhood | Target RX or TX | cycle/path median of one contribution per active local `callsign + locator` | one Target/local-Reference peer-cycle | Target-Active Gate | same peer path and cycle | TX values normalized to reported 1 W; correction applied before the local median | median Delta SNR | median of station medians | dynamic uncalibrated pool; result depends on radius and active membership |
| Local Best Station | Target RX or TX | strongest qualifying local station for that cycle/path | one Target/best-Reference peer-cycle | Target-Active Gate | same peer path and cycle | TX values normalized to reported 1 W; correction applied before best selection | median Delta SNR | median of station medians | changing best-peer envelope, not a local average or fixed Reference |

The matrix is an orientation aid. The definitions, formulas and processing rules below are authoritative.

<a id="sec-7-1"></a>
#### 7.1 Data source, decode selection and time model

WSPRadar reads the public `wspr.rx` table through the selected read-only ClickHouse HTTP interface. Spots are observational records from independently operated transmitters, receivers, software and networks. They are not a randomized or calibrated sample of possible paths. Decode selection, historical fallback and upstream-data behavior are documented once in [Sections 5.4-5.6](#sec-6-4).

The selected UTC endpoints are resolved when the run starts, then both are quantized down to 15-minute boundaries for query reuse. Success uses a half-open interval, `start <= time < end`: an observation exactly at the quantized start is eligible, while one exactly at the quantized end is excluded. Compare currently uses database `BETWEEN`, so it can include an observation exactly at both the quantized start and end. A boundary observation can therefore appear in Compare but not Success, and adjacent Compare windows can share the exact endpoint.

A **WSPR cycle** is the two-minute interval aligned to an even UTC minute. WSPRadar derives simultaneous cycles from spot timestamps. Sequential TX A/B instead retains timestamps, admits only each path's configured modulo schedule, and attaches the planned Target and Reference starts of its nearest one-to-one pair. A scheduled pair is eligible only when both planned starts lie inside the selected comparison window.

<a id="sec-7-2"></a>
#### 7.2 Identity and matching rules

WSPRadar retains the reported identity as part of the evidence. Callsign variants and reported locators are therefore scientifically meaningful inputs, not cosmetic labels.

| Analysis | Target matching | Peer / Reference identity | Lowest result unit |
|---|---|---|---|
| RX Success | exact RX callsign plus Target QTH grid-4 | TX callsign + reported TX locator | one Target-active peer-cycle |
| TX Success | exact TX callsign plus Target QTH grid-4 | RX callsign + reported RX locator | one Target-active peer-cycle |
| Simultaneous Compare | exact Target and Reference callsigns | remote callsign + reported locator | one consolidated peer-cycle |
| Sequential TX A/B | exact Target callsign split by configured UTC schedule | RX callsign + reported locator | one planned Target/Reference pair |
| Local Reference pool | exact local callsign + locator inside radius | remote peer as above | one local-identity contribution per cycle/path |

Compare callsigns are matched exactly. Success Target matching is stricter: it uses the exact callsign together with the configured QTH's first four locator characters. A Target uploading `JN37` while the configuration says `JN38` will not satisfy the Success Target condition.

Peer identities use exact callsign plus the full reported locator string. Bad, stale or changing locators can split one physical station, move it into the wrong segment or trigger the moving-station filter.

Multiple qualifying rows for one side of a normal simultaneous peer-cycle are consolidated; the maximum normalized SNR represents that side. Local Median Neighborhood instead takes a within-local-identity median and then a median across local identities.

The local pool excludes the Target by exact callsign. A base callsign and a suffixed callsign are therefore distinct identities unless the exact Target form matches. Each local contribution retains its reported locator as part of identity.

<a id="sec-7-3"></a>
#### 7.3 Target-Active Gate

The Target-Active Gate anchors Success and simultaneous Compare to cycles in which Target participation is observable:

* **TX:** at least one qualifying Target transmission spot exists somewhere in the cycle.
* **RX:** at least one qualifying decode uploaded by the Target receiver exists in the cycle.

The gate protects known Target downtime from becoming automatic failure. For example, Reference spots from hours when the Target station is shut down are not counted as defeats.

The asymmetry is deliberate: in the absence of authoritative operating schedules, WSPRadar defines Success and simultaneous Compare around the designated Target and admits only cycles with observable Target participation. In Compare, Reference uptime is not a second gate and must therefore be controlled by the experimenter.

Because every Joint observation already demonstrates Target participation, the gate's asymmetry affects only one-sided or asynchronous Decode Outcomes and the counter-evidence denominator of Success Rate; the gate itself does not alter Joint-only Delta SNR summaries.

Swapping Target and Reference can therefore change eligible cycles and Decode Outcomes. Sequential TX A/B uses deterministic schedule assignment and planned pairs rather than this simultaneous gate. Its role-independent half-interval tie rule preserves the same physical pairs when A/B is swapped.

<a id="sec-7-4"></a>
#### 7.4 Success classification and formulas

Success measures the Target's conditional reach among opportunities that have independent evidence of network activity.

For each Target-active peer-cycle, WSPRadar records Target evidence and independent external evidence:

* **RX external evidence:** a different receiver reported the same transmitter identity in the same cycle.
* **TX external evidence:** the peer receiver reported a non-Target same-band transmitter in the same cycle.

Target requires both Target and external evidence. Elsewhere / Other Signals requires external evidence without Target. Target-only means Target evidence exists without external evidence and is excluded from the denominator.

$$\text{Success Rate}_{RX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Elsewhere}}$$

$$\text{Success Rate}_{TX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Other Signals}}$$

The eligible peer population is globally sourced after band, time, gate, filters and thresholds. Success Rate is therefore conditional on observable network activity and propagation. It is not an estimate of every attempted transmission or a calibrated receiver detection probability.

The Success Rate classification itself is not power-normalized. The successful Target SNR displayed beside it is normalized to reported 1 W.

<a id="sec-7-5"></a>
#### 7.5 Power normalization, correction and Delta SNR

Power normalization places successful TX evidence on a common reported-power basis. WSPR SNR is decoder-reported in dB on the WSJT scale, referenced to a 2500 Hz bandwidth. WSPR messages include reported transmit power in dBm. <a href="#ref-18">[Ref-18]</a>

WSPRadar normalizes successful SNR to a reported 1 W / 30 dBm reference:

$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$

This removes the **reported** power term. It does not correct antenna gain, efficiency, feedline loss, effective isotropic radiated power (EIRP), receiver calibration or local noise.

Reference SNR Correction is added to the Reference side:

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

Compare map `STATIONS` categories assign identities; `SPOTS` categories count evidence volume. Success map bars use the same two levels but align them with the Success denominator. A `Joint Spot` is a consolidated same-cycle comparison unit, not necessarily one untouched database row.

<a id="sec-7-7"></a>
#### 7.7 Aggregation hierarchy

WSPRadar calculates a peer-level value before the geographic segment value. This gives each qualifying peer one vote in station-balanced summaries, so a high-volume station cannot dominate solely because it uploaded more observations.

Medians reduce sensitivity to isolated extreme values, duplicate-like bursts and quantized SNR outliers. They do not remove systematic calibration error, propagation bias or correlation across time and stations.

**Success**

1. Classify each Target-active peer-cycle.
2. Sum Target, counter-evidence and Target-only by peer `callsign + locator`.
3. Require the configured Target+counter threshold.
4. Calculate one Success Rate per qualifying peer.
5. Calculate the segment arithmetic mean of peer rates.
6. Retain the pooled observation-level rate as a diagnostic.

The station-balanced value and pooled observation-level value answer different questions. The first describes the typical qualifying identity with equal peer weights; the second gives every qualifying observation equal weight.

**Simultaneous Compare**

1. Consolidate Target and Reference evidence by cycle and peer identity.
2. Calculate Delta SNR for joint cycles.
3. Require the configured joint count for each peer.
4. Calculate one station-level median Delta SNR.
5. Calculate the segment median across station medians.

**Sequential TX A/B**

1. Retain exact-callsign spots only when their UTC start matches the configured Target or Reference schedule.
2. Pair scheduled Target and Reference starts one-to-one by nearest cyclic separation and require both planned starts to lie inside the comparison window.
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
#### 7.8 Stability, distributions and inspection-layer weighting

WSPRadar uses a deterministic 500-resample percentile bootstrap with replacement and reports the central 90% interval around the median. Station-level intervals resample station medians. Raw paired intervals resample peer-cycle or scheduled-pair Delta values.

The calculation treats values as exchangeable even though WSPR observations can remain correlated by station, time and geography. It is a descriptive **Stability** interval, not a confidence interval or significance test.

Compare Delta SNR histograms use fixed bins within a panel. They normally use 1 dB bins, use 0.5 dB only for a clear half-dB lattice and aggregate broad ranges to 1, 2, 3, 6 or 10 dB so a panel does not exceed 40 bars. A minimum visible span of 3 dB avoids visually magnifying tiny variation.

Compare temporal heatmaps first count evidence in cells formed by UTC-time, or folded UTC-hour, bins and rounded integer-dB Delta SNR bins. Each panel is scaled independently:

$$D_{relative} = 100 \times \frac{n_{cell}}{\max(n_{cell,panel})}$$

The densest occupied cell is therefore `100`, proportional occupied cells lie between `0` and `100`, and empty cells remain blank. This is a percentage of that panel's maximum cell count, not a percentage of all evidence. Values and colors therefore do not provide absolute-count comparability between separately normalized panels. Segment-level and selected-station Compare timelines use this rule; Success timelines retain their documented Success-rate and count semantics.

The four Compare distribution and temporal panels use a presentation-only, median-centered nonlinear Delta SNR scale. The two segment temporal panels share the observation-level median of all paired evidence in the selected segment. The selected-station distribution and its active time panel instead share the pooled median of the currently selected station or stations. Thus each two-panel evidence scope has one center, while absolute labels preserve interpretation between scopes.

The white connected markers remain a separate statistic: the median within each populated time bin.

Let `M` denote that scope's exact evidence median. For a broad range, equal visual steps are anchored at `M`, `M +/- 3`, `M +/- 6`, `M +/- 10`, `M +/- 20` and `M +/- 30 dB`; an unlabelled tail anchor continues at `M +/- 60 dB` and extrapolates farther when necessary. If every required deviation from `M` is at most `10 dB`, the tighter visible anchors are `M`, `M +/- 1`, `M +/- 3`, `M +/- 6` and `M +/- 10 dB`; unlabelled `M +/- 20` and `M +/- 40 dB` anchors define the compressed continuation outside that visible range. The required deviation includes the raw histogram and rounded heatmap-bin edges, a minimum 3 dB half-span and absolute `0 dB`, so tails and the Target-equals-Reference reference are not silently clipped.

Tick labels show the resulting **absolute Delta SNR**, not distance from `M`. For example, `M = +6 dB` produces the broad labels `-24, -14, -4, 0, +3, +6 M, +9, +12, +16, +26, +36 dB`.

The transform does not change scientific values or grouping. Histogram counts and bin edges remain in raw dB, temporal cells remain rounded integer-dB bins, medians and Stability intervals remain raw-dB statistics, and relative-density colors retain the calculation above. Because nonlinear vertical stretching gives equal raw-dB histogram bins unequal displayed heights, read histogram **bar length** against `Share (%)`; displayed bar area is not probability. Success SNR figures remain linear.

The selected-station plots use the observation-level weighting and display rules described in [Section 2.6](#sec-3-7); those view choices do not change map aggregation, opportunity classification or pairing.

<a id="sec-7-9"></a>
#### 7.9 Geography and solar classification

WSPRadar calculates distance and azimuth using a spherical Earth radius of 6371 km and renders an Azimuthal Equidistant projection centered on Target QTH. Radial boundaries are 2500, 5000, 10000, 15000, 20000 and 22000 km; azimuth sectors are 22.5 degrees.

This gives internally consistent mapping geometry. It is not survey-grade geodesy, and reported locators represent grid-cell positions rather than measured antenna coordinates.

`Local QTH Solar State` uses solar elevation at Target QTH. Normal same-cycle evidence uses its cycle timestamp. Automatic scheduled TX A/B uses the midpoint between the two planned starts, so Target and Reference in one pair cannot be split into different solar classes. Success evidence plots separately classify sampled great-circle path illumination as night, greyline/mixed or daylight. These answer different questions.

<div style="page-break-before: always;"></div>

<a id="sec-8"></a>
### 8. Evidence-Matched Claims and Reproducibility

WSPRadar supports precise statements about conditional reach, paired differences, one-sided evidence and where those effects were observed. Strong reporting describes the evidence actually produced, preserves the run definition and keeps laboratory quantities separate from network observables.

<a id="sec-8-1"></a>
#### 8.1 Claims the evidence supports

Use the result type that matches the statement:

* **Success** supports a statement about conditional Target reach among independently confirmed opportunities. Use the receiver-sensitivity and expected-100% rows below together with the denominator in [Section 7.4](#sec-7-4).
* **Compare Delta SNR** supports a statement about paired Target-minus-Reference evidence. Use the gain and significance rows together with [Sections 7.5](#sec-7-5) and [7.6](#sec-7-6).
* **Decode Outcomes** support a statement about joint and one-sided evidence. Use the exclusive-decode row and report the paired subset separately.
* **Distance-dependent patterns** support a statement about the observed distance segments. Use the take-off-angle row because distance is observed while radiation angle is not.
* **Local Neighborhood Benchmark** supports a statement about the selected dynamic neighborhood definition. Use the local-median row and report radius, method and active contributors.

| Avoid | Evidence-matched wording |
|---|---|
| "Antenna A has 3 dBi more gain." | "Path A produced a +3.0 dB median normalized Delta SNR against B for the paired evidence in this band, window and segment." |
| "My receiver sensitivity is 72%." | "The Target receiver's Success Rate was 72% among qualifying peer-cycles independently confirmed elsewhere." |
| "Success should be close to 100%." | "Success is a conditional global network-reach factor; 100% is not the expected baseline." |
| "A is statistically significantly better." | "The paired median favored A and its descriptive 90% Stability interval was [range]; no significance test was performed." |
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
* Success Rate is conditional on globally sourced observable opportunities;
* a TX cycle decoded nowhere is indistinguishable from no transmission without an external log;
* Target-active gating is asymmetric;
* sequential TX A/B remains time-separated;
* reported-power normalization is only as accurate as the reported field;
* station hardware, software, terrain, noise, polarization and propagation remain combined;
* network density varies by geography, band and time;
* distance does not establish radiation angle or propagation mode;
* upstream availability and archive corrections remain external.

These boundaries do not prevent useful station comparisons. They determine which quantity the result represents and how precisely it should be reported.

<a id="sec-8-3"></a>
#### 8.3 Reporting checklist

For a serious result, report:

* preserve the saved `.config` and separately record the WSPRadar release or Git commit because the export does not currently capture it;
* configured UTC selection and, when available from the run notes, the resolved 15-minute query bounds; identify whether the evidence is Success or Compare because exact-endpoint handling differs;
* exact band and TX/RX direction;
* Target callsign and configured QTH;
* Benchmark Design, Reference identity or local radius/method;
* Hardware schedule design where applicable;
* Reference SNR Correction and calibration basis;
* special, moving-station and solar filters;
* all evidence thresholds;
* joint station and joint spot/pair counts;
* station-level median Delta SNR and 90% Stability interval;
* Decode Outcomes and `STATIONS` / `SPOTS` distributions;
* Success Rate with its denominator and weighting level;
* equipment, power, schedule and known limitations;
* export package plus external experiment notes.

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
  figure_selected_station_evidence.png
  table_station_insights_current_segment.csv
  table_drilldown_selected_stations.csv
  table_drilldown_all_stations_current_segment.csv
  analysis_cache.parquet
success/                         # when a Success result exists
  ...same figure/table pattern...
  analysis_cache.parquet
```

Figures use a high-resolution light/paper presentation. Files without an applicable recipe or selected evidence can be absent. CSV files reflect current segment and station selections. Parquet files contain processed post-filter evidence, not untouched upstream dumps.

For Compare, `figure_selected_station_evidence.png` reproduces the selected-station temporal view active when the export is prepared. Chronological mode uses the selected Compare time bin; `UTC-Hour` uses fixed one-hour slots and the same selected evidence rows. The mode is stored in the saved `.config` and in `run_metadata.json`.

The saved configuration records the applicable runnable settings. `run_metadata.json` records the application name and version; export time; language; direction; band; benchmark choice; configured time selection; correction; filters; thresholds; result blocks and inspector selections.

The effective `code = 1` or historical-fallback state is reported while the run executes but is not stored in the package. The package also does not provide a Git commit, exact resolved pre-quantization endpoints, a stable explicit interval convention, or a query/query-parameter fingerprint. Quantized map bounds can occur inside the opaque export signature, but that internal value is not a versioned endpoint contract and should not be treated as one.

The package supports audit and reproducibility but is not a complete computational snapshot. It does not currently include:

* a Git commit or clean-worktree record;
* explicit resolved and quantized UTC endpoint fields with the applicable interval convention;
* effective strict `code = 1` versus historical-fallback state for each result block;
* exact SQL, a stable query/query-parameter fingerprint or untouched upstream responses;
* a dependency lock or operating-system description;
* authoritative transmitter/receiver operating logs, calibration records or external experiment notes.

Retain the ZIP with station notes, switching schedule, power measurements and calibration data.

<a id="sec-8-5"></a>
#### 8.5 Disclaimer

WSPRadar is experimental open-source software provided "as is" without warranties. Its source and methods can be audited, but accuracy, completeness, availability and suitability are not guaranteed. Do not make major financial or safety decisions from WSPRadar alone.

<div style="page-break-before: always;"></div>

<a id="sec-ref"></a>
### References

* <a id="ref-1"></a><a href="https://arxiv.org/abs/2209.08989">[Ref-1]</a> **Preprint.** Zander, J. (2022). *Simple HF antenna efficiency comparisons using the WSPR system*. arXiv:2209.08989v1. doi:10.48550/arXiv.2209.08989.

* <a id="ref-2"></a><a href="https://doi.org/10.1155/2022/4809313">[Ref-2]</a> **Peer-reviewed article.** Vanhamel, J.; Machiels, W.; Lamy, H. (2022). *Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*. International Journal of Antennas and Propagation, 2022, 4809313. doi:10.1155/2022/4809313.

* <a id="ref-3"></a><a href="https://www.mdpi.com/2073-4433/13/8/1340">[Ref-3]</a> **Peer-reviewed article.** Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). *A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals*. Atmosphere, 13(8), 1340. doi:10.3390/atmos13081340.

* <a id="ref-4"></a><a href="https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf">[Ref-4]</a> Taylor, J. H.; Walker, B. (2010). *WSPRing Around the World*. QST, 94(11), 30-32.

* <a id="ref-5"></a><a href="https://wspr.live/">[Ref-5]</a> **Official data-service documentation.** WSPR.live, *Welcome to WSPR Live* and <a href="https://wspr.live/wspr_downloader.php">*WSPR Exporter*</a>: database description, schema, mode-code mapping, raw-data/availability disclaimer and real-time delay. Accessed 2026-07-15.

* <a id="ref-6"></a><a href="https://wsjt.sourceforge.io/wsjtx-main_en.html">[Ref-6]</a> **Official operating documentation.** WSJT-X 3.0.1 User Guide: WSPR message formats and decoder performance; Windows `--rig-name` file isolation; Audio settings and file locations. QRP Labs, <a href="https://www.qrp-labs.com/images/qmx/manuals/operation_1_03_000.pdf">*QMX Operating Manual, firmware 1_03_000*</a>: Beacon `Frame` and `Start` scheduling and WSPR repetition guidance; <a href="https://qrp-labs.com/images/ultimate3s/operation3.12a.pdf">*Ultimate3S Operating Manual, firmware v3.12a*</a>: global Frame/Start behavior, sequential mode entries and per-entry `Aux` values; <a href="https://qrp-labs.com/images/appnotes/AN003_A4.pdf">*AN003: Ultimate3/3S relay-switched filters*</a>: filtered relay/driver interfacing and RF-off switching intervals. Accessed 2026-07-15.

* <a id="ref-7"></a><a href="https://sivantoledotech.wordpress.com/2010/09/24/failure-to-use-wspr-to-compare-antennas/">[Ref-7]</a> **Operator technical account.** Toledo, S. / 4X6IZ (2010). *Failure to Use WSPR to Compare Antennas*.

* <a id="ref-8"></a><a href="https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2023.1184171/full">[Ref-8]</a> **Peer-reviewed review article.** Frissell, N. A. et al. (2023). *Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations*. Frontiers in Astronomy and Space Sciences, 10, 1184171. doi:10.3389/fspas.2023.1184171.

* <a id="ref-9"></a><a href="https://www.qsl.net/kp4md/wspr.htm">[Ref-9]</a> **Amateur-radio technical article and club presentation.** Milazzo, C. F. / KP4MD (2011). *Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*.

* <a id="ref-10"></a><a href="https://www.researchgate.net/publication/319903566_Improving_HF_Band_SNR_from_analysis_of_WSPR_spots">[Ref-10]</a> **Amateur-radio magazine article.** Griffiths, G.; Squibb, N. J. (2017). *Improving HF Band SNR from analysis of WSPR spots*. Practical Wireless, October 2017, 23-26.

* <a id="ref-11"></a><a href="https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf">[Ref-11]</a> **Conference paper.** Griffiths, G.; Robinett, R. (2020). *Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana*. ARRL/TAPR Digital Communications Conference 2020.

* <a id="ref-12"></a><a href="https://wspr.rocks/help.html">[Ref-12]</a> **Tool documentation.** WSPR.Rocks, *Help &amp; Documentation*: SpotQ, SQL access, duplicate analysis, maps, charts and heatmaps.

* <a id="ref-13"></a><a href="https://wsprdaemon.readthedocs.io/en/stable/description/how_it_works.html">[Ref-13]</a> **Tool documentation.** WSPRdaemon, *How wsprdaemon Works*: multi-receiver decoding, reporting, scheduling, noise and Doppler metadata.

* <a id="ref-14"></a><a href="https://www.sotabeams.co.uk/wsprlite-classic">[Ref-14]</a> **Product documentation.** SOTABEAMS, *WSPRlite Classic / DXplorer*: WSPR-based antenna-performance analysis and DX10 metric.

* <a id="ref-15"></a><a href="https://sites.google.com/myuba.be/wspr-station-compare/home">[Ref-15]</a> **Project documentation.** WSPR-Station-Compare, project page referencing Vanhamel et al. and Zander.

* <a id="ref-16"></a><a href="https://wspr.bsdworld.org/">[Ref-16]</a> **Tool documentation.** Antenna Performance Analysis Tool, WSPR-based antenna report generator.

* <a id="ref-17"></a><a href="https://www.gm4eau.com/home-page/wspr/">[Ref-17]</a> **Tool documentation.** GM4EAU, *WATT WSPR Analysis Tool*: Excel/VBA reporting, mapping, filtering and timeline animation.

* <a id="ref-18"></a><a href="https://www.arrl.org/wspr">[Ref-18]</a> **Official technical overview.** ARRL, *WSPR*: message format, coding, duration, timing, occupied bandwidth and SNR reference. Accessed 2026-07-12.

<div style="page-break-before: always;"></div>

<a id="part-iv"></a>
## Part IV: Practical Supplements

This part collects optional setup procedures, the timed relay helper, Reference-side calibration guidance and the project license. Use the sections that apply to your station and experiment.

<a id="sec-a"></a>
### Appendix A: Parallel WSJT-X Instances

This procedure creates a second isolated WSJT-X instance, for example for simultaneous RX Hardware A/B Test on Windows. The current WSJT-X guide documents `--rig-name` as the supported way to isolate each instance's settings and writable files. WSJT-X versions and installation paths can change, so verify the current guide if your menus differ. <a href="#ref-6">[Ref-6]</a>

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
5. Open **File > Settings > General** and set the exact Setup B callsign and locator used for reporting.
6. Return to the main WSPR screen, confirm the intended band and audio level, enable spot uploading when required, and verify that uploaded rows use the Setup B identity.
7. Confirm clock synchronization for both instances.

Separate directories do not prove RF-path independence. Confirm empirically that both streams use the intended hardware.

<div style="page-break-before: always;"></div>

<a id="sec-b"></a>
### Appendix B: Timed A/B Relay Switch

For sequential TX A/B antenna tests, one transmitter feeding two RF paths through a controlled switch is normally preferable to two independent transmitters. Transmitter, frequency reference, WSPR chain, callsign, power setting and timing remain common.

WSPRadar includes:

`tools/Timed-AB-Relay-Switch`

Currently published version-0.1 release package:

[Download the Timed A/B Relay Switch release package](https://github.com/markusthemaker/WSPRadar/releases/download/timed-ab-relay-switch-v0.1.0/Timed-AB-Relay-Switch-v0.1.0.zip)

The repository helper uses the same schedule vocabulary and constraints as WSPRadar:

* `Repeat Interval` is shared by Target and Reference and accepts `4, 6, 10, 12, 20, 30` or `60 min`.
* `Target Start` and `Reference Start` are different even UTC phases below that interval.
* The default is `Repeat Interval = 10`, `Target Start = 00`, `Reference Start = 02`.

The relay selects each path before its configured start and holds the most recently selected path through unscheduled gaps. It does not switch at unused two-minute WSPR boundaries. Configure the helper and WSPRadar identically from the transmissions that actually occur on each RF path. For example, one QMX emitting at `00, 10, 20, 30, 40, 50` through an alternating relay produces `Repeat Interval = 20`, Target `00`, Reference `10`; it does not produce `10 / 00 / 02`. If physical polarity is reversed, change whether relay ON means Target or swap the two Start assignments.

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

Before transmitting:

* test without RF power;
* verify Target and Reference path polarity;
* verify no transition occurs during a WSPR transmission;
* use a dummy load or low-power continuity/SWR test;
* document relay channel, polarity, lead time, schedule assignment and path mapping.

Switch loss, isolation, connectors, feedline differences and antenna surroundings remain part of the result. Swapping antennas between switch paths can help separate antenna effects from path effects.

<div style="page-break-before: always;"></div>

<a id="sec-c"></a>
### Appendix C: Reference SNR Calibration

This procedure estimates a stable additive offset between receive chains or Reference-side paths.

1. **Common input:** feed both receive chains from one stable antenna through a suitable splitter and controlled cables.
2. **Characterize the splitter:** account for output imbalance and cable differences; swap outputs in a control run when practical.
3. **Collect paired evidence:** operate simultaneously across the intended signal levels without changing gain or decoder settings.
4. **Estimate the offset:** use paired Delta SNR evidence and state whether the estimator is station-balanced or raw-pair.
5. **Check stability:** inspect by station, time and SNR. One constant is not defensible if offset changes with level, frequency, AGC or time.
6. **Apply the sign:** enter the observed `target - reference` offset with the same sign.
7. **Validate:** repeat or swap paths and confirm corrected common-input Delta is plausibly near zero.

A narrow Stability interval indicates repeatability of the available sample, not traceable laboratory accuracy. Splitter loss, mismatch, coupling and source instability can remain.

<a id="sec-license"></a>
### License

WSPRadar is licensed under the GNU Affero General Public License version 3 (AGPLv3). The repository `LICENSE` file is controlling.

"""
