"""Version-1 adapter between public query parameters and canonical config state.

The public URL is deliberately not a second scientific configuration model.
Parsing builds the existing version-1 settings hierarchy, validates it through
``ui.config_io.normalize_config_settings``, and only then applies the resulting
canonical values through the normal configuration lifecycle. Serialization
travels in the opposite direction from validated session state.
"""

from __future__ import annotations

import logging
import math
import re
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlencode, urlsplit, urlunsplit

from config import (
    APP_URL,
    SEGMENT_DIRECTION_OPTIONS,
    SEGMENT_EVIDENCE_TIME_BINS,
    SEGMENT_RANGE_OPTIONS,
    SEGMENT_SELECTION_ALL,
)
from core.time_utils import format_utc_minute, parse_utc_minute
from ui.analysis_submission_state import begin_analysis_submission
from ui.config_io import (
    apply_config_state_values,
    apply_config_values_to_state,
    build_config_settings_from_state,
    normalize_config_settings,
)
from ui.page_navigation import RESULTS_INSPECTION_ANCHOR_ID
from ui.url_synchronizer import render_url_query_synchronizer


LOGGER = logging.getLogger(__name__)

URL_V1_VERSION = "1"
URL_V1_PUBLIC_MODES = (
    "performance",
    "hardware_ab",
    "reference_station",
    "local_neighborhood",
)
URL_V1_MODE_TO_CONFIG = {
    "performance": "none",
    "hardware_ab": "hardware_ab",
    "reference_station": "reference_station",
    "local_neighborhood": "local_neighborhood",
}
URL_V1_CONFIG_TO_MODE = {
    config_mode: public_mode
    for public_mode, config_mode in URL_V1_MODE_TO_CONFIG.items()
}

URL_V1_RANGE_TOKENS = (
    "0-2500",
    "2500-5000",
    "5000-10000",
    "10000-15000",
    "15000-20000",
    "20000-22000",
)
URL_V1_RANGE_TO_CONFIG = dict(
    zip(URL_V1_RANGE_TOKENS, SEGMENT_RANGE_OPTIONS, strict=True)
)
URL_V1_CONFIG_TO_RANGE = {
    config_range: public_range
    for public_range, config_range in URL_V1_RANGE_TO_CONFIG.items()
}

URL_V1_DEFAULTS = {
    "solar": "all",
    "max_distance_km": 22000,
    "exclude_special": False,
    "exclude_moving": False,
    "min_joint_spots": 1,
    "min_opportunities": 5,
    "min_segment_stations": 1,
    "ranges": SEGMENT_SELECTION_ALL,
    "directions": SEGMENT_SELECTION_ALL,
    "segment_bin": "auto",
    "station_bin": "3h",
    "temporal_view": "chronological",
    "selected_stations": None,
    "show_zero": False,
    "show_unpaired": False,
}

URL_V1_PARAMETER_ORDER = (
    "v",
    "run",
    "direction",
    "callsign",
    "qth",
    "band",
    "from",
    "to",
    "mode",
    "reference",
    "reference_qth",
    "local_benchmark",
    "radius_km",
    "tx_ab_method",
    "repeat_min",
    "target_start_min",
    "reference_start_min",
    "snr_correction_mode",
    "snr_correction_db",
    "solar",
    "max_distance_km",
    "exclude_special",
    "exclude_moving",
    "min_joint_spots",
    "min_opportunities",
    "min_segment_stations",
    "ranges",
    "directions",
    "segment_bin",
    "station_bin",
    "temporal_view",
    "selected_station",
    "show_zero",
    "show_unpaired",
)
URL_V1_RETIRED_PARAMETERS = (
    "hours",
    "anchor",
)
URL_V1_OWNED_QUERY_KEYS = URL_V1_PARAMETER_ORDER + URL_V1_RETIRED_PARAMETERS

URL_HYDRATION_SIGNATURE_KEY = "_url_v1_initial_hydration_signature"
URL_HYDRATION_ERROR_KEY = "_url_v1_initial_hydration_error"
URL_REPLAY_NAVIGATION_PENDING_KEY = "_url_v1_replay_navigation_pending"
URL_QUERY_SYNCHRONIZER_PAGE_KEY = "wspradar_url_query_synchronizer_page"
URL_QUERY_SYNCHRONIZER_FRAGMENT_KEY = "wspradar_url_query_synchronizer_fragment"

_CORE_PARAMETERS = {
    "v",
    "run",
    "direction",
    "callsign",
    "qth",
    "band",
    "from",
    "to",
    "mode",
}
_COMMON_ADVANCED_PARAMETERS = {
    "solar",
    "max_distance_km",
    "exclude_special",
    "exclude_moving",
    "min_opportunities",
    "min_segment_stations",
}
_COMMON_RESULT_PARAMETERS = {
    "ranges",
    "directions",
    "segment_bin",
    "station_bin",
    "selected_station",
}
_INTEGER_PATTERN = re.compile(r"^-?(?:0|[1-9]\d*)$")
_DECIMAL_PATTERN = re.compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?$")


class UrlStateError(ValueError):
    """Describe a rejected public URL with a stable localization category."""

    def __init__(self, code: str, message: str):
        """Store a safe display category separately from technical detail."""
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class UrlHydrationResult:
    """Report whether one initial query applied config or scheduled a replay."""

    was_processed: bool
    config_was_applied: bool
    replay_was_scheduled: bool
    error_code: str | None = None


def collect_query_values(query_parameters: Any) -> dict[str, tuple[str, ...]]:
    """Copy a Streamlit-like query object without losing duplicate values."""
    collected: dict[str, tuple[str, ...]] = {}
    for raw_key in query_parameters:
        key = str(raw_key)
        if hasattr(query_parameters, "get_all"):
            raw_values = query_parameters.get_all(raw_key)
        else:
            raw_values = query_parameters[raw_key]
        if isinstance(raw_values, str):
            values = (raw_values,)
        elif isinstance(raw_values, Sequence):
            values = tuple(str(value) for value in raw_values)
        else:
            values = (str(raw_values),)
        collected[key] = values
    return collected


def _coerce_query_value_sequence(raw_values: Any) -> tuple[str, ...]:
    """Return one query value sequence while preserving duplicates."""
    if isinstance(raw_values, str):
        return (raw_values,)
    if isinstance(raw_values, Sequence):
        return tuple(str(value) for value in raw_values)
    return (str(raw_values),)


def parse_url_query(
    query_values: Mapping[str, Sequence[str] | str],
) -> dict[str, str] | None:
    """Return one duplicate-free URL-v1 parameter map, ignoring unrelated keys."""
    supplied_parameters: dict[str, str] = {}
    for key in URL_V1_OWNED_QUERY_KEYS:
        if key not in query_values:
            continue
        values = _coerce_query_value_sequence(query_values[key])
        if len(values) != 1:
            raise UrlStateError(
                "invalid",
                f"Duplicate WSPRadar query parameter: {key!r}.",
            )
        supplied_parameters[key] = values[0]

    if not supplied_parameters:
        return None
    retired_parameters = sorted(
        set(supplied_parameters).intersection(URL_V1_RETIRED_PARAMETERS)
    )
    if retired_parameters:
        raise UrlStateError(
            "invalid",
            "Retired WSPRadar query parameters are not supported: "
            + ", ".join(retired_parameters),
        )
    if "v" not in supplied_parameters:
        raise UrlStateError("invalid", "Missing required URL parameter: v.")
    if supplied_parameters["v"] != URL_V1_VERSION:
        raise UrlStateError(
            "unsupported_version",
            f"Unsupported WSPRadar URL version: {supplied_parameters['v']!r}.",
        )
    if "run" in supplied_parameters and supplied_parameters["run"] != "1":
        raise UrlStateError("invalid", "run must be exactly 1 when supplied.")
    return supplied_parameters


def _require_parameter(parameters: Mapping[str, str], key: str) -> str:
    """Return one required non-empty URL value."""
    if key not in parameters or not parameters[key]:
        raise UrlStateError("invalid", f"Missing required URL parameter: {key}.")
    return parameters[key]


def _parse_integer(parameters: Mapping[str, str], key: str, default: int) -> int:
    """Parse one canonical base-10 URL integer."""
    if key not in parameters:
        return default
    raw_value = parameters[key]
    if _INTEGER_PATTERN.fullmatch(raw_value) is None:
        raise UrlStateError("invalid", f"{key} must be a canonical integer.")
    return int(raw_value)


def _parse_decimal(parameters: Mapping[str, str], key: str) -> float:
    """Parse one finite non-exponential URL decimal."""
    raw_value = _require_parameter(parameters, key)
    if _DECIMAL_PATTERN.fullmatch(raw_value) is None:
        raise UrlStateError("invalid", f"{key} must be a canonical decimal.")
    try:
        parsed_value = Decimal(raw_value)
    except InvalidOperation as error:
        raise UrlStateError("invalid", f"{key} must be a finite decimal.") from error
    numeric_value = float(parsed_value)
    if not math.isfinite(numeric_value):
        raise UrlStateError("invalid", f"{key} must be a finite decimal.")
    return numeric_value


def _parse_boolean_flag(parameters: Mapping[str, str], key: str) -> bool:
    """Parse one presence-sensitive URL boolean represented only by ``1``."""
    if key not in parameters:
        return False
    if parameters[key] != "1":
        raise UrlStateError("invalid", f"{key} must be exactly 1 when supplied.")
    return True


def _parse_ordered_selection(
    parameters: Mapping[str, str],
    key: str,
    *,
    public_order: Sequence[str],
    public_to_config: Mapping[str, str] | None = None,
) -> str | list[str]:
    """Parse one unique comma list and return canonical config ordering."""
    if key not in parameters:
        return SEGMENT_SELECTION_ALL
    tokens = parameters[key].split(",")
    if not tokens or any(not token for token in tokens):
        raise UrlStateError("invalid", f"{key} must contain a non-empty token list.")
    if len(set(tokens)) != len(tokens):
        raise UrlStateError("invalid", f"{key} contains duplicate tokens.")
    unknown_tokens = sorted(set(tokens).difference(public_order))
    if unknown_tokens:
        raise UrlStateError(
            "invalid",
            f"{key} contains unsupported tokens: {', '.join(unknown_tokens)}.",
        )
    selected_tokens = set(tokens)
    if selected_tokens == set(public_order):
        return SEGMENT_SELECTION_ALL
    ordered_tokens = [token for token in public_order if token in selected_tokens]
    if public_to_config is None:
        return ordered_tokens
    return [public_to_config[token] for token in ordered_tokens]


def _parse_selected_station(
    parameters: Mapping[str, str],
) -> None | list[dict[str, str]]:
    """Parse omitted, explicit-none, or exactly one public station identity."""
    if "selected_station" not in parameters:
        return None
    station_value = parameters["selected_station"]
    if station_value == "none":
        return []
    if station_value.count("@") != 1:
        raise UrlStateError(
            "invalid",
            "selected_station must use CALLSIGN@LOCATOR or the token none.",
        )
    callsign, locator = station_value.split("@", 1)
    if not callsign or not locator:
        raise UrlStateError(
            "invalid",
            "selected_station must contain both a callsign and locator.",
        )
    return [{"callsign": callsign, "locator": locator}]


def _comparison_contract(
    parameters: Mapping[str, str],
    *,
    public_mode: str,
    direction: str,
) -> tuple[set[str], set[str], dict[str, Any]]:
    """Return allowed/required URL keys and one canonical comparison object."""
    comparison: dict[str, Any] = {
        "mode": URL_V1_MODE_TO_CONFIG[public_mode],
    }
    if public_mode == "performance":
        return set(), set(), comparison

    required = {"snr_correction_mode", "snr_correction_db"}
    allowed = set(required)
    comparison["snr_correction_mode"] = _require_parameter(
        parameters,
        "snr_correction_mode",
    )
    comparison["snr_correction_db"] = _parse_decimal(
        parameters,
        "snr_correction_db",
    )

    if public_mode == "reference_station":
        required.update({"reference", "reference_qth"})
        allowed.update(required)
        comparison["reference_callsign"] = _require_parameter(
            parameters,
            "reference",
        )
        comparison["reference_qth"] = _require_parameter(
            parameters,
            "reference_qth",
        )
    elif public_mode == "local_neighborhood":
        required.update({"local_benchmark", "radius_km"})
        allowed.update(required)
        comparison["local_benchmark"] = _require_parameter(
            parameters,
            "local_benchmark",
        )
        _require_parameter(parameters, "radius_km")
        comparison["neighborhood_radius_km"] = _parse_integer(
            parameters,
            "radius_km",
            0,
        )
    elif direction == "rx":
        required.add("reference")
        allowed.add("reference")
        comparison["reference_callsign"] = _require_parameter(
            parameters,
            "reference",
        )
    else:
        required.add("tx_ab_method")
        allowed.add("tx_ab_method")
        tx_ab_method = _require_parameter(parameters, "tx_ab_method")
        comparison["tx_ab_method"] = tx_ab_method
        if tx_ab_method == "simultaneous":
            required.add("reference")
            allowed.add("reference")
            comparison["reference_callsign"] = _require_parameter(
                parameters,
                "reference",
            )
        elif tx_ab_method == "sequential":
            schedule_parameters = {
                "repeat_min",
                "target_start_min",
                "reference_start_min",
            }
            required.update(schedule_parameters)
            allowed.update(schedule_parameters)
            for schedule_parameter in schedule_parameters:
                _require_parameter(parameters, schedule_parameter)
            comparison.update(
                {
                    "repeat_interval_minutes": _parse_integer(
                        parameters,
                        "repeat_min",
                        0,
                    ),
                    "target_start_minute": _parse_integer(
                        parameters,
                        "target_start_min",
                        0,
                    ),
                    "reference_start_minute": _parse_integer(
                        parameters,
                        "reference_start_min",
                        0,
                    ),
                }
            )
        else:
            raise UrlStateError(
                "invalid",
                "tx_ab_method must be simultaneous or sequential.",
            )
    return allowed, required, comparison


def _default_success_results_view() -> dict[str, Any]:
    """Return stable URL-v1 defaults for the Performance result branch."""
    return {
        "selected_ranges": URL_V1_DEFAULTS["ranges"],
        "selected_directions": URL_V1_DEFAULTS["directions"],
        "show_zero_target": URL_V1_DEFAULTS["show_zero"],
        "segment_evidence_time_bin": URL_V1_DEFAULTS["segment_bin"],
        "station_evidence_time_bin": URL_V1_DEFAULTS["station_bin"],
        "selected_stations": URL_V1_DEFAULTS["selected_stations"],
    }


def _default_compare_results_view() -> dict[str, Any]:
    """Return stable URL-v1 defaults for the Compare result branch."""
    return {
        "selected_ranges": URL_V1_DEFAULTS["ranges"],
        "selected_directions": URL_V1_DEFAULTS["directions"],
        "show_non_joint": URL_V1_DEFAULTS["show_unpaired"],
        "segment_evidence_time_bin": URL_V1_DEFAULTS["segment_bin"],
        "station_evidence_time_bin": URL_V1_DEFAULTS["station_bin"],
        "station_evidence_temporal_view": URL_V1_DEFAULTS["temporal_view"],
        "selected_stations": URL_V1_DEFAULTS["selected_stations"],
    }


def build_config_from_url(parameters: Mapping[str, str]) -> dict[str, Any]:
    """Build and fully validate one canonical config from parsed URL-v1 values."""
    if parameters.get("v") != URL_V1_VERSION:
        raise UrlStateError(
            "unsupported_version",
            f"Unsupported WSPRadar URL version: {parameters.get('v')!r}.",
        )
    if "run" in parameters and parameters["run"] != "1":
        raise UrlStateError("invalid", "run must be exactly 1 when supplied.")
    required_core = {
        "v",
        "direction",
        "callsign",
        "qth",
        "band",
        "from",
        "to",
        "mode",
    }
    missing_core = sorted(required_core.difference(parameters))
    if missing_core:
        raise UrlStateError(
            "invalid",
            f"Missing required URL parameters: {', '.join(missing_core)}.",
        )

    direction = _require_parameter(parameters, "direction")
    if direction not in {"rx", "tx"}:
        raise UrlStateError("invalid", "direction must be rx or tx.")
    public_mode = _require_parameter(parameters, "mode")
    if public_mode not in URL_V1_PUBLIC_MODES:
        raise UrlStateError(
            "invalid",
            f"Unsupported URL analysis mode: {public_mode!r}.",
        )

    comparison_allowed, _comparison_required, comparison = _comparison_contract(
        parameters,
        public_mode=public_mode,
        direction=direction,
    )
    result_allowed = set(_COMMON_RESULT_PARAMETERS)
    if public_mode == "performance":
        result_allowed.add("show_zero")
    else:
        result_allowed.update({"temporal_view", "show_unpaired"})
    advanced_allowed = set(_COMMON_ADVANCED_PARAMETERS)
    if public_mode != "performance":
        advanced_allowed.add("min_joint_spots")

    allowed_parameters = (
        _CORE_PARAMETERS
        | comparison_allowed
        | advanced_allowed
        | result_allowed
    )
    inapplicable_parameters = sorted(set(parameters).difference(allowed_parameters))
    if inapplicable_parameters:
        raise UrlStateError(
            "invalid",
            "URL parameters are not applicable to the selected analysis: "
            + ", ".join(inapplicable_parameters),
        )

    try:
        start_utc = parse_utc_minute(
            _require_parameter(parameters, "from"),
            field="from",
        )
        end_utc = parse_utc_minute(
            _require_parameter(parameters, "to"),
            field="to",
        )
    except ValueError as error:
        raise UrlStateError("invalid", str(error)) from error
    selected_ranges = _parse_ordered_selection(
        parameters,
        "ranges",
        public_order=URL_V1_RANGE_TOKENS,
        public_to_config=URL_V1_RANGE_TO_CONFIG,
    )
    selected_directions = _parse_ordered_selection(
        parameters,
        "directions",
        public_order=SEGMENT_DIRECTION_OPTIONS,
    )
    selected_stations = _parse_selected_station(parameters)

    active_results_view: dict[str, Any]
    results_view = {"success": _default_success_results_view()}
    if public_mode == "performance":
        active_results_view = results_view["success"]
        active_results_view["show_zero_target"] = _parse_boolean_flag(
            parameters,
            "show_zero",
        )
    else:
        results_view["compare"] = _default_compare_results_view()
        active_results_view = results_view["compare"]
        active_results_view["show_non_joint"] = _parse_boolean_flag(
            parameters,
            "show_unpaired",
        )
        active_results_view["station_evidence_temporal_view"] = parameters.get(
            "temporal_view",
            URL_V1_DEFAULTS["temporal_view"],
        )
    active_results_view.update(
        {
            "selected_ranges": selected_ranges,
            "selected_directions": selected_directions,
            "segment_evidence_time_bin": parameters.get(
                "segment_bin",
                URL_V1_DEFAULTS["segment_bin"],
            ),
            "station_evidence_time_bin": parameters.get(
                "station_bin",
                URL_V1_DEFAULTS["station_bin"],
            ),
            "selected_stations": selected_stations,
        }
    )

    advanced_parameters = {
        "solar_state": parameters.get("solar", URL_V1_DEFAULTS["solar"]),
        "max_peer_distance_km": _parse_integer(
            parameters,
            "max_distance_km",
            URL_V1_DEFAULTS["max_distance_km"],
        ),
        "exclude_special_callsigns": _parse_boolean_flag(
            parameters,
            "exclude_special",
        ),
        "exclude_moving_stations": _parse_boolean_flag(
            parameters,
            "exclude_moving",
        ),
        "min_confirmed_opportunities_per_peer": _parse_integer(
            parameters,
            "min_opportunities",
            URL_V1_DEFAULTS["min_opportunities"],
        ),
        "min_joint_stations_per_map_segment": _parse_integer(
            parameters,
            "min_segment_stations",
            URL_V1_DEFAULTS["min_segment_stations"],
        ),
    }
    if public_mode != "performance":
        advanced_parameters["min_joint_spots_per_station"] = _parse_integer(
            parameters,
            "min_joint_spots",
            URL_V1_DEFAULTS["min_joint_spots"],
        )

    settings = {
        "core_parameters": {
            "analysis_direction": direction,
            "callsign": _require_parameter(parameters, "callsign"),
            "qth": _require_parameter(parameters, "qth"),
            "band": _require_parameter(parameters, "band"),
            "time_selection": {
                "start_utc": format_utc_minute(start_utc),
                "end_utc": format_utc_minute(end_utc),
            },
        },
        "comparison_parameters": comparison,
        "advanced_parameters": advanced_parameters,
        "results_view": results_view,
    }
    try:
        normalized_config = normalize_config_settings(settings)
        _require_complete_normalized_config(normalized_config)
    except UrlStateError:
        raise
    except ValueError as error:
        raise UrlStateError(
            "invalid",
            f"The URL does not describe a valid WSPRadar configuration: {error}",
        ) from error
    return normalized_config


def _require_complete_normalized_config(config: Mapping[str, Any]) -> None:
    """Reject config-valid empty identities that cannot form a runnable URL."""
    if not config.get("callsign"):
        raise UrlStateError("invalid", "callsign must not be empty.")
    if not config.get("qth"):
        raise UrlStateError("invalid", "qth must not be empty.")
    benchmark_mode = config.get("benchmark_mode")
    direction = config.get("analysis_direction")
    requires_reference_callsign = (
        benchmark_mode == "reference_station"
        or (
            benchmark_mode == "hardware_ab"
            and (
                direction == "rx"
                or config.get("tx_ab_method") == "simultaneous"
            )
        )
    )
    if requires_reference_callsign and not config.get("reference_callsign"):
        raise UrlStateError("invalid", "reference must not be empty.")
    if benchmark_mode == "reference_station" and not config.get("reference_qth"):
        raise UrlStateError("invalid", "reference_qth must not be empty.")


def _canonical_settings_from_normalized_config(
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Round-trip normalized values through the existing state/config adapters."""
    canonical_state: dict[str, Any] = {}
    apply_config_state_values(dict(config), canonical_state)
    return build_config_settings_from_state(canonical_state, language="en")


def _canonical_number(value: Any) -> str:
    """Format one finite numeric value without redundant sign or trailing zeros."""
    if isinstance(value, bool):
        raise ValueError("Boolean values are not canonical URL numbers.")
    numeric = Decimal(str(value))
    if not numeric.is_finite():
        raise ValueError("URL numbers must be finite.")
    normalized = format(numeric.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    if normalized in {"-0", ""}:
        return "0"
    return normalized


def _append_nondefault(
    entries: list[tuple[str, str]],
    key: str,
    value: Any,
    default: Any,
) -> None:
    """Append one canonical entry only when it differs from its URL-v1 default."""
    if value == default:
        return
    entries.append((key, _canonical_number(value) if isinstance(value, int) else str(value)))


def _serialize_segment_selection(
    selection: Any,
    *,
    config_order: Sequence[str],
    config_to_public: Mapping[str, str] | None = None,
) -> str | None:
    """Return one ordered public comma list, or ``None`` for canonical All."""
    if selection == SEGMENT_SELECTION_ALL:
        return None
    if not isinstance(selection, list) or not selection:
        raise ValueError("Segment selections must be All or a non-empty list.")
    if len(set(selection)) != len(selection):
        raise ValueError("Segment selections must not contain duplicates.")
    unknown_values = set(selection).difference(config_order)
    if unknown_values:
        raise ValueError(
            f"Unsupported canonical segment values: {sorted(unknown_values)!r}."
        )
    selected_values = set(selection)
    ordered_values = [value for value in config_order if value in selected_values]
    if config_to_public is not None:
        ordered_values = [config_to_public[value] for value in ordered_values]
    return ",".join(ordered_values)


def _serialize_selected_station(selection: Any) -> str | None:
    """Return omitted, explicit-none, or one canonical public station identity."""
    if selection is None:
        return None
    if selection == []:
        return "none"
    if not isinstance(selection, list) or len(selection) != 1:
        raise ValueError("A public URL can contain at most one selected station.")
    station = selection[0]
    if not isinstance(station, Mapping):
        raise ValueError("The selected station must be an identity object.")
    callsign = station.get("callsign")
    locator = station.get("locator")
    if not isinstance(callsign, str) or not isinstance(locator, str):
        raise ValueError("The selected station identity is incomplete.")
    return f"{callsign}@{locator}"


def build_query_from_settings(
    settings: Mapping[str, Any],
    *,
    include_run: bool,
) -> tuple[tuple[str, str], ...]:
    """Serialize validated canonical settings in deterministic URL-v1 order."""
    normalized_config = normalize_config_settings(dict(settings))
    _require_complete_normalized_config(normalized_config)
    canonical_settings = _canonical_settings_from_normalized_config(
        normalized_config
    )
    core = canonical_settings["core_parameters"]
    comparison = canonical_settings["comparison_parameters"]
    advanced = canonical_settings["advanced_parameters"]
    results = canonical_settings["results_view"]
    public_mode = URL_V1_CONFIG_TO_MODE[comparison["mode"]]

    entries: list[tuple[str, str]] = [("v", URL_V1_VERSION)]
    if include_run:
        entries.append(("run", "1"))
    entries.extend(
        (
            ("direction", core["analysis_direction"]),
            ("callsign", core["callsign"]),
            ("qth", core["qth"]),
            ("band", core["band"]),
            ("from", core["time_selection"]["start_utc"]),
            ("to", core["time_selection"]["end_utc"]),
            ("mode", public_mode),
        )
    )

    if public_mode == "reference_station":
        entries.extend(
            (
                ("reference", comparison["reference_callsign"]),
                ("reference_qth", comparison["reference_qth"]),
            )
        )
    elif public_mode == "local_neighborhood":
        entries.extend(
            (
                ("local_benchmark", comparison["local_benchmark"]),
                (
                    "radius_km",
                    _canonical_number(comparison["neighborhood_radius_km"]),
                ),
            )
        )
    elif public_mode == "hardware_ab":
        if core["analysis_direction"] == "rx":
            entries.append(("reference", comparison["reference_callsign"]))
        else:
            tx_ab_method = comparison["tx_ab_method"]
            entries.append(("tx_ab_method", tx_ab_method))
            if tx_ab_method == "simultaneous":
                entries.append(("reference", comparison["reference_callsign"]))
            else:
                entries.extend(
                    (
                        (
                            "repeat_min",
                            _canonical_number(
                                comparison["repeat_interval_minutes"]
                            ),
                        ),
                        (
                            "target_start_min",
                            _canonical_number(comparison["target_start_minute"]),
                        ),
                        (
                            "reference_start_min",
                            _canonical_number(
                                comparison["reference_start_minute"]
                            ),
                        ),
                    )
                )
    if public_mode != "performance":
        entries.extend(
            (
                ("snr_correction_mode", comparison["snr_correction_mode"]),
                (
                    "snr_correction_db",
                    _canonical_number(comparison["snr_correction_db"]),
                ),
            )
        )

    _append_nondefault(
        entries,
        "solar",
        advanced["solar_state"],
        URL_V1_DEFAULTS["solar"],
    )
    _append_nondefault(
        entries,
        "max_distance_km",
        advanced["max_peer_distance_km"],
        URL_V1_DEFAULTS["max_distance_km"],
    )
    if advanced["exclude_special_callsigns"]:
        entries.append(("exclude_special", "1"))
    if advanced["exclude_moving_stations"]:
        entries.append(("exclude_moving", "1"))
    if public_mode != "performance":
        _append_nondefault(
            entries,
            "min_joint_spots",
            advanced["min_joint_spots_per_station"],
            URL_V1_DEFAULTS["min_joint_spots"],
        )
    _append_nondefault(
        entries,
        "min_opportunities",
        advanced["min_confirmed_opportunities_per_peer"],
        URL_V1_DEFAULTS["min_opportunities"],
    )
    _append_nondefault(
        entries,
        "min_segment_stations",
        advanced["min_joint_stations_per_map_segment"],
        URL_V1_DEFAULTS["min_segment_stations"],
    )

    active_results = (
        results["success"]
        if public_mode == "performance"
        else results["compare"]
    )
    serialized_ranges = _serialize_segment_selection(
        active_results["selected_ranges"],
        config_order=SEGMENT_RANGE_OPTIONS,
        config_to_public=URL_V1_CONFIG_TO_RANGE,
    )
    if serialized_ranges is not None:
        entries.append(("ranges", serialized_ranges))
    serialized_directions = _serialize_segment_selection(
        active_results["selected_directions"],
        config_order=SEGMENT_DIRECTION_OPTIONS,
    )
    if serialized_directions is not None:
        entries.append(("directions", serialized_directions))
    _append_nondefault(
        entries,
        "segment_bin",
        active_results["segment_evidence_time_bin"],
        URL_V1_DEFAULTS["segment_bin"],
    )
    _append_nondefault(
        entries,
        "station_bin",
        active_results["station_evidence_time_bin"],
        URL_V1_DEFAULTS["station_bin"],
    )
    if public_mode != "performance":
        _append_nondefault(
            entries,
            "temporal_view",
            active_results["station_evidence_temporal_view"],
            URL_V1_DEFAULTS["temporal_view"],
        )
    selected_station = _serialize_selected_station(
        active_results["selected_stations"]
    )
    if selected_station is not None:
        entries.append(("selected_station", selected_station))
    if public_mode == "performance" and active_results["show_zero_target"]:
        entries.append(("show_zero", "1"))
    if public_mode != "performance" and active_results["show_non_joint"]:
        entries.append(("show_unpaired", "1"))

    entries.sort(key=lambda entry: URL_V1_PARAMETER_ORDER.index(entry[0]))
    return tuple(entries)


def build_query_from_state(
    state: Mapping[str, Any],
    *,
    include_run: bool | None = None,
) -> tuple[tuple[str, str], ...]:
    """Build canonical URL entries from the existing durable session state."""
    settings = build_config_settings_from_state(
        state,
        language=state.get("lang", "en"),
    )
    if include_run is None:
        include_run = bool(state.get("run_mode"))
    return build_query_from_settings(settings, include_run=bool(include_run))


def build_query_string(entries: Sequence[tuple[str, str]]) -> str:
    """Encode canonical URL entries with the standard query encoder."""
    return urlencode(tuple(entries), doseq=False)


def canonicalize_query(
    query_values: Mapping[str, Sequence[str] | str],
) -> str:
    """Validate an input query and return its deterministic URL-v1 encoding."""
    parameters = parse_url_query(query_values)
    if parameters is None:
        return ""
    normalized_config = build_config_from_url(parameters)
    canonical_settings = _canonical_settings_from_normalized_config(
        normalized_config
    )
    return build_query_string(
        build_query_from_settings(
            canonical_settings,
            include_run=parameters.get("run") == "1",
        )
    )


def build_share_url(state: Mapping[str, Any]) -> str:
    """Build one replay URL containing only canonical WSPRadar-owned state."""
    entries = build_query_from_state(state, include_run=True)
    public_url = urlsplit(APP_URL)
    if public_url.scheme != "https" or not public_url.netloc:
        raise ValueError("APP_URL must identify the canonical public HTTPS origin.")
    return urlunsplit(
        (
            public_url.scheme,
            public_url.netloc,
            public_url.path or "/",
            build_query_string(entries),
            RESULTS_INSPECTION_ANCHOR_ID,
        )
    )


def _query_signature(
    query_values: Mapping[str, Sequence[str] | str],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return a deterministic signature without discarding duplicates."""
    return tuple(
        sorted(
            (
                str(key),
                _coerce_query_value_sequence(raw_values),
            )
            for key, raw_values in query_values.items()
        )
    )


def hydrate_initial_url_state(
    session_state: MutableMapping[str, Any],
    query_values: Mapping[str, Sequence[str] | str],
    *,
    apply_config: Callable[
        [Mapping[str, Any], MutableMapping[str, Any]],
        None,
    ] = apply_config_values_to_state,
    submit_analysis: Callable[..., str] = begin_analysis_submission,
) -> UrlHydrationResult:
    """Validate and apply the initial query exactly once for this browser session."""
    if URL_HYDRATION_SIGNATURE_KEY in session_state:
        return UrlHydrationResult(False, False, False)
    session_state[URL_HYDRATION_SIGNATURE_KEY] = _query_signature(query_values)
    session_state.pop(URL_HYDRATION_ERROR_KEY, None)

    try:
        parameters = parse_url_query(query_values)
        if parameters is None:
            return UrlHydrationResult(True, False, False)
        normalized_config = build_config_from_url(parameters)
    except (UrlStateError, ValueError) as error:
        error_code = (
            error.code if isinstance(error, UrlStateError) else "invalid"
        )
        session_state[URL_HYDRATION_ERROR_KEY] = {
            "code": error_code,
            "detail": str(error),
        }
        LOGGER.warning("Rejected initial WSPRadar URL: %s", error)
        return UrlHydrationResult(True, False, False, error_code)

    apply_config(normalized_config, session_state)
    should_replay = parameters.get("run") == "1"
    if should_replay:
        submit_analysis(
            session_state,
            request_source="url_replay",
        )
        session_state[URL_REPLAY_NAVIGATION_PENDING_KEY] = True
    return UrlHydrationResult(True, True, should_replay)


def consume_url_hydration_error(
    session_state: MutableMapping[str, Any],
) -> dict[str, str] | None:
    """Consume one safe URL error category after localization is available."""
    error = session_state.pop(URL_HYDRATION_ERROR_KEY, None)
    return error if isinstance(error, dict) else None


def consume_url_replay_navigation(
    session_state: MutableMapping[str, Any],
) -> bool:
    """Consume the one-shot results-anchor landing requested by URL replay."""
    return bool(session_state.pop(URL_REPLAY_NAVIGATION_PENDING_KEY, False))


def render_current_url_synchronizer(
    state: Mapping[str, Any],
    *,
    key: str,
) -> None:
    """Synchronize valid state, or remove owned keys while inputs are incomplete."""
    try:
        entries = build_query_from_state(state)
    except (KeyError, TypeError, ValueError):
        entries = ()
    render_url_query_synchronizer(
        entries,
        owned_keys=URL_V1_OWNED_QUERY_KEYS,
        key=key,
    )
