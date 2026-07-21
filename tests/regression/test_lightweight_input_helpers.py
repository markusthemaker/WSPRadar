from datetime import datetime, timezone

import pytest

from core import input_validation, math_utils, time_utils


@pytest.mark.parametrize(
    "callsign",
    [
        "w1a",
        "DL1MKS",
        "SK0WE/P",
        "EA8/DL1ABC/P",
        "VK2FXXX/MM",
        "DL1MKS-1",
        "DL1MKS-P",
        "EA8/DL1ABC-1",
        "DL1MKS/P-1",
    ],
)
def test_dependency_free_callsign_validation_accepts_plausible_archive_tokens(
    callsign,
):
    """Accept plausible exact callsign tokens, including portable affixes."""
    assert input_validation.is_valid_callsign(callsign)


@pytest.mark.parametrize(
    "callsign",
    [
        "ABC",
        "123",
        "///",
        "/DL1ABC",
        "DL1ABC/",
        "DL1ABC//P",
        "-DL1MKS",
        "DL1MKS-",
        "DL1MKS--1",
        "DL1MKS-1-2",
        "DL1MKS-1/P",
        "DL1MKS/-1",
        "ABC-1",
        "123-P",
        "DL1ABC'; DROP TABLE spots",
        "DL1 ABC",
        "DL1\u00df",
        "DL1\ufb00",
        "D\u01311ABC",
    ],
)
def test_dependency_free_callsign_validation_rejects_malformed_or_unicode_tokens(
    callsign,
):
    """Reject malformed input and Unicode that could expand during uppercasing."""
    assert not input_validation.is_valid_callsign(callsign)


@pytest.mark.parametrize(
    "locator",
    ["aa00", "RR99", "JN37", "AA00AA", "RR99XX", "jn37aa"],
)
def test_dependency_free_locator_validation_accepts_exact_maidenhead_ranges(
    locator,
):
    """Accept only the defined four- and six-character Maidenhead ranges."""
    assert input_validation.is_valid_locator(locator)


@pytest.mark.parametrize(
    "locator",
    [
        "JN3",
        "JN370",
        "JN37A",
        "JN37AAA",
        "SS00",
        "JN37YY",
        "JN3'; DROP TABLE spots",
        "J\u013137",
        "J\u212a37",
    ],
)
def test_dependency_free_locator_validation_rejects_length_range_and_unicode_bypasses(
    locator,
):
    """Reject invalid ranges and Unicode characters before case normalization."""
    assert not input_validation.is_valid_locator(locator)


@pytest.mark.parametrize("grid4", ["aa00", "JN37", "RR99"])
def test_grid4_helper_accepts_only_exact_reference_station_selectors(grid4):
    """Accept the four-character selector owned by Reference Station."""
    assert input_validation.is_valid_grid4(grid4)


@pytest.mark.parametrize(
    "grid4",
    ["JN3", "JN37AA", "SS00", "J\u013137", "J\u212a37"],
)
def test_grid4_helper_rejects_other_precision_ranges_and_unicode(grid4):
    """Do not accept grid-6 or Unicode-folded text as a Reference grid-4."""
    assert not input_validation.is_valid_grid4(grid4)


def test_six_character_locator_helper_preserves_exact_length_contract():
    """Keep the specialized grid-6 helper aligned with general validation."""
    assert input_validation.is_valid_6char_locator("JN37AA")
    assert input_validation.is_valid_6char_locator("rr99xx")
    assert not input_validation.is_valid_6char_locator("JN37")
    assert not input_validation.is_valid_6char_locator("JN37YY")
    assert not input_validation.is_valid_6char_locator("J\u013137AA")


def test_time_quantization_floors_minutes_and_preserves_timezone():
    """Idle-shell quantization keeps the original timezone-aware timestamp."""
    timestamp = datetime(2026, 7, 12, 14, 29, 59, 123456, tzinfo=timezone.utc)

    quantized = time_utils.quantize_time(timestamp)

    assert quantized == datetime(2026, 7, 12, 14, 15, tzinfo=timezone.utc)


def test_math_utils_preserves_compatibility_exports():
    """Existing scientific consumers can retain the historical import path."""
    assert math_utils.is_valid_callsign is input_validation.is_valid_callsign
    assert math_utils.is_valid_locator is input_validation.is_valid_locator
    assert math_utils.is_valid_6char_locator is input_validation.is_valid_6char_locator
    assert math_utils.quantize_time is time_utils.quantize_time
