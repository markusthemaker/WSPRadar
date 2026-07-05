from datetime import datetime, timezone

import pandas as pd

from core.analysis_context import (
    AnalysisContext,
    COMPARISON_HARDWARE_AB,
    COMPARISON_LOCAL_NEIGHBORHOOD,
    COMPARISON_REFERENCE_STATION,
    LOCAL_BENCHMARK_MEDIAN,
    SELF_TEST_RX,
    SELF_TEST_TX,
    WSPR_FRAME_00_04_08,
    WSPR_FRAME_02_06_10,
)
from core.analysis_runner import apply_post_fetch_filters, build_analysis_batches
from i18n import T


START_TIME = datetime(2026, 5, 27, tzinfo=timezone.utc)
END_TIME = datetime(2026, 5, 28, tzinfo=timezone.utc)


def _analysis_context(**overrides):
    values = {
        "language": "en",
        "run_mode": "TX",
        "callsign": "DL1MKS",
        "qth": "JN37",
        "band": "20m",
        "comparison_mode": COMPARISON_REFERENCE_STATION,
        "reference_callsign": "DL2XYZ",
        "target_wspr_frame": WSPR_FRAME_00_04_08,
        "reference_wspr_frame": WSPR_FRAME_02_06_10,
        "tx_ab_bin_minutes": 8,
    }
    values.update(overrides)
    return AnalysisContext(**values)


def _build_analyses(context):
    return build_analysis_batches(
        context,
        START_TIME,
        END_TIME,
        47.0,
        8.0,
        "AND band = '14'",
    )


def _analysis_by_id(context, analysis_id):
    return next(analysis for analysis in _build_analyses(context) if analysis["id"] == analysis_id)


def test_tx_ab_wspr_frame_sql_uses_complete_utc_start_minute_sequences():
    context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
        target_wspr_frame=WSPR_FRAME_00_04_08,
        reference_wspr_frame=WSPR_FRAME_02_06_10,
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")
    tx_absolute = _analysis_by_id(context, "TX_ABS")

    assert "toMinute(time) % 4 = 0" in tx_compare["query"]
    assert "toMinute(time) % 4 = 2" in tx_compare["query"]
    assert "toMinute(time) % 4 = 0" in tx_absolute["query"]


def test_positive_reference_snr_correction_is_added_to_reference_side():
    context = _analysis_context(reference_snr_correction_db=1.6)

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert "maxIf(snr - power + 30, is_me = 1) AS snr_u_norm" in tx_compare["query"]
    assert "maxIf((snr - power + 30 + 1.6), is_me = 0) AS snr_r_norm" in tx_compare["query"]
    assert "maxIf((snr - power + 30 + 1.6), is_me = 1)" not in tx_compare["query"]


def test_reference_station_matching_uses_prefix_callsign_filters():
    context = _analysis_context(
        comparison_mode=COMPARISON_REFERENCE_STATION,
        reference_callsign="DL2XYZ",
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert "tx_sign LIKE 'DL1MKS%'" in tx_compare["query"]
    assert "tx_sign LIKE 'DL2XYZ%'" in tx_compare["query"]


def test_rx_hardware_ab_matching_uses_exact_callsigns_to_protect_suffixes():
    context = _analysis_context(
        run_mode="RX",
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_RX,
        setup_b_callsign="DL1MKS/P",
    )

    rx_compare = _analysis_by_id(context, "RX_COMP")

    assert "rx_sign = 'DL1MKS'" in rx_compare["query"]
    assert "rx_sign = 'DL1MKS/P'" in rx_compare["query"]
    assert "rx_sign LIKE 'DL1MKS%'" not in rx_compare["query"]
    assert "rx_sign LIKE 'DL1MKS/P%'" not in rx_compare["query"]


def test_local_median_neighborhood_uses_median_reference_sql_and_detail_rows():
    context = _analysis_context(
        comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
        local_benchmark=LOCAL_BENCHMARK_MEDIAN,
        neighborhood_radius_km=100,
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert "quantileExactInclusiveIf(0.5)((snr - power + 30 + 0.0), is_me = 0) AS snr_r_norm" in tx_compare["query"]
    assert "groupArrayIf(tuple(local_sign, local_grid, local_dist, (snr - power + 30 + 0.0)), is_me = 0) AS ref_detail_rows" in tx_compare["query"]


def test_non_sequential_cycle_synchronization_keeps_only_target_active_slots():
    context = _analysis_context()
    analysis = {
        "analysis_kind": "comparison",
        "is_compare": True,
        "is_sequential": False,
        "title": "cycle sync",
    }
    rows = pd.DataFrame({
        "time_slot": [1, 1, 2, 2, 3],
        "has_u": [1, 0, 0, 0, 1],
        "has_r": [1, 1, 1, 0, 0],
        "snr_u_norm": [1.0, None, None, None, 2.0],
        "snr_r_norm": [0.0, 0.5, -1.0, None, None],
    })

    filtered, warning = apply_post_fetch_filters(rows, analysis, context, 47.0, 8.0, T["en"])

    assert warning is None
    assert set(filtered["time_slot"]) == {1, 3}


def test_sequential_comparison_does_not_apply_async_cycle_synchronization():
    context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
    )
    analysis = {
        "analysis_kind": "comparison",
        "is_compare": True,
        "is_sequential": True,
        "title": "sequential",
    }
    rows = pd.DataFrame({
        "time": [START_TIME, END_TIME],
        "is_me": [1, 0],
        "stat_val": [1.0, 0.0],
        "has_u": [1, 0],
    })

    filtered, warning = apply_post_fetch_filters(rows, analysis, context, 47.0, 8.0, T["en"])

    assert warning is None
    assert len(filtered) == 2
