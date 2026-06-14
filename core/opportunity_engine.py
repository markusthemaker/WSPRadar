"""
Opportunity-based Absolute analysis for WSPRadar.

The server query returns one row per UTC WSPR cycle and remote
callsign/locator identity. All scientific classification and peer-balanced
aggregation is then performed locally from that compact evidence table.
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

from core.math_utils import is_valid_6char_locator, is_valid_callsign, locator_to_latlon


ABSOLUTE_METHOD_VERSION = "opportunity-v1"
DEFAULT_MIN_OPPORTUNITIES = 5


def opportunity_rate_scale_max(values, minimum=1.0):
    """
    Return a readable linear upper limit for confirmation-rate plots.

    The limit adds 10 percent headroom above the largest finite value, keeps
    zero visible, and never exceeds the physical 100 percent ceiling.
    """
    numeric = pd.to_numeric(pd.Series(values, dtype="float64"), errors="coerce")
    numeric = numeric[np.isfinite(numeric) & (numeric >= 0.0)]
    minimum = min(max(float(minimum), 0.1), 100.0)
    if numeric.empty:
        return minimum

    maximum = float(numeric.max())
    if maximum <= 0.0:
        return minimum
    return min(100.0, max(minimum, round(maximum * 1.10, 1)))


def _sql_literal(value: str) -> str:
    """Return a single-quoted SQL literal after strict upstream validation."""
    return "'" + value.replace("'", "''") + "'"


def _is_valid_maidenhead(locator: str) -> bool:
    locator = str(locator or "").strip().upper()
    if len(locator) == 4:
        return (
            "A" <= locator[0] <= "R" and
            "A" <= locator[1] <= "R" and
            locator[2].isdigit() and
            locator[3].isdigit()
        )
    return is_valid_6char_locator(locator)


def target_grid4(qth: str) -> str:
    """Return the configured four-character target grid used for identity matching."""
    qth = str(qth or "").strip().upper()
    if not _is_valid_maidenhead(qth):
        raise ValueError("Absolute opportunity analysis requires a valid target QTH locator.")
    return qth[:4]


def build_absolute_opportunity_query(
    *,
    mode: str,
    start_t: datetime,
    end_t: datetime,
    band_value: str,
    callsign: str,
    qth: str,
    exclude_special_callsigns: bool = False,
    target_frame_mod4: int | None = None,
) -> str:
    """
    Build the compact RX or TX opportunity query.

    The query deliberately uses the physical ``(band, time, id)`` table order
    in PREWHERE, reads only locator-level geometry, and avoids joins,
    geographic functions, arrays, and exact quantiles.
    """
    mode = str(mode).strip().upper()
    callsign = str(callsign or "").strip().upper()
    if mode not in {"RX", "TX"}:
        raise ValueError("mode must be RX or TX.")
    if not is_valid_callsign(callsign):
        raise ValueError("Absolute opportunity analysis requires a valid exact target callsign.")
    if not str(band_value or "").strip():
        raise ValueError("Absolute opportunity analysis requires one exact operating band.")

    grid4 = target_grid4(qth)
    start_sql = start_t.strftime("%Y-%m-%d %H:%M:%S")
    end_sql = end_t.strftime("%Y-%m-%d %H:%M:%S")
    call_sql = _sql_literal(callsign)
    grid_sql = _sql_literal(grid4)
    band_sql = int(band_value)

    if mode == "RX":
        target_condition = (
            f"rx_sign = {call_sql} AND substring(rx_loc, 1, 4) = {grid_sql}"
        )
        external_condition = f"rx_sign != {call_sql}"
        peer_sign = "tx_sign"
        peer_grid = "tx_loc"
    else:
        target_condition = (
            f"tx_sign = {call_sql} AND substring(tx_loc, 1, 4) = {grid_sql}"
        )
        external_condition = f"tx_sign != {call_sql}"
        peer_sign = "rx_sign"
        peer_grid = "rx_loc"

    peer_exclusions = ""
    if exclude_special_callsigns:
        peer_exclusions = " " + " ".join(
            f"AND {peer_sign} NOT LIKE '{prefix}%'" for prefix in ("Q", "0", "1")
        )
    frame_filter = ""
    if target_frame_mod4 in {0, 2}:
        frame_filter = f"\n      AND toMinute(time) % 4 = {int(target_frame_mod4)}"

    return f"""
WITH active_cycles AS
(
    SELECT DISTINCT intDiv(toUnixTimestamp(time), 120) AS cycle
    FROM wspr.rx
    PREWHERE band = {band_sql}
      AND time >= '{start_sql}'
      AND time < '{end_sql}'
    WHERE code = 1
      AND {target_condition}
      {frame_filter}
)
SELECT
    intDiv(toUnixTimestamp(time), 120) AS time_slot,
    {peer_sign} AS peer_sign,
    {peer_grid} AS peer_grid,
    max(toUInt8({target_condition})) AS target_seen,
    max(toUInt8({external_condition})) AS external_seen,
    if(
        countIf({target_condition}) > 0,
        toNullable(maxIf(toInt16(snr) - toInt16(power) + 30, {target_condition})),
        CAST(NULL, 'Nullable(Int16)')
    ) AS target_snr
FROM wspr.rx
PREWHERE band = {band_sql}
  AND time >= '{start_sql}'
  AND time < '{end_sql}'
WHERE code = 1
  AND ({target_condition} OR {external_condition})
  AND notEmpty({peer_sign})
  AND notEmpty({peer_grid})
  AND intDiv(toUnixTimestamp(time), 120) IN (SELECT cycle FROM active_cycles)
  {peer_exclusions}
GROUP BY time_slot, peer_sign, peer_grid
FORMAT Parquet
""".strip()


def _locator_coordinates(locators: pd.Series) -> pd.DataFrame:
    """Resolve unique Maidenhead locators to their cell-centre coordinates."""
    rows = []
    for locator in pd.Series(locators, dtype="string").dropna().drop_duplicates():
        locator = str(locator).strip().upper()
        if not _is_valid_maidenhead(locator):
            continue
        lat, lon = locator_to_latlon(locator)
        rows.append((locator, float(lat), float(lon)))
    return pd.DataFrame(rows, columns=["peer_grid", "peer_lat", "peer_lon"])


def prepare_opportunity_rows(
    df: pd.DataFrame,
    *,
    target_callsign: str,
    target_qth: str,
) -> pd.DataFrame:
    """
    Normalize server evidence and classify every peer-cycle as H, M, or T.

    ``opportunity`` is independently confirmed evidence. ``target_only`` is
    retained separately and never contributes to the denominator.
    """
    required = {
        "time_slot",
        "peer_sign",
        "peer_grid",
        "target_seen",
        "external_seen",
        "target_snr",
    }
    if df is None or df.empty:
        return pd.DataFrame(columns=sorted(required))
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Opportunity result is missing columns: {', '.join(sorted(missing))}")

    work = df.copy()
    work["peer_sign"] = work["peer_sign"].astype(str).str.strip().str.upper()
    work["peer_grid"] = work["peer_grid"].astype(str).str.strip().str.upper()
    for column in ["time_slot", "target_seen", "external_seen", "target_snr"]:
        work[column] = pd.to_numeric(work[column], errors="coerce")
    work = work.dropna(subset=["time_slot", "peer_sign", "peer_grid"])
    work = work[work["peer_sign"].ne("") & work["peer_grid"].ne("")].copy()
    work["time_slot"] = work["time_slot"].astype("int64")
    work["target_seen"] = (work["target_seen"].fillna(0) > 0).astype("int8")
    work["external_seen"] = (work["external_seen"].fillna(0) > 0).astype("int8")

    target_call = str(target_callsign or "").strip().upper()
    _ = target_grid4(target_qth)
    is_target_identity = work["peer_sign"].eq(target_call)
    work = work[~is_target_identity].copy()

    coordinates = _locator_coordinates(work["peer_grid"])
    work = work.merge(coordinates, on="peer_grid", how="inner")
    if work.empty:
        return work

    work["cycle_time"] = pd.to_datetime(
        work["time_slot"] * 120,
        unit="s",
        utc=True,
        errors="coerce",
    )
    work["opportunity"] = work["external_seen"].astype("int8")
    work["hit"] = (
        (work["target_seen"] == 1) & (work["external_seen"] == 1)
    ).astype("int8")
    work["miss"] = (
        (work["target_seen"] == 0) & (work["external_seen"] == 1)
    ).astype("int8")
    work["target_only"] = (
        (work["target_seen"] == 1) & (work["external_seen"] == 0)
    ).astype("int8")
    work["outcome"] = np.select(
        [work["hit"] == 1, work["miss"] == 1, work["target_only"] == 1],
        ["H", "M", "T"],
        default="",
    )
    work["target_snr"] = pd.to_numeric(work["target_snr"], errors="coerce").round(1)
    return work.reset_index(drop=True)


def aggregate_opportunity_peers(
    rows: pd.DataFrame,
    *,
    min_opportunities: int,
) -> pd.DataFrame:
    """Aggregate peer-cycle evidence into auditable peer-level O/H/M/T rates."""
    if rows is None or rows.empty:
        return pd.DataFrame()

    min_opportunities = max(int(min_opportunities), 1)
    grouped = (
        rows.groupby(["peer_sign", "peer_grid"], dropna=False)
        .agg(
            opportunities=("opportunity", "sum"),
            hits=("hit", "sum"),
            misses=("miss", "sum"),
            target_only=("target_only", "sum"),
            target_observations=("target_seen", "sum"),
            successful_snr_median=("target_snr", "median"),
            first_evidence_utc=("cycle_time", "min"),
            last_evidence_utc=("cycle_time", "max"),
            peer_lat=("peer_lat", "first"),
            peer_lon=("peer_lon", "first"),
        )
        .reset_index()
    )
    for column in [
        "opportunities",
        "hits",
        "misses",
        "target_only",
        "target_observations",
    ]:
        grouped[column] = grouped[column].astype("int64")

    grouped["eligible"] = grouped["opportunities"] >= min_opportunities
    grouped["rate_pct"] = np.where(
        grouped["opportunities"] > 0,
        100.0 * grouped["hits"] / grouped["opportunities"],
        np.nan,
    )
    grouped["rate_pct"] = grouped["rate_pct"].round(1)
    grouped["stat_val"] = grouped["rate_pct"].where(grouped["eligible"])
    grouped["spot_count"] = grouped["opportunities"]
    grouped["successful_snr_median"] = grouped["successful_snr_median"].round(1)
    return grouped


def aggregate_opportunity_segments(peer_df: pd.DataFrame) -> pd.DataFrame:
    """Return station-balanced and pooled opportunity statistics per map segment."""
    if peer_df is None or peer_df.empty:
        return pd.DataFrame()

    group_keys = [
        "SegmentID",
        "dist_label",
        "dir_name",
        "r_min",
        "r_max",
        "az_bucket",
    ]
    eligible = peer_df[peer_df["eligible"] & peer_df["rate_pct"].notna()].copy()
    if eligible.empty:
        return pd.DataFrame(columns=group_keys)

    segments = (
        eligible.groupby(group_keys, dropna=False)
        .agg(
            val=("rate_pct", "median"),
            cnt=("peer_sign", "size"),
            total_opportunities=("opportunities", "sum"),
            total_hits=("hits", "sum"),
            total_misses=("misses", "sum"),
            total_target_only=("target_only", "sum"),
        )
        .reset_index()
    )
    segments["pooled_rate_pct"] = np.where(
        segments["total_opportunities"] > 0,
        100.0 * segments["total_hits"] / segments["total_opportunities"],
        np.nan,
    )
    segments["val"] = segments["val"].round(1)
    segments["pooled_rate_pct"] = segments["pooled_rate_pct"].round(1)
    return segments
