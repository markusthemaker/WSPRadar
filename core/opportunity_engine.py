"""
Opportunity-based Absolute analysis for WSPRadar.

The server query returns one row per UTC WSPR cycle and remote
callsign/locator identity. All scientific classification and peer-balanced
aggregation is then performed locally from that compact evidence table.
"""

from __future__ import annotations

from datetime import datetime
from contextlib import nullcontext

import numpy as np
import pandas as pd

from config import (
    ABS_PATH_DAYLIGHT_FRACTION_THRESHOLD,
    ABS_PATH_SAMPLE_POINTS,
    ABS_PATH_TWILIGHT_ELEVATION_DEG,
)
from core.input_validation import is_valid_6char_locator, is_valid_callsign
from core.math_utils import locator_to_latlon
from core.solar_path import classify_path_illumination
from core.tx_ab_schedule import tx_ab_schedule_sql


ABSOLUTE_METHOD_VERSION = "opportunity-v1"
DEFAULT_MIN_OPPORTUNITIES = 5
OPPORTUNITY_SLOT_SECONDS = 120
OPPORTUNITY_OUTCOME_CATEGORIES = ("H", "M", "T", "")
OPPORTUNITY_QUERY_COLUMNS = (
    "time_slot",
    "peer_sign",
    "peer_grid",
    "target_seen",
    "external_seen",
    "target_snr",
)
PROCESSED_OPPORTUNITY_SCHEMA = {
    "time_slot": "int64",
    "peer_sign": "category",
    "peer_grid": "category",
    "target_seen": "int8",
    "external_seen": "int8",
    "target_snr": "float64",
    "peer_lat": "float64",
    "peer_lon": "float64",
    "opportunity": "int8",
    "hit": "int8",
    "miss": "int8",
    "target_only": "int8",
    "outcome": "category",
    "path_daylight_fraction": "float32",
    "target_solar_elevation": "float32",
    "path_midpoint_solar_elevation": "float32",
    "peer_solar_elevation": "float32",
    "path_greyline_crossing": "int8",
    "path_illumination": "category",
}
PROCESSED_OPPORTUNITY_COLUMNS = tuple(PROCESSED_OPPORTUNITY_SCHEMA.keys())
OPPORTUNITY_SEGMENT_VIEW_COLUMNS = (
    "time_slot",
    "peer_sign",
    "peer_grid",
    "hit",
    "miss",
)
OPPORTUNITY_DRILLDOWN_VIEW_COLUMNS = (
    "time_slot",
    "peer_sign",
    "peer_grid",
    "hit",
    "miss",
    "target_only",
    "target_snr",
    "path_illumination",
)
OPPORTUNITY_MAP_EXPORT_COLUMNS = (
    "time_slot",
    "peer_sign",
    "peer_grid",
    "target_seen",
    "target_snr",
    "peer_lat",
    "peer_lon",
    "opportunity",
    "hit",
    "miss",
    "target_only",
)
SUCCESS_RATE_EPSILON = 1e-12
SUCCESS_RATE_BOUNDS = (
    0.0,
    SUCCESS_RATE_EPSILON,
    1.0,
    2.0,
    5.0,
    10.0,
    20.0,
    40.0,
    60.0,
    80.0,
    100.0,
)
SUCCESS_RATE_TICK_LABELS = ("0%", ">0%", "1%", "2%", "5%", "10%", "20%", "40%", "60%", "80%", "100%")
SUCCESS_RATE_COLORS = (
    "#3b0f70",
    "#364b9a",
    "#277f8e",
    "#1fa187",
    "#4ac16d",
    "#a0da39",
    "#fde725",
    "#f89540",
    "#d73027",
    "#a50026",
)


def _timed_span(timing_collector, label, detail=""):
    """Return a timing context when profiling is active."""
    if timing_collector is None:
        return nullcontext()
    return timing_collector.span(label, detail=detail)


def opportunity_utc_from_time_slot(time_slot):
    """Return timezone-aware UTC WSPR-frame timestamps from integer time slots."""
    numeric = pd.to_numeric(time_slot, errors="coerce")
    return pd.to_datetime(
        numeric * OPPORTUNITY_SLOT_SECONDS,
        unit="s",
        utc=True,
        errors="coerce",
    )


def _empty_processed_opportunity_rows() -> pd.DataFrame:
    """Return an empty processed opportunity frame with the canonical schema."""
    columns = {}
    for column, dtype in PROCESSED_OPPORTUNITY_SCHEMA.items():
        if column == "outcome":
            columns[column] = pd.Categorical([], categories=OPPORTUNITY_OUTCOME_CATEGORIES)
        elif dtype == "category":
            columns[column] = pd.Categorical([])
        else:
            columns[column] = pd.Series(dtype=dtype)
    return pd.DataFrame(columns)


def _apply_processed_opportunity_schema(frame: pd.DataFrame) -> pd.DataFrame:
    """Order and type processed opportunity rows for stable cache/read behavior."""
    if frame is None or frame.empty:
        return _empty_processed_opportunity_rows()

    work = frame.loc[:, PROCESSED_OPPORTUNITY_COLUMNS]
    work["time_slot"] = pd.to_numeric(work["time_slot"], errors="coerce").astype("int64")
    for column in ["target_seen", "external_seen", "opportunity", "hit", "miss", "target_only", "path_greyline_crossing"]:
        work[column] = pd.to_numeric(work[column], errors="coerce").fillna(0).astype("int8")
    for column in ["target_snr", "peer_lat", "peer_lon"]:
        work[column] = pd.to_numeric(work[column], errors="coerce").astype("float64")
    for column in [
        "path_daylight_fraction",
        "target_solar_elevation",
        "path_midpoint_solar_elevation",
        "peer_solar_elevation",
    ]:
        work[column] = pd.to_numeric(work[column], errors="coerce").astype("float32")
    work["peer_sign"] = work["peer_sign"].astype("category")
    work["peer_grid"] = work["peer_grid"].astype("category")
    work["outcome"] = pd.Categorical(
        work["outcome"].astype(str),
        categories=OPPORTUNITY_OUTCOME_CATEGORIES,
    )
    if not isinstance(work["path_illumination"].dtype, pd.CategoricalDtype):
        work["path_illumination"] = work["path_illumination"].astype("category")
    return work


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
    """Return the configured grid-4 shared by Success and Compare Target matching."""
    qth = str(qth or "").strip().upper()
    if not _is_valid_maidenhead(qth):
        raise ValueError("Analysis requires a valid target QTH locator.")
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
    target_repeat_interval_minutes: int | None = None,
    target_start_minute_utc: int | None = None,
    require_decode_code: bool = True,
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
    schedule_filter = ""
    has_repeat_interval = target_repeat_interval_minutes is not None
    has_start_minute = target_start_minute_utc is not None
    if has_repeat_interval != has_start_minute:
        raise ValueError(
            "Target schedule requires both repeat interval and UTC start minute."
        )
    if has_repeat_interval:
        schedule_filter = "\n      AND " + tx_ab_schedule_sql(
            target_repeat_interval_minutes,
            target_start_minute_utc,
        )
    active_decode_filter = "\n      AND code = 1" if require_decode_code else ""
    main_decode_filter = "\n  AND code = 1" if require_decode_code else ""

    return f"""
WITH active_cycles AS
(
    SELECT DISTINCT intDiv(toUnixTimestamp(time), 120) AS cycle
    FROM wspr.rx
    PREWHERE band = {band_sql}
      AND time >= '{start_sql}'
      AND time < '{end_sql}'
    WHERE {target_condition}{active_decode_filter}{schedule_filter}
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
WHERE ({target_condition} OR {external_condition}){main_decode_filter}
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
    timing_collector=None,
    owns_input: bool = False,
) -> pd.DataFrame:
    """
    Normalize server evidence and classify every peer-cycle as H, M, or T.

    ``opportunity`` is independently confirmed evidence. ``target_only`` is
    retained separately and never contributes to the denominator.
    """
    required = set(OPPORTUNITY_QUERY_COLUMNS)
    if df is None or df.empty:
        return _empty_processed_opportunity_rows()
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Opportunity result is missing columns: {', '.join(sorted(missing))}")

    with _timed_span(timing_collector, "opportunity normalize rows"):
        work = df if owns_input else df.copy()
        work["peer_sign"] = work["peer_sign"].astype(str).str.strip().str.upper()
        work["peer_grid"] = work["peer_grid"].astype(str).str.strip().str.upper()
        for column in ["time_slot", "target_seen", "external_seen", "target_snr"]:
            work[column] = pd.to_numeric(work[column], errors="coerce")
        valid_identity = (
            work["time_slot"].notna()
            & work["peer_sign"].ne("")
            & work["peer_grid"].ne("")
        )
        if not bool(valid_identity.all()):
            work = work.loc[valid_identity].copy()
        if work.empty:
            return _empty_processed_opportunity_rows()
        work["time_slot"] = work["time_slot"].astype("int64")
        work["target_seen"] = (work["target_seen"].fillna(0) > 0).astype("int8")
        work["external_seen"] = (work["external_seen"].fillna(0) > 0).astype("int8")

    with _timed_span(timing_collector, "opportunity target identity filter"):
        target_call = str(target_callsign or "").strip().upper()
        _ = target_grid4(target_qth)
        target_latitude, target_longitude = locator_to_latlon(target_qth)
        is_target_identity = work["peer_sign"].eq(target_call)
        if bool(is_target_identity.any()):
            work = work.loc[~is_target_identity].copy()
        if work.empty:
            return _empty_processed_opportunity_rows()

    with _timed_span(timing_collector, "opportunity locator coordinate resolution"):
        coordinates = _locator_coordinates(work["peer_grid"])
    if coordinates.empty:
        return _empty_processed_opportunity_rows()

    with _timed_span(timing_collector, "opportunity coordinate assignment"):
        coordinate_lookup = coordinates.set_index("peer_grid")
        work["peer_lat"] = work["peer_grid"].map(coordinate_lookup["peer_lat"])
        work["peer_lon"] = work["peer_grid"].map(coordinate_lookup["peer_lon"])
        valid_coordinates = work["peer_lat"].notna() & work["peer_lon"].notna()
        if not bool(valid_coordinates.all()):
            work = work.loc[valid_coordinates].copy()
    if work.empty:
        return _empty_processed_opportunity_rows()

    with _timed_span(timing_collector, "opportunity outcome columns"):
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

    with _timed_span(timing_collector, "opportunity path illumination"):
        work = classify_path_illumination(
            work,
            target_latitude=target_latitude,
            target_longitude=target_longitude,
            daylight_fraction_threshold=ABS_PATH_DAYLIGHT_FRACTION_THRESHOLD,
            twilight_elevation_degrees=ABS_PATH_TWILIGHT_ELEVATION_DEG,
            sample_points=ABS_PATH_SAMPLE_POINTS,
            time_values=opportunity_utc_from_time_slot(work["time_slot"]),
            copy=False,
            timing_collector=timing_collector,
        )

    with _timed_span(timing_collector, "opportunity final reset"):
        return _apply_processed_opportunity_schema(work.reset_index(drop=True))


def aggregate_opportunity_peers(
    rows: pd.DataFrame,
    *,
    min_opportunities: int,
) -> pd.DataFrame:
    """Aggregate peer-cycle evidence into auditable peer-level O/H/M/T rates."""
    if rows is None or rows.empty:
        return pd.DataFrame()

    min_opportunities = max(int(min_opportunities), 1)
    work = rows.copy()
    work["hit_snr"] = pd.to_numeric(work["target_snr"], errors="coerce").where(
        work["hit"] > 0
    )
    work["evidence_utc"] = opportunity_utc_from_time_slot(work["time_slot"])
    grouped = (
        work.groupby(["peer_sign", "peer_grid"], dropna=False, observed=True)
        .agg(
            opportunities=("opportunity", "sum"),
            hits=("hit", "sum"),
            misses=("miss", "sum"),
            target_only=("target_only", "sum"),
            target_observations=("target_seen", "sum"),
            successful_snr_median=("hit_snr", "median"),
            first_evidence_utc=("evidence_utc", "min"),
            last_evidence_utc=("evidence_utc", "max"),
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
    """Return average-station and overall success rates per map segment."""
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
    eligible["station_success_rate_pct"] = np.where(
        (eligible["hits"] + eligible["misses"]) > 0,
        100.0 * eligible["hits"] / (eligible["hits"] + eligible["misses"]),
        np.nan,
    )

    segments = (
        eligible.groupby(group_keys, dropna=False, observed=True)
        .agg(
            val=("station_success_rate_pct", "mean"),
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


def opportunity_footer_counts(
    peer_df: pd.DataFrame,
    *,
    max_dist_km: float,
) -> dict[str, int]:
    """Return visible qualified station and denominator-evidence counts for Success maps.

    Target counts are successful independently confirmed observations (hits), while
    counter counts are misses confirmed by Elsewhere evidence in RX or Other Signals
    in TX. Stations are assigned to Target when they have at least one hit and to
    counter-only otherwise. Ineligible identities, out-of-scope identities, and
    Target-only observations are excluded because they do not enter Success Rate.
    """
    if peer_df is None or peer_df.empty:
        return {
            "stat_target": 0,
            "stat_counter_only": 0,
            "spot_target": 0,
            "spot_counter": 0,
            "tot_stats": 0,
            "tot_spots": 0,
        }

    visible_eligible = peer_df[
        (peer_df["r_min"] < float(max_dist_km))
        & peer_df["eligible"]
        & peer_df["rate_pct"].notna()
    ]
    stat_target = int((visible_eligible["hits"] > 0).sum())
    stat_counter_only = int((visible_eligible["hits"] == 0).sum())
    spot_target = int(visible_eligible["hits"].sum())
    spot_counter = int(visible_eligible["misses"].sum())

    return {
        "stat_target": stat_target,
        "stat_counter_only": stat_counter_only,
        "spot_target": spot_target,
        "spot_counter": spot_counter,
        "tot_stats": int(stat_target + stat_counter_only),
        "tot_spots": int(spot_target + spot_counter),
    }
