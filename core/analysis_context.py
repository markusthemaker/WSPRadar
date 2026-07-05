"""Canonical scalar run context for WSPRadar core analysis code."""

from dataclasses import asdict, dataclass


COMPARISON_LOCAL_NEIGHBORHOOD = "local_neighborhood"
COMPARISON_REFERENCE_STATION = "reference_station"
COMPARISON_HARDWARE_AB = "hardware_ab"

LOCAL_BENCHMARK_MEDIAN = "local_median"
LOCAL_BENCHMARK_BEST = "local_best"

SELF_TEST_RX = "rx"
SELF_TEST_TX = "tx"

WSPR_FRAME_00_04_08 = "frame_00_04_08"
WSPR_FRAME_02_06_10 = "frame_02_06_10"

SOLAR_ALL = "all"
SOLAR_DAY = "day"
SOLAR_NIGHT = "night"
SOLAR_GREYLINE = "greyline"

_WSPR_FRAME_MOD4 = {
    WSPR_FRAME_00_04_08: 0,
    WSPR_FRAME_02_06_10: 2,
}

_SOLAR_PATH_STATE = {
    SOLAR_DAY: "day",
    SOLAR_NIGHT: "night",
    SOLAR_GREYLINE: "grey",
}


@dataclass(frozen=True)
class AnalysisContext:
    """Stable, localized-label-free configuration used by core analysis code."""

    language: str = "en"
    run_mode: str | None = None
    callsign: str = ""
    qth: str = ""
    band: str = "20m"
    comparison_mode: str = COMPARISON_LOCAL_NEIGHBORHOOD
    local_benchmark: str = LOCAL_BENCHMARK_MEDIAN
    reference_callsign: str = ""
    neighborhood_radius_km: int = 100
    reference_snr_correction_db: float = 0.0
    self_test_mode: str = SELF_TEST_RX
    setup_b_callsign: str = ""
    target_wspr_frame: str = WSPR_FRAME_00_04_08
    reference_wspr_frame: str = WSPR_FRAME_02_06_10
    tx_ab_bin_minutes: int = 8
    solar_state: str = SOLAR_ALL
    map_scope_km: int = 22000
    exclude_special_callsigns: bool = False
    exclude_moving_stations: bool = False
    min_joint_spots_per_station: int = 1
    min_confirmed_opportunities_per_peer: int = 5
    min_joint_stations_per_map_segment: int = 1
    is_demo_run: bool = False
    active_demo_profile: str | None = None

    def to_dict(self):
        """Return a JSON-friendly scalar representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, values):
        """Build a context from a previously serialized scalar representation."""
        if isinstance(values, cls):
            return values
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


def wspr_frame_mod4(frame_key):
    return _WSPR_FRAME_MOD4.get(frame_key)


def wspr_frame_sql(frame_key):
    mod4 = wspr_frame_mod4(frame_key)
    return f"AND toMinute(time) % 4 = {mod4}" if mod4 is not None else ""


def solar_path_state(solar_state):
    return _SOLAR_PATH_STATE.get(solar_state)
