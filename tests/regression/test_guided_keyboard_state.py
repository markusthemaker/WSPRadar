"""Pure contracts for Guided Tab commit acknowledgments and stale-intent guards."""

from copy import deepcopy
from datetime import date, time

import pytest

from config.delta_snr_outlier import DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
from ui.guided_inputs.keyboard_state import (
    GUIDED_KEYBOARD_PENDING_KEY,
    GUIDED_KEYBOARD_RETIRED_KEY,
    cancel_guided_keyboard,
    consume_guided_keyboard,
    guided_keyboard_ack,
    guided_keyboard_values,
    prepare_guided_keyboard,
)


NODES = ("use_case", "target_and_window", "reference_design", "offset_calibration", "scope", "review")
RADIO_OPTIONS = {"guided_use_case": ("rx_performance", "tx_performance", "rx_benchmark", "tx_benchmark")}


def _state(**updates):
    state = {
        "input_view": "guided",
        "guided_active_node": "target_and_window",
        "guided_use_case": "rx_performance",
        "val_analysis_direction": "rx",
        "val_comp_mode": "none",
        "val_callsign": "DL1MKS",
        "val_qth": "JO62",
        "val_band": "20m",
        "val_start_d": date(2026, 10, 8),
        "val_end_d": date(2026, 10, 9),
        "val_start_t": time(20, 4),
        "val_end_t": time(20, 4),
        "val_filter_moving": True,
        "val_exclude_special_callsigns": False,
        "val_benchmark_offset_db": 0.0,
        "val_min_stations": 3,
    }
    state.update(updates)
    return state


def _prepare(state, expected=None, token="request-1", node="target_and_window"):
    prepare_guided_keyboard(state, {"token": token, "node": node, "expected": expected}, NODES, "review")


def _values(state):
    return guided_keyboard_values(state, RADIO_OPTIONS)


def _ack(state):
    return guided_keyboard_ack(state, _values(state), NODES)


def _consume(state, ack):
    return consume_guided_keyboard(state, {"token": ack["token"], "fingerprint": ack["fingerprint"]}, _values(state), NODES)


def test_values_are_native_primitives_with_ordered_radio_options_and_canonical_aliases():
    state = _state(
        _val_filter_moving=False,
        _val_benchmark_offset_db_text="+1.27",
        val_benchmark_offset_db=1.3,
        unrelated_secret="not a widget",
        val_unrelated_inspector_state={"not": "a configuration input"},
    )
    original = deepcopy(state)
    descriptors = {value["key"]: value for value in _values(state)}

    assert descriptors["val_start_d"]["value"] == "2026-10-08"
    assert descriptors["val_start_t"]["value"] == "20:04"
    assert descriptors["val_filter_moving"]["value"] == "true"
    assert descriptors["_val_filter_moving"]["value"] == "true"
    assert descriptors["val_min_stations"]["value"] == "3"
    assert descriptors["_val_benchmark_offset_db_text"] == {
        "key": "_val_benchmark_offset_db_text", "kind": "text", "value": "1.3",
    }
    assert descriptors["guided_use_case"]["options"] == list(RADIO_OPTIONS["guided_use_case"])
    assert "unrelated_secret" not in descriptors
    assert "val_unrelated_inspector_state" not in descriptors
    assert state == original


def test_prepare_does_not_advance_or_change_scientific_values():
    state = _state()
    original = deepcopy(state)
    _prepare(state, {"key": "val_qth", "kind": "text", "value": "gn38"})

    assert state[GUIDED_KEYBOARD_PENDING_KEY]["ready"] is False
    assert {key: value for key, value in state.items() if key != GUIDED_KEYBOARD_PENDING_KEY} == original


def test_all_canonical_detector_thresholds_participate_in_committed_snapshot():
    state = _state(**{
        f"val_{config_field}": 1.5
        for config_field, _policy_field in DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
    })
    descriptors = {value["key"]: value for value in _values(state)}
    for config_field, _policy_field in DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD:
        key = f"val_{config_field}"
        assert descriptors[key] == {"key": key, "kind": "number", "value": "1.5"}


def test_prepare_accepts_manually_reopened_available_panel_without_activating_it():
    state = _state(guided_active_node="scope", guided_collapse_all=True)
    _prepare(state)

    assert state[GUIDED_KEYBOARD_PENDING_KEY]["node"] == "target_and_window"
    assert state["guided_active_node"] == "scope"
    assert state["guided_collapse_all"] is True


@pytest.mark.parametrize("payload", [
    None, [], {},
    {"token": "x", "node": "review", "expected": None},
    {"token": "x", "node": "missing", "expected": None},
    {"token": "x" * 161, "node": "target_and_window", "expected": None},
    {"token": "<script>", "node": "target_and_window", "expected": None},
    {"token": [], "node": "target_and_window", "expected": None},
    {"token": "x", "node": [], "expected": None},
    {"token": "x", "node": "target_and_window", "expected": {"key": "arbitrary", "kind": "text", "value": "x"}},
    {"token": "x", "node": "target_and_window", "expected": {"key": "val_qth", "kind": "date", "value": "2026-10-09"}},
    {"token": "x", "node": "target_and_window", "expected": {"key": "val_qth", "kind": "text", "value": []}},
    {"token": "x", "node": "target_and_window", "expected": {"key": "val_qth", "kind": "text", "value": "x" * 257}},
    {"token": "x", "node": "target_and_window", "expected": None, "extra": "not supported"},
])
def test_malformed_prepare_payloads_and_terminal_nodes_are_ignored(payload):
    state = _state()
    original = deepcopy(state)
    prepare_guided_keyboard(state, payload, NODES, "review")
    assert state == original


def test_classic_view_cannot_queue_guided_navigation():
    state = _state(input_view="classic")
    _prepare(state)
    assert GUIDED_KEYBOARD_PENDING_KEY not in state


def test_ack_waits_for_native_commit_then_uses_full_post_callback_snapshot():
    state = _state()
    _prepare(state, {"key": "val_start_d", "kind": "date", "value": "2026-10-10"})
    waiting = _ack(state)
    assert waiting == {"token": "request-1", "node": "target_and_window", "ready": False, "fingerprint": None}

    # The existing Start Date callback may also move End Date. The intent only
    # compares the native field left by the user, then fingerprints both dates.
    state.update(val_start_d=date(2026, 10, 10), val_end_d=date(2026, 10, 11))
    ready = _ack(state)
    assert ready["ready"] is True
    assert len(ready["fingerprint"]) == 64
    assert _consume(state, ready) == "target_and_window"


@pytest.mark.parametrize(("key", "expected", "current", "ready"), [
    ("val_callsign", "  dl1mks ", "DL1MKS", True),
    ("val_qth", " gn38 ", "GN38", True),
    ("val_ref_callsign", " m7aeo ", "M7AEO", True),
    ("val_ref_qth", " io82 ", "IO82", True),
    ("val_callsign", "ß1ABC", "SS1ABC", False),
    ("val_qth", "GN39", "GN38", False),
])
def test_identity_ack_matches_existing_ascii_normalization(key, expected, current, ready):
    state = _state(**{key: current})
    _prepare(state, {"key": key, "kind": "text", "value": expected})
    assert _ack(state)["ready"] is ready


@pytest.mark.parametrize(("expected", "current", "ready"), [
    ("+1.27", 1.3, True), ("", 0.0, True), ("-.0", 0.0, True),
    ("2", 2.0, True), ("1.2", 2.0, False), ("1,2", 1.2, False),
    ("NaN", 0.0, False), ("Infinity", 0.0, False), ("1e0", 1.0, False),
])
def test_correction_ack_uses_committed_decimal_normalization(expected, current, ready):
    state = _state(val_benchmark_offset_db=current, _val_benchmark_offset_db_text=expected)
    _prepare(state, {"key": "_val_benchmark_offset_db_text", "kind": "text", "value": expected})
    assert _ack(state)["ready"] is ready


@pytest.mark.parametrize("rejected_text", ["invalid", "1,2", "100.0", "-100.0"])
def test_native_correction_rejection_is_acknowledged_for_ordinary_validation(rejected_text):
    # The existing callback retains the valid canonical correction, restores
    # its widget text, and records the rejection for the ordinary validator.
    state = _state(
        guided_active_node="offset_calibration",
        val_benchmark_offset_db=1.3,
        _val_benchmark_offset_db_text="1.3",
        _val_benchmark_offset_db_text_error=True,
    )
    original = deepcopy(state)
    _prepare(
        state,
        {"key": "_val_benchmark_offset_db_text", "kind": "text", "value": rejected_text},
        node="offset_calibration",
    )

    ack = _ack(state)
    assert ack["ready"] is True
    assert _consume(state, ack) == "offset_calibration"
    assert {
        key: value for key, value in state.items()
        if key != GUIDED_KEYBOARD_RETIRED_KEY
    } == original


def test_correction_rejection_flag_is_part_of_consumed_fingerprint():
    state = _state(_val_benchmark_offset_db_text_error=True)
    _prepare(state, {"key": "_val_benchmark_offset_db_text", "kind": "text", "value": "invalid"})
    ack = _ack(state)
    assert ack["ready"] is True
    state.pop("_val_benchmark_offset_db_text_error")
    assert _consume(state, ack) is None


def test_correction_rejection_does_not_acknowledge_another_uncommitted_field():
    state = _state(_val_benchmark_offset_db_text_error=True)
    _prepare(state, {"key": "val_qth", "kind": "text", "value": "GN38"})
    assert _ack(state)["ready"] is False


def test_population_ack_waits_for_canonical_callback_not_only_widget_state():
    state = _state(_val_filter_moving=False)
    _prepare(state, {"key": "_val_filter_moving", "kind": "bool", "value": "false"})
    assert _ack(state)["ready"] is False
    state["val_filter_moving"] = False
    assert _ack(state)["ready"] is True


def test_numerical_slider_ack_allows_native_equivalent_decimal_representation():
    state = _state()
    _prepare(state, {"key": "val_min_stations", "kind": "number", "value": "3.0"})
    assert _ack(state)["ready"] is True


def test_matching_snapshot_is_consumed_once_and_cannot_be_reprepared():
    state = _state()
    original = deepcopy(state)
    _prepare(state)
    ack = _ack(state)
    assert _consume(state, ack) == "target_and_window"
    assert _consume(state, ack) is None
    _prepare(state)
    assert GUIDED_KEYBOARD_PENDING_KEY not in state
    assert {key: value for key, value in state.items() if key != GUIDED_KEYBOARD_RETIRED_KEY} == original


def test_stale_fingerprint_retires_request_when_another_field_changes_after_ack():
    state = _state()
    _prepare(state)
    ack = _ack(state)
    state["val_min_stations"] = 4
    assert _consume(state, ack) is None
    assert GUIDED_KEYBOARD_PENDING_KEY not in state
    state["val_min_stations"] = 3
    assert _consume(state, ack) is None


@pytest.mark.parametrize("change", [
    {"input_view": "classic"},
    {"guided_active_node": "scope"},
    {"guided_collapse_all": True},
])
def test_ack_cancels_after_deliberate_view_or_active_panel_change(change):
    state = _state()
    _prepare(state)
    state.update(change)
    assert _ack(state) is None
    assert GUIDED_KEYBOARD_PENDING_KEY not in state


def test_branch_change_removing_pending_panel_cancels_ack_and_consume():
    state = _state(guided_active_node="reference_design")
    _prepare(state, node="reference_design")
    ack = _ack(state)
    shorter_nodes = ("use_case", "target_and_window", "scope", "review")
    assert consume_guided_keyboard(state, {"token": ack["token"], "fingerprint": ack["fingerprint"]}, _values(state), shorter_nodes) is None
    assert GUIDED_KEYBOARD_PENDING_KEY not in state


def test_stale_cancel_or_advance_does_not_discard_newer_pending_intent():
    state = _state()
    _prepare(state, token="old")
    old_ack = _ack(state)
    _prepare(state, token="new")
    cancel_guided_keyboard(state, "old")
    assert _consume(state, old_ack) is None
    assert state[GUIDED_KEYBOARD_PENDING_KEY]["token"] == "new"
    assert _consume(state, _ack(state)) == "target_and_window"


@pytest.mark.parametrize("payload", [None, {}, [], {"token": "request-1"}, {"token": [], "fingerprint": []}])
def test_malformed_advance_cannot_consume_a_ready_request(payload):
    state = _state()
    _prepare(state)
    _ack(state)
    assert consume_guided_keyboard(state, payload, _values(state), NODES) is None
    assert state[GUIDED_KEYBOARD_PENDING_KEY]["token"] == "request-1"


def test_fingerprint_is_deterministic_for_descriptor_order_and_options():
    state = _state()
    _prepare(state)
    values = _values(state)
    ack = guided_keyboard_ack(state, values, NODES)
    assert guided_keyboard_ack(state, tuple(reversed(values)), NODES) == ack
    reordered_radios = guided_keyboard_values(state, {"guided_use_case": tuple(reversed(RADIO_OPTIONS["guided_use_case"]))})
    assert guided_keyboard_ack(state, reordered_radios, NODES)["fingerprint"] != ack["fingerprint"]
