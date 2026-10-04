"""Required-field guidance is explicit, reversible and shared by both editors."""

from datetime import date, time
from copy import deepcopy
from string import Formatter

import pytest

from ui.input_validation_state import (
    attempt_input_validation, get_field_error, tx_message_pattern_warning,
    validate_input_fields,
)


def valid_state(**overrides):
    state = dict(input_view="guided", lang="en", guided_use_case="rx_benchmark",
                 val_analysis_direction="rx", val_callsign="DL1MKS", val_qth="JN37AA",
                 val_band="20m", val_start_d=date(2026, 7, 1), val_start_t=time(0),
                 val_end_d=date(2026, 7, 2), val_end_t=time(0),
                 val_comp_mode="reference_station", val_ref_callsign="DL2XYZ", val_ref_qth="",
                 val_snr_correction_mode="no_offset",
                 val_benchmark_offset_db=0.0, val_local_benchmark="local_median",
                 val_solar="all", val_ref_radius_km=100,
                 val_min_spots=1, val_min_opportunities=5, val_min_stations=1)
    state.update(overrides)
    return state


def test_initial_empty_fields_are_neutral_then_all_missing_fields_are_reported():
    state = valid_state(val_callsign="", val_qth="", val_ref_callsign="")
    assert get_field_error(state, "val_callsign") is None
    errors = attempt_input_validation(state)
    assert {"val_callsign", "val_qth", "val_ref_callsign"} <= errors.keys()
    assert state["guided_active_node"] == "target_and_window"
    assert "_analysis_submission_token" not in state
    assert get_field_error(state, "val_callsign")


def test_each_corrected_field_clears_without_hiding_other_errors():
    state = valid_state(val_callsign="", val_qth="")
    attempt_input_validation(state)
    state["val_callsign"] = "DL1MKS"
    assert get_field_error(state, "val_callsign") is None
    assert get_field_error(state, "val_qth")
    state["val_qth"] = "JN37AA"
    assert not validate_input_fields(state)


@pytest.mark.parametrize("view,key", [("guided", "guided_use_case"), ("classic", "classic_question")])
def test_pending_benchmark_design_cannot_execute_as_performance(view, key):
    state = valid_state(input_view=view, val_comp_mode="none")
    state[key] = "rx_benchmark"
    assert "val_comp_mode" in attempt_input_validation(state)
    assert state["guided_active_node"] == "reference_design"


def test_automatic_reference_location_is_allowed_but_equal_callsigns_are_not():
    assert not validate_input_fields(valid_state())
    state = valid_state(val_ref_callsign="DL1MKS")
    assert "val_ref_callsign" in validate_input_fields(state)


@pytest.mark.parametrize("view,node", [("guided", "offset_calibration"), ("classic", "reference_design")])
def test_numeric_correction_error_opens_its_editor_specific_section(view, node):
    state = valid_state(input_view=view, val_snr_correction_mode="established_offset", val_benchmark_offset_db=float("nan"))
    errors = attempt_input_validation(state)
    assert "_val_benchmark_offset_db_text" in errors
    assert state["guided_active_node"] == node


def test_correction_intent_error_still_opens_calibration_step():
    state = valid_state(val_snr_correction_mode="invalid")
    errors = attempt_input_validation(state)
    assert "val_snr_correction_mode" in errors
    assert state["guided_active_node"] == "offset_calibration"


def test_invalid_time_and_reference_are_both_reported():
    state = valid_state(val_end_d=date(2026, 6, 1), val_ref_callsign="")
    errors = validate_input_fields(state)
    assert {"val_start_d", "val_end_d", "val_ref_callsign"} <= errors.keys()


def test_unused_reference_is_not_required_for_performance():
    state = valid_state(guided_use_case="rx_performance", val_comp_mode="none", val_ref_callsign="")
    assert not validate_input_fields(state)


def test_time_only_invalid_window_marks_time_fields_and_clears_after_correction():
    state = valid_state(val_start_t=time(12), val_end_d=date(2026, 7, 1), val_end_t=time(11))
    fields = {"val_start_d", "val_start_t", "val_end_d", "val_end_t"}
    assert fields <= attempt_input_validation(state).keys()
    assert all(get_field_error(state, field) for field in fields)
    state["val_end_t"] = time(13)
    assert all(get_field_error(state, field) is None for field in fields)


@pytest.mark.parametrize("target,reference,expected", [
    ("DL1MKS", "DL1MKS/P", True),
    ("DL1MKS/1", "DL1MKS", True),
    ("DL1MKS", "G1XYZ/P", True),
    ("F/DL1MKS", "G1XYZ", True),
    (" dl1mks ", " g1xyz/p ", True),
    ("DL1MKS", "G1XYZ", False),
    ("DL1MKS/1", "DL1MKS/2", False),
    ("DL1MKS/P", "G1XYZ/P", False),
    ("DL1MKS/P", "DL1MKS/P", False),
    ("DL1MKS", "", False),
    ("", "DL1MKS/P", False),
    ("DL1MKS", "DL1MKS//P", False),
    ("DL1MKS/", "G1XYZ", False),
])
def test_tx_message_pattern_warning_checks_structure_without_rejecting_inputs(
    target, reference, expected,
):
    state = valid_state(
        guided_use_case="tx_benchmark", val_analysis_direction="tx",
        val_callsign=target, val_ref_callsign=reference,
    )
    before = deepcopy(state)
    assert bool(tx_message_pattern_warning(state)) is expected
    assert state == before


@pytest.mark.parametrize("direction,mode", [
    ("rx", "reference_station"), ("rx", "none"),
    ("rx", "local_neighborhood"), ("tx", "none"),
    ("tx", "local_neighborhood"), (None, "reference_station"),
])
def test_tx_message_pattern_warning_is_limited_to_fixed_reference_tx(direction, mode):
    state = valid_state(
        val_analysis_direction=direction, val_comp_mode=mode,
        val_callsign="DL1MKS", val_ref_callsign="DL1MKS/P",
    )
    assert tx_message_pattern_warning(state) is None


@pytest.mark.parametrize("view", ["guided", "classic"])
def test_tx_message_pattern_warning_preserves_validation_and_saved_config(view):
    from ui.components.config_review import is_canonical_configuration_ready
    from ui.config_io import build_config_settings_from_state

    state = valid_state(
        input_view=view, guided_use_case="tx_benchmark",
        classic_question="tx_benchmark", val_analysis_direction="tx",
        val_ref_callsign="DL1MKS/P",
    )
    settings = build_config_settings_from_state(state)
    assert tx_message_pattern_warning(state)
    assert not validate_input_fields(state)
    assert is_canonical_configuration_ready(state)
    assert build_config_settings_from_state(state) == settings
    state["val_callsign"] = "DL1MKS/P"
    assert "val_ref_callsign" in validate_input_fields(state)
    assert not is_canonical_configuration_ready(state)


def test_tx_message_pattern_warning_uses_bilingual_catalog_with_placeholder_parity():
    from i18n import T

    for key in ("warn_tx_message_patterns_title", "warn_tx_message_patterns"):
        assert all(T[language][key] for language in ("en", "de"))
        placeholders = lambda text: {
            field for _, field, _, _ in Formatter().parse(text) if field is not None
        }
        assert placeholders(T["en"][key]) == placeholders(T["de"][key])
    for language in ("en", "de"):
        state = valid_state(
            lang=language, val_analysis_direction="tx", val_ref_callsign="DL1MKS/P",
        )
        warning = tx_message_pattern_warning(state)
        assert warning == (
            f"**{T[language]['warn_tx_message_patterns_title']}**\n\n"
            f"{T[language]['warn_tx_message_patterns']}"
        )
        assert "`CALL/1`" in warning and "`CALL/2`" in warning
