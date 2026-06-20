"""
Compare-mode aggregation helpers for WSPRadar.

This module keeps the A/B comparison science separate from map rendering:
joint observations, non-joint evidence, sequential bin pairing, and segment
medians are calculated here; plot_engine only draws the resulting tables.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.snr_utils import round_snr_like_columns


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


def _aggregate_sequential_compare(
    df: pd.DataFrame,
    *,
    min_joint_bins: int,
    tx_ab_bin_minutes: int,
    group_keys: list[str],
    spatial_agg: dict[str, str],
) -> pd.DataFrame:
    """Aggregate sequential TX A/B observations into paired micro-median bins."""
    df_plot = df.copy()
    df_plot["dt_time"] = pd.to_datetime(df_plot["time"])
    df_plot["time_bin"] = df_plot["dt_time"].dt.floor(f"{int(tx_ab_bin_minutes)}min")

    df_t = df_plot[df_plot["is_me"] == 1].copy()
    df_r = df_plot[df_plot["is_me"] == 0].copy()
    spatial_agg_named = {key: (key, value) for key, value in spatial_agg.items()}

    bin_t = (
        df_t.groupby(["time_bin"] + group_keys, dropna=False)
        .agg(
            t_count=("stat_val", "size"),
            t_med=("stat_val", "median"),
            **spatial_agg_named,
        )
        .reset_index()
    )

    bin_r = (
        df_r.groupby(["time_bin"] + group_keys, dropna=False)
        .agg(
            r_count=("stat_val", "size"),
            r_med=("stat_val", "median"),
        )
        .reset_index()
    )

    df_bins = pd.merge(bin_t, bin_r, on=["time_bin"] + group_keys, how="outer")
    df_bins["t_count"] = df_bins["t_count"].fillna(0)
    df_bins["r_count"] = df_bins["r_count"].fillna(0)
    df_bins["is_joint"] = (df_bins["t_count"] > 0) & (df_bins["r_count"] > 0)
    df_bins["bin_delta"] = df_bins["t_med"] - df_bins["r_med"]
    df_bins = round_snr_like_columns(df_bins)

    df_joint = df_bins[df_bins["is_joint"]]
    df_excl = df_bins[~df_bins["is_joint"]]
    spatial_agg_first = {key: (key, "first") for key in spatial_agg.keys()}

    agg_joint = (
        df_joint.groupby(group_keys, dropna=False)
        .agg(
            joint_bins_count=("time_bin", "size"),
            spot_count_u=("t_count", "sum"),
            spot_count_r=("r_count", "sum"),
            stat_val=("bin_delta", "median"),
            **spatial_agg_first,
        )
        .reset_index()
    )
    agg_joint["spot_count"] = agg_joint["spot_count_u"] + agg_joint["spot_count_r"]

    agg_excl = (
        df_excl.groupby(group_keys, dropna=False)
        .agg(
            count_only_u=("t_count", "sum"),
            count_only_r=("r_count", "sum"),
            **spatial_agg_first,
        )
        .reset_index()
    )

    df_agg = pd.merge(agg_joint, agg_excl, on=group_keys, how="outer", suffixes=("", "_excl"))
    for key in spatial_agg.keys():
        duplicate_key = f"{key}_excl"
        if duplicate_key in df_agg.columns:
            df_agg[key] = df_agg[key].fillna(df_agg[duplicate_key])
            df_agg = df_agg.drop(columns=[duplicate_key])

    df_agg = df_agg.fillna(
        {
            "joint_bins_count": 0,
            "spot_count": 0,
            "count_only_u": 0,
            "count_only_r": 0,
        }
    )

    is_joint = df_agg["joint_bins_count"] >= min_joint_bins
    is_u = df_agg["count_only_u"] >= min_joint_bins
    is_r = df_agg["count_only_r"] >= min_joint_bins

    df_agg["stat_val"] = np.where(is_joint, df_agg["stat_val"], np.nan)
    df_agg["spot_count"] = np.where(is_joint, df_agg["spot_count"], 0)
    df_agg["count_only_u"] = np.where(is_u, df_agg["count_only_u"], 0)
    df_agg["count_only_r"] = np.where(is_r, df_agg["count_only_r"], 0)
    return df_agg


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
    tx_ab_bin_minutes: int = 8,
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
        df_agg = _aggregate_sequential_compare(
            work,
            min_joint_bins=min_spots,
            tx_ab_bin_minutes=tx_ab_bin_minutes,
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
