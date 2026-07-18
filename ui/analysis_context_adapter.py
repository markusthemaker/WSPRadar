"""Build canonical core analysis context objects from Streamlit UI state."""

from config import DEFAULT_BAND
from core.analysis_context import AnalysisContext
from i18n import T
from ui.config_io import (
    LOCAL_BENCHMARK_VALUES,
    MODE_VALUES,
    SOLAR_VALUES,
    canonical_from_translated,
)


def build_analysis_context_from_session_state(session_state):
    """Convert localized Streamlit session values into one stable scalar context."""
    language = session_state.get("lang", "en")
    t = T.get(language, T["en"])
    analysis_direction = session_state.get("val_analysis_direction")

    return AnalysisContext(
        run_mode=session_state.get("run_mode"),
        callsign=str(session_state.get("val_callsign", "")).strip().upper(),
        qth=str(session_state.get("val_qth", "")).strip().upper(),
        band=session_state.get("val_band", DEFAULT_BAND),
        comparison_mode=canonical_from_translated(
            session_state.get("val_comp_mode", t["opt_comp_none"]),
            MODE_VALUES,
            "none",
        ),
        local_benchmark=canonical_from_translated(
            session_state.get("val_local_benchmark", t["opt_local_median"]),
            LOCAL_BENCHMARK_VALUES,
            "local_median",
        ),
        reference_callsign=str(session_state.get("val_ref_callsign", "")).strip().upper(),
        neighborhood_radius_km=int(session_state.get("val_ref_radius_km", 100)),
        reference_snr_correction_db=round(float(session_state.get("val_benchmark_offset_db", 0.0)), 1),
        self_test_mode="tx" if analysis_direction == "tx" else "rx",
        setup_b_callsign=str(session_state.get("val_self_call_b", "")).strip().upper(),
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
            session_state.get("val_solar", t["opt_solar_all"]),
            SOLAR_VALUES,
            "all",
        ),
        map_scope_km=int(session_state.get("val_max_dist", 22000)),
        exclude_special_callsigns=bool(session_state.get("val_exclude_special_callsigns", False)),
        exclude_moving_stations=bool(session_state.get("val_filter_moving", False)),
        min_joint_spots_per_station=int(session_state.get("val_min_spots", 1)),
        min_confirmed_opportunities_per_peer=int(session_state.get("val_min_opportunities", 5)),
        min_joint_stations_per_map_segment=int(session_state.get("val_min_stations", 1)),
    )
