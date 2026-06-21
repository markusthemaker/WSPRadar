import pandas as pd

from core.analysis_runner import (
    DECODE_FILTER_LEGACY,
    DECODE_FILTER_STRICT,
    should_retry_without_decode_filter,
    without_decode_code_filter,
)


def _analysis(kind="comparison"):
    return {
        "analysis_kind": kind,
        "decode_filter_mode": DECODE_FILTER_STRICT,
        "legacy_query": "SELECT * FROM wspr.rx",
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
