"""Canonical version-1 WSPRadar configuration document constants.

The serialized settings hierarchy mirrors the four durable areas of the UI.
The time window is always stored as absolute UTC boundaries. Conditional
comparison objects contain only fields applicable to the selected mode;
inactive widget state is deliberately not part of the configuration contract.
Optional profile metadata makes the same document usable as either a personal
saved configuration or a built-in demo.
"""

from datetime import timedelta
from math import isfinite


CONFIG_APP_NAME = "WSPRadar.org"
CONFIG_DOCUMENT_FORMAT = "wspradar.config"
CONFIG_SCHEMA_VERSION = 1
CONFIG_DOCUMENT_KEYS = frozenset(
    {"format", "schema_version", "metadata", "profile", "settings", "extensions"}
)

CONFIG_KEYS = frozenset(
    {
        "core_parameters",
        "comparison_parameters",
        "advanced_parameters",
        "results_view",
    }
)

PERFORMANCE_RESULTS_VIEW_KEY = "performance"
BENCHMARK_RESULTS_VIEW_KEY = "benchmark"
RESULTS_VIEW_KEYS = frozenset(
    {PERFORMANCE_RESULTS_VIEW_KEY, BENCHMARK_RESULTS_VIEW_KEY}
)
LEGACY_RESULTS_VIEW_KEY_ALIASES = (
    ("success", PERFORMANCE_RESULTS_VIEW_KEY),
    ("compare", BENCHMARK_RESULTS_VIEW_KEY),
)

ANALYSIS_DIRECTIONS = frozenset({"rx", "tx"})
COMPARISON_MODES = frozenset(
    {"none", "hardware_ab", "reference_station", "local_neighborhood"}
)
SNR_CORRECTION_MODES = frozenset(
    {"no_offset", "established_offset", "establish_offset"}
)
TEMPORAL_EVIDENCE_TIME_BIN_OPTIONS = (
    "2m",
    "10m",
    "30m",
    "1h",
    "2h",
    "3h",
    "6h",
    "12h",
    "24h",
)
LEGACY_TEMPORAL_EVIDENCE_TIME_BIN_OPTIONS = (
    "5m",
    "15m",
)
TEMPORAL_EVIDENCE_TIME_BIN_PRESETS = (
    (
        timedelta(hours=6),
        ("2m", "10m", "30m", "1h", "2h", "3h", "6h"),
        "10m",
    ),
    (
        timedelta(hours=24),
        ("2m", "10m", "30m", "1h", "2h", "3h", "6h"),
        "30m",
    ),
    (
        timedelta(days=7),
        ("30m", "1h", "2h", "3h", "6h", "12h", "24h"),
        "12h",
    ),
    (
        None,
        ("1h", "2h", "3h", "6h", "12h", "24h"),
        "12h",
    ),
)
STATION_EVIDENCE_TIME_BIN_OPTIONS = TEMPORAL_EVIDENCE_TIME_BIN_OPTIONS
STATION_EVIDENCE_TIME_BINS = frozenset(
    TEMPORAL_EVIDENCE_TIME_BIN_OPTIONS
    + LEGACY_TEMPORAL_EVIDENCE_TIME_BIN_OPTIONS
)
SEGMENT_EVIDENCE_TIME_BINS = STATION_EVIDENCE_TIME_BINS | {
    "auto",
}


def _temporal_evidence_time_bin_minutes(time_bin):
    """Return the positive minute width of one canonical time-bin token."""
    token = str(time_bin).strip().lower()
    if token.endswith("m"):
        numeric_token = token[:-1]
        multiplier = 1
    elif token.endswith("h"):
        numeric_token = token[:-1]
        multiplier = 60
    else:
        raise ValueError(f"Unsupported temporal evidence time bin: {time_bin}")
    try:
        numeric_value = int(numeric_token)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Unsupported temporal evidence time bin: {time_bin}"
        ) from exc
    if numeric_value <= 0:
        raise ValueError(f"Unsupported temporal evidence time bin: {time_bin}")
    return numeric_value * multiplier


def temporal_evidence_time_bin_policy_for_duration(
    duration,
    *,
    retained_time_bin=None,
):
    """Return adaptive options/default while retaining one valid saved choice.

    ``5m`` and ``15m`` remain accepted solely for saved-config and public-URL
    compatibility. They are included in a returned option list only when one is
    the explicitly retained value. The same rule preserves any valid current
    choice that falls outside the adaptive tier without silently changing its
    meaning.
    """
    if not hasattr(duration, "total_seconds"):
        raise TypeError("Temporal evidence duration must provide total_seconds().")
    duration_seconds = float(duration.total_seconds())
    if not isfinite(duration_seconds) or duration_seconds <= 0.0:
        raise ValueError("Temporal evidence duration must be positive.")

    adaptive_options = None
    adaptive_default = None
    for maximum_duration, options, default in TEMPORAL_EVIDENCE_TIME_BIN_PRESETS:
        if (
            maximum_duration is None
            or duration_seconds <= maximum_duration.total_seconds()
        ):
            adaptive_options = tuple(options)
            adaptive_default = str(default)
            break
    if adaptive_options is None or adaptive_default is None:
        raise RuntimeError("Temporal evidence time-bin policy is incomplete.")

    retained_token = (
        str(retained_time_bin)
        if retained_time_bin is not None
        else None
    )
    if retained_token not in STATION_EVIDENCE_TIME_BINS:
        return list(adaptive_options), adaptive_default
    if retained_token in adaptive_options:
        return list(adaptive_options), adaptive_default

    retained_options = set(adaptive_options)
    retained_options.add(retained_token)
    ordered_options = sorted(
        retained_options,
        key=_temporal_evidence_time_bin_minutes,
    )
    return ordered_options, adaptive_default


SEGMENT_SELECTION_ALL = "all"
SEGMENT_RANGE_OPTIONS = (
    "[0-2500km]",
    "[2500-5000km]",
    "[5000-10000km]",
    "[10000-15000km]",
    "[15000-20000km]",
    "[20000-22000km]",
)
SEGMENT_DIRECTION_OPTIONS = (
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
)

PROFILE_ID_MAX_LENGTH = 64
PROFILE_ID_TOKEN_PATTERN = (
    rf"[a-z0-9](?:[a-z0-9_-]{{0,{PROFILE_ID_MAX_LENGTH - 2}}}[a-z0-9])?"
)
PROFILE_ID_PATTERN = rf"^{PROFILE_ID_TOKEN_PATTERN}$"
LOCALIZED_LANGUAGE_PATTERN = r"^[a-z]{2}(?:-[A-Z]{2})?$"

TX_AB_REPEAT_INTERVAL_OPTIONS = (4, 6, 10, 12, 20, 30, 60)
TX_AB_METHODS = frozenset({"simultaneous", "sequential"})
