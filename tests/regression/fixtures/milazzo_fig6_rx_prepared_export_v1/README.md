# Milazzo Figure 6 prepared-export snapshot

This small Benchmark export activates the prepared-package integrity regression
test with real tables, native production figures, configuration, metadata and
Parquet evidence. It is a **derivative package snapshot**, not a new independent
scientific oracle, a live provider capture, or an approval by a human reviewer.

## Source and execution

The unchanged source is
[`milazzo_fig6_rx_v1`](../../reference_fixtures/milazzo_fig6_rx_v1/README.md).
Its 86 frozen user-supplied wspr.rocks reports contain 44 selected endpoint
reports within 19 December 2010 12:00 through 20 December 2010 20:00 UTC.
They describe VE6PDQ transmitting to KP4MD (Target) and WB6RQN (Reference),
using both full reported transmitter locators, DO34 and DO34ir.

The maintenance script executes production-generated SQL using the established
offline SQLite compatibility executor, then production filtering, map
aggregation, inspector preparation, native figure recipes and
`ui.results_export.build_results_zip`. It calls the existing
`scripts/build_regression_fixture_from_demo_folder.py` builder on that real
unzipped package. All network connections are explicitly rejected during the
build. The original independent reference files are neither regenerated nor
modified. Their input/configuration/oracle hashes are recorded in `manifest.json`.

Mode codes were unknown in the supplied reports. The strict query is empty;
the historical fallback supplies the result. Export metadata therefore records
`legacy_no_code`. This does not establish original mode provenance.

The production exporter requires a known provider enum and has no offline
value. The `wspr_live` value in this derivative package is solely the required
**export-harness provider label**. It does not identify where these supplied
reports were obtained. `fixture_provenance` in `config/run_metadata.json` and
`org.wspradar.fixture_provenance` in the saved configuration explicitly record
the actual frozen-source origin and `provider_queried: false`. The additional
metadata qualification is attached after ZIP extraction; the production
signature and other generated metadata are retained. No HTTP or native
ClickHouse query was executed for this snapshot.

## Reviewed contents

The replay was checked against the independent native-unit expectations before
export. It yields 39 SQL groups and 34 retained native units: 26 Target-only,
five Joint and three Reference-only. The five paired differences are
8, 17, 22, 7 and 7 dB, with median 8 dB. These gate counts apply only to this
bounded VE6PDQ input; other transmitters are absent and global receiver activity
cannot be inferred from their absence.

The snapshot selects the full geographic range, all directions, a three-hour
evidence bin, non-joint evidence included, and VE6PDQ / DO34IR as the selected
path. These are presentation choices; the independent scientific configuration
is preserved. There are:

- Two station rows, with five Joint Spots in total. DO34IR has three Joint
  Spots and median 8 dB; DO34 has two and median 12 dB.
- Thirteen selected-path drilldown rows, including three Joint differences
  (7, 8 and 22 dB), and 34 full-segment drilldown rows.
- One 34-row, 11-column processed-evidence Parquet file.
- Four actual production PNGs: map, segment insight, segment temporal
  evidence and selected-station evidence. These were visually inspected.
- A production-saved configuration and generated run metadata, qualified as
  described above.

The generated `expected_metrics.json` and regression reports summarize this
snapshot's package shape and values. They are not independent expected
scientific results. Independent arithmetic, pairing, locator and paper-marker
tests remain in `test_milazzo_reference.py`. The integrity test does not compare
new renderer output pixel-for-pixel or substitute for those scientific checks.
The maintenance script rejects empty tables, missing required figures and a
missing/wrong-sized Parquet rather than recording an incomplete export as valid.

## Rebuild

From the repository root, using a new work directory and a new destination:

```powershell
.\.venv\Scripts\python.exe scripts/build_milazzo_prepared_export_fixture.py --work-directory tmp/milazzo_export_review --fixtures-directory tmp/milazzo_export_review/fixtures
```

Review the generated configuration, qualified provenance, all table rows,
independent-oracle checks and all four PNGs before replacing this snapshot.
The builder refuses to overwrite an existing destination. Export timestamps
and signatures may differ between runs; the numerical and package contracts
are the comparison targets. Local temporary absolute paths are omitted from
the committed manifest. Preserve this explanatory README when refreshing the
generated package.
