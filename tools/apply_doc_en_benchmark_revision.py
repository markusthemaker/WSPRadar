#!/usr/bin/env python3
"""Apply the controlled Compare -> Benchmark documentation revision.

This helper is intentionally temporary. The accompanying one-shot workflow runs it
on the documentation branch, validates the result, and removes both helper files
before committing the final documentation-only diff.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "doc_en.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "apply-doc-en-benchmark.yml"
SELF_PATH = Path(__file__).resolve()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def replace_section(text: str, start: str, end: str, replacement: str, label: str) -> str:
    start_index = text.find(start)
    if start_index < 0:
        raise RuntimeError(f"{label}: start marker not found")
    end_index = text.find(end, start_index + len(start))
    if end_index < 0:
        raise RuntimeError(f"{label}: end marker not found")
    return text[:start_index] + replacement.rstrip() + "\n\n" + text[end_index:]


text = DOC_PATH.read_text(encoding="utf-8")
original = text
anchor_pattern = re.compile(r'<a id=\\"([^\"]+)\\"')
anchors_before = anchor_pattern.findall(original)

# ---------------------------------------------------------------------------
# Preface: position the two named result types and describe their evidence.
# ---------------------------------------------------------------------------
text = replace_once(
    text,
    r'''WSPRadar evaluates one <strong class=\"defined-term\">Target</strong> under one explicit experiment design. The Target can be a complete installed station or one controlled hardware path. It can be evaluated on its own or against a meaningful <strong class=\"defined-term\">Reference</strong>. Depending on the question, the Reference can be a second controlled path at the same station, one known external station, the active local WSPR neighborhood or its strongest active member.''',
    r'''WSPRadar is a WSPR-based antenna and station performance analysis and benchmarking system. It turns archived WSPR reports into an auditable evidence path for two distinct questions: how one station behaves across independently confirmed opportunities, and how a Target behaves relative to a selected Reference under matched conditions.

WSPRadar evaluates one <strong class=\"defined-term\">Target</strong> under one explicit experiment design. The Target can be a complete installed station or one controlled hardware path. It can be evaluated on its own or against a meaningful <strong class=\"defined-term\">Reference</strong>. Depending on the question, the Reference can be a second controlled path at the same station, one known external station, the active local WSPR neighborhood or its strongest active member.''',
    "preface positioning",
)

text = replace_once(
    text,
    r'''The Reference is part of the scientific question, not merely a display option. A <strong class=\"defined-term\">Hardware A/B Test</strong> can narrow the comparison to two local antennas, feedlines, receivers or complete receive chains when the remaining variables are held stable. A <strong class=\"defined-term\">Reference Station / Buddy Test</strong> compares two complete stations, including their QTHs, equipment, terrain and noise environments. A Local Neighborhood Benchmark asks how the Target compares with a changing population of active nearby WSPR stations. <strong class=\"defined-term\">Performance</strong> evaluates the Target itself from independently confirmed opportunities. <strong class=\"defined-term\">Compare</strong> evaluates the Target relative to a Reference using matched evidence. In Performance, <strong class=\"defined-term\">qualifying evidence</strong> is the Target and independent-activity evidence retained after the run's eligibility rules.

Performance describes the observed conditional behavior of the complete Target station within independently confirmed WSPR opportunities. It is not an absolute measurement of receiver sensitivity, radiated power, antenna gain or antenna efficiency.''',
    r'''The Reference is part of the scientific question, not merely a display option. A <strong class=\"defined-term\">Hardware A/B Test</strong> can narrow the comparison to two local antennas, feedlines, receivers or complete receive chains when the remaining variables are held stable. A <strong class=\"defined-term\">Reference Station / Buddy Test</strong> compares two complete stations, including their QTHs, equipment, terrain and noise environments. A Local Neighborhood Benchmark asks how the Target compares with a changing population of active nearby WSPR stations. <strong class=\"defined-term\">Performance</strong> evaluates the Target itself across independently confirmed opportunities. <strong class=\"defined-term\">Benchmark</strong> evaluates the Target relative to a Reference using matched WSPR evidence. In Performance, <strong class=\"defined-term\">qualifying evidence</strong> is the Target and independent-activity evidence retained after the run's eligibility rules.

Performance describes the observed conditional behavior of the complete Target station within independently confirmed WSPR opportunities. Benchmark describes an observed Target-minus-Reference difference within the evidence that the selected design can validly match. The strongest benchmarks use controlled Hardware A/B arrangements or a stable, well-understood Reference. Taken together, WSPRadar can show practical footprint, Decode Rate, successful signal levels, relative signal strength, distance and direction structure, temporal recurrence and the breadth and depth of supporting evidence. It does not convert either result into an absolute measurement of receiver sensitivity, radiated power, antenna gain or antenna efficiency.''',
    "preface result definitions",
)

text = replace_once(
    text,
    r'''* <strong class=\"defined-term\">Performance</strong> evaluates the Target itself from independently confirmed opportunities. It reports Decode Rate, at-least-once reach, successful Target SNR and temporal behavior without introducing a Reference.
* <strong class=\"defined-term\">Compare</strong> evaluates the Target relative to a Reference using matched evidence. It reports paired **Delta SNR** and **Decode Outcomes**. Delta SNR is Target-side SNR minus Reference-side SNR after any configured Reference correction. Positive values favor the Target; negative values favor the Reference. Decode Outcomes retain both paired evidence and cases where only one side was decoded.

Performance and Compare answer different questions. WSPRadar keeps them separate so that a single attractive number cannot hide weak opportunity coverage, one-sided decodes or a paired subset that represents only part of the evidence.

Results open on a map and then follow the same concise evidence path for Performance and Compare: **Map → Segment Inspector → Station Insights → Drill-Down**.''',
    r'''* <strong class=\"defined-term\">Performance</strong> evaluates the Target itself from independently confirmed opportunities. It reports at-least-once reach, Station-balanced and Opportunity-level Decode Rate, successful Target SNR, distance and direction structure, chronological and UTC-hour behavior, and the stations and opportunities supporting those views without introducing a Reference.
* <strong class=\"defined-term\">Benchmark</strong> evaluates the Target relative to a Reference using matched evidence. It reports paired **Delta SNR**, **Decode Outcomes** and the share of evidence that was jointly pairable. Delta SNR is Target-side SNR minus Reference-side SNR after any configured Reference correction. Positive values favor the Target; negative values favor the Reference. Decode Outcomes retain both paired evidence and cases where only one side was decoded, while geography, time and selected-path views show where the relative result appears.

Performance and Benchmark answer different questions. WSPRadar keeps them separate so that a single attractive number cannot hide weak opportunity coverage, one-sided decodes, successful-decode censoring or a paired subset that represents only part of the evidence.

Results open on a map and then follow the same concise evidence path for Performance and Benchmark: **Map → Segment Inspector → Station Insights → Drill-Down**.''',
    "run output definitions",
)

text = replace_once(
    text,
    "The Performance Evidence, Comparison Evidence, Temporal Evidence and Selected Station Evidence sections remain available at their applicable points in that workflow.",
    "The applicable Performance or Benchmark evidence, Temporal Evidence and Selected Station Evidence sections remain available at their points in that workflow.",
    "demo evidence wording",
)

# ---------------------------------------------------------------------------
# Operator Guide: add a practical evidence framework before the playbooks.
# ---------------------------------------------------------------------------
text = replace_once(
    text,
    "A clear question and a stable physical setup make the result easier to interpret.\n\n**Define the experiment and run**",
    r'''A clear question and a stable physical setup make the result easier to interpret.

**Decide what evidence would answer the question**

WSPRadar does not reduce station behavior to one score. Before operating, decide which of these observations would support the intended conclusion:

* **Reach:** which qualifying stations or paths produced Target evidence at least once during the selected interval.
* **Conditional consistency:** how often Target evidence appeared among independently confirmed opportunities, shown as both Station-balanced and Opportunity-level Decode Rate.
* **Successful signal level:** normalized SNR for successful Target decodes or reports. Misses have no Target SNR, so this evidence must be read beside Decode Rate.
* **Relative signal strength:** paired Target-minus-Reference Delta SNR in Benchmark.
* **Evidence coverage:** how much Benchmark evidence was Joint and how much was one-sided, together with the stations, opportunities, spots or scheduled pairs supporting the summaries.
* **Structure:** where behavior changes with distance, azimuth, chronological time, UTC hour or selected solar state.

These observations answer different questions. Broad at-least-once reach can coexist with intermittent Decode Rate; a smaller footprint can be comparatively consistent; successful SNR can remain steady or rise while Decode Rate falls because weaker signals are no longer decoded. Define in advance which combination would count as confirmation and which views are exploratory.

**Define the experiment and run**''',
    "operator evidence framework",
)

# Replace the complete Performance playbook while preserving its anchor and place.
performance_start = r'''<a id=\"sec-2-2\"></a>

#### 1.2 Performance only: evaluate the Target'''
performance_end = r'''<a id=\"sec-2-3\"></a>'''
performance_section = r'''<a id=\"sec-2-2\"></a>

#### 1.2 Performance only: evaluate the Target

**Question answered**

What practical footprint, conditional consistency, successful-signal level and temporal or geographic behavior did the Target show among remote stations or signals independently shown to be active?

**What WSPRadar shows**

For this playbook, <strong class=\"defined-term\">qualifying evidence</strong> is the Target and independent activity evidence retained after the run's identity, band, time, Target-activity, filter and threshold rules.

* **RX Performance** tests whether the Target receiver also decoded remote transmitter-cycles that another eligible receiver independently confirmed.
* **TX Performance** tests whether independently active remote receiver-cycles also decoded the Target transmitter when those receivers were shown to contain other same-band activity.

Performance does not merely count spots or report a single decode outcome. It separates several complementary parts of practical station behavior:

* **At-least-once reach** shows how much of the qualifying station footprint produced Target evidence at least once during the selected interval. It is a breadth measure and normally grows with a longer run.
* **Decode Rate** shows how consistently the Target succeeded within confirmed opportunities. The Station-balanced view gives each qualifying station one vote; the Opportunity-level view gives each confirmed opportunity one vote. Their difference shows whether high-volume stations behave differently from the wider station population.
* **Successful Target SNR** shows the normalized signal levels of evidence that the Target actually decoded or that remote receivers successfully reported. It is conditional on success: missed opportunities have no Target SNR and receive no synthetic value.
* **Distance and direction views** show whether reach, Decode Rate or successful SNR changes across the observed paths. They describe the installed station's WSPR behavior; they do not directly measure an absolute radiation pattern, take-off angle, gain or sensitivity.
* **Chronological and UTC-hour views** show whether behavior changed during the run or recurred at particular hours. Successful-SNR deviation shows when decoded signals were stronger or weaker than each path's own usual successful level, while the evidence stacks show station support, opportunity depth and Decode Rate through the same periods.
* **Station and row-level evidence** shows which callsign-plus-locator identities support the pattern and lets one selected path be inspected down to the retained opportunities.

Read these layers together. High reach with a lower Decode Rate means many paths opened at least once but were intermittent. Lower reach with a high Decode Rate means fewer paths opened, but those paths were comparatively consistent. A stable or rising successful-SNR median alongside a falling Decode Rate can mean that weaker signals disappeared below the decoder threshold, leaving only stronger successful survivors. A recurring distance, azimuth or UTC-hour pattern can be operationally useful, but it remains a pattern in the observed WSPR paths rather than proof of one propagation mode or antenna property.

Propagation is not merely unwanted variation in this playbook. Changing paths and conditions expose the real operating envelope of the complete station. Repetition across many stations, cycles, directions and propagation states can show where behavior is broad and persistent. It does not by itself identify why the station behaved that way.

**Set up the analysis**

Choose `RX Analysis` or `TX Analysis`, enter the exact Target callsign and QTH, choose one band and an active UTC window, then select `Performance — no Reference`.

**Useful applications**

Performance is well suited to station commissioning and baselining; mapping where and when a station is dependably heard; identifying directional, distance-dependent or daily operating patterns; monitoring station stability; and locating the time window in which behavior changed. A sudden or recurring change can motivate checks for local noise, interference, overload, gain or decoder changes, feedline and switching faults, intermittent hardware or environmental conditions. The view can identify the scope and timing of the observation, but it cannot assign the cause without an appropriate controlled change, crossover, independent measurement or repetition.

Separate before-and-after Performance runs can document that observed station behavior changed between two windows. Because propagation and the active station population can also change, use a controlled Benchmark, rapid alternation, crossover or repeated like-for-like windows when the intended conclusion is specifically about a hardware change.

**Strengthen the evidence**

Use an operating window with observable Target activity and enough independent WSPR activity. Inspect reach, both Decode Rate weightings, successful SNR, distance and azimuth structure, chronological and UTC-hour recurrence, station breadth and opportunity depth together. Select representative and surprising stations for path-level inspection and Drill-Down. If only a few peers survive, extend the observation window or narrow the geographic or temporal scope of the conclusion. For a confirmatory run, define the primary scope and evidence pattern in advance, keep the configuration fixed and repeat it in another suitable window. Change filters or thresholds only for a stated experimental reason and preserve the changed configuration as a separate run.

**Evidence-matched conclusion**

> For this Target, band, UTC window and selected peer population, the displayed Performance evidence describes the Target's at-least-once reach, Decode Rate within independently confirmed opportunities, successful-decode SNR and the geographic and temporal scope in which those observations appeared. State the weighting used, the qualifying station and opportunity support, and whether the pattern was broad, intermittent, directional, distance-dependent or recurring.

In everyday station terms: among the worldwide WSPR activity that this run could independently verify and fairly test, the result shows where your station participated, how consistently it did so, what signal levels successful evidence had, when the behavior occurred and how much evidence supports that picture. It describes the complete station under the selected real-world conditions rather than an isolated laboratory property.'''
text = replace_section(
    text,
    performance_start,
    performance_end,
    performance_section,
    "Performance playbook",
)

# Enrich the remaining playbooks without changing their structure.
text = replace_once(
    text,
    r'''Unless receiver, audio and decoder differences have been characterized, the result compares the complete receive paths rather than the antennas alone.

**Set up the experiment**''',
    r'''Unless receiver, audio and decoder differences have been characterized, the result compares the complete receive paths rather than the antennas alone.

Read paired Delta SNR together with Decode Outcomes, station breadth, geographic scope, temporal recurrence and selected-path evidence. A broad and recurring shift across many remote transmitters supports a stable complete-path difference more strongly than a shift confined to one direction, hour or transmitter. WSPRadar can show where and when the difference appears; attribution to an antenna, feedline, filter, receiver, decoder or noise environment is justified only to the extent that the rest of the two paths was controlled.

**Set up the experiment**''',
    "RX A/B evidence interpretation",
)

text = replace_once(
    text,
    r'''For either method, operate both paths at the same physical test QTH and report locators within the configured Target grid-4. Hardware A/B derives both displayed grid-4 values from Target QTH rather than accepting an independent Reference location. Report actual transmitter power and document everything that is not common. The Hardware A/B run produces Compare only; use a separate `Performance — no Reference` configuration when the non-comparative Target question is also relevant.''',
    r'''For either method, operate both paths at the same physical test QTH and report locators within the configured Target grid-4. Hardware A/B derives both displayed grid-4 values from Target QTH rather than accepting an independent Reference location. Report actual transmitter power and document everything that is not common. The Hardware A/B run produces Compare only; use a separate `Performance — no Reference` configuration when the non-comparative Target question is also relevant.

In both methods, read Delta SNR, Decode Outcomes, station breadth and geographic and temporal patterns together. A consistent shift across many receiving stations is different evidence from an advantage limited to one azimuth, distance range or UTC period. The latter can still reveal useful directional or path-dependent installed-station behavior, but it is not one context-free antenna number.''',
    "TX A/B common interpretation",
)

text = replace_once(
    text,
    r'''The Target-Active Gate remains Target-centric: a cycle is eligible only when the Target was decoded somewhere. Within an eligible cycle, a receiver may still contribute one-sided Reference evidence. A cycle in which Reference was decoded but Target was decoded nowhere is excluded rather than counted as a Target loss. [Section 7.3](#sec-7-3) defines this boundary.

**Set up the experiment**''',
    r'''The Target-Active Gate remains Target-centric: a cycle is eligible only when the Target was decoded somewhere. Within an eligible cycle, a receiver may still contribute one-sided Reference evidence. A cycle in which Reference was decoded but Target was decoded nowhere is excluded rather than counted as a Target loss. [Section 7.3](#sec-7-3) defines this boundary.

Together, the paired and one-sided views can show relative signal strength, practical reach near the decoder threshold and whether an advantage is broad or concentrated. A difference tied mainly to one receiving station, audio-frequency assignment or short interval can indicate path-specific propagation, QRM or chain response rather than a general antenna difference. Frequency swaps, chain crossovers and repeated runs provide useful controls.

**Set up the experiment**''',
    "simultaneous TX interpretation",
)

text = replace_once(
    text,
    r'''Sequential TX Hardware A/B assigns complete WSPR transmissions to Target and Reference from a time-locked schedule. WSPRadar then forms deterministic one-to-one scheduled pairs for each remote receiver identity and reports scheduled-pair Delta SNR plus one-sided Decode Outcomes.

**Set up the experiment**''',
    r'''Sequential TX Hardware A/B assigns complete WSPR transmissions to Target and Reference from a time-locked schedule. WSPRadar then forms deterministic one-to-one scheduled pairs for each remote receiver identity and reports scheduled-pair Delta SNR plus one-sided Decode Outcomes.

Inspect the median Pair Delta together with incomplete or one-sided scheduled pairs, station breadth, distance and direction structure and the chronological pattern. A difference that recurs across many receivers and survives reversed schedule assignments is more persuasive than one locked to a particular phase, switch state or short propagation interval. The views can expose those dependencies, but the two transmissions remain sequential.

**Set up the experiment**''',
    "sequential TX interpretation",
)

text = replace_once(
    text,
    r'''Same-cycle TX pairs therefore share one remote receiver, while RX pairs share one remote transmitter. This controls one endpoint of the comparison; it does not remove differences in QTH, radio path, station hardware, terrain or local noise.

**Set up the analysis**''',
    r'''Same-cycle TX pairs therefore share one remote receiver, while RX pairs share one remote transmitter. This controls one endpoint of the comparison; it does not remove differences in QTH, radio path, station hardware, terrain or local noise.

The result can show where one complete station was relatively stronger, where one-sided reach differed, how the relationship changed with distance, direction or UTC time and how broadly joint evidence supported the paired result. This makes a known buddy useful as a whole-station baseline or diagnostic partner. It does not isolate which station component caused the observed difference.

**Set up the analysis**''',
    "buddy interpretation",
)

text = replace_once(
    text,
    r'''The Reference can change from cycle to cycle. It is a local activity benchmark rather than one fixed or calibrated station.

**Set up the analysis**''',
    r'''The Reference can change from cycle to cycle. It is a local activity benchmark rather than one fixed or calibrated station.

This view can show whether the Target tends to sit above, near or below the active local baseline for particular paths and times, and whether that relationship is broad or concentrated. Read the contributor identities and Joint Evidence Share with the result: a change can reflect the Target, a changed neighborhood membership or both. It is a contextual benchmark, not a permanent station ranking.

**Set up the analysis**''',
    "local median interpretation",
)

text = replace_once(
    text,
    r'''Local Best Station forms a changing best-peer envelope from active station identities inside the selected radius. It is intentionally stricter than the neighborhood median and does not represent a local average.

**Set up the analysis**''',
    r'''Local Best Station forms a changing best-peer envelope from active station identities inside the selected radius. It is intentionally stricter than the neighborhood median and does not represent a local average.

This view shows the Target's gap to the strongest qualifying nearby evidence available on each path and cycle, including where and when that gap changes. Because the winning local identity can change continuously, inspect the contributors and support before treating a pooled value as stable. It is a demanding moving reference envelope, not a league table or comparison with one permanent competitor.

**Set up the analysis**''',
    "local best interpretation",
)

# Add a clear observation-versus-explanation boundary to the reporting guidance.
text = replace_once(
    text,
    r'''WSPRadar deliberately does not collapse these dimensions into one proof grade. The visible counts, distributions and underlying rows let the operator judge the result in the context of the actual experiment.''',
    r'''WSPRadar deliberately does not collapse these dimensions into one proof grade. The visible counts, distributions and underlying rows let the operator judge the result in the context of the actual experiment.

The observed time, distance, direction, Decode Rate, successful-SNR or Delta-SNR pattern is the evidence. An explanation such as antenna directivity, a local-noise change, propagation mode, overload or an intermittent component is an interpretation. Match the wording to the observation first, then test the explanation through a controlled change, crossover, independent measurement or repetition.''',
    "evidence versus explanation",
)

text = replace_once(
    text,
    r'''> For this Target, band, UTC window and selected peer population, the displayed Decode Rate describes the fraction of independently confirmed opportunities in which the Target also produced qualifying evidence. State whether the reported value is the Station-balanced Decode Rate or the Opportunity-level Decode Rate. Qualifying stations, confirmed opportunities, geographic scope and temporal views describe the breadth, depth and recurrence supporting that result.

**Compare wording**''',
    r'''> For this Target, band, UTC window and selected peer population, the displayed Decode Rate describes the fraction of independently confirmed opportunities in which the Target also produced qualifying evidence. State whether the reported value is the Station-balanced Decode Rate or the Opportunity-level Decode Rate. Qualifying stations, confirmed opportunities, geographic scope and temporal views describe the breadth, depth and recurrence supporting that result.

A complete Performance statement can additionally say whether at-least-once reach was broad or limited, whether participation was consistent or intermittent, where distance or directional patterns appeared, whether a UTC-hour pattern recurred and how successful Target SNR behaved. Describe these as observed WSPR behavior of the complete station under the selected conditions, not as isolated gain, sensitivity or efficiency.

**Compare wording**''',
    "expanded Performance reporting",
)

# ---------------------------------------------------------------------------
# Intelligent formal terminology migration. Capitalized Compare denotes the
# named result type throughout this document; lowercase compare/comparison is
# retained as ordinary English and compatibility identifiers remain unchanged.
# ---------------------------------------------------------------------------
text = re.sub(r"\bCompare\b", "Benchmark", text)

# Restore external names/titles and genuine ordinary-English uses.
for changed, restored in {
    "WSPR-Station-Benchmark": "WSPR-Station-Compare",
    "*Failure to Use WSPR to Benchmark Antennas*": "*Failure to Use WSPR to Compare Antennas*",
    "*Using the Weak Signal Propagation Reporter Network to Benchmark Antenna Performance*": "*Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*",
    'Benchmark like-for-like TX and RX runs when investigating station balance or an \"alligator\" pattern.': 'Compare like-for-like TX and RX runs when investigating station balance or an \"alligator\" pattern.',
    "6. Benchmark Target with that cycle-level Reference.": "6. Compare Target with that cycle-level Reference.",
}.items():
    text = text.replace(changed, restored)

# Natural wording and compatibility notes after the systematic rename.
for old, new in {
    "The applicable Performance or Benchmark evidence, Temporal Evidence": "The applicable Performance or Benchmark Evidence, Temporal Evidence",
    "Performance and Benchmark are mutually exclusive result types. No benchmark produces Performance only; every benchmark choice produces Benchmark only and does not render, inspect or export a separate Performance result.": "Performance and Benchmark are mutually exclusive result types. Selecting any Reference-based design produces Benchmark only; it does not render, inspect or export a separate Performance result.",
    "Every comparison configuration records": "Every Benchmark configuration records",
    "an applicable comparison file without": "an applicable Benchmark configuration file without",
    "Inactive comparison branches": "Inactive Benchmark branches",
    "dormant comparison parameters": "dormant Benchmark parameters",
    "**Comparison Parameters:**": "**Benchmark Parameters:**",
    "Target identity, comparison design and selected geographic": "Target identity, Benchmark Design and selected geographic",
    "A Benchmark configuration may retain both the canonical `results_view.compare` block and the canonical `results_view.success` block": "A Benchmark configuration may retain both the canonical compatibility block `results_view.compare` and the canonical `results_view.success` block",
    "or Benchmark when a benchmark is selected": "or Benchmark when a Reference-based benchmark design is selected",
    "Buddy Benchmark": "Reference Station / Buddy Test",
    "Local Benchmark |": "Local Neighborhood Benchmark |",
    "Benchmark keeps two complementary views of performance.": "Benchmark keeps two complementary evidence views.",
    "The Segment Benchmark Delta SNR histograms": "The Benchmark Delta SNR histograms in Segment Inspector",
    "The retained Segment Benchmark histograms": "The retained Benchmark histograms in Segment Inspector",
    "compare/                         # when a benchmark result exists": "compare/                         # compatibility folder for a Benchmark result",
}.items():
    text = text.replace(old, new)

controls_choices = r'''- `Performance — no Reference`
- `Benchmark — Hardware A/B`
- `Benchmark — Known Reference Station`
- `Benchmark — local neighborhood benchmark`

The choices are mutually exclusive result types. Performance and Benchmark are mutually exclusive result types. Selecting any Reference-based design produces Benchmark only; it does not render, inspect or export a separate Performance result.'''
controls_replacement = r'''- `Performance — no Reference`
- `Benchmark — Hardware A/B`
- `Benchmark — Known Reference Station`
- `Benchmark — local neighborhood benchmark`

Performance and Benchmark are mutually exclusive result types. Selecting any Reference-based design produces Benchmark only; it does not render, inspect or export a separate Performance result.

The visible result type is **Benchmark**. Existing versioned configuration and export identifiers containing lower-case `compare`, including `results_view.compare` and the `compare/` package folder, remain compatibility names. They do not represent a separate user-facing mode.'''
text = replace_once(text, controls_choices, controls_replacement, "controls compatibility note")

# Refine the formal reporting template after the rename.
text = replace_once(
    text,
    r'''**Benchmark wording**

> For this Target, Reference, band, UTC window and selected segment, station-balanced Delta SNR favored the Target/Reference by the displayed amount. The observation-level Delta SNR, joint station and spot/pair counts and Decode Outcomes describe the supporting paired and one-sided evidence.''',
    r'''**Benchmark wording**

> For this Target, Reference, band, UTC window and selected segment, station-balanced Delta SNR favored the Target/Reference by the displayed amount. The observation-level Delta SNR, joint station and spot/pair counts, Joint Evidence Share and Decode Outcomes describe the supporting paired and one-sided evidence.

For a controlled Hardware A/B result, name the complete paths compared and any crossover or calibration. For a Reference Station / Buddy Test, state that complete installed stations and their environments were benchmarked. For a Local Neighborhood Benchmark, state the radius, method and changing Reference definition.''',
    "Benchmark reporting template",
)

# ---------------------------------------------------------------------------
# Validation: preserve structure and compatibility while enforcing the visible
# terminology migration.
# ---------------------------------------------------------------------------
anchors_after = anchor_pattern.findall(text)
if anchors_after != anchors_before:
    raise RuntimeError("documentation anchors changed; structure must remain intact")

compile(text, str(DOC_PATH), "exec")

for token in (
    "results_view.compare",
    "compare/",
    "compare_evidence_figures",
    "compare_evidence_recipes",
):
    if token not in original or token not in text:
        raise RuntimeError(f"compatibility identifier was lost: {token}")

for forbidden in (
    "`Compare —",
    "Read a Compare result",
    "(Compare Mode)",
    "Worked Compare example",
    "Comparison Evidence",
):
    if forbidden in text:
        raise RuntimeError(f"formal Compare terminology remains: {forbidden}")

allowed_compare_fragments = (
    "WSPR-Station-Compare",
    "Failure to Use WSPR to Compare Antennas",
    "Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance",
    "Compare like-for-like TX and RX runs",
    "6. Compare Target with that cycle-level Reference.",
)
remaining_compare_lines = [
    line for line in text.splitlines() if re.search(r"\bCompare\b", line)
]
unexpected_compare_lines = [
    line
    for line in remaining_compare_lines
    if not any(fragment in line for fragment in allowed_compare_fragments)
]
if unexpected_compare_lines:
    raise RuntimeError(
        "unexpected capitalized Compare remains:\n" + "\n".join(unexpected_compare_lines)
    )

required_phrases = (
    "performance analysis and benchmarking system",
    "Performance and Benchmark answer different questions",
    "Benchmark — Hardware A/B",
    "#### 2.2 Read a Benchmark result",
    "#### 2.5b Inspect a Geographic Segment (Benchmark Mode)",
    "#### 2.8 Worked Benchmark example",
    "**Decide what evidence would answer the question**",
    "**Useful applications**",
    "The observed time, distance, direction, Decode Rate, successful-SNR or Delta-SNR pattern is the evidence.",
)
for phrase in required_phrases:
    if phrase not in text:
        raise RuntimeError(f"required revision is missing: {phrase}")

DOC_PATH.write_text(text, encoding="utf-8", newline="\n")

# Remove the temporary automation so the resulting PR diff contains only the
# requested documentation file.
if WORKFLOW_PATH.exists():
    WORKFLOW_PATH.unlink()
if SELF_PATH.exists():
    SELF_PATH.unlink()

print(
    "Revised docs/doc_en.py: "
    f"{original.count('Compare')} capitalized Compare occurrences reviewed; "
    f"{len(remaining_compare_lines)} intentional ordinary/external uses retained."
)
