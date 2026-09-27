# WSPRadar verification history

This file preserves dated verification and evidence-retention records moved from
`AGENT_README.md` on 2026-09-27. The records below retain their original wording,
including historical failure counts, environment details, paths and claims about
what was pending at the time. They are evidence for the stated run, not a current
pass/fail summary or instructions to repeat obsolete commands.

Current setup, operating commands and fixture availability are maintained in the
[repository guide](../AGENT_README.md). The
[script index](../scripts/README.md) identifies current routine and specialist
maintenance commands.

## Reading historical paths and status

- Historical `scripts/build_*.py`, `scripts/verify_*.py`,
  `scripts/demo_pdf_header.py`, `scripts/demo_pdf_footer.py` and
  `scripts/sync_reference_figure_pdfs.py` paths now reside under
  `scripts/internal/` with unchanged filenames. Recorded commands below are
  preserved as executed; use the current path when repeating a check.
- `scripts/sync_readme_from_doc_en.py`, regression launchers and Git workflow
  commands remain directly under `scripts/`.
- Statements that the prepared-export fixture was absent or skipped describe
  their historical runs. The committed
  `tests/regression/fixtures/milazzo_fig6_rx_prepared_export_v1/` now supplies the
  mandatory availability check and prepared-package integrity coverage.
- Historical `output/`, `tmp/`, `.test/` and worktree paths identify their original
  run locations. They are not instructions to recreate scratch folders, and
  their continued local availability is not implied. The scratch-archive record
  below identifies retained material; current scratch rules are in the guide.
- The 2026-07-11 source-compilation and whitespace record refers to the
  `python -m compileall -q app.py config core docs ui scripts tests tools` and
  `git diff --check` commands retained in the guide.

## Record index

- [Installation verification, 2026-07-11](#installation-2026-07-11)
- [Startup verification, 2026-07-11](#startup-2026-07-11)
- [Scratch evidence archive, 2026-09-27](#scratch-archive-2026-09-27)
- [Performance endpoint-participation verification, 2026-09-25](#performance-method-2026-09-25)
- [Milazzo human-review and provider verification, 2026-09-26](#milazzo-human-review-2026-09-26)
- [Runtime verification records, 2026-09-26 and 2026-09-27](#recent-runtime-checks-2026-09-26-27)
- [Regression and performance records, 2026-08-17 through 2026-09-25](#regression-and-performance-records-2026-08-17-to-09-25)
- [Source-compilation and whitespace record, 2026-07-11](#source-and-whitespace-2026-07-11)
- [Griffiths publication-reference verification, 2026-09-24](#griffiths-paper-reference-2026-09-24)
- [Zander reference verification, 2026-09-24](#zander-reference-2026-09-24)
- [Vanhamel calibration verification, 2026-09-24](#vanhamel-calibration-2026-09-24)
- [Vanhamel rotation verification, 2026-09-24](#vanhamel-rotation-2026-09-24)
- [Milazzo TX reference verification, 2026-09-24](#milazzo-tx-reference-2026-09-24)
- [Milazzo RX reference verification, 2026-09-24](#milazzo-rx-reference-2026-09-24)
- [Milazzo overlay artifact verification, 2026-09-24](#milazzo-overlay-artifact-2026-09-24)
- [Milazzo overlay regression integration, 2026-09-24](#milazzo-overlay-integration-2026-09-24)

<a id="installation-2026-07-11"></a>

## Installation verification, 2026-07-11

Verification status on 2026-07-11:

- All runtime and test dependency imports succeeded under Python 3.12.13.
- `python -m pip check` reported no broken requirements.
- A fresh virtual-environment installation was not performed because the local
  environment already contained the installed dependency set.
- The development-container image was inspected but not built during this review.

<a id="startup-2026-07-11"></a>

## Startup verification, 2026-07-11

The start command was verified headlessly on port 8503 on 2026-07-11. The
Streamlit health endpoint returned HTTP 200 with `ok`.

<a id="scratch-archive-2026-09-27"></a>

## Scratch evidence archive, 2026-09-27

The 2026-09-27 scratch cleanup removed the former root `tmp/` after inventory
and hash verification. It retained 418 files of historical source, derivation,
review and verification evidence in the local archive
`%USERPROFILE%\Documents\WSPRadar-Archives\WSPRadar-tmp-evidence-20260927T113845Z.zip`
(32,521,717 bytes; SHA-256
`9885133ed45b6cf14bc4f42a468aa7790ebb76ee751a40e3f9ab6c22d5c9f178`).
The ZIP contains a README and complete original-file inventory, preserving
the original `tmp/` relative paths. This includes the one-off
`build_griffiths_fig6_reference_20260924.py` derivation referenced in historical
Griffiths fixture provenance, the Zander live-window capture, the Milazzo review
packet and completed-run reports. It is an external historical archive, not a
runtime dependency or a newly approved scientific reference. Required current
fixtures and published PDFs remain in the repository.

<a id="performance-method-2026-09-25"></a>

## Performance endpoint-participation verification, 2026-09-25

Verification on 2026-09-25 under the existing Python 3.12.14 environment:
the canonical foreground runner completed with **3,179 passed, 1 skipped and
3 expected failures** in 445.71 seconds, exit 0. The absent generated export
fixture remains skipped; the three established Griffiths publication
disagreements remain expected failures. The existing Matplotlib
pending-deprecation warning is unchanged. Full repository compilation,
whitespace checking and the 87-module/five-chunk manifest validation passed.
All 303 protected review/reference files retained their starting SHA-256 hashes.
The initial full run exposed two stale Classic Input caption assertions; both
were deliberately updated to the revised method before the successful full run.

<a id="milazzo-human-review-2026-09-26"></a>

## Milazzo human-review and provider verification, 2026-09-26

Verification on 2026-09-26: the canonical complete foreground run reported
**3,221 passed, 1 skipped, 3 expected failures and 1 existing Matplotlib warning**
in **397.49 seconds**, with exit code 0. All 89 regression modules are assigned
exactly once across the five fallback chunks. Full Python compilation and
whitespace checks passed. All 303 protected original review/reference files
remain byte-identical. The new approval/reference is separate from those files.

The explicit live comparisons matched Performance's strict/fallback outputs
on **WD2 (0 / 5,541 rows)** and Benchmark's outputs on its original capture
provider, **wspr.live (0 / 1,610 rows)**. These are separately scoped provider
checks, not a four-query pass on a single provider. wspr.live rejected the
Performance query with HTTP 500 / `TOO_DEEP_SUBQUERIES` (maximum 2); WD2's
Benchmark output had the same identities, flags, SNRs and counts but different
peer coordinates and `best_ref_dist`. That cross-provider comparison correctly
failed. No scientific expectations or tolerances were changed to hide it.
Local diagnostic reports are retained under
`output/milazzo_clickhouse_2026-09-26_wd2`,
`output/milazzo_clickhouse_2026-09-26_benchmark_wspr_live` and
`output/milazzo_clickhouse_2026-09-26_performance_provider_diagnostic`.

<a id="recent-runtime-checks-2026-09-26-27"></a>

## Runtime verification records, 2026-09-26 and 2026-09-27

The Delta-SNR detector comparison-tolerance change on 2026-09-27 passed
**121 focused detector/export checks**, **219 documentation/marker/cache
checks**, and **2 generated-PDF tolerance-equation checks**. An initial setup
error in the two new PDF cases came from parameter IDs containing the complete
manual text; explicit language IDs fixed the test harness without changing
runtime behavior. The canonical complete foreground suite then passed with
**3,436 passed, 3 existing expected failures, no failures or skips, and
1 existing Matplotlib warning in 483.67 seconds** (exit 0). Full repository
Python compilation, exact README synchronization and CRLF-aware whitespace
checks passed. Tests cover both departure signs, acceptance/rejection at the
dB boundaries, ordinary float32/demo float64 normalization with Reference
correction, unrounded evidence, strict robust-z gates, low-threshold grouping,
fixed 1 dB grouping, detector/export agreement and v8 identity. Both generated
language PDFs retain the tolerance symbol and equations. No live provider
requests or browser walkthrough were required for this numerical policy change.

The manuals were updated in parallel against the approved comparison-only
policy. Source SHA-256 values were
`b0ce1404626a7ed298c28673782025bd1508807fbe3692452e2a4a2eedbcdf31`
for `docs/doc_en.py` and
`c29d088bb794a1b6d259b5e46048368eb644d4acbefc986083915d0a436d0aeb`
for `docs/doc_de.py`. Semantic review covered the Section 4.6 control reminder
and Section 7.11 definitions, equations and grouping limits, with no material
language divergence. Existing content outside the necessary integrations was
preserved; README and PDF formula mappings were synchronized afterward.

The Target-QTH map-centering and Local Median footer correction on 2026-09-27
passed all **67 focused map lifecycle tests**, with the existing Matplotlib
warning. Coverage exercises real Cartopy projection and disk-cache construction
for four-character grids and distinct six-character subsquares, same-center
reuse, RX/TX and EN/DE footer rendering in both themes, and prepared-export
invalidation. Production dark/light maps centered on `IO91AA` were rendered and
visually inspected; both used the same full-QTH origin, retained the configured
neighborhood radius and omitted the maximum Reference-distance annotation.
The task-specific diagnostic images and cache were removed after inspection.
The canonical complete foreground suite then passed with **3,401 passed,
3 existing expected failures, no failures or skips, and 1 existing Matplotlib
warning in 433.07 seconds** (exit 0). Full repository Python compilation,
manual/README synchronization and CRLF-aware whitespace checks passed. No live
provider request or browser walkthrough was required for these renderer changes.

The persistent demo-query cache change on 2026-09-27 was verified with the
complete foreground runner: **3,359 passed, 3 expected failures, no failures or
skips, and 1 existing Matplotlib warning in 454.51 seconds** (exit 0). The prior
focused run passed all 333 checks in 41.14 seconds. Coverage includes old and
future-dated demo files, decades-later RAM/disk reuse, actual fresh-interpreter
disk reuse with network access blocked, query/format invalidation, missing and
corrupt cache recovery, strict/legacy admission, finite overflow markers and
cleanup that preserves published demo files while removing abandoned writes.
Full Python compilation, bilingual manual/README synchronization and CRLF-aware
patch validation (`git -c core.safecrlf=false -c core.whitespace=cr-at-eol diff
--check`) passed. The CRLF setting preserves an already modified frozen Zander
manifest. No live provider requests, startup preloading or deployment checks were
performed for this change; the existing three Griffiths scientific comparison
expected failures remain unchanged.

The demo regression repairs on 2026-09-27 were verified with the complete
foreground runner: **3,346 passed, 3 expected failures, no failures or skips,
and 1 existing Matplotlib warning in 493.15 seconds** (exit 0). The installed
seven-demo catalogue and independent loader fixture pass; the retired scheduled
TX A/B demo test was removed. Zander's installed 09:45-10:30 UTC window preserves
all 564 SQL groups, 457 retained groups and 166 Joint Spots, with exact agreement
against the original 09:30-10:30 frozen replay and independent histogram.
Its description and PDF header now agree with the installed window. The new
Milazzo prepared-export snapshot exercises the formerly skipped package check
with real production tables, figures and Parquet; explicit offline provenance
and the actual `legacy_no_code` selection are checked. The three strict
Griffiths expected failures remain the documented paper-comparison limits.
Full Python compilation, generated README synchronization, all seven published
PDF-copy checks and fixture source hashes passed. CRLF-aware patch validation
(`git -c core.whitespace=cr-at-eol diff --check`) passed while preserving frozen
manifest line endings. No live provider query was used for these repairs.

The Milazzo Figure 6 RX demo change on 2026-09-27 was verified with the complete
foreground runner: **3,335 passed, 1 skipped, 3 expected failures, 1 existing
Matplotlib warning and 9 failed in 462.07 seconds** (exit 1). All 84
Milazzo/header checks passed, including the installed RX configuration replay,
separate DO34IR/DO34 Joint populations and preserved TX publication-window
replay. Eight failures are stale demo filenames/IDs in `test_config_package.py`;
the ninth is the already different installed Zander window (09:45-10:30 UTC)
versus its frozen fixture (09:30-10:30 UTC). The failing test files, Zander
configuration and frozen Zander configuration were confirmed unchanged from
HEAD. Full Python compilation, patch whitespace, README synchronization,
90-module/five-chunk manifest validation and all seven published PDF-copy
checks passed. The installed Milazzo demo changed direction and explanatory
metadata only; 89 scientific/reference/PDF files remained byte-identical.
Only three fixture README files and their manifest entries were updated. No live
provider query or interactive browser session was needed for this fixture-backed
configuration change.

The correction-aware temporal-density change on 2026-09-26 was verified with
the complete foreground runner: **3,222 passed, 1 skipped, 1 existing warning,
8 failed and 85 setup errors in 488.11 seconds** (exit 1). All eight failures
are in `test_config_package.py` and depend on already renamed or removed demo
files/IDs. The 85 setup errors are in the Griffiths and Milazzo publication
fixtures: five PNGs were already deleted while their manifests still require
them. These unrelated checkout changes were retained. No new correction-grid
regression failed. The final targeted rerun passed **50 selected checks** after
updating older test mocks to include explicit numerical correction metadata.
Full compilation, whitespace, README synchronization, independent Vanhamel
density-only oracle reproduction, final PDF visual review and all seven
published reference-PDF synchronization checks passed. The frozen Vanhamel
production replay preserves 1,441 pairs, the 3 dB step and scientific statistics;
all 476 density counts/masks are unchanged and corrected cell edges equal
zero-correction edges minus 1.6 dB. Its first occupied span is -4.1 to +1.9 dB.
This verifies the local frozen-data and rendering paths; no live provider or
full interactive browser session was run for this change.
Final English/German documentation and PDF/rendering checks passed **108 tests
in 11.55 seconds** after the last terminology-precision adjustment.

<a id="regression-and-performance-records-2026-08-17-to-09-25"></a>

## Regression and performance records, 2026-08-17 through 2026-09-25

Focused verification on 2026-09-24 added the mandatory G3ZIL/G4HZX temporal
reference fixture. The new module and the existing prepared-export integrity,
segment temporal evidence, evidence-statistics and runner tests reported
**57 passed, 1 skipped, 1 existing warning in 28.07 seconds**. After making the
axis assertions explicitly UTC, the new module separately reported
**8 passed, 1 existing warning in 9.61 seconds**, with 2.82 seconds for its
shared numerical preparation. The skip still belongs to the absent
prepared-export package; the new scientific reference never skips. Four
temporary in-memory faults were rejected: reversed Delta SNR, a three-hour
timestamp shift, means substituted for bin medians, and an omitted geographic
filter. The 82-module chunk manifest, changed-test compilation and whitespace
checks passed. This was a test/data and engineering-documentation addition;
application runtime code was unchanged, so a full-suite or browser run was not
required for this focused work.

The companion Figure 6 fixture was integrated later on 2026-09-24 using the same
reference module. Both publication cases and the directly related modules
reported **69 passed, 1 skipped, 1 existing warning in 21.75 seconds**. Eight
in-memory erroneous results/configuration choices were rejected by the actual
reference assertion helpers: means, station-hour or date-hour medians used in
place of pooled medians; shifted UTC hours or density cells; reversed Delta SNR;
an extended final-hour boundary; and an omitted geographic cutoff. These checks
did not mutate application source or frozen expectations. The Figure 3 fixture
remained unchanged, and the same 82-module manifest registration applies.
Changed-test compilation and whitespace checks passed. This focused addition
changed only tests, fixture data and engineering documentation; full-suite,
browser and database-SQL checks were not performed.

The subsequent external Figure 6 source-image addition on 2026-09-24 passed
the same focused module set with **82 passed, 1 skipped, 1 existing warning in
25.03 seconds**. All 33 Griffiths reference tests are mandatory, including nine
paper-density sensitivity cases, qualitative density ordering and three
independently digitized isolated-point witnesses. Expected source positions
and tolerances remained fixed after their first comparisons. Five in-memory
faults were rejected: reversed Delta SNR, constant +5 dB differences, a +4 dB
offset, a six-hour UTC density shift and a uniform density grid. The 82-module
manifest, changed-test compilation and whitespace checks passed. The prior
archive fixtures and application runtime were unchanged; no full-suite,
browser, live-provider or SQL-execution run was performed for this addition.

The Figure 3 tail-discrepancy annotation update on 2026-09-25 passed the focused
module set with **96 passed, 3 xfailed, 1 existing warning in 63.26 seconds**.
Matching calibrated rectangles and sibling-PDF links in A/B were visually
checked. Panel C remains pixel-identical, diagnostic artifacts byte-identical,
and numerical provenance unchanged. All fixture manifests, published PDF
copies, link annotations, changed-source compilation and whitespace checks
passed. No scientific runtime or numerical expectation changed.

The subsequent Figure 3 paper-style marker update on 2026-09-25 passed the same
focused module set with **96 passed, 3 xfailed, 1 existing warning in 66.31
seconds**. Assertions now preserve every original pair coordinate and coincident
observation in the larger-dot overlay while keeping the linear density unchanged.
Panels A/C remain pixel-identical and the separate tail artifacts byte-identical.
Compilation, whitespace, vector PDF inspection and published-copy checks passed;
no scientific runtime or numerical expectation changed.

Focused Figure 3 density-presentation verification on 2026-09-25 reported
**96 passed, 3 xfailed, 1 existing warning in 64.70 seconds** across the Griffiths
references, segment temporal rendering, evidence statistics and demo PDF-link
integrity. Two new cases check exact production hourly density, its equivalence
to the 12-hour grid, global scaling and native sparse-marker coordinates at time
and rounding boundaries. Changed-source compilation, whitespace, PDF integrity
and visual checks passed. Panels A/C remain pixel-identical, and the separate
tail graphics/ledger remain byte-identical. Scientific runtime and numerical
expectations are unchanged; this isolated presentation update used focused
verification rather than another complete-suite run.

Latest complete regression verification on 2026-09-25 covered production-pipeline
publication reconstruction, including 13 additional cases protecting raw-source
replay, expected-input isolation and propagation of changed production evidence.
The complete foreground Windows runner reported:

```text
3153 passed, 1 skipped, 3 xfailed, 1 warning in 345.11 seconds
```

The skip, three strict expected failures and Matplotlib warning remain those
documented below. All eleven reference-fixture manifests (187 file entries),
97 unchanged frozen scientific inputs/expectations, full source compilation and
whitespace checks passed. All seven regenerated comparison PDFs were visually
reviewed and checked for their single original-publication raster and searchable
native plot/text content. Their static copies match the fixture sources. PNG
companions remain available. The generated SQL is executed through the bounded
offline SQLite adapter; this run does not claim live-provider or native
ClickHouse verification. No scientific runtime algorithm, demo setting or
independent numerical oracle changed. The existing static route and browser
checks below were not repeated because their implementation and URLs are
unchanged.

Earlier complete regression verification on 2026-09-25 covered the publication
comparison PDF additions, expanded Figure 3 tail review, demo PDF links and all
existing reference fixtures. The complete foreground Windows runner reported:

```text
3140 passed, 1 skipped, 3 xfailed, 1 warning in 359.67 seconds
```

The skip remains the absent prepared-export package; the three strict expected
failures remain the documented Griffiths paper/strongest-pair differences.
The warning is the existing Matplotlib `set_bad` pending deprecation. All eleven
reference-fixture manifests, full source compilation and whitespace checks
passed. The seven published PDF copies match their fixture sources and are
served as `application/pdf` with HTTP 200. Browser inspection confirmed the demo
links resolve to those routes and open in a new tab; the automation browser's
embedded viewer could not display PDFs, so visual inspection used Poppler
renderings. Each comparison PDF contains native generated plot geometry and
searchable text, with only its original publication panel stored as an image.
Existing demo settings and description text are preserved; no scientific
runtime calculation or frozen numerical oracle changed.

Previous complete regression verification on 2026-09-23 covered the shared remote-peer
special-callsign filter in `C:\Users\marku\Code\WSPRadar`, together with the
pre-existing working-tree changes to historical decode compatibility. The
complete foreground Windows runner reported:

```text
2996 passed, 1 skipped, 1 warning in 271.58 seconds
```

The warning is the existing Matplotlib pending deprecation. All 24 focused
peer-filter regression cases also passed. Generated Target/Reference predicates
were executed with SQLite for every supported Benchmark design and RX/TX
Performance, checking all three prefixes, enabled/disabled filtering, historical
fallback, and special-prefix Target, Reference and local-reference contributors.
The Performance check also preserves Target activity established through an
excluded remote peer. These are local predicate checks, not live ClickHouse
measurements. Full Python compilation, the runner's regression manifest
validation, README synchronization, JSON syntax and patch whitespace checks
passed. The full suite includes documentation rendering, localization, shared
Guided/Classic state, export and idle-import contracts. No live archive query,
browser walkthrough or deployment test was performed for this change.

The updated filter guidance is a completed co-authored English/German
integration under the approved remote-peer-only specification. Review covered
the manual filter row, shared tooltip, Guided explanation and compact review,
including RX/TX direction, eligible analysed endpoints and unchanged defaults.
German uses the established `Referenz` terminology. No semantic divergence or
unmatched unit remains in this scope. Integrated manual source SHA-256 hashes:

- `docs/doc_en.py`: `C789C9228E5F8133FBC60E57F4790A6A86B0FA4D253B1A82E450FE8CD1F871A7`
- `docs/doc_de.py`: `6E5288452C91F022C470988C37E75620F3C7C1529E6582D4DE6DE7F21AF4C02B`

Earlier regression verification on 2026-09-14 covered the initial-page import
boundary, bundled browser fonts, and the 140-pixel logo in
`C:\Users\marku\Code\WSPRadar`. The complete foreground Windows run reported:

```text
2887 passed, 1 skipped, 1 warning in 344.08 seconds
```

The warning is the existing Matplotlib pending deprecation. The focused
navigation, URL, documentation-controller, styling, and idle-import checks also
passed all 83 tests. Full Python compilation, the 81-module/five-chunk manifest,
and patch whitespace checks passed. The fresh-process audit confirms that the
idle app leaves NumPy, pandas, and PyArrow unloaded, including indirect framework
imports; controller payload JSON remains identical.

A bounded local Streamlit smoke check returned HTTP 200 `ok`, and all 15 bundled
font subsets returned HTTP 200 with exact file bytes. This Windows environment
labels those static fonts `application/octet-stream`; the Chromium browser check
rendered the intended text and icon styles without browser errors and confirmed
the header image's natural dimensions are 140 by 140 pixels. The temporary browser
and server were closed, with no matching server process remaining. These checks
do not establish deployed cold-browser timings or other browser/platform results.
The new PNG is 56,544 bytes versus 114,598 bytes for the original; its base64
payload is 75,392 bytes versus 152,800 bytes. Original logo files remain intact.

Earlier regression verification on 2026-09-14 covered the shared Guided/Classic
stale-result fix in `C:\Users\marku\Code\WSPRadar`. The complete foreground
Windows run reported:

```text
1 failed, 2882 passed, 1 skipped, 2 warnings in 415.47 seconds
```

The sole failure was an indentation-sensitive source assertion in
`test_url_state.py`; the new results-region context changed indentation without
changing the tested readiness condition. That assertion now compares the Python
syntax tree, and the complete affected module then passed all 88 tests in
2.65 seconds. No runtime code changed after the full run. The absent scientific
fixture remains skipped. The full-run warnings were the existing Matplotlib
pending deprecation and a local pytest cache-directory permission warning;
disabling cache writes for the follow-up produced an unused `cache_dir` option
warning. Full repository compilation and patch whitespace checks passed.

The full run used Node.js on `PATH` and fresh ignored temporary/cache paths
(`.test/pytest-stale-results-final` and
`.test/pytest-stale-results-final-cache`). Browser verification used the actual
app shell, configuration controls, map-block renderer, navigation controller,
and deferred Inspector placement with synthetic map data and controlled local
preparation delays. Guided-to-Classic, Classic-to-Guided, and Benchmark-to-
Performance transitions produced no misplaced or duplicate result headers.
Old maps cleared before a fresh run; the current map remained visible while
Inspector preparation waited. Status and first-map landings remained near the
80 px offset. A completed-result rerender retained exactly the measured scroll
position (1838.5966 px) and Inspector heading position (362.8015 px) during
preparation and after completion. The real app entry point returned HTTP 200
`ok`; all temporary browser tabs and bounded servers were closed. No Community
Cloud deployment was performed.

Earlier complete serial verification on 2026-09-14 ran in
`C:\Users\marku\Code\WSPRadar` after the approved processing-panel and first-map
scroll milestones, manual-navigation cancellation, and viewport-preserving
rerenders:

```text
2869 passed, 1 skipped, 1 warning in 295.21 seconds
```

The canonical foreground Windows runner used fresh ignored temporary/cache
directories through `PYTEST_ADDOPTS` (`--basetemp=.test/pytest-navigation-final-full-20260914`
and `--override-ini=cache_dir=.test/pytest-navigation-final-full-cache-20260914`)
because the older default pytest directories were owned by a different local
account. Node.js was on `PATH`, so all navigation event scenarios executed. The
remaining skip is the absent scientific fixture, and the warning is the existing
Matplotlib pending deprecation. Full Python compilation and patch whitespace
checks passed. The actual app started, returned HTTP 200 `ok`, and rendered its
idle interface. A separate controlled Streamlit browser fixture using the
production navigation controller verified status landing before map readiness,
map landing while Inspector preparation was held open, manual-scroll
cancellation, completion without another landing, and an ordinary rerender with
exactly unchanged scroll position. This browser check used synthetic map data;
the full regression suite separately verifies the real run-controller ordering,
first valid map after no-data blocks, token replacement, and failure cleanup.
English and German navigation guidance were updated together and README was
regenerated from the authoritative English manual.

Earlier complete serial verification on 2026-09-14 ran directly in
`C:\Users\marku\Code\WSPRadar` after the approved Performance temporal-key
preparation and shared temporal bar-collection changes. All charts and offered
time-bin variants remain prepared immediately. Temporal layout version 3
invalidates prior preview and prepared-export render caches; scientific recipe
schemas and persisted evidence remain unchanged.

```text
2831 passed, 1 skipped, 1 warning in 296.87 seconds
```

The canonical Windows launcher used
`--basetemp=.test/pytest-temporal-full-20260913` and
`--override-ini=cache_dir=.test/pytest-cache-temporal-full-20260913`, preserving
the existing ownership of older temporary directories. The 81-module manifest,
full Python compilation, tracked patch whitespace and new-file whitespace checks
passed. The suite includes 31 new cases for compact station/time keys, timestamp
resolution, count widening, selected-station raw SNR, categorical identity
matching, caller ownership, exact bar geometry and preview/export raster checks.

Offline comparisons loaded the actual cached Griffiths Performance and Benchmark
analyses from the supplied performance log. The 638,847-row Performance input
produced the exact same complete scope and selected-station recipes for all six
one-hour through 24-hour variants. Eight additional edge cases covered shared
callsigns at different locators, unequal coverage, unused categorical levels,
missing identities, empty evidence, count totals above 255, compatible nonbinary
inputs and unequal selected-station SNR depth. The original artifacts retained
their hashes and timestamps; full-chart comparisons also verified that source
DataFrames were unchanged.

Local timings below are medians of three alternating before/after samples against
saved pre-change functions, with no concurrent test or benchmark run. Renderer
measurements exclude one warm-up per implementation and include figure
construction plus a 100-DPI canvas draw, excluding PNG encoding and browser
painting. They are component measurements, not an end-to-end or concurrent
Community Cloud speedup.

| Component | Before | After | Component speedup |
| --- | ---: | ---: | ---: |
| Performance scope temporal preparation, all six variants | 5.617 s | 4.273 s | 1.31x |
| Performance selected temporal preparation, all six variants | 0.746 s | 0.729 s | Essentially unchanged |
| Performance selected outcome chart, six-hour bins | 1.902 s | 0.832 s | 2.29x |
| Performance scope outcome chart, one-hour bins | 6.473 s | 0.890 s | 7.28x |
| Benchmark scope coverage chart, one-hour bins | 9.376 s | 1.091 s | 8.60x |

The Performance scope's prepared temporal DataFrame decreased from 47,822,160
to 35,351,874 bytes (45.6 to 33.7 MiB, 26.1%). This is the materialized
DataFrame size, not peak process memory. The one-hour Performance scope chart
uses eight bar collections instead of 2,976 Rectangle artists; the Benchmark
scope chart uses twelve collections instead of 4,464 Rectangles.

Eight full-chart comparisons covered Performance and Benchmark, scope and
selected station, English 100-DPI previews and German 300-DPI exports. All
recipes, drawn polygon coordinates, axes and text matched exactly. Seven images
were pixel-identical. One Benchmark selected-station preview differed at 15
bar-edge pixels out of 728,000 (0.0021%) despite exact geometry; the corresponding
export image was identical. Visual inspection found no perceptible change.
No provider requests, commits, pushes, deployment or Cloud load test were made.

Previous complete serial verification on 2026-09-13 ran directly in
`C:\Users\marku\Code\WSPRadar` after selective transfer of the three
correctness fixes and four performance optimizations. The checkout retained its
newer Benchmark folded-date annotation behavior and temporal layout version 2.

```text
2800 passed, 1 skipped, 1 warning in 288.66 seconds
```

The canonical Windows launcher used
`--basetemp=.test/pytest-transfer-20260913` and
`--override-ini=cache_dir=.test/pytest-cache-transfer-20260913`. Its default
temporary and cache directories were owned by another Windows account and
rejected cleanup; the initial focused run therefore had 407 passes and 112
setup errors. The complete successful run supersedes that incomplete check.
Existing directory ownership and permissions were left unchanged.

A local offline AppTest replay used the exact cached `vanhamel_rx_buddy`
observations from the supplied profiling log. The real demo callback launched
the unchanged application before shell rendering, avoiding AppTest's inability
to serialize one existing shell widget for a synthetic second-run button click.
All scientific preparation and chart rendering remained real. The replay
verified all 110 imported project modules originated in the intended checkout.

The replay retained 7,139 evidence rows from 7,166 raw observations, with 75 map
stations and 13 segments. Complete evidence and both map-aggregate frames matched
the original run exactly. The map and all five Inspector PNGs were rendered;
the map read used ten projected columns, no network request was attempted, no
ZIP was prepared, and the original cache contents and timestamps were unchanged.
The recorded analysis duration was 11.650 seconds; the full AppTest execution,
including initial application work, took 15.856 seconds. This is one local
serial replay, excluding browser painting and concurrent Community Cloud load;
it does not establish a controlled end-to-end speedup against the earlier log.

Repeating the same 100,000-row component diagnostics in the intended checkout
gave the following medians of three alternating before/after samples, with exact
result equality checked before timing and no concurrent test or diagnostic run:

| Component | Before | After | Component speedup |
| --- | ---: | ---: | ---: |
| Map geometry and labels | 5.383 s | 0.159 s | 33.8x |
| Solar states, 1,000 distinct timestamps | 6.306 s | 0.069 s | 90.8x |
| Temporal summaries, 1,000 groups | 1.628 s | 0.073 s | 22.4x |
| Local Median Parquet read, five Reference detail entries per row | 0.042 s | 0.037 s | 1.15x |

The projected Local Median DataFrame again decreased from 28,390,132 to
10,190,132 bytes (64.1%). This measures materialized DataFrame size, not process
RSS. Full compilation, patch and new-file whitespace checks, and the 79-module
regression manifest passed. The existing fixture skip and Matplotlib warning
remain unchanged. No commit, push, deployment, or Cloud load test was performed.

Local component measurements in the Codex worktree on 2026-09-13 compared the implemented performance
changes against saved pre-change functions in the same Python 3.12.14 process
(pandas 3.0.3, NumPy 2.4.6). Each timing is the median of three alternating
before/after samples, following an exact-result comparison, without concurrent
pytest or another diagnostic process. All examples contain 100,000 rows:

| Component | Before | After | Component speedup |
| --- | ---: | ---: | ---: |
| Map geometry and labels | 5.983 s | 0.159 s | 37.5x |
| Solar states, 1,000 distinct two-minute timestamps | 6.161 s | 0.074 s | 83.4x |
| Temporal summaries, 1,000 groups | 1.507 s | 0.072 s | 20.9x |
| Local Median Parquet read, five Reference detail entries per row | 0.051 s | 0.038 s | 1.33x |

The map example uses seeded random coordinates plus missing/wrap/boundary cases;
the solar example repeats 1,000 instants starting on 2026-07-01 at Target
coordinates 52.5, 13.4. Temporal summaries use seeded normal values, a missing
value every 197 rows, and three additional empty bins. The random seed is
20260913. Exact quartile interpolation requires two native order-statistic
passes, so its measured speedup is lower than the earlier simple grouped-linear
prototype; the implementation preserves the prior scalar arithmetic.

In the synthetic Local Median example, projecting 12 stored columns to the 10
map-consumed columns reduces `DataFrame.memory_usage(deep=True)` from 28,390,132
to 10,190,132 bytes (64.1%). Complete Reference details remain in the staged
Parquet artifact. This is materialized DataFrame size, not process RSS, and the
read timings include a warm local filesystem cache. These component results do
not establish end-to-end application speedup or Community Cloud concurrency
capacity. No deployment or Community Cloud load test was performed.

Previous complete serial verification in the Codex worktree on 2026-09-13
through the Windows launcher,
under Python 3.12.14, covers map-label lookups, distinct-timestamp solar
classification, exact native grouped quartiles, and map-specific Parquet reads:

```text
2800 passed, 1 skipped, 1 warning in 292.73 seconds
```

The 86 additional cases cover geometry and bin-label equivalence, solar states
and timestamp alignment across analysis modes, exact quartile and dtype
compatibility, and full-versus-projected map aggregates and evidence ownership.
The existing controller lifecycle test also verifies use of the declared map
projection. Full repository compilation, patch/new-file whitespace checks, and
the 79-module serial regression manifest passed. The skipped fixture-integrity
test and Matplotlib pending-deprecation warning remain unchanged.

Previous complete serial verification in the Codex worktree on 2026-09-13
through the Windows launcher,
under Python 3.12.14, covers the admission cache-preparation split, localized
Performance Drill-Down filtering, and explicit export evidence failures:

```text
2714 passed, 1 skipped, 1 warning in 299.99 seconds
```

The 56 additional regression cases cover responsive permit/status operations
during blocked cache preparation, FIFO/provider reservation and timeout cleanup,
localized Target/Counter filters, and failed versus legitimately empty export
evidence. Four seeded Streamlit AppTests exercise the real filter multiselect
and slider in both languages and directions. Full compilation, tracked and
changed-untracked-file whitespace checks, and the 78-module manifest passed.
The worktree reused the existing project virtual environment through an ignored
`.venv` junction. Verification was local; no Community Cloud load test or
deployment was performed.

Previous complete serial measurement on 2026-09-13 through the Windows launcher,
including typed export payloads, detached content ownership, complete package
signatures and unchanged-rerender reuse, under Python 3.12.14:

```text
2658 passed, 1 skipped, 1 warning in 268.70 seconds
```

Full repository compilation, patch/new-file whitespace checks, the 78-module
serial regression manifest, and the idle-import boundary passed. Real Streamlit
AppTests verify that a committed profile edit removes an already rendered stale
download while retaining completed results, and that drafts and identical
commits preserve prepared exports. Export tests cover nested table/recipe
ownership, dtype and numerical precision, duplicate columns, complete content
invalidation, captured queue inputs, stale-publication rejection, current saved
configuration metadata, established schemas and filenames, and shared
preview/export recipes. A bounded startup check returned HTTP 200 with `ok`
and stopped its exact child process.

A local export-bookkeeping diagnostic used seven alternating before/after
samples with representative ten-column tables, a fixed 160 KB numerical recipe,
validated saved configuration, the English translation catalog, and three
session-owned artifacts. Median unchanged registration plus footer time was
16.27/18.11 ms for empty tables, 14.24/18.24 ms for 10 rows, 42.60/21.85 ms for
1,000 rows, and 280.81/35.15 ms for 10,000 rows. Warm footer signatures improved
at every measured size; complete registration checks add 2–4 ms for tiny inputs
whose full recipe/context content was previously omitted. Unchanged Inspector
and map registrations retained their owned blocks and prepared ZIP bytes;
changed map context invalidated the ZIP. These measurements cover export
bookkeeping only, excluding widgets, scientific preparation, network access,
figure rendering and ZIP construction; they are not whole-app latency claims.

Earlier complete serial measurement on 2026-09-13 through the Windows launcher,
including the Inspector preparation coordinator and focused presentation
components, under Python 3.12.14:

```text
2593 passed, 1 skipped, 1 warning in 267.59 seconds
```

Full repository compilation, patch/new-file whitespace checks, the 76-module
serial regression manifest, and the expanded idle-import boundary passed.
The Inspector orchestration module now has 265 lines, with a 99-line page-flow
function. Regression coverage exercises the production component flow,
selection/navigation callbacks, cache reuse, exact identities, native comparison
precision, compact display profiles, exported recipes, and unchanged source-frame
ownership. A real Streamlit scope-control check also passed stable widget keys,
language switching, hidden-widget rehydration, scope tokens, and clearing a
selection back to All. A bounded startup check returned HTTP 200 with `ok` and
stopped its exact child process.

An isolated before/after warm Inspector cache-access diagnostic measured median
lookup time at 7.48/7.22 microseconds with identical 684-byte cached values.
Five samples of 20,000 lookups alternated execution order, with logging stubbed
equally on both paths. This measures cache-access overhead only, not complete
application latency. Existing scientific helpers, cache versions, byte/entry
limits, complete presentation/scientific dependencies, and lazy artifact-read
branches were retained.

Earlier complete serial measurement on 2026-09-13 through the Windows launcher,
including the canonical Inspector selection contract and selection/navigation
state owner, under Python 3.12.14:

```text
2562 passed, 1 skipped, 1 warning in 278.43 seconds
```

Full repository compilation, patch/new-file whitespace checks, the 73-module
serial regression manifest, and the idle-import boundary passed. A bounded
Streamlit startup check returned HTTP 200 with `ok` and stopped its exact child
process. Real Streamlit AppTests exercised scope callbacks, conditional-widget
cleanup, candidate-focus rehydration, manual zoom, explicit Off, and stale
scope handling. The ownership audit allows only Inspector cache writes in the
renderer; selection mutations belong to the new adapter. Scientific and figure
preparation retain their existing implementations.

A local before/after comparison retained the same outcomes across 24 station
selection cases, including automatic selection, deliberate deselection, missing
identities, and exact ordered selections. Median lookup time for 1,000 rows
with one selected station was 12.39/10.82 milliseconds; eight selected stations
measured 12.87/11.31 milliseconds. The new path includes construction and
validation of `InspectorSelection`. A separate isolated 10,000-row comparison
measured 111.30/109.25 milliseconds for one selected station and
110.51/105.98 milliseconds for eight. Each comparison alternated execution
order over five samples of ten lookups. The adapter avoids the former temporary
two-column DataFrame allocation and reuses already validated station identities.
These are local lookup diagnostics, not browser-latency or multi-user load
measurements. The initial longer timing probe was stopped without using its
results; the largest fixture was measured again without concurrent verification.

Earlier complete serial measurement on 2026-09-13 through the Windows launcher,
including immutable analysis/completed-run contracts and centralized lifecycle
transitions:

```text
2509 passed, 1 skipped, 1 warning in 279.48 seconds
```

Full repository compilation, the idle-import boundary, and a bounded Streamlit
startup check passed; the health endpoint returned HTTP 200 with `ok`, and the
exact check process was stopped. Independent before/after comparison across 56
plan cases retained identical mappings, scientific fingerprints, and all 112
strict/legacy SQL texts.

A small comparison using three fresh processes per version and the same
browser-component stubs measured median server-side AppTest startup at
2.73/2.76 seconds and warm idle rerenders at 95.5/93.4 milliseconds
(before/after). Warm completed-snapshot reads measured 37.5/0.34 microseconds
after replacing recursive copies with immutable-record reuse. These are local
diagnostic timings, not browser latency or a multi-user load benchmark. The
Windows RSS helper returned unavailable values; no memory-performance result
was established.

Earlier complete serial measurement on 2026-09-13 through the Windows launcher,
including completed-result language switching and manifest-validation coverage:

```text
2440 passed, 1 skipped, 1 warning in 241.86 seconds
```

Earlier complete serial measurement on 2026-09-13, including the Benchmark
callsign-plus-full-locator weighting/support correction and its bilingual
explanations:

```text
2326 passed, 1 skipped, 1 warning in 275.67 seconds
```

Earlier complete serial measurement on 2026-09-13, including the conservative
Local Neighborhood date-line/pole bounding-box correction:

```text
2279 passed, 1 skipped, 1 warning in 263.53 seconds
```

Earlier complete serial measurement on 2026-08-17:

```text
2062 passed, 1 skipped, 1 warning in 234.55 seconds
```

The skipped test requires a generated fixture under
`tests/regression/fixtures/`. That directory currently contains only `.gitkeep`.
The warning is a Matplotlib pending deprecation for `set_bad` in
`ui/plots/evidence_figures.py`.

<a id="source-and-whitespace-2026-07-11"></a>

## Source-compilation and whitespace record, 2026-07-11

Both commands passed during the 2026-07-11 review.

<a id="griffiths-paper-reference-2026-09-24"></a>

## Griffiths publication-reference verification, 2026-09-24

Focused verification on 2026-09-24 reported **100 passed, 1 skipped,
3 xfailed, 1 existing warning in 34.70 seconds** across the reference module
and directly related fixture/evidence/runner modules. The three strict expected
failures are the documented publication-versus-production pairing differences;
the skip remains the absent prepared-export fixture. Compilation, whitespace,
82-module manifest validation and preservation hashes passed. This isolated
addition did not run the complete suite, browser, live provider or database SQL.

<a id="zander-reference-2026-09-24"></a>

## Zander reference verification, 2026-09-24

Focused verification on
2026-09-24 reported **138 passed, 3 existing xfailed, 1 existing warning in
57.02 seconds** across Zander, Griffiths and related evidence/runner modules.
The three expected failures remain the documented Griffiths Figure 3 cases;
Zander has no expected failures. The new module is registered once in the
83-module, five-chunk manifest. This isolated test/fixture addition changes no
runtime behavior and does not run the complete suite or a live provider.

<a id="vanhamel-calibration-2026-09-24"></a>

## Vanhamel calibration verification, 2026-09-24

Focused verification on 2026-09-24 reported **317 passed, 3 existing xfailed,
1 existing warning in 50.07 seconds**, covering Vanhamel, Zander, Griffiths,
configuration/schema, regression-runner, temporal-evidence and evidence-statistic
modules. All nine new Vanhamel checks pass. The three expected failures remain
the documented Griffiths Figure 3 cases. The updated manifest validates 84
modules across five serial chunks; changed Python compilation and whitespace
checks pass. The ten independent expected files regenerate byte-identically.
This demo-data/test addition does not change scientific runtime calculations;
the complete suite and a native ClickHouse replay were not run for this step.

<a id="vanhamel-rotation-2026-09-24"></a>

## Vanhamel rotation verification, 2026-09-24

Focused verification on 2026-09-24 reported **377 passed, 3 existing xfailed,
1 existing warning in 78.32 seconds**, covering all four publication reference
modules plus configuration/schema, regression-runner, evidence-statistics,
segment-temporal and selected-station figure coverage. All thirteen new
Figure 6 checks pass; expected failures remain the documented Griffiths
Figure 3 cases, and the warning is the existing Matplotlib deprecation.
The eight expected files regenerate byte-identically with the standard-library
builder under `python -S`. All eighteen frozen files match the SHA256 manifest
and retain identical hashes with Git clean filters applied. The manifest
validates 85 modules across five serial chunks, and changed Python compilation
and whitespace checks pass. This isolated fixture/demo-data addition does not
change shared scientific algorithms; the full regression suite and native
ClickHouse execution were not rerun for this step.

<a id="milazzo-tx-reference-2026-09-24"></a>

## Milazzo TX reference verification, 2026-09-24

All ten calculated expected files regenerate byte-identically under
`python -S`. The source CSV preserves the original Parquet values exactly,
including binary coordinate values; all 28 manifest files pass SHA256 and
Git clean-filter byte-preservation checks. The fixed runner validates
86 modules across five serial chunks. Changed Python compilation passes.

Focused verification on 2026-09-24 first passed all **17 new Milazzo tests**.
The related integration run reported **418 passed, 3 existing xfailed and
one failure in 93.63 seconds**: the new demo description lacked the required
spaces around em dashes. After that presentation-only correction, rerunning
the complete Milazzo and configuration modules reported **41 passed in
28.20 seconds**. Both runs emitted the one existing Matplotlib deprecation
warning. The expected failures remain the documented Griffiths Figure 3
cases. Related coverage included all publication reference modules,
configuration/schema, regression-runner, historical decode fallback,
non-joint evidence, temporal coverage and evidence statistics. No shared
scientific calculation changed; the complete regression suite and native
ClickHouse replay were not run for this isolated fixture/demo-copy addition.

<a id="milazzo-rx-reference-2026-09-24"></a>

## Milazzo RX reference verification, 2026-09-24

Focused verification on 2026-09-24 passed all **23 Milazzo tests** before the
additional TX-table cross-check. The final focused run, including that added
test, configuration/schema, non-joint evidence, decode fallback and runner
coverage, passed **296 tests with one existing Matplotlib warning in 70.47
seconds**. The final Milazzo module contains 24 tests. Changed Python source
compilation, 86-module/five-chunk manifest validation and whitespace checks
passed. No shared runtime calculation changed; the full suite and native
ClickHouse replay were not run for this fixture and demo-copy update.

<a id="milazzo-overlay-artifact-2026-09-24"></a>

## Milazzo overlay artifact verification, 2026-09-24

On 2026-09-24 the complete
Milazzo module passed **24 tests with one existing warning in 27.55 seconds**.
Changed-script compilation, artifact hashes and whitespace checks passed.
No runtime calculation or demo settings changed; native ClickHouse and the
full suite were not rerun for this artifact addition.

<a id="milazzo-overlay-integration-2026-09-24"></a>

## Milazzo overlay regression integration, 2026-09-24

Focused verification on 2026-09-24 passed **33 Milazzo tests with one existing
Matplotlib warning in 25.49 seconds**. Changed-test source compilation,
86-module/five-chunk manifest validation and whitespace checks passed.
This supersedes the earlier overlay-only Figure 7 coverage limit. No runtime
calculation, demo settings or original publication images changed; the complete
suite and native ClickHouse replay were not rerun for this isolated addition.

