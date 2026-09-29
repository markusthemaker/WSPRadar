# Demo backlog

This folder holds draft saved configurations for possible future Guided demos.
They are not installed demos: `config/demo_profiles.py` discovers `*.config`
files only in the neighboring `config/demos/` directory.

| Draft | Intended example |
| --- | --- |
| `06_rx_local_median_neighborhood.config` | RX Reference Neighbourhood Benchmark. |
| `07_rx_calibration_ab.config` | RX calibration A/B. |
| `08_rx_hardware_ab.config` | RX hardware A/B. |

Scheduled sequential TX comparisons are not supported.

Before promoting a draft, review its scientific settings, current saved-config
schema compatibility, historical data availability and explanatory text. Check
its unique `profile.id`, English fallback text and any supplied German text.
Choose its filename deliberately: installed demos are ordered lexicographically
by filename. Move the reviewed configuration into `config/demos/` and verify the
demo-loading contracts and its intended analysis in the target environment.

Presence in this backlog is not a record of successful execution or approval for
publication. Keep frozen scientific reference inputs and expectations under
`tests/regression/reference_fixtures/`, and temporary investigations under the
ignored task workspace.
