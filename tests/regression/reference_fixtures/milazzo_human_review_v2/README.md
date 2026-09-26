# Milazzo MR01 revision 2: human-verified scientific regression reference

The user explicitly verified **P01–P10 and B01–B04 on 26 September 2026**.
`approval.json` preserves the approval statement, the 14 card decisions and the
hashes of the reviewed packet, card definitions, configurations and transcribed
numeric anchors. This is a human-reviewed archive reconstruction, not a claim
that the publication independently supplies every WSPRadar expectation.

`review_packet.pdf` and `review_cards.json` are byte-preserved copies of revision
2. Their pending-review wording records their state when generated. The separate
approval supersedes that wording; the original revision-1 and revision-2 authoring
packets and earlier decisions remain unchanged.

## Frozen scientific scope and evidence

- TX Performance: **KP4MD / CM98 -> peer RX stations**; 40 m; 19 December 2010
  12:00 UTC inclusive to 20 December 20:00 UTC exclusive; distance strictly below
  5,000 km; all directions and solar states; special callsigns and moving stations
  included; at least five opportunities per eligible receiver.
- TX Benchmark: **KP4MD / CM98 and WB6RQN / CM98 -> common peer RX**; the same
  32-hour window and geographic scope; no Reference SNR correction; at least one
  Joint observation per eligible receiver.
- `network_source.parquet` contains the complete frozen 40 m population of
  **65,647 raw reports** for the Performance window, including other transmitters
  and receivers needed for activity witnesses. It must not be replaced by a
  two-transmitter capture or the subset printed on the cards.
- `benchmark_source.csv` preserves the existing **1,992-report** two-transmitter
  capture, including reports outside the 32-hour review window. Production SQL
  must apply the frozen `benchmark.config` window. This source alone is not a
  complete Performance activity population.
- These historical sources contain decode code 0. Generated strict queries and
  the explicitly permitted legacy fallback are both exercised. This does not
  establish that every other historical dataset has identical mode semantics.

`network_capture.json`, `benchmark_capture_provenance.json`, the capture SQL and
`provenance.json` retain source and derivation history. Historical candidate-status
phrases inside copied provenance files do not override `approval.json`.

## Human anchors and independent supporting expectations

`reviewed_expectations.json` contains the fixed P01–P10 and B01–B04 numerical
anchors. `benchmark_expected.json` supplies the same B01–B04 mapping for the
existing Benchmark module. Performance anchors were preserved from the reviewed
card JSON; Benchmark anchors were transcribed from its reviewed arithmetic.

`performance_expected_ledger.csv`, `performance_expected_stations.csv`,
`performance_expected_profiles.json` and `benchmark_expected_native_units.csv`
are independently derived supporting evidence. They protect complete identities,
classification, SNR values and profile populations in addition to the printed
anchors. Human sign-off on the cards does not assert that every unprinted source
report or supporting value was individually inspected by the reviewer.

The application under test receives only raw reports and frozen configurations.
It must generate SQL, process its results, aggregate stations/maps and prepare
Inspector and figure data itself. Expected files are read only for assertions,
never as inputs to production preparation. No production snapshot or stored
figure recipe is used as the result being tested.

## Card coverage

| Cards | Protected contract |
| --- | --- |
| P01 | Named endpoint activity witnesses; Target-only success counted once; absent Target activity and unknown peer activity excluded |
| P02–P03 | VE6PDQ 57 successes / 79 opportunities, 22 Misses; successful SNR distribution |
| P04–P06 | Station-balanced versus pooled rates, distance summaries, Peer Reach including zero-success eligible receivers |
| P07 | Complete 3-hour selected-path counts, rate and successful-SNR quartiles |
| P08 | Represented-date means, zero-evidence date-hours and the exclusive final boundary; missing evidence never invents opportunities |
| P09 | One SNR vote per date-hour; sparse IQR visibility |
| P10 | Per-receiver full-window baselines; nine final-bin values, median +1.5 dB and IQR [-3,+3] dB; actual plotted marker |
| B01 | Raw pair identity, reported-power normalization and Target-minus-Reference sign |
| B02 | 30 station medians versus 45 Joint values, distribution statistics and +8 dB bar denominators |
| B03 | Station-history categories, actual footer/figure counts and distinct station/observation denominators |
| B04 | Map median of station medians, documented rounding, two receivers and three Joint observations |

The Performance module is `tests/regression/test_milazzo_human_performance.py`;
the Benchmark card tests extend `tests/regression/test_milazzo_reference.py`.
`coverage.json` maps every card to its exact pytest node and expectation key.
Both are mandatory members of the normal local regression suite. Preparation is
shared within a module to avoid replaying the complete source for every card.
Figure checks inspect scientific artist coordinates and quantities, not pixels,
font rasterization or unrelated visual style.

## Execution and change policy

Run the normal local suite with `scripts/run_regression.cmd` on Windows or
`python -m pytest tests/regression -q` on other platforms. The new fixture never
skips when inputs are missing and routine execution must not access the network.
Every new module belongs to exactly one fixed serial regression chunk. GitHub CI
is unchanged by this addition.

The routine SQLite adapter evaluates generated production SQL on frozen input
with bounded ClickHouse dialect adaptations. It does not prove native engine
semantics, provider availability or unchanging upstream archives. The separate
explicit `scripts/verify_milazzo_clickhouse.py` command queries a real configured
provider and compares its scientific query results with the frozen reference;
use it before completing a major development effort, not on every regression.
It never uploads this fixture or changes upstream data. A mismatch requires
investigation of query behavior and possible upstream archive drift.

The command defaults to both analyses. `--analysis performance` and
`--analysis benchmark` explicitly select two strict/fallback queries; their
reports identify the limited scope and cannot claim a complete four-query pass.
Use `--provider` to name the source being compared. Coordinate metadata can
differ across providers even when report identities and SNRs agree, so a
cross-provider mismatch must be investigated rather than silently tolerated.

`benchmark_native_sql_capture.csv` and `benchmark_native_capture.sql` preserve
the original native provider capture; their hashes were verified against the
existing capture provenance before promotion. This supplementary machine-captured
reference is not an independent scientific oracle or additional human approval.
After clipping to the reviewed window, its identities and scientific columns
must agree with the independently checked offline replay. Only its
`best_ref_dist` diagnostic supplies a native baseline: ClickHouse's native
`geoDistance` and the offline adapter's spherical approximation differ. The
live comparison then checks every returned column, including that diagnostic,
without weakening the SNR/count tolerances or silently dropping a column.
The archived Float32 peer coordinates are compared at their source precision,
so CSV's shorter decimal representation does not create a false mismatch.

Never regenerate approved expectations from current production output merely to
make a failure pass. Deliberate scientific changes require a new fixture revision,
an explanation and renewed human review. Preserve the previous approved revision.
Fixture manifests protect accidental changes; they are checksums, not a digital
signature or independent proof of scientific validity.
