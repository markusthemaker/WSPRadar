# docs/drafts/doc_en_candidate.py

"""Complete reviewed English manual candidate built from the production manual.

The candidate deliberately inherits unchanged content from ``docs.doc_en`` and
applies explicit, assertion-checked replacements to sections reviewed during the
manual-structure pass. Running this module prints the complete candidate manual.

Baseline production commit: 78e286d312890bb0bbe5c512f8557962bb083c52
Baseline docs/doc_en.py blob: da1fb29f948811483193a8d3c2adcfecb645f856
"""

from __future__ import annotations

from pathlib import Path
import sys

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

from docs.doc_en import DOC_EN as _PRODUCTION_DOC_EN  # noqa: E402


def _replace_section(
    document: str,
    start_marker: str,
    end_marker: str,
    replacement: str,
) -> str:
    """Replace one unique anchor-bounded section and retain the end marker."""

    if document.count(start_marker) != 1:
        raise ValueError(f"Expected one start marker: {start_marker!r}")
    start_index = document.index(start_marker)
    end_index = document.index(end_marker, start_index + len(start_marker))
    return (
        document[:start_index]
        + replacement.rstrip()
        + "\n\n"
        + document[end_index:]
    )


def _replace_exact(document: str, old: str, new: str) -> str:
    """Replace one exact passage and fail if the production baseline has drifted."""

    if document.count(old) != 1:
        raise ValueError(f"Expected one exact passage, found {document.count(old)}: {old!r}")
    return document.replace(old, new, 1)


DOC_EN = _PRODUCTION_DOC_EN

if "### 0. Why WSPRadar?" not in DOC_EN:
    raise ValueError("The production Part 0 baseline is not the reviewed version.")

# Part 0: retain production wording, with one causal-language correction.
DOC_EN = _replace_exact(
    DOC_EN,
    "The map locates the effect; it is the start of the analysis, not the conclusion.",
    "The map locates the observed pattern; it is the start of the analysis, not the conclusion.",
)

# Table of Contents headings affected by the review.
DOC_EN = _replace_exact(
    DOC_EN,
    "    * [2.3 Use the map to locate the effect](#sec-3-4)",
    "    * [2.3 Use the map to locate the observed pattern](#sec-3-4)",
)
DOC_EN = _replace_exact(
    DOC_EN,
    "    * [3.1 Recognize broad and stable evidence](#sec-4-1)",
    "    * [3.1 Judge breadth, Stability and repeatability](#sec-4-1)",
)
DOC_EN = _replace_exact(
    DOC_EN,
    "* [Appendix B: Timed A/B Relay Switch](#sec-b)",
    "* [Appendix B: Sequential TX A/B Scheduling and Switching](#sec-b)\n"
    "    * [B.1 Requirements for a valid scheduled experiment](#sec-b-1)\n"
    "    * [B.2 WSPRadar Timed A/B Relay Switch](#sec-b-2)\n"
    "    * [B.3 Ultimate3S schedule example](#sec-b-3)\n"
    "    * [B.4 QMX schedule examples](#sec-b-4)\n"
    "    * [B.5 Verify mapping and preserve the experiment](#sec-b-5)",
)

# Part I introduction and Section 1.1.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="part-i"></a>',
    '<a id="sec-2-2"></a>',
    r'''<a id="part-i"></a>

## Part I: Operator Guide

This part takes you from an operating question to a well-supported result. Use Chapter 1 to choose and operate the experiment, Chapter 2 to inspect the evidence, and Chapter 3 to strengthen, report and preserve the conclusion. Exact controls, processing methods and reproducibility details are collected in Parts II and III.

In this guide, the **experiment** is the physical on-air operation and station configuration. A **run** or **analysis** is WSPRadar's configured processing of the resulting observations. A **result** is the Success or Compare evidence produced by that run.

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
* Enter callsigns exactly as uploaded, including any valid `/P`, `/1` or `/QRP` suffix.
* Verify the Target QTH. Success identifies the Target using the exact callsign together with the first four locator characters.
* Select a UTC window in which the Target was actually operating. Use a window long enough to cover the propagation states named in the intended conclusion; multi-day runs are preferable when the conclusion spans complete daily cycles.
* Record the antennas, feedlines, tuner, transmitter or receiver, decoder, software version, power, schedule and intentional changes.

Every run uses one exact band; combining bands would mix different propagation, activity, station populations and observability.

**Keep the physical experiment stable**

* Keep every non-tested variable as stable as practical.
* Keep station clocks synchronized.
* For TX, keep actual and reported power synchronized and stable unless power itself is under test. WSPR is commonly operated at low power; `20-30 dBm` corresponds to approximately `0.1-1 W`.
* For RX, keep gain, filtering, audio routing, decoder settings and upload behavior stable unless one of those is the tested variable.
* Confirm that each benchmark side operates as intended. The <strong class="defined-term">Target-Active Gate</strong> protects periods without observable Target activity, but it does not prove Reference uptime.

For an exploratory run, use the evidence ladder in [Chapter 2](#sec-3) to identify a possible pattern. Before a confirmatory repetition, define the primary geographic and temporal scope and keep direction, band, benchmark, filters, thresholds and schedule fixed unless the change itself is part of the stated test.''',
)

# Section 1.2.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-2-2"></a>',
    '<a id="sec-2-3"></a>',
    r'''<a id="sec-2-2"></a>

#### 1.2 Success only: explore Target reach

**Question answered**

Where, when and how consistently does the Target produce qualifying evidence among remote stations or signals independently shown to be active, and what SNR is observed for successful Target decodes?

**What WSPRadar shows**

For this playbook, <strong class="defined-term">qualifying evidence</strong> is the Target and independent activity evidence retained after the run's identity, band, time, Target-activity, filter and threshold rules.

* **RX Success** compares Target receiver decodes with independently confirmed remote transmitter-cycles.
* **TX Success** compares Target transmitter decodes with remote receiver-cycles shown to contain other same-band activity.

There is no Reference station or Setup B. Success Rate describes conditional reach; successful Target SNR is a separate signal-strength summary. [Section 2.1](#sec-3-2) explains the operator classifications and weighting, and [Section 7.4](#sec-7-4) defines the exact denominator.

**Set up the analysis**

Choose `RX Analysis` or `TX Analysis`, enter the exact Target callsign and QTH, choose one band and an active UTC window, then select `No benchmark (Success only)`.

**Strengthen the evidence**

Use an operating window with observable Target activity and enough independent WSPR activity. Check geographic scope, Stations, Spots and time views. If only a few peers survive, extend the observation window or narrow the geographic or temporal scope of the conclusion. Change filters or thresholds only for a stated experimental reason and report the changed configuration as a separate run.

**Evidence-matched conclusion**

> For this Target, band, UTC window and selected peer population, the displayed Success Rate summarizes the fraction of independently confirmed global WSPR-network opportunities in which the Target also produced qualifying evidence, calculated per peer and then balanced across qualifying peers.

In everyday station terms: among the worldwide WSPR activity that this run could independently verify and fairly test, the result shows how consistently your station also produced the expected TX or RX evidence. The successful-decode SNR view separately shows the signal strengths of the Target evidence that was actually decoded.''',
)

# Section 1.3.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-2-3"></a>',
    '<a id="sec-2-4"></a>',
    r'''<a id="sec-2-3"></a>

#### 1.3 RX Hardware A/B: compare simultaneous receive paths

**Question answered**

Did two local receive paths differ while observing the same remote WSPR transmissions?

For a radio amateur, this can mean comparing two antennas, each feeding its own independently reporting receiver/decoder chain; two receivers fed from one antenna through a characterized splitter; preamplifiers, filters or feedlines; or two complete parallel receive chains.

**What WSPRadar shows**

Simultaneous RX Hardware A/B compares two local receiving paths at one station. Setup A and Setup B observe the same remote transmitter identities in the same WSPR cycles. This is WSPRadar's closest design to a controlled same-signal hardware comparison.

Unless receiver, audio and decoder differences have been characterized, the result compares the complete receive paths rather than the antennas alone.

**Set up the experiment**

Select the UI choice `Hardware A/B-Test (Local Setup)` and operate two receivers simultaneously with different exact reporting callsigns:

* Setup A uses the Target callsign.
* Setup B uses the `Setup B Callsign`.

Keep clocks, antenna routing, gain, audio paths, decoder settings and uploads controlled. Components intended to be common must be physically common; measure or document unavoidable differences between the two chains.

The run produces an RX Hardware Compare result and the Target's separate RX Success result.

**Strengthen the evidence**

Document splitter balance, feedline differences, receiver gain, automatic gain control (AGC) behavior, clipping, decoder configuration and upload behavior. A measured Reference SNR correction can compensate for a stable offset; it cannot correct nonlinear or time-varying behavior.

[Appendix A](#sec-a) describes parallel WSJT-X instances. [Appendix C](#sec-c) describes Reference SNR calibration.

**Evidence-matched conclusion**

> Under the documented simultaneous RX setup, paired Delta SNR showed the observed difference between receive paths A and B for the shared transmitters, cycles and geographic scope.

In everyday station terms: for remote signals that both paths observed at the same time, the result shows which receive path tended to produce stronger decodes, where that difference appeared and how much shared evidence supported it.''',
)

# Section 1.4.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-2-4"></a>',
    '<a id="sec-2-5"></a>',
    r'''<a id="sec-2-4"></a>

#### 1.4 TX Hardware A/B: compare alternating transmit paths

**Question answered**

Did two local antennas, feedlines or switched RF paths differ when driven by one common station setup?

<a id="sec-2-4-why"></a>

**Why deterministic alternation is used**

When two nearby antennas radiate the same WSPR waveform and callsign in the same cycle and frequency channel, a remote receiver observes their combined field. Its spot cannot identify how much came from antenna A or B. Distinguishable simultaneous signals normally require separate callsigns and transmitter chains, introducing additional power, calibration, timing and frequency differences.

Deterministic alternation instead retains one callsign and preferably one common transmitter chain while exposing both paths repeatedly to changing propagation and receiver conditions. It remains a sequential comparison: shorter separation reduces the time available for conditions to change, but does not make the observations simultaneous.

**What WSPRadar shows**

Sequential TX Hardware A/B assigns complete WSPR transmissions to Setup A and Setup B from a time-locked schedule. WSPRadar then forms deterministic one-to-one scheduled pairs for each remote receiver identity and reports scheduled-pair Delta SNR plus one-sided Decode Outcomes.

**Set up the experiment**

Use the station's normal valid exact callsign for both paths. Path identity comes from the deterministic UTC schedule, not from `/1` and `/2` suffixes or different reported powers.

In `TX A/B Schedule`, enter each physical path's **actual recurrence and UTC phase**. Do not infer those values solely from a transmitter's `Frame` label. Use a deterministic scheduler or controller; standard WSJT-X randomized transmit-percentage operation does not create a valid fixed A/B sequence. Exact controls and supported phases are in [Section 4.3](#sec-5-3), while device-specific schedules and switching procedures are in [Appendix B](#sec-b).

WSPRadar forms scheduled pairs automatically. Exact pair assignment, edge-window eligibility and micro-median aggregation are defined in [Sections 7.1](#sec-7-1) and [7.7](#sec-7-7).

Report the actual transmit power. Do not encode path identity through false reported-power values: TX normalization would turn an invented power difference into an artificial comparison offset. [Section 7.5](#sec-7-5) defines the calculation, and [Appendix C](#sec-c) describes defensible Reference-side calibration.

Verify the physical schedule-to-path mapping without RF before starting. A reversed mapping labels the paths backwards and reverses the practical interpretation of the Delta SNR sign.

The run produces a sequential TX Hardware Compare result and a separate TX Success result. Success is limited to the configured Target schedule and therefore describes Setup A.

**Strengthen the evidence**

Control switch loss, feedline differences, antenna coupling, clock accuracy, schedule-to-path mapping and switching timing. Use the shortest practical separation and extend the run across the propagation periods relevant to the question.

Across a balanced run, random short-term variation may average down because both paths are repeatedly exposed to changing conditions. Systematic schedule-, switching- or time-of-cycle effects do not necessarily average down. When a small difference matters, repeat the experiment with the A/B schedule assignments reversed and compare like-for-like runs as described in [Section 3.2](#sec-4-2).

[Section 6.3](#sec-d-toledo) gives the experimental lineage and explains why short alternation is preferable to long blocks <a href="#ref-3">[Ref-3]</a>.

**Evidence-matched conclusion**

> Under the documented time-locked schedule, scheduled-pair Delta SNR showed the observed difference between switched paths A and B for the selected receivers, times and geographic scope.

In everyday station terms: after repeatedly alternating the two RF paths, the result shows whether path A or B tended to produce stronger reports for the receivers and propagation periods represented in the run, while remaining sequential rather than simultaneous.''',
)

# Section 1.5.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-2-5"></a>',
    '<a id="sec-2-6"></a>',
    r'''<a id="sec-2-5"></a>

#### 1.5 Reference Station / Buddy Test

**Question answered**

How did the Target station compare with one known external station during overlapping operation?

**What WSPRadar shows**

A Buddy Test compares two complete installed station systems. The comparison includes their locations, antennas, feedlines, transmitters or receivers, local noise, terrain, software and operating environments.

* In TX, Target and Reference are compared at the same remote receiver when both were decoded in the same cycle.
* In RX, Target and Reference receivers are compared on the same remote transmitter identity in the same cycle.

Same-cycle TX pairs therefore share one remote receiver, while RX pairs share one remote transmitter. This controls one endpoint of the comparison; it does not remove differences in QTH, radio path, station hardware, terrain or local noise.

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

In everyday station terms: this shows how your complete on-air station performed against your buddy's complete station on shared paths; it does not assign the observed difference to one antenna, receiver or location by itself.''',
)

# Section 1.6.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-2-6"></a>',
    '<a id="sec-2-7"></a>',
    r'''<a id="sec-2-6"></a>

#### 1.6 Local Median Neighborhood

**Question answered**

How does the Target compare with the typical active WSPR evidence from stations around its configured QTH?

**What WSPRadar shows**

Local Median Neighborhood forms a dynamic Reference from active station identities inside the selected radius. For each qualifying cycle and path, the neighborhood median represents the active local group without allowing one high-volume identity to dominate.

The Reference can change from cycle to cycle. It is a local activity benchmark rather than one fixed or calibrated station.

**Set up the analysis**

Select `Local Neighborhood Benchmark`, choose a radius from 10 to 250 km and choose `Local Median Neighborhood` under `Local Benchmark Method`.

Verify the Target callsign and QTH because they determine Target exclusion from the local pool and define the radius origin. Choose the primary radius from local geography and expected station density before interpreting the result; it should have a clear local meaning and enough active identities.

The run produces a Local Compare result and the Target's separate non-comparative Success result.

**Strengthen the evidence**

Inspect which local identities contribute and their evidence counts. Alternative scientifically defensible radii can be reported as a sensitivity analysis: a smaller radius can describe a more similar local environment but leave a fragile pool, while a larger radius can add contributors but mix different terrain, noise and station conditions. Do not retain only the radius producing the most favorable result.

Local stations can differ in antenna, hardware, schedule and reported-power accuracy. Report the primary radius, method, contributors, evidence counts and any sensitivity runs.

**Evidence-matched conclusion**

> Relative to the active median neighborhood inside the selected radius, the Target showed the displayed paired Delta SNR and Decode Outcomes for the observed paths and cycles.

In everyday station terms: this shows whether your station tended to perform above, near or below the typical active nearby WSPR group for the paths and times both sides could compare.''',
)

# Section 1.7.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-2-7"></a>',
    '<a id="sec-3"></a>',
    r'''<a id="sec-2-7"></a>

#### 1.7 Local Best Station

**Question answered**

How does the Target compare with the strongest active local Reference available for each qualifying path and cycle?

**What WSPRadar shows**

Local Best Station forms a changing best-peer envelope from active station identities inside the selected radius. It is intentionally stricter than the neighborhood median and does not represent a local average.

**Set up the analysis**

Select `Local Neighborhood Benchmark`, choose a radius from 10 to 250 km and choose `Local Best Station` under `Local Benchmark Method`.

Verify the Target callsign and QTH. Choose the primary radius from local geography and expected station density before interpreting the result; it must retain a meaningful and adequately populated local pool.

The run produces a Local Compare result and the Target's separate non-comparative Success result.

**Strengthen the evidence**

Inspect the changing local Reference contributors. Alternative scientifically defensible radii can be reported as a sensitivity analysis when the conclusion depends strongly on pool membership; do not retain only the radius producing the most favorable comparison.

Local contributors can differ in terrain, equipment, noise, schedule and reported-power accuracy. Report the changing best-peer definition rather than describing the result as a comparison with one fixed station.

**Evidence-matched conclusion**

> Relative to the strongest active local Reference selected for each qualifying path and cycle inside the stated radius, the Target showed the displayed paired Delta SNR and Decode Outcomes.

In everyday station terms: this shows how your station compared with the strongest qualifying nearby station available on each path and cycle, rather than with one permanently fixed competitor.

Exact local-pool membership and aggregation rules are in [Sections 7.2](#sec-7-2) and [7.7](#sec-7-7).''',
)

# Chapter 2 evidence-ladder language.
DOC_EN = _replace_exact(
    DOC_EN,
    "* Use the map to locate the effect.",
    "* Use the map to locate the observed pattern.",
)

# Section 2.2.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-3-3"></a>',
    '<a id="sec-3-4"></a>',
    r'''<a id="sec-3-3"></a>

#### 2.2 Read a Compare result

Compare keeps two evidence questions separate.

**Delta SNR**

Delta SNR asks: when Target and Reference both produced comparable evidence, which side had the stronger SNR and by how much?

In the operator view, Delta SNR is the Target-side SNR minus the corrected Reference-side SNR. The exact equation and correction convention are in [Section 7.5](#sec-7-5). Positive values favor the Target; negative values favor the Reference.

Paired Delta SNR is normally the primary quantitative comparison because the two sides share the closest available conditions:

* In simultaneous RX Compare, Target and Reference receivers measure the same remote transmitter. This reduces transmitter-power, waveform and shared-path differences within the pair.
* In same-cycle TX Compare, such as applicable Buddy or Local Neighborhood comparisons, the same remote receiver measures Target and Reference. This reduces receiver-hardware, antenna, local-noise and reporting differences within the pair.
* Sequential TX Hardware A/B uses deterministic scheduled pairs rather than same-cycle evidence.

**Decode Outcomes**

Decode Outcomes show joint and one-sided evidence inside and outside the paired subset:

* <strong class="defined-term">Joint / Joint Spots / Joint Pairs:</strong> qualifying paired evidence exists.
* <strong class="defined-term">Only Target:</strong> Target evidence exists without Reference evidence in the relevant comparison unit.
* <strong class="defined-term">Only Reference:</strong> Reference evidence exists without Target evidence.
* <strong class="defined-term">Both (Async):</strong> both sides have evidence for the peer identity, but no qualifying joint unit survives for that category.

Use Delta SNR to describe the paired strength difference and Decode Outcomes to describe the joint and one-sided decode evidence. A result can have a clear paired median while retaining substantial one-sided evidence; both observations belong in the conclusion.

Decode Outcomes do not reconstruct or power-normalize a missing-side SNR. In TX comparisons, interpret one-sided outcomes together with actual and reported transmit power. [Section 7.6](#sec-7-6) defines this boundary.

Same-cycle pairing reduces shared confounders but does not make separated stations or different hardware chains physically identical. In same-cycle comparisons, the Target-Active Gate protects Target downtime from being counted as failure, while Reference uptime still needs independent confirmation.''',
)

# Section 2.3.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-3-4"></a>',
    '<a id="sec-3-5"></a>',
    r'''<a id="sec-3-4"></a>

#### 2.3 Use the map to locate the observed pattern

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

Map color locates the observed pattern. The following evidence levels show how broad and well-supported it is.''',
)

# Section 2.4 analysis-identity warning.
DOC_EN = _replace_exact(
    DOC_EN,
    "Footer counts follow the visible map scope. A large number of Spots from only a few Stations means repeated evidence from a narrow identity base. Many Stations show wider identity and geographic participation.",
    "Footer counts follow the visible map scope. A large number of Spots from only a few Stations means repeated evidence from a narrow identity base. Many Stations show wider identity and geographic participation.\n\n"
    "A `callsign + locator` is an analysis identity, not proof of one unique physical station. Suffixes, stale locators and locator changes can split or move a physical station in the evidence.",
)

DOC_EN = _replace_exact(
    DOC_EN,
    "A wide or split distribution shows that the effect varies by path.",
    "A wide or split distribution shows that the observed difference varies by path.",
)
DOC_EN = _replace_exact(
    DOC_EN,
    "* Simultaneous Compare exposes same-cycle Target/Reference evidence and Delta SNR.",
    "* Same-cycle Compare exposes Target/Reference evidence and Delta SNR from the shared cycle.",
)

# Section 3.1.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-4-1"></a>',
    '<a id="sec-4-2"></a>',
    r'''<a id="sec-4-1"></a>

#### 3.1 Judge breadth, Stability and repeatability

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

Evidence is **broader** when several identities and adjacent segments agree. It is **more internally consistent** when station-balanced, observation-level and time views tell a compatible story. It is **better controlled** when the selected playbook's operating requirements were followed and documented.

<strong class="defined-term">90% Stability</strong> is a descriptive bootstrap interval around a median. A narrow interval means the displayed median changes little when the available values are resampled. Use it to describe sensitivity to the observed sample. It is not a confidence interval or statistical significance test, and it does not establish independence or eliminate data bias.

**Sample Stability and experimental repeatability are different.** The Stability interval resamples evidence already present in this run. Repeating the experiment in another suitable window tests whether the observed pattern persists under new operating and propagation conditions.

WSPRadar deliberately does not collapse these dimensions into one proof grade. The visible counts, distributions and underlying rows let the operator judge the result in the context of the actual experiment.''',
)

# Section 3.2.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-4-2"></a>',
    '<a id="sec-4-3"></a>',
    r'''<a id="sec-4-2"></a>

#### 3.2 Strengthen a result through repetition and control

Use an initial exploratory run to identify a possible pattern. Before a confirmatory repetition, freeze the direction, band, benchmark, filters, evidence thresholds, schedule and primary geographic or temporal evaluation scope. Report alternative radii or scopes as sensitivity analyses rather than retaining only the most favorable view.

When the result will support an important station decision:

* extend the observation window across the propagation states named in the conclusion;
* prefer multi-day evidence for statements spanning complete daily cycles;
* repeat the experiment on another day or propagation period;
* for sequential TX Hardware A/B, reverse the A/B schedule assignments;
* keep non-tested variables stable between repetitions;
* compare runs with the same direction, band, benchmark, filters and evidence thresholds;
* investigate any identity, locator or short interval that supplies a large fraction of the evidence;
* preserve setup notes so a later run can reproduce the station configuration.

Small observed differences become more useful when they recur across stations, time periods, adjacent segments and controlled repetitions. A reversed sequential TX assignment is especially useful because it can expose schedule-, switch-path- or time-of-cycle effects that ordinary repetition leaves in the same role.

TX and RX use different peer populations and opportunity definitions. Compare like-for-like TX and RX runs when investigating station balance or an "alligator" pattern.''',
)

# Section 3.3.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-4-3"></a>',
    '<a id="sec-4-4"></a>',
    r'''<a id="sec-4-3"></a>

#### 3.3 Write an evidence-matched conclusion

A minimum operator statement identifies the Target and Reference, TX or RX direction, band, UTC window, geographic scope, result type, displayed value and supporting station/evidence count.

A full technical report also states:

* station-balanced and observation-level values where both apply;
* Stations and Spots or joint-station and joint-spot/pair counts;
* Decode Outcomes for Compare;
* experiment conditions and any Reference correction;
* filters and evidence thresholds;
* whether the pattern repeated across time, stations or runs;
* any alternative radius or scope used as a sensitivity analysis.

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

The complete supported/unsupported wording reference is in [Chapter 8](#sec-8).''',
)

# Section 3.4 preservation additions.
DOC_EN = _replace_exact(
    DOC_EN,
    "* operating schedule;\n* calibration procedure;",
    "* operating schedule, physical schedule-to-path mapping and any reversed assignment;\n* calibration procedure;",
)

# Part II: make schedule controls the exact authoritative home.
DOC_EN = _replace_exact(
    DOC_EN,
    "Hardware A/B Test follows the selected **RX Analysis / TX Analysis** option. RX displays the two-receiver Setup B callsign; TX displays the shared Repeat Interval, two disjoint Start controls, a swap action and the resulting one-hour schedule preview. Pairing follows that schedule automatically.",
    "Hardware A/B Test follows the selected **RX Analysis / TX Analysis** option. RX displays the two-receiver Setup B callsign; TX displays the shared Repeat Interval, two disjoint Start controls, a swap action and the resulting one-hour schedule preview. Pairing follows that schedule automatically.\n\n"
    "For TX Hardware A/B, `Repeat Interval` is each physical path's actual recurrence. It is not necessarily the `Frame` label shown by a transmitter that alternates one output between two paths. Check the preview against observed on-air starts and the physical switch mapping. Device-specific examples are in [Appendix B](#sec-b); exact pair construction is in [Sections 7.1](#sec-7-1) and [7.7](#sec-7-7).",
)
DOC_EN = _replace_exact(
    DOC_EN,
    "These controls let you shape the peer population, illumination period and minimum evidence required for display.",
    "These controls let you shape the peer population, illumination period and minimum evidence required for display. Choose them from the intended population and evidence floor. Do not relax filters or thresholds after inspecting the result solely to obtain a denser or more favorable map; report a changed analysis as a separate configuration.",
)

# Section 5.2: retain symptom diagnosis, move provider/cache status to 5.6.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-6-2"></a>',
    '<a id="sec-6-3"></a>',
    r'''<a id="sec-6-2"></a>

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

An upstream-data issue changes what the selected source supplies. An experiment-design issue changes whether the retained rows answer the intended question. Diagnose and report the two separately.''',
)

# Section 5.6: add the moved System Audit Status explanation.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-6-6"></a>',
    '<div style="page-break-before: always;"></div>\n\n<a id="part-iii"></a>',
    r'''<a id="sec-6-6"></a>

#### 5.6 Working with upstream data

wspr.live states that its data is raw WSPRnet-reported data and may contain duplicates, false spots and other errors. Its volunteer infrastructure provides no guarantee of correctness, availability or stability. <a href="#ref-10">[Ref-10]</a>

wspr.live describes real-time data as available with a delay of a few minutes and says its scraper checks for new spots every few minutes. As a practical operating estimate, wait about **five minutes** after the final WSPR cycle before expecting a fresh analysis window to be reasonably populated.

Five minutes is not a completeness guarantee. Delayed uploads, ingestion interruptions and later corrections can appear after that point. <a href="#ref-10">[Ref-10]</a>

WSPRadar uses pairing, identity grouping, medians, thresholds and Drill-Down to reduce sensitivity to isolated bad rows and make them easier to inspect. Repeated plausible errors can still survive those controls.

Reported power and locators are user-supplied. Correct mathematics applied to an incorrect power or locator remains physically wrong.

**Read System Audit Status**

System Audit Status names the database origin once for the complete run. Its reason is `primary` when the first-priority source was selected, `cache affinity` when a guided demo selected a complete fresh bundle from a lower-priority provider before normal network-backed provider selection, `capacity spillover` when a lower-priority ready source admitted the complete request bundle because higher-priority request capacity could not, `failure fallback` when this run restarted after a provider-scoped failure or a higher-priority source was already unavailable during provider-health cooldown or recovery probing, or `committed source` when a rerender retained the run's already committed source.

It then reports `database request`, `RAM cache` or `disk cache` plus timing for each strict and optional historical-fallback query separately. Those delivery labels describe how rows reached the analysis; they do not identify different databases or change the origin reason.

On the same deployment, a guided demo can reuse raw provider query rows for up to 24 hours from their original fetch. Before making a new demo request, WSPRadar prefers the first configured provider that already has the complete required demo bundle cached. The cached rows retain their actual provider origin and are never combined across providers. Cache hits do not renew the deadline. A process restart loses the RAM tier, but the disk tier remains reusable if local storage survives; storage eviction can remove it sooner.''',
)

# Part III minor claim-language and checklist corrections.
DOC_EN = _replace_exact(
    DOC_EN,
    "WSPRadar supports precise statements about conditional reach, paired differences, one-sided evidence and where those effects were observed.",
    "WSPRadar supports precise statements about conditional reach, paired differences, one-sided evidence and where those observed patterns appeared.",
)
DOC_EN = _replace_exact(
    DOC_EN,
    "For a serious result, report:",
    "For a serious result, preserve and report:",
)

# Part IV introduction.
DOC_EN = _replace_exact(
    DOC_EN,
    "This part collects optional setup procedures, the timed relay helper, Reference-side calibration guidance and the project license. Use the sections that apply to your station and experiment.",
    "This part collects optional setup procedures, sequential TX A/B scheduling and switching guidance, Reference-side calibration and the project license. Use the sections that apply to your station and experiment.",
)

# Appendix B: broaden the practical supplement and move device-specific material.
DOC_EN = _replace_section(
    DOC_EN,
    '<a id="sec-b"></a>',
    '<a id="sec-c"></a>',
    r'''<a id="sec-b"></a>
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

<div style="page-break-before: always;"></div>''',
)

# Integration assertions.
_REQUIRED_PASSAGES = (
    "### 0. Why WSPRadar?",
    "## Part I: Operator Guide",
    "#### 1.4 TX Hardware A/B: compare alternating transmit paths",
    "#### 3.1 Judge breadth, Stability and repeatability",
    "#### 5.6 Working with upstream data",
    "### Appendix B: Sequential TX A/B Scheduling and Switching",
    "#### B.4 QMX schedule examples",
    "### Appendix C: Reference SNR Calibration",
)
for _required_passage in _REQUIRED_PASSAGES:
    if DOC_EN.count(_required_passage) != 1:
        raise ValueError(f"Candidate integration failed for {_required_passage!r}")

_FORBIDDEN_PASSAGES = (
    "The map locates the effect",
    "Use the map to locate the effect",
    "Use Delta SNR to describe the paired strength difference and Decode Outcomes to describe comparative reach.",
    "Over a balanced run lasting many hours or days, short-term changes repeatedly affect both sides and tend to average down.",
)
for _forbidden_passage in _FORBIDDEN_PASSAGES:
    if _forbidden_passage in DOC_EN:
        raise ValueError(f"Superseded wording remains: {_forbidden_passage!r}")


if __name__ == "__main__":
    print(DOC_EN)
