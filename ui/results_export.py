"""
Result export helpers for WSPRadar.

The export layer deliberately consumes registered result recipes instead of
rerunning analysis SQL. High-resolution figures and full-segment drill-down
tables are built only after the user requests the prepared results package,
while preserving the current segment, station, non-joint, and time-bin state.
"""

import hashlib
import io
import json
import math
from copy import deepcopy
from collections.abc import Mapping
from pathlib import Path
import time
import zipfile
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from matplotlib import colors as mcolors
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.text import Text

from config import APP_VERSION, CACHE_DIR, TEMPORAL_IQR_BAND_ALPHA
from config.delta_snr_outlier import (
    DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
    DeltaSnrOutlierDetectionPolicy,
)
from core.analysis_admission import AnalysisQueueFull, AnalysisQueueTimeout
from core.analysis_context import AnalysisContext
from core.artifact_store import (
    ARTIFACT_STORE,
    session_artifact_owner,
    validate_registered_session_artifacts,
)
from core.export_admission import EXPORT_ADMISSION_GATE
from core.fetch_models import DatabaseSource
from core.matplotlib_runtime import matplotlib_operation_lock
from core.map_data_artifacts import (
    MAP_DATA_ARTIFACT_SCHEMA_VERSION,
    MapDataArtifactPaths,
    read_map_data_artifacts,
)
from core.performance_timer import (
    log_performance_event,
    process_peak_rss_bytes,
    process_rss_bytes,
)
from core.presentation_context import PresentationContext
from core.snr_utils import format_snr_like_columns_for_csv
from i18n import T
from ui.config_io import CONFIG_APP_NAME, build_config_payload
from ui.config_save import render_config_save_control
from ui.share_analysis import render_share_analysis_browser
from ui.result_guidance import (
    RESULT_GUIDANCE_DOWNLOAD,
    render_result_guidance_popover,
)
from ui.result_hierarchy import utility_header_html
from ui.result_state import (
    EXPORT_RUN_ID_KEY,
    EXPORT_STATE_KEY,
    EXPORT_ZIP_BYTES_KEY,
    EXPORT_ZIP_FILENAME_KEY,
    EXPORT_ZIP_SIGNATURE_KEY,
    clear_prepared_result_state,
)
from ui.matplotlib_renderer import dispose_matplotlib_figure
from ui.inspector.drilldown_focus import (
    DRILLDOWN_FOCUS_SCHEMA_VERSION,
    DRILLDOWN_OUTLIER_FOCUS_OPTION,
)
from ui.inspector.outlier_export import (
    DELTA_SNR_OUTLIER_EXPORT_SCHEMA_VERSION,
    DeltaSnrOutlierExportTables,
    OUTLIER_EVENT_PATH_COLUMNS,
    OUTLIER_EVENT_PATHS_TABLE_FILENAME,
    OUTLIER_PAIRED_EVIDENCE_COLUMNS,
    OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME,
)
from ui.plots.temporal_layout import TEMPORAL_EVIDENCE_LAYOUT_VERSION
from ui.url_state import build_share_url


BENCHMARK_EXPORT_FOLDER = "benchmark"
PERFORMANCE_EXPORT_FOLDER = "performance"
EXPORTABLE_RESULT_FOLDERS = frozenset(
    {BENCHMARK_EXPORT_FOLDER, PERFORMANCE_EXPORT_FOLDER}
)
PERFORMANCE_DISTANCE_EXPORT_RENDER_VERSION = 1
TEMPORAL_SNR_EXPORT_RENDER_VERSION = 8
TEMPORAL_IQR_EXPORT_LINEWIDTH = 0.4
DRILLDOWN_ZOOM_EXPORT_SCHEMA_VERSION = DRILLDOWN_FOCUS_SCHEMA_VERSION
DRILLDOWN_ZOOM_PERFORMANCE_FIGURE_EXPORTS = (
    (
        "figure_drilldown_zoom_snr_evidence.png",
        "drilldown_zoom_performance_snr_figure_recipe",
        ("snr_title", "title"),
    ),
    (
        "figure_drilldown_zoom_temporal_evidence.png",
        "drilldown_zoom_performance_temporal_figure_recipe",
        ("evidence_title", "title"),
    ),
)
DRILLDOWN_ZOOM_BENCHMARK_FIGURE_EXPORTS = (
    (
        "figure_drilldown_zoom_delta_snr_evidence.png",
        "drilldown_zoom_benchmark_delta_snr_figure_recipe",
        ("title", "evidence_title"),
    ),
    (
        "figure_drilldown_zoom_coverage.png",
        "drilldown_zoom_benchmark_coverage_figure_recipe",
        ("evidence_title", "title"),
    ),
)
DRILLDOWN_ZOOM_RECIPE_KEYS = tuple(
    recipe_key
    for _figure_name, recipe_key, _title_keys in (
        *DRILLDOWN_ZOOM_PERFORMANCE_FIGURE_EXPORTS,
        *DRILLDOWN_ZOOM_BENCHMARK_FIGURE_EXPORTS,
    )
)
BENCHMARK_EVIDENCE_FIGURE_EXPORTS = (
    (
        "figure_segment_temporal_coverage.png",
        "segment_temporal_coverage_figure_recipe",
        ("evidence_title",),
    ),
    (
        "figure_selected_station_coverage.png",
        "selected_station_coverage_figure_recipe",
        ("evidence_title",),
    ),
)

OUTLIER_EXPORT_TABLE_FILENAMES = (
    OUTLIER_EVENT_PATHS_TABLE_FILENAME,
    OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME,
)

OUTLIER_EXPORT_COLUMN_TRANSLATION_KEYS = {
    "event_id": "col_export_outlier_event_id",
    "combined_event_class": "col_export_outlier_combined_event_class",
    "event_first_evidence_utc": (
        "col_export_outlier_event_first_evidence_utc"
    ),
    "event_last_evidence_utc": "col_export_outlier_event_last_evidence_utc",
    "cross_path_context": "col_export_outlier_cross_path_context",
    "departure_direction": "col_export_outlier_departure_direction",
    "qualifying_path_count": "col_export_outlier_qualifying_path_count",
    "path_event_id": "col_export_outlier_path_event_id",
    "path_number": "col_export_outlier_path_number",
    "path_occurrence": "col_export_outlier_path_occurrence",
    "path": "col_export_outlier_path",
    "callsign": "col_export_outlier_callsign",
    "locator": "col_export_outlier_locator",
    "direction": "col_export_outlier_direction",
    "path_event_class": "col_export_outlier_path_event_class",
    "path_first_evidence_utc": (
        "col_export_outlier_path_first_evidence_utc"
    ),
    "path_last_evidence_utc": "col_export_outlier_path_last_evidence_utc",
    "paired_unit_type": "col_export_outlier_paired_unit_type",
    "paired_unit_count": "col_export_outlier_paired_unit_count",
    "first_to_last_span_minutes": (
        "col_export_outlier_first_to_last_span_minutes"
    ),
    "median_evidence_interval_minutes": (
        "col_export_outlier_median_evidence_interval_minutes"
    ),
    "largest_gap_minutes": "col_export_outlier_largest_gap_minutes",
    "expected_local_delta_snr_db": (
        "col_export_outlier_expected_local_delta_snr_db"
    ),
    "observed_median_delta_snr_db": (
        "col_export_outlier_observed_median_delta_snr_db"
    ),
    "largest_single_unit_departure_db": (
        "col_export_outlier_largest_single_unit_departure_db"
    ),
    "path_robust_z_score": "col_export_outlier_episode_robust_z_score",
    "pre_event_baseline_delta_snr_db": (
        "col_export_outlier_pre_event_baseline_delta_snr_db"
    ),
    "post_event_baseline_delta_snr_db": (
        "col_export_outlier_post_event_baseline_delta_snr_db"
    ),
    "absolute_pre_post_baseline_difference_db": (
        "col_export_outlier_absolute_pre_post_baseline_difference_db"
    ),
    "agreeing_paired_unit_count": (
        "col_export_outlier_agreeing_paired_unit_count"
    ),
    "paired_unit_sign_agreement_fraction": (
        "col_export_outlier_paired_unit_sign_agreement_fraction"
    ),
    "decode_edge_warning": "col_export_outlier_decode_edge_warning",
    "decode_edge_warning_reason": (
        "col_export_outlier_decode_edge_warning_reason"
    ),
    "nearby_joint_unit_count": "col_export_outlier_nearby_joint_unit_count",
    "nearby_target_only_unit_count": (
        "col_export_outlier_nearby_target_only_unit_count"
    ),
    "nearby_reference_only_unit_count": (
        "col_export_outlier_nearby_reference_only_unit_count"
    ),
    "unit_sequence": "col_export_outlier_unit_sequence",
    "utc": "col_export_outlier_utc",
    "target_snr_db": "col_export_outlier_target_snr_db",
    "corrected_reference_snr_db": (
        "col_export_outlier_corrected_reference_snr_db"
    ),
    "delta_snr_db": "col_export_outlier_delta_snr_db",
    "departure_from_local_baseline_db": (
        "col_export_outlier_departure_from_local_baseline_db"
    ),
    "cycle_robust_z_score": "col_export_outlier_cycle_robust_z_score",
    "meets_strong_anchor_gates": (
        "col_export_outlier_meets_strong_anchor_gates"
    ),
    "reported_boundary": "col_export_outlier_reported_boundary",
}

OUTLIER_EXPORT_EVENT_CLASS_TRANSLATION_KEYS = {
    "spot_impulse": "txt_outlier_event_spot_impulse",
    "short_burst": "txt_outlier_event_short_burst",
    "sustained_excursion": "txt_outlier_event_sustained_excursion",
    "mixed_duration": "txt_outlier_event_mixed_duration",
}
OUTLIER_EXPORT_SCOPE_TRANSLATION_KEYS = {
    "path_specific": "txt_export_outlier_scope_path_specific",
    "directionally_coherent": (
        "txt_export_outlier_scope_directionally_coherent"
    ),
    "scope_wide": "txt_export_outlier_scope_scope_wide",
    "multiple_paths": "txt_export_outlier_scope_multiple_paths",
}
OUTLIER_EXPORT_DEPARTURE_TRANSLATION_KEYS = {
    "positive": "txt_export_outlier_departure_positive",
    "negative": "txt_export_outlier_departure_negative",
    "mixed": "txt_export_outlier_departure_mixed",
    "neutral": "txt_export_outlier_departure_neutral",
}
OUTLIER_EXPORT_PAIRED_UNIT_TRANSLATION_KEYS = {
    "joint_spot": "txt_export_outlier_paired_unit_joint",
    "complete_scheduled_pair": "txt_export_outlier_paired_unit_scheduled",
}
OUTLIER_EXPORT_BOUNDARY_TRANSLATION_KEYS = {
    "start": "txt_export_outlier_boundary_start",
    "end": "txt_export_outlier_boundary_end",
    "start_and_end": "txt_export_outlier_boundary_start_and_end",
}
OUTLIER_EXPORT_WARNING_TRANSLATION_KEYS = {
    "reference_missing_near_positive_episode": (
        "txt_export_outlier_warning_reference_missing"
    ),
    "target_missing_near_negative_episode": (
        "txt_export_outlier_warning_target_missing"
    ),
}


class ExportArtifactUnavailableError(RuntimeError):
    """Report that a required registered export artifact cannot be reused."""


def _normalized_database_source(source_key) -> str:
    """Return a validated stable database-source key for export provenance."""
    if isinstance(source_key, DatabaseSource):
        return source_key.value
    try:
        return DatabaseSource(str(source_key)).value
    except ValueError as exc:
        raise ValueError("Export results require a known database source") from exc


def _current_run_id():
    return st.session_state.get("run_id", 0)


def _clear_prepared_results():
    """Drop prepared ZIP bytes when result selections or analysis runs change."""
    clear_prepared_result_state(st.session_state)


def _ensure_current_export_state():
    run_id = _current_run_id()
    if st.session_state.get(EXPORT_RUN_ID_KEY) != run_id:
        st.session_state[EXPORT_STATE_KEY] = {}
        st.session_state[EXPORT_RUN_ID_KEY] = run_id
        _clear_prepared_results()
    if EXPORT_STATE_KEY not in st.session_state:
        st.session_state[EXPORT_STATE_KEY] = {}
    return st.session_state[EXPORT_STATE_KEY]


def _set_with_restore(snapshots, obj, getter_name, setter_name, value):
    try:
        getter = getattr(obj, getter_name)
        setter = getattr(obj, setter_name)
        old_value = getter()
        setter(value)
        snapshots.append((setter, old_value))
    except Exception:
        return


def _is_near_white(rgba):
    try:
        r, g, b, a = mcolors.to_rgba(rgba)
        return a > 0 and r > 0.94 and g > 0.94 and b > 0.94
    except Exception:
        return False


def _is_near_black(rgba):
    try:
        r, g, b, a = mcolors.to_rgba(rgba)
        return a > 0 and r < 0.16 and g < 0.16 and b < 0.16
    except Exception:
        return False


def _is_light_line_color(rgba):
    """Return True for pale line colors that disappear on white export backgrounds."""
    try:
        r, g, b, a = mcolors.to_rgba(rgba)
        return a > 0 and r > 0.65 and g > 0.65 and b > 0.65
    except Exception:
        return False


def _style_patch_for_paper(snapshots, patch):
    """Temporarily adapt one dark-theme patch to a white paper background."""
    if _is_near_white(patch.get_facecolor()):
        _set_with_restore(
            snapshots,
            patch,
            "get_facecolor",
            "set_facecolor",
            "#d0d0d0",
        )
    elif _is_near_black(patch.get_facecolor()):
        _set_with_restore(
            snapshots,
            patch,
            "get_facecolor",
            "set_facecolor",
            "#f3f3f3",
        )
    if _is_near_white(patch.get_edgecolor()):
        _set_with_restore(
            snapshots,
            patch,
            "get_edgecolor",
            "set_edgecolor",
            "#777777",
        )


def _style_figure_for_paper(fig):
    """Temporarily restyle a dark UI figure for white-paper PNG export."""
    snapshots = []
    _set_with_restore(snapshots, fig.patch, "get_facecolor", "set_facecolor", "white")

    for ax in fig.axes:
        _set_with_restore(snapshots, ax, "get_facecolor", "set_facecolor", "white")
        try:
            ax.tick_params(colors="#222222")
        except Exception:
            pass
        for spine in ax.spines.values():
            _set_with_restore(snapshots, spine, "get_edgecolor", "set_edgecolor", "#777777")
        for patch in ax.patches:
            _style_patch_for_paper(snapshots, patch)
        for collection in ax.collections:
            try:
                facecolors = collection.get_facecolors()
            except Exception:
                continue
            if collection.get_gid() == "temporal-bin-iqr-band":
                _set_with_restore(
                    snapshots,
                    collection,
                    "get_facecolors",
                    "set_facecolor",
                    "#111111",
                )
            elif len(facecolors) and all(_is_near_white(color) for color in facecolors):
                _set_with_restore(snapshots, collection, "get_facecolors", "set_facecolor", "#d0d0d0")
            elif len(facecolors) and all(_is_near_black(color) for color in facecolors):
                _set_with_restore(snapshots, collection, "get_facecolors", "set_facecolor", "#f3f3f3")
            try:
                edgecolors = collection.get_edgecolors()
            except Exception:
                edgecolors = []
            if len(edgecolors) and all(_is_near_white(color) for color in edgecolors):
                _set_with_restore(snapshots, collection, "get_edgecolors", "set_edgecolor", "#777777")

    for text in fig.findobj(Text):
        _set_with_restore(snapshots, text, "get_color", "set_color", "#111111")
        text_box = text.get_bbox_patch()
        if text_box is not None:
            _style_patch_for_paper(snapshots, text_box)

    for line in fig.findobj(Line2D):
        line_gid = str(line.get_gid() or "")
        if (
            line_gid.startswith("temporal-bin-iqr-")
            and line_gid.endswith("-understroke")
        ):
            _set_with_restore(
                snapshots,
                line,
                "get_visible",
                "set_visible",
                False,
            )
            continue
        if line_gid in {"temporal-bin-iqr-q1", "temporal-bin-iqr-q3"}:
            _set_with_restore(
                snapshots,
                line,
                "get_linewidth",
                "set_linewidth",
                TEMPORAL_IQR_EXPORT_LINEWIDTH,
            )
        if _is_near_white(line.get_color()) or _is_light_line_color(line.get_color()):
            _set_with_restore(snapshots, line, "get_color", "set_color", "#111111")

    for legend in fig.findobj(Legend):
        frame = legend.get_frame()
        _set_with_restore(snapshots, frame, "get_facecolor", "set_facecolor", "white")
        _set_with_restore(snapshots, frame, "get_edgecolor", "set_edgecolor", "#bbbbbb")
        for text in legend.get_texts():
            _set_with_restore(snapshots, text, "get_color", "set_color", "#111111")
        for legend_handle in getattr(legend, "legend_handles", ()):
            if legend_handle.get_gid() == "temporal-bin-iqr-band-legend":
                _set_with_restore(
                    snapshots,
                    legend_handle,
                    "get_facecolor",
                    "set_facecolor",
                    mcolors.to_rgba(
                        "#111111",
                        TEMPORAL_IQR_BAND_ALPHA,
                    ),
                )
                _set_with_restore(
                    snapshots,
                    legend_handle,
                    "get_edgecolor",
                    "set_edgecolor",
                    "#111111",
                )
                _set_with_restore(
                    snapshots,
                    legend_handle,
                    "get_linewidth",
                    "set_linewidth",
                    TEMPORAL_IQR_EXPORT_LINEWIDTH,
                )

    for ax in fig.axes:
        try:
            ax.grid(axis="y", color="#dddddd", linewidth=0.8, alpha=0.9)
        except Exception:
            pass

    return snapshots


def _restore_figure_style(snapshots):
    for setter, old_value in reversed(snapshots):
        try:
            setter(old_value)
        except Exception:
            continue


def figure_to_png_bytes(
    fig,
    dpi=300,
    paper_theme=True,
    *,
    preserve_canvas_size=False,
):
    """Render a Matplotlib figure to high-resolution PNG bytes.

    ``preserve_canvas_size`` disables tight cropping so paired preview and
    export figures retain the same physical aspect ratio.
    """
    with matplotlib_operation_lock():
        snapshots = _style_figure_for_paper(fig) if paper_theme else []
        try:
            buf = io.BytesIO()
            save_options = {
                "format": "png",
                "dpi": dpi,
                "facecolor": "white" if paper_theme else fig.get_facecolor(),
                "edgecolor": "none",
            }
            if not preserve_canvas_size:
                save_options.update(
                    {
                        "bbox_inches": "tight",
                        "pad_inches": 0.15,
                    }
                )
            fig.savefig(buf, **save_options)
            return buf.getvalue()
        finally:
            _restore_figure_style(snapshots)


def register_map_export_context(
    analysis,
    parquet_path,
    map_data_paths,
    start_t,
    end_t,
    max_peer_distance_km,
    base_min_stations,
    lat_0,
    lon_0,
    analysis_context,
    presentation_context,
    database_source,
):
    """Register compact map and raw-evidence recipes with immutable provenance."""
    if not isinstance(map_data_paths, MapDataArtifactPaths):
        raise TypeError("Map export context requires compact map artifact paths")
    validated_paths = validate_registered_session_artifacts(
        CACHE_DIR,
        st.session_state,
        analysis_id=analysis["id"],
        artifact_paths_by_kind={
            "spots": parquet_path,
            "map_stations": map_data_paths.station_rows_path,
            "map_segments": map_data_paths.segment_rows_path,
        },
    )
    parquet_path = str(validated_paths["spots"])
    station_rows_path = str(validated_paths["map_stations"])
    segment_rows_path = str(validated_paths["map_segments"])
    blocks = _ensure_current_export_state()
    block = blocks.setdefault(analysis["id"], {})
    block.update({
        "analysis_id": analysis["id"],
        "title": analysis["title"],
        "mode_folder": (
            BENCHMARK_EXPORT_FOLDER
            if analysis["is_compare"]
            else PERFORMANCE_EXPORT_FOLDER
        ),
        "is_compare": bool(analysis["is_compare"]),
        "is_sequential": bool(analysis["is_sequential"]),
        "analysis_kind": analysis["analysis_kind"],
        "performance_method_version": analysis.get("absolute_method_version"),
        "decode_filter_mode": analysis.get("decode_filter_mode"),
        "database_source": _normalized_database_source(database_source),
        "map_context": {
            "parquet_path": parquet_path,
            "map_data_artifacts": {
                "schema_version": MAP_DATA_ARTIFACT_SCHEMA_VERSION,
                "analysis_id": str(analysis["id"]),
                "is_compare": bool(analysis["is_compare"]),
                "is_sequential": bool(analysis["is_sequential"]),
                "analysis_kind": str(analysis["analysis_kind"]),
                "station_rows_path": station_rows_path,
                "segment_rows_path": segment_rows_path,
            },
            "start_t": start_t,
            "end_t": end_t,
            "max_peer_distance_km": max_peer_distance_km,
            "base_min_stations": base_min_stations,
            "lat_0": lat_0,
            "lon_0": lon_0,
            "analysis_context": analysis_context.to_dict(),
            "presentation_context": {
                "language": presentation_context.language,
                "theme": presentation_context.theme,
                "solar_label": presentation_context.solar_label,
            },
        },
    })
    _clear_prepared_results()


def _validated_delta_snr_outlier_export_tables(
    export_tables,
) -> DeltaSnrOutlierExportTables:
    """Validate and isolate both enabled-only outlier table projections."""
    if not isinstance(export_tables, DeltaSnrOutlierExportTables):
        raise TypeError(
            "Enabled Delta-SNR outlier exports require both table projections."
        )
    expected_schemas = (
        (export_tables.event_paths, OUTLIER_EVENT_PATH_COLUMNS, "event paths"),
        (
            export_tables.paired_evidence,
            OUTLIER_PAIRED_EVIDENCE_COLUMNS,
            "paired evidence",
        ),
    )
    for table_df, expected_columns, table_label in expected_schemas:
        if not isinstance(table_df, pd.DataFrame):
            raise TypeError(
                f"Delta-SNR {table_label} export must be a DataFrame."
            )
        if tuple(table_df.columns) != expected_columns:
            raise ValueError(
                f"Delta-SNR {table_label} export columns are invalid."
            )
    return DeltaSnrOutlierExportTables(
        event_paths=export_tables.event_paths.copy(deep=True),
        paired_evidence=export_tables.paired_evidence.copy(deep=True),
    )


def _validated_delta_snr_outlier_export_metadata(
    metadata,
    export_tables: DeltaSnrOutlierExportTables,
) -> dict[str, object]:
    """Validate enabled-only table status and count metadata atomically."""
    if not isinstance(metadata, Mapping):
        raise TypeError(
            "Enabled Delta-SNR outlier exports require table metadata."
        )
    required_keys = {
        "schema_version",
        "result_status",
        "candidate_signature",
        "detection_resolution",
        "event_count",
        "path_event_count",
        "unique_qualifying_path_count",
        "paired_evidence_row_count",
        "populated_paired_unit_count",
        "evaluable_paired_unit_count",
        "abstained_paired_unit_count",
        "tables",
    }
    if set(metadata) != required_keys:
        raise ValueError(
            "Delta-SNR outlier export metadata fields are invalid."
        )
    normalized = deepcopy(dict(metadata))
    if normalized["schema_version"] != DELTA_SNR_OUTLIER_EXPORT_SCHEMA_VERSION:
        raise ValueError("Delta-SNR outlier export schema version is invalid.")
    if normalized["result_status"] not in {
        "insufficient_paired_evidence",
        "insufficient_local_baseline",
        "no_candidates",
        "candidates",
    }:
        raise ValueError("Delta-SNR outlier export result status is invalid.")
    for text_key in ("candidate_signature", "detection_resolution"):
        if not isinstance(normalized[text_key], str) or not normalized[
            text_key
        ].strip():
            raise ValueError(
                f"Delta-SNR outlier export {text_key} must be non-empty."
            )
    count_keys = (
        "event_count",
        "path_event_count",
        "unique_qualifying_path_count",
        "paired_evidence_row_count",
        "populated_paired_unit_count",
        "evaluable_paired_unit_count",
        "abstained_paired_unit_count",
    )
    for count_key in count_keys:
        count_value = normalized[count_key]
        if isinstance(count_value, bool) or not isinstance(count_value, int):
            raise TypeError(
                f"Delta-SNR outlier export {count_key} must be an integer."
            )
        if count_value < 0:
            raise ValueError(
                f"Delta-SNR outlier export {count_key} must be non-negative."
            )
    if normalized["path_event_count"] != len(export_tables.event_paths):
        raise ValueError(
            "Delta-SNR path-event metadata must match the summary table."
        )
    if normalized["paired_evidence_row_count"] != len(
        export_tables.paired_evidence
    ):
        raise ValueError(
            "Delta-SNR paired-evidence metadata must match the evidence table."
        )
    if not (
        normalized["unique_qualifying_path_count"]
        <= normalized["path_event_count"]
        and normalized["event_count"] <= normalized["path_event_count"]
    ):
        raise ValueError("Delta-SNR outlier export event counts are inconsistent.")
    if (
        normalized["evaluable_paired_unit_count"]
        + normalized["abstained_paired_unit_count"]
        != normalized["populated_paired_unit_count"]
    ):
        raise ValueError(
            "Delta-SNR outlier export evaluable and abstained counts must "
            "partition populated paired evidence."
        )
    has_candidates = normalized["path_event_count"] > 0
    if (normalized["result_status"] == "candidates") != has_candidates:
        raise ValueError(
            "Delta-SNR outlier export status must agree with path events."
        )
    expected_tables = {
        "event_paths": OUTLIER_EVENT_PATHS_TABLE_FILENAME,
        "paired_evidence": OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME,
    }
    if normalized["tables"] != expected_tables:
        raise ValueError("Delta-SNR outlier export table names are invalid.")
    _validate_delta_snr_outlier_table_relationships(
        normalized,
        export_tables,
    )
    return normalized


def _validate_delta_snr_outlier_table_relationships(
    metadata: Mapping[str, object],
    export_tables: DeltaSnrOutlierExportTables,
) -> None:
    """Validate event/path joins and duplicated evidence context."""
    event_paths = export_tables.event_paths
    paired_evidence = export_tables.paired_evidence
    if event_paths.empty:
        if not paired_evidence.empty:
            raise ValueError(
                "Delta-SNR paired evidence requires a path-event summary."
            )
        return
    if event_paths["event_id"].isna().any() or event_paths[
        "path_event_id"
    ].isna().any():
        raise ValueError("Delta-SNR outlier export IDs must be present.")
    if event_paths["path_event_id"].duplicated().any():
        raise ValueError("Delta-SNR path-event IDs must be unique.")
    if int(event_paths["event_id"].nunique()) != metadata["event_count"]:
        raise ValueError(
            "Delta-SNR event metadata must match the summary IDs."
        )
    unique_path_count = len(
        event_paths[["callsign", "locator"]].drop_duplicates()
    )
    if unique_path_count != metadata["unique_qualifying_path_count"]:
        raise ValueError(
            "Delta-SNR qualifying-path metadata must match summary identities."
        )
    summary_path_event_ids = set(event_paths["path_event_id"])
    evidence_path_event_ids = set(paired_evidence["path_event_id"])
    if evidence_path_event_ids != summary_path_event_ids:
        raise ValueError(
            "Delta-SNR paired evidence must cover every summarized path event."
        )

    repeated_context_columns = (
        "event_id",
        "path",
        "callsign",
        "locator",
        "direction",
        "path_event_class",
        "paired_unit_type",
    )
    for summary_row in event_paths.to_dict(orient="records"):
        path_event_id = summary_row["path_event_id"]
        evidence_rows = paired_evidence.loc[
            paired_evidence["path_event_id"] == path_event_id
        ]
        expected_count = int(summary_row["paired_unit_count"])
        if len(evidence_rows) != expected_count:
            raise ValueError(
                "Delta-SNR paired-evidence rows must match each path-event count."
            )
        if evidence_rows["unit_sequence"].tolist() != list(
            range(1, expected_count + 1)
        ):
            raise ValueError(
                "Delta-SNR paired-evidence sequence must be contiguous."
            )
        for context_column in repeated_context_columns:
            if not evidence_rows[context_column].eq(
                summary_row[context_column]
            ).all():
                raise ValueError(
                    "Delta-SNR paired evidence disagrees with duplicated "
                    f"{context_column} context."
                )
        if not evidence_rows["event_first_evidence_utc"].eq(
            summary_row["event_first_evidence_utc"]
        ).all() or not evidence_rows["event_last_evidence_utc"].eq(
            summary_row["event_last_evidence_utc"]
        ).all():
            raise ValueError(
                "Delta-SNR paired evidence disagrees with event UTC bounds."
            )


def _validated_zoom_iso_utc(value, *, field_name):
    """Return one normalized focused-export UTC string."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be an ISO timestamp string.")
    try:
        timestamp = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid ISO timestamp.") from exc
    if timestamp.tzinfo is None:
        raise ValueError(f"{field_name} must include a timezone.")
    return timestamp.tz_convert("UTC")


def _validated_drilldown_outlier_candidate_metadata(candidate_metadata):
    """Validate exact optional detector provenance for a focused export."""
    if not isinstance(candidate_metadata, Mapping):
        raise TypeError("Drill-Down outlier candidate metadata must be a mapping.")
    timestamp_fields = (
        "representative_utc",
        "event_start_utc",
        "event_end_utc",
        "pre_flank_start_utc",
        "pre_flank_end_utc",
        "post_flank_start_utc",
        "post_flank_end_utc",
    )
    numeric_fields = (
        "representative_delta_snr_db",
        "local_baseline_db",
        "pre_baseline_db",
        "post_baseline_db",
        "robust_spread_db",
        "robust_z",
        "minimum_robust_z",
        "minimum_departure_db",
    )
    text_fields = (
        "request_token",
        "detector_version",
        "candidate_signature",
        "robust_spread_method",
    )
    required_fields = set(timestamp_fields + numeric_fields + text_fields)
    if set(candidate_metadata) != required_fields:
        raise ValueError(
            "Drill-Down outlier candidate metadata fields are invalid."
        )
    normalized_text = {
        field: str(candidate_metadata[field] or "").strip()
        for field in text_fields
    }
    if not all(normalized_text.values()):
        raise ValueError(
            "Drill-Down outlier candidate text fields must not be empty."
        )
    normalized_timestamps = {
        field: _validated_zoom_iso_utc(
            candidate_metadata[field],
            field_name=f"Drill-Down outlier {field}",
        )
        for field in timestamp_fields
    }
    if not (
        normalized_timestamps["event_start_utc"]
        <= normalized_timestamps["representative_utc"]
        < normalized_timestamps["event_end_utc"]
    ):
        raise ValueError(
            "Drill-Down outlier representative UTC must lie inside its event."
        )
    if not (
        normalized_timestamps["pre_flank_start_utc"]
        <= normalized_timestamps["pre_flank_end_utc"]
        <= normalized_timestamps["event_start_utc"]
        < normalized_timestamps["event_end_utc"]
        <= normalized_timestamps["post_flank_start_utc"]
        <= normalized_timestamps["post_flank_end_utc"]
    ):
        raise ValueError(
            "Drill-Down outlier event and flank bounds are inconsistent."
        )
    normalized_numbers = {}
    for field in numeric_fields:
        try:
            numeric_value = float(candidate_metadata[field])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Drill-Down outlier {field} must be finite."
            ) from exc
        if not math.isfinite(numeric_value):
            raise ValueError(f"Drill-Down outlier {field} must be finite.")
        if field in {
            "robust_spread_db",
            "minimum_robust_z",
            "minimum_departure_db",
        } and numeric_value <= 0.0:
            raise ValueError(f"Drill-Down outlier {field} must be positive.")
        normalized_numbers[field] = numeric_value
    return {
        **normalized_text,
        **normalized_numbers,
        **{
            field: timestamp.isoformat().replace("+00:00", "Z")
            for field, timestamp in normalized_timestamps.items()
        },
    }


def _validated_drilldown_zoom_metadata(metadata) -> dict[str, object]:
    """Validate and normalize one active focused Drill-Down export contract."""
    if not isinstance(metadata, Mapping):
        raise TypeError("Drill-Down zoom export metadata must be a mapping.")
    required_keys = {
        "schema_version",
        "station",
        "start_utc",
        "end_utc",
        "option",
        "origin",
        "time_bin",
        "resolution",
        "aggregation",
        "layout_version",
    }
    allowed_keys = required_keys | {"outlier_candidate"}
    if not required_keys.issubset(metadata) or not set(metadata).issubset(
        allowed_keys
    ):
        raise ValueError("Drill-Down zoom export metadata fields are invalid.")
    schema_version = metadata.get("schema_version")
    if (
        isinstance(schema_version, bool)
        or schema_version != DRILLDOWN_ZOOM_EXPORT_SCHEMA_VERSION
    ):
        raise ValueError("Drill-Down zoom export schema version is invalid.")

    station = metadata.get("station")
    if not isinstance(station, Mapping) or set(station) != {
        "callsign",
        "locator",
    }:
        raise ValueError(
            "Drill-Down zoom export requires one exact station identity."
        )
    callsign = str(station.get("callsign") or "").strip().upper()
    locator = str(station.get("locator") or "").strip().upper()
    if not callsign or not locator:
        raise ValueError(
            "Drill-Down zoom export station callsign and locator are required."
        )

    start_utc = _validated_zoom_iso_utc(
        metadata.get("start_utc"),
        field_name="Drill-Down zoom export start_utc",
    )
    end_utc = _validated_zoom_iso_utc(
        metadata.get("end_utc"),
        field_name="Drill-Down zoom export end_utc",
    )
    if end_utc <= start_utc:
        raise ValueError(
            "Drill-Down zoom export end_utc must be after start_utc."
        )

    origin = str(metadata.get("origin") or "").strip()
    option = str(metadata.get("option") or "").strip()
    if origin not in {"manual", DRILLDOWN_OUTLIER_FOCUS_OPTION}:
        raise ValueError("Drill-Down zoom export origin is invalid.")
    manual_options = {"1h", "3h", "6h", "12h", "24h"}
    if origin == "manual" and option not in manual_options:
        raise ValueError("Fixed Drill-Down zoom export option is invalid.")
    if (
        origin == DRILLDOWN_OUTLIER_FOCUS_OPTION
        and option != DRILLDOWN_OUTLIER_FOCUS_OPTION
    ):
        raise ValueError("Outlier Focus Drill-Down option is invalid.")
    time_bin = str(metadata.get("time_bin") or "").strip()
    resolution = str(metadata.get("resolution") or "").strip()
    aggregation = str(metadata.get("aggregation") or "").strip()

    from ui.plots.drilldown_zoom_figures import (
        DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
        DRILLDOWN_ZOOM_NATIVE_RESOLUTION,
        DRILLDOWN_ZOOM_NO_AGGREGATION,
    )

    if (
        time_bin != "native"
        or resolution != DRILLDOWN_ZOOM_NATIVE_RESOLUTION
        or aggregation != DRILLDOWN_ZOOM_NO_AGGREGATION
    ):
        raise ValueError(
            "Drill-Down zoom export must use native unaggregated evidence."
        )

    layout_version = metadata.get("layout_version")
    if (
        isinstance(layout_version, bool)
        or layout_version != DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION
    ):
        raise ValueError("Drill-Down zoom export layout version is invalid.")
    normalized_metadata = {
        "schema_version": DRILLDOWN_ZOOM_EXPORT_SCHEMA_VERSION,
        "station": {"callsign": callsign, "locator": locator},
        "start_utc": start_utc.isoformat().replace("+00:00", "Z"),
        "end_utc": end_utc.isoformat().replace("+00:00", "Z"),
        "option": option,
        "origin": origin,
        "time_bin": time_bin,
        "resolution": resolution,
        "aggregation": aggregation,
        "layout_version": DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
    }
    if "outlier_candidate" in metadata:
        normalized_metadata["outlier_candidate"] = (
            _validated_drilldown_outlier_candidate_metadata(
                metadata["outlier_candidate"]
            )
        )
    return normalized_metadata


def _validated_drilldown_zoom_registration(
    *,
    metadata,
    selected_station_count,
    performance_snr_recipe,
    performance_temporal_recipe,
    benchmark_delta_snr_recipe,
    benchmark_coverage_recipe,
):
    """Validate the optional metadata-plus-two-recipes registration atomically."""
    performance_recipes = (
        performance_snr_recipe,
        performance_temporal_recipe,
    )
    benchmark_recipes = (
        benchmark_delta_snr_recipe,
        benchmark_coverage_recipe,
    )
    has_any_recipe = any(
        recipe is not None
        for recipe in (*performance_recipes, *benchmark_recipes)
    )
    if metadata is None:
        if has_any_recipe:
            raise ValueError(
                "Drill-Down zoom figure recipes require export metadata."
            )
        return None, None

    if selected_station_count != 1:
        raise ValueError(
            "Drill-Down zoom export requires exactly one selected station."
        )
    has_performance_pair = all(
        recipe is not None for recipe in performance_recipes
    )
    has_benchmark_pair = all(recipe is not None for recipe in benchmark_recipes)
    if any(recipe is not None for recipe in performance_recipes) != (
        has_performance_pair
    ) or any(recipe is not None for recipe in benchmark_recipes) != (
        has_benchmark_pair
    ):
        raise ValueError(
            "Drill-Down zoom export requires both mode-specific figure recipes."
        )
    if has_performance_pair == has_benchmark_pair:
        raise ValueError(
            "Drill-Down zoom export requires exactly one result-family recipe pair."
        )
    active_recipes = (
        performance_recipes if has_performance_pair else benchmark_recipes
    )
    if any(not isinstance(recipe, Mapping) for recipe in active_recipes):
        raise TypeError("Drill-Down zoom figure recipes must be mappings.")
    validated_metadata = _validated_drilldown_zoom_metadata(metadata)
    metric_recipe = active_recipes[0]
    for field in ("time_bin", "resolution", "aggregation", "layout_version"):
        if metric_recipe.get(field) != validated_metadata.get(field):
            raise ValueError(
                "Drill-Down zoom metric recipe disagrees with export metadata."
            )
    candidate_metadata = validated_metadata.get("outlier_candidate")
    metric_overlay = metric_recipe.get("outlier_overlay")
    if has_performance_pair and candidate_metadata is not None:
        raise ValueError(
            "Performance Drill-Down zoom export cannot carry outlier metadata."
        )
    if has_performance_pair and metric_overlay is not None:
        raise ValueError(
            "Performance Drill-Down zoom export cannot carry an outlier overlay."
        )
    if has_benchmark_pair and (
        (candidate_metadata is None) != (metric_overlay is None)
    ):
        raise ValueError(
            "Benchmark Drill-Down outlier metadata and plot overlay must agree."
        )
    if candidate_metadata is not None:
        expected_overlay_values = {
            "representative_utc_ns": int(
                pd.Timestamp(candidate_metadata["representative_utc"]).value
            ),
            "representative_delta_snr_db": candidate_metadata[
                "representative_delta_snr_db"
            ],
            "candidate_start_utc_ns": int(
                pd.Timestamp(candidate_metadata["event_start_utc"]).value
            ),
            "candidate_end_utc_ns": int(
                pd.Timestamp(candidate_metadata["event_end_utc"]).value
            ),
            "local_baseline_db": candidate_metadata["local_baseline_db"],
            "pre_baseline_db": candidate_metadata["pre_baseline_db"],
            "post_baseline_db": candidate_metadata["post_baseline_db"],
            "robust_spread_db": candidate_metadata["robust_spread_db"],
            "robust_spread_method": candidate_metadata[
                "robust_spread_method"
            ],
            "minimum_robust_z": candidate_metadata["minimum_robust_z"],
            "minimum_departure_db": candidate_metadata[
                "minimum_departure_db"
            ],
        }
        if any(
            metric_overlay.get(field) != expected_value
            for field, expected_value in expected_overlay_values.items()
        ):
            raise ValueError(
                "Benchmark Drill-Down outlier overlay disagrees with metadata."
            )
        try:
            marker_utc_ns = tuple(
                int(value)
                for value in metric_overlay["qualifying_marker_utc_ns"]
            )
            marker_delta_snr_db = tuple(
                float(value)
                for value in metric_overlay[
                    "qualifying_marker_delta_snr_db"
                ]
            )
            marker_count = int(metric_overlay["qualifying_marker_count"])
            native_unit_width_ns = int(
                metric_overlay["native_evidence_unit_width_ns"]
            )
            visual_start_ns = int(
                metric_overlay["focused_episode_visual_start_utc_ns"]
            )
            visual_end_ns = int(
                metric_overlay["focused_episode_visual_end_utc_ns"]
            )
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise ValueError(
                "Benchmark Drill-Down qualifying-unit overlay is invalid."
            ) from exc
        marker_coordinates = tuple(
            zip(marker_utc_ns, marker_delta_snr_db)
        )
        if (
            marker_count != len(marker_coordinates)
            or len(marker_utc_ns) != len(marker_delta_snr_db)
            or len(set(marker_coordinates)) != len(marker_coordinates)
            or native_unit_width_ns <= 0
        ):
            raise ValueError(
                "Benchmark Drill-Down qualifying-unit overlay is invalid."
            )
        focus_start_ns = int(
            pd.Timestamp(validated_metadata["start_utc"]).value
        )
        focus_end_ns = int(
            pd.Timestamp(validated_metadata["end_utc"]).value
        )
        if any(
            marker_utc < focus_start_ns or marker_utc >= focus_end_ns
            for marker_utc in marker_utc_ns
        ):
            raise ValueError(
                "Benchmark Drill-Down qualifying-unit markers must lie in "
                "the focused window."
            )
        try:
            native_utc_ns = tuple(
                int(value) for value in metric_recipe["point_utc_ns"]
            )
            native_delta_snr_db = tuple(
                float(value) for value in metric_recipe["metric_db"]
            )
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise ValueError(
                "Benchmark Drill-Down native evidence coordinates are invalid."
            ) from exc
        if len(native_utc_ns) != len(native_delta_snr_db):
            raise ValueError(
                "Benchmark Drill-Down native evidence coordinates are invalid."
            )
        native_coordinates = set(
            zip(native_utc_ns, native_delta_snr_db)
        )
        if not set(marker_coordinates).issubset(native_coordinates):
            raise ValueError(
                "Benchmark Drill-Down qualifying-unit markers must match "
                "native evidence points."
            )
        representative_coordinate = (
            expected_overlay_values["representative_utc_ns"],
            float(
                expected_overlay_values["representative_delta_snr_db"]
            ),
        )
        if (
            focus_start_ns <= representative_coordinate[0] < focus_end_ns
            and representative_coordinate not in marker_coordinates
        ):
            raise ValueError(
                "Benchmark Drill-Down visible representative must be a "
                "qualifying-unit marker."
            )
        expected_visual_start_ns = (
            expected_overlay_values["candidate_start_utc_ns"]
            - native_unit_width_ns // 2
        )
        expected_visual_end_ns = (
            expected_overlay_values["candidate_end_utc_ns"]
            - 1
            + (native_unit_width_ns - native_unit_width_ns // 2)
        )
        if (
            visual_start_ns != expected_visual_start_ns
            or visual_end_ns != expected_visual_end_ns
            or visual_end_ns <= focus_start_ns
            or visual_start_ns >= focus_end_ns
        ):
            raise ValueError(
                "Benchmark Drill-Down focused-episode band is invalid."
            )
    return (
        validated_metadata,
        PERFORMANCE_EXPORT_FOLDER
        if has_performance_pair
        else BENCHMARK_EXPORT_FOLDER,
    )


def _without_drilldown_outlier_metadata(metadata):
    """Remove stale candidate provenance without mutating caller metadata."""
    if not isinstance(metadata, Mapping) or "outlier_candidate" not in metadata:
        return metadata
    sanitized_metadata = dict(metadata)
    sanitized_metadata.pop("outlier_candidate", None)
    return sanitized_metadata


def _without_drilldown_outlier_overlay(recipe):
    """Remove a stale native overlay without mutating the caller recipe."""
    if not isinstance(recipe, Mapping) or recipe.get("outlier_overlay") is None:
        return recipe
    sanitized_recipe = dict(recipe)
    sanitized_recipe["outlier_overlay"] = None
    return sanitized_recipe


def register_inspector_export(
    analysis_id,
    selected_segment,
    selected_distance,
    selected_direction,
    show_non_joint,
    evidence_time_bin,
    selected_stations,
    translations,
    show_zero_target=False,
    segment_evidence_time_bin=None,
    selected_ranges=None,
    selected_directions=None,
    segment_figure_recipe=None,
    segment_temporal_evidence_figure_recipe=None,
    segment_temporal_snr_deviation_figure_recipe=None,
    segment_temporal_coverage_figure_recipe=None,
    selected_evidence_figure_recipe=None,
    selected_station_snr_evidence_figure_recipe=None,
    selected_station_temporal_evidence_figure_recipe=None,
    selected_station_coverage_figure_recipe=None,
    station_insights_df=None,
    drilldown_selected_df=None,
    all_drilldown_context=None,
    reference_snr_header=None,
    selected_station_label=None,
    selected_station_context_label=None,
    selected_station_role=None,
    selected_evidence_figure_descriptions=None,
    allow_multiple_selected_stations=False,
    report_delta_snr_outlier_candidates=False,
    delta_snr_outlier_detector_version=None,
    delta_snr_outlier_detection_policy=None,
    delta_snr_outlier_export_tables=None,
    delta_snr_outlier_export_metadata=None,
    drilldown_zoom_metadata=None,
    drilldown_zoom_performance_snr_figure_recipe=None,
    drilldown_zoom_performance_temporal_figure_recipe=None,
    drilldown_zoom_benchmark_delta_snr_figure_recipe=None,
    drilldown_zoom_benchmark_coverage_figure_recipe=None,
):
    """Register localized Inspector state for lazy high-resolution export.

    Performance selected-station artifacts remain bounded to one path.
    Benchmark callers may explicitly register an ordered multi-path selection.
    Validate that boundary before mutating pending export state.
    """
    if selected_stations is None:
        selected_stations = []
    elif not isinstance(selected_stations, (list, tuple)):
        raise ValueError(
            "Selected-station export metadata must be a list or tuple."
        )
    else:
        selected_stations = list(selected_stations)
    is_outlier_reporting_enabled = bool(
        report_delta_snr_outlier_candidates
    )
    if not is_outlier_reporting_enabled:
        drilldown_zoom_metadata = _without_drilldown_outlier_metadata(
            drilldown_zoom_metadata
        )
        drilldown_zoom_performance_snr_figure_recipe = (
            _without_drilldown_outlier_overlay(
                drilldown_zoom_performance_snr_figure_recipe
            )
        )
        drilldown_zoom_benchmark_delta_snr_figure_recipe = (
            _without_drilldown_outlier_overlay(
                drilldown_zoom_benchmark_delta_snr_figure_recipe
            )
        )
    if len(selected_stations) > 1 and not allow_multiple_selected_stations:
        raise ValueError(
            "Selected-station exports support at most one station."
        )
    if len(selected_stations) > 1 and not is_outlier_reporting_enabled:
        raise ValueError(
            "Multi-station Benchmark exports require enabled Delta-SNR "
            "outlier reporting."
        )
    (
        validated_drilldown_zoom_metadata,
        drilldown_zoom_mode_folder,
    ) = _validated_drilldown_zoom_registration(
        metadata=drilldown_zoom_metadata,
        selected_station_count=len(selected_stations),
        performance_snr_recipe=(
            drilldown_zoom_performance_snr_figure_recipe
        ),
        performance_temporal_recipe=(
            drilldown_zoom_performance_temporal_figure_recipe
        ),
        benchmark_delta_snr_recipe=(
            drilldown_zoom_benchmark_delta_snr_figure_recipe
        ),
        benchmark_coverage_recipe=(
            drilldown_zoom_benchmark_coverage_figure_recipe
        ),
    )
    if validated_drilldown_zoom_metadata is not None:
        zoom_station = validated_drilldown_zoom_metadata["station"]
        expected_selected_label = (
            f"{zoom_station['callsign']} ({zoom_station['locator']})"
        )
        if str(selected_stations[0]).strip().upper() != expected_selected_label:
            raise ValueError(
                "Drill-Down zoom station identity must match the selected station."
            )
    if is_outlier_reporting_enabled:
        detector_version = str(
            delta_snr_outlier_detector_version or ""
        ).strip()
        if not detector_version:
            raise ValueError(
                "Enabled Delta-SNR outlier export metadata requires a "
                "detector version."
            )
        resolved_outlier_policy = (
            DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY
            if delta_snr_outlier_detection_policy is None
            else delta_snr_outlier_detection_policy
        )
        if not isinstance(
            resolved_outlier_policy,
            DeltaSnrOutlierDetectionPolicy,
        ):
            raise TypeError(
                "Enabled Delta-SNR outlier export metadata requires a "
                "DeltaSnrOutlierDetectionPolicy."
            )
        outlier_policy_metadata = resolved_outlier_policy.as_dict()
        validated_outlier_tables = (
            _validated_delta_snr_outlier_export_tables(
                delta_snr_outlier_export_tables
            )
        )
        validated_outlier_export_metadata = (
            _validated_delta_snr_outlier_export_metadata(
                delta_snr_outlier_export_metadata,
                validated_outlier_tables,
            )
        )
    else:
        outlier_policy_metadata = None
        validated_outlier_tables = None
        validated_outlier_export_metadata = None
        segment_temporal_evidence_figure_recipe = (
            _without_delta_snr_outlier_markers(
                segment_temporal_evidence_figure_recipe
            )
        )
        segment_temporal_snr_deviation_figure_recipe = (
            _without_delta_snr_outlier_markers(
                segment_temporal_snr_deviation_figure_recipe
            )
        )
        selected_evidence_figure_recipe = (
            _without_delta_snr_outlier_markers(
                selected_evidence_figure_recipe
            )
        )
        selected_station_snr_evidence_figure_recipe = (
            _without_delta_snr_outlier_markers(
                selected_station_snr_evidence_figure_recipe
            )
        )
        selected_station_temporal_evidence_figure_recipe = (
            _without_delta_snr_outlier_markers(
                selected_station_temporal_evidence_figure_recipe
            )
        )

    blocks = _ensure_current_export_state()
    existing_mode_folder = (blocks.get(analysis_id) or {}).get("mode_folder")
    if (
        drilldown_zoom_mode_folder is not None
        and existing_mode_folder is not None
        and existing_mode_folder != drilldown_zoom_mode_folder
    ):
        raise ValueError(
            "Drill-Down zoom recipes do not match the registered result family."
        )
    block = blocks.setdefault(analysis_id, {"analysis_id": analysis_id})
    selected_station_count = len(selected_stations)
    block.update({
        "selected_segment": selected_segment,
        "selected_distance": selected_distance,
        "selected_direction": selected_direction,
        "selected_ranges": list(selected_ranges or []),
        "selected_directions": list(selected_directions or []),
        "show_non_joint": bool(show_non_joint),
        "show_zero_target": bool(show_zero_target),
        "evidence_time_bin": evidence_time_bin,
        "segment_evidence_time_bin": segment_evidence_time_bin,
        "selected_stations": selected_stations,
        "selected_station_label": selected_station_label,
        "selected_station_context_label": selected_station_context_label,
        "selected_station_count": selected_station_count,
        "selected_station_role": selected_station_role,
        "selected_evidence_weighting": _selected_evidence_weighting_label(
            selected_station_count,
            translations,
        ),
        "selected_evidence_figure_descriptions": dict(
            selected_evidence_figure_descriptions or {}
        ),
        "segment_figure_recipe": segment_figure_recipe,
        "segment_temporal_evidence_figure_recipe": segment_temporal_evidence_figure_recipe,
        "segment_temporal_snr_deviation_figure_recipe": (
            segment_temporal_snr_deviation_figure_recipe
        ),
        "segment_temporal_coverage_figure_recipe": (
            segment_temporal_coverage_figure_recipe
        ),
        "selected_evidence_figure_recipe": selected_evidence_figure_recipe,
        "selected_station_snr_evidence_figure_recipe": (
            selected_station_snr_evidence_figure_recipe
        ),
        "selected_station_temporal_evidence_figure_recipe": (
            selected_station_temporal_evidence_figure_recipe
        ),
        "selected_station_coverage_figure_recipe": (
            selected_station_coverage_figure_recipe
        ),
        "table_station_insights_current_segment.csv": station_insights_df.copy() if isinstance(station_insights_df, pd.DataFrame) else pd.DataFrame(),
        "table_drilldown_selected_stations.csv": drilldown_selected_df.copy() if isinstance(drilldown_selected_df, pd.DataFrame) else pd.DataFrame(),
        "all_drilldown_context": all_drilldown_context,
        "reference_snr_header": reference_snr_header,
    })
    if is_outlier_reporting_enabled:
        block.update(
            {
                "report_delta_snr_outlier_candidates": True,
                "delta_snr_outlier_detector_version": detector_version,
                "delta_snr_outlier_detection_policy": (
                    outlier_policy_metadata
                ),
                "delta_snr_outlier_export": (
                    validated_outlier_export_metadata
                ),
                OUTLIER_EVENT_PATHS_TABLE_FILENAME: (
                    validated_outlier_tables.event_paths
                ),
                OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME: (
                    validated_outlier_tables.paired_evidence
                ),
            }
        )
    else:
        block.pop("report_delta_snr_outlier_candidates", None)
        block.pop("delta_snr_outlier_detector_version", None)
        block.pop("delta_snr_outlier_detection_policy", None)
        block.pop("delta_snr_outlier_export", None)
        for table_filename in OUTLIER_EXPORT_TABLE_FILENAMES:
            block.pop(table_filename, None)

    if validated_drilldown_zoom_metadata is None:
        block.pop("drilldown_zoom_metadata", None)
        for recipe_key in DRILLDOWN_ZOOM_RECIPE_KEYS:
            block.pop(recipe_key, None)
    else:
        block["drilldown_zoom_metadata"] = (
            validated_drilldown_zoom_metadata
        )
        zoom_recipes = {
            "drilldown_zoom_performance_snr_figure_recipe": (
                drilldown_zoom_performance_snr_figure_recipe
            ),
            "drilldown_zoom_performance_temporal_figure_recipe": (
                drilldown_zoom_performance_temporal_figure_recipe
            ),
            "drilldown_zoom_benchmark_delta_snr_figure_recipe": (
                drilldown_zoom_benchmark_delta_snr_figure_recipe
            ),
            "drilldown_zoom_benchmark_coverage_figure_recipe": (
                drilldown_zoom_benchmark_coverage_figure_recipe
            ),
        }
        for recipe_key, recipe in zoom_recipes.items():
            if recipe is None:
                block.pop(recipe_key, None)
            else:
                block[recipe_key] = recipe


def _selected_evidence_weighting_label(selected_station_count, translations):
    """Return localized human-readable weighting metadata for a selection."""
    if selected_station_count > 1:
        return translations["export_weighting_combined_observation"]
    if selected_station_count == 1:
        return translations["export_weighting_single_selected_path"]
    return None


def _without_delta_snr_outlier_markers(recipe):
    """Remove stale marker payloads from an explicitly disabled export recipe."""
    if not isinstance(recipe, dict) or "delta_snr_outlier_markers" not in recipe:
        return recipe
    sanitized_recipe = dict(recipe)
    sanitized_recipe.pop("delta_snr_outlier_markers", None)
    return sanitized_recipe


def _benchmark_evidence_figure_descriptions(block):
    """Map registered Benchmark coverage filenames to localized recipe titles."""
    descriptions = {}
    for figure_name, recipe_key, title_keys in BENCHMARK_EVIDENCE_FIGURE_EXPORTS:
        recipe = block.get(recipe_key)
        if not isinstance(recipe, dict):
            continue
        for title_key in title_keys:
            title_value = recipe.get(title_key)
            if title_value is None:
                continue
            description = str(title_value).strip()
            if description:
                descriptions[figure_name] = description
                break
    return descriptions


def _benchmark_evidence_recipe_signature(block):
    """Fingerprint compact Benchmark recipes without serializing plot arrays."""
    recipe_signatures = []
    for figure_name, recipe_key, title_keys in BENCHMARK_EVIDENCE_FIGURE_EXPORTS:
        recipe = block.get(recipe_key)
        if recipe is None:
            continue
        description = None
        if isinstance(recipe, dict):
            for title_key in title_keys:
                title_value = recipe.get(title_key)
                if title_value is None:
                    continue
                normalized_title = str(title_value).strip()
                if normalized_title:
                    description = normalized_title
                    break
        recipe_signatures.append(
            {
                "filename": figure_name,
                "kind": (
                    recipe.get("kind")
                    if isinstance(recipe, dict)
                    else type(recipe).__name__
                ),
                "schema_version": (
                    recipe.get("schema_version")
                    if isinstance(recipe, dict)
                    else None
                ),
                "time_bin": (
                    recipe.get("time_bin")
                    if isinstance(recipe, dict)
                    else None
                ),
                "description": description,
            }
        )
    return recipe_signatures


def _drilldown_zoom_figure_exports(block):
    """Return the active result family's focused figure export definitions."""
    if not isinstance(block.get("drilldown_zoom_metadata"), Mapping):
        return ()
    if block.get("mode_folder") == PERFORMANCE_EXPORT_FOLDER:
        return DRILLDOWN_ZOOM_PERFORMANCE_FIGURE_EXPORTS
    if block.get("mode_folder") == BENCHMARK_EXPORT_FOLDER:
        return DRILLDOWN_ZOOM_BENCHMARK_FIGURE_EXPORTS
    return ()


def _drilldown_zoom_figure_descriptions(block):
    """Return active zoom filenames and their registered localized titles."""
    descriptions = {}
    for figure_name, recipe_key, title_keys in _drilldown_zoom_figure_exports(
        block
    ):
        recipe = block.get(recipe_key)
        if not isinstance(recipe, Mapping):
            continue
        description = next(
            (
                str(recipe[title_key]).strip()
                for title_key in title_keys
                if recipe.get(title_key) is not None
                and str(recipe[title_key]).strip()
            ),
            figure_name,
        )
        descriptions[figure_name] = description
    return descriptions


def _drilldown_zoom_metadata_for_block(block):
    """Return portable zoom metadata plus its conditional figure inventory."""
    metadata = block.get("drilldown_zoom_metadata")
    if not isinstance(metadata, Mapping):
        return None
    portable_metadata = deepcopy(dict(metadata))
    portable_metadata["figures"] = _drilldown_zoom_figure_descriptions(block)
    return portable_metadata


def _drilldown_zoom_recipe_signature(block):
    """Fingerprint focused metadata and compact recipe presentation contracts."""
    metadata = _drilldown_zoom_metadata_for_block(block)
    if metadata is None:
        return None
    recipes = []
    for figure_name, recipe_key, title_keys in _drilldown_zoom_figure_exports(
        block
    ):
        recipe = block.get(recipe_key)
        if not isinstance(recipe, Mapping):
            continue
        recipes.append(
            {
                "filename": figure_name,
                "kind": recipe.get("kind"),
                "schema_version": recipe.get("schema_version"),
                "layout_version": recipe.get("layout_version"),
                "time_bin": recipe.get("time_bin"),
                "resolution": recipe.get("resolution"),
                "aggregation": recipe.get("aggregation"),
                "outlier_overlay": (
                    _drilldown_zoom_outlier_overlay_signature(
                        recipe.get("outlier_overlay")
                    )
                ),
                "titles": {
                    title_key: recipe.get(title_key)
                    for title_key in title_keys
                    if recipe.get(title_key) is not None
                },
            }
        )
    return {"metadata": metadata, "recipes": recipes}


def _drilldown_zoom_outlier_overlay_signature(overlay):
    """Return compact exact detector-guide identity for export invalidation."""
    if not isinstance(overlay, Mapping):
        return None
    fields = (
        "schema_version",
        "normalization",
        "representative_utc_ns",
        "representative_delta_snr_db",
        "qualifying_marker_count",
        "candidate_start_utc_ns",
        "candidate_end_utc_ns",
        "native_evidence_unit_width_ns",
        "focused_episode_visual_start_utc_ns",
        "focused_episode_visual_end_utc_ns",
        "local_baseline_db",
        "pre_baseline_db",
        "post_baseline_db",
        "pre_flank_utc_ns",
        "post_flank_utc_ns",
        "robust_spread_db",
        "robust_spread_method",
        "minimum_robust_z",
        "minimum_departure_db",
        "absolute_departure_lower_db",
        "absolute_departure_upper_db",
        "robust_z_guides",
        "labels",
    )
    signature = {field: deepcopy(overlay.get(field)) for field in fields}
    for field in (
        "qualifying_marker_utc_ns",
        "qualifying_marker_delta_snr_db",
    ):
        marker_values = overlay.get(field, ())
        try:
            signature[field] = [
                int(value) if field.endswith("utc_ns") else float(value)
                for value in marker_values
            ]
        except (TypeError, ValueError, OverflowError):
            signature[field] = deepcopy(marker_values)
    return signature


def _delta_snr_outlier_recipe_signature(recipe):
    """Return compact marker identity without serializing temporal plot arrays."""
    if not isinstance(recipe, dict):
        return None
    marker_recipe = recipe.get("delta_snr_outlier_markers")
    if not isinstance(marker_recipe, dict):
        return None
    return {
        "schema_version": marker_recipe.get("schema_version"),
        "detector_version": marker_recipe.get("detector_version"),
        "detection_resolution": marker_recipe.get("detection_resolution"),
        "detection_policy_signature": marker_recipe.get(
            "detection_policy_signature"
        ),
        "candidate_count": marker_recipe.get("candidate_count"),
        "candidate_signature": marker_recipe.get("candidate_signature"),
        "legend_label": marker_recipe.get("legend_label"),
        "markers": [
            {
                "callsign": marker.get("callsign"),
                "locator": marker.get("locator"),
                "marker_utc_ns": marker.get("marker_utc_ns"),
                "marker_delta_snr_db": marker.get("marker_delta_snr_db"),
                "episode_start_utc_ns": marker.get(
                    "episode_start_utc_ns"
                ),
                "episode_end_utc_ns": marker.get("episode_end_utc_ns"),
                "event_kind": marker.get("event_kind"),
                "detection_policy_signature": marker.get(
                    "detection_policy_signature"
                ),
            }
            for marker in marker_recipe.get("markers", ())
            if isinstance(marker, Mapping)
        ],
    }


def _should_annotate_reference_correction(column_name, reference_snr_header=None):
    text = str(column_name).strip().casefold()
    reference_text = str(reference_snr_header).strip().casefold() if reference_snr_header else ""
    if reference_text and text == reference_text:
        return True
    return (
        "ref snr" in text or
        "reference snr" in text or
        "cycle ref median" in text or
        "micro-med b" in text or
        "bin \u03b4" in text or
        "\u03b4 snr" in text or
        "delta snr" in text or
        "median \u03b4" in text
    )


def _annotate_reference_correction_headers(
    df,
    correction_db,
    translations,
    reference_snr_header=None,
):
    """Return a display copy whose affected headers state the applied correction."""
    if not isinstance(df, pd.DataFrame) or df.empty or abs(float(correction_db or 0.0)) < 0.05:
        return df

    suffix = translations["fmt_export_reference_correction_suffix"].format(
        value=float(correction_db)
    )
    renamed = {}
    for col in df.columns:
        if _should_annotate_reference_correction(col, reference_snr_header):
            renamed[col] = f"{col}{suffix}"
    return df.rename(columns=renamed) if renamed else df


def _dataframe_to_csv_bytes(
    df,
    translations,
    correction_db=0.0,
    reference_snr_header=None,
):
    """Serialize a CSV with localized human-readable correction annotations."""
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()
    export_df = _annotate_reference_correction_headers(
        df,
        correction_db,
        translations,
        reference_snr_header,
    )
    return format_snr_like_columns_for_csv(export_df).to_csv(index=False).encode("utf-8-sig")


def _localized_outlier_export_table(
    table_df,
    translations,
    *,
    expected_columns,
):
    """Localize one canonical outlier table only at CSV presentation time."""
    if not isinstance(table_df, pd.DataFrame):
        raise TypeError("Delta-SNR outlier export table must be a DataFrame.")
    if tuple(table_df.columns) != expected_columns:
        raise ValueError("Delta-SNR outlier export table columns are invalid.")
    localized = table_df.copy(deep=True)

    def translated_value(value, translation_keys, field_name):
        if value is None or (not isinstance(value, str) and pd.isna(value)):
            return ""
        canonical_value = str(value)
        translation_key = translation_keys.get(canonical_value)
        if translation_key is None:
            raise ValueError(
                f"Unsupported Delta-SNR outlier {field_name}: "
                f"{canonical_value!r}."
            )
        return translations[translation_key]

    for class_column in ("combined_event_class", "path_event_class"):
        if class_column in localized.columns:
            localized[class_column] = localized[class_column].map(
                lambda value: translated_value(
                    value,
                    OUTLIER_EXPORT_EVENT_CLASS_TRANSLATION_KEYS,
                    "event class",
                )
            )
    if "cross_path_context" in localized.columns:
        localized["cross_path_context"] = localized[
            "cross_path_context"
        ].map(
            lambda value: translated_value(
                value,
                OUTLIER_EXPORT_SCOPE_TRANSLATION_KEYS,
                "cross-path context",
            )
        )
    if "departure_direction" in localized.columns:
        localized["departure_direction"] = localized[
            "departure_direction"
        ].map(
            lambda value: translated_value(
                value,
                OUTLIER_EXPORT_DEPARTURE_TRANSLATION_KEYS,
                "departure direction",
            )
        )
    if "paired_unit_type" in localized.columns:
        localized["paired_unit_type"] = localized["paired_unit_type"].map(
            lambda value: translated_value(
                value,
                OUTLIER_EXPORT_PAIRED_UNIT_TRANSLATION_KEYS,
                "paired-evidence type",
            )
        )
    if "direction" in localized.columns:
        localized["direction"] = localized["direction"].map(
            lambda value: (
                translations["txt_outlier_direction_unavailable"]
                if value is None or pd.isna(value) or not str(value).strip()
                else str(value).replace(
                    "E",
                    translations["abbr_compass_east"],
                )
            )
        )
    for boolean_column in (
        "decode_edge_warning",
        "meets_strong_anchor_gates",
    ):
        if boolean_column in localized.columns:
            localized[boolean_column] = localized[boolean_column].map(
                lambda value: translations[
                    "txt_export_outlier_yes"
                    if bool(value)
                    else "txt_export_outlier_no"
                ]
            )
    if "decode_edge_warning_reason" in localized.columns:
        localized["decode_edge_warning_reason"] = localized[
            "decode_edge_warning_reason"
        ].map(
            lambda value: (
                ""
                if value is None or pd.isna(value) or not str(value).strip()
                else translated_value(
                    value,
                    OUTLIER_EXPORT_WARNING_TRANSLATION_KEYS,
                    "decode-edge warning reason",
                )
            )
        )
    if "reported_boundary" in localized.columns:
        localized["reported_boundary"] = localized["reported_boundary"].map(
            lambda value: (
                ""
                if value is None or pd.isna(value) or not str(value).strip()
                else translated_value(
                    value,
                    OUTLIER_EXPORT_BOUNDARY_TRANSLATION_KEYS,
                    "reported boundary",
                )
            )
        )

    localized_headers = {
        column: translations[OUTLIER_EXPORT_COLUMN_TRANSLATION_KEYS[column]]
        for column in expected_columns
    }
    if len(set(localized_headers.values())) != len(localized_headers):
        raise ValueError("Localized Delta-SNR outlier headers must be unique.")
    return localized.rename(columns=localized_headers)


def _json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return str(value)


def _canonical_export_analysis_id(block, analysis_direction):
    """Return a portable direction/result identifier without internal aliases."""
    result_mode = str(block.get("mode_folder", "")).strip().casefold()
    direction = str(analysis_direction or "").strip().casefold()
    if direction not in {"rx", "tx"}:
        internal_analysis_id = str(block.get("analysis_id", "")).strip()
        candidate_direction = internal_analysis_id.partition("_")[0].casefold()
        direction = candidate_direction if candidate_direction in {"rx", "tx"} else ""
    return f"{direction}_{result_mode}" if direction else result_mode


def _build_run_metadata(blocks, config_payload, analysis_cache_paths=None):
    settings = config_payload.get("settings", {})
    core_parameters = settings.get("core_parameters", {})
    comparison_parameters = settings.get("comparison_parameters", {})
    advanced_parameters = settings.get("advanced_parameters", {})
    time_selection = core_parameters.get("time_selection", {})
    benchmark_present = any(
        block.get("mode_folder") == BENCHMARK_EXPORT_FOLDER
        for block in blocks.values()
    )
    performance_present = any(
        block.get("mode_folder") == PERFORMANCE_EXPORT_FOLDER
        for block in blocks.values()
    )
    analysis_cache_paths = analysis_cache_paths or {}
    database_sources = [block.get("database_source") for block in blocks.values()]
    if database_sources and any(source is None for source in database_sources):
        raise ValueError("Export result blocks must record one database source")
    normalized_database_sources = {
        _normalized_database_source(source)
        for source in database_sources
    }
    if len(normalized_database_sources) > 1:
        raise ValueError("Export result blocks must share one database source")
    database_source = (
        next(iter(normalized_database_sources))
        if normalized_database_sources
        else None
    )

    return {
        "app": CONFIG_APP_NAME,
        "version": APP_VERSION,
        "export_signature": _export_signature(blocks),
        "exported_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "language": st.session_state.get("lang"),
        "run_mode": str(core_parameters.get("analysis_direction", "")).upper(),
        "database_source": database_source,
        "blocks_present": {
            BENCHMARK_EXPORT_FOLDER: benchmark_present,
            PERFORMANCE_EXPORT_FOLDER: performance_present,
        },
        "callsign": core_parameters.get("callsign"),
        "reference_or_benchmark_mode": comparison_parameters.get("mode"),
        "band": core_parameters.get("band"),
        "time_window": {
            "start_utc": time_selection.get("start_utc"),
            "end_utc": time_selection.get("end_utc"),
        },
        "benchmark_snr_correction_mode": comparison_parameters.get(
            "snr_correction_mode"
        ),
        "benchmark_snr_correction_db": comparison_parameters.get("snr_correction_db"),
        "thresholds_and_filters": {
            "solar_state": advanced_parameters.get("solar_state"),
            "max_peer_distance_km": advanced_parameters.get(
                "max_peer_distance_km"
            ),
            "exclude_special_callsigns": advanced_parameters.get("exclude_special_callsigns"),
            "exclude_moving_stations": advanced_parameters.get("exclude_moving_stations"),
            "min_joint_spots_per_station": advanced_parameters.get("min_joint_spots_per_station"),
            "min_confirmed_opportunities_per_peer": advanced_parameters.get("min_confirmed_opportunities_per_peer"),
            "min_joint_stations_per_map_segment": advanced_parameters.get("min_joint_stations_per_map_segment"),
        },
        "result_blocks": [
            {
                "analysis_id": _canonical_export_analysis_id(
                    block,
                    core_parameters.get("analysis_direction"),
                ),
                "title": block.get("title"),
                "folder": block.get("mode_folder"),
                "result_mode": block.get("mode_folder"),
                "analysis_cache_file": analysis_cache_paths.get(key),
                "selected_segment": block.get("selected_segment"),
                "selected_distance": block.get("selected_distance"),
                "selected_direction": block.get("selected_direction"),
                "selected_ranges": block.get("selected_ranges", []),
                "selected_directions": block.get("selected_directions", []),
                "selected_stations": block.get("selected_stations", []),
                "selected_station_label": block.get(
                    "selected_station_label"
                ),
                "selected_station_context": block.get(
                    "selected_station_context_label"
                ),
                "selected_station_count": block.get(
                    "selected_station_count",
                    len(block.get("selected_stations", [])),
                ),
                "selected_station_role": block.get(
                    "selected_station_role"
                ),
                "selected_evidence_weighting": block.get(
                    "selected_evidence_weighting"
                ),
                "selected_evidence_figures": block.get(
                    "selected_evidence_figure_descriptions",
                    {},
                ),
                "benchmark_evidence_figures": (
                    _benchmark_evidence_figure_descriptions(block)
                ),
                "show_non_joint": block.get("show_non_joint"),
                "show_zero_target": block.get("show_zero_target"),
                "evidence_time_bin": block.get("evidence_time_bin"),
                "segment_evidence_time_bin": block.get("segment_evidence_time_bin"),
                "is_sequential": block.get("is_sequential"),
                "performance_method_version": block.get(
                    "performance_method_version"
                ),
                **(
                    {
                        "drilldown_zoom": (
                            _drilldown_zoom_metadata_for_block(block)
                        )
                    }
                    if isinstance(
                        block.get("drilldown_zoom_metadata"),
                        Mapping,
                    )
                    else {}
                ),
                **(
                    {
                        "report_delta_snr_outlier_candidates": True,
                        "delta_snr_outlier_detector_version": block.get(
                            "delta_snr_outlier_detector_version"
                        ),
                        "delta_snr_outlier_detection_policy": block.get(
                            "delta_snr_outlier_detection_policy"
                        ),
                        "delta_snr_outlier_export": deepcopy(
                            block.get("delta_snr_outlier_export")
                        ),
                    }
                    if block.get(
                        "report_delta_snr_outlier_candidates"
                    )
                    is True
                    else {}
                ),
            }
            for key, block in blocks.items()
        ],
    }


def _table_content_signature(df):
    """Fingerprint one registered table's schema, order, and canonical values."""
    if not isinstance(df, pd.DataFrame):
        return None
    normalized = df.astype(object).where(pd.notna(df), None)
    payload = {
        "columns": [str(column) for column in normalized.columns],
        "rows": normalized.to_dict(orient="records"),
    }
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=_json_default,
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def _artifact_export_signature(path_value):
    """Return path-free identity and stat inputs for one immutable artifact."""
    if not isinstance(path_value, (str, Path)) or not str(path_value).strip():
        return None
    try:
        artifact_path = Path(path_value).resolve()
    except (OSError, RuntimeError, ValueError):
        return {"identity": "invalid", "exists": False}
    signature = {
        "identity": hashlib.sha256(
            str(artifact_path).encode("utf-8")
        ).hexdigest(),
    }
    try:
        artifact_stat = artifact_path.stat()
    except OSError:
        signature["exists"] = False
    else:
        signature.update({
            "exists": True,
            "size_bytes": int(artifact_stat.st_size),
        })
    return signature


def _map_context_export_signature(context):
    """Return map recipe inputs without embedding filesystem path text."""
    if not isinstance(context, dict):
        return None
    map_artifacts = context.get("map_data_artifacts")
    safe_context = {
        key: value
        for key, value in context.items()
        if key not in {"parquet_path", "map_data_artifacts"}
    }
    safe_context["evidence_artifact"] = _artifact_export_signature(
        context.get("parquet_path")
    )
    if isinstance(map_artifacts, dict):
        safe_context["map_data_artifacts"] = {
            "schema_version": map_artifacts.get("schema_version"),
            "analysis_id": map_artifacts.get("analysis_id"),
            "is_compare": map_artifacts.get("is_compare"),
            "is_sequential": map_artifacts.get("is_sequential"),
            "analysis_kind": map_artifacts.get("analysis_kind"),
            "station_artifact": _artifact_export_signature(
                map_artifacts.get("station_rows_path")
            ),
            "segment_artifact": _artifact_export_signature(
                map_artifacts.get("segment_rows_path")
            ),
        }
    else:
        safe_context["map_data_artifacts"] = None
    return safe_context


def _export_signature(blocks):
    """Return a compact fingerprint for registered state and render contracts."""
    payload = []
    for key, block in sorted(blocks.items()):
        payload.append({
            "key": key,
            "performance_distance_export_render_version": (
                PERFORMANCE_DISTANCE_EXPORT_RENDER_VERSION
                if block.get("mode_folder") == PERFORMANCE_EXPORT_FOLDER
                else None
            ),
            "temporal_snr_export_render_version": (
                TEMPORAL_SNR_EXPORT_RENDER_VERSION
            ),
            "temporal_evidence_layout_version": (
                TEMPORAL_EVIDENCE_LAYOUT_VERSION
            ),
            "temporal_iqr_band_alpha": TEMPORAL_IQR_BAND_ALPHA,
            "analysis_id": block.get("analysis_id"),
            "title": block.get("title"),
            "mode_folder": block.get("mode_folder"),
            "database_source": block.get("database_source"),
            "selected_segment": block.get("selected_segment"),
            "selected_distance": block.get("selected_distance"),
            "selected_direction": block.get("selected_direction"),
            "selected_ranges": block.get("selected_ranges", []),
            "selected_directions": block.get("selected_directions", []),
            "selected_stations": block.get("selected_stations", []),
            "selected_station_label": block.get("selected_station_label"),
            "selected_station_context": block.get(
                "selected_station_context_label"
            ),
            "selected_station_count": block.get(
                "selected_station_count",
                len(block.get("selected_stations", [])),
            ),
            "selected_station_role": block.get("selected_station_role"),
            "selected_evidence_weighting": block.get(
                "selected_evidence_weighting"
            ),
            "selected_evidence_figures": block.get(
                "selected_evidence_figure_descriptions",
                {},
            ),
            "benchmark_evidence_recipes": (
                _benchmark_evidence_recipe_signature(block)
            ),
            **(
                {
                    "drilldown_zoom": (
                        _drilldown_zoom_recipe_signature(block)
                    )
                }
                if isinstance(
                    block.get("drilldown_zoom_metadata"),
                    Mapping,
                )
                else {}
            ),
            **(
                {
                    "report_delta_snr_outlier_candidates": True,
                    "delta_snr_outlier_detector_version": block.get(
                        "delta_snr_outlier_detector_version"
                    ),
                    "delta_snr_outlier_detection_policy": block.get(
                        "delta_snr_outlier_detection_policy"
                    ),
                    "delta_snr_outlier_export": block.get(
                        "delta_snr_outlier_export"
                    ),
                    "delta_snr_outlier_event_paths_table": (
                        _table_content_signature(
                            block.get(OUTLIER_EVENT_PATHS_TABLE_FILENAME)
                        )
                    ),
                    "delta_snr_outlier_paired_evidence_table": (
                        _table_content_signature(
                            block.get(OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME)
                        )
                    ),
                    "segment_delta_snr_outlier_markers": (
                        _delta_snr_outlier_recipe_signature(
                            block.get(
                                "segment_temporal_evidence_figure_recipe"
                            )
                        )
                    ),
                    "selected_delta_snr_outlier_markers": (
                        _delta_snr_outlier_recipe_signature(
                            block.get("selected_evidence_figure_recipe")
                        )
                    ),
                }
                if block.get("report_delta_snr_outlier_candidates") is True
                else {}
            ),
            "show_non_joint": block.get("show_non_joint"),
            "show_zero_target": block.get("show_zero_target"),
            "evidence_time_bin": block.get("evidence_time_bin"),
            "segment_evidence_time_bin": block.get("segment_evidence_time_bin"),
            "map_context": _map_context_export_signature(
                block.get("map_context")
            ),
            "station_table_content": _table_content_signature(
                block.get("table_station_insights_current_segment.csv")
            ),
            "selected_drilldown_content": _table_content_signature(
                block.get("table_drilldown_selected_stations.csv")
            ),
            "all_drilldown_station_count": len((block.get("all_drilldown_context") or {}).get("station_meta_df", [])),
        })
    canonical_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    )
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()


def _safe_analysis_filename(analysis_id):
    safe_id = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(analysis_id or "analysis"))
    safe_id = "_".join(part for part in safe_id.split("_") if part)
    return safe_id or "analysis"


def _analysis_cache_export_paths(blocks):
    """Return ZIP-relative parquet cache paths for exportable result blocks."""
    paths = {}
    used_folders = {}

    for key, block in blocks.items():
        folder = block.get("mode_folder")
        context = block.get("map_context") or {}
        parquet_path = context.get("parquet_path")
        if folder not in EXPORTABLE_RESULT_FOLDERS or not parquet_path:
            continue
        if not ARTIFACT_STORE.touch(parquet_path):
            continue

        folder_count = used_folders.get(folder, 0)
        used_folders[folder] = folder_count + 1
        parquet_name = "analysis_cache.parquet" if folder_count == 0 else f"analysis_cache_{_safe_analysis_filename(block.get('analysis_id'))}.parquet"
        paths[key] = f"{folder}/{parquet_name}"

    return paths


def _render_map_png_for_block(block):
    """Render a light-theme map from its compact registered aggregate pair."""
    analysis_id = str(block.get("analysis_id", ""))
    context = block.get("map_context")
    if not isinstance(context, dict):
        raise ExportArtifactUnavailableError(
            f"Required map export context is unavailable for {analysis_id}; "
            "run the analysis again"
        )
    map_artifacts = context.get("map_data_artifacts")
    if not isinstance(map_artifacts, dict):
        raise ExportArtifactUnavailableError(
            f"Required compact map data is unavailable for {analysis_id}; "
            "run the analysis again"
        )
    expected_identity = {
        "schema_version": MAP_DATA_ARTIFACT_SCHEMA_VERSION,
        "analysis_id": analysis_id,
        "is_compare": bool(block.get("is_compare")),
        "is_sequential": bool(block.get("is_sequential")),
        "analysis_kind": str(block.get("analysis_kind", "")),
    }
    if any(
        map_artifacts.get(identity_key) != identity_value
        for identity_key, identity_value in expected_identity.items()
    ):
        raise ExportArtifactUnavailableError(
            f"Compact map data identity no longer matches {analysis_id}; "
            "run the analysis again"
        )
    station_rows_path = map_artifacts.get("station_rows_path")
    segment_rows_path = map_artifacts.get("segment_rows_path")
    try:
        validated_paths = validate_registered_session_artifacts(
            CACHE_DIR,
            st.session_state,
            analysis_id=analysis_id,
            artifact_paths_by_kind={
                "spots": context.get("parquet_path"),
                "map_stations": station_rows_path,
                "map_segments": segment_rows_path,
            },
        )
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise ExportArtifactUnavailableError(
            f"Required map artifacts are no longer valid for {analysis_id}; "
            "run the analysis again"
        ) from exc
    map_data_paths = MapDataArtifactPaths(
        station_rows_path=validated_paths["map_stations"],
        segment_rows_path=validated_paths["map_segments"],
    )
    try:
        map_data = read_map_data_artifacts(
            map_data_paths,
            analysis_id=expected_identity["analysis_id"],
            is_compare=expected_identity["is_compare"],
            is_sequential=expected_identity["is_sequential"],
            analysis_kind=expected_identity["analysis_kind"],
        )
    except Exception as exc:
        raise ExportArtifactUnavailableError(
            f"Required compact map data could not be read for {analysis_id}; "
            "run the analysis again"
        ) from exc

    try:
        from core.plot_engine import render_map_figure

        analysis_context = AnalysisContext.from_dict(context["analysis_context"])
        presentation_values = context["presentation_context"]
        presentation_language = presentation_values["language"]
        presentation_labels = T[presentation_language]
        presentation_context = PresentationContext(
            language=presentation_language,
            labels=presentation_labels,
            theme="light",
            solar_label=presentation_values.get(
                "solar_label",
                presentation_labels["opt_solar_all"],
            ),
        )
        plot_result = render_map_figure(
            map_data,
            title=block.get("title", ""),
            start_t=context["start_t"],
            end_t=context["end_t"],
            max_dist_km=context["max_peer_distance_km"],
            base_min_stations=context["base_min_stations"],
            lat_0=context["lat_0"],
            lon_0=context["lon_0"],
            analysis_context=analysis_context,
            presentation_context=presentation_context,
        )
        if plot_result is None:
            raise ValueError("Map renderer produced no figure")
        fig = plot_result.figure
    except Exception as exc:
        raise ExportArtifactUnavailableError(
            f"Required map export could not be rendered for {analysis_id}; "
            "run the analysis again"
        ) from exc

    try:
        return figure_to_png_bytes(fig, paper_theme=False)
    except Exception as exc:
        raise ExportArtifactUnavailableError(
            f"Required map export could not be encoded for {analysis_id}; "
            "run the analysis again"
        ) from exc
    finally:
        dispose_matplotlib_figure(fig)

def _render_inspector_png_for_block(block, figure_name):
    """Render one inspector figure from compact inputs only during ZIP preparation."""
    from ui.plots.evidence_figures import (
        render_segment_insight_export_figure,
        render_segment_temporal_evidence_export_figure,
        render_segment_temporal_snr_export_figure,
        render_selected_evidence_export_figure,
    )
    selected_performance_figure_names = {
        "figure_selected_station_snr_evidence.png",
        "figure_selected_station_temporal_evidence.png",
    }
    selected_performance_recipes = {
        "figure_selected_station_snr_evidence.png": block.get(
            "selected_station_snr_evidence_figure_recipe"
        ),
        "figure_selected_station_temporal_evidence.png": block.get(
            "selected_station_temporal_evidence_figure_recipe"
        ),
    }
    drilldown_zoom_recipe_keys = {
        export_figure_name: recipe_key
        for export_figure_name, recipe_key, _title_keys in (
            *DRILLDOWN_ZOOM_PERFORMANCE_FIGURE_EXPORTS,
            *DRILLDOWN_ZOOM_BENCHMARK_FIGURE_EXPORTS,
        )
    }
    benchmark_coverage_recipe_keys = {
        figure_name: recipe_key
        for figure_name, recipe_key, _title_keys in (
            BENCHMARK_EVIDENCE_FIGURE_EXPORTS
        )
    }
    if figure_name in selected_performance_figure_names:
        selected_performance_recipe = selected_performance_recipes[figure_name]
        if selected_performance_recipe is None:
            return None
    if figure_name in drilldown_zoom_recipe_keys:
        drilldown_zoom_recipe = block.get(
            drilldown_zoom_recipe_keys[figure_name]
        )
        if drilldown_zoom_recipe is None:
            return None
        from ui.plots.drilldown_zoom_figures import (
            render_drilldown_zoom_benchmark_coverage_figure,
            render_drilldown_zoom_benchmark_delta_snr_figure,
            render_drilldown_zoom_performance_evidence_figure,
            render_drilldown_zoom_performance_snr_figure,
        )

        drilldown_zoom_renderers = {
            "figure_drilldown_zoom_snr_evidence.png": (
                render_drilldown_zoom_performance_snr_figure
            ),
            "figure_drilldown_zoom_temporal_evidence.png": (
                render_drilldown_zoom_performance_evidence_figure
            ),
            "figure_drilldown_zoom_delta_snr_evidence.png": (
                render_drilldown_zoom_benchmark_delta_snr_figure
            ),
            "figure_drilldown_zoom_coverage.png": (
                render_drilldown_zoom_benchmark_coverage_figure
            ),
        }
        fig = drilldown_zoom_renderers[figure_name](drilldown_zoom_recipe)
    elif figure_name in benchmark_coverage_recipe_keys:
        coverage_recipe = block.get(
            benchmark_coverage_recipe_keys[figure_name]
        )
        if coverage_recipe is None:
            return None
        from ui.plots.benchmark_evidence_figures import (
            render_compare_temporal_coverage_export_figure,
            render_selected_compare_coverage_export_figure,
        )
        benchmark_coverage_renderers = {
            "figure_segment_temporal_coverage.png": (
                render_compare_temporal_coverage_export_figure
            ),
            "figure_selected_station_coverage.png": (
                render_selected_compare_coverage_export_figure
            ),
        }
        fig = benchmark_coverage_renderers[figure_name](coverage_recipe)
    elif figure_name == "figure_segment_insight.png":
        fig = render_segment_insight_export_figure(block.get("segment_figure_recipe"))
    elif figure_name == "figure_segment_temporal_evidence.png":
        fig = render_segment_temporal_evidence_export_figure(
            block.get("segment_temporal_evidence_figure_recipe")
        )
    elif figure_name == "figure_segment_temporal_snr_deviation.png":
        fig = render_segment_temporal_snr_export_figure(
            block.get("segment_temporal_snr_deviation_figure_recipe")
        )
    elif figure_name == "figure_selected_station_evidence.png":
        fig = render_selected_evidence_export_figure(block.get("selected_evidence_figure_recipe"))
    elif figure_name == "figure_selected_station_snr_evidence.png":
        fig = render_segment_temporal_snr_export_figure(
            selected_performance_recipes[figure_name]
        )
    elif figure_name == "figure_selected_station_temporal_evidence.png":
        fig = render_segment_temporal_evidence_export_figure(
            selected_performance_recipes[figure_name]
        )
    else:
        return None
    if fig is None:
        return None
    try:
        return figure_to_png_bytes(fig, paper_theme=True)
    finally:
        dispose_matplotlib_figure(fig)

def _build_all_drilldown_for_block(block):
    """Load and build the full-segment drill-down table only during ZIP preparation."""
    context = block.get("all_drilldown_context") or {}
    map_context = block.get("map_context") or {}
    station_meta_df = context.get("station_meta_df")
    parquet_path = map_context.get("parquet_path")
    if not isinstance(station_meta_df, pd.DataFrame) or station_meta_df.empty or not parquet_path:
        return pd.DataFrame()

    from i18n import T
    from ui.inspector.drilldown import _build_drilldown_table, _load_station_rows_for_drilldown

    lang = context.get("lang", "en")
    t = T.get(lang, T["en"])
    try:
        station_rows_df = _load_station_rows_for_drilldown(
            parquet_path,
            station_meta_df,
            context["station_col"],
            context["loc_col"],
        )
        drilldown_df, _ = _build_drilldown_table(
            parquet_path,
            station_meta_df,
            context["station_col"],
            context["loc_col"],
            context["km_col"],
            context["az_col"],
            context["analysis_id"],
            context["is_sequential"],
            context["show_non_joint"],
            context["is_local_median"],
            context["col_u_name"],
            context["ref_header"],
            t,
            station_rows_df=station_rows_df,
            tx_ab_repeat_interval_minutes=context.get(
                "tx_ab_repeat_interval_minutes",
                10,
            ),
            tx_ab_target_start_minute=context.get(
                "tx_ab_target_start_minute",
                0,
            ),
            tx_ab_reference_start_minute=context.get(
                "tx_ab_reference_start_minute",
                2,
            ),
            target_callsign=context.get("target_callsign", ""),
        )
        return drilldown_df
    except (FileNotFoundError, KeyError, ValueError):
        return pd.DataFrame()


def build_results_zip(translations):
    """Build a results ZIP with localized human-readable presentation metadata."""
    blocks = _ensure_current_export_state()
    exportable_blocks = {
        key: block for key, block in blocks.items()
        if block.get("mode_folder") in EXPORTABLE_RESULT_FOLDERS
    }
    if not exportable_blocks:
        return None, None

    config_bytes, _ = build_config_payload()
    config_payload = json.loads(config_bytes.decode("utf-8"))
    analysis_cache_paths = _analysis_cache_export_paths(exportable_blocks)
    metadata = _build_run_metadata(exportable_blocks, config_payload, analysis_cache_paths)
    timestamp_local = datetime.now().strftime("%Y_%m_%d__%H_%M")
    root = f"WSPRadar_export_{timestamp_local}"

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{root}/config/wspradar_config.config", config_bytes)
        zf.writestr(
            f"{root}/config/run_metadata.json",
            json.dumps(
                metadata,
                indent=2,
                ensure_ascii=False,
                default=_json_default,
            ).encode("utf-8"),
        )

        for block_key, block in exportable_blocks.items():
            folder = block["mode_folder"]
            correction_db = (
                config_payload.get("settings", {})
                .get("comparison_parameters", {})
                .get("snr_correction_db", 0.0)
                if block.get("is_compare")
                else 0.0
            )
            figure_names = [
                "figure_map_highres.png",
                "figure_segment_insight.png",
                "figure_segment_temporal_evidence.png",
            ]
            if folder == PERFORMANCE_EXPORT_FOLDER:
                figure_names.insert(
                    2,
                    "figure_segment_temporal_snr_deviation.png",
                )
                figure_names.extend(
                    [
                        "figure_selected_station_snr_evidence.png",
                        "figure_selected_station_temporal_evidence.png",
                    ]
                )
            else:
                figure_names.extend(
                    [
                        "figure_segment_temporal_coverage.png",
                        "figure_selected_station_evidence.png",
                        "figure_selected_station_coverage.png",
                    ]
                )
            figure_names.extend(
                figure_name
                for figure_name, _recipe_key, _title_keys in (
                    _drilldown_zoom_figure_exports(block)
                )
            )
            required_drilldown_zoom_figures = {
                figure_name
                for figure_name, _recipe_key, _title_keys in (
                    _drilldown_zoom_figure_exports(block)
                )
            }
            for figure_name in figure_names:
                png_bytes = (
                    _render_map_png_for_block(block)
                    if figure_name == "figure_map_highres.png"
                    else _render_inspector_png_for_block(block, figure_name)
                )
                if figure_name == "figure_map_highres.png" and not png_bytes:
                    raise ExportArtifactUnavailableError(
                        "Required high-resolution map export produced no image; "
                        "run the analysis again"
                    )
                if (
                    figure_name in required_drilldown_zoom_figures
                    and not png_bytes
                ):
                    raise ExportArtifactUnavailableError(
                        "Required Drill-Down zoom export produced no image; "
                        "adjust the focus or run the analysis again"
                    )
                if png_bytes:
                    zf.writestr(f"{root}/{folder}/{figure_name}", png_bytes)

            lazy_all_drilldown_df = _build_all_drilldown_for_block(block)
            for table_name in [
                "table_station_insights_current_segment.csv",
                "table_drilldown_selected_stations.csv",
                "table_drilldown_all_stations_current_segment.csv",
            ]:
                table_df = (
                    lazy_all_drilldown_df
                    if table_name == "table_drilldown_all_stations_current_segment.csv"
                    else block.get(table_name)
                )
                zf.writestr(
                    f"{root}/{folder}/{table_name}",
                    _dataframe_to_csv_bytes(
                        table_df,
                        translations,
                        correction_db=correction_db,
                        reference_snr_header=block.get("reference_snr_header"),
                    )
                )

            if block.get("report_delta_snr_outlier_candidates") is True:
                outlier_table_schemas = (
                    (
                        OUTLIER_EVENT_PATHS_TABLE_FILENAME,
                        OUTLIER_EVENT_PATH_COLUMNS,
                    ),
                    (
                        OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME,
                        OUTLIER_PAIRED_EVIDENCE_COLUMNS,
                    ),
                )
                for table_name, expected_columns in outlier_table_schemas:
                    localized_table = _localized_outlier_export_table(
                        block.get(table_name),
                        translations,
                        expected_columns=expected_columns,
                    )
                    zf.writestr(
                        f"{root}/{folder}/{table_name}",
                        _dataframe_to_csv_bytes(
                            localized_table,
                            translations,
                        ),
                    )

            analysis_cache_path = analysis_cache_paths.get(block_key)
            parquet_path = (block.get("map_context") or {}).get("parquet_path")
            if analysis_cache_path and parquet_path:
                try:
                    with ARTIFACT_STORE.lease(parquet_path) as leased_path:
                        zf.write(leased_path, f"{root}/{analysis_cache_path}")
                except FileNotFoundError:
                    pass

    return zip_buf.getvalue(), f"{root}.zip"


def _prepare_results_zip_with_admission(t):
    """Wait for export capacity and build one prepared result package."""
    queue_slot = st.empty()
    waiting_status = None
    waiting_body = None
    queue_profile = {
        "initial_position": 0,
        "maximum_position": 0,
    }
    admission_started = time.perf_counter()

    def show_waiting(snapshot):
        nonlocal waiting_status, waiting_body
        if queue_profile["initial_position"] == 0:
            queue_profile["initial_position"] = snapshot.position
        queue_profile["maximum_position"] = max(
            queue_profile["maximum_position"],
            snapshot.position,
        )
        label = t["msg_export_queue_wait"].format(position=snapshot.position)
        detail = t["msg_export_queue_detail"].format(
            active=snapshot.active,
            maximum=snapshot.max_active,
            queued=snapshot.queued,
        )
        if waiting_status is None:
            with queue_slot.container():
                waiting_status = st.status(label, expanded=True, state="running")
                with waiting_status:
                    waiting_body = st.empty()
        else:
            waiting_status.update(label=label, expanded=True, state="running")
        waiting_body.markdown(detail)

    owner = (
        f"{session_artifact_owner(st.session_state)}:"
        f"{st.session_state.get('run_id', 0)}:export"
    )

    def log_admission(outcome):
        active, queued = EXPORT_ADMISSION_GATE.counts()
        log_performance_event(
            "export_admission",
            outcome=outcome,
            wait_seconds=time.perf_counter() - admission_started,
            initial_queue_position=queue_profile["initial_position"],
            maximum_queue_position=queue_profile["maximum_position"],
            active=active,
            queued=queued,
            rss_bytes=process_rss_bytes(),
        )

    try:
        permit = EXPORT_ADMISSION_GATE.acquire(owner=owner, on_wait=show_waiting)
    except AnalysisQueueFull:
        log_admission("queue_full")
        st.warning(t["warn_export_queue_full"])
        return None, None
    except AnalysisQueueTimeout:
        log_admission("queue_timeout")
        queue_slot.empty()
        st.warning(t["warn_export_queue_timeout"])
        return None, None

    log_admission("admitted")
    queue_slot.empty()
    export_started = time.perf_counter()
    rss_start = process_rss_bytes()
    export_outcome = "completed"
    result = (None, None)
    try:
        with permit:
            permit.touch()
            with st.spinner(t["msg_preparing_all_results"]):
                result = build_results_zip(t)
        if not result[0]:
            export_outcome = "empty"
        return result
    except ExportArtifactUnavailableError:
        export_outcome = ExportArtifactUnavailableError.__name__
        st.error(t["err_analysis_processing_failed"])
        return None, None
    except BaseException as exc:
        export_outcome = type(exc).__name__
        raise
    finally:
        active, queued = EXPORT_ADMISSION_GATE.counts()
        log_performance_event(
            "export_preparation",
            outcome=export_outcome,
            duration_seconds=time.perf_counter() - export_started,
            zip_bytes=len(result[0]) if result[0] else 0,
            active_after_release=active,
            queued_after_release=queued,
            rss_start_bytes=rss_start,
            rss_end_bytes=process_rss_bytes(),
            process_peak_rss_bytes=process_peak_rss_bytes(),
        )


def _share_analysis_content(translations):
    """Build localized browser-share copy from validated canonical state."""
    comparison_mode = st.session_state.get("val_comp_mode", "none")
    mode_label_key = {
        "none": "share_mode_performance",
        "hardware_ab": "share_mode_hardware_ab",
        "reference_station": "share_mode_reference_station",
        "local_neighborhood": "share_mode_local_neighborhood",
    }[comparison_mode]
    title = translations["share_analysis_title"].format(
        callsign=str(st.session_state.get("val_callsign", "")).strip().upper(),
        direction=str(
            st.session_state.get("val_analysis_direction", "")
        ).strip().upper(),
        mode=translations[mode_label_key],
        band=st.session_state.get("val_band", ""),
    )
    labels = {
        "url_field": translations["share_url_field"],
        "copy_link": translations["share_copy_link"],
        "copied": translations["share_copied"],
        "manual_copy": translations["share_manual_copy"],
        "native_share": translations["share_native"],
        "native_share_failed": translations["share_native_failed"],
        "email": translations["share_email"],
        "whatsapp": translations["share_whatsapp"],
        "x": translations["share_x"],
        "facebook": translations["share_facebook"],
        "linkedin": translations["share_linkedin"],
    }
    return title, translations["share_analysis_message"], labels


def render_download_all_results(t):
    """Render adjacent result-export, config-save, and sharing controls."""
    blocks = _ensure_current_export_state()
    exportable_blocks = {
        key: block for key, block in blocks.items()
        if block.get("mode_folder") in EXPORTABLE_RESULT_FOLDERS
    }
    if not exportable_blocks:
        return

    signature = _export_signature(exportable_blocks)
    if st.session_state.get(EXPORT_ZIP_SIGNATURE_KEY) != signature:
        _clear_prepared_results()

    st.markdown(
        utility_header_html(
            t["hdr_results_download_evidence"],
            t["sub_results_download_evidence"],
        ),
        unsafe_allow_html=True,
    )
    render_result_guidance_popover(
        RESULT_GUIDANCE_DOWNLOAD,
        t["hdr_results_download_evidence"],
        language=st.session_state.get("lang", "en"),
        translations=t,
        key=f"results_guidance_download_{_current_run_id()}",
    )
    export_column, save_column, share_column = st.columns(
        [0.5, 0.25, 0.25],
        gap="large",
        vertical_alignment="center",
    )
    with export_column:
        prepared_bytes = st.session_state.get(EXPORT_ZIP_BYTES_KEY)
        prepared_filename = st.session_state.get(EXPORT_ZIP_FILENAME_KEY)
        if prepared_bytes and prepared_filename:
            st.download_button(
                t["btn_download_prepared_results"],
                data=prepared_bytes,
                file_name=prepared_filename,
                mime="application/zip",
                icon=":material/download:",
                type="primary",
                width="stretch",
            )
        elif st.button(
            t["btn_prepare_all_results"],
            icon=":material/archive:",
            type="secondary",
            width="stretch",
        ):
            zip_bytes, filename = _prepare_results_zip_with_admission(t)
            if zip_bytes:
                st.session_state[EXPORT_ZIP_BYTES_KEY] = zip_bytes
                st.session_state[EXPORT_ZIP_FILENAME_KEY] = filename
                st.session_state[EXPORT_ZIP_SIGNATURE_KEY] = signature
                st.download_button(
                    t["btn_download_prepared_results"],
                    data=zip_bytes,
                    file_name=filename,
                    mime="application/zip",
                    icon=":material/download:",
                    type="primary",
                    width="stretch",
                )
    with save_column:
        render_config_save_control(
            popover_key="config_save_results_trigger",
            form_scope="results",
        )
    with share_column:
        share_popover = st.popover(
            t["btn_share_analysis"],
            icon=":material/share:",
            type="primary",
            width="stretch",
            key="share_analysis_results_trigger",
            on_change="rerun",
        )
        if share_popover.open:
            with share_popover:
                share_title, share_message, share_labels = (
                    _share_analysis_content(t)
                )
                render_share_analysis_browser(
                    share_url=build_share_url(st.session_state),
                    title=share_title,
                    message=share_message,
                    labels=share_labels,
                    key=f"share_analysis_browser_{_current_run_id()}",
                )
