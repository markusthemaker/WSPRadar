"""
Configuration import/export helpers for WSPRadar.

The on-disk format is intentionally JSON inside a .config file: easy to inspect,
strictly typed, dependency-free, and safe to validate before touching session state.
"""

import json
from datetime import datetime, timedelta, timezone, time as dt_time

import streamlit as st

from config import BAND_MAP, MAP_SCOPE_OPTIONS, MAX_DAYS_HISTORY, MAX_DYNAMIC_RADIUS_KM
from i18n import T
from core.math_utils import is_valid_callsign, is_valid_6char_locator


CONFIG_APP_NAME = "WSPRadar.org"
CONFIG_SCHEMA_VERSION = 3
MAX_CONFIG_BYTES = 200_000
MIN_CONFIG_DATE = datetime(2008, 1, 1, tzinfo=timezone.utc).date()

MODE_KEYS = {
    "local_neighborhood": "opt_comp_radius",
    "reference_station": "opt_comp_buddy",
    "hardware_ab": "opt_comp_self",
}
LOCAL_BENCHMARK_KEYS = {
    "local_median": "opt_local_median",
    "local_best": "opt_local_best",
}
SELF_TEST_KEYS = {
    "rx": "opt_self_rx",
    "tx": "opt_self_tx",
}
WSPR_FRAME_KEYS = {
    "frame_00_04_08": "opt_wspr_frame_00_04_08",
    "frame_02_06_10": "opt_wspr_frame_02_06_10",
}
LEGACY_WSPR_FRAME_KEYS = {
    "even": "frame_00_04_08",
    "odd": "frame_02_06_10",
}
SOLAR_KEYS = {
    "all": "opt_solar_all",
    "day": "opt_solar_day",
    "night": "opt_solar_night",
    "greyline": "opt_solar_grey",
}

MODE_VALUES = {value: key for key, value in MODE_KEYS.items()}
LOCAL_BENCHMARK_VALUES = {value: key for key, value in LOCAL_BENCHMARK_KEYS.items()}
SELF_TEST_VALUES = {value: key for key, value in SELF_TEST_KEYS.items()}
WSPR_FRAME_VALUES = {value: key for key, value in WSPR_FRAME_KEYS.items()}
WSPR_FRAME_VALUES.update({
    "opt_slot_even": "frame_00_04_08",
    "opt_slot_odd": "frame_02_06_10",
})
SOLAR_VALUES = {value: key for key, value in SOLAR_KEYS.items()}

CONFIG_KEYS = {
    "callsign",
    "qth",
    "band",
    "time_mode",
    "hours",
    "start_date",
    "end_date",
    "start_time",
    "end_time",
    "benchmark_mode",
    "local_benchmark",
    "reference_callsign",
    "neighborhood_radius_km",
    "benchmark_snr_correction_db",
    "self_test_mode",
    "setup_b_callsign",
    "target_wspr_frame",
    "reference_wspr_frame",
    "tx_ab_bin_minutes",
    "solar_state",
    "map_scope_km",
    "exclude_special_callsigns",
    "exclude_moving_stations",
    "min_joint_spots_per_station",
    "min_confirmed_opportunities_per_peer",
    "min_joint_stations_per_map_segment",
}
LEGACY_CONFIG_KEYS = {
    "target_time_slot",
    "reference_time_slot",
}
ALL_CONFIG_KEYS = CONFIG_KEYS | LEGACY_CONFIG_KEYS


def _canonical_from_translated(state_value, value_map, fallback):
    """Translate the current localized UI value into a stable config key."""
    for lang_dict in T.values():
        for translation_key, canonical in value_map.items():
            if state_value == lang_dict.get(translation_key):
                return canonical
    return fallback


def _translated_from_canonical(canonical, key_map, lang, fallback):
    """Translate a stable config key back into the current UI language."""
    translation_key = key_map.get(canonical)
    if not translation_key:
        return fallback
    return T[lang][translation_key]


def _default_config():
    today = datetime.now(timezone.utc).date()
    return {
        "callsign": "",
        "qth": "",
        "band": "20m",
        "time_mode": "last_x",
        "hours": 24,
        "start_date": (today - timedelta(days=1)).isoformat(),
        "end_date": today.isoformat(),
        "start_time": "00:00",
        "end_time": "23:59",
        "benchmark_mode": "local_neighborhood",
        "local_benchmark": "local_median",
        "reference_callsign": "",
        "neighborhood_radius_km": 100,
        "benchmark_snr_correction_db": 0.0,
        "self_test_mode": "rx",
        "setup_b_callsign": "",
        "target_wspr_frame": "frame_00_04_08",
        "reference_wspr_frame": "frame_02_06_10",
        "tx_ab_bin_minutes": 8,
        "solar_state": "all",
        "map_scope_km": 22000,
        "exclude_special_callsigns": False,
        "exclude_moving_stations": False,
        "min_joint_spots_per_station": 1,
        "min_confirmed_opportunities_per_peer": 5,
        "min_joint_stations_per_map_segment": 1,
    }


def _parse_date(value, field):
    try:
        parsed = datetime.strptime(str(value), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValueError(f"{field} must use YYYY-MM-DD format.")
    today = datetime.now(timezone.utc).date()
    if parsed < MIN_CONFIG_DATE or parsed > today:
        raise ValueError(f"{field} must be between {MIN_CONFIG_DATE.isoformat()} and {today.isoformat()}.")
    return parsed


def _parse_time(value, field):
    try:
        return datetime.strptime(str(value), "%H:%M").time()
    except (TypeError, ValueError):
        raise ValueError(f"{field} must use HH:MM format.")


def _validate_bool(value, field):
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be true or false.")
    return value


def _validate_int(value, field, min_value, max_value, allowed_values=None):
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer.")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be an integer.")
    if parsed < min_value or parsed > max_value:
        raise ValueError(f"{field} must be between {min_value} and {max_value}.")
    if allowed_values is not None and parsed not in allowed_values:
        raise ValueError(f"{field} must be one of: {', '.join(str(v) for v in allowed_values)}.")
    return parsed


def _validate_float(value, field, min_value, max_value):
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric.")
    try:
        parsed = round(float(value), 1)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be numeric.")
    if parsed < min_value or parsed > max_value:
        raise ValueError(f"{field} must be between {min_value:.1f} and {max_value:.1f}.")
    return parsed


def _validate_choice(value, field, choices):
    value = str(value)
    if value not in choices:
        raise ValueError(f"{field} must be one of: {', '.join(choices)}.")
    return value


def _validate_wspr_frame(value, field):
    value = str(value)
    value = LEGACY_WSPR_FRAME_KEYS.get(value, value)
    return _validate_choice(value, field, WSPR_FRAME_KEYS.keys())


def _validate_callsign(value, field, allow_empty=True):
    value = str(value or "").strip().upper()
    if not value and allow_empty:
        return ""
    if not is_valid_callsign(value):
        raise ValueError(f"{field} is not a valid callsign.")
    return value


def _is_valid_locator_strict(locator):
    locator = str(locator or "").strip().upper()
    if len(locator) == 4:
        return (
            "A" <= locator[0] <= "R" and
            "A" <= locator[1] <= "R" and
            locator[2].isdigit() and
            locator[3].isdigit()
        )
    return is_valid_6char_locator(locator)


def _validate_locator(value, field, allow_empty=True):
    value = str(value or "").strip().upper()
    if not value and allow_empty:
        return ""
    if not _is_valid_locator_strict(value):
        raise ValueError(f"{field} is not a valid 4- or 6-character Maidenhead locator.")
    return value


def build_config_payload():
    """Return a JSON byte payload and a timestamped .config filename."""
    lang = st.session_state.lang
    defaults = _default_config()
    state = st.session_state
    time_mode = "last_x" if state.get("val_time_mode", T[lang]["opt_last_x"]) == T[lang]["opt_last_x"] else "custom"
    config = {
        "callsign": state.get("val_callsign", defaults["callsign"]).strip().upper(),
        "qth": state.get("val_qth", defaults["qth"]).strip().upper(),
        "band": state.get("val_band", defaults["band"]),
        "time_mode": time_mode,
        "hours": int(state.get("val_hours", defaults["hours"])),
        "start_date": state.get("val_start_d", datetime.fromisoformat(defaults["start_date"]).date()).isoformat(),
        "end_date": state.get("val_end_d", datetime.fromisoformat(defaults["end_date"]).date()).isoformat(),
        "start_time": state.get("val_start_t", dt_time(0, 0)).strftime("%H:%M"),
        "end_time": state.get("val_end_t", dt_time(23, 59)).strftime("%H:%M"),
        "benchmark_mode": _canonical_from_translated(state.get("val_comp_mode", T[lang]["opt_comp_radius"]), MODE_VALUES, "local_neighborhood"),
        "local_benchmark": _canonical_from_translated(state.get("val_local_benchmark", T[lang]["opt_local_median"]), LOCAL_BENCHMARK_VALUES, "local_median"),
        "reference_callsign": state.get("val_ref_callsign", defaults["reference_callsign"]).strip().upper(),
        "neighborhood_radius_km": int(state.get("val_ref_radius_km", defaults["neighborhood_radius_km"])),
        "benchmark_snr_correction_db": round(float(state.get("val_benchmark_offset_db", defaults["benchmark_snr_correction_db"])), 1),
        "self_test_mode": _canonical_from_translated(state.get("val_self_test_mode", T[lang]["opt_self_rx"]), SELF_TEST_VALUES, "rx"),
        "setup_b_callsign": state.get("val_self_call_b", defaults["setup_b_callsign"]).strip().upper(),
        "target_wspr_frame": _canonical_from_translated(state.get("val_target_wspr_frame", T[lang]["opt_wspr_frame_00_04_08"]), WSPR_FRAME_VALUES, "frame_00_04_08"),
        "reference_wspr_frame": _canonical_from_translated(state.get("val_reference_wspr_frame", T[lang]["opt_wspr_frame_02_06_10"]), WSPR_FRAME_VALUES, "frame_02_06_10"),
        "tx_ab_bin_minutes": int(state.get("val_tx_ab_bin_minutes", defaults["tx_ab_bin_minutes"])),
        "solar_state": _canonical_from_translated(state.get("val_solar", T[lang]["opt_solar_all"]), SOLAR_VALUES, "all"),
        "map_scope_km": int(state.get("val_max_dist", defaults["map_scope_km"])),
        "exclude_special_callsigns": bool(state.get("val_exclude_special_callsigns", defaults["exclude_special_callsigns"])),
        "exclude_moving_stations": bool(state.get("val_filter_moving", defaults["exclude_moving_stations"])),
        "min_joint_spots_per_station": int(state.get("val_min_spots", defaults["min_joint_spots_per_station"])),
        "min_confirmed_opportunities_per_peer": int(state.get("val_min_opportunities", defaults["min_confirmed_opportunities_per_peer"])),
        "min_joint_stations_per_map_segment": int(state.get("val_min_stations", defaults["min_joint_stations_per_map_segment"])),
    }
    payload = {
        "app": CONFIG_APP_NAME,
        "schema_version": CONFIG_SCHEMA_VERSION,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "config": config,
    }
    timestamp = datetime.now().strftime("%Y_%m__%d__%H_%M")
    return json.dumps(payload, indent=2).encode("utf-8"), f"WSPRadar_{timestamp}.config"


def validate_config_upload(raw_bytes):
    """Parse and validate uploaded config bytes. Returns normalized config and warnings."""
    if not raw_bytes:
        raise ValueError("The uploaded config file is empty.")
    if len(raw_bytes) > MAX_CONFIG_BYTES:
        raise ValueError("The uploaded config file is too large.")

    try:
        payload = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("The uploaded config file is not valid UTF-8 JSON.")

    if not isinstance(payload, dict):
        raise ValueError("The uploaded config file must contain a JSON object.")
    if payload.get("app") != CONFIG_APP_NAME:
        raise ValueError(f"The uploaded config is not a {CONFIG_APP_NAME} config file.")
    if not isinstance(payload.get("config"), dict):
        raise ValueError("The uploaded config file does not contain a config object.")

    warnings = []
    raw_config = payload["config"]
    unknown_keys = sorted(set(raw_config.keys()) - ALL_CONFIG_KEYS)
    if unknown_keys:
        warnings.append(f"Ignored unknown config field(s): {', '.join(unknown_keys)}.")

    config = _default_config()
    for key in CONFIG_KEYS:
        if key in raw_config:
            config[key] = raw_config[key]
    if "target_wspr_frame" not in raw_config and "target_time_slot" in raw_config:
        config["target_wspr_frame"] = raw_config["target_time_slot"]
    if "reference_wspr_frame" not in raw_config and "reference_time_slot" in raw_config:
        config["reference_wspr_frame"] = raw_config["reference_time_slot"]

    normalized = {}
    normalized["callsign"] = _validate_callsign(config["callsign"], "callsign")
    normalized["qth"] = _validate_locator(config["qth"], "qth")
    normalized["band"] = _validate_choice(config["band"], "band", BAND_MAP.keys())
    normalized["time_mode"] = _validate_choice(config["time_mode"], "time_mode", ["last_x", "custom"])
    normalized["hours"] = _validate_int(config["hours"], "hours", 1, 168)
    normalized["start_date"] = _parse_date(config["start_date"], "start_date")
    normalized["end_date"] = _parse_date(config["end_date"], "end_date")
    normalized["start_time"] = _parse_time(config["start_time"], "start_time")
    normalized["end_time"] = _parse_time(config["end_time"], "end_time")
    normalized["benchmark_mode"] = _validate_choice(config["benchmark_mode"], "benchmark_mode", MODE_KEYS.keys())
    normalized["local_benchmark"] = _validate_choice(config["local_benchmark"], "local_benchmark", LOCAL_BENCHMARK_KEYS.keys())
    normalized["reference_callsign"] = _validate_callsign(config["reference_callsign"], "reference_callsign")
    normalized["neighborhood_radius_km"] = _validate_int(config["neighborhood_radius_km"], "neighborhood_radius_km", 10, MAX_DYNAMIC_RADIUS_KM)
    normalized["benchmark_snr_correction_db"] = _validate_float(config["benchmark_snr_correction_db"], "benchmark_snr_correction_db", -99.9, 99.9)
    normalized["self_test_mode"] = _validate_choice(config["self_test_mode"], "self_test_mode", SELF_TEST_KEYS.keys())
    normalized["setup_b_callsign"] = _validate_callsign(config["setup_b_callsign"], "setup_b_callsign")
    normalized["target_wspr_frame"] = _validate_wspr_frame(config["target_wspr_frame"], "target_wspr_frame")
    normalized["reference_wspr_frame"] = _validate_wspr_frame(config["reference_wspr_frame"], "reference_wspr_frame")
    normalized["tx_ab_bin_minutes"] = _validate_int(config["tx_ab_bin_minutes"], "tx_ab_bin_minutes", 4, 20, allowed_values=[4, 8, 12, 16, 20])
    normalized["solar_state"] = _validate_choice(config["solar_state"], "solar_state", SOLAR_KEYS.keys())
    normalized["map_scope_km"] = _validate_int(config["map_scope_km"], "map_scope_km", min(MAP_SCOPE_OPTIONS), max(MAP_SCOPE_OPTIONS), allowed_values=MAP_SCOPE_OPTIONS)
    normalized["exclude_special_callsigns"] = _validate_bool(config["exclude_special_callsigns"], "exclude_special_callsigns")
    normalized["exclude_moving_stations"] = _validate_bool(config["exclude_moving_stations"], "exclude_moving_stations")
    normalized["min_joint_spots_per_station"] = _validate_int(config["min_joint_spots_per_station"], "min_joint_spots_per_station", 1, 50)
    normalized["min_confirmed_opportunities_per_peer"] = _validate_int(
        config["min_confirmed_opportunities_per_peer"],
        "min_confirmed_opportunities_per_peer",
        1,
        100,
    )
    normalized["min_joint_stations_per_map_segment"] = _validate_int(config["min_joint_stations_per_map_segment"], "min_joint_stations_per_map_segment", 1, 10)

    if normalized["end_date"] < normalized["start_date"]:
        raise ValueError("end_date must not be before start_date.")
    start_dt = datetime.combine(normalized["start_date"], normalized["start_time"])
    end_dt = datetime.combine(normalized["end_date"], normalized["end_time"])
    if end_dt <= start_dt:
        raise ValueError("The configured end date/time must be after the start date/time.")
    if end_dt - start_dt > timedelta(days=MAX_DAYS_HISTORY):
        raise ValueError(f"The configured date/time range must not exceed {MAX_DAYS_HISTORY} days.")
    if (
        normalized["benchmark_mode"] == "reference_station" and
        normalized["callsign"] and
        normalized["reference_callsign"] and
        normalized["callsign"] == normalized["reference_callsign"]
    ):
        raise ValueError("reference_callsign must be different from callsign in reference-station mode.")
    if (
        normalized["benchmark_mode"] == "hardware_ab" and
        normalized["self_test_mode"] == "rx" and
        normalized["callsign"] and
        normalized["setup_b_callsign"] and
        normalized["callsign"] == normalized["setup_b_callsign"]
    ):
        raise ValueError("setup_b_callsign must be different from callsign in RX A/B mode.")
    if (
        normalized["benchmark_mode"] == "hardware_ab" and
        normalized["self_test_mode"] == "tx" and
        normalized["target_wspr_frame"] == normalized["reference_wspr_frame"]
    ):
        raise ValueError("target_wspr_frame and reference_wspr_frame must be different in TX A/B mode.")

    return normalized, warnings


def apply_config_values(config):
    """Apply a validated canonical config to Streamlit session state."""
    lang = st.session_state.lang
    t = T[lang]

    st.session_state.is_demo_mode = False
    st.session_state.active_demo_profile = None
    st.session_state.demo_view_defaults = {}
    st.session_state.show_demo_launcher = False
    st.session_state.show_config_loader = False
    st.session_state.config_panels_expanded = True
    st.session_state._collapse_config_panels_once = False
    st.session_state.run_mode = None

    st.session_state.val_callsign = config["callsign"]
    st.session_state.val_qth = config["qth"]
    st.session_state.val_band = config["band"]
    st.session_state.val_time_mode = t["opt_last_x"] if config["time_mode"] == "last_x" else t["opt_custom"]
    st.session_state.val_hours = config["hours"]
    st.session_state.val_start_d = config["start_date"]
    st.session_state.val_end_d = config["end_date"]
    st.session_state.val_start_t = config["start_time"]
    st.session_state.val_end_t = config["end_time"]
    st.session_state.val_comp_mode = _translated_from_canonical(config["benchmark_mode"], MODE_KEYS, lang, t["opt_comp_radius"])
    st.session_state.val_local_benchmark = _translated_from_canonical(config["local_benchmark"], LOCAL_BENCHMARK_KEYS, lang, t["opt_local_median"])
    st.session_state.val_ref_callsign = config["reference_callsign"]
    st.session_state.val_ref_radius_km = config["neighborhood_radius_km"]
    st.session_state.val_benchmark_offset_db = config["benchmark_snr_correction_db"]
    st.session_state.val_self_test_mode = _translated_from_canonical(config["self_test_mode"], SELF_TEST_KEYS, lang, t["opt_self_rx"])
    st.session_state.val_self_call_b = config["setup_b_callsign"]
    st.session_state.val_target_wspr_frame = _translated_from_canonical(config["target_wspr_frame"], WSPR_FRAME_KEYS, lang, t["opt_wspr_frame_00_04_08"])
    st.session_state.val_reference_wspr_frame = _translated_from_canonical(config["reference_wspr_frame"], WSPR_FRAME_KEYS, lang, t["opt_wspr_frame_02_06_10"])
    st.session_state.val_tx_ab_bin_minutes = config["tx_ab_bin_minutes"]
    st.session_state.val_solar = _translated_from_canonical(config["solar_state"], SOLAR_KEYS, lang, t["opt_solar_all"])
    st.session_state.val_max_dist = config["map_scope_km"]
    st.session_state.val_exclude_special_callsigns = config["exclude_special_callsigns"]
    st.session_state.val_filter_moving = config["exclude_moving_stations"]
    st.session_state.val_min_spots = config["min_joint_spots_per_station"]
    st.session_state.val_min_opportunities = config["min_confirmed_opportunities_per_peer"]
    st.session_state.val_min_stations = config["min_joint_stations_per_map_segment"]

    for key in list(st.session_state.keys()):
        if key.startswith("img_buf_"):
            del st.session_state[key]
