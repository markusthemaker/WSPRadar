"""Session adapters for canonical Inspector selections and navigation state.

This module never reads Streamlit globals. Callers supply the session mapping;
scientific focus helpers and Pandas load only when an active focus needs them.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from numbers import Integral
from typing import Any

from config import SEGMENT_SELECTION_ALL
from ui.inspector.selection import (
    InspectorSelection,
    StationIdentity,
    parse_station_identities,
    station_identity_records,
)

RESULTS_SHOW_NON_JOINT_STATE_KEY = "val_results_show_non_joint"
RESULTS_SHOW_ZERO_TARGET_STATE_KEY = "val_results_show_zero_target"
RESULTS_SELECTED_RANGES_COMPARE_STATE_KEY = "val_results_selected_ranges_compare"
RESULTS_SELECTED_DIRECTIONS_COMPARE_STATE_KEY = "val_results_selected_directions_compare"
RESULTS_SELECTED_RANGES_ABSOLUTE_STATE_KEY = "val_results_selected_ranges_absolute"
RESULTS_SELECTED_DIRECTIONS_ABSOLUTE_STATE_KEY = "val_results_selected_directions_absolute"
RESULTS_TIME_BIN_COMPARE_STATE_KEY = "val_results_time_bin_compare"
RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY = "val_results_time_bin_absolute"
RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY = "val_results_segment_time_bin_compare"
RESULTS_SEGMENT_TIME_BIN_ABSOLUTE_STATE_KEY = "val_results_segment_time_bin_absolute"
RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY = "val_results_selected_stations_compare"
RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY = "val_results_selected_stations_absolute"
RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY = "results_station_selection_revision_compare"
RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY = "results_station_insights_focus_compare"
RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY = "results_drilldown_focus_compare"
RESULTS_REPORT_DELTA_SNR_OUTLIER_CANDIDATES_STATE_KEY = "val_report_delta_snr_outlier_candidates"


def validate_single_station_identity_records(configured_identities):
    """Validate automatic, deliberately empty, or one exact saved identity."""
    return station_identity_records(parse_station_identities(configured_identities))


def validate_multiple_station_identity_records(configured_identities):
    """Validate UI selections while retaining their historical deduplication."""
    return station_identity_records(
        _parse_unique_ui_station_identities(configured_identities)
    )


def _parse_unique_ui_station_identities(configured_identities):
    """Validate each UI identity once, retaining its first normalized occurrence."""
    if configured_identities is None:
        return None
    if not isinstance(configured_identities, list):
        raise ValueError("Benchmark selected-station state must be null or a list.")
    normalized_identities = []
    seen_identity_pairs = set()
    for configured_identity in configured_identities:
        station_identity = parse_station_identities([configured_identity])[0]
        if station_identity.pair in seen_identity_pairs:
            continue
        seen_identity_pairs.add(station_identity.pair)
        normalized_identities.append(station_identity)
    return tuple(normalized_identities)



def time_bin_persistent_state_key(is_compare):
    """Return the canonical saved-config state key for one evidence view."""
    return (
        RESULTS_TIME_BIN_COMPARE_STATE_KEY
        if is_compare
        else RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY
    )


def selected_stations_persistent_state_key(is_compare):
    """Return the canonical selected-station state key for one result type."""
    return (
        RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY
        if is_compare
        else RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY
    )


def segment_scope_persistent_state_keys(is_compare):
    """Return canonical range and direction keys for Benchmark or Performance."""
    if is_compare:
        return (
            RESULTS_SELECTED_RANGES_COMPARE_STATE_KEY,
            RESULTS_SELECTED_DIRECTIONS_COMPARE_STATE_KEY,
        )
    return (
        RESULTS_SELECTED_RANGES_ABSOLUTE_STATE_KEY,
        RESULTS_SELECTED_DIRECTIONS_ABSOLUTE_STATE_KEY,
    )


def validated_time_bin(options, preferred, fallback):
    """Return a supported bin, preferring the configured deterministic fallback."""
    available_options = tuple(options)
    if not available_options:
        raise ValueError("At least one evidence time-bin option is required.")
    if preferred in available_options:
        return preferred
    if fallback in available_options:
        return fallback
    return available_options[0]


def initialize_time_bin_widget_state(session_state, widget_key, persistent_key, options, fallback):
    """Initialize a transient widget from its validated canonical saved value."""
    selected_time_bin = validated_time_bin(
        options,
        session_state.get(persistent_key),
        fallback,
    )
    session_state[persistent_key] = selected_time_bin
    session_state[widget_key] = selected_time_bin
    return selected_time_bin


def sync_time_bin_widget_state(session_state, widget_key, persistent_key, options, fallback):
    """Copy one widget selection into canonical state after option validation."""
    selected_time_bin = validated_time_bin(
        options,
        session_state.get(widget_key),
        fallback,
    )
    session_state[persistent_key] = selected_time_bin
    return selected_time_bin


def initialize_boolean_widget_state(session_state, widget_key, persistent_key, fallback):
    """Initialize a transient toggle from a canonical boolean saved-config value."""
    persistent_value = session_state.get(persistent_key)
    selected_value = (
        persistent_value
        if isinstance(persistent_value, bool)
        else bool(fallback)
    )
    session_state[persistent_key] = selected_value
    session_state[widget_key] = selected_value
    return selected_value


def sync_boolean_widget_state(session_state, widget_key, persistent_key):
    """Copy one toggle value into canonical saved-config state."""
    selected_value = bool(session_state.get(widget_key, False))
    session_state[persistent_key] = selected_value
    return selected_value


def station_identity_record(callsign, locator):
    """Return one stable station identity record, or ``None`` for blank values."""
    if callsign is None or locator is None:
        return None
    callsign_text = str(callsign).strip().upper()
    locator_text = str(locator).strip().upper()
    if not callsign_text or not locator_text:
        return None
    return {"callsign": callsign_text, "locator": locator_text}


def station_selection_for_outlier_reporting_mode(
    configured_identities,
    *,
    is_outlier_reporting_enabled,
):
    """Restore the historical singleton selection when the opt-in is off."""
    if (
        is_outlier_reporting_enabled
        or not isinstance(configured_identities, list)
        or len(configured_identities) <= 1
    ):
        return configured_identities
    return configured_identities[:1]


def station_selection_default_rows(
    station_table,
    station_column,
    locator_column,
    configured_identities,
    *,
    allow_multiple=False,
):
    """Resolve saved station identities to current display-row positions.

    A missing explicit identity is reported separately and never causes a
    substitute row to be selected. A ``None`` configuration retains the normal
    first-row default, whereas an empty list resolves to no selected rows.
    """
    has_typed_selection = isinstance(configured_identities, InspectorSelection)
    if has_typed_selection:
        normalized_identities = configured_identities.selected_stations
        if not allow_multiple and normalized_identities and len(normalized_identities) > 1:
            raise ValueError("Selected-station state must contain at most one identity.")
    else:
        normalized_identities = (
            validate_multiple_station_identity_records(configured_identities)
            if allow_multiple
            else validate_single_station_identity_records(configured_identities)
        )
    if normalized_identities is None:
        return ([0] if not station_table.empty else []), []
    if not normalized_identities:
        return [], []

    available_rows = {}
    for row_position, (callsign, locator) in enumerate(
        zip(station_table[station_column], station_table[locator_column])
    ):
        identity_record = station_identity_record(callsign, locator)
        if identity_record is None:
            continue
        identity_pair = (
            identity_record["callsign"],
            identity_record["locator"],
        )
        available_rows.setdefault(identity_pair, row_position)

    selected_rows = []
    missing_identities = []
    for identity_record in normalized_identities:
        identity_pair = identity_record.pair if has_typed_selection else (
            identity_record["callsign"],
            identity_record["locator"],
        )
        row_position = available_rows.get(identity_pair)
        if row_position is None:
            missing_identities.append(
                identity_record.to_dict() if has_typed_selection else identity_record
            )
        else:
            selected_rows.append(row_position)
    return selected_rows, missing_identities


def focused_station_identities_for_scope(
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
):
    """Return one report-driven table focus only in its originating scope."""
    focus_record = session_state.get(
        RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY
    )
    if not isinstance(focus_record, dict):
        return None
    expected_scope = {
        "analysis_id": analysis_id,
        "run_id": run_id,
        "scope_token": scope_token,
    }
    if any(
        focus_record.get(field_name) != expected_value
        for field_name, expected_value in expected_scope.items()
    ):
        return None
    station_identities = focus_record.get("station_identities")
    if not isinstance(station_identities, list):
        return None
    return station_identities


def station_identity_records_for_rows(
    station_table,
    selected_rows,
    station_column,
    locator_column,
    *,
    allow_multiple=False,
):
    """Return ordered exact identities for valid selected station rows."""
    valid_rows = [
        row_position
        for row_position in selected_rows
        if isinstance(row_position, Integral)
        and 0 <= row_position < len(station_table)
    ]
    if not allow_multiple and len(valid_rows) > 1:
        raise ValueError("Station selection must contain at most one row.")
    if not valid_rows:
        return []

    selected_identity_records = []
    for row_position in valid_rows:
        row = station_table.iloc[row_position]
        identity_record = station_identity_record(
            row[station_column],
            row[locator_column],
        )
        if identity_record is None:
            raise ValueError(
                "Selected station row must contain a callsign and locator."
            )
        selected_identity_records.append(identity_record)
    if allow_multiple:
        return validate_multiple_station_identity_records(
            selected_identity_records
        )
    return validate_single_station_identity_records(
        selected_identity_records
    )


def sync_selected_station_state(
    session_state,
    persistent_key,
    station_table,
    selected_rows,
    station_column,
    locator_column,
    *,
    allow_multiple=False,
):
    """Persist an explicit empty, single, or Benchmark multi-selection."""
    selected_identities = station_identity_records_for_rows(
        station_table,
        selected_rows,
        station_column,
        locator_column,
        allow_multiple=allow_multiple,
    )
    session_state[persistent_key] = selected_identities
    return selected_identities


def mark_station_selection_changed(session_state, selection_changed_key):
    """Record that a user, rather than a table default, changed selection."""
    session_state[selection_changed_key] = True
    clear_inspector_focus(session_state)


def sync_selected_station_state_if_changed(
    session_state,
    selection_changed_key,
    persistent_key,
    station_table,
    selected_rows,
    station_column,
    locator_column,
    *,
    allow_multiple=False,
):
    """Persist visible rows only after a user-generated selection event.

    Applying a saved default, changing transient segment scope, or rendering a
    table that does not contain every saved identity must not rewrite the
    canonical config state. A real selection event replaces it exactly,
    including a deliberate empty selection.
    """
    if not session_state.pop(selection_changed_key, False):
        return session_state.get(persistent_key)
    return sync_selected_station_state(
        session_state,
        persistent_key,
        station_table,
        selected_rows,
        station_column,
        locator_column,
        allow_multiple=allow_multiple,
    )


def resolve_explicit_all_selection(current, previous, all_option, specific_options):
    """Normalize one multiselect where All is explicit and mutually exclusive."""
    allowed_specific = set(specific_options)
    current = [
        value for value in (current or [])
        if value == all_option or value in allowed_specific
    ]
    previous = [
        value for value in (previous or [])
        if value == all_option or value in allowed_specific
    ]
    specifics = [value for value in current if value != all_option]

    if all_option in current and specifics:
        return specifics if all_option in previous else [all_option]
    if specifics:
        return specifics
    return [all_option]


def initialize_explicit_all_multiselect(
    session_state,
    key,
    previous_key,
    all_option,
    specific_options,
    persistent_key=None,
):
    """Initialize a scope widget from canonical saved state for a new run."""
    if key in session_state:
        current = session_state[key]
    else:
        persisted_selection = session_state.get(
            persistent_key,
            SEGMENT_SELECTION_ALL,
        )
        if persisted_selection == SEGMENT_SELECTION_ALL:
            current = [all_option]
        elif isinstance(persisted_selection, (list, tuple)):
            persisted_values = set(persisted_selection)
            if persisted_values and persisted_values.issubset(specific_options):
                current = [
                    option
                    for option in specific_options
                    if option in persisted_values
                ]
            else:
                current = [all_option]
                if persistent_key is not None:
                    session_state[persistent_key] = SEGMENT_SELECTION_ALL
        else:
            current = [all_option]
            if persistent_key is not None:
                session_state[persistent_key] = SEGMENT_SELECTION_ALL
    if isinstance(current, str):
        current = [current]
    previous = session_state.get(previous_key, [all_option])
    if isinstance(previous, str):
        previous = [previous]
    normalized = resolve_explicit_all_selection(current, previous, all_option, specific_options)
    session_state[key] = normalized
    session_state[previous_key] = normalized


def update_explicit_all_multiselect(
    session_state,
    key,
    previous_key,
    all_option,
    specific_options,
    persistent_key=None,
):
    """Apply explicit-All behavior and persist a user-generated scope change."""
    current = session_state.get(key, [])
    previous = session_state.get(previous_key, [all_option])
    normalized = resolve_explicit_all_selection(current, previous, all_option, specific_options)
    session_state[key] = normalized
    session_state[previous_key] = normalized
    if persistent_key is not None:
        session_state[persistent_key] = (
            SEGMENT_SELECTION_ALL
            if normalized == [all_option]
            else [option for option in specific_options if option in normalized]
        )


def canonical_specific_selection(selection, all_option, ordered_options):
    """Return selected specific options in their canonical UI order."""
    if all_option in selection:
        return ()
    selected = set(selection)
    return tuple(option for option in ordered_options if option in selected)


def drilldown_outlier_context_for_scope(
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
    selected_identity,
    analysis_start_utc,
    analysis_end_utc,
):
    """Return validated candidate provenance belonging to this run and path."""
    from ui.inspector.drilldown_focus import drilldown_outlier_candidate_context_for_scope

    return drilldown_outlier_candidate_context_for_scope(
        session_state.get(RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY),
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
        selected_identity=selected_identity,
        analysis_start_utc=analysis_start_utc,
        analysis_end_utc=analysis_end_utc,
    )


def drilldown_focus_identity_token(selected_identity):
    """Return a stable compact widget namespace for one selected station."""
    callsign, locator = selected_identity
    return sha256(
        f"{str(callsign).strip().upper()}\0{str(locator).strip().upper()}".encode(
            "utf-8"
        )
    ).hexdigest()[:12]


@dataclass(frozen=True)
class DrilldownZoomStateKeys:
    """Transient Drill-Down control keys for one run, scope, and station."""

    widget_scope: str
    zoom_widget: str
    focus_date_widget: str
    focus_time_widget: str
    applied_outlier_request: str
    applied_option: str


def drilldown_zoom_state_keys(
    analysis_id,
    run_id,
    scope_token,
    selected_identity,
):
    """Return the complete dynamic key namespace for Drill-Down zoom state."""
    identity_token = drilldown_focus_identity_token(selected_identity)
    widget_scope = f"{analysis_id}_{run_id}_{scope_token}_{identity_token}"
    zoom_widget = f"d_zoom_{widget_scope}"
    return DrilldownZoomStateKeys(
        widget_scope=widget_scope,
        zoom_widget=zoom_widget,
        focus_date_widget=f"d_zoom_focus_date_{widget_scope}",
        focus_time_widget=f"d_zoom_focus_time_{widget_scope}",
        applied_outlier_request=(
            f"{zoom_widget}_applied_outlier_request"
        ),
        applied_option=f"{zoom_widget}_applied_option",
    )


def drilldown_focus_center_from_widget_values(date_value, time_value):
    """Combine direct calendar/time inputs into one timezone-aware UTC center."""
    import pandas as pd

    return pd.Timestamp(
        datetime.combine(
            date_value,
            time_value.replace(tzinfo=None),
            tzinfo=timezone.utc,
        )
    )


def store_drilldown_focus_center(
    session_state,
    *,
    date_key,
    time_key,
    focus_center,
):
    """Write one UTC center into the date/time widget value types."""
    import pandas as pd

    normalized_center = pd.Timestamp(focus_center).tz_convert("UTC")
    session_state[date_key] = normalized_center.date()
    session_state[time_key] = normalized_center.time().replace(tzinfo=None)


def normalize_drilldown_focus_center_state(
    session_state,
    date_key,
    time_key,
    analysis_start_utc,
    analysis_end_utc,
    option,
):
    """Clamp direct widget values while preserving the chosen full duration."""
    from ui.inspector.drilldown_focus import (
        default_focus_center_utc, focus_center_utc, resolve_centered_zoom_window,
    )

    try:
        requested_center = drilldown_focus_center_from_widget_values(
            session_state[date_key],
            session_state[time_key],
        )
        focus_window = resolve_centered_zoom_window(
            analysis_start_utc,
            analysis_end_utc,
            option,
            requested_center,
        )
    except (KeyError, TypeError, ValueError, OverflowError):
        requested_center = default_focus_center_utc(
            analysis_start_utc,
            analysis_end_utc,
            option,
        )
        focus_window = resolve_centered_zoom_window(
            analysis_start_utc,
            analysis_end_utc,
            option,
            requested_center,
        )
    if focus_window is None:
        return
    store_drilldown_focus_center(
        session_state,
        date_key=date_key,
        time_key=time_key,
        focus_center=focus_center_utc(focus_window),
    )


def shift_drilldown_focus_center_state(
    session_state,
    date_key,
    time_key,
    analysis_start_utc,
    analysis_end_utc,
    option,
    direction,
):
    """Move a manual focus center by one complete selected zoom window."""
    import pandas as pd

    from ui.inspector.drilldown_focus import (
        DRILLDOWN_ZOOM_DURATION_HOURS, focus_center_utc, resolve_centered_zoom_window,
    )

    normalize_drilldown_focus_center_state(
        session_state,
        date_key,
        time_key,
        analysis_start_utc,
        analysis_end_utc,
        option,
    )
    current_center = drilldown_focus_center_from_widget_values(
        session_state[date_key],
        session_state[time_key],
    )
    shifted_center = current_center + int(direction) * pd.Timedelta(
        hours=DRILLDOWN_ZOOM_DURATION_HOURS[option]
    )
    focus_window = resolve_centered_zoom_window(
        analysis_start_utc,
        analysis_end_utc,
        option,
        shifted_center,
    )
    if focus_window is None:
        return
    store_drilldown_focus_center(
        session_state,
        date_key=date_key,
        time_key=time_key,
        focus_center=focus_center_utc(focus_window),
    )


def select_outlier_station_identities(
    station_identities,
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
    navigation_anchor_id=None,
    preserve_drilldown_focus=False,
):
    """Select, focus, and navigate to exact detector path identities."""
    if "run_id" in session_state and session_state["run_id"] != run_id:
        return None
    normalized_identities = _parse_unique_ui_station_identities([
        {"callsign": station_identity.callsign, "locator": station_identity.locator}
        for station_identity in station_identities
    ])
    return _publish_outlier_station_selection(
        normalized_identities,
        session_state,
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
        navigation_anchor_id=navigation_anchor_id,
        preserve_drilldown_focus=preserve_drilldown_focus,
    )


def _publish_outlier_station_selection(
    normalized_identities: tuple[StationIdentity, ...],
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
    navigation_anchor_id,
    preserve_drilldown_focus,
):
    """Publish one already validated action without repeating identity parsing."""
    from ui.page_navigation import STATION_INSIGHTS_ANCHOR_ID, request_page_navigation

    if navigation_anchor_id is None:
        navigation_anchor_id = STATION_INSIGHTS_ANCHOR_ID
    selected_identities = station_identity_records(normalized_identities)
    session_state[
        RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY
    ] = selected_identities
    if not preserve_drilldown_focus:
        session_state.pop(
            RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY,
            None,
        )
    session_state[
        RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY
    ] = get_station_selection_revision(session_state) + 1
    session_state[
        RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY
    ] = {
        "analysis_id": analysis_id,
        "run_id": run_id,
        "scope_token": scope_token,
        "station_identities": selected_identities,
    }
    request_page_navigation(
        session_state,
        navigation_anchor_id,
        should_scroll=True,
    )
    return selected_identities


def select_outlier_path(
    station_identity,
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
):
    """Show exactly one qualifying detector path in Station Insights."""
    return select_outlier_station_identities(
        (station_identity,),
        session_state,
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
    )


def select_outlier_candidate(
    candidate,
    outlier_model,
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
    navigation_anchor_id,
):
    """Preload one exact Outlier Focus and navigate to its selected path."""
    if "run_id" in session_state and session_state["run_id"] != run_id:
        return None
    normalized_identities = _parse_unique_ui_station_identities([
        {"callsign": candidate.station_identity.callsign,
         "locator": candidate.station_identity.locator},
    ])
    selected_identity = normalized_identities[0]
    from ui.inspector.drilldown_focus import DRILLDOWN_OUTLIER_CONTEXT_SCHEMA_VERSION
    from ui.inspector.outlier_candidates import build_delta_snr_outlier_context_bounds

    context_bounds = build_delta_snr_outlier_context_bounds(
        candidate,
        analysis_start_utc=outlier_model.analysis_start_utc,
        analysis_end_utc=outlier_model.analysis_end_utc,
    )
    request_payload = {
        "schema_version": DRILLDOWN_OUTLIER_CONTEXT_SCHEMA_VERSION,
        "analysis_id": analysis_id,
        "run_id": run_id,
        "scope_token": scope_token,
        "callsign": selected_identity.callsign,
        "locator": selected_identity.locator,
        "event_start_utc_ns": int(candidate.start_utc.value),
        "event_end_utc_ns": int(candidate.end_utc.value),
        "representative_utc_ns": int(candidate.representative_utc.value),
        "representative_delta_snr_db": float(
            candidate.representative_delta_snr_db
        ),
        "local_baseline_db": float(candidate.station_baseline_db),
        "pre_baseline_db": float(candidate.pre_baseline_db),
        "post_baseline_db": float(candidate.post_baseline_db),
        "robust_spread_db": float(candidate.robust_spread_db),
        "robust_spread_method": candidate.robust_spread_method,
        "robust_z": float(candidate.robust_z),
        "minimum_robust_z": float(
            outlier_model.detection_policy.minimum_robust_z
        ),
        "minimum_departure_db": float(
            outlier_model.detection_policy.minimum_departure_db
        ),
        "baseline_anchor_start_utc_ns": int(
            candidate.baseline_anchor_start_utc.value
        ),
        "baseline_anchor_end_utc_ns": int(
            candidate.baseline_anchor_end_utc.value
        ),
        "episode_guard_minutes": float(candidate.episode_guard_minutes),
        "pre_flank_start_utc_ns": int(
            context_bounds.pre_flank_start_utc.value
        ),
        "pre_flank_end_utc_ns": int(
            context_bounds.pre_flank_end_utc.value
        ),
        "post_flank_start_utc_ns": int(
            context_bounds.post_flank_start_utc.value
        ),
        "post_flank_end_utc_ns": int(
            context_bounds.post_flank_end_utc.value
        ),
        "detector_version": outlier_model.detector_version,
        "candidate_signature": outlier_model.candidate_signature,
    }
    request_payload["request_token"] = sha256(
        json.dumps(
            request_payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    zoom_state_keys = drilldown_zoom_state_keys(
        analysis_id,
        run_id,
        scope_token,
        selected_identity.pair,
    )
    session_state.pop(zoom_state_keys.applied_outlier_request, None)
    session_state[RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY] = request_payload
    return _publish_outlier_station_selection(
        normalized_identities,
        session_state,
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
        navigation_anchor_id=navigation_anchor_id,
        preserve_drilldown_focus=True,
    )


def select_outlier_episode_paths(
    report_entry,
    session_state,
    *,
    analysis_id,
    run_id,
    scope_token,
):
    """Show all unique qualifying paths from one event in Station Insights."""
    return select_outlier_station_identities(
        report_entry.station_identities,
        session_state,
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
    )


_INSPECTOR_SELECTION_DEFAULTS = {
    RESULTS_SHOW_NON_JOINT_STATE_KEY: None,
    RESULTS_SHOW_ZERO_TARGET_STATE_KEY: False,
    RESULTS_SELECTED_RANGES_COMPARE_STATE_KEY: SEGMENT_SELECTION_ALL,
    RESULTS_SELECTED_DIRECTIONS_COMPARE_STATE_KEY: SEGMENT_SELECTION_ALL,
    RESULTS_SELECTED_RANGES_ABSOLUTE_STATE_KEY: SEGMENT_SELECTION_ALL,
    RESULTS_SELECTED_DIRECTIONS_ABSOLUTE_STATE_KEY: SEGMENT_SELECTION_ALL,
    RESULTS_TIME_BIN_COMPARE_STATE_KEY: None,
    RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY: None,
    RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY: "auto",
    RESULTS_SEGMENT_TIME_BIN_ABSOLUTE_STATE_KEY: "auto",
    RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY: None,
    RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY: None,
}


def seed_inspector_selection_state(
    session_state: MutableMapping[str, Any],
    values: Mapping[str, Any] | None = None,
    *,
    overwrite: bool = False,
) -> None:
    """Initialize missing values or apply explicitly validated loaded settings.

    With no supplied values, use the established startup/factory defaults.
    Supplied values are already validated by the configuration boundary; only
    this adapter's known durable selection fields may be written here.
    """
    selection_values = _INSPECTOR_SELECTION_DEFAULTS if values is None else values
    unknown_keys = selection_values.keys() - _INSPECTOR_SELECTION_DEFAULTS.keys()
    if unknown_keys:
        raise ValueError(f"Unknown Inspector selection fields: {sorted(unknown_keys)}")
    for state_key, selection_value in selection_values.items():
        if overwrite or state_key not in session_state:
            session_state[state_key] = selection_value


def clear_inspector_focus(session_state: MutableMapping[str, Any]) -> None:
    """Release both transient report/navigation focus records in bounded work."""
    session_state.pop(RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY, None)
    session_state.pop(RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY, None)


def release_selected_station_state(session_state: MutableMapping[str, Any]) -> None:
    """Release exact station intent when its completed evidence is retired."""
    session_state[RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY] = None
    session_state[RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY] = None


def get_station_selection_revision(session_state: Mapping[str, Any]) -> int:
    """Read a valid report-driven table revision without rewriting session state."""
    selection_revision = session_state.get(
        RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY, 0,
    )
    if isinstance(selection_revision, bool) or not isinstance(selection_revision, Integral):
        return 0
    return int(selection_revision)


def resolve_configured_station_selection_for_reporting(
    session_state: MutableMapping[str, Any],
    *,
    is_outlier_reporting_enabled: bool,
):
    """Retain configured intent while restoring the historical opt-out singleton."""
    configured_identities = session_state.get(RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY)
    mode_appropriate_identities = station_selection_for_outlier_reporting_mode(
        configured_identities,
        is_outlier_reporting_enabled=is_outlier_reporting_enabled,
    )
    if mode_appropriate_identities is not configured_identities:
        session_state[RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY] = mode_appropriate_identities
    return mode_appropriate_identities


def normalize_compare_station_selection_for_outlier_reporting(
    session_state: MutableMapping[str, Any],
) -> bool:
    """Restore the opt-out singleton and clear transient report focus."""
    if session_state.get(RESULTS_REPORT_DELTA_SNR_OUTLIER_CANDIDATES_STATE_KEY, False) is True:
        return False
    clear_inspector_focus(session_state)
    configured_identities = session_state.get(RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY)
    normalized_identities = resolve_configured_station_selection_for_reporting(
        session_state,
        is_outlier_reporting_enabled=False,
    )
    return normalized_identities is not configured_identities


def read_inspector_selection(
    session_state: Mapping[str, Any],
    *,
    run_id: int,
    analysis_id: str,
    scope_token: str,
    is_compare: bool,
    selected_ranges,
    selected_directions,
    is_outlier_reporting_enabled: bool = False,
) -> InspectorSelection:
    """Read one compact typed selection for the currently resolved visible scope."""
    station_records = session_state.get(selected_stations_persistent_state_key(is_compare))
    selected_stations = parse_station_identities(
        station_records,
        maximum_count=None if is_compare and is_outlier_reporting_enabled else 1,
    )
    return InspectorSelection(
        run_id=run_id,
        analysis_id=analysis_id,
        scope_token=scope_token,
        is_compare=is_compare,
        is_outlier_reporting_enabled=is_outlier_reporting_enabled,
        selected_ranges=tuple(selected_ranges) or None,
        selected_directions=tuple(selected_directions) or None,
        selected_stations=selected_stations,
        segment_time_bin=session_state.get(
            RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY if is_compare
            else RESULTS_SEGMENT_TIME_BIN_ABSOLUTE_STATE_KEY,
            "auto",
        ),
        station_time_bin=session_state.get(time_bin_persistent_state_key(is_compare)),
    )


@dataclass(frozen=True)
class DrilldownControls:
    """Prepared control state; candidate provenance remains a separate record."""

    keys: DrilldownZoomStateKeys
    available_options: tuple[str, ...]
    outlier_context: Any


def prepare_drilldown_controls(
    session_state: MutableMapping[str, Any],
    *,
    analysis_id,
    run_id,
    scope_token,
    selected_identity,
    analysis_start_utc,
    analysis_end_utc,
) -> DrilldownControls:
    """Validate retained provenance and initialize this path's stable zoom keys."""
    from ui.inspector.drilldown_focus import (
        DRILLDOWN_OUTLIER_FOCUS_OPTION,
        available_manual_zoom_options,
    )

    manual_options = available_manual_zoom_options(analysis_start_utc, analysis_end_utc)
    outlier_context = drilldown_outlier_context_for_scope(
        session_state,
        analysis_id=analysis_id,
        run_id=run_id,
        scope_token=scope_token,
        selected_identity=selected_identity,
        analysis_start_utc=analysis_start_utc,
        analysis_end_utc=analysis_end_utc,
    )
    if session_state.get(RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY) is not None and outlier_context is None:
        session_state.pop(RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY, None)
    available_options = tuple(manual_options) if outlier_context is None else (
        "off", DRILLDOWN_OUTLIER_FOCUS_OPTION,
        *(option for option in manual_options if option != "off"),
    )
    zoom_keys = drilldown_zoom_state_keys(analysis_id, run_id, scope_token, selected_identity)
    if outlier_context is not None and (
        session_state.get(zoom_keys.applied_outlier_request) != outlier_context.request_token
        or zoom_keys.zoom_widget not in session_state
    ):
        session_state[zoom_keys.zoom_widget] = DRILLDOWN_OUTLIER_FOCUS_OPTION
        session_state[zoom_keys.applied_outlier_request] = outlier_context.request_token
        store_drilldown_focus_center(
            session_state,
            date_key=zoom_keys.focus_date_widget,
            time_key=zoom_keys.focus_time_widget,
            focus_center=outlier_context.representative_utc,
        )
    if session_state.get(zoom_keys.zoom_widget) not in available_options:
        session_state[zoom_keys.zoom_widget] = "off"
    return DrilldownControls(zoom_keys, available_options, outlier_context)


def prepare_manual_focus_center(
    session_state: MutableMapping[str, Any],
    *,
    zoom_keys: DrilldownZoomStateKeys,
    selected_option: str,
    outlier_context,
    analysis_start_utc,
    analysis_end_utc,
):
    """Initialize and clamp manual center widgets, returning their UTC bounds."""
    from ui.inspector.drilldown_focus import (
        DRILLDOWN_OUTLIER_FOCUS_OPTION,
        default_focus_center_utc,
        manual_zoom_center_bounds,
    )

    prior_option = session_state.get(zoom_keys.applied_option)
    if (
        zoom_keys.focus_date_widget not in session_state
        or zoom_keys.focus_time_widget not in session_state
        or (prior_option == DRILLDOWN_OUTLIER_FOCUS_OPTION and outlier_context is not None)
    ):
        initial_center = outlier_context.representative_utc if outlier_context is not None else default_focus_center_utc(
            analysis_start_utc, analysis_end_utc, selected_option,
        )
        store_drilldown_focus_center(
            session_state,
            date_key=zoom_keys.focus_date_widget,
            time_key=zoom_keys.focus_time_widget,
            focus_center=initial_center,
        )
    normalize_drilldown_focus_center_state(
        session_state,
        zoom_keys.focus_date_widget,
        zoom_keys.focus_time_widget,
        analysis_start_utc,
        analysis_end_utc,
        selected_option,
    )
    return manual_zoom_center_bounds(analysis_start_utc, analysis_end_utc, selected_option)


def finish_drilldown_option(
    session_state: MutableMapping[str, Any],
    zoom_keys: DrilldownZoomStateKeys,
    selected_option: str,
) -> None:
    """Commit the displayed option; Off releases its prior candidate request."""
    if selected_option == "off":
        session_state.pop(RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY, None)
        session_state.pop(zoom_keys.applied_outlier_request, None)
    session_state[zoom_keys.applied_option] = selected_option
