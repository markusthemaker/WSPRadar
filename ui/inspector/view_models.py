"""Pure view-model preparation for compare and opportunity inspectors."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from config import COMPASS
from core.analysis_context import (
    COMPARISON_HARDWARE_AB,
    COMPARISON_LOCAL_NEIGHBORHOOD,
    LOCAL_BENCHMARK_MEDIAN,
)


@dataclass
class InspectorOptionsViewModel:
    source_rows: pd.DataFrame
    valid_distances: list[str]
    valid_directions: list[str]


@dataclass
class CompareInspectorViewModel:
    scope_rows: pd.DataFrame
    values: pd.Series
    has_joint_rows: bool
    has_non_joint_rows: bool
    has_plot_data: bool
    station_column: str
    station_type: str
    locator_column: str
    distance_column: str
    azimuth_column: str
    joint_column: str | None
    target_name: str
    reference_header: str
    yield_reference_header: str
    target_only_label: str
    reference_only_label: str
    is_local_median: bool
    scope_summary: str
    full_station_table: pd.DataFrame
    station_table: pd.DataFrame
    evidence_identities: pd.DataFrame


@dataclass
class OpportunityInspectorViewModel:
    confirmed_rows: pd.DataFrame
    evidence_rows: pd.DataFrame
    summary_lines: list[str]
    full_station_table: pd.DataFrame
    station_column: str
    locator_column: str
    distance_column: str
    azimuth_column: str
    hit_column: str
    miss_column: str
    rate_column: str
    snr_column: str


def build_inspector_options(
    enriched_df: pd.DataFrame,
    *,
    max_peer_distance_km: float,
) -> InspectorOptionsViewModel:
    """Return inspectable options inside the half-open peer-distance scope."""
    source_rows = enriched_df[enriched_df["SegmentID"] != "Out of Bounds"].copy()
    source_rows = source_rows[
        source_rows["r_min"] < max_peer_distance_km
    ]
    valid_distances = sorted(
        [value for value in source_rows["dist_label"].dropna().unique()],
        key=lambda value: int(value.strip("[]km").split("-")[0]),
    )
    valid_directions = sorted(
        [
            value
            for value in source_rows["dir_name"].dropna().unique()
            if value in COMPASS
        ],
        key=COMPASS.index,
    )
    return InspectorOptionsViewModel(
        source_rows=source_rows,
        valid_distances=valid_distances,
        valid_directions=valid_directions,
    )


def filter_inspector_scope(
    source_rows: pd.DataFrame,
    *,
    selected_ranges,
    selected_directions,
) -> pd.DataFrame:
    """Return the selected Cartesian distance/direction scope."""
    scope_rows = source_rows.copy()
    if selected_ranges:
        scope_rows = scope_rows[scope_rows["dist_label"].isin(selected_ranges)]
    if selected_directions:
        scope_rows = scope_rows[scope_rows["dir_name"].isin(selected_directions)]
    return scope_rows


def compare_scope_availability(scope_rows: pd.DataFrame, *, is_compare: bool) -> tuple[bool, bool]:
    if not is_compare or "count_only_u" not in scope_rows.columns:
        return False, False
    has_joint_rows = bool((scope_rows["spot_count"] > 0).any())
    has_non_joint_rows = bool(
        ((scope_rows["count_only_u"] > 0) | (scope_rows["count_only_r"] > 0)).any()
    )
    return has_joint_rows, has_non_joint_rows


def _compare_labels(analysis_context, labels, *, is_sequential):
    """Return Target/Reference labels for fixed, local, and scheduled Compare."""
    target_call = analysis_context.callsign.upper()
    if (
        analysis_context.comparison_mode == COMPARISON_HARDWARE_AB
        and is_sequential
    ):
        target_name = labels.get("txt_target", "Target")
        reference_header = labels.get("txt_reference", "Reference")
        target_only_label = labels["leg_only_me"].format(callsign=target_name)
        reference_only_label = labels["leg_only_ref"].format(
            ref_callsign=reference_header
        )
    else:
        target_only_label = labels["leg_only_me"].format(callsign=target_call)
        target_name = target_call
        if analysis_context.comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD:
            reference_only_label = labels["leg_only_ref_radius"]
            reference_header = "Best Ref"
        else:
            reference_header = analysis_context.reference_callsign.upper()
            reference_only_label = labels["leg_only_ref"].format(
                ref_callsign=reference_header
            )
    return target_name, reference_header, target_only_label, reference_only_label


def build_compare_inspector_view_model(
    scope_rows: pd.DataFrame,
    *,
    analysis_id: str,
    is_compare: bool,
    is_sequential: bool,
    show_non_joint: bool,
    analysis_context,
    presentation_context,
) -> CompareInspectorViewModel:
    """Prepare compare/legacy-absolute tables and evidence identities without widgets."""
    labels = presentation_context.labels
    has_joint_rows, has_non_joint_rows = compare_scope_availability(
        scope_rows,
        is_compare=is_compare,
    )
    values = scope_rows["stat_val"].dropna()
    target_name, reference_header, target_only_label, reference_only_label = (
        _compare_labels(
            analysis_context,
            labels,
            is_sequential=is_sequential,
        )
    )
    is_local_median = (
        analysis_context.comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD
        and analysis_context.local_benchmark == LOCAL_BENCHMARK_MEDIAN
    )
    yield_reference_header = (
        labels.get("lbl_neighborhood", "Neighborhood")
        if is_local_median
        else reference_header
    )
    if is_local_median:
        reference_header = labels.get("opt_local_median", "Local Median Neighborhood")

    remote_label = (
        labels["txt_rx_stations"]
        if analysis_id.startswith("TX")
        else labels["txt_tx_stations"]
    )
    if is_compare and "count_only_u" in scope_rows.columns:
        if is_sequential:
            scope_summary = (
                f"Both (Async): {len(scope_rows[(scope_rows['count_only_u'] > 0) & (scope_rows['count_only_r'] > 0)])}"
                f"  |  {target_only_label}: {int(scope_rows['count_only_u'].sum())}"
                f"  |  {reference_only_label}: {int(scope_rows['count_only_r'].sum())}"
                f"  |  {labels['txt_remote']} {remote_label}: {len(scope_rows)}"
            )
        else:
            joint_rows = scope_rows[scope_rows["spot_count"] > 0]
            scope_summary = (
                f"{labels['txt_joint_decodes']}: {int(scope_rows['spot_count'].sum())}"
                f"  |  {target_only_label}: {int(scope_rows['count_only_u'].sum())}"
                f"  |  {reference_only_label}: {int(scope_rows['count_only_r'].sum())}"
                f"  |  {labels['txt_joint']} {remote_label}: {len(joint_rows)}"
                f"  |  {labels['txt_remote']} {remote_label}: {len(scope_rows)}"
            )
    else:
        scope_summary = (
            f"{labels['txt_total_decodes']}: {int(scope_rows['spot_count'].sum())}"
            f"  |  {labels['txt_remote']} {remote_label}: {len(scope_rows)}"
        )

    station_column = labels["tbl_col_rx"] if analysis_id.startswith("TX") else labels["tbl_col_tx"]
    station_type = station_column
    locator_column = labels["tbl_col_loc"]
    distance_column = labels["tbl_col_km"]
    azimuth_column = labels["tbl_col_az"]

    if not is_compare:
        station_table = scope_rows[
            ["peer_sign", "peer_grid", "calc_dist", "calc_azimuth", "spot_count", "stat_val"]
        ].copy()
        station_table.columns = [
            station_column,
            locator_column,
            distance_column,
            azimuth_column,
            labels["tbl_col_spots"],
            labels["tbl_col_med_snr"],
        ]
        joint_column = None
    else:
        if is_sequential:
            joint_column = labels.get("tbl_col_joint_pairs", "Joint Pairs")
            source_columns = [
                "peer_sign",
                "peer_grid",
                "calc_dist",
                "calc_azimuth",
                "joint_pairs_count",
                "count_only_u",
                "count_only_r",
                "stat_val",
            ]
        else:
            joint_column = labels["tbl_col_joint"]
            source_columns = [
                "peer_sign",
                "peer_grid",
                "calc_dist",
                "calc_azimuth",
                "spot_count",
                "count_only_u",
                "count_only_r",
                "stat_val",
            ]
        station_table = scope_rows[source_columns].copy()
        station_table.columns = [
            station_column,
            locator_column,
            distance_column,
            azimuth_column,
            joint_column,
            labels["tbl_col_only_u"].format(callsign=target_name),
            reference_only_label,
            labels["tbl_col_med_delta"],
        ]

    station_table[distance_column] = station_table[distance_column].round(0).astype("Int64")
    station_table[azimuth_column] = station_table[azimuth_column].round(1)
    metric_column = station_table.columns[-1]
    station_table[metric_column] = pd.to_numeric(
        station_table[metric_column],
        errors="coerce",
    ).round(1)
    if is_compare:
        sort_columns = (
            [joint_column, metric_column]
            if joint_column != metric_column
            else [joint_column]
        )
    else:
        spots_column = labels["tbl_col_spots"]
        sort_columns = (
            [spots_column, metric_column]
            if spots_column != metric_column
            else [spots_column]
        )
    full_station_table = station_table.sort_values(
        by=sort_columns,
        ascending=[False] * len(sort_columns),
        na_position="last",
    ).reset_index(drop=True)
    if is_compare and not show_non_joint and joint_column in station_table.columns:
        station_table = station_table[station_table[joint_column] > 0]
    station_table = station_table.sort_values(
        by=sort_columns,
        ascending=[False] * len(sort_columns),
        na_position="last",
    ).reset_index(drop=True)

    evidence_rows = station_table
    if is_compare and joint_column in station_table.columns:
        evidence_rows = station_table[station_table[joint_column] > 0]
    evidence_identities = evidence_rows[[station_column, locator_column]].copy()
    evidence_identities.columns = ["peer_sign", "peer_grid"]
    has_plot_data = bool(
        not values.empty
        or (
            is_compare
            and "count_only_u" in scope_rows.columns
            and (
                scope_rows["count_only_u"].sum() > 0
                or scope_rows["count_only_r"].sum() > 0
            )
        )
    )
    return CompareInspectorViewModel(
        scope_rows=scope_rows,
        values=values,
        has_joint_rows=has_joint_rows,
        has_non_joint_rows=has_non_joint_rows,
        has_plot_data=has_plot_data,
        station_column=station_column,
        station_type=station_type,
        locator_column=locator_column,
        distance_column=distance_column,
        azimuth_column=azimuth_column,
        joint_column=joint_column,
        target_name=target_name,
        reference_header=reference_header,
        yield_reference_header=yield_reference_header,
        target_only_label=target_only_label,
        reference_only_label=reference_only_label,
        is_local_median=is_local_median,
        scope_summary=scope_summary,
        full_station_table=full_station_table,
        station_table=station_table,
        evidence_identities=evidence_identities,
    )


def build_opportunity_inspector_view_model(
    scope_rows: pd.DataFrame,
    evidence_rows: pd.DataFrame,
    *,
    analysis_id: str,
    selected_segment: str,
    minimum_confirmed: int,
    presentation_context,
) -> OpportunityInspectorViewModel:
    """Prepare opportunity summary and station table without Streamlit state."""
    labels = presentation_context.labels
    terms = presentation_context.absolute_terms(
        "TX" if analysis_id.startswith("TX") else "RX"
    )
    station_column = labels["tbl_col_rx"] if analysis_id.startswith("TX") else labels["tbl_col_tx"]
    locator_column = labels["tbl_col_loc"]
    distance_column = labels["tbl_col_km"]
    azimuth_column = labels["tbl_col_az"]
    confirmed = scope_rows[scope_rows["eligible"] & scope_rows["rate_pct"].notna()].copy()
    confirmed_evidence = evidence_rows.merge(
        confirmed[["peer_sign", "peer_grid"]].drop_duplicates(),
        on=["peer_sign", "peer_grid"],
        how="inner",
    )
    hits = int(confirmed_evidence["hit"].sum())
    misses = int(confirmed_evidence["miss"].sum())
    overall_rate = 100.0 * hits / (hits + misses) if hits + misses else np.nan
    confirmed_trials = confirmed["hits"] + confirmed["misses"]
    confirmed_station_rates = np.where(
        confirmed_trials > 0,
        100.0 * confirmed["hits"] / confirmed_trials,
        np.nan,
    )
    station_average_rate = (
        float(np.nanmean(confirmed_station_rates))
        if len(confirmed_station_rates)
        else np.nan
    )
    summary_lines = [
        labels.get(
            "txt_abs_selected_segment",
            "Selected Segment: {segment}",
        ).format(segment=selected_segment),
        labels.get(
            "txt_abs_evidence_summary",
            "Evidence ({pair} >= {threshold} per station): Target {target} | {counter} {counter_count}",
        ).format(
            pair=terms["pair"],
            threshold=int(minimum_confirmed),
            target=hits,
            counter=terms["counter"],
            counter_count=misses,
            hits=hits,
            misses=misses,
        ),
    ]
    if pd.notna(station_average_rate) and pd.notna(overall_rate):
        summary_lines.append(
            labels.get(
                "txt_abs_rate_summary",
                "Success Rate {formula}: Average by Station {station_average:.1f}% | Observation-Level {overall:.1f}%",
            ).format(
                formula=terms["formula"],
                station_average=station_average_rate,
                overall=overall_rate,
            )
        )
    else:
        summary_lines.append(
            labels.get(
                "txt_abs_no_eligible",
                "No station meets the {pair} threshold in this scope.",
            ).format(pair=terms["pair"])
        )

    snr_column = labels.get("tbl_col_success_snr", "Median Target SNR (dB @ 1W)")
    station_table = confirmed[
        [
            "peer_sign",
            "peer_grid",
            "calc_dist",
            "calc_azimuth",
            "hits",
            "misses",
            "rate_pct",
            "successful_snr_median",
        ]
    ].copy()
    station_table.columns = [
        station_column,
        locator_column,
        distance_column,
        azimuth_column,
        terms["target_column"],
        terms["counter_column"],
        terms["rate_column"],
        snr_column,
    ]
    station_table[distance_column] = station_table[distance_column].round(0).astype("Int64")
    station_table[azimuth_column] = station_table[azimuth_column].round(1)
    station_table[terms["rate_column"]] = pd.to_numeric(
        station_table[terms["rate_column"]], errors="coerce"
    ).round(1)
    station_table[snr_column] = pd.to_numeric(
        station_table[snr_column], errors="coerce"
    ).round(1)
    full_station_table = station_table.sort_values(
        [terms["target_column"], terms["counter_column"], terms["rate_column"]],
        ascending=[False, False, False],
        na_position="last",
    ).reset_index(drop=True)
    return OpportunityInspectorViewModel(
        confirmed_rows=confirmed,
        evidence_rows=confirmed_evidence,
        summary_lines=summary_lines,
        full_station_table=full_station_table,
        station_column=station_column,
        locator_column=locator_column,
        distance_column=distance_column,
        azimuth_column=azimuth_column,
        hit_column=terms["target_column"],
        miss_column=terms["counter_column"],
        rate_column=terms["rate_column"],
        snr_column=snr_column,
    )
