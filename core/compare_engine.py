"""
Compare-mode aggregation helpers for WSPRadar.

This module keeps the A/B comparison science separate from map rendering:
joint observations, non-joint evidence, sequential scheduled pairing, and segment
medians are calculated here; plot_engine only draws the resulting tables.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.snr_utils import round_snr_like_columns
from core.tx_ab_schedule import assign_tx_ab_pair_columns


COMPARE_GROUP_KEYS = [
    "SegmentID",
    "dist_label",
    "dir_name",
    "r_min",
    "r_max",
    "az_bucket",
    "peer_sign",
    "peer_grid",
]

COMPARE_SEGMENT_KEYS = [
    "SegmentID",
    "dist_label",
    "dir_name",
    "r_min",
    "r_max",
    "az_bucket",
]


def _compare_spatial_aggregation_columns(df: pd.DataFrame) -> dict[str, str]:
    """Return first-value geometry/reference aggregations available in df."""
    spatial_agg = {
        "peer_lat": "first",
        "peer_lon": "first",
        "calc_dist": "first",
        "calc_azimuth": "first",
    }
    if "best_ref_sign" in df.columns:
        spatial_agg["best_ref_sign"] = "first"
    if "best_ref_dist" in df.columns:
        spatial_agg["best_ref_dist"] = "first"
    return spatial_agg


def _aggregate_periodic_sequential_compare(
    df: pd.DataFrame,
    *,
    min_joint_pairs: int,
    repeat_interval_minutes: int,
    target_start_minute: int,
    reference_start_minute: int,
    group_keys: list[str],
    spatial_agg: dict[str, str],
) -> pd.DataFrame:
    """Aggregate decoded rows by deterministic scheduled Target/Reference pair."""
    work = df.copy()
    if "tx_ab_pair_id" not in work.columns:
        work = assign_tx_ab_pair_columns(
            work,
            repeat_interval_minutes=repeat_interval_minutes,
            target_start_minute_utc=target_start_minute,
            reference_start_minute_utc=reference_start_minute,
        )

    pair_keys = ["tx_ab_pair_id"] + group_keys
    spatial_agg_named = {key: (key, value) for key, value in spatial_agg.items()}
    pair_spatial = (
        work.groupby(pair_keys, dropna=False)
        .agg(**spatial_agg_named)
        .reset_index()
    )
    target_pairs = (
        work[work["is_me"] == 1]
        .groupby(pair_keys, dropna=False)
        .agg(
            target_decode_count=("stat_val", "size"),
            target_micro_median=("stat_val", "median"),
        )
        .reset_index()
    )
    reference_pairs = (
        work[work["is_me"] == 0]
        .groupby(pair_keys, dropna=False)
        .agg(
            reference_decode_count=("stat_val", "size"),
            reference_micro_median=("stat_val", "median"),
        )
        .reset_index()
    )
    pairs = pd.merge(target_pairs, reference_pairs, on=pair_keys, how="outer")
    pairs = pairs.merge(pair_spatial, on=pair_keys, how="left")
    pairs["target_decode_count"] = pairs["target_decode_count"].fillna(0)
    pairs["reference_decode_count"] = pairs["reference_decode_count"].fillna(0)
    pairs["is_joint"] = (
        (pairs["target_decode_count"] > 0)
        & (pairs["reference_decode_count"] > 0)
    )
    pairs["target_only_pair"] = (
        (pairs["target_decode_count"] > 0)
        & (pairs["reference_decode_count"] == 0)
    ).astype("int64")
    pairs["reference_only_pair"] = (
        (pairs["target_decode_count"] == 0)
        & (pairs["reference_decode_count"] > 0)
    ).astype("int64")
    pairs["pair_delta"] = (
        pairs["target_micro_median"] - pairs["reference_micro_median"]
    )
    pairs = round_snr_like_columns(pairs, columns=["pair_delta"])

    joint_pairs = pairs[pairs["is_joint"]]
    non_joint_pairs = pairs[~pairs["is_joint"]]
    spatial_agg_first = {key: (key, "first") for key in spatial_agg.keys()}
    aggregate_joint = (
        joint_pairs.groupby(group_keys, dropna=False)
        .agg(
            joint_pairs_count=("tx_ab_pair_id", "size"),
            target_decode_count=("target_decode_count", "sum"),
            reference_decode_count=("reference_decode_count", "sum"),
            stat_val=("pair_delta", "median"),
            **spatial_agg_first,
        )
        .reset_index()
    )
    aggregate_non_joint = (
        non_joint_pairs.groupby(group_keys, dropna=False)
        .agg(
            count_only_u=("target_only_pair", "sum"),
            count_only_r=("reference_only_pair", "sum"),
            **spatial_agg_first,
        )
        .reset_index()
    )
    aggregate = pd.merge(
        aggregate_joint,
        aggregate_non_joint,
        on=group_keys,
        how="outer",
        suffixes=("", "_non_joint"),
    )
    for key in spatial_agg.keys():
        duplicate_key = f"{key}_non_joint"
        if duplicate_key in aggregate.columns:
            aggregate[key] = aggregate[key].fillna(aggregate[duplicate_key])
            aggregate = aggregate.drop(columns=[duplicate_key])

    aggregate = aggregate.fillna(
        {
            "joint_pairs_count": 0,
            "target_decode_count": 0,
            "reference_decode_count": 0,
            "count_only_u": 0,
            "count_only_r": 0,
        }
    )
    has_joint_evidence = aggregate["joint_pairs_count"] >= min_joint_pairs
    has_target_only_evidence = aggregate["count_only_u"] >= min_joint_pairs
    has_reference_only_evidence = aggregate["count_only_r"] >= min_joint_pairs

    aggregate["stat_val"] = np.where(
        has_joint_evidence,
        aggregate["stat_val"],
        np.nan,
    )
    # ``spot_count`` remains the shared downstream evidence-count field. For
    # periodic TX A/B it deliberately counts joint scheduled pairs, not raw rows.
    aggregate["spot_count"] = np.where(
        has_joint_evidence,
        aggregate["joint_pairs_count"],
        0,
    )
    aggregate["count_only_u"] = np.where(
        has_target_only_evidence,
        aggregate["count_only_u"],
        0,
    )
    aggregate["count_only_r"] = np.where(
        has_reference_only_evidence,
        aggregate["count_only_r"],
        0,
    )
    return aggregate


def _aggregate_simultaneous_compare(
    df: pd.DataFrame,
    *,
    min_joint_spots: int,
    group_keys: list[str],
    spatial_agg: dict[str, str],
) -> pd.DataFrame:
    """Aggregate simultaneous RX/TX compare observations into station evidence."""
    df_plot = df.copy()
    df_plot["is_joint_spot"] = ((df_plot["has_u"] > 0) & (df_plot["has_r"] > 0)).astype(int)
    df_plot["is_u_spot"] = ((df_plot["has_u"] > 0) & (df_plot["has_r"] == 0)).astype(int)
    df_plot["is_r_spot"] = ((df_plot["has_u"] == 0) & (df_plot["has_r"] > 0)).astype(int)
    df_plot["spot_diff"] = np.where(
        df_plot["is_joint_spot"] == 1,
        df_plot["snr_u_norm"] - df_plot["snr_r_norm"],
        np.nan,
    )
    df_plot = round_snr_like_columns(df_plot)

    agg_ops = {
        "is_joint_spot": "sum",
        "is_u_spot": "sum",
        "is_r_spot": "sum",
        "spot_diff": "median",
        **spatial_agg,
    }
    df_agg = df_plot.groupby(group_keys, dropna=False).agg(agg_ops).reset_index()

    cnt_j = df_agg["is_joint_spot"]
    cnt_u = df_agg["is_u_spot"]
    cnt_r = df_agg["is_r_spot"]

    is_joint = cnt_j >= min_joint_spots
    is_u = cnt_u >= min_joint_spots
    is_r = cnt_r >= min_joint_spots

    df_agg["spot_count"] = np.where(is_joint, cnt_j, 0)
    df_agg["count_only_u"] = np.where(is_u, cnt_u, 0)
    df_agg["count_only_r"] = np.where(is_r, cnt_r, 0)
    df_agg["stat_val"] = np.where(is_joint, df_agg["spot_diff"], np.nan)
    return df_agg.drop(columns=["is_joint_spot", "is_u_spot", "is_r_spot", "spot_diff"])


def aggregate_compare_map_data(
    df: pd.DataFrame,
    *,
    is_sequential: bool,
    min_spots: int,
    base_min_stations: int,
    tx_ab_repeat_interval_minutes: int = 10,
    tx_ab_target_start_minute: int = 0,
    tx_ab_reference_start_minute: int = 2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aggregate raw Compare rows into map station rows and segment medians.

    The returned dataframes intentionally preserve the historical plot_engine
    schema so the segment inspector, export flow, and map rendering continue to
    see the same columns.
    """
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    work = df.copy()
    min_spots = int(min_spots)
    base_min_stations = int(base_min_stations)
    spatial_agg = _compare_spatial_aggregation_columns(work)

    if is_sequential:
        df_agg = _aggregate_periodic_sequential_compare(
            work,
            min_joint_pairs=min_spots,
            repeat_interval_minutes=tx_ab_repeat_interval_minutes,
            target_start_minute=tx_ab_target_start_minute,
            reference_start_minute=tx_ab_reference_start_minute,
            group_keys=COMPARE_GROUP_KEYS,
            spatial_agg=spatial_agg,
        )
    else:
        df_agg = _aggregate_simultaneous_compare(
            work,
            min_joint_spots=min_spots,
            group_keys=COMPARE_GROUP_KEYS,
            spatial_agg=spatial_agg,
        )

    df_plot = df_agg[
        (df_agg["spot_count"] > 0)
        | (df_agg["count_only_u"] > 0)
        | (df_agg["count_only_r"] > 0)
    ].copy()
    df_plot = round_snr_like_columns(df_plot)

    def segment_agg(segment_df):
        vals = segment_df["stat_val"].dropna()
        cnt = segment_df.loc[segment_df["spot_count"] > 0, "peer_sign"].nunique()
        return pd.Series(
            {
                "val": vals.median() if len(vals) > 0 else np.nan,
                "cnt": cnt,
                "total_spots": segment_df["spot_count"].sum(),
            }
        )

    if df_plot.empty:
        return df_plot, pd.DataFrame(columns=COMPARE_SEGMENT_KEYS + ["val", "cnt", "total_spots"])

    segs = df_plot.groupby(COMPARE_SEGMENT_KEYS).apply(segment_agg).reset_index()
    segs = round_snr_like_columns(segs, columns=["val"])
    segs = segs[segs["cnt"] >= base_min_stations]
    return df_plot, segs


def compare_footer_counts(df_plot: pd.DataFrame, *, max_dist_km: float) -> dict[str, int]:
    """Return station/spot yield counts for the Compare map footer bars."""
    if df_plot is None or df_plot.empty:
        return {
            "stat_joint": 0,
            "stat_both_async": 0,
            "stat_only_u": 0,
            "stat_only_r": 0,
            "spot_joint": 0,
            "spot_both_async": 0,
            "spot_only_u": 0,
            "spot_only_r": 0,
            "tot_stats": 0,
            "tot_spots": 0,
        }

    df_footer = df_plot[df_plot["r_min"] < max_dist_km]
    stat_joint = len(df_footer[df_footer["spot_count"] > 0])
    stat_both_async = len(
        df_footer[
            (df_footer["spot_count"] == 0)
            & (df_footer["count_only_u"] > 0)
            & (df_footer["count_only_r"] > 0)
        ]
    )
    stat_only_u = len(
        df_footer[
            (df_footer["spot_count"] == 0)
            & (df_footer["count_only_u"] > 0)
            & (df_footer["count_only_r"] == 0)
        ]
    )
    stat_only_r = len(
        df_footer[
            (df_footer["spot_count"] == 0)
            & (df_footer["count_only_u"] == 0)
            & (df_footer["count_only_r"] > 0)
        ]
    )

    spot_joint = int(df_footer["spot_count"].sum())
    spot_both_async = int(
        df_footer[
            (df_footer["spot_count"] == 0)
            & (df_footer["count_only_u"] > 0)
            & (df_footer["count_only_r"] > 0)
        ][["count_only_u", "count_only_r"]]
        .sum()
        .sum()
    )
    spot_both_async += int(
        df_footer[df_footer["spot_count"] > 0][["count_only_u", "count_only_r"]]
        .sum()
        .sum()
    )
    spot_only_u = int(
        df_footer[
            (df_footer["spot_count"] == 0)
            & (df_footer["count_only_u"] > 0)
            & (df_footer["count_only_r"] == 0)
        ]["count_only_u"].sum()
    )
    spot_only_r = int(
        df_footer[
            (df_footer["spot_count"] == 0)
            & (df_footer["count_only_u"] == 0)
            & (df_footer["count_only_r"] > 0)
        ]["count_only_r"].sum()
    )

    return {
        "stat_joint": int(stat_joint),
        "stat_both_async": int(stat_both_async),
        "stat_only_u": int(stat_only_u),
        "stat_only_r": int(stat_only_r),
        "spot_joint": int(spot_joint),
        "spot_both_async": int(spot_both_async),
        "spot_only_u": int(spot_only_u),
        "spot_only_r": int(spot_only_r),
        "tot_stats": int(stat_only_u + stat_joint + stat_both_async + stat_only_r),
        "tot_spots": int(spot_only_u + spot_joint + spot_both_async + spot_only_r),
    }
