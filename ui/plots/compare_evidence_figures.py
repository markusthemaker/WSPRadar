"""Pure preparation and rendering for Compare evidence coverage views."""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.dates as mdates

from config import (
    COLOR_JOINT,
    COLOR_ONLY_ME,
    COLOR_ONLY_REF,
)
from core.matplotlib_runtime import synchronized_matplotlib
from ui.inspector.evidence_data import (
    COMPARE_OUTCOME_JOINT,
    COMPARE_OUTCOME_REFERENCE_ONLY,
    COMPARE_OUTCOME_TARGET_ONLY,
    COMPARE_OUTCOMES,
)
from ui.plots.evidence_figures import (
    METRIC_FONT_FAMILY,
    METRIC_LEGEND_FONTSIZE,
    _format_temporal_time_bin_label,
    _place_metric_legend,
    _set_metric_axis_labels,
    _style_evidence_axis,
    _time_agg_minutes,
)
from ui.plots.opportunity_figures import (
    SUCCESS_TEMPORAL_EVIDENCE_FIGURE_TOP,
    SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
    SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    _as_utc_timestamp,
    _average_folded_counts_per_represented_date,
    _configure_success_chronological_axis,
    _configure_success_folded_axis,
    _create_success_temporal_figure,
    _format_ham_compact_count,
    _place_success_temporal_evidence_column_header,
    _represented_utc_date_hour_counts,
    _success_temporal_rate_axis_max,
)
from ui.plots.temporal_layout import (
    TEMPORAL_EVIDENCE_ROW_SPACE,
    align_folded_evidence_axes_to_colorbar,
    build_temporal_plot_grid,
    draw_folded_utc_unavailable_annotation,
)


COMPARE_COVERAGE_RECIPE_SCHEMA_VERSION = 2
COMPARE_TEMPORAL_COVERAGE_RECIPE_KIND = (
    "compare_temporal_evidence_coverage"
)
COMPARE_SELECTED_PATH_COVERAGE_RECIPE_KIND = (
    "selected_path_evidence_coverage"
)
COMPARE_STATION_JOINT_SHARE_COLOR = "#36aaf9"
COMPARE_OUTCOME_JOINT_SHARE_COLOR = "#ffbe33"
COMPARE_OUTCOME_COLORS = (
    COLOR_JOINT,
    COLOR_ONLY_ME,
    COLOR_ONLY_REF,
)
COMPARE_COVERAGE_FIGURE_BOTTOM = 0.22
COMPARE_SELECTED_COVERAGE_FIGURE_BOTTOM = 0.25
COMPARE_COVERAGE_NOTE_FOOTER_Y = 0.04
COMPARE_COVERAGE_VERSION_FOOTER_Y = 0.012


def _required_compare_labels(figure_labels, required_keys):
    """Return string-only localized labels and reject incomplete recipes."""
    labels = dict(figure_labels or {})
    missing = sorted(key for key in required_keys if key not in labels)
    if missing:
        raise ValueError(
            "Compare temporal figure labels are missing: "
            + ", ".join(missing)
        )
    return {key: str(labels[key]) for key in required_keys}


def _prepare_compare_coverage_units(
    comparison_units,
    *,
    analysis_start_t,
    analysis_end_t,
):
    """Validate and clip retained outcome units to one half-open UTC run."""
    required_columns = {
        "peer_sign",
        "peer_grid",
        "evidence_utc",
        "outcome",
    }
    if comparison_units is None:
        comparison_units = pd.DataFrame()
    missing_columns = sorted(
        required_columns.difference(comparison_units.columns)
    )
    if missing_columns:
        raise ValueError(
            "Compare temporal units are missing columns: "
            + ", ".join(missing_columns)
        )
    start = _as_utc_timestamp(analysis_start_t)
    end = _as_utc_timestamp(analysis_end_t)
    if pd.isna(start) or pd.isna(end) or end <= start:
        raise ValueError(
            "Compare temporal evidence requires a positive UTC window."
        )

    work = comparison_units[
        [
            "peer_sign",
            "peer_grid",
            "evidence_utc",
            "outcome",
        ]
    ].copy()
    work["peer_sign"] = work["peer_sign"].astype(str)
    work["peer_grid"] = work["peer_grid"].astype(str)
    work["evidence_utc"] = pd.to_datetime(
        work["evidence_utc"],
        errors="coerce",
        utc=True,
    )
    work = work[
        work["outcome"].isin(COMPARE_OUTCOMES)
        & work["evidence_utc"].notna()
        & work["evidence_utc"].ge(start)
        & work["evidence_utc"].lt(end)
    ].copy()
    return work, start, end


def _compare_outcome_indicators(work):
    """Attach integer Only Target, Joint and Only Reference indicators."""
    categorized = work.copy()
    categorized["target_only_count"] = categorized["outcome"].eq(
        COMPARE_OUTCOME_TARGET_ONLY
    ).astype("int64")
    categorized["joint_count"] = categorized["outcome"].eq(
        COMPARE_OUTCOME_JOINT
    ).astype("int64")
    categorized["reference_only_count"] = categorized["outcome"].eq(
        COMPARE_OUTCOME_REFERENCE_ONLY
    ).astype("int64")
    return categorized


def _compare_chronological_axis(start, end, time_bin):
    """Return exact Performance-style chronological edges and centers."""
    bin_delta = pd.Timedelta(minutes=_time_agg_minutes(time_bin))
    bin_count = max(1, int(np.ceil((end - start) / bin_delta)))
    bin_starts = pd.DatetimeIndex(
        [start + (index * bin_delta) for index in range(bin_count)]
    )
    bin_edges = pd.DatetimeIndex(list(bin_starts) + [end])
    bin_centers = pd.DatetimeIndex(
        [
            lower + ((upper - lower) / 2)
            for lower, upper in zip(bin_edges[:-1], bin_edges[1:])
        ]
    )
    return bin_delta, bin_count, bin_edges, bin_centers


def _aggregate_compare_chronological_coverage(work, start, end, time_bin):
    """Aggregate station-split votes and raw comparison units by run-time bin."""
    (
        bin_delta,
        bin_count,
        bin_edges,
        bin_centers,
    ) = _compare_chronological_axis(start, end, time_bin)
    station_joint_share = np.full(bin_count, np.nan, dtype=float)
    outcome_joint_share = np.full(bin_count, np.nan, dtype=float)
    station_target_votes = np.zeros(bin_count, dtype=float)
    station_joint_votes = np.zeros(bin_count, dtype=float)
    station_reference_votes = np.zeros(bin_count, dtype=float)
    unit_target_counts = np.zeros(bin_count, dtype=np.int64)
    unit_joint_counts = np.zeros(bin_count, dtype=np.int64)
    unit_reference_counts = np.zeros(bin_count, dtype=np.int64)
    station_counts = np.zeros(bin_count, dtype=np.int64)

    if not work.empty:
        binned = _compare_outcome_indicators(work)
        binned["bin_index"] = (
            (binned["evidence_utc"] - start) // bin_delta
        ).astype("int64")
        station_bins = (
            binned.groupby(
                ["bin_index", "peer_sign", "peer_grid"],
                dropna=False,
                observed=True,
            )
            .agg(
                target_only=("target_only_count", "sum"),
                joint=("joint_count", "sum"),
                reference_only=("reference_only_count", "sum"),
            )
            .reset_index()
        )
        station_bins["total"] = (
            station_bins["target_only"]
            + station_bins["joint"]
            + station_bins["reference_only"]
        )
        station_bins = station_bins[station_bins["total"] > 0].copy()
        station_bins["target_vote"] = (
            station_bins["target_only"] / station_bins["total"]
        )
        station_bins["joint_vote"] = (
            station_bins["joint"] / station_bins["total"]
        )
        station_bins["reference_vote"] = (
            station_bins["reference_only"] / station_bins["total"]
        )
        bins = (
            station_bins.groupby("bin_index", observed=True)
            .agg(
                station_target_votes=("target_vote", "sum"),
                station_joint_votes=("joint_vote", "sum"),
                station_reference_votes=("reference_vote", "sum"),
                station_joint_share_pct=("joint_vote", "mean"),
                target_only=("target_only", "sum"),
                joint=("joint", "sum"),
                reference_only=("reference_only", "sum"),
                station_count=("peer_sign", "size"),
            )
            .reset_index()
        )
        bins["station_joint_share_pct"] *= 100.0
        bins["outcome_joint_share_pct"] = np.where(
            (
                bins["target_only"]
                + bins["joint"]
                + bins["reference_only"]
            )
            > 0,
            100.0
            * bins["joint"]
            / (
                bins["target_only"]
                + bins["joint"]
                + bins["reference_only"]
            ),
            np.nan,
        )
        indexes = bins["bin_index"].to_numpy(dtype=np.int64, copy=False)
        valid = (indexes >= 0) & (indexes < bin_count)
        indexes = indexes[valid]
        station_joint_share[indexes] = bins.loc[
            valid,
            "station_joint_share_pct",
        ].to_numpy(dtype=float, copy=False)
        outcome_joint_share[indexes] = bins.loc[
            valid,
            "outcome_joint_share_pct",
        ].to_numpy(dtype=float, copy=False)
        station_target_votes[indexes] = bins.loc[
            valid,
            "station_target_votes",
        ].to_numpy(dtype=float, copy=False)
        station_joint_votes[indexes] = bins.loc[
            valid,
            "station_joint_votes",
        ].to_numpy(dtype=float, copy=False)
        station_reference_votes[indexes] = bins.loc[
            valid,
            "station_reference_votes",
        ].to_numpy(dtype=float, copy=False)
        unit_target_counts[indexes] = bins.loc[
            valid,
            "target_only",
        ].to_numpy(dtype=np.int64, copy=False)
        unit_joint_counts[indexes] = bins.loc[
            valid,
            "joint",
        ].to_numpy(dtype=np.int64, copy=False)
        unit_reference_counts[indexes] = bins.loc[
            valid,
            "reference_only",
        ].to_numpy(dtype=np.int64, copy=False)
        station_counts[indexes] = bins.loc[
            valid,
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
        "station_joint_share_pct": station_joint_share,
        "outcome_joint_share_pct": outcome_joint_share,
        "station_target_votes": station_target_votes,
        "station_joint_votes": station_joint_votes,
        "station_reference_votes": station_reference_votes,
        "unit_target_counts": unit_target_counts,
        "unit_joint_counts": unit_joint_counts,
        "unit_reference_counts": unit_reference_counts,
        "station_counts": station_counts,
    }


def _partition_compare_folded_station_support(
    average_support,
    target_share_pct,
    joint_share_pct,
    reference_share_pct,
):
    """Partition true mean station presence by pooled equal-station shares."""
    support = np.asarray(average_support, dtype=float)
    shares = [
        np.asarray(target_share_pct, dtype=float),
        np.asarray(joint_share_pct, dtype=float),
        np.asarray(reference_share_pct, dtype=float),
    ]
    if any(share.shape != support.shape for share in shares):
        raise ValueError(
            "Folded Compare station support and share arrays must align."
        )
    has_support = support > 0.0
    share_sum = shares[0] + shares[1] + shares[2]
    invalid = has_support & (
        ~np.isfinite(share_sum)
        | ~np.isclose(share_sum, 100.0, atol=1e-8)
        | np.logical_or.reduce(
            tuple((share < 0.0) | (share > 100.0) for share in shares)
        )
    )
    if invalid.any():
        raise ValueError(
            "Positive folded Compare station support requires three finite "
            "shares that sum to 100%."
        )
    partitions = []
    for share in shares:
        partition = np.zeros_like(support, dtype=float)
        partition[has_support] = (
            support[has_support] * share[has_support] / 100.0
        )
        partitions.append(partition)
    return tuple(partitions)


def _aggregate_compare_folded_coverage(work, start, end):
    """Fold Compare coverage with Performance represented-date normalization."""
    station_joint_share = np.full(24, np.nan, dtype=float)
    outcome_joint_share = np.full(24, np.nan, dtype=float)
    station_target_votes = np.zeros(24, dtype=float)
    station_joint_votes = np.zeros(24, dtype=float)
    station_reference_votes = np.zeros(24, dtype=float)
    unit_target_counts = np.zeros(24, dtype=np.int64)
    unit_joint_counts = np.zeros(24, dtype=np.int64)
    unit_reference_counts = np.zeros(24, dtype=np.int64)
    station_counts = np.zeros(24, dtype=np.int64)
    station_date_hour_presence_counts = np.zeros(24, dtype=np.int64)
    station_target_share = np.full(24, np.nan, dtype=float)
    station_reference_share = np.full(24, np.nan, dtype=float)

    if not work.empty:
        folded = _compare_outcome_indicators(work)
        folded["utc_hour"] = folded["evidence_utc"].dt.hour.astype("int8")
        folded["utc_date"] = folded["evidence_utc"].dt.normalize()
        station_hours = (
            folded.groupby(
                ["utc_hour", "peer_sign", "peer_grid"],
                dropna=False,
                observed=True,
            )
            .agg(
                target_only=("target_only_count", "sum"),
                joint=("joint_count", "sum"),
                reference_only=("reference_only_count", "sum"),
            )
            .reset_index()
        )
        station_hours["total"] = (
            station_hours["target_only"]
            + station_hours["joint"]
            + station_hours["reference_only"]
        )
        station_hours = station_hours[station_hours["total"] > 0].copy()
        station_hours["target_vote"] = (
            station_hours["target_only"] / station_hours["total"]
        )
        station_hours["joint_vote"] = (
            station_hours["joint"] / station_hours["total"]
        )
        station_hours["reference_vote"] = (
            station_hours["reference_only"] / station_hours["total"]
        )
        hours = (
            station_hours.groupby("utc_hour", observed=True)
            .agg(
                station_target_votes=("target_vote", "sum"),
                station_joint_votes=("joint_vote", "sum"),
                station_reference_votes=("reference_vote", "sum"),
                station_target_share_pct=("target_vote", "mean"),
                station_joint_share_pct=("joint_vote", "mean"),
                station_reference_share_pct=("reference_vote", "mean"),
                target_only=("target_only", "sum"),
                joint=("joint", "sum"),
                reference_only=("reference_only", "sum"),
                station_count=("peer_sign", "size"),
            )
            .reset_index()
        )
        for column in (
            "station_target_share_pct",
            "station_joint_share_pct",
            "station_reference_share_pct",
        ):
            hours[column] *= 100.0
        hours["outcome_joint_share_pct"] = np.where(
            (
                hours["target_only"]
                + hours["joint"]
                + hours["reference_only"]
            )
            > 0,
            100.0
            * hours["joint"]
            / (
                hours["target_only"]
                + hours["joint"]
                + hours["reference_only"]
            ),
            np.nan,
        )
        indexes = hours["utc_hour"].to_numpy(dtype=np.int64, copy=False)
        station_target_share[indexes] = hours[
            "station_target_share_pct"
        ].to_numpy(dtype=float, copy=False)
        station_joint_share[indexes] = hours[
            "station_joint_share_pct"
        ].to_numpy(dtype=float, copy=False)
        station_reference_share[indexes] = hours[
            "station_reference_share_pct"
        ].to_numpy(dtype=float, copy=False)
        outcome_joint_share[indexes] = hours[
            "outcome_joint_share_pct"
        ].to_numpy(dtype=float, copy=False)
        station_target_votes[indexes] = hours[
            "station_target_votes"
        ].to_numpy(dtype=float, copy=False)
        station_joint_votes[indexes] = hours[
            "station_joint_votes"
        ].to_numpy(dtype=float, copy=False)
        station_reference_votes[indexes] = hours[
            "station_reference_votes"
        ].to_numpy(dtype=float, copy=False)
        unit_target_counts[indexes] = hours["target_only"].to_numpy(
            dtype=np.int64,
            copy=False,
        )
        unit_joint_counts[indexes] = hours["joint"].to_numpy(
            dtype=np.int64,
            copy=False,
        )
        unit_reference_counts[indexes] = hours[
            "reference_only"
        ].to_numpy(dtype=np.int64, copy=False)
        station_counts[indexes] = hours["station_count"].to_numpy(
            dtype=np.int64,
            copy=False,
        )
        station_date_hours = (
            folded.groupby(
                ["utc_hour", "utc_date", "peer_sign", "peer_grid"],
                dropna=False,
                observed=True,
            )
            .size()
            .groupby(level="utc_hour")
            .size()
        )
        station_date_hour_presence_counts[
            station_date_hours.index.to_numpy(dtype=np.int64, copy=False)
        ] = station_date_hours.to_numpy(dtype=np.int64, copy=False)

    represented_date_counts = _represented_utc_date_hour_counts(
        work,
        start,
        end,
    )
    station_average_support = _average_folded_counts_per_represented_date(
        station_date_hour_presence_counts,
        represented_date_counts,
    )
    (
        station_target_support,
        station_joint_support,
        station_reference_support,
    ) = _partition_compare_folded_station_support(
        station_average_support,
        station_target_share,
        station_joint_share,
        station_reference_share,
    )
    return {
        "utc_hours": np.arange(24, dtype=np.int64),
        "station_joint_share_pct": station_joint_share,
        "outcome_joint_share_pct": outcome_joint_share,
        "station_target_votes": station_target_votes,
        "station_joint_votes": station_joint_votes,
        "station_reference_votes": station_reference_votes,
        "station_target_support_per_utc_date": station_target_support,
        "station_joint_support_per_utc_date": station_joint_support,
        "station_reference_support_per_utc_date": station_reference_support,
        "station_average_support_per_utc_date": station_average_support,
        "station_date_hour_presence_counts": (
            station_date_hour_presence_counts
        ),
        "unit_target_counts": unit_target_counts,
        "unit_joint_counts": unit_joint_counts,
        "unit_reference_counts": unit_reference_counts,
        "unit_target_counts_per_utc_date": (
            _average_folded_counts_per_represented_date(
                unit_target_counts,
                represented_date_counts,
            )
        ),
        "unit_joint_counts_per_utc_date": (
            _average_folded_counts_per_represented_date(
                unit_joint_counts,
                represented_date_counts,
            )
        ),
        "unit_reference_counts_per_utc_date": (
            _average_folded_counts_per_represented_date(
                unit_reference_counts,
                represented_date_counts,
            )
        ),
        "station_counts": station_counts,
        "represented_utc_date_counts": represented_date_counts,
    }


def _compare_coverage_recipe(
    comparison_units,
    *,
    coverage_title,
    selected_segment,
    analysis_start_t,
    analysis_end_t,
    time_bin_options,
    time_bin_default,
    figure_labels,
    population_mode=SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
):
    """Build coverage-only recipes from canonical retained Compare units.

    Each chronological bin preserves one split vote per contributing station
    plus every retained comparison unit. Folded profiles preserve represented
    UTC-date normalization and zero-support hours.
    """
    required_label_keys = (
        "utc_dates_folded",
        "folded_unavailable",
        "time_x",
        "utc_hour_x",
        "evidence_chronological_title",
        "evidence_utc_hour_title",
        "station_vote_y",
        "station_folded_y",
        "unit_y",
        "unit_folded_y",
        "joint_share_y",
        "station_joint_share",
        "outcome_joint_share",
        "target_only",
        "joint",
        "reference_only",
        "gate_note",
        "selected_chronological_title",
        "selected_utc_hour_title",
        "selected_title_unit",
        "selected_unit_y",
        "selected_unit_folded_y",
        "selected_joint_share",
    )
    labels = _required_compare_labels(
        figure_labels,
        required_label_keys,
    )
    work, start, end = _prepare_compare_coverage_units(
        comparison_units,
        analysis_start_t=analysis_start_t,
        analysis_end_t=analysis_end_t,
    )
    time_bin_options = [str(value) for value in time_bin_options]
    if not time_bin_options:
        raise ValueError("Compare temporal evidence requires time-bin options.")
    time_bin_default = str(time_bin_default)
    if time_bin_default not in time_bin_options:
        raise ValueError(
            "Compare temporal default must be one of its time-bin options."
        )
    if population_mode not in {
        SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
        SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    }:
        raise ValueError(
            f"Unsupported Compare temporal population mode: {population_mode}"
        )
    if (
        population_mode == SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
        and len(work[["peer_sign", "peer_grid"]].drop_duplicates()) > 1
    ):
        raise ValueError(
            "Selected-path Compare coverage requires exactly one identity."
        )

    profiles = {
        time_bin: _aggregate_compare_chronological_coverage(
            work,
            start,
            end,
            time_bin,
        )
        for time_bin in time_bin_options
    }
    folded_profile = _aggregate_compare_folded_coverage(work, start, end)
    utc_date_count = int(work["evidence_utc"].dt.normalize().nunique())
    kind = (
        COMPARE_SELECTED_PATH_COVERAGE_RECIPE_KIND
        if population_mode == SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
        else COMPARE_TEMPORAL_COVERAGE_RECIPE_KIND
    )
    return {
        "kind": kind,
        "schema_version": COMPARE_COVERAGE_RECIPE_SCHEMA_VERSION,
        "population_mode": population_mode,
        "title": str(coverage_title),
        "evidence_title": str(coverage_title),
        "selected_segment": str(selected_segment),
        "labels": labels,
        "time_bin_options": list(time_bin_options),
        "time_bin_default": time_bin_default,
        "time_bin": time_bin_default,
        "chronological_profiles": profiles,
        "folded_profile": folded_profile,
        "utc_date_count": utc_date_count,
        "comparison_unit_count": int(len(work)),
        "paired_comparison_unit_count": int(
            work["outcome"].eq(COMPARE_OUTCOME_JOINT).sum()
        ),
        "folded_unit_normalization": (
            "sum-units-per-represented-utc-date-v1"
        ),
        "folded_station_support_policy": (
            "station-date-hour-presence-per-represented-utc-date-"
            "partitioned-by-pooled-station-composition-v1"
        ),
        "station_vote_policy": (
            "one-vote-per-station-split-by-outcome-composition-v1"
        ),
    }


def _compare_coverage_render_context(recipe):
    """Validate one coverage recipe and resolve its selected plot profiles."""
    if int(recipe.get("schema_version", 0)) != (
        COMPARE_COVERAGE_RECIPE_SCHEMA_VERSION
    ):
        raise ValueError("Unsupported Compare coverage recipe schema.")
    population_mode = str(
        recipe.get(
            "population_mode",
            SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
        )
    )
    if population_mode not in {
        SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
        SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    }:
        raise ValueError(
            f"Unsupported Compare coverage population mode: {population_mode}"
        )
    selected_time_bin = str(recipe.get("time_bin", "1h"))
    profiles = recipe.get("chronological_profiles") or {}
    if selected_time_bin not in profiles:
        raise ValueError(
            f"Unsupported Compare coverage time bin: {selected_time_bin}"
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
    if len(chronological_edge_numbers) != (
        len(chronological_center_numbers) + 1
    ):
        raise ValueError(
            "Compare coverage chronological edges must bound every time bin."
        )
    utc_date_count = int(recipe.get("utc_date_count", 0))
    return {
        "labels": dict(recipe.get("labels") or {}),
        "population_mode": population_mode,
        "selected_time_bin": selected_time_bin,
        "display_time_bin": _format_temporal_time_bin_label(selected_time_bin),
        "chronological": chronological,
        "folded": dict(recipe.get("folded_profile") or {}),
        "utc_date_count": utc_date_count,
        "folded_data_available": utc_date_count >= 2,
        "chronological_centers": chronological_center_numbers,
        "chronological_edges": chronological_edge_numbers,
        "folded_edges": np.arange(25, dtype=float),
        "folded_centers": np.arange(24, dtype=float) + 0.5,
    }


def _draw_compare_outcome_stack(
    axis,
    x_values,
    target_values,
    joint_values,
    reference_values,
    labels,
    *,
    bar_width,
    y_label,
    gid_prefix,
    integer_axis,
):
    """Draw Joint, Only Target, then Only Reference from the baseline upward."""
    x = np.asarray(x_values, dtype=float)
    value_arrays = [
        np.asarray(joint_values, dtype=float),
        np.asarray(target_values, dtype=float),
        np.asarray(reference_values, dtype=float),
    ]
    if any(len(values) != len(x) for values in value_arrays):
        raise ValueError(
            "Compare temporal outcome arrays must match their time axis."
        )
    bottoms = np.zeros(len(x), dtype=float)
    artists = []
    category_specs = zip(
        ("joint", "target-only", "reference-only"),
        value_arrays,
        COMPARE_OUTCOME_COLORS,
        (
            labels["joint"],
            labels["target_only"],
            labels["reference_only"],
        ),
    )
    for category, values, color, label in category_specs:
        bars = axis.bar(
            x,
            values,
            width=bar_width,
            bottom=bottoms,
            color=color,
            edgecolor="#111111",
            linewidth=0.35,
            label=label,
            zorder=2,
        )
        for bar in bars:
            bar.set_gid(f"{gid_prefix}-{category}")
        artists.append(bars)
        bottoms = bottoms + values
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
    return tuple(artists)


def _draw_compare_joint_share_overlay(
    count_axis,
    x_values,
    share_values,
    labels,
    *,
    upper_limit,
    line_color,
    line_label,
    gid_suffix,
):
    """Draw one denominator-matched Joint Evidence Share line."""
    x = np.asarray(x_values, dtype=float)
    shares = np.asarray(share_values, dtype=float)
    if len(shares) != len(x):
        raise ValueError(
            "Compare Joint Evidence Share must match its time axis."
        )
    share_axis = count_axis.twinx()
    share_axis.set_position(count_axis.get_position(), which="both")
    share_axis.set_gid(f"compare-temporal-{gid_suffix}-share-axis")
    share_axis.patch.set_visible(False)
    share_axis.tick_params(axis="y", colors=line_color, labelsize=8)
    share_axis.spines["right"].set_color("#5f7177")
    share_axis.spines["top"].set_color("#444444")
    share_axis.spines["left"].set_visible(False)
    share_axis.set_ylim(0.0, float(upper_limit))
    share_axis.yaxis.set_major_locator(
        mpl.ticker.MaxNLocator(nbins=5, min_n_ticks=3)
    )
    _set_metric_axis_labels(
        share_axis,
        y_label=labels["joint_share_y"],
        y_color=line_color,
    )
    share_axis.yaxis.labelpad = 1.0
    line = share_axis.plot(
        x,
        shares,
        color=line_color,
        marker="o",
        markersize=3.0,
        linewidth=1.2,
        label=line_label,
        zorder=5,
    )[0]
    line.set_gid(f"compare-temporal-{gid_suffix}-share")
    return share_axis, line


def _place_compare_coverage_legend(figure, labels, *, selected_path):
    """Place the shared category/share legend below the coverage title."""
    handles = [
        mpl.patches.Patch(
            facecolor=color,
            edgecolor="#111111",
            label=label,
        )
        for color, label in zip(
            COMPARE_OUTCOME_COLORS,
            (
                labels["joint"],
                labels["target_only"],
                labels["reference_only"],
            ),
        )
    ]
    if selected_path:
        handles.append(
            mpl.lines.Line2D(
                [],
                [],
                color=COMPARE_OUTCOME_JOINT_SHARE_COLOR,
                marker="o",
                markersize=3.0,
                linewidth=1.2,
                label=labels["selected_joint_share"],
            )
        )
    else:
        handles.extend(
            [
                mpl.lines.Line2D(
                    [],
                    [],
                    color=COMPARE_STATION_JOINT_SHARE_COLOR,
                    marker="o",
                    markersize=3.0,
                    linewidth=1.2,
                    label=labels["station_joint_share"],
                ),
                mpl.lines.Line2D(
                    [],
                    [],
                    color=COMPARE_OUTCOME_JOINT_SHARE_COLOR,
                    marker="o",
                    markersize=3.0,
                    linewidth=1.2,
                    label=labels["outcome_joint_share"],
                ),
            ]
        )
    _place_metric_legend(
        figure,
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.895),
        borderaxespad=0.0,
        ncol=len(handles),
        columnspacing=1.05,
        handletextpad=0.45,
        gid="compare-temporal-coverage-legend",
    )


def _annotate_compare_coverage_note(figure, note):
    """Place the mode-specific denominator/gate note in the figure footer."""
    annotation = figure.text(
        0.5,
        COMPARE_COVERAGE_NOTE_FOOTER_Y,
        str(note),
        color="#cfcfcf",
        fontsize=METRIC_LEGEND_FONTSIZE,
        fontfamily=METRIC_FONT_FAMILY,
        ha="center",
        va="bottom",
        multialignment="center",
        linespacing=1.15,
    )
    annotation.set_gid("compare-temporal-coverage-gate-note")
    return annotation


@synchronized_matplotlib
def render_compare_temporal_coverage_export_figure(recipe):
    """Render the two-row station/unit Compare coverage view."""
    if (
        not recipe
        or recipe.get("kind") != COMPARE_TEMPORAL_COVERAGE_RECIPE_KIND
    ):
        return None
    context = _compare_coverage_render_context(recipe)
    labels = context["labels"]
    chronological = context["chronological"]
    folded = context["folded"]
    folded_data_available = context["folded_data_available"]
    share_series = [
        chronological.get("station_joint_share_pct", []),
        chronological.get("outcome_joint_share_pct", []),
    ]
    if folded_data_available:
        share_series.extend(
            [
                folded.get("station_joint_share_pct", []),
                folded.get("outcome_joint_share_pct", []),
            ]
        )
    common_share_limit = _success_temporal_rate_axis_max(*share_series)
    figure = _create_success_temporal_figure(
        recipe,
        title_key="evidence_title",
        figure_top=SUCCESS_TEMPORAL_EVIDENCE_FIGURE_TOP,
        figure_bottom=COMPARE_COVERAGE_FIGURE_BOTTOM,
        footer_y=COMPARE_COVERAGE_VERSION_FOOTER_Y,
    )
    plot_grid = build_temporal_plot_grid(
        figure,
        row_count=2,
        row_space=TEMPORAL_EVIDENCE_ROW_SPACE,
    )
    chronological_station_axis = figure.add_subplot(plot_grid[0, 0])
    chronological_station_axis.set_gid(
        "compare-temporal-station-chronological-axis"
    )
    chronological_unit_axis = figure.add_subplot(
        plot_grid[1, 0],
        sharex=chronological_station_axis,
    )
    chronological_unit_axis.set_gid(
        "compare-temporal-unit-chronological-axis"
    )
    folded_station_axis = figure.add_subplot(plot_grid[0, 1])
    folded_station_axis.set_gid(
        "compare-temporal-station-folded-axis"
    )
    folded_unit_axis = figure.add_subplot(
        plot_grid[1, 1],
        sharex=folded_station_axis,
    )
    folded_unit_axis.set_gid("compare-temporal-unit-folded-axis")
    axes = (
        chronological_station_axis,
        chronological_unit_axis,
        folded_station_axis,
        folded_unit_axis,
    )
    for axis in axes:
        _style_evidence_axis(axis)
    align_folded_evidence_axes_to_colorbar(
        figure,
        all_axes=axes,
        folded_axes=(
            folded_station_axis,
            folded_unit_axis,
        ),
    )
    _place_success_temporal_evidence_column_header(
        figure,
        chronological_station_axis,
        labels["evidence_chronological_title"].format(
            time_bin=context["display_time_bin"],
        ),
        gid="compare-temporal-coverage-chronological-column-header",
    )
    _place_success_temporal_evidence_column_header(
        figure,
        folded_station_axis,
        labels["evidence_utc_hour_title"],
        gid="compare-temporal-coverage-folded-column-header",
    )

    bar_widths = np.diff(context["chronological_edges"]) * 0.78
    _draw_compare_outcome_stack(
        chronological_station_axis,
        context["chronological_centers"],
        chronological.get("station_target_votes", []),
        chronological.get("station_joint_votes", []),
        chronological.get("station_reference_votes", []),
        labels,
        bar_width=bar_widths,
        y_label=labels["station_vote_y"],
        gid_prefix="compare-temporal-station-vote",
        integer_axis=False,
    )
    _draw_compare_outcome_stack(
        chronological_unit_axis,
        context["chronological_centers"],
        chronological.get("unit_target_counts", []),
        chronological.get("unit_joint_counts", []),
        chronological.get("unit_reference_counts", []),
        labels,
        bar_width=bar_widths,
        y_label=labels["unit_y"],
        gid_prefix="compare-temporal-unit-count",
        integer_axis=True,
    )
    _draw_compare_joint_share_overlay(
        chronological_station_axis,
        context["chronological_centers"],
        chronological.get("station_joint_share_pct", []),
        labels,
        upper_limit=common_share_limit,
        line_color=COMPARE_STATION_JOINT_SHARE_COLOR,
        line_label=labels["station_joint_share"],
        gid_suffix="station-balanced-chronological",
    )
    _draw_compare_joint_share_overlay(
        chronological_unit_axis,
        context["chronological_centers"],
        chronological.get("outcome_joint_share_pct", []),
        labels,
        upper_limit=common_share_limit,
        line_color=COMPARE_OUTCOME_JOINT_SHARE_COLOR,
        line_label=labels["outcome_joint_share"],
        gid_suffix="outcome-level-chronological",
    )
    _configure_success_chronological_axis(
        chronological_station_axis,
        context,
        show_labels=False,
    )
    _configure_success_chronological_axis(
        chronological_unit_axis,
        context,
        show_labels=True,
    )

    if folded_data_available:
        _draw_compare_outcome_stack(
            folded_station_axis,
            context["folded_centers"],
            folded.get("station_target_support_per_utc_date", []),
            folded.get("station_joint_support_per_utc_date", []),
            folded.get("station_reference_support_per_utc_date", []),
            labels,
            bar_width=0.78,
            y_label=labels["station_folded_y"],
            gid_prefix="compare-temporal-station-support",
            integer_axis=False,
        )
        folded_station_axis.yaxis.labelpad = 0.0
        _draw_compare_outcome_stack(
            folded_unit_axis,
            context["folded_centers"],
            folded.get("unit_target_counts_per_utc_date", []),
            folded.get("unit_joint_counts_per_utc_date", []),
            folded.get("unit_reference_counts_per_utc_date", []),
            labels,
            bar_width=0.78,
            y_label=labels["unit_folded_y"],
            gid_prefix="compare-temporal-unit-count",
            integer_axis=False,
        )
        folded_unit_axis.yaxis.labelpad = 0.0
        _draw_compare_joint_share_overlay(
            folded_station_axis,
            context["folded_centers"],
            folded.get("station_joint_share_pct", []),
            labels,
            upper_limit=common_share_limit,
            line_color=COMPARE_STATION_JOINT_SHARE_COLOR,
            line_label=labels["station_joint_share"],
            gid_suffix="station-balanced-folded",
        )
        _draw_compare_joint_share_overlay(
            folded_unit_axis,
            context["folded_centers"],
            folded.get("outcome_joint_share_pct", []),
            labels,
            upper_limit=common_share_limit,
            line_color=COMPARE_OUTCOME_JOINT_SHARE_COLOR,
            line_label=labels["outcome_joint_share"],
            gid_suffix="outcome-level-folded",
        )
        _configure_success_folded_axis(
            folded_station_axis,
            context,
            show_labels=False,
        )
        _configure_success_folded_axis(
            folded_unit_axis,
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
    else:
        for axis, y_label, show_labels in (
            (folded_station_axis, labels["station_folded_y"], False),
            (folded_unit_axis, labels["unit_folded_y"], True),
        ):
            _set_metric_axis_labels(axis, y_label=y_label)
            axis.yaxis.labelpad = 0.0
            axis.set_ylim(0.0, 1.0)
            axis.set_yticks([])
            _configure_success_folded_axis(
                axis,
                context,
                show_labels=show_labels,
            )
            draw_folded_utc_unavailable_annotation(
                axis,
                labels["folded_unavailable"],
            )
    _place_compare_coverage_legend(
        figure,
        labels,
        selected_path=False,
    )
    _annotate_compare_coverage_note(figure, labels["gate_note"])
    return figure


@synchronized_matplotlib
def render_selected_compare_coverage_export_figure(recipe):
    """Render one chronological/folded comparison-unit row for one path."""
    if (
        not recipe
        or recipe.get("kind")
        != COMPARE_SELECTED_PATH_COVERAGE_RECIPE_KIND
    ):
        return None
    context = _compare_coverage_render_context(recipe)
    labels = context["labels"]
    chronological = context["chronological"]
    folded = context["folded"]
    folded_data_available = context["folded_data_available"]
    share_series = [chronological.get("outcome_joint_share_pct", [])]
    if folded_data_available:
        share_series.append(folded.get("outcome_joint_share_pct", []))
    common_share_limit = _success_temporal_rate_axis_max(*share_series)
    figure = _create_success_temporal_figure(
        recipe,
        title_key="evidence_title",
        figure_top=SUCCESS_TEMPORAL_EVIDENCE_FIGURE_TOP,
        figure_bottom=COMPARE_SELECTED_COVERAGE_FIGURE_BOTTOM,
        footer_y=COMPARE_COVERAGE_VERSION_FOOTER_Y,
    )
    plot_grid = build_temporal_plot_grid(
        figure,
        row_count=1,
        row_space=0.0,
    )
    chronological_axis = figure.add_subplot(plot_grid[0, 0])
    chronological_axis.set_gid(
        "selected-compare-coverage-chronological-axis"
    )
    folded_axis = figure.add_subplot(plot_grid[0, 1])
    folded_axis.set_gid("selected-compare-coverage-folded-axis")
    axes = (chronological_axis, folded_axis)
    for axis in axes:
        _style_evidence_axis(axis)
    align_folded_evidence_axes_to_colorbar(
        figure,
        all_axes=axes,
        folded_axes=(folded_axis,),
    )
    _place_success_temporal_evidence_column_header(
        figure,
        chronological_axis,
        labels["selected_chronological_title"].format(
            unit=labels["selected_title_unit"],
            time_bin=context["display_time_bin"],
        ),
        gid="selected-compare-coverage-chronological-header",
    )
    _place_success_temporal_evidence_column_header(
        figure,
        folded_axis,
        labels["selected_utc_hour_title"].format(
            unit=labels["selected_title_unit"],
        ),
        gid="selected-compare-coverage-folded-header",
    )
    bar_widths = np.diff(context["chronological_edges"]) * 0.78
    _draw_compare_outcome_stack(
        chronological_axis,
        context["chronological_centers"],
        chronological.get("unit_target_counts", []),
        chronological.get("unit_joint_counts", []),
        chronological.get("unit_reference_counts", []),
        labels,
        bar_width=bar_widths,
        y_label=labels["selected_unit_y"],
        gid_prefix="selected-compare-coverage-unit-count",
        integer_axis=True,
    )
    _draw_compare_joint_share_overlay(
        chronological_axis,
        context["chronological_centers"],
        chronological.get("outcome_joint_share_pct", []),
        labels,
        upper_limit=common_share_limit,
        line_color=COMPARE_OUTCOME_JOINT_SHARE_COLOR,
        line_label=labels["selected_joint_share"],
        gid_suffix="selected-outcome-chronological",
    )
    _configure_success_chronological_axis(
        chronological_axis,
        context,
        show_labels=True,
    )
    if folded_data_available:
        _draw_compare_outcome_stack(
            folded_axis,
            context["folded_centers"],
            folded.get("unit_target_counts_per_utc_date", []),
            folded.get("unit_joint_counts_per_utc_date", []),
            folded.get("unit_reference_counts_per_utc_date", []),
            labels,
            bar_width=0.78,
            y_label=labels["selected_unit_folded_y"],
            gid_prefix="selected-compare-coverage-unit-count",
            integer_axis=False,
        )
        folded_axis.yaxis.labelpad = 0.0
        _draw_compare_joint_share_overlay(
            folded_axis,
            context["folded_centers"],
            folded.get("outcome_joint_share_pct", []),
            labels,
            upper_limit=common_share_limit,
            line_color=COMPARE_OUTCOME_JOINT_SHARE_COLOR,
            line_label=labels["selected_joint_share"],
            gid_suffix="selected-outcome-folded",
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
        _set_metric_axis_labels(
            folded_axis,
            y_label=labels["selected_unit_folded_y"],
        )
        folded_axis.yaxis.labelpad = 0.0
        folded_axis.set_ylim(0.0, 1.0)
        folded_axis.set_yticks([])
        _configure_success_folded_axis(
            folded_axis,
            context,
            show_labels=True,
        )
        draw_folded_utc_unavailable_annotation(
            folded_axis,
            labels["folded_unavailable"],
        )
    _place_compare_coverage_legend(
        figure,
        labels,
        selected_path=True,
    )
    _annotate_compare_coverage_note(figure, labels["gate_note"])
    return figure
