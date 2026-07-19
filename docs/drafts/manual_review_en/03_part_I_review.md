# Part I Review — Operator Guide

## Overall decision

Retain the three-stage operator journey:

1. choose and operate the experiment;
2. read the evidence from map to rows;
3. strengthen, report and preserve the result.

No worked Success example is added in this review.

## Part I introduction

Add a compact terminology distinction:

- the **experiment** is the physical on-air operation and station configuration;
- a **run** or **analysis** is WSPRadar's configured processing of those observations;
- a **result** is the Success or Compare evidence produced by that run.

This avoids alternating between those words as though they were interchangeable.

## Chapter 1 — Experiment Playbooks

### 1.1 A strong foundation for every experiment

Retain the existing setup checklist and add:

- state whether the run is exploratory or intended to confirm an earlier pattern;
- for a confirmatory run, define the primary geographic/time scope and core configuration before inspecting the result;
- distinguish the physical experiment from the software run.

Reason: repeated analysis is more defensible when the second run does not simply adopt whichever scope looked strongest in the first.

### 1.2 Success only

Accepted changes:

- Move the dense authoritative definition of qualifying evidence to its existing homes in Sections 2.1 and 7.4; retain one short operator definition here.
- Separate conditional Success Rate from successful-decode SNR in the question answered.
- Replace `broaden the evidence` with an instruction to extend the window or narrow the claim. Filters and thresholds should change only for a stated experimental reason.

Revised question:

> Where, when and how consistently does the Target produce qualifying evidence among remote stations or signals independently shown to be active, and what SNR is observed for successful Target decodes?

### 1.3 RX Hardware A/B

Accepted changes:

- Clarify that two antennas normally require one independently reporting receiver/decoder chain per antenna.
- State explicitly that uncharacterized receiver/decoder differences make the result a comparison of complete receive paths, not isolated antennas.
- Replace `Keep shared hardware genuinely common` with a more testable instruction: components intended to be common must be physically common; unavoidable chain differences must be measured or documented.

### 1.4 TX Hardware A/B

This section is the principal restructuring target.

Retain in Chapter 1:

- why deterministic alternation is used;
- one callsign and preferably one common transmitter chain;
- use the actual physical recurrence and UTC phase;
- deterministic scheduling is required;
- false power reports must not encode path identity;
- verify schedule-to-path mapping without RF;
- sequential timing remains a limitation;
- use the shortest practical separation;
- reverse assignments in a repeated test when a small result matters;
- one design-specific conclusion example.

Relocate:

- exact interval choices, defaults and preview behavior to 4.3;
- nearest-pair, tie, micro-median and edge-window rules to 7.1/7.7;
- Ultimate3S and QMX recipes to a broadened Appendix B;
- formula mechanics to 7.5;
- full repetition guidance to 3.2;
- full station-note requirements to 3.4.

Replace the over-broad averaging sentence with:

> Across a balanced run, random short-term variation may average down because both paths are repeatedly exposed to changing conditions. Systematic schedule-, switching- or time-of-cycle effects do not necessarily average down and should be tested through reversed assignments and repeated runs.

### 1.5 Reference Station / Buddy Test

Replace the abstract `shared endpoint` description with the physical endpoint:

- TX pairs share one remote receiver;
- RX pairs share one remote transmitter;
- the paired endpoint controls one part of the comparison but does not remove QTH, path, hardware or local-noise differences.

### 1.6 and 1.7 Local Neighborhood methods

Retain both playbooks and add a selection safeguard:

- choose the primary radius from local geography and station density before interpreting the result;
- alternative radii are a documented sensitivity analysis;
- do not retain only the radius producing the most favorable result.

## Chapter 2 — Read Your Results

### Evidence ladder

Change `locate the effect` to `locate the observed pattern` throughout the operator layer.

### 2.2 Compare

Accepted changes:

- Use `same-cycle TX Compare` in the operator explanation to avoid confusion with sequential TX Hardware A/B.
- Describe Decode Outcomes as joint and one-sided decode evidence, not generically as `comparative reach`.
- Add the existing scientific boundary in short operator form: one-sided TX outcomes are not power-normalized because the missing side has no SNR to reconstruct.

### 2.4 Stations and Spots

Add:

> A `callsign + locator` is an analysis identity, not proof of one unique physical station. Suffixes, stale locators and locator changes can split or move a physical station in the evidence.

### 2.5/2.6 numbering

The cleaner long-term hierarchy is 2.5.1/2.5.2 and 2.6.1/2.6.2. This review retains the published `2.5a/b` and `2.6a/b` anchors to avoid unnecessary link churn. The empty legacy `sec-3-1` anchor may remain as a compatibility alias.

## Chapter 3 — Strengthen and Communicate

### 3.1 Stability versus repeatability

Add an explicit distinction:

> Sample Stability and experimental repeatability are different. The 90% Stability interval describes sensitivity of the displayed median to resampling the evidence already present in this run. Repeating the experiment in another suitable window tests whether the observed pattern persists under new operating and propagation conditions.

### 3.2 Exploratory and confirmatory use

Add a two-stage workflow:

- use an initial run to discover a possible pattern;
- before a confirmatory repetition, freeze direction, band, benchmark, filters, thresholds, schedule and primary evaluation scope;
- treat alternative radii or scopes as reported sensitivity analyses rather than selecting only a favorable view.

### 3.3 Reporting

Retain the comprehensive checklist. Add a short distinction between a minimum operator statement and a full technical report, without removing the current wording examples.

### 3.4 Preservation

Add the physical schedule-to-path mapping and any reversed assignment to the station-note list.
