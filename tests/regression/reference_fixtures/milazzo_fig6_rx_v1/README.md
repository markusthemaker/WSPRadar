# Milazzo Figure 6: reciprocal RX reconciliation

All 44 independently digitized Figure 6 markers match the user-supplied
wspr.rocks reports of **VE6PDQ transmitting to KP4MD and WB6RQN**: 31 blue
KP4MD receptions and 13 red WB6RQN receptions. Every annotated SNR matches
exactly; the largest time-readout difference is two minutes, inside the
original four-minute graphical tolerance. No vertical or horizontal shift was
fitted. All supplied 40 m reports inside the plotted date interval are matched.

The [article](https://www.qsl.net/kp4md/wspr.htm) and
[Figure 6 title](https://www.qsl.net/kp4md/WSPR%2040m%20at%20VE6PDQ.JPG)
describe reception **at VE6PDQ**. The numerical match instead identifies
reception **from VE6PDQ**. This is strong evidence of a direction-labelling
discrepancy, not proof that Figures 6 and 7 were swapped. The original chart
labels remain recorded in `paper_features_original.json`; its `receiver`
field records the printed claim, not the verified direction.

A subsequent [two-direction overlay review](../milazzo_publication_overlays_v1/README.md)
also matches 47 compact Figure 7 anchors to the TX direction at a common
37 dBm scale, supporting the suspected reversal of the two printed direction
labels. It flags one extra archive report absent from the visible Figure 7
markers and does not claim to resolve every overlapping marker. That follow-up
extends the direction evidence beyond the Figure 6-only reconciliation here.

Both original JPEGs and both overlay PNGs are now mandatory, hash-verified
files in that shared publication fixture during regression. The current SQL
is checked against all 44 RX and all 76 TX overlay reports using independent
source-row arithmetic; the Figure 7 comparison adds 47 executable paper anchors.

The existing `milazzo_tx_reference_v1` remains an independent test of the
installed TX demo. Its initial publication mapping used the printed direction
and therefore compared different observations. Those negative TX comparisons
do not establish archive loss or a WSPRadar calculation error. This companion
fixture supersedes the unresolved-direction conclusion, not its TX arithmetic.

## Inputs and independence

- `paper_markers.csv` and `paper_features_original.json` retain the exact bytes
  of the pre-existing source-only digitization, made before the reciprocal
  reports were supplied. The graphical tolerances have not been widened.
- `user_wb6rqn_reports.tsv` is the complete 52-row attached wspr.rocks paste,
  preserved byte for byte. It includes other bands and dates for selection
  checks.
- `user_kp4md_40m_rows.csv` transcribes all 34 40 m reports from the user's
  inline table, in its original relative order, preserving UTC, both callsigns,
  both locators, frequency, power and SNR. Its three reports after 20 December
  20:00 are excluded from Figure 6. Unrelated 20 m inline rows are not copied.
- `source_rows.csv` combines these 86 reports into an SQL-compatible input.
  Source-row keys are local provenance references, **not WSPRnet spot IDs**.
  No upstream IDs were supplied or invented. The paste says mode `unknown`,
  so `code` remains null rather than being assigned historical code 0 or 1.
- The displayed nominal 5 W is represented as the WSPR 37 dBm power level.
  Coordinates are independently calculated Maidenhead cell centers from the
  displayed locators, not original provider coordinates. This is not a
  coordinate precision or native ClickHouse distance-validation fixture.

`scripts/build_milazzo_rx_reference_fixture.py` uses only the Python standard
library. It reads the pasted reports and independently extracted markers,
never WSPRadar output. It writes exact grouped/native/pair expectations,
marker-to-source mappings and a summary. `rx_reference.config` is a fixture-only
RX configuration, not an added or modified installed demo.

## Pairing and conditioning are separate from graphical matching

The plot contains individual SNR reports. It does not contain 44 paired Delta
SNRs. Pairing uses exact 120-second cycles and the full transmitter callsign
and locator, without applying the graphical time tolerance to synchronization.

Eight cycles have reports at both receivers. Three have different reported
locator precision (`DO34` versus `DO34ir`): 19 December 23:24 and 23:46, and
20 December 10:46. Current WSPRadar identity rules preserve those as separate
one-sided units. Their nested grid cells do not establish identical physical
locations, and this fixture does not change the identity policy to force pairs.

The five eligible pairs are hand-checkable directly from published annotations:

| UTC | Full transmitter locator | KP4MD SNR | WB6RQN SNR | Delta SNR |
|---|---|---:|---:|---:|
| 19 Dec 14:46 | DO34ir | +2 | -6 | +8 |
| 20 Dec 07:46 | DO34 | -5 | -22 | +17 |
| 20 Dec 09:04 | DO34ir | -5 | -27 | +22 |
| 20 Dec 15:24 | DO34 | -6 | -13 | +7 |
| 20 Dec 15:46 | DO34ir | -10 | -17 | +7 |

Their median is +8 dB. These five selected pairs are not the distribution of
all Figure 6 points or an independently measured antenna gain. RX differences
include the receive chains and local noise as well as antenna/path effects.

The input contains only the VE6PDQ path. It does **not** establish full receiver
activity across other transmitters. Running the production Target-Active Gate
on this explicitly bounded input retains 34 native units: 26 Target-only,
five Joint and three Reference-only. Five Reference reports fall outside the
31 Target-active cycles observed in this subset. Their exclusion cannot be
claimed for a complete live RX demo, where other transmitters can establish
Target activity. All 44 paper reports are therefore checked before this gate.

## Executable checks

`test_milazzo_reference.py` verifies all frozen files and executes the current
generated RX SQL through the bounded SQLite adapter, followed by production
filtering, station aggregation and Inspector selection. It checks all 39 SQL
groups, every endpoint component, the 44 external paper anchors, all retained
native units and the five paired differences. Missing sides remain null.

The tests explicitly distinguish the printed TX claim from the matched RX
direction. Applying the TX query to these reciprocal inputs must yield no
rows. Receiver exchange and a one-dB SNR shift must fail the paper oracle;
merging coarse/fine locator identities must not create three extra pairs.
The suite neither contacts a live provider nor proves native ClickHouse
equivalence. It does not assume that the paste is the complete historical
archive or that a wrong-direction mismatch implies missing source data.

Recalculate into a separate candidate directory for review:

```powershell
.\.venv\Scripts\python.exe -S scripts/build_milazzo_rx_reference_fixture.py `
  --input-directory tests/regression/reference_fixtures/milazzo_fig6_rx_v1 `
  --output-directory tmp/milazzo_rx_candidate
```

Preserve the original source digitization and supplied rows. Never refresh
expectations from application results. The manifest hashes all fixture files;
the existing Git attributes preserve their bytes across platforms.
