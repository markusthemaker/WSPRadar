"""Shared field errors and setup guidance without importing scientific runtime."""

from collections.abc import Mapping
import math

from config import BAND_MAP, MAX_DYNAMIC_RADIUS_KM
from core.input_validation import is_valid_callsign, is_valid_grid4, is_valid_locator, normalize_ascii_upper
from ui.time_window import TIME_WINDOW_STATE_KEYS, utc_window_from_state, time_window_validation_message_key


INPUT_VALIDATION_ATTEMPTED_KEY = "_input_validation_attempted"
INPUT_FIELD_ERRORS_KEY = "_input_field_errors"

_MESSAGES = {
    "en": {
        "target": "Enter the Target callsign.", "qth": "Enter the Target QTH (4 or 6 characters).",
        "question": "Choose RX or TX and Performance or Benchmark.",
        "reference": "Enter the Reference callsign.", "band": "Choose a supported WSPR band.",
        "design": "Choose Reference Setup/Station or Reference Neighborhood.",
        "radius": "Enter a valid Reference Neighborhood radius.",
        "correction": "Enter a finite Reference correction from -99.9 to +99.9 dB.",
        "correction_mode": "Choose why a Reference correction is being used.",
        "threshold": "Enter a positive whole-number evidence requirement.",
        "summary": "Please correct the highlighted inputs before continuing.",
        "generic": "Check this configuration value.",
    },
    "de": {
        "target": "Gib das Target-Rufzeichen ein.", "qth": "Gib das Target-QTH ein (4 oder 6 Zeichen).",
        "question": "Wähle RX oder TX sowie Performance oder Benchmark.",
        "reference": "Gib das Referenz-Rufzeichen ein.", "band": "Wähle ein unterstütztes WSPR-Band.",
        "design": "Wähle Referenzaufbau/-station oder Referenznachbarschaft.",
        "radius": "Gib einen gültigen Radius für die Referenznachbarschaft ein.",
        "correction": "Gib eine endliche Referenzkorrektur von -99,9 bis +99,9 dB ein.",
        "correction_mode": "Wähle den Zweck der Referenzkorrektur.",
        "threshold": "Gib eine positive ganzzahlige Evidenzanforderung ein.",
        "summary": "Bitte korrigiere die markierten Eingaben, bevor du fortfährst.",
        "generic": "Prüfe diesen Konfigurationswert.",
    },
}


def validation_message(state, key):
    return _MESSAGES.get(state.get("lang", "en"), _MESSAGES["en"])[key]


def tx_message_pattern_warning(state: Mapping, labels=None) -> str | None:
    """Return advisory setup guidance for unlike TX callsign structures.

    A slash is only a reason to check the actual message patterns and schedule;
    this does not infer firmware settings or establish protocol compatibility.
    The warning never changes field validity or canonical configuration.
    """
    if (
        state.get("val_analysis_direction") != "tx"
        or state.get("val_comp_mode") != "reference_station"
    ):
        return None
    target = normalize_ascii_upper(state.get("val_callsign"))
    reference = normalize_ascii_upper(state.get("val_ref_callsign"))
    if not is_valid_callsign(target) or not is_valid_callsign(reference):
        return None
    if ("/" in target) == ("/" in reference):
        return None
    if labels is None:
        from i18n import T
        labels = T.get(state.get("lang", "en"), T["en"])
    return (
        f"**{labels['warn_tx_message_patterns_title']}**\n\n"
        f"{labels['warn_tx_message_patterns']}"
    )


def validate_input_fields(state: Mapping, labels=None) -> dict[str, str]:
    """Validate all active fields; a pending Reference lookup is not an error."""
    if labels is None:
        from i18n import T
        labels = T.get(state.get("lang", "en"), T["en"])
    errors = {}
    message = lambda key: validation_message(state, key)
    question_key = "guided_use_case" if state.get("input_view") == "guided" else "classic_question"
    question = state.get(question_key)
    if state.get("val_analysis_direction") not in {"rx", "tx"}:
        errors[question_key] = message("question")
    target = normalize_ascii_upper(state.get("val_callsign"))
    if not is_valid_callsign(target):
        errors["val_callsign"] = labels["err_callsign_format"] if target else message("target")
    qth = normalize_ascii_upper(state.get("val_qth"))
    if not is_valid_locator(qth):
        errors["val_qth"] = labels["err_qth_format"] if qth else message("qth")
    if state.get("val_band") not in BAND_MAP:
        errors["val_band"] = message("band")
    try:
        utc_window_from_state(state)
    except (TypeError, ValueError) as exc:
        key = time_window_validation_message_key(exc) if hasattr(exc, "reason") else "err_time_invalid"
        text = labels.get(key, labels["err_time_invalid"])
        for field in TIME_WINDOW_STATE_KEYS:
            errors[field] = text
    mode = state.get("val_comp_mode", "none")
    if mode not in {"none", "reference_station", "local_neighborhood"} or (
        str(question).endswith("_benchmark") and mode == "none"
    ):
        errors["val_comp_mode"] = message("design")
    if mode == "reference_station":
        reference = normalize_ascii_upper(state.get("val_ref_callsign"))
        if not is_valid_callsign(reference):
            errors["val_ref_callsign"] = labels["err_reference_callsign_format"] if reference else message("reference")
        elif reference == target:
            errors["val_ref_callsign"] = labels["err_reference_callsign_same"]
        grid = normalize_ascii_upper(state.get("val_ref_qth"))
        if grid and not is_valid_grid4(grid):
            errors["val_ref_qth"] = labels["err_reference_grid4_format"]
    if mode == "local_neighborhood":
        radius = state.get("val_ref_radius_km", 100)
        if isinstance(radius, bool) or not isinstance(radius, (int, float)) or not 0 < radius <= MAX_DYNAMIC_RADIUS_KM:
            errors["val_ref_radius_km"] = message("radius")
    if mode != "none":
        try:
            correction = float(state.get("val_benchmark_offset_db", 0))
            if not math.isfinite(correction) or not -99.9 <= correction <= 99.9:
                raise ValueError
            if state.get("_val_benchmark_offset_db_text_error"):
                raise ValueError
        except (TypeError, ValueError):
            errors["_val_benchmark_offset_db_text"] = message("correction")
        correction_mode = state.get("val_snr_correction_mode", "no_offset")
        if correction_mode not in {"no_offset", "establish_offset", "established_offset"}:
            errors["val_snr_correction_mode"] = message("correction_mode")
    for key in ("val_min_spots" if mode != "none" else "val_min_opportunities", "val_min_stations"):
        value = state.get(key, 1)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            errors[key] = message("threshold")
    # The strict persisted-config validator covers cross-field invariants as well.
    if not errors:
        from ui.config_io import build_config_settings_from_state
        try:
            build_config_settings_from_state(state)
        except (KeyError, TypeError, ValueError) as exc:
            text = str(exc)
            mappings = {
                "snr_correction": "_val_benchmark_offset_db_text", "radius": "val_ref_radius_km",
                "distance": "val_max_peer_distance_km", "outlier": "val_report_delta_snr_outlier_candidates",
                "local_benchmark": "val_comp_mode",
            }
            field = next((value for token, value in mappings.items() if token in text), "val_comp_mode")
            errors[field] = text or message("generic")
    return errors


def get_field_error(state, key):
    if not state.get(INPUT_VALIDATION_ATTEMPTED_KEY):
        return None
    return validate_input_fields(state).get(key)


def attempt_input_validation(state, labels=None):
    state[INPUT_VALIDATION_ATTEMPTED_KEY] = True
    errors = validate_input_fields(state, labels)
    state[INPUT_FIELD_ERRORS_KEY] = errors
    if errors:
        first = next(iter(errors))
        if first in {"guided_use_case", "classic_question"}:
            node = "use_case"
        elif first == "_val_benchmark_offset_db_text":
            node = (
                "offset_calibration"
                if state.get("input_view") == "guided" and state.get("val_comp_mode") == "reference_station"
                else "reference_design"
            )
        elif first in {"val_ref_callsign", "val_ref_qth", "val_comp_mode", "val_ref_radius_km"}:
            node = "reference_design"
        elif "correction" in first or "offset" in first:
            node = "offset_calibration"
        elif first.startswith("val_min"):
            node = "scope_and_evidence"
        else:
            node = "target_and_window"
        state["guided_active_node"] = node
        state["guided_collapse_all"] = False
        state["config_panels_expanded"] = True
        state["_collapse_config_panels_once"] = False
    return errors


def validation_focus_key(state, field):
    """Translate canonical configuration fields to the active editor widget."""
    if field == "val_comp_mode":
        return "guided_reference_design" if state.get("input_view") == "guided" else "_classic_benchmark_design"
    return field
