"""Pure geographic bucketing and aggregation for map presentation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import AZIMUTH_STEP, COMPASS, DIST_BINS
from core.compare_engine import aggregate_compare_map_data
from core.geographic_scope import great_circle_distances_km
from core.map_models import MapData
from core.opportunity_engine import aggregate_opportunity_peers, aggregate_opportunity_segments


def validate_map_analysis_mode(*, analysis_kind: str, is_compare: bool) -> bool:
    """Validate the two supported map modes and return whether this is Success.

    Success maps use ``analysis_kind="opportunity"`` with ``is_compare=False``.
    Compare maps use ``analysis_kind="comparison"`` with ``is_compare=True``.
    Any other combination is outside the analysis-batch contract.
    """
    normalized_kind = str(analysis_kind)
    compare_enabled = bool(is_compare)
    if normalized_kind == "opportunity" and not compare_enabled:
        return True
    if normalized_kind == "comparison" and compare_enabled:
        return False
    raise ValueError(
        "Map analysis mode must be Success "
        "(analysis_kind='opportunity', is_compare=False) or Compare "
        "(analysis_kind='comparison', is_compare=True)."
    )


def _attach_map_geometry(frame: pd.DataFrame, *, center_latitude: float, center_longitude: float) -> None:
    """Attach distance, bearing, and stable segment keys to an owned frame."""
    frame["calc_dist"] = great_circle_distances_km(
        center_latitude=center_latitude,
        center_longitude=center_longitude,
        peer_latitudes=frame["peer_lat"],
        peer_longitudes=frame["peer_lon"],
    )

    lat_1, lon_1, lat_2, lon_2 = map(
        np.radians,
        [center_latitude, center_longitude, frame["peer_lat"], frame["peer_lon"]],
    )
    bearing_y = np.sin(lon_2 - lon_1) * np.cos(lat_2)
    bearing_x = (
        np.cos(lat_1) * np.sin(lat_2)
        - np.sin(lat_1) * np.cos(lat_2) * np.cos(lon_2 - lon_1)
    )
    frame["calc_azimuth"] = (np.degrees(np.arctan2(bearing_y, bearing_x)) + 360) % 360
    frame["az_bucket"] = (
        ((frame["calc_azimuth"] + (AZIMUTH_STEP / 2.0)) % 360) // AZIMUTH_STEP
    )
    frame["dir_name"] = frame["az_bucket"].apply(
        lambda value: COMPASS[int(value)] if pd.notnull(value) else ""
    )
    frame["r_min"] = pd.cut(
        frame["calc_dist"],
        bins=DIST_BINS,
        labels=DIST_BINS[:-1],
        right=False,
    ).astype(float)
    frame["r_max"] = pd.cut(
        frame["calc_dist"],
        bins=DIST_BINS,
        labels=DIST_BINS[1:],
        right=False,
    ).astype(float)
    frame["dist_label"] = frame.apply(
        lambda row: (
            f"[{int(row['r_min'])}-{int(row['r_max'])}km]"
            if pd.notnull(row["r_min"])
            else ""
        ),
        axis=1,
    )
    frame["SegmentID"] = frame.apply(
        lambda row: (
            f"{row['dist_label']} {row['dir_name']}"
            if pd.notnull(row["r_min"])
            else "Out of Bounds"
        ),
        axis=1,
    )


def build_map_data(
    frame: pd.DataFrame,
    *,
    analysis_id: str,
    is_compare: bool,
    is_sequential: bool,
    analysis_kind: str,
    center_latitude: float,
    center_longitude: float,
    min_spots: int,
    min_opportunities: int,
    base_min_stations: int,
    tx_ab_repeat_interval_minutes: int,
    tx_ab_target_start_minute: int,
    tx_ab_reference_start_minute: int,
    owns_input: bool = False,
) -> MapData | None:
    """Return language-free Success or Compare aggregates for one map."""
    is_opportunity = validate_map_analysis_mode(
        analysis_kind=analysis_kind,
        is_compare=is_compare,
    )
    if frame is None or frame.empty:
        return None

    work = frame if owns_input else frame.copy()
    if is_opportunity:
        work = aggregate_opportunity_peers(
            work,
            min_opportunities=int(min_opportunities),
        )
        if work.empty:
            return None

    _attach_map_geometry(
        work,
        center_latitude=center_latitude,
        center_longitude=center_longitude,
    )

    if is_opportunity:
        station_rows = work.copy()
        segment_rows = aggregate_opportunity_segments(station_rows)
        if not segment_rows.empty:
            segment_rows = segment_rows[
                segment_rows["cnt"] >= int(base_min_stations)
            ]
    else:
        station_rows, segment_rows = aggregate_compare_map_data(
            work,
            is_sequential=is_sequential,
            min_spots=int(min_spots),
            base_min_stations=int(base_min_stations),
            tx_ab_repeat_interval_minutes=int(tx_ab_repeat_interval_minutes),
            tx_ab_target_start_minute=int(tx_ab_target_start_minute),
            tx_ab_reference_start_minute=int(tx_ab_reference_start_minute),
        )

    if station_rows.empty or (segment_rows.empty and not is_opportunity):
        return None
    return MapData(
        station_rows=station_rows,
        segment_rows=segment_rows,
        analysis_id=str(analysis_id),
        is_compare=bool(is_compare),
        is_sequential=bool(is_sequential),
        analysis_kind=str(analysis_kind),
    )
