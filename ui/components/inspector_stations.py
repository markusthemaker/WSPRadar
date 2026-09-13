"""Station Insights components over prepared Benchmark and Performance tables.

Views preserve display filtering and exact station intent. The selection owner
handles session transitions; preparation and export retain evidence ownership.
"""

from functools import partial

import pandas as pd
import streamlit as st

from ui.components.inspector_common import (
    render_compact_dataframe,
    render_reference_correction_notice,
    snr_column_config,
    supports_dataframe_selection_default,
    timed_span,
)
from ui.inspector import selection_state as inspector_selection
from ui.inspector.contracts import InspectorContext, InspectorScope, StationInsightsView
from ui.inspector.selection import InspectorSelection
from ui.inspector.view_models import compare_scope_availability
from ui.page_navigation import STATION_INSIGHTS_ANCHOR_ID, render_page_anchor
from ui.result_guidance import RESULT_GUIDANCE_STATION_INSIGHTS, render_result_guidance_popover
from ui.result_hierarchy import (
    evidence_level_header_html,
    remote_station_type,
    scope_context_html,
    station_scope_text,
)


STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS = (5, 4, 3)
SUCCESS_STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS = (9, 2)



def prioritize_focused_station_identities(
    station_table,
    station_column,
    locator_column,
    focused_identities,
):
    """Move exact focused identities to the top of a display-only table.

    Matching and non-matching rows each retain their existing relative order.
    The supplied table is never mutated, and a focus hidden by an active table
    filter remains absent rather than bypassing that filter.
    """
    normalized_identities = inspector_selection.validate_multiple_station_identity_records(
        focused_identities
    )
    if not normalized_identities or station_table.empty:
        return station_table
    focused_pairs = {
        (identity["callsign"], identity["locator"])
        for identity in normalized_identities
    }
    focused_positions = []
    remaining_positions = []
    for row_position, (callsign, locator) in enumerate(
        station_table[[station_column, locator_column]].itertuples(
            index=False,
            name=None,
        )
    ):
        identity_record = inspector_selection.station_identity_record(callsign, locator)
        identity_pair = (
            (
                identity_record["callsign"],
                identity_record["locator"],
            )
            if identity_record is not None
            else None
        )
        destination = (
            focused_positions
            if identity_pair in focused_pairs
            else remaining_positions
        )
        destination.append(row_position)
    if not focused_positions:
        return station_table
    return station_table.iloc[
        focused_positions + remaining_positions
    ].reset_index(drop=True)


def selection_requires_zero_hit_rows(
    station_table,
    station_column,
    locator_column,
    hit_column,
    configured_identities,
):
    """Return whether a Performance selection includes a hidden zero-hit row."""
    if isinstance(configured_identities, InspectorSelection):
        if not configured_identities.selected_stations:
            return False
        selected_pair = configured_identities.selected_stations[0].pair
    else:
        normalized_identities = inspector_selection.validate_single_station_identity_records(
            configured_identities
        )
        if not normalized_identities:
            return False
        selected_identity = normalized_identities[0]
        selected_pair = (
            selected_identity["callsign"],
            selected_identity["locator"],
        )
    hit_counts = pd.to_numeric(station_table[hit_column], errors="coerce")
    for row_position, (callsign, locator) in enumerate(
        station_table[[station_column, locator_column]].itertuples(
            index=False,
            name=None,
        )
    ):
        identity_record = inspector_selection.station_identity_record(callsign, locator)
        if identity_record is None:
            continue
        identity_pair = (
            identity_record["callsign"],
            identity_record["locator"],
        )
        if identity_pair != selected_pair:
            continue
        hit_count = hit_counts.iloc[row_position]
        if pd.isna(hit_count) or hit_count <= 0:
            return True
    return False


def warn_missing_station_identities(missing_identities, t):
    """Warn that saved identities are unavailable without choosing substitutes."""
    if not missing_identities:
        return
    missing_labels = ", ".join(
        f"{identity['callsign']} ({identity['locator']})"
        for identity in missing_identities
    )
    warning_template = t["warn_saved_station_unavailable"]
    st.warning(
        warning_template.format(stations=missing_labels),
        icon=":material/warning:",
    )


def render_performance_station_insights(
    context: InspectorContext,
    scope: InspectorScope,
    current_selection: InspectorSelection,
    prepared_segment,
    *,
    session_state,
) -> StationInsightsView:
    """Render Performance station controls and retain exact visible selection."""
    analysis_id = context.analysis_id
    run_id = context.run_id
    t = context.translations
    analysis_context = context.analysis_context
    presentation_context = context.presentation_context
    timing_collector = context.timing_collector
    scope_token = scope.scope_token
    range_summary = scope.range_summary
    direction_summary = scope.direction_summary
    opportunity_display_model = prepared_segment.bundle["display_model"]
    opportunity_terms = presentation_context.absolute_terms(
        "TX" if analysis_id.startswith("TX") else "RX"
    )
    station_col = opportunity_display_model["station_column"]
    loc_col = opportunity_display_model["locator_column"]
    km_col = opportunity_display_model["distance_column"]
    az_col = opportunity_display_model["azimuth_column"]
    hit_col = opportunity_display_model["hit_column"]
    full_segment_disp_df = opportunity_display_model["full_station_table"]

    zero_hits_key = f"opp_show_zero_hits_{analysis_id}_{run_id}_{scope_token}"
    configured_station_identities = current_selection
    show_zero_hits = inspector_selection.initialize_boolean_widget_state(
        session_state,
        zero_hits_key,
        inspector_selection.RESULTS_SHOW_ZERO_TARGET_STATE_KEY,
        selection_requires_zero_hit_rows(
            full_segment_disp_df,
            station_col,
            loc_col,
            hit_col,
            configured_station_identities,
        ),
    )

    disp_df = full_segment_disp_df
    if not show_zero_hits:
        disp_df = full_segment_disp_df.loc[
            full_segment_disp_df[hit_col] > 0
        ].reset_index(drop=True)

    level_three_container = st.container(
        key=(
            f"results_evidence_level_3_"
            f"{analysis_id}_{run_id}_{scope_token}"
        )
    )
    station_type = remote_station_type(analysis_id)
    station_insights_title = t["lbl_insights"]
    level_three_container.markdown(
        evidence_level_header_html(
            3,
            t["lbl_results_level_stations"],
            station_insights_title,
            t["sub_results_station_insights_success"].format(
                station_type=station_type
            ),
            station_scope_text(
                range_summary,
                direction_summary,
                len(disp_df),
                analysis_id,
                t,
            ),
        ),
        unsafe_allow_html=True,
    )
    with level_three_container:
        render_result_guidance_popover(
            RESULT_GUIDANCE_STATION_INSIGHTS,
            station_insights_title,
            language=presentation_context.language,
            translations=t,
            key=(
                f"results_guidance_station_insights_"
                f"{analysis_id}_{run_id}_{scope_token}"
            ),
            analysis_id=analysis_id,
            is_compare=False,
            is_sequential=False,
            analysis_context=analysis_context,
        )

    col_toggle, col_filter = level_three_container.columns(
        SUCCESS_STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS,
        vertical_alignment="center",
    )
    with col_toggle:
        show_zero_hits = st.toggle(
            opportunity_terms["show_counter"],
            key=zero_hits_key,
            on_change=inspector_selection.sync_boolean_widget_state,
            args=(session_state, zero_hits_key, inspector_selection.RESULTS_SHOW_ZERO_TARGET_STATE_KEY),
        )
        show_zero_hits = inspector_selection.sync_boolean_widget_state(
            session_state,
            zero_hits_key,
            inspector_selection.RESULTS_SHOW_ZERO_TARGET_STATE_KEY,
        )

    disp_df = full_segment_disp_df
    if not show_zero_hits:
        disp_df = full_segment_disp_df.loc[
            full_segment_disp_df[hit_col] > 0
        ].reset_index(drop=True)

    with col_filter:
        with st.popover(
            t["lbl_filter"],
            icon=":material/filter_alt:",
            width="stretch",
        ):
            filter_cols = st.multiselect(
                t["lbl_select_columns"],
                disp_df.columns,
                label_visibility="collapsed",
                key=f"opp_filter_cols_{analysis_id}_{run_id}_{scope_token}",
            )
            for column in filter_cols:
                if pd.api.types.is_numeric_dtype(disp_df[column]):
                    numeric = pd.to_numeric(disp_df[column], errors="coerce").dropna()
                    if not numeric.empty and numeric.min() < numeric.max():
                        step = 1.0 if pd.api.types.is_integer_dtype(numeric) else 0.1
                        selected = st.slider(
                            column,
                            float(numeric.min()),
                            float(numeric.max()),
                            (float(numeric.min()), float(numeric.max())),
                            step=step,
                            key=f"opp_filter_{column}_{analysis_id}_{run_id}_{scope_token}",
                        )
                        disp_df = disp_df[
                            pd.to_numeric(disp_df[column], errors="coerce").between(selected[0], selected[1])
                        ]

    table_key = f"tbl_{analysis_id}_{run_id}_{scope_token}"
    selection_changed_key = f"{table_key}_selection_changed"
    dataframe_kwargs = {
        "width": "stretch",
        "hide_index": True,
        "selection_mode": "single-row",
        "on_select": partial(
            inspector_selection.mark_station_selection_changed,
            session_state,
            selection_changed_key,
        ),
        "key": table_key,
        "column_config": snr_column_config(disp_df),
    }
    selection_default_rows, missing_station_identities = (
        inspector_selection.station_selection_default_rows(
            disp_df,
            station_col,
            loc_col,
            configured_station_identities,
        )
    )
    with level_three_container:
        warn_missing_station_identities(missing_station_identities, t)
    if supports_dataframe_selection_default():
        dataframe_kwargs["selection_default"] = {
            "selection": {"rows": selection_default_rows}
        }
    with timed_span(timing_collector, "opportunity station table render"):
        table_event = render_compact_dataframe(
            level_three_container,
            disp_df,
            **dataframe_kwargs,
        )

    selected_rows = [
        row
        for row in (table_event.selection.rows or [])
        if 0 <= row < len(disp_df)
    ][:1]
    inspector_selection.sync_selected_station_state_if_changed(
        session_state,
        selection_changed_key,
        inspector_selection.RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY,
        disp_df,
        selected_rows,
        station_col,
        loc_col,
    )

    return StationInsightsView(
        displayed_table=disp_df,
        export_station_table=disp_df,
        full_station_table=full_segment_disp_df,
        selected_station_table=disp_df,
        selected_rows=tuple(selected_rows),
        station_column=station_col,
        locator_column=loc_col,
        distance_column=km_col,
        azimuth_column=az_col,
        show_non_joint=False,
        show_zero_target=show_zero_hits,
        level_three_container=level_three_container,
    )


def render_benchmark_station_insights(
    context: InspectorContext,
    scope: InspectorScope,
    current_selection: InspectorSelection,
    prepared_segment,
    *,
    session_state,
) -> StationInsightsView:
    """Render Benchmark station controls without changing evidence ownership."""
    analysis_id = context.analysis_id
    run_id = context.run_id
    t = context.translations
    is_sequential = context.is_sequential
    analysis_context = context.analysis_context
    presentation_context = context.presentation_context
    timing_collector = context.timing_collector
    scope_token = scope.scope_token
    range_summary = scope.range_summary
    direction_summary = scope.direction_summary
    is_outlier_reporting_enabled = current_selection.is_outlier_reporting_enabled
    df_seg = prepared_segment.scope_rows
    compare_view_model = prepared_segment.bundle["view_model"]
    station_col = compare_view_model.station_column
    col_joint_name = compare_view_model.joint_column
    has_joint_rows, has_non_joint_rows = compare_scope_availability(df_seg)
    toggle_key = f"tgl_{analysis_id}_{run_id}_{scope_token}"
    default_state = has_non_joint_rows and not has_joint_rows
    show_non_joint = inspector_selection.initialize_boolean_widget_state(
        session_state,
        toggle_key,
        inspector_selection.RESULTS_SHOW_NON_JOINT_STATE_KEY,
        default_state,
    )

    disp_df = compare_view_model.station_table
    if not show_non_joint and col_joint_name in disp_df.columns:
        disp_df = disp_df[disp_df[col_joint_name] > 0].reset_index(drop=True)
    sorted_disp_df = disp_df
    full_segment_disp_df = compare_view_model.station_table

    render_page_anchor(STATION_INSIGHTS_ANCHOR_ID)
    level_three_container = st.container(
        key=(
            f"results_evidence_level_3_"
            f"{analysis_id}_{run_id}_{scope_token}"
        )
    )
    station_type = remote_station_type(analysis_id)
    station_insights_title = t["lbl_insights"]
    level_three_container.markdown(
        evidence_level_header_html(
            3,
            t["lbl_results_level_stations"],
            station_insights_title,
            t[
                "sub_results_station_insights_multi"
                if is_outlier_reporting_enabled
                else "sub_results_station_insights"
            ].format(
                station_type=station_type
            ),
            station_scope_text(
                range_summary,
                direction_summary,
                len(sorted_disp_df),
                analysis_id,
                t,
            ),
        ),
        unsafe_allow_html=True,
    )
    with level_three_container:
        render_result_guidance_popover(
            RESULT_GUIDANCE_STATION_INSIGHTS,
            station_insights_title,
            language=presentation_context.language,
            translations=t,
            key=(
                f"results_guidance_station_insights_"
                f"{analysis_id}_{run_id}_{scope_token}"
            ),
            analysis_id=analysis_id,
            is_compare=True,
            is_sequential=is_sequential,
            analysis_context=analysis_context,
            allows_multiple_station_selection=(
                is_outlier_reporting_enabled
            ),
        )
    # --- 1. Define layout columns ---
    # Give localized toggle labels enough room while preserving the filter width.
    col_ins1, col_ins2, col_ins3 = level_three_container.columns(
        STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS,
        vertical_alignment="center",
    )

    with col_ins1:
        sub_text = t["txt_station_insights_normalized_30dbm"]
        st.markdown(
            scope_context_html(sub_text.strip(" ()")),
            unsafe_allow_html=True,
        )

    with col_ins2:
        # Default to showing unpaired rows when the segment contains no joint
        # evidence but does contain target-only, reference-only, or async-both evidence.
        st.toggle(
            t["lbl_include_unpaired_evidence"],
            key=toggle_key,
            on_change=inspector_selection.sync_boolean_widget_state,
            args=(session_state, toggle_key, inspector_selection.RESULTS_SHOW_NON_JOINT_STATE_KEY),
        )
        show_non_joint = inspector_selection.sync_boolean_widget_state(
            session_state,
            toggle_key,
            inspector_selection.RESULTS_SHOW_NON_JOINT_STATE_KEY,
        )

    # --- DYNAMIC EXCEL-STYLE FILTER ---
    # sorted_disp_df is ready, so render the filter button in column 3.
    with col_ins3:
        # Subtle native Material Design filter button.
        with st.popover(
            t["lbl_filter"],
            icon=":material/filter_alt:",
            width="stretch",
        ):
            st.markdown(f"**{t['lbl_filter_columns']}**")
            filter_cols = st.multiselect(
                t["lbl_select_columns"],
                sorted_disp_df.columns,
                label_visibility="collapsed",
            )

            for col in filter_cols:
                if pd.api.types.is_numeric_dtype(sorted_disp_df[col]):
                    min_val = float(sorted_disp_df[col].min())
                    max_val = float(sorted_disp_df[col].max())
                    if min_val < max_val:
                        step = 1.0 if pd.api.types.is_integer_dtype(sorted_disp_df[col]) else 0.1
                        sel_range = st.slider(f"{col}", min_val, max_val, (min_val, max_val), step=step)
                        sorted_disp_df = sorted_disp_df[(sorted_disp_df[col] >= sel_range[0]) & (sorted_disp_df[col] <= sel_range[1])]
                else:
                    unique_vals = sorted_disp_df[col].dropna().unique()
                    sel_vals = st.multiselect(f"{col}", unique_vals, default=[])
                    if sel_vals:
                        sorted_disp_df = sorted_disp_df[sorted_disp_df[col].isin(sel_vals)]

    # --- END FILTER ---

    station_insights_display_df = sorted_disp_df
    if is_outlier_reporting_enabled:
        focused_station_identities = (
            inspector_selection.focused_station_identities_for_scope(
                session_state,
                analysis_id=analysis_id,
                run_id=run_id,
                scope_token=scope_token,
            )
        )
        station_insights_display_df = (
            prioritize_focused_station_identities(
                sorted_disp_df,
                station_col,
                t['tbl_col_loc'],
                focused_station_identities,
            )
        )

    with level_three_container:
        render_reference_correction_notice(
            t,
            is_compare=True,
            is_sequential=is_sequential,
            analysis_context=analysis_context,
        )

    # Die Tabelle rendert nun den gefilterten Zustand
    tbl_key = f"tbl_{analysis_id}_{run_id}_{scope_token}"
    if is_outlier_reporting_enabled:
        selection_revision = inspector_selection.get_station_selection_revision(
            session_state
        )
        tbl_key += f"_multi_selection_{selection_revision}"
    selected_stations_state_key = inspector_selection.selected_stations_persistent_state_key(
        True
    )
    allow_multiple_station_selection = current_selection.is_outlier_reporting_enabled
    configured_station_identities = current_selection
    selection_changed_key = f"{tbl_key}_selection_changed"
    dataframe_kwargs = {
        "width": "stretch",
        "hide_index": True,
        "selection_mode": (
            "multi-row"
            if allow_multiple_station_selection
            else "single-row"
        ),
        "on_select": partial(
            inspector_selection.mark_station_selection_changed,
            session_state,
            selection_changed_key,
        ),
        "key": tbl_key,
        "column_config": snr_column_config(
            station_insights_display_df
        ),
    }
    selection_default_rows, missing_station_identities = (
        inspector_selection.station_selection_default_rows(
            station_insights_display_df,
            station_col,
            t['tbl_col_loc'],
            configured_station_identities,
            allow_multiple=allow_multiple_station_selection,
        )
    )
    with level_three_container:
        warn_missing_station_identities(missing_station_identities, t)
    if supports_dataframe_selection_default():
        dataframe_kwargs["selection_default"] = {
            "selection": {"rows": selection_default_rows}
        }
    with timed_span(timing_collector, "station insights table render"):
        tbl_event = render_compact_dataframe(
            level_three_container,
            station_insights_display_df,
            **dataframe_kwargs,
        )


    # ----------------------------------------------------
    # Render Raw Drill-Down Data (if user clicks a row)
    # ----------------------------------------------------
    # Streamlit selection remains user-driven after saved identities establish
    # the first render; deliberate deselection is persisted as an empty list.
    raw_sel_rows = tbl_event.selection.rows or []
    sel_rows = [
        row
        for row in raw_sel_rows
        if 0 <= row < len(station_insights_display_df)
    ]
    if not allow_multiple_station_selection:
        sel_rows = sel_rows[:1]
    inspector_selection.sync_selected_station_state_if_changed(
        session_state,
        selection_changed_key,
        selected_stations_state_key,
        station_insights_display_df,
        sel_rows,
        station_col,
        t['tbl_col_loc'],
        allow_multiple=allow_multiple_station_selection,
    )
    selected_station_table = station_insights_display_df
    selected_rows_for_evidence = sel_rows
    if allow_multiple_station_selection:
        # A report selection remains exact even when a local Station
        # Insights filter currently hides one of its station identities.
        selected_station_table = full_segment_disp_df
        updated_selection = inspector_selection.read_inspector_selection(
            session_state,
            run_id=run_id,
            analysis_id=analysis_id,
            scope_token=scope_token,
            is_compare=True,
            selected_ranges=scope.selected_ranges,
            selected_directions=scope.selected_directions,
            is_outlier_reporting_enabled=is_outlier_reporting_enabled,
        )
        selected_rows_for_evidence, _missing_from_active_scope = (
            inspector_selection.station_selection_default_rows(
                selected_station_table,
                station_col,
                t['tbl_col_loc'],
                updated_selection,
                allow_multiple=True,
            )
        )

    return StationInsightsView(
        displayed_table=station_insights_display_df,
        export_station_table=sorted_disp_df,
        full_station_table=full_segment_disp_df,
        selected_station_table=selected_station_table,
        selected_rows=tuple(selected_rows_for_evidence),
        station_column=station_col,
        locator_column=t["tbl_col_loc"],
        distance_column=t["tbl_col_km"],
        azimuth_column=t["tbl_col_az"],
        show_non_joint=show_non_joint,
        level_three_container=level_three_container,
    )
