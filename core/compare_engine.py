"""
Benchmark-mode aggregation helpers for WSPRadar.

This module keeps the A/B comparison science separate from map rendering:
joint observations, non-joint evidence, and segment
medians are calculated here; plot_engine only draws the resulting tables.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.snr_utils import round_snr_like_columns


# Reported peer identity is exact callsign plus full locator, not a unique
# physical station. Both Benchmark paths aggregate one row per identity/segment.
COMPARE_PEER_IDENTITY_KEYS = ["peer_sign", "peer_grid"]

COMPARE_GROUP_KEYS = [
    "SegmentID",
    "dist_label",
    "dir_name",
    "r_min",
    "r_max",
    "az_bucket",
    *COMPARE_PEER_IDENTITY_KEYS,
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


def _aggregate_simultaneous_compare(
    df: pd.DataFrame,
    *,
    min_joint_spots: int,
    group_keys: list[str],
    spatial_agg: dict[str, str],
) -> pd.DataFrame:
    """Aggregate an owned simultaneous RX/TX frame into station evidence."""
    df_plot = df
    df_plot["is_joint_spot"] = ((df_plot["has_u"] > 0) & (df_plot["has_r"] > 0)).astype(int)
    df_plot["is_u_spot"] = ((df_plot["has_u"] > 0) & (df_plot["has_r"] == 0)).astype(int)
    df_plot["is_r_spot"] = ((df_plot["has_u"] == 0) & (df_plot["has_r"] > 0)).astype(int)
    df_plot["spot_diff"] = np.where(
        df_plot["is_joint_spot"] == 1,
        df_plot["snr_u_norm"] - df_plot["snr_r_norm"],
        np.nan,
    )
    df_plot = round_snr_like_columns(df_plot, owns_input=True)

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
    min_spots: int,
    base_min_stations: int,
    owns_input: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aggregate raw Benchmark rows into map station rows and segment medians.

    A station row represents one exact callsign/full-reported-locator identity
    within a segment. Each identity meeting the paired-evidence requirement
    contributes one median and one support count to that segment, regardless of
    its observation count or other identities sharing its callsign.

    The returned dataframes intentionally preserve the historical plot_engine
    schema so the segment inspector, export flow, and map rendering continue to
    see the same columns. By default the raw input remains unchanged. When
    ``owns_input`` is true, the caller transfers the frame for in-place
    transient-column preparation and must not use it afterward.
    """
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    work = df if owns_input else df.copy()
    min_spots = int(min_spots)
    base_min_stations = int(base_min_stations)
    spatial_agg = _compare_spatial_aggregation_columns(work)

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
    df_plot = round_snr_like_columns(df_plot, owns_input=True)

    def segment_agg(segment_df):
        """Use the same qualifying identity medians for segment value and support."""
        # COMPARE_GROUP_KEYS already guarantees one row per peer identity in
        # this segment. Counting callsigns would merge separately weighted paths.
        qualifying_station_medians = segment_df.loc[
            segment_df["spot_count"] > 0, "stat_val"
        ].dropna()
        return pd.Series(
            {
                "val": (
                    qualifying_station_medians.median()
                    if not qualifying_station_medians.empty
                    else np.nan
                ),
                "cnt": len(qualifying_station_medians),
                "total_spots": segment_df["spot_count"].sum(),
            }
        )

    if df_plot.empty:
        return df_plot, pd.DataFrame(columns=COMPARE_SEGMENT_KEYS + ["val", "cnt", "total_spots"])

    segs = df_plot.groupby(COMPARE_SEGMENT_KEYS).apply(segment_agg).reset_index()
    segs = round_snr_like_columns(
        segs,
        columns=["val"],
        owns_input=True,
    )
    segs = segs[segs["cnt"] >= base_min_stations]
    return df_plot, segs


def compare_footer_counts(df_plot: pd.DataFrame, *, max_dist_km: float) -> dict[str, int]:
    """Return station/spot yield counts for the Benchmark map footer bars."""
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
