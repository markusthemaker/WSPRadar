# Repository scripts

Routine repository commands live directly in `scripts/`. Specialist fixture,
scientific-reference and publication maintenance tools live in
[`scripts/internal/`](internal/). Both groups are available for maintainers to
run explicitly; the distinction describes their purpose, not an access restriction.

Run the examples below from the repository root using the project's configured
Python environment. Setup and verification policy are documented in
[`AGENT_README.md`](../AGENT_README.md). The PowerShell Git workflow has its own
[`README-git-workflow.md`](README-git-workflow.md), including each command's
options and effects.

## Routine commands

| Command or supporting file | Purpose |
| --- | --- |
| [`git-baseline-temp.ps1`](git-baseline-temp.ps1) | Bring the local `temp` branch to the remote baseline according to the documented Git workflow. |
| [`git-push-temp.ps1`](git-push-temp.ps1) | Commit and publish work through the documented `temp` workflow. |
| [`git-release-main.ps1`](git-release-main.ps1) | Publish tested `temp` work to `main` through the documented release workflow. |
| [`git-cleanup-onedrive.ps1`](git-cleanup-onedrive.ps1) | Perform the documented cleanup of OneDrive-related Git artifacts. |
| [`run_regression.cmd`](run_regression.cmd) | Windows foreground entry point for the regression runner. |
| [`run_regression.ps1`](run_regression.ps1) | Implementation of that runner, including fixed serial chunk validation. |
| [`regression_test_chunks.json`](regression_test_chunks.json) | The runner's maintained partition of regression modules; this is supporting configuration, not a command. |
| [`sync_readme_from_doc_en.py`](sync_readme_from_doc_en.py) | Regenerate the root README from authoritative `docs/doc_en.py`. |

For example:

```powershell
.\scripts\run_regression.cmd
.\scripts\run_regression.cmd -Focused tests/regression/test_input_validation_state.py -x
python scripts/sync_readme_from_doc_en.py
```

`-Focused` accepts existing Python regression files and `::node` selections;
place every target before forwarded pytest options. For pytest short options
that overlap PowerShell common parameters, use their long forms: for example,
`--override-ini=cache_dir=...` instead of `-o`, and `--verbose` instead of `-v`.
It cannot be combined with
`-Chunk` or `-ValidateChunks`. Without `-Focused` or `-Chunk`, the runner still
selects the complete regression suite.

Each executing Windows invocation prints and uses a fresh
`.test/runs/<run-id>/temp` and `cache` workspace. Explicit pytest `--basetemp`
or `--override-ini=cache_dir=...` options override those defaults. `-ValidateChunks` creates
no directories. Previous runs remain available for diagnosis and use disk space;
after preserving needed evidence and checking for active users, clean only the
exact completed run directory owned by the task. A fresh cache does not carry
`--last-failed` history; pass an explicit reused cache directory when needed.
Separate pytest paths do not make the application tests safe to run concurrently.

On Linux or macOS, use `python -m pytest tests/regression -q` when a complete
regression run is required. The Windows regression scripts remain together with
their manifest because they form one operating workflow.

## Specialist maintenance

Use the fixture's own README for source inputs, scientific assumptions and the
review procedure. The [scientific reference index](../tests/regression/reference_fixtures/README.md)
and [regression directory guide](../tests/regression/README.md) distinguish
independent scientific references from prepared-export integrity fixtures.

| Tool in `internal/` | Purpose |
| --- | --- |
| [`build_regression_fixture_from_demo_folder.py`](internal/build_regression_fixture_from_demo_folder.py) | Convert an unpacked prepared-results export into an integrity fixture. |
| [`build_milazzo_prepared_export_fixture.py`](internal/build_milazzo_prepared_export_fixture.py) | Build the offline Milazzo RX prepared-export fixture from its frozen scientific reference. |
| [`build_zander_reference_fixture.py`](internal/build_zander_reference_fixture.py) | Calculate independent Zander Experiment A expectations from frozen raw reports. |
| [`build_vanhamel_reference_fixture.py`](internal/build_vanhamel_reference_fixture.py) | Calculate independent Vanhamel RX calibration expectations. |
| [`build_vanhamel_rotation_reference_fixture.py`](internal/build_vanhamel_rotation_reference_fixture.py) | Calculate independent Vanhamel Figure 6 rotation expectations. |
| [`build_vanhamel_temporal_density_reference.py`](internal/build_vanhamel_temporal_density_reference.py) | Derive the versioned correction-aware temporal-density reference without changing the original scientific expectations. |
| [`build_milazzo_reference_fixture.py`](internal/build_milazzo_reference_fixture.py) | Calculate the bounded independent Milazzo TX reference. |
| [`build_milazzo_rx_reference_fixture.py`](internal/build_milazzo_rx_reference_fixture.py) | Derive the bounded Milazzo Figure 6 RX reference and paper-marker correspondence. |
| [`build_griffiths_figure3_comparisons.py`](internal/build_griffiths_figure3_comparisons.py) | Render Griffiths Figure 3 comparisons and diagnostics. |
| [`build_griffiths_fig6_comparison.py`](internal/build_griffiths_fig6_comparison.py) | Render the Griffiths Figure 6 comparison. |
| [`build_vanhamel_rotation_comparison.py`](internal/build_vanhamel_rotation_comparison.py) | Render the Vanhamel Figure 6 rotation comparison. |
| [`build_zander_fig4_comparison.py`](internal/build_zander_fig4_comparison.py) | Render the Zander Figure 4 comparison from production replay and paper evidence. |
| [`build_milazzo_publication_overlays.py`](internal/build_milazzo_publication_overlays.py) | Build Milazzo publication review overlays from paper pixels and production SQL replay. |
| [`verify_performance_method_revision.py`](internal/verify_performance_method_revision.py) | Compare independent frozen-source Performance arithmetic with production replay. |
| [`verify_milazzo_clickhouse.py`](internal/verify_milazzo_clickhouse.py) | Explicitly compare the frozen Milazzo reference against one live configured provider; `--dry-run` prepares the offline comparison without sending queries. |
| [`sync_reference_figure_pdfs.py`](internal/sync_reference_figure_pdfs.py) | Publish the fixture PDFs referenced by demo descriptions into static assets, or check those copies with `--check`. |
| [`demo_pdf_header.py`](internal/demo_pdf_header.py) and [`demo_pdf_footer.py`](internal/demo_pdf_footer.py) | Shared presentation helpers imported by the figure builders; not standalone commands. |

Command paths now include `internal/`, for example:

```bash
python scripts/internal/sync_reference_figure_pdfs.py --check
python scripts/internal/verify_milazzo_clickhouse.py --dry-run
```

Builder options and output behavior are unchanged by this directory move. Some
presentation builders default to their authoritative fixture directory. Follow
the relevant fixture README and choose a separate candidate output directory
when reviewing changes. Use a task-specific ignored `.tmp/` directory for
temporary candidates, and retain approved artifacts in their documented
authoritative locations.

Frozen manifests and provenance documents retain the script paths and hashes
recorded when their artifacts were created. Those historical records are not
rewritten for a directory move. The corresponding current commands are under
`scripts/internal/`; newly generated provenance records the current source.

## Manual multi-user testing

The complete dedicated harness stays in
[`tests/manual/multi_user_load_test/`](../tests/manual/multi_user_load_test/README.md),
including its runner, capture and packaging tools, dependency list, tests and
Linux/Codespaces instructions. It is not duplicated under `scripts/`.

Captured load-test datasets and result archives use the locations documented in
that harness README. Ignored working data is separate from the reusable source
code and must be retained separately when an exact replay is needed later.

## Verification of this reorganization

The 2026-09-27 relocation and browser-protection changes were reviewed as source;
executable checks were deferred to Codespaces at the operator's request. From a
Codespaces checkout or fresh source snapshot containing these changes, with the
documented development and load-harness dependencies installed, run:

```bash
python -m unittest discover -s tests/manual/multi_user_load_test -p test_bundle.py
python -m pytest tests/regression/test_config_package.py tests/regression/test_demo_fixtures.py tests/regression/test_demo_pdf_headers.py tests/regression/test_griffiths_temporal_reference.py tests/regression/test_milazzo_provider_check.py tests/regression/test_milazzo_reference.py tests/regression/test_vanhamel_rotation_reference.py tests/regression/test_zander_experiment_a_reference.py tests/regression/test_public_entrypoint.py -q
python -m compileall -q scripts tests/manual/multi_user_load_test tests/regression
```

In a Git checkout, also run `git diff --check`. An extracted source ZIP does not
contain the source checkout's Git diff; an enclosing Codespaces repository cannot
substitute for that check. Follow `AGENT_README.md` for complete release
qualification. The focused commands above do not establish a full regression pass.

After deployment, verify loading, saved-configuration upload, and reconnecting
after an idle period on the Community Cloud app with both CORS and XSRF enabled.
Local/static configuration assertions do not prove the deployed connection path.
