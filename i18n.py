"""
Lokalisierungs-Modul (i18n) für WSPRadar.
Enthält alle Text-Strings für die Mehrsprachigkeit (DE/EN).
"""
from config import APP_VERSION, DB_URL


T = {
    "en": {
        'cfg_min_joint_pairs': "Minimum scheduled pairs per station",
        'hlp_min_joint_pairs': "Sequential TX A/B requires at least X joint scheduled pairs per station. The same numeric threshold applies to one-sided scheduled-pair categories.",
        'lbl_no_joint_pairs': "No joint scheduled pairs are available in this segment to calculate a \u0394 SNR histogram.",
        'fig_scheduled_pair_count': "Scheduled pair count",
        'fig_joint_spot_count': "Joint spot count",
        'fig_relative_joint_spot_density': "Relative joint-spot density (% of panel maximum)",
        'fig_relative_scheduled_pair_density': "Relative scheduled-pair density (% of panel maximum)",
        'lbl_chronological_bin_size': "Chronological bin size",
        'lbl_time_aggregation_bin_size': "Time aggregation bin size:",
        'lbl_selected_temporal_view': "Temporal view",
        'opt_temporal_chronological': "Chronological",
        'opt_temporal_utc_hour': "UTC-Hour",
        'fig_segment_chronological_delta': "\u0394 SNR over Time",
        'fig_segment_utc_hour_delta': "\u0394 SNR by UTC Hour",
        'fig_segment_utc_hour_title': "\u0394 SNR by UTC Hour (1 h bins)",
        'fig_rx_comp_temporal_prefix': "RX Compare Temporal",
        'fig_tx_comp_temporal_prefix': "TX Compare Temporal",
        'fig_segment_chronological_x': "Date/Time (UTC)",
        'fig_segment_utc_hour_x': "UTC hour",
        'fig_segment_dates_folded': "{count} UTC dates folded",
        'fig_segment_dates_insufficient': "{count} UTC dates available; folding unavailable",
        'fig_segment_folded_unavailable': "UTC-hour pattern unavailable - requires joint evidence from at least 2 UTC dates.",
        'fig_compare_median_focus_axis': "\u0394 SNR (dB \u00b7 median-centered nonlinear)",
        'fig_median_label': "Median",
        'fig_temporal_bin_median': "Bin median",
        'fig_segment_focus_median': "Segment median",
        'fig_selected_focus_median': "Selected median",
        'fig_scheduled_pair_delta': "Scheduled-Pair \u0394 SNR",
        'lbl_scheduled_pair_evidence': "Scheduled-pair",
        'tbl_col_joint_pairs': "Joint Pairs",
        'tbl_col_pair': "Scheduled Pair (UTC)",
        'tbl_col_micro_a': "Target Micro-Median",
        'tbl_col_micro_b': "Reference Micro-Median",
        'tbl_col_pair_delta': "Pair \u0394",
        'lbl_tx_ab_method': "TX A/B Method",
        'opt_tx_ab_simultaneous': "Simultaneous TX",
        'opt_tx_ab_sequential': "Sequential TX",
        'lbl_tx_ab_schedule': "TX A/B Schedule",
        'lbl_tx_ab_repeat_interval': "Repeat Interval",
        'lbl_tx_ab_target_start': "Target Start",
        'lbl_tx_ab_reference_start': "Reference Start",
        'hlp_tx_ab_repeat_interval': "Actual recurrence of each physical path. WSPRadar accepts even WSPR-compatible intervals that divide one UTC hour.",
        'hlp_tx_ab_start': "UTC minute phase for this path. Target and Reference starts are kept disjoint.",
        'hlp_tx_ab_swap': "Swap Target and Reference schedule attribution.",
        'txt_tx_ab_shared_interval': "Shared by Target and Reference paths",
        'txt_tx_ab_schedule_valid': "Disjoint schedules · {separation} min separation · {transmissions} transmissions/hour/path",
        'warn_tx_ab_high_duty': "This is a high-duty-cycle schedule. Confirm that the transmitter, network occupancy, and local operating practice permit it.",
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
        "lbl_config_time_policy": "How should this Last-X time selection be saved?",
        "opt_config_time_freeze": "Freeze the resolved UTC range",
        "opt_config_time_relative": "Keep Last-X relative",
        "txt_config_resolved_window": "Resolved run: {start} to {end}",
        "warn_config_freeze_unavailable": "Run the analysis first to freeze its resolved UTC range.",
        "warn_saved_station_unavailable": "Saved station selection could not be fully restored because these stations are not available in the current Station Insights table: {stations}. No substitute was selected.",
        "msg_config_prepared": "Config prepared. Download it below.",
        "err_config_save": "Config could not be prepared: {error}",
        "btn_apply_config": "Load Selected Config",
        "btn_load_demo_selected": "Load Selected Demo Configuration",
        "btn_run_demo_selected": "Run Selected Demo",
        "btn_download_all_results": "Download All Results",
        "btn_prepare_all_results": "Prepare All Results for Download",
        "btn_download_prepared_results": "Download Prepared Results",
        "hdr_results_compare": "{direction} Compare Results",
        "hdr_results_success": "{direction} Success Results",
        "sub_results_compare": "{callsign} (Target) vs. {comparison}",
        "sub_results_compare_scheduled": "{callsign} · Target schedule vs. Reference schedule",
        "sub_results_rx_success": "Target {callsign} · same signals heard elsewhere",
        "sub_results_tx_success": "Target {callsign} · Other Signals at active RX stations",
        "txt_results_metadata": "{band} · {utc_window} · Target QTH {qth}",
        "txt_results_reference_grid4": "Reference Grid-4 {grid4}",
        "txt_results_shared_grid4": "Shared Grid-4 {grid4}",
        "txt_results_reference_benchmark": "Reference benchmark {benchmark}",
        "txt_results_tx_schedule": "TX schedule {interval} min · Target :{target_phase} · Reference :{reference_phase} UTC",
        "fmt_results_thousands_separator": ",",
        "lbl_results_evidence_path": "Evidence path",
        "txt_results_evidence_path": "Map → Stations & Spots → Segment Inspector → Station Insights → Drill-Down",
        "lbl_results_level_run": "Complete run",
        "lbl_results_level_scope": "Geographic scope",
        "lbl_results_level_stations": "Contributing stations",
        "lbl_results_level_selection": "Selected stations",
        "lbl_results_level_rows": "Row-level evidence",
        "hdr_results_map_view": "Map View",
        "sub_results_map_compare": "Geographic overview of station-balanced ΔSNR and Decode Outcomes.",
        "sub_results_map_success": "Remote {station_type} stations grouped by distance and direction, showing station-balanced Success Rate.",
        "hdr_results_segment_inspector": "Segment Inspector",
        "sub_results_segment_inspector": "Choose one or more distance ranges and directions. All evidence below follows the active scope.",
        "lbl_results_distance_range": "Distance range",
        "lbl_results_direction": "Direction",
        "txt_results_active_scope": "Active scope · {distance} · {direction}",
        "txt_results_evidence_scope": "Evidence in scope · {station_count} · {evidence_count} {evidence_unit}",
        "txt_results_transition_scope": "↓ Select distance and direction to inspect a geographic scope",
        "txt_results_transition_stations": "↓ Select one or more stations to inspect their evidence",
        "txt_results_transition_rows": "↓ Review the underlying evidence rows",
        "hdr_results_comparison_evidence": "Comparison Evidence",
        "sub_results_comparison_evidence_joint": "Decode Outcomes, station medians, and joint-spot ΔSNR for the active scope.",
        "sub_results_comparison_evidence_scheduled": "Decode Outcomes, station medians, and scheduled-pair ΔSNR for the active scope.",
        "fmt_results_station_delta_summary": "Station-level · Median {median} dB · Mean {mean} dB",
        "fmt_results_joint_spot_delta_summary": "Joint-Spot level · Median {median} dB · Mean {mean} dB",
        "fmt_results_scheduled_pair_delta_summary": "Scheduled-Pair level · Median {median} dB · Mean {mean} dB",
        "hdr_results_temporal_evidence": "Temporal Evidence",
        "sub_results_temporal_evidence": "The same paired evidence shown chronologically and by UTC hour.",
        "lbl_include_unpaired_evidence": "Include Unpaired Evidence",
        "hdr_results_success_temporal": "Success & Temporal Evidence",
        "sub_results_success_temporal": "Evidence depth, station-balanced and observation-level Success Rate, and time pattern for the active scope.",
        "sub_results_station_insights": "Contributing {station_type} stations in the active scope. Select one or more rows to inspect their evidence.",
        "txt_results_station_scope": "Active scope · {distance} · {direction} · {station_count}",
        "hdr_results_selected_station_evidence": "Selected Station Evidence",
        "sub_results_selected_station_single": "{station} ({locator}) · {evidence_count} {evidence_unit}",
        "sub_results_selected_station_multi": "{selected_count} selected {station_type} stations · combined view · {evidence_count} {evidence_unit}",
        "txt_results_selected_no_paired_evidence": "No paired evidence is available for this selection; retained unpaired rows can still be audited below.",
        "hdr_results_drilldown": "Drill-Down Data",
        "sub_results_drilldown_single": "Row-level evidence for {station} within the active scope.",
        "sub_results_drilldown_multi": "Row-level evidence for {count} selected {station_type} stations within the active scope.",
        "txt_results_drilldown_filter_note": "Filters change only the displayed table, not the completed analysis.",
        "unit_joint_spot_singular": "joint spot",
        "unit_joint_spot_plural": "joint spots",
        "unit_scheduled_pair_singular": "scheduled pair",
        "unit_scheduled_pair_plural": "scheduled pairs",
        "unit_confirmed_opportunity_singular": "confirmed opportunity",
        "unit_confirmed_opportunity_plural": "confirmed opportunities",
        "unit_station_singular": "{count} contributing {station_type} station",
        "unit_station_plural": "{count} contributing {station_type} stations",
        "hdr_results_download_evidence": "Download Evidence",
        "sub_results_download_evidence": "Prepare the completed run, active Inspector scope, station selection, tables, metadata, and high-resolution figures as a reproducibility package; Save Config preserves reusable analysis settings separately.",
        "hdr_results_reusable_configuration": "Reusable Configuration",
        "sub_documentation": "Method, interpretation, controls, limitations, and troubleshooting.",
        "msg_preparing_all_results": "Preparing high-resolution result package...",
        "btn_prepare_documentation_pdf": "Prepare PDF",
        "btn_download_documentation_pdf": "Download PDF",
        "btn_load_full_documentation": "Load full documentation",
        "btn_hide_full_documentation": "Hide full documentation",
        "msg_loading_analysis_engine": "Preparing analysis engine...",
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
        "cbar_abs": "Average Station Success Rate (%)",
        "cbar_comp": "Median \u0394 Normalized SNR vs. Benchmark (1S=6dB)",
        "comp_title_ref": "{callsign} (Reference)",
        "comp_title_local_best": "Local Best Station (≤{radius} km)",
        "comp_title_local_median": "Local Median Neighborhood (≤{radius} km)",
        "config_title": "Configuration",
        "dev_credit": f"Release {APP_VERSION} | Repo: <a href='https://github.com/markusthemaker/WSPRadar/' target='_blank' style='color:#39ff14; text-decoration:none;'>GitHub</a> | License: <a href='https://github.com/markusthemaker/WSPRadar/blob/main/LICENSE' target='_blank' style='color:#39ff14; text-decoration:none;'>AGPLv3</a><br>Developed by Dr. Markus Brosch (DL1MKS) ",        
        "exp_adv": "⚙️ Filters, analysis scope and evidence",
        "exp_comp": "⚖️ Results view and benchmark design",
        "exp_core": "📡 Target and measurement window",
        "exp_metadata": "🏷️ Metadata",
        "fig_rx_abs": "RX Success: Target {callsign} vs. Same Signals Heard Elsewhere",
        "fig_rx_comp": "RX Compare: {callsign} (Target) vs. {comp_title}",
        "fig_tx_abs": "TX Success: Target {callsign} vs. Other Signals at Active RX Stations",
        "abs_rx_counter": "Elsewhere",
        "abs_rx_counter_short": "E",
        "abs_rx_target_column": "Target (T)",
        "abs_rx_pair": "Target+Elsewhere",
        "abs_rx_formula": "Target/(Target+Elsewhere)",
        "abs_rx_formula_spaced": "Target / (Target + Elsewhere)",
        "abs_rx_rate_column": "T/(T+E) (%)",
        "abs_rx_counter_column": "Elsewhere (E)",
        "abs_rx_count_axis": "Target + Elsewhere count",
        "abs_rx_counter_marker": "E (Elsewhere)",
        "abs_rx_no_evidence": "No T/E evidence",
        "abs_rx_empty_evidence": "No Target/Elsewhere evidence",
        "abs_rx_subtext": " (T=Target | E=Elsewhere | Click a row for evidence)",
        "abs_tx_counter": "Other Signals",
        "abs_tx_counter_short": "OS",
        "abs_tx_target_column": "Target (T)",
        "abs_tx_pair": "Target+Other Signals",
        "abs_tx_formula": "Target/(Target+Other Signals)",
        "abs_tx_formula_spaced": "Target / (Target + Other Signals)",
        "abs_tx_rate_column": "T/(T+OS) (%)",
        "abs_tx_counter_column": "Other Signals (OS)",
        "abs_tx_count_axis": "Target + Other Signals count",
        "abs_tx_counter_marker": "OS (Other Signals)",
        "abs_tx_no_evidence": "No T/OS evidence",
        "abs_tx_empty_evidence": "No Target/Other Signals evidence",
        "abs_tx_subtext": " (T=Target | OS=Other Signals | Click a row for evidence)",
        "fig_tx_comp": "TX Compare: {callsign} (Target) vs. {comp_title}",
        "hlp_max_dist": "Scientific maximum distance of mapped peers from Target QTH. Only peers strictly nearer than this maximum remain in the processed result, map, Inspector and export; the provider query and raw query cache remain global.",
        "hlp_min_spots": "Compare maps require at least X joint spots per station.",
        "hlp_min_opportunities": "Absolute success-rate views include a station only after this many Target+counter-evidence observations. Counter-evidence is Elsewhere for RX and Other Signals for TX. Target-only observations never enter Target, counter-evidence, or the denominator.",
        "hlp_min_stations": "A map segment requires at least X qualifying stations. Compare uses the joint-evidence threshold; Absolute uses the mode-specific Target+counter-evidence threshold.",
        "hlp_benchmark_offset_db": "Added to the reference-side SNR before \u0394 SNR is calculated. Applies to compare maps only. Buddy/local benchmarks use the reference side; Hardware A/B uses the Reference identity or Reference schedule. If a calibration run shows target-reference = +1.6 dB, enter +1.6 dB.",
        "hlp_callsign_entry": "Use the exact identifier uploaded to WSPR. Standard callsign forms are recommended; in addition to slash forms such as DL1MKS/P, WSPRadar accepts one terminal alphanumeric hyphen suffix such as DL1MKS-1. Each spelling is a distinct identity.",
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
        "msg_select_analysis_direction_hardware": "Select RX or TX Analysis before configuring the direction-specific Hardware A/B parameters.",
        "lbl_comp_mode": "Results view and benchmark design",
        "lbl_drill_multi": "**Drill-Down Data: {count} Stations Selected** (Normalized @ 1W)",
        "lbl_drill_single": "**Drill-Down Data: {station}** (Normalized @ 1W)",
        "lbl_end_d": "End Date",
        "lbl_end_t": "End Time (UTC)",
        "lbl_hist_count": "Count (Stations)",
        "lbl_hist_x_abs": "{station_type} Median of Norm. SNR (dB @ 1W)",
        "lbl_hist_x_comp": "{station_type} Median of \u0394 Norm. SNR (dB)",
        "lbl_hours": "Last X Hours",
        "lbl_insights": "Station Insights",
        "lbl_insights_sub": " (Normalized @ 1W | Click a row for Forensic Data)",
        "lbl_show_zero_hits": "Show Zero-Target",
        "lbl_max_dist": "Maximum peer distance from Target (km)",
        "lbl_med_seg": "Segment Median: {med:.1f} dB",
        "lbl_med_stat": "Median: {med:.1f} dB",
        "lbl_min_spots": "Minimum joint evidence per station",
        "lbl_min_opportunities": "Minimum confirmed opportunities per station",
        "lbl_min_stations": "Minimum qualifying stations per map segment",
        "lbl_no_joint": "No joint spots available in this segment to calculate a \u0394 SNR histogram.",
        "lbl_qth": "Target QTH (4 or 6 characters)",
        "lbl_local_benchmark": "Local Benchmark Method",
        "lbl_radius": "Nearest Ref. Stations (per Cycle)",
        "lbl_ref_radius_km": "Neighborhood Radius (km)",
        "lbl_ref_call": "Reference Callsign",
        "lbl_target_callsign": "Target callsign",
        "lbl_reference_callsign": "Reference callsign",
        "lbl_target_qth": "Target QTH",
        "lbl_reference_qth": "Reference QTH",
        "lbl_target_grid4": "Target Grid-4",
        "lbl_reference_grid4": "Reference Grid-4",
        "ph_reference_callsign": "e.g. DL1MKS/P or DL1MKS-1",
        "ph_reference_qth": "e.g. JN37",
        "txt_target": "Target",
        "txt_reference": "Reference",
        "lbl_solar": "Solar state at Target QTH",
        "lbl_start_d": "Start Date",
        "lbl_start_t": "Start Time (UTC)",
        "lbl_time_mode": "UTC measurement window",
        "txt_benchmark_offset_note": "Ref SNR Corr: {offset:+.1f} dB",
        "opt_comp_none": "Success — Target only",
        "opt_comp_radius": "Compare — local neighborhood benchmark",
        "opt_comp_buddy": "Compare — Known Reference Station",
        "opt_comp_self": "Compare — Hardware A/B",
        "opt_local_best": "Local Best Station",
        "opt_local_median": "Local Median Neighborhood",
        "err_self_test": "You entered your own callsign. Please use 'Hardware A/B-Test' mode.",
        "err_reference_callsign_same": "Target and Reference callsigns must be different.",
        "err_reference_callsign_required": "Please configure a Reference Callsign.",
        "err_reference_qth_required": "Please configure a Reference Grid-4.",
        "err_callsign_format": "Enter a plausible callsign/reporting identifier: 3-15 ASCII characters; use '/' only between non-empty alphanumeric segments and at most one terminal '-' before a non-empty alphanumeric suffix. At least one segment before any hyphen must contain both a letter and a digit.",
        "err_qth_format": "Enter a valid 4- or 6-character Maidenhead locator (e.g. JN37 or JN37AA).",
        "err_reference_callsign_format": "Enter a plausible Reference Callsign: 3-15 ASCII characters; use '/' only between non-empty alphanumeric segments and at most one terminal '-' before a non-empty alphanumeric suffix. At least one segment before any hyphen must contain both a letter and a digit.",
        "err_reference_qth_format": "Enter a valid 4- or 6-character Reference QTH Maidenhead locator (e.g. JN37 or JN37AA).",
        "err_reference_grid4_format": "Enter an exact 4-character Reference Maidenhead grid (e.g. JN37).",
        "err_reference_qth_match_target": "Reference QTH is derived from Target QTH in Hardware A/B mode.",
        "err_reference_qth_grid4": "Target and Reference QTH must share the same grid-4 in Hardware A/B mode.",
        "err_loc_length": "Error: Both locators must be exactly 6 characters long for an RX A/B-Test.",
        "err_loc_match": "Error: The first 4 characters of both locators must be identical.",
        "err_loc_format": "Error: Invalid 6-character locator format (e.g., JN37AA).",
        "err_loc_identical": "Error: Locators must be different (e.g., AA vs AB) to generate joint spots.",
        "err_loc_incomplete": "Error: Please complete a valid 6-character locator setup before running the analysis.",
        "lbl_qth_a": "Target Locator (Antenna A)",
        "lbl_qth_b": "Reference Locator (Antenna B)",
        "leg_both_async": "Both (Async)",
        "leg_abs_eligible": "Target/counter-evidence",
        "leg_abs_insufficient": "Below Target+counter-evidence threshold",
        "leg_abs_target_only": "Target-only evidence",
        "leg_abs_hit": "T (Target)",
        "leg_abs_hit_one": "Target (T) = 1",
        "leg_abs_hit_mid": "Target (T) = 2-5",
        "leg_abs_hit_high": "Target (T) > 5",
        "leg_abs_miss": "E (Elsewhere)",
        "leg_abs_no_hm": "No T/E evidence",
        "leg_joint": "Both (Joint)",
        "leg_only_me": "Only {callsign}",
        "leg_only_ref": "Only {ref_callsign}",
        "leg_only_ref_radius": "Only Reference",
        "msg_proc": "Processing {id}...",
        "msg_analysis_queue_wait": "All analysis capacity is in use; queued at position {position}.",
        "msg_analysis_queue_detail": "Analyses waiting: {queued}.",
        "msg_analysis_duplicate": "This identical analysis is already active or queued for this session.",
        "msg_analysis_submission_active": "Analysis submitted; Run Analysis is disabled until it finishes.",
        "msg_config_loaded": "Config loaded. Existing results were cleared.",
        "msg_sync": "Synchronizing active time cycles...",
        "opt_all_dirs": "All Directions",
        "opt_custom": "Custom Date/Time",
        "opt_full_range": "Full Range",
        "opt_insp_dir": "--- Segment Inspector (Direction) ---",
        "opt_insp_dist": "--- Segment Inspector (Distance) ---",
        "opt_last_x": "Last X Hours",
        "opt_no_station": "No Stations",
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
        "tbl_col_med_snr": "Median SNR (dB)",
        "tbl_col_only_ref": "Only Reference",
        "tbl_col_only_u": "Only {callsign}",
        "tbl_col_cycle_ref_median": "Cycle Ref Median SNR (dB)",
        "tbl_col_delta_snr": "\u0394 SNR (dB)",
        "lbl_neighborhood": "Neighborhood",
        "tbl_col_ref_median_km": "Median Ref km",
        "tbl_col_ref_pool": "Ref Pool",
        "tbl_col_ref_snr": "Ref SNR (dB)",
        "tbl_col_ref_station": "Ref Station",
        "tbl_col_rx": "RX Station",
        "tbl_col_spots": "Spots",
        "tbl_col_opportunities": "Target+Counter-Evidence",
        "tbl_col_hits": "Target",
        "tbl_col_misses": "Counter-Evidence",
        "tbl_col_target_only": "Target-only",
        "tbl_col_rate": "Success Rate (%)",
        "tbl_col_success_snr": "Median Target SNR (dB @ 1W)",
        "tbl_col_eligible": "Qualified",
        "txt_abs_evidence_summary": "Evidence ({pair} >= {threshold} per station): Target {target} | {counter} {counter_count}",
        "txt_abs_rate_summary": "Success Rate {formula}: Average by Station {station_average:.1f}% | Observation-Level {overall:.1f}%",
        "txt_abs_no_eligible": "No station meets the {pair} threshold in this scope.",
        "tbl_col_tx": "TX Station",
        "lbl_exclude_special": "Exclude Special Callsigns Q, 0, 1",
        "hdr_remote_station_filters": "Remote station filters",
        "hdr_analysis_scope": "Analysis scope",
        "hdr_evidence_requirements": "Evidence requirements",
        "tt_exclude_special": "Filter out balloon telemetry.","title": "WSPRadar.org",
        "lbl_filter_moving": "Exclude Moving Stations",
        "tt_filter_moving": "Filters out balloons, cars, or ships that change their Grid Locator during the selected timeframe.","txt_joint": "Joint",
        "txt_joint_decodes": "Joint Decodes",
        "txt_remote": "Total Remote",
        "txt_rx_stations": "RX Stations",
        "txt_total_decodes": "Total Decodes",
        "txt_tx_stations": "TX Stations",
        "warn_analysis_queue_full": "High demand right now. The analysis queue is full. Please try again shortly.",
        "warn_analysis_queue_timeout": "Analysis capacity did not become available in time. Please run the analysis again.",
        "warn_no_data": "Not enough qualifying data found for **{title}** after applying filters. Are the callsign entries, locator, band, date, and UTC time correct?",
        "err_config_load": "Config could not be loaded: {error}"
    },
    "de": {
        'cfg_min_joint_pairs': "Minimale geplante Paare pro Station",
        'hlp_min_joint_pairs': "Sequenzielles TX A/B erfordert mindestens X gemeinsame geplante Paare pro Station. Derselbe Zahlenwert gilt f\u00fcr einseitige Paar-Kategorien.",
        'lbl_no_joint_pairs': "Keine gemeinsamen geplanten Paare in diesem Segment f\u00fcr ein \u0394-SNR-Histogramm vorhanden.",
        'fig_scheduled_pair_count': "Anzahl geplanter Paare",
        'fig_joint_spot_count': "Anzahl Joint Spots",
        'fig_relative_joint_spot_density': "Relative Joint-Spot-Dichte (% des Panelmaximums)",
        'fig_relative_scheduled_pair_density': "Relative Dichte geplanter Paare (% des Panelmaximums)",
        'lbl_chronological_bin_size': "Chronologische Bin-Breite",
        'lbl_time_aggregation_bin_size': "Zeitliche Aggregationsbreite:",
        'lbl_selected_temporal_view': "Zeitansicht",
        'opt_temporal_chronological': "Chronologisch",
        'opt_temporal_utc_hour': "UTC-Stunde",
        'fig_segment_chronological_delta': "\u0394 SNR im Zeitverlauf",
        'fig_segment_utc_hour_delta': "\u0394 SNR nach UTC-Stunde",
        'fig_segment_utc_hour_title': "\u0394 SNR nach UTC-Stunde (1-h-Bins)",
        'fig_rx_comp_temporal_prefix': "RX Vergleich - Zeitverlauf",
        'fig_tx_comp_temporal_prefix': "TX Vergleich - Zeitverlauf",
        'fig_segment_chronological_x': "Datum/Uhrzeit (UTC)",
        'fig_segment_utc_hour_x': "UTC-Stunde",
        'fig_segment_dates_folded': "{count} UTC-Tage zusammengef\u00fchrt",
        'fig_segment_dates_insufficient': "{count} UTC-Tage verf\u00fcgbar; Faltung nicht verf\u00fcgbar",
        'fig_segment_folded_unavailable': "UTC-Stundenmuster nicht verf\u00fcgbar - erfordert gemeinsame Evidenz aus mindestens 2 UTC-Tagen.",
        'fig_compare_median_focus_axis': "\u0394 SNR (dB \u00b7 nichtlinear um Median zentriert)",
        'fig_median_label': "Median",
        'fig_temporal_bin_median': "Lokaler Median",
        'fig_segment_focus_median': "Segmentmedian",
        'fig_selected_focus_median': "Median der Auswahl",
        'fig_scheduled_pair_delta': "Geplantes Paar \u0394 SNR",
        'lbl_scheduled_pair_evidence': "Geplantes Paar",
        'tbl_col_joint_pairs': "Joint-Paare",
        'tbl_col_pair': "Geplantes Paar (UTC)",
        'tbl_col_micro_a': "Target-Mikromedian",
        'tbl_col_micro_b': "Referenz-Mikromedian",
        'tbl_col_pair_delta': "Paar \u0394",
        'lbl_tx_ab_method': "TX-A/B-Methode",
        'opt_tx_ab_simultaneous': "Simultanes TX",
        'opt_tx_ab_sequential': "Sequenzielles TX",
        'lbl_tx_ab_schedule': "TX-A/B-Zeitplan",
        'lbl_tx_ab_repeat_interval': "Wiederholintervall",
        'lbl_tx_ab_target_start': "Target-Start",
        'lbl_tx_ab_reference_start': "Referenz-Start",
        'hlp_tx_ab_repeat_interval': "Tatsächliche Wiederholung jedes physischen Pfads. WSPRadar akzeptiert gerade WSPR-kompatible Intervalle, die eine UTC-Stunde teilen.",
        'hlp_tx_ab_start': "UTC-Minutenphase dieses Pfads. Target- und Referenz-Start bleiben disjunkt.",
        'hlp_tx_ab_swap': "Target- und Referenz-Zuordnung tauschen.",
        'txt_tx_ab_shared_interval': "Gemeinsam für Target- und Referenzpfad",
        'txt_tx_ab_schedule_valid': "Disjunkte Zeitpläne · {separation} min Abstand · {transmissions} Aussendungen/Stunde/Pfad",
        'warn_tx_ab_high_duty': "Dies ist ein Zeitplan mit hoher Sendedauer. Prüfe Sender, Netzauslastung und lokale Betriebspraxis.",
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
        "lbl_config_time_policy": "Wie soll diese Letzte-X-Zeitauswahl gespeichert werden?",
        "opt_config_time_freeze": "Aufgel\u00f6sten UTC-Zeitraum fixieren",
        "opt_config_time_relative": "Letzte X relativ beibehalten",
        "txt_config_resolved_window": "Aufgel\u00f6ster Lauf: {start} bis {end}",
        "warn_config_freeze_unavailable": "Zuerst die Analyse starten, um ihren aufgel\u00f6sten UTC-Zeitraum zu fixieren.",
        "warn_saved_station_unavailable": "Die gespeicherte Stationsauswahl konnte nicht vollst\u00e4ndig wiederhergestellt werden, weil diese Stationen in der aktuellen Station-Insights-Tabelle nicht verf\u00fcgbar sind: {stations}. Es wurde kein Ersatz ausgew\u00e4hlt.",
        "msg_config_prepared": "Konfiguration vorbereitet. Sie kann unten heruntergeladen werden.",
        "err_config_save": "Konfiguration konnte nicht vorbereitet werden: {error}",
        "btn_apply_config": "Ausgewaehlte Konfig laden",
        "btn_load_demo_selected": "Ausgewaehlte Demo-Konfiguration laden",
        "btn_run_demo_selected": "Ausgewaehlte Demo starten",
        "btn_download_all_results": "Alle Ergebnisse herunterladen",
        "btn_prepare_all_results": "Alle Ergebnisse zum Download vorbereiten",
        "btn_download_prepared_results": "Vorbereitete Ergebnisse herunterladen",
        "hdr_results_compare": "{direction}-Compare-Ergebnisse",
        "hdr_results_success": "{direction}-Success-Ergebnisse",
        "sub_results_compare": "{callsign} (Target) vs. {comparison}",
        "sub_results_compare_scheduled": "{callsign} · Target-Zeitplan vs. Referenz-Zeitplan",
        "sub_results_rx_success": "Target {callsign} · dieselben Signale andernorts empfangen",
        "sub_results_tx_success": "Target {callsign} · Other Signals an aktiven RX-Stationen",
        "txt_results_metadata": "{band} · {utc_window} · Target-QTH {qth}",
        "txt_results_reference_grid4": "Referenz-Grid-4 {grid4}",
        "txt_results_shared_grid4": "Gemeinsames Grid-4 {grid4}",
        "txt_results_reference_benchmark": "Referenz-Benchmark {benchmark}",
        "txt_results_tx_schedule": "TX-Zeitplan {interval} min · Target :{target_phase} · Referenz :{reference_phase} UTC",
        "fmt_results_thousands_separator": ".",
        "lbl_results_evidence_path": "Evidenzpfad",
        "txt_results_evidence_path": "Karte → Stationen & Spots → Segment-Inspektor → Station Insights → Drill-Down",
        "lbl_results_level_run": "Vollständiger Lauf",
        "lbl_results_level_scope": "Geografischer Bereich",
        "lbl_results_level_stations": "Beitragende Stationen",
        "lbl_results_level_selection": "Ausgewählte Stationen",
        "lbl_results_level_rows": "Evidenz auf Zeilenebene",
        "hdr_results_map_view": "Kartenansicht",
        "sub_results_map_compare": "Geografischer Überblick über stationsgleichgewichtetes Δ SNR und Decode Outcomes.",
        "sub_results_map_success": "Remote {station_type}-Stationen nach Entfernung und Richtung gruppiert; dargestellt ist die stationsgleichgewichtete Success Rate.",
        "hdr_results_segment_inspector": "Segment-Inspektor",
        "sub_results_segment_inspector": "Wähle einen oder mehrere Entfernungsbereiche und Himmelsrichtungen. Alle nachfolgenden Evidenzansichten beziehen sich auf den aktiven Bereich.",
        "lbl_results_distance_range": "Entfernungsbereich",
        "lbl_results_direction": "Richtung",
        "txt_results_active_scope": "Aktiver Bereich · {distance} · {direction}",
        "txt_results_evidence_scope": "Evidenz im aktiven Bereich · {station_count} · {evidence_count} {evidence_unit}",
        "txt_results_transition_scope": "↓ Wähle Entfernung und Richtung, um einen geografischen Bereich zu untersuchen",
        "txt_results_transition_stations": "↓ Wähle eine oder mehrere Stationen, um ihre Evidenz zu untersuchen",
        "txt_results_transition_rows": "↓ Prüfe die zugrunde liegenden Evidenzzeilen",
        "hdr_results_comparison_evidence": "Vergleichsevidenz",
        "sub_results_comparison_evidence_joint": "Decode Outcomes, Stationsmediane und Δ SNR aus Joint Spots im aktiven Bereich.",
        "sub_results_comparison_evidence_scheduled": "Decode Outcomes, Stationsmediane und Δ SNR aus geplanten Paaren im aktiven Bereich.",
        "fmt_results_station_delta_summary": "Stationsebene · Median {median} dB · Mittelwert {mean} dB",
        "fmt_results_joint_spot_delta_summary": "Joint-Spot-Ebene · Median {median} dB · Mittelwert {mean} dB",
        "fmt_results_scheduled_pair_delta_summary": "Ebene geplanter Paare · Median {median} dB · Mittelwert {mean} dB",
        "hdr_results_temporal_evidence": "Zeitliche Evidenz",
        "sub_results_temporal_evidence": "Dieselbe gepaarte Evidenz, chronologisch und nach UTC-Stunde dargestellt.",
        "lbl_include_unpaired_evidence": "Ungepaarte Evidenz einbeziehen",
        "hdr_results_success_temporal": "Success & zeitliche Evidenz",
        "sub_results_success_temporal": "Evidenzumfang, stationsgleichgewichtete Success Rate, Success Rate auf Beobachtungsebene und zeitlicher Verlauf im aktiven Bereich.",
        "sub_results_station_insights": "Beitragende {station_type}-Stationen im aktiven Bereich. Wähle eine oder mehrere Zeilen, um ihre Evidenz zu untersuchen.",
        "txt_results_station_scope": "Aktiver Bereich · {distance} · {direction} · {station_count}",
        "hdr_results_selected_station_evidence": "Evidenz ausgewählter Stationen",
        "sub_results_selected_station_single": "{station} ({locator}) · {evidence_count} {evidence_unit}",
        "sub_results_selected_station_multi": "{selected_count} ausgewählte {station_type}-Stationen · kombinierte Ansicht · {evidence_count} {evidence_unit}",
        "txt_results_selected_no_paired_evidence": "Für diese Auswahl liegt keine gepaarte Evidenz vor; beibehaltene ungepaarte Zeilen können unten weiterhin geprüft werden.",
        "hdr_results_drilldown": "Drill-Down-Daten",
        "sub_results_drilldown_single": "Evidenz auf Zeilenebene für {station} im aktiven Bereich.",
        "sub_results_drilldown_multi": "Evidenz auf Zeilenebene für {count} ausgewählte {station_type}-Stationen im aktiven Bereich.",
        "txt_results_drilldown_filter_note": "Filter verändern nur die angezeigte Tabelle, nicht die abgeschlossene Analyse.",
        "unit_joint_spot_singular": "Joint Spot",
        "unit_joint_spot_plural": "Joint Spots",
        "unit_scheduled_pair_singular": "geplantes Paar",
        "unit_scheduled_pair_plural": "geplante Paare",
        "unit_confirmed_opportunity_singular": "bestätigte Gelegenheit",
        "unit_confirmed_opportunity_plural": "bestätigte Gelegenheiten",
        "unit_station_singular": "{count} beitragende {station_type}-Station",
        "unit_station_plural": "{count} beitragende {station_type}-Stationen",
        "hdr_results_download_evidence": "Evidenz herunterladen",
        "sub_results_download_evidence": "Stelle den abgeschlossenen Lauf, den aktiven Inspector-Bereich, die Stationsauswahl, Tabellen, Metadaten und hochauflösende Abbildungen als Reproduzierbarkeitspaket zusammen; Konfig speichern bewahrt die wiederverwendbaren Analyseeinstellungen separat.",
        "hdr_results_reusable_configuration": "Wiederverwendbare Konfiguration",
        "sub_documentation": "Methode, Interpretation, Bedienelemente, Grenzen und Fehlerbehebung.",
        "msg_preparing_all_results": "Hochaufloesendes Ergebnispaket wird vorbereitet...",
        "btn_prepare_documentation_pdf": "PDF vorbereiten",
        "btn_download_documentation_pdf": "PDF herunterladen",
        "btn_load_full_documentation": "Vollst\u00e4ndige Dokumentation laden",
        "btn_hide_full_documentation": "Vollst\u00e4ndige Dokumentation ausblenden",
        "msg_loading_analysis_engine": "Analyse-Engine wird vorbereitet...",
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
        "cbar_abs": "Mittlere Stations-Erfolgsrate (%)",
        "cbar_comp": "Median \u0394 normiertes SNR vs. Referenz (1S=6dB)",
        "comp_title_ref": "{callsign} (Referenz)",
        "comp_title_local_best": "Beste lokale Station (≤{radius} km)",
        "comp_title_local_median": "Lokaler Nachbarschafts-Median (≤{radius} km)",
        "config_title": "Konfiguration",
        "dev_credit": f"Release {APP_VERSION} | Repo: <a href='https://github.com/markusthemaker/WSPRadar/' target='_blank' style='color:#39ff14; text-decoration:none;'>GitHub</a> | License: <a href='https://github.com/markusthemaker/WSPRadar/blob/main/LICENSE' target='_blank' style='color:#39ff14; text-decoration:none;'>AGPLv3</a><br>Developed by Dr. Markus Brosch (DL1MKS) ",        
        "exp_adv": "⚙️ Filter, Analyseumfang und Evidenz",
        "exp_comp": "⚖️ Ergebnisansicht und Benchmark-Design",
        "exp_core": "📡 Target und Messzeitraum",
        "exp_metadata": "🏷️ Metadaten",
        "fig_rx_abs": "RX Success: Target {callsign} vs. Same Signals Heard Elsewhere",
        "fig_rx_comp": "RX Vergleich: {callsign} (Target) vs. {comp_title}",
        "fig_tx_abs": "TX Success: Target {callsign} vs. Other Signals at Active RX Stations",
        "abs_rx_counter": "Elsewhere",
        "abs_rx_counter_short": "E",
        "abs_rx_target_column": "Target (T)",
        "abs_rx_pair": "Target+Elsewhere",
        "abs_rx_formula": "Target/(Target+Elsewhere)",
        "abs_rx_formula_spaced": "Target / (Target + Elsewhere)",
        "abs_rx_rate_column": "T/(T+E) (%)",
        "abs_rx_counter_column": "Elsewhere (E)",
        "abs_rx_count_axis": "Target + Elsewhere count",
        "abs_rx_counter_marker": "E (Elsewhere)",
        "abs_rx_no_evidence": "Keine T/E-Evidenz",
        "abs_rx_empty_evidence": "Keine Target/Elsewhere-Evidenz",
        "abs_rx_subtext": " (T=Target | E=Elsewhere | Klick auf eine Zeile fuer Evidenz)",
        "abs_tx_counter": "Other Signals",
        "abs_tx_counter_short": "OS",
        "abs_tx_target_column": "Target (T)",
        "abs_tx_pair": "Target+Other Signals",
        "abs_tx_formula": "Target/(Target+Other Signals)",
        "abs_tx_formula_spaced": "Target / (Target + Other Signals)",
        "abs_tx_rate_column": "T/(T+OS) (%)",
        "abs_tx_counter_column": "Other Signals (OS)",
        "abs_tx_count_axis": "Target + Other Signals count",
        "abs_tx_counter_marker": "OS (Other Signals)",
        "abs_tx_no_evidence": "Keine T/OS-Evidenz",
        "abs_tx_empty_evidence": "Keine Target/Other-Signals-Evidenz",
        "abs_tx_subtext": " (T=Target | OS=Other Signals | Klick auf eine Zeile fuer Evidenz)",
        "fig_tx_comp": "TX Vergleich: {callsign} (Target) vs. {comp_title}",
        "hlp_max_dist": "Wissenschaftliche Maximalentfernung der kartierten Peers vom Target-QTH. Nur Peers mit einer strikt kleineren Entfernung bleiben in verarbeitetem Ergebnis, Karte, Inspector und Export; Provider-Abfrage und Rohabfrage-Cache bleiben global.",
        "hlp_min_spots": "Compare-Karten erfordern mindestens X gemeinsame Spots pro Station.",
        "hlp_min_opportunities": "Absolute Erfolgsraten beruecksichtigen eine Station erst nach dieser Anzahl Target+Gegen-Evidenz-Beobachtungen. Gegen-Evidenz ist Elsewhere fuer RX und Other Signals fuer TX. Target-only Beobachtungen gehoeren weder zu Target oder Gegen-Evidenz noch in den Nenner.",
        "hlp_min_stations": "Ein Kartensegment erfordert mindestens X qualifizierte Stationen. Compare nutzt die Joint-Evidenzschwelle; Absolute nutzt die modus-spezifische Target+Gegen-Evidenz-Schwelle.",
        "hlp_benchmark_offset_db": "Wird vor der Berechnung von \u0394 SNR zum Referenzseiten-SNR addiert. Gilt nur f\u00fcr Vergleichskarten. Buddy/lokale Benchmarks nutzen die Referenzseite; Hardware A/B nutzt die Referenzidentit\u00e4t oder den Referenz-Zeitplan. Wenn ein Kalibrierlauf Target-Referenz = +1,6 dB ergibt, verwende +1,6 dB.",
        "hlp_callsign_entry": "Verwende die exakt zu WSPR hochgeladene Kennung. Standardm\u00e4\u00dfige Rufzeichenformen werden empfohlen; zus\u00e4tzlich zu Schr\u00e4gstrichformen wie DL1MKS/P akzeptiert WSPRadar ein abschlie\u00dfendes alphanumerisches Suffix mit '-' wie DL1MKS-1. Jede Schreibweise ist eine eigene Identit\u00e4t.",
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
        "msg_select_analysis_direction_hardware": "Wähle RX- oder TX-Analyse, bevor du die richtungsspezifischen Hardware-A/B-Parameter konfigurierst.",
        "lbl_comp_mode": "Ergebnisansicht und Benchmark-Design",
        "lbl_drill_multi": "**Detaildaten: {count} Stationen ausgewählt** (Normiert @ 1W)",
        "lbl_drill_single": "**Detaildaten: {station}** (Normiert @ 1W)",
        "lbl_end_d": "Enddatum",
        "lbl_end_t": "Endzeit (UTC)",
        "lbl_hist_count": "Anzahl (Stationen)",
        "lbl_hist_x_abs": "{station_type} Median normiertes SNR (dB @ 1W)",
        "lbl_hist_x_comp": "{station_type} Median \u0394 normiertes SNR (dB)",
        "lbl_hours": "Letzte X Stunden",
        "lbl_insights": "Station Insights",
        "lbl_insights_sub": " (Normiert @ 1W | Klick auf eine Zeile für Detaildaten)",
        "lbl_show_zero_hits": "Zero-Target-Stationen zeigen",
        "lbl_max_dist": "Maximale Peer-Entfernung vom Target (km)",
        "lbl_med_seg": "Segment-Median: {med:.1f} dB",
        "lbl_med_stat": "Median: {med:.1f} dB",
        "lbl_min_spots": "Minimale Joint-Evidenz pro Station",
        "lbl_min_opportunities": "Minimale bestätigte Gelegenheiten pro Station",
        "lbl_min_stations": "Minimale qualifizierte Stationen pro Kartensegment",
        "lbl_no_joint": "Keine gemeinsamen Spots in diesem Segment für ein \u0394-SNR-Histogramm vorhanden.",
        "lbl_qth": "Target-QTH (4 oder 6 Zeichen)",
        "lbl_local_benchmark": "Lokale Benchmark-Methode",
        "lbl_radius": "Nächste Ref. Stationen (pro Zyklus)",
        "lbl_ref_radius_km": "Nachbarschaftsradius (km)",
        "lbl_ref_call": "Referenz-Rufzeichen",
        "lbl_target_callsign": "Target-Rufzeichen",
        "lbl_reference_callsign": "Referenz-Rufzeichen",
        "lbl_target_qth": "Target-QTH",
        "lbl_reference_qth": "Referenz-QTH",
        "lbl_target_grid4": "Target-Grid-4",
        "lbl_reference_grid4": "Referenz-Grid-4",
        "ph_reference_callsign": "z. B. DL1MKS/P oder DL1MKS-1",
        "ph_reference_qth": "z. B. JN37",
        "txt_target": "Target",
        "txt_reference": "Referenz",
        "lbl_solar": "Sonnenstand am Target-QTH",
        "lbl_start_d": "Startdatum",
        "lbl_start_t": "Startzeit (UTC)",
        "lbl_time_mode": "UTC-Messzeitraum",
        "txt_benchmark_offset_note": "Ref SNR Corr: {offset:+.1f} dB",
        "opt_comp_none": "Success — nur Target",
        "opt_comp_radius": "Compare — lokaler Nachbarschaftsvergleich",
        "opt_comp_buddy": "Compare — bekannte Referenzstation",
        "opt_comp_self": "Compare — Hardware A/B",
        "opt_local_best": "Beste lokale Station",
        "opt_local_median": "Lokaler Nachbarschafts-Median",
        "err_reference_callsign_same": "Target- und Referenz-Rufzeichen m\u00fcssen verschieden sein.",
        "err_reference_callsign_required": "Bitte ein Referenz-Rufzeichen konfigurieren.",
        "err_reference_qth_required": "Bitte ein Referenz-Grid-4 konfigurieren.",
        "err_callsign_format": "Bitte eine plausible Rufzeichen-/Meldekennung eingeben: 3-15 ASCII-Zeichen; '/' nur zwischen nicht leeren alphanumerischen Segmenten und h\u00f6chstens ein abschlie\u00dfendes '-' vor einem nicht leeren alphanumerischen Suffix verwenden. Mindestens ein Segment vor einem etwaigen Bindestrich muss sowohl einen Buchstaben als auch eine Ziffer enthalten.",
        "err_qth_format": "Bitte einen g\u00fcltigen 4- oder 6-stelligen Maidenhead-Locator eingeben (z. B. JN37 oder JN37AA).",
        "err_reference_callsign_format": "Bitte ein plausibles Referenz-Rufzeichen eingeben: 3-15 ASCII-Zeichen; '/' nur zwischen nicht leeren alphanumerischen Segmenten und h\u00f6chstens ein abschlie\u00dfendes '-' vor einem nicht leeren alphanumerischen Suffix verwenden. Mindestens ein Segment vor einem etwaigen Bindestrich muss sowohl einen Buchstaben als auch eine Ziffer enthalten.",
        "err_reference_qth_format": "Bitte f\u00fcr das Referenz-QTH einen g\u00fcltigen 4- oder 6-stelligen Maidenhead-Locator eingeben (z. B. JN37 oder JN37AA).",
        "err_reference_grid4_format": "Bitte ein genau 4-stelliges Maidenhead-Grid f\u00fcr die Referenz eingeben (z. B. JN37).",
        "err_reference_qth_match_target": "Im Hardware-A/B-Modus wird das Referenz-QTH aus dem Target-QTH abgeleitet.",
        "err_reference_qth_grid4": "Target- und Referenz-QTH m\u00fcssen im Hardware-A/B-Modus dasselbe Grid-4 haben.",
        "err_self_test": "Du hast dein eigenes Rufzeichen eingegeben. Bitte wähle den 'Hardware A/B-Test' Modus.",
        "err_loc_length": "Fehler: Beide Locators müssen für den RX A/B-Test exakt 6 Zeichen lang sein.",
        "err_loc_match": "Fehler: Die ersten 4 Zeichen beider Locators müssen identisch sein.",
        "err_loc_format": "Fehler: Ungültiges 6-stelliges Locator-Format (z.B. JN37AA).",
        "err_loc_identical": "Fehler: Locators müssen unterschiedlich sein (z.B. AA vs AB), um Joint-Spots zu generieren.",
        "err_loc_incomplete": "Fehler: Bitte ein gültiges 6-stelliges Locator-Setup abschließen, bevor die Analyse gestartet wird.",
        "lbl_qth_a": "Target Locator (Antenna A)",
        "lbl_qth_b": "Referenz Locator (Antenne B)",
        "leg_both_async": "Beide (Async)",
        "leg_abs_eligible": "Target/Gegen-Evidenz",
        "leg_abs_insufficient": "Unter Target+Gegen-Evidenz-Schwelle",
        "leg_abs_target_only": "Nur-Target-Evidenz",
        "leg_abs_hit": "T (Target)",
        "leg_abs_hit_one": "Target (T) = 1",
        "leg_abs_hit_mid": "Target (T) = 2-5",
        "leg_abs_hit_high": "Target (T) > 5",
        "leg_abs_miss": "E (Elsewhere)",
        "leg_abs_no_hm": "Keine T/E-Evidenz",
        "leg_joint": "Beide (Sync)",
        "leg_only_me": "Nur {callsign}",
        "leg_only_ref": "Nur {ref_callsign}",
        "leg_only_ref_radius": "Nur Referenz",
        "msg_proc": "Verarbeite {id}...",
        "msg_analysis_queue_wait": "Alle Analysekapazitaeten sind belegt; Ihre Analyse wartet auf Position {position}.",
        "msg_analysis_queue_detail": "Wartende Analysen: {queued}.",
        "msg_analysis_duplicate": "Diese identische Analyse ist fuer diese Sitzung bereits aktiv oder vorgemerkt.",
        "msg_analysis_submission_active": "Analyse uebermittelt; Analyse starten bleibt bis zum Abschluss deaktiviert.",
        "msg_config_loaded": "Konfiguration geladen. Bestehende Ergebnisse wurden geloescht.",
        "err_config_load": "Konfiguration konnte nicht geladen werden: {error}",
        "msg_sync": "Synchronisiere aktive WSPR-Zyklen...",
        "opt_all_dirs": "Alle Richtungen",
        "opt_custom": "Datum/Uhrzeit manuell",
        "opt_full_range": "Gesamter Bereich",
        "opt_insp_dir": "--- Segment-Inspektor (Richtung) ---",
        "opt_insp_dist": "--- Segment-Inspektor (Distanz) ---",
        "opt_last_x": "Letzte X Stunden",
        "opt_no_station": "Keine Stationen",
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
        "tbl_col_med_snr": "Median SNR (dB)",
        "tbl_col_only_ref": "Nur Referenz",
        "tbl_col_only_u": "Nur {callsign}",
        "tbl_col_cycle_ref_median": "Zyklus Ref-Median SNR (dB)",
        "tbl_col_delta_snr": "\u0394 SNR (dB)",
        "lbl_neighborhood": "Nachbarschaft",
        "tbl_col_ref_median_km": "Median Ref km",
        "tbl_col_ref_pool": "Referenz-Pool",
        "tbl_col_ref_snr": "Ref SNR (dB)",
        "tbl_col_ref_station": "Ref Station",
        "tbl_col_rx": "RX Station",
        "tbl_col_spots": "Spots",
        "tbl_col_opportunities": "Target+Gegen-Evidenz",
        "tbl_col_hits": "Target",
        "tbl_col_misses": "Counter-Evidence",
        "tbl_col_target_only": "Nur Target",
        "tbl_col_rate": "Success Rate (%)",
        "tbl_col_success_snr": "Median Target-SNR (dB @ 1W)",
        "tbl_col_eligible": "Qualifiziert",
        "txt_abs_evidence_summary": "Evidenz ({pair} >= {threshold} pro Station): Target {target} | {counter} {counter_count}",
        "txt_abs_rate_summary": "Erfolgsrate {formula}: Stationsmittel {station_average:.1f}% | Beobachtungsebene {overall:.1f}%",
        "txt_abs_no_eligible": "Keine Station erreicht in diesem Bereich die {pair}-Schwelle.",
        "tbl_col_tx": "TX Station",
        "lbl_exclude_special": "Spezial-Rufzeichen Q, 0, 1 ausschließen",
        "hdr_remote_station_filters": "Remote Stationsfilter",
        "hdr_analysis_scope": "Analyseumfang",
        "hdr_evidence_requirements": "Evidenzanforderungen",
        "tt_exclude_special": "Filtert Ballon-Telemetrie heraus.",
        "lbl_filter_moving": "Bewegliche Stationen filtern",
        "tt_filter_moving": "Filtert Ballons, Autos oder Schiffe heraus, die im Analysezeitraum ihren Grid-Locator wechseln.",
        "title": "WSPRadar.org",
        "txt_joint": "Synced",
        "txt_joint_decodes": "Synced Decodes",
        "txt_remote": "Total Remote",
        "txt_rx_stations": "RX Stationen",
        "txt_total_decodes": "Gesamte Decodes",
        "txt_tx_stations": "TX Stationen",
        "warn_analysis_queue_full": "Hohe Auslastung. Die Analysewarteschlange ist voll. Bitte versuchen Sie es in Kuerze erneut.",
        "warn_analysis_queue_timeout": "Es wurde nicht rechtzeitig Analysekapazitaet frei. Bitte starten Sie die Analyse erneut.",
        "warn_no_data": "Nicht genügend qualifizierte Daten für **{title}** nach Anwendung der Filter gefunden. Sind Rufzeichenangaben, Locator, Band, Datum und UTC-Zeit korrekt?"
    }
}


# Result guidance is shared by Guided and Classic because both input editors
# render the same completed-result hierarchy. Keep this content separate from
# ``GUIDED_INPUTS``: it explains how to read established result contracts and
# must never select scientific behavior.
RESULT_GUIDANCE = {
    "en": {
        "trigger": "How to read this",
        "trigger_help": "How to read {section}",
        "read_label": "What this view can establish and how to read it.",
        "limits_label": "Evidence boundary.",
        "sections": {
            "context_rx_success": {
                "read": (
                    "RX Success can establish how consistently the "
                    '<strong class="defined-term">Target</strong> receiver decoded '
                    "signals within independently confirmed opportunities for this "
                    "band, UTC window and geographic scope. The "
                    '<strong class="defined-term">Target-Active Gate</strong> first '
                    "retains only UTC cycles in which the archive shows the Target "
                    "receiver reporting at least one decode. Within those cycles, a "
                    '<strong class="defined-term">confirmed opportunity</strong> is '
                    "a remote TX-station cycle in which another receiver "
                    "independently decoded the same transmitter under the run's "
                    "eligibility rules. "
                    '<strong class="defined-term">Elsewhere</strong> means that the '
                    "other receiver decoded it but the Target did not; "
                    '<strong class="defined-term">Target-only</strong> means that '
                    "the Target decoded it without the independent confirmation "
                    "required by the denominator. Displayed "
                    '<strong class="defined-term">RX Success Rate</strong> (%) is '
                    "`100 × Target / (Target + Elsewhere)`."
                ),
                "limits": (
                    "This is a conditional reach measure within confirmed archive "
                    "evidence, not an absolute sensitivity measurement or an "
                    "explanation for individual missed decodes."
                ),
            },
            "context_tx_success": {
                "read": (
                    "TX Success can establish how consistently the "
                    '<strong class="defined-term">Target</strong> transmitter was '
                    "decoded by receivers that were independently shown to be "
                    "active for this band, UTC window and geographic scope. The "
                    '<strong class="defined-term">Target-Active Gate</strong> first '
                    "retains only UTC cycles in which at least one receiver "
                    "reported the Target transmission. Within those cycles, a "
                    '<strong class="defined-term">confirmed opportunity</strong> is '
                    "a remote RX-station cycle containing qualifying "
                    '<strong class="defined-term">Other Signals</strong> on the '
                    "same band. Other Signals means that the receiver decoded "
                    "another signal but not the Target; "
                    '<strong class="defined-term">Target-only</strong> means that '
                    "it decoded the Target without the independent activity "
                    "evidence required by the denominator. Displayed "
                    '<strong class="defined-term">TX Success Rate</strong> (%) is '
                    "`100 × Target / (Target + Other Signals)`."
                ),
                "limits": (
                    "This measures conditional reach across the retained active "
                    "receivers; it does not measure actual radiated power, antenna "
                    "efficiency or the cause of an individual missed decode."
                ),
            },
            "context_rx_compare": {
                "read": (
                    "RX Compare can establish the direction and magnitude of an "
                    "observed paired difference between the complete "
                    '<strong class="defined-term">Target</strong> and '
                    '<strong class="defined-term">Reference</strong> receiving '
                    "paths. <strong class=\"defined-term\">SNR</strong> is the "
                    "signal-to-noise ratio reported by the WSPR decoder in "
                    "decibels (dB); a less-negative value is stronger relative to "
                    "noise. <strong class=\"defined-term\">Delta SNR (ΔSNR)</strong> "
                    "is Target SNR minus corrected Reference SNR: positive values "
                    "favor the Target and negative values favor the Reference. RX "
                    "Compare forms a pair when both receivers report the same "
                    "remote transmitter in the same UTC cycle."
                ),
                "limits": (
                    "The result compares complete receiving paths; it isolates "
                    "antenna gain, receiver sensitivity or a cause only to the "
                    "extent that the experiment controlled the remaining path "
                    "differences."
                ),
            },
            "context_tx_compare": {
                "read": (
                    "TX Compare can establish the direction and magnitude of an "
                    "observed paired difference between the complete "
                    '<strong class="defined-term">Target</strong> and '
                    '<strong class="defined-term">Reference</strong> transmitting '
                    "paths at the same remote receivers. "
                    '<strong class="defined-term">SNR</strong> is the '
                    "signal-to-noise ratio reported by the WSPR decoder in "
                    "decibels (dB); a less-negative value is stronger relative to "
                    "noise. SNR is normalized to reported 1 W before "
                    '<strong class="defined-term">Delta SNR (ΔSNR)</strong> is '
                    "calculated as Target SNR minus corrected Reference SNR. "
                    "Positive values favor the Target and negative values favor the "
                    "Reference. Same-cycle TX Compare forms a pair when one "
                    "receiver reports both signals in the same UTC cycle."
                ),
                "limits": (
                    "The result compares complete transmitting paths; attribution "
                    "to power, antenna efficiency or individual hardware requires "
                    "those remaining variables to be independently controlled."
                ),
            },
            "context_tx_compare_scheduled": {
                "read": (
                    "Scheduled TX Compare can establish the direction, magnitude "
                    "and repeatability of an observed difference between the "
                    "scheduled <strong class=\"defined-term\">Target</strong> and "
                    '<strong class="defined-term">Reference</strong> transmitting '
                    "paths. <strong class=\"defined-term\">SNR</strong> is the "
                    "decoder-reported signal-to-noise ratio in decibels (dB), "
                    "normalized to reported 1 W. "
                    '<strong class="defined-term">Delta SNR (ΔSNR)</strong> is '
                    "Target SNR minus corrected Reference SNR: positive values "
                    "favor the Target and negative values favor the Reference. "
                    "WSPRadar forms each "
                    '<strong class="defined-term">Scheduled Pair</strong> from the '
                    "configured UTC schedule; its two transmissions are "
                    "time-separated rather than simultaneous."
                ),
                "limits": (
                    "The result retains schedule-timing, propagation, interference "
                    "and switching differences between the two transmissions, so a "
                    "recurring schedule-phase effect can resemble a path difference."
                ),
            },
            "benchmark_hardware": {
                "read": (
                    "The <strong class=\"defined-term\">Hardware A/B "
                    "benchmark</strong> is designed to compare two controlled paths "
                    "operating within the shared Grid-4. When the rest of the setup "
                    "is held constant, it supports attributing the observed "
                    "difference to the controlled path change."
                ),
                "limits": (
                    "It does not isolate one component or establish calibrated gain "
                    "unless the experimental controls support that narrower claim."
                ),
            },
            "benchmark_reference": {
                "read": (
                    "The <strong class=\"defined-term\">Reference Station "
                    "benchmark</strong> can establish how the Target's complete "
                    "installed station performed relative to the selected "
                    '<strong class="defined-term">Reference</strong> station. '
                    "WSPRadar selects that Reference by its exact callsign and "
                    "independently configured Reference Grid-4."
                ),
                "limits": (
                    "The comparison includes both stations' radios, antennas, "
                    "terrain, noise and locations; it does not isolate any one of "
                    "them."
                ),
            },
            "benchmark_local_median": {
                "read": (
                    "<strong class=\"defined-term\">Local Median "
                    "Neighborhood</strong> can establish how the Target compared "
                    "with the typical qualifying local station within {radius} km. "
                    "WSPRadar recalculates the Reference as the median of the active "
                    "local stations for each applicable path and cycle."
                ),
                "limits": (
                    "The Reference changes with local participation and depends on "
                    "the chosen radius; it is not one fixed or calibrated station."
                ),
            },
            "benchmark_local_best": {
                "read": (
                    "<strong class=\"defined-term\">Local Best Station</strong> can "
                    "establish how the Target compared with the strongest "
                    "qualifying local station available within {radius} km for each "
                    "applicable path and cycle."
                ),
                "limits": (
                    "This is a changing best-peer benchmark, not a local average, "
                    "fixed Reference station or calibrated performance ceiling."
                ),
            },
            "map_compare_rx": {
                "read": (
                    "Map View can establish where the observed Target–Reference "
                    "difference appeared and how widely the supporting evidence "
                    "was distributed. Each colored distance-and-direction sector "
                    "shows the median of its contributing stations' median "
                    '<strong class="defined-term">ΔSNR</strong> values. This is '
                    '<strong class="defined-term">station-balanced</strong>: every '
                    "qualifying station contributes one station-level value before "
                    "the sector is summarized. Markers and footer bars separate "
                    '<strong class="defined-term">Joint</strong>, '
                    '<strong class="defined-term">Both (Async)</strong>, '
                    '<strong class="defined-term">Only Target</strong> and '
                    '<strong class="defined-term">Only Reference</strong> evidence. '
                    "Joint means that a station has at least one usable pair; Both "
                    "(Async) means that both sides contributed for that station but "
                    "no usable pair was formed. "
                    '<strong class="defined-term">STATIONS</strong> shows '
                    "callsign-plus-locator participation, while "
                    '<strong class="defined-term">SPOTS</strong> shows processed '
                    "evidence volume. Read both: many spots can come from relatively "
                    "few stations."
                ),
                "limits": (
                    "The map does not identify propagation mode, radiation angle, "
                    "calibrated gain, causation or the missing SNR of an undecoded "
                    "side. S-unit labels are a display convention; use the "
                    "numerical dB values for magnitude."
                ),
            },
            "map_compare_tx": {
                "read": (
                    "Map View can establish where the observed Target–Reference "
                    "difference appeared and how widely the supporting evidence "
                    "was distributed. Each colored distance-and-direction sector "
                    "shows the median of its contributing stations' median "
                    '<strong class="defined-term">ΔSNR</strong> values. This is '
                    '<strong class="defined-term">station-balanced</strong>: every '
                    "qualifying station contributes one station-level value before "
                    "the sector is summarized. Markers and footer bars separate "
                    '<strong class="defined-term">Joint</strong>, '
                    '<strong class="defined-term">Both (Async)</strong>, '
                    '<strong class="defined-term">Only Target</strong> and '
                    '<strong class="defined-term">Only Reference</strong> evidence. '
                    "Joint means that a station has at least one usable pair; Both "
                    "(Async) means that both sides contributed for that station but "
                    "no usable pair was formed. "
                    '<strong class="defined-term">STATIONS</strong> shows '
                    "callsign-plus-locator participation, while "
                    '<strong class="defined-term">SPOTS</strong> or '
                    '<strong class="defined-term">PAIRS</strong> shows processed '
                    "evidence volume."
                ),
                "limits": (
                    "The map does not identify propagation mode, radiation angle, "
                    "actual radiated power, calibrated gain or causation. An "
                    "undecoded side has no SNR to normalize, so one-sided TX "
                    "outcomes are not power-normalized."
                ),
            },
            "map_success": {
                "read": (
                    "Map View can establish where station-balanced conditional "
                    '<strong class="defined-term">Success Rate</strong> was higher '
                    "or lower and how broadly the evidence was distributed. Each "
                    "sector first calculates one rate per qualifying {peer_type} "
                    "station, then gives every station one equal vote. This is the "
                    '<strong class="defined-term">station-balanced</strong> view. '
                    "Green markers identify stations with Target evidence; grey "
                    "markers identify qualifying "
                    '<strong class="defined-term">{counter}</strong>-only stations. '
                    '<strong class="defined-term">STATIONS</strong> shows '
                    "callsign-plus-locator participation, while "
                    '<strong class="defined-term">SPOTS</strong> shows processed '
                    "Target and {counter} evidence volume."
                ),
                "limits": (
                    "This is conditional reach within confirmed opportunities, not "
                    "unconditional coverage or calibrated decode probability. A "
                    "displayed 100% means success in every retained opportunity "
                    "represented there, not every possible transmission."
                ),
            },
            "segment": {
                "read": (
                    "Segment Inspector can establish whether the completed result "
                    "persists, changes or concentrates within a chosen geographic "
                    "subset. The distance and direction selectors define the "
                    '<strong class="defined-term">active scope</strong>, which '
                    "every following figure, station table and Selected Station "
                    "Evidence view inherits. "
                    '<strong class="defined-term">Evidence in scope</strong> reports '
                    "two complementary quantities: the contributing stations and "
                    "their qualifying Joint Spots, Scheduled Pairs or confirmed "
                    "opportunities. More stations show broader participation; more "
                    "evidence units show more repeated observations."
                ),
                "limits": (
                    "Changing the active scope does not rerun or widen the analysis, "
                    "and it cannot restore stations excluded by the run's "
                    "maximum-distance setting. Evidence counts alone do not "
                    "establish independence or experimental quality."
                ),
            },
            "comparison_evidence_joint": {
                "read": (
                    "Together, these figures can establish how broad the paired "
                    "result is, how consistently its direction appears across "
                    "stations and how much spot-level variation surrounds it. "
                    '<strong class="defined-term">Decode Outcomes</strong> counts '
                    "stations with <strong class=\"defined-term\">Joint</strong>, "
                    '<strong class="defined-term">Only Target</strong>, '
                    '<strong class="defined-term">Both (Async)</strong> or '
                    '<strong class="defined-term">Only Reference</strong> evidence. '
                    "A <strong class=\"defined-term\">Joint Spot</strong> is a "
                    "consolidated same-cycle unit containing comparable Target and "
                    "Reference evidence. **Station Medians (Δ SNR)** gives every "
                    "qualifying station one median ΔSNR and therefore one equal "
                    "vote. **Joint-Spot Δ SNR** gives every Joint Spot one value, "
                    "so "
                    "stations with more observations contribute more values. "
                    "Agreement between the two distributions supports a result "
                    "that is similar under station and spot weighting; a difference "
                    "shows where evidence volume changes the picture. The median "
                    "resists isolated extremes more than the arithmetic mean."
                ),
                "limits": (
                    "ΔSNR describes only the paired subset. Read it with Decode "
                    "Outcomes; these figures do not by themselves establish formal "
                    "significance, universality or physical cause."
                ),
            },
            "comparison_evidence_scheduled": {
                "read": (
                    "Together, these figures can establish how broad the scheduled "
                    "result is, how consistently its direction appears across RX "
                    "stations and how much pair-level variation surrounds it. "
                    '<strong class="defined-term">Decode Outcomes</strong> separates '
                    "complete Scheduled Pairs from one-sided and asynchronous "
                    "scheduled evidence. A "
                    '<strong class="defined-term">Scheduled Pair</strong> is the '
                    "deterministic Target–Reference unit formed from the configured "
                    "UTC schedule. **Station Medians (Δ SNR)** gives every "
                    "qualifying "
                    "RX station one median Pair ΔSNR and therefore one equal vote. "
                    "**Scheduled-Pair Δ SNR** gives every valid pair one value, so "
                    "stations with more pairs contribute more values. Agreement "
                    "between the two distributions supports a result that is "
                    "similar under station and pair weighting; a difference shows "
                    "where evidence volume changes the picture. The median resists "
                    "isolated extremes more than the arithmetic mean."
                ),
                "limits": (
                    "Pair ΔSNR excludes incomplete pairs, and the time-separated "
                    "design retains changes between transmissions. These figures "
                    "do not by themselves establish formal significance or "
                    "physical cause."
                ),
            },
            "temporal_evidence_joint": {
                "read": (
                    "Temporal Evidence can establish when the paired pattern "
                    "occurred during the run and whether a similar UTC-hour pattern "
                    "recurred across dates. Both panels use the same Joint Spots as "
                    "**Joint-Spot Δ SNR**; Station Insights selections do not "
                    "change "
                    "this segment-level view. "
                    '<strong class="defined-term">Chronological</strong> preserves '
                    "the actual UTC dates and times, revealing changes, gaps and "
                    "short-lived patterns. "
                    '<strong class="defined-term">UTC-Hour</strong> folds all '
                    "represented dates onto one 24-hour clock to reveal recurring "
                    "hour-of-day associations when at least two UTC dates "
                    "contribute. Color shows "
                    '<strong class="defined-term">relative density</strong> within '
                    "each panel: its densest cell is 100%, not 100% of all evidence. "
                    "Use the numerical dB labels and median traces because the ΔSNR "
                    "axis is visually expanded around its median."
                ),
                "limits": (
                    "These panels establish time patterns within the retained run, "
                    "not their cause. Because each panel is normalized separately, "
                    "its density colors are not absolute counts and cannot be "
                    "compared directly with the other panel."
                ),
            },
            "temporal_evidence_scheduled": {
                "read": (
                    "Temporal Evidence can establish when the scheduled-pair "
                    "pattern occurred and whether a similar UTC-hour pattern "
                    "recurred across dates. Both panels use the same Scheduled Pairs "
                    "as **Scheduled-Pair Δ SNR**; Station Insights selections do "
                    "not "
                    "change this segment-level view. "
                    '<strong class="defined-term">Chronological</strong> preserves '
                    "the actual UTC dates and planned pair times. "
                    '<strong class="defined-term">UTC-Hour</strong> folds all '
                    "represented dates onto one 24-hour clock. Color shows "
                    '<strong class="defined-term">relative density</strong> within '
                    "each panel rather than an absolute pair count. Use the "
                    "numerical dB labels and median traces because the ΔSNR axis is "
                    "visually expanded around its median."
                ),
                "limits": (
                    "These panels establish schedule-linked time patterns, not "
                    "whether hardware, propagation, interference or switching "
                    "caused them. Separately normalized density colors cannot be "
                    "compared as absolute evidence volume."
                ),
            },
            "success_evidence": {
                "read": (
                    "These figures can establish the "
                    '<strong class="defined-term">Success Rate</strong>, the '
                    "evidence depth behind it and whether high-volume stations "
                    "change the station-balanced picture. Displayed Success Rate "
                    "(%) is `100 × {formula}`. **Station Success Rate by Evidence "
                    "Count** places one station with at least one Target observation "
                    "at each point: height is its Success Rate, while horizontal "
                    "position is its qualifying evidence count on a base-2 "
                    "logarithmic scale. Points farther right have more repeated "
                    "evidence. Qualifying zero-Target stations are omitted from this "
                    "plot but remain available in Station Insights through "
                    "`Show Zero-Target`. **Average Station Success Rate** gives "
                    "every qualifying station one equal vote in each "
                    "time-and-distance cell. **Observation-Level Success Rate** "
                    "pools all Target and {counter} observations, so stations with "
                    "more evidence receive more weight. Agreement supports a result "
                    "that is similar under both weightings; divergence shows where "
                    "station mix or evidence volume matters. Empty cells mean no "
                    "qualifying evidence, not 0%."
                ),
                "limits": (
                    "Evidence count shows depth, not statistical confidence, and "
                    "these figures do not establish why rates differ."
                ),
            },
            "station_insights_compare_joint": {
                "read": (
                    "Station Insights can establish which {peer_type} stations "
                    "support the paired result, how their station-level results "
                    "differ and where evidence is concentrated. Each row is one "
                    "reported station, represented by its callsign plus locator. "
                    "Read <strong class=\"defined-term\">Joint Spots</strong>, "
                    "one-sided counts and station median "
                    '<strong class="defined-term">ΔSNR</strong> together. '
                    "`Include Unpaired Evidence` adds stations with one-sided or "
                    "asynchronous evidence but no usable paired ΔSNR. Select one or "
                    "more station rows to open their Selected Station Evidence. "
                    "Table filters change only the displayed rows and selection, "
                    "not the completed analysis."
                ),
                "limits": (
                    "A callsign-plus-locator row is not proof of one unique physical "
                    "station, and a row without paired evidence cannot establish a "
                    "Target–Reference strength difference."
                ),
            },
            "station_insights_compare_scheduled": {
                "read": (
                    "Station Insights can establish which RX stations support the "
                    "scheduled result, how their station-level results differ and "
                    "where evidence is concentrated. Each row is one reported RX "
                    "station, represented by its callsign plus locator. Read "
                    '<strong class="defined-term">Scheduled Pairs</strong>, '
                    "one-sided scheduled counts and station median "
                    '<strong class="defined-term">Pair ΔSNR</strong> together. '
                    "`Include Unpaired Evidence` adds stations without a complete "
                    "pair. Select one or more station rows to open their Selected "
                    "Station Evidence. Table filters change only the displayed rows "
                    "and selection, not the completed analysis."
                ),
                "limits": (
                    "A callsign-plus-locator row is not proof of one unique physical "
                    "station, and an incomplete pair cannot establish Pair ΔSNR."
                ),
            },
            "station_insights_success": {
                "read": (
                    "Station Insights can establish which {peer_type} stations "
                    "contribute to Success Rate, the evidence depth behind each "
                    "rate and how successful Target SNR differs among stations. "
                    "Each row is one reported station, represented by its callsign "
                    "plus locator. Read Target, "
                    '<strong class="defined-term">{counter}</strong>, '
                    '<strong class="defined-term">Success Rate</strong> and median '
                    "successful Target SNR together. `Show Zero-Target` adds "
                    "qualifying stations with no Target observation. "
                    '<strong class="defined-term">Normalized SNR at reported '
                    "1 W</strong> removes the reported transmit-power term from "
                    "successful Target decodes; a less-negative value is stronger "
                    "relative to noise. Success Rate itself is not power-normalized. "
                    "Select station rows to inspect their evidence. Table filters "
                    "change only the displayed rows and selection."
                ),
                "limits": (
                    "The table cannot show the SNR of a missed signal or correct "
                    "inaccurate reported power, and a station row does not prove a "
                    "unique physical station."
                ),
            },
            "selected_compare_joint": {
                "read": (
                    "Selected Station Evidence can establish how the paired "
                    "difference is distributed and changes over time for the "
                    "selected {peer_type} stations. The view "
                    '<strong class="defined-term">pools</strong> their Joint Spots, '
                    "meaning that it combines all selected observations; a station "
                    "with more Joint Spots contributes more values. **Δ SNR "
                    "Distribution** shows the paired center, spread and outliers. "
                    "Read bar length against `Share (%)` and compare the numerical "
                    "median and mean. **Chronological** places the same Joint Spots "
                    "in their actual UTC sequence. **UTC-Hour** folds the represented "
                    "dates by UTC hour to reveal recurring associations. Relative "
                    "density is normalized within the active time panel."
                ),
                "limits": (
                    "This is an observation-weighted view of the selected stations; "
                    "it does not replace the segment's station-balanced result or "
                    "establish the cause of a time pattern."
                ),
            },
            "selected_compare_scheduled": {
                "read": (
                    "Selected Station Evidence can establish how Pair ΔSNR is "
                    "distributed and changes over time for the selected RX "
                    "stations. The view "
                    '<strong class="defined-term">pools</strong> their Scheduled '
                    "Pairs, meaning that it combines all selected pairs; a station "
                    "with more valid pairs contributes more values. **Δ SNR "
                    "Distribution** shows the pair-level center, spread and "
                    "outliers. **Chronological** places the same pairs in their "
                    "planned UTC sequence. **UTC-Hour** folds the represented dates "
                    "by UTC hour to reveal recurring associations. Use the numerical "
                    "dB labels, median and mean; relative density is normalized "
                    "within the active time panel."
                ),
                "limits": (
                    "This is an observation-weighted view of the selected stations; "
                    "it does not replace the segment's station-balanced result or "
                    "separate a path difference from propagation, switching or "
                    "schedule-phase effects."
                ),
            },
            "selected_success": {
                "read": (
                    "Selected Station Evidence can establish when outcomes and "
                    "evidence volume changed for the selected {peer_type} stations "
                    "and how successful Target SNR was distributed. The view "
                    '<strong class="defined-term">pools</strong> the selected '
                    "stations' Target and "
                    '<strong class="defined-term">{counter}</strong> evidence, so a '
                    "station with more observations contributes more weight. "
                    "**Station Success Rate + Evidence over Time** combines the "
                    "Success Rate line with stacked Target and {counter} counts; "
                    "read the rate together with its evidence volume. The colors "
                    "classify the sampled great-circle path as night, "
                    "greyline/mixed or daylight, allowing time patterns to be "
                    "compared with path illumination. **Target SNR** contains only "
                    "successful Target decodes normalized to reported 1 W; a "
                    "less-negative value is stronger relative to noise."
                ),
                "limits": (
                    "The view can show an association with path illumination but "
                    "not that illumination caused the change. Target SNR cannot "
                    "reveal the strength of missed signals or measure actual "
                    "radiated power."
                ),
            },
            "drilldown_compare_joint": {
                "read": (
                    "Drill-Down Data provides the audit trail from the paired "
                    "result back to its contributing evidence. It shows "
                    '<strong class="defined-term">processed row-level '
                    "evidence</strong> after WSPRadar's matching and filters, "
                    "rather than untouched provider rows. Same-cycle Compare shows "
                    "the Target and Reference values used for each pair and its "
                    "ΔSNR. Use exact UTC times, stations and values to reconcile "
                    "summaries and inspect exceptional observations. Filters "
                    "change only the displayed table."
                ),
                "limits": (
                    "The rows establish how WSPRadar formed the displayed "
                    "summaries; they do not reconstruct a missing-side SNR or turn "
                    "one exceptional row into a general result."
                ),
            },
            "drilldown_compare_scheduled": {
                "read": (
                    "Drill-Down Data provides the audit trail from the scheduled "
                    "result back to its contributing pairs. It shows "
                    '<strong class="defined-term">processed scheduled '
                    "evidence</strong>, including the planned UTC pair, TX role, "
                    "Target and Reference micro-medians and Pair ΔSNR. Use it to "
                    "confirm that the displayed values follow the configured "
                    "schedule and reconcile with the summaries. Filters change "
                    "only the displayed table."
                ),
                "limits": (
                    "The rows establish how WSPRadar formed the displayed scheduled "
                    "evidence; they cannot show that propagation or interference "
                    "remained unchanged between transmissions."
                ),
            },
            "drilldown_success": {
                "read": (
                    "Drill-Down Data provides the audit trail from Success Rate "
                    "back to its contributing cycles. It shows "
                    '<strong class="defined-term">processed row-level '
                    "evidence</strong> after WSPRadar's eligibility rules and "
                    "filters, rather than untouched provider rows. Outcomes "
                    "identify Target, <strong class=\"defined-term\">{counter}"
                    "</strong> and <strong class=\"defined-term\">Target-only"
                    "</strong> evidence. Target-only remains auditable but does "
                    "not enter the Success Rate denominator. Use the table to "
                    "reconcile numerator and denominator with their contributing "
                    "cycles. Filters change only the displayed table."
                ),
                "limits": (
                    "The rows establish how the retained evidence formed the "
                    "displayed summaries; they cannot reveal unobserved "
                    "transmissions or explain why a decode failed."
                ),
            },
            "drilldown_local_median": {
                "read": (
                    "For Local Median Neighborhood, Drill-Down also identifies the "
                    "local Reference stations that contributed to each applicable "
                    "cycle median. This makes the changing neighborhood benchmark "
                    "directly auditable."
                ),
                "limits": (
                    "The contributing stations explain the dynamic Reference; they "
                    "do not turn it into one fixed or calibrated Reference station."
                ),
            },
            "download": {
                "read": (
                    "Download Evidence preserves the completed analysis in an "
                    '<strong class="defined-term">analysis evidence '
                    "package</strong> for audit, sharing and reproducibility. It "
                    "includes the run configuration and metadata, processed "
                    "evidence retained by the run's geographic scope, and the "
                    "applicable tables and high-resolution figures for the current "
                    "Inspector scope and selected stations. `Save Config` "
                    "separately preserves reusable analysis settings without the "
                    "evidence from this run."
                ),
                "limits": (
                    "The package reproduces WSPRadar's recorded analysis state, not "
                    "the physical experiment or untouched provider responses. A "
                    "later archive retrieval may differ if upstream records or "
                    "WSPRadar change."
                ),
            },
        },
    },
    "de": {
        "trigger": "So liest du das",
        "trigger_help": "So liest du „{section}“",
        "read_label": "Was dieser Bereich belegen kann und wie du ihn liest.",
        "limits_label": "Aussagegrenze.",
        "sections": {
            "context_rx_success": {
                "read": (
                    "RX Success kann belegen, wie zuverlässig der "
                    '<strong class="defined-term">Target</strong>-Empfänger '
                    "Signale innerhalb unabhängig bestätigter Gelegenheiten für "
                    "Band, UTC-Zeitfenster und geografischen Bereich dieses Laufs "
                    "decodierte. Das "
                    '<strong class="defined-term">Target-Active Gate</strong> '
                    "berücksichtigt zunächst nur UTC-Zyklen, in denen der "
                    "Target-Empfänger mindestens einen Decode gemeldet hat. Eine "
                    '<strong class="defined-term">bestätigte Gelegenheit</strong> '
                    "liegt innerhalb dieser Zyklen vor, wenn eine andere "
                    "qualifizierende Empfangsstation denselben entfernten Sender "
                    "decodiert und damit dessen Aktivität unabhängig bestätigt. "
                    '<strong class="defined-term">Elsewhere</strong> bedeutet: Die '
                    "andere Station decodierte den Sender, das Target nicht. "
                    '<strong class="defined-term">Target-only</strong> bedeutet: '
                    "Das Target decodierte ihn, aber die unabhängige Bestätigung "
                    "für den Nenner fehlt. Die angezeigte RX Success Rate (%) ist "
                    "`100 × Target / (Target + Elsewhere)`."
                ),
                "limits": (
                    "Das ist bedingte Reichweite innerhalb bestätigter "
                    "Archivevidenz, keine absolute Empfindlichkeitsmessung oder "
                    "Erklärung einzelner fehlender Decodes."
                ),
            },
            "context_tx_success": {
                "read": (
                    "TX Success kann belegen, wie zuverlässig der "
                    '<strong class="defined-term">Target</strong>-Sender von '
                    "Empfangsstationen decodiert wurde, die für Band, "
                    "UTC-Zeitfenster und geografischen Bereich dieses Laufs "
                    "unabhängig als aktiv bestätigt sind. Das "
                    '<strong class="defined-term">Target-Active Gate</strong> '
                    "berücksichtigt zunächst nur UTC-Zyklen, in denen mindestens "
                    "eine Empfangsstation die Target-Aussendung gemeldet hat. Eine "
                    '<strong class="defined-term">bestätigte Gelegenheit</strong> '
                    "liegt innerhalb dieser Zyklen vor, wenn eine entfernte "
                    "Empfangsstation durch qualifizierende "
                    '<strong class="defined-term">Other Signals</strong> im selben '
                    "Band nachweislich aktiv war. "
                    '<strong class="defined-term">Target-only</strong> bedeutet: '
                    "Die Station decodierte das Target, aber die unabhängige "
                    "Aktivitätsbestätigung für den Nenner fehlt. Die angezeigte TX "
                    "Success Rate (%) ist "
                    "`100 × Target / (Target + Other Signals)`."
                ),
                "limits": (
                    "Das misst bedingte Reichweite unter den bestätigten aktiven "
                    "Empfangsstationen, nicht tatsächlich abgestrahlte Leistung, "
                    "Antennenwirkungsgrad oder die Ursache einzelner fehlender "
                    "Decodes."
                ),
            },
            "context_rx_compare": {
                "read": (
                    "RX Compare kann Richtung und Größe eines beobachteten "
                    "gepaarten Unterschieds zwischen dem vollständigen "
                    '<strong class="defined-term">Target</strong>- und '
                    '<strong class="defined-term">Referenz</strong>-Empfangspfad '
                    "belegen. <strong class=\"defined-term\">SNR</strong> ist das "
                    "vom WSPR-Decoder gemeldete Signal-Rausch-Verhältnis in "
                    "Dezibel (dB); ein weniger negativer Wert ist relativ zum "
                    "Rauschen stärker. "
                    '<strong class="defined-term">Delta SNR (ΔSNR)</strong> ist '
                    "Target-SNR minus korrigiertes Referenz-SNR: Positive Werte "
                    "sprechen für das Target, negative für die Referenz. RX "
                    "Compare paart Reports desselben entfernten Senders im selben "
                    "UTC-Zyklus."
                ),
                "limits": (
                    "Das Ergebnis vergleicht vollständige Empfangspfade; "
                    "Antennengewinn, Empfängerempfindlichkeit oder eine Ursache "
                    "isoliert es nur, soweit der Versuch die übrigen "
                    "Pfadunterschiede kontrollierte."
                ),
            },
            "context_tx_compare": {
                "read": (
                    "TX Compare kann Richtung und Größe eines beobachteten "
                    "gepaarten Unterschieds zwischen dem vollständigen "
                    '<strong class="defined-term">Target</strong>- und '
                    '<strong class="defined-term">Referenz</strong>-Sendepfad an '
                    "denselben entfernten Empfangsstationen belegen. "
                    '<strong class="defined-term">SNR</strong> ist das vom '
                    "WSPR-Decoder gemeldete Signal-Rausch-Verhältnis in Dezibel "
                    "(dB); ein weniger negativer Wert ist relativ zum Rauschen "
                    "stärker. SNR wird zunächst auf die gemeldete Leistung von 1 W "
                    "normiert. "
                    '<strong class="defined-term">Delta SNR (ΔSNR)</strong> ist '
                    "Target-SNR minus korrigiertes Referenz-SNR: Positive Werte "
                    "sprechen für das Target, negative für die Referenz. "
                    "Same-cycle TX Compare paart beide Signale an derselben "
                    "Empfangsstation im selben UTC-Zyklus."
                ),
                "limits": (
                    "Das Ergebnis vergleicht vollständige Sendepfade; Leistung, "
                    "Antennenwirkungsgrad oder einzelne Hardware isoliert es nur "
                    "bei entsprechender Kontrolle der übrigen Variablen."
                ),
            },
            "context_tx_compare_scheduled": {
                "read": (
                    "Scheduled TX Compare kann Richtung, Größe und Wiederholbarkeit "
                    "eines beobachteten Unterschieds zwischen den geplanten "
                    '<strong class="defined-term">Target</strong>- und '
                    '<strong class="defined-term">Referenz</strong>-Sendepfaden '
                    "belegen. <strong class=\"defined-term\">SNR</strong> ist das "
                    "vom WSPR-Decoder gemeldete Signal-Rausch-Verhältnis in "
                    "Dezibel (dB), normiert auf die gemeldete Leistung von 1 W. "
                    '<strong class="defined-term">Delta SNR (ΔSNR)</strong> ist '
                    "Target-SNR minus korrigiertes Referenz-SNR: Positive Werte "
                    "sprechen für das Target, negative für die Referenz. WSPRadar "
                    "bildet aus dem konfigurierten UTC-Zeitplan deterministische "
                    '<strong class="defined-term">geplante Paare</strong>. Die '
                    "beiden Aussendungen eines Paars sind zeitlich getrennt."
                ),
                "limits": (
                    "Zeitplan, Ausbreitung, Störungen und Umschaltung können sich "
                    "zwischen beiden Aussendungen ändern; ein wiederkehrender "
                    "Zeitplaneffekt kann daher wie ein Pfadunterschied aussehen."
                ),
            },
            "benchmark_hardware": {
                "read": (
                    "Der <strong class=\"defined-term\">Hardware-A/B-"
                    "Benchmark</strong> vergleicht zwei kontrollierte Pfade im "
                    "gemeinsamen Grid-4. Bleibt der übrige Aufbau konstant, "
                    "unterstützt er die Zuordnung des beobachteten Unterschieds "
                    "zur kontrollierten Pfadänderung."
                ),
                "limits": (
                    "Eine einzelne Komponente oder kalibrierten Antennengewinn "
                    "isoliert er nur mit entsprechend engeren Versuchskontrollen."
                ),
            },
            "benchmark_reference": {
                "read": (
                    "Der <strong class=\"defined-term\">Referenzstations-"
                    "Benchmark</strong> kann belegen, wie die vollständig "
                    "installierte Target-Station relativ zur ausgewählten "
                    '<strong class="defined-term">Referenz</strong> abschnitt. '
                    "WSPRadar wählt die Referenz über ihr exaktes Rufzeichen und "
                    "das unabhängig konfigurierte Referenz-Grid-4."
                ),
                "limits": (
                    "Der Vergleich umfasst Funkgeräte, Antennen, Gelände, lokales "
                    "Rauschen und Standorte beider Stationen; keinen dieser "
                    "Einflüsse isoliert er für sich."
                ),
            },
            "benchmark_local_median": {
                "read": (
                    "<strong class=\"defined-term\">Lokaler "
                    "Nachbarschaftsmedian</strong> kann belegen, wie das Target "
                    "gegenüber der typischen qualifizierenden lokalen Station "
                    "innerhalb von {radius} km abschnitt. WSPRadar berechnet die "
                    "Referenz für jeden anwendbaren Pfad und Zyklus neu als Median "
                    "der aktiven lokalen Stationen."
                ),
                "limits": (
                    "Die Referenz ändert sich mit der lokalen Beteiligung und hängt "
                    "vom Radius ab; sie ist keine feste oder kalibrierte Station."
                ),
            },
            "benchmark_local_best": {
                "read": (
                    "<strong class=\"defined-term\">Beste lokale "
                    "Station</strong> kann belegen, wie das Target gegenüber der "
                    "stärksten verfügbaren qualifizierenden Station innerhalb von "
                    "{radius} km für jeden anwendbaren Pfad und Zyklus abschnitt."
                ),
                "limits": (
                    "Das ist ein wechselnder Best-Peer-Benchmark, kein lokaler "
                    "Durchschnitt, keine feste Referenzstation und keine "
                    "kalibrierte Leistungsgrenze."
                ),
            },
            "map_compare_rx": {
                "read": (
                    "Die Kartenansicht kann belegen, wo der beobachtete "
                    "Target–Referenz-Unterschied auftrat und wie breit die "
                    "stützende Evidenz verteilt war. Jedes farbige Entfernungs- "
                    "und Richtungssegment zeigt den Median der Stationsmediane des "
                    '<strong class="defined-term">ΔSNR</strong>. '
                    '<strong class="defined-term">Stationsgleichgewichtet</strong> '
                    "bedeutet: Jede qualifizierende Station zählt einmal, "
                    "unabhängig von ihrer Spot-Anzahl. Marker und Fußbalken "
                    "unterscheiden <strong class=\"defined-term\">Joint</strong>, "
                    '<strong class="defined-term">Both (Async)</strong>, '
                    '<strong class="defined-term">Only Target</strong> und '
                    '<strong class="defined-term">Only Reference</strong>. Joint '
                    "bedeutet mindestens ein nutzbares Paar; Both (Async) bedeutet "
                    "Evidenz auf beiden Seiten, aber kein nutzbares Paar. "
                    "`STATIONS` zeigt die geografische Breite der beitragenden "
                    "Stationen, `SPOTS` den Umfang wiederholter Evidenz. Lies "
                    "beides zusammen: Viele Spots können von relativ wenigen "
                    "Stationen stammen."
                ),
                "limits": (
                    "Die Karte leitet die Ursache des Musters nicht her und kennt "
                    "kein SNR für eine nicht decodierte Seite; für die Größe des "
                    "Unterschieds sind die numerischen dB-Werte maßgeblich."
                ),
            },
            "map_compare_tx": {
                "read": (
                    "Die Kartenansicht kann belegen, wo der beobachtete "
                    "Target–Referenz-Unterschied auftrat und wie breit die "
                    "stützende Evidenz verteilt war. Jedes farbige Entfernungs- "
                    "und Richtungssegment zeigt den Median der Stationsmediane des "
                    '<strong class="defined-term">ΔSNR</strong>. '
                    '<strong class="defined-term">Stationsgleichgewichtet</strong> '
                    "bedeutet: Jede qualifizierende Empfangsstation zählt einmal, "
                    "unabhängig von ihrem Evidenzumfang. Marker und Fußbalken "
                    "unterscheiden <strong class=\"defined-term\">Joint</strong>, "
                    '<strong class="defined-term">Both (Async)</strong>, '
                    '<strong class="defined-term">Only Target</strong> und '
                    '<strong class="defined-term">Only Reference</strong>. Joint '
                    "bedeutet mindestens ein nutzbares Paar; Both (Async) bedeutet "
                    "Evidenz auf beiden Seiten, aber kein nutzbares Paar. "
                    "`STATIONS` zeigt die geografische Breite der beitragenden "
                    "Empfangsstationen, `SPOTS` beziehungsweise `PAIRS` den Umfang "
                    "wiederholter Evidenz."
                ),
                "limits": (
                    "Die Karte leitet weder Ursache noch tatsächlich abgestrahlte "
                    "Leistung her; eine nicht decodierte Seite besitzt kein "
                    "normierbares SNR."
                ),
            },
            "map_success": {
                "read": (
                    "Die Kartenansicht kann belegen, wo die bedingte "
                    '<strong class="defined-term">Success Rate</strong> innerhalb '
                    "dieses Laufs höher oder niedriger war und wie breit die "
                    "Evidenz verteilt ist. Jedes Segment berechnet zunächst eine "
                    "Rate je qualifizierender {peer_type}-Station und gewichtet "
                    "anschließend jede Station gleich; dies ist die "
                    '<strong class="defined-term">stationsgleichgewichtete</strong> '
                    "Ansicht. Grüne Marker zeigen Stationen mit Target-Evidenz, "
                    "graue Marker Stationen mit ausschließlich "
                    '<strong class="defined-term">{counter}</strong>-Evidenz. '
                    "`STATIONS` zeigt die geografische Breite, `SPOTS` den Umfang "
                    "der Target- und {counter}-Evidenz."
                ),
                "limits": (
                    "Das ist bedingte Reichweite, keine unbedingte Abdeckung oder "
                    "kalibrierte Empfangswahrscheinlichkeit; 100 % gelten nur für "
                    "die dargestellten bestätigten Gelegenheiten."
                ),
            },
            "segment": {
                "read": (
                    "Der Segment-Inspektor kann belegen, ob das abgeschlossene "
                    "Ergebnis "
                    "in einem gewählten geografischen Teilbereich bestehen bleibt, "
                    "sich ändert oder konzentriert. Die Auswahl von Entfernung und "
                    "Richtung definiert den "
                    '<strong class="defined-term">aktiven Bereich</strong>. Alle '
                    "folgenden Abbildungen, Stationstabellen und Ansichten "
                    "ausgewählter Stationen beziehen sich auf diesen Ausschnitt. "
                    '<strong class="defined-term">Evidenz im aktiven '
                    "Bereich</strong> zeigt zwei ergänzende Größen: die "
                    "qualifizierenden beitragenden Stationen und die zugehörigen "
                    "Joint Spots, geplanten Paare oder bestätigten Gelegenheiten. "
                    "Mehr Stationen zeigen größere Breite; mehr Evidenzeinheiten "
                    "zeigen mehr wiederholte Beobachtungen."
                ),
                "limits": (
                    "Die Auswahl startet keine neue Analyse und kann Stationen "
                    "außerhalb des ursprünglichen Laufs nicht zurückholen; die "
                    "Anzahlen allein belegen keine Unabhängigkeit oder "
                    "Versuchsqualität."
                ),
            },
            "comparison_evidence_joint": {
                "read": (
                    "Zusammen können diese Abbildungen belegen, wie breit der "
                    "gepaarte Unterschied über Stationen auftritt und wie viel "
                    "Variation die einzelnen Spots zeigen. **Decode Outcomes** "
                    "zählt Stationen mit "
                    '<strong class="defined-term">Joint</strong>, '
                    '<strong class="defined-term">Only Target</strong>, '
                    '<strong class="defined-term">Both (Async)</strong> oder '
                    '<strong class="defined-term">Only Reference</strong>. Ein '
                    '<strong class="defined-term">Joint Spot</strong> ist eine '
                    "zusammengeführte Beobachtung desselben UTC-Zyklus mit "
                    "vergleichbarer Evidenz für Target und Referenz. **Station "
                    "Medians (Δ SNR)** gibt jeder qualifizierenden Station genau "
                    "einen Median und damit dasselbe Gewicht. **Joint-Spot Δ SNR** "
                    "gibt jedem Joint Spot einen Wert; Stationen mit vielen Spots "
                    "wirken hier stärker. Stimmen beide Verteilungen überein, ist "
                    "das Ergebnis unter Stations- und Spot-Gewichtung ähnlich; "
                    "eine Abweichung zeigt, wo Evidenzumfang das Bild verändert. "
                    "Der Median reagiert weniger auf einzelne Extremwerte als das "
                    "arithmetische Mittel."
                ),
                "limits": (
                    "ΔSNR beschreibt nur die gepaarte Teilmenge; lies es zusammen "
                    "mit Decode Outcomes. Die Abbildungen belegen für sich weder "
                    "formale Signifikanz noch die physische Ursache."
                ),
            },
            "comparison_evidence_scheduled": {
                "read": (
                    "Zusammen können diese Abbildungen belegen, wie breit der "
                    "geplante Unterschied über RX-Stationen auftritt und wie viel "
                    "Variation die einzelnen Paare zeigen. **Decode Outcomes** "
                    "trennt vollständige geplante Paare von einseitiger und "
                    "asynchroner Evidenz. Ein "
                    '<strong class="defined-term">geplantes Paar</strong> ist die '
                    "deterministische Target–Referenz-Einheit aus dem "
                    "konfigurierten UTC-Zeitplan. **Station Medians (Δ SNR)** gibt "
                    "jeder qualifizierenden RX-Station genau einen medianen "
                    "Paar-ΔSNR und damit dasselbe Gewicht. **Geplantes Paar Δ SNR** "
                    "gibt jedem gültigen Paar einen Wert; Stationen mit vielen "
                    "Paaren wirken hier stärker. Stimmen beide Verteilungen "
                    "überein, ist das Ergebnis unter Stations- und Paar-Gewichtung "
                    "ähnlich; eine Abweichung zeigt, wo Evidenzumfang das Bild "
                    "verändert. Der Median reagiert weniger auf einzelne "
                    "Extremwerte als das arithmetische Mittel."
                ),
                "limits": (
                    "Paar-ΔSNR schließt unvollständige Paare aus, und zeitliche "
                    "Änderungen zwischen den Aussendungen bleiben erhalten. Die "
                    "Abbildungen belegen für sich weder formale Signifikanz noch "
                    "die physische Ursache."
                ),
            },
            "temporal_evidence_joint": {
                "read": (
                    "Der Bereich Zeitliche Evidenz kann belegen, wann das gepaarte "
                    "Muster im "
                    "Lauf auftrat und ob sich ein ähnliches Muster nach UTC-Stunde "
                    "über mehrere Tage wiederholte. Beide Panels verwenden "
                    "dieselben Joint Spots wie **Joint-Spot Δ SNR**; die Auswahl "
                    "in "
                    "Station Insights verändert diese Segmentansicht nicht. "
                    "**Chronologisch** behält tatsächliche UTC-Daten und -Zeiten "
                    "bei und zeigt Änderungen, Lücken und kurzzeitige Muster. "
                    "**UTC-Stunde** legt alle dargestellten Tage auf eine gemeinsame "
                    "24-Stunden-Uhr. Die Farbe zeigt die "
                    '<strong class="defined-term">relative Dichte</strong> '
                    "innerhalb des jeweiligen Panels: Die dichteste Zelle "
                    "entspricht 100 %, nicht 100 % der gesamten Evidenz. Nutze für "
                    "die Größe des Unterschieds die dB-Werte und Medianlinien."
                ),
                "limits": (
                    "Die Panels belegen Zeitmuster innerhalb der beibehaltenen "
                    "Evidenz, nicht deren Ursache; die separat normierten "
                    "Dichtefarben sind keine absoluten, direkt vergleichbaren "
                    "Anzahlen."
                ),
            },
            "temporal_evidence_scheduled": {
                "read": (
                    "Der Bereich Zeitliche Evidenz kann belegen, wann das geplante "
                    "Paarmuster "
                    "auftrat und ob sich ein ähnliches Muster nach UTC-Stunde über "
                    "mehrere Tage wiederholte. Beide Panels verwenden dieselben "
                    "geplanten Paare wie **Geplantes Paar Δ SNR**; die Auswahl in "
                    "Station Insights verändert diese Segmentansicht nicht. "
                    "**Chronologisch** behält tatsächliche UTC-Daten und geplante "
                    "Paarzeiten bei. **UTC-Stunde** legt alle dargestellten Tage auf "
                    "eine gemeinsame 24-Stunden-Uhr. Die Farbe zeigt die "
                    '<strong class="defined-term">relative Dichte</strong> '
                    "innerhalb des jeweiligen Panels, keine absolute Paaranzahl. "
                    "Nutze für die Größe des Unterschieds die dB-Werte und "
                    "Medianlinien."
                ),
                "limits": (
                    "Die Panels belegen zeitplanbezogene Zeitmuster, trennen aber "
                    "Hardware, Ausbreitung, Störungen und Umschaltung als Ursachen "
                    "nicht; die Dichtefarben sind keine absoluten Anzahlen."
                ),
            },
            "success_evidence": {
                "read": (
                    "Diese Abbildungen können Success Rate, Evidenztiefe und den "
                    "Einfluss evidenzstarker Stationen auf das "
                    "stationsgleichgewichtete Bild belegen. Die angezeigte "
                    '<strong class="defined-term">Success Rate</strong> (%) ist '
                    "`100 × {formula}`. "
                    "**Station Success Rate by Evidence Count** zeigt jede "
                    "Station mit mindestens einem Target-Decode als Punkt: "
                    "Die Höhe ist ihre Rate, die horizontale Position ihre "
                    "qualifizierende Evidenzanzahl auf einer logarithmischen "
                    "Basis-2-Skala. Punkte weiter rechts besitzen mehr wiederholte "
                    "Evidenz. Qualifizierende Stationen ohne Target-Decode fehlen "
                    "hier, können aber in Station Insights mit "
                    "`Zero-Target-Stationen zeigen` eingeblendet werden. "
                    "**Average Station Success Rate** gibt jeder "
                    "qualifizierenden Station in jeder Zeit- und Entfernungszelle "
                    "eine gleich große Stimme. "
                    "**Observation-Level Success Rate** fasst alle "
                    "qualifizierenden Target- und {counter}-Beobachtungen zusammen; "
                    "Stationen mit viel Evidenz erhalten dadurch mehr Gewicht. "
                    "Übereinstimmung stützt ein unter beiden Gewichtungen ähnliches "
                    "Ergebnis; Abweichung zeigt, wo Stationsmix oder Evidenzumfang "
                    "zählt. Leere Zellen bedeuten fehlende qualifizierende Evidenz, "
                    "nicht 0 %."
                ),
                "limits": (
                    "Evidenzanzahl zeigt Tiefe, nicht statistische Sicherheit; die "
                    "Abbildungen erklären nicht, warum Raten abweichen."
                ),
            },
            "station_insights_compare_joint": {
                "read": (
                    "Station Insights kann belegen, welche {peer_type}-Stationen "
                    "das gepaarte Ergebnis stützen, wie sich ihre "
                    "Stationsergebnisse unterscheiden und wo Evidenz konzentriert "
                    "ist. In dieser Tabelle bezeichnet eine Station die gemeldete "
                    "Kombination aus Rufzeichen und Locator. Lies "
                    '<strong class="defined-term">Joint Spots</strong>, '
                    "einseitige Anzahlen und das mediane Stations-"
                    '<strong class="defined-term">ΔSNR</strong> zusammen. '
                    "`Ungepaarte Evidenz einbeziehen` zeigt zusätzlich Stationen "
                    "mit einseitiger oder asynchroner Evidenz ohne nutzbares "
                    "gepaartes ΔSNR. Wähle eine oder mehrere Stationen, um ihre "
                    "Evidenz ausgewählter Stationen zu öffnen. Tabellenfilter "
                    "verändern "
                    "nur Anzeige und Auswahl, nicht die abgeschlossene Analyse."
                ),
                "limits": (
                    "Eine Rufzeichen-plus-Locator-Zeile belegt keine eindeutig "
                    "einzelne physische Station; ohne gepaarte Evidenz lässt sich "
                    "kein Target–Referenz-Stärkeunterschied bestimmen."
                ),
            },
            "station_insights_compare_scheduled": {
                "read": (
                    "Station Insights kann belegen, welche RX-Stationen das "
                    "geplante Ergebnis stützen, wie sich ihre Stationsergebnisse "
                    "unterscheiden und wo Evidenz konzentriert ist. In dieser "
                    "Tabelle bezeichnet eine Station die gemeldete Kombination "
                    "aus Rufzeichen und Locator. Lies "
                    '<strong class="defined-term">geplante Paare</strong>, '
                    "einseitige Anzahlen und das mediane "
                    '<strong class="defined-term">Paar-ΔSNR</strong> zusammen. '
                    "`Ungepaarte Evidenz einbeziehen` zeigt zusätzlich Stationen "
                    "ohne vollständiges Paar. Wähle eine oder mehrere Stationen, "
                    "um ihre Evidenz ausgewählter Stationen zu öffnen. Tabellenfilter "
                    "verändern nur Anzeige und Auswahl, nicht die abgeschlossene "
                    "Analyse."
                ),
                "limits": (
                    "Eine Rufzeichen-plus-Locator-Zeile belegt keine eindeutig "
                    "einzelne physische Station; ohne vollständiges Paar lässt sich "
                    "kein Paar-ΔSNR bestimmen."
                ),
            },
            "station_insights_success": {
                "read": (
                    "Station Insights kann belegen, welche {peer_type}-Stationen "
                    "zur Success Rate beitragen, welche Evidenztiefe hinter jeder "
                    "Rate steht und wie sich erfolgreiches Target-SNR zwischen "
                    "Stationen unterscheidet. In dieser Tabelle bezeichnet eine "
                    "Station die gemeldete Kombination aus Rufzeichen und Locator. "
                    "Lies Target, <strong class=\"defined-term\">{counter}</strong>, "
                    '<strong class="defined-term">Success Rate</strong> und den '
                    "Median des SNR erfolgreicher Target-Decodes zusammen. "
                    "`Zero-Target-Stationen zeigen` blendet qualifizierende "
                    "Stationen ohne Target-Decode ein. "
                    '<strong class="defined-term">Auf die gemeldete Leistung von '
                    "1 W normiertes SNR</strong> entfernt den gemeldeten "
                    "Sendeleistungsterm aus erfolgreichen Target-Decodes; ein "
                    "weniger negativer Wert ist relativ zum Rauschen stärker. Die "
                    "Success Rate selbst wird nicht leistungsnormiert. Wähle "
                    "Stationen aus, um ihre Evidenz zu untersuchen; Tabellenfilter "
                    "verändern nur Anzeige und Auswahl."
                ),
                "limits": (
                    "Das SNR eines nicht decodierten Signals bleibt unbekannt, und "
                    "eine Stationszeile kann weder ungenaue Leistungsangaben "
                    "korrigieren noch eine eindeutig einzelne physische Station "
                    "belegen."
                ),
            },
            "selected_compare_joint": {
                "read": (
                    "Die Evidenz ausgewählter Stationen kann belegen, wie sich der "
                    "gepaarte "
                    "Unterschied für die "
                    '<strong class="defined-term">ausgewählten {peer_type}-'
                    "Stationen</strong> verteilt und über die Zeit verändert. Die "
                    "Ansicht <strong class=\"defined-term\">poolt</strong> ihre "
                    "Joint Spots, kombiniert also alle ausgewählten Beobachtungen; "
                    "eine Station mit mehr Joint Spots trägt mehr Werte bei. "
                    "**Δ SNR Verteilung** zeigt Zentrum, Streuung und Ausreißer "
                    "der Paare. Lies die Balkenlänge an `Share (%)` ab und "
                    "vergleiche numerischen Median und Mittelwert. "
                    "**Chronologisch** ordnet dieselben Joint Spots in ihrer "
                    "tatsächlichen UTC-Folge an. **UTC-Stunde** legt die dargestellten "
                    "Tage auf eine gemeinsame 24-Stunden-Uhr und macht "
                    "wiederkehrende Zuordnungen sichtbar. Die relative Dichte wird "
                    "innerhalb des aktiven Zeitpanels normiert."
                ),
                "limits": (
                    "Das ist eine beobachtungsgewichtete Ansicht der ausgewählten "
                    "Stationen; sie ersetzt nicht das stationsgleichgewichtete "
                    "Segmentergebnis und belegt nicht die Ursache eines Zeitmusters."
                ),
            },
            "selected_compare_scheduled": {
                "read": (
                    "Die Evidenz ausgewählter Stationen kann belegen, wie sich "
                    "Paar-ΔSNR "
                    "für die <strong class=\"defined-term\">ausgewählten "
                    "RX-Stationen</strong> verteilt und über die Zeit verändert. "
                    "Die Ansicht <strong class=\"defined-term\">poolt</strong> ihre "
                    "geplanten Paare, kombiniert also alle ausgewählten Paare; "
                    "eine Station mit mehr gültigen Paaren trägt mehr Werte bei. "
                    "**Δ SNR Verteilung** zeigt Zentrum, Streuung und Ausreißer "
                    "der Paare. **Chronologisch** ordnet dieselben Paare in ihrer "
                    "geplanten UTC-Folge an. **UTC-Stunde** legt die dargestellten "
                    "Tage auf eine gemeinsame 24-Stunden-Uhr und macht "
                    "wiederkehrende Zuordnungen sichtbar. Nutze numerische "
                    "dB-Werte, Median und Mittelwert; die relative Dichte wird "
                    "innerhalb des aktiven Zeitpanels normiert."
                ),
                "limits": (
                    "Das ist eine beobachtungsgewichtete Ansicht der ausgewählten "
                    "Stationen; sie ersetzt nicht das stationsgleichgewichtete "
                    "Segmentergebnis und trennt Pfad-, Ausbreitungs-, Schalt- oder "
                    "Zeitplaneffekte nicht voneinander."
                ),
            },
            "selected_success": {
                "read": (
                    "Die Evidenz ausgewählter Stationen kann belegen, wann sich "
                    "Ergebnisse "
                    "und Evidenzumfang für die "
                    '<strong class="defined-term">ausgewählten {peer_type}-'
                    "Stationen</strong> änderten und wie erfolgreiches Target-SNR "
                    "verteilt war. Die Ansicht "
                    '<strong class="defined-term">poolt</strong> ihre Target- und '
                    '<strong class="defined-term">{counter}</strong>-Evidenz; '
                    "Stationen mit mehr Beobachtungen wirken stärker. **Station "
                    "Success Rate + Evidence over Time** verbindet die Success "
                    "Rate mit den zugehörigen Target- und {counter}-Anzahlen; lies "
                    "die Rate zusammen mit ihrem Evidenzumfang. Die Farben zeigen, "
                    "ob der betrachtete Großkreispfad als Nacht, "
                    "Greyline/gemischt oder Tageslicht klassifiziert wurde. "
                    "**Target SNR** enthält nur erfolgreiche Target-Decodes, "
                    "normiert auf die gemeldete Leistung von 1 W; ein weniger "
                    "negativer Wert ist relativ zum Rauschen stärker."
                ),
                "limits": (
                    "Die Ansicht kann einen Zusammenhang mit der Pfadbeleuchtung "
                    "zeigen, aber keine Ursache belegen; Target-SNR kennt weder die "
                    "Stärke fehlender Decodes noch die tatsächlich abgestrahlte "
                    "Leistung."
                ),
            },
            "drilldown_compare_joint": {
                "read": (
                    "Die Drill-Down-Daten liefern den Prüfpfad vom gepaarten "
                    "Ergebnis "
                    "zurück zu seiner beitragenden Evidenz. Es zeigt die "
                    '<strong class="defined-term">verarbeiteten '
                    "Evidenzzeilen</strong> nach Zuordnung und Filtern von "
                    "WSPRadar, nicht unveränderte Provider-Zeilen. Same-cycle "
                    "Compare zeigt für jedes Paar die verwendeten Target- und "
                    "Referenzwerte sowie sein ΔSNR. Nutze genaue UTC-Zeiten, "
                    "Stationen und Werte, um Zusammenfassungen abzugleichen und "
                    "außergewöhnliche Beobachtungen zu untersuchen. Filter "
                    "verändern nur die angezeigte Tabelle."
                ),
                "limits": (
                    "Die Zeilen belegen, wie WSPRadar die Zusammenfassungen "
                    "gebildet hat; fehlendes SNR und nicht erfasste Eigenschaften "
                    "des physischen Aufbaus können sie nicht rekonstruieren."
                ),
            },
            "drilldown_compare_scheduled": {
                "read": (
                    "Die Drill-Down-Daten liefern den Prüfpfad vom geplanten "
                    "Ergebnis "
                    "zurück zu seinen beitragenden Paaren. Es zeigt die "
                    '<strong class="defined-term">verarbeiteten geplanten '
                    "Paare</strong> mit UTC-Paar, TX-Rolle, Target- und "
                    "Referenz-Mikromedian sowie Paar-ΔSNR. Damit kannst du prüfen, "
                    "ob die Paarbildung dem konfigurierten Zeitplan folgt, und die "
                    "Zusammenfassungen bis zu den einzelnen Paaren nachvollziehen. "
                    "Filter verändern nur die angezeigte Tabelle."
                ),
                "limits": (
                    "Die Zeilen belegen Paarbildung und berechnete Werte; ob "
                    "Ausbreitung oder Störungen zwischen beiden Aussendungen "
                    "konstant blieben, können sie nicht zeigen."
                ),
            },
            "drilldown_success": {
                "read": (
                    "Die Drill-Down-Daten liefern den Prüfpfad von der Success Rate "
                    "zurück zu den beitragenden Zyklen. Es zeigt die "
                    '<strong class="defined-term">verarbeiteten '
                    "Evidenzzeilen</strong> nach Evidenzregeln und Filtern von "
                    "WSPRadar. Outcomes unterscheiden Target, "
                    '<strong class="defined-term">{counter}</strong> und '
                    '<strong class="defined-term">Target-only</strong>. '
                    "Target-only bleibt prüfbar, fließt aber nicht in den Nenner "
                    "der Success Rate ein. Damit kannst du Zähler und Nenner bis "
                    "zu den beitragenden Stationen und UTC-Zyklen nachvollziehen. "
                    "Filter verändern nur die angezeigte Tabelle."
                ),
                "limits": (
                    "Die Zeilen belegen, wie die berücksichtigten Zyklen die "
                    "Success-Zusammenfassungen bilden; nicht bestätigte "
                    "Aussendungen und die Ursache eines fehlenden Decodes bleiben "
                    "unbeobachtet."
                ),
            },
            "drilldown_local_median": {
                "read": (
                    "Beim lokalen Nachbarschaftsmedian zeigt Drill-Down zusätzlich "
                    "die lokalen Referenzstationen, aus denen der jeweilige "
                    "Zyklusmedian gebildet wurde. Damit ist der wechselnde "
                    "Nachbarschaftsbenchmark direkt nachvollziehbar."
                ),
                "limits": (
                    "Die beitragenden Stationen erklären die dynamische Referenz; "
                    "sie machen daraus keine feste oder kalibrierte "
                    "Referenzstation."
                ),
            },
            "download": {
                "read": (
                    "Mit `Evidenz herunterladen` bewahrst du die abgeschlossene "
                    "Analyse als "
                    '<strong class="defined-term">Analyse-'
                    "Evidenzpaket</strong> für Prüfung, Weitergabe und "
                    "Reproduzierbarkeit. Es enthält Konfiguration und Metadaten "
                    "des Laufs, die im geografischen Analyseumfang beibehaltene "
                    "verarbeitete Evidenz sowie die anwendbaren Tabellen und "
                    "hochauflösenden Abbildungen für den aktuellen "
                    "Inspector-Bereich und die ausgewählten Stationen. `Konfig "
                    "speichern` bewahrt separat wiederverwendbare "
                    "Analyseeinstellungen ohne die Evidenz dieses Laufs."
                ),
                "limits": (
                    "Das Paket reproduziert den aufgezeichneten WSPRadar-"
                    "Analysestand, nicht den physischen Versuch oder unveränderte "
                    "Provider-Antworten; spätere Archivabfragen können bei "
                    "Änderungen an Daten oder WSPRadar abweichen."
                ),
            },
        },
    },
}


# Streamlit sessions created before canonical widget tokens were introduced can
# survive a deployment rerun with the old display label still stored as state.
# Keep these historical labels explicit so changing UI wording never changes a
# live session's scientific comparison design.
LEGACY_LOCALIZED_STATE_VALUES = {
    "Hardware A/B-Test (Local Setup)": "hardware_ab",
    "Hardware A/B-Test (Eigenes Setup)": "hardware_ab",
    "Reference Station (Buddy Test)": "reference_station",
    "Fremdes Rufzeichen (Buddy-Test)": "reference_station",
    "Local Neighborhood Benchmark": "local_neighborhood",
    "Lokaler Nachbarschafts-Benchmark": "local_neighborhood",
    "Nearest Peers (Local Average)": "local_neighborhood",
    "Nearest Peers (Lokaler Durchschnitt)": "local_neighborhood",
}


# Guided Input owns question-led presentation text only. Scientific labels that
# are shared with Classic Input remain in ``T`` so both editors name the same
# canonical field consistently.
GUIDED_INPUTS = {
    "en": {
        "mode": {
            "label": "Input view",
            "guided": "🧭 Guided",
            "classic": "⚙️ Classic",
        },
        "steps": {
            "use_case": {
                "title": "What do you want to investigate?",
                "body_md": """Turn WSPR spots into evidence about your station. Explore where, when and how well your receiver or transmitter performs, benchmark an antenna, radio or complete signal path against a Reference, or start with one of the prepared demos above. The <strong class="defined-term">Target</strong> is the station or signal path you want to examine. <strong class="defined-term">RX</strong> means receiving; <strong class="defined-term">TX</strong> means transmitting. Choose <strong class="defined-term">Success</strong> to assess the Target on its own. Choose <strong class="defined-term">Compare</strong> when you want to compare the Target against a <strong class="defined-term">Reference</strong>. This choice determines the remaining steps and whether the results show stand-alone Target values or relative Target-versus-Reference values.""",
            },
            "target_and_window": {
                "title": "Define the Target and measurement window",
                "body_md": """The <strong class="defined-term">Target</strong> is the station or controlled path being tested. A WSPR <strong class="defined-term">spot</strong> is a successful decode uploaded by a reporting station. Enter the exact callsign or reporting identity stored in the WSPR archive and the Target's <strong class="defined-term">QTH</strong>—its station location. Choose one band and a UTC period during which the identity, location and tested setup were correct and reasonably stable. **Last X hours** is resolved to an exact UTC interval when the analysis starts; **Custom date/time** uses the dates and times entered below.""",
            },
            "reference_design": {
                "title": "What should be used as the Reference?",
                "body_md": """The <strong class="defined-term">Reference</strong> is the baseline used to compare the Target. It can be another controlled path at your station, one known station at another QTH, or a local benchmark formed from nearby active stations. This choice determines what is actually being compared and how narrowly the result can be interpreted.

**Compare terminology**

- <strong class="defined-term">SNR</strong> is the signal-to-noise ratio reported by the WSPR decoder, in dB. A less-negative value represents a stronger signal relative to noise.
- <strong class="defined-term">ΔSNR</strong> ("delta SNR") is the Target SNR minus the Reference SNR. A positive value favors the Target; a negative value favors the Reference.
- **Joint evidence** means that comparable evidence is available for both sides: the same transmission was decoded by both RX sides, corresponding Target and Reference reports were made at the same receiving station, or a scheduled Target–Reference pair is available for sequential TX.""",
            },
            "offset_calibration": {
                "title": "Is there an established Target–Reference offset?",
                "body_md": """An <strong class="defined-term">offset</strong> is a repeatable Target–Reference difference that is already present before the effect you want to study. A Reference-side correction adjusts the Reference SNR before ΔSNR is calculated. Leave the correction at **0.0 dB** unless the offset was established and documented for the same identities or paths, band, hardware and comparison method. The correction shifts every comparison result; it cannot compensate for uncontrolled differences that vary with time, station or radio path.""",
            },
            "scope_and_evidence": {
                "title": "Scope and evidence",
                "body_md": """Set the remote station filters, analysis scope, and evidence requirements for this run.""",
            },
            "review_and_run": {
                "title": "Review and run",
                "body_md": """Check that this summary matches the station setup and operating period you actually want to analyze. It defines the Target, Reference, band, UTC window, scope and evidence rules used by the run. Guided and Classic Input edit the same scientific configuration; changing the input view does not change the analysis.""",
            },
        },
        "options": {
            "use_cases": {
                "rx_success": {
                    "label": "RX Success",
                    "description": """Choose this to evaluate your receiver without a Reference. WSPRadar finds WSPR cycles in which another receiver decoded the same transmitter, confirming that the transmitter was active and heard elsewhere, and then checks whether the Target receiver also decoded it. Success Rate is the share of those confirmed opportunities decoded by the Target. The results show stand-alone Target values only, not a Reference comparison.""",
                },
                "tx_success": {
                    "label": "TX Success",
                    "description": """Choose this to evaluate your transmitter without a Reference. During cycles in which the Target is known to be transmitting, a remote receiver is treated as active when it decoded another signal on the same band; WSPRadar then checks whether it also decoded the Target. Success Rate is the share of those confirmed opportunities in which the Target was decoded. The results show stand-alone Target values only, not a Reference comparison.""",
                },
                "rx_compare": {
                    "label": "RX Compare",
                    "description": """Choose this when you want to compare your receiver or receive path against a Reference. In the next step, the Reference can be another controlled path, one known station, or a local neighborhood benchmark. The results show relative Target-versus-Reference values only, not a stand-alone Success result.""",
                },
                "tx_compare": {
                    "label": "TX Compare",
                    "description": """Choose this when you want to compare your transmitter, TX path or complete station against a Reference. In the next step, the Reference can be another controlled path, one known station, or a local neighborhood benchmark. The results show relative Target-versus-Reference values only, not a stand-alone Success result.""",
                },
            },
            "reference_design": {
                "hardware_ab": {
                    "label": "Controlled paths at the same station",
                    "description": """Use this for two controlled paths at one station—for example antennas, feedlines, receivers, transmitters or complete chains. Keep every other relevant condition as stable as possible. The result describes the complete paths as installed, including any difference that was not controlled; it does not by itself isolate antenna gain or one component's performance.""",
                },
                "reference_station": {
                    "label": "Known Reference Station",
                    "description": """Use this to compare the Target with one specified station at another QTH. This is a whole-station comparison: site, terrain, local noise, antennas, equipment, operating practice and the different radio paths remain part of the result. It cannot by itself isolate one hardware component.""",
                },
                "local_neighborhood": {
                    "label": "Local neighborhood benchmark",
                    "description": """Use this when you want to compare the Target with active WSPR stations near the Target QTH rather than with one fixed station. WSPRadar forms the Reference from eligible stations inside the chosen radius. The contributing stations can change from cycle to cycle, so the result is relative to a local peer population.""",
                },
            },
            "local_benchmark": {
                "local_median": {
                    "label": "Local median — typical nearby performance",
                    "description": """Use the median SNR of the eligible nearby stations in each comparable cycle. This represents typical nearby performance and limits the influence of one unusually strong station. The stations contributing to the median may change over time.""",
                },
                "local_best": {
                    "label": "Local best — strongest nearby station",
                    "description": """Use the strongest eligible nearby station in each comparable cycle. This is a demanding benchmark against the best local performer available at that time, not a measure of typical neighborhood performance. The Reference station may change from cycle to cycle.""",
                },
            },
            "tx_ab_method": {
                "simultaneous": {
                    "label": "Transmit simultaneously",
                    "description": """Target and Reference transmit in the same WSPR cycle under distinct exact callsigns. A receiver that decodes both supplies same-cycle joint evidence, minimizing the time available for propagation or noise to change. Confirm that simultaneous operation is safe, compliant and free of self-interference.""",
                },
                "sequential": {
                    "label": "Alternate on a fixed schedule",
                    "description": """The same callsign is transmitted alternately through the two physical paths at fixed UTC minute phases. WSPRadar compares the planned Target and Reference transmissions as scheduled pairs. This avoids simultaneous transmission, but propagation and noise can change between the two transmissions.""",
                },
            },
            "offset_intent": {
                "no_offset": {
                    "label": "No established offset — use 0.0 dB",
                    "description": """Apply no Reference-side correction. Use this for a first exploratory run or whenever no defensible baseline exists and you are not establishing one in this run. Any stable Target–Reference bias remains part of the reported ΔSNR.""",
                },
                "established_offset": {
                    "label": "Use an established correction",
                    "description": """Apply a documented signed correction established for the same paths or identities, band, hardware and comparison method. The formula shown below explains how the sign changes the corrected ΔSNR.""",
                },
                "establish_offset": {
                    "label": "Set up an offset-establishment run",
                    "description": """Run Compare with a 0.0 dB correction to characterize the existing Target–Reference baseline. WSPRadar displays the paired evidence but does not choose a correction automatically. Review and document the result, then enter a defensible signed value in a later run.""",
                },
            },
            "scope_mode": {
                "general": {
                    "label": "Use general-purpose settings",
                    "description": "Use WSPRadar's current default values.",
                },
                "custom": {
                    "label": "Review and customize",
                    "description": "Show the remote station filters, scope controls and evidence thresholds for editing.",
                },
                "demo": {
                    "label": "Keep the guided demo settings",
                    "description": "Use the values stored in the selected demo profile.",
                },
            },
        },
        "summaries": {
            "window_last_x": "last {hours} h",
            "window_custom": "{start}–{end} UTC",
            "window_incomplete": "UTC interval incomplete",
            "use_case": "{step} · Question — {choice} ✓",
            "target_and_window": "{step} · Target — {callsign} · {qth} · {band} · {window} ✓",
            "reference_hardware_rx": "{step} · Reference — {callsign} · controlled local RX path ✓",
            "reference_hardware_tx_simultaneous": "{step} · Reference — {callsign} · simultaneous local TX paths ✓",
            "reference_hardware_tx_sequential": "{step} · Reference — scheduled alternating local TX paths ✓",
            "reference_station": "{step} · Reference — {callsign} · known station · {qth} ✓",
            "reference_local_median": "{step} · Reference — local median within {radius} km ✓",
            "reference_local_best": "{step} · Reference — local best within {radius} km ✓",
            "offset_none": "{step} · Reference correction — 0.0 dB ✓",
            "offset_established": "{step} · Reference correction — {offset:+.1f} dB ✓",
            "offset_establish": "{step} · Baseline run — 0.0 dB correction ✓",
            "scope": "{step} · Scope and evidence — max {distance} km · {solar} · {mode} ✓",
            "review_ready": "{step} · Review — ready to run ✓",
        },
        "messages": {
            "demo_title": "Guided demo",
            "demo_preset": """This demo loads a complete preset for a documented example. For a first run, keep the preset unchanged and use it to learn how the question, identities and analysis settings lead to the displayed result. The demo describes the listed stations and historical period; it is not evidence about your own station.""",
            "demo_walkthrough": "Walk me through the setup",
            "demo_walkthrough_help": "Review each preset choice and what it changes in the analysis.",
            "demo_skip_to_review": "Skip to review and run",
            "demo_skip_to_review_help": "Go directly to the complete configuration summary before starting the demo.",
            "target_callsign_help": """Enter the exact callsign or reporting identity uploaded to the WSPR archive. The archive treats forms such as DL1MKS, DL1MKS/P and DL1MKS-1 as different identities, so a spelling or suffix difference selects different evidence—or none.""",
            "target_qth_help": """QTH means station location. Enter the 4- or 6-character Maidenhead locator used by the Target during the selected period. WSPRadar uses it to identify and position the Target and to calculate map geometry, distance, direction and the local solar state.""",
            "band_help": """Choose the single WSPR band used for the experiment. WSPRadar does not combine evidence from different bands because propagation, antenna response, noise and station hardware can differ substantially by band.""",
            "time_help": """Choose a period in which the callsigns, locations, hardware, schedules and reported power were correct and reasonably stable. Shorter windows describe a more specific situation but may contain little evidence; longer windows add evidence while mixing more propagation states and possible station changes.""",
            "reference_designs_title": "Reference designs",
            "controlled_path_note": """In a controlled Hardware A/B comparison, the two paths should differ only in the item you intend to test. Keep the remaining band, timing, gain or power, software and station chain stable. The result still describes the complete installed paths and includes every difference that was not controlled.""",
            "known_reference_note": """This compares complete stations. Differences in QTH, terrain, local noise, antennas, equipment, operating practice and radio path remain part of the result. The comparison cannot by itself isolate antenna gain or one hardware component.""",
            "reference_callsign_help": """Enter the Reference's exact callsign or reporting identity in the WSPR archive. A portable form, suffix or spelling change is a different identity and therefore selects different reports.""",
            "reference_grid4_help": """Enter the four-character Maidenhead grid reported for the Reference during this period. It constrains the Reference to the intended station location and supplies the Reference-side map geometry.""",
            "local_neighborhood_note": """The neighborhood is a changing pool of active stations, not one fixed Reference. The radius determines which stations can enter that pool. A larger radius usually adds evidence but weakens the assumption that the stations share comparable local conditions.""",
            "local_benchmark_help": """Local median represents typical eligible nearby performance. Local best selects the strongest eligible neighbor in each comparable cycle. Both methods may use different stations over time, and the choice changes the Reference used by Compare.""",
            "local_radius_help": """Only active Reference stations within this distance of the Target QTH may contribute. Increasing the radius usually adds candidates but makes the benchmark less local. This setting changes the Reference population and the result; it is not merely a map-zoom control.""",
            "local_existing_correction_warning": """This configuration already contains a {offset:+.1f} dB correction for the local Reference. The standard Guided neighborhood path leaves that advanced value unchanged, so it would still affect every ΔSNR. Open Classic setup to review or reset it before running.""",
            "tx_ab_method_help": """Simultaneous TX provides same-cycle evidence and minimizes time separation, but it requires distinct archive identities and operation that is safe, compliant and free of self-interference. Sequential TX uses a deterministic UTC schedule, but it cannot remove propagation or noise changes between the paired transmissions.""",
            "correction_formula": """**Corrected ΔSNR = Target SNR − (Reference SNR + correction)**\x20\x20\nA positive ΔSNR favors the Target; a negative value favors the Reference.""",
            "correction_consequence": """{offset:+.1f} dB will be added to every Reference SNR before subtraction. A positive correction lowers the corrected ΔSNR; a negative correction raises it.""",
            "hardware_calibration": """Here, calibration means estimating a repeatable baseline difference between the complete Target and Reference paths while both paths receive a common, known input or while the intended difference is independently known. It is not an absolute measurement of antenna gain, efficiency or receiver sensitivity.""",
            "reference_calibration": """Here, the offset is an empirical baseline for this exact Target–Reference pair under a defined band, setup and operating design. Because geographically separated stations do not share the same site or radio path, this is not an absolute calibration and should not be transferred to another station pair or setup.""",
            "establish_hardware_guidance": """Create a baseline in which the intended difference is absent or independently known. For RX, feed both paths from the same stable source or antenna. For TX, use an independently characterized equal-output baseline or measure both paths at the same RF reference plane. Hold the remaining setup fixed.\n\nAfter the run, choose and document one ΔSNR estimate: the median or arithmetic mean from **Station Medians**, or from **Joint Spots / Scheduled Pairs**. Enter the observed Target − Reference value with the same sign as the Reference correction in the next run—for example, enter `+1.6 dB` for a `+1.6 dB` baseline.\n\nStation level gives each station one vote and is usually the better default for WSPRadar's station-balanced result. Spot/pair level gives each observation one vote, so high-volume stations can dominate. The median is more robust to outliers and skew; the mean can be appropriate for a roughly symmetric distribution without influential extremes, but is more sensitive to them. Choose from the intended weighting and evidence distribution—not the preferred answer. If the estimates differ materially, investigate rather than cherry-picking; one constant offset may not be defensible. Finally, repeat or swap paths and verify that the corrected common-input ΔSNR is plausibly centered near `0 dB`.""",
            "establish_reference_guidance": """Choose a stable baseline period for this exact Target–Reference pair, band and operating design, with no known station change. Keep the identities, scope and operating conditions fixed.\n\nAfter the run, choose and document one ΔSNR estimate: the median or arithmetic mean from **Station Medians**, or from **Joint Spots / Scheduled Pairs**. Enter the observed Target − Reference value with the same sign as the Reference correction in the next run—for example, enter `+1.6 dB` for a `+1.6 dB` baseline.\n\nStation level gives each station one vote and is usually the better default for WSPRadar's station-balanced result. Spot/pair level gives each observation one vote, so high-volume stations can dominate. The median is more robust to outliers and skew; the mean can be appropriate for a roughly symmetric distribution without influential extremes, but is more sensitive to them. Choose from the intended weighting and evidence distribution—not the preferred answer. If the estimates differ materially, investigate rather than cherry-picking; one constant offset may not be defensible. Check stability across stations, signal level and time, then repeat the baseline under the same operating design and verify that the corrected ΔSNR is plausibly centered near `0 dB`.""",
            "calibration_run_notice": """Offset-establishment run: the Reference correction is fixed at 0.0 dB. Run the normal Compare analysis to measure the uncorrected Target − Reference baseline. WSPRadar shows the available summaries but does not select or apply an offset.""",
            "station_population_title": "Remote station filters",
            "station_population_body": """These controls exclude telemetry-like identifiers or stations whose reported locator changed during the selected period. Exclusions can improve identity or location consistency, but they can also remove valid evidence. Set them from the experiment design rather than after seeing a preferred result.""",
            "analysis_scope_title": "Analysis scope",
            "analysis_scope_body": """Solar state selects observations by the Sun's elevation at the Target QTH. Maximum distance limits which peer stations remain in the analysis, map, Inspector and export. These settings change the analyzed data; maximum distance is not only a map-zoom control.""",
            "evidence_requirements_title": "Evidence requirements",
            "compare_evidence_requirements_body": """Each station must provide the selected minimum number of joint observations or scheduled TX pairs. A map segment must also contain the selected number of qualifying stations. Higher thresholds require more repeated evidence but reduce station and geographic coverage; they do not remove propagation effects or guarantee measurement quality.""",
            "success_evidence_requirements_body": """Each station must provide the selected minimum number of independently confirmed opportunities. A map segment must also contain the selected number of qualifying stations. Higher thresholds require more repeated evidence but reduce station and geographic coverage; they do not remove propagation effects or guarantee measurement quality.""",
            "general_active": """General-purpose settings are active. Treat them as a starting point, not a quality grade.""",
            "demo_active": """The guided demo's saved settings are active. They apply to this example, not universally.""",
            "included": "excluded",
            "not_included": "included",
            "compare_evidence": """joint evidence ≥ {value} per station; qualifying stations ≥ {stations} per map segment""",
            "success_evidence": """confirmed opportunities ≥ {value} per station; qualifying stations ≥ {stations} per map segment""",
            "review_question": "Question",
            "review_target": "Target",
            "review_target_value": "{callsign} at {qth}",
            "review_reference": "Reference",
            "review_tx_simultaneous_value": "{callsign} · {method}",
            "review_tx_sequential_value": "{method} · repeat interval {repeat} min · Target {target:02d} UTC · Reference {reference:02d} UTC",
            "review_band_window": "Band and UTC window",
            "review_correction": "Reference-side correction",
            "review_population": "Remote station filters",
            "review_population_value": "special identifiers {special}; stations changing locator {moving}",
            "review_scope": "Solar and geographic scope",
            "review_evidence": "Evidence requirements",
            "review_result": "Result type",
            "result_success": "Success — stand-alone Target values",
            "result_compare": "Compare — Target-versus-Reference values",
            "open_classic": "Open Classic setup",
            "continue": "Continue",
            "configuration_changed": """Inputs changed since the last run. Run the analysis again before interpreting the results.""",
        },
        "validation": {
            "use_case": "Choose one operating question before continuing.",
            "target_and_window": "Enter a valid Target identity and QTH, select a band, and complete the UTC measurement window before continuing.",
            "reference_design": "Complete the selected Reference design, including the required identity and QTH, neighborhood settings, or TX schedule.",
            "offset_calibration": "Choose whether to use no correction, enter an established correction, or set up an offset-establishment run.",
            "scope_and_evidence": "Choose general-purpose, customized or demo-defined scope and evidence settings before continuing.",
            "flow_invalid": "Guided Input is unavailable because its workflow configuration is invalid: {error}",
        },
    },
    "de": {
        "mode": {
            "label": "Eingabeansicht",
            "guided": "🧭 Geführt",
            "classic": "⚙️ Klassisch",
        },
        "steps": {
            "use_case": {
                "title": "Was möchtest du untersuchen?",
                "body_md": """WSPR-Spots liefern belastbare Evidenz über deine Station. Untersuche, wo, wann und wie gut dein Empfänger oder Sender arbeitet, vergleiche eine Antenne, einen Transceiver oder einen vollständigen Signalpfad systematisch mit einer Referenz – oder starte mit einer der oben vorbereiteten Demos. Das <strong class="defined-term">Target</strong> ist die Station oder der Signalpfad, den du untersuchen möchtest. <strong class="defined-term">RX</strong> bedeutet Empfang, <strong class="defined-term">TX</strong> bedeutet Senden. Wähle <strong class="defined-term">Success</strong>, wenn du das Target für sich bewerten möchtest. Wähle <strong class="defined-term">Compare</strong>, wenn du das Target mit einer <strong class="defined-term">Referenz</strong> vergleichen möchtest. Diese Auswahl bestimmt die weiteren Schritte und ob die Ergebnisse eigenständige Target-Werte oder relative Target–Referenz-Werte zeigen.""",
            },
            "target_and_window": {
                "title": "Target und Messzeitraum festlegen",
                "body_md": """Das <strong class="defined-term">Target</strong> ist die getestete Station oder der getestete kontrollierte Pfad. Ein WSPR-<strong class="defined-term">Spot</strong> ist ein erfolgreicher Decode, den eine meldende Station hochgeladen hat. Gib die exakte im WSPR-Archiv gespeicherte Rufzeichen bzw. die im WSPR-Archiv verwendete Kennung und das <strong class="defined-term">QTH</strong> des Targets ein—also seinen Stationsstandort. Wähle ein Band und einen UTC-Zeitraum, in dem Kennung, Standort und getesteter Aufbau korrekt und möglichst stabil waren. **Letzte X Stunden** wird beim Start der Analyse in einen exakten UTC-Zeitraum aufgelöst; **Datum/Uhrzeit manuell** verwendet die unten eingegebenen Werte.""",
            },
            "reference_design": {
                "title": "Was soll als Referenz dienen?",
                "body_md": """Die <strong class="defined-term">Referenz</strong> ist die Vergleichsbasis für das Target. Sie kann ein weiterer kontrollierter Pfad an deiner Station, eine bekannte Station an einem anderen QTH oder ein lokaler Vergleichsmaßstab aus nahen aktiven Stationen sein. Diese Wahl legt fest, was tatsächlich verglichen wird und wie eng das Ergebnis interpretiert werden darf.

**Begriffe in Compare**

- <strong class="defined-term">SNR</strong> ist das vom WSPR-Decoder gemeldete Signal-Rausch-Verhältnis in dB. Ein weniger negativer Wert bedeutet ein stärkeres Signal im Verhältnis zum Rauschen.
- <strong class="defined-term">ΔSNR</strong> ("Delta-SNR") ist Target-SNR minus Referenz-SNR. Ein positiver Wert spricht für das Target, ein negativer Wert für die Referenz.
- **Joint-Evidenz** bedeutet, dass für beide Seiten vergleichbare Daten vorliegen: dieselbe Aussendung wurde von beiden RX-Seiten dekodiert, an derselben Empfangsstation liegen passende Reports für Target und Referenz vor, oder bei sequenziellem TX gibt es ein geplantes Target–Referenz-Paar.""",
            },
            "offset_calibration": {
                "title": "Gibt es einen ermittelten Target–Referenz-Offset?",
                "body_md": """Ein <strong class="defined-term">Offset</strong> ist eine wiederholbare Target–Referenz-Differenz, die bereits vorhanden ist, bevor der eigentliche untersuchte Effekt hinzukommt. Eine referenzseitige Korrektur verändert das Referenz-SNR, bevor ΔSNR berechnet wird. Belasse die Korrektur bei **0,0 dB**, sofern der Offset nicht für dieselben Kennungen oder Pfade, dasselbe Band, dieselbe Hardware und dieselbe Vergleichsmethode ermittelt und dokumentiert wurde. Die Korrektur verschiebt jedes Vergleichsergebnis; sie kann keine unkontrollierten Unterschiede ausgleichen, die sich mit Zeit, Station oder Funkweg ändern.""",
            },
            "scope_and_evidence": {
                "title": "Umfang und Evidenz",
                "body_md": """Lege Remote Stationsfilter, Analyseumfang und Evidenzanforderungen für diesen Lauf fest.""",
            },
            "review_and_run": {
                "title": "Prüfen und starten",
                "body_md": """Prüfe, ob diese Zusammenfassung zu dem Stationsaufbau und Betriebszeitraum passt, den du tatsächlich analysieren möchtest. Sie definiert Target, Referenz, Band, UTC-Zeitraum, Umfang und Evidenzregeln des Laufs. Die geführte und die klassische Eingabe bearbeiten dieselbe wissenschaftliche Konfiguration; der Wechsel der Eingabeansicht verändert die Analyse nicht.""",
            },
        },
        "options": {
            "use_cases": {
                "rx_success": {
                    "label": "RX Success",
                    "description": """Wähle dies, um deinen Empfänger ohne Referenz zu bewerten. WSPRadar sucht WSPR-Zyklen, in denen ein anderer Empfänger denselben Sender dekodiert hat—damit ist bestätigt, dass der Sender aktiv war und anderswo gehört wurde—und prüft dann, ob auch der Target-Empfänger ihn dekodiert hat. Die Success Rate ist der Anteil dieser bestätigten Gelegenheiten, die das Target dekodiert hat. Die Ergebnisse zeigen nur eigenständige Target-Werte, keinen Referenzvergleich.""",
                },
                "tx_success": {
                    "label": "TX Success",
                    "description": """Wähle dies, um deinen Sender ohne Referenz zu bewerten. In Zyklen, in denen das Target nachweislich sendet, gilt eine entfernte Empfangsstation als aktiv, wenn sie auf demselben Band ein anderes Signal dekodiert hat; WSPRadar prüft dann, ob sie auch das Target dekodiert hat. Die Success Rate ist der Anteil dieser bestätigten Gelegenheiten, in denen das Target gehört wurde. Die Ergebnisse zeigen nur eigenständige Target-Werte, keinen Referenzvergleich.""",
                },
                "rx_compare": {
                    "label": "RX Compare",
                    "description": """Wähle dies, wenn du deinen Empfänger oder RX-Pfad mit einer Referenz vergleichen möchtest. Im nächsten Schritt kann die Referenz ein weiterer kontrollierter Pfad, eine bekannte Station oder ein lokaler Nachbarschaftsmaßstab sein. Die Ergebnisse zeigen nur relative Target–Referenz-Werte, kein eigenständiges Success-Ergebnis.""",
                },
                "tx_compare": {
                    "label": "TX Compare",
                    "description": """Wähle dies, wenn du deinen Sender, TX-Pfad oder deine vollständige Station mit einer Referenz vergleichen möchtest. Im nächsten Schritt kann die Referenz ein weiterer kontrollierter Pfad, eine bekannte Station oder ein lokaler Nachbarschaftsmaßstab sein. Die Ergebnisse zeigen nur relative Target–Referenz-Werte, kein eigenständiges Success-Ergebnis.""",
                },
            },
            "reference_design": {
                "hardware_ab": {
                    "label": "Kontrollierte Pfade an derselben Station",
                    "description": """Verwende dies für zwei kontrollierte Pfade an einer Station—zum Beispiel Antennen, Speiseleitungen, Empfänger, Sender oder vollständige Ketten. Halte alle anderen relevanten Bedingungen möglichst stabil. Das Ergebnis beschreibt die vollständigen installierten Pfade einschließlich aller nicht kontrollierten Unterschiede; es isoliert nicht automatisch Antennengewinn oder die Leistung eines einzelnen Bauteils.""",
                },
                "reference_station": {
                    "label": "Bekannte Referenzstation",
                    "description": """Verwende dies, um das Target mit einer bestimmten Station an einem anderen QTH zu vergleichen. Dabei werden vollständige Stationen verglichen: Standort, Gelände, lokales Rauschen, Antennen, Geräte, Betriebspraxis und die unterschiedlichen Funkwege bleiben Teil des Ergebnisses. Eine einzelne Hardwarekomponente lässt sich damit nicht isolieren.""",
                },
                "local_neighborhood": {
                    "label": "Lokaler Nachbarschaftsvergleich",
                    "description": """Verwende dies, wenn du das Target nicht mit einer festen Station, sondern mit aktiven WSPR-Stationen in der Nähe des Target-QTH vergleichen möchtest. WSPRadar bildet die Referenz aus geeigneten Stationen innerhalb des gewählten Radius. Die beteiligten Stationen können von Zyklus zu Zyklus wechseln; das Ergebnis bezieht sich daher auf eine lokale Vergleichsgruppe.""",
                },
            },
            "local_benchmark": {
                "local_median": {
                    "label": "Lokaler Median — typische Leistung in der Nähe",
                    "description": """Verwende in jedem vergleichbaren Zyklus den Median des SNR der geeigneten nahen Stationen. Das bildet eine typische lokale Leistung ab und begrenzt den Einfluss einer einzelnen ungewöhnlich starken Station. Die Stationen, die zum Median beitragen, können sich im Zeitverlauf ändern.""",
                },
                "local_best": {
                    "label": "Beste lokale Station — stärkster Nachbar",
                    "description": """Verwende in jedem vergleichbaren Zyklus die stärkste geeignete Station in der Nähe. Das ist ein anspruchsvoller Vergleich mit dem jeweils besten verfügbaren lokalen Teilnehmer, kein Maß für die typische Nachbarschaft. Die Referenzstation kann von Zyklus zu Zyklus wechseln.""",
                },
            },
            "tx_ab_method": {
                "simultaneous": {
                    "label": "Gleichzeitig senden",
                    "description": """Target und Referenz senden im selben WSPR-Zyklus unter zwei unterschiedlichen exakten Rufzeichen. Eine Empfangsstation, die beide dekodiert, liefert Joint-Evidenz aus demselben Zyklus und verkürzt damit die Zeit, in der sich Ausbreitung oder Rauschen ändern können. Stelle sicher, dass der gleichzeitige Betrieb sicher, zulässig und frei von Eigenstörungen ist.""",
                },
                "sequential": {
                    "label": "Nach festem Zeitplan abwechseln",
                    "description": """Dasselbe Rufzeichen wird zu festen UTC-Minutenphasen abwechselnd über die beiden physischen Pfade gesendet. WSPRadar vergleicht die geplanten Target- und Referenzaussendungen als Zeitplanpaare. Dadurch wird gleichzeitiges Senden vermieden, aber Ausbreitung und Rauschen können sich zwischen den beiden Aussendungen ändern.""",
                },
            },
            "offset_intent": {
                "no_offset": {
                    "label": "Kein ermittelter Offset — 0,0 dB verwenden",
                    "description": """Wende keine referenzseitige Korrektur an. Verwende dies für einen ersten Erkundungslauf oder wenn keine belastbare Basislinie vorliegt und in diesem Lauf keine ermittelt wird. Ein stabiler Target–Referenz-Versatz bleibt dann Teil des ausgewiesenen ΔSNR.""",
                },
                "established_offset": {
                    "label": "Ermittelte Korrektur verwenden",
                    "description": """Wende eine dokumentierte Korrektur mit Vorzeichen an, die für dieselben Pfade oder Kennungen, dasselbe Band, dieselbe Hardware und dieselbe Vergleichsmethode ermittelt wurde. Die unten gezeigte Formel erklärt, wie das Vorzeichen das korrigierte ΔSNR verändert.""",
                },
                "establish_offset": {
                    "label": "Offset-Ermittlungslauf einrichten",
                    "description": """Führe Compare mit 0,0 dB Korrektur aus, um die vorhandene Target–Referenz-Basislinie zu bestimmen. WSPRadar zeigt die gepaarte Evidenz, wählt aber keine Korrektur automatisch aus. Prüfe und dokumentiere das Ergebnis und trage anschließend in einem späteren Lauf einen belastbaren Wert mit korrektem Vorzeichen ein.""",
                },
            },
            "scope_mode": {
                "general": {
                    "label": "Allgemeine Einstellungen verwenden",
                    "description": "Verwende die aktuellen Standardwerte von WSPRadar.",
                },
                "custom": {
                    "label": "Prüfen und anpassen",
                    "description": "Zeige Remote Stationsfilter, Umfangseinstellungen und Evidenzschwellen zur Bearbeitung an.",
                },
                "demo": {
                    "label": "Einstellungen der geführten Demo beibehalten",
                    "description": "Verwende die im ausgewählten Demo-Profil gespeicherten Werte.",
                },
            },
        },
        "summaries": {
            "window_last_x": "letzte {hours} h",
            "window_custom": "{start}–{end} UTC",
            "window_incomplete": "UTC-Zeitraum unvollständig",
            "use_case": "{step} · Frage — {choice} ✓",
            "target_and_window": "{step} · Target — {callsign} · {qth} · {band} · {window} ✓",
            "reference_hardware_rx": "{step} · Referenz — {callsign} · kontrollierter lokaler RX-Pfad ✓",
            "reference_hardware_tx_simultaneous": "{step} · Referenz — {callsign} · gleichzeitige lokale TX-Pfade ✓",
            "reference_hardware_tx_sequential": "{step} · Referenz — geplante abwechselnde lokale TX-Pfade ✓",
            "reference_station": "{step} · Referenz — {callsign} · bekannte Station · {qth} ✓",
            "reference_local_median": "{step} · Referenz — lokaler Median innerhalb {radius} km ✓",
            "reference_local_best": "{step} · Referenz — beste lokale Station innerhalb {radius} km ✓",
            "offset_none": "{step} · Referenzkorrektur — 0,0 dB ✓",
            "offset_established": "{step} · Referenzkorrektur — {offset:+.1f} dB ✓",
            "offset_establish": "{step} · Basislinienlauf — 0,0 dB Korrektur ✓",
            "scope": "{step} · Umfang und Evidenz — max. {distance} km · {solar} · {mode} ✓",
            "review_ready": "{step} · Prüfung — startbereit ✓",
        },
        "messages": {
            "demo_title": "Geführte Demo",
            "demo_preset": """Diese Demo lädt eine vollständige Voreinstellung für ein dokumentiertes Beispiel. Belasse die Werte beim ersten Lauf unverändert und nutze das Beispiel, um zu sehen, wie Fragestellung, Kennungen und Analyseparameter zum angezeigten Ergebnis führen. Die Demo beschreibt die aufgeführten Stationen und den historischen Zeitraum; sie ist keine Aussage über deine eigene Station.""",
            "demo_walkthrough": "Einstellungen Schritt für Schritt durchgehen",
            "demo_walkthrough_help": "Prüfe jede Voreinstellung und erfahre, was sie in der Analyse verändert.",
            "demo_skip_to_review": "Direkt zu Prüfen und starten",
            "demo_skip_to_review_help": "Gehe direkt zur vollständigen Konfigurationsübersicht, bevor du die Demo startest.",
            "target_callsign_help": """Gib genau das Rufzeichen oder die Meldekennung ein, die in das WSPR-Archiv hochgeladen wurde. Das Archiv behandelt Formen wie DL1MKS, DL1MKS/P und DL1MKS-1 als unterschiedliche Identitäten. Eine abweichende Schreibweise oder ein anderes Suffix wählt daher andere Evidenz—oder gar keine.""",
            "target_qth_help": """QTH bedeutet Stationsstandort. Gib den vier- oder sechsstelligen Maidenhead-Locator ein, den das Target im ausgewählten Zeitraum verwendet hat. WSPRadar nutzt ihn zur Identifikation und Positionierung des Targets sowie für Kartengeometrie, Entfernung, Richtung und lokalen Sonnenstand.""",
            "band_help": """Wähle das einzelne WSPR-Band des Versuchs. WSPRadar führt Evidenz verschiedener Bänder nicht zusammen, weil sich Ausbreitung, Antennenverhalten, Rauschen und Stationshardware je nach Band deutlich unterscheiden können.""",
            "time_help": """Wähle einen Zeitraum, in dem Rufzeichen, Standorte, Hardware, Zeitpläne und gemeldete Leistung korrekt und möglichst stabil waren. Kürzere Zeiträume beschreiben eine konkretere Situation, können aber wenig Evidenz enthalten. Längere Zeiträume liefern mehr Evidenz, mischen jedoch mehr Ausbreitungszustände und mögliche Stationsänderungen.""",
            "reference_designs_title": "Referenzdesigns",
            "controlled_path_note": """Bei einem kontrollierten Hardware-A/B-Vergleich sollten sich die beiden Pfade nur in dem Teil unterscheiden, den du untersuchen möchtest. Halte Band, Zeitablauf, Verstärkung oder Leistung, Software und die übrige Stationskette stabil. Das Ergebnis beschreibt trotzdem die vollständigen installierten Pfade und enthält jeden Unterschied, der nicht kontrolliert wurde.""",
            "known_reference_note": """Hier vergleichst du vollständige Stationen. Unterschiede in QTH, Gelände, lokalem Rauschen, Antennen, Geräten, Betriebspraxis und Funkweg bleiben Teil des Ergebnisses. Antennengewinn oder eine einzelne Hardwarekomponente lassen sich daraus allein nicht isolieren.""",
            "reference_callsign_help": """Gib das exakte Rufzeichen bzw. die im WSPR-Archiv verwendete Kennung der Referenz im WSPR-Archiv ein. Eine Portable-Form, ein Suffix oder eine andere Schreibweise ist eine andere Identität und wählt deshalb andere Reports.""",
            "reference_grid4_help": """Gib das vierstellige Maidenhead-Grid ein, das die Referenz in diesem Zeitraum gemeldet hat. Es begrenzt die Referenz auf den beabsichtigten Stationsstandort und liefert die referenzseitige Kartengeometrie.""",
            "local_neighborhood_note": """Die Nachbarschaft ist ein wechselnder Pool aktiver Stationen und keine feste Referenz. Der Radius bestimmt, welche Stationen in diesen Pool gelangen können. Ein größerer Radius liefert meist mehr Evidenz, schwächt aber die Annahme vergleichbarer lokaler Bedingungen.""",
            "local_benchmark_help": """Lokaler Median steht für die typische Leistung geeigneter Stationen in der Nähe. Beste lokale Station wählt in jedem vergleichbaren Zyklus den stärksten geeigneten Nachbarn. Beide Methoden können im Zeitverlauf unterschiedliche Stationen verwenden; die Wahl verändert die Referenz, die Compare nutzt.""",
            "local_radius_help": """Nur aktive Referenzstationen innerhalb dieser Entfernung vom Target-QTH dürfen beitragen. Ein größerer Radius liefert meist mehr Kandidaten, macht den Vergleich aber weniger lokal. Diese Einstellung verändert die Referenzpopulation und das Ergebnis; sie ist nicht nur eine Karten-Zoomstufe.""",
            "local_existing_correction_warning": """Diese Konfiguration enthält bereits eine Korrektur von {offset:+.1f} dB für die lokale Referenz. Der normale geführte Nachbarschaftspfad verändert diesen erweiterten Wert nicht; er würde deshalb weiterhin jedes ΔSNR beeinflussen. Öffne vor dem Start die Klassische Eingabe, um ihn zu prüfen oder zurückzusetzen.""",
            "tx_ab_method_help": """Gleichzeitiges TX liefert Evidenz aus demselben Zyklus und minimiert den Zeitversatz, erfordert aber getrennte Archividentitäten sowie einen sicheren, zulässigen und eigenstörungsfreien Betrieb. Sequenzielles TX nutzt einen festen UTC-Zeitplan, kann Änderungen von Ausbreitung oder Rauschen zwischen den gepaarten Aussendungen jedoch nicht beseitigen.""",
            "correction_formula": """**Korrigiertes ΔSNR = Target-SNR − (Referenz-SNR + Korrektur)**\x20\x20\nEin positives ΔSNR spricht für das Target, ein negativer Wert für die Referenz.""",
            "correction_consequence": """Vor der Subtraktion werden zu jedem Referenz-SNR {offset:+.1f} dB addiert. Eine positive Korrektur senkt das korrigierte ΔSNR; eine negative Korrektur erhöht es.""",
            "hardware_calibration": """Kalibrierung bedeutet hier, eine wiederholbare Basisdifferenz zwischen den vollständigen Target- und Referenzpfaden zu bestimmen, während beide Pfade ein gemeinsames bekanntes Eingangssignal erhalten oder der beabsichtigte Unterschied unabhängig bekannt ist. Das ist keine absolute Messung von Antennengewinn, Wirkungsgrad oder Empfängerempfindlichkeit.""",
            "reference_calibration": """Der Offset ist hier eine empirische Basislinie für genau dieses Target–Referenz-Paar unter einem festgelegten Band, Aufbau und Betriebsdesign. Räumlich getrennte Stationen teilen weder Standort noch Funkweg; daher ist dies keine absolute Kalibrierung und darf nicht auf ein anderes Stationspaar oder einen anderen Aufbau übertragen werden.""",
            "establish_hardware_guidance": """Erzeuge eine Basislinie, bei der der beabsichtigte Unterschied fehlt oder unabhängig bekannt ist. Für RX speist du beide Pfade aus derselben stabilen Quelle oder Antenne. Für TX verwendest du eine unabhängig charakterisierte Basis mit gleicher Ausgangsleistung oder misst beide Pfade an derselben HF-Referenzebene. Halte den übrigen Aufbau konstant.\n\nWähle und dokumentiere nach dem Lauf genau einen ΔSNR-Schätzwert: Median oder arithmetisches Mittel aus **Stationsmediane** oder aus **Joint-Spots / geplante Paare**. Trage den beobachteten Wert Target − Referenz mit demselben Vorzeichen im nächsten Lauf als Referenzkorrektur ein—beispielsweise `+1,6 dB` bei einer Basislinie von `+1,6 dB`.\n\nAuf Stationsebene erhält jede Station eine Stimme; dies ist meist der bessere Standard für das stationsbalancierte WSPRadar-Ergebnis. Auf Spot-/Paarebene erhält jede Beobachtung eine Stimme, sodass Stationen mit vielen Reports dominieren können. Der Median ist robuster gegenüber Ausreißern und Schiefe. Das arithmetische Mittel kann bei einer annähernd symmetrischen Verteilung ohne einflussreiche Extremwerte sinnvoll sein, reagiert aber empfindlicher darauf. Wähle nach der beabsichtigten Gewichtung und Evidenzverteilung—nicht nach dem bevorzugten Ergebnis. Weichen die Schätzwerte deutlich voneinander ab, untersuche die Ursache, statt einen passenden Wert herauszugreifen; möglicherweise ist ein konstanter Offset nicht vertretbar. Wiederhole anschließend den Lauf oder vertausche die Pfade und prüfe, ob das korrigierte ΔSNR bei gemeinsamem Eingang plausibel um `0 dB` zentriert ist.""",
            "establish_reference_guidance": """Wähle für genau dieses Target–Referenz-Paar, Band und Betriebsdesign einen stabilen Basiszeitraum ohne bekannte Stationsänderung. Halte Kennungen, Umfang und Betriebsbedingungen konstant.\n\nWähle und dokumentiere nach dem Lauf genau einen ΔSNR-Schätzwert: Median oder arithmetisches Mittel aus **Stationsmediane** oder aus **Joint-Spots / geplante Paare**. Trage den beobachteten Wert Target − Referenz mit demselben Vorzeichen im nächsten Lauf als Referenzkorrektur ein—beispielsweise `+1,6 dB` bei einer Basislinie von `+1,6 dB`.\n\nAuf Stationsebene erhält jede Station eine Stimme; dies ist meist der bessere Standard für das stationsbalancierte WSPRadar-Ergebnis. Auf Spot-/Paarebene erhält jede Beobachtung eine Stimme, sodass Stationen mit vielen Reports dominieren können. Der Median ist robuster gegenüber Ausreißern und Schiefe. Das arithmetische Mittel kann bei einer annähernd symmetrischen Verteilung ohne einflussreiche Extremwerte sinnvoll sein, reagiert aber empfindlicher darauf. Wähle nach der beabsichtigten Gewichtung und Evidenzverteilung—nicht nach dem bevorzugten Ergebnis. Weichen die Schätzwerte deutlich voneinander ab, untersuche die Ursache, statt einen passenden Wert herauszugreifen; möglicherweise ist ein konstanter Offset nicht vertretbar. Prüfe die Stabilität über Stationen, Signalpegel und Zeit, wiederhole die Basislinie anschließend unter demselben Betriebsdesign und bestätige, dass das korrigierte ΔSNR plausibel um `0 dB` zentriert ist.""",
            "calibration_run_notice": """Offset-Ermittlungslauf: Die Referenzkorrektur ist auf 0,0 dB festgelegt. Führe die normale Compare-Analyse aus, um die unkorrigierte Basislinie Target − Referenz zu bestimmen. WSPRadar zeigt die verfügbaren Zusammenfassungen, wählt aber keinen Offset aus und wendet keinen an.""",
            "station_population_title": "Remote Stationsfilter",
            "station_population_body": """Diese Regler schließen telemetrieähnliche Kennungen oder Stationen aus, deren gemeldeter Locator sich im ausgewählten Zeitraum geändert hat. Solche Ausschlüsse können die Konsistenz von Identität und Standort verbessern, entfernen aber möglicherweise auch gültige Evidenz. Lege sie aus dem Versuchsdesign fest und nicht erst nach einem bevorzugten Ergebnis.""",
            "analysis_scope_title": "Analyseumfang",
            "analysis_scope_body": """Der Sonnenzustand wählt Beobachtungen anhand des Sonnenstands am Target-QTH aus. Die Maximalentfernung begrenzt, welche Gegenstationen in Analyse, Karte, Inspector und Export verbleiben. Diese Einstellungen verändern die analysierten Daten; die Maximalentfernung ist nicht nur eine Karten-Zoomstufe.""",
            "evidence_requirements_title": "Evidenzanforderungen",
            "compare_evidence_requirements_body": """Jede Station muss die gewählte Mindestzahl an Joint-Beobachtungen oder geplanten TX-Paaren liefern. Ein Kartensegment benötigt zusätzlich die gewählte Zahl qualifizierter Stationen. Höhere Schwellen verlangen mehr wiederholte Evidenz, verringern aber Stationszahl und geografische Abdeckung; sie beseitigen keine Ausbreitungseffekte und garantieren keine Messqualität.""",
            "success_evidence_requirements_body": """Jede Station muss die gewählte Mindestzahl unabhängig bestätigter Gelegenheiten liefern. Ein Kartensegment benötigt zusätzlich die gewählte Zahl qualifizierter Stationen. Höhere Schwellen verlangen mehr wiederholte Evidenz, verringern aber Stationszahl und geografische Abdeckung; sie beseitigen keine Ausbreitungseffekte und garantieren keine Messqualität.""",
            "general_active": """Die allgemeinen Einstellungen sind aktiv. Betrachte sie als Ausgangspunkt, nicht als Qualitätsurteil.""",
            "demo_active": """Die gespeicherten Einstellungen der geführten Demo sind aktiv. Sie gelten für dieses Beispiel, nicht allgemein.""",
            "included": "ausgeschlossen",
            "not_included": "einbezogen",
            "compare_evidence": """Joint-Evidenz ≥ {value} je Station; qualifizierte Stationen ≥ {stations} je Kartensegment""",
            "success_evidence": """bestätigte Gelegenheiten ≥ {value} je Station; qualifizierte Stationen ≥ {stations} je Kartensegment""",
            "review_question": "Fragestellung",
            "review_target": "Target",
            "review_target_value": "{callsign} bei {qth}",
            "review_reference": "Referenz",
            "review_tx_simultaneous_value": "{callsign} · {method}",
            "review_tx_sequential_value": "{method} · Wiederholintervall {repeat} min · Target {target:02d} UTC · Referenz {reference:02d} UTC",
            "review_band_window": "Band und UTC-Zeitraum",
            "review_correction": "Referenzseitige Korrektur",
            "review_population": "Remote Stationsfilter",
            "review_population_value": "Sonderkennungen {special}; Stationen mit Locatorwechsel {moving}",
            "review_scope": "Sonnenzustand und geografischer Umfang",
            "review_evidence": "Evidenzanforderungen",
            "review_result": "Ergebnistyp",
            "result_success": "Success — eigenständige Target-Werte",
            "result_compare": "Compare — relative Target–Referenz-Werte",
            "open_classic": "Klassische Eingabe öffnen",
            "continue": "Weiter",
            "configuration_changed": """Die Eingaben wurden seit dem letzten Lauf geändert. Starte die Analyse erneut, bevor du die Ergebnisse interpretierst.""",
        },
        "validation": {
            "use_case": "Wähle eine Fragestellung, bevor du fortfährst.",
            "target_and_window": "Gib eine gültige Target-Kennung und ein gültiges QTH ein, wähle ein Band und vervollständige den UTC-Messzeitraum.",
            "reference_design": "Vervollständige das gewählte Referenzdesign einschließlich der erforderlichen Kennung und des QTH, der Nachbarschaftseinstellungen oder des TX-Zeitplans.",
            "offset_calibration": "Wähle, ob keine Korrektur verwendet, eine ermittelte Korrektur eingegeben oder ein Offset-Ermittlungslauf eingerichtet werden soll.",
            "scope_and_evidence": "Wähle allgemeine, angepasste oder durch die Demo vorgegebene Umfangs- und Evidenzeinstellungen.",
            "flow_invalid": "Die Geführte Eingabe ist nicht verfügbar, weil ihre Ablaufkonfiguration ungültig ist: {error}",
        },
    },
}

def absolute_terms(t, mode):
    """Return mode-specific display terms for Absolute Success Rate views."""
    mode_key = "tx" if str(mode).upper().startswith("TX") else "rx"
    default_counter = "Other Signals" if mode_key == "tx" else "Elsewhere"
    default_short = "OS" if mode_key == "tx" else "E"

    counter = t.get(f"abs_{mode_key}_counter", default_counter)
    counter_short = t.get(f"abs_{mode_key}_counter_short", default_short)
    pair = t.get(f"abs_{mode_key}_pair", f"Target+{counter}")
    formula = t.get(f"abs_{mode_key}_formula", f"Target/(Target+{counter})")
    formula_spaced = t.get(
        f"abs_{mode_key}_formula_spaced",
        f"Target / (Target + {counter})",
    )
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
        "target": "Target",
        "target_short": "T",
        "target_column": t.get(f"abs_{mode_key}_target_column", "Target"),
        "counter": counter,
        "counter_short": counter_short,
        "counter_column": counter_column,
        "count_axis_label": t.get(f"abs_{mode_key}_count_axis", f"Target + {counter} count"),
        "counter_marker": t.get(f"abs_{mode_key}_counter_marker", counter_column),
        "counter_bar": counter,
        "pair": pair,
        "formula": formula,
        "formula_spaced": formula_spaced,
        "rate_column": rate_column,
        "no_evidence": t.get(f"abs_{mode_key}_no_evidence", f"No T/{counter_short} evidence"),
        "empty_evidence": t.get(f"abs_{mode_key}_empty_evidence", f"No {pair} evidence"),
        "subtext": t.get(
            f"abs_{mode_key}_subtext",
            f" (T=Target | {counter_short}={counter} | Click a row for evidence)",
        ),
    }
