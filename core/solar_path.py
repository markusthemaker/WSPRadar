"""Great-circle path illumination helpers for Absolute success evidence."""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass

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


@dataclass(frozen=True)
class SolarTimeTerms:
    """Time-only solar terms reusable across many positions at the same UTC times."""

    times: pd.DatetimeIndex
    minutes_utc: np.ndarray
    equation_of_time: np.ndarray
    declination: np.ndarray


def _timed_span(timing_collector, label, detail=""):
    """Return a timing context when profiling is active."""
    if timing_collector is None:
        return nullcontext()
    return timing_collector.span(label, detail=detail)


def _utc_datetime_index(times_utc):
    """Return UTC timestamps as a DatetimeIndex, preserving scalar inputs as one row."""
    times = pd.to_datetime(times_utc, utc=True, errors="coerce")
    if isinstance(times, pd.Timestamp):
        return pd.DatetimeIndex([times])
    return pd.DatetimeIndex(times)


def _solar_time_terms(times_utc):
    """Return solar terms that depend only on UTC time, not on observer position."""
    times = _utc_datetime_index(times_utc)
    count = len(times)
    if count == 0:
        empty = np.asarray([], dtype=float)
        return SolarTimeTerms(
            times=times,
            minutes_utc=empty,
            equation_of_time=empty,
            declination=empty,
        )

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

    return SolarTimeTerms(
        times=times,
        minutes_utc=minutes_utc,
        equation_of_time=equation_of_time,
        declination=declination,
    )


def solar_elevation_from_terms(solar_time_terms, latitude_degrees, longitude_degrees):
    """Return approximate solar elevation from precomputed UTC solar terms."""
    count = len(solar_time_terms.times)
    if count == 0:
        return np.asarray([], dtype=float)

    latitude = np.broadcast_to(np.asarray(latitude_degrees, dtype=float), count)
    longitude = np.broadcast_to(np.asarray(longitude_degrees, dtype=float), count)

    true_solar_minutes = (
        solar_time_terms.minutes_utc
        + solar_time_terms.equation_of_time
        + 4.0 * longitude
    ) % 1440.0
    hour_angle = np.radians(true_solar_minutes / 4.0 - 180.0)
    latitude_radians = np.radians(latitude)
    cos_zenith = (
        np.sin(latitude_radians) * np.sin(solar_time_terms.declination)
        + np.cos(latitude_radians) * np.cos(solar_time_terms.declination) * np.cos(hour_angle)
    )
    cos_zenith = np.clip(cos_zenith, -1.0, 1.0)
    return 90.0 - np.degrees(np.arccos(cos_zenith))


def sun_unit_vectors_from_terms(solar_time_terms):
    """Return geocentric sun direction unit vectors for the precomputed UTC terms."""
    count = len(solar_time_terms.times)
    if count == 0:
        return np.empty((3, 0), dtype=float)

    greenwich_hour_angle = np.radians(
        solar_time_terms.minutes_utc / 4.0
        + solar_time_terms.equation_of_time / 4.0
        - 180.0
    )
    cos_declination = np.cos(solar_time_terms.declination)
    return np.stack(
        [
            cos_declination * np.cos(greenwich_hour_angle),
            -cos_declination * np.sin(greenwich_hour_angle),
            np.sin(solar_time_terms.declination),
        ],
        axis=0,
    )


def solar_elevation_from_sun_vectors(sun_vectors, latitude_degrees, longitude_degrees):
    """Return solar elevation by dotting observer surface vectors with sun vectors."""
    count = sun_vectors.shape[1]
    if count == 0:
        return np.asarray([], dtype=float)

    latitude = np.broadcast_to(np.asarray(latitude_degrees, dtype=float), count)
    longitude = np.broadcast_to(np.asarray(longitude_degrees, dtype=float), count)
    surface_vectors = _unit_vector(np.radians(latitude), np.radians(longitude))
    return _solar_elevation_from_unit_vectors(sun_vectors, surface_vectors)


def solar_elevation_degrees(times_utc, latitude_degrees, longitude_degrees):
    """Return approximate solar elevation in degrees for UTC times and positions."""
    return solar_elevation_from_terms(
        _solar_time_terms(times_utc),
        latitude_degrees,
        longitude_degrees,
    )


def _solar_elevation_from_unit_vectors(sun_vectors, surface_vectors):
    """Return solar elevation from matching sun and surface unit vectors."""
    cos_zenith = np.sum(surface_vectors * sun_vectors, axis=0)
    cos_zenith = np.clip(cos_zenith, -1.0, 1.0)
    return np.degrees(np.arcsin(cos_zenith))


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
    timing_collector=None,
) -> pd.DataFrame:
    """Attach great-circle path illumination metrics to station-cycle rows."""
    if frame is None or frame.empty:
        return frame

    with _timed_span(timing_collector, "path illumination input setup"):
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
        with _timed_span(timing_collector, "path illumination unique keying"):
            valid_indices = np.flatnonzero(valid)
            valid_times = times.iloc[valid_indices]
            valid_peer_latitude = peer_latitude[valid_indices]
            valid_peer_longitude = peer_longitude[valid_indices]

            time_nanoseconds = valid_times.astype("int64").to_numpy()
            illumination_keys = pd.MultiIndex.from_arrays(
                [time_nanoseconds, valid_peer_latitude, valid_peer_longitude],
                names=["time_ns", "peer_latitude", "peer_longitude"],
            )
            inverse_codes, _ = pd.factorize(illumination_keys, sort=False)
            unique_positions = np.flatnonzero(~illumination_keys.duplicated())
            unique_times = valid_times.iloc[unique_positions]
            unique_peer_latitude = valid_peer_latitude[unique_positions]
            unique_peer_longitude = valid_peer_longitude[unique_positions]
            unique_count = len(unique_positions)
        if timing_collector is not None:
            duplicate_factor = len(valid_indices) / max(unique_count, 1)
            timing_collector.add(
                "path illumination key cardinality",
                0.0,
                detail=f"rows={count} valid={len(valid_indices)} unique={unique_count} duplicate_factor={duplicate_factor:.2f}",
            )

        with _timed_span(timing_collector, "path illumination solar time terms"):
            solar_time_terms = _solar_time_terms(unique_times)

        with _timed_span(timing_collector, "path illumination sun vectors"):
            sun_vectors = sun_unit_vectors_from_terms(solar_time_terms)

        with _timed_span(timing_collector, "path illumination geometry prep"):
            sample_points = max(int(sample_points), 3)
            fractions = np.linspace(0.0, 1.0, sample_points)
            target_latitude_radians = np.radians(float(target_latitude))
            target_longitude_radians = np.radians(float(target_longitude))
            peer_latitude_radians = np.radians(unique_peer_latitude)
            peer_longitude_radians = np.radians(unique_peer_longitude)

            target_vector = _unit_vector(target_latitude_radians, target_longitude_radians).reshape(3, 1)
            peer_vector = _unit_vector(peer_latitude_radians, peer_longitude_radians)
            dot = np.clip(np.sum(target_vector * peer_vector, axis=0), -1.0, 1.0)
            omega = np.arccos(dot)
            sin_omega = np.sin(omega)
            same_point = np.abs(sin_omega) < 1e-12

            daylight_counts = np.zeros(unique_count, dtype=float)
            twilight_counts = np.zeros(unique_count, dtype=float)
            midpoint_sample_index = int(np.argmin(np.abs(fractions - 0.5)))
            midpoint_altitudes = None

        with _timed_span(timing_collector, "path illumination endpoint solar"):
            unique_target_elevation = _solar_elevation_from_unit_vectors(
                sun_vectors,
                target_vector,
            ).astype("float32")
            unique_peer_elevation = _solar_elevation_from_unit_vectors(
                sun_vectors,
                peer_vector,
            ).astype("float32")

        with _timed_span(timing_collector, "path illumination sample loop", detail=f"samples={sample_points} unique={unique_count}"):
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
                sample_altitude = _solar_elevation_from_unit_vectors(sun_vectors, sample_vector)

                daylight_counts += sample_altitude > 0.0
                twilight_counts += np.abs(sample_altitude) <= float(twilight_elevation_degrees)
                if sample_index == midpoint_sample_index:
                    midpoint_altitudes = sample_altitude

        with _timed_span(timing_collector, "path illumination classification"):
            unique_daylight_fraction = daylight_counts / float(sample_points)
            unique_twilight_fraction = twilight_counts / float(sample_points)

            threshold = min(max(float(daylight_fraction_threshold), 0.5), 1.0)
            lower_threshold = 1.0 - threshold
            midpoint_near_twilight = np.abs(midpoint_altitudes) <= float(twilight_elevation_degrees)
            mixed_path = (unique_daylight_fraction > lower_threshold) & (unique_daylight_fraction < threshold)
            has_twilight_samples = unique_twilight_fraction > 0.0
            unique_greyline_crossing = ((unique_daylight_fraction > 0.0) & (unique_daylight_fraction < 1.0)) | has_twilight_samples

            unique_class = np.full(unique_count, ILLUMINATION_GREYLINE_MIXED, dtype=object)
            unique_class[(unique_daylight_fraction >= threshold) & ~midpoint_near_twilight] = ILLUMINATION_DAYLIGHT
            unique_class[(unique_daylight_fraction <= lower_threshold) & ~midpoint_near_twilight] = ILLUMINATION_NIGHT
            unique_class[mixed_path | midpoint_near_twilight] = ILLUMINATION_GREYLINE_MIXED

        with _timed_span(timing_collector, "path illumination expand results"):
            daylight_fraction[valid_indices] = unique_daylight_fraction[inverse_codes].astype("float32")
            target_elevation[valid_indices] = unique_target_elevation[inverse_codes]
            midpoint_elevation[valid_indices] = midpoint_altitudes[inverse_codes].astype("float32")
            peer_elevation[valid_indices] = unique_peer_elevation[inverse_codes]
            greyline_crossing[valid_indices] = unique_greyline_crossing[inverse_codes].astype("int8")
            path_class[valid_indices] = unique_class[inverse_codes]

    with _timed_span(timing_collector, "path illumination dataframe assignment"):
        result["path_daylight_fraction"] = np.round(daylight_fraction, 3)
        result["target_solar_elevation"] = np.round(target_elevation, 1)
        result["path_midpoint_solar_elevation"] = np.round(midpoint_elevation, 1)
        result["peer_solar_elevation"] = np.round(peer_elevation, 1)
        result["path_greyline_crossing"] = greyline_crossing
        result["path_illumination"] = pd.Categorical(path_class, categories=ILLUMINATION_CLASSES, ordered=True)
    return result
