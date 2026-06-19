from datetime import datetime, timezone
import math

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

    peers = aggregate_opportunity_peers(rows, min_opportunities=2)
    peer = peers.iloc[0]
    assert int(peer["opportunities"]) == 2
    assert int(peer["hits"]) == 1
    assert int(peer["misses"]) == 1
    assert int(peer["target_only"]) == 1
    assert bool(peer["eligible"])
    assert math.isclose(float(peer["rate_pct"]), 50.0, abs_tol=0.001)
    assert math.isclose(float(peer["successful_snr_median"]), -12.0, abs_tol=0.001)


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
