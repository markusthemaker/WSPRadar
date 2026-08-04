"""Pure presentation helpers for the progressive result-evidence hierarchy."""

from dataclasses import dataclass
from datetime import datetime
from html import escape
import re

from core.analysis_context import (
    COMPARISON_HARDWARE_AB,
    COMPARISON_LOCAL_NEIGHBORHOOD,
    COMPARISON_REFERENCE_STATION,
    LOCAL_BENCHMARK_BEST,
)
from ui.reference_correction import configured_snr_correction_notice


@dataclass(frozen=True)
class ResultContext:
    """Describe the completed analysis context shown above one result flow."""

    title: str
    subtitle: str
    metadata: str
    evidence_path_label: str
    evidence_path: str
    configured_snr_correction: str = ""


def _escaped(value):
    """Return one dynamic presentation value escaped for HTML text content."""
    return escape(str(value), quote=True)


def _escaped_with_line_breaks(value):
    """Escape dynamic text and preserve its explicit line boundaries safely."""
    normalized = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return _escaped(normalized).replace("\n", "<br>")


def _format_utc_timestamp(value):
    """Format one datetime-like value as a compact minute-resolution timestamp."""
    if isinstance(value, datetime) or hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)


def result_direction(analysis_id):
    """Return the canonical RX or TX direction encoded in an analysis ID."""
    direction = str(analysis_id).upper().split("_", 1)[0]
    return direction if direction in {"RX", "TX"} else ""


def remote_station_type(analysis_id):
    """Return the remote station role contributing evidence to an analysis."""
    return "TX" if result_direction(analysis_id) == "RX" else "RX"


def _localized_integer(count, translations):
    """Format one non-negative presentation count with localized grouping."""
    separator = translations["fmt_results_thousands_separator"]
    return f"{int(count):,}".replace(",", str(separator))


def comparison_constraint_text(analysis, analysis_context, translations):
    """Return the active Benchmark constraint for result provenance metadata."""
    if not bool(analysis.get("is_compare")):
        return ""

    comparison_mode = getattr(analysis_context, "comparison_mode", "")
    if comparison_mode == COMPARISON_REFERENCE_STATION:
        reference_grid4 = str(
            getattr(analysis_context, "reference_qth", "")
        ).strip().upper()[:4]
        if not reference_grid4:
            return ""
        return translations["txt_results_reference_grid4"].format(
            grid4=reference_grid4
        )

    if comparison_mode == COMPARISON_HARDWARE_AB:
        shared_grid4 = str(
            getattr(analysis_context, "qth", "")
        ).strip().upper()[:4]
        if not shared_grid4:
            return ""
        constraint = translations["txt_results_shared_grid4"].format(
            grid4=shared_grid4
        )
        if analysis.get("is_sequential"):
            schedule = translations["txt_results_tx_schedule"].format(
                interval=int(
                    getattr(
                        analysis_context,
                        "tx_ab_repeat_interval_minutes",
                        10,
                    )
                ),
                target_phase=f"{int(getattr(analysis_context, 'tx_ab_target_start_minute', 0)):02d}",
                reference_phase=f"{int(getattr(analysis_context, 'tx_ab_reference_start_minute', 2)):02d}",
            )
            return f"{constraint} · {schedule}"
        return constraint

    if comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD:
        is_local_best = (
            getattr(analysis_context, "local_benchmark", "")
            == LOCAL_BENCHMARK_BEST
        )
        benchmark_key = (
            "comp_title_local_best"
            if is_local_best
            else "comp_title_local_median"
        )
        benchmark = translations[benchmark_key].format(
            radius=int(
                getattr(analysis_context, "neighborhood_radius_km", 100)
            )
        )
        return translations["txt_results_reference_benchmark"].format(
            benchmark=benchmark
        )

    return ""


def build_result_context(
    analysis,
    analysis_context,
    start_utc,
    end_utc,
    translations,
):
    """Build localized run identity without changing the figure's export title."""
    direction = result_direction(analysis.get("id", ""))
    is_compare = bool(analysis.get("is_compare"))
    title_key = "hdr_results_compare" if is_compare else "hdr_results_success"
    title = translations[title_key].format(direction=direction)

    callsign = str(getattr(analysis_context, "callsign", "")).upper()
    if is_compare and analysis.get("is_sequential"):
        subtitle = translations["sub_results_compare_scheduled"].format(
            callsign=callsign
        )
    elif is_compare:
        figure_title = str(analysis.get("title", ""))
        _prefix, separator, title_context = figure_title.partition(": ")
        subtitle = title_context if separator else figure_title
    elif direction == "RX":
        subtitle = translations["sub_results_rx_success"].format(
            callsign=callsign
        )
    else:
        subtitle = translations["sub_results_tx_success"].format(
            callsign=callsign
        )

    utc_window = (
        f"{_format_utc_timestamp(start_utc)} – "
        f"{_format_utc_timestamp(end_utc)} UTC"
    )
    metadata = translations["txt_results_metadata"].format(
        band=getattr(analysis_context, "band", ""),
        utc_window=utc_window,
        qth=str(getattr(analysis_context, "qth", "")).upper(),
    )
    comparison_constraint = comparison_constraint_text(
        analysis,
        analysis_context,
        translations,
    )
    if comparison_constraint:
        metadata = f"{metadata} · {comparison_constraint}"
    evidence_path_key = (
        "txt_results_evidence_path"
        if is_compare
        else "txt_results_evidence_path_success"
    )
    correction_notice = configured_snr_correction_notice(
        analysis_context,
        translations,
        is_compare=is_compare,
        is_sequential=bool(analysis.get("is_sequential")),
    )
    return ResultContext(
        title=title,
        subtitle=subtitle,
        metadata=metadata,
        evidence_path_label=translations["lbl_results_evidence_path"],
        evidence_path=translations[evidence_path_key],
        configured_snr_correction=correction_notice,
    )


def result_context_html(context):
    """Render one completed run context as semantic, escaped HTML."""
    correction_html = (
        "<p class='result-context-meta result-context-correction'>"
        f"{_escaped(context.configured_snr_correction)}</p>"
        if context.configured_snr_correction
        else ""
    )
    return (
        "<section class='result-context-header' aria-label='"
        f"{_escaped(context.title)}'>"
        f"<h2 class='result-context-title'>{_escaped(context.title)}</h2>"
        f"<p class='result-context-subtitle'>{_escaped(context.subtitle)}</p>"
        f"<p class='result-context-meta'>{_escaped(context.metadata)}</p>"
        f"{correction_html}"
        "<p class='result-evidence-path'>"
        f"<span class='result-evidence-path-label'>"
        f"{_escaped(context.evidence_path_label)}</span>"
        f"<span>{_escaped(context.evidence_path)}</span>"
        "</p>"
        "</section>"
    )


def evidence_level_header_html(
    level_number,
    level_label,
    title,
    subtitle="",
    context="",
):
    """Render one numbered zoom level as semantic, escaped HTML."""
    normalized_level = int(level_number)
    subtitle_html = (
        "<p class='result-evidence-level-subtitle'>"
        f"{_escaped_with_line_breaks(subtitle)}</p>"
        if subtitle
        else ""
    )
    context_html = (
        "<p class='result-scope-context'>"
        f"{_escaped_with_line_breaks(context)}</p>"
        if context
        else ""
    )
    accessible_label = (
        f"{normalized_level:02d} · {level_label}: {title}"
    )
    return (
        "<header class='result-evidence-level-header "
        f"result-evidence-level-{normalized_level:02d}' "
        f"data-evidence-level='{normalized_level}' "
        f"aria-label='{_escaped(accessible_label)}'>"
        f"<h3 class='result-evidence-level-title'>{_escaped(title)}</h3>"
        f"{subtitle_html}{context_html}"
        "</header>"
    )


def evidence_child_header_html(title, subtitle=""):
    """Render one figure-group heading below an evidence zoom level."""
    subtitle_html = (
        f"<p class='result-evidence-child-subtitle'>{_escaped(subtitle)}</p>"
        if subtitle
        else ""
    )
    return (
        "<header class='result-evidence-child-header'>"
        f"<h4 class='result-evidence-child-title'>{_escaped(title)}</h4>"
        f"{subtitle_html}"
        "</header>"
    )


def scope_context_html(context):
    """Render one inherited-scope trail as escaped HTML."""
    return f"<p class='result-scope-context'>{_escaped(context)}</p>"


def scope_summary_html(context, evidence_context=""):
    """Render active scope and optional evidence as one compact HTML block."""
    evidence_html = (
        "<p class='result-scope-context result-scope-context-data'>"
        f"{_escaped(evidence_context)}</p>"
        if evidence_context
        else ""
    )
    return (
        "<div class='result-scope-summary'>"
        "<p class='result-scope-context result-scope-context-data'>"
        f"{_escaped(context)}</p>"
        f"{evidence_html}</div>"
    )


def segment_statistics_html(summary_lines):
    """Render escaped Segment Inspector statistics with scope-data typography."""
    summary_html = "".join(
        "<p class='result-scope-context result-scope-context-data'>"
        f"{_escaped(summary_line)}</p>"
        for summary_line in (summary_lines or ())
        if summary_line
    )
    return (
        "<div class='result-segment-statistics'>"
        f"{summary_html}</div>"
    )


def transition_prompt_html(prompt):
    """Render one muted cue that points to the next evidence level."""
    prompt_text = str(prompt).strip()
    arrow = "↓"
    if prompt_text.startswith(("↑", "↓")):
        arrow = prompt_text[0]
        prompt_text = prompt_text[1:].strip()
    return (
        "<p class='result-evidence-transition' aria-hidden='true'>"
        f"<span>{arrow}</span> {_escaped(prompt_text)}</p>"
    )


def utility_header_html(title, subtitle=""):
    """Render one unnumbered result utility section as semantic HTML."""
    subtitle_html = (
        f"<p class='result-utility-subtitle'>{_escaped(subtitle)}</p>"
        if subtitle
        else ""
    )
    return (
        "<header class='result-utility-header'>"
        f"<h3 class='result-utility-title'>{_escaped(title)}</h3>"
        f"{subtitle_html}"
        "</header>"
    )


def evidence_unit_label(count, *, is_compare, is_sequential, translations):
    """Return the localized singular or plural evidence unit for one count."""
    if not is_compare:
        unit = "confirmed_opportunity"
    elif is_sequential:
        unit = "scheduled_pair"
    else:
        unit = "joint_spot"
    plurality = "singular" if int(count) == 1 else "plural"
    label = translations[f"unit_{unit}_{plurality}"]
    return str(label)


def station_count_label(count, station_type, translations):
    """Return a localized station count with the RX or TX role preserved."""
    key = (
        "unit_station_singular"
        if int(count) == 1
        else "unit_station_plural"
    )
    return translations[key].format(
        count=_localized_integer(count, translations),
        station_type=station_type,
    )


def scope_evidence_text(
    station_count,
    evidence_count,
    *,
    analysis_id,
    is_compare,
    is_sequential,
    translations,
):
    """Return localized evidence depth for the active geographic scope."""
    return translations["txt_results_evidence_scope"].format(
        station_count=station_count_label(
            station_count,
            remote_station_type(analysis_id),
            translations,
        ),
        evidence_count=_localized_integer(evidence_count, translations),
        evidence_unit=evidence_unit_label(
            evidence_count,
            is_compare=is_compare,
            is_sequential=is_sequential,
            translations=translations,
        ),
    )


def active_scope_text(range_summary, direction_summary, translations):
    """Return the inherited geographic scope used by downstream evidence."""
    return translations["txt_results_active_scope"].format(
        distance=range_summary,
        direction=direction_summary,
    )


def station_scope_text(
    range_summary,
    direction_summary,
    station_count,
    analysis_id,
    translations,
):
    """Return active scope plus the number and role of contributing stations."""
    return translations["txt_results_station_scope"].format(
        distance=range_summary,
        direction=direction_summary,
        station_count=station_count_label(
            station_count,
            remote_station_type(analysis_id),
            translations,
        ),
    )


def _split_station_identity(identity):
    """Split a display identity of the form CALLSIGN (GRID), when available."""
    match = re.fullmatch(r"\s*(.*?)\s+\(([^()]*)\)\s*", str(identity))
    if match:
        return match.group(1), match.group(2)
    return str(identity), ""


def selected_station_label(
    station_identities,
    *,
    analysis_id,
    translations,
):
    """Return the exact label for one selected callsign-plus-locator identity."""
    identities = tuple(str(identity) for identity in station_identities)
    if len(identities) != 1:
        raise ValueError("Selected-station labels require exactly one identity.")
    return identities[0]


def selected_station_context(
    station_identities,
    evidence_count,
    *,
    analysis_id,
    is_sequential,
    translations,
):
    """Return localized Benchmark context for one selected radio path."""
    identities = [str(identity) for identity in station_identities]
    if len(identities) != 1:
        raise ValueError("Selected-station context requires exactly one identity.")
    selection_label = selected_station_label(
        identities,
        analysis_id=analysis_id,
        translations=translations,
    )
    localized_evidence_count = _localized_integer(
        evidence_count,
        translations,
    )
    unit = evidence_unit_label(
        evidence_count,
        is_compare=True,
        is_sequential=is_sequential,
        translations=translations,
    )
    station, locator = _split_station_identity(selection_label)
    return translations["sub_results_selected_station_single"].format(
        station=station,
        locator=locator,
        evidence_count=localized_evidence_count,
        evidence_unit=unit,
    )


def drilldown_subtitle(station_identities, analysis_id, translations):
    """Return localized row-level scope for exactly one selected identity."""
    identities = [str(identity) for identity in station_identities]
    if len(identities) != 1:
        raise ValueError("Drill-Down context requires exactly one station.")
    return translations["sub_results_drilldown_single"].format(
        station=identities[0]
    )
