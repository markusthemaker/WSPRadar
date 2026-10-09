"""
Lokalisierungs-Modul (i18n) für WSPRadar.
Enthält alle Text-Strings für die Mehrsprachigkeit (DE/EN).
"""
from config import APP_VERSION


T = {
    "en": {
        "fig_tx_abs": 'TX Performance: {callsign} — Target Heard vs. Other Signals Heard Only',




        'fig_joint_spot_count': "Joint spot count",
        'fig_relative_joint_spot_density': "Relative joint-spot density (% of panel maximum)",

        'lbl_time_aggregation_bin_size': "Select time aggregation bin size",
        'lbl_report_delta_snr_outlier_candidates': "Report ΔSNR outlier candidates",
        'tt_report_delta_snr_outlier_candidates': """Flag **unusual ΔSNR departures** for closer inspection, using supporting observations **before and after** each candidate. This adds a report; it does not remove evidence or identify a cause.""",
        'lbl_delta_snr_outlier_minimum_departure_db': "Minimum absolute ΔSNR departure (dB)",
        'tt_delta_snr_outlier_minimum_departure_db': """Minimum difference, in either direction, between a candidate’s **median ΔSNR** and its **surrounding baseline**. Lower values flag smaller departures.""",
        'lbl_delta_snr_outlier_minimum_robust_z': "Minimum robust z-score",
        'tt_delta_snr_outlier_minimum_robust_z': """Minimum departure relative to the **robust spread** of the surrounding evidence. Higher values require the departure to stand out more strongly from that variability.""",
        'lbl_delta_snr_outlier_maximum_baseline_difference_db': "Maximum pre/post baseline difference (dB)",
        'tt_delta_snr_outlier_maximum_baseline_difference_db': """Largest allowed difference between the **baselines before and after** a candidate. Lower values require a more stable background.""",
        'btn_reset_delta_snr_outlier_detector_defaults': "Reset detector defaults",
        'lbl_delta_snr_outlier_detector_thresholds': "Outlier detector thresholds",
        'fmt_delta_snr_outlier_detector_thresholds': "Departure ≥ {departure:g} dB · robust z ≥ {robust_z:g} · pre/post baseline difference ≤ {baseline_difference:g} dB",
        'fig_delta_snr_outlier_candidate': "ΔSNR outlier candidate",
        'fig_segment_chronological_delta': "\u0394 SNR over Time",
        'fig_segment_utc_hour_title': "\u0394 SNR by UTC Hour (1 h bins)",
        'fig_selected_compare_chronological_title': "\u0394 SNR over Time",
        'fig_selected_compare_folded_title': "\u0394 SNR by UTC Hour",
        'fig_rx_comp_temporal_prefix': "RX Benchmark Temporal",
        'fig_tx_comp_temporal_prefix': "TX Benchmark Temporal",
        'fig_segment_chronological_x': "Date/Time (UTC)",
        'fig_segment_utc_hour_x': "UTC hour",
        'fig_segment_dates_folded': "{count} UTC dates folded",
        'fig_segment_folded_unavailable': "UTC-hour pattern unavailable - requires paired evidence from at least 2 UTC dates.",
        'fig_compare_chronological_unavailable': "No paired Δ SNR evidence is available in the selected UTC window.",
        'fig_compare_coverage_title_rx': "RX Benchmark Temporal Evidence Coverage: Target {callsign}",
        'fig_compare_coverage_title_tx': "TX Benchmark Temporal Evidence Coverage: Target {callsign}",
        'fig_compare_coverage_chronological_title': "Evidence Coverage over Time ({time_bin} bins)",
        'fig_compare_coverage_utc_hour_title': "Evidence Coverage by UTC Hour (1 h bins)",
        'fig_compare_coverage_folded_unavailable': "UTC-hour pattern unavailable — requires Benchmark evidence from at least 2 UTC dates.",
        'fig_compare_coverage_station_y_rx': "TX Stations",
        'fig_compare_coverage_station_y_tx': "RX Stations",
        'fig_compare_coverage_station_folded_y_rx': "Avg. TX Stations",
        'fig_compare_coverage_station_folded_y_tx': "Avg. RX Stations",
        'fig_compare_coverage_unit_y_rx': "Transmitter-Cycles",
        'fig_compare_coverage_unit_y_tx': "Receiver-Cycles",

        'fig_compare_coverage_unit_folded_y_rx': "Avg. Transmitter-Cycles",
        'fig_compare_coverage_unit_folded_y_tx': "Avg. Receiver-Cycles",

        'fig_compare_joint_share_station': "Station-balanced Joint Evidence Share",
        'fig_compare_joint_share_outcome': "Outcome-level Joint Evidence Share",
        'fig_compare_joint_share_y': "Joint Evidence (%)",
        'fig_compare_coverage_gate_simultaneous': """WSPR cycles without evidence that the Target was operating are left out, so possible Target downtime is not counted as a loss.\nOnly Target and Only Reference are therefore not symmetric. Joint Evidence Share shows pair coverage within those same cycles.""",

        'fig_selected_compare_coverage_title_rx': "RX Benchmark Selected Path Evidence Coverage: {station} ({locator})",
        'fig_selected_compare_coverage_title_tx': "TX Benchmark Selected Path Evidence Coverage: {station} ({locator})",
        'fig_selected_compare_coverage_chronological_title': "{unit} over Time ({time_bin} bins)",
        'fig_selected_compare_coverage_utc_hour_title': "{unit} by UTC Hour (1 h bins)",
        'fig_selected_compare_coverage_unit_simultaneous': "Retained WSPR Cycles",

        'fig_selected_compare_coverage_unit_y_simultaneous': "WSPR Cycles",
        'fig_selected_compare_coverage_unit_folded_y_simultaneous': "Avg. WSPR Cycles",
        'fig_selected_compare_joint_share': "Joint Evidence Share",
        'fig_selected_compare_coverage_unavailable': "No retained Benchmark outcomes are available for this selected path.",
        'fig_selected_compare_coverage_unavailable_multi': "Selected Path Evidence Coverage is available only for one selected path; the combined ΔSNR evidence remains available above.",
        'fig_success_temporal_title_rx': "RX Performance Temporal Evidence: Target {callsign}",
        'fig_success_temporal_title_tx': "TX Performance Temporal Evidence: Target {callsign}",
        'fig_success_temporal_snr_title_rx': "RX Performance Temporal SNR Evidence: Target {callsign}",
        'fig_success_temporal_snr_title_tx': "TX Performance Temporal SNR Evidence: Target {callsign}",
        'fig_success_selected_station_snr_title_rx': "RX Performance Selected Station SNR Evidence: {station} ({locator})",
        'fig_success_selected_station_snr_title_tx': "TX Performance Selected Station SNR Evidence: {station} ({locator})",
        'fig_success_selected_station_temporal_title_rx': "RX Performance Selected Station Temporal Evidence: {station} ({locator})",
        'fig_success_selected_station_temporal_title_tx': "TX Performance Selected Station Temporal Evidence: {station} ({locator})",
        'fig_success_reach_title_rx': "TX Stations Heard by Target at Least Once by Distance",
        'fig_success_reach_title_tx': "RX Stations Hearing the Target at Least Once by Distance",
        'fig_success_reach_y_rx': "Qualifying TX stations heard by Target at least once (%)",
        'fig_success_reach_y_tx': "Qualifying RX stations that heard Target at least once (%)",
        'fig_success_consistency_title_rx': "RX Decode Rate by TX-Station Distance",
        'fig_success_consistency_title_tx': "TX Decode Rate by RX-Station Distance",
        'fig_success_snr_distance_title_rx': "Successful Target SNR by TX-Station Distance",
        'fig_success_snr_distance_title_tx': "Successful Target SNR by RX-Station Distance",
        'fig_success_distance_x': "Distance from Target QTH (km)",
        'fig_success_rate_y': "Decode Rate (%)",
        'fig_success_snr_y': "Station-median successful Target SNR (dB @ 30 dBm)",
        'fig_success_confirmed_opportunities': "Confirmed opportunities",
        'fig_success_qualifying_stations': "Qualifying stations",
        'fig_success_successful_snr_stations': "Stations with successful SNR",
        'fig_success_station_balanced': "Station-balanced Decode Rate",
        'fig_success_observation_level': "Opportunity-level Decode Rate",
        'fig_success_median': "Median",
        'fig_success_iqr': "IQR (3+ stations)",
        'fig_success_two_station_range': "Min-Max (2 stations)",
        'fig_success_support': "Support",
        'fig_success_support_title': "Evidence Support by Distance",
        'fig_success_bin_width': "Bin width: {width_km:g} km",
        'fig_success_locator_precision_note': "Calculated distance inherits the precision of reported locators; a four-character Maidenhead locator does not provide survey-grade positioning.",
        'fig_success_snr_chronological_title_rx': "Successful RX SNR Deviation over Time",
        'fig_success_snr_chronological_title_tx': "Successful TX SNR Deviation over Time",
        'fig_success_snr_utc_hour_title_rx': "Successful RX SNR Deviation by UTC Hour",
        'fig_success_snr_utc_hour_title_tx': "Successful TX SNR Deviation by UTC Hour",
        'fig_success_evidence_chronological_title': "Evidence over Time ({time_bin} bins)",
        'fig_success_evidence_utc_hour_title': "Evidence by UTC Hour (1 h bins)",
        'fig_success_station_votes_y_rx': "TX Stations",
        'fig_success_station_votes_y_tx': "RX Stations",
        'fig_success_station_support_folded_y_rx': "Avg. TX Stations",
        'fig_success_station_support_folded_y_tx': "Avg. RX Stations",
        'fig_success_opportunities_y': "Opportunities",
        'fig_success_opportunities_folded_y': "Avg. Opportunities",
        'fig_success_rate_legend': "Decode Rate",
        'fig_success_time_x': "Date/Time (UTC)",
        'fig_success_utc_hour_x': "UTC hour",
        'fig_success_snr_anomaly_y_rx': "Deviation from each TX station’s run median (dB)",
        'fig_success_snr_anomaly_y_tx': "Deviation from each RX station’s run median (dB)",
        'fig_success_snr_density': "Relative density of station-level SNR deviations",
        'fig_success_station_baseline': "Each station’s run median (0 dB)",
        'fig_success_bin_median_chronological': "Median across stations",
        'fig_success_bin_median_folded': "Median across stations and dates",
        'fig_success_selected_snr_chronological_title': "Successful Target SNR over Time",
        'fig_success_selected_snr_utc_hour_title': "Successful Target SNR by UTC Hour",
        'fig_success_selected_temporal_snr_y': "Normalized Target SNR (dB @ 30 dBm)",
        'fig_success_selected_snr_density': "Relative density of successful Target SNR",
        'fig_success_selected_folded_median': "Median across represented dates",
        'fig_success_selected_snr_unavailable': "No successful Target SNR is available for this station. Missed signals have no recorded Target SNR.",
        'lbl_selected_time_aggregation_bin_size': "Select time aggregation bin size:",
        'fig_success_selected_bin_median': "Bin median",
        'fig_success_snr_anomaly_unavailable': "Successful-SNR anomaly unavailable — requires at least 3 successful Target SNR observations per station.",
        'fig_success_temporal_unavailable': "UTC-hour pattern unavailable — requires evidence from at least 2 UTC dates.",
        'fig_success_utc_dates_folded': "{count} UTC dates folded",
        'fig_compare_median_focus_axis': "\u0394 SNR (dB \u00b7 median-centered nonlinear)",
        'fig_median_label': "Median",
        'fig_temporal_bin_median': "Bin median",
        'fig_temporal_bin_iqr': "Bin IQR (middle 50%)",

        'tbl_col_joint_pairs': "Joint Pairs",

        'tbl_col_micro_a': "Target Micro-Median",
        'tbl_col_micro_b': "Reference Micro-Median",
        'tbl_col_pair_delta': "Pair \u0394",
        "btn_demo": "Load Demo",
        "btn_load_config": "Load Config",
        "btn_save_config": "Save Config",
        "btn_prepare_config": "Prepare Config",
        "btn_download_config": "Download Config",
        "txt_config_profile_intro": "Add reusable profile details, then prepare the config download.",
        "lbl_config_profile_title": "Title",
        "lbl_config_profile_description": "Description (optional)",
        "lbl_config_profile_id": "Profile ID (optional)",
        "hlp_config_profile_id": "Leave blank to derive a stable ID from the title.",
        "warn_saved_station_unavailable": "The saved station selection could not be restored because this station is not available in the current Station Insights table: {stations}. No substitute was selected.",
        "msg_config_prepared": "Config prepared. Download it below.",
        "btn_apply_config": "Load Selected Config",
        "btn_load_demo_selected": "Load Selected Demo Configuration",
        "btn_run_demo_selected": "Run Selected Demo",
        "btn_prepare_all_results": "Prepare All Results for Download",
        "btn_download_prepared_results": "Download Prepared Results",
        "btn_share_analysis": "Share Analysis",
        "share_url_field": "Analysis URL",
        "share_copy_link": "Copy Link",
        "share_copied": "Link copied.",
        "share_manual_copy": "The URL is selected. Copy it manually.",
        "share_native": "Share\u2026",
        "share_native_failed": "Browser sharing was unavailable. Copy the selected URL instead.",
        "share_email": "Email",
        "share_whatsapp": "WhatsApp",
        "share_x": "X",
        "share_facebook": "Facebook",
        "share_linkedin": "LinkedIn",
        "share_analysis_title": "WSPRadar analysis: {callsign} {direction} {mode} on {band}",
        "share_analysis_message": "Open this link to reconstruct and rerun the analysis with the current WSPRadar code and upstream data.",
        "help_share_analysis": """:primary[**Share Analysis**] creates a link that loads the current analysis settings and supported Inspector choices, then reruns the analysis. Use `Copy Link` or a sharing option to send it.

Choose **Download Evidence** to share the retained observations, tables, and figures from this completed run.""",
        "help_share_analysis_limits": """The link contains settings, not a frozen result package. The recipient runs the analysis with the then-current WSPRadar code and available archive data, so the result may differ.""",
        "share_mode_performance": "Performance",
        "share_mode_reference_station": "Reference Setup/Station",
        "share_mode_local_neighborhood": "Reference Neighborhood",
        "hdr_results_compare": "{direction} Benchmark Results",
        "hdr_results_success": "{direction} Performance Results",

        "sub_results_rx_success": "Target {callsign} · signals heard by the Target or by others only",
        "sub_results_tx_success": "Target {callsign} · Target heard or other signals heard only at active RX stations",
        "txt_results_metadata": "{band} · {utc_window} · Target QTH {qth}",
        "txt_results_reference_grid4": "Reference Locator {grid4}",
        "txt_results_shared_grid4": "Shared Locator {grid4}",
        "txt_results_reference_benchmark": "Reference benchmark {benchmark}",
        "txt_results_configured_snr_correction": "Configured SNR correction: {correction_db} dB applied to {recipient}",
        "txt_results_snr_correction_reference_identity": "Reference ({callsign})",
        "txt_results_snr_correction_reference_schedule": "Reference schedule",
        "txt_results_snr_correction_reference_benchmark": "Reference benchmark",
        "fmt_results_thousands_separator": ",",
        "lbl_results_evidence_path": "Evidence path",
        "txt_results_evidence_path": "Map → Segment Inspector → Station Insights → Drill-Down",
        "txt_results_evidence_path_success": "Map → Segment Inspector → Station Insights → Drill-Down",
        "lbl_results_level_run": "Complete run",
        "lbl_results_level_scope": "Geographic scope",
        "lbl_results_level_stations": "Contributing stations",
        "lbl_results_level_selection": "Selected stations",
        "lbl_results_level_selection_success": "Selected station",
        "lbl_results_level_rows": "Row-level evidence",
        "hdr_results_map_view": "Map View",
        "sub_results_map_compare": "Geographic overview of station-balanced ΔSNR and Decode Outcomes.",
        "sub_results_map_success": "Remote {station_type} stations grouped by distance and direction, showing the Station-balanced Decode Rate.",
        "hdr_results_segment_inspector": "Segment Inspector",
        "sub_results_segment_inspector": "Choose one or more distance ranges and directions. All evidence below follows the active scope.",
        "lbl_results_distance_range": "Distance range",
        "lbl_results_direction": "Direction",
        "txt_results_active_scope": "Active scope · {distance} · {direction}",
        "txt_results_evidence_scope": "Evidence in scope · {station_count} · {evidence_count} {evidence_unit}",
        "txt_results_transition_scope": "↓ Select distance and direction to inspect a geographic scope",
        "txt_results_transition_stations": "↓ Select one station to inspect its evidence",
        "txt_results_transition_stations_multi": "↓ Select one or more stations to inspect their evidence",
        "txt_results_transition_stations_success": "↑ Select one station to inspect its evidence",
        "txt_results_transition_rows": "↓ Review the underlying evidence rows",
        "hdr_results_comparison_evidence": "Benchmark Evidence",
        "sub_results_comparison_evidence_joint": "Decode Outcomes, station medians, and joint-spot ΔSNR for the active scope.",

        "fmt_results_station_delta_summary": "Stations{count_context} · Median {median} dB · Mean {mean} dB",
        "fmt_results_joint_spot_delta_summary": "Spots{count_context} · Median {median} dB · Mean {mean} dB",

        "lbl_results_stations": "Stations",
        "lbl_results_spots": "Spots",

        "hdr_results_temporal_evidence": "Temporal Evidence",
        "sub_results_temporal_evidence": "Absolute ΔSNR, paired-evidence coverage and UTC-hour patterns for the active scope.",
        "hdr_results_outlier_report": "Outlier Report",
        "sub_results_outlier_report": "Native ΔSNR excursions with shared qualification gates, qualifying-path summaries and chronological cycle evidence for the active scope.",
        "msg_outlier_report_insufficient_paired_evidence": "No {paired_evidence} are available in the active scope, so no path-level ΔSNR candidate can be evaluated.",
        "msg_outlier_report_insufficient_local_baseline": "None of the {populated} {paired_evidence} in the active scope had a supported candidate-excluded local baseline; all {abstained} native paired units were left unclassified.",
        "msg_outlier_report_no_candidates": "None of the {assessed} native paired units with a supported local baseline formed a qualifying ΔSNR excursion; {abstained} of {populated} {paired_evidence} lacked baseline support and remain unclassified.",
        "msg_outlier_report_invalid_detector_settings": "Outlier reporting is unavailable because the detector thresholds are invalid. Correct the advanced settings and run a new analysis.",
        "btn_outlier_show_path_in_station_insights": "↓ Show in Station Insights",
        "btn_outlier_show_drilldown_details": "↓ Show Drill-Down Details",
        "btn_outlier_show_all_paths_in_station_insights": "Show all qualifying paths in Station Insights",
        "txt_outlier_event_spot_impulse": "Spot impulse",
        "txt_outlier_event_short_burst": "Short burst",
        "txt_outlier_event_sustained_excursion": "Sustained excursion",
        "txt_outlier_event_mixed_duration": "Mixed-duration excursions",
        "fmt_outlier_path_heading": "Path {index} · {identity} · {direction}",
        "fmt_outlier_candidate_timeframe": "Timeframe {utc_range}",
        "fmt_outlier_joint_count_singular": "1 Joint Spot",
        "fmt_outlier_joint_count_plural": "{count} Joint Spots",


        "fmt_outlier_path_observation_context": "{paired_count} · first-to-last span {first_to_last_span} · median interval {median_interval} · largest gap {largest_gap}",
        "fmt_outlier_path_delta_context": "- **Expected local ΔSNR:** {expected_local} dB\n- **Observed median ΔSNR:** {observed_median} dB\n- **Largest single-cycle departure:** {largest_departure} dB",
        "txt_outlier_paired_evidence_joint": "Joint Spots",

        "exp_outlier_wspr_cycle_evidence": "Chronological WSPR-cycle evidence · {utc_range}",

        "col_outlier_evidence_utc": "UTC",
        "col_outlier_evidence_path": "Path",
        "col_outlier_evidence_direction": "Direction",
        "col_outlier_evidence_delta_snr": "ΔSNR (dB)",
        "col_outlier_evidence_local_baseline": "Local baseline (dB)",
        "col_outlier_evidence_residual": "Residual (dB)",
        "col_export_outlier_event_id": "Event ID",
        "col_export_outlier_combined_event_class": "Combined event class",
        "col_export_outlier_event_first_evidence_utc": "Event first evidence UTC",
        "col_export_outlier_event_last_evidence_utc": "Event last evidence UTC",
        "col_export_outlier_cross_path_context": "Cross-path context",
        "col_export_outlier_departure_direction": "Departure direction",
        "col_export_outlier_qualifying_path_count": "Qualifying path count",
        "col_export_outlier_path_event_id": "Path event ID",
        "col_export_outlier_path_number": "Path number",
        "col_export_outlier_path_occurrence": "Path event number",
        "col_export_outlier_path": "Path",
        "col_export_outlier_callsign": "Callsign",
        "col_export_outlier_locator": "Locator",
        "col_export_outlier_direction": "Direction",
        "col_export_outlier_path_event_class": "Path event class",
        "col_export_outlier_path_first_evidence_utc": "Path first evidence UTC",
        "col_export_outlier_path_last_evidence_utc": "Path last evidence UTC",
        "col_export_outlier_paired_unit_type": "Paired evidence type",
        "col_export_outlier_paired_unit_count": "Paired evidence count",
        "col_export_outlier_first_to_last_span_minutes": "First-to-last span (min)",
        "col_export_outlier_median_evidence_interval_minutes": "Median evidence interval (min)",
        "col_export_outlier_largest_gap_minutes": "Largest gap (min)",
        "col_export_outlier_expected_local_delta_snr_db": "Expected local ΔSNR (dB)",
        "col_export_outlier_observed_median_delta_snr_db": "Observed median ΔSNR (dB)",
        "col_export_outlier_largest_single_unit_departure_db": "Largest single-cycle departure (dB)",
        "col_export_outlier_episode_robust_z_score": "Robust z-score",
        "col_export_outlier_pre_event_baseline_delta_snr_db": "Pre-event baseline ΔSNR (dB)",
        "col_export_outlier_post_event_baseline_delta_snr_db": "Post-event baseline ΔSNR (dB)",
        "col_export_outlier_absolute_pre_post_baseline_difference_db": "Absolute pre/post baseline difference (dB)",
        "col_export_outlier_agreeing_paired_unit_count": "Agreeing paired evidence",
        "col_export_outlier_paired_unit_sign_agreement_fraction": "Paired-evidence sign agreement fraction",
        "col_export_outlier_decode_edge_warning": "Decode-edge warning",
        "col_export_outlier_decode_edge_warning_reason": "Decode-edge warning reason",
        "col_export_outlier_nearby_joint_unit_count": "Nearby Joint evidence",
        "col_export_outlier_nearby_target_only_unit_count": "Nearby Only Target evidence",
        "col_export_outlier_nearby_reference_only_unit_count": "Nearby Only Reference evidence",
        "col_export_outlier_unit_sequence": "Evidence sequence",
        "col_export_outlier_utc": "UTC",
        "col_export_outlier_target_snr_db": "Target SNR (dB)",
        "col_export_outlier_corrected_reference_snr_db": "Corrected Reference SNR (dB)",
        "col_export_outlier_delta_snr_db": "ΔSNR (dB)",
        "col_export_outlier_departure_from_local_baseline_db": "Departure from local baseline (dB)",
        "col_export_outlier_cycle_robust_z_score": "Cycle robust z-score",
        "col_export_outlier_meets_strong_anchor_gates": "Meets strong-anchor gates",
        "col_export_outlier_reported_boundary": "Reported boundary",
        "txt_export_outlier_scope_path_specific": "Path-specific",
        "txt_export_outlier_scope_directionally_coherent": "Directionally coherent",
        "txt_export_outlier_scope_scope_wide": "Scope-wide",
        "txt_export_outlier_scope_multiple_paths": "Multiple paths",
        "txt_export_outlier_departure_positive": "Above local baseline",
        "txt_export_outlier_departure_negative": "Below local baseline",
        "txt_export_outlier_departure_mixed": "Mixed",
        "txt_export_outlier_departure_neutral": "No signed departure",
        "txt_export_outlier_paired_unit_joint": "Joint Spot",

        "txt_export_outlier_yes": "Yes",
        "txt_export_outlier_no": "No",
        "txt_export_outlier_boundary_start": "Start",
        "txt_export_outlier_boundary_end": "End",
        "txt_export_outlier_boundary_start_and_end": "Start and end",
        "txt_export_outlier_warning_reference_missing": "Reference missing near positive event",
        "txt_export_outlier_warning_target_missing": "Target missing near negative event",
        "txt_outlier_direction_unavailable": "Not available",
        "fmt_outlier_minutes": "{value} min",
        "fmt_outlier_evidence_utc": "{timestamp} UTC",
        "fmt_outlier_utc_date": "{day:02d}-{month} {time}",
        "fmt_outlier_utc_instant": "{timestamp} UTC",
        "fmt_outlier_utc_range": "{start}–{end} UTC",
        "txt_outlier_utc_months": "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec",
        "lbl_include_unpaired_evidence": "Include Unpaired Evidence",
        "hdr_results_success_evidence": "Performance Evidence",
        "sub_results_success_evidence": "Decode Rate and successful-signal strength by calculated distance for the active scope.",
        "sub_results_success_temporal": "Successful signal-strength deviations, station support, confirmed-opportunity volume and Decode Rate weightings shown chronologically and by UTC hour.",
        "sub_results_station_insights": "Contributing {station_type} stations in the active scope. Select one row to inspect its evidence.",
        "sub_results_station_insights_multi": "Contributing {station_type} stations in the active scope. Select one or more rows to inspect their evidence.",
        "sub_results_station_insights_success": "Contributing {station_type} stations in the active scope. Select one row to inspect its evidence.",
        "txt_results_station_scope": "Active scope · {distance} · {direction} · {station_count}",
        "hdr_results_selected_station_evidence": "Selected Station Evidence",
        "lbl_results_selected_station_named": "{selected_count} selected {station_type} stations: {stations}",
        "lbl_results_selected_station_count": "{selected_count} selected {station_type} stations",
        "sub_results_selected_station_single": "{station} ({locator}) · {evidence_count} {evidence_unit}",
        "sub_results_selected_station_named": "{selection_label} · combined view · {evidence_count} {evidence_unit}",
        "sub_results_selected_station_multi": "{selection_label} · combined view · {evidence_count} {evidence_unit}",
        "fmt_success_selected_context": "{station} ({locator}) · {distance_km} km · {azimuth_degrees}° {direction}\n{confirmed_opportunities} {opportunity_unit} · Decode Rate {success_rate}% · Median Target SNR {median_snr}",
        "abbr_compass_east": "E",
        "txt_results_selected_no_paired_evidence": "No paired evidence is available for this selection; retained unpaired rows can still be audited below.",
        "hdr_results_drilldown": "Drill-Down Data",
        "sub_results_drilldown_single": "Row-level evidence for {station} within the active scope.",
        "sub_results_drilldown_multi": "Row-level evidence for {count} selected {station_type} stations within the active scope.",
        "lbl_drilldown_zoom_window": "Zoom window",
        "lbl_drilldown_center_date_utc": "Center date (UTC)",
        "lbl_drilldown_center_time_utc": "Center time (UTC)",
        "btn_drilldown_zoom_earlier": "← Earlier",
        "btn_drilldown_zoom_later": "Later →",
        "lbl_drilldown_zoom_off": "Off",
        "lbl_drilldown_zoom_outlier_focus": "Outlier Focus",
        "fmt_drilldown_zoom_time_window": "{identity} - Time Window: {start} to {end} UTC",
        "fmt_drilldown_zoom_selected_window": "Selected window: {start} to {end} UTC",
        "txt_drilldown_zoom_single_station_only": "Zoomed evidence is available only when exactly one station is selected.",
        "fig_drilldown_native_performance_panel_title": "Successful Target SNR over Time",
        "fig_drilldown_native_benchmark_panel_title": "Δ SNR over Time",
        "fig_drilldown_native_time_x": "Date/Time (UTC)",
        "fig_drilldown_native_performance_y": "Normalized Target SNR (dB @ 30 dBm)",
        "fig_drilldown_native_benchmark_y": "Δ SNR (dB)",
        "fig_drilldown_native_performance_unavailable": "No successful Target SNR is available in this time window. Unsuccessful opportunities have no recorded Target SNR.",
        "fig_drilldown_native_benchmark_unavailable": "No paired Δ SNR evidence is available in this time window.",
        "fig_drilldown_native_joint_spot": "Individual Joint Spot",

        "fig_drilldown_native_successful_opportunity": "Individual successful confirmed opportunity",
        "fig_drilldown_outlier_candidate": "Outlier candidate",
        "fig_drilldown_outlier_focused_episode": "Focused episode",
        "fig_drilldown_outlier_expected_local_delta_snr": "Expected local ΔSNR",
        "fig_drilldown_outlier_flank_baseline": "Pre/post flank baseline",
        "fmt_drilldown_outlier_robust_z_guide": "|robust z| = {value:g}",
        "fmt_drilldown_outlier_qualifying_robust_z_guide": "|robust z| = {value:g} (qualifying threshold)",
        "fmt_drilldown_outlier_absolute_departure_gate": "Absolute-departure gate (±{value:g} dB)",
        "lbl_filter_table": "Filter table",
        "txt_results_drilldown_filter_note": "Filter table changes only the displayed table; Zoom window limits both the focused plots and table, never the completed analysis.",
        "unit_joint_spot_singular": "joint spot",
        "unit_joint_spot_plural": "joint spots",


        "unit_confirmed_opportunity_singular": "confirmed opportunity",
        "unit_confirmed_opportunity_plural": "confirmed opportunities",
        "unit_station_singular": "{count} contributing {station_type} station",
        "unit_station_plural": "{count} contributing {station_type} stations",
        "hdr_results_download_evidence": "Download Evidence",
        "sub_results_download_evidence": "Prepare the completed run, active Inspector scope, station selection, tables, metadata, and high-resolution figures as a reproducibility package; Save Config preserves reusable analysis settings separately.",
        "sub_documentation": "Method, interpretation, controls, limitations, and troubleshooting.",
        "msg_preparing_all_results": "Preparing high-resolution result package...",
        "btn_prepare_documentation_pdf": "Prepare PDF",
        "btn_download_documentation_pdf": "Download PDF",
        "btn_load_full_documentation": "Load full documentation",
        "btn_hide_full_documentation": "Hide full documentation",
        "msg_loading_analysis_engine": "Preparing analysis engine...",
        "msg_preparing_inspector": "Preparing Segment Inspector and Drill-Down data...",
        "msg_preparing_documentation_pdf": "Preparing documentation PDF...",
        "help_documentation_pdf_unavailable": "PDF export requires the documentation PDF dependencies.",
        "msg_export_queue_wait": "Another export is being prepared. You are position {position} in the export queue.",
        "msg_export_queue_detail": "{active}/{maximum} export preparation active; {queued} waiting.",
        "warn_export_queue_full": "High demand right now. The export queue is full. Please try again shortly.",
        "warn_export_queue_timeout": "Export capacity did not become available in time. Please try again shortly.",
        "btn_reset": "Reset Config",
        "btn_run_analysis_rx": "Run RX Analysis",
        "btn_run_analysis_tx": "Run TX Analysis",
        "btn_select_analysis_direction": "Select RX or TX Analysis",
        "cbar_abs_rx": "Station-balanced RX Decode Rate (%)",
        "cbar_abs_tx": "Station-balanced TX Decode Rate (%)",
        "map_success_footer_opportunities": "OPPORTUNITIES",
        "map_success_footer_stations": "STATIONS",
        "success_rx_opportunity_success": "Heard by Target",
        "success_rx_opportunity_counter": "Heard by others only",
        "success_rx_station_success": "Heard by Target",
        "success_rx_station_counter": "Heard by others only",
        "success_rx_target_only_audit": "Heard by Target only (included in successes)",
        "success_rx_show_counter": "Heard only by other stations.",
        "success_tx_opportunity_success": "Target heard",
        "success_tx_opportunity_counter": "Other signals heard only",
        "success_tx_station_success": "Target heard",
        "success_tx_station_counter": "Other signals heard only",
        "success_tx_target_only_audit": "Target heard only (included in successes)",
        "success_tx_show_counter": "Only other signals heard.",
        "map_success_rx_opportunity_target": "Heard by Target",
        "map_success_rx_opportunity_counter": "Heard by others only",
        "map_success_rx_station_target": "Heard by Target",
        "map_success_rx_station_counter": "Heard by others only",
        "map_success_tx_opportunity_target": "Target heard",
        "map_success_tx_opportunity_counter": "Other signals heard only",
        "map_success_tx_station_target": "Target heard",
        "map_success_tx_station_counter": "Other signals heard only",
        "map_success_legend_insufficient": "Insufficient evidence",
        "cbar_comp": "Station-balanced median \u0394SNR (dB)",
        "comp_title_ref": "{callsign} (Reference)",
        "comp_title_local_median": "Local Median Neighborhood (≤{radius} km)",
        "dev_credit": f"Release {APP_VERSION} | Repo: <a href='https://github.com/markusthemaker/WSPRadar/' target='_blank' style='color:#39ff14; text-decoration:none;'>GitHub</a> | License: <a href='https://github.com/markusthemaker/WSPRadar/blob/main/LICENSE' target='_blank' style='color:#39ff14; text-decoration:none;'>AGPLv3</a><br>Developed by Dr. Markus Brosch (<a href='https://www.qrz.com/db/DL1MKS' target='_blank' rel='noopener noreferrer' aria-label='DL1MKS on QRZ.com (opens in a new tab)' style='color:#39ff14; text-decoration:none; white-space:nowrap;'>DL1MKS<span aria-hidden='true' style='display:inline-block; color:#39ff14; font-size:0.95em; font-weight:700; line-height:1; margin-left:0.18em; text-decoration:none; vertical-align:0.08em;'>&#8599;</span></a>) ",
        "exp_adv": "Optional Filters, scope and evidence",
        "exp_comp": "Benchmark design",
        "exp_core": "Target and measurement window",
        "exp_question": "Question",
        "exp_metadata": "Metadata",
        "fig_rx_abs": "RX Performance: {callsign} — Heard by Target vs. Heard by Others Only",
        "fig_rx_comp": "RX Benchmark: {callsign} (Target) vs. {comp_title}",
        "abs_rx_counter": "Elsewhere",
        "abs_rx_counter_short": "E",
        "abs_rx_target_column": "Target (T)",
        "abs_rx_pair": "Target+Elsewhere",
        "abs_rx_formula": "Target/(Target+Elsewhere)",
        "abs_rx_rate_column": "T/(T+E) (%)",
        "abs_rx_counter_column": "Elsewhere (E)",
        "abs_tx_counter": "Other Signals",
        "abs_tx_counter_short": "OS",
        "abs_tx_target_column": "Target (T)",
        "abs_tx_pair": "Target+Other Signals",
        "abs_tx_formula": "Target/(Target+Other Signals)",
        "abs_tx_rate_column": "T/(T+OS) (%)",
        "abs_tx_counter_column": "Other Signals (OS)",
        "fig_tx_comp": "TX Benchmark: {callsign} (Target) vs. {comp_title}",
        "hlp_solar": """Select daylight, nighttime or greyline at the **Target’s location**, rather than along the entire radio path. All 24h keeps all solar states within your measurement window.""",
        "hlp_max_dist": """Include only **remote stations** nearer than this distance from the Target. This changes analysis evidence, maps, Inspector and exports; it **does not reduce archive retrieval**.""",
        "hlp_min_spots": """Minimum :primary[**Joint Spots**] per remote station: Target–Reference comparisons from the **same WSPR cycle**. The same minimum applies **separately to one-sided evidence**, which does not qualify a station for ΔSNR.""",
        "hlp_min_opportunities_rx": """Minimum **confirmed opportunities** per remote transmitter. Count both Target decodes and transmissions heard by other receivers while the active Target does not decode them.""",
        "hlp_min_opportunities_tx": """Minimum **confirmed opportunities** per remote receiver. Count both Target decodes and cycles when that same receiver hears another qualifying transmitter but misses the active Target.""",
        "hlp_min_stations_compare": """Minimum qualifying **callsign + full locator** identities **per map segment**. Each must meet the Joint Spot minimum; one-sided evidence does not count. These are reported identities, not necessarily independent physical stations.""",
        "hlp_min_stations_success_rx": """Show a **map segment** only when this many remote transmitters meet the **confirmed-opportunity minimum**. Stations can qualify even if none of their signals were decoded by the Target.""",
        "hlp_min_stations_success_tx": """Show a **map segment** only when this many remote receivers meet the **confirmed-opportunity minimum**. A receiver can qualify even if it never decoded the Target.""",
        "hlp_benchmark_offset_db": """Added to Reference SNR before calculating ΔSNR. **Positive values lower ΔSNR; negative values raise it.** Use 0.0 dB unless you have a documented correction for this comparison.""",
        "err_benchmark_offset_db": "Enter a value from -99.9 to 99.9 using a decimal point, for example 1.2 or -1.2.",
        "hlp_callsign_entry": """Enter the **exact reporting identity** stored in the WSPR archive, **including any suffix**. Different spellings select different identities.""",
        "hlp_target_qth": """Enter the Target’s **Maidenhead locator** for the selected period. It anchors station selection, map geometry, distance and local solar state.""",
        "hlp_band": """Analyze one WSPR band at a time. Choose the band used during the measurement period.""",
        "hlp_time_window": """Choose a **UTC interval** when station identities, locations and setup were reasonably stable. Longer windows add evidence but may mix different operating and propagation conditions.""",
        "hlp_reference_callsign": """Enter the Reference callsign **exactly as reported in the WSPR archive, including any suffix**. For example, `CALL` and `CALL/P` are distinct reporting identities; enter the form actually recorded for your Reference.

WSPRadar resolves its location from the selected **band, direction and UTC window**.""",
        "hlp_reference_radius": """**Maximum distance** from the Target for contributing Reference stations. A larger radius can add contributors but makes the comparison less local.""",
        "hlp_benchmark_reference_station": """Compare the Target with another controlled signal path or one known station, at the same or another location. The comparison reflects the **complete setups and their operating conditions**.""",
        "hlp_benchmark_local_neighborhood": """Compare the Target with the **median** of qualifying nearby station contributions within your chosen radius, for each remote station and WSPR cycle. No single fixed Reference is selected; **contributors can change** between paths and cycles.""",
        "fmt_reference_choice_selected": "{choice} (selected)",
        "fmt_reference_choice_help": "Help for {choice}",
        "lbl_band": "Operating Band",
        "lbl_benchmark_offset_db": "Reference-side SNR correction (dB)",
        "lbl_config_file": "Select WSPRadar .config file",
        "lbl_demo_select": "Select demo profile",
        "lbl_callsign": "Your Callsign (Target under Test)",
        "lbl_callsign_rx": "Target callsign (receiver under test)",
        "lbl_callsign_tx": "Target callsign (transmitter under test)",
        "lbl_analysis_selector": "RX or TX Analysis",
        "opt_analysis_rx": "RX Analysis",
        "opt_analysis_tx": "TX Analysis",
        "lbl_comp_mode": "Benchmark design",
        "lbl_question": "Question",
        "txt_question_intro": """The **Target** is the station or controlled signal path being evaluated - likely your station. Choose whether to assess its RX or TX Performance, or Benchmark it against a Reference:""",
        "lbl_end_d": "End Date (UTC)",
        "lbl_end_t": "End Time (UTC)",
        "lbl_insights": "Station Insights",
        "lbl_max_dist": "Maximum peer distance from Target (km)",
        "lbl_min_spots": "Minimum joint evidence per station",
        "lbl_min_opportunities": "Minimum confirmed opportunities per station",
        "lbl_min_stations": "Minimum qualifying stations per map segment",
        "lbl_no_joint": "No joint spots available in this segment to calculate a \u0394 SNR histogram.",
        "lbl_qth": "Target QTH (4 or 6 characters)",
        "lbl_ref_radius_km": "Neighborhood Radius (km)",
        "lbl_target_callsign": "Target callsign",
        "lbl_reference_callsign": "Reference callsign",
        "ph_reference_callsign": "e.g. CALL/P",

        "txt_target": "Target",
        "txt_reference": "Reference",
        "lbl_solar": "Solar state at Target QTH",
        "lbl_start_d": "Start Date (UTC)",
        "lbl_start_t": "Start Time (UTC)",
        "lbl_time_window": "UTC measurement window",
        "txt_benchmark_offset_note": "Ref SNR Corr: {offset:+.1f} dB",
        "opt_comp_none": "Performance — no Reference",
        "opt_comp_radius": "Benchmark — Reference Neighborhood",
        "opt_comp_buddy": "Benchmark — Reference Setup/Station",
        "opt_benchmark_reference_station": "Reference Setup/Station",
        "opt_benchmark_local_neighborhood": "Reference Neighborhood",
        "opt_question_rx_performance": "RX Performance",
        "opt_question_tx_performance": "TX Performance",
        "opt_question_rx_benchmark": "RX Benchmark",
        "opt_question_tx_benchmark": "TX Benchmark",
        "desc_question_rx_performance": """Assess how reliably the Target RX decodes peer TX signals across confirmed opportunities.""",
        "desc_question_tx_performance": """Assess how reliably active receivers hear the Target.""",
        "desc_question_rx_benchmark": """Compare what the Target and Reference receivers hear under matched conditions.""",
        "desc_question_tx_benchmark": """Compare how the Target and Reference transmit paths are heard under matched conditions.""",
        "opt_local_median": "Local Median Neighborhood",
        "err_local_benchmark": """Local Median Neighborhood is the supported local method. Use Reset Config to restore valid inputs.""",
        "err_reference_callsign_same": "Target and Reference callsigns must be different.",
        "warn_tx_message_patterns_title": "Check the TX message patterns",
        "warn_tx_message_patterns": """These callsigns may use different WSPR message patterns. This can skew one-sided counts and Joint Evidence Share.

For a controlled TX comparison, use two standard callsigns transmitting Type 1 messages, or two compound callsigns transmitting synchronized Type 2/Type 3 sequences. When using the same base callsign, give both transmitters different suffixes, for example `CALL/1` and `CALL/2`. Check which suffixes are permitted for your callsign and operation in your country.

Check that matching message types are transmitted in the same two-minute cycles.""",
        "err_reference_callsign_required": "Please configure a Reference Callsign.",
        "err_reference_qth_required": "Resolve the Reference location before starting the analysis.",
        "err_callsign_format": "Enter a plausible callsign/reporting identifier: 3-15 ASCII characters; use '/' only between non-empty alphanumeric segments and at most one terminal '-' before a non-empty alphanumeric suffix. The portion before any hyphen must contain at least one letter; a digit is not required.",
        "err_qth_format": "Enter a valid 4- or 6-character Maidenhead locator (e.g. JN37 or JN37AA).",
        "err_time_invalid": "Enter valid UTC start and end dates and times.",
        "err_time_before_minimum": "The UTC start must be on or after 2008-01-01 00:00 UTC.",
        "err_time_order": "The UTC end must be after the start.",
        "err_time_duration": "The UTC measurement window must not exceed 31 days.",
        "err_time_future": "The UTC end must not be after the current UTC minute.",
        "err_url_invalid": "This WSPRadar analysis URL is invalid and was not applied.",
        "err_url_unsupported_version": "This WSPRadar analysis URL uses an unsupported version and was not applied.",
        "err_reference_callsign_format": "Enter a plausible Reference Callsign: 3-15 ASCII characters; use '/' only between non-empty alphanumeric segments and at most one terminal '-' before a non-empty alphanumeric suffix. The portion before any hyphen must contain at least one letter; a digit is not required.",
        "err_reference_grid4_format": "The resolved Reference location must be a four-character Maidenhead grid. Run location discovery again.",
        "leg_both_async": "Both (Async)",
        "leg_joint": "Both (Joint)",
        "leg_only_me": "Only {callsign}",
        "leg_only_ref": "Only {ref_callsign}",
        "leg_only_ref_radius": "Only Reference",
        "msg_proc": "Processing {id}...",
        "msg_analysis_queue_wait": "All analysis capacity is in use; queued at position {position}.",
        "msg_analysis_submission_active": "Analysis submitted; Run Analysis is disabled until it finishes.",
        "msg_config_loaded": "Config loaded. Existing results were cleared.",
        "opt_all_dirs": "All Directions",
        "opt_full_range": "Full Range",
        "opt_solar_all": "All 24h",
        "opt_solar_day": "Daylight (Elev > +6°)",
        "opt_solar_grey": "Greyline (-6° to +6°)",
        "opt_solar_night": "Nighttime (Elev < -6°)",
        "subtitle": "HAM RADIO STATION & ANTENNA BENCHMARKING",
        "tbl_col_az": "Azimuth",
        "tbl_col_joint": "Joint Spots",
        "tbl_col_km": "km",
        "tbl_col_loc": "Locator",
        "tbl_col_med_delta": "Median \u0394 SNR (dB)",
        "tbl_col_only_u": "Only {callsign}",
        "tbl_col_cycle_ref_median": "Cycle Ref Median SNR (dB)",
        "tbl_col_delta_snr": "\u0394 SNR (dB)",
        "lbl_neighborhood": "Neighborhood",
        "tbl_col_ref_snr": "Ref SNR (dB)",
        "tbl_col_ref_station": "Ref Station",
        "tbl_col_rx": "RX Station",
        "tbl_col_success_station_rx": "TX Station",
        "tbl_col_success_station_tx": "RX Station",
        "tbl_col_success_rate": "Decode Rate (%)",
        "tbl_col_success_snr": "Median Target SNR (dB @ 30 dBm)",
        "tbl_col_success_counter_display_tx": "Other signals heard",
        "tbl_col_success_snr_display": "Median SNR @ 30 dBm",
        "fmt_results_success_station_summary": "Stations: {success_label} {success_station_count} · {counter_label} {counter_station_count} · Station-balanced Decode Rate {station_balanced_rate:.1f}%",
        "fmt_results_success_opportunity_summary": "Opportunities: {success_label} {success_count} · {counter_label} {counter_count} · Opportunity-level Decode Rate {observation_level_rate:.1f}%",
        "txt_results_success_no_eligible": "No station meets the confirmed-opportunity threshold in this scope.",
        "tbl_col_tx": "TX Station",
        "lbl_exclude_special": "Exclude Special Callsigns Q, 0, 1",
        "hdr_remote_station_filters": "Remote station filters",
        "hdr_analysis_scope": "Analysis scope",
        "hdr_evidence_requirements": "Evidence requirements",
        "tt_exclude_special": """Exclude **remote callsigns** starting with **Q, 0 or 1**, typically used for balloon telemetry. Target and Reference stations, including neighborhood contributors, remain eligible.""",
        "title": "WSPRadar.org",
        "lbl_filter_moving": "Exclude Moving Stations",
        "tt_filter_moving": """Exclude remote callsigns reported from **more than one four-character grid square**. Locator changes can reflect movement or reporting errors; movement within one square is not detected.""","txt_joint": "Joint",
        "txt_joint_decodes": "Joint Decodes",
        "txt_remote": "Total Remote",
        "txt_rx_stations": "RX Stations",
        "txt_tx_stations": "TX Stations",
        "warn_analysis_queue_full": "High demand right now. The analysis queue is full. Please try again shortly.",
        "warn_analysis_queue_timeout": "Analysis capacity did not become available in time. Please run the analysis again.",
        "warn_analysis_result_row_limit": """Search result exceeded the safe limit of **{max_rows} rows**, so the analysis was stopped before processing; no partial result was analyzed. Shorten the analysis period. {special_callsign_advice}**{max_peer_distance_label}**, moving-station, solar-state, and evidence filters are applied after retrieval and will not avoid this limit. For a Reference Neighborhood comparison, reducing **{neighborhood_radius_label}** can reduce the database result.""",
        "warn_analysis_result_row_limit_special_callsign_advice": "Enabling **{special_callsign_label}** may also reduce the database result. ",
        "status_analysis_result_row_limit": "Analysis stopped at the safe row limit",
        "warn_no_data": "Not enough qualifying data found for **{title}** after applying filters. Are the callsign entries, locator, band, date, and UTC time correct?",
        "warn_no_source_rows": "No source rows were returned for **{title}**. Check the exact callsign or reporting identity, locator, band, UTC window, and actual operation. The active filters, analysis scope, and evidence requirements are shown in Review above.",
        "warn_no_target_mode_evidence": """No reports for the Target matched the required **WSPR-2 mode filter** for the selected callsign, locator, band and period. WSPR-2 is the standard WSPR mode with two-minute transmission cycles. WSPRadar filters reports using the database’s recorded mode information (`code = 1`).

Older archive records may have missing or ambiguous mode information. WSPRadar automatically retries without this filter only when the **entire selected period is before 1 January 2022 (UTC)**. Your selected period extends beyond that historical compatibility range, so the mode filter remains applied.""",
        "warn_source_rows_filtered_out": "The source returned **{source_row_count} rows** for **{title}**, but none remained after the active post-fetch filters and analysis scope were applied. This does not by itself prove that the scope was too narrow. The applied configuration is shown in Review above.",
        "warn_performance_no_eligible_station": "The active filters and scope retained **{station_identity_count} station identities (callsign + locator)** for **{title}**, but none met the per-station evidence requirement. Highest observed: **{maximum_confirmed_opportunities_per_station} confirmed opportunities**; required: **at least {minimum_confirmed_opportunities_per_station} per station**. Empty map, Inspector, and table components are omitted. The applied configuration is shown in Review above.",
        "warn_performance_no_qualifying_segment": "**{eligible_station_count} station identities** met the per-station evidence requirement for **{title}**, but no map segment met its station requirement. Highest observed: **{maximum_stations_per_segment} qualifying stations in one segment**; required: **at least {minimum_qualifying_stations_per_map_segment} per map segment**. Station-level evidence remains available below; only segment-dependent output is omitted. The applied configuration is shown in Review above.",
        "warn_benchmark_no_qualifying_result_simultaneous": "No qualifying Benchmark result was available for **{title}** after applying the active filters, analysis scope, and evidence requirements. Required: **at least {minimum_joint_evidence_per_station} Joint observations per station** and **at least {minimum_qualifying_stations_per_map_segment} qualifying stations per map segment**. This does not by itself prove that the scope was too narrow. The applied configuration is shown in Review above.",

        "fig_mean_label": "Mean",
        "fig_share_percent_axis": "Share (%)",
        "fmt_temporal_title_with_bins": "{title} ({time_bin} bins)",
        "fig_decode_outcomes": "Decode Outcomes",
        "fig_station_medians_delta": "Station Medians (\u0394 SNR)",
        "fig_joint_spot_delta": "Joint-Spot \u0394 SNR",
        "fig_no_data": "No data",
        "msg_loading": "\u23f3 Loading...",
        "fmt_results_selected_station_evidence_title": "{heading}: {selection_context}",
        "txt_snr_values_normalized_30dbm": "SNR values are normalized to 30 dBm.",
        "lbl_filter": "Filter",
        "lbl_filter_columns": "Filter column(s):",
        "lbl_select_columns": "Select Columns",
        "fmt_results_selected_range_count": "{count} ranges",
        "fmt_results_selected_direction_count": "{count} directions",
        "msg_results_no_stations_in_scope": "No stations in the selected scope.",
        "txt_station_insights_normalized_30dbm": "Norm. @ 30 dBm. Click for details",
        "msg_drilldown_no_stations_selected": "No station selected.",
        "msg_drilldown_no_spots": "No spots available.",


        "msg_drilldown_no_joint_spots": "No joint spots are available for the selected station.",
        "msg_drilldown_no_reference_station_details": "No reference-station details are available for the selected station.",
        "warn_analysis_cache_expired": "Cache file expired. Please run the analysis again.",
        "err_analysis_evidence_schema_invalid": "Analysis evidence could not be read because its schema is invalid.",
        "err_analysis_processing_failed": "Analysis evidence could not be prepared. Please run the analysis again.",
        "err_analysis_configuration_invalid": "The analysis configuration is invalid. Check the inputs and try again.",
        "err_config_validation_field": "Invalid configuration at {field_path}.",
        "err_config_validation_generic": "The configuration is invalid.",
        "fmt_export_reference_correction_suffix": " (Reference correction {value:+.1f} dB)",
        "export_weighting_single_selected_path": "Single selected path",
        "export_weighting_combined_observation": "Combined observation-weighted evidence",
        "map_footer_time": "Time: {value}",
        "map_footer_band": "Band: {value}",
        "map_footer_solar": "Solar: {value}",

        "map_footer_joint_pairs_per_station": "Joint Pairs/Station: \u2265{threshold}",
        "map_footer_joint_spots_per_station": "Joint Spots/Station: \u2265{threshold}",
        "map_footer_joint_stations_per_segment": "Joint stations/segment: \u2265{threshold}",
        "map_footer_schedule": "Schedule: {interval} min / T {target_start:02d} / R {reference_start:02d} UTC",
        "map_footer_reference": "Reference: {reference}",
        "map_performance_footer_confirmed_opportunities_per_station": "Confirmed opportunities/station: \u2265{threshold}",
        "map_performance_footer_stations_per_segment": "Stations/segment: \u2265{threshold}",
        "map_performance_footer_segment_metric": "Segment: Station-balanced Decode Rate",
        "map_compare_footer_pairs": "PAIRS",
        "map_compare_footer_spots": "SPOTS",
        "pdf_metric_decode_rate": "Decode Rate",
        "pdf_formula_correction": "Correction",
        "pdf_formula_delta_snr": "Delta SNR",
        "pdf_formula_approx": "approx.",
        "pdf_page_label": "Page",
        "ph_target_callsign": "e.g. CALL",
        "txt_reference_location_resolved": "Reference location: {grid4}",
        "txt_reference_location_pending": "Reference location will be resolved from the database for the selected period when you run the analysis.",
    },
    "de": {
        "fig_tx_abs": 'TX Performance: {callsign} — Target gehört vs. nur andere Signale gehört',




        'fig_joint_spot_count': "Anzahl Joint Spots",
        'fig_relative_joint_spot_density': "Relative Joint-Spot-Dichte (% des Panelmaximums)",

        'lbl_time_aggregation_bin_size': "Zeitliche Aggregationsbreite auswählen",
        'lbl_report_delta_snr_outlier_candidates': "ΔSNR-Ausreißerkandidaten melden",
        'tt_report_delta_snr_outlier_candidates': """Markiere **ungewöhnliche ΔSNR-Abweichungen** zur genaueren Prüfung anhand unterstützender Beobachtungen **vor und nach** jedem Kandidaten. Dies ergänzt einen Bericht; es entfernt keine Evidenz und bestimmt keine Ursache.""",
        'lbl_delta_snr_outlier_minimum_departure_db': "Minimale absolute ΔSNR-Abweichung (dB)",
        'tt_delta_snr_outlier_minimum_departure_db': """Mindestunterschied in beliebiger Richtung zwischen dem **medianen ΔSNR** eines Kandidaten und seiner **umgebenden Baseline**. Niedrigere Werte markieren kleinere Abweichungen.""",
        'lbl_delta_snr_outlier_minimum_robust_z': "Minimaler robuster z-Wert",
        'tt_delta_snr_outlier_minimum_robust_z': """Mindestabweichung relativ zur **robusten Streuung** der umgebenden Evidenz. Höhere Werte verlangen, dass sich die Abweichung stärker von dieser Variabilität abhebt.""",
        'lbl_delta_snr_outlier_maximum_baseline_difference_db': "Maximaler Unterschied zwischen Baseline davor/danach (dB)",
        'tt_delta_snr_outlier_maximum_baseline_difference_db': """Größter zulässiger Unterschied zwischen den **Baselines vor und nach** einem Kandidaten. Niedrigere Werte verlangen einen stabileren Hintergrund.""",
        'btn_reset_delta_snr_outlier_detector_defaults': "Detektor-Standardwerte wiederherstellen",
        'lbl_delta_snr_outlier_detector_thresholds': "Schwellenwerte des Ausreißerdetektors",
        'fmt_delta_snr_outlier_detector_thresholds': "Abweichung ≥ {departure:g} dB · robuster z-Wert ≥ {robust_z:g} · Baseline-Unterschied davor/danach ≤ {baseline_difference:g} dB",
        'fig_delta_snr_outlier_candidate': "ΔSNR-Ausreißerkandidat",
        'fig_segment_chronological_delta': "\u0394 SNR im Zeitverlauf",
        'fig_segment_utc_hour_title': "\u0394 SNR nach UTC-Stunde (1-h-Bins)",
        'fig_selected_compare_chronological_title': "\u0394 SNR im Zeitverlauf",
        'fig_selected_compare_folded_title': "\u0394 SNR nach UTC-Stunde",
        'fig_rx_comp_temporal_prefix': "RX-Benchmark – Zeitverlauf",
        'fig_tx_comp_temporal_prefix': "TX-Benchmark – Zeitverlauf",
        'fig_segment_chronological_x': "Datum/Uhrzeit (UTC)",
        'fig_segment_utc_hour_x': "UTC-Stunde",
        'fig_segment_dates_folded': "{count} UTC-Tage zusammengef\u00fchrt",
        'fig_segment_folded_unavailable': "UTC-Stundenmuster nicht verf\u00fcgbar - erfordert gepaarte Evidenz aus mindestens 2 UTC-Tagen.",
        'fig_compare_chronological_unavailable': "Im ausgew\u00e4hlten UTC-Zeitfenster liegt keine gepaarte Evidenz f\u00fcr \u0394 SNR vor.",
        'fig_compare_coverage_title_rx': "RX-Benchmark — Zeitliche Evidenzabdeckung: Target {callsign}",
        'fig_compare_coverage_title_tx': "TX-Benchmark — Zeitliche Evidenzabdeckung: Target {callsign}",
        'fig_compare_coverage_chronological_title': "Evidenzabdeckung im Zeitverlauf ({time_bin}-Bins)",
        'fig_compare_coverage_utc_hour_title': "Evidenzabdeckung nach UTC-Stunde (1-h-Bins)",
        'fig_compare_coverage_folded_unavailable': "UTC-Stundenmuster nicht verfügbar — erfordert Benchmark-Evidenz aus mindestens 2 UTC-Tagen.",
        'fig_compare_coverage_station_y_rx': "TX-Stationen",
        'fig_compare_coverage_station_y_tx': "RX-Stationen",
        'fig_compare_coverage_station_folded_y_rx': "Ø TX-Stationen",
        'fig_compare_coverage_station_folded_y_tx': "Ø RX-Stationen",
        'fig_compare_coverage_unit_y_rx': "Senderzyklen",
        'fig_compare_coverage_unit_y_tx': "Empfängerzyklen",

        'fig_compare_coverage_unit_folded_y_rx': "Ø Senderzyklen",
        'fig_compare_coverage_unit_folded_y_tx': "Ø Empfängerzyklen",

        'fig_compare_joint_share_station': "Stationsgleichgewichteter Joint-Evidenzanteil",
        'fig_compare_joint_share_outcome': "Joint-Evidenzanteil auf Outcome-Ebene",
        'fig_compare_joint_share_y': "Joint-Evidenz (%)",
        'fig_compare_coverage_gate_simultaneous': """WSPR-Zyklen ohne Evidenz für den Betrieb des Targets bleiben unberücksichtigt, damit mögliche Ausfallzeiten des Targets nicht als Misserfolg zählen.\nOnly Target und Only Reference sind daher nicht symmetrisch. Der Joint-Evidenzanteil zeigt die Paarabdeckung innerhalb dieser Zyklen.""",

        'fig_selected_compare_coverage_title_rx': "RX-Benchmark — Evidenzabdeckung des ausgewählten Funkwegs: {station} ({locator})",
        'fig_selected_compare_coverage_title_tx': "TX-Benchmark — Evidenzabdeckung des ausgewählten Funkwegs: {station} ({locator})",
        'fig_selected_compare_coverage_chronological_title': "{unit} im Zeitverlauf ({time_bin}-Bins)",
        'fig_selected_compare_coverage_utc_hour_title': "{unit}\nnach UTC-Stunde (1-h-Bins)",
        'fig_selected_compare_coverage_unit_simultaneous': "Berücksichtigte WSPR-Zyklen",

        'fig_selected_compare_coverage_unit_y_simultaneous': "WSPR-Zyklen",
        'fig_selected_compare_coverage_unit_folded_y_simultaneous': "Ø WSPR-Zyklen",
        'fig_selected_compare_joint_share': "Joint-Evidenzanteil",
        'fig_selected_compare_coverage_unavailable': "Für diesen ausgewählten Funkweg sind keine beibehaltenen Benchmark-Outcomes verfügbar.",
        'fig_selected_compare_coverage_unavailable_multi': "Die Evidenzabdeckung des ausgewählten Funkwegs ist nur für einen ausgewählten Funkweg verfügbar; die kombinierte ΔSNR-Evidenz bleibt oben verfügbar.",
        'fig_success_temporal_title_rx': "RX Performance — Zeitliche Evidenz: Target {callsign}",
        'fig_success_temporal_title_tx': "TX Performance — Zeitliche Evidenz: Target {callsign}",
        'fig_success_temporal_snr_title_rx': "RX Performance — Zeitliche SNR-Evidenz: Target {callsign}",
        'fig_success_temporal_snr_title_tx': "TX Performance — Zeitliche SNR-Evidenz: Target {callsign}",
        'fig_success_selected_station_snr_title_rx': "RX Performance — SNR-Evidenz der ausgewählten Station: {station} ({locator})",
        'fig_success_selected_station_snr_title_tx': "TX Performance — SNR-Evidenz der ausgewählten Station: {station} ({locator})",
        'fig_success_selected_station_temporal_title_rx': "RX Performance — Zeitliche Evidenz der ausgewählten Station: {station} ({locator})",
        'fig_success_selected_station_temporal_title_tx': "TX Performance — Zeitliche Evidenz der ausgewählten Station: {station} ({locator})",
        'fig_success_reach_title_rx': "Vom Target mindestens einmal gehörte TX-Stationen nach Entfernung",
        'fig_success_reach_title_tx': "RX-Stationen, die das Target mindestens einmal hörten, nach Entfernung",
        'fig_success_reach_y_rx': "Qualifizierende TX-Stationen, vom Target mindestens einmal gehört (%)",
        'fig_success_reach_y_tx': "Qualifizierende RX-Stationen, die das Target mindestens einmal hörten (%)",
        'fig_success_consistency_title_rx': "RX Dekodierrate nach Entfernung der TX-Station",
        'fig_success_consistency_title_tx': "TX Dekodierrate nach Entfernung der RX-Station",
        'fig_success_snr_distance_title_rx': "Erfolgreiches Target-SNR nach Entfernung der TX-Station",
        'fig_success_snr_distance_title_tx': "Erfolgreiches Target-SNR nach Entfernung der RX-Station",
        'fig_success_distance_x': "Entfernung vom Target-QTH (km)",
        'fig_success_rate_y': "Dekodierrate (%)",
        'fig_success_snr_y': "Stationsmedian des erfolgreichen Target-SNR (dB @ 30 dBm)",
        'fig_success_confirmed_opportunities': "Bestätigte Gelegenheiten",
        'fig_success_qualifying_stations': "Qualifizierende Stationen",
        'fig_success_successful_snr_stations': "Stationen mit erfolgreichem SNR",
        'fig_success_station_balanced': "Stationsgleichgewichtete Dekodierrate",
        'fig_success_observation_level': "Dekodierrate auf Gelegenheitsebene",
        'fig_success_median': "Median",
        'fig_success_iqr': "IQR (3+ Stationen)",
        'fig_success_two_station_range': "Min-Max (2 Stationen)",
        'fig_success_support': "Evidenzbasis",
        'fig_success_support_title': "Evidenzumfang nach Entfernung",
        'fig_success_bin_width': "Binbreite: {width_km:g} km",
        'fig_success_locator_precision_note': "Die berechnete Entfernung übernimmt die Genauigkeit der gemeldeten Locator; ein Maidenhead-Locator mit vier Zeichen ist keine vermessungsgenaue Positionsangabe.",
        'fig_success_snr_chronological_title_rx': "Abweichung des erfolgreichen RX-SNR im Zeitverlauf",
        'fig_success_snr_chronological_title_tx': "Abweichung des erfolgreichen TX-SNR im Zeitverlauf",
        'fig_success_snr_utc_hour_title_rx': "Abweichung des erfolgreichen RX-SNR nach UTC-Stunde",
        'fig_success_snr_utc_hour_title_tx': "Abweichung des erfolgreichen TX-SNR nach UTC-Stunde",
        'fig_success_evidence_chronological_title': "Evidenz im Zeitverlauf ({time_bin}-Bins)",
        'fig_success_evidence_utc_hour_title': "Evidenz nach UTC-Stunde (1-h-Bins)",
        'fig_success_station_votes_y_rx': "TX-Stationen",
        'fig_success_station_votes_y_tx': "RX-Stationen",
        'fig_success_station_support_folded_y_rx': "Ø TX-Stationen",
        'fig_success_station_support_folded_y_tx': "Ø RX-Stationen",
        'fig_success_opportunities_y': "Gelegenheiten",
        'fig_success_opportunities_folded_y': "Ø Gelegenheiten",
        'fig_success_rate_legend': "Dekodierrate",
        'fig_success_time_x': "Datum/Uhrzeit (UTC)",
        'fig_success_utc_hour_x': "UTC-Stunde",
        'fig_success_snr_anomaly_y_rx': "Abweichung vom Laufmedian jeder TX-Station (dB)",
        'fig_success_snr_anomaly_y_tx': "Abweichung vom Laufmedian jeder RX-Station (dB)",
        'fig_success_snr_density': "Relative Dichte stationsbezogener SNR-Abweichungen",
        'fig_success_station_baseline': "Laufmedian jeder Station (0 dB)",
        'fig_success_bin_median_chronological': "Median über Stationen",
        'fig_success_bin_median_folded': "Median über Stationen und Tage",
        'fig_success_selected_snr_chronological_title': "Erfolgreiches Target-SNR im Zeitverlauf",
        'fig_success_selected_snr_utc_hour_title': "Erfolgreiches Target-SNR nach UTC-Stunde",
        'fig_success_selected_temporal_snr_y': "Normiertes Target-SNR (dB @ 30 dBm)",
        'fig_success_selected_snr_density': "Relative Dichte des erfolgreichen Target-SNR",
        'fig_success_selected_folded_median': "Median über berücksichtigte Tage",
        'fig_success_selected_snr_unavailable': "Für diese Station ist kein erfolgreiches Target-SNR verfügbar. Für verpasste Signale gibt es kein aufgezeichnetes Target-SNR.",
        'lbl_selected_time_aggregation_bin_size': "Zeitliche Aggregationsbreite wählen:",
        'fig_success_selected_bin_median': "Bin-Median",
        'fig_success_snr_anomaly_unavailable': "SNR-Anomalie nicht verfügbar — erfordert mindestens 3 erfolgreiche Target-SNR-Beobachtungen je Station.",
        'fig_success_temporal_unavailable': "UTC-Stundenmuster nicht verfügbar — erfordert Evidenz aus mindestens 2 UTC-Tagen.",
        'fig_success_utc_dates_folded': "{count} UTC-Tage zusammengeführt",
        'fig_compare_median_focus_axis': "\u0394 SNR (dB \u00b7 nichtlinear um Median zentriert)",
        'fig_median_label': "Median",
        'fig_temporal_bin_median': "Lokaler Median",
        'fig_temporal_bin_iqr': "IQR je Bin (mittlere 50 %)",

        'tbl_col_joint_pairs': "Joint-Paare",

        'tbl_col_micro_a': "Target-Mikromedian",
        'tbl_col_micro_b': "Referenz-Mikromedian",
        'tbl_col_pair_delta': "Paar \u0394",
        "btn_demo": "Demo laden",
        "btn_load_config": "Konfig laden",
        "btn_save_config": "Konfig speichern",
        "btn_prepare_config": "Konfiguration vorbereiten",
        "btn_download_config": "Konfiguration herunterladen",
        "txt_config_profile_intro": "Wiederverwendbare Profildaten angeben und danach den Download vorbereiten.",
        "lbl_config_profile_title": "Titel",
        "lbl_config_profile_description": "Beschreibung (optional)",
        "lbl_config_profile_id": "Profil-ID (optional)",
        "hlp_config_profile_id": "Leer lassen, um eine stabile ID aus dem Titel abzuleiten.",
        "warn_saved_station_unavailable": "Die gespeicherte Stationsauswahl konnte nicht wiederhergestellt werden, weil diese Station in der aktuellen Station-Insights-Tabelle nicht verf\u00fcgbar ist: {stations}. Es wurde kein Ersatz ausgew\u00e4hlt.",
        "msg_config_prepared": "Konfiguration vorbereitet. Sie kann unten heruntergeladen werden.",
        "btn_apply_config": "Ausgewaehlte Konfig laden",
        "btn_load_demo_selected": "Ausgewaehlte Demo-Konfiguration laden",
        "btn_run_demo_selected": "Ausgewaehlte Demo starten",
        "btn_prepare_all_results": "Alle Ergebnisse zum Download vorbereiten",
        "btn_download_prepared_results": "Vorbereitete Ergebnisse herunterladen",
        "btn_share_analysis": "Analyse teilen",
        "share_url_field": "Analyse-URL",
        "share_copy_link": "Link kopieren",
        "share_copied": "Link kopiert.",
        "share_manual_copy": "Die URL ist markiert. Bitte manuell kopieren.",
        "share_native": "Teilen\u2026",
        "share_native_failed": "Die Browser-Freigabe war nicht verf\u00fcgbar. Bitte stattdessen die markierte URL kopieren.",
        "share_email": "E-Mail",
        "share_whatsapp": "WhatsApp",
        "share_x": "X",
        "share_facebook": "Facebook",
        "share_linkedin": "LinkedIn",
        "share_analysis_title": "WSPRadar-Analyse: {callsign} {direction} {mode} auf {band}",
        "share_analysis_message": "Dieser Link rekonstruiert und startet die Analyse mit dem aktuellen WSPRadar-Code und den dann verf\u00fcgbaren Quelldaten erneut.",
        "help_share_analysis": """:primary[**Analyse teilen**] erstellt einen Link, der die aktuellen Analyseeinstellungen und unterstützten Inspector-Auswahlen lädt und anschließend die Analyse erneut ausführt. Nutze `Link kopieren` oder eine Freigabeoption, um ihn zu versenden.

Wähle **Evidenz herunterladen**, um die beibehaltenen Beobachtungen, Tabellen und Abbildungen dieses abgeschlossenen Laufs weiterzugeben.""",
        "help_share_analysis_limits": """Der Link enthält Einstellungen, kein eingefrorenes Ergebnispaket. Beim Empfänger läuft die Analyse mit dem dann aktuellen WSPRadar-Code und den verfügbaren Archivdaten; das Ergebnis kann daher abweichen.""",
        "share_mode_performance": "Performance",
        "share_mode_reference_station": "Referenzaufbau/-station",
        "share_mode_local_neighborhood": "Referenznachbarschaft",
        "hdr_results_compare": "{direction}-Benchmark-Ergebnisse",
        "hdr_results_success": "{direction} Performance – Ergebnisse",

        "sub_results_rx_success": "Target {callsign} · vom Target oder nur von anderen gehört",
        "sub_results_tx_success": "Target {callsign} · Target gehört oder nur andere Signale an aktiven RX-Stationen gehört",
        "txt_results_metadata": "{band} · {utc_window} · Target-QTH {qth}",
        "txt_results_reference_grid4": "Referenz-Locator {grid4}",
        "txt_results_shared_grid4": "Gemeinsamer Locator {grid4}",
        "txt_results_reference_benchmark": "Referenz-Benchmark {benchmark}",
        "txt_results_configured_snr_correction": "Konfigurierte SNR-Korrektur: {correction_db} dB auf {recipient} angewendet",
        "txt_results_snr_correction_reference_identity": "die Referenz ({callsign})",
        "txt_results_snr_correction_reference_schedule": "den Referenz-Zeitplan",
        "txt_results_snr_correction_reference_benchmark": "den Referenz-Benchmark",
        "fmt_results_thousands_separator": ".",
        "lbl_results_evidence_path": "Evidenzpfad",
        "txt_results_evidence_path": "Karte → Segment-Inspektor → Station Insights → Drill-Down",
        "txt_results_evidence_path_success": "Karte → Segment-Inspektor → Station Insights → Drill-Down",
        "lbl_results_level_run": "Vollständiger Lauf",
        "lbl_results_level_scope": "Geografischer Bereich",
        "lbl_results_level_stations": "Beitragende Stationen",
        "lbl_results_level_selection": "Ausgewählte Stationen",
        "lbl_results_level_selection_success": "Ausgewählte Station",
        "lbl_results_level_rows": "Evidenz auf Zeilenebene",
        "hdr_results_map_view": "Kartenansicht",
        "sub_results_map_compare": "Geografischer Überblick über stationsgleichgewichtetes Δ SNR und Decode Outcomes.",
        "sub_results_map_success": "Remote {station_type}-Stationen nach Entfernung und Richtung gruppiert; dargestellt ist die stationsgleichgewichtete Dekodierrate.",
        "hdr_results_segment_inspector": "Segment-Inspektor",
        "sub_results_segment_inspector": "Wähle einen oder mehrere Entfernungsbereiche und Himmelsrichtungen. Alle nachfolgenden Evidenzansichten beziehen sich auf den aktiven Bereich.",
        "lbl_results_distance_range": "Entfernungsbereich",
        "lbl_results_direction": "Richtung",
        "txt_results_active_scope": "Aktiver Bereich · {distance} · {direction}",
        "txt_results_evidence_scope": "Evidenz im aktiven Bereich · {station_count} · {evidence_count} {evidence_unit}",
        "txt_results_transition_scope": "↓ Wähle Entfernung und Richtung, um einen geografischen Bereich zu untersuchen",
        "txt_results_transition_stations": "↓ Wähle eine Station, um ihre Evidenz zu untersuchen",
        "txt_results_transition_stations_multi": "↓ Wähle eine oder mehrere Stationen, um ihre Evidenz zu untersuchen",
        "txt_results_transition_stations_success": "↑ Wähle eine Station, um ihre Evidenz zu untersuchen",
        "txt_results_transition_rows": "↓ Prüfe die zugrunde liegenden Evidenzzeilen",
        "hdr_results_comparison_evidence": "Benchmark-Evidenz",
        "sub_results_comparison_evidence_joint": "Decode Outcomes, Stationsmediane und Δ SNR aus Joint Spots im aktiven Bereich.",

        "fmt_results_station_delta_summary": "Stationen{count_context} · Median {median} dB · Mittelwert {mean} dB",
        "fmt_results_joint_spot_delta_summary": "Spots{count_context} · Median {median} dB · Mittelwert {mean} dB",

        "lbl_results_stations": "Stationen",
        "lbl_results_spots": "Spots",

        "hdr_results_temporal_evidence": "Zeitliche Evidenz",
        "sub_results_temporal_evidence": "Absolutes ΔSNR, Abdeckung gepaarter Evidenz und UTC-Stundenmuster im aktiven Bereich.",
        "hdr_results_outlier_report": "Ausreißerbericht",
        "sub_results_outlier_report": "Native ΔSNR-Auslenkungen mit gemeinsamen Qualifikationskriterien, Zusammenfassungen qualifizierender Funkwege und chronologischer Zyklusevidenz im aktiven Bereich.",
        "msg_outlier_report_insufficient_paired_evidence": "Im aktiven Bereich sind keine {paired_evidence} verfügbar; daher kann kein ΔSNR-Kandidat auf Funkwegebene bewertet werden.",
        "msg_outlier_report_insufficient_local_baseline": "Keines der {populated} {paired_evidence} im aktiven Bereich hatte eine gestützte kandidatenbereinigte lokale Baseline; alle {abstained} nativen gepaarten Einheiten blieben unklassifiziert.",
        "msg_outlier_report_no_candidates": "Keine der {assessed} nativen gepaarten Einheiten mit gestützter lokaler Baseline bildete eine qualifizierende ΔSNR-Auslenkung; {abstained} von {populated} {paired_evidence} hatten keine ausreichende Baseline-Stützung und bleiben unklassifiziert.",
        "msg_outlier_report_invalid_detector_settings": "Der Ausreißerbericht ist nicht verfügbar, weil die Detektorschwellen ungültig sind. Korrigiere die erweiterten Einstellungen und starte eine neue Analyse.",
        "btn_outlier_show_path_in_station_insights": "↓ In Station Insights anzeigen",
        "btn_outlier_show_drilldown_details": "↓ Drill-Down-Details anzeigen",
        "btn_outlier_show_all_paths_in_station_insights": "Alle qualifizierenden Funkwege in Station Insights anzeigen",
        "txt_outlier_event_spot_impulse": "Spot-Impuls",
        "txt_outlier_event_short_burst": "Kurzer Ausbruch",
        "txt_outlier_event_sustained_excursion": "Anhaltende Auslenkung",
        "txt_outlier_event_mixed_duration": "Auslenkungen gemischter Dauer",
        "fmt_outlier_path_heading": "Funkweg {index} · {identity} · {direction}",
        "fmt_outlier_candidate_timeframe": "Zeitraum {utc_range}",
        "fmt_outlier_joint_count_singular": "1 Joint Spot",
        "fmt_outlier_joint_count_plural": "{count} Joint Spots",


        "fmt_outlier_path_observation_context": "{paired_count} · Spanne vom ersten bis zum letzten {first_to_last_span} · Medianabstand {median_interval} · größte Lücke {largest_gap}",
        "fmt_outlier_path_delta_context": "- **Erwartetes lokales ΔSNR:** {expected_local} dB\n- **Beobachteter ΔSNR-Median:** {observed_median} dB\n- **Größte Einzelzyklusabweichung:** {largest_departure} dB",
        "txt_outlier_paired_evidence_joint": "Joint Spots",

        "exp_outlier_wspr_cycle_evidence": "Chronologische WSPR-Zyklusevidenz · {utc_range}",

        "col_outlier_evidence_utc": "UTC",
        "col_outlier_evidence_path": "Funkweg",
        "col_outlier_evidence_direction": "Richtung",
        "col_outlier_evidence_delta_snr": "ΔSNR (dB)",
        "col_outlier_evidence_local_baseline": "Lokale Baseline (dB)",
        "col_outlier_evidence_residual": "Residuum (dB)",
        "col_export_outlier_event_id": "Ereignis-ID",
        "col_export_outlier_combined_event_class": "Zusammengefasste Ereignisklasse",
        "col_export_outlier_event_first_evidence_utc": "Erste Evidenz des Ereignisses (UTC)",
        "col_export_outlier_event_last_evidence_utc": "Letzte Evidenz des Ereignisses (UTC)",
        "col_export_outlier_cross_path_context": "Funkwegübergreifender Zusammenhang",
        "col_export_outlier_departure_direction": "Abweichungsrichtung",
        "col_export_outlier_qualifying_path_count": "Anzahl qualifizierender Funkwege",
        "col_export_outlier_path_event_id": "Funkwegereignis-ID",
        "col_export_outlier_path_number": "Funkwegnummer",
        "col_export_outlier_path_occurrence": "Funkwegereignisnummer",
        "col_export_outlier_path": "Funkweg",
        "col_export_outlier_callsign": "Rufzeichen",
        "col_export_outlier_locator": "Locator",
        "col_export_outlier_direction": "Richtung",
        "col_export_outlier_path_event_class": "Ereignisklasse des Funkwegs",
        "col_export_outlier_path_first_evidence_utc": "Erste Evidenz des Funkwegs (UTC)",
        "col_export_outlier_path_last_evidence_utc": "Letzte Evidenz des Funkwegs (UTC)",
        "col_export_outlier_paired_unit_type": "Art der gepaarten Evidenz",
        "col_export_outlier_paired_unit_count": "Anzahl gepaarter Evidenzeinheiten",
        "col_export_outlier_first_to_last_span_minutes": "Spanne erste–letzte Evidenz (min)",
        "col_export_outlier_median_evidence_interval_minutes": "Median-Evidenzabstand (min)",
        "col_export_outlier_largest_gap_minutes": "Größte Lücke (min)",
        "col_export_outlier_expected_local_delta_snr_db": "Erwartetes lokales ΔSNR (dB)",
        "col_export_outlier_observed_median_delta_snr_db": "Beobachteter ΔSNR-Median (dB)",
        "col_export_outlier_largest_single_unit_departure_db": "Größte Einzelzyklusabweichung (dB)",
        "col_export_outlier_episode_robust_z_score": "Robuster z-Wert",
        "col_export_outlier_pre_event_baseline_delta_snr_db": "Baseline-ΔSNR vor dem Ereignis (dB)",
        "col_export_outlier_post_event_baseline_delta_snr_db": "Baseline-ΔSNR nach dem Ereignis (dB)",
        "col_export_outlier_absolute_pre_post_baseline_difference_db": "Absoluter Baseline-Unterschied davor/danach (dB)",
        "col_export_outlier_agreeing_paired_unit_count": "Übereinstimmende gepaarte Evidenz",
        "col_export_outlier_paired_unit_sign_agreement_fraction": "Vorzeichenübereinstimmung der gepaarten Evidenz",
        "col_export_outlier_decode_edge_warning": "Warnung zu einseitiger Dekodierung",
        "col_export_outlier_decode_edge_warning_reason": "Grund der Warnung zu einseitiger Dekodierung",
        "col_export_outlier_nearby_joint_unit_count": "Nahe Joint-Evidenz",
        "col_export_outlier_nearby_target_only_unit_count": "Nahe Nur-Target-Evidenz",
        "col_export_outlier_nearby_reference_only_unit_count": "Nahe Nur-Reference-Evidenz",
        "col_export_outlier_unit_sequence": "Evidenznummer",
        "col_export_outlier_utc": "UTC",
        "col_export_outlier_target_snr_db": "Target-SNR (dB)",
        "col_export_outlier_corrected_reference_snr_db": "Korrigiertes Reference-SNR (dB)",
        "col_export_outlier_delta_snr_db": "ΔSNR (dB)",
        "col_export_outlier_departure_from_local_baseline_db": "Abweichung von lokaler Baseline (dB)",
        "col_export_outlier_cycle_robust_z_score": "Robuster z-Wert des Zyklus",
        "col_export_outlier_meets_strong_anchor_gates": "Erfüllt starke Ankerkriterien",
        "col_export_outlier_reported_boundary": "Berichtete Grenze",
        "txt_export_outlier_scope_path_specific": "Funkwegspezifisch",
        "txt_export_outlier_scope_directionally_coherent": "Richtungskohärent",
        "txt_export_outlier_scope_scope_wide": "Bereichsweit",
        "txt_export_outlier_scope_multiple_paths": "Mehrere Funkwege",
        "txt_export_outlier_departure_positive": "Über lokaler Baseline",
        "txt_export_outlier_departure_negative": "Unter lokaler Baseline",
        "txt_export_outlier_departure_mixed": "Gemischt",
        "txt_export_outlier_departure_neutral": "Keine gerichtete Abweichung",
        "txt_export_outlier_paired_unit_joint": "Joint Spot",

        "txt_export_outlier_yes": "Ja",
        "txt_export_outlier_no": "Nein",
        "txt_export_outlier_boundary_start": "Start",
        "txt_export_outlier_boundary_end": "Ende",
        "txt_export_outlier_boundary_start_and_end": "Start und Ende",
        "txt_export_outlier_warning_reference_missing": "Reference fehlt nahe einem positiven Ereignis",
        "txt_export_outlier_warning_target_missing": "Target fehlt nahe einem negativen Ereignis",
        "txt_outlier_direction_unavailable": "Nicht verfügbar",
        "fmt_outlier_minutes": "{value} min",
        "fmt_outlier_evidence_utc": "{timestamp} UTC",
        "fmt_outlier_utc_date": "{day:02d}.{month}. {time}",
        "fmt_outlier_utc_instant": "{timestamp} UTC",
        "fmt_outlier_utc_range": "{start}–{end} UTC",
        "txt_outlier_utc_months": "01|02|03|04|05|06|07|08|09|10|11|12",
        "lbl_include_unpaired_evidence": "Ungepaarte Evidenz einbeziehen",
        "hdr_results_success_evidence": "Performance-Evidenz",
        "sub_results_success_evidence": "Dekodierrate und Stärke erfolgreicher Signale nach berechneter Entfernung im aktiven Bereich.",
        "sub_results_success_temporal": "Abweichungen erfolgreicher Signalstärken, Stationsstützung, Volumen bestätigter Gelegenheiten und Gewichtungen der Dekodierrate, chronologisch und nach UTC-Stunde dargestellt.",
        "sub_results_station_insights": "Beitragende {station_type}-Stationen im aktiven Bereich. Wähle eine Zeile, um ihre Evidenz zu untersuchen.",
        "sub_results_station_insights_multi": "Beitragende {station_type}-Stationen im aktiven Bereich. Wähle eine oder mehrere Zeilen, um ihre Evidenz zu untersuchen.",
        "sub_results_station_insights_success": "Beitragende {station_type}-Stationen im aktiven Bereich. Wähle eine Zeile, um ihre Evidenz zu untersuchen.",
        "txt_results_station_scope": "Aktiver Bereich · {distance} · {direction} · {station_count}",
        "hdr_results_selected_station_evidence": "Evidenz der ausgewählten Station",
        "lbl_results_selected_station_named": "{selected_count} ausgewählte {station_type}-Stationen: {stations}",
        "lbl_results_selected_station_count": "{selected_count} ausgewählte {station_type}-Stationen",
        "sub_results_selected_station_single": "{station} ({locator}) · {evidence_count} {evidence_unit}",
        "sub_results_selected_station_named": "{selection_label} · kombinierte Ansicht · {evidence_count} {evidence_unit}",
        "sub_results_selected_station_multi": "{selection_label} · kombinierte Ansicht · {evidence_count} {evidence_unit}",
        "fmt_success_selected_context": "{station} ({locator}) · {distance_km} km · {azimuth_degrees}° {direction}\n{confirmed_opportunities} {opportunity_unit} · Dekodierrate {success_rate}% · Median Target-SNR {median_snr}",
        "abbr_compass_east": "O",
        "txt_results_selected_no_paired_evidence": "Für diese Auswahl liegt keine gepaarte Evidenz vor; beibehaltene ungepaarte Zeilen können unten weiterhin geprüft werden.",
        "hdr_results_drilldown": "Drill-Down-Daten",
        "sub_results_drilldown_single": "Evidenz auf Zeilenebene für {station} im aktiven Bereich.",
        "sub_results_drilldown_multi": "Evidenz auf Zeilenebene für {count} ausgewählte {station_type}-Stationen im aktiven Bereich.",
        "lbl_drilldown_zoom_window": "Zoom-Zeitfenster",
        "lbl_drilldown_center_date_utc": "Datum der Fenstermitte (UTC)",
        "lbl_drilldown_center_time_utc": "Uhrzeit der Fenstermitte (UTC)",
        "btn_drilldown_zoom_earlier": "← Früher",
        "btn_drilldown_zoom_later": "Später →",
        "lbl_drilldown_zoom_off": "Aus",
        "lbl_drilldown_zoom_outlier_focus": "Ausreißerfokus",
        "fmt_drilldown_zoom_time_window": "{identity} - Zeitfenster: {start} bis {end} UTC",
        "fmt_drilldown_zoom_selected_window": "Ausgewähltes Zeitfenster: {start} bis {end} UTC",
        "txt_drilldown_zoom_single_station_only": "Die gezoomte Evidenz ist nur verfügbar, wenn genau eine Station ausgewählt ist.",
        "fig_drilldown_native_performance_panel_title": "Erfolgreiches Target-SNR im Zeitverlauf",
        "fig_drilldown_native_benchmark_panel_title": "Δ SNR im Zeitverlauf",
        "fig_drilldown_native_time_x": "Datum/Uhrzeit (UTC)",
        "fig_drilldown_native_performance_y": "Normiertes Target-SNR (dB @ 30 dBm)",
        "fig_drilldown_native_benchmark_y": "Δ SNR (dB)",
        "fig_drilldown_native_performance_unavailable": "In diesem Zeitfenster ist kein erfolgreiches Target-SNR verfügbar. Erfolglose Gelegenheiten haben kein aufgezeichnetes Target-SNR.",
        "fig_drilldown_native_benchmark_unavailable": "In diesem Zeitfenster ist keine gepaarte Evidenz für Δ SNR verfügbar.",
        "fig_drilldown_native_joint_spot": "Einzelner Joint Spot",

        "fig_drilldown_native_successful_opportunity": "Einzelne erfolgreiche bestätigte Gelegenheit",
        "fig_drilldown_outlier_candidate": "Ausreißerkandidat",
        "fig_drilldown_outlier_focused_episode": "Fokussierte Episode",
        "fig_drilldown_outlier_expected_local_delta_snr": "Erwartetes lokales ΔSNR",
        "fig_drilldown_outlier_flank_baseline": "Baseline der Flanke davor/danach",
        "fmt_drilldown_outlier_robust_z_guide": "|robuster z-Wert| = {value:g}",
        "fmt_drilldown_outlier_qualifying_robust_z_guide": "|robuster z-Wert| = {value:g} (Qualifikationsschwelle)",
        "fmt_drilldown_outlier_absolute_departure_gate": "Gate der absoluten Abweichung (±{value:g} dB)",
        "lbl_filter_table": "Tabelle filtern",
        "txt_results_drilldown_filter_note": "Mit „Tabelle filtern“ wird nur die angezeigte Tabelle verändert; das Zoom-Zeitfenster begrenzt fokussierte Abbildungen und Tabelle, niemals die abgeschlossene Analyse.",
        "unit_joint_spot_singular": "Joint Spot",
        "unit_joint_spot_plural": "Joint Spots",


        "unit_confirmed_opportunity_singular": "bestätigte Gelegenheit",
        "unit_confirmed_opportunity_plural": "bestätigte Gelegenheiten",
        "unit_station_singular": "{count} beitragende {station_type}-Station",
        "unit_station_plural": "{count} beitragende {station_type}-Stationen",
        "hdr_results_download_evidence": "Evidenz herunterladen",
        "sub_results_download_evidence": "Stelle den abgeschlossenen Lauf, den aktiven Inspector-Bereich, die Stationsauswahl, Tabellen, Metadaten und hochauflösende Abbildungen als Reproduzierbarkeitspaket zusammen; Konfig speichern bewahrt die wiederverwendbaren Analyseeinstellungen separat.",
        "sub_documentation": "Methode, Interpretation, Bedienelemente, Grenzen und Fehlerbehebung.",
        "msg_preparing_all_results": "Hochaufloesendes Ergebnispaket wird vorbereitet...",
        "btn_prepare_documentation_pdf": "PDF vorbereiten",
        "btn_download_documentation_pdf": "PDF herunterladen",
        "btn_load_full_documentation": "Vollst\u00e4ndige Dokumentation laden",
        "btn_hide_full_documentation": "Vollst\u00e4ndige Dokumentation ausblenden",
        "msg_loading_analysis_engine": "Analyse-Engine wird vorbereitet...",
        "msg_preparing_inspector": "Segment-Inspektor und Drill-Down-Daten werden vorbereitet...",
        "msg_preparing_documentation_pdf": "Dokumentations-PDF wird vorbereitet...",
        "help_documentation_pdf_unavailable": "Der PDF-Export benoetigt die Abhaengigkeiten fuer Dokumentations-PDFs.",
        "msg_export_queue_wait": "Ein anderer Export wird vorbereitet. Sie sind auf Position {position} in der Export-Warteschlange.",
        "msg_export_queue_detail": "{active}/{maximum} Exportvorbereitung aktiv; {queued} warten.",
        "warn_export_queue_full": "Derzeit hohe Nachfrage. Die Export-Warteschlange ist voll. Bitte versuchen Sie es in Kuerze erneut.",
        "warn_export_queue_timeout": "Exportkapazitaet wurde nicht rechtzeitig frei. Bitte versuchen Sie es in Kuerze erneut.",
        "btn_reset": "Reset Konfig",
        "btn_run_analysis_rx": "RX-Analyse starten",
        "btn_run_analysis_tx": "TX-Analyse starten",
        "btn_select_analysis_direction": "RX- oder TX-Analyse auswählen",
        "cbar_abs_rx": "Stationsgleichgewichtete RX-Dekodierrate (%)",
        "cbar_abs_tx": "Stationsgleichgewichtete TX-Dekodierrate (%)",
        "map_success_footer_opportunities": "GELEGENHEITEN",
        "map_success_footer_stations": "STATIONEN",
        "success_rx_opportunity_success": "Vom Target gehört",
        "success_rx_opportunity_counter": "Nur von anderen gehört",
        "success_rx_station_success": "Vom Target gehört",
        "success_rx_station_counter": "Nur von anderen gehört",
        "success_rx_target_only_audit": "Nur vom Target gehört (in Erfolgen enthalten)",
        "success_rx_show_counter": "Nur von anderen Stationen gehört.",
        "success_tx_opportunity_success": "Target gehört",
        "success_tx_opportunity_counter": "Nur andere Signale gehört",
        "success_tx_station_success": "Target gehört",
        "success_tx_station_counter": "Nur andere Signale gehört",
        "success_tx_target_only_audit": "Nur Target gehört (in Erfolgen enthalten)",
        "success_tx_show_counter": "Nur andere Signale gehört.",
        "map_success_rx_opportunity_target": "Vom Target gehört",
        "map_success_rx_opportunity_counter": "Nur von anderen gehört",
        "map_success_rx_station_target": "Vom Target gehört",
        "map_success_rx_station_counter": "Nur von anderen gehört",
        "map_success_tx_opportunity_target": "Target gehört",
        "map_success_tx_opportunity_counter": "Nur andere Signale gehört",
        "map_success_tx_station_target": "Target gehört",
        "map_success_tx_station_counter": "Nur andere Signale gehört",
        "map_success_legend_insufficient": "Unzureichende Evidenz",
        "cbar_comp": "Stationsgleichgewichteter Median des \u0394SNR (dB)",
        "comp_title_ref": "{callsign} (Referenz)",
        "comp_title_local_median": "Lokaler Nachbarschafts-Median (≤{radius} km)",
        "dev_credit": f"Release {APP_VERSION} | Repo: <a href='https://github.com/markusthemaker/WSPRadar/' target='_blank' style='color:#39ff14; text-decoration:none;'>GitHub</a> | License: <a href='https://github.com/markusthemaker/WSPRadar/blob/main/LICENSE' target='_blank' style='color:#39ff14; text-decoration:none;'>AGPLv3</a><br>Developed by Dr. Markus Brosch (<a href='https://www.qrz.com/db/DL1MKS' target='_blank' rel='noopener noreferrer' aria-label='DL1MKS auf QRZ.com (öffnet in einem neuen Tab)' style='color:#39ff14; text-decoration:none; white-space:nowrap;'>DL1MKS<span aria-hidden='true' style='display:inline-block; color:#39ff14; font-size:0.95em; font-weight:700; line-height:1; margin-left:0.18em; text-decoration:none; vertical-align:0.08em;'>&#8599;</span></a>) ",
        "exp_adv": "Optionale Filter, Analyseumfang und Evidenz",
        "exp_comp": "Benchmark-Design",
        "exp_core": "Target und Messzeitraum",
        "exp_question": "Frage",
        "exp_metadata": "Metadaten",
        "fig_rx_abs": "RX Performance: {callsign} — Vom Target gehört vs. nur von anderen gehört",
        "fig_rx_comp": "RX-Benchmark: {callsign} (Target) vs. {comp_title}",
        "abs_rx_counter": "Elsewhere",
        "abs_rx_counter_short": "E",
        "abs_rx_target_column": "Target (T)",
        "abs_rx_pair": "Target+Elsewhere",
        "abs_rx_formula": "Target/(Target+Elsewhere)",
        "abs_rx_rate_column": "T/(T+E) (%)",
        "abs_rx_counter_column": "Elsewhere (E)",
        "abs_tx_counter": "Other Signals",
        "abs_tx_counter_short": "OS",
        "abs_tx_target_column": "Target (T)",
        "abs_tx_pair": "Target+Other Signals",
        "abs_tx_formula": "Target/(Target+Other Signals)",
        "abs_tx_rate_column": "T/(T+OS) (%)",
        "abs_tx_counter_column": "Other Signals (OS)",
        "fig_tx_comp": "TX-Benchmark: {callsign} (Target) vs. {comp_title}",
        "hlp_solar": """Wähle Tageslicht, Nacht oder Greyline am **Standort des Targets**; maßgeblich ist dieser Standort, nicht der gesamte Funkweg. Ganze 24h behält alle Sonnenzustände innerhalb deines Messzeitraums bei.""",
        "hlp_max_dist": """Beziehe nur **Gegenstationen** ein, deren Entfernung vom Target kleiner als dieser Wert ist. Dies verändert die Evidenz in Analyse, Karten, Inspector und Exporten; es **verringert nicht den Archivabruf**.""",
        "hlp_min_spots": """Mindestzahl an :primary[**Joint Spots**] je Gegenstation: Target–Referenz-Vergleiche aus **demselben WSPR-Zyklus**. Derselbe Mindestwert gilt **getrennt für einseitige Evidenz**, die eine Station nicht für ΔSNR qualifiziert.""",
        "hlp_min_opportunities_rx": """Mindestzahl **bestätigter Gelegenheiten** je entferntem Sender. Gezählt werden sowohl Target-Decodes als auch Aussendungen, die andere Empfänger hören, während das aktive Target sie nicht decodiert.""",
        "hlp_min_opportunities_tx": """Mindestzahl **bestätigter Gelegenheiten** je entferntem Empfänger. Gezählt werden sowohl Decodes des Targets als auch Zyklen, in denen derselbe Empfänger einen anderen qualifizierenden Sender hört, aber das aktive Target nicht decodiert.""",
        "hlp_min_stations_compare": """Mindestzahl qualifizierender Identitäten aus **Rufzeichen + vollständigem Locator** **je Kartensegment**. Jede muss die Mindestzahl an Joint Spots erfüllen; einseitige Evidenz zählt nicht. Dies sind gemeldete Identitäten, nicht zwingend unabhängige physische Stationen.""",
        "hlp_min_stations_success_rx": """Zeige ein **Kartensegment** nur, wenn diese Anzahl entfernter Sender die **Mindestzahl bestätigter Gelegenheiten** erfüllt. Stationen können sich qualifizieren, auch wenn das Target keines ihrer Signale decodiert hat.""",
        "hlp_min_stations_success_tx": """Zeige ein **Kartensegment** nur, wenn diese Anzahl entfernter Empfänger die **Mindestzahl bestätigter Gelegenheiten** erfüllt. Ein Empfänger kann sich qualifizieren, auch wenn er das Target nie decodiert hat.""",
        "hlp_benchmark_offset_db": """Wird vor der Berechnung von ΔSNR zum Referenz-SNR addiert. **Positive Werte senken ΔSNR; negative Werte erhöhen es.** Verwende 0,0 dB, sofern du keine dokumentierte Korrektur für diesen Vergleich hast.""",
        "err_benchmark_offset_db": "Gib einen Wert von -99.9 bis 99.9 mit Dezimalpunkt ein, zum Beispiel 1.2 oder -1.2.",
        "hlp_callsign_entry": """Gib die **exakte im WSPR-Archiv gespeicherte Meldekennung** **einschließlich eines etwaigen Suffixes** ein. Unterschiedliche Schreibweisen wählen unterschiedliche Identitäten aus.""",
        "hlp_target_qth": """Gib den **Maidenhead-Locator** des Targets für den ausgewählten Zeitraum ein. Er dient als Bezugspunkt für Stationsauswahl, Kartengeometrie, Entfernung und lokalen Sonnenstand.""",
        "hlp_band": """Analysiere jeweils ein WSPR-Band. Wähle das während des Messzeitraums verwendete Band.""",
        "hlp_time_window": """Wähle einen **UTC-Zeitraum**, in dem Stationskennungen, Standorte und Aufbau möglichst stabil waren. Längere Zeiträume liefern mehr Evidenz, können aber unterschiedliche Betriebs- und Ausbreitungsbedingungen mischen.""",
        "hlp_reference_callsign": """Gib das Referenzrufzeichen **einschließlich eines etwaigen Suffixes exakt so ein, wie es im WSPR-Archiv gemeldet wurde**. Beispielsweise sind `CALL` und `CALL/P` unterschiedliche Meldekennungen; gib die tatsächlich für deine Referenz gespeicherte Form ein.

WSPRadar bestimmt ihren Standort anhand des gewählten **Bands, der Analyserichtung und des UTC-Zeitraums**.""",
        "hlp_reference_radius": """**Maximale Entfernung** beitragender Referenzstationen vom Target. Ein größerer Radius kann zusätzliche Stationen einbeziehen, macht den Vergleich aber weniger lokal.""",
        "hlp_benchmark_reference_station": """Vergleiche das Target mit einem anderen kontrollierten Signalpfad oder einer bekannten Station am selben oder an einem anderen Standort. Der Vergleich spiegelt die **vollständigen Aufbauten und ihre Betriebsbedingungen** wider.""",
        "hlp_benchmark_local_neighborhood": """Vergleiche das Target für jede Gegenstation und jeden WSPR-Zyklus mit dem **Median** qualifizierender Beiträge benachbarter Stationen innerhalb des von dir gewählten Radius. Es wird keine einzelne feste Referenz ausgewählt; die **beitragenden Stationen können je nach Funkweg und Zyklus wechseln**.""",
        "fmt_reference_choice_selected": "{choice} (ausgewählt)",
        "fmt_reference_choice_help": "Hilfe zu {choice}",
        "lbl_band": "Frequenzband",
        "lbl_benchmark_offset_db": "Referenzseitige SNR-Korrektur (dB)",
        "lbl_config_file": "WSPRadar .config Datei auswaehlen",
        "lbl_demo_select": "Demo-Profil auswaehlen",
        "lbl_callsign": "Dein Rufzeichen (Target under Test)",
        "lbl_callsign_rx": "Target-Rufzeichen (Empfänger im Test)",
        "lbl_callsign_tx": "Target-Rufzeichen (Sender im Test)",
        "lbl_analysis_selector": "RX- oder TX-Analyse",
        "opt_analysis_rx": "RX-Analyse",
        "opt_analysis_tx": "TX-Analyse",
        "lbl_comp_mode": "Benchmark-Design",
        "lbl_question": "Frage",
        "txt_question_intro": """Als **Target** wird eine Station oder ein kontrollierter Signalpfad ausgewertet – wahrscheinlich deine Station. Wähle, ob du die RX- oder TX-Performance des Targets bewerten oder es gegen eine Referenz benchmarken möchtest:""",
        "lbl_end_d": "Enddatum (UTC)",
        "lbl_end_t": "Endzeit (UTC)",
        "lbl_insights": "Station Insights",
        "lbl_max_dist": "Maximale Peer-Entfernung vom Target (km)",
        "lbl_min_spots": "Minimale Joint-Evidenz pro Station",
        "lbl_min_opportunities": "Minimale bestätigte Gelegenheiten pro Station",
        "lbl_min_stations": "Minimale qualifizierte Stationen pro Kartensegment",
        "lbl_no_joint": "Keine gemeinsamen Spots in diesem Segment für ein \u0394-SNR-Histogramm vorhanden.",
        "lbl_qth": "Target-QTH (4 oder 6 Zeichen)",
        "lbl_ref_radius_km": "Nachbarschaftsradius (km)",
        "lbl_target_callsign": "Target-Rufzeichen",
        "lbl_reference_callsign": "Referenz-Rufzeichen",
        "ph_reference_callsign": "z. B. CALL/P",

        "txt_target": "Target",
        "txt_reference": "Referenz",
        "lbl_solar": "Sonnenstand am Target-QTH",
        "lbl_start_d": "Startdatum (UTC)",
        "lbl_start_t": "Startzeit (UTC)",
        "lbl_time_window": "UTC-Messzeitraum",
        "txt_benchmark_offset_note": "Ref SNR Corr: {offset:+.1f} dB",
        "opt_comp_none": "Performance — keine Referenz",
        "opt_comp_radius": "Benchmark — Referenznachbarschaft",
        "opt_comp_buddy": "Benchmark — Referenzaufbau/-station",
        "opt_benchmark_reference_station": "Referenzaufbau/-station",
        "opt_benchmark_local_neighborhood": "Referenznachbarschaft",
        "opt_question_rx_performance": "RX Performance",
        "opt_question_tx_performance": "TX Performance",
        "opt_question_rx_benchmark": "RX-Benchmark",
        "opt_question_tx_benchmark": "TX-Benchmark",
        "desc_question_rx_performance": """Bewerte, wie zuverlässig der Target-RX Peer-TX-Signale innerhalb bestätigter Gelegenheiten decodiert.""",
        "desc_question_tx_performance": """Bewerte, wie zuverlässig nachweislich aktive Empfänger das Target hören.""",
        "desc_question_rx_benchmark": """Vergleiche, was die Target- und Referenzempfänger unter zugeordneten Bedingungen hören.""",
        "desc_question_tx_benchmark": """Vergleiche, wie die Target- und Referenzsendepfade unter zugeordneten Bedingungen gehört werden.""",
        "opt_local_median": "Lokaler Nachbarschafts-Median",
        "err_local_benchmark": """Lokaler Nachbarschafts-Median ist die unterstützte lokale Methode. Verwende Reset Konfig, um gültige Eingaben wiederherzustellen.""",
        "err_reference_callsign_same": "Target- und Referenz-Rufzeichen m\u00fcssen verschieden sein.",
        "warn_tx_message_patterns_title": "WSPR-Nachrichtenfolgen der Sender prüfen",
        "warn_tx_message_patterns": """Diese Rufzeichen können unterschiedliche WSPR-Nachrichtenfolgen verwenden. Das kann die Anzahl einseitiger Meldungen und den Joint-Evidenzanteil verzerren.

Verwende für einen kontrollierten TX-Vergleich entweder zwei Standardrufzeichen mit Typ-1-Nachrichten oder zwei zusammengesetzte Rufzeichen mit synchronisierten Typ-2-/Typ-3-Nachrichtenfolgen. Wenn beide Sender dasselbe Basisrufzeichen verwenden, müssen beide unterschiedliche Zusätze tragen, zum Beispiel `CALL/1` und `CALL/2`. Prüfe, welche Zusätze für dein Rufzeichen und deinen Betrieb in deinem Land zulässig sind.

Prüfe, dass beide Sender in denselben Zwei-Minuten-Zyklen die jeweils gleichen Nachrichtentypen aussenden.""",
        "err_reference_callsign_required": "Bitte ein Referenz-Rufzeichen konfigurieren.",
        "err_reference_qth_required": "Bestimme den Referenzstandort vor dem Start der Analyse.",
        "err_callsign_format": "Bitte eine plausible Rufzeichen-/Meldekennung eingeben: 3-15 ASCII-Zeichen; '/' nur zwischen nicht leeren alphanumerischen Segmenten und h\u00f6chstens ein abschlie\u00dfendes '-' vor einem nicht leeren alphanumerischen Suffix verwenden. Der Teil vor einem etwaigen Bindestrich muss mindestens einen Buchstaben enthalten; eine Ziffer ist nicht erforderlich.",
        "err_qth_format": "Bitte einen g\u00fcltigen 4- oder 6-stelligen Maidenhead-Locator eingeben (z. B. JN37 oder JN37AA).",
        "err_time_invalid": "Bitte gültige UTC-Start- und Enddaten mit Uhrzeiten eingeben.",
        "err_time_before_minimum": "Der UTC-Start muss am oder nach dem 01.01.2008 um 00:00 UTC liegen.",
        "err_time_order": "Das UTC-Ende muss nach dem Start liegen.",
        "err_time_duration": "Der UTC-Messzeitraum darf höchstens 31 Tage umfassen.",
        "err_time_future": "Das UTC-Ende darf nicht nach der aktuellen UTC-Minute liegen.",
        "err_url_invalid": "Diese WSPRadar-Analyse-URL ist ung\u00fcltig und wurde nicht angewendet.",
        "err_url_unsupported_version": "Diese WSPRadar-Analyse-URL verwendet eine nicht unterst\u00fctzte Version und wurde nicht angewendet.",
        "err_reference_callsign_format": "Bitte ein plausibles Referenz-Rufzeichen eingeben: 3-15 ASCII-Zeichen; '/' nur zwischen nicht leeren alphanumerischen Segmenten und h\u00f6chstens ein abschlie\u00dfendes '-' vor einem nicht leeren alphanumerischen Suffix verwenden. Der Teil vor einem etwaigen Bindestrich muss mindestens einen Buchstaben enthalten; eine Ziffer ist nicht erforderlich.",
        "err_reference_grid4_format": "Der bestimmte Referenzstandort muss ein Maidenhead-Großfeld mit vier Zeichen sein. Starte die Standortsuche erneut.",
        "leg_both_async": "Beide (Async)",
        "leg_joint": "Beide (Sync)",
        "leg_only_me": "Nur {callsign}",
        "leg_only_ref": "Nur {ref_callsign}",
        "leg_only_ref_radius": "Nur Referenz",
        "msg_proc": "Verarbeite {id}...",
        "msg_analysis_queue_wait": "Alle Analysekapazitaeten sind belegt; Ihre Analyse wartet auf Position {position}.",
        "msg_analysis_submission_active": "Analyse uebermittelt; Analyse starten bleibt bis zum Abschluss deaktiviert.",
        "msg_config_loaded": "Konfiguration geladen. Bestehende Ergebnisse wurden geloescht.",
        "opt_all_dirs": "Alle Richtungen",
        "opt_full_range": "Gesamter Bereich",
        "opt_solar_all": "Ganze 24h",
        "opt_solar_day": "Tag (Elev > +6°)",
        "opt_solar_grey": "Greyline (-6° bis +6°)",
        "opt_solar_night": "Nacht (Elev < -6°)",
        "subtitle": "AMATEURFUNK STATION & ANTENNEN BENCHMARKING",
        "tbl_col_az": "Azimut",
        "tbl_col_joint": "Synced Spots",
        "tbl_col_km": "km",
        "tbl_col_loc": "Locator",
        "tbl_col_med_delta": "Median \u0394 SNR (dB)",
        "tbl_col_only_u": "Nur {callsign}",
        "tbl_col_cycle_ref_median": "Zyklus Ref-Median SNR (dB)",
        "tbl_col_delta_snr": "\u0394 SNR (dB)",
        "lbl_neighborhood": "Nachbarschaft",
        "tbl_col_ref_snr": "Ref SNR (dB)",
        "tbl_col_ref_station": "Ref Station",
        "tbl_col_rx": "RX Station",
        "tbl_col_success_station_rx": "TX-Station",
        "tbl_col_success_station_tx": "RX-Station",
        "tbl_col_success_rate": "Dekodierrate (%)",
        "tbl_col_success_snr": "Median Target-SNR (dB @ 30 dBm)",
        "tbl_col_success_counter_display_tx": "Andere Signale gehört",
        "tbl_col_success_snr_display": "Median-SNR @ 30 dBm",
        "fmt_results_success_station_summary": "Stationen: {success_label} {success_station_count} · {counter_label} {counter_station_count} · Stationsgleichgewichtete Dekodierrate {station_balanced_rate:.1f}%",
        "fmt_results_success_opportunity_summary": "Gelegenheiten: {success_label} {success_count} · {counter_label} {counter_count} · Dekodierrate auf Gelegenheitsebene {observation_level_rate:.1f}%",
        "txt_results_success_no_eligible": "Keine Station erfüllt in diesem Bereich die Schwelle für bestätigte Gelegenheiten.",
        "tbl_col_tx": "TX Station",
        "lbl_exclude_special": "Spezial-Rufzeichen Q, 0, 1 ausschließen",
        "hdr_remote_station_filters": "Remote Stationsfilter",
        "hdr_analysis_scope": "Analyseumfang",
        "hdr_evidence_requirements": "Evidenzanforderungen",
        "tt_exclude_special": """Schließe **entfernte Rufzeichen** aus, die mit **Q, 0 oder 1** beginnen und typischerweise für Ballontelemetrie verwendet werden. Target- und Referenzstationen einschließlich beitragender Nachbarschaftsstationen bleiben zulässig.""",
        "lbl_filter_moving": "Bewegliche Stationen filtern",
        "tt_filter_moving": """Schließe entfernte Rufzeichen aus, die aus **mehr als einem Gitterfeld mit vierstelligem Locator** gemeldet wurden. Locatorwechsel können Bewegung oder Meldefehler widerspiegeln; Bewegung innerhalb eines Felds wird nicht erkannt.""",
        "title": "WSPRadar.org",
        "txt_joint": "Synced",
        "txt_joint_decodes": "Synced Decodes",
        "txt_remote": "Total Remote",
        "txt_rx_stations": "RX Stationen",
        "txt_tx_stations": "TX Stationen",
        "warn_analysis_queue_full": "Hohe Auslastung. Die Analysewarteschlange ist voll. Bitte versuchen Sie es in Kuerze erneut.",
        "warn_analysis_queue_timeout": "Es wurde nicht rechtzeitig Analysekapazitaet frei. Bitte starten Sie die Analyse erneut.",
        "warn_analysis_result_row_limit": "Das Suchergebnis überschritt die sichere Grenze von **{max_rows} Zeilen**. Die Analyse wurde deshalb vor der Verarbeitung gestoppt; es wurde kein Teilergebnis ausgewertet. Verkürze den Analysezeitraum. {special_callsign_advice}**{max_peer_distance_label}** sowie Filter für bewegliche Stationen, Sonnenstand und Evidenz werden erst nach dem Abruf angewendet und können diese Grenze nicht vermeiden. Bei einem lokalen Nachbarschaftsvergleich kann ein kleinerer **{neighborhood_radius_label}** das Datenbankergebnis verkleinern.",
        "warn_analysis_result_row_limit_special_callsign_advice": "Das Aktivieren von **{special_callsign_label}** kann das Datenbankergebnis ebenfalls verkleinern. ",
        "status_analysis_result_row_limit": "Analyse an der sicheren Zeilengrenze gestoppt",
        "fig_mean_label": "Arithmetisches Mittel",
        "fig_share_percent_axis": "Anteil (%)",
        "fmt_temporal_title_with_bins": "{title} ({time_bin}-Intervalle)",
        "fig_decode_outcomes": "Decode Outcomes",
        "fig_station_medians_delta": "Stationsmediane (\u0394 SNR)",
        "fig_joint_spot_delta": "Joint-Spot \u0394 SNR",
        "fig_no_data": "Keine Daten",
        "msg_loading": "\u23f3 Wird geladen...",
        "fmt_results_selected_station_evidence_title": "{heading}: {selection_context}",
        "txt_snr_values_normalized_30dbm": "SNR-Werte sind auf 30 dBm normiert.",
        "lbl_filter": "Filter",
        "lbl_filter_columns": "Spalte(n) filtern:",
        "lbl_select_columns": "Spalten ausw\u00e4hlen",
        "fmt_results_selected_range_count": "{count} Bereiche",
        "fmt_results_selected_direction_count": "{count} Richtungen",
        "msg_results_no_stations_in_scope": "Keine Stationen im ausgew\u00e4hlten Bereich.",
        "txt_station_insights_normalized_30dbm": "Norm. @ 30 dBm. F\u00fcr Details klicken",
        "msg_drilldown_no_stations_selected": "Keine Station ausgew\u00e4hlt.",
        "msg_drilldown_no_spots": "Keine Spots verf\u00fcgbar.",


        "msg_drilldown_no_joint_spots": "F\u00fcr die ausgew\u00e4hlte Station sind keine Joint Spots verf\u00fcgbar.",
        "msg_drilldown_no_reference_station_details": "F\u00fcr die ausgew\u00e4hlte Station sind keine Details zur Referenzstation verf\u00fcgbar.",
        "warn_analysis_cache_expired": "Die Cache-Datei ist abgelaufen. Bitte f\u00fchre die Analyse erneut aus.",
        "err_analysis_evidence_schema_invalid": "Die Analyse-Evidenz konnte nicht gelesen werden, weil ihr Schema ung\u00fcltig ist.",
        "err_analysis_processing_failed": "Die Analyse-Evidenz konnte nicht vorbereitet werden. Bitte f\u00fchre die Analyse erneut aus.",
        "err_analysis_configuration_invalid": "Die Analysekonfiguration ist ung\u00fcltig. Pr\u00fcfe die Eingaben und versuche es erneut.",
        "err_config_validation_field": "Ung\u00fcltige Konfiguration bei {field_path}.",
        "err_config_validation_generic": "Die Konfiguration ist ung\u00fcltig.",
        "fmt_export_reference_correction_suffix": " (Referenzkorrektur {value:+.1f} dB)",
        "export_weighting_single_selected_path": "Ein ausgew\u00e4hlter Funkweg",
        "export_weighting_combined_observation": "Kombinierte beobachtungsgewichtete Evidenz",
        "map_footer_time": "Zeitraum: {value}",
        "map_footer_band": "Band: {value}",
        "map_footer_solar": "Sonnenstand: {value}",

        "map_footer_joint_pairs_per_station": "Joint-Paare/Station: \u2265{threshold}",
        "map_footer_joint_spots_per_station": "Joint Spots/Station: \u2265{threshold}",
        "map_footer_joint_stations_per_segment": "Joint-Stationen/Segment: \u2265{threshold}",
        "map_footer_schedule": "Zeitplan: {interval} min / T {target_start:02d} / R {reference_start:02d} UTC",
        "map_footer_reference": "Referenz: {reference}",
        "map_performance_footer_confirmed_opportunities_per_station": "Best\u00e4tigte Gelegenheiten/Station: \u2265{threshold}",
        "map_performance_footer_stations_per_segment": "Stationen/Segment: \u2265{threshold}",
        "map_performance_footer_segment_metric": "Segment: Stationsgleichgewichtete Dekodierrate",
        "map_compare_footer_pairs": "PAARE",
        "map_compare_footer_spots": "SPOTS",
        "pdf_metric_decode_rate": "Dekodierrate",
        "pdf_formula_correction": "Korrektur",
        "pdf_formula_delta_snr": "Delta SNR",
        "pdf_formula_approx": "ca.",
        "pdf_page_label": "Seite",
        "warn_no_data": "Nicht genügend qualifizierte Daten für **{title}** nach Anwendung der Filter gefunden. Sind Rufzeichenangaben, Locator, Band, Datum und UTC-Zeit korrekt?",
        "warn_no_source_rows": "Für **{title}** wurden keine Quellzeilen geliefert. Prüfe die exakte Rufzeichen- oder Meldeidentität, den Locator, das Band, den UTC-Zeitraum und den tatsächlichen Betrieb. Die aktiven Filter, der Analyseumfang und die Evidenzanforderungen stehen oben im Prüfbereich.",
        "warn_no_target_mode_evidence": """Für das Target wurden keine Meldungen gefunden, die bei dem gewählten Rufzeichen, Locator, Band und Zeitraum dem erforderlichen **WSPR-2-Modusfilter** entsprechen. WSPR-2 ist der Standard-WSPR-Modus mit zweiminütigen Sendezyklen. WSPRadar filtert die Meldungen anhand der in der Datenbank gespeicherten Modusangabe (`code = 1`).

Bei älteren Archivmeldungen können Modusangaben fehlen oder mehrdeutig sein. WSPRadar wiederholt die Abfrage automatisch ohne diesen Filter nur dann, wenn der **gesamte gewählte Zeitraum vor dem 1. Januar 2022 (UTC)** liegt. Dein gewählter Zeitraum reicht über diesen historischen Kompatibilitätsbereich hinaus, daher bleibt der Modusfilter aktiv.""",
        "warn_source_rows_filtered_out": "Die Quelle lieferte **{source_row_count} Zeilen** für **{title}**, nach Anwendung der aktiven nachgelagerten Filter und des Analyseumfangs blieb jedoch keine Zeile erhalten. Dies belegt für sich allein nicht, dass der Umfang zu eng war. Die angewandte Konfiguration steht oben im Prüfbereich.",
        "warn_performance_no_eligible_station": "Die aktiven Filter und der Umfang behielten **{station_identity_count} Stationsidentitäten (Rufzeichen + Locator)** für **{title}** bei, aber keine erfüllte die Evidenzanforderung je Station. Höchster beobachteter Wert: **{maximum_confirmed_opportunities_per_station} bestätigte Gelegenheiten**; erforderlich: **mindestens {minimum_confirmed_opportunities_per_station} je Station**. Leere Karten-, Inspector- und Tabellenbestandteile werden nicht angezeigt. Die angewandte Konfiguration steht oben im Prüfbereich.",
        "warn_performance_no_qualifying_segment": "**{eligible_station_count} Stationsidentitäten** erfüllten die Evidenzanforderung je Station für **{title}**, aber kein Kartensegment erfüllte seine Stationsanforderung. Höchster beobachteter Wert: **{maximum_stations_per_segment} qualifizierte Stationen in einem Segment**; erforderlich: **mindestens {minimum_qualifying_stations_per_map_segment} je Kartensegment**. Evidenz auf Stationsebene bleibt unten verfügbar; nur segmentabhängige Ausgaben entfallen. Die angewandte Konfiguration steht oben im Prüfbereich.",
        "warn_benchmark_no_qualifying_result_simultaneous": "Für **{title}** war nach Anwendung der aktiven Filter, des Analyseumfangs und der Evidenzanforderungen kein qualifizierendes Benchmark-Ergebnis verfügbar. Erforderlich: **mindestens {minimum_joint_evidence_per_station} Joint-Beobachtungen je Station** und **mindestens {minimum_qualifying_stations_per_map_segment} qualifizierte Stationen je Kartensegment**. Dies belegt für sich allein nicht, dass der Umfang zu eng war. Die angewandte Konfiguration steht oben im Prüfbereich.",

        "ph_target_callsign": "z. B. CALL",
        "txt_reference_location_resolved": "Referenzstandort: {grid4}",
        "txt_reference_location_pending": "Der Referenzstandort wird beim Start der Analyse für den gewählten Zeitraum aus der Datenbank bestimmt.",
    }
}


# Result guidance is shared by Guided and Classic because both input editors
# render the same completed-result hierarchy. Keep this content separate from
# ``GUIDED_INPUTS``: it explains how to read established result contracts and
# must never select scientific behavior.
RESULT_GUIDANCE = {
    "en": {
        "trigger": 'How to read this',
        "trigger_help": 'How to read {section}',
        "read_label": 'What this view shows and how to read it.',
        "limits_label": 'Keep in mind.',
        "context_layout": """**Read from top to bottom**

<strong class="defined-term">{map_heading} → {segment_heading} → {evidence_heading} → {temporal_heading} → {stations_heading} → {selected_heading} → {drilldown_heading}</strong>

<strong class="defined-term">{map_heading}</strong> gives the geographic overview; **{segment_heading}** lets you choose the geographic scope for the sections below.

<strong class="defined-term">{evidence_heading}</strong> summarizes station results and the observations behind them; **{temporal_heading}** shows how the patterns and their supporting evidence vary over time.

<strong class="defined-term">{stations_heading}</strong> lets you compare individual remote stations; **{selected_heading}** follows your selection over time, and **{drilldown_heading}** exposes the underlying observations.

Start with the geographic overview, narrow the scope, then compare stations and time periods. Select a station to examine its evidence and trace the pattern to individual observations.""",
        "sections": {
            "context_rx_success": {
                "read": """<strong class="defined-term">RX Performance Results</strong> show where and how often your Target receiving station decoded remote transmitters within confirmed reception opportunities. Use the results to explore geographic reach, Decode Rate, and successful signal levels, and how these vary across stations and time.""",
                "limits": """These results describe the complete receiving station within retained opportunities, not every signal that may have reached it. They cannot identify why a decode failed or provide calibrated measurements of receiver sensitivity, antenna gain, or efficiency.""",
            },
            "context_tx_success": {
                "read": """<strong class="defined-term">TX Performance Results</strong> show where and how often remote receivers decoded your Target transmitter within confirmed reception opportunities. Use the results to explore geographic reach, Decode Rate, and successful signal levels, and how these vary across receivers and time.""",
                "limits": """These results describe the complete transmitting station within retained opportunities, not unconditional coverage. They do not measure actual radiated power or calibrated antenna gain or efficiency.""",
            },
            "context_rx_compare": {
                "read": """<strong class="defined-term">RX Benchmark Results</strong> compare your Target receiving setup with the selected Reference. They show where and when relative signal levels differ, how those differences vary across remote transmitters, and how much paired and one-sided evidence supports the comparison.""",
                "limits": """ΔSNR exists only where both sides supplied usable evidence. These paired observations may differ from signals decoded by only one side. The comparison describes complete receiving paths; different sites, noise conditions, hardware, and propagation remain relevant. Attributing a difference to one component requires independent control of the other differences.""",
            },
            "context_tx_compare": {
                "read": """<strong class="defined-term">TX Benchmark Results</strong> compare your Target transmitting setup with the selected Reference. They show where and when relative signal levels differ, how those differences vary across remote receivers, and how much paired and one-sided evidence supports the comparison.""",
                "limits": """ΔSNR exists only where both signals were decoded; an undecoded signal has no SNR to normalize. The result compares complete transmitting paths and relies on reported power, which need not equal actual output or radiated power. Attributing a difference to one antenna or component requires independent control of the other differences.""",
            },
            "benchmark_reference": {
                "read": """<strong class="defined-term">Reference Setup/Station</strong> uses **one selected Reference callsign** within the **four-character locator** resolved from the archive period. It may represent another controlled signal path at the Target site or a station at a different location. The same-cycle pairing rules apply in either case.

A controlled comparison can investigate antennas, feedlines, radios, or complete setups; an independent station comparison also includes the other installation and environment.

Check whether the observed difference persists across remote stations and time. A calibrated comparison, or swapping the component between setups, can help investigate whether the difference follows that component.""",
                "limits": """Sharing a four-character locator does not establish co-location. The Reference is a comparison setup, not automatically a calibrated standard. Site, terrain, noise, equipment, and operating differences limit what can be attributed to an individual component.""",
            },
            "benchmark_local_median": {
                "read": """<strong class="defined-term">Reference Neighborhood (Local Median)</strong> compares the Target with qualifying observations from stations within **{radius} km**: nearby receivers for RX, or nearby transmitters for TX.

For each remote station and WSPR cycle, each contributing local callsign-and-locator identity supplies **one SNR value**. The Reference is their <strong class="defined-term">median</strong>: the middle value, or the average of the middle two values. **Contributors can change** from one radio path or cycle to another.

Read ΔSNR alongside **Joint Evidence Share** and **Decode Outcomes**, then use **Drill-Down** to inspect the local contributors. Check whether changes in the Target–Reference difference coincide with changes in the contributing stations.""",
                "limits": """This Reference represents observed contributors, not every nearby station or a fixed calibrated standard; a cycle may have only one contributor. Differences in equipment, sites, noise, reported power, and propagation remain part of the result. A neighborhood comparison cannot isolate antenna gain.""",
            },
            "map_compare_rx": {
                "read": """Map View shows where the RX Benchmark difference appears around the Target.

Each shaded distance-and-direction <strong class="defined-term">map segment</strong> summarizes qualifying remote transmitter identities, distinguished by callsign and reported locator. WSPRadar first finds each station’s median ΔSNR, then takes the median of those station values. This <strong class="defined-term">station-balanced</strong> summary gives each qualifying identity **one contribution**, regardless of its spot count. **Positive values favor the Target**; **negative values favor the Reference**.

Markers summarize retained evidence: <strong class="defined-term">Both (Joint)</strong> meets the Joint Spot requirement; <strong class="defined-term">Both (Async)</strong> has qualifying one-sided evidence on both sides but **no qualifying Joint summary**; <strong class="defined-term">Only …</strong> names the side with qualifying evidence alone.

<strong class="defined-term">STATIONS</strong> counts identities, while <strong class="defined-term">SPOTS</strong> counts retained paired and unpaired observations. The async portion of SPOTS can also include **unpaired observations from Joint-classified stations**.

Read segment color together with station breadth and observation counts, then investigate the pattern in **Segment Inspector**.""",
                "limits": """Evidence minimums affect the marker groups; “Async” does not prove that no pairs existed. An uncolored segment has no qualifying summary, not a measured zero difference. The symmetric dB scale spans at least −6 to +6 dB and can expand between runs, so compare color-bar numbers rather than colors alone. The pale band around zero is a display interval; only 0 dB means equality. The map does not establish propagation mode, radiation angle, calibrated gain, or physical cause.""",
            },
            "map_compare_tx": {
                "read": """Map View shows where the TX Benchmark difference appears around the Target.

Each shaded distance-and-direction <strong class="defined-term">map segment</strong> summarizes qualifying remote receiver identities, distinguished by callsign and reported locator. WSPRadar first finds each receiver’s median ΔSNR, then takes the median of those station values. This <strong class="defined-term">station-balanced</strong> summary gives each qualifying identity **one contribution**, regardless of its report count. **Positive values favor the Target**; **negative values favor the Reference**.

Markers summarize retained evidence: <strong class="defined-term">Both (Joint)</strong> meets the Joint Spot requirement; <strong class="defined-term">Both (Async)</strong> has qualifying one-sided evidence on both sides but **no qualifying Joint summary**; <strong class="defined-term">Only …</strong> names the side with qualifying evidence alone.

<strong class="defined-term">STATIONS</strong> counts receiver identities, while <strong class="defined-term">SPOTS</strong> counts retained paired and unpaired observations. The async portion of SPOTS can also include **unpaired observations from Joint-classified receivers**.

Read segment color together with receiver breadth and observation counts, then investigate the pattern in **Segment Inspector**.""",
                "limits": """Evidence minimums affect the marker groups; “Async” does not prove that no pairs existed. An uncolored segment has no qualifying summary, not a measured zero difference. The symmetric dB scale spans at least −6 to +6 dB and can expand between runs, so compare color-bar numbers rather than colors alone. The pale band around zero is a display interval; only 0 dB means equality. Undecoded signals have no SNR to compare, and the map does not establish actual radiated power or physical cause.""",
            },
            "map_success_rx": {
                "read": """Map View shows the geographic pattern of RX Decode Rate within retained reception opportunities.

For each qualifying remote transmitter identity — callsign and reported locator — WSPRadar divides successful Target decodes by that transmitter’s confirmed opportunities. A shaded distance-and-direction <strong class="defined-term">map segment</strong> shows the **arithmetic mean** of those individual percentages: the <strong class="defined-term">Station-balanced Decode Rate</strong>. Each identity has **equal weight** even when its opportunity count differs.

A dark-green marker means <strong class="defined-term">Heard by Target</strong> **at least once**; it **does not mean every opportunity succeeded**. A light-gray marker means <strong class="defined-term">Heard by others only</strong>, with no Target decode in the retained opportunities.

<strong class="defined-term">STATIONS</strong> counts transmitter identities; <strong class="defined-term">OPPORTUNITIES</strong> counts individual successes and misses. Markers and footer counts can include eligible stations in segments that **lack enough stations for shading**.

Compare color, station count, and opportunity count before narrowing the view in **Segment Inspector**.""",
                "limits": """An uncolored segment has no qualifying summary; it is not evidence of zero reception. The map describes confirmed, retained opportunities, not unconditional coverage or calibrated receiver sensitivity. Even 100% applies only to those opportunities. The map cannot explain why a particular signal was or was not decoded.""",
            },
            "map_success_tx": {
                "read": """Map View shows the geographic pattern of TX Decode Rate within retained reception opportunities.

For each qualifying remote receiver identity — callsign and reported locator — WSPRadar divides successful Target decodes by that receiver’s confirmed opportunities. A shaded distance-and-direction <strong class="defined-term">map segment</strong> shows the **arithmetic mean** of those individual percentages: the <strong class="defined-term">Station-balanced Decode Rate</strong>. Each identity has **equal weight** even when its opportunity count differs.

A dark-green marker means <strong class="defined-term">Target heard</strong> **at least once**; it **does not mean every opportunity succeeded**. A light-gray marker means <strong class="defined-term">Other signals heard only</strong>, with no Target decode in the retained opportunities.

<strong class="defined-term">STATIONS</strong> counts receiver identities; <strong class="defined-term">OPPORTUNITIES</strong> counts individual successes and misses. Markers and footer counts can include eligible receivers in segments that **lack enough stations for shading**.

Compare color, receiver count, and opportunity count before narrowing the view in **Segment Inspector**.""",
                "limits": """An uncolored segment has no qualifying summary; it is not evidence of zero reception. The map describes confirmed active receivers within retained opportunities, not unconditional coverage, actual radiated power, or calibrated antenna efficiency. Even 100% applies only to those opportunities, and missing decodes do not establish their cause.""",
            },
            "segment": {
                "read": """<strong class="defined-term">Segment Inspector</strong> lets you examine a distance-and-direction subset of the completed Benchmark run. The controls define the <strong class="defined-term">active scope</strong> used by Benchmark Evidence, Temporal Evidence, Station Insights, and Selected Station Evidence below.

**Read together.** Start with the complete scope, narrow it to the directions or distances relevant to your question, and check whether the ΔSNR pattern is shared across several stations or concentrated in a few.""",
                "limits": """Changing scope filters the completed run; it does not fetch new observations or restore stations excluded by the original settings. Many Joint Spots from a few stations do not provide the same geographic breadth as observations from many stations. Neither count establishes independence, experimental control, or physical cause.""",
            },
            "segment_success_rx": {
                "read": """<strong class="defined-term">Segment Inspector</strong> lets you examine RX Performance within selected distances and directions from the Target. These controls define the <strong class="defined-term">active scope</strong> used by the following figures and station tables.

The station summary counts qualifying TX stations <strong class="defined-term">Heard by Target</strong> at least once and those <strong class="defined-term">Heard by others only</strong> throughout the retained observations. Its <strong class="defined-term">Station-balanced Decode Rate</strong> averages the individual TX-station rates, giving **each station equal weight**.

The opportunity summary counts successful Target decodes and confirmed missed decodes; its <strong class="defined-term">Opportunity-level Decode Rate</strong> is **successful opportunities divided by all confirmed opportunities**. Stations with many opportunities therefore influence this second rate more.

**Read together.** Read both rates with the station and opportunity counts, then use Station Insights to investigate differences.""",
                "limits": """Similar overall rates do not prove that individual stations behave alike. The rates describe confirmed opportunities during observed Target activity, not every possible transmission. Changing scope cannot recover evidence excluded by the original settings or establish why a decode was missed.""",
            },
            "segment_success_tx": {
                "read": """<strong class="defined-term">Segment Inspector</strong> lets you examine TX Performance within selected distances and directions from the Target. These controls define the <strong class="defined-term">active scope</strong> used by the following figures and station tables.

The station summary counts qualifying RX stations where the <strong class="defined-term">Target was heard</strong> at least once and those where <strong class="defined-term">Other signals were heard only</strong> throughout the retained observations. Its <strong class="defined-term">Station-balanced Decode Rate</strong> averages the individual receiver rates, giving **each receiver equal weight**.

The opportunity summary counts successful Target reports and confirmed missed opportunities; its <strong class="defined-term">Opportunity-level Decode Rate</strong> is **successful opportunities divided by all confirmed opportunities**. Receivers with many opportunities therefore influence this second rate more.

**Read together.** Read both rates with the receiver and opportunity counts, then use Station Insights to investigate differences.""",
                "limits": """Similar overall rates do not prove that individual receivers behave alike. The rates describe confirmed active receivers during observed Target activity, not unconditional coverage. Changing scope cannot recover excluded evidence or establish transmit power, antenna efficiency, or the cause of a missed decode.""",
            },
            "comparison_evidence_joint": {
                "read": """Benchmark Evidence shows how much evidence is paired, how stations differ, and how individual paired observations vary. A <strong class="defined-term">Joint Spot</strong> contains Target and Reference evidence for the same remote transmitter in RX, or the same remote receiver in TX, in one WSPR cycle. Read the three panels from left to right.

<strong class="defined-term">Decode Outcomes</strong> shows **percentages** (**Share (%)**): hatched bars (**Stations**) use the **total station count**, while solid bars (**Spots**) use the **total spot count**. At station level, Joint meets the **paired-evidence minimum**; Both (Async) has qualifying one-sided evidence on both sides but **no qualifying Joint summary**; Only Target or Only Reference has qualifying evidence on one side alone. In the Spots bars, Both (Async) **also includes qualifying unpaired observations** from Joint-classified stations. Total and Joint counts above the figure show the corresponding evidence volume.

<strong class="defined-term">Station Medians (Δ SNR)</strong> gives **each qualifying station one median paired difference**. The bars show the **percentage of stations** in each ΔSNR range; a narrow cluster means their median differences are similar.

<strong class="defined-term">Joint-Spot Δ SNR</strong> gives **each Joint Spot one value**, so frequently observed stations contribute more. The bars show the **percentage of Joint Spots** in each range, revealing how much individual comparisons vary across stations and time.

**Read together**

Read **ΔSNR in dB** on the horizontal axis: positive favors Target, negative favors Reference, and **0 dB means equality**. Both distributions show percentages **within their own population**. The median describes the **central value**; the mean is the **arithmetic average**. Compare their centers and spread to assess whether the station summaries and individual observations show a similar pattern, then check the station and spot counts behind it.""",
                "limits": """The ΔSNR panels describe qualifying paired evidence only. Categories reflect the configured minimums; a category that fails its threshold does not prove that no such observations existed. Station and spot classifications are not interchangeable. Similar distribution centers can conceal differing paths, and repeated observations do not establish independence or physical cause.""",
            },
            "temporal_evidence_joint": {
                "read": """Temporal Evidence shows when the paired ΔSNR pattern occurs and how much evidence supports it.

<strong class="defined-term">Δ SNR over Time</strong> shows time from left to right and ΔSNR vertically across the selected UTC window, grouping Joint Spots into your chosen time intervals; bins begin at the selected start and the last may be shorter.

<strong class="defined-term">Δ SNR by UTC Hour</strong> combines the same hour from different dates to reveal recurring daily patterns.

Positive values favor Target, negative values favor Reference, and **0 dB means equality**. The red dashed line is the **median of all qualifying Joint Spots in scope**; pale markers show **bin medians**. The <strong class="defined-term">IQR</strong>, bounded by Q1 and Q3, spans the **middle 50%** of a bin’s values when **at least five Joint Spots** contribute. Color shows **relative observation concentration** within each panel: blue cells contain a lower concentration of Joint Spots, orange/red cells a higher concentration; read ΔSNR from the labeled, **nonlinear dB axis**.

Blank intervals contain **no Joint evidence**, not a 0 dB result. The UTC-hour view requires evidence from **at least two dates**.

**Read together**

Follow the bin medians to see when the typical Target–Reference difference changes, then check station breadth, observation volume, and Joint share at those times in **Benchmark Temporal Evidence Coverage**.""",
                "limits": """Q1–Q3 describes spread, not a confidence interval. Recurring UTC patterns do not establish cause.""",
            },
            "temporal_evidence_coverage_joint": {
                "read": """<strong class="defined-term">Benchmark Temporal Evidence Coverage</strong> shows how much comparison evidence supports the paired ΔSNR pattern, including Only Target and Only Reference evidence.

<strong class="defined-term">Station-balanced Joint Evidence Share</strong>. In the chronological view, the upper bars give **each station one vote** divided among its outcomes, so their total height counts stations; the blue line **averages station Joint shares**.

<strong class="defined-term">Outcome-level Joint Evidence Share</strong>. The lower bars count <strong class="defined-term">comparison units</strong> — one remote station in one WSPR cycle — split into Only Target, Joint, and Only Reference; the amber line is **Joint units divided by all retained units**.

UTC-hour bars show **daily average participation or counts**, while the blue line still gives **each distinct station one rate vote**. Each UTC-hour view requires evidence from **at least two dates**.

**Read together.** Check the ΔSNR pattern against station breadth, observation volume, and Joint share.""",
                "limits": """Benchmark retains cycles with observed Target activity: the Target decoded a qualifying signal in RX or was decoded somewhere in TX. Reference has no equivalent gate. One-sided outcomes therefore describe conditional evidence availability, not symmetric wins or losses; Joint Spots already contain both sides. Joint share measures pairability, not Target success. Similar aggregate shares do not prove station agreement, and recurring UTC patterns do not establish cause.""",
            },
            "outlier_report": {
                "read": """Outlier Report highlights unusual changes in paired ΔSNR for closer inspection. A <strong class="defined-term">path</strong> is one remote callsign-and-locator identity; a <strong class="defined-term">Joint Spot</strong> is its paired Target–Reference observation from one WSPR cycle. WSPRadar estimates a local baseline from supported evidence before and after a candidate, excluding the candidate itself. A <strong class="defined-term">residual</strong> is observed ΔSNR minus that baseline.

Read <strong class="defined-term">Expected local ΔSNR</strong> as the baseline, <strong class="defined-term">Observed median ΔSNR</strong> as the candidate’s central paired value, and <strong class="defined-term">Largest single-cycle departure</strong> as its greatest departure in magnitude from the baseline, retaining its sign.

<strong class="defined-term">Spot impulse</strong>, <strong class="defined-term">short burst</strong>, and <strong class="defined-term">sustained excursion</strong> describe the span of grouped observations. All use the same configured requirements for **median departure**, **robust z-score** — a departure measured relative to local scatter — and **stability between the before/after baselines**. Reported intervals begin and end at observations passing both point-level departure requirements; weaker observations may remain between those endpoints.

Each Path block identifies the station, direction, UTC interval, **observation count**, and **timing gaps**. A single observation has no interval or gap to report.

`↓ Show in Station Insights` selects that path and prepares its Outlier Focus; `↓ Show Drill-Down Details` opens the corresponding detailed view. Multi-path cards also offer `Show all qualifying paths in Station Insights`.

Where available, <strong class="defined-term">Chronological WSPR-cycle evidence</strong> lists the paired observations, baseline, ΔSNR, and residual in time order.

**Read together.** Compare expected and observed ΔSNR first, then check the observation count, gaps, and individual evidence.""",
                "limits": """Candidates are inspection prompts, not established physical events or identified mechanisms. Sparse evidence or inadequate support before and after a candidate can leave observations unassessed; this does not classify them as normal. Durations and gaps describe listed observations, not transmitter schedules or an unseen event’s duration. Several paths do not establish independence or common cause. ΔSNR alone cannot determine whether Target, Reference, or both changed. The report uses processed Joint Spots, not untouched provider rows.""",
            },
            "outlier_focus": {
                "read": """<strong class="defined-term">Outlier Focus</strong> shows one reported candidate together with the supporting observations before and after it.

The ΔSNR points are **individual retained Joint Spots** at their **actual cycle times**.

The shaded <strong class="defined-term">Focused episode</strong> band identifies the selected candidate.

<strong class="defined-term">Expected local ΔSNR</strong> is its estimated baseline; the before/after baseline lines show the surrounding level used to assess stability.

Symmetric **robust-z guides** at 1, 2, 3, and the configured threshold show departure relative to local scatter. The **absolute-departure guides** show the required difference in dB.

**Stars** mark observations belonging to reported candidates that **individually pass both departure requirements**. The displayed guides belong to the focused episode; another starred candidate may have been assessed against a different baseline and scatter.

In the all-path temporal summary, one star represents the strongest individually qualifying observation in each reported event, which can differ from the report’s **Largest single-cycle departure**.

**Read together.** Compare the candidate points with the observations before and after, then check the report’s counts and time gaps.""",
                "limits": """These guides are detector criteria, not confidence intervals. Crossing one line alone does not satisfy all requirements for support, baseline stability, grouped departure, robust score, and sign agreement. The shaded band includes small display padding and is clipped to the selected window; it does not measure a physical event’s duration. A flagged departure does not identify its cause.""",
            },
            "success_evidence_rx": {
                "read": """Performance Evidence shows how RX results vary with distance across qualifying TX stations in the active scope. Read its three panels from left to right.

<strong class="defined-term">TX Stations Heard by Target at Least Once by Distance</strong> shows the percentage of qualifying transmitters in each distance bin that the Target decoded **at least once**.

<strong class="defined-term">RX Decode Rate by TX-Station Distance</strong> compares **equal weighting** of individual station rates with a rate calculated from **all successful and missed opportunities together**; frequently observed stations influence the latter more. The two lines are labeled **Station-balanced Decode Rate** and **Opportunity-level Decode Rate**, respectively.

<strong class="defined-term">Successful Target SNR by TX-Station Distance</strong> first calculates each transmitter’s median successful SNR, then shows the median of those station values in each distance bin. SNR is normalized to a common transmit-power basis of **30 dBm (1 W)** **using reported power**. With **two contributing stations**, Min-Max spans their two medians; with **three or more**, <strong class="defined-term">IQR</strong> spans the **middle 50%** of station medians.

**Read together.** Read the panels as at-least-once reception, Decode Rate, and signal strength when decoded. Check the supporting station and opportunity counts before comparing distance bins.""",
                "limits": """At-least-once reception depends on the window length and available activity. Distance comes from reported locators. Successful SNR excludes missed decodes, and power normalization depends on reported power; it does not calibrate antennas or receiver chains. The rates describe confirmed opportunities during observed Target activity.""",
            },
            "success_evidence_tx": {
                "read": """Performance Evidence shows how TX results vary with distance across qualifying RX stations in the active scope. Read its three panels from left to right.

<strong class="defined-term">RX Stations Hearing the Target at Least Once by Distance</strong> shows the percentage of qualifying receivers in each distance bin that reported the Target **at least once**.

<strong class="defined-term">TX Decode Rate by RX-Station Distance</strong> compares **equal weighting** of individual receiver rates with a rate calculated from **all successful and missed opportunities together**; frequently observed receivers influence the latter more. The two lines are labeled **Station-balanced Decode Rate** and **Opportunity-level Decode Rate**, respectively.

<strong class="defined-term">Successful Target SNR by RX-Station Distance</strong> first calculates each receiver’s median successful Target SNR, then shows the median of those receiver values in each distance bin. SNR is normalized to a common transmit-power basis of **30 dBm (1 W)** **using reported power**. With **two contributing receivers**, Min-Max spans their two medians; with **three or more**, <strong class="defined-term">IQR</strong> spans the **middle 50%** of receiver medians.

**Read together.** Read the panels as at-least-once reach, Decode Rate, and signal strength when decoded. Check the supporting receiver and opportunity counts before comparing distance bins.""",
                "limits": """At-least-once reach depends on the window length and available receiver activity. Distance comes from reported locators. Successful SNR excludes missed decodes, and power normalization depends on reported power; it does not calibrate antennas or receiver chains. The rates describe confirmed active receivers during observed Target activity.""",
            },
            "success_temporal_evidence_rx": {
                "read": """Temporal Evidence shows when successful RX signal strength and Decode Rate change, together with their support. The left panels follow the selected UTC window; the right panels combine matching UTC hours across dates.

<strong class="defined-term">Successful RX SNR Deviation over Time</strong> / <strong class="defined-term">Successful RX SNR Deviation by UTC Hour</strong>. **Successful RX SNR Deviation** compares each transmitter with the median of its own successful Target decodes over the run. **At least three successful observations** are needed for that baseline. **Positive deviations** mean stronger successful reception than that station’s baseline; **negative values** mean weaker reception. The dashed **0 dB** line marks the baseline.

<strong class="defined-term">Median across stations</strong> / <strong class="defined-term">Median across stations and dates</strong>. The white line summarizes **one median per station in each chronological bin**, or **one median per station, date, and hour** in the UTC-hour view. Color shows their **relative concentration** within each panel: lower in blue cells, higher in orange/red cells; **vertical position shows the SNR deviation**. The <strong class="defined-term">IQR</strong>, bounded by Q1 and Q3, spans the **middle 50%** when **at least five values** contribute.

<strong class="defined-term">TX Stations</strong>. Below, the station row divides each transmitter’s vote between <strong class="defined-term">Heard by Target</strong> and <strong class="defined-term">Heard by others only</strong>; its Decode Rate gives stations equal weight.

<strong class="defined-term">Opportunities</strong>. The opportunity row counts every confirmed opportunity and divides successful decodes by all opportunities.

UTC-hour bar heights show **daily average station presences or opportunity counts**; the station-rate line still gives **each distinct station one vote across dates**. With `1h` selected, folded totals average the corresponding chronological hourly totals.

**Read together**

Follow the white line for the typical SNR deviation, then compare both Decode Rate lines and the station and opportunity bar heights before inspecting individual stations where the summaries differ.""",
                "limits": """SNR describes successful decodes only; missing SNR is not zero signal strength. UTC-hour SNR weights station/date/hour values, while the station Decode Rate weights each distinct station once. Folding requires at least two represented dates. Q1–Q3 describes spread, not a confidence interval. Changing station participation and which signals are successfully decoded can change the pattern without establishing propagation, noise, interference, or hardware as its cause.""",
            },
            "success_temporal_evidence_tx": {
                "read": """Temporal Evidence shows when successful TX signal strength and Decode Rate change, together with their support. The left panels follow the selected UTC window; the right panels combine matching UTC hours across dates.

<strong class="defined-term">Successful TX SNR Deviation over Time</strong> / <strong class="defined-term">Successful TX SNR Deviation by UTC Hour</strong>. **Successful TX SNR Deviation** compares each receiver with the median of its own successful Target reports over the run. **At least three successful observations** are needed for that baseline. **Positive deviations** mean stronger successful Target reports than that receiver’s baseline; **negative values** mean weaker reports. The dashed **0 dB** line marks the baseline.

<strong class="defined-term">Median across stations</strong> / <strong class="defined-term">Median across stations and dates</strong>. The white line summarizes **one median per receiver in each chronological bin**, or **one median per receiver, date, and hour** in the UTC-hour view. Color shows their **relative concentration** within each panel: lower in blue cells, higher in orange/red cells; **vertical position shows the SNR deviation**. The <strong class="defined-term">IQR</strong>, bounded by Q1 and Q3, spans the **middle 50%** when **at least five values** contribute.

<strong class="defined-term">RX Stations</strong>. Below, the station row divides each receiver’s vote between <strong class="defined-term">Target heard</strong> and <strong class="defined-term">Other signals heard only</strong>; its Decode Rate gives receivers equal weight.

<strong class="defined-term">Opportunities</strong>. The opportunity row counts every confirmed opportunity and divides successful Target reports by all opportunities.

UTC-hour bar heights show **daily average receiver presences or opportunity counts**; the station-rate line still gives **each distinct receiver one vote across dates**. With `1h` selected, folded totals average the corresponding chronological hourly totals.

**Read together**

Follow the white line for the typical SNR deviation, then compare both Decode Rate lines and the receiver and opportunity bar heights before inspecting individual receivers where the summaries differ.""",
                "limits": """SNR describes successful Target reports only and depends on reported-power normalization; missing SNR is not zero signal strength. UTC-hour SNR weights receiver/date/hour values, while the station Decode Rate weights each distinct receiver once. Folding requires at least two represented dates. Q1–Q3 describes spread, not a confidence interval. Changing receiver participation and which signals are successfully decoded can change the pattern without identifying its physical cause.""",
            },
            "station_insights_compare_joint": {
                "read": """Station Insights shows the remote {peer_type} stations contributing to the active scope. Each row identifies one reported callsign and locator.

<strong class="defined-term">Joint Spots</strong> counts comparisons with usable Target and Reference evidence for that remote station in the **same WSPR cycle**. The **median ΔSNR** summarizes those paired differences: positive favors Target, negative favors Reference, and 0 dB means equality.

**Only Target** and **Only Reference** show retained evidence without a matching observation on the other side.

`Include Unpaired Evidence` also reveals stations without qualifying Joint evidence. Sorting and table filters change displayed rows, not the Segment Inspector summaries.

Compare Joint-Spot counts with the sign and size of each median, then select one row to examine that path over time.""",
                "limits": """A callsign and locator identify an archive identity, not necessarily one unique physical station. A blank median provides no qualifying paired ΔSNR. One-sided counts are conditioned on observed Target activity and are not symmetric wins and losses. Agreement within this run does not establish experimental repeatability in another run.""",
            },
            "station_insights_compare_joint_multi": {
                "read": """Station Insights shows the remote {peer_type} stations contributing to the active scope. Each row identifies one reported callsign and locator.

<strong class="defined-term">Joint Spots</strong> counts comparisons with usable Target and Reference evidence for that remote station in the **same WSPR cycle**. The **median ΔSNR** summarizes those paired differences: positive favors Target, negative favors Reference, and 0 dB means equality.

**Only Target** and **Only Reference** show retained evidence without a matching observation on the other side.

`Include Unpaired Evidence` also reveals stations without qualifying Joint evidence. Sorting and table filters change displayed rows, not the Segment Inspector summaries.

Compare Joint-Spot counts and station medians, then select one path for a detailed check or several paths to inspect their combined evidence.""",
                "limits": """A callsign and locator do not necessarily identify one unique physical station. A blank median provides no qualifying paired ΔSNR. One-sided counts are conditioned on observed Target activity and are not symmetric wins and losses. Selecting several paths combines their observations; it does not give each path equal weight or establish experimental repeatability.""",
            },
            "station_insights_success_rx": {
                "read": """Station Insights shows the remote transmitters contributing to the active RX Performance scope. Each row identifies one reported callsign and locator.

<strong class="defined-term">Heard by Target</strong> counts successful Target decodes; <strong class="defined-term">Heard by others only</strong> counts confirmed transmissions reported elsewhere that the active Target did not decode. <strong class="defined-term">Decode Rate</strong> is Heard by Target divided by the sum of those two counts, expressed as a percentage.

<strong class="defined-term">Median SNR @ 30 dBm</strong> summarizes successful Target decodes after adjustment to a **common 1 W transmit-power basis** using reported power; a less-negative SNR is stronger relative to noise.

`Heard only by other stations.` also reveals transmitters with no successful Target decodes. Sorting, table filters, and row selection do not recalculate the Segment Inspector figures.

Check the counts behind a rate, then select a row to see when that path succeeded or was missed.""",
                "limits": """The rate describes confirmed opportunities, not every transmission that may have occurred. Missed signals have no recorded Target SNR. Power adjustment depends on reported transmit power, and a callsign-plus-locator identity does not prove one unique physical station.""",
            },
            "station_insights_success_tx": {
                "read": """Station Insights shows the remote receivers contributing to the active TX Performance scope. Each row identifies one reported callsign and locator.

<strong class="defined-term">Target heard</strong> counts successful reports of the Target; <strong class="defined-term">Other signals heard</strong> counts opportunities when that receiver reported another qualifying signal but did not report the active Target. <strong class="defined-term">Decode Rate</strong> is Target heard divided by the sum of those two counts, expressed as a percentage.

<strong class="defined-term">Median SNR @ 30 dBm</strong> summarizes successful Target reports after adjustment to a **common 1 W transmit-power basis** using reported power; a less-negative SNR is stronger relative to noise.

`Only other signals heard.` also reveals receivers with no successful Target reports. Sorting, table filters, and row selection do not recalculate the Segment Inspector figures.

Check the counts behind a rate, then select a row to inspect its evidence over time.""",
                "limits": """The rate describes confirmed opportunities, not unconditional coverage at that receiver. A missed Target has no reported SNR. Power adjustment cannot correct an inaccurate reported Target power, and a callsign-plus-locator identity does not prove one unique physical receiver.""",
            },
            "selected_compare_joint": {
                "read": """Selected Station Evidence shows how the Target–Reference difference changes along one selected {peer_type} path.

<strong class="defined-term">Δ SNR over Time</strong> groups Joint Spots into your chosen intervals across the full UTC window; <strong class="defined-term">Δ SNR by UTC Hour</strong> combines observations from the same hour across dates. Chronological intervals begin at the analysis start, and the last may be shorter. Positive ΔSNR favors Target, negative favors Reference, and **0 dB means equality**; these are paired differences, not changes from a station baseline.

The **red dashed line** is the median of all selected Joint Spots. Pale markers show interval medians; the **Q1–Q3 band** spans the middle 50% when **at least five values** contribute. Color shows **relative observation concentration**, not advantage; read the labeled nonlinear dB axis. **Blank intervals** contain no Joint evidence, not a 0 dB difference.

<strong class="defined-term">Selected Path Evidence Coverage</strong> adds Only Target, Joint, and Only Reference. Bars count retained WSPR cycles; <strong class="defined-term">Joint Evidence Share</strong> is Joint divided by all three outcomes. UTC-hour bars show average counts per represented date.

Check whether the ΔSNR sign persists across well-supported intervals, and use coverage to identify periods with little paired evidence.""",
                "limits": """Every Joint Spot has equal weight here; this is not the segment’s station-balanced result. Benchmark retains cycles with observed Target activity, without an equivalent Reference activity gate. Target-offline cycles are excluded, while missing Reference evidence can become Only Target. One-sided counts therefore show conditional availability, not symmetric wins or losses. Joint Evidence Share measures pairability, not Target success. Swapping roles can change coverage; paired differences reverse sign. Joint Spots already contain both sides. Q1–Q3 describes spread, not a confidence interval, and recurring UTC patterns do not establish cause.""",
            },
            "selected_compare_joint_multi": {
                "read": """Selected Station Evidence combines <strong class="defined-term">Joint Spots</strong> from the selected {peer_type} paths.

<strong class="defined-term">Δ SNR over Time</strong> groups them into your chosen chronological intervals; <strong class="defined-term">Δ SNR by UTC Hour</strong> combines observations from the same hour across dates. Every Joint Spot contributes one value, so a path with **more paired observations has more influence**. Positive ΔSNR favors Target, negative favors Reference, and **0 dB means equality**; values are not shifted to a station baseline.

The **red dashed line** is the median of all selected Joint Spots, pale markers show pooled interval medians, and the **Q1–Q3 band** spans the middle 50% when **at least five values** contribute. Color shows relative observation concentration; use the labeled dB axis to judge magnitude. **Blank intervals** have no Joint evidence.

When outlier reporting is enabled, **stars** reuse active-scope candidates for the selected identities; selection does not rerun detection.

Inspect individual paths to check whether one frequently observed path dominates the combined pattern.""",
                "limits": """This view does not weight paths equally or replace the station-balanced segment result. Selected Path Evidence Coverage is available only for one selected path because its denominator is path-specific. Q1–Q3 describes spread, not a confidence interval. Pooled observations, recurring UTC patterns, and candidate markers do not establish independence or physical cause.""",
            },
            "selected_success_rx": {
                "read": """Selected Station Evidence examines one remote transmitter from the active RX Performance scope; selecting another Station Insights row replaces it.

<strong class="defined-term">Selected Station SNR Evidence</strong> shows successful Target SNR normalized to **30 dBm (1 W)**, rather than departures from a station baseline. The chronological panel groups successful decodes into your chosen intervals: color shows their concentration and the line shows the median. The UTC-hour panel combines matching hours across dates, using **one hourly median per represented date**. The **Q1–Q3 band** spans the middle 50% of successful observations chronologically, or date-hour medians in the UTC-hour panel, when **at least five values** contribute.

<strong class="defined-term">Selected Station Temporal Evidence</strong> adds successful and missed opportunities. Its station row divides this transmitter’s one contribution between Heard by Target and Heard by others only; its opportunity row counts every confirmed opportunity. UTC-hour bars show daily average presence or opportunity counts. <strong class="defined-term">Decode Rate</strong> is successful decodes divided by all confirmed opportunities. With one transmitter, Station-balanced and Opportunity-level Decode Rates coincide, so **overlapping lines are expected**.

Read SNR alongside Decode Rate: stronger recorded signals can accompany better reception, but can also reflect fewer weak signals being decoded.""",
                "limits": """Successful SNR excludes missed signals, whose Target SNR is unknown. Normalization depends on reported transmit power and the selected callsign-plus-locator identity. Q1–Q3 describes spread, not a confidence interval. UTC-hour patterns can reveal recurring associations but cannot distinguish propagation, local noise, interference, or equipment changes as their cause.""",
            },
            "selected_success_tx": {
                "read": """Selected Station Evidence examines one remote receiver from the active TX Performance scope; selecting another Station Insights row replaces it.

<strong class="defined-term">Selected Station SNR Evidence</strong> shows the Target SNR reported by this receiver, normalized to **30 dBm (1 W)**, rather than departures from a station baseline. The chronological panel groups successful reports into your chosen intervals: color shows their concentration and the line shows the median. The UTC-hour panel combines matching hours across dates, using **one hourly median per represented date**. The **Q1–Q3 band** spans the middle 50% of successful reports chronologically, or date-hour medians in the UTC-hour panel, when **at least five values** contribute.

<strong class="defined-term">Selected Station Temporal Evidence</strong> adds successful and missed opportunities. Its station row divides this receiver’s one contribution between Target heard and Other signals heard only; its opportunity row counts every confirmed opportunity. UTC-hour bars show daily average presence or opportunity counts. <strong class="defined-term">Decode Rate</strong> is successful Target reports divided by all confirmed opportunities. With one receiver, Station-balanced and Opportunity-level Decode Rates coincide, so **overlapping lines are expected**.

Read SNR alongside Decode Rate: stronger recorded signals can accompany better reception, but can also reflect fewer weak Target signals being decoded.""",
                "limits": """Successful SNR excludes missed Target signals, whose SNR is unknown. Normalization depends on reported Target power. Q1–Q3 describes spread, not a confidence interval. UTC-hour patterns can reveal recurring associations but cannot distinguish propagation, receiver noise, interference, or Target changes as their cause.""",
            },
            "drilldown_compare_joint": {
                "read": """Drill-Down Data connects Benchmark summaries to individual retained WSPR cycles. The table shows exact UTC times, remote station identities, **normalized Target and Reference SNR**, and **paired ΔSNR**. With `Include Unpaired Evidence` enabled, it can also show cycles with only one side present; these have no paired ΔSNR.

When exactly one station is selected, `Zoom window`, `Center date (UTC)`, and `Center time (UTC)` focus the table and additional plots on a centered interval.

The focused ΔSNR plot (<strong class="defined-term">Δ SNR over Time</strong>) shows **one actual value** per retained <strong class="defined-term">Joint Spot</strong> at its cycle time, without time-bin medians, density coloring, an IQR band, a full-run median, or UTC-hour folding. Segment and full-window Selected Station Evidence retain their aggregated views.

`Filter table` narrows **only the displayed rows** and leaves the focused plots and completed analysis unchanged.

Start with a feature in the timeline, inspect its contributing cycles, and check whether several observations support it.""",
                "limits": """These are processed rows after matching and filtering, not untouched provider responses. A missing side has no SNR to reconstruct. Exact timestamps and individual values support traceability but do not establish physical cause; one exceptional row should not be generalized.""",
            },
            "drilldown_success_rx": {
                "read": """Drill-Down Data connects RX Performance summaries to individual confirmed WSPR opportunities. Each opportunity concerns one transmitter identity — its callsign and reported locator — in one WSPR cycle where **Target activity is confirmed**. The table shows UTC time, transmitter identity, and the counted outcomes <strong class="defined-term">Heard by Target</strong> or <strong class="defined-term">Heard by others only</strong>. Every valid Target decode is a success and confirms both endpoints, including decodes recorded only by the Target; this **Target-only** subset is **already included once** in the success count and successful SNR. A miss requires another eligible receiver to report the same transmitter while **Target activity is confirmed in that cycle**.

With one station selected, `Zoom window` and the UTC center controls focus the table and additional plots on a centered interval.

The focused SNR plot (<strong class="defined-term">Successful Target SNR over Time</strong>) shows each successful opportunity’s normalized Target SNR at its cycle time; **missed opportunities have no SNR point**. These are individual values, without temporal medians, IQR bands, density coloring, a full-run median, or UTC-hour folding. The companion outcome plot summarizes the retained opportunities over time.

`Filter table` changes **only displayed rows**, not the focused plots or completed analysis.

Use the outcome counts to reconcile a rate, then inspect when successful and missed opportunities change.""",
                "limits": """These are processed observations after eligibility rules and filters, not untouched archive responses. They cannot reveal unobserved transmissions, the SNR of a missed signal, or why a decode failed. Cycles without evidence of Target activity are excluded; another receiver’s activity alone cannot prove that the Target was listening.""",
            },
            "drilldown_success_tx": {
                "read": """Drill-Down Data connects TX Performance summaries to individual confirmed WSPR opportunities. Each opportunity concerns one receiver identity — its callsign and reported locator — in one WSPR cycle where **Target activity is confirmed**. The table shows UTC time, receiver identity, and the counted outcomes <strong class="defined-term">Target heard</strong> or <strong class="defined-term">Other signals heard</strong>. Every valid report of the Target is a success and confirms both endpoints, including reports without evidence of another signal; this **Target-only** subset is **already included once** in the success count and successful SNR. A miss requires that same receiver to report another qualifying transmitter while **Target activity is confirmed in that cycle**.

With one station selected, `Zoom window` and the UTC center controls focus the table and additional plots on a centered interval.

The focused SNR plot (<strong class="defined-term">Successful Target SNR over Time</strong>) shows each successful opportunity’s normalized Target SNR at its cycle time; **missed opportunities have no SNR point**. These are individual values, without temporal medians, IQR bands, density coloring, a full-run median, or UTC-hour folding. The companion outcome plot summarizes the retained opportunities over time.

`Filter table` changes **only displayed rows**, not the focused plots or completed analysis.

Use the outcome counts to reconcile a rate, then inspect when successful and missed opportunities change.""",
                "limits": """These are processed observations after eligibility rules and filters, not untouched archive responses. They cannot reveal unobserved receiver activity, the SNR of a missed Target, or why a decode failed. Activity at another receiver cannot establish that a silent receiver was listening; insufficient activity evidence remains unknown and excluded.""",
            },
            "drilldown_local_median": {
                "read": """For <strong class="defined-term">Reference Neighborhood</strong>, Drill-Down Data also lists the local Reference callsigns, locators, and SNR values contributing to each cycle’s median. Compare the individual Reference values with the cycle’s Reference median and resulting Target–Reference ΔSNR. Several contributor rows can describe **one comparison cycle**; they are **not additional independent Joint Spots**.

Check whether the contributing stations change when the observed ΔSNR changes.""",
                "limits": """The contributor list explains how the Reference was formed. It cannot establish whether a difference arose from the Target, the neighborhood, or their respective conditions.""",
            },
            "download": {
                "read": """Download Evidence preserves the completed run together with the evidence needed to inspect it later. Choose `Prepare All Results for Download`, then `Download Prepared Results` to save the package. It includes the run configuration and metadata, **processed evidence** retained by the run, and applicable tables and high-resolution figures for the current Inspector scope and selected station or stations. This connects the summaries to their settings and contributing observations.

`Save Config` stores reusable analysis settings **without this run’s evidence**. Before preparing a package, check that the Inspector scope and station selection match the result you want to preserve.""",
                "limits": """The package records WSPRadar’s analysis state, not the physical experiment or untouched provider responses. Retaining it preserves this run’s processed evidence; retrieving the archive again later may produce a different result if source records or WSPRadar change.""",
            },
        },
    },
    "de": {
        "trigger": 'So liest du das',
        "trigger_help": 'So liest du „{section}“',
        "read_label": 'Was diese Ansicht zeigt und wie du sie liest.',
        "limits_label": 'Wichtig zu wissen.',
        "context_layout": """**Von oben nach unten lesen**

<strong class="defined-term">{map_heading} → {segment_heading} → {evidence_heading} → {temporal_heading} → {stations_heading} → {selected_heading} → {drilldown_heading}</strong>

Die <strong class="defined-term">{map_heading}</strong> gibt den geografischen Überblick; im **{segment_heading}** wählst du den geografischen Bereich für die folgenden Abschnitte.

<strong class="defined-term">{evidence_heading}</strong> fasst Stationsergebnisse und die zugrunde liegenden Beobachtungen zusammen; **{temporal_heading}** zeigt, wie sich die Muster und ihre Evidenzbasis im Zeitverlauf verändern.

<strong class="defined-term">{stations_heading}</strong> ermöglicht den Vergleich einzelner Gegenstationen; **{selected_heading}** zeigt deine Auswahl im Zeitverlauf, und **{drilldown_heading}** legt die zugrunde liegenden Beobachtungen offen.

Beginne beim geografischen Überblick, grenze den Bereich ein und vergleiche Stationen und Zeitabschnitte. Wähle eine Station, um ihre Evidenz zu untersuchen und das Muster bis zu einzelnen Beobachtungen nachzuvollziehen.""",
        "sections": {
            "context_rx_success": {
                "read": """<strong class="defined-term">RX-Performance-Ergebnisse</strong> zeigen, wo und wie häufig deine Target-Empfangsstation entfernte Sender innerhalb bestätigter Empfangsgelegenheiten decodiert hat. Untersuche damit die geografische Reichweite, Dekodierrate und erfolgreichen Signalpegel sowie deren Unterschiede zwischen Stationen und im Zeitverlauf.""",
                "limits": """Diese Ergebnisse beschreiben die vollständige Empfangsstation innerhalb der berücksichtigten Gelegenheiten, nicht jedes Signal, das sie möglicherweise erreicht hat. Sie erklären weder die Ursache eines fehlenden Decodes noch liefern sie kalibrierte Messungen der Empfängerempfindlichkeit, des Antennengewinns oder des Antennenwirkungsgrads.""",
            },
            "context_tx_success": {
                "read": """<strong class="defined-term">TX-Performance-Ergebnisse</strong> zeigen, wo und wie häufig entfernte Empfänger deinen Target-Sender innerhalb bestätigter Empfangsgelegenheiten decodiert haben. Untersuche damit die geografische Reichweite, Dekodierrate und erfolgreichen Signalpegel sowie deren Unterschiede zwischen Empfängern und im Zeitverlauf.""",
                "limits": """Diese Ergebnisse beschreiben die vollständige Sendestation innerhalb der berücksichtigten Gelegenheiten, keine unbedingte Abdeckung. Sie messen weder die tatsächlich abgestrahlte Leistung noch den kalibrierten Antennengewinn oder Antennenwirkungsgrad.""",
            },
            "context_rx_compare": {
                "read": """<strong class="defined-term">RX-Benchmark-Ergebnisse</strong> vergleichen deinen Target-Empfangsaufbau mit der gewählten Referenz. Sie zeigen, wo und wann sich die relativen Signalpegel unterscheiden, wie diese Unterschiede zwischen entfernten Sendern variieren und wie viel gepaarte und einseitige Evidenz den Vergleich stützt.""",
                "limits": """ΔSNR liegt nur vor, wenn beide Seiten nutzbare Evidenz geliefert haben. Diese gepaarten Beobachtungen können sich von Signalen unterscheiden, die nur eine Seite decodiert hat. Der Vergleich beschreibt vollständige Empfangspfade; unterschiedliche Standorte, Rauschbedingungen, Hardware und Ausbreitungsbedingungen bleiben relevant. Die Zuordnung eines Unterschieds zu einer einzelnen Komponente erfordert die unabhängige Kontrolle der übrigen Unterschiede.""",
            },
            "context_tx_compare": {
                "read": """<strong class="defined-term">TX-Benchmark-Ergebnisse</strong> vergleichen deinen Target-Sendeaufbau mit der gewählten Referenz. Sie zeigen, wo und wann sich die relativen Signalpegel unterscheiden, wie diese Unterschiede zwischen entfernten Empfängern variieren und wie viel gepaarte und einseitige Evidenz den Vergleich stützt.""",
                "limits": """ΔSNR liegt nur vor, wenn beide Signale decodiert wurden; für ein nicht decodiertes Signal gibt es kein normierbares SNR. Das Ergebnis vergleicht vollständige Sendepfade und stützt sich auf die gemeldete Leistung, die nicht der tatsächlichen Ausgangsleistung oder abgestrahlten Leistung entsprechen muss. Die Zuordnung eines Unterschieds zu einer einzelnen Antenne oder Komponente erfordert die unabhängige Kontrolle der übrigen Unterschiede.""",
            },
            "benchmark_reference": {
                "read": """<strong class="defined-term">Referenzaufbau/-station</strong> verwendet **ein gewähltes Referenzrufzeichen** innerhalb des **vierstelligen Locators**, der aus dem Archivzeitfenster bestimmt wurde. Es kann einen anderen kontrollierten Signalpfad am Target-Standort oder eine Station an einem anderen Ort bezeichnen. In beiden Fällen gelten dieselben Regeln zur Paarbildung innerhalb eines Zyklus.

Ein kontrollierter Vergleich kann Antennen, Speiseleitungen, Funkgeräte oder vollständige Aufbauten untersuchen; ein Vergleich mit einer unabhängigen Station umfasst auch deren andere Installation und Umgebung.

Prüfe, ob der beobachtete Unterschied über entfernte Stationen und Zeit hinweg bestehen bleibt. Ein kalibrierter Vergleich oder ein Tausch der Komponente zwischen den Aufbauten kann helfen zu untersuchen, ob der Unterschied dieser Komponente folgt.""",
                "limits": """Ein gemeinsamer vierstelliger Locator belegt keine Ko-Lokation. Die Referenz ist ein Vergleichsaufbau, nicht automatisch ein kalibrierter Standard. Unterschiede bei Standort, Gelände, Rauschen, Ausrüstung und Betrieb begrenzen, was sich einer einzelnen Komponente zuordnen lässt.""",
            },
            "benchmark_local_median": {
                "read": """<strong class="defined-term">Referenznachbarschaft (Lokaler Median)</strong> vergleicht das Target mit qualifizierenden Beobachtungen von Stationen innerhalb von **{radius} km**: bei RX mit nahe gelegenen Empfängern, bei TX mit nahe gelegenen Sendern.

Für jede entfernte Station und jeden WSPR-Zyklus liefert jede beitragende lokale Identität aus Rufzeichen und Locator **einen SNR-Wert**. Die Referenz ist deren <strong class="defined-term">Median</strong>: der mittlere Wert oder der Mittelwert der beiden mittleren Werte. **Die Beitragenden können sich** von einem Funkweg oder Zyklus zum nächsten ändern.

Lies ΔSNR zusammen mit dem **Joint-Evidenzanteil** und den **Decode Outcomes** und prüfe anschließend im **Drill-Down** die lokalen Beitragenden. Prüfe, ob Änderungen der Target–Referenz-Differenz mit Änderungen der beitragenden Stationen zusammenfallen.""",
                "limits": """Diese Referenz repräsentiert beobachtete Beitragende, nicht jede nahe gelegene Station oder einen festen kalibrierten Standard; ein Zyklus kann nur einen Beitragenden haben. Unterschiede bei Ausrüstung, Standorten, Rauschen, gemeldeter Leistung und Ausbreitung bleiben Teil des Ergebnisses. Ein Nachbarschaftsvergleich kann keinen Antennengewinn isolieren.""",
            },
            "map_compare_rx": {
                "read": """Die Kartenansicht zeigt, wo sich der RX-Benchmark-Unterschied rund um das Target abzeichnet.

Jedes eingefärbte <strong class="defined-term">Kartensegment</strong> für einen Entfernungs- und Richtungsbereich fasst qualifizierende entfernte Senderidentitäten zusammen, unterschieden nach Rufzeichen und gemeldetem Locator. WSPRadar bestimmt zunächst das mediane ΔSNR jeder Station und bildet dann den Median dieser Stationswerte. Diese <strong class="defined-term">stationsgleichgewichtete</strong> Zusammenfassung gibt jeder qualifizierenden Identität **einen Beitrag**, unabhängig von ihrer Spot-Anzahl. **Positive Werte sprechen für das Target**, **negative für die Referenz**.

Marker fassen die berücksichtigte Evidenz zusammen: <strong class="defined-term">Beide (Sync)</strong> erfüllt die Joint-Spot-Anforderung; <strong class="defined-term">Beide (Async)</strong> besitzt qualifizierende einseitige Evidenz auf beiden Seiten, aber **keine qualifizierende Joint-Zusammenfassung**; <strong class="defined-term">Nur …</strong> nennt die Seite, für die allein qualifizierende Evidenz vorliegt.

<strong class="defined-term">STATIONEN</strong> zählt Identitäten, <strong class="defined-term">SPOTS</strong> die berücksichtigten gepaarten und ungepaarten Beobachtungen. Der Async-Anteil von SPOTS kann auch **ungepaarte Beobachtungen von als Joint eingestuften Stationen** enthalten.

Lies die Segmentfarbe zusammen mit der Breite der Stationsbasis und den Beobachtungsanzahlen und untersuche das Muster anschließend im **Segment-Inspektor**.""",
                "limits": """Mindestanforderungen an die Evidenz beeinflussen die Markergruppen; „Async“ beweist nicht, dass keine Paare vorlagen. Ein nicht eingefärbtes Segment besitzt keine qualifizierende Zusammenfassung, keinen gemessenen Unterschied von null. Die symmetrische dB-Skala reicht mindestens von −6 bis +6 dB und kann sich zwischen Läufen erweitern; vergleiche deshalb die Zahlen der Farbskala statt nur die Farben. Das helle Band um null ist ein Darstellungsintervall; nur 0 dB bedeutet Gleichheit. Die Karte belegt weder Ausbreitungsart, Abstrahlwinkel, kalibrierten Gewinn noch physische Ursache.""",
            },
            "map_compare_tx": {
                "read": """Die Kartenansicht zeigt, wo sich der TX-Benchmark-Unterschied rund um das Target abzeichnet.

Jedes eingefärbte <strong class="defined-term">Kartensegment</strong> für einen Entfernungs- und Richtungsbereich fasst qualifizierende entfernte Empfängeridentitäten zusammen, unterschieden nach Rufzeichen und gemeldetem Locator. WSPRadar bestimmt zunächst das mediane ΔSNR jedes Empfängers und bildet dann den Median dieser Stationswerte. Diese <strong class="defined-term">stationsgleichgewichtete</strong> Zusammenfassung gibt jeder qualifizierenden Identität **einen Beitrag**, unabhängig von ihrer Report-Anzahl. **Positive Werte sprechen für das Target**, **negative für die Referenz**.

Marker fassen die berücksichtigte Evidenz zusammen: <strong class="defined-term">Beide (Sync)</strong> erfüllt die Joint-Spot-Anforderung; <strong class="defined-term">Beide (Async)</strong> besitzt qualifizierende einseitige Evidenz auf beiden Seiten, aber **keine qualifizierende Joint-Zusammenfassung**; <strong class="defined-term">Nur …</strong> nennt die Seite, für die allein qualifizierende Evidenz vorliegt.

<strong class="defined-term">STATIONEN</strong> zählt Empfängeridentitäten, <strong class="defined-term">SPOTS</strong> die berücksichtigten gepaarten und ungepaarten Beobachtungen. Der Async-Anteil von SPOTS kann auch **ungepaarte Beobachtungen von als Joint eingestuften Empfängern** enthalten.

Lies die Segmentfarbe zusammen mit der Breite der Empfängerbasis und den Beobachtungsanzahlen und untersuche das Muster anschließend im **Segment-Inspektor**.""",
                "limits": """Mindestanforderungen an die Evidenz beeinflussen die Markergruppen; „Async“ beweist nicht, dass keine Paare vorlagen. Ein nicht eingefärbtes Segment besitzt keine qualifizierende Zusammenfassung, keinen gemessenen Unterschied von null. Die symmetrische dB-Skala reicht mindestens von −6 bis +6 dB und kann sich zwischen Läufen erweitern; vergleiche deshalb die Zahlen der Farbskala statt nur die Farben. Das helle Band um null ist ein Darstellungsintervall; nur 0 dB bedeutet Gleichheit. Für nicht decodierte Signale gibt es kein vergleichbares SNR, und die Karte belegt weder tatsächlich abgestrahlte Leistung noch physische Ursache.""",
            },
            "map_success_rx": {
                "read": """Die Kartenansicht zeigt das geografische Muster der RX-Dekodierrate innerhalb der berücksichtigten Empfangsgelegenheiten.

Für jede qualifizierende entfernte Senderidentität – Rufzeichen und gemeldeter Locator – teilt WSPRadar die erfolgreichen Target-Decodes durch die bestätigten Gelegenheiten dieses Senders. Ein eingefärbtes <strong class="defined-term">Kartensegment</strong> für einen Entfernungs- und Richtungsbereich zeigt das **arithmetische Mittel** dieser einzelnen Prozentwerte: die <strong class="defined-term">stationsgleichgewichtete Dekodierrate</strong>. Jede Identität hat **dasselbe Gewicht**, auch bei unterschiedlicher Gelegenheitsanzahl.

Ein dunkelgrüner Marker bedeutet **mindestens einmal** <strong class="defined-term">Vom Target gehört</strong>; er bedeutet **nicht, dass jede Gelegenheit erfolgreich war**. Ein hellgrauer Marker bedeutet <strong class="defined-term">Nur von anderen gehört</strong>, ohne Target-Decode in den berücksichtigten Gelegenheiten.

<strong class="defined-term">STATIONEN</strong> zählt Senderidentitäten; <strong class="defined-term">GELEGENHEITEN</strong> zählt einzelne Erfolge und verpasste Decodes. Marker und Anzahlen im Fußbereich können qualifizierende Stationen in Segmenten einschließen, deren Stationszahl **für eine Einfärbung nicht ausreicht**.

Vergleiche Farbe, Stationszahl und Gelegenheitsanzahl, bevor du den Bereich im **Segment-Inspektor** eingrenzt.""",
                "limits": """Ein nicht eingefärbtes Segment besitzt keine qualifizierende Zusammenfassung; es belegt keinen vollständig fehlenden Empfang. Die Karte beschreibt bestätigte, berücksichtigte Gelegenheiten, keine unbedingte Abdeckung oder kalibrierte Empfängerempfindlichkeit. Auch 100% gelten nur für diese Gelegenheiten. Die Karte erklärt nicht, warum ein bestimmtes Signal decodiert oder nicht decodiert wurde.""",
            },
            "map_success_tx": {
                "read": """Die Kartenansicht zeigt das geografische Muster der TX-Dekodierrate innerhalb der berücksichtigten Empfangsgelegenheiten.

Für jede qualifizierende entfernte Empfängeridentität – Rufzeichen und gemeldeter Locator – teilt WSPRadar die erfolgreichen Target-Decodes durch die bestätigten Gelegenheiten dieses Empfängers. Ein eingefärbtes <strong class="defined-term">Kartensegment</strong> für einen Entfernungs- und Richtungsbereich zeigt das **arithmetische Mittel** dieser einzelnen Prozentwerte: die <strong class="defined-term">stationsgleichgewichtete Dekodierrate</strong>. Jede Identität hat **dasselbe Gewicht**, auch bei unterschiedlicher Gelegenheitsanzahl.

Ein dunkelgrüner Marker bedeutet **mindestens einmal** <strong class="defined-term">Target gehört</strong>; er bedeutet **nicht, dass jede Gelegenheit erfolgreich war**. Ein hellgrauer Marker bedeutet <strong class="defined-term">Nur andere Signale gehört</strong>, ohne Target-Decode in den berücksichtigten Gelegenheiten.

<strong class="defined-term">STATIONEN</strong> zählt Empfängeridentitäten; <strong class="defined-term">GELEGENHEITEN</strong> zählt einzelne Erfolge und verpasste Decodes. Marker und Anzahlen im Fußbereich können qualifizierende Empfänger in Segmenten einschließen, deren Stationszahl **für eine Einfärbung nicht ausreicht**.

Vergleiche Farbe, Empfängerzahl und Gelegenheitsanzahl, bevor du den Bereich im **Segment-Inspektor** eingrenzt.""",
                "limits": """Ein nicht eingefärbtes Segment besitzt keine qualifizierende Zusammenfassung; es belegt keinen vollständig fehlenden Empfang. Die Karte beschreibt bestätigt aktive Empfänger innerhalb der berücksichtigten Gelegenheiten, keine unbedingte Abdeckung, tatsächlich abgestrahlte Leistung oder kalibrierten Antennenwirkungsgrad. Auch 100% gelten nur für diese Gelegenheiten, und fehlende Decodes belegen nicht ihre Ursache.""",
            },
            "segment": {
                "read": """Der <strong class="defined-term">Segment-Inspektor</strong> untersucht einen nach Entfernung und Richtung ausgewählten Teil des abgeschlossenen Benchmark-Laufs. Die Steuerelemente legen den <strong class="defined-term">aktiven Bereich</strong> fest, den auch Benchmark-Evidenz, Zeitliche Evidenz, Station Insights und die Evidenz der ausgewählten Station darunter verwenden.

**Zusammen betrachten.** Beginne mit dem vollständigen Bereich, grenze ihn auf die für deine Frage relevanten Richtungen oder Entfernungen ein und prüfe, ob das ΔSNR-Muster mehrere Stationen umfasst oder sich auf wenige konzentriert.""",
                "limits": """Ein anderer Bereich filtert den abgeschlossenen Lauf; er lädt keine neuen Beobachtungen und stellt keine durch die ursprünglichen Einstellungen ausgeschlossenen Stationen wieder her. Viele Joint Spots von wenigen Stationen bieten nicht dieselbe geografische Breite wie Beobachtungen vieler Stationen. Keine der beiden Anzahlen belegt Unabhängigkeit, experimentelle Kontrolle oder eine physische Ursache.""",
            },
            "segment_success_rx": {
                "read": """Der <strong class="defined-term">Segment-Inspektor</strong> untersucht RX Performance innerhalb ausgewählter Entfernungen und Richtungen vom Target. Diese Steuerelemente legen den <strong class="defined-term">aktiven Bereich</strong> für die folgenden Abbildungen und Stationstabellen fest.

Die Stationsübersicht zählt qualifizierende TX-Stationen mit mindestens einem Decode durch das Target (<strong class="defined-term">Vom Target gehört</strong>) sowie Stationen, die während der gesamten beibehaltenen Beobachtungen nur von anderen decodiert wurden (<strong class="defined-term">Nur von anderen gehört</strong>). Ihre <strong class="defined-term">Stationsgleichgewichtete Dekodierrate</strong> mittelt die einzelnen TX-Stationsraten mit **gleichem Gewicht je Station**.

Die Gelegenheitsübersicht zählt erfolgreiche Target-Decodes und bestätigte verpasste Decodes; ihre <strong class="defined-term">Dekodierrate auf Gelegenheitsebene</strong> teilt **erfolgreiche Gelegenheiten durch alle bestätigten Gelegenheiten**. Stationen mit vielen Gelegenheiten beeinflussen diese zweite Rate daher stärker.

**Zusammen betrachten.** Lies beide Raten zusammen mit den Stations- und Gelegenheitszahlen und untersuche Unterschiede anschließend in Station Insights.""",
                "limits": """Ähnliche Gesamtraten belegen nicht, dass sich die einzelnen Stationen gleich verhalten. Die Raten beschreiben bestätigte Gelegenheiten bei beobachteter Target-Aktivität, nicht jede mögliche Aussendung. Eine andere Bereichsauswahl kann durch die ursprünglichen Einstellungen ausgeschlossene Evidenz nicht wiederherstellen oder erklären, warum ein Decode ausblieb.""",
            },
            "segment_success_tx": {
                "read": """Der <strong class="defined-term">Segment-Inspektor</strong> untersucht TX Performance innerhalb ausgewählter Entfernungen und Richtungen vom Target. Diese Steuerelemente legen den <strong class="defined-term">aktiven Bereich</strong> für die folgenden Abbildungen und Stationstabellen fest.

Die Stationsübersicht zählt qualifizierende RX-Stationen, die das Target mindestens einmal gehört haben (<strong class="defined-term">Target gehört</strong>), sowie solche, die während der gesamten beibehaltenen Beobachtungen nur andere Signale gehört haben (<strong class="defined-term">Nur andere Signale gehört</strong>). Ihre <strong class="defined-term">Stationsgleichgewichtete Dekodierrate</strong> mittelt die einzelnen Empfängerraten mit **gleichem Gewicht je Empfänger**.

Die Gelegenheitsübersicht zählt erfolgreiche Target-Reports und bestätigte verpasste Gelegenheiten; ihre <strong class="defined-term">Dekodierrate auf Gelegenheitsebene</strong> teilt **erfolgreiche Gelegenheiten durch alle bestätigten Gelegenheiten**. Empfänger mit vielen Gelegenheiten beeinflussen diese zweite Rate daher stärker.

**Zusammen betrachten.** Lies beide Raten zusammen mit den Empfänger- und Gelegenheitszahlen und untersuche Unterschiede anschließend in Station Insights.""",
                "limits": """Ähnliche Gesamtraten belegen nicht, dass sich die einzelnen Empfänger gleich verhalten. Die Raten beschreiben nachweislich aktive Empfänger bei beobachteter Target-Aktivität, nicht bedingungslose Abdeckung. Eine andere Bereichsauswahl kann ausgeschlossene Evidenz nicht wiederherstellen oder Sendeleistung, Antennenwirkungsgrad oder die Ursache eines verpassten Decodes bestimmen.""",
            },
            "comparison_evidence_joint": {
                "read": """Benchmark-Evidenz zeigt, welcher Teil der Evidenz gepaart ist, wie sich Stationen unterscheiden und wie einzelne gepaarte Beobachtungen variieren. Ein <strong class="defined-term">Joint Spot</strong> enthält Target- und Referenz-Evidenz für denselben entfernten Sender in RX oder denselben entfernten Empfänger in TX in einem WSPR-Zyklus. Lies die drei Panels von links nach rechts.

<strong class="defined-term">Decode Outcomes</strong> zeigt **Prozentanteile** (**Anteil (%)**): Schraffierte Balken (**Stationen**) beziehen sich auf die **Gesamtzahl der Stationen**, gefüllte Balken (**Spots**) auf die **Gesamtzahl der Spots**. Auf Stationsebene erfüllt Joint die **Mindestanforderung an gepaarte Evidenz**; Beide (Async) hat qualifizierende einseitige Evidenz auf beiden Seiten, aber **keine qualifizierende Joint-Zusammenfassung**; Nur Target oder Nur Referenz hat qualifizierende Evidenz ausschließlich auf einer Seite. In den Spots-Balken umfasst Beide (Async) **auch qualifizierende ungepaarte Beobachtungen** von Stationen mit Joint-Klassifikation. Gesamt- und Joint-Anzahlen oberhalb der Abbildung zeigen den zugehörigen Evidenzumfang.

<strong class="defined-term">Stationsmediane (Δ SNR)</strong> gibt **jeder qualifizierenden Station einen Median ihrer gepaarten Unterschiede**. Die Balken zeigen den **Prozentanteil der Stationen** im jeweiligen ΔSNR-Bereich; eine enge Verteilung bedeutet, dass ihre medianen Unterschiede ähnlich sind.

<strong class="defined-term">Joint-Spot Δ SNR</strong> gibt **jedem Joint Spot einen Wert**; häufig beobachtete Stationen tragen daher mehr bei. Die Balken zeigen den **Prozentanteil der Joint Spots** im jeweiligen Bereich und damit, wie stark einzelne Vergleiche über Stationen und Zeiten hinweg variieren.

**Zusammen betrachten**

Lies **ΔSNR in dB** an der horizontalen Achse ab: Positive Werte sprechen für das Target, negative für die Referenz, und **0 dB bedeutet Gleichheit**. Beide Verteilungen zeigen Prozentanteile **innerhalb ihrer jeweiligen Population**. Der Median beschreibt den **zentralen Wert**; der Mittelwert ist das **arithmetische Mittel**. Vergleiche Lage und Streuung, um zu beurteilen, ob Stationszusammenfassungen und Einzelbeobachtungen ein ähnliches Muster zeigen, und prüfe anschließend die Stations- und Spot-Anzahlen dahinter.""",
                "limits": """Die ΔSNR-Panels beschreiben ausschließlich qualifizierende gepaarte Evidenz. Die Kategorien hängen von den eingestellten Mindestanforderungen ab; eine Kategorie unterhalb ihrer Schwelle belegt nicht, dass keine entsprechenden Beobachtungen vorlagen. Stations- und Spot-Klassifikationen sind nicht austauschbar. Ähnliche Verteilungszentren können unterschiedliche Funkwege verdecken, und wiederholte Beobachtungen belegen weder Unabhängigkeit noch eine physische Ursache.""",
            },
            "temporal_evidence_joint": {
                "read": """Zeitliche Evidenz zeigt, wann das gepaarte ΔSNR-Muster auftritt und wie viel Evidenz es stützt.

<strong class="defined-term">Δ SNR im Zeitverlauf</strong> zeigt die Zeit von links nach rechts und ΔSNR senkrecht über das ausgewählte UTC-Zeitfenster, wobei Joint Spots in den gewählten Zeitintervallen zusammengefasst werden; die Bins beginnen am ausgewählten Startzeitpunkt, der letzte kann kürzer sein.

<strong class="defined-term">Δ SNR nach UTC-Stunde</strong> führt dieselbe Stunde verschiedener Tage zusammen und macht wiederkehrende Tagesmuster sichtbar.

Positive Werte sprechen für das Target, negative für die Referenz; **0 dB bedeutet Gleichheit**. Die rote gestrichelte Linie ist der **Median aller qualifizierenden Joint Spots im Bereich**; helle Marker zeigen die **Bin-Mediane**. Der <strong class="defined-term">IQR</strong>, begrenzt durch Q1 und Q3, umfasst die **mittleren 50 %** der Werte eines Bins, wenn **mindestens fünf Joint Spots** beitragen. Die Farbe zeigt die **relative Beobachtungsdichte** innerhalb jedes Panels: Blaue Felder enthalten eine geringere Dichte an Joint Spots, orange und rote eine höhere; lies ΔSNR an der beschrifteten, **nichtlinearen dB-Achse** ab.

Leere Intervalle enthalten **keine Joint-Evidenz** und bedeuten kein Ergebnis von 0 dB. Die UTC-Stundenansicht erfordert Evidenz aus **mindestens zwei Tagen**.

**Zusammen betrachten**

Verfolge die Bin-Mediane, um Änderungen des typischen Target–Referenz-Unterschieds zu erkennen, und prüfe für diese Zeiten die Breite über Stationen, den Beobachtungsumfang und den Joint-Anteil in der **Zeitlichen Benchmark-Evidenzabdeckung**.""",
                "limits": """Q1–Q3 beschreibt die Streuung, kein Konfidenzintervall. Wiederkehrende UTC-Muster belegen keine Ursache.""",
            },
            "temporal_evidence_coverage_joint": {
                "read": """Die <strong class="defined-term">zeitliche Benchmark-Evidenzabdeckung</strong> zeigt, wie viel Vergleichsevidenz das gepaarte ΔSNR-Muster stützt, einschließlich der Evidenz Nur Target und Nur Referenz.

<strong class="defined-term">Stationsgleichgewichteter Joint-Evidenzanteil</strong>. In der chronologischen Ansicht erhält in den oberen Balken **jede Station eine Stimme**, aufgeteilt auf ihre Outcomes; die Gesamthöhe zählt daher Stationen, während die blaue Linie **die Joint-Anteile der Stationen mittelt**.

<strong class="defined-term">Joint-Evidenzanteil auf Outcome-Ebene</strong>. Die unteren Balken zählen <strong class="defined-term">Vergleichseinheiten</strong> (jeweils eine Gegenstation in einem WSPR-Zyklus), aufgeteilt in Nur Target, Joint und Nur Referenz; die bernsteinfarbene Linie zeigt **Joint-Einheiten geteilt durch alle beibehaltenen Einheiten**.

Die UTC-Stundenbalken zeigen die **durchschnittliche tägliche Beteiligung beziehungsweise durchschnittliche Anzahlen**, während die blaue Linie weiterhin **jede unterschiedliche Station mit einer Ratenstimme** gewichtet. Jede UTC-Stundenansicht erfordert Evidenz aus **mindestens zwei Tagen**.

**Zusammen betrachten.** Prüfe das ΔSNR-Muster zusammen mit der Breite über Stationen, dem Beobachtungsumfang und dem Joint-Anteil.""",
                "limits": """Benchmark behält Zyklen mit beobachteter Target-Aktivität bei: In RX hat das Target ein qualifizierendes Signal decodiert; in TX wurde es irgendwo decodiert. Für die Referenz gibt es kein entsprechendes Gate. Einseitige Outcomes beschreiben daher bedingte Evidenzverfügbarkeit, keine symmetrischen Siege oder Niederlagen; Joint Spots enthalten bereits beide Seiten. Der Joint-Anteil misst die Paarbarkeit, nicht den Target-Erfolg. Ähnliche zusammengefasste Anteile belegen keine Übereinstimmung zwischen Stationen, und wiederkehrende UTC-Muster belegen keine Ursache.""",
            },
            "outlier_report": {
                "read": """Der Ausreißerbericht hebt ungewöhnliche Änderungen des gepaarten ΔSNR zur genaueren Prüfung hervor. Ein <strong class="defined-term">Funkweg</strong> ist eine entfernte Rufzeichen-Locator-Identität; ein <strong class="defined-term">Joint Spot</strong> ist deren gepaarte Target–Referenz-Beobachtung aus einem WSPR-Zyklus. WSPRadar bestimmt eine lokale Baseline aus gestützter Evidenz vor und nach einem Kandidaten; der Kandidat selbst bleibt dabei ausgeschlossen. Ein <strong class="defined-term">Residuum</strong> ist das beobachtete ΔSNR abzüglich dieser Baseline.

Lies <strong class="defined-term">Erwartetes lokales ΔSNR</strong> als Baseline, <strong class="defined-term">Beobachteter ΔSNR-Median</strong> als zentralen gepaarten Wert des Kandidaten und <strong class="defined-term">Größte Einzelzyklusabweichung</strong> als dessen betragsmäßig größte Abweichung von der Baseline mit ihrem Vorzeichen.

<strong class="defined-term">Spot-Impuls</strong>, <strong class="defined-term">Kurzer Ausbruch</strong> und <strong class="defined-term">Anhaltende Auslenkung</strong> beschreiben die Zeitspanne gruppierter Beobachtungen. Für alle gelten dieselben konfigurierten Anforderungen an die **Medianabweichung**, den **robusten z-Wert** — eine Abweichung im Verhältnis zur lokalen Streuung — und die **Stabilität der Baselines davor und danach**. Berichtete Intervalle beginnen und enden bei Beobachtungen, die beide Abweichungsanforderungen auf Einzelpunktebene erfüllen; schwächere Beobachtungen können zwischen diesen Endpunkten erhalten bleiben.

Jeder Funkwegblock nennt Station, Richtung, UTC-Intervall, **Beobachtungszahl** und **zeitliche Lücken**. Bei einer einzelnen Beobachtung gibt es keinen zeitlichen Abstand und keine Lücke anzugeben.

`↓ In Station Insights anzeigen` wählt diesen Funkweg aus und bereitet seinen Ausreißerfokus vor; `↓ Drill-Down-Details anzeigen` öffnet die zugehörige Detailansicht. Karten mit mehreren Funkwegen bieten zusätzlich `Alle qualifizierenden Funkwege in Station Insights anzeigen`.

Soweit verfügbar, listet <strong class="defined-term">Chronologische WSPR-Zyklusevidenz</strong> die gepaarten Beobachtungen, Baseline, ΔSNR und Residuum in zeitlicher Reihenfolge.

**Zusammen betrachten.** Vergleiche zuerst erwartetes und beobachtetes ΔSNR und prüfe anschließend Beobachtungszahl, Lücken und Einzelevidenz.""",
                "limits": """Kandidaten sind Hinweise zur Prüfung, keine nachgewiesenen physischen Ereignisse oder identifizierten Mechanismen. Spärliche Evidenz oder unzureichende Unterstützung vor und nach einem Kandidaten kann Beobachtungen unbewertet lassen; damit sind sie nicht als normal eingestuft. Zeitspannen und Lücken beschreiben aufgelistete Beobachtungen, keine Sendepläne oder die Dauer eines unbeobachteten Ereignisses. Mehrere Funkwege belegen weder Unabhängigkeit noch eine gemeinsame Ursache. ΔSNR allein kann nicht bestimmen, ob sich Target, Referenz oder beide verändert haben. Der Bericht verwendet verarbeitete Joint Spots, keine unveränderten Anbieterzeilen.""",
            },
            "outlier_focus": {
                "read": """Der <strong class="defined-term">Ausreißerfokus</strong> zeigt einen berichteten Kandidaten zusammen mit den stützenden Beobachtungen davor und danach.

Die ΔSNR-Punkte sind **einzelne erhaltene Joint Spots** zu ihren **tatsächlichen Zykluszeiten**.

Das schattierte Band <strong class="defined-term">Fokussierte Episode</strong> kennzeichnet den ausgewählten Kandidaten.

<strong class="defined-term">Erwartetes lokales ΔSNR</strong> ist dessen geschätzte Baseline; die Baseline-Linien davor und danach zeigen das umgebende Niveau, anhand dessen die Stabilität beurteilt wird.

**Symmetrische Hilfslinien** für den robusten z-Wert bei 1, 2, 3 und der konfigurierten Schwelle zeigen die Abweichung im Verhältnis zur lokalen Streuung. Die **Hilfslinien der absoluten Abweichung** zeigen den erforderlichen Unterschied in dB.

**Sterne** kennzeichnen Beobachtungen, die zu berichteten Kandidaten gehören und **einzeln beide Abweichungsanforderungen erfüllen**. Die angezeigten Hilfslinien gehören zur fokussierten Episode; ein anderer markierter Kandidat kann anhand einer anderen Baseline und Streuung beurteilt worden sein.

In der zeitlichen Zusammenfassung aller Funkwege steht ein Stern für die stärkste einzeln qualifizierende Beobachtung jedes berichteten Ereignisses; diese kann von der Berichtsgröße **Größte Einzelzyklusabweichung** abweichen.

**Zusammen betrachten.** Vergleiche die Kandidatenpunkte mit den Beobachtungen davor und danach und prüfe anschließend die Beobachtungszahlen und zeitlichen Lücken im Bericht.""",
                "limits": """Diese Hilfslinien sind Detektorkriterien, keine Konfidenzintervalle. Das Überschreiten einer einzelnen Linie erfüllt noch nicht alle Anforderungen an Unterstützung, Baseline-Stabilität, gruppierte Abweichung, robusten z-Wert und Vorzeichenübereinstimmung. Das schattierte Band enthält einen kleinen Anzeigerand und wird auf das ausgewählte Fenster begrenzt; es misst nicht die Dauer eines physischen Ereignisses. Eine markierte Abweichung bestimmt nicht deren Ursache.""",
            },
            "success_evidence_rx": {
                "read": """Performance-Evidenz zeigt, wie RX-Ergebnisse mit der Entfernung über qualifizierende TX-Stationen im aktiven Bereich variieren. Lies die drei Panels von links nach rechts.

<strong class="defined-term">Vom Target mindestens einmal gehörte TX-Stationen nach Entfernung</strong> zeigt den Anteil qualifizierender Sender in jedem Entfernungs-Bin, die das Target **mindestens einmal** decodiert hat.

<strong class="defined-term">RX Dekodierrate nach Entfernung der TX-Station</strong> vergleicht **gleich gewichtete** einzelne Stationsraten mit einer Rate aus **allen erfolgreichen und verpassten Gelegenheiten zusammen**; häufig beobachtete Stationen beeinflussen die zweite Rate stärker. Die beiden Linien heißen entsprechend **Stationsgleichgewichtete Dekodierrate** und **Dekodierrate auf Gelegenheitsebene**.

<strong class="defined-term">Erfolgreiches Target-SNR nach Entfernung der TX-Station</strong> berechnet zunächst den Median des erfolgreichen SNR jedes Senders und zeigt dann den Median dieser Stationswerte je Entfernungs-Bin. Das SNR wird **anhand der gemeldeten Leistung** auf eine gemeinsame Sendeleistungsbasis von **30 dBm (1 W)** normiert. Bei **zwei beitragenden Stationen** umfasst Min-Max deren beide Mediane; bei **drei oder mehr** umfasst der <strong class="defined-term">IQR</strong> die **mittleren 50 %** der Stationsmediane.

**Zusammen betrachten.** Lies die Panels als mindestens einmaligen Empfang, Dekodierrate und Signalstärke bei erfolgreichem Decode. Prüfe vor dem Vergleich der Entfernungs-Bins die zugehörigen Stations- und Gelegenheitszahlen.""",
                "limits": """Mindestens einmaliger Empfang hängt von der Länge des Zeitfensters und der verfügbaren Aktivität ab. Die Entfernung wird aus gemeldeten Locatoren berechnet. Erfolgreiches SNR schließt verpasste Decodes aus, und die Leistungsnormierung hängt von der gemeldeten Leistung ab; sie kalibriert weder Antennen noch Empfangsketten. Die Raten beschreiben bestätigte Gelegenheiten bei beobachteter Target-Aktivität.""",
            },
            "success_evidence_tx": {
                "read": """Performance-Evidenz zeigt, wie TX-Ergebnisse mit der Entfernung über qualifizierende RX-Stationen im aktiven Bereich variieren. Lies die drei Panels von links nach rechts.

<strong class="defined-term">RX-Stationen, die das Target mindestens einmal hörten, nach Entfernung</strong> zeigt den Anteil qualifizierender Empfänger in jedem Entfernungs-Bin, die das Target **mindestens einmal** gemeldet haben.

<strong class="defined-term">TX Dekodierrate nach Entfernung der RX-Station</strong> vergleicht **gleich gewichtete** einzelne Empfängerraten mit einer Rate aus **allen erfolgreichen und verpassten Gelegenheiten zusammen**; häufig beobachtete Empfänger beeinflussen die zweite Rate stärker. Die beiden Linien heißen entsprechend **Stationsgleichgewichtete Dekodierrate** und **Dekodierrate auf Gelegenheitsebene**.

<strong class="defined-term">Erfolgreiches Target-SNR nach Entfernung der RX-Station</strong> berechnet zunächst den Median des erfolgreichen Target-SNR jedes Empfängers und zeigt dann den Median dieser Empfängerwerte je Entfernungs-Bin. Das SNR wird **anhand der gemeldeten Leistung** auf eine gemeinsame Sendeleistungsbasis von **30 dBm (1 W)** normiert. Bei **zwei beitragenden Empfängern** umfasst Min-Max deren beide Mediane; bei **drei oder mehr** umfasst der <strong class="defined-term">IQR</strong> die **mittleren 50 %** der Empfängermediane.

**Zusammen betrachten.** Lies die Panels als mindestens einmalige Reichweite, Dekodierrate und Signalstärke bei erfolgreichem Decode. Prüfe vor dem Vergleich der Entfernungs-Bins die zugehörigen Empfänger- und Gelegenheitszahlen.""",
                "limits": """Mindestens einmalige Reichweite hängt von der Länge des Zeitfensters und der verfügbaren Empfängeraktivität ab. Die Entfernung wird aus gemeldeten Locatoren berechnet. Erfolgreiches SNR schließt verpasste Decodes aus, und die Leistungsnormierung hängt von der gemeldeten Leistung ab; sie kalibriert weder Antennen noch Empfangsketten. Die Raten beschreiben nachweislich aktive Empfänger bei beobachteter Target-Aktivität.""",
            },
            "success_temporal_evidence_rx": {
                "read": """Zeitliche Evidenz zeigt, wann sich die Signalstärke erfolgreicher RX-Decodes und die Dekodierrate ändern, zusammen mit ihrer Evidenzbasis. Die linken Panels folgen dem ausgewählten UTC-Zeitfenster; die rechten führen dieselben UTC-Stunden verschiedener Tage zusammen.

<strong class="defined-term">Abweichung des erfolgreichen RX-SNR im Zeitverlauf</strong> / <strong class="defined-term">Abweichung des erfolgreichen RX-SNR nach UTC-Stunde</strong>. **Abweichung des erfolgreichen RX-SNR** vergleicht jeden Sender mit dem Median seiner eigenen erfolgreichen Target-Decodes im Lauf. Diese Baseline erfordert **mindestens drei erfolgreiche Beobachtungen**. **Positive Abweichungen** bedeuten stärkeren erfolgreichen Empfang als die Baseline dieser Station, **negative Werte** schwächeren Empfang. Die gestrichelte **0-dB-Linie** markiert die Baseline.

<strong class="defined-term">Median über Stationen</strong> / <strong class="defined-term">Median über Stationen und Tage</strong>. Die weiße Linie fasst **einen Median je Station in jedem chronologischen Bin** zusammen, beziehungsweise **einen Median je Station, Datum und Stunde** in der UTC-Stundenansicht. Die Farbe zeigt deren **relative Dichte** im Panel: blau geringer, orange/rot höher; die **Höhe zeigt die SNR-Abweichung**. Der <strong class="defined-term">IQR</strong>, begrenzt durch Q1 und Q3, umfasst die **mittleren 50 %**, wenn **mindestens fünf Werte** beitragen.

<strong class="defined-term">TX-Stationen</strong>. Darunter teilt die Stationszeile die Stimme jedes Senders zwischen <strong class="defined-term">Vom Target gehört</strong> und <strong class="defined-term">Nur von anderen gehört</strong> auf; ihre Dekodierrate gewichtet die Stationen gleich.

<strong class="defined-term">Gelegenheiten</strong>. Die Gelegenheitszeile zählt jede bestätigte Gelegenheit und teilt erfolgreiche Decodes durch alle Gelegenheiten.

Die Höhe der UTC-Stundenbalken zeigt **durchschnittliche tägliche Stationspräsenzen beziehungsweise Gelegenheitszahlen**; die Stationsratenlinie gibt **jeder unterschiedlichen Station weiterhin eine Stimme über alle Tage**. Bei gewähltem `1h` sind die zusammengeführten Gesamthöhen Mittelwerte der entsprechenden chronologischen Stundensummen.

**Zusammen betrachten**

Verfolge die weiße Linie für die typische SNR-Abweichung, vergleiche beide Dekodierratenlinien und die Höhe der Stations- und Gelegenheitsbalken und prüfe einzelne Stationen, wenn die Zusammenfassungen abweichen.""",
                "limits": """SNR beschreibt ausschließlich erfolgreiche Decodes; fehlendes SNR bedeutet keine Signalstärke von null. Das UTC-Stunden-SNR gewichtet Werte je Station, Datum und Stunde, die Stationsdekodierrate dagegen jede unterschiedliche Station einmal. Das Zusammenführen erfordert mindestens zwei berücksichtigte Tage. Q1–Q3 beschreibt die Streuung, kein Konfidenzintervall. Änderungen der Stationsbeteiligung und der erfolgreich decodierten Signale können das Muster verändern, ohne Ausbreitung, Rauschen, Störungen oder Hardware als Ursache zu belegen.""",
            },
            "success_temporal_evidence_tx": {
                "read": """Zeitliche Evidenz zeigt, wann sich die Signalstärke erfolgreicher TX-Reports und die Dekodierrate ändern, zusammen mit ihrer Evidenzbasis. Die linken Panels folgen dem ausgewählten UTC-Zeitfenster; die rechten führen dieselben UTC-Stunden verschiedener Tage zusammen.

<strong class="defined-term">Abweichung des erfolgreichen TX-SNR im Zeitverlauf</strong> / <strong class="defined-term">Abweichung des erfolgreichen TX-SNR nach UTC-Stunde</strong>. **Abweichung des erfolgreichen TX-SNR** vergleicht jeden Empfänger mit dem Median seiner eigenen erfolgreichen Target-Reports im Lauf. Diese Baseline erfordert **mindestens drei erfolgreiche Beobachtungen**. **Positive Abweichungen** bedeuten stärkere erfolgreiche Target-Reports als die Baseline dieses Empfängers, **negative Werte** schwächere Reports. Die gestrichelte **0-dB-Linie** markiert die Baseline.

<strong class="defined-term">Median über Stationen</strong> / <strong class="defined-term">Median über Stationen und Tage</strong>. Die weiße Linie fasst **einen Median je Empfänger in jedem chronologischen Bin** zusammen, beziehungsweise **einen Median je Empfänger, Datum und Stunde** in der UTC-Stundenansicht. Die Farbe zeigt deren **relative Dichte** im Panel: blau geringer, orange/rot höher; die **Höhe zeigt die SNR-Abweichung**. Der <strong class="defined-term">IQR</strong>, begrenzt durch Q1 und Q3, umfasst die **mittleren 50 %**, wenn **mindestens fünf Werte** beitragen.

<strong class="defined-term">RX-Stationen</strong>. Darunter teilt die Stationszeile die Stimme jedes Empfängers zwischen <strong class="defined-term">Target gehört</strong> und <strong class="defined-term">Nur andere Signale gehört</strong> auf; ihre Dekodierrate gewichtet die Empfänger gleich.

<strong class="defined-term">Gelegenheiten</strong>. Die Gelegenheitszeile zählt jede bestätigte Gelegenheit und teilt erfolgreiche Target-Reports durch alle Gelegenheiten.

Die Höhe der UTC-Stundenbalken zeigt **durchschnittliche tägliche Empfängerpräsenzen beziehungsweise Gelegenheitszahlen**; die Stationsratenlinie gibt **jedem unterschiedlichen Empfänger weiterhin eine Stimme über alle Tage**. Bei gewähltem `1h` sind die zusammengeführten Gesamthöhen Mittelwerte der entsprechenden chronologischen Stundensummen.

**Zusammen betrachten**

Verfolge die weiße Linie für die typische SNR-Abweichung, vergleiche beide Dekodierratenlinien und die Höhe der Empfänger- und Gelegenheitsbalken und prüfe einzelne Empfänger, wenn die Zusammenfassungen abweichen.""",
                "limits": """SNR beschreibt ausschließlich erfolgreiche Target-Reports und hängt von der Normierung anhand der gemeldeten Leistung ab; fehlendes SNR bedeutet keine Signalstärke von null. Das UTC-Stunden-SNR gewichtet Werte je Empfänger, Datum und Stunde, die Stationsdekodierrate dagegen jeden unterschiedlichen Empfänger einmal. Das Zusammenführen erfordert mindestens zwei berücksichtigte Tage. Q1–Q3 beschreibt die Streuung, kein Konfidenzintervall. Änderungen der Empfängerbeteiligung und der erfolgreich decodierten Signale können das Muster verändern, ohne seine physische Ursache zu bestimmen.""",
            },
            "station_insights_compare_joint": {
                "read": """Station Insights zeigt die entfernten {peer_type}-Stationen, die zum aktiven Bereich beitragen. Jede Zeile bezeichnet eine gemeldete Kombination aus Rufzeichen und Locator.

<strong class="defined-term">Synced Spots</strong> zählt Vergleiche mit verwertbarer Target- und Referenzevidenz für dieselbe Gegenstation im **selben WSPR-Zyklus**. Das **mediane ΔSNR** fasst diese gepaarten Differenzen zusammen: Positive Werte sprechen für das Target, negative für die Referenz; 0 dB bedeutet Gleichheit.

**Only Target** und **Only Reference** zeigen berücksichtigte Evidenz ohne passende Beobachtung auf der jeweils anderen Seite.

`Ungepaarte Evidenz einbeziehen` zeigt auch Stationen ohne qualifizierende Joint-Evidenz. Sortierung und Tabellenfilter verändern die angezeigten Zeilen, nicht die Zusammenfassungen im Segment-Inspektor.

Vergleiche die Anzahl der Joint Spots mit Vorzeichen und Größe jedes Medians und wähle anschließend eine Zeile, um diesen Funkweg im Zeitverlauf zu untersuchen.""",
                "limits": """Rufzeichen und Locator bezeichnen eine Archividentität, nicht zwingend eine einzelne physische Station. Ein leeres Medianfeld liefert kein qualifizierendes gepaartes ΔSNR. Einseitige Anzahlen sind an beobachtete Target-Aktivität gebunden und keine symmetrischen Siege und Niederlagen. Übereinstimmung innerhalb dieses Laufs belegt keine experimentelle Wiederholbarkeit in einem anderen Lauf.""",
            },
            "station_insights_compare_joint_multi": {
                "read": """Station Insights zeigt die entfernten {peer_type}-Stationen, die zum aktiven Bereich beitragen. Jede Zeile bezeichnet eine gemeldete Kombination aus Rufzeichen und Locator.

<strong class="defined-term">Synced Spots</strong> zählt Vergleiche mit verwertbarer Target- und Referenzevidenz für dieselbe Gegenstation im **selben WSPR-Zyklus**. Das **mediane ΔSNR** fasst diese gepaarten Differenzen zusammen: Positive Werte sprechen für das Target, negative für die Referenz; 0 dB bedeutet Gleichheit.

**Only Target** und **Only Reference** zeigen berücksichtigte Evidenz ohne passende Beobachtung auf der jeweils anderen Seite.

`Ungepaarte Evidenz einbeziehen` zeigt auch Stationen ohne qualifizierende Joint-Evidenz. Sortierung und Tabellenfilter verändern die angezeigten Zeilen, nicht die Zusammenfassungen im Segment-Inspektor.

Vergleiche die Anzahl der Joint Spots und die Stationsmediane und wähle anschließend einen Funkweg für eine genauere Prüfung oder mehrere Funkwege für ihre kombinierte Evidenz.""",
                "limits": """Rufzeichen und Locator bezeichnen nicht zwingend eine einzelne physische Station. Ein leeres Medianfeld liefert kein qualifizierendes gepaartes ΔSNR. Einseitige Anzahlen sind an beobachtete Target-Aktivität gebunden und keine symmetrischen Siege und Niederlagen. Die Auswahl mehrerer Funkwege kombiniert deren Beobachtungen; sie gewichtet die Funkwege nicht gleich und belegt keine experimentelle Wiederholbarkeit.""",
            },
            "station_insights_success_rx": {
                "read": """Station Insights zeigt die entfernten Sender, die zum aktiven RX-Performance-Bereich beitragen. Jede Zeile bezeichnet eine gemeldete Kombination aus Rufzeichen und Locator.

<strong class="defined-term">Vom Target gehört</strong> zählt erfolgreiche Target-Decodes; <strong class="defined-term">Nur von anderen gehört</strong> zählt bestätigte Aussendungen, die anderswo gemeldet, vom aktiven Target aber nicht decodiert wurden. Die <strong class="defined-term">Dekodierrate (%)</strong> ist Vom Target gehört geteilt durch die Summe dieser beiden Anzahlen, ausgedrückt in Prozent.

<strong class="defined-term">Median-SNR @ 30 dBm</strong> fasst erfolgreiche Target-Decodes nach Anpassung auf eine **gemeinsame Sendeleistungsbasis von 1 W** anhand der gemeldeten Leistung zusammen; ein weniger negatives SNR bedeutet ein stärkeres Signal relativ zum Rauschen.

`Nur von anderen Stationen gehört.` zeigt auch Sender ohne erfolgreiche Target-Decodes. Sortierung, Tabellenfilter und Zeilenauswahl berechnen die Abbildungen im Segment-Inspektor nicht neu.

Prüfe die Anzahlen hinter einer Rate und wähle anschließend eine Zeile, um zu sehen, wann das Target die Signale dieses Funkwegs decodierte oder verpasste.""",
                "limits": """Die Rate beschreibt bestätigte Gelegenheiten, nicht jede möglicherweise erfolgte Aussendung. Für verpasste Signale gibt es kein aufgezeichnetes Target-SNR. Die Leistungsanpassung hängt von der gemeldeten Sendeleistung ab; eine Rufzeichen-Locator-Identität belegt keine einzelne physische Station.""",
            },
            "station_insights_success_tx": {
                "read": """Station Insights zeigt die entfernten Empfänger, die zum aktiven TX-Performance-Bereich beitragen. Jede Zeile bezeichnet eine gemeldete Kombination aus Rufzeichen und Locator.

<strong class="defined-term">Target gehört</strong> zählt erfolgreiche Target-Reports; <strong class="defined-term">Andere Signale gehört</strong> zählt Gelegenheiten, bei denen dieser Empfänger ein anderes qualifizierendes Signal, aber nicht das aktive Target meldete. Die <strong class="defined-term">Dekodierrate (%)</strong> ist Target gehört geteilt durch die Summe dieser beiden Anzahlen, ausgedrückt in Prozent.

<strong class="defined-term">Median-SNR @ 30 dBm</strong> fasst erfolgreiche Target-Reports nach Anpassung auf eine **gemeinsame Sendeleistungsbasis von 1 W** anhand der gemeldeten Leistung zusammen; ein weniger negatives SNR bedeutet ein stärkeres Signal relativ zum Rauschen.

`Nur andere Signale gehört.` zeigt auch Empfänger ohne erfolgreiche Target-Reports. Sortierung, Tabellenfilter und Zeilenauswahl berechnen die Abbildungen im Segment-Inspektor nicht neu.

Prüfe die Anzahlen hinter einer Rate und wähle anschließend eine Zeile, um ihre Evidenz im Zeitverlauf zu untersuchen.""",
                "limits": """Die Rate beschreibt bestätigte Gelegenheiten, keine uneingeschränkte Abdeckung an diesem Empfänger. Für ein verpasstes Target gibt es kein gemeldetes SNR. Die Leistungsanpassung kann eine ungenau gemeldete Target-Leistung nicht korrigieren; eine Rufzeichen-Locator-Identität belegt keinen einzelnen physischen Empfänger.""",
            },
            "selected_compare_joint": {
                "read": """Die Evidenz der ausgewählten Station zeigt, wie sich die Target–Referenz-Differenz auf einem ausgewählten {peer_type}-Funkweg verändert.

<strong class="defined-term">Δ SNR im Zeitverlauf</strong> gruppiert Joint Spots über das vollständige UTC-Zeitfenster in die gewählten Intervalle; <strong class="defined-term">Δ SNR nach UTC-Stunde</strong> führt Beobachtungen derselben Stunde über mehrere Tage zusammen. Chronologische Intervalle beginnen am Analysestart; das letzte kann kürzer sein. Positive ΔSNR-Werte sprechen für das Target, negative für die Referenz; **0 dB bedeutet Gleichheit**. Es sind gepaarte Differenzen, keine Abweichungen von einer Stationsbasislinie.

Die **rote gestrichelte Linie** ist der Median aller ausgewählten Joint Spots. Helle Marker zeigen Intervallmediane; das **Q1–Q3-Band** umfasst die mittleren 50 %, wenn **mindestens fünf Werte** beitragen. Die Farbe zeigt die **relative Häufung von Beobachtungen**, keinen Vorteil; lies die beschriftete nichtlineare dB-Achse. **Leere Intervalle** enthalten keine Joint-Evidenz und bedeuten keine Differenz von 0 dB.

Die <strong class="defined-term">Evidenzabdeckung des ausgewählten Funkwegs</strong> ergänzt Only Target, Joint und Only Reference. Balken zählen berücksichtigte WSPR-Zyklen; der <strong class="defined-term">Joint-Evidenzanteil</strong> ist Joint geteilt durch die Summe aller drei Outcomes. UTC-Stundenbalken zeigen durchschnittliche Anzahlen je berücksichtigtem Tag.

Prüfe, ob das ΔSNR-Vorzeichen über gut belegte Intervalle hinweg erhalten bleibt, und nutze die Abdeckung, um Zeiträume mit wenig gepaarter Evidenz zu erkennen.""",
                "limits": """Jeder Joint Spot hat hier dasselbe Gewicht; dies ist nicht das stationsgleichgewichtete Segmentergebnis. Benchmark berücksichtigt Zyklen mit beobachteter Target-Aktivität, ohne entsprechende Aktivitätsbedingung für die Referenz. Zyklen ohne Target-Aktivität werden ausgeschlossen; fehlende Referenzevidenz kann dagegen zu Only Target führen. Einseitige Anzahlen zeigen daher bedingte Verfügbarkeit, keine symmetrischen Siege oder Niederlagen. Der Joint-Evidenzanteil misst Paarbarkeit, nicht den Target-Erfolg. Ein Rollentausch kann die Abdeckung verändern; gepaarte Differenzen wechseln das Vorzeichen. Joint Spots enthalten bereits beide Seiten. Q1–Q3 beschreibt Streuung, kein Konfidenzintervall; wiederkehrende UTC-Muster belegen keine Ursache.""",
            },
            "selected_compare_joint_multi": {
                "read": """Die Evidenz der ausgewählten Station kombiniert <strong class="defined-term">Joint Spots</strong> der ausgewählten {peer_type}-Funkwege.

<strong class="defined-term">Δ SNR im Zeitverlauf</strong> gruppiert sie in die gewählten chronologischen Intervalle; <strong class="defined-term">Δ SNR nach UTC-Stunde</strong> führt Beobachtungen derselben Stunde über mehrere Tage zusammen. Jeder Joint Spot liefert einen Wert; ein Funkweg mit **mehr gepaarten Beobachtungen hat daher mehr Einfluss**. Positive ΔSNR-Werte sprechen für das Target, negative für die Referenz; **0 dB bedeutet Gleichheit**. Die Werte werden nicht auf eine Stationsbasislinie verschoben.

Die **rote gestrichelte Linie** ist der Median aller ausgewählten Joint Spots, helle Marker zeigen Mediane der zusammengeführten Intervallwerte, und das **Q1–Q3-Band** umfasst die mittleren 50 %, wenn **mindestens fünf Werte** beitragen. Die Farbe zeigt die relative Häufung von Beobachtungen; nutze die beschriftete dB-Achse, um die Größe der Differenz zu beurteilen. **Leere Intervalle** enthalten keine Joint-Evidenz.

Bei aktivierter Ausreißermeldung zeigen **Sterne** bereits ermittelte Kandidaten des aktiven Bereichs für die ausgewählten Identitäten; die Auswahl startet keine erneute Erkennung.

Untersuche einzelne Funkwege, um zu prüfen, ob ein häufig beobachteter Funkweg das kombinierte Muster dominiert.""",
                "limits": """Diese Ansicht gewichtet Funkwege nicht gleich und ersetzt das stationsgleichgewichtete Segmentergebnis nicht. Die Evidenzabdeckung des ausgewählten Funkwegs ist nur für einen ausgewählten Funkweg verfügbar, weil ihr Nenner funkwegspezifisch ist. Q1–Q3 beschreibt Streuung, kein Konfidenzintervall. Zusammengeführte Beobachtungen, wiederkehrende UTC-Muster und Kandidatenmarker belegen weder Unabhängigkeit noch eine physische Ursache.""",
            },
            "selected_success_rx": {
                "read": """Die Evidenz der ausgewählten Station untersucht einen entfernten Sender aus dem aktiven RX-Performance-Bereich; die Auswahl einer anderen Zeile in Station Insights ersetzt ihn.

Die <strong class="defined-term">SNR-Evidenz der ausgewählten Station</strong> zeigt erfolgreiches Target-SNR, normiert auf **30 dBm (1 W)**, statt Abweichungen von einer Stationsbasislinie. Das chronologische Panel gruppiert erfolgreiche Decodes in die gewählten Intervalle: Die Farbe zeigt ihre Häufung, die Linie den Median. Das UTC-Stundenpanel führt gleiche Stunden über mehrere Tage zusammen und verwendet **einen Stundenmedian je berücksichtigtem Tag**. Das **Q1–Q3-Band** umfasst die mittleren 50 % der erfolgreichen Beobachtungen im Zeitverlauf beziehungsweise der Datum-Stunden-Mediane im UTC-Stundenpanel, wenn **mindestens fünf Werte** beitragen.

Die <strong class="defined-term">Zeitliche Evidenz der ausgewählten Station</strong> ergänzt erfolgreiche und verpasste Gelegenheiten. Ihre Stationszeile teilt den einen Beitrag dieses Senders zwischen Vom Target gehört und Nur von anderen gehört auf; ihre Gelegenheitszeile zählt jede bestätigte Gelegenheit. UTC-Stundenbalken zeigen die mittlere tägliche Präsenz oder Anzahl von Gelegenheiten. Die <strong class="defined-term">Dekodierrate</strong> ist die Zahl erfolgreicher Decodes geteilt durch alle bestätigten Gelegenheiten. Bei einem Sender stimmen Stationsgleichgewichtete Dekodierrate und Dekodierrate auf Gelegenheitsebene überein; **überlagerte Linien sind daher zu erwarten**.

Lies SNR und Dekodierrate zusammen: Stärkere aufgezeichnete Signale können mit besserem Empfang einhergehen, aber auch darauf zurückgehen, dass weniger schwache Signale decodiert werden.""",
                "limits": """Erfolgreiches SNR schließt verpasste Signale aus; deren Target-SNR ist unbekannt. Die Normierung hängt von der gemeldeten Sendeleistung und der ausgewählten Rufzeichen-Locator-Identität ab. Q1–Q3 beschreibt Streuung, kein Konfidenzintervall. UTC-Stundenmuster können wiederkehrende Zusammenhänge sichtbar machen, aber nicht zwischen Ausbreitung, lokalem Rauschen, Störungen oder Geräteänderungen als Ursache unterscheiden.""",
            },
            "selected_success_tx": {
                "read": """Die Evidenz der ausgewählten Station untersucht einen entfernten Empfänger aus dem aktiven TX-Performance-Bereich; die Auswahl einer anderen Zeile in Station Insights ersetzt ihn.

Die <strong class="defined-term">SNR-Evidenz der ausgewählten Station</strong> zeigt das von diesem Empfänger gemeldete Target-SNR, normiert auf **30 dBm (1 W)**, statt Abweichungen von einer Stationsbasislinie. Das chronologische Panel gruppiert erfolgreiche Reports in die gewählten Intervalle: Die Farbe zeigt ihre Häufung, die Linie den Median. Das UTC-Stundenpanel führt gleiche Stunden über mehrere Tage zusammen und verwendet **einen Stundenmedian je berücksichtigtem Tag**. Das **Q1–Q3-Band** umfasst die mittleren 50 % der erfolgreichen Reports im Zeitverlauf beziehungsweise der Datum-Stunden-Mediane im UTC-Stundenpanel, wenn **mindestens fünf Werte** beitragen.

Die <strong class="defined-term">Zeitliche Evidenz der ausgewählten Station</strong> ergänzt erfolgreiche und verpasste Gelegenheiten. Ihre Stationszeile teilt den einen Beitrag dieses Empfängers zwischen Target gehört und Nur andere Signale gehört auf; ihre Gelegenheitszeile zählt jede bestätigte Gelegenheit. UTC-Stundenbalken zeigen die mittlere tägliche Präsenz oder Anzahl von Gelegenheiten. Die <strong class="defined-term">Dekodierrate</strong> ist die Zahl erfolgreicher Target-Reports geteilt durch alle bestätigten Gelegenheiten. Bei einem Empfänger stimmen Stationsgleichgewichtete Dekodierrate und Dekodierrate auf Gelegenheitsebene überein; **überlagerte Linien sind daher zu erwarten**.

Lies SNR und Dekodierrate zusammen: Stärkere aufgezeichnete Signale können mit besserem Empfang einhergehen, aber auch darauf zurückgehen, dass weniger schwache Target-Signale decodiert werden.""",
                "limits": """Erfolgreiches SNR schließt verpasste Target-Signale aus; deren SNR ist unbekannt. Die Normierung hängt von der gemeldeten Target-Leistung ab. Q1–Q3 beschreibt Streuung, kein Konfidenzintervall. UTC-Stundenmuster können wiederkehrende Zusammenhänge sichtbar machen, aber nicht zwischen Ausbreitung, Empfängerrauschen, Störungen oder Target-Änderungen als Ursache unterscheiden.""",
            },
            "drilldown_compare_joint": {
                "read": """Drill-Down-Daten verbinden Benchmark-Zusammenfassungen mit einzelnen berücksichtigten WSPR-Zyklen. Die Tabelle zeigt exakte UTC-Zeiten, Identitäten entfernter Stationen, **normiertes Target- und Referenz-SNR** sowie **gepaartes ΔSNR**. Bei aktiviertem `Ungepaarte Evidenz einbeziehen` kann sie auch Zyklen mit nur einer beobachteten Seite zeigen; für diese gibt es kein gepaartes ΔSNR.

Ist genau eine Station ausgewählt, begrenzen `Zoom-Zeitfenster`, `Datum der Fenstermitte (UTC)` und `Uhrzeit der Fenstermitte (UTC)` die Tabelle und zusätzliche Abbildungen auf ein zentriertes Intervall.

Die fokussierte ΔSNR-Abbildung (<strong class="defined-term">Δ SNR im Zeitverlauf</strong>) zeigt **einen tatsächlichen Wert** je berücksichtigtem <strong class="defined-term">Joint Spot</strong> zu dessen Zykluszeit, ohne Zeit-Bin-Mediane, Dichtefärbung, IQR-Band, Median des vollständigen Laufs oder Zusammenführung nach UTC-Stunde. Segmentansicht und Evidenz der ausgewählten Station über das vollständige Fenster behalten ihre aggregierte Darstellung.

`Tabelle filtern` schränkt **nur die angezeigten Zeilen** ein und lässt die fokussierten Abbildungen sowie die abgeschlossene Analyse unverändert.

Beginne bei einem Merkmal im Zeitverlauf, prüfe die beitragenden Zyklen und achte darauf, ob mehrere Beobachtungen es stützen.""",
                "limits": """Dies sind verarbeitete Zeilen nach Zuordnung und Filterung, keine unveränderten Provider-Antworten. Für eine fehlende Seite lässt sich kein SNR rekonstruieren. Exakte Zeitstempel und Einzelwerte ermöglichen Nachvollziehbarkeit, belegen aber keine physische Ursache; eine Ausnahmezeile sollte nicht verallgemeinert werden.""",
            },
            "drilldown_success_rx": {
                "read": """Drill-Down-Daten verbinden RX-Performance-Zusammenfassungen mit einzelnen bestätigten WSPR-Gelegenheiten. Jede Gelegenheit betrifft eine Senderidentität — Rufzeichen und gemeldeten Locator — in einem WSPR-Zyklus mit **bestätigter Target-Aktivität**. Die Tabelle zeigt UTC-Zeit, Senderidentität und die gezählten Outcomes <strong class="defined-term">Vom Target gehört</strong> oder <strong class="defined-term">Nur von anderen gehört</strong>. Jeder gültige Target-Decode ist ein Erfolg und bestätigt beide Endpunkte, einschließlich ausschließlich vom Target aufgezeichneter Decodes; diese **Target-only**-Teilmenge ist **bereits einmal** in der Erfolgsanzahl und im erfolgreichen SNR enthalten. Eine verpasste Gelegenheit wird nur gezählt, wenn ein anderer geeigneter Empfänger denselben Sender meldet und zugleich **die Target-Aktivität in diesem Zyklus bestätigt ist**.

Bei einer ausgewählten Station begrenzen `Zoom-Zeitfenster` und die UTC-Einstellungen der Fenstermitte die Tabelle und zusätzliche Abbildungen auf ein zentriertes Intervall.

Die fokussierte SNR-Abbildung (<strong class="defined-term">Erfolgreiches Target-SNR im Zeitverlauf</strong>) zeigt das normierte Target-SNR jeder erfolgreichen Gelegenheit zu deren Zykluszeit; **verpasste Gelegenheiten haben keinen SNR-Punkt**. Dies sind Einzelwerte ohne Zeitmediane, IQR-Bänder, Dichtefärbung, Median des vollständigen Laufs oder Zusammenführung nach UTC-Stunde. Die ergänzende Outcome-Abbildung fasst die berücksichtigten Gelegenheiten im Zeitverlauf zusammen.

`Tabelle filtern` verändert **nur angezeigte Zeilen**, nicht die fokussierten Abbildungen oder die abgeschlossene Analyse.

Gleiche anhand der Outcome-Anzahlen eine Rate ab und prüfe anschließend, wann sich erfolgreiche und verpasste Gelegenheiten verändern.""",
                "limits": """Dies sind verarbeitete Beobachtungen nach Eignungsregeln und Filtern, keine unveränderten Archivantworten. Sie können unbeobachtete Aussendungen, das SNR eines verpassten Signals oder den Grund eines fehlgeschlagenen Decodes nicht offenlegen. Zyklen ohne Nachweis der Target-Aktivität werden ausgeschlossen; die Aktivität eines anderen Empfängers allein belegt nicht, dass das Target zugehört hat.""",
            },
            "drilldown_success_tx": {
                "read": """Drill-Down-Daten verbinden TX-Performance-Zusammenfassungen mit einzelnen bestätigten WSPR-Gelegenheiten. Jede Gelegenheit betrifft eine Empfängeridentität — Rufzeichen und gemeldeten Locator — in einem WSPR-Zyklus mit **bestätigter Target-Aktivität**. Die Tabelle zeigt UTC-Zeit, Empfängeridentität und die gezählten Outcomes <strong class="defined-term">Target gehört</strong> oder <strong class="defined-term">Andere Signale gehört</strong>. Jeder gültige Target-Report ist ein Erfolg und bestätigt beide Endpunkte, einschließlich Reports ohne Nachweis eines anderen Signals; diese **Target-only**-Teilmenge ist **bereits einmal** in der Erfolgsanzahl und im erfolgreichen SNR enthalten. Eine verpasste Gelegenheit wird nur gezählt, wenn derselbe Empfänger einen anderen qualifizierenden Sender meldet und zugleich **die Target-Aktivität in diesem Zyklus bestätigt ist**.

Bei einer ausgewählten Station begrenzen `Zoom-Zeitfenster` und die UTC-Einstellungen der Fenstermitte die Tabelle und zusätzliche Abbildungen auf ein zentriertes Intervall.

Die fokussierte SNR-Abbildung (<strong class="defined-term">Erfolgreiches Target-SNR im Zeitverlauf</strong>) zeigt das normierte Target-SNR jeder erfolgreichen Gelegenheit zu deren Zykluszeit; **verpasste Gelegenheiten haben keinen SNR-Punkt**. Dies sind Einzelwerte ohne Zeitmediane, IQR-Bänder, Dichtefärbung, Median des vollständigen Laufs oder Zusammenführung nach UTC-Stunde. Die ergänzende Outcome-Abbildung fasst die berücksichtigten Gelegenheiten im Zeitverlauf zusammen.

`Tabelle filtern` verändert **nur angezeigte Zeilen**, nicht die fokussierten Abbildungen oder die abgeschlossene Analyse.

Gleiche anhand der Outcome-Anzahlen eine Rate ab und prüfe anschließend, wann sich erfolgreiche und verpasste Gelegenheiten verändern.""",
                "limits": """Dies sind verarbeitete Beobachtungen nach Eignungsregeln und Filtern, keine unveränderten Archivantworten. Sie können unbeobachtete Empfängeraktivität, das SNR eines verpassten Targets oder den Grund eines fehlgeschlagenen Decodes nicht offenlegen. Die Aktivität eines anderen Empfängers belegt nicht, dass ein stiller Empfänger zugehört hat; unzureichend belegte Aktivität bleibt unbekannt und ausgeschlossen.""",
            },
            "drilldown_local_median": {
                "read": """Für die <strong class="defined-term">Referenznachbarschaft</strong> listen die Drill-Down-Daten auch lokale Referenzrufzeichen, Locator und SNR-Werte auf, die zum Median jedes Zyklus beitragen. Vergleiche die einzelnen Referenzwerte mit dem Referenzmedian des Zyklus und dem resultierenden Target–Referenz-ΔSNR. Mehrere Beitragszeilen können **einen Vergleichszyklus** beschreiben; sie sind **keine zusätzlichen unabhängigen Joint Spots**.

Prüfe, ob die beitragenden Stationen wechseln, wenn sich das beobachtete ΔSNR verändert.""",
                "limits": """Die Liste der Beitragenden erklärt, wie die Referenz gebildet wurde. Sie kann nicht belegen, ob ein Unterschied vom Target, von der Nachbarschaft oder von deren jeweiligen Bedingungen ausging.""",
            },
            "download": {
                "read": """Evidenz herunterladen bewahrt den abgeschlossenen Lauf zusammen mit der Evidenz, die für eine spätere Prüfung benötigt wird. Wähle `Alle Ergebnisse zum Download vorbereiten` und anschließend `Vorbereitete Ergebnisse herunterladen`, um das Paket zu speichern. Es enthält Konfiguration und Metadaten des Laufs, die vom Lauf beibehaltene **verarbeitete Evidenz** sowie die jeweils verfügbaren Tabellen und hochauflösenden Abbildungen für den aktuellen Inspector-Bereich und die ausgewählte Station oder Stationsgruppe. Dadurch bleiben die Zusammenfassungen mit ihren Einstellungen und beitragenden Beobachtungen verbunden.

`Konfig speichern` speichert wiederverwendbare Analyseeinstellungen **ohne die Evidenz dieses Laufs**. Prüfe vor dem Vorbereiten eines Pakets, ob Inspector-Bereich und Stationsauswahl dem Ergebnis entsprechen, das du bewahren möchtest.""",
                "limits": """Das Paket hält den WSPRadar-Analysestand fest, nicht den physischen Versuch oder unveränderte Provider-Antworten. Wenn du es aufbewahrst, bleibt die verarbeitete Evidenz dieses Laufs erhalten; eine spätere Archivabfrage kann ein anderes Ergebnis liefern, wenn sich Quelldatensätze oder WSPRadar ändern.""",
            },
        },
    },
}

# Guided Input owns question-led presentation text only. Scientific labels that
# are shared with Classic Input remain in ``T`` so both editors name the same
# canonical field consistently.
GUIDED_INPUTS = {
    "en": {
        "mode": {
            "label": "Input view",
            "guided": "Guided",
            "classic": "Classic",
        },
        "steps": {
            "use_case": {
                "title": "What do you want to investigate?",
                "body_md": """**Turn WSPR spots into evidence about your station.** Use these reception reports to explore where, when and how well your receiver or transmitter performs, or compare an antenna, radio or complete signal path with a Reference.

Choose <strong class="defined-term">Performance</strong> to explore your station on its own, or <strong class="defined-term">Benchmark</strong> to compare it with another setup, a known station or nearby stations. For a first look at what WSPRadar can show you, try one of the **prepared demos above**.

The <strong class="defined-term">Target</strong> is your station or signal path under investigation. The <strong class="defined-term">Reference</strong> is the setup or station — or group of stations — you compare it with. <strong class="defined-term">RX</strong> means receiving; <strong class="defined-term">TX</strong> means transmitting.""",
            },
            "target_and_window": {
                "title": "Define the Target and measurement window",
                "body_md": """The <strong class="defined-term">Target</strong> is the station or controlled path being tested. Enter the exact callsign or reporting identity stored in the WSPR database and the Target's <strong class="defined-term">QTH</strong> — its station location. Choose one band and enter absolute UTC start and end values for a period during which the identity, location and tested setup were correct and reasonably stable.""",
            },
            "reference_design": {
                "title": "What should be used as the Reference?",
                "body_md": """The <strong class="defined-term">Reference</strong> is the baseline used to compare your Target.""",
            },
            "offset_calibration": {
                "title": "Is there an established Target–Reference offset?",
                "body_md": """<strong class="defined-term">SNR</strong> is the signal-to-noise ratio reported by the WSPR decoder, in decibels (dB). A higher value means a stronger signal relative to noise.

<strong class="defined-term">ΔSNR</strong> ("delta SNR") is the Target SNR minus the corrected Reference SNR. A positive value favors the Target; a negative value favors the Reference.

An <strong class="defined-term">offset</strong> is a repeatable Target–Reference difference that is already present before the effect you want to study. A Reference-side correction adjusts the Reference SNR before ΔSNR is calculated. Leave the correction at **0.0 dB** unless the offset was established and documented for the same identities or paths, band, hardware and comparison method. The correction shifts every comparison result; it cannot compensate for uncontrolled differences that vary with time, station or radio path.""",
            },
            "scope_and_evidence": {
                "title": "Optional Filters, scope and evidence",
                "body_md": """Choose which remote stations and observations contribute to your results, and how much evidence is required for station and map summaries. Review the displayed settings and change them where your question requires it. These values apply even if you leave this panel unchanged.""",
            },
            "review_and_run": {
                "title": "Review and run",
                "body_md": """Check that this summary matches the station setup and operating period you actually want to analyze. It defines the Target, Reference, band, UTC window, scope and evidence rules used by the run. Guided and Classic Input edit the same scientific configuration; changing the input view does not change the analysis.""",
            },
        },
        "options": {
            "use_cases": {
                "rx_performance": {
                    "label": "RX Performance",
                    "description": """Explore how well your receiver hears WSPR signals. See reception patterns by direction, distance and time, including how often signals are decoded within confirmed reception opportunities. No Reference needed.""",
                },
                "tx_performance": {
                    "label": "TX Performance",
                    "description": """Explore how well other stations hear your WSPR transmissions. See reception patterns by direction, distance and time, including how often your signal is decoded within confirmed reception opportunities. No Reference needed.""",
                },
                "rx_benchmark": {
                    "label": "RX Benchmark",
                    "description": """Compare your receiver or receive path with another setup, a known station or nearby stations. Use observations from the same WSPR cycles to explore differences in reception by direction, distance and time.""",
                },
                "tx_benchmark": {
                    "label": "TX Benchmark",
                    "description": """Compare your transmitter, transmit path or complete station with another setup, a known station or nearby stations. Use observations from the same WSPR cycles to explore differences in reception by direction, distance and time.""",
                },
            },
            "reference_design": {
                "reference_station": {
                    "label": "Reference Setup/Station",
                    "description": """Compare with another controlled signal path at your station or one known station at the same or another location. A controlled setup helps you investigate equipment differences; an independent station provides a comparison of complete stations and their operating conditions.""",
                },
                "local_neighborhood": {
                    "label": "Reference Neighborhood",
                    "description": """Compare with the local median of qualifying nearby stations within your chosen radius. This provides a local comparison when you do not have a suitable individual Reference. The contributing stations can vary across signal paths and time.""",
                },
            },
            "local_benchmark": {
                "local_median": {
                    "label": """Local Median Neighborhood""",
                    "description": """Compares the Target with the median of qualifying nearby station contributions for each remote station and WSPR cycle. Contributors can change between paths and cycles. The result describes complete-station performance relative to those observed peers.""",
                },
            },
            "offset_intent": {
                "no_offset": {
                    "label": "No established offset — use 0.0 dB",
                    "description": """Apply no Reference-side correction. Use this for a first exploratory run or whenever no defensible baseline exists and you are not establishing one in this run. Any stable Target–Reference bias remains part of the reported ΔSNR.""",
                },
                "established_offset": {
                    "label": "Use an established correction",
                    "description": """Apply a documented signed correction established for the same paths or identities, band, hardware and comparison method. Enter its value below after selecting this option. The formula above explains how the sign changes the corrected ΔSNR.""",
                },
                "establish_offset": {
                    "label": "Set up an offset-establishment run",
                    "description": """Run Benchmark with a 0.0 dB correction to characterize the existing Target–Reference baseline. WSPRadar displays the paired evidence but does not choose a correction automatically. Review and document the result, then enter a defensible signed value in a later run.""",
                },
            },
        },
        "summaries": {
            "window_utc": "{start}–{end} UTC",
            "window_incomplete": "UTC interval incomplete",
            "use_case": "{step} · Question — {choice} ✓",
            "target_and_window": "{step} · Target — {callsign} · {qth} · {band} · {window} ✓",
            "reference_station": "{step} · Reference — {callsign} · {qth} ✓",
            "reference_local_median": "{step} · Reference — local median within {radius} km ✓",
            "offset_none": "{step} · Reference correction — 0.0 dB ✓",
            "offset_established": "{step} · Reference correction — {offset:+.1f} dB ✓",
            "offset_establish": "{step} · Baseline run — 0.0 dB correction ✓",
            "scope": "{step} · Optional Filters, scope and evidence — max {distance} km · {solar} ✓",
            "review_ready": "{step} · Review — ready to run ✓",
        },
        "messages": {
            "use_case_limits": """Results reflect the complete stations and conditions observed. They do not, by themselves, measure absolute receiver sensitivity, radiated power, antenna gain or antenna efficiency.""",
            "demo_title": "Guided demo",
            "demo_preset": """This demo loads a complete preset for a documented example. For a first run, keep the preset unchanged and use it to learn how the question, identities and analysis settings lead to the displayed result. The demo describes the listed stations and historical period; it is not evidence about your own station.""",
            "demo_walkthrough": "Walk me through the setup",
            "demo_walkthrough_help": "Review each preset choice and what it changes in the analysis.",
            "demo_skip_to_review": "Skip to review and run",
            "demo_skip_to_review_help": "Open the complete configuration summary and start the analysis immediately with the current settings.",
            "local_existing_correction_warning": """This configuration already contains a {offset:+.1f} dB correction for the local Reference. The standard Guided neighborhood path leaves that advanced value unchanged, so it would still affect every ΔSNR. Open Classic setup to review or reset it before running.""",
            "correction_formula": """**Corrected ΔSNR = Target SNR − (Reference SNR + correction)**\x20\x20\nA positive ΔSNR favors the Target; a negative value favors the Reference.""",
            "correction_consequence": """{offset:+.1f} dB will be added to every Reference SNR before subtraction. A positive correction lowers the corrected ΔSNR; a negative correction raises it.""",
            "establish_reference_guidance": """Station level gives each station one vote and is usually the better default for WSPRadar's station-balanced result. Spot level gives each observation one vote, so high-volume stations can dominate. The median is more robust to outliers and skew; the mean can be appropriate for a roughly symmetric distribution without influential extremes, but is more sensitive to them. Choose from the intended weighting and evidence distribution — not the preferred answer. If the estimates differ materially, investigate rather than cherry-picking; one constant offset may not be defensible. Check stability across stations, signal level and time, then repeat the baseline under the same operating design and verify that the corrected ΔSNR is plausibly centered near `0 dB`. For a controlled common-input baseline, repeat or swap paths and verify that the corrected common-input ΔSNR is plausibly centered near `0 dB`.""",
            "calibration_run_notice": """Offset-establishment run: the Reference correction is fixed at 0.0 dB. Run the normal Benchmark analysis to measure the uncorrected Target − Reference baseline. WSPRadar shows the available summaries but does not select or apply an offset.

After the run, choose and document one ΔSNR estimate: the median or arithmetic mean from **Station Medians**, or from **Joint Spots**. Enter the observed Target − Reference value with the same sign as the Reference correction in the next run — for example, enter `+1.6 dB` for a `+1.6 dB` baseline.""",
            "station_population_title": "Remote station filters",
            "station_population_body": """<strong class="defined-term">Remote stations</strong> are the transmitters your Target listens for in RX analyses, or the receivers that listen for your Target in TX analyses. These filters let you restrict which of those stations contribute to the analysis.

The special-callsign filter excludes remote callsigns beginning with Q, 0 or 1, typically used for balloon telemetry. Target and Reference stations, including Reference Neighborhood reference contributors, remain eligible under this filter.

The moving-station filter excludes remote callsigns reported from more than one four-character grid locator square in the eligible observations.

Use these filters when those exclusions match your investigation. They can improve consistency, but can also remove valid evidence; choose them from your question, rather than to obtain a preferred result.""",
            "analysis_scope_title": "Analysis scope",
            "analysis_scope_body": """Use Solar state to examine observations made during daylight, nighttime or greyline conditions at the Target’s location. This describes the Sun’s position at the Target, not along the entire radio path.

Maximum peer distance limits how far from the Target contributing remote stations may be. It changes the evidence included in the analysis, map, Inspector and exports.""",
            "evidence_requirements_title": "Evidence requirements",
            "compare_evidence_requirements_body": """Evidence requirements set a minimum amount of support for your results: enough observations for each station, and enough qualifying stations within each <strong class="defined-term">map segment</strong> — a geographic area defined by direction and distance.

A station qualifies for the ΔSNR map when it provides the required number of <strong class="defined-term">Joint Spots</strong>: comparisons of Target and Reference observations from the same WSPR cycle through the same remote station. Each qualifying station contributes one median ΔSNR and counts once toward the map segment’s station minimum. Observations involving only the Target or only the Reference do not satisfy that paired-evidence requirement.

A station is one exact callsign + full reported locator identity; the same callsign at different locators counts separately. These are reported identities, not a count of independent physical stations.

Higher minimums require more supporting evidence but reduce station and geographic coverage. They do not remove propagation effects or guarantee measurement quality.""",
            "success_evidence_requirements_body": """Evidence requirements set a minimum amount of support for your results: enough observations for each station, and enough qualifying stations within each <strong class="defined-term">map segment</strong> — a geographic area defined by direction and distance.

A station qualifies when it provides the required number of <strong class="defined-term">confirmed reception opportunities</strong>. These include successful Target decodes and opportunities where other reports establish the relevant activity but the Target decode is absent. They are not simply a count of successful decodes. A map segment must also contain the selected number of qualifying stations.

Higher minimums require more supporting evidence but reduce station and geographic coverage. They do not remove propagation effects or guarantee measurement quality.""",
            "included": "excluded",
            "not_included": "included",
            "compare_evidence": """joint evidence ≥ {value} per station; qualifying stations ≥ {stations} per map segment""",

            "success_evidence": """confirmed opportunities ≥ {value} per station; qualifying stations ≥ {stations} per map segment""",
            "review_question": "Question",
            "review_target": "Target",
            "review_target_value": "{callsign} at {qth}",
            "review_reference": "Reference",
            "review_band_window": "Band and UTC window",
            "review_correction": "Reference-side correction",
            "review_population": "Remote station filters",
            "review_population_value": """remote peer callsigns beginning with Q, 0, or 1 {special}; stations changing locator {moving}""",
            "review_scope": "Solar and geographic scope",
            "review_evidence": "Evidence requirements",
            "review_result": "Result type",
            "result_performance": "Performance only — stand-alone Target values",
            "result_benchmark": "Benchmark — Target-versus-Reference values",
            "open_classic": "Open Classic setup",
            "continue": "Continue",
            "configuration_changed": """Inputs changed since the last run. Run the analysis again before interpreting the results.""",
            "reference_location_pending_short": "location pending",
        },
        "validation": {
            "use_case": "Choose one operating question before continuing.",
            "target_and_window": "Enter a valid Target identity and QTH, select a band, and complete the UTC measurement window before continuing.",
            "reference_design": "Complete the selected Reference design: enter the Reference callsign or set the Reference Neighborhood radius. The fixed Reference location is resolved automatically.",
            "offset_calibration": "Choose whether to use no correction, enter an established correction below, or set up an offset-establishment run.",
            "scope_and_evidence": "Review the active filters, analysis scope and evidence requirements and correct any invalid value before continuing.",
            "review_and_run": "Complete the required question, Target, measurement window, Reference design when applicable, and the visible scope and evidence fields before running.",
            "flow_invalid": "Guided Input is unavailable because its workflow configuration is invalid: {error}",
        },
    },
    "de": {
        "mode": {
            "label": "Eingabeansicht",
            "guided": "Geführt",
            "classic": "Klassisch",
        },
        "steps": {
            "use_case": {
                "title": "Was möchtest du untersuchen?",
                "body_md": """**WSPR-Spots liefern Evidenz über deine Station.** Nutze diese Empfangsmeldungen, um zu untersuchen, wo, wann und wie gut dein Empfänger oder Sender arbeitet, oder um eine Antenne, ein Funkgerät oder einen vollständigen Signalpfad mit einer Referenz zu vergleichen.

Wähle <strong class="defined-term">Performance</strong>, um deine Station für sich zu untersuchen, oder <strong class="defined-term">Benchmark</strong>, um sie mit einem anderen Aufbau, einer bekannten Station oder benachbarten Stationen zu vergleichen. Für einen ersten Eindruck davon, was WSPRadar dir zeigen kann, probiere eine der **vorbereiteten Demos weiter oben** aus.

Deine Station oder dein Signalpfad ist das <strong class="defined-term">Target</strong> deiner Untersuchung. Als <strong class="defined-term">Referenz</strong> dient für den Vergleich mit dem Target ein Aufbau, eine Station oder eine Gruppe von Stationen. <strong class="defined-term">RX</strong> bedeutet Empfang; <strong class="defined-term">TX</strong> bedeutet Senden.""",
            },
            "target_and_window": {
                "title": "Target und Messzeitraum festlegen",
                "body_md": """Das <strong class="defined-term">Target</strong> ist die getestete Station oder der getestete kontrollierte Pfad. Gib das exakte in der WSPR-Datenbank gespeicherte Rufzeichen oder die dort gespeicherte Meldekennung und das <strong class="defined-term">QTH</strong> des Targets ein — also seinen Stationsstandort. Wähle ein Band und gib absolute UTC-Start- und Endwerte für einen Zeitraum ein, in dem Kennung, Standort und getesteter Aufbau korrekt und möglichst stabil waren.""",
            },
            "reference_design": {
                "title": "Was soll als Referenz dienen?",
                "body_md": """Die <strong class="defined-term">Referenz</strong> ist die Vergleichsbasis für dein Target.""",
            },
            "offset_calibration": {
                "title": "Gibt es einen ermittelten Target–Referenz-Offset?",
                "body_md": """<strong class="defined-term">SNR</strong> ist das vom WSPR-Decoder gemeldete Signal-Rausch-Verhältnis in Dezibel (dB). Ein höherer Wert bedeutet ein stärkeres Signal im Verhältnis zum Rauschen.

<strong class="defined-term">ΔSNR</strong> ("Delta-SNR") ist Target-SNR minus korrigiertes Referenz-SNR. Ein positiver Wert spricht für das Target, ein negativer Wert für die Referenz.

Ein <strong class="defined-term">Offset</strong> ist eine wiederholbare Target–Referenz-Differenz, die bereits vorhanden ist, bevor der eigentliche untersuchte Effekt hinzukommt. Eine referenzseitige Korrektur verändert das Referenz-SNR, bevor ΔSNR berechnet wird. Belasse die Korrektur bei **0,0 dB**, sofern der Offset nicht für dieselben Kennungen oder Pfade, dasselbe Band, dieselbe Hardware und dieselbe Vergleichsmethode ermittelt und dokumentiert wurde. Die Korrektur verschiebt jedes Vergleichsergebnis; sie kann keine unkontrollierten Unterschiede ausgleichen, die sich mit Zeit, Station oder Funkweg ändern.""",
            },
            "scope_and_evidence": {
                "title": "Optionale Filter, Analyseumfang und Evidenz",
                "body_md": """Wähle, welche Gegenstationen und Beobachtungen zu deinen Ergebnissen beitragen und wie viel Evidenz für Stations- und Kartenzusammenfassungen erforderlich ist. Prüfe die angezeigten Einstellungen und ändere sie dort, wo deine Fragestellung es erfordert. Diese Werte gelten auch dann, wenn du diesen Bereich unverändert lässt.""",
            },
            "review_and_run": {
                "title": "Prüfen und starten",
                "body_md": """Prüfe, ob diese Zusammenfassung zu dem Stationsaufbau und Betriebszeitraum passt, den du tatsächlich analysieren möchtest. Sie definiert Target, Referenz, Band, UTC-Zeitraum, Umfang und Evidenzregeln des Laufs. Die geführte und die klassische Eingabe bearbeiten dieselbe wissenschaftliche Konfiguration; der Wechsel der Eingabeansicht verändert die Analyse nicht.""",
            },
        },
        "options": {
            "use_cases": {
                "rx_performance": {
                    "label": "RX Performance",
                    "description": """Untersuche, wie gut dein Empfänger WSPR-Signale hört. Erkunde Empfangsmuster nach Richtung, Entfernung und Zeit und sieh, wie häufig Signale bei bestätigten Empfangsgelegenheiten dekodiert werden. Keine Referenz nötig.""",
                },
                "tx_performance": {
                    "label": "TX Performance",
                    "description": """Untersuche, wie gut andere Stationen deine WSPR-Aussendungen hören. Erkunde Empfangsmuster nach Richtung, Entfernung und Zeit und sieh, wie häufig dein Signal bei bestätigten Empfangsgelegenheiten dekodiert wird. Keine Referenz nötig.""",
                },
                "rx_benchmark": {
                    "label": "RX-Benchmark",
                    "description": """Vergleiche deinen Empfänger oder Empfangspfad mit einem anderen Aufbau, einer bekannten Station oder benachbarten Stationen. Untersuche anhand von Beobachtungen aus denselben WSPR-Zyklen Unterschiede im Empfang nach Richtung, Entfernung und Zeit.""",
                },
                "tx_benchmark": {
                    "label": "TX-Benchmark",
                    "description": """Vergleiche deinen Sender, Sendepfad oder deine vollständige Station mit einem anderen Aufbau, einer bekannten Station oder benachbarten Stationen. Untersuche anhand von Beobachtungen aus denselben WSPR-Zyklen Unterschiede im Empfang nach Richtung, Entfernung und Zeit.""",
                },
            },
            "reference_design": {
                "reference_station": {
                    "label": "Referenzaufbau/-station",
                    "description": """Vergleiche mit einem weiteren kontrollierten Signalpfad an deiner Station oder einer bekannten Station am selben oder einem anderen Standort. Ein kontrollierter Aufbau hilft dir, Unterschiede in der Ausrüstung zu untersuchen; eine unabhängige Station ermöglicht einen Vergleich vollständiger Stationen und ihrer Betriebsbedingungen.""",
                },
                "local_neighborhood": {
                    "label": "Referenznachbarschaft",
                    "description": """Vergleiche mit dem lokalen Median qualifizierender benachbarter Stationen innerhalb deines gewählten Radius. Dies ermöglicht einen lokalen Vergleich, wenn dir keine geeignete einzelne Referenz zur Verfügung steht. Die beitragenden Stationen können je nach Signalpfad und Zeitpunkt variieren.""",
                },
            },
            "local_benchmark": {
                "local_median": {
                    "label": """Lokaler Nachbarschafts-Median""",
                    "description": """Vergleicht das Target für jede entfernte Station und jeden WSPR-Zyklus mit dem Median der qualifizierenden Beiträge benachbarter Stationen. Die Beitragenden können je nach Funkweg und Zyklus wechseln. Das Ergebnis beschreibt das Verhalten der vollständigen Station im Vergleich zu diesen beobachteten Peers.""",
                },
            },
            "offset_intent": {
                "no_offset": {
                    "label": "Kein ermittelter Offset — 0,0 dB verwenden",
                    "description": """Wende keine referenzseitige Korrektur an. Verwende dies für einen ersten Erkundungslauf oder wenn keine belastbare Basislinie vorliegt und in diesem Lauf keine ermittelt wird. Ein stabiler Target–Referenz-Versatz bleibt dann Teil des ausgewiesenen ΔSNR.""",
                },
                "established_offset": {
                    "label": "Ermittelte Korrektur verwenden",
                    "description": """Wende eine dokumentierte Korrektur mit Vorzeichen an, die für dieselben Pfade oder Kennungen, dasselbe Band, dieselbe Hardware und dieselbe Vergleichsmethode ermittelt wurde. Trage den Wert unten ein, nachdem du diese Option ausgewählt hast. Die oben gezeigte Formel erklärt, wie das Vorzeichen das korrigierte ΔSNR verändert.""",
                },
                "establish_offset": {
                    "label": "Offset-Ermittlungslauf einrichten",
                    "description": """Führe Benchmark mit 0,0 dB Korrektur aus, um die vorhandene Target–Referenz-Basislinie zu bestimmen. WSPRadar zeigt die gepaarte Evidenz, wählt aber keine Korrektur automatisch aus. Prüfe und dokumentiere das Ergebnis und trage anschließend in einem späteren Lauf einen belastbaren Wert mit korrektem Vorzeichen ein.""",
                },
            },
        },
        "summaries": {
            "window_utc": "{start}–{end} UTC",
            "window_incomplete": "UTC-Zeitraum unvollständig",
            "use_case": "{step} · Frage — {choice} ✓",
            "target_and_window": "{step} · Target — {callsign} · {qth} · {band} · {window} ✓",
            "reference_station": "{step} · Referenz — {callsign} · {qth} ✓",
            "reference_local_median": "{step} · Referenz — lokaler Median innerhalb {radius} km ✓",
            "offset_none": "{step} · Referenzkorrektur — 0,0 dB ✓",
            "offset_established": "{step} · Referenzkorrektur — {offset:+.1f} dB ✓",
            "offset_establish": "{step} · Basislinienlauf — 0,0 dB Korrektur ✓",
            "scope": "{step} · Optionale Filter, Analyseumfang und Evidenz — max. {distance} km · {solar} ✓",
            "review_ready": "{step} · Prüfung — startbereit ✓",
        },
        "messages": {
            "use_case_limits": """Die Ergebnisse spiegeln die vollständigen Stationen und die beobachteten Bedingungen wider. Sie allein liefern keine absolute Messung der Empfängerempfindlichkeit, der abgestrahlten Leistung, des Antennengewinns oder des Antennenwirkungsgrads.""",
            "demo_title": "Geführte Demo",
            "demo_preset": """Diese Demo lädt eine vollständige Voreinstellung für ein dokumentiertes Beispiel. Belasse die Werte beim ersten Lauf unverändert und nutze das Beispiel, um zu sehen, wie Fragestellung, Kennungen und Analyseparameter zum angezeigten Ergebnis führen. Die Demo beschreibt die aufgeführten Stationen und den historischen Zeitraum; sie ist keine Aussage über deine eigene Station.""",
            "demo_walkthrough": "Einstellungen Schritt für Schritt durchgehen",
            "demo_walkthrough_help": "Prüfe jede Voreinstellung und erfahre, was sie in der Analyse verändert.",
            "demo_skip_to_review": "Direkt zu Prüfen und starten",
            "demo_skip_to_review_help": "Öffne die vollständige Konfigurationsübersicht und starte die Analyse sofort mit den aktuellen Einstellungen.",
            "local_existing_correction_warning": """Diese Konfiguration enthält bereits eine Korrektur von {offset:+.1f} dB für die lokale Referenz. Der normale geführte Nachbarschaftspfad verändert diesen erweiterten Wert nicht; er würde deshalb weiterhin jedes ΔSNR beeinflussen. Öffne vor dem Start die Klassische Eingabe, um ihn zu prüfen oder zurückzusetzen.""",
            "correction_formula": """**Korrigiertes ΔSNR = Target-SNR − (Referenz-SNR + Korrektur)**\x20\x20\nEin positives ΔSNR spricht für das Target, ein negativer Wert für die Referenz.""",
            "correction_consequence": """Vor der Subtraktion werden zu jedem Referenz-SNR {offset:+.1f} dB addiert. Eine positive Korrektur senkt das korrigierte ΔSNR; eine negative Korrektur erhöht es.""",
            "establish_reference_guidance": """Auf Stationsebene erhält jede Station eine Stimme; dies ist meist der bessere Standard für das stationsbalancierte WSPRadar-Ergebnis. Auf Spotebene erhält jede Beobachtung eine Stimme, sodass Stationen mit vielen Reports dominieren können. Der Median ist robuster gegenüber Ausreißern und Schiefe. Das arithmetische Mittel kann bei einer annähernd symmetrischen Verteilung ohne einflussreiche Extremwerte sinnvoll sein, reagiert aber empfindlicher darauf. Wähle nach der beabsichtigten Gewichtung und Evidenzverteilung — nicht nach dem bevorzugten Ergebnis. Weichen die Schätzwerte deutlich voneinander ab, untersuche die Ursache, statt einen passenden Wert herauszugreifen; möglicherweise ist ein konstanter Offset nicht vertretbar. Prüfe die Stabilität über Stationen, Signalpegel und Zeit, wiederhole die Basislinie anschließend unter demselben Betriebsdesign und bestätige, dass das korrigierte ΔSNR plausibel um `0 dB` zentriert ist. Bei einer kontrollierten Basislinie mit gemeinsamem Eingang wiederholst du den Lauf oder vertauschst die Pfade und prüfst, ob das korrigierte ΔSNR bei gemeinsamem Eingang plausibel um `0 dB` zentriert ist.""",
            "calibration_run_notice": """Offset-Ermittlungslauf: Die Referenzkorrektur ist auf 0,0 dB festgelegt. Führe die normale Benchmark-Analyse aus, um die unkorrigierte Basislinie Target − Referenz zu bestimmen. WSPRadar zeigt die verfügbaren Zusammenfassungen, wählt aber keinen Offset aus und wendet keinen an.

Wähle und dokumentiere nach dem Lauf genau einen ΔSNR-Schätzwert: Median oder arithmetisches Mittel aus **Stationsmediane** oder aus **Joint-Spots**. Trage den beobachteten Wert Target − Referenz mit demselben Vorzeichen im nächsten Lauf als Referenzkorrektur ein — beispielsweise `+1.6 dB` bei einer Basislinie von `+1.6 dB`.""",
            "station_population_title": "Remote Stationsfilter",
            "station_population_body": """<strong class="defined-term">Gegenstationen</strong> sind bei RX-Analysen die Sender, auf deren Signale dein Target hört, und bei TX-Analysen die Empfänger, die auf die Signale deines Targets hören. Mit diesen Filtern schränkst du ein, welche dieser Stationen zur Analyse beitragen.

Der Spezial-Rufzeichenfilter schließt entfernte Rufzeichen aus, die mit Q, 0 oder 1 beginnen und typischerweise für Ballontelemetrie verwendet werden. Target- und Referenzstationen einschließlich der Stationen, die zur Referenz der lokalen Nachbarschaft beitragen, bleiben von diesem Filter unberührt.

Der Filter für bewegliche Stationen schließt entfernte Rufzeichen aus, die in den zulässigen Beobachtungen aus mehr als einem Gitterfeld mit vierstelligem Locator gemeldet wurden.

Nutze diese Filter, wenn die Ausschlüsse zu deiner Untersuchung passen. Sie können die Konsistenz verbessern, aber auch gültige Evidenz entfernen; wähle sie anhand deiner Fragestellung und nicht, um ein bevorzugtes Ergebnis zu erzielen.""",
            "analysis_scope_title": "Analyseumfang",
            "analysis_scope_body": """Nutze Sonnenstand am Target-QTH, um Beobachtungen bei Tageslicht, in der Nacht oder bei Greyline-Bedingungen am Standort des Targets zu untersuchen. Dies beschreibt die Position der Sonne am Target, nicht entlang des gesamten Funkwegs.

Die maximale Peer-Entfernung legt fest, wie weit beitragende Gegenstationen vom Target entfernt sein dürfen. Sie verändert die Evidenz, die in Analyse, Karte, Inspector und Exporte eingeht.""",
            "evidence_requirements_title": "Evidenzanforderungen",
            "compare_evidence_requirements_body": """Evidenzanforderungen legen eine Mindestbasis für deine Ergebnisse fest: genügend Beobachtungen je Station und genügend qualifizierende Stationen in jedem <strong class="defined-term">Kartensegment</strong> — einem geografischen Bereich, der durch Richtung und Entfernung definiert ist.

Eine Station qualifiziert sich für die ΔSNR-Karte, wenn sie die erforderliche Anzahl an <strong class="defined-term">Joint Spots</strong> liefert: Vergleiche von Target- und Referenzbeobachtungen aus demselben WSPR-Zyklus über dieselbe Gegenstation. Jede qualifizierende Station trägt einen medianen ΔSNR-Wert bei und zählt einmal zur Mindestzahl an Stationen im Kartensegment. Beobachtungen, die nur das Target oder nur die Referenz betreffen, erfüllen diese Anforderung an gepaarte Evidenz nicht.

Eine Station ist eine exakte Identität aus Rufzeichen + vollständig gemeldetem Locator; dasselbe Rufzeichen mit unterschiedlichen Locatorn zählt getrennt. Dies sind gemeldete Identitäten, keine Anzahl unabhängiger physischer Stationen.

Höhere Mindestwerte verlangen mehr unterstützende Evidenz, verringern aber Stationszahl und geografische Abdeckung. Sie beseitigen keine Ausbreitungseffekte und garantieren keine Messqualität.""",
            "success_evidence_requirements_body": """Evidenzanforderungen legen eine Mindestbasis für deine Ergebnisse fest: genügend Beobachtungen je Station und genügend qualifizierende Stationen in jedem <strong class="defined-term">Kartensegment</strong> — einem geografischen Bereich, der durch Richtung und Entfernung definiert ist.

Eine Station qualifiziert sich, wenn sie die erforderliche Anzahl <strong class="defined-term">bestätigter Empfangsgelegenheiten</strong> liefert. Dazu gehören erfolgreiche Target-Decodes und Gelegenheiten, bei denen andere Meldungen die relevante Aktivität belegen, aber der Target-Decode fehlt. Gezählt werden also nicht nur erfolgreiche Decodes. Ein Kartensegment benötigt zusätzlich die gewählte Anzahl qualifizierender Stationen.

Höhere Mindestwerte verlangen mehr unterstützende Evidenz, verringern aber Stationszahl und geografische Abdeckung. Sie beseitigen keine Ausbreitungseffekte und garantieren keine Messqualität.""",
            "included": "ausgeschlossen",
            "not_included": "einbezogen",
            "compare_evidence": """Joint-Evidenz ≥ {value} je Station; qualifizierte Stationen ≥ {stations} je Kartensegment""",

            "success_evidence": """bestätigte Gelegenheiten ≥ {value} je Station; qualifizierte Stationen ≥ {stations} je Kartensegment""",
            "review_question": "Fragestellung",
            "review_target": "Target",
            "review_target_value": "{callsign} bei {qth}",
            "review_reference": "Referenz",
            "review_band_window": "Band und UTC-Zeitraum",
            "review_correction": "Referenzseitige Korrektur",
            "review_population": "Remote Stationsfilter",
            "review_population_value": """Entfernte Peer-Rufzeichen mit Q, 0 oder 1 am Anfang {special}; Stationen mit Locatorwechsel {moving}""",
            "review_scope": "Sonnenzustand und geografischer Umfang",
            "review_evidence": "Evidenzanforderungen",
            "review_result": "Ergebnistyp",
            "result_performance": "Nur Performance — eigenständige Target-Werte",
            "result_benchmark": "Benchmark — relative Target–Referenz-Werte",
            "open_classic": "Klassische Eingabe öffnen",
            "continue": "Weiter",
            "configuration_changed": """Die Eingaben wurden seit dem letzten Lauf geändert. Starte die Analyse erneut, bevor du die Ergebnisse interpretierst.""",
            "reference_location_pending_short": "Standort noch offen",
        },
        "validation": {
            "use_case": "Wähle eine Fragestellung, bevor du fortfährst.",
            "target_and_window": "Gib eine gültige Target-Kennung und ein gültiges QTH ein, wähle ein Band und vervollständige den UTC-Messzeitraum.",
            "reference_design": "Vervollständige das gewählte Referenzdesign: Gib das Referenz-Rufzeichen ein oder lege den Radius der Referenznachbarschaft fest. Der Standort der festen Referenz wird automatisch bestimmt.",
            "offset_calibration": "Wähle, ob keine Korrektur verwendet, unten eine ermittelte Korrektur eingegeben oder ein Offset-Ermittlungslauf eingerichtet werden soll.",
            "scope_and_evidence": "Prüfe die aktiven Filter, den Analyseumfang und die Evidenzanforderungen und korrigiere vor dem Fortfahren jeden ungültigen Wert.",
            "review_and_run": "Vervollständige vor dem Start die erforderliche Fragestellung, das Target, den Messzeitraum, gegebenenfalls das Referenzdesign sowie die sichtbaren Umfangs- und Evidenzfelder.",
            "flow_invalid": "Die Geführte Eingabe ist nicht verfügbar, weil ihre Ablaufkonfiguration ungültig ist: {error}",
        },
    },
}

def absolute_terms(t, mode):
    """Return canonical calculation terms and localized Performance labels."""
    mode_key = "tx" if str(mode).upper().startswith("TX") else "rx"
    default_counter = "Other Signals" if mode_key == "tx" else "Elsewhere"
    default_short = "OS" if mode_key == "tx" else "E"

    counter = t.get(f"abs_{mode_key}_counter", default_counter)
    counter_short = t.get(f"abs_{mode_key}_counter_short", default_short)
    pair = t.get(f"abs_{mode_key}_pair", f"Target+{counter}")
    formula = t.get(f"abs_{mode_key}_formula", f"Target/(Target+{counter})")
    rate_column = t.get(
        f"abs_{mode_key}_rate_column",
        f"Target/(Target+{counter}) (%)",
    )
    counter_column = t.get(
        f"abs_{mode_key}_counter_column",
        counter,
    )
    return {
        "mode": mode_key.upper(),
        "target_column": t.get(f"abs_{mode_key}_target_column", "Target"),
        "counter": counter,
        "counter_short": counter_short,
        "counter_column": counter_column,
        "opportunity_success": t[
            f"success_{mode_key}_opportunity_success"
        ],
        "opportunity_counter": t[
            f"success_{mode_key}_opportunity_counter"
        ],
        "station_success": t[f"success_{mode_key}_station_success"],
        "station_counter": t[f"success_{mode_key}_station_counter"],
        "target_only_audit": t[f"success_{mode_key}_target_only_audit"],
        "show_counter": t[f"success_{mode_key}_show_counter"],
        "pair": pair,
        "formula": formula,
        "rate_column": rate_column,
    }
