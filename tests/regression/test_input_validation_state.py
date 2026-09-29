"""Required-field guidance is explicit, reversible and shared by both editors."""

from datetime import date, time

import pytest

from ui.input_validation_state import (
    attempt_input_validation, get_field_error, validate_input_fields,
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
