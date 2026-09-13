"""Pure localized labels and interpretation text for Inspector presentation."""

import numpy as np
import pandas as pd

from ui.result_hierarchy import selected_station_context


def segment_temporal_figure_title(title, analysis_id, selected_segment, t):
    """Build the localized Benchmark-temporal title with its scope text."""
    original_title = str(title)
    _, separator, comparison_title = original_title.partition(":")
    if not separator:
        comparison_title = original_title
    if str(analysis_id).upper().startswith("TX"):
        temporal_prefix = t["fig_tx_comp_temporal_prefix"]
    else:
        temporal_prefix = t["fig_rx_comp_temporal_prefix"]
    return (
        f"{temporal_prefix}: {comparison_title.strip()} - {selected_segment}"
    )


def success_figure_labels(translations, analysis_id):
    """Return localized labels for the pure Performance evidence recipes."""
    is_tx = str(analysis_id).upper().startswith("TX")
    mode_suffix = "tx" if is_tx else "rx"
    return {
        "reach_title": translations[
            f"fig_success_reach_title_{mode_suffix}"
        ],
        "reach_y": translations[
            f"fig_success_reach_y_{mode_suffix}"
        ],
        "consistency_title": translations[
            f"fig_success_consistency_title_{mode_suffix}"
        ],
        "snr_distance_title": translations[
            f"fig_success_snr_distance_title_{mode_suffix}"
        ],
        "distance_x": translations["fig_success_distance_x"],
        "rate_y": translations["fig_success_rate_y"],
        "snr_y": translations["fig_success_snr_y"],
        "confirmed_opportunities": translations[
            "fig_success_confirmed_opportunities"
        ],
        "qualifying_stations": translations[
            "fig_success_qualifying_stations"
        ],
        "target_stations": translations[
            f"map_success_{mode_suffix}_station_target"
        ],
        "successful_snr_stations": translations[
            "fig_success_successful_snr_stations"
        ],
        "station_balanced": translations["fig_success_station_balanced"],
        "observation_level": translations[
            "fig_success_observation_level"
        ],
        "target_evidence": translations[
            f"success_{mode_suffix}_opportunity_success"
        ],
        "counter_evidence": translations[
            f"success_{mode_suffix}_opportunity_counter"
        ],
        "median": translations["fig_success_median"],
        "iqr": translations["fig_success_iqr"],
        "two_station_range": translations[
            "fig_success_two_station_range"
        ],
        "support": translations["fig_success_support"],
        "support_title": translations["fig_success_support_title"],
        "bin_width": translations["fig_success_bin_width"],
        "locator_precision_note": translations[
            "fig_success_locator_precision_note"
        ],
        "thousands_separator": translations[
            "fmt_results_thousands_separator"
        ],
        "snr_chronological_title": translations[
            f"fig_success_snr_chronological_title_{mode_suffix}"
        ],
        "snr_utc_hour_title": translations[
            f"fig_success_snr_utc_hour_title_{mode_suffix}"
        ],
        "evidence_chronological_title": translations[
            "fig_success_evidence_chronological_title"
        ],
        "evidence_utc_hour_title": translations[
            "fig_success_evidence_utc_hour_title"
        ],
        "station_vote_y": translations[
            f"fig_success_station_votes_y_{mode_suffix}"
        ],
        "station_support_folded_y": translations[
            f"fig_success_station_support_folded_y_{mode_suffix}"
        ],
        "opportunity_y": translations[
            "fig_success_opportunities_y"
        ],
        "opportunity_folded_y": translations[
            "fig_success_opportunities_folded_y"
        ],
        "rate_legend": translations["fig_success_rate_legend"],
        "time_x": translations["fig_success_time_x"],
        "utc_hour_x": translations["fig_success_utc_hour_x"],
        "snr_anomaly_y": translations[
            f"fig_success_snr_anomaly_y_{mode_suffix}"
        ],
        "snr_density": translations["fig_success_snr_density"],
        "station_baseline": translations[
            "fig_success_station_baseline"
        ],
        "bin_median_chronological": translations[
            "fig_success_bin_median_chronological"
        ],
        "bin_median_folded": translations[
            "fig_success_bin_median_folded"
        ],
        "bin_iqr": translations["fig_temporal_bin_iqr"],
        "snr_anomaly_unavailable": translations[
            "fig_success_snr_anomaly_unavailable"
        ],
        "temporal_unavailable": translations[
            "fig_success_temporal_unavailable"
        ],
        "utc_dates_folded": translations[
            "fig_success_utc_dates_folded"
        ],
        "selected_snr_chronological_title": translations[
            "fig_success_selected_snr_chronological_title"
        ],
        "selected_snr_utc_hour_title": translations[
            "fig_success_selected_snr_utc_hour_title"
        ],
        "selected_snr_y": translations[
            "fig_success_selected_temporal_snr_y"
        ],
        "selected_snr_density": translations[
            "fig_success_selected_snr_density"
        ],
        "selected_bin_median_chronological": translations[
            "fig_success_selected_bin_median"
        ],
        "selected_bin_median_folded": translations[
            "fig_success_selected_folded_median"
        ],
        "selected_snr_unavailable": translations[
            "fig_success_selected_snr_unavailable"
        ],
    }


def compare_coverage_figure_labels(
    translations,
    analysis_id,
    *,
    is_sequential,
    target_only_label,
    joint_label,
    reference_only_label,
):
    """Return semantic labels for Benchmark evidence-coverage recipes."""
    if (
        target_only_label is None
        or joint_label is None
        or reference_only_label is None
    ):
        raise ValueError(
            "Benchmark temporal outcome labels must be localized strings."
        )
    mode_suffix = (
        "tx"
        if str(analysis_id).upper().startswith("TX")
        else "rx"
    )
    if is_sequential:
        unit_y = translations["fig_compare_coverage_unit_y_scheduled"]
        unit_folded_y = translations[
            "fig_compare_coverage_unit_folded_y_scheduled"
        ]
        selected_title_unit = translations[
            "fig_selected_compare_coverage_unit_scheduled"
        ]
        selected_unit_y = unit_y
        selected_unit_folded_y = unit_folded_y
        gate_note = translations[
            "fig_compare_coverage_gate_scheduled"
        ]
    else:
        unit_y = translations[
            f"fig_compare_coverage_unit_y_{mode_suffix}"
        ]
        unit_folded_y = translations[
            f"fig_compare_coverage_unit_folded_y_{mode_suffix}"
        ]
        selected_title_unit = translations[
            "fig_selected_compare_coverage_unit_simultaneous"
        ]
        selected_unit_y = translations[
            "fig_selected_compare_coverage_unit_y_simultaneous"
        ]
        selected_unit_folded_y = translations[
            "fig_selected_compare_coverage_unit_folded_y_simultaneous"
        ]
        gate_note = translations[
            "fig_compare_coverage_gate_simultaneous"
        ]
    return {
        "utc_dates_folded": translations["fig_segment_dates_folded"],
        "folded_unavailable": translations[
            "fig_compare_coverage_folded_unavailable"
        ],
        "time_x": translations["fig_segment_chronological_x"],
        "utc_hour_x": translations["fig_segment_utc_hour_x"],
        "evidence_chronological_title": translations[
            "fig_compare_coverage_chronological_title"
        ],
        "evidence_utc_hour_title": translations[
            "fig_compare_coverage_utc_hour_title"
        ],
        "station_vote_y": translations[
            f"fig_compare_coverage_station_y_{mode_suffix}"
        ],
        "station_folded_y": translations[
            f"fig_compare_coverage_station_folded_y_{mode_suffix}"
        ],
        "unit_y": unit_y,
        "unit_folded_y": unit_folded_y,
        "joint_share_y": translations["fig_compare_joint_share_y"],
        "station_joint_share": translations[
            "fig_compare_joint_share_station"
        ],
        "outcome_joint_share": translations[
            "fig_compare_joint_share_outcome"
        ],
        "target_only": str(target_only_label),
        "joint": str(joint_label),
        "reference_only": str(reference_only_label),
        "gate_note": gate_note,
        "selected_chronological_title": translations[
            "fig_selected_compare_coverage_chronological_title"
        ],
        "selected_utc_hour_title": translations[
            "fig_selected_compare_coverage_utc_hour_title"
        ],
        "selected_title_unit": selected_title_unit,
        "selected_unit_y": selected_unit_y,
        "selected_unit_folded_y": selected_unit_folded_y,
        "selected_joint_share": translations[
            "fig_selected_compare_joint_share"
        ],
    }


def compare_temporal_coverage_title(
    translations,
    analysis_id,
    callsign,
):
    """Build the localized Benchmark Temporal Evidence Coverage title."""
    mode_suffix = (
        "tx"
        if str(analysis_id).upper().startswith("TX")
        else "rx"
    )
    return translations[f"fig_compare_coverage_title_{mode_suffix}"].format(
        callsign=str(callsign).strip().upper(),
    )


def success_temporal_figure_title(
    callsign,
    analysis_id,
    translations,
    *,
    figure_kind,
):
    """Build one localized Performance temporal SNR or evidence figure title."""
    mode_suffix = (
        "tx"
        if str(analysis_id).upper().startswith("TX")
        else "rx"
    )
    if figure_kind == "snr":
        title_key = f"fig_success_temporal_snr_title_{mode_suffix}"
    elif figure_kind == "evidence":
        title_key = f"fig_success_temporal_title_{mode_suffix}"
    else:
        raise ValueError(
            "Performance temporal figure kind must be 'snr' or 'evidence'."
        )
    return translations[
        title_key
    ].format(
        callsign=str(callsign).strip().upper(),
    )


def selected_success_temporal_figure_title(
    station,
    locator,
    analysis_id,
    translations,
    *,
    figure_kind,
):
    """Build one localized figure title for a selected Performance station."""
    mode_suffix = (
        "tx"
        if str(analysis_id).upper().startswith("TX")
        else "rx"
    )
    if figure_kind == "snr":
        title_key = (
            f"fig_success_selected_station_snr_title_{mode_suffix}"
        )
    elif figure_kind == "evidence":
        title_key = (
            f"fig_success_selected_station_temporal_title_{mode_suffix}"
        )
    else:
        raise ValueError(
            "Selected Performance figure kind must be 'snr' or 'evidence'."
        )
    return translations[title_key].format(
        station=str(station).strip().upper(),
        locator=str(locator).strip().upper(),
    )


def folded_utc_hour_panel_title(t):
    """Return the complete localized title for the fixed one-hour folded panel."""
    return t["fig_segment_utc_hour_title"]


def segment_summary_lines(
    station_summary,
    spot_summary,
):
    """Return the available station- and observation-level metric summaries."""
    return [
        summary
        for summary in (station_summary, spot_summary)
        if summary
    ]


def format_localized_integer(count, translations):
    """Format one evidence count with the active presentation separator."""
    formatted = f"{int(count):,}"
    separator = str(translations["fmt_results_thousands_separator"])
    return formatted if separator == "," else formatted.replace(",", separator)


def format_localized_decimal(value, translations, *, decimals=1):
    """Format one finite display value without changing its stored precision."""
    numeric_value = float(value)
    if not np.isfinite(numeric_value):
        return "—"
    formatted = f"{numeric_value:.{int(decimals)}f}".replace("-", "−")
    if translations["fmt_results_thousands_separator"] == ".":
        formatted = formatted.replace(".", ",")
    return formatted


def format_summary_count(count):
    """Format an integer summary count with an apostrophe thousands separator."""
    return f"{int(count):,}".replace(",", "'")


def compare_metric_distribution_summary(
    values,
    template,
    *,
    total_count=None,
    joint_count=None,
    joint_label="Joint",
):
    """Format one Benchmark distribution summary with optional outcome counts."""
    numeric_values = np.asarray(values, dtype=float)
    numeric_values = numeric_values[np.isfinite(numeric_values)]
    if len(numeric_values) == 0:
        return None

    count_context = ""
    if total_count is not None and joint_count is not None:
        count_context = (
            f" (n={format_summary_count(total_count)}; "
            f"{joint_label}={format_summary_count(joint_count)})"
        )

    return template.format(
        count_context=count_context,
        median=f"{float(np.median(numeric_values)):+.1f}",
        mean=f"{float(np.mean(numeric_values)):+.1f}",
    )


def selected_evidence_figure_title(
    station_identities,
    evidence_count,
    *,
    analysis_id,
    is_sequential,
    translations,
    allow_multiple=False,
):
    """Build a localized selected-station figure title from semantic evidence."""
    heading = translations["hdr_results_selected_station_evidence"]
    selection_context = selected_station_context(
        station_identities,
        evidence_count,
        analysis_id=analysis_id,
        is_sequential=is_sequential,
        translations=translations,
        allow_multiple=allow_multiple,
    )
    return translations[
        "fmt_results_selected_station_evidence_title"
    ].format(
        heading=heading,
        selection_context=selection_context,
    )


def format_drilldown_focus_utc(value):
    """Format one UTC bound compactly while retaining non-minute precision."""
    timestamp = pd.Timestamp(value).tz_convert("UTC")
    if timestamp.second or timestamp.microsecond or timestamp.nanosecond:
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp.strftime("%Y-%m-%d %H:%M")


def drilldown_focus_title(identity_label, focus_window, translations):
    """Return the compact selected-path identity plus exact focused interval."""
    if focus_window is None:
        return str(identity_label)
    return translations["fmt_drilldown_zoom_time_window"].format(
        identity=str(identity_label),
        start=format_drilldown_focus_utc(focus_window.start_utc),
        end=format_drilldown_focus_utc(focus_window.end_utc),
    )


def drilldown_focus_time_bin(focus_window):
    """Return the cycle-sized companion-profile bin for one focused view."""
    if focus_window is None:
        return None
    return "2m"


def selected_success_context_line(recipe, translations):
    """Format complete-run context for one selected Performance path."""
    summary = dict((recipe or {}).get("selected_station_summary") or {})
    confirmed_opportunities = int(
        summary.get("confirmed_opportunities", 0)
    )
    opportunity_unit = translations[
        "unit_confirmed_opportunity_singular"
        if confirmed_opportunities == 1
        else "unit_confirmed_opportunity_plural"
    ]
    distance_km = summary.get("distance_km", np.nan)
    distance_text = (
        format_localized_integer(round(float(distance_km)), translations)
        if pd.notna(distance_km) and np.isfinite(float(distance_km))
        else "—"
    )
    azimuth_degrees = summary.get("azimuth_degrees", np.nan)
    azimuth_text = format_localized_decimal(
        azimuth_degrees,
        translations,
        decimals=0,
    )
    direction = str(summary.get("direction", "")).strip().upper()
    localized_east = translations["abbr_compass_east"]
    localized_direction = direction.replace("E", localized_east)
    successful_snr_median_db = summary.get(
        "successful_snr_median_db",
        np.nan,
    )
    median_snr_text = (
        f"{format_localized_decimal(
            successful_snr_median_db,
            translations,
        )} dB"
        if pd.notna(successful_snr_median_db)
        and np.isfinite(float(successful_snr_median_db))
        else "—"
    )
    return translations["fmt_success_selected_context"].format(
        station=str(summary.get("peer_sign", "")).strip().upper(),
        locator=str(summary.get("peer_grid", "")).strip().upper(),
        distance_km=distance_text,
        azimuth_degrees=azimuth_text,
        direction=localized_direction,
        confirmed_opportunities=format_localized_integer(
            confirmed_opportunities,
            translations,
        ),
        opportunity_unit=opportunity_unit,
        success_rate=format_localized_decimal(
            summary.get("success_rate_pct", np.nan),
            translations,
        ),
        median_snr=median_snr_text,
    )


def selection_summary(selection, all_option, item_kind, translations):
    """Build a compact scope label without losing single-selection detail."""
    if not selection:
        return all_option
    limit = 2 if item_kind == "range" else 4
    if len(selection) <= limit:
        return ", ".join(selection)
    template_key = (
        "fmt_results_selected_range_count"
        if item_kind == "range"
        else "fmt_results_selected_direction_count"
    )
    return translations[template_key].format(count=len(selection))
