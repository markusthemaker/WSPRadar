# Same-cycle Reference workflow and locator discovery

## Approved scope and source model

On 2026-09-28 the user authorized removing sequential TX completely, merging controlled Hardware A/B and independent-station comparison into Reference Setup/Station, retaining Reference Neighbourhood (Local Median), and making Reference locator discovery replace manual entry. Relevant deletion and merging were explicitly authorized; unrelated scientific guidance and historical records remain intact. No backward compatibility for retired unpublished configurations was requested. The user subsequently authorized removing the timed scheduler and its associated WSPRadar documentation while preserving the utility separately outside this codebase.

The accepted source model is a parallel co-authored English/German pair. The common semantic specification is: exact callsign and locator identity; same-band, same-cycle pairing; Target QTH as the sole manual analysis locator and geographic origin; provider/role/band/window-bound Reference discovery with explicit multiple-candidate choice; field-local Run validation; current-only saved-configuration and URL contracts without retired aliases or migrations; Joint-only Delta SNR while retaining one-sided and Both (Async) evidence.

## Disposition and destinations

| Original scope | Disposition | Authoritative destination / reason |
|---|---|---|
| RX/TX controlled and Buddy playbooks | Merged, with experiment-specific interpretation preserved | Sections 1.2, 2.3.1 and 2.4.1: one fixed-Reference calculation, distinct controlled-setup and independent-station explanations |
| Sequential TX playbook and Appendix C scheduling/switching | Retired active application guidance | No application destination: feature removed. The timed relay utility and its operating guide are preserved independently outside WSPRadar; no scheduler integration remains in the application guides |
| Schedule controls and scheduled scientific/evidence branches | Retired | Sections 4.3 and 7 retain only supported same-cycle behavior; every unchanged mathematical display formula is retained |
| Mandatory manually entered Reference locator | Replaced | Sections 4.3, 5.3 and 7.2 explain archive resolution, ambiguity, source failure and the limit of physical-location claims |
| Controlled calibration and independent-station caveats | Retained and relabeled | Fixed-Reference playbooks, Section 4.3 and the now-numbered Appendix C calibration procedure |
| Simultaneous device/frequency procedures | Retained | Appendix B; a frequency-swap schedule is still an experimental procedure, not a cross-cycle pairing method |
| External prior art and historical records | Retained | Chapter 6/source references, prior changelog entries, frozen fixtures and provenance; only assertions of current sequential application support changed |
| Result guidance | Merged / retired | benchmark_reference carries both physical interpretations; obsolete scheduled and benchmark_hardware entries retired, common one-sided/outlier guidance preserved |

## Bilingual structural and semantic review

Both manuals retain 146 unique anchors with no missing internal targets. Chapter order and the common formulas remain aligned: 30 display formulas per language, including all 13 detector formulas; no display formulas were deleted. The same scientific edits were reviewed as paired semantic units across method choice, RX/TX playbooks, controls, identity/conditioning/aggregation, outlier evidence, interpretation, exports and appendices. English Reference Setup/Station and Reference Neighbourhood correspond to German Referenzaufbau/-station and Referenznachbarschaft. Controlled-setup and independent-station interpretation remain scientific guidance; the subsequently removed optional context field is recorded below.

Compilation, synchronization, whitespace and internal-anchor checks have been performed. Regression and rendered-PDF verification are recorded in the task handoff; this ledger does not substitute for those checks.

## Source hashes and reverse outlines

### EN

- Original SHA-256: `75ccc2147e2550183c55dd13f5bf1b1637460913af02929e98af21a392cee225`
- Integrated SHA-256: `09ebb06c78bc7e4c2de508e1043c99aa093b753a1931050f43ec28f3fad1149f`

# docs/doc_en.py
### 0. Why WSPRadar?
#### 0.0 WSPR in 2 Minutes
#### 0.1 What WSPRadar can show
#### 0.2 What one run produces
#### 0.3 Your first useful run
### Table of Contents
## Part I: Operator Guide
### 1. Choose and Prepare the Analysis
#### 1.1 Build a strong experiment foundation
#### 1.2 Choose the analysis that matches the question
#### 1.3 Follow the evidence path
### 2. Run and Interpret Your Analysis
#### 2.1 RX Performance
#### 2.2 TX Performance
#### 2.3 RX Benchmark
##### 2.3.1 Reference Setup/Station
##### 2.3.2 Reference Neighbourhood
#### 2.4 TX Benchmark
##### 2.4.1 Reference Setup/Station
##### 2.4.2 Reference Neighbourhood
#### 2.5 Find and Review Temporary ΔSNR Departures
##### 2.5.1 When to use this expert diagnostic
##### 2.5.2 How detection works in practice
##### 2.5.3 Read and investigate a reported event
##### 2.5.4 Adjust selectivity and preserve the result
### 3. Strengthen and Communicate Your Result
#### 3.1 Judge breadth, consistency and repeatability
#### 3.2 Strengthen a result through repetition and control
#### 3.3 Write an evidence-matched conclusion
#### 3.4 Preserve the run and its context
## Part II: Controls and Troubleshooting
### 4. Controls and Configuration
#### 4.1 Workflow controls
#### 4.2 Question, Target and measurement-window controls
#### 4.3 Benchmark-design controls
##### Reference-side SNR correction sign
#### 4.4 Filters and evidence thresholds
#### 4.5 Map, inspector and export controls
#### 4.6 Benchmark outlier-detection controls
### 5. Troubleshooting and Data Quality
#### 5.1 Confirm the run definition first
#### 5.2 Diagnose by symptom
#### 5.3 Callsign and locator checks
#### 5.4 Historical decode-code fallback
#### 5.5 How the Target-Active Gate shapes evidence
#### 5.6 Working with upstream data
## Part III: Scientific Foundations, Methods and Claims
### 6. Literature, Prior Art and Positioning
#### 6.1 From reporting network to experimental dataset
#### 6.2 Making observational WSPR data interpretable
#### 6.3 Antenna and station-comparison lineage
#### 6.4 Analysis infrastructure and related tools
#### 6.5 What WSPRadar inherits, integrates and adds
### 7. Scientific Methods
#### 7.1 Data source, observation units and time model
#### 7.2 Identity, matching and row consolidation
#### 7.3 Target-active conditioning and eligibility
#### 7.4 Performance analysis target, classification and summary statistics
#### 7.5 Power normalization, correction and Benchmark Delta SNR
#### 7.6 Paired evidence, Decode Outcomes and missingness
#### 7.7 Aggregation hierarchy and weighting
#### 7.8 Geographic, temporal and selected-path summaries
##### 7.8.1 Geographic summaries
##### 7.8.2 Benchmark evidence coverage
##### 7.8.3 Temporal summaries and UTC folding
##### 7.8.4 Selected-path summaries
##### 7.8.5 Descriptive spread and visualization transforms
#### 7.9 Geography, solar classification and population filters
#### 7.10 Dependence, uncertainty and validation scope
#### 7.11 Robust local-baseline Delta SNR event detection
### 8. Evidence-Matched Claims and Reproducibility
#### 8.1 Claim classes and evidence-matched wording
#### 8.2 Interpretation boundaries
#### 8.3 Reporting and reproducibility checklist
#### 8.4 Analysis export package
#### 8.5 Disclaimer
### References
## Part IV: Practical Supplements
### Appendix A: Parallel WSJT-X Instances for Simultaneous RX
#### A.1 Create the second instance
#### A.2 Clone the starting configuration if required
#### A.3 Separate every data path
#### A.4 Limitations of WSJT-X for simultaneous TX
### Appendix B: Simultaneous TX Reference Setup
#### B.1 Choose the callsigns
#### B.2 Align the schedule and separate the signals
#### B.3 Check power and simultaneous signal quality
#### B.4 Verify WSPRnet and the selected archive
#### B.5 Device-specific setup
##### B.5.1–B.5.2 QMX and QMX+ Virtual U3S, and Ultimate3S
##### B.5.3 ZachTek firmware 2.19 randomized split-lane builds
#### B.6 Confirm by exchange or crossover
### Appendix C: Reference SNR Calibration
### License

### Verbatim original passages changed or retired (en)

Each source span below is preserved verbatim from the accepted original. Its heading gives the original source line and nearest section; the disposition follows the scope table above. A changed span may contain retained material that was moved or rephrased solely to integrate the approved contract.

#### Original docs/doc_en.py:44 — 0.0 WSPR in 2 Minutes

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
WSPRadar does not decode these radio messages or reconstruct a compound identity from Type 2 and Type 3 phases. It analyzes the callsign, locator, time and power fields preserved by the selected reporting archive. For simultaneous TX A/B, both exact identities must therefore appear in the archive with the truthful shared grid-4 and aligned message phases; [Sections 2.4.1](#sec-3-tx-benchmark-simultaneous), [7.1](#sec-7-1), [7.2](#sec-7-2) and [7.6](#sec-7-6) explain the practical and scientific consequences.
````

#### Original docs/doc_en.py:70 — 0.1 What WSPRadar can show

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| <span class="analysis-choice"><span class="analysis-family">RX Benchmark</span><br><strong class="analysis-variant">Hardware A/B</strong></span> | Did two local receive paths differ while observing the same remote transmissions? | Compare two antennas, each feeding its own simultaneous receiver and decoder chain, as complete receive paths; attribute a difference specifically to the antennas only when the remaining chains are matched, characterized or confirmed by crossover; feed one antenna through a characterized splitter into two receivers to compare receiver or decoder paths; place a preamplifier, filter, feedline or common-mode choke in only one otherwise controlled path and benchmark the two documented complete receive paths. |
| <span class="analysis-choice"><span class="analysis-family">TX Benchmark</span><br><strong class="analysis-variant">Hardware A/B</strong></span> | Did two local transmit paths differ under simultaneous or tightly scheduled operation? | Feed two antennas from separate calibrated transmit chains and transmit simultaneously with synchronized cycles, distinguishable signals and adequate isolation; use one transmitter and a controlled RF switch to alternate between two antennas on a fixed UTC schedule; compare two feedlines, matching networks, filters or complete transmit paths while controlling actual power, timing and the remaining chain. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Reference Station / Buddy Test</strong></span> | How does my complete station compare with one known station? | <strong>RX:</strong> compare your receiver with a known Buddy receiver while both observe the same remote transmitters in the same cycles; <strong>TX:</strong> compare your transmitter with a Buddy transmitter at the same remote receivers in the same cycles; repeat a stable, well-understood Buddy design as a relative whole-station baseline before and after documented station work, without treating the Buddy as an absolute calibrated standard. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Local Median Neighborhood</strong></span> | How does my complete station compare with the observed nearby WSPR peers? | See whether your receive or transmit station is broadly above, near or below the cycle- and path-specific median of qualifying observed local peers inside the selected radius; commission a station when no single suitable Buddy Reference is available; identify directions, distances or UTC periods where the station departs from that contextual local baseline, while checking neighborhood membership and radius sensitivity. This compares complete stations under the observed conditions; it does not isolate antenna gain or rank all nearby stations. |
````

#### Original docs/doc_en.py:75 — 0.1 What WSPRadar can show

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
The Reference is part of the scientific question, not just a display choice. A controlled <strong class="defined-term">Hardware A/B Test</strong> provides the strongest basis for attributing an observed difference to local paths or components, but only to the extent that the remaining chains are controlled. A <strong class="defined-term">Reference Station / Buddy Test</strong> compares two complete installed stations, including their QTHs, equipment, terrain and local noise environments. Neighborhood benchmarks provide changing contextual baselines rather than fixed or calibrated standards.
````

#### Original docs/doc_en.py:93 — 0.2 What one run produces

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
The map provides the geographic overview. Segment-level evidence shows how the observation changes with distance and direction and how much support lies behind it. Performance or Benchmark Evidence separates the main result from its complementary evidence. Temporal Evidence shows whether the pattern changed during the run or recurred at particular UTC hours. Station Insights reveals which station identities contribute. Selected Station Evidence follows one exact radio path, and Drill-Down exposes the observations, same-cycle comparisons or scheduled A/B pairs behind the summaries.
````

#### Original docs/doc_en.py:135 — Table of Contents

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
        * [2.3.1 Hardware A/B: simultaneous receive paths](#sec-3-rx-benchmark-hardware)
        * [2.3.2 Reference Station / Buddy Test](#sec-3-rx-benchmark-buddy)
        * [2.3.3 Local Median Neighborhood](#sec-3-rx-benchmark-local-median)
````

#### Original docs/doc_en.py:139 — Table of Contents

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
        * [2.4.1 Hardware A/B: simultaneous transmit paths](#sec-3-tx-benchmark-simultaneous)
        * [2.4.2 Hardware A/B: sequential transmit paths](#sec-3-tx-benchmark-sequential)
        * [2.4.3 Reference Station / Buddy Test](#sec-3-tx-benchmark-buddy)
        * [2.4.4 Local Median Neighborhood](#sec-3-tx-benchmark-local-median)
````

#### Original docs/doc_en.py:213 — Table of Contents

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* [Appendix B: Simultaneous TX Hardware A/B Setup](#sec-simultaneous-tx-setup)
````

#### Original docs/doc_en.py:222 — Table of Contents

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
* [Appendix C: Sequential TX A/B Scheduling and Switching](#sec-sequential-tx-setup)
    * [C.1 Requirements for a valid scheduled experiment](#sec-sequential-tx-setup-1)
    * [C.2 WSPRadar Timed A/B Relay Switch](#sec-sequential-tx-setup-2)
    * [C.3 Ultimate3S schedule example](#sec-sequential-tx-setup-3)
    * [C.4 QMX schedule examples](#sec-sequential-tx-setup-4)
    * [C.5 Verify mapping and preserve the experiment](#sec-sequential-tx-setup-5)
* [Appendix D: Reference SNR Calibration](#sec-reference-snr-calibration)
````

#### Original docs/doc_en.py:278 — 1.2 Choose the analysis that matches the question

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* **Hardware A/B** is the strongest design for a local component or path question, but it isolates that component only to the extent that the remaining paths are controlled.
* **Reference Station / Buddy Test** compares complete installed stations and their operating environments.
````

#### Original docs/doc_en.py:283 — 1.2 Choose the analysis that matches the question

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* **Local Median Neighborhood** compares your complete receiving or transmitting station with a changing Reference formed from qualifying nearby WSPR observations inside the selected radius. The Reference is calculated separately for each remote station and WSPR cycle.
````

#### Original docs/doc_en.py:322 — 1.3 Follow the evidence path

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Drill-Down.** Verify the retained opportunities, same-cycle pairs or scheduled pairs behind a result. Use it to check identities, locator changes, timing, one-sided evidence and isolated outliers.
````

#### Original docs/doc_en.py:420 — 2.3.1 Hardware A/B: simultaneous receive paths

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.3.1 Hardware A/B: simultaneous receive paths
````

#### Original docs/doc_en.py:422 — 2.3.1 Hardware A/B: simultaneous receive paths

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Use this design for two local antennas, feedlines, filters, preamplifiers, receivers or complete receive chains operated simultaneously at the same physical test QTH. Target and Reference need distinct exact reporting callsigns and the same Target grid-4. Components intended to be common must be physically common; shared grid-4 matching does not prove co-location or path equality.
````

#### Original docs/doc_en.py:424 — 2.3.1 Hardware A/B: simultaneous receive paths

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
This is the strongest RX design for attributing a difference to a local path. The result still compares the complete documented receive paths unless receiver, audio, gain, decoder and routing differences have been characterized. A broad recurring Delta-SNR shift plus compatible one-sided evidence supports one path outperforming the other under the tested conditions. A common-input calibration, splitter-output swap or hardware crossover is the most useful confirmation because it can separate the tested component from a persistent chain offset. [Appendix D](#sec-reference-snr-calibration) describes Reference SNR calibration.
````

#### Original docs/doc_en.py:426 — 2.3.1 Hardware A/B: simultaneous receive paths

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
<blockquote class="evidence-conclusion"><p>Under the documented simultaneous RX Hardware A/B setup, paired Delta SNR and Decode Outcomes described the observed difference between the Target and Reference receive paths for the shared transmitters, cycles and selected geographic scope.</p></blockquote>
````

#### Original docs/doc_en.py:430 — 2.3.2 Reference Station / Buddy Test

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.3.2 Reference Station / Buddy Test
````

#### Original docs/doc_en.py:432 — 2.3.2 Reference Station / Buddy Test

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Use a known, separately identifiable complete Reference receiver whose QTH, callsign, equipment, operating schedule and local environment are understood. RX pairs share the same remote transmitter and cycle, but Target and Reference remain distinct complete receiving stations with their own antennas, hardware, signal paths and local noise environments. The separately entered Reference Locator may contain the same grid-4 as Target QTH; equal grid-4 does not prove physical co-location.
````

#### Original docs/doc_en.py:440 — 2.3.3 Local Median Neighborhood

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.3.3 Local Median Neighborhood
````

#### Original docs/doc_en.py:456 — 2.4 TX Benchmark

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Question answered.** How did the Target transmitter or scheduled path differ from the selected Reference at shared remote receivers?
````

#### Original docs/doc_en.py:458 — 2.4 TX Benchmark

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
**Shared TX Benchmark evidence.** Same-cycle TX Benchmark compares Target and Reference at the same remote receiver in the same WSPR cycle. Sequential Hardware A/B instead uses deterministic scheduled pairs at the same receiver. Successful TX SNR is normalized to reported power before Delta SNR is formed; the result therefore depends directly on accurate power reporting. Decode Outcomes preserve Joint and one-sided evidence, but an exclusive observation has no missing-side SNR and is not power-normalized.
````

#### Original docs/doc_en.py:460 — 2.4 TX Benchmark

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Read the evidence path.** On the **Map**, sector color summarizes station-balanced median Delta SNR across remote receivers. Marker and footer categories show Joint and one-sided receiver evidence. Read each sector with receiver breadth and spot or scheduled-pair depth.
````

#### Original docs/doc_en.py:462 — 2.4 TX Benchmark

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
In **Segment Inspector**, compare the station-level Decode Outcomes with the observation- or pair-level composition. Station Medians give each remote receiver one equal vote, while Joint-Spot or Scheduled-Pair Delta SNR shows the full paired observation distribution. A shift shared across many receivers is different from one dominated by a few high-volume receivers.
````

#### Original docs/doc_en.py:464 — 2.4 TX Benchmark

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
**Temporal Evidence** shows whether Delta SNR changed through the run or recurred by UTC hour. Benchmark Evidence Coverage shows whether paired evidence remained broad through those times. For sequential TX, inspect whether the result is tied to one schedule phase or switching period; for simultaneous TX, inspect whether it is tied to one receiver, audio-frequency assignment or short interval.
````

#### Original docs/doc_en.py:466 — 2.4 TX Benchmark

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
In **Station Insights**, read each receiver's median Delta SNR with its Joint and one-sided counts. **Selected Station Evidence** reveals the paired result and evidence coverage at one receiver path. **Drill-Down** verifies receiver identity, reported powers, same-cycle pairing or scheduled-pair assignment, and correction sign.
````

#### Original docs/doc_en.py:470 — 2.4 TX Benchmark

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
**Boundary and confirmation.** TX Benchmark remains conditional on pairable evidence and accurate reported power. Simultaneous designs retain transmitter-chain, frequency-response, isolation and coupling differences. Sequential designs remain time-separated. Same-cycle one-sided evidence is also affected by the Target-Active Gate. Strengthen the result with broad receiver support, accurate power measurement, repeated runs and the method-specific controls below.
````

#### Original docs/doc_en.py:476 — 2.4.1 Hardware A/B: simultaneous transmit paths

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.4.1 Hardware A/B: simultaneous transmit paths
````

#### Original docs/doc_en.py:478 — 2.4.1 Hardware A/B: simultaneous transmit paths

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Use two distinguishable complete transmitter chains at the same physical test QTH, with different valid exact callsigns, synchronized WSPR cycles, separated clear frequencies, established actual and reported power, and adequate RF isolation. Prefer ordinary callsigns that fit one Type 1 transmission and avoid compound callsigns unless they are necessary. If a compound callsign is unavoidable, keep both chains on the same Type 2/Type 3 message pattern and verify both exact archive identities and their shared truthful grid-4 before the experiment. [Appendix B](#sec-simultaneous-tx-setup) gives the practical setup and preflight.
````

#### Original docs/doc_en.py:480 — 2.4.1 Hardware A/B: simultaneous transmit paths

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Same-receiver, same-cycle Delta SNR removes the sequential time gap and is the strongest TX design when the two transmitter chains can be controlled. It still compares the complete documented transmit paths. Frequency-selective QRM, chain response, coupling and power error can remain. Swap the frequency positions and, where practical, cross the tested antennas or components between chains.
````

#### Original docs/doc_en.py:482 — 2.4.1 Hardware A/B: simultaneous transmit paths

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
<blockquote class="evidence-conclusion"><p>Under the documented simultaneous two-transmitter Hardware A/B setup, same-receiver, same-cycle Delta SNR and Decode Outcomes described the observed difference between the Target and Reference transmit paths for the selected receivers and geographic scope.</p></blockquote>
````

#### Original docs/doc_en.py:484 — 2.4.1 Hardware A/B: simultaneous transmit paths

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
<a id="sec-2-4-sequential"></a>
<a id="sec-2-4-why"></a>
<a id="sec-3-tx-benchmark-sequential"></a>

##### 2.4.2 Hardware A/B: sequential transmit paths

Use a deterministic schedule that assigns complete WSPR transmissions to Target and Reference phases. One transmitter switched between two RF paths is normally the strongest arrangement because callsign, frequency reference and transmitter remain common. Enter each path's actual recurrence and UTC phase, verify the physical schedule-to-path mapping without RF, and report actual power. Device-specific scheduling and switching guidance is in [Appendix C](#sec-sequential-tx-setup).

WSPRadar forms one-to-one Scheduled A/B Pairs automatically. Pair Delta remains sequential: short balanced alternation reduces but does not eliminate propagation, interference, schedule-position and switching effects. Inspect incomplete pairs and chronological behavior with the paired median. Reverse the Target and Reference schedule assignments in a confirmatory run; persistence of the physical-path advantage after the role reversal is substantially more persuasive than repetition with the same phase assignment.

<blockquote class="evidence-conclusion"><p>Under the documented deterministic schedule, Scheduled-Pair Delta SNR and one-sided pair outcomes described the observed difference between the switched Target and Reference paths for the selected receivers, times and geographic scope.</p></blockquote>
````

#### Original docs/doc_en.py:498 — 2.4.3 Reference Station / Buddy Test

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.4.3 Reference Station / Buddy Test
````

#### Original docs/doc_en.py:500 — 2.4.3 Reference Station / Buddy Test

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Use a known, separately identifiable complete Reference transmitter whose QTH, callsign, actual and reported power, equipment and operating schedule are understood. TX pairs share the same remote receiver and cycle, but Target and Reference remain distinct complete transmitting stations with their own transmitters, antennas, feedlines and installed environments. The separately entered Reference Locator may contain the same grid-4 as Target QTH; equal grid-4 does not prove physical co-location.
````

#### Original docs/doc_en.py:502 — 2.4.3 Reference Station / Buddy Test

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
When both transmit paths instead form one locally controlled A/B apparatus, select Hardware A/B. The physical arrangement, not whether two callsigns share a base, determines the design. Simultaneous Hardware A/B requires two valid exact on-air identities; if only one is available, use sequential Hardware A/B.
````

#### Original docs/doc_en.py:510 — 2.4.4 Local Median Neighborhood

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.4.4 Local Median Neighborhood
````

#### Original docs/doc_en.py:536 — 2.5.1 When to use this expert diagnostic

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Use the detector only with Benchmark evidence. Its native evidence unit is a simultaneous **Joint Spot** or, for sequential TX Hardware A/B, one **complete Scheduled Pair**. Only those units contain both Target and corrected Reference SNR and therefore a paired Delta SNR. Only Target and Only Reference outcomes remain useful diagnostic context but cannot themselves qualify an event.
````

#### Original docs/doc_en.py:549 — 2.5.2 How detection works in practice

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
1. keeps the paired observations at their native WSPR-cycle or Scheduled-Pair times;
````

#### Original docs/doc_en.py:571 — 2.5.3 Read and investigate a reported event

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
* The green **`↓ Show in Station Insights`** and **`↓ Show Drill-Down Details`** actions sit to the right of their exact path timeframe. The first selects that path, preloads Drill-Down and navigates to Station Insights for the wider run history; the second makes the same selection and preload but navigates directly to Drill-Down. Both open **`Outlier Focus`** over the complete supported pre-event baseline flank, guarded provisional episode and post-event baseline flank, clipped only to the completed analysis window; this detector-support interval may exceed 24 hours. The focused Delta SNR plot shows one actual retained Joint Spot or complete Scheduled Pair at its native time instead of a bin median, IQR or density layer. Identical `*` markers identify every native unit in the current window that individually meets both configured departure and robust-z gates as part of a reported candidate, including all such units in a multi-unit burst or episode. A muted **Focused episode** band identifies the selected reported episode. It spans that episode's reported retained-evidence interval, padded by half one native evidence-unit width at each end and clipped to the focused window so a one-unit impulse remains visible; it is neither a confidence interval nor a measurement of physical-event duration. Overlays show the expected local Delta SNR, the pre/post flank baselines over their actual support intervals, symmetric robust-z guides at 1, 2 and 3 plus the configured qualifying threshold, and the configured absolute-departure boundary for the focused episode only. Other starred candidate units may have been evaluated against different local baselines and robust spreads. These are detector guides, not confidence intervals, and crossing any one guide cannot qualify a candidate by itself. Use the underlying Target and corrected Reference SNR values and nearby one-sided outcomes to check whether the Delta SNR movement came mainly from one side, whether either signal approached the decode edge, and whether pairability changed nearby.
````

#### Original docs/doc_en.py:608 — 3.1 Judge breadth, consistency and repeatability

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* qualifying confirmed-opportunity, spot or scheduled-pair volume;
````

#### Original docs/doc_en.py:636 — 3.2 Strengthen a result through repetition and control

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
* for sequential TX Hardware A/B, reverse the Target/Reference schedule assignments;
````

#### Original docs/doc_en.py:642 — 3.2 Strengthen a result through repetition and control

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Small observed differences become more useful when they recur across stations, time periods, adjacent segments and controlled repetitions. A reversed sequential TX assignment is especially useful because it can expose schedule-, switch-path- or time-of-cycle effects that ordinary repetition leaves in the same role.
````

#### Original docs/doc_en.py:672 — 3.3 Write an evidence-matched conclusion

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
For a controlled Hardware A/B result, name the complete paths compared and any crossover or calibration. For a Reference Station / Buddy Test, state that complete installed stations and their environments were benchmarked. For a Local Neighborhood Benchmark, state the radius and changing Local Median Neighborhood Reference definition.
````

#### Original docs/doc_en.py:676 — 3.3 Write an evidence-matched conclusion

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* A **Hardware A/B Test** compares the documented local paths.
* A **Buddy Test** compares complete installed stations and their environments.
* **Local Median Neighborhood** compares the complete Target station with the median of the contributing nearby peers inside the selected radius under the observed conditions.
````

#### Original docs/doc_en.py:751 — 4.1 Workflow controls

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Configuration compatibility.** Saved files preserve the inputs and durable view choices applicable to the selected analysis. Invalid or unsupported files are rejected rather than silently reinterpreted. The formal JSON Schema is the authoritative exhaustive saved-configuration contract; [Section 8.4](#sec-8-4) gives a concise operator-facing summary of selected public identifiers. Loading or saving a configuration does not create an additional result; only the selected Performance or Benchmark analysis is run.
````

#### Original docs/doc_en.py:772 — 4.2 Question, Target and measurement-window controls

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Use the callsign or reporting identifier exactly as uploaded. In schematic form, `CALLSIGN`, `CALLSIGN/1`, `CALLSIGN/2`, `CALLSIGN/P`, `CALLSIGN/QRP` and `CALLSIGN-1` are distinct exact identities; WSPRadar does not apply hidden prefix or suffix matching. These examples describe matching syntax, not whether a particular on-air identity is assigned or permitted.
````

#### Original docs/doc_en.py:782 — 4.3 Benchmark-design controls

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
- `Hardware A/B`
- `Known Reference Station`
- `Local Neighborhood`
````

#### Original docs/doc_en.py:786 — 4.3 Benchmark-design controls

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Classic omits the **`Benchmark design`** panel entirely for `RX Performance` and `TX Performance`, because Performance has no Reference. The terminal Review panel still appears after the shared filters, scope and evidence panel; its direction-specific `Run RX Analysis` / `Run TX Analysis` action and `Save Config` remain unavailable while the Question is incomplete or while a Benchmark question has no complete Benchmark design. Performance and Benchmark are mutually exclusive result types: one run produces only the selected result. [Section 8.4](#sec-8-4) summarizes selected public machine-readable configuration, URL and export names; it is not an exhaustive field or parameter catalog.
````

#### Original docs/doc_en.py:790 — 4.3 Benchmark-design controls

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| **Is there an established Target–Reference offset?** | `No established offset — use 0.0 dB` | Guided Hardware A/B and Known Reference Station | Distinguishes no established correction, use of one established correction, and a deliberate offset-establishment run. |
````

#### Original docs/doc_en.py:792 — 4.3 Benchmark-design controls

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| **Reference callsign** | blank | Hardware A/B and Reference Station | Exact Reference reporting identity. |
| **Reference Locator** | independent grid-4 for Reference Station; derived Target grid-4 for Hardware A/B | Benchmark | Controls Reference archive matching. |
| **Neighborhood Radius (km)** | `100`; 10–250 km in 10 km steps | Local Neighborhood Benchmark | Defines the local Reference pool around Target QTH. |
| **TX A/B Method** | `Simultaneous TX` | TX Hardware A/B | Selects same-cycle two-transmitter matching or deterministic sequential pairing. |
| **Repeat Interval** | `10 min`; `4, 6, 10, 12, 20, 30, 60 min` | Sequential TX A/B | Actual recurrence of each physical path. |
| **Target Start / Reference Start** | `00 UTC` / `02 UTC`; distinct even phases below Repeat Interval | Sequential TX A/B | Assigns transmissions to Target and Reference schedule phases. |
````

#### Original docs/doc_en.py:799 — 4.3 Benchmark-design controls

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
For TX Hardware A/B, `Repeat Interval` is each path's actual recurrence, not necessarily a transmitter's displayed `Frame` value. Compare the one-hour preview with the observed on-air starts and physical switch mapping. Sequential device examples are in [Appendix C](#sec-sequential-tx-setup); pair construction is in [Sections 7.1](#sec-7-1) and [7.7](#sec-7-7) <a href="#ref-12">[Ref-12]</a>.
````

#### Original docs/doc_en.py:807 — Reference-side SNR correction sign

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
The correction applies to the Reference receive/transmit path or schedule in Hardware A/B, the known Reference Station, or each local contribution before the Local Median Neighborhood is formed.
````

#### Original docs/doc_en.py:815 — Reference-side SNR correction sign

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
A constant correction cannot repair clipping, unstable AGC, intermittent routing, frequency-dependent response or incorrect power reporting. Hardware A/B calibration should use a common input or calibrated reference plane. A geographically separated Reference Station can support only a repeatable baseline for that particular pair, band and setup — not an absolute calibration. [Appendix D](#sec-reference-snr-calibration) gives the practical procedure.
````

#### Original docs/doc_en.py:817 — Reference-side SNR correction sign

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
For Local Median Neighborhood, use `0.0 dB` when no independently justified correction has been established. A nonzero correction requires a documented reason why the same additive offset applies to the contributing Reference population under the selected conditions. Adjusting the correction until the neighborhood matches the Target does not establish calibration. A common offset cannot correct different unknown errors in individual neighboring stations.
````

#### Original docs/doc_en.py:829 — 4.4 Filters and evidence thresholds

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| **Exclude Special Callsigns Q, 0, 1** | Performance on; Benchmark off | all results | Excludes remote peer callsigns beginning with `Q`, `0` or `1`: transmitters in RX analyses and receivers in TX analyses. Target and Reference stations, including Local Neighborhood reference contributors, remain eligible under this filter. The prefix rule does not establish whether a station carries telemetry. Retain beacon/telemetry-like identities when they are part of the question; exclude them when the intended population is ordinary amateur activity. |
````

#### Original docs/doc_en.py:833 — 4.4 Filters and evidence thresholds

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| **Minimum joint evidence per station** | `1`; range 1–50 | simultaneous Benchmark | Requires repeated Joint peer-cycles before a station contributes paired Delta SNR; the same numeric floor also applies to exclusive categories. |
| **Minimum scheduled pairs per station** | `1`; range 1–50 | sequential TX A/B | Requires repeated complete scheduled pairs before a station contributes Pair Delta; one-sided pair categories use the same numeric floor. |
````

#### Original docs/doc_en.py:840 — 4.4 Filters and evidence thresholds

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
`Maximum peer distance from Target (km)` limits the analysed population after the archive rows have been retrieved, so reducing it does not avoid the archive row limit. A smaller Local Neighborhood radius and `Exclude Special Callsigns Q, 0, 1` can reduce the population retrieved for some analyses; [Section 5.6](#sec-6-6) covers oversized requests.
````

#### Original docs/doc_en.py:868 — 4.5 Map, inspector and export controls

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
The `2h` choice is therefore available for every run duration. Legacy `5m` and `15m` values remain accepted for saved-configuration and URL compatibility, but they are not offered for a new choice; an explicitly loaded valid legacy value remains selectable so it is not silently changed. Chronological aggregation never changes opportunity classification, Benchmark pairing or the fixed one-hour UTC-folded profiles. Empty Performance time or distance bins remain missing evidence rather than synthetic zero-rate observations.
````

#### Original docs/doc_en.py:870 — 4.5 Map, inspector and export controls

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Drill-Down zoom is transient and is available only for exactly one selected station. Choose **`Off`**, or a complete `1h`, `3h`, `6h`, `12h` or `24h` interval. **`Center date (UTC)`** and **`Center time (UTC)`** select the center of that interval; WSPRadar derives its exact start and end, moves the complete interval against a run boundary instead of shortening it, and lets **`← Earlier`** or **`Later →`** step by one complete selected window. The resolved bounds appear on one line as **`Selected window: {start} to {end} UTC`**. The zoom restricts the focused figures and Drill-Down table; **`Filter table`** then changes only the displayed table and never the focused plots or completed analysis. Its metric plot is deliberately not a two-minute aggregate: simultaneous Benchmark shows one actual Delta SNR dot per retained Joint Spot at its canonical cycle time; sequential TX A/B shows one actual Pair Delta SNR dot per retained complete Scheduled Pair at its planned Target-start coordinate; Performance shows the actual normalized Target SNR of each successful confirmed opportunity at its canonical cycle time. These are individual retained scientific evidence units after WSPRadar's consolidation, matching and filters, not untouched provider rows. No bin median, IQR, density background, colorbar, full-run median or UTC-hour-folded metric panel is drawn in the focused view. The companion Performance outcome or Benchmark coverage view may retain its chronological aggregation, while Segment and full-window Selected Station Evidence remain density-based aggregated views. Both Target and Reference component rows of an admitted sequential pair remain together in the table. Focused figure titles use the compact format **`DG2CAD (JN47mv) - Time Window: {start} to {end} UTC`**.
````

#### Original docs/doc_en.py:878 — 4.6 Benchmark outlier-detection controls

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Benchmark Delta SNR outlier detection is an optional expert analysis over retained native paired evidence. A native paired unit is a simultaneous **Joint Spot** or, for sequential TX Hardware A/B, one **complete Scheduled Pair**. Detection runs separately for every exact peer `callsign + locator` path and is independent of the selected Temporal Evidence display bin. One-sided evidence cannot supply a missing Delta SNR. [Section 2.5](#sec-outlier) explains operation and interpretation; [Section 7.11](#sec-7-11) defines the method formally.
````

#### Original docs/doc_en.py:926 — 5.2 Diagnose by symptom

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| **No qualifying Benchmark result remains** | Review the configured Joint-evidence or complete-Scheduled-Pair requirement, minimum qualifying stations per map segment, filters and scope. WSPRadar reports those applied requirements but does not invent observed Benchmark maxima that the pipeline did not calculate. |
| **Benchmark has no Delta SNR** | Check shared remote peers in overlapping cycles or scheduled pairs, Reference uptime, clocks, schedule mapping, joint threshold, filters and scope. |
````

#### Original docs/doc_en.py:932 — 5.2 Diagnose by symptom

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| **Unexpected Hardware A/B Delta SNR sign** | Verify physical A/B mapping, Target/Reference order, correction sign, schedule phases, actual/reported power and calibration. Reconcile one path in Drill-Down. |
````

#### Original docs/doc_en.py:934 — 5.2 Diagnose by symptom

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| **Run stops because the source result is too large** | Shorten the UTC window. `Exclude Special Callsigns Q, 0, 1` or a smaller Local Neighborhood radius can reduce relevant source queries; maximum peer distance cannot because it is applied after retrieval. |
````

#### Original docs/doc_en.py:945 — 5.3 Callsign and locator checks

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Reference Station uses exact Reference callsign plus an independent four-character Reference Locator. RX and simultaneous TX Hardware A/B derive the Reference grid-4 from Target QTH; sequential TX Hardware A/B uses the shared Target identity and distinguishes paths by schedule. Local References are selected geographically.
````

#### Original docs/doc_en.py:947 — 5.3 Callsign and locator checks

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
WSPRadar does not reconstruct a compound callsign from Type 2 and Type 3 messages and does not infer a missing locator. Check the selected data source for both exact identities and their intended shared grid-4. If one identity is missing, appears only without the required locator, or is stored under a different grid-4, simultaneous Hardware A/B cannot match it merely because another archive or map display looks correct.
````

#### Original docs/doc_en.py:965 — 5.5 How the Target-Active Gate shapes evidence

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
The gate is intentionally Target-centric. Reference uptime remains an experimental responsibility, and swapping Target and Reference can change one-sided Decode Outcomes and the eligible population. Sequential TX Hardware A/B uses deterministic scheduled pairs instead. [Section 7.3](#sec-7-3) defines the conditioning formally.
````

#### Original docs/doc_en.py:1017 — 6.3 Antenna and station-comparison lineage

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Toledo (2010): why slow alternation fails.** Sivan Toledo tested one antenna for roughly an hour and then another, finding path-SNR changes comparable with the apparent antenna difference. He concluded that this naive design could not isolate the antennas and proposed per-cycle switching or simultaneous transmissions with separate hardware. WSPRadar's deterministic interleaved TX A/B schedule follows the same practical logic: short separation reduces temporal confounding, but does not eliminate it. <a href="#ref-3">[Ref-3]</a>
````

#### Original docs/doc_en.py:1026 — 6.3 Antenna and station-comparison lineage

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Vanhamel, Machiels and Lamy (2022): conditioned simultaneous RX.** Their peer-reviewed experiment conditioned two nominally identical 160 m WSPR receiver stations and compared common remote transmissions simultaneously. This is the strongest direct precedent in this review set for RX Hardware A/B and for characterizing receive-chain offsets before interpreting antenna differences. Their propagation results also show that polarization and ionospheric effects remain coupled to reported SNR. <a href="#ref-2">[Ref-2]</a>
````

#### Original docs/doc_en.py:1031 — 6.3 Antenna and station-comparison lineage

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Zander reports about 1,000 observations per preliminary experiment, of which roughly 150–200 joint reports from 15–35 receivers were retained, with sample standard deviation near 3 dB. The paper's sub-dB statement concerns precision of an arithmetic mean under its model and sample assumptions, not traceable total accuracy. Geographic sampling, antenna directivity and unknown elevation angles remain systematic limitations. The study supports simultaneous same-receiver Delta SNR, but not WSPRadar's sequential one-transmitter design, station-balanced medians, Decode Outcomes or neighborhood References.
````

#### Original docs/doc_en.py:1048 — 6.5 What WSPRadar inherits, integrates and adds

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* Hardware A/B, Reference Station and dynamic Local Neighborhood Benchmarks;
* same-cycle or deterministic scheduled-pair matching;
````

#### Original docs/doc_en.py:1056 — 6.5 What WSPRadar inherits, integrates and adds

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Within the reviewed sources, WSPRadar's clearest specific additions are the explicit conditional Performance denominator, the paired-versus-one-sided evidence split, dynamic Local Median Neighborhood References, hierarchical station-balanced geographic aggregation and an integrated audit path across all supported designs.
````

#### Original docs/doc_en.py:1068 — 7. Scientific Methods

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
2. **Constructed evidence units:** qualifying opportunities, peer-cycles, Joint units and scheduled A/B pairs formed by WSPRadar’s eligibility and matching rules.
````

#### Original docs/doc_en.py:1078 — 7. Scientific Methods

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| $c$ | one eligible WSPR <strong class="defined-term">cycle</strong> or, for sequential TX A/B, one scheduled pair |
````

#### Original docs/doc_en.py:1096 — 7. Scientific Methods

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| RX Hardware A/B / Buddy | one remote-transmitter peer-cycle | Target active; both receivers report the same transmitter-cycle for Delta SNR | station median Delta SNR, then median across stations | complete receive paths unless chains are controlled |
| Simultaneous TX Hardware A/B / applicable Buddy or Local Benchmark | one remote-receiver peer-cycle | Target active; same receiver-cycle for paired Delta SNR | station median Delta SNR, then median across stations | power, chain and joint-decode selection |
| Sequential TX Hardware A/B | one remote receiver in one scheduled Target/Reference pair | deterministic disjoint schedule and complete in-window pair | station median Pair Delta, then median across stations | time separation and switching/schedule effects |
| Local Median Neighborhood | one Target/local-Reference peer-cycle | Target active; one contribution per active local identity | local median Reference, then station/segment Delta medians | changing uncalibrated membership |
````

#### Original docs/doc_en.py:1110 — 7.1 Data source, observation units and time model

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
WSPRadar does not classify a row as Type 1, Type 2 or Type 3 and does not join complementary extended-WSPR transmissions across cycles. Each archive row belongs to its reported cycle. In simultaneous TX Hardware A/B, the resolved Target and Reference rows must therefore occur in the same cycle; aligned Type 2 phases can pair with each other and aligned Type 3 phases can pair with each other, but WSPRadar never crosses from one phase or cycle to the next. Sequential Hardware A/B remains governed by its configured schedule instead.
````

#### Original docs/doc_en.py:1114 — 7.1 Data source, observation units and time model

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
* Performance and simultaneous Benchmark use one peer identity in one eligible WSPR cycle.
* Sequential TX A/B retains exact scheduled starts, assigns them to Target or Reference by the configured modulo schedule and forms deterministic one-to-one Target/Reference pairs for each peer. Both planned starts must lie within the run window.
* Local Neighborhood Benchmark additionally constructs a cycle/path Reference from qualifying local identities before forming Target-minus-Reference evidence.
````

#### Original docs/doc_en.py:1131 — 7.2 Identity, matching and row consolidation

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| Reference Station / Buddy | exact Target callsign + Target grid-4 | exact Reference callsign + independent Reference grid-4; remote peer identity | consolidated peer-cycle |
| RX Hardware A/B | exact Target callsign + Target grid-4 | exact Reference callsign + same derived Target grid-4; remote TX identity | consolidated peer-cycle |
| Simultaneous TX Hardware A/B | exact Target callsign + Target grid-4 | exact Reference callsign + same derived Target grid-4; remote RX identity | consolidated peer-cycle |
| Sequential TX Hardware A/B | exact shared Target callsign + Target grid-4, split by schedule | same callsign/grid-4 on Reference schedule; remote RX identity | scheduled Target/Reference pair |
| Local Neighborhood Benchmark | exact Target callsign + Target grid-4 | local identity inside radius; remote peer identity | Target/local-Reference peer-cycle |
````

#### Original docs/doc_en.py:1137 — 7.2 Identity, matching and row consolidation

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Target archive selection uses grid-4 even when a six-character QTH is configured. The full QTH remains relevant to distance, azimuth, solar elevation and local-radius geometry. Shared Hardware A/B grid-4 matching does not prove physical co-location.
````

#### Original docs/doc_en.py:1141 — 7.2 Identity, matching and row consolidation

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
If several qualifying non-identical rows represent one logical side/peer/cycle identity, WSPRadar retains the strongest qualifying normalized SNR as the best observed value for that logical identity. This prevents exact repeats or weaker secondary decodes from lowering the retained side value, but it is not a representative central value for one physical receiver. Different multi-receiver/reporting behavior on the two sides can therefore introduce asymmetry. Local Median Neighborhood instead forms a median within each local identity before aggregating across identities.
````

#### Original docs/doc_en.py:1147 — 7.2 Identity, matching and row consolidation

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
The strongest-report rule applies to Performance SNR values, both endpoints of simultaneous fixed-Reference Benchmark, and the Target side of Local Median Neighborhood. Local Reference contributors retain their within-identity medians and subsequent median across identities; Sequential TX A/B retains its per-side medians within scheduled comparison pairs. These distinct constructions are defined in [Section 7.7](#sec-7-7). Medians and IQR across retained observations remain summaries of the resulting evidence, separate from choosing one SNR value within a cycle/path.
````

#### Original docs/doc_en.py:1159 — 7.3 Target-active conditioning and eligibility

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Performance and simultaneous Benchmark condition on $A_c=1$. This protects known Target downtime from becoming automatic counter-evidence, but it changes the analysis population: the result describes cycles in which Target participation was observable, not all clock time or all planned attempts.
````

#### Original docs/doc_en.py:1163 — 7.3 Target-active conditioning and eligibility

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Every Joint observation already implies Target participation, so the gate does not change Joint-only Delta SNR values. It changes the population of one-sided/asynchronous outcomes and, in Performance, the opportunity denominator. Sequential TX A/B uses deterministic scheduled eligibility rather than the simultaneous Target-Active Gate.
````

#### Original docs/doc_en.py:1255 — 7.6 Paired evidence, Decode Outcomes and missingness

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
`Both (Async)` means that an identity has retained evidence from both sides but lacks a qualifying same-cycle or scheduled pair for the relevant station category. It indicates broader two-sided participation without contributing paired Delta SNR.
````

#### Original docs/doc_en.py:1290 — 7.7 Aggregation hierarchy and weighting

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
For every Benchmark design, a station is one exact `callsign + full reported locator` identity for both weighting and segment support. Each identity must separately meet the configured minimum Joint-evidence count, or minimum complete Scheduled-Pair count for sequential TX A/B. The identities contributing one peer median each are exactly the identities counted toward the minimum qualifying stations per map segment. Identities with only one-sided evidence do not contribute to this Delta-SNR support count. The same callsign at different full locators counts separately, including two locators in the same grid-4. This counts reported path identities; it does not establish independent physical stations or sites.
````

#### Original docs/doc_en.py:1294 — 7.7 Aggregation hierarchy and weighting

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
**Sequential TX A/B**

1. Retain exact-identity reports matching Target or Reference schedule phases.
2. Pair planned starts one-to-one by nearest cyclic separation under the common Repeat Interval.
3. Require both planned starts to lie within the run window.
4. Within each peer and scheduled pair, calculate a micro-median for each side.
5. Calculate Pair Delta when both micro-medians exist; otherwise retain the pair as one-sided evidence.
6. Apply the minimum complete-pair count per peer.
7. Calculate peer and segment medians as above.

The micro-median protects a scheduled side from duplicate-like repeated rows but does not make the two sequential transmissions simultaneous.

<p style="page-break-after: avoid; -pdf-keep-with-next: true;"><strong>Local Median Neighborhood</strong></p>
````

#### Original docs/doc_en.py:1364 — 7.8.2 Benchmark evidence coverage

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Under the Target-Active Gate, Only Target and Only Reference are directional and asymmetric. Sequential TX A/B instead uses deterministic complete or one-sided scheduled pairs, but a one-sided pair still has no Pair Delta.
````

#### Original docs/doc_en.py:1371 — 7.8.3 Temporal summaries and UTC folding

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Offered chronological widths are governed by the complete run duration, not by the observed evidence span: runs through 6 hours default to `10m`; longer runs through 24 hours default to `30m`; runs longer than 24 hours default to `12h`. The offered sets are listed in [Section 4.5](#sec-5-5), including the `2h` choice in every duration tier. An explicitly loaded valid legacy `5m` or `15m` choice is preserved without making those widths normal new choices.
````

#### Original docs/doc_en.py:1387 — 7.8.3 Temporal summaries and UTC folding

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Benchmark temporal Delta SNR uses retained Joint observations or complete scheduled pairs. If no paired values remain, the Delta SNR panel still shows the full selected UTC window and states that paired Δ SNR evidence is absent. This means no retained Joint observation or complete scheduled pair remains in the displayed scope; it does not by itself mean that the data source returned no observations, and temporal coverage can still show one-sided outcomes. Chronological bins summarize raw paired values in actual time; UTC-hour bins summarize the same paired population by hour across dates represented by retained Benchmark evidence. Benchmark temporal coverage uses all retained Only Target, Joint and Only Reference units and the two Joint Evidence Share summaries above. Benchmark folding likewise requires at least two represented evidence dates.
````

#### Original docs/doc_en.py:1403 — 7.8.4 Selected-path summaries

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
For Benchmark, the selected path reports observation-level Delta SNR for each Joint unit or complete scheduled pair and separately reports Only Target, Joint and Only Reference coverage. Changing the selected path or display bin changes only the retained-evidence view, not matching, eligibility or aggregation upstream.
````

#### Original docs/doc_en.py:1405 — 7.8.4 Selected-path summaries

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Drill-Down can temporarily restrict this same selected-path evidence to one centered `1h`, `3h`, `6h`, `12h` or `24h` interval before ordinary table filters run. Its focused metric recipe retains one scientific unit at its native coordinate: one consolidated Joint Spot and actual Delta SNR at canonical cycle UTC for simultaneous Benchmark; one complete Scheduled Pair and actual Pair Delta SNR at planned Target-start UTC for sequential TX A/B; or one successful confirmed opportunity and actual normalized Target SNR at canonical cycle UTC for Performance. Thus “native” describes processed retained evidence after consolidation, matching and scientific filters, not untouched provider rows. The focused metric recipe contains neither temporal-bin medians or quartiles nor a density grid, colorbar, full-run median or folded profile. Companion outcome/coverage panels may retain their chronological aggregation, and the segment and full-window selected-path recipes remain unchanged density summaries. Sequential membership still keeps both Target and Reference component rows of each admitted pair together in the table.
````

#### Original docs/doc_en.py:1442 — 7.9 Geography, solar classification and population filters

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Solar classification uses solar elevation at Target QTH. Same-cycle evidence uses the cycle timestamp. Scheduled TX A/B uses the midpoint between the planned Target and Reference starts so one pair cannot be split across solar classes.
````

#### Original docs/doc_en.py:1457 — 7.10 Dependence, uncertainty and validation scope

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* **evidence depth:** number of opportunities, Joint units or scheduled pairs;
````

#### Original docs/doc_en.py:1475 — 7.11 Robust local-baseline Delta SNR event detection

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| $u$ | one native paired unit: a same-cycle Joint Spot or complete Scheduled Pair |
````

#### Original docs/doc_en.py:1627 — 8.1 Claim classes and evidence-matched wording

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| **Component attribution** | A difference associated with a local path or component. | Controlled Hardware A/B, calibration and preferably crossover/reversal. |
````

#### Original docs/doc_en.py:1637 — 8.1 Claim classes and evidence-matched wording

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* **Local Neighborhood Benchmark** supports descriptions of how the complete Target station compared with the contributing nearby peers under the selected conditions. Its Reference changes with the qualifying observations, radius, remote path and cycle. It is neither a permanent station ranking nor a calibrated antenna comparison.
````

#### Original docs/doc_en.py:1676 — 8.2 Interpretation boundaries

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
* sequential TX remains time-separated;
````

#### Original docs/doc_en.py:1854 — Part IV: Practical Supplements

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
This part collects parallel WSJT-X setup for simultaneous receive paths, the limitation of WSJT-X for sparse synchronized transmit tests, practical simultaneous and sequential TX Hardware A/B procedures, Reference-side calibration and the project license. Use the sections that apply to your station and experiment.
````

#### Original docs/doc_en.py:1859 — Appendix A: Parallel WSJT-X Instances for Simultaneous RX

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
This procedure creates a second isolated WSJT-X instance for a simultaneous RX Hardware A/B Test on Windows. The current WSJT-X guide documents `--rig-name` as the supported way to isolate each instance's settings and writable files. WSJT-X versions and installation paths can change, so verify the current guide if your menus differ. <a href="#ref-12">[Ref-12]</a>
````

#### Original docs/doc_en.py:1908 — Appendix B: Simultaneous TX Hardware A/B Setup

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
### Appendix B: Simultaneous TX Hardware A/B Setup
````

#### Original docs/doc_en.py:1919 — B.1 Choose the callsigns

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Enter the two exact archive identities as Target and Reference and use the same truthful test-QTH grid-4 for both. If two valid identities are not available, use the sequential Hardware A/B method in [Appendix C](#sec-sequential-tx-setup), which distinguishes the two RF paths by schedule while retaining one callsign.
````

#### Original docs/doc_en.py:1958 — B.4 Verify WSPRnet and the selected archive

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Do not start the measurement window until both exact callsigns appear consistently in the shared grid-4 and common receivers report both signals in the intended cycles. A successful preflight applies only to the tested combination of transmitters, firmware, decoders and data source.
````

#### Original docs/doc_en.py:1981 — B.5.1–B.5.2 QMX and QMX+ Virtual U3S, and Ultimate3S

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| Scheduled pair | Target RF position | Reference RF position |
````

#### Original docs/doc_en.py:2044 — B.6 Confirm by exchange or crossover

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
<a id="sec-sequential-tx-setup"></a>
### Appendix C: Sequential TX A/B Scheduling and Switching

This appendix collects the practical schedule and switching guidance behind the TX Hardware A/B playbook. Exact UI controls are in [Section 4.3](#sec-5-3), and exact scheduled-pair construction is in [Sections 7.1](#sec-7-1) and [7.7](#sec-7-7).

<a id="sec-b-1"></a>
<a id="sec-sequential-tx-setup-1"></a>
#### C.1 Requirements for a valid scheduled experiment

For sequential TX A/B antenna tests, one transmitter feeding two RF paths through a controlled switch is normally preferable to two independent transmitters. Transmitter, frequency reference, WSPR chain, callsign, power setting and timing remain common.

Use one normal valid callsign for both paths and identify the paths through different deterministic UTC phases. Enter the transmissions that actually occur on each RF path:

* `Repeat Interval` is each path's actual recurrence, not necessarily a transmitter's displayed `Frame` value.
* `Target Start` and `Reference Start` are different even UTC phases below that interval.
* Use the shortest practical separation compatible with reliable operation and an acceptable duty cycle.
* Report actual power; do not encode path identity through false dBm values.
* Verify clock synchronization and the physical schedule-to-path mapping before transmitting.

A deterministic scheduler or controller is required. Standard randomized WSJT-X transmit-percentage operation does not create a fixed A/B sequence.

<a id="sec-b-2"></a>
<a id="sec-sequential-tx-setup-2"></a>
#### C.2 WSPRadar Timed A/B Relay Switch

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
<a id="sec-sequential-tx-setup-3"></a>
#### C.3 Ultimate3S schedule example

The QRP Labs Ultimate3S can run a sequence of WSPR entries and apply a per-entry `Aux` output to external path-switching hardware. When a two-entry sequence begins at `00`, a global 10-minute frame can use Target at `00`, Reference at `02`, then pause until the next sequence at `10`; in WSPRadar this is `Repeat Interval = 10`, `Target Start = 00`, `Reference Start = 02`. The same arrangement with a 20-minute global frame gives each path a 20-minute recurrence while retaining two-minute A/B separation.

The Ultimate3S manual documents `Start = 00` specially as "not used", so verify the displayed and observed UTC sequence and enter its actual phases rather than assuming a literal setting-to-time mapping. The `Aux` lines share display signals; use the documented filtered driver or relay interface and switch only in the RF-off interval <a href="#ref-12">[Ref-12]</a>.

<a id="sec-b-4"></a>
<a id="sec-sequential-tx-setup-4"></a>
#### C.4 QMX schedule examples

One QMX with `Frame = 10`, `Start = 0` transmits at `00, 10, 20, 30, 40, 50`. If an external switch alternates those transmissions between paths, Target is `00, 20, 40` and Reference is `10, 30, 50`; each path repeats every 20 minutes. Enter `Repeat Interval = 20`, `Target Start = 00`, `Reference Start = 10`; do not enter `10 / 00 / 02`.

A single QMX cannot produce an adjacent `00/02` pair followed by an eight-minute pause with that beacon scheduler. It can alternate adjacent paths only by transmitting every two minutes, which the QMX manual discourages as antisocial network use. Two independently scheduled QMX units with `Frame = 10`, Starts `00` and `02`, do implement WSPRadar's `10 / 00 / 02` schedule, but their transmitter chains and actual powers must be controlled as separate hardware <a href="#ref-12">[Ref-12]</a>.

<a id="sec-b-5"></a>
<a id="sec-sequential-tx-setup-5"></a>
#### C.5 Verify mapping and preserve the experiment

Before transmitting:

* test without RF power;
* verify Target and Reference path polarity;
* verify no transition occurs during a WSPR transmission;
* use a dummy load or low-power continuity/SWR test;
* document relay channel, polarity, lead time, actual on-air schedule, schedule assignment and path mapping.

Switch loss, isolation, connectors, feedline differences and antenna surroundings remain part of the result. Swapping antennas between switch paths can help separate antenna effects from path effects. Repeating the experiment with reversed schedule assignments can help expose timing or role-dependent effects.

<div style="page-break-before: always;"></div>

<a id="sec-c"></a>
````

#### Original docs/doc_en.py:2152 — Appendix D: Reference SNR Calibration

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
### Appendix D: Reference SNR Calibration
````

### DE

- Original SHA-256: `6aa3b6fc5b284eaea63aa76908b43c32fc8a08f122bb220e143134575a4b6753`
- Integrated SHA-256: `7fc2c58d20d8d6aa7965479909289ae8a45b51c9ba1cd8585a25b87a7f11fb78`

# docs/doc_de.py
### 0. Warum WSPRadar?
#### 0.0 WSPR in 2 Minuten
#### 0.1 Was WSPRadar zeigen kann
#### 0.2 Was ein Lauf liefert
#### 0.3 Der erste sinnvolle Lauf
### Inhaltsverzeichnis
## Teil I: Leitfaden für den Funkbetrieb
### 1. Analyse auswählen und vorbereiten
#### 1.1 Solide Versuchsgrundlage schaffen
#### 1.2 Die zur Fragestellung passende Analyse wählen
#### 1.3 Dem Evidenzpfad folgen
### 2. Analyse durchführen und auswerten
#### 2.1 RX Performance
#### 2.2 TX Performance
#### 2.3 RX Benchmark
##### 2.3.1 Referenzaufbau/-station
##### 2.3.2 Referenznachbarschaft
#### 2.4 TX Benchmark
##### 2.4.1 Referenzaufbau/-station
##### 2.4.2 Referenznachbarschaft
#### 2.5 Vorübergehende ΔSNR-Abweichungen finden und prüfen
##### 2.5.1 Wann dieses Diagnosewerkzeug sinnvoll ist
##### 2.5.2 Wie die Erkennung praktisch arbeitet
##### 2.5.3 Ein berichtetes Ereignis lesen und untersuchen
##### 2.5.4 Selektivität anpassen und Ergebnis sichern
### 3. Ergebnis absichern und kommunizieren
#### 3.1 Breite, Konsistenz und Wiederholbarkeit beurteilen
#### 3.2 Ergebnis durch Wiederholung und Kontrolle absichern
#### 3.3 Evidenzgerechte Schlussfolgerung formulieren
#### 3.4 Lauf und Kontext sichern
## Teil II: Bedienelemente und Fehlersuche
### 4. Bedienelemente und Konfiguration
#### 4.1 Ablaufsteuerung
#### 4.2 Frage, Target und Messzeitraum
#### 4.3 Benchmark-Design und -Einstellungen
##### Vorzeichen der referenzseitigen SNR-Korrektur
#### 4.4 Filter und Evidenzschwellen
#### 4.5 Karten-, Inspektor- und Exporteinstellungen
#### 4.6 Bedienelemente der Benchmark-Ausreißererkennung
### 5. Fehlersuche und Datenqualität
#### 5.1 Zuerst die Laufdefinition prüfen
#### 5.2 Fehler nach Symptom eingrenzen
#### 5.3 Rufzeichen und Locator prüfen
#### 5.4 Fallback für historische Decode-Codes
#### 5.5 Wie das Target-Active Gate die Evidenz prägt
#### 5.6 Umgang mit Upstream-Daten
## Teil III: Wissenschaftliche Grundlagen, Methoden und Aussagen
### 6. Literatur, Vorarbeiten und Einordnung
#### 6.1 Vom Meldenetz zum Versuchsdatensatz
#### 6.2 WSPR-Beobachtungsdaten interpretierbar machen
#### 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen
#### 6.4 Analyseinfrastruktur und verwandte Werkzeuge
#### 6.5 Was WSPRadar übernimmt, integriert und ergänzt
### 7. Wissenschaftliche Methoden
#### 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell
#### 7.2 Identität, Zuordnung und Zeilenkonsolidierung
#### 7.3 Konditionierung auf Target-Aktivität und Zulässigkeit
#### 7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen
#### 7.5 Leistungsnormierung, Korrektur und Benchmark-Delta-SNR
#### 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen
#### 7.7 Aggregationshierarchie und Gewichtung
#### 7.8 Geografische, zeitliche und funkwegbezogene Zusammenfassungen
##### 7.8.1 Geografische Zusammenfassungen
##### 7.8.2 Abdeckung der Benchmark-Evidenz
##### 7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung
##### 7.8.4 Zusammenfassungen für den ausgewählten Funkweg
##### 7.8.5 Deskriptive Streuung und Visualisierungstransformationen
#### 7.9 Geografie, Sonnenstandsklassifikation und Populationsfilter
#### 7.10 Abhängigkeit, Unsicherheit und Geltungsbereich der Validierung
#### 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie
### 8. Evidenzgerechte Aussagen und Reproduzierbarkeit
#### 8.1 Aussageklassen und evidenzgerechte Formulierungen
#### 8.2 Interpretationsgrenzen
#### 8.3 Checkliste für Berichterstattung und Reproduzierbarkeit
#### 8.4 Exportpaket der Analyse
#### 8.5 Haftungsausschluss
### Literatur und Quellen
## Teil IV: Praktische Ergänzungen
### Anhang A: Parallele WSJT-X-Instanzen für simultanes RX
#### A.1 Zweite Instanz anlegen
#### A.2 Ausgangskonfiguration bei Bedarf kopieren
#### A.3 Alle Datenpfade trennen
#### A.4 Grenzen von WSJT-X für simultanes TX
### Anhang B: Simultanes TX Referenzaufbau/-station praktisch einrichten
#### B.1 Rufzeichen auswählen
#### B.2 Zeitplan angleichen und Signale trennen
#### B.3 Leistung und simultane Signalqualität prüfen
#### B.4 WSPRnet und ausgewählte Datenquelle prüfen
#### B.5 Gerätespezifische Einrichtung
##### B.5.1–B.5.2 QMX und QMX+ Virtual U3S sowie Ultimate3S
##### B.5.3 ZachTek-Firmware 2.19: Zufallswahl in getrennten Frequenzfenstern
#### B.6 Durch Tausch oder Kreuztausch bestätigen
### Anhang C: Referenz-SNR-Kalibrierung
### Lizenz

### Verbatim original passages changed or retired (de)

Each source span below is preserved verbatim from the accepted original. Its heading gives the original source line and nearest section; the disposition follows the scope table above. A changed span may contain retained material that was moved or rephrased solely to integrate the approved contract.

#### Original docs/doc_de.py:70 — 0.1 Was WSPRadar zeigen kann

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| <span class="analysis-choice"><span class="analysis-family">RX Benchmark</span><br><strong class="analysis-variant">Hardware A/B</strong></span> | Unterschieden sich zwei lokale Empfangspfade beim gleichzeitigen Beobachten derselben entfernten Aussendungen? | Zwei Antennen vergleichen, die jeweils eine eigene simultane Empfänger- und Decoderkette speisen, wobei das Ergebnis zunächst die vollständigen Empfangspfade beschreibt; einen Unterschied nur dann gezielt den Antennen zuschreiben, wenn die übrigen Ketten abgeglichen, charakterisiert oder durch einen Kreuztausch bestätigt wurden; eine Antenne über einen charakterisierten Verteiler an zwei Empfänger führen, um Empfänger oder Decoderpfade zu vergleichen; Vorverstärker, Filter, Speiseleitung oder Mantelwellensperre nur in einen ansonsten kontrollierten Pfad einfügen und die beiden dokumentierten vollständigen Empfangspfade benchmarken. |
| <span class="analysis-choice"><span class="analysis-family">TX Benchmark</span><br><strong class="analysis-variant">Hardware A/B</strong></span> | Unterschieden sich zwei lokale Sendepfade bei simultanem oder eng getaktetem Betrieb? | Zwei Antennen über getrennte, kalibrierte Sendeketten speisen und mit synchronisierten Zyklen, unterscheidbaren Signalen und ausreichender Entkopplung gleichzeitig senden; einen Sender über einen kontrollierten HF-Umschalter nach festem UTC-Zeitplan abwechselnd auf zwei Antennen schalten; zwei Speiseleitungen, Anpassnetzwerke, Filter oder vollständige Sendepfade vergleichen und dabei tatsächliche Leistung, Zeitsteuerung und die übrige Kette kontrollieren. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Referenzstation / Buddy-Test</strong></span> | Wie schneidet meine vollständige Station gegenüber einer bekannten Station ab? | <strong>RX:</strong> den eigenen Empfänger mit dem bekannten Empfänger eines Funkfreunds vergleichen, während beide in denselben Zyklen dieselben entfernten Sender beobachten; <strong>TX:</strong> den eigenen Sender mit dem Sender eines Funkfreunds an denselben entfernten Empfängern und in denselben Zyklen vergleichen; ein stabiles, gut verstandenes Buddy-Design vor und nach dokumentierten Stationsarbeiten als relative Basislinie für die Gesamtstation wiederholen, ohne die Buddy-Station als absolut kalibrierten Standard zu behandeln. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Lokaler Nachbarschafts-Median</strong></span> | Wie schneidet meine vollständige Station gegenüber den beobachteten WSPR-Peers in der Umgebung ab? | Prüfen, ob die eigene Empfangs- oder Sendestation insgesamt über, nahe oder unter dem zyklus- und funkwegspezifischen Median der qualifizierenden beobachteten lokalen Peers im gewählten Radius liegt; eine Station in Betrieb nehmen, wenn keine einzelne geeignete Buddy-Referenz verfügbar ist; Richtungen, Entfernungen oder UTC-Zeiträume erkennen, in denen die Station von dieser kontextbezogenen lokalen Basislinie abweicht, und dabei Zusammensetzung der Nachbarschaft sowie Radiusabhängigkeit prüfen. Verglichen werden vollständige Stationen unter den beobachteten Bedingungen; daraus ergeben sich weder isolierter Antennengewinn noch eine Rangliste aller Stationen in der Umgebung. |
````

#### Original docs/doc_de.py:75 — 0.1 Was WSPRadar zeigen kann

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Die Referenz ist Bestandteil der wissenschaftlichen Fragestellung und nicht nur eine Darstellungsoption. Ein kontrollierter <strong class="defined-term">Hardware-A/B-Test</strong> bietet die stärkste Grundlage, einen beobachteten Unterschied lokalen Pfaden oder Bauteilen zuzuordnen – allerdings nur in dem Maß, in dem die übrigen Ketten kontrolliert sind. Ein <strong class="defined-term">Referenzstations-/Buddy-Test</strong> vergleicht zwei vollständig aufgebaute Stationen einschließlich QTH, Geräten, Gelände sowie lokaler Stör- und Rauschumgebung. Nachbarschafts-Benchmarks liefern wechselnde kontextbezogene Basislinien und keine festen oder kalibrierten Standards.
````

#### Original docs/doc_de.py:93 — 0.2 Was ein Lauf liefert

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Die Karte liefert den geografischen Überblick. Evidenz auf Segmentebene zeigt, wie sich die Beobachtung nach Entfernung und Richtung verändert und wie viel Unterstützung dahintersteht. Performance- beziehungsweise Benchmark-Evidenz trennt das Hauptergebnis von seiner ergänzenden Evidenz. Zeitliche Evidenz zeigt, ob sich das Muster während des Laufs veränderte oder zu bestimmten UTC-Stunden wiederkehrte. Station Insights legt offen, welche Stationsidentitäten beitragen. Die Evidenz der ausgewählten Station verfolgt einen exakten Funkweg; Drill-Down zeigt die Beobachtungen, Vergleiche desselben Zyklus oder geplanten A/B-Paare hinter den Zusammenfassungen.
````

#### Original docs/doc_de.py:135 — Inhaltsverzeichnis

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
        * [2.3.1 Hardware A/B: simultane Empfangspfade](#sec-3-rx-benchmark-hardware)
        * [2.3.2 Referenzstation / Buddy-Test](#sec-3-rx-benchmark-buddy)
        * [2.3.3 Lokaler Nachbarschafts-Median](#sec-3-rx-benchmark-local-median)
````

#### Original docs/doc_de.py:139 — Inhaltsverzeichnis

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
        * [2.4.1 Hardware A/B: simultane Sendepfade](#sec-3-tx-benchmark-simultaneous)
        * [2.4.2 Hardware A/B: sequenzielle Sendepfade](#sec-3-tx-benchmark-sequential)
        * [2.4.3 Referenzstation / Buddy-Test](#sec-3-tx-benchmark-buddy)
        * [2.4.4 Lokaler Nachbarschafts-Median](#sec-3-tx-benchmark-local-median)
````

#### Original docs/doc_de.py:211 — Inhaltsverzeichnis

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* [Anhang B: Simultanes TX Hardware A/B praktisch einrichten](#sec-simultaneous-tx-setup)
````

#### Original docs/doc_de.py:220 — Inhaltsverzeichnis

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
* [Anhang C: Sequenzielle TX-A/B-Zeitplanung und Umschaltung](#sec-sequential-tx-setup)
    * [C.1 Anforderungen an einen gültigen zeitgesteuerten Versuch](#sec-sequential-tx-setup-1)
    * [C.2 Zeitgesteuerter WSPRadar-A/B-Relaisumschalter](#sec-sequential-tx-setup-2)
    * [C.3 Zeitplanbeispiel für Ultimate3S](#sec-sequential-tx-setup-3)
    * [C.4 Zeitplanbeispiele für QMX](#sec-sequential-tx-setup-4)
    * [C.5 Zuordnung prüfen und Versuch dokumentieren](#sec-sequential-tx-setup-5)
* [Anhang D: Referenz-SNR-Kalibrierung](#sec-reference-snr-calibration)
````

#### Original docs/doc_de.py:275 — 1.2 Die zur Fragestellung passende Analyse wählen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* **Hardware A/B** ist das stärkste Design für eine Frage zu einem lokalen Bauteil oder Signalpfad. Es isoliert dieses Bauteil jedoch nur in dem Maß, in dem die übrigen Pfade kontrolliert sind.
* **Referenzstation / Buddy-Test** vergleicht vollständig aufgebaute Stationen und ihre Betriebsumgebungen.
````

#### Original docs/doc_de.py:280 — 1.2 Die zur Fragestellung passende Analyse wählen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* **Lokaler Nachbarschafts-Median** vergleicht deine vollständige Empfangs- oder Sendestation mit einer wechselnden Referenz aus qualifizierenden WSPR-Beobachtungen der Umgebung innerhalb des ausgewählten Radius. Die Referenz wird für jede entfernte Station und jeden WSPR-Zyklus getrennt berechnet.
````

#### Original docs/doc_de.py:319 — 1.3 Dem Evidenzpfad folgen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Drill-Down.** Prüfe die beibehaltenen Gelegenheiten, Vergleiche desselben Zyklus oder geplanten Paare hinter dem Ergebnis. Nutze Drill-Down, um Identitäten, Locatorwechsel, Zeitsteuerung, einseitige Evidenz und einzelne Ausreißer nachzuvollziehen.
````

#### Original docs/doc_de.py:417 — 2.3.1 Hardware A/B: simultane Empfangspfade

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.3.1 Hardware A/B: simultane Empfangspfade
````

#### Original docs/doc_de.py:419 — 2.3.1 Hardware A/B: simultane Empfangspfade

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Verwende dieses Design für zwei lokale Antennen, Speiseleitungen, Filter, Vorverstärker, Empfänger oder vollständige Empfangsketten, die gleichzeitig am selben physischen Test-QTH betrieben werden. Target und Referenz benötigen unterschiedliche exakte Melderufzeichen und dasselbe Target-Grid-4. Komponenten, die gemeinsam sein sollen, müssen physisch gemeinsam genutzt werden; die Zuordnung zum selben Grid-4 beweist weder Ko-Lokation noch Gleichheit der Pfade.
````

#### Original docs/doc_de.py:421 — 2.3.1 Hardware A/B: simultane Empfangspfade

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Dies ist das stärkste RX-Design, um einen Unterschied einem lokalen Pfad zuzuordnen. Sofern Unterschiede bei Empfänger, Audio, Verstärkung, Decoder und Signalführung nicht charakterisiert wurden, vergleicht das Ergebnis weiterhin die vollständigen dokumentierten Empfangspfade. Eine breite, wiederkehrende Delta-SNR-Verschiebung zusammen mit dazu passender einseitiger Evidenz stützt die Aussage, dass ein Pfad unter den geprüften Bedingungen besser abschnitt. Eine Kalibrierung mit gemeinsamem Eingang, ein Tausch der Verteilerausgänge oder ein Hardware-Kreuztausch ist die nützlichste Bestätigung, weil dadurch das Prüfobjekt von einem dauerhaften Kettenoffset getrennt werden kann. [Anhang D](#sec-reference-snr-calibration) beschreibt die Referenz-SNR-Kalibrierung.
````

#### Original docs/doc_de.py:423 — 2.3.1 Hardware A/B: simultane Empfangspfade

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
<blockquote class="evidence-conclusion"><p>Unter dem dokumentierten simultanen RX-Hardware-A/B-Aufbau beschrieben gepaartes Delta SNR und Decode Outcomes den beobachteten Unterschied zwischen Target- und Referenzempfangspfad für die gemeinsamen Sender, Zyklen und den ausgewählten geografischen Bereich.</p></blockquote>
````

#### Original docs/doc_de.py:427 — 2.3.2 Referenzstation / Buddy-Test

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.3.2 Referenzstation / Buddy-Test
````

#### Original docs/doc_de.py:429 — 2.3.2 Referenzstation / Buddy-Test

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Verwende eine bekannte, separat identifizierbare vollständige Referenz-Empfangsstation, deren QTH, Rufzeichen, Ausrüstung, Betriebsplan und lokale Umgebung bekannt und nachvollziehbar sind. RX-Paare teilen denselben entfernten Sender und denselben Zyklus; Target und Referenz bleiben jedoch eigenständige vollständige Empfangsstationen mit jeweils eigenen Antennen, Geräten, Signalwegen und lokalen Störumgebungen. Der getrennt eingegebene Referenz-Locator darf dasselbe Grid-4 wie das Target-QTH enthalten; gleiches Grid-4 beweist keine physische Ko-Lokation.
````

#### Original docs/doc_de.py:437 — 2.3.3 Lokaler Nachbarschafts-Median

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.3.3 Lokaler Nachbarschafts-Median
````

#### Original docs/doc_de.py:453 — 2.4 TX Benchmark

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Beantwortete Frage.** Wie unterschied sich der Target-Sender beziehungsweise der geplante Target-Pfad von der ausgewählten Referenz an gemeinsamen entfernten Empfängern?
````

#### Original docs/doc_de.py:455 — 2.4 TX Benchmark

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
**Gemeinsame TX-Benchmark-Evidenz.** Ein TX-Benchmark im selben Zyklus vergleicht Target und Referenz am selben entfernten Empfänger im selben WSPR-Zyklus. Sequenzielles Hardware A/B verwendet stattdessen deterministische geplante Paare am selben Empfänger. Erfolgreiches TX-SNR wird vor der Bildung des Delta SNR auf die gemeldete Leistung normiert; das Ergebnis hängt daher unmittelbar von korrekten Leistungsangaben ab. Decode Outcomes bewahren Joint- und einseitige Evidenz. Eine exklusive Beobachtung besitzt jedoch kein SNR der fehlenden Seite und wird nicht als Paar leistungsnormiert.
````

#### Original docs/doc_de.py:457 — 2.4 TX Benchmark

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Dem Evidenzpfad folgen.** Auf der **Karte** fasst die Sektorfarbe das stationsgleichgewichtete mediane Delta SNR über entfernte Empfänger zusammen. Marker- und Kartenfußkategorien zeigen Joint- und einseitige Empfängerevidenz. Lies jeden Sektor zusammen mit der Breite über Empfänger sowie der Tiefe durch Spots oder geplante Paare.
````

#### Original docs/doc_de.py:459 — 2.4 TX Benchmark

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Vergleiche im **Segment-Inspektor** die stationsbezogenen Decode Outcomes mit der Zusammensetzung auf Beobachtungs- beziehungsweise Paarebene. Stationsmediane geben jedem entfernten Empfänger eine gleich große Stimme; die Delta-SNR-Verteilung der Joint Spots oder geplanten Paare zeigt die vollständige gepaarte Beobachtungspopulation. Eine Verschiebung über viele Empfänger ist andere Evidenz als ein Ergebnis, das von wenigen Empfängern mit hohem Datenvolumen dominiert wird.
````

#### Original docs/doc_de.py:461 — 2.4 TX Benchmark

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Die **Zeitliche Evidenz** zeigt, ob sich Delta SNR im Verlauf des Laufs veränderte oder nach UTC-Stunde wiederkehrte. Die Abdeckung der Benchmark-Evidenz zeigt, ob die gepaarte Evidenz während dieser Zeiten breit blieb. Prüfe beim sequenziellen TX, ob das Ergebnis an eine Zeitplanphase oder Schaltperiode gebunden ist; prüfe beim simultanen TX, ob es vor allem an einem Empfänger, einer Audiofrequenzzuordnung oder einem kurzen Zeitraum auftritt.
````

#### Original docs/doc_de.py:463 — 2.4 TX Benchmark

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Lies in **Station Insights** das mediane Delta SNR jedes Empfängers zusammen mit seinen Joint- und einseitigen Anzahlen. Die **Evidenz der ausgewählten Station** legt das gepaarte Ergebnis und die Evidenzabdeckung an einem Empfängerpfad offen. **Drill-Down** prüft Empfängeridentität, gemeldete Leistungen, Paarbildung im selben Zyklus oder Zuordnung geplanter Paare sowie das Vorzeichen der Korrektur.
````

#### Original docs/doc_de.py:467 — 2.4 TX Benchmark

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
**Grenze und Bestätigung.** TX Benchmark bleibt auf paarbare Evidenz und korrekte Leistungsangaben konditioniert. Simultane Designs behalten Unterschiede der Sendeketten bei Leistung, Frequenzgang, Entkopplung und Kopplung bei. Sequenzielle Designs bleiben zeitlich getrennt. Einseitige Evidenz im selben Zyklus wird außerdem vom Target-Active Gate beeinflusst. Stärke das Ergebnis durch breite Empfängerunterstützung, genaue Leistungsmessung, Wiederholung und die nachfolgend beschriebenen methodenspezifischen Kontrollen.
````

#### Original docs/doc_de.py:473 — 2.4.1 Hardware A/B: simultane Sendepfade

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.4.1 Hardware A/B: simultane Sendepfade
````

#### Original docs/doc_de.py:477 — 2.4.1 Hardware A/B: simultane Sendepfade

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Delta SNR am selben Empfänger und im selben Zyklus beseitigt den zeitlichen Abstand des sequenziellen Designs und ist das stärkste TX-Design, wenn beide Sendeketten kontrolliert werden können. Verglichen werden dennoch die vollständigen dokumentierten Sendepfade. Frequenzselektives QRM, Kettenfrequenzgang, Kopplung und Leistungsfehler können bestehen bleiben. Tausche die Frequenzpositionen und führe nach Möglichkeit einen Kreuztausch der geprüften Antennen oder Bauteile zwischen den Ketten durch.
````

#### Original docs/doc_de.py:479 — 2.4.1 Hardware A/B: simultane Sendepfade

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
<blockquote class="evidence-conclusion"><p>Unter dem dokumentierten simultanen Hardware-A/B-Aufbau mit zwei Sendern beschrieben Delta SNR am selben Empfänger und im selben Zyklus sowie Decode Outcomes den beobachteten Unterschied zwischen Target- und Referenzsendepfad für die ausgewählten Empfänger und den geografischen Bereich.</p></blockquote>

<a id="sec-2-4-sequential"></a>
<a id="sec-2-4-why"></a>
<a id="sec-3-tx-benchmark-sequential"></a>

##### 2.4.2 Hardware A/B: sequenzielle Sendepfade

Verwende einen deterministischen Zeitplan, der vollständige WSPR-Aussendungen Target- und Referenzphasen zuordnet. Ein Sender, der zwischen zwei HF-Pfaden umgeschaltet wird, ist normalerweise der stärkste Aufbau, weil Rufzeichen, Frequenzreferenz und Sender gemeinsam bleiben. Trage die tatsächliche Wiederkehr und UTC-Phase jedes Pfads ein, prüfe die physische Zuordnung des Zeitplans zu den Pfaden ohne HF und melde die tatsächliche Leistung. Gerätespezifische Hinweise zu Zeitplanung und Umschaltung stehen in [Anhang C](#sec-sequential-tx-setup).

WSPRadar bildet automatisch eindeutige geplante A/B-Paare. Das Paar-Delta bleibt sequenziell: Kurzes, ausgewogenes Abwechseln verringert Unterschiede durch Ausbreitung, Störungen, Zeitplanposition und Umschaltung, beseitigt sie aber nicht. Prüfe unvollständige Paare und den chronologischen Verlauf zusammen mit dem gepaarten Median. Vertausche in einem bestätigenden Lauf die Target- und Referenzzeitplanphasen; bleibt der Vorteil des physischen Pfads nach dem Rollentausch bestehen, ist dies wesentlich überzeugender als eine Wiederholung mit derselben Phasenzuordnung.

<blockquote class="evidence-conclusion"><p>Unter dem dokumentierten deterministischen Zeitplan beschrieben das Delta SNR geplanter Paare und die einseitigen Paar-Outcomes den beobachteten Unterschied zwischen den geschalteten Target- und Referenzpfaden für die ausgewählten Empfänger, Zeiten und den geografischen Bereich.</p></blockquote>
````

#### Original docs/doc_de.py:495 — 2.4.3 Referenzstation / Buddy-Test

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.4.3 Referenzstation / Buddy-Test
````

#### Original docs/doc_de.py:497 — 2.4.3 Referenzstation / Buddy-Test

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Verwende eine bekannte, separat identifizierbare vollständige Referenz-Sendestation, deren QTH, Rufzeichen, tatsächliche und gemeldete Leistung, Ausrüstung und Betriebsplan bekannt und nachvollziehbar sind. TX-Paare teilen denselben entfernten Empfänger und denselben Zyklus; Target und Referenz bleiben jedoch eigenständige vollständige Sendestationen mit jeweils eigenen Sendern, Antennen, Speiseleitungen und Stationsumgebungen. Der getrennt eingegebene Referenz-Locator darf dasselbe Grid-4 wie das Target-QTH enthalten; gleiches Grid-4 beweist keine physische Ko-Lokation.
````

#### Original docs/doc_de.py:499 — 2.4.3 Referenzstation / Buddy-Test

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Bilden beide Sendepfade dagegen einen einzigen lokal gesteuerten A/B-Aufbau, wähle Hardware A/B. Die physische Anordnung bestimmt das Design und nicht die Verwandtschaft der Rufzeichen. Simultanes Hardware A/B benötigt weiterhin zwei verschiedene gültige exakte Rufzeichen; steht nur eine gültige exakte Identität zur Verfügung, verwende sequenzielles Hardware A/B.
````

#### Original docs/doc_de.py:507 — 2.4.4 Lokaler Nachbarschafts-Median

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
##### 2.4.4 Lokaler Nachbarschafts-Median
````

#### Original docs/doc_de.py:533 — 2.5.1 Wann dieses Diagnosewerkzeug sinnvoll ist

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Nutze den Detektor ausschließlich mit Benchmark-Evidenz. Seine native Evidenzeinheit ist ein simultaner **Joint Spot** oder bei sequenziellem TX Hardware A/B ein **vollständiges geplantes Paar**. Nur diese Einheiten enthalten sowohl Target-SNR als auch korrigiertes Referenz-SNR und damit ein gepaartes Delta SNR. Outcomes `Only Target` und `Only Reference` bleiben nützlicher Diagnosekontext, können ein Ereignis aber nicht selbst qualifizieren.
````

#### Original docs/doc_de.py:546 — 2.5.2 Wie die Erkennung praktisch arbeitet

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
1. Die gepaarten Beobachtungen bleiben an ihren nativen WSPR-Zyklus- beziehungsweise geplanten Paarzeiten erhalten.
````

#### Original docs/doc_de.py:568 — 2.5.3 Ein berichtetes Ereignis lesen und untersuchen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* Die grünen Aktionen **`↓ In Station Insights anzeigen`** und **`↓ Drill-Down-Details anzeigen`** stehen rechts neben ihrem exakten Funkwegzeitraum. Die erste wählt diesen Funkweg aus, lädt den Drill-Down vor und navigiert für die breitere Laufhistorie zu Station Insights; die zweite nimmt dieselbe Auswahl und Vorladung vor, navigiert aber unmittelbar zum Drill-Down. Beide öffnen den **`Ausreißerfokus`** über die vollständige gestützte Baseline-Flanke vor dem Ereignis, die geschützte vorläufige Episode und die Baseline-Flanke danach; begrenzt wird er nur durch das abgeschlossene Analysefenster, und dieses Detektor-Stützintervall darf länger als 24 Stunden sein. Die fokussierte Delta-SNR-Abbildung zeigt jeden tatsächlichen beibehaltenen Joint Spot beziehungsweise jedes vollständige geplante Paar zu seiner nativen Zeit anstelle eines Binmedians, IQR oder einer Dichteschicht. Identische `*`-Marker kennzeichnen jede native Einheit im aktuellen Fenster, die innerhalb eines gemeldeten Kandidaten einzeln sowohl das konfigurierte Abweichungs- als auch das robuste-z-Kriterium erfüllt; dies schließt alle solchen Einheiten eines mehrteiligen Ausbruchs oder einer Episode ein. Ein dezentes Band **Fokussierte Episode** kennzeichnet die ausgewählte berichtete Episode. Es umfasst deren berichtetes Intervall der beibehaltenen Evidenz, ist an beiden Enden um eine halbe Breite der nativen Evidenzeinheit erweitert und wird am Fokusfenster abgeschnitten, damit ein Impuls aus einer Einheit sichtbar bleibt; es ist weder ein Konfidenzintervall noch eine Messung der Dauer eines physischen Ereignisses. Weitere Overlays zeigen das erwartete lokale Delta SNR, die Baselines davor und danach nur über ihre tatsächlichen Stützintervalle, symmetrische robuste-z-Hilfslinien bei 1, 2 und 3 sowie an der konfigurierten Qualifikationsschwelle und die konfigurierte Grenze der absoluten Abweichung ausschließlich für die fokussierte Episode. Andere mit Stern markierte Kandidateneinheiten können gegen andere lokale Baselines und robuste Streuungen bewertet worden sein. Dies sind Detektorhilfen und keine Konfidenzintervalle; das Überschreiten einer einzelnen Linie kann keinen Kandidaten allein qualifizieren. Prüfe anhand der zugrunde liegenden Werte für Target-SNR und korrigiertes Referenz-SNR sowie naher einseitiger Outcomes, ob die Bewegung des Delta SNR hauptsächlich von einer Seite ausging, ob sich eines der Signale der Decode-Grenze näherte und ob sich die Paarbarkeit in der Umgebung veränderte.
````

#### Original docs/doc_de.py:605 — 3.1 Breite, Konsistenz und Wiederholbarkeit beurteilen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* Umfang der qualifizierenden bestätigten Gelegenheiten, Spots oder geplanten Paare;
````

#### Original docs/doc_de.py:633 — 3.2 Ergebnis durch Wiederholung und Kontrolle absichern

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
* vertausche bei sequenziellem TX Hardware A/B die Target- und Referenzzeitplanphasen;
````

#### Original docs/doc_de.py:639 — 3.2 Ergebnis durch Wiederholung und Kontrolle absichern

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Kleine beobachtete Unterschiede werden nützlicher, wenn sie über Stationen, Zeiträume, benachbarte Segmente und kontrollierte Wiederholungen erneut auftreten. Eine vertauschte Zuordnung bei sequenziellem TX ist besonders aufschlussreich, weil sie Zeitplan-, Schaltpfad- oder Zykluspositionseffekte sichtbar machen kann, die bei einer gewöhnlichen Wiederholung in derselben Rolle verbleiben.
````

#### Original docs/doc_de.py:669 — 3.3 Evidenzgerechte Schlussfolgerung formulieren

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Nenne bei einem kontrollierten Hardware-A/B-Ergebnis die vollständigen verglichenen Pfade und jeden Kreuztausch oder jede Kalibrierung. Stelle bei einem Referenzstations-/Buddy-Test klar, dass vollständig aufgebaute Stationen und ihre Umgebungen gebenchmarkt wurden. Nenne bei einem lokalen Nachbarschafts-Benchmark den Radius und die wechselnde Referenzdefinition des lokalen Nachbarschafts-Medians.
````

#### Original docs/doc_de.py:673 — 3.3 Evidenzgerechte Schlussfolgerung formulieren

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* Ein **Hardware-A/B-Test** vergleicht die dokumentierten lokalen Pfade.
* Ein **Buddy-Test** vergleicht vollständig aufgebaute Stationen und ihre Umgebungen.
* **Lokaler Nachbarschafts-Median** vergleicht die vollständige Target-Station mit dem Median der beitragenden Peers in der Umgebung innerhalb des ausgewählten Radius unter den beobachteten Bedingungen.
````

#### Original docs/doc_de.py:748 — 4.1 Ablaufsteuerung

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Konfigurationskompatibilität.** Gespeicherte Dateien bewahren die Eingaben und dauerhaften Ansichtsoptionen, die für die ausgewählte Analyse gelten. Ungültige oder nicht unterstützte Dateien werden abgelehnt, statt stillschweigend neu interpretiert zu werden. Das formale JSON-Schema ist der maßgebliche vollständige Vertrag gespeicherter Konfigurationen; [Abschnitt 8.4](#sec-8-4) bietet eine knappe, betriebsbezogene Zusammenfassung ausgewählter öffentlicher Bezeichnungen. Das Laden oder Speichern einer Konfiguration erzeugt kein zusätzliches Ergebnis; ausgeführt wird nur die ausgewählte Performance- oder Benchmark-Analyse.
````

#### Original docs/doc_de.py:769 — 4.2 Frage, Target und Messzeitraum

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Verwende das Rufzeichen oder die Meldekennung exakt so, wie es beziehungsweise sie hochgeladen wurde. Nur als schematische Platzhalter stehen `CALLSIGN`, `CALLSIGN/1`, `CALLSIGN/2`, `CALLSIGN/P`, `CALLSIGN/QRP` und `CALLSIGN-1` für verschiedene exakte Archividentitäten. WSPRadar führt sie weder anhand des Basisrufzeichens zusammen noch wendet es eine verdeckte Präfix- oder Suffixzuordnung an. Die Beispiele zeigen lediglich die Zuordnungssyntax; sie begründen weder die Zuteilung noch die Berechtigung, eine dieser Identitäten zu senden. Verwende nur ein vollständiges Rufzeichen, das für den Bediener und die Betriebsumstände zulässig ist.
````

#### Original docs/doc_de.py:779 — 4.3 Benchmark-Design und -Einstellungen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
- `Hardware A/B`
- `Bekannte Referenzstation`
- `Lokale Nachbarschaft`
````

#### Original docs/doc_de.py:783 — 4.3 Benchmark-Design und -Einstellungen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Bei `RX Performance` und `TX Performance` entfällt der Bereich **`Benchmark-Design`** vollständig, weil Performance keine Referenz verwendet. Der abschließende Prüfbereich erscheint dennoch nach dem gemeinsamen Bereich für Filter, Umfang und Evidenz; seine richtungsabhängige Aktion `RX-Analyse starten` / `TX-Analyse starten` und `Konfig speichern` bleiben unverfügbar, solange die Frage unvollständig ist oder für eine Benchmark-Frage kein vollständiges Benchmark-Design vorliegt. Performance und Benchmark sind sich gegenseitig ausschließende Ergebnistypen: Ein Lauf erzeugt nur das ausgewählte Ergebnis. [Abschnitt 8.4](#sec-8-4) fasst ausgewählte öffentliche maschinenlesbare Bezeichnungen für Konfiguration, URL und Export zusammen; er ist kein vollständiger Feld- oder Parameterkatalog.
````

#### Original docs/doc_de.py:787 — 4.3 Benchmark-Design und -Einstellungen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| **Gibt es einen ermittelten Target–Referenz-Offset?** | `Kein ermittelter Offset — 0,0 dB verwenden` | Geführtes Hardware A/B und bekannte Referenzstation | Unterscheidet keinen ermittelten Offset, die Verwendung einer ermittelten Korrektur und einen gezielten Offset-Ermittlungslauf. |
````

#### Original docs/doc_de.py:789 — 4.3 Benchmark-Design und -Einstellungen

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| **Referenz-Rufzeichen** | leer | Hardware A/B und Referenzstation | Exakte Meldeidentität der Referenz. |
| **Referenz-Locator** | unabhängiges Grid-4 bei Referenzstation; abgeleitetes Target-Grid-4 bei Hardware A/B | Benchmark | Steuert die Zuordnung der Referenzzeilen im Archiv. |
| **Nachbarschaftsradius (km)** | `100`; 10–250 km in 10-km-Schritten | Lokaler Nachbarschafts-Benchmark | Definiert den lokalen Referenzpool um das Target-QTH. |
| **TX-A/B-Methode** | `Simultanes TX` | TX Hardware A/B | Wählt Paarbildung zweier Sender im selben Zyklus oder deterministische sequenzielle Paarung. |
| **Wiederholintervall** | `10 min`; `4, 6, 10, 12, 20, 30, 60 min` | Sequenzielles TX A/B | Tatsächliche Wiederkehr jedes physischen Pfads. |
| **Target-Start / Referenz-Start** | `00 UTC` / `02 UTC`; verschiedene gerade Phasen unterhalb des Wiederholintervalls | Sequenzielles TX A/B | Ordnet Aussendungen den Target- und Referenzphasen des Zeitplans zu. |
````

#### Original docs/doc_de.py:796 — 4.3 Benchmark-Design und -Einstellungen

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Bei TX Hardware A/B bezeichnet das `Wiederholintervall` die tatsächliche Wiederkehr jedes Pfads und nicht zwangsläufig den angezeigten `Frame`-Wert eines Senders. Vergleiche die Stunden-Vorschau mit den beobachteten Startzeiten auf Sendung und der physischen Schaltzuordnung. Gerätebeispiele für simultanes TX stehen in [Anhang B](#sec-simultaneous-tx-setup), Beispiele für sequenzielles TX in [Anhang C](#sec-sequential-tx-setup); die Paarbildung beschreiben die [Abschnitte 7.1](#sec-7-1) und [7.7](#sec-7-7) <a href="#ref-12">[Ref-12]</a>.
````

#### Original docs/doc_de.py:804 — Vorzeichen der referenzseitigen SNR-Korrektur

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Die Korrektur gilt für den Referenz-Empfangs- beziehungsweise Sendepfad oder -Zeitplan bei Hardware A/B, die bekannte Referenzstation oder jeden lokalen Beitrag vor Bildung des lokalen Nachbarschafts-Medians.
````

#### Original docs/doc_de.py:812 — Vorzeichen der referenzseitigen SNR-Korrektur

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Eine konstante Korrektur kann Übersteuerung, instabile AGC, intermittierende Signalführung, frequenzabhängigen Amplitudengang oder falsche Leistungsangaben nicht beheben. Hardware-A/B-Kalibrierung sollte ein gemeinsames Eingangssignal oder eine kalibrierte Bezugsebene verwenden. Eine geografisch getrennte Referenzstation kann nur eine wiederholbare Basislinie für genau dieses Paar, Band und diesen Aufbau stützen – keine absolute Kalibrierung. [Anhang D](#sec-reference-snr-calibration) beschreibt das praktische Verfahren.
````

#### Original docs/doc_de.py:831 — 4.4 Filter und Evidenzschwellen

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| **Minimale geplante Paare pro Station** | `1`; Bereich 1–50 | sequenzielles TX A/B | Verlangt wiederholte vollständige geplante Paare, bevor eine Station ein Paar-Delta beiträgt; einseitige Paarkategorien verwenden denselben Zahlenwert. |
````

#### Original docs/doc_de.py:865 — 4.5 Karten-, Inspektor- und Exporteinstellungen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Damit steht `2h` bei jeder Laufdauer zur Verfügung. Die früheren Werte `5m` und `15m` bleiben aus Kompatibilitätsgründen für gespeicherte Konfigurationen und URLs zulässig, werden aber nicht als neue Auswahl angeboten. Ein ausdrücklich geladener gültiger Altwert bleibt auswählbar und wird nicht stillschweigend geändert. Die chronologische Aggregation verändert weder die Klassifikation von Gelegenheiten noch die Benchmark-Paarbildung oder die festen einstündigen UTC-Profile. Leere Performance-Zeit- oder Entfernungs-Bins bleiben fehlende Evidenz und werden nicht zu künstlichen Beobachtungen mit einer Rate von null.
````

#### Original docs/doc_de.py:867 — 4.5 Karten-, Inspektor- und Exporteinstellungen

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Der Drill-Down-Zoom ist flüchtig und nur für genau eine ausgewählte Station verfügbar. Wähle **`Aus`** oder ein vollständiges Intervall von `1h`, `3h`, `6h`, `12h` beziehungsweise `24h`. **`Datum der Fenstermitte (UTC)`** und **`Uhrzeit der Fenstermitte (UTC)`** wählen die Mitte dieses Intervalls; WSPRadar leitet daraus exakten Start und exaktes Ende ab, verschiebt das vollständige Intervall an einer Laufgrenze, statt es zu kürzen, und lässt es mit **`← Früher`** beziehungsweise **`Später →`** um ein vollständiges ausgewähltes Fenster versetzen. Die aufgelösten Grenzen erscheinen in einer Zeile als **`Ausgewähltes Zeitfenster: {start} bis {end} UTC`**. Der Zoom begrenzt die fokussierten Abbildungen und die Drill-Down-Tabelle; **`Tabelle filtern`** verändert anschließend nur die angezeigte Tabelle und niemals die fokussierten Abbildungen oder die abgeschlossene Analyse. Seine Messwertabbildung ist bewusst kein Zwei-Minuten-Aggregat: Der simultane Benchmark zeigt einen tatsächlichen Delta-SNR-Punkt je beibehaltenem Joint Spot zu seiner kanonischen Zykluszeit; sequenzielles TX A/B zeigt einen tatsächlichen Paar-Delta-SNR-Punkt je beibehaltenem vollständigem geplanten Paar am geplanten Target-Start; Performance zeigt das tatsächliche normierte Target-SNR jeder erfolgreichen bestätigten Gelegenheit zu ihrer kanonischen Zykluszeit. Dies sind einzelne beibehaltene wissenschaftliche Evidenzeinheiten nach Zusammenführung, Zuordnung und Filtern durch WSPRadar und keine unveränderten Provider-Zeilen. In der fokussierten Messwertansicht entfallen Binmedian, IQR, Dichtehintergrund, Farbskala, Median des vollständigen Laufs und nach UTC-Stunde gefaltetes Messwertpanel. Die ergänzende Performance-Outcome- beziehungsweise Benchmark-Abdeckungsansicht darf ihre chronologische Aggregation beibehalten; Segmentansicht und Evidenz der ausgewählten Station über das vollständige Fenster bleiben dichtebasierte aggregierte Ansichten. Target- und Referenz-Komponentenzeile eines aufgenommenen sequenziellen Paars bleiben gemeinsam in der Tabelle. Titel fokussierter Abbildungen verwenden das kompakte Format **`DG2CAD (JN47mv) - Zeitfenster: {start} bis {end} UTC`**.
````

#### Original docs/doc_de.py:875 — 4.6 Bedienelemente der Benchmark-Ausreißererkennung

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Die Delta-SNR-Ausreißererkennung für Benchmark ist eine optionale fachkundige Analyseebene über der beibehaltenen nativen gepaarten Evidenz. Eine native gepaarte Einheit ist ein simultaner **Joint Spot** oder bei sequenziellem TX Hardware A/B ein **vollständiges geplantes Paar**. Die Erkennung läuft getrennt für jeden exakten Peer-Funkweg `Rufzeichen + Locator` und unabhängig vom ausgewählten Darstellungs-Bin der **Zeitlichen Evidenz**. Einseitige Evidenz kann ein fehlendes Delta SNR nicht ersetzen. [Abschnitt 2.5](#sec-outlier) erklärt Bedienung und Interpretation; [Abschnitt 7.11](#sec-7-11) definiert die Methode formal.
````

#### Original docs/doc_de.py:923 — 5.2 Fehler nach Symptom eingrenzen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| **Kein qualifizierendes Benchmark-Ergebnis bleibt erhalten** | Prüfe die konfigurierte Anforderung an Joint-Evidenz beziehungsweise vollständige geplante Paare, die Mindestanzahl qualifizierter Stationen pro Kartensegment, Filter und Umfang. WSPRadar nennt diese angewandten Anforderungen, erfindet jedoch keine beobachteten Benchmark-Maxima, die die Pipeline nicht berechnet hat. |
| **Benchmark enthält kein Delta SNR** | Prüfe gemeinsame entfernte Peers in überlappenden Zyklen oder geplanten Paaren, Referenzbetriebszeit, Uhren, Zeitplanzuordnung, Joint-Schwelle, Filter und Bereich. |
````

#### Original docs/doc_de.py:929 — 5.2 Fehler nach Symptom eingrenzen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| **Unerwartetes Vorzeichen des Delta SNR bei Hardware A/B** | Prüfe physische A/B-Zuordnung, Reihenfolge von Target und Referenz, Korrekturvorzeichen, Zeitplanphasen, tatsächliche und gemeldete Leistung sowie Kalibrierung. Gleiche einen Funkweg im Drill-Down ab. |
````

#### Original docs/doc_de.py:942 — 5.3 Rufzeichen und Locator prüfen

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Eine Referenzstation verwendet das exakte Referenz-Rufzeichen plus einen unabhängigen vierstelligen Referenz-Locator. RX und simultanes TX Hardware A/B leiten das Referenz-Grid-4 aus dem Target-QTH ab; sequenzielles TX Hardware A/B verwendet die gemeinsame Target-Identität und unterscheidet die Pfade über den Zeitplan. Lokale Referenzen werden geografisch gewählt.
````

#### Original docs/doc_de.py:946 — 5.3 Rufzeichen und Locator prüfen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Simultanes TX mit zusammengesetzten Rufzeichen.** WSPRadar rekonstruiert Typ-2- und Typ-3-Nachrichten nicht und leitet einen fehlenden Sender-Locator nicht aus einer benachbarten Aussendung ab. Prüfe vor dem Sammeln von Evidenz mehrere Upstream-Spots und bestätige, dass die für den WSPRadar-Lauf ausgewählte Datenquelle beide exakten Identitäten im gemeinsamen Target-Grid-4 meldet. Wird eine Identität ohne verwendbaren Locator oder mit einem anderen Grid-4 bereitgestellt, erfüllen diese Zeilen die Identitätszuordnung von Hardware A/B nicht.
````

#### Original docs/doc_de.py:962 — 5.5 Wie das Target-Active Gate die Evidenz prägt

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Das Gate ist bewusst Target-zentriert. Die Betriebsbereitschaft der Referenz bleibt Teil des Versuchs, und ein Tausch von Target und Referenz kann die einseitigen Decode Outcomes und die zulässige Population verändern. Sequenzielles TX Hardware A/B verwendet stattdessen deterministische geplante Paare. [Abschnitt 7.3](#sec-7-3) definiert diese Konditionierung formal.
````

#### Original docs/doc_de.py:1017 — 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Toledo (2010): Warum langsames Abwechseln scheitert.** Sivan Toledo erprobte ungefähr eine Stunde lang eine Antenne und anschließend eine andere. Dabei änderte sich das SNR des Funkwegs in derselben Größenordnung wie der scheinbare Antennenunterschied. Er folgerte, dass dieser naive Aufbau die Antennen nicht isolieren konnte, und schlug eine Umschaltung in jedem Zyklus oder simultane Aussendungen mit getrennter Hardware vor. Der deterministische alternierende TX-A/B-Zeitplan von WSPRadar folgt derselben praktischen Logik: Ein kurzer zeitlicher Abstand verringert zeitliche Konfundierung, beseitigt sie aber nicht. <a href="#ref-3">[Ref-3]</a>
````

#### Original docs/doc_de.py:1026 — 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Vanhamel, Machiels und Lamy (2022): Konditioniertes simultanes RX.** Ihr begutachteter Versuch konditionierte zwei nominell identische 160-m-WSPR-Empfangsstationen und verglich gemeinsame entfernte Aussendungen simultan. Innerhalb der hier betrachteten Quellen ist dies die stärkste direkte Vorarbeit für RX Hardware A/B und für die Charakterisierung von Offsets zwischen Empfangsketten vor der Interpretation von Antennenunterschieden. Die Ausbreitungsergebnisse zeigen außerdem, dass Polarisation und ionosphärische Effekte mit dem gemeldeten SNR gekoppelt bleiben. <a href="#ref-2">[Ref-2]</a>
````

#### Original docs/doc_de.py:1031 — 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Zander berichtet je Vorversuch ungefähr 1.000 Beobachtungen, von denen etwa 150–200 gemeinsame Meldungen aus 15–35 Empfängern beibehalten wurden; die Stichproben-Standardabweichung lag nahe 3 dB. Die Aussage der Arbeit im Sub-dB-Bereich betrifft die Präzision eines arithmetischen Mittels unter den Modell- und Stichprobenannahmen und keine rückführbare Gesamtgenauigkeit. Geografische Stichprobe, Antennenrichtwirkung und unbekannte Elevationswinkel bleiben systematische Grenzen. Die Studie stützt simultanes Delta SNR am selben Empfänger, nicht jedoch das sequenzielle Ein-Sender-Design von WSPRadar, stationsgleichgewichtete Mediane, Decode Outcomes oder Nachbarschaftsreferenzen.
````

#### Original docs/doc_de.py:1048 — 6.5 Was WSPRadar übernimmt, integriert und ergänzt

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* Hardware A/B, Referenzstation und dynamischen lokalen Nachbarschafts-Benchmarks;
* Zuordnung im selben Zyklus oder über deterministische geplante Paare;
````

#### Original docs/doc_de.py:1068 — 7. Wissenschaftliche Methoden

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
2. **Gebildete Evidenzeinheiten:** qualifizierende Gelegenheiten, Peer-Zyklen, Joint-Einheiten und geplante A/B-Paare, die nach den Zulässigkeits- und Zuordnungsregeln von WSPRadar entstehen.
````

#### Original docs/doc_de.py:1078 — 7. Wissenschaftliche Methoden

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| $c$ | ein zulässiger WSPR-<strong class="defined-term">Zyklus</strong> oder beim sequenziellen TX A/B ein geplantes Paar |
````

#### Original docs/doc_de.py:1096 — 7. Wissenschaftliche Methoden

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| RX Hardware A/B / Buddy | ein Peer-Zyklus eines entfernten Senders | Target aktiv; beide Empfänger melden denselben Sender-Zyklus für Delta SNR | Stationsmedian des Delta SNR, danach Median über Stationen | vollständige Empfangspfade, sofern Ketten nicht kontrolliert sind |
| Simultanes TX Hardware A/B / zutreffender Buddy- oder lokaler Benchmark | ein Peer-Zyklus eines entfernten Empfängers | Target aktiv; derselbe Empfänger-Zyklus für gepaartes Delta SNR | Stationsmedian des Delta SNR, danach Median über Stationen | Leistung, Kettenunterschiede und Auswahl nach Joint-Decode |
| Sequenzielles TX Hardware A/B | ein entfernter Empfänger in einem geplanten Target-/Referenzpaar | deterministischer, überschneidungsfreier Zeitplan und vollständiges Paar im Zeitfenster | Stationsmedian des Paar-Deltas, danach Median über Stationen | zeitliche Trennung sowie Umschalt- und Zeitplaneffekte |
| Lokaler Nachbarschafts-Median | ein Target-/lokaler-Referenz-Peer-Zyklus | Target aktiv; ein Beitrag je aktiver lokaler Identität | lokaler Median als Referenz, danach Stations- und Segmentmediane des Delta SNR | wechselnde, unkalibrierte Zusammensetzung |
````

#### Original docs/doc_de.py:1113 — 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
* Sequenzielles TX A/B behält die exakten geplanten Startzeiten, ordnet sie anhand des konfigurierten Modulo-Zeitplans Target oder Referenz zu und bildet für jeden Peer deterministische Eins-zu-eins-Paare. Beide geplanten Starts müssen im Laufzeitfenster liegen.
````

#### Original docs/doc_de.py:1116 — 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
WSPRadar klassifiziert archivierte WSPR-Meldungen nicht als Typ 1, Typ 2 oder Typ 3. Beim simultanen Benchmark ist die wissenschaftliche Einheit der nach den Identitätsregeln aus Abschnitt 7.2 aufgelöste Peer-Zyklus des Archivs. Aufeinanderfolgende Aussendungen einer erweiterten WSPR-Folge bleiben getrennte zweiminütige Zyklen; jede kann getrennt eine Joint-Einheit bilden, wenn derselbe entfernte Empfänger in diesem Zyklus sowohl Target als auch Referenz meldet. Ein simultaner Benchmark verbindet niemals das Target aus einem Zyklus mit der Referenz aus einem anderen Zyklus. Sequenzielles TX Hardware A/B ist das getrennte Design, das bewusst unterschiedliche geplante Zyklen paart.
````

#### Original docs/doc_de.py:1127 — 7.2 Identität, Zuordnung und Zeilenkonsolidierung

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| Analyse | Target-Zuordnung | Referenz-/Peer-Identität | Kleinste Ergebniseinheit |
````

#### Original docs/doc_de.py:1131 — 7.2 Identität, Zuordnung und Zeilenkonsolidierung

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
| Referenzstation / Buddy | exaktes Target-Rufzeichen + Target-Grid-4 | exaktes Referenzrufzeichen + unabhängiges Referenz-Grid-4; entfernte Peer-Identität | konsolidierter Peer-Zyklus |
| RX Hardware A/B | exaktes Target-Rufzeichen + Target-Grid-4 | exaktes Referenzrufzeichen + dasselbe abgeleitete Target-Grid-4; entfernte TX-Identität | konsolidierter Peer-Zyklus |
| Simultanes TX Hardware A/B | exaktes Target-Rufzeichen + Target-Grid-4 | exaktes Referenzrufzeichen + dasselbe abgeleitete Target-Grid-4; entfernte RX-Identität | konsolidierter Peer-Zyklus |
| Sequenzielles TX Hardware A/B | gemeinsames exaktes Target-Rufzeichen + Target-Grid-4, nach Zeitplan getrennt | dasselbe Rufzeichen/Grid-4 im Referenzzeitplan; entfernte RX-Identität | geplantes Target-/Referenzpaar |
| Lokaler Nachbarschafts-Benchmark | exaktes Target-Rufzeichen + Target-Grid-4 | lokale Identität innerhalb des Radius; entfernte Peer-Identität | Target-/lokale-Referenz-Peer-Zyklus |
````

#### Original docs/doc_de.py:1137 — 7.2 Identität, Zuordnung und Zeilenkonsolidierung

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Für die Auswahl der Target-Zeilen im Archiv verwendet WSPRadar Grid-4, auch wenn ein sechsstelliges QTH konfiguriert ist. Das vollständige QTH bleibt für Entfernung, Azimut, Sonnenhöhe und die Geometrie des lokalen Radius relevant. Ein gemeinsames Hardware-A/B-Grid-4 belegt keine physische Ko-Lokation.
````

#### Original docs/doc_de.py:1139 — 7.2 Identität, Zuordnung und Zeilenkonsolidierung

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Bei simultanem TX Hardware A/B arbeitet WSPRadar mit der Darstellung des Archivs: exaktes Target-Rufzeichen plus Target-Grid-4 sowie exaktes Referenzrufzeichen plus dasselbe Grid-4. Es leitet keinen Locator aus einer benachbarten Typ-2- oder Typ-3-Aussendung ab und verlangt nicht, dass beide Folgenpositionen vorliegen, bevor eine Einheit desselben Zyklus zugelassen wird. Beide Positionen einer korrekt ausgerichteten Folge können deshalb getrennt beitragen, wenn das ausgewählte Archiv beide Identitäten wie erforderlich auflöst.
````

#### Original docs/doc_de.py:1147 — 7.2 Identität, Zuordnung und Zeilenkonsolidierung

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Die Auswahl der stärksten Meldung gilt für die SNR-Werte bei Performance, beide Seiten eines simultanen Benchmarks mit fester Referenz und die Target-Seite des lokalen Nachbarschafts-Medians. Bei lokalen Referenzbeiträgen bleiben die Mediane innerhalb jeder Identität und der anschließende Median über die Identitäten erhalten; sequenzielles TX A/B behält seine Mediane je Seite innerhalb geplanter Vergleichspaare bei. Diese unterschiedlichen Konstruktionen sind in [Abschnitt 7.7](#sec-7-7) definiert. Mediane und IQR über beibehaltene Beobachtungen bleiben Zusammenfassungen der daraus entstehenden Evidenz und sind von der Auswahl eines SNR-Werts innerhalb eines Zyklus und Funkwegs zu unterscheiden.
````

#### Original docs/doc_de.py:1163 — 7.3 Konditionierung auf Target-Aktivität und Zulässigkeit

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Jede Joint-Beobachtung belegt bereits eine Target-Beteiligung. Das Gate verändert daher nicht die Delta-SNR-Werte der Joint-Beobachtungen. Es verändert die Population einseitiger oder asynchroner Outcomes und bei Performance den Gelegenheitsnenner. Sequenzielles TX A/B verwendet statt des simultanen Target-Active Gates eine deterministische Zeitplanzulässigkeit.
````

#### Original docs/doc_de.py:1255 — 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
`Both (Async)` bedeutet, dass für eine Identität beibehaltene Evidenz beider Seiten existiert, aber für die betreffende Stationskategorie keine qualifizierende Einheit desselben Zyklus oder kein geplantes Paar erhalten bleibt. Die Kategorie zeigt eine breitere Beteiligung beider Seiten, trägt jedoch kein gepaartes Delta SNR bei.
````

#### Original docs/doc_de.py:1294 — 7.7 Aggregationshierarchie und Gewichtung

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Bei jedem Benchmark-Design gilt für Gewichtung und Segmentunterstützung dieselbe Stationsidentität: das exakte `Rufzeichen + vollständig gemeldeter Locator`. Jede Identität muss für sich die konfigurierte Mindestzahl an Joint-Evidenz beziehungsweise bei sequenziellem TX A/B an vollständigen geplanten Paaren erfüllen. Genau die Identitäten, die jeweils einen Peer-Median beitragen, zählen auch für die Mindestanzahl qualifizierender Stationen pro Kartensegment. Identitäten mit ausschließlich einseitiger Evidenz tragen nicht zu dieser Delta-SNR-Unterstützungszahl bei. Dasselbe Rufzeichen mit unterschiedlichen vollständigen Locatorn zählt getrennt, auch wenn beide Locator im selben Grid-4 liegen. Gezählt werden gemeldete Funkwegidentitäten; daraus folgen keine unabhängigen physischen Stationen oder Standorte.
````

#### Original docs/doc_de.py:1298 — 7.7 Aggregationshierarchie und Gewichtung

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
**Sequenzielles TX A/B**

1. Meldungen der exakten Identität behalten, deren Startzeit zur Target- oder Referenzphase passt.
2. Geplante Starts unter dem gemeinsamen Wiederholintervall anhand des kleinsten zyklischen Abstands eins zu eins paaren.
3. Verlangen, dass beide geplanten Starts im Laufzeitfenster liegen.
4. Innerhalb jedes Peers und geplanten Paars für jede Seite einen Mikro-Median berechnen.
5. Das Paar-Delta berechnen, wenn beide Mikro-Mediane existieren; andernfalls das Paar als einseitige Evidenz behalten.
6. Die Mindestanzahl vollständiger Paare je Peer anwenden.
7. Peer- und Segmentmediane wie oben berechnen.

Der Mikro-Median schützt eine geplante Seite vor duplikatähnlichen Wiederholungszeilen, macht die beiden nacheinander gesendeten Aussendungen aber nicht simultan.

<p style="page-break-after: avoid; -pdf-keep-with-next: true;"><strong>Lokaler Nachbarschafts-Median</strong></p>
````

#### Original docs/doc_de.py:1368 — 7.8.2 Abdeckung der Benchmark-Evidenz

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Unter dem Target-Active Gate sind Only Target und Only Reference gerichtet und asymmetrisch. Sequenzielles TX A/B verwendet stattdessen deterministische vollständige oder einseitige geplante Paare; auch ein einseitiges Paar besitzt jedoch kein Paar-Delta.
````

#### Original docs/doc_de.py:1375 — 7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Die angebotenen chronologischen Breiten richten sich nach der vollständigen Laufdauer und nicht nach der beobachteten Evidenzspanne: Läufe bis 6 Stunden verwenden standardmäßig `10m`, längere Läufe bis 24 Stunden `30m` und Läufe über 24 Stunden `12h`. [Abschnitt 4.5](#sec-5-5) führt die vollständigen Angebote einschließlich `2h` in jeder Dauerstufe auf. Ein ausdrücklich geladener gültiger Altwert von `5m` oder `15m` bleibt erhalten, ohne diese Breiten zu normalen neuen Auswahlwerten zu machen.
````

#### Original docs/doc_de.py:1391 — 7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Das zeitliche Benchmark-Delta-SNR verwendet beibehaltene Joint-Beobachtungen oder vollständige geplante Paare. Wenn keine gepaarten Werte verbleiben, zeigt das Delta-SNR-Panel weiterhin das vollständige ausgewählte UTC-Zeitfenster und weist auf die fehlende gepaarte Evidenz für Δ SNR hin. Das bedeutet, dass im dargestellten Bereich keine beibehaltene Joint-Beobachtung beziehungsweise kein vollständiges geplantes Paar verbleibt; daraus folgt nicht, dass die Datenquelle keine Beobachtungen lieferte, und die zeitliche Abdeckung kann weiterhin einseitige Outcomes zeigen. Chronologische Bins fassen gepaarte Werte in tatsächlicher Zeit zusammen; UTC-Stunden-Bins fassen dieselbe gepaarte Population nach Stunde über die Tage zusammen, die in der beibehaltenen Benchmark-Evidenz vertreten sind. Die zeitliche Benchmark-Abdeckung verwendet alle beibehaltenen Einheiten Only Target, Joint und Only Reference sowie die beiden oben definierten Zusammenfassungen des Joint-Evidenzanteils. Auch die Benchmark-Faltung erfordert mindestens zwei Tage mit Evidenz.
````

#### Original docs/doc_de.py:1407 — 7.8.4 Zusammenfassungen für den ausgewählten Funkweg

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Bei Benchmark zeigt der ausgewählte Funkweg das Delta SNR jeder Joint-Einheit oder jedes vollständigen geplanten Paars auf Beobachtungsebene und getrennt die Abdeckung durch Only Target, Joint und Only Reference. Ein Wechsel des ausgewählten Funkwegs oder Darstellungs-Bins verändert nur die Ansicht der beibehaltenen Evidenz, nicht die vorgelagerte Zuordnung, Zulässigkeit oder Aggregation.
````

#### Original docs/doc_de.py:1409 — 7.8.4 Zusammenfassungen für den ausgewählten Funkweg

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Der Drill-Down kann dieselbe Evidenz des ausgewählten Funkwegs vor Anwendung gewöhnlicher Tabellenfilter vorübergehend auf ein zentriertes Intervall von `1h`, `3h`, `6h`, `12h` oder `24h` begrenzen. Sein fokussiertes Messwertrezept behält je nativer Koordinate eine wissenschaftliche Einheit: beim simultanen Benchmark einen zusammengeführten Joint Spot mit tatsächlichem Delta SNR zur kanonischen Zykluszeit, bei sequenziellem TX A/B ein vollständiges geplantes Paar mit tatsächlichem Paar-Delta-SNR am geplanten Target-Start oder bei Performance eine erfolgreiche bestätigte Gelegenheit mit tatsächlichem normiertem Target-SNR zur kanonischen Zykluszeit. „Nativ“ bezeichnet damit verarbeitete beibehaltene Evidenz nach Zusammenführung, Zuordnung und wissenschaftlichen Filtern und keine unveränderten Provider-Zeilen. Das fokussierte Messwertrezept enthält weder Mediane oder Quartile zeitlicher Bins noch Dichtegitter, Farbskala, Median des vollständigen Laufs oder gefaltetes Profil. Ergänzende Outcome- beziehungsweise Abdeckungspanels dürfen ihre chronologische Aggregation beibehalten; Segment- und ausgewählte Funkwegrezepte über das vollständige Fenster bleiben unveränderte Dichtezusammenfassungen. Die sequenzielle Zugehörigkeit hält weiterhin Target- und Referenz-Komponentenzeile jedes aufgenommenen Paars gemeinsam in der Tabelle.
````

#### Original docs/doc_de.py:1446 — 7.9 Geografie, Sonnenstandsklassifikation und Populationsfilter

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Die Sonnenstandsklassifikation verwendet die Sonnenhöhe am Target-QTH. Evidenz desselben Zyklus verwendet den Zykluszeitstempel. Beim geplanten TX A/B wird die Mitte zwischen den geplanten Target- und Referenzstarts verwendet, damit ein Paar nicht auf zwei Sonnenklassen verteilt werden kann.
````

#### Original docs/doc_de.py:1465 — 7.10 Abhängigkeit, Unsicherheit und Geltungsbereich der Validierung

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* **Evidenztiefe:** Zahl der Gelegenheiten, Joint-Einheiten oder geplanten Paare;
````

#### Original docs/doc_de.py:1485 — 7.11 Robuste Delta-SNR-Ereigniserkennung mit lokaler Basislinie

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| $u$ | eine native gepaarte Einheit: ein Joint Spot aus demselben Zyklus oder ein vollständiges geplantes Paar |
````

#### Original docs/doc_de.py:1637 — 8.1 Aussageklassen und evidenzgerechte Formulierungen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| **Bauteilzuordnung** | Ein mit einem lokalen Pfad oder Bauteil verbundener Unterschied. | Kontrolliertes Hardware A/B, Kalibrierung und möglichst Kreuztausch beziehungsweise Rollentausch. |
````

#### Original docs/doc_de.py:1647 — 8.1 Aussageklassen und evidenzgerechte Formulierungen

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
* **Lokaler Nachbarschafts-Benchmark** stützt Beschreibungen, wie die vollständige Target-Station unter den ausgewählten Bedingungen gegenüber den beitragenden Peers in der Umgebung abschnitt. Seine Referenz ändert sich mit den qualifizierenden Beobachtungen, dem Radius, dem entfernten Funkweg und dem Zyklus. Sie ist weder eine dauerhafte Stationsrangliste noch ein kalibrierter Antennenvergleich.
````

#### Original docs/doc_de.py:1686 — 8.2 Interpretationsgrenzen

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
* sequenzielles TX bleibt zeitlich getrennt;
````

#### Original docs/doc_de.py:1864 — Teil IV: Praktische Ergänzungen

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Dieser Teil bündelt die Einrichtung paralleler WSJT-X-Instanzen für simultane Empfangspfade, die Grenze von WSJT-X bei sparsamen synchronen Sendetests, praktische Verfahren für simultanes und sequenzielles TX Hardware A/B, die Kalibrierung der Referenzseite und die Projektlizenz. Verwende die Abschnitte, die für deine Station und deinen Versuch relevant sind.
````

#### Original docs/doc_de.py:1869 — Anhang A: Parallele WSJT-X-Instanzen für simultanes RX

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Mit diesem Verfahren wird unter Windows eine zweite isolierte WSJT-X-Instanz für einen simultanen RX-Hardware-A/B-Test eingerichtet. Das aktuelle WSJT-X-Handbuch nennt `--rig-name` als unterstützten Weg, die Einstellungen und beschreibbaren Dateien jeder Instanz zu trennen. Da sich WSJT-X-Versionen und Installationspfade ändern können, sollte bei abweichenden Menüs das aktuelle Handbuch geprüft werden. Parallele WSJT-X-Instanzen lösen dagegen nicht die Zeitplanung eines sparsamen simultanen TX-Hardware-A/B-Laufs; diese Grenze beschreibt Abschnitt A.4. <a href="#ref-12">[Ref-12]</a>
````

#### Original docs/doc_de.py:1918 — Anhang B: Simultanes TX Hardware A/B praktisch einrichten

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
### Anhang B: Simultanes TX Hardware A/B praktisch einrichten
````

#### Original docs/doc_de.py:1920 — Anhang B: Simultanes TX Hardware A/B praktisch einrichten

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
Dieser Anhang führt Schritt für Schritt durch einen simultanen TX-Hardware-A/B-Aufbau mit zwei lokal kontrollierten Sendepfaden. Er eignet sich für Vergleiche von Antennen, Speiseleitungen, Filtern, Anpassnetzwerken oder vollständigen Sendeketten. Beginne an geeigneten Kunstantennen oder über einen sicher ausgelegten Testpfad mit geringer Leistung und gehe erst nach der vollständigen Vorabprüfung auf Sendung.
````

#### Original docs/doc_de.py:1929 — B.1 Rufzeichen auswählen

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
Verwende nicht einen regulären Einzelaussender gegen einen anders geplanten Sender mit zusammengesetztem Rufzeichen. Die zusätzliche oder fehlende Folgenposition würde als vom Versuchsdesign erzeugte einseitige Evidenz erscheinen. Erfinde keinen Rufzeichenzusatz als bloßes Hardware-Etikett. Stehen keine zwei zulässigen exakten Identitäten zur Verfügung, verwende sequenzielles TX Hardware A/B. Konfiguriere beide Pfade für dasselbe wahrheitsgemäße physische Test-QTH; WSPRadar ordnet beide Identitäten im Grid-4 des Target-QTHs zu.
````

#### Original docs/doc_de.py:1989 — B.5.1–B.5.2 QMX und QMX+ Virtual U3S sowie Ultimate3S

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
**Verwende einen festen Zeitplan für den Frequenztausch.** Ordne nicht dauerhaft das Target der unteren und die Referenz der oberen Frequenz zu. Schmalbandiges QRM, ein anderes WSPR-Signal, der Frequenzgang eines Empfängers oder ein frequenzabhängiges Senderverhalten könnten dann einen Pfad begünstigen. Programmiere stattdessen komplementäre Eintragsfolgen, sodass die Pfade zwischen aufeinanderfolgenden geplanten Paaren ihre Frequenzpositionen tauschen, während ihre Rufzeichen weiterhin Target und Referenz identifizieren.
````

#### Original docs/doc_de.py:1993 — B.5.1–B.5.2 QMX und QMX+ Virtual U3S sowie Ultimate3S

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
| Geplantes Paar | HF-Position Target | HF-Position Referenz |
````

#### Original docs/doc_de.py:2061 — B.6 Durch Tausch oder Kreuztausch bestätigen

Retired unsupported sequential workflow. See the disposition table for the retained authoritative destination.

````text
<a id="sec-sequential-tx-setup"></a>
### Anhang C: Sequenzielle TX-A/B-Zeitplanung und Umschaltung

Dieser Anhang bündelt die praktischen Hinweise zu Zeitplan und Umschaltung hinter dem TX-Hardware-A/B-Leitfaden. Die exakten UI-Bedienelemente stehen in [Abschnitt 4.3](#sec-5-3), die genaue Bildung geplanter Paare in den [Abschnitten 7.1](#sec-7-1) und [7.7](#sec-7-7).

<a id="sec-b-1"></a>
<a id="sec-sequential-tx-setup-1"></a>
#### C.1 Anforderungen an einen gültigen zeitgesteuerten Versuch

Für sequenzielle TX-A/B-Antennentests ist ein Sender, der über einen kontrollierten Umschalter zwei HF-Pfade speist, normalerweise zwei unabhängigen Sendern vorzuziehen. Sender, Frequenzreferenz, WSPR-Kette, Rufzeichen, Leistungseinstellung und Zeitsteuerung bleiben damit gemeinsam.

Verwende für beide Pfade ein reguläres, gültiges Rufzeichen und unterscheide sie durch verschiedene deterministische UTC-Phasen. Trage die Aussendungen ein, die tatsächlich über den jeweiligen HF-Pfad erfolgen:

* Das `Wiederholintervall` ist die tatsächliche Wiederkehr jedes Pfads und entspricht nicht zwangsläufig dem angezeigten `Frame`-Wert eines Senders.
* `Target-Start` und `Referenz-Start` sind unterschiedliche gerade UTC-Phasen unterhalb dieses Intervalls.
* Verwende den kürzesten praktikablen Abstand, der einen zuverlässigen Betrieb und einen vertretbaren Tastgrad erlaubt.
* Melde die tatsächliche Leistung; kennzeichne den Pfad nicht durch falsche dBm-Werte.
* Prüfe vor dem Senden die Zeitsynchronisation und die physische Zuordnung von Zeitplan und Pfad.

Ein deterministischer Zeitgeber oder Controller ist erforderlich. Der zufällige Sendebetrieb über die prozentuale TX-Einstellung von WSJT-X erzeugt keine feste A/B-Folge.

<a id="sec-b-2"></a>
<a id="sec-sequential-tx-setup-2"></a>
#### C.2 Zeitgesteuerter WSPRadar-A/B-Relaisumschalter

WSPRadar enthält:

`tools/Timed-AB-Relay-Switch`

Derzeit veröffentlichtes Release-Paket der Version 0.1:

[Release-Paket des zeitgesteuerten A/B-Relaisumschalters herunterladen](https://github.com/markusthemaker/WSPRadar/releases/download/timed-ab-relay-switch-v0.1.0/Timed-AB-Relay-Switch-v0.1.0.zip)

Das Hilfsprogramm im Repository verwendet dieselben Begriffe und Bedingungen für den Zeitplan wie WSPRadar:

* `Wiederholintervall` gilt gemeinsam für Target und Referenz; zulässig sind `4, 6, 10, 12, 20, 30` oder `60 min`.
* `Target-Start` und `Referenz-Start` sind unterschiedliche gerade UTC-Phasen unterhalb dieses Intervalls.
* Die Voreinstellung lautet `Wiederholintervall = 10`, `Target-Start = 00`, `Referenz-Start = 02`.

Das Relais wählt jeden Pfad vor dessen konfiguriertem Start und hält während nicht belegter Lücken den zuletzt gewählten Pfad. An ungenutzten zweiminütigen WSPR-Grenzen wird nicht geschaltet. Hilfsprogramm und WSPRadar müssen anhand der Aussendungen, die tatsächlich über den jeweiligen HF-Pfad erfolgen, identisch konfiguriert werden. Ist die physische Polarität umgekehrt, ändere, ob Relais ON dem Target entspricht, oder tausche die beiden Startzuordnungen.

Eine optionale Vorlaufzeit lässt den HF-Pfad vor jedem geplanten Start einschwingen. Die manuelle physische Relaissteuerung ON/OFF bleibt unabhängig vom automatischen Zeitplan verfügbar. Bestehende Modulo-4-Konfigurationen der Version 0.1 behalten beim Laden ihr bisheriges Verhalten als `4 / 00 / 02` oder `4 / 02 / 00`. Das Hilfsprogramm ist für verbreitete ATtiny45/V-USB-HID-Relaisplatinen mit USB-VID/PID `16c0:05df` ausgelegt und verwendet unter Windows, Linux und macOS den Python-HID-Stack. Aktuelle Hinweise zu Installation, Berechtigungen und Optionen stehen in seiner README-Datei.

Das verlinkte Paket der Version 0.1 enthält noch den früheren festen Modulo-4-Zeitplaner. Bis ein neueres Paket veröffentlicht ist, ist für den hier beschriebenen konfigurierbaren Zeitplan die Version aus dem Repository zu verwenden.

Installation aus dem Werkzeugverzeichnis:

```bat
py -3 -m pip install -r requirements-relay.txt
```

oder unter Linux/macOS:

```sh
python3 -m pip install -r requirements-relay.txt
```

Einrichtung und Testlauf unter Windows:

```bat
Start-Timed-AB-Relay-Switch.cmd --setup
Start-Timed-AB-Relay-Switch.cmd --dry-run
```

Einrichtung und Testlauf unter Linux/macOS:

```sh
chmod +x ./Start-Timed-AB-Relay-Switch.sh
./Start-Timed-AB-Relay-Switch.sh --setup
./Start-Timed-AB-Relay-Switch.sh --dry-run
```

Ein kleines USB-Relais sollte die HF normalerweise nicht direkt schalten. Es sollte ein für die Aufgabe ausreichend dimensioniertes HF-Schaltsystem oder -Relais ansteuern. Prüfe Spannung, Strom, Polarität, ausfallsicheren Zustand, HF-Leistung, Isolation und Verriegelungen.

<a id="sec-b-3"></a>
<a id="sec-sequential-tx-setup-3"></a>
#### C.3 Zeitplanbeispiel für Ultimate3S

Der QRP Labs Ultimate3S kann eine Folge von WSPR-Einträgen abarbeiten und pro Eintrag einen `Aux`-Ausgang für externe Umschalthardware setzen. Beginnt eine Folge aus zwei Einträgen um `00`, kann ein globaler 10-Minuten-Frame das Target um `00` und die Referenz um `02` senden und anschließend bis zum nächsten Sequenzstart um `10` pausieren; in WSPRadar entspricht das `Wiederholintervall = 10`, `Target-Start = 00`, `Referenz-Start = 02`. Dieselbe Anordnung mit einem globalen 20-Minuten-Frame ergibt für jeden Pfad eine Wiederholung alle 20 Minuten bei weiterhin zwei Minuten A/B-Abstand.

Laut Ultimate3S-Handbuch hat `Start = 00` die besondere Bedeutung „not used“. Prüfe deshalb die angezeigte und tatsächlich beobachtete UTC-Folge und trage deren wirkliche Phasen ein, statt eine wörtliche Zuordnung von Einstellung zu Uhrzeit anzunehmen. Die `Aux`-Leitungen werden gemeinsam mit Displaysignalen genutzt; verwende den dokumentierten gefilterten Treiber oder eine geeignete Relaisschnittstelle und schalte ausschließlich in der sendefreien Zeit <a href="#ref-12">[Ref-12]</a>.

<a id="sec-b-4"></a>
<a id="sec-sequential-tx-setup-4"></a>
#### C.4 Zeitplanbeispiele für QMX

Ein QMX mit `Frame = 10`, `Start = 0` sendet um `00, 10, 20, 30, 40, 50`. Schaltet ein externer Umschalter diese Aussendungen abwechselnd auf zwei Pfade, liegt das Target bei `00, 20, 40` und die Referenz bei `10, 30, 50`; jeder Pfad wiederholt sich alle 20 Minuten. Trage deshalb `Wiederholintervall = 20`, `Target-Start = 00`, `Referenz-Start = 10` ein; verwende nicht `10 / 00 / 02`.

Mit diesem Bakenscheduler kann ein einzelner QMX kein benachbartes Paar `00/02` mit anschließender achtminütiger Pause erzeugen. Zwischen den beiden Pfaden in benachbarten Zwei-Minuten-Slots könnte ein einzelner QMX nur wechseln, indem er alle zwei Minuten sendet, wovon das QMX-Handbuch wegen der unangemessen hohen Netzbelegung abrät. Zwei unabhängig geplante QMX mit `Frame = 10` und den Starts `00` beziehungsweise `02` setzen hingegen den WSPRadar-Zeitplan `10 / 00 / 02` um; ihre Sendeketten und tatsächlichen Leistungen müssen dann jedoch als getrennte Hardware kontrolliert werden <a href="#ref-12">[Ref-12]</a>.

<a id="sec-b-5"></a>
<a id="sec-sequential-tx-setup-5"></a>
#### C.5 Zuordnung prüfen und Versuch dokumentieren

Vor dem Senden:

* ohne HF-Leistung testen;
* Polarität des Target- und Referenzpfads prüfen;
* sicherstellen, dass während einer WSPR-Aussendung nicht umgeschaltet wird;
* eine Kunstantenne (Dummy Load) oder einen Durchgangs-/SWR-Test mit geringer Leistung verwenden;
* Relaiskanal, Polarität, Vorlaufzeit, tatsächlichen Sendeplan, Zeitplanzuordnung und Pfadbelegung dokumentieren.

Schaltverlust, Isolation, Steckverbinder, Unterschiede der Speiseleitungen und das Antennenumfeld bleiben Bestandteil des Ergebnisses. Ein Tausch der Antennen zwischen den Schaltpfaden kann helfen, Antenneneffekte von Pfadeffekten zu trennen. Eine Wiederholung mit vertauschten Zeitplanzuordnungen kann Zeit- oder rollenspezifische Effekte sichtbar machen.

<div style="page-break-before: always;"></div>

<a id="sec-c"></a>
````

#### Original docs/doc_de.py:2169 — Anhang D: Referenz-SNR-Kalibrierung

Integrated approved Reference terminology, location resolution or shared interpretation. See the disposition table for the retained authoritative destination.

````text
### Anhang D: Referenz-SNR-Kalibrierung
````

## Standalone scheduler extraction: engineering-guide removals

The user explicitly approved removing the scheduler and its associated WSPRadar documentation. The following former repository-integration descriptions are retired. The standalone tool's operating instructions are preserved with the separately exported utility; external device literature and historical scientific evidence remain unchanged. No additional manual formulas or active manual anchors were removed in this follow-up.

### Former docs/architecture.md: Separate Relay Utility

````text
### Separate Relay Utility

`tools/Timed-AB-Relay-Switch/` is a separate console program for timed USB HID
relay switching. It has independent requirements, configuration, wrappers, and
operating risks. The Streamlit application neither imports nor starts it.
````

### Former docs/architecture.md: Relay Utility Services

````text
### Relay Utility Services

The separate timed relay tool uses HID hardware and can use network time. Those
dependencies are isolated from the Streamlit application and are documented in
the tool directory.
````

### Former AGENT_README.md: separate utility paragraph

````text
The separate `tools/Timed-AB-Relay-Switch/` utility has its own README,
requirements, launch wrappers, and local configuration. Do not assume that
changes to it are exercised by the Streamlit regression suite.
````

## Follow-up: remove optional Reference context and declaration gate

On 2026-09-28 the user explicitly removed the optional Reference context input and its controlled-setup cross-grid confirmation. The same deletion was applied to English and German Section 4.3 and the engineering guides. The source model remains parallel co-authored manuals. No headings, anchors, formulas or links changed; both language counterparts were reviewed together. The location ambiguity chooser, Target-QTH mismatch check, physical-site uncertainty and controlled-versus-independent scientific advice remain. No intentional semantic divergence was introduced.

Changed semantic units: the optional control-table row; the sentence describing persisted optional intent; and the cross-grid declaration/confirmation sentences. The remaining metadata uncertainty sentence now refers to reported locators instead of a removed prompt. The original passages below are verbatim, including surrounding text retained in the revised paragraphs.

### `docs/doc_en.py`

Before SHA-256: `45a034dd8b9379c62d86f7620f55a0d8f23ea975a767dc6b851b2cdbbc360ef2`. After SHA-256: `420090c56a27587e715ccb07b6a94a97c3f2756394ca5266b423290b6f472e7e`.

```text
| **Reference context (optional)** | `Unspecified`; `Controlled setup`; `Independent station` | Reference Setup/Station | Optional context for interpretation and calibration; it does not change evidence selection or calculations. |
```

```text
One grid-4 is not proof of one physical site. Different fine locators within it remain visible as reported variants; a coarse/fine combination may be geographically compatible without proving one transmitter or receiver. Discovery does not merge the remote peer identities used for pairing. The optional Reference context records `Unspecified`, `Controlled setup` or `Independent station`; it changes the interpretation and calibration context, not scientific matching.

If a declared controlled setup has a Reference grid different from the Target grid, WSPRadar pauses for an explicit decision: review the identities and locations, or continue as a comparison of complete independent stations. Different reported grids can reflect separate sites or incorrect archive metadata; the prompt does not prove which explanation applies. If no eligible Target reports match the entered Target QTH, review the inputs; the analysis origin is never changed automatically.
```

### `docs/doc_de.py`

Before SHA-256: `5d62ce3ec1c363fef9a800028f3666d5b4d2a267006e7b4c977a41a4714e0594`. After SHA-256: `79118209e35fccabb816d8b74e836a12edf05dbaec066c580fc917e7e2381c9e`.

```text
| **Referenzkontext (optional)** | `Nicht angegeben`; `Kontrollierter Aufbau`; `Unabhängige Station` | Referenzaufbau/<br>-station | Optionaler Kontext für Interpretation und Kalibrierung; verändert weder Evidenzauswahl noch Berechnungen. |
```

```text
Ein Grid-4 beweist keinen einzelnen physischen Standort. Unterschiedliche Feinlocator darin bleiben als gemeldete Varianten sichtbar; eine Kombination aus grobem und feinem Locator kann geografisch vereinbar sein, ohne einen einzigen Sender oder Empfänger zu beweisen. Die Suche führt die entfernten Peer-Identitäten für die Paarbildung nicht zusammen. Der optionale Referenzkontext hält `Nicht angegeben`, `Kontrollierter Aufbau` oder `Unabhängige Station` fest; er verändert Interpretations- und Kalibrierungskontext, nicht die wissenschaftliche Zuordnung.

Liegt das Referenzfeld eines angegebenen kontrollierten Aufbaus außerhalb des Target-Felds, wartet WSPRadar auf eine ausdrückliche Entscheidung: Kennungen und Standorte prüfen oder als Vergleich vollständiger unabhängiger Stationen fortfahren. Unterschiedliche gemeldete Felder können getrennte Standorte oder falsche Archivmetadaten bedeuten; der Hinweis beweist keine der beiden Erklärungen. Passen keine geeigneten Target-Meldungen zum eingegebenen Target-QTH, prüfe die Eingaben; der Analyseursprung wird niemals automatisch geändert.
```

### `docs/architecture.md`

```text
configuration with a resolved grid retains that selection. If a declared controlled
setup resolves to a different grid, the UI requires review or an explicit change to
the independent-station interpretation; this does not introduce another reducer.

The optional `reference_intent` in comparison parameters is `unspecified`,
`controlled_setup` or `independent_station`. It documents experimental interpretation
without changing `AnalysisContext`, SQL or scientific identity. Reference Neighbourhood
uses the Local Median algorithm. All Benchmark pairing is same-cycle; scheduled TX
```

```text
six-character QTH remains the geographic origin. Both fixed-reference experiment
intents use the same matching contract; `reference_intent` stays outside the scientific
context. Target and Reference roles do not replace their scientific identity fields.
```

### `AGENT_README.md`

```text
The optional `reference_intent` (`unspecified`, `controlled_setup`, `independent_station`)
is presentation context and does not change pairing or `AnalysisContext`.
```

## Follow-up: initial Benchmark choice and retained experiment distinction

The user requested Reference Setup/Station as the initial design when RX/TX Benchmark is selected without an existing design, preserving a valid existing Reference Neighbourhood selection. Section 4.3 documents the same behavior in both languages. Section 2.3.1 retains both controlled-setup and independent-station explanations, calibration, crossover and causal limits, with one paired sentence making the intended tested-item difference explicit. Section 4.1 corrects obsolete disabled-Run wording and removes retired TX-schedule state from demo lifecycle; Section 5.1 replaces obsolete schedule-to-path troubleshooting with simultaneous TX frequency placement. The engineering guides describe the same current defaults and validation. These are narrow current-contract corrections; no headings, anchors, links, formulas or scientific calculations changed.

The affected semantic units were reviewed together in the parallel co-authored English/German source model; no intentional language divergence exists. The original changed passages are recorded verbatim below.

### `docs/doc_en.py`

Before SHA-256: `420090c56a27587e715ccb07b6a94a97c3f2756394ca5266b423290b6f472e7e`. After SHA-256: `e0da8739d5961410a62e17763d88efe6fe4faa2f70bceb13e537058a2a8ae75c`.

```text
Use this design for two local antennas, feedlines, filters, preamplifiers, receivers or complete receive chains operated simultaneously at the same physical test QTH. Target and Reference need distinct exact reporting callsigns. Verify that the resolved Reference location agrees with the actual experiment. Components intended to be common must be physically common; shared grid-4 matching does not prove co-location or path equality.
```

```text
| **`Run RX Analysis` / `Run TX Analysis`** | Runs the selected Performance or Benchmark result from the terminal Review panel in Guided and Classic. | Running remains unavailable until the Question and, for a Benchmark, the Benchmark design are complete. Changing a scientific control after a run clears the result and requires a new run. |
```

```text
**Demo context lifecycle.** A loaded demo keeps its visible context when only population filters, evidence thresholds, Inspector scope or other result-view controls are changed, so an adapted view can still be interpreted against the example from which it began. Changing the Question or direction, Target callsign or QTH, band, measurement window, Benchmark design or identity, neighborhood radius, TX schedule, or correction intent/value removes the demo metadata and profile identity from later saves because the setup no longer represents that documented experiment. Any scientific edit also ends exact-demo cache identity, even when the explanatory demo context remains visible. A population- or evidence-changing scientific edit clears any preselected Performance and Benchmark Station Insights identity; the path may no longer exist in the new result. Result-view-only controls do not clear that selection.
```

```text
For `RX Benchmark` and `TX Benchmark`, Classic displays a third panel named **`Benchmark design`** and requires one of:
```

```text
7. **Design mechanics:** clock synchronization, TX schedule-to-path mapping, switching, signal routing, actual and reported power.
```

### `docs/doc_de.py`

Before SHA-256: `79118209e35fccabb816d8b74e836a12edf05dbaec066c580fc917e7e2381c9e`. After SHA-256: `23cc25f6947f54a418e082c6e39ab05aebd4a3eb9545a219ff01288b00bde1c4`.

```text
Verwende dieses Design für zwei lokale Antennen, Speiseleitungen, Filter, Vorverstärker, Empfänger oder vollständige Empfangsketten, die gleichzeitig am selben physischen Test-QTH betrieben werden. Target und Referenz benötigen unterschiedliche exakte Melderufzeichen. Prüfe, ob der aufgelöste Referenzstandort zum tatsächlichen Versuch passt. Komponenten, die gemeinsam sein sollen, müssen physisch gemeinsam genutzt werden; die Zuordnung zum selben Grid-4 beweist weder Ko-Lokation noch Gleichheit der Pfade.
```

```text
| **`RX-Analyse starten` / `TX-Analyse starten`** | Führt in der geführten und klassischen Eingabe das ausgewählte Performance- oder Benchmark-Ergebnis aus dem abschließenden Prüfbereich aus. | Das Starten bleibt unverfügbar, bis die Frage und bei einem Benchmark zusätzlich das Benchmark-Design vollständig sind. Eine Änderung eines wissenschaftlichen Bedienelements nach dem Lauf verwirft das Ergebnis und verlangt einen neuen Lauf. |
```

```text
**Lebenszyklus des Demo-Kontexts.** Eine geladene Demo behält ihren sichtbaren Kontext, wenn nur Populationsfilter, Evidenzschwellen, Inspektor-Bereich oder andere Bedienelemente der Ergebnisansicht geändert werden. Eine angepasste Ansicht lässt sich dadurch weiterhin vor dem Hintergrund des ursprünglichen Beispiels deuten. Änderungen an Frage oder Richtung, Target-Rufzeichen oder -QTH, Band, Messzeitraum, Benchmark-Design oder -Identität, Nachbarschaftsradius, TX-Zeitplan sowie Absicht oder Wert der Korrektur entfernen Demo-Metadaten und Profilidentität aus später gespeicherten Konfigurationen, weil der Aufbau nicht mehr dem dokumentierten Versuch entspricht. Jede wissenschaftliche Änderung beendet außerdem die exakte Demo-Cache-Identität, auch wenn der erklärende Demo-Kontext sichtbar bleibt. Eine wissenschaftliche Änderung der Population oder Evidenz löscht jede vorausgewählte Performance- und Benchmark-Identität in Station Insights, da der Funkweg im neuen Ergebnis fehlen kann. Reine Bedienelemente der Ergebnisansicht löschen diese Auswahl nicht.
```

```text
Für `RX-Benchmark` und `TX-Benchmark` zeigt die Klassische Eingabe einen dritten Bereich namens **`Benchmark-Design`** und verlangt eine der folgenden Auswahlen:
```

```text
7. **Versuchsmechanik:** Uhrensynchronisation, Zuordnung des TX-Zeitplans zu den Pfaden, Umschaltung, Signalführung sowie tatsächliche und gemeldete Leistung.
```

### `docs/architecture.md`

```text
not an edit and therefore does not by itself retire demo provenance. A newly
selected Benchmark may therefore have valid transient RX/TX Benchmark intent
while canonical `val_comp_mode` remains
`none` until Reference Setup/Station or Reference Neighbourhood is chosen.
During that incomplete state, Run, Save Config, and public-URL synchronization
are gated, while the advanced panel explicitly routes Benchmark thresholds, so
the canonical `none` value cannot be misrepresented as an intentional
Performance configuration. Correction mode is
```

### `AGENT_README.md`

```text
the shared Target/window fields and conditionally requires a Benchmark design.
While Benchmark intent is selected but its design is still absent, Run, Save
Config, and public-URL synchronization remain gated, while the advanced panel
explicitly uses Benchmark thresholds rather than interpreting canonical
`val_comp_mode = "none"` as an operator-selected Performance setup. Correction
```

## Final narrow copy correction after context removal

Removed the last English/German sentence implying an explicit declaration of Reference intent from Section 1.2. Both now state that controlled and independent arrangements use the same pairing algorithm. Removed one duplicate German fixed-Reference bullet whose complete-station meaning remains in the immediately preceding merged explanation. Section 2.3.1 retains the scientific distinction and calibration limits. No field-placement or pre-lookup location-caption promise exists in the manuals, so the subsequent input-column change requires no copy edit. Changed units were reviewed together; no intended language divergence, anchor, formula or link change.

### `docs/doc_en.py`

Replaced original sentence:

```text
Declaring this intent documents interpretation; it does not select a different pairing algorithm.
```

Before SHA-256: `e0da8739d5961410a62e17763d88efe6fe4faa2f70bceb13e537058a2a8ae75c`. After SHA-256: `09ebb06c78bc7e4c2de508e1043c99aa093b753a1931050f43ec28f3fad1149f`.

### `docs/doc_de.py`

Replaced original sentence:

```text
Die Angabe dieser Absicht dokumentiert die Interpretation; sie wählt keinen anderen Paarbildungsalgorithmus.
```

Duplicate original bullet, merged meaning retained:

```text
* **Referenzaufbau/-station** vergleicht vollständig aufgebaute Stationen und ihre Betriebsumgebungen.
```

Before SHA-256: `23cc25f6947f54a418e082c6e39ab05aebd4a3eb9545a219ff01288b00bde1c4`. After SHA-256: `7fc2c58d20d8d6aa7965479909289ae8a45b51c9ba1cd8585a25b87a7f11fb78`.
