# WSPRadar Contributor Instructions

These instructions apply to the complete repository. Read `AGENT_README.md` and
`docs/architecture.md` before changing runtime behavior. `README.md` is the
generated end-user and scientific manual, not the repository engineering guide.

## Repository Structure

| Path | Responsibility |
| --- | --- |
| `app.py` | Streamlit entry point and top-level page orchestration. |
| `config/` | Application limits, bands, filename-ordered standalone demo configurations and their reader, saved-config schema constants and formal JSON Schema, and plotting constants. |
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
- `config/app_config.py` owns ordered database providers, provider request and
  cooldown policies, runtime URLs, cache settings, HTTP limits, admission
  limits, and inspector-cache limits.
- `config/bands.py`, `config/demos/*.config`, `config/demo_profiles.py`,
  `config/config_schema.py`, `config/config_codec.py`,
  `config/wspradar-config.schema.json`, and `config/plot_constants.py` own band
  mappings, ordered standalone demo definitions, demo loading, the versioned
  saved-config contract, schema-version handling and formal JSON Schema, and
  map/scientific plotting constants.
- `core/analysis_context.py` defines canonical scientific configuration.
- `core/presentation_context.py` defines language, labels, and theme inputs.
- `core/opportunity_engine.py` defines the processed opportunity-row schema and
  required Parquet projections.
- `core/artifact_store.py` owns cache namespaces, paths, locks, atomic writes,
  leases, touching, and TTL cleanup.
- `core/input_validation.py` and `core/time_utils.py` own dependency-free input
  and time helpers used by the idle shell; `ui/result_state.py` owns the
  lightweight result-reset lifecycle and its session-state keys;
  `ui/analysis_submission_state.py` owns token-aware in-flight submission state.
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

For automated Windows checks, invoke an existing repository environment directly
as `.\.venv\Scripts\python.exe`; activation is unnecessary. Verify that this
interpreter starts and imports the declared dependencies before running checks.
Do not combine another Python runtime with `.venv` packages through `PYTHONPATH`;
if the launcher fails, inspect `.venv/pyvenv.cfg` and base-interpreter access
instead of treating the failure as evidence that dependencies are missing.

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

Run the complete regression suite on Windows through the checked-in foreground
runner:

```powershell
.\scripts\run_regression.cmd
```

On Linux or macOS, invoke pytest directly:

```bash
python -m pytest tests/regression -q
```

The Windows runner invokes `.\.venv\Scripts\python.exe -u -m pytest` directly,
keeps pytest attached to the foreground terminal, validates the fixed serial
fallback chunks, and propagates pytest's exit code. The dated complete-run
record is maintained in `AGENT_README.md`. The fixture-integrity test is skipped
when no generated fixture is committed under `tests/regression/fixtures/`. One
existing Matplotlib pending-deprecation warning is emitted from
`ui/plots/evidence_figures.py`.

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

### Progress Updates for Broad Tasks

Keep the user informed during broad audits, multi-file implementation, cleanup,
or verification work that lasts more than a short interaction:

- give an initial scope/status update before substantial tool work, then update
  at meaningful milestones and at least once every 60 seconds while work is
  actively continuing;
- include rough, separately labelled percentages for review/audit,
  implementation or cleanup, and verification when those phases apply, plus a
  concrete statement of what remains;
- treat percentages as honest estimates rather than false precision. Revise
  them transparently when new coupling or additional scope is discovered;
- report unexpected failures, stalls, terminal-session interruptions, or
  possible leftover processes promptly, together with the bounded recovery
  action being taken;
- do not hide progress behind a long blocking tool call. Keep long checks in a
  Codex-managed foreground terminal session that can be polled, or run them as
  deterministic fixed chunks, so commentary remains available and the user can
  redirect the work;
- keep short tasks concise; percentage updates are unnecessary when the work
  completes within one quick tool round trip.

### Running Long Windows Checks in Foreground Terminal Sessions

Run verification commands in a Codex-managed foreground terminal session. Allow
a long command to yield a reusable terminal or session identifier, then poll
that same session; keep the command attached to its terminal for its entire
lifetime.

- invoke the repository interpreter directly and keep each pytest, compilation,
  or documentation check in the foreground;
- use `.\scripts\run_regression.cmd` for the complete Windows regression suite.
  The launcher applies a process-local execution-policy bypass only to the
  checked-in PowerShell runner, which invokes the repository venv directly with
  unbuffered Python and propagates pytest's exit code;
- poll the same terminal session at bounded intervals of no more than 60 seconds
  and provide progress commentary. Quiet output alone is not evidence of a hang
  or failure;
- do not use `Start-Process`, PowerShell background jobs, hidden-window
  launchers, detached child processes, output redirection, or custom
  PID/stdout/stderr/exit-status supervisors for routine checks. A tool-call yield
  or duration limit is not a reason to detach the command. In particular,
  `Start-Process` can fail before launch when a host process exposes both `Path`
  and `PATH`;
- treat the Windows venv launcher and its configured base interpreter as one
  foreground command. Seeing both processes is not by itself evidence of a
  stall; the foreground terminal's output and final exit code are authoritative;
- prefer one complete pytest session because it also detects cross-module state
  leakage. If that session cannot be retained reliably, run
  `.\scripts\run_regression.cmd -Chunk 1` through `-Chunk 5` serially. The
  checked-in manifest is validated before every invocation and fails if a test
  module is unassigned, duplicated, renamed, or removed. Never run these chunks
  concurrently because pytest clears and reuses the same `.test` workspace;
- use `.\scripts\run_regression.cmd -ValidateChunks` to check the fixed fallback
  partition without running pytest. Use
  `.\scripts\run_regression.cmd -Durations 30` to report the slowest tests in a
  canonical serial full-suite run;
- do not install or use pytest-xdist and do not pass `-n` until a separate audit
  proves that concurrency, filesystem, Streamlit, Matplotlib, cache, port, and
  process-state tests are worker-isolated. The runner rejects xdist worker
  options. Timing results may inform a later checked-in chunk rebalance, but do
  not reshuffle a run already in progress;
- for a short startup or health check that must spawn a child process, use a
  bounded foreground wrapper. Retain the exact child handle or PID, enforce an
  explicit deadline, and terminate that exact child in a `finally` path,
  escalating from graceful termination only if the deadline expires;
- if a terminal session or tool call is interrupted, do not immediately
  relaunch the check. Reconnect to or poll the same session when possible. If a
  process may remain, validate its exact PID, executable, and command line before
  stopping that process tree; never stop every Python or pytest process by name;
- capture the terminal output and exit status before reporting. If no reliable
  exit status remains, report the affected run as inconclusive and rerun only
  the affected fixed chunk. Clean up only exact run artifacts after preserving
  any needed diagnostics.

## Verification Scope and Proportionality

Select the least expensive verification level that still exercises every
changed contract. Classify work by blast radius and failure consequence, not by
line count alone: a one-line scientific or cache-key change can require full
verification, while a multi-line localized-copy change can remain focused. If
the scope cannot be established confidently, use full verification.

For every change:

- run the most specific regression tests that exercise the changed behavior;
- run `git diff --check`;
- compile changed Python files or their containing package when Python changed;
- expand verification when a focused check exposes unexpected coupling, an
  affected caller lacks direct coverage, or a failure appears outside the
  expected scope;
- state the checks actually run and distinguish existing unrelated failures
  from failures caused by the change.

### Focused verification

Focused verification is sufficient only when the change is demonstrably
isolated, has direct regression coverage, and does not alter a shared runtime
contract. Typical examples are:

- localized copy, labels, help text, or non-interactive presentation composed
  from established UI primitives;
- a narrow documentation correction that is not a substantial manual
  restructuring;
- an isolated test, fixture, or private helper change after its callers and
  contracts have been inspected.

Run the directly affected test nodes or modules plus applicable localization
parity, schema, rendering, or synchronization checks. Compile only the changed
Python scope. The complete regression suite is not required for this class
during incremental work.

High-cost presentation and integration tests are scoped by the contract touched;
they are not a default addition to every focused run:

- run figure and plot rendering tests only when changes can affect `ui/plots/`,
  `core/plot_engine.py`, `core/matplotlib_runtime.py`, plotting constants,
  figure recipes, layout/render versions, preview/export parity, or their direct
  callers;
- run export-package and exported-figure tests only when changes can affect
  `ui/results_export.py`, export recipes, export metadata, exported projections
  or schemas, artifact ownership, filenames, or rendered export assets;
- run documentation PDF/rendering tests only when documentation generation,
  document content, PDF layout, fonts, or document-rendering dependencies change;
- run Streamlit AppTest input/integration modules only when application shell,
  input, state, callback, navigation, or submission behavior can change. Run the
  idle-import boundary test only for startup/import-boundary changes;
- do not decide scope from test filenames alone. Some evidence modules combine
  scientific recipe assertions with rendering assertions; when a shared recipe
  or caller changes, run the complete directly affected module.

These focused-scope rules do not override the full-verification triggers below.
When full verification is required, the complete suite runs, including figures,
PDFs, Streamlit integration, and exports.

Focused verification is not sufficient for changes to scientific calculations,
SQL, time synchronization, normalization, classification, geometry, context or
cache-key inputs, saved schemas or migrations, persistence and artifact
lifecycle, DataFrame ownership or projections, concurrency and admission,
provider selection or failover, shared callbacks or session ownership,
exports, dependencies, startup/import boundaries, security settings, or other
compatibility-sensitive interfaces.

### Targeted UI and browser verification

UI changes to CSS, layout, widget interaction, visibility, navigation,
accessibility, responsive behavior, upload/download flows, or browser-specific
integration require focused UI tests and the shortest additional runtime check
needed to prove the changed behavior. Prefer seeded state, component tests,
Streamlit AppTest, DOM assertions, or a targeted screenshot over manually
walking through prerequisite workflow steps.

A browser walkthrough is not required merely because a task includes a
screenshot or changes visible copy. Use browser verification only when the user
explicitly requests it, the behavior is browser-specific, or automated
structural tests cannot establish the requested visual or interactive outcome.
Do not continue through unrelated parts of the workflow after the changed
behavior has been verified.

### Full verification

Run the complete regression suite, full repository Python compilation, and
`git diff --check` when any of the following applies:

- the change touches one of the shared or compatibility-sensitive contracts
  excluded from focused verification above;
- the change spans multiple architectural layers or performs a broad refactor;
- focused tests reveal unexpected coupling or the blast radius remains
  uncertain;
- work is being finalized for release or submission to GitHub.

Accumulated changes that used focused verification incrementally must receive
one full verification run before their final release or GitHub submission.
Start Streamlit and check its health endpoint when entry-point, dependency,
startup, or import-boundary behavior changes. Add a targeted browser smoke test
only when the changed contract is browser-specific or remains unproven by
automated tests.

Documentation-only work uses the applicable documentation, rendering, link, and
synchronization checks. A substantial manual restructuring remains subject to
the complete verification requirements in **Documentation restructuring
checks** below.

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
- Treat UI values, uploaded configurations, and other external data as
  untrusted. Validate and normalize runtime inputs at their input boundary with
  explicit types, allowlists or ranges, and mode-specific invariants; reject
  invalid values with actionable field-specific errors. Repeat safety-critical
  validation at core boundaries, do not rely on widget constraints alone, and
  escape or encode text for its output context rather than interpolating
  unchecked values into SQL, paths, HTML, shell commands, or filenames.
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

### Configuration-Driven Variation

- Separate mechanism from policy and instance data. Runtime code implements
  generic behavior; authoritative configuration owns values and choices expected
  to vary by demo, profile, deployment, workflow, provider, presentation or
  operating context.
- Never branch runtime behavior on a specific record identity such as a
  demo/profile ID, filename, title, callsign, locator, display label or
  translated string. Identifiers identify records; they are not feature flags.
- Do not infer an independent semantic state from naming conventions, prose or a
  sentinel value when several meanings can share that value. Represent the state
  with an explicit typed configuration field.
- When records using one schema require different behavior, extend the schema
  with a validated field and implement one generic interpreter. Adding another
  record that uses an existing capability must require configuration changes,
  not another runtime branch.
- Keep each configurable value in one authoritative location. Do not duplicate
  configuration-owned mappings, defaults, thresholds or record-specific choices
  in callbacks, UI reconstruction, algorithms or compatibility tables.
- Keep configuration strict and auditable: define allowed values, defaults,
  conditional applicability and cross-field invariants in its authoritative
  schema and semantic validator. At persisted or external configuration
  boundaries, reject invalid combinations instead of silently repairing or
  guessing them.
- Preserve the scientific/presentation boundary. Persisted workflow or
  presentation configuration must not enter `AnalysisContext`, SQL, scientific
  branches, cache identity or request fingerprints unless it genuinely changes
  the scientific result.
- Code-defined constants remain appropriate for intrinsic algorithms,
  mathematical definitions, protocol/schema identifiers, security boundaries,
  safety limits, implementation dispatch and invariants that must not be
  operator-configurable. Centralize them in their authoritative module and
  document non-obvious cases.
- Before adding a literal record ID, per-record mapping or special-case branch to
  runtime code, stop and determine whether the distinction belongs in
  configuration. If code is genuinely required, document why configuration is
  unsuitable and cover the exception with a regression test.

### Readability, Naming, and Documentation

- Optimize code for human readability and maintainability, not merely for
  brevity.
- Keep human-maintained configuration, UI copy, and localization catalogs
  editor-friendly. In Python text catalogs such as `i18n.py`, keep each prose
  paragraph on one physical source line and rely on the editor's soft wrapping;
  represent long prose values with triple-quoted strings (`"""..."""`) instead
  of manually hard-wrapped adjacent string fragments. Retain physical line
  breaks only when they are semantically required, such as Markdown paragraph
  boundaries, lists, tables, or code blocks, and preserve the native formatting
  requirements of JSON, schemas, and other machine-readable formats.

#### Terminology Change Protocol

Treat established user-visible terminology as a cross-surface presentation
contract. A terminology change is incomplete until every applicable surface has
been audited, even when only some surfaces require edits.

Before editing:

- Do not change a plot axis label or a figure or panel title without the user's
  explicit approval of the replacement wording. A user request that explicitly
  supplies that wording, or the user's explicit approval of proposed wording,
  satisfies this requirement.
- Define the old term, the approved replacement, capitalization, singular/plural
  forms, and any RX/TX, Benchmark/Performance, or English/German variants.
- State whether the change affects only presentation terminology or also changes
  scientific meaning, configuration, schemas, exports, or compatibility.
- Identify canonical internal terms that must remain stable in code and
  supported contracts. Do not globally replace internal identifiers, DataFrame
  columns, classifications, formulas, schema fields, cache keys, or compatibility
  export headings merely because their visible presentation name changes. Do not
  expose those internal names in the narrative manuals merely to map prose back to
  the implementation.

Audit all applicable surfaces:

- `T`, `GUIDED_INPUTS`, `RESULT_GUIDANCE`, and other localization catalogs;
- Guided and Classic Input labels, captions, help text, validation messages,
  summaries, and fallback strings;
- result headers, maps, legends, figure titles, axes, annotations, tables,
  inspectors, drill-down views, empty states, and download descriptions;
- direction-, mode-, and benchmark-specific routing through shared renderers;
- `docs/doc_en.py`, `docs/doc_de.py`, generated `README.md`, architecture
  documentation, and changelog entries where the terminology is relevant;
- exported user-facing headings, metadata, recipes, filenames, and
  reproducibility documentation, while preserving compatibility contracts unless
  an explicit migration is authorized;
- regression tests, fixtures, snapshots, screenshots, and demo expectations that
  encode the visible terminology.

Search for the former term and likely variants before and after the change.
Classify every remaining occurrence as one of:

1. active user-facing text that must change;
2. canonical scientific or compatibility terminology that must remain;
3. obsolete or unreachable presentation text that should be removed;
4. unrelated prose requiring no change.

Do not treat a repository-wide text replacement as an audit. Follow actual call
paths, including shared components, localized fallbacks, conditional modes, and
Guided/Classic reuse, to establish which strings can be rendered.

For bilingual terminology changes:

- preserve English/German key and placeholder parity;
- use an approved phrase matrix for every semantic and directional variant;
- verify natural German wording rather than literal word substitution;
- ensure fallback text cannot expose superseded English or canonical terms in
  either language.

Tests must cover:

- the exact approved visible terms for every affected language and mode;
- routing through each distinct active path, including shared renderers;
- absence of superseded terminology from active presentation paths;
- preservation of canonical calculations, classifications, schemas, state keys,
  and compatibility exports;
- localization key and placeholder parity.

Update end-user documentation only when the change affects workflow,
interpretation, result meaning, controls, or terminology used to explain those
concepts. Pure styling or incidental wording changes require a documentation
audit but not necessarily a documentation edit. When authoritative English
documentation changes, regenerate `README.md` through the established sync
script.

The completion report must list:

- surfaces audited and files changed;
- superseded active phrases removed;
- intentional canonical or compatibility occurrences retained;
- routing and fallback behavior verified;
- tests and documentation-generation checks run;
- any surface that could not be verified.

#### Result-Guidance Copy

Treat `RESULT_GUIDANCE` as bilingual, point-of-use interpretation guidance for
completed results—not as input guidance, generic tooltip copy, marketing, a
duplicate scientific manual, or an automatic interpretation of live result
values. The catalog describes established scientific contracts; it must never
define or select scientific behavior.

- Every item must contain one substantive `read` paragraph and one shorter
  `limits` paragraph.
- Treat roughly 2,000 combined characters as a readability target, not a hard
  editorial limit. Prefer clear, scientifically complete wording over forced
  compression; modest overruns are acceptable when an essential distinction
  needs space. Tests may use a generous ceiling only to catch genuinely
  excessive popover copy.
- Begin `read` by naming the visible view and explaining its operator-relevant
  purpose. As applicable, define the evidence unit, denominator, aggregation or
  weighting; explain how complementary figures differ; and tell the operator
  how to assess breadth, depth, consistency and traceability.
- End the positive explanation with a practical reading heuristic. Lead with
  what the evidence can show; keep caveats in `limits`.
- Use `limits` to state the strongest relevant evidence boundary concretely:
  conditionality, missing observations, selection effects, weighting,
  calibration, confounding, independence or causal attribution. Avoid generic
  disclaimers.
- Use a technically rigorous but practical and inviting voice. Prefer concrete
  station and evidence language over implementation terminology or unnecessary
  statistical jargon. Do not pronounce a live result strong, weak, significant
  or causal.

- Reserve **experimental repeatability** for a result reproduced in a separate
  suitably controlled run. Describe dispersion or agreement inside one completed
  run as **within-run consistency**, **within-path consistency**, or
  **station-to-station agreement**.
- Name every displayed ratio by its actual denominator and scientific meaning.
  In Target-active-conditioned Benchmark, Only Target and Only Reference remain
  directional evidence rather than symmetric wins or losses. Joint Evidence Share
  is a pairability or coverage metric; never describe it as a Target score, win
  rate, or symmetric Target-versus-Reference success rate.
- Name visible figures, controls, units and result terms exactly as rendered.
  Use `<strong class="defined-term">...</strong>` for introduced semantic
  vocabulary, Markdown bold for named figures, and code spans for literal
  controls, formulas or displayed values.
- Include presentation mechanics only when they materially prevent a wrong
  interpretation; omit self-evident layout, typography and styling narration.
- Preserve English/German semantic, key and placeholder parity. German should
  be a natural technical adaptation, not a mechanically literal translation.
- Write each field as a complete prose fragment that remains grammatical when
  mode-, benchmark- or drill-down-specific items are concatenated. Keep prose
  paragraphs as triple-quoted strings on one physical source line.
- Resolve variants only from semantic result fields, never localized wording or
  record identity. Escape dynamic substitutions and keep the guidance
  presentation-only and identical in Guided and Classic views.
- Test stable meaning, routing, bilingual structure, placeholders, escaping,
  placement and exact visible UI names. Avoid pinning incidental wording unless
  that wording is itself a user-interface contract.

- Use descriptive, self-explanatory names for variables, functions, methods,
  classes, constants, modules, and DataFrame columns.
- Prefer complete words over abbreviations. Domain-standard abbreviations such
  as `WSPR`, `TX`, `RX`, `SNR`, `UTC`, `SQL`, `UI`, and `DB` are acceptable when
  their meaning is unambiguous.
- Use established WSPRadar terminology consistently. Do not introduce synonyms
  for visible concepts such as Target, Reference, Joint, Opportunity, Decode Rate,
  Decode Outcomes or Target-Active Gate. Internal or compatibility terms such as
  `success`, Elsewhere and Other Signals may remain in code or a supported external
  contract where required; they must not appear in narrative manual prose merely to
  explain how the implementation stores a scientific category. If an exact name is
  part of a supported configuration, URL, export or data contract, document it once
  in Chapter 8 or a dedicated data dictionary and label it explicitly as a
  machine-readable contract value.
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

### Replacement and Dead-Code Cleanup

Treat removal of superseded implementation as part of completing a replacement,
not as optional follow-up work.

- Trace the old and new call paths before editing. When behavior is replaced or
  removed, delete every old runtime branch that no active producer, caller,
  dispatcher, or supported compatibility contract can reach.
- Remove private helpers, methods, classes, imports, constants, configuration
  entries, localization keys, compatibility shims, comments, and documentation
  that exist only for the retired behavior. Do not keep an obsolete
  implementation merely because a regression test imports or exercises it
  directly.
- Delete tests and fixtures that assert only retired behavior. Replace them with
  coverage of the active contract and retain negative assertions when they
  prevent obsolete UI, exports, terminology, or schemas from returning.
- Audit shared and mode-specific paths—including visible Performance and Benchmark paths, canonical `performance` contract paths, RX, TX,
  Guided, Classic, preview, export, and both languages—before declaring code
  unused. Preserve a compatibility path only when a current supported producer
  or consumer, persisted contract, or explicit migration requirement still
  needs it; document that reason in the code or handoff.
- Search for every removed symbol, key, filename, and distinctive phrase after
  cleanup. Classify any remaining occurrence as active, compatibility-required,
  or an intentional negative regression assertion. Unexplained remnants make
  the replacement incomplete.
- Run verification proportional to the affected contract after cleanup. The
  completion report must distinguish deleted dead artifacts from intentionally
  retained compatibility surfaces and identify anything that could not be
  proven reachable or unreachable.

## Git and GitHub Publishing

- Never push directly to `main`, `master`, or another default branch unless the
  user explicitly authorizes that specific direct push in the current
  conversation.
- Do not infer direct-push authorization from a general request to commit,
  publish, submit, or push, or from any previous exception.
- Without that explicit authorization, use a separate feature branch and pull
  request, or stop and ask before publishing.

## Changelog Policy

- Keep `CHANGELOG_DAILY.md` in reverse chronological order, with the newest
  submission entry at the top.
- Record only major or significant changes that are useful at project-history
  level; omit minor styling, diagnostics and internal implementation details.
- Consolidate work from consecutive unsubmitted days into one coherent entry
  dated when that work is submitted to GitHub. Describe the final submitted
  outcome rather than retaining intermediate designs that were replaced before
  submission.
- Preserve older submitted entries unless a factual correction is required.

## Architectural Constraints

- The application is read-only with respect to wspr.live, WSPRDaemon WD2, and
  WSPRDaemon WD1. Do not add upstream mutation or credentials without an
  explicit design review.
- Every published analysis run must use exactly one database source across the
  selected active result's strict and legacy queries. On provider failover,
  discard the unpublished partial bundle and restart the active-result bundle
  from its first required request. Database identity must remain separate from
  cache medium and participate in query-cache identity and run/export
  provenance.
- Analysis and export gates are process-local. Their limits are safety controls,
  not globally distributed quotas. Provider request budgets and circuit state
  are likewise process-local and cannot enforce a shared-egress-IP quota across
  replicas.
- Query, derived-analysis, and session-artifact files have different lifecycles.
  Do not collapse their namespaces or cleanup policies.
- Session artifacts may remain in use after a Streamlit rerun. Cleanup must
  honor active leases and touches rather than deleting by age alone.
- Duplicate analysis admission is keyed by stable session ownership plus a
  scientific request fingerprint. Demo identity is part of the fingerprint so
  separate users can run the same demo while one session cannot enqueue the
  same work repeatedly. The UI submission token is separate from `run_mode` and
  must be cleared only by its owning terminal path or an explicit scientific
  request replacement.
- Upstream CSV and Parquet reads must retain connect/read deadlines, streamed
  byte ceilings, and structured errors.
- The base-map cache is shared and constructed under same-key coordination.
  Writes must remain unique-temporary-plus-atomic-replace operations.
- Export recipes reuse completed analysis artifacts; exports must not rerun the
  upstream scientific query.
- Documentation PDF generation is lazy, process-cached, and single-flight.
- Keep `core/`, `docs/`, `ui/`, and the runtime `ui/` subdirectories as regular
  Python packages with their committed `__init__.py` markers. Streamlit watches
  PEP 420 namespace-package directories recursively, so first-import bytecode
  writes inside those directories can trigger overlapping cold-start reruns.

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
- `docs/doc_en.py`, `docs/doc_de.py`, and README synchronization. Preserve all
  manual text and translations by default. Only a task that explicitly requests
  restructuring may remove passages classified under the relocation protocol;
  preserve all unique, correct and useful guidance and bilingual parity.
- Release scripts. `git-baseline-temp.ps1` resets the local `temp` branch to its
  remote baseline and is destructive to uncommitted work.
- Files under `tests/demo/`; they are historical exported evidence, not current
  generated regression fixtures.

## Compatibility

- Treat versioned JSON `.config` files, exported metadata, Parquet projections,
  DataFrame columns, and reproducibility packages as compatibility-sensitive
  interfaces. The current saved-config schema version 1 is explicitly
  pre-production and may be revised in place before the first production
  release; unpublished version-1 prototypes need not be migrated and may be
  rejected. After a schema has been published for production, every subsequent
  saved-config schema increase must retain an ordered migration from each
  preceding supported production version; do not guess at newer unsupported
  schemas.
- Saved configurations and built-in demo configurations must use the same
  standalone document and grouped runnable-settings structure. Serialize only fields applicable to the
  selected time and comparison branches; inactive hidden UI state is not part
  of the configuration contract.
- Changes to these interfaces require explicit migration or versioning decisions
  and corresponding regression tests.

## Handoff Requirements

- Summarize changed behavior, not merely changed files.
- State which checks were actually executed and their results.
- When full-suite or browser verification was not required, name the selected
  verification scope and why the narrower checks covered the changed contract.
- Explicitly identify unverified assumptions, remaining risks, and checks that
  could not be run.

## Definition of Done

1. The implementation follows the existing core/UI and context boundaries.
2. Scientific and user-visible behavior is unchanged unless the task explicitly
   requests a change. Document requested user-visible changes only when they
   meet the end-user relevance criteria below.
3. Tests cover changed behavior, including failure, ownership, concurrency, or
   persistence semantics where relevant.
4. The checks required by **Verification Scope and Proportionality** pass.
   `python -m pytest tests/regression -q` passes for full-verification work and
   final release or GitHub submission; focused incremental work records its
   narrower passing checks instead.
5. `git diff --check` passes. Changed Python scope compiles, and full repository
   compilation passes when full verification is required.
6. Streamlit starts successfully when entry-point, dependency, startup, or
   import-boundary behavior changes.
7. No unrelated files or user changes are reverted.
8. `CHANGELOG_DAILY.md` follows the Changelog Policy above and is updated for
   every major or significant submitted change.
9. Documentation and configuration are updated when contracts or commands change.
10. Generated user documentation is changed through its authoritative source,
   followed by the sync workflow, rather than by editing `README.md` directly.
11. Record-specific behavior is expressed through validated configuration rather
    than literal identifiers or per-record runtime branches. Adding a record
    that uses an existing capability requires no runtime-code change.
12. Any check that could not be run is stated explicitly in the handoff.
13. Every user-visible terminology change has completed the Terminology Change
    Protocol, including cross-surface search, bilingual parity, active-route
    verification, and an explicit distinction between presentation wording and
    retained canonical or compatibility terminology.

## Documentation Maintenance

- Treat `AGENTS.md`, `AGENT_README.md`, and `docs/architecture.md` as living
  project documentation.
- When a change introduces or alters architecture, repository structure,
  development commands, coding conventions, authoritative files, invariants,
  or operational constraints, update the corresponding documentation in the
  same change and make those changes explicit to the user once you are done
- Do not update these files for implementation details that do not affect their
  documented contracts.
- **Narrow the documentation-update trigger.** Update `docs/doc_en.py` and
  `docs/doc_de.py`, then regenerate `README.md` using
  `scripts/sync_readme_from_doc_en.py`, when a change alters workflow, controls,
  result meaning, scientific interpretation, output contracts, limitations or
  troubleshooting. Purely presentational changes do not require a manual update
  unless they materially affect accessibility or correct interpretation.
- Before completing a task, verify that factual claims and documented contracts
  still map to the implementation. This verification does not require visual or
  layout parity between the manual and the rendered UI.

### Manual Style, Audience and Structure

Use the layered rules below as the reference model for future end-user and
scientific-manual work. Existing manual prose is source material to audit, not
automatic style precedent; a passage does not belong merely because it is
technically correct or already present.

**Audience and technical depth are part-specific:**

- **Part 0 is the product preface and bounded positioning layer.** Write for
  prospective and first-time users who need to understand the measurement
  problem, why WSPRadar is distinctive, which questions it can answer, what its
  evidence can reveal and where its limits lie. Part 0 may use engaging,
  benefit-led and modestly promotional language, concrete station use cases and
  an inviting call to explore a demo. It must remain technically honest and
  must not use unsupported `first`, `only`, calibrated-measurement, superiority
  or causation claims. It is not an operating guide.
- **Part I is operator-first.** Write for first-time WSPR users and experienced
  experimenters who need to prepare, run and interpret an analysis.
- **Part II is an exact operating reference.** Document the controls, defaults,
  ranges, applicability, persistence and diagnosis that affect operator action.
  Do not reproduce cache, queue or rendering internals unless they explain an
  observable status or materially change troubleshooting.
- **Part III is a scientific methods reference.** Write for scientifically
  critical radio amateurs, HamSCI contributors and reviewers. Formal notation,
  equations and detailed treatment of analysis targets, observation and
  comparison units, constructed evidence units, derived quantities, descriptive
  summaries, conditioning, missingness, weighting, dependence, transformations,
  uncertainty limits, provenance and reproducibility are appropriate. Part III
  must nevertheless remain accessible to a technically minded radio amateur:
  introduce the radio or analysis meaning before the formal definition, define
  symbols and denominators, explain formulas again in plain language and add a
  small numerical example when it materially improves understanding. Prefer
  precise plain language over unnecessary statistical jargon. Part III may be
  longer and denser than the operator sections when the added detail is
  scientifically material; `lean` means removing non-scientific clutter, not
  suppressing methods needed for audit. Include software implementation detail
  only when it changes scientific semantics, provenance or reproducibility; keep
  repository architecture and cosmetic rendering behavior elsewhere.
- **Part IV is a practical technical supplement.** Retain platform-, device- and
  calibration-specific procedures that would interrupt the main operator path.
- Begin with why WSPRadar is useful and distinctive. Part 0 should create
  interest by making the real station-measurement problem recognizable, showing
  how WSPR and WSPRadar address it, and describing the practical value of an
  auditable evidence path. Follow with the minimum WSPR background, the
  questions WSPRadar can address, what one run produces and an invitation to
  begin with a maintained demo. Explain genuine strengths without unsupported
  `first`, `only`, calibrated-measurement, superiority or causation claims.
- Build understanding progressively. Introduce terms such as Target, Reference,
  peer, Decode Rate, Decode Outcomes, and Delta SNR in plain operator language
  before relying on them. Do not front-load a dense glossary.
- Preserve the manual's authoritative order: Part 0 Preface; Part I Operator
  Guide with **Choose and Prepare the Analysis**, **Run and Interpret Your
  Analysis**, and **Strengthen and Communicate Your Result**; Part II Controls
  and Troubleshooting; Part III Scientific Foundations, Methods and Claims with
  Literature, Prior Art and Positioning, Scientific Methods, and
  Evidence-Matched Claims and Reproducibility; References; Part IV Practical
  Supplements; then License. Within Part 0 use this sequence: **Why WSPRadar?**;
  **WSPR in 2 Minutes**; **What WSPRadar can show**, including the conceptual
  question-to-analysis overview; **What one run produces**; and **Your first
  useful run**.
- Organize Part I around the operator's analysis question rather than around a
  generic inventory of screens. Chapter 2 uses the four analysis families **RX
  Performance**, **TX Performance**, **RX Benchmark**, and **TX Benchmark**.
  RX Benchmark distinguishes Hardware A/B, Reference Station / Buddy Test,
  Local Median Neighborhood and Local Best Station. TX Benchmark distinguishes
  simultaneous Hardware A/B, sequential Hardware A/B, Reference Station / Buddy
  Test, Local Median Neighborhood and Local Best Station.
- Use the common evidence path **Map → Segment Inspector →
  Performance/Benchmark Evidence → Temporal Evidence → Station Insights →
  Selected Station Evidence → Drill-Down**. Explain the path once at overview
  level, then interpret it in the relevant RX/TX and Reference context.
- Give direction- or design-specific playbooks a consistent interpretive shape:
  question answered; minimum valid setup; what WSPRadar evaluates or compares;
  how to read the evidence path; common interpretation patterns; strongest
  relevant boundary; how to strengthen or confirm the result; and an
  evidence-matched conclusion. These elements need not become mechanical
  headings when a shorter treatment is clearer.
- Share common Benchmark mechanics once at RX- or TX-family level. Design
  subsections should focus on what the Reference represents, which setup
  controls matter, which interpretations become stronger or weaker, and which
  confirmation method is most useful. Do not repeat the complete UI or
  scientific explanation in every Reference subsection.
- Worked examples are optional and are not required in the core Part I
  structure. Prefer maintained demo-specific interpretation in a later,
  explicitly scoped iteration over generic hypothetical examples embedded in
  every manual revision.
- Keep the structure as MECE as the subject permits. Give experiment selection,
  result interpretation, configuration, scientific formulas and inference
  limits one authoritative home each. When a complex multi-stage method requires
  a documented ownership split, follow the Authoritative Ownership rules below.
  Cross-reference instead of repeating full explanations.
- Layer practical and scientific depth. State what a result means for the
  operator first, then place exact matching, denominators, evidence units,
  aggregation, and formulas in Chapter 7, Scientific Methods.
- Make Part 0 explain why the product is worth exploring, what problems it can
  address, what evidence it produces and why that evidence is different from a
  spot count or one-off report. Make the Part I playbooks teach how to prepare,
  recognize and interpret a valid result. Neither section should merely list
  buttons.
- Keep the tone technically rigorous but practical and inviting. Each paragraph
  should help answer an operator's likely `so what?`; avoid dry implementation
  narration that does not change setup, interpretation or claim language.
- **Apply a product-relevance test to Part 0.** Include a detail when it helps a
  prospective user understand the station-measurement problem, WSPRadar's value
  and distinctiveness, the questions it can answer, the evidence one run
  produces, a compelling real-world use case or an important credibility
  boundary. Part 0 need not instruct an operator action, but every paragraph
  should strengthen understanding, interest or trust.
- **Apply the operator-relevance test to Parts I-II.** Include a detail only if
  it changes what the operator should do, how evidence should be interpreted,
  what real-world consequence it has, what claim is supported, or how a problem
  is diagnosed. When evidence supports practical value, explain it
  constructively without overstating the supported claim.
- **Apply a scientific-relevance and reproducibility test to Part III.** Include
  a detail when it is needed to define or audit the data, analysis target,
  observation or comparison unit, constructed evidence unit, derived quantity,
  descriptive summary, conditioning, transformation, uncertainty boundary,
  validation evidence, provenance or reproducibility contract. Technical
  accuracy alone still does not justify UI-layout narration, cache mechanics or
  implementation trivia that has no scientific consequence.
- **Audit every code-styled or implementation-facing name in the manuals.**
  Classify it as visible UI terminology, formal mathematical notation, a
  scientifically necessary upstream source field, a supported public contract
  value, or an internal implementation name. Retain public contract values only in
  Chapter 8 or a dedicated data dictionary. Remove private enum values, DataFrame
  columns, helper names, cache keys, state keys, temporary state names and internal
  classifications when their scientific meaning can be stated in domain language.
- **The end-user manual is not a UI specification, rendering contract,
  regression-test oracle, code map or catalogue of every visible label.** Do not
  inventory titles, panel order, axis labels, legend placement, spacing, empty-state
  geometry or other presentation details solely because they exist. Do not expose
  private enum values, internal classifications, DataFrame columns, helper names,
  cache keys, state keys or temporary state names in narrative manual sections.
  Name a figure or control exactly when the reader needs that name to locate,
  operate or correctly interpret it.
- **Keep automatic interval-boundary semantics out of the end-user manual.**
  The half-open query/window convention is a deterministic internal rule, not
  an operator choice or reporting requirement. Do not mention it in
  `docs/doc_en.py`, `docs/doc_de.py` or generated `README.md`; retain exact
  boundary semantics only in code, tests and engineering architecture where
  they protect implementation correctness.
- **Exclude self-evident presentation narration.** Do not document typography,
  font style, legend placement, panel placement, title prefixes, spacing,
  axis-label styling, or the absence of unrelated statistics or annotations.
  The rendered UI is authoritative for its appearance and does not need an
  explanation.
- **Treat implementation and tests as fact-checking sources, not documentation
  checklists.** They establish whether a claim is accurate; they do not establish
  that every implementation or rendering fact belongs in the manual. Translate
  scientific behavior into domain language instead of preserving the names of
  internal storage categories.
- **Keep scientific mechanics in Chapter 7.** Observation and comparison units,
  notation, analysis targets, evidence construction, derived quantities,
  descriptive summaries, eligibility, conditioning, missingness, censoring,
  normalization, binning, weighting, aggregation, dependence, analysis
  transformations and scientifically material edge cases belong once in
  Scientific Methods. Describe classifications by their scientific meaning rather
  than by private enum values or internal column names. Exact upstream source fields
  may be named only when they materially define reproducible source selection. Part
  II owns exact control labels, defaults, ranges, applicability, configuration
  behavior and diagnosis. Part I should state the operator consequence and link to
  the authoritative method only where omission would cause a materially wrong
  operation or interpretation.
- Distinguish observations, assumptions, heuristics, and supported inferences.
  Explain conditional denominators and asymmetries, and state explicitly which
  claims the evidence does and does not support.
- Define each formula once in its scientific home, ensure it renders in both the
  Web UI and generated PDF, and link to it from practical sections when needed.
- In Chapter 7, use the hierarchy **reported observations → constructed
  evidence units → derived quantities → descriptive summaries → bounded
  interpretation**. Distinguish the selected **analysis target** from the
  retained evidence and from the descriptive summary calculated from that
  evidence. The selected design defines the analysis target—formally, the
  *estimand*—through its eligibility, conditioning and weighting rules. WSPRadar's
  rates, medians, shares, reach values and temporal or geographic aggregates are
  exact descriptive summaries of the retained evidence under those documented
  rules; they are not automatically calibrated estimates of a wider population,
  future behavior or physical station parameter. Use *estimator* only when the
  text explicitly discusses generalization beyond the retained evidence and
  identifies the sampling, dependence or inferential model supporting that
  generalization.
- Present each non-trivial Chapter 7 method in accessible layers: first state the
  radio or analysis question; then define the observation or comparison unit,
  eligibility, denominator, grouping and weighting; then give the formula;
  follow it with a plain-language explanation of what the calculation does; add
  a small numerical example when useful; and finish with the principal
  interpretation boundary. Define every symbol, index, unit and denominator so a
  technically minded amateur does not have to infer the radio meaning from the
  notation alone.
- State conditioning and selection explicitly: Target-active eligibility,
  independent-activity qualification, joint-decode selection, successful-decode
  censoring, one-sided evidence and any missing-not-at-random consequence.
- State dependence explicitly. Repeated cycles, stations sharing propagation,
  geographic clustering and temporal autocorrelation mean that row count is not
  an independent sample size. Do not imply confidence intervals, significance or
  precision that WSPRadar does not calculate.
- Keep validation evidence auditable. Any empirical audit statistic must name or
  link its datasets, date, method and software/revision context, or be clearly
  labelled as a dated implementation check rather than a timeless method rule.
- Separate analysis transformations from display-only transformations. Document
  a presentation transform only when it changes how a scientific value must be
  read; state explicitly that retained scientific values, evidence units,
  groupings and descriptive summaries remain unchanged.
- Chapter 8 should distinguish descriptive, comparative, component-attribution,
  causal and inferential claims, and should specify the provenance and external
  experiment records needed for reproduction. It is also the authoritative home for
  exact names that form supported machine-readable configuration, URL, export or
  data contracts; identify them explicitly as contract values and keep them out of
  narrative method explanations.
- When the manual names a UI label, default, result unit, export field or
  behavior, keep its name and meaning current. This is an accuracy requirement,
  not a requirement to inventory every visible interface detail. Challenge
  documentation claims against implementation and regression tests; report
  disagreements rather than changing runtime behavior to fit prose.
- Keep literature, prior art and positioning in Chapter 6. Keep platform-,
  transmitter-, accessory- and procedure-specific guidance in the Part IV
  appendices. Place References after Chapter 8 and cite every retained source in
  order of first use.
- Render every source citation as a compact linked label in the form `[Ref-n]`,
  assign numbers globally in order of first source use, and reuse the same
  number for later citations of that source. Do not hyperlink author names,
  publication titles, or explanatory phrases as source citations; reserve
  descriptive links for structural navigation such as sections and appendices.
- **Clarify the preservation rule.** An ordinary documentation task must
  preserve all existing text. During an explicitly requested restructuring,
  preserve unique, correct and useful user guidance. `Useful` means that the
  content changes operator action, interpretation, diagnosis or supported
  claims. In Part III, useful content also includes material needed to define or
  audit the scientific data, analysis target, evidence construction, derived
  quantities, descriptive summaries, conditioning, uncertainty or
  reproducibility contract. Technical accuracy alone does not make a sentence
  useful, and removing duplicated material is not content loss. An explicitly
  requested lean-manual audit authorizes removal of duplicated, obsolete,
  implementation-only, self-evident presentation or scientifically unsupported
  passages after useful guidance has been retained or relocated. Do not silently
  lose genuinely useful guidance.

### Manual Content Ownership and Relocation

Place manual information in the layer where the intended reader needs it and
keep each rule's complete explanation in one authoritative home, subject to the
explicit
multi-stage-method ownership rule below:

- **Part 0 — Preface:** persuasive but bounded product motivation; the minimum
  WSPR background; a conceptual question-to-Performance/Benchmark overview;
  the evidence package produced by one run; and a gentle invitation to begin
  with a maintained demo. It may explain the common evidence path at a high
  level because that auditability is part of WSPRadar's value proposition, but
  it must not become a walkthrough. Exclude exact control labels, selectors,
  parameter choices, defaults, ranges, button sequences, saved-state behavior,
  provider topology and cache behavior; those belong in Parts I-II or the
  scientific and architecture documentation.
- **Part I, Chapter 1 — Choose and Prepare the Analysis:** common experiment
  foundation, the decision between RX/TX and Performance/Benchmark, Reference
  selection, and a concise overview of the common evidence path. Do not repeat
  exact control ranges, complete algorithms or device-specific procedures.
- **Part I, Chapter 2 — Run and Interpret Your Analysis:** direction-, result-
  and design-specific operator playbooks for RX Performance, TX Performance, RX
  Benchmark and TX Benchmark. Explain what the visible evidence means in that
  experiment context, how the evidence-path views should be combined, common
  interpretation patterns, the strongest design-specific boundary and how to
  strengthen the result. Include only the minimum setup reminders needed to
  avoid an invalid experiment; exact controls remain in Part II and exact
  scientific mechanics remain in Chapter 7.
- **Part I, Chapter 3 — Strengthen and Communicate Your Result:** breadth,
  internal consistency, experimental repeatability, repetition and controls,
  evidence-matched conclusions, and preservation of the run and its physical
  context.
- **Part II, Chapter 4 — Controls and Configuration:** exact UI labels,
  defaults, ranges, applicability, scientific consequence, configuration
  behavior and saved-state behavior. Prefer compact control tables. Omit
  internal state-machine, cache and queue details that do not alter operator
  action or reproducibility.
- **Part II, Chapter 5 — Troubleshooting and Data Quality:** run-definition,
  symptom, callsign, locator, historical fallback, Target-Active Gate and
  upstream-data diagnosis. Explain audit/provenance statuses at the level needed
  to diagnose a run; leave provider-selection and cache-lifecycle mechanics to
  architecture documentation.
- **Part III, Chapter 6 — Literature, Prior Art and Positioning:** the scope and
  evidence class of the review; scientific lineage; prior art; source-specific
  boundaries; and bounded novelty claims. State explicitly when the review is a
  focused methodological review rather than a systematic or exhaustive search.
- **Part III, Chapter 7 — Scientific Methods:** scientific scope and notation;
  reported observations and constructed evidence units; time model; identity,
  matching and consolidation; eligibility, conditioning and missingness;
  Performance and Benchmark analysis targets; power normalization and
  correction; derived Delta SNR and Decode Outcomes; hierarchical aggregation
  and weighting; geographic, temporal and selected-path descriptive summaries;
  scientifically material display transforms; dependence, uncertainty
  limitations and dated validation scope. Present the practical radio meaning
  before formal notation, explain every formula again in accessible prose and
  describe category semantics without exposing private implementation names.
- **Part III, Chapter 8 — Evidence-Matched Claims and Reproducibility:** claim
  classes, supported inference, interpretation limits, reporting and provenance
  requirements, machine-readable configuration/URL/export/data contracts and
  disclaimer. Describe export artifacts by scientific content, scope and stable
  contract fields; label exact identifiers as machine-readable contract values and
  do not turn the export section into an inventory of figure titles, axis labels or
  browser layout.
- **References:** the consolidated source list follows Chapter 8 and precedes
  Part IV.
- **Part IV — Practical Supplements:** Appendix A owns parallel WSJT-X setup;
  Appendix B owns sequential TX A/B scheduling, switching and device examples;
  Appendix C owns Reference SNR Calibration. The License follows Appendix C.

Use this timing test when placement is unclear:

- needed to choose the question or prepare the common experiment -> Chapter 1;
- needed to execute or interpret one specific RX/TX Performance or Benchmark
  analysis -> Chapter 2;
- needed when repeating, reporting or preserving the experiment -> Chapter 3;
- needed to operate an exact control or diagnose behavior -> Part II;
- needed to establish scientific lineage, prior art or positioning -> Chapter 6;
- needed to audit data construction, an observation or comparison unit,
  analysis target, derived quantity, descriptive summary, conditioning rule,
  transformation, dependence or uncertainty boundary -> Chapter 7;
- needed to classify, bound, report or reproduce a claim -> Chapter 8;
- needed to provide consolidated source metadata -> References;
- needed only for a particular device, platform or calibration procedure ->
  Part IV.

#### Authoritative ownership plus point-of-action reminders

Give each rule, formula or procedure one authoritative explanation. A complex
multi-stage method may be split across sections when each section owns a
distinct scientific role and forcing the complete method into one section would
make it harder to audit. In that case, state the split explicitly and
cross-reference every section needed to reconstruct the method. A concise
warning or summary may appear at the point of action when omitting it could
cause an invalid experiment, incorrect configuration or materially wrong
interpretation. The reminder must link to the authoritative explanation and
must not reproduce the complete mechanics.

Examples:

- define the power-normalization equation in Section 7.5; retain `report actual power` as a warning in the TX A/B playbook;
- for sequential TX A/B, treat Sections 7.1 and 7.7 as jointly necessary:
  Section 7.1 owns the time model and window eligibility, while Section 7.7
  presents the end-to-end pair construction, micro-medians, one-sided outcomes
  and aggregation sequence. Section 7.6 owns the interpretation of paired
  evidence and Decode Outcomes, and Section 7.3 may state the
  Target/Reference-swap consequence of the tie rule. Cross-reference Sections
  7.1 and 7.7 together from practical guidance; retain `pairing is automatic
  and deterministic` in the playbook;
- define exact schedule choices in Section 4.3; retain `enter each path's actual recurrence and UTC phase` in the playbook;
- keep the Ultimate3S and QMX schedule examples in Appendix B, Sections B.3 and
  B.4, and link to them from the playbook.

#### Relocation protocol

A restructuring is substantial when it relocates content across multiple
sections or parts, or removes or merges passages. An explicitly requested
lean-manual audit is a substantial restructuring and may remove duplicated,
obsolete, implementation-only or self-evident presentation passages after
useful operator or scientific guidance has been retained or relocated.

The relocation-ledger requirement is prospective. A manually integrated
baseline that the user explicitly accepts as grandfathered does not require a
reconstructed ledger; apply the ledger requirement to later substantial
restructures. When the user explicitly requests an English-only review draft,
that draft may precede German parity and README synchronization. It is not a
completed repository integration, must not be published as the authoritative
manual, and does not require a committed relocation ledger until the structure
is accepted for integration.

1. Identify the authoritative destination before removing source text.
2. Classify the source passage as unique useful guidance, duplicated explanation, obsolete material, implementation-only detail or unsupported claim.
3. Add or improve the destination before removing unique guidance from the source.
4. Retain a concise reminder and cross-reference at the original decision point when needed.
5. Create and commit a task-specific relocation ledger at
   `docs/relocation-ledgers/<topic>.md`, using a concise descriptive topic name.
6. Record verbatim any original passage not retained anywhere, together with its section, disposition and reason.
7. Update the Table of Contents, anchors, internal cross-references, known
   compatibility anchors, references and both language versions in the same
   completed integration.
8. Verify that no useful guidance remains only in an obsolete or removed location.

#### Exploratory and confirmatory guidance

When documentation describes evidence strengthening, distinguish exploratory use from confirmatory repetition. An initial run may identify a possible pattern. Before a confirmatory run, instruct the operator to fix the relevant direction, band, benchmark, filters, thresholds, schedule and primary evaluation scope. Alternative radii, time windows or scopes should be reported as sensitivity analyses rather than selected only because they are favorable.

#### Consistency and repeatability

Do not use `stable` ambiguously. Distinguish:

- **internal consistency:** agreement among the station-balanced,
  observation-level, geographic and temporal evidence views within one run;
- **experimental repeatability:** persistence of the observed pattern in a new controlled run or operating window.

Internal consistency within one run does not by itself establish future
repeatability, independence, calibration or statistical significance.

#### English and German structural parity

English and German manuals must retain equivalent section ownership, claims,
warnings, formulas, references and cross-links in every completed integration.
German should be a native technical adaptation using established amateur-radio
terminology, not a mechanically literal translation. In German Part III,
prefer precise but readable terms such as **Analyseziel**, **Beobachtung**,
**gebildete Evidenzeinheit**, **beobachtete gepaarte Differenz**, **deskriptive
Kennzahl** and **Zusammenfassungsgröße**. Avoid **Schätzer**, **Schätzfunktion**
and **Schätzwert** unless the passage genuinely discusses inference to a wider
population under an explicit statistical model. Preserve every formula and
scientific distinction, but explain it in natural amateur-radio and HamSCI
German that remains accessible to a technically minded operator. A relocation
is incomplete until both languages have the same authoritative content home.

An English-only restructuring may be supplied as an explicitly labelled review
draft when the user requests staged evaluation of the new structure. Do not
regenerate `README.md`, publish the draft as authoritative or treat the
restructuring as complete until the German manual has been adapted and parity,
links, rendering and full integration checks have passed.

#### Documentation restructuring checks

For a substantial manual restructuring, verify:

- every Table of Contents link resolves to exactly one existing anchor;
- retained compatibility anchors do not create duplicate headings;
- every defined term is introduced before it is relied upon;
- formulas have one authoritative home; complex multi-stage methods follow the
  explicitly documented ownership split and cross-links;
- Part 0 is engaging, benefit-led and technically bounded; follows the approved
  sequence from motivation through WSPR background, capabilities/questions,
  run outputs and first demo; and contains no control, selector, parameter or
  button walkthrough;
- Part II remains an operating reference and does not become an internal state,
  cache, queue or persistence-structure specification;
- Part III clearly distinguishes reported observations, constructed evidence
  units, derived quantities, descriptive summaries and bounded interpretation;
  defines analysis targets, observation and comparison units, conditioning,
  missingness, weighting and dependence sufficiently for scientific audit; and
  explains formal notation and formulas in language accessible to a technically
  minded radio amateur;
- empirical validation statistics carry reproducible provenance, are isolated
  as dated validation evidence, or are removed from the normative method;
- display-only transformations are separated from scientific calculations and
  cosmetic rendering behavior is excluded;
- Chapter 8 distinguishes descriptive, comparative, component-attribution,
  causal and inferential claims; export documentation describes stable artifacts
  and provenance rather than incidental figure layout; and every exact identifier
  retained in the manuals is either a visible term, formal notation, a scientifically
  necessary upstream field or an explicitly labelled public contract value;
- no device-specific procedure interrupts the main operator journey;
- no useful original guidance was silently dropped;
- source references remain globally numbered in order of first use;
- Part I follows the approved analysis-centred playbook structure and does
  not revert to a generic screen inventory;
- self-evident UI narration and implementation-only rendering detail have not
  been retained merely for technical completeness;
- English and German structures and claim boundaries remain equivalent for a
  completed integration; an explicitly requested English-only review draft is
  identified as incomplete;
- documentation tests assert required meaning and structure rather than obsolete
  incidental prose where practical;
- README synchronization and web/PDF rendering are completed after authoritative
  bilingual integration;
- the authoritative manuals import and compile, internal links resolve, and the
  complete regression suite plus any applicable documentation-specific checks
  pass.
