# Global English Manual Integration Check

## Baseline and scope

- Baseline production commit: `78e286d312890bb0bbe5c512f8557962bb083c52`
- Baseline `docs/doc_en.py` blob: `da1fb29f948811483193a8d3c2adcfecb645f856`
- Production Part 0 retained except for `effect` -> `observed pattern` in Section 0.3.
- No production or runtime file is modified by this review branch.
- No worked Success example is added.
- No new external reference is introduced.

## Candidate design

`docs/drafts/doc_en_candidate.py` imports the production `DOC_EN` and applies explicit replacements bounded by stable manual anchors or exact baseline passages. This makes the candidate complete while preserving every unchanged production section.

The candidate fails loudly when:

- the reviewed production Part 0 is absent;
- a start marker is missing or duplicated;
- an exact passage has drifted;
- a required revised section is absent;
- superseded wording remains.

Run from the repository root:

```bash
python docs/drafts/doc_en_candidate.py > /tmp/wspradar-doc-en-candidate.md
```

## Structural checks completed in the review

- Part 0 remains motivation and orientation.
- Chapter 1 now contains minimum valid experiment setup and point-of-action warnings rather than complete algorithms or device recipes.
- Chapter 2 remains the map-to-row evidence-reading path.
- Chapter 3 now distinguishes exploratory analysis, confirmatory repetition, sample Stability and experimental repeatability.
- Section 4.3 owns exact TX A/B schedule controls.
- Sections 7.1 and 7.7 remain the authoritative homes for scheduled-pair construction.
- Section 7.5 remains the authoritative home for power normalization.
- Section 5.6 now owns database-origin, provider-reason and cache-delivery interpretation.
- Appendix B owns transmitter- and switch-specific sequential TX A/B procedures.
- Section 8 remains the authoritative claim and reproducibility boundary.

## Cross-reference and anchor decisions

- Existing top-level anchors are preserved.
- Published `2.5a/b` and `2.6a/b` numbering is retained to avoid unnecessary link churn.
- The legacy empty `sec-3-1` anchor remains inherited as a compatibility alias.
- Appendix B gains anchors `sec-b-1` through `sec-b-5` and matching Table of Contents entries.
- Moved content links back to Sections 3.2, 4.3, 7.1, 7.5, 7.7 and Appendices B/C as applicable.

## Preservation audit

- Every relocation is marked `Completed` in `01_relocation_ledger.md`.
- Original wording not retained verbatim is recorded in `doc_en_fallout.md` with section, disposition and reason.
- QMX, Ultimate3S, relay installation, safety and calibration guidance remain present.
- The only substantive claim removed rather than relocated is the unqualified implication that short-term changes necessarily tend to average down in a balanced sequential run. It is replaced by a random-versus-systematic distinction.

## Validation still required before production integration

The GitHub connector supports file review and writes but does not execute repository Python. Before replacing `docs/doc_en.py`, run locally or in CI:

```bash
python -m compileall -q docs/drafts/doc_en_candidate.py
python docs/drafts/doc_en_candidate.py > /tmp/wspradar-doc-en-candidate.md
python -m pytest tests/regression -q
```

Then verify:

1. the candidate executes without an assertion failure;
2. every Table of Contents link resolves in the rendered web manual and PDF;
3. Markdown tables, formulas and page breaks render correctly;
4. the English candidate is integrated into authoritative `docs/doc_en.py` rather than imported from it;
5. the German manual is updated with equivalent structure, warnings, claims and links;
6. `README.md` is regenerated through `scripts/sync_readme_from_doc_en.py`;
7. Python compilation and `git diff --check` pass;
8. references remain globally consistent after German and README integration.

## Production-integration note

The overlay is a review artifact, not the intended permanent architecture. Final integration should materialize the resolved `DOC_EN` content into `docs/doc_en.py`, update `docs/doc_de.py`, regenerate `README.md`, run the documented checks and then remove or archive the temporary review workspace as appropriate.
