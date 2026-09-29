"""Build canonical core analysis context objects from Streamlit UI state."""

from config import DEFAULT_BAND
from core.analysis_context import (
    AnalysisContext,
    COMPARISON_LOCAL_NEIGHBORHOOD,
)
from core.input_validation import normalize_ascii_upper
from ui.config_io import (
    validate_local_benchmark_state,
)
from ui.population_exclusion_state import (
    population_exclusion_defaults,
    result_type_from_comparison_mode,
)


def build_analysis_context_from_session_state(session_state):
    """Convert canonical Streamlit session values into one stable scalar context."""
    comparison_mode = session_state.get("val_comp_mode", "none")
    population_defaults = population_exclusion_defaults(
        result_type_from_comparison_mode(comparison_mode)
    )
    target_qth = normalize_ascii_upper(session_state.get("val_qth", ""))

    return AnalysisContext(
        run_mode=session_state.get("run_mode"),
        callsign=normalize_ascii_upper(session_state.get("val_callsign", "")),
        qth=target_qth,
        band=session_state.get("val_band", DEFAULT_BAND),
        comparison_mode=comparison_mode,
        local_benchmark=(
            validate_local_benchmark_state(
                session_state.get("val_local_benchmark", "local_median")
            )
            if comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD
            else "local_median"
        ),
        reference_callsign=normalize_ascii_upper(
            session_state.get("val_ref_callsign", "")
        ),
        reference_qth=normalize_ascii_upper(session_state.get("val_ref_qth", "")),
        neighborhood_radius_km=int(session_state.get("val_ref_radius_km", 100)),
        reference_snr_correction_db=round(float(session_state.get("val_benchmark_offset_db", 0.0)), 1),
        solar_state=session_state.get("val_solar", "all"),
        max_peer_distance_km=int(
            session_state.get("val_max_peer_distance_km", 22000)
        ),
        exclude_special_callsigns=bool(
            session_state.get(
                "val_exclude_special_callsigns",
                population_defaults["val_exclude_special_callsigns"],
            )
        ),
        exclude_moving_stations=bool(
            session_state.get(
                "val_filter_moving",
                population_defaults["val_filter_moving"],
            )
        ),
        min_joint_spots_per_station=int(session_state.get("val_min_spots", 1)),
        min_confirmed_opportunities_per_peer=int(session_state.get("val_min_opportunities", 5)),
        min_joint_stations_per_map_segment=int(session_state.get("val_min_stations", 1)),
    )
