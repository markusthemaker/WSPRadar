"""
Configuration import/export helpers for WSPRadar.

The version-1 on-disk format is strict UTF-8 JSON inside a ``.config`` file.
Unsupported schema versions are rejected rather than interpreted with guessed
defaults.
"""

import hashlib
import json
import math
import re
import unicodedata
from copy import deepcopy
from datetime import datetime, timedelta, timezone, time as dt_time

import streamlit as st

from config import APP_VERSION, BAND_MAP, DEFAULT_BAND, MAP_SCOPE_OPTIONS, MAX_DAYS_HISTORY, MAX_DYNAMIC_RADIUS_KM
from config.config_schema import (
    ANALYSIS_DIRECTIONS,
    COMPARISON_MODES,
    CONFIG_APP_NAME,
    CONFIG_DOCUMENT_FORMAT,
    CONFIG_KEYS,
    CONFIG_SCHEMA_VERSION,
    EVIDENCE_TIME_BINS,
    SEGMENT_DIRECTION_OPTIONS,
    SEGMENT_EVIDENCE_TIME_BINS,
    SEGMENT_RANGE_OPTIONS,
    SEGMENT_SELECTION_ALL,
    STATION_SELECTION_ALL,
    STATION_EVIDENCE_TEMPORAL_VIEWS,
    TX_AB_REPEAT_INTERVAL_OPTIONS,
)
from config.config_codec import prepare_config_document
from config.json_utils import decode_strict_json_bytes
from i18n import T
from core.input_validation import is_valid_6char_locator, is_valid_callsign
from ui.analysis_submission_state import cancel_analysis_submission
from ui.result_state import reset_result_state


MAX_CONFIG_BYTES = 200_000
MIN_CONFIG_DATE = datetime(2008, 1, 1, tzinfo=timezone.utc).date()
MODE_KEYS = {
    "none": "opt_comp_none",
    "hardware_ab": "opt_comp_self",
    "reference_station": "opt_comp_buddy",
    "local_neighborhood": "opt_comp_radius",
}
LOCAL_BENCHMARK_KEYS = {
    "local_median": "opt_local_median",
    "local_best": "opt_local_best",
}
SOLAR_KEYS = {
    "all": "opt_solar_all",
    "day": "opt_solar_day",
    "night": "opt_solar_night",
    "greyline": "opt_solar_grey",
}

MODE_VALUES = {value: key for key, value in MODE_KEYS.items()}
LOCAL_BENCHMARK_VALUES = {value: key for key, value in LOCAL_BENCHMARK_KEYS.items()}
SOLAR_VALUES = {value: key for key, value in SOLAR_KEYS.items()}

def _canonical_from_translated(state_value, value_map, fallback):
    """Translate the current localized UI value into a stable config key."""
    for lang_dict in T.values():
        for translation_key, canonical in value_map.items():
            if state_value == lang_dict.get(translation_key):
                return canonical
    return fallback


def canonical_from_translated(state_value, value_map, fallback):
    """Translate a localized UI value into a stable config key."""
    return _canonical_from_translated(state_value, value_map, fallback)


def _translated_from_canonical(canonical, key_map, lang, fallback):
    """Translate a stable config key back into the current UI language."""
    translation_key = key_map.get(canonical)
    if not translation_key:
        return fallback
    return T[lang][translation_key]


def _default_config():
    today = datetime.now(timezone.utc).date()
    return {
        "analysis_direction": None,
        "callsign": "",
        "qth": "",
        "band": DEFAULT_BAND,
        "time_mode": "last_x",
        "hours": 24,
        "start_date": (today - timedelta(days=1)).isoformat(),
        "end_date": today.isoformat(),
        "start_time": "00:00",
        "end_time": "23:59",
        "benchmark_mode": "none",
        "local_benchmark": "local_median",
        "reference_callsign": "",
        "neighborhood_radius_km": 100,
        "benchmark_snr_correction_db": 0.0,
        "setup_b_callsign": "",
        "tx_ab_repeat_interval_minutes": 10,
        "tx_ab_target_start_minute": 0,
        "tx_ab_reference_start_minute": 2,
        "solar_state": "all",
        "map_scope_km": 22000,
        "exclude_special_callsigns": False,
        "exclude_moving_stations": False,
        "min_joint_spots_per_station": 1,
        "min_confirmed_opportunities_per_peer": 5,
        "min_joint_stations_per_map_segment": 1,
        "show_non_joint": False,
        "show_zero_target": False,
        "selected_ranges_compare": SEGMENT_SELECTION_ALL,
        "selected_directions_compare": SEGMENT_SELECTION_ALL,
        "selected_ranges_absolute": SEGMENT_SELECTION_ALL,
        "selected_directions_absolute": SEGMENT_SELECTION_ALL,
        "segment_evidence_time_bin_compare": "auto",
        "station_evidence_time_bin_compare": "3h",
        "station_evidence_temporal_view_compare": "chronological",
        "selected_stations_compare": None,
        "station_evidence_time_bin_absolute": "3h",
        "selected_stations_absolute": None,
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
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer.")
    parsed = value
    if parsed < min_value or parsed > max_value:
        raise ValueError(f"{field} must be between {min_value} and {max_value}.")
    if allowed_values is not None and parsed not in allowed_values:
        raise ValueError(f"{field} must be one of: {', '.join(str(v) for v in allowed_values)}.")
    return parsed


def _validate_float(value, field, min_value, max_value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric.")
    parsed = round(float(value), 1)
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be finite.")
    if parsed < min_value or parsed > max_value:
        raise ValueError(f"{field} must be between {min_value:.1f} and {max_value:.1f}.")
    return parsed


def _validate_choice(value, field, choices):
    value = str(value)
    if value not in choices:
        raise ValueError(f"{field} must be one of: {', '.join(choices)}.")
    return value


def _validate_tx_ab_schedule_values(
    repeat_interval_minutes,
    target_start_minute,
    reference_start_minute,
):
    """Validate one canonical periodic TX A/B schedule."""
    repeat_interval_minutes = _validate_int(
        repeat_interval_minutes,
        "repeat_interval_minutes",
        min(TX_AB_REPEAT_INTERVAL_OPTIONS),
        max(TX_AB_REPEAT_INTERVAL_OPTIONS),
        allowed_values=TX_AB_REPEAT_INTERVAL_OPTIONS,
    )
    permitted_starts = tuple(range(0, repeat_interval_minutes, 2))
    target_start_minute = _validate_int(
        target_start_minute,
        "target_start_minute",
        0,
        repeat_interval_minutes - 1,
        allowed_values=permitted_starts,
    )
    reference_start_minute = _validate_int(
        reference_start_minute,
        "reference_start_minute",
        0,
        repeat_interval_minutes - 1,
        allowed_values=permitted_starts,
    )
    if target_start_minute == reference_start_minute:
        raise ValueError(
            "target_start_minute and reference_start_minute must be different "
            "in TX A/B mode."
        )

    return {
        "tx_ab_repeat_interval_minutes": repeat_interval_minutes,
        "tx_ab_target_start_minute": target_start_minute,
        "tx_ab_reference_start_minute": reference_start_minute,
    }


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


def _validate_selected_stations(value, field):
    """Normalize automatic, all-station, or explicit station-selection intent."""
    if value is None:
        return None
    if value == STATION_SELECTION_ALL:
        return STATION_SELECTION_ALL
    if not isinstance(value, list):
        raise ValueError(
            f"{field} must be null, {STATION_SELECTION_ALL!r}, or a JSON array."
        )

    normalized_stations = []
    seen_station_identities = set()
    for station_index, station in enumerate(value):
        station_field = f"{field}[{station_index}]"
        station = _validate_object_fields(
            station,
            station_field,
            {"callsign", "locator"},
        )
        callsign = _validate_callsign(
            station["callsign"],
            f"{station_field}.callsign",
            allow_empty=False,
        )
        locator = _validate_locator(
            station["locator"],
            f"{station_field}.locator",
            allow_empty=False,
        )
        station_identity = (callsign, locator)
        if station_identity in seen_station_identities:
            raise ValueError(
                f"{field} contains duplicate station identity "
                f"{callsign}/{locator}."
            )
        seen_station_identities.add(station_identity)
        normalized_stations.append(
            {"callsign": callsign, "locator": locator}
        )
    return normalized_stations


def _validate_segment_selection(value, field, choices):
    """Normalize explicit All or one non-empty canonical segment selection."""
    if value == SEGMENT_SELECTION_ALL:
        return SEGMENT_SELECTION_ALL
    if not isinstance(value, list) or not value:
        raise ValueError(
            f"{field} must be {SEGMENT_SELECTION_ALL!r} or a non-empty JSON array."
        )

    normalized_values = []
    seen_values = set()
    for selection_index, selected_value in enumerate(value):
        selection_field = f"{field}[{selection_index}]"
        if not isinstance(selected_value, str) or selected_value not in choices:
            raise ValueError(
                f"{selection_field} must be one of: {', '.join(choices)}."
            )
        if selected_value in seen_values:
            raise ValueError(f"{field} contains duplicate value {selected_value!r}.")
        seen_values.add(selected_value)
        normalized_values.append(selected_value)
    return normalized_values


def _date_state_to_iso(value):
    """Serialize one Streamlit date value as an ISO calendar date."""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _time_state_to_hhmm(value):
    """Serialize one Streamlit time value as a UTC ``HH:MM`` string."""
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")
    return str(value)


def _time_selection_from_frozen_window(frozen_time_window):
    """Return a custom UTC selection for one resolved, aware analysis interval."""
    if frozen_time_window is None:
        return None
    if (
        not isinstance(frozen_time_window, (tuple, list))
        or len(frozen_time_window) != 2
    ):
        raise ValueError("frozen_time_window must contain a UTC start and end.")
    start_utc, end_utc = frozen_time_window
    if not isinstance(start_utc, datetime) or not isinstance(end_utc, datetime):
        raise ValueError("The frozen UTC start and end must be datetimes.")
    if start_utc.tzinfo is None or end_utc.tzinfo is None:
        raise ValueError("The frozen UTC start and end must be timezone-aware.")
    start_utc = start_utc.astimezone(timezone.utc)
    end_utc = end_utc.astimezone(timezone.utc)
    if end_utc <= start_utc:
        raise ValueError("The frozen UTC end must be after its start.")
    if end_utc - start_utc > timedelta(days=MAX_DAYS_HISTORY):
        raise ValueError(
            f"The frozen UTC range must not exceed {MAX_DAYS_HISTORY} days."
        )
    return {
        "mode": "custom",
        "start_date": start_utc.date().isoformat(),
        "end_date": end_utc.date().isoformat(),
        "start_time_utc": start_utc.strftime("%H:%M"),
        "end_time_utc": end_utc.strftime("%H:%M"),
    }


def _settings_from_session_state(state, lang, *, frozen_time_window=None):
    """Build grouped version-1 settings from applicable Streamlit controls."""
    defaults = _default_config()
    analysis_direction = _validate_choice(
        str(state.get("val_analysis_direction", "")).lower(),
        "analysis_direction",
        ANALYSIS_DIRECTIONS,
    )
    time_mode = (
        "last_x"
        if state.get("val_time_mode", T[lang]["opt_last_x"])
        == T[lang]["opt_last_x"]
        else "custom"
    )
    frozen_time_selection = _time_selection_from_frozen_window(frozen_time_window)
    if frozen_time_selection is not None:
        time_selection = frozen_time_selection
    elif time_mode == "last_x":
        time_selection = {
            "mode": "last_x",
            "hours": int(state.get("val_hours", defaults["hours"])),
        }
    else:
        time_selection = {
            "mode": "custom",
            "start_date": _date_state_to_iso(
                state.get(
                    "val_start_d",
                    datetime.fromisoformat(defaults["start_date"]).date(),
                )
            ),
            "end_date": _date_state_to_iso(
                state.get(
                    "val_end_d",
                    datetime.fromisoformat(defaults["end_date"]).date(),
                )
            ),
            "start_time_utc": _time_state_to_hhmm(
                state.get("val_start_t", dt_time(0, 0))
            ),
            "end_time_utc": _time_state_to_hhmm(
                state.get("val_end_t", dt_time(23, 59))
            ),
        }

    benchmark_mode = _canonical_from_translated(
        state.get("val_comp_mode", T[lang]["opt_comp_none"]),
        MODE_VALUES,
        "none",
    )
    comparison_parameters = {"mode": benchmark_mode}
    if benchmark_mode != "none":
        comparison_parameters["snr_correction_db"] = round(
            float(
                state.get(
                    "val_benchmark_offset_db",
                    defaults["benchmark_snr_correction_db"],
                )
            ),
            1,
        )
    if benchmark_mode == "reference_station":
        comparison_parameters["reference_callsign"] = str(
            state.get("val_ref_callsign", defaults["reference_callsign"])
        ).strip().upper()
    elif benchmark_mode == "local_neighborhood":
        comparison_parameters["local_benchmark"] = _canonical_from_translated(
            state.get(
                "val_local_benchmark",
                T[lang]["opt_local_median"],
            ),
            LOCAL_BENCHMARK_VALUES,
            "local_median",
        )
        comparison_parameters["neighborhood_radius_km"] = int(
            state.get(
                "val_ref_radius_km",
                defaults["neighborhood_radius_km"],
            )
        )
    elif benchmark_mode == "hardware_ab" and analysis_direction == "rx":
        comparison_parameters["setup_b_callsign"] = str(
            state.get("val_self_call_b", defaults["setup_b_callsign"])
        ).strip().upper()
    elif benchmark_mode == "hardware_ab":
        comparison_parameters.update(
            {
                "repeat_interval_minutes": int(
                    state.get(
                        "val_tx_ab_repeat_interval_minutes",
                        defaults["tx_ab_repeat_interval_minutes"],
                    )
                ),
                "target_start_minute": int(
                    state.get(
                        "val_tx_ab_target_start_minute",
                        defaults["tx_ab_target_start_minute"],
                    )
                ),
                "reference_start_minute": int(
                    state.get(
                        "val_tx_ab_reference_start_minute",
                        defaults["tx_ab_reference_start_minute"],
                    )
                ),
            }
        )
    advanced_parameters = {
        "solar_state": _canonical_from_translated(
            state.get("val_solar", T[lang]["opt_solar_all"]),
            SOLAR_VALUES,
            "all",
        ),
        "map_scope_km": int(
            state.get("val_max_dist", defaults["map_scope_km"])
        ),
        "exclude_special_callsigns": bool(
            state.get(
                "val_exclude_special_callsigns",
                defaults["exclude_special_callsigns"],
            )
        ),
        "exclude_moving_stations": bool(
            state.get("val_filter_moving", defaults["exclude_moving_stations"])
        ),
        "min_confirmed_opportunities_per_peer": int(
            state.get(
                "val_min_opportunities",
                defaults["min_confirmed_opportunities_per_peer"],
            )
        ),
        "min_joint_stations_per_map_segment": int(
            state.get(
                "val_min_stations",
                defaults["min_joint_stations_per_map_segment"],
            )
        ),
    }
    if benchmark_mode != "none":
        advanced_parameters["min_joint_spots_per_station"] = int(
            state.get(
                "val_min_spots",
                defaults["min_joint_spots_per_station"],
            )
        )

    results_view = {
        "success": {
            "selected_ranges": _validate_segment_selection(
                state.get(
                    "val_results_selected_ranges_absolute",
                    defaults["selected_ranges_absolute"],
                ),
                "results_view.success.selected_ranges",
                SEGMENT_RANGE_OPTIONS,
            ),
            "selected_directions": _validate_segment_selection(
                state.get(
                    "val_results_selected_directions_absolute",
                    defaults["selected_directions_absolute"],
                ),
                "results_view.success.selected_directions",
                SEGMENT_DIRECTION_OPTIONS,
            ),
            "show_zero_target": bool(
                state.get(
                    "val_results_show_zero_target",
                    defaults["show_zero_target"],
                )
            ),
            "station_evidence_time_bin": (
                state.get("val_results_time_bin_absolute")
                or defaults["station_evidence_time_bin_absolute"]
            ),
            "selected_stations": _validate_selected_stations(
                state.get(
                    "val_results_selected_stations_absolute",
                    defaults["selected_stations_absolute"],
                ),
                "results_view.success.selected_stations",
            ),
        }
    }
    if benchmark_mode != "none":
        results_view["compare"] = {
                "selected_ranges": _validate_segment_selection(
                    state.get(
                        "val_results_selected_ranges_compare",
                        defaults["selected_ranges_compare"],
                    ),
                    "results_view.compare.selected_ranges",
                    SEGMENT_RANGE_OPTIONS,
                ),
                "selected_directions": _validate_segment_selection(
                    state.get(
                        "val_results_selected_directions_compare",
                        defaults["selected_directions_compare"],
                    ),
                    "results_view.compare.selected_directions",
                    SEGMENT_DIRECTION_OPTIONS,
                ),
                "show_non_joint": bool(
                    state.get(
                        "val_results_show_non_joint",
                        defaults["show_non_joint"],
                    )
                ),
                "segment_evidence_time_bin": (
                    state.get("val_results_segment_time_bin_compare")
                    or defaults["segment_evidence_time_bin_compare"]
                ),
                "station_evidence_time_bin": (
                    state.get("val_results_time_bin_compare")
                    or defaults["station_evidence_time_bin_compare"]
                ),
                "station_evidence_temporal_view": (
                    state.get("val_results_station_temporal_view_compare")
                    or defaults["station_evidence_temporal_view_compare"]
                ),
                "selected_stations": _validate_selected_stations(
                    state.get(
                        "val_results_selected_stations_compare",
                        defaults["selected_stations_compare"],
                    ),
                    "results_view.compare.selected_stations",
                ),
            }

    return {
        "core_parameters": {
            "analysis_direction": analysis_direction,
            "callsign": str(
                state.get("val_callsign", defaults["callsign"])
            ).strip().upper(),
            "qth": str(state.get("val_qth", defaults["qth"])).strip().upper(),
            "band": state.get("val_band", defaults["band"]),
            "time_selection": time_selection,
        },
        "comparison_parameters": comparison_parameters,
        "advanced_parameters": advanced_parameters,
        "results_view": results_view,
    }


def derive_config_profile_id(title):
    """Derive a deterministic, schema-safe profile ID from one display title."""
    normalized_title = str(title or "").strip()
    if not normalized_title:
        raise ValueError("A profile title is required before deriving its ID.")
    ascii_title = (
        unicodedata.normalize("NFKD", normalized_title)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    profile_slug = re.sub(r"[^a-z0-9]+", "-", ascii_title).strip("-")
    if not profile_slug:
        profile_slug = "profile"
    title_digest = hashlib.sha256(
        normalized_title.casefold().encode("utf-8")
    ).hexdigest()[:8]
    maximum_slug_length = 64 - len(title_digest) - 1
    profile_slug = profile_slug[:maximum_slug_length].rstrip("-") or "profile"
    return f"{profile_slug}-{title_digest}"


def _localized_fallback_text(localized_values, language):
    """Return the displayed fallback when one language has no own text."""
    if not isinstance(localized_values, dict):
        return ""
    for fallback_language in ("en",):
        if fallback_language == language:
            continue
        fallback_value = localized_values.get(fallback_language)
        if isinstance(fallback_value, str) and fallback_value.strip():
            return fallback_value.strip()
    for fallback_value in localized_values.values():
        if isinstance(fallback_value, str) and fallback_value.strip():
            return fallback_value.strip()
    return ""


def _localized_profile_for_save(
    state,
    *,
    language,
    title,
    description,
    profile_id,
):
    """Update one language in loaded profile metadata without losing others."""
    normalized_title = str(title or "").strip()
    if not normalized_title:
        raise ValueError("The config profile title is required.")
    normalized_language = str(language or "").strip().lower()
    if not normalized_language:
        raise ValueError("The config profile language is required.")

    loaded_profile = state.get("val_config_profile")
    if not isinstance(loaded_profile, dict):
        loaded_profile = {}
    titles = deepcopy(loaded_profile.get("title", {}))
    if not isinstance(titles, dict):
        titles = {}
    existing_title = titles.get(normalized_language)
    title_fallback = _localized_fallback_text(titles, normalized_language)
    if existing_title is not None or normalized_title != title_fallback:
        titles[normalized_language] = normalized_title

    descriptions = deepcopy(loaded_profile.get("description", {}))
    if not isinstance(descriptions, dict):
        descriptions = {}
    normalized_description = str(description or "").strip()
    existing_description = descriptions.get(normalized_language)
    description_fallback = _localized_fallback_text(
        descriptions,
        normalized_language,
    )
    if normalized_description and (
        existing_description is not None
        or normalized_description != description_fallback
    ):
        descriptions[normalized_language] = normalized_description
    elif not normalized_description:
        descriptions.pop(normalized_language, None)

    if profile_id is None:
        normalized_profile_id = str(loaded_profile.get("id", "")).strip()
    else:
        normalized_profile_id = str(profile_id).strip()
    if not normalized_profile_id:
        normalized_profile_id = derive_config_profile_id(normalized_title)

    profile = {
        "id": normalized_profile_id,
        "title": titles,
    }
    if descriptions:
        profile["description"] = descriptions
    return profile


def _config_save_components(
    state,
    *,
    language,
    title,
    description="",
    profile_id=None,
    frozen_time_window=None,
):
    """Build and validate the durable settings, profile, and extensions blocks."""
    settings = _settings_from_session_state(
        state,
        language,
        frozen_time_window=frozen_time_window,
    )
    normalize_config_settings(settings)
    if title is None:
        loaded_profile = state.get("val_config_profile")
        profile = deepcopy(loaded_profile) if isinstance(loaded_profile, dict) else None
    else:
        profile = _localized_profile_for_save(
            state,
            language=language,
            title=title,
            description=description,
            profile_id=profile_id,
        )
    extensions = deepcopy(state.get("val_config_extensions", {}))
    if not isinstance(extensions, dict):
        raise ValueError("The preserved config extensions must be a JSON object.")
    return settings, profile, extensions


def build_config_state_signature(
    *,
    title,
    description="",
    profile_id=None,
    language=None,
    frozen_time_window=None,
    state=None,
):
    """Return a stable digest for the current save inputs and durable UI state."""
    state = st.session_state if state is None else state
    language = language or state.get("lang", "en")
    settings, profile, extensions = _config_save_components(
        state,
        language=language,
        title=title,
        description=description,
        profile_id=profile_id,
        frozen_time_window=frozen_time_window,
    )
    signature_payload = {
        "settings": settings,
        "profile": profile,
        "extensions": extensions,
    }
    serialized_signature_payload = json.dumps(
        signature_payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized_signature_payload).hexdigest()


def build_config_payload(
    *,
    title=None,
    description="",
    profile_id=None,
    language=None,
    frozen_time_window=None,
    state=None,
    exported_utc=None,
):
    """Return one ordinary v1 config document and a suitable filename.

    ``frozen_time_window`` converts a Last-X selection into the supplied
    resolved UTC interval. Loaded profile localizations and extensions survive
    re-saving; writer provenance is regenerated for this download. Interactive
    saves supply ``title`` and therefore always carry profile metadata. A
    noninteractive analysis export may omit it; an already loaded profile is
    still retained when available.
    """
    state = st.session_state if state is None else state
    language = language or state.get("lang", "en")
    settings, profile, extensions = _config_save_components(
        state,
        language=language,
        title=title,
        description=description,
        profile_id=profile_id,
        frozen_time_window=frozen_time_window,
    )
    exported_utc = exported_utc or datetime.now(timezone.utc)
    if exported_utc.tzinfo is None:
        raise ValueError("exported_utc must be timezone-aware.")
    exported_utc = exported_utc.astimezone(timezone.utc).replace(microsecond=0)
    unprepared_payload = {
        "format": CONFIG_DOCUMENT_FORMAT,
        "schema_version": CONFIG_SCHEMA_VERSION,
        "metadata": {
            "created_utc": exported_utc.isoformat().replace("+00:00", "Z"),
            "generator": {
                "application": CONFIG_APP_NAME,
                "version": APP_VERSION,
            },
        },
    }
    if profile is not None:
        unprepared_payload["profile"] = profile
    unprepared_payload["settings"] = settings
    unprepared_payload["extensions"] = extensions
    payload = prepare_config_document(unprepared_payload)
    filename = (
        f"{profile['id']}.config"
        if profile is not None
        else f"WSPRadar_config_{exported_utc.strftime('%Y-%m-%dT%H%MZ')}.config"
    )
    return (
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False).encode(
            "utf-8"
        ),
        filename,
    )


def _validate_object_fields(value, field, required_fields):
    """Return one object after enforcing its exact active-branch fields."""
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a JSON object.")
    missing_fields = sorted(set(required_fields) - set(value))
    if missing_fields:
        raise ValueError(
            f"Missing required {field} field(s): " + ", ".join(missing_fields) + "."
        )
    unknown_fields = sorted(set(value) - set(required_fields))
    if unknown_fields:
        raise ValueError(
            f"Unknown {field} field(s): " + ", ".join(unknown_fields) + "."
        )
    return value


def normalize_config_settings(raw_settings):
    """Validate grouped active-only settings and return canonical flat UI values."""
    settings = _validate_object_fields(raw_settings, "settings", CONFIG_KEYS)
    core = _validate_object_fields(
        settings["core_parameters"],
        "settings.core_parameters",
        {"analysis_direction", "callsign", "qth", "band", "time_selection"},
    )

    normalized = {
        "analysis_direction": _validate_choice(
            core["analysis_direction"],
            "analysis_direction",
            ANALYSIS_DIRECTIONS,
        ),
        "callsign": _validate_callsign(core["callsign"], "callsign"),
        "qth": _validate_locator(core["qth"], "qth"),
        "band": _validate_choice(core["band"], "band", BAND_MAP.keys()),
    }

    time_selection = core["time_selection"]
    if not isinstance(time_selection, dict):
        raise ValueError("settings.core_parameters.time_selection must be a JSON object.")
    time_mode = _validate_choice(
        time_selection.get("mode"),
        "time_selection.mode",
        {"last_x", "custom"},
    )
    normalized["time_mode"] = time_mode
    if time_mode == "last_x":
        _validate_object_fields(
            time_selection,
            "settings.core_parameters.time_selection",
            {"mode", "hours"},
        )
        normalized["hours"] = _validate_int(
            time_selection["hours"], "hours", 1, 168
        )
    else:
        _validate_object_fields(
            time_selection,
            "settings.core_parameters.time_selection",
            {
                "mode",
                "start_date",
                "end_date",
                "start_time_utc",
                "end_time_utc",
            },
        )
        normalized["start_date"] = _parse_date(
            time_selection["start_date"], "start_date"
        )
        normalized["end_date"] = _parse_date(
            time_selection["end_date"], "end_date"
        )
        normalized["start_time"] = _parse_time(
            time_selection["start_time_utc"], "start_time_utc"
        )
        normalized["end_time"] = _parse_time(
            time_selection["end_time_utc"], "end_time_utc"
        )
        if normalized["end_date"] < normalized["start_date"]:
            raise ValueError("end_date must not be before start_date.")
        start_datetime = datetime.combine(
            normalized["start_date"], normalized["start_time"]
        )
        end_datetime = datetime.combine(
            normalized["end_date"], normalized["end_time"]
        )
        if end_datetime <= start_datetime:
            raise ValueError(
                "The configured end date/time must be after the start date/time."
            )
        if end_datetime - start_datetime > timedelta(days=MAX_DAYS_HISTORY):
            raise ValueError(
                f"The configured date/time range must not exceed "
                f"{MAX_DAYS_HISTORY} days."
            )

    comparison = settings["comparison_parameters"]
    if not isinstance(comparison, dict):
        raise ValueError("settings.comparison_parameters must be a JSON object.")
    benchmark_mode = _validate_choice(
        comparison.get("mode"),
        "comparison_parameters.mode",
        COMPARISON_MODES,
    )
    normalized["benchmark_mode"] = benchmark_mode
    comparison_fields = {"mode"}
    if benchmark_mode == "reference_station":
        comparison_fields |= {"reference_callsign", "snr_correction_db"}
    elif benchmark_mode == "local_neighborhood":
        comparison_fields |= {
            "local_benchmark",
            "neighborhood_radius_km",
            "snr_correction_db",
        }
    elif benchmark_mode == "hardware_ab":
        comparison_fields.add("snr_correction_db")
        if normalized["analysis_direction"] == "rx":
            comparison_fields.add("setup_b_callsign")
        else:
            comparison_fields |= {
                "repeat_interval_minutes",
                "target_start_minute",
                "reference_start_minute",
            }
    _validate_object_fields(
        comparison,
        "settings.comparison_parameters",
        comparison_fields,
    )

    if benchmark_mode != "none":
        normalized["benchmark_snr_correction_db"] = _validate_float(
            comparison["snr_correction_db"],
            "snr_correction_db",
            -99.9,
            99.9,
        )
    if benchmark_mode == "reference_station":
        normalized["reference_callsign"] = _validate_callsign(
            comparison["reference_callsign"], "reference_callsign"
        )
        if (
            normalized["callsign"]
            and normalized["reference_callsign"]
            and normalized["callsign"] == normalized["reference_callsign"]
        ):
            raise ValueError(
                "reference_callsign must be different from callsign in "
                "reference-station mode."
            )
    elif benchmark_mode == "local_neighborhood":
        normalized["local_benchmark"] = _validate_choice(
            comparison["local_benchmark"],
            "local_benchmark",
            LOCAL_BENCHMARK_KEYS.keys(),
        )
        normalized["neighborhood_radius_km"] = _validate_int(
            comparison["neighborhood_radius_km"],
            "neighborhood_radius_km",
            10,
            MAX_DYNAMIC_RADIUS_KM,
        )
    elif benchmark_mode == "hardware_ab" and normalized["analysis_direction"] == "rx":
        normalized["setup_b_callsign"] = _validate_callsign(
            comparison["setup_b_callsign"], "setup_b_callsign"
        )
        if (
            normalized["callsign"]
            and normalized["setup_b_callsign"]
            and normalized["callsign"] == normalized["setup_b_callsign"]
        ):
            raise ValueError(
                "setup_b_callsign must be different from callsign in RX A/B mode."
            )
    elif benchmark_mode == "hardware_ab":
        normalized.update(
            _validate_tx_ab_schedule_values(
                comparison["repeat_interval_minutes"],
                comparison["target_start_minute"],
                comparison["reference_start_minute"],
            )
        )

    advanced_fields = {
        "solar_state",
        "map_scope_km",
        "exclude_special_callsigns",
        "exclude_moving_stations",
        "min_confirmed_opportunities_per_peer",
        "min_joint_stations_per_map_segment",
    }
    if benchmark_mode != "none":
        advanced_fields.add("min_joint_spots_per_station")
    advanced = _validate_object_fields(
        settings["advanced_parameters"],
        "settings.advanced_parameters",
        advanced_fields,
    )
    normalized["solar_state"] = _validate_choice(
        advanced["solar_state"], "solar_state", SOLAR_KEYS.keys()
    )
    normalized["map_scope_km"] = _validate_int(
        advanced["map_scope_km"],
        "map_scope_km",
        min(MAP_SCOPE_OPTIONS),
        max(MAP_SCOPE_OPTIONS),
        allowed_values=MAP_SCOPE_OPTIONS,
    )
    normalized["exclude_special_callsigns"] = _validate_bool(
        advanced["exclude_special_callsigns"], "exclude_special_callsigns"
    )
    normalized["exclude_moving_stations"] = _validate_bool(
        advanced["exclude_moving_stations"], "exclude_moving_stations"
    )
    normalized["min_confirmed_opportunities_per_peer"] = _validate_int(
        advanced["min_confirmed_opportunities_per_peer"],
        "min_confirmed_opportunities_per_peer",
        1,
        100,
    )
    normalized["min_joint_stations_per_map_segment"] = _validate_int(
        advanced["min_joint_stations_per_map_segment"],
        "min_joint_stations_per_map_segment",
        1,
        10,
    )
    if benchmark_mode != "none":
        normalized["min_joint_spots_per_station"] = _validate_int(
            advanced["min_joint_spots_per_station"],
            "min_joint_spots_per_station",
            1,
            50,
        )

    results_fields = {"success"}
    if benchmark_mode != "none":
        results_fields.add("compare")
    results_view = _validate_object_fields(
        settings["results_view"],
        "settings.results_view",
        results_fields,
    )
    success_results_view = _validate_object_fields(
        results_view["success"],
        "settings.results_view.success",
        {
            "selected_ranges",
            "selected_directions",
            "show_zero_target",
            "station_evidence_time_bin",
            "selected_stations",
        },
    )
    normalized["selected_ranges_absolute"] = _validate_segment_selection(
        success_results_view["selected_ranges"],
        "results_view.success.selected_ranges",
        SEGMENT_RANGE_OPTIONS,
    )
    normalized["selected_directions_absolute"] = _validate_segment_selection(
        success_results_view["selected_directions"],
        "results_view.success.selected_directions",
        SEGMENT_DIRECTION_OPTIONS,
    )
    normalized["show_zero_target"] = _validate_bool(
        success_results_view["show_zero_target"],
        "results_view.success.show_zero_target",
    )
    normalized["station_evidence_time_bin_absolute"] = _validate_choice(
        success_results_view["station_evidence_time_bin"],
        "results_view.success.station_evidence_time_bin",
        EVIDENCE_TIME_BINS,
    )
    normalized["selected_stations_absolute"] = _validate_selected_stations(
        success_results_view["selected_stations"],
        "results_view.success.selected_stations",
    )
    if benchmark_mode != "none":
        compare_results_view = _validate_object_fields(
            results_view["compare"],
            "settings.results_view.compare",
            {
                "selected_ranges",
                "selected_directions",
                "show_non_joint",
                "segment_evidence_time_bin",
                "station_evidence_time_bin",
                "station_evidence_temporal_view",
                "selected_stations",
            },
        )
        normalized["selected_ranges_compare"] = _validate_segment_selection(
            compare_results_view["selected_ranges"],
            "results_view.compare.selected_ranges",
            SEGMENT_RANGE_OPTIONS,
        )
        normalized["selected_directions_compare"] = _validate_segment_selection(
            compare_results_view["selected_directions"],
            "results_view.compare.selected_directions",
            SEGMENT_DIRECTION_OPTIONS,
        )
        normalized["show_non_joint"] = _validate_bool(
            compare_results_view["show_non_joint"],
            "results_view.compare.show_non_joint",
        )
        normalized["segment_evidence_time_bin_compare"] = _validate_choice(
            compare_results_view["segment_evidence_time_bin"],
            "results_view.compare.segment_evidence_time_bin",
            SEGMENT_EVIDENCE_TIME_BINS,
        )
        normalized["station_evidence_time_bin_compare"] = _validate_choice(
            compare_results_view["station_evidence_time_bin"],
            "results_view.compare.station_evidence_time_bin",
            EVIDENCE_TIME_BINS,
        )
        normalized["station_evidence_temporal_view_compare"] = _validate_choice(
            compare_results_view["station_evidence_temporal_view"],
            "results_view.compare.station_evidence_temporal_view",
            STATION_EVIDENCE_TEMPORAL_VIEWS,
        )
        normalized["selected_stations_compare"] = _validate_selected_stations(
            compare_results_view["selected_stations"],
            "results_view.compare.selected_stations",
        )

    return normalized


def validate_config_document(payload):
    """Validate and normalize one decoded versioned WSPRadar config document."""
    prepared_document = prepare_config_document(payload)
    normalized_config = normalize_config_settings(prepared_document["settings"])
    normalized_config["profile"] = deepcopy(prepared_document.get("profile"))
    normalized_config["extensions"] = deepcopy(
        prepared_document.get("extensions", {})
    )
    return normalized_config


def validate_config_upload(raw_bytes):
    """Strictly decode and validate an uploaded versioned config document."""
    if not raw_bytes:
        raise ValueError("The uploaded config file is empty.")
    if len(raw_bytes) > MAX_CONFIG_BYTES:
        raise ValueError("The uploaded config file is too large.")
    payload = decode_strict_json_bytes(
        raw_bytes,
        document_name="uploaded config file",
    )
    return validate_config_document(payload), []


def apply_config_state_values(config, session_state):
    """Apply active values, loaded metadata, and canonical inactive defaults."""
    lang = session_state.lang
    t = T[lang]
    defaults = _default_config()

    session_state.val_analysis_direction = config["analysis_direction"]
    session_state.val_callsign = config["callsign"]
    session_state.val_qth = config["qth"]
    session_state.val_band = config["band"]
    session_state.val_time_mode = t["opt_last_x"] if config["time_mode"] == "last_x" else t["opt_custom"]
    session_state.val_hours = config.get("hours", defaults["hours"])
    session_state.val_start_d = config.get(
        "start_date", datetime.fromisoformat(defaults["start_date"]).date()
    )
    session_state.val_end_d = config.get(
        "end_date", datetime.fromisoformat(defaults["end_date"]).date()
    )
    session_state.val_start_t = config.get("start_time", dt_time(0, 0))
    session_state.val_end_t = config.get("end_time", dt_time(23, 59))
    session_state.val_comp_mode = _translated_from_canonical(config["benchmark_mode"], MODE_KEYS, lang, t["opt_comp_none"])
    session_state.val_local_benchmark = _translated_from_canonical(
        config.get("local_benchmark", defaults["local_benchmark"]),
        LOCAL_BENCHMARK_KEYS,
        lang,
        t["opt_local_median"],
    )
    session_state.val_ref_callsign = config.get(
        "reference_callsign", defaults["reference_callsign"]
    )
    session_state.val_ref_radius_km = config.get(
        "neighborhood_radius_km", defaults["neighborhood_radius_km"]
    )
    session_state.val_benchmark_offset_db = config.get(
        "benchmark_snr_correction_db", defaults["benchmark_snr_correction_db"]
    )
    session_state.val_self_call_b = config.get(
        "setup_b_callsign", defaults["setup_b_callsign"]
    )
    session_state.val_tx_ab_repeat_interval_minutes = config.get(
        "tx_ab_repeat_interval_minutes",
        defaults["tx_ab_repeat_interval_minutes"],
    )
    session_state.val_tx_ab_target_start_minute = config.get(
        "tx_ab_target_start_minute",
        defaults["tx_ab_target_start_minute"],
    )
    session_state.val_tx_ab_reference_start_minute = config.get(
        "tx_ab_reference_start_minute",
        defaults["tx_ab_reference_start_minute"],
    )
    session_state.val_solar = _translated_from_canonical(config["solar_state"], SOLAR_KEYS, lang, t["opt_solar_all"])
    session_state.val_max_dist = config["map_scope_km"]
    session_state.val_exclude_special_callsigns = config["exclude_special_callsigns"]
    session_state.val_filter_moving = config["exclude_moving_stations"]
    session_state.val_min_spots = config.get(
        "min_joint_spots_per_station", defaults["min_joint_spots_per_station"]
    )
    session_state.val_min_opportunities = config["min_confirmed_opportunities_per_peer"]
    session_state.val_min_stations = config["min_joint_stations_per_map_segment"]
    session_state.val_results_show_non_joint = config.get("show_non_joint")
    session_state.val_results_show_zero_target = config["show_zero_target"]
    session_state.val_results_selected_ranges_compare = deepcopy(
        config.get("selected_ranges_compare", defaults["selected_ranges_compare"])
    )
    session_state.val_results_selected_directions_compare = deepcopy(
        config.get(
            "selected_directions_compare",
            defaults["selected_directions_compare"],
        )
    )
    session_state.val_results_selected_ranges_absolute = deepcopy(
        config["selected_ranges_absolute"]
    )
    session_state.val_results_selected_directions_absolute = deepcopy(
        config["selected_directions_absolute"]
    )
    session_state.val_results_time_bin_compare = config.get(
        "station_evidence_time_bin_compare"
    )
    session_state.val_results_time_bin_absolute = config[
        "station_evidence_time_bin_absolute"
    ]
    session_state.val_results_segment_time_bin_compare = config.get(
        "segment_evidence_time_bin_compare",
        defaults["segment_evidence_time_bin_compare"],
    )
    session_state.val_results_station_temporal_view_compare = config.get(
        "station_evidence_temporal_view_compare",
        defaults["station_evidence_temporal_view_compare"],
    )
    session_state.val_results_selected_stations_compare = deepcopy(
        config.get("selected_stations_compare")
    )
    session_state.val_results_selected_stations_absolute = deepcopy(
        config.get("selected_stations_absolute")
    )
    session_state.val_config_profile = deepcopy(config.get("profile"))
    session_state.loaded_config_profile = deepcopy(config.get("profile"))
    session_state.val_config_extensions = deepcopy(config.get("extensions", {}))


def apply_config_values(config):
    """Apply validated settings and reset the editable UI lifecycle."""
    session_state = st.session_state

    cancel_analysis_submission(session_state)
    session_state.is_demo_mode = False
    session_state.active_demo_profile = None
    session_state.show_demo_launcher = False
    session_state.show_config_loader = False
    session_state.config_panels_expanded = True
    session_state._collapse_config_panels_once = False
    session_state.run_mode = None
    reset_result_state(session_state)
    for state_key in tuple(session_state.keys()):
        if state_key.startswith("config_save_"):
            session_state.pop(state_key, None)
    apply_config_state_values(config, session_state)

    for key in list(session_state.keys()):
        if key.startswith("img_buf_"):
            del session_state[key]
