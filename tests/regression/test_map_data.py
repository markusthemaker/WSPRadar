"""Geometry and stable segment-label equivalence for map preparation."""

from bisect import bisect_right

import numpy as np
import pandas as pd
import pytest

from config import AZIMUTH_STEP, COMPASS, DIST_BINS
from core import map_data
from core.geographic_scope import great_circle_distances_km


def _attach_legacy_map_geometry(frame, *, center_latitude, center_longitude):
    """Freeze the previous row-wise recipe as a scientific equivalence oracle."""
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
        frame["calc_dist"], bins=DIST_BINS, labels=DIST_BINS[:-1], right=False
    ).astype(float)
    frame["r_max"] = pd.cut(
        frame["calc_dist"], bins=DIST_BINS, labels=DIST_BINS[1:], right=False
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


@pytest.mark.parametrize(
    "center_latitude,center_longitude",
    [(52.5, 13.4), (0.0, 179.9), (89.0, 0.0), (-89.0, 0.0)],
)
def test_map_geometry_and_labels_match_legacy_exactly(
    center_latitude, center_longitude
):
    random = np.random.default_rng(20260913)
    frame = pd.DataFrame(
        {
            "peer_lat": np.concatenate(
                [
                    random.uniform(-90.0, 90.0, 512),
                    [center_latitude, 0.0, 0.0, 90.0, -90.0, np.nan, 52.5],
                ]
            ),
            "peer_lon": np.concatenate(
                [
                    random.uniform(-180.0, 180.0, 512),
                    [center_longitude, 180.0, -180.0, 0.0, 0.0, 0.0, np.nan],
                ]
            ),
        }
    )
    frame["evidence"] = pd.Categorical(np.arange(len(frame)) % 3)
    frame.index = pd.Index(np.arange(len(frame)) // 2, name="source_row")
    expected = frame.copy(deep=True)
    actual = frame.copy(deep=True)

    _attach_legacy_map_geometry(
        expected,
        center_latitude=center_latitude,
        center_longitude=center_longitude,
    )
    result = map_data._attach_map_geometry(
        actual,
        center_latitude=center_latitude,
        center_longitude=center_longitude,
    )

    assert result is None
    pd.testing.assert_frame_equal(actual, expected, check_exact=True)


def test_distance_labels_keep_half_open_bins_and_out_of_bounds(monkeypatch):
    distances = np.array(
        [
            value
            for boundary in DIST_BINS
            for value in (
                np.nextafter(float(boundary), -np.inf),
                float(boundary),
                np.nextafter(float(boundary), np.inf),
            )
        ]
        + [-np.inf, np.inf, np.nan]
    )
    frame = pd.DataFrame({"peer_lat": np.zeros(len(distances)), "peer_lon": 1.0})
    monkeypatch.setattr(
        map_data, "great_circle_distances_km", lambda **_kwargs: distances
    )

    map_data._attach_map_geometry(frame, center_latitude=0.0, center_longitude=0.0)

    expected_labels = []
    expected_segments = []
    expected_lower_bounds = []
    expected_upper_bounds = []
    for distance in distances:
        if not np.isfinite(distance) or not DIST_BINS[0] <= distance < DIST_BINS[-1]:
            expected_labels.append("")
            expected_segments.append("Out of Bounds")
            expected_lower_bounds.append(np.nan)
            expected_upper_bounds.append(np.nan)
            continue
        position = bisect_right(DIST_BINS, distance) - 1
        lower_bound, upper_bound = DIST_BINS[position : position + 2]
        label = f"[{int(lower_bound)}-{int(upper_bound)}km]"
        expected_labels.append(label)
        expected_segments.append(f"{label} E")
        expected_lower_bounds.append(float(lower_bound))
        expected_upper_bounds.append(float(upper_bound))

    np.testing.assert_array_equal(frame["calc_dist"].to_numpy(), distances)
    np.testing.assert_array_equal(frame["r_min"].to_numpy(), expected_lower_bounds)
    np.testing.assert_array_equal(frame["r_max"].to_numpy(), expected_upper_bounds)
    assert frame["dist_label"].tolist() == expected_labels
    assert frame["SegmentID"].tolist() == expected_segments


def test_compass_labels_keep_exact_sector_boundaries_and_north_wrap(monkeypatch):
    bearings = [0.0, 360.0, -360.0, np.nan]
    expected_names = ["N", "N", "N", ""]
    for position in range(len(COMPASS)):
        boundary = position * AZIMUTH_STEP + AZIMUTH_STEP / 2.0
        bearings.extend([boundary - 1e-9, boundary, boundary + 1e-9])
        expected_names.extend(
            [COMPASS[position], COMPASS[(position + 1) % len(COMPASS)]]
            + [COMPASS[(position + 1) % len(COMPASS)]]
        )
    frame = pd.DataFrame({"peer_lat": np.zeros(len(bearings)), "peer_lon": 1.0})
    monkeypatch.setattr(
        map_data.np,
        "arctan2",
        lambda _bearing_y, _bearing_x: np.radians(bearings),
    )

    map_data._attach_map_geometry(frame, center_latitude=0.0, center_longitude=0.0)

    assert frame["dir_name"].tolist() == expected_names
    distance_label = f"[{DIST_BINS[0]}-{DIST_BINS[1]}km]"
    assert frame["SegmentID"].tolist() == [
        f"{distance_label} {name}" for name in expected_names
    ]


def test_map_label_preparation_uses_no_per_row_apply_callbacks(monkeypatch):
    frame = pd.DataFrame(
        {"peer_lat": [52.5, 0.0, np.nan], "peer_lon": [13.4, 180.0, 0.0]}
    )

    def reject_apply(*_args, **_kwargs):
        raise AssertionError("Map label preparation must use vectorized lookups.")

    monkeypatch.setattr(pd.Series, "apply", reject_apply)
    monkeypatch.setattr(pd.DataFrame, "apply", reject_apply)

    map_data._attach_map_geometry(frame, center_latitude=52.5, center_longitude=13.4)

    assert frame.loc[0, "SegmentID"] == f"[{DIST_BINS[0]}-{DIST_BINS[1]}km] N"
    assert frame.loc[2, "dir_name"] == ""
    assert frame.loc[2, "SegmentID"] == "Out of Bounds"
