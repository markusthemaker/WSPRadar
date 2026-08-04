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
    """Small selector model that never owns the station-row source frame."""

    valid_distances: list[str]
    valid_directions: list[str]


@dataclass
class CompareInspectorViewModel:
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
    station_table: pd.DataFrame

    def build_evidence_identities(self) -> pd.DataFrame:
        """Project Joint station identities without retaining a second table."""
        identities = self.station_table.loc[
            self.station_table[self.joint_column] > 0,
            [self.station_column, self.locator_column],
        ].copy()
        identities.columns = ["peer_sign", "peer_grid"]
        return identities


@dataclass
class OpportunityInspectorViewModel:
    confirmed_rows: pd.DataFrame
    confirmed_station_count: int
    target_station_count: int
    zero_target_station_count: int
    confirmed_opportunity_count: int
    target_count: int
    counter_count: int
    station_balanced_rate_pct: float
    observation_level_rate_pct: float
    weighting_gap_percentage_points: float
    median_opportunities_per_station: float
    summary_lines: list[str]
    full_station_table: pd.DataFrame
    export_column_renames: dict[str, str]
    station_column: str
    locator_column: str
    distance_column: str
    azimuth_column: str
    hit_column: str
    miss_column: str
    rate_column: str
    snr_column: str
    export_station_column: str
    export_locator_column: str

    def build_export_station_table(self) -> pd.DataFrame:
        """Return the canonical export schema without retaining a second table."""
        return self.full_station_table.rename(
            columns=self.export_column_renames,
        )


def _localized_integer(count: int, labels) -> str:
    """Format an integer with the presentation catalog's thousands separator."""
    formatted = f"{int(count):,}"
    separator = str(labels["fmt_results_thousands_separator"])
    return formatted if separator == "," else formatted.replace(",", separator)


def build_inspector_options(
    enriched_df: pd.DataFrame,
    *,
    max_peer_distance_km: float,
) -> InspectorOptionsViewModel:
    """Return options without retaining or copying the station-row source."""
    inspectable_mask = (
        enriched_df["SegmentID"].ne("Out of Bounds")
        & enriched_df["r_min"].lt(max_peer_distance_km)
    )
    valid_distances = sorted(
        [
            value
            for value in enriched_df.loc[
                inspectable_mask,
                "dist_label",
            ].dropna().unique()
        ],
        key=lambda value: int(value.strip("[]km").split("-")[0]),
    )
    valid_directions = sorted(
        [
            value
            for value in enriched_df.loc[
                inspectable_mask,
                "dir_name",
            ].dropna().unique()
            if value in COMPASS
        ],
        key=COMPASS.index,
    )
    return InspectorOptionsViewModel(
        valid_distances=valid_distances,
        valid_directions=valid_directions,
    )


def filter_inspector_scope(
    enriched_df: pd.DataFrame,
    *,
    max_peer_distance_km: float,
    selected_ranges,
    selected_directions,
) -> pd.DataFrame:
    """Materialize one selected scope directly from the shared station rows."""
    selected_mask = (
        enriched_df["SegmentID"].ne("Out of Bounds")
        & enriched_df["r_min"].lt(max_peer_distance_km)
    )
    if selected_ranges:
        selected_mask &= enriched_df["dist_label"].isin(selected_ranges)
    if selected_directions:
        selected_mask &= enriched_df["dir_name"].isin(selected_directions)
    return enriched_df.loc[selected_mask]


def compare_scope_availability(scope_rows: pd.DataFrame) -> tuple[bool, bool]:
    """Return whether a Benchmark scope contains paired or unpaired evidence."""
    has_joint_rows = bool((scope_rows["spot_count"] > 0).any())
    has_non_joint_rows = bool(
        ((scope_rows["count_only_u"] > 0) | (scope_rows["count_only_r"] > 0)).any()
    )
    return has_joint_rows, has_non_joint_rows


def _compare_labels(analysis_context, labels, *, is_sequential):
    """Return Target/Reference labels for fixed, local, and scheduled Benchmark."""
    target_call = analysis_context.callsign.upper()
    if (
        analysis_context.comparison_mode == COMPARISON_HARDWARE_AB
        and is_sequential
    ):
        target_name = labels["txt_target"]
        reference_header = labels["txt_reference"]
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
    is_sequential: bool,
    analysis_context,
    presentation_context,
) -> CompareInspectorViewModel:
    """Prepare Benchmark tables and paired-evidence identities without widgets."""
    labels = presentation_context.labels
    has_joint_rows, has_non_joint_rows = compare_scope_availability(scope_rows)
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
        labels["lbl_neighborhood"]
        if is_local_median
        else reference_header
    )
    if is_local_median:
        reference_header = labels["opt_local_median"]

    remote_label = (
        labels["txt_rx_stations"]
        if analysis_id.startswith("TX")
        else labels["txt_tx_stations"]
    )
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

    station_column = labels["tbl_col_rx"] if analysis_id.startswith("TX") else labels["tbl_col_tx"]
    station_type = station_column
    locator_column = labels["tbl_col_loc"]
    distance_column = labels["tbl_col_km"]
    azimuth_column = labels["tbl_col_az"]

    if is_sequential:
        joint_column = labels["tbl_col_joint_pairs"]
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
    sort_columns = (
        [joint_column, metric_column]
        if joint_column != metric_column
        else [joint_column]
    )
    station_table = station_table.sort_values(
        by=sort_columns,
        ascending=[False] * len(sort_columns),
        na_position="last",
    ).reset_index(drop=True)
    has_plot_data = bool(
        not values.empty
        or (
            scope_rows["count_only_u"].sum() > 0
            or scope_rows["count_only_r"].sum() > 0
        )
    )
    return CompareInspectorViewModel(
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
        station_table=station_table,
    )


def build_opportunity_inspector_view_model(
    scope_rows: pd.DataFrame,
    *,
    analysis_id: str,
    minimum_confirmed: int,
    presentation_context,
) -> OpportunityInspectorViewModel:
    """Prepare the scoped Success weighting summary and station table.

    Qualifying callsign/locator identities receive one vote in the
    station-balanced rate. Confirmed Target and counter outcomes receive one
    vote in the observation-level rate. The peer aggregates already exclude
    Target-only rows from that denominator, so row-level evidence is not
    retained by this display model.
    """
    labels = presentation_context.labels
    terms = presentation_context.absolute_terms(
        "TX" if analysis_id.startswith("TX") else "RX"
    )
    mode_key = "tx" if analysis_id.startswith("TX") else "rx"
    export_station_column = (
        labels["tbl_col_rx"]
        if analysis_id.startswith("TX")
        else labels["tbl_col_tx"]
    )
    station_column = labels[f"tbl_col_success_station_{mode_key}"]
    locator_column = labels["tbl_col_loc"]
    distance_column = labels["tbl_col_km"]
    azimuth_column = labels["tbl_col_az"]
    confirmed = scope_rows[scope_rows["eligible"] & scope_rows["rate_pct"].notna()].copy()
    hits = int(pd.to_numeric(confirmed["hits"], errors="coerce").fillna(0).sum())
    misses = int(
        pd.to_numeric(confirmed["misses"], errors="coerce").fillna(0).sum()
    )
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
    zero_target_station_count = int(
        (pd.to_numeric(confirmed["hits"], errors="coerce").fillna(0) == 0).sum()
    )
    target_station_count = int(len(confirmed) - zero_target_station_count)
    median_opportunities_per_station = (
        float(np.median(pd.to_numeric(confirmed_trials, errors="coerce")))
        if len(confirmed_trials)
        else np.nan
    )
    weighting_gap = (
        float(overall_rate - station_average_rate)
        if pd.notna(station_average_rate) and pd.notna(overall_rate)
        else np.nan
    )
    if confirmed.empty:
        summary_lines = [
            labels["txt_results_success_no_eligible"]
        ]
    else:
        summary_lines = [
            labels["fmt_results_success_station_summary"].format(
                success_label=terms["station_success"],
                success_station_count=_localized_integer(
                    target_station_count,
                    labels,
                ),
                counter_label=terms["station_counter"],
                counter_station_count=_localized_integer(
                    zero_target_station_count,
                    labels,
                ),
                station_balanced_rate=station_average_rate,
            ),
            labels["fmt_results_success_opportunity_summary"].format(
                success_label=terms["opportunity_success"],
                success_count=_localized_integer(hits, labels),
                counter_label=terms["opportunity_counter"],
                counter_count=_localized_integer(misses, labels),
                observation_level_rate=overall_rate,
            ),
        ]

    snr_column = labels["tbl_col_success_snr_display"]
    export_snr_column = labels["tbl_col_success_snr"]
    station_counter_column = (
        labels["tbl_col_success_counter_display_tx"]
        if mode_key == "tx"
        else terms["station_counter"]
    )
    rate_column = labels["tbl_col_success_rate"]
    display_station_table = confirmed[
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
    display_station_table.columns = [
        station_column,
        locator_column,
        distance_column,
        azimuth_column,
        terms["station_success"],
        station_counter_column,
        rate_column,
        snr_column,
    ]
    display_station_table[distance_column] = (
        display_station_table[distance_column].round(0).astype("Int64")
    )
    display_station_table[azimuth_column] = display_station_table[
        azimuth_column
    ].round(1)
    display_station_table[rate_column] = pd.to_numeric(
        display_station_table[rate_column], errors="coerce"
    ).round(1)
    display_station_table[snr_column] = pd.to_numeric(
        display_station_table[snr_column], errors="coerce"
    ).round(1)
    full_station_table = display_station_table.sort_values(
        [terms["station_success"], station_counter_column, rate_column],
        ascending=[False, False, False],
        na_position="last",
    ).reset_index(drop=True)

    export_column_renames = {
        station_column: export_station_column,
        terms["station_success"]: terms["target_column"],
        station_counter_column: terms["counter_column"],
        rate_column: terms["rate_column"],
        snr_column: export_snr_column,
    }
    return OpportunityInspectorViewModel(
        confirmed_rows=confirmed,
        confirmed_station_count=len(confirmed),
        target_station_count=target_station_count,
        zero_target_station_count=zero_target_station_count,
        confirmed_opportunity_count=hits + misses,
        target_count=hits,
        counter_count=misses,
        station_balanced_rate_pct=float(station_average_rate),
        observation_level_rate_pct=float(overall_rate),
        weighting_gap_percentage_points=weighting_gap,
        median_opportunities_per_station=median_opportunities_per_station,
        summary_lines=summary_lines,
        full_station_table=full_station_table,
        export_column_renames=export_column_renames,
        station_column=station_column,
        locator_column=locator_column,
        distance_column=distance_column,
        azimuth_column=azimuth_column,
        hit_column=terms["station_success"],
        miss_column=station_counter_column,
        rate_column=rate_column,
        snr_column=snr_column,
        export_station_column=export_station_column,
        export_locator_column=locator_column,
    )
