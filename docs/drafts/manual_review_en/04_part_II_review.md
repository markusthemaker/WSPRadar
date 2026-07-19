# Part II Review — Controls and Troubleshooting

## Overall decision

Part II already fulfills its role well: exact controls, defaults, applicability, saved-state behavior and symptom-based diagnosis. Retain its chapter structure.

## Chapter 4 — Controls and Configuration

### 4.1 Workflow controls

Retain. The distinction between loaded demos, ordinary analyses, configurations and result exports is operator-relevant.

### 4.2 Core controls

Retain. Exact identity, band and time-window contracts belong here.

### 4.3 Benchmark controls

This is the authoritative home for the exact TX A/B schedule controls moved out of 1.4.

Add immediately after the schedule-control table:

- the Repeat Interval describes each physical path's actual recurrence;
- it is not necessarily the `Frame` label shown by a transmitter that alternates one output between paths;
- the preview must be checked against observed on-air starts and physical switch mapping.

Keep exact ranges, defaults, disjoint-phase behavior and automatic pairing here. Link to Appendix B for device-specific examples and to Sections 7.1/7.7 for exact pairing.

### 4.4 Filters and evidence thresholds

Retain exact behavior. Add one interpretation safeguard:

> Choose filters and evidence thresholds from the intended population and evidence floor. Do not relax them after inspecting the result solely to obtain a denser or more favorable map; report any changed analysis as a separate configuration.

### 4.5 Map, inspector and export controls

Retain. The present detail is justified because view settings affect saved inspection state and exported artifacts.

## Chapter 5 — Troubleshooting and Data Quality

### 5.1 Confirm the run definition first

Retain. This is the correct diagnostic entry point.

### 5.2 Diagnose by symptom

Retain the symptom tables and the distinction between upstream-data and experiment-design problems.

Relocate the long `System Audit Status` provider/cache explanation to Section 5.6. It is valuable operational information, but it interrupts symptom diagnosis and belongs with upstream source behavior.

### 5.3 Callsign and locator checks

Retain. Add no duplicate explanation beyond the short analysis-identity warning in 2.4.

### 5.4 Historical decode-code fallback

Retain. Its export limitation remains relevant to serious use.

### 5.5 Target-Active Gate

Retain. This is the operator-facing troubleshooting explanation; Chapter 7 remains authoritative for exact scientific behavior.

### 5.6 Working with upstream data

Retain the raw-data, delay and user-supplied-field warnings. Add a subheading `Read System Audit Status` and move the complete provider/cache explanation here.

The moved explanation remains detailed because it changes diagnosis: database origin, provider-selection reason and delivery tier are different concepts, and cached rows must not be mistaken for mixed-source evidence.
