"""Mode-aware interpretation guidance for the shared result hierarchy."""

from dataclasses import dataclass

import streamlit as st

from core.analysis_context import (
    COMPARISON_HARDWARE_AB,
    COMPARISON_LOCAL_NEIGHBORHOOD,
    COMPARISON_NONE,
    COMPARISON_REFERENCE_STATION,
    LOCAL_BENCHMARK_BEST,
    LOCAL_BENCHMARK_MEDIAN,
)
from i18n import RESULT_GUIDANCE, absolute_terms
from ui.result_hierarchy import remote_station_type, result_direction


RESULT_GUIDANCE_CONTEXT = "context"
RESULT_GUIDANCE_MAP = "map"
RESULT_GUIDANCE_SEGMENT = "segment"
RESULT_GUIDANCE_COMPARISON_EVIDENCE = "comparison_evidence"
RESULT_GUIDANCE_TEMPORAL_EVIDENCE = "temporal_evidence"
RESULT_GUIDANCE_SUCCESS_EVIDENCE = "success_evidence"
RESULT_GUIDANCE_STATION_INSIGHTS = "station_insights"
RESULT_GUIDANCE_SELECTED_STATIONS = "selected_stations"
RESULT_GUIDANCE_DRILLDOWN = "drilldown"
RESULT_GUIDANCE_DOWNLOAD = "download"

RESULT_GUIDANCE_SECTION_IDS = frozenset(
    {
        RESULT_GUIDANCE_CONTEXT,
        RESULT_GUIDANCE_MAP,
        RESULT_GUIDANCE_SEGMENT,
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        RESULT_GUIDANCE_STATION_INSIGHTS,
        RESULT_GUIDANCE_SELECTED_STATIONS,
        RESULT_GUIDANCE_DRILLDOWN,
        RESULT_GUIDANCE_DOWNLOAD,
    }
)


@dataclass(frozen=True)
class ResultGuidanceText:
    """Hold the two interpretation layers rendered inside one result popover."""

    read: str
    limits: str


def _localized_guidance_item(section_content, item_key, format_values):
    """Return one localized catalog item after checked placeholder expansion."""
    try:
        item = section_content[item_key]
    except KeyError as exc:
        raise ValueError(f"Unknown result-guidance item: {item_key}") from exc
    return ResultGuidanceText(
        read=str(item["read"]).format(**format_values),
        limits=str(item["limits"]).format(**format_values),
    )


def _comparison_benchmark_guidance_key(analysis_context):
    """Return the generic guidance key for the active Compare benchmark."""
    comparison_mode = getattr(
        analysis_context,
        "comparison_mode",
        COMPARISON_NONE,
    )
    if comparison_mode == COMPARISON_HARDWARE_AB:
        return "benchmark_hardware"
    if comparison_mode == COMPARISON_REFERENCE_STATION:
        return "benchmark_reference"
    if comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD:
        local_benchmark = getattr(
            analysis_context,
            "local_benchmark",
            LOCAL_BENCHMARK_MEDIAN,
        )
        if local_benchmark == LOCAL_BENCHMARK_MEDIAN:
            return "benchmark_local_median"
        if local_benchmark == LOCAL_BENCHMARK_BEST:
            return "benchmark_local_best"
        raise ValueError(f"Unsupported local benchmark: {local_benchmark}")
    raise ValueError(
        "Compare result guidance requires a supported comparison mode"
    )


def _result_guidance_item_keys(
    section_id,
    *,
    direction,
    is_compare,
    is_sequential,
    analysis_context,
):
    """Resolve generic content keys for one valid result section and mode."""
    if section_id == RESULT_GUIDANCE_DOWNLOAD:
        return ["download"]

    if direction not in {"RX", "TX"}:
        raise ValueError("Result guidance requires an RX or TX analysis ID")
    if is_sequential and (
        not is_compare
        or direction != "TX"
        or getattr(analysis_context, "comparison_mode", COMPARISON_NONE)
        != COMPARISON_HARDWARE_AB
    ):
        raise ValueError(
            "Scheduled result guidance is valid only for TX Hardware A/B Compare"
        )

    if section_id == RESULT_GUIDANCE_CONTEXT:
        if not is_compare:
            return [f"context_{direction.lower()}_success"]
        context_key = (
            "context_tx_compare_scheduled"
            if is_sequential
            else f"context_{direction.lower()}_compare"
        )
        return [
            context_key,
            _comparison_benchmark_guidance_key(analysis_context),
        ]

    if section_id == RESULT_GUIDANCE_MAP:
        if is_compare:
            return [f"map_compare_{direction.lower()}"]
        return ["map_success"]

    if section_id == RESULT_GUIDANCE_SEGMENT:
        return ["segment"]

    if section_id == RESULT_GUIDANCE_COMPARISON_EVIDENCE:
        if not is_compare:
            raise ValueError(
                "Comparison Evidence guidance is unavailable for Success"
            )
        return [
            "comparison_evidence_scheduled"
            if is_sequential
            else "comparison_evidence_joint"
        ]

    if section_id == RESULT_GUIDANCE_TEMPORAL_EVIDENCE:
        if not is_compare:
            raise ValueError(
                "Temporal Evidence guidance is unavailable for Success"
            )
        return [
            "temporal_evidence_scheduled"
            if is_sequential
            else "temporal_evidence_joint"
        ]

    if section_id == RESULT_GUIDANCE_SUCCESS_EVIDENCE:
        if is_compare:
            raise ValueError(
                "Success Evidence guidance is unavailable for Compare"
            )
        return ["success_evidence"]

    if section_id == RESULT_GUIDANCE_STATION_INSIGHTS:
        if not is_compare:
            return ["station_insights_success"]
        return [
            "station_insights_compare_scheduled"
            if is_sequential
            else "station_insights_compare_joint"
        ]

    if section_id == RESULT_GUIDANCE_SELECTED_STATIONS:
        if not is_compare:
            return ["selected_success"]
        return [
            "selected_compare_scheduled"
            if is_sequential
            else "selected_compare_joint"
        ]

    if section_id == RESULT_GUIDANCE_DRILLDOWN:
        if not is_compare:
            return ["drilldown_success"]
        item_keys = [
            "drilldown_compare_scheduled"
            if is_sequential
            else "drilldown_compare_joint"
        ]
        if (
            getattr(analysis_context, "comparison_mode", COMPARISON_NONE)
            == COMPARISON_LOCAL_NEIGHBORHOOD
            and getattr(
                analysis_context,
                "local_benchmark",
                LOCAL_BENCHMARK_MEDIAN,
            )
            == LOCAL_BENCHMARK_MEDIAN
        ):
            item_keys.append("drilldown_local_median")
        return item_keys

    raise ValueError(f"Unknown result-guidance section: {section_id}")


def build_result_guidance(
    section_id,
    *,
    language,
    translations,
    analysis_id="",
    is_compare=False,
    is_sequential=False,
    analysis_context=None,
):
    """Build self-contained localized Markdown for one result-help popover.

    The resolver uses only semantic mode fields. It never parses localized
    labels or record identities, and its output is presentation-only.
    """
    if section_id not in RESULT_GUIDANCE_SECTION_IDS:
        raise ValueError(f"Unknown result-guidance section: {section_id}")
    try:
        guidance_content = RESULT_GUIDANCE[language]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported result-guidance language: {language}"
        ) from exc

    direction = result_direction(analysis_id)
    opportunity_terms = absolute_terms(translations, direction)
    format_values = {
        "peer_type": remote_station_type(analysis_id),
        "counter": opportunity_terms["counter"],
        "formula": opportunity_terms["formula_spaced"],
        "radius": int(
            getattr(analysis_context, "neighborhood_radius_km", 100)
        ),
    }
    item_keys = _result_guidance_item_keys(
        section_id,
        direction=direction,
        is_compare=bool(is_compare),
        is_sequential=bool(is_sequential),
        analysis_context=analysis_context,
    )
    items = [
        _localized_guidance_item(
            guidance_content["sections"],
            item_key,
            format_values,
        )
        for item_key in item_keys
    ]
    read_text = " ".join(item.read for item in items)
    limits_text = " ".join(item.limits for item in items)
    return (
        f"**{guidance_content['read_label']}** {read_text}\n\n"
        f"**{guidance_content['limits_label']}** {limits_text}"
    )


def render_result_guidance_popover(
    section_id,
    section_title,
    *,
    language,
    translations,
    key,
    analysis_id="",
    is_compare=False,
    is_sequential=False,
    analysis_context=None,
):
    """Render one static click-open interpretation popover without a rerun."""
    guidance_markdown = build_result_guidance(
        section_id,
        language=language,
        translations=translations,
        analysis_id=analysis_id,
        is_compare=is_compare,
        is_sequential=is_sequential,
        analysis_context=analysis_context,
    )
    guidance_content = RESULT_GUIDANCE[language]
    with st.popover(
        guidance_content["trigger"],
        icon=":material/help_outline:",
        type="tertiary",
        help=guidance_content["trigger_help"].format(section=section_title),
        width="content",
        key=key,
        on_change="ignore",
    ):
        st.markdown(guidance_markdown)
