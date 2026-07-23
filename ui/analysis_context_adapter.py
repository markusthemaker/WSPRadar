"""Build canonical core analysis context objects from Streamlit UI state."""

from config import DEFAULT_BAND
from core.analysis_context import AnalysisContext, COMPARISON_HARDWARE_AB
from core.input_validation import normalize_ascii_upper
from ui.config_io import (
    LOCAL_BENCHMARK_VALUES,
    MODE_VALUES,
    SOLAR_VALUES,
    canonical_from_translated,
)


def build_analysis_context_from_session_state(session_state):
    """Convert localized Streamlit session values into one stable scalar context."""
    analysis_direction = session_state.get("val_analysis_direction")
    comparison_mode = canonical_from_translated(
        session_state.get("val_comp_mode", "none"),
        MODE_VALUES,
        "none",
    )
    target_qth = normalize_ascii_upper(session_state.get("val_qth", ""))
    reference_qth = (
        target_qth[:4]
        if comparison_mode == COMPARISON_HARDWARE_AB
        else normalize_ascii_upper(session_state.get("val_ref_qth", ""))
    )

    return AnalysisContext(
        run_mode=session_state.get("run_mode"),
        callsign=normalize_ascii_upper(session_state.get("val_callsign", "")),
        qth=target_qth,
        band=session_state.get("val_band", DEFAULT_BAND),
        comparison_mode=comparison_mode,
        local_benchmark=canonical_from_translated(
            session_state.get("val_local_benchmark", "local_median"),
            LOCAL_BENCHMARK_VALUES,
            "local_median",
        ),
        reference_callsign=normalize_ascii_upper(
            session_state.get("val_ref_callsign", "")
        ),
        reference_qth=reference_qth,
        neighborhood_radius_km=int(session_state.get("val_ref_radius_km", 100)),
        reference_snr_correction_db=round(float(session_state.get("val_benchmark_offset_db", 0.0)), 1),
        self_test_mode="tx" if analysis_direction == "tx" else "rx",
        tx_ab_method=str(
            session_state.get("val_tx_ab_method", "simultaneous")
        ),
        tx_ab_repeat_interval_minutes=int(
            session_state.get("val_tx_ab_repeat_interval_minutes", 10)
        ),
        tx_ab_target_start_minute=int(
            session_state.get("val_tx_ab_target_start_minute", 0)
        ),
        tx_ab_reference_start_minute=int(
            session_state.get("val_tx_ab_reference_start_minute", 2)
        ),
        solar_state=canonical_from_translated(
            session_state.get("val_solar", "all"),
            SOLAR_VALUES,
            "all",
        ),
        max_peer_distance_km=int(
            session_state.get("val_max_peer_distance_km", 22000)
        ),
        exclude_special_callsigns=bool(session_state.get("val_exclude_special_callsigns", False)),
        exclude_moving_stations=bool(session_state.get("val_filter_moving", False)),
        min_joint_spots_per_station=int(session_state.get("val_min_spots", 1)),
        min_confirmed_opportunities_per_peer=int(session_state.get("val_min_opportunities", 5)),
        min_joint_stations_per_map_segment=int(session_state.get("val_min_stations", 1)),
    )
