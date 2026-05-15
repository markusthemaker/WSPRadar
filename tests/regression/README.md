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

Run the current fixture integrity tests:

`python -m pytest tests/regression`

Print the per-fixture comparison summary while running:

`python -m pytest -s tests/regression`

If pytest is not installed in the active Python environment:

`python -m pip install -r requirements-dev.txt`

These tests are intentionally conservative. They first verify that checked-in golden exports are internally consistent and complete. The next layer can regenerate tables and figures from the bundled parquet caches and compare them against the fixture outputs.
