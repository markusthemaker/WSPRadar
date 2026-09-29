"""Canonical scalar run context for WSPRadar core analysis code."""

from dataclasses import asdict, dataclass

from config import DEFAULT_BAND


COMPARISON_NONE = "none"
COMPARISON_LOCAL_NEIGHBORHOOD = "local_neighborhood"
COMPARISON_REFERENCE_STATION = "reference_station"

LOCAL_BENCHMARK_MEDIAN = "local_median"


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
    four-character Maidenhead grid. The maximum peer distance
    is a half-open Target-QTH radius for mapped scientific peers; global
    moving-station validation and Target-active evidence are intentionally
    outside that radius.
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
    solar_state: str = SOLAR_ALL
    max_peer_distance_km: int = 22000
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
        """Build a current context, rejecting unknown scientific fields."""
        if isinstance(values, cls):
            return values
        values = dict(values or {})
        field_names = cls.__dataclass_fields__.keys()
        unknown_fields = values.keys() - field_names
        if unknown_fields:
            names = ", ".join(sorted(str(key) for key in unknown_fields))
            raise ValueError(f"Unknown AnalysisContext fields: {names}")
        return cls(**values)


def solar_path_state(solar_state):
    return _SOLAR_PATH_STATE.get(solar_state)
