from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from core.analysis_context import (
    AnalysisContext,
    COMPARISON_HARDWARE_AB,
    COMPARISON_LOCAL_NEIGHBORHOOD,
    COMPARISON_NONE,
    COMPARISON_REFERENCE_STATION,
    LOCAL_BENCHMARK_MEDIAN,
    SELF_TEST_RX,
    SELF_TEST_TX,
    TX_AB_METHOD_SEQUENTIAL,
    TX_AB_METHOD_SIMULTANEOUS,
)
from core.analysis_runner import apply_post_fetch_filters, build_analysis_batches
from i18n import T


START_TIME = datetime(2026, 5, 27, tzinfo=timezone.utc)
END_TIME = datetime(2026, 5, 28, tzinfo=timezone.utc)


def _analysis_context(**overrides):
    values = {
        "run_mode": "TX",
        "callsign": "DL1MKS",
        "qth": "JN37",
        "band": "20m",
        "comparison_mode": COMPARISON_REFERENCE_STATION,
        "reference_callsign": "DL2XYZ",
        "reference_qth": "JO62",
        "tx_ab_repeat_interval_minutes": 10,
        "tx_ab_target_start_minute": 0,
        "tx_ab_reference_start_minute": 2,
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


def test_no_benchmark_builds_only_the_directional_success_analysis():
    tx_analyses = _build_analyses(
        _analysis_context(run_mode="TX", comparison_mode=COMPARISON_NONE)
    )
    rx_analyses = _build_analyses(
        _analysis_context(run_mode="RX", comparison_mode=COMPARISON_NONE)
    )

    assert [analysis["id"] for analysis in tx_analyses] == ["TX_ABS"]
    assert [analysis["id"] for analysis in rx_analyses] == ["RX_ABS"]
    assert all(analysis["analysis_kind"] == "opportunity" for analysis in tx_analyses + rx_analyses)


@pytest.mark.parametrize(
    "comparison_mode",
    [
        COMPARISON_HARDWARE_AB,
        COMPARISON_REFERENCE_STATION,
        COMPARISON_LOCAL_NEIGHBORHOOD,
    ],
)
@pytest.mark.parametrize(
    ("run_mode", "self_test_mode", "expected_analysis_id"),
    [
        ("RX", SELF_TEST_RX, "RX_COMP"),
        ("TX", SELF_TEST_TX, "TX_COMP"),
    ],
)
def test_benchmark_builds_only_the_directional_compare_analysis(
    comparison_mode,
    run_mode,
    self_test_mode,
    expected_analysis_id,
):
    """Keep every benchmark run Compare-only in both analysis directions."""
    analyses = _build_analyses(
        _analysis_context(
            run_mode=run_mode,
            self_test_mode=self_test_mode,
            comparison_mode=comparison_mode,
        )
    )

    assert [analysis["id"] for analysis in analyses] == [expected_analysis_id]
    assert analyses[0]["analysis_kind"] == "comparison"
    assert analyses[0]["is_compare"] is True


def test_analysis_batch_builder_rejects_removed_all_band_context():
    with pytest.raises(ValueError, match="Choose one exact WSPR band"):
        _build_analyses(
            _analysis_context(
                run_mode="RX",
                comparison_mode=COMPARISON_NONE,
                band="All",
            )
        )


@pytest.mark.parametrize(
    ("overrides", "error_pattern"),
    [
        ({"callsign": "DL1\u00df"}, "Invalid Target Callsign"),
        ({"qth": "J\u013137"}, "valid target QTH locator"),
        ({"reference_callsign": "DL2\ufb00"}, "Invalid Reference Callsign"),
        ({"reference_qth": "J\u212a37"}, "four-character Reference QTH"),
    ],
)
def test_batch_builder_rejects_unicode_before_case_expansion(
    overrides,
    error_pattern,
):
    """Revalidate raw identities before any core normalization or SQL."""
    with pytest.raises(ValueError, match=error_pattern):
        _build_analyses(_analysis_context(**overrides))


def test_added_live_wspr_bands_build_numeric_opportunity_predicates():
    for band, band_value in {
        "LF": "-1",
        "MF": "0",
        "22m": "13",
        "8m": "40",
        "4m": "70",
    }.items():
        context = _analysis_context(
            run_mode="RX",
            comparison_mode=COMPARISON_NONE,
            band=band,
        )
        analyses = build_analysis_batches(
            context,
            START_TIME,
            END_TIME,
            47.0,
            8.0,
            f"AND band = '{band_value}'",
        )

        assert len(analyses) == 1
        assert analyses[0]["id"] == "RX_ABS"
        assert f"band = {band_value}" in analyses[0]["query"]


def test_tx_ab_schedule_sql_filters_compare_to_both_configured_starts():
    context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
        tx_ab_method=TX_AB_METHOD_SEQUENTIAL,
        qth="JN37UN",
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert "toMinute(time) % 10 = 0" in tx_compare["query"]
    assert "toMinute(time) % 10 = 2" in tx_compare["query"]
    assert tx_compare["query"].count(
        "tx_sign = 'DL1MKS' AND substring(tx_loc, 1, 4) = 'JN37'"
    ) == 2


def test_four_minute_tx_ab_schedule_uses_demo_query_contract():
    context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
        tx_ab_method=TX_AB_METHOD_SEQUENTIAL,
        tx_ab_repeat_interval_minutes=4,
        tx_ab_target_start_minute=2,
        tx_ab_reference_start_minute=0,
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert "toMinute(time) % 4 = 2" in tx_compare["query"]
    assert "toMinute(time) % 4 = 0" in tx_compare["query"]


def test_tx_ab_schedule_rejects_overlapping_starts_before_sql_is_built():
    context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
        tx_ab_method=TX_AB_METHOD_SEQUENTIAL,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=0,
    )

    with pytest.raises(ValueError, match="Invalid TX A/B schedule"):
        _build_analyses(context)


def test_tx_hardware_ab_defaults_to_simultaneous_fixed_reference_comparison():
    context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
        qth="JN37UN",
        reference_callsign="DL2XYZ/P",
        reference_qth="",
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert context.tx_ab_method == TX_AB_METHOD_SIMULTANEOUS
    assert tx_compare["is_sequential"] is False
    assert (
        "tx_sign = 'DL1MKS' AND substring(tx_loc, 1, 4) = 'JN37'"
        in tx_compare["query"]
    )
    assert (
        "tx_sign = 'DL2XYZ/P' AND substring(tx_loc, 1, 4) = 'JN37'"
        in tx_compare["query"]
    )
    assert "toMinute(time) %" not in tx_compare["query"]
    assert tx_compare["title"] == (
        "TX Compare: DL1MKS (Target) vs. DL2XYZ/P (Reference)"
    )


def test_sequential_tx_hardware_ab_preserves_shared_identity_and_schedule_title():
    context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
        tx_ab_method=TX_AB_METHOD_SEQUENTIAL,
        reference_callsign="",
        reference_qth="",
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert tx_compare["is_sequential"] is True
    assert tx_compare["query"].count(
        "tx_sign = 'DL1MKS' AND substring(tx_loc, 1, 4) = 'JN37'"
    ) == 2
    assert "toMinute(time) % 10 = 0" in tx_compare["query"]
    assert "toMinute(time) % 10 = 2" in tx_compare["query"]
    assert tx_compare["title"] == (
        "TX Compare: DL1MKS (Target) vs. DL1MKS (Reference)"
    )


@pytest.mark.parametrize(
    ("run_mode", "self_test_mode", "analysis_id"),
    [
        ("TX", SELF_TEST_TX, "TX_COMP"),
        ("RX", SELF_TEST_RX, "RX_COMP"),
    ],
)
def test_simultaneous_hardware_ab_reuses_fixed_reference_query_contract(
    run_mode,
    self_test_mode,
    analysis_id,
):
    reference_analysis = _analysis_by_id(
        _analysis_context(
            comparison_mode=COMPARISON_REFERENCE_STATION,
            run_mode=run_mode,
            self_test_mode=self_test_mode,
            qth="JN37UN",
            reference_callsign="DL2XYZ",
            reference_qth="JN37",
            reference_snr_correction_db=1.2,
        ),
        analysis_id,
    )
    hardware_analysis = _analysis_by_id(
        _analysis_context(
            comparison_mode=COMPARISON_HARDWARE_AB,
            tx_ab_method=TX_AB_METHOD_SIMULTANEOUS,
            run_mode=run_mode,
            self_test_mode=self_test_mode,
            qth="JN37UN",
            reference_callsign="DL2XYZ",
            reference_qth="",
            reference_snr_correction_db=1.2,
        ),
        analysis_id,
    )

    assert hardware_analysis["is_sequential"] is False
    assert hardware_analysis["query"] == reference_analysis["query"]
    assert hardware_analysis["title"] == reference_analysis["title"]


@pytest.mark.parametrize(
    ("self_test_mode", "tx_ab_method"),
    [
        (SELF_TEST_RX, TX_AB_METHOD_SIMULTANEOUS),
        (SELF_TEST_TX, TX_AB_METHOD_SIMULTANEOUS),
    ],
)
def test_hardware_ab_derives_reference_grid4_from_target_qth(
    self_test_mode,
    tx_ab_method,
):
    context = _analysis_context(
        run_mode=self_test_mode.upper(),
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=self_test_mode,
        tx_ab_method=tx_ab_method,
        qth="JN37UN",
        reference_callsign="DL2XYZ",
        reference_qth="JO62",
    )

    comparison = _analysis_by_id(
        context,
        "RX_COMP" if self_test_mode == SELF_TEST_RX else "TX_COMP",
    )

    identity_column = "rx" if self_test_mode == SELF_TEST_RX else "tx"
    assert (
        f"{identity_column}_sign = 'DL2XYZ' AND "
        f"substring({identity_column}_loc, 1, 4) = 'JN37'"
        in comparison["query"]
    )
    assert "'JO62'" not in comparison["query"]


def test_simultaneous_hardware_ab_rejects_identical_callsigns():
    context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
        reference_callsign="DL1MKS",
        reference_qth="",
    )

    with pytest.raises(
        ValueError,
        match="requires distinct Target and Reference callsigns",
    ):
        _build_analyses(context)


def test_tx_hardware_ab_rejects_unknown_method_before_query_construction():
    context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
        tx_ab_method="parallel-ish",
    )

    with pytest.raises(ValueError, match="Unknown TX Hardware A/B method"):
        _build_analyses(context)


def test_reference_station_requires_valid_reference_qth():
    context = _analysis_context(reference_qth="")

    with pytest.raises(ValueError, match="four-character Reference QTH"):
        _build_analyses(context)


def test_reference_station_rejects_grid6_reference_qth():
    """Keep the independently editable Reference selector exactly grid-4."""
    context = _analysis_context(reference_qth="JO62QM")

    with pytest.raises(ValueError, match="four-character Reference QTH"):
        _build_analyses(context)


def test_positive_reference_snr_correction_is_added_to_reference_side():
    context = _analysis_context(reference_snr_correction_db=1.6)

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert "maxIf(snr - power + 30, is_me = 1) AS snr_u_norm" in tx_compare["query"]
    assert "maxIf((snr - power + 30 + 1.6), is_me = 0) AS snr_r_norm" in tx_compare["query"]
    assert "maxIf((snr - power + 30 + 1.6), is_me = 1)" not in tx_compare["query"]


def test_reference_station_matching_uses_exact_callsign_and_grid4_per_side():
    context = _analysis_context(
        comparison_mode=COMPARISON_REFERENCE_STATION,
        reference_callsign="DL2XYZ",
        qth="JN37UN",
        reference_qth="JO62",
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert (
        "tx_sign = 'DL1MKS' AND substring(tx_loc, 1, 4) = 'JN37'"
        in tx_compare["query"]
    )
    assert (
        "tx_sign = 'DL2XYZ' AND substring(tx_loc, 1, 4) = 'JO62'"
        in tx_compare["query"]
    )
    assert tx_compare["query"].count("substring(tx_loc, 1, 4) = 'JN37'") == 1
    assert tx_compare["query"].count("substring(tx_loc, 1, 4) = 'JO62'") == 1
    assert "tx_sign LIKE 'DL1MKS%'" not in tx_compare["query"]
    assert "tx_sign LIKE 'DL2XYZ%'" not in tx_compare["query"]


def test_rx_reference_station_constrains_each_side_to_its_configured_grid4():
    context = _analysis_context(
        run_mode="RX",
        comparison_mode=COMPARISON_REFERENCE_STATION,
        reference_callsign="DL2XYZ",
        qth="jn37un",
        reference_qth="jo62",
    )

    rx_compare = _analysis_by_id(context, "RX_COMP")

    assert (
        "rx_sign = 'DL1MKS' AND substring(rx_loc, 1, 4) = 'JN37'"
        in rx_compare["query"]
    )
    assert (
        "rx_sign = 'DL2XYZ' AND substring(rx_loc, 1, 4) = 'JO62'"
        in rx_compare["query"]
    )
    assert rx_compare["query"].count("substring(rx_loc, 1, 4) = 'JN37'") == 1
    assert rx_compare["query"].count("substring(rx_loc, 1, 4) = 'JO62'") == 1


@pytest.mark.parametrize(
    ("target_callsign", "reference_callsign"),
    [
        ("DL1MKS/P", "DL2XYZ/QRP"),
        ("DL1MKS-1", "DL2XYZ/P"),
        ("DL1MKS/P", "DL2XYZ-1"),
    ],
)
def test_reference_station_matching_accepts_exact_suffix_callsigns_per_side(
    target_callsign,
    reference_callsign,
):
    context = _analysis_context(
        comparison_mode=COMPARISON_REFERENCE_STATION,
        callsign=target_callsign,
        reference_callsign=reference_callsign,
        reference_qth="JO62",
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert f"tx_sign = '{target_callsign}'" in tx_compare["query"]
    assert f"tx_sign = '{reference_callsign}'" in tx_compare["query"]
    assert "tx_sign LIKE" not in tx_compare["query"]


def test_rx_hardware_ab_matching_uses_exact_callsigns_to_protect_suffixes():
    context = _analysis_context(
        run_mode="RX",
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_RX,
        reference_callsign="DL1MKS/P",
        reference_qth="",
    )

    rx_compare = _analysis_by_id(context, "RX_COMP")

    assert "rx_sign = 'DL1MKS'" in rx_compare["query"]
    assert "rx_sign = 'DL1MKS/P'" in rx_compare["query"]
    assert (
        "rx_sign = 'DL1MKS' AND substring(rx_loc, 1, 4) = 'JN37'"
        in rx_compare["query"]
    )
    assert (
        "rx_sign = 'DL1MKS/P' AND substring(rx_loc, 1, 4) = 'JN37'"
        in rx_compare["query"]
    )
    assert rx_compare["query"].count("substring(rx_loc, 1, 4) = 'JN37'") == 2
    assert "rx_sign LIKE 'DL1MKS%'" not in rx_compare["query"]
    assert "rx_sign LIKE 'DL1MKS/P%'" not in rx_compare["query"]


def test_rx_hardware_ab_matching_accepts_one_exact_reference_suffix_callsign():
    context = _analysis_context(
        run_mode="RX",
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_RX,
        callsign="DL1MKS/1",
        reference_callsign="DL1MKS/P",
        reference_qth="",
    )

    rx_compare = _analysis_by_id(context, "RX_COMP")

    assert (
        "rx_sign = 'DL1MKS/1' AND substring(rx_loc, 1, 4) = 'JN37'"
        in rx_compare["query"]
    )
    assert (
        "rx_sign = 'DL1MKS/P' AND substring(rx_loc, 1, 4) = 'JN37'"
        in rx_compare["query"]
    )
    assert "rx_sign LIKE 'DL1MKS%'" not in rx_compare["query"]


def test_local_median_neighborhood_uses_station_weighted_reference_median_sql():
    context = _analysis_context(
        comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
        local_benchmark=LOCAL_BENCHMARK_MEDIAN,
        neighborhood_radius_km=100,
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert tx_compare["is_local_median"] is True
    assert "quantileExactInclusive(0.5)((snr - power + 30 + 0.0)) AS station_snr_norm" in tx_compare["query"]
    assert "GROUP BY time_slot, peer_sign, peer_grid, local_sign, local_grid" in tx_compare["query"]
    assert "quantileExactInclusiveIf(0.5)(station_snr_norm, is_me = 0) AS snr_r_norm" in tx_compare["query"]
    assert "countIf(is_me = 0) AS has_r" in tx_compare["query"]
    assert "groupArrayIf(tuple(local_sign, local_grid, local_dist, station_snr_norm), is_me = 0) AS ref_detail_rows" in tx_compare["query"]
    assert "quantileExactInclusiveIf(0.5)((snr - power + 30 + 0.0), is_me = 0) AS snr_r_norm" not in tx_compare["query"]


def test_local_neighborhood_excludes_only_the_exact_target_callsign():
    context = _analysis_context(
        comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
        local_benchmark=LOCAL_BENCHMARK_MEDIAN,
        neighborhood_radius_km=100,
        callsign="DL1MKS/P",
    )

    tx_compare = _analysis_by_id(context, "TX_COMP")

    assert (
        "tx_sign = 'DL1MKS/P' AND substring(tx_loc, 1, 4) = 'JN37'"
        in tx_compare["query"]
    )
    assert tx_compare["query"].count("substring(tx_loc, 1, 4) = 'JN37'") == 1
    assert "tx_sign != 'DL1MKS/P'" in tx_compare["query"]
    assert "geoDistance(8.0, 47.0, tx_lon, tx_lat)" in tx_compare["query"]
    assert "tx_sign NOT LIKE 'DL1MKS%'" not in tx_compare["query"]


def test_rx_local_median_neighborhood_weights_receiver_reference_identities():
    context = _analysis_context(
        run_mode="RX",
        comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
        local_benchmark=LOCAL_BENCHMARK_MEDIAN,
        neighborhood_radius_km=100,
    )

    rx_compare = _analysis_by_id(context, "RX_COMP")

    assert (
        "rx_sign = 'DL1MKS' AND substring(rx_loc, 1, 4) = 'JN37'"
        in rx_compare["query"]
    )
    assert rx_compare["query"].count("substring(rx_loc, 1, 4) = 'JN37'") == 1
    assert "geoDistance(8.0, 47.0, rx_lon, rx_lat)" in rx_compare["query"]
    assert "tx_sign AS peer_sign" in rx_compare["query"]
    assert "rx_sign AS local_sign" in rx_compare["query"]
    assert "rx_loc AS local_grid" in rx_compare["query"]
    assert "quantileExactInclusive(0.5)((snr - power + 30 + 0.0)) AS station_snr_norm" in rx_compare["query"]
    assert "GROUP BY time_slot, peer_sign, peer_grid, local_sign, local_grid" in rx_compare["query"]


@pytest.mark.parametrize(
    ("run_mode", "analysis_id"),
    [("TX", "TX_COMP"), ("RX", "RX_COMP")],
)
def test_compare_queries_use_half_open_analysis_interval(run_mode, analysis_id):
    context = _analysis_context(run_mode=run_mode)

    comparison = _analysis_by_id(context, analysis_id)

    for query in (comparison["query"], comparison["legacy_query"]):
        assert query.count("time >= '2026-05-27 00:00:00'") == 2
        assert query.count("time < '2026-05-28 00:00:00'") == 2
        assert "time BETWEEN" not in query


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
        tx_ab_method=TX_AB_METHOD_SEQUENTIAL,
    )
    analysis = {
        "analysis_kind": "comparison",
        "is_compare": True,
        "is_sequential": True,
        "title": "sequential",
    }
    rows = pd.DataFrame({
        "time": [START_TIME, START_TIME + timedelta(minutes=2)],
        "is_me": [1, 0],
        "stat_val": [1.0, 0.0],
        "has_u": [1, 0],
    })

    filtered, warning = apply_post_fetch_filters(rows, analysis, context, 47.0, 8.0, T["en"])

    assert warning is None
    assert len(filtered) == 2
    assert filtered["tx_ab_pair_id"].nunique() == 1
