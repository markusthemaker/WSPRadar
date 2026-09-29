"""Dependency-light session ownership for a pending location decision."""

import hashlib
import json

from core.input_validation import normalize_ascii_upper


REFERENCE_LOCATION_STATE_KEY = "_reference_location_resolution"


def location_request_signature(state, start_utc, end_utc):
    payload = {
        "direction": state.get("val_analysis_direction"),
        "target": normalize_ascii_upper(state.get("val_callsign")),
        "qth": normalize_ascii_upper(state.get("val_qth")),
        "reference": normalize_ascii_upper(state.get("val_ref_callsign")),
        "band": state.get("val_band"),
        "start": start_utc.isoformat(), "end": end_utc.isoformat(),
        "exclude_special": bool(state.get("val_exclude_special_callsigns", False)),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def store_location_discovery(state, discovery, signature):
    resolution = discovery.to_dict()
    resolution["signature"] = signature
    resolution["selected_grid"] = None
    state[REFERENCE_LOCATION_STATE_KEY] = resolution
    return resolution


def current_location_resolution(state, start_utc, end_utc):
    value = state.get(REFERENCE_LOCATION_STATE_KEY)
    if not isinstance(value, dict):
        return None
    if value.get("signature") != location_request_signature(state, start_utc, end_utc):
        return None
    return value


def select_reference_location(state, grid):
    resolution = state.get(REFERENCE_LOCATION_STATE_KEY)
    candidates = resolution.get("reference_locations", ()) if isinstance(resolution, dict) else ()
    grid = normalize_ascii_upper(grid)
    if grid not in {candidate["grid"] for candidate in candidates}:
        raise ValueError("Select one of the discovered Reference locations.")
    resolution = dict(resolution, selected_grid=grid)
    state[REFERENCE_LOCATION_STATE_KEY] = resolution
    state["val_ref_qth"] = grid


def resolved_discovery_source(state, start_utc, end_utc):
    if state.get("val_comp_mode") != "reference_station":
        return None
    resolution = current_location_resolution(state, start_utc, end_utc)
    if resolution and resolution.get("selected_grid") == state.get("val_ref_qth"):
        return resolution.get("database_source")
    return None


def discard_failed_discovery_source(state, database_source):
    """Require fresh discovery on the next Run after its archive fails."""
    resolution = state.get(REFERENCE_LOCATION_STATE_KEY)
    if isinstance(resolution, dict) and resolution.get("database_source") == database_source:
        state.pop(REFERENCE_LOCATION_STATE_KEY, None)
        state["val_ref_qth"] = ""
