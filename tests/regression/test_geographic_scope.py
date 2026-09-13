from contextlib import closing
from datetime import datetime, timezone
import sqlite3

import numpy as np
import pandas as pd
import pytest
from pyproj import Geod

from core.analysis_context import (
    AnalysisContext,
    COMPARISON_HARDWARE_AB,
    COMPARISON_REFERENCE_STATION,
    SELF_TEST_TX,
    TX_AB_METHOD_SEQUENTIAL,
)
from core.analysis_runner import apply_post_fetch_filters, build_analysis_batches
from core.geographic_scope import (
    build_neighborhood_bounding_box,
    filter_peer_rows_by_distance,
    great_circle_distances_km,
    validate_max_peer_distance_km,
)
from core.map_data import _attach_map_geometry
from core.math_utils import locator_to_latlon
from core.presentation_context import PresentationContext
from i18n import T


LABELS = {"warn_no_data": "No data for {title}."}


def _comparison_analysis(*, is_sequential=False):
    """Return the minimal post-fetch comparison contract used by scope tests."""
    return {
        "analysis_kind": "comparison",
        "is_compare": True,
        "is_sequential": is_sequential,
        "title": "geographic scope",
    }


def _comparison_context(**overrides):
    """Return a valid comparison context with an overridable scope."""
    values = {
        "run_mode": "TX",
        "callsign": "DL1MKS",
        "qth": "JN37",
        "comparison_mode": COMPARISON_REFERENCE_STATION,
        "reference_callsign": "DL2XYZ",
        "reference_qth": "JO62",
        "max_peer_distance_km": 2500,
    }
    values.update(overrides)
    return AnalysisContext(**values)


def test_scope_uses_the_same_distance_values_as_map_geometry_and_is_half_open():
    """Exclude a peer exactly at the configured boundary used by map geometry."""
    frame = pd.DataFrame({"peer_lat": [0.0], "peer_lon": [1.0]})
    distance_km = great_circle_distances_km(
        center_latitude=0.0,
        center_longitude=0.0,
        peer_latitudes=frame["peer_lat"],
        peer_longitudes=frame["peer_lon"],
    )[0]

    map_frame = frame.copy()
    _attach_map_geometry(
        map_frame,
        center_latitude=0.0,
        center_longitude=0.0,
    )

    assert map_frame.loc[0, "calc_dist"] == pytest.approx(distance_km)
    assert filter_peer_rows_by_distance(
        frame,
        center_latitude=0.0,
        center_longitude=0.0,
        max_peer_distance_km=distance_km,
    ).empty
    assert len(
        filter_peer_rows_by_distance(
            frame,
            center_latitude=0.0,
            center_longitude=0.0,
            max_peer_distance_km=np.nextafter(distance_km, np.inf),
        )
    ) == 1


def test_global_scope_is_a_zero_work_identity_fast_path():
    """Keep global behavior unchanged without requiring or copying coordinates."""
    frame = pd.DataFrame({"peer_sign": ["K1AAA"], "evidence": [1]})

    filtered = filter_peer_rows_by_distance(
        frame,
        center_latitude=0.0,
        center_longitude=0.0,
        max_peer_distance_km=22000,
    )

    assert filtered is frame


def test_geographic_scope_does_not_change_global_provider_queries():
    """Keep raw provider queries and cache identity reusable across scope choices."""
    analysis_start = datetime(2026, 7, 1, tzinfo=timezone.utc)
    analysis_end = datetime(2026, 7, 2, tzinfo=timezone.utc)

    def provider_queries(max_peer_distance_km):
        analyses = build_analysis_batches(
            _comparison_context(
                max_peer_distance_km=max_peer_distance_km,
            ),
            analysis_start,
            analysis_end,
            47.0,
            8.0,
            "AND band = '14'",
            presentation_context=PresentationContext(
                labels=T["en"],
                solar_label=T["en"]["opt_solar_all"].split()[0],
            ),
        )
        return [
            (analysis["query"], analysis.get("legacy_query"))
            for analysis in analyses
        ]

    assert provider_queries(2500) == provider_queries(22000)


@pytest.mark.parametrize("invalid_distance", [True, 0, -1, np.nan, np.inf, 22001])
def test_scope_rejects_invalid_core_distance_limits(invalid_distance):
    """Reject invalid scientific limits even if UI validation is bypassed."""
    with pytest.raises(ValueError, match="Maximum peer distance"):
        validate_max_peer_distance_km(invalid_distance)


def test_moving_station_detection_sees_out_of_scope_locator_before_scope_filter():
    """Reject a globally moving callsign even when only one locator is nearby."""
    rows = pd.DataFrame(
        {
            "time_slot": [1, 2, 1],
            "peer_sign": ["MOVE1", "MOVE1", "STATIC1"],
            "peer_grid": ["JJ00AA", "RJ00AA", "JJ00AA"],
            "peer_lat": [0.0, 0.0, 0.0],
            "peer_lon": [1.0, 90.0, 1.0],
            "has_u": [1, 1, 1],
            "has_r": [1, 1, 1],
            "snr_u_norm": [-10.0, -11.0, -12.0],
            "snr_r_norm": [-13.0, -14.0, -15.0],
        }
    )
    context = _comparison_context(exclude_moving_stations=True)

    filtered, warning = apply_post_fetch_filters(
        rows,
        _comparison_analysis(),
        context,
        0.0,
        0.0,
        LABELS,
    )

    assert warning is None
    assert filtered["peer_sign"].tolist() == ["STATIC1"]


def test_target_active_gate_uses_out_of_scope_peer_before_scope_filter():
    """Let distant evidence establish activity without entering scoped results."""
    rows = pd.DataFrame(
        {
            "time_slot": [1, 1],
            "peer_sign": ["DISTANT", "NEARBY"],
            "peer_grid": ["RJ00AA", "JJ00AA"],
            "peer_lat": [0.0, 0.0],
            "peer_lon": [90.0, 1.0],
            "has_u": [1, 0],
            "has_r": [0, 1],
            "snr_u_norm": [-10.0, np.nan],
            "snr_r_norm": [np.nan, -12.0],
        }
    )

    filtered, warning = apply_post_fetch_filters(
        rows,
        _comparison_analysis(),
        _comparison_context(),
        0.0,
        0.0,
        LABELS,
    )

    assert warning is None
    assert filtered["peer_sign"].tolist() == ["NEARBY"]
    assert filtered["time_slot"].tolist() == [1]


def test_sequential_pair_assignment_precedes_scope_filter():
    """Retain scheduled pair columns while excluding a distant peer pair."""
    start_time = datetime(2026, 7, 23, 0, 0, tzinfo=timezone.utc)
    rows = pd.DataFrame(
        {
            "time": [
                start_time,
                start_time.replace(minute=2),
                start_time,
                start_time.replace(minute=2),
            ],
            "peer_sign": ["NEARBY", "NEARBY", "DISTANT", "DISTANT"],
            "peer_grid": ["JJ00AA", "JJ00AA", "RJ00AA", "RJ00AA"],
            "peer_lat": [0.0, 0.0, 0.0, 0.0],
            "peer_lon": [1.0, 1.0, 90.0, 90.0],
            "is_me": [1, 0, 1, 0],
            "stat_val": [-10.0, -12.0, -11.0, -13.0],
        }
    )
    context = _comparison_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
        tx_ab_method=TX_AB_METHOD_SEQUENTIAL,
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )

    filtered, warning = apply_post_fetch_filters(
        rows,
        _comparison_analysis(is_sequential=True),
        context,
        0.0,
        0.0,
        LABELS,
    )

    assert warning is None
    assert filtered["peer_sign"].tolist() == ["NEARBY", "NEARBY"]
    assert filtered["tx_ab_pair_id"].nunique() == 1
    assert {
        "tx_ab_pair_target_time",
        "tx_ab_pair_reference_time",
    }.issubset(filtered.columns)


def test_opportunity_rows_are_scoped_before_the_processed_result_is_returned():
    """Remove distant Success peers while preserving canonical processed columns."""
    target_qth = "JJ00AA"
    target_latitude, target_longitude = locator_to_latlon(target_qth)
    rows = pd.DataFrame(
        {
            "time_slot": [15_000_000, 15_000_000],
            "peer_sign": ["K1AAA", "JA1AAA"],
            "peer_grid": ["JJ00AA", "RJ00AA"],
            "target_seen": [1, 0],
            "external_seen": [1, 1],
            "target_snr": [-10.0, np.nan],
        }
    )
    context = AnalysisContext(
        run_mode="RX",
        callsign="DL1MKS",
        qth=target_qth,
        max_peer_distance_km=2500,
    )
    analysis = {
        "analysis_kind": "opportunity",
        "is_compare": False,
        "is_sequential": False,
        "title": "Performance scope",
    }

    filtered, warning = apply_post_fetch_filters(
        rows,
        analysis,
        context,
        target_latitude,
        target_longitude,
        LABELS,
    )

    assert warning is None
    assert filtered["peer_sign"].astype(str).tolist() == ["K1AAA"]
    assert filtered["outcome"].astype(str).tolist() == ["H"]


def _select_neighborhood_coordinates_with_sql(
    bounding_box,
    coordinates,
    *,
    coordinate_prefix="tx",
):
    """Execute the generated predicate against bound station coordinates."""
    with closing(sqlite3.connect(":memory:")) as connection:
        connection.execute(
            "CREATE TABLE stations (station_id INTEGER, tx_lat REAL, "
            "tx_lon REAL, rx_lat REAL, rx_lon REAL, is_reference INTEGER)"
        )
        station_rows = [
            (station_id, latitude, longitude, latitude, longitude, 1)
            for station_id, (latitude, longitude) in enumerate(coordinates)
        ]
        # Excluded duplicates on each wrapped side expose an ungrouped SQL OR.
        station_rows.extend(
            (-station_id - 1, latitude, longitude, latitude, longitude, 0)
            for station_id, (latitude, longitude) in enumerate(coordinates)
        )
        connection.executemany(
            "INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?)",
            station_rows,
        )
        bounding_predicate = bounding_box.to_sql(
            f"{coordinate_prefix}_lat",
            f"{coordinate_prefix}_lon",
        )
        return [
            station_id
            for (station_id,) in connection.execute(
                "SELECT station_id FROM stations WHERE is_reference = 1 AND "
                + bounding_predicate
                + " ORDER BY station_id"
            )
        ]


@pytest.mark.parametrize("coordinate_prefix", ["tx", "rx"])
@pytest.mark.parametrize("center_longitude", [-179.0, 179.0])
def test_neighborhood_prefilter_keeps_references_across_the_date_line(
    coordinate_prefix,
    center_longitude,
):
    """Retain the reported 139 km Reference and reject distant coordinates."""
    bounding_box = build_neighborhood_bounding_box(
        center_latitude=51.5,
        center_longitude=center_longitude,
        radius_km=200,
    )
    _, _, reference_distance_m = Geod(ellps="WGS84").inv(
        center_longitude,
        51.5,
        -center_longitude,
        51.5,
    )
    coordinates = [
        (51.5, center_longitude),
        (51.5, -center_longitude),
        (51.5, -180.0),
        (51.5, 180.0),
        (51.5, 0.0),
        (40.0, -center_longitude),
    ]

    assert reference_distance_m < 200_000
    assert len(bounding_box.longitude_ranges) == 2
    assert _select_neighborhood_coordinates_with_sql(
        bounding_box,
        coordinates,
        coordinate_prefix=coordinate_prefix,
    ) == [0, 1, 2, 3]


@pytest.mark.parametrize("coordinate_prefix", ["tx", "rx"])
def test_neighborhood_prefilter_treats_both_date_line_centers_equally(
    coordinate_prefix,
):
    """Both legal representations of the date line describe the same region."""
    coordinates = [
        (0.0, -180.0),
        (0.0, 180.0),
        (0.0, -179.95),
        (0.0, 179.95),
        (0.0, -179.0),
        (0.0, 179.0),
        (1.0, 180.0),
    ]
    for center_longitude in (-180.0, 180.0):
        bounding_box = build_neighborhood_bounding_box(
            center_latitude=0.0,
            center_longitude=center_longitude,
            radius_km=10,
        )
        assert _select_neighborhood_coordinates_with_sql(
            bounding_box,
            coordinates,
            coordinate_prefix=coordinate_prefix,
        ) == [0, 1, 2, 3]


@pytest.mark.parametrize("center_latitude", [-90.0, -89.9, 89.9, 90.0])
@pytest.mark.parametrize("coordinate_prefix", ["tx", "rx"])
def test_neighborhood_prefilter_allows_all_longitudes_when_a_pole_is_reached(
    center_latitude,
    coordinate_prefix,
):
    """Longitude must not remove nearby stations in a pole-spanning cap."""
    bounding_box = build_neighborhood_bounding_box(
        center_latitude=center_latitude,
        center_longitude=40.0,
        radius_km=100,
    )
    pole_latitude = 90.0 if center_latitude > 0.0 else -90.0
    coordinates = [
        (pole_latitude, longitude)
        for longitude in (-180.0, -90.0, 0.0, 90.0, 180.0)
    ]
    coordinates.append((0.0, 40.0))

    assert bounding_box.longitude_ranges == ()
    assert -90.0 <= bounding_box.minimum_latitude
    assert bounding_box.maximum_latitude <= 90.0
    assert _select_neighborhood_coordinates_with_sql(
        bounding_box,
        coordinates,
        coordinate_prefix=coordinate_prefix,
    ) == list(range(5))


@pytest.mark.parametrize("latitude_sign", [-1.0, 1.0])
def test_neighborhood_prefilter_keeps_high_latitude_longitude_extremes(
    latitude_sign,
):
    """Keep a 248.94 km station beyond the former 25.84-degree half-width."""
    center_latitude = latitude_sign * 85.0
    reference_latitude = latitude_sign * 85.5
    _, _, reference_distance_m = Geod(ellps="WGS84").inv(
        0.0,
        center_latitude,
        26.5,
        reference_latitude,
    )
    bounding_box = build_neighborhood_bounding_box(
        center_latitude=center_latitude,
        center_longitude=0.0,
        radius_km=250,
    )

    assert reference_distance_m == pytest.approx(248_941.64, abs=0.01)
    assert _select_neighborhood_coordinates_with_sql(
        bounding_box,
        [(reference_latitude, -26.5), (reference_latitude, 26.5)],
    ) == [0, 1]


@pytest.mark.parametrize("radius_km", [10, 100, 200, 250])
@pytest.mark.parametrize(
    ("center_latitude", "center_longitude"),
    [
        (0.0, 0.0),
        (0.0, -180.0),
        (0.0, 180.0),
        (47.0, 8.0),
        (-47.0, -8.0),
        (51.5, 179.0),
        (51.5, -179.0),
        (85.0, 0.0),
        (-85.0, 0.0),
        (88.0, 179.0),
        (-88.0, -179.0),
        (89.95, -120.0),
        (-89.95, 120.0),
        (90.0, 0.0),
        (-90.0, 0.0),
    ],
)
def test_neighborhood_prefilter_contains_wgs84_circle_and_interior(
    center_latitude,
    center_longitude,
    radius_km,
):
    """An independent ellipsoidal oracle probes bearings and radius fractions."""
    bounding_box = build_neighborhood_bounding_box(
        center_latitude=center_latitude,
        center_longitude=center_longitude,
        radius_km=radius_km,
    )
    geodesic = Geod(ellps="WGS84")
    coordinates = [(center_latitude, center_longitude)]
    for radius_fraction in (0.25, 0.5, 0.75, 0.999999, 1.0):
        for azimuth_degrees in range(0, 360, 5):
            reference_longitude, reference_latitude, _ = geodesic.fwd(
                center_longitude,
                center_latitude,
                azimuth_degrees,
                radius_fraction * radius_km * 1000,
            )
            coordinates.append((reference_latitude, reference_longitude))

    assert _select_neighborhood_coordinates_with_sql(
        bounding_box,
        coordinates,
    ) == list(range(len(coordinates)))


def test_neighborhood_prefilter_retains_a_narrow_ordinary_bounding_box():
    """The corrected prefilter still discards distant rows before distance work."""
    bounding_box = build_neighborhood_bounding_box(
        center_latitude=0.0,
        center_longitude=0.0,
        radius_km=100,
    )
    coordinates = [(0.0, 0.0), (0.8, 0.8), (1.0, 0.0), (0.0, 1.0)]

    assert len(bounding_box.longitude_ranges) == 1
    # The rectangle intentionally admits a corner outside the 100 km circle;
    # the existing authoritative geoDistance predicate removes that candidate.
    assert _select_neighborhood_coordinates_with_sql(
        bounding_box,
        coordinates,
    ) == [0, 1]


@pytest.mark.parametrize(
    "invalid_radius_km",
    [True, np.bool_(False), 0, -1, np.nan, np.inf, -np.inf, 251, None, "invalid"],
)
def test_neighborhood_prefilter_rejects_invalid_radius_at_core_boundary(
    invalid_radius_km,
):
    with pytest.raises(ValueError):
        build_neighborhood_bounding_box(
            center_latitude=0.0,
            center_longitude=0.0,
            radius_km=invalid_radius_km,
        )


@pytest.mark.parametrize(
    ("coordinate_name", "invalid_coordinate"),
    [
        ("center_latitude", -90.01),
        ("center_latitude", 90.01),
        ("center_longitude", -180.01),
        ("center_longitude", 180.01),
        ("center_latitude", True),
        ("center_longitude", np.bool_(False)),
        ("center_latitude", np.nan),
        ("center_longitude", np.nan),
        ("center_latitude", np.inf),
        ("center_longitude", -np.inf),
        ("center_latitude", None),
        ("center_longitude", "invalid"),
    ],
)
def test_neighborhood_prefilter_rejects_invalid_coordinates_at_core_boundary(
    coordinate_name,
    invalid_coordinate,
):
    arguments = {
        "center_latitude": 0.0,
        "center_longitude": 0.0,
        "radius_km": 100,
        coordinate_name: invalid_coordinate,
    }
    with pytest.raises(ValueError):
        build_neighborhood_bounding_box(**arguments)


@pytest.mark.parametrize(
    ("latitude_column", "longitude_column"),
    [
        ("tx_lat", "rx_lon"),
        ("rx_lat", "tx_lon"),
        ("peer_lat", "peer_lon"),
        ("tx_lat OR 1=1", "tx_lon"),
        ("rx_lat", "rx_lon); DROP TABLE stations; --"),
    ],
)
def test_neighborhood_prefilter_rejects_unapproved_sql_coordinate_columns(
    latitude_column,
    longitude_column,
):
    bounding_box = build_neighborhood_bounding_box(
        center_latitude=0.0,
        center_longitude=0.0,
        radius_km=10,
    )
    with pytest.raises(ValueError):
        bounding_box.to_sql(latitude_column, longitude_column)
