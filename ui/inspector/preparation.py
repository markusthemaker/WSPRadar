"""Run-scoped Inspector preparation, bounded cache access, and artifact reads.

Numeric evidence is prepared only on the original cache-miss or selected-path
branches. Localized compact recipes reuse those temporary references; only the
existing compact bundles are cached, with unchanged dependencies and budgets.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from contextlib import nullcontext
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd

from config import (COMPASS, INSPECTOR_CACHE_MAX_BYTES,
    INSPECTOR_CACHE_OPTIONS_MAX_ENTRIES, INSPECTOR_CACHE_PNG_MAX_ENTRIES,
    INSPECTOR_CACHE_SEGMENT_MAX_ENTRIES, INSPECTOR_CACHE_SELECTED_MAX_ENTRIES)
from config.delta_snr_outlier import (DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
    DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD, DeltaSnrOutlierDetectionPolicy)
from core.artifact_store import ARTIFACT_STORE, read_parquet_artifact
from core.compare_engine import compare_footer_counts
from core.opportunity_engine import (OPPORTUNITY_DRILLDOWN_VIEW_COLUMNS,
    OPPORTUNITY_SEGMENT_VIEW_COLUMNS, opportunity_utc_from_time_slot)
from core.performance_timer import log_performance_event
from ui.inspector import selection_state as inspector_selection
from ui.inspector.contracts import InspectorContext, InspectorScope, StationInsightsView
from ui.inspector.drilldown import _build_drilldown_table, _load_station_rows_for_drilldown
from ui.inspector.drilldown_focus import (DRILLDOWN_FOCUS_SCHEMA_VERSION,
    filter_station_rows_to_focus_window)
from ui.inspector.evidence_data import (_build_compare_unit_rows,
    _build_segment_compare_units, _compare_joint_evidence_points,
    _prepare_identity_meta, _retain_thresholded_compare_outcomes)
from ui.inspector.outlier_candidates import (DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
    DELTA_SNR_OUTLIER_DETECTOR_VERSION, prepare_delta_snr_outlier_model)
from ui.inspector.outlier_report import build_delta_snr_outlier_report_view_model
from ui.inspector.outlier_export import (build_delta_snr_outlier_export_metadata,
    build_delta_snr_outlier_export_tables)
from ui.inspector.session_cache import SessionInspectorCache
from ui.inspector.view_models import (build_compare_inspector_view_model,
    build_inspector_options, build_opportunity_inspector_view_model,
    filter_inspector_scope)
from ui.plots.evidence_figures import (_segment_figure_export_recipe,
    _segment_temporal_evidence_export_recipe, _selected_evidence_export_recipe,
    _time_agg_options_for_window)
from ui.plots.opportunity_figures import (SUCCESS_DISTANCE_BINNING_VERSION,
    SUCCESS_SNR_BASELINE_VERSION, SUCCESS_SNR_REPRESENTATION_ACTUAL,
    SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE,
    SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
    SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION, _as_utc_timestamp,
    _opportunity_segment_recipe, _opportunity_temporal_recipe)
from ui.plots.benchmark_evidence_figures import _compare_coverage_recipe
from ui.plots.drilldown_zoom_figures import (DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
    build_drilldown_zoom_benchmark_delta_snr_recipe,
    build_drilldown_zoom_outlier_overlay_recipe,
    build_drilldown_zoom_performance_snr_recipe)
from ui.reference_correction import configured_snr_correction_notice
from ui.result_hierarchy import selected_station_label
from ui.result_state import INSPECTOR_CACHE_STATE_KEY
from ui.inspector.presentation import (
    segment_temporal_figure_title,
    success_figure_labels,
    compare_coverage_figure_labels,
    compare_temporal_coverage_title,
    success_temporal_figure_title,
    selected_success_temporal_figure_title,
    folded_utc_hour_panel_title,
    segment_summary_lines,
    format_localized_integer,
    format_localized_decimal,
    format_summary_count,
    compare_metric_distribution_summary,
    selected_evidence_figure_title,
    format_drilldown_focus_utc,
    drilldown_focus_title,
    drilldown_focus_time_bin,
    selected_success_context_line,
)

INSPECTOR_CACHE_VERSION = 48
INSPECTOR_CACHE_NAMESPACE_LIMITS = {
    "options": INSPECTOR_CACHE_OPTIONS_MAX_ENTRIES,
    "segment": INSPECTOR_CACHE_SEGMENT_MAX_ENTRIES,
    "selected": INSPECTOR_CACHE_SELECTED_MAX_ENTRIES,
    "png": INSPECTOR_CACHE_PNG_MAX_ENTRIES,
}


class InspectorArtifactReadError(Exception):
    """A projected artifact read failed before numerical/view preparation."""

    def __init__(self, original_exception):
        super().__init__(str(original_exception))
        self.original_exception = original_exception
        self.is_missing = isinstance(original_exception, FileNotFoundError)


@dataclass(frozen=True, slots=True)
class PreparedScope:
    """Cached compact view data alongside the current, uncached scope rows."""
    cache_key: tuple
    bundle: Mapping[str, Any]
    scope_rows: pd.DataFrame

@dataclass(frozen=True, slots=True)
class PreparedEvidence:
    """Selected evidence recipes and their exact adaptive-bin cache identity."""
    cache_key: tuple
    bundle: Mapping[str, Any]

def _timed_span(timing_collector, label, detail=""):
    """Return a timing context when profiling is active."""
    if timing_collector is None:
        return nullcontext()
    return timing_collector.span(label, detail=detail)

def _log_artifact_read_failure(exc, *, parquet_path, analysis_id, run_id, stage):
    """Record enough context to distinguish lifecycle loss from schema failures."""
    path = Path(parquet_path)
    log_performance_event(
        "session_artifact_read",
        outcome="missing" if isinstance(exc, FileNotFoundError) else "invalid",
        stage=stage,
        analysis_id=analysis_id,
        run_id=run_id,
        artifact=path.name,
        exists=path.is_file(),
        error_type=type(exc).__name__,
    )

def compare_temporal_time_bin_policy(
    analysis_start_t,
    analysis_end_t,
    preferred_time_bin,
):
    """Resolve adaptive bins plus a cache token for one retained extra choice."""
    adaptive_options, adaptive_default = _time_agg_options_for_window(
        analysis_start_t,
        analysis_end_t,
    )
    resolved_options, _resolved_default = _time_agg_options_for_window(
        analysis_start_t,
        analysis_end_t,
        retained_time_bin=preferred_time_bin,
    )
    retained_extra_cache_token = (
        str(preferred_time_bin)
        if (
            preferred_time_bin in resolved_options
            and preferred_time_bin not in adaptive_options
        )
        else None
    )
    return resolved_options, adaptive_default, retained_extra_cache_token

def delta_snr_outlier_segment_cache_suffix(
    is_enabled,
    detection_policy=None,
):
    """Return no cache fields when disabled and detector identity when on."""
    if not is_enabled:
        return ()
    resolved_policy = (
        DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY
        if detection_policy is None
        else detection_policy
    )
    if not isinstance(resolved_policy, DeltaSnrOutlierDetectionPolicy):
        raise TypeError(
            "detection_policy must be a DeltaSnrOutlierDetectionPolicy."
        )
    return (
        "delta-snr-outlier-candidates",
        True,
        DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        resolved_policy.signature_tuple,
    )

def enabled_delta_snr_outlier_detection_policy(session_state):
    """Return the valid enabled policy, pausing on invalid live edits."""
    if session_state.get(
        inspector_selection.RESULTS_REPORT_DELTA_SNR_OUTLIER_CANDIDATES_STATE_KEY,
        False,
    ) is not True:
        return None
    try:
        return DeltaSnrOutlierDetectionPolicy(
            **{
                policy_field: session_state.get(
                    f"val_{config_field}",
                    getattr(
                        DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
                        policy_field,
                    ),
                )
                for config_field, policy_field in (
                    DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
                )
            }
        )
    except ValueError:
        return None

def success_distance_scope_intervals(
    inspector_source_df,
    selected_ranges,
    *,
    max_peer_distance_km,
):
    """Resolve distance intervals before direction filtering for stable bins."""
    if not selected_ranges:
        return ((0.0, float(max_peer_distance_km)),)
    interval_rows = (
        inspector_source_df.loc[
            inspector_source_df["dist_label"].isin(selected_ranges),
            ["dist_label", "r_min", "r_max"],
        ]
        .drop_duplicates(subset=["dist_label"])
        .sort_values(["r_min", "r_max"], kind="stable")
    )
    intervals = tuple(
        (
            float(distance_row.r_min),
            float(distance_row.r_max),
        )
        for distance_row in interval_rows.itertuples(index=False)
    )
    if len(intervals) != len(selected_ranges):
        raise ValueError(
            "Every selected Performance distance range requires stable bounds."
        )
    return intervals

def drilldown_zoom_export_metadata(
    focus_window,
    *,
    selected_identity,
    metric_recipe,
    outlier_context=None,
):
    """Return the strict optional export identity for one focused view."""
    if (
        focus_window is None
        or selected_identity is None
        or not isinstance(metric_recipe, Mapping)
    ):
        return None
    callsign, locator = selected_identity
    metadata = {
        "schema_version": DRILLDOWN_FOCUS_SCHEMA_VERSION,
        "station": {
            "callsign": str(callsign).strip().upper(),
            "locator": str(locator).strip().upper(),
        },
        "start_utc": focus_window.start_utc.isoformat(),
        "end_utc": focus_window.end_utc.isoformat(),
        "option": focus_window.option,
        "origin": focus_window.origin,
        "time_bin": str(metric_recipe.get("time_bin") or ""),
        "resolution": str(metric_recipe.get("resolution") or ""),
        "aggregation": str(metric_recipe.get("aggregation") or ""),
        "layout_version": DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
    }
    if outlier_context is not None:
        metadata["outlier_candidate"] = {
            "request_token": outlier_context.request_token,
            "detector_version": outlier_context.detector_version,
            "candidate_signature": outlier_context.candidate_signature,
            "representative_utc": (
                outlier_context.representative_utc.isoformat()
            ),
            "representative_delta_snr_db": (
                outlier_context.representative_delta_snr_db
            ),
            "event_start_utc": outlier_context.event_start_utc.isoformat(),
            "event_end_utc": outlier_context.event_end_utc.isoformat(),
            "pre_flank_start_utc": (
                outlier_context.pre_flank_start_utc.isoformat()
            ),
            "pre_flank_end_utc": (
                outlier_context.pre_flank_end_utc.isoformat()
            ),
            "post_flank_start_utc": (
                outlier_context.post_flank_start_utc.isoformat()
            ),
            "post_flank_end_utc": (
                outlier_context.post_flank_end_utc.isoformat()
            ),
            "local_baseline_db": outlier_context.local_baseline_db,
            "pre_baseline_db": outlier_context.pre_baseline_db,
            "post_baseline_db": outlier_context.post_baseline_db,
            "robust_spread_db": outlier_context.robust_spread_db,
            "robust_spread_method": outlier_context.robust_spread_method,
            "robust_z": outlier_context.robust_z,
            "minimum_robust_z": outlier_context.minimum_robust_z,
            "minimum_departure_db": outlier_context.minimum_departure_db,
        }
    return metadata

def build_performance_drilldown_zoom_recipes(
    selected_base_recipe,
    selected_peer_rows,
    selected_station_rows,
    selected_identity_label,
    focus_window,
    focus_time_bin,
    translations,
):
    """Build native SNR plus cycle-resolution outcome evidence for one path."""
    if focus_window is None or selected_base_recipe is None:
        return None, None
    zoom_title = drilldown_focus_title(
        selected_identity_label,
        focus_window,
        translations,
    )
    native_snr_recipe = build_drilldown_zoom_performance_snr_recipe(
        selected_station_rows,
        start_utc=focus_window.start_utc,
        end_utc=focus_window.end_utc,
        title=zoom_title,
        panel_title=translations[
            "fig_drilldown_native_performance_panel_title"
        ],
        x_label=translations["fig_drilldown_native_time_x"],
        y_label=translations["fig_drilldown_native_performance_y"],
        empty_text=translations[
            "fig_drilldown_native_performance_unavailable"
        ],
        evidence_unit_label=translations[
            "fig_drilldown_native_successful_opportunity"
        ],
    )
    focused_evidence_recipe = _opportunity_temporal_recipe(
        zoom_title,
        selected_base_recipe["selected_segment"],
        selected_peer_rows,
        selected_station_rows,
        focus_window.start_utc,
        focus_window.end_utc,
        selected_base_recipe["terminology"],
        figure_labels=selected_base_recipe["labels"],
        snr_title=zoom_title,
        population_mode=SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
        snr_representation=SUCCESS_SNR_REPRESENTATION_ACTUAL,
        time_bin_options=(focus_time_bin,),
        time_bin_default=focus_time_bin,
    )
    focused_evidence_recipe["time_bin"] = focus_time_bin
    return native_snr_recipe, dict(focused_evidence_recipe)

def build_benchmark_drilldown_zoom_recipes(
    station_df,
    selected_identity_df,
    thresholded_station_rows,
    is_sequential,
    analysis_context,
    focus_window,
    focus_time_bin,
    full_delta_recipe,
    full_coverage_recipe,
    translations,
    outlier_context=None,
    outlier_model=None,
):
    """Build native selected-path Delta-SNR and focused coverage recipes."""
    if (
        focus_window is None
        or full_delta_recipe is None
        or full_coverage_recipe is None
    ):
        return None, None
    identity_meta = _prepare_identity_meta(selected_identity_df)
    if len(identity_meta) != 1:
        return None, None
    comparison_units = _build_compare_unit_rows(
        station_df,
        identity_meta,
        is_sequential,
        paired_identity_df=identity_meta,
        tx_ab_repeat_interval_minutes=(
            analysis_context.tx_ab_repeat_interval_minutes
        ),
        tx_ab_target_start_minute=(
            analysis_context.tx_ab_target_start_minute
        ),
        tx_ab_reference_start_minute=(
            analysis_context.tx_ab_reference_start_minute
        ),
    )
    comparison_units = _retain_thresholded_compare_outcomes(
        comparison_units,
        thresholded_station_rows,
    )
    evidence_utc = pd.to_datetime(
        comparison_units.get("evidence_utc"),
        errors="coerce",
        utc=True,
    )
    comparison_units = comparison_units.loc[
        evidence_utc.notna()
        & evidence_utc.ge(focus_window.start_utc)
        & evidence_utc.lt(focus_window.end_utc)
    ].copy()
    evidence_df = _compare_joint_evidence_points(
        comparison_units,
        preserve_metric_precision=True,
    )
    selected_identity_label = str(identity_meta.iloc[0]["identity"])
    zoom_title = drilldown_focus_title(
        selected_identity_label,
        focus_window,
        translations,
    )
    outlier_overlay = None
    qualifying_marker_recipe_builder = getattr(
        outlier_model,
        "qualifying_unit_marker_recipe",
        None,
    )
    has_current_outlier_model = (
        outlier_context is not None
        and getattr(outlier_model, "detector_version", None)
        == DELTA_SNR_OUTLIER_DETECTOR_VERSION
        and outlier_context.detector_version
        == DELTA_SNR_OUTLIER_DETECTOR_VERSION
        and getattr(outlier_model, "candidate_signature", None)
        == outlier_context.candidate_signature
        and callable(qualifying_marker_recipe_builder)
    )
    if (
        has_current_outlier_model
        and outlier_context.event_start_utc < focus_window.end_utc
        and outlier_context.event_end_utc > focus_window.start_utc
    ):
        qualifying_marker_times_utc = []
        qualifying_marker_delta_snr_db = []
        qualifying_marker_recipe = qualifying_marker_recipe_builder(
            [
                (
                    str(identity_meta.iloc[0]["peer_sign"]),
                    str(identity_meta.iloc[0]["peer_grid"]),
                )
            ],
            start_utc=focus_window.start_utc,
            end_utc=focus_window.end_utc,
        )
        if isinstance(qualifying_marker_recipe, Mapping):
            for marker in qualifying_marker_recipe.get("markers", ()):
                if not isinstance(marker, Mapping):
                    continue
                qualifying_marker_times_utc.append(
                    pd.Timestamp(
                        int(marker["marker_utc_ns"]),
                        unit="ns",
                        tz="UTC",
                    )
                )
                qualifying_marker_delta_snr_db.append(
                    float(marker["marker_delta_snr_db"])
                )

        native_evidence_unit_minutes = (
            analysis_context.tx_ab_repeat_interval_minutes
            if is_sequential
            else 2.0
        )
        outlier_overlay = build_drilldown_zoom_outlier_overlay_recipe(
            representative_utc=outlier_context.representative_utc,
            representative_delta_snr_db=(
                outlier_context.representative_delta_snr_db
            ),
            qualifying_marker_times_utc=qualifying_marker_times_utc,
            qualifying_marker_delta_snr_db=(
                qualifying_marker_delta_snr_db
            ),
            candidate_start_utc=outlier_context.event_start_utc,
            candidate_end_utc=outlier_context.event_end_utc,
            native_evidence_unit_minutes=native_evidence_unit_minutes,
            local_baseline_db=outlier_context.local_baseline_db,
            pre_baseline_db=outlier_context.pre_baseline_db,
            post_baseline_db=outlier_context.post_baseline_db,
            pre_flank_start_utc=outlier_context.pre_flank_start_utc,
            pre_flank_end_utc=outlier_context.pre_flank_end_utc,
            post_flank_start_utc=outlier_context.post_flank_start_utc,
            post_flank_end_utc=outlier_context.post_flank_end_utc,
            robust_spread_db=outlier_context.robust_spread_db,
            robust_spread_method=outlier_context.robust_spread_method,
            minimum_robust_z=outlier_context.minimum_robust_z,
            minimum_departure_db=outlier_context.minimum_departure_db,
            labels={
                "marker": translations["fig_drilldown_outlier_candidate"],
                "focused_episode": translations[
                    "fig_drilldown_outlier_focused_episode"
                ],
                "local_baseline": translations[
                    "fig_drilldown_outlier_expected_local_delta_snr"
                ],
                "flank_baseline": translations[
                    "fig_drilldown_outlier_flank_baseline"
                ],
                "robust_z": translations[
                    "fmt_drilldown_outlier_robust_z_guide"
                ],
                "qualifying_robust_z": translations[
                    "fmt_drilldown_outlier_qualifying_robust_z_guide"
                ],
                "absolute_departure": translations[
                    "fmt_drilldown_outlier_absolute_departure_gate"
                ],
            },
        )
    delta_recipe = build_drilldown_zoom_benchmark_delta_snr_recipe(
        evidence_df,
        start_utc=focus_window.start_utc,
        end_utc=focus_window.end_utc,
        title=zoom_title,
        panel_title=translations[
            "fig_drilldown_native_benchmark_panel_title"
        ],
        x_label=translations["fig_drilldown_native_time_x"],
        y_label=translations["fig_drilldown_native_benchmark_y"],
        empty_text=translations[
            "fig_drilldown_native_benchmark_unavailable"
        ],
        evidence_unit_label=translations[
            "fig_drilldown_native_scheduled_pair"
            if is_sequential
            else "fig_drilldown_native_joint_spot"
        ],
        is_sequential=is_sequential,
        reference_snr_correction_notice=full_delta_recipe.get(
            "reference_snr_correction_notice",
            "",
        ),
        outlier_overlay=outlier_overlay,
    )
    coverage_recipe = _compare_coverage_recipe(
        comparison_units,
        coverage_title=zoom_title,
        selected_segment=full_coverage_recipe["selected_segment"],
        analysis_start_t=focus_window.start_utc,
        analysis_end_t=focus_window.end_utc,
        time_bin_options=(focus_time_bin,),
        time_bin_default=focus_time_bin,
        figure_labels=full_coverage_recipe["labels"],
        population_mode=SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    )
    return delta_recipe, coverage_recipe

def delta_snr_outlier_marker_recipe(
    outlier_model,
    translations,
    station_identities=None,
):
    """Return localized markers at episode or selected-path resolution."""
    if outlier_model is None:
        return None
    marker_recipe = outlier_model.marker_recipe(station_identities)
    if marker_recipe is None:
        return None
    report_entries = getattr(outlier_model, "report_entries", None)
    if station_identities is None and report_entries is not None:
        representative_keys = {
            (
                strongest_candidate.station_identity.callsign,
                strongest_candidate.station_identity.locator,
                int(strongest_candidate.representative_utc.value),
            )
            for report_entry in report_entries
            if report_entry.candidates
            for strongest_candidate in (
                max(
                    report_entry.candidates,
                    key=lambda candidate: abs(
                        candidate.representative_delta_snr_db
                        - candidate.station_baseline_db
                    ),
                ),
            )
        }
        episode_markers = [
            marker
            for marker in marker_recipe["markers"]
            if (
                marker["callsign"],
                marker["locator"],
                int(marker["marker_utc_ns"]),
            )
            in representative_keys
        ]
        if not episode_markers:
            return None
        marker_recipe = dict(marker_recipe)
        marker_recipe["markers"] = episode_markers
        marker_recipe["candidate_count"] = len(episode_markers)
        marker_recipe["candidate_signature"] = sha256(
            json.dumps(
                episode_markers,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
        ).hexdigest()
    marker_recipe["legend_label"] = translations[
        "fig_delta_snr_outlier_candidate"
    ]
    return marker_recipe

def outlier_station_direction_lookup(scope_rows):
    """Return exact station identities mapped to retained compass sectors."""
    required_columns = {"peer_sign", "peer_grid", "dir_name"}
    if (
        scope_rows is None
        or scope_rows.empty
        or not required_columns.issubset(scope_rows.columns)
    ):
        return {}
    direction_lookup = {}
    for callsign, locator, direction in scope_rows[
        ["peer_sign", "peer_grid", "dir_name"]
    ].itertuples(index=False, name=None):
        callsign_text = str(callsign).strip().upper()
        locator_text = str(locator).strip().upper()
        direction_text = str(direction).strip().upper()
        if (
            callsign_text
            and locator_text
            and direction_text in COMPASS
        ):
            direction_lookup.setdefault(
                (callsign_text, locator_text),
                direction_text,
            )
    return direction_lookup

class InspectorPreparation:
    """Own the active run's bounded cache and on-demand evidence preparation."""

    def __init__(self, session_state, run_id, timing_collector=None):
        self.session_state = session_state
        self.run_id = run_id
        self.timing_collector = timing_collector

    def _cache(self):
        """Return the current run's bounded cache from this Streamlit session."""
        cache = self.session_state.get(INSPECTOR_CACHE_STATE_KEY)
        if not isinstance(cache, SessionInspectorCache) or cache.run_id != self.run_id:
            cache = SessionInspectorCache(
                self.run_id,
                max_bytes=INSPECTOR_CACHE_MAX_BYTES,
                namespace_limits=INSPECTOR_CACHE_NAMESPACE_LIMITS,
            )
            self.session_state[INSPECTOR_CACHE_STATE_KEY] = cache
        return cache

    def cache_get(self, namespace, key, *, item=""):
        """Read one cache entry and expose the outcome to terminal profiling."""
        started_at = perf_counter()
        cache = self._cache()
        value, hit = cache.get(namespace, key)
        elapsed = perf_counter() - started_at
        detail = (
            f"{'hit' if hit else 'miss'} | entries {cache.entry_count} | "
            f"cached {cache.total_bytes / 1024:.1f} KiB"
        )
        if self.timing_collector is not None:
            self.timing_collector.add(f"inspector cache {namespace}", elapsed, detail=detail)
        log_performance_event(
            "inspector_cache",
            namespace=namespace,
            item=item or namespace,
            outcome="hit" if hit else "miss",
            entries=cache.entry_count,
            cache_bytes=cache.total_bytes,
        )
        return value, hit

    def cache_put(self, namespace, key, value, *, size_bytes=None):
        cache = self._cache()
        stored = cache.put(namespace, key, value, size_bytes=size_bytes)
        self.session_state[INSPECTOR_CACHE_STATE_KEY] = cache
        if not stored:
            log_performance_event(
                "inspector_cache",
                namespace=namespace,
                outcome="not_stored",
                entries=cache.entry_count,
                cache_bytes=cache.total_bytes,
            )
        return stored

    def prepare_options(self, enriched_df, *, analysis_id, max_peer_distance_km):
        options_cache_key = (
            INSPECTOR_CACHE_VERSION,
            analysis_id,
            float(max_peer_distance_km),
        )
        options_view_model, options_cache_hit = self.cache_get("options", options_cache_key,
            item="inspector options",
        )
        if not options_cache_hit:
            options_view_model = build_inspector_options(
                enriched_df,
                max_peer_distance_km=max_peer_distance_km,
            )
            self.cache_put(
                "options",
                options_cache_key,
                options_view_model,
            )

        return options_view_model


    def prepare_performance_segment(self, context: InspectorContext, scope: InspectorScope, scope_rows: pd.DataFrame, *, retained_time_bin) -> PreparedScope:
        analysis_id = context.analysis_id
        title = context.title
        parquet_path = context.parquet_path
        t = context.translations
        analysis_context = context.analysis_context
        presentation_context = context.presentation_context
        analysis_start_t = context.analysis_start_t
        analysis_end_t = context.analysis_end_t
        timing_collector = self.timing_collector
        selected_ranges = scope.selected_ranges
        selected_directions = scope.selected_directions
        selected_seg = scope.selected_segment
        distance_scope_intervals = scope.distance_scope_intervals
        df_seg = scope_rows
        selected_ranges = selected_ranges or (t["opt_full_range"],)
        selected_directions = selected_directions or (t["opt_all_dirs"],)
        opportunity_terms = presentation_context.absolute_terms(
            "TX" if analysis_id.startswith("TX") else "RX"
        )
        success_labels = success_figure_labels(t, analysis_id)
        retained_segment_time_bin = retained_time_bin
        if analysis_start_t is not None and analysis_end_t is not None:
            (
                _segment_time_bin_options,
                _segment_time_bin_default,
                retained_segment_time_bin_cache_token,
            ) = compare_temporal_time_bin_policy(
                analysis_start_t,
                analysis_end_t,
                retained_segment_time_bin,
            )
        else:
            retained_segment_time_bin_cache_token = retained_segment_time_bin

        segment_cache_key = (
            INSPECTOR_CACHE_VERSION,
            "opportunity",
            SUCCESS_DISTANCE_BINNING_VERSION,
            SUCCESS_SNR_BASELINE_VERSION,
            analysis_id,
            tuple(selected_ranges),
            tuple(selected_directions),
            tuple(
                (float(lower_km), float(upper_km))
                for lower_km, upper_km in distance_scope_intervals
            ),
            int(analysis_context.min_confirmed_opportunities_per_peer),
            str(analysis_start_t),
            str(analysis_end_t),
            presentation_context.language,
            presentation_context.theme,
            title,
            selected_seg,
            retained_segment_time_bin_cache_token,
        )
        segment_bundle, segment_cache_hit = self.cache_get("segment", segment_cache_key,
            item="opportunity segment model",
        )
        if not segment_cache_hit:
            rows, analysis_start_t, analysis_end_t = self._prepare_performance_rows(
                scope_rows, parquet_path=parquet_path, analysis_id=analysis_id,
                analysis_start_t=analysis_start_t, analysis_end_t=analysis_end_t,
            )
            with _timed_span(timing_collector, "opportunity segment view prep"):
                opportunity_view_model = build_opportunity_inspector_view_model(
                    df_seg,
                    analysis_id=analysis_id,
                    minimum_confirmed=analysis_context.min_confirmed_opportunities_per_peer,
                    presentation_context=presentation_context,
                )

            with _timed_span(
                timing_collector,
                "opportunity exact-distance evidence prep",
            ):
                segment_recipe = _opportunity_segment_recipe(
                    title,
                    selected_seg,
                    opportunity_view_model.confirmed_rows,
                    analysis_start_t,
                    analysis_end_t,
                    opportunity_terms,
                    minimum_trials=analysis_context.min_confirmed_opportunities_per_peer,
                    figure_labels=success_labels,
                    distance_scope_intervals=distance_scope_intervals,
                )
            with _timed_span(
                timing_collector,
                "opportunity temporal evidence prep",
            ):
                temporal_base_recipe = _opportunity_temporal_recipe(
                    success_temporal_figure_title(
                        analysis_context.callsign,
                        analysis_id,
                        t,
                        figure_kind="evidence",
                    ),
                    selected_seg,
                    opportunity_view_model.confirmed_rows,
                    rows,
                    analysis_start_t,
                    analysis_end_t,
                    opportunity_terms,
                    figure_labels=success_labels,
                    snr_title=success_temporal_figure_title(
                        analysis_context.callsign,
                        analysis_id,
                        t,
                        figure_kind="snr",
                    ),
                    population_mode=SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
                    snr_representation=(
                        SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE
                    ),
                    retained_time_bin=retained_segment_time_bin,
                )
            temporal_bundle = {
                "base_recipe": temporal_base_recipe,
                "time_bin_options": tuple(
                    temporal_base_recipe["time_bin_options"]
                ),
                "time_bin_default": temporal_base_recipe["time_bin_default"],
            }
            opportunity_display_model = {
                "summary_lines": list(opportunity_view_model.summary_lines),
                "confirmed_station_count": int(
                    opportunity_view_model.confirmed_station_count
                ),
                "confirmed_opportunity_count": int(
                    opportunity_view_model.confirmed_opportunity_count
                ),
                "full_station_table": opportunity_view_model.full_station_table,
                "export_column_renames": dict(
                    opportunity_view_model.export_column_renames
                ),
                "station_column": opportunity_view_model.station_column,
                "locator_column": opportunity_view_model.locator_column,
                "distance_column": opportunity_view_model.distance_column,
                "azimuth_column": opportunity_view_model.azimuth_column,
                "hit_column": opportunity_view_model.hit_column,
                "export_station_column": (
                    opportunity_view_model.export_station_column
                ),
                "export_locator_column": (
                    opportunity_view_model.export_locator_column
                ),
            }
            segment_bundle = {
                "display_model": opportunity_display_model,
                "figure_recipe": segment_recipe,
                "temporal_bundle": temporal_bundle,
                "analysis_start_t": analysis_start_t,
                "analysis_end_t": analysis_end_t,
            }
            del opportunity_view_model, rows
            self.cache_put(
                "segment",
                segment_cache_key,
                segment_bundle,
            )


        return PreparedScope(segment_cache_key, segment_bundle, scope_rows)


    def prepare_benchmark_segment(self, context: InspectorContext, scope: InspectorScope, scope_rows: pd.DataFrame, *, retained_time_bin, outlier_detection_policy=None) -> PreparedScope:
        analysis_id = context.analysis_id
        title = context.title
        parquet_path = context.parquet_path
        t = context.translations
        analysis_context = context.analysis_context
        presentation_context = context.presentation_context
        analysis_start_t = context.analysis_start_t
        analysis_end_t = context.analysis_end_t
        is_sequential = context.is_sequential
        timing_collector = self.timing_collector
        selected_ranges = scope.selected_ranges
        selected_directions = scope.selected_directions
        selected_seg = scope.selected_segment
        df_seg = scope_rows
        is_outlier_reporting_enabled = outlier_detection_policy is not None
        reference_snr_correction_notice = configured_snr_correction_notice(
            analysis_context, t, is_compare=True, is_sequential=is_sequential,
        )
        preferred_segment_time_bin = retained_time_bin
        (
            temporal_time_options,
            temporal_time_default,
            retained_segment_time_bin_cache_token,
        ) = compare_temporal_time_bin_policy(
            analysis_start_t,
            analysis_end_t,
            preferred_segment_time_bin,
        )
        outlier_cache_key_suffix = (
            delta_snr_outlier_segment_cache_suffix(
                is_outlier_reporting_enabled,
                outlier_detection_policy,
            )
        )

        segment_cache_key = (
            INSPECTOR_CACHE_VERSION,
            "comparison",
            analysis_id,
            tuple(selected_ranges),
            tuple(selected_directions),
            bool(is_sequential),
            int(analysis_context.tx_ab_repeat_interval_minutes),
            int(analysis_context.tx_ab_target_start_minute),
            int(analysis_context.tx_ab_reference_start_minute),
            str(analysis_start_t),
            str(analysis_end_t),
            retained_segment_time_bin_cache_token,
            presentation_context.language,
            presentation_context.theme,
            title,
            selected_seg,
        ) + outlier_cache_key_suffix
        segment_bundle, segment_cache_hit = self.cache_get("segment", segment_cache_key,
            item="segment insight model",
        )
        if not segment_cache_hit:
            compare_view_model = build_compare_inspector_view_model(
                df_seg,
                analysis_id=analysis_id,
                is_sequential=is_sequential,
                analysis_context=analysis_context,
                presentation_context=presentation_context,
            )
            vals = df_seg["stat_val"].dropna()
            col_u_name = compare_view_model.target_name
            evidence_meta_df = (
                compare_view_model.build_evidence_identities()
            )
            has_plot_data = compare_view_model.has_plot_data
            segment_figure_recipe = None
            segment_temporal_bundle = None
            segment_summary = []
            segment_station_count = 0
            segment_evidence_count = 0
            segment_station_total_count = None
            segment_station_joint_count = None
            segment_spot_total_count = None
            segment_spot_joint_count = None
            joint_lbl = t["txt_joint"]
            outlier_model = None
            outlier_report_view_model = None

            if has_plot_data:
                (segment_comparison_units, segment_evidence_df,
                 outlier_model, outlier_report_view_model) = self._prepare_segment_comparison_units(
                    scope_rows, evidence_meta_df, parquet_path=parquet_path,
                    is_sequential=is_sequential, analysis_context=analysis_context,
                    analysis_start_t=analysis_start_t, analysis_end_t=analysis_end_t,
                    outlier_detection_policy=outlier_detection_policy,
                )
                segment_raw_values = (
                    segment_evidence_df["metric"]
                    if not segment_evidence_df.empty
                    else pd.Series(dtype=float)
                )
                segment_station_count = len(vals)
                segment_evidence_count = len(segment_raw_values)
                outcome_counts = compare_footer_counts(
                    df_seg,
                    max_dist_km=float("inf"),
                )
                joint_lbl = (
                    t["tbl_col_joint_pairs"]
                    if is_sequential
                    else t["txt_joint"]
                )
                async_lbl = t["leg_both_async"]
                segment_panel_station_counts = [
                    outcome_counts["stat_only_u"],
                    outcome_counts["stat_joint"],
                    outcome_counts["stat_both_async"],
                    outcome_counts["stat_only_r"],
                ]
                segment_panel_spot_counts = [
                    outcome_counts["spot_only_u"],
                    outcome_counts["spot_joint"],
                    outcome_counts["spot_both_async"],
                    outcome_counts["spot_only_r"],
                ]
                segment_panel_labels = [
                    compare_view_model.target_only_label,
                    joint_lbl,
                    async_lbl,
                    compare_view_model.reference_only_label,
                ]
                segment_panel_series_labels = [
                    t["lbl_results_stations"],
                    (
                        t["lbl_results_scheduled_pairs"]
                        if is_sequential
                        else t["lbl_results_spots"]
                    ),
                ]
                segment_station_total_count = sum(segment_panel_station_counts)
                segment_station_joint_count = outcome_counts["stat_joint"]
                segment_spot_total_count = sum(segment_panel_spot_counts)
                segment_spot_joint_count = outcome_counts["spot_joint"]

                segment_figure_recipe = _segment_figure_export_recipe(
                    title=title,
                    selected_segment=selected_seg,
                    is_sequential=is_sequential,
                    reference_snr_correction_notice=(
                        reference_snr_correction_notice
                    ),
                    station_values=vals,
                    spot_values=segment_raw_values,
                    panel_labels=segment_panel_labels,
                    panel_y_label=t["fig_share_percent_axis"],
                    decode_outcomes_title=t["fig_decode_outcomes"],
                    station_medians_title=t[
                        "fig_station_medians_delta"
                    ],
                    metric_axis_label=t["tbl_col_delta_snr"],
                    median_label=t["fig_median_label"],
                    mean_label=t["fig_mean_label"],
                    no_data_label=t["fig_no_data"],
                    panel_station_counts=segment_panel_station_counts,
                    panel_spot_counts=segment_panel_spot_counts,
                    panel_series_labels=segment_panel_series_labels,
                    paired_evidence_title=(
                        t["fig_scheduled_pair_delta"]
                        if is_sequential
                        else t["fig_joint_spot_delta"]
                    ),
                )
                station_summary = compare_metric_distribution_summary(
                    vals,
                    t["fmt_results_station_delta_summary"],
                    total_count=segment_station_total_count,
                    joint_count=segment_station_joint_count,
                    joint_label=joint_lbl,
                )
                observation_summary_key = (
                    "fmt_results_scheduled_pair_delta_summary"
                    if is_sequential
                    else "fmt_results_joint_spot_delta_summary"
                )
                spot_summary = compare_metric_distribution_summary(
                    segment_raw_values,
                    t[observation_summary_key],
                    total_count=segment_spot_total_count,
                    joint_count=segment_spot_joint_count,
                    joint_label=joint_lbl,
                )
                segment_summary = segment_summary_lines(
                    station_summary=station_summary,
                    spot_summary=spot_summary,
                )
                segment_temporal_rows = segment_evidence_df[
                    ["plot_time", "metric"]
                ].copy()
                del segment_evidence_df, segment_raw_values
                if not segment_comparison_units.empty:
                    chronological_title_label = t[
                        "fig_segment_chronological_delta"
                    ]
                    chronological_title_template = t[
                        "fmt_temporal_title_with_bins"
                    ].format(
                        title=chronological_title_label,
                        time_bin="{time_bin}",
                    )
                    folded_date_template = t[
                        "fig_segment_dates_folded"
                    ].replace("{count}", "{utc_date_count}")
                    temporal_figure_title = segment_temporal_figure_title(
                        title,
                        analysis_id,
                        selected_seg,
                        t,
                    )
                    compare_figure_labels = (
                        compare_coverage_figure_labels(
                            t,
                            analysis_id,
                            is_sequential=is_sequential,
                            target_only_label=t[
                                "leg_only_me"
                            ].format(
                                callsign=t["txt_target"]
                            ),
                            joint_label=t["txt_joint"],
                            reference_only_label=t[
                                "leg_only_ref"
                            ].format(
                                ref_callsign=t["txt_reference"]
                            ),
                        )
                    )
                    compare_coverage_recipe = _compare_coverage_recipe(
                        segment_comparison_units,
                        coverage_title=compare_temporal_coverage_title(
                            t,
                            analysis_id,
                            analysis_context.callsign,
                        ),
                        selected_segment=selected_seg,
                        analysis_start_t=analysis_start_t,
                        analysis_end_t=analysis_end_t,
                        time_bin_options=temporal_time_options,
                        time_bin_default=temporal_time_default,
                        figure_labels=compare_figure_labels,
                    )
                    del segment_comparison_units
                    if is_sequential:
                        temporal_count_label = t[
                            "fig_scheduled_pair_count"
                        ]
                        temporal_density_label = t[
                            "fig_relative_scheduled_pair_density"
                        ]
                    else:
                        temporal_count_label = t[
                            "fig_joint_spot_count"
                        ]
                        temporal_density_label = t[
                            "fig_relative_joint_spot_density"
                        ]
                    with _timed_span(
                        timing_collector,
                        "segment temporal profiles build",
                    ):
                        temporal_base_recipe = (
                            _segment_temporal_evidence_export_recipe(
                                segment_temporal_rows,
                                temporal_figure_title,
                                temporal_time_default,
                                temporal_count_label,
                                analysis_start_t=analysis_start_t,
                                analysis_end_t=analysis_end_t,
                                reference_snr_correction_notice=(
                                    reference_snr_correction_notice
                                ),
                                chronological_title=(
                                    chronological_title_template
                                ),
                                chronological_x_label=t[
                                    "fig_segment_chronological_x"
                                ],
                                chronological_unavailable_text=t[
                                    "fig_compare_chronological_unavailable"
                                ],
                                metric_axis_label=t["tbl_col_delta_snr"],
                                folded_title=(
                                    folded_utc_hour_panel_title(t)
                                ),
                                folded_date_annotation=folded_date_template,
                                folded_x_label=t[
                                    "fig_segment_utc_hour_x"
                                ],
                                density_label=temporal_density_label,
                                folded_unavailable_text=t[
                                    "fig_segment_folded_unavailable"
                                ],
                                median_focus_axis_label=t[
                                    "fig_compare_median_focus_axis"
                                ],
                                median_label=t["fig_median_label"],
                                bin_median_label=t[
                                    "fig_temporal_bin_median"
                                ],
                                bin_iqr_label=t[
                                    "fig_temporal_bin_iqr"
                                ],
                                time_bin_options=temporal_time_options,
                            )
                        )
                    segment_temporal_bundle = {
                        "base_recipe": temporal_base_recipe,
                        "coverage_recipe": compare_coverage_recipe,
                        "time_bin_options": tuple(temporal_time_options),
                        "time_bin_default": temporal_time_default,
                        "chronological_title_template": chronological_title_template,
                    }
                else:
                    del segment_comparison_units
                del segment_temporal_rows

            if is_outlier_reporting_enabled and outlier_model is None:
                outlier_model = prepare_delta_snr_outlier_model(
                    True,
                    pd.DataFrame(),
                    analysis_start_utc=analysis_start_t,
                    analysis_end_utc=analysis_end_t,
                    paired_unit_cadence_minutes=(
                        analysis_context.tx_ab_repeat_interval_minutes
                        if is_sequential
                        else 2.0
                    ),
                    detection_policy=outlier_detection_policy,
                )
                outlier_report_view_model = (
                    build_delta_snr_outlier_report_view_model(
                        outlier_model,
                        pd.DataFrame(),
                    )
                )

            del vals, evidence_meta_df
            segment_bundle = {
                "view_model": compare_view_model,
                "figure_recipe": segment_figure_recipe,
                "temporal_bundle": segment_temporal_bundle,
                "summary": segment_summary,
                "evidence_station_count": int(segment_station_count),
                "evidence_count": int(segment_evidence_count),
            }
            if is_outlier_reporting_enabled:
                segment_bundle["outlier_model"] = outlier_model
                segment_bundle["outlier_report_view_model"] = (
                    outlier_report_view_model
                )
            self.cache_put(
                "segment",
                segment_cache_key,
                segment_bundle,
            )


        return PreparedScope(segment_cache_key, segment_bundle, scope_rows)


    def prepare_selected_benchmark_evidence(
        self, station_df, selected_identity_df, is_sequential,
        tx_ab_repeat_interval_minutes, tx_ab_target_start_minute,
        tx_ab_reference_start_minute, *, t, analysis_id, cache_key,
        analysis_context, preferred_time_bin, thresholded_station_rows=None,
        analysis_start_t=None, analysis_end_t=None, target_only_label=None,
        reference_only_label=None, outlier_model=None,
    ):
        identity_meta = _prepare_identity_meta(selected_identity_df)
        if identity_meta.empty:
            return None
        if len(identity_meta) > 1 and outlier_model is None:
            raise ValueError(
                "Selected Station Evidence requires exactly one station identity "
                "when outlier reporting is disabled."
            )
        identity_labels = identity_meta["identity"].tolist()
        reference_snr_correction_notice = configured_snr_correction_notice(
            analysis_context,
            t,
            is_compare=True,
            is_sequential=is_sequential,
        )
        (
            adaptive_time_agg_options,
            adaptive_time_agg_default,
            retained_extra_cache_token,
        ) = compare_temporal_time_bin_policy(
            analysis_start_t,
            analysis_end_t,
            preferred_time_bin,
        )
        cache_key = (
            *cache_key,
            "adaptive-time-bin-policy-v1",
            tuple(adaptive_time_agg_options),
            adaptive_time_agg_default,
            retained_extra_cache_token,
        )

        selected_bundle, selected_cache_hit = self.cache_get("selected", cache_key,
            item="selected evidence model",
        )
        if not selected_cache_hit:
            comparison_units, evidence_df = self._prepare_selected_comparison_units(
                station_df, identity_meta, is_sequential=is_sequential,
                tx_ab_repeat_interval_minutes=tx_ab_repeat_interval_minutes,
                tx_ab_target_start_minute=tx_ab_target_start_minute,
                tx_ab_reference_start_minute=tx_ab_reference_start_minute,
                thresholded_station_rows=thresholded_station_rows,
            )

            if is_sequential:
                count_label = t["fig_scheduled_pair_count"]
                density_label = t["fig_relative_scheduled_pair_density"]
            else:
                count_label = t["fig_joint_spot_count"]
                density_label = t["fig_relative_joint_spot_density"]
            evidence_count = len(evidence_df)
            evidence_title = selected_evidence_figure_title(
                identity_labels,
                evidence_count,
                analysis_id=analysis_id,
                is_sequential=is_sequential,
                translations=t,
                allow_multiple=(outlier_model is not None),
            )
            time_agg_options = tuple(adaptive_time_agg_options)
            time_agg_default = adaptive_time_agg_default
            folded_date_template = t[
                "fig_segment_dates_folded"
            ].replace(
                "{count}",
                "{utc_date_count}",
            )
            base_recipe = _selected_evidence_export_recipe(
                evidence_df,
                evidence_title,
                time_agg_default,
                is_sequential,
                analysis_start_t=analysis_start_t,
                analysis_end_t=analysis_end_t,
                reference_snr_correction_notice=(
                    reference_snr_correction_notice
                ),
                count_label=count_label,
                chronological_title=t[
                    "fig_selected_compare_chronological_title"
                ],
                chronological_x_label=t[
                    "fig_segment_chronological_x"
                ],
                chronological_unavailable_text=t[
                    "fig_compare_chronological_unavailable"
                ],
                metric_axis_label=t["tbl_col_delta_snr"],
                folded_title=t[
                    "fig_selected_compare_folded_title"
                ],
                folded_date_annotation=folded_date_template,
                folded_x_label=t["fig_segment_utc_hour_x"],
                density_label=density_label,
                folded_unavailable_text=t[
                    "fig_segment_folded_unavailable"
                ],
                median_focus_axis_label=t[
                    "fig_compare_median_focus_axis"
                ],
                median_label=t["fig_median_label"],
                bin_median_label=t["fig_temporal_bin_median"],
                bin_iqr_label=t["fig_temporal_bin_iqr"],
                time_bin_options=time_agg_options,
            )
            selected_coverage_recipe = None
            if not comparison_units.empty and len(identity_meta) == 1:
                selected_identity = identity_meta.iloc[0]
                mode_suffix = (
                    "tx"
                    if analysis_id.startswith("TX")
                    else "rx"
                )
                selected_coverage_title = t[
                    f"fig_selected_compare_coverage_title_{mode_suffix}"
                ].format(
                    station=str(selected_identity["peer_sign"]),
                    locator=str(selected_identity["peer_grid"]),
                )
                selected_coverage_recipe = _compare_coverage_recipe(
                    comparison_units,
                    coverage_title=selected_coverage_title,
                    selected_segment=identity_labels[0],
                    analysis_start_t=analysis_start_t,
                    analysis_end_t=analysis_end_t,
                    time_bin_options=time_agg_options,
                    time_bin_default=time_agg_default,
                    figure_labels=compare_coverage_figure_labels(
                        t,
                        analysis_id,
                        is_sequential=is_sequential,
                        target_only_label=target_only_label,
                        joint_label=t["txt_joint"],
                        reference_only_label=reference_only_label,
                    ),
                    population_mode=(
                        SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
                    ),
                )
            selected_bundle = {
                "base_recipe": base_recipe,
                "coverage_recipe": selected_coverage_recipe,
                "time_agg_options": tuple(time_agg_options),
                "time_agg_default": time_agg_default,
                "title": evidence_title,
                "identity_labels": tuple(identity_labels),
                "evidence_count": int(evidence_count),
                "comparison_unit_count": int(len(comparison_units)),
                "selected_station_count": int(len(identity_meta)),
            }
            self.cache_put(
                "selected",
                cache_key,
                selected_bundle,
            )
            del comparison_units, evidence_df


        return PreparedEvidence(cache_key, selected_bundle)


    def prepare_selected_performance(self, context: InspectorContext, scope: InspectorScope, station_view: StationInsightsView, prepared_segment: PreparedScope, *, preferred_time_bin):
        analysis_id = context.analysis_id
        parquet_path = context.parquet_path
        t = context.translations
        presentation_context = context.presentation_context
        analysis_start_t = context.analysis_start_t
        analysis_end_t = context.analysis_end_t
        timing_collector = self.timing_collector
        selected_seg = scope.selected_segment
        scope_token = scope.scope_token
        station_col = station_view.station_column
        loc_col = station_view.locator_column
        km_col = station_view.distance_column
        az_col = station_view.azimuth_column
        selected_rows = list(station_view.selected_rows)
        df_seg = prepared_segment.scope_rows
        disp_df = station_view.displayed_table
        analysis_start_t = prepared_segment.bundle["analysis_start_t"]
        analysis_end_t = prepared_segment.bundle["analysis_end_t"]
        opportunity_terms = presentation_context.absolute_terms("TX" if analysis_id.startswith("TX") else "RX")
        success_labels = success_figure_labels(t, analysis_id)
        selected_meta_df = disp_df.iloc[selected_rows][[station_col, loc_col, km_col, az_col]].copy()
        selected_meta_df = selected_meta_df.drop_duplicates(subset=[station_col, loc_col])
        selected_identity = selected_meta_df[[station_col, loc_col]].copy()
        selected_identity.columns = ["peer_sign", "peer_grid"]
        selected_station_labels = (
            selected_identity["peer_sign"].astype(str) +
            " (" + selected_identity["peer_grid"].astype(str) + ")"
        ).tolist()
        with _timed_span(timing_collector, "selected station rows load"):
            selected_station_rows = _load_station_rows_for_drilldown(
                parquet_path,
                selected_meta_df,
                station_col,
                loc_col,
                columns=OPPORTUNITY_DRILLDOWN_VIEW_COLUMNS,
            )

        selection_label = selected_station_label(
            selected_station_labels,
            analysis_id=analysis_id,
            translations=t,
        )
        selected_station = str(
            selected_identity.iloc[0]["peer_sign"]
        ).strip().upper()
        selected_locator = str(
            selected_identity.iloc[0]["peer_grid"]
        ).strip().upper()
        selected_peer_rows = df_seg.loc[
            (df_seg["peer_sign"].astype(str).str.upper() == selected_station)
            & (
                df_seg["peer_grid"].astype(str).str.upper()
                == selected_locator
            )
        ].copy()
        selected_cache_key = (
            INSPECTOR_CACHE_VERSION,
            "opportunity",
            "selected-success-temporal-v1",
            SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
            SUCCESS_SNR_REPRESENTATION_ACTUAL,
            analysis_id,
            scope_token,
            selected_station,
            selected_locator,
            str(analysis_start_t),
            str(analysis_end_t),
            presentation_context.language,
            presentation_context.theme,
            compare_temporal_time_bin_policy(
                analysis_start_t,
                analysis_end_t,
                preferred_time_bin,
            )[2],
        )
        selected_base_recipe, selected_cache_hit = self.cache_get("selected", selected_cache_key,
            item="opportunity selected temporal model",
        )
        if not selected_cache_hit:
            with _timed_span(
                timing_collector,
                "opportunity selected temporal evidence prep",
            ):
                selected_base_recipe = _opportunity_temporal_recipe(
                    selected_success_temporal_figure_title(
                        selected_station,
                        selected_locator,
                        analysis_id,
                        t,
                        figure_kind="evidence",
                    ),
                    selected_seg,
                    selected_peer_rows,
                    selected_station_rows,
                    analysis_start_t,
                    analysis_end_t,
                    opportunity_terms,
                    figure_labels=success_labels,
                    snr_title=selected_success_temporal_figure_title(
                        selected_station,
                        selected_locator,
                        analysis_id,
                        t,
                        figure_kind="snr",
                    ),
                    population_mode=(
                        SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
                    ),
                    snr_representation=SUCCESS_SNR_REPRESENTATION_ACTUAL,
                    retained_time_bin=preferred_time_bin,
                )
            self.cache_put(
                "selected",
                selected_cache_key,
                selected_base_recipe,
            )


        return {
            'selected_meta_df': selected_meta_df,
            'selected_identity': selected_identity,
            'selected_station_labels': selected_station_labels,
            'selected_station_rows': selected_station_rows,
            'selected_station': selected_station,
            'selected_locator': selected_locator,
            'selected_peer_rows': selected_peer_rows,
            'selected_cache_key': selected_cache_key,
            'selected_base_recipe': selected_base_recipe,
            'selection_label': selection_label,
        }


    def prepare_selected_benchmark(self, context: InspectorContext, scope: InspectorScope, station_view: StationInsightsView, prepared_segment: PreparedScope):
        t = context.translations
        station_col = station_view.station_column
        loc_col = station_view.locator_column
        selected_rows = list(station_view.selected_rows)
        df_seg = prepared_segment.scope_rows
        selected_station_table = station_view.selected_station_table
        selected_rows_for_evidence = list(station_view.selected_rows)
        loc_col = t['tbl_col_loc']
        selected_meta_df = selected_station_table.iloc[
            selected_rows_for_evidence
        ][
            [station_col, loc_col, t['tbl_col_km'], t['tbl_col_az']]
        ].copy()
        selected_meta_df[station_col] = selected_meta_df[station_col].astype(str)
        selected_meta_df[loc_col] = selected_meta_df[loc_col].astype(str)
        selected_meta_df = selected_meta_df.drop_duplicates(subset=[station_col, loc_col])
        selected_identity_df = selected_meta_df[[station_col, loc_col]].copy()
        selected_identity_df.columns = ["peer_sign", "peer_grid"]
        selected_identity_df = selected_identity_df.drop_duplicates()
        selected_identity_pairs = tuple(
            (
                str(callsign).strip().upper(),
                str(locator).strip().upper(),
            )
            for callsign, locator in selected_identity_df[
                ["peer_sign", "peer_grid"]
            ].itertuples(index=False, name=None)
        )
        selected_station_labels = (
            selected_identity_df["peer_sign"].astype(str) +
            " (" + selected_identity_df["peer_grid"].astype(str) + ")"
        ).tolist()
        selected_identity_pair_set = set(selected_identity_pairs)
        selected_thresholded_mask = [
            (callsign, locator) in selected_identity_pair_set
            for callsign, locator in zip(
                df_seg["peer_sign"]
                .astype(str)
                .str.strip()
                .str.upper(),
                df_seg["peer_grid"]
                .astype(str)
                .str.strip()
                .str.upper(),
            )
        ]
        selected_thresholded_rows = df_seg.loc[
            selected_thresholded_mask
        ].copy()
        selected_identity_cache_key = (
            selected_identity_pairs[0]
            if len(selected_identity_pairs) == 1
            else (
                "multiple-selected-stations",
                selected_identity_pairs,
            )
        )
        return {
            'selected_meta_df': selected_meta_df,
            'selected_identity_df': selected_identity_df,
            'selected_identity_pairs': selected_identity_pairs,
            'selected_station_labels': selected_station_labels,
            'selected_thresholded_rows': selected_thresholded_rows,
            'selected_identity_cache_key': selected_identity_cache_key,
        }



    def _prepare_performance_rows(self, scope_rows, *, parquet_path, analysis_id, analysis_start_t, analysis_end_t):
        """Read projected rows and resolve UTC bounds without localized recipes."""
        df_seg = scope_rows
        timing_collector = self.timing_collector
        run_id = self.run_id
        identity_meta = df_seg[["peer_sign", "peer_grid"]].drop_duplicates()
        try:
            with _timed_span(timing_collector, "opportunity rows parquet read"):
                rows = read_parquet_artifact(
                    parquet_path,
                    columns=list(OPPORTUNITY_SEGMENT_VIEW_COLUMNS),
                    filters=[("peer_sign", "in", identity_meta["peer_sign"].astype(str).unique().tolist())],
                )
        except FileNotFoundError as exc:
            _log_artifact_read_failure(
                exc,
                parquet_path=parquet_path,
                analysis_id=analysis_id,
                run_id=run_id,
                stage="opportunity segment read",
            )
            raise InspectorArtifactReadError(exc) from exc
        except (KeyError, ValueError) as exc:
            _log_artifact_read_failure(
                exc,
                parquet_path=parquet_path,
                analysis_id=analysis_id,
                run_id=run_id,
                stage="opportunity segment read",
            )
            raise InspectorArtifactReadError(exc) from exc
        with _timed_span(timing_collector, "opportunity segment prep"):
            rows["peer_sign"] = rows["peer_sign"].astype(str)
            rows["peer_grid"] = rows["peer_grid"].astype(str)
            rows = rows.merge(identity_meta, on=["peer_sign", "peer_grid"], how="inner")
            row_times = opportunity_utc_from_time_slot(rows["time_slot"]).dropna()
            if analysis_start_t is None:
                analysis_start_t = row_times.min() if not row_times.empty else pd.Timestamp.now(tz="UTC")
            if analysis_end_t is None:
                analysis_end_t = (
                    row_times.max() + pd.Timedelta(minutes=2)
                    if not row_times.empty
                    else _as_utc_timestamp(analysis_start_t) + pd.Timedelta(minutes=2)
                )
            del row_times

        return rows, analysis_start_t, analysis_end_t

    def _prepare_segment_comparison_units(
        self, scope_rows, evidence_meta_df, *, parquet_path, is_sequential,
        analysis_context, analysis_start_t, analysis_end_t, outlier_detection_policy,
    ):
        """Prepare canonical paired units and detector evidence before localization."""
        df_seg = scope_rows
        timing_collector = self.timing_collector
        is_outlier_reporting_enabled = outlier_detection_policy is not None
        outlier_model = None
        outlier_report_view_model = None
        with _timed_span(
            timing_collector,
            "segment comparison units build",
        ):
            segment_comparison_units = _build_segment_compare_units(
                df_seg,
                evidence_meta_df,
                parquet_path,
                is_sequential,
                tx_ab_repeat_interval_minutes=(
                    analysis_context.tx_ab_repeat_interval_minutes
                ),
                tx_ab_target_start_minute=(
                    analysis_context.tx_ab_target_start_minute
                ),
                tx_ab_reference_start_minute=(
                    analysis_context.tx_ab_reference_start_minute
                ),
            )
            segment_evidence_df = _compare_joint_evidence_points(
                segment_comparison_units,
                require_paired_eligible=True,
            )
            if is_outlier_reporting_enabled:
                with _timed_span(
                    timing_collector,
                    "Delta-SNR outlier candidate detection",
                ):
                    outlier_model = prepare_delta_snr_outlier_model(
                        True,
                        segment_comparison_units,
                        analysis_start_utc=analysis_start_t,
                        analysis_end_utc=analysis_end_t,
                        station_directions=(
                            outlier_station_direction_lookup(df_seg)
                        ),
                        paired_unit_cadence_minutes=(
                            analysis_context.tx_ab_repeat_interval_minutes
                            if is_sequential
                            else 2.0
                        ),
                        detection_policy=outlier_detection_policy,
                    )
                    outlier_report_view_model = (
                        build_delta_snr_outlier_report_view_model(
                            outlier_model,
                            segment_comparison_units,
                        )
                    )
        return (segment_comparison_units, segment_evidence_df,
                outlier_model, outlier_report_view_model)

    def _prepare_selected_comparison_units(
        self, station_df, identity_meta, *, is_sequential,
        tx_ab_repeat_interval_minutes, tx_ab_target_start_minute,
        tx_ab_reference_start_minute, thresholded_station_rows,
    ):
        """Prepare thresholded native paired evidence without localized recipes."""
        timing_collector = self.timing_collector
        with _timed_span(
            timing_collector,
            "selected comparison units build",
        ):
            comparison_units = _build_compare_unit_rows(
                station_df,
                identity_meta,
                is_sequential,
                paired_identity_df=identity_meta,
                tx_ab_repeat_interval_minutes=tx_ab_repeat_interval_minutes,
                tx_ab_target_start_minute=tx_ab_target_start_minute,
                tx_ab_reference_start_minute=tx_ab_reference_start_minute,
            )
            comparison_units = _retain_thresholded_compare_outcomes(
                comparison_units,
                thresholded_station_rows,
            )
            evidence_df = _compare_joint_evidence_points(
                comparison_units,
            )

        return comparison_units, evidence_df

    def load_selected_benchmark_rows(self, context, station_view, selected_meta_df):
        with _timed_span(self.timing_collector, "selected station rows load"):
            return _load_station_rows_for_drilldown(
                context.parquet_path, selected_meta_df,
                station_view.station_column, station_view.locator_column,
            )

    def touch_artifact(self, parquet_path, analysis_id):
        """Retain the existing fragment heartbeat without reading the artifact."""
        touched = ARTIFACT_STORE.touch(parquet_path)
        if not touched:
            log_performance_event(
                "session_artifact_read", outcome="missing",
                stage="inspector heartbeat", analysis_id=analysis_id,
                run_id=self.run_id, artifact=Path(parquet_path).name,
                exists=False, error_type="FileNotFoundError",
            )
        return touched

    def log_artifact_read_failure(self, exc, *, parquet_path, analysis_id, stage):
        _log_artifact_read_failure(
            exc, parquet_path=parquet_path, analysis_id=analysis_id,
            run_id=self.run_id, stage=stage,
        )

    def prepare_empty_outlier_report(self, context, *, detection_policy):
        model = prepare_delta_snr_outlier_model(
            True, pd.DataFrame(), analysis_start_utc=context.analysis_start_t,
            analysis_end_utc=context.analysis_end_t,
            paired_unit_cadence_minutes=(
                context.analysis_context.tx_ab_repeat_interval_minutes
                if context.is_sequential else 2.0
            ),
            detection_policy=detection_policy,
        )
        report = build_delta_snr_outlier_report_view_model(model, pd.DataFrame())
        return model, report

    def prepare_outlier_exports(self, model, report, *, is_sequential):
        tables = build_delta_snr_outlier_export_tables(
            model, report, is_sequential=is_sequential,
        )
        metadata = build_delta_snr_outlier_export_metadata(model, tables)
        return tables, metadata

    filter_scope_rows = staticmethod(filter_inspector_scope)
    success_distance_scope_intervals = staticmethod(success_distance_scope_intervals)
    filter_station_rows_to_focus_window = staticmethod(filter_station_rows_to_focus_window)
    build_drilldown_table = staticmethod(_build_drilldown_table)
    load_station_rows = staticmethod(_load_station_rows_for_drilldown)
    delta_snr_outlier_marker_recipe = staticmethod(delta_snr_outlier_marker_recipe)
    build_performance_drilldown_zoom_recipes = staticmethod(build_performance_drilldown_zoom_recipes)
    build_benchmark_drilldown_zoom_recipes = staticmethod(build_benchmark_drilldown_zoom_recipes)
    drilldown_zoom_export_metadata = staticmethod(drilldown_zoom_export_metadata)

    def all_drilldown_context(self, context, station_view, prepared_segment, *, language):
        """Prepare the unchanged all-station export identity projection."""
        station_column = station_view.station_column
        locator_column = station_view.locator_column
        distance_column = station_view.distance_column
        azimuth_column = station_view.azimuth_column
        station_meta = station_view.full_station_table[
            [station_column, locator_column, distance_column, azimuth_column]
        ].copy()
        if context.is_opportunity:
            display_model = prepared_segment.bundle["display_model"]
            export_station_column = display_model["export_station_column"]
            export_locator_column = display_model["export_locator_column"]
            station_meta.rename(columns={
                station_column: export_station_column,
                locator_column: export_locator_column,
            }, inplace=True)
            station_column = export_station_column
            locator_column = export_locator_column
            is_local_median = False
            target_name = context.analysis_context.callsign.upper()
            reference_header = ""
        else:
            view_model = prepared_segment.bundle["view_model"]
            is_local_median = bool(view_model.is_local_median)
            target_name = view_model.target_name
            reference_header = view_model.reference_header
        return {
            "station_meta_df": station_meta,
            "station_col": station_column,
            "loc_col": locator_column,
            "km_col": distance_column,
            "az_col": azimuth_column,
            "analysis_id": context.analysis_id,
            "is_sequential": bool(context.is_sequential) if context.is_compare else False,
            "show_non_joint": bool(context.is_compare),
            "is_local_median": is_local_median,
            "col_u_name": target_name,
            "ref_header": reference_header,
            "tx_ab_repeat_interval_minutes": context.analysis_context.tx_ab_repeat_interval_minutes,
            "tx_ab_target_start_minute": context.analysis_context.tx_ab_target_start_minute,
            "tx_ab_reference_start_minute": context.analysis_context.tx_ab_reference_start_minute,
            "target_callsign": context.analysis_context.callsign,
            "lang": language,
        }

    def build_performance_drilldown_table(
        self, context, station_view, selected_meta_df, focused_station_rows,
        *, export_station_column,
    ):
        """Prepare canonical Performance export columns for the drill-down table."""
        station_column = station_view.station_column
        selected_meta_export_df = selected_meta_df.rename(
            columns={station_column: export_station_column}
        )
        selected_station_rows_export = focused_station_rows.rename(
            columns={station_column: export_station_column}
        )
        analysis_context = context.analysis_context
        return _build_drilldown_table(
            context.parquet_path, selected_meta_export_df,
            export_station_column, station_view.locator_column,
            station_view.distance_column, station_view.azimuth_column,
            context.analysis_id, False, False, False,
            analysis_context.callsign.upper(), "", context.translations,
            station_rows_df=selected_station_rows_export,
            tx_ab_repeat_interval_minutes=analysis_context.tx_ab_repeat_interval_minutes,
            tx_ab_target_start_minute=analysis_context.tx_ab_target_start_minute,
            tx_ab_reference_start_minute=analysis_context.tx_ab_reference_start_minute,
            target_callsign=analysis_context.callsign,
        )
