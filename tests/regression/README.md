# Regression Fixtures

This folder holds golden WSPRadar result exports generated from demo runs.

Each fixture is built from an unzipped prepared-results export and contains:

- the saved WSPRadar config
- run metadata
- exported CSV tables
- exported PNG figures
- parquet analysis cache files
- a generated `expected_metrics.json`
- generated `regression_report.json` and `regression_report.md` files

Build a fixture from a demo export:

`python scripts/build_regression_fixture_from_demo_folder.py tests/demo/<demo-folder>`

Overwrite an existing fixture intentionally:

`python scripts/build_regression_fixture_from_demo_folder.py tests/demo/<demo-folder> --force`

Run the complete regression suite on Windows in the canonical serial
environment:

`.\scripts\run_regression.cmd`

Validate the five fixed fallback chunks without running pytest:

`.\scripts\run_regression.cmd -ValidateChunks`

Profile the 30 slowest tests in one serial full-suite run:

`.\scripts\run_regression.cmd -Durations 30`

Print the per-fixture comparison summary while running:

`python -m pytest -s tests/regression`

On Linux or macOS, run `python -m pytest tests/regression -q`. Do not run the
Windows chunks concurrently or use pytest-xdist/`-n`; the suite contains shared
filesystem, process, Streamlit, Matplotlib, and cache state that has not been
audited for worker isolation.

If pytest is not installed in the active Python environment:

`python -m pip install -r requirements-dev.txt`

These tests are intentionally conservative. They first verify that checked-in golden exports are internally consistent and complete. The next layer can regenerate tables and figures from the bundled parquet caches and compare them against the fixture outputs.
