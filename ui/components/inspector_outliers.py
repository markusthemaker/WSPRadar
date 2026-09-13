"""Outlier Report presentation over prepared detector and review models.

The renderer receives its run, presentation and session context explicitly.
Candidate navigation delegates all state changes to the selection owner.
"""

import numpy as np
import pandas as pd
import streamlit as st

from config import COMPASS
from ui.components.inspector_common import render_compact_dataframe
from ui.inspector import selection_state as inspector_selection
from ui.inspector.outlier_report import OUTLIER_UNAVAILABLE_VALUE
from ui.inspector.presentation import format_localized_decimal, format_localized_integer
from ui.page_navigation import DRILLDOWN_ANCHOR_ID, STATION_INSIGHTS_ANCHOR_ID
from ui.result_guidance import (
    RESULT_GUIDANCE_OUTLIER_REPORT,
    render_result_guidance_popover,
)
from ui.result_hierarchy import evidence_child_header_html



def format_signed_outlier_db(value, translations):
    """Format one signed dB value with the active decimal separator."""
    numeric_value = float(value)
    sign = "+" if numeric_value >= 0.0 else "\u2212"
    return f"{sign}{format_localized_decimal(abs(numeric_value), translations)}"


def format_outlier_utc_interval(start_utc, end_utc, translations):
    """Format one exact UTC interval without relying on process locale."""
    interval_start = pd.Timestamp(start_utc).tz_convert("UTC")
    interval_end = pd.Timestamp(end_utc).tz_convert("UTC")
    is_same_date = interval_start.date() == interval_end.date()
    month_names = str(translations["txt_outlier_utc_months"]).split("|")
    if len(month_names) != 12:
        raise ValueError("Outlier UTC month catalog must contain 12 entries.")

    def format_date(timestamp):
        return translations["fmt_outlier_utc_date"].format(
            day=timestamp.day,
            month=month_names[timestamp.month - 1],
            time=timestamp.strftime("%H:%M"),
        )

    start_text = format_date(interval_start)
    end_text = (
        interval_end.strftime("%H:%M")
        if is_same_date
        else format_date(interval_end)
    )
    return translations["fmt_outlier_utc_range"].format(
        start=start_text,
        end=end_text,
    )


def format_outlier_utc_range(report_entry, translations):
    """Format exact observed UTC bounds without exposing half-open sentinels."""
    interval_start = pd.Timestamp(report_entry.start_utc).tz_convert("UTC")
    interval_end = pd.Timestamp(report_entry.end_utc).tz_convert("UTC")
    if interval_end - interval_start <= pd.Timedelta(nanoseconds=1):
        month_names = str(translations["txt_outlier_utc_months"]).split("|")
        if len(month_names) != 12:
            raise ValueError(
                "Outlier UTC month catalog must contain 12 entries."
            )
        timestamp_text = translations["fmt_outlier_utc_date"].format(
            day=interval_start.day,
            month=month_names[interval_start.month - 1],
            time=interval_start.strftime("%H:%M"),
        )
        return translations["fmt_outlier_utc_instant"].format(
            timestamp=timestamp_text,
        )
    if interval_end > interval_start:
        interval_end -= pd.Timedelta(nanoseconds=1)
    return format_outlier_utc_interval(
        interval_start,
        interval_end,
        translations,
    )


def localized_outlier_direction(direction, translations):
    """Localize the east component of one canonical compass sector."""
    return str(direction).replace(
        "E",
        translations["abbr_compass_east"],
    )


def format_outlier_duration_minutes(value, translations):
    """Format an observed episode duration without false decimal precision."""
    numeric_value = float(value)
    decimals = 0 if np.isclose(numeric_value, round(numeric_value)) else 1
    return translations["fmt_outlier_minutes"].format(
        value=format_localized_decimal(
            numeric_value,
            translations,
            decimals=decimals,
        )
    )


def localized_outlier_event_kind(event_kind, translations):
    """Return the approved label for one detector event classification."""
    event_keys = {
        "spot_impulse": "txt_outlier_event_spot_impulse",
        "short_burst": "txt_outlier_event_short_burst",
        "sustained_excursion": "txt_outlier_event_sustained_excursion",
        "mixed_duration": "txt_outlier_event_mixed_duration",
    }
    try:
        return translations[event_keys[str(event_kind)]]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported Delta-SNR outlier event kind: {event_kind!r}."
        ) from exc


def validate_outlier_report_entry_counts(report_entry):
    """Validate one episode's narrowing path denominators."""
    contributing_count = int(report_entry.contributing_station_count)
    evaluable_count = int(report_entry.evaluable_station_count)
    flagged_count = int(report_entry.flagged_station_count)
    sign_counts = (
        int(report_entry.segment_positive_station_count),
        int(report_entry.segment_negative_station_count),
        int(report_entry.segment_neutral_station_count),
    )
    if not 0 <= flagged_count <= evaluable_count <= contributing_count:
        raise ValueError(
            "Outlier episode path counts must satisfy "
            "flagged <= assessed <= paired evidence."
        )
    if any(count < 0 for count in sign_counts):
        raise ValueError("Outlier episode sign counts must be non-negative.")
    if sum(sign_counts) != evaluable_count:
        raise ValueError(
            "Outlier episode above, below, and unchanged counts must sum "
            "to the assessed-path count."
        )
    return contributing_count - evaluable_count


def format_outlier_named_paired_unit_count(
    count,
    is_sequential,
    translations,
):
    """Name any complete paired-unit count in established WSPRadar terms."""
    unit_kind = "scheduled" if is_sequential else "joint"
    count = int(count)
    number = "singular" if count == 1 else "plural"
    return translations[f"fmt_outlier_{unit_kind}_count_{number}"].format(
        count=format_localized_integer(count, translations)
    )


def candidate_joint_evidence_times(candidate, episode_card):
    """Return the exact listed Joint timestamps belonging to one path episode."""
    episode_start_utc = pd.Timestamp(candidate.start_utc).tz_convert("UTC")
    episode_end_utc = pd.Timestamp(candidate.end_utc).tz_convert("UTC")
    evidence_times = tuple(
        sorted(
            {
                pd.Timestamp(evidence_row.evidence_utc).tz_convert("UTC")
                for evidence_row in episode_card.evidence_rows
                if evidence_row.station_identity == candidate.station_identity
                and episode_start_utc
                <= pd.Timestamp(evidence_row.evidence_utc).tz_convert("UTC")
                < episode_end_utc
            }
        )
    )
    if len(evidence_times) != int(candidate.paired_unit_count):
        raise ValueError(
            "Listed Joint evidence must match the detector episode count."
        )
    return evidence_times


def format_outlier_optional_minutes(value, translations):
    """Format one minute interval or an em dash when no interval exists."""
    if value is None:
        return OUTLIER_UNAVAILABLE_VALUE
    return format_outlier_duration_minutes(value, translations)


def format_outlier_candidate_facts(
    candidate,
    episode_card,
    translations,
    is_sequential,
):
    """Format path-centred evidence timing and Delta-SNR interpretation facts."""
    evidence_times = candidate_joint_evidence_times(candidate, episode_card)
    first_to_last_minutes = (
        evidence_times[-1] - evidence_times[0]
    ).total_seconds() / 60.0
    interval_minutes = [
        (later_utc - earlier_utc).total_seconds() / 60.0
        for earlier_utc, later_utc in zip(
            evidence_times,
            evidence_times[1:],
        )
    ]
    median_interval_minutes = (
        float(np.median(interval_minutes)) if interval_minutes else None
    )
    largest_gap_minutes = max(interval_minutes) if interval_minutes else None
    observation_context = translations[
        "fmt_outlier_path_observation_context"
    ].format(
        paired_count=format_outlier_named_paired_unit_count(
            len(evidence_times),
            is_sequential,
            translations,
        ),
        first_to_last_span=format_outlier_duration_minutes(
            first_to_last_minutes,
            translations,
        ),
        median_interval=format_outlier_optional_minutes(
            median_interval_minutes,
            translations,
        ),
        largest_gap=format_outlier_optional_minutes(
            largest_gap_minutes,
            translations,
        ),
    )
    delta_context = translations["fmt_outlier_path_delta_context"].format(
        expected_local=format_signed_outlier_db(
            candidate.station_baseline_db,
            translations,
        ),
        observed_median=format_signed_outlier_db(
            candidate.episode_median_delta_snr_db,
            translations,
        ),
        largest_departure=format_signed_outlier_db(
            candidate.peak_anomaly_db,
            translations,
        ),
    )
    return f"{observation_context}\n\n{delta_context}"


def format_outlier_table_db(value, translations):
    """Format one signed table value or an em dash for unavailable evidence."""
    if value is None:
        return OUTLIER_UNAVAILABLE_VALUE
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return OUTLIER_UNAVAILABLE_VALUE
    if not np.isfinite(numeric_value):
        return OUTLIER_UNAVAILABLE_VALUE
    return format_signed_outlier_db(numeric_value, translations)


def format_outlier_evidence_utc(evidence_utc, translations):
    """Format one exact native evidence timestamp in UTC."""
    timestamp = pd.Timestamp(evidence_utc).tz_convert("UTC")
    return translations["fmt_outlier_evidence_utc"].format(
        timestamp=timestamp.strftime("%Y-%m-%d %H:%M"),
    )


def build_outlier_cycle_evidence_table(
    episode_card,
    translations,
):
    """Build the compact chronological table of episode-member Joint rows."""
    columns = [
        translations["col_outlier_evidence_utc"],
        translations["col_outlier_evidence_path"],
        translations["col_outlier_evidence_direction"],
        translations["col_outlier_evidence_local_baseline"],
        translations["col_outlier_evidence_delta_snr"],
        translations["col_outlier_evidence_residual"],
    ]
    rows = []
    for evidence_row in episode_card.evidence_rows:
        direction = (
            localized_outlier_direction(
                evidence_row.direction_sector,
                translations,
            )
            if evidence_row.direction_sector in COMPASS
            else OUTLIER_UNAVAILABLE_VALUE
        )
        rows.append(
            {
                columns[0]: format_outlier_evidence_utc(
                    evidence_row.evidence_utc,
                    translations,
                ),
                columns[1]: evidence_row.station_identity.label,
                columns[2]: direction,
                columns[3]: format_outlier_table_db(
                    evidence_row.local_baseline_db,
                    translations,
                ),
                columns[4]: format_outlier_table_db(
                    evidence_row.delta_snr_db,
                    translations,
                ),
                columns[5]: format_outlier_table_db(
                    evidence_row.residual_db,
                    translations,
                ),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def outlier_candidates_by_identity(report_entry):
    """Group one report entry's candidates in detector path order."""
    candidates_by_identity = {}
    for candidate in report_entry.candidates:
        candidates_by_identity.setdefault(
            candidate.station_identity,
            [],
        ).append(candidate)
    grouped_candidates = []
    for station_identity in report_entry.station_identities:
        path_candidates = tuple(
            candidates_by_identity.get(station_identity, ())
        )
        if not path_candidates:
            raise ValueError(
                "Every flagged episode path must retain a candidate."
            )
        grouped_candidates.append((station_identity, path_candidates))
    return tuple(grouped_candidates)


def outlier_candidate_direction_text(candidates, translations):
    """Return the retained direction or an explicit unavailable label."""
    directions = tuple(
        dict.fromkeys(
            localized_outlier_direction(
                candidate.direction_sector,
                translations,
            )
            for candidate in candidates
            if candidate.direction_sector in COMPASS
        )
    )
    return ", ".join(directions) or translations[
        "txt_outlier_direction_unavailable"
    ]


def render_outlier_candidate_navigation(
    parent_container,
    candidate,
    outlier_model,
    *,
    session_state,
    candidate_key_suffix,
    analysis_id,
    run_id,
    scope_token,
    translations,
):
    """Render the two candidate-specific downward navigation actions."""
    action_container = parent_container.container(
        key=f"outlier_path_actions_{candidate_key_suffix}",
        horizontal=True,
        horizontal_alignment="right",
        vertical_alignment="center",
        gap="small",
    )
    if action_container.button(
        translations["btn_outlier_show_path_in_station_insights"],
        key=f"show_outlier_station_{candidate_key_suffix}",
        type="tertiary",
    ):
        inspector_selection.select_outlier_candidate(
            candidate,
            outlier_model,
            session_state,
            analysis_id=analysis_id,
            run_id=run_id,
            scope_token=scope_token,
            navigation_anchor_id=STATION_INSIGHTS_ANCHOR_ID,
        )
        st.rerun(scope="app")
    if action_container.button(
        translations["btn_outlier_show_drilldown_details"],
        key=f"show_outlier_drilldown_{candidate_key_suffix}",
        type="tertiary",
    ):
        inspector_selection.select_outlier_candidate(
            candidate,
            outlier_model,
            session_state,
            analysis_id=analysis_id,
            run_id=run_id,
            scope_token=scope_token,
            navigation_anchor_id=DRILLDOWN_ANCHOR_ID,
        )
        st.rerun(scope="app")


def render_delta_snr_outlier_report(
    outlier_model,
    report_view_model,
    *,
    session_state,
    t,
    language,
    analysis_id,
    run_id,
    scope_token,
    is_sequential,
    analysis_context,
):
    """Render native shared-gate detector episodes as review cards."""
    if outlier_model is None or report_view_model is None:
        raise ValueError(
            "Enabled Delta-SNR outlier reporting requires detector and "
            "report view models."
        )
    report_title = t["hdr_results_outlier_report"]
    st.markdown(
        evidence_child_header_html(
            report_title,
            t["sub_results_outlier_report"],
        ),
        unsafe_allow_html=True,
    )
    render_result_guidance_popover(
        RESULT_GUIDANCE_OUTLIER_REPORT,
        report_title,
        language=language,
        translations=t,
        key=(
            f"results_guidance_outlier_report_"
            f"{analysis_id}_{run_id}_{scope_token}"
        ),
        analysis_id=analysis_id,
        is_compare=True,
        is_sequential=is_sequential,
        analysis_context=analysis_context,
    )
    report_entries = outlier_model.report_entries
    paired_evidence_name = t[
        "txt_outlier_paired_evidence_scheduled"
        if is_sequential
        else "txt_outlier_paired_evidence_joint"
    ]
    if outlier_model.populated_station_cycle_count == 0:
        st.info(
            t["msg_outlier_report_insufficient_paired_evidence"].format(
                paired_evidence=paired_evidence_name,
            ),
            icon=":material/info:",
        )
        return
    if outlier_model.evaluable_station_cycle_count == 0:
        st.info(
            t["msg_outlier_report_insufficient_local_baseline"].format(
                populated=format_localized_integer(
                    outlier_model.populated_station_cycle_count,
                    t,
                ),
                abstained=format_localized_integer(
                    outlier_model.abstained_station_cycle_count,
                    t,
                ),
                paired_evidence=paired_evidence_name,
            ),
            icon=":material/info:",
        )
        return
    if not report_entries:
        st.info(
            t["msg_outlier_report_no_candidates"].format(
                assessed=format_localized_integer(
                    outlier_model.evaluable_station_cycle_count,
                    t,
                ),
                abstained=format_localized_integer(
                    outlier_model.abstained_station_cycle_count,
                    t,
                ),
                populated=format_localized_integer(
                    outlier_model.populated_station_cycle_count,
                    t,
                ),
                paired_evidence=paired_evidence_name,
            ),
            icon=":material/search_off:",
        )
        return

    if len(report_view_model.cards) != len(report_entries):
        raise ValueError(
            "Delta-SNR report view-model cards must match detector entries."
        )
    evidence_expander_key = (
        "exp_outlier_scheduled_pair_evidence"
        if is_sequential
        else "exp_outlier_wspr_cycle_evidence"
    )
    for episode_card, report_entry in zip(
        report_view_model.cards,
        report_entries,
    ):
        if episode_card.report_entry != report_entry:
            raise ValueError(
                "Delta-SNR report view-model entry order is inconsistent."
            )
        validate_outlier_report_entry_counts(report_entry)
        episode_start_utc = pd.Timestamp(report_entry.start_utc)
        episode_end_utc = pd.Timestamp(report_entry.end_utc)
        episode_key_suffix = (
            f"{analysis_id}_{run_id}_{scope_token}_"
            f"{report_entry.episode_index}_"
            f"{episode_start_utc.value}_{episode_end_utc.value}_"
            f"{outlier_model.candidate_signature[:12]}"
        )
        episode_container = st.container(
            border=True,
            key=f"outlier_episode_{episode_key_suffix}",
        )
        episode_utc_range = format_outlier_utc_range(report_entry, t)
        episode_container.markdown(
            f"##### {localized_outlier_event_kind(report_entry.event_kind, t)} · "
            f"{episode_utc_range}"
        )
        grouped_candidates = outlier_candidates_by_identity(report_entry)
        for path_index, (station_identity, path_candidates) in enumerate(
            grouped_candidates,
            start=1,
        ):
            path_heading = (
                "###### "
                + t["fmt_outlier_path_heading"].format(
                    index=format_localized_integer(path_index, t),
                    identity=station_identity.label,
                    direction=outlier_candidate_direction_text(
                        path_candidates,
                        t,
                    ),
                )
            )
            if len(path_candidates) > 1:
                episode_container.markdown(path_heading)
            for candidate in path_candidates:
                candidate_key_suffix = (
                    f"{episode_key_suffix}_{path_index}_"
                    f"{station_identity.callsign}_{station_identity.locator}_"
                    f"{int(candidate.start_utc.value)}_"
                    f"{int(candidate.end_utc.value)}"
                )
                path_heading_container = episode_container.container(
                    key=f"outlier_path_heading_{candidate_key_suffix}",
                    horizontal=True,
                    horizontal_alignment="distribute",
                    vertical_alignment="center",
                    gap="small",
                )
                if len(path_candidates) > 1:
                    path_heading_container.markdown(
                        "**"
                        + t["fmt_outlier_candidate_timeframe"].format(
                            utc_range=format_outlier_utc_range(
                                candidate,
                                t,
                            )
                        )
                        + "**"
                    )
                else:
                    path_heading_container.markdown(path_heading)
                render_outlier_candidate_navigation(
                    path_heading_container,
                    candidate,
                    outlier_model,
                    session_state=session_state,
                    candidate_key_suffix=candidate_key_suffix,
                    analysis_id=analysis_id,
                    run_id=run_id,
                    scope_token=scope_token,
                    translations=t,
                )
                episode_container.caption(
                    format_outlier_candidate_facts(
                        candidate,
                        episode_card,
                        t,
                        is_sequential,
                    )
                )
        if report_entry.flagged_station_count > 1:
            if episode_container.button(
                t["btn_outlier_show_all_paths_in_station_insights"],
                key=f"show_all_outlier_paths_{episode_key_suffix}",
                type="tertiary",
                icon=":material/checklist:",
            ):
                inspector_selection.select_outlier_episode_paths(
                    report_entry,
                    session_state,
                    analysis_id=analysis_id,
                    run_id=run_id,
                    scope_token=scope_token,
                )
                st.rerun(scope="app")
        if len(episode_card.evidence_rows) > 1:
            evidence_expander = episode_container.expander(
                t[evidence_expander_key].format(
                    utc_range=episode_utc_range,
                ),
                expanded=False,
                key=f"outlier_cycle_evidence_{episode_key_suffix}",
                icon=":material/table_view:",
            )
            render_compact_dataframe(
                evidence_expander,
                build_outlier_cycle_evidence_table(
                    episode_card,
                    t,
                ),
                width="stretch",
                hide_index=True,
            )
