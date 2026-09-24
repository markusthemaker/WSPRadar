# G3ZIL / G4HZX Figure 3 temporal fixture

This is a pragmatic, paper-corroborated regression baseline for the first enabled demo. It preserves the numerical evidence behind the attached 24-hour and 3-hour Temporal Evidence screenshots. The companion `../../test_griffiths_temporal_reference.py` replays the production numerical path offline. Application runtime code is unchanged.

## Fixed case

- Target: G3ZIL, IO90HW; Reference: G4HZX, IO91; RX Benchmark, 40 m.
- UTC interval: 2017-04-01 00:00 inclusive to 2017-05-01 00:00 exclusive.
- Scope: Full Range | All Directions within the demo's 10,000 km geographic limit.
- Solar selection: all; special-callsign and moving-station exclusions off; minimum one Joint Spot per peer identity; no SNR offset.
- Frozen source: wspr.live capture from 2026-09-23, including historical decode-code provenance and dirty-working-tree source hashes in capture_provenance.json.
- Evidence unit: one retained same-cycle observation of the same transmitter callsign plus full locator at both receivers. The temporal summaries pool these Joint Spots; they are not station-balanced summaries.

## Reviewable numeric anchors

| Quantity | Fixed baseline |
| --- | ---: |
| Joint Spots | 57,767 |
| Joint transmitter identities | 792 |
| Mean Joint Spots per UTC day | 1,925.5666666667 |
| Full-window paired median | +7 dB |
| Full-window paired mean | +6.5490851178 dB |
| Full-window Q1 / Q3 | +3 / +10 dB |
| Daily bins | 30 |
| Three-hour bins | 240 |
| Folded UTC-hour bins | 24 |

Daily median Delta SNR, April 1 through April 30, in dB:

`2, 4, 3, 4, 5, 6, 5, 6, 5, 7, 6, 8, 8, 8, 9, 8, 8, 8, 8, 6, 6, 6, 7, 7, 8, 7, 6, 8, 7, 7`

The complete CSVs also preserve per-bin counts, means, quartiles and exact UTC bounds. Thus a wrong shape cannot pass merely by retaining the correct monthly median or count.

## Link to the paper and screenshots

[Griffiths and Squibb, Practical Wireless, October 2017, pp. 23-26](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf), Figure 3 and text on printed page 25, provides external corroboration. The authors report approximately 2,000 spots per day on average. The current 1,925.6/day is 3.72% below 2,000 and compatible with that rounded description; the publication does not establish an exact count or numerical tolerance. Same-transmitter/same-time selection makes paired comparisons the most plausible interpretation of the count.

The black scatter in Figure 3 represents Delta SNR. The blue squares represent soil moisture on the inverted right-hand axis; they are not an SNR average or median. Therefore none of our expected SNR values was digitized from the blue series. The early-April upward shift and recurring daily structure corroborate the observed temporal pattern. The paper does not print our 30 exact daily medians or 57,767 exact count.

The attached WSPRadar screenshots show daily medians/IQR and a 3-hour view over the same observations, with a +7 dB pooled reference line. Their folded UTC-hour panel should remain identical when changing the chronological bin size. Numeric expected values were extracted from frozen data rather than estimated from screenshot pixels. In particular, compressed axis spacing, colors and clipping are not numerical tolerances.

## Files

- `demo.config`, `analysis_context.json`: exact selected case.
- `input_sql_rows.parquet`: 125,759 SQL-aggregated rows before normal post-fetch filtering; input to the mandatory offline regression test.
- `source_rows.parquet`, `source_rows_query.sql`, `query_legacy.sql`: original endpoint observations and query provenance, retained for any later SQL-level test.
- `expected_paired_rows.parquet`: 57,767 sorted native paired units with time, peer identity, both normalized SNR components and Delta SNR.
- `expected_24h.csv`, `expected_3h.csv`, `expected_utc_hour.csv`: numeric curve summaries. Quartiles use linear interpolation at index `(n-1)*p`; even-sample medians average the two central values.
- `expected_density_*.csv`: exact histogram counts by temporal bin and 1 dB Delta-SNR bin. Raw counts are preferable to normalized colors as a scientific check; the renderer can normalize each panel by its maximum.
- `expected_summary.json`: fixed metadata, global anchors and scope limitations.
- `capture_provenance.json`: original source/date/provider/implementation provenance. Its file inventory describes the larger original capture, including files not repeated here; `manifest.json` is the completeness contract for this installed fixture.
- `verification.json`: historical pre-integration verification on 2026-09-24, when production calculations were compared against separately calculated fixture statistics. Its `test_module_added: false` records that earlier stage, not the current installed status.
- `manifest.json`: checksums for this fixture package.

## Installed regression test

1. Read the fixed config/context and `input_sql_rows.parquet`. Run the existing post-fetch filters and the same scope/paired-eligibility selection used by Segment Inspector. Do not query a live provider.
2. Rebuild native paired evidence through the production evidence builder. Compare sorted identities, times, both SNR components and Delta SNR against `expected_paired_rows.parquet`.
3. Build the existing 24-hour, 3-hour and folded-hour numerical profiles. Compare every bin count, median, Q1 and Q3 against the expected CSVs, and the density matrices against their expected count tables. The included means provide an additional human-readable/paper-comparison statistic; the displayed profile does not currently store means.
4. Require exactly 57,767 total Joint Spots and +7 dB global median. The count sum must be identical for every binning. Require one unchanged folded-hour result regardless of chronological bin selection.
5. Keep tests on numeric evidence and plot recipes, so font, color and layout changes do not masquerade as scientific regressions. Honor the renderer's minimum-support rules for displaying IQR and connected medians; storing a quartile for a sparse bin does not mean it must be drawn.

Integer counts, identities and times must match exactly. For this integer-dB dataset, medians and linear quartiles are exactly representable, so exact equality is appropriate. A small absolute roundoff allowance such as 1e-12 dB is sufficient if comparing arithmetic means or generic float arrays. Do not use a broad +/-1 dB tolerance for these frozen expectations.

Expectations must be immutable during tests and never regenerated automatically from the implementation being tested. An intentional change in method, population or bin semantics requires explicit review and a documented baseline update.

## Meaning of a failure

With identical frozen input and configuration, a changed numeric result is an unexpected behavior change and should fail regression testing until explained. It does not automatically prove the scientific method is false: a deliberate correction may appropriately change the baseline. Conversely, passing this case does not prove correctness for every dataset or experimental interpretation.

This fixture's exact expected values are a reviewed WSPRadar baseline with independently recomputed summary arithmetic and approximate paper corroboration. It is not an author-supplied independent numerical oracle. The installed regression starts after database aggregation; it covers post-fetch selection, Delta SNR construction and temporal binning, but not SQL execution. That scope is deliberate and keeps the first test small and useful.


## Running and maintaining the reference

Run from the repository root with the existing environment:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/regression/test_griffiths_temporal_reference.py -q
```

The module is also assigned once in `scripts/regression_test_chunks.json` and runs with the complete foreground regression runner. Required fixture files are mandatory; missing or corrupt data fails instead of skipping. The numerical production path is prepared once per module, with network connections blocked during its execution. Assertions reuse that result and never replace scientific functions with expected-output stubs.

The baseline also records the complete post-fetch population: 124,622 rows, comprising 57,767 Joint, 56,260 Only Target and 10,595 Only Reference rows, and 1,130 station rows before paired-only selection. These stage checks help locate filtering and eligibility regressions before inspecting the temporal differences.

The source and expected Parquet files are copied byte-for-byte from the reviewed capture. Text files use UTF-8 without BOM and LF line endings under a scoped Git attributes rule; the installed manifest hashes those canonical bytes. Keep source-revision and code hashes as historical provenance, not assertions against the current checkout. No automatic fixture-regeneration command is included. A reviewed change to fixture text or expected values must explicitly refresh its manifest entry; scientific expected values must never be regenerated merely to make a failing test pass.

Original capture commands and upstream artifacts used the earlier location under `tmp/`; the checked-in files here are self-contained and do not depend on that temporary directory. The source archive remains available for future SQL validation, but this module does not claim to execute SQL, validate the historical mode interpretation, test provider failover or recalculate normalization performed upstream in SQL.


## Integration verification (2026-09-24)

The new reference module and existing prepared-export integrity, segment temporal evidence, evidence-statistics and regression-runner modules passed together: **57 passed, 1 skipped, 1 existing Matplotlib warning in 28.07 seconds**. The prepared-export package remains absent and accounts for the skip; this reference is mandatory. Following explicit UTC handling in axis assertions, the reference module passed again: **8 passed, 1 existing warning in 9.61 seconds**, with **2.82 seconds** for its shared numerical preparation on the local Windows environment.

Four temporary in-memory faults were each rejected by the actual regression assertions: reversed Delta SNR, timestamps shifted by three hours, arithmetic means substituted for bin medians, and omission of the geographic filter. No application source or frozen expected values were modified for those fault checks. The chunk manifest contains all 82 discovered modules exactly once; changed-test compilation and patch whitespace checks passed. No full regression suite, browser run, live database request or ClickHouse execution was performed for this test-only integration.
