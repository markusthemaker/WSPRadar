# Proposed AGENTS.md Documentation Guidance

## Assessment of the current instructions

The existing `End-User Manual Style and Structure` section is already strong. It correctly requires:

- operator-first progressive explanation;
- one authoritative home for each content type;
- cross-references rather than repeated full mechanics;
- exact formulas in Scientific Methods;
- an operator-relevance test;
- explicit claim boundaries;
- preservation of unique useful guidance during restructuring.

The remaining gap is operational: it does not define chapter ownership precisely enough to prevent a playbook such as Section 1.4 from gradually accumulating control tables, algorithms, device recipes, repetition guidance and reporting rules.

## Proposed addition

Add the following after the existing MECE and operator-relevance guidance.

---

### Manual Content Ownership and Relocation

Place end-user information in the layer where the reader needs it and keep the complete explanation in one authoritative home:

- **Part 0 — Preface:** motivation, minimum WSPR background, experiment-question selection and the result blocks produced by one run.
- **Part I, Chapter 1 — Experiment Playbooks:** which experiment answers the question, the minimum valid physical setup, critical pre-run warnings and the design's principal interpretation boundary. Do not reproduce complete control ranges, exact algorithms or device-specific procedures.
- **Part I, Chapter 2 — Read Your Results:** how to interpret the completed result, including map, Stations and Spots, Segment Inspector, Station Insights and Drill-Down. Summarize scientific mechanics only where omission would cause a materially wrong reading.
- **Part I, Chapter 3 — Strengthen and Communicate:** exploratory versus confirmatory use, repetition, reversal and control experiments, conclusion language and preservation of physical station context.
- **Part II — Controls and Troubleshooting:** exact UI labels, defaults, ranges, applicability, configuration behavior, saved-state behavior and diagnosis.
- **Part III, Chapter 6 — Literature and Positioning:** scientific lineage, prior art, source-specific boundaries and bounded novelty claims.
- **Part III, Chapter 7 — Scientific Methods:** exact eligibility, identity, matching, pairing, formulas, denominators, aggregation, estimators, edge cases and scientific display transforms.
- **Part III, Chapter 8 — Claims and Reproducibility:** supported inference, interpretation limits, reporting requirements, export content and reproducibility boundaries.
- **Part IV — Practical Supplements:** optional platform-, transmitter-, accessory- and procedure-specific setup or calibration guidance.

Use this timing test when placement is unclear:

- needed before or during the physical experiment -> Chapter 1;
- needed while reading completed evidence -> Chapter 2;
- needed when repeating, reporting or preserving the experiment -> Chapter 3;
- needed to operate an exact control or diagnose behavior -> Part II;
- needed to audit the calculation or scientific claim -> Part III;
- needed only for a particular device or platform -> Part IV.

#### One authoritative home plus point-of-action reminders

Define the complete explanation once. A concise warning or summary may appear at the point of action when omitting it could cause an invalid experiment, incorrect configuration or materially wrong interpretation. The reminder must link to the authoritative home and must not reproduce the complete mechanics.

Examples:

- define the power-normalization equation in Section 7.5; retain `report actual power` as a warning in the TX A/B playbook;
- define scheduled-pair construction in Sections 7.1 and 7.7; retain `pairing is automatic and deterministic` in the playbook;
- define exact schedule choices in Section 4.3; retain `enter each path's actual recurrence and UTC phase` in the playbook;
- keep device-specific Ultimate3S or QMX recipes in an appendix and link to them from the playbook.

#### Relocation protocol

For a substantial documentation move:

1. Identify the authoritative destination before removing source text.
2. Classify the source passage as unique useful guidance, duplicated explanation, obsolete material, implementation-only detail or unsupported claim.
3. Add or improve the destination before removing unique guidance from the source.
4. Retain a concise reminder and cross-reference at the original decision point when needed.
5. Maintain a relocation ledger for multi-section or multi-part restructuring.
6. Record verbatim any original passage not retained anywhere, together with its section, disposition and reason.
7. Update the Table of Contents, anchors, incoming links, references and both language versions in the same completed integration.
8. Verify that no useful guidance remains only in an obsolete or removed location.

#### Exploratory and confirmatory guidance

When documentation describes evidence strengthening, distinguish exploratory use from confirmatory repetition. An initial run may identify a possible pattern. Before a confirmatory run, instruct the operator to fix the relevant direction, band, benchmark, filters, thresholds, schedule and primary evaluation scope. Alternative radii, time windows or scopes should be reported as sensitivity analyses rather than selected only because they are favorable.

#### Stability and repeatability

Do not use `stable` ambiguously. Distinguish:

- **sample Stability:** sensitivity of a displayed statistic to resampling the evidence already present in one run;
- **experimental repeatability:** persistence of the observed pattern in a new controlled run or operating window.

A narrow Stability interval does not by itself establish future repeatability, independence, calibration or statistical significance.

#### English and German structural parity

English and German manuals must retain equivalent section ownership, claims, warnings, formulas, references and cross-links. German should be a native technical adaptation using established amateur-radio terminology, not a mechanically literal translation. A relocation is incomplete until both languages have the same authoritative content home.

#### Documentation restructuring checks

For a substantial manual restructuring, verify:

- every heading in the Table of Contents points to one existing anchor;
- retained compatibility anchors do not create duplicate headings;
- every defined term is introduced before it is relied upon;
- formulas and complete algorithms have one authoritative home;
- no device-specific procedure interrupts the main operator journey;
- no useful original guidance was silently dropped;
- source references remain globally numbered in order of first use;
- English and German structures and claim boundaries remain equivalent;
- README synchronization and web/PDF rendering are completed after authoritative integration;
- the candidate or integrated manual imports/compiles and all anchor-bounded transformation assertions pass.

---

## Recommended integration approach

Do not replace the existing style instructions. Append the proposed block, then remove only wording that becomes strictly duplicated. The current operator-first, MECE, scientific-home and preservation rules should remain controlling principles.
