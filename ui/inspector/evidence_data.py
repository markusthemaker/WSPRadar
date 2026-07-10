"""Evidence dataframe builders for Segment Inspector views."""

import numpy as np
import pandas as pd

from core.artifact_store import read_parquet_artifact

def _empty_evidence_df():
    return pd.DataFrame(columns=["identity", "station", "grid", "plot_time", "metric", "identity_order"])

def _prepare_identity_meta(identity_df):
    """Normalize selected station identities to callsign+locator rows with stable labels."""
    if identity_df is None or identity_df.empty or not {"peer_sign", "peer_grid"}.issubset(identity_df.columns):
        return pd.DataFrame(columns=["peer_sign", "peer_grid", "identity", "identity_order"])

    meta = identity_df[["peer_sign", "peer_grid"]].dropna().copy()
    meta["peer_sign"] = meta["peer_sign"].astype(str)
    meta["peer_grid"] = meta["peer_grid"].astype(str)
    meta = meta.drop_duplicates().reset_index(drop=True)
    meta["identity"] = meta["peer_sign"] + " (" + meta["peer_grid"] + ")"
    meta["identity_order"] = np.arange(len(meta))
    return meta

def _build_evidence_points(
    station_df,
    identity_df,
    is_compare,
    is_sequential,
    *,
    tx_ab_bin_minutes=8,
):
    """Build raw evidence points for the selected station+locator distribution and time plots."""
    identity_meta = _prepare_identity_meta(identity_df)
    if identity_meta.empty or station_df.empty:
        return _empty_evidence_df()

    station_df = station_df.copy()
    if not {"peer_sign", "peer_grid"}.issubset(station_df.columns):
        return _empty_evidence_df()
    station_df["peer_sign"] = station_df["peer_sign"].astype(str)
    station_df["peer_grid"] = station_df["peer_grid"].astype(str)
    station_df = station_df.merge(identity_meta, on=["peer_sign", "peer_grid"], how="inner")
    if station_df.empty:
        return _empty_evidence_df()

    if not is_compare:
        if "time" not in station_df.columns or "stat_val" not in station_df.columns:
            return _empty_evidence_df()

        evidence_df = station_df[["peer_sign", "peer_grid", "identity", "identity_order", "time", "stat_val"]].copy()
        evidence_df["plot_time"] = pd.to_datetime(evidence_df["time"], errors="coerce")
        evidence_df["metric"] = pd.to_numeric(evidence_df["stat_val"], errors="coerce")
    elif is_sequential:
        required_cols = {"peer_sign", "peer_grid", "identity", "identity_order", "time", "is_me", "stat_val"}
        if not required_cols.issubset(station_df.columns):
            return _empty_evidence_df()

        bin_minutes = int(tx_ab_bin_minutes)
        work_df = station_df[list(required_cols)].copy()
        work_df["dt_time"] = pd.to_datetime(work_df["time"], errors="coerce")
        work_df = work_df.dropna(subset=["dt_time"])
        work_df["time_bin"] = work_df["dt_time"].dt.floor(f"{bin_minutes}min")
        work_df["is_me"] = pd.to_numeric(work_df["is_me"], errors="coerce")
        work_df["stat_val"] = pd.to_numeric(work_df["stat_val"], errors="coerce")

        target_df = (
            work_df[work_df["is_me"] == 1]
            .groupby(["peer_sign", "peer_grid", "identity", "identity_order", "time_bin"], dropna=False)["stat_val"]
            .median()
            .reset_index(name="target_snr")
        )
        ref_df = (
            work_df[work_df["is_me"] == 0]
            .groupby(["peer_sign", "peer_grid", "identity", "identity_order", "time_bin"], dropna=False)["stat_val"]
            .median()
            .reset_index(name="ref_snr")
        )
        evidence_df = target_df.merge(
            ref_df,
            on=["peer_sign", "peer_grid", "identity", "identity_order", "time_bin"],
            how="inner"
        )
        evidence_df["plot_time"] = evidence_df["time_bin"]
        evidence_df["metric"] = evidence_df["target_snr"] - evidence_df["ref_snr"]
    else:
        required_cols = {"peer_sign", "peer_grid", "identity", "identity_order", "time_slot", "has_u", "has_r", "snr_u_norm", "snr_r_norm"}
        if not required_cols.issubset(station_df.columns):
            return _empty_evidence_df()

        evidence_df = station_df[list(required_cols)].copy()
        for col in ["time_slot", "has_u", "has_r", "snr_u_norm", "snr_r_norm"]:
            evidence_df[col] = pd.to_numeric(evidence_df[col], errors="coerce")
        evidence_df = evidence_df[(evidence_df["has_u"] > 0) & (evidence_df["has_r"] > 0)]
        evidence_df["plot_time"] = pd.to_datetime(evidence_df["time_slot"] * 120, unit="s", errors="coerce")
        evidence_df["metric"] = (
            pd.to_numeric(evidence_df["snr_u_norm"], errors="coerce") -
            pd.to_numeric(evidence_df["snr_r_norm"], errors="coerce")
        )

    evidence_df = evidence_df[["identity", "peer_sign", "peer_grid", "identity_order", "plot_time", "metric"]].copy()
    evidence_df.columns = ["identity", "station", "grid", "identity_order", "plot_time", "metric"]
    evidence_df = evidence_df.dropna(subset=["identity", "plot_time", "metric"])
    if evidence_df.empty:
        return evidence_df

    evidence_df["metric"] = evidence_df["metric"].round(1)
    identity_labels = identity_meta["identity"].tolist()
    evidence_df["identity"] = pd.Categorical(evidence_df["identity"], categories=identity_labels, ordered=True)
    return evidence_df.sort_values(["identity_order", "plot_time"]).reset_index(drop=True)

def _build_segment_evidence_points(
    df_seg,
    parquet_path,
    is_compare,
    is_sequential,
    *,
    tx_ab_bin_minutes=8,
):
    """Build raw segment-level evidence points from parquet using station+locator identity."""
    if df_seg.empty or not {"peer_sign", "peer_grid"}.issubset(df_seg.columns):
        return _empty_evidence_df()

    segment_meta = df_seg[["peer_sign", "peer_grid"]].dropna().copy()
    segment_meta["peer_sign"] = segment_meta["peer_sign"].astype(str)
    segment_meta["peer_grid"] = segment_meta["peer_grid"].astype(str)
    segment_meta = segment_meta.drop_duplicates()
    if segment_meta.empty:
        return _empty_evidence_df()

    read_columns = ["peer_sign", "peer_grid"]
    if not is_compare:
        read_columns += ["time", "stat_val"]
    elif is_sequential:
        read_columns += ["time", "is_me", "stat_val"]
    else:
        read_columns += ["time_slot", "has_u", "has_r", "snr_u_norm", "snr_r_norm"]

    try:
        raw_df = read_parquet_artifact(
            parquet_path,
            columns=read_columns,
            filters=[("peer_sign", "in", segment_meta["peer_sign"].unique().tolist())]
        )
    except (FileNotFoundError, KeyError, ValueError):
        return _empty_evidence_df()

    if raw_df.empty:
        return _empty_evidence_df()

    raw_df["peer_sign"] = raw_df["peer_sign"].astype(str)
    raw_df["peer_grid"] = raw_df["peer_grid"].astype(str)
    segment_raw_df = raw_df.merge(segment_meta, on=["peer_sign", "peer_grid"], how="inner")
    if segment_raw_df.empty:
        return _empty_evidence_df()

    return _build_evidence_points(
        segment_raw_df,
        segment_meta,
        is_compare,
        is_sequential,
        tx_ab_bin_minutes=tx_ab_bin_minutes,
    )
