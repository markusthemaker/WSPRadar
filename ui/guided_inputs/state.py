"""Canonical-state adapters and completion rules for Guided Input."""

from __future__ import annotations

import math
from datetime import datetime, time as dt_time, timedelta
from numbers import Integral
from typing import Any, Mapping, MutableMapping

from config import (
    BAND_MAP,
    MAP_SCOPE_OPTIONS,
    MAX_DAYS_HISTORY,
    MAX_DYNAMIC_RADIUS_KM,
    TX_AB_REPEAT_INTERVAL_OPTIONS,
)
from core.input_validation import is_valid_callsign, is_valid_grid4, is_valid_locator
from ui.config_io import _default_config


GUIDED_USE_CASES = frozenset(
    {"rx_success", "tx_success", "rx_compare", "tx_compare"}
)
GUIDED_OFFSET_INTENTS = frozenset(
    {"no_offset", "established_offset", "establish_offset"}
)
GUIDED_SCOPE_MODES = frozenset({"general", "custom", "demo"})
COMPARISON_MODES = frozenset(
    {"hardware_ab", "reference_station", "local_neighborhood"}
)
DEMO_OFFSET_INTENTS = {
    "vanhamel_rx_calibration": "establish_offset",
}


def derive_guided_use_case(state: Mapping[str, Any]) -> str | None:
    """Derive the completed operating question from canonical scientific state."""
    analysis_direction = state.get("val_analysis_direction")
    if analysis_direction not in {"rx", "tx"}:
        return None
    result_type = (
        "success" if state.get("val_comp_mode", "none") == "none" else "compare"
    )
    return f"{analysis_direction}_{result_type}"


def guided_facts(state: Mapping[str, Any]) -> dict[str, Any]:
    """Return the finite semantic facts exposed to declarative flow conditions."""
    guided_use_case = state.get("guided_use_case")
    if guided_use_case not in GUIDED_USE_CASES:
        guided_use_case = derive_guided_use_case(state)
    return {
        "guided_use_case": guided_use_case,
        "analysis_direction": state.get("val_analysis_direction"),
        "callsign": state.get("val_callsign"),
        "qth": state.get("val_qth"),
        "band": state.get("val_band"),
        "time_mode": state.get("val_time_mode"),
        "benchmark_mode": state.get("val_comp_mode"),
        "local_benchmark": state.get("val_local_benchmark"),
        "tx_ab_method": state.get("val_tx_ab_method"),
        "guided_offset_intent": state.get("guided_offset_intent"),
        "guided_scope_mode": state.get("guided_scope_mode"),
    }


def _valid_custom_window(state: Mapping[str, Any]) -> bool:
    """Return whether custom UTC date/time fields form one allowed interval."""
    start_date = state.get("val_start_d")
    end_date = state.get("val_end_d")
    start_time = state.get("val_start_t")
    end_time = state.get("val_end_t")
    if not all(
        (
            hasattr(start_date, "year"),
            hasattr(end_date, "year"),
            isinstance(start_time, dt_time),
            isinstance(end_time, dt_time),
        )
    ):
        return False
    start_utc = datetime.combine(start_date, start_time)
    end_utc = datetime.combine(end_date, end_time)
    return start_utc < end_utc <= start_utc + timedelta(days=MAX_DAYS_HISTORY)


def _target_and_window_complete(state: Mapping[str, Any]) -> bool:
    """Validate the Target identity, band and active time-selection branch."""
    if state.get("val_analysis_direction") not in {"rx", "tx"}:
        return False
    if not is_valid_callsign(state.get("val_callsign", "")):
        return False
    if not is_valid_locator(state.get("val_qth", "")):
        return False
    if state.get("val_band") not in BAND_MAP:
        return False
    time_mode = state.get("val_time_mode")
    if time_mode == "last_x":
        hours = state.get("val_hours")
        return isinstance(hours, int) and not isinstance(hours, bool) and 1 <= hours <= 168
    if time_mode == "custom":
        return _valid_custom_window(state)
    return False


def _reference_design_complete(state: Mapping[str, Any]) -> bool:
    """Validate only the identity/neighborhood/schedule branch currently selected."""
    benchmark_mode = state.get("val_comp_mode")
    if benchmark_mode == "local_neighborhood":
        radius_km = state.get("val_ref_radius_km")
        return (
            state.get("val_local_benchmark") in {"local_median", "local_best"}
            and isinstance(radius_km, int)
            and not isinstance(radius_km, bool)
            and 10 <= radius_km <= MAX_DYNAMIC_RADIUS_KM
            and radius_km % 10 == 0
        )
    if benchmark_mode not in {"hardware_ab", "reference_station"}:
        return False

    target_callsign = str(state.get("val_callsign", "")).strip().upper()
    reference_callsign = str(state.get("val_ref_callsign", "")).strip().upper()
    if benchmark_mode == "reference_station":
        return (
            is_valid_callsign(reference_callsign)
            and reference_callsign != target_callsign
            and is_valid_grid4(state.get("val_ref_qth", ""))
        )

    analysis_direction = state.get("val_analysis_direction")
    if analysis_direction == "rx" or state.get("val_tx_ab_method") == "simultaneous":
        return (
            is_valid_callsign(reference_callsign)
            and reference_callsign != target_callsign
        )
    if analysis_direction != "tx" or state.get("val_tx_ab_method") != "sequential":
        return False
    repeat_interval = state.get("val_tx_ab_repeat_interval_minutes")
    target_start = state.get("val_tx_ab_target_start_minute")
    reference_start = state.get("val_tx_ab_reference_start_minute")
    if (
        isinstance(repeat_interval, bool)
        or not isinstance(repeat_interval, Integral)
        or repeat_interval not in TX_AB_REPEAT_INTERVAL_OPTIONS
        or isinstance(target_start, bool)
        or not isinstance(target_start, Integral)
        or isinstance(reference_start, bool)
        or not isinstance(reference_start, Integral)
    ):
        return False
    permitted_starts = tuple(range(0, int(repeat_interval), 2))
    return (
        int(target_start) in permitted_starts
        and int(reference_start) in permitted_starts
        and int(target_start) != int(reference_start)
    )


def _offset_complete(state: Mapping[str, Any]) -> bool:
    """Validate Guided offset intent against the one canonical correction field."""
    intent = state.get("guided_offset_intent")
    if intent not in GUIDED_OFFSET_INTENTS:
        return False
    try:
        correction_db = float(state.get("val_benchmark_offset_db", 0.0))
    except (TypeError, ValueError):
        return False
    if not math.isfinite(correction_db) or not -99.9 <= correction_db <= 99.9:
        return False
    if intent in {"no_offset", "establish_offset"}:
        return round(correction_db, 1) == 0.0
    return True


def _scope_complete(state: Mapping[str, Any]) -> bool:
    """Validate the shared scope and evidence values used by either result type."""
    if state.get("guided_scope_mode") not in GUIDED_SCOPE_MODES:
        return False
    integer_ranges = {
        "val_min_spots": (1, 50),
        "val_min_opportunities": (1, 100),
        "val_min_stations": (1, 10),
    }
    for key, (minimum, maximum) in integer_ranges.items():
        value = state.get(key)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or not minimum <= value <= maximum
        ):
            return False
    return (
        state.get("val_solar") in {"all", "day", "night", "greyline"}
        and state.get("val_max_peer_distance_km") in MAP_SCOPE_OPTIONS
        and isinstance(state.get("val_exclude_special_callsigns"), bool)
        and isinstance(state.get("val_filter_moving"), bool)
    )


def is_guided_node_complete(node_id: str, state: Mapping[str, Any]) -> bool:
    """Return completion for one logical step without mutating its configuration."""
    if node_id == "use_case":
        return state.get("guided_use_case") in GUIDED_USE_CASES
    if node_id == "target_and_window":
        return _target_and_window_complete(state)
    if node_id == "reference_design":
        return _reference_design_complete(state)
    if node_id == "offset_calibration":
        return _offset_complete(state)
    if node_id == "scope_and_evidence":
        return _scope_complete(state)
    if node_id == "review_and_run":
        return True
    raise KeyError(f"Unknown Guided Input node {node_id!r}.")


def scope_matches_general_defaults(state: Mapping[str, Any]) -> bool:
    """Return whether every scope/evidence field equals its authoritative default."""
    defaults = _default_config()
    expected_values = {
        "val_solar": defaults["solar_state"],
        "val_max_peer_distance_km": defaults["max_peer_distance_km"],
        "val_exclude_special_callsigns": defaults["exclude_special_callsigns"],
        "val_filter_moving": defaults["exclude_moving_stations"],
        "val_min_spots": defaults["min_joint_spots_per_station"],
        "val_min_opportunities": defaults[
            "min_confirmed_opportunities_per_peer"
        ],
        "val_min_stations": defaults["min_joint_stations_per_map_segment"],
    }
    return all(state.get(key) == value for key, value in expected_values.items())


def apply_general_scope_defaults(state: MutableMapping[str, Any]) -> None:
    """Apply the current authoritative general-purpose population/scope defaults."""
    defaults = _default_config()
    state["val_solar"] = defaults["solar_state"]
    state["val_max_peer_distance_km"] = defaults["max_peer_distance_km"]
    state["val_exclude_special_callsigns"] = defaults["exclude_special_callsigns"]
    state["val_filter_moving"] = defaults["exclude_moving_stations"]
    state["val_min_spots"] = defaults["min_joint_spots_per_station"]
    state["val_min_opportunities"] = defaults[
        "min_confirmed_opportunities_per_peer"
    ]
    state["val_min_stations"] = defaults["min_joint_stations_per_map_segment"]


def reconstruct_guided_transients(
    state: MutableMapping[str, Any],
    *,
    has_loaded_demo: bool,
) -> None:
    """Rebuild transient choices from one loaded canonical configuration."""
    state["guided_use_case"] = derive_guided_use_case(state)
    benchmark_mode = state.get("val_comp_mode")
    state["guided_reference_design"] = (
        benchmark_mode if benchmark_mode in COMPARISON_MODES else None
    )
    if benchmark_mode in COMPARISON_MODES:
        state["guided_last_compare_mode"] = benchmark_mode
    correction_db = round(float(state.get("val_benchmark_offset_db", 0.0)), 1)
    demo_offset_intent = DEMO_OFFSET_INTENTS.get(
        state.get("active_demo_profile")
    )
    if demo_offset_intent == "establish_offset" and correction_db == 0.0:
        state["guided_offset_intent"] = demo_offset_intent
    else:
        state["guided_offset_intent"] = (
            "established_offset" if correction_db != 0.0 else "no_offset"
        )
    if has_loaded_demo:
        state["guided_scope_mode"] = "demo"
    else:
        state["guided_scope_mode"] = (
            "general" if scope_matches_general_defaults(state) else "custom"
        )
