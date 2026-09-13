"""Conservative neighborhood bounds and vectorized scientific peer-scope filtering."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from config import DIST_BINS, EARTH_RADIUS_KM, MAX_DYNAMIC_RADIUS_KM


MAX_SUPPORTED_PEER_DISTANCE_KM = float(max(DIST_BINS))
MAXIMUM_GREAT_CIRCLE_DISTANCE_KM = math.pi * EARTH_RADIUS_KM

# Below the minimum WGS-84 curvature radius (6335.439 km), with additional
# slack for ClickHouse geoDistance's numerical approximations. This radius
# enlarges only the prefilter; geoDistance still applies the requested cutoff.
NEIGHBORHOOD_BOUNDING_EARTH_RADIUS_KM = 6300.0


@dataclass(frozen=True)
class GeographicBoundingBox:
    """Inclusive latitude/longitude bounds in degrees; no ranges means all longitudes."""

    minimum_latitude: float
    maximum_latitude: float
    longitude_ranges: tuple[tuple[float, float], ...]

    def to_sql(self, latitude_column: str, longitude_column: str) -> str:
        """Return a SQL condition for one trusted archive endpoint column pair.

        Wrapped longitude ranges are grouped so surrounding AND predicates
        apply to both sides of the date line. Reject other SQL identifiers.
        """
        if (latitude_column, longitude_column) not in {
            ("tx_lat", "tx_lon"), ("rx_lat", "rx_lon")
        }:
            raise ValueError("Neighborhood bounds require matching TX or RX coordinate columns.")
        latitude_sql = (
            f"{latitude_column} BETWEEN {self.minimum_latitude} "
            f"AND {self.maximum_latitude}"
        )
        if not self.longitude_ranges:
            return latitude_sql
        longitude_sql = " OR ".join(
            f"{longitude_column} BETWEEN {minimum_longitude} AND {maximum_longitude}"
            for minimum_longitude, maximum_longitude in self.longitude_ranges
        )
        return f"{latitude_sql} AND ({longitude_sql})"


def build_neighborhood_bounding_box(
    *,
    center_latitude: float,
    center_longitude: float,
    radius_km: float,
) -> GeographicBoundingBox:
    """Enclose a local distance circle with cheap, conservative geographic bounds.

    Accept finite coordinates in degrees and a positive radius up to the
    supported neighborhood maximum. Invalid inputs raise ValueError. Compute
    a spherical cap using a deliberately small Earth radius to enclose the
    WGS-84 neighborhood, including high-latitude longitude extrema. Pole-reaching
    caps require every longitude; other caps use one or two inclusive ranges.
    These bounds are only a prefilter for the existing geoDistance predicate.
    """
    normalized_parameters = []
    for parameter, field_name, absolute_limit in (
        (center_latitude, "Neighborhood center latitude", 90.0),
        (center_longitude, "Neighborhood center longitude", 180.0),
        (radius_km, "Neighborhood radius", float(MAX_DYNAMIC_RADIUS_KM)),
    ):
        if isinstance(parameter, (bool, np.bool_)):
            raise ValueError(f"{field_name} must be a finite number.")
        try:
            normalized_parameter = float(parameter)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{field_name} must be a finite number.") from exc
        if not math.isfinite(normalized_parameter) or abs(normalized_parameter) > absolute_limit:
            raise ValueError(f"{field_name} must be finite and within +/-{absolute_limit:g}.")
        normalized_parameters.append(normalized_parameter)
    latitude_degrees, longitude_degrees, normalized_radius_km = normalized_parameters
    if normalized_radius_km <= 0.0:
        raise ValueError("Neighborhood radius must be greater than 0 km.")

    angular_radius = normalized_radius_km / NEIGHBORHOOD_BOUNDING_EARTH_RADIUS_KM
    latitude_half_width = math.degrees(angular_radius)
    minimum_latitude = max(-90.0, latitude_degrees - latitude_half_width)
    maximum_latitude = min(90.0, latitude_degrees + latitude_half_width)
    if minimum_latitude <= -90.0 or maximum_latitude >= 90.0:
        return GeographicBoundingBox(minimum_latitude, maximum_latitude, ())

    longitude_half_width = math.degrees(math.asin(min(
        1.0, math.sin(angular_radius) / math.cos(math.radians(latitude_degrees))
    )))
    minimum_longitude = longitude_degrees - longitude_half_width
    maximum_longitude = longitude_degrees + longitude_half_width
    # Include both representations of the date line even when a bound only
    # touches +/-180 rather than crossing it.
    if minimum_longitude <= -180.0:
        longitude_ranges = (
            (-180.0, maximum_longitude), (minimum_longitude + 360.0, 180.0)
        )
    elif maximum_longitude >= 180.0:
        longitude_ranges = (
            (minimum_longitude, 180.0), (-180.0, maximum_longitude - 360.0)
        )
    else:
        longitude_ranges = ((minimum_longitude, maximum_longitude),)
    return GeographicBoundingBox(minimum_latitude, maximum_latitude, longitude_ranges)


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
