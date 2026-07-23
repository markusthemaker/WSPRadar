"""Pure compact summaries for completed Guided Input steps."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from i18n import T
from ui.config_io import SOLAR_KEYS


def _window_summary(state: Mapping[str, Any], guided_content) -> str:
    """Format the active UTC window entirely from Guided localization templates."""
    summaries = guided_content["summaries"]
    if state.get("val_time_mode") == "last_x":
        hours = int(state.get("val_hours", 24))
        return summaries["window_last_x"].format(hours=hours)
    start_date = state.get("val_start_d")
    end_date = state.get("val_end_d")
    start_time = state.get("val_start_t")
    end_time = state.get("val_end_t")
    if not all((start_date, end_date, start_time, end_time)):
        return summaries["window_incomplete"]
    start_utc = datetime.combine(start_date, start_time)
    end_utc = datetime.combine(end_date, end_time)
    return summaries["window_custom"].format(
        start=f"{start_utc:%Y-%m-%d %H:%M}",
        end=f"{end_utc:%Y-%m-%d %H:%M}",
    )


def use_case_summary(state, guided_content, step_number, language):
    """Summarize the selected operating question."""
    choice = guided_content["options"]["use_cases"][state["guided_use_case"]][
        "label"
    ]
    return guided_content["summaries"]["use_case"].format(
        step=step_number,
        choice=choice,
    )


def target_and_window_summary(state, guided_content, step_number, language):
    """Summarize Target identity, band and active time branch."""
    return guided_content["summaries"]["target_and_window"].format(
        step=step_number,
        callsign=str(state.get("val_callsign", "")).upper(),
        qth=str(state.get("val_qth", "")).upper(),
        band=state.get("val_band", ""),
        window=_window_summary(state, guided_content),
    )


def reference_design_summary(state, guided_content, step_number, language):
    """Summarize the active Reference design without exposing inactive values."""
    benchmark_mode = state.get("val_comp_mode")
    summaries = guided_content["summaries"]
    if benchmark_mode == "reference_station":
        return summaries["reference_station"].format(
            step=step_number,
            callsign=str(state.get("val_ref_callsign", "")).upper(),
            qth=str(state.get("val_ref_qth", "")).upper(),
        )
    if benchmark_mode == "local_neighborhood":
        summary_key = (
            "reference_local_best"
            if state.get("val_local_benchmark") == "local_best"
            else "reference_local_median"
        )
        return summaries[summary_key].format(
            step=step_number,
            radius=state.get("val_ref_radius_km", 100),
        )
    if (
        state.get("val_analysis_direction") == "tx"
        and state.get("val_tx_ab_method") == "sequential"
    ):
        return summaries["reference_hardware_tx_sequential"].format(
            step=step_number
        )
    summary_key = (
        "reference_hardware_tx_simultaneous"
        if state.get("val_analysis_direction") == "tx"
        else "reference_hardware_rx"
    )
    return summaries[summary_key].format(
        step=step_number,
        callsign=str(state.get("val_ref_callsign", "")).upper(),
    )


def offset_calibration_summary(state, guided_content, step_number, language):
    """Summarize no, established, or requested offset calibration intent."""
    intent = state.get("guided_offset_intent")
    summary_key = {
        "no_offset": "offset_none",
        "established_offset": "offset_established",
        "establish_offset": "offset_establish",
    }[intent]
    return guided_content["summaries"][summary_key].format(
        step=step_number,
        offset=float(state.get("val_benchmark_offset_db", 0.0)),
    )


def scope_and_evidence_summary(state, guided_content, step_number, language):
    """Summarize scope using localized solar and Guided preset labels."""
    labels = T[language]
    solar_state = state.get("val_solar", "all")
    solar_label = labels[SOLAR_KEYS.get(solar_state, "opt_solar_all")]
    scope_mode = state.get("guided_scope_mode", "custom")
    mode_label = guided_content["options"]["scope_mode"][scope_mode]["label"]
    return guided_content["summaries"]["scope"].format(
        step=step_number,
        distance=state.get("val_max_peer_distance_km", 22000),
        solar=solar_label,
        mode=mode_label,
    )


def review_and_run_summary(state, guided_content, step_number, language):
    """Summarize the terminal readiness state."""
    return guided_content["summaries"]["review_ready"].format(step=step_number)


SUMMARY_RENDERERS = {
    "use_case_summary": use_case_summary,
    "target_and_window_summary": target_and_window_summary,
    "reference_design_summary": reference_design_summary,
    "offset_calibration_summary": offset_calibration_summary,
    "scope_and_evidence_summary": scope_and_evidence_summary,
    "review_and_run_summary": review_and_run_summary,
}
