"""Great-circle path illumination helpers for Absolute success evidence."""

from __future__ import annotations

import numpy as np
import pandas as pd

ILLUMINATION_NIGHT = "night"
ILLUMINATION_GREYLINE_MIXED = "greyline_mixed"
ILLUMINATION_DAYLIGHT = "daylight"
ILLUMINATION_CLASSES = (
    ILLUMINATION_NIGHT,
    ILLUMINATION_GREYLINE_MIXED,
    ILLUMINATION_DAYLIGHT,
)
ILLUMINATION_DISPLAY_LABELS = {
    ILLUMINATION_NIGHT: "night",
    ILLUMINATION_GREYLINE_MIXED: "greyline/mixed",
    ILLUMINATION_DAYLIGHT: "daylight",
}


def solar_elevation_degrees(times_utc, latitude_degrees, longitude_degrees):
    """Return approximate solar elevation in degrees for UTC times and positions."""
    times = pd.to_datetime(times_utc, utc=True, errors="coerce")
    if isinstance(times, pd.Timestamp):
        times = pd.DatetimeIndex([times])
    else:
        times = pd.DatetimeIndex(times)

    count = len(times)
    if count == 0:
        return np.asarray([], dtype=float)

    latitude = np.broadcast_to(np.asarray(latitude_degrees, dtype=float), count)
    longitude = np.broadcast_to(np.asarray(longitude_degrees, dtype=float), count)

    day_of_year = times.dayofyear.to_numpy(dtype=float)
    minutes_utc = (
        times.hour.to_numpy(dtype=float) * 60.0
        + times.minute.to_numpy(dtype=float)
        + times.second.to_numpy(dtype=float) / 60.0
        + times.microsecond.to_numpy(dtype=float) / 60_000_000.0
    )
    fractional_hour = minutes_utc / 60.0
    gamma = 2.0 * np.pi / 365.0 * (day_of_year - 1.0 + (fractional_hour - 12.0) / 24.0)

    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * np.cos(gamma)
        - 0.032077 * np.sin(gamma)
        - 0.014615 * np.cos(2.0 * gamma)
        - 0.040849 * np.sin(2.0 * gamma)
    )
    declination = (
        0.006918
        - 0.399912 * np.cos(gamma)
        + 0.070257 * np.sin(gamma)
        - 0.006758 * np.cos(2.0 * gamma)
        + 0.000907 * np.sin(2.0 * gamma)
        - 0.002697 * np.cos(3.0 * gamma)
        + 0.00148 * np.sin(3.0 * gamma)
    )

    true_solar_minutes = (minutes_utc + equation_of_time + 4.0 * longitude) % 1440.0
    hour_angle = np.radians(true_solar_minutes / 4.0 - 180.0)
    latitude_radians = np.radians(latitude)
    cos_zenith = (
        np.sin(latitude_radians) * np.sin(declination)
        + np.cos(latitude_radians) * np.cos(declination) * np.cos(hour_angle)
    )
    cos_zenith = np.clip(cos_zenith, -1.0, 1.0)
    return 90.0 - np.degrees(np.arccos(cos_zenith))


def _unit_vector(latitude_radians, longitude_radians):
    cos_latitude = np.cos(latitude_radians)
    return np.stack(
        [
            cos_latitude * np.cos(longitude_radians),
            cos_latitude * np.sin(longitude_radians),
            np.sin(latitude_radians),
        ],
        axis=0,
    )


def classify_path_illumination(
    frame: pd.DataFrame,
    *,
    target_latitude: float,
    target_longitude: float,
    daylight_fraction_threshold: float,
    twilight_elevation_degrees: float,
    sample_points: int,
    time_column: str = "cycle_time",
    peer_latitude_column: str = "peer_lat",
    peer_longitude_column: str = "peer_lon",
) -> pd.DataFrame:
    """Attach great-circle path illumination metrics to station-cycle rows."""
    if frame is None or frame.empty:
        return frame

    result = frame.copy()
    times = pd.to_datetime(result[time_column], utc=True, errors="coerce")
    peer_latitude = pd.to_numeric(result[peer_latitude_column], errors="coerce").to_numpy(dtype=float)
    peer_longitude = pd.to_numeric(result[peer_longitude_column], errors="coerce").to_numpy(dtype=float)
    valid = times.notna().to_numpy() & np.isfinite(peer_latitude) & np.isfinite(peer_longitude)
    count = len(result)

    daylight_fraction = np.full(count, np.nan, dtype="float32")
    target_elevation = np.full(count, np.nan, dtype="float32")
    midpoint_elevation = np.full(count, np.nan, dtype="float32")
    peer_elevation = np.full(count, np.nan, dtype="float32")
    greyline_crossing = np.zeros(count, dtype="int8")
    path_class = np.full(count, ILLUMINATION_GREYLINE_MIXED, dtype=object)

    if valid.any():
        valid_indices = np.flatnonzero(valid)
        valid_times = times.iloc[valid_indices]
        valid_peer_latitude = peer_latitude[valid_indices]
        valid_peer_longitude = peer_longitude[valid_indices]

        target_elevation[valid_indices] = solar_elevation_degrees(
            valid_times,
            target_latitude,
            target_longitude,
        ).astype("float32")
        peer_elevation[valid_indices] = solar_elevation_degrees(
            valid_times,
            valid_peer_latitude,
            valid_peer_longitude,
        ).astype("float32")

        sample_points = max(int(sample_points), 3)
        fractions = np.linspace(0.0, 1.0, sample_points)
        target_latitude_radians = np.radians(float(target_latitude))
        target_longitude_radians = np.radians(float(target_longitude))
        peer_latitude_radians = np.radians(valid_peer_latitude)
        peer_longitude_radians = np.radians(valid_peer_longitude)

        target_vector = _unit_vector(target_latitude_radians, target_longitude_radians).reshape(3, 1)
        peer_vector = _unit_vector(peer_latitude_radians, peer_longitude_radians)
        dot = np.clip(np.sum(target_vector * peer_vector, axis=0), -1.0, 1.0)
        omega = np.arccos(dot)
        sin_omega = np.sin(omega)
        same_point = np.abs(sin_omega) < 1e-12

        daylight_counts = np.zeros(len(valid_indices), dtype=float)
        twilight_counts = np.zeros(len(valid_indices), dtype=float)
        midpoint_sample_index = int(np.argmin(np.abs(fractions - 0.5)))
        midpoint_altitudes = None

        for sample_index, fraction in enumerate(fractions):
            weight_target = np.empty_like(omega)
            weight_peer = np.empty_like(omega)
            normal = ~same_point
            weight_target[normal] = np.sin((1.0 - fraction) * omega[normal]) / sin_omega[normal]
            weight_peer[normal] = np.sin(fraction * omega[normal]) / sin_omega[normal]
            weight_target[same_point] = 1.0 - fraction
            weight_peer[same_point] = fraction

            sample_vector = target_vector * weight_target + peer_vector * weight_peer
            sample_norm = np.linalg.norm(sample_vector, axis=0)
            sample_norm = np.where(sample_norm > 0.0, sample_norm, 1.0)
            sample_vector = sample_vector / sample_norm
            sample_latitude = np.degrees(np.arcsin(np.clip(sample_vector[2], -1.0, 1.0)))
            sample_longitude = np.degrees(np.arctan2(sample_vector[1], sample_vector[0]))
            sample_altitude = solar_elevation_degrees(valid_times, sample_latitude, sample_longitude)

            daylight_counts += sample_altitude > 0.0
            twilight_counts += np.abs(sample_altitude) <= float(twilight_elevation_degrees)
            if sample_index == midpoint_sample_index:
                midpoint_altitudes = sample_altitude

        valid_daylight_fraction = daylight_counts / float(sample_points)
        valid_twilight_fraction = twilight_counts / float(sample_points)
        daylight_fraction[valid_indices] = valid_daylight_fraction.astype("float32")
        if midpoint_altitudes is not None:
            midpoint_elevation[valid_indices] = midpoint_altitudes.astype("float32")

        threshold = min(max(float(daylight_fraction_threshold), 0.5), 1.0)
        lower_threshold = 1.0 - threshold
        midpoint_near_twilight = np.abs(midpoint_elevation[valid_indices]) <= float(twilight_elevation_degrees)
        mixed_path = (valid_daylight_fraction > lower_threshold) & (valid_daylight_fraction < threshold)
        has_twilight_samples = valid_twilight_fraction > 0.0
        valid_greyline_crossing = ((valid_daylight_fraction > 0.0) & (valid_daylight_fraction < 1.0)) | has_twilight_samples
        greyline_crossing[valid_indices] = valid_greyline_crossing.astype("int8")

        valid_class = np.full(len(valid_indices), ILLUMINATION_GREYLINE_MIXED, dtype=object)
        valid_class[(valid_daylight_fraction >= threshold) & ~midpoint_near_twilight] = ILLUMINATION_DAYLIGHT
        valid_class[(valid_daylight_fraction <= lower_threshold) & ~midpoint_near_twilight] = ILLUMINATION_NIGHT
        valid_class[mixed_path | midpoint_near_twilight] = ILLUMINATION_GREYLINE_MIXED
        path_class[valid_indices] = valid_class

    result["path_daylight_fraction"] = np.round(daylight_fraction, 3)
    result["target_solar_elevation"] = np.round(target_elevation, 1)
    result["path_midpoint_solar_elevation"] = np.round(midpoint_elevation, 1)
    result["peer_solar_elevation"] = np.round(peer_elevation, 1)
    result["path_greyline_crossing"] = greyline_crossing
    result["path_illumination"] = pd.Categorical(path_class, categories=ILLUMINATION_CLASSES, ordered=True)
    return result