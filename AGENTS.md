# WSPRadar Contributor Instructions

These instructions apply to the complete repository. Read `AGENT_README.md` and
`docs/architecture.md` before changing runtime behavior. `README.md` is the
generated end-user and scientific manual, not the repository engineering guide.

## Repository Structure

| Path | Responsibility |
| --- | --- |
| `app.py` | Streamlit entry point and top-level page orchestration. |
| `config/` | Application limits, bands, demo profiles, and plotting constants. |
| `core/` | Scientific analysis, SQL construction, data access, caching, admission control, map aggregation, and rendering primitives. |
| `ui/` | Streamlit adapters, state, controls, analysis orchestration, inspectors, plots, and exports. |
| `docs/` | English and German manuals plus lazy PDF generation. |
| `tests/regression/` | Regression and contract tests for scientific, persistence, concurrency, UI-boundary, and performance-sensitive behavior. |
| `scripts/` | Repository maintenance, release, fixture-building, and README synchronization scripts. |
| `tools/Timed-AB-Relay-Switch/` | Separate USB relay console utility; it is not part of the Streamlit runtime. |
| `.streamlit/` | Streamlit theme and server configuration. |
| `.devcontainer/` | Linux development-container definition and native package setup. |
| `.github/workflows/` | Deployment wake-up automation. There is currently no test or lint workflow. |

## Authoritative Files

- `docs/doc_en.py` and `docs/doc_de.py` are the authoritative end-user manuals.
- `README.md` is generated from `docs/doc_en.py` by
  `scripts/sync_readme_from_doc_en.py`. Do not hand-edit `README.md`; the sync
  script rewrites the complete file.
- `AGENT_README.md` is the authoritative repository setup and operating guide.
- `docs/architecture.md` is the authoritative code-level architecture guide.
- `config/app_config.py` owns runtime URLs, cache settings, HTTP limits,
  admission limits, and inspector-cache limits.
- `config/bands.py`, `config/demo_profiles.py`, and `config/plot_constants.py`
  own band mappings, demo definitions, and map/scientific plotting constants.
- `core/analysis_context.py` defines canonical scientific configuration.
- `core/presentation_context.py` defines language, labels, and theme inputs.
- `core/opportunity_engine.py` defines the processed opportunity-row schema and
  required Parquet projections.
- `core/artifact_store.py` owns cache namespaces, paths, locks, atomic writes,
  leases, touching, and TTL cleanup.
- `core/input_validation.py` and `core/time_utils.py` own dependency-free input
  and time helpers used by the idle shell; `ui/result_state.py` owns the
  lightweight result-reset lifecycle and its session-state keys.
- `ui/documentation_state.py` owns documentation visibility and one-shot scroll
  state; `ui/documentation_scroll_trigger.py` owns the browser viewport signal.
- `tests/regression/` is the executable behavioral contract.

## Setup

The repository has no `pyproject.toml`, package metadata, or root-level declared
Python version. The development container uses Python 3.10. The commands below
were verified with Python 3.12.13 on 2026-07-11.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

For runtime-only installation, install `requirements.txt` instead. Linux needs
the native Cairo/PROJ/GEOS support represented by `packages.txt` and
`.devcontainer/devcontainer.json`.

Verification note: dependency imports and `python -m pip check` passed in the
existing environment. A completely fresh environment install and the full
development-container build were not executed during the 2026-07-11
documentation review, so platform-specific installation remains unverified.

## Run, Test, and Check Commands

Start the application from the repository root:

```powershell
python -m streamlit run app.py
```

The entry point was verified by starting it headlessly on an alternate port and
receiving `200 ok` from `/_stcore/health`.

Run the complete regression suite:

```powershell
python -m pytest tests/regression -q
```

Expected result as of 2026-07-11: `116 passed, 1 skipped`. The skip is the
fixture-integrity test because no generated fixture is committed under
`tests/regression/fixtures/`. One existing Matplotlib pending-deprecation
warning is emitted from `ui/plots/evidence_figures.py`.

Compile all Python sources:

```powershell
python -m compileall -q app.py config core docs ui scripts tests tools
```

Check patch whitespace:

```powershell
git diff --check
```

There is no configured Ruff, Flake8, Black, mypy, pre-commit, or equivalent
lint command. Do not document or require one until its configuration is added.
The GitHub workflow currently wakes the deployed app; it does not run tests.

## Coding Conventions

- Preserve the separation between scientific configuration and presentation.
  Localized labels and theme values must not influence SQL or scientific
  branches.
- Keep Streamlit imports and session-state access in `app.py` and `ui/`.
  `core/` and pure inspector view-model modules must remain UI-independent.
- Preserve the idle import boundary: configuration callbacks and result resets
  must not import analysis, inspector, DataFrame, HTTP, Matplotlib, Cartopy, or
  export-rendering modules. Load that scientific runtime only for an active run.
- Pass `AnalysisContext` into scientific work and `PresentationContext` into
  rendering. Add fields deliberately because they affect cache keys and tests.
- Keep SQL construction and post-fetch classification deterministic. Validate
  callsigns, locators, dates, and mode-specific inputs before interpolation.
- Preserve numerical precision unless a scientific equivalence test justifies
  changing it. Coordinates, SNR values, solar calculations, time-bin rules,
  outcome definitions, and aggregation denominators are scientific behavior.
- Use the canonical time-slot conversion in `core/opportunity_engine.py`; do
  not reintroduce a stored duplicate cycle timestamp.
- Preserve the explicit opportunity schema, categorical repeated fields,
  `observed=True` categorical grouping, and projected Parquet reads.
- Treat DataFrame ownership as an API contract. Do not add unconditional full
  copies to the opportunity or solar pipelines.
- Use `core/artifact_store.py` for shared filesystem artifacts. Preserve path
  validation, per-key coordination, unique temporary files, atomic replacement,
  leases, and access touching.
- Use `core/matplotlib_runtime.py` for Matplotlib serialization and dispose of
  figures after rendering. Matplotlib is shared mutable process state.
- Keep inspector view-model and figure preparation pure. The Streamlit fragment
  should manage selection and rendering, not duplicate scientific preparation.
- Follow existing naming and module boundaries before adding abstractions.

### Readability, Naming, and Documentation

- Optimize code for human readability and maintainability, not merely for
  brevity.
- Use descriptive, self-explanatory names for variables, functions, methods,
  classes, constants, modules, and DataFrame columns.
- Prefer complete words over abbreviations. Domain-standard abbreviations such
  as `WSPR`, `TX`, `RX`, `SNR`, `UTC`, `SQL`, `UI`, and `DB` are acceptable when
  their meaning is unambiguous.
- Use established WSPRadar terminology consistently. Do not introduce synonyms
  for existing concepts such as Target, Reference, Elsewhere, Other Signals,
  Joint, Opportunity, Success Rate, Decode Outcomes, or Target-Active Gate.
- Function and method names should describe the action performed, normally using
  a verb phrase such as `build_analysis_batches`, `prepare_opportunity_rows`, or
  `validate_config_upload`.
- Variable names should describe the value's meaning rather than its
  implementation or temporary role. Avoid vague names such as `data`, `value`,
  `result`, `item`, `obj`, `tmp`, `process`, or `handle` when a more precise name
  is available.
- Boolean names must read as predicates and normally begin with `is_`, `has_`,
  `should_`, `can_`, or `requires_`.
- Collection names should normally be plural.
- Include units, coordinate systems, or time bases in names where ambiguity is
  possible, for example `distance_km`, `timeout_seconds`,
  `response_size_bytes`, `snr_correction_db`, `cycle_start_utc`, and
  `latitude_degrees`.
- Avoid single-letter names except for conventional short-lived indices or
  clearly documented mathematical notation.
- A function should have one clear responsibility. If its purpose cannot be
  expressed with a concise and precise name, consider splitting it rather than
  hiding multiple responsibilities behind a generic name.
- Every new or materially changed public class, function, and method, and every
  new or materially changed non-trivial private function, must have a concise,
  human-readable docstring. Do not perform unrelated repository-wide docstring
  backfills as part of a scoped task.
- Docstrings should document the relevant parts of:
  - purpose and scientific meaning;
  - input expectations;
  - return type or row/schema meaning;
  - units and time basis;
  - side effects;
  - raised exceptions or structured failure behavior;
  - important invariants and assumptions.
- Complex SQL, DataFrame, caching, concurrency, and scientific pipelines must
  document the meaning of rows, required columns, grouping levels, denominators,
  ownership, and lifecycle where these are not immediately obvious.
- Comments should explain why the code exists, which invariant it protects, or
  why an apparently simpler implementation is incorrect. Do not add comments
  that merely restate Python syntax.
- Preserve useful existing comments and docstrings when editing code. Update
  them whenever behavior, names, units, schemas, or assumptions change.
- Do not use documentation as a substitute for unclear code. Improve names and
  structure first, then document the remaining non-obvious reasoning.
- Do not perform broad naming cleanups as part of an unrelated task. Renames must
  update all call sites, tests, documentation, serialized fields, DataFrame
  contracts, cache keys, and export consumers atomically.

## Change Scope

- Make the smallest complete change that satisfies the task.
- Do not perform unrelated refactoring, renaming, formatting, or cleanup.
- A bug fix should include a regression test that fails without the fix.

## Architectural Constraints

- The application is read-only with respect to wspr.live. Do not add upstream
  mutation or credentials without an explicit design review.
- Analysis and export gates are process-local. Their limits are safety controls,
  not globally distributed quotas.
- Query, derived-analysis, and session-artifact files have different lifecycles.
  Do not collapse their namespaces or cleanup policies.
- Session artifacts may remain in use after a Streamlit rerun. Cleanup must
  honor active leases and touches rather than deleting by age alone.
- Duplicate analysis admission is keyed by stable session ownership plus a
  scientific request fingerprint. Demo identity is part of the fingerprint so
  separate users can run the same demo while one session cannot enqueue the
  same work repeatedly.
- Upstream CSV and Parquet reads must retain connect/read deadlines, streamed
  byte ceilings, and structured errors.
- The base-map cache is shared and constructed under same-key coordination.
  Writes must remain unique-temporary-plus-atomic-replace operations.
- Export recipes reuse completed analysis artifacts; exports must not rerun the
  upstream scientific query.
- Documentation PDF generation is lazy, process-cached, and single-flight.

## Do Not Change Casually

- SQL predicates, cycle synchronization, WSPR frame selection, legacy decode
  fallback, normalized SNR formulas, rounding, solar thresholds, and outcome
  classification.
- Opportunity map and inspector denominators, especially the distinction between
  peer-balanced segment averages and pooled diagnostics.
- Maidenhead conversion, distance/azimuth geometry, map projection, and range
  bucket boundaries.
- Cache-key inputs, artifact path layout, TTL/lease behavior, lock ordering, and
  queue ownership semantics.
- Admission defaults in `config/app_config.py`; they are sized for limited
  Streamlit Community Cloud resources.
- `.streamlit/config.toml`, especially CORS and XSRF settings. They are currently
  disabled and are a documented security risk, not harmless formatting.
- `docs/doc_en.py`, `docs/doc_de.py`, and README synchronization. Preserve full
  manual content and translations.
- Release scripts. `git-baseline-temp.ps1` resets the local `temp` branch to its
  remote baseline and is destructive to uncommitted work.
- Files under `tests/demo/`; they are historical exported evidence, not current
  generated regression fixtures.

## Compatibility

- Treat saved `.config` files, exported metadata, Parquet projections, DataFrame
  columns, and reproducibility packages as compatibility-sensitive interfaces.
- Changes to these interfaces require explicit migration or versioning decisions
  and corresponding regression tests.

## Handoff Requirements

- Summarize changed behavior, not merely changed files.
- State which checks were actually executed and their results.
- Explicitly identify unverified assumptions, remaining risks, and checks that
  could not be run.

## Definition of Done

1. The implementation follows the existing core/UI and context boundaries.
2. Scientific and user-visible behavior is unchanged unless the task explicitly
   requests and documents a change.
3. Tests cover changed behavior, including failure, ownership, concurrency, or
   persistence semantics where relevant.
4. `python -m pytest tests/regression -q` passes.
5. Python compilation and `git diff --check` pass.
6. Streamlit starts successfully when entry-point or dependency behavior changes.
7. No unrelated files or user changes are reverted.
8. CHANGELOG_DAILY.md is updated for every meaningful change. Consecutive changes belonging to the same feature, fix, or refactoring effort are consolidated into one coherent entry that follows the existing changelog structure, tone, and level of detail.
9. Documentation and configuration are updated when contracts or commands change.
10. Generated user documentation is changed through its authoritative source,
   followed by the sync workflow, rather than by editing `README.md` directly.
11. Any check that could not be run is stated explicitly in the handoff.

## Documentation Maintenance

- Treat `AGENTS.md`, `AGENT_README.md`, and `docs/architecture.md` as living
  project documentation.
- When a change introduces or alters architecture, repository structure,
  development commands, coding conventions, authoritative files, invariants,
  or operational constraints, update the corresponding documentation in the
  same change and make those changes explicit to the user once you are done
- Do not update these files for implementation details that do not affect their
  documented contracts.
- When end-user or scientific behavior changes, update `docs/doc_en.py` and
  `docs/doc_de.py`, then regenerate `README.md` using
  `scripts/sync_readme_from_doc_en.py`.
- Before completing a task, verify that the documentation still maps to the
  implementation.

### End-User Manual Style and Structure

Use the English manual's operator-first, layered style as the reference model
for future end-user documentation work:

- Write primarily for radio amateurs and WSPR operators: first-time WSPR users,
  experienced experimenters, and scientifically critical readers. Keep
  repository-engineering detail in contributor or architecture documentation.
- Begin with why WSPRadar is useful and distinctive, followed by the minimum
  WSPR background needed to understand it. Explain genuine strengths without
  unsupported `first`, `only`, calibrated-measurement, or causation claims.
- Build understanding progressively. Introduce terms such as Target, Reference,
  peer, Success Rate, Decode Outcomes, and Delta SNR in plain operator language
  before relying on them. Do not front-load a dense glossary.
- Preserve an operator journey: value and WSPR primer; valid Quick Start;
  analysis choice and experiment design; result interpretation; controls and
  defaults; troubleshooting; scientific methods; limitations, valid claim
  language, and reproducibility; then operational and literature appendices.
- Keep that structure MECE. Give experiment selection, UI interpretation,
  configuration, scientific algorithms/formulas, and inference limits one
  authoritative home each. Cross-reference instead of repeating full
  explanations in several mode guides.
- Layer practical and scientific depth. State what a result means for the
  operator first, then place exact matching, denominators, evidence units,
  aggregation, and formulas in the scientific section.
- Make the Quick Start teach how to produce and recognize a valid result, not
  merely which buttons to click.
- Keep the tone technically rigorous but practical and inviting. Each paragraph
  should help answer an operator's likely `so what?`; avoid dry implementation
  narration that does not change setup, interpretation, or claim language.
- Distinguish observations, assumptions, heuristics, and supported inferences.
  Explain conditional denominators and asymmetries, and state explicitly which
  claims the evidence does and does not support.
- Define each formula once in its scientific home, ensure it renders in both the
  Web UI and generated PDF, and link to it from practical sections when needed.
- Use current UI labels, defaults, result units, export contents, and behavior.
  Challenge documentation claims against implementation and regression tests;
  report disagreements rather than changing runtime behavior to fit prose.
- Keep operational procedures and literature/prior art available without
  interrupting the main operator flow. Use appendices and cite every retained
  reference in order of first use.
- During restructuring, preserve unique, correct user guidance. Classify content
  before removal as duplicated, obsolete, implementation-only, scientifically
  unsupported, or genuinely useful; do not silently lose the last category.
