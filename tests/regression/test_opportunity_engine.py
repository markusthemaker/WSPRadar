from datetime import datetime, timezone
import math

import numpy as np
import pandas as pd

from core.opportunity_engine import (
    SUCCESS_RATE_BOUNDS,
    SUCCESS_RATE_COLORS,
    SUCCESS_RATE_TICK_LABELS,
    aggregate_opportunity_peers,
    aggregate_opportunity_segments,
    build_absolute_opportunity_query,
    opportunity_rate_scale_max,
    prepare_opportunity_rows,
)
from core.solar_path import (
    ILLUMINATION_DAYLIGHT,
    ILLUMINATION_NIGHT,
    _solar_time_terms,
    classify_path_illumination,
    solar_elevation_degrees,
    solar_elevation_from_terms,
    solar_elevation_from_sun_vectors,
    sun_unit_vectors_from_terms,
)


def _server_row(slot, call, grid, target_seen, external_seen, target_snr=None):
    return {
        "time_slot": slot,
        "peer_sign": call,
        "peer_grid": grid,
        "target_seen": target_seen,
        "external_seen": external_seen,
        "target_snr": target_snr,
    }


def test_rx_opportunity_classification_and_target_exclusion():
    source = pd.DataFrame([
        _server_row(100, "K1AAA", "FN31aa", 1, 1, -12),
        _server_row(101, "K1AAA", "FN31aa", 0, 1, None),
        _server_row(102, "K1AAA", "FN31aa", 1, 0, -8),
        _server_row(103, "DL1MKS", "JO31aa", 1, 1, -5),
        _server_row(104, "BAD", "INVALID", 1, 1, -5),
    ])

    rows = prepare_opportunity_rows(
        source,
        target_callsign="DL1MKS",
        target_qth="JN37UN",
    )

    assert rows["outcome"].tolist() == ["H", "M", "T"]
    assert int(rows["opportunity"].sum()) == 2
    assert int(rows["hit"].sum()) == 1
    assert int(rows["miss"].sum()) == 1
    assert int(rows["target_only"].sum()) == 1
    assert (rows["opportunity"] == rows["hit"] + rows["miss"]).all()
    assert {"path_illumination", "path_daylight_fraction", "target_solar_elevation", "path_midpoint_solar_elevation", "peer_solar_elevation", "path_greyline_crossing"}.issubset(rows.columns)

    peers = aggregate_opportunity_peers(rows, min_opportunities=2)
    peer = peers.iloc[0]
    assert int(peer["opportunities"]) == 2
    assert int(peer["hits"]) == 1
    assert int(peer["misses"]) == 1
    assert int(peer["target_only"]) == 1
    assert bool(peer["eligible"])
    assert math.isclose(float(peer["rate_pct"]), 50.0, abs_tol=0.001)
    assert math.isclose(float(peer["successful_snr_median"]), -12.0, abs_tol=0.001)


def test_path_illumination_preserves_duplicate_row_results():
    duplicate_rows = pd.DataFrame({
        "cycle_time": [
            datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        ],
        "peer_lat": [40.0, 40.0],
        "peer_lon": [-75.0, -75.0],
    })

    classified = classify_path_illumination(
        duplicate_rows,
        target_latitude=47.0,
        target_longitude=8.0,
        daylight_fraction_threshold=0.75,
        twilight_elevation_degrees=6.0,
        sample_points=5,
    )
    single = classify_path_illumination(
        duplicate_rows.iloc[[0]],
        target_latitude=47.0,
        target_longitude=8.0,
        daylight_fraction_threshold=0.75,
        twilight_elevation_degrees=6.0,
        sample_points=5,
    )

    assert len(classified) == 2
    for column in [
        "path_daylight_fraction",
        "target_solar_elevation",
        "path_midpoint_solar_elevation",
        "peer_solar_elevation",
        "path_greyline_crossing",
    ]:
        assert classified.loc[0, column] == classified.loc[1, column]
        assert classified.loc[0, column] == single.loc[0, column]
    assert str(classified.loc[0, "path_illumination"]) == str(classified.loc[1, "path_illumination"])
    assert str(classified.loc[0, "path_illumination"]) == str(single.loc[0, "path_illumination"])


def test_precomputed_solar_terms_match_direct_elevation_helper():
    times = pd.DatetimeIndex([
        "2026-03-20 00:00:00Z",
        "2026-06-21 12:30:00Z",
        "2026-12-21 23:58:00Z",
    ])
    latitudes = np.asarray([0.0, 47.0, -33.9], dtype=float)
    longitudes = np.asarray([0.0, 8.0, 151.2], dtype=float)

    direct = solar_elevation_degrees(times, latitudes, longitudes)
    from_terms = solar_elevation_from_terms(_solar_time_terms(times), latitudes, longitudes)

    assert np.allclose(from_terms, direct, rtol=0.0, atol=1e-12)


def test_sun_vector_elevation_matches_reference_formula_across_edge_cases():
    times = pd.DatetimeIndex([
        "2026-03-20 00:00:00Z",
        "2026-03-20 12:00:00Z",
        "2026-06-21 23:58:00Z",
        "2026-12-21 00:02:00Z",
        "2026-07-05 04:30:00Z",
        "2026-07-05 16:30:00Z",
    ])
    latitudes = np.asarray([0.0, 0.0, 66.5, -66.5, 47.0, -33.9], dtype=float)
    longitudes = np.asarray([0.0, 179.9, -179.9, 8.0, -75.0, 151.2], dtype=float)
    solar_terms = _solar_time_terms(times)

    reference = solar_elevation_from_terms(solar_terms, latitudes, longitudes)
    vectorized = solar_elevation_from_sun_vectors(
        sun_unit_vectors_from_terms(solar_terms),
        latitudes,
        longitudes,
    )

    assert np.allclose(vectorized, reference, rtol=0.0, atol=1e-10)


def test_target_only_never_enters_denominator():
    source = pd.DataFrame([
        _server_row(100, "K1AAA", "FN31aa", 1, 0, -12),
        _server_row(101, "K1AAA", "FN31aa", 1, 0, -8),
    ])
    rows = prepare_opportunity_rows(
        source,
        target_callsign="DL1MKS",
        target_qth="JN37",
    )
    peer = aggregate_opportunity_peers(rows, min_opportunities=1).iloc[0]

    assert int(peer["opportunities"]) == 0
    assert int(peer["target_only"]) == 2
    assert not bool(peer["eligible"])
    assert pd.isna(peer["rate_pct"])


def test_segment_value_is_average_station_rate_not_pooled():
    peers = pd.DataFrame([
        {
            "SegmentID": "A",
            "dist_label": "[0-2500km]",
            "dir_name": "W",
            "r_min": 0.0,
            "r_max": 2500.0,
            "az_bucket": 12.0,
            "peer_sign": "A",
            "peer_grid": "AA00",
            "eligible": True,
            "rate_pct": 100.0,
            "opportunities": 10,
            "hits": 10,
            "misses": 0,
            "target_only": 0,
        },
        {
            "SegmentID": "A",
            "dist_label": "[0-2500km]",
            "dir_name": "W",
            "r_min": 0.0,
            "r_max": 2500.0,
            "az_bucket": 12.0,
            "peer_sign": "C",
            "peer_grid": "CC00",
            "eligible": True,
            "rate_pct": 100.0,
            "opportunities": 1,
            "hits": 1,
            "misses": 0,
            "target_only": 0,
        },
        {
            "SegmentID": "A",
            "dist_label": "[0-2500km]",
            "dir_name": "W",
            "r_min": 0.0,
            "r_max": 2500.0,
            "az_bucket": 12.0,
            "peer_sign": "B",
            "peer_grid": "BB00",
            "eligible": True,
            "rate_pct": 0.0,
            "opportunities": 1,
            "hits": 0,
            "misses": 1,
            "target_only": 0,
        },
        {
            "SegmentID": "A",
            "dist_label": "[0-2500km]",
            "dir_name": "W",
            "r_min": 0.0,
            "r_max": 2500.0,
            "az_bucket": 12.0,
            "peer_sign": "LOW_EVIDENCE",
            "peer_grid": "DD00",
            "eligible": False,
            "rate_pct": 100.0,
            "opportunities": 100,
            "hits": 100,
            "misses": 0,
            "target_only": 0,
        },
    ])

    segment = aggregate_opportunity_segments(peers).iloc[0]
    assert math.isclose(float(segment["val"]), 66.7, abs_tol=0.1)
    assert math.isclose(float(segment["pooled_rate_pct"]), 91.7, abs_tol=0.1)


def test_opportunity_rate_scale_adds_headroom_and_caps_at_100():
    assert math.isclose(opportunity_rate_scale_max([]), 1.0, abs_tol=0.001)
    assert math.isclose(opportunity_rate_scale_max([0.0]), 1.0, abs_tol=0.001)
    assert math.isclose(opportunity_rate_scale_max([2.7]), 3.0, abs_tol=0.001)
    assert math.isclose(opportunity_rate_scale_max([80.0]), 88.0, abs_tol=0.001)
    assert math.isclose(opportunity_rate_scale_max([100.0]), 100.0, abs_tol=0.001)


def test_success_rate_scale_separates_zero_from_positive_evidence():
    assert SUCCESS_RATE_BOUNDS[0] == 0.0
    assert 0.0 < SUCCESS_RATE_BOUNDS[1] < 1.0
    assert SUCCESS_RATE_TICK_LABELS[:3] == ("0%", ">0%", "1%")
    assert len(SUCCESS_RATE_TICK_LABELS) == len(SUCCESS_RATE_BOUNDS)
    assert len(SUCCESS_RATE_COLORS) == len(SUCCESS_RATE_BOUNDS) - 1


def test_rx_query_uses_exact_target_qth_half_open_time_and_compact_schema():
    query = build_absolute_opportunity_query(
        mode="RX",
        start_t=datetime(2026, 5, 27, tzinfo=timezone.utc),
        end_t=datetime(2026, 6, 1, tzinfo=timezone.utc),
        band_value="14",
        callsign="DL1MKS",
        qth="JN37UN",
        exclude_special_callsigns=True,
    )

    assert "rx_sign = 'DL1MKS'" in query
    assert "max(toUInt8(rx_sign != 'DL1MKS')) AS external_seen" in query
    assert "(rx_sign = 'DL1MKS' AND substring(rx_loc, 1, 4) = 'JN37' OR rx_sign != 'DL1MKS')" in query
    assert "substring(rx_loc, 1, 4) = 'JN37'" in query
    assert "time >= '2026-05-27 00:00:00'" in query
    assert "time < '2026-06-01 00:00:00'" in query
    assert "band = 14" in query
    assert "code = 1" in query
    assert "tx_sign NOT LIKE 'Q%'" in query
    assert "notEmpty(tx_sign)" in query
    assert "IN (SELECT cycle FROM active_cycles)" in query
    assert "tx_lat" not in query
    assert "tx_lon" not in query
    assert "JOIN" not in query.upper()
    assert query.endswith("FORMAT Parquet")


def test_rx_query_can_disable_decode_code_for_legacy_rows():
    query = build_absolute_opportunity_query(
        mode="RX",
        start_t=datetime(2010, 12, 18, tzinfo=timezone.utc),
        end_t=datetime(2010, 12, 21, tzinfo=timezone.utc),
        band_value="7",
        callsign="KP4MD",
        qth="CM98",
        require_decode_code=False,
    )

    assert "code = 1" not in query
    assert "rx_sign = 'KP4MD'" in query
    assert "substring(rx_loc, 1, 4) = 'CM98'" in query
    assert query.endswith("FORMAT Parquet")


def test_tx_query_uses_receiver_peers_and_target_frame_when_requested():
    query = build_absolute_opportunity_query(
        mode="TX",
        start_t=datetime(2026, 5, 27, tzinfo=timezone.utc),
        end_t=datetime(2026, 5, 28, tzinfo=timezone.utc),
        band_value="14",
        callsign="DL1MKS",
        qth="JN37",
        target_frame_mod4=2,
    )

    assert "tx_sign = 'DL1MKS'" in query
    assert "max(toUInt8(tx_sign != 'DL1MKS')) AS external_seen" in query
    assert "substring(tx_loc, 1, 4) = 'JN37'" in query
    assert "rx_sign AS peer_sign" in query
    assert "rx_loc AS peer_grid" in query
    assert "toMinute(time) % 4 = 2" in query

def test_path_illumination_uses_configurable_daylight_fraction_threshold():
    frame = pd.DataFrame({
        "cycle_time": [
            pd.Timestamp("2026-03-20 12:00:00Z"),
            pd.Timestamp("2026-03-20 00:00:00Z"),
        ],
        "peer_lat": [0.0, 0.0],
        "peer_lon": [10.0, 10.0],
    })

    classified = classify_path_illumination(
        frame,
        target_latitude=0.0,
        target_longitude=0.0,
        daylight_fraction_threshold=0.75,
        twilight_elevation_degrees=6.0,
        sample_points=9,
    )

    assert classified["path_illumination"].astype(str).tolist() == [
        ILLUMINATION_DAYLIGHT,
        ILLUMINATION_NIGHT,
    ]
    assert float(classified.iloc[0]["path_daylight_fraction"]) >= 0.75
    assert float(classified.iloc[1]["path_daylight_fraction"]) <= 0.25
