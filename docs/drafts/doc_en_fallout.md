# English Manual Fallout Register

## Purpose

This file records original production-manual wording that is not retained verbatim in `doc_en_candidate.py`. It distinguishes:

- **not retained as a claim:** wording deliberately removed because it was too broad or causally suggestive;
- **reworded or condensed:** the operator-useful substance remains in the candidate, but the original sentence does not;
- **relocated:** the useful content remains in another authoritative chapter or appendix and is tracked in `manual_review_en/01_relocation_ledger.md`.

No unique, correct and operator-useful guidance was intentionally discarded without either a destination or an entry below.

## Part 0 — Preface

### Section 0.3

> The map locates the effect; it is the start of the analysis, not the conclusion.

**Disposition:** Reworded.

**Candidate treatment:** `effect` becomes `observed pattern` because a map localizes observational evidence but does not establish a causal effect.

## Part I — Operator Guide

### Section 1.1

> A clear question and a stable operating setup make the result easier to interpret.

**Disposition:** Reworded and expanded.

**Candidate treatment:** Distinguishes the physical experiment, the WSPRadar run and the result, then adds exploratory versus confirmatory use.

> Once the run completes, use the evidence ladder in Chapter 2 to inspect its geographic breadth, observation volume and underlying rows.

**Disposition:** Reworded and expanded.

**Candidate treatment:** The first run may be exploratory; before confirmation, the primary scope and core configuration are fixed.

### Section 1.2

> Qualifying evidence means the decoded WSPR observations retained after the run's identity, locator, band, UTC-window, Target-activity and filter rules, for peers and segments that also satisfy the configured evidence thresholds. For Success, this includes Target decodes and the independent same-cycle activity used to establish opportunities that are fair to count.

**Disposition:** Condensed in the playbook; full substance retained in Sections 2.1 and 7.4.

**Reason:** The dense definition preceded the practical question and duplicated the authoritative classification and denominator.

> Where, when and at what signal strength does the Target produce qualifying evidence among remote stations or signals independently shown to be active?

**Disposition:** Reworded.

**Candidate treatment:** Separates conditional Success Rate from successful-decode SNR rather than implying they are one signal-strength metric.

> Use an operating window with observable Target activity and enough independent WSPR activity. Check the geographic scope, Stations, Spots and time views. If only a few peers survive the selected filters or evidence thresholds, extend the run or broaden the evidence before drawing a wide conclusion.

**Disposition:** Reworded.

**Reason:** `Broaden the evidence` could be read as relaxing filters or thresholds after inspecting the result. The candidate recommends extending the window or narrowing the claim and requires a stated reason for configuration changes.

### Section 1.3

> For a ham operator, this can mean comparing two antennas with one receiver and decoder path per antenna; comparing two receivers fed from the same antenna through a characterized splitter; comparing preamplifiers, filters or feedlines; or comparing two complete parallel receive chains. Keep everything outside the item under test as similar and stable as practical.

**Disposition:** Reworded.

**Reason:** `One receiver and decoder path per antenna` was grammatically ambiguous. The candidate states that each antenna normally feeds its own independently reporting receiver/decoder chain and explicitly bounds the result to complete receive paths unless chain differences are characterized.

> Keep shared hardware genuinely common.

**Disposition:** Reworded.

**Candidate treatment:** Components intended to be common must be physically common; unavoidable chain differences must be measured or documented.

### Section 1.4

The exact schedule ranges, defaults, preview behavior, pair-construction mechanics, Ultimate3S procedure and QMX procedures are **relocated**, not discarded. See relocation entries R-001 through R-006.

> This design keeps one callsign and normally one transmitter chain. Target and Reference can be two minutes apart, but lower-duty-cycle schedules with a greater separation are also valid. Shorter separation limits the time available for propagation, interference and receiver conditions to change; it does not make a sequential comparison simultaneous.

**Disposition:** Condensed and reorganized.

**Candidate treatment:** The rationale now precedes setup instructions and distinguishes shorter separation from simultaneity.

> The time-locked schedule, rather than callsign `/1` and `/2` suffixes, identifies the two paths.

**Disposition:** Reworded.

**Candidate treatment:** Path identity comes from the deterministic UTC schedule, not suffixes or different reported powers.

> Do not encode path identity by reporting false values such as `30 dBm` for one path and `33 dBm` for the other. WSPRadar normalizes TX SNR as `SNR - reported power + 30`; an invented 3 dB report difference therefore creates an artificial 3 dB comparison offset. Time-locking identifies the paths. Report the actual power and use a measured Reference correction for a real, defensible path offset.

**Disposition:** Condensed at the point of action; exact formula retained in Section 7.5.

**Reason:** The full formula should have one scientific home, while the pre-run warning must remain prominent.

> Alternating complete scheduled transmissions retains one common transmitter chain and gives both paths repeated exposure to changing propagation and receiver conditions. Over a balanced run lasting many hours or days, short-term changes repeatedly affect both sides and tend to average down.

**Disposition:** First sentence condensed; second sentence not retained as written.

**Reason:** The original averaging statement did not distinguish random variation from systematic schedule-, switching- or time-of-cycle effects.

**Candidate replacement:**

> Across a balanced run, random short-term variation may average down because both paths are repeatedly exposed to changing conditions. Systematic schedule-, switching- or time-of-cycle effects do not necessarily average down.

> In everyday station terms: after repeatedly alternating the two RF paths, the result shows whether path A or B tended to produce stronger reports for the receivers and propagation periods represented in the run. Why alternating transmissions are useful and Section 6.3 explain why this comparison is defensible while still remaining sequential rather than simultaneous.

**Disposition:** Tightened.

**Candidate treatment:** Retains the design boundary without repeating the internal section link in the conclusion.

### Section 1.5

> Same-cycle pairing gives the two sides a shared endpoint and reduces many path, transmitter or receiver differences within each pair.

**Disposition:** Reworded.

**Reason:** `Shared endpoint` was abstract and could suggest more control than the Buddy design provides.

**Candidate treatment:** TX pairs share one remote receiver; RX pairs share one remote transmitter. QTH, path, hardware, terrain and local-noise differences remain.

### Section 1.6

> Inspect which local identities contribute, their evidence counts and how the result changes with radius. A smaller radius can describe a more similar local environment but may leave a fragile pool; a larger radius can provide more contributors while including different terrain, noise and station conditions.

**Disposition:** Reworded and expanded.

**Candidate treatment:** The primary radius is selected before interpretation; alternative radii are documented sensitivity analyses rather than a search for the most favorable result.

### Section 1.7

> Inspect the local Reference contributors and repeat the analysis with scientifically defensible radii when the conclusion depends strongly on pool membership. Report the changing best-peer definition rather than describing the result as a comparison with one fixed station.

**Disposition:** Reworded and expanded.

**Candidate treatment:** Preserves the contributor and changing-envelope guidance while adding the same primary-radius and sensitivity-analysis safeguard as Section 1.6.

## Chapter 2 — Read Your Results

### Chapter introduction and Section 2.3

> Use the map to locate the effect.

> 2.3 Use the map to locate the effect

> Map color points to the effect. The following evidence levels show how broad and well-supported it is.

**Disposition:** Reworded.

**Candidate treatment:** Uses `observed pattern` rather than causal `effect`.

### Section 2.2

> In simultaneous TX Compare, the same remote receiver measures Target and Reference. This reduces receiver-hardware, antenna, local-noise and reporting differences within the pair.

**Disposition:** Reworded.

**Candidate treatment:** Uses `same-cycle TX Compare` to avoid confusion with sequential TX Hardware A/B.

> Use Delta SNR to describe the paired strength difference and Decode Outcomes to describe comparative reach.

**Disposition:** Reworded.

**Reason:** Decode Outcomes are joint and one-sided observational categories, not a reconstructed or universally power-normalized reach metric.

### Section 2.5b

> A wide or split distribution shows that the effect varies by path.

**Disposition:** Reworded.

**Candidate treatment:** `Observed difference` replaces `effect`.

### Section 2.7

> Simultaneous Compare exposes same-cycle Target/Reference evidence and Delta SNR.

**Disposition:** Reworded.

**Candidate treatment:** `Same-cycle Compare` avoids confusion with the sequential Hardware A/B branch.

## Chapter 3 — Strengthen and Communicate

### Section 3.1

> Evidence is more stable when the station-balanced view, observation-level view, time views and repeated runs tell a compatible story.

**Disposition:** Not retained as written.

**Reason:** It merged internal sample consistency, the formal Stability interval and real-world repeatability into one use of `stable`.

**Candidate treatment:** Separates breadth, internal consistency, descriptive 90% Stability and experimental repeatability.

### Section 3.3

> A useful conclusion states:

**Disposition:** Replaced by a two-level reporting structure.

**Candidate treatment:** Distinguishes a minimum operator statement from a full technical report. The substantive checklist items remain.

## Part II — Controls and Troubleshooting

### Section 5.2

The full `System Audit Status` provider/cache paragraph is not discarded. It is moved to Section 5.6 and split into shorter paragraphs under `Read System Audit Status`.

## Part III — Scientific Foundations, Methods and Claims

### Chapter 8 introduction

> WSPRadar supports precise statements about conditional reach, paired differences, one-sided evidence and where those effects were observed.

**Disposition:** Reworded.

**Candidate treatment:** `Observed patterns` replaces generic causal `effects`.

### Section 8.3

> For a serious result, report:

**Disposition:** Grammatical correction.

**Candidate treatment:** `For a serious result, preserve and report:` matches the first checklist item and the reproducibility purpose.

## Part IV — Practical Supplements

### Appendix B

No useful scheduling, QMX, Ultimate3S, relay installation or safety guidance is discarded. The material is consolidated into Appendix B subsections B.1-B.5. Duplicate QMX explanation is merged into one device-specific example.

## Net result

The only substantive claim removed rather than preserved is the unqualified implication that short-term changes necessarily tend to average down in a balanced sequential TX run. It is replaced by a bounded distinction between random variation and systematic timing or switching effects. All other entries are wording corrections, clarification, condensation or relocation.
