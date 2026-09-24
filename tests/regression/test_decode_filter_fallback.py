from datetime import datetime, timezone

import pandas as pd
import pytest

from config import BAND_MAP, DEMO_PROFILES
from core.analysis_context import AnalysisContext
from core.presentation_context import PresentationContext
from core.analysis_runner import (
    DECODE_FILTER_LEGACY,
    DECODE_FILTER_STRICT,
    allows_legacy_decode_fallback,
    build_analysis_batches,
    should_retry_without_decode_filter,
    without_decode_code_filter,
    with_decode_fallback,
)
from i18n import T


def _analysis(kind="comparison"):
    return {
        "analysis_kind": kind,
        "decode_filter_mode": DECODE_FILTER_STRICT,
        "legacy_query": "SELECT * FROM wspr.rx",
        "analysis_start_utc": datetime(2017, 4, 1, tzinfo=timezone.utc),
        "analysis_end_utc": datetime(2017, 5, 1, tzinfo=timezone.utc),
    }


def test_without_decode_code_filter_removes_strict_predicate_forms():
    query = (
        "SELECT * FROM wspr.rx\n"
        "WHERE code = 1\n"
        "  AND tx_sign = 'KP4MD'\n"
        "      AND code = 1"
        " AND code = 1"
    )

    legacy = without_decode_code_filter(query)

    assert "code = 1" not in legacy
    assert "tx_sign = 'KP4MD'" in legacy


def test_bounded_decode_fallback_preserves_outer_limit_and_format():
    analysis = with_decode_fallback({
        **_analysis(),
        "query": (
            "SELECT * FROM wspr.rx WHERE code = 1 AND tx_sign = 'KP4MD' "
            "FORMAT CSVWithNames"
        )
    })

    assert "code = 1" in analysis["query"]
    assert "code = 1" not in analysis["legacy_query"]
    for query in (analysis["query"], analysis["legacy_query"]):
        assert query.count("LIMIT 1000001") == 1
        assert query.endswith("LIMIT 1000001\nFORMAT CSVWithNames")


def test_retry_compare_only_when_target_side_is_absent():
    analysis = _analysis("comparison")

    assert should_retry_without_decode_filter(None, analysis)
    assert should_retry_without_decode_filter(pd.DataFrame(), analysis)
    assert should_retry_without_decode_filter(
        pd.DataFrame({"has_u": [0], "has_r": [1]}),
        analysis,
    )
    assert not should_retry_without_decode_filter(
        pd.DataFrame({"has_u": [1], "has_r": [0]}),
        analysis,
    )
    assert not should_retry_without_decode_filter(
        pd.DataFrame({"is_me": [1, 0]}),
        analysis,
    )


def test_retry_opportunity_only_when_target_side_is_absent():
    analysis = _analysis("opportunity")

    assert should_retry_without_decode_filter(
        pd.DataFrame({"target_seen": [0], "external_seen": [1]}),
        analysis,
    )
    assert not should_retry_without_decode_filter(
        pd.DataFrame({"target_seen": [1], "external_seen": [0]}),
        analysis,
    )

    legacy_analysis = dict(analysis, decode_filter_mode=DECODE_FILTER_LEGACY)
    assert not should_retry_without_decode_filter(
        pd.DataFrame({"target_seen": [0], "external_seen": [1]}),
        legacy_analysis,
    )


@pytest.mark.parametrize(
    ("start", "end", "is_allowed"),
    [
        ("2021-12-30T00:00:00+00:00", "2021-12-31T23:59:59+00:00", True),
        ("2021-12-31T00:00:00+00:00", "2022-01-01T00:00:00+00:00", False),
        ("2021-12-31T00:00:00+00:00", "2022-01-02T00:00:00+00:00", False),
        ("2022-01-01T00:00:00+00:00", "2022-01-02T00:00:00+00:00", False),
        ("2026-09-01T00:00:00+00:00", "2026-09-02T00:00:00+00:00", False),
        ("2021-12-31T00:00:00+01:00", "2022-01-01T00:30:00+01:00", True),
        ("2021-12-31T00:00:00-01:00", "2021-12-31T23:30:00-01:00", False),
        ("2021-12-30T00:00:00", "2021-12-31T00:00:00", True),
        ("2021-12-31T00:00:00", "2022-01-01T00:00:00", False),
    ],
)
def test_legacy_fallback_requires_the_complete_window_before_cutoff(start, end, is_allowed):
    analysis = dict(
        _analysis(),
        analysis_start_utc=datetime.fromisoformat(start),
        analysis_end_utc=datetime.fromisoformat(end),
        query="SELECT * FROM wspr.rx WHERE code = 1 AND band = 7 FORMAT CSVWithNames",
    )
    # Execution must reject a disallowed window even if an old plan has legacy SQL.
    assert allows_legacy_decode_fallback(analysis) is is_allowed
    assert should_retry_without_decode_filter(pd.DataFrame(), analysis) is is_allowed
    planned = with_decode_fallback(analysis)
    assert "code = 1" in planned["query"]
    assert ("legacy_query" in planned) is is_allowed
    assert ("legacy_decode_filter_mode" in planned) is is_allowed
    assert not should_retry_without_decode_filter(pd.DataFrame({"has_u": [1]}), planned)


@pytest.mark.parametrize("boundaries", [{}, {"analysis_start_utc": "2017-04-01", "analysis_end_utc": "2017-05-01"}])
def test_unverified_window_never_authorizes_legacy_retry(boundaries):
    assert not allows_legacy_decode_fallback(boundaries)


@pytest.mark.parametrize("run_mode", ["TX", "RX"])
@pytest.mark.parametrize("comparison_mode", ["none", "reference_station", "local_neighborhood", "hardware_ab"])
@pytest.mark.parametrize(
    ("start", "end", "is_allowed"),
    [
        ("2021-12-30", "2021-12-31", True),
        ("2021-12-31", "2022-01-01", False),
        ("2021-12-31", "2022-01-02", False),
        ("2022-01-01", "2022-01-02", False),
    ],
)
def test_every_analysis_style_plans_only_eligible_legacy_queries(run_mode, comparison_mode, start, end, is_allowed):
    context = AnalysisContext(
        run_mode=run_mode, callsign="G3ZIL", qth="IO90HW", band="40m",
        comparison_mode=comparison_mode, reference_callsign="G4HZX", reference_qth="IO91",
        self_test_mode=run_mode.lower(), tx_ab_method="sequential",
    )
    start_utc = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
    end_utc = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
    plan = build_analysis_batches(
        context, start_utc, end_utc, 50.0, -1.0, "AND band = '7'",
        presentation_context=PresentationContext(labels=T["en"], solar_label="All"),
    )[0]
    assert plan.analysis_start_utc == start_utc
    assert plan.analysis_end_utc == end_utc
    assert "code = 1" in plan.query
    assert plan.decode_filter_mode == DECODE_FILTER_STRICT
    assert bool(plan.legacy_query) is is_allowed
    assert should_retry_without_decode_filter(pd.DataFrame(), plan) is is_allowed


@pytest.mark.parametrize("profile_id", ["griffiths_squibb_fig3", "griffiths_squibb_rx_performance", "griffiths_squibb_fig6", "milazzo_tx_buddy"])
def test_historical_demo_profiles_retain_strict_first_legacy_compatibility(profile_id):
    settings = DEMO_PROFILES[profile_id]["configuration"]["settings"]
    core = settings["core_parameters"]
    comparison = settings["comparison_parameters"]
    context = AnalysisContext(
        run_mode=core["analysis_direction"].upper(), callsign=core["callsign"],
        qth=core["qth"], band=core["band"], comparison_mode=comparison["mode"],
        reference_callsign=comparison.get("reference_callsign", ""),
        reference_qth=comparison.get("reference_qth", ""),
    )
    plan = build_analysis_batches(
        context,
        datetime.fromisoformat(core["time_selection"]["start_utc"]),
        datetime.fromisoformat(core["time_selection"]["end_utc"]),
        50.0, -1.0, f"AND band = '{BAND_MAP[context.band]}'",
        presentation_context=PresentationContext(labels=T["en"], solar_label="All"),
    )[0]
    assert "code = 1" in plan.query
    assert plan.decode_filter_mode == DECODE_FILTER_STRICT
    assert should_retry_without_decode_filter(pd.DataFrame(), plan)
    assert "code = 1" not in plan.for_legacy_query().query
    assert plan.for_legacy_query().decode_filter_mode == DECODE_FILTER_LEGACY
