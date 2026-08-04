"""Evidence dataframe builders for Segment Inspector views."""

import numpy as np
import pandas as pd

from core.artifact_store import read_parquet_artifact
from core.tx_ab_schedule import assign_tx_ab_pair_columns

COMPARE_OUTCOME_TARGET_ONLY = "target_only"
COMPARE_OUTCOME_JOINT = "joint"
COMPARE_OUTCOME_REFERENCE_ONLY = "reference_only"
COMPARE_OUTCOMES = (
    COMPARE_OUTCOME_TARGET_ONLY,
    COMPARE_OUTCOME_JOINT,
    COMPARE_OUTCOME_REFERENCE_ONLY,
)


def _empty_evidence_df():
    return pd.DataFrame(columns=["identity", "station", "grid", "plot_time", "metric", "identity_order"])


def _empty_compare_unit_df():
    """Return the canonical retained Benchmark-unit schema."""
    return pd.DataFrame(
        columns=[
            "identity",
            "peer_sign",
            "peer_grid",
            "identity_order",
            "evidence_utc",
            "outcome",
            "metric",
            "paired_eligible",
        ]
    )


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


def _build_compare_unit_rows(
    station_df,
    identity_df,
    is_sequential,
    *,
    paired_identity_df=None,
    tx_ab_repeat_interval_minutes=10,
    tx_ab_target_start_minute=0,
    tx_ab_reference_start_minute=2,
):
    """Build one canonical row per retained simultaneous cycle or scheduled pair.

    ``identity_df`` defines the active callsign-plus-locator population.
    ``paired_identity_df`` identifies the subset admitted to segment-level
    paired-Delta-SNR views; coverage retains all active identities. Sequential
    rows are reduced to one planned pair per receiver after applying the
    established per-side micro-median contract.
    """
    identity_meta = _prepare_identity_meta(identity_df)
    if (
        identity_meta.empty
        or station_df is None
        or station_df.empty
        or not {"peer_sign", "peer_grid"}.issubset(station_df.columns)
    ):
        return _empty_compare_unit_df()

    work = station_df.copy()
    work["peer_sign"] = work["peer_sign"].astype(str)
    work["peer_grid"] = work["peer_grid"].astype(str)
    work = work.merge(
        identity_meta,
        on=["peer_sign", "peer_grid"],
        how="inner",
    )
    if work.empty:
        return _empty_compare_unit_df()

    if is_sequential:
        if "tx_ab_pair_id" not in work.columns:
            required_schedule_columns = {"time", "is_me"}
            if not required_schedule_columns.issubset(work.columns):
                return _empty_compare_unit_df()
            work = assign_tx_ab_pair_columns(
                work,
                repeat_interval_minutes=tx_ab_repeat_interval_minutes,
                target_start_minute_utc=tx_ab_target_start_minute,
                reference_start_minute_utc=tx_ab_reference_start_minute,
            )
        required_columns = {
            "peer_sign",
            "peer_grid",
            "identity",
            "identity_order",
            "tx_ab_pair_id",
            "is_me",
            "stat_val",
        }
        if not required_columns.issubset(work.columns):
            return _empty_compare_unit_df()

        pair_rows = work[list(required_columns)].copy()
        pair_rows["is_me"] = pd.to_numeric(
            pair_rows["is_me"],
            errors="coerce",
        )
        pair_rows["stat_val"] = pd.to_numeric(
            pair_rows["stat_val"],
            errors="coerce",
        )
        pair_rows["tx_ab_pair_id"] = pd.to_numeric(
            pair_rows["tx_ab_pair_id"],
            errors="coerce",
        )
        pair_rows = pair_rows[pair_rows["tx_ab_pair_id"].notna()].copy()
        if pair_rows.empty:
            return _empty_compare_unit_df()
        pair_rows["tx_ab_pair_id"] = pair_rows["tx_ab_pair_id"].astype("int64")
        pair_keys = [
            "peer_sign",
            "peer_grid",
            "identity",
            "identity_order",
            "tx_ab_pair_id",
        ]
        target_pairs = (
            pair_rows[pair_rows["is_me"] == 1]
            .groupby(pair_keys, dropna=False, observed=True)
            .agg(
                target_decode_count=("stat_val", "count"),
                target_snr=("stat_val", "median"),
            )
            .reset_index()
        )
        reference_pairs = (
            pair_rows[pair_rows["is_me"] == 0]
            .groupby(pair_keys, dropna=False, observed=True)
            .agg(
                reference_decode_count=("stat_val", "count"),
                reference_snr=("stat_val", "median"),
            )
            .reset_index()
        )
        units = target_pairs.merge(
            reference_pairs,
            on=pair_keys,
            how="outer",
        )
        units["target_decode_count"] = (
            pd.to_numeric(units["target_decode_count"], errors="coerce")
            .fillna(0)
            .astype("int64")
        )
        units["reference_decode_count"] = (
            pd.to_numeric(units["reference_decode_count"], errors="coerce")
            .fillna(0)
            .astype("int64")
        )
        has_target = units["target_decode_count"] > 0
        has_reference = units["reference_decode_count"] > 0
        units["outcome"] = np.select(
            [
                has_target & has_reference,
                has_target & ~has_reference,
                ~has_target & has_reference,
            ],
            [
                COMPARE_OUTCOME_JOINT,
                COMPARE_OUTCOME_TARGET_ONLY,
                COMPARE_OUTCOME_REFERENCE_ONLY,
            ],
            default="",
        )
        units["evidence_utc"] = pd.to_datetime(
            units["tx_ab_pair_id"],
            unit="m",
            utc=True,
            errors="coerce",
        )
        units["metric"] = np.where(
            units["outcome"] == COMPARE_OUTCOME_JOINT,
            pd.to_numeric(units["target_snr"], errors="coerce")
            - pd.to_numeric(units["reference_snr"], errors="coerce"),
            np.nan,
        )
    else:
        required_columns = {
            "peer_sign",
            "peer_grid",
            "identity",
            "identity_order",
            "time_slot",
            "has_u",
            "has_r",
            "snr_u_norm",
            "snr_r_norm",
        }
        if not required_columns.issubset(work.columns):
            return _empty_compare_unit_df()
        units = work[list(required_columns)].copy()
        for column in [
            "time_slot",
            "has_u",
            "has_r",
            "snr_u_norm",
            "snr_r_norm",
        ]:
            units[column] = pd.to_numeric(units[column], errors="coerce")
        has_target = units["has_u"] > 0
        has_reference = units["has_r"] > 0
        units["outcome"] = np.select(
            [
                has_target & has_reference,
                has_target & ~has_reference,
                ~has_target & has_reference,
            ],
            [
                COMPARE_OUTCOME_JOINT,
                COMPARE_OUTCOME_TARGET_ONLY,
                COMPARE_OUTCOME_REFERENCE_ONLY,
            ],
            default="",
        )
        units["evidence_utc"] = pd.to_datetime(
            units["time_slot"] * 120,
            unit="s",
            utc=True,
            errors="coerce",
        )
        units["metric"] = np.where(
            units["outcome"] == COMPARE_OUTCOME_JOINT,
            units["snr_u_norm"] - units["snr_r_norm"],
            np.nan,
        )

    units = units[
        units["outcome"].isin(COMPARE_OUTCOMES)
        & units["evidence_utc"].notna()
    ].copy()
    if units.empty:
        return _empty_compare_unit_df()

    paired_meta = _prepare_identity_meta(
        identity_df if paired_identity_df is None else paired_identity_df
    )[["peer_sign", "peer_grid"]].drop_duplicates()
    paired_meta["paired_eligible"] = True
    units = units.merge(
        paired_meta,
        on=["peer_sign", "peer_grid"],
        how="left",
    )
    units["paired_eligible"] = units["paired_eligible"].fillna(False).astype(bool)
    units["metric"] = pd.to_numeric(units["metric"], errors="coerce")
    identity_labels = identity_meta["identity"].tolist()
    units["identity"] = pd.Categorical(
        units["identity"],
        categories=identity_labels,
        ordered=True,
    )
    return (
        units[
            [
                "identity",
                "peer_sign",
                "peer_grid",
                "identity_order",
                "evidence_utc",
                "outcome",
                "metric",
                "paired_eligible",
            ]
        ]
        .sort_values(["identity_order", "evidence_utc"])
        .reset_index(drop=True)
    )


def _compare_joint_evidence_points(
    comparison_units,
    *,
    require_paired_eligible=False,
):
    """Project non-missing Joint units into the established Delta-SNR schema."""
    if comparison_units is None or comparison_units.empty:
        return _empty_evidence_df()
    required_columns = {
        "identity",
        "peer_sign",
        "peer_grid",
        "identity_order",
        "evidence_utc",
        "outcome",
        "metric",
        "paired_eligible",
    }
    if not required_columns.issubset(comparison_units.columns):
        return _empty_evidence_df()
    paired = comparison_units[
        comparison_units["outcome"].eq(COMPARE_OUTCOME_JOINT)
    ].copy()
    if require_paired_eligible:
        paired = paired[paired["paired_eligible"]].copy()
    paired["metric"] = pd.to_numeric(paired["metric"], errors="coerce")
    paired = paired[
        paired["identity"].notna()
        & paired["evidence_utc"].notna()
        & paired["metric"].notna()
    ].copy()
    if paired.empty:
        return _empty_evidence_df()
    # Preserve the established absolute Delta-SNR display contract while the
    # canonical units retain full precision for new scientific aggregation.
    paired["metric"] = paired["metric"].round(1)
    paired = paired.rename(
        columns={
            "peer_sign": "station",
            "peer_grid": "grid",
            "evidence_utc": "plot_time",
        }
    )
    return paired[
        [
            "identity",
            "station",
            "grid",
            "identity_order",
            "plot_time",
            "metric",
        ]
    ].reset_index(drop=True)


def _retain_thresholded_compare_outcomes(
    comparison_units,
    thresholded_station_rows,
):
    """Keep only outcome categories retained by station-level thresholds."""
    threshold_columns = [
        "peer_sign",
        "peer_grid",
        "spot_count",
        "count_only_u",
        "count_only_r",
    ]
    if (
        comparison_units is None
        or comparison_units.empty
        or thresholded_station_rows is None
        or not set(threshold_columns).issubset(
            thresholded_station_rows.columns
        )
    ):
        return comparison_units

    category_eligibility = thresholded_station_rows[
        threshold_columns
    ].copy()
    category_eligibility["peer_sign"] = (
        category_eligibility["peer_sign"].astype(str)
    )
    category_eligibility["peer_grid"] = (
        category_eligibility["peer_grid"].astype(str)
    )
    category_eligibility = (
        category_eligibility.groupby(
            ["peer_sign", "peer_grid"],
            dropna=False,
            observed=True,
        )
        .agg(
            retain_joint=("spot_count", lambda values: (values > 0).any()),
            retain_target=(
                "count_only_u",
                lambda values: (values > 0).any(),
            ),
            retain_reference=(
                "count_only_r",
                lambda values: (values > 0).any(),
            ),
        )
        .reset_index()
    )
    comparison_units = comparison_units.merge(
        category_eligibility,
        on=["peer_sign", "peer_grid"],
        how="left",
    )
    keep_outcome = (
        (
            comparison_units["outcome"].eq(COMPARE_OUTCOME_JOINT)
            & comparison_units["retain_joint"].fillna(False)
        )
        | (
            comparison_units["outcome"].eq(COMPARE_OUTCOME_TARGET_ONLY)
            & comparison_units["retain_target"].fillna(False)
        )
        | (
            comparison_units["outcome"].eq(
                COMPARE_OUTCOME_REFERENCE_ONLY
            )
            & comparison_units["retain_reference"].fillna(False)
        )
    )
    return (
        comparison_units.loc[
            keep_outcome,
            _empty_compare_unit_df().columns,
        ]
        .reset_index(drop=True)
    )


def _build_evidence_points(
    station_df,
    identity_df,
    is_sequential,
    *,
    tx_ab_repeat_interval_minutes=10,
    tx_ab_target_start_minute=0,
    tx_ab_reference_start_minute=2,
):
    """Build Benchmark Delta-SNR points for selected station identities."""
    comparison_units = _build_compare_unit_rows(
        station_df,
        identity_df,
        is_sequential,
        paired_identity_df=identity_df,
        tx_ab_repeat_interval_minutes=tx_ab_repeat_interval_minutes,
        tx_ab_target_start_minute=tx_ab_target_start_minute,
        tx_ab_reference_start_minute=tx_ab_reference_start_minute,
    )
    return _compare_joint_evidence_points(comparison_units)


def _build_segment_compare_units(
    scope_identity_df,
    paired_identity_df,
    parquet_path,
    is_sequential,
    *,
    tx_ab_repeat_interval_minutes=10,
    tx_ab_target_start_minute=0,
    tx_ab_reference_start_minute=2,
):
    """Load one projected active-scope frame and build all retained Benchmark units.

    When the scoped station frame carries the established thresholded category
    counts, units are retained only for outcome categories that survived that
    station-level threshold. This keeps temporal coverage aligned with the map,
    footer, and Station Insights population.
    """
    scope_meta = _prepare_identity_meta(scope_identity_df)
    if scope_meta.empty:
        return _empty_compare_unit_df()
    paired_meta = _prepare_identity_meta(paired_identity_df)
    if not paired_meta.empty:
        ordered_scope_meta = pd.concat(
            [
                paired_meta[["peer_sign", "peer_grid"]],
                scope_meta[["peer_sign", "peer_grid"]],
            ],
            ignore_index=True,
        ).drop_duplicates(
            subset=["peer_sign", "peer_grid"],
            keep="first",
        )
        scope_meta = _prepare_identity_meta(ordered_scope_meta)

    read_columns = ["peer_sign", "peer_grid"]
    if is_sequential:
        read_columns += ["tx_ab_pair_id", "is_me", "stat_val"]
    else:
        read_columns += [
            "time_slot",
            "has_u",
            "has_r",
            "snr_u_norm",
            "snr_r_norm",
        ]

    try:
        raw_df = read_parquet_artifact(
            parquet_path,
            columns=read_columns,
            filters=[
                (
                    "peer_sign",
                    "in",
                    scope_meta["peer_sign"].unique().tolist(),
                )
            ],
        )
    except (FileNotFoundError, KeyError, ValueError):
        return _empty_compare_unit_df()

    comparison_units = _build_compare_unit_rows(
        raw_df,
        scope_meta,
        is_sequential,
        paired_identity_df=paired_identity_df,
        tx_ab_repeat_interval_minutes=tx_ab_repeat_interval_minutes,
        tx_ab_target_start_minute=tx_ab_target_start_minute,
        tx_ab_reference_start_minute=tx_ab_reference_start_minute,
    )
    return _retain_thresholded_compare_outcomes(
        comparison_units,
        scope_identity_df,
    )


def _build_segment_evidence_points(
    df_seg,
    parquet_path,
    is_sequential,
    *,
    tx_ab_repeat_interval_minutes=10,
    tx_ab_target_start_minute=0,
    tx_ab_reference_start_minute=2,
):
    """Build Benchmark segment evidence from projected station-identity rows."""
    comparison_units = _build_segment_compare_units(
        df_seg,
        df_seg,
        parquet_path,
        is_sequential,
        tx_ab_repeat_interval_minutes=tx_ab_repeat_interval_minutes,
        tx_ab_target_start_minute=tx_ab_target_start_minute,
        tx_ab_reference_start_minute=tx_ab_reference_start_minute,
    )
    return _compare_joint_evidence_points(
        comparison_units,
        require_paired_eligible=True,
    )
