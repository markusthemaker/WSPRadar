# Milazzo TX reference: independent archive arithmetic

This fixture checks the current demo's scientific selection and calculations
against an independent, standard-library calculation from frozen raw reports.
It is not a claim that WSPRadar reproduces the publication's plotted SNR series
or its antenna-performance conclusion. The publication comparison is separate
and preserves the initial wrong-direction comparison for traceability. All
44 Figure 6 markers now reconcile with reciprocal RX observations in
[milazzo_fig6_rx_v1](../milazzo_fig6_rx_v1/README.md), contradicting the figure's
printed direction. That RX reconciliation does not validate this TX dataset.

The subsequent [Figure 7 TX overlay](../milazzo_publication_overlays_v1/README.md)
provides a separate publication check for this receiver path: 47 compact
image-derived anchors agree with the current SQL components at a common
37 dBm scale. The overlay retains all 76 archive reports in the plotted window
and flags an extra report with no visible paper marker. It does not replace
this fixture's independent arithmetic or claim that every overlapping paper
marker was resolved.

The Figure 7 comparison is now executable in `test_milazzo_reference.py`:
47 independent paper anchors, all 76 TX reports within the plotted interval,
the unplotted report and the near-overlapping reports are checked separately.
The original Figure 7 JPEG and its overlay PNG are mandatory, hash-verified
files in the linked shared publication fixture.

## Frozen inputs and provenance

The source is the complete captured 40 m population for transmitter callsigns
KP4MD and WB6RQN, from 2010-12-18 00:00 UTC inclusive through 2010-12-21 00:00 UTC
exclusive. The bounded query returned 1,992 reports from `https://db1.wspr.live/`
on 2026-09-23. `source_rows_query.sql` retains the exact raw query. It selected
both endpoint callsigns before locator, geographic, mode-code, activity, or
duplicate filtering. Its 1,000,001-row limit was not approached.

`source_rows.parquet` is byte-identical to the provider capture. In
`source_rows.csv`, timestamps are explicit ISO UTC and the captured float32
coordinates were promoted to float64 before serialization. This preserves the
binary values actually received; it does not claim greater geographic accuracy.
The independently calculated distance uses those preserved coordinates.

`capture_provenance.json` preserves the historical capture record, including
the then-dirty checkout and implementation observations. These observations
never supply the independent expected values. Its hashes describe files in
the original capture directory, not renamed or newline-normalized files here.
`analysis_context.json`, `query_legacy.sql`, and `query_strict.sql` preserve
scientific context and query provenance. The copied `demo.config` includes the
subsequently corrected demo explanation with unchanged scientific settings.
`provenance.json` records this fixture's transformation and scope. Historical
runtime and builder hashes are provenance, not a requirement that current
production code retain identical source bytes.

All captured reports have decode code 0. The captured strict code-1 query
returned no rows; the legacy query omitted the code predicate. This fixture
therefore explicitly covers the historical legacy population. It does not
prove a modern decode-code interpretation or automatic provider fallback.

The user's later wspr.rocks cross-check also supplies the TX direction.
`user_kp4md_tx_reports.tsv` preserves the complete 90-row attachment unchanged;
its 63 40 m reports match every captured KP4MD-to-VE6PDQ report.
`user_wb6rqn_tx_40m_rows.csv` transcribes all 26 40 m reports from the user's
inline WB6RQN-to-VE6PDQ table in its original relative order. Together they
match all 89 captured reports on this receiver path in UTC, endpoint callsigns
and full locators, SNR and nominal power (5 W = 37 dBm; 2 W = 33 dBm).
This is corroboration through another view of archive data, not an independent
measurement or proof of separate provider provenance. Displayed mode is
unknown; the cross-check does not infer a mode code, compare unavailable
upstream IDs/coordinates, or replace the original provider capture. Frequency
is used only to select 40 m because the original capture stores band, not MHz.

## Independent calculation

`scripts/build_milazzo_reference_fixture.py` imports only Python's standard
library. It reads `source_rows.csv` and `demo.config`, with no WSPRadar imports
and no prepared application outputs. The calculator deliberately accepts only
this bounded TX/reference-station contract:

1. Select the configured 40 m window, endpoint transmitters in locator CM98,
   and receiver latitude unequal to zero. All 1,992 frozen reports qualify.
2. Group by 120-second UTC cycle, complete receiver callsign, and complete
   receiver locator. Preserve endpoint report counts and source IDs. Normalize
   each report as `SNR - reported power dBm + 30`, and take each endpoint's
   maximum normalized value within a group. There are no duplicate endpoint
   groups in this capture, so it does not independently exercise duplicate
   competition. Coordinate ambiguity fails rather than choosing a row.
3. Establish global Target activity from all qualifying KP4MD reports before
   the receiver-distance filter. A Reference-only receiver group survives the
   activity gate only if KP4MD was heard by some qualifying receiver in that
   cycle. Record all source-report witnesses for every active cycle.
4. Retain groups strictly below 5,000 km from the independently decoded CM98
   cell center, latitude 38.5 degrees and longitude -121 degrees. Distance uses
   spherical haversine with radius 6,371 km. Group exclusion reasons are
   ordered: inactive Target first, then distance. They are mutually exclusive.
5. Preserve all retained Target-only, Joint, and Reference-only native units.
   Only Joint units have a finite Delta SNR, calculated Target minus Reference.
   Missing endpoint components remain null. A missing-side zero in the SQL
   aggregate is a transport convention, not an observed zero-dB measurement.

| Selection stage | Target-only | Joint | Reference-only | Total groups |
| --- | ---: | ---: | ---: | ---: |
| Before global Target-Active Gate | 1,093 | 46 | 807 | 1,946 |
| Target-active, before distance | 1,093 | 46 | 21 | 1,160 |
| Target-active, below 5,000 km | 1,069 | 45 | 21 | 1,135 |

The radius excludes 24 Target-only groups and one Joint group. There are 179
globally Target-active cycles, 80 retained receiver identities, and 30 receiver
identities with paired evidence. The 45 Joint units occur in nine cycles; their
median Delta SNR is -4 dB, mean is approximately -3.9556 dB, and quartiles are
-6 and -2 dB. These units are paired evidence, not 45 independent controlled
antenna experiments.

## Complete ledgers and numerical files

- `expected_sql_rows.csv`: all 1,946 independently calculated grouped rows;
  the nine scientific aggregation columns omit auxiliary reference metadata.
- `expected_classified_groups.csv`: every grouped identity, endpoint source
  IDs, normalized components, independent geometry, activity state, outcome,
  and retained/excluded reason.
- `expected_source_ledger.csv`: every one of the 1,992 source IDs exactly once,
  with original fields, raw SNR and power, normalization, full grouped identity,
  endpoint maximum status, outcome, and selection reason. Non-joint and
  excluded reports remain inspectable.
- `expected_active_cycles.csv`: all 179 Target-active cycles and every Target
  report witnessing that activity. Activity does not depend on a selected
  receiver or on the subsequent radius filter.
- `expected_retained_rows.csv`: all 1,135 rows surviving activity and distance.
- `expected_native_units.csv`: all 1,135 retained units, including absent-side
  nulls and non-joint evidence. `expected_paired_rows.csv` contains the 45 Joint
  units with the same columns and their raw endpoint SNR/power components.
- `expected_station_rows.csv`: all 80 receiver identities, directional unit
  counts, Joint Evidence Share, and descriptive paired statistics. The share
  denominator is all retained native units of that receiver.
- `expected_coverage_3h.csv`: 24 complete three-hour bins for all receivers and
  another 24 for VE6PDQ. Each bin records directional counts, station breadth,
  pooled Joint Evidence Share, and the arithmetic mean of per-station shares.
  Empty-bin shares are null. Bin start is inclusive and end exclusive.
- `expected_summary.json`: selection-stage counts and descriptive statistics.

CSV nulls are empty fields; they must not become zero-valued observations.
Joint Evidence Share describes pairability, not an antenna success score or a
symmetric comparison of operating schedules. The independent station-balanced
coverage column is supplemental arithmetic and is not a claim that every
application view displays that statistic.

## VE6PDQ hand-check

The capture has 89 VE6PDQ reports at full locator DO34ir: 63 KP4MD and 26
WB6RQN. Global Target activity excludes 25 WB6RQN-only reports. The retained
evidence is 62 Target-only units and one Joint unit, with no Reference-only
unit. None of those 62 Target-only reports is discarded merely for lacking a
paired Reference observation.

At 2010-12-20 00:22 UTC, Target report 44698904 has SNR -13 dB and power 37 dBm,
so its normalized SNR is `-13 - 37 + 30 = -20 dB`. Reference report 44698905 has
SNR -15 dB and power 33 dBm, giving `-15 - 33 + 30 = -18 dB`. Their paired
difference is therefore `-20 - (-18) = -2 dB`. The raw-SNR difference of +2 dB
would answer a different question because the reported powers differ.

## Publication boundary and maintenance

[Milazzo's technical article](https://www.qsl.net/kp4md/wspr.htm) motivates the
demo. The `publication_*` files preserve separately extracted publication
facts and marker coordinates, all eligible archive candidates under their
frozen matching rules, and the resulting disagreements. A nearby timestamp
does not prove that an archive row is the same plotted observation. Alternative
power conventions and time shifts are labeled diagnostics, not automatically
accepted matches. See `publication_mapping.md` for that separate assessment.
The publication image is not redistributed in this fixture because its reuse
permission has not been established.

This package checks independent archive arithmetic and supports offline replay;
it does not itself claim that a particular SQL engine was executed. The
regression module states which production stages it actually exercises.
Historical capture success is not a substitute for a current test result.

## Executable regression

`tests/regression/test_milazzo_reference.py` is mandatory and runs offline.
It executes the current generated strict and legacy SQL over the frozen raw
reports through the bounded SQLite compatibility adapter. It verifies the
historical empty-strict-result retry predicate, then exercises production
post-fetch filtering, station aggregation, Inspector evidence selection,
Drill-Down with non-joint evidence both shown and hidden, and chronological
coverage preparation. It does not execute the live provider retry dispatcher
or establish native ClickHouse engine equivalence.

All grouped and retained identities and SNR components are checked, including
all one-sided observations and their absent-side nulls. The tests link every
raw report to its independently recorded outcome or exclusion, retain the
fifty station identities without paired evidence, check both global activity
witnesses and inactive cycles, and distinguish the 5,000 km population from
the unrestricted counts. Complete three-hour coverage counts and pooled versus
station-balanced shares are checked for the full scope and VE6PDQ. An explicit
activity-removal control must remove every receiver in the affected cycle.

The publication audit checks are limited to complete candidate enumeration and
linkage to actual retention outcomes. They do not turn the wrong-direction SNR
differences into a passing publication agreement test. The reciprocal RX checks
in the same test module provide the external Figure 6 agreement. The source CSV is also
compared field by field with the original Parquet capture to protect portable
replay from serialization loss.

To review a recalculation, write into a separate candidate directory:

```powershell
.\.venv\Scripts\python.exe -S scripts/build_milazzo_reference_fixture.py `
  --source-csv tests/regression/reference_fixtures/milazzo_tx_reference_v1/source_rows.csv `
  --config tests/regression/reference_fixtures/milazzo_tx_reference_v1/demo.config `
  --output-directory tmp/milazzo_reference_candidate
```

Compare generated expectations explicitly. Never regenerate expected results
inside a test or silently replace publication bounds with application output.
The builder rejects destinations inside the installed reference-fixture tree
or equal to the input-file directories. Explicit input checks remain active
under optimized Python, preventing bypass of the bounded scientific contract.
`manifest.json` inventories the completed package; missing or altered inputs
must fail instead of skipping validation. Calculator-generated expectations and
fixture metadata use UTF-8 with LF endings. Publication source files retain
their original bytes, including the marker CSV's CRLF endings; generated
publication mapping CSVs also use deterministic CRLF. The fixture's Git
attributes disable text conversion so all recorded hashes remain portable.
