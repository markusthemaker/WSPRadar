"""Canonical scalar run context for WSPRadar core analysis code."""

from dataclasses import asdict, dataclass

from config import DEFAULT_BAND


COMPARISON_NONE = "none"
COMPARISON_LOCAL_NEIGHBORHOOD = "local_neighborhood"
COMPARISON_REFERENCE_STATION = "reference_station"
COMPARISON_HARDWARE_AB = "hardware_ab"

LOCAL_BENCHMARK_MEDIAN = "local_median"
LOCAL_BENCHMARK_BEST = "local_best"

SELF_TEST_RX = "rx"
SELF_TEST_TX = "tx"

TX_AB_METHOD_SIMULTANEOUS = "simultaneous"
TX_AB_METHOD_SEQUENTIAL = "sequential"

SOLAR_ALL = "all"
SOLAR_DAY = "day"
SOLAR_NIGHT = "night"
SOLAR_GREYLINE = "greyline"

_SOLAR_PATH_STATE = {
    SOLAR_DAY: "day",
    SOLAR_NIGHT: "night",
    SOLAR_GREYLINE: "grey",
}


@dataclass(frozen=True)
class AnalysisContext:
    """Stable, localized-label-free configuration used by core analysis code.

    Reference Station identifies each side by an exact callsign and
    four-character Maidenhead grid. Hardware A/B derives its shared grid-4 from
    Target QTH. Periodic sequential TX A/B fields describe one shared repeat
    interval and two disjoint even UTC start phases.
    """

    run_mode: str | None = None
    callsign: str = ""
    qth: str = ""
    band: str = DEFAULT_BAND
    comparison_mode: str = COMPARISON_NONE
    local_benchmark: str = LOCAL_BENCHMARK_MEDIAN
    reference_callsign: str = ""
    reference_qth: str = ""
    neighborhood_radius_km: int = 100
    reference_snr_correction_db: float = 0.0
    self_test_mode: str = SELF_TEST_RX
    tx_ab_method: str = TX_AB_METHOD_SIMULTANEOUS
    tx_ab_repeat_interval_minutes: int = 10
    tx_ab_target_start_minute: int = 0
    tx_ab_reference_start_minute: int = 2
    solar_state: str = SOLAR_ALL
    map_scope_km: int = 22000
    exclude_special_callsigns: bool = False
    exclude_moving_stations: bool = False
    min_joint_spots_per_station: int = 1
    min_confirmed_opportunities_per_peer: int = 5
    min_joint_stations_per_map_segment: int = 1

    def to_dict(self):
        """Return a JSON-friendly scalar representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, values):
        """Build a context from matching canonical scalar fields."""
        if isinstance(values, cls):
            return values
        values = dict(values or {})
        field_names = cls.__dataclass_fields__.keys()
        return cls(**{key: values[key] for key in field_names if key in values})


def is_radius_comparison(context):
    return context.comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD


def is_reference_station_comparison(context):
    return context.comparison_mode == COMPARISON_REFERENCE_STATION


def is_hardware_ab_comparison(context):
    return context.comparison_mode == COMPARISON_HARDWARE_AB


def is_rx_hardware_ab(context):
    return is_hardware_ab_comparison(context) and context.self_test_mode == SELF_TEST_RX


def is_tx_hardware_ab(context):
    return is_hardware_ab_comparison(context) and context.self_test_mode == SELF_TEST_TX


def solar_path_state(solar_state):
    return _SOLAR_PATH_STATE.get(solar_state)
