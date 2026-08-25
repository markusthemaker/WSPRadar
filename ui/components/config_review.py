"""Shared canonical configuration review for Guided and Classic Input."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from core.input_validation import (
    is_valid_callsign,
    is_valid_grid4,
    is_valid_locator,
    normalize_ascii_upper,
)
from ui.analysis_question_state import derive_analysis_question
from ui.config_io import SOLAR_KEYS, build_config_settings_from_state


def is_canonical_configuration_ready(state: Mapping[str, Any]) -> bool:
    """Return whether current active values form one valid saved/run configuration."""
    target_callsign = normalize_ascii_upper(state.get("val_callsign"))
    if not is_valid_callsign(target_callsign):
        return False
    if not is_valid_locator(normalize_ascii_upper(state.get("val_qth"))):
        return False

    comparison_mode = state.get("val_comp_mode")
    requires_reference_callsign = bool(
        comparison_mode == "reference_station"
        or (
            comparison_mode == "hardware_ab"
            and (
                state.get("val_analysis_direction") == "rx"
                or state.get("val_tx_ab_method") == "simultaneous"
            )
        )
    )
    if requires_reference_callsign:
        reference_callsign = normalize_ascii_upper(
            state.get("val_ref_callsign")
        )
        if (
            not is_valid_callsign(reference_callsign)
            or reference_callsign == target_callsign
        ):
            return False
    if comparison_mode == "reference_station" and not is_valid_grid4(
        normalize_ascii_upper(state.get("val_ref_qth"))
    ):
        return False

    try:
        build_config_settings_from_state(state)
    except (KeyError, TypeError, ValueError):
        return False
    return True


def _window_summary(state: Mapping[str, Any], guided_content) -> str:
    """Format the absolute UTC window from shared localized templates."""
    summaries = guided_content["summaries"]
    start_date = state.get("val_start_d")
    end_date = state.get("val_end_d")
    start_time = state.get("val_start_t")
    end_time = state.get("val_end_t")
    if not all((start_date, end_date, start_time, end_time)):
        return summaries["window_incomplete"]
    start_utc = datetime.combine(start_date, start_time)
    end_utc = datetime.combine(end_date, end_time)
    return summaries["window_utc"].format(
        start=f"{start_utc:%Y-%m-%d %H:%M}",
        end=f"{end_utc:%Y-%m-%d %H:%M}",
    )


def evidence_value_summary(
    state: Mapping[str, Any],
    guided_content,
) -> str:
    """Return the active result method's localized evidence thresholds."""
    messages = guided_content["messages"]
    is_benchmark = state.get("val_comp_mode") != "none"
    is_scheduled_tx = bool(
        state.get("val_analysis_direction") == "tx"
        and state.get("val_comp_mode") == "hardware_ab"
        and state.get("val_tx_ab_method") == "sequential"
    )
    evidence_message_key = (
        "scheduled_evidence"
        if is_scheduled_tx
        else "compare_evidence" if is_benchmark else "success_evidence"
    )
    return messages[evidence_message_key].format(
        value=(
            state.get("val_min_spots", 1)
            if is_benchmark
            else state.get("val_min_opportunities", 5)
        ),
        stations=state.get("val_min_stations", 1),
    )


def reference_review_value(
    state: Mapping[str, Any],
    guided_content,
) -> str:
    """Return one human-readable active Reference value for shared review."""
    options = guided_content["options"]
    benchmark_mode = state.get("val_comp_mode")
    if benchmark_mode == "reference_station":
        return (
            f"{str(state.get('val_ref_callsign', '')).upper()} · "
            f"{str(state.get('val_ref_qth', '')).upper()} · "
            f"{options['reference_design'][benchmark_mode]['label']}"
        )
    if benchmark_mode == "local_neighborhood":
        local_method = state.get("val_local_benchmark", "local_median")
        return (
            f"{options['local_benchmark'][local_method]['label']} · "
            f"{state.get('val_ref_radius_km', 100)} km"
        )
    if (
        state.get("val_analysis_direction") == "tx"
        and state.get("val_tx_ab_method") == "sequential"
    ):
        return guided_content["messages"]["review_tx_sequential_value"].format(
            method=options["tx_ab_method"]["sequential"]["label"],
            repeat=state.get("val_tx_ab_repeat_interval_minutes", 10),
            target=int(state.get("val_tx_ab_target_start_minute", 0)),
            reference=int(state.get("val_tx_ab_reference_start_minute", 2)),
        )
    if state.get("val_analysis_direction") == "tx":
        return guided_content["messages"]["review_tx_simultaneous_value"].format(
            callsign=str(state.get("val_ref_callsign", "")).upper(),
            method=options["tx_ab_method"]["simultaneous"]["label"],
        )
    return (
        f"{str(state.get('val_ref_callsign', '')).upper()} · "
        f"{options['reference_design']['hardware_ab']['label']}"
    )


def render_configuration_review(
    streamlit_api,
    t,
    guided_content,
    state: Mapping[str, Any],
    *,
    on_open_classic=None,
):
    """Render the shared active configuration summary and return its action slot."""
    messages = guided_content["messages"]
    use_case = derive_analysis_question(state)
    is_benchmark = use_case in {"rx_benchmark", "tx_benchmark"}
    lines = [
        f"- **{messages['review_question']}:** {guided_content['options']['use_cases'][use_case]['label']}",
        f"- **{messages['review_target']}:** "
        + messages["review_target_value"].format(
            callsign=str(state.get("val_callsign", "")).upper(),
            qth=str(state.get("val_qth", "")).upper(),
        ),
    ]
    if is_benchmark:
        lines.append(
            f"- **{messages['review_reference']}:** "
            f"{reference_review_value(state, guided_content)}"
        )
    lines.append(
        f"- **{messages['review_band_window']}:** {state.get('val_band')} · "
        f"{_window_summary(state, guided_content)}"
    )
    if is_benchmark and (
        state.get("val_comp_mode") != "local_neighborhood"
        or float(state.get("val_benchmark_offset_db", 0.0)) != 0.0
    ):
        lines.append(
            f"- **{messages['review_correction']}:** "
            f"{float(state.get('val_benchmark_offset_db', 0.0)):+.1f} dB"
        )
    lines.extend(
        [
            f"- **{messages['review_population']}:** "
            + messages["review_population_value"].format(
                special=(
                    messages["included"]
                    if state.get("val_exclude_special_callsigns")
                    else messages["not_included"]
                ),
                moving=(
                    messages["included"]
                    if state.get("val_filter_moving")
                    else messages["not_included"]
                ),
            ),
            f"- **{messages['review_scope']}:** "
            f"{state.get('val_max_peer_distance_km', 22000)} km · "
            f"{t[SOLAR_KEYS.get(state.get('val_solar'), 'opt_solar_all')]}",
            f"- **{messages['review_evidence']}:** "
            f"{evidence_value_summary(state, guided_content)}",
            f"- **{messages['review_result']}:** "
            f"{messages['result_benchmark' if is_benchmark else 'result_performance']}",
        ]
    )
    if is_benchmark:
        is_outlier_reporting_enabled = state.get(
            "val_report_delta_snr_outlier_candidates",
            False,
        )
        lines.append(
            f"- **{t['lbl_report_delta_snr_outlier_candidates']}:** "
            + ("\u2713" if is_outlier_reporting_enabled else "\u2014")
        )
        if is_outlier_reporting_enabled:
            lines.append(
                f"- **{t['lbl_delta_snr_outlier_detector_thresholds']}:** "
                + t["fmt_delta_snr_outlier_detector_thresholds"].format(
                    departure=float(
                        state["val_delta_snr_outlier_minimum_departure_db"]
                    ),
                    robust_z=float(
                        state["val_delta_snr_outlier_minimum_robust_z"]
                    ),
                    baseline_difference=float(
                        state[
                            "val_delta_snr_outlier_maximum_baseline_difference_db"
                        ]
                    ),
                )
            )
    streamlit_api.markdown("\n".join(lines))
    if state.get("val_snr_correction_mode") == "establish_offset":
        streamlit_api.warning(messages["calibration_run_notice"])
    if on_open_classic is not None:
        streamlit_api.button(
            messages["open_classic"],
            icon=":material/settings:",
            key="guided_open_classic",
            on_click=on_open_classic,
            width="stretch",
        )
    return streamlit_api.empty()
