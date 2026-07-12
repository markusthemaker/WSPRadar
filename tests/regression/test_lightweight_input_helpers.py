from datetime import datetime, timezone

from core import input_validation, math_utils, time_utils


def test_dependency_free_callsign_and_locator_validation_preserves_contracts():
    """Split validation helpers must retain the accepted identity syntax."""
    assert input_validation.is_valid_callsign("w1a")
    assert input_validation.is_valid_callsign("VK2FXXX/MM")
    assert not input_validation.is_valid_callsign("DL1ABC'; DROP TABLE spots")

    assert input_validation.is_valid_locator("jn37")
    assert input_validation.is_valid_locator("JN37AA")
    assert not input_validation.is_valid_locator("JN3")
    assert input_validation.is_valid_6char_locator("JN37AA")
    assert not input_validation.is_valid_6char_locator("JN37")


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
