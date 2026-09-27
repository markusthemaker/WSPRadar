# Demo Export Intake

Place unzipped WSPRadar prepared-results exports here when you want to turn them into regression fixtures.

This is local intake, not the permanent fixture store. Its contents are ignored
by Git except for this README. After review, use the builder below to create a
fixture under `tests/regression/fixtures/`; preserve any unique source evidence
before removing an intake directory. Keeping an export here does not include it
in a commit or a source-transfer bundle.

Recommended workflow:

1. Run a demo or representative analysis in the app.
2. Use `Prepare All Results for Download`, then download the prepared ZIP.
   The ZIP includes CSV tables, high-resolution figures, run metadata, config,
   and the parquet analysis caches needed for offline regression work.
3. Unzip it under this folder, for example:

   `tests/demo/vanhamel_rx_buddy/WSPRadar_export_2026_05_15__21_30/...`

4. Build a regression fixture:

   `python scripts/internal/build_regression_fixture_from_demo_folder.py tests/demo/vanhamel_rx_buddy`

The builder accepts either a folder that directly contains `config/run_metadata.json` or a parent folder with exactly one exported WSPRadar result folder inside it.
