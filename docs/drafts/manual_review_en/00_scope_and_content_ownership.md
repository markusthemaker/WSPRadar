# English Manual Review: Scope and Content Ownership

## Baseline

- Repository: `markusthemaker/WSPRadar`
- Review branch: `agent/stronger-english-preface`
- Baseline: current `main` after the production Part 0 introduction was integrated.
- Authoritative source under review: `docs/doc_en.py`.
- Output remains under `docs/drafts` until explicitly integrated.

## Review objective

Produce one complete English candidate that preserves all unique, correct and operator-useful guidance while improving information placement, progression, precision and cross-referencing. The review must not silently remove useful content.

## Content ownership by manual layer

### Part 0 — Preface

Owns motivation, the minimum WSPR background, experiment-question selection and the result blocks produced by one run.

### Part I, Chapter 1 — Experiment Playbooks

Owns which experiment answers a practical question, the minimum valid operating setup, critical point-of-action warnings and the design's principal interpretation boundary. It should not reproduce complete control ranges, exact algorithms or device-specific procedures.

### Part I, Chapter 2 — Read Your Results

Owns interpretation of completed evidence: result identity, map, Stations and Spots, Segment Inspector, Station Insights and Drill-Down. It may summarize scientific mechanics only where necessary to prevent a materially wrong reading.

### Part I, Chapter 3 — Strengthen and Communicate

Owns repetition, reversal and control experiments, exploratory versus confirmatory use, evidence-matched wording and preservation of station context.

### Part II — Controls and Troubleshooting

Owns exact UI labels, defaults, ranges, applicability, configuration behavior, view-versus-scientific control distinctions, diagnosis and upstream-data behavior.

### Part III, Chapter 6 — Literature, Prior Art and Positioning

Owns scientific lineage, prior art, source-specific boundaries and bounded WSPRadar positioning.

### Part III, Chapter 7 — Scientific Methods

Owns exact eligibility, matching, identity, pairing, formulas, denominators, aggregation, estimators, edge cases and scientific display transforms.

### Part III, Chapter 8 — Claims and Reproducibility

Owns supported inference, interpretation boundaries, reporting requirements, export content and reproducibility limits.

### Part IV — Practical Supplements

Owns optional platform-, device- and procedure-specific operating guidance, switching recipes and calibration procedures.

## Placement test

Place information according to when the operator needs it:

- before or during the experiment: Chapter 1;
- while reading a completed result: Chapter 2;
- while repeating, reporting or preserving it: Chapter 3;
- while configuring an exact control or diagnosing behavior: Part II;
- while auditing the calculation or scientific claim: Part III;
- only for a particular platform, transmitter or accessory: Part IV.

## Controlled-duplication rule

Use one authoritative home for the complete explanation. Retain a short point-of-action reminder where omission could cause an invalid experiment, incorrect configuration or materially wrong interpretation. The reminder must link to the authoritative home and must not reproduce the full mechanics.

## Relocation protocol

1. Identify the authoritative destination.
2. Classify the source as unique useful guidance, duplicated explanation, obsolete material, implementation-only detail or unsupported claim.
3. Add or improve the destination before removing unique guidance from the source.
4. Retain a concise reminder and cross-reference at the original decision point when needed.
5. Update the Table of Contents, anchors, incoming links, references and parallel terminology.
6. Record every relocation in `01_relocation_ledger.md`.
7. Record every original sentence or paragraph that does not survive anywhere in the candidate in `doc_en_fallout.md`.

## Review constraints

- Part 0 remains the production baseline unless a concrete defect is found.
- No new worked Success example is added in this review.
- Exact formulas remain defined once in Chapter 7.
- Device-specific TX A/B examples move out of the main operator playbook if they can be preserved in Part IV.
- Existing anchors are retained where practical; compatibility aliases may remain when headings are reorganized.
- References are not renumbered during drafting unless required by a changed first-use order; any renumbering must be global and internally consistent.

## Deliverables

- temporary review notes under `docs/drafts/manual_review_en/`;
- `docs/drafts/doc_en_candidate.py`: one executable candidate module that derives the complete candidate from the production English manual using explicit anchor-bounded replacements;
- `docs/drafts/doc_en_fallout.md`: verbatim original wording not retained anywhere in the candidate;
- `docs/drafts/AGENTS_documentation_guidance_proposal.md`: proposed durable documentation-maintenance instructions.
