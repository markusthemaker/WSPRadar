"""Pure, transient handshake for committing a Guided boundary-Tab edit.

The browser first asks to prepare a move with its last editable value. Only an
acknowledged committed snapshot may then be consumed by the ordinary Continue
callback. These helpers never change a scientific value or decide validity.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
import re
from typing import Any

from config.delta_snr_outlier import DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
from core.input_validation import normalize_ascii_upper


GUIDED_KEYBOARD_PENDING_KEY = "_guided_keyboard_pending"
GUIDED_KEYBOARD_RETIRED_KEY = "_guided_keyboard_retired_tokens"
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,160}")
_DECIMAL_PATTERN = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", re.ASCII)
_IDENTITY_KEYS = frozenset({"val_callsign", "val_qth", "val_ref_callsign", "val_ref_qth"})
_CORRECTION_KEY = "_val_benchmark_offset_db_text"
_CORRECTION_ERROR_KEY = "_val_benchmark_offset_db_text_error"
_RADIO_KEYS = frozenset({"guided_use_case", "guided_reference_design", "val_snr_correction_mode"})
_FIELD_KINDS = {
    "guided_use_case": "radio",
    "guided_reference_design": "radio",
    "val_analysis_direction": "text",
    "val_callsign": "text",
    "val_qth": "text",
    "val_band": "text",
    "val_start_d": "date",
    "val_end_d": "date",
    "val_start_t": "time",
    "val_end_t": "time",
    "val_comp_mode": "text",
    "val_local_benchmark": "text",
    "val_ref_callsign": "text",
    "val_ref_qth": "text",
    "val_ref_radius_km": "number",
    "val_benchmark_offset_db": "number",
    "val_snr_correction_mode": "radio",
    _CORRECTION_KEY: "text",
    _CORRECTION_ERROR_KEY: "bool",
    "val_solar": "text",
    "val_max_peer_distance_km": "number",
    "val_exclude_special_callsigns": "bool",
    "val_filter_moving": "bool",
    "_val_exclude_special_callsigns": "bool",
    "_val_filter_moving": "bool",
    "val_min_spots": "number",
    "val_min_opportunities": "number",
    "val_min_stations": "number",
    "val_report_delta_snr_outlier_candidates": "bool",
    **{
        f"val_{config_field}": "number"
        for config_field, _policy_field in (
            DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
        )
    },
}
_ALIASES = {
    "_val_exclude_special_callsigns": "val_exclude_special_callsigns",
    "_val_filter_moving": "val_filter_moving",
    _CORRECTION_KEY: "val_benchmark_offset_db",
}


def _string_value(value: Any, kind: str) -> str:
    """Serialize only the native primitive represented by a known widget."""
    if value is None:
        return ""
    if kind == "date":
        return value.isoformat() if isinstance(value, date) and not isinstance(value, datetime) else ""
    if kind == "time":
        return value.isoformat(timespec="minutes") if isinstance(value, time) else ""
    if kind == "bool":
        return str(value).lower() if isinstance(value, bool) else ""
    if kind == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return ""
        return str(value) if math.isfinite(value) else ""
    return value if isinstance(value, str) else ""


def guided_keyboard_values(
    state: Mapping[str, Any], radio_options: Mapping[str, Sequence[str]]
) -> tuple[dict[str, Any], ...]:
    """Describe known committed fields, including widget-to-canonical aliases.

    Radio options retain the renderer's order so a browser radio index can be
    translated without interpreting localized labels. Unrelated session values
    and all unknown widget keys are deliberately excluded.
    """
    result = []
    for key, kind in _FIELD_KINDS.items():
        source_key = _ALIASES.get(key, key)
        if source_key not in state:
            continue
        source_kind = "number" if key == _CORRECTION_KEY else kind
        descriptor = {"key": key, "kind": kind, "value": _string_value(state[source_key], source_kind)}
        if key in _RADIO_KEYS:
            options = radio_options.get(key, ())
            if isinstance(options, Sequence) and not isinstance(options, (str, bytes)):
                if all(isinstance(option, str) and len(option) <= 256 for option in options):
                    descriptor["options"] = list(options)
        result.append(descriptor)
    return tuple(result)


def _valid_token(token: Any) -> bool:
    return isinstance(token, str) and _TOKEN_PATTERN.fullmatch(token) is not None


def _retire(state: MutableMapping[str, Any], token: Any) -> None:
    if not _valid_token(token):
        return
    previous = state.get(GUIDED_KEYBOARD_RETIRED_KEY, ())
    previous = previous if isinstance(previous, (list, tuple)) else ()
    state[GUIDED_KEYBOARD_RETIRED_KEY] = [
        value for value in previous if _valid_token(value) and value != token
    ][-63:] + [token]


def cancel_guided_keyboard(state: MutableMapping[str, Any], token: str) -> None:
    """Cancel only the named request; delayed cancels cannot replace a newer one."""
    if not _valid_token(token):
        return
    pending = state.get(GUIDED_KEYBOARD_PENDING_KEY)
    if isinstance(pending, Mapping) and pending.get("token") == token:
        state.pop(GUIDED_KEYBOARD_PENDING_KEY, None)
    _retire(state, token)


def _available_node(state: Mapping[str, Any], node: Any, available_nodes: Sequence[str]) -> bool:
    return (
        state.get("input_view") == "guided"
        and _valid_token(node)
        and node in available_nodes
    )


def _active_node(state: Mapping[str, Any], node: Any, available_nodes: Sequence[str]) -> bool:
    return (
        _available_node(state, node, available_nodes)
        and state.get("guided_active_node") == node
        and not state.get("guided_collapse_all", False)
    )


def _valid_expected(expected: Any) -> bool:
    if expected is None:
        return True
    return (
        isinstance(expected, Mapping)
        and set(expected) == {"key", "kind", "value"}
        and isinstance(expected["key"], str)
        and expected["key"] in _FIELD_KINDS
        and expected["kind"] == _FIELD_KINDS[expected["key"]]
        and isinstance(expected["value"], str)
        and len(expected["value"]) <= 256
    )


def prepare_guided_keyboard(
    state: MutableMapping[str, Any], payload: Any,
    available_nodes: Sequence[str], terminal_node: str,
) -> None:
    """Queue a bounded browser intent without advancing or validating a panel."""
    if not isinstance(payload, Mapping) or set(payload) != {"token", "node", "expected"}:
        return
    token, node = payload["token"], payload["node"]
    if (
        not _valid_token(token)
        or token in state.get(GUIDED_KEYBOARD_RETIRED_KEY, ())
        or not _available_node(state, node, available_nodes)
        or node == terminal_node
        or not _valid_expected(payload["expected"])
    ):
        return
    pending = state.get(GUIDED_KEYBOARD_PENDING_KEY)
    if isinstance(pending, Mapping):
        if pending.get("token") == token:
            return
        _retire(state, pending.get("token"))
    state[GUIDED_KEYBOARD_PENDING_KEY] = {
        "token": token, "node": node,
        "expected": dict(payload["expected"]) if payload["expected"] is not None else None,
        "ready": False, "fingerprint": None,
    }


def _fingerprint(values: Sequence[Mapping[str, Any]]) -> str:
    serialized = json.dumps(sorted(values, key=lambda value: value["key"]), sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _number(value: str) -> Decimal | None:
    try:
        number = Decimal(value)
    except InvalidOperation:
        return None
    return number if number.is_finite() else None


def _same_value(expected: Mapping[str, str], committed: Mapping[str, Any]) -> bool:
    if expected["kind"] != committed["kind"]:
        return False
    key, value, current = expected["key"], expected["value"], committed["value"]
    if key in _IDENTITY_KEYS:
        return normalize_ascii_upper(value) == normalize_ascii_upper(current)
    if key == _CORRECTION_KEY:
        # Match the existing text callback's decimal syntax and one-decimal
        # normalization. Scientific bounds remain the normal validator's job.
        text = value.strip()
        if text and not _DECIMAL_PATTERN.fullmatch(text):
            return False
        rounded = round(float(text or "0"), 1)
        return math.isfinite(rounded) and _number(str(rounded)) == _number(current)
    if expected["kind"] == "number":
        number = _number(value)
        return number is not None and number == _number(current)
    return value == current


def guided_keyboard_ack(
    state: MutableMapping[str, Any], values: Sequence[Mapping[str, Any]],
    available_nodes: Sequence[str],
) -> dict[str, Any] | None:
    """Acknowledge only values already committed by native widget callbacks."""
    pending = state.get(GUIDED_KEYBOARD_PENDING_KEY)
    if not isinstance(pending, dict):
        return None
    if not _active_node(state, pending["node"], available_nodes):
        cancel_guided_keyboard(state, pending["token"])
        return None
    expected = pending["expected"]
    committed = next((value for value in values if expected and value["key"] == expected["key"]), None)
    # A rejected correction is also a finished native callback: Continue must
    # validate and focus that field instead of waiting for its invalid raw text
    # to equal the deliberately retained canonical number. The rejection flag
    # participates in the fingerprint and remains the validator's authority.
    correction_rejected = bool(
        expected
        and expected["key"] == _CORRECTION_KEY
        and any(
            value["key"] == _CORRECTION_ERROR_KEY
            and value["kind"] == "bool"
            and value["value"] == "true"
            for value in values
        )
    )
    ready = expected is None or correction_rejected or (committed is not None and _same_value(expected, committed))
    fingerprint = _fingerprint(values) if ready else None
    pending.update(ready=ready, fingerprint=fingerprint)
    return {"token": pending["token"], "node": pending["node"], "ready": ready, "fingerprint": fingerprint}


def consume_guided_keyboard(
    state: MutableMapping[str, Any], payload: Any,
    values: Sequence[Mapping[str, Any]], available_nodes: Sequence[str],
) -> str | None:
    """Consume one acknowledged intent only while its full snapshot is current."""
    if not isinstance(payload, Mapping) or set(payload) != {"token", "fingerprint"}:
        return None
    pending = state.get(GUIDED_KEYBOARD_PENDING_KEY)
    if not isinstance(pending, Mapping) or payload["token"] != pending.get("token"):
        return None
    token = pending["token"]
    if not _active_node(state, pending["node"], available_nodes):
        cancel_guided_keyboard(state, token)
        return None
    if (
        not pending.get("ready")
        or payload["fingerprint"] != pending.get("fingerprint")
        or payload["fingerprint"] != _fingerprint(values)
    ):
        cancel_guided_keyboard(state, token)
        return None
    node = pending["node"]
    cancel_guided_keyboard(state, token)
    return node
