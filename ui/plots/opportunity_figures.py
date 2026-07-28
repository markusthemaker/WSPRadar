"""Opportunity evidence figures for WSPRadar."""

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.dates as mdates

from config import APP_VERSION
from core.matplotlib_runtime import create_agg_figure, synchronized_matplotlib
from core.opportunity_engine import (
    opportunity_utc_from_time_slot,
    opportunity_rate_scale_max,
)
from ui.plots.evidence_figures import (
    EVIDENCE_AGG_COLOR,
    EVIDENCE_DENSITY_MAX,
    EVIDENCE_DENSITY_MIN,
    EVIDENCE_HEATMAP_CMAP,
    METRIC_FONT_FAMILY,
    METRIC_FIGURE_TITLE_FONTSIZE,
    METRIC_FOOTER_FONTSIZE,
    METRIC_LEGEND_FONTSIZE,
    METRIC_PANEL_TITLE_FONTSIZE,
    METRIC_TICK_LABEL_FONTSIZE,
    SEGMENT_FIGURE_BOTTOM,
    SEGMENT_FIGURE_FOOTER_Y,
    SEGMENT_TEMPORAL_COLORBAR_FRACTION,
    SEGMENT_TEMPORAL_COLORBAR_PAD,
    SEGMENT_TEMPORAL_COLUMN_SPACE,
    SEGMENT_TEMPORAL_COLUMN_WIDTH_RATIOS,
    SEGMENT_TEMPORAL_FIGURE_LEFT,
    SEGMENT_TEMPORAL_FIGURE_RIGHT,
    SEGMENT_TEMPORAL_FIGURE_SIZE_INCHES,
    SEGMENT_TEMPORAL_FIGURE_TOP,
    _place_metric_legend,
    _set_metric_axis_labels,
    _set_temporal_panel_title,
    _style_evidence_axis,
    _time_agg_minutes,
)
SUCCESS_TEMPORAL_TIME_BINS = ("1h", "2h", "3h", "6h", "12h", "24h")
SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE = "active_scope"
SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION = "selected_station"
SUCCESS_TEMPORAL_POPULATION_MODES = frozenset(
    {
        SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
        SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    }
)
SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE = "station_relative_deviation"
SUCCESS_SNR_REPRESENTATION_ACTUAL = "actual_normalized_snr"
SUCCESS_SNR_REPRESENTATIONS = frozenset(
    {
        SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE,
        SUCCESS_SNR_REPRESENTATION_ACTUAL,
    }
)
SUCCESS_DISTANCE_BINNING_VERSION = "exact-distance-v1"
SUCCESS_SNR_BASELINE_VERSION = "station-median-min3-v1"
SUCCESS_MINIMUM_SNR_BASELINE_OBSERVATIONS = 3
SUCCESS_DISTANCE_BIN_WIDTH_RULES_KM = (
    (1250.0, 125.0),
    (3000.0, 250.0),
    (6000.0, 500.0),
    (np.inf, 1000.0),
)
SUCCESS_STATION_BALANCED_COLOR = "#36aaf9"
SUCCESS_OBSERVATION_LEVEL_COLOR = "#ffbe33"
SUCCESS_OUTCOME_COLOR = "#39ff14"
SUCCESS_COUNTER_OUTCOME_COLOR = "#858585"
SUCCESS_RATE_LINE_COLOR = "#c8f4ff"
SUCCESS_TEMPORAL_RATE_CEILINGS = (
    10.0,
    20.0,
    25.0,
    30.0,
    40.0,
    50.0,
    60.0,
    75.0,
    100.0,
)
SUCCESS_TEMPORAL_EVIDENCE_FIGURE_TOP = 0.76
SUCCESS_TEMPORAL_EVIDENCE_ROW_SPACE = 0.24
SUCCESS_TEMPORAL_FOLDED_COLUMN_X_SHIFT = 0.025
SUCCESS_TEMPORAL_REFERENCE_FIGURE_WIDTH_PX = 1300.0
SUCCESS_TEMPORAL_FOLDED_COLUMN_LEFT_EXPANSION_PX = 28.0


def _opportunity_time_bin(rows, analysis_start_t=None, analysis_end_t=None):
    """Choose a readable fixed UTC bin for opportunity-rate evidence."""
    if analysis_start_t is not None and analysis_end_t is not None:
        span = _as_utc_timestamp(analysis_end_t) - _as_utc_timestamp(analysis_start_t)
    else:
        if rows.empty:
            return "3h"
        times = opportunity_utc_from_time_slot(rows["time_slot"]).dropna()
        if times.empty:
            return "3h"
        span = times.max() - times.min()
    if span <= pd.Timedelta(days=1):
        return "1h"
    if span <= pd.Timedelta(days=7):
        return "3h"
    return "12h"

def _as_utc_timestamp(value):
    """Normalize a datetime-like value to a timezone-aware UTC Timestamp."""
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")

def _required_figure_labels(figure_labels, required_keys):
    """Return an immutable-style string copy of required localized figure labels."""
    labels = dict(figure_labels or {})
    missing = sorted(key for key in required_keys if key not in labels)
    if missing:
        raise ValueError(
            "Success figure labels are missing: " + ", ".join(missing)
        )
    return {key: str(labels[key]) for key in required_keys}


def _normalize_success_distance_scope_intervals(distance_scope_intervals):
    """Return sorted, merged non-negative distance intervals in kilometres."""
    normalized = []
    for lower_km, upper_km in distance_scope_intervals or ():
        lower = float(lower_km)
        upper = float(upper_km)
        if (
            not np.isfinite(lower)
            or not np.isfinite(upper)
            or lower < 0.0
            or upper <= lower
        ):
            raise ValueError(
                "Success distance scope requires finite intervals with "
                "0 <= lower < upper."
            )
        normalized.append((lower, upper))
    if not normalized:
        raise ValueError("Success distance evidence requires a distance scope.")

    merged = []
    for lower, upper in sorted(normalized):
        if merged and lower <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], upper))
        else:
            merged.append((lower, upper))
    return tuple(merged)


def _success_distance_bin_width_km(distance_scope_intervals):
    """Choose the deterministic exact-distance width from selected scope span."""
    intervals = _normalize_success_distance_scope_intervals(
        distance_scope_intervals
    )
    selected_span_km = intervals[-1][1] - intervals[0][0]
    for maximum_span_km, width_km in SUCCESS_DISTANCE_BIN_WIDTH_RULES_KM:
        if selected_span_km <= maximum_span_km:
            return float(width_km)
    raise AssertionError("The final Success distance-bin rule must be unbounded.")


def _format_success_distance_km(value_km, thousands_separator):
    """Format one integer-kilometre boundary for a localized compact label."""
    formatted = f"{int(round(float(value_km))):,}"
    separator = str(thousands_separator or ",")
    return formatted if separator == "," else formatted.replace(",", separator)


def _success_distance_bin_definition(
    distance_scope_intervals,
    *,
    thousands_separator=",",
):
    """Build one shared zero-anchored exact-distance grid for all panels.

    The grid depends only on selected distance intervals. Inactive bins between
    disjoint intervals remain in the grid so plotted lines break across the
    visible geographic gap.
    """
    intervals = _normalize_success_distance_scope_intervals(
        distance_scope_intervals
    )
    width_km = _success_distance_bin_width_km(intervals)
    minimum_km = intervals[0][0]
    maximum_km = intervals[-1][1]
    first_edge_km = np.floor(minimum_km / width_km) * width_km
    final_edge_km = np.ceil(maximum_km / width_km) * width_km
    if final_edge_km <= first_edge_km:
        final_edge_km = first_edge_km + width_km
    bin_count = int(round((final_edge_km - first_edge_km) / width_km))
    edges_km = first_edge_km + (
        np.arange(bin_count + 1, dtype=float) * width_km
    )
    lower_edges_km = edges_km[:-1]
    upper_edges_km = edges_km[1:]
    centers_km = (lower_edges_km + upper_edges_km) / 2.0
    active_mask = np.zeros(bin_count, dtype=bool)
    for lower_km, upper_km in intervals:
        active_mask |= (
            (lower_edges_km < upper_km)
            & (upper_edges_km > lower_km)
        )
    labels = [
        (
            f"{_format_success_distance_km(lower, thousands_separator)}"
            "\u2013"
            f"{_format_success_distance_km(upper, thousands_separator)} km"
        )
        for lower, upper in zip(lower_edges_km, upper_edges_km)
    ]
    return {
        "version": SUCCESS_DISTANCE_BINNING_VERSION,
        "scope_intervals_km": intervals,
        "width_km": width_km,
        "edges_km": edges_km,
        "centers_km": centers_km,
        "labels": labels,
        "active_mask": active_mask,
    }


def _assign_success_distance_bins(distances_km, bin_definition):
    """Assign exact distances to half-open bins with the final scope bound closed."""
    distances = pd.to_numeric(
        pd.Series(distances_km, copy=False),
        errors="coerce",
    ).to_numpy(dtype=float, copy=True)
    edges_km = np.asarray(bin_definition["edges_km"], dtype=float)
    intervals = tuple(bin_definition["scope_intervals_km"])
    active_mask = np.asarray(bin_definition["active_mask"], dtype=bool)
    indexes = np.full(len(distances), -1, dtype=np.int64)
    finite = np.isfinite(distances)
    if not finite.any():
        return indexes

    maximum_scope_km = intervals[-1][1]
    belongs_to_scope = np.zeros(len(distances), dtype=bool)
    for lower_km, upper_km in intervals:
        upper_inclusive = upper_km == maximum_scope_km
        interval_members = distances >= lower_km
        if upper_inclusive:
            interval_members &= (
                (distances < upper_km)
                | (distances == upper_km)
            )
        else:
            interval_members &= distances < upper_km
        belongs_to_scope |= interval_members

    assigned = np.searchsorted(edges_km, distances, side="right") - 1
    final_edge = distances == edges_km[-1]
    assigned[final_edge] = len(edges_km) - 2
    valid = (
        finite
        & belongs_to_scope
        & (assigned >= 0)
        & (assigned < len(active_mask))
    )
    valid_positions = np.flatnonzero(valid)
    if len(valid_positions):
        valid_positions = valid_positions[
            active_mask[assigned[valid_positions]]
        ]
        indexes[valid_positions] = assigned[valid_positions]
    return indexes


def _aggregate_success_distance_profile(
    peer_df,
    distance_scope_intervals,
    *,
    thousands_separator=",",
):
    """Aggregate reach, rates, successful SNR, and support on one distance grid."""
    required_columns = {
        "peer_sign",
        "peer_grid",
        "calc_dist",
        "eligible",
        "rate_pct",
        "hits",
        "misses",
        "successful_snr_median",
    }
    missing_columns = sorted(required_columns.difference(peer_df.columns))
    if missing_columns:
        raise ValueError(
            "Success evidence peers are missing columns: "
            + ", ".join(missing_columns)
        )
    bin_definition = _success_distance_bin_definition(
        distance_scope_intervals,
        thousands_separator=thousands_separator,
    )
    bin_count = len(bin_definition["centers_km"])
    confirmed = peer_df[
        peer_df["eligible"]
        & pd.to_numeric(peer_df["rate_pct"], errors="coerce").notna()
    ].copy()
    confirmed["hits"] = pd.to_numeric(
        confirmed["hits"],
        errors="coerce",
    ).fillna(0.0)
    confirmed["misses"] = pd.to_numeric(
        confirmed["misses"],
        errors="coerce",
    ).fillna(0.0)
    confirmed["opportunities"] = confirmed["hits"] + confirmed["misses"]
    confirmed = confirmed[confirmed["opportunities"] > 0].copy()
    confirmed["exact_rate_pct"] = (
        100.0 * confirmed["hits"] / confirmed["opportunities"]
    )
    confirmed["has_target"] = (confirmed["hits"] >= 1.0).astype("int64")
    confirmed["successful_snr_median"] = pd.to_numeric(
        confirmed["successful_snr_median"],
        errors="coerce",
    )
    confirmed["distance_bin_index"] = _assign_success_distance_bins(
        confirmed["calc_dist"],
        bin_definition,
    )
    confirmed = confirmed[confirmed["distance_bin_index"] >= 0].copy()

    profile = pd.DataFrame(
        {
            "distance_bin_index": np.arange(bin_count, dtype=np.int64),
        }
    )
    if confirmed.empty:
        station_groups = pd.DataFrame(
            columns=[
                "distance_bin_index",
                "station_balanced_rate_pct",
                "target_count",
                "counter_count",
                "qualifying_station_count",
                "target_station_count",
            ]
        )
    else:
        station_groups = (
            confirmed.groupby(
                "distance_bin_index",
                observed=True,
            )
            .agg(
                station_balanced_rate_pct=("exact_rate_pct", "mean"),
                target_count=("hits", "sum"),
                counter_count=("misses", "sum"),
                qualifying_station_count=("peer_sign", "size"),
                target_station_count=("has_target", "sum"),
            )
            .reset_index()
        )
    profile = profile.merge(
        station_groups,
        on="distance_bin_index",
        how="left",
    )
    profile["confirmed_opportunity_count"] = (
        pd.to_numeric(profile["target_count"], errors="coerce")
        + pd.to_numeric(profile["counter_count"], errors="coerce")
    )
    profile["peer_reach_pct"] = np.where(
        profile["qualifying_station_count"] > 0,
        (
            100.0
            * profile["target_station_count"]
            / profile["qualifying_station_count"]
        ),
        np.nan,
    )
    profile["observation_level_rate_pct"] = np.where(
        profile["confirmed_opportunity_count"] > 0,
        (
            100.0
            * profile["target_count"]
            / profile["confirmed_opportunity_count"]
        ),
        np.nan,
    )

    successful_snr = confirmed[
        (confirmed["hits"] >= 1.0)
        & confirmed["successful_snr_median"].notna()
    ]
    if successful_snr.empty:
        snr_groups = pd.DataFrame(
            columns=[
                "distance_bin_index",
                "successful_snr_station_count",
                "successful_snr_median_db",
                "successful_snr_min_db",
                "successful_snr_max_db",
                "successful_snr_q1_db",
                "successful_snr_q3_db",
            ]
        )
    else:
        snr_grouped = successful_snr.groupby(
            "distance_bin_index",
            observed=True,
        )["successful_snr_median"]
        snr_groups = snr_grouped.agg(
            successful_snr_station_count="size",
            successful_snr_median_db="median",
            successful_snr_min_db="min",
            successful_snr_max_db="max",
        ).reset_index()
        quartiles = (
            snr_grouped.quantile([0.25, 0.75])
            .unstack()
            .rename(
                columns={
                    0.25: "successful_snr_q1_db",
                    0.75: "successful_snr_q3_db",
                }
            )
            .reset_index()
        )
        snr_groups = snr_groups.merge(
            quartiles,
            on="distance_bin_index",
            how="left",
        )
    profile = profile.merge(
        snr_groups,
        on="distance_bin_index",
        how="left",
    )
    snr_station_count = pd.to_numeric(
        profile["successful_snr_station_count"],
        errors="coerce",
    ).fillna(0)
    profile["successful_snr_interval_lower_db"] = np.select(
        [
            snr_station_count == 2,
            snr_station_count >= 3,
        ],
        [
            profile["successful_snr_min_db"],
            profile["successful_snr_q1_db"],
        ],
        default=np.nan,
    )
    profile["successful_snr_interval_upper_db"] = np.select(
        [
            snr_station_count == 2,
            snr_station_count >= 3,
        ],
        [
            profile["successful_snr_max_db"],
            profile["successful_snr_q3_db"],
        ],
        default=np.nan,
    )
    profile["successful_snr_interval_kind"] = np.select(
        [
            snr_station_count == 2,
            snr_station_count >= 3,
        ],
        ["range", "iqr"],
        default="none",
    )
    count_columns = (
        "qualifying_station_count",
        "target_station_count",
        "confirmed_opportunity_count",
        "target_count",
        "counter_count",
        "successful_snr_station_count",
    )
    for column in count_columns:
        profile[column] = pd.to_numeric(
            profile[column],
            errors="coerce",
        ).fillna(0).astype("int64")

    inactive = ~np.asarray(bin_definition["active_mask"], dtype=bool)
    metric_columns = (
        "peer_reach_pct",
        "station_balanced_rate_pct",
        "observation_level_rate_pct",
        "successful_snr_median_db",
        "successful_snr_interval_lower_db",
        "successful_snr_interval_upper_db",
    )
    profile.loc[inactive, metric_columns] = np.nan
    return bin_definition, profile


def _opportunity_segment_recipe(
    title,
    selected_segment,
    peer_df,
    rows,
    analysis_start_t,
    analysis_end_t,
    terminology,
    minimum_trials=5,
    figure_labels=None,
    distance_scope_intervals=None,
):
    """Build exact-distance reach, consistency, SNR, and support evidence."""
    labels = _required_figure_labels(
        figure_labels,
        (
            "reach_title",
            "reach_y",
            "consistency_title",
            "snr_distance_title",
            "distance_x",
            "rate_y",
            "snr_y",
            "confirmed_opportunities",
            "qualifying_stations",
            "target_stations",
            "successful_snr_stations",
            "station_balanced",
            "observation_level",
            "target_evidence",
            "counter_evidence",
            "median",
            "iqr",
            "two_station_range",
            "support",
            "support_title",
            "bin_width",
            "locator_precision_note",
            "thousands_separator",
        ),
    )
    if distance_scope_intervals is None:
        distance_bounds = (
            peer_df.loc[
                peer_df["r_min"].notna() & peer_df["r_max"].notna(),
                ["r_min", "r_max"],
            ]
            .drop_duplicates()
            .sort_values(["r_min", "r_max"], kind="stable")
        )
        distance_scope_intervals = tuple(
            distance_bounds.itertuples(index=False, name=None)
        )
    bin_definition, distance_profile = _aggregate_success_distance_profile(
        peer_df,
        distance_scope_intervals,
        thousands_separator=labels.get("thousands_separator", ","),
    )

    return {
        "kind": "opportunity_success_evidence",
        "schema_version": 2,
        "distance_binning_version": SUCCESS_DISTANCE_BINNING_VERSION,
        "title": title,
        "absolute_mode": terminology.get("mode", "RX"),
        "terminology": dict(terminology),
        "labels": labels,
        "selected_segment": selected_segment,
        "minimum_trials": int(minimum_trials),
        "distance_scope_intervals_km": [
            [float(lower), float(upper)]
            for lower, upper in bin_definition["scope_intervals_km"]
        ],
        "distance_bin_width_km": float(bin_definition["width_km"]),
        "distance_edges_km": np.asarray(
            bin_definition["edges_km"],
            dtype=float,
        ).copy(),
        "distance_centers_km": np.asarray(
            bin_definition["centers_km"],
            dtype=float,
        ).copy(),
        "distance_labels": list(bin_definition["labels"]),
        "distance_active_mask": np.asarray(
            bin_definition["active_mask"],
            dtype=bool,
        ).copy(),
        "distance_peer_reach_pct": pd.to_numeric(
            distance_profile["peer_reach_pct"],
            errors="coerce",
        ).to_numpy(dtype=float, copy=True),
        "distance_station_balanced_rate_pct": pd.to_numeric(
            distance_profile["station_balanced_rate_pct"],
            errors="coerce",
        ).to_numpy(dtype=float, copy=True),
        "distance_observation_level_rate_pct": pd.to_numeric(
            distance_profile["observation_level_rate_pct"],
            errors="coerce",
        ).to_numpy(dtype=float, copy=True),
        "distance_successful_snr_median_db": pd.to_numeric(
            distance_profile["successful_snr_median_db"],
            errors="coerce",
        ).to_numpy(dtype=float, copy=True),
        "distance_successful_snr_interval_lower_db": pd.to_numeric(
            distance_profile["successful_snr_interval_lower_db"],
            errors="coerce",
        ).to_numpy(dtype=float, copy=True),
        "distance_successful_snr_interval_upper_db": pd.to_numeric(
            distance_profile["successful_snr_interval_upper_db"],
            errors="coerce",
        ).to_numpy(dtype=float, copy=True),
        "distance_successful_snr_interval_kind": distance_profile[
            "successful_snr_interval_kind"
        ].astype(str).tolist(),
        "distance_qualifying_station_counts": distance_profile[
            "qualifying_station_count"
        ].to_numpy(dtype=np.int64, copy=True),
        "distance_target_station_counts": distance_profile[
            "target_station_count"
        ].to_numpy(dtype=np.int64, copy=True),
        "distance_confirmed_opportunity_counts": distance_profile[
            "confirmed_opportunity_count"
        ].to_numpy(dtype=np.int64, copy=True),
        "distance_target_counts": distance_profile[
            "target_count"
        ].to_numpy(dtype=np.int64, copy=True),
        "distance_counter_counts": distance_profile[
            "counter_count"
        ].to_numpy(dtype=np.int64, copy=True),
        "distance_successful_snr_station_counts": distance_profile[
            "successful_snr_station_count"
        ].to_numpy(dtype=np.int64, copy=True),
    }

def _success_distance_panel_title(title):
    """Wrap a long Success panel title at its final distance qualifier."""
    normalized_title = str(title)
    for separator in (" by ", " nach "):
        title_prefix, matched_separator, distance_qualifier = (
            normalized_title.rpartition(separator)
        )
        if matched_separator:
            return (
                f"{title_prefix}\n"
                f"{matched_separator.strip()} {distance_qualifier}"
            )
    return normalized_title


@synchronized_matplotlib
def _render_opportunity_segment_figure(recipe):
    """Render the three exact-distance Success Evidence panels."""
    labels = dict(recipe.get("labels") or {})
    distance_edges = np.asarray(
        recipe.get("distance_edges_km", []),
        dtype=float,
    )
    distance_centers = np.asarray(
        recipe.get("distance_centers_km", []),
        dtype=float,
    )
    distance_labels = list(recipe.get("distance_labels", []))
    active_mask = np.asarray(
        recipe.get("distance_active_mask", []),
        dtype=bool,
    )
    distance_scope_intervals = tuple(
        (float(lower_km), float(upper_km))
        for lower_km, upper_km in recipe.get(
            "distance_scope_intervals_km",
            (),
        )
    )
    if (
        len(distance_edges) != len(distance_centers) + 1
        or len(distance_labels) != len(distance_centers)
        or len(active_mask) != len(distance_centers)
    ):
        raise ValueError("Success evidence requires one shared distance grid.")

    fig = create_agg_figure(figsize=(13, 6.5), facecolor="black")
    fig.subplots_adjust(
        left=0.05,
        right=0.98,
        bottom=0.245,
        top=0.78,
        wspace=0.24,
    )
    fig.suptitle(
        f"\n{recipe.get('title', '')} - {recipe.get('selected_segment', '')}",
        color="white",
        fontweight="bold",
        fontsize=METRIC_FIGURE_TITLE_FONTSIZE,
        fontfamily=METRIC_FONT_FAMILY,
        y=0.98,
    )
    fig.text(
        0.98,
        0.014,
        f"WSPRadar.org {APP_VERSION}",
        color="#888888",
        ha="right",
        fontsize=METRIC_FOOTER_FONTSIZE,
        fontfamily=METRIC_FONT_FAMILY,
    )
    grid_spec = fig.add_gridspec(1, 3)
    reach_axis = fig.add_subplot(grid_spec[0, 0])
    consistency_axis = fig.add_subplot(grid_spec[0, 1])
    snr_axis = fig.add_subplot(grid_spec[0, 2])
    reach_axis.set_gid("success-distance-reach-axis")
    consistency_axis.set_gid("success-distance-consistency-axis")
    snr_axis.set_gid("success-distance-snr-axis")
    for axis in (reach_axis, consistency_axis, snr_axis):
        axis.set_box_aspect(1)
        _style_evidence_axis(axis)
        axis.set_xlim(distance_edges[0], distance_edges[-1])
        axis.set_xticks(distance_centers)
        axis.set_xticklabels(
            distance_labels,
            rotation=58,
            ha="right",
            fontsize=METRIC_TICK_LABEL_FONTSIZE,
            fontfamily=METRIC_FONT_FAMILY,
        )
        gap_start_km = float(distance_edges[0])
        for scope_lower_km, scope_upper_km in distance_scope_intervals:
            if scope_lower_km > gap_start_km:
                gap = axis.axvspan(
                    gap_start_km,
                    scope_lower_km,
                    facecolor="#1b1b1b",
                    edgecolor="#333333",
                    hatch="////",
                    linewidth=0.25,
                    alpha=0.75,
                    zorder=1,
                )
                gap.set_gid("success-distance-scope-gap")
            gap_start_km = max(gap_start_km, scope_upper_km)
        if gap_start_km < distance_edges[-1]:
            gap = axis.axvspan(
                gap_start_km,
                distance_edges[-1],
                facecolor="#1b1b1b",
                edgecolor="#333333",
                hatch="////",
                linewidth=0.25,
                alpha=0.75,
                zorder=1,
            )
            gap.set_gid("success-distance-scope-gap")
        _set_metric_axis_labels(
            axis,
            x_label=labels["distance_x"],
        )

    distance_widths = np.diff(distance_edges)
    peer_reach = np.asarray(
        recipe.get("distance_peer_reach_pct", []),
        dtype=float,
    )
    reach_bars = reach_axis.bar(
        distance_centers,
        peer_reach,
        width=distance_widths * 0.72,
        color=EVIDENCE_AGG_COLOR,
        alpha=0.70,
        edgecolor="#67c4ff",
        linewidth=0.7,
        zorder=3,
    )
    for bar in reach_bars:
        bar.set_gid("success-distance-peer-reach")
    reach_axis.set_ylim(0.0, opportunity_rate_scale_max(peer_reach))
    reach_axis.set_title(
        _success_distance_panel_title(labels["reach_title"]),
        color="white",
        fontweight="bold",
        fontsize=METRIC_PANEL_TITLE_FONTSIZE,
        fontfamily=METRIC_FONT_FAMILY,
        pad=10,
    )
    _set_metric_axis_labels(
        reach_axis,
        y_label=labels["reach_y"],
    )

    station_balanced_rates = np.asarray(
        recipe.get("distance_station_balanced_rate_pct", []),
        dtype=float,
    )
    observation_rates = np.asarray(
        recipe.get("distance_observation_level_rate_pct", []),
        dtype=float,
    )
    station_line = consistency_axis.plot(
        distance_centers,
        station_balanced_rates,
        color=SUCCESS_STATION_BALANCED_COLOR,
        marker="o",
        markersize=4,
        linewidth=1.5,
        label=labels["station_balanced"],
        zorder=4,
    )[0]
    station_line.set_gid("success-distance-station-balanced")
    observation_line = consistency_axis.plot(
        distance_centers,
        observation_rates,
        color=SUCCESS_OBSERVATION_LEVEL_COLOR,
        marker="s",
        markersize=3.5,
        linewidth=1.3,
        linestyle="dashed",
        label=labels["observation_level"],
        zorder=4,
    )[0]
    observation_line.set_gid("success-distance-observation-level")
    consistency_axis.set_ylim(
        0.0,
        opportunity_rate_scale_max(
            np.concatenate((station_balanced_rates, observation_rates))
        ),
    )
    consistency_axis.set_title(
        _success_distance_panel_title(labels["consistency_title"]),
        color="white",
        fontweight="bold",
        fontsize=METRIC_PANEL_TITLE_FONTSIZE,
        fontfamily=METRIC_FONT_FAMILY,
        pad=10,
    )
    _set_metric_axis_labels(
        consistency_axis,
        y_label=labels["rate_y"],
    )
    _place_metric_legend(
        consistency_axis,
        loc="upper right",
        borderaxespad=0.0,
        gid="success-distance-rate-legend",
    )

    snr_medians = np.asarray(
        recipe.get("distance_successful_snr_median_db", []),
        dtype=float,
    )
    snr_lower = np.asarray(
        recipe.get("distance_successful_snr_interval_lower_db", []),
        dtype=float,
    )
    snr_upper = np.asarray(
        recipe.get("distance_successful_snr_interval_upper_db", []),
        dtype=float,
    )
    snr_interval_kind = np.asarray(
        recipe.get("distance_successful_snr_interval_kind", []),
        dtype=object,
    )
    iqr_lower = np.where(snr_interval_kind == "iqr", snr_lower, np.nan)
    iqr_upper = np.where(snr_interval_kind == "iqr", snr_upper, np.nan)
    iqr_artist = snr_axis.fill_between(
        distance_centers,
        iqr_lower,
        iqr_upper,
        color=SUCCESS_STATION_BALANCED_COLOR,
        alpha=0.22,
        label=labels["iqr"],
        zorder=2,
    )
    iqr_artist.set_gid("success-distance-snr-iqr")
    two_station_mask = (
        (snr_interval_kind == "range")
        & np.isfinite(snr_lower)
        & np.isfinite(snr_upper)
    )
    if two_station_mask.any():
        range_artist = snr_axis.vlines(
            distance_centers[two_station_mask],
            snr_lower[two_station_mask],
            snr_upper[two_station_mask],
            color=SUCCESS_OBSERVATION_LEVEL_COLOR,
            linewidth=2.0,
            alpha=0.85,
            label=labels["two_station_range"],
            zorder=3,
        )
        range_artist.set_gid("success-distance-snr-two-station-range")
    snr_line = snr_axis.plot(
        distance_centers,
        snr_medians,
        color=SUCCESS_STATION_BALANCED_COLOR,
        marker="o",
        markersize=4,
        linewidth=1.5,
        label=labels["median"],
        zorder=4,
    )[0]
    snr_line.set_gid("success-distance-snr-median")
    snr_axis.set_title(
        _success_distance_panel_title(labels["snr_distance_title"]),
        color="white",
        fontweight="bold",
        fontsize=METRIC_PANEL_TITLE_FONTSIZE,
        fontfamily=METRIC_FONT_FAMILY,
        pad=10,
    )
    _set_metric_axis_labels(
        snr_axis,
        y_label=labels["snr_y"],
    )
    _place_metric_legend(
        snr_axis,
        loc="upper right",
        borderaxespad=0.0,
        gid="success-distance-snr-legend",
    )

    return fig


def _aggregate_success_chronological_profile(work, start, end, time_bin):
    """Aggregate chronological SNR-independent Success evidence by fixed bin.

    Every contributing qualifying station supplies one split vote whose two
    fractions sum to one. Raw opportunity arrays retain one count per confirmed
    outcome so the two stacked layers preserve their distinct weighting.
    """
    bin_minutes = _time_agg_minutes(time_bin)
    bin_delta = pd.Timedelta(minutes=bin_minutes)
    bin_count = max(1, int(np.ceil((end - start) / bin_delta)))
    bin_starts = pd.DatetimeIndex(
        [start + (index * bin_delta) for index in range(bin_count)]
    )
    bin_edges = pd.DatetimeIndex(
        list(bin_starts) + [end]
    )
    bin_centers = pd.DatetimeIndex(
        [
            lower + ((upper - lower) / 2)
            for lower, upper in zip(bin_edges[:-1], bin_edges[1:])
        ]
    )
    station_balanced = np.full(bin_count, np.nan, dtype=float)
    observation_level = np.full(bin_count, np.nan, dtype=float)
    station_success_votes = np.zeros(bin_count, dtype=float)
    station_counter_votes = np.zeros(bin_count, dtype=float)
    target_counts = np.zeros(bin_count, dtype=np.int64)
    counter_counts = np.zeros(bin_count, dtype=np.int64)
    station_counts = np.zeros(bin_count, dtype=np.int64)
    if not work.empty:
        binned = work.copy()
        binned["bin_index"] = (
            (binned["evidence_utc"] - start) // bin_delta
        ).astype("int64")
        station_bins = (
            binned.groupby(
                ["bin_index", "peer_sign", "peer_grid"],
                dropna=False,
                observed=True,
            )
            .agg(hits=("hit", "sum"), misses=("miss", "sum"))
            .reset_index()
        )
        station_bins["confirmed"] = station_bins["hits"] + station_bins["misses"]
        station_bins = station_bins[station_bins["confirmed"] > 0].copy()
        station_bins["rate_pct"] = (
            100.0 * station_bins["hits"] / station_bins["confirmed"]
        )
        station_bins["success_vote"] = (
            station_bins["hits"] / station_bins["confirmed"]
        )
        station_bins["counter_vote"] = (
            station_bins["misses"] / station_bins["confirmed"]
        )
        bins = (
            station_bins.groupby("bin_index", observed=True)
            .agg(
                station_balanced_rate_pct=("rate_pct", "mean"),
                station_success_votes=("success_vote", "sum"),
                station_counter_votes=("counter_vote", "sum"),
                hits=("hits", "sum"),
                misses=("misses", "sum"),
                station_count=("peer_sign", "size"),
            )
            .reset_index()
        )
        bins["observation_level_rate_pct"] = np.where(
            (bins["hits"] + bins["misses"]) > 0,
            100.0 * bins["hits"] / (bins["hits"] + bins["misses"]),
            np.nan,
        )
        indexes = bins["bin_index"].to_numpy(dtype=np.int64, copy=False)
        valid_indexes = (indexes >= 0) & (indexes < bin_count)
        indexes = indexes[valid_indexes]
        station_balanced[indexes] = bins.loc[
            valid_indexes,
            "station_balanced_rate_pct",
        ].to_numpy(dtype=float, copy=False)
        observation_level[indexes] = bins.loc[
            valid_indexes,
            "observation_level_rate_pct",
        ].to_numpy(dtype=float, copy=False)
        station_success_votes[indexes] = bins.loc[
            valid_indexes,
            "station_success_votes",
        ].to_numpy(dtype=float, copy=False)
        station_counter_votes[indexes] = bins.loc[
            valid_indexes,
            "station_counter_votes",
        ].to_numpy(dtype=float, copy=False)
        target_counts[indexes] = bins.loc[
            valid_indexes,
            "hits",
        ].to_numpy(dtype=np.int64, copy=False)
        counter_counts[indexes] = bins.loc[
            valid_indexes,
            "misses",
        ].to_numpy(dtype=np.int64, copy=False)
        station_counts[indexes] = bins.loc[
            valid_indexes,
            "station_count",
        ].to_numpy(dtype=np.int64, copy=False)
    return {
        "time_ns": (
            bin_centers.tz_convert(None)
            .to_numpy(dtype="datetime64[ns]")
            .astype(np.int64, copy=True)
        ),
        "time_edge_ns": (
            bin_edges.tz_convert(None)
            .to_numpy(dtype="datetime64[ns]")
            .astype(np.int64, copy=True)
        ),
        "station_balanced_rate_pct": station_balanced,
        "observation_level_rate_pct": observation_level,
        "station_success_votes": station_success_votes,
        "station_counter_votes": station_counter_votes,
        "opportunity_success_counts": target_counts,
        "opportunity_counter_counts": counter_counts,
        "target_counts": target_counts,
        "counter_counts": counter_counts,
        "station_counts": station_counts,
    }


def _represented_utc_date_hour_counts(work, start, end):
    """Count represented dates whose hourly slot overlaps the analysis window.

    A represented date is a UTC calendar date with eligible evidence somewhere
    in the active scope. Every selected hour on that date remains in the
    denominator even when the date-hour itself contains no evidence.
    """
    date_hour_counts = np.zeros(24, dtype=np.int64)
    if work.empty:
        return date_hour_counts

    represented_dates = (
        work["evidence_utc"]
        .dropna()
        .dt.normalize()
        .drop_duplicates()
    )
    one_hour = pd.Timedelta(hours=1)
    for represented_date in represented_dates:
        hour_starts = pd.DatetimeIndex(
            [
                represented_date + pd.Timedelta(hours=hour)
                for hour in range(24)
            ]
        )
        hour_ends = hour_starts + one_hour
        date_hour_counts += np.asarray(
            (hour_starts < end) & (hour_ends > start),
            dtype=np.int64,
        )
    return date_hour_counts


def _average_folded_counts_per_represented_date(values, date_hour_counts):
    """Return folded display counts averaged over represented selected dates."""
    numeric_values = np.asarray(values, dtype=float)
    denominators = np.asarray(date_hour_counts, dtype=float)
    if numeric_values.shape != denominators.shape:
        raise ValueError(
            "Folded Success counts and represented-date denominators "
            "must have the same shape."
        )
    averages = np.zeros_like(numeric_values, dtype=float)
    np.divide(
        numeric_values,
        denominators,
        out=averages,
        where=denominators > 0.0,
    )
    return averages


def _partition_average_station_support(average_support, rate_pct):
    """Split mean station-date-hour support by an unchanged pooled station rate.

    The total remains the true mean number of contributing station identities
    per represented UTC date-hour. Its two display components use the folded
    equal-station Success Rate, which continues to pool each station across
    dates before giving every distinct station one vote.
    """
    support = np.asarray(average_support, dtype=float)
    rates = np.asarray(rate_pct, dtype=float)
    if support.shape != rates.shape:
        raise ValueError(
            "Folded station support and station-balanced rates "
            "must have the same shape."
        )
    has_support = support > 0.0
    invalid_rates = has_support & (
        ~np.isfinite(rates)
        | (rates < 0.0)
        | (rates > 100.0)
    )
    if invalid_rates.any():
        raise ValueError(
            "Positive folded station support requires a finite "
            "station-balanced rate from 0% through 100%."
        )
    success_support = np.zeros_like(support, dtype=float)
    success_support[has_support] = (
        support[has_support] * rates[has_support] / 100.0
    )
    counter_support = support - success_support
    return success_support, counter_support


def _aggregate_success_folded_profile(work, start, end):
    """Fold confirmed rows into rate diagnostics and mean per-date support.

    Rates pool a station across represented dates within the same UTC hour, so
    every distinct station retains one equal rate vote. Display support instead
    counts distinct station-date-hour presences and averages them over every
    represented date whose hour overlaps the selected window. The displayed
    station stack partitions that true mean support by the unchanged pooled
    station-balanced rate.

    The caller supplies eligible confirmed rows already clipped to the
    half-open analysis window. Raw station-vote and station-count arrays remain
    pooled distinct-station diagnostics for the unchanged folded rate; only the
    explicit support arrays drive the folded station bars.
    """
    station_balanced = np.full(24, np.nan, dtype=float)
    observation_level = np.full(24, np.nan, dtype=float)
    station_success_votes = np.zeros(24, dtype=float)
    station_counter_votes = np.zeros(24, dtype=float)
    target_counts = np.zeros(24, dtype=np.int64)
    counter_counts = np.zeros(24, dtype=np.int64)
    station_counts = np.zeros(24, dtype=np.int64)
    station_date_hour_presence_counts = np.zeros(24, dtype=np.int64)
    utc_date_counts = np.zeros(24, dtype=np.int64)
    if not work.empty:
        folded = work.copy()
        folded["utc_hour"] = folded["evidence_utc"].dt.hour.astype("int8")
        folded["utc_date"] = folded["evidence_utc"].dt.normalize()
        station_hours = (
            folded.groupby(
                ["utc_hour", "peer_sign", "peer_grid"],
                dropna=False,
                observed=True,
            )
            .agg(hits=("hit", "sum"), misses=("miss", "sum"))
            .reset_index()
        )
        station_hours["confirmed"] = (
            station_hours["hits"] + station_hours["misses"]
        )
        station_hours = station_hours[station_hours["confirmed"] > 0].copy()
        station_hours["rate_pct"] = (
            100.0 * station_hours["hits"] / station_hours["confirmed"]
        )
        station_hours["success_vote"] = (
            station_hours["hits"] / station_hours["confirmed"]
        )
        station_hours["counter_vote"] = (
            station_hours["misses"] / station_hours["confirmed"]
        )
        hours = (
            station_hours.groupby("utc_hour", observed=True)
            .agg(
                station_balanced_rate_pct=("rate_pct", "mean"),
                station_success_votes=("success_vote", "sum"),
                station_counter_votes=("counter_vote", "sum"),
                hits=("hits", "sum"),
                misses=("misses", "sum"),
                station_count=("peer_sign", "size"),
            )
            .reset_index()
        )
        station_date_hour_counts = (
            folded.groupby(
                [
                    "utc_hour",
                    "utc_date",
                    "peer_sign",
                    "peer_grid",
                ],
                dropna=False,
                observed=True,
            )
            .size()
            .groupby(level="utc_hour")
            .size()
        )
        station_date_hour_presence_counts[
            station_date_hour_counts.index.to_numpy(
                dtype=np.int64,
                copy=False,
            )
        ] = station_date_hour_counts.to_numpy(
            dtype=np.int64,
            copy=False,
        )
        hours["observation_level_rate_pct"] = np.where(
            (hours["hits"] + hours["misses"]) > 0,
            100.0 * hours["hits"] / (hours["hits"] + hours["misses"]),
            np.nan,
        )
        indexes = hours["utc_hour"].to_numpy(dtype=np.int64, copy=False)
        station_balanced[indexes] = hours[
            "station_balanced_rate_pct"
        ].to_numpy(dtype=float, copy=False)
        observation_level[indexes] = hours[
            "observation_level_rate_pct"
        ].to_numpy(dtype=float, copy=False)
        station_success_votes[indexes] = hours[
            "station_success_votes"
        ].to_numpy(dtype=float, copy=False)
        station_counter_votes[indexes] = hours[
            "station_counter_votes"
        ].to_numpy(dtype=float, copy=False)
        target_counts[indexes] = hours["hits"].to_numpy(
            dtype=np.int64,
            copy=False,
        )
        counter_counts[indexes] = hours["misses"].to_numpy(
            dtype=np.int64,
            copy=False,
        )
        station_counts[indexes] = hours["station_count"].to_numpy(
            dtype=np.int64,
            copy=False,
        )
        date_counts = (
            folded.groupby("utc_hour", observed=True)["utc_date"]
            .nunique()
        )
        utc_date_counts[
            date_counts.index.to_numpy(dtype=np.int64, copy=False)
        ] = date_counts.to_numpy(dtype=np.int64, copy=False)
    represented_utc_date_counts = _represented_utc_date_hour_counts(
        work,
        start,
        end,
    )
    station_average_support_per_utc_date = (
        _average_folded_counts_per_represented_date(
            station_date_hour_presence_counts,
            represented_utc_date_counts,
        )
    )
    (
        station_success_support_per_utc_date,
        station_counter_support_per_utc_date,
    ) = _partition_average_station_support(
        station_average_support_per_utc_date,
        station_balanced,
    )
    return {
        "utc_hours": np.arange(24, dtype=np.int64),
        "station_balanced_rate_pct": station_balanced,
        "observation_level_rate_pct": observation_level,
        "station_success_votes": station_success_votes,
        "station_counter_votes": station_counter_votes,
        "station_date_hour_presence_counts": (
            station_date_hour_presence_counts
        ),
        "station_average_support_per_utc_date": (
            station_average_support_per_utc_date
        ),
        "station_success_support_per_utc_date": (
            station_success_support_per_utc_date
        ),
        "station_counter_support_per_utc_date": (
            station_counter_support_per_utc_date
        ),
        "opportunity_success_counts": target_counts,
        "opportunity_counter_counts": counter_counts,
        "opportunity_success_counts_per_utc_date": (
            _average_folded_counts_per_represented_date(
                target_counts,
                represented_utc_date_counts,
            )
        ),
        "opportunity_counter_counts_per_utc_date": (
            _average_folded_counts_per_represented_date(
                counter_counts,
                represented_utc_date_counts,
            )
        ),
        "target_counts": target_counts,
        "counter_counts": counter_counts,
        "station_counts": station_counts,
        "utc_date_counts": utc_date_counts,
        "represented_utc_date_counts": represented_utc_date_counts,
    }


def _prepare_success_snr_anomalies(work):
    """Return successful rows centered on baselines from at least three decodes."""
    successful = work[
        (work["hit"] > 0)
        & pd.to_numeric(work["target_snr"], errors="coerce").notna()
    ].copy()
    successful["target_snr"] = pd.to_numeric(
        successful["target_snr"],
        errors="coerce",
    )
    if successful.empty:
        successful["station_baseline_snr_db"] = pd.Series(dtype=float)
        successful["snr_anomaly_db"] = pd.Series(dtype=float)
        return successful, pd.DataFrame(
            columns=[
                "peer_sign",
                "peer_grid",
                "successful_snr_observation_count",
                "station_baseline_snr_db",
            ]
        )

    station_baselines = (
        successful.groupby(
            ["peer_sign", "peer_grid"],
            dropna=False,
            observed=True,
        )["target_snr"]
        .agg(
            successful_snr_observation_count="size",
            station_baseline_snr_db="median",
        )
        .reset_index()
    )
    station_baselines = station_baselines[
        station_baselines["successful_snr_observation_count"]
        >= SUCCESS_MINIMUM_SNR_BASELINE_OBSERVATIONS
    ].copy()
    successful = successful.merge(
        station_baselines,
        on=["peer_sign", "peer_grid"],
        how="inner",
    )
    successful["snr_anomaly_db"] = (
        successful["target_snr"]
        - successful["station_baseline_snr_db"]
    )
    return successful, station_baselines


def _success_snr_anomaly_axis(anomaly_values):
    """Return integer-dB centers and half-step edges including the 0 dB baseline."""
    numeric = pd.to_numeric(
        pd.Series(anomaly_values, copy=False),
        errors="coerce",
    ).to_numpy(dtype=float, copy=True)
    numeric = numeric[np.isfinite(numeric)]
    if len(numeric):
        minimum_db = min(-1, int(np.floor(numeric.min())))
        maximum_db = max(1, int(np.ceil(numeric.max())))
    else:
        minimum_db = -1
        maximum_db = 1
    centers_db = np.arange(
        minimum_db,
        maximum_db + 1,
        dtype=float,
    )
    edges_db = np.arange(
        minimum_db - 0.5,
        maximum_db + 1.5,
        dtype=float,
    )
    return centers_db, edges_db


def _success_relative_density_grid(
    x_indexes,
    anomaly_values,
    *,
    x_count,
    anomaly_centers_db,
):
    """Return an occupied-cell grid normalized to this panel's maximum cell."""
    x_indexes = np.asarray(x_indexes, dtype=np.int64)
    anomalies = pd.to_numeric(
        pd.Series(anomaly_values, copy=False),
        errors="coerce",
    ).to_numpy(dtype=float, copy=True)
    grid = np.zeros(
        (len(anomaly_centers_db), int(x_count)),
        dtype=float,
    )
    if not len(x_indexes) or not len(anomalies):
        grid[:] = np.nan
        return grid

    finite_anomalies = np.isfinite(anomalies)
    y_indexes = np.full(len(anomalies), -1, dtype=np.int64)
    y_indexes[finite_anomalies] = (
        np.floor(anomalies[finite_anomalies] + 0.5)
        - float(anomaly_centers_db[0])
    ).astype(np.int64)
    valid = (
        finite_anomalies
        & (x_indexes >= 0)
        & (x_indexes < int(x_count))
        & (y_indexes >= 0)
        & (y_indexes < len(anomaly_centers_db))
    )
    np.add.at(grid, (y_indexes[valid], x_indexes[valid]), 1.0)
    maximum = float(grid.max()) if grid.size else 0.0
    if maximum > 0.0:
        grid = np.where(
            grid > 0.0,
            100.0 * grid / maximum,
            np.nan,
        )
    else:
        grid[:] = np.nan
    return grid


def _aggregate_success_chronological_snr(
    anomaly_rows,
    start,
    end,
    time_bin,
    anomaly_centers_db,
    anomaly_edges_db,
):
    """Aggregate at most one station-median anomaly into each chronological bin."""
    bin_minutes = _time_agg_minutes(time_bin)
    bin_delta = pd.Timedelta(minutes=bin_minutes)
    bin_count = max(1, int(np.ceil((end - start) / bin_delta)))
    median_trace = np.full(bin_count, np.nan, dtype=float)
    station_value_counts = np.zeros(bin_count, dtype=np.int64)
    if anomaly_rows.empty:
        station_bins = pd.DataFrame(
            columns=["bin_index", "snr_anomaly_db"]
        )
    else:
        binned = anomaly_rows.copy()
        binned["bin_index"] = (
            (binned["evidence_utc"] - start) // bin_delta
        ).astype("int64")
        station_bins = (
            binned.groupby(
                ["bin_index", "peer_sign", "peer_grid"],
                dropna=False,
                observed=True,
            )["snr_anomaly_db"]
            .median()
            .reset_index()
        )
        station_bins = station_bins[
            station_bins["bin_index"].between(0, bin_count - 1)
        ].copy()
        if not station_bins.empty:
            medians = station_bins.groupby(
                "bin_index",
                observed=True,
            )["snr_anomaly_db"].median()
            counts = station_bins.groupby(
                "bin_index",
                observed=True,
            ).size()
            median_indexes = medians.index.to_numpy(
                dtype=np.int64,
                copy=False,
            )
            median_trace[median_indexes] = medians.to_numpy(
                dtype=float,
                copy=False,
            )
            station_value_counts[
                counts.index.to_numpy(dtype=np.int64, copy=False)
            ] = counts.to_numpy(dtype=np.int64, copy=False)
    return {
        "snr_anomaly_centers_db": np.asarray(
            anomaly_centers_db,
            dtype=float,
        ).copy(),
        "snr_anomaly_edges_db": np.asarray(
            anomaly_edges_db,
            dtype=float,
        ).copy(),
        "snr_density_pct": _success_relative_density_grid(
            station_bins.get("bin_index", pd.Series(dtype="int64")),
            station_bins.get("snr_anomaly_db", pd.Series(dtype=float)),
            x_count=bin_count,
            anomaly_centers_db=anomaly_centers_db,
        ),
        "snr_station_balanced_median_db": median_trace,
        "snr_station_value_counts": station_value_counts,
    }


def _aggregate_success_folded_snr(
    anomaly_rows,
    anomaly_centers_db,
    anomaly_edges_db,
):
    """Aggregate one station-date-hour median anomaly into each UTC hour."""
    median_trace = np.full(24, np.nan, dtype=float)
    station_value_counts = np.zeros(24, dtype=np.int64)
    if anomaly_rows.empty:
        station_date_hours = pd.DataFrame(
            columns=["utc_hour", "snr_anomaly_db"]
        )
    else:
        folded = anomaly_rows.copy()
        folded["utc_hour"] = folded["evidence_utc"].dt.hour.astype("int8")
        folded["utc_date"] = folded["evidence_utc"].dt.normalize()
        station_date_hours = (
            folded.groupby(
                [
                    "utc_hour",
                    "utc_date",
                    "peer_sign",
                    "peer_grid",
                ],
                dropna=False,
                observed=True,
            )["snr_anomaly_db"]
            .median()
            .reset_index()
        )
        if not station_date_hours.empty:
            medians = station_date_hours.groupby(
                "utc_hour",
                observed=True,
            )["snr_anomaly_db"].median()
            counts = station_date_hours.groupby(
                "utc_hour",
                observed=True,
            ).size()
            median_trace[
                medians.index.to_numpy(dtype=np.int64, copy=False)
            ] = medians.to_numpy(dtype=float, copy=False)
            station_value_counts[
                counts.index.to_numpy(dtype=np.int64, copy=False)
            ] = counts.to_numpy(dtype=np.int64, copy=False)
    return {
        "snr_anomaly_centers_db": np.asarray(
            anomaly_centers_db,
            dtype=float,
        ).copy(),
        "snr_anomaly_edges_db": np.asarray(
            anomaly_edges_db,
            dtype=float,
        ).copy(),
        "snr_density_pct": _success_relative_density_grid(
            station_date_hours.get(
                "utc_hour",
                pd.Series(dtype="int64"),
            ),
            station_date_hours.get(
                "snr_anomaly_db",
                pd.Series(dtype=float),
            ),
            x_count=24,
            anomaly_centers_db=anomaly_centers_db,
        ),
        "snr_station_balanced_median_db": median_trace,
        "snr_station_value_counts": station_value_counts,
    }


def _prepare_success_actual_snr(work):
    """Return every finite normalized Target SNR from successful outcomes."""
    successful_rows = work[
        (work["hit"] > 0)
        & pd.to_numeric(work["target_snr"], errors="coerce").notna()
    ].copy()
    successful_rows["target_snr"] = pd.to_numeric(
        successful_rows["target_snr"],
        errors="coerce",
    )
    return successful_rows.loc[
        successful_rows["evidence_utc"].notna()
        & np.isfinite(successful_rows["target_snr"])
    ].copy()


def _success_actual_snr_axis(actual_snr_values):
    """Return padded half-step edges around readable integer-dB SNR centers."""
    numeric_values = pd.to_numeric(
        pd.Series(actual_snr_values, copy=False),
        errors="coerce",
    ).to_numpy(dtype=float, copy=True)
    numeric_values = numeric_values[np.isfinite(numeric_values)]
    if len(numeric_values):
        lower_center_db = int(np.floor(numeric_values.min())) - 1
        upper_center_db = int(np.ceil(numeric_values.max())) + 1
    else:
        lower_center_db = -35
        upper_center_db = 5
    if upper_center_db <= lower_center_db:
        upper_center_db = lower_center_db + 2
    return np.arange(
        lower_center_db - 0.5,
        upper_center_db + 1.5,
        dtype=float,
    )


def _success_relative_density_grid_from_edges(
    x_indexes,
    snr_values,
    *,
    x_count,
    snr_edges_db,
):
    """Return independently normalized density using explicit actual-SNR bins."""
    x_indexes = np.asarray(x_indexes, dtype=np.int64)
    values = pd.to_numeric(
        pd.Series(snr_values, copy=False),
        errors="coerce",
    ).to_numpy(dtype=float, copy=True)
    edges = np.asarray(snr_edges_db, dtype=float)
    if len(edges) < 2 or np.any(np.diff(edges) <= 0.0):
        raise ValueError(
            "Actual Success SNR density requires increasing dB edges."
        )
    if len(x_indexes) != len(values):
        raise ValueError(
            "Actual Success SNR density values must match their x indexes."
        )
    density_grid = np.zeros(
        (len(edges) - 1, int(x_count)),
        dtype=float,
    )
    if not len(x_indexes):
        density_grid[:] = np.nan
        return density_grid

    y_indexes = np.searchsorted(edges, values, side="right") - 1
    valid = (
        np.isfinite(values)
        & (x_indexes >= 0)
        & (x_indexes < int(x_count))
        & (y_indexes >= 0)
        & (y_indexes < len(edges) - 1)
    )
    np.add.at(density_grid, (y_indexes[valid], x_indexes[valid]), 1.0)
    maximum = float(density_grid.max()) if density_grid.size else 0.0
    if maximum > 0.0:
        density_grid = np.where(
            density_grid > 0.0,
            100.0 * density_grid / maximum,
            np.nan,
        )
    else:
        density_grid[:] = np.nan
    return density_grid


def _aggregate_success_chronological_actual_snr(
    successful_rows,
    start,
    end,
    time_bin,
    snr_edges_db,
):
    """Aggregate all selected-station successful SNR observations by time bin."""
    bin_delta = pd.Timedelta(minutes=_time_agg_minutes(time_bin))
    bin_count = max(1, int(np.ceil((end - start) / bin_delta)))
    median_trace = np.full(bin_count, np.nan, dtype=float)
    value_counts = np.zeros(bin_count, dtype=np.int64)
    if successful_rows.empty:
        binned_rows = pd.DataFrame(columns=["bin_index", "target_snr"])
    else:
        binned_rows = successful_rows.copy()
        binned_rows["bin_index"] = (
            (binned_rows["evidence_utc"] - start) // bin_delta
        ).astype("int64")
        binned_rows = binned_rows[
            binned_rows["bin_index"].between(0, bin_count - 1)
        ].copy()
        if not binned_rows.empty:
            medians = binned_rows.groupby(
                "bin_index",
                observed=True,
            )["target_snr"].median()
            counts = binned_rows.groupby(
                "bin_index",
                observed=True,
            ).size()
            indexes = medians.index.to_numpy(dtype=np.int64, copy=False)
            median_trace[indexes] = medians.to_numpy(
                dtype=float,
                copy=False,
            )
            value_counts[
                counts.index.to_numpy(dtype=np.int64, copy=False)
            ] = counts.to_numpy(dtype=np.int64, copy=False)
    return {
        "snr_value_edges_db": np.asarray(
            snr_edges_db,
            dtype=float,
        ).copy(),
        "snr_density_pct": _success_relative_density_grid_from_edges(
            binned_rows.get("bin_index", pd.Series(dtype="int64")),
            binned_rows.get("target_snr", pd.Series(dtype=float)),
            x_count=bin_count,
            snr_edges_db=snr_edges_db,
        ),
        "snr_median_db": median_trace,
        "snr_value_counts": value_counts,
    }


def _aggregate_success_folded_actual_snr(
    successful_rows,
    snr_edges_db,
):
    """Fold one selected-station median per represented date-hour."""
    median_trace = np.full(24, np.nan, dtype=float)
    value_counts = np.zeros(24, dtype=np.int64)
    if successful_rows.empty:
        date_hour_medians = pd.DataFrame(
            columns=["utc_hour", "target_snr"]
        )
    else:
        folded_rows = successful_rows.copy()
        folded_rows["utc_hour"] = (
            folded_rows["evidence_utc"].dt.hour.astype("int8")
        )
        folded_rows["utc_date"] = (
            folded_rows["evidence_utc"].dt.normalize()
        )
        date_hour_medians = (
            folded_rows.groupby(
                ["utc_hour", "utc_date"],
                dropna=False,
                observed=True,
            )["target_snr"]
            .median()
            .reset_index()
        )
        if not date_hour_medians.empty:
            medians = date_hour_medians.groupby(
                "utc_hour",
                observed=True,
            )["target_snr"].median()
            counts = date_hour_medians.groupby(
                "utc_hour",
                observed=True,
            ).size()
            indexes = medians.index.to_numpy(dtype=np.int64, copy=False)
            median_trace[indexes] = medians.to_numpy(
                dtype=float,
                copy=False,
            )
            value_counts[
                counts.index.to_numpy(dtype=np.int64, copy=False)
            ] = counts.to_numpy(dtype=np.int64, copy=False)
    return {
        "snr_value_edges_db": np.asarray(
            snr_edges_db,
            dtype=float,
        ).copy(),
        "snr_density_pct": _success_relative_density_grid_from_edges(
            date_hour_medians.get(
                "utc_hour",
                pd.Series(dtype="int64"),
            ),
            date_hour_medians.get(
                "target_snr",
                pd.Series(dtype=float),
            ),
            x_count=24,
            snr_edges_db=snr_edges_db,
        ),
        "snr_median_db": median_trace,
        "snr_value_counts": value_counts,
    }


def _success_selected_station_summary(peer_df, work):
    """Return exact retained-run context for one selected station identity."""
    identity_rows = work[["peer_sign", "peer_grid"]].drop_duplicates()
    if identity_rows.empty:
        identity_rows = peer_df[["peer_sign", "peer_grid"]].drop_duplicates()
    if len(identity_rows) != 1:
        raise ValueError(
            "Selected-station context requires exactly one "
            "callsign-plus-locator identity."
        )
    peer_sign, peer_grid = identity_rows.iloc[0].astype(str)
    matching_peers = peer_df[
        (peer_df["peer_sign"].astype(str) == peer_sign)
        & (peer_df["peer_grid"].astype(str) == peer_grid)
    ]
    peer_values = (
        matching_peers.iloc[0].to_dict()
        if not matching_peers.empty
        else {}
    )
    successful_count = int(
        pd.to_numeric(
            work.get("hit", pd.Series(dtype=float)),
            errors="coerce",
        ).fillna(0).sum()
    )
    counter_count = int(
        pd.to_numeric(
            work.get("miss", pd.Series(dtype=float)),
            errors="coerce",
        ).fillna(0).sum()
    )
    confirmed_count = successful_count + counter_count
    successful_snr_values = pd.to_numeric(
        work.loc[
            pd.to_numeric(work["hit"], errors="coerce").fillna(0) > 0,
            "target_snr",
        ],
        errors="coerce",
    )
    successful_snr_values = successful_snr_values.loc[
        np.isfinite(successful_snr_values)
    ]

    def numeric_peer_value(column_name):
        """Return one finite station-level numeric value or NaN."""
        numeric_value = pd.to_numeric(
            pd.Series([peer_values.get(column_name)]),
            errors="coerce",
        ).iloc[0]
        return (
            float(numeric_value)
            if pd.notna(numeric_value) and np.isfinite(float(numeric_value))
            else np.nan
        )

    return {
        "peer_sign": peer_sign,
        "peer_grid": peer_grid,
        "distance_km": numeric_peer_value("calc_dist"),
        "azimuth_degrees": numeric_peer_value("calc_azimuth"),
        "direction": str(peer_values.get("dir_name", "")),
        "confirmed_opportunities": confirmed_count,
        "successful_outcomes": successful_count,
        "counter_outcomes": counter_count,
        "success_rate_pct": (
            100.0 * successful_count / confirmed_count
            if confirmed_count
            else np.nan
        ),
        "successful_snr_median_db": (
            float(successful_snr_values.median())
            if not successful_snr_values.empty
            else np.nan
        ),
    }


def _opportunity_temporal_recipe(
    title,
    selected_segment,
    peer_df,
    rows,
    analysis_start_t,
    analysis_end_t,
    terminology,
    *,
    figure_labels,
    snr_title=None,
    population_mode=SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
    snr_representation=SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE,
):
    """Build shared Success temporal evidence for one population and SNR mode.

    ``active_scope`` preserves the established equal-station temporal contract.
    ``selected_station`` requires exactly one eligible callsign-plus-locator
    identity. SNR can remain station-relative or use every retained successful
    normalized Target observation from that selected station.
    """
    population_mode = str(population_mode)
    snr_representation = str(snr_representation)
    if population_mode not in SUCCESS_TEMPORAL_POPULATION_MODES:
        raise ValueError(
            f"Unsupported Success temporal population mode: {population_mode}"
        )
    if snr_representation not in SUCCESS_SNR_REPRESENTATIONS:
        raise ValueError(
            "Unsupported Success temporal SNR representation: "
            f"{snr_representation}"
        )
    common_label_keys = (
        "evidence_chronological_title",
        "evidence_utc_hour_title",
        "station_support_folded_subtitle",
        "opportunity_folded_subtitle",
        "station_vote_y",
        "station_support_folded_y",
        "opportunity_y",
        "opportunity_folded_y",
        "rate_y",
        "rate_legend",
        "time_x",
        "utc_hour_x",
        "target_evidence",
        "counter_evidence",
        "temporal_unavailable",
        "utc_dates_folded",
    )
    if snr_representation == SUCCESS_SNR_REPRESENTATION_ACTUAL:
        representation_label_keys = (
            "selected_snr_chronological_title",
            "selected_snr_chronological_subtitle",
            "selected_snr_utc_hour_title",
            "selected_snr_utc_hour_subtitle",
            "selected_snr_y",
            "selected_snr_density",
            "selected_bin_median_chronological",
            "selected_bin_median_folded",
            "selected_snr_unavailable",
            "selected_station_support_folded_subtitle",
        )
    else:
        representation_label_keys = (
            "snr_chronological_title",
            "snr_chronological_subtitle",
            "snr_utc_hour_title",
            "snr_utc_hour_subtitle",
            "snr_anomaly_y",
            "snr_density",
            "station_baseline",
            "bin_median_chronological",
            "bin_median_folded",
            "snr_anomaly_unavailable",
        )
    labels = _required_figure_labels(
        figure_labels,
        common_label_keys + representation_label_keys,
    )
    if snr_representation == SUCCESS_SNR_REPRESENTATION_ACTUAL:
        labels.update(
            {
                "snr_chronological_title": labels[
                    "selected_snr_chronological_title"
                ],
                "snr_chronological_subtitle": labels[
                    "selected_snr_chronological_subtitle"
                ],
                "snr_utc_hour_title": labels[
                    "selected_snr_utc_hour_title"
                ],
                "snr_utc_hour_subtitle": labels[
                    "selected_snr_utc_hour_subtitle"
                ],
                "snr_y": labels["selected_snr_y"],
                "snr_density": labels["selected_snr_density"],
                "bin_median_chronological": labels[
                    "selected_bin_median_chronological"
                ],
                "bin_median_folded": labels[
                    "selected_bin_median_folded"
                ],
                "snr_unavailable": labels["selected_snr_unavailable"],
                "station_support_folded_subtitle": labels[
                    "selected_station_support_folded_subtitle"
                ],
            }
        )
    else:
        labels.update(
            {
                "snr_y": labels["snr_anomaly_y"],
                "snr_unavailable": labels["snr_anomaly_unavailable"],
            }
        )
    start = _as_utc_timestamp(analysis_start_t)
    end = _as_utc_timestamp(analysis_end_t)
    if end <= start:
        raise ValueError("Success temporal evidence requires a positive UTC window.")

    eligible_identities = peer_df.loc[
        peer_df["eligible"]
        & pd.to_numeric(peer_df["rate_pct"], errors="coerce").notna(),
        ["peer_sign", "peer_grid"],
    ].drop_duplicates()
    eligible_identities = eligible_identities.astype(str)
    if (
        population_mode == SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
        and len(eligible_identities) != 1
    ):
        raise ValueError(
            "Selected-station temporal evidence requires exactly one "
            "eligible callsign-plus-locator identity."
        )
    required_row_columns = {
        "time_slot",
        "peer_sign",
        "peer_grid",
        "hit",
        "miss",
        "target_snr",
    }
    missing_row_columns = sorted(required_row_columns.difference(rows.columns))
    if missing_row_columns:
        raise ValueError(
            "Success temporal evidence rows are missing columns: "
            + ", ".join(missing_row_columns)
        )
    work = rows.loc[
        :,
        [
            "time_slot",
            "peer_sign",
            "peer_grid",
            "hit",
            "miss",
            "target_snr",
        ],
    ].copy()
    work["peer_sign"] = work["peer_sign"].astype(str)
    work["peer_grid"] = work["peer_grid"].astype(str)
    work = work.merge(
        eligible_identities,
        on=["peer_sign", "peer_grid"],
        how="inner",
    )
    work["hit"] = pd.to_numeric(work["hit"], errors="coerce").fillna(0).astype(
        "int64"
    )
    work["miss"] = pd.to_numeric(work["miss"], errors="coerce").fillna(0).astype(
        "int64"
    )
    work["target_snr"] = pd.to_numeric(
        work["target_snr"],
        errors="coerce",
    )
    work = work[(work["hit"] + work["miss"]) > 0].copy()
    work["evidence_utc"] = opportunity_utc_from_time_slot(work["time_slot"])
    work = work[
        work["evidence_utc"].notna()
        & work["evidence_utc"].ge(start)
        & work["evidence_utc"].lt(end)
    ].copy()
    if population_mode == SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION:
        selected_work_identities = work[
            ["peer_sign", "peer_grid"]
        ].drop_duplicates()
        if len(selected_work_identities) > 1:
            raise ValueError(
                "Selected-station temporal evidence contains multiple "
                "callsign-plus-locator identities."
            )

    station_baselines = pd.DataFrame()
    successful_actual_snr_rows = pd.DataFrame()
    if snr_representation == SUCCESS_SNR_REPRESENTATION_ACTUAL:
        successful_actual_snr_rows = _prepare_success_actual_snr(work)
        actual_snr_edges_db = _success_actual_snr_axis(
            successful_actual_snr_rows.get(
                "target_snr",
                pd.Series(dtype=float),
            )
        )
    else:
        anomaly_rows, station_baselines = _prepare_success_snr_anomalies(work)
        anomaly_centers_db, anomaly_edges_db = _success_snr_anomaly_axis(
            anomaly_rows.get("snr_anomaly_db", pd.Series(dtype=float))
        )
    profiles = {}
    for time_bin in SUCCESS_TEMPORAL_TIME_BINS:
        profile = _aggregate_success_chronological_profile(
            work,
            start,
            end,
            time_bin,
        )
        if snr_representation == SUCCESS_SNR_REPRESENTATION_ACTUAL:
            profile.update(
                _aggregate_success_chronological_actual_snr(
                    successful_actual_snr_rows,
                    start,
                    end,
                    time_bin,
                    actual_snr_edges_db,
                )
            )
        else:
            profile.update(
                _aggregate_success_chronological_snr(
                    anomaly_rows,
                    start,
                    end,
                    time_bin,
                    anomaly_centers_db,
                    anomaly_edges_db,
                )
            )
        profiles[time_bin] = profile
    folded_profile = _aggregate_success_folded_profile(
        work,
        start,
        end,
    )
    if snr_representation == SUCCESS_SNR_REPRESENTATION_ACTUAL:
        folded_profile.update(
            _aggregate_success_folded_actual_snr(
                successful_actual_snr_rows,
                actual_snr_edges_db,
            )
        )
    else:
        folded_profile.update(
            _aggregate_success_folded_snr(
                anomaly_rows,
                anomaly_centers_db,
                anomaly_edges_db,
            )
        )
    utc_date_count = int(work["evidence_utc"].dt.normalize().nunique())
    selected_station_summary = (
        _success_selected_station_summary(peer_df, work)
        if population_mode == SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
        else None
    )
    return {
        "kind": "opportunity_success_temporal",
        "schema_version": 7,
        "population_mode": population_mode,
        "snr_representation": snr_representation,
        "snr_baseline_version": (
            SUCCESS_SNR_BASELINE_VERSION
            if snr_representation
            == SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE
            else None
        ),
        "actual_snr_axis_policy": (
            "integer-db-centers-full-observation-envelope-v1"
            if snr_representation == SUCCESS_SNR_REPRESENTATION_ACTUAL
            else None
        ),
        "folded_opportunity_normalization": (
            "sum-outcomes-per-represented-utc-date-v1"
        ),
        "folded_station_support_policy": (
            "station-date-hour-presence-per-represented-utc-date-"
            "partitioned-by-pooled-station-rate-v1"
        ),
        "minimum_snr_baseline_observations": (
            SUCCESS_MINIMUM_SNR_BASELINE_OBSERVATIONS
            if snr_representation
            == SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE
            else None
        ),
        "snr_baseline_station_count": int(len(station_baselines)),
        "title": str(title),
        "evidence_title": str(title),
        "snr_title": str(snr_title if snr_title is not None else title),
        "selected_segment": str(selected_segment),
        "absolute_mode": terminology.get("mode", "RX"),
        "terminology": dict(terminology),
        "labels": labels,
        "time_bin_options": list(SUCCESS_TEMPORAL_TIME_BINS),
        "time_bin_default": _opportunity_time_bin(
            work,
            analysis_start_t,
            analysis_end_t,
        ),
        "time_bin": _opportunity_time_bin(
            work,
            analysis_start_t,
            analysis_end_t,
        ),
        "chronological_profiles": profiles,
        "folded_profile": folded_profile,
        "utc_date_count": utc_date_count,
        "selected_station_summary": selected_station_summary,
    }


def _draw_success_outcome_stack(
    axis,
    x_values,
    success_values,
    counter_values,
    labels,
    *,
    bar_width,
    y_label,
    gid_prefix,
    integer_axis,
):
    """Draw one green/grey Success evidence stack on its count axis."""
    success = np.asarray(success_values, dtype=float)
    counter = np.asarray(counter_values, dtype=float)
    x = np.asarray(x_values, dtype=float)
    if len(success) != len(x) or len(counter) != len(x):
        raise ValueError(
            "Success temporal outcome arrays must match their time axis."
        )
    success_bars = axis.bar(
        x,
        success,
        width=bar_width,
        color=SUCCESS_OUTCOME_COLOR,
        edgecolor="#111111",
        linewidth=0.35,
        label=labels["target_evidence"],
        zorder=2,
    )
    counter_bars = axis.bar(
        x,
        counter,
        width=bar_width,
        bottom=success,
        color=SUCCESS_COUNTER_OUTCOME_COLOR,
        edgecolor="#111111",
        linewidth=0.35,
        label=labels["counter_evidence"],
        zorder=2,
    )
    for bar in success_bars:
        bar.set_gid(f"{gid_prefix}-success")
    for bar in counter_bars:
        bar.set_gid(f"{gid_prefix}-counter")
    _set_metric_axis_labels(axis, y_label=y_label)
    axis.set_ylim(bottom=0.0)
    axis.yaxis.set_major_locator(
        mpl.ticker.MaxNLocator(
            nbins=5,
            min_n_ticks=3,
            integer=bool(integer_axis),
        )
    )
    axis.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(_format_ham_compact_count)
    )
    return success_bars, counter_bars


def _format_ham_compact_count(value, _position=None):
    """Format a count with compact ham-style decimal-prefix notation."""
    numeric_value = float(value)
    if not np.isfinite(numeric_value):
        return ""
    if np.isclose(numeric_value, 0.0):
        return "0"

    sign = "-" if numeric_value < 0.0 else ""
    magnitude = abs(numeric_value)
    if magnitude < 1000.0:
        if np.isclose(magnitude, round(magnitude), atol=1e-9):
            body = str(int(round(magnitude)))
        else:
            if magnitude < 10.0:
                decimal_places = 2
            elif magnitude < 100.0:
                decimal_places = 1
            else:
                decimal_places = 0
            body = f"{magnitude:.{decimal_places}f}"
            if "." in body:
                body = body.rstrip("0").rstrip(".")
        return sign + body

    scale_definitions = (
        (1_000_000_000.0, "G"),
        (1_000_000.0, "M"),
        (1_000.0, "k"),
    )
    scale, prefix = next(
        (scale, prefix)
        for scale, prefix in scale_definitions
        if magnitude >= scale
    )
    scaled = magnitude / scale
    if scaled < 10.0:
        decimal_places = 2
    elif scaled < 100.0:
        decimal_places = 1
    else:
        decimal_places = 0
    rounded = round(scaled, decimal_places)
    if rounded >= 1000.0 and prefix != "G":
        promoted_scale = scale * 1000.0
        promoted_prefix = "M" if prefix == "k" else "G"
        rounded = magnitude / promoted_scale
        prefix = promoted_prefix
        decimal_places = 2 if rounded < 10.0 else 1

    mantissa = f"{rounded:.{decimal_places}f}"
    if "." in mantissa:
        mantissa = mantissa.rstrip("0").rstrip(".")
    if "." in mantissa:
        whole, fraction = mantissa.split(".", maxsplit=1)
        body = f"{whole}{prefix}{fraction}"
    else:
        body = f"{mantissa}{prefix}"
    return sign + body


def _success_temporal_rate_axis_max(*rate_series):
    """Return one rounded 20%-headroom ceiling shared by four rate axes."""
    finite_rates = []
    for rates in rate_series:
        numeric_rates = np.asarray(rates, dtype=float).ravel()
        finite_rates.extend(
            numeric_rates[
                np.isfinite(numeric_rates) & (numeric_rates >= 0.0)
            ].tolist()
        )
    maximum_rate = max(finite_rates, default=0.0)
    requested_ceiling = min(100.0, maximum_rate * 1.20)
    for ceiling in SUCCESS_TEMPORAL_RATE_CEILINGS:
        if requested_ceiling <= ceiling:
            return float(ceiling)
    return 100.0


def _place_success_temporal_panel_subtitle(
    axis,
    subtitle,
    *,
    gid="success-temporal-panel-subtitle",
    y=1.01,
):
    """Place one localized Success temporal subtitle above its data axis."""
    subtitle_artist = axis.text(
        0.5,
        float(y),
        str(subtitle),
        transform=axis.transAxes,
        color="white",
        fontsize=METRIC_LEGEND_FONTSIZE,
        fontweight="normal",
        fontfamily=METRIC_FONT_FAMILY,
        ha="center",
        va="bottom",
        wrap=True,
    )
    subtitle_artist.set_gid(gid)
    return subtitle_artist


def _set_success_temporal_panel_title(axis, title, subtitle):
    """Apply the Success temporal title/subtitle typography hierarchy."""
    title_artist = _set_temporal_panel_title(
        axis,
        title,
        y=1.06,
        pad=0,
    )
    title_artist.set_wrap(True)
    return _place_success_temporal_panel_subtitle(axis, subtitle)


def _draw_success_rate_overlay(
    count_axis,
    x_values,
    rate_values,
    labels,
    *,
    upper_limit,
    gid_suffix,
):
    """Draw one Success Rate line on a secondary right y-axis."""
    x = np.asarray(x_values, dtype=float)
    rates = np.asarray(rate_values, dtype=float)
    if len(rates) != len(x):
        raise ValueError(
            "Success temporal rates must match their time axis."
        )
    rate_axis = count_axis.twinx()
    rate_axis.set_position(count_axis.get_position(), which="both")
    rate_axis.set_gid(f"success-temporal-{gid_suffix}-rate-axis")
    rate_axis.patch.set_visible(False)
    rate_axis.tick_params(
        axis="y",
        colors=SUCCESS_RATE_LINE_COLOR,
        labelsize=8,
    )
    rate_axis.spines["right"].set_color("#5f7177")
    rate_axis.spines["top"].set_color("#444444")
    rate_axis.spines["left"].set_visible(False)
    rate_axis.set_ylim(0.0, float(upper_limit))
    rate_axis.yaxis.set_major_locator(
        mpl.ticker.MaxNLocator(nbins=5, min_n_ticks=3)
    )
    _set_metric_axis_labels(
        rate_axis,
        y_label=labels["rate_y"],
        y_color=SUCCESS_RATE_LINE_COLOR,
    )
    rate_axis.yaxis.labelpad = 1.0
    rate_line = rate_axis.plot(
        x,
        rates,
        color=SUCCESS_RATE_LINE_COLOR,
        marker="o",
        markersize=3.0,
        linewidth=1.2,
        label=labels["rate_legend"],
        zorder=5,
    )[0]
    rate_line.set_gid(f"success-temporal-{gid_suffix}-rate")
    return rate_axis, rate_line


def _place_success_outcome_legend(figure, labels):
    """Place one three-entry legend directly below the lower figure title."""
    handles = [
        mpl.patches.Patch(
            facecolor=SUCCESS_OUTCOME_COLOR,
            edgecolor="#111111",
            label=labels["target_evidence"],
        ),
        mpl.patches.Patch(
            facecolor=SUCCESS_COUNTER_OUTCOME_COLOR,
            edgecolor="#111111",
            label=labels["counter_evidence"],
        ),
        mpl.lines.Line2D(
            [],
            [],
            color=SUCCESS_RATE_LINE_COLOR,
            marker="o",
            markersize=3.0,
            linewidth=1.2,
            label=labels["rate_legend"],
        ),
    ]
    _place_metric_legend(
        figure,
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.895),
        borderaxespad=0.0,
        ncol=3,
        columnspacing=1.2,
        handletextpad=0.5,
        gid="success-temporal-outcome-legend",
    )


def _draw_success_snr_density_panel(
    axis,
    x_edges,
    x_centers,
    profile,
    labels,
    title,
    subtitle,
    median_label,
    snr_representation,
):
    """Draw one shared successful-SNR density panel and its median trace."""
    is_actual_snr = (
        snr_representation == SUCCESS_SNR_REPRESENTATION_ACTUAL
    )
    snr_edges_db = np.asarray(
        profile.get(
            "snr_value_edges_db"
            if is_actual_snr
            else "snr_anomaly_edges_db",
            [],
        ),
        dtype=float,
    )
    density_pct = np.asarray(
        profile.get("snr_density_pct", []),
        dtype=float,
    )
    expected_shape = (
        max(0, len(snr_edges_db) - 1),
        max(0, len(x_edges) - 1),
    )
    if density_pct.shape != expected_shape:
        raise ValueError(
            "Success temporal SNR density does not match its time and dB axes."
        )
    mesh = axis.pcolormesh(
        x_edges,
        snr_edges_db,
        np.ma.masked_invalid(density_pct),
        cmap=EVIDENCE_HEATMAP_CMAP,
        vmin=EVIDENCE_DENSITY_MIN,
        vmax=EVIDENCE_DENSITY_MAX,
        shading="flat",
        zorder=2,
    )
    mesh.set_gid("success-temporal-snr-density")
    legend_handles = []
    if not is_actual_snr:
        baseline_line = axis.axhline(
            0.0,
            color="#f4f1e8",
            linewidth=1.0,
            linestyle="dashed",
            label=labels["station_baseline"],
            zorder=4,
        )
        baseline_line.set_gid("success-temporal-snr-baseline")
        legend_handles.append(baseline_line)
    median_trace = np.asarray(
        profile.get(
            "snr_median_db"
            if is_actual_snr
            else "snr_station_balanced_median_db",
            [],
        ),
        dtype=float,
    )
    median_line = axis.plot(
        x_centers,
        median_trace,
        color="white",
        marker="o",
        markersize=2.8,
        linewidth=1.2,
        label=median_label,
        zorder=5,
    )[0]
    median_line.set_gid("success-temporal-snr-bin-median")
    legend_handles.append(median_line)
    axis.set_ylim(snr_edges_db[0], snr_edges_db[-1])
    if is_actual_snr:
        axis.yaxis.set_major_locator(
            mpl.ticker.MaxNLocator(nbins=7, integer=True)
        )
    _set_success_temporal_panel_title(
        axis,
        title,
        subtitle,
    )
    _set_metric_axis_labels(
        axis,
        y_label=labels["snr_y"],
    )
    _place_metric_legend(
        axis,
        handles=legend_handles,
        loc="upper right",
        borderaxespad=0.0,
        gid="success-temporal-snr-legend",
    )
    if not np.isfinite(density_pct).any():
        axis.text(
            0.5,
            0.5,
            labels["snr_unavailable"],
            transform=axis.transAxes,
            color="#cccccc",
            fontsize=8.5,
            ha="center",
            va="center",
        )
    return mesh


def _success_temporal_render_context(recipe):
    """Resolve and validate the shared profile and axes for both figure blocks."""
    if int(recipe.get("schema_version", 0)) != 7:
        raise ValueError("Unsupported Success temporal recipe schema.")
    population_mode = str(
        recipe.get(
            "population_mode",
            SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
        )
    )
    snr_representation = str(
        recipe.get(
            "snr_representation",
            SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE,
        )
    )
    if population_mode not in SUCCESS_TEMPORAL_POPULATION_MODES:
        raise ValueError(
            f"Unsupported Success temporal population mode: {population_mode}"
        )
    if snr_representation not in SUCCESS_SNR_REPRESENTATIONS:
        raise ValueError(
            "Unsupported Success temporal SNR representation: "
            f"{snr_representation}"
        )
    labels = dict(recipe.get("labels") or {})
    selected_time_bin = str(recipe.get("time_bin", "1h"))
    profiles = recipe.get("chronological_profiles") or {}
    if selected_time_bin not in profiles:
        raise ValueError(
            f"Unsupported Success temporal time bin: {selected_time_bin}"
        )
    chronological = dict(profiles[selected_time_bin])
    chronological_centers = pd.to_datetime(
        np.asarray(chronological.get("time_ns", []), dtype=np.int64),
        unit="ns",
        utc=True,
    ).tz_convert(None)
    chronological_edges = pd.to_datetime(
        np.asarray(chronological.get("time_edge_ns", []), dtype=np.int64),
        unit="ns",
        utc=True,
    ).tz_convert(None)
    chronological_center_numbers = mdates.date2num(
        chronological_centers.to_pydatetime()
    )
    chronological_edge_numbers = mdates.date2num(
        chronological_edges.to_pydatetime()
    )
    if len(chronological_edge_numbers) != len(chronological_center_numbers) + 1:
        raise ValueError(
            "Success temporal chronological edges must bound every time bin."
        )
    utc_date_count = int(recipe.get("utc_date_count", 0))
    return {
        "labels": labels,
        "population_mode": population_mode,
        "snr_representation": snr_representation,
        "selected_time_bin": selected_time_bin,
        "display_time_bin": selected_time_bin.replace("h", " h"),
        "chronological": chronological,
        "folded": dict(recipe.get("folded_profile") or {}),
        "utc_date_count": utc_date_count,
        "folding_available": utc_date_count >= 2,
        "chronological_centers": chronological_center_numbers,
        "chronological_edges": chronological_edge_numbers,
        "folded_edges": np.arange(25, dtype=float),
        "folded_centers": np.arange(24, dtype=float) + 0.5,
    }


def _create_success_temporal_figure(recipe, *, title_key, figure_top):
    """Create one Success temporal canvas with its routed title and footer."""
    figure = create_agg_figure(
        figsize=SEGMENT_TEMPORAL_FIGURE_SIZE_INCHES,
        facecolor="black",
    )
    figure.subplots_adjust(
        left=SEGMENT_TEMPORAL_FIGURE_LEFT,
        right=SEGMENT_TEMPORAL_FIGURE_RIGHT,
        bottom=SEGMENT_FIGURE_BOTTOM,
        top=float(figure_top),
        wspace=SEGMENT_TEMPORAL_COLUMN_SPACE,
    )
    figure_title = recipe.get(title_key, recipe.get("title", ""))
    if (
        recipe.get("population_mode")
        == SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
    ):
        complete_title = str(figure_title)
    else:
        complete_title = (
            f"{figure_title} — {recipe.get('selected_segment', '')}"
        )
    figure.suptitle(
        complete_title,
        color="white",
        fontweight="bold",
        fontsize=METRIC_FIGURE_TITLE_FONTSIZE,
        y=0.96,
    )
    figure.text(
        0.98,
        SEGMENT_FIGURE_FOOTER_Y,
        f"WSPRadar.org {APP_VERSION}",
        color="#888888",
        ha="right",
        fontsize=METRIC_FOOTER_FONTSIZE,
    )
    return figure


def _success_temporal_plot_grid(
    figure,
    *,
    row_count,
    folding_available,
    row_space,
    column_space=SEGMENT_TEMPORAL_COLUMN_SPACE,
):
    """Create Success temporal plot columns with caller-selected gutter width."""
    column_count = 2 if folding_available else 1
    grid_kwargs = {
        "nrows": int(row_count),
        "ncols": column_count,
        "hspace": float(row_space),
    }
    if folding_available:
        grid_kwargs.update(
            {
                "width_ratios": SEGMENT_TEMPORAL_COLUMN_WIDTH_RATIOS,
                "wspace": float(column_space),
            }
        )
    return figure.add_gridspec(**grid_kwargs)


def _reserve_success_temporal_colorbar_footprint(figure, axes):
    """Reserve the upper SNR colorbar gutter without adding a lower colorbar."""
    layout_mappable = mpl.cm.ScalarMappable(
        norm=mpl.colors.Normalize(
            vmin=EVIDENCE_DENSITY_MIN,
            vmax=EVIDENCE_DENSITY_MAX,
        ),
        cmap=EVIDENCE_HEATMAP_CMAP,
    )
    reserved_colorbar = figure.colorbar(
        layout_mappable,
        ax=list(axes),
        pad=SEGMENT_TEMPORAL_COLORBAR_PAD,
        fraction=SEGMENT_TEMPORAL_COLORBAR_FRACTION,
    )
    reserved_colorbar.ax.remove()


def _translate_success_temporal_folded_column(*folded_axes):
    """Move the complete lower UTC-hour column into the colorbar footprint.

    The figure-relative translation preserves each panel's width and height.
    Titles, ticks, labels, annotations, and the subsequently created twin axes
    inherit the translated axis transforms.
    """
    for axis in folded_axes:
        position = axis.get_position()
        axis.set_position(
            [
                position.x0 + SUCCESS_TEMPORAL_FOLDED_COLUMN_X_SHIFT,
                position.y0,
                position.width,
                position.height,
            ],
            which="both",
        )


def _expand_success_temporal_folded_column_left(*folded_axes):
    """Widen both folded evidence panels equally toward their left side.

    Their shared right edge remains fixed while both left axes and their labels
    move 20 pixels left on the 1,300-pixel reference canvas. The subsequently
    created Decode Rate twin axes inherit the widened bounds.
    """
    left_expansion = (
        SUCCESS_TEMPORAL_FOLDED_COLUMN_LEFT_EXPANSION_PX
        / SUCCESS_TEMPORAL_REFERENCE_FIGURE_WIDTH_PX
    )
    for axis in folded_axes:
        position = axis.get_position()
        axis.set_position(
            [
                position.x0 - left_expansion,
                position.y0,
                position.width + left_expansion,
                position.height,
            ],
            which="both",
        )


def _place_success_temporal_evidence_column_header(
    figure,
    axis,
    text,
    *,
    gid,
):
    """Center one Compare-styled heading above both lower evidence rows."""
    position = axis.get_position()
    header = figure.text(
        (position.x0 + position.x1) / 2.0,
        position.y1 + 0.022,
        str(text),
        color="white",
        fontweight="bold",
        fontfamily=METRIC_FONT_FAMILY,
        fontsize=mpl.rcParams["axes.titlesize"],
        ha="center",
        va="bottom",
    )
    header.set_gid(gid)
    return header


def _configure_success_chronological_axis(axis, context, *, show_labels):
    """Apply shared real-UTC x limits, ticks, and the optional axis title."""
    edges = context["chronological_edges"]
    axis.set_xlim(edges[0], edges[-1])
    axis.xaxis.set_major_locator(
        mdates.AutoDateLocator(minticks=4, maxticks=8)
    )
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b\n%H:%M"))
    axis.tick_params(axis="x", labelbottom=bool(show_labels))
    if show_labels:
        _set_metric_axis_labels(
            axis,
            x_label=context["labels"]["time_x"],
        )


def _configure_success_folded_axis(axis, context, *, show_labels):
    """Apply shared folded-hour x limits, ticks, and the optional axis title."""
    axis.set_xlim(0.0, 24.0)
    axis.set_xticks(np.arange(0.5, 24.0, 3.0))
    axis.set_xticklabels([f"{hour:02d}" for hour in range(0, 24, 3)])
    axis.tick_params(axis="x", labelbottom=bool(show_labels))
    if show_labels:
        _set_metric_axis_labels(
            axis,
            x_label=context["labels"]["utc_hour_x"],
        )


@synchronized_matplotlib
def _render_opportunity_temporal_snr_figure(recipe):
    """Render the standalone Compare-sized successful-SNR temporal figure."""
    context = _success_temporal_render_context(recipe)
    labels = context["labels"]
    chronological = context["chronological"]
    folded = context["folded"]
    folding_available = context["folding_available"]
    figure = _create_success_temporal_figure(
        recipe,
        title_key="snr_title",
        figure_top=SEGMENT_TEMPORAL_FIGURE_TOP,
    )
    plot_grid = _success_temporal_plot_grid(
        figure,
        row_count=1,
        folding_available=folding_available,
        row_space=0.0,
    )
    chronological_axis = figure.add_subplot(plot_grid[0, 0])
    chronological_axis.set_gid("success-temporal-snr-chronological-axis")
    folded_axis = None
    if folding_available:
        folded_axis = figure.add_subplot(
            plot_grid[0, 1],
            sharey=chronological_axis,
        )
        folded_axis.set_gid("success-temporal-snr-folded-axis")
    for axis in (chronological_axis, folded_axis):
        if axis is not None:
            _style_evidence_axis(axis)

    chronological_mesh = _draw_success_snr_density_panel(
        chronological_axis,
        context["chronological_edges"],
        context["chronological_centers"],
        chronological,
        labels,
        labels["snr_chronological_title"],
        labels["snr_chronological_subtitle"].format(
            time_bin=context["display_time_bin"],
        ),
        labels["bin_median_chronological"],
        context["snr_representation"],
    )
    _configure_success_chronological_axis(
        chronological_axis,
        context,
        show_labels=True,
    )

    folded_mesh = None
    if folding_available:
        folded_mesh = _draw_success_snr_density_panel(
            folded_axis,
            context["folded_edges"],
            context["folded_centers"],
            folded,
            labels,
            labels["snr_utc_hour_title"],
            labels["snr_utc_hour_subtitle"],
            labels["bin_median_folded"],
            context["snr_representation"],
        )
        _configure_success_folded_axis(
            folded_axis,
            context,
            show_labels=True,
        )
        folded_axis.text(
            0.02,
            0.04,
            labels["utc_dates_folded"].format(
                count=context["utc_date_count"]
            ),
            transform=folded_axis.transAxes,
            color="#cccccc",
            fontsize=8,
            ha="left",
            va="bottom",
        )
    else:
        chronological_axis.text(
            0.98,
            0.05,
            labels["temporal_unavailable"],
            transform=chronological_axis.transAxes,
            color="#cccccc",
            fontsize=METRIC_TICK_LABEL_FONTSIZE,
            ha="right",
            va="bottom",
            bbox={
                "facecolor": "none",
                "edgecolor": "#444444",
                "alpha": 1.0,
                "pad": 4,
            },
        )

    colorbar_axes = [chronological_axis]
    if folded_axis is not None:
        colorbar_axes.append(folded_axis)
    colorbar = figure.colorbar(
        folded_mesh if folded_mesh is not None else chronological_mesh,
        ax=colorbar_axes,
        pad=SEGMENT_TEMPORAL_COLORBAR_PAD,
        fraction=SEGMENT_TEMPORAL_COLORBAR_FRACTION,
        ticks=np.linspace(
            EVIDENCE_DENSITY_MIN,
            EVIDENCE_DENSITY_MAX,
            5,
        ),
    )
    colorbar_axis = colorbar.ax
    colorbar_axis.set_gid("success-temporal-snr-colorbar-axis")
    colorbar.set_label(labels["snr_density"], color="white")
    colorbar.ax.tick_params(colors="white", labelsize=8)
    colorbar.outline.set_edgecolor("#444444")
    return figure


@synchronized_matplotlib
def _render_opportunity_temporal_evidence_figure(recipe):
    """Render station-vote and opportunity-count stacks below the SNR figure."""
    context = _success_temporal_render_context(recipe)
    labels = context["labels"]
    chronological = context["chronological"]
    folded = context["folded"]
    folding_available = context["folding_available"]
    common_rate_upper_limit = _success_temporal_rate_axis_max(
        chronological.get("station_balanced_rate_pct", []),
        chronological.get("observation_level_rate_pct", []),
        folded.get("station_balanced_rate_pct", []),
        folded.get("observation_level_rate_pct", []),
    )
    figure = _create_success_temporal_figure(
        recipe,
        title_key="evidence_title",
        figure_top=SUCCESS_TEMPORAL_EVIDENCE_FIGURE_TOP,
    )
    plot_grid = _success_temporal_plot_grid(
        figure,
        row_count=2,
        folding_available=folding_available,
        row_space=SUCCESS_TEMPORAL_EVIDENCE_ROW_SPACE,
    )
    chronological_station_axis = figure.add_subplot(plot_grid[0, 0])
    chronological_station_axis.set_gid(
        "success-temporal-station-chronological-axis"
    )
    chronological_opportunity_axis = figure.add_subplot(
        plot_grid[1, 0],
        sharex=chronological_station_axis,
    )
    chronological_opportunity_axis.set_gid(
        "success-temporal-opportunity-chronological-axis"
    )
    folded_station_axis = None
    folded_opportunity_axis = None
    if folding_available:
        folded_station_axis = figure.add_subplot(plot_grid[0, 1])
        folded_station_axis.set_gid(
            "success-temporal-station-folded-axis"
        )
        folded_opportunity_axis = figure.add_subplot(
            plot_grid[1, 1],
            sharex=folded_station_axis,
        )
        folded_opportunity_axis.set_gid(
            "success-temporal-opportunity-folded-axis"
        )
    for axis in (
        chronological_station_axis,
        chronological_opportunity_axis,
        folded_station_axis,
        folded_opportunity_axis,
    ):
        if axis is not None:
            _style_evidence_axis(axis)

    _reserve_success_temporal_colorbar_footprint(
        figure,
        tuple(
            axis
            for axis in (
                chronological_station_axis,
                chronological_opportunity_axis,
                folded_station_axis,
                folded_opportunity_axis,
            )
            if axis is not None
        ),
    )
    if folding_available:
        _translate_success_temporal_folded_column(
            folded_station_axis,
            folded_opportunity_axis,
        )
        _expand_success_temporal_folded_column_left(
            folded_station_axis,
            folded_opportunity_axis,
        )
    _place_success_temporal_evidence_column_header(
        figure,
        chronological_station_axis,
        labels["evidence_chronological_title"].format(
            time_bin=context["display_time_bin"],
        ),
        gid="success-temporal-evidence-chronological-column-header",
    )
    if folding_available:
        _place_success_temporal_evidence_column_header(
            figure,
            folded_station_axis,
            labels["evidence_utc_hour_title"],
            gid="success-temporal-evidence-folded-column-header",
        )
        _place_success_temporal_panel_subtitle(
            folded_station_axis,
            labels["station_support_folded_subtitle"],
            gid="success-temporal-station-folded-subtitle",
            y=1.0,
        )
        _place_success_temporal_panel_subtitle(
            folded_opportunity_axis,
            labels["opportunity_folded_subtitle"],
            gid="success-temporal-opportunity-folded-subtitle",
            y=1.0,
        )

    chronological_bar_widths = (
        np.diff(context["chronological_edges"]) * 0.78
    )
    _draw_success_outcome_stack(
        chronological_station_axis,
        context["chronological_centers"],
        chronological.get("station_success_votes", []),
        chronological.get("station_counter_votes", []),
        labels,
        bar_width=chronological_bar_widths,
        y_label=labels["station_vote_y"],
        gid_prefix="success-temporal-station-vote",
        integer_axis=False,
    )
    _draw_success_outcome_stack(
        chronological_opportunity_axis,
        context["chronological_centers"],
        chronological.get("opportunity_success_counts", []),
        chronological.get("opportunity_counter_counts", []),
        labels,
        bar_width=chronological_bar_widths,
        y_label=labels["opportunity_y"],
        gid_prefix="success-temporal-opportunity-count",
        integer_axis=True,
    )
    _draw_success_rate_overlay(
        chronological_station_axis,
        context["chronological_centers"],
        chronological.get("station_balanced_rate_pct", []),
        labels,
        upper_limit=common_rate_upper_limit,
        gid_suffix="station-balanced-chronological",
    )
    _draw_success_rate_overlay(
        chronological_opportunity_axis,
        context["chronological_centers"],
        chronological.get("observation_level_rate_pct", []),
        labels,
        upper_limit=common_rate_upper_limit,
        gid_suffix="observation-level-chronological",
    )
    _place_success_outcome_legend(figure, labels)
    _configure_success_chronological_axis(
        chronological_station_axis,
        context,
        show_labels=False,
    )
    _configure_success_chronological_axis(
        chronological_opportunity_axis,
        context,
        show_labels=True,
    )

    if folding_available:
        _draw_success_outcome_stack(
            folded_station_axis,
            context["folded_centers"],
            folded.get("station_success_support_per_utc_date", []),
            folded.get("station_counter_support_per_utc_date", []),
            labels,
            bar_width=0.78,
            y_label=labels["station_support_folded_y"],
            gid_prefix="success-temporal-station-support",
            integer_axis=False,
        )
        folded_station_axis.yaxis.labelpad = 1.0
        _draw_success_outcome_stack(
            folded_opportunity_axis,
            context["folded_centers"],
            folded.get("opportunity_success_counts_per_utc_date", []),
            folded.get("opportunity_counter_counts_per_utc_date", []),
            labels,
            bar_width=0.78,
            y_label=labels["opportunity_folded_y"],
            gid_prefix="success-temporal-opportunity-count",
            integer_axis=False,
        )
        folded_opportunity_axis.yaxis.labelpad = 1.0
        _draw_success_rate_overlay(
            folded_station_axis,
            context["folded_centers"],
            folded.get("station_balanced_rate_pct", []),
            labels,
            upper_limit=common_rate_upper_limit,
            gid_suffix="station-balanced-folded",
        )
        _draw_success_rate_overlay(
            folded_opportunity_axis,
            context["folded_centers"],
            folded.get("observation_level_rate_pct", []),
            labels,
            upper_limit=common_rate_upper_limit,
            gid_suffix="observation-level-folded",
        )
        _configure_success_folded_axis(
            folded_station_axis,
            context,
            show_labels=False,
        )
        _configure_success_folded_axis(
            folded_opportunity_axis,
            context,
            show_labels=True,
        )
        folded_station_axis.text(
            0.98,
            0.04,
            labels["utc_dates_folded"].format(
                count=context["utc_date_count"]
            ),
            transform=folded_station_axis.transAxes,
            color="#cccccc",
            fontsize=8,
            ha="right",
            va="bottom",
        )
    return figure
