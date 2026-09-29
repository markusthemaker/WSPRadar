# Reference workflow regression debrief

Recorded on 2026-09-28 for the current-contract Reference workflow simplification.

## Initial integrated result

The first complete regression run exited with status **1**: **22 failed, 3328
passed, 3 xfailed, 1 warning in 511.52 seconds**. The run was not a passing
verification of the integrated changes.

The approved scope removes sequential TX analysis and old configuration
compatibility, merges the fixed-Reference choices, discovers Reference location
from the selected archive scope, and validates incomplete inputs when Run is
pressed. The relay scheduler was preserved outside the WSPRadar codebase and
the repository's `tools/` directory was removed.
These scope decisions were already authorized; none of the failures below
requires another user decision.

The table records all **22 failed parameterized executions**, grouped where they
share a cause. Test names are the names reported by the initial run, including
names subsequently changed or removed. Module names refer to
`tests/regression/test_<module>.py`. Corrections are implemented. A focused
subsequent run covering every initial failure module and the additional runtime
regressions **passed: 1,139 tests in 176.09 seconds**. This verifies the current
replacement coverage; removed obsolete tests were not rerun under their old
contracts. The subsequent complete integrated run also passed: **3,330 passed,
3 existing expected failures, 1 existing warning in 466.35 seconds**, exit 0.

## The 22 failed executions

| Cases | Module and initial test name | Verified cause | Correction and retained contract |
| --- | --- | --- | --- |
| 1 | `absolute_time_window::test_app_blocks_submission_while_entry_time_window_is_invalid` | Obsolete source-text assertion required Run to be disabled for an invalid window. Run now remains available to show actionable validation. | Removed the obsolete source-shape test. Date/window unit validation remains; the Classic AppTest below presses Run and checks that invalid windows produce errors without submission. |
| 2–3 | `benchmark_mode_defaults::test_classic_compact_control_labels_are_bilingual` — English and German | Stale expected-label dictionaries still required the removed `cfg_min_joint_pairs` key. | Removed the scheduled-pair expectation and unused manual Reference-locator label expectation. Exact current compact labels remain checked in both languages. |
| 4–5 | `config_migration::test_local_neighborhood_accepts_supported_localized_median_state` — English and German | Compatibility success tests still expected localized UI text to be converted into canonical `local_median` state. That conversion was explicitly removed. | Replaced with `test_local_neighborhood_rejects_localized_labels_as_canonical_state`; both localized inputs must raise `LocalBenchmarkValidationError`. Canonical `local_median` remains supported. |
| 6 | `guided_input_flow::test_offset_establishment_guidance_explains_estimator_choice_and_sign` | A German text assertion still expected `Joint-Spots / geplante Paare` after sequential-pair guidance was removed. | Expect `Joint-Spots`. Estimator choice, station versus observation weighting, correction sign, neutral calibration and subsequent validation assertions remain. |
| 7 | `guided_input_integration::test_guided_run_validates_incomplete_inputs_and_save_requires_readiness` | The new subprocess probe attempted to read `application.session_state.filtered_state`, which is not supported by the AppTest session-state wrapper. The probe failed before returning validation evidence. | Read the named `_input_field_errors` key with a membership guard and `run_mode` directly. Retain actual Run-click validation and Save-readiness assertions. |
| 8 | `guided_input_integration::test_classic_run_reports_missing_design_and_save_waits_for_readiness` | Same shared AppTest probe failure as case 7. | Same probe correction; retain missing-design feedback and Save-readiness assertions. |
| 9 | `guided_input_integration::test_classic_invalid_windows_are_reported_and_blocked_before_submission` | Same shared AppTest probe failure as case 7. | Same probe correction; retain actual invalid-window Run clicks, field errors and blocked-submission assertions. |
| 10 | `guided_input_integration::test_letter_only_archive_identity_is_valid_in_guided_and_classic_inputs` | Same shared AppTest probe failure as case 7. | Same probe correction; retain acceptance of valid letter-only archive identities in both input views. |
| 11 | `guided_input_integration::test_stale_warning_preserves_the_ready_rerun_action` | Same shared AppTest probe failure as case 7. | Same probe correction; retain stale-result warning and ready rerun-action assertions. |
| 12 | `idle_import_boundary::test_idle_browser_component_payloads_preserve_json_transport` | Expected navigation payload omitted the new optional `focusFieldKey` field. | Include `focusFieldKey: None` in the expected payload. JSON transport and idle import-boundary assertions remain. |
| 13–14 | `inspector_selection_state::test_active_selection_record_retains_automatic_versus_empty_intent` — `None-None` and `configured_stations1-expected_stations1` | Fixtures used the retired `15m` configuration bin. | Use supported `10m`, preserving automatic-selection versus explicitly empty-selection intent assertions. |
| 15 | `inspector_session_cache::test_compare_shared_bin_policy_retains_explicit_fine_bin_for_long_window` | Fixture used the retired `5m` configuration bin. | Use supported `10m`. Continue checking that an explicit fine-bin choice survives the shared bin policy. |
| 16 | `inspector_session_cache::test_performance_models_key_only_on_an_off_tier_retained_bin` | Fixture used retired `5m`; replacing it with `10m` also requires a longer window because `10m` is an ordinary offered choice at 24 hours. | Use `10m` with a 31-day window, preserving the intended test of an explicit bin outside that window's offered tier and its cache identity. |
| 17 | `page_navigation::test_page_navigation_controller_passes_stable_anchor_and_request_contract` | Expected component payload omitted `focusFieldKey`. | Include `focusFieldKey: None`; preserve stable destination, anchor, request-token and transport assertions. |
| 18 | `page_navigation::test_runtime_anchors_bound_the_top_settings_and_results_regions` | Structural test assumed a single navigation request. There are now two deliberate paths: valid Run to results, and invalid Run to the parameters and first invalid field. | Select calls by destination and verify both requests, with the input focus field on the validation path. |
| 19 | `result_hierarchy::test_dynamic_result_values_are_escaped_at_the_html_boundary` | The callsign-injection fixture used a Benchmark subtitle that does not render that callsign; the escaped callsign was therefore absent, rather than rendered unsafely. | Exercise callsign escaping through the Performance subtitle that renders it. Keep the separate Benchmark figure-title injection check and metadata escaping assertions. |
| 20–21 | `run_controller_data_source::test_malformed_numeric_csv_restarts_complete_bundle_on_wd2` — `False` and `True` demo variants | The test response still represented the removed sequential schema. Its first same-cycle rewrite omitted mandatory `best_ref_sign` and `best_ref_dist`, so the first RX response failed schema validation before the intended malformed TX numeric response. | Supply a complete same-cycle response and inject the malformed value into `snr_u_norm`. Retain complete provider restart, invalidated cache and ordinary/demo variant assertions. |
| 22 | `success_evidence_rework::test_success_temporal_recipe_retains_legacy_bin_only_when_explicit` | Fixture used the retired `15m` configuration bin. | Use supported `10m` and rename the test around an explicit off-tier bin. Preserve the distinction between an explicit retained choice and automatic bin selection. |

The five AppTest failures were five executions of one broken test probe, not
evidence of five separate application defects. Likewise, the retired-bin cases
did not establish a numerical binning error: their inputs violated the newly
approved configuration contract. The updated tests exercise the current
behavior and passed in the focused subsequent run. No exact traceback text is
reconstructed here.

## Separate runtime findings from review

The following issues were found by implementation review and contract audit.
They are **additional findings, not additional members of the 22 failures**.
Their corrections and added regressions passed in both the focused subsequent
run and the complete integrated run.

| Finding | Concrete failure condition | Implemented correction and verification target |
| --- | --- | --- |
| Reference discovery provider leaked into Performance | After a fixed-Reference Benchmark, changing to Performance while retaining otherwise matching discovery inputs could reuse the saved discovery provider. That could pin a Performance run to the former provider and interfere with its ordinary failover behavior. | [`resolved_discovery_source`](../ui/reference_location_state.py) now returns a discovery provider only for `reference_station`. [`test_reference_location.py`](../tests/regression/test_reference_location.py) checks discovery ownership and that Performance does not inherit the provider. |
| Negative discovery could remain stuck across explicit Run attempts | A saved Target-location mismatch or empty Reference lookup could be reused indefinitely, even after a later explicit Run should permit a fresh archive query. | [`resolve_reference_before_analysis`](../ui/reference_location.py) refreshes terminal negative results on explicit Run. Valid single-location and multiple-location chooser state remains stable for resume. [`test_reference_location_ui.py`](../tests/regression/test_reference_location_ui.py) covers the negative refresh and positive-state distinction. |
| Unknown scientific configuration fields were silently discarded | `AnalysisContext.from_dict` could accept obsolete or misspelled fields by ignoring them, contradicting the current-contract-only boundary. | [`AnalysisContext.from_dict`](../core/analysis_context.py) rejects unknown fields. [`test_analysis_runner_contracts.py`](../tests/regression/test_analysis_runner_contracts.py) covers rejection, current defaults and round trip. |
| Explicit unbounded query/session cache lifetimes lost their rejection guard | Removing old TTL aliases also removed the guard against explicitly passing `None` for query or session cleanup TTLs. | [`cleanup_artifact_namespaces`](../core/artifact_store.py) rejects `None` for those two lifetimes; the separately permitted demo lifetime policy remains. [`test_artifact_store.py`](../tests/regression/test_artifact_store.py) covers both rejected parameters. |
| Retired fetched-row shape still influenced Target-evidence detection | `has_target_evidence` still accepted the obsolete fetched `is_me` column as evidence, although current processed Performance and Benchmark rows use `target_seen` and `has_u`. | [`has_target_evidence`](../core/analysis_runner.py) reads the two current schemas and returns false for unknown or retired shapes. [`test_decode_filter_fallback.py`](../tests/regression/test_decode_filter_fallback.py) checks this boundary. This removes an obsolete result reader; it does not remove legitimate internal SQL side-marker expressions or historical archive decode handling. |

## Verification record

| Stage | Result |
| --- | --- |
| First complete integrated run | Exit 1; 22 failed, 3328 passed, 3 xfailed, 1 warning; 511.52 seconds. |
| Focused subsequent run | Exit 0; 1,139 passed, 1 existing Matplotlib pending-deprecation warning; 176.09 seconds. Included every initial failure module and the new location, validation, navigation, context, TTL and source-ownership coverage. |
| Listed expectation, fixture and probe corrections | Current replacement coverage passed in the focused subsequent run. |
| Five review-discovered runtime corrections | Implemented with regression coverage; passed in the focused subsequent run. |
| Extracted standalone relay tool | 32 passed in 0.57 seconds outside WSPRadar. The repository `tools/` directory is absent. This is separate from application regression coverage. |
| Complete integrated verification | `.\scripts\run_regression.cmd --tb=short`; exit 0; 3,330 passed, 3 xfailed, 1 existing Matplotlib pending-deprecation warning; 466.35 seconds. |
| Final bounded input follow-up | Exit 0; 10 passed in 33.88 seconds. `test_input_validation_state.py` and the Guided/Classic `test_invalid_windows_are_reported_and_blocked_before_submission` cases verify errors, actual field-outline markup, blocked submission, and clearing after time correction. Invalid UTC windows now mark both time fields as well as both dates; an unused schedule-formatting helper and obsolete schedule docstring were removed. |
| Final structural checks | Full Python compilation and `git diff --check` passed. Regression manifest covers 90 modules exactly once across five serial chunks. Generated README matches the authoritative English manual. |

All 22 initial failures are resolved under the approved current contracts.
The complete-run case count differs from the initial run because obsolete
feature tests were removed, the relay tests moved to the standalone project,
and current-contract regressions were added. The three strict expected failures
remain the documented Griffiths paper comparisons whose raw-report weighting
differs from WSPRadar's maximum-per-receiver evidence policy. Frozen scientific
fixtures and numerical expectations were not changed to obtain a passing run.

The browser check also caught and corrected initial focus landing on an input's
help button. Navigation now prioritizes the actual input control. Browser
verification confirmed red-field rendering, focus, correction clearing, the
Reference callsign placeholder and the absence of a manual Reference-grid field.
Streamlit's local health endpoint returned HTTP 200. Archive discovery was tested
with controlled provider responses; the standalone tests did not operate USB
hardware.

## Subsequent bounded UI and documentation follow-up

After the complete integrated run above, the requested follow-up shortened the
four Guided analysis-choice descriptions, removed the optional Reference context
field and its saved-config contract, and made Reference Setup/Station the default
for an empty Benchmark selection while preserving an existing Neighbourhood
choice. Both input editors now place Reference selection on the left and the
fixed Reference callsign with SNR correction below it on the right. The input
panel no longer displays a Reference-location caption before discovery. Location
discovery, explicit selection between ambiguous grids, and Target-QTH mismatch
validation remain covered.

Section 2.3.1 retains the distinction between a controlled Reference setup and an
independent Reference station without tying it to an input field. The overview
table now wraps its full labels within their cells in English and German.

| Follow-up check | Result |
| --- | --- |
| Initial focused configuration, discovery, input and documentation run | 934 passed, 1 failed, 1 existing warning; 116.49 seconds. The sole failure expected the removed German context-option label. Its replacement checks the retained setup-versus-station explanation in Section 2.3.1. This is separate from the original 22 failures above. |
| Final input and documentation rerun | 510 passed, 1 existing Matplotlib pending-deprecation warning; 110.41 seconds. Covers both languages and editors, actual column/widget placement, one correction widget, correction persistence through Guided navigation, explicit zero-correction selection, validation navigation, localization, documentation rendering and PDFs. |
| Frozen-demo and export contract checks | 7 passed, 1 existing Matplotlib pending-deprecation warning; 44.15 seconds. Griffiths, Vanhamel calibration and rotation, Zander and Milazzo configuration/population checks plus correction metadata export. Frozen scientific input bytes and numerical expectations remain unchanged. |
| Browser and structural checks | Running-app English/German overview labels remained inside their table cells. Changed Python scopes compiled, generated README was synchronized, and whitespace checks passed. The temporary verification server stopped and task scratch files were removed. |

These bounded follow-ups were verified with the affected tests. The earlier
3,330-pass complete-suite record applies to the integrated state before these
follow-ups; it is not presented as a second full-suite run of the final UI state.
