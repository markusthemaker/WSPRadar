# Contributing to WSPRadar

Contributions are welcome when they preserve WSPRadar's central objective: transparent, reproducible, and cautiously interpreted real-world station-system analysis using public WSPR observations.

Read `README.md`, `AGENTS.md`, and `docs/architecture.md` before changing analysis logic or architecture.

## Start with the correct issue type

Use the structured issue forms:

- **Bug report** for reproducible incorrect behavior or regressions
- **Feature request** for a new capability or material improvement
- **Scientific or methodological concern** for assumptions, statistics, data handling, interpretation, or scientific claim wording

Use GitHub Discussions for questions, experiment-design advice, result interpretation, and ideas that are not yet sufficiently defined for implementation.

## Manual issue workflow

WSPRadar intentionally starts with a manual workflow. Automation must not decide whether a scientific concern is valid or whether a proposed method should become part of the analysis.

Recommended state labels:

1. `needs-triage` — newly submitted and not yet evaluated
2. `needs-reproduction` — a defect cannot yet be reproduced
3. `needs-design` — behavior or methodology requires a decision
4. `accepted` — direction and scope are approved
5. `ready-for-codex` — implementation task is sufficiently specified
6. `in-progress` — implementation has started
7. `blocked` — progress depends on an unresolved external decision or dependency

Recommended classification labels include `bug`, `feature`, `scientific-method`, `documentation`, `performance`, `user-interface`, and `data-query`.

Labels are a maintainer aid, not a substitute for a complete issue body.

## Triage checklist

Before marking an issue `ready-for-codex`, the maintainer should ensure that it contains:

- **Problem** — the specific defect or unmet need
- **Intended behavior** — the approved observable result
- **Scope** — files, modes, or workflows allowed to change
- **Out of scope** — behavior that must remain unchanged
- **Acceptance criteria** — objective completion conditions
- **Relevant modules** — likely code and documentation locations
- **Required tests** — unit, regression, fixture, or manual validation
- **Documentation impact** — README, user documentation, architecture, terminology, and configuration
- **Changelog impact** — whether `CHANGELOG_DAILY.md` must be updated

Scientific decisions must be made explicitly by a maintainer. Codex may identify ambiguity or propose alternatives, but it must not silently redefine the analysis model.

## Codex implementation handoff

A suitable handoff prompt is:

> Implement GitHub issue #NUMBER completely. Treat the approved issue body and acceptance criteria as authoritative. Follow `AGENTS.md`. Preserve all existing behavior outside the stated scope. Add or update regression tests, documentation, and `CHANGELOG_DAILY.md` where required. Do not change the scientific methodology beyond the explicitly approved scope. Report any unresolved ambiguity in the pull request.

For substantial work, use a dedicated branch and open a pull request linked to the issue.

## Code and scientific requirements

- Preserve exact callsign, cycle, evidence, and aggregation semantics unless the approved issue explicitly changes them.
- Keep scientific configuration independent from localized labels, themes, and presentation state.
- Prefer explicit, human-readable variable and function names.
- Document non-obvious calculations, assumptions, and boundary conditions for human readers.
- Add regression coverage for bug fixes and method changes.
- Validate backward compatibility for saved configurations and exports when affected.
- Avoid describing WSPR-derived results as calibrated antenna gain, efficiency, sensitivity, or take-off-angle measurements unless a separately validated method supports that claim.

## Pull requests

A pull request should:

- link the issue it implements
- explain what changed and why
- identify scientific or methodological impact
- state what remains intentionally unchanged
- list tests and manual checks performed
- update documentation and `CHANGELOG_DAILY.md` when applicable
- remain reviewable and avoid unrelated refactoring

Generated code must be reviewed before merge. Passing tests do not by themselves validate a scientific assumption.
