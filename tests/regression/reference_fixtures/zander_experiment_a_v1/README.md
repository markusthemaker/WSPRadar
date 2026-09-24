# Zander Experiment A: independent archive reference

This mandatory offline reference reconstructs the installed simultaneous TX Hardware A/B demo from frozen original reports. It complements the separate [Figure 4 paper fixture](../zander_fig4_paper_v1/README.md), whose expectations were extracted independently from the publication.

## Fixed population and independent expectations

- Target SK0WE/P, Reference SK0WE/1, both constrained to JO97, 20 m / 14 MHz.
- UTC interval 2022-05-21 09:30 inclusive to 10:30 exclusive; strict `code = 1` selection.
- All directions and solar states, Target-centered radius strictly below 10,000 km, minimum one joint observation per receiver identity, no SNR offset or station exclusions.
- One peer identity is receiver callsign plus its complete reported locator; pairing uses a common 120-second UTC cycle.
- Each endpoint contributes its maximum normalized SNR, `snr - power + 30`, within that identity/cycle. Both transmitters report 23 dBm throughout this capture, so normalization cancels in the paired difference. This is reported-power consistency, not independent power calibration.

The provider capture contains 731 rows, including one `code = 4` report. Strict mode retains 730 source reports and produces 564 SQL groups. Global Target activity and geographic selection retain 457 groups: 166 Joint, 36 Only Target and 255 Only Reference. There are 85 retained receiver identities; 37 contribute Joint observations over 12 joint cycles. No eligible endpoint group has duplicate reports.

The exact Joint population has mean -6.783132530120482 dB, sample standard deviation 3.51463845382668 dB, median -7 dB, Q1 -9 dB, Q3 -4 dB, and range -17 to +4 dB. Of 166 differences, 162 are negative, two zero and two positive. The mean of the 37 receiver medians is -6.054054054054054 dB, demonstrating why the Station Medians histogram is a different comparison from the Joint-Spot histogram.

Expectations were calculated by [build_zander_reference_fixture.py](../../../../scripts/build_zander_reference_fixture.py), which imports only the Python standard library and reads the raw CSV and frozen configuration. It does not import WSPRadar or read application-produced rows. Dictionary grouping, maximum selection, explicit UTC cycle arithmetic, spherical geometry, sorted quartiles and `statistics.stdev` provide the independent calculation. CSV coordinates retain the original Parquet Float32 values without premature rounding. There is no ambiguous within-group receiver coordinate in this source population.

The exact date, hour, callsigns and count are archive/demo reconstruction facts; the paper does not publish them. The selected population is fixed, not searched or adjusted to fit the paper's histogram. The original capture provenance identifies a dirty working tree and clearly labels its application outputs as observations rather than independent expected results.

## Executable coverage

The test module `../../test_zander_experiment_a_reference.py`:

1. Verifies mandatory manifests; missing or altered input fails. Network access is blocked.
2. Builds current production SQL from the frozen demo and executes it against the frozen source rows in an in-memory SQLite table named `wspr.rx`. It removes only `FORMAT CSVWithNames` and supplies `any`, `maxIf`, `countIf`, `argMaxIf`, timestamp and distance functions. The original source predicates, UNION, grouping, SNR expressions, conditional aggregation and LIMIT execute as SQL.
3. Compares every scientific SQL row with the independent expected table and the archived native ClickHouse response. Diagnostic `best_ref_dist` is excluded: the adapter uses spherical distance and does not reproduce ClickHouse's distance approximation. Coordinates in the captured CSV are restored to their original Float32 precision for this comparison.
4. Runs production post-fetch eligibility, map/station aggregation, Inspector identity selection, native paired evidence, and the actual Segment Insight histogram recipe. Compares selected groups, all paired identities and both SNR components, and exact 1 dB Joint histogram counts.
5. Checks the rendered right-hand bars are percentages of the Joint sample and distinct from the station-median panel. The external paper tests rebin the right-hand recipe's counts into the independently measured paper intervals, converting to density per dB.
6. Exercises assertion sensitivity to incorrect mode selection, omitted power normalization, reversed differences, a 1 dB offset and station weighting substituted for pooled observations.

The test executes generated aggregation SQL, but the compatibility functions do not validate native ClickHouse engine semantics, aggregate ties or provider behavior. The source has no duplicate endpoint groups, so it does not add a real-world duplicate-selection example. The captured native ClickHouse response provides an additional historical cross-check, not a replacement for a live engine integration test.

## Files and maintenance

`source_rows.parquet`, the capture query and provenance preserve the original provider response. `source_rows.csv` is a lossless numerical projection for standard-library calculation and portable SQL replay. `captured_query_strict.sql` and `captured_sql_output.csv` preserve the former application query/response as supplementary evidence. The independent `expected_*` tables preserve SQL groups, retained groups, native pairs with original source IDs, station summaries and the full 1 dB histogram. `analysis_context.json` and `demo.config` pin the scientific configuration.

To review a deliberate baseline update, run the builder into a separate directory:

```powershell
.\.venv\Scripts\python.exe scripts/build_zander_reference_fixture.py --source-csv tests/regression/reference_fixtures/zander_experiment_a_v1/source_rows.csv --config tests/regression/reference_fixtures/zander_experiment_a_v1/demo.config --output-directory tmp/zander_reference_candidate
```

Tests never regenerate expected results or paper annotations. Review any differences before replacing data and updating manifest hashes. Preserve the separation between independently computed archive expectations and paper-derived evidence.
