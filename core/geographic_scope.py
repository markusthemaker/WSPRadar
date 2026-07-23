"""Vectorized geographic distance and scientific peer-scope filtering."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from config import DIST_BINS, EARTH_RADIUS_KM


MAX_SUPPORTED_PEER_DISTANCE_KM = float(max(DIST_BINS))
MAXIMUM_GREAT_CIRCLE_DISTANCE_KM = math.pi * EARTH_RADIUS_KM


def validate_max_peer_distance_km(max_peer_distance_km: float) -> float:
    """Return a finite supported peer-distance limit in kilometres.

    The UI currently supplies integer map-ring boundaries, but this core
    boundary accepts intermediate positive distances so callers and tests can
    express the exact half-open cutoff without relying on widget validation.
    """
    if isinstance(max_peer_distance_km, (bool, np.bool_)):
        raise ValueError("Maximum peer distance must be a number of kilometres.")
    try:
        normalized_distance_km = float(max_peer_distance_km)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Maximum peer distance must be a number of kilometres."
        ) from exc
    if (
        not math.isfinite(normalized_distance_km)
        or normalized_distance_km <= 0.0
        or normalized_distance_km > MAX_SUPPORTED_PEER_DISTANCE_KM
    ):
        raise ValueError(
            "Maximum peer distance must be greater than 0 km and no greater "
            f"than {MAX_SUPPORTED_PEER_DISTANCE_KM:g} km."
        )
    return normalized_distance_km


def great_circle_distances_km(
    *,
    center_latitude: float,
    center_longitude: float,
    peer_latitudes,
    peer_longitudes,
) -> np.ndarray:
    """Return spherical great-circle distances from one QTH to peer coordinates.

    Inputs are interpreted as decimal degrees. The calculation is fully
    vectorized, returns float64 kilometres, and reuses temporary arrays to keep
    peak working memory linear and bounded for large evidence frames.
    """
    peer_latitude_values = np.asarray(peer_latitudes, dtype=np.float64)
    peer_longitude_values = np.asarray(peer_longitudes, dtype=np.float64)
    if peer_latitude_values.shape != peer_longitude_values.shape:
        raise ValueError("Peer latitude and longitude arrays must have equal shapes.")

    center_latitude_radians = math.radians(float(center_latitude))
    center_longitude_radians = math.radians(float(center_longitude))
    peer_latitude_radians = np.deg2rad(peer_latitude_values)
    longitude_term = np.deg2rad(peer_longitude_values)

    latitude_term = peer_latitude_radians.copy()
    latitude_term -= center_latitude_radians
    latitude_term *= 0.5
    np.sin(latitude_term, out=latitude_term)
    np.square(latitude_term, out=latitude_term)

    longitude_term -= center_longitude_radians
    longitude_term *= 0.5
    np.sin(longitude_term, out=longitude_term)
    np.square(longitude_term, out=longitude_term)
    np.cos(peer_latitude_radians, out=peer_latitude_radians)
    longitude_term *= peer_latitude_radians
    longitude_term *= math.cos(center_latitude_radians)
    latitude_term += longitude_term

    # Floating-point roundoff can otherwise place an antipodal result just
    # outside the mathematical asin domain.
    np.clip(latitude_term, 0.0, 1.0, out=latitude_term)
    np.sqrt(latitude_term, out=latitude_term)
    np.arcsin(latitude_term, out=latitude_term)
    latitude_term *= 2.0 * EARTH_RADIUS_KM
    return latitude_term


def filter_peer_rows_by_distance(
    frame: pd.DataFrame,
    *,
    center_latitude: float,
    center_longitude: float,
    max_peer_distance_km: float,
) -> pd.DataFrame:
    """Return only mapped peer rows strictly inside the configured radius.

    A limit covering the Earth's maximum great-circle distance is a deliberate
    zero-work fast path: the owned input frame is returned unchanged. Narrower
    limits require ``peer_lat`` and ``peer_lon`` and use one vectorized distance
    pass. If every row is already in scope, the original frame is likewise
    returned to avoid an unnecessary full-frame copy.
    """
    normalized_distance_km = validate_max_peer_distance_km(
        max_peer_distance_km
    )
    if frame is None or frame.empty:
        return frame
    if normalized_distance_km >= MAXIMUM_GREAT_CIRCLE_DISTANCE_KM:
        return frame

    required_columns = {"peer_lat", "peer_lon"}
    missing_columns = required_columns - set(frame.columns)
    if missing_columns:
        raise ValueError(
            "Geographic peer-scope filtering requires columns: "
            + ", ".join(sorted(missing_columns))
        )

    peer_distances_km = great_circle_distances_km(
        center_latitude=center_latitude,
        center_longitude=center_longitude,
        peer_latitudes=frame["peer_lat"],
        peer_longitudes=frame["peer_lon"],
    )
    is_in_scope = peer_distances_km < normalized_distance_km
    if bool(np.all(is_in_scope)):
        return frame
    return frame.loc[is_in_scope]
