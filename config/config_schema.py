"""Canonical version-1 WSPRadar configuration document constants.

The serialized settings hierarchy mirrors the four durable areas of the UI.
The time window is always stored as absolute UTC boundaries. Conditional
comparison objects contain only fields applicable to the selected mode;
inactive widget state is deliberately not part of the configuration contract.
Optional profile metadata makes the same document usable as either a personal
saved configuration or a built-in demo.
"""


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

ANALYSIS_DIRECTIONS = frozenset({"rx", "tx"})
COMPARISON_MODES = frozenset(
    {"none", "hardware_ab", "reference_station", "local_neighborhood"}
)
SNR_CORRECTION_MODES = frozenset(
    {"no_offset", "established_offset", "establish_offset"}
)
STATION_EVIDENCE_TIME_BIN_OPTIONS = (
    "1h",
    "2h",
    "3h",
    "6h",
    "12h",
    "24h",
)
STATION_EVIDENCE_TIME_BINS = frozenset(STATION_EVIDENCE_TIME_BIN_OPTIONS)
SEGMENT_EVIDENCE_TIME_BINS = STATION_EVIDENCE_TIME_BINS | {
    "auto",
    "5m",
    "15m",
    "30m",
}
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
