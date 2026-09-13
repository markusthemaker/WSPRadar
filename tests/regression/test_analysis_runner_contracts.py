from datetime import datetime, timedelta, timezone
from contextlib import closing
from dataclasses import FrozenInstanceError, replace
import sqlite3

import pandas as pd
import pytest
from pyproj import Geod

from config import MAX_ANALYSIS_RESULT_ROWS
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
from core.analysis_runner import (
    AnalysisConfigError,
    apply_post_fetch_filters,
    build_analysis_batches,
)
from core.analysis_plan import AnalysisPlan, DECODE_FILTER_LEGACY, DECODE_FILTER_STRICT
from core.presentation_context import PresentationContext
from core.query_limits import apply_analysis_result_row_limit
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
        presentation_context=PresentationContext(
            labels=T["en"],
            solar_label=T["en"]["opt_solar_all"].split()[0],
        ),
    )


def _analysis_by_id(context, analysis_id):
    return next(analysis for analysis in _build_analyses(context) if analysis["id"] == analysis_id)


def test_no_benchmark_builds_only_the_directional_performance_analysis():
    tx_analyses = _build_analyses(
        _analysis_context(run_mode="TX", comparison_mode=COMPARISON_NONE)
    )
    rx_analyses = _build_analyses(
        _analysis_context(run_mode="RX", comparison_mode=COMPARISON_NONE)
    )

    assert [analysis["id"] for analysis in tx_analyses] == ["TX_PERFORMANCE"]
    assert [analysis["id"] for analysis in rx_analyses] == ["RX_PERFORMANCE"]
    assert all(
        analysis["result_family"] == "performance"
        for analysis in tx_analyses + rx_analyses
    )
    assert all(analysis["analysis_kind"] == "opportunity" for analysis in tx_analyses + rx_analyses)
    assert all(
        analysis["absolute_method_version"] == "opportunity-v2"
        for analysis in tx_analyses + rx_analyses
    )


@pytest.mark.parametrize(
    "context",
    [
        _analysis_context(run_mode="TX", comparison_mode=COMPARISON_NONE),
        _analysis_context(run_mode="RX", comparison_mode=COMPARISON_NONE),
        _analysis_context(run_mode="TX", comparison_mode=COMPARISON_REFERENCE_STATION),
        _analysis_context(run_mode="RX", comparison_mode=COMPARISON_REFERENCE_STATION),
        _analysis_context(
            run_mode="TX",
            self_test_mode=SELF_TEST_TX,
            comparison_mode=COMPARISON_HARDWARE_AB,
            tx_ab_method=TX_AB_METHOD_SEQUENTIAL,
        ),
        _analysis_context(
            run_mode="RX",
            comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
            local_benchmark=LOCAL_BENCHMARK_MEDIAN,
        ),
    ],
)
def test_every_analysis_query_has_one_outer_result_row_sentinel(context):
    """Bound each complete strict and legacy result after unions and grouping."""
    analysis = _build_analyses(context)[0]
    assert isinstance(analysis, AnalysisPlan)
    sentinel_clause = f"LIMIT {MAX_ANALYSIS_RESULT_ROWS + 1}"

    for query in (analysis["query"], analysis["legacy_query"]):
        expected_format = (
            "Parquet"
            if analysis["response_format"] == "parquet"
            else "CSVWithNames"
        )
        assert query.startswith("SELECT *\nFROM (\n")
        assert query.count("LIMIT ") == 1
        assert query.count("FORMAT ") == 1
        assert query.rfind(sentinel_clause) > query.rfind("UNION ALL")
        assert query.rfind(sentinel_clause) > query.rfind("GROUP BY")
        assert query.rfind("FORMAT ") > query.rfind(sentinel_clause)
        assert query.endswith(
            f")\n{sentinel_clause}\nFORMAT {expected_format}"
        )


def test_analysis_plan_keeps_sql_and_optional_mapping_fields_unchanged():
    """Preserve exact query text and optional-field absence across the boundary."""
    analysis = _build_analyses(_analysis_context(comparison_mode=COMPARISON_NONE))[0]
    serialized_plan = dict(analysis)
    restored_plan = AnalysisPlan.from_mapping(serialized_plan)

    assert dict(restored_plan) == serialized_plan
    assert restored_plan.query is serialized_plan["query"]
    assert restored_plan.legacy_query is serialized_plan["legacy_query"]
    assert AnalysisPlan.from_mapping(restored_plan) is restored_plan
    assert "analysis_start_utc" not in restored_plan
    assert "analysis_end_utc" not in restored_plan
    assert "is_local_median" not in restored_plan
    assert restored_plan.get("is_local_median", False) is False
    with pytest.raises(KeyError):
        restored_plan["analysis_start_utc"]


def test_analysis_plan_replacements_preserve_strict_plan_and_time_window():
    """Keep query selection distinct from presentation and restored provenance."""
    strict_plan = _build_analyses(_analysis_context())[0]
    legacy_plan = strict_plan.for_legacy_query()
    restored_plan = strict_plan.with_decode_filter_mode(DECODE_FILTER_LEGACY)
    translated_plan = replace(strict_plan, title="Lokalisierter Benchmark")

    assert strict_plan.decode_filter_mode == DECODE_FILTER_STRICT
    assert legacy_plan.decode_filter_mode == DECODE_FILTER_LEGACY
    assert legacy_plan.query == strict_plan.legacy_query
    assert restored_plan.query == strict_plan.query
    assert translated_plan.query == strict_plan.query
    assert translated_plan.legacy_query == strict_plan.legacy_query
    assert legacy_plan.analysis_start_utc is strict_plan.analysis_start_utc
    assert legacy_plan.analysis_end_utc is strict_plan.analysis_end_utc
    assert strict_plan.with_decode_filter_mode(DECODE_FILTER_STRICT) is strict_plan
    with pytest.raises(FrozenInstanceError):
        strict_plan.query = "changed"
    with pytest.raises(TypeError):
        strict_plan["query"] = "changed"


@pytest.mark.parametrize(
    ("field_name", "replacement", "message"),
    [
        ("is_compare", False, "Benchmark comparison"),
        ("is_sequential", 1, "boolean"),
        ("result_family", "performance", "Benchmark comparison"),
        ("response_format", "parquet", "csv responses"),
        ("analysis_kind", "unknown", "analysis_kind"),
        ("absolute_mode", "TX", "Performance method"),
        ("decode_filter_mode", "unknown", "decode_filter_mode"),
        ("legacy_decode_filter_mode", "unknown", "legacy_no_code"),
        ("analysis_start_utc", END_TIME, "end must be after"),
        ("analysis_end_utc", None, "time window"),
    ],
)
def test_analysis_plan_rejects_inconsistent_comparison_contracts(
    field_name, replacement, message,
):
    """Reject inconsistent scientific or provenance facts before acquisition."""
    serialized_plan = dict(_build_analyses(_analysis_context())[0])
    serialized_plan[field_name] = replacement

    with pytest.raises((TypeError, ValueError), match=message):
        AnalysisPlan.from_mapping(serialized_plan)


@pytest.mark.parametrize("field_name", ("result_family", "is_compare", "decode_filter_mode"))
def test_analysis_plan_rejects_missing_required_fields(field_name):
    serialized_plan = dict(_build_analyses(_analysis_context())[0])
    serialized_plan.pop(field_name)

    with pytest.raises(TypeError, match=field_name):
        AnalysisPlan.from_mapping(serialized_plan)


@pytest.mark.parametrize(
    ("field_name", "replacement", "message"),
    [
        ("is_compare", True, "Performance semantics"),
        ("is_sequential", True, "Performance semantics"),
        ("is_local_median", True, "Local Median"),
        ("absolute_mode", None, "absolute_mode"),
        ("absolute_method_version", None, "absolute_method_version"),
    ],
)
def test_analysis_plan_rejects_inconsistent_opportunity_contracts(
    field_name, replacement, message,
):
    serialized_plan = dict(_build_analyses(_analysis_context(comparison_mode=COMPARISON_NONE))[0])
    serialized_plan[field_name] = replacement

    with pytest.raises(ValueError, match=message):
        AnalysisPlan.from_mapping(serialized_plan)


def test_result_limit_wraps_complete_union_and_moves_terminal_format():
    """Keep the sentinel outside a full union and normalize its SQL terminator."""
    bounded_query = apply_analysis_result_row_limit(
        "SELECT 1 AS value UNION ALL SELECT 2 AS value FORMAT CSVWithNames;",
        max_result_rows=7,
    )

    assert bounded_query == (
        "SELECT *\n"
        "FROM (\n"
        "SELECT 1 AS value UNION ALL SELECT 2 AS value\n"
        ")\n"
        "LIMIT 8\n"
        "FORMAT CSVWithNames"
    )


@pytest.mark.parametrize(
    ("sql_query", "maximum_rows", "expected_exception"),
    [
        ("SELECT 1 FORMAT CSVWithNames", True, TypeError),
        ("SELECT 1 FORMAT CSVWithNames", 1.5, TypeError),
        ("SELECT 1 FORMAT CSVWithNames", 0, ValueError),
        ("SELECT 1 FORMAT CSVWithNames", -1, ValueError),
        ("", 1, ValueError),
        ("SELECT 1", 1, ValueError),
    ],
)
def test_result_limit_rejects_invalid_policy_or_unfinished_sql(
    sql_query,
    maximum_rows,
    expected_exception,
):
    """Fail closed when the safety policy or terminal FORMAT is invalid."""
    with pytest.raises(expected_exception):
        apply_analysis_result_row_limit(
            sql_query,
            max_result_rows=maximum_rows,
        )


def test_letter_only_reporting_identifier_builds_exact_rx_success_query():
    """Query an exact archive reporter such as KFS without prefix matching."""
    rx_analysis = _analysis_by_id(
        _analysis_context(
            run_mode="RX",
            comparison_mode=COMPARISON_NONE,
            callsign=" kfs ",
        ),
        "RX_PERFORMANCE",
    )

    assert "rx_sign = 'KFS'" in rx_analysis["query"]
    assert "rx_sign != 'KFS'" in rx_analysis["query"]
    assert "rx_sign LIKE 'KFS%'" not in rx_analysis["query"]


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
        ("RX", SELF_TEST_RX, "RX_BENCHMARK"),
        ("TX", SELF_TEST_TX, "TX_BENCHMARK"),
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
            presentation_context=PresentationContext(
                labels=T["en"],
                solar_label=T["en"]["opt_solar_all"].split()[0],
            ),
        )

        assert len(analyses) == 1
        assert analyses[0]["id"] == "RX_PERFORMANCE"
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

    tx_compare = _analysis_by_id(context, "TX_BENCHMARK")

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

    tx_compare = _analysis_by_id(context, "TX_BENCHMARK")

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

    tx_compare = _analysis_by_id(context, "TX_BENCHMARK")

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
        "TX Benchmark: DL1MKS (Target) vs. DL2XYZ/P (Reference)"
    )


def test_sequential_tx_hardware_ab_preserves_shared_identity_and_schedule_title():
    context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        self_test_mode=SELF_TEST_TX,
        tx_ab_method=TX_AB_METHOD_SEQUENTIAL,
        reference_callsign="",
        reference_qth="",
    )

    tx_compare = _analysis_by_id(context, "TX_BENCHMARK")

    assert tx_compare["is_sequential"] is True
    assert tx_compare["query"].count(
        "tx_sign = 'DL1MKS' AND substring(tx_loc, 1, 4) = 'JN37'"
    ) == 2
    assert "toMinute(time) % 10 = 0" in tx_compare["query"]
    assert "toMinute(time) % 10 = 2" in tx_compare["query"]
    assert tx_compare["title"] == (
        "TX Benchmark: DL1MKS (Target) vs. DL1MKS (Reference)"
    )


@pytest.mark.parametrize(
    ("run_mode", "self_test_mode", "analysis_id"),
    [
        ("TX", SELF_TEST_TX, "TX_BENCHMARK"),
        ("RX", SELF_TEST_RX, "RX_BENCHMARK"),
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
        "RX_BENCHMARK" if self_test_mode == SELF_TEST_RX else "TX_BENCHMARK",
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

    tx_compare = _analysis_by_id(context, "TX_BENCHMARK")

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

    tx_compare = _analysis_by_id(context, "TX_BENCHMARK")

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

    rx_compare = _analysis_by_id(context, "RX_BENCHMARK")

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

    tx_compare = _analysis_by_id(context, "TX_BENCHMARK")

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

    rx_compare = _analysis_by_id(context, "RX_BENCHMARK")

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

    rx_compare = _analysis_by_id(context, "RX_BENCHMARK")

    assert (
        "rx_sign = 'DL1MKS/1' AND substring(rx_loc, 1, 4) = 'JN37'"
        in rx_compare["query"]
    )
    assert (
        "rx_sign = 'DL1MKS/P' AND substring(rx_loc, 1, 4) = 'JN37'"
        in rx_compare["query"]
    )
    assert "rx_sign LIKE 'DL1MKS%'" not in rx_compare["query"]


@pytest.mark.parametrize("run_mode", ["RX", "TX"])
@pytest.mark.parametrize("local_benchmark", ["local_best", "unknown", "", None, []])
def test_local_neighborhood_rejects_unsupported_method_before_query_preparation(
    run_mode,
    local_benchmark,
):
    """Reject explicit invalid local methods before labels, dates, or SQL are used."""
    context = _analysis_context(
        run_mode=run_mode,
        comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
        local_benchmark=local_benchmark,
    )

    with pytest.raises(AnalysisConfigError, match="local_benchmark.*local_median"):
        build_analysis_batches(context, None, None, None, None, None)


@pytest.mark.parametrize("run_mode", ["RX", "TX"])
def test_fixed_reference_keeps_maximum_consolidation(run_mode):
    """Keep fixed-reference consolidation independent of the local median method."""
    comparison = _analysis_by_id(
        _analysis_context(run_mode=run_mode),
        f"{run_mode}_BENCHMARK",
    )

    for query in (comparison["query"], comparison["legacy_query"]):
        assert "maxIf((snr - power + 30 + 0.0), is_me = 0) AS snr_r_norm" in query
        assert "argMaxIf(local_sign, (snr - power + 30 + 0.0), is_me = 0)" in query
        assert "station_snr_norm" not in query
    assert comparison["is_local_median"] is False


def test_local_median_neighborhood_uses_station_weighted_reference_median_sql():
    context = _analysis_context(
        comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
        local_benchmark=LOCAL_BENCHMARK_MEDIAN,
        neighborhood_radius_km=100,
    )

    tx_compare = _analysis_by_id(context, "TX_BENCHMARK")

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

    tx_compare = _analysis_by_id(context, "TX_BENCHMARK")

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

    rx_compare = _analysis_by_id(context, "RX_BENCHMARK")

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


@pytest.mark.parametrize("run_mode", ["TX", "RX"])
@pytest.mark.parametrize(
    ("center_latitude", "center_longitude", "radius_km", "bearing_degrees"),
    [
        (47.0, 8.0, 100, 45.0),
        (51.5, 179.0, 200, 90.0),
        (51.5, -179.0, 200, -90.0),
        (85.0, 10.0, 250, 69.0),
        (89.5, 45.0, 100, 0.0),
        (-89.5, -45.0, 100, 180.0),
        (0.0, 30.0, 10, 45.0),
    ],
)
def test_local_neighborhood_sql_retains_circle_membership_and_other_filters(
    run_mode, center_latitude, center_longitude, radius_km, bearing_degrees
):
    """Execute actual Reference predicates with an independent distance oracle.

    SQLite exercises the generated boolean SQL, while WGS84 geodesics place
    reports just inside/outside the circle. This checks the query wiring and
    unchanged cutoff, not ClickHouse's own distance approximation accuracy.
    """
    geodesic = Geod(ellps="WGS84")
    comparisons = build_analysis_batches(
        _analysis_context(
            run_mode=run_mode,
            comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
            local_benchmark=LOCAL_BENCHMARK_MEDIAN,
            neighborhood_radius_km=radius_km,
            exclude_special_callsigns=False,
        ),
        START_TIME, END_TIME, center_latitude, center_longitude,
        "AND band = '14'",
        presentation_context=PresentationContext(
            labels=T["en"], solar_label=T["en"]["opt_solar_all"].split()[0]
        ),
    )
    comparison = next(
        analysis for analysis in comparisons if analysis["id"] == f"{run_mode}_BENCHMARK"
    )
    local_prefix = run_mode.lower()
    remote_prefix = "rx" if run_mode == "TX" else "tx"
    observations = []
    for station_name, distance_metres in (
        ("inside", radius_km * 100.0),
        ("inside_edge", radius_km * 1000.0 - 1.0),
        ("outside_edge", radius_km * 1000.0 + 1.0),
        ("outside", radius_km * 2000.0),
    ):
        longitude, latitude, _ = geodesic.fwd(
            center_longitude, center_latitude, bearing_degrees, distance_metres
        )
        observations.append((
            station_name, "DL2XYZ", latitude, longitude, 40.0,
            "14", "2026-05-27 12:00:00", 1,
        ))
    inside_edge = observations[1]
    observations.extend([
        ("target", "DL1MKS", *inside_edge[2:]),
        ("wrong_band", *inside_edge[1:5], "7", *inside_edge[6:]),
        ("wrong_time", *inside_edge[1:6], "2026-05-28 12:00:00", 1),
        ("legacy_decode", *inside_edge[1:7], 2),
    ])

    def wgs84_distance(longitude_0, latitude_0, longitude_1, latitude_1):
        """Supply independently calculated metres to the generated SQL cutoff."""
        return geodesic.inv(longitude_0, latitude_0, longitude_1, latitude_1)[2]

    with closing(sqlite3.connect(":memory:")) as connection:
        connection.create_function("geoDistance", 4, wgs84_distance)
        connection.execute(
            f"CREATE TABLE observations (name TEXT, {local_prefix}_sign TEXT, "
            f"{local_prefix}_lat REAL, {local_prefix}_lon REAL, {remote_prefix}_lat REAL, "
            "band TEXT, time TEXT, code INTEGER)"
        )
        connection.executemany("INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?, ?, ?)", observations)
        for query_key in ("query", "legacy_query"):
            reference_predicate = comparison[query_key].split("FROM wspr.rx WHERE ")[2].split(" GROUP BY ")[0]
            assert (
                f"geoDistance({center_longitude}, {center_latitude}, "
                f"{local_prefix}_lon, {local_prefix}_lat) <= {radius_km * 1000}"
                in reference_predicate
            )
            selected_names = {
                row[0] for row in connection.execute(
                    f"SELECT name FROM observations WHERE {reference_predicate}"
                )
            }
            expected_names = {"inside", "inside_edge"}
            if query_key == "legacy_query":
                expected_names.add("legacy_decode")
            assert selected_names == expected_names


@pytest.mark.parametrize(
    ("run_mode", "analysis_id"),
    [("TX", "TX_BENCHMARK"), ("RX", "RX_BENCHMARK")],
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
