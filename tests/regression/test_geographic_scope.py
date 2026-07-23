from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from core.analysis_context import (
    AnalysisContext,
    COMPARISON_HARDWARE_AB,
    COMPARISON_REFERENCE_STATION,
    SELF_TEST_TX,
    TX_AB_METHOD_SEQUENTIAL,
)
from core.analysis_runner import apply_post_fetch_filters, build_analysis_batches
from core.geographic_scope import (
    filter_peer_rows_by_distance,
    great_circle_distances_km,
    validate_max_peer_distance_km,
)
from core.map_data import _attach_map_geometry
from core.math_utils import locator_to_latlon


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
        "title": "Success scope",
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
